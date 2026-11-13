//! Part cooling for one stretch of one object: the model paths of that object lying between two
//! planes square to an axis take the part fan at a chosen speed. Every other path keeps the fan
//! the slicer and the foundation stage gave it, and no path's motion or extrusion changes.

use crate::gcode::{words, MODEL};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::path::Path;

/// The stretch of `object`, in plate coordinates: the points whose distance along `axis` from
/// `origin` lies in `span`.
#[derive(Clone, Copy, Debug)]
pub struct Stretch {
    pub object: i64,
    pub origin: [f64; 3],
    pub axis: [f64; 3],
    pub span: [f64; 2],
    /// The part fan's speed over the stretch, in percent.
    pub fan_percent: f64,
}

/// What the stage changed.
#[derive(Clone, Copy, Debug, Default)]
pub struct Reading {
    pub cooled_moves: u64,
    pub cooled_mm: f64,
    pub cooled_seconds: f64,
    /// Of the cooled motion, what the fan was already blowing on.
    pub already_cooled_seconds: f64,
    pub fan_commands: u64,
    pub z_mm: [f64; 2],
    /// The object's model motion outside the stretch, in seconds.
    pub other_seconds: f64,
}

fn word(words: &[(u8, f64)], key: u8) -> Option<f64> {
    words.iter().find(|(k, _)| *k == key).map(|(_, v)| *v)
}

/// Write `source`'s G-code to `output` with the stretch's cooling.
pub fn apply(source: &Path, output: &Path, stretch: &Stretch) -> std::io::Result<Reading> {
    let cooling = stretch.fan_percent * 255.0 / 100.0;
    let mut out = BufWriter::new(std::fs::File::create(output)?);
    let mut reading = Reading { z_mm: [f64::INFINITY, f64::NEG_INFINITY], ..Reading::default() };
    let (mut pos, mut feed) = ([0.0f64; 3], 0.0f64);
    let (mut absolute, mut relative_e, mut e) = (true, true, 0.0f64);
    let (mut feature, mut object) = (String::new(), -1i64);
    // The fan the plate asks for here, and the fan last commanded.
    let (mut native, mut emitted) = (0.0f64, 0.0f64);
    for line in BufReader::new(std::fs::File::open(source)?).lines() {
        let line = line?;
        let line = line.trim_end_matches(['\r', '\n']);
        if let Some(comment) = line.strip_prefix(';').map(str::trim) {
            if let Some(value) = comment.strip_prefix("FEATURE:") {
                feature = value.trim().into();
            } else if let Some(value) = comment.strip_prefix("OBJECT_ID:").or_else(|| comment.strip_prefix("start printing object, unique label id:")) {
                object = value.trim().parse().unwrap_or(-1);
            } else if comment.starts_with("stop printing object") {
                object = -1;
            }
            writeln!(out, "{line}")?;
            continue;
        }
        let code = line.split(';').next().unwrap_or("").trim();
        let command = code.split_whitespace().next().unwrap_or("");
        let w = words(code.get(command.len()..).unwrap_or(""));
        match command {
            "M106" | "M107" if word(&w, b'P').unwrap_or(1.0) == 1.0 => {
                native = if command == "M107" { 0.0 } else { word(&w, b'S').unwrap_or(255.0) };
                emitted = native;
            }
            "G90" | "G91" => absolute = command == "G90",
            "M82" | "M83" => relative_e = command == "M83",
            "G92" => {
                for (axis, key) in [b'X', b'Y', b'Z'].into_iter().enumerate() {
                    pos[axis] = word(&w, key).unwrap_or(pos[axis]);
                }
                e = word(&w, b'E').unwrap_or(e);
            }
            _ => {}
        }
        if !matches!(command, "G0" | "G1" | "G2" | "G3") {
            writeln!(out, "{line}")?;
            continue;
        }
        feed = word(&w, b'F').unwrap_or(feed);
        let mut next = pos;
        for (axis, key) in [b'X', b'Y', b'Z'].into_iter().enumerate() {
            if let Some(value) = word(&w, key) {
                next[axis] = if absolute { value } else { pos[axis] + value };
            }
        }
        let pushed = match word(&w, b'E') {
            Some(value) if relative_e => value,
            Some(value) => value - e,
            None => 0.0,
        };
        if let Some(value) = word(&w, b'E') {
            e = if relative_e { e + value } else { value };
        }
        let length = (next[0] - pos[0]).hypot(next[1] - pos[1]);
        if pushed > 0.0 && length > 1e-9 {
            let middle = [0, 1, 2].map(|axis| 0.5 * (pos[axis] + next[axis]));
            let along: f64 = (0..3).map(|axis| (middle[axis] - stretch.origin[axis]) * stretch.axis[axis]).sum();
            let model = object == stretch.object && MODEL.contains(&feature.as_str());
            let inside = model && along >= stretch.span[0] && along <= stretch.span[1];
            let target = if inside { native.max(cooling) } else { native };
            if (emitted - target).abs() > 1e-6 {
                writeln!(out, "M106 P1 S{target:.3}")?;
                emitted = target;
                reading.fan_commands += 1;
            }
            let seconds = if feed > 0.0 { length * 60.0 / feed } else { 0.0 };
            if inside {
                reading.cooled_moves += 1;
                reading.cooled_mm += length;
                reading.cooled_seconds += seconds;
                if native > 0.0 {
                    reading.already_cooled_seconds += seconds;
                }
                reading.z_mm = [reading.z_mm[0].min(middle[2]), reading.z_mm[1].max(middle[2])];
            } else if model {
                reading.other_seconds += seconds;
            }
        }
        pos = next;
        writeln!(out, "{line}")?;
    }
    out.flush()?;
    Ok(reading)
}
