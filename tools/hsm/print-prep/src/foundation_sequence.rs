//! Splices inclined tip interface and shell courses into the ordinary Mark2 slice.

use super::*;
use crate::base_foundation::{HEAD_TRAVEL_MARGIN, left_nozzle};
use crate::course_field::{distance, mix};
use crate::gcode;
use std::ops::Range;

const FIRST_INTERFACE: f64 = 23.8;
const FIRST_VISIBLE: f64 = 24.8;
const TIP_COURSE_HEIGHT: f64 = 0.2;
const TIP_SHELL_COURSES: usize = 7;
const LANDING: f64 = 0.12;
const MIN_LAYER_SHARE: f64 = 0.3;
/// The spacing of the tip's ground under the nozzle, of the coarser ground under the head,
/// and of the samples along a travel.
const GROUND_STEP: f64 = 0.25;
const HEAD_GROUND_STEP: f64 = 1.0;

/// A grid of the highest bead in each cell, with the cells that hold any.
struct Grid {
    x0: f64,
    y0: f64,
    step: f64,
    nx: usize,
    ny: usize,
    top: Vec<f64>,
    occupied: Vec<usize>,
}

impl Grid {
    fn new(lo: [f64; 2], hi: [f64; 2], step: f64) -> Grid {
        let pad = 5.0;
        let (x0, y0) = (lo[0] - pad, lo[1] - pad);
        let nx = ((hi[0] - lo[0] + 2.0 * pad) / step).ceil() as usize + 1;
        let ny = ((hi[1] - lo[1] + 2.0 * pad) / step).ceil() as usize + 1;
        Grid { x0, y0, step, nx, ny, top: vec![f64::NEG_INFINITY; nx * ny], occupied: Vec::new() }
    }

    fn cell(&self, x: f64, y: f64) -> Option<usize> {
        let (i, j) = (((x - self.x0) / self.step).round(), ((y - self.y0) / self.step).round());
        (i >= 0.0 && j >= 0.0 && (i as usize) < self.nx && (j as usize) < self.ny).then(|| j as usize * self.nx + i as usize)
    }

    fn centre(&self, cell: usize) -> [f64; 2] {
        [self.x0 + (cell % self.nx) as f64 * self.step, self.y0 + (cell / self.nx) as f64 * self.step]
    }

    fn raise(&mut self, x: f64, y: f64, z: f64) {
        if let Some(cell) = self.cell(x, y) {
            if self.top[cell] == f64::NEG_INFINITY {
                self.occupied.push(cell);
            }
            self.top[cell] = self.top[cell].max(z);
        }
    }
}

/// The tip's laid plastic as the travelling head meets it: the highest bead over a fine grid for
/// the left nozzle's flat and cone, over a coarser one for the head's underside from the head map.
struct Ground {
    fine: Grid,
    coarse: Grid,
    nozzle: [f64; 3],
    head: Vec<f64>,
    head_step: f64,
    head_x0: f64,
    head_y0: f64,
    head_cols: usize,
    head_rows: usize,
}

impl Ground {
    fn new(lo: [f64; 2], hi: [f64; 2], headmap: &Path) -> Result<Ground> {
        let arrays = crate::npz::read_arrays(headmap)?;
        let get = |name: &str| arrays.get(name).with_context(|| format!("the head map has no {name}"));
        let scalar = |name: &str| -> Result<f64> { get(name)?.f64().and_then(|v| v.first().copied()).with_context(|| format!("{name} is a number")) };
        let h = get("H")?;
        Ok(Ground {
            fine: Grid::new(lo, hi, GROUND_STEP), coarse: Grid::new(lo, hi, HEAD_GROUND_STEP), nozzle: left_nozzle()?,
            head: h.f64().context("H")?.to_vec(), head_step: scalar("step")?, head_x0: scalar("x0")?, head_y0: scalar("y0")?,
            head_rows: h.shape[0], head_cols: h.shape[1],
        })
    }

