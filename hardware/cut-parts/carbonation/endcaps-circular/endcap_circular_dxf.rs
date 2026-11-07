//! The end cap's laser file, the one SendCutSend cuts both discs from: the disc and its two NPT tap
//! drills as CIRCLE entities on layer 0 of an R2010 DXF in inches. The rod register is not in it:
//! it is a blind hole drilled in-house from the inside face, and a laser cuts only through, which
//! would breach the pressure boundary. The template carries the format's headers, tables, blocks and
//! objects, with handles left free for the cut's entities. It runs by hand when the cap's numbers
//! change, outside the normal build, and leaves the file as it is when its bytes come out the same.
//!
//!     endcap-circular-dxf [<output directory>]
use anyhow::{Result, bail, ensure};
use hsm_endcap_circular_numbers as cap;
use std::fmt::Write;
use std::path::PathBuf;

const OUTPUT: &str = "hardware/cut-parts/carbonation/endcaps-circular";
const NAME: &str = "endcap-circular-2hole.dxf";
/// The template's first free handle, and how many it leaves before its own objects resume.
const FIRST_HANDLE: usize = 0x2F;
const FREE_HANDLES: usize = 3;

/// A circle at `center` of `radius`, as an entity with `handle` in the template's model space
/// (block record 0x17).
fn circle(text: &mut String, center: [f64; 2], radius: f64, handle: usize) -> std::fmt::Result {
    write!(
        text,
        "  0\nCIRCLE\n  5\n{handle:X}\n330\n17\n100\nAcDbEntity\n  8\n0\n100\nAcDbCircle\n 10\n{:?}\n 20\n{:?}\n 30\n0.0\n 40\n{:?}\n",
        center[0], center[1], radius
    )
}

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: endcap-circular-dxf [<output directory>]");
    }
    std::fs::create_dir_all(&out)?;
    let hole = cap::HOLE_DIAMETER_IN / 2.;
    let offset = cap::HOLE_SPACING_IN / 2.;
    let circles = [([0., 0.], cap::DIAMETER_IN / 2.), ([-offset, 0.], hole), ([offset, 0.], hole)];
    ensure!(circles.len() <= FREE_HANDLES, "the template leaves handles for {FREE_HANDLES} entities");
    let mut body = String::new();
    for (index, (center, radius)) in circles.iter().enumerate() {
        circle(&mut body, *center, *radius, FIRST_HANDLE + index)?;
    }
    let text = include_str!("r2010-template.dxf.in").replace("{{ENTITIES}}\n", &body);
    let path = out.join(NAME);
    hsm_documents::write_if_changed(&path, &hsm_documents::canonicalize_dxf(text.as_bytes()))?;
    println!("-> {}", path.display());
    Ok(())
}
