use anyhow::{Context, Result, bail};
use hsm_run_slots::runtime::{install, runner};
use serde_json::Value;
use std::path::{Path, PathBuf};
fn main() {
    match main_result() {
        Ok(code) => std::process::exit(code),
        Err(error) => {
            eprintln!("[run] {error:#}");
            std::process::exit(if error.to_string().starts_with("usage:") {
                2
            } else {
                1
            });
        }
    }
}
fn main_result() -> Result<i32> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    match args.first().map(String::as_str) {
        Some("--workspace") => {
            let root = Path::new(args.get(1).context("workspace path")?);
            install::run_current(root, &args[2..])
        }
        Some("--rebuild-runtime") => {
            let root = Path::new(args.get(1).context("workspace path")?);
            install::rebuild_runtime(root)?;
            Ok(0)
        }
        Some("--runtime-info") => {
            let root = Path::new(args.get(1).context("workspace path")?);
            println!("{}", install::info(root)?);
            Ok(0)
        }
        Some("--bootstrap") => {
            let root = match args.get(1) {
                Some(path) => PathBuf::from(path),
                None => std::env::current_dir()?,
            };
            println!("{}", install::bootstrap(&root)?);
            Ok(0)
        }
        Some("--install-runtime") => {
            let root = Path::new(args.get(1).context("workspace path")?);
            let destination = args
                .get(2)
                .map(PathBuf::from)
                .unwrap_or_else(install::prefix);
            println!("{}", install::install_runtime(root, &destination)?);
            Ok(0)
        }
        Some("--install-hsm") => {
            let workspace = Path::new(args.get(1).context("workspace path")?);
            let mut binary = None;
            let mut destination = install::prefix();
            let mut sockets = Vec::new();
            let mut i = 2;
            while i < args.len() {
                let flag = &args[i];
                match flag.as_str() {
                    "--help" | "-h" => {
                        println!(
                            "Install the built hsm and its native host runtime.\n\nUsage: hsm-run --install-hsm WORKSPACE BINARY [--root DIRECTORY] [--legacy-socket PATH]"
                        );
                        return Ok(0);
                    }
                    "--root" | "--legacy-socket" => {
                        i += 1;
                        let value = args.get(i).context("usage: installer option value")?;
                        if flag == "--root" {
                            destination = PathBuf::from(value);
                        } else {
                            sockets.push(value.clone());
                        }
                    }
                    _ if flag.starts_with("--root=") => destination = PathBuf::from(&flag[7..]),
                    _ if flag.starts_with("--legacy-socket=") => sockets.push(flag[16..].into()),
                    _ if flag.starts_with('-') => {
                        bail!("usage: unrecognized installer option {flag}")
                    }
                    _ if binary.is_none() => binary = Some(PathBuf::from(flag)),
                    _ => bail!("usage: unexpected installer argument {flag}"),
                }
                i += 1;
            }
            let binary = binary.context("usage: hsm binary path")?;
            let receipt = install::install_hsm(&binary, &destination, &sockets, workspace)?;
            println!("{}", serde_json::to_string_pretty(&receipt)?);
            Ok(0)
        }
        Some("--install-tools") => {
            let workspace = Path::new(args.get(1).context("workspace path")?);
            let mut destination = install::prefix();
            let mut binaries = Vec::new();
            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--prefix" => {
                        i += 1;
                        destination = PathBuf::from(args.get(i).context("--prefix directory")?);
                    }
                    "-h" | "--help" => {
                        println!(
                            "Install built native tools at immutable paths.\nUsage: hsm-run --install-tools WORKSPACE [--prefix DIRECTORY] BINARY..."
                        );
                        return Ok(0);
                    }
                    name if name.starts_with('-') => bail!("unknown tool installer option {name}"),
                    name => binaries.push(PathBuf::from(name)),
                }
                i += 1;
            }
            anyhow::ensure!(!binaries.is_empty(), "name the built tools to install");
            println!(
                "{}",
                install::install_tools(workspace, &destination, &binaries)?
            );
            Ok(0)
        }
        Some("--request") => {
            let input: Value = serde_json::from_str(args.get(1).context("JSON request")?)?;
            println!("{}", hsm_run_slots::runtime::dispatch(input, None)?);
            Ok(0)
        }
        _ => runner::run(&args),
    }
}
