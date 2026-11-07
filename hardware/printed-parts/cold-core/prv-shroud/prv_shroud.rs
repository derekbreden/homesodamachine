//! The PRV shroud's files: the PETG cup that keeps the foam off the pressure-relief valve, with
//! the radial vent socket the valve's vent line leaves through, bored through the barrel's −Y
//! wall and opened by the supported-surface allowance at its print-up crown.
//!
//!     prv-shroud [<output directory>]
use anyhow::{Result, bail, ensure};
use hsm_cold_core_catalog as catalog;
use hsm_kernel::part::write_part;
use hsm_kernel::*;
use hsm_prv_shroud_numbers as shroud;
use std::path::PathBuf;

const NAME: &str = "prv-shroud";
const OUTPUT: &str = "hardware/printed-parts/cold-core/prv-shroud";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: prv-shroud [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let cup = build()?;
    let bodies = [Body { name: NAME, color: Some(shroud::colour().linear), solid: &cup }];
    println!("{}", write_part(&out, NAME, &bodies)?);
    Ok(())
}

fn build() -> Result<Solid> {
    let outer_radius = shroud::outer_diameter() / 2.;
    let overcut = shroud::OVERCUT;
    let barrel = Plane::XY.cylinder(outer_radius, shroud::TOTAL_LENGTH)?;
    let cavity = Plane::XY
        .at(v3(0., 0., -overcut))
        .cylinder(shroud::inner_diameter() / 2., shroud::CAVITY_LENGTH + overcut)?;
    let vent = Plane::XZ
        .at(v3(0., 0., shroud::VENT_STATION_Z))
        .cylinder(shroud::vent_hole_diameter() / 2., outer_radius + overcut)?;
    let vent = vent.union(&vent.translate(v3(0., 0., -catalog::fits().supported_surface)))?;
    let cup = barrel.cut(&cavity)?.cut(&vent)?;
    ensure!(cup.components().len() == 1, "the shroud is one connected body");
    Ok(cup)
}
