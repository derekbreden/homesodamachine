//! Packages a trial plate as a print-only Mark2 archive bound to its sequenced motion.
//!
//! The native slice's archive supplies everything else: the archive carries the sequenced
//! G-code with its estimates and filament, and leaves out the editable geometry.

use crate::xml::{document, parse};
use anyhow::{bail, ensure, Context, Result};
use serde_json::{json, Value};
use std::f64::consts::PI;
use std::fs;
use std::io::{Read, Write};
use std::path::Path;

const GCODE: &str = "Metadata/plate_1.gcode";
const SLICE: &str = "Metadata/slice_info.config";
const LAYOUT: &str = "Metadata/plate_1.json";
const MODEL: &str = "3D/3dmodel.model";
const SETTINGS: &str = "Metadata/model_settings.config";

fn duration(seconds: f64) -> String {
    let total = seconds.ceil() as i64;
    format!("{}h {}m {}s", total / 3600, total / 60 % 60, total % 60)
}

/// The first header line that is `key` followed by a plain decimal.
fn header_number(gcode: &[u8], key: &str) -> Result<f64> {
    for line in gcode.split(|b| *b == b'\n') {
        if let Some(value) = line.strip_prefix(key.as_bytes()) {
            if !value.is_empty() && value.iter().all(|c| *c == b'.' || c.is_ascii_digit()) {
                return Ok(std::str::from_utf8(value)?.parse()?);
            }
        }
    }
    bail!("The G-code has no {key:?}")
}

/// The G-code with the first line starting `key` made `line`.
fn replace_line(gcode: &[u8], key: &str, line: &str) -> Result<Vec<u8>> {
    let mut at = 0;
    while at <= gcode.len() {
        let end = gcode[at..].iter().position(|b| *b == b'\n').map_or(gcode.len(), |i| at + i);
        if gcode[at..end].starts_with(key.as_bytes()) {
            return Ok([&gcode[..at], line.as_bytes(), &gcode[end..]].concat());
        }
        at = end + 1;
    }
    bail!("The Bambu header has no {key:?}")
}

/// The startup's progress events, showing the remaining minutes of the sequenced motion.
fn startup_progress(gcode: &[u8], minutes: i64) -> Result<Vec<u8>> {
    const MARK: &[u8] = b"; MACHINE_START_GCODE_END\n";
    let split = gcode.windows(MARK.len()).position(|w| w == MARK).context("The G-code has no startup end")?;
    let mut out = Vec::with_capacity(gcode.len());
    for line in gcode[..split].split_inclusive(|b| *b == b'\n') {
        let digits = [b"M73 P0 R".as_slice(), b"M73 P1 R"].iter().find(|p| line.starts_with(p))
            .map(|p| line[p.len()..].iter().take_while(|c| c.is_ascii_digit()).count());
        match digits {
            Some(digits) if digits > 0 => {
                out.extend_from_slice(&line[..8]);
                out.extend_from_slice(minutes.to_string().as_bytes());
                out.extend_from_slice(&line[8 + digits..]);
            }
            _ => out.extend_from_slice(line),
        }
    }
    out.extend_from_slice(&gcode[split..]);
    Ok(out)
}

/// The last layer a plate's own progress events name, `M73 L` at a line's start, if it sends any.
fn printer_layers(gcode: &[u8]) -> Option<usize> {
    gcode.split(|b| *b == b'\n').filter_map(|line| line.strip_prefix(b"M73 L"))
        .filter_map(|rest| std::str::from_utf8(rest).ok()?.trim().parse::<usize>().ok()).max()
}

/// The number of non-overlapping places `pattern` occurs.
fn count(data: &[u8], pattern: &[u8]) -> usize {
    let (mut found, mut at) = (0, 0);
    while let Some(i) = data[at..].windows(pattern.len()).position(|w| w == pattern) {
        found += 1;
        at += i + pattern.len();
    }
    found
}

