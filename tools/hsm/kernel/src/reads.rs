//! The files a program reads, named for the part engine that keeps its runs.
//!
//! The engine (`tools/hsm/engine`, `build`) keeps a program's run by everything that decides its
//! files, and a file the program opens decides them as much as its numbers do. When `HSM_READS`
//! names a file, `Numbers::read` makes it with the line `hsm-reads 1`, and every read through the
//! kernel (a payload, a STEP and the payload it is read through, a DXF, a font) appends
//! `path\tsha256`, the path whole. A program built before this leaves no file, and the engine
//! keeps none of its runs.
use sha2::{Digest, Sha256};
use std::io::Write;
use std::path::Path;
use std::sync::Once;

static BEGUN: Once = Once::new();

/// A runtime JSON document, recorded among the inputs that decide this run's outputs.
pub fn json(path: impl AsRef<Path>) -> anyhow::Result<serde_json::Value> {
    use anyhow::Context;
    let path = path.as_ref();
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    read(path, &bytes);
    serde_json::from_slice(&bytes).with_context(|| format!("parsing {}", path.display()))
}

/// Say that this program names its reads, before it has read anything.
pub fn begin() {
    BEGUN.call_once(|| {
        if let Some(log) = std::env::var_os("HSM_READS") {
            let _ = std::fs::write(log, "hsm-reads 1\n");
        }
    });
}

/// `bytes`, read from `path`.
pub fn read(path: &Path, bytes: &[u8]) {
    if std::env::var_os("HSM_READS").is_some() {
        digest(path, &format!("{:x}", Sha256::digest(bytes)));
    }
}

/// The file at `path`, read, whose SHA-256 is `digest`.
pub fn digest(path: &Path, digest: &str) {
    let Some(log) = std::env::var_os("HSM_READS") else {
        return;
    };
    begin();
    let full = std::env::current_dir()
        .map(|d| d.join(path))
        .unwrap_or_else(|_| path.to_path_buf());
    // One write of one line, appended, so lines from two threads never interleave.
    let line = format!("{}\t{digest}\n", full.display());
    if let Ok(mut f) = std::fs::OpenOptions::new().append(true).open(log) {
        let _ = f.write_all(line.as_bytes());
    }
}
