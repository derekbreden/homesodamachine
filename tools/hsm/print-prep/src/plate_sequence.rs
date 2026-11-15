//! Composes the faucet plate from course groups of other slices: the base's staged foundation,
//! the native slice and the donor tip's courses, with the screw-seat rings.
//!
//! Each group keeps its own commands and the state they start from, and the travel between
//! groups lifts over the plastic already laid.

use crate::gcode;
use anyhow::{bail, ensure, Context, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, HashSet};
use std::fmt::Write;
use std::path::Path;

#[path = "foundation_sequence.rs"]
pub mod foundation_sequence;

pub const BASE: i64 = 1901;
pub const TIP: i64 = 1902;
pub const COVER: i64 = 1903;
pub const PLATE: i64 = 1904;
pub const LEVER: i64 = 1905;
const OBJECTS: [i64; 5] = [BASE, TIP, COVER, PLATE, LEVER];

const START: &str = "; MACHINE_START_GCODE_END";
const END: &str = "; MACHINE_END_GCODE_START";
const LAYER: &str = "; CHANGE_LAYER";
const HEIGHT: &str = "; Z_HEIGHT: ";
const PHASE: &str = "; HSM_PHASE: ";
const TIP_PHASE: &str = "; HSM_TIP_PHASE: ";
const TIP_COURSE: &str = "; HSM_TIP_COURSE: ";
const PLATE_RING: &str = "; HSM_PLATE_RING_Z: ";
const ENTRY: &str = "; HSM_ENTRY_XYZ: ";
const DEBT: &str = "; HSM_ENTRY_RETRACT_MM: ";
const NEXT_GROUP: &str = "; HSM_NEXT_GROUP: ";
const OBJECT: &str = "; start printing object, unique label id: ";
const STOP: &str = "; stop printing object, unique label id: ";
const END_LIFT: &str = "; HSM_PHASE_TRAVEL: final clearance lift";
const RING_PHASE: &str = "mounting plate counterbore supports";
const BED_LAYER: f64 = 0.2;
const PARKED: [f64; 3] = [290., -0.5, 6.2];
const BASELINE_Z_LIFT: f64 = 1.2;

fn name(obj: i64) -> Result<&'static str> {
    Ok(match obj {
        BASE => "base",
        TIP => "tip",
        COVER => "display cover",
        PLATE => "mounting plate",
        LEVER => "lever",
        _ => bail!("Unknown object {obj}"),
    })
}

fn mask(obj: i64) -> Result<&'static str> {
    Ok(match obj {
        BASE => "AQ",
        TIP => "Ag",
        COVER => "BA",
        PLATE => "CA",
        LEVER => "EA",
        _ => bail!("Unknown object {obj}"),
    })
}

/// A G-code file, read as lines that keep their newlines.
pub struct Tape {
    text: String,
}

impl Tape {
    pub fn read(path: &Path) -> Result<Tape> {
        Ok(Tape { text: std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))? })
    }

    pub fn lines(&self) -> Vec<&str> {
        self.text.split_inclusive('\n').collect()
    }
}

/// The number a line writes, white space aside.
fn number<T: std::str::FromStr>(text: &str) -> Result<T>
where
    T::Err: std::error::Error + Send + Sync + 'static,
{
    text.trim().parse().with_context(|| format!("{text:?} is not a number"))
}

fn word(words: &[(u8, f64)], key: u8) -> Option<f64> {
    words.iter().find(|(k, _)| *k == key).map(|(_, v)| *v)
}

/// The state a deposit starts from.
#[derive(Clone, Debug)]
pub struct Entry<'a> {
    pub xyz: [f64; 3],
    pub feed: f64,
    pub fan: f64,
    pub acceleration: f64,
    pub feature: &'a str,
    pub width: f64,
    pub height: f64,
}

type Deposit = ([f64; 3], [f64; 3], f64);

/// The retraction a deposit may start with unrecovered, as the written plastic rounds.
const RECOVERED: f64 = 1e-5;

/// The modal state commands leave, and the retraction a deposit must have recovered.
#[derive(Clone)]
struct Modal<'a> {
    xyz: [f64; 3],
    feed: f64,
    fan: f64,
    acceleration: f64,
    feature: &'a str,
    width: f64,
    height: f64,
    debt: f64,
}

impl<'a> Modal<'a> {
    fn new(xyz: [f64; 3], debt: f64) -> Modal<'a> {
        Modal { xyz, feed: 1800., fan: 0., acceleration: 10000., feature: "Custom", width: 0.42, height: 0.24, debt }
    }

    fn entry(&self, xyz: [f64; 3]) -> Entry<'a> {
        Entry { xyz, feed: self.feed, fan: self.fan, acceleration: self.acceleration, feature: self.feature,
                width: self.width, height: self.height }
    }

    /// Takes in one line: its feature, line width or layer height, the part fan, the
    /// acceleration, or a move. Returns the move when it lays plastic.
    fn apply(&mut self, line: &'a str) -> Result<Option<Deposit>> {
        if let Some(rest) = line.strip_prefix("; FEATURE: ") {
            self.feature = rest.trim();
        } else if let Some(rest) = line.strip_prefix("; LINE_WIDTH: ") {
            self.width = number(rest)?;
        } else if let Some(rest) = line.strip_prefix("; LAYER_HEIGHT: ") {
            self.height = number(rest)?;
        }
        let code = line.split(';').next().unwrap_or("").trim();
        let command = code.split_whitespace().next().unwrap_or("");
        let words = gcode::words(&code[command.len()..]);
        match command {
            "G0" | "G1" | "G2" | "G3" => return self.motion(&words, command, line),
            "M106" if word(&words, b'P').unwrap_or(1.0) == 1.0 => {
                self.fan = word(&words, b'S').with_context(|| format!("M106 without S: {line}"))?;
            }
            "M204" => self.acceleration = word(&words, b'S').unwrap_or(self.acceleration),
            _ => {}
        }
        Ok(None)
    }

    /// A move lays plastic when it extrudes along the bed: a line that changes X or Y, or an arc.
    fn motion(&mut self, w: &[(u8, f64)], command: &str, line: &str) -> Result<Option<Deposit>> {
        let start = self.xyz;
        let target = [word(w, b'X').unwrap_or(start[0]), word(w, b'Y').unwrap_or(start[1]), word(w, b'Z').unwrap_or(start[2])];
        self.xyz = target;
        self.feed = word(w, b'F').unwrap_or(self.feed);
        let e = word(w, b'E').unwrap_or(0.0);
        let along = start[0] != target[0] || start[1] != target[1] || matches!(command, "G2" | "G3");
        if e <= 0.0 || !along {
            self.debt = (self.debt - e).max(0.0);
            return Ok(None);
        }
        if self.debt > RECOVERED {
            bail!("Extrusion starts with {} mm retract debt at {start:?}: {line}", self.debt);
        }
        Ok(Some((start, target, e)))
    }
}

