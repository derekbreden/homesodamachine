//! Lays the Sculpted tip's warp-donor slice back onto the plate. The shoulder field carries each
//! road to its physical height, each donor course laid whole, and the nose above the field keeps
//! the donor's own route, arcs, cooling and plastic.

use crate::course_field::{active, distance, groups, lay, read_moves, rounded, Move, ShoulderHold};
use crate::tip_warp::dot;
use anyhow::{ensure, Context, Result};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::Path;
use std::rc::Rc;

const PURPOSE: &str = "Replay the inverse-sliced tip's courses at their physical heights with bounded nozzle paths.";
const TIP_ID: i64 = 1902;
const RETRACT: f64 = 0.8;
const RETRACT_FEED: i64 = 1800;
/// The Z speed ceilings for laying plastic and for travel, and the plan travel speed.
const Z_PRINT_MM_MIN: f64 = 450.0;
const Z_TRAVEL_MM_MIN: f64 = 900.0;
const TRAVEL_XY_MM_MIN: f64 = 5400.0;
/// How far above a course the nozzle travels between runs.
const LIFT: f64 = 0.85;
/// A road piece shorter than this is no motion.
const MIN_PATH: f64 = 1e-5;
/// Shorter motion than this is no motion to the donor's reader.
const SPATIAL: f64 = 1e-7;
/// The longest piece the field lays a road in.
const SUBDIVIDE_ROAD_MM: f64 = 1.0;
/// The highest donor course laid.
const UPPER_UP_TO: f64 = 320.0;

/// The tape and its report.
pub struct Tape {
    pub gcode: String,
    pub report: String,
}

/// Lay the donor slice `gcode`, whose part placements are in `donor_report`, through the field
/// in the tip's warp receipt.
pub fn tape(gcode: &Path, donor_report: &Path, warp_receipt: &Path) -> Result<Tape> {
    let text = std::fs::read_to_string(gcode).with_context(|| format!("reading {}", gcode.display()))?;
    let receipt_bytes = std::fs::read(warp_receipt).with_context(|| format!("reading {}", warp_receipt.display()))?;
    let receipt: Value = serde_json::from_slice(&receipt_bytes)?;
    let report: Value = serde_json::from_slice(&std::fs::read(donor_report).with_context(|| format!("reading {}", donor_report.display()))?)?;
    let field = layout(&receipt, &report)?;
    let mut schedule: Vec<Course> = Vec::new();
    for (layer, moves) in groups(read_moves(&text)?) {
        let u = layer.parse::<f64>().with_context(|| format!("the donor course height {layer}"))? + field.displacement[2];
        if u > UPPER_UP_TO {
            break;
        }
        if u >= field.normal_again - 1e-4 {
            let body = active(&moves);
            if body.iter().any(|m| positive(m.e) && m.deposition()) {
                schedule.push(Course { state: 2, u, body: Body::Native(body.to_vec()) });
            }
            continue;
        }
        let runs = split_runs(&moves, &field)?;
        if !runs.iter().flatten().any(|m| positive(m.e)) {
            continue;
        }
        let state = if u <= field.bed_through { 0 } else { 2 };
        schedule.push(Course { state, u, body: Body::Laid(runs) });
    }
    let order = |a: f64, b: f64| a.partial_cmp(&b).unwrap_or(std::cmp::Ordering::Equal);
    schedule.sort_by(|a, b| a.state.cmp(&b.state).then(order(a.u, b.u)));

    let mut out = String::from("G90\nM83\n");
    let mut stats = Stats::default();
    for (i, course) in schedule.iter().enumerate() {
        match &course.body {
            Body::Native(moves) => write_native_course(&mut out, i + 1, course.u, moves, &field, &mut stats),
            Body::Laid(runs) => write_course(&mut out, i + 1, course.u, runs, &field, &mut stats),
        }
    }
    let report = json!({
        "purpose": PURPOSE,
        "gcode_source_sha256": crate::sha256_hex(text.as_bytes()),
        "warp_report_sha256": crate::sha256_hex(&receipt_bytes),
        "tip_tape_sha256": crate::sha256_hex(out.as_bytes()),
        "shoulder_placement_mm": field.shoulder,
        "native_nose_from_physical_z_mm": field.normal_again,
        "native_donor_translation_to_plate_mm": field.displacement,
        "physical_order": "whole virtual course in source height order",
        "retained_native_nose_travel": true,
        "phase_stats": stats.json(),
    });
    Ok(Tape { gcode: out, report: serde_json::to_string_pretty(&report)? + "\n" })
}

