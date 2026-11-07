//! The fake countertop's files: the inverted-U bench stand in its show-face-down print frame,
//! the slab on the bed and the legs rising from it.
//!
//!     fake-countertop [<output directory>]
use anyhow::{Result, bail, ensure};
use hsm_fake_countertop_numbers as counter;
use hsm_kernel::part::write_part;
use hsm_kernel::*;
use std::path::PathBuf;

const NAME: &str = "fake-countertop";
const OUTPUT: &str = "hardware/printed-parts/fixtures/fake-countertop";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: fake-countertop [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let body = build()?;
    let bodies = [Body { name: NAME, color: Some(hsm_catalog::petgf_black()), solid: &body }];
    println!("{}", write_part(&out, NAME, &bodies)?);
    Ok(())
}

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

fn build() -> Result<Solid> {
    let x = counter::slab_x() / 2.;
    let y = counter::slab_y() / 2.;
    let inside = counter::CAVITY / 2.;
    let thickness = counter::THICKNESS;
    let height = counter::HEIGHT;
    let slab = cuboid(-x, x, -y, y, 0., thickness);
    let left = cuboid(-x, -inside, -y, y, thickness - 1., height);
    let right = cuboid(inside, x, -y, y, thickness - 1., height);
    let mut body = slab.union(&left)?.union(&right)?.simplified()?;
    let edges = selected(&body, "|Z", |p| {
        p.x.abs() > inside + 1. && p.y.abs() > y - 1.
    })?;
    body = body.fillet(&edges, counter::CORNER_RADIUS)?;
    let edges = selected(&body, "", |p| {
        (p.x.abs() - inside).abs() < 1e-6 && (p.z - thickness).abs() < 1e-6
    })?;
    body = body.fillet(&edges, counter::ROOT_RADIUS)?;
    let edges = selected(&body, "|Z", |p| {
        (p.x.abs() - inside).abs() < 1e-6 && p.y.abs() > y - 1.
    })?;
    body = body.fillet(&edges, counter::FOOT_RADIUS)?;
    body = body.fillet(&body.edges(">Z")?, counter::FOOT_RADIUS)?;
    let hole = Solid::cylinder(
        v3(0., 0., -1.),
        V3::Z,
        counter::HOLE_DIAMETER / 2.,
        thickness + 2.,
    )?;
    let body = body.cut(&hole)?;
    body.check()?;
    ensure!(
        body.components().len() == 1 && body.volume() > 0.,
        "fake countertop must be one valid positive-volume solid"
    );
    ensure!(
        height - thickness >= counter::UMBILICAL_BELOW_COUNTER + counter::UMBILICAL_BEND_RADIUS + counter::HAND_ROOM,
        "countertop under-slab clearance"
    );
    let probe = Solid::cylinder(
        v3(0., 0., -1.),
        V3::Z,
        counter::HOLE_DIAMETER / 2. - 0.05,
        thickness + 2.,
    )?;
    ensure!(
        body.shared_volume(&probe)? <= 1e-6,
        "the countertop hole is smaller than the shank standard"
    );
    let first = body
        .intersect(&cuboid(
            -counter::LEFT_REACH_X,
            counter::LEFT_REACH_X,
            -counter::LEFT_REACH_Y,
            counter::LEFT_REACH_Y,
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
