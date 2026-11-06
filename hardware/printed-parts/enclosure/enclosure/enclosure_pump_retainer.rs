//! The lower pump retainer's files from the declared Box: its wings relaxed, as it prints and
//! the page draws it from its STL, and seated, as the assemblies show it.
//!
//!     enclosure-pump-retainer [--box <declared Box>] [<output directory>]
#[path = "retainer/retainer.rs"]
mod retainer;

use anyhow::Result;
use hsm_enclosure_numbers::{Color, catalog, pump, shell, spec};
use hsm_enclosure_solid::pieces::{payload, solids};
use hsm_enclosure_solid::plan::{self, Graph, Shape};
use hsm_kernel::Body;
use hsm_kernel::part::{write_printed, write_shown};
use std::path::Path;

fn main() -> Result<()> {
    let (b, out) = hsm_enclosure_solid::run::arguments("enclosure-pump-retainer")?;
    for seated in [false, true] {
        let p = retainer::piece(&b, seated);
        write(&out, &p.graph, p.result, p.name, p.seated, p.color)?;
    }
    Ok(())
}

/// Relaxed, the retainer prints and draws from its STL; seated, it is drawn from its solid and
/// not printed.
fn write(dir: &Path, g: &Graph, result: Shape, name: &str, seated: bool, color: Color) -> Result<()> {
    let [solid] = solids(g, [result], None)?;
    let bodies = [Body { name, color: Some(color), solid: &solid }];
    if seated {
        write_shown(dir, name, &bodies)?;
        return Ok(());
    }
    write_printed(dir, name, &bodies)?;
    let step = std::fs::read(dir.join(format!("{name}.step")))?;
    let stl = std::fs::read(dir.join(format!("{name}.stl")))?;
    payload(dir, name, color, &stl, &step, None)
}