    /// Lays each road's bead into the grids.
    fn add(&mut self, roads: &[Road]) {
        for r in roads.iter().filter(|r| r.e > 0.0) {
            let count = (distance(r.a, r.b) / (GROUND_STEP / 2.0)).ceil().max(1.0) as usize;
            for k in 0..=count {
                let p = mix(r.a, r.b, k as f64 / count as f64);
                self.fine.raise(p[0], p[1], p[2]);
                self.coarse.raise(p[0], p[1], p[2]);
            }
        }
    }

    /// The head's lowest underside over a coarse cell at `offset` from the nozzle, if the head
    /// reaches there.
    fn underside(&self, offset: [f64; 2]) -> Option<f64> {
        let half = HEAD_GROUND_STEP / 2.0;
        let mut low: Option<f64> = None;
        let mut x = offset[0] - half;
        while x <= offset[0] + half + 1e-9 {
            let mut y = offset[1] - half;
            while y <= offset[1] + half + 1e-9 {
                let i = ((x - self.head_x0) / self.head_step).round();
                let j = ((y - self.head_y0) / self.head_step).round();
                if i >= 0.0 && j >= 0.0 && (i as usize) < self.head_cols && (j as usize) < self.head_rows {
                    let h = self.head[j as usize * self.head_cols + i as usize];
                    if h.is_finite() {
                        low = Some(low.map_or(h, |l: f64| l.min(h)));
                    }
                }
                y += self.head_step;
            }
            x += self.head_step;
        }
        low
    }

    /// Whether the slicer's spiral lift from `a`, around `centre` by `rise`, keeps the nozzle's
    /// flat and cone out of every bead it passes.
    fn spiral_clear(&self, a: [f64; 3], centre: [f64; 2], radius: f64, rise: f64) -> bool {
        let [flat, cone, height] = self.nozzle;
        let start = (a[1] - centre[1]).atan2(a[0] - centre[0]);
        let count = ((std::f64::consts::TAU * radius) / GROUND_STEP).ceil().max(8.0) as usize;
        let reach = (cone / GROUND_STEP).ceil() as i64;
        (0..=count).all(|k| {
            let t = k as f64 / count as f64;
            let angle = start + std::f64::consts::TAU * t;
            let p = [centre[0] + radius * angle.cos(), centre[1] + radius * angle.sin()];
            let z = a[2] + rise * t;
            let Some(cell) = self.fine.cell(p[0], p[1]) else { return true };
            let (ci, cj) = ((cell % self.fine.nx) as i64, (cell / self.fine.nx) as i64);
            (cj - reach..=cj + reach).all(|j| (ci - reach..=ci + reach).all(|i| {
                if i < 0 || j < 0 || i >= self.fine.nx as i64 || j >= self.fine.ny as i64 {
                    return true;
                }
                let cell = j as usize * self.fine.nx + i as usize;
                let q = self.fine.centre(cell);
                let d = (q[0] - p[0]).hypot(q[1] - p[1]);
                let lift = if d <= flat { 0.0 } else if d <= cone { height * (d - flat) / (cone - flat) } else { return true };
                self.fine.top[cell] - lift <= z + 1e-6
            }))
        })
    }

    /// The lowest the nozzle may cross from `a` to `b`: its flat and cone `clear` over every bead
    /// they pass, and the head's underside the head travel margin over every bead it passes.
    fn floor(&self, a: [f64; 3], b: [f64; 3], clear: f64) -> f64 {
        let [flat, cone, rise] = self.nozzle;
        let count = (distance([a[0], a[1], 0.0], [b[0], b[1], 0.0]) / GROUND_STEP).ceil().max(1.0) as usize;
        let reach = (cone / GROUND_STEP).ceil() as i64;
        let mut floor = f64::NEG_INFINITY;
        for k in 0..=count {
            let t = k as f64 / count as f64;
            let p = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
            if let Some(centre) = self.fine.cell(p[0], p[1]) {
                let (ci, cj) = ((centre % self.fine.nx) as i64, (centre / self.fine.nx) as i64);
                for j in (cj - reach).max(0)..=(cj + reach).min(self.fine.ny as i64 - 1) {
                    for i in (ci - reach).max(0)..=(ci + reach).min(self.fine.nx as i64 - 1) {
                        let cell = j as usize * self.fine.nx + i as usize;
                        let m = self.fine.top[cell];
                        if m == f64::NEG_INFINITY {
                            continue;
                        }
                        let q = self.fine.centre(cell);
                        let d = (q[0] - p[0]).hypot(q[1] - p[1]);
                        if d <= cone {
                            let lift = if d <= flat { 0.0 } else { rise * (d - flat) / (cone - flat) };
                            floor = floor.max(m - lift + clear);
                        }
                    }
                }
            }
            for &cell in &self.coarse.occupied {
                let q = self.coarse.centre(cell);
                if let Some(h) = self.underside([q[0] - p[0], q[1] - p[1]]) {
                    floor = floor.max(self.coarse.top[cell] - h + HEAD_TRAVEL_MARGIN);
                }
            }
        }
        floor
    }
}

