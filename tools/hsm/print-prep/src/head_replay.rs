//! The head replay plays a sliced plate's moves against the material laid before each one, with
//! the modeled toolhead over them. For each phase of the plate it reads the head body's and the
//! nozzle flank's least clearance over the beads already laid, the tip's travels below them, and
//! the phase's moves, feed time and extrusion. Inside the nozzle windows a finer model reads the
//! nozzle's flat and cone over the nominal beads nearby, while it lays and while it travels dry.
//! Each object's first extrusion, idle spans and bead bounds come with it.
//!
//! The beads are nominal sections stamped on rasters and the head is the full head map's raster,
//! so its readings are of the plate's paths and the model, not of the print. Its times are
//! feed-time estimates.

use crate::head_map::HeadMap;
use anyhow::{bail, ensure, Context, Result};
use std::collections::{BTreeMap, HashMap};
use std::fmt::Write as _;
use std::io::{BufRead, BufReader};
use std::path::Path;
use std::rc::Rc;

/// The nozzle windows on the plate, as least X and Y and most X and Y: the base, the tip, the
/// mounting plate's screw-seat rings and the display cover.
pub const WINDOWS: [[f64; 4]; 4] = [
    [45.0, 73.0, 125.0, 213.0],
    [137.0, 166.0, 229.0, 250.0],
    [180.0, 82.0, 232.0, 110.0],
    [234.0, 202.0, 268.0, 266.0],
];
/// The terrain raster's pitch, which the head map's grid matches.
const PITCH: f64 = 0.5;
/// The longest step a straight move and an arc are sampled in away from the nozzle windows.
const MOTION_SAMPLE: f64 = 0.5;
const ARC_SAMPLE: f64 = 0.25;
/// The cells a side of the terrain's tiles, whose highest bead bounds the head's search.
const TILE: i32 = 8;
/// The axis feed limits, in millimetres a second, before the plate sets its own.
const START_LIMITS: [f64; 4] = [1000.0, 1000.0, 30.0, 50.0];
/// A travel sample this far below a laid bead's top is an anomaly; the report keeps this many.
const TRAVEL_TOLERANCE: f64 = 0.31;
const ANOMALIES: usize = 120;
/// The shared bed's extent.
const BED: [f64; 3] = [325.0, 320.0, 325.0];
/// The nozzle tip in the windows' model: its flat's radius, and its cone's radius and rise.
const TIP_FLAT_R: f64 = 0.34;
const TIP_CONE_R: f64 = 2.0;
const TIP_CONE_HEIGHT: f64 = 2.48;
/// Within this of the tip's axis the windows' model reads the bead under the nozzle's centre.
const TIP_CENTER_R: f64 = 0.20;
/// The nozzle flank's map cells this far from the tip's axis are read; nearer ones are the tip's.
const FLANK_FROM: f64 = 0.6;
/// The nozzle windows' raster pitch, which their moves are sampled at.
const NEARBY_PITCH: f64 = 0.10;
/// A raster point no bead has reached.
const UNFILLED: f32 = -1000.0;
/// The slicer's nominal bead section is read back with its flow ratio and a bridge's extra flow.
const FLOW: f64 = 0.9555;
const BRIDGE_FLOW: f64 = 1.25;
const FILAMENT_DIAMETER: f64 = 1.75;

fn removable_feature(feature: &str) -> bool {
    feature.starts_with("Support") || feature == "Brim" || feature == "Skirt"
}

fn trim(text: &str) -> &str {
    text.trim_matches([' ', '\t', '\r'])
}

/// `x`, or zero where `x` is not above it.
fn at_least_zero(x: f64) -> f64 {
    if 0.0 < x { x } else { 0.0 }
}

/// The number at the start of `text`, as `strtod` reads one: white space, a sign, digits with
/// an optional point and exponent; nothing it can read is zero.
fn strtod(text: &[u8]) -> f64 {
    let mut at = text.iter().take_while(|c| c.is_ascii_whitespace()).count();
    let start = at;
    if matches!(text.get(at), Some(b'+' | b'-')) {
        at += 1;
    }
    let digits = |from: usize| text[from.min(text.len())..].iter().take_while(|c| c.is_ascii_digit()).count();
    let whole = digits(at);
    at += whole;
    let mut fraction = 0;
    if text.get(at) == Some(&b'.') {
        fraction = digits(at + 1);
        if whole + fraction > 0 {
            at += 1 + fraction;
        }
    }
    if whole + fraction == 0 {
        return 0.0;
    }
    if matches!(text.get(at), Some(b'e' | b'E')) {
        let sign = usize::from(matches!(text.get(at + 1), Some(b'+' | b'-')));
        let exponent = digits(at + 1 + sign);
        if exponent > 0 {
            at += 1 + sign + exponent;
        }
    }
    std::str::from_utf8(&text[start..at]).ok().and_then(|s| s.parse().ok()).unwrap_or(0.0)
}

/// A command's letter words: each upper-case letter followed directly by a number.
struct Words {
    values: [f64; 26],
    seen: [bool; 26],
}

impl Words {
    fn new(text: &str) -> Words {
        let (mut values, mut seen) = ([0.0; 26], [false; 26]);
        let bytes = text.as_bytes();
        let mut p = 0;
        while p < bytes.len() {
            let key = bytes[p];
            p += 1;
            if !key.is_ascii_uppercase() {
                continue;
            }
            let start = p;
            while p < bytes.len() && matches!(bytes[p], b'-' | b'+' | b'.' | b'0'..=b'9') {
                p += 1;
            }
            if p != start {
                let k = usize::from(key - b'A');
                seen[k] = true;
                values[k] = strtod(&bytes[start..]);
            }
        }
        Words { values, seen }
    }

    fn has(&self, key: u8) -> bool {
        self.seen[usize::from(key - b'A')]
    }

    fn get(&self, key: u8) -> f64 {
        self.or(key, 0.0)
    }

    fn or(&self, key: u8, fallback: f64) -> f64 {
        if self.has(key) { self.values[usize::from(key - b'A')] } else { fallback }
    }
}

/// The highest bead laid over a terrain cell, by which object, and whether it is support.
#[derive(Clone, Copy)]
struct Cell {
    height: f32,
    object: i32,
    removable: bool,
}

const EMPTY: Cell = Cell { height: 0.0, object: 0, removable: false };

/// The laid beads' tops over the whole plate and around it, where the head reaches.
struct Terrain {
    cells: Vec<Cell>,
    highest: Vec<f32>,
    source: Vec<i32>,
}

impl Terrain {
    const X0: i32 = -208;
    const Y0: i32 = -208;
    const WIDTH: i32 = 1280;
    const HEIGHT: i32 = 1280;
    const TILES_X: i32 = Self::WIDTH / TILE;
    const TILES_Y: i32 = Self::HEIGHT / TILE;

    fn new() -> Terrain {
        let tiles = (Self::TILES_X * Self::TILES_Y) as usize;
        Terrain { cells: vec![EMPTY; (Self::WIDTH * Self::HEIGHT) as usize], highest: vec![0.0; tiles], source: vec![0; tiles] }
    }

    fn index_x(mm: f64) -> i32 {
        (mm / PITCH).round() as i32 - Self::X0
    }

    fn index_y(mm: f64) -> i32 {
        (mm / PITCH).round() as i32 - Self::Y0
    }

    fn x_at(i: i32) -> f64 {
        f64::from(i + Self::X0) * PITCH
    }

    fn y_at(j: i32) -> f64 {
        f64::from(j + Self::Y0) * PITCH
    }

    fn get(&self, i: i32, j: i32) -> &Cell {
        if i < 0 || j < 0 || i >= Self::WIDTH || j >= Self::HEIGHT {
            return &EMPTY;
        }
        &self.cells[(j * Self::WIDTH + i) as usize]
    }

    fn tile_max(&self, i: i32, j: i32) -> f64 {
        if i < 0 || j < 0 || i >= Self::TILES_X || j >= Self::TILES_Y {
            return 0.0;
        }
        f64::from(self.highest[(j * Self::TILES_X + i) as usize])
    }

