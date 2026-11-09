//! Runtime design files keep editable numbers outside the compiled geometry program.
use anyhow::{Context, Result};
use serde::de::DeserializeOwned;
use std::path::Path;

/// A design document read from the run's repository frame and recorded for kept runs.
pub fn json<T: DeserializeOwned>(path: impl AsRef<Path>) -> Result<T> {
    let path = path.as_ref();
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(path, &bytes);
    serde_json::from_slice(&bytes).with_context(|| format!("parsing {}", path.display()))
}
