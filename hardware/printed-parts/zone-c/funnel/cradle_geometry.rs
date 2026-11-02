//! Cradle stock, scanned-profile pocket and the snap receiver, in the hole's frame.
use anyhow::{Context, Result, ensure};
use hsm_kernel::part::Numbers;
use hsm_kernel::{Loop, Plane, Profile, Seg, Solid, V2, V3, import, v2, v3};
use serde_json::{Value, json};

fn points(n: &Numbers, key: &str) -> Result<Vec<V2>> {
    n.get(key)?.as_array().context("a profile is a point list")?.iter()
        .map(|p| Ok(v2(p[0].as_f64().context("profile coordinate")?,
                      p[1].as_f64().context("profile coordinate")?))).collect()
}

fn turned(n: &Numbers, key: &str, y: bool) -> Result<Solid> {
    let solid = Plane::XZ.revolve(&Profile::polygon(&points(n, key)?), 360.0,
                                  v2(0.0, 0.0), v2(0.0, 1.0))?;
    Ok(if y { solid.rotate(V3::ZERO, V3::X, -90.0) } else { solid })
}

fn upward(n: &Numbers) -> Result<Solid> {
    let (tx, ty) = n.pair("mouth_tangent")?;
    let a = v2(-tx, ty);
    let b = v2(tx, ty);
    let edge = points(n, "mouth_chain")?;
    let mut segments = vec![Seg::Arc { a, b, c: V2::ZERO, ccw: true }];
    let mut at = b;
    for p in edge.iter().skip(1).copied()
        .chain(edge.iter().skip(1).rev().map(|p| v2(-p.x, p.y))) {
        if at != p { segments.push(Seg::Line { a: at, b: p }); at = p; }
    }
    if at != a { segments.push(Seg::Line { a: at, b: a }); }
    let profile = Profile::new(Loop::new(segments)?);
    Plane::XY.at(v3(0.0, 0.0, n.f("mouth_lift")?))
        .extrude(&profile, n.f("shadow_height")?)
}

fn shadow(n: &Numbers) -> Result<Solid> {
    let rc = n.f("shadow_core_radius")?;
    let core = Solid::sphere(V3::ZERO, rc)?.union(
        &Solid::cylinder(V3::ZERO, V3::Z, rc, n.f("shadow_height")?)?)?;
    Ok(Solid::union_all(&[turned(n, "vertical_profile", false)?,
        turned(n, "horizontal_profile", true)?, upward(n)?, core,
    ])?.translate(v3(0.0, 0.0, n.f("elbow_z")?)))
}

pub fn cradle(n: &Numbers) -> Result<Solid> {
    let b = n.list("block")?;
    let (half, y0, y1, z0, z1) = (b[0], b[1], b[2], b[3], b[4]);
    let mut body = Solid::cuboid(v3(-half,y0,z0),v3(half,y1,z1)).cut(&shadow(n)?)?;
    let relief = n.f("lower_side_relief")?;
    let stock = n.f("root_stock")?;
    for side in [-1.0, 1.0] {
        let p = [(half-relief,z0-1.0),(half+2.0,z0-1.0),
                 (half+2.0,z1-stock),(half,z1-stock),(half-relief,z1-stock-relief)]
            .map(|(x,z)| v2(side*x,z));
        let cut = Plane::XZ.at(v3(0.0,y0-1.0,0.0))
            .extrude(&Profile::polygon(&p), -(y1-y0+2.0))?;
        body = body.cut(&cut)?;
    }
    let (wi, wo) = n.pair("wing_x")?;
    let tip = n.f("hook_tip")?;
    let face = n.f("hook_face")?;
    let top = n.f("hook_top")?;
    for side in [-1.0, 1.0] {
        for (a,b,lo) in [(wi,wo,z1-0.01),(wo-0.01,tip,face)] {
            let (x0,x1) = ((side*a).min(side*b),(side*a).max(side*b));
            body = body.union(&Solid::cuboid(v3(x0,y0,lo),v3(x1,y1,top)))?;
        }
    }
    Ok(body)
}

