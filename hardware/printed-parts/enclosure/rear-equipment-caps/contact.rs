//! Sample the fitted cap roofs for the same bounded contact mapping used on the faucet.

use anyhow::{Context, Result, ensure};
use hsm_print_prep::project::Object;
use hsm_print_prep::{apply, mesh};
use serde_json::{Value, json};

type Point = [f64; 3];
type Triangle = [Point; 3];

fn difference(a: Point, b: Point) -> Point {
    [0, 1, 2].map(|i| a[i] - b[i])
}

fn distance_xy(a: Point, b: Point) -> f64 {
    (a[0] - b[0]).powi(2) + (a[1] - b[1]).powi(2)
}

fn cross_xy(a: Point, b: Point) -> f64 {
    a[0] * b[1] - a[1] * b[0]
}

fn nearest_edge(p: Point, a: Point, b: Point) -> Point {
    let edge = difference(b, a);
    let d = difference(p, a);
    let t = ((d[0] * edge[0] + d[1] * edge[1]) / distance_xy(a, b)).clamp(0., 1.);
    [0, 1, 2].map(|axis| a[axis] + t * edge[axis])
}

struct RoofTriangle {
    points: Triangle,
    u: Point,
    v: Point,
    determinant: f64,
}

impl RoofTriangle {
    fn downward(points: Triangle) -> Option<Self> {
        let [a, b, c] = points;
        let u = difference(b, a);
        let v = difference(c, a);
        let determinant = cross_xy(u, v);
        let slope = (u[1] * v[2] - u[2] * v[1]).hypot(u[2] * v[0] - u[0] * v[2]);
        (determinant < -1e-9
            && slope > -determinant * 0.5_f64.to_radians().tan()
            && slope < -determinant)
            .then_some(Self {
                points,
                u,
                v,
                determinant,
            })
    }

    /// Interpolate the mesh roof and extend it along the closest boundary where the roof ends.
    fn nearest_height(&self, p: Point) -> (f64, f64) {
        let [a, b, c] = self.points;
        let d = difference(p, a);
        let s = cross_xy(d, self.v) / self.determinant;
        let t = cross_xy(self.u, d) / self.determinant;
        if s >= 0. && t >= 0. && s + t <= 1. {
            return (0., a[2] + s * self.u[2] + t * self.v[2]);
        }
        [(a, b), (b, c), (c, a)]
            .into_iter()
            .map(|(u, v)| {
                let q = nearest_edge(p, u, v);
                (distance_xy(p, q), q[2])
            })
            .min_by(compare)
            .expect("a triangle has edges")
    }
}

fn compare(a: &(f64, f64), b: &(f64, f64)) -> std::cmp::Ordering {
    a.0.total_cmp(&b.0).then(a.1.total_cmp(&b.1))
}

/// Fit the motion map to the actual triangles in this cap's source-coordinate roof selection.
pub fn specification(object: &Object, selection: &Value, defaults: &Value) -> Result<Value> {
    let [low, high]: [Point; 2] = serde_json::from_value(selection["bounds_source_mm"].clone())?;
    ensure!(
        (0..3).all(|axis| low[axis] < high[axis]),
        "invalid cap roof bounds"
    );
    let to_plate = |p: Point| {
        let r = apply(&object.rotation, difference(p, object.source_center));
        [0, 1, 2].map(|axis| r[axis] + object.translation[axis])
    };
    let source: Vec<Point> = object
        .vertices
        .iter()
        .map(|p| [0, 1, 2].map(|axis| p[axis] + object.source_center[axis]))
        .collect();
    let triangles: Vec<RoofTriangle> = object
        .faces
        .iter()
        .filter_map(|face| {
            let points = face.map(|i| source[i]);
            let (a, b) = mesh::bounds(&points);
            (0..3)
                .all(|axis| a[axis] <= high[axis] && b[axis] >= low[axis])
                .then(|| RoofTriangle::downward(points.map(to_plate)))
                .flatten()
        })
        .collect();
    ensure!(
        !triangles.is_empty(),
        "{}: no inclined roof in its contact selection",
        object.name
    );
    let corners = [
        to_plate(low),
        to_plate([low[0], high[1], low[2]]),
        to_plate([high[0], low[1], low[2]]),
        to_plate(high),
    ];
    let (a, b) = mesh::bounds(&corners);
    let bounds = [[a[0], a[1]], [b[0], b[1]]];
    let step = defaults["maximum_gcode_segment_mm"]
        .as_f64()
        .context("contact sampling step")?;
    ensure!(step > 0., "contact sampling step must be positive");
    let [nx, ny] = [0, 1].map(|axis| ((b[axis] - a[axis]) / step).ceil() as usize + 1);
    let mut heights = Vec::with_capacity(nx * ny);
    for iy in 0..ny {
        let y = a[1] + (b[1] - a[1]) * iy as f64 / (ny - 1) as f64;
        for ix in 0..nx {
            let x = a[0] + (b[0] - a[0]) * ix as f64 / (nx - 1) as f64;
            let (_, z) = triangles
                .iter()
                .map(|face| face.nearest_height([x, y, 0.]))
                .min_by(compare)
                .expect("the roof has triangles");
            heights.push(z);
        }
    }
    let mut parameters = defaults.clone();
    let phase = selection["band_phase_source_mm"]
        .as_f64()
        .context("cap contact band phase")?;
    parameters["band_phase_mm"] = json!(to_plate([0., 0., phase])[2]);
    Ok(
        json!({"object": object.name, "selection": selection, "sampled_roof_triangles": triangles.len(),
        "bounds_mm": bounds, "edge_blend_mm": selection["edge_blend_mm"], "parameters": parameters,
        "height_field": {"bounds_mm": bounds, "samples": [nx, ny], "z_mm": heights}}),
    )
}
