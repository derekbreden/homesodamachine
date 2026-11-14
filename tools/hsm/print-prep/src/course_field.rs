//! Lays a part's courses, sliced where its chosen face lies level, back into the part's pose on
//! the plate, easing them to level, with each road's plastic scaled to the course it fills.
//!
//! A donor slice is an ordinary slice of the part in a frame where the face the courses should
//! follow lies flat on the virtual bed. A field keeps each road's plan position in its own frame
//! and moves the road's height: along the face where the courses follow it, level where they
//! return to the plate's own layers, and through a smooth blend between. Each road is laid in
//! pieces short enough for the field to stay straight along them, and each field shares the
//! road's plastic among its pieces by its own rule.

use crate::gcode::words;
use anyhow::{Context, Result, bail, ensure};
use serde_json::Value;
use std::rc::Rc;

/// The longest chord an arc is laid in.
const ARC_SEGMENT: f64 = 0.75;
/// Shorter motion than this is no motion.
const SPATIAL: f64 = 1e-7;
/// A road piece shorter than this is dropped.
const MIN_PATH: f64 = 1e-5;
/// A field this close to its slicing height leaves a road's plastic as sliced.
const IDENTITY: f64 = 1e-8;

/// One commanded move of the donor's print body, at its donor position, with the bead settings
/// in force when it was commanded.
#[derive(Clone, Debug)]
pub struct Move {
    pub start: [f64; 3],
    pub end: [f64; 3],
    pub feed: f64,
    pub e: Option<f64>,
    pub arc: Option<Arc>,
    pub feature: Rc<str>,
    pub width: Rc<str>,
    pub bead_height: Rc<str>,
    pub fan: i64,
    pub acceleration: i64,
    /// The slice height of the course the move belongs to, as the slicer wrote it.
    pub layer: Rc<str>,
}

/// An arc in the XY plane, about the centre at `i`, `j` from its start.
#[derive(Clone, Copy, Debug)]
pub struct Arc {
    pub clockwise: bool,
    pub i: f64,
    pub j: f64,
}

impl Move {
    /// Whether the move lays plastic, or holds the nozzle on a road with none.
    pub fn deposition(&self) -> bool {
        self.e.is_some_and(|e| e >= 0.0) && (self.arc.is_some() || distance(self.start, self.end) > SPATIAL)
    }
}

/// A laid piece of road, in plate coordinates.
#[derive(Clone, Debug)]
pub struct Road {
    pub start: [f64; 3],
    pub end: [f64; 3],
    pub e: f64,
}

/// The straight-line distance between two points.
pub fn distance(a: [f64; 3], b: [f64; 3]) -> f64 {
    ((a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) + (a[2] - b[2]) * (a[2] - b[2])).sqrt()
}

/// The point `t` of the way from `a` to `b`.
pub fn mix(a: [f64; 3], b: [f64; 3], t: f64) -> [f64; 3] {
    [0, 1, 2].map(|i| a[i] * (1.0 - t) + b[i] * t)
}

fn comment_value(line: &str, key: &str) -> Option<Rc<str>> {
    line.strip_prefix(key).map(|v| Rc::from(v.trim()))
}

