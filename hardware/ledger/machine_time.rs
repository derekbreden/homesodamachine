//! The print farm's occupancy: `machine-time.md`'s figures and their sidecar, from the BOM's
//! printed masses and the native slices' times.
//!
//!     machine-time [--check] [<output directory>]
use anyhow::{Result, bail};
use hsm_ledger::{printing, shared::Context};
use serde_json::json;
use std::path::{PathBuf, absolute};

fn main() -> Result<()> {
    hsm_kernel::reads::begin();
    let (mut check, mut out) = (false, None);
    for arg in std::env::args().skip(1) {
        match arg.as_str() {
            "--check" => check = true,
            other if other.starts_with("--") => bail!("unknown option {other}"),
            other => out = Some(absolute(PathBuf::from(other))?),
        }
    }
    let mut ledger = Context::at(absolute(".")?, out);
    let result = printing::dispatch("main", &json!({"check": check}), &mut ledger)?;
    print!("{}", result["output"].as_str().unwrap_or(""));
    std::process::exit(result["status"].as_i64().unwrap_or(1) as i32)
}