/// How the tip's own stage crossed between its roads.
#[derive(Default)]
struct TipTravels {
    /// By phase: crossings at the slicer's z-hop on its spiral, crossings at the z-hop lifted
    /// straight because the spiral would meet a bead, and crossings lifted higher, with how far
    /// over the higher end each was lifted.
    rows: Vec<(String, usize, usize, Vec<f64>)>,
}

impl TipTravels {
    fn note(&mut self, phase: &str, over_ends: f64, z_hop: f64, spiral: bool) {
        let row = match self.rows.iter().position(|r| r.0 == phase) {
            Some(i) => &mut self.rows[i],
            None => {
                self.rows.push((phase.to_string(), 0, 0, Vec::new()));
                self.rows.last_mut().unwrap()
            }
        };
        if over_ends > z_hop + 1e-6 {
            row.3.push(over_ends)
        } else if spiral {
            row.1 += 1
        } else {
            row.2 += 1
        }
    }

    fn json(&self) -> Json {
        Json::Dict(self.rows.iter().map(|(phase, hop, straight, lifted)| {
            let mut sorted = lifted.clone();
            sorted.sort_by(f64::total_cmp);
            let pick = |q: f64| sorted.get(((sorted.len() as f64 - 1.0) * q).round() as usize).copied().map_or(Json::Null, Json::Float);
            (phase.clone(), Json::Dict(vec![
                ("at_the_slicer_z_hop_on_its_spiral".into(), Json::Int(*hop as i64)),
                ("at_the_slicer_z_hop_lifted_straight".into(), Json::Int(*straight as i64)),
                ("lifted_higher".into(), Json::Int(sorted.len() as i64)),
                ("lift_over_higher_end_mm_least_median_most".into(), Json::List(vec![pick(0.0), pick(0.5), pick(1.0)])),
            ]))
        }).collect())
    }
}

#[derive(Clone, Copy)]
struct Shoulder {
    origin: [f64; 3],
    sin: f64,
    cos: f64,
    split_y: f64,
}

impl Shoulder {
    fn read(path: &Path) -> Result<Self> {
        let data: serde_json::Value = serde_json::from_slice(&std::fs::read(path)?)?;
        let origin = serde_json::from_value(data["authored_plane_pick_world_xyz_mm"].clone())?;
        let angle = data["bearing_plane_degrees"]
            .as_f64()
            .context("Bearing incline")?;
        let [low, _]: [f64; 2] =
            serde_json::from_value(data["xy_limits_exact_plane_y_mm"].clone())?;
        let [first, last]: [f64; 2] =
            serde_json::from_value(data["exactly_inclined_virtual_mm"].clone())?;
        ensure!(
            first <= FIRST_INTERFACE && last >= Self::last_visible(),
            "The tip donor needs to hold the exact incline through its interface and shell courses"
        );
        let (sin, cos) = angle.to_radians().sin_cos();
        Ok(Self {
            origin,
            sin,
            cos,
            split_y: low - 5.0,
        })
    }

    fn u(self, p: [f64; 3]) -> f64 {
        self.origin[2] + (p[1] - self.origin[1]) * self.sin + (p[2] - self.origin[2]) * self.cos
    }

    fn last_visible() -> f64 {
        FIRST_VISIBLE + (TIP_SHELL_COURSES - 1) as f64 * TIP_COURSE_HEIGHT
    }
}

