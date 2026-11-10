//! This opt-in command refreshes the install guide's appliance illustrations from current meshes.
mod pixels;
mod refresh;

use anyhow::{Context, Result, bail};
use std::path::PathBuf;

#[derive(Default)]
struct Options {
    root: Option<PathBuf>,
    out: Option<PathBuf>,
    assets: Option<PathBuf>,
    views: Vec<String>,
}

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1).peekable();
    if args
        .peek()
        .is_none_or(|s| matches!(s.as_str(), "help" | "--help" | "-h"))
    {
        println!(
            "hsm-install-art refresh [--root DIR] [--out DIR] [--assets DIR] [--views NAME ...]"
        );
        return Ok(());
    }
    let operation = args.next().unwrap();
    if operation != "refresh" {
        bail!("unknown install-art operation {operation}");
    }
    let mut options = Options::default();
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--root" => options.root = Some(args.next().context("--root DIR")?.into()),
            "--out" => options.out = Some(args.next().context("--out DIR")?.into()),
            "--assets" => options.assets = Some(args.next().context("--assets DIR")?.into()),
            "--views" => {
                while args.peek().is_some_and(|s| !s.starts_with('-')) {
                    options.views.push(args.next().unwrap());
                }
            }
            _ => bail!("unknown argument {arg}"),
        }
    }
    refresh::run(options)
}