/// The donor's print-body moves, from the end of the start G-code to the start of the end
/// G-code, once the slicer has named a course height.
pub fn read_moves(text: &str) -> Result<Vec<Move>> {
    let (mut xyz, mut started, mut absolute, mut relative_e, mut feed) = ([0.0; 3], false, true, true, 0.0);
    let mut feature: Rc<str> = Rc::from("Custom");
    let (mut layer, mut width, mut height): (Rc<str>, Rc<str>, Rc<str>) = (Rc::from("0"), Rc::from(""), Rc::from(""));
    let (mut fan, mut acceleration) = (0_i64, 6000_i64);
    let mut moves = Vec::new();
    for line in text.lines() {
        if line.starts_with("; MACHINE_START_GCODE_END") {
            started = true;
        } else if line.starts_with("; MACHINE_END_GCODE_START") {
            break;
        } else if let Some(v) = comment_value(line, "; Z_HEIGHT:") {
            layer = v;
        } else if let Some(v) = comment_value(line, "; FEATURE:") {
            feature = v;
        } else if let Some(v) = comment_value(line, "; LINE_WIDTH:") {
            width = v;
        } else if let Some(v) = comment_value(line, "; LAYER_HEIGHT:") {
            height = v;
        }
        if line.starts_with(';') {
            continue;
        }
        let code = line.split(';').next().unwrap_or("").trim();
        let op = code.split_whitespace().next().unwrap_or("");
        let args = words(&code[op.len()..]);
        let get = |key: u8| args.iter().find(|(k, _)| *k == key).map(|(_, v)| *v);
        match op {
            "G90" | "G91" => absolute = op == "G90",
            "M83" | "M82" => relative_e = op == "M83",
            "M106" if get(b'P').unwrap_or(1.0) == 1.0 => fan = get(b'S').unwrap_or(255.0).round_ties_even() as i64,
            "M204" => {
                if let Some(s) = get(b'S') {
                    acceleration = s.round_ties_even() as i64;
                }
            }
            _ => {}
        }
        if !matches!(op, "G0" | "G1" | "G2" | "G3") {
            continue;
        }
        let target = std::array::from_fn(|i| {
            let value = get(b"XYZ"[i]);
            if absolute { value.unwrap_or(xyz[i]) } else { xyz[i] + value.unwrap_or(0.0) }
        });
        feed = get(b'F').unwrap_or(feed);
        if started && &*layer != "0" {
            ensure!(absolute && relative_e && feed > 0.0, "the donor print body must have G90, M83 and a valid feed");
            let arc = if matches!(op, "G2" | "G3") {
                ensure!(get(b'R').is_none() && get(b'P').unwrap_or(1.0) == 1.0, "unexpected donor arc: {}", line.trim());
                Some(Arc { clockwise: op == "G2", i: get(b'I').unwrap_or(0.0), j: get(b'J').unwrap_or(0.0) })
            } else {
                None
            };
            moves.push(Move {
                start: xyz, end: target, feed, e: get(b'E'), arc, feature: feature.clone(), width: width.clone(),
                bead_height: height.clone(), fan, acceleration, layer: layer.clone(),
            });
        }
        xyz = target;
    }
    Ok(moves)
}

/// The donor's moves split at each change of slice height, in order.
pub fn groups(moves: Vec<Move>) -> Vec<(Rc<str>, Vec<Move>)> {
    let mut out: Vec<(Rc<str>, Vec<Move>)> = Vec::new();
    for m in moves {
        match out.last_mut() {
            Some((layer, group)) if *layer == m.layer => group.push(m),
            _ => out.push((m.layer.clone(), vec![m])),
        }
    }
    out
}

/// A group's moves from its first deposition to its last.
pub fn active(moves: &[Move]) -> &[Move] {
    let Some(first) = moves.iter().position(Move::deposition) else { return &[] };
    let last = moves.iter().rposition(Move::deposition).unwrap_or(first);
    &moves[first..=last]
}

/// The points an XY-plane arc is laid through, after its start, ending at its end, at most
/// `ARC_SEGMENT` apart.
pub fn arc_points(m: &Move) -> Vec<[f64; 3]> {
    let Some(arc) = m.arc else { return vec![m.end] };
    let ([x, y, z], [u, v, w]) = (m.start, m.end);
    let (cx, cy) = (x + arc.i, y + arc.j);
    let radius = arc.i.hypot(arc.j);
    if radius < SPATIAL {
        return if distance(m.start, m.end) > SPATIAL { vec![m.end] } else { Vec::new() };
    }
    let angle = (y - cy).atan2(x - cx);
    let mut turn = (v - cy).atan2(u - cx) - angle;
    if arc.clockwise && turn >= -SPATIAL {
        turn -= std::f64::consts::TAU;
    } else if !arc.clockwise && turn <= SPATIAL {
        turn += std::f64::consts::TAU;
    }
    let count = ((turn.abs() * radius / ARC_SEGMENT).ceil() as usize).max(1);
    let mut out: Vec<[f64; 3]> = (1..count)
        .map(|index| {
            let fraction = index as f64 / count as f64;
            let at = angle + turn * fraction;
            [cx + radius * at.cos(), cy + radius * at.sin(), z + (w - z) * fraction]
        })
        .collect();
    out.push(m.end);
    out
}

