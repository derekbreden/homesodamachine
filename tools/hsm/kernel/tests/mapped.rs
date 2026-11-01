//! A solid sheared against CadQuery's `transformGeometry` of the same block (`mapped_reference.py`):
//! its volume within LINEAR × its surface area of OCCT's, its bounds within LINEAR, and every point
//! sampled across OCCT's faces within LINEAR of its triangles. A plane's record stays a plane with
//! its normal carried by the inverse transpose, a cylinder's becomes a free surface, and a
//! similarity keeps a cylinder a cylinder.
mod common;
use common::trimesh;
use hsm_geometry::parry::math::{Isometry, Point};
use hsm_geometry::parry::query::PointQuery;
use hsm_kernel::*;
use serde_json::Value;

fn block() -> Solid {
    let body = Solid::cuboid(v3(-10.0, -6.0, 0.0), v3(10.0, 6.0, 8.0));
    let hole = Solid::cylinder(v3(4.0, 0.0, -1.0), V3::Z, 3.0, 10.0).unwrap();
    let boss = Solid::cylinder(v3(-4.0, -6.0, 8.0), V3::Y, 2.5, 12.0).unwrap();
    body.cut(&hole).unwrap().union(&boss).unwrap()
}

fn shear(want: &Value) -> Affine {
    let rows = want["shear"].as_array().unwrap();
    let mut t = Affine::IDENTITY;
    for (i, row) in rows.iter().enumerate() {
        for (j, x) in row.as_array().unwrap().iter().enumerate() {
            t.m[i][j] = x.as_f64().unwrap();
        }
    }
    t
}

#[test]
fn a_shear_matches_occt() {
    let want: Value = serde_json::from_str(include_str!("mapped_reference.json")).unwrap();
    let t = shear(&want);
    let s = block().mapped(&t).unwrap();
    s.check().unwrap();
    let (volume, area) = (want["volume"].as_f64().unwrap(), want["area"].as_f64().unwrap());
    assert!((s.volume() - volume).abs() <= LINEAR * area, "volume {} against OCCT's {volume}", s.volume());
    let b = s.bounds();
    let got = [b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z];
    let bbox: Vec<f64> = want["bbox"].as_array().unwrap().iter().map(|x| x.as_f64().unwrap()).collect();
    for k in 0..6 {
        // OCCT pads its box by 1e-7.
        assert!((got[k] - bbox[k]).abs() <= LINEAR + 1e-6, "bounds {got:?} against OCCT's {bbox:?}");
    }
    let mesh = trimesh(s.verts(), s.tris());
    let mut far = 0.0f64;
    for p in want["samples"].as_array().unwrap() {
        let c: Vec<f64> = p.as_array().unwrap().iter().map(|x| x.as_f64().unwrap()).collect();
        let q = Point::new(c[0], c[1], c[2]);
        far = far.max((mesh.project_point(&Isometry::identity(), &q, false).point - q).norm());
    }
    println!("volume {:.6} against {volume:.6}, OCCT's faces within {far:.5}", s.volume());
    assert!(far <= LINEAR, "a point of OCCT's faces lies {far} off the sheared solid");

    let top = t.normal(V3::Z);
    let kinds: Vec<&str> = s.faces().iter().map(|f| f.surface.kind()).collect();
    assert!(!kinds.contains(&"CYLINDER"), "a sheared cylinder kept its record: {kinds:?}");
    assert!(kinds.contains(&"BSPLINE"));
    assert!(s.faces().iter().any(|f| matches!(f.surface, Surface::Plane { n, .. } if (n - top).norm() < 1e-12)));
    let tilted = s.faces().iter().filter(|f| matches!(f.surface, Surface::Plane { n, .. } if n.x.abs() > 0.9)).count();
    assert_eq!(tilted, 2, "the block's two ends, leaning with the shear");
}

#[test]
fn a_similarity_keeps_its_records() {
    let t = Affine::rotation(v3(1.0, 2.0, 3.0), v3(1.0, 1.0, 0.0), 30.0).then(&Affine::scale(2.0));
    let s = block().mapped(&t).unwrap();
    assert_eq!(s.faces(), block().transformed(&t).faces());
    assert!(s.faces().iter().any(|f| f.surface.kind() == "CYLINDER"));
}
