//! A seam-enforcer strip on one exterior plane: the facets the strip crosses are split along its
//! two edges, without moving the surface, and the facets inside it on that plane are painted.

use crate::project::Paint;
use anyhow::{bail, Result};
use serde_json::{json, Value};
use std::collections::BTreeMap;

fn half(polygon: &[[f64; 3]], axis: usize, coordinate: f64, sign: f64) -> Vec<[f64; 3]> {
    let mut result = Vec::new();
    let mut previous = polygon[polygon.len() - 1];
    let mut previous_in = sign * (previous[axis] - coordinate) >= -1e-10;
    for &current in polygon {
        let current_in = sign * (current[axis] - coordinate) >= -1e-10;
        if current_in != previous_in {
            let fraction = (coordinate - previous[axis]) / (current[axis] - previous[axis]);
            let mut point = [0, 1, 2].map(|k| previous[k] + fraction * (current[k] - previous[k]));
            point[axis] = coordinate;
            result.push(point);
        }
        if current_in {
            result.push(current);
        }
        previous = current;
        previous_in = current_in;
    }
    result
}

fn cross_length(t: &[[f64; 3]; 3]) -> f64 {
    let (u, w) = ([0, 1, 2].map(|k| t[1][k] - t[0][k]), [0, 1, 2].map(|k| t[2][k] - t[0][k]));
    let c = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]];
    (c[0] * c[0] + c[1] * c[1] + c[2] * c[2]).sqrt()
}

/// The split mesh (vertices sorted by their rounded coordinates, as numpy's unique sorts them),
/// each facet's paint, and the record of the strip.
pub fn strip(vertices: &[[f64; 3]], faces: &[[usize; 3]], declaration: &Value) -> Result<(Vec<[f64; 3]>, Vec<[usize; 3]>, Vec<Option<Paint>>, Value)> {
    let original: Vec<[[f64; 3]; 3]> = faces.iter().map(|f| f.map(|i| vertices[i])).collect();
    let mut triangles = original.clone();
    let mut parents: Vec<usize> = (0..faces.len()).collect();
    let axis = "xyz".find(declaration["axis"].as_str().unwrap_or("x")).unwrap_or(0);
    let center = declaration["center_mm"].as_f64().unwrap_or(0.0);
    let half_width = declaration["half_width_mm"].as_f64().unwrap_or(0.0);
    for coordinate in [center - half_width, center + half_width] {
        let (mut result, mut ids) = (Vec::new(), Vec::new());
        for (triangle, &parent) in triangles.iter().zip(&parents) {
            let lo = triangle.iter().map(|p| p[axis]).fold(f64::INFINITY, f64::min);
            let hi = triangle.iter().map(|p| p[axis]).fold(f64::NEG_INFINITY, f64::max);
            if lo >= coordinate - 1e-10 || hi <= coordinate + 1e-10 {
                result.push(*triangle);
                ids.push(parent);
                continue;
            }
            for sign in [-1.0, 1.0] {
                let polygon = half(triangle, axis, coordinate, sign);
                for i in 1..polygon.len().saturating_sub(1) {
                    let child = [polygon[0], polygon[i], polygon[i + 1]];
                    if cross_length(&child) > 1e-10 {
                        result.push(child);
                        ids.push(parent);
                    }
                }
            }
        }
        triangles = result;
        parents = ids;
    }
    // np.unique(np.round(corners, 9), axis=0): rows sorted by value, x then y then z.
    // + 0.0: -0.0 and 0.0 are one point, as numpy's comparison makes them.
    let round9 = |v: f64| (v * 1e9).round() / 1e9 + 0.0;
    let corners: Vec<[f64; 3]> = triangles.iter().flat_map(|t| t.map(|p| p.map(round9))).collect();
    let mut sorted: Vec<[f64; 3]> = corners.clone();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());
    sorted.dedup();
    let keys: BTreeMap<[u64; 3], usize> = sorted.iter().enumerate().map(|(i, p)| (p.map(f64::to_bits), i)).collect();
    let flat: Vec<usize> = corners.iter().map(|p| keys[&p.map(f64::to_bits)]).collect();
    let split_faces: Vec<[usize; 3]> = flat.chunks(3).map(|c| [c[0], c[1], c[2]]).collect();
    let face_axis = "xyz".find(declaration["face_axis"].as_str().unwrap_or("x")).unwrap_or(0);
    let plane = declaration["face_coordinate_mm"].as_f64().unwrap_or(0.0);
    let face_sign = declaration["face_sign"].as_f64().unwrap_or(1.0);
    let mut paint = Vec::with_capacity(split_faces.len());
    let mut painted = 0usize;
    let mut plane_error: f64 = 0.0;
    let mut area = vec![0.0; original.len()];
    for (k, f) in split_faces.iter().enumerate() {
        let t = f.map(|i| sorted[i]);
        let u = [0, 1, 2].map(|j| t[1][j] - t[0][j]);
        let w = [0, 1, 2].map(|j| t[2][j] - t[0][j]);
        let normal = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]];
        let norm = (normal[0].powi(2) + normal[1].powi(2) + normal[2].powi(2)).sqrt();
        let on_plane = t.iter().map(|p| (p[face_axis] - plane).abs()).fold(0.0, f64::max) < 0.001;
        let lo = t.iter().map(|p| p[axis]).fold(f64::INFINITY, f64::min);
        let hi = t.iter().map(|p| p[axis]).fold(f64::NEG_INFINITY, f64::max);
        let selected = on_plane && lo >= center - half_width - 1e-8 && hi <= center + half_width + 1e-8
            && normal[face_axis] * face_sign > 0.99 * norm;
        if selected {
            painted += 1;
        }
        paint.push(selected.then(|| vec![("paint_seam".to_string(), "4".to_string())]));
        let parent = parents[k];
        let src = original[parent];
        let su = [0, 1, 2].map(|j| src[1][j] - src[0][j]);
        let sw = [0, 1, 2].map(|j| src[2][j] - src[0][j]);
        let sn = [su[1] * sw[2] - su[2] * sw[1], su[2] * sw[0] - su[0] * sw[2], su[0] * sw[1] - su[1] * sw[0]];
        let sl = (sn[0].powi(2) + sn[1].powi(2) + sn[2].powi(2)).sqrt();
        for p in t {
            let d = ((p[0] - src[0][0]) * sn[0] + (p[1] - src[0][1]) * sn[1] + (p[2] - src[0][2]) * sn[2]) / sl;
            plane_error = plane_error.max(d.abs());
        }
        area[parent] += norm / 2.0;
    }
    let area_error = original.iter().enumerate().map(|(i, t)| (area[i] - cross_length(t) / 2.0).abs()).fold(0.0, f64::max);
    if painted == 0 {
        bail!("seam strip misses the declared exterior plane: {declaration}");
    }
    let mut record = declaration.clone();
    if let Value::Object(m) = &mut record {
        m.insert("source_facets".into(), json!(faces.len()));
        m.insert("project_facets".into(), json!(split_faces.len()));
        m.insert("painted_facets".into(), json!(painted));
        m.insert("maximum_source_plane_error_mm".into(), json!(plane_error));
        m.insert("maximum_source_facet_area_error_mm2".into(), json!(area_error));
    }
    Ok((sorted, split_faces, paint, record))
}
