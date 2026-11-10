//! X1 interface records retain raw receive bytes and the operator's explicit console request.
use crate::{flag, option, serials, text_output, validate_args, write_json};
use anyhow::{Context, Result, bail, ensure};
use serde_json::{Value, json};
use serialport::{DataBits, FlowControl, Parity, StopBits};
use std::{
    fs::{self, OpenOptions},
    io::Write,
    path::PathBuf,
    process::Command,
    sync::atomic::{AtomicBool, Ordering},
    thread,
    time::{Duration, Instant},
};

static INTERRUPTED: AtomicBool = AtomicBool::new(false);
extern "C" fn interrupt(_: libc::c_int) {
    INTERRUPTED.store(true, Ordering::Relaxed);
}
struct Interrupt(libc::sighandler_t);
impl Interrupt {
    fn install() -> Self {
        INTERRUPTED.store(false, Ordering::Relaxed);
        Self(unsafe { libc::signal(libc::SIGINT, interrupt as *const () as libc::sighandler_t) })
    }
}
impl Drop for Interrupt {
    fn drop(&mut self) {
        unsafe {
            libc::signal(libc::SIGINT, self.0);
        }
    }
}

fn utc() -> Result<String> {
    text_output(Command::new("date").args(["-u", "+%Y-%m-%dT%H:%M:%SZ"]))
}
fn new_directory(path: &PathBuf) -> Result<()> {
    if let Some(parent) = path.parent().filter(|p| !p.as_os_str().is_empty()) {
        fs::create_dir_all(parent)?;
    }
    fs::create_dir(path)
        .with_context(|| format!("capture destination must be new: {}", path.display()))
}
fn required(args: &[String], key: &str) -> Result<String> {
    option(args, key)?.with_context(|| format!("{key} is required"))
}

pub fn capture(args: &[String]) -> Result<()> {
    ensure!(
        validate_args(
            args,
            &["--list", "--rx-only-wiring-confirmed"],
            &[
                "--port",
                "--baud",
                "--parity",
                "--data-bits",
                "--stop-bits",
                "--seconds",
                "--output",
                "--label"
            ]
        )?
        .is_empty(),
        "x1-capture --port PORT --baud BAUD --output NEW_DIRECTORY --rx-only-wiring-confirmed"
    );
    if flag(args, "--list") {
        return serials::list();
    }
    ensure!(
        flag(args, "--rx-only-wiring-confirmed"),
        "verify physical receive-only wiring and pass --rx-only-wiring-confirmed"
    );
    let path = required(args, "--port")?;
    let baud = required(args, "--baud")?.parse::<u32>()?;
    ensure!(baud > 0, "baud must be positive");
    let bits = option(args, "--data-bits")?
        .unwrap_or_else(|| "8".into())
        .parse::<u8>()?;
    let data_bits = match bits {
        7 => DataBits::Seven,
        8 => DataBits::Eight,
        _ => bail!("data bits must be seven or eight"),
    };
    let parity_name = option(args, "--parity")?.unwrap_or_else(|| "N".into());
    let parity = match parity_name.as_str() {
        "N" => Parity::None,
        "E" => Parity::Even,
        "O" => Parity::Odd,
        _ => bail!("parity must be N, E or O"),
    };
    let stops = option(args, "--stop-bits")?
        .unwrap_or_else(|| "1".into())
        .parse::<u8>()?;
    let stop_bits = match stops {
        1 => StopBits::One,
        2 => StopBits::Two,
        _ => bail!("stop bits must be one or two"),
    };
    let seconds = option(args, "--seconds")?
        .unwrap_or_else(|| "30".into())
        .parse::<f64>()?;
    ensure!(
        seconds.is_finite() && seconds > 0.0 && seconds <= 3600.0,
        "seconds must be finite and within the capture limit"
    );
    let destination = PathBuf::from(required(args, "--output")?);
    new_directory(&destination)?;
    let metadata_path = destination.join("capture.json");
    let mut metadata = json!({"started_utc":utc()?,"port":path,"baud":baud,"data_bits":bits,"parity":parity_name,"stop_bits":stops,"requested_seconds":seconds,"label":option(args,"--label")?.unwrap_or_default(),"rx_only_wiring_confirmed":true,"serial_transmit_operations":0,"timing_scope":"host read batches, not individual UART edges"});
    write_json(&metadata_path, &metadata)?;
    let _interrupt = Interrupt::install();
    let mut started = Instant::now();
    let mut offset = 0usize;
    let mut batches = 0usize;
    let result = (|| -> Result<()> {
        let mut raw = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(destination.join("raw.bin"))?;
        let mut events = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(destination.join("events.jsonl"))?;
        let mut receiver = serialport::new(&path, baud)
            .data_bits(data_bits)
            .parity(parity)
            .stop_bits(stop_bits)
            .flow_control(FlowControl::None)
            .timeout(Duration::from_millis(50))
            .dtr_on_open(false)
            .exclusive(true)
            .open()?;
        receiver.write_request_to_send(false)?;
        started = Instant::now();
        println!(
            "Listening on {path} at {baud} {bits}{parity_name}{stops}\nCapture directory: {}\nNo commands are sent. Ctrl-C preserves the captured data.",
            destination.canonicalize()?.display()
        );
        let capture_started = started;
        let mut next_progress = capture_started + Duration::from_secs(5);
        while capture_started.elapsed().as_secs_f64() < seconds
            && !INTERRUPTED.load(Ordering::Relaxed)
        {
            let chunk = serials::poll(&mut *receiver)?;
            if !chunk.is_empty() {
                raw.write_all(&chunk)?;
                raw.flush()?;
                let hex = chunk.iter().map(|v| format!("{v:02x}")).collect::<String>();
                writeln!(
                    events,
                    "{}",
                    json!({"elapsed_s":capture_started.elapsed().as_secs_f64(),"utc":utc()?,"offset":offset,"length":chunk.len(),"hex":hex})
                )?;
                events.flush()?;
                offset += chunk.len();
                batches += 1;
            }
            if Instant::now() >= next_progress {
                println!("Received {offset} bytes in {batches} host read batches");
                next_progress = Instant::now() + Duration::from_secs(5);
            }
        }
        Ok(())
    })();
    let outcome = if result.is_err() {
        "error"
    } else if INTERRUPTED.load(Ordering::Relaxed) {
        "interrupted"
    } else {
        "complete"
    };
    metadata["ended_utc"] = Value::String(utc()?);
    metadata["elapsed_s"] = json!(started.elapsed().as_secs_f64());
    metadata["bytes_received"] = json!(offset);
    metadata["read_batches"] = json!(batches);
    metadata["outcome"] = json!(outcome);
    if let Err(error) = &result {
        metadata["error"] = json!(error.to_string());
    }
    write_json(&metadata_path, &metadata)?;
    println!("{outcome}: {offset} bytes received; no serial transmit operations");
    if offset == 0 {
        println!(
            "Silence does not establish the baud rate, protocol, or absence of computer control."
        );
    }
    result?;
    if INTERRUPTED.load(Ordering::Relaxed) {
        std::process::exit(130);
    }
    Ok(())
}

