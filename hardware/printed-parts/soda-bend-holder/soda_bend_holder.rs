//! The soda bend holder's files: the D-backed teardrop holder round the soda tube's quarter turn,
//! on its flat back as it prints, from the inlet plan's holder figures.
//!
//!     soda-bend-holder [<output directory>]
use anyhow::{Context, Result, bail};
use hsm_kernel::part::write_part;
use hsm_kernel::{Body, Curve, Pen, Plane, Profile, Region, Solid, V3, v2, v3};
use hsm_soda_bend_holder_numbers::{Holder, MOUTH_STATIONS};
use serde::Deserialize;
use std::path::{Path, PathBuf};

const NAME: &str = "soda-bend-holder";
const OUTPUT: &str = "hardware/printed-parts/soda-bend-holder";
const DESIGN: &str = "hardware/manifold-layout/above-core.json";

#[derive(Deserialize)]
struct Inlet {
    holder: Holder,
}

#[derive(Deserialize)]
struct Design {
    soda_inlet: Inlet,
}

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: soda-bend-holder [<output directory>]");
    }
    hsm_kernel::reads::begin();
    let bytes = std::fs::read(DESIGN).context("the inlet plan's design")?;
    hsm_kernel::reads::read(Path::new(DESIGN), &bytes);
    let holder = serde_json::from_slice::<Design>(&bytes).context("the inlet plan's holder")?.soda_inlet.holder;
    std::fs::create_dir_all(&out)?;
    let solid = build(&holder)?;
    let bodies = [Body { name: NAME, color: Some(hsm_catalog::petgf_black()), solid: &solid }];
    println!("{}", write_part(&out, NAME, &bodies)?);
    Ok(())
}

fn sections(profile: &Profile, plane: &Plane) -> Region {
    // The torus has two curved directions. Quarter the profile's existing arc
    // spans so both directions fit the shared surface-error budget.
    let mut region = profile.place(plane);
    for ring in &mut region.loops {
        let (mut points, mut edges) = (Vec::new(), Vec::new());
        for i in 0..ring.pts.len() {
            let (a, b, edge) = (ring.pts[i], ring.pts[(i + 1) % ring.pts.len()], ring.seg[i]);
            points.push(a);
            edges.push(edge);
            if let Curve::Circle { c, axis, .. } = region.curves[edge as usize] {
                let (u, v, d) = (a - c, b - c, axis.unit());
                let turn = u.cross(v).dot(d).atan2(u.dot(v));
                for j in 1..4 {
                    let angle = turn * j as f64 / 4.0;
                    let (s, co) = angle.sin_cos();
                    points.push(c + u * co + d.cross(u) * s + d * (d.dot(u) * (1.0 - co)));
                    edges.push(edge);
                }
            }
        }
        ring.pts = points;
        ring.seg = edges;
    }
    region
}

fn teardrop(x: f64, z: f64, radius: f64) -> Result<Profile> {
    let k = radius / 2.0_f64.sqrt();
    Ok(Profile::new(Pen::new(v2(x + k, z + k))
        .line_to(v2(x, z + 2.0_f64.sqrt() * radius))
        .line_to(v2(x - k, z + k))
        .arc_center(v2(x, z), v2(x + k, z + k), true)
        .close()?))
}

fn build(h: &Holder) -> Result<Solid> {
    let bend = h.centreline_bend_r_mm;
    let outer = h.outer_radius();
    let z = h.stock_arc_z();
    let section = Profile::new(Pen::new(v2(bend - outer, 0.0))
        .line_to(v2(bend + outer, 0.0))
        .line_to(v2(bend + outer, z))
        .arc_center(v2(bend, z), v2(bend - outer, z), true)
        .close()?);
    let channel = teardrop(bend, h.channel_z(), h.channel_radius())?;
    let turn = h.turn_degrees;
    let ring = section.with_hole(channel.outer);
    let region = sections(&ring, &Plane::XZ);
    let arc = Solid::revolve(&region, V3::ZERO, V3::Z, turn)?;
    let [nx, ny, nz] = h.mirror_normal();
    let normal = v3(nx, ny, nz);
    let mouths = MOUTH_STATIONS.iter().zip(h.mouth_radii()).map(|(&y, radius)| {
        Ok(sections(&teardrop(bend, h.channel_z(), radius)?, &Plane::XZ.at(v3(0.0, y, 0.0))))
    }).collect::<Result<Vec<_>>>()?;
    let mut mouth = Solid::loft(&mouths)?;
    let leg = h.leg_mm;
    if leg > 0.0 {
        mouth = mouth.translate(v3(0.0, -leg, 0.0));
    }
    let mouths = [mouth.clone(), mouth.mirror(V3::ZERO, normal)];
    let entries = |mut solid: Solid| -> Result<Solid> {
        for tool in &mouths {
            let (a, b) = (solid.bounds(), tool.bounds());
            if (0..3).all(|k| a.min[k] < b.max[k] && b.min[k] < a.max[k]) {
                solid = solid.cut(tool)?;
            }
        }
        Ok(solid)
    };
    let mut pieces = vec![entries(arc)?];
    if leg > 0.0 {
        let straight = Solid::extrude(&region, Plane::XZ.z, Plane::XZ.z * leg)?;
        pieces.push(entries(straight.clone())?);
        pieces.push(entries(straight.mirror(V3::ZERO, normal))?);
    }
    Solid::union_all(&pieces)
}
