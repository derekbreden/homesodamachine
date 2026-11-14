//! Applies the PET-GF foundation cooling stage to the shaft's bridge stitch and the native
//! courses that recover on it, leaving every other byte of the sequenced plate as it was.

use crate::cooling;
use crate::json::Json;
use crate::sha256_hex;
use anyhow::{Context, Result, bail, ensure};
use serde_json::Value;
use std::io::Read;
use std::path::{Path, PathBuf};

const SETTINGS: [&str; 4] = ["filament_settings_id", "overhang_fan_speed", "filament_bridge_speed", "bridge_speed"];
const STITCH: &[u8] = b"; HSM_BRIDGE_STITCH: shaft join bridge stitch\n";
const UPPER: &[u8] = b"; HSM_PHASE: native level upper base\n";
const BASE: &[u8] = b"; OBJECT_ID: 1901\n";
const MARKER: &[u8] = b"; HSM bridge-foundation cooling";
const TAIL: &[u8] = b"; HSM bridge-foundation result: ";
const TRAVEL: &[u8] = b"; HSM_PHASE_TRAVEL:";
/// The scalars the cooling depth is read from, under the checkout.
pub const CATALOG: &str = "tools/hsm/shared-data/catalog/scalars.json";

fn find(hay: &[u8], needle: &[u8], from: usize) -> Option<usize> {
    if needle.is_empty() || hay.len() < needle.len() {
        return None;
    }
    (from..=hay.len() - needle.len()).find(|&i| &hay[i..i + needle.len()] == needle)
}

fn count(hay: &[u8], needle: &[u8]) -> usize {
    let (mut n, mut at) = (0, 0);
    while let Some(i) = find(hay, needle, at) {
        n += 1;
        at = i + needle.len();
    }
    n
}

/// Each course's start and slice height, where a line reads `; CHANGE_LAYER` and the next
/// `; Z_HEIGHT: ` with digits.
fn layers(raw: &[u8]) -> Vec<(usize, f64)> {
    let head = b"; CHANGE_LAYER\n; Z_HEIGHT: ";
    let mut out = Vec::new();
    let mut at = 0;
    while let Some(i) = find(raw, head, at) {
        at = i + 1;
        if i > 0 && raw[i - 1] != b'\n' {
            continue;
        }
        let digits = raw[i + head.len()..].iter().take_while(|c| c.is_ascii_digit() || **c == b'.').count();
        let end = i + head.len() + digits;
        if digits == 0 || raw.get(end) != Some(&b'\n') {
            continue;
        }
        if let Ok(z) = std::str::from_utf8(&raw[i + head.len()..end]).unwrap_or("").parse() {
            out.push((i, z));
            at = end + 1;
        }
    }
    out
}

/// The stitch course and the upper courses within the foundation depth above it: its start,
/// end and first upper course, and their heights.
fn local_window(raw: &[u8], depth: f64) -> Result<(usize, usize, usize, Vec<f64>)> {
    ensure!(count(raw, STITCH) == 1, "Expected one shaft bridge stitch marker");
    let marker = find(raw, STITCH, 0).context("the stitch marker")?;
    let layers = layers(raw);
    let stitch = layers.iter().rposition(|(start, _)| *start < marker).context("no course before the stitch")?;
    let stitch_z = layers[stitch].1;
    let end_index = (stitch + 1..layers.len()).find(|&i| layers[i].1 > stitch_z + depth + 1e-6)
        .context("no course above the recovery depth")?;
    for i in stitch + 1..end_index {
        let band = &raw[layers[i].0..layers[i + 1].0];
        ensure!(find(band, UPPER, 0).is_some() && find(band, BASE, 0).is_some(),
            "The recovery window must contain only original upper base courses");
    }
    Ok((layers[stitch].0, layers[end_index].0, layers[stitch + 1].0, layers[stitch..end_index].iter().map(|l| l.1).collect()))
}

