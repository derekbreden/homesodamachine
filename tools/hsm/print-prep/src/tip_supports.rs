//! Describes the Sculpted tip's mating seat to the plug-ramp donor's native support slicing: a
//! roof sector over each half of the mating annulus that calls for support, an access slit
//! between the sectors that keeps it out, and a keepout over the male plug, each carried through
//! the field into the donor's frame, with the course settings the preparer reads beside them.
//!
//! The arithmetic is the trial's numpy and trimesh arithmetic, so the meshes and settings are
//! the ones its Python wrote.

use crate::json::Json;
use crate::tip_warp::{closed, column, entry, fused, linspace, number, numbers, plain, shoulder_field, stl, CANONICAL_POINT, PLUG_RAMP};
use anyhow::{ensure, Context, Result};
use serde_json::Value;
use std::collections::HashMap;
use std::path::Path;

/// The mating annulus's centre across the bearing plane.
const CENTRE: f64 = 4.024;
/// The roof sectors' radii and their depths about the bearing plane.
const ROOF_RADII: [f64; 2] = [12.05, 14.0];
const ENFORCEMENT_DEPTH: [f64; 2] = [-0.72, 0.55];
/// Half the angle of each access slit, which the roof sectors stop short of.
const RELEASE_HALF_ANGLE: f64 = 4.0;
const SLIT_RADII: [f64; 2] = [11.72, 14.28];
const SLIT_DEPTH: [f64; 2] = [-1.0, 0.74];
const PLUG_RADIUS: f64 = 11.8;
const PLUG_DEPTH: [f64; 2] = [-1.15, 0.38];
/// The points along each roof sector and each slit, and the wedges around the plug.
const ROOF_POINTS: usize = 175;
const SLIT_POINTS: usize = 9;
const PLUG_SECTIONS: usize = 144;
/// The preparer's course bands, each a start, end and step in millimetres.
const COURSE_BANDS: [[f64; 3]; 1] = [[0.2, 30.2, 0.2]];

/// A closed mesh: its vertices and its faces.
type Solid = (Vec<[f64; 3]>, Vec<[usize; 3]>);

/// Write the support settings to `output` and the support meshes beside it, for the warp in
/// `warp_receipt`.
pub fn write(warp_receipt: &Path, output: &Path) -> Result<()> {
    let receipt: Value =
        serde_json::from_slice(&std::fs::read(warp_receipt).with_context(|| format!("reading {}", warp_receipt.display()))?)?;
    let rotation: [[f64; 3]; 3] = serde_json::from_value(receipt["physical_rotation"].clone()).context("the receipt's rotation")?;
    let translation: [f64; 3] =
        serde_json::from_value(receipt["physical_cad_to_plate_translation"].clone()).context("the receipt's translation")?;
    let shoulder = [0, 1, 2].map(|i| plain(rotation[i], CANONICAL_POINT) + translation[i]);
    let field = shoulder_field(&PLUG_RAMP, shoulder);
    let bearing = crate::rotation_x(-PLUG_RAMP.bearing_angle);
    let folder = output.parent().unwrap_or(Path::new("."));
    let mut parts = Vec::new();
    let mut part = |name: String, role: &str, (vertices, faces): Solid| -> Result<()> {
        let seated: Vec<[f64; 3]> = vertices
            .iter()
            .map(|v| {
                let on = bearing.map(|row| fused(*v, row));
                let on = [0, 1, 2].map(|i| on[i] + shoulder[i]);
                let sliced = [on[0] - translation[0], on[1] - translation[1], field.inverse(on[1], on[2]) - translation[2]];
                [0, 1, 2].map(|i| fused(sliced, column(&rotation, i)))
            })
            .collect();
        ensure!(closed(&faces), "{name} has an open support mesh");
        let faces = if volume(&seated, &faces) < 0.0 { faces.iter().map(|f| [f[2], f[1], f[0]]).collect() } else { faces };
        let file = format!("{}.stl", name.replace(' ', "-").to_lowercase());
        let path = folder.join(&file);
        std::fs::write(&path, stl(&seated, &faces)).with_context(|| format!("writing {}", path.display()))?;
        parts.push(Json::Map(vec![entry("name", Json::Text(name)), entry("role", Json::Text(role.into())), entry("stl", Json::Text(file))]));
        Ok(())
    };
    for (i, centre) in [0.0, 180.0].into_iter().enumerate() {
        let roof = linspace(centre + RELEASE_HALF_ANGLE, centre + 180.0 - RELEASE_HALF_ANGLE, ROOF_POINTS);
        part(format!("Shoulder roof sector {}", i + 1), "support_enforcer", sector(&roof, ROOF_RADII, ENFORCEMENT_DEPTH))?;
        let slit = linspace(centre - RELEASE_HALF_ANGLE, centre + RELEASE_HALF_ANGLE, SLIT_POINTS);
        part(format!("Roof access slit {}", i + 1), "support_blocker", sector(&slit, SLIT_RADII, SLIT_DEPTH))?;
    }
    part("Mating plug keepout".into(), "support_blocker", plug())?;
    let settings = Json::Map(vec![
        entry("course_bands_mm", Json::List(COURSE_BANDS.iter().map(|band| numbers(band)).collect())),
        entry("native_nose_handoff_mm", number(PLUG_RAMP.normal_again)),
        entry("support_parts", Json::List(parts)),
    ]);
    std::fs::write(output, settings.dumps() + "\n").with_context(|| format!("writing {}", output.display()))
}

