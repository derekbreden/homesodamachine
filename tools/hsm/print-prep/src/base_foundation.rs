//! Lays a faucet base's sloped underside ahead of its plate: a scaffold of level layers and the
//! roof's courses where the slicer's temporary fill stood, then courses parallel to the mounting
//! face. The plate's own G-code follows, the base's level courses kept above that stack and every
//! travel the toolhead would carry into it lifted over it.
//!
//! Production plates lay skin courses across the face with a deck in the bore. The Sculpted
//! trial's foundation lays the foot instead: courses cut from the base's own sections up past its
//! insert sockets' shoulders, with a plug rising in each socket and a deck in the bore.

use crate::mesh::Mesh;
use crate::sloped_courses::{Piece, Point, Region, edge_pieces, hatch, level_order, narrow_pieces, section, uphill_halves};
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use std::path::Path;

// The stack, normal to the mounting face.
pub const COURSE: f64 = 0.24;
const AIR: f64 = 0.24;
const ROOF_COURSES: usize = 3;
/// Sloped courses laid on the sockets' shoulders before the level courses.
const COURSES_OVER_SHOULDER: usize = 1;
/// The courses the base is cut into while its sockets' shoulder is looked for.
const PROBE_COURSES: usize = 24;
const ROOF_WIDTH: f64 = 0.62;
const SKIN_WIDTH: f64 = 0.42;
const SKIN_PITCH: f64 = 0.40;
const LIP: f64 = 2.0;
/// The bore's deck from the slab's edge.
const DECK_KERF: f64 = 0.8;
/// A socket's plug from the socket's wall.
const PLUG_CLEAR: f64 = 0.5;
/// The shoulder's bridge onto the socket's rim.
const SHOULDER_REACH: f64 = 0.3;
/// The fill into the ring beside it.
const OVERLAP: f64 = 0.06;
/// Half the least width the fill is laid in; narrower strips take rings.
const OPEN: f64 = 1.0;
/// The Sculpted trial's rim half-width and half-depth.
const SCULPTED_RIM: [f64; 2] = [29.0, 29.5];
/// The skin courses a production plate lays.
const SKIN_COURSES: usize = 2;
const ELLIPSE_POINTS: usize = 720;
// The scaffold.
const FIRST_LAYER: f64 = 0.20;
const LAYER: f64 = 0.24;
const WALL_PITCH: f64 = 2.5;
const TIE_PITCH: f64 = 10.0;
// Motion.
const FLOW: f64 = 0.9555;
const BRIDGE_FLOW: f64 = 1.25;
const BRIDGE_FAN: &str = "M106 S178";
const Z_PRINT_RATE: f64 = 7.5;
const Z_TRAVEL_RATE: f64 = 15.0;
const TRAVEL_LIFT: f64 = 1.0;
const TRAVEL_SPEED: f64 = 150.0;
const BED_MIN_Z: f64 = 0.2;
// Clearance.
const HEAD_TRAVEL_MARGIN: f64 = 3.0;
const NOZZLE_TRAVEL_MARGIN: f64 = 0.3;
const NOZZLE_FLAT_R: f64 = 0.6;
const FEATHER_MIN: f64 = 0.3;
const KEEP_FRACTION: f64 = 0.5;

fn bead(width: f64, height: f64) -> f64 {
    (width - height) * height + std::f64::consts::PI * (height / 2.0).powi(2)
}

fn e_per_mm(width: f64, height: f64, flow: f64) -> f64 {
    bead(width, height) / (std::f64::consts::PI * 0.875 * 0.875) * FLOW * flow
}

fn dist3(a: [f64; 3], b: [f64; 3]) -> f64 {
    ((b[0] - a[0]).powi(2) + (b[1] - a[1]).powi(2) + (b[2] - a[2]).powi(2)).sqrt()
}

/// `count` values from `start` to `end`, both ends included.
fn spread(start: f64, end: f64, count: usize) -> impl Iterator<Item = f64> {
    (0..count).map(move |i| if i + 1 == count { end } else { start + (end - start) * i as f64 / (count - 1) as f64 })
}

/// The mounting face's frame: `a` across the slope, `b` up it, `n` along its normal.
#[derive(Clone, Copy, Debug)]
pub struct Frame {
    pub cx: f64,
    pub cy: f64,
    pub cz: f64,
    pub s: f64,
    pub c: f64,
    pub t: f64,
    /// The rim's half-width and half-depth.
    pub rim: [f64; 2],
}

impl Frame {
    pub fn new(seat: [f64; 3], rim: [f64; 2]) -> Self {
        let tilt = hsm_faucet_numbers::shell::PRINT_BASE_BUILD_ROT;
        Self { cx: seat[0], cy: seat[1], cz: seat[2], s: tilt.sin(), c: tilt.cos(), t: tilt.tan(), rim }
    }

    pub fn xyz(&self, a: f64, b: f64, n: f64) -> [f64; 3] {
        [self.cx + a, self.cy - b * self.c + n * self.s, self.cz + b * self.s + n * self.c]
    }

    fn at(&self, p: Point, n: f64) -> [f64; 3] {
        self.xyz(p[0], p[1], n)
    }

    /// The mounting face's height over the plate at `y`.
    pub fn face(&self, y: f64) -> f64 {
        self.cz - (y - self.cy) * self.t
    }

    pub fn b_at_height(&self, z: f64, n: f64) -> f64 {
        (z - self.cz - n * self.c) / self.s
    }

    /// `shape` where a bead topped at `n_top` stands at least a first layer over the bed.
    fn limited(&self, shape: &Region, n_top: f64) -> Region {
        shape.above(self.b_at_height(BED_MIN_Z, n_top))
    }
}

/// Relative-extrusion G-code with a tracked nozzle, for the courses this stage adds.
#[derive(Default)]
pub struct Writer {
    pub out: Vec<String>,
    pub pos: Option<[f64; 3]>,
    pub retracted: bool,
    pub time: f64,
    pub filament: f64,
    pub lengths: Vec<(String, f64)>,
    pub feature: Option<String>,
}

impl Writer {
    pub fn new() -> Self {
        Self { retracted: true, ..Default::default() }
    }

    pub fn raw(&mut self, text: impl Into<String>) {
        self.out.push(text.into());
    }

    pub fn comment_feature(&mut self, name: &str, width: f64) {
        self.feature = Some(name.to_string());
        self.out.push(format!("; FEATURE: {name}"));
        self.out.push(format!("; LINE_WIDTH: {width:.2}"));
    }

    fn line(&mut self, target: [f64; 3], e: Option<f64>, feed: f64) {
        let mut words = Vec::new();
        for (i, letter) in ["X", "Y", "Z"].into_iter().enumerate() {
            if self.pos.is_none_or(|p| (target[i] - p[i]).abs() > 5e-4) {
                words.push(format!("{letter}{:.3}", target[i]));
            }
        }
        if words.is_empty() && e.is_none() {
            return;
        }
        let mut text = format!("G1 {}", words.join(" "));
        if let Some(e) = e {
            text.push_str(&format!(" E{e:.5}"));
        }
        text.push_str(&format!(" F{:.0}", feed * 60.0));
        self.out.push(text);
        if let Some(p) = self.pos {
            let d = dist3(p, target);
            self.time += d / feed.max(1e-6);
            if let Some(e) = e.filter(|e| *e != 0.0) {
                let feature = self.feature.clone().unwrap_or_default();
                match self.lengths.iter_mut().find(|(f, _)| *f == feature) {
                    Some(slot) => slot.1 += d,
                    None => self.lengths.push((feature, d)),
                }
                self.filament += e;
            }
        }
        self.pos = Some(target);
    }

    pub fn retract(&mut self) {
        if !self.retracted {
            self.out.push("G1 E-0.8 F1800".into());
            self.time += 0.8 / 30.0;
            self.retracted = true;
        }
    }

    pub fn unretract(&mut self) {
        if self.retracted {
            self.out.push("G1 E0.8 F1800".into());
            self.time += 0.8 / 30.0;
            self.retracted = false;
        }
    }

    /// Lift, cross and lower; a crossing shorter than `hop` runs along the course in hand.
    pub fn travel(&mut self, target: [f64; 3], lift: f64, hop: f64) {
        let Some([x0, y0, z0]) = self.pos else {
            self.out.push(format!("G1 Z{:.3} F1800", target[2] + lift + 4.0));
            self.out.push(format!("G1 X{:.3} Y{:.3} F{:.0}", target[0], target[1], TRAVEL_SPEED * 60.0));
            self.pos = Some([target[0], target[1], target[2] + lift + 4.0]);
            self.line(target, None, 20.0);
            return;
        };
        let flat = (target[0] - x0).hypot(target[1] - y0);
        if flat < hop && (target[2] - z0).abs() < 0.5 && !self.retracted {
            self.line(target, None, TRAVEL_SPEED.min(60.0));
            return;
        }
        self.retract();
        self.line([x0, y0, z0 + lift], None, 20.0);
        let dz = (target[2] - z0).abs();
        let feed = if dz < 1e-9 { TRAVEL_SPEED } else { TRAVEL_SPEED.min(Z_TRAVEL_RATE * flat.hypot(dz) / dz) };
        self.line([target[0], target[1], target[2] + lift], None, feed);
        self.line(target, None, 20.0);
    }

