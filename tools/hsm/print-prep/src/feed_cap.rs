//! Holds the rebuilt tip's mapped linear courses to the filament profile's volumetric flow limit.
//!
//! A deposit's commanded feed is lowered where it would exceed the limit, and nothing else in
//! the plate changes. The capped plate is then bound to the course groups of the plate it came
//! from.

use crate::course_field::distance;
use crate::gcode::words;
use anyhow::{bail, ensure, Context, Result};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::f64::consts::PI;
use std::fs;
use std::path::Path;

const PURPOSE: &str = "Limit commanded volumetric flow in the rebuilt tip's linear courses.";
const PHASE: &str = "; HSM_PHASE: ";
const START: &str = "; start printing object, unique label id: ";
const STOP: &str = "; stop printing object, unique label id: ";
const MODEL_START: &str = "; MACHINE_START_GCODE_END";
const MODEL_END: &str = "; MACHINE_END_GCODE_START";
const MAPPED: [&str; 3] = ["tip shoulder entry", "tip yellow shoulder", "tip shoulder fade"];
const CAP_LINE: &str = "; filament_max_volumetric_speed = ";
const DIAMETER_LINE: &str = "; filament_diameter = ";
const TIP_ID: i64 = 1902;

/// The first value of a header setting.
fn config_number(value: &str) -> Result<f64> {
    Ok(value.split(',').next().unwrap_or(value).trim().parse()?)
}

/// Where each feed word of `code` starts and ends.
fn feed_words(code: &str) -> Vec<(usize, usize)> {
    let mut found = Vec::new();
    let mut at = 0;
    for word in code.split(' ') {
        if word.starts_with('F') {
            found.push((at, at + word.trim_end().len()));
        }
        at += word.len() + 1;
    }
    found
}

fn get(args: &[(u8, f64)], key: u8) -> Option<f64> {
    args.iter().find(|(k, _)| *k == key).map(|(_, v)| *v)
}

fn extra_flow(area: f64, length_extruded: f64, distance: f64, feed: f64, speed: f64, extrusion: f64) -> f64 {
    area * length_extruded * feed * speed * extrusion / (60. * distance)
}

