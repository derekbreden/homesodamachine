//! The tube miter box's files: the block with its two open troughs and the razor slot across them,
//! upright as it prints.
//!
//!     tube-miter-box [<output directory>]
use anyhow::{Result, bail, ensure};
use hsm_kernel::part::write_part;
use hsm_kernel::{Body, Solid, V3, v3};
use hsm_tube_miter_box_numbers as miter;
use std::path::PathBuf;

const NAME: &str = "tube-miter-box";
const OUTPUT: &str = "hardware/printed-parts/fixtures/tube-miter-box";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: tube-miter-box [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let body = build()?;
    let bodies = [Body { name: NAME, color: Some(hsm_catalog::petgf_black()), solid: &body }];
    println!("{}", write_part(&out, NAME, &bodies)?);
    Ok(())
}

fn block(x0: f64, x1: f64, y0: f64, y1: f64, z0: f64, z1: f64) -> Solid {
    Solid::cuboid(v3(x0, y0, z0), v3(x1, y1, z1))
}

fn build() -> Result<Solid> {
    let size = miter::block();
    let [width, length, height] = size;
    let floor = miter::trough_floor();
    let mut cuts = vec![];
    for [x, radius] in miter::troughs() {
        let axis = floor + radius;
        cuts.push(Solid::cylinder(v3(x, -1., axis), V3::Y, radius, length + 2.)?);
        cuts.push(block(x - radius, x + radius, -1., length + 1., axis, height + 1.));
    }
    let [y0, y1] = miter::slot_y();
    let half_slot = miter::SLOT_L / 2.;
    cuts.push(block(-half_slot, half_slot, y0, y1, miter::FLOOR_UNDER_SLOT, height + 1.));
    let body = block(-width / 2., width / 2., 0., length, 0., height).cut_all(&cuts)?;
    body.check()?;
    ensure!(
        body.components().len() == 1 && body.volume() > 0.,
        "the tube miter box is one closed positive-volume body"
    );
    let [x0, x1, ry0, ry1, z0, z1] = miter::razor_bounds();
    ensure!(
        body.shared_volume(&block(x0, x1, ry0, ry1, z0, z1))? <= 1e-6,
        "the razor at the end of its stroke clears the block"
    );
    ensure!(floor > z0, "the razor's edge passes below the troughs' floor");
    Ok(body)
}