    fn tile_may_have_other_object(&self, i: i32, j: i32, object: i32) -> bool {
        if i < 0 || j < 0 || i >= Self::TILES_X || j >= Self::TILES_Y {
            return false;
        }
        let producer = self.source[(j * Self::TILES_X + i) as usize];
        producer != 0 && producer != object
    }

    fn add(&mut self, i: i32, j: i32, z: f32, object: i32, removable: bool) {
        if i < 0 || j < 0 || i >= Self::WIDTH || j >= Self::HEIGHT {
            return;
        }
        let cell = &mut self.cells[(j * Self::WIDTH + i) as usize];
        if z < cell.height - 1.0e-5 {
            return;
        }
        *cell = Cell { height: z, object, removable };
        let index = ((j / TILE) * Self::TILES_X + i / TILE) as usize;
        if self.highest[index] < z {
            self.highest[index] = z;
        }
        let producer = &mut self.source[index];
        if *producer == 0 {
            *producer = object;
        } else if object != 0 && *producer != object {
            *producer = -1;
        }
    }
}

/// A head map cell, as terrain cells from the tip, and the head's height over it.
#[derive(Clone, Copy)]
struct HeadCell {
    x: i32,
    y: i32,
    height: f64,
}

/// The head cells over one terrain tile, for one position of the tip within its tile.
struct Block {
    dx: i32,
    dy: i32,
    underside: f64,
    cells: Vec<HeadCell>,
}

/// The head's body by the tip's position within a tile, its lowest blocks first, and the nozzle's flank.
struct Head {
    body: Vec<Vec<Block>>,
    flank: Vec<HeadCell>,
}

impl Head {
    fn new(map: &HeadMap) -> Result<Head> {
        ensure!(map.step == PITCH, "the head map's grid is not the replay's terrain grid");
        let (left, bottom) = ((map.x0 / map.step).round_ties_even() as i32, (map.y0 / map.step).round_ties_even() as i32);
        let cells = |grid: &[f64]| -> Vec<HeadCell> {
            (0..map.rows).flat_map(|row| (0..map.cols).map(move |col| (row, col)))
                .filter(|&(row, col)| grid[row * map.cols + col].is_finite())
                .map(|(row, col)| HeadCell { x: left + col as i32, y: bottom + row as i32, height: grid[row * map.cols + col] })
                .collect()
        };
        let mut body: Vec<Vec<Block>> = (0..TILE * TILE).map(|_| Vec::new()).collect();
        let mut seen: Vec<HashMap<(i32, i32), usize>> = (0..TILE * TILE).map(|_| HashMap::new()).collect();
        for cell in cells(&map.head) {
            for ry in 0..TILE {
                for rx in 0..TILE {
                    let r = (ry * TILE + rx) as usize;
                    let key = ((cell.x + rx).div_euclid(TILE), (cell.y + ry).div_euclid(TILE));
                    match seen[r].get(&key) {
                        Some(&b) => {
                            let block = &mut body[r][b];
                            block.underside = block.underside.min(cell.height);
                            block.cells.push(cell);
                        }
                        None => {
                            seen[r].insert(key, body[r].len());
                            body[r].push(Block { dx: key.0, dy: key.1, underside: cell.height, cells: vec![cell] });
                        }
                    }
                }
            }
        }
        // Low hardware offers a smaller bound and is visited first.
        for blocks in &mut body {
            blocks.sort_by(|a, b| a.underside.partial_cmp(&b.underside).unwrap_or(std::cmp::Ordering::Equal));
        }
        let flank = cells(&map.nozzle)
            .into_iter()
            .filter(|c| (f64::from(c.x) * PITCH).hypot(f64::from(c.y) * PITCH) >= FLANK_FROM)
            .collect();
        Ok(Head { body, flank })
    }
}

/// A least clearance and where it was read: the tip, the time, the line, the moving object, the
/// object whose bead it was over, and the head cell over that bead.
#[derive(Clone, Copy)]
struct Clearance {
    gap: f64,
    xyz: [f64; 3],
    time: f64,
    line: usize,
    object: i32,
    obstacle: i32,
    offset_x: i32,
    offset_y: i32,
    earlier_bead_removable: bool,
}

impl Default for Clearance {
    fn default() -> Clearance {
        Clearance { gap: f64::INFINITY, xyz: [0.0; 3], time: 0.0, line: 0, object: 0, obstacle: 0, offset_x: 0, offset_y: 0, earlier_bead_removable: false }
    }
}

/// A least clearance of the nozzle windows' model and the bead it was over.
#[derive(Clone)]
struct LocalClearance {
    gap: f64,
    nozzle: [f64; 3],
    bead: [f64; 3],
    age: f64,
    radius: f64,
    line: usize,
    source_line: usize,
    object: i32,
    deposited_by: i32,
    feature: Rc<str>,
    earlier_bead_removable: bool,
}

impl Default for LocalClearance {
    fn default() -> LocalClearance {
        LocalClearance { gap: f64::INFINITY, nozzle: [0.0; 3], bead: [0.0; 3], age: 0.0, radius: 0.0, line: 0, source_line: 0, object: 0,
                         deposited_by: 0, feature: Rc::from(""), earlier_bead_removable: false }
    }
}

/// The nozzle windows' readings, in the order the report writes them.
const READINGS: [&str; 14] = [
    "fresh_same_run_flat",
    "prior_road_flat_during_extrusion",
    "prior_road_cone_during_extrusion",
    "prior_support_flat_during_extrusion",
    "prior_support_cone_during_extrusion",
    "prior_part_flat_during_extrusion",
    "prior_part_cone_during_extrusion",
    "dry_travel_flat",
    "dry_travel_cone",
    "dry_travel_flat_against_support",
    "dry_travel_cone_against_support",
    "dry_travel_flat_against_part",
    "dry_travel_cone_against_part",
    "dry_travel_occupied_nominal_center",
];
const FRESH_FLAT: usize = 0;
const ADJACENT: [usize; 2] = [1, 2];
const EARLIER_SUPPORT: [usize; 2] = [3, 4];
const EARLIER_PART: [usize; 2] = [5, 6];
const TRAVEL: [usize; 2] = [7, 8];
const DRY_SUPPORT: [usize; 2] = [9, 10];
const DRY_PART: [usize; 2] = [11, 12];
const DRY_CENTER: usize = 13;

/// One phase's readings in the nozzle windows.
#[derive(Default)]
struct NozzleClearance {
    readings: [LocalClearance; 14],
    total_road_mm: f64,
    downslope_road_mm: f64,
    fresh_flat_past_005_road_mm: f64,
    sampled_fresh_flat_past_005_road_mm: f64,
    adjacent_past_01_road_mm: f64,
    adjacent_past_02_road_mm: f64,
    outer_wall_mm: f64,
    outer_wall_fresh_past_005_road_mm: f64,
    outer_wall_sampled_fresh_past_005_road_mm: f64,
    outer_wall_adjacent_past_01_road_mm: f64,
    sampled: usize,
    travel_sampled: usize,
}

/// The least gaps one tip position reads to the road it lays and to the beads laid before it.
struct LocalSample {
    fresh_flat: f64,
    adjacent: f64,
}

/// The top of the nominal bead over one point of a nozzle window.
#[derive(Clone, Copy)]
struct LocalPoint {
    height: f32,
    time: f32,
    run: i32,
    object: i32,
    line: usize,
    removable: bool,
}

/// A nozzle window: its nominal beads' tops on a fine raster.
struct LocalTerrain {
    x0: f64,
    y0: f64,
    x1: f64,
    y1: f64,
    nx: i32,
    ny: i32,
    points: Vec<LocalPoint>,
}

impl LocalTerrain {
    fn new([x0, y0, x1, y1]: [f64; 4]) -> LocalTerrain {
        let nx = 1 + ((x1 - x0) / NEARBY_PITCH).round() as i32;
        let ny = 1 + ((y1 - y0) / NEARBY_PITCH).round() as i32;
        let empty = LocalPoint { height: 0.0, time: UNFILLED, run: 0, object: 0, line: 0, removable: false };
        LocalTerrain { x0, y0, x1, y1, nx, ny, points: vec![empty; (nx * ny) as usize] }
    }

    fn x(&self, i: i32) -> f64 {
        self.x0 + f64::from(i) * NEARBY_PITCH
    }

