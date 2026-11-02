//! Authored TPU vent cup and its two recessed tie lands.
use anyhow::Result;
use hsm_kernel::part::{args, write_part, Numbers};
use hsm_kernel::{v2, v3, Body, Curve, Plane, Profile, Region, Solid, V2, V3};

fn circular_section(radius: f64, plane: &Plane) -> Region {
    // The turn curves in both directions; subdivide only its circular section.
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

fn build(n: &Numbers) -> Result<Solid> {
    let (rb, rt) = (n.f("barb_radius")?, n.f("tube_radius")?);
    let drop = n.f("socket_drop")?;
    let reach = n.f("elbow_reach")?;
    let elbow = n.f("elbow_radius")?;
    let start = n.f("turn_start_z")?;
    let barb = n.f("barb_bore")? / 2.;
    let tube = n.f("tube_bore")? / 2.;
    let cup = Solid::cylinder(v3(0., 0., -drop - rt), V3::Z, rb,
        n.f("installed_reach")? + drop + rt)?;
    let socket = Solid::cylinder(v3(0., 0., -drop), -V3::X, rt, reach)?;
    let mut body = cup.union(&socket)?;
    let section = circular_section(tube, &Plane::new(v3(0., 0., start), V3::X, -V3::Z)?);
    let turn = Solid::revolve(&section, v3(-elbow, 0., start), V3::Y, 90.)?;
    let bore = Solid::cylinder(v3(-elbow, 0., -drop), -V3::X, tube, reach - elbow + 0.1)?;
    let transition = Solid::cone(v3(0., 0., start), V3::Z, tube, barb, n.f("reducer_length")?)?;
    let inlet = Solid::cylinder(V3::ZERO, V3::Z, barb, n.f("installed_reach")? + 0.1)?;
    body = body.cut(&inlet)?.cut(&transition)?.cut(&turn)?.cut(&bore)?;
    let centres = n.list("groove_centres")?;
    let flat = n.f("groove_flat")? / 2.;
    let ramp = n.f("groove_ramp")?;
    let depth = n.f("groove_depth")?;
    for (i, radius) in [rb, rt].into_iter().enumerate() {
        let (lo, hi) = (centres[i] - flat, centres[i] + flat);
        let points = [v2(radius, lo - ramp), v2(radius - depth, lo),
            v2(radius - depth, hi), v2(radius, hi + ramp),
            v2(radius + 1., hi + ramp), v2(radius + 1., lo - ramp)];
        let mut groove = Plane::XZ.revolve(&Profile::polygon(&points), 360., V2::ZERO, v2(0., 1.))?;
        if i == 1 {
            groove = groove.rotate(V3::ZERO, V3::Y, -90.).translate(v3(0., 0., -drop));
        }
        body = body.cut(&groove)?;
    }
    let body = body.rotate(V3::ZERO, V3::Y, 45.);
    let flat = n.f("flat_z")?;
    let body = body.cut(&Solid::cuboid(v3(-50., -50., flat - 1.), v3(50., 50., flat)))?;
    let shift = n.list("print_shift")?;
    Ok(body.translate(v3(shift[0], shift[1], shift[2])))
}

fn main() -> Result<()> {
    let (numbers, output) = args()?;
    let solid = build(&numbers)?;
    println!("{}", write_part(&output, "asse-drain-adapter", &[Body {
        name: "asse-drain-adapter", color: Some(numbers.color("color")?), solid: &solid,
    }])?);
    Ok(())
}