pub fn receiver(n: &Numbers) -> Result<Solid> {
    let (x,y) = n.pair("receiver_half_size")?;
    let h = n.f("receiver_height")?;
    let (w,d) = n.pair("receiver_socket_size")?;
    let socket = Plane::XY.at(v3(0.0,0.0,n.f("web")?)).extrude(
        &Profile::new(Loop::rounded_rect(V2::ZERO,w,d,n.f("socket_radius")?)?),
        n.f("socket_depth")?)?;
    let mut tools = vec![socket, Solid::cylinder(v3(0.0,0.0,-1.0),V3::Z,
                                               n.f("hole_radius")?,n.f("web")?+2.0)?];
    let (sx0,sx1) = n.pair("slot_x")?;
    let (sy0,sy1) = n.pair("slot_y")?;
    for side in [-1.0,1.0] {
        tools.push(Solid::cuboid(v3((side*sx0).min(side*sx1),sy0,-1.0),
                                v3((side*sx0).max(side*sx1),sy1,n.f("web")?+1.0)));
    }
    Solid::cuboid(v3(-x,-y,0.0),v3(x,y,h)).cut_all(&tools)
}

fn elbow(n: &Numbers) -> Result<Solid> {
    let parts = import::payload(n.text("elbow_payload")?)?;
    let z = n.f("elbow_z")?;
    Ok(Solid::compose(&parts.into_iter().map(|part| part.solid
        .rotate(V3::ZERO,V3::Y,90.0).translate(v3(0.0,0.0,z)))
        .collect::<Vec<_>>()))
}

pub fn selftest(n: &Numbers, cradle: &Solid) -> Result<()> {
    let elbow = elbow(n)?;
    for k in 1..=60 {
        ensure!(elbow.translate(v3(0.0,0.0,0.5*k as f64)).shared_volume(cradle)? < 1e-3,
                "the elbow's upward path meets the cradle at step {k}");
    }
    let b = n.list("block")?;
    let (wi,wo) = n.pair("wing_x")?;
    for side in [-1.0,1.0] {
        let foot = Solid::cuboid(v3((side*wi).min(side*wo),b[1],b[4]-0.5),
                                v3((side*wi).max(side*wo),b[2],b[4]));
        ensure!((cradle.shared_volume(&foot)?-foot.volume()).abs()<1e-3,
                "the cradle wing stands on its body");
    }
    Ok(())
}

pub fn trial_facts(n: &Numbers, receiver: &Solid, cradle: &Solid) -> Result<Value> {
    use hsm_geometry::{payload::Mesh, queries};
    let measured = |name, solid: &Solid| Mesh::from_arrays(name,
        solid.verts().iter().map(|p| p.to_array()).collect(), solid.tris().to_vec());
    let elbow = elbow(n)?;
    let receiver_mesh = measured("receiver", receiver)?;
    let cradle_mesh = measured("cradle", cradle)?;
    let elbow_mesh = measured("elbow", &elbow)?;
    let home = queries::gap(&cradle_mesh, &receiver_mesh, [0.0; 3])?;
    let hanging = queries::gap(&cradle_mesh, &receiver_mesh, [0.0, 0.0, -n.f("catch_gap")?])?;
    let nose = queries::gap(&elbow_mesh, &receiver_mesh, [0.0; 3])?;
    let seat = queries::gap(&elbow_mesh, &cradle_mesh, [0.0; 3])?;
    let overlap = |gap: &queries::Gap| gap.intersection_volume_mm3.context("trial overlap requires a closed solid");
    let clearance = |gap: &queries::Gap| gap.clearance_mm.context("trial clearance requires a closed solid");
    let mut facts = n.get("trial_facts")?.clone();
    for (key,value) in [
        ("cradle_overlap_home_mm3",overlap(&home)?),
        ("cradle_gap_home_mm",clearance(&home)?),
        ("cradle_overlap_hanging_mm3",overlap(&hanging)?),
        ("cradle_gap_hanging_mm",clearance(&hanging)?),
        ("elbow_overlap_mm3",overlap(&nose)?+overlap(&seat)?),
        ("elbow_nose_gap_mm",clearance(&nose)?),
        ("elbow_seat_gap_mm",(clearance(&seat)?*1000.0).round_ties_even()/1000.0),
        ("receiver_volume_mm3",receiver.volume()),
        ("cradle_volume_mm3",cradle.volume()),
    ] { facts[key] = json!(value); }
    for value in facts.as_object_mut().unwrap().values_mut() {
        if let Some(number) = value.as_f64() {
            *value = json!((number*10000.0).round_ties_even()/10000.0);
        }
    }
    Ok(facts)
}
