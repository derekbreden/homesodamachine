//! Inspect chamber-camera settings and verify automatic print-process recording changes.
use crate::{config, home, mqtt::Connection, Args};
use anyhow::{bail, Context, Result};
use serde_json::{json, Value};
use std::time::Duration;

pub fn summary(printer: &config::Printer, status: &Value) -> Value {
    let mut camera = json!({});
    for key in [
        "ipcam_dev",
        "ipcam_record",
        "timelapse",
        "resolution",
        "resolution_supported",
        "mode_bits",
    ] {
        if let Some(value) = status["ipcam"].get(key) {
            camera[key] = value.clone();
        }
    }
    json!({"printer":printer.name,"camera":camera,"storage_present":status["sdcard"],"observed_at":crate::now()})
}

pub fn run(args: &mut Args) -> Result<()> {
    let timeout = args.number("--timeout", 12_f64)?;
    if !timeout.is_finite() || timeout <= 0. {
        bail!("--timeout must be positive")
    }
    let name = if args.values.is_empty() {
        "all".to_owned()
    } else {
        args.positional("printer")?
    };
    let mode = if args.values.is_empty() {
        None
    } else {
        Some(args.positional("mode")?)
    };
    args.finish()?;
    if mode.as_deref().is_some_and(|m| !matches!(m, "on" | "off")) {
        bail!("Camera recording mode must be on or off")
    }
    let printers = config::configured(&home()?)?;
    let selected: Vec<_> = if name == "all" {
        printers.values().collect()
    } else {
        vec![printers.get(&name).context("Unknown configured printer")?]
    };
    let mut results = Vec::new();
    for printer in selected {
        let mut connection = Connection::open(printer, Duration::from_secs_f64(timeout))?;
        let status = if let Some(mode) = &mode {
            connection.recording(mode == "on")?
        } else {
            connection.status()?
        };
        results.push(summary(printer, &status));
    }
    println!("{}", serde_json::to_string_pretty(&results)?);
    Ok(())
}