    fn y(&self, j: i32) -> f64 {
        self.y0 + f64::from(j) * NEARBY_PITCH
    }

    fn nearby(&self, p: [f64; 3]) -> bool {
        p[0] > self.x0 - TIP_CONE_R && p[0] < self.x1 + TIP_CONE_R && p[1] > self.y0 - TIP_CONE_R && p[1] < self.y1 + TIP_CONE_R
    }

    fn possibly_crosses(&self, first: [f64; 3], last: [f64; 3], pad: f64) -> bool {
        let extension = TIP_CONE_R + pad;
        first[0].min(last[0]) < self.x1 + extension
            && first[0].max(last[0]) > self.x0 - extension
            && first[1].min(last[1]) < self.y1 + extension
            && first[1].max(last[1]) > self.y0 - extension
    }

    /// The raster's range of indices from `low` to `high` millimetres, along an axis from `origin`.
    fn span(low: f64, high: f64, origin: f64, count: i32) -> (i32, i32) {
        (0.max(((low - origin) / NEARBY_PITCH).ceil() as i32), (count - 1).min(((high - origin) / NEARBY_PITCH).floor() as i32))
    }

    #[allow(clippy::too_many_arguments)]
    fn add(&mut self, a: [f64; 3], b: [f64; 3], width: f64, height: f64, time0: f64, time1: f64, run: i32, object: i32, line: usize, removable: bool) {
        let (dx, dy) = (b[0] - a[0], b[1] - a[1]);
        let length2 = dx * dx + dy * dy;
        if length2 <= 1e-16 || width <= 0.0 || (!self.nearby(a) && !self.nearby(b)) {
            return;
        }
        let r = width / 2.0;
        let flat = at_least_zero((width - height) / 2.0);
        let flank = r - flat;
        let (i0, i1) = Self::span(a[0].min(b[0]) - r, a[0].max(b[0]) + r, self.x0, self.nx);
        let (j0, j1) = Self::span(a[1].min(b[1]) - r, a[1].max(b[1]) + r, self.y0, self.ny);
        for j in j0..=j1 {
            for i in i0..=i1 {
                let (ux, uy) = (self.x(i) - a[0], self.y(j) - a[1]);
                let t = ((ux * dx + uy * dy) / length2).clamp(0.0, 1.0);
                let (sx, sy) = (ux - t * dx, uy - t * dy);
                let lateral2 = sx * sx + sy * sy;
                if lateral2 > r * r {
                    continue;
                }
                let round_fraction = if flank <= 1e-9 { 0.0 } else { ((lateral2.sqrt() - flat) / flank).clamp(0.0, 1.0) };
                let edge_drop = height / 2.0 * (1.0 - (1.0 - round_fraction * round_fraction).sqrt());
                let z = a[2] + (b[2] - a[2]) * t - edge_drop;
                let last = &mut self.points[(j * self.nx + i) as usize];
                if z >= f64::from(last.height) - 1e-5 {
                    *last = LocalPoint { height: z as f32, time: (time0 + (time1 - time0) * t) as f32, run, object, line, removable };
                }
            }
        }
    }

    #[allow(clippy::too_many_arguments)]
    fn nozzle(&self, p: [f64; 3], time: f64, run: i32, object: i32, line: usize, feature: &Rc<str>, summary: &mut NozzleClearance, laying: bool) -> LocalSample {
        let mut sampled = LocalSample { fresh_flat: 0.0, adjacent: 0.0 };
        if !self.nearby(p) {
            return sampled;
        }
        if laying {
            summary.sampled += 1;
        } else {
            summary.travel_sampled += 1;
        }
        let (i0, i1) = Self::span(p[0] - TIP_CONE_R, p[0] + TIP_CONE_R, self.x0, self.nx);
        let (j0, j1) = Self::span(p[1] - TIP_CONE_R, p[1] + TIP_CONE_R, self.y0, self.ny);
        for j in j0..=j1 {
            for i in i0..=i1 {
                let last = &self.points[(j * self.nx + i) as usize];
                let height = f64::from(last.height);
                if height <= p[2] && height < p[2] - 0.3 {
                    continue;
                }
                let (ux, uy) = (self.x(i) - p[0], self.y(j) - p[1]);
                let r2 = ux * ux + uy * uy;
                if r2 > TIP_CONE_R * TIP_CONE_R {
                    continue;
                }
                let reading = |gap: f64, radius: f64| LocalClearance {
                    gap, nozzle: p, bead: [self.x(i), self.y(j), height], age: time - f64::from(last.time), radius, line,
                    source_line: last.line, object, deposited_by: last.object, feature: feature.clone(), earlier_bead_removable: last.removable,
                };
                if r2 < TIP_CENTER_R * TIP_CENTER_R {
                    let gap = p[2] - height;
                    if !laying && last.object != 0 && gap < summary.readings[DRY_CENTER].gap {
                        summary.readings[DRY_CENTER] = reading(gap, r2.sqrt());
                    }
                    continue;
                }
                let flat = r2 <= TIP_FLAT_R * TIP_FLAT_R;
                let shape = usize::from(!flat);
                let same_run = last.run == run && last.object == object;
                let radius = r2.sqrt();
                let rise = if flat { 0.0 } else { TIP_CONE_HEIGHT * (radius - TIP_FLAT_R) / (TIP_CONE_R - TIP_FLAT_R) };
                let gap = p[2] + rise - height;
                let (result, material) = if !laying {
                    (TRAVEL[shape], Some(if last.removable { DRY_SUPPORT[shape] } else { DRY_PART[shape] }))
                } else if same_run {
                    if !flat {
                        continue;
                    }
                    if gap < sampled.fresh_flat {
                        sampled.fresh_flat = gap;
                    }
                    (FRESH_FLAT, None)
                } else {
                    if gap < sampled.adjacent {
                        sampled.adjacent = gap;
                    }
                    (ADJACENT[shape], Some(if last.removable { EARLIER_SUPPORT[shape] } else { EARLIER_PART[shape] }))
                };
                let closer = gap < summary.readings[result].gap;
                let closer_material = material.is_some_and(|m| gap < summary.readings[m].gap);
                if closer || closer_material {
                    let found = reading(gap, radius);
                    if let Some(m) = material.filter(|_| closer_material) {
                        summary.readings[m] = found.clone();
                    }
                    if closer {
                        summary.readings[result] = found;
                    }
                }
            }
        }
        sampled
    }
}

/// One phase's moves, samples, time, extrusion and least clearances.
#[derive(Default)]
struct Activity {
    moves: usize,
    samples: usize,
    travel_samples: usize,
    travel_below_samples: usize,
    travel_below_moves: usize,
    unprimed_moves: usize,
    seconds: f64,
    max_z_feed: f64,
    max_deposit_z_feed: f64,
    extrusion: f64,
    max_retraction_debt_while_moving_extrusion: f64,
    body: Clearance,
    flank: Clearance,
    travel_body: Clearance,
    travel_tip: Clearance,
}

/// One object's extrusion: its first and last, its idle spans, and its bead bounds.
struct Object {
    first: f64,
    first_model: f64,
    last: f64,
    last_model: f64,
    max_model_gap: f64,
    max_gap: f64,
    extrusion: f64,
    first_layer_extrusion: f64,
    last_z: f64,
    max_gap_z_before: f64,
    max_gap_z_after: f64,
    max_gap_time_before: f64,
    max_gap_time_after: f64,
    first_z: f64,
    first_model_z: f64,
    first_280_time: f64,
    first_nozzle: f64,
    first_model_nozzle: f64,
    first_fan: f64,
    first_model_fan: f64,
    first_bed_temperature: f64,
    extrusion_first_bed_course_max_nozzle: f64,
    max: [f64; 3],
    min: [f64; 3],
    fan_extrusion: BTreeMap<i64, f64>,
}

