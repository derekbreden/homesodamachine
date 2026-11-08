//! The side-loading pump cartridge's print and installed files from the declared Box.
//!
//!     enclosure-pump-retainer [--box <declared Box>] [<output directory>]
#[path = "retainer/retainer.rs"]
mod retainer;

use anyhow::Result;
use hsm_enclosure_numbers::{Color, catalog, spec};
use hsm_enclosure_solid::pieces::{digest, keep, payload, solids};
use hsm_enclosure_solid::plan::{self, Graph, Shape};
use hsm_kernel::Body;
use hsm_kernel::write::{PrintOutput, payload_bytes_with_sources};
use std::path::Path;

fn main() -> Result<()> {
    let (b, out) = hsm_enclosure_solid::run::arguments("enclosure-pump-retainer")?;
    for seated in [false, true] {
        let p = retainer::piece(&b, seated);
        write(&out, &p.graph, p.result, p.name, p.seated, p.color)?;
    }
    Ok(())
}

/// The standalone cartridge draws from its STL; the installed alias carries the same solid.
fn write(dir: &Path, g: &Graph, result: Shape, name: &str, seated: bool, color: Color) -> Result<()> {
    let [solid] = solids(g, [result], None)?;
    let bodies = [Body { name, color: Some(color), solid: &solid }];
    if seated {
        let model=hsm_kernel::model_bytes(&bodies);
        keep(&dir.join(format!("{name}.step.npz")),&model)?;
        let bytes=payload_bytes_with_sources(&bodies,Some(&digest(&model)),None);
        let mut head=hsm_kernel::scene::pack(&bytes)?;
        head["step_export"]=false.into();
        hsm_kernel::scene::persist(&dir.join(format!("{name}.step.mesh")),&head)?;
        return Ok(());
    }
    let simple=solid.simplified()?;
    let print=PrintOutput::new(&[Body{name,color:Some(color),solid:&simple}]);
    let model=print.model_bytes(&bodies,&format!("{name}.stl"),None)?;
    let stl=print.into_stl_bytes();
    keep(&dir.join(format!("{name}.step.npz")),&model)?;
    keep(&dir.join(format!("{name}.stl")),&stl)?;
    payload(dir, name, color, &stl, &model, None)
}
