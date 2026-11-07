//! The ASSE drain adapter's files: the TPU vent cup with its quarter turn and its two recessed tie
//! lands, tipped so both bores rise at 45° and stood on the flat cut across its corner.
//!
//!     asse-drain-adapter [<output directory>]
use anyhow::{Result, bail};
use hsm_asse_drain_adapter_numbers as adapter;
use hsm_kernel::part::write_part;
use hsm_kernel::{Body, Curve, Plane, Profile, Region, Solid, V2, V3, v2, v3};
use std::path::PathBuf;

const NAME: &str = "asse-drain-adapter";
const OUTPUT: &str = "hardware/printed-parts/asse-drain-adapter";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: asse-drain-adapter [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let solid = build()?;
    let bodies = [Body { name: NAME, color: Some(hsm_catalog::tpu_black()), solid: &solid }];
    println!("{}", write_part(&out, NAME, &bodies)?);
    Ok(())
}

/// The turn's circular section, each arc split in four so the swept passage follows the bend in
/// both directions.
fn circular_section(radius: f64, plane: &Plane) -> Region {
    let mut region = Profile::circle(V2::ZERO, radius).place(plane);
    for ring in &mut region.loops {
        let (mut points, mut edges) = (vec![], vec![]);
        for i in 0..ring.pts.len() {
            let (a, b, edge) = (ring.pts[i], ring.pts[(i + 1) % ring.pts.len()], ring.seg[i]);
            points.push(a);
            edges.push(edge);
            if let Curve::Circle { c, axis, .. } = region.curves[edge as usize] {
                let (u, v, d) = (a - c, b - c, axis.unit());
                let turn = u.cross(v).dot(d).atan2(u.dot(v));
                for j in 1..4 {
                    let (s, co) = (turn * j as f64 / 4.).sin_cos();
                    points.push(c + u * co + d.cross(u) * s + d * (d.dot(u) * (1. - co)));
                    edges.push(edge);
                }
            }
        }
        ring.pts = points;
        ring.seg = edges;
    }
    region
}

fn build() -> Result<Solid> {
    let (rb, rt) = (adapter::barb_od() / 2., adapter::tube_od() / 2.);
    let (drop, reach, elbow) = (adapter::socket_drop(), adapter::ELBOW_REACH, adapter::ELBOW_RADIUS);
    let start = adapter::turn_start_z();
    let (barb, tube) = (adapter::BARB_BORE / 2., adapter::TUBE_BORE / 2.);
    let reach_in = adapter::INSTALLED_REACH;

    let cup = Solid::cylinder(v3(0., 0., -drop - rt), V3::Z, rb, reach_in + drop + rt)?;
    let socket = Solid::cylinder(v3(0., 0., -drop), -V3::X, rt, reach)?;
    let section = circular_section(tube, &Plane::new(v3(0., 0., start), V3::X, -V3::Z)?);
    let turn = Solid::revolve(&section, v3(-elbow, 0., start), V3::Y, 90.)?;
    let bore = Solid::cylinder(v3(-elbow, 0., -drop), -V3::X, tube, reach - elbow + 0.1)?;
    let transition = Solid::cone(v3(0., 0., start), V3::Z, tube, barb, adapter::REDUCER_LENGTH)?;
    let inlet = Solid::cylinder(V3::ZERO, V3::Z, barb, reach_in + 0.1)?;
    let mut body = cup.union(&socket)?.cut(&inlet)?.cut(&transition)?.cut(&turn)?.cut(&bore)?;

    let (flat, ramp, depth) = (adapter::GROOVE_FLAT / 2., adapter::GROOVE_RAMP, adapter::GROOVE_DEPTH);
    for (i, (centre, radius)) in adapter::groove_centres().into_iter().zip([rb, rt]).enumerate() {
        let (lo, hi) = (centre - flat, centre + flat);
        let points = [
            v2(radius, lo - ramp),
            v2(radius - depth, lo),
            v2(radius - depth, hi),
            v2(radius, hi + ramp),
            v2(radius + 1., hi + ramp),
            v2(radius + 1., lo - ramp),
        ];
        let mut groove = Plane::XZ.revolve(&Profile::polygon(&points), 360., V2::ZERO, v2(0., 1.))?;
        if i == 1 {
            groove = groove.rotate(V3::ZERO, V3::Y, -90.).translate(v3(0., 0., -drop));
        }
        body = body.cut(&groove)?;
    }

    let flat_z = adapter::flat_z();
    let body = body
        .rotate(V3::ZERO, V3::Y, 45.)
        .cut(&Solid::cuboid(v3(-50., -50., flat_z - 1.), v3(50., 50., flat_z)))?;
    let [x, y, z] = adapter::print_shift();
    Ok(body.translate(v3(x, y, z)))
}
