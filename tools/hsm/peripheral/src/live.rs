//! Manual display checks measure the existing USB diagnostics and restore explicit test operations.
use crate::{flag, option, serials, validate_args};
use anyhow::{Context, Result, bail, ensure};
use serialport::{ClearBuffer, SerialPort};
use std::{
    collections::BTreeMap,
    thread,
    time::{Duration, Instant},
};

type Fields = BTreeMap<String, String>;
fn fields(line: &str, prefix: &str) -> Result<Fields> {
    Ok(line
        .strip_prefix(prefix)
        .with_context(|| format!("expected {prefix}, got {line:?}"))?
        .split(',')
        .filter_map(|part| part.split_once('='))
        .map(|(k, v)| (k.to_owned(), v.to_owned()))
        .collect())
}
fn value<'a>(fields: &'a Fields, key: &str) -> &'a str {
    fields.get(key).map_or("", String::as_str)
}
fn number(fields: &Fields, key: &str, default: i64) -> Result<i64> {
    fields.get(key).map_or(Ok(default), |v| {
        v.parse()
            .with_context(|| format!("diagnostic {key} is not an integer: {v}"))
    })
}
fn same(before: &Fields, after: &Fields, keys: &[&str]) -> Result<()> {
    for key in keys {
        ensure!(
            number(before, key, 0)? == number(after, key, 0)?,
            "diagnostic {key} changed: {} -> {}",
            value(before, key),
            value(after, key)
        );
    }
    Ok(())
}
fn wait(seconds: f64) {
    thread::sleep(Duration::from_secs_f64(seconds));
}
fn argument<T: std::str::FromStr>(args: &[String], key: &str, default: T) -> Result<T>
where
    T::Err: std::fmt::Display,
{
    option(args, key)?.map_or(Ok(default), |s| {
        s.parse().map_err(|e| anyhow::anyhow!("{key}: {e}"))
    })
}
fn finish(result: Result<()>, cleanup: Result<()>) -> Result<()> {
    match (result, cleanup) {
        (Err(error), Err(cleanup)) => {
            eprintln!("cleanup also failed: {cleanup:#}");
            Err(error)
        }
        (Err(error), _) => Err(error),
        (_, cleanup) => cleanup,
    }
}

struct Display {
    port: Box<dyn SerialPort>,
    pending: Vec<u8>,
    preserve: bool,
}
impl Display {
    fn new(path: &str, enclosure: bool) -> Result<Self> {
        let port = serials::open(path, enclosure, Duration::from_millis(50))?;
        if enclosure {
            wait(0.25);
            port.clear(ClearBuffer::Input)?;
        }
        Ok(Self {
            port,
            pending: vec![],
            preserve: !enclosure,
        })
    }
    fn send(&mut self, command: &str) -> Result<Instant> {
        let started = Instant::now();
        serials::send(&mut *self.port, format!("{command}\n").as_bytes())?;
        Ok(started)
    }
    fn line(&mut self, prefix: &str, timeout: f64) -> Result<(String, Instant)> {
        if !self.preserve {
            self.pending.clear();
        }
        let deadline = Instant::now() + Duration::from_secs_f64(timeout);
        while Instant::now() < deadline {
            self.pending.extend(serials::poll(&mut *self.port)?);
            while let Some(index) = self.pending.iter().position(|v| *v == b'\n') {
                let bytes = self.pending.drain(..=index).collect::<Vec<_>>();
                let line = String::from_utf8_lossy(&bytes).trim().to_owned();
                if line.starts_with(prefix) {
                    if !self.preserve {
                        self.pending.clear();
                    }
                    return Ok((line, Instant::now()));
                }
            }
        }
        bail!("timed out waiting for {prefix}")
    }
    fn query_timeout(
        &mut self,
        command: &str,
        prefix: &str,
        timeout: f64,
    ) -> Result<(String, f64)> {
        let started = self.send(command)?;
        let (line, at) = self.line(prefix, timeout)?;
        Ok((line, at.duration_since(started).as_secs_f64() * 1000.0))
    }
    fn query(&mut self, command: &str, prefix: &str) -> Result<String> {
        Ok(self.query_timeout(command, prefix, 1.5)?.0)
    }
    fn data(&mut self, command: &str, prefix: &str) -> Result<Fields> {
        fields(&self.query(command, prefix)?, prefix)
    }
    fn state(&mut self) -> Result<Fields> {
        self.data("GET_STATE", "STATE:")
    }
    fn diag(&mut self) -> Result<Fields> {
        self.data("GET_DIAG", "DIAG:")
    }
    fn panel(&mut self) -> Result<Fields> {
        self.data("GET_PANEL", "PANEL:")
    }
    fn prime_diag(&mut self) -> Result<Fields> {
        self.data("GET_DIAG", "DIAG_PRIME:")
    }
}
fn display_path(args: &[String], name: &str) -> Result<String> {
    if let Some(port) = option(args, name)? {
        return Ok(port);
    }
    let ports = serials::ports_with_id(serials::ESP32_S3)?;
    ensure!(!ports.is_empty(), "display not found on native USB");
    ensure!(
        ports.len() == 1,
        "more than one S3 is connected; name it with {name}"
    );
    Ok(ports[0].port_name.clone())
}

