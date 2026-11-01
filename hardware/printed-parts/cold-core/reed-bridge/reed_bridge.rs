//! The carbonator reed bridge and its rim-hung setting gauge.
//! `reed_bridge.py` owns the dimensions, native profiles and cutter extents.
use anyhow::{ensure, Context, Result};
use hsm_kernel::part::{args, write_part, Numbers};
use hsm_kernel::*;
use serde_json::Value;

fn polygon(n: &Numbers, name: &str) -> Result<Profile> {
    let points = n
        .get(name)?
        .as_array()
        .with_context(|| format!("{name} is a point list"))?
        .iter()
        .map(|p| -> Result<V2> {
            Ok(v2(
                p[0].as_f64().context("profile x is a number")?,
                p[1].as_f64().context("profile y is a number")?,
            ))
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(Profile::polygon(&points))
}

fn cuboid(ranges: &Value) -> Result<Solid> {
    let value = |axis: usize, end: usize| {
        ranges[axis][end]
            .as_f64()
            .context("a box has three numeric ranges")
    };
    Ok(Solid::cuboid(
        v3(value(0, 0)?, value(1, 0)?, value(2, 0)?),
        v3(value(0, 1)?, value(1, 1)?, value(2, 1)?),
    ))
}

fn build(n: &Numbers) -> Result<(Solid, Solid)> {
    let ridge = Plane::XZ.revolve(
        &polygon(n, "ridge_section")?,
        360.0,
        v2(0.0, 0.0),
        v2(0.0, 1.0),
    )?;
    let plan = Plane::XY
        .at(v3(0.0, 0.0, n.f("plan_bottom")?))
        .extrude(&polygon(n, "plan_outline")?, n.f("plan_height")?)?;
    let mut bridge = ridge.intersect(&plan)?;
    let pockets = n
        .get("pockets")?
        .as_array()
        .context("pockets is a box list")?;
    let notches = n
        .get("notches")?
        .as_array()
        .context("notches is a box list")?;
    for (i, pocket) in pockets.iter().enumerate() {
        bridge = bridge.cut(&cuboid(pocket)?)?;
        bridge = bridge.cut(&cuboid(&notches[2 * i])?)?;
        bridge = bridge.cut(&cuboid(&notches[2 * i + 1])?)?;
    }
    bridge = bridge.cut(&cuboid(n.get("lead_groove")?)?)?;
    let gauge = Plane::XZ.revolve(
        &polygon(n, "gauge_section")?,
        n.f("gauge_arc_degrees")?,
        v2(0.0, 0.0),
        v2(0.0, 1.0),
    )?;
    for (name, solid) in [
        ("reed-bridge", &bridge),
        ("reed-bridge-setting-gauge", &gauge),
    ] {
        ensure!(
            solid.components().len() == 1,
            "{name} is one connected body"
        );
    }
    Ok((bridge, gauge))
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let (bridge, gauge) = build(&n)?;
    let color = Some(n.color("color")?);
    for (name, solid) in [
        ("reed-bridge", &bridge),
        ("reed-bridge-setting-gauge", &gauge),
    ] {
        println!(
            "{}",
            write_part(&out, name, &[Body { name, color, solid }])?
        );
    }
    Ok(())
}
