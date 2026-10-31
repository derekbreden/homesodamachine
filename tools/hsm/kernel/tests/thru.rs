//! Lofts through sections against OCCT's for the same sections (`thru_reference.py`): the volume
//! within LINEAR × the surface area, the bounds within LINEAR, and every point sampled on OCCT's
//! side faces within LINEAR of the loft's triangles.
mod common;
use common::trimesh;
use hsm_geometry::parry::math::{Isometry, Point};
use hsm_geometry::parry::query::PointQuery;
use hsm_kernel::*;
use serde_json::Value;

fn reference() -> Value {
    serde_json::from_str(include_str!("thru_reference.json")).unwrap()
}

fn v(x: &Value) -> V3 {
    let a: Vec<f64> = x.as_array().unwrap().iter().map(|c| c.as_f64().unwrap()).collect();
    v3(a[0], a[1], a[2])
}

fn sections(case: &Value) -> Vec<LoftSection> {
    case["sections"]
        .as_array()
        .unwrap()
        .iter()
        .map(|s| {
            LoftSection::new(
                s.as_array()
                    .unwrap()
                    .iter()
                    .map(|e| {
                        if let Some(l) = e.get("line") {
                            LoftEdge::Line { a: v(&l[0]), b: v(&l[1]) }
                        } else {
                            let c = &e["conic"];
                            LoftEdge::Conic {
                                c: v(&c["c"]),
                                x: v(&c["x"]),
                                y: v(&c["y"]),
                                t0: c["t0"].as_f64().unwrap(),
                                t1: c["t1"].as_f64().unwrap(),
                            }
                        }
                    })
                    .collect(),
            )
        })
        .collect()
}

fn check(name: &str) {
    let all = reference();
    let case = &all[name];
    let s = Solid::thru_sections(&sections(case), case["ruled"].as_bool().unwrap()).unwrap_or_else(|e| panic!("{name}: {e}"));
    s.check().unwrap_or_else(|e| panic!("{name}: {e}"));
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
    let off = (0..6).map(|k| (got[k] - bbox[k]).abs()).fold(0.0, f64::max);
    println!(
        "{name:16} {:7} triangles  volume off OCCT's by {:+.2e}  OCCT's surface {far:.1e} off the triangles  bounds {off:.1e} off",
        s.tris().len(),
        (s.volume() - volume) / volume
    );
    assert!((s.volume() - volume).abs() <= LINEAR * area, "{name}: volume {} against OCCT's {volume}", s.volume());
    assert!(far <= LINEAR, "{name}: OCCT's surface lies {far:e} off the loft");
    assert!(off <= LINEAR + 1e-9, "{name}: bounds {got:?} against OCCT's {bbox:?}");
}

#[test]
fn ellipses() {
    check("ellipses3");
    check("ellipses12");
}

#[test]
fn cut_by_the_polar_method() {
    check("shell_like");
    check("counts_differ");
}

#[test]
fn rounded_outlines() {
    check("rounded3");
}

#[test]
fn ruled() {
    check("rect_slot_ruled");
}

#[test]
fn tilted_planes() {
    check("tilted");
}