/// Write the tape to `output` and its report beside it, as `.json`.
pub fn write(gcode: &Path, donor_report: &Path, warp_receipt: &Path, output: &Path) -> Result<()> {
    let tape = tape(gcode, donor_report, warp_receipt)?;
    std::fs::write(output, &tape.gcode).with_context(|| format!("writing {}", output.display()))?;
    let report = output.with_extension("json");
    std::fs::write(&report, &tape.report).with_context(|| format!("writing {}", report.display()))
}

/// One course of the tape: its place in the order, the donor course it came from and what it
/// lays.
struct Course {
    /// Anchor courses come first, then the whole courses and the nose.
    state: u8,
    u: f64,
    body: Body,
}

enum Body {
    /// The donor's own moves, shifted onto the plate.
    Native(Vec<Move>),
    /// Runs of road pieces the field laid.
    Laid(Vec<Vec<Move>>),
}

/// The field the warp receipt records, for the donor as its report places the tip.
fn layout(receipt: &Value, report: &Value) -> Result<ShoulderHold> {
    let tip = report["parts"]
        .as_array()
        .and_then(|parts| parts.iter().find(|p| p["name"] == "faucet-shell-tip"))
        .context("the donor report has no faucet-shell-tip")?;
    let placed: [f64; 12] = serde_json::from_value(tip["build_transform"].clone()).context("the tip's build transform")?;
    let centre: [f64; 3] = serde_json::from_value(tip["source_center_mm"].clone()).context("the tip's source centre")?;
    let rotation: [[f64; 3]; 3] = std::array::from_fn(|i| std::array::from_fn(|j| placed[3 * j + i]));
    let donor = [0, 1, 2].map(|i| placed[9 + i] - dot(rotation[i], centre));
    let recorded: [[f64; 3]; 3] = serde_json::from_value(receipt["physical_rotation"].clone()).context("the receipt's rotation")?;
    ensure!(
        (0..3).all(|i| (0..3).all(|j| (rotation[i][j] - recorded[i][j]).abs() <= 1e-6)),
        "Warped donor rotation contradicts model pre-warp receipt"
    );
    let translation: [f64; 3] =
        serde_json::from_value(receipt["physical_cad_to_plate_translation"].clone()).context("the receipt's translation")?;
    ShoulderHold::from_receipt(receipt, [0, 1, 2].map(|i| translation[i] - donor[i]), SUBDIVIDE_ROAD_MM)
}

/// Which part of the tip a course at slicing height `u` prints.
fn phase(field: &ShoulderHold, u: f64) -> &'static str {
    if u <= field.bed_through {
        "tip anchor"
    } else if u < field.hold[0] {
        "tip shoulder entry"
    } else if u <= field.hold[1] + 1e-4 {
        "tip yellow shoulder"
    } else if u < field.normal_again - 1e-4 {
        "tip shoulder fade"
    } else {
        "tip native nose"
    }
}

/// Whether a move lays plastic the tape keeps: extrusion that is positive at the five places
/// it is written to.
fn positive(e: Option<f64>) -> bool {
    e.is_some_and(|e| e > 0.5e-5)
}

/// A nose feed, written to six significant digits.
fn feed(f: f64) -> String {
    let exponent: i32 = format!("{f:.5e}").split_once('e').map_or(0, |(_, e)| e.parse().unwrap_or(0));
    let text = format!("{f:.*}", (5 - exponent).max(0) as usize);
    if text.contains('.') { text.trim_end_matches('0').trim_end_matches('.').to_string() } else { text }
}

/// A laid point as the tape writes it, to three places.
fn written(p: [f64; 3]) -> [f64; 3] {
    p.map(|v| rounded(v, 3))
}

/// The feed for a motion between two written points, its Z speed held to `cap`.
fn output_feed(start: [f64; 3], end: [f64; 3], requested: f64, cap: f64) -> i64 {
    let dz = (end[2] - start[2]).abs();
    if dz < SPATIAL {
        return requested.floor() as i64;
    }
    (requested.min(cap * distance(start, end) / dz) + 1e-9).floor() as i64
}

/// The donor's runs: consecutive deposition of one feature, split at travel and retraction.
fn runs_of(moves: &[Move]) -> Vec<Vec<&Move>> {
    let mut out = Vec::new();
    let mut run: Vec<&Move> = Vec::new();
    for m in moves {
        if m.deposition() {
            if let Some(previous) = run.last() {
                if previous.feature != m.feature || distance(previous.end, m.start) > SPATIAL {
                    out.push(std::mem::take(&mut run));
                }
            }
            run.push(m);
        } else if !run.is_empty() && (distance(m.start, m.end) > SPATIAL || m.e.unwrap_or(0.0) < 0.0) {
            out.push(std::mem::take(&mut run));
        }
    }
    if !run.is_empty() {
        out.push(run);
    }
    out
}

