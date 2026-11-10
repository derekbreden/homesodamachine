//! Optional host commands prepare display assets, firmware releases and native app reviews.
mod firmware;
mod ios;
mod live;
mod ota;
mod panel;
mod positioner;
mod serials;
mod x1;

use anyhow::{Context, Result, bail, ensure};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::{
    env, fs,
    path::{Path, PathBuf},
    process::{Command, Output},
    time::{SystemTime, UNIX_EPOCH},
};

fn main() {
    if let Err(error) = run() {
        eprintln!("{error:#}");
        std::process::exit(1);
    }
}

fn run() -> Result<()> {
    let mut args = env::args().skip(1).collect::<Vec<_>>();
    let root = if args.first().is_some_and(|v| v == "--root") {
        ensure!(args.len() >= 3, "--root requires a checkout and a command");
        let root = PathBuf::from(args.remove(1)).canonicalize()?;
        args.remove(0);
        root
    } else {
        root()?
    };
    ensure!(!args.is_empty(), usage());
    let command = args.remove(0);
    if args
        .iter()
        .any(|arg| matches!(arg.as_str(), "--help" | "-h"))
    {
        println!("{}", usage());
        return Ok(());
    }
    match command.as_str() {
        "ios-checks" => ios::checks(&root, &args),
        "ios-capture" => ios::capture(&root, &args),
        "positioner-geometry" => positioner::geometry(&root, &args),
        "positioner-verify" => positioner::verify(&root, &args),
        "uf2" => positioner::uf2(&args),
        "pico-pad-checksum" => positioner::pico_pad_checksum(&args),
        "firmware-pre-build" => firmware::pre_build(&root, &args),
        "boards" => serials::boards(&args),
        "display-usb" => serials::display_usb(&args),
        "panelcam-console" => serials::panelcam(&args, false),
        "panelcam-wake" => serials::panelcam(&args, true),
        "ota" => ota::run(&root, &args),
        "x1-console" => x1::console(&args),
        "x1-capture" => x1::capture(&args),
        "firmware-live-check" => live::enclosure(&args),
        "firmware-faucet-check" => live::faucet(&args),
        "panelcam-rectify" => panel::run(&root, &args),
        "help" | "--help" | "-h" => {
            println!("{}", usage());
            Ok(())
        }
        _ => bail!("unknown command {command:?}\n{}", usage()),
    }
}

fn usage() -> &'static str {
    "hsm-peripheral [--root CHECKOUT] COMMAND [OPTIONS]\nCommands: ios-checks, ios-capture, positioner-geometry, positioner-verify, uf2, pico-pad-checksum, firmware-pre-build, boards, display-usb, panelcam-console, panelcam-wake, ota, x1-console, x1-capture, firmware-live-check, firmware-faucet-check, panelcam-rectify"
}

fn root() -> Result<PathBuf> {
    if let Some(root) = env::var_os("HSM_WORKSPACE") {
        return Ok(PathBuf::from(root).canonicalize()?);
    }
    let cwd = env::current_dir()?;
    for parent in cwd.ancestors() {
        if parent.join("tools/hsm/Cargo.toml").is_file() && parent.join("firmware").is_dir() {
            return Ok(parent.to_owned());
        }
    }
    bail!("run from the machine checkout or pass --root CHECKOUT")
}

fn execute(command: &mut Command) -> Result<()> {
    let status = command
        .status()
        .with_context(|| format!("start {command:?}"))?;
    ensure!(status.success(), "{command:?} exited {status}");
    Ok(())
}

fn output(command: &mut Command) -> Result<Output> {
    let out = command
        .output()
        .with_context(|| format!("start {command:?}"))?;
    ensure!(
        out.status.success(),
        "{command:?} exited {}: {}",
        out.status,
        String::from_utf8_lossy(&out.stderr)
    );
    Ok(out)
}

fn text_output(command: &mut Command) -> Result<String> {
    Ok(String::from_utf8(output(command)?.stdout)?
        .trim()
        .to_owned())
}

fn read_json(path: &Path) -> Result<Value> {
    serde_json::from_slice(&fs::read(path).with_context(|| format!("read {}", path.display()))?)
        .with_context(|| format!("parse {}", path.display()))
}

fn write_json(path: &Path, value: &impl serde::Serialize) -> Result<()> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    write(path, &bytes)
}

fn write(path: &Path, bytes: &[u8]) -> Result<()> {
    if let Some(parent) = path.parent().filter(|p| !p.as_os_str().is_empty()) {
        fs::create_dir_all(parent)?;
    }
    fs::write(path, bytes).with_context(|| format!("write {}", path.display()))
}

fn write_changed(path: &Path, bytes: &[u8]) -> Result<()> {
    if fs::read(path).is_ok_and(|prior| prior == bytes) {
        return Ok(());
    }
    write(path, bytes)
}

fn sha(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn option(args: &[String], name: &str) -> Result<Option<String>> {
    if let Some(index) = args.iter().position(|v| v == name) {
        return Ok(Some(
            args.get(index + 1)
                .with_context(|| format!("{name} requires a value"))?
                .clone(),
        ));
    }
    Ok(None)
}

fn flag(args: &[String], name: &str) -> bool {
    args.iter().any(|v| v == name)
}

fn validate_args(args: &[String], flags: &[&str], valued: &[&str]) -> Result<Vec<String>> {
    let mut positional = Vec::new();
    let mut index = 0;
    while index < args.len() {
        let arg = args[index].as_str();
        if valued.contains(&arg) {
            ensure!(args.get(index + 1).is_some(), "{arg} requires a value");
            index += 2;
        } else if flags.contains(&arg) {
            index += 1;
        } else {
            ensure!(!arg.starts_with('-'), "unknown option {arg}");
            positional.push(args[index].clone());
            index += 1;
        }
    }
    Ok(positional)
}

struct Temporary(PathBuf);
impl Temporary {
    fn new(name: &str) -> Result<Self> {
        let stamp = SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos();
        let path = env::temp_dir().join(format!("{name}-{}-{stamp}", std::process::id()));
        fs::create_dir(&path)?;
        Ok(Self(path))
    }
}
impl Drop for Temporary {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}
