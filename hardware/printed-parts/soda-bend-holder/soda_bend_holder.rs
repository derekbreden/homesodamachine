//! The accepted D-backed soda bend holder, in its original flat-back print frame.
use anyhow::Result;
use hsm_kernel::part::{args, write_part, Numbers};
use hsm_kernel::{v2, v3, Body, Curve, Pen, Plane, Profile, Region, Solid, V3};

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

fn build(n: &Numbers) -> Result<Solid> {
    let bend = n.f("bend_radius")?;
    let outer = n.f("outer_radius")?;
    let z = n.f("stock_arc_z")?;
    let section = Profile::new(Pen::new(v2(bend - outer, 0.0))
        .line_to(v2(bend + outer, 0.0))
        .line_to(v2(bend + outer, z))
        .arc_center(v2(bend, z), v2(bend - outer, z), true)
        .close()?);
    let channel = teardrop(bend, n.f("channel_z")?, n.f("channel_radius")?)?;
    let turn = n.f("turn_degrees")?;
    let ring = section.with_hole(channel.outer);
    let region = sections(&ring, &Plane::XZ);
    let arc = Solid::revolve(&region, V3::ZERO, V3::Z, turn)?;
    let normal = n.list("mirror_normal")?;
    let normal = v3(normal[0], normal[1], normal[2]);
    let y = n.list("mouth_y")?;
    let radii = n.list("mouth_radii")?;
    let mouths = y.iter().zip(radii).map(|(&y, radius)| {
        Ok(sections(&teardrop(bend, n.f("channel_z")?, radius)?, &Plane::XZ.at(v3(0.0, y, 0.0))))
    }).collect::<Result<Vec<_>>>()?;
    let mut mouth = Solid::loft(&mouths)?;
    let leg = n.f("leg")?;
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

fn main() -> Result<()> {
    let (numbers, out) = args()?;
    let solid = build(&numbers)?;
    let name = "soda-bend-holder";
    println!("{}", write_part(&out, name, &[Body {
        name, color: Some(numbers.color("color")?), solid: &solid,
    }])?);
    Ok(())
}
