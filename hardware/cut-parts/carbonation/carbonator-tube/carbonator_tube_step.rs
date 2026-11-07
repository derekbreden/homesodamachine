//! The carbonator tube's files: the barrel as it is cut from 316 stainless tube, ends square and
//! its bore straight through, standing on the saw's datum at the origin rather than where the cold
//! core places it. The STEP is the quote artifact; the model and payload are what the site shows.
//!
//!     carbonator-tube-step [<output directory>]
use anyhow::{Context, Result, bail};
use hsm_carbonator_tube_numbers as tube;
use hsm_kernel::part::write_shown_with_step;
use hsm_kernel::step::{AxialBore, RoundStock};
use hsm_kernel::{Body, v2};
use std::path::PathBuf;

const NAME: &str = "carbonator-tube";
const OUTPUT: &str = "hardware/cut-parts/carbonation/carbonator-tube";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: carbonator-tube-step [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;

    let stock = RoundStock {
        radius: tube::OUTER_RADIUS,
        height: tube::LENGTH,
        bores: vec![AxialBore { center: v2(0., 0.), radius: tube::ID / 2., floor: 0. }],
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