/// Python's `bytes.splitlines`.
fn split_lines(data: &[u8]) -> Vec<&[u8]> {
    let mut out = Vec::new();
    let (mut start, mut i) = (0, 0);
    while i < data.len() {
        match data[i] {
            b'\n' => {
                out.push(&data[start..i]);
                start = i + 1;
            }
            b'\r' => {
                out.push(&data[start..i]);
                if data.get(i + 1) == Some(&b'\n') {
                    i += 1;
                }
                start = i + 1;
            }
            _ => {}
        }
        i += 1;
    }
    if start < data.len() {
        out.push(&data[start..]);
    }
    out
}

/// Each ` F` word a line carries, as `(start, end)` of the word, where a run of digits, points
/// and minus signs follows the `F` and ends the line or meets white space.
fn feed_words(line: &[u8]) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    let mut i = 0;
    while i + 1 < line.len() {
        if line[i] == b' ' && line[i + 1] == b'F' {
            let run = line[i + 2..].iter().take_while(|c| c.is_ascii_digit() || **c == b'.' || **c == b'-').count();
            let end = i + 2 + run;
            if run > 0 && (end == line.len() || line[end].is_ascii_whitespace() || line[end] == 0x0b) {
                out.push((i, end));
                i = end;
                continue;
            }
        }
        i += 1;
    }
    out
}

fn replace_feeds(data: &[u8], mut with: impl FnMut(&[u8]) -> Vec<u8>) -> Vec<u8> {
    let mut out = Vec::with_capacity(data.len());
    let mut last = 0;
    for (a, b) in feed_words(data) {
        out.extend_from_slice(&data[last..a]);
        out.extend(with(&data[a + 2..b]));
        last = b;
    }
    out.extend_from_slice(&data[last..]);
    out
}

/// The motion lines with their feeds removed, which the cooling must leave unchanged.
fn motion_without_feed(data: &[u8]) -> Vec<Vec<u8>> {
    split_lines(data).into_iter()
        .filter(|l| [b"G0 ", b"G1 ", b"G2 ", b"G3 "].iter().any(|p| l.starts_with(*p)) && !l.starts_with(b"G1 F"))
        .map(|l| replace_feeds(l, |_| Vec::new()))
        .collect()
}

/// The feeds rewritten as `%g`, so a feed the cooling only reformats compares equal.
fn normalize_feed(data: &[u8]) -> Vec<u8> {
    replace_feeds(data, |run| {
        let value: f64 = std::str::from_utf8(run).ok().and_then(|s| s.parse().ok()).unwrap_or(f64::NAN);
        let mut word = b" F".to_vec();
        word.extend(crate::python_text::g(value).into_bytes());
        word
    })
}

/// The cooling stage's settings for the project's filament slots.
fn settings(project: &Path) -> Result<Value> {
    let mut zip = zip::ZipArchive::new(std::fs::File::open(project).with_context(|| format!("opening {}", project.display()))?)?;
    let mut text = String::new();
    zip.by_name("Metadata/project_settings.config")?.read_to_string(&mut text)?;
    let all: Value = serde_json::from_str(&text)?;
    let mut out = serde_json::Map::new();
    for key in SETTINGS {
        let value = all.get(key).with_context(|| format!("the project has no {key}"))?;
        out.insert(key.into(), match value {
            Value::Array(_) => value.clone(),
            other => Value::Array(vec![other.clone()]),
        });
    }
    Ok(Value::Object(out))
}