pub fn console(args: &[String]) -> Result<()> {
    ensure!(
        validate_args(
            args,
            &["--list"],
            &[
                "--port",
                "--baud",
                "--cmd",
                "--eol",
                "--seconds",
                "--output",
                "--label"
            ]
        )?
        .is_empty(),
        "x1-console --port PORT --cmd COMMAND --output NEW_DIRECTORY"
    );
    if flag(args, "--list") {
        return serials::list();
    }
    let path = required(args, "--port")?;
    let command = required(args, "--cmd")?;
    let baud = option(args, "--baud")?
        .unwrap_or_else(|| "115200".into())
        .parse::<u32>()?;
    let eol_name = option(args, "--eol")?.unwrap_or_else(|| "cr".into());
    let eol = match eol_name.as_str() {
        "cr" => "\r",
        "lf" => "\n",
        "crlf" => "\r\n",
        _ => bail!("eol must be cr, lf or crlf"),
    };
    let seconds = option(args, "--seconds")?
        .unwrap_or_else(|| "4".into())
        .parse::<f64>()?;
    ensure!(
        seconds.is_finite() && seconds > 0.0,
        "listen duration must be positive and finite"
    );
    let destination = PathBuf::from(required(args, "--output")?);
    new_directory(&destination)?;
    let mut console = serialport::new(&path, baud)
        .timeout(Duration::from_millis(50))
        .dtr_on_open(true)
        .open()?;
    console.write_request_to_send(true)?;
    thread::sleep(Duration::from_millis(250));
    console.clear(serialport::ClearBuffer::Input)?;
    let sent = command
        .chars()
        .chain(eol.chars())
        .map(|c| u8::try_from(u32::from(c)).context("command is outside Latin-1"))
        .collect::<Result<Vec<_>>>()?;
    serials::send(&mut *console, &sent)?;
    let started = Instant::now();
    let mut buffer = Vec::new();
    while started.elapsed().as_secs_f64() < seconds {
        buffer.extend(serials::poll(&mut *console)?);
    }
    fs::write(destination.join("raw.bin"), &buffer)?;
    write_json(
        &destination.join("console.json"),
        &json!({"utc":utc()?,"port":path,"baud":baud,"command":command,"eol":eol_name,"listen_seconds":seconds,"label":option(args,"--label")?.unwrap_or_default(),"bytes_received":buffer.len()}),
    )?;
    println!(
        "{}\n---\n[{} bytes captured]",
        buffer.iter().map(|v| char::from(*v)).collect::<String>(),
        buffer.len()
    );
    Ok(())
}