/// Where a field lays a donor's courses.
pub trait CourseField {
    /// The plate point a donor point is laid at.
    fn place(&self, p: [f64; 3]) -> [f64; 3];
    /// The donor points a move's road is laid through, its start first.
    fn points(&self, m: &Move) -> Vec<[f64; 3]>;
    /// The plastic of each piece between consecutive `points` of the move.
    fn extrusion(&self, m: &Move, points: &[[f64; 3]]) -> Vec<f64>;
}

/// A move's road, laid by `field` in pieces, each with the field's share of the move's plastic.
pub fn lay(m: &Move, field: &dyn CourseField) -> Vec<Road> {
    let points = field.points(m);
    if points.len() < 2 {
        return Vec::new();
    }
    let e = field.extrusion(m, &points);
    points.windows(2).zip(e).map(|(w, e)| Road { start: field.place(w[0]), end: field.place(w[1]), e }).collect()
}

fn triple(v: &Value, key: &str) -> Result<[f64; 3]> {
    serde_json::from_value(v[key].clone()).with_context(|| format!("{key} must hold three numbers"))
}

fn pair(v: &Value, key: &str) -> Result<[f64; 2]> {
    serde_json::from_value(v[key].clone()).with_context(|| format!("{key} must hold two numbers"))
}

fn number(v: &Value, key: &str) -> Result<f64> {
    v[key].as_f64().with_context(|| format!("{key} must be a number"))
}

fn smoothstep(t: f64) -> f64 {
    t * t * (3.0 - 2.0 * t)
}

/// The Sculpted base: sliced with its mounting face level, its courses follow that face through
/// the foot and lower shaft, then ease to the plate's level layers inside the straight shaft,
/// keeping each road's position across the shaft.
pub struct ShaftEase {
    pub sin: f64,
    pub cos: f64,
    pub tangent: f64,
    pub end_derivative: f64,
    pub donor: [f64; 3],
    pub seat: [f64; 3],
    pub fade: [f64; 2],
    pub pivot_y: f64,
    pub phase: f64,
}

impl ShaftEase {
    /// The field the shaft trial recorded in its transition receipt, at the base's incline.
    pub fn from_receipt(receipt: &Value, incline_degrees: f64) -> Result<Self> {
        let rotation = incline_degrees.to_radians();
        let (sin, cos) = (rotation.sin(), rotation.cos());
        let seat = triple(receipt, "physical_seat_origin_mm")?;
        let fade = pair(receipt, "donor_normal_fade_extent_mm")?;
        let pivot_y = number(receipt, "cad_shaft_pivot_y_mm")?;
        let join_z = number(receipt, "physical_join_z_mm")?;
        ensure!(fade[0] < fade[1], "the fade must start below its end");
        Ok(Self {
            sin, cos, tangent: sin / cos, end_derivative: 1.0 / cos - 1.0,
            donor: triple(receipt, "early_donor_origin_mm")?, seat, fade, pivot_y,
            phase: (join_z - seat[2] + sin * pivot_y) / cos - fade[1],
        })
    }

    /// The height along the face's normal a course sliced at `height` is laid at, across the
    /// shaft at `cad_y`, and its rate with slicing height.
    pub fn height_and_scale(&self, cad_y: f64, height: f64) -> (f64, f64) {
        let [start, end] = self.fade;
        if height <= start {
            return (height, 1.0);
        }
        let target_offset = self.tangent * (cad_y - self.pivot_y) + self.phase;
        if height >= end {
            return (end + target_offset + (height - end) / self.cos, 1.0 / self.cos);
        }
        let span = end - start;
        let t = (height - start) / span;
        let blend = smoothstep(t);
        let start_to_end_pitch = self.end_derivative * span * t * t * (t - 1.0);
        let normal = height + blend * target_offset + start_to_end_pitch;
        let derivative = 1.0 + (6.0 * t * (1.0 - t) / span) * target_offset + self.end_derivative * t * (3.0 * t - 2.0);
        (normal, derivative)
    }

    /// A donor point relative to the donor origin.
    pub fn local(&self, p: [f64; 3]) -> [f64; 3] {
        [0, 1, 2].map(|i| p[i] - self.donor[i])
    }
}

