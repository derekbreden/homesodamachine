//! Console tools enumerate boards and carry explicit commands over their existing serial links.
use crate::{option, validate_args};
use anyhow::{Context, Result, bail, ensure};
use serialport::{ClearBuffer, SerialPort, SerialPortInfo, SerialPortType};
use std::{
    collections::BTreeSet,
    io::ErrorKind,
    thread,
    time::{Duration, Instant},
};

pub const CH340: (u16, u16) = (0x1a86, 0x7523);
pub const ESP32_S3: (u16, u16) = (0x303a, 0x1001);

pub fn ports() -> Result<Vec<SerialPortInfo>> {
    let mut ports = serialport::available_ports()?;
    // macOS lists every device twice, as its call-out node and its dial-in node. They are one
    // board, and the call-out node is the one that opens without waiting for carrier.
    ports.retain(|port| !port.port_name.starts_with("/dev/tty."));
    ports.sort_by(|a, b| a.port_name.cmp(&b.port_name));
    Ok(ports)
}

pub fn matches(port: &SerialPortInfo, id: (u16, u16)) -> bool {
    matches!(&port.port_type, SerialPortType::UsbPort(usb) if (usb.vid, usb.pid) == id)
}

pub fn ports_with_id(id: (u16, u16)) -> Result<Vec<SerialPortInfo>> {
    Ok(ports()?.into_iter().filter(|p| matches(p, id)).collect())
}

pub fn main_board_port() -> Result<String> {
    let ports = ports_with_id(CH340)?;
    ensure!(
        !ports.is_empty(),
        "no main board on USB (looking for the CH340C at J14)"
    );
    ensure!(
        ports.len() == 1,
        "more than one CH340 present: {}",
        ports
            .iter()
            .map(|p| p.port_name.as_str())
            .collect::<Vec<_>>()
            .join(", ")
    );
    Ok(ports[0].port_name.clone())
}

/// True when another program has the port. Every tool here opens a port to itself, so a second
/// opener is refused instead of being fed half of the first one's bytes.
pub fn busy(error: &serialport::Error) -> bool {
    error.description.to_lowercase().contains("busy")
}

fn open_once(path: &str, dtr: bool, timeout: Duration) -> serialport::Result<Box<dyn SerialPort>> {
    let mut port = serialport::new(path, 115200)
        .timeout(timeout)
        .dtr_on_open(dtr)
        .open()?;
    port.write_request_to_send(false)?;
    Ok(port)
}

pub fn open(path: &str, dtr: bool, timeout: Duration) -> Result<Box<dyn SerialPort>> {
    // The bench watcher (bench.rs) has a main board's port for a fraction of a second every few
    // seconds. An open that lands on that waits it out; one that lands on a tool at work fails.
    let started = Instant::now();
    loop {
        match open_once(path, dtr, timeout) {
            Ok(port) => return Ok(port),
            Err(error) if busy(&error) && started.elapsed() < Duration::from_secs(3) => {
                thread::sleep(Duration::from_millis(50));
            }
            Err(error) => return Err(error.into()),
        }
    }
}

/// A port opened without restarting the board and with neither of its strapping lines held.
/// DTR is left as the open made it until RTS is let go, because the other order is the reset
/// pulse; it is then let go too, so a board that restarts for its own reasons while the port is
/// open boots its firmware and not its loader. A port another program has is refused at once.
pub fn open_quiet(path: &str, timeout: Duration) -> serialport::Result<Box<dyn SerialPort>> {
    let mut port = open_once(path, true, timeout)?;
    port.write_data_terminal_ready(false)?;
    Ok(port)
}

pub fn poll(port: &mut dyn SerialPort) -> Result<Vec<u8>> {
    let mut bytes = vec![0; (port.bytes_to_read()? as usize).clamp(1, 65536)];
    let length = match port.read(&mut bytes) {
        Ok(n) => n,
        Err(error)
            if matches!(
                error.kind(),
                ErrorKind::TimedOut | ErrorKind::WouldBlock | ErrorKind::Interrupted
            ) =>
        {
            0
        }
        Err(error) => return Err(error.into()),
    };
    bytes.truncate(length);
    Ok(bytes)
}

pub fn send(port: &mut dyn SerialPort, bytes: &[u8]) -> Result<()> {
    port.write_all(bytes)?;
    port.flush()?;
    Ok(())
}

pub fn list() -> Result<()> {
    for port in ports()? {
        let (description, id) = match &port.port_type {
            SerialPortType::UsbPort(usb) => (
                usb.product.as_deref().unwrap_or("USB serial"),
                format!("{:04x}:{:04x}", usb.vid, usb.pid),
            ),
            _ => ("serial port", "no USB ID".to_owned()),
        };
        println!("{}\t{description}\t{id}", port.port_name);
    }
    Ok(())
}

