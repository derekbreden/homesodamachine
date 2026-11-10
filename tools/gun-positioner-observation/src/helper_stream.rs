//! The capture helper's framed stream and launch lifecycle preserve its app-owned camera permission.
use crate::capture::{Codec, RawFrame, SourceItem};
use anyhow::{Context, Result, bail, ensure};
use serde::Deserialize;
use serde_json::{Value, json};
use std::{
    collections::BTreeMap,
    fs::{File, OpenOptions},
    io::Read,
    os::unix::{fs::OpenOptionsExt, io::AsRawFd},
    path::{Path, PathBuf},
    process::{Child, Command, Stdio},
    sync::{
        Arc,
        atomic::{AtomicBool, Ordering},
        mpsc::{self, Receiver, SyncSender, TrySendError},
    },
    thread::{self, JoinHandle},
    time::{Duration, Instant},
};

pub const MAGIC: &[u8; 4] = b"GPO1";
pub struct Message {
    pub header: Value,
    pub payload: Vec<u8>,
}
fn exact(reader: &mut impl Read, length: usize) -> Result<Vec<u8>> {
    let mut bytes = vec![0; length];
    let mut used = 0;
    while used < length {
        match reader.read(&mut bytes[used..]) {
            Ok(0) => break,
            Ok(n) => used += n,
            Err(e) if e.kind() == std::io::ErrorKind::Interrupted => continue,
            Err(e) => return Err(e.into()),
        }
    }
    bytes.truncate(used);
    Ok(bytes)
}
pub fn read_message(reader: &mut impl Read) -> Result<Option<Message>> {
    let header = exact(reader, 12)?;
    if header.is_empty() {
        return Ok(None);
    }
    ensure!(header.len() == 12, "stream ended inside a message header");
    ensure!(&header[..4] == MAGIC, "bad capture stream magic");
    let header_length = u32::from_le_bytes(header[4..8].try_into()?) as usize;
    let payload_length = u32::from_le_bytes(header[8..12].try_into()?) as usize;
    ensure!(
        header_length <= 1 << 20 && payload_length <= 256 << 20,
        "implausible capture message length"
    );
    let header = exact(reader, header_length)?;
    let payload = exact(reader, payload_length)?;
    ensure!(
        header.len() == header_length && payload.len() == payload_length,
        "stream ended inside a message body"
    );
    Ok(Some(Message {
        header: serde_json::from_slice(&header)?,
        payload,
    }))
}
pub fn encode_message(header: &Value, payload: &[u8]) -> Result<Vec<u8>> {
    let header = serde_json::to_vec(header)?;
    let mut bytes = MAGIC.to_vec();
    bytes.extend_from_slice(&u32::try_from(header.len())?.to_le_bytes());
    bytes.extend_from_slice(&u32::try_from(payload.len())?.to_le_bytes());
    bytes.extend(header);
    bytes.extend_from_slice(payload);
    Ok(bytes)
}
#[derive(Deserialize)]
struct FrameHeader {
    codec: Option<Codec>,
    width: Option<usize>,
    height: Option<usize>,
    seq: Option<u64>,
    pts_ns: Option<u64>,
    host_ns: Option<u64>,
    duration_ns: Option<u64>,
    subtype: Option<String>,
}
pub fn to_item(message: Message) -> Result<SourceItem> {
    let mut header = message
        .header
        .as_object()
        .context("capture message header object")?
        .clone();
    let kind = header
        .remove("type")
        .and_then(|v| v.as_str().map(str::to_owned))
        .unwrap_or_else(|| "unknown".into());
    if kind == "frame" {
        let frame: FrameHeader = serde_json::from_value(Value::Object(header))?;
        return Ok(SourceItem::Frame(RawFrame {
            payload: message.payload,
            codec: frame.codec.unwrap_or(Codec::Jpeg),
            width: frame.width,
            height: frame.height,
            source_seq: frame.seq,
            device_pts_ns: frame.pts_ns,
            source_host_ns: frame.host_ns,
            duration_ns: frame.duration_ns,
            subtype: frame.subtype,
        }));
    }
    if kind == "drop" {
        return Ok(SourceItem::Drop {
            device_pts_ns: header.get("pts_ns").and_then(Value::as_u64),
            reason: header
                .get("reason")
                .and_then(Value::as_str)
                .filter(|s| !s.is_empty())
                .unwrap_or("unspecified")
                .into(),
        });
    }
    Ok(SourceItem::Event {
        event: kind,
        detail: header.into_iter().collect(),
    })
}