    /// Lays a bead along `path`; `flows` gives each segment its own share of the flow.
    pub fn extrude(&mut self, path: &[[f64; 3]], width: f64, height: f64, speed: f64, flow: f64, flows: Option<&[f64]>) {
        self.unretract();
        for i in 1..path.len() {
            let (a, b) = (path[i - 1], path[i]);
            let d = dist3(a, b);
            if d < 1e-6 {
                continue;
            }
            let share = flows.map_or(1.0, |f| f[i - 1].max(0.0));
            let dz = (b[2] - a[2]).abs();
            let feed = if dz < 1e-9 { speed } else { speed.min(Z_PRINT_RATE * d / dz) };
            self.line(b, Some(e_per_mm(width, height, flow * share) * d), feed);
        }
    }

    /// Leaves at `z`, above everything, retracted and at the plate's first-layer temperature, as
    /// the plate's first layer expects, and closes the base's object with `closing`.
    pub fn park(&mut self, z: f64, temperature: &str, closing: &[String]) -> Result<()> {
        self.retract();
        let [x, y, _] = self.pos.context("the preamble laid nothing")?;
        self.line([x, y, z], None, 25.0);
        self.raw(format!("M104 S{temperature} ; the plate's first-layer temperature"));
        self.raw("M625");
        self.out.extend(closing.iter().cloned());
        self.raw("; ===== end of the sloped underside =====");
        Ok(())
    }
}

/// The planes the preamble's stack is laid on, normal to the mounting face.
pub struct Stack {
    pub n_scaffold: f64,
    pub n_roof: [f64; ROOF_COURSES],
    pub scaffold_layers: usize,
    pub scaffold_top: f64,
}

/// How a method opens its preamble and lays its roof's first course.
pub struct Opening {
    /// The preamble's title.
    pub title: String,
    /// The lines that open the base's object on the plate.
    pub object: Vec<String>,
    /// The plate's nozzle temperature for its regular layers.
    pub temperature: String,
    /// Lay the roof's first course line by line, each after those just downhill of it, rather
    /// than row by row.
    pub level_roof: bool,
}

/// The preamble's opening, its scaffold of level layers and its roof courses.
pub fn scaffold_and_roof(w: &mut Writer, frame: &Frame, opening: &Opening) -> Result<Stack> {
    let n_roof: [f64; ROOF_COURSES] = std::array::from_fn(|i| -AIR - COURSE * (ROOF_COURSES - 1 - i) as f64);
    let n_scaffold = -AIR - COURSE * ROOF_COURSES as f64;
    w.raw(opening.title.clone());
    w.out.extend(opening.object.iter().cloned());
    w.raw("G90");
    w.raw("M83");
    w.raw("M106 S0");
    let (sx, sy) = (frame.rim[0] + LIP, (frame.rim[1] + LIP) * frame.c);
    let y_centre = frame.cy + n_scaffold * frame.s;
    let span_x = |y: f64| {
        let r = 1.0 - ((y - y_centre) / sy).powi(2);
        (r > 0.0).then(|| (frame.cx - sx * r.sqrt(), frame.cx + sx * r.sqrt()))
    };
    let span_y = |x: f64| {
        let r = 1.0 - ((x - frame.cx) / sx).powi(2);
        (r > 0.0).then(|| (y_centre - sy * r.sqrt(), y_centre + sy * r.sqrt()))
    };
    // each layer reaches back to its nose, where the roof's lowest course meets it
    let mut layers = Vec::new();
    for index in 0.. {
        let z = ((FIRST_LAYER + LAYER * index as f64) * 1e6).round() / 1e6;
        let nose = frame.cy - frame.b_at_height(z, n_scaffold) * frame.c + n_scaffold * frame.s;
        if nose - ROOF_WIDTH <= y_centre - sy {
            break;
        }
        layers.push((z, nose));
    }
    w.raw("M204 S500");
    let count = layers.len();
    for (index, &(z, nose)) in layers.iter().enumerate() {
        w.raw(format!("; scaffold layer {} of {count}", index + 1));
        let height = if index == 0 { FIRST_LAYER } else { LAYER };
        let speed = if index == 0 { 40.0 } else { 80.0 };
        if index == 1 {
            w.raw(format!("M104 S{} ; the plate's regular-layer temperature", opening.temperature));
            w.raw("M204 S3000");
        }
        w.comment_feature("Support", ROOF_WIDTH);
        let back = (nose - ROOF_WIDTH / 2.0).min(y_centre + sy - 0.05);
        let mut paths: Vec<Vec<[f64; 3]>> = Vec::new();
        // the outline in front of the nose, one arc from side to side, and the nose's chord
        if back > y_centre - sy + 0.5 {
            let t0 = ((back - y_centre) / sy).clamp(-1.0, 1.0).asin();
            let steps = (((std::f64::consts::PI + 2.0 * t0) * sx) as usize).max(8);
            let ts = spread(std::f64::consts::PI - t0, std::f64::consts::TAU + t0, steps);
            paths.push(ts.map(|t| [frame.cx + sx * t.cos(), y_centre + sy * t.sin(), z]).collect());
            if let Some(sp) = span_x(back).filter(|sp| sp.1 - sp.0 > 1.0) {
                paths.push(vec![[sp.1, back, z], [sp.0, back, z]]);
            }
        }
        let pitch = if index == 0 { WALL_PITCH / 2.0 } else { WALL_PITCH };
        let reach = (sx / pitch).floor() as i64;
        let mut walls = Vec::new();
        for j in -reach..=reach {
            let x = frame.cx + j as f64 * pitch;
            let Some(sp) = span_y(x) else { continue };
            let (y0, y1) = (sp.0 + ROOF_WIDTH / 2.0, (sp.1 - ROOF_WIDTH / 2.0).min(back - ROOF_WIDTH / 2.0));
            if y1 - y0 > 1.0 {
                walls.push(vec![[x, y0, z], [x, y1, z]]);
            }
        }
        for (k, mut wall) in walls.into_iter().enumerate() {
            if k % 2 == 1 {
                wall.reverse();
            }
            paths.push(wall);
        }
        if index == 0 || index % 2 == 1 {
            let tie = if index == 0 { TIE_PITCH / 2.0 } else { TIE_PITCH };
            let ties = (0..).map(|k| y_centre - sy + tie / 2.0 + k as f64 * tie).take_while(|y| *y < back - 2.0);
            for (k, y) in ties.enumerate() {
                if let Some(sp) = span_x(y).filter(|sp| sp.1 - sp.0 > 2.0) {
                    let mut line = vec![[sp.0 + ROOF_WIDTH / 2.0, y, z], [sp.1 - ROOF_WIDTH / 2.0, y, z]];
                    if k % 2 == 1 {
                        line.reverse();
                    }
                    paths.push(line);
                }
            }
        }
        for path in &paths {
            w.travel(path[0], 0.6, 1.5);
            w.extrude(path, ROOF_WIDTH, height, speed, 1.0, None);
        }
    }
    let tops: Vec<f64> = layers.iter().map(|l| l.0).collect();
    // the scaffold's top under the roof at y, or the bed
    let top_below = |y: f64| {
        let limit = frame.face(y) + n_scaffold / frame.c;
        tops.iter().copied().filter(|z| *z <= limit + 1e-6).last().unwrap_or(0.0)
    };
    let roof = Region::ellipse(frame.rim[0] + LIP, frame.rim[1] + LIP, ELLIPSE_POINTS);
    // the first course: level lines across the slope, each on the scaffold under it
    w.raw(format!("; underside roof course 1 of {ROOF_COURSES}"));
    w.raw("M204 S2000");
    w.comment_feature("Support interface", ROOF_WIDTH);
    let rows = hatch(&frame.limited(&roof, n_roof[0]), 0.0, ROOF_WIDTH, 1.0);
    let (lines, hop) = if opening.level_roof {
        (level_order(&rows), 4.0)
    } else {
        let back_and_forth = rows.iter().enumerate().flat_map(|(k, pieces)| -> Vec<(Point, Point)> {
            if k % 2 == 0 { pieces.clone() } else { pieces.iter().rev().map(|&(p, q)| (q, p)).collect() }
        });
        (back_and_forth.collect(), 1.5)
    };
    for (a, b) in lines {
        let (p0, p1) = (frame.at(a, n_roof[0]), frame.at(b, n_roof[0]));
        let height = p0[2] - top_below(p0[1]);
        ensure!((0.19..=COURSE / frame.c + LAYER + 1e-6).contains(&height), "a roof line stands {height} over the scaffold");
        w.travel(p0, 0.5, hop);
        w.extrude(&[p0, p1], ROOF_WIDTH, height, 50.0, 1.0, None);
    }
    // the others: lines up the slope, then diagonal; each line climbs, since coming down
    // the nozzle's shoulder would ride on the bead it had just laid
    for (course, (n_top, angle)) in [(n_roof[1], 90.0), (n_roof[2], 45.0)].into_iter().enumerate() {
        w.raw(format!("; underside roof course {} of {ROOF_COURSES}", course + 2));
        for (a, b) in hatch(&frame.limited(&roof, n_top), angle, ROOF_WIDTH, 1.0).into_iter().flatten() {
            let path = [frame.at(a, n_top), frame.at(b, n_top)];
            w.travel(path[0], TRAVEL_LIFT, 1.5);
            w.extrude(&path, ROOF_WIDTH, COURSE, 40.0, 1.0, None);
        }
    }
    let top = tops.last().copied().context("the scaffold has no layer")?;
    Ok(Stack { n_scaffold, n_roof, scaffold_layers: tops.len(), scaffold_top: top })
}