impl Default for Object {
    fn default() -> Object {
        Object {
            first: -1.0, first_model: -1.0, last: -1.0, last_model: -1.0, max_model_gap: 0.0, max_gap: 0.0, extrusion: 0.0,
            first_layer_extrusion: 0.0, last_z: 0.0, max_gap_z_before: 0.0, max_gap_z_after: 0.0, max_gap_time_before: 0.0,
            max_gap_time_after: 0.0, first_z: 0.0, first_model_z: 0.0, first_280_time: -1.0, first_nozzle: 0.0, first_model_nozzle: 0.0,
            first_fan: 0.0, first_model_fan: 0.0, first_bed_temperature: 0.0, extrusion_first_bed_course_max_nozzle: 0.0,
            max: [f64::NEG_INFINITY; 3], min: [f64::INFINITY; 3], fan_extrusion: BTreeMap::new(),
        }
    }
}

/// A G2 or G3 arc in the XY plane: its centre, radius, start angle and signed sweep.
struct Arc {
    cx: f64,
    cy: f64,
    radius: f64,
    start: f64,
    sweep: f64,
}

impl Arc {
    fn new(a: [f64; 3], b: [f64; 3], words: &Words, clockwise: bool, absolute_center: bool) -> Result<Arc> {
        let tau = std::f64::consts::TAU;
        let (cx, cy) = if words.has(b'R') {
            let signed_radius = words.get(b'R');
            let radius = signed_radius.abs();
            let (dx, dy) = (b[0] - a[0], b[1] - a[1]);
            let chord = dx.hypot(dy);
            if chord <= 1e-9 || chord > 2.0 * radius + 0.002 || radius <= 1e-9 {
                bail!("invalid R arc");
            }
            let side = if clockwise == (signed_radius >= 0.0) { -1.0 } else { 1.0 };
            let rise = at_least_zero(radius * radius - chord * chord / 4.0).sqrt();
            ((a[0] + b[0]) / 2.0 - side * dy / chord * rise, (a[1] + b[1]) / 2.0 + side * dx / chord * rise)
        } else if absolute_center {
            (words.or(b'I', a[0]), words.or(b'J', a[1]))
        } else {
            (a[0] + words.get(b'I'), a[1] + words.get(b'J'))
        };
        let radius = (a[0] - cx).hypot(a[1] - cy);
        if radius <= 1e-9 {
            bail!("invalid IJ arc");
        }
        let start = (a[1] - cy).atan2(a[0] - cx);
        let turns = words.or(b'P', 1.0);
        if turns < 1.0 || turns != turns.floor() {
            bail!("invalid arc turns");
        }
        let sweep = if (a[0] - b[0]).hypot(a[1] - b[1]) < 1e-8 {
            (if clockwise { -tau } else { tau }) * turns
        } else {
            let end = (b[1] - cy).atan2(b[0] - cx);
            let mut sweep = (if clockwise { start - end } else { end - start }) % tau;
            if sweep <= 1e-9 {
                sweep += tau;
            }
            (if clockwise { -1.0 } else { 1.0 }) * (sweep + (turns - 1.0) * tau)
        };
        Ok(Arc { cx, cy, radius, start, sweep })
    }

    fn at(&self, a: [f64; 3], b: [f64; 3], fraction: f64) -> [f64; 3] {
        if fraction >= 1.0 {
            return b;
        }
        let angle = self.start + self.sweep * fraction;
        [self.cx + self.radius * angle.cos(), self.cy + self.radius * angle.sin(), a[2] + fraction * (b[2] - a[2])]
    }
}

/// Values by name, read in name order.
struct Named<T> {
    items: Vec<T>,
    index: BTreeMap<String, usize>,
}

impl<T: Default> Named<T> {
    fn new() -> Named<T> {
        Named { items: Vec::new(), index: BTreeMap::new() }
    }

    fn entry(&mut self, name: &str) -> usize {
        if let Some(&i) = self.index.get(name) {
            return i;
        }
        self.items.push(T::default());
        self.index.insert(name.to_string(), self.items.len() - 1);
        self.items.len() - 1
    }

    fn sorted(&self) -> impl Iterator<Item = (&String, &T)> {
        self.index.iter().map(|(name, &i)| (name, &self.items[i]))
    }
}

fn witness(best: &mut Clearance, gap: f64, p: [f64; 3], time: f64, line: usize, object: i32, obstacle: &Cell, dx: i32, dy: i32) {
    if gap < best.gap {
        *best = Clearance { gap, xyz: p, time, line, object, obstacle: obstacle.object, offset_x: dx, offset_y: dy, earlier_bead_removable: obstacle.removable };
    }
}

struct Replay {
    head: Head,
    terrain: Terrain,
    local: Vec<LocalTerrain>,
    local_by_phase: Named<NozzleClearance>,
    near_active: usize,
    local_phase: String,
    phase_stats: Named<Activity>,
    active: usize,
    objects: BTreeMap<i32, Object>,
    opaque_commands: BTreeMap<String, usize>,
    phase: String,
    feature: Rc<str>,
    current: [f64; 3],
    offset: [f64; 3],
    e: f64,
    debt: f64,
    feed: f64,
    rate_multiplier: f64,
    flow_multiplier: f64,
    time: f64,
    fan: f64,
    nozzle: f64,
    bed_temperature: f64,
    width: f64,
    limits: [f64; 4],
    largest_relative_obstacle: f64,
    fixed_wait: f64,
    absolute: bool,
    absolute_e: bool,
    absolute_center: bool,
    xy_plane: bool,
    recording: bool,
    ended: bool,
    prior_is_laying: bool,
    run: i32,
    line: usize,
    arcs: usize,
    spiral_arcs: usize,
    unknown_deposit: usize,
    object: i32,
    high_relative: Clearance,
    travel_violations: Vec<Clearance>,
    cross_object_witness: Clearance,
    first_three_by_object: BTreeMap<i32, [f64; 6]>,
}

impl Replay {
    fn new(map: &HeadMap, windows: &[[f64; 4]]) -> Result<Replay> {
        let (mut local_by_phase, mut phase_stats) = (Named::new(), Named::new());
        let (near_active, active) = (local_by_phase.entry("native"), phase_stats.entry("native"));
        Ok(Replay {
            head: Head::new(map)?,
            terrain: Terrain::new(),
            local: windows.iter().map(|&w| LocalTerrain::new(w)).collect(),
            local_by_phase,
            near_active,
            local_phase: "native".into(),
            phase_stats,
            active,
            objects: BTreeMap::new(),
            opaque_commands: BTreeMap::new(),
            phase: "native".into(),
            feature: Rc::from(""),
            current: [0.0; 3],
            offset: [0.0; 3],
            e: 0.0,
            debt: 0.0,
            feed: 0.0,
            rate_multiplier: 1.0,
            flow_multiplier: 1.0,
            time: 0.0,
            fan: 0.0,
            nozzle: 0.0,
            bed_temperature: 0.0,
            width: 0.42,
            limits: START_LIMITS,
            largest_relative_obstacle: 0.0,
            fixed_wait: 0.0,
            absolute: true,
            absolute_e: false,
            absolute_center: false,
            xy_plane: true,
            recording: false,
            ended: false,
            prior_is_laying: false,
            run: 0,
            line: 0,
            arcs: 0,
            spiral_arcs: 0,
            unknown_deposit: 0,
            object: 0,
            high_relative: Clearance { gap: f64::NEG_INFINITY, ..Clearance::default() },
            travel_violations: Vec::new(),
            cross_object_witness: Clearance::default(),
            first_three_by_object: BTreeMap::new(),
        })
    }

