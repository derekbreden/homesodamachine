//! Optional native printer commands preserve reviewed toolpaths and verify explicit LAN/application actions.
mod archive;
mod ax;
mod config;
mod ftp;
mod gc;
mod mqtt;
mod picker;
mod purge;
mod send;
mod state;
mod ui;
#[path = "../../print-prep/src/xml.rs"]
#[allow(dead_code)]
mod xml;

use anyhow::{bail, Context, Result};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::{
    env,
    fs::File,
    io::Read,
    path::{Path, PathBuf},
    str::FromStr,
    time::{Duration, SystemTime, UNIX_EPOCH},
};

fn main() {
    if let Err(error) = run() {
        eprintln!("hsm-printer: {error:#}");
        std::process::exit(1)
    }
}
fn run() -> Result<()> {
    let mut args = Args {
        values: env::args().skip(1).collect(),
        errors: Vec::new(),
    };
    if args.flag("--help") || args.flag("-h") {
        println!("hsm-printer [--root CHECKOUT] COMMAND [OPTIONS]\nCommands: status [all|PRINTER], light PRINTER on|off [--node NODE], print ARCHIVE PRINTER, send ARCHIVE PRINTER, archive SOURCE DESTINATION, purge-archive [--output PATH], gc, picker-check\nprint holds Bambu Connect in front; send uses background accessibility with the visible external-spool picker. Both accept --dry-run, --attempts, --accept-timeout and --timelapse. gc preserves the timelapse retention flags. No command runs on the normal build path.");
        return Ok(());
    }
    let requested_root = args.option("--root").map(PathBuf::from);
    let timeout = args.option("--timeout");
    let command = args.positional("command")?;
    if let Some(timeout) = timeout {
        args.values.extend(["--timeout".to_owned(), timeout]);
    }
    match command.as_str() {
        "print" => send::run(&checkout(requested_root.as_deref())?, &mut args, false),
        "send" => send::run(&checkout(requested_root.as_deref())?, &mut args, true),
        "gc" => gc::run(&mut args),
        "purge-archive" => purge::run(&checkout(requested_root.as_deref())?, &mut args),
        "picker-check" => {
            args.finish()?;
            picker::run(&checkout(requested_root.as_deref())?)
        }
        "archive" => {
            let source = expand(&args.positional("source")?);
            let dest = expand(&args.positional("destination")?);
            args.finish()?;
            println!(
                "{}",
                serde_json::to_string_pretty(&archive::package(&source, &dest)?)?
            );
            Ok(())
        }
        "status" | "light" => lan(&command, &mut args),
        _ => bail!("Unknown command; use --help"),
    }
}
fn checkout(requested: Option<&Path>) -> Result<PathBuf> {
    if let Some(requested) = requested {
        let root = requested.canonicalize()?;
        if root.join("tools/hsm/Cargo.toml").is_file() {
            return Ok(root);
        }
        bail!("--root must name the machine checkout")
    }
    if let Some(root) = env::var_os("HSM_WORKSPACE") {
        return checkout(Some(Path::new(&root)));
    }
    let cwd = env::current_dir()?;
    cwd.ancestors()
        .chain(Path::new(env!("CARGO_MANIFEST_DIR")).ancestors())
        .find(|path| path.join("tools/hsm/Cargo.toml").is_file())
        .map(Path::to_owned)
        .context("pass --root CHECKOUT for this asset command")
}
fn lan(command: &str, args: &mut Args) -> Result<()> {
    let timeout = args.number("--timeout", 12_f64)?;
    if !timeout.is_finite() || timeout <= 0. {
        bail!("--timeout must be positive")
    }
    let timeout = Duration::from_secs_f64(timeout);
    let name = if args.values.is_empty() && command == "status" {
        "all".into()
    } else {
        args.positional("printer")?
    };
    let printers = config::configured(&home()?)?;
    if command == "light" {
        let mode = args.positional("mode")?;
        let node = args
            .option("--node")
            .unwrap_or_else(|| "chamber_light".into());
        args.finish()?;
        if !matches!(mode.as_str(), "on" | "off")
            || !matches!(node.as_str(), "chamber_light" | "chamber_light2")
        {
            bail!("Invalid light mode or node")
        }
        let printer = printers
            .get(&name)
            .context("Light requires one configured printer name")?;
        let value = mqtt::Connection::open(printer, timeout)?.light(&node, &mode)?;
        println!("{}", serde_json::to_string_pretty(&value)?);
        return Ok(());
    }
    args.finish()?;
    let selected: Vec<_> = if name == "all" {
        printers.values().collect()
    } else {
        vec![printers.get(&name).context("Unknown configured printer")?]
    };
    let results = std::thread::scope(|scope| -> Result<Vec<Value>> {
        let jobs: Vec<_> = selected
            .iter()
            .map(|printer| scope.spawn(move || summary(printer, timeout)))
            .collect();
        jobs.into_iter()
            .map(|job| {
                job.join()
                    .map_err(|_| anyhow::anyhow!("Printer status worker stopped"))?
            })
            .collect()
    })?;
    println!("{}", serde_json::to_string_pretty(&results)?);
    Ok(())
}
fn summary(printer: &config::Printer, timeout: Duration) -> Result<Value> {
    let status = mqtt::Connection::open(printer, timeout)?.status()?;
    let mut result = json!({"printer":printer.name,"observed_at":now(),"external_spools":{},"nozzle_type":status["nozzle_type"],"nozzles":[]});
    for key in [
        "gcode_state",
        "subtask_name",
        "mc_percent",
        "layer_num",
        "total_layer_num",
        "mc_remaining_time",
        "print_error",
        "hms",
        "nozzle_temper",
        "nozzle_target_temper",
        "bed_temper",
        "bed_target_temper",
        "lights_report",
    ] {
        if let Some(value) = status.get(key) {
            result[key] = value.clone()
        }
    }
    if let Some(trays) = status["vir_slot"].as_array() {
        for tray in trays {
            result["external_spools"][state::text(&tray["id"])] =
                json!({"type":tray["tray_type"],"colour":tray["tray_color"]});
        }
    }
    if let Some(nozzles) = status["device"]["nozzle"]["info"].as_array() {
        result["nozzles"] = json!(nozzles
            .iter()
            .map(|n| json!({"id":n["id"],"type":n["type"],"diameter":n["diameter"],"sn":n["sn"]}))
            .collect::<Vec<_>>());
    }
    Ok(result)
}
pub struct Args {
    values: Vec<String>,
    errors: Vec<String>,
}
impl Args {
    pub fn flag(&mut self, key: &str) -> bool {
        let count = self.values.len();
        self.values.retain(|value| value != key);
        self.values.len() != count
    }
    pub fn option(&mut self, key: &str) -> Option<String> {
        let equals = format!("{key}=");
        let mut selected = None;
        let mut index = 0;
        while index < self.values.len() {
            if let Some(value) = self.values[index].strip_prefix(&equals) {
                selected = Some(value.to_owned());
                self.values.remove(index);
            } else if self.values[index] == key {
                self.values.remove(index);
                if index >= self.values.len() || self.values[index].starts_with("--") {
                    self.errors.push(format!("{key} requires a value"));
                } else {
                    selected = Some(self.values.remove(index));
                }
            } else {
                index += 1;
            }
        }
        selected
    }
    pub fn number<T: FromStr>(&mut self, key: &str, default: T) -> Result<T>
    where
        T::Err: std::error::Error + Send + Sync + 'static,
    {
        self.option(key)
            .map(|value| value.parse().with_context(|| format!("Invalid {key}")))
            .unwrap_or(Ok(default))
    }
    pub fn positional(&mut self, name: &str) -> Result<String> {
        if self.values.is_empty() || self.values[0].starts_with('-') {
            bail!("Missing {name}")
        }
        Ok(self.values.remove(0))
    }
    pub fn finish(&self) -> Result<()> {
        if !self.errors.is_empty() {
            bail!("{}", self.errors.join("; "))
        }
        if !self.values.is_empty() {
            bail!("Unknown arguments; use --help")
        }
        Ok(())
    }
}

