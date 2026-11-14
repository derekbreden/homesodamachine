//! Composes the Sculpted faucet's Mark2 trial plates from course groups of other plates.
//!
//! Each group keeps its own commands and the state they start from, and the travel between
//! groups lifts over the plastic already laid. The tip trial composes the previous plate's base,
//! mounting plate and lever with a native slice's cover, a custom tip and the screw-seat rings;
//! the plug-ramp trial composes a new tip with all of the previous plate's other groups; the
//! shaft trial composes a staged foundation slice with a continued-base donor.

use crate::python_text::{float, g, int, lstrip, max3, min3, read_text, repr, splitlines, strip, Json};
use anyhow::{bail, ensure, Context, Result};
use std::collections::HashSet;
use std::fmt::Write;
use std::path::{Path, PathBuf};

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
const TIP_BAND: &str = "; HSM_TIP_BAND_Z: ";
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

/// The word patterns each trial's Python reads commands with.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum Dialect {
    /// The tip trial: words after any spaces, from the line before its comment.
    Tip,
    /// The shaft trial: words straight after their letter, from the stripped command.
    Shaft,
}

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

/// A file's lines as the trials' Python reads them.
pub struct Tape {
    text: String,
}

impl Tape {
    pub fn read(path: &Path) -> Result<Tape> {
        Ok(Tape { text: read_text(path)? })
    }

    pub fn lines(&self) -> Vec<&str> {
        splitlines(&self.text)
    }
}

fn is_space(c: u8) -> bool {
    matches!(c, b' ' | b'\t' | b'\n' | b'\r' | b'\x0b' | b'\x0c' | b'\x1c'..=b'\x1f')
}

/// The number a word pattern takes: an optional minus, then digits with an optional point and
/// digits, or a point and digits.
fn number_length(text: &[u8]) -> Option<usize> {
    let mut at = usize::from(text.first() == Some(&b'-'));
    let digits = |from: usize| text[from..].iter().take_while(|c| c.is_ascii_digit()).count();
    let whole = digits(at);
    if whole > 0 {
        at += whole;
        if text.get(at) == Some(&b'.') {
            at += 1 + digits(at + 1);
        }
    } else if text.get(at) == Some(&b'.') && digits(at + 1) > 0 {
        at += 1 + digits(at + 1);
    } else {
        return None;
    }
    Some(at)
}

/// The words a trial's pattern finds in `code`, later ones replacing earlier.
fn words(code: &str, letters: &[u8], spaced: bool) -> Result<Vec<(u8, f64)>> {
    let bytes = code.as_bytes();
    let mut found: Vec<(u8, f64)> = Vec::new();
    let mut at = 0;
    while at < bytes.len() {
        if letters.contains(&bytes[at]) {
            let mut from = at + 1;
            if spaced {
                while from < bytes.len() && is_space(bytes[from]) {
                    from += 1;
                }
            }
            if let Some(length) = number_length(&bytes[from..]) {
                let value: f64 = code[from..from + length].parse()?;
                match found.iter_mut().find(|(k, _)| *k == bytes[at]) {
                    Some(slot) => slot.1 = value,
                    None => found.push((bytes[at], value)),
                }
                at = from + length;
                continue;
            }
        }
        at += 1;
    }
    Ok(found)
}

fn word(words: &[(u8, f64)], key: u8) -> Option<f64> {
    words.iter().find(|(k, _)| *k == key).map(|(_, v)| *v)
}