#[derive(Clone, Copy, PartialEq)]
enum Portion {
    Lower,
    Inclined,
    Upper,
}

/// Parameter interval with a nonnegative affine value at each point.
fn intersect(span: &mut Range<f64>, a: f64, b: f64) -> bool {
    if a < 0.0 && b < 0.0 {
        return false;
    }
    if a < 0.0 {
        span.start = span.start.max(a / (a - b));
    }
    if b < 0.0 {
        span.end = span.end.min(a / (a - b));
    }
    span.end > span.start
}

#[derive(Clone)]
struct Road<'a> {
    a: [f64; 3],
    b: [f64; 3],
    e: f64,
    modal: Modal<'a>,
}

impl<'a> Road<'a> {
    fn sub(&self, t: Range<f64>, flow: f64) -> Self {
        Self {
            a: mix(self.a, self.b, t.start),
            b: mix(self.a, self.b, t.end),
            e: self.e * (t.end - t.start) * flow,
            modal: self.modal.clone(),
        }
    }
}

/// The roads to which the shoulder join can apply. XY arcs are split where a cut needs to
/// see their interior; complete native courses outside the join keep their source arcs.
fn roads<'a>(band: &Band<'a>) -> Result<Vec<Road<'a>>> {
    let entry = band.entry.as_ref().context("Tip course entry")?;
    let mut modal = Modal::new(entry.xyz, 0.0);
    modal.feed = entry.feed;
    modal.feature = entry.feature;
    modal.width = entry.width;
    modal.height = entry.height;
    modal.fan = entry.fan;
    modal.acceleration = entry.acceleration;
    let mut out = Vec::with_capacity(band.roads);
    for &line in &band.tape[band.start.context("tip course has no deposition")?..=band.end] {
        let Some((a, b, e)) = modal.apply(line)? else {
            continue;
        };
        let curve = line.starts_with("G2 ") || line.starts_with("G3 ");
        if curve {
            let words = gcode::words(line.split(';').next().unwrap_or(""));
            let points = gcode::arc(
                a[0],
                a[1],
                b[0],
                b[1],
                &words,
                line.starts_with("G2 "),
                0.25,
            );
            let count = points.len() - 1;
            let p = |i: usize| {
                [
                    points[i].0,
                    points[i].1,
                    a[2] + (b[2] - a[2]) * (i as f64 / count as f64),
                ]
            };
            out.extend((0..count).map(|i| Road {
                a: p(i),
                b: p(i + 1),
                e: e / count as f64,
                modal: modal.clone(),
            }));
        } else {
            out.push(Road {
                a,
                b,
                e,
                modal: modal.clone(),
            });
        }
    }
    Ok(out)
}

fn support(road: &Road) -> bool {
    road.modal.feature.starts_with("Support")
}

fn clipped<'a>(
    road: &Road<'a>,
    shoulder: Shoulder,
    portion: Portion,
    world_z: f64,
) -> Vec<Road<'a>> {
    let mut local = 0.0..1.0;
    let mut distant = 0.0..1.0;
    let y = [road.a[1] - shoulder.split_y, road.b[1] - shoulder.split_y];
    let mut out = Vec::new();
    let lower = portion == Portion::Lower;
    let upper = portion == Portion::Upper;
    if portion != Portion::Inclined
        && lower == (world_z < FIRST_INTERFACE)
        && intersect(&mut distant, -y[0], -y[1])
    {
        out.push(road.sub(distant, 1.0));
    }
    if !intersect(&mut local, y[0], y[1]) {
        return out;
    }
    let heights = [shoulder.u(road.a), shoulder.u(road.b)];
    if lower {
        let floor = FIRST_INTERFACE - LANDING;
        if intersect(&mut local, floor - heights[0], floor - heights[1]) {
            out.push(road.sub(local, 1.0));
        }
    } else if upper {
        let top = Shoulder::last_visible();
        let room = heights.map(|u| (u - top) / shoulder.cos);
        let h = road.modal.height;
        let minimum = (MIN_LAYER_SHARE * h).max(0.07);
        if !intersect(&mut local, room[0] - minimum, room[1] - minimum) {
            return out;
        }
        if room[0].min(room[1]) >= h {
            out.push(road.sub(local, 1.0));
        } else {
            let size = distance(road.a, road.b) * (local.end - local.start);
            let count = (size / 0.25).ceil().max(1.0) as usize;
            for i in 0..count {
                let at = |k| local.start + (local.end - local.start) * k as f64 / count as f64;
                let (a, b) = (at(i), at(i + 1));
                let mid = (a + b) * 0.5;
                let share = ((room[0] + mid * (room[1] - room[0])) / h).min(1.0);
                out.push(road.sub(a..b, share));
            }
        }
    } else {
        out.push(road.sub(local, 1.0));
    }
    out
}

