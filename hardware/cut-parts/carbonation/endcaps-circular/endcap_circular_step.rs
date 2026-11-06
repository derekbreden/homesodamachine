//! The machined end cap's files: the disc, its two tap-drill holes through it, and the blind rod
//! register on its inside face, the +Z face. One part covers both caps. The STEP is the quote
//! artifact for CNC vendors, where the register is a machined feature; the laser file leaves it
//! out because a laser cuts only through.
//!
//!     endcap-circular-step [<output directory>]
use anyhow::{Context, Result, bail};
use hsm_endcap_circular_numbers as cap;
use hsm_kernel::part::write_shown_with_step;
use hsm_kernel::step::{AxialBore, RoundStock};
use hsm_kernel::{Body, v2};
use std::path::PathBuf;

const NAME: &str = "endcap-circular-2hole";
const OUTPUT: &str = "hardware/cut-parts/carbonation/endcaps-circular";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: endcap-circular-step [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;

    let inch = cap::INCH;
    let thickness = cap::THICKNESS_IN * inch;
    let hole_offset = cap::HOLE_SPACING_IN / 2. * inch;
    let hole_radius = cap::HOLE_DIAMETER_IN * inch / 2.;
    let stock = RoundStock {
        radius: cap::DIAMETER_IN * inch / 2.,
        height: thickness,
        bores: vec![
            AxialBore { center: v2(-hole_offset, 0.), radius: hole_radius, floor: 0. },
            AxialBore { center: v2(hole_offset, 0.), radius: hole_radius, floor: 0. },
            AxialBore {
                center: v2(-cap::REGISTER_RADIUS_IN * inch, 0.),
                radius: cap::REGISTER_DRILL_IN * inch / 2.,
                floor: thickness - cap::REGISTER_DEPTH_IN * inch,
            },
        ],
    };
    let solid = stock.solid()?;
    let color = Some(stainless()?);
    let quote = stock.step_bytes(NAME, color)?;
    let bodies = [Body { name: NAME, color, solid: &solid }];
    println!("{}", write_shown_with_step(&out, NAME, &bodies, quote)?);
    Ok(())
}

/// 316 stainless as the payload carries it: the materials catalog's colour, linear RGB at single
/// precision.
fn stainless() -> Result<[f64; 3]> {
    let catalog: serde_json::Value =
        serde_json::from_str(include_str!("../../../../tools/hsm/shared-data/catalog/materials.json"))?;
    let args = &catalog["colors"]["M_STAINLESS"]["args"];
    let mut linear = [0.; 3];
    for (i, channel) in linear.iter_mut().enumerate() {
        let c = args[i].as_f64().context("the stainless colour's channels")?;
        let curved = if c <= 0.04045 { c / 12.92 } else { ((c + 0.055) / 1.055).powf(2.4) };
        *channel = curved as f32 as f64;
    }
    Ok(linear)
}