fn after_colon(line: &str) -> &str {
    line.split_once(':').map_or("", |(_, rest)| rest)
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

/// The modal state commands leave, and the retraction a deposit must have recovered.
#[derive(Clone)]
struct Modal<'a> {
    dialect: Dialect,
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
    fn new(dialect: Dialect, xyz: [f64; 3], debt: f64) -> Modal<'a> {
        Modal { dialect, xyz, feed: 1800., fan: 0., acceleration: 10000., feature: "Custom", width: 0.42, height: 0.24, debt }
    }

    fn entry(&self, xyz: [f64; 3]) -> Entry<'a> {
        Entry { xyz, feed: self.feed, fan: self.fan, acceleration: self.acceleration, feature: self.feature,
                width: self.width, height: self.height }
    }

    fn apply(&mut self, line: &'a str) -> Result<Option<Deposit>> {
        match self.dialect {
            Dialect::Tip => self.apply_tip(line),
            Dialect::Shaft => self.apply_shaft(line),
        }
    }

    fn apply_tip(&mut self, line: &'a str) -> Result<Option<Deposit>> {
        const LETTERS: &[u8] = b"XYZEFSIJP";
        let action = strip(line.split(' ').next().unwrap_or(""));
        let code = line.split(';').next().unwrap_or("");
        if matches!(action, "G0" | "G1" | "G2" | "G3") {
            return self.motion(&words(code, LETTERS, true)?, action, false, 1e-5, line);
        }
        if let Some(rest) = line.strip_prefix("; FEATURE: ") {
            self.feature = strip(rest);
        } else if line.starts_with("; LINE_WIDTH: ") {
            self.width = float(after_colon(line))?;
        } else if line.starts_with("; LAYER_HEIGHT: ") {
            self.height = float(after_colon(line))?;
        } else if action == "M106" {
            let w = words(code, LETTERS, true)?;
            if word(&w, b'P').unwrap_or(1.0) == 1.0 {
                self.fan = word(&w, b'S').with_context(|| format!("M106 without S: {line}"))?;
            }
        } else if action == "M204" && line.starts_with("M204 S") {
            self.acceleration = word(&words(code, LETTERS, true)?, b'S').with_context(|| format!("M204 without S: {line}"))?;
        }
        Ok(None)
    }

    fn apply_shaft(&mut self, text: &'a str) -> Result<Option<Deposit>> {
        const LETTERS: &[u8] = b"XYZEFIJS";
        if let Some(rest) = text.strip_prefix("; FEATURE: ") {
            self.feature = strip(rest);
        }
        if text.starts_with("; LINE_WIDTH: ") {
            self.width = float(after_colon(text))?;
        }
        if text.starts_with("; LAYER_HEIGHT: ") {
            self.height = float(after_colon(text))?;
        }
        let line = strip(text.split(';').next().unwrap_or(""));
        let action = line.split(' ').next().unwrap_or("");
        if action == "M106" {
            let w = words(line, b"PS", true)?;
            if word(&w, b'P').unwrap_or(1.0) == 1.0 {
                self.fan = word(&w, b'S').with_context(|| format!("M106 without S: {text}"))?;
            }
        }
        if action == "M204" && line.contains('S') {
            self.acceleration = word(&words(line, LETTERS, false)?, b'S').with_context(|| format!("M204 without S: {text}"))?;
        }
        if !matches!(action, "G0" | "G1" | "G2" | "G3") {
            return Ok(None);
        }
        self.motion(&words(line, LETTERS, false)?, action, true, 1e-6, text)
    }

    fn motion(&mut self, w: &[(u8, f64)], action: &str, still_is_travel: bool, limit: f64, line: &str) -> Result<Option<Deposit>> {
        let start = self.xyz;
        let target = [word(w, b'X').unwrap_or(start[0]), word(w, b'Y').unwrap_or(start[1]), word(w, b'Z').unwrap_or(start[2])];
        self.xyz = target;
        self.feed = word(w, b'F').unwrap_or(self.feed);
        let e = word(w, b'E').unwrap_or(0.0);
        let still = start[0] == target[0] && start[1] == target[1];
        if (still_is_travel && still && start[2] == target[2]) || e <= 0.0 || (still && matches!(action, "G0" | "G1")) {
            let debt = self.debt - e;
            self.debt = if debt > 0.0 { debt } else { 0.0 };
            return Ok(None);
        }
        if self.debt > limit {
            bail!("Extrusion starts with {} mm retract debt at {start:?}: {line}", g(self.debt));
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
    /// The shaft trial's group kind, donor phase and upper native height.
    pub group: String,
    pub source_phase: String,
    pub upper_native_z: Option<f64>,
}

impl<'a> Band<'a> {
    fn new(tape: &'a [&'a str], label: String, phase: String, obj: i64, z: f64, line: usize, metadata: usize) -> Band<'a> {
        Band { tape, label, phase, obj, z, numbered: false, line, start: None, end: 0, entry: None, exit: [0.; 3],
               lo: [f64::INFINITY; 3], hi: [f64::NEG_INFINITY; 3], metadata, e: 0., roads: 0,
               group: String::new(), source_phase: String::new(), upper_native_z: None }
    }

    fn note(&mut self, index: usize, modal: &Modal<'a>, (start, target, e): Deposit) {
        if self.start.is_none() {
            self.start = Some(index);
            self.entry = Some(modal.entry(start));
        }
        self.end = index;
        self.exit = target;
        for axis in 0..3 {
            self.lo[axis] = min3(self.lo[axis], start[axis], target[axis]);
            self.hi[axis] = max3(self.hi[axis], start[axis], target[axis]);
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

/// The startup before the previous plate's first layer, its groups with their phase and stream
/// order, and its footer.
pub fn read_reference<'a>(tape: &'a [&'a str], metadata: &mut Metadata) -> Result<(Vec<&'a str>, Vec<Band<'a>>, Vec<&'a str>)> {
    first_line(tape, START)?;
    let last = first_line(tape, END)?;
    let first = first_line(tape, LAYER)?;
    let start = first_line(&tape[..first], "M1003 S0")?;
    let mut modal = Modal::new(Dialect::Tip, PARKED, 0.8);
    let mut bands: Vec<Band> = Vec::new();
    let mut band: Option<usize> = None;
    let mut list = 0;
    let mut z = 0.;
    let (mut label, mut phase) = (String::new(), String::new());
    for i in first..last {
        let line = tape[i];
        if line.starts_with(END_LIFT) {
            break;
        }
        if line.starts_with(LAYER) {
            band = None;
            list = metadata.list(Vec::new());
            label.clear();
            phase.clear();
        } else if let Some(rest) = line.strip_prefix(HEIGHT) {
            z = float(rest)?;
        } else if let Some(rest) = line.strip_prefix(NEXT_GROUP) {
            label = strip(rest).to_string();
        } else if let Some(rest) = line.strip_prefix(PHASE) {
            phase = strip(rest).to_string();
        } else if let Some(rest) = line.strip_prefix(OBJECT) {
            let obj = int(rest)?;
            ensure!(!phase.is_empty() && !label.is_empty(), "Prior band lacks phase/label at {}", i + 1);
            bands.push(Band::new(tape, label.clone(), phase.clone(), obj, z, i, list));
            band = Some(bands.len() - 1);
        } else if line.starts_with(STOP) {
            band = None;
        } else if !phase.is_empty() && band.is_none() && line.starts_with("; ") && !line.starts_with("; OBJECT_ID: ") {
            metadata.lists[list].push(line.to_string());
        }
        if let Some(deposit) = modal.apply(line)? {
            let Some(b) = band else { bail!("Prior archive has unlabeled extrusion at {}", i + 1) };
            bands[b].note(i, &modal, deposit);
        }
    }
    ensure!(!bands.is_empty() && bands.iter().all(|b| b.start.is_some()), "Prior archive has an empty or missing object span");
    Ok((tape[..start].to_vec(), bands, tape[last..].to_vec()))
}

/// The cover and native tip groups of a native slice, with their starting state.
pub fn read_native<'a>(tape: &'a [&'a str]) -> Result<Vec<Band<'a>>> {
    let first = first_line(tape, START)? + 1;
    let last = first_line(tape, END)?;
    let mut modal = Modal::new(Dialect::Tip, PARKED, 0.);
    let mut bands: Vec<Band> = Vec::new();
    let mut band: Option<(i64, Option<usize>)> = None;
    let mut z = 0.;
    for i in first..last {
        let line = tape[i];
        if let Some(rest) = line.strip_prefix(HEIGHT) {
            z = float(rest)?;
        } else if let Some(rest) = line.strip_prefix(OBJECT) {
            let obj = int(rest)?;
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
    let mut modal = Modal::new(Dialect::Tip, [0.; 3], 0.8);
    let mut bands: Vec<Band> = Vec::new();
    let mut phase = String::new();
    for (i, &line) in tape.iter().enumerate() {
        if let Some(rest) = line.strip_prefix(TIP_PHASE) {
            phase = strip(rest).to_string();
        } else if let Some(rest) = line.strip_prefix(TIP_COURSE) {
            ensure!(!phase.is_empty(), "Tip course appears before its phase declaration");
            let list = metadata.list(vec![line.to_string()]);
            bands.push(Band::new(tape, format!("{phase} course {}", strip(rest)), phase.clone(), obj, 0., i, list));
        } else if let Some(rest) = line.strip_prefix(PLATE_RING) {
            let z = float(rest)?;
            phase = RING_PHASE.to_string();
            let list = metadata.list(vec![line.to_string()]);
            bands.push(Band::new(tape, format!("{phase} at Z{}", g(z)), phase.clone(), obj, z, i, list));
        } else if let Some(rest) = line.strip_prefix(ENTRY) {
            let xyz: Vec<f64> = rest.split_whitespace().map(float).collect::<Result<_>>()?;
            ensure!(xyz.len() == 3, "An entry needs three coordinates: {line}");
            modal = Modal::new(Dialect::Tip, [xyz[0], xyz[1], xyz[2]], 0.8);
        } else if let Some(rest) = line.strip_prefix(DEBT) {
            modal.debt = float(rest)?;
        } else if let Some(rest) = line.strip_prefix(TIP_BAND) {
            float(rest)?;
            let band = bands.last().context("A tip band height precedes every course")?;
            metadata.lists[band.metadata].push(line.to_string());
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
        tip_floor[k] = if tip_floor[k + 1] < lo { tip_floor[k + 1] } else { lo };
    }
    let mut out: Vec<&Band> = Vec::new();
    let (mut i_tip, mut i_cover, mut ring) = (0, 0, 0);
    let (mut seen_tip, mut seen_cover) = (false, false);
    let (mut cursor_tip, mut cursor_cover) = (0.0f64, 0.0f64);
    let cover_limit = |cursor_cover: f64, i_tip: usize| {
        let floor = tip_floor[i_tip] + 0.6;
        let level = if floor > BED_LAYER { floor } else { BED_LAYER };
        if level < cursor_cover { level } else { cursor_cover }
    };
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
        if band.z > *cursor {
            *cursor = band.z;
        }
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
    let lead = line.len() - line.trim_start_matches(|c: char| c.is_ascii() && is_space(c as u8)).len();
    let rest = line[lead..].strip_prefix("G29 A")?;
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
    let tail = rest.strip_prefix(" R")?;
    if !tail.bytes().all(is_space) {
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
        Ok([float(b.values[0])?, float(b.values[1])?, float(b.values[2])?, float(b.values[3])?])
    }).collect::<Result<_>>()?;
    let mut origin = [0.; 2];
    let mut upper = [0.; 2];
    for axis in 0..2 {
        origin[axis] = values.iter().map(|v| v[axis]).reduce(|a, b| if b < a { b } else { a }).unwrap();
        upper[axis] = values.iter().map(|v| v[axis] + v[axis + 2]).reduce(|a, b| if b > a { b } else { a }).unwrap();
    }
    for band in schedule {
        if !(band.obj == TIP || band.obj == COVER) || !band.first_bed_course() {
            continue;
        }
        for axis in 0..2 {
            if band.lo[axis] < origin[axis] {
                origin[axis] = band.lo[axis];
            }
            if band.hi[axis] > upper[axis] {
                upper[axis] = band.hi[axis];
            }
        }
    }
    let old = startup.iter().find_map(|l| level_box(l)).context("The startup has no leveling window")?;
    let bounds = [origin[0], origin[1], upper[0] - origin[0], upper[1] - origin[1]];
    let mut changed = false;
    for (a, b) in bounds.iter().zip(old.values) {
        changed |= (a - float(b)?).abs() > 1e-4;
    }
    let startup = startup.into_iter().map(|line| match level_box(line) {
        Some(found) if changed => format!("{}X{:.5} Y{:.5} I{:.5} J{:.5}{}", found.prefix, bounds[0], bounds[1], bounds[2], bounds[3], found.suffix),
        _ => line.to_string(),
    }).collect();
    Ok((startup, [origin, upper]))
}

/// The plastic each object has laid so far.
pub type Terrain = Vec<(i64, [f64; 3], [f64; 3])>;

/// The highest deposit under the head's swept envelope from `old` to `entry`, no lower than
/// either end or `floor`.
fn clearance(old: [f64; 3], entry: [f64; 3], terrain: &Terrain, floor: f64) -> f64 {
    let xmin = old[0].min(entry[0]) - 30.;
    let xmax = old[0].max(entry[0]) + 66.5;
    let ymin = old[1].min(entry[1]) - 19.;
    let ymax = old[1].max(entry[1]) + 99.;
    let mut top = floor;
    for (_, lo, hi) in terrain {
        if lo[0] <= xmax && xmin <= hi[0] && lo[1] <= ymax && ymin <= hi[1] && hi[2] > top {
            top = hi[2];
        }
    }
    max3(top, old[2], entry[2])
}

/// One group: the lift and travel to its entry, its labels, its starting state, then its own
/// commands without the native layer events.
fn emit_band(out: &mut String, band: &Band, old: [f64; 3], terrain: &Terrain, floor: f64, metadata: &Metadata) -> Result<[f64; 3]> {
    let entry = band.entry.as_ref().context("A group without deposits")?;
    let reach = clearance(old, entry.xyz, terrain, floor) + 0.8;
    let lift = if reach > 5. { reach } else { 5. };
    ensure!(lift <= 315., "Lift exceeds the machine travel space: {}", repr(lift));
    let obj = band.obj;
    let _ = write!(out, "{LAYER}\n{HEIGHT}{:.5}\n", band.hi[2]);
    let _ = write!(out, "; HSM_PHASE_TRAVEL: transfer between course groups\n{NEXT_GROUP}{}\n", band.label);
    let _ = write!(out, "G1 Z{lift:.3} F900\nG1 X{:.5} Y{:.5} F9000\nG1 Z{:.5} F900\n", entry.xyz[0], entry.xyz[1], entry.xyz[2]);
    let _ = writeln!(out, "{PHASE}{}", band.phase);
    for line in &metadata.lists[band.metadata] {
        out.push_str(line);
    }
    let _ = write!(out, "; OBJECT_ID: {obj}\n{OBJECT}{obj}\nM624 {}AAAAAAAAA=\n", mask(obj)?);
    let _ = write!(out, "M106 S{}\nM204 S{}\nG1 E.8 F1800\nG1 F{:.5}\n", g(entry.fan), g(entry.acceleration), entry.feed);
    let _ = write!(out, "; FEATURE: {}\n; LINE_WIDTH: {}\n; LAYER_HEIGHT: {}\n", entry.feature, g(entry.width), g(entry.height));
    let start = band.start.context("A group without deposits")?;
    let mut camera = false;
    for &line in &band.tape[start..=band.end] {
        if line.starts_with("; object ids of layer ") {
            ensure!(!camera, "Nested camera event in {}", band.label);
            camera = true;
            continue;
        }
        if camera {
            let command = lstrip(line);
            ensure!(!["G0 ", "G1 ", "G2 ", "G3 "].iter().any(|p| command.starts_with(p)), "Native camera callback contains a gantry move");
            if strip(line) == "M625" {
                camera = false;
            }
            continue;
        }
        if ["M73 ", "M991 ", "M1003 ", "M104 "].iter().any(|p| line.starts_with(p)) {
            continue;
        }
        let command = lstrip(line);
        ensure!(!["M624", "M625", "M622", "M623", "M971", "M1004"].iter().any(|p| command.starts_with(p)),
                "Unexpected nested object or camera command in {}: {line}", band.label);
        out.push_str(line);
    }
    ensure!(!camera, "Unterminated camera event in {}", band.label);
    let _ = write!(out, "G1 E-.8 F1800\n{STOP}{obj}\nM625\n");
    Ok(band.exit)
}

/// A plate: the startup, the groups in order with the regular temperature before `heat_at`, the
/// final lift and the footer carried up to it.
fn write_plate(startup: &[String], schedule: &[&Band], heat_at: Option<usize>, footer: &[&str], floor: f64, metadata: &Metadata,
               allowed: impl Fn(f64) -> Result<()>) -> Result<(String, Terrain)> {
    let mut out = String::new();
    for line in startup {
        out.push_str(line);
    }
    let _ = write!(out, "M1003 S0\n{PHASE}whole-plate first layer\nG1 E-.8 F1800\n");
    let mut terrain: Terrain = Vec::new();
    let mut pos = PARKED;
    for (n, band) in schedule.iter().enumerate() {
        if heat_at == Some(n) {
            out.push_str("M109 S280 ; reach regular deposition temperature\n");
        }
        pos = emit_band(&mut out, band, pos, &terrain, floor, metadata)?;
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
    let top = terrain.iter().map(|(_, _, hi)| hi[2]).fold(floor, |a, b| if b > a { b } else { a });
    allowed(top)?;
    let lifted = top + BASELINE_Z_LIFT;
    let _ = write!(out, "{END_LIFT}\nG1 Z{lifted:.3} F900\n");
    out.push_str("M1003 S0\nM106 S0\nM106 P2 S0\nM981 S0 P20000\n; FEATURE: Custom\n");
    for &line in footer {
        match footer_z(line) {
            Some((head, z, rest)) if float_below(z, lifted)? => {
                let _ = writeln!(out, "{head}{lifted:.3}{rest}");
            }
            _ => out.push_str(line),
        }
    }
    Ok((out, terrain))
}

fn float_below(text: &str, limit: f64) -> Result<bool> {
    Ok(float(text)? < limit)
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

/// Adds `amount` to the row for `key`, the rows kept in the order their keys first appear.
fn add<K: PartialEq, T: std::ops::AddAssign + Default>(rows: &mut Vec<(K, T)>, key: K, amount: T) {
    match rows.iter_mut().find(|(k, _)| *k == key) {
        Some((_, total)) => *total += amount,
        None => {
            let mut total = T::default();
            total += amount;
            rows.push((key, total));
        }
    }
}

fn point(xyz: &[f64]) -> Json {
    Json::List(xyz.iter().map(|v| Json::Float(*v)).collect())
}

fn keyed<T>(rows: Vec<(i64, T)>, value: impl Fn(T) -> Json) -> Json {
    Json::Dict(rows.into_iter().map(|(k, v)| (k.to_string(), value(v))).collect())
}

/// The tip trial's plate from the previous plate, a native slice for the cover, the custom tip
/// and the screw-seat rings, written to `output` with its report beside it.
pub fn compose_tip(reference: &Path, native: &Path, output: &Path, tip_model: &Path, plate_rings: Option<&Path>) -> Result<Json> {
    let reference_tape = Tape::read(reference)?;
    let native_tape = Tape::read(native)?;
    let tip_tape = Tape::read(tip_model)?;
    let ring_tape = plate_rings.map(Tape::read).transpose()?;
    let reference_lines = reference_tape.lines();
    let native_lines = native_tape.lines();
    let tip_lines = tip_tape.lines();
    let ring_lines = ring_tape.as_ref().map(Tape::lines).unwrap_or_default();
    let mut metadata = Metadata::new();
    let (startup, reference_bands, footer) = read_reference(&reference_lines, &mut metadata)?;
    let cover: Vec<Band> = read_native(&native_lines)?.into_iter().filter(|b| b.obj == COVER).collect();
    let tip = read_custom(&tip_lines, TIP, &mut metadata)?;
    let rings = if plate_rings.is_some() { read_custom(&ring_lines, PLATE, &mut metadata)? } else { Vec::new() };
    ensure!(rings.windows(2).all(|w| w[0].z < w[1].z), "Counterbore support courses must follow increasing Z");
    let schedule = interleave(&reference_bands, &tip, &cover, &rings)?;
    let retained = reference_bands.iter().filter(|b| b.obj != TIP && b.obj != COVER);
    each_once(&schedule, pointers(tip.iter().chain(&cover).chain(&rings).chain(retained)))?;
    let (startup, window) = leveling(startup, &native_lines, &schedule)?;
    let mut result = emit(output, &startup, &schedule, &footer, &metadata)?;
    let mut sources = vec![("reference".to_string(), Json::Str(crate::sha256_hex(&std::fs::read(reference)?))),
                           ("native".to_string(), Json::Str(crate::sha256_hex(&std::fs::read(native)?))),
                           ("tip_model".to_string(), Json::Str(crate::sha256_hex(&std::fs::read(tip_model)?)))];
    if let Some(rings) = plate_rings {
        sources.push(("plate_rings".to_string(), Json::Str(crate::sha256_hex(&std::fs::read(rings)?))));
    }
    result.set("source_gcode_sha256", Json::Dict(sources));
    result.set("first_native_tip_z_mm", Json::Null);
    result.set("stock_leveling_window_xy_mm", Json::List(window.iter().map(|p| point(p)).collect()));
    std::fs::write(output.with_extension("json"), result.dumps_indented() + "\n")?;
    Ok(result)
}

/// The tip trial's plate written to `output`, and its report: phases, filament, roads, groups,
/// bounds and the plate's hash.
pub fn emit(output: &Path, startup: &[String], schedule: &[&Band], footer: &[&str], metadata: &Metadata) -> Result<Json> {
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
        ensure!(top + BASELINE_Z_LIFT < 247.24, "Print height conflicts with inherited finish motion: {}", repr(top));
        Ok(())
    };
    let (text, terrain) = write_plate(startup, schedule, heat_at, footer, f64::NEG_INFINITY, metadata, allowed)?;
    std::fs::write(output, &text)?;
    let (mut counts, mut filament, mut roads) = (Vec::new(), Vec::new(), Vec::new());
    let mut groups = Vec::new();
    for band in schedule {
        add(&mut counts, band.phase.clone(), 1i64);
        add(&mut filament, band.obj, band.e);
        add(&mut roads, band.obj, band.roads as i64);
        groups.push(Json::List(vec![Json::Str(band.phase.clone()), Json::Str(band.label.clone()), Json::Int(band.obj),
                                    Json::Float(band.z), point(&band.lo), point(&band.hi), Json::Int(band.line as i64 + 1)]));
    }
    let bounds: Vec<(i64, Json)> = terrain.iter().map(|(obj, lo, hi)| (*obj, Json::List(vec![point(lo), point(hi)]))).collect();
    Ok(Json::Dict(vec![
        ("counts_by_phase".into(), Json::Dict(counts.into_iter().map(|(k, v)| (k, Json::Int(v))).collect())),
        ("deposition_mm_filament".into(), keyed(filament, Json::Float)),
        ("deposition_roads".into(), keyed(roads, Json::Int)),
        ("groups".into(), Json::List(groups)),
        ("bounds_by_object_mm".into(), keyed(bounds, |v| v)),
        ("sequenced_gcode_sha256".into(), Json::Str(crate::sha256_hex(text.as_bytes()))),
    ]))
}

/// What a trial pins its previous plate to, and the sequencer provenance its plates' reports
/// carry; each is checked or recorded only when the trial names it.
#[derive(Default)]
pub struct MergePins {
    /// The previous plate's G-code, by SHA-256.
    pub reference_sha256: Option<String>,
    /// How many screw-seat ring groups the previous plate carries.
    pub rings: Option<usize>,
    /// The sequencer recipe the trial's archive names.
    pub sequencer_sha256: Option<String>,
}

/// Each plug-ramp alternative: its tip tape composed against the previous plate's other parts,
/// written to its plate path with its report beside it. Each plate's summary is returned.
pub fn merge(reference: &Path, candidates: &[(PathBuf, PathBuf)], pins: &MergePins) -> Result<Vec<Json>> {
    let reference_sha = crate::sha256_hex(&std::fs::read(reference)?);
    if let Some(expected) = &pins.reference_sha256 {
        ensure!(reference_sha == *expected, "The previous plate is not the one the trial names");
    }
    let reference_tape = Tape::read(reference)?;
    let reference_lines = reference_tape.lines();
    let mut metadata = Metadata::new();
    let (startup, reference_bands, footer) = read_reference(&reference_lines, &mut metadata)?;
    let cover: Vec<Band> = reference_bands.iter().filter(|b| b.obj == COVER).cloned().collect();
    let retained: Vec<&Band> = reference_bands.iter().filter(|b| b.obj != TIP && b.obj != COVER).collect();
    let ring_count = retained.iter().filter(|b| b.phase == RING_PHASE).count();
    ensure!(!cover.is_empty() && pins.rings.is_none_or(|n| ring_count == n), "The previous plate is missing its cover or ring groups");
    let mut summaries = Vec::new();
    for (tip_path, output) in candidates {
        let tip_sha = crate::sha256_hex(&std::fs::read(tip_path)?);
        let declared = Json::loads(&std::fs::read_to_string(tip_path.with_extension("json"))?)?;
        ensure!(declared.get("tip_tape_sha256") == Some(&Json::Str(tip_sha.clone())),
                "The mapped tip tape and its receipt differ: {}", tip_path.display());
        let tip_tape = Tape::read(tip_path)?;
        let tip_lines = tip_tape.lines();
        let tip = read_custom(&tip_lines, TIP, &mut metadata)?;
        let schedule = interleave(&reference_bands, &tip, &cover, &[])?;
        each_once(&schedule, pointers(tip.iter().chain(&cover).chain(retained.iter().copied())))?;
        let (startup_window, window) = leveling(startup.clone(), &reference_lines, &schedule)?;
        let mut result = emit(output, &startup_window, &schedule, &footer, &metadata)?;
        result.set("source_gcode_sha256", Json::Dict(vec![
            ("reference_for_all_non_tip_parts".into(), Json::Str(reference_sha.clone())),
            ("tip_model".into(), Json::Str(tip_sha.clone())),
        ]));
        result.set("stock_leveling_window_xy_mm", Json::List(window.iter().map(|p| point(p)).collect()));
        result.set("retained_ring_count", Json::Int(ring_count as i64));
        if let Some(sequencer) = &pins.sequencer_sha256 {
            result.set("archived_sequencer_sha256", Json::Str(sequencer.clone()));
        }
        std::fs::write(output.with_extension("json"), result.dumps_indented() + "\n")?;
        let groups = match result.get("groups") {
            Some(Json::List(rows)) => rows.len(),
            _ => 0,
        };
        summaries.push(Json::Dict(vec![
            ("plate".into(), Json::Str(output.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default())),
            ("groups".into(), Json::Int(groups as i64)),
            ("plate_sha256".into(), result.get("sequenced_gcode_sha256").cloned().unwrap_or(Json::Null)),
            ("tip_sha256".into(), Json::Str(tip_sha)),
            ("counts_by_phase".into(), result.get("counts_by_phase").cloned().unwrap_or(Json::Null)),
        ]));
    }
    Ok(summaries)
}

/// A report without its group rows, as the sequencers print it.
pub fn summary(report: &Json) -> Json {
    match report {
        Json::Dict(items) => Json::Dict(items.iter().filter(|(k, _)| k != "groups").cloned().collect()),
        other => other.clone(),
    }
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

/// The phase a shaft-trial group writes.
fn shaft_phase(band: &Band) -> String {
    match band.group.as_str() {
        "native" if band.obj == BASE => "inclined-base conventional handoff".into(),
        "native" => "native companions".into(),
        "whole base" => band.source_phase.clone(),
        group => group.into(),
    }
}

/// The staged foundation: its startup, its authored scaffold and course groups, its native
/// object groups and its footer.
fn read_staged<'a>(tape: &'a [&'a str]) -> Result<(Vec<&'a str>, Vec<Band<'a>>, Vec<Band<'a>>, Vec<&'a str>)> {
    let startup = first_line(tape, START)?;
    let footer = first_line(tape, END)?;
    let first = startup + first_line(&tape[startup..footer], LAYER)?;
    let mut modal = Modal::new(Dialect::Shaft, [0.; 3], 0.);
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
            z = float(l.split(':').nth(1).unwrap_or(""))?;
        } else if group == "native" && l.starts_with(OBJECT) {
            let obj = int(l.split_whitespace().last().unwrap_or(""))?;
            let mut band = Band::new(tape, part(obj).into(), String::new(), obj, z, i, 0);
            band.group = "native".into();
            native.push(band);
            seg = Some((false, native.len() - 1));
        } else if group != "native" {
            let marker = strip(l.get(2..).unwrap_or(""));
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

/// The continued base's courses, each with its donor phase and level.
fn read_donor<'a>(tape: &'a [&'a str]) -> Result<Vec<Band<'a>>> {
    let mut modal = Modal::new(Dialect::Shaft, [0.; 3], 0.8);
    let mut spans: Vec<Band> = Vec::new();
    let mut phase = "native base along the mounting incline".to_string();
    let mut upper_native_z = None;
    for (i, &l) in tape.iter().enumerate() {
        if l.starts_with("; HSM_DONOR_PHASE: ") {
            phase = strip(after_colon(l)).into();
            upper_native_z = None;
        }
        if l.starts_with("; HSM_UPPER_NATIVE_Z: ") {
            upper_native_z = Some(float(after_colon(l))?);
        }
        if course(l).is_some() {
            let mut band = Band::new(tape, strip(&l[2..]).into(), String::new(), BASE, 0.0, i, 0);
            band.group = "whole base".into();
            band.source_phase = phase.clone();
            band.upper_native_z = upper_native_z;
            spans.push(band);
        }
        if l.starts_with("; HSM_NORMAL_Z: ") {
            let band = spans.last_mut().context("A normal height precedes every donor course")?;
            band.z = float(l.split(':').nth(1).unwrap_or(""))?;
        }
        if let Some(rest) = l.strip_prefix("; HSM_ENTRY_XYZ: ") {
            let xyz: Vec<f64> = rest.split_whitespace().map(float).collect::<Result<_>>()?;
            ensure!(xyz.len() == 3, "An entry needs three coordinates: {l}");
            modal = Modal::new(Dialect::Shaft, [xyz[0], xyz[1], xyz[2]], 0.8);
        }
        if let Some(rest) = l.strip_prefix("; HSM_ENTRY_RETRACT_MM: ") {
            modal.debt = float(rest)?;
        }
        if let Some(deposit) = modal.apply(l)? {
            spans.last_mut().context("Donor deposition before its first course")?.note(i, &modal, deposit);
        }
    }
    Ok(spans.into_iter().filter(|b| b.start.is_some()).collect())
}

/// The shaft trial's order: the scaffold and native first courses, then each source in its own
/// order, with cadence limits on how far the companions get ahead.
fn interleave_shaft<'b, 'a>(authored: &'b [Band<'a>], native: &'b [Band<'a>], donor: &'b [Band<'a>]) -> Result<Vec<&'b Band<'a>>> {
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
    let has_donor = !donor.is_empty();
    for s in &authored[1..] {
        if s.group == "scaffold layer" {
            if let Some(&(_, back_lim, front_lim)) = CAPS.iter().find(|c| c.0 == s.z) {
                if has_donor {
                    native_to(&mut out, back_lim, front_lim);
                } else {
                    native_to(&mut out, back_lim.min(3.56), front_lim.min(3.56));
                }
            }
        }
        if has_donor && s.group.starts_with("underside roof") {
            let raised = if s.z - 1. > 0. { s.z - 1. } else { 0. };
            native_to(&mut out, 4.25 + 0.24 * raised, 6.44 + 0.48 * s.z);
        }
        if has_donor && s.group == "sloped course" {
            native_to(&mut out, 4.73 + 0.24 * (s.z - 1.), 7.88 + 0.35 * (s.z - 1.));
        }
        out.push(s);
    }
    if !has_donor {
        let mut rest: Vec<&Band> = back[bi..].iter().chain(&front[fi..]).chain(&pending).copied().collect();
        rest.sort_by_key(|s| s.start);
        out.extend(rest);
        return Ok(out);
    }
    for (i, s) in donor.iter().enumerate() {
        if i % 7 == 0 {
            let reach = s.lo[2] + 1.0;
            native_to(&mut out, if reach > 8.0 { reach } else { 8.0 }, if reach > 12.20 { reach } else { 12.20 });
        }
        out.push(s);
    }
    let mut rest: Vec<&Band> = back[bi..].iter().chain(&front[fi..]).copied().collect();
    rest.sort_by_key(|s| s.start);
    out.extend(rest);
    Ok(out)
}

/// The shaft trial's plate from the staged foundation slice and the continued-base donor,
/// written to `output` with its report beside it.
pub fn compose_shaft(source: &Path, output: &Path, donor: Option<&Path>) -> Result<Json> {
    let source_tape = Tape::read(source)?;
    let donor_tape = donor.map(Tape::read).transpose()?;
    let source_lines = source_tape.lines();
    let donor_lines = donor_tape.as_ref().map(Tape::lines).unwrap_or_default();
    let (startup, authored, native, footer) = read_staged(&source_lines)?;
    let donor_bands = if donor.is_some() { read_donor(&donor_lines)? } else { Vec::new() };
    let native: Vec<Band> = if donor_bands.is_empty() { native } else { native.into_iter().filter(|s| s.obj != BASE).collect() };
    ensure!(authored.first().is_some_and(|s| s.group == "scaffold layer"), "the authored stream needs a marked first scaffold layer");
    let schedule = interleave_shaft(&authored, &native, &donor_bands)?;
    each_once(&schedule, pointers(authored.iter().chain(&native).chain(&donor_bands)))?;
    let mut metadata = Metadata::new();
    let mut front: Vec<(i64, f64)> = Vec::new();
    let mut heat_at = None;
    let mut labelled: Vec<Band> = Vec::with_capacity(schedule.len());
    for (n, span) in schedule.iter().enumerate() {
        if heat_at.is_none() && (span.group == "scaffold layer" || span.group == "exterior scaffold layer") && span.z > 1. {
            heat_at = Some(n);
        }
        if span.group == "native" {
            let reached = front.iter().find(|(obj, _)| *obj == span.obj).map_or(0., |(_, z)| *z);
            ensure!(span.z >= reached, "native object course order reversed");
            match front.iter_mut().find(|(obj, _)| *obj == span.obj) {
                Some(slot) => slot.1 = span.z,
                None => front.push((span.obj, span.z)),
            }
        }
        let mut lines = Vec::new();
        if span.group != "native" {
            lines.push(format!("; {}\n", span.label));
        }
        if span.group == "whole base" {
            lines.push(format!("; HSM_DONOR_PHASE: {}\n", span.source_phase));
            lines.push(match span.upper_native_z {
                Some(z) => format!("; HSM_UPPER_NATIVE_Z: {z:.5}\n"),
                None => format!("; HSM_NORMAL_Z: {:.5}\n", span.z),
            });
        }
        let mut band = (*span).clone();
        band.phase = shaft_phase(span);
        band.metadata = metadata.list(lines);
        labelled.push(band);
    }
    let ordered: Vec<&Band> = labelled.iter().collect();
    let startup: Vec<String> = startup.iter().map(|l| l.to_string()).collect();
    let allowed = |top: f64| -> Result<()> {
        ensure!(top + 0.4 <= 245.640001, "the actual print rise requires revisiting the native finish positions");
        Ok(())
    };
    let (text, _) = write_plate(&startup, &ordered, heat_at, &footer, 0.0, &metadata, allowed)?;
    std::fs::write(output, &text)?;
    let (mut counts, mut filament) = (Vec::new(), Vec::new());
    let mut groups = Vec::new();
    for band in &labelled {
        add(&mut counts, band.phase.clone(), 1i64);
        add(&mut filament, band.obj, band.e);
        let level = if band.numbered { Json::Int(band.z as i64) } else { Json::Float(band.z) };
        groups.push(Json::List(vec![Json::Str(band.phase.clone()), Json::Str(band.label.clone()), Json::Int(band.obj), level,
                                    point(&band.lo), point(&band.hi)]));
    }
    let mut result = Json::Dict(vec![
        ("groups".into(), Json::List(groups)),
        ("counts_by_phase".into(), Json::Dict(counts.into_iter().map(|(k, v)| (k, Json::Int(v))).collect())),
        ("deposition_mm_filament".into(), keyed(filament, Json::Float)),
        ("source_gcode_sha256".into(), Json::Str(crate::sha256_hex(&std::fs::read(source)?))),
    ]);
    if let Some(donor) = donor {
        result.set("inclined_donor_sha256", Json::Str(crate::sha256_hex(&std::fs::read(donor)?)));
    }
    result.set("sequenced_gcode_sha256", Json::Str(crate::sha256_hex(text.as_bytes())));
    std::fs::write(output.with_extension("json"), result.dumps_indented() + "\n")?;
    Ok(result)
}
