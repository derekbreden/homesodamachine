//! Rounds and chamfers against OCCT's for the same models (`round_reference.py`): the volume
//! within LINEAR × the surface area, the area within 0.1%, the bounds within LINEAR, every vertex
//! within twice LINEAR of its face's surface, and every point of OCCT's mesh of the result within
//! LINEAR of the kernel's triangles. Among the models are a round beside a fin 0.3 mm away, fills
//! in corners of 1 mm and 0.8 mm walls, and rounds and chamfers along the edges a round made.
mod common;
use anyhow::Result;
use common::{off_surface, trimesh};
use hsm_geometry::parry::math::{Isometry, Point};
use hsm_geometry::parry::query::PointQuery;
use hsm_kernel::*;
use serde_json::Value;
use std::sync::OnceLock;

fn reference() -> &'static Value {
    static TABLE: OnceLock<Value> = OnceLock::new();
    TABLE.get_or_init(|| serde_json::from_str(include_str!("round_reference.json")).unwrap())
}

fn v(x: &Value) -> V3 {
    let a: Vec<f64> = x.as_array().unwrap().iter().map(|c| c.as_f64().unwrap()).collect();
    v3(a[0], a[1], a[2])
}

fn check(name: &str, s: Solid) {
    let case = &reference()[name];
    assert!(case.is_object(), "no OCCT reference for {name}");
    s.check().unwrap_or_else(|e| panic!("{name}: {e}"));
    let off = off_surface(name, &s);
    let (volume, area) = (case["volume"].as_f64().unwrap(), case["area"].as_f64().unwrap());
    let mesh = trimesh(s.verts(), s.tris());
    let mut far = 0.0f64;
    for p in case["samples"].as_array().unwrap() {
        let p = v(p);
        let q = Point::new(p.x, p.y, p.z);
        far = far.max((mesh.project_point(&Isometry::identity(), &q, false).point - q).norm());
    }
    let b = s.bounds();
    let got = [b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z];
    let bbox: Vec<f64> = case["bbox"].as_array().unwrap().iter().map(|x| x.as_f64().unwrap()).collect();
    let bounds = (0..6).map(|k| (got[k] - bbox[k]).abs()).fold(0.0, f64::max);
    println!(
        "{name:22} {:6} triangles  volume off OCCT's by {:+.2e}  area by {:+.2e}  OCCT's surface {far:.1e} off  vertices {off:.1e} off their surfaces  bounds {bounds:.1e} off",
        s.tris().len(),
        (s.volume() - volume) / volume,
        (s.area() - area) / area,
    );
    assert!((s.volume() - volume).abs() <= LINEAR * area, "{name}: volume {} against OCCT's {volume}", s.volume());
    assert!((s.area() - area).abs() <= 1e-3 * area, "{name}: area {} against OCCT's {area}", s.area());
    assert!(far <= LINEAR, "{name}: OCCT's surface lies {far:e} off the kernel's");
    assert!(off <= 2.0 * LINEAR, "{name}: a vertex lies {off:e} off its face's surface");
    assert!(bounds <= LINEAR + 1e-9, "{name}: bounds {got:?} against OCCT's {bbox:?}");
}

#[test]
fn box_edges() -> Result<()> {
    let b = Plane::XY.cuboid(20.0, 20.0, 10.0);
    check("box_vertical", b.fillet(&b.edges("|Z")?, 3.0)?);
    check("top_edges_round", b.fillet(&b.edges(">Z")?, 2.0)?);
    check("top_edges_chamfer", b.chamfer(&b.edges(">Z")?, 2.0)?);
    let c = Plane::XY.cuboid(30.0, 20.0, 10.0);
    check("z_and_max_y", c.fillet(&c.edges("|Z and >Y")?, 4.0)?);
    let r = Plane::XY.cuboid(20.0, 10.0, 8.0).rotate(V3::ZERO, V3::Z, 30.0);
    check("rotated_box", r.fillet(&r.edges("|Z")?, 2.0)?);
    Ok(())
}