/// One course group: its commands in their tape and the state they start from.
#[derive(Clone, Debug)]
pub struct Band<'a> {
    pub tape: &'a [&'a str],
    pub label: String,
    pub phase: String,
    pub obj: i64,
    /// The group's height; a shaft group's level, which is a course number when `numbered`.
    pub z: f64,
    pub numbered: bool,
    pub line: usize,
    pub start: Option<usize>,
    pub end: usize,
    pub entry: Option<Entry<'a>>,
    pub exit: [f64; 3],
    pub lo: [f64; 3],
    pub hi: [f64; 3],
    /// The comment lines written after the phase: an index into the plate's metadata lists.
    pub metadata: usize,
    pub e: f64,
    pub roads: usize,
    /// The staged foundation's group kind.
    pub group: String,
}

impl<'a> Band<'a> {
    fn new(tape: &'a [&'a str], label: String, phase: String, obj: i64, z: f64, line: usize, metadata: usize) -> Band<'a> {
        Band { tape, label, phase, obj, z, numbered: false, line, start: None, end: 0, entry: None, exit: [0.; 3],
               lo: [f64::INFINITY; 3], hi: [f64::NEG_INFINITY; 3], metadata, e: 0., roads: 0,
               group: String::new() }
    }

    fn note(&mut self, index: usize, modal: &Modal<'a>, (start, target, e): Deposit) {
        if self.start.is_none() {
            self.start = Some(index);
            self.entry = Some(modal.entry(start));
        }
        self.end = index;
        self.exit = target;
        for axis in 0..3 {
            self.lo[axis] = self.lo[axis].min(start[axis]).min(target[axis]);
            self.hi[axis] = self.hi[axis].max(start[axis]).max(target[axis]);
        }
        self.e += e;
        self.roads += 1;
    }

    pub fn first_bed_course(&self) -> bool {
        (self.lo[2] - BED_LAYER).abs() < 0.0001 && (self.hi[2] - BED_LAYER).abs() < 0.0001
    }
}

/// The comment lines each group writes after its phase. Groups read from one course group of a
/// previous plate share a list.
#[derive(Default)]
pub struct Metadata {
    lists: Vec<Vec<String>>,
}

impl Metadata {
    pub fn new() -> Metadata {
        Metadata { lists: vec![Vec::new()] }
    }

    fn list(&mut self, lines: Vec<String>) -> usize {
        self.lists.push(lines);
        self.lists.len() - 1
    }
}

fn first_line(tape: &[&str], prefix: &str) -> Result<usize> {
    tape.iter().position(|l| l.starts_with(prefix)).with_context(|| format!("No line starts with {prefix:?}"))
}

