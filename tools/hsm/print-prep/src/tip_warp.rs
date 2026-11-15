//! Flattens the Sculpted tip's mating shoulder for slicing. The tip is posed on the plate, cut
//! finer until its shoulder field carries every edge and face back to the plate within
//! tolerance, and laid into the virtual frame its warp donor is sliced in, with a receipt of the
//! pose and the field for the stages that lay the donor's courses back.

use crate::course_field::ShoulderHold;
use crate::mesh::{bounds, stl_corners, write_stl, Mesh};
use anyhow::{bail, ensure, Context, Result};
use hsm_faucet_numbers::paths;
use serde_json::{json, Value};
use std::collections::HashMap;
use std::io::Read;
use std::path::Path;

/// How a trial poses the tip and shapes the field its courses follow.
pub struct Recipe {
    /// The receipt's purpose line.
    pub purpose: &'static str,
    pub pose: Pose,
    /// The incline the field lays the shoulder's courses at, in degrees.
    pub field_angle: f64,
    /// The mating bearing plane's incline, in degrees: it turns the tip and sets the width of the
    /// flat shoulder.
    pub bearing_angle: f64,
    /// The slicing height of the shoulder course, or none for the shoulder pick's own height.
    pub shoulder_layer: Option<f64>,
    /// The slicing height up to which courses stay level on the bed.
    pub bed_through: f64,
    pub transition: Transition,
    /// The donor's nominal course height.
    pub normal_course: f64,
    pub receipt: Receipt,
}

/// Where the courses hold their full tilt and where they become level.
pub enum Transition {
    /// All boundaries are slicing heights measured from the plate.
    Plate { hold: [f64; 2], level_from: f64 },
    /// Hold on either side of the mating plane and ease to level where the tube axis is vertical.
    Tube { shoulder_offsets: [f64; 2] },
}

/// Where the tip stands on the plate while it is warped.
pub enum Pose {
    /// Turned about X from its CAD frame by the donor angle less the bearing plane's incline,
    /// centred in plan where the editable project centres it, and set down on the bed.
    Turned,
    /// As the editable project places it.
    Project,
}

/// The line a trial's receipt carries besides the common ones.
pub enum Receipt {
    /// The slicing height of the first model course laid onto the shoulder.
    FirstCourse,
    /// The bearing plane's incline.
    BearingPlane,
}

/// The tip-shoulder trial: the tip turned exactly to its bearing plane, its courses holding the
/// plane's incline through the shoulder.
pub const TIP_SHOULDER: Recipe = Recipe {
    purpose: FLATTEN,
    pose: Pose::Turned,
    field_angle: 35.0,
    bearing_angle: 35.0,
    shoulder_layer: Some(JOINT_LAYER),
    bed_through: 0.92,
    transition: Transition::Plate { hold: [JOINT_LAYER - 0.48, JOINT_LAYER + 1.68], level_from: 62.12 },
    normal_course: 0.24,
    receipt: Receipt::FirstCourse,
};

/// The plug-ramp trial: the tip as the editable project poses it, its courses ramping gently up
/// through the male plug and holding that ramp across the shoulder.
pub const PLUG_RAMP: Recipe = Recipe {
    purpose: FLATTEN,
    pose: Pose::Project,
    field_angle: 15.0,
    bearing_angle: 35.0,
    shoulder_layer: None,
    bed_through: 0.92,
    transition: Transition::Plate { hold: [18.44, 29.0], level_from: 66.2 },
    normal_course: 0.2,
    receipt: Receipt::BearingPlane,
};

/// The matched shoulder: start the tilt above the hidden bed anchor and hold the mating plane
/// through the support interface and the first model courses.
pub const MATCHED_SHOULDER: Recipe = Recipe {
    purpose: FLATTEN,
    pose: Pose::Project,
    field_angle: 20.0,
    bearing_angle: 20.0,
    shoulder_layer: None,
    bed_through: 0.68,
    transition: Transition::Tube { shoulder_offsets: [-1.2, 1.2] },
    normal_course: 0.2,
    receipt: Receipt::BearingPlane,
};

/// The shoulder's interface and visible foundation hold the same plane through the last course.
pub const SHORT_SHOULDER: Recipe = Recipe {
    transition: Transition::Tube { shoulder_offsets: [-1.2, 1.4] },
    ..MATCHED_SHOULDER
};

/// The purpose line both trials' receipts carry.
const FLATTEN: &str = "Flatten the mating shoulder for slicing while preserving physical tip geometry.";
const JOINT_LAYER: f64 = 22.28;

