//! OTA sends receiver-requested image chunks through the main board and confirms the running version.
use crate::{flag, option, serials, validate_args};
use anyhow::{Context, Result, bail, ensure};
use serialport::{ClearBuffer, SerialPort};
use std::{
    fs,
    io::Write,
    ops::Range,
    path::Path,
    thread,
    time::{Duration, Instant},
};

pub fn crc32(bytes: &[u8]) -> u32 {
    let mut crc = !0u32;
    for byte in bytes {
        crc ^= u32::from(*byte);
        for _ in 0..8 {
            crc = (crc >> 1) ^ (0xedb88320u32 & (0u32.wrapping_sub(crc & 1)));
        }
    }
    !crc
}

pub fn environment(target: &str) -> Result<&'static str> {
    match target {
        "self" => Ok("appliance"),
        "faucet" | "logos-faucet" => Ok("esp32s3_faucet"),
        "enclosure" | "art" | "logos" => Ok("esp32s3_front"),
        _ => bail!("unknown OTA target {target}"),
    }
}

pub fn run(root: &Path, args: &[String]) -> Result<()> {
    let positional = validate_args(args, &["-v", "--verbose"], &["--image"])?;
    ensure!(
        positional.len() == 1,
        "ota TARGET [--image IMAGE] [--verbose]"
    );
    let target = &positional[0];
    let environment = environment(target)?;
    let filename = if target == "art" {
        "art.bin"
    } else if target.starts_with("logos") {
        "logos.bin"
    } else {
        "firmware.bin"
    };
    let path = option(args, "--image")?
        .map(std::path::PathBuf::from)
        .unwrap_or_else(|| root.join(".pio/build").join(environment).join(filename));
    ensure!(
        path.is_file(),
        "no image at {}; build the {environment} firmware or its display assets first",
        path.display()
    );
    let image = fs::read(&path)?;
    ensure!(!image.is_empty(), "image is empty");
    let crc = crc32(&image);
    println!(
        "{}  {} bytes  crc32 {crc:#010x}\ntarget: {target}",
        path.display(),
        image.len()
    );
    let path = serials::main_board_port()?;
    let mut port = open_console(&path)?;
    println!("main board on {path}");
    serials::send(
        &mut *port,
        format!("ota {target} {} {crc}\n", image.len()).as_bytes(),
    )?;
    let mut pending = Vec::new();
    let started = Instant::now();
    let mut idle = started;
    let mut reported = started
        .checked_sub(Duration::from_secs(1))
        .unwrap_or(started);
    let verbose = flag(args, "-v") || flag(args, "--verbose");
    loop {
        let chunk = serials::poll(&mut *port)?;
        if !chunk.is_empty() {
            pending.extend(chunk);
            idle = Instant::now();
        }
        ensure!(
            idle.elapsed() <= Duration::from_secs(30),
            "timed out waiting for the main board"
        );
        while let Some(index) = pending.iter().position(|v| *v == b'\n') {
            let bytes = pending.drain(..=index).collect::<Vec<_>>();
            let line = String::from_utf8_lossy(&bytes).trim().to_owned();
            if line.is_empty() {
                continue;
            }
            match parse_response(&line, image.len())? {
                Response::Baud(rate) => {
                    thread::sleep(Duration::from_millis(50));
                    port.set_baud_rate(rate)?;
                    thread::sleep(Duration::from_millis(50));
                    port.clear(ClearBuffer::Input)?;
                    pending.clear();
                    println!("console at {rate} baud");
                }
                Response::Need(range) => {
                    serials::send(&mut *port, &image[range.clone()])?;
                    if reported.elapsed() > Duration::from_millis(500) {
                        reported = Instant::now();
                        print!(
                            "\r  {:5.1}%  {}/{}  {:.1} KB/s",
                            100.0 * range.end as f64 / image.len() as f64,
                            range.end,
                            image.len(),
                            range.end as f64 / started.elapsed().as_secs_f64().max(0.001) / 1024.0
                        );
                        std::io::stdout().flush()?;
                    }
                }
                Response::Done => {
                    println!(
                        "\r  {} bytes verified in {:.0}s; the board restarts itself",
                        image.len(),
                        started.elapsed().as_secs_f64()
                    );
                    drop(port);
                    return confirm_version(root, &path, target);
                }
                Response::Failed => bail!("{line}"),
                Response::Other => {
                    if verbose || line.starts_with("OTA:STALL") {
                        println!("  [{line}]");
                    }
                }
            }
        }
    }
}

pub fn open_console(path: &str) -> Result<Box<dyn SerialPort>> {
    let mut port = serials::open(path, false, Duration::from_millis(5))?;
    let started = Instant::now();
    let mut quiet = started;
    while quiet.elapsed() < Duration::from_millis(400)
        && started.elapsed() < Duration::from_secs(12)
    {
        if !serials::poll(&mut *port)?.is_empty() {
            quiet = Instant::now();
        }
    }
    port.clear(ClearBuffer::Input)?;
    serials::send(&mut *port, b"ota\n")?;
    let deadline = Instant::now() + Duration::from_secs(10);
    let mut seen = Vec::new();
    loop {
        seen.extend(serials::poll(&mut *port)?);
        let text = String::from_utf8_lossy(&seen);
        ensure!(
            !text.contains("SINGLE SLOT"),
            "main board still has a single-slot partition table"
        );
        if text.trim_end().ends_with('>') {
            break;
        }
        ensure!(
            Instant::now() < deadline,
            "main board never answered; check its supply at J10"
        );
        thread::sleep(Duration::from_millis(20));
    }
    port.clear(ClearBuffer::Input)?;
    Ok(port)
}

