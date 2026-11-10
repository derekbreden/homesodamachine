//! Optional PCB commands build the detailed board model and inspect authored copper and silkscreen.
mod circuit;
mod geometry;
mod harness;
mod model;
mod routing;
mod silk;

use anyhow::{Context, Result, bail, ensure};
use std::{
    env, fs,
    path::{Path, PathBuf},
    process::Command,
};

fn main() {
    if let Err(error) = run() {
        eprintln!("{error:#}");
        std::process::exit(1);
    }
}
fn run() -> Result<()> {
    let mut args = env::args().skip(1).collect::<Vec<_>>();
    let cwd = env::current_dir()?;
    let root = if args.first().is_some_and(|s| s == "--root") {
        ensure!(args.len() > 2, "--root CHECKOUT COMMAND");
        let p = PathBuf::from(args.remove(1)).canonicalize()?;
        args.remove(0);
        p
    } else {
        cwd.ancestors()
            .find(|p| p.join("tools/hsm/Cargo.toml").is_file())
            .context("run from the checkout or pass --root")?
            .to_owned()
    };
    ensure!(
        !args.is_empty(),
        "hsm-pcb COMMAND [ARGS]; commands: model, harness-crops, orientation, trace-check, topreach, plot-region, silk-audit, run-lock"
    );
    let command = args.remove(0);
    match command.as_str() {
        "model" => model::run(&root, &args),
        "harness-crops" => harness::run(&root, &args),
        "orientation" => model::orientation(&root, &args),
        "trace-check" => routing::trace_check(&args),
        "topreach" => routing::topreach(&args),
        "plot-region" => routing::plot(&args),
        "silk-audit" => silk::run(&root, &args),
        "run-lock" => run_lock(&args),
        "help" | "--help" | "-h" => {
            println!(
                "hsm-pcb COMMAND [ARGS]\nCommands: model, harness-crops, orientation, trace-check, topreach, plot-region, silk-audit, run-lock"
            );
            Ok(())
        }
        _ => bail!("unknown PCB command {command}"),
    }
}
fn output(command: &mut Command) -> Result<Vec<u8>> {
    let out = command
        .output()
        .with_context(|| format!("start {command:?}"))?;
    ensure!(
        out.status.success(),
        "{command:?}: {}",
        String::from_utf8_lossy(&out.stderr)
    );
    Ok(out.stdout)
}
fn write(path: &Path, bytes: &[u8]) -> Result<()> {
    if let Some(parent) = path.parent().filter(|p| !p.as_os_str().is_empty()) {
        fs::create_dir_all(parent)?;
    }
    fs::write(path, bytes)?;
    Ok(())
}
fn run_lock(args: &[String]) -> Result<()> {
    use sha2::{Digest, Sha256};
    use std::{
        io::{Read, Write},
        os::fd::AsRawFd,
        os::unix::fs::OpenOptionsExt,
        thread,
        time::Duration,
    };
    ensure!(args.len() == 1, "run-lock BOARD_KEY");
    let _lease =
        hsm_run_slots::inherited()?.context("board mutex requires a verified parent run lease")?;
    let hash = format!("{:x}", Sha256::digest(args[0].as_bytes()));
    let path = hsm_run_slots::directory()?.join(format!("board.{}.lock", &hash[..16]));
    let lock = fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .mode(0o600)
        .open(path)?;
    loop {
        if unsafe { libc::flock(lock.as_raw_fd(), libc::LOCK_EX | libc::LOCK_NB) } == 0 {
            break;
        }
        let error = std::io::Error::last_os_error();
        ensure!(
            error.kind() == std::io::ErrorKind::WouldBlock,
            "board lock failed: {error}"
        );
        let mut poll = libc::pollfd {
            fd: 0,
            events: libc::POLLIN | libc::POLLHUP,
            revents: 0,
        };
        if unsafe { libc::poll(&mut poll, 1, 100) } > 0 {
            let mut byte = [0];
            if std::io::stdin().read(&mut byte)? == 0 {
                return Ok(());
            }
        }
        thread::sleep(Duration::from_millis(1));
    }
    println!("{{\"ready\":true}}");
    std::io::stdout().flush()?;
    std::io::copy(&mut std::io::stdin(), &mut std::io::sink())?;
    Ok(())
}