/// The angle about X the donor's CAD frame is turned from before the bearing plane's incline.
const DONOR_ANGLE: f64 = -70.0;
/// The tip's mating shoulder point in its CAD frame.
pub(crate) const CANONICAL_POINT: [f64; 3] = [0.0, -38.36796889030837, 220.8576411168048];
/// The mating annulus's outer radius and its centre across the bearing plane.
const SHOULDER_RADIUS: f64 = 13.5;
const SHOULDER_CENTRE: f64 = 4.024;
/// How far past the annulus, across Y, the shoulder stays flat.
const FLAT_SHOULDER_Y_PADDING: f64 = 1.45;
/// The width across Y over which the flat shoulder eases out.
const EDGE_EASE_WIDTH: f64 = 2.0;
/// The largest height error the field may leave along an edge or at a face's centre.
const MAX_REMAP_EDGE_ERROR: f64 = 0.0125;
const EDGE_REFINE_ROUNDS: usize = 12;
const FACE_REFINE_ROUNDS: usize = 4;
/// The grid the field's rate of lift is checked on, and the least rate that keeps it invertible.
const GRID_Y: usize = 221;
const GRID_U: usize = 301;
const MIN_DERIVATIVE: f64 = 0.08;

pub(crate) fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

pub(crate) fn column(m: &[[f64; 3]; 3], i: usize) -> [f64; 3] {
    [m[0][i], m[1][i], m[2][i]]
}

/// The warped tip in the donor's virtual frame, and its receipt.
pub struct Warped {
    pub vertices: Vec<[f64; 3]>,
    pub faces: Vec<[usize; 3]>,
    pub receipt: Value,
}

