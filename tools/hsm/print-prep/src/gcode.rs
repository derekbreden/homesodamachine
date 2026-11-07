//! The paths a sliced plate's G-code deposits, layer by layer: each layer's top and height, and
//! its roads, the straight runs a bead is laid along, with their width, feature and object.

use anyhow::{Context, Result};
use std::io::{BufRead, BufReader, Read};
use std::path::Path;
use std::rc::Rc;

pub const SUPPORT: [&str; 3] = ["Support", "Support interface", "Support transition"];
pub const MODEL: [&str; 11] = ["Outer wall", "Inner wall", "Overhang wall", "Bottom surface", "Top surface",
    "Internal solid infill", "Sparse infill", "Bridge", "Gap infill", "Internal Bridge", "Floating vertical shell"];
pub const WALLS: [&str; 3] = ["Outer wall", "Inner wall", "Overhang wall"];

#[derive(Clone)]
pub struct Road {
    pub x0: f64,
    pub y0: f64,
    pub x1: f64,
    pub y1: f64,
    pub width: f64,
    pub feature: Rc<str>,
    pub object: Option<i64>,
}

impl Road {
    pub fn is_support(&self) -> bool {
        SUPPORT.contains(&&*self.feature)
    }
}

pub struct Layer {
    pub z: f64,
    pub height: f64,
    pub roads: Vec<Road>,
}

/// The plate's G-code, read from a sliced archive.
pub fn plate_gcode(archive: &Path) -> Result<Vec<u8>> {
    let mut zip = zip::ZipArchive::new(std::fs::File::open(archive).with_context(|| format!("opening {}", archive.display()))?)?;
    let mut bytes = Vec::new();
    zip.by_name("Metadata/plate_1.gcode")?.read_to_end(&mut bytes)?;
    Ok(bytes)
}

/// Every layer of `gcode`, read in one pass; `each` sees one layer at a time.
pub fn layers(gcode: &[u8], mut each: impl FnMut(Layer)) {
    let mut reader = Reader::default();
    for line in BufReader::new(gcode).split(b'\n') {
        let Ok(line) = line else { break };
        if let Some(layer) = reader.line(&String::from_utf8_lossy(&line)) {
            each(layer);
        }
    }
    if let Some(layer) = reader.finish() {
        each(layer);
    }
}

struct Reader {
    x: f64,
    y: f64,
    e: f64,
    width: f64,
    height: f64,
    feature: Rc<str>,
    object: Option<i64>,
    z: Option<f64>,
    roads: Vec<Road>,
    absolute: bool,
    relative_e: bool,
}

impl Default for Reader {
    fn default() -> Reader {
        Reader { x: 0.0, y: 0.0, e: 0.0, width: 0.42, height: 0.24, feature: Rc::from(""), object: None, z: None,
                 roads: Vec::new(), absolute: true, relative_e: true }
    }
}

/// A number as G-code writes one: optional sign, digits with an optional point, or a point and
/// digits.
fn number(text: &[u8]) -> Option<(f64, usize)> {
    let mut at = 0;
    if at < text.len() && (text[at] == b'-' || text[at] == b'+') {
        at += 1;
    }
    let digits = |from: usize| text[from..].iter().take_while(|c| c.is_ascii_digit()).count();
    let whole = digits(at);
    let mut end = at + whole;
    if whole > 0 {
        if end < text.len() && text[end] == b'.' {
            end += 1 + digits(end + 1);
        }
    } else if end < text.len() && text[end] == b'.' && digits(end + 1) > 0 {
        end += 1 + digits(end + 1);
    } else {
        return None;
    }
    std::str::from_utf8(&text[..end]).ok()?.parse().ok().map(|v| (v, end))
}

/// The letter words of a command, later ones replacing earlier.
pub fn words(text: &str) -> Vec<(u8, f64)> {
    let bytes = text.as_bytes();
    let mut out: Vec<(u8, f64)> = Vec::new();
    let mut at = 0;
    while at < bytes.len() {
        let c = bytes[at];
        if c.is_ascii_uppercase() {
            if let Some((value, length)) = number(&bytes[at + 1..]) {
                match out.iter_mut().find(|(k, _)| *k == c) {
                    Some(slot) => slot.1 = value,
                    None => out.push((c, value)),
                }
                at += 1 + length;
                continue;
            }
        }
        at += 1;
    }
    out
}

fn word(words: &[(u8, f64)], key: u8) -> Option<f64> {
    words.iter().find(|(k, _)| *k == key).map(|(_, v)| *v)
}

/// The longest chord an arc is read in.
const CHORD: f64 = 0.25;