/// The cover and native tip groups of a native slice, with their starting state.
pub fn read_native<'a>(tape: &'a [&'a str]) -> Result<Vec<Band<'a>>> {
    let first = first_line(tape, START)? + 1;
    let last = first_line(tape, END)?;
    let mut modal = Modal::new(PARKED, 0.);
    let mut bands: Vec<Band> = Vec::new();
    let mut band: Option<(i64, Option<usize>)> = None;
    let mut z = 0.;
    for i in first..last {
        let line = tape[i];
        if let Some(rest) = line.strip_prefix(HEIGHT) {
            z = number(rest)?;
        } else if let Some(rest) = line.strip_prefix(OBJECT) {
            let obj = number(rest)?;
            let phase = if obj == TIP { "native tip upper" } else { "native display cover" };
            let created = Band::new(tape, name(obj)?.to_string(), phase.to_string(), obj, z, i, 0);
            band = Some((obj, None));
            if obj == TIP || obj == COVER {
                bands.push(created);
                band = Some((obj, Some(bands.len() - 1)));
            }
        } else if line.starts_with(STOP) {
            band = None;
        }
        if let Some(deposit) = modal.apply(line)? {
            if let Some((_, Some(b))) = band {
                bands[b].note(i, &modal, deposit);
            }
        }
    }
    Ok(bands.into_iter().filter(|b| b.start.is_some()).collect())
}

/// Author-labeled tip courses or screw-seat ring courses, with their starting state.
pub fn read_custom<'a>(tape: &'a [&'a str], obj: i64, metadata: &mut Metadata) -> Result<Vec<Band<'a>>> {
    let mut modal = Modal::new([0.; 3], 0.8);
    let mut bands: Vec<Band> = Vec::new();
    let mut phase = String::new();
    for (i, &line) in tape.iter().enumerate() {
        if let Some(rest) = line.strip_prefix(TIP_PHASE) {
            phase = rest.trim().to_string();
        } else if let Some(rest) = line.strip_prefix(TIP_COURSE) {
            ensure!(!phase.is_empty(), "Tip course appears before its phase declaration");
            let list = metadata.list(vec![line.to_string()]);
            bands.push(Band::new(tape, format!("{phase} course {}", rest.trim()), phase.clone(), obj, 0., i, list));
        } else if let Some(rest) = line.strip_prefix(PLATE_RING) {
            let z: f64 = number(rest)?;
            phase = RING_PHASE.to_string();
            let list = metadata.list(vec![line.to_string()]);
            bands.push(Band::new(tape, format!("{phase} at Z{z}"), phase.clone(), obj, z, i, list));
        } else if let Some(rest) = line.strip_prefix(ENTRY) {
            let xyz: Vec<f64> = rest.split_whitespace().map(number).collect::<Result<_>>()?;
            ensure!(xyz.len() == 3, "An entry needs three coordinates: {line}");
            modal = Modal::new([xyz[0], xyz[1], xyz[2]], 0.8);
        } else if let Some(rest) = line.strip_prefix(DEBT) {
            modal.debt = number(rest)?;
        } else if let Some(band) = bands.last() {
            if band.start.is_none() && line.starts_with("; HSM_TIP_") {
                metadata.lists[band.metadata].push(line.to_string());
            }
        }
        if let Some(deposit) = modal.apply(line)? {
            let band = bands.last_mut().with_context(|| format!("Tip donor has unlabeled extrusion at {}", i + 1))?;
            band.note(i, &modal, deposit);
        }
    }
    for band in &mut bands {
        if obj == PLATE && (band.z - band.hi[2]).abs() > 1e-5 {
            bail!("Actual ring Z differs from declared Z in {}", band.label);
        }
        band.z = band.hi[2];
        ensure!(band.start.is_some(), "Empty tip band {}", band.label);
    }
    Ok(bands)
}

/// The previous plate's scheduling windows, with the replacement tip and cover in them and the
/// cover held under the tip's travel envelope.
pub fn interleave<'b, 'a>(reference: &'b [Band<'a>], tip: &'b [Band<'a>], cover: &'b [Band<'a>], rings: &'b [Band<'a>]) -> Result<Vec<&'b Band<'a>>> {
    let firsts = |bands: &'b [Band<'a>]| bands.iter().take_while(|b| b.first_bed_course()).count();
    let (tip_first, cover_first) = (firsts(tip), firsts(cover));
    for (obj, bands, first) in [(TIP, tip, tip_first), (COVER, cover, cover_first)] {
        let all = bands.iter().filter(|b| b.first_bed_course()).count();
        ensure!(first > 0 && first == all, "{} does not start with its whole first bed layer", name(obj)?);
    }
    let (tip_queue, cover_queue) = (&tip[tip_first..], &cover[cover_first..]);
    let mut tip_floor = vec![f64::INFINITY; tip_queue.len() + 1];
    for k in (0..tip_queue.len()).rev() {
        let lo = tip_queue[k].lo[2];
        tip_floor[k] = tip_floor[k + 1].min(lo);
    }
    let mut out: Vec<&Band> = Vec::new();
    let (mut i_tip, mut i_cover, mut ring) = (0, 0, 0);
    let (mut seen_tip, mut seen_cover) = (false, false);
    let (mut cursor_tip, mut cursor_cover) = (0.0f64, 0.0f64);
    let cover_limit = |cursor_cover: f64, i_tip: usize| (tip_floor[i_tip] + 0.6).max(BED_LAYER).min(cursor_cover);
    for band in reference {
        if band.obj != TIP && band.obj != COVER {
            if band.obj == PLATE {
                while ring < rings.len() && rings[ring].z <= band.z + 1e-4 {
                    out.push(&rings[ring]);
                    ring += 1;
                }
            }
            out.push(band);
            continue;
        }
        if band.obj == TIP && !seen_tip {
            seen_tip = true;
            out.extend(&tip[..tip_first]);
        }
        if band.obj == COVER && !seen_cover {
            seen_cover = true;
            out.extend(&cover[..cover_first]);
        }
        let cursor = if band.obj == TIP { &mut cursor_tip } else { &mut cursor_cover };
        *cursor = cursor.max(band.z);
        if band.first_bed_course() {
            continue;
        }
        if band.obj == COVER {
            let cap = cover_limit(cursor_cover, i_tip);
            while i_cover < cover_queue.len() && cover_queue[i_cover].z <= cap + 1e-4 {
                out.push(&cover_queue[i_cover]);
                i_cover += 1;
            }
            continue;
        }
        let cap = cursor_tip;
        while i_tip < tip_queue.len() && tip_queue[i_tip].z <= cap + 1e-4 {
            let cover_cap = cover_limit(cursor_cover, i_tip);
            while i_cover < cover_queue.len() && cover_queue[i_cover].z <= cover_cap + 1e-4 {
                out.push(&cover_queue[i_cover]);
                i_cover += 1;
            }
            out.push(&tip_queue[i_tip]);
            i_tip += 1;
        }
    }
    for (obj, queue, at, cursor) in [(TIP, tip_queue, i_tip, cursor_tip), (COVER, cover_queue, i_cover, cursor_cover)] {
        let pending = &queue[at..];
        if pending.is_empty() {
            continue;
        }
        if pending[0].z < cursor - 3. {
            bail!("Scheduling delays {} beneath the completed plate ({})", pending[0].label, name(obj)?);
        }
        out.extend(pending);
    }
    ensure!(ring == rings.len(), "Counterbore support is taller than all mounting-plate courses");
    Ok(out)
}

/// Each selected group exactly once.
fn each_once(schedule: &[&Band], wanted: Vec<*const Band>) -> Result<()> {
    let mut seen = HashSet::new();
    for band in schedule {
        ensure!(seen.insert(*band as *const Band), "The sequence must emit each selected band once");
    }
    ensure!(seen.len() == wanted.len() && wanted.iter().all(|b| seen.contains(b)), "The sequence must emit each selected band once");
    Ok(())
}