    /// Reads the head's and the tip's clearance at `p`; true when a travel there runs below a laid bead.
    fn sample(&mut self, p: [f64; 3], laying: bool, sample_time: f64) -> bool {
        let Replay { head, terrain, phase_stats, active, largest_relative_obstacle, high_relative, travel_violations, cross_object_witness, line, object, .. } = self;
        let (line, object) = (*line, *object);
        let result = &mut phase_stats.items[*active];
        result.samples += 1;
        let i = Terrain::index_x(p[0]);
        let j = Terrain::index_y(p[1]);
        let below = *terrain.get(i, j);
        let below_height = f64::from(below.height);
        if !laying {
            result.travel_samples += 1;
            witness(&mut result.travel_tip, p[2] - below_height, p, sample_time, line, object, &below, 0, 0);
            if below_height > 0.0 && p[2] < below_height - TRAVEL_TOLERANCE && travel_violations.len() < ANOMALIES {
                let mut occurrence = Clearance::default();
                witness(&mut occurrence, p[2] - below_height, p, sample_time, line, object, &below, 0, 0);
                travel_violations.push(occurrence);
            }
        }
        let (ti, tj) = (i.div_euclid(TILE), j.div_euclid(TILE));
        let blocks = &head.body[((j - tj * TILE) * TILE + i - ti * TILE) as usize];
        for block in blocks {
            let (block_x, block_y) = (ti + block.dx, tj + block.dy);
            let peak = terrain.tile_max(block_x, block_y);
            let possible = p[2] + block.underside - peak;
            let below_nozzle = peak - p[2];
            if below_nozzle > *largest_relative_obstacle {
                // A tile maximum is only a cheap upper bound. Confirm its nearest modeled cell.
                let mut verified = *largest_relative_obstacle;
                for item in &block.cells {
                    let floor = terrain.get(i + item.x, j + item.y);
                    let delta = f64::from(floor.height) - p[2];
                    if delta > verified {
                        verified = delta;
                        *high_relative = Clearance { gap: delta, xyz: p, time: sample_time, line, object, obstacle: floor.object,
                                                     offset_x: item.x, offset_y: item.y, earlier_bead_removable: floor.removable };
                    }
                }
                *largest_relative_obstacle = verified;
            }
            let threshold = if laying { result.body.gap } else { result.body.gap.max(result.travel_body.gap) };
            let compare_other = laying && object != 0 && possible < cross_object_witness.gap
                && terrain.tile_may_have_other_object(block_x, block_y, object);
            if possible >= threshold && !compare_other {
                continue;
            }
            for item in &block.cells {
                let floor = terrain.get(i + item.x, j + item.y);
                let gap = p[2] + item.height - f64::from(floor.height);
                witness(&mut result.body, gap, p, sample_time, line, object, floor, item.x, item.y);
                if !laying {
                    witness(&mut result.travel_body, gap, p, sample_time, line, object, floor, item.x, item.y);
                }
                if compare_other && floor.object != 0 && floor.object != object {
                    witness(cross_object_witness, gap, p, sample_time, line, object, floor, item.x, item.y);
                }
            }
        }
        for item in &head.flank {
            let floor = terrain.get(i + item.x, j + item.y);
            let gap = p[2] + item.height - f64::from(floor.height);
            witness(&mut result.flank, gap, p, sample_time, line, object, floor, item.x, item.y);
        }
        let bad_travel = !laying && below_height > 0.0 && p[2] < below_height - TRAVEL_TOLERANCE;
        if bad_travel {
            result.travel_below_samples += 1;
        }
        bad_travel
    }

    /// Stamps the swept nominal bead footprint. The nearest cell-centre fallback retains thin beads.
    fn deposit(&mut self, from: [f64; 3], to: [f64; 3], print_width: f64) {
        let radius = print_width / 2.0;
        let disposable = removable_feature(&self.feature);
        let (dx, dy) = (to[0] - from[0], to[1] - from[1]);
        let denominator = dx * dx + dy * dy;
        if denominator <= 1e-16 {
            return;
        }
        let (max_x, min_x) = (from[0].max(to[0]) + radius, from[0].min(to[0]) - radius);
        let (max_y, min_y) = (from[1].max(to[1]) + radius, from[1].min(to[1]) - radius);
        for j in Terrain::index_y(min_y)..=Terrain::index_y(max_y) {
            for i in Terrain::index_x(min_x)..=Terrain::index_x(max_x) {
                let (rx, ry) = (Terrain::x_at(i) - from[0], Terrain::y_at(j) - from[1]);
                let factor = ((rx * dx + ry * dy) / denominator).clamp(0.0, 1.0);
                if (rx - dx * factor).hypot(ry - dy * factor) <= radius {
                    let z = from[2] + (to[2] - from[2]) * factor;
                    self.terrain.add(i, j, z as f32, self.object, disposable);
                }
            }
        }
        // The centerline's ends, even when a road is narrower than the grid.
        for p in [from, to] {
            self.terrain.add(Terrain::index_x(p[0]), Terrain::index_y(p[1]), p[2] as f32, self.object, disposable);
        }
    }

    fn stat_extrusion(&mut self, from: [f64; 3], to: [f64; 3], amount: f64) {
        let solid = !removable_feature(&self.feature);
        if self.object == 0 {
            self.unknown_deposit += 1;
        }
        let (time, nozzle, fan, width, object) = (self.time, self.nozzle, self.fan, self.width, self.object);
        let row = self.objects.entry(object).or_default();
        if row.first < 0.0 {
            row.first = time;
            row.first_z = to[2];
            row.first_nozzle = nozzle;
            row.first_bed_temperature = self.bed_temperature;
            row.first_fan = fan;
        } else if time - row.last > row.max_gap {
            row.max_gap = time - row.last;
            row.max_gap_time_before = row.last;
            row.max_gap_time_after = time;
            row.max_gap_z_before = row.last_z;
            row.max_gap_z_after = to[2];
        }
        row.last = time;
        row.last_z = to[2];
        if solid {
            if row.first_model < 0.0 {
                row.first_model = time;
                row.first_model_z = to[2];
                row.first_model_nozzle = nozzle;
                row.first_model_fan = fan;
            } else {
                row.max_model_gap = row.max_model_gap.max(time - row.last_model);
            }
            row.last_model = time;
        }
        if row.first_280_time < 0.0 && nozzle >= 278.0 {
            row.first_280_time = time;
        }
        row.extrusion += amount;
        *row.fan_extrusion.entry(fan.round() as i64).or_default() += amount;
        let bead_top = from[2].max(to[2]);
        if bead_top <= 0.205 {
            row.first_layer_extrusion += amount;
            row.extrusion_first_bed_course_max_nozzle = nozzle.max(row.extrusion_first_bed_course_max_nozzle);
        }
        for axis in 0..2 {
            row.min[axis] = row.min[axis].min(from[axis].min(to[axis]) - width / 2.0);
            row.max[axis] = row.max[axis].max(from[axis].max(to[axis]) + width / 2.0);
        }
        row.min[2] = row.min[2].min(from[2].min(to[2]));
        row.max[2] = row.max[2].max(from[2].max(to[2]));
        if object > 0 && object != 1901 && bead_top <= 0.685 {
            let course = if bead_top <= 0.205 { 0 } else if bead_top <= 0.445 { 1 } else { 2 };
            let reported = self.first_three_by_object.entry(object).or_default();
            reported[2 * course] += amount;
            if nozzle > 270.0 {
                reported[2 * course + 1] += amount;
            }
        }
    }

    fn set_phase(&mut self, name: &str) {
        self.phase = if name.is_empty() { "native".into() } else { name.to_string() };
        self.active = self.phase_stats.entry(&self.phase);
        self.local_phase = self.phase.clone();
        self.near_active = self.local_by_phase.entry(&self.local_phase);
    }

    fn comment(&mut self, kind: &str) {
        if kind == "MACHINE_START_GCODE_END" {
            self.recording = true;
            self.debt = 0.0;
            return;
        }
        if kind == "MACHINE_END_GCODE_START" {
            self.ended = true;
            return;
        }
        if !self.recording {
            return;
        }
        let number = |key: &str| strtod(&kind.as_bytes()[key.len()..]);
        if let Some(rest) = kind.strip_prefix("FEATURE:") {
            self.feature = Rc::from(trim(rest));
        } else if kind.starts_with("LINE_WIDTH:") {
            self.width = number("LINE_WIDTH:");
        } else if kind.starts_with("OBJECT_ID:") {
            // OBJECT_ID sometimes anticipates a later start. The explicit start/stop label governs.
            // Whole-base study tapes carry that object identifier only.
            if self.local_phase == "donated tilted base" {
                self.object = number("OBJECT_ID:").round() as i32;
            }
        } else if kind.starts_with("start printing object, unique label id:") {
            self.object = number("start printing object, unique label id:").round() as i32;
        } else if kind.starts_with("stop printing object") {
            self.object = 0;
        } else if kind.starts_with("===== sloped underside") {
            self.set_phase("sloped underside");
            self.object = 1901;
        } else if kind.starts_with("===== end of the sloped underside") {
            self.set_phase("native");
            self.object = 0;
        } else if let Some(rest) = kind.strip_prefix("HSM_PHASE:") {
            self.set_phase(trim(rest));
        } else if let Some(rest) = kind.strip_prefix("HSM_PHASE_TRAVEL:") {
            let name = trim(rest);
            self.set_phase(if name == "final clearance lift" { name } else { "transfers between course groups" });
        } else if let Some(rest) = kind.strip_prefix("HSM_DONOR_PHASE:") {
            self.set_phase(trim(rest));
        } else if let Some(rest) = kind.strip_prefix("HSM_BRIDGE_STITCH:") {
            self.set_phase(trim(rest));
        } else if let Some(rest) = kind.strip_prefix("HSM_TIP_PHASE:") {
            self.set_phase(trim(rest));
        }
    }

