//! Lays the Sculpted base's courses for the Mark2 plate: the level-face donor's courses through
//! the shaft ease, a bridge stitch across the shaft on the course where the ease ends, and the
//! level upper courses as the slicer laid them. Each course is a restartable band whose entry and
//! exit the plate scheduler reads from its markers.

use crate::course_field::{CourseField, Move, ShaftEase, active, arc_points, groups, read_moves};
use crate::gcode::words;
use crate::json::{Json, python_number};
use crate::python_text::{dist, round};
use crate::shaft_stitch;
use anyhow::{Context, Result, bail, ensure};
use serde_json::Value;
use std::fmt::Write as _;
use std::path::Path;
use std::rc::Rc;

/// The features whose runs are reordered to climb.
pub const WALLS: [&str; 4] = ["Outer wall", "Overhang wall", "Inner wall", "Floating vertical shell"];
/// The donor's nominal course.
pub const BASE_NORMAL_LAYER: f64 = 0.24;
const EXTRUSION_Z_FEED: f64 = 7.5 * 60.0;
const TRAVEL_Z_FEED: f64 = 15.0 * 60.0;
const LOCAL_LIFT: f64 = 1.10;
const TRAVEL_FEED: f64 = 100.0 * 60.0;
const RETRACT: &str = "0.8";
const RETRACT_SPEED: i64 = 1800;
const SPATIAL: f64 = 1e-7;
/// The base's turn about X on the plate.
pub const INCLINE_DEGREES: f64 = 15.0;
const SKIN_TOP: f64 = 3.6;
const FADE_START: f64 = 88.0;
/// Where the ease ends on the donor's slicing height, unless asked otherwise.
pub const FADE_END: f64 = 144.0;
/// The plate height the level upper courses continue from, unless asked otherwise.
pub const NATIVE_JOIN_Z: f64 = 143.48;
const SHAFT_PIVOT_Y: f64 = 12.9;
const SHAFT_RADIUS: f64 = 13.5;
const BASE_ID: i64 = 1901;
const FLOOR: &str = "native tilted base";
const SHAFT: &str = "graded shaft transition";
const UPPER: &str = "native level upper base";

fn output_point(p: [f64; 3]) -> [f64; 3] {
    p.map(|v| round(v, 3))
}

/// The feed the firmware receives, held under the Z speed ceiling of the rounded motion.
fn output_feed(start: [f64; 3], end: [f64; 3], requested: f64, cap: f64) -> i64 {
    let (start, end) = (output_point(start), output_point(end));
    let dz = (end[2] - start[2]).abs();
    if dz < SPATIAL {
        return requested.floor() as i64;
    }
    let limited = cap * dist(&start, &end) / dz;
    let feed = if limited < requested { limited } else { requested };
    (feed + 1e-9).floor() as i64
}

fn xyz(p: [f64; 3]) -> String {
    format!("{:.3} {:.3} {:.3}", p[0], p[1], p[2])
}

/// What a phase deposited, in the order the receipt reports it.
pub struct Stats {
    pub road_mm: f64,
    pub filament_mm: f64,
    pub dz_roads: i64,
    pub features: Vec<(Rc<str>, f64)>,
    pub min_xyz: [f64; 3],
    pub max_xyz: [f64; 3],
}

impl Stats {
    pub fn new() -> Self {
        Self { road_mm: 0.0, filament_mm: 0.0, dz_roads: 0, features: Vec::new(),
               min_xyz: [f64::INFINITY; 3], max_xyz: [f64::NEG_INFINITY; 3] }
    }

    fn road(&mut self, feature: &Rc<str>, length: f64, e: Option<f64>, dz: f64, a: [f64; 3], b: [f64; 3]) {
        self.road_mm += length;
        if let Some(e) = e {
            self.filament_mm += e;
        }
        match self.features.iter_mut().find(|(f, _)| f == feature) {
            Some(slot) => slot.1 += length,
            None => self.features.push((feature.clone(), 0.0 + length)),
        }
        self.dz_roads += (dz > 0.0005) as i64;
        for i in 0..3 {
            self.min_xyz[i] = py_min(py_min(self.min_xyz[i], a[i]), b[i]);
            self.max_xyz[i] = py_max(py_max(self.max_xyz[i], a[i]), b[i]);
        }
    }

