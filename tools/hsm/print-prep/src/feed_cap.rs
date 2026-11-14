//! Holds the rebuilt tip's mapped linear courses to the filament profile's volumetric flow limit.
//!
//! A deposit's commanded feed is lowered where it would exceed the limit, and nothing else in
//! the plate changes. The capped plate is then bound to the course groups of the plate it came
//! from.

use crate::python_text::{dist, Json};
use anyhow::{bail, ensure, Context, Result};
use std::f64::consts::PI;
use std::fs;
use std::path::Path;

const PURPOSE: &str = "Limit commanded volumetric flow in the rebuilt tip's linear courses.";
const PHASE: &[u8] = b"; HSM_PHASE: ";
const START: &[u8] = b"; start printing object, unique label id: ";
const STOP: &[u8] = b"; stop printing object, unique label id: ";
const MODEL_START: &[u8] = b"; MACHINE_START_GCODE_END";
const MODEL_END: &[u8] = b"; MACHINE_END_GCODE_START";
const MAPPED: [&[u8]; 3] = [b"tip shoulder entry", b"tip yellow shoulder", b"tip shoulder fade"];
const CAP_LINE: &[u8] = b"; filament_max_volumetric_speed = ";
const DIAMETER_LINE: &[u8] = b"; filament_diameter = ";
const TIP_ID: i64 = 1902;

fn is_space(c: u8) -> bool {
    matches!(c, b' ' | b'\t' | b'\n' | b'\r' | b'\x0b' | b'\x0c')
}

/// `bytes.strip()`.
fn strip(text: &[u8]) -> &[u8] {
    let start = text.iter().position(|c| !is_space(*c)).unwrap_or(text.len());
    let end = text.iter().rposition(|c| !is_space(*c)).map_or(start, |i| i + 1);
    &text[start..end.max(start)]
}

fn parse<T: std::str::FromStr>(text: &[u8]) -> Result<T>
where
    T::Err: std::error::Error + Send + Sync + 'static,
{
    Ok(std::str::from_utf8(strip(text))?.parse::<T>()?)
}

/// The first value of a header setting.
fn config_number(line: &[u8], prefix: &[u8]) -> Result<f64> {
    let value = strip(&line[prefix.len()..]);
    parse(value.split(|c| *c == b',').next().unwrap_or(value))
}

fn word_char(c: u8) -> bool {
    c.is_ascii_alphanumeric() || c == b'_'
}