/// The base's sections for the foot's courses, lowest first, and the course that first lays
/// its insert sockets' shoulders: the first whose small openings have closed down to the
/// inserts' pilots.
pub struct Foot {
    regions: Vec<Region>,
    shoulder: usize,
}

impl Foot {
    /// The base cut parallel to its mounting face through the middle of each course.
    pub fn cut(stl: &Path) -> Result<Foot> {
        let mesh = Mesh::read_stl(stl)?;
        mesh.check_closed_single_body("faucet base")?;
        let mut probe = Vec::with_capacity(PROBE_COURSES);
        for k in 1..=PROBE_COURSES {
            // CAD y runs down the slope, so b = -y
            let rings: Vec<Vec<Point>> = section(&mesh, (k as f64 - 0.5) * COURSE)?.into_iter()
                .map(|r| r.into_iter().map(|p| [p[0], -p[1]]).collect())
                .collect();
            let region = Region::from_rings(&rings);
            ensure!(region.pieces() == 1, "the base's course {k} is not one piece");
            probe.push(region);
        }
        let small = |r: &Region| {
            let mut areas: Vec<f64> = r.holes().iter().map(Region::area).collect();
            areas.sort_by(f64::total_cmp);
            areas.pop();
            areas
        };
        let sockets = small(&probe[0]);
        ensure!(sockets.len() == 3, "the mounting face does not open on three insert sockets");
        let shoulder = 1 + probe.iter()
            .position(|r| small(r).into_iter().fold(f64::NEG_INFINITY, f64::max) < 0.6 * sockets[0])
            .context("no course closes the sockets down to their pilots")?;
        let regions: Vec<Region> = probe.into_iter().take(shoulder + COURSES_OVER_SHOULDER).collect();
        let reach = regions.iter().fold([0.0_f64; 2], |m, r| {
            let (lo, hi) = r.bounds();
            [m[0].max(lo[0].abs()).max(hi[0].abs()), m[1].max(lo[1].abs()).max(hi[1].abs())]
        });
        ensure!(reach[0] + SKIN_WIDTH < SCULPTED_RIM[0] + LIP && reach[1] + SKIN_WIDTH < SCULPTED_RIM[1] + LIP,
            "the foot's courses reach past the roof's lip");
        Ok(Foot { regions, shoulder })
    }
}

/// What the foot's courses laid, as the stage reports it.
#[derive(Default)]
pub struct FootLaid {
    pub ring_pieces: usize,
    pub narrow_rings: usize,
    pub fill_lines: usize,
    pub sloped_courses: usize,
    pub shoulder_course: usize,
    pub slab_top: f64,
    pub plug_top: f64,
    pub deck_top: f64,
}

/// One feature of a course as it is laid: its rings and its fill.
struct Feature<'a> {
    pitch: f64,
    ring_speed: f64,
    fill_speed: f64,
    flow: f64,
    ring: &'a str,
    fill: &'a str,
    lap: f64,
}

const BRIDGE: Feature<'static> = Feature { pitch: SKIN_PITCH, ring_speed: 15.0, fill_speed: 15.0, flow: BRIDGE_FLOW, ring: "Bridge", fill: "Bridge", lap: 0.5 };

/// The foot's G-code, laid into the preamble.
struct Laying<'a> {
    w: &'a mut Writer,
    frame: &'a Frame,
    laid: FootLaid,
}

impl Laying<'_> {
    fn pieces(&mut self, pieces: &[Piece], n_top: f64, width: f64, speed: f64, flow: f64, height: f64) {
        for (pts, flows) in pieces {
            let path: Vec<[f64; 3]> = pts.iter().map(|p| self.frame.at(*p, n_top)).collect();
            // a whisker lays nothing worth having
            let shares: Vec<f64> = flows.windows(2).map(|f| (f[0] + f[1]) / 2.0).map(|s| if s < 0.12 { 0.0 } else { s }).collect();
            self.w.travel(path[0], TRAVEL_LIFT, 1.5);
            self.w.extrude(&path, width, height, speed, flow, Some(&shares));
        }
    }

    fn lines(&mut self, rows: &[Vec<(Point, Point)>], n_top: f64, angle: f64, width: f64, speed: f64, flow: f64, height: f64) -> usize {
        let lines = if angle == 0.0 { level_order(rows) } else { rows.iter().flatten().copied().collect() };
        for &(a, b) in &lines {
            let path = [self.frame.at(a, n_top), self.frame.at(b, n_top)];
            // from one level line to the next the nozzle runs along the course it is laying
            self.w.travel(path[0], TRAVEL_LIFT, if angle == 0.0 { 4.0 } else { 1.5 });
            self.w.extrude(&path, width, height, speed, flow, None);
        }
        lines.len()
    }

    /// One course of the foot: the rings its stock lies uphill of, the rings of its narrow
    /// strips, the fill, then the rings its stock lies downhill of. A backing wall doubles the
    /// rings inside the outer ones.
    fn course(&mut self, region: &Region, n_top: f64, angle: f64, f: &Feature, backing_wall: bool) {
        if region.is_empty() {
            return;
        }
        let (mut first, mut last) = edge_pieces(&region.offset(-SKIN_WIDTH / 2.0), f.lap);
        let backing = if backing_wall { SKIN_WIDTH } else { 0.0 };
        let mut fill = region.offset(-(SKIN_WIDTH + backing + f.pitch / 2.0 - OVERLAP));
        if !fill.is_empty() {
            fill = fill.offset(-OPEN).offset(OPEN).and(&fill);
        }
        let mut narrow = narrow_pieces(region, SKIN_WIDTH, f.pitch, &fill);
        if backing_wall {
            // the inner pair replaces the first narrow-ring band; any narrower stock farther in stays
            let (inner_first, inner_last) = edge_pieces(&region.offset(-1.5 * SKIN_WIDTH), f.lap);
            let ring_stock = region.offset(-2.0 * SKIN_WIDTH + 0.06);
            narrow.retain(|(pts, _)| ring_stock.covers(pts));
            first.extend(inner_first);
            last = [inner_last, last].concat();
        }
        self.w.comment_feature(f.ring, SKIN_WIDTH);
        self.pieces(&first, n_top, SKIN_WIDTH, f.ring_speed, f.flow, COURSE);
        self.pieces(&narrow, n_top, SKIN_WIDTH, f.ring_speed, f.flow, COURSE);
        self.w.comment_feature(f.fill, SKIN_WIDTH);
        self.laid.fill_lines += self.lines(&hatch(&fill, angle, f.pitch, 0.8), n_top, angle, SKIN_WIDTH, f.fill_speed, f.flow, COURSE);
        self.w.comment_feature(f.ring, SKIN_WIDTH);
        self.pieces(&last, n_top, SKIN_WIDTH, f.ring_speed, f.flow, COURSE);
        self.laid.ring_pieces += first.len() + last.len();
        self.laid.narrow_rings += narrow.len();
    }

    /// One course of a plug or of the deck: a ring and lines inside it.
    fn support(&mut self, shape: &Region, n_top: f64, angle: f64, pitch: f64, height: f64) {
        if shape.is_empty() {
            return;
        }
        let (first, last) = edge_pieces(&shape.offset(-ROOF_WIDTH / 2.0), 0.6);
        self.pieces(&[first, last].concat(), n_top, ROOF_WIDTH, 30.0, 1.0, height);
        self.lines(&hatch(&shape.offset(-ROOF_WIDTH * 0.9), angle, pitch, 0.8), n_top, angle, ROOF_WIDTH, 40.0, 1.0, height);
    }
}

