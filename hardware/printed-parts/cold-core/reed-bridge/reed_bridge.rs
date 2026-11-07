//! The reed bridge's files, and its setting gauge's. The bridge is the ring round the tube from
//! its bore to its plateau, ramped down to the skirt at each end and trimmed to its plan, which
//! ramps down to the skirt at each side; each reed's pocket goes clear through it to the wall, a
//! cross-notch at either end of the pocket brings the reed's leads into the lead groove beside
//! them, and the groove runs out the top. The gauge is a band of the tube's rim that hooks under
//! it, its top face at the bridge's bottom edge.
//!
//!     reed-bridge [<output directory>]
use anyhow::{Result, bail, ensure};
use hsm_kernel::part::write_part;
use hsm_kernel::*;
use hsm_reed_bridge_numbers as bridge;
use std::path::PathBuf;

const OUTPUT: &str = "hardware/printed-parts/cold-core/reed-bridge";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: reed-bridge [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let color = Some(bridge::colour().linear);
    for (name, solid) in [("reed-bridge", reed_bridge()?), ("reed-bridge-setting-gauge", gauge()?)] {
        ensure!(solid.components().len() == 1, "{name} is one connected body");
        println!("{}", write_part(&out, name, &[Body { name, color, solid: &solid }])?);
    }
    Ok(())
}

fn reed_bridge() -> Result<Solid> {
    let (inner, skirt, plateau) = (bridge::inner_radius(), bridge::skirt_radius(), bridge::plateau_radius());
    let (bottom, top) = (bridge::bridge_z_bottom(), bridge::bridge_z_top());
    let (plateau_bottom, plateau_top) = (bridge::plateau_z_bottom(), bridge::plateau_z_top());
    let overcut = bridge::OVERCUT;
    let section = Profile::polygon(&[
        v2(inner, bottom),
        v2(skirt, bottom),
        v2(plateau, plateau_bottom),
        v2(plateau, plateau_top),
        v2(skirt, top),
        v2(inner, top),
    ]);
    let ring = Plane::XZ.revolve(&section, 360., v2(0., 0.), v2(0., 1.))?;
    let half = bridge::bridge_half_angle();
    let segments = f64::from(bridge::PLAN_SEGMENTS);
    let mut outline = vec![v2(0., 0.)];
    for i in 0..=bridge::PLAN_SEGMENTS {
        let angle = -half + 2. * half * f64::from(i) / segments;
        let radius = bridge::plan_radius(angle);
        outline.push(v2(radius * angle.cos(), radius * angle.sin()));
    }
    let plan = Plane::XY
        .at(v3(0., 0., bottom - overcut))
        .extrude(&Profile::polygon(&outline), top - bottom + 2. * overcut)?;
    let mut part = ring.intersect(&plan)?;
    let (length, half_width) = (bridge::pocket_length(), bridge::pocket_width() / 2.);
    let groove = (bridge::LEAD_GROOVE_Y - bridge::LEAD_GROOVE_WIDTH / 2., bridge::LEAD_GROOVE_Y + bridge::LEAD_GROOVE_WIDTH / 2.);
    let notch = bridge::LEAD_NOTCH_LENGTH;
    for reed in [bridge::reed_low_z(), bridge::reed_high_z()] {
        let (low, high) = (reed - length / 2., reed + length / 2.);
        part = part.cut(&Solid::cuboid(
            v3(inner - overcut, -half_width, low),
            v3(plateau + overcut, half_width, high),
        ))?;
        for z in [low, high - notch] {
            part = part.cut(&Solid::cuboid(
                v3(skirt, -half_width, z),
                v3(plateau + overcut, groove.1, z + notch),
            ))?;
        }
    }
    part.cut(&Solid::cuboid(
        v3(skirt, groove.0, plateau_bottom),
        v3(plateau + overcut, groove.1, top + overcut),
    ))
}

fn gauge() -> Result<Solid> {
    let inner = bridge::inner_radius();
    let (hook, height, wall) = (bridge::GAUGE_HOOK_DEPTH, bridge::GAUGE_HOOK_HEIGHT, bridge::GAUGE_WALL);
    let top = bridge::bridge_z_bottom();
    let section = Profile::polygon(&[
        v2(inner - hook, -height),
        v2(inner + wall, -height),
        v2(inner + wall, top),
        v2(inner, top),
        v2(inner, 0.),
        v2(inner - hook, 0.),
    ]);
    Plane::XZ.revolve(&section, bridge::GAUGE_ARC_DEGREES, v2(0., 0.), v2(0., 1.))
}
