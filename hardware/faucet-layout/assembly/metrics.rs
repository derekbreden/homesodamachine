//! What the assembly measures on the paths and hulls it builds: a centreline's length, to cut each
//! tube by, and a hull's area, centroid and perimeter.
use anyhow::Result;
use hsm_kernel::*;

#[allow(clippy::too_many_arguments)]
fn simpson(f: &impl Fn(f64) -> f64, a: f64, b: f64, fa: f64, fm: f64, fb: f64, whole: f64, tolerance: f64, depth: usize) -> f64 {
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

/// A curve's length, integrated adaptively from 64 seeds along it, so no one span has to find
/// every change in an interpolated curve's curvature.
fn curve_length(curve: &Spline) -> f64 {
    let (start, end) = curve.range();
    let speed = |t| curve.derivative(t).norm();
    (0..64)
        .map(|i| {
            let a = start + (end - start) * i as f64 / 64.0;
            let b = start + (end - start) * (i + 1) as f64 / 64.0;
            let (fa, fm, fb) = (speed(a), speed((a + b) / 2.0), speed(b));
            simpson(&speed, a, b, fa, fm, fb, (b - a) * (fa + 4.0 * fm + fb) / 6.0, 1e-9 / 64.0, 16)
        })
        .sum()
}

/// The length along `path`.
pub fn length(path: &Path) -> f64 {
    path.legs
        .iter()
        .map(|leg| match *leg {
            Leg::Line { a, b } => (b - a).norm(),
            Leg::Arc { a, c, turn, .. } => (a - c).norm() * turn,
            Leg::Curve { k, .. } => curve_length(&path.curves[k]),
        })
        .sum()
}

/// The hull round `circles`: its area, its centroid and its perimeter.
pub fn hull(circles: &[Wrapped]) -> Result<(f64, V2, f64)> {
    let (mut area, mut mx, mut my, mut perimeter) = (0.0, 0.0, 0.0, 0.0);
    for edge in hull_edges(circles)? {
        match edge {
            HullEdge::Line { a, b } => {
                area += (a.x * b.y - b.x * a.y) / 2.0;
                mx += (b.y - a.y) * (a.x * a.x + a.x * b.x + b.x * b.x) / 6.0;
                my -= (b.x - a.x) * (a.y * a.y + a.y * b.y + b.y * b.y) / 6.0;
                perimeter += (b - a).norm();
            }
            HullEdge::Arc { c, r, t0, t1, .. } => {
                let dt = t1 - t0;
                let ds = t1.sin() - t0.sin();
                let dc = t1.cos() - t0.cos();
                let ds2 = (2.0 * t1).sin() - (2.0 * t0).sin();
                let ds3 = (t1.sin() - t1.sin().powi(3) / 3.0) - (t0.sin() - t0.sin().powi(3) / 3.0);
                let dc3 = (-t1.cos() + t1.cos().powi(3) / 3.0) - (-t0.cos() + t0.cos().powi(3) / 3.0);
                area += (r * c.x * ds - r * c.y * dc + r * r * dt) / 2.0;
                mx += r * (c.x * c.x * ds + 2.0 * c.x * r * (dt / 2.0 + ds2 / 4.0) + r * r * ds3) / 2.0;
                my += r * (-c.y * c.y * dc + 2.0 * c.y * r * (dt / 2.0 - ds2 / 4.0) + r * r * dc3) / 2.0;
                perimeter += r * dt;
            }
        }
    }
    Ok((area, v2(mx / area, my / area), perimeter))
}
