//! Flattens the Sculpted tip's mating shoulder for slicing. The tip is posed on the plate, cut
//! finer until its shoulder field carries every edge and face back to the plate within
//! tolerance, and laid into the virtual frame its warp donor is sliced in, with a receipt of the
//! pose and the field for the stages that lay the donor's courses back.
//!
//! The arithmetic is the trial's numpy arithmetic, operation for operation, so the mesh and
//! receipt are the ones its Python wrote.

use crate::course_field::ShoulderHold;
use crate::json::{python_number, Json};
use crate::mesh::{bounds, stl_corners, Mesh};
use anyhow::{bail, ensure, Context, Result};
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
    /// The slicing heights between which courses hold the field's full incline.
    pub hold: [f64; 2],
    /// The slicing height from which courses are level again.
    pub normal_again: f64,
    /// The donor's nominal course height.
    pub normal_course: f64,
    pub receipt: Receipt,
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
    hold: [JOINT_LAYER - 0.48, JOINT_LAYER + 1.68],
    normal_again: 62.12,
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
    hold: [18.44, 29.0],
    normal_again: 66.2,
    normal_course: 0.2,
    receipt: Receipt::BearingPlane,
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
const REFINE_ROUNDS: usize = 12;
/// The grid the field's rate of lift is checked on, and the least rate that keeps it invertible.
const GRID_Y: usize = 221;
const GRID_U: usize = 301;
const MIN_DERIVATIVE: f64 = 0.08;
/// Below this a face's cross product has no direction, as trimesh judges it.
const TOL_ZERO: f64 = 1e-13;

/// A dot product as Accelerate's matrix products in the trial's numpy accumulate one: each
/// product fused into the running sum, in index order.
pub fn fused(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[2].mul_add(b[2], a[1].mul_add(b[1], a[0] * b[0]))
}

