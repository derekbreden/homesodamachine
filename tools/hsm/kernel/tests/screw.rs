//! Helix sweeps against OCCT's sweeps of the same profiles along the same helices
//! (`screw_reference.py`): the mesh volume OCCT's within LINEAR × the surface area, the bounds
//! within LINEAR, every vertex of a cylinder or plane record on that surface, and every end
//! facing the way OCCT's does.
//!
//! A screw is OCCT's sweep in the Frenet frame, exactly. A helix sweep is its corrected Frenet
//! sweep, whose frame OCCT fits to the rotation-minimizing one: over the coil mandrel's nine
//! and a half turns the two part by 0.002 rad, 0.006 mm across the groove's end.
mod common;
use common::off_surface;
use hsm_kernel::*;
use serde_json::Value;

const Z: V3 = V3::Z;

struct Reference {
    volume: f64,
    area: f64,
    bbox: [f64; 6],
    planes: Vec<V3>,
}

fn reference(name: &str) -> Reference {
    let t: Value = serde_json::from_str(include_str!("screw_reference.json")).unwrap();
    let e = &t[name];
    assert!(e.is_object(), "no OCCT reference for {name}");
    let nums = |v: &Value| -> Vec<f64> { v.as_array().unwrap().iter().map(|x| x.as_f64().unwrap()).collect() };
    Reference {
        volume: e["volume"].as_f64().unwrap(),
        area: e["area"].as_f64().unwrap(),
        bbox: nums(&e["bbox"]).try_into().unwrap(),
        planes: e["plane_normals"].as_array().unwrap().iter().map(|n| V3::from(<[f64; 3]>::try_from(nums(n)).unwrap())).collect(),
    }
}

fn matches(name: &str, s: &Solid, on_surface: f64, turned: f64) {
    s.check().unwrap_or_else(|e| panic!("{name}: {e}"));
    let off = off_surface(name, s);
    assert!(off <= on_surface, "{name}: a vertex lies {off:e} off its face's surface");
    let r = reference(name);
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
        assert!((got[k] - r.bbox[k]).abs() <= LINEAR + 1e-6, "{name}: bounds {got:?} against OCCT's {:?}", r.bbox);
    }
    let mine: Vec<V3> = s
        .faces()
        .iter()
        .filter_map(|f| match f.surface {
            Surface::Plane { n, .. } => Some(n),
            _ => None,
        })
        .collect();
    let mut worst: f64 = 0.0;
    for n in &r.planes {
        let apart = mine.iter().map(|m| m.unit().dot(n.unit()).clamp(-1.0, 1.0).acos()).fold(f64::INFINITY, f64::min);
        worst = worst.max(apart);
    }
    assert!(worst <= turned, "{name}: an end faces {worst:.2e} rad off OCCT's");
    println!(
        "{name:22} {:7} triangles  volume off OCCT's by {:+.2e}  vertex off its surface {off:.1e}  ends off OCCT's by {worst:.1e} rad",
        s.tris().len(),
        (v - r.volume) / r.volume
    );
}

/// The coil mandrel's groove profile: a circle in the X-Z plane through the helix's start.
fn start(z0: f64) -> Plane {
    Plane::new(v3(63.675, 0.0, z0), Z, V3::Y).unwrap()
}

fn circle() -> Profile {
    Profile::circle(v2(0.0, 0.0), 3.175)
}

#[test]
fn groove_in_the_minimal_frame() -> anyhow::Result<()> {
    matches("helix_groove", &start(0.0).helix_sweep(&circle(), V3::ZERO, Z, 12.33, 2.0)?, 1e-6, 1e-3);
    let pitch = 12.325584919167285;
    let mandrel = start(0.0).helix_sweep(&circle(), V3::ZERO, Z, pitch, 119.4 / pitch)?;
    matches("helix_groove_mandrel", &mandrel, 1e-6, 2.5e-3);
    Ok(())
}

#[test]
fn groove_in_the_screw_frame() -> anyhow::Result<()> {
    matches("screw_groove", &start(0.0).screw(&circle(), V3::ZERO, Z, 12.33, 2.0)?, 1e-6, 1e-9);
    Ok(())
}

#[test]
fn left_handed_thread() -> anyhow::Result<()> {
    let plane = Plane::new(v3(10.0, 0.0, 0.0), V3::X, V3::Y)?;
    let thread = plane.screw(&Profile::rect(v2(0.0, 0.0), 2.0, 1.5), V3::ZERO, Z, 4.0, -2.0)?;
    matches("screw_thread_left", &thread, 1e-6, 1e-9);
    let walls: Vec<f64> = thread
        .faces()
        .iter()
        .filter_map(|f| match f.surface {
            Surface::Cylinder { r, .. } => Some(r),
            _ => None,
        })
        .collect();
    assert_eq!(walls.len(), 2, "the thread's inner and outer walls are cylinders: {walls:?}");
    Ok(())
}

#[test]
fn grooved_ring() -> anyhow::Result<()> {
    let ring = Plane::XY.extrude(&Profile::circle(v2(0.0, 0.0), 61.5).with_hole(Loop::circle(v2(0.0, 0.0), 56.5)), 40.0)?;
    let groove = start(5.0).helix_sweep(&circle(), V3::ZERO, Z, 12.33, 2.0)?;
    matches("helix_grooved_ring", &ring.cut(&groove)?, 2.0 * LINEAR, 1e-3);
    Ok(())
}

#[test]
fn same_bytes_every_time() -> anyhow::Result<()> {
    let build = || start(0.0).helix_sweep(&circle(), V3::ZERO, Z, 12.33, 2.0);
    assert!(stl_bytes(&[&build()?])? == stl_bytes(&[&build()?])?, "two builds of one helix sweep wrote different bytes");
    Ok(())
}