/// The points of a G2/G3 arc, at most `CHORD` apart.
fn arc(x0: f64, y0: f64, x1: f64, y1: f64, words: &[(u8, f64)], clockwise: bool) -> Vec<(f64, f64)> {
    let (cx, cy) = (x0 + word(words, b'I').unwrap_or(0.0), y0 + word(words, b'J').unwrap_or(0.0));
    let r = (x0 - cx).hypot(y0 - cy);
    let a0 = (y0 - cy).atan2(x0 - cx);
    let mut sweep = (y1 - cy).atan2(x1 - cx) - a0;
    if clockwise {
        if sweep >= -1e-9 {
            sweep -= 2.0 * std::f64::consts::PI;
        }
    } else if sweep <= 1e-9 {
        sweep += 2.0 * std::f64::consts::PI;
    }
    let n = ((sweep.abs() * r / CHORD).ceil() as usize).max(1);
    let mut points: Vec<(f64, f64)> = (0..=n).map(|i| {
        let a = a0 + sweep * i as f64 / n as f64;
        (cx + r * a.cos(), cy + r * a.sin())
    }).collect();
    points[n] = (x1, y1);
    points
}

impl Reader {
    fn line(&mut self, raw: &str) -> Option<Layer> {
        let line = raw.trim();
        if let Some(comment) = line.strip_prefix(';') {
            let text = comment.trim();
            let value = |prefix: &str| text.strip_prefix(prefix).map(str::trim);
            if let Some(v) = value("Z_HEIGHT:") {
                let done = self.z.map(|z| Layer { z, height: self.height, roads: std::mem::take(&mut self.roads) });
                self.z = v.parse().ok();
                return done;
            } else if let Some(v) = value("LAYER_HEIGHT:") {
                self.height = v.parse().unwrap_or(self.height);
            } else if let Some(v) = value("FEATURE:") {
                if &*self.feature != v {
                    self.feature = Rc::from(v);
                }
            } else if let Some(v) = value("LINE_WIDTH:") {
                self.width = v.parse().unwrap_or(self.width);
            } else if let Some(v) = value("OBJECT_ID:") {
                self.object = v.parse().ok();
            } else if text.starts_with("start printing object, unique label id:") {
                self.object = text.rsplit(':').next().and_then(|v| v.trim().parse().ok());
            } else if text.starts_with("stop printing object") {
                self.object = None;
            }
            return None;
        }
        let code = line.split(';').next().unwrap_or("").trim();
        let Some(command) = code.split_whitespace().next() else { return None };
        match command {
            "G90" | "G91" => {
                self.absolute = command == "G90";
                return None;
            }
            "M82" | "M83" => {
                self.relative_e = command == "M83";
                return None;
            }
            "G0" | "G1" | "G2" | "G3" | "G92" => {}
            _ => return None,
        }
        let words = words(&code[command.len()..]);
        if command == "G92" {
            self.x = word(&words, b'X').unwrap_or(self.x);
            self.y = word(&words, b'Y').unwrap_or(self.y);
            self.e = word(&words, b'E').unwrap_or(self.e);
            return None;
        }
        let nx = if self.absolute { word(&words, b'X').unwrap_or(self.x) } else { self.x + word(&words, b'X').unwrap_or(0.0) };
        let ny = if self.absolute { word(&words, b'Y').unwrap_or(self.y) } else { self.y + word(&words, b'Y').unwrap_or(0.0) };
        let de = match word(&words, b'E') {
            Some(v) => {
                let de = if self.relative_e { v } else { v - self.e };
                self.e = if self.relative_e { self.e + v } else { v };
                de
            }
            None => 0.0,
        };
        if self.z.is_some() && de > 1e-9 && (nx != self.x || ny != self.y) {
            if command == "G2" || command == "G3" {
                let points = arc(self.x, self.y, nx, ny, &words, command == "G2");
                for pair in points.windows(2) {
                    self.roads.push(Road { x0: pair[0].0, y0: pair[0].1, x1: pair[1].0, y1: pair[1].1, width: self.width,
                                           feature: self.feature.clone(), object: self.object });
                }
            } else {
                self.roads.push(Road { x0: self.x, y0: self.y, x1: nx, y1: ny, width: self.width, feature: self.feature.clone(), object: self.object });
            }
        }
        self.x = nx;
        self.y = ny;
        None
    }

    fn finish(&mut self) -> Option<Layer> {
        self.z.map(|z| Layer { z, height: self.height, roads: std::mem::take(&mut self.roads) })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn roads_follow_moves_that_extrude() {
        let gcode = b"; Z_HEIGHT: 0.2\n; LAYER_HEIGHT: 0.2\n; FEATURE: Outer wall\n; LINE_WIDTH: 0.45\nG1 X1 Y1\nG1 X2 Y1 E.05\nG1 X3 Y1\n; Z_HEIGHT: 0.44\nG1 X3 Y2 E0.1\n";
        let mut seen = Vec::new();
        layers(gcode, |layer| seen.push((layer.z, layer.height, layer.roads.len(), layer.roads.first().map(|r| (r.x0, r.x1, r.width, r.feature.to_string())))));
        assert_eq!(seen[0], (0.2, 0.2, 1, Some((1.0, 2.0, 0.45, "Outer wall".to_string()))));
        assert_eq!(seen[1].2, 1);
    }

    #[test]
    fn arcs_become_short_chords() {
        let gcode = b"; Z_HEIGHT: 0.2\nG1 X10 Y0\nG3 X-10 Y0 I-10 J0 E1\n";
        let mut count = 0;
        layers(gcode, |layer| count = layer.roads.len());
        assert_eq!(count, (std::f64::consts::PI * 10.0 / CHORD).ceil() as usize);
    }
}