fn virtual_z(band: &Band) -> Result<f64> {
    band.tape[band.line..band.start.context("Tip donor course starting line")?]
        .iter()
        .find_map(|line| line.strip_prefix("; HSM_TIP_VIRTUAL_Z: "))
        .context("Tip donor course has no virtual height")?
        .trim()
        .parse()
        .context("Tip donor virtual height")
}

fn same_point(a: [f64; 3], b: [f64; 3]) -> bool {
    a.into_iter()
        .zip(b)
        .all(|(a, b)| (a * 1000.0).round() == (b * 1000.0).round())
}

/// Emit the clipped runs with original deposition settings, and `travel` written between them
/// at each new start.
fn write_roads(out: &mut String, roads: &[Road], phase: &str, z: f64, travel: &mut dyn FnMut(&mut String, [f64; 3], [f64; 3])) {
    let usable = |r: &&Road| r.e >= 0.000005 && !same_point(r.a, r.b);
    let mut moves = roads.iter().filter(usable).peekable();
    let Some(first) = moves.peek() else { return };
    let [x, y, z0] = first.a;
    let _ = write!(
        out,
        "; HSM_TIP_PHASE: {phase}\n; HSM_TIP_COURSE: {z:.5}\n\
        ; HSM_TIP_VIRTUAL_Z: {z:.5}\n; HSM_ENTRY_XYZ: {x:.3} {y:.3} {z0:.3}\n\
        ; HSM_ENTRY_RETRACT_MM: 0.8\nG1 E.8 F1800\n"
    );
    let mut previous = first.a;
    let mut modes: Option<(&str, f64, f64, f64, f64)> = None;
    for r in moves {
        if !same_point(previous, r.a) {
            out.push_str("G1 E-.8 F1800\n");
            travel(out, previous, r.a);
            out.push_str("G1 E.8 F1800\n");
            // the travel set its own acceleration; the road sets its modes again
            modes = None;
        }
        let m = &r.modal;
        let key = (m.feature, m.width, m.height, m.fan, m.acceleration);
        if modes != Some(key) {
            let _ = write!(
                out,
                "; FEATURE: {}\n; LINE_WIDTH: {}\n; LAYER_HEIGHT: {}\nM106 S{}\nM204 S{}\n",
                m.feature, m.width, m.height, m.fan, m.acceleration
            );
            modes = Some(key);
        }
        let [x, y, z] = r.b;
        let feed = m.feed;
        let _ = writeln!(out, "G1 X{x:.3} Y{y:.3} Z{z:.3} E{:.5} F{feed:.5}", r.e);
        previous = r.b;
    }
    out.push_str("G1 E-.8 F1800\n; HSM_TIP_END_COURSE\n");
}

/// A tip course cut to one side of the physical join: its level and its roads.
type Cut<'a> = (f64, Vec<Road<'a>>);

