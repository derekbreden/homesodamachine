//! The reed sweep rig's log reader runs a sweep through the rig's controller and turns the
//! controller's lines into the places each reed closes and opens along the tube.
use crate::{flag, option, read_json, serials, sha, validate_args, write_json, x1};
use anyhow::{Context, Result, bail, ensure};
use serde_json::{Value, json};
use std::{
    collections::BTreeMap,
    fs::{self, OpenOptions},
    io::Write,
    path::{Path, PathBuf},
    thread,
    time::{Duration, Instant},
};

const DATUMS: &str = "hardware/printed-parts/fixtures/reed-sweep-rig/reed-sweep-rig-datums.json";
const USAGE: &str = "reed-sweep (--port PORT | --replay RAW_LOG) --output NEW_DIRECTORY --sled near|nominal|far [--reeds 1=NAME,2=NAME] [--from MM] [--to MM] [--speed MM_PER_S] [--cycles N] [--play MM] [--glass MM] [--merge MM] [--label TEXT] | reed-sweep --list";

/// How far the sweep's near end stands past the sled's home.
const NEAR_END_PAST_HOME_MM: f64 = 1.0;
const DEFAULT_SPEED_MM_PER_S: f64 = 2.0;
const DEFAULT_CYCLES: u32 = 3;
/// Reed changes closer together than this along the tube are one reed's chatter at one crossing.
const DEFAULT_MERGE_MM: f64 = 0.3;

// --- What the controller says -------------------------------------------------------------

/// The controller's own account of itself, from its `I` line.
#[derive(Debug, Clone, PartialEq)]
struct Info {
    steps_per_mm: f64,
    tab_steps: f64,
    deepest_steps: f64,
    fields: BTreeMap<String, String>,
}

/// A reed opened or closed with the sled at a step.
#[derive(Debug, Clone, Copy, PartialEq)]
struct Change {
    station: usize,
    closed: bool,
    step: i64,
}

/// One read leg of a sweep: where it began and ended, what every reed read at each end, and the
/// changes between.
#[derive(Debug, Clone, PartialEq)]
struct Leg {
    number: u32,
    rising: bool,
    start_step: i64,
    start_reeds: Vec<bool>,
    changes: Vec<Change>,
    end: Option<(i64, Vec<bool>)>,
}

#[derive(Debug, Default)]
struct Log {
    info: Option<Info>,
    legs: Vec<Leg>,
    /// The line the sweep ended in, `OK ...` or `ERR ...`.
    ending: Option<String>,
    faults: Vec<String>,
}

fn reeds(text: &str) -> Result<Vec<bool>> {
    text.chars()
        .map(|c| match c {
            '1' => Ok(true),
            '0' => Ok(false),
            _ => bail!("a reed reads 0 or 1, not {c:?}"),
        })
        .collect()
}

fn info(line: &str) -> Result<Info> {
    let fields: BTreeMap<String, String> = line
        .split(',')
        .skip(1)
        .filter_map(|field| field.split_once('='))
        .map(|(key, value)| (key.to_owned(), value.to_owned()))
        .collect();
    let number = |key: &str| -> Result<f64> {
        fields
            .get(key)
            .with_context(|| format!("the controller's line names no {key}"))?
            .parse::<f64>()
            .with_context(|| format!("the controller's {key} is not a number"))
    };
    ensure!(
        fields.get("rig").map(String::as_str) == Some("reed-sweep"),
        "the board on this port is not the reed sweep rig's controller"
    );
    let (steps_per_mm, tab_steps, deepest_steps) = (number("steps_per_mm")?, number("tab_steps")?, number("deepest_steps")?);
    ensure!(steps_per_mm > 0.0, "the controller counts no steps to a millimetre");
    Ok(Info { steps_per_mm, tab_steps, deepest_steps, fields })
}

/// The record in a controller's lines. Lines it cannot read are kept as faults, not dropped.
fn parse(text: &str) -> Log {
    let mut log = Log::default();
    let mut open: Option<Leg> = None;
    for line in text.lines().map(|line| line.trim_end_matches('\r').trim()) {
        let fields: Vec<&str> = line.split(',').collect();
        let read = (|| -> Result<()> {
            match fields[0] {
                "I" => log.info = Some(info(line)?),
                "P" => {
                    ensure!(fields.len() == 5, "a leg's opening line has five fields");
                    if let Some(leg) = open.take() {
                        log.faults.push(format!("leg {} never ended", leg.number));
                        log.legs.push(leg);
                    }
                    open = Some(Leg {
                        number: fields[1].parse()?,
                        rising: match fields[2] {
                            "+" => true,
                            "-" => false,
                            other => bail!("a leg runs + or -, not {other:?}"),
                        },
                        start_step: fields[3].parse()?,
                        start_reeds: reeds(fields[4])?,
                        changes: Vec::new(),
                        end: None,
                    });
                }
                "R" => {
                    ensure!(fields.len() == 5, "a reed's line has five fields");
                    let station: usize = fields[1].parse()?;
                    ensure!(station >= 1, "stations count from 1");
                    let closed = match fields[2] {
                        "1" => true,
                        "0" => false,
                        other => bail!("a reed reads 0 or 1, not {other:?}"),
                    };
                    // A change outside a read leg is the sled on its way to one.
                    if let Some(leg) = open.as_mut() {
                        leg.changes.push(Change { station: station - 1, closed, step: fields[3].parse()? });
                    }
                }
                "E" => {
                    ensure!(fields.len() == 4, "a leg's closing line has four fields");
                    let number: u32 = fields[1].parse()?;
                    let mut leg = open.take().with_context(|| format!("leg {number} ended without beginning"))?;
                    ensure!(leg.number == number, "leg {} was open when leg {number} ended", leg.number);
                    leg.end = Some((fields[2].parse()?, reeds(fields[3])?));
                    log.legs.push(leg);
                }
                _ if line.starts_with("OK sweep") || line.starts_with("ERR") => log.ending = Some(line.to_owned()),
                _ => {}
            }
            Ok(())
        })();
        if let Err(error) = read {
            log.faults.push(format!("{line:?}: {error:#}"));
        }
    }
    if let Some(leg) = open {
        log.faults.push(format!("leg {} never ended", leg.number));
        log.legs.push(leg);
    }
    log
}