    pub fn to_json(&self) -> Json {
        Json::Map(vec![
            ("road_mm".into(), float(self.road_mm)),
            ("filament_mm".into(), float(self.filament_mm)),
            ("dz_roads".into(), int(self.dz_roads)),
            ("features".into(), Json::Map(self.features.iter().map(|(k, v)| (k.to_string(), float(*v))).collect())),
            ("min_xyz".into(), Json::List(self.min_xyz.iter().map(|v| float(*v)).collect())),
            ("max_xyz".into(), Json::List(self.max_xyz.iter().map(|v| float(*v)).collect())),
        ])
    }
}

impl Default for Stats {
    fn default() -> Self {
        Self::new()
    }
}

/// Python's `min(a, b)`: `b` only when it is smaller.
fn py_min(a: f64, b: f64) -> f64 {
    if b < a { b } else { a }
}

fn py_max(a: f64, b: f64) -> f64 {
    if b > a { b } else { a }
}

/// A float as `json.dumps` writes it.
pub fn float(v: f64) -> Json {
    Json::Number(python_number(v), v)
}

/// An integer as `json.dumps` writes it.
pub fn int(v: i64) -> Json {
    Json::Number(v.to_string(), v as f64)
}

/// The bead settings a band has announced.
#[derive(Default)]
struct Flags {
    feature: Option<Rc<str>>,
    width: Option<Rc<str>>,
    height: Option<Rc<str>>,
    fan: Option<i64>,
    acceleration: Option<i64>,
}

impl Flags {
    fn bead(&mut self, out: &mut String, m: &Move) {
        for (key, slot, value) in [("FEATURE", &mut self.feature, &m.feature), ("LINE_WIDTH", &mut self.width, &m.width),
                                   ("LAYER_HEIGHT", &mut self.height, &m.bead_height)] {
            if slot.as_ref() != Some(value) {
                let _ = writeln!(out, "; {key}: {value}");
                *slot = Some(value.clone());
            }
        }
    }

    fn machine(&mut self, out: &mut String, m: &Move) {
        for (key, slot, value) in [("M106", &mut self.fan, m.fan), ("M204", &mut self.acceleration, m.acceleration)] {
            if *slot != Some(value) {
                let _ = writeln!(out, "{key} S{value}");
                *slot = Some(value);
            }
        }
    }
}

fn header(out: &mut String, height: &str, section: usize, total: usize, entry: [f64; 3], exit: [f64; 3]) {
    let _ = write!(out, "; whole-base course {section} of {total}\n; HSM_ENTRY_XYZ: {}\n; HSM_ENTRY_RETRACT_MM: {RETRACT}\n\
                         ; HSM_EXIT_XYZ: {}\n; HSM_EXIT_RETRACT_MM: {RETRACT}\n; HSM_NORMAL_Z: {height}\n; OBJECT_ID: 1901\n\
                         G90\nM83\nG1 E{RETRACT} F{RETRACT_SPEED}\n", xyz(entry), xyz(exit));
}

fn footer(out: &mut String) {
    let _ = write!(out, "G1 E-{RETRACT} F{RETRACT_SPEED}\n; HSM_END_WHOLE_BASE_COURSE\n");
}

/// One course as a restartable physical band, laid in the donor's order: the plate scheduler
/// owns the travel to its entry.
pub fn write_group(out: &mut String, height: &str, section: usize, total: usize, moves: &[Move],
                   map: &dyn Fn([f64; 3]) -> [f64; 3], seen: &mut Stats) -> Result<()> {
    let entry = map(moves[0].start);
    let exit = map(moves[moves.len() - 1].end);
    header(out, height, section, total, entry, exit);
    let mut flags = Flags::default();
    let mut cursor = entry;
    for m in moves {
        let mapped_end = map(m.end);
        let deposition = m.deposition();
        if deposition {
            let expected = map(m.start);
            ensure!(dist(&cursor, &expected) <= 0.002,
                "Support remap lost nozzle continuity at {height}: {cursor:?} -> {expected:?}");
            flags.bead(out, m);
        }
        flags.machine(out, m);
        let mut prev = cursor;
        let points = if m.arc.is_some() { arc_points(m) } else { vec![m.end] };
        let count = points.len() as f64;
        for point in &points {
            let mut p = if *point == m.end { mapped_end } else { map(*point) };
            let delta = dist(&prev, &p);
            let e = m.e.map(|e| e / count);
            if delta < SPATIAL && !deposition {
                p = cursor;
            }
            let mut line;
            let feed;
            if delta > SPATIAL {
                if output_point(prev) == output_point(p) {
                    if e.is_some_and(|e| e != 0.0 && round(e, 5) != 0.0) {
                        bail!("Positive extrusion collapsed to one coordinate at {height}: {prev:?} -> {p:?}");
                    }
                    prev = p;
                    continue;
                }
                ensure!(p.iter().all(|c| -1.0 < *c && *c < 330.0), "Requested nozzle coordinate outside the plate or Z travel: {p:?}");
                let dz = (prev[2] - p[2]).abs();
                let cap = if deposition { EXTRUSION_Z_FEED } else { TRAVEL_Z_FEED };
                feed = output_feed(prev, p, m.feed, cap);
                if deposition {
                    seen.road(&m.feature, delta, e, dz, prev, p);
                }
                line = format!("G1 X{:.3} Y{:.3} Z{:.3}", p[0], p[1], p[2]);
            } else if e.is_some() {
                line = String::from("G1");
                feed = m.feed.floor() as i64;
            } else {
                continue;
            }
            if let Some(e) = e {
                let _ = write!(line, " E{e:.5}");
            }
            let _ = writeln!(out, "{line} F{feed}");
            prev = p;
        }
        cursor = prev;
    }
    footer(out);
    Ok(())
}