    fn command(&mut self, text: &str) -> Result<()> {
        let stop = text.find([' ', '\t']);
        let op = &text[..stop.unwrap_or(text.len())];
        let words = Words::new(stop.map_or("", |s| &text[s..]));
        match op {
            "G90" => self.absolute = true,
            "G91" => self.absolute = false,
            "G90.1" => self.absolute_center = true,
            "G91.1" => self.absolute_center = false,
            "M82" => self.absolute_e = true,
            "M83" => self.absolute_e = false,
            "G17" => self.xy_plane = true,
            "G18" | "G19" => self.xy_plane = false,
            "G92" => {
                for (axis, key) in b"XYZ".iter().enumerate() {
                    if words.has(*key) {
                        self.offset[axis] = self.current[axis] - words.get(*key);
                    }
                }
                if words.has(b'E') {
                    self.e = words.get(b'E');
                }
            }
            "M203" => {
                for (limit, key) in self.limits.iter_mut().zip(b"XYZE") {
                    *limit = words.or(*key, *limit);
                }
            }
            "M220" => self.rate_multiplier = words.or(b'S', 100.0) / 100.0,
            "M221" => {
                if words.has(b'S') {
                    self.flow_multiplier = words.get(b'S') / 100.0;
                }
            }
            "M106" if words.or(b'P', 1.0) == 1.0 => self.fan = words.or(b'S', 255.0),
            "M107" if words.or(b'P', 1.0) == 1.0 => self.fan = 0.0,
            "M140" | "M190" => {
                self.bed_temperature = words.or(b'S', words.or(b'R', self.bed_temperature));
                if self.recording && op == "M190" {
                    *self.opaque_commands.entry(op.to_string()).or_default() += 1;
                }
            }
            "M104" | "M109" => {
                self.nozzle = words.or(b'S', words.or(b'R', self.nozzle));
                if self.recording && op == "M109" {
                    *self.opaque_commands.entry(op.to_string()).or_default() += 1;
                }
            }
            "G4" => {
                if self.recording {
                    let dwell = words.get(b'P') / 1000.0 + words.get(b'S');
                    self.fixed_wait += dwell;
                    self.time += dwell;
                    self.phase_stats.items[self.active].seconds += dwell;
                }
            }
            "G0" | "G1" | "G2" | "G3" => self.motion(op, &words)?,
            _ => {
                if self.recording
                    && (op.starts_with('T') || matches!(op, "G20" | "G5" | "G10" | "G11" | "M400")
                        || op.starts_with("G28") || op.starts_with("G29") || op.starts_with("G387"))
                {
                    *self.opaque_commands.entry(op.to_string()).or_default() += 1;
                }
            }
        }
        Ok(())
    }

    fn motion(&mut self, op: &str, words: &Words) -> Result<()> {
        if words.has(b'F') {
            self.feed = words.get(b'F') / 60.0;
        }
        let mut to = self.current;
        for (axis, key) in b"XYZ".iter().enumerate() {
            if words.has(*key) {
                to[axis] = if self.absolute { words.get(*key) + self.offset[axis] } else { self.current[axis] + words.get(*key) };
            }
        }
        let de = if words.has(b'E') { if self.absolute_e { words.get(b'E') - self.e } else { words.get(b'E') } } else { 0.0 };
        if words.has(b'E') {
            self.e = if self.absolute_e { words.get(b'E') } else { self.e + de };
        }
        let from = self.current;
        self.current = to;
        if !self.recording {
            return Ok(());
        }
        let (dz, dx, dy) = (to[2] - from[2], to[0] - from[0], to[1] - from[1]);
        let arc = op == "G2" || op == "G3";
        if arc && !self.xy_plane {
            bail!("non-XY arc");
        }
        let curve = if arc { Some(Arc::new(from, to, words, op == "G2", self.absolute_center)?) } else { None };
        let dxy = curve.as_ref().map_or_else(|| dx.hypot(dy), |c| c.radius * c.sweep.abs());
        let length = dxy.hypot(dz);
        if length <= 1e-9 && de.abs() <= 1e-9 {
            return Ok(());
        }
        if self.feed <= 0.0 || self.rate_multiplier <= 0.0 {
            bail!("motion or extrusion has no positive feed");
        }
        if arc {
            self.arcs += 1;
            if dx.hypot(dy) < 1e-8 && dz.abs() > 1e-9 {
                self.spiral_arcs += 1;
            }
        }
        let positive_e = de > 1e-9;
        let needed = if positive_e { if de < self.debt { de } else { self.debt } } else { 0.0 };
        let printed = if positive_e { (de - needed) * self.flow_multiplier } else { 0.0 };
        self.debt = at_least_zero(self.debt - de);
        let active = &mut self.phase_stats.items[self.active];
        if de > 0.0 && dxy > 1e-8 && needed > 0.01 {
            active.unprimed_moves += 1;
            active.max_retraction_debt_while_moving_extrusion = active.max_retraction_debt_while_moving_extrusion.max(needed);
        }
        let laying = positive_e && dxy > 1e-8 && printed > 1e-9;
        if laying && !self.prior_is_laying {
            self.run += 1;
        }
        self.prior_is_laying = laying;
        let capped_feed = self.feed * self.rate_multiplier;
        let [x_limit, y_limit, z_limit, e_limit] = self.limits;
        let axis_seconds = (dx.abs() / x_limit).max(dy.abs() / y_limit).max(dz.abs() / z_limit).max(de.abs() / e_limit);
        let seconds = axis_seconds.max((if length > 1e-9 { length } else { de.abs() }) / capped_feed);
        active.moves += 1;
        active.seconds += seconds;
        let z_rate = if length > 1e-9 { dz.abs() / length * capped_feed } else { 0.0 };
        active.max_z_feed = active.max_z_feed.max(z_rate);
        if laying {
            active.max_deposit_z_feed = active.max_deposit_z_feed.max(z_rate);
            active.extrusion += printed;
        }
        if length > 1e-9 {
            let pad = curve.as_ref().map_or(0.0, |c| 2.0 * c.radius);
            let near_motion = self.local.iter().any(|zone| zone.possibly_crosses(from, to, pad));
            let step = if near_motion { NEARBY_PITCH } else if arc { ARC_SAMPLE } else { MOTION_SAMPLE };
            let samples = ((length / step).ceil() as i32).max(1);
            let raw_section = printed * (std::f64::consts::PI * FILAMENT_DIAMETER * FILAMENT_DIAMETER / 4.0) / length;
            let nominal_section = raw_section / (FLOW * if &*self.feature == "Bridge" { BRIDGE_FLOW } else { 1.0 });
            let factor = 1.0 - std::f64::consts::PI / 4.0;
            let width = self.width;
            let disc = at_least_zero(width * width - 4.0 * factor * nominal_section);
            let local_height = ((width - disc.sqrt()) / (2.0 * factor)).clamp(0.0, at_least_zero(width));
            let horizontal_length = dxy / f64::from(samples);
            let compare_fresh_flat = near_motion && laying && dz < -0.01 && local_height > 0.0;
            let disposable = removable_feature(&self.feature);
            let outer_wall = &*self.feature == "Outer wall";
            if near_motion && laying {
                let near = &mut self.local_by_phase.items[self.near_active];
                near.total_road_mm += dxy;
                if outer_wall {
                    near.outer_wall_mm += dxy;
                }
                if dz < -1e-6 {
                    near.downslope_road_mm += dxy;
                }
                // The straight, continuously laid road behind the tip spans the annulus.
                if compare_fresh_flat && dz.abs() / dxy * TIP_FLAT_R > 0.05 {
                    near.fresh_flat_past_005_road_mm += dxy;
                    if outer_wall {
                        near.outer_wall_fresh_past_005_road_mm += dxy;
                    }
                }
            }
            let mut a = from;
            let mut travel = false;
            let delay = if positive_e { needed / de } else { 0.0 };
            for segment in 1..=samples {
                let fraction = f64::from(segment) / f64::from(samples);
                let p = match &curve {
                    Some(c) => c.at(from, to, fraction),
                    None => std::array::from_fn(|axis| from[axis] + (to[axis] - from[axis]) * fraction),
                };
                let at = self.time + fraction * seconds;
                let depositing = laying && fraction > delay;
                travel |= self.sample(p, depositing, at);
                if near_motion {
                    let mut point = LocalSample { fresh_flat: 0.0, adjacent: 0.0 };
                    let near = &mut self.local_by_phase.items[self.near_active];
                    for zone in &self.local {
                        if zone.nearby(p) {
                            let one = zone.nozzle(p, at, self.run, self.object, self.line, &self.feature, near, depositing);
                            if one.fresh_flat < point.fresh_flat {
                                point.fresh_flat = one.fresh_flat;
                            }
                            if one.adjacent < point.adjacent {
                                point.adjacent = one.adjacent;
                            }
                        }
                    }
                    if depositing {
                        if point.fresh_flat < -0.05 {
                            near.sampled_fresh_flat_past_005_road_mm += horizontal_length;
                            if outer_wall {
                                near.outer_wall_sampled_fresh_past_005_road_mm += horizontal_length;
                            }
                        }
                        if point.adjacent < -0.1 {
                            near.adjacent_past_01_road_mm += horizontal_length;
                            if outer_wall {
                                near.outer_wall_adjacent_past_01_road_mm += horizontal_length;
                            }
                        }
                        if point.adjacent < -0.2 {
                            near.adjacent_past_02_road_mm += horizontal_length;
                        }
                    }
                }
                if depositing {
                    if segment == 1 && delay > 0.0 {
                        a = std::array::from_fn(|axis| from[axis] + (to[axis] - from[axis]) * delay);
                    }
                    let start = self.time + (fraction - 1.0 / f64::from(samples)) * seconds;
                    self.deposit(a, p, width);
                    if near_motion {
                        for zone in &mut self.local {
                            if zone.nearby(p) || zone.nearby(a) {
                                zone.add(a, p, width, local_height, start, at, self.run, self.object, self.line, disposable);
                            }
                        }
                    }
                    self.stat_extrusion(a, p, printed / f64::from(samples));
                }
                a = p;
            }
            if travel {
                self.phase_stats.items[self.active].travel_below_moves += 1;
            }
        }
        self.time += seconds;
        Ok(())
    }