/// The foot's sloped courses on the roof, with the plugs and the deck rising beside them.
/// `deck_top` stops the deck short of the slab's top, and the last course then takes a backing
/// wall.
pub fn lay_foot(w: &mut Writer, frame: &Frame, foot: &Foot, deck_top: Option<f64>) -> Result<FootLaid> {
    let regions = &foot.regions;
    let count = regions.len();
    let mut openings = regions[0].holes();
    openings.sort_by(|a, b| b.area().total_cmp(&a.area()));
    ensure!(!openings.is_empty(), "the mounting face has no bore");
    let bore = openings.remove(0);
    let sockets = openings;
    let deck = bore.offset(-DECK_KERF);
    let plugs: Vec<Region> = sockets.iter().map(|s| s.offset(-PLUG_CLEAR)).collect();
    // the last course the plugs rise with
    let plug_top = foot.shoulder.saturating_sub(2);
    let slab_top = count as f64 * COURSE;
    let deck_top = deck_top.unwrap_or(slab_top);
    ensure!((count - 1) as f64 * COURSE < deck_top && deck_top <= slab_top, "the deck's top {deck_top} is not in the last course");
    let laid = FootLaid { sloped_courses: count, shoulder_course: foot.shoulder, slab_top, plug_top: plug_top as f64 * COURSE, deck_top, ..Default::default() };
    let mut lay = Laying { w, frame, laid };
    // the plugs and the deck start on the roof, level with the mounting face
    lay.w.raw("; underside deck bedding");
    lay.w.comment_feature("Support", ROOF_WIDTH);
    lay.support(&frame.limited(&deck, 0.0), 0.0, 0.0, ROOF_WIDTH, COURSE);
    for plug in &plugs {
        lay.support(&frame.limited(plug, 0.0), 0.0, 0.0, ROOF_WIDTH, COURSE);
    }
    lay.w.raw("M204 S1000");
    for k in 1..=count {
        let n_top = k as f64 * COURSE;
        let region = &regions[k - 1];
        let angle = if k % 2 == 1 { 90.0 } else { 0.0 };
        let fill_speed = if angle != 0.0 { 40.0 } else { 50.0 };
        let wall = |flow| Feature { pitch: SKIN_WIDTH, ring_speed: 25.0, fill_speed, flow, ring: "Outer wall", fill: "Internal solid infill", lap: 1.2 };
        lay.w.raw(format!("; sloped course {k} of {count}"));
        if k == 1 {
            // the first course crosses the roof's air as a bridge, as Support D lays it
            lay.w.raw(format!("{BRIDGE_FAN} ; the first course over air takes the bridge's fan"));
            lay.course(region, n_top, 90.0, &Feature { ring: "Bottom surface", fill: "Bottom surface", ..BRIDGE }, false);
            lay.w.raw("M106 S0");
        } else if k == foot.shoulder {
            // the sockets' shoulders cross the plugs' air the same way, after the rest of the course
            let zone = sockets.iter().fold(Region::default(), |z, s| z.union(&s.offset(SHOULDER_REACH)));
            lay.course(&region.minus(&zone), n_top, angle, &wall(1.0), false);
            lay.w.raw(format!("{BRIDGE_FAN} ; the shoulders over the plugs take the bridge's fan"));
            lay.course(&region.and(&zone), n_top, 90.0, &BRIDGE, false);
            lay.w.raw("M106 S0");
        } else {
            let flow = if k == 2 { 1.05 } else { 1.0 };
            lay.course(region, n_top, angle, &wall(flow), deck_top < slab_top && k == count);
        }
        lay.w.comment_feature("Support", ROOF_WIDTH);
        let deck_n = n_top.min(deck_top);
        let pitch = if k + 3 > count { ROOF_WIDTH } else { 3.0 * ROOF_WIDTH };
        lay.support(&deck, deck_n, angle, pitch, deck_n - (k - 1) as f64 * COURSE);
        if k <= plug_top {
            for plug in &plugs {
                lay.support(plug, n_top, angle, ROOF_WIDTH, COURSE);
            }
        }
    }
    Ok(lay.laid)
}

/// A production base's mounting face in its own plane, from the base's lowest faces: the face
/// and its bore.
pub struct Skin {
    region: Region,
    bore: Region,
}

impl Skin {
    pub fn cut(stl: &Path) -> Result<Skin> {
        let mesh = Mesh::read_stl(stl)?;
        let low = mesh.vertices.iter().map(|p| p[2]).fold(f64::INFINITY, f64::min);
        let faces: Vec<Vec<Point>> = mesh.faces.iter()
            .filter(|f| f.iter().all(|&i| (mesh.vertices[i][2] - low).abs() < 1e-6))
            .map(|f| f.iter().map(|&i| [mesh.vertices[i][0], -mesh.vertices[i][1]]).collect())
            .collect();
        let region = Region::from_rings(&faces);
        let mut holes = region.holes();
        ensure!(region.pieces() == 1 && holes.len() == 4, "the mounting face is not the ring with four openings");
        holes.sort_by(|a, b| b.area().total_cmp(&a.area()));
        Ok(Skin { region, bore: holes.swap_remove(0) })
    }
}

/// The bore's deck and the skin's courses on the roof: in each course a ring at every edge, laid
/// in halves up the slope, then lines across the face, each stopping short of the ring above it.
/// Returns the ring halves laid.
pub fn lay_skin(w: &mut Writer, frame: &Frame, skin: &Skin) -> usize {
    const PULL_BACK: f64 = 0.2;
    let n_skin: [f64; SKIN_COURSES] = std::array::from_fn(|i| COURSE * (i + 1) as f64);
    let lines = |region: &Region, angle: f64, pitch: f64| -> Vec<(Point, Point)> {
        let (s, c) = angle.to_radians().sin_cos();
        hatch(region, angle, pitch, 0.5).into_iter().flatten()
            .map(|(a, b)| if s > 1e-9 { (a, [b[0] - c * PULL_BACK, b[1] - s * PULL_BACK]) } else { (a, b) })
            .collect()
    };
    // the bore's deck, level with the face, for the trees that stand inside the base
    for (a, b) in hatch(&frame.limited(&skin.bore.offset(-DECK_KERF), 0.0), 135.0, ROOF_WIDTH, 1.0).into_iter().flatten() {
        let (lo, hi) = if a[1] <= b[1] { (a, b) } else { (b, a) };
        let path = [frame.at(lo, 0.0), frame.at(hi, 0.0)];
        w.travel(path[0], TRAVEL_LIFT, 1.5);
        w.extrude(&path, ROOF_WIDTH, COURSE, 40.0, 1.0, None);
    }
    let edge = skin.region.offset(-SKIN_WIDTH / 2.0);
    let mut halves = 0;
    let mut rings = |w: &mut Writer, n_top: f64, speed: f64, flow: f64| {
        for ring in edge.rings() {
            for half in uphill_halves(&ring) {
                let path: Vec<[f64; 3]> = half.iter().map(|p| frame.at(*p, n_top)).collect();
                w.travel(path[0], TRAVEL_LIFT, 1.5);
                w.extrude(&path, SKIN_WIDTH, COURSE, speed, flow, None);
                halves += 1;
            }
        }
    };
    let fill = |w: &mut Writer, lines: Vec<(Point, Point)>, n_top: f64, speed: f64, flow: f64| {
        for (a, b) in lines {
            let path = [frame.at(a, n_top), frame.at(b, n_top)];
            w.travel(path[0], TRAVEL_LIFT, 1.5);
            w.extrude(&path, SKIN_WIDTH, COURSE, speed, flow, None);
        }
    };
    // the first course crosses the roof's air as a bridge: lines straight up the slope
    w.raw("M204 S1000");
    w.raw(format!("{BRIDGE_FAN} ; the first course over air takes the bridge's fan"));
    w.comment_feature("Bottom surface", SKIN_WIDTH);
    rings(w, n_skin[0], 15.0, BRIDGE_FLOW);
    fill(w, lines(&skin.region.offset(-(SKIN_WIDTH + SKIN_PITCH / 2.0 - 0.06)), 90.0, SKIN_PITCH), n_skin[0], 15.0, BRIDGE_FLOW);
    w.raw("M106 S0");
    // the second: diagonal lines across the first
    w.comment_feature("Bottom surface", SKIN_WIDTH);
    rings(w, n_skin[1], 25.0, 1.0);
    w.comment_feature("Internal solid infill", SKIN_WIDTH);
    fill(w, lines(&skin.region.offset(-(SKIN_WIDTH + SKIN_WIDTH / 2.0 - 0.06)), 45.0, SKIN_WIDTH), n_skin[1], 40.0, 1.03);
    halves
}

/// The lowest the active tip may sit at each plate position with the toolhead clear of the
/// finished scaffold, roof and courses.
pub struct Clearance {
    step: f64,
    cx0: f64,
    cy0: f64,
    rows: usize,
    cols: usize,
    head: Vec<f64>,
    nozzle: Vec<f64>,
}