/// Runs of consecutive roads of a single feature, split at native travel or retraction.
fn runs_of(moves: &[Move]) -> Vec<Vec<Move>> {
    let mut runs = Vec::new();
    let mut run: Vec<Move> = Vec::new();
    for m in moves {
        if m.deposition() {
            if let Some(previous) = run.last() {
                if previous.feature != m.feature || dist(&previous.end, &m.start) > SPATIAL {
                    runs.push(std::mem::take(&mut run));
                }
            }
            run.push(m.clone());
        } else if !run.is_empty() && (dist(&m.start, &m.end) > SPATIAL || m.e.unwrap_or(0.0) < 0.0) {
            runs.push(std::mem::take(&mut run));
        }
    }
    if !run.is_empty() {
        runs.push(run);
    }
    runs
}

/// A wall run in pieces that each climb: each road keeps its centerline, plastic and ramp, and
/// the run divides only where its mapped height turns back.
fn climbing(run: Vec<Move>, map: &dyn Fn([f64; 3]) -> [f64; 3]) -> Result<Vec<Vec<Move>>> {
    ensure!(run.iter().all(|m| m.arc.is_none()), "Split/reverse needs linear wall roads");
    let slope_dz = 0.003;
    let mut pieces: Vec<(i32, Vec<Move>)> = Vec::new();
    let mut piece = Vec::new();
    let mut sign = 0;
    for m in run {
        let dz = map(m.end)[2] - map(m.start)[2];
        let direction = if dz.abs() > slope_dz { if dz > 0.0 { 1 } else { -1 } } else { 0 };
        if direction != 0 && sign != 0 && direction != sign {
            pieces.push((sign, std::mem::take(&mut piece)));
        }
        piece.push(m);
        if direction != 0 {
            sign = direction;
        }
    }
    if !piece.is_empty() {
        pieces.push((sign, piece));
    }
    Ok(pieces.into_iter().map(|(sign, piece)| {
        if sign < 0 {
            piece.into_iter().rev().map(|mut m| {
                std::mem::swap(&mut m.start, &mut m.end);
                m
            }).collect()
        } else {
            piece
        }
    }).collect())
}