/// A ring sector about the annulus centre through `angles`, in degrees, between two radii and
/// two depths, closed by a quad at each end.
fn sector(angles: &[f64], [inner, outer]: [f64; 2], [low, high]: [f64; 2]) -> Solid {
    let section = [[inner, low], [outer, low], [outer, high], [inner, high]];
    let mut vertices = Vec::with_capacity(angles.len() * 4);
    for a in angles {
        let a = a.to_radians();
        for [r, z] in section {
            vertices.push([a.cos() * r, CENTRE + a.sin() * r, z]);
        }
    }
    let mut faces = vec![[0, 2, 1], [0, 3, 2]];
    for step in 0..angles.len() - 1 {
        for edge in 0..4 {
            let (i, j) = (step * 4 + edge, step * 4 + (edge + 1) % 4);
            faces.extend([[i, j, j + 4], [i, j + 4, i + 4]]);
        }
    }
    let end = 4 * (angles.len() - 1);
    faces.extend([[end, end + 1, end + 2], [end, end + 2, end + 3]]);
    (vertices, faces)
}

/// The plug keepout: a cylinder as trimesh revolves one, its profile's axis points joined into
/// one point per cap, moved onto the annulus centre and depth.
fn plug() -> Solid {
    let half = (PLUG_DEPTH[1] - PLUG_DEPTH[0]).abs() / 2.0;
    let profile = [[0.0, -half], [PLUG_RADIUS, -half], [PLUG_RADIUS, half], [0.0, half]];
    let theta = linspace(0.0, std::f64::consts::PI * 2.0, PLUG_SECTIONS + 1);
    // The revolution is closed, so its last ring is its first.
    let mut vertices = Vec::with_capacity(PLUG_SECTIONS * profile.len());
    for t in &theta[..PLUG_SECTIONS] {
        for [r, z] in profile {
            vertices.push([t.cos() * r, t.sin() * r, z]);
        }
    }
    // Each wedge's faces, the two that would join axis points to themselves having no area.
    let count = vertices.len();
    let wedge = [[1, 4, 5], [1, 5, 2], [2, 5, 6], [2, 6, 3]];
    let faces: Vec<[usize; 3]> = (0..PLUG_SECTIONS).flat_map(|k| wedge.map(|f| f.map(|i| (i + 4 * k) % count))).collect();
    let (vertices, faces) = merged(vertices, faces);
    // trimesh moves the points by a homogeneous matrix, which Accelerate multiplies through.
    let depth = (PLUG_DEPTH[0] + PLUG_DEPTH[1]) / 2.0;
    let matrix = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, CENTRE], [0.0, 0.0, 1.0, depth]];
    let moved = vertices
        .iter()
        .map(|v| {
            let point = [v[0], v[1], v[2], 1.0];
            matrix.map(|row| (1..4).fold(row[0] * point[0], |sum, k| row[k].mul_add(point[k], sum)))
        })
        .collect();
    (moved, faces)
}

/// Vertices that land on the same point, at trimesh's merging precision, joined into the first,
/// as trimesh merges them.
fn merged(vertices: Vec<[f64; 3]>, faces: Vec<[usize; 3]>) -> Solid {
    let mut index: HashMap<[i64; 3], usize> = HashMap::with_capacity(vertices.len());
    let mut kept = Vec::with_capacity(vertices.len());
    let renumber: Vec<usize> = vertices
        .iter()
        .map(|v| {
            *index.entry(v.map(|x| (x * 1e8).round_ties_even() as i64)).or_insert_with(|| {
                kept.push(*v);
                kept.len() - 1
            })
        })
        .collect();
    (kept, faces.iter().map(|f| f.map(|i| renumber[i])).collect())
}

/// The signed volume, positive when the faces wind outward.
fn volume(vertices: &[[f64; 3]], faces: &[[usize; 3]]) -> f64 {
    faces
        .iter()
        .map(|f| {
            let [a, b, c] = f.map(|i| vertices[i]);
            let (u, w) = ([b[1] - a[1], b[2] - a[2]], [c[1] - b[1], c[2] - b[2]]);
            (u[0] * w[1] - u[1] * w[0]) * (a[0] + b[0] + c[0])
        })
        .sum::<f64>()
        / 6.0
}