/// The slice record with the sequenced plate's prediction, weight, first-course time, filament
/// and layers, edited in place so the record keeps the slicer's own layout.
fn slice_info(template: &[u8], prediction: i64, grams: f64, first_course_seconds: f64, filament_mm: f64, layers: usize) -> Result<Vec<u8>> {
    /// Puts `value` in the quoted value after the first `marker` from `from` on.
    fn put(info: &mut String, from: usize, marker: &str, value: &str, what: &str) -> Result<()> {
        let at = from + info[from..].find(marker).with_context(|| format!("No {what}"))? + marker.len();
        let end = at + info[at..].find('"').with_context(|| format!("Unclosed {what}"))?;
        info.replace_range(at..end, value);
        Ok(())
    }
    let mut info = String::from_utf8(template.to_vec())?;
    for (key, value) in [("prediction", prediction.to_string()), ("weight", format!("{grams:.2}")),
                         ("first_layer_time", format!("{first_course_seconds:.6}"))] {
        let marker = format!("key=\"{key}\" value=\"");
        let from = info.rfind(&marker).with_context(|| format!("No {key} metadata"))?;
        put(&mut info, from, &marker, &value, &format!("{key} metadata"))?;
    }
    let filament = info.find("<filament ").context("No <filament>")?;
    put(&mut info, filament, " used_m=\"", &format!("{:.2}", filament_mm / 1000.0), "filament length")?;
    put(&mut info, filament, " used_g=\"", &format!("{grams:.2}"), "filament weight")?;
    let open = info.find("<layer_filament_lists>").context("No <layer_filament_lists>")? + "<layer_filament_lists>".len();
    let close = open + info[open..].find("</layer_filament_lists>").context("Unclosed <layer_filament_lists>")?;
    info.replace_range(open..close, &format!("\n      <layer_filament_list filament_list=\"0\" layer_ranges=\"0 {layers}\" />\n    "));
    Ok(info.into_bytes())
}

/// The model without its objects and build items, as a print-only archive carries it.
fn print_only_model(data: &[u8]) -> Result<Vec<u8>> {
    let mut model = parse(std::str::from_utf8(data)?)?;
    for tag in ["resources", "build"] {
        let child = model.children.iter_mut().find(|e| e.local() == tag).with_context(|| format!("Model has no {tag}"))?;
        child.attributes.clear();
        child.children.clear();
        child.text.clear();
    }
    model.attributes.retain(|(key, _)| key != "requiredextensions");
    Ok(document(&model))
}

/// The model settings without objects, assemblies or plate instances.
fn print_only_settings(data: &[u8]) -> Result<Vec<u8>> {
    let mut config = parse(std::str::from_utf8(data)?)?;
    config.children.retain(|e| !matches!(e.local(), "object" | "assemble"));
    for plate in config.children.iter_mut().filter(|e| e.local() == "plate") {
        plate.children.retain(|e| e.local() != "model_instance");
    }
    Ok(document(&config))
}

fn editable(name: &str) -> bool {
    name.starts_with("3D/Objects/") || name.starts_with("3D/_rels/")
        || matches!(name, "Metadata/layer_config_ranges.xml" | "Metadata/cut_information.xml")
}

/// The motion reader's per-move record: the move's end time at its start, its G-code line at
/// `MOVE_LINE`, in a record `MOVE_RECORD` bytes long.
const MOVE_RECORD: usize = 62;
const MOVE_LINE: usize = 52;