/// Move one tip course to the correct side of the physical join. Courses wholly clear of
/// either cut are passed through untouched, including the source's rear scarf and travel.
#[allow(clippy::type_complexity)]
fn split_tip<'a>(
    tip: &[Band<'a>],
    shoulder: Shoulder,
    upper_z: f64,
    lower_z: f64,
) -> Result<(Vec<Band<'a>>, Vec<Cut<'a>>, Vec<Cut<'a>>, Vec<Band<'a>>)> {
    let (mut before, mut after) = (Vec::new(), Vec::new());
    let (mut lower, mut upper) = (Vec::new(), Vec::new());
    for band in tip {
        if band.hi[2] < lower_z {
            let mut native = band.clone();
            native.phase = "native tip plug and roots".into();
            before.push(native);
        } else if band.lo[2] > upper_z {
            let mut native = band.clone();
            native.phase = "native tip shell".into();
            after.push(native);
        } else {
            let roads = roads(band)?;
            for (out, portion) in [(&mut lower, Portion::Lower), (&mut upper, Portion::Upper)] {
                let laid: Vec<_> = roads
                    .iter()
                    .flat_map(|r| clipped(r, shoulder, portion, band.z))
                    .collect();
                out.push((band.z, laid));
            }
        }
    }
    Ok((before, lower, upper, after))
}

