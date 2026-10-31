//! The one triangulation rule.
//!
//! EVERY CURVE IS CUT INTO SEGMENTS BY ONE RULE. A circle of radius r gets `ring_count(r)`
//! points at fixed angles about its axis, measured from a frame that depends on the axis and
//! nothing else. A boss and the bore it sits in, a cutter and the wall it trims, two parts that
//! touch on a cylinder: wherever two surfaces coincide they were cut into the same points, so a
//! boolean between them leaves no sliver.
//!
//! No chord strays more than `LINEAR` from the true curve and no segment turns more than
//! `ANGULAR`. Counts round up to a multiple of 8, so every ring has its points on the axes of
//! its own frame and its bounding box is exact.
//!
//! Every vertex a builder makes lands on one grid, `GRID` apart (`snap`): two computations of
//! one point that differ in their last bits come out as the same point.
//!
//! These are meshcad's numbers (`hardware/scripts/meshcad/rule.py`), so a surface cut here
//! and the same surface cut there land on the same points.
use crate::math::{PI, TAU, V3, acos, atan2, cos, sin, v3};

/// mm, the chord's largest distance from the curve.
pub const LINEAR: f64 = 0.005;
/// rad, the largest turn between two segments.
pub const ANGULAR: f64 = 0.05;
/// mm, 2^-30: the spacing every built vertex is snapped to.
pub const GRID: f64 = 1.0 / 1073741824.0;
/// mm, the shortest edge and thinnest sliver a file's triangles keep.
pub const TOLERANCE: f64 = 1e-5;

pub fn snap(x: f64) -> f64 {
    (x / GRID).round_ties_even() * GRID
}

pub fn snap3(p: V3) -> V3 {
    v3(snap(p.x), snap(p.y), snap(p.z))
}

/// Segments in a full circle of radius `r`.
pub fn ring_count(r: f64) -> usize {
    if r <= 1e-9 {
        return 1;
    }
    let step = if r <= LINEAR {
        ANGULAR
    } else {
        ANGULAR.min(2.0 * acos(1.0 - LINEAR / r))
    };
    8 * (2.0 * PI / step / 8.0 - 1e-9).ceil() as usize
}

/// `d` or `-d`, whichever points into the positive half: both directions of one axis share a
/// frame, so a bore drilled down meets a boss extruded up on the same points.
pub fn canonical_axis(d: V3) -> V3 {
    let d = d.unit();
    for c in [d.x, d.y, d.z] {
        if c.abs() > 1e-6 {
            return if c > 0.0 { d } else { -d };
        }
    }
    d
}

/// (axis, x, y): the canonical axis of `d` and the frame its rings are measured in.
pub fn axis_frame(d: V3) -> (V3, V3, V3) {
    let d = canonical_axis(d);
    let w = if d.z.abs() < 0.9 { V3::Z } else { V3::X };
    let x = (w - d * w.dot(d)).unit();
    (d, x, d.cross(x))
}

/// `axis_frame` turned so counterclockwise is about `normal` itself.
pub fn plane_frame(normal: V3) -> (V3, V3, V3) {
    let (d, x, y) = axis_frame(normal);
    if d.dot(normal) < 0.0 { (-d, x, -y) } else { (d, x, y) }
}

/// Angles of a whole ring of radius `r` about its canonical frame.
pub fn ring_angles(r: f64) -> Vec<f64> {
    let n = ring_count(r);
    let step = 2.0 * PI / n as f64;
    (0..n).map(|k| k as f64 * step).collect()
}

/// The ends `a0` < `a1` of an arc of radius `r`, with the rule's angles strictly between them.
pub fn arc_angles(r: f64, a0: f64, a1: f64) -> Vec<f64> {
    let n = ring_count(r);
    let step = 2.0 * PI / n as f64;
    let k0 = (a0 / step).floor() as i64 + 1;
    let k1 = (a1 / step).ceil() as i64 - 1;
    let mut out = vec![a0];
    for k in k0..=k1 {
        let a = k as f64 * step;
        if a - a0 > 0.25 * step && a1 - a > 0.25 * step {
            out.push(a);
        }
    }
    out.push(a1);
    out
}

fn on_ring(center: V3, x: V3, y: V3, r: f64, a: f64) -> V3 {
    center + (x * cos(a) + y * sin(a)) * r
}

/// The whole circle on the rule's angles, counterclockwise about its canonical axis.
pub fn circle_points(center: V3, axis: V3, r: f64) -> Vec<V3> {
    let (_, x, y) = axis_frame(axis);
    ring_angles(r)
        .into_iter()
        .map(|a| on_ring(center, x, y, r, a))
        .collect()
}

/// The arc from `start` to `end` turning counterclockwise about `ccw_about`, on the rule's
/// angles, beginning at `start` and ending at `end` exactly. `start == end` is the whole turn.
pub fn arc_points(center: V3, axis: V3, r: f64, start: V3, end: V3, ccw_about: V3) -> Vec<V3> {
    let (d, x, y) = axis_frame(axis);
    let sense = if ccw_about.dot(d) > 0.0 { 1.0 } else { -1.0 };
    let (v0, v1) = (start - center, end - center);
    let mut t0 = atan2(v0.dot(y), v0.dot(x));
    let mut t1 = atan2(v1.dot(y), v1.dot(x));
    if sense < 0.0 {
        std::mem::swap(&mut t0, &mut t1);
    }
    if t1 <= t0 + 1e-12 {
        t1 += TAU;
    }
    let mut pts: Vec<V3> = arc_angles(r, t0, t1)
        .into_iter()
        .map(|a| on_ring(center, x, y, r, a))
        .collect();
    if sense < 0.0 {
        pts.reverse();
    }
    let last = pts.len() - 1;
    pts[0] = start;
    pts[last] = end;
    pts
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn counts_are_multiples_of_eight_and_hold_the_chord() {
        for r in [0.001, 0.005, 0.1, 1.0, 2.1, 10.0, 63.5, 500.0] {
            let n = ring_count(r);
            assert_eq!(n % 8, 0, "r {r}");
            let sag = r * (1.0 - cos(PI / n as f64));
            assert!(sag <= LINEAR + 1e-12, "r {r} n {n} sagitta {sag}");
            assert!(2.0 * PI / n as f64 <= ANGULAR + 1e-12);
        }
        assert_eq!(ring_count(0.0), 1);
    }

    #[test]
    fn both_senses_of_an_axis_share_a_frame() {
        let (a, xa, ya) = axis_frame(v3(0.0, 0.0, -1.0));
        let (b, xb, yb) = axis_frame(V3::Z);
        assert_eq!((a, xa, ya), (b, xb, yb));
    }

    #[test]
    fn an_arc_keeps_its_ends_and_the_ring_angles_between() {
        let c = V3::ZERO;
        let r = 10.0;
        let ring = circle_points(c, V3::Z, r);
        let arc = arc_points(c, V3::Z, r, v3(r, 0.0, 0.0), v3(0.0, r, 0.0), V3::Z);
        assert_eq!(arc[0], v3(r, 0.0, 0.0));
        assert_eq!(*arc.last().unwrap(), v3(0.0, r, 0.0));
        for p in &arc[1..arc.len() - 1] {
            assert!(ring.contains(p));
        }
        assert_eq!(arc.len(), ring.len() / 4 + 1);
    }
}