impl Clearance {
    /// `top` gives the finished stack's top along the face's normal at a point of the face.
    pub fn new(headmap: &Path, frame: &Frame, top: &dyn Fn(Point) -> f64) -> Result<Self> {
        let arrays = crate::npz::read_arrays(headmap)?;
        let get = |name: &str| arrays.get(name).with_context(|| format!("the head map has no {name}"));
        let (h, n) = (get("H")?, get("N")?);
        let scalar = |name: &str| -> Result<f64> { get(name)?.f64().and_then(|v| v.first().copied()).with_context(|| format!("{name} is a number")) };
        let (hs, hx0, hy0) = (scalar("step")?, scalar("x0")?, scalar("y0")?);
        let step = 0.5;
        ensure!((hs - step).abs() < 1e-9, "the head map's step is not the clearance step");
        let (hr, hc) = (h.shape[0], h.shape[1]);
        ensure!(n.shape == h.shape, "the head and nozzle maps differ in shape");
        let (hv, nv) = (h.f64().context("H")?, n.f64().context("N")?);
        // the terrain: the stack's top wherever the roof reaches
        let (ra, rb) = (frame.rim[0] + LIP, frame.rim[1] + LIP);
        let tx0 = ((frame.cx - ra - 1.0) / step).floor() * step;
        let ty0 = ((frame.cy - rb * frame.c - 1.5) / step).floor() * step;
        let nx = ((2.0 * ra + 2.0) / step).ceil() as usize + 1;
        let ny = ((2.0 * rb * frame.c + 3.0) / step).ceil() as usize + 1;
        let mut terrain = vec![f64::NEG_INFINITY; nx * ny];
        for j in 0..ny {
            let y = ty0 + j as f64 * step;
            for i in 0..nx {
                let x = tx0 + i as f64 * step;
                let (a, b) = (x - frame.cx, (frame.cy - y) / frame.c);
                if (a / ra).powi(2) + (b / rb).powi(2) <= 1.0 {
                    terrain[j * nx + i] = (frame.face(y) + top([a, b]) / frame.c).max(0.0);
                }
            }
        }
        // the lowest each head cell may stand over the terrain, as a dilation of the terrain by
        // the head's underside; the nozzle's own flat stands clear of the flank map
        let cx0 = tx0 - hx0 - (hc - 1) as f64 * step;
        let cy0 = ty0 - hy0 - (hr - 1) as f64 * step;
        let (cols, rows) = (nx + hc - 1, ny + hr - 1);
        let mut head = vec![f64::NEG_INFINITY; rows * cols];
        let mut nozzle = vec![f64::NEG_INFINITY; rows * cols];
        let mut flank = nv.to_vec();
        for j in 0..hr {
            for i in 0..hc {
                if (hx0 + i as f64 * step).hypot(hy0 + j as f64 * step) < NOZZLE_FLAT_R {
                    flank[j * hc + i] = f64::INFINITY;
                }
            }
        }
        for (target, source) in [(&mut head, hv), (&mut nozzle, &flank[..])] {
            for j in 0..hr {
                for i in 0..hc {
                    let s = source[j * hc + i];
                    if !s.is_finite() {
                        continue;
                    }
                    let (r0, c0) = (hr - 1 - j, hc - 1 - i);
                    for y in 0..ny {
                        let row = &mut target[(r0 + y) * cols + c0..(r0 + y) * cols + c0 + nx];
                        for (cell, t) in row.iter_mut().zip(&terrain[y * nx..(y + 1) * nx]) {
                            *cell = cell.max(t - s);
                        }
                    }
                }
            }
        }
        Ok(Self { step, cx0, cy0, rows, cols, head, nozzle })
    }

    fn sample(&self, grid: &[f64], x: f64, y: f64) -> f64 {
        let i = ((x - self.cx0) / self.step).round_ties_even();
        let j = ((y - self.cy0) / self.step).round_ties_even();
        if i >= 0.0 && (i as usize) < self.cols && j >= 0.0 && (j as usize) < self.rows {
            grid[j as usize * self.cols + i as usize]
        } else {
            f64::NEG_INFINITY
        }
    }

    pub fn head_floor(&self, x: f64, y: f64) -> f64 {
        self.sample(&self.head, x, y)
    }

    /// The lowest a travel may run from (`x0`, `y0`) to (`x1`, `y1`).
    pub fn travel_floor(&self, x0: f64, y0: f64, x1: f64, y1: f64) -> f64 {
        let count = (((x1 - x0).hypot(y1 - y0) / (self.step * 0.8)) as usize + 2).max(2);
        spread(0.0, 1.0, count).map(|t| {
            let (x, y) = (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t);
            (self.sample(&self.head, x, y) + HEAD_TRAVEL_MARGIN).max(self.sample(&self.nozzle, x, y) + NOZZLE_TRAVEL_MARGIN)
        }).fold(f64::NEG_INFINITY, f64::max)
    }

    fn reach(&self) -> [f64; 4] {
        [self.cx0 - 1.0, self.cx0 + self.cols as f64 * self.step + 1.0, self.cy0 - 1.0, self.cy0 + self.rows as f64 * self.step + 1.0]
    }

    pub fn near(&self, x: f64, y: f64) -> bool {
        let [x0, x1, y0, y1] = self.reach();
        x0 <= x && x <= x1 && y0 <= y && y <= y1
    }

    /// Whether a straight run between the two points can pass where the head reaches the scaffold.
    pub fn crosses(&self, x0: f64, y0: f64, x1: f64, y1: f64) -> bool {
        let [lx, hx, ly, hy] = self.reach();
        !(x0.max(x1) < lx || x0.min(x1) > hx || y0.max(y1) < ly || y0.min(y1) > hy)
    }
}

/// The letter words of a plate line the rewrite reads, later ones replacing earlier.
fn plate_words(text: &str) -> Vec<(u8, f64)> {
    let code = text.split(';').next().unwrap_or("").as_bytes();
    let mut out: Vec<(u8, f64)> = Vec::new();
    let mut i = 0;
    while i < code.len() {
        let c = code[i];
        if b"XYZEFIJP".contains(&c) {
            let mut j = i + 1;
            if code.get(j) == Some(&b'-') {
                j += 1;
            }
            let digits = code[j..].iter().take_while(|b| b.is_ascii_digit()).count();
            let mut end = j + digits;
            if code.get(end) == Some(&b'.') && code.get(end + 1).is_some_and(|b| b.is_ascii_digit()) {
                end += 1 + code[end + 1..].iter().take_while(|b| b.is_ascii_digit()).count();
            } else if digits == 0 {
                i += 1;
                continue;
            }
            if let Ok(v) = std::str::from_utf8(&code[i + 1..end]).unwrap_or("").parse::<f64>() {
                match out.iter_mut().find(|(k, _)| *k == c) {
                    Some(slot) => slot.1 = v,
                    None => out.push((c, v)),
                }
            }
            i = end;
            continue;
        }
        i += 1;
    }
    out
}

fn word(words: &[(u8, f64)], key: u8) -> Option<f64> {
    words.iter().find(|(k, _)| *k == key).map(|(_, v)| *v)
}

/// A coordinate as the rewrite writes one, with trailing zeros dropped.
fn fmt(v: f64) -> String {
    let text = format!("{v:.3}");
    let text = text.trim_end_matches('0').trim_end_matches('.');
    if text.is_empty() || text == "-0" { "0".into() } else { text.into() }
}

/// What the rewrite kept of the plate, as the stage reports it.
#[derive(Default)]
pub struct PlateStats {
    pub kept_mm: f64,
    pub dropped_mm: f64,
    pub dropped_support_mm: f64,
    pub lifted_travels: i64,
    pub highest_lift_mm: f64,
    pub clipped_layers: i64,
    pub feathered_mm: f64,
    pub least_base_head_clearance_mm: f64,
    pub least_other_head_clearance_mm: f64,
    pub rewritten_travels: i64,
}

impl PlateStats {
    pub fn to_json(&self) -> Value {
        let f = |v: f64| if v.is_finite() { json!((v * 1e3).round() / 1e3) } else { Value::Null };
        json!({
            "kept_mm": f(self.kept_mm), "dropped_mm": f(self.dropped_mm), "dropped_support_mm": f(self.dropped_support_mm),
            "lifted_travels": self.lifted_travels, "highest_lift_mm": f(self.highest_lift_mm),
            "clipped_layers": self.clipped_layers, "feathered_mm": f(self.feathered_mm),
            "least_base_head_clearance_mm": f(self.least_base_head_clearance_mm),
            "least_other_head_clearance_mm": f(self.least_other_head_clearance_mm),
            "rewritten_travels": self.rewritten_travels,
        })
    }
}

/// How a level course of the base that reaches into the stack is cut.
#[derive(Clone, Copy)]
pub enum Clip {
    /// Laid where it has room over the stack, with as much plastic as the room takes, and none
    /// where under the feather's share of the bead is left.
    Feather,
    /// Kept where the course clears the stack by its kept share of height, cut square there.
    Half,
}

/// How a method's stack meets the plate's own courses.
#[derive(Clone, Copy)]
pub struct Rule {
    /// The stack's top over the mounting face, along its normal.
    pub top: f64,
    /// What the plate's own supports stand on over the face, along its normal.
    pub support_floor: f64,
    pub clip: Clip,
    /// The least the nozzle stands over the stack while laying a level course.
    pub nozzle_over: f64,
    /// Where the preamble parks the nozzle; travels above it need no lift.
    pub park_z: f64,
}

/// The plate's own stream, with the base kept above the stack and travels lifted over the scaffold.
struct Plate<'a> {
    frame: Frame,
    clear: &'a Clearance,
    base_id: i64,
    rule: Rule,
    skin: f64,
    clip_until: f64,
    out: Vec<String>,
    real: [f64; 3],
    virtual_: [f64; 3],
    real_retracted: bool,
    virtual_retracted: bool,
    real_feed: Option<f64>,
    virtual_feed: Option<f64>,
    layer_z: Option<f64>,
    layer_h: Option<f64>,
    object: Option<i64>,
    feature: Option<String>,
    stats: PlateStats,
    layer_clipped: bool,
}