// --- Where the magnet stood ---------------------------------------------------------------

/// What turns a step into the magnet's place: the rig's datums and what was read off this bench.
#[derive(Debug, Clone, PartialEq)]
struct Rig {
    /// Each station's reed centre, in millimetres into the tube from the rim on the tab.
    reed_centres: Vec<f64>,
    magnet_from_sled_face: f64,
    /// The roller's play in the sled's slot.
    play: f64,
    /// Reed changes nearer than this are one crossing.
    merge: f64,
}

/// A stretch of the tube over which a reed read closed, as the magnet's centre less the reed's.
/// An end is clipped when the leg began or ended inside the stretch, so no crossing was seen.
#[derive(Debug, Clone, Copy, PartialEq)]
struct Band {
    low: f64,
    high: f64,
    low_clipped: bool,
    high_clipped: bool,
}

/// The magnet's centre along the tube when the controller stands at `step` on a leg. Home was
/// found drawing the sled back, so a leg that draws it back reads true, and one that pushes it
/// into the tube has the sled trailing by the roller's play.
fn magnet_mm(step: i64, rising: bool, info: &Info, rig: &Rig) -> f64 {
    let sled_face = (step as f64 + info.tab_steps) / info.steps_per_mm - if rising { rig.play } else { 0.0 };
    sled_face + rig.magnet_from_sled_face
}

/// One station's closed stretches on one leg, lowest first, with what did not add up.
fn bands(leg: &Leg, station: usize, info: &Info, rig: &Rig) -> (Vec<Band>, Vec<String>) {
    let mut faults = Vec::new();
    let Some(&centre) = rig.reed_centres.get(station) else {
        return (Vec::new(), vec![format!("leg {}: no station {}", leg.number, station + 1)]);
    };
    let at = |step: i64| magnet_mm(step, leg.rising, info, rig) - centre;
    let mut closed = leg.start_reeds.get(station).copied().unwrap_or(false);
    // Each stretch as the leg met it: where the reed closed, where it opened, and whether either
    // was the leg's own end.
    let mut met: Vec<(f64, f64, bool, bool)> = Vec::new();
    let mut entered = closed.then(|| (at(leg.start_step), true));
    for change in leg.changes.iter().filter(|change| change.station == station) {
        if change.closed == closed {
            faults.push(format!("leg {} station {}: read {} twice running at step {}", leg.number, station + 1, if closed { "closed" } else { "open" }, change.step));
            continue;
        }
        closed = change.closed;
        if closed {
            entered = Some((at(change.step), false));
        } else if let Some((from, clipped)) = entered.take() {
            met.push((from, at(change.step), clipped, false));
        }
    }
    match (&leg.end, entered) {
        (Some((step, ends)), Some((from, clipped))) => {
            met.push((from, at(*step), clipped, true));
            if ends.get(station) != Some(&true) {
                faults.push(format!("leg {} station {}: the changes leave it closed and the leg's end reads it open", leg.number, station + 1));
            }
        }
        (Some((_, ends)), None) if ends.get(station) == Some(&true) => {
            faults.push(format!("leg {} station {}: the changes leave it open and the leg's end reads it closed", leg.number, station + 1));
        }
        (None, Some((from, clipped))) => {
            let last = leg.changes.last().map_or(leg.start_step, |change| change.step);
            met.push((from, at(last), clipped, true));
        }
        _ => {}
    }
    let mut found: Vec<Band> = met
        .into_iter()
        .map(|(from, to, from_clipped, to_clipped)| if leg.rising {
            Band { low: from, high: to, low_clipped: from_clipped, high_clipped: to_clipped }
        } else {
            Band { low: to, high: from, low_clipped: to_clipped, high_clipped: from_clipped }
        })
        .collect();
    found.sort_by(|a, b| a.low.total_cmp(&b.low));
    // Chatter at a crossing reads as slivers of closed and open: join stretches a sliver apart,
    // then drop what is still only a sliver.
    let mut joined: Vec<Band> = Vec::new();
    for band in found {
        match joined.last_mut() {
            Some(last) if band.low - last.high < rig.merge => {
                last.high = band.high;
                last.high_clipped = band.high_clipped;
            }
            _ => joined.push(band),
        }
    }
    joined.retain(|band| band.high - band.low >= rig.merge || band.low_clipped || band.high_clipped);
    (joined, faults)
}

fn round(value: f64) -> f64 {
    (value * 1000.0).round() / 1000.0
}

/// A set of readings of one crossing: their mean, their spread and how many.
fn spread(values: &[f64]) -> Value {
    if values.is_empty() {
        return Value::Null;
    }
    let (low, high) = values.iter().fold((f64::INFINITY, f64::NEG_INFINITY), |(low, high), v| (low.min(*v), high.max(*v)));
    json!({"mean_mm": round(values.iter().sum::<f64>() / values.len() as f64), "spread_mm": round(high - low), "readings": values.len()})
}