#[derive(Debug, PartialEq)]
enum Response {
    Baud(u32),
    Need(Range<usize>),
    Done,
    Failed,
    Other,
}

fn parse_response(line: &str, size: usize) -> Result<Response> {
    let words = line.split_whitespace().collect::<Vec<_>>();
    match words.first().copied() {
        Some("OTA:BAUD") => {
            ensure!(words.len() == 2, "malformed OTA baud response");
            Ok(Response::Baud(words[1].parse()?))
        }
        Some("OTA:NEED") => {
            ensure!(words.len() == 3, "malformed OTA chunk request");
            let start = words[1].parse::<usize>()?;
            let length = words[2].parse::<usize>()?;
            let end = start
                .checked_add(length)
                .context("OTA chunk range overflows")?;
            ensure!(
                length != 0 && end <= size,
                "receiver requested bytes outside the image"
            );
            Ok(Response::Need(start..end))
        }
        Some("OTA:DONE") => Ok(Response::Done),
        Some("OTA:FAIL" | "OTA:ABORT") => Ok(Response::Failed),
        _ => Ok(Response::Other),
    }
}

fn expected_version(root: &Path, target: &str) -> Option<String> {
    let tree = match target {
        "self" => "src_appliance",
        "faucet" => "src_faucet",
        "enclosure" => "src_front",
        _ => return None,
    };
    fs::read_to_string(root.join("firmware").join(tree).join("fw_version.h"))
        .ok()?
        .lines()
        .find(|line| line.contains("FW_VERSION") && line.contains('"'))?
        .split('"')
        .nth(1)
        .map(str::to_owned)
}

fn version_report(line: &str, target: &str) -> Option<String> {
    let label = match target {
        "self" => "main board",
        "faucet" => "faucet",
        "enclosure" => "enclosure",
        _ => return None,
    };
    let line = line.trim();
    let line = line.strip_prefix("VERSION").map(str::trim).unwrap_or(line);
    let tail = line.strip_prefix(label)?;
    if !tail.starts_with(char::is_whitespace) && !tail.starts_with('=') {
        return None;
    }
    let mut value = tail
        .trim()
        .strip_prefix('=')
        .map(str::trim)
        .unwrap_or_else(|| tail.trim());
    if let Some(index) = value.find(" art crc ") {
        value = &value[..index];
    }
    if let Some(index) = value.find(" committed ") {
        value = &value[..index];
    }
    let value = value.trim();
    (!value.is_empty() && value != "(unanswered)").then(|| value.to_owned())
}

fn confirm_version(root: &Path, path: &str, target: &str) -> Result<()> {
    let Some(wanted) = expected_version(root, target) else {
        return Ok(());
    };
    thread::sleep(Duration::from_secs(8));
    let mut port = open_console(path)?;
    let deadline = Instant::now() + Duration::from_secs(75);
    let mut asked = None::<Instant>;
    let mut pending = Vec::new();
    let mut seen = None;
    while Instant::now() < deadline {
        if asked.is_none_or(|at| at.elapsed() >= Duration::from_secs(5)) {
            serials::send(&mut *port, b"versions\n")?;
            asked = Some(Instant::now());
        }
        pending.extend(serials::poll(&mut *port)?);
        while let Some(index) = pending.iter().position(|v| *v == b'\n') {
            let bytes = pending.drain(..=index).collect::<Vec<_>>();
            if let Some(version) = version_report(&String::from_utf8_lossy(&bytes), target) {
                if version == wanted {
                    println!("confirmed: {target} is running {version}");
                    return Ok(());
                }
                seen = Some(version);
            }
        }
        thread::sleep(Duration::from_millis(100));
    }
    bail!("could not confirm {target} running {wanted:?}; last report: {seen:?}")
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn receiver_controls_transfer_ranges() {
        assert_eq!(
            parse_response("OTA:NEED 1024 40", 1064).unwrap(),
            Response::Need(1024..1064)
        );
        assert!(parse_response("OTA:NEED 1024 41", 1064).is_err());
        assert!(parse_response("OTA:NEED 0 0", 1064).is_err());
        assert_eq!(
            parse_response("OTA:BAUD 500000", 10).unwrap(),
            Response::Baud(500000)
        );
        assert_eq!(crc32(b"123456789"), 0xcbf43926);
    }
    #[test]
    fn firmware_identity_excludes_report_columns() {
        assert_eq!(
            version_report(
                "VERSION main board = 2026.11.09 abcdef+ committed 123",
                "self"
            )
            .as_deref(),
            Some("2026.11.09 abcdef+")
        );
        assert_eq!(
            version_report(
                "faucet 2026.11.09 abcdef art crc 00AA committed 123",
                "faucet"
            )
            .as_deref(),
            Some("2026.11.09 abcdef")
        );
        assert_eq!(version_report("enclosure (unanswered)", "enclosure"), None);
        assert_eq!(version_report("faucet-cache abc", "faucet"), None);
    }
}
