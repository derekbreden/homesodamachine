//! Splines against OCCT's through the same points (`spline_reference.py`): the same parameter
//! range, and the point and direction at every sampled parameter; and a circle swept along a
//! path through one of them against OCCT's sweep, by its volume within LINEAR × the surface area
//! and every point sampled on OCCT's side faces within LINEAR of the tube's triangles.
mod common;
use common::trimesh;
use hsm_geometry::parry::math::{Isometry, Point};
use hsm_geometry::parry::query::PointQuery;
use hsm_kernel::*;
use serde_json::Value;

fn reference() -> Value {
    serde_json::from_str(include_str!("spline_reference.json")).unwrap()
}

fn v(x: &Value) -> V3 {
    let a: Vec<f64> = x.as_array().unwrap().iter().map(|c| c.as_f64().unwrap()).collect();
    v3(a[0], a[1], a[2])
}

fn points(case: &Value) -> Vec<V3> {
    case["points"].as_array().unwrap().iter().map(v).collect()
}

#[test]
fn curves_match_occt() {
    let all = reference();
    for name in ["eased", "bent", "four", "three", "two", "hermite"] {
        let case = &all[name];
        let pts = points(case);
        let s = match case.get("tangents") {
            Some(t) => Spline::hermite(pts[0], pts[1], v(&t[0]), v(&t[1])).unwrap(),
            None => Spline::through(&pts).unwrap(),
        };
        let (t0, t1) = s.range();
        let range = &case["range"];
        assert!((t0 - range[0].as_f64().unwrap()).abs() < 1e-12 && (t1 - range[1].as_f64().unwrap()).abs() < 1e-9, "{name}: range {t0}..{t1}");
        let (mut far, mut turned) = (0.0f64, 0.0f64);
        for sample in case["samples"].as_array().unwrap() {
            let t = sample["t"].as_f64().unwrap();
            far = far.max((s.point(t) - v(&sample["p"])).norm());
            turned = turned.max((s.derivative(t).unit() - v(&sample["d"])).norm());
        }
        println!("{name:8} points {far:.1e} off OCCT's, directions {turned:.1e}");
        assert!(far < 1e-9, "{name}: a point lies {far:e} off OCCT's");
        assert!(turned < 1e-9, "{name}: a direction turns {turned:e} off OCCT's");
    }
}

#[test]
fn a_tube_along_a_spline_matches_occt() {
    let all = reference();
    let pts = points(&all["eased"]);
    let (start, end) = (pts[0], pts[pts.len() - 1]);
    let path = Path::new(v3(start.x, start.y, 0.0))
        .line_to(start)
        .spline_through(&pts)
        .unwrap()
        .line_to(v3(end.x, end.y, 90.0));
    let tube = Plane::XY.sweep(&Profile::circle(v2(start.x, start.y), 2.0), &path).unwrap();
    tube.check().unwrap();
    let case = &all["swept"];
    let (volume, area) = (case["volume"].as_f64().unwrap(), case["area"].as_f64().unwrap());
    let mesh = trimesh(tube.verts(), tube.tris());
    let mut far = 0.0f64;
    for p in case["samples"].as_array().unwrap() {
        let p = v(p);
        let q = Point::new(p.x, p.y, p.z);
        far = far.max((mesh.project_point(&Isometry::identity(), &q, false).point - q).norm());
    }
    let free = tube.faces().iter().filter(|f| matches!(f.surface, Surface::Free { .. })).count();
    println!("tube {:7} triangles  volume off OCCT's by {:+.2e}  OCCT's surface {far:.1e} off the triangles", tube.tris().len(), (tube.volume() - volume) / volume);
    assert!((tube.volume() - volume).abs() <= LINEAR * area, "volume {} against OCCT's {volume}", tube.volume());
    assert!(far <= LINEAR, "OCCT's surface lies {far:e} off the tube");
    assert_eq!(free, 1, "the curve's wall is one free surface");
}