/// The tip in `mesh`, posed from the editable `project` and warped by `recipe`.
pub fn warp(recipe: &Recipe, mesh: &Path, project: &Path) -> Result<Warped> {
    let bytes = std::fs::read(mesh).with_context(|| format!("reading {}", mesh.display()))?;
    let corners = stl_corners(&bytes).with_context(|| format!("reading {}", mesh.display()))?;
    let source = Mesh::from_corners(&corners);
    let (physical, translation) = physical_origin(project, &corners)?;
    let (rotation, placement, world, shoulder) = match recipe.pose {
        Pose::Turned => {
            let desired = crate::rotation_x(DONOR_ANGLE - recipe.bearing_angle);
            let turned: Vec<[f64; 3]> = source.vertices.iter().map(|v| desired.map(|row| dot(*v, row))).collect();
            let old: Vec<[f64; 3]> = source.vertices.iter().map(|v| physical.map(|row| dot(*v, row))).collect();
            let ((old_low, old_high), (low, high)) = (bounds(&old), bounds(&turned));
            let mut placement = [0, 1, 2].map(|i| translation[i] + (old_low[i] + old_high[i]) * 0.5 - (low[i] + high[i]) * 0.5);
            placement[2] = -low[2];
            let world: Vec<[f64; 3]> = turned.iter().map(|p| [0, 1, 2].map(|i| p[i] + placement[i])).collect();
            let shoulder = [0, 1, 2].map(|i| dot(desired[i], CANONICAL_POINT) + placement[i]);
            (desired, placement, world, shoulder)
        }
        Pose::Project => {
            let world: Vec<[f64; 3]> = source
                .vertices
                .iter()
                .map(|v| {
                    let p = physical.map(|row| dot(*v, row));
                    [0, 1, 2].map(|i| p[i] + translation[i])
                })
                .collect();
            let shoulder = [0, 1, 2].map(|i| dot(physical[i], CANONICAL_POINT) + translation[i]);
            (physical, translation, world, shoulder)
        }
    };
    if matches!(recipe.transition, Transition::Tube { .. }) {
        let expected = crate::rotation_x(-paths::JOINT_ANGLE.to_degrees() - recipe.bearing_angle);
        ensure!(
            rotation.iter().flatten().zip(expected.iter().flatten()).all(|(actual, wanted)| (actual - wanted).abs() <= 1e-6),
            "The editable tip pose must set the mating shoulder to {}° from the bed",
            recipe.bearing_angle
        );
    }
    let field = shoulder_field(recipe, shoulder);
    let (low, high) = bounds(&world);
    let ys = linspace(low[1], high[1], GRID_Y);
    let us = linspace(field.bed_through, field.normal_again, GRID_U);
    let f = &field;
    let least = ys.iter().flat_map(|y| us.iter().map(move |u| f.derivative(*y, *u))).fold(f64::INFINITY, f64::min);
    ensure!(least > MIN_DERIVATIVE, "Tip inverse needs a single, continuous crossing, got {least}");
    let original_faces = source.faces.len();
    let (refined, faces, [edge_error, centroid_error]) = refine(world, source.faces, &field)?;
    let mut pitch = (f64::INFINITY, f64::NEG_INFINITY);
    let virtual_vertices: Vec<[f64; 3]> = refined
        .iter()
        .map(|p| {
            let lifted = [p[0], p[1], field.inverse(p[1], p[2])];
            let rate = field.derivative(lifted[1], lifted[2]);
            pitch = (pitch.0.min(rate), pitch.1.max(rate));
            let m = [0, 1, 2].map(|i| lifted[i] - placement[i]);
            [0, 1, 2].map(|i| dot(m, column(&rotation, i)))
        })
        .collect();
    ensure!(closed(&faces), "The conforming warp yielded an open model");

    let mut receipt = json!({
        "purpose": recipe.purpose,
        "orientation_degrees": DONOR_ANGLE - recipe.bearing_angle,
        "authored_plane_pick_world_xyz_mm": field.shoulder,
        "physical_cad_to_plate_translation": placement,
        "physical_rotation": rotation,
        "virtual_shoulder_z_mm": field.shoulder_layer,
        "incoming_fade_virtual_mm": [field.bed_through, field.hold[0]],
        "outgoing_fade_virtual_mm": [field.hold[1], field.normal_again],
        "exactly_inclined_virtual_mm": field.hold,
        "xy_limits_exact_plane_y_mm": field.exact_y,
        "outside_edge_blend_width_y_mm": EDGE_EASE_WIDTH,
        "full_angle_degrees": recipe.field_angle,
        "normal_course_mm": recipe.normal_course,
        "maximum_cad_error": {
            "max_sampled_edge_remap_error_mm": edge_error,
            "max_sampled_centroid_remap_error_mm": centroid_error,
            "tip_unchanged_under_z": field.bed_through,
            "tip_unchanged_above_z": field.normal_again,
        },
        "area_scope": {
            "physical_print_bounds_mm": [low, high],
            "donor_nominal_physical_pitch_sample_mm": [pitch.0 * recipe.normal_course, pitch.1 * recipe.normal_course],
        },
        "original_facet_count": original_faces,
        "warped_facet_count": faces.len(),
        "minimum_invertibility_derivative": least,
    });
    match recipe.receipt {
        Receipt::BearingPlane => receipt["bearing_plane_degrees"] = json!(recipe.bearing_angle),
        Receipt::FirstCourse => receipt["first_model_virtual_onto_shoulder_z_mm"] = json!(field.shoulder_layer + recipe.normal_course),
    }
    Ok(Warped { vertices: virtual_vertices, faces, receipt })
}

/// Write the warped tip to `output` and its receipt beside it, as `.json`.
pub fn write(recipe: &Recipe, mesh: &Path, project: &Path, output: &Path) -> Result<()> {
    let warped = warp(recipe, mesh, project)?;
    write_stl(output, &warped.vertices, &warped.faces).with_context(|| format!("writing {}", output.display()))?;
    let receipt = output.with_extension("json");
    std::fs::write(&receipt, serde_json::to_string_pretty(&warped.receipt)? + "\n").with_context(|| format!("writing {}", receipt.display()))
}

/// The recipe's field about the shoulder pick, placed on the plate.
pub(crate) fn shoulder_field(recipe: &Recipe, shoulder: [f64; 3]) -> ShoulderHold {
    let field = recipe.field_angle.to_radians();
    let c = recipe.bearing_angle.to_radians().cos();
    let shoulder_layer = recipe.shoulder_layer.unwrap_or(shoulder[2]);
    let (hold, normal_again) = match recipe.transition {
        Transition::Plate { hold, level_from } => (hold, level_from),
        Transition::Tube { shoulder_offsets } => {
            let vertical_angle = paths::JOINT_ANGLE + recipe.bearing_angle.to_radians();
            let vertical = paths::arc_point(vertical_angle, 0.0, 0.0);
            let delta = std::array::from_fn(|i| vertical[i] - CANONICAL_POINT[i]);
            let rotation = crate::rotation_x(-vertical_angle.to_degrees());
            (shoulder_offsets.map(|offset| shoulder_layer + offset), shoulder[2] + dot(rotation[2], delta))
        }
    };
    ShoulderHold {
        shoulder,
        shoulder_layer,
        tangent: field.tan(),
        sec_minus_one: 1.0 / field.cos() - 1.0,
        bed_through: recipe.bed_through,
        hold,
        normal_again,
        exact_y: [
            shoulder[1] + (SHOULDER_CENTRE - SHOULDER_RADIUS) * c - FLAT_SHOULDER_Y_PADDING,
            shoulder[1] + (SHOULDER_CENTRE + SHOULDER_RADIUS) * c + FLAT_SHOULDER_Y_PADDING,
        ],
        edge_width: EDGE_EASE_WIDTH,
        displacement: [0.0; 3],
        // The warp moves vertices and lays no roads.
        piece: f64::INFINITY,
    }
}

