//! The printed casing pieces' own print surfaces in the core's payload: each piece's payload, cut
//! from its print at the viewer's tolerance, carried by the placement its fine model takes and put
//! in place of the surface the assembly drew for it; and the fine model bound to the payload that
//! results.
use anyhow::{Context, Result, ensure};
use hsm_cold_core_assembly_numbers::{Placement, Turn};
use hsm_model_export::model::Frame;
use hsm_model_export::payload::Payload;
use std::path::Path;

type Matrix = [[f64; 4]; 4];

fn identity() -> Matrix {
    std::array::from_fn(|r| std::array::from_fn(|c| if r == c { 1.0 } else { 0.0 }))
}

fn multiply(left: Matrix, right: Matrix) -> Matrix {
    std::array::from_fn(|row| {
        std::array::from_fn(|column| (0..4).fold(0.0, |sum, k| sum + left[row][k] * right[k][column]))
    })
}

fn turned(matrix: Matrix, turn: &Turn) -> Matrix {
    let length = turn.axis.iter().fold(0.0, |sum, v| sum + v * v).sqrt();
    let axis = turn.axis.map(|v| v / length);
    let [x, y, z] = axis;
    let skew = [[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]];
    let angle = turn.degrees.to_radians();
    let (cosine, sine) = (angle.cos(), angle.sin());
    let mut turn = identity();
    for row in 0..3 {
        for column in 0..3 {
            turn[row][column] = cosine * if row == column { 1.0 } else { 0.0 }
                + sine * skew[row][column]
                + (1.0 - cosine) * (axis[row] * axis[column]);
        }
    }
    multiply(turn, matrix)
}

fn shifted(matrix: Matrix, shift: [f64; 3]) -> Matrix {
    let mut moved = identity();
    for (row, component) in shift.into_iter().enumerate() {
        moved[row][3] = component;
    }
    multiply(moved, matrix)
}

/// The placement as one carry, applied to a payload's single-precision points.
pub fn frame(placement: &Placement) -> Frame {
    let mut m = identity();
    for turn in &placement.turns {
        m = turned(m, turn);
    }
    m = shifted(m, placement.shift);
    if let Some(carry) = &placement.carry {
        let mut value = identity();
        for (column, components) in carry.columns.iter().enumerate() {
            for (row, component) in components.iter().enumerate() {
                value[row][column] = *component;
            }
        }
        for (row, component) in carry.translation.iter().enumerate() {
            value[row][3] = *component;
        }
        m = multiply(value, m);
    }
    for turn in &placement.after_turns {
        m = turned(m, turn);
    }
    if placement.after_shift != [0.; 3] {
        m = shifted(m, placement.after_shift);
    }
    Frame([m[0], m[1], m[2]])
}

/// Puts each printed piece's own surface, carried by its placement, in place of the surface drawn
/// for the body of its name in the payload at `payload`, and binds the fine model at `model` to
/// the payload that results. Answers how many surfaces it put.
pub fn graft(payload: &Path, model: &Path, pieces: &[(&str, &str, Placement)]) -> Result<usize> {
    let mut host = Payload::read(payload)?;
    let mut grafted = 0;
    for (name, file, placement) in pieces {
        let printed = Payload::read(Path::new(file)).with_context(|| format!("reading {file}"))?;
        ensure!(printed.meshes.len() == 1, "{file} draws one surface");
        let surface = printed.meshes[0].clone().carried(&frame(placement));
        for target in host.meshes.iter_mut().filter(|mesh| mesh.name() == *name || mesh.body() == *name) {
            for (key, value) in &surface.arrays {
                target.arrays.insert(key.clone(), value.clone());
            }
            match surface.meta.get("face_sources") {
                Some(sources) => target.meta["face_sources"] = sources.clone(),
                None => {
                    target
                        .meta
                        .as_object_mut()
                        .context("a payload entry is an object")?
                        .remove("face_sources");
                }
            }
            grafted += 1;
        }
    }
    host.write(payload)?;
    hsm_model_export::model::bind(model, payload)?;
    Ok(grafted)
}