/// A donor course's roads laid by the field and gathered into runs.
fn split_runs(moves: &[Move], field: &ShoulderHold) -> Result<Vec<Vec<Move>>> {
    let mut grouped: Vec<Vec<Move>> = Vec::new();
    for native in runs_of(moves) {
        let mut runs: Vec<Vec<Move>> = Vec::new();
        for m in native {
            for road in lay(m, field) {
                let p = Move { start: road.start, end: road.end, e: Some(road.e), arc: None, ..m.clone() };
                if written(p.start) == written(p.end) {
                    continue;
                }
                match runs.last_mut() {
                    Some(run) if distance(run[run.len() - 1].end, p.start) <= 0.002 => run.push(p),
                    _ => runs.push(vec![p]),
                }
            }
        }
        grouped.extend(runs.into_iter().filter(|path| path.iter().any(|m| positive(m.e))));
    }
    Ok(grouped)
}

/// The bead settings a course has written, so each is written only when it changes.
#[derive(Default)]
struct Modes {
    feature: Option<Rc<str>>,
    width: Option<Rc<str>>,
    height: Option<Rc<str>>,
    fan: Option<i64>,
    acceleration: Option<i64>,
}

fn set_text(out: &mut String, slot: &mut Option<Rc<str>>, key: &str, value: &Rc<str>, otherwise: &str) {
    let value: Rc<str> = if value.is_empty() { Rc::from(otherwise) } else { value.clone() };
    if slot.as_ref() != Some(&value) {
        let _ = writeln!(out, "; {key}: {value}");
        *slot = Some(value);
    }
}

fn set_number(out: &mut String, slot: &mut Option<i64>, key: &str, value: i64) {
    if *slot != Some(value) {
        let _ = writeln!(out, "{key} S{value}");
        *slot = Some(value);
    }
}

fn xyz(p: [f64; 3], digits: usize) -> String {
    format!("{:.d$} {:.d$} {:.d$}", p[0], p[1], p[2], d = digits)
}

fn course_head(out: &mut String, phase: &str, index: usize, height: f64, entry: String, exit: String) {
    let _ = write!(out, "; HSM_TIP_PHASE: {phase}\n; HSM_TIP_COURSE: {index}\n");
    let _ = writeln!(out, "; HSM_TIP_VIRTUAL_Z: {height:.5}");
    let _ = write!(out, "; HSM_ENTRY_XYZ: {entry}\n; HSM_ENTRY_RETRACT_MM: {RETRACT}\n");
    let _ = write!(out, "; HSM_EXIT_XYZ: {exit}\n; HSM_EXIT_RETRACT_MM: {RETRACT}\n");
    let _ = write!(out, "; OBJECT_ID: {TIP_ID}\nG90\nM83\nG1 E{RETRACT} F{RETRACT_FEED}\n");
}

/// A straight motion to `point`, unless it is written as the point the nozzle is at.
fn linear(out: &mut String, prev: &mut [f64; 3], point: [f64; 3], feed: f64, extrusion: Option<f64>) {
    let (from, to) = (written(*prev), written(point));
    if from == to {
        return;
    }
    let rate = output_feed(from, to, feed, if extrusion.is_some() { Z_PRINT_MM_MIN } else { Z_TRAVEL_MM_MIN });
    let _ = write!(out, "G1 X{:.3} Y{:.3} Z{:.3}", point[0], point[1], point[2]);
    if let Some(e) = extrusion {
        let _ = write!(out, " E{e:.5}");
    }
    let _ = writeln!(out, " F{rate}");
    *prev = point;
}

