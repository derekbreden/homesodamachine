//! The approach readings take each dry nozzle approach the head replay finds below the earlier
//! beads in the tip's, transfers' and base's course phases, and read it again at its exact
//! position over the nominal bead tracks laid before it: the move that makes the approach, whether
//! the approach is where that move lands, and the earlier track it comes closest to.
//!
//! A bead's track is its nominal centerline with the section the slicer's flow gives it, so the
//! readings are of the plate's paths, not of the print.

use crate::course_field::distance;
use crate::gcode;
use crate::python_text::{self, Json};
use anyhow::{bail, Context, Result};
use std::collections::BTreeMap;
use std::path::Path;

/// The phases whose dry approaches are read again.
const PHASES: [&str; 7] = [
    "tip shoulder entry",
    "tip yellow shoulder",
    "tip level paths above shoulder",
    "tip level paths below shoulder",
    "transfers between course groups",
    "inclined-base conventional handoff",
    "sloped course",
];
/// The replay's dry nozzle readings an approach is taken from.
const METRICS: [&str; 2] = ["dry_travel_flat", "dry_travel_cone"];
/// A modeled gap below this is read again.
const PROBE_GAP: f64 = -0.05;
const BODY_START: &str = "; MACHINE_START_GCODE_END";
const BODY_END: &str = "; MACHINE_END_GCODE_START";
const FEATURE: &str = "; FEATURE:";
const WIDTH: &str = "; LINE_WIDTH:";
const OBJECT_START: &str = "; start printing object, unique label id: ";
const OBJECT_END: &str = "; stop printing object, unique label id: ";
const PHASE: [&str; 4] = ["; HSM_PHASE:", "; HSM_PHASE_TRAVEL:", "; HSM_TIP_PHASE:", "; HSM_DONOR_PHASE:"];
/// The line width before the plate names one.
const START_WIDTH: f64 = 0.42;
const EPS: f64 = 1e-8;
/// The flow ratio the slicer's nominal bead sections are read back with, and a bridge's extra flow.
const FLOW: f64 = 0.9555;
const BRIDGE_FLOW: f64 = 1.25;
const FILAMENT_DIAMETER: f64 = 1.75;
/// An approach this close to its move's end is where the move lands.
const LANDING: f64 = 0.00005;
/// The longest step an arc's track is followed in.
const ARC_STEP: f64 = 0.025;

/// The approach readings of the replay report at `replay` on the plate G-code at `gcode`.
pub fn read(gcode: &Path, replay: &Path) -> Result<Json> {
    let report = Json::loads(&python_text::read_text(replay)?)?;
    let Some(Json::Dict(phases)) = report.get("local_nozzle_model") else {
        bail!("{} has no local nozzle model", replay.display());
    };
    let mut probes = Vec::new();
    for (phase, row) in phases {
        if !PHASES.contains(&phase.as_str()) {
            continue;
        }
        let Json::Dict(metrics) = row else { bail!("{phase}'s nozzle readings are not a table") };
        for (metric, witness) in metrics {
            if !METRICS.contains(&metric.as_str()) || *witness == Json::Null {
                continue;
            }
            let field = |key: &str| witness.get(key).cloned().with_context(|| format!("{phase} {metric} has no {key}"));
            if !(number(&field("gap_mm")?)? < PROBE_GAP) {
                continue;
            }
            probes.push(Json::Dict(vec![
                ("phase".into(), Json::Str(phase.clone())),
                ("metric".into(), Json::Str(metric.clone())),
                ("line".into(), field("line")?),
                ("deposited_by".into(), field("deposited_by")?),
                ("xyz_mm".into(), field("nozzle_xyz_mm")?),
                ("model_gap_mm".into(), field("gap_mm")?),
            ]));
        }
    }
    check(gcode, &probes)
}

fn number(value: &Json) -> Result<f64> {
    match value {
        Json::Float(x) => Ok(*x),
        Json::Int(i) => Ok(*i as f64),
        other => bail!("{other:?} is not a number"),
    }
}

fn integer(value: Option<&Json>) -> Result<i64> {
    match value {
        Some(Json::Int(i)) => Ok(*i),
        other => bail!("{other:?} is not a whole number"),
    }
}

