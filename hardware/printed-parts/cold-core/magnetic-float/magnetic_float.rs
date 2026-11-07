//! The PETG-shell bench float's files: its ASA Aero core and the RC62 magnet the core seats, as
//! the site shows them, the STLs the core, the PETG envelope and the Aero insert print from, and
//! the calculations its print setup and checks read (`design.json`). Each printed piece stands on
//! its own print face; the magnet stands where it seats in the float.
//!
//!     magnetic-float [<output directory>]
use anyhow::{Result, bail};
use hsm_kernel::part::{write_part, write_shown};
use hsm_kernel::*;
use hsm_magnetic_float_numbers as float;
use std::path::PathBuf;

mod design;

const OUTPUT: &str = "hardware/printed-parts/cold-core/magnetic-float";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: magnetic-float [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;

    let (outer, inner) = (float::CORE_OUTER_RADIUS, float::CORE_INNER_RADIUS);
    let pocket = annulus(float::POCKET_OD / 2., float::POCKET_ID / 2., float::MAGNET_SEAT, float::INSERT_BOTTOM)?;
    let core = led_annulus(outer, inner, float::FLOOR, float::INSERT_BOTTOM)?
        .cut(&pocket)?
        .translate(v3(0., 0., -float::FLOOR));
    let magnet_top = float::MAGNET_SEAT + float::MAGNET_THICKNESS;
    let magnet = annulus(float::MAGNET_OD / 2., float::MAGNET_ID / 2., float::MAGNET_SEAT, magnet_top)?;
    let envelope = annulus(float::OUTER_RADIUS, float::BORE_RADIUS, 0., float::HEIGHT)?
        .cut(&annulus(outer, inner, float::FLOOR, float::ROOF_BOTTOM)?)?;
    let insert = led_annulus(outer, inner, float::INSERT_BOTTOM, float::INSERT_TOP)?
        .translate(v3(0., 0., -float::INSERT_BOTTOM));

    let core = [Body { name: "body-aero", color: Some(float::aero_colour().linear), solid: &core }];
    println!("{}", write_part(&out, "body-aero", &core)?);
    let magnet = [Body { name: "magnet", color: Some(float::magnet_colour().linear), solid: &magnet }];
    println!("{}", write_shown(&out, "magnet", &magnet)?);
    write_stl(out.join("body-petg.stl"), &[&envelope])?;
    write_stl(out.join("insert-aero.stl"), &[&insert])?;
    std::fs::write(out.join("design.json"), design::json()?)?;
    Ok(())
}

/// The ring between two radii, standing from `bottom` to `top`.
fn annulus(outer: f64, inner: f64, bottom: f64, top: f64) -> Result<Solid> {
    let section = Profile::circle(v2(0., 0.), outer).with_hole(Loop::circle(v2(0., 0.), inner));
    Plane::XY.at(v3(0., 0., bottom)).extrude(&section, top - bottom)
}

/// The ring with both lower edges chamfered by the insertion lead, so the press fit starts on them.
fn led_annulus(outer: f64, inner: f64, bottom: f64, top: f64) -> Result<Solid> {
    let lead = float::INSERTION_LEAD;
    let section = Profile::polygon(&[
        v2(inner + lead, bottom),
        v2(outer - lead, bottom),
        v2(outer, bottom + lead),
        v2(outer, top),
        v2(inner, top),
        v2(inner, bottom + lead),
    ]);
    Plane::XZ.revolve(&section, 360., v2(0., 0.), v2(0., 1.))
}