/// A dot product as Accelerate takes a row of a row-ordered matrix with a vector: each product
/// rounded, the products summed in index order.
pub fn plain(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

pub(crate) fn column(m: &[[f64; 3]; 3], i: usize) -> [f64; 3] {
    [m[0][i], m[1][i], m[2][i]]
}

/// The warped tip's binary STL and its receipt.
pub struct Warped {
    pub stl: Vec<u8>,
    pub receipt: String,
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
            let turned: Vec<[f64; 3]> = source.vertices.iter().map(|v| desired.map(|row| fused(*v, row))).collect();
            let old: Vec<[f64; 3]> = source.vertices.iter().map(|v| physical.map(|row| fused(*v, row))).collect();
            let ((old_low, old_high), (low, high)) = (bounds(&old), bounds(&turned));
            let mut placement = [0, 1, 2].map(|i| translation[i] + (old_low[i] + old_high[i]) * 0.5 - (low[i] + high[i]) * 0.5);
            placement[2] = -low[2];
            let world: Vec<[f64; 3]> = turned.iter().map(|p| [0, 1, 2].map(|i| p[i] + placement[i])).collect();
            let shoulder = [0, 1, 2].map(|i| plain(desired[i], CANONICAL_POINT) + placement[i]);
            (desired, placement, world, shoulder)
        }
        Pose::Project => {
            let world: Vec<[f64; 3]> = source
                .vertices
                .iter()
                .map(|v| {
                    let p = physical.map(|row| fused(*v, row));
                    [0, 1, 2].map(|i| p[i] + translation[i])
                })
                .collect();
            let shoulder = [0, 1, 2].map(|i| fused(physical[i], CANONICAL_POINT) + translation[i]);
            (physical, translation, world, shoulder)
        }
    };
    let field = shoulder_field(recipe, shoulder);
    let (low, high) = bounds(&world);
    let ys = linspace(low[1], high[1], GRID_Y);
    let us = linspace(recipe.bed_through, recipe.normal_again, GRID_U);
    let f = &field;
    let least = ys.iter().flat_map(|y| us.iter().map(move |u| f.derivative(*y, *u))).fold(f64::INFINITY, f64::min);
    ensure!(least > MIN_DERIVATIVE, "Tip inverse needs a single, continuous crossing, got {}", python_number(least));
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
            [0, 1, 2].map(|i| fused(m, column(&rotation, i)))
        })
        .collect();
    ensure!(closed(&faces), "The conforming warp yielded an open model");

    let mut receipt = vec![
        entry("purpose", Json::Text(recipe.purpose.into())),
        entry("orientation_degrees", number(DONOR_ANGLE - recipe.bearing_angle)),
    ];
    if let Receipt::BearingPlane = recipe.receipt {
        receipt.push(entry("bearing_plane_degrees", number(recipe.bearing_angle)));
    }
    receipt.extend([
        entry("authored_plane_pick_world_xyz_mm", numbers(&field.shoulder)),
        entry("physical_cad_to_plate_translation", numbers(&placement)),
        entry("physical_rotation", Json::List(rotation.iter().map(|row| numbers(row)).collect())),
        entry("virtual_shoulder_z_mm", number(field.shoulder_layer)),
    ]);
    if let Receipt::FirstCourse = recipe.receipt {
        receipt.push(entry("first_model_virtual_onto_shoulder_z_mm", number(field.shoulder_layer + recipe.normal_course)));
    }
    receipt.extend([
        entry("incoming_fade_virtual_mm", numbers(&[recipe.bed_through, recipe.hold[0]])),
        entry("outgoing_fade_virtual_mm", numbers(&[recipe.hold[1], recipe.normal_again])),
        entry("exactly_inclined_virtual_mm", numbers(&recipe.hold)),
        entry("xy_limits_exact_plane_y_mm", numbers(&field.exact_y)),
        entry("outside_edge_blend_width_y_mm", number(EDGE_EASE_WIDTH)),
        entry("full_angle_degrees", number(recipe.field_angle)),
        entry("normal_course_mm", number(recipe.normal_course)),
        entry(
            "maximum_cad_error",
            Json::Map(vec![
                entry("max_sampled_edge_remap_error_mm", number(edge_error)),
                entry("max_sampled_centroid_remap_error_mm", number(centroid_error)),
                entry("tip_unchanged_under_z", number(recipe.bed_through)),
                entry("tip_unchanged_above_z", number(recipe.normal_again)),
            ]),
        ),
        entry(
            "area_scope",
            Json::Map(vec![
                entry("physical_print_bounds_mm", Json::List(vec![numbers(&low), numbers(&high)])),
                entry(
                    "donor_nominal_physical_pitch_sample_mm",
                    numbers(&[pitch.0 * recipe.normal_course, pitch.1 * recipe.normal_course]),
                ),
            ]),
        ),
        entry("original_facet_count", count(original_faces)),
        entry("warped_facet_count", count(faces.len())),
        entry("minimum_invertibility_derivative", number(least)),
    ]);
    Ok(Warped { stl: stl(&virtual_vertices, &faces), receipt: Json::Map(receipt).dumps() + "\n" })
}

/// Write the warped tip to `output` and its receipt beside it, as `.json`.
pub fn write(recipe: &Recipe, mesh: &Path, project: &Path, output: &Path) -> Result<()> {
    let warped = warp(recipe, mesh, project)?;
    std::fs::write(output, &warped.stl).with_context(|| format!("writing {}", output.display()))?;
    let receipt = output.with_extension("json");
    std::fs::write(&receipt, &warped.receipt).with_context(|| format!("writing {}", receipt.display()))
}

pub(crate) fn entry(key: &str, value: Json) -> (String, Json) {
    (key.to_string(), value)
}

pub(crate) fn number(v: f64) -> Json {
    Json::Number(python_number(v), v)
}

pub(crate) fn numbers(v: &[f64]) -> Json {
    Json::List(v.iter().map(|x| number(*x)).collect())
}

fn count(n: usize) -> Json {
    Json::Number(n.to_string(), n as f64)
}