#[derive(Clone, Debug)]
pub struct HelperPaths {
    pub app: PathBuf,
    pub binary: PathBuf,
}
impl HelperPaths {
    pub fn in_root(root: &Path) -> Self {
        let app = root.join("tools/gun-positioner-observation/helper/build/GPOCapture.app");
        let binary = app.join("Contents/MacOS/GPOCapture");
        Self { app, binary }
    }
}
#[derive(Clone, Copy, Debug)]
pub enum LaunchMode {
    Exec,
    Open,
}

struct Pipe {
    reader: Box<dyn Read + Send>,
    stop: Arc<AtomicBool>,
    deadline: Option<Instant>,
}
impl Read for Pipe {
    fn read(&mut self, out: &mut [u8]) -> std::io::Result<usize> {
        loop {
            if self.stop.load(Ordering::Acquire) {
                return Ok(0);
            }
            if self
                .deadline
                .is_some_and(|deadline| Instant::now() >= deadline)
            {
                return Err(std::io::Error::new(
                    std::io::ErrorKind::TimedOut,
                    "capture helper did not connect its output",
                ));
            }
            match self.reader.read(out) {
                Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                    thread::sleep(Duration::from_millis(1))
                }
                other => return other,
            }
        }
    }
}
fn nonblocking(fd: std::os::fd::RawFd) -> Result<()> {
    let flags = unsafe { libc::fcntl(fd, libc::F_GETFL) };
    ensure!(
        flags >= 0,
        "capture pipe flags: {}",
        std::io::Error::last_os_error()
    );
    ensure!(
        unsafe { libc::fcntl(fd, libc::F_SETFL, flags | libc::O_NONBLOCK) } >= 0,
        "capture pipe mode: {}",
        std::io::Error::last_os_error()
    );
    Ok(())
}
struct HelperProcess {
    child: Child,
    reader: Option<Pipe>,
    keeper: Option<File>,
    directory: Option<PathBuf>,
    mode: LaunchMode,
    stop: Arc<AtomicBool>,
}
impl HelperProcess {
    fn launch(
        paths: &HelperPaths,
        args: &[String],
        mode: LaunchMode,
        log: Option<&Path>,
    ) -> Result<Self> {
        let suffix = format!("{}-{}", std::process::id(), crate::monotonic_ns());
        let log = log
            .map(PathBuf::from)
            .unwrap_or_else(|| std::env::temp_dir().join(format!("gpocapture-{suffix}.log")));
        let stop = Arc::new(AtomicBool::new(false));
        let (child, reader, keeper, directory) = match mode {
            LaunchMode::Exec => {
                ensure!(
                    paths.binary.is_file(),
                    "build the capture helper before starting it"
                );
                let error = OpenOptions::new().create(true).append(true).open(&log)?;
                let mut child = Command::new(&paths.binary)
                    .args(args)
                    .stdout(Stdio::piped())
                    .stderr(error)
                    .spawn()?;
                let stdout = child.stdout.take().context("capture helper output")?;
                nonblocking(stdout.as_raw_fd())?;
                (child, Box::new(stdout) as Box<dyn Read + Send>, None, None)
            }
            LaunchMode::Open => {
                ensure!(
                    paths.app.is_dir(),
                    "build the capture helper app before starting it"
                );
                let directory = std::env::temp_dir().join(format!("gpocapture-{suffix}"));
                std::fs::create_dir(&directory)?;
                let fifo = directory.join("stream");
                use std::os::unix::ffi::OsStrExt;
                let name = std::ffi::CString::new(fifo.as_os_str().as_bytes())?;
                ensure!(
                    unsafe { libc::mkfifo(name.as_ptr(), 0o600) } == 0,
                    "capture FIFO: {}",
                    std::io::Error::last_os_error()
                );
                let reader = OpenOptions::new()
                    .read(true)
                    .custom_flags(libc::O_NONBLOCK)
                    .open(&fifo)?;
                let keeper = OpenOptions::new()
                    .write(true)
                    .custom_flags(libc::O_NONBLOCK)
                    .open(&fifo)?;
                let child = Command::new("open")
                    .args(["-n", "-W", "-g", "-o"])
                    .arg(&fifo)
                    .arg("--stderr")
                    .arg(&log)
                    .arg(&paths.app)
                    .arg("--args")
                    .args(args)
                    .spawn()?;
                (
                    child,
                    Box::new(reader) as Box<dyn Read + Send>,
                    Some(keeper),
                    Some(directory),
                )
            }
        };
        Ok(Self {
            child,
            reader: Some(Pipe {
                reader,
                stop: Arc::clone(&stop),
                deadline: Some(Instant::now() + Duration::from_secs(20)),
            }),
            keeper,
            directory,
            mode,
            stop,
        })
    }
    fn stop(&mut self) -> Result<()> {
        self.stop.store(true, Ordering::Release);
        self.reader.take();
        self.keeper.take();
        if self.child.try_wait()?.is_none() && matches!(self.mode, LaunchMode::Exec) {
            unsafe {
                libc::kill(self.child.id() as i32, libc::SIGTERM);
            }
        }
        let deadline = Instant::now() + Duration::from_secs(3);
        while self.child.try_wait()?.is_none() && Instant::now() < deadline {
            thread::sleep(Duration::from_millis(10));
        }
        if self.child.try_wait()?.is_none() {
            self.child.kill()?;
            self.child.wait()?;
        }
        if let Some(directory) = self.directory.take() {
            let _ = std::fs::remove_dir_all(directory);
        }
        Ok(())
    }
}
impl Drop for HelperProcess {
    fn drop(&mut self) {
        let _ = self.stop();
    }
}