/// Everything the lines say, in millimetres: each leg's stretches, each crossing in the reed
/// calibration's own fields, and each station's crossings gathered over the cycles.
fn reduce(log: &Log, rig: &Rig, names: &BTreeMap<usize, String>, sled: &str) -> Result<Value> {
    let info = log.info.as_ref().context("the log holds no line from the controller about itself")?;
    let mut faults = log.faults.clone();
    let mut legs = Vec::new();
    let mut crossings = Vec::new();
    // Station, then rising or falling, then each leg's stretches in order.
    let mut gathered: BTreeMap<(usize, bool), Vec<Vec<Band>>> = BTreeMap::new();
    for leg in &log.legs {
        let mut stations = serde_json::Map::new();
        for station in 0..rig.reed_centres.len() {
            let (found, wrong) = bands(leg, station, info, rig);
            faults.extend(wrong);
            let changes = leg.changes.iter().filter(|change| change.station == station).count();
            if !names.contains_key(&station) {
                if changes > 0 {
                    faults.push(format!("leg {}: station {} changed {changes} times and no reed is named there", leg.number, station + 1));
                }
                continue;
            }
            let direction = if leg.rising { "rising" } else { "falling" };
            let repeat = leg.number.div_ceil(2);
            for band in &found {
                // Rising, a stretch is entered at its low end; falling, at its high end.
                let (closure, release) = if leg.rising { ((band.low, band.low_clipped), (band.high, band.high_clipped)) } else { ((band.high, band.high_clipped), (band.low, band.low_clipped)) };
                for (what, (at, clipped)) in [("closure", closure), ("release", release)] {
                    if !clipped {
                        crossings.push(json!({
                            "reed_id": names[&station], "station": station + 1, "vessel": "bare carbonator tube on the reed sweep rig",
                            "fluid": "air", "direction": direction, "radial_position": sled, "repeat": repeat,
                            "closure_or_release": what, "magnet_center_minus_reed_center_mm": round(at),
                            "liquid_height_mm": Value::Null, "liquid_volume_ml": Value::Null,
                        }));
                    }
                }
            }
            stations.insert((station + 1).to_string(), json!({
                "closed_at_start": leg.start_reeds.get(station).copied().unwrap_or(false),
                "changes": changes,
                "closed_over_mm": found.iter().map(|band| json!({
                    "from": round(band.low), "to": round(band.high), "from_is_the_legs_end": band.low_clipped, "to_is_the_legs_end": band.high_clipped,
                })).collect::<Vec<_>>(),
            }));
            gathered.entry((station, leg.rising)).or_default().push(found);
        }
        let end = leg.end.as_ref().map(|(step, _)| *step);
        legs.push(json!({
            "leg": leg.number, "direction": if leg.rising { "rising" } else { "falling" },
            "magnet_from_mm": round(magnet_mm(leg.start_step, leg.rising, info, rig)),
            "magnet_to_mm": end.map(|step| round(magnet_mm(step, leg.rising, info, rig))),
            "stations": stations,
        }));
    }
    let mut summary = serde_json::Map::new();
    for ((station, rising), per_leg) in &gathered {
        let direction = if *rising { "rising" } else { "falling" };
        let count = per_leg.first().map_or(0, Vec::len);
        let entry = if per_leg.iter().any(|found| found.len() != count) {
            faults.push(format!("station {} {direction}: the legs do not agree on how many stretches it closed over", station + 1));
            json!({"closed_stretches_per_leg": per_leg.iter().map(Vec::len).collect::<Vec<_>>()})
        } else {
            json!({"closed_stretches": (0..count).map(|index| {
                let ends = |pick: fn(&Band) -> (f64, bool)| -> Vec<f64> {
                    per_leg.iter().map(|found| pick(&found[index])).filter(|(_, clipped)| !clipped).map(|(at, _)| at).collect()
                };
                let (low, high) = (ends(|band| (band.low, band.low_clipped)), ends(|band| (band.high, band.high_clipped)));
                let (closes, opens) = if *rising { (low, high) } else { (high, low) };
                json!({"closes_at": spread(&closes), "opens_at": spread(&opens)})
            }).collect::<Vec<_>>()})
        };
        let name = names.get(station).cloned().unwrap_or_default();
        let slot = summary.entry((station + 1).to_string()).or_insert_with(|| json!({"reed_id": name}));
        slot[direction] = entry;
    }
    Ok(json!({
        "controller": info.fields,
        "sled": sled,
        "reeds": names.iter().map(|(station, name)| ((station + 1).to_string(), json!(name))).collect::<serde_json::Map<_, _>>(),
        "taken_as": {"roller_play_mm": rig.play, "chatter_joined_within_mm": rig.merge, "reed_centres_mm": rig.reed_centres, "magnet_from_sled_face_mm": rig.magnet_from_sled_face},
        "positions": "millimetres of the magnet's centre past the reed's centre, positive into the tube, which is up the carbonator",
        "ending": log.ending,
        "legs": legs,
        "crossings": crossings,
        "summary": summary,
        "faults": faults,
    }))
}