    fn read(&mut self, gcode: &Path) -> Result<()> {
        let mut stream = BufReader::new(std::fs::File::open(gcode).with_context(|| format!("reading {}", gcode.display()))?);
        let mut raw = Vec::new();
        loop {
            raw.clear();
            if stream.read_until(b'\n', &mut raw)? == 0 {
                break;
            }
            if raw.last() == Some(&b'\n') {
                raw.pop();
            }
            self.line += 1;
            let text = String::from_utf8_lossy(&raw);
            let text = trim(&text);
            let handled = if let Some(comment) = text.strip_prefix(';') {
                self.comment(trim(comment));
                Ok(())
            } else if !text.is_empty() {
                self.command(trim(&text[..text.find(';').unwrap_or(text.len())]))
            } else {
                Ok(())
            };
            handled.with_context(|| format!("line {}", self.line))?;
            if self.ended {
                break;
            }
        }
        ensure!(self.ended && self.recording, "machine-start or machine-end boundaries absent");
        Ok(())
    }
}

/// `x` as the report writes a real number: fixed, to five places.
fn real(out: &mut String, x: f64) {
    if x.is_nan() {
        out.push_str("nan");
    } else if x.is_infinite() {
        out.push_str(if x > 0.0 { "inf" } else { "-inf" });
    } else {
        let _ = write!(out, "{x:.5}");
    }
}

fn reals(out: &mut String, xs: &[f64]) {
    out.push('[');
    for (n, &x) in xs.iter().enumerate() {
        if n > 0 {
            out.push_str(", ");
        }
        real(out, x);
    }
    out.push(']');
}

fn quote(out: &mut String, value: &str) {
    out.push('"');
    for c in value.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\t' => out.push_str("\\t"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            _ => out.push(c),
        }
    }
    out.push('"');
}

fn local_clearance(out: &mut String, found: &LocalClearance) {
    if !found.gap.is_finite() {
        out.push_str("null");
        return;
    }
    out.push_str("{\"gap_mm\": ");
    real(out, found.gap);
    let _ = write!(out, ", \"line\": {}, \"from_line\": {}, \"nozzle_xyz_mm\": ", found.line, found.source_line);
    reals(out, &found.nozzle);
    out.push_str(", \"deposited_xyz_mm\": ");
    reals(out, &found.bead);
    out.push_str(", \"deposited_age_s_at_nominal_feed\": ");
    real(out, found.age);
    out.push_str(", \"distance_from_tip_center_mm\": ");
    real(out, found.radius);
    let _ = write!(out, ", \"object\": {}, \"deposited_by\": {}, \"feature\": ", found.object, found.deposited_by);
    quote(out, &found.feature);
    if found.source_line > 0 {
        let _ = write!(out, ", \"deposited_material\": \"{}\"", if found.earlier_bead_removable { "support" } else { "part" });
    }
    out.push('}');
}

fn clearance(out: &mut String, found: &Clearance) {
    if !found.gap.is_finite() {
        out.push_str("null");
        return;
    }
    out.push_str("{\"gap_mm\": ");
    real(out, found.gap);
    let _ = write!(out, ", \"line\": {}, \"xyz_mm\": ", found.line);
    reals(out, &found.xyz);
    out.push_str(", \"head_cell_offset_xy_mm\": ");
    reals(out, &[f64::from(found.offset_x) * PITCH, f64::from(found.offset_y) * PITCH]);
    let _ = write!(out, ", \"object\": {}, \"deposited_by\": {}, \"minimum_elapsed_s\": ", found.object, found.obstacle);
    real(out, found.time);
    if found.obstacle > 0 {
        let _ = write!(out, ", \"deposited_material\": \"{}\"", if found.earlier_bead_removable { "support" } else { "part" });
    }
    out.push('}');
}

