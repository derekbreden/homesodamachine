//! What the kernel's tests share: OCCT's reference values and the checks a solid answers to.
#![allow(dead_code)]
use hsm_geometry::parry::math::{Isometry, Point};
use hsm_geometry::parry::query::PointQuery;
use hsm_geometry::parry::shape::TriMesh;
use hsm_kernel::{LINEAR, Solid, Surface, V3};
use serde_json::Value;
use std::sync::OnceLock;

pub struct Ref {
    pub volume: f64,
    pub area: f64,
    pub bbox: [f64; 6],
}

pub fn occt(name: &str) -> Ref {
    static TABLE: OnceLock<Value> = OnceLock::new();
    let t = TABLE.get_or_init(|| {
        let text = include_str!("../occt_reference.json");
        serde_json::from_str(text).unwrap()
    });
    let e = &t[name];
    assert!(e.is_object(), "no OCCT reference for {name}");
    let bbox: Vec<f64> = e["bbox"].as_array().unwrap().iter().map(|x| x.as_f64().unwrap()).collect();
    Ref {
        volume: e["volume"].as_f64().unwrap(),
        area: e["area"].as_f64().unwrap(),
        bbox: bbox.try_into().unwrap(),
    }
}

/// The farthest any vertex of an analytic face lies from that face's surface. Every triangle of a
/// plane face faces the way its record's normal points.
pub fn off_surface(name: &str, s: &Solid) -> f64 {
    let mut worst = 0.0f64;
    for (t, tri) in s.tris().iter().enumerate() {
        let f = s.face_at(t);
        let p: Vec<V3> = tri.iter().map(|&i| s.verts()[i as usize]).collect();
        for q in &p {
            if let Some(d) = f.surface.distance(*q) {
                worst = worst.max(d.abs());
            }
        }
        if let Surface::Plane { n, .. } = f.surface {
            let tn = (p[1] - p[0]).cross(p[2] - p[0]);
            if tn.norm() > 1e-12 {
                assert!(tn.unit().dot(n) > 0.999, "{name}: a triangle of {f} faces away from its normal");
            }
        }
    }
    worst
}

/// The solid is closed, its vertices within `on_surface` of their records' surfaces, and its
/// volume and bounds OCCT's within the rule. Returns the volume's relative error and the
/// farthest vertex off its surface.
pub fn matches_occt(name: &str, s: &Solid, on_surface: f64) -> (f64, f64) {
    s.check().unwrap_or_else(|e| panic!("{name}: {e}"));
    let off = off_surface(name, s);
    assert!(off <= on_surface, "{name}: a vertex lies {off:e} off its face's surface");
    let r = occt(name);
    let v = s.volume();
    let tol = LINEAR * r.area;
    assert!(
        (v - r.volume).abs() <= tol,
        "{name}: volume {v:.6} against OCCT's {:.6}, more than LINEAR × area = {tol:.6} apart",
        r.volume
    );
    let b = s.bounds();
    let got = [b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z];
    for k in 0..6 {
        assert!(
            (got[k] - r.bbox[k]).abs() <= LINEAR + 1e-9,
            "{name}: bounds {got:?} against OCCT's {:?}",
            r.bbox
        );
    }
    ((v - r.volume) / r.volume, off)
}

pub fn trimesh(verts: &[V3], tris: &[[u32; 3]]) -> TriMesh {
    TriMesh::new(verts.iter().map(|p| Point::new(p.x, p.y, p.z)).collect(), tris.to_vec()).unwrap()
}

/// Points over a surface: its vertices, its triangles' centroids and its edges' midpoints.
pub fn samples(verts: &[V3], tris: &[[u32; 3]]) -> Vec<V3> {
    let mut out = verts.to_vec();
    for t in tris {
        let (a, b, c) = (verts[t[0] as usize], verts[t[1] as usize], verts[t[2] as usize]);
        out.push((a + b + c) / 3.0);
        out.push((a + b) * 0.5);
        out.push((b + c) * 0.5);
        out.push((c + a) * 0.5);
    }
    out
}

/// The largest distance from the samples of one surface to the other, both ways.
pub fn hausdorff(a: (&[V3], &[[u32; 3]]), b: (&[V3], &[[u32; 3]])) -> f64 {
    let one_way = |from: (&[V3], &[[u32; 3]]), to: (&[V3], &[[u32; 3]])| {
        let mesh = trimesh(to.0, to.1);
        samples(from.0, from.1)
            .iter()
            .map(|p| {
                let q = Point::new(p.x, p.y, p.z);
                let proj = mesh.project_point(&Isometry::identity(), &q, false);
                (proj.point - q).norm()
            })
            .fold(0.0, f64::max)
    };
    one_way(a, b).max(one_way(b, a))
}

/// A binary STL's triangles.
pub fn read_stl(bytes: &[u8]) -> (Vec<V3>, Vec<[u32; 3]>) {
    let n = u32::from_le_bytes(bytes[80..84].try_into().unwrap()) as usize;
    let mut verts = vec![];
    let mut tris = vec![];
    for i in 0..n {
        let rec = &bytes[84 + 50 * i..84 + 50 * (i + 1)];
        let f = |k: usize| f32::from_le_bytes(rec[4 * k..4 * k + 4].try_into().unwrap()) as f64;
        let base = verts.len() as u32;
        for v in 0..3 {
            verts.push(V3::from([f(3 + 3 * v), f(4 + 3 * v), f(5 + 3 * v)]));
        }
        tris.push([base, base + 1, base + 2]);
    }
    (verts, tris)
}