/// One course with each wall feature's runs laid uphill and the course's own travel lifted
/// over what it has laid.
pub fn write_ordered_group(out: &mut String, height: &str, section: usize, total: usize, moves: &[Move],
                           map: &dyn Fn([f64; 3]) -> [f64; 3], seen: &mut Stats) -> Result<()> {
    let mut runs: Vec<Vec<Move>> = Vec::new();
    let all = runs_of(moves);
    let mut i = 0;
    while i < all.len() {
        let feature = all[i][0].feature.clone();
        let mut j = i;
        while j < all.len() && all[j][0].feature == feature {
            j += 1;
        }
        if WALLS.contains(&&*feature) {
            let mut pieces = Vec::new();
            for run in &all[i..j] {
                pieces.extend(climbing(run.clone(), map)?);
            }
            let keyed: Vec<(f64, Vec<Move>)> = pieces.into_iter().map(|p| (map(p[0].start)[2], p)).collect();
            let mut keyed = keyed;
            keyed.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap_or(std::cmp::Ordering::Equal));
            runs.extend(keyed.into_iter().map(|(_, p)| p));
        } else {
            runs.extend(all[i..j].iter().cloned());
        }
        i = j;
    }
    let entry = map(runs[0][0].start);
    let last = runs[runs.len() - 1].last().context("an empty run")?;
    let exit = map(last.end);
    header(out, height, section, total, entry, exit);
    let mut flags = Flags::default();
    let mut previous = entry;
    let linear = |out: &mut String, previous: &mut [f64; 3], next: [f64; 3], feed: f64, e: Option<f64>,
                      feature: Option<&Rc<str>>, seen: &mut Stats| -> Result<()> {
        let length = dist(&*previous, &next);
        let dz = (next[2] - previous[2]).abs();
        if output_point(*previous) == output_point(next) {
            if e.is_some_and(|e| e != 0.0 && round(e, 5) != 0.0) {
                bail!("Positive extrusion collapsed to one coordinate at {height}: {previous:?} -> {next:?}");
            }
            *previous = next;
            return Ok(());
        }
        let limit = if e.is_none() { TRAVEL_Z_FEED } else { EXTRUSION_Z_FEED };
        let feed = output_feed(*previous, next, feed, limit);
        let _ = write!(out, "G1 X{:.3} Y{:.3} Z{:.3}", next[0], next[1], next[2]);
        if let Some(e) = e {
            let _ = write!(out, " E{e:.5}");
        }
        let _ = writeln!(out, " F{feed}");
        if e.is_some() {
            seen.road(feature.context("a road before its feature")?, length, e, dz, *previous, next);
        }
        *previous = next;
        Ok(())
    };
    for run in &runs {
        let start = map(run[0].start);
        if dist(&previous, &start) > 0.002 {
            let _ = writeln!(out, "G1 E-{RETRACT} F{RETRACT_SPEED}");
            let up = [previous[0], previous[1], previous[2] + LOCAL_LIFT];
            linear(out, &mut previous, up, TRAVEL_Z_FEED, None, None, seen)?;
            linear(out, &mut previous, [start[0], start[1], start[2] + LOCAL_LIFT], TRAVEL_FEED, None, None, seen)?;
            linear(out, &mut previous, start, TRAVEL_Z_FEED, None, None, seen)?;
            let _ = writeln!(out, "G1 E{RETRACT} F{RETRACT_SPEED}");
        }
        for m in run {
            flags.bead(out, m);
            flags.machine(out, m);
            let points = if m.arc.is_some() { arc_points(m) } else { vec![m.end] };
            let e = m.e.context("a wall road without plastic")? / points.len() as f64;
            for point in points {
                let feature = flags.feature.clone();
                linear(out, &mut previous, map(point), m.feed, Some(e), feature.as_ref(), seen)?;
            }
        }
    }
    footer(out);
    Ok(())
}

/// The shaft ease and the plate pose it lays the donor into.
pub struct ShaftTransition {
    pub ease: ShaftEase,
    pub fade_end: f64,
    pub native_join_z: f64,
}

impl ShaftTransition {
    pub fn new(donor: [f64; 3], physical: [f64; 3], fade_end: f64, native_join_z: f64) -> Self {
        let rotation = INCLINE_DEGREES.to_radians();
        let (sin, cos) = (rotation.sin(), rotation.cos());
        let ease = ShaftEase {
            sin, cos, tangent: sin / cos, end_derivative: 1.0 / cos - 1.0, donor, seat: physical,
            fade: [FADE_START, fade_end], pivot_y: SHAFT_PIVOT_Y,
            phase: (native_join_z - physical[2] + sin * SHAFT_PIVOT_Y) / cos - fade_end,
        };
        Self { ease, fade_end, native_join_z }
    }

    /// A donor move with its plastic scaled by the ease's rate of lift at its midpoint.
    pub fn adjust(&self, m: &Move) -> Move {
        let mut m = m.clone();
        let e = m.e.unwrap_or(0.0);
        if !m.deposition() || e == 0.0 || py_max(m.start[2], m.end[2]) <= FADE_START {
            return m;
        }
        let donor = self.ease.donor;
        let y = (m.start[1] + m.end[1]) * 0.5 - donor[1];
        let u = (m.start[2] + m.end[2]) * 0.5 - donor[2];
        m.e = Some(e * self.ease.height_and_scale(y, u).1);
        m
    }

