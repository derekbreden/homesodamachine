//! Describes the Sculpted tip's mating seat to the plug-ramp donor's native support slicing: a
//! roof sector over each half of the mating annulus that calls for support, an access slit
//! between the sectors that keeps it out, and a keepout over the male plug, each carried through
//! the field into the donor's frame, with the course settings the preparer reads beside them.

use crate::mesh::{write_stl, Mesh};
use crate::tip_warp::{closed, column, dot, linspace, shoulder_field, CANONICAL_POINT, PLUG_RAMP};
use anyhow::{ensure, Context, Result};
use serde_json::{json, Value};
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

/// Write the support settings to `output` and the support meshes beside it, for the warp in
/// `warp_receipt`.
pub fn write(warp_receipt: &Path, output: &Path) -> Result<()> {
    let receipt: Value =
        serde_json::from_slice(&std::fs::read(warp_receipt).with_context(|| format!("reading {}", warp_receipt.display()))?)?;
    let rotation: [[f64; 3]; 3] = serde_json::from_value(receipt["physical_rotation"].clone()).context("the receipt's rotation")?;
    let translation: [f64; 3] =
        serde_json::from_value(receipt["physical_cad_to_plate_translation"].clone()).context("the receipt's translation")?;
    let shoulder = [0, 1, 2].map(|i| dot(rotation[i], CANONICAL_POINT) + translation[i]);
    let field = shoulder_field(&PLUG_RAMP, shoulder);
    let bearing = crate::rotation_x(-PLUG_RAMP.bearing_angle);
    let folder = output.parent().unwrap_or(Path::new("."));
    let mut parts = Vec::new();
    let mut part = |name: String, role: &str, solid: Mesh| -> Result<()> {
        let vertices = solid
            .vertices
            .iter()
            .map(|v| {
                let on = bearing.map(|row| dot(*v, row));
                let on = [0, 1, 2].map(|i| on[i] + shoulder[i]);
                let sliced = [on[0] - translation[0], on[1] - translation[1], field.inverse(on[1], on[2]) - translation[2]];
                [0, 1, 2].map(|i| dot(sliced, column(&rotation, i)))
            })
            .collect();
        ensure!(closed(&solid.faces), "{name} has an open support mesh");
        let mut seated = Mesh { vertices, faces: solid.faces };
        if seated.volume() < 0.0 {
            seated.faces.iter_mut().for_each(|f| f.swap(0, 2));
        }
        let file = format!("{}.stl", name.replace(' ', "-").to_lowercase());
        let path = folder.join(&file);
        write_stl(&path, &seated.vertices, &seated.faces).with_context(|| format!("writing {}", path.display()))?;
        parts.push(json!({"name": name, "role": role, "stl": file}));
        Ok(())
    };
    for (i, centre) in [0.0, 180.0].into_iter().enumerate() {
        let roof = linspace(centre + RELEASE_HALF_ANGLE, centre + 180.0 - RELEASE_HALF_ANGLE, ROOF_POINTS);
        part(format!("Shoulder roof sector {}", i + 1), "support_enforcer", sector(&roof, ROOF_RADII, ENFORCEMENT_DEPTH))?;
        let slit = linspace(centre - RELEASE_HALF_ANGLE, centre + RELEASE_HALF_ANGLE, SLIT_POINTS);
        part(format!("Roof access slit {}", i + 1), "support_blocker", sector(&slit, SLIT_RADII, SLIT_DEPTH))?;
    }
    part("Mating plug keepout".into(), "support_blocker", plug())?;
    let settings = json!({
        "course_bands_mm": COURSE_BANDS,
        "native_nose_handoff_mm": PLUG_RAMP.normal_again,
        "support_parts": parts,
    });
    std::fs::write(output, serde_json::to_string_pretty(&settings)? + "\n").with_context(|| format!("writing {}", output.display()))
}

/// A ring sector about the annulus centre through `angles`, in degrees, between two radii and
/// two depths, closed by a quad at each end.
fn sector(angles: &[f64], [inner, outer]: [f64; 2], [low, high]: [f64; 2]) -> Mesh {
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
    Mesh { vertices, faces }
}

/// The plug keepout: a cylinder about the annulus centre between the plug's depths, each cap a
/// fan about its centre.
fn plug() -> Mesh {
    let [low, high] = PLUG_DEPTH;
    let mut vertices = vec![[0.0, CENTRE, low], [0.0, CENTRE, high]];
    for t in &linspace(0.0, std::f64::consts::TAU, PLUG_SECTIONS + 1)[..PLUG_SECTIONS] {
        let (x, y) = (t.cos() * PLUG_RADIUS, CENTRE + t.sin() * PLUG_RADIUS);
        vertices.extend([[x, y, low], [x, y, high]]);
    }
    let rim = |k: usize| (2 + 2 * (k % PLUG_SECTIONS), 3 + 2 * (k % PLUG_SECTIONS));
    let faces = (0..PLUG_SECTIONS)
        .flat_map(|k| {
            let ((b, t), (b1, t1)) = (rim(k), rim(k + 1));
            [[b, 0, b1], [b, b1, t], [t, b1, t1], [t, t1, 1]]
        })
        .collect();
    Mesh { vertices, faces }
}