pub struct HelperSource {
    pub camera_id: String,
    pub unique_id: String,
    pub name: String,
    paths: HelperPaths,
    args: Vec<String>,
    mode: LaunchMode,
    log: Option<PathBuf>,
    process: Option<HelperProcess>,
    receiver: Option<Receiver<Option<SourceItem>>>,
    pump: Option<JoinHandle<()>>,
}
#[derive(Clone)]
pub struct CaptureOptions {
    pub width: usize,
    pub height: usize,
    pub fps: f64,
    pub subtypes: String,
    pub chroma: bool,
    pub mode: LaunchMode,
    pub log: Option<PathBuf>,
    pub extra_args: Vec<String>,
}
impl Default for CaptureOptions {
    fn default() -> Self {
        Self {
            width: 3840,
            height: 2160,
            fps: 30.,
            subtypes: "dmb1,jpeg,420v,420f,yuvs,2vuy".into(),
            chroma: false,
            mode: LaunchMode::Open,
            log: None,
            extra_args: vec![],
        }
    }
}
fn deliver(
    sender: &SyncSender<Option<SourceItem>>,
    mut item: Option<SourceItem>,
    stop: &AtomicBool,
) -> bool {
    loop {
        if stop.load(Ordering::Acquire) {
            return false;
        }
        match sender.try_send(item) {
            Ok(()) => return true,
            Err(TrySendError::Disconnected(_)) => return false,
            Err(TrySendError::Full(value)) => {
                item = value;
                thread::sleep(Duration::from_millis(1));
            }
        }
    }
}
impl HelperSource {
    pub fn capture(
        paths: HelperPaths,
        camera_id: &str,
        unique_id: &str,
        options: CaptureOptions,
    ) -> Self {
        let mut args = vec![
            "capture".into(),
            "--unique-id".into(),
            unique_id.into(),
            "--width".into(),
            options.width.to_string(),
            "--height".into(),
            options.height.to_string(),
            "--fps".into(),
            options.fps.to_string(),
            "--subtypes".into(),
            options.subtypes,
            "--chroma".into(),
            if options.chroma { "1" } else { "0" }.into(),
        ];
        args.extend(options.extra_args);
        Self {
            camera_id: camera_id.into(),
            unique_id: unique_id.into(),
            name: String::new(),
            paths,
            args,
            mode: options.mode,
            log: options.log,
            process: None,
            receiver: None,
            pump: None,
        }
    }
    pub fn start(&mut self) -> Result<Value> {
        let mut process =
            HelperProcess::launch(&self.paths, &self.args, self.mode, self.log.as_deref())?;
        let mut reader = process.reader.take().context("capture helper stream")?;
        let first =
            read_message(&mut reader)?.context("capture helper ended before its greeting")?;
        ensure!(
            first.header.get("type").and_then(Value::as_str) == Some("hello"),
            "capture helper did not start capture: {}",
            first.header
        );
        process.keeper.take();
        reader.deadline = None;
        let stop = Arc::clone(&process.stop);
        let (sender, receiver) = mpsc::sync_channel(4);
        self.pump = Some(thread::spawn(move || {
            loop {
                match read_message(&mut reader).and_then(|message| message.map(to_item).transpose())
                {
                    Ok(Some(item)) => {
                        if !deliver(&sender, Some(item), &stop) {
                            return;
                        }
                    }
                    Ok(None) => break,
                    Err(error) => {
                        let mut detail = BTreeMap::new();
                        detail.insert("error".into(), json!(error.to_string()));
                        deliver(
                            &sender,
                            Some(SourceItem::Event {
                                event: "stream_error".into(),
                                detail,
                            }),
                            &stop,
                        );
                        break;
                    }
                }
            }
            deliver(&sender, None, &stop);
        }));
        self.receiver = Some(receiver);
        self.process = Some(process);
        let mut hello = first.header;
        let object = hello.as_object_mut().context("capture greeting object")?;
        object.insert("kind".into(), json!("gpocapture"));
        object.insert(
            "launch".into(),
            json!(match self.mode {
                LaunchMode::Exec => "exec",
                LaunchMode::Open => "open",
            }),
        );
        Ok(hello)
    }
    pub fn read(
        &self,
        timeout: Duration,
    ) -> std::result::Result<Option<SourceItem>, mpsc::RecvTimeoutError> {
        match &self.receiver {
            Some(receiver) => receiver.recv_timeout(timeout),
            None => Err(mpsc::RecvTimeoutError::Disconnected),
        }
    }
    pub fn stop(&mut self) -> Result<()> {
        if let Some(process) = &self.process {
            process.stop.store(true, Ordering::Release);
        }
        self.receiver.take();
        if let Some(pump) = self.pump.take() {
            let _ = pump.join();
        }
        if let Some(mut process) = self.process.take() {
            process.stop()?;
        }
        Ok(())
    }
}
impl Drop for HelperSource {
    fn drop(&mut self) {
        let _ = self.stop();
    }
}

