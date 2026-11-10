//! The cargo-config producer writes the workspace's canonical compiler-input fingerprint.
use anyhow::{Context, Result, bail};
use std::{env, path::{Path, PathBuf}};

fn main() {
    if let Err(error) = run() { eprintln!("[cargo-config] {error:#}"); std::process::exit(1); }
}

fn run() -> Result<()> {
    let mut root = env::var_os("HSM_REPO_ROOT").or_else(|| env::var_os("HSM_WORKSPACE")).map(PathBuf::from).unwrap_or_else(||
        Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(3).unwrap().to_owned());
    let mut output = None;
    let mut directory = None;
    let args = env::args().skip(1).collect::<Vec<_>>(); let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--root" | "--output" => {
                let flag = &args[i]; i += 1; let value = PathBuf::from(args.get(i).context("option requires a path")?);
                if flag == "--root" { root = value; } else { output = Some(value); }
            }
            "--help" | "-h" => { println!("hsm-cargo-config writes the canonical Rust compiler configuration.\n\nUsage: hsm-cargo-config [OUTPUT_DIRECTORY] [--root ROOT] [--output FILE]"); return Ok(()); }
            arg if !arg.starts_with('-') && directory.is_none() => directory = Some(PathBuf::from(arg)),
            arg => bail!("unknown cargo-config argument: {arg}"),
        }
        i += 1;
    }
    if directory.is_some() && output.is_some() { bail!("choose an output directory or --output, not both"); }
    let root = std::fs::canonicalize(root)?;
    let output = output.or_else(|| directory.map(|directory| directory.join("tools/hsm/cargo-config.json")))
        .unwrap_or_else(|| PathBuf::from("tools/hsm/cargo-config.json"));
    let output = if output.is_absolute() { output } else { root.join(output) };
    hsm_cargo_config::write(&root, &output)?;
    println!("-> {}", output.strip_prefix(&root).unwrap_or(&output).display());
    Ok(())
}