    /// A plate point on the join plane, as the donor point the ease lays there.
    pub fn join_plane_to_donor(&self, p: [f64; 3]) -> [f64; 3] {
        let (seat, donor, e) = (self.ease.seat, self.ease.donor, &self.ease);
        let [x, y, z] = [0, 1, 2].map(|i| p[i] - seat[i]);
        [donor[0] + x, donor[1] + e.cos * y - e.sin * z, donor[2] + self.fade_end]
    }

    fn summary(&self) -> Vec<(String, Json)> {
        let e = &self.ease;
        let (mut pitch, mut slopes, mut heights) = (Vec::new(), Vec::new(), Vec::new());
        for index in 0..=1000 {
            let t = index as f64 / 1000.0;
            let u = FADE_START + (self.fade_end - FADE_START) * t;
            let w = t * t * (3.0 - 2.0 * t);
            let normal_slope = w * e.tangent;
            let physical_slope = (-e.sin + e.cos * normal_slope) / (e.cos + e.sin * normal_slope);
            slopes.push(physical_slope.atan() * (180.0 / std::f64::consts::PI));
            for y in [SHAFT_PIVOT_Y - SHAFT_RADIUS, SHAFT_PIVOT_Y + SHAFT_RADIUS] {
                let (n, jacobian) = e.height_and_scale(y, u);
                heights.push(e.seat[2] - e.sin * y + e.cos * n);
                pitch.push(BASE_NORMAL_LAYER * jacobian / dist(&[1.0, normal_slope], &[0.0, 0.0]));
            }
        }
        let range = |v: &[f64]| Json::List(vec![
            float(v.iter().skip(1).fold(v[0], |m, &x| py_min(m, x))),
            float(v.iter().skip(1).fold(v[0], |m, &x| py_max(m, x))),
        ]);
        vec![
            ("local_plane_slope_range_degrees".into(), range(&slopes)),
            ("physical_fade_z_extent_mm".into(), range(&heights)),
            ("approx_bead_normal_pitch_range_mm".into(), range(&pitch)),
            ("physical_join_z_mm".into(), float(self.native_join_z)),
            ("cad_join_section_offset_mm".into(), float(e.phase)),
            ("donor_normal_fade_extent_mm".into(), Json::List(vec![float(FADE_START), float(self.fade_end)])),
            ("cad_shaft_pivot_y_mm".into(), float(SHAFT_PIVOT_Y)),
            ("native_upper_first_z_mm".into(), float(self.native_join_z + BASE_NORMAL_LAYER)),
        ]
    }
}

/// The last eased course: its walls, then a bridge stitch across the shaft's actual section
/// where native infill would start.
fn write_stitched_join(out: &mut String, height: &str, section: usize, total: usize, moves: &[Move],
                       warp: &ShaftTransition, seen: &mut Stats, mesh: &Path) -> Result<Json> {
    let (bridges, report) = shaft_stitch::ties(mesh, warp.native_join_z, warp.ease.seat, warp.ease.sin, warp.ease.cos,
                                               BASE_NORMAL_LAYER, height)?;
    let mut laid: Vec<Move> = moves.iter().filter(|m| m.deposition() && WALLS.contains(&&*m.feature)).cloned().collect();
    let mut stock: Vec<&str> = moves.iter().filter(|m| m.deposition()).map(|m| &*m.feature)
        .filter(|f| !WALLS.contains(f)).collect();
    stock.sort_unstable();
    stock.dedup();
    ensure!(stock == ["Sparse infill"], "Unexpected shaft join features: {stock:?}");
    laid.extend(bridges.into_iter().map(|mut m| {
        m.start = warp.join_plane_to_donor(m.start);
        m.end = warp.join_plane_to_donor(m.end);
        m
    }));
    let mut written = String::new();
    write_ordered_group(&mut written, height, section, total, &laid, &|p| warp.ease.place(p), seen)?;
    let marker = "; FEATURE: Bridge\n";
    ensure!(written.matches(marker).count() == 1, "The shaft needs one uninterrupted bridge stitch feature band");
    out.push_str(&written.replace(marker, &format!("; HSM_BRIDGE_STITCH: shaft join bridge stitch\n{marker}")));
    Ok(report)
}

