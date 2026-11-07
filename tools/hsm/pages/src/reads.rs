//! The files a program reads, named for the build that records its inputs: with `HSM_READS`
//! naming a file, each read appends `path\tsha256`, as the kernel's reads do
//! (`tools/hsm/kernel/src/reads.rs`).
use anyhow::{Context, Result};
use sha2::{Digest, Sha256};
use std::io::Write;
use std::path::Path;
use std::sync::Once;

static BEGUN: Once = Once::new();

/// The bytes of `path`, its read recorded.
pub fn read(path: impl AsRef<Path>) -> Result<Vec<u8>> {
    let path = path.as_ref();
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    if let Some(log) = std::env::var_os("HSM_READS") {
        BEGUN.call_once(|| {
            let _ = std::fs::write(&log, "hsm-reads 1\n");
        });
        let full = std::env::current_dir().map(|d| d.join(path)).unwrap_or_else(|_| path.to_path_buf());
        let line = format!("{}\t{:x}\n", full.display(), Sha256::digest(&bytes));
        if let Ok(mut f) = std::fs::OpenOptions::new().append(true).open(log) {
            let _ = f.write_all(line.as_bytes());
        }
    }
    Ok(bytes)
}

/// The text of `path`, its read recorded.
pub fn text(path: impl AsRef<Path>) -> Result<String> {
    let path = path.as_ref();
    String::from_utf8(read(path)?).with_context(|| format!("{} is not UTF-8", path.display()))
}
