//! The faucet's umbilical organizer, upright as it prints: round stock, its rims eased, and five
//! passages through it, each eased at both ends: four round tube bores and the cable's flat slot.
//!
//!     umbilical-organizer [<output directory>]
use anyhow::Result;
use hsm_faucet_numbers::catalog;
use hsm_kernel::*;
use hsm_print_payload::printed;
use hsm_umbilical_organizer_numbers::{self as puck, Passage};
use std::f64::consts::FRAC_PI_2;

const NAME: &str = "umbilical-organizer";

/// How far a bore's cutter runs past the stock's faces.
const PAST: f64 = 1.0;

fn main() -> Result<()> {
    let out = printed::out_dir("hardware/printed-parts/faucet/umbilical-organizer")?;
    let length = puck::LENGTH;
    let stock = Solid::cylinder(V3::ZERO, V3::Z, puck::OD / 2.0, length)?;
    let mut body = stock.chamfer(&stock.edges("%Circle")?, puck::OUTSIDE_EASE)?;
    for (_, xy, passage) in puck::BORES {
        let (x, y) = (xy[0] - puck::CENTRE_XY[0], xy[1] - puck::CENTRE_XY[1]);
        let cutters = match passage {
            Passage::Slot => {
                let entry = puck::CABLE_ENTRY;
                let section = |z: f64, grow: f64| {
                    let r = puck::CABLE_SLOT_DEPTH / 2.0 + grow;
                    let half = (puck::CABLE_SLOT_LENGTH - puck::CABLE_SLOT_DEPTH) / 2.0;
                    let conic = |cx, t0, t1| LoftEdge::Conic { c: v3(cx, y, z), x: v3(r, 0.0, 0.0), y: v3(0.0, r, 0.0), t0, t1 };
                    LoftSection::new(vec![
                        LoftEdge::Line { a: v3(x - half, y - r, z), b: v3(x + half, y - r, z) },
                        conic(x + half, -FRAC_PI_2, FRAC_PI_2),
                        LoftEdge::Line { a: v3(x + half, y + r, z), b: v3(x - half, y + r, z) },
                        conic(x - half, FRAC_PI_2, 3.0 * FRAC_PI_2),
                    ])
                };
                vec![
                    Solid::extrude(&section(-PAST, 0.0).region(), V3::Z, v3(0.0, 0.0, length + 2.0 * PAST))?,
                    Solid::thru_sections(&[section(0.0, entry), section(entry, 0.0)], true)?,
                    Solid::thru_sections(&[section(length - entry, 0.0), section(length, entry)], true)?,
                ]
            }
            Passage::Bore(diameter) => {
                let (radius, entry) = (diameter / 2.0, puck::ENTRY);
                vec![
                    Solid::cylinder(v3(x, y, -PAST), V3::Z, radius, length + 2.0 * PAST)?,
                    Solid::cone(v3(x, y, 0.0), V3::Z, radius + entry, radius, entry)?,
                    Solid::cone(v3(x, y, length - entry), V3::Z, radius, radius + entry, entry)?,
                ]
            }
        };
        body = body.cut(&Solid::union_all(&cutters)?)?;
    }
    let body = Body { name: NAME, color: Some(catalog::faucet_black()), solid: &body };
    println!("{}", printed::write(&out, NAME, body)?);
    Ok(())
}