/// The recipe's field about the shoulder pick, placed on the plate.
pub(crate) fn shoulder_field(recipe: &Recipe, shoulder: [f64; 3]) -> ShoulderHold {
    let field = recipe.field_angle.to_radians();
    let c = recipe.bearing_angle.to_radians().cos();
    ShoulderHold {
        shoulder,
        shoulder_layer: recipe.shoulder_layer.unwrap_or(shoulder[2]),
        tangent: field.tan(),
        sec_minus_one: 1.0 / field.cos() - 1.0,
        bed_through: recipe.bed_through,
        hold: recipe.hold,
        normal_again: recipe.normal_again,
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
    Ok((rotation, [0, 1, 2].map(|i| placed[9 + i] - fused(rotation[i], centre))))
}

/// `count` evenly spaced values from `start` to `stop`, as numpy's linspace makes them.
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
    for _ in 0..REFINE_ROUNDS {
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
        let mean = |v: [f64; 3]| (0.0 + v[0] + v[1] + v[2]) / 3.0;
        let mut centroid_error = 0.0f64;
        for (f, owned) in faces.iter().zip(&face_edges) {
            let corners = f.map(|i| vertices[i]);
            let lifted = corners.map(|p| field.inverse(p[1], p[2]));
            let error = (field.forward(mean(corners.map(|p| p[1])), mean(lifted)) - mean(corners.map(|p| p[2]))).abs();
            if error > MAX_REMAP_EDGE_ERROR {
                for &e in owned {
                    split[e] = true;
                }
            }
            centroid_error = centroid_error.max(error);
        }
        if !split.contains(&true) {
            let worst_edge = edge_error.iter().copied().fold(f64::NEG_INFINITY, f64::max);
            return Ok((vertices, faces, [worst_edge, centroid_error]));
        }
        let mut middle = vec![usize::MAX; edges.len()];
        for (k, &(a, b)) in edges.iter().enumerate() {
            if split[k] {
                let (p, q) = (vertices[a], vertices[b]);
                middle[k] = vertices.len();
                vertices.push([0, 1, 2].map(|i| (0.0 + p[i] + q[i]) / 2.0));
            }
        }
        faces = split_faces(&faces, &face_edges, &middle);
    }
    bail!("Nonplanar slicing mesh refinement did not meet fidelity target")
}

/// The faces a face is cut into, by the pattern of its split edges, as indices into its corners
/// `a`, `b`, `c` followed by the midpoints of `ab`, `bc`, `ca`. A pattern's faces come together,
/// each of its pieces in turn across all its faces.
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
    let corners: Vec<[usize; 6]> = faces
        .iter()
        .zip(face_edges)
        .map(|(f, e)| [f[0], f[1], f[2], middle[e[0]], middle[e[1]], middle[e[2]]])
        .collect();
    let pattern: Vec<usize> = corners.iter().map(|c| (3..6).filter(|&k| c[k] != usize::MAX).map(|k| 1 << (k - 3)).sum()).collect();
    let mut out = Vec::with_capacity(faces.len() * 2);
    for (kind, pieces) in PIECES.iter().enumerate() {
        let matched: Vec<&[usize; 6]> = corners.iter().zip(&pattern).filter(|(_, p)| **p == kind).map(|(c, _)| c).collect();
        for piece in pieces.iter() {
            out.extend(matched.iter().map(|c| (*piece).map(|k| c[k])));
        }
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

/// A binary STL as trimesh exports one: each face's normal from its first two edges in turn,
/// scaled by the reciprocal of its length, or none for a face without area.
pub(crate) fn stl(vertices: &[[f64; 3]], faces: &[[usize; 3]]) -> Vec<u8> {
    let mut out = vec![0u8; 80];
    out.extend_from_slice(&(faces.len() as u32).to_le_bytes());
    out.reserve(faces.len() * 50);
    for f in faces {
        let [a, b, c] = f.map(|i| vertices[i]);
        let u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
        let w = [c[0] - b[0], c[1] - b[1], c[2] - b[2]];
        let n = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]];
        let length = (n[0] * n[0] + n[1] * n[1] + n[2] * n[2]).sqrt();
        let normal = if length > TOL_ZERO {
            let r = 1.0 / length;
            n.map(|v| v * r)
        } else {
            [0.0; 3]
        };
        for v in normal.iter().chain(&a).chain(&b).chain(&c) {
            out.extend_from_slice(&(*v as f32).to_le_bytes());
        }
        out.extend_from_slice(&[0, 0]);
    }
    out
}
