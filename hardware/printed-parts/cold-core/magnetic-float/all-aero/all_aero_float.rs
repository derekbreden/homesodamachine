//! The one-piece ASA Aero float's files: the float with its RC62 magnet sealed in, as the site
//! shows it, the float body's STL that prints, with the STEP and model beside it that the float
//! integration check reads, and the calculations the float build guide and the print setup read
//! (`design.json`). The guide bore is on Z and the flat print bottom at Z = 0; the magnet drops
//! into the closed annular pocket at the print's pause.
//!
//!     all-aero-float [<output directory>]
use anyhow::{Result, bail, ensure};
use hsm_aero_float_numbers as float;
use hsm_cold_core_catalog as catalog;
use hsm_kernel::part::{write_printed, write_shown};
use hsm_kernel::*;
use std::path::PathBuf;

mod design;

const OUTPUT: &str = "hardware/printed-parts/cold-core/magnetic-float/all-aero";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: all-aero-float [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;

    let seat = float::magnet_seat();
    let pocket = annulus(float::POCKET_OD / 2., float::POCKET_ID / 2., seat, float::pocket_roof())?;
    let body = annulus(float::DIAMETER / 2., float::BORE_DIAMETER / 2., 0., float::height())?.cut(&pocket)?;
    let magnet = annulus(float::MAGNET_OD / 2., float::MAGNET_ID / 2., seat, seat + float::MAGNET_THICKNESS)?;
    body.check()?;
    ensure!(body.components().len() == 1, "the float is one connected body round its closed pocket");
    ensure!(body.intersect(&magnet)?.volume() < 1e-7, "the RC62 clears the float's pocket");

    let aero = Some(catalog::asa_aero_white().linear);
    let metal = Some(catalog::hex(float::MAGNET_COLOUR).linear);
    println!("{}", write_printed(&out, "float-aero", &[Body { name: "float-aero", color: aero, solid: &body }])?);
    let assembly = [
        Body { name: "float-aero", color: aero, solid: &body },
        Body { name: "RC62", color: metal, solid: &magnet },
    ];
    println!("{}", write_shown(&out, "assembly", &assembly)?);
    std::fs::write(out.join("design.json"), design::json()?)?;
    Ok(())
}

/// The ring between two radii, standing from `bottom` to `top`.
fn annulus(outer: f64, inner: f64, bottom: f64, top: f64) -> Result<Solid> {
    let section = Profile::circle(v2(0., 0.), outer).with_hole(Loop::circle(v2(0., 0.), inner));
    Plane::XY.at(v3(0., 0., bottom)).extrude(&section, top - bottom)
}