/// The summary as lines a person reads at the bench.
fn report(reduced: &Value) -> String {
    let mut out = String::new();
    let stretch = |value: &Value| match value.as_object() {
        Some(reading) => format!("{:+.2} (spread {:.2}, {} readings)", reading["mean_mm"].as_f64().unwrap_or(0.0), reading["spread_mm"].as_f64().unwrap_or(0.0), reading["readings"]),
        None => "beyond the sweep".to_owned(),
    };
    for (station, entry) in reduced["summary"].as_object().into_iter().flatten() {
        out += &format!("station {station}, reed {}\n", entry["reed_id"].as_str().unwrap_or("?"));
        for direction in ["rising", "falling"] {
            let Some(found) = entry.get(direction) else { continue };
            match found["closed_stretches"].as_array() {
                Some(stretches) if stretches.is_empty() => out += &format!("  {direction}: never closed\n"),
                Some(stretches) => {
                    for (index, one) in stretches.iter().enumerate() {
                        out += &format!("  {direction} stretch {}: closes at {}, opens at {}\n", index + 1, stretch(&one["closes_at"]), stretch(&one["opens_at"]));
                    }
                }
                None => out += &format!("  {direction}: the legs disagree, closing over {} stretches\n", found["closed_stretches_per_leg"]),
            }
        }
    }
    for fault in reduced["faults"].as_array().into_iter().flatten() {
        out += &format!("fault: {}\n", fault.as_str().unwrap_or_default());
    }
    out
}

// --- The session at the bench -------------------------------------------------------------

/// The line to the controller. The bench has a serial port behind it and the tests a script.
trait Wire {
    fn poll(&mut self) -> Result<Vec<u8>>;
    fn send(&mut self, bytes: &[u8]) -> Result<()>;
}

struct Port(Box<dyn serialport::SerialPort>);
impl Wire for Port {
    fn poll(&mut self) -> Result<Vec<u8>> {
        serials::poll(&mut *self.0)
    }
    fn send(&mut self, bytes: &[u8]) -> Result<()> {
        serials::send(&mut *self.0, bytes)
    }
}

/// Every byte the controller sends: held in memory until the sweep has a directory, then
/// written to its file as it arrives.
#[derive(Default)]
struct Kept {
    held: Vec<u8>,
    file: Option<fs::File>,
}

impl Kept {
    fn take(&mut self, bytes: &[u8]) -> Result<()> {
        match &mut self.file {
            Some(file) => file.write_all(bytes)?,
            None => self.held.extend_from_slice(bytes),
        }
        Ok(())
    }

    fn settle(&mut self, path: &Path) -> Result<()> {
        let mut file = OpenOptions::new().write(true).create_new(true).open(path)?;
        file.write_all(&self.held)?;
        self.held.clear();
        self.file = Some(file);
        Ok(())
    }
}

/// A conversation with the controller.
struct Session<'a> {
    wire: &'a mut dyn Wire,
    kept: Kept,
    pending: String,
    echo: bool,
}

impl Session<'_> {
    /// The whole lines that have arrived since the last call.
    fn lines(&mut self) -> Result<Vec<String>> {
        let bytes = self.wire.poll()?;
        self.kept.take(&bytes)?;
        self.pending += &String::from_utf8_lossy(&bytes);
        let mut lines = Vec::new();
        while let Some(end) = self.pending.find('\n') {
            let line = self.pending[..end].trim_end_matches('\r').to_owned();
            self.pending.drain(..=end);
            if self.echo {
                println!("{line}");
            }
            lines.push(line);
        }
        Ok(lines)
    }

    fn say(&mut self, command: &str) -> Result<()> {
        if self.echo {
            println!("> {command}");
        }
        self.wire.send(format!("{command}\n").as_bytes())
    }

    /// Sends `command` and waits for the first line `wanted` picks. An `ERR` line ends the wait
    /// as a failure, and so does Ctrl-C, which also stops the sled.
    fn ask(&mut self, command: &str, wanted: fn(&str) -> bool, patience: Duration) -> Result<String> {
        self.say(command)?;
        let started = Instant::now();
        loop {
            for line in self.lines()? {
                if wanted(&line) {
                    return Ok(line);
                }
                if line.starts_with("ERR") {
                    bail!("the controller answered {command:?} with: {line}");
                }
            }
            if x1::interrupted() {
                self.wire.send(b"stop\n")?;
                bail!("interrupted during {command:?}; the sled was told to stop");
            }
            ensure!(started.elapsed() < patience, "no answer to {command:?} in {} s", patience.as_secs());
            thread::sleep(Duration::from_millis(5));
        }
    }
}

/// What a sweep was asked to be.
#[derive(Debug, Clone, Copy, PartialEq)]
struct Asked {
    from: Option<f64>,
    to: Option<f64>,
    speed: f64,
    cycles: u32,
}

/// Asks the controller what it is and homes the sled. Nothing is kept on disk if this fails, so
/// the same command runs again once the bench is put right.
fn ready(session: &mut Session) -> Result<Info> {
    // A controller that restarted when its port opened is still talking; let it finish.
    let settle = Instant::now();
    while settle.elapsed() < Duration::from_millis(1500) {
        session.lines()?;
        thread::sleep(Duration::from_millis(20));
    }
    let about = info(&session.ask("status", |line| line.starts_with("I,"), Duration::from_secs(5))?)?;
    session.ask("home", |line| line.starts_with("OK home"), Duration::from_secs(240))?;
    Ok(about)
}

