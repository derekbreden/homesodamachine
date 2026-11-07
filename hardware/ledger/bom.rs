//! The bill of materials and the attended-labor ledger: bom.md's printed-part masses from the
//! parts' fine models, its hardware counts and the figures they price from the machine's parts,
//! its section and grand totals, and labor.md's runs and totals, with each document's figures
//! sidecar. `--check` writes nothing and says which figures are stale; `--totals` writes only the
//! totals and the labor ledger, for a tree that carries its masses and counts in from a build.
//!
//!     bom [--check | --totals] [<output directory>]
#[path = "bom/hardware.rs"]
mod hardware;
#[path = "bom/inputs.rs"]
mod inputs;

use anyhow::{Result, bail};
use hsm_ledger::{bom, bom_sync, labor, printing, shared::Context};
use serde_json::json;
use std::path::{PathBuf, absolute};

fn main() -> Result<()> {
    hsm_kernel::reads::begin();
    let (mut check, mut totals, mut out) = (false, false, None);
    for arg in std::env::args().skip(1) {
        match arg.as_str() {
            "--check" => check = true,
            "--totals" => totals = true,
            other if other.starts_with("--") => bail!("unknown option {other}"),
            other => out = Some(absolute(PathBuf::from(other))?),
        }
    }
    let root = absolute(".")?;
    let mut ledger = Context::at(root.clone(), out);
    let request = json!({"check": check});
    let mut status = 0;
    let mut say = |result: serde_json::Value| {
        print!("{}", result["output"].as_str().unwrap_or(""));
        status = status.max(result["status"].as_i64().unwrap_or(1));
    };
    // The masses first: the hardware counts, the totals and the print-farm figures read §7.
    if !totals {
        say(printing::dispatch("mass_main", &request, &mut ledger)?);
        if !check {
            say(bom_sync::sync(&inputs::inputs(&root)?, &mut ledger)?);
        }
    }
    say(bom::dispatch("main", &request, &mut ledger)?);
    say(labor::dispatch("main", &request, &mut ledger)?);
    std::process::exit(status as i32)
}