fn faucet_ready(state: &Fields, flavor: Option<i64>) -> bool {
    flavor.is_none_or(|f| value(state, "FLAVOR") == f.to_string())
        && value(state, "SYNC") == "1"
        && value(state, "BASE") == value(state, "FLAVOR")
        && value(state, "PERSISTED") == "1"
        && ["PENDING", "DURABILITYPENDING", "CACHEPENDING"]
            .iter()
            .all(|k| value(state, k) == "0")
}
fn faucet_wait(display: &mut Display, flavor: Option<i64>) -> Result<Fields> {
    let deadline = Instant::now() + Duration::from_secs(6);
    loop {
        let state = display.state()?;
        if faucet_ready(&state, flavor) {
            return Ok(state);
        }
        ensure!(
            Instant::now() < deadline,
            "flavor state did not converge and persist: {state:?}"
        );
        wait(0.1);
    }
}
fn faucet_diag(diag: &Fields, loop_limit: i64, link_limit: i64) -> Result<()> {
    for (key, wanted) in [
        ("base", "up"),
        ("sync", "1"),
        ("basePersisted", "1"),
        ("basePersistErr", "0"),
        ("durabilityPending", "0"),
        ("localPersistErr", "0"),
        ("pending", "0"),
        ("qDrop", "0"),
    ] {
        ensure!(
            value(diag, key) == wanted,
            "faucet {key}={}; expected {wanted}",
            value(diag, key)
        );
    }
    ensure!(
        number(diag, "maxLoopMs", 999999)? <= loop_limit,
        "faucet loop high-water exceeds its limit: {diag:?}"
    );
    ensure!(
        number(diag, "maxLinkUs", 999999)? <= link_limit,
        "J3 service high-water exceeds its limit: {diag:?}"
    );
    Ok(())
}
pub fn faucet(args: &[String]) -> Result<()> {
    ensure!(
        validate_args(
            args,
            &["--toggle"],
            &[
                "--faucet-port",
                "--query-count",
                "--query-p95-ms",
                "--loop-limit-ms",
                "--ack-limit-ms",
                "--link-service-limit-us"
            ]
        )?
        .is_empty(),
        "firmware-faucet-check [--faucet-port PORT] [--toggle]"
    );
    let count = argument(args, "--query-count", 40usize)?;
    ensure!(count > 0, "--query-count must be positive");
    let p95_limit = argument(args, "--query-p95-ms", 15.0f64)?;
    let loop_limit = argument(args, "--loop-limit-ms", 50i64)?;
    let ack_limit = argument(args, "--ack-limit-ms", 250i64)?;
    let link_limit = argument(args, "--link-service-limit-us", 5000i64)?;
    let path = display_path(args, "--faucet-port")?;
    let mut display = Display::new(&path, false)?;
    let deadline = Instant::now() + Duration::from_secs(7);
    let version = loop {
        display.send("GET_VERSION")?;
        if let Ok((line, _)) = display.line("VERSION:FAUCET=", 0.5) {
            break line;
        }
        ensure!(
            Instant::now() < deadline,
            "native USB board did not identify as the faucet display"
        );
    };
    let initial = faucet_wait(&mut display, None)?;
    display.diag()?;
    let mut samples = Vec::with_capacity(count);
    for _ in 0..count {
        let (line, elapsed) = display.query_timeout("GET_STATE", "STATE:", 1.5)?;
        ensure!(
            faucet_ready(&fields(&line, "STATE:")?, None),
            "state changed during latency run: {line}"
        );
        samples.push(elapsed);
    }
    samples.sort_by(f64::total_cmp);
    let p95 = samples[((count as f64 * 0.95).ceil() as usize).saturating_sub(1)];
    let median = if count % 2 == 0 {
        (samples[count / 2 - 1] + samples[count / 2]) / 2.0
    } else {
        samples[count / 2]
    };
    ensure!(
        p95 <= p95_limit,
        "USB query p95 {p95:.2} ms exceeds {p95_limit:.2} ms"
    );
    let diag = display.diag()?;
    faucet_diag(&diag, loop_limit, link_limit)?;
    println!(
        "{version}\nselection   flavor {}, main board and faucet cache persisted\nlatency     USB median {median:.2} ms, p95 {p95:.2} ms; loop {} ms, J3 service {} us\nlink        rx {}, tx {}, retries {}",
        value(&initial, "FLAVOR"),
        value(&diag, "maxLoopMs"),
        value(&diag, "maxLinkUs"),
        value(&diag, "linkRx"),
        value(&diag, "linkTx"),
        value(&diag, "retries")
    );
    if flag(args, "--toggle") {
        let original = number(&initial, "FLAVOR", 0)?;
        let target = original ^ 1;
        let result = (|| -> Result<()> {
            let answer = display.query(&format!("FLAVOR:{target}"), "OK:FLAVOR=")?;
            ensure!(
                answer == format!("OK:FLAVOR={target}"),
                "unexpected selection answer: {answer}"
            );
            faucet_wait(&mut display, Some(target))?;
            let diag = display.diag()?;
            ensure!(
                number(&diag, "lastAckMs", 999999)? <= ack_limit,
                "flavor acknowledgement exceeds its limit"
            );
            println!(
                "toggle      flavor {target}, main board ack {} ms, both stores durable",
                value(&diag, "lastAckMs")
            );
            Ok(())
        })();
        let cleanup = (|| -> Result<()> {
            let answer = display.query(&format!("FLAVOR:{original}"), "OK:FLAVOR=")?;
            ensure!(
                answer == format!("OK:FLAVOR={original}"),
                "restore was not accepted: {answer}"
            );
            faucet_wait(&mut display, Some(original))?;
            println!("restore     flavor {original}, main board and faucet cache durable");
            Ok(())
        })();
        finish(result, cleanup)?;
    }
    println!("faucet firmware check: PASS");
    Ok(())
}

