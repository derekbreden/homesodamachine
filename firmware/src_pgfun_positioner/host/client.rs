//! One serialized controller session keeps heartbeat acknowledgements separate from motion acceptance.
use crate::kinematics::{Geometry, MAX_DURATION_US, MAX_JOG_COUNTS, MAX_RATE, MIN_DURATION_US};
use anyhow::{Context, Result, bail, ensure};
use serde::{Deserialize, Serialize};
use std::{
    fmt,
    fs::File,
    io::{Read, Write},
    sync::{
        Arc, Mutex,
        atomic::{AtomicBool, Ordering},
    },
    thread::{self, JoinHandle},
    time::{Duration, Instant},
};

pub trait Transport: Send {
    fn read(&mut self, buffer: &mut [u8]) -> std::io::Result<usize>;
    fn write_all(&mut self, bytes: &[u8]) -> std::io::Result<()>;
    fn close(&mut self) -> std::io::Result<()> {
        Ok(())
    }
}
pub trait Clock: Send + Sync {
    fn now_ns(&self) -> u64;
    fn sleep(&self, duration: Duration);
}
pub struct HostClock;
impl Clock for HostClock {
    fn now_ns(&self) -> u64 {
        hsm_pgfun_observation::monotonic_ns()
    }
    fn sleep(&self, duration: Duration) {
        thread::sleep(duration);
    }
}

pub struct SerialTransport {
    port: Option<Box<dyn serialport::SerialPort>>,
}
impl SerialTransport {
    pub fn open(path: &str) -> Result<Self> {
        Ok(Self {
            port: Some(
                serialport::new(path, 115200)
                    .timeout(Duration::from_millis(20))
                    .open()?,
            ),
        })
    }
}
impl Transport for SerialTransport {
    fn read(&mut self, buffer: &mut [u8]) -> std::io::Result<usize> {
        self.port
            .as_mut()
            .ok_or_else(|| {
                std::io::Error::new(
                    std::io::ErrorKind::BrokenPipe,
                    "closed controller transport",
                )
            })?
            .read(buffer)
    }
    fn write_all(&mut self, bytes: &[u8]) -> std::io::Result<()> {
        let port = self.port.as_mut().ok_or_else(|| {
            std::io::Error::new(
                std::io::ErrorKind::BrokenPipe,
                "closed controller transport",
            )
        })?;
        port.set_timeout(Duration::from_millis(100))
            .map_err(std::io::Error::other)?;
        let result = port.write_all(bytes);
        let restored = port
            .set_timeout(Duration::from_millis(20))
            .map_err(std::io::Error::other);
        result.and(restored)
    }
    fn close(&mut self) -> std::io::Result<()> {
        self.port.take();
        Ok(())
    }
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum State {
    Unreferenced,
    Referenced,
    Armed,
    Moving,
    Fault,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Snapshot {
    pub boot: String,
    pub seq: u32,
    pub last_seq: u32,
    pub time_us: u64,
    pub state: State,
    pub fault: String,
    pub referenced: bool,
    pub count: [i32; 2],
    pub completed_seq: u32,
    pub completed_us: u64,
    pub stop_closed: bool,
    pub open_limit_mask: u8,
    pub supply_adc: u16,
    pub drivers_ok: bool,
    pub profile: String,
    pub counts_per_rev: u64,
    pub max_rate: u64,
    pub geometry_sha256: String,
    pub current_scales: [u8; 2],
    pub configured_vsense: [u8; 2],
    pub vsense: [Option<u8>; 2],
    pub microsteps: [Option<u16>; 2],
    #[serde(default)]
    pub vm_epoch: u32,
    #[serde(default)]
    pub timer_ticks: u32,
    #[serde(default)]
    pub pedal_pressed: bool,
    #[serde(default)]
    pub playback_waiting: bool,
    #[serde(default)]
    pub playback_active: bool,
    #[serde(default)]
    pub playback_started_us: u64,
    #[serde(default)]
    pub loaded_knots: usize,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub op: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Driver {
    pub axis: u8,
    pub gstat: u32,
    pub drv_status: u32,
    pub bus: u8,
    pub address: u8,
    pub cs_actual: u8,
    pub configured_cs: u8,
    pub configured_vsense: u8,
    pub sample_valid: bool,
    pub sample_us: u64,
    pub microsteps: Option<u16>,
    pub vsense: Option<u8>,
}
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(tag = "type", rename_all = "lowercase")]
enum Reply {
    Status(Snapshot),
    Ack(Snapshot),
    Stopped(Snapshot),
    Error(Snapshot),
    Driver(Driver),
}
impl Reply {
    fn snapshot(&self) -> Option<&Snapshot> {
        match self {
            Self::Status(s) | Self::Ack(s) | Self::Stopped(s) | Self::Error(s) => Some(s),
            _ => None,
        }
    }
}
#[derive(Debug)]
struct CommandRejected(String);
impl fmt::Display for CommandRejected {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "controller rejected command: {}", self.0)
    }
}
impl std::error::Error for CommandRejected {}

