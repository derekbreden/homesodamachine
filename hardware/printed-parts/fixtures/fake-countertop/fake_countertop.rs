//! The current inverted-U countertop fixture in its show-face-down print frame.
use anyhow::{ensure, Result};
use hsm_kernel::part::{args, write_printed, Numbers};
use hsm_kernel::*;

fn cuboid(x0: f64, x1: f64, y0: f64, y1: f64, z0: f64, z1: f64) -> Solid {
    Plane::XY
        .at(v3((x0 + x1) / 2., (y0 + y1) / 2., (z0 + z1) / 2.))
        .cuboid(x1 - x0, y1 - y0, z1 - z0)
}

fn selected(s: &Solid, selector: &str, keep: impl Fn(V3) -> bool) -> Result<Edges> {
    Ok(Edges(
        s.edges(selector)?
            .iter()
            .filter(|e| keep(e.center))
            .cloned()
            .collect(),
    ))
}

fn build(n: &Numbers) -> Result<Solid> {
    let x = n.f("slab_x")? / 2.;
    let y = n.f("slab_y")? / 2.;
    let inside = n.f("cavity")? / 2.;
    let thickness = n.f("thickness")?;
    let height = n.f("height")?;
    let slab = cuboid(-x, x, -y, y, 0., thickness);
    let left = cuboid(-x, -inside, -y, y, thickness - 1., height);
    let right = cuboid(inside, x, -y, y, thickness - 1., height);
    let mut body = slab.union(&left)?.union(&right)?.simplified()?;
    let edges = selected(&body, "|Z", |p| {
        p.x.abs() > inside + 1. && p.y.abs() > y - 1.
    })?;
    body = body.fillet(&edges, n.f("corner_radius")?)?;
    let edges = selected(&body, "", |p| {
        (p.x.abs() - inside).abs() < 1e-6 && (p.z - thickness).abs() < 1e-6
    })?;
    body = body.fillet(&edges, n.f("root_radius")?)?;
    let edges = selected(&body, "|Z", |p| {
        (p.x.abs() - inside).abs() < 1e-6 && p.y.abs() > y - 1.
    })?;
    body = body.fillet(&edges, n.f("foot_radius")?)?;
    body = body.fillet(&body.edges(">Z")?, n.f("foot_radius")?)?;
    let hole = Solid::cylinder(
        v3(0., 0., -1.),
        V3::Z,
        n.f("hole_diameter")? / 2.,
        thickness + 2.,
    )?;
    let body = body.cut(&hole)?;
    body.check()?;
    ensure!(
        body.components().len() == 1 && body.volume() > 0.,
        "fake countertop must be one valid positive-volume solid"
    );
    ensure!(
        height - thickness >= n.f("umbilical_below")? + n.f("bend_radius")? + n.f("hand_room")?,
        "countertop under-slab clearance"
    );
    let probe = Solid::cylinder(
        v3(0., 0., -1.),
        V3::Z,
        n.f("hole_diameter")? / 2. - 0.05,
        thickness + 2.,
    )?;
    ensure!(
        body.shared_volume(&probe)? <= 1e-6,
        "the countertop hole is smaller than the shank standard"
    );
    let first = body
        .intersect(&cuboid(
            -n.f("reach_x")?,
            n.f("reach_x")?,
            -n.f("reach_y")?,
            n.f("reach_y")?,
            0.19,
            0.21,
        ))?
        .bounds();
    let bounds = body.bounds();
    ensure!(
        ((first.max.x - first.min.x) - (bounds.max.x - bounds.min.x)).abs() <= 1e-3
            && ((first.max.y - first.min.y) - (bounds.max.y - bounds.min.y)).abs() <= 1e-3,
        "the first layer must hold the whole countertop footprint"
    );
    Ok(body)
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let body = build(&n)?;
    println!(
        "{}",
        write_printed(
            &out,
            "fake-countertop",
            &[Body {
                name: "fake-countertop",
                color: Some(n.color("color")?),
                solid: &body,
            }]
        )?
    );
    Ok(())
}