fn floats(p: [f64; 3]) -> Json {
    Json::List(p.iter().map(|&v| Json::Float(v)).collect())
}

/// `min(a, b)` and `max(a, b)` as the readings compare: the first of equals.
fn least(a: f64, b: f64) -> f64 {
    if b < a { b } else { a }
}
fn most(a: f64, b: f64) -> f64 {
    if b > a { b } else { a }
}

/// An approach as the replay named it.
struct Approach {
    line: usize,
    object: i64,
    xyz: [f64; 3],
}

/// The earlier nominal track an approach comes closest to.
struct Stock {
    gap: f64,
    height: f64,
    lateral: f64,
    center: [f64; 3],
    line: usize,
    feature: String,
}

impl Stock {
    fn json(&self) -> Json {
        Json::Dict(vec![
            ("gap_mm".into(), Json::Float(self.gap)),
            ("nominal_bead_height_mm".into(), Json::Float(self.height)),
            ("distance_to_earlier_centerline_mm".into(), Json::Float(self.lateral)),
            ("earlier_centerline_xyz_mm".into(), floats(self.center)),
            ("prior_line".into(), Json::Int(self.line as i64)),
            ("prior_feature".into(), Json::Str(self.feature.clone())),
        ])
    }
}

fn check(tape: &Path, observations: &[Json]) -> Result<Json> {
    if observations.is_empty() {
        return Ok(Json::List(Vec::new()));
    }
    let mut approaches = Vec::new();
    for w in observations {
        let xyz = match w.get("xyz_mm") {
            Some(Json::List(v)) if v.len() == 3 => [number(&v[0])?, number(&v[1])?, number(&v[2])?],
            other => bail!("{other:?} is not a position"),
        };
        approaches.push(Approach { line: usize::try_from(integer(w.get("line"))?)?, object: integer(w.get("deposited_by"))?, xyz });
    }
    let mut at_line: BTreeMap<usize, Vec<usize>> = BTreeMap::new();
    let mut by_object: BTreeMap<i64, Vec<usize>> = BTreeMap::new();
    for (i, w) in approaches.iter().enumerate() {
        at_line.entry(w.line).or_default().push(i);
        by_object.entry(w.object).or_default().push(i);
    }
    let bbox: BTreeMap<i64, [f64; 4]> = by_object.iter().map(|(&object, probes)| {
        let [mut x0, mut y0] = [approaches[probes[0]].xyz[0], approaches[probes[0]].xyz[1]];
        let [mut x1, mut y1] = [x0, y0];
        for &i in probes {
            let q = approaches[i].xyz;
            (x0, y0, x1, y1) = (least(x0, q[0]), least(y0, q[1]), most(x1, q[0]), most(y1, q[1]));
        }
        (object, [x0, y0, x1, y1])
    }).collect();
    let mut finest: Vec<Option<Stock>> = observations.iter().map(|_| None).collect();
    let mut found = Vec::new();
    let (mut pos, mut offset) = ([0.0; 3], [0.0; 3]);
    let (mut e, mut debt, mut width) = (0.0, 0.0, START_WIDTH);
    let (mut absolute, mut relative_e, mut absolute_arc, mut enabled) = (true, true, false, false);
    let mut object = 0;
    let (mut feature, mut phase) = (String::from("Custom"), String::from("machine startup"));
    let end_line = *at_line.keys().last().context("no approaches")?;
    let text = python_text::read_text(tape)?;
    for (index, line) in text.split('\n').enumerate() {
        let n = index + 1;
        if n > end_line || line.starts_with(BODY_END) {
            break;
        }
        if line.starts_with(';') {
            if line.starts_with(BODY_START) {
                enabled = true;
                debt = 0.0;
            } else if let Some(v) = line.strip_prefix(WIDTH) {
                width = python_text::float(v)?;
            } else if let Some(v) = line.strip_prefix(FEATURE) {
                feature = python_text::strip(v).to_string();
            } else if PHASE.iter().any(|p| line.starts_with(p)) {
                phase = python_text::strip(line.split_once(':').map_or("", |(_, v)| v)).to_string();
            } else if let Some(v) = line.strip_prefix(OBJECT_START) {
                object = python_text::int(v)?;
            } else if line.starts_with(OBJECT_END) {
                object = 0;
            }
            continue;
        }
        let code = line.split(';').next().unwrap_or("").trim_start();
        let end = code.find(char::is_whitespace).unwrap_or(code.len());
        let command = &code[..end];
        match command {
            "" => continue,
            "G90" | "G91" => absolute = command == "G90",
            "G90.1" | "G91.1" => absolute_arc = command == "G90.1",
            "M82" | "M83" => relative_e = command == "M83",
            _ => {}
        }
        if !matches!(command, "G0" | "G1" | "G2" | "G3" | "G92") {
            continue;
        }
        let words = gcode::words(&code[end..]);
        let word = |key: u8| words.iter().find(|(k, _)| *k == key).map(|(_, v)| *v);
        let axis = |i: usize| word(b"XYZ"[i]);
        if command == "G92" {
            offset = std::array::from_fn(|i| pos[i] - axis(i).unwrap_or(pos[i] - offset[i]));
            e = word(b'E').unwrap_or(e);
            continue;
        }
        let next: [f64; 3] = if absolute {
            std::array::from_fn(|i| axis(i).unwrap_or(pos[i] - offset[i]) + offset[i])
        } else {
            std::array::from_fn(|i| pos[i] + axis(i).unwrap_or(0.0))
        };
        let increment = if relative_e { word(b'E').unwrap_or(0.0) } else { word(b'E').unwrap_or(e) - e };
        e += increment;
        let net = increment - debt;
        let remaining = most(0.0, debt - increment);
        for &i in at_line.get(&n).into_iter().flatten() {
            found.push(Json::Dict(vec![
                ("phase".into(), Json::Str(phase.clone())),
                ("observation".into(), observations[i].clone()),
                ("approach_move_from".into(), floats(pos)),
                ("approach_move_to".into(), floats(next)),
                ("landing_sample".into(), Json::Bool(distance(approaches[i].xyz, next) <= LANDING)),
                ("closest_prior_nominal_stock".into(), finest[i].as_ref().map_or(Json::Null, Stock::json)),
            ]));
        }
        let laid = enabled && net > EPS && (pos[0] != next[0] || pos[1] != next[1] || command == "G2" || command == "G3");
        if let Some(&[x0, y0, x1, y1]) = bbox.get(&object).filter(|_| laid) {
            let (length, curve) = contour(command, pos, next, &word, absolute_arc)?;
            let r = width * 0.5;
            let [mut low_x, mut low_y] = [curve[0][0], curve[0][1]];
            let [mut high_x, mut high_y] = [low_x, low_y];
            for p in &curve {
                (low_x, low_y, high_x, high_y) = (least(low_x, p[0]), least(low_y, p[1]), most(high_x, p[0]), most(high_y, p[1]));
            }
            if low_x - r <= x1 && high_x + r >= x0 && low_y - r <= y1 && high_y + r >= y0 {
                let h = height(net, length, width, &feature);
                for &i in &by_object[&object] {
                    let (stop, q) = (approaches[i].line, approaches[i].xyz);
                    if n >= stop {
                        continue;
                    }
                    for pair in curve.windows(2) {
                        let (a, b) = (pair[0], pair[1]);
                        if !(least(a[0], b[0]) - r <= q[0] && q[0] <= most(a[0], b[0]) + r)
                            || !(least(a[1], b[1]) - r <= q[1] && q[1] <= most(a[1], b[1]) + r)
                        {
                            continue;
                        }
                        let Some((gap, lateral, center)) = nearest_top(q, a, b, width, h) else { continue };
                        if finest[i].as_ref().is_none_or(|f| gap < f.gap) {
                            finest[i] = Some(Stock { gap, height: h, lateral, center, line: n, feature: feature.clone() });
                        }
                    }
                }
            }
        }
        debt = remaining;
        pos = next;
    }
    Ok(Json::List(found))
}