fn report(replay: &Replay) -> String {
    let mut os = String::new();
    let out = &mut os;
    let field = |out: &mut String, name: &str, x: f64| {
        let _ = write!(out, ",\n  \"{name}\": ");
        real(out, x);
    };
    out.push_str("{\n  \"grid_mm\": ");
    real(out, PITCH);
    field(out, "motion_sample_mm", MOTION_SAMPLE);
    field(out, "arc_step_mm", ARC_SAMPLE);
    let _ = write!(out, ",\n  \"arc_count\": {},\n  \"full_turn_lifts\": {}", replay.arcs, replay.spiral_arcs);
    field(out, "declared_dwell_s", replay.fixed_wait);
    field(out, "minimum_feed_time_s", replay.time);
    let _ = write!(out, ",\n  \"unknown_extrusion_samples\": {},\n  \"unexpanded_machine_commands\": {{", replay.unknown_deposit);
    for (n, (key, count)) in replay.opaque_commands.iter().enumerate() {
        if n > 0 {
            out.push_str(", ");
        }
        quote(out, key);
        let _ = write!(out, ": {count}");
    }
    out.push('}');
    field(out, "largest_prior_terrain_height_above_active_tip_mm", replay.largest_relative_obstacle);
    out.push_str(",\n  \"largest_prior_terrain_witness\": ");
    clearance(out, &replay.high_relative);
    out.push_str(",\n  \"modeled_cross_object_clearance_witness_while_depositing\": ");
    clearance(out, &replay.cross_object_witness);
    out.push_str(",\n  \"first_three_companion_courses_by_extrusion_temperature\": {");
    for (n, (id, courses)) in replay.first_three_by_object.iter().enumerate() {
        if n > 0 {
            out.push_str(", ");
        }
        let _ = write!(out, "\"{id}\": [");
        for course in 0..3 {
            if course > 0 {
                out.push_str(", ");
            }
            out.push_str("{\"net_filament_mm\": ");
            real(out, courses[2 * course]);
            out.push_str(", \"net_at_nozzle_setpoint_over_270_c_mm\": ");
            real(out, courses[2 * course + 1]);
            out.push('}');
        }
        out.push(']');
    }
    out.push_str("},\n  \"phases\": {");
    for (n, (key, stats)) in replay.phase_stats.sorted().enumerate() {
        if n > 0 {
            out.push(',');
        }
        out.push_str("\n    ");
        quote(out, key);
        let _ = write!(out, ": {{\n      \"moves\": {}, \"samples\": {}, \"travel_samples\": {}, \"minimum_feed_time_s\": ",
                       stats.moves, stats.samples, stats.travel_samples);
        real(out, stats.seconds);
        out.push_str(", \"extrusion_mm\": ");
        real(out, stats.extrusion);
        for (name, found) in [("minimum_head_body", &stats.body), ("minimum_travel_head_body", &stats.travel_body),
                              ("minimum_nozzle_flank", &stats.flank), ("minimum_travel_tip", &stats.travel_tip)] {
            let _ = write!(out, ",\n      \"{name}\": ");
            clearance(out, found);
        }
        let _ = write!(out, ",\n      \"travel_samples_below_prior_bead_by_over_0_31_mm\": {}, \"affected_moves\": {}",
                       stats.travel_below_samples, stats.travel_below_moves);
        let _ = write!(out, ",\n      \"extrusion_travelling_with_retraction_debt\": {}, \"maximum_retraction_mismatch_mm\": ", stats.unprimed_moves);
        real(out, stats.max_retraction_debt_while_moving_extrusion);
        out.push_str(",\n      \"max_commanded_z_mm_per_s\": ");
        real(out, stats.max_z_feed);
        out.push_str(", \"max_commanded_extruding_z_mm_per_s\": ");
        real(out, stats.max_deposit_z_feed);
        out.push_str("\n    }");
    }
    out.push_str("\n  },\n  \"local_nozzle_model\": {");
    let mut first = true;
    for (key, contact) in replay.local_by_phase.sorted() {
        if contact.sampled == 0 && contact.travel_sampled == 0 {
            continue;
        }
        if !first {
            out.push(',');
        }
        first = false;
        out.push_str("\n    ");
        quote(out, key);
        let _ = write!(out, ": {{\n      \"extrusion_samples\": {}, \"travel_samples\": {}", contact.sampled, contact.travel_sampled);
        let each = |out: &mut String, separator: &str, name: &str, x: f64| {
            let _ = write!(out, "{separator}\"{name}\": ");
            real(out, x);
        };
        each(out, ", ", "tested_road_mm", contact.total_road_mm);
        each(out, ", ", "downhill_road_mm", contact.downslope_road_mm);
        each(out, ", ", "outer_wall_road_mm", contact.outer_wall_mm);
        each(out, ", ", "outer_wall_straight_descent_flat_relief_demand_over_0_05_mm_road_mm", contact.outer_wall_fresh_past_005_road_mm);
        each(out, ", ", "straight_descent_flat_relief_demand_over_0_05_mm_road_mm", contact.fresh_flat_past_005_road_mm);
        each(out, ",\n      ", "road_mm_sampled_fresh_flat_gap_below_minus_0_05", contact.sampled_fresh_flat_past_005_road_mm);
        each(out, ", ", "outer_wall_road_mm_sampled_fresh_flat_gap_below_minus_0_05", contact.outer_wall_sampled_fresh_past_005_road_mm);
        each(out, ", ", "outer_wall_road_mm_adjacent_model_gap_below_minus_0_1", contact.outer_wall_adjacent_past_01_road_mm);
        each(out, ",\n      ", "road_mm_adjacent_model_gap_below_minus_0_1", contact.adjacent_past_01_road_mm);
        each(out, ", ", "road_mm_adjacent_model_gap_below_minus_0_2", contact.adjacent_past_02_road_mm);
        for (name, found) in READINGS.iter().zip(&contact.readings) {
            let _ = write!(out, ",\n      \"{name}\": ");
            local_clearance(out, found);
        }
        out.push_str("\n    }");
    }
    out.push_str("\n  },\n  \"objects\": {");
    let (mut low, mut high) = ([f64::INFINITY; 3], [f64::NEG_INFINITY; 3]);
    for (n, (id, row)) in replay.objects.iter().enumerate() {
        if n > 0 {
            out.push(',');
        }
        let _ = write!(out, "\n    \"{id}\": {{");
        let values = [
            ("first_extrusion_s", row.first),
            ("first_model_s", row.first_model),
            ("first_extrusion_z_mm", row.first_z),
            ("first_model_z_mm", row.first_model_z),
            ("first_extrusion_commanded_nozzle_c", row.first_nozzle),
            ("first_extrusion_commanded_bed_c", row.first_bed_temperature),
            ("first_model_commanded_nozzle_c", row.first_model_nozzle),
            ("first_model_commanded_fan_pwm", row.first_model_fan),
            ("first_extrusion_commanded_fan_pwm", row.first_fan),
            ("first_extrusion_at_regular_nozzle_temp_s", row.first_280_time),
            ("max_model_idle_s", row.max_model_gap),
            ("max_extrusion_idle_s", row.max_gap),
        ];
        for (k, (name, x)) in values.into_iter().enumerate() {
            let _ = write!(out, "{}\"{name}\": ", if k > 0 { ", " } else { "" });
            real(out, x);
        }
        out.push_str(", \"max_extrusion_idle_between_z_mm\": ");
        reals(out, &[row.max_gap_z_before, row.max_gap_z_after]);
        out.push_str(", \"max_extrusion_idle_at_s\": ");
        reals(out, &[row.max_gap_time_before, row.max_gap_time_after]);
        out.push_str(", \"extrusion_mm\": ");
        real(out, row.extrusion);
        out.push_str(", \"first_bed_course_extrusion_mm\": ");
        real(out, row.first_layer_extrusion);
        out.push_str(", \"first_bed_course_max_commanded_nozzle_c\": ");
        real(out, row.extrusion_first_bed_course_max_nozzle);
        out.push_str(", \"bead_bounds_mm\": [");
        reals(out, &row.min);
        out.push_str(", ");
        reals(out, &row.max);
        out.push_str("], \"extrusion_mm_by_commanded_fan_pwm\": {");
        for (k, (pwm, amount)) in row.fan_extrusion.iter().enumerate() {
            let _ = write!(out, "{}\"{pwm}\": ", if k > 0 { ", " } else { "" });
            real(out, *amount);
        }
        out.push_str("}}");
        for axis in 0..3 {
            low[axis] = low[axis].min(row.min[axis]);
            high[axis] = high[axis].max(row.max[axis]);
        }
    }
    out.push_str("\n  },\n  \"extrusion_bounds_mm\": [");
    reals(out, &low);
    out.push_str(", ");
    reals(out, &high);
    out.push_str("],");
    out.push_str("\n  \"minimum_shared_bed_edge_inset_mm\": ");
    real(out, [low[1], BED[0] - high[0], BED[1] - high[1]].into_iter().fold(low[0], |m, x| if x < m { x } else { m }));
    field(out, "height_available_above_deposited_mm", BED[2] - high[2]);
    out.push_str(",\n  \"initial_travel_anomalies\": [");
    for (n, anomaly) in replay.travel_violations.iter().enumerate() {
        if n > 0 {
            out.push_str(", ");
        }
        out.push_str("\n    ");
        clearance(out, anomaly);
    }
    out.push_str("\n  ]\n}\n");
    os
}

/// The replay of the plate G-code at `gcode` under the head map at `head_map`, as its report's text.
pub fn replay(gcode: &Path, head_map: &Path) -> Result<String> {
    let map = HeadMap::read(head_map)?;
    let mut replay = Replay::new(&map, &WINDOWS)?;
    replay.read(gcode)?;
    Ok(report(&replay))
}