fn pointers<'x, 'a: 'x>(bands: impl IntoIterator<Item = &'x Band<'a>>) -> Vec<*const Band<'a>> {
    bands.into_iter().map(|b| b as *const Band).collect()
}

struct LevelBox<'a> {
    prefix: &'a str,
    values: [&'a str; 4],
    suffix: &'a str,
}

/// A startup line that levels the bed over a window: `G29 A1` or `A2` with its origin and size.
fn level_box(line: &str) -> Option<LevelBox<'_>> {
    let rest = line.trim_start().strip_prefix("G29 A")?;
    if !rest.starts_with('1') && !rest.starts_with('2') {
        return None;
    }
    let mut rest = rest[1..].strip_prefix(" O ")?;
    let prefix = &line[..line.len() - rest.len()];
    let mut values = [""; 4];
    for (n, key) in ["X", " Y", " I", " J"].into_iter().enumerate() {
        rest = rest.strip_prefix(key)?;
        let length = rest.bytes().take_while(|c| *c == b'-' || *c == b'.' || c.is_ascii_digit()).count();
        if length == 0 {
            return None;
        }
        values[n] = &rest[..length];
        rest = &rest[length..];
    }
    if !rest.strip_prefix(" R")?.trim().is_empty() {
        return None;
    }
    Some(LevelBox { prefix, values, suffix: rest })
}

/// The proven launch sequence, with its leveling window widened over the new first-bed
/// deposits.
pub fn leveling<'a>(startup: Vec<&'a str>, native: &[&str], schedule: &[&Band]) -> Result<(Vec<String>, [[f64; 2]; 2])> {
    let boxes: Vec<LevelBox> = startup.iter().chain(native.iter().take(2000)).filter_map(|l| level_box(l)).collect();
    ensure!(boxes.len() == 4, "Each complete stock startup must expose both bed leveling windows");
    let values: Vec<[f64; 4]> = boxes.iter().map(|b| -> Result<[f64; 4]> {
        Ok([number(b.values[0])?, number(b.values[1])?, number(b.values[2])?, number(b.values[3])?])
    }).collect::<Result<_>>()?;
    let mut origin = [f64::INFINITY; 2];
    let mut upper = [f64::NEG_INFINITY; 2];
    for axis in 0..2 {
        for v in &values {
            origin[axis] = origin[axis].min(v[axis]);
            upper[axis] = upper[axis].max(v[axis] + v[axis + 2]);
        }
    }
    for band in schedule {
        if !(band.obj == TIP || band.obj == COVER) || !band.first_bed_course() {
            continue;
        }
        for axis in 0..2 {
            origin[axis] = origin[axis].min(band.lo[axis]);
            upper[axis] = upper[axis].max(band.hi[axis]);
        }
    }
    let old = startup.iter().find_map(|l| level_box(l)).context("The startup has no leveling window")?;
    let bounds = [origin[0], origin[1], upper[0] - origin[0], upper[1] - origin[1]];
    let mut changed = false;
    for (a, b) in bounds.iter().zip(old.values) {
        changed |= (a - number::<f64>(b)?).abs() > 1e-4;
    }
    let startup = startup.into_iter().map(|line| match level_box(line) {
        Some(found) if changed => format!("{}X{:.5} Y{:.5} I{:.5} J{:.5}{}", found.prefix, bounds[0], bounds[1], bounds[2], bounds[3], found.suffix),
        _ => line.to_string(),
    }).collect();
    Ok((startup, [origin, upper]))
}

/// The plastic each object has laid so far.
pub type Terrain = Vec<(i64, [f64; 3], [f64; 3])>;

/// The highest deposit under the head's swept envelope from `old` to `entry`, if any.
fn terrain_top(old: [f64; 3], entry: [f64; 3], terrain: &Terrain) -> f64 {
    let xmin = old[0].min(entry[0]) - 30.;
    let xmax = old[0].max(entry[0]) + 66.5;
    let ymin = old[1].min(entry[1]) - 19.;
    let ymax = old[1].max(entry[1]) + 99.;
    let mut top = f64::NEG_INFINITY;
    for (_, lo, hi) in terrain {
        if lo[0] <= xmax && xmin <= hi[0] && lo[1] <= ymax && ymin <= hi[1] && hi[2] > top {
            top = hi[2];
        }
    }
    top
}

/// The highest deposit under the head's swept envelope from `old` to `entry`, no lower than
/// either end or `floor`.
fn clearance(old: [f64; 3], entry: [f64; 3], terrain: &Terrain, floor: f64) -> f64 {
    terrain_top(old, entry, terrain).max(floor).max(old[2]).max(entry[2])
}

/// The groups laid along a slope or on the stack that carries one: a transfer to or from one of
/// them keeps the slow, high lift over all laid plastic.
const TILTED: [&str; 6] = ["scaffold layer", "underside roof course", "underside deck bedding", "sloped course",
                           "tip shoulder entry", "tip yellow shoulder"];

fn tilted(band: &Band) -> bool {
    TILTED.contains(&band.phase.as_str())
}

/// The slicer's travel, z-hop and printer settings a native plate follows, read from the native
/// slice's own header, and the timelapse block that slice sends at each layer.
pub struct Native {
    pub z_hop: f64,
    pub travel_speed: f64,
    pub travel_acceleration: f64,
    pub max_speed_z: f64,
    pub nozzle_temperature: f64,
    camera: Vec<String>,
}

/// The slope of the slicer's spiral lift, as Bambu Studio's G-code writer winds it.
const SPIRAL_SLOPE_DEGREES: f64 = 3.0;

