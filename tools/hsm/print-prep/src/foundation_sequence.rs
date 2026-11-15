//! Splices inclined tip interface and shell courses into the ordinary Mark2 slice.

use super::*;
use crate::course_field::{distance, mix};
use crate::gcode;
use std::ops::Range;

const FIRST_INTERFACE: f64 = 23.8;
const FIRST_VISIBLE: f64 = 24.8;
const TIP_COURSE_HEIGHT: f64 = 0.2;
const TIP_SHELL_COURSES: usize = 7;
const LANDING: f64 = 0.12;
const MIN_LAYER_SHARE: f64 = 0.3;

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
    let mut modal = Modal::new(Dialect::Tip, entry.xyz, 0.0);
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

/// Emit the clipped runs with original deposition settings and lifts at the new ends.
fn write_roads(out: &mut String, roads: &[Road], phase: &str, z: f64, ceiling: f64) {
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
            let [x, y, z] = r.a;
            let high = previous[2].max(z).max(ceiling) + 1.15;
            let _ = write!(
                out,
                "G1 E-.8 F1800\nG1 Z{high:.3} F900\nG1 X{x:.3} Y{y:.3} F9000\nG1 Z{z:.3} F900\nG1 E.8 F1800\n"
            );
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

/// Move one tip course to the correct side of the physical join. Courses wholly clear of
/// either cut are passed through untouched, including the source's rear scarf and travel.
fn split_tip<'a>(
    tip: &[Band<'a>],
    shoulder: Shoulder,
    upper_z: f64,
    lower_z: f64,
) -> Result<(Vec<Band<'a>>, String, String, Vec<Band<'a>>)> {
    let (mut before, mut after) = (Vec::new(), Vec::new());
    let (mut lower, mut upper) = (String::new(), String::new());
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
            for (out, portion, phase, clearance) in [
                (
                    &mut lower,
                    Portion::Lower,
                    "tip level paths below shoulder",
                    band.hi[2],
                ),
                (
                    &mut upper,
                    Portion::Upper,
                    "tip level paths above shoulder",
                    upper_z,
                ),
            ] {
                let laid: Vec<_> = roads
                    .iter()
                    .flat_map(|r| clipped(r, shoulder, portion, band.z))
                    .collect();
                write_roads(out, &laid, phase, band.z, clearance);
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
    let mut inclined = String::new();
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
        write_roads(&mut inclined, &laid, phase, u, band.hi[2]);
    }
    ensure!(
        seen_shell == TIP_SHELL_COURSES,
        "Expected {TIP_SHELL_COURSES} tilted tip shell courses, found {seen_shell}"
    );
    let (mut lower_native, lower, upper, upper_native) =
        split_tip(&tip, shoulder, limit[1] + 1.2, limit[0] - 0.6)?;
    let lower_lines = splitlines(&lower);
    let incline_lines = splitlines(&inclined);
    let upper_lines = splitlines(&upper);
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
    let mut report = emit(output, &startup, &outgoing, &footer, &metadata)?;
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
