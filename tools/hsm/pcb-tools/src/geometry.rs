//! PCB geometry measures trace approaches, copper outlines and source model placements.
use crate::circuit::{Cad, Pad, Point, Vector};
pub type Bounds = [f64; 4];
pub type Segment = (Point, Point);

pub fn point_segment(p: Point, a: Point, b: Point) -> (f64, Point) {
    let (dx, dy) = (b.x - a.x, b.y - a.y);
    let length = dx * dx + dy * dy;
    let t = if length == 0.0 {
        0.0
    } else {
        ((p.x - a.x) * dx + (p.y - a.y) * dy) / length
    }
    .clamp(0.0, 1.0);
    let q = a.mix(b, t);
    (p.distance(q), q)
}
pub fn segment_distance(a: Point, b: Point, c: Point, d: Point) -> (f64, Point) {
    let cross =
        |o: Point, a: Point, b: Point| (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
    let (d1, d2, d3, d4) = (
        cross(c, d, a),
        cross(c, d, b),
        cross(a, b, c),
        cross(a, b, d),
    );
    if (d1 > 0.0) != (d2 > 0.0) && (d3 > 0.0) != (d4 > 0.0) {
        return (0.0, c.mix(d, d3 / (d3 - d4)));
    }
    let mut best = (f64::INFINITY, a);
    for p in [c, d] {
        let candidate = point_segment(p, a, b);
        if candidate.0 < best.0 {
            best = candidate;
        }
    }
    for p in [a, b] {
        let candidate = point_segment(p, c, d);
        if candidate.0 < best.0 {
            best = (candidate.0, p);
        }
    }
    best
}
pub fn rect_distance(a: Point, b: Point, c: Point, half: [f64; 2], rotation: f64) -> f64 {
    let (sin, cos) = (-rotation.to_radians()).sin_cos();
    let samples = 24usize.max((a.distance(b) / 0.35) as usize + 1);
    (0..=samples)
        .map(|i| {
            let p = a.mix(b, i as f64 / samples as f64);
            let (x, y) = (p.x - c.x, p.y - c.y);
            ((cos * x - sin * y).abs() - half[0])
                .max(0.0)
                .hypot(((sin * x + cos * y).abs() - half[1]).max(0.0))
        })
        .fold(f64::INFINITY, f64::min)
}
#[derive(Clone)]
pub enum Shape {
    Circle(Point, f64),
    Rect(Point, [f64; 2], f64),
    Capsule(Point, Point, f64),
}
impl Shape {
    pub fn pad(p: &Pad, plated: bool) -> Self {
        let c = p.point();
        let rotation = p.ccw_rotation.unwrap_or(0.0);
        if !plated && matches!(p.shape.as_str(), "rect" | "rotated_rect") {
            return Self::Rect(
                c,
                [p.width.unwrap_or(0.0), p.height.unwrap_or(0.0)],
                rotation,
            );
        }
        if p.shape == "circle" {
            return Self::Circle(
                c,
                if plated {
                    p.outer_diameter.unwrap_or(0.0) / 2.0
                } else {
                    p.radius.unwrap_or_else(|| p.width.unwrap_or(0.0) / 2.0)
                },
            );
        }
        let (w, h) = if plated {
            (p.outer_width.unwrap_or(0.0), p.outer_height.unwrap_or(0.0))
        } else {
            (p.width.unwrap_or(0.0), p.height.unwrap_or(0.0))
        };
        let radius = if plated {
            w.min(h) / 2.0
        } else {
            p.radius.unwrap_or(w.min(h) / 2.0)
        };
        let half = ((w.max(h) - 2.0 * radius) / 2.0).max(0.0);
        let (sin, cos) = ((if h >= w { 90.0 } else { 0.0 }) + rotation)
            .to_radians()
            .sin_cos();
        Self::Capsule(
            Point {
                x: c.x - cos * half,
                y: c.y - sin * half,
            },
            Point {
                x: c.x + cos * half,
                y: c.y + sin * half,
            },
            radius,
        )
    }
    pub fn bounds(&self) -> Bounds {
        match self {
            Self::Circle(c, r) => [c.x - r, c.x + r, c.y - r, c.y + r],
            Self::Rect(c, [w, h], _) => {
                let radius = w.hypot(*h) / 2.0;
                [c.x - radius, c.x + radius, c.y - radius, c.y + radius]
            }
            Self::Capsule(a, b, r) => [
                a.x.min(b.x) - r,
                a.x.max(b.x) + r,
                a.y.min(b.y) - r,
                a.y.max(b.y) + r,
            ],
        }
    }
    pub fn inside(&self, p: Point) -> f64 {
        match self {
            Self::Circle(c, r) => r - c.distance(p),
            Self::Capsule(a, b, r) => r - point_segment(p, *a, *b).0,
            Self::Rect(c, [w, h], rotation) => {
                let (sin, cos) = rotation.to_radians().sin_cos();
                let (x, y) = (p.x - c.x, p.y - c.y);
                let (dx, dy) = (
                    (x * cos + y * sin).abs() - w / 2.0,
                    (-x * sin + y * cos).abs() - h / 2.0,
                );
                -(dx.max(0.0).hypot(dy.max(0.0)) + dx.max(dy).min(0.0))
            }
        }
    }
    pub fn penetration(&self, a: Point, b: Point, r: f64) -> f64 {
        let count = (a.distance(b) / 0.03).ceil().max(1.0) as usize;
        (0..=count)
            .map(|i| self.inside(a.mix(b, i as f64 / count as f64)) + r)
            .fold(f64::NEG_INFINITY, f64::max)
    }
}
pub fn bounds(segments: &[Segment], r: f64, fallback: Point) -> Bounds {
    if segments.is_empty() {
        return [fallback.x, fallback.x, fallback.y, fallback.y];
    }
    let mut out = [
        f64::INFINITY,
        f64::NEG_INFINITY,
        f64::INFINITY,
        f64::NEG_INFINITY,
    ];
    for (a, b) in segments {
        for p in [a, b] {
            out[0] = out[0].min(p.x - r);
            out[1] = out[1].max(p.x + r);
            out[2] = out[2].min(p.y - r);
            out[3] = out[3].max(p.y + r);
        }
    }
    out
}
pub fn far(a: Bounds, b: Bounds, margin: f64) -> bool {
    a[0] > b[1] + margin || b[0] > a[1] + margin || a[2] > b[3] + margin || b[2] > a[3] + margin
}
pub fn rotate(mut v: [f64; 3], rotation: Vector, bottom: bool) -> [f64; 3] {
    for (axis, degrees) in [rotation.x, rotation.y, rotation.z].into_iter().enumerate() {
        let (s, c) = degrees.to_radians().sin_cos();
        let [x, y, z] = v;
        v = match axis {
            0 => [x, y * c - z * s, y * s + z * c],
            1 => [x * c + z * s, y, -x * s + z * c],
            _ => [x * c - y * s, x * s + y * c, z],
        };
    }
    if bottom {
        v[1] = -v[1];
        v[2] = -v[2];
    }
    v
}
pub fn place(v: [f64; 3], cad: &Cad, bottom: bool) -> [f64; 3] {
    let origin = cad.model_origin_position.array();
    let local = std::array::from_fn(|i| v[i] - origin[i]);
    let turned = rotate(local, cad.rotation, bottom);
    let position = cad.position.array();
    std::array::from_fn(|i| turned[i] + position[i])
}