/// Reads the homed sled out and back. Returns the sweep as it was commanded.
fn read_out(session: &mut Session, about: &Info, asked: Asked) -> Result<Value> {
    let home_mm = about.tab_steps / about.steps_per_mm;
    let deepest_mm = about.deepest_steps / about.steps_per_mm;
    let from = asked.from.unwrap_or(home_mm + NEAR_END_PAST_HOME_MM);
    // The controller takes whole steps; a far end named to three places stays inside its reach.
    let to = asked.to.unwrap_or((deepest_mm * 1000.0).floor() / 1000.0);
    ensure!(from < to, "the sweep's near end {from} mm is not short of its far end {to} mm");
    let travel = (to - from) * 2.0 * f64::from(asked.cycles) / asked.speed;
    let command = format!("sweep {from:.3} {to:.3} {:.3} {}", asked.speed, asked.cycles);
    session.ask(&command, |line| line.starts_with("OK sweep"), Duration::from_secs_f64(travel + 120.0))?;
    Ok(json!({"from_mm": from, "to_mm": to, "mm_per_s": asked.speed, "cycles": asked.cycles, "sent": command}))
}

// --- The command ----------------------------------------------------------------------------

fn number(args: &[String], key: &str) -> Result<Option<f64>> {
    option(args, key)?
        .map(|text| {
            let value: f64 = text.parse().with_context(|| format!("{key} takes a number"))?;
            ensure!(value.is_finite(), "{key} takes a finite number");
            Ok(value)
        })
        .transpose()
}

/// `1=NAME,2=NAME`: the reed lying at each station, by the name it carries on the bench.
fn named(text: &str, stations: usize) -> Result<BTreeMap<usize, String>> {
    let mut names = BTreeMap::new();
    for pair in text.split(',').filter(|pair| !pair.trim().is_empty()) {
        let (station, name) = pair.split_once('=').with_context(|| format!("--reeds takes STATION=NAME, not {pair:?}"))?;
        let station: usize = station.trim().parse().with_context(|| format!("a station is a number, not {station:?}"))?;
        ensure!((1..=stations).contains(&station), "the comb has stations 1 to {stations}, not {station}");
        ensure!(!name.trim().is_empty(), "station {station}'s reed needs a name");
        ensure!(names.insert(station - 1, name.trim().to_owned()).is_none(), "station {station} is named twice");
    }
    ensure!(!names.is_empty(), "--reeds names no reed");
    Ok(names)
}