/// A move's length and the points its track is followed through.
fn contour(command: &str, a: [f64; 3], b: [f64; 3], word: &dyn Fn(u8) -> Option<f64>, absolute_arcs: bool) -> Result<(f64, Vec<[f64; 3]>)> {
    if command == "G0" || command == "G1" {
        return Ok((distance(a, b), vec![a, b]));
    }
    let (x, y) = arc_center(command == "G2", a, b, word, absolute_arcs)?;
    let radius = (a[0] - x).hypot(a[1] - y);
    let start = (a[1] - y).atan2(a[0] - x);
    let end = (b[1] - y).atan2(b[0] - x);
    let direction = if command == "G2" { -1.0 } else { 1.0 };
    let mut sweep = (direction * (end - start)).rem_euclid(std::f64::consts::TAU);
    if sweep < EPS {
        sweep = std::f64::consts::TAU;
    }
    let whole = (sweep + (word(b'P').unwrap_or(1.0) - 1.0) * std::f64::consts::TAU) * direction;
    let length = (radius * whole).hypot(b[2] - a[2]);
    let count = ((whole.abs() * radius / ARC_STEP).ceil() as usize).max(1);
    let mut points = vec![a];
    for i in 1..count {
        let angle = start + whole * i as f64 / count as f64;
        points.push([x + radius * angle.cos(), y + radius * angle.sin(), a[2] + (b[2] - a[2]) * i as f64 / count as f64]);
    }
    points.push(b);
    Ok((length, points))
}