/// The length of a signed number with optional point and digits, or a point and digits.
fn number_length(text: &[u8]) -> Option<usize> {
    let mut at = usize::from(matches!(text.first(), Some(b'-' | b'+')));
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

/// Each word starting a word: a letter from `letters` after a non-word character, and its
/// number, as `(start, letter, end)`.
fn words(code: &[u8], letters: &[u8]) -> Vec<(usize, u8, usize)> {
    let mut found = Vec::new();
    let mut at = 0;
    while at < code.len() {
        if letters.contains(&code[at]) && (at == 0 || !word_char(code[at - 1])) {
            if let Some(length) = number_length(&code[at + 1..]) {
                found.push((at, code[at], at + 1 + length));
                at += 1 + length;
                continue;
            }
        }
        at += 1;
    }
    found
}

fn arguments(rest: &[u8]) -> Result<Vec<(u8, f64)>> {
    let mut args: Vec<(u8, f64)> = Vec::new();
    for (start, letter, end) in words(rest, b"XYZEFS") {
        let value: f64 = parse(&rest[start + 1..end])?;
        match args.iter_mut().find(|(k, _)| *k == letter) {
            Some(slot) => slot.1 = value,
            None => args.push((letter, value)),
        }
    }
    Ok(args)
}

fn get(args: &[(u8, f64)], key: u8) -> Option<f64> {
    args.iter().find(|(k, _)| *k == key).map(|(_, v)| *v)
}

/// `code.split(None, 1)`.
fn split_command(code: &[u8]) -> Option<(&[u8], &[u8])> {
    let start = code.iter().position(|c| !is_space(*c))?;
    let length = code[start..].iter().position(|c| is_space(*c)).unwrap_or(code.len() - start);
    let command = &code[start..start + length];
    let rest = &code[start + length..];
    let rest_start = rest.iter().position(|c| !is_space(*c)).unwrap_or(rest.len());
    Some((command, &rest[rest_start..]))
}

fn extra_flow(area: f64, length_extruded: f64, distance: f64, feed: f64, speed: f64, extrusion: f64) -> f64 {
    area * length_extruded * feed * speed * extrusion / (60. * distance)
}

fn add(rows: &mut Vec<(String, Json)>, key: &str, amount: Json) {
    match (rows.iter_mut().find(|(k, _)| k == key), amount) {
        (Some((_, Json::Int(total))), Json::Int(more)) => *total += more,
        (Some((_, Json::Float(total))), Json::Float(more)) => *total += more,
        (Some(_), _) => {}
        (None, Json::Float(more)) => rows.push((key.to_string(), Json::Float(0.0 + more))),
        (None, amount) => rows.push((key.to_string(), amount)),
    }
}

/// The plate with its mapped tip deposits' feeds capped, written to `output` with its receipt
/// beside it. The receipt is returned.
pub fn cap(source: &Path, output: &Path) -> Result<Json> {
    ensure!(!output.exists() || fs::canonicalize(source)? != fs::canonicalize(output)?, "Preserve original tape");
    let data = fs::read(source)?;
    let mut out: Vec<u8> = Vec::with_capacity(data.len());
    let mut counts: Vec<(String, Json)> = Vec::new();
    let mut delta_seconds: Vec<(String, Json)> = Vec::new();
    let mut min_feed: Option<f64> = None;
    let (mut used_cap, mut diameter): (Option<f64>, Option<f64>) = (None, None);
    let mut world = [0.; 3];
    let mut offset = [0.; 3];
    let (mut original_feed, mut emitted_feed, mut speed, mut extrusion) = (0., 0., 1., 1.);
    let (mut began, mut absolute, mut relative_e) = (false, true, false);
    let (mut obj, mut phase): (Option<i64>, &[u8]) = (None, b"");
    let (mut retract_debt, mut current_e) = (0., 0.);
    let mut area = 0.;
    let mut first_changed: Option<usize> = None;
    let mut worst_output_flow = 0.;
    for (index, line) in data.split_inclusive(|c| *c == b'\n').enumerate() {
        let n = index + 1;
        if line.starts_with(b";") {
            if line.starts_with(CAP_LINE) {
                used_cap = Some(config_number(line, CAP_LINE)?);
            } else if line.starts_with(DIAMETER_LINE) {
                diameter = Some(config_number(line, DIAMETER_LINE)?);
            } else if line.starts_with(MODEL_START) {
                began = true;
                match (used_cap, diameter) {
                    (Some(cap), Some(d)) if cap > 0. && d > 0. => area = PI * (d / 2.).powf(2.),
                    _ => bail!("Print profile is missing physical flow inputs"),
                }
                retract_debt = 0.;
            } else if line.starts_with(MODEL_END) {
                began = false;
            } else if line.starts_with(START) {
                obj = Some(parse(&line[START.len()..])?);
            } else if line.starts_with(STOP) {
                obj = None;
            } else if line.starts_with(PHASE) {
                phase = strip(&line[PHASE.len()..]);
            }
            out.extend_from_slice(line);
            continue;
        }
        let split = line.iter().position(|c| *c == b';').unwrap_or(line.len());
        let (code, rest_of_line) = line.split_at(split);
        let Some((cmd, rest)) = split_command(code) else {
            out.extend_from_slice(line);
            continue;
        };
        match cmd {
            b"G90" => absolute = true,
            b"G91" => absolute = false,
            b"M82" | b"M83" => relative_e = cmd == b"M83",
            _ => {}
        }
        if !matches!(cmd, b"G0" | b"G1" | b"G2" | b"G3" | b"G92" | b"M220" | b"M221") {
            out.extend_from_slice(line);
            continue;
        }
        let args = arguments(rest)?;
        if cmd == b"M220" {
            speed = get(&args, b'S').unwrap_or(100.) / 100.;
        } else if cmd == b"M221" {
            extrusion = get(&args, b'S').unwrap_or(100.) / 100.;
        } else if cmd == b"G92" {
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
            let debt = retract_debt - delta_e;
            retract_debt = if debt > 0. { debt } else { 0. };
            original_feed = get(&args, b'F').unwrap_or(original_feed);
            emitted_feed = get(&args, b'F').unwrap_or(emitted_feed);
            let scoped = began && obj == Some(TIP_ID) && MAPPED.contains(&phase);
            let moved = world != endpoint;
            if scoped && net > 1e-9 && (moved || cmd == b"G2" || cmd == b"G3") {
                if !(cmd == b"G0" || cmd == b"G1") || get(&args, b'F').is_none() || !relative_e || !absolute {
                    bail!("Mapped deposition must be explicit-feed absolute linear pose: {n}");
                }
                let least = [original_feed, speed, extrusion].into_iter().reduce(|a, b| if b < a { b } else { a }).unwrap();
                ensure!(least > 0., "Invalid deposition feed or flow override: {n}");
                let used = used_cap.context("No flow limit")?;
                let d = dist(&world, &endpoint);
                let cap = 60. * used * d / (area * net * speed * extrusion);
                if original_feed > cap {
                    // Rounding downward preserves the cap even for very short rounded moves.
                    emitted_feed = (cap * 100.).floor() / 100.;
                    ensure!(emitted_feed > 0., "Cannot represent positive capped feed at line {n}");
                    let feeds = words(code, b"F");
                    ensure!(feeds.len() == 1, "Expected one explicit feed token at line {n}");
                    let (start, _, end) = feeds[0];
                    let text = format!("F{emitted_feed:.2}");
                    out.extend_from_slice(&code[..start]);
                    out.extend_from_slice(text.as_bytes());
                    out.extend_from_slice(&code[end..]);
                    out.extend_from_slice(rest_of_line);
                    let key = String::from_utf8_lossy(phase).into_owned();
                    add(&mut counts, &key, Json::Int(1));
                    add(&mut delta_seconds, &key, Json::Float(60. * d / speed * (1. / emitted_feed - 1. / original_feed)));
                    min_feed = Some(match min_feed {
                        Some(m) if emitted_feed < m => emitted_feed,
                        Some(m) => m,
                        None => emitted_feed,
                    });
                    first_changed.get_or_insert(n);
                    let flow = extra_flow(area, net, d, emitted_feed, speed, extrusion);
                    if flow > worst_output_flow {
                        worst_output_flow = flow;
                    }
                    world = endpoint;
                    continue;
                }
                let flow = extra_flow(area, net, d, emitted_feed, speed, extrusion);
                if flow > worst_output_flow {
                    worst_output_flow = flow;
                }
            } else if began && emitted_feed != original_feed && (moved || delta_e != 0.) {
                bail!("Capped modal feed would leak to untouched movement at line {n}");
            }
            world = endpoint;
        }
        out.extend_from_slice(line);
    }
    let used_cap = used_cap.map_or(Json::Null, Json::Float);
    ensure!(!matches!(used_cap, Json::Float(c) if worst_output_flow > c + 1e-8), "An above-cap mapped rate survived");
    let receipt = Json::Dict(vec![
        ("purpose".into(), Json::Str(PURPOSE.into())),
        ("profile_cap_mm3_s".into(), used_cap),
        ("filament_diameter_mm".into(), diameter.map_or(Json::Null, Json::Float)),
        ("source_gcode_sha256".into(), Json::Str(crate::sha256_hex(&data))),
        ("gcode_sha256".into(), Json::Str(crate::sha256_hex(&out))),
        ("capped_moves_by_phase".into(), Json::Dict(counts)),
        ("feed_only_additional_seconds_by_phase".into(), Json::Dict(delta_seconds)),
        ("minimum_capped_feed_mm_min".into(), min_feed.map_or(Json::Null, Json::Float)),
        ("maximum_nominal_output_flow_mm3_s".into(), Json::Float(worst_output_flow)),
        ("first_changed_gcode_line".into(), first_changed.map_or(Json::Null, |n| Json::Int(n as i64))),
        ("identifies_only_explicit_feed_words_in_mapped_linear_tip_deposition".into(), Json::Bool(true)),
        ("prior_nose_and_nontip_gcode_byte_identical".into(), Json::Bool(true)),
        ("scope".into(), Json::Str("Compares flow at commanded feed and tightened scope from the source header filament settings.".into())),
    ]);
    fs::write(output, &out)?;
    fs::write(output.with_extension("json"), receipt.dumps_indented() + "\n")?;
    Ok(receipt)
}

/// The capped plate copied to `output`, with the uncapped plate's course-group report carried
/// beside it under the capped plate's hash. The capped plate's hash is returned.
pub fn bind(uncapped: &Path, capped: &Path, output: &Path, clamp_receipt: Option<&Path>) -> Result<String> {
    let mut geometry = Json::loads(&fs::read_to_string(uncapped.with_extension("json"))?)?;
    let source_sha = crate::sha256_hex(&fs::read(uncapped)?);
    ensure!(geometry.get("sequenced_gcode_sha256") == Some(&Json::Str(source_sha.clone())), "Original tape and course geometry do not match");
    let capped_data = fs::read(capped)?;
    let capped_sha = crate::sha256_hex(&capped_data);
    ensure!(source_sha != capped_sha, "Capped and uncapped inputs are identical");
    if let Some(receipt) = clamp_receipt {
        let bytes = fs::read(receipt)?;
        let verify = String::from_utf8_lossy(&bytes);
        ensure!(verify.contains(&source_sha) && verify.contains(&capped_sha), "Clamp receipt does not cover this tape pair");
        geometry.set("mapped_speed_cap_receipt_sha256", Json::Str(crate::sha256_hex(&bytes)));
    }
    geometry.set("pre_cap_gcode_sha256", Json::Str(source_sha));
    geometry.set("sequenced_gcode_sha256", Json::Str(capped_sha.clone()));
    if capped != output {
        fs::write(output, &capped_data)?;
    }
    let emitted = capped_data.split_inclusive(|c| *c == b'\n').filter(|l| *l == b"; CHANGE_LAYER\n").count();
    let Some(Json::List(groups)) = geometry.get("groups") else { bail!("The course geometry has no groups") };
    ensure!(emitted == groups.len(), "The feed clamp changed course group boundaries");
    fs::write(output.with_extension("json"), geometry.dumps_indented() + "\n")?;
    Ok(capped_sha)
}