/// Cools the stitch and its recovery courses in `source` with the project's PET-GF slots and
/// writes `output`, its recovery report and the sequenced report with the cooled plate's hash.
pub fn cool_shaft_join(source: &Path, project: &Path, output: &Path, catalog: &Path) -> Result<()> {
    let raw = std::fs::read(source).with_context(|| format!("reading {}", source.display()))?;
    let schedule_path = source.with_extension("json");
    let mut schedule = Json::parse(&std::fs::read_to_string(&schedule_path).with_context(|| format!("reading {}", schedule_path.display()))?)?;
    let before = sha256_hex(&raw);
    ensure!(schedule.get("sequenced_gcode_sha256").and_then(Json::text) == Some(before.as_str()), "Uncooled schedule and G-code differ");
    let scalars: Value = serde_json::from_slice(&std::fs::read(catalog).with_context(|| format!("reading {}", catalog.display()))?)?;
    let depth = scalars["petgf_cooling"]["FOUNDATION"]["height_mm"].as_f64().context("the foundation's cooling depth")?;
    let (start, end, first_native, levels) = local_window(&raw, depth)?;
    let original = &raw[start..end];
    let settings = settings(project)?;
    let parent = output.parent().map(Path::to_path_buf).unwrap_or_else(|| PathBuf::from("."));
    let scratch = parent.join(format!(".shaft-join-cooling-{}", std::process::id()));
    std::fs::create_dir_all(&scratch)?;
    let result = (|| -> Result<(Value, Vec<u8>)> {
        let window = scratch.join("shaft-bridge-window.gcode");
        let cooled = scratch.join("shaft-bridge-window.gcode.cooling");
        std::fs::write(&window, original)?;
        let report = cooling::foundation(&window, &cooled, &settings)?;
        ensure!(report["changed"].as_bool() == Some(true), "Canonical cooling did not find any covered recovery roads");
        Ok((report, std::fs::read(&cooled)?))
    })();
    let _ = std::fs::remove_dir_all(&scratch);
    let (report, written) = result?;
    let newline = written.iter().position(|b| *b == b'\n').context("the cooling stage wrote no marker")?;
    let (marker, modified) = (&written[..newline], &written[newline + 1..]);
    if marker != MARKER || count(modified, TAIL) != 1 {
        bail!("Unrecognized canonical foundation stage output");
    }
    let modified = &modified[..find(modified, TAIL, 0).unwrap_or(modified.len())];
    let rest = &original[first_native - start..];
    let native_marker = &rest[..find(rest, TRAVEL, 0).unwrap_or(rest.len())];
    ensure!(count(modified, native_marker) == 1, "Canonical stage changed the first upper layer marker");
    let native_start = find(modified, native_marker, 0).unwrap_or(0);
    let seed = &original[..first_native - start];
    ensure!(normalize_feed(&modified[..native_start]) == normalize_feed(seed), "Canonical stage changed the stitch seed course");
    let modified: Vec<u8> = [seed, &modified[native_start..]].concat();
    ensure!(motion_without_feed(original) == motion_without_feed(&modified), "Foundation cooling changed motion geometry or extrusion");
    let combined: Vec<u8> = [&raw[..start], &modified[..], &raw[end..]].concat();
    std::fs::write(output, &combined).with_context(|| format!("writing {}", output.display()))?;
    let mut report = Json::from_value(&report);
    let lines = |upto: usize| raw[..upto].iter().filter(|b| **b == b'\n').count() as i64;
    let project_bytes = std::fs::read(project)?;
    for (key, value) in [
        ("source_sha256", Json::Text(before.clone())),
        ("output_sha256", Json::Text(sha256_hex(&combined))),
        ("source_project_sha256", Json::Text(sha256_hex(&project_bytes))),
        ("stitch_and_recovery_z_mm", Json::List(levels.iter().map(|z| Json::Number(crate::json::python_number(*z), *z)).collect())),
        ("start_line", Json::Number((lines(start) + 1).to_string(), (lines(start) + 1) as f64)),
        ("last_source_line", Json::Number(lines(end).to_string(), lines(end) as f64)),
        ("scope_geometry_and_extrusion_verified", Json::Bool(true)),
        ("outside_scope_bytes_retained", Json::Bool(true)),
    ] {
        report.set(key, value);
    }
    let recovery = output.with_extension("recovery.json");
    std::fs::write(&recovery, report.dumps() + "\n").with_context(|| format!("writing {}", recovery.display()))?;
    let output_hash = report.get("output_sha256").cloned().context("the output hash")?;
    schedule.set("sequenced_gcode_sha256", output_hash);
    schedule.set("pre_recovery_gcode_sha256", Json::Text(before));
    schedule.set("shaft_join_recovery", report);
    let cooled = output.with_extension("json");
    std::fs::write(&cooled, schedule.dumps() + "\n").with_context(|| format!("writing {}", cooled.display()))?;
    Ok(())
}
