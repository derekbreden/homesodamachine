//! The PRV cup and its radial supported vent. Python holds the dimensions.
use anyhow::{ensure, Result};
use hsm_kernel::part::{args, write_part, Numbers};
use hsm_kernel::*;

fn build(n: &Numbers) -> Result<Solid> {
    let outer = Plane::XY.cylinder(n.f("outer_radius")?, n.f("total_length")?)?;
    let cavity = Plane::XY.at(v3(0.0, 0.0, -n.f("overcut")?)).cylinder(
        n.f("inner_radius")?,
        n.f("cavity_length")? + n.f("overcut")?,
    )?;
    let vent = Plane::XZ
        .at(v3(0.0, 0.0, n.f("vent_station_z")?))
        .cylinder(n.f("vent_radius")?, n.f("outer_radius")? + n.f("overcut")?)?;
    let vent = vent.union(&vent.translate(v3(0.0, 0.0, -n.f("supported_surface")?)))?;
    let shroud = outer.cut(&cavity)?.cut(&vent)?;
    ensure!(
        shroud.components().len() == 1,
        "prv-shroud is one connected body"
    );
    Ok(shroud)
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let shroud = build(&n)?;
    println!(
        "{}",
        write_part(
            &out,
            "prv-shroud",
            &[Body {
                name: "prv-shroud",
                color: Some(n.color("color")?),
                solid: &shroud
            },]
        )?
    );
    Ok(())
}