/// The tip's rotation and translation onto the plate in the editable project, for its mesh
/// centred on its CAD bounding box.
fn physical_origin(project: &Path, corners: &[[f64; 3]]) -> Result<([[f64; 3]; 3], [f64; 3])> {
    let file = std::fs::File::open(project).with_context(|| format!("opening {}", project.display()))?;
    let mut archive = zip::ZipArchive::new(file).with_context(|| format!("reading {}", project.display()))?;
    let mut member = |name: &str| -> Result<String> {
        let mut text = String::new();
        archive.by_name(name).with_context(|| format!("{} has no {name}", project.display()))?.read_to_string(&mut text)?;
        Ok(text)
    };
    let model = crate::xml::parse(&member("3D/3dmodel.model")?)?;
    let settings = crate::xml::parse(&member("Metadata/model_settings.config")?)?;
    let named = |o: &&crate::xml::Element| {
        o.children_named("metadata").any(|m| m.attribute("key") == Some("name") && m.attribute("value") == Some("faucet-shell-tip"))
    };
    let number = settings
        .children_named("object")
        .find(named)
        .and_then(|o| o.attribute("id"))
        .context("the editable project has no faucet-shell-tip")?;
    let transform = model
        .children_named("build")
        .flat_map(|b| b.children_named("item"))
        .find(|i| i.attribute("objectid") == Some(number))
        .and_then(|i| i.attribute("transform"))
        .context("the editable project does not place the faucet-shell-tip")?;
    let placed: Vec<f64> = transform.split_whitespace().map(str::parse).collect::<Result<_, _>>()?;
    ensure!(placed.len() == 12, "the tip's build transform has {} numbers", placed.len());
    let rotation: [[f64; 3]; 3] = std::array::from_fn(|i| std::array::from_fn(|j| placed[3 * j + i]));
    let (low, high) = bounds(corners);
    let centre = [0, 1, 2].map(|i| (low[i] + high[i]) * 0.5);
    Ok((rotation, [0, 1, 2].map(|i| placed[9 + i] - dot(rotation[i], centre))))
}

/// `count` evenly spaced values from `start` to `stop`.
pub(crate) fn linspace(start: f64, stop: f64, count: usize) -> Vec<f64> {
    let step = (stop - start) / (count - 1) as f64;
    let mut values: Vec<f64> = (0..count).map(|i| i as f64 * step + start).collect();
    values[count - 1] = stop;
    values
}

/// Each face's edges as indices into the mesh's distinct edges, in the order `ab`, `bc`, `ca`.
fn unique_edges(faces: &[[usize; 3]]) -> (Vec<(usize, usize)>, Vec<[usize; 3]>) {
    let mut index: HashMap<(usize, usize), usize> = HashMap::with_capacity(faces.len() * 2);
    let mut edges = Vec::with_capacity(faces.len() * 2);
    let face_edges = faces
        .iter()
        .map(|f| {
            [0, 1, 2].map(|k| {
                let (a, b) = (f[k], f[(k + 1) % 3]);
                let key = (a.min(b), a.max(b));
                *index.entry(key).or_insert_with(|| {
                    edges.push(key);
                    edges.len() - 1
                })
            })
        })
        .collect();
    (edges, face_edges)
}