impl Native {
    pub fn read(tape: &[&str]) -> Result<Native> {
        let first = |key: &str| -> Result<f64> {
            let prefix = format!("; {key} = ");
            let line = tape.iter().find_map(|l| l.strip_prefix(prefix.as_str())).with_context(|| format!("The slice header has no {key}"))?;
            number(line.split(',').next().unwrap_or(""))
        };
        let all = OBJECTS.map(|o| o.to_string()).join(",");
        let opening = format!(" start: {all}");
        let start = tape.iter().position(|l| l.starts_with("; object ids of layer ") && l.trim_end().ends_with(&opening))
            .context("The native slice has no timelapse block over every object")?;
        let end = start + tape[start..].iter().position(|l| l.starts_with("; object ids of this layer"))
            .context("The native timelapse block does not close")?;
        ensure!(tape.get(end + 1).map(|l| l.trim()) == Some("M625"), "The native timelapse block does not end its object span");
        ensure!(!tape[start + 1..end].iter().any(|l| ["G0 ", "G1 ", "G2 ", "G3 "].iter().any(|p| l.trim_start().starts_with(p))),
                "The native timelapse block moves the head");
        Ok(Native {
            z_hop: first("z_hop")?,
            travel_speed: first("travel_speed")?,
            travel_acceleration: first("travel_acceleration")?,
            max_speed_z: first("machine_max_speed_z")?,
            nozzle_temperature: first("nozzle_temperature")?,
            camera: tape[start + 1..end].iter().map(|l| l.trim_end_matches(['\r', '\n']).to_string()).collect(),
        })
    }

    /// The commands the slicer sends as a layer begins: its progress, the layer-change notice
    /// and the timelapse frame.
    fn layer(&self, out: &mut String, layer: usize, total: usize) {
        let all = OBJECTS.map(|o| o.to_string()).join(",");
        let _ = writeln!(out, "; layer num/total_layer_count: {layer}/{total}\n; update layer progress\nM73 L{layer}");
        let _ = writeln!(out, "M991 S0 P{} ;notify layer change", layer - 1);
        let _ = writeln!(out, "; object ids of layer {layer} start: {all}");
        for line in &self.camera {
            let _ = writeln!(out, "{line}");
        }
        let _ = writeln!(out, "; object ids of this layer{layer} end: {all}\nM625");
    }

    /// What the slicer sends once the first layer is laid: power-loss recovery on, and the
    /// regular nozzle temperature without waiting for it.
    fn second_layer(&self, out: &mut String) {
        let _ = writeln!(out, "; open powerlost recovery\nM1003 S1\nM104 S{} ; set nozzle temperature", self.nozzle_temperature);
    }

    /// The spiral the slicer lifts by `rise` on before a travel from `from` to `to`: its centre's
    /// offset from `from`, beside the travel, and its radius.
    pub fn spiral(&self, from: [f64; 3], to: [f64; 3], rise: f64) -> ([f64; 2], f64) {
        let radius = rise / (std::f64::consts::TAU * SPIRAL_SLOPE_DEGREES.to_radians().atan());
        let (dx, dy) = (to[0] - from[0], to[1] - from[1]);
        let run = dx.hypot(dy);
        (if run > 1e-9 { [-dy / run * radius, dx / run * radius] } else { [radius, 0.] }, radius)
    }

    /// A travel from `from` to `to` that crosses at `height`: the slicer's spiral lift when it
    /// rises by no more than its z-hop and `spiral` allows it, else a straight lift at the
    /// machine's Z speed, then the crossing at the slicer's travel speed and the drop.
    pub fn travel(&self, out: &mut String, from: [f64; 3], to: [f64; 3], height: f64, spiral: bool) {
        let rise = height - from[2];
        let feed = self.travel_speed * 60.;
        let _ = writeln!(out, "M204 S{}", self.travel_acceleration);
        if spiral && rise > 1e-6 && rise <= self.z_hop + 1e-6 {
            let ([i, j], _) = self.spiral(from, to, rise);
            let _ = writeln!(out, "G17\nG3 Z{height:.3} I{i:.3} J{j:.3} P1 F{feed:.0}");
            let _ = writeln!(out, "G1 X{:.3} Y{:.3} Z{height:.3}", to[0], to[1]);
        } else {
            if rise > 1e-6 {
                let _ = writeln!(out, "G1 Z{height:.3} F{:.0}", self.max_speed_z * 60.);
            }
            let _ = writeln!(out, "G1 X{:.3} Y{:.3} F{feed:.0}", to[0], to[1]);
        }
        let _ = writeln!(out, "G1 Z{:.5} F{:.0}", to[2], self.max_speed_z * 60.);
    }
}

/// What a native plate's group sends ahead of its transfer: the layer it starts as the print
/// climbs, of how many, and whether it follows the whole first layer.
#[derive(Clone, Copy)]
struct Plan<'p> {
    profile: &'p Native,
    layer: Option<(usize, usize)>,
    second: bool,
}

/// How the transfers between a plate's course groups moved.
#[derive(Default)]
pub struct Handoffs {
    /// Transfers that move as the slicer's layer and object changes do.
    pub native: usize,
    /// Transfers that lift over all laid plastic, by why.
    pub lifted_tilted: usize,
    pub lifted_over_plastic: usize,
    pub lifted_first: usize,
    /// Level layers the printer hears of as the print climbs.
    pub layers: usize,
}

