//! The evaporator coil's model for its fabrication drawing: the wrap and both tails as the coil
//! is ordered, each tail on past the front wall to its working stub, written as the fine model the
//! drawing projects its views from (`evaporator-coil.step.npz`). The drawing runs it when the coil
//! is ordered.
//!
//!     evaporator-coil-model [<output directory>]
#[path = "core-assembly/copper.rs"]
mod copper;

use anyhow::{Context, Result, bail};
use hsm_coil_numbers::Tail;
use hsm_kernel::write::Body;
use std::path::PathBuf;

const NAME: &str = "evaporator-coil";
const OUTPUT: &str = ".cache/drawings/evaporator-coil";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: evaporator-coil-model [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let chord = hsm_cold_core_assembly_numbers::COIL_PATH_CHORD;
    let mut copper = vec![("evap-coil".to_owned(), copper::wrap(chord)?)];
    for tail in Tail::BOTH {
        copper.push((format!("evap-tail-{}", tail.name()), copper::tail(tail, true, chord)?));
    }
    let colour = hsm_cold_core_catalog::copper().linear;
    let bodies: Vec<Body> =
        copper.iter().map(|(name, solid)| Body { name, color: Some(colour), solid }).collect();
    let path = out.join(format!("{NAME}.step.npz"));
    std::fs::write(&path, hsm_kernel::step::model_bytes(&bodies))
        .with_context(|| format!("writing {}", path.display()))?;
    println!("{}", serde_json::json!({"files": [format!("{NAME}.step.npz")], "model": path}));
    Ok(())
}