#[derive(Clone)]
pub struct SessionConfig {
    pub reply_timeout: Duration,
    pub heartbeat_interval: Duration,
}
impl Default for SessionConfig {
    fn default() -> Self {
        Self {
            reply_timeout: Duration::from_millis(200),
            heartbeat_interval: Duration::from_millis(100),
        }
    }
}

struct Session<T: Transport> {
    transport: T,
    clock: Arc<dyn Clock>,
    geometry: Geometry,
    config: SessionConfig,
    failure: Option<String>,
    buffer: Vec<u8>,
    boot: Option<String>,
    sequence: u32,
    last: Option<Snapshot>,
    log: Option<File>,
    closed: bool,
}
impl<T: Transport> Session<T> {
    fn record(&mut self, value: &impl Serialize) -> Result<()> {
        if let Some(log) = &mut self.log {
            serde_json::to_writer(&mut *log, value)?;
            log.write_all(b"\n")?;
            log.flush()?;
        }
        Ok(())
    }
    fn read(&mut self, deadline: u64) -> Result<Reply> {
        while self.clock.now_ns() < deadline {
            if let Some(end) = self.buffer.iter().position(|&b| b == b'\n') {
                let tail = self.buffer.split_off(end + 1);
                let mut line = std::mem::replace(&mut self.buffer, tail);
                line.truncate(end);
                if line.iter().all(u8::is_ascii_whitespace) {
                    continue;
                }
                let reply: Reply = serde_json::from_slice(&line).context("controller reply")?;
                self.record(&serde_json::json!({"type":"device_reply","host_receive_ns":self.clock.now_ns(),"device":reply}))?;
                if let Some(snapshot) = reply.snapshot() {
                    let changed = self.boot.as_ref().is_some_and(|old| old != &snapshot.boot);
                    self.boot = Some(snapshot.boot.clone());
                    self.last = Some(snapshot.clone());
                    if changed {
                        let message = "controller reset: recover and re-establish the datum";
                        self.failure = Some(message.into());
                        bail!("{message}");
                    }
                }
                return Ok(reply);
            }
            let mut chunk = [0_u8; 4096];
            match self.transport.read(&mut chunk) {
                Ok(length) => {
                    self.buffer.extend_from_slice(&chunk[..length]);
                    ensure!(
                        self.buffer.len() <= 8192,
                        "malformed or overlong controller response"
                    );
                    if length == 0 {
                        self.clock.sleep(Duration::from_millis(1));
                    }
                }
                Err(error)
                    if matches!(
                        error.kind(),
                        std::io::ErrorKind::TimedOut | std::io::ErrorKind::WouldBlock
                    ) =>
                {
                    self.clock.sleep(Duration::from_millis(1))
                }
                Err(error) => return Err(error.into()),
            }
        }
        bail!("no complete controller reply before the deadline")
    }
    fn exchange(
        &mut self,
        command: &str,
        desired: &str,
        sequence: Option<u32>,
        operation: Option<&str>,
    ) -> Result<Snapshot> {
        let sent = self.clock.now_ns();
        self.record(
            &serde_json::json!({"type":"host_command","host_send_ns":sent,"command":command}),
        )?;
        ensure!(command.is_ascii(), "controller commands use ASCII");
        self.transport
            .write_all(format!("{command}\n").as_bytes())?;
        let deadline = self.clock.now_ns() + self.config.reply_timeout.as_nanos() as u64;
        loop {
            let reply = self.read(deadline)?;
            let Some(snapshot) = reply.snapshot() else {
                continue;
            };
            let matches_op = operation.is_none_or(|op| snapshot.op.as_deref() == Some(op));
            if matches!(reply, Reply::Error(_))
                && matches_op
                && sequence.is_none_or(|seq| snapshot.seq == 0 || snapshot.seq == seq)
            {
                return Err(CommandRejected(
                    snapshot.error.clone().unwrap_or_else(|| "unknown".into()),
                )
                .into());
            }
            let matches_kind = matches!(
                (&reply, desired),
                (Reply::Status(_), "status")
                    | (Reply::Ack(_), "ack")
                    | (Reply::Stopped(_), "stopped")
            );
            if matches_kind && matches_op && sequence.is_none_or(|seq| snapshot.seq == seq) {
                self.record(&serde_json::json!({"type":"clock_bracket","host_send_ns":sent,"host_receive_ns":self.clock.now_ns(),"device_time_us":snapshot.time_us,"boot":snapshot.boot}))?;
                return Ok(snapshot.clone());
            }
        }
    }
    fn status(&mut self) -> Result<Snapshot> {
        self.exchange("STATUS", "status", None, None)
    }
    fn stop(&mut self) -> Result<Snapshot> {
        self.exchange("STOP", "stopped", None, Some("STOP"))
    }
    fn request(&mut self, operation: &str, args: &[String]) -> Result<Snapshot> {
        ensure!(
            self.failure.is_none(),
            "host session failed; stop and re-reference"
        );
        let sequence = self
            .sequence
            .checked_add(1)
            .context("controller sequence exhausted")?;
        let boot = self.boot.as_ref().context("controller boot identity")?;
        let mut command = format!("{operation} {boot} {sequence}");
        for argument in args {
            command.push(' ');
            command.push_str(argument);
        }
        let result = self.exchange(&command, "ack", Some(sequence), Some(operation));
        match result {
            Ok(reply) => {
                self.sequence = sequence;
                Ok(reply)
            }
            Err(error) if error.downcast_ref::<CommandRejected>().is_some() => Err(error),
            Err(error) => {
                self.failure = Some(error.to_string());
                let _ = self.stop();
                if let Ok(snapshot) = self.status() {
                    self.sequence = snapshot.last_seq;
                }
                Err(error)
            }
        }
    }
}