fn restore(display: &mut Display, initial: &Fields) -> Result<()> {
    let page = number(initial, "page", 0)?;
    let stage = number(initial, "stage", 0)?;
    display.query(&format!("PAGE:{page}"), "OK:PAGE=")?;
    if value(initial, "idle") == "1" || stage > 0 {
        display.query(&format!("IDLE:{}", stage.clamp(1, 3)), "OK:IDLE=")?;
    }
    display.query(
        if value(initial, "lock") == "1" {
            "LOCK:SHOW"
        } else {
            "LOCK:HIDE"
        },
        if value(initial, "lock") == "1" {
            "OK:LOCK=1"
        } else {
            "OK:LOCK=0"
        },
    )?;
    Ok(())
}
fn wake(display: &mut Display) -> Result<f64> {
    let before = display.panel()?;
    ensure!(
        value(&before, "kickStage") == "0",
        "panel kick already active"
    );
    display.query("IDLE:1", "OK:IDLE=1")?;
    wait(0.05);
    let dark = display.panel()?;
    ensure!(value(&dark, "bl") == "0", "panel did not go dark");
    let keys = [
        "drawErr",
        "frameTimeout",
        "kickTimeout",
        "phaseErr",
        "scanRecover",
        "exioErr",
    ];
    same(&before, &dark, &keys)?;
    let started = Instant::now();
    display.query("IDLE:0", "OK:IDLE=0")?;
    let deadline = Instant::now() + Duration::from_millis(1500);
    let after = loop {
        let after = display.panel()?;
        if number(&after, "kickStart", 0)? > number(&before, "kickStart", 0)?
            && number(&after, "kickDone", 0)? > number(&before, "kickDone", 0)?
            && value(&after, "kickStage") == "0"
            && value(&after, "bl") == "1"
        {
            break after;
        }
        ensure!(
            Instant::now() < deadline,
            "panel wake did not complete: {after:?}"
        );
        wait(0.02);
    };
    same(&before, &after, &keys)?;
    ensure!(
        number(&after, "phaseDone", 0)? - number(&before, "phaseDone", 0)? >= 2,
        "wake did not phase reset and DISP at VSYNC"
    );
    for key in ["vsync", "frameDone"] {
        ensure!(
            number(&after, key, 0)? - number(&before, key, 0)? >= 4,
            "wake crossed too few {key} events"
        );
    }
    Ok(started.elapsed().as_secs_f64() * 1000.0)
}
fn fresh(display: &mut Display) -> Result<Fields> {
    let mut diag = display.diag()?;
    let mut previous = number(&diag, "ctrlRx", 0)?;
    for _ in 0..2 {
        let deadline = Instant::now() + Duration::from_secs(2);
        let mut requested = None::<Instant>;
        loop {
            if requested.is_none_or(|at| at.elapsed() >= Duration::from_millis(150)) {
                display.query("STATUS", "OK:STATUS requested")?;
                requested = Some(Instant::now());
            }
            diag = display.diag()?;
            let next = number(&diag, "ctrlRx", 0)?;
            if next != previous {
                previous = next;
                break;
            }
            ensure!(
                Instant::now() < deadline,
                "main board status did not refresh: {diag:?}"
            );
            wait(0.02);
        }
    }
    Ok(diag)
}
fn wait_flavor(display: &mut Display, flavor: i64, durable: bool) -> Result<()> {
    let deadline = Instant::now() + Duration::from_secs(4);
    loop {
        let state = display.state()?;
        if value(&state, "FLAVOR") == flavor.to_string()
            && value(&state, "SYNC") == "1"
            && ["PENDING", "PERSISTERR"]
                .iter()
                .all(|k| value(&state, k) == "0")
            && (!durable || value(&state, "PERSISTED") == "1")
        {
            return Ok(());
        }
        ensure!(
            Instant::now() < deadline,
            "flavor {flavor} did not synchronize/persist: {state:?}"
        );
        wait(0.05);
    }
}
fn toggle(display: &mut Display, original: i64, ack_limit: f64, loop_limit: i64) -> Result<()> {
    let target = original ^ 1;
    let result = (|| -> Result<()> {
        let started = display.send(&format!("FLAVOR:{target}"))?;
        let (answer, _) = display.line("OK:FLAVOR=", 1.5)?;
        ensure!(
            answer == format!("OK:FLAVOR={target}"),
            "unexpected selection answer: {answer}"
        );
        wait_flavor(display, target, false)?;
        let ack = started.elapsed().as_secs_f64() * 1000.0;
        ensure!(
            ack <= ack_limit,
            "flavor synchronization {ack:.1} ms exceeds its limit"
        );
        wait_flavor(display, target, true)?;
        let diag = display.diag()?;
        ensure!(
            number(&diag, "maxLoopMs", 999999)? <= loop_limit,
            "flavor repaint loop exceeds its limit"
        );
        println!("flavor     selected {target}, main board ack {ack:.1} ms, durable");
        Ok(())
    })();
    let cleanup = (|| -> Result<()> {
        display.query(&format!("FLAVOR:{original}"), "OK:FLAVOR=")?;
        wait_flavor(display, original, true)?;
        println!("restore    flavor {original}, main board durable");
        Ok(())
    })();
    finish(result, cleanup)
}
fn prime_off(diag: &Fields) -> bool {
    value(diag, "known") == "1"
        && ["phase", "owner", "desired", "cancel", "stop"]
            .iter()
            .all(|k| value(diag, k) == "0")
        && ["session", "hold"]
            .iter()
            .all(|k| i64::from_str_radix(value(diag, k), 16).ok() == Some(0))
}
fn wait_prime_diag(
    display: &mut Display,
    predicate: impl Fn(&Fields) -> bool,
    what: &str,
) -> Result<Fields> {
    let deadline = Instant::now() + Duration::from_secs(3);
    loop {
        let diag = display.prime_diag()?;
        if predicate(&diag) {
            return Ok(diag);
        }
        ensure!(
            Instant::now() < deadline,
            "timed out waiting for {what}: {diag:?}"
        );
        wait(0.02);
    }
}
fn close_prime(display: &mut Display) -> Result<Fields> {
    let mut errors = vec![];
    for (command, prefix) in [
        ("PRIME:STOP", "OK:PRIME:STOP"),
        ("PRIME:EXIT", "OK:PRIME:EXIT"),
    ] {
        if let Err(error) = display.query(command, prefix) {
            errors.push(error.to_string());
        }
    }
    let off = wait_prime_diag(display, prime_off, "authoritative prime OFF");
    ensure!(errors.is_empty(), "{}", errors.join("; "));
    off
}
fn wait_prime_state(display: &mut Display, phase: &str, owner: &str) -> Result<(Fields, Instant)> {
    let deadline = Instant::now() + Duration::from_millis(2500);
    loop {
        let (line, _) = display.query_timeout("GET_STATE", "STATE:", 0.5)?;
        let state = fields(&line, "STATE:")?;
        if value(&state, "PRIME") == phase && value(&state, "OWNER") == owner {
            return Ok((state, Instant::now()));
        }
        ensure!(
            Instant::now() < deadline,
            "prime did not reach phase={phase}, owner={owner}: {state:?}"
        );
        wait(0.01);
    }
}
fn prime(display: &mut Display, initial: &Fields, channel: &str, ack_limit: f64) -> Result<()> {
    ensure!(matches!(channel, "a" | "b"), "--prime must be a or b");
    let flavor = if channel == "a" { 1 } else { 2 };
    let mut session_open = false;
    let result = (|| -> Result<()> {
        let mut before = wait_prime_diag(
            display,
            |d| value(d, "known") == "1",
            "authoritative prime discovery",
        )?;
        if !prime_off(&before) {
            close_prime(display)?;
            before = display.prime_diag()?;
        }
        ensure!(
            prime_off(&before),
            "prime precondition is not authoritative OFF"
        );
        session_open = true;
        let started = display.send(&format!("PRIME:START:{flavor}"))?;
        let (running, answered) = wait_prime_state(display, "2", "1")?;
        ensure!(
            value(&running, "PRIMECH") == format!("{}", flavor - 1),
            "prime ran the wrong channel"
        );
        let start_ms = answered.duration_since(started).as_secs_f64() * 1000.0;
        ensure!(
            start_ms <= ack_limit,
            "prime start acknowledgement exceeds its limit"
        );
        let running_diag = display.prime_diag()?;
        let token = |diag: &Fields, key: &str| {
            i64::from_str_radix(value(diag, key), 16)
                .with_context(|| format!("invalid {key} token"))
        };
        let session = token(&running_diag, "session")?;
        let hold = token(&running_diag, "hold")?;
        ensure!(
            session != 0 && hold != 0,
            "prime did not establish fresh nonzero tokens"
        );
        while answered.elapsed() < Duration::from_secs(1) {
            wait(0.01);
        }
        let stopped = display.send("PRIME:STOP")?;
        let (_, answered) = wait_prime_state(display, "1", "0")?;
        let diag = display.prime_diag()?;
        ensure!(
            value(&diag, "outcome") == "1",
            "prime did not stop normally"
        );
        ensure!(
            token(&diag, "session")? == session && token(&diag, "hold")? == hold,
            "prime terminal state belongs to another run"
        );
        let elapsed = number(&diag, "elapsed", 0)?;
        ensure!(
            (850..=1750).contains(&elapsed),
            "prime elapsed interval outside the requested run bound"
        );
        let stop_ms = answered.duration_since(stopped).as_secs_f64() * 1000.0;
        ensure!(
            stop_ms <= ack_limit,
            "prime stop acknowledgement exceeds its limit"
        );
        let off = close_prime(display)?;
        session_open = false;
        ensure!(prime_off(&off), "display retained prime state after exit");
        println!(
            "prime {}     start ack {start_ms:.1} ms, stop ack {stop_ms:.1} ms, elapsed {elapsed} ms, OFF",
            channel.to_uppercase()
        );
        Ok(())
    })();
    let cleanup = if session_open {
        close_prime(display).map(|_| ())
    } else {
        Ok(())
    };
    let result = finish(result, cleanup);
    let restored = restore(display, initial);
    finish(result, restored)
}