fn known_s3(serial: &str) -> Option<(&'static str, &'static str)> {
    match serial.to_uppercase().as_str() {
        "44:1B:F6:86:15:98" | "28:84:85:54:FF:94" => Some(("esp32s3_faucet", "faucet display")),
        "E8:F6:0A:8E:8B:C8" | "14:C1:9F:4A:F6:40" => Some(("esp32s3_front", "enclosure display")),
        _ => None,
    }
}

pub fn boards(args: &[String]) -> Result<()> {
    ensure!(
        validate_args(args, &[], &["--learn"])?.is_empty(),
        "boards [--learn ENV]"
    );
    let ports = ports()?;
    let main = ports
        .iter()
        .filter(|p| matches(p, CH340))
        .collect::<Vec<_>>();
    let panels = ports
        .iter()
        .filter(|p| matches(p, ESP32_S3))
        .collect::<Vec<_>>();
    if let Some(environment) = option(args, "--learn")? {
        ensure!(
            panels.len() == 1,
            "need exactly one S3 on USB to learn it; found {}",
            panels.len()
        );
        let SerialPortType::UsbPort(usb) = &panels[0].port_type else {
            unreachable!()
        };
        let serial = usb
            .serial_number
            .as_ref()
            .filter(|v| !v.is_empty())
            .context("S3 reports no serial number")?;
        println!(
            "Add to known_s3 in tools/hsm/peripheral/src/serials.rs:\n  {:?} => Some(({environment:?}, \"display\")),",
            serial.to_uppercase()
        );
        return Ok(());
    }
    if main.is_empty() {
        println!("main board        NOT FOUND");
    }
    for port in &main {
        println!("main board        {} (CH340C at J14)", port.port_name);
    }
    if panels.is_empty() {
        println!("ESP32-S3 board    NOT FOUND");
    }
    for port in &panels {
        let SerialPortType::UsbPort(usb) = &port.port_type else {
            unreachable!()
        };
        let serial = usb.serial_number.as_deref().unwrap_or("");
        let label = known_s3(serial).map_or("ESP32-S3 board (unknown)", |(_, label)| label);
        println!("{label:24} {} (native USB, {serial})", port.port_name);
    }
    if !main.is_empty() && panels.is_empty() {
        println!(
            "\nAsk the externally powered enclosure display to reattach its USB PHY:\n  hsm-peripheral display-usb\nThe development command leaves its supply rail and loads powered. If UNREACHABLE, the display needs a physical reset or supply power cycle."
        );
    }
    if main.is_empty() && panels.is_empty() {
        println!(
            "The main board needs its supply at J10 before the CH340C enumerates; USB VBUS powers nothing on it."
        );
    }
    if let Some(port) = main.first() {
        for environment in ["appliance", "pcba_bench"] {
            println!(
                "PLATFORMIO_UPLOAD_PORT={} pio run -e {environment} -t upload",
                port.port_name
            );
        }
    }
    if let Some(port) = panels.first() {
        let SerialPortType::UsbPort(usb) = &port.port_type else {
            unreachable!()
        };
        let environments = match known_s3(usb.serial_number.as_deref().unwrap_or("")) {
            Some((environment, _)) => vec![environment],
            None => vec!["esp32s3_front", "esp32s3_faucet"],
        };
        for environment in environments {
            println!(
                "PLATFORMIO_UPLOAD_PORT={} pio run -e {environment} -t upload",
                port.port_name
            );
        }
        println!("A board held in ROM download mode stays there until a plain RESET.");
    }
    if !main.is_empty() && !panels.is_empty() {
        println!("Always name the upload port with both boards connected.");
    }
    Ok(())
}

pub fn panelcam(args: &[String], wake: bool) -> Result<()> {
    if wake {
        ensure!(args.len() <= 1, "panelcam-wake [PORT]");
        let path = args.first().map_or("/dev/cu.usbserial-10", String::as_str);
        if let Ok(lines) = ask(path, "wake") {
            println!(
                "{}",
                if lines.iter().any(|v| v.contains("idle")) {
                    "awake"
                } else {
                    "no answer from the console"
                }
            );
        }
        return Ok(());
    }
    ensure!(args.len() >= 2, "panelcam-console PORT COMMAND...");
    let lines = ask(&args[0], &args[1..].join(" "))?;
    println!(
        "{}",
        if lines.is_empty() {
            "no answer from the console".to_owned()
        } else {
            lines.join("\n")
        }
    );
    Ok(())
}

