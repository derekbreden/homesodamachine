//! The TPU ring between the machine display's glass and its cover: the glass's outline less the
//! cover's window, filling the gap between the glass and the cover's underside, in the cover's
//! own frame.
//!
//!     display-gasket [<output directory>]
use anyhow::Result;
use hsm_enclosure_numbers::display_mount as m;
use hsm_kernel::part::write_part;
use hsm_kernel::{Body, Loop, Plane, Profile, Solid, v2, v3};

const NAME: &str = "display-gasket";

/// The ring prints in the catalog's black TPU.
const TPU_BLACK: [f64; 3] = [0.01960664801299572, 0.01960664801299572, 0.01960664801299572];

/// A rounded rectangle about the display's centre, between two depths.
fn rounded(width: f64, height: f64, corner: f64, lo: f64, hi: f64) -> Result<Solid> {
    let outer = Loop::rounded_rect(v2(0.0, 0.0), width, height, corner)?;
    Plane::XY.at(v3(0.0, 0.0, lo)).extrude(&Profile { outer, holes: vec![] }, hi - lo)
}

fn main() -> Result<()> {
    let out = hsm_enclosure_components::output(NAME, "hardware/printed-parts/enclosure/display-gasket")?;
    // The ring bears on the cover's underside and the glass below it; the window is cut through
    // past both faces, at the glass's corners.
    let (top, bottom) = (-m::THICK, -m::THICK - m::GASKET_THICK);
    let corner = m::WINDOW[2];
    let ring = rounded(m::GLASS[0], m::GLASS[1], corner, bottom, top)?
        .cut(&rounded(m::WINDOW[0], m::WINDOW[1], corner, bottom - 1.0, top + 1.0)?)?;
    println!("{}", write_part(&out, NAME, &[Body { name: NAME, color: Some(TPU_BLACK), solid: &ring }])?);
    Ok(())
}