pub fn enclosure(args: &[String]) -> Result<()> {
    ensure!(
        validate_args(
            args,
            &["--animation", "--toggle"],
            &[
                "--display-port",
                "--wake-cycles",
                "--prime",
                "--ack-limit-ms",
                "--loop-limit-ms",
                "--min-animation-fps"
            ]
        )?
        .is_empty(),
        "firmware-live-check [--display-port PORT] [--animation] [--wake-cycles COUNT] [--toggle] [--prime a|b]"
    );
    let cycles = argument(args, "--wake-cycles", 0usize)?;
    let ack_limit = argument(args, "--ack-limit-ms", 250.0f64)?;
    let loop_limit = argument(args, "--loop-limit-ms", 140i64)?;
    let min_fps = argument(args, "--min-animation-fps", 9.0f64)?;
    let path = display_path(args, "--display-port")?;
    let mut display = Display::new(&path, true)?;
    let version = display.query("GET_VERSION", "VERSION:ENCLOSURE=")?;
    let state = display.state()?;
    let diag = display.diag()?;
    let link = display.query("LINK", "LINK:")?;
    ensure!(
        !matches!(value(&diag, "gt911"), "" | "0x00"),
        "GT911 touch controller absent"
    );
    for key in ["reinits", "sendErr"] {
        ensure!(
            value(&diag, key) == "0",
            "display {key}={}",
            value(&diag, key)
        );
    }
    if diag.contains_key("outDrop") {
        ensure!(
            value(&diag, "outDrop") == "0",
            "display outbound queue dropped frames"
        );
    }
    ensure!(
        value(&diag, "link") == "rx",
        "display has received no J9 frame"
    );
    for (key, wanted) in [
        ("SYNC", "1"),
        ("PERSISTED", "1"),
        ("PERSISTERR", "0"),
        ("PENDING", "0"),
    ] {
        ensure!(
            value(&state, key) == wanted,
            "display state {key}={} expected {wanted}",
            value(&state, key)
        );
    }
    let link_fields = fields(&link, "LINK:")?;
    ensure!(
        number(&link_fields, "framesRx", 0)? > 0,
        "unhealthy J9 report: {link}"
    );
    println!(
        "{version}\ndisplay    GT911 {}, heap {}, min {}, idle stage {}\n{link}\nflavor     {}, main board synchronized and durable",
        value(&diag, "gt911"),
        value(&diag, "heap"),
        value(&diag, "minHeap"),
        value(&diag, "stage"),
        value(&state, "FLAVOR")
    );
    let panel = display.panel()?;
    for key in ["drawErr", "frameTimeout", "kickTimeout", "exioErr"] {
        ensure!(
            value(&panel, key) == "0",
            "panel reports {key}={}",
            value(&panel, key)
        );
    }
    println!(
        "panel      {} complete frames, {} completed submissions",
        value(&panel, "frameDone"),
        value(&panel, "flushes")
    );
    let before = fresh(&mut display)?;
    let prime_before = display.prime_diag()?;
    if cycles > 0 {
        let result = (|| -> Result<()> {
            let mut durations = vec![];
            for _ in 0..cycles {
                durations.push(wake(&mut display)?);
                wait(0.05);
            }
            println!(
                "wake        {cycles} cycles, {:.1}–{:.1} ms, no panel/expander errors",
                durations.iter().copied().fold(f64::INFINITY, f64::min),
                durations.iter().copied().fold(0.0, f64::max)
            );
            Ok(())
        })();
        let cleanup = restore(&mut display, &diag);
        finish(result, cleanup)?;
    }
    if flag(args, "--animation") {
        let result = (|| -> Result<()> {
            let wake_ms = wake(&mut display)?;
            display.query("LOCK:SHOW", "OK:LOCK=1")?;
            wait(0.3);
            let first = display.diag()?;
            let started = Instant::now();
            wait(2.0);
            let second = display.diag()?;
            let fps = (number(&second, "flushes", 0)? - number(&first, "flushes", 0)?) as f64
                / started.elapsed().as_secs_f64();
            let high = number(&second, "maxLoopMs", 999999)?;
            ensure!(
                fps >= min_fps,
                "lock-screen animation only advanced at {fps:.2} fps"
            );
            ensure!(
                high <= loop_limit,
                "display loop high-water exceeds its limit"
            );
            println!(
                "animation  {fps:.2} flushes/s, loop high-water {high} ms, wake {wake_ms:.1} ms"
            );
            Ok(())
        })();
        let cleanup = (|| -> Result<()> {
            display.query("LOCK:HIDE", "OK:LOCK=0")?;
            restore(&mut display, &diag)?;
            wait(0.35);
            Ok(())
        })();
        finish(result, cleanup)?;
    }
    if flag(args, "--toggle") {
        toggle(
            &mut display,
            number(&state, "FLAVOR", 0)?,
            ack_limit,
            loop_limit,
        )?;
    }
    if let Some(channel) = option(args, "--prime")? {
        prime(&mut display, &diag, &channel, ack_limit)?;
    }
    let after = fresh(&mut display)?;
    let prime_after = display.prime_diag()?;
    ensure!(
        value(&after, "sendErr") == "0",
        "display send error after check"
    );
    same(&before, &after, &["reinits", "outDrop", "ctrlTurnOver"])?;
    same(&prime_before, &prime_after, &["staleReinits"])?;
    ensure!(
        number(&after, "ctrlTurnMax", 255)? <= 1,
        "main board emitted too many replies in one J9 turn"
    );
    println!("firmware live check: PASS");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn unknown_prime_placeholder_does_not_qualify_as_off() {
        let mut d = fields(
            "DIAG_PRIME:known=0,phase=0,owner=0,desired=0,cancel=0,stop=0,session=0000,hold=0000",
            "DIAG_PRIME:",
        )
        .unwrap();
        assert!(!prime_off(&d));
        d.insert("known".into(), "1".into());
        assert!(prime_off(&d));
        d.insert("hold".into(), "0001".into());
        assert!(!prime_off(&d));
    }
    #[test]
    fn faucet_cache_durability_is_required() {
        let mut state = fields(
            "STATE:FLAVOR=1,BASE=1,SYNC=1,PERSISTED=1,PENDING=0,DURABILITYPENDING=0,CACHEPENDING=1",
            "STATE:",
        )
        .unwrap();
        assert!(!faucet_ready(&state, Some(1)));
        state.insert("CACHEPENDING".into(), "0".into());
        assert!(faucet_ready(&state, Some(1)));
        assert!(!faucet_ready(&state, Some(0)));
    }
}