/// The mesh cut at the midpoints of its edges until the field maps every edge's sample points
/// and every face's centre within tolerance, with the largest errors left.
fn refine(mut vertices: Vec<[f64; 3]>, mut faces: Vec<[usize; 3]>, field: &ShoulderHold) -> Result<(Vec<[f64; 3]>, Vec<[usize; 3]>, [f64; 2])> {
    let mut residual = [0.0; 2];
    for round in 0..=EDGE_REFINE_ROUNDS + FACE_REFINE_ROUNDS {
        let (edges, face_edges) = unique_edges(&faces);
        let mut edge_error = Vec::with_capacity(edges.len());
        let mut split = Vec::with_capacity(edges.len());
        for &(a, b) in &edges {
            let (p, q) = (vertices[a], vertices[b]);
            let (wp, wq) = (field.inverse(p[1], p[2]), field.inverse(q[1], q[2]));
            let mut worst = 0.0f64;
            for t in [0.25, 0.5, 0.75] {
                let y = p[1] * (1.0 - t) + q[1] * t;
                let w = wp * (1.0 - t) + wq * t;
                let z = p[2] * (1.0 - t) + q[2] * t;
                worst = worst.max((field.forward(y, w) - z).abs());
            }
            edge_error.push(worst);
            split.push(worst > MAX_REMAP_EDGE_ERROR);
        }
        let mean = |v: [f64; 3]| (v[0] + v[1] + v[2]) / 3.0;
        let mut centroid_error = 0.0f64;
        for (f, owned) in faces.iter().zip(&face_edges) {
            let corners = f.map(|i| vertices[i]);
            let lifted = corners.map(|p| field.inverse(p[1], p[2]));
            let error = (field.forward(mean(corners.map(|p| p[1])), mean(lifted)) - mean(corners.map(|p| p[2]))).abs();
            // Splitting only one edge of a slender face can lay another long diagonal across
            // the same bend in the field. Subdivide the whole affected face if this persists.
            if error > MAX_REMAP_EDGE_ERROR || (round >= EDGE_REFINE_ROUNDS && owned.iter().any(|&e| edge_error[e] > MAX_REMAP_EDGE_ERROR)) {
                for &e in owned {
                    split[e] = true;
                }
            }
            centroid_error = centroid_error.max(error);
        }
        residual = [edge_error.iter().copied().fold(f64::NEG_INFINITY, f64::max), centroid_error];
        if !split.contains(&true) {
            return Ok((vertices, faces, residual));
        }
        if round == EDGE_REFINE_ROUNDS + FACE_REFINE_ROUNDS {
            break;
        }
        let mut middle = vec![usize::MAX; edges.len()];
        for (k, &(a, b)) in edges.iter().enumerate() {
            if split[k] {
                let (p, q) = (vertices[a], vertices[b]);
                middle[k] = vertices.len();
                vertices.push([0, 1, 2].map(|i| (p[i] + q[i]) / 2.0));
            }
        }
        faces = split_faces(&faces, &face_edges, &middle);
    }
    bail!("Nonplanar slicing mesh refinement did not meet fidelity target: edge {:.5} mm, face {:.5} mm", residual[0], residual[1])
}

/// The faces a face is cut into, by the pattern of its split edges, as indices into its corners
/// `a`, `b`, `c` followed by the midpoints of `ab`, `bc`, `ca`.
const PIECES: [&[[usize; 3]]; 8] = [
    &[[0, 1, 2]],
    &[[0, 3, 2], [3, 1, 2]],
    &[[0, 1, 4], [0, 4, 2]],
    &[[3, 1, 4], [0, 3, 4], [0, 4, 2]],
    &[[0, 1, 5], [1, 2, 5]],
    &[[0, 3, 5], [3, 1, 2], [3, 2, 5]],
    &[[2, 5, 4], [1, 4, 5], [1, 5, 0]],
    &[[0, 3, 5], [3, 1, 4], [5, 4, 2], [3, 4, 5]],
];

fn split_faces(faces: &[[usize; 3]], face_edges: &[[usize; 3]], middle: &[usize]) -> Vec<[usize; 3]> {
    let mut out = Vec::with_capacity(faces.len() * 2);
    for (f, e) in faces.iter().zip(face_edges) {
        let corners = [f[0], f[1], f[2], middle[e[0]], middle[e[1]], middle[e[2]]];
        let pattern: usize = (0..3).filter(|&k| corners[3 + k] != usize::MAX).map(|k| 1 << k).sum();
        out.extend(PIECES[pattern].iter().map(|piece| piece.map(|k| corners[k])));
    }
    out
}

/// Whether every edge is shared by exactly two faces.
pub(crate) fn closed(faces: &[[usize; 3]]) -> bool {
    let mut uses: HashMap<(usize, usize), u32> = HashMap::with_capacity(faces.len() * 2);
    for f in faces {
        for k in 0..3 {
            let (a, b) = (f[k], f[(k + 1) % 3]);
            *uses.entry((a.min(b), a.max(b))).or_default() += 1;
        }
    }
    uses.values().all(|&n| n == 2)
}