impl Plate<'_> {
    fn emit(&mut self, text: impl Into<String>) {
        self.out.push(text.into());
    }

    fn mv(&mut self, x: f64, y: f64, z: f64, feed: Option<f64>, e: Option<f64>) {
        let mut words = Vec::new();
        for (i, (letter, v)) in [("X", x), ("Y", y), ("Z", z)].into_iter().enumerate() {
            if (v - self.real[i]).abs() > 5e-4 {
                words.push(format!("{letter}{}", fmt(v)));
            }
        }
        if words.is_empty() && e.is_none() {
            return;
        }
        let mut text = format!("G1 {}", words.join(" "));
        if let Some(e) = e {
            text.push_str(&format!(" E{e:.5}"));
        }
        if let Some(feed) = feed.filter(|f| Some(*f) != self.real_feed) {
            text.push_str(&format!(" F{feed:.0}"));
            self.real_feed = Some(feed);
        }
        self.emit(text);
        self.real = [x, y, z];
    }

    fn set_retracted(&mut self, want: bool) {
        if want != self.real_retracted {
            self.emit(if want { "G1 E-0.8 F1800" } else { "G1 E0.8 F1800" });
            self.real_feed = Some(1800.0);
        }
        self.real_retracted = want;
    }

    /// Carries the real nozzle to (`x`, `y`, `z`), over whatever the toolhead would otherwise meet.
    fn safe_travel(&mut self, x: f64, y: f64, z: f64) {
        let [x0, y0, z0] = self.real;
        let flat = (x - x0).hypot(y - y0);
        if flat < 1e-4 && (z - z0).abs() < 1e-4 {
            return;
        }
        let floor = if self.clear.crosses(x0, y0, x, y) { self.clear.travel_floor(x0, y0, x, y) } else { f64::NEG_INFINITY };
        if flat <= 1.2 && (z - z0).abs() < 1e-6 && z >= floor {
            self.mv(x, y, z, Some(9000.0), None);
            return;
        }
        self.set_retracted(true);
        let mut high = z0.max(z) + 0.4;
        if floor > high {
            self.stats.lifted_travels += 1;
            self.stats.highest_lift_mm = self.stats.highest_lift_mm.max(floor);
            high = floor;
        }
        self.mv(x0, y0, high, Some(1800.0), None);
        self.mv(x, y, high, Some(60000.0), None);
        self.mv(x, y, z, Some(1800.0), None);
    }

    fn clipping(&self) -> bool {
        self.object == Some(self.base_id) && match (self.layer_z, self.layer_h) {
            (Some(z), Some(h)) => z - KEEP_FRACTION * h < self.clip_until,
            _ => false,
        }
    }

    fn line(&mut self, text: &str) -> Result<()> {
        if text.starts_with(';') {
            let value = |t: &str| t.split(':').nth(1).unwrap_or("").trim().parse::<f64>();
            if text.starts_with("; Z_HEIGHT:") {
                self.layer_z = Some(value(text)?);
                self.layer_clipped = false;
            } else if text.starts_with("; LAYER_HEIGHT:") {
                self.layer_h = Some(value(text)?);
            } else if text.starts_with("; start printing object") {
                self.object = Some(text.rsplit(':').next().unwrap_or("").trim().parse()?);
            } else if text.starts_with("; stop printing object") {
                if self.object == Some(self.base_id) {
                    self.set_retracted(self.virtual_retracted);
                }
                self.object = None;
            } else if let Some(f) = text.strip_prefix("; FEATURE:") {
                self.feature = Some(f.trim().to_string());
            }
            self.emit(text);
            return Ok(());
        }
        let head = text.get(..3).unwrap_or("");
        if !matches!(head, "G1 " | "G0 " | "G2 " | "G3 ") {
            self.emit(text);
            return Ok(());
        }
        let w = plate_words(text);
        let [vx, vy, vz] = self.virtual_;
        let (x, y, z) = (word(&w, b'X'), word(&w, b'Y'), word(&w, b'Z'));
        let (tx, ty, tz) = (x.unwrap_or(vx), y.unwrap_or(vy), z.unwrap_or(vz));
        let e = word(&w, b'E');
        if let Some(f) = word(&w, b'F') {
            self.virtual_feed = Some(f);
        }
        let arc = matches!(head, "G2 " | "G3 ");
        let clip = self.clipping();
        if clip && !self.layer_clipped {
            self.layer_clipped = true;
            self.stats.clipped_layers += 1;
        }
        if x.is_none() && y.is_none() && z.is_none() && !arc {
            if let Some(e) = e.filter(|e| e.abs() > 1e-9) {
                self.virtual_retracted = e < 0.0;
                if clip {
                    return Ok(());
                }
                self.real_retracted = self.virtual_retracted;
            }
            self.real_feed = self.virtual_feed;
            self.emit(text);
            return Ok(());
        }
        self.virtual_ = [tx, ty, tz];
        let laying = (x.is_some() || y.is_some()) && e.is_some_and(|e| e > 0.0);
        if laying && !arc && clip {
            return self.clipped_extrusion([vx, vy, vz], [tx, ty, tz], e.unwrap_or(0.0));
        }
        if e.is_some_and(|e| e < 0.0) {
            self.virtual_retracted = true;
        }
        if clip {
            ensure!(!laying, "an arc lays plastic in a course of the base this stage cuts");
            return Ok(());
        }
        let [rx, ry, rz] = self.real;
        let target = [x.unwrap_or(rx), y.unwrap_or(ry), z.unwrap_or(rz)];
        if laying {
            self.pass_extrusion(text, target)
        } else {
            self.pass_travel(text, &w, arc, target, e)
        }
    }

    fn pass_extrusion(&mut self, text: &str, target: [f64; 3]) -> Result<()> {
        self.real = target;
        ensure!(dist3(self.real, self.virtual_) <= 2e-3,
            "the nozzle is not where the plate's course expects it: {:?} against {:?}", self.real, self.virtual_);
        self.real_retracted = false;
        self.real_feed = self.virtual_feed;
        if self.clear.near(target[0], target[1]) && target[2] < self.rule.park_z {
            let gap = target[2] - self.clear.head_floor(target[0], target[1]);
            let least = if self.object == Some(self.base_id) {
                &mut self.stats.least_base_head_clearance_mm
            } else {
                &mut self.stats.least_other_head_clearance_mm
            };
            *least = least.min(gap);
        }
        self.emit(text);
        Ok(())
    }

    fn pass_travel(&mut self, text: &str, w: &[(u8, f64)], arc: bool, target: [f64; 3], e: Option<f64>) -> Result<()> {
        let [rx, ry, rz] = self.real;
        let [tx, ty, tz] = target;
        let passed = |p: &mut Self| {
            p.emit(text);
            p.real = target;
            p.real_feed = p.virtual_feed;
            if e.is_some_and(|e| e < 0.0) {
                p.real_retracted = true;
            }
        };
        if rz.min(tz) >= self.rule.park_z || !self.clear.crosses(rx, ry, tx, ty) {
            passed(self);
            return Ok(());
        }
        let resume = |p: &mut Self| {
            if let Some(f) = p.virtual_feed.filter(|f| p.real_feed != Some(*f)) {
                p.emit(format!("G1 F{f:.0}"));
                p.real_feed = Some(f);
            }
        };
        if arc && word(w, b'X').is_none() && word(w, b'Y').is_none() {
            self.mv(rx, ry, tz.max(rz), Some(1800.0), None);
            resume(self);
            return Ok(());
        }
        let floor = self.clear.travel_floor(rx, ry, tx, ty);
        if rz.min(tz) >= floor {
            passed(self);
            return Ok(());
        }
        ensure!(!arc, "an arc travels low beside the scaffold");
        let end_floor = self.clear.travel_floor(tx, ty, tx, ty);
        ensure!(tz >= end_floor, "a travel ends {:.2} mm low at X{tx:.2} Y{ty:.2} Z{tz:.2} (object {:?})", end_floor - tz, self.object);
        self.stats.rewritten_travels += 1;
        self.stats.lifted_travels += 1;
        self.stats.highest_lift_mm = self.stats.highest_lift_mm.max(floor);
        if let Some(e) = e.filter(|e| *e < 0.0) {
            self.emit(format!("G1 E{e:.5} F1800"));
            self.real_retracted = true;
        }
        let high = rz.max(tz).max(floor);
        self.mv(rx, ry, high, Some(1800.0), None);
        self.mv(tx, ty, high, Some(word(w, b'F').unwrap_or(60000.0)), None);
        self.mv(tx, ty, tz, Some(1800.0), None);
        resume(self);
        Ok(())
    }

    /// A level course of the base where it crosses the stack, cut by the rule's clip. A support
    /// line under what the plate's supports stand on is dropped whole.
    fn clipped_extrusion(&mut self, a: [f64; 3], b: [f64; 3], e: f64) -> Result<()> {
        let ([x0, y0, z0], [x1, y1, z1]) = (a, b);
        let length = (x1 - x0).hypot(y1 - y0);
        let f = self.frame;
        let (layer_z, layer_h) = (self.layer_z.context("a clipped road before its course")?, self.layer_h.context("a clipped road before its height")?);
        let mut parts: Vec<(f64, f64, f64)> = Vec::new();
        if self.feature.as_deref().is_some_and(|f| f.starts_with("Support")) {
            if z1 - layer_h < f.face((y0 + y1) / 2.0) + self.rule.support_floor / f.c - 0.05 {
                self.stats.dropped_support_mm += length;
                return Ok(());
            }
            parts.push((0.0, 1.0, 1.0));
        } else if let Clip::Half = self.rule.clip {
            // keep the part of the bead over the stack: y at or beyond the cut for this course; a
            // seam's ramp climbs inside its course, so the course's own height sets the cut
            let cut = f.cy + (f.cz + self.skin - (layer_z - KEEP_FRACTION * layer_h)) / f.t;
            let (a, b) = (y0 - cut, y1 - cut);
            if a < 0.0 && b < 0.0 {
                self.stats.dropped_mm += length;
                return Ok(());
            }
            let (mut t0, mut t1) = (0.0_f64, 1.0_f64);
            if a < 0.0 {
                t0 = a / (a - b);
            }
            if b < 0.0 {
                t1 = a / (a - b);
            }
            // and only where the nozzle itself stands over the stack
            let g0 = z0 - (f.face(y0) + self.skin) - self.rule.nozzle_over;
            let g1 = z1 - (f.face(y1) + self.skin) - self.rule.nozzle_over;
            if g0 < 0.0 && g1 < 0.0 {
                self.stats.dropped_mm += length;
                return Ok(());
            }
            if g0 < 0.0 {
                t0 = t0.max(g0 / (g0 - g1));
            }
            if g1 < 0.0 {
                t1 = t1.min(g0 / (g0 - g1));
            }
            if (t1 - t0) * length < 0.05 {
                self.stats.dropped_mm += length;
                return Ok(());
            }
            self.stats.dropped_mm += (1.0 - (t1 - t0)) * length;
            parts.push((t0, t1, 1.0));
        } else {
            let under = layer_z - layer_h;
            let room0 = z0 - (f.face(y0) + self.skin);
            let room1 = z1 - (f.face(y1) + self.skin);
            let (bead0, bead1) = ((z0 - under).max(1e-6), (z1 - under).max(1e-6));
            let (mut lo, mut hi) = (0.0_f64, 1.0_f64);
            let over = self.rule.nozzle_over;
            for (g0, g1) in [(room0 - FEATHER_MIN * bead0, room1 - FEATHER_MIN * bead1), (room0 - over, room1 - over)] {
                if g0 < 0.0 && g1 < 0.0 {
                    self.stats.dropped_mm += length;
                    return Ok(());
                }
                if g0 < 0.0 {
                    lo = lo.max(g0 / (g0 - g1));
                }
                if g1 < 0.0 {
                    hi = hi.min(g0 / (g0 - g1));
                }
            }
            if (hi - lo) * length < 0.05 {
                self.stats.dropped_mm += length;
                return Ok(());
            }
            self.stats.dropped_mm += (1.0 - (hi - lo)) * length;
            let (full0, full1) = (room0 - bead0, room1 - bead1);
            let whole = if full0 >= 0.0 && full1 >= 0.0 {
                Some((lo, hi))
            } else if full0 < 0.0 && full1 < 0.0 {
                None
            } else {
                let at = full0 / (full0 - full1);
                let w = if full0 < 0.0 { (lo.max(at), hi) } else { (lo, hi.min(at)) };
                (w.1 - w.0 > 1e-9).then_some(w)
            };
            let thin = |ta: f64, tb: f64, parts: &mut Vec<(f64, f64, f64)>, stats: &mut PlateStats| {
                let steps = (((tb - ta) * length / 0.25).ceil() as usize).max(1);
                for i in 0..steps {
                    let u0 = ta + (tb - ta) * i as f64 / steps as f64;
                    let u1 = ta + (tb - ta) * (i + 1) as f64 / steps as f64;
                    let um = (u0 + u1) / 2.0;
                    let share = (room0 + (room1 - room0) * um) / (bead0 + (bead1 - bead0) * um);
                    parts.push((u0, u1, share.clamp(0.0, 1.0)));
                }
                stats.feathered_mm += (tb - ta) * length;
            };
            match whole {
                None => thin(lo, hi, &mut parts, &mut self.stats),
                Some(w) => {
                    if w.0 - lo > 1e-9 {
                        thin(lo, w.0, &mut parts, &mut self.stats);
                    }
                    parts.push((w.0, w.1, 1.0));
                    if hi - w.1 > 1e-9 {
                        thin(w.1, hi, &mut parts, &mut self.stats);
                    }
                }
            }
        }
        for (u0, u1, share) in parts {
            let (sx, sy, sz) = (x0 + (x1 - x0) * u0, y0 + (y1 - y0) * u0, z0 + (z1 - z0) * u0);
            let (ex, ey, ez) = (x0 + (x1 - x0) * u1, y0 + (y1 - y0) * u1, z0 + (z1 - z0) * u1);
            if (sx - self.real[0]).hypot(sy - self.real[1]) > 1e-3 || (sz - self.real[2]).abs() > 1e-4 {
                self.safe_travel(sx, sy, sz);
            }
            self.set_retracted(false);
            let gap = ez - self.clear.head_floor(ex, ey);
            self.stats.least_base_head_clearance_mm = self.stats.least_base_head_clearance_mm.min(gap);
            self.stats.kept_mm += (u1 - u0) * length;
            self.mv(ex, ey, ez, self.virtual_feed, Some(e * (u1 - u0) * share));
        }
        Ok(())
    }
}