/// Where a plate's printer progress changes: before each G-code line, counted from one, the
/// whole percent and whole minutes left the motion estimate gives as that line starts.
fn progress_points(gcode: &str, moves: &[u8]) -> Result<Vec<(usize, u64, u64)>> {
    ensure!(moves.len() % MOVE_RECORD == 0 && !moves.is_empty(), "The motion file is not whole records");
    let records: Vec<(f64, usize)> = moves.chunks_exact(MOVE_RECORD).map(|r| {
        (f64::from_le_bytes(r[..8].try_into().unwrap()), u32::from_le_bytes(r[MOVE_LINE..MOVE_LINE + 4].try_into().unwrap()) as usize)
    }).collect();
    let total = records.last().map(|r| r.0).context("The motion file has no moves")?;
    ensure!(total > 0.0, "The motion estimate takes no time");
    let line_of = |marker: &str| gcode.lines().position(|l| l.starts_with(marker)).map(|i| i + 1).with_context(|| format!("The plate has no {marker}"));
    let (start, end) = (line_of("; MACHINE_START_GCODE_END")?, line_of("; MACHINE_END_GCODE_START")?);
    let mut points = Vec::new();
    let mut last = None;
    let mut at = 0.0;
    for &(end_time, line) in &records {
        if line > start && line < end {
            let state = ((100.0 * at / total).floor() as u64, ((total - at) / 60.0).floor() as u64);
            if last != Some(state) && points.last().is_none_or(|p: &(usize, u64, u64)| p.0 < line) {
                points.push((line, state.0, state.1));
                last = Some(state);
            }
        }
        at = end_time;
    }
    Ok(points)
}

/// The plate with the printer's percent and time-left written in, as the slicer writes them on
/// its own plates: an `M73 P R` line wherever the motion estimate's whole percent or whole minute
/// left changes. `times` is the motion reader's move file, or the receipt of an earlier run on the
/// same plate. Only lines are added. The plate's course-group report is carried to `output`'s
/// under the new hash, with the progress points; the receipt is returned.
pub fn progress(plate: &Path, times: &Path, output: &Path) -> Result<Value> {
    ensure!(plate != output && !output.exists(), "Write the progress plate to a new path");
    let gcode = fs::read_to_string(plate)?;
    let source = crate::sha256_hex(gcode.as_bytes());
    let mut report: Value = serde_json::from_slice(&fs::read(plate.with_extension("json"))?)?;
    ensure!(report["sequenced_gcode_sha256"] == source.as_str(), "The plate and its course-group report differ");
    let points: Vec<(usize, u64, u64)> = if times.extension().is_some_and(|e| e == "json") {
        let earlier: Value = serde_json::from_slice(&fs::read(times)?)?;
        ensure!(earlier["pre_progress_gcode_sha256"] == source.as_str(), "The progress receipt belongs to another plate");
        serde_json::from_value(earlier["printer_progress"]["points"].clone()).context("The receipt's progress points")?
    } else {
        progress_points(&gcode, &fs::read(times)?)?
    };
    let mut out = String::with_capacity(gcode.len() + points.len() * 16);
    let mut next = points.iter().peekable();
    for (i, line) in gcode.split_inclusive('\n').enumerate() {
        while let Some(&&(at, p, r)) = next.peek() {
            if at != i + 1 {
                break;
            }
            let _ = std::fmt::Write::write_fmt(&mut out, format_args!("M73 P{p} R{r}\n"));
            next.next();
        }
        out.push_str(line);
    }
    ensure!(next.peek().is_none(), "A progress point lies past the plate's end");
    let sha = crate::sha256_hex(out.as_bytes());
    report["pre_progress_gcode_sha256"] = json!(source);
    report["sequenced_gcode_sha256"] = json!(sha);
    report["printer_progress"] = json!({
        "purpose": "The printer's percent and time-left as the motion estimate runs, written where either changes.",
        "lines": points.len(),
        "points": points,
    });
    fs::write(output, &out)?;
    fs::write(output.with_extension("json"), serde_json::to_string_pretty(&report)? + "\n")?;
    Ok(json!({"lines": points.len(), "source_gcode_sha256": source, "gcode_sha256": sha}))
}