impl CourseField for ShaftEase {
    fn place(&self, p: [f64; 3]) -> [f64; 3] {
        let [x, y, u] = self.local(p);
        let n = self.height_and_scale(y, u).0;
        let [a, b, c] = self.seat;
        [a + x, b + self.cos * y + self.sin * n, c - self.sin * y + self.cos * n]
    }

    /// Each course stays a plane, so a straight run stays whole and an arc keeps its chords.
    fn points(&self, m: &Move) -> Vec<[f64; 3]> {
        let mut points = vec![m.start];
        points.extend(arc_points(m));
        points
    }

    /// The whole move's plastic, scaled by the field's rate of lift at the move's midpoint once
    /// the move rises past the start of the fade, shared evenly across an arc's chords.
    fn extrusion(&self, m: &Move, points: &[[f64; 3]]) -> Vec<f64> {
        let mut e = m.e.unwrap_or(0.0);
        if m.deposition() && e != 0.0 && m.start[2].max(m.end[2]) - self.donor[2] > self.fade[0] {
            let y = (m.start[1] + m.end[1]) * 0.5 - self.donor[1];
            let u = (m.start[2] + m.end[2]) * 0.5 - self.donor[2];
            e *= self.height_and_scale(y, u).1;
        }
        let n = points.len() - 1;
        vec![e / n as f64; n]
    }
}

/// The Sculpted tip: sliced with its mating shoulder level, its courses rise from the bed onto
/// the shoulder's incline, hold it through the shoulder, and ease back to level below the nose,
/// keeping each road's plan position on the plate.
pub struct ShoulderHold {
    pub shoulder: [f64; 3],
    pub shoulder_layer: f64,
    pub tangent: f64,
    pub sec_minus_one: f64,
    pub bed_through: f64,
    pub hold: [f64; 2],
    pub normal_again: f64,
    pub exact_y: [f64; 2],
    pub edge_width: f64,
    pub displacement: [f64; 3],
    pub piece: f64,
}

impl ShoulderHold {
    /// The field the tip trial recorded in its warp receipt, for a donor placed `displacement`
    /// from the plate, laid in pieces at most `piece` long where the field moves courses.
    pub fn from_receipt(receipt: &Value, displacement: [f64; 3], piece: f64) -> Result<Self> {
        let angle = number(receipt, "full_angle_degrees")?.to_radians();
        let incoming = pair(receipt, "incoming_fade_virtual_mm")?;
        let outgoing = pair(receipt, "outgoing_fade_virtual_mm")?;
        ensure!(piece > 0.0, "road pieces must have a length");
        Ok(Self {
            shoulder: triple(receipt, "authored_plane_pick_world_xyz_mm")?,
            shoulder_layer: number(receipt, "virtual_shoulder_z_mm")?,
            tangent: angle.tan(),
            sec_minus_one: 1.0 / angle.cos() - 1.0,
            bed_through: incoming[0],
            hold: [incoming[1], outgoing[0]],
            normal_again: outgoing[1],
            exact_y: pair(receipt, "xy_limits_exact_plane_y_mm")?,
            edge_width: number(receipt, "outside_edge_blend_width_y_mm")?,
            displacement,
            piece,
        })
    }

    /// The shoulder's plan position across it, held to the flat shoulder and eased past its
    /// edges.
    pub fn effective_y(&self, y: f64) -> f64 {
        let [low, high] = self.exact_y;
        let w = self.edge_width;
        let left = ((low - y) / w).clamp(0.0, 1.0);
        let right = ((y - high) / w).clamp(0.0, 1.0);
        let drift = |x: f64| w * x * (1.0 - x / 2.0);
        y.clamp(low, high) - drift(left) + drift(right)
    }

    /// The share of the shoulder a course at slicing height `u` follows, and that share scaled
    /// by its distance from the shoulder course.
    pub fn parameters_at(&self, u: f64) -> (f64, f64) {
        let w0 = self.hold[0] - self.bed_through;
        let w1 = self.normal_again - self.hold[1];
        let left = ((u - self.bed_through) / w0).clamp(0.0, 1.0);
        let right = ((self.normal_again - u) / w1).clamp(0.0, 1.0);
        let a = left * left * (3.0 - 2.0 * left) * right * right * (3.0 - 2.0 * right);
        (a, (u - self.shoulder_layer) * a)
    }

