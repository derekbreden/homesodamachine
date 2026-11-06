//! A piece program's command line: the declared Box it cuts from and the directory its files go
//! into. A program runs at the repository root, or a copy of the files it reads at their
//! repository paths.
use anyhow::{Context, Result, bail};
use hsm_enclosure_numbers::spec::Box;
use std::path::{Path, PathBuf};

pub const BOX: &str = "hardware/manifold-layout/enclosure-box.json";
pub const OUTPUT: &str = "hardware/printed-parts/enclosure/enclosure";

/// The Box and the output directory `<program> [--box <declared Box>] [<output directory>]`
/// names, with the Box read as the run's first input.
pub fn arguments(program: &str) -> Result<(Box, PathBuf)> {
    let usage = format!("usage: {program} [--box <declared Box>] [<output directory>]");
    let (mut declared, mut out) = (PathBuf::from(BOX), None);
    let mut args = std::env::args_os().skip(1);
    while let Some(arg) = args.next() {
        match arg.to_str() {
            Some("--box") => declared = args.next().with_context(|| usage.clone())?.into(),
            _ if out.is_none() => out = Some(PathBuf::from(arg)),
            _ => bail!(usage),
        }
    }
    let out = out.unwrap_or_else(|| PathBuf::from(OUTPUT));
    hsm_kernel::reads::begin();
    let document = read(&declared)?;
    let b = Box::from_document(serde_json::from_slice(&document)?).with_context(|| declared.display().to_string())?;
    std::fs::create_dir_all(&out)?;
    Ok((b, out))
}

/// A file's bytes, listed among the run's reads.
pub fn read(path: &Path) -> Result<Vec<u8>> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(path, &bytes);
    Ok(bytes)
}