/// The plate's lines with the preamble before its first layer's first object and the base kept
/// above the stack by `rule`; `parked` is where the preamble leaves the nozzle.
pub fn rewrite(lines: &[&str], frame: &Frame, clearance: &Clearance, base_id: i64, rule: Rule,
               preamble: &[String], parked: [f64; 3]) -> Result<(Vec<String>, PlateStats)> {
    let first_layer = lines.iter().position(|l| l.starts_with("; CHANGE_LAYER")).context("the plate has no layers")?;
    let insert = (first_layer..lines.len()).find(|&i| lines[i].starts_with("; OBJECT_ID:")).context("the plate has no object")?;
    let end = lines.iter().position(|l| l.starts_with("; MACHINE_END_GCODE_START")).context("the plate has no end G-code")?;
    let skin = rule.top / frame.c;
    let mut plate = Plate {
        frame: *frame, clear: clearance, base_id, rule, skin,
        clip_until: frame.cz + (frame.rim[1] + LIP) * frame.s + skin + 0.6,
        out: Vec::with_capacity(lines.len() + preamble.len()),
        real: parked, virtual_: [0.0; 3], real_retracted: true, virtual_retracted: true, real_feed: None,
        virtual_feed: None, layer_z: None, layer_h: None, object: None, feature: None,
        stats: PlateStats {
            least_base_head_clearance_mm: f64::INFINITY, least_other_head_clearance_mm: f64::INFINITY,
            ..Default::default()
        },
        layer_clipped: false,
    };
    for l in &lines[first_layer..insert] {
        let value = || l.split(':').nth(1).unwrap_or("").trim().parse::<f64>();
        if l.starts_with("; Z_HEIGHT:") {
            plate.layer_z = Some(value()?);
        } else if l.starts_with("; LAYER_HEIGHT:") {
            plate.layer_h = Some(value()?);
        }
    }
    let mut pos: [Option<f64>; 3] = [None; 3];
    for l in lines[..insert].iter().filter(|l| l.starts_with("G1 ") || l.starts_with("G0 ")) {
        let w = plate_words(l);
        for (k, letter) in b"XYZ".iter().enumerate() {
            if let Some(v) = word(&w, *letter) {
                pos[k] = Some(v);
            }
        }
    }
    let [Some(x), Some(y), Some(z)] = pos else { anyhow::bail!("the start sequence leaves the nozzle somewhere unknown") };
    plate.virtual_ = [x, y, z];
    plate.out.extend(lines[..insert].iter().map(|l| l.to_string()));
    plate.out.extend(preamble.iter().cloned());
    for l in &lines[insert..end] {
        plate.line(l)?;
    }
    plate.out.extend(lines[end..].iter().map(|l| l.to_string()));
    Ok((plate.out, plate.stats))
}

/// The inputs of the foundation stage.
pub struct Foundation<'a> {
    pub archive: &'a Path,
    pub report: &'a Path,
    pub stl: &'a Path,
    pub headmap: &'a Path,
    pub out_dir: &'a Path,
    pub deck_top: Option<f64>,
}

/// The base's seat, its object id on the plate and the label its object start carries.
pub fn plate_inputs(report: &Value, lines: &[&str]) -> Result<(Frame, [f64; 3], i64, String)> {
    let rims = &report["base_rim_supports"];
    let seat: [f64; 3] = serde_json::from_value(rims["seat_print_world_center_mm"].clone()).context("the seat")?;
    let normal: [f64; 3] = serde_json::from_value(rims["seat_print_world_outward_normal"].clone()).context("the seat normal")?;
    let frame = Frame::new(seat, SCULPTED_RIM);
    ensure!(normal[0].abs() < 1e-9 && (normal[1] + frame.s).abs() < 1e-6 && (normal[2] + frame.c).abs() < 1e-6,
        "the seat is not turned 15 degrees about X");
    let base_id = report["parts"].as_array().context("the parts")?.iter()
        .find(|p| p["name"] == "faucet-shell-base").and_then(|p| p["identify_id"].as_i64()).context("the base's id")?;
    let start = lines.iter().position(|l| l.starts_with(&format!("; start printing object, unique label id: {base_id}")))
        .context("the plate never starts the base")?;
    let label = lines.get(start + 1).context("the base's label")?.to_string();
    ensure!(label.starts_with("M624 "), "{label}");
    Ok((frame, seat, base_id, label))
}