    /// The plate height a course sliced at `u` is laid at, at plan position `y`.
    pub fn forward(&self, y: f64, u: f64) -> f64 {
        let (a, b) = self.parameters_at(u);
        let root = self.shoulder[2] - self.tangent * (self.effective_y(y) - self.shoulder[1]);
        u + a * (root - self.shoulder_layer) + self.sec_minus_one * b
    }

    /// The field's rate of plate height with slicing height, by central difference.
    pub fn derivative(&self, y: f64, u: f64) -> f64 {
        let ds = 0.0001;
        (self.forward(y, u + ds) - self.forward(y, u - ds)) / (2.0 * ds)
    }

    /// The slicing height a plate height `z` at plan position `y` was sliced at.
    pub fn inverse(&self, y: f64, z: f64) -> f64 {
        if z <= self.bed_through || z >= self.normal_again {
            return z;
        }
        let (mut low, mut high) = (z.min(self.bed_through), z.max(self.normal_again));
        for _ in 0..36 {
            let middle = (low + high) * 0.5;
            if self.forward(y, middle) < z {
                low = middle;
            } else {
                high = middle;
            }
        }
        (low + high) * 0.5
    }

    /// A donor point moved onto the plate.
    pub fn plate(&self, p: [f64; 3]) -> [f64; 3] {
        [0, 1, 2].map(|i| p[i] + self.displacement[i])
    }
}

impl CourseField for ShoulderHold {
    fn place(&self, p: [f64; 3]) -> [f64; 3] {
        let [x, y, z] = self.plate(p);
        [x, y, self.forward(y, z)]
    }

    /// Runs the field moves are laid in short pieces, and motion too short to carry a piece is
    /// dropped; runs below its first course or above its last stay whole.
    fn points(&self, m: &Move) -> Vec<[f64; 3]> {
        let dz = self.displacement[2];
        let mut prev = m.start;
        let mut points = vec![prev];
        for point in arc_points(m) {
            let gap = distance(prev, point);
            if gap <= MIN_PATH {
                continue;
            }
            let still = prev[2].max(point[2]) + dz <= self.bed_through || prev[2].min(point[2]) + dz >= self.normal_again;
            let n = if still { 1 } else { ((gap / self.piece).ceil() as usize).max(1) };
            points.extend((1..=n).map(|j| mix(prev, point, j as f64 / n as f64)));
            prev = point;
        }
        points
    }

    /// Each piece's share of the move's plastic by length, scaled by how much thicker the field
    /// lays the piece's bead than the slicer did.
    fn extrusion(&self, m: &Move, points: &[[f64; 3]]) -> Vec<f64> {
        let lengths: Vec<f64> = points.windows(2).map(|w| distance(w[0], w[1])).collect();
        let total: f64 = lengths.iter().sum();
        let unmoved = points.iter().all(|p| {
            let [_, y, z] = self.plate(*p);
            (self.forward(y, z) - p[2] - self.displacement[2]).abs() < IDENTITY
        });
        let bead = m.bead_height.parse::<f64>().ok().filter(|h| *h != 0.0);
        let e = m.e.unwrap_or(0.0);
        points
            .windows(2)
            .zip(&lengths)
            .map(|(w, length)| {
                let [_, y, z] = self.plate([0, 1, 2].map(|i| (w[1][i] + w[0][i]) * 0.5));
                let thickening = match (unmoved, bead) {
                    (true, _) => 1.0,
                    (false, Some(h)) => (self.forward(y, z) - self.forward(y, z - h)) / h,
                    (false, None) => self.derivative(y, z),
                };
                e * length / total * thickening
            })
            .collect()
    }
}

/// The field a receipt describes: the base's shaft ease or the tip's shoulder hold.
pub fn field_from_receipt(kind: &str, receipt: &Value, incline_degrees: Option<f64>, displacement: [f64; 3], piece: f64)
    -> Result<Box<dyn CourseField>> {
    Ok(match kind {
        "shaft-ease" => Box::new(ShaftEase::from_receipt(receipt, incline_degrees.context("the shaft ease needs the base's incline")?)?),
        "shoulder-hold" => Box::new(ShoulderHold::from_receipt(receipt, displacement, piece)?),
        _ => bail!("unknown course field {kind}"),
    })
}
