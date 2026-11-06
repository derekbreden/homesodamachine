//! Physical model export from explicit file references, frames and bodies made in process:
//! the fine archive, its STEP and the payload the viewer draws.
use anyhow::{Context, Result};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::path::Path;

pub mod component_order;
pub mod model;
pub mod payload;

pub fn text<'a>(value: &'a Value, key: &str) -> Result<&'a str> {
    value
        .get(key)
        .and_then(Value::as_str)
        .with_context(|| format!("missing text {key}"))
}

pub fn read(path: &Path) -> Result<Vec<u8>> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(path, &bytes);
    Ok(bytes)
}

pub fn digest(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

pub fn put(path: &Path, bytes: &[u8]) -> Result<()> {
    if path.is_file()
        && std::fs::metadata(path)?.len() == bytes.len() as u64
        && std::fs::read(path)? == bytes
    {
        return Ok(());
    }
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let temp = path.with_file_name(format!(
        ".{}.{}.tmp",
        path.file_name().unwrap().to_string_lossy(),
        std::process::id()
    ));
    std::fs::write(&temp, bytes)?;
    std::fs::rename(&temp, path)?;
    Ok(())
}

pub fn output_name(path: &Path, output: &Path) -> String {
    path.strip_prefix(output)
        .unwrap_or(path)
        .to_string_lossy()
        .into_owned()
}
