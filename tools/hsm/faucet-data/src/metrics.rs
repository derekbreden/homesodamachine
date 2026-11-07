//! The faucet's scalar dimensions, measured on the paths and circle hulls the assembly's readers
//! name in JSON: each path's length and each hull's area, centroid and perimeter.
use anyhow::{Context, Result, anyhow, bail, ensure};
use hsm_kernel::part::Numbers;
use hsm_kernel::*;
use serde_json::{Map, Value, json};

/// The numbers in a JSON list, if it is one of numbers only.
fn floats(v: &Value) -> Option<Vec<f64>> {
    v.as_array()?.iter().map(Value::as_f64).collect()
}

/// A JSON point `[x, y, z]`.
fn point(v: &Value) -> Result<V3> {
    match floats(v).as_deref() {
        Some([x, y, z]) => Ok(v3(*x, *y, *z)),
        _ => Err(anyhow!("{v} is not a point")),
    }
}

/// A JSON list.
fn rows(v: &Value) -> Result<&Vec<Value>> {
    v.as_array().ok_or_else(|| anyhow!("{v} is not a list"))
}

/// Circles `[[x, y, r], ...]` as hull entities.
fn circles(v: &Value) -> Result<Vec<Wrapped>> {
    rows(v)?
        .iter()
        .map(|c| match floats(c).as_deref() {
            Some([x, y, r]) => Ok(Wrapped::Circle { c: v2(*x, *y), r: *r }),
            _ => Err(anyhow!("{c} is not a circle")),
        })
        .collect()
}

fn simpson(f: &impl Fn(f64) -> f64, a: f64, b: f64, fa: f64, fm: f64, fb: f64,
           whole: f64, tolerance: f64, depth: usize) -> f64 {
    let mid = (a + b) / 2.0;
    let left_mid = f((a + mid) / 2.0);
    let right_mid = f((mid + b) / 2.0);
    let left = (mid - a) * (fa + 4.0 * left_mid + fm) / 6.0;
    let right = (b - mid) * (fm + 4.0 * right_mid + fb) / 6.0;
    let delta = left + right - whole;
    if depth == 0 || delta.abs() <= 15.0 * tolerance {
        left + right + delta / 15.0
    } else {
        simpson(f, a, mid, fa, left_mid, fm, left, tolerance / 2.0, depth - 1)
            + simpson(f, mid, b, fm, right_mid, fb, right, tolerance / 2.0, depth - 1)
    }
}

fn curve_length(curve: &Spline) -> f64 {
    let (start, end) = curve.range();
    let speed = |t| curve.derivative(t).norm();
    // Seed the integration across the curve rather than asking one triplet to
    // discover every change in an interpolated curve's curvature.
    (0..64).map(|i| {
        let a = start + (end - start) * i as f64 / 64.0;
        let b = start + (end - start) * (i + 1) as f64 / 64.0;
        let (fa, fm, fb) = (speed(a), speed((a + b) / 2.0), speed(b));
        simpson(&speed, a, b, fa, fm, fb, (b - a) * (fa + 4.0 * fm + fb) / 6.0,
                1e-9 / 64.0, 16)
    }).sum()
}

fn path_length(path: &Path) -> f64 {
    path.legs.iter().map(|leg| match *leg {
        Leg::Line { a, b } => (b - a).norm(),
        Leg::Arc { a, c, turn, .. } => (a - c).norm() * turn,
        Leg::Curve { k, .. } => curve_length(&path.curves[k]),
    }).sum()
}

fn hull_metrics(entities: &[Wrapped]) -> Result<Value> {
    let (mut area, mut mx, mut my, mut perimeter) = (0.0, 0.0, 0.0, 0.0);
    for edge in hull_edges(entities)? {
        match edge {
            HullEdge::Line { a, b } => {
                area += (a.x * b.y - b.x * a.y) / 2.0;
                mx += (b.y - a.y) * (a.x*a.x + a.x*b.x + b.x*b.x) / 6.0;
                my -= (b.x - a.x) * (a.y*a.y + a.y*b.y + b.y*b.y) / 6.0;
                perimeter += (b - a).norm();
            }
            HullEdge::Arc { c, r, t0, t1, .. } => {
                let dt = t1 - t0;
                let ds = t1.sin() - t0.sin();
                let dc = t1.cos() - t0.cos();
                let ds2 = (2.0*t1).sin() - (2.0*t0).sin();
                let ds3 = (t1.sin() - t1.sin().powi(3)/3.0)
                    - (t0.sin() - t0.sin().powi(3)/3.0);
                let dc3 = (-t1.cos() + t1.cos().powi(3)/3.0)
                    - (-t0.cos() + t0.cos().powi(3)/3.0);
                area += (r*c.x*ds - r*c.y*dc + r*r*dt) / 2.0;
                mx += r * (c.x*c.x*ds + 2.0*c.x*r*(dt/2.0 + ds2/4.0) + r*r*ds3) / 2.0;
                my += r * (-c.y*c.y*dc + 2.0*c.y*r*(dt/2.0 - ds2/4.0) + r*r*dc3) / 2.0;
                perimeter += r * dt;
            }
        }
    }
    Ok(json!({"area":area, "center":[mx/area, my/area], "perimeter":perimeter}))
}

/// A centreline from JSON legs — `{"line": [a, b]}`, `{"arc": [a, mid, b]}`, `{"spline": points}`
/// and `{"hermite": [a, b, ta, tb]}` — each leg from where the last one ends.
fn path(legs: &Value) -> Result<Path> {
    let mut path: Option<Path> = None;
    for leg in rows(legs)? {
        let (kind, pts) = leg.as_object().and_then(|o| o.iter().next()).ok_or_else(|| anyhow!("{leg} is not a leg"))?;
        let pts = rows(pts)?.iter().map(point).collect::<Result<Vec<_>>>()?;
        let start = *pts.first().ok_or_else(|| anyhow!("{leg} has no points"))?;
        let p = path.take().unwrap_or_else(|| Path::new(start));
        ensure!((p.at() - start).norm() < 1e-7, "a {kind} leg from {start:?}, where the path ends at {:?}", p.at());
        path = Some(match (kind.as_str(), &pts[..]) {
            ("line", [_, b]) => p.line_to(*b),
            ("arc", [_, mid, b]) => p.arc_through(*mid, *b)?,
            ("spline", _) => p.spline_through(&pts)?,
            ("hermite", [_, b, ta, tb]) => p.spline_to(*b, *ta, *tb)?,
            _ => bail!("{leg} is not a leg"),
        });
    }
    path.context("a path of no legs")
}

pub fn measure(n: &Numbers) -> Result<Value> {
    let mut lengths = Map::new();
    for (name, legs) in n.get("paths")?.as_object().ok_or_else(|| anyhow!("paths is an object"))? {
        lengths.insert(name.clone(), json!(path_length(&path(legs)?)));
    }
    let mut hulls = Map::new();
    for (name, rows) in n.get("hulls")?.as_object().ok_or_else(|| anyhow!("hulls is an object"))? {
        hulls.insert(name.clone(), hull_metrics(&circles(rows)?)?);
    }
    Ok(json!({"lengths":lengths, "hulls":hulls}))
}
