//! Where a zone C program's files go: the directory its command line names, or its own in the
//! tree; a file holding the same bytes is left as it is.
use anyhow::{Context, Result, bail};
use std::path::{Path, PathBuf};

/// The directory the program writes to. It names what it reads from here on.
pub fn out_dir(own: &str) -> Result<PathBuf> {
    hsm_kernel::reads::begin();
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| own.into());
    if args.next().is_some() {
        bail!("usage: {} [<output directory>]", std::env::args().next().unwrap_or_default());
    }
    std::fs::create_dir_all(&out)?;
    Ok(out)
}

/// Write `bytes` to `path` unless it already holds them, through a temporary beside it.
pub fn keep(path: &Path, bytes: &[u8]) -> Result<()> {
    if std::fs::read(path).ok().as_deref() == Some(bytes) {
        return Ok(());
    }
    let name = path.file_name().context("output has a file name")?.to_string_lossy();
    let temporary = path.with_file_name(format!(".{name}.{}", std::process::id()));
    std::fs::write(&temporary, bytes)?;
    std::fs::rename(&temporary, path)?;
    Ok(())
}

/// Write `value` to `path` as JSON, the way the installed machine reads a part's placement.
pub fn json(path: &Path, value: &serde_json::Value) -> Result<()> {
    keep(path, (serde_json::to_string_pretty(value)? + "\n").as_bytes())
}