pub fn ask(path: &str, line: &str) -> Result<Vec<String>> {
    let mut port = open(path, true, Duration::from_millis(50))?;
    let started = Instant::now();
    let mut quiet = started;
    let mut seen = Vec::new();
    while started.elapsed() < Duration::from_secs(6) {
        let chunk = poll(&mut *port)?;
        if !chunk.is_empty() {
            seen.extend(chunk);
            quiet = Instant::now();
            if String::from_utf8_lossy(&seen).contains("type 'help'") {
                break;
            }
        } else if quiet.elapsed() > Duration::from_secs(2) {
            break;
        }
    }
    port.clear(ClearBuffer::Input)?;
    send(&mut *port, format!("\n{line}\n").as_bytes())?;
    let deadline = Instant::now() + Duration::from_secs(6);
    let mut reply = Vec::new();
    while Instant::now() < deadline {
        reply.extend(poll(&mut *port)?);
        if String::from_utf8_lossy(&reply).trim_end().ends_with('>') {
            break;
        }
    }
    Ok(String::from_utf8_lossy(&reply)
        .lines()
        .map(str::trim)
        .filter(|v| !v.is_empty() && *v != ">" && *v != line)
        .map(str::to_owned)
        .collect())
}

pub fn display_usb(args: &[String]) -> Result<()> {
    ensure!(
        validate_args(args, &[], &["--main-board-port"])?.is_empty(),
        "display-usb [--main-board-port PORT]"
    );
    let path = option(args, "--main-board-port")?.map_or_else(main_board_port, Ok)?;
    let old = ports_with_id(ESP32_S3)?
        .into_iter()
        .map(|p| p.port_name)
        .collect::<BTreeSet<_>>();
    println!("main board  {path}");
    let mut port = open(&path, false, Duration::from_millis(50))?;
    port.clear(ClearBuffer::Input)?;
    let mut seen = Vec::new();
    let mut accepted = false;
    for _ in 0..3 {
        send(&mut *port, b"\ndisplay usb\n")?;
        let deadline = Instant::now() + Duration::from_secs(4);
        while Instant::now() < deadline {
            seen.extend(poll(&mut *port)?);
            let text = String::from_utf8_lossy(&seen);
            if text.contains("DISPLAY_USB:UNREACHABLE") {
                bail!("{text}");
            }
            if text.contains("DISPLAY_USB:APP") {
                accepted = true;
                break;
            }
            thread::sleep(Duration::from_millis(20));
        }
        if accepted {
            break;
        }
    }
    drop(port);
    for line in String::from_utf8_lossy(&seen)
        .lines()
        .filter(|v| v.contains("DISPLAY_USB:"))
    {
        println!("{}", line.trim());
    }
    ensure!(
        accepted,
        "main board did not recognize or finish 'display usb'; build and flash the appliance environment"
    );
    if !old.is_empty() {
        let deadline = Instant::now() + Duration::from_secs(4);
        loop {
            if ports_with_id(ESP32_S3)?
                .iter()
                .all(|p| !old.contains(&p.port_name))
            {
                break;
            }
            ensure!(
                Instant::now() < deadline,
                "display accepted the command, but its previous USB attachment never detached"
            );
            thread::sleep(Duration::from_millis(50));
        }
    }
    let deadline = Instant::now() + Duration::from_secs(12);
    while ports_with_id(ESP32_S3)?.is_empty() {
        ensure!(
            Instant::now() < deadline,
            "display command succeeded, but no S3 USB device enumerated"
        );
        thread::sleep(Duration::from_millis(250));
    }
    let deadline = Instant::now() + Duration::from_secs(18);
    while Instant::now() < deadline {
        for device in ports_with_id(ESP32_S3)? {
            let Ok(mut display) = open(&device.port_name, true, Duration::from_millis(100)) else {
                continue;
            };
            display.clear(ClearBuffer::Input)?;
            let mut reply = Vec::new();
            for _ in 0..3 {
                send(&mut *display, b"GET_VERSION\n")?;
                let wait = Instant::now() + Duration::from_millis(800);
                while Instant::now() < wait {
                    reply.extend(poll(&mut *display)?);
                    if let Some(version) = String::from_utf8_lossy(&reply)
                        .lines()
                        .find(|line| line.starts_with("VERSION:ENCLOSURE="))
                    {
                        println!("display     {}\n{version}", device.port_name);
                        return Ok(());
                    }
                    thread::sleep(Duration::from_millis(20));
                }
            }
        }
        thread::sleep(Duration::from_millis(500));
    }
    bail!("USB enumerated, but the enclosure display did not answer GET_VERSION")
}