/// One group: the lift and travel to its entry, its labels, its starting state, then its own
/// commands without the native layer events. On a native plate a transfer between level groups
/// with nothing laid higher than its ends under the head moves as the slicer's layer changes do,
/// and a group that starts a level layer first sends that layer's printer commands.
#[allow(clippy::too_many_arguments)]
fn emit_band(out: &mut String, band: &Band, prev: Option<&Band>, old: [f64; 3], terrain: &Terrain, floor: f64, metadata: &Metadata,
             native: Option<Plan>, handoffs: &mut Handoffs) -> Result<[f64; 3]> {
    let entry = band.entry.as_ref().context("A group without deposits")?;
    let obj = band.obj;
    let _ = write!(out, "{LAYER}\n{HEIGHT}{:.5}\n", band.hi[2]);
    if let Some(plan) = &native {
        if let Some((layer, total)) = plan.layer {
            plan.profile.layer(out, layer, total);
        }
        if plan.second {
            plan.profile.second_layer(out);
        }
    }
    let level_ends = prev.is_some_and(|p| !tilted(p)) && !tilted(band);
    let top = terrain_top(old, entry.xyz, terrain);
    match native.map(|plan| plan.profile) {
        Some(profile) if level_ends && top <= old[2].max(entry.xyz[2]) + 1e-6 => {
            let _ = write!(out, "; HSM_PHASE_TRAVEL: level change between course groups\n{NEXT_GROUP}{}\n", band.label);
            let height = top.max(old[2]) + profile.z_hop;
            // nothing under the head stands higher than the group just laid, so the spiral
            // around its last bead stays over it, as the slicer's own does
            profile.travel(out, old, entry.xyz, height, true);
            handoffs.native += 1;
        }
        _ => {
            if native.is_some() {
                match prev {
                    None => handoffs.lifted_first += 1,
                    Some(_) if !level_ends => handoffs.lifted_tilted += 1,
                    Some(_) => handoffs.lifted_over_plastic += 1,
                }
            }
            let lift = (clearance(old, entry.xyz, terrain, floor) + 0.8).max(5.);
            ensure!(lift <= 315., "Lift exceeds the machine travel space: {lift}");
            let _ = write!(out, "; HSM_PHASE_TRAVEL: transfer between course groups\n{NEXT_GROUP}{}\n", band.label);
            let _ = write!(out, "G1 Z{lift:.3} F900\nG1 X{:.5} Y{:.5} F9000\nG1 Z{:.5} F900\n", entry.xyz[0], entry.xyz[1], entry.xyz[2]);
        }
    }
    let _ = writeln!(out, "{PHASE}{}", band.phase);
    for line in &metadata.lists[band.metadata] {
        out.push_str(line);
    }
    let _ = write!(out, "; OBJECT_ID: {obj}\n{OBJECT}{obj}\nM624 {}AAAAAAAAA=\n", mask(obj)?);
    let _ = write!(out, "M106 S{}\nM204 S{}\nG1 E.8 F1800\nG1 F{:.5}\n", entry.fan, entry.acceleration, entry.feed);
    let _ = write!(out, "; FEATURE: {}\n; LINE_WIDTH: {}\n; LAYER_HEIGHT: {}\n", entry.feature, entry.width, entry.height);
    let start = band.start.context("A group without deposits")?;
    let mut camera = false;
    for &line in &band.tape[start..=band.end] {
        if line.starts_with("; object ids of layer ") {
            ensure!(!camera, "Nested camera event in {}", band.label);
            camera = true;
            continue;
        }
        if camera {
            let command = line.trim_start();
            ensure!(!["G0 ", "G1 ", "G2 ", "G3 "].iter().any(|p| command.starts_with(p)), "Native camera callback contains a gantry move");
            if line.trim() == "M625" {
                camera = false;
            }
            continue;
        }
        if ["M73 ", "M991 ", "M1003 ", "M104 "].iter().any(|p| line.starts_with(p)) {
            continue;
        }
        let command = line.trim_start();
        ensure!(!["M624", "M625", "M622", "M623", "M971", "M1004"].iter().any(|p| command.starts_with(p)),
                "Unexpected nested object or camera command in {}: {line}", band.label);
        out.push_str(line);
    }
    ensure!(!camera, "Unterminated camera event in {}", band.label);
    let _ = write!(out, "G1 E-.8 F1800\n{STOP}{obj}\nM625\n");
    Ok(band.exit)
}

/// The level layer each group starts as the print climbs, counted from one: the plate's first
/// group starts the first, and a level group starts one when it lies above every group that
/// started one before it. Returns them with their count.
fn climbing_layers(schedule: &[&Band]) -> (Vec<Option<usize>>, usize) {
    let mut reached = f64::NEG_INFINITY;
    let mut count = 0;
    let starts = schedule.iter().enumerate().map(|(n, band)| {
        if n > 0 && (tilted(band) || band.hi[2] <= reached + 1e-4) {
            return None;
        }
        reached = band.hi[2];
        count += 1;
        Some(count)
    }).collect();
    (starts, count)
}

/// A plate: the startup, the groups in order with the regular temperature before `heat_at`, the
/// final lift and the footer carried up to it. A `native` plate sends the regular temperature
/// with its second level layer's commands instead, without waiting for it.
#[allow(clippy::too_many_arguments)]
fn write_plate(startup: &[String], schedule: &[&Band], heat_at: Option<usize>, footer: &[&str], floor: f64, metadata: &Metadata,
               native: Option<&Native>, allowed: impl Fn(f64) -> Result<()>) -> Result<(String, Terrain, Handoffs)> {
    let mut out = String::new();
    for line in startup {
        out.push_str(line);
    }
    let _ = write!(out, "M1003 S0\n{PHASE}whole-plate first layer\nG1 E-.8 F1800\n");
    let mut terrain: Terrain = Vec::new();
    let mut pos = PARKED;
    let mut handoffs = Handoffs::default();
    let (layers, total) = climbing_layers(schedule);
    if native.is_some() {
        ensure!(total >= 2, "A native plate climbs through fewer than two level layers");
        handoffs.layers = total;
    }
    let mut prev: Option<&Band> = None;
    for (n, band) in schedule.iter().enumerate() {
        if heat_at == Some(n) && native.is_none() {
            out.push_str("M109 S280 ; reach regular deposition temperature\n");
        }
        let plan = native.map(|profile| Plan { profile, layer: layers[n].map(|layer| (layer, total)), second: heat_at == Some(n) });
        pos = emit_band(&mut out, band, prev, pos, &terrain, floor, metadata, plan, &mut handoffs)?;
        prev = Some(band);
        match terrain.iter_mut().find(|(obj, _, _)| *obj == band.obj) {
            Some((_, lo, hi)) => {
                for axis in 0..3 {
                    if band.lo[axis] < lo[axis] {
                        lo[axis] = band.lo[axis];
                    }
                    if band.hi[axis] > hi[axis] {
                        hi[axis] = band.hi[axis];
                    }
                }
            }
            None => terrain.push((band.obj, band.lo, band.hi)),
        }
    }
    let top = terrain.iter().map(|(_, _, hi)| hi[2]).fold(floor, f64::max);
    allowed(top)?;
    let lifted = top + BASELINE_Z_LIFT;
    let _ = write!(out, "{END_LIFT}\nG1 Z{lifted:.3} F900\n");
    out.push_str("M1003 S0\nM106 S0\nM106 P2 S0\nM981 S0 P20000\n; FEATURE: Custom\n");
    for &line in footer {
        match footer_z(line) {
            Some((head, z, rest)) if number::<f64>(z)? < lifted => {
                let _ = writeln!(out, "{head}{lifted:.3}{rest}");
            }
            _ => out.push_str(line),
        }
    }
    Ok((out, terrain, handoffs))
}