/// Review finding 3: a round after a round takes the edges the first one made.
#[test]
fn rounds_after_rounds() -> Result<()> {
    let b = Plane::XY.cuboid(20.0, 20.0, 10.0);
    let r = b.fillet(&b.edges("|Z")?, 3.0)?;
    check("vert_then_top", r.fillet(&r.edges(">Z")?, 1.0)?);
    check("vert_then_top_chamfer", r.chamfer(&r.face_edges(">Z")?, 1.0)?);
    let c = b.fillet(&b.edges("|Z and >X and >Y")?, 5.0)?;
    check("corner_then_top", c.fillet(&c.edges(">Z")?, 1.0)?);
    Ok(())
}

/// Review finding 1: a fin 0.3 mm from the rounded face is left whole.
#[test]
fn a_fin_beside_a_round() -> Result<()> {
    let base = Plane::XY.at(v3(4.15, 0.0, -1.0)).cuboid(8.3, 10.0, 2.0);
    let wall = Plane::XY.at(v3(3.0, 0.0, 5.0)).cuboid(6.0, 10.0, 10.0);
    let fin = Plane::XY.at(v3(7.3, 0.0, 5.0)).cuboid(2.0, 10.0, 10.0);
    let s = base.union(&wall)?.union(&fin)?;
    check("slot_beside_round", s.fillet(&s.edges("|Y")?.nearest(v3(6.0, 0.0, 10.0))?, 4.0)?);
    Ok(())
}

/// Review finding 2: a fill stays inside walls of 1 mm and 0.8 mm.
#[test]
fn fills_in_thin_walls() -> Result<()> {
    let pts = [v2(-1.0, -1.0), v2(20.0, -1.0), v2(20.0, 0.0), v2(0.0, 0.0), v2(0.0, 20.0), v2(-1.0, 20.0)];
    let l = Plane::YZ.extrude(&Profile::polygon(&pts), 10.0)?;
    check("thin_l_inside", l.fillet(&l.edges("|X")?.nearest(v3(5.0, 0.0, 0.0))?, 5.0)?);
    let plate = Plane::XY.cuboid(30.0, 30.0, 0.8);
    let s = plate.union(&Solid::cylinder(v3(0.0, 0.0, 0.4), V3::Z, 5.0, 6.0)?)?;
    check("thin_plate_boss_root", s.fillet(&s.edges("")?.nearest(v3(0.0, 0.0, 0.4))?, 4.0)?);
    Ok(())
}

#[test]
fn circles() -> Result<()> {
    let c = Solid::cylinder(V3::ZERO, V3::Z, 5.0, 10.0)?;
    check("cylinder_top_round", c.fillet(&c.face_edges(">Z")?, 1.0)?);
    let c = Solid::cylinder(V3::ZERO, V3::Z, 10.0, 5.0)?;
    check("cylinder_top_chamfer", c.chamfer(&c.edges(">Z")?, 1.0)?);
    let b = Plane::XY.cuboid(20.0, 20.0, 10.0).cut(&Solid::cylinder(v3(0.0, 0.0, -6.0), V3::Z, 3.0, 12.0)?)?;
    check("hole_top_round", b.fillet(&b.face_edges(">Z")?.select("%CIRCLE")?, 1.0)?);
    let ring = Plane::XZ.revolve(&Profile::rect(v2(12.0, 1.5), 4.0, 3.0), 90.0, v2(0.0, 0.0), v2(0.0, 1.0))?;
    check("quarter_ring_round", ring.fillet(&ring.edges("%CIRCLE and >Z")?.nearest(v3(10.0, 10.0, 3.0))?, 1.0)?);
    Ok(())
}

#[test]
fn slants_and_slots() -> Result<()> {
    let pts = [v2(0.0, 0.0), v2(20.0, 0.0), v2(14.0, 10.0), v2(0.0, 10.0)];
    let slant = Plane::XZ.extrude(&Profile::polygon(&pts), -10.0)?;
    check("slanted_round", slant.fillet(&slant.edges("|Y")?.select(">Z")?.select(">X")?, 2.0)?);
    let slot = Plane::XY.extrude(&Profile::new(Loop::slot(V2::ZERO, 16.0, 6.0, 0.0)), 5.0)?;
    let b = Plane::XY.cuboid(30.0, 20.0, 8.0).cut(&slot)?;
    check("slot_top_round", b.fillet(&b.face_edges(">Z")?.select("not(<X or >X or <Y or >Y)")?, 1.0)?);
    Ok(())
}