pub fn sweep(root: &Path, args: &[String]) -> Result<()> {
    ensure!(
        validate_args(args, &["--list"], &["--port", "--replay", "--output", "--sled", "--reeds", "--from", "--to", "--speed", "--cycles", "--play", "--glass", "--merge", "--label"])?.is_empty(),
        USAGE
    );
    if flag(args, "--list") {
        return serials::list();
    }
    let datums_path = root.join(DATUMS);
    let datums = read_json(&datums_path)?;
    let field = |key: &str| datums[key].as_f64().with_context(|| format!("{DATUMS} holds no {key}"));
    let sled = option(args, "--sled")?.context(USAGE)?;
    let chosen = datums["sleds"]
        .as_array()
        .into_iter()
        .flatten()
        .find(|entry| entry["sled"] == sled.as_str())
        .with_context(|| format!("no sled named {sled:?} in {DATUMS}"))?
        .clone();
    let pockets: Vec<f64> = datums["stations"].as_array().into_iter().flatten().filter_map(|station| station["reed_centre_mm"].as_f64()).collect();
    ensure!(!pockets.is_empty(), "{DATUMS} holds no stations");
    // A reed lies pushed toward the tab, so its centre is short of its pocket's by half the room
    // the pocket leaves its glass.
    let glass = number(args, "--glass")?.map_or_else(|| field("reed_glass_length_mm"), Ok)?;
    let room = field("reed_pocket_length_mm")? - glass;
    ensure!(room >= 0.0, "a glass {glass} mm long does not fit the pocket");
    let rig = Rig {
        reed_centres: pockets.iter().map(|pocket| pocket - room / 2.0).collect(),
        magnet_from_sled_face: field("magnet_from_sled_face_mm")?,
        play: number(args, "--play")?.map_or_else(|| field("roller_play_in_slot_mm"), Ok)?,
        merge: number(args, "--merge")?.unwrap_or(DEFAULT_MERGE_MM),
    };
    ensure!(rig.play >= 0.0 && rig.merge >= 0.0, "--play and --merge are not negative");
    let names = match option(args, "--reeds")? {
        Some(text) => named(&text, pockets.len())?,
        None => (0..pockets.len()).map(|station| (station, format!("station {}", station + 1))).collect(),
    };
    let asked = Asked {
        from: number(args, "--from")?,
        to: number(args, "--to")?,
        speed: number(args, "--speed")?.unwrap_or(DEFAULT_SPEED_MM_PER_S),
        cycles: option(args, "--cycles")?.map_or(Ok(DEFAULT_CYCLES), |text| text.parse().context("--cycles takes a whole number"))?,
    };
    ensure!(asked.speed > 0.0 && asked.cycles >= 1, "a sweep has a speed and at least one cycle");

    let destination = PathBuf::from(option(args, "--output")?.context(USAGE)?);
    let (port, replay) = (option(args, "--port")?, option(args, "--replay")?);
    ensure!(port.is_some() != replay.is_some(), "name the controller's --port, or a saved log to --replay");
    ensure!(!destination.exists(), "the sweep's directory must be new: {}", destination.display());
    let directory = || -> Result<()> {
        if let Some(parent) = destination.parent().filter(|parent| !parent.as_os_str().is_empty()) {
            fs::create_dir_all(parent)?;
        }
        fs::create_dir(&destination).with_context(|| format!("the sweep's directory must be new: {}", destination.display()))
    };
    let raw_path = destination.join("raw.log");
    let started = x1::utc()?;

    let (commanded, failure) = match (&port, &replay) {
        (Some(port), _) => {
            let mut wire = Port(serials::open_quiet(port, Duration::from_millis(20))?);
            let _interrupt = x1::Interrupt::install();
            let mut session = Session { wire: &mut wire, kept: Kept::default(), pending: String::new(), echo: true };
            let about = ready(&mut session)?;
            directory()?;
            session.kept.settle(&raw_path)?;
            match read_out(&mut session, &about, asked) {
                Ok(commanded) => (commanded, None),
                Err(error) => (Value::Null, Some(format!("{error:#}"))),
            }
        }
        (None, Some(saved)) => {
            ensure!(Path::new(saved).is_file(), "no saved log at {saved}");
            directory()?;
            fs::copy(saved, &raw_path).with_context(|| format!("read {saved}"))?;
            (Value::Null, None)
        }
        (None, None) => unreachable!("one of --port and --replay is named"),
    };

    let text = String::from_utf8_lossy(&fs::read(&raw_path)?).into_owned();
    let log = parse(&text);
    let mut record = json!({
        "what": "One sweep of the reed sweep rig: a float pushed along a bare carbonator tube past the reeds under its wall.",
        "started_utc": started,
        "label": option(args, "--label")?.unwrap_or_default(),
        "source": port.map_or_else(|| json!({"replayed": replay}), |port| json!({"port": port})),
        "commanded": commanded,
        "sled_as_drawn": chosen,
        "datums": {"file": DATUMS, "sha256": sha(&fs::read(&datums_path)?)},
        "reed_glass_length_mm": glass,
        "failure": failure,
    });
    match reduce(&log, &rig, &names, &sled) {
        Ok(reduced) => {
            print!("{}", report(&reduced));
            for (key, value) in reduced.as_object().into_iter().flatten() {
                record[key] = value.clone();
            }
        }
        Err(error) => record["failure"] = json!(format!("{}{error:#}", failure.as_ref().map(|first| format!("{first}; ")).unwrap_or_default())),
    }
    write_json(&destination.join("sweep.json"), &record)?;
    println!("{}", destination.join("sweep.json").display());
    if let Some(failure) = record["failure"].as_str() {
        bail!("{failure}");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn rig() -> Rig {
        Rig { reed_centres: vec![30.0, 58.0, 86.0, 114.0], magnet_from_sled_face: 25.0, play: 0.4, merge: 0.3 }
    }

    fn about() -> Info {
        info("I,rig=reed-sweep,built=Nov 12 2026 10:00:00,steps_per_mm=320,tab_steps=243,deepest_steps=34528,homed=1,pos=0,reeds=0000,home=0,dirinvert=0,homelevel=high").unwrap()
    }

    /// The step at which the magnet stands `offset` mm past station `station`'s reed on a leg.
    fn step_at(station: usize, offset: f64, rising: bool) -> i64 {
        let (info, rig) = (about(), rig());
        let sled_face = rig.reed_centres[station] + offset - rig.magnet_from_sled_face + if rising { rig.play } else { 0.0 };
        (sled_face * info.steps_per_mm - info.tab_steps).round() as i64
    }

    /// A controller's lines for a reed at station 2 that closes from 12 mm below its centre to
    /// 13 mm above on the way up, and from 12.5 above to 12.5 below on the way down.
    fn two_legs() -> String {
        let info = "I,rig=reed-sweep,built=Nov 12 2026 10:00:00,steps_per_mm=320,tab_steps=243,deepest_steps=34528,homed=1,pos=320,reeds=0000,home=0,dirinvert=0,homelevel=high";
        format!(
            "{info}\nP,1,+,320,0000\nR,2,1,{},100\nR,2,0,{},200\nE,1,34000,0000\nP,2,-,34000,0000\nR,2,1,{},300\nR,2,0,{},400\nE,2,320,0000\nOK sweep\n",
            step_at(1, -12.0, true),
            step_at(1, 13.0, true),
            step_at(1, 12.5, false),
            step_at(1, -12.5, false),
        )
    }

    fn names() -> BTreeMap<usize, String> {
        BTreeMap::from([(1, "A".to_owned())])
    }

    #[test]
    fn the_controllers_line_about_itself_is_read() {
        let info = about();
        assert_eq!((info.steps_per_mm, info.tab_steps, info.deepest_steps), (320.0, 243.0, 34528.0));
        assert_eq!(info.fields["built"], "Nov 12 2026 10:00:00");
        assert!(super::info("I,rig=weld,steps_per_mm=320,tab_steps=1,deepest_steps=2").is_err());
        assert!(super::info("I,rig=reed-sweep,tab_steps=1,deepest_steps=2").is_err());
    }

    #[test]
    fn a_sweeps_lines_become_its_legs() {
        let log = parse(&two_legs());
        assert!(log.faults.is_empty(), "{:?}", log.faults);
        assert_eq!(log.ending.as_deref(), Some("OK sweep"));
        assert_eq!(log.legs.len(), 2);
        assert!(log.legs[0].rising && !log.legs[1].rising);
        assert_eq!(log.legs[0].changes.len(), 2);
        assert_eq!(log.legs[0].changes[0].station, 1);
        assert_eq!(log.legs[1].end, Some((320, vec![false; 4])));
    }

    #[test]
    fn a_change_between_legs_belongs_to_none() {
        let log = parse("R,1,1,50,1\nP,1,+,100,1000\nE,1,200,1000\nR,1,0,150,2\n");
        assert!(log.faults.is_empty(), "{:?}", log.faults);
        assert_eq!(log.legs.len(), 1);
        assert!(log.legs[0].changes.is_empty());
    }

    #[test]
    fn lines_that_do_not_read_are_kept_as_faults() {
        let log = parse("P,1,up,100,0000\nR,0,1,5,1\nE,3,200,0000\nP,2,+,0,0000\n");
        assert_eq!(log.faults.len(), 4, "{:?}", log.faults);
        assert_eq!(log.legs.len(), 1);
        assert!(log.legs[0].end.is_none());
    }

    #[test]
    fn a_closed_stretch_is_placed_from_the_reeds_centre_both_ways() {
        let log = parse(&two_legs());
        let (up, faults) = bands(&log.legs[0], 1, &about(), &rig());
        assert!(faults.is_empty(), "{faults:?}");
        assert_eq!(up.len(), 1);
        assert!((up[0].low + 12.0).abs() < 0.01 && (up[0].high - 13.0).abs() < 0.01, "{up:?}");
        assert!(!up[0].low_clipped && !up[0].high_clipped);
        let (down, _) = bands(&log.legs[1], 1, &about(), &rig());
        assert!((down[0].low + 12.5).abs() < 0.01 && (down[0].high - 12.5).abs() < 0.01, "{down:?}");
    }

    #[test]
    fn the_rollers_play_moves_only_the_legs_that_push() {
        let (info, mut rig) = (about(), rig());
        let pushed = magnet_mm(3200, true, &info, &rig);
        let drawn = magnet_mm(3200, false, &info, &rig);
        assert!((drawn - pushed - rig.play).abs() < 1e-9);
        rig.play = 0.0;
        assert_eq!(magnet_mm(3200, true, &info, &rig), magnet_mm(3200, false, &info, &rig));
        assert!((magnet_mm(0, false, &info, &rig) - (243.0 / 320.0 + 25.0)).abs() < 1e-9);
    }

    #[test]
    fn a_leg_that_begins_or_ends_inside_a_stretch_claims_no_crossing_there() {
        let text = format!("P,1,+,320,0100\nR,2,0,{},1\nR,2,1,{},2\nE,1,34000,0100\n", step_at(1, -20.0, true), step_at(1, 20.0, true));
        let log = parse(&text);
        let (found, faults) = bands(&log.legs[0], 1, &about(), &rig());
        assert!(faults.is_empty(), "{faults:?}");
        assert_eq!(found.len(), 2);
        assert!(found[0].low_clipped && !found[0].high_clipped);
        assert!(!found[1].low_clipped && found[1].high_clipped);
        assert!((found[0].high + 20.0).abs() < 0.01 && (found[1].low - 20.0).abs() < 0.01);
    }

    #[test]
    fn chatter_at_a_crossing_is_one_crossing() {
        // Closing chatters three times over a tenth of a millimetre, and a lone blip stands far off.
        let steps = [(-12.00, true), (-11.97, false), (-11.94, true), (-11.92, false), (-11.90, true), (13.0, false), (30.0, true), (30.05, false)];
        let lines: String = steps.iter().map(|(offset, closed)| format!("R,2,{},{},1\n", u8::from(*closed), step_at(1, *offset, true))).collect();
        let log = parse(&format!("P,1,+,320,0000\n{lines}E,1,34000,0000\n"));
        let (found, faults) = bands(&log.legs[0], 1, &about(), &rig());
        assert!(faults.is_empty(), "{faults:?}");
        assert_eq!(found.len(), 1, "{found:?}");
        assert!((found[0].low + 12.0).abs() < 0.01 && (found[0].high - 13.0).abs() < 0.01);
    }

    #[test]
    fn a_reed_that_reads_the_same_twice_is_a_fault() {
        let log = parse("P,1,+,320,0000\nR,2,1,5000,1\nR,2,1,5100,2\nR,2,0,9000,3\nE,1,34000,0100\n");
        let (found, faults) = bands(&log.legs[0], 1, &about(), &rig());
        assert_eq!(found.len(), 1);
        assert_eq!(faults.len(), 2, "{faults:?}");
    }

    #[test]
    fn crossings_are_named_by_the_way_the_float_is_going() {
        let reduced = reduce(&parse(&two_legs()), &rig(), &names(), "nominal").unwrap();
        let crossings = reduced["crossings"].as_array().unwrap();
        let find = |direction: &str, what: &str| crossings.iter().find(|c| c["direction"] == direction && c["closure_or_release"] == what).unwrap()["magnet_center_minus_reed_center_mm"].as_f64().unwrap();
        assert!((find("rising", "closure") + 12.0).abs() < 0.01);
        assert!((find("rising", "release") - 13.0).abs() < 0.01);
        assert!((find("falling", "closure") - 12.5).abs() < 0.01);
        assert!((find("falling", "release") + 12.5).abs() < 0.01);
        assert_eq!(crossings.len(), 4);
        assert_eq!(crossings[0]["reed_id"], "A");
        assert_eq!(crossings[0]["radial_position"], "nominal");
        assert!(reduced["faults"].as_array().unwrap().is_empty(), "{}", reduced["faults"]);
    }

    #[test]
    fn cycles_gather_into_a_mean_and_a_spread() {
        let leg = |number: u32, low: f64, high: f64| format!("P,{number},+,320,0000\nR,2,1,{},1\nR,2,0,{},2\nE,{number},34000,0000\n", step_at(1, low, true), step_at(1, high, true));
        let text = format!("{}\n{}{}{}", "I,rig=reed-sweep,steps_per_mm=320,tab_steps=243,deepest_steps=34528", leg(1, -12.0, 13.0), leg(3, -12.2, 13.1), leg(5, -11.8, 12.9));
        let reduced = reduce(&parse(&text), &rig(), &names(), "far").unwrap();
        let stretch = &reduced["summary"]["2"]["rising"]["closed_stretches"][0];
        assert!((stretch["closes_at"]["mean_mm"].as_f64().unwrap() + 12.0).abs() < 0.01);
        assert!((stretch["closes_at"]["spread_mm"].as_f64().unwrap() - 0.4).abs() < 0.01);
        assert_eq!(stretch["opens_at"]["readings"], 3);
        assert!(report(&reduced).contains("station 2, reed A"));
        assert!(report(&reduced).contains("rising stretch 1: closes at -12.00"));
    }

    #[test]
    fn legs_that_disagree_are_said_to() {
        let text = format!(
            "I,rig=reed-sweep,steps_per_mm=320,tab_steps=243,deepest_steps=34528\nP,1,+,320,0000\nR,2,1,{},1\nR,2,0,{},2\nE,1,34000,0000\nP,3,+,320,0000\nE,3,34000,0000\n",
            step_at(1, -12.0, true),
            step_at(1, 13.0, true)
        );
        let reduced = reduce(&parse(&text), &rig(), &names(), "nominal").unwrap();
        assert_eq!(reduced["summary"]["2"]["rising"]["closed_stretches_per_leg"], json!([1, 0]));
        assert!(reduced["faults"].as_array().unwrap().iter().any(|fault| fault.as_str().unwrap().contains("do not agree")));
    }

    #[test]
    fn a_reed_at_a_station_with_no_name_is_a_fault() {
        let text = "I,rig=reed-sweep,steps_per_mm=320,tab_steps=243,deepest_steps=34528\nP,1,+,320,0000\nR,4,1,9000,1\nR,4,0,9900,2\nE,1,34000,0000\n";
        let reduced = reduce(&parse(text), &rig(), &names(), "nominal").unwrap();
        assert!(reduced["crossings"].as_array().unwrap().is_empty());
        assert!(reduced["faults"][0].as_str().unwrap().contains("station 4"));
    }

    #[test]
    fn reeds_are_named_by_station() {
        let names = named("1=A, 3=B", 4).unwrap();
        assert_eq!(names, BTreeMap::from([(0, "A".to_owned()), (2, "B".to_owned())]));
        assert!(named("5=A", 4).is_err());
        assert!(named("1=A,1=B", 4).is_err());
        assert!(named("A", 4).is_err());
        assert!(named("", 4).is_err());
    }

    /// A controller that answers each command with the lines scripted for it.
    struct Scripted {
        answers: Vec<(&'static str, String)>,
        waiting: Vec<u8>,
        heard: Vec<String>,
    }
    impl Wire for Scripted {
        fn poll(&mut self) -> Result<Vec<u8>> {
            Ok(std::mem::take(&mut self.waiting))
        }
        fn send(&mut self, bytes: &[u8]) -> Result<()> {
            let command = String::from_utf8_lossy(bytes).trim().to_owned();
            let answer = self.answers.iter().find(|(prefix, _)| command.starts_with(prefix)).map(|(_, answer)| answer.clone()).unwrap_or_else(|| "ERR unknown command; type help\n".to_owned());
            self.waiting.extend(answer.as_bytes());
            self.heard.push(command);
            Ok(())
        }
    }

    #[test]
    fn a_session_homes_then_sweeps_the_sleds_whole_reach() {
        let status = "\n-- reed sweep rig --\nI,rig=reed-sweep,steps_per_mm=320,tab_steps=243,deepest_steps=34528,homed=0,pos=0,reeds=0000,home=0\n".to_owned();
        let mut wire = Scripted { answers: vec![("status", status), ("home", "OK home, the switch lets go 0.300 mm past its trip\n".to_owned()), ("sweep", two_legs())], waiting: Vec::new(), heard: Vec::new() };
        let mut session = Session { wire: &mut wire, kept: Kept::default(), pending: String::new(), echo: false };
        let about = ready(&mut session).unwrap();
        let commanded = read_out(&mut session, &about, Asked { from: None, to: None, speed: 2.0, cycles: 1 }).unwrap();
        let raw = std::mem::take(&mut session.kept.held);
        assert_eq!(wire.heard, ["status", "home", "sweep 1.759 107.900 2.000 1"]);
        assert_eq!(commanded["to_mm"], 107.9);
        let log = parse(&String::from_utf8(raw).unwrap());
        assert_eq!(log.legs.len(), 2);
        assert_eq!(log.ending.as_deref(), Some("OK sweep"));
    }

    #[test]
    fn a_session_stops_at_the_controllers_refusal() {
        let status = "I,rig=reed-sweep,steps_per_mm=320,tab_steps=243,deepest_steps=34528\n".to_owned();
        let mut wire = Scripted { answers: vec![("status", status), ("home", "ERR home: press the home switch's lever once by hand, then send home again\n".to_owned())], waiting: Vec::new(), heard: Vec::new() };
        let mut session = Session { wire: &mut wire, kept: Kept::default(), pending: String::new(), echo: false };
        let error = ready(&mut session).err().unwrap();
        assert!(format!("{error:#}").contains("press the home switch"));
        assert_eq!(wire.heard, ["status", "home"]);
    }
}