/// Writes the print-only archive for `sequenced` to the new file `output`, from the native
/// slice's archive `template`, the sequencer's report beside `sequenced`, the playback motion
/// time and the first bed course's deposition span. The summary is returned.
pub fn package(template: &Path, sequenced: &Path, output: &Path, motion_seconds: f64, first_course_seconds: f64) -> Result<Value> {
    ensure!(!output.exists() && output != template, "Use a new destination; preserve the reviewed source archive");
    let raw = fs::read(sequenced)?;
    let report: Value = serde_json::from_slice(&fs::read(sequenced.with_extension("json"))?)?;
    ensure!(report["sequenced_gcode_sha256"] == crate::sha256_hex(&raw).as_str(), "Sequencer report and G-code differ");
    let groups = count(&raw, b"\n; CHANGE_LAYER\n");
    let rows = report["groups"].as_array().context("The report has no groups")?;
    ensure!(groups == rows.len(), "Missing course group delimiters");
    // a plate that tells the printer of its layers as it climbs counts those; otherwise its groups
    let layers = printer_layers(&raw).unwrap_or(groups);
    let deposition = report["deposition_mm_filament"].as_object().context("The report has no filament")?;
    let filament_mm = deposition.values().map(|v| v.as_f64().context("A filament length is not a number")).sum::<Result<f64>>()?;
    let diameter = header_number(&raw, "; filament_diameter: ")?;
    let density = header_number(&raw, "; filament_density: ")?;
    let volume_mm3 = PI * (diameter / 2.0).powf(2.0) * filament_mm;
    let grams = density * volume_mm3 / 1000.0;
    let time = duration(motion_seconds);
    let mut gcode = raw;
    for (key, line) in [
        ("; model printing time: ", format!("; model printing time: {time}; total estimated time: {time}")),
        ("; total layer number: ", format!("; total layer number: {layers}")),
        ("; total filament length [mm] : ", format!("; total filament length [mm] : {filament_mm:.2}")),
        // Native Bambu header stores the value in cubic millimeters under this key.
        ("; total filament volume [cm^3] : ", format!("; total filament volume [cm^3] : {volume_mm3:.2}")),
        ("; total filament weight [g] : ", format!("; total filament weight [g] : {grams:.2}")),
    ] {
        gcode = replace_line(&gcode, key, &line)?;
    }
    // Retain stock UI progress events at startup with the sequenced motion estimate.
    let gcode = startup_progress(&gcode, (motion_seconds / 60.0).ceil() as i64)?;

    let mut archive = zip::ZipArchive::new(fs::File::open(template).with_context(|| format!("opening {}", template.display()))?)?;
    let mut writer = zip::ZipWriter::new(fs::OpenOptions::new().write(true).create_new(true).open(output)?);
    let options = zip::write::SimpleFileOptions::default().compression_method(zip::CompressionMethod::Deflated).compression_level(Some(6));
    for i in 0..archive.len() {
        let mut entry = archive.by_index(i)?;
        let name = entry.name()?.to_string();
        if name.starts_with("Metadata/hsm_") || editable(&name) {
            continue;
        }
        let mut data = Vec::new();
        entry.read_to_end(&mut data)?;
        let data = match name.as_str() {
            GCODE => gcode.clone(),
            n if n == format!("{GCODE}.md5") => crate::ids::md5_hex(&gcode).into_bytes(),
            SLICE => slice_info(&data, motion_seconds.ceil() as i64, grams, first_course_seconds, filament_mm, layers)?,
            LAYOUT => {
                let mut layout: Value = serde_json::from_slice(&data)?;
                layout["first_layer_time"] = json!(first_course_seconds);
                serde_json::to_vec(&layout)?
            }
            MODEL => print_only_model(&data)?,
            SETTINGS => print_only_settings(&data)?,
            _ => data,
        };
        writer.start_file(name, options)?;
        writer.write_all(&data)?;
    }
    writer.finish()?;
    Ok(json!({
        "gcode_sha256": crate::sha256_hex(&gcode),
        "gcode_md5": crate::ids::md5_hex(&gcode),
        "course_groups": groups,
        "printer_layers": layers,
        "deposition_filament_mm": filament_mm,
        "deposition_weight_g": grams,
        "estimated_motion_seconds": motion_seconds,
        "first_bed_course_deposition_span_seconds": first_course_seconds,
    }))
}
