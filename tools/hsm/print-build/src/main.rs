//! The print build carries each completed producer and publishes it while the remaining build continues.
use anyhow::{Context, Result, bail};
use hsm_print_build::{Config, run};
use std::path::PathBuf;

const USAGE: &str = "hsm-print-build carries and publishes completed producers progressively.\n\nUsage: hsm-print-build [--root ROOT] [--run-dir DIR] [--runner PATH] [--bazel PATH] [--publisher PATH] [--progress PATH] -- [BAZEL_ARGS ...]\nWithout Bazel arguments the normal print build selects //:everything.";

fn main() {
    let result = main_result();
    match result {
        Ok(code) => std::process::exit(code),
        Err(error) => {
            eprintln!("[print-build] {error:#}");
            std::process::exit(1);
        }
    }
}

fn main_result() -> Result<i32> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    let mut config = Config::defaults()?;
    let mut index = 0;
    while index < args.len() {
        match args[index].as_str() {
            "--" => { config.bazel_args = args[index + 1..].to_vec(); break; }
            "--help" | "-h" => { println!("{USAGE}"); return Ok(0); }
            flag @ ("--root" | "--run-dir" | "--runner" | "--bazel" | "--publisher" | "--progress") => {
                index += 1;
                let value = PathBuf::from(args.get(index).with_context(|| format!("{flag} requires a path"))?);
                match flag {
                    "--root" => config.root = value,
                    "--run-dir" => config.run_dir = Some(value),
                    "--runner" => config.runner = Some(value),
                    "--bazel" => config.bazel = value,
                    "--publisher" => config.publisher = Some(value),
                    "--progress" => config.progress = Some(value),
                    _ => unreachable!(),
                }
            }
            flag if flag.starts_with("--root=") => config.root = PathBuf::from(&flag[7..]),
            flag if flag.starts_with("--run-dir=") => config.run_dir = Some(PathBuf::from(&flag[10..])),
            flag if flag.starts_with("--runner=") => config.runner = Some(PathBuf::from(&flag[9..])),
            flag if flag.starts_with("--bazel=") => config.bazel = PathBuf::from(&flag[8..]),
            flag if flag.starts_with("--publisher=") => config.publisher = Some(PathBuf::from(&flag[12..])),
            flag if flag.starts_with("--progress=") => config.progress = Some(PathBuf::from(&flag[11..])),
            "" => bail!("an empty argument cannot select a build"),
            _ => { config.bazel_args = args[index..].to_vec(); break; }
        }
        index += 1;
    }
    run(config)
}