/// The plate with its mapped tip deposits' feeds capped, written to `output` with its receipt
/// beside it. The receipt is returned.
pub fn cap(source: &Path, output: &Path) -> Result<Value> {
    ensure!(!output.exists() || fs::canonicalize(source)? != fs::canonicalize(output)?, "Preserve original tape");
    let data = fs::read_to_string(source).with_context(|| format!("reading {}", source.display()))?;
    let mut out = String::with_capacity(data.len());
    let mut counts: BTreeMap<String, i64> = BTreeMap::new();
    let mut delta_seconds: BTreeMap<String, f64> = BTreeMap::new();
    let mut min_feed: Option<f64> = None;
    let (mut used_cap, mut diameter): (Option<f64>, Option<f64>) = (None, None);
    let mut world = [0.; 3];
    let mut offset = [0.; 3];
    let (mut original_feed, mut emitted_feed, mut speed, mut extrusion) = (0., 0., 1., 1.);
    let (mut began, mut absolute, mut relative_e) = (false, true, false);
    let (mut obj, mut phase): (Option<i64>, &str) = (None, "");
    let (mut retract_debt, mut current_e) = (0., 0.);
    let mut area = 0.;
    let mut first_changed: Option<usize> = None;
    let mut worst_output_flow = 0.;
    for (index, line) in data.split_inclusive('\n').enumerate() {
        let n = index + 1;
        if line.starts_with(';') {
            if let Some(value) = line.strip_prefix(CAP_LINE) {
                used_cap = Some(config_number(value)?);
            } else if let Some(value) = line.strip_prefix(DIAMETER_LINE) {
                diameter = Some(config_number(value)?);
            } else if line.starts_with(MODEL_START) {
                began = true;
                match (used_cap, diameter) {
                    (Some(cap), Some(d)) if cap > 0. && d > 0. => area = PI * (d / 2.).powi(2),
                    _ => bail!("Print profile is missing physical flow inputs"),
                }
                retract_debt = 0.;
            } else if line.starts_with(MODEL_END) {
                began = false;
            } else if let Some(id) = line.strip_prefix(START) {
                obj = Some(id.trim().parse()?);
            } else if line.starts_with(STOP) {
                obj = None;
            } else if let Some(name) = line.strip_prefix(PHASE) {
                phase = name.trim();
            }
            out.push_str(line);
            continue;
        }
        let (code, rest_of_line) = line.split_at(line.find(';').unwrap_or(line.len()));
        let cmd = code.split_whitespace().next().unwrap_or("");
        match cmd {
            "G90" => absolute = true,
            "G91" => absolute = false,
            "M82" | "M83" => relative_e = cmd == "M83",
            _ => {}
        }
        if !matches!(cmd, "G0" | "G1" | "G2" | "G3" | "G92" | "M220" | "M221") {
            out.push_str(line);
            continue;
        }
        let args = words(&code.trim_start()[cmd.len()..]);
        if cmd == "M220" {
            speed = get(&args, b'S').unwrap_or(100.) / 100.;
        } else if cmd == "M221" {
            extrusion = get(&args, b'S').unwrap_or(100.) / 100.;
        } else if cmd == "G92" {
            for (axis, key) in [b'X', b'Y', b'Z'].into_iter().enumerate() {
                offset[axis] = world[axis] - get(&args, key).unwrap_or(world[axis] - offset[axis]);
            }
            current_e = get(&args, b'E').unwrap_or(current_e);
        } else {
            let endpoint: [f64; 3] = std::array::from_fn(|axis| {
                let key = [b'X', b'Y', b'Z'][axis];
                if absolute {
                    get(&args, key).unwrap_or(world[axis] - offset[axis]) + offset[axis]
                } else {
                    world[axis] + get(&args, key).unwrap_or(0.)
                }
            });
            let delta_e = if relative_e { get(&args, b'E').unwrap_or(0.) } else { get(&args, b'E').unwrap_or(current_e) - current_e };
            current_e += delta_e;
            let net = delta_e - retract_debt;
            retract_debt = (retract_debt - delta_e).max(0.);
            original_feed = get(&args, b'F').unwrap_or(original_feed);
            emitted_feed = get(&args, b'F').unwrap_or(emitted_feed);
            let scoped = began && obj == Some(TIP_ID) && MAPPED.contains(&phase);
            let moved = world != endpoint;
            if scoped && net > 1e-9 && (moved || cmd == "G2" || cmd == "G3") {
                if !(cmd == "G0" || cmd == "G1") || get(&args, b'F').is_none() || !relative_e || !absolute {
                    bail!("Mapped deposition must be explicit-feed absolute linear pose: {n}");
                }
                ensure!(original_feed.min(speed).min(extrusion) > 0., "Invalid deposition feed or flow override: {n}");
                let used = used_cap.context("No flow limit")?;
                let d = distance(world, endpoint);
                let cap = 60. * used * d / (area * net * speed * extrusion);
                if original_feed > cap {
                    // Rounding downward preserves the cap even for very short rounded moves.
                    emitted_feed = (cap * 100.).floor() / 100.;
                    ensure!(emitted_feed > 0., "Cannot represent positive capped feed at line {n}");
                    let feeds = feed_words(code);
                    ensure!(feeds.len() == 1, "Expected one explicit feed token at line {n}");
                    let (start, end) = feeds[0];
                    out.push_str(&code[..start]);
                    out.push_str(&format!("F{emitted_feed:.2}"));
                    out.push_str(&code[end..]);
                    out.push_str(rest_of_line);
                    *counts.entry(phase.to_string()).or_default() += 1;
                    *delta_seconds.entry(phase.to_string()).or_default() += 60. * d / speed * (1. / emitted_feed - 1. / original_feed);
                    min_feed = Some(min_feed.map_or(emitted_feed, |m: f64| m.min(emitted_feed)));
                    first_changed.get_or_insert(n);
                    worst_output_flow = extra_flow(area, net, d, emitted_feed, speed, extrusion).max(worst_output_flow);
                    world = endpoint;
                    continue;
                }
                worst_output_flow = extra_flow(area, net, d, emitted_feed, speed, extrusion).max(worst_output_flow);
            } else if began && emitted_feed != original_feed && (moved || delta_e != 0.) {
                bail!("Capped modal feed would leak to untouched movement at line {n}");
            }
            world = endpoint;
        }
        out.push_str(line);
    }
    ensure!(used_cap.is_none_or(|c| worst_output_flow <= c + 1e-8), "An above-cap mapped rate survived");
    let receipt = json!({
        "purpose": PURPOSE,
        "profile_cap_mm3_s": used_cap,
        "filament_diameter_mm": diameter,
        "source_gcode_sha256": crate::sha256_hex(data.as_bytes()),
        "gcode_sha256": crate::sha256_hex(out.as_bytes()),
        "capped_moves_by_phase": counts,
        "feed_only_additional_seconds_by_phase": delta_seconds,
        "minimum_capped_feed_mm_min": min_feed,
        "maximum_nominal_output_flow_mm3_s": worst_output_flow,
        "first_changed_gcode_line": first_changed,
        "identifies_only_explicit_feed_words_in_mapped_linear_tip_deposition": true,
        "prior_nose_and_nontip_gcode_byte_identical": true,
        "scope": "Compares flow at commanded feed and tightened scope from the source header filament settings.",
    });
    fs::write(output, &out)?;
    fs::write(output.with_extension("json"), serde_json::to_string_pretty(&receipt)? + "\n")?;
    Ok(receipt)
}

/// The capped plate copied to `output`, with the uncapped plate's course-group report carried
/// beside it under the capped plate's hash. The capped plate's hash is returned.
pub fn bind(uncapped: &Path, capped: &Path, output: &Path, clamp_receipt: Option<&Path>) -> Result<String> {
    let mut geometry: Value = serde_json::from_slice(&fs::read(uncapped.with_extension("json"))?)?;
    let source_sha = crate::sha256_hex(&fs::read(uncapped)?);
    ensure!(geometry["sequenced_gcode_sha256"] == source_sha.as_str(), "Original tape and course geometry do not match");
    let capped_data = fs::read(capped)?;
    let capped_sha = crate::sha256_hex(&capped_data);
    ensure!(source_sha != capped_sha, "Capped and uncapped inputs are identical");
    if let Some(receipt) = clamp_receipt {
        let bytes = fs::read(receipt)?;
        let verify = String::from_utf8_lossy(&bytes);
        ensure!(verify.contains(&source_sha) && verify.contains(&capped_sha), "Clamp receipt does not cover this tape pair");
        geometry["mapped_speed_cap_receipt_sha256"] = json!(crate::sha256_hex(&bytes));
    }
    geometry["pre_cap_gcode_sha256"] = json!(source_sha);
    geometry["sequenced_gcode_sha256"] = json!(capped_sha);
    if capped != output {
        fs::write(output, &capped_data)?;
    }
    let emitted = capped_data.split_inclusive(|c| *c == b'\n').filter(|l| *l == b"; CHANGE_LAYER\n").count();
    let groups = geometry["groups"].as_array().context("The course geometry has no groups")?.len();
    ensure!(emitted == groups, "The feed clamp changed course group boundaries");
    fs::write(output.with_extension("json"), serde_json::to_string_pretty(&geometry)? + "\n")?;
    Ok(capped_sha)
}
