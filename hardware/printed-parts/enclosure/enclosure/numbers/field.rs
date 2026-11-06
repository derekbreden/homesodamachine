//! The exterior flute field: the plan perimeter its print rail walks, the rail's sampled frames,
//! and the field's tolerances.
use crate::catalog::{flute_skin, flute_width};
use crate::{Bounds, P2};
use crate::shell::{CORNER_ROUND, FLUTE_COUNT, FLUTE_DEPTH, FLUTE_RISE};
use serde::{Deserialize, Serialize};
use std::f64::consts::PI;

/// The print rail's frames round the closed plan perimeter.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Rail {
    pub s: Vec<f64>,
    pub point: Vec<P2>,
    pub normal: Vec<P2>,
    pub closed: bool,
    pub band: Option<P2>,
    /// The plain lands the flutes stop short of.
    pub plain: Vec<Bounds>,
}

/// The field's tolerances and the flutes' pitch, width, depth and rise.
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Field {
    pub across: f64,
    pub along: f64,
    pub margin: f64,
    pub overrun: f64,
    pub plan_tol: f64,
    pub face_tol: f64,
    pub pitch: f64,
    pub width: f64,
    pub depth: f64,
    pub rise: f64,
}

/// One run of the plan outline: a straight run or a quarter turn round a corner.
#[derive(Clone, Copy, Debug)]
pub enum Segment {
    /// A start point, the run's direction and its outward normal.
    Line { length: f64, start: P2, tangent: P2, normal: P2 },
    /// The corner's centre, the start angle and the radius.
    Arc { length: f64, centre: P2, a0: f64, radius: f64 },
}

impl Segment {
    fn length(&self) -> f64 {
        match self {
            Segment::Line { length, .. } | Segment::Arc { length, .. } => *length,
        }
    }
}

/// The plan outline, counterclockwise from the middle of the front face.
pub fn plan_segments(outer: &Bounds) -> [Segment; 9] {
    let [ox0, ox1, oy0, oy1, _, _] = *outer;
    let r = CORNER_ROUND;
    let run_x = (ox1 - ox0) - 2.0 * r;
    let run_y = (oy1 - oy0) - 2.0 * r;
    let turn = PI * r / 2.0;
    let line = |length, start, tangent, normal| Segment::Line { length, start, tangent, normal };
    let arc = |length, centre, a0, radius| Segment::Arc { length, centre, a0, radius };
    [
        line(run_x / 2.0, [0.0, oy0], [1.0, 0.0], [0.0, -1.0]),
        arc(turn, [ox1 - r, oy0 + r], -PI / 2.0, r),
        line(run_y, [ox1, oy0 + r], [0.0, 1.0], [1.0, 0.0]),
        arc(turn, [ox1 - r, oy1 - r], 0.0, r),
        line(run_x, [ox1 - r, oy1], [-1.0, 0.0], [0.0, 1.0]),
        arc(turn, [ox0 + r, oy1 - r], PI / 2.0, r),
        line(run_y, [ox0, oy1 - r], [0.0, -1.0], [-1.0, 0.0]),
        arc(turn, [ox0 + r, oy0 + r], PI, r),
        line(run_x / 2.0, [ox0 + r, oy0], [1.0, 0.0], [0.0, -1.0]),
    ]
}

pub fn plan_perimeter(outer: &Bounds) -> f64 {
    plan_segments(outer).iter().map(Segment::length).sum()
}

/// One flute per pitch round the perimeter.
pub fn flute_pitch(outer: &Bounds) -> f64 {
    plan_perimeter(outer) / FLUTE_COUNT
}

/// The point and outward normal an arc length `s` along a run of segments reaches.
pub fn walk(segments: &[Segment], s: f64) -> (P2, P2) {
    let total: f64 = segments.iter().map(Segment::length).sum();
    assert!((-1e-9..=total + 1e-9).contains(&s), "arc length walked off the end of a run");
    let mut s = s.max(0.0).min(total);
    for segment in segments {
        if s <= segment.length() + 1e-9 {
            return match *segment {
                Segment::Line { start, tangent, normal, .. } => {
                    ([start[0] + tangent[0] * s, start[1] + tangent[1] * s], normal)
                }
                Segment::Arc { centre, a0, radius, .. } => {
                    let a = a0 + s / radius;
                    let n = [a.cos(), a.sin()];
                    ([centre[0] + radius * n[0], centre[1] + radius * n[1]], n)
                }
            };
        }
        s -= segment.length();
    }
    panic!("arc length walked off the end of a run")
}

pub fn plan_at(s: f64, outer: &Bounds) -> (P2, P2) {
    let segments = plan_segments(outer);
    let total: f64 = segments.iter().map(Segment::length).sum();
    walk(&segments, s.rem_euclid(total))
}

/// Sample the closed perimeter rail once per grid step across the flutes.
pub fn perimeter_rail(outer: &Bounds, plain: Vec<Bounds>) -> Rail {
    let length = plan_perimeter(outer);
    let steps = ((length / flute_skin().grid_across).round_ties_even() as usize).max(3);
    let h = length / steps as f64;
    let s: Vec<f64> = (0..steps).map(|i| i as f64 * h).collect();
    let (point, normal) = s.iter().map(|&si| plan_at(si, outer)).unzip();
    Rail { s, point, normal, closed: true, band: None, plain }
}

pub fn field(outer: &Bounds) -> Field {
    let f = flute_skin();
    Field {
        across: f.grid_across,
        along: f.grid_along,
        margin: f.cut_margin,
        overrun: f.cut_overrun,
        plan_tol: f.plan_tol,
        face_tol: f.face_tol,
        pitch: flute_pitch(outer),
        width: flute_width(),
        depth: FLUTE_DEPTH,
        rise: FLUTE_RISE,
    }
}
