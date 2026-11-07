//! The coil mandrel's files: a hollow ring the evaporator's copper is wound on, the helical
//! groove cut into it over the wind zone, and a plain handle ring at either end. The groove's
//! sweep overshoots the wind zone by its own radius at each end; the handle rings, fused back over
//! it, keep their walls whole.
//!
//!     coil-mandrel [<output directory>]
use anyhow::{Result, bail};
use hsm_coil_mandrel_numbers as mandrel;
use hsm_coil_numbers as coil;
use hsm_kernel::part::write_part;
use hsm_kernel::*;
use std::path::PathBuf;

const NAME: &str = "coil-mandrel";
const OUTPUT: &str = "hardware/printed-parts/cold-core/coil-mandrel";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: coil-mandrel [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let solid = build()?;
    let bodies = [Body { name: NAME, color: Some(mandrel::colour().linear), solid: &solid }];
    println!("{}", write_part(&out, NAME, &bodies)?);
    Ok(())
}

fn build() -> Result<Solid> {
    let [wind_bottom, wind_top] = mandrel::WIND_Z;
    Solid::union_all(&[
        ring(0., mandrel::LENGTH)?.cut(&groove()?)?,
        ring(0., wind_bottom)?,
        ring(wind_top, mandrel::LENGTH)?,
    ])
}

/// The ring between the mandrel's bore and its face, from `bottom` up to `top`.
fn ring(bottom: f64, top: f64) -> Result<Solid> {
    let section = Profile::circle(v2(0., 0.), mandrel::RADIUS)
        .with_hole(Loop::circle(v2(0., 0.), mandrel::INNER_RADIUS));
    Plane::XY.at(v3(0., 0., bottom)).extrude(&section, top - bottom)
}

/// The copper's section, standing in the X-Z plane at the wind zone's foot, carried up the
/// mandrel's helix in a rotation-minimizing frame.
fn groove() -> Result<Solid> {
    let start = v3(coil::MANDREL_WIND_RADIUS, 0., mandrel::WIND_Z[0]);
    let section = Profile::circle(v2(0., 0.), mandrel::GROOVE_PROFILE_RADIUS);
    Plane::new(start, V3::Z, V3::Y)?.helix_sweep(&section, V3::ZERO, V3::Z, coil::mandrel_pitch(), coil::mandrel_wraps())
}