pub struct Client<T: Transport + 'static> {
    session: Arc<Mutex<Session<T>>>,
    shutdown: Arc<AtomicBool>,
    heartbeat: Option<JoinHandle<()>>,
}
impl Client<SerialTransport> {
    pub fn open(path: &str, geometry: Geometry, log: Option<&std::path::Path>) -> Result<Self> {
        let log = log
            .map(|path| {
                std::fs::OpenOptions::new()
                    .append(true)
                    .create(true)
                    .open(path)
            })
            .transpose()?;
        Self::with_transport(
            SerialTransport::open(path)?,
            geometry,
            Arc::new(HostClock),
            SessionConfig::default(),
            log,
        )
    }
}
impl<T: Transport + 'static> Client<T> {
    pub fn with_transport(
        transport: T,
        geometry: Geometry,
        clock: Arc<dyn Clock>,
        config: SessionConfig,
        log: Option<File>,
    ) -> Result<Self> {
        let mut session = Session {
            transport,
            clock,
            geometry,
            config,
            failure: None,
            buffer: vec![],
            boot: None,
            sequence: 0,
            last: None,
            log,
            closed: false,
        };
        let status = match session.status().and_then(|status| {
            check_profile(&status, &session.geometry)?;
            Ok(status)
        }) {
            Ok(status) => status,
            Err(error) => {
                let _ = session.transport.close();
                return Err(error);
            }
        };
        session.sequence = status.last_seq;
        Ok(Self {
            session: Arc::new(Mutex::new(session)),
            shutdown: Arc::new(AtomicBool::new(false)),
            heartbeat: None,
        })
    }
    fn lock(&self) -> Result<std::sync::MutexGuard<'_, Session<T>>> {
        self.session
            .lock()
            .map_err(|_| anyhow::anyhow!("controller session lock poisoned"))
    }
    pub fn status(&self) -> Result<Snapshot> {
        ensure!(!crate::interrupted(), "host interrupted");
        self.lock()?.status()
    }
    pub fn stop(&self) -> Result<Snapshot> {
        self.lock()?.stop()
    }
    pub fn request(&self, operation: &str, args: &[String]) -> Result<Snapshot> {
        ensure!(!crate::interrupted(), "host interrupted");
        self.lock()?.request(operation, args)
    }
    pub fn failure(&self) -> Result<Option<String>> {
        Ok(self.lock()?.failure.clone())
    }
    pub fn clock(&self) -> Result<Arc<dyn Clock>> {
        Ok(Arc::clone(&self.lock()?.clock))
    }
    fn end_heartbeat(&mut self, timeout: Duration) -> Result<()> {
        self.shutdown.store(true, Ordering::Release);
        if let Some(handle) = self.heartbeat.take() {
            let deadline = Instant::now() + timeout;
            while !handle.is_finished() && Instant::now() < deadline {
                thread::sleep(Duration::from_millis(1));
            }
            if !handle.is_finished() {
                self.heartbeat = Some(handle);
                self.lock()?.failure =
                    Some("heartbeat thread did not stop; reconnect the console".into());
                bail!("heartbeat thread did not stop; reconnect the console");
            }
            handle
                .join()
                .map_err(|_| anyhow::anyhow!("heartbeat thread panicked"))?;
        }
        Ok(())
    }
    pub fn recover(&mut self) -> Result<Snapshot> {
        self.end_heartbeat(Duration::from_secs(1))?;
        let result = {
            let mut session = self.lock()?;
            session
                .stop()
                .and_then(|_| session.status())
                .and_then(|snapshot| {
                    check_profile(&snapshot, &session.geometry)?;
                    Ok(snapshot)
                })
        };
        match result {
            Ok(snapshot) => {
                let mut session = self.lock()?;
                session.sequence = snapshot.last_seq;
                session.failure = None;
                drop(session);
                self.shutdown.store(false, Ordering::Release);
                Ok(snapshot)
            }
            Err(error) => {
                self.lock()?.failure = Some(error.to_string());
                Err(error)
            }
        }
    }
    pub fn start_heartbeat(&mut self) -> Result<()> {
        ensure!(
            self.lock()?.failure.is_none(),
            "use explicit recover before restarting heartbeat"
        );
        if self
            .heartbeat
            .as_ref()
            .is_some_and(|handle| !handle.is_finished())
        {
            return Ok(());
        }
        let session = Arc::clone(&self.session);
        let shutdown = Arc::clone(&self.shutdown);
        let interval = self.lock()?.config.heartbeat_interval;
        self.heartbeat = Some(thread::spawn(move || {
            while !shutdown.load(Ordering::Acquire) {
                let until = Instant::now() + interval;
                while Instant::now() < until && !shutdown.load(Ordering::Acquire) {
                    thread::sleep(Duration::from_millis(1));
                }
                if shutdown.load(Ordering::Acquire) {
                    break;
                }
                let Ok(mut session) = session.lock() else {
                    break;
                };
                if let Err(error) = session.request("PING", &[]) {
                    session.failure = Some(error.to_string());
                    let _ = session.transport.write_all(b"STOP\n");
                    break;
                }
            }
        }));
        Ok(())
    }
    pub fn move_counts(&self, delta: [i32; 2], duration_us: u64) -> Result<Snapshot> {
        ensure!(
            delta
                .iter()
                .all(|v| i64::from(*v).abs() <= MAX_JOG_COUNTS as i64)
                && delta != [0, 0],
            "bounded nonzero two-axis count deltas required"
        );
        ensure!(
            (MIN_DURATION_US..=MAX_DURATION_US).contains(&duration_us),
            "move duration outside the controller interval"
        );
        let accepted = self.request(
            "MOVE2",
            &[
                duration_us.to_string(),
                delta[0].to_string(),
                delta[1].to_string(),
            ],
        )?;
        let clock = Arc::clone(&self.lock()?.clock);
        let deadline = clock.now_ns() + duration_us * 1000 + 500_000_000;
        while clock.now_ns() < deadline {
            let status = match self.status() {
                Ok(value) => value,
                Err(error) => {
                    let _ = self.stop();
                    return Err(error);
                }
            };
            if status.state == State::Fault {
                let _ = self.stop();
                bail!("motion fault: {}", status.fault);
            }
            if status.completed_seq == accepted.seq {
                return Ok(status);
            }
            clock.sleep(Duration::from_millis(30));
        }
        let _ = self.stop();
        bail!("move completion absent; reference invalidated")
    }
    pub fn move_to_counts(&self, target: [i32; 2], duration_us: u64) -> Result<Snapshot> {
        let mut current = self.status()?;
        ensure!(
            current.state == State::Armed && current.referenced,
            "a healthy armed physical reference is required"
        );
        let segments = self.lock()?.geometry.split_target(current.count, target)?;
        for segment in segments {
            current = self.move_counts(segment, duration_us)?;
        }
        Ok(current)
    }
    pub fn establish(&mut self) -> Result<()> {
        self.recover()?;
        self.request("CLEAR", &[])?;
        self.request("REF", &[])?;
        self.request("ARM", &[])?;
        self.start_heartbeat()
    }
    pub fn load_trajectory(&self, profile: &crate::trajectory::Profile) -> Result<Snapshot> {
        ensure!(
            profile.geometry_sha256 == self.lock()?.geometry.sha256,
            "trajectory geometry mismatch"
        );
        self.request(
            "LOAD2",
            &[
                profile.period_us.to_string(),
                profile.knots.len().to_string(),
            ],
        )?;
        for (index, knot) in profile.knots.iter().enumerate() {
            self.request(
                "KNOT",
                &[index.to_string(), knot[0].to_string(), knot[1].to_string()],
            )?;
        }
        self.move_to_counts(profile.knots[0], 1_000_000)?;
        self.request("PLAY", &[])
    }
    pub fn drivers(&self) -> Result<[Driver; 2]> {
        let mut session = self.lock()?;
        session.transport.write_all(b"DRIVERS\n")?;
        let deadline = session.clock.now_ns() + session.config.reply_timeout.as_nanos() as u64;
        let mut rows: [Option<Driver>; 2] = [None, None];
        while rows.iter().any(Option::is_none) {
            if let Reply::Driver(row) = session.read(deadline)? {
                let axis = row.axis as usize;
                ensure!(axis < 2, "unknown controller driver axis");
                rows[axis] = Some(row);
            }
        }
        Ok(rows.map(Option::unwrap))
    }
    pub fn close(&mut self) -> Result<()> {
        let _ = self.end_heartbeat(Duration::from_millis(300));
        let mut session = self.lock()?;
        if !session.closed {
            let _ = session.stop();
            session.transport.close()?;
            session.log.take();
            session.closed = true;
        }
        Ok(())
    }
}
impl<T: Transport + 'static> Drop for Client<T> {
    fn drop(&mut self) {
        let _ = self.close();
    }
}

pub fn check_profile(status: &Snapshot, geometry: &Geometry) -> Result<()> {
    ensure!(
        status.profile == "pgfun-50-64"
            && status.counts_per_rev == geometry.counts_per_rev()?
            && status.geometry_sha256 == geometry.sha256
            && status.current_scales == [13, 13]
            && status.configured_vsense == [0, 0]
            && status.max_rate == MAX_RATE
            && (!status.drivers_ok
                || (status.vsense == [Some(0), Some(0)]
                    && status.microsteps == [Some(64), Some(64)])),
        "controller or geometry does not match this package"
    );
    Ok(())
}