/// The whole stage: the preamble, the plate rewritten around it, and in `out_dir` the plate's
/// G-code with the stage's record beside it.
pub fn foundation(args: &Foundation) -> Result<()> {
    let report: Value = serde_json::from_slice(&std::fs::read(args.report)?)?;
    let source = std::fs::read(args.archive)?;
    let gcode = String::from_utf8(crate::gcode::plate_gcode(args.archive)?)?;
    let lines: Vec<&str> = gcode.split('\n').collect();
    let (frame, seat, base_id, label) = plate_inputs(&report, &lines)?;
    let foot = Foot::cut(args.stl)?;
    let mut w = Writer::new();
    let opening = Opening {
        title: "; ===== sloped underside of faucet-shell-base: scaffold, roof and foot =====".into(),
        object: vec![label], temperature: "280".into(), level_roof: true,
    };
    let stack = scaffold_and_roof(&mut w, &frame, &opening)?;
    let laid = lay_foot(&mut w, &frame, &foot, args.deck_top)?;
    let rule = Rule { top: laid.slab_top, support_floor: laid.slab_top, clip: Clip::Feather, nozzle_over: 0.06, park_z: 26.0 };
    w.park(rule.park_z, "265", &[])?;
    let clearance = Clearance::new(args.headmap, &frame, &|_| laid.slab_top)?;
    let parked = w.pos.context("the preamble laid nothing")?;
    let (out, stats) = rewrite(&lines, &frame, &clearance, base_id, rule, &w.out, parked)?;
    let text = out.join("\n");
    std::fs::create_dir_all(args.out_dir)?;
    std::fs::write(args.out_dir.join("plate_1.gcode"), &text)?;
    let round = |v: f64, places: i32| (v * 10f64.powi(places)).round() / 10f64.powi(places);
    let record = json!({
        "purpose": "Binds the Sculpted base's sloped foot to the courses this stage laid and what it kept of the plate.",
        "input_archive": {"path": args.archive.display().to_string(), "sha256": crate::sha256_hex(&source)},
        "gcode_sha256": crate::sha256_hex(text.as_bytes()),
        "seat_center_mm": seat,
        "tilt_x_degrees": -15,
        "stack_normal_mm": {
            "course": COURSE, "air_asked": AIR, "roof_courses": ROOF_COURSES, "scaffold_ceiling": stack.n_scaffold,
            "roof_tops": stack.n_roof, "slab_top": laid.slab_top, "shoulder_course": laid.shoulder_course,
            "plug_top": laid.plug_top, "deck_top": laid.deck_top,
        },
        "roof_lip_mm": LIP,
        "laid": {
            "ring_pieces": laid.ring_pieces, "narrow_rings": laid.narrow_rings, "fill_lines": laid.fill_lines,
            "scaffold_layers": stack.scaffold_layers, "scaffold_top_mm": stack.scaffold_top, "sloped_courses": laid.sloped_courses,
        },
        "preamble": {
            "seconds": round(w.time, 1), "filament_mm": round(w.filament, 2),
            "extrusion_mm_by_feature": w.lengths.iter().map(|(k, v)| (k.clone(), json!(round(*v, 1)))).collect::<serde_json::Map<_, _>>(),
        },
        "plate": stats.to_json(),
        "limits": {
            "z_while_printing_mm_s": Z_PRINT_RATE, "z_while_travelling_mm_s": Z_TRAVEL_RATE,
            "head_travel_margin_mm": HEAD_TRAVEL_MARGIN, "nozzle_travel_margin_mm": NOZZLE_TRAVEL_MARGIN,
            "least_share_of_a_level_course_laid": FEATHER_MIN, "nozzle_over_slab_mm": rule.nozzle_over,
        },
    });
    std::fs::write(args.out_dir.join("sloped-underside.json"), serde_json::to_vec_pretty(&record)?)?;
    Ok(())
}

/// A production plate's sloped underside: the scaffold, the roof, the bore's deck and the skin
/// ahead of the plate `raw` the slicer wrote from the filled base, and the plate with the base
/// kept above the skin. `report` is the plate's preparation record; `stl` is the real base.
/// Returns the plate's G-code and the stage's record.
pub fn skin_underside(raw: &[u8], report: &Value, stl: &Path, headmap: &Path) -> Result<(String, Value)> {
    let base = &report["base_underside"];
    let seat: [f64; 3] = serde_json::from_value(base["seat_print_world_center_mm"].clone()).context("the seat")?;
    let normal: [f64; 3] = serde_json::from_value(base["seat_print_world_outward_normal"].clone()).context("the seat normal")?;
    let rim: [f64; 2] = serde_json::from_value(base["rim_semi_axes_mm"].clone()).context("the rim")?;
    let base_id = base["identify_id"].as_i64().context("the base's id")?;
    let temperature = |key: &str| base[key][0].as_str().map(str::to_string).with_context(|| format!("the base's {key}"));
    let frame = Frame::new(seat, rim);
    ensure!(normal[0].abs() < 1e-9 && (normal[1] + frame.s).abs() < 1e-6 && (normal[2] + frame.c).abs() < 1e-6,
        "the seat is not turned 15 degrees about X");
    let skin = Skin::cut(stl)?;
    let text = std::str::from_utf8(raw)?;
    let lines: Vec<&str> = text.split('\n').collect();
    let start = format!("; start printing object, unique label id: {base_id}");
    let label = lines.iter().position(|l| l.starts_with(&start)).and_then(|i| lines.get(i + 1)).context("the plate never starts the base")?;
    ensure!(label.starts_with("M624 "), "{label}");
    let mut w = Writer::new();
    let opening = Opening {
        title: "; ===== sloped underside: scaffold, roof and skin =====".into(),
        object: vec![start, label.to_string()], temperature: temperature("nozzle_temperature")?, level_roof: false,
    };
    let stack = scaffold_and_roof(&mut w, &frame, &opening)?;
    let halves = lay_skin(&mut w, &frame, &skin);
    let n_skin: Vec<f64> = (1..=SKIN_COURSES).map(|i| COURSE * i as f64).collect();
    let rule = Rule { top: n_skin[SKIN_COURSES - 1], support_floor: 0.0, clip: Clip::Half, nozzle_over: 0.05, park_z: 22.0 };
    w.park(rule.park_z, &temperature("nozzle_temperature_initial_layer")?, &[format!("; stop printing object, unique label id: {base_id}")])?;
    // the skin over the face, the deck in the bore, the roof elsewhere under the lip
    let face = skin.region.offset(0.3);
    let top = |p: Point| if face.contains(p) { rule.top } else if skin.bore.contains(p) { 0.0 } else { stack.n_roof[ROOF_COURSES - 1] };
    let clearance = Clearance::new(headmap, &frame, &top)?;
    let parked = w.pos.context("the preamble laid nothing")?;
    let (out, stats) = rewrite(&lines, &frame, &clearance, base_id, rule, &w.out, parked)?;
    let gcode = out.join("\n");
    let round = |v: f64, places: i32| (v * 10f64.powi(places)).round() / 10f64.powi(places);
    let record = json!({
        "purpose": "Binds the base's sloped courses and the retained native paths to the resulting plate.",
        "gcode_input_sha256": crate::sha256_hex(raw),
        "gcode_sha256": crate::sha256_hex(gcode.as_bytes()),
        "seat_center_mm": seat,
        "tilt_x_degrees": -15,
        "stack_normal_mm": {
            "course": COURSE, "air_asked": AIR, "roof_courses": ROOF_COURSES, "skin_courses": SKIN_COURSES,
            "scaffold_ceiling": stack.n_scaffold, "roof_tops": stack.n_roof, "skin_tops": n_skin, "deck_top": 0.0,
        },
        "roof_lip_mm": LIP,
        "laid": {"scaffold_layers": stack.scaffold_layers, "scaffold_top_mm": stack.scaffold_top, "skin_ring_halves": halves},
        "preamble": {
            "seconds": round(w.time, 1), "filament_mm": round(w.filament, 2),
            "extrusion_mm_by_feature": w.lengths.iter().map(|(k, v)| (k.clone(), json!(round(*v, 1)))).collect::<serde_json::Map<_, _>>(),
        },
        "plate": stats.to_json(),
        "limits": {
            "z_while_printing_mm_s": Z_PRINT_RATE, "z_while_travelling_mm_s": Z_TRAVEL_RATE,
            "head_travel_margin_mm": HEAD_TRAVEL_MARGIN, "nozzle_travel_margin_mm": NOZZLE_TRAVEL_MARGIN,
            "kept_fraction_of_course_height": KEEP_FRACTION,
        },
    });
    Ok((gcode, record))
}