/// The tip returns to the unwarped native tape just above the sloped foundation.
pub fn compose(
    staged_base: &Path,
    native: &Path,
    donor: &Path,
    warp: &Path,
    output: &Path,
    ring: &Path,
    headmap: &Path,
) -> Result<Json> {
    let staged_tape = Tape::read(staged_base)?;
    let native_tape = Tape::read(native)?;
    let donor_tape = Tape::read(donor)?;
    let ring_tape = Tape::read(ring)?;
    let staged_lines = staged_tape.lines();
    let native_lines = native_tape.lines();
    let donor_lines = donor_tape.lines();
    let ring_lines = ring_tape.lines();
    let shoulder = Shoulder::read(warp)?;
    let mut metadata = Metadata::new();

    let (startup, mut authored, mut base_native, footer) = read_staged(&staged_lines)?;
    for band in authored.iter_mut().chain(base_native.iter_mut()) {
        band.phase = shaft_phase(band);
        if band.group != "native" {
            band.metadata = metadata.list(vec![format!("; {}\n", band.label)]);
        }
    }
    let schedule = interleave_shaft(&authored, &base_native, &[])?;
    let native = read_native(&native_lines)?;
    let tip: Vec<_> = native.iter().filter(|b| b.obj == TIP).cloned().collect();
    let covers: Vec<_> = native.iter().filter(|b| b.obj == COVER).cloned().collect();
    let rings = read_custom(&ring_lines, PLATE, &mut metadata)?;
    let donor_bands = read_custom(&donor_lines, TIP, &mut metadata)?;
    let profile = Native::read(&native_lines)?;
    let mut courses: Vec<(f64, &str, Vec<Road>)> = Vec::new();
    let mut limit = [f64::INFINITY, f64::NEG_INFINITY];
    let mut seen_shell = 0;
    for band in &donor_bands {
        let u = virtual_z(band)?;
        if u < FIRST_INTERFACE - 1e-5 || u > Shoulder::last_visible() + 1e-5 {
            continue;
        }
        let mut laid: Vec<_> = roads(band)?
            .iter()
            .flat_map(|r| clipped(r, shoulder, Portion::Inclined, 0.0))
            .collect();
        let visible = u >= FIRST_VISIBLE - 1e-5;
        if !visible {
            ensure!(
                !laid.is_empty() && laid.iter().any(support),
                "The donor has no local interface at {u}"
            );
        } else {
            laid.retain(|r| !support(r));
            ensure!(
                laid.iter().any(|r| r.modal.feature.ends_with("wall")),
                "No visible tip wall at {u}"
            );
            seen_shell += 1;
        }
        for road in &laid {
            limit[0] = limit[0].min(road.a[2]).min(road.b[2]);
            limit[1] = limit[1].max(road.a[2]).max(road.b[2]);
        }
        let phase = if visible {
            "tip yellow shoulder"
        } else {
            "tip shoulder entry"
        };
        courses.push((u, phase, laid));
    }
    ensure!(
        seen_shell == TIP_SHELL_COURSES,
        "Expected {TIP_SHELL_COURSES} tilted tip shell courses, found {seen_shell}"
    );
    let (mut lower_native, lower_cuts, upper_cuts, upper_native) =
        split_tip(&tip, shoulder, limit[1] + 1.2, limit[0] - 0.6)?;
    // The tip's stage lays its level paths below the shoulder, the shoulder's courses and the
    // level paths above it in that order; each crossing between its roads stands as high over
    // the beads already laid, and the course it crosses, as the nozzle and head need.
    let (mut lo, mut hi) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
    for band in &tip {
        for axis in 0..2 {
            lo[axis] = lo[axis].min(band.lo[axis]);
            hi[axis] = hi[axis].max(band.hi[axis]);
        }
    }
    let mut ground = Ground::new(lo, hi, headmap)?;
    for band in &lower_native {
        ground.add(&roads(band)?);
    }
    let mut travels = TipTravels::default();
    let z_hop = profile.z_hop;
    let cross = |ground: &Ground, travels: &mut TipTravels, phase: &str, out: &mut String, a: [f64; 3], b: [f64; 3]| {
        let ends = a[2].max(b[2]);
        let height = ground.floor(a, b, z_hop).max(ends + z_hop);
        let rise = height - a[2];
        let (offset, radius) = profile.spiral(a, b, rise);
        let spiral = ground.spiral_clear(a, [a[0] + offset[0], a[1] + offset[1]], radius, rise);
        travels.note(phase, height - ends, z_hop, spiral && rise <= z_hop + 1e-6);
        profile.travel(out, a, b, height, spiral);
    };
    let (mut lower, mut inclined, mut upper) = (String::new(), String::new(), String::new());
    let below = "tip level paths below shoulder";
    for (z, laid) in &lower_cuts {
        ground.add(laid);
        write_roads(&mut lower, laid, below, *z, &mut |out, a, b| cross(&ground, &mut travels, below, out, a, b));
    }
    for (u, phase, laid) in &courses {
        ground.add(laid);
        write_roads(&mut inclined, laid, phase, *u, &mut |out, a, b| cross(&ground, &mut travels, phase, out, a, b));
    }
    let above = "tip level paths above shoulder";
    for (z, laid) in &upper_cuts {
        ground.add(laid);
        write_roads(&mut upper, laid, above, *z, &mut |out, a, b| cross(&ground, &mut travels, above, out, a, b));
    }
    let lower_lines: Vec<&str> = lower.split_inclusive('\n').collect();
    let incline_lines: Vec<&str> = inclined.split_inclusive('\n').collect();
    let upper_lines: Vec<&str> = upper.split_inclusive('\n').collect();
    lower_native.extend(read_custom(&lower_lines, TIP, &mut metadata)?);
    lower_native.extend(read_custom(&incline_lines, TIP, &mut metadata)?);
    lower_native.extend(read_custom(&upper_lines, TIP, &mut metadata)?);
    lower_native.extend(upper_native);
    let base: Vec<_> = schedule.into_iter().cloned().collect();
    let outgoing = interleave(&base, &lower_native, &covers, &rings)?;
    let all = lower_native
        .iter()
        .chain(&covers)
        .chain(&rings)
        .chain(base.iter().filter(|b| b.obj != TIP && b.obj != COVER));
    each_once(&outgoing, pointers(all))?;
    let (startup, window) = leveling(startup, &native_lines, &outgoing)?;
    let mut report = emit_with(output, &startup, &outgoing, &footer, &metadata, Some(&profile))?;
    report.set("tip_stage_crossings", travels.json());
    report.set(
        "tip_visible_nonplanar_courses",
        Json::Int(seen_shell as i64),
    );
    report.set(
        "tip_virtual_interface_start_mm",
        Json::Float(FIRST_INTERFACE),
    );
    report.set("tip_virtual_first_visible_mm", Json::Float(FIRST_VISIBLE));
    report.set(
        "tip_virtual_shell_end_mm",
        Json::Float(Shoulder::last_visible()),
    );
    report.set("tip_shoulder_world_z_mm", point(&limit));
    report.set(
        "stock_leveling_window_xy_mm",
        Json::List(window.iter().map(|p| point(p)).collect()),
    );
    std::fs::write(
        output.with_extension("json"),
        report.dumps_indented() + "\n",
    )?;
    Ok(report)
}