/// The slicing heights of a G-code's courses that `keep` takes.
fn relevant_layers(text: &str, keep: impl Fn(f64) -> bool) -> Result<Vec<f64>> {
    let mut out = Vec::new();
    for line in text.lines() {
        if let Some(v) = line.strip_prefix("; Z_HEIGHT:") {
            let height: f64 = v.trim().parse().with_context(|| format!("a course height {v:?}"))?;
            if keep(height) {
                out.push(height);
            }
        }
    }
    Ok(out)
}

/// The native upper band's positive roads above the join, all of them the base's own model roads.
fn audit_upper_source(text: &str, join_z: f64) -> Result<i64> {
    let (mut height, mut object, mut feature) = (0.0_f64, None::<i64>, None::<String>);
    let mut count = 0;
    for line in text.lines() {
        if line.starts_with("; MACHINE_END_GCODE_START") {
            break;
        }
        if let Some(v) = line.strip_prefix("; Z_HEIGHT:") {
            height = v.trim().parse()?;
        }
        if height <= join_z {
            continue;
        }
        if let Some(v) = line.strip_prefix("; OBJECT_ID:") {
            object = Some(v.trim().parse()?);
        } else if let Some(v) = line.strip_prefix("; FEATURE:") {
            feature = Some(v.trim().to_string());
        } else if (line.starts_with("G1 ") || line.starts_with("G2 ") || line.starts_with("G3 "))
            && line.contains(" E") && (line.contains(" X") || line.contains(" Y")) {
            let code = line.split(';').next().unwrap_or("").trim();
            let op = code.split_whitespace().next().unwrap_or("");
            let e = words(&code[op.len()..]).iter().find(|(k, _)| *k == b'E').map(|(_, v)| *v).unwrap_or(0.0);
            if e > 0.0 {
                let support = feature.as_deref().is_some_and(|f| !f.is_empty() && f.starts_with("Support"));
                ensure!(object == Some(BASE_ID) && !support,
                    "Upper native band has unrelated deposition at {height}, object_id={object:?}, feature={feature:?}");
                count += 1;
            }
        }
    }
    ensure!(count > 0, "No upper native model extrusion found");
    Ok(count)
}

fn triple(v: &Value) -> Result<[f64; 3]> {
    serde_json::from_value(v.clone()).context("three numbers")
}

/// The donor's origin under the base and the base's seat on the plate, from the donor's and the
/// physical slice's preparation reports.
pub fn tape_origin(donor_report: &Value, physical_report: &Value) -> Result<([f64; 3], [f64; 3])> {
    let base = donor_report["parts"].as_array().context("donor parts")?.iter()
        .find(|p| p["identify_id"].as_i64() == Some(BASE_ID)).context("the donor has no base")?;
    ensure!(base["rotation_x_degrees"].as_f64().context("donor rotation")?.abs() <= 1e-9,
        "The donor base has to be horizontal in its CAD frame");
    let (t, c) = (triple(&base["plate_translation_mm"])?, triple(&base["source_center_mm"])?);
    let donor = [t[0] - c[0], t[1] - c[1], t[2] - c[2]];
    let physical = triple(&physical_report["base_rim_supports"]["seat_print_world_center_mm"])?;
    Ok((donor, physical))
}

/// The inputs of the continued base.
pub struct ContinuedBase<'a> {
    pub donor_gcode: &'a Path,
    pub donor_report: &'a Path,
    pub physical_gcode: &'a Path,
    pub physical_report: &'a Path,
    pub output: &'a Path,
    pub uphill_wall_runs: bool,
    pub stitch_mesh: Option<&'a Path>,
    pub fade_end: f64,
    pub native_join_z: f64,
}

