//! The arithmetic of points and directions the mounts are worked in, term by term in the order
//! the layout's own frames work it.
use crate::P3;

pub fn add(a: P3, b: P3) -> P3 {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}

pub fn sub(a: P3, b: P3) -> P3 {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

pub fn mul(a: P3, s: f64) -> P3 {
    [a[0] * s, a[1] * s, a[2] * s]
}

pub fn dot(a: P3, b: P3) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

pub fn cross(a: P3, b: P3) -> P3 {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}

pub fn norm(a: P3) -> f64 {
    dot(a, a).sqrt()
}

/// `a` scaled to unit length.
pub fn unit(a: P3) -> P3 {
    mul(a, 1. / norm(a))
}

/// The distance between two points.
pub fn dist(a: P3, b: P3) -> f64 {
    (a[0] - b[0]).abs().hypot(a[1] - b[1]).hypot(a[2] - b[2])
}

/// Each axis's least and greatest over `points`.
pub fn bounds(points: &[P3]) -> [P3; 2] {
    let mut lo = [f64::INFINITY; 3];
    let mut hi = [f64::NEG_INFINITY; 3];
    for p in points {
        for i in 0..3 {
            lo[i] = lo[i].min(p[i]);
            hi[i] = hi[i].max(p[i]);
        }
    }
    [lo, hi]
}

/// Degrees to radians, rounded as the layout's recipes round them.
pub fn radians(degrees: f64) -> f64 {
    degrees * std::f64::consts::PI / 180.
}