/// A footer move to a height: `G0 Z` or `G1 Z`, the height, and the rest of the line.
fn footer_z(line: &str) -> Option<(&str, &str, &str)> {
    if !(line.starts_with("G0 Z") || line.starts_with("G1 Z")) {
        return None;
    }
    let body = line.strip_suffix('\n').unwrap_or(line);
    let length = body[4..].bytes().take_while(|c| *c == b'.' || c.is_ascii_digit()).count();
    if length == 0 || body[4 + length..].contains('\n') {
        return None;
    }
    Some((&body[..4], &body[4..4 + length], &body[4 + length..]))
}

/// A file's SHA-256.
/// A report written beside its plate.
fn write_report(output: &Path, report: &Value) -> Result<()> {
    std::fs::write(output.with_extension("json"), serde_json::to_string_pretty(report)? + "\n")?;
    Ok(())
}

/// The plate the schedule lays written to `output`, and its report: phases, filament, roads,
/// groups, bounds and the plate's hash, with the transfers and printer commands of a `native`
/// plate when it is one, and their counts.
pub fn emit_with(output: &Path, startup: &[String], schedule: &[&Band], footer: &[&str], metadata: &Metadata,
                 native: Option<&Native>) -> Result<Value> {
    let heat_at = schedule.iter().position(|b| !b.first_bed_course());
    if let Some(at) = heat_at {
        let first_bed: HashSet<i64> = schedule[..at].iter().map(|b| b.obj).collect();
        let missing: Vec<i64> = OBJECTS.iter().copied().filter(|o| !first_bed.contains(o)).collect();
        ensure!(missing.is_empty(), "First bed course is missing {missing:?}");
        if let Some(late) = schedule[at..].iter().find(|b| b.first_bed_course()) {
            bail!("Unexpected second start on the bed in {}", late.label);
        }
    }
    let allowed = |top: f64| -> Result<()> {
        ensure!(top + BASELINE_Z_LIFT < 247.24, "Print height conflicts with inherited finish motion: {top}");
        Ok(())
    };
    let (text, terrain, handoffs) = write_plate(startup, schedule, heat_at, footer, f64::NEG_INFINITY, metadata, native, allowed)?;
    std::fs::write(output, &text)?;
    let (mut counts, mut filament, mut roads) = (BTreeMap::<&str, usize>::new(), BTreeMap::<i64, f64>::new(), BTreeMap::<i64, usize>::new());
    let mut groups = Vec::new();
    for band in schedule {
        *counts.entry(band.phase.as_str()).or_default() += 1;
        *filament.entry(band.obj).or_default() += band.e;
        *roads.entry(band.obj).or_default() += band.roads;
        groups.push(json!([band.phase, band.label, band.obj, band.z, band.lo, band.hi, band.line + 1]));
    }
    let bounds: BTreeMap<i64, [[f64; 3]; 2]> = terrain.iter().map(|(obj, lo, hi)| (*obj, [*lo, *hi])).collect();
    let mut report = json!({
        "counts_by_phase": counts,
        "deposition_mm_filament": filament,
        "deposition_roads": roads,
        "groups": groups,
        "bounds_by_object_mm": bounds,
        "sequenced_gcode_sha256": crate::sha256_hex(text.as_bytes()),
    });
    if native.is_some() {
        report["transfers_between_groups"] = json!({
            "as_the_slicer_changes_layers": handoffs.native,
            "lifted_from_or_to_a_tilted_group": handoffs.lifted_tilted,
            "lifted_over_higher_plastic": handoffs.lifted_over_plastic,
            "lifted_from_the_start": handoffs.lifted_first,
        });
        report["printer_layers"] = json!(handoffs.layers);
    }
    Ok(report)
}

/// A report without its group rows, as the sequencers print it.
pub fn summary(report: &Value) -> Value {
    let mut summary = report.clone();
    if let Some(items) = summary.as_object_mut() {
        items.remove("groups");
    }
    summary
}

/// The course marker of a staged or donor course: its kind and its course number.
fn course(line: &str) -> Option<(&str, i64)> {
    const KINDS: [&str; 6] = ["scaffold layer", "sloped course", "transition course", "whole-base course",
                              "exterior scaffold layer", "underside roof course"];
    let rest = line.strip_prefix("; ")?;
    let kind = KINDS.into_iter().find(|k| rest.starts_with(k) && rest[k.len()..].starts_with(' '))?;
    let rest = &rest[kind.len() + 1..];
    let digits = rest.bytes().take_while(u8::is_ascii_digit).count();
    let after = rest[digits..].strip_prefix(" of ")?;
    if digits == 0 || !after.starts_with(|c: char| c.is_ascii_digit()) {
        return None;
    }
    Some((kind, rest[..digits].parse().ok()?))
}