/// Writes the continued base's G-code and, beside it, its receipt.
pub fn continue_base(args: &ContinuedBase) -> Result<()> {
    let read = |p: &Path| std::fs::read(p).with_context(|| format!("reading {}", p.display()));
    let (donor_bytes, physical_bytes) = (read(args.donor_gcode)?, read(args.physical_gcode)?);
    let donor_text = std::str::from_utf8(&donor_bytes)?;
    let physical_text = std::str::from_utf8(&physical_bytes)?;
    let (donor, physical) = tape_origin(&serde_json::from_slice(&read(args.donor_report)?)?,
                                        &serde_json::from_slice(&read(args.physical_report)?)?)?;
    let warp = ShaftTransition::new(donor, physical, args.fade_end, args.native_join_z);
    ensure!(args.fade_end > FADE_START, "The shaft blend must end above where it begins");
    let use_donor = |z: f64| SKIN_TOP < z && z <= warp.fade_end;
    let use_upper = |z: f64| z > warp.native_join_z;
    let lower = relevant_layers(donor_text, use_donor)?;
    let upper = relevant_layers(physical_text, use_upper)?;
    ensure!((lower.last().context("no donor course in range")? - warp.fade_end).abs() <= 0.0001,
        "The fade must end precisely on a donor course");
    ensure!((upper.first().context("no upper course")? - warp.native_join_z - BASE_NORMAL_LAYER).abs() <= 0.0001,
        "The upper source must begin one complete native course above the blend");
    let count = lower.len() + upper.len();
    let audited = audit_upper_source(physical_text, warp.native_join_z)?;
    let mut stats = [Stats::new(), Stats::new(), Stats::new()];
    let mut events: Vec<(&str, i64)> = Vec::new();
    let mut event = |phase: &'static str| match events.iter_mut().find(|(p, _)| *p == phase) {
        Some(slot) => slot.1 += 1,
        None => events.push((phase, 1)),
    };
    let mut section = 0;
    let mut stitched = Json::Null;
    let mut out = String::new();
    let place = |p: [f64; 3]| warp.ease.place(p);
    for (height, moves) in groups(read_moves(donor_text)?) {
        let z: f64 = height.parse()?;
        if z > warp.fade_end {
            break;
        }
        if !use_donor(z) {
            continue;
        }
        let laid = active(&moves);
        if laid.is_empty() {
            continue;
        }
        let (phase, index) = if z <= FADE_START { (FLOOR, 0) } else { (SHAFT, 1) };
        section += 1;
        event(phase);
        let _ = writeln!(out, "; HSM_DONOR_PHASE: {phase}");
        let adjusted: Vec<Move> = laid.iter().map(|m| warp.adjust(m)).collect();
        match args.stitch_mesh {
            Some(mesh) if z == warp.fade_end => {
                stitched = write_stitched_join(&mut out, &height, section, count, &adjusted, &warp, &mut stats[index], mesh)?;
            }
            _ if args.uphill_wall_runs => write_ordered_group(&mut out, &height, section, count, &adjusted, &place, &mut stats[index])?,
            _ => write_group(&mut out, &height, section, count, &adjusted, &place, &mut stats[index])?,
        }
    }
    for (height, moves) in groups(read_moves(physical_text)?) {
        let z: f64 = height.parse()?;
        if !use_upper(z) {
            continue;
        }
        let laid = active(&moves);
        if laid.is_empty() {
            continue;
        }
        section += 1;
        event(UPPER);
        let _ = write!(out, "; HSM_DONOR_PHASE: {UPPER}\n; HSM_UPPER_NATIVE_Z: {height}\n");
        let progress = warp.fade_end + z - warp.native_join_z;
        write_group(&mut out, &format!("{progress:.5}"), section, count, laid, &|p| p, &mut stats[2])?;
    }
    ensure!(section == count, "A selected source course contains no deposition");
    std::fs::write(args.output, out.as_bytes()).with_context(|| format!("writing {}", args.output.display()))?;
    let mut summary = warp.summary();
    let point = |p: [f64; 3]| Json::List(p.iter().map(|v| float(*v)).collect());
    summary.extend([
        ("donor_gcode_sha256".into(), Json::Text(crate::sha256_hex(&donor_bytes))),
        ("physical_gcode_sha256".into(), Json::Text(crate::sha256_hex(&physical_bytes))),
        ("candidate_gcode_sha256".into(), Json::Text(crate::sha256_hex(out.as_bytes()))),
        ("early_donor_origin_mm".into(), point(donor)),
        ("physical_seat_origin_mm".into(), point(physical)),
        ("native_upper_positive_source_roads_audited".into(), int(audited)),
        ("emitted_events_by_phase".into(), Json::Map(events.iter().map(|(p, n)| (p.to_string(), int(*n))).collect())),
        ("emitted_deposition_by_phase".into(), Json::Map(
            [FLOOR, SHAFT, UPPER].iter().zip(&stats).map(|(p, s)| (p.to_string(), s.to_json())).collect())),
        ("shaft_bridge_stitch".into(), stitched),
        ("uphill_wall_runs".into(), Json::Bool(args.uphill_wall_runs)),
    ]);
    let receipt = args.output.with_extension("json");
    std::fs::write(&receipt, Json::Map(summary).dumps() + "\n").with_context(|| format!("writing {}", receipt.display()))?;
    Ok(())
}