pub fn run_json(program: &Path, args: &[String], timeout: Duration) -> Result<Value> {
    let mut child = Command::new(program)
        .args(args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()?;
    let mut stdout = child.stdout.take().context("helper JSON output")?;
    let mut stderr = child.stderr.take().context("helper diagnostics")?;
    let output = thread::spawn(move || {
        let mut data = vec![];
        stdout.read_to_end(&mut data).map(|_| data)
    });
    let errors = thread::spawn(move || {
        let mut data = vec![];
        stderr.read_to_end(&mut data).map(|_| data)
    });
    let deadline = Instant::now() + timeout;
    let status = loop {
        if let Some(status) = child.try_wait()? {
            break status;
        }
        if Instant::now() >= deadline {
            child.kill()?;
            child.wait()?;
            let _ = output.join();
            let _ = errors.join();
            bail!("helper command timed out");
        }
        thread::sleep(Duration::from_millis(10));
    };
    let bytes = output
        .join()
        .map_err(|_| anyhow::anyhow!("helper output reader panicked"))??;
    let errors = errors
        .join()
        .map_err(|_| anyhow::anyhow!("helper diagnostics reader panicked"))??;
    ensure!(
        status.success(),
        "helper command failed: {}",
        String::from_utf8_lossy(&errors)
    );
    Ok(serde_json::from_slice(&bytes)?)
}
pub fn list_cameras(paths: &HelperPaths) -> Result<Value> {
    if paths.binary.is_file() {
        return Ok(
            json!({"source":"GPOCapture list","devices":run_json(&paths.binary,&["list".into()],Duration::from_secs(20))?}),
        );
    }
    let data = run_json(
        Path::new("system_profiler"),
        &["SPCameraDataType".into(), "-json".into()],
        Duration::from_secs(60),
    )?;
    let devices=data.get("SPCameraDataType").and_then(Value::as_array).map(|items|items.iter().map(|d|json!({"unique_id":d.get("spcamera_unique-id"),"name":d.get("_name"),"model_id":d.get("spcamera_model-id"),"formats":null})).collect::<Vec<_>>()).unwrap_or_default();
    Ok(json!({"source":"system_profiler SPCameraDataType","devices":devices}))
}
pub fn clock_check(paths: &HelperPaths) -> Result<Value> {
    let before = crate::monotonic_ns();
    let mut data = run_json(&paths.binary, &["clock".into()], Duration::from_secs(20))?;
    let after = crate::monotonic_ns();
    let object = data.as_object_mut().context("helper clock object")?;
    let within = |name: &str| {
        object
            .get(name)
            .and_then(Value::as_u64)
            .is_some_and(|value| before <= value && value <= after)
    };
    let uptime = within("uptime_raw_ns");
    let host = within("host_time_clock_ns");
    object.insert("host_before_ns".into(), json!(before));
    object.insert("host_after_ns".into(), json!(after));
    object.insert("uptime_raw_within_bracket".into(), json!(uptime));
    object.insert("host_time_clock_within_bracket".into(), json!(host));
    Ok(data)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Cursor;
    struct ShortReads(Cursor<Vec<u8>>);
    impl Read for ShortReads {
        fn read(&mut self, buffer: &mut [u8]) -> std::io::Result<usize> {
            let length = buffer.len().min(3);
            self.0.read(&mut buffer[..length])
        }
    }
    #[test]
    fn fragmented_messages_keep_frames_drops_and_events_in_order() {
        let headers = [
            json!({"type":"hello","mode":"capture","unique_id":"saved-camera"}),
            json!({"type":"frame","seq":1,"pts_ns":10,"host_ns":12,"duration_ns":33,"codec":"gray8","width":4,"height":3,"subtype":"420v"}),
            json!({"type":"frame","seq":2,"codec":"jpeg","width":3840,"height":2160}),
            json!({"type":"drop","pts_ns":99,"reason":"OutOfBuffers"}),
            json!({"type":"bye","frames":2,"drops":1}),
        ];
        let payloads = [vec![], (0..12).collect(), vec![0xff, 0xd8], vec![], vec![]];
        let mut bytes = vec![];
        for (header, payload) in headers.iter().zip(payloads) {
            bytes.extend(encode_message(header, &payload).unwrap());
        }
        let mut reader = ShortReads(Cursor::new(bytes));
        let mut items = vec![];
        while let Some(message) = read_message(&mut reader).unwrap() {
            items.push(to_item(message).unwrap());
        }
        assert!(
            matches!(&items[0],SourceItem::Event {event,detail}if event=="hello"&&detail["unique_id"]=="saved-camera")
        );
        let SourceItem::Frame(frame) = &items[1] else {
            panic!("saved gray frame");
        };
        assert_eq!(frame.codec, Codec::Gray8);
        assert_eq!(frame.source_seq, Some(1));
        assert_eq!(frame.device_pts_ns, Some(10));
        assert_eq!(frame.source_host_ns, Some(12));
        assert_eq!(frame.payload, (0..12).collect::<Vec<u8>>());
        assert!(matches!(&items[2],SourceItem::Frame(frame)if frame.codec==Codec::Jpeg));
        assert!(matches!(&items[3],SourceItem::Drop {reason,..}if reason=="OutOfBuffers"));
        assert!(matches!(&items[4],SourceItem::Event {event,..}if event=="bye"));
    }
    #[test]
    fn partial_or_corrupt_messages_are_rejected() {
        let good =
            encode_message(&json!({"type":"frame","seq":1,"codec":"jpeg"}), b"abcdef").unwrap();
        for corrupt in [
            good[..good.len() - 2].to_vec(),
            good[..7].to_vec(),
            [b"XXXX".as_slice(), &good[4..]].concat(),
        ] {
            assert!(read_message(&mut Cursor::new(corrupt)).is_err());
        }
        assert!(
            read_message(&mut Cursor::new(Vec::<u8>::new()))
                .unwrap()
                .is_none()
        );
        let mut oversized = good;
        oversized[8..12].copy_from_slice(&u32::MAX.to_le_bytes());
        assert!(read_message(&mut Cursor::new(oversized)).is_err());
    }
}