#[cfg(test)]
mod argument_tests {
    use super::*;
    fn args(values: &[&str]) -> Args {
        Args {
            values: values.iter().map(|s| s.to_string()).collect(),
            errors: Vec::new(),
        }
    }
    #[test]
    fn credential_options_consume_equals_and_duplicates_before_environment_defaults() {
        let mut values = args(&[
            "--access-code",
            "fixture-first",
            "--access-code=fixture-last",
            "--host=cli.invalid",
        ]);
        let code = values
            .option("--access-code")
            .or_else(|| Some("fixture-environment".into()));
        let host = values
            .option("--host")
            .or_else(|| Some("environment.invalid".into()));
        assert_eq!(code.as_deref(), Some("fixture-last"));
        assert_eq!(host.as_deref(), Some("cli.invalid"));
        values.finish().unwrap();
        let mut values = args(&[
            "--access-code=fixture-first",
            "--access-code",
            "fixture-last",
        ]);
        assert_eq!(
            values.option("--access-code").as_deref(),
            Some("fixture-last")
        );
        values.finish().unwrap();
    }
    #[test]
    fn malformed_or_unknown_credentials_do_not_appear_in_diagnostics() {
        for values in [
            &["--unknown-access-code=fixture-secret"][..],
            &["--access-code", "fixture-secret", "--unknown"][..],
            &["--unknown", "fixture-secret"][..],
        ] {
            let values = args(values);
            assert!(!values
                .finish()
                .unwrap_err()
                .to_string()
                .contains("fixture-secret"));
        }
        let mut values = args(&["--access-code", "--apply"]);
        assert!(values.option("--access-code").is_none());
        assert!(values.flag("--apply"));
        assert!(values.finish().is_err());
    }
}
pub fn home() -> Result<PathBuf> {
    Ok(PathBuf::from(env::var_os("HOME").context("HOME is unset")?))
}
pub fn expand(value: &str) -> PathBuf {
    if value == "~" {
        home().unwrap_or_else(|_| PathBuf::from(value))
    } else if let Some(tail) = value.strip_prefix("~/") {
        home()
            .map(|p| p.join(tail))
            .unwrap_or_else(|_| PathBuf::from(value))
    } else {
        PathBuf::from(value)
    }
}
pub fn hash(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}
pub fn digest(path: &Path) -> Result<String> {
    let mut file = File::open(path)?;
    let mut hash = Sha256::new();
    let mut buffer = vec![0; 1024 * 1024];
    loop {
        let size = file.read(&mut buffer)?;
        if size == 0 {
            break;
        }
        hash.update(&buffer[..size]);
    }
    Ok(format!("{:x}", hash.finalize()))
}
pub fn timestamp(epoch: Option<i64>) -> String {
    let Some(epoch) = epoch else {
        return "????-??-?? ??:??".into();
    };
    let epoch = epoch as libc::time_t;
    let mut time: libc::tm = unsafe { std::mem::zeroed() };
    unsafe { libc::gmtime_r(&epoch, &mut time) };
    format!(
        "{:04}-{:02}-{:02} {:02}:{:02}",
        time.tm_year + 1900,
        time.tm_mon + 1,
        time.tm_mday,
        time.tm_hour,
        time.tm_min
    )
}
pub fn now() -> String {
    let epoch = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs() as libc::time_t;
    let mut time: libc::tm = unsafe { std::mem::zeroed() };
    unsafe { libc::gmtime_r(&epoch, &mut time) };
    format!(
        "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}+00:00",
        time.tm_year + 1900,
        time.tm_mon + 1,
        time.tm_mday,
        time.tm_hour,
        time.tm_min,
        time.tm_sec
    )
}