fn arc_center(clockwise: bool, a: [f64; 3], b: [f64; 3], word: &dyn Fn(u8) -> Option<f64>, absolute_arcs: bool) -> Result<(f64, f64)> {
    let Some(signed) = word(b'R') else {
        let center = |key: u8, at: f64| if absolute_arcs { word(key).unwrap_or(at) } else { at + word(key).unwrap_or(0.0) };
        return Ok((center(b'I', a[0]), center(b'J', a[1])));
    };
    let radius = signed.abs();
    let (dx, dy) = (b[0] - a[0], b[1] - a[1]);
    let chord = dx.hypot(dy);
    if chord <= EPS || chord > 2.0 * radius + 0.002 {
        bail!("invalid R arc at {a:?} → {b:?}");
    }
    let sign = if clockwise == (signed >= 0.0) { -1.0 } else { 1.0 };
    let rise = most(0.0, radius * radius - chord * chord * 0.25).sqrt() * sign;
    Ok(((a[0] + b[0]) * 0.5 - dy / chord * rise, (a[1] + b[1]) * 0.5 + dx / chord * rise))
}

/// The nominal height of a bead laying `net_e` of filament over `length`.
fn height(net_e: f64, length: f64, width: f64, feature: &str) -> f64 {
    if length <= EPS || width <= 0.0 {
        return 0.0;
    }
    let mut volume_per_mm = net_e * std::f64::consts::PI * (FILAMENT_DIAMETER * FILAMENT_DIAMETER) * 0.25 / length / FLOW;
    if feature == "Bridge" {
        volume_per_mm /= BRIDGE_FLOW;
    }
    let k = 1.0 - std::f64::consts::PI / 4.0;
    let determinant = most(0.0, width * width - 4.0 * k * volume_per_mm);
    least(width, most(0.0, (width - determinant.sqrt()) / (2.0 * k)))
}

/// The gap from `tip` down to the top of the bead laid from `a` to `b` where it passes under the
/// tip, the tip's distance from that bead's centerline, and the centerline's point there.
fn nearest_top(tip: [f64; 3], a: [f64; 3], b: [f64; 3], width: f64, bead_height: f64) -> Option<(f64, f64, [f64; 3])> {
    let (x, y) = (b[0] - a[0], b[1] - a[1]);
    let length2 = x * x + y * y;
    if length2 < EPS * EPS {
        return None;
    }
    let t = most(0.0, least(1.0, ((tip[0] - a[0]) * x + (tip[1] - a[1]) * y) / length2));
    let center: [f64; 3] = std::array::from_fn(|i| a[i] + (b[i] - a[i]) * t);
    let lateral = (tip[0] - center[0]).hypot(tip[1] - center[1]);
    let r = width * 0.5;
    if lateral > r {
        return None;
    }
    let flat = most(0.0, (width - bead_height) * 0.5);
    let roll = least(1.0, most(0.0, (lateral - flat) / most(EPS, r - flat)));
    let drops = bead_height * 0.5 * (1.0 - (1.0 - roll * roll).sqrt());
    Some((tip[2] - center[2] + drops, lateral, center))
}