fn part(obj: i64) -> &'static str {
    match obj {
        TIP => "tip",
        COVER => "display cover",
        PLATE => "mounting plate",
        LEVER => "lever",
        _ => "base",
    }
}

/// The phase a staged foundation group writes.
fn shaft_phase(band: &Band) -> String {
    match band.group.as_str() {
        "native" if band.obj == BASE => "inclined-base conventional handoff".into(),
        "native" => "native companions".into(),
        group => group.into(),
    }
}

/// The staged foundation: its startup, its authored scaffold and course groups, its native
/// object groups and its footer.
fn read_staged<'a>(tape: &'a [&'a str]) -> Result<(Vec<&'a str>, Vec<Band<'a>>, Vec<Band<'a>>, Vec<&'a str>)> {
    let startup = first_line(tape, START)?;
    let footer = first_line(tape, END)?;
    let first = startup + first_line(&tape[startup..footer], LAYER)?;
    let mut modal = Modal::new([0.; 3], 0.);
    let (mut authored, mut native): (Vec<Band>, Vec<Band>) = (Vec::new(), Vec::new());
    let mut seg: Option<(bool, usize)> = None;
    let mut group = "startup";
    let mut z = 0.20;
    for i in first..footer {
        let l = tape[i];
        if l.starts_with("; ===== sloped underside") {
            group = "scaffold";
            seg = None;
        } else if l.starts_with("; ===== end of the sloped underside") {
            group = "native";
            seg = None;
        } else if group == "native" && l.starts_with(LAYER) {
            seg = None;
        } else if group == "native" && l.starts_with(HEIGHT) {
            z = number(l.split(':').nth(1).unwrap_or(""))?;
        } else if group == "native" && l.starts_with(OBJECT) {
            let obj = number(l.split_whitespace().last().unwrap_or(""))?;
            let mut band = Band::new(tape, part(obj).into(), String::new(), obj, z, i, 0);
            band.group = "native".into();
            native.push(band);
            seg = Some((false, native.len() - 1));
        } else if group != "native" {
            let marker = l.get(2..).unwrap_or("").trim();
            let found = course(l);
            if found.is_some() || marker == "underside roof" || marker == "underside deck bedding" {
                let (kind, k) = match found {
                    Some(_) => (marker.rsplitn(4, ' ').last().unwrap_or(marker), found.unwrap().1),
                    None => (marker, 0),
                };
                let mut band = Band::new(tape, marker.into(), String::new(), BASE, k as f64, i, 0);
                band.numbered = true;
                band.group = kind.into();
                authored.push(band);
                seg = Some((true, authored.len() - 1));
            }
        }
        let deposit = modal.apply(l).with_context(|| format!("line {}", i + 1))?;
        if let Some(deposit) = deposit {
            match seg {
                Some((true, b)) => authored[b].note(i, &modal, deposit),
                Some((false, b)) => native[b].note(i, &modal, deposit),
                None => bail!("unowned deposition at {}: {l}", i + 1),
            }
        }
    }
    let keep = |bands: Vec<Band<'a>>| bands.into_iter().filter(|b| b.start.is_some()).collect::<Vec<_>>();
    Ok((tape[..first].to_vec(), keep(authored), keep(native), tape[footer..].to_vec()))
}

/// The staged foundation's order: the scaffold and native first courses, then each source in its
/// own order, with cadence limits on how far the companions get ahead.
fn interleave_shaft<'b, 'a>(authored: &'b [Band<'a>], native: &'b [Band<'a>]) -> Result<Vec<&'b Band<'a>>> {
    let first: Vec<&Band> = native.iter().filter(|s| s.z <= 0.201).collect();
    let objects: HashSet<i64> = first.iter().map(|s| s.obj).collect();
    ensure!(objects == HashSet::from([TIP, COVER, PLATE, LEVER]), "all four companions must have native first courses");
    let mut out: Vec<&Band> = vec![&authored[0]];
    out.extend(&first);
    let early: HashSet<*const Band> = first.iter().map(|s| *s as *const Band).collect();
    let back: Vec<&Band> = native.iter().filter(|s| (s.obj == TIP || s.obj == COVER) && !early.contains(&(*s as *const Band))).collect();
    let front: Vec<&Band> = native.iter().filter(|s| (s.obj == PLATE || s.obj == LEVER) && !early.contains(&(*s as *const Band))).collect();
    let pending: Vec<&Band> = native.iter().filter(|s| s.obj == BASE).collect();
    let (mut bi, mut fi) = (0, 0);
    let mut native_to = |out: &mut Vec<&'b Band<'a>>, back_limit: f64, front_limit: f64| {
        let mut elected = Vec::new();
        while bi < back.len() && back[bi].z <= back_limit {
            elected.push(back[bi]);
            bi += 1;
        }
        while fi < front.len() && front[fi].z <= front_limit {
            elected.push(front[fi]);
            fi += 1;
        }
        elected.sort_by_key(|s| s.start);
        out.extend(elected);
    };
    const CAPS: [(f64, f64, f64); 9] = [(5., 0.44, 0.44), (9., 0.92, 0.92), (14., 1.64, 1.64), (20., 2.36, 2.36), (28., 3.08, 3.08),
                                        (36., 3.56, 3.80), (43., 3.80, 4.76), (52., 4.04, 5.48), (61., 4.25, 6.20)];
    for s in &authored[1..] {
        if s.group == "scaffold layer" {
            if let Some(&(_, back_lim, front_lim)) = CAPS.iter().find(|c| c.0 == s.z) {
                native_to(&mut out, back_lim.min(3.56), front_lim.min(3.56));
            }
        }
        out.push(s);
    }
    let mut rest: Vec<&Band> = back[bi..].iter().chain(&front[fi..]).chain(&pending).copied().collect();
    rest.sort_by_key(|s| s.start);
    out.extend(rest);
    Ok(out)
}