/// A course the field laid, each run entered from above after a retraction.
fn write_course(out: &mut String, index: usize, height: f64, runs: &[Vec<Move>], field: &ShoulderHold, stats: &mut Stats) {
    let phase = phase(field, height);
    let start = runs[0][0].start;
    let end = runs[runs.len() - 1][runs[runs.len() - 1].len() - 1].end;
    course_head(out, phase, index, height, xyz(start, 3), xyz(end, 3));
    let mut prev = start;
    let mut modes = Modes::default();
    for run in runs {
        let start = run[0].start;
        if distance(prev, start) > 0.001 {
            let _ = writeln!(out, "G1 E-{RETRACT} F{RETRACT_FEED}");
            // The nozzle travels above itself and the run's start.
            let hike = prev[2].max(start[2]) + LIFT;
            let rise = [prev[0], prev[1], hike];
            linear(out, &mut prev, rise, Z_TRAVEL_MM_MIN, None);
            linear(out, &mut prev, [start[0], start[1], hike], TRAVEL_XY_MM_MIN, None);
            linear(out, &mut prev, start, Z_TRAVEL_MM_MIN, None);
            let _ = writeln!(out, "G1 E{RETRACT} F{RETRACT_FEED}");
        }
        for m in run {
            set_text(out, &mut modes.feature, "FEATURE", &m.feature, "");
            set_text(out, &mut modes.width, "LINE_WIDTH", &m.width, ".42");
            set_text(out, &mut modes.height, "LAYER_HEIGHT", &m.bead_height, ".24");
            set_number(out, &mut modes.fan, "M106", m.fan);
            set_number(out, &mut modes.acceleration, "M204", m.acceleration);
            let e = m.e.unwrap_or(0.0);
            linear(out, &mut prev, m.end, m.feed, Some(e));
            stats.count(phase, "deposition_roads", 1);
            stats.sum(phase, "filament_mm", e);
            stats.count(phase, "vertical_roads", ((m.end[2] - m.start[2]).abs() > 0.002) as i64);
            stats.count(phase, "downward_bridge_roads", (m.feature.contains("Bridge") && m.end[2] < m.start[2] - 0.002) as i64);
        }
    }
    let _ = write!(out, "G1 E-{RETRACT} F{RETRACT_FEED}\n; HSM_TIP_END_COURSE\n");
    stats.count(phase, "courses", 1);
}

/// A nose course as the donor sliced it, moved onto the plate.
fn write_native_course(out: &mut String, index: usize, height: f64, moves: &[Move], field: &ShoulderHold, stats: &mut Stats) {
    let phase = phase(field, height);
    let shift = |p: [f64; 3]| [0, 1, 2].map(|i| p[i] + field.displacement[i]);
    course_head(out, phase, index, height, xyz(shift(moves[0].start), 5), xyz(shift(moves[moves.len() - 1].end), 5));
    let mut modes = Modes::default();
    for m in moves {
        set_number(out, &mut modes.fan, "M106", m.fan);
        set_number(out, &mut modes.acceleration, "M204", m.acceleration);
        if m.deposition() {
            set_text(out, &mut modes.feature, "FEATURE", &m.feature, "");
            set_text(out, &mut modes.width, "LINE_WIDTH", &m.width, ".42");
            set_text(out, &mut modes.height, "LAYER_HEIGHT", &m.bead_height, ".24");
        }
        let spatial = distance(m.start, m.end) > MIN_PATH || m.arc.is_some();
        if !spatial && m.e.is_none() {
            continue;
        }
        out.push_str(match m.arc {
            None => "G1 ",
            Some(arc) if arc.clockwise => "G2 ",
            Some(_) => "G3 ",
        });
        if spatial {
            let t = shift(m.end);
            let _ = write!(out, "X{:.5} Y{:.5} Z{:.5}", t[0], t[1], t[2]);
        }
        if let Some(arc) = m.arc {
            let _ = write!(out, " I{:.5} J{:.5}", arc.i, arc.j);
        }
        if let Some(e) = m.e {
            let _ = write!(out, " E{e:.5}");
        }
        let _ = writeln!(out, " F{}", feed(m.feed));
        if m.deposition() {
            stats.count(phase, "deposition_roads", 1);
            stats.sum(phase, "filament_mm", m.e.unwrap_or(0.0));
            stats.count(phase, "vertical_roads", ((m.end[2] - m.start[2]).abs() > 0.002) as i64);
        }
    }
    let _ = write!(out, "G1 E-{RETRACT} F{RETRACT_FEED}\n; HSM_TIP_END_COURSE\n");
    stats.count(phase, "courses", 1);
}

/// Per phase, what the tape laid: counts of courses and roads, and the filament they take.
#[derive(Default)]
struct Stats {
    counts: BTreeMap<(&'static str, &'static str), i64>,
    sums: BTreeMap<(&'static str, &'static str), f64>,
}

impl Stats {
    fn count(&mut self, phase: &'static str, key: &'static str, n: i64) {
        *self.counts.entry((phase, key)).or_default() += n;
    }

    fn sum(&mut self, phase: &'static str, key: &'static str, x: f64) {
        *self.sums.entry((phase, key)).or_default() += x;
    }

    fn json(&self) -> Value {
        let mut out = json!({});
        for (&(phase, key), n) in &self.counts {
            out[phase][key] = json!(n);
        }
        for (&(phase, key), x) in &self.sums {
            out[phase][key] = json!(x);
        }
        out
    }
}
