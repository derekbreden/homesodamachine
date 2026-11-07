//! The cradle's stock, its scanned-profile pocket and its wings, in the drain hole's frame.
use anyhow::Result;
use hsm_kernel::{Loop, Plane, Profile, Seg, Solid, V2, V3, v2, v3};
use hsm_zone_c_numbers::cradle::{Cradle, LOWER_SIDE_RELIEF, ROOT_STOCK};

fn points(rows: &[[f64; 2]]) -> Vec<V2> {
    rows.iter().map(|p| v2(p[0], p[1])).collect()
}

fn turned(rows: &[[f64; 2]], y: bool) -> Result<Solid> {
    let solid = Plane::XZ.revolve(&Profile::polygon(&points(rows)), 360.0, v2(0.0, 0.0), v2(0.0, 1.0))?;
    Ok(if y { solid.rotate(V3::ZERO, V3::X, -90.0) } else { solid })
}

fn upward(n: &Cradle) -> Result<Solid> {
    let [tx, ty] = n.mouth_tangent;
    let a = v2(-tx, ty);
    let b = v2(tx, ty);
    let edge = points(&n.mouth_chain);
    let mut segments = vec![Seg::Arc { a, b, c: V2::ZERO, ccw: true }];
    let mut at = b;
    for p in edge.iter().skip(1).copied().chain(edge.iter().skip(1).rev().map(|p| v2(-p.x, p.y))) {
        if at != p {
            segments.push(Seg::Line { a: at, b: p });
            at = p;
        }
    }
    if at != a {
        segments.push(Seg::Line { a: at, b: a });
    }
    let profile = Profile::new(Loop::new(segments)?);
    Plane::XY.at(v3(0.0, 0.0, n.mouth_lift)).extrude(&profile, n.shadow_height)
}

fn shadow(n: &Cradle) -> Result<Solid> {
    let rc = n.shadow_core_radius;
    let core = Solid::sphere(V3::ZERO, rc)?.union(&Solid::cylinder(V3::ZERO, V3::Z, rc, n.shadow_height)?)?;
    Ok(Solid::union_all(&[turned(&n.vertical_profile, false)?, turned(&n.horizontal_profile, true)?, upward(n)?, core])?
        .translate(v3(0.0, 0.0, n.elbow_z)))
}

/// The cradle in the drain hole's frame.
pub fn cradle(n: &Cradle) -> Result<Solid> {
    let [half, y0, y1, z0, z1] = n.block;
    let mut body = Solid::cuboid(v3(-half, y0, z0), v3(half, y1, z1)).cut(&shadow(n)?)?;
    let relief = LOWER_SIDE_RELIEF;
    let stock = ROOT_STOCK;
    for side in [-1.0, 1.0] {
        let p = [(half - relief, z0 - 1.0), (half + 2.0, z0 - 1.0), (half + 2.0, z1 - stock), (half, z1 - stock), (half - relief, z1 - stock - relief)]
            .map(|(x, z)| v2(side * x, z));
        let cut = Plane::XZ.at(v3(0.0, y0 - 1.0, 0.0)).extrude(&Profile::polygon(&p), -(y1 - y0 + 2.0))?;
        body = body.cut(&cut)?;
    }
    let [wi, wo] = n.wing_x;
    let (tip, face, top) = (n.hook_tip, n.hook_face, n.hook_top);
    for side in [-1.0, 1.0] {
        for (a, b, lo) in [(wi, wo, z1 - 0.01), (wo - 0.01, tip, face)] {
            let (x0, x1) = ((side * a).min(side * b), (side * a).max(side * b));
            body = body.union(&Solid::cuboid(v3(x0, y0, lo), v3(x1, y1, top)))?;
        }
    }
    Ok(body)
}
