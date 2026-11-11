//! reservoir-slice-review — the current reservoir project's native slice, read against its
//! recipe, into `slice-review.json`. Never contacts a printer.
//!
//!     reservoir-slice-review
//!
//! It slices `reservoir.3mf` and audits each plate's supports into the review folder when the
//! folder holds no slice of the current project. The review checks the plate processes, left
//! nozzle assignment, Engineering Plate trim, layer heights, bed margins, body cooling and
//! support placement.

use anyhow::{bail, ensure, Context, Result};
use hsm_print_prep::ids::md5_hex;
use hsm_print_prep::{audit, faucet, root, sha256_hex, slice, xml};
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::f64::consts::{FRAC_PI_2, PI, TAU};
use std::path::Path;

const HERE: &str = "hardware/printed-parts/cold-core/reservoir";
const FOLDER: &str = ".cache/prints/reservoir-slice-review";
const ARCHIVE: &str = "reservoir-review.3mf";
const SETTINGS: &str = "Metadata/project_settings.config";
const TRIMS: [&str; 2] = ["G29.1 Z0 ; clear z-trim value first", "G29.1 Z0"];
const ASSIGNMENT: [(&str, &str); 3] = [("filament_map", "1"), ("filament_nozzle_map", "0"), ("nozzle_diameter", "0.8,0.8")];
const FIRST_LAYER: f64 = 0.30;
const LAYER: f64 = 0.24;
/// Walls above this height are the bodies' and caps' upper walls, whose cooling is read.
const WALL_COOLING_ABOVE_Z: f64 = 12.0;
/// The two caps keep this much clearance between their full bead envelopes.
const CAP_GAP: f64 = 5.0;

/// The letter words of a command, as `([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))` finds them.
fn words(code: &str) -> BTreeMap<char, f64> {
    let b = code.as_bytes();
    let mut out = BTreeMap::new();
    let mut i = 0;
    while i < b.len() {
        if b[i].is_ascii_uppercase() {
            let mut j = i + 1;
            if j < b.len() && (b[j] == b'-' || b[j] == b'+') {
                j += 1;
            }
            let digits = |k: usize| b[k..].iter().take_while(|c| c.is_ascii_digit()).count();
            let whole = digits(j);
            let end = if whole > 0 {
                let mut e = j + whole;
                if e < b.len() && b[e] == b'.' {
                    e += 1 + digits(e + 1);
                }
                e
            } else if j < b.len() && b[j] == b'.' && digits(j + 1) > 0 {
                j + 1 + digits(j + 1)
            } else {
                0
            };
            if end > 0 {
                if let Ok(v) = code[i + 1..end].parse() {
                    out.insert(b[i] as char, v);
                }
                i = end;
                continue;
            }
        }
        i += 1;
    }
    out
}

/// An I/J arc's length and the points that bound it: its ends and the cardinal points it passes.
fn arc(start: [f64; 2], end: [f64; 2], w: &BTreeMap<char, f64>, clockwise: bool) -> Result<(f64, Vec<[f64; 2]>)> {
    if w.contains_key(&'R') || !(w.contains_key(&'I') || w.contains_key(&'J')) {
        bail!("an arc the review cannot read");
    }
    let centre = [start[0] + w.get(&'I').copied().unwrap_or(0.0), start[1] + w.get(&'J').copied().unwrap_or(0.0)];
    let radius = (start[0] - centre[0]).hypot(start[1] - centre[1]);
    let first = (start[1] - centre[1]).atan2(start[0] - centre[0]);
    let last = (end[1] - centre[1]).atan2(end[0] - centre[0]);
    let mut sweep = (if clockwise { first - last } else { last - first }).rem_euclid(TAU);
    if (end[0] - start[0]).hypot(end[1] - start[1]) < 1e-7 {
        sweep = TAU;
    }
    let mut points = vec![start, end];
    for angle in [0.0, FRAC_PI_2, PI, 3.0 * FRAC_PI_2] {
        let offset = (if clockwise { first - angle } else { angle - first }).rem_euclid(TAU);
        if offset <= sweep + 1e-8 {
            points.push([centre[0] + radius * angle.cos(), centre[1] + radius * angle.sin()]);
        }
    }
    Ok((radius * sweep, points))
}

/// Every deposited bead's full width against the bed, each object's bead box, and the fan
/// commanded on the upper walls.
fn toolpaths(text: &str, ids: &[i64], bed: [[f64; 2]; 2], margin: f64, body_fan: Option<[f64; 2]>) -> Result<(Value, Vec<f64>)> {
    if text.lines().any(|l| l.strip_prefix("; FEATURE:").is_some_and(|f| f.trim() == "Ironing")) {
        bail!("the slice holds an ironing feature");
    }
    let (mut x, mut y, mut e, mut width, mut fan) = (0.0f64, 0.0f64, 0.0f64, 0.0f64, 0.0f64);
    let (mut z, mut object) = (None::<f64>, None::<i64>);
    let (mut absolute, mut relative_e) = (true, true);
    let mut feature = String::new();
    let (mut deposited, mut supports) = (0usize, 0usize);
    let (mut low, mut high) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
    let mut boxes: BTreeMap<i64, ([f64; 2], [f64; 2])> = ids.iter().map(|&i| (i, ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]))).collect();
    let mut cooling: BTreeMap<u64, f64> = BTreeMap::new();
    for raw in text.lines() {
        if let Some(rest) = raw.strip_prefix("; OBJECT_ID: ").or_else(|| raw.strip_prefix("; start printing object, unique label id: ")) {
            let id: i64 = rest.chars().take_while(char::is_ascii_digit).collect::<String>().parse()?;
            if !boxes.contains_key(&id) {
                bail!("an unexpected object in the slice: {id}");
            }
            object = Some(id);
        }
        if raw.starts_with("; stop printing object") {
            object = None;
        }
        if let Some(v) = raw.strip_prefix("; Z_HEIGHT:") {
            z = v.trim().parse().ok();
        }
        if let Some(v) = raw.strip_prefix("; FEATURE:") {
            feature = v.trim().to_string();
        }
        if let Some(v) = raw.strip_prefix("; LINE_WIDTH:") {
            width = v.trim().parse().unwrap_or(width);
        }
        let code = raw.split(';').next().unwrap_or("").trim();
        let Some(command) = code.split_whitespace().next() else { continue };
        let w = words(code);
        if command == "M1031" && w.get(&'S') == Some(&1.0) {
            bail!("the slice turns ironing on");
        }
        if command == "M106" && w.get(&'P').copied().unwrap_or(1.0) == 1.0 {
            fan = w.get(&'S').copied().unwrap_or(255.0);
        }
        match command {
            "G90" | "G91" => absolute = command == "G90",
            "M82" | "M83" => relative_e = command == "M83",
            "G92" => {
                x = w.get(&'X').copied().unwrap_or(x);
                y = w.get(&'Y').copied().unwrap_or(y);
                e = w.get(&'E').copied().unwrap_or(e);
            }
            _ => {}
        }
        if !matches!(command, "G0" | "G1" | "G2" | "G3") {
            continue;
        }
        let nx = if absolute { w.get(&'X').copied().unwrap_or(x) } else { x + w.get(&'X').copied().unwrap_or(0.0) };
        let ny = if absolute { w.get(&'Y').copied().unwrap_or(y) } else { y + w.get(&'Y').copied().unwrap_or(0.0) };
        let ne = w.get(&'E').copied().unwrap_or(if relative_e { 0.0 } else { e });
        let extrusion = if relative_e { ne } else { ne - e };
        let (length, extrema) = if command == "G2" || command == "G3" {
            arc([x, y], [nx, ny], &w, command == "G2")?
        } else {
            ((nx - x).hypot(ny - y), vec![[x, y], [nx, ny]])
        };
        if z.is_some() && !feature.is_empty() && feature != "Custom" && extrusion > 0.0 && length > 0.001 {
            if width <= 0.0 {
                bail!("a deposited path has no bead width");
            }
            let a = [0, 1].map(|k| extrema.iter().map(|p| p[k]).fold(f64::INFINITY, f64::min) - width / 2.0);
            let b = [0, 1].map(|k| extrema.iter().map(|p| p[k]).fold(f64::NEG_INFINITY, f64::max) + width / 2.0);
            low = [low[0].min(a[0]), low[1].min(a[1])];
            high = [high[0].max(b[0]), high[1].max(b[1])];
            deposited += 1;
            supports += usize::from(feature.starts_with("Support"));
            if let Some(box_) = object.and_then(|o| boxes.get_mut(&o)) {
                box_.0 = [box_.0[0].min(a[0]), box_.0[1].min(a[1])];
                box_.1 = [box_.1[0].max(b[0]), box_.1[1].max(b[1])];
            }
            if (feature == "Outer wall" || feature == "Inner wall") && z.is_some_and(|z| z > WALL_COOLING_ABOVE_Z) {
                cooling.insert(fan.to_bits(), fan);
            }
        }
        x = nx;
        y = ny;
        e = if relative_e { e + ne } else { ne };
    }
    let margins = [low[0] - bed[0][0], low[1] - bed[0][1], bed[1][0] - high[0], bed[1][1] - high[1]];
    let least = margins.iter().copied().fold(f64::INFINITY, f64::min);
    if deposited == 0 || least < margin {
        bail!("the full beads leave the bed margin: {margins:?}");
    }
    if boxes.values().any(|(a, b)| !(a.iter().chain(b).all(|v| v.is_finite()))) {
        bail!("a body or cap lays no beads");
    }
    let gap = if let [a, b] = ids {
        let (first, second) = (boxes[a], boxes[b]);
        let gap = (0..2).map(|k| (first.0[k] - second.1[k]).max(second.0[k] - first.1[k]).max(0.0).powi(2)).sum::<f64>().sqrt();
        ensure!(gap >= CAP_GAP, "the caps stand too close together");
        Some(gap)
    } else {
        None
    };
    let mut pwm: Vec<f64> = cooling.into_values().collect();
    pwm.sort_by(f64::total_cmp);
    ensure!(body_fan.is_none_or(|[minimum, maximum]| pwm.iter().any(|&p| minimum - 1e-6 <= p && p <= maximum + 1e-6)),
        "the upper reservoir walls leave the ordinary cooling range");
    Ok((json!({"left_nozzle_usable_bed_bounds_mm": bed, "model_support_brim_xy_bounds_mm": [low, high],
        "edge_margins_left_front_right_back_mm": margins, "minimum_full_bead_edge_margin_mm": least,
        "minimum_cap_full_bead_box_gap_mm": gap, "deposited_move_count": deposited, "support_move_count": supports,
        "scope": "Native deposited model, support and brim beads, including arc extrema and half-width. Vendor startup purge/calibration paths are excluded. Placement does not establish adhesion."}), pwm))
}

/// Slice the project into `folder` and audit each plate's supports there.
fn slice_and_audit(project: &Path, folder: &Path, plate_count: usize) -> Result<()> {
    // Bambu Studio's slice is one of the Mac's heavy runs.
    hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
    std::fs::create_dir_all(folder)?;
    let log = std::fs::File::create(folder.join("bambu-cli.log"))?;
    let status = std::process::Command::new(slice::SLICER)
        .args(["--slice", "0", "--arrange", "0", "--orient", "0", "--outputdir"]).arg(folder).args(["--export-3mf", ARCHIVE]).arg(project)
        .current_dir(folder).stdout(log.try_clone()?).stderr(log).status()?;
    if !status.success() {
        bail!("the offline slice exited {}; {}", status.code().unwrap_or(-1), folder.join("bambu-cli.log").display());
    }
    let members = faucet::members(&folder.join(ARCHIVE))?;
    for i in 1..=plate_count {
        let gcode = members.get(&format!("Metadata/plate_{i}.gcode")).with_context(|| format!("the slice has no plate {i}"))?;
        let options = audit::Options { piece: format!("reservoir plate {i}"), object: None, include_unlabelled: true, cad_transform: None,
                                       bed_reseat: None, inputs: json!({"archive": ARCHIVE, "plate": i, "gcode_sha256": sha256_hex(gcode)}) };
        let reading = audit::audit(gcode, &options);
        std::fs::write(folder.join(format!("plate_{i}-supports.json")), serde_json::to_string_pretty(&reading)? + "\n")?;
    }
    Ok(())
}

fn main() -> Result<()> {
    let root = root();
    if let Some(arg) = std::env::args().nth(1) {
        bail!("unknown argument {arg}");
    }
    let here = root.join(HERE);
    let folder = root.join(FOLDER);
    let project = here.join("reservoir.3mf");
    let generated = faucet::read_json(&here.join("reservoir.print.json"))?;
    let project_sha = faucet::file_sha(&project)?;
    if generated["project_sha256"].as_str() != Some(project_sha.as_str()) {
        bail!("reservoir.3mf differs from its preparation record");
    }
    let planned = generated["plates"].as_array().context("the project has no plate plan")?;
    let project_members = faucet::members(&project)?;
    let source: Value = serde_json::from_slice(project_members.get(SETTINGS).context("the project has no settings")?)?;
    // A slice of another project is sliced again.
    let sliced_from = folder.join("project.sha256");
    if !folder.join("result.json").is_file() || std::fs::read_to_string(&sliced_from).ok().as_deref() != Some(project_sha.as_str()) {
        if folder.exists() {
            std::fs::remove_dir_all(&folder)?;
        }
        slice_and_audit(&project, &folder, planned.len())?;
        std::fs::write(&sliced_from, &project_sha)?;
    }
    let result = faucet::read_json(&folder.join("result.json"))?;
    let plates = result["sliced_plates"].as_array().context("the slice names no plates")?;
    ensure!(result["return_code"] == 0 && plates.len() == planned.len(), "the slice did not finish all planned plates");
    if source["ironing_type"] != "no ironing" || source["enable_support_ironing"] != "0" {
        bail!("the recipe must keep model and support ironing off");
    }
    let area = source["extruder_printable_area"][0].as_str().context("no left-nozzle area")?;
    let points: Vec<[f64; 2]> = area.split(',').map(|p| {
        let (a, b) = p.split_once('x').context("an area point")?;
        Ok([a.trim().parse()?, b.trim().parse()?])
    }).collect::<Result<_>>()?;
    let bed = [[0, 1].map(|k| points.iter().map(|p| p[k]).fold(f64::INFINITY, f64::min)),
               [0, 1].map(|k| points.iter().map(|p| p[k]).fold(f64::NEG_INFINITY, f64::max))];
    let members = faucet::members(&folder.join(ARCHIVE))?;
    let sliced: Value = serde_json::from_slice(members.get(SETTINGS).context("the slice has no settings")?)?;
    let (source_map, sliced_map) = (source.as_object().context("recipe settings")?, sliced.as_object().context("slice settings")?);
    let added: Map<String, Value> = sliced_map.iter().filter(|(k, _)| !source_map.contains_key(*k)).map(|(k, v)| (k.clone(), v.clone())).collect();
    if !(added.is_empty() || Value::Object(added.clone()) == json!({"filament_map_2": ["1"]})) || source_map.iter().any(|(k, v)| sliced_map.get(k) != Some(v)) {
        bail!("the slicer changed the saved process");
    }
    let config = xml::parse(std::str::from_utf8(members.get("Metadata/model_settings.config").context("the slice has no object settings")?)?)?;
    let fans = ["fan_min_speed", "fan_max_speed"].map(|k| source[k][0].as_str().and_then(|v| v.parse::<f64>().ok()).unwrap_or(0.0) * 2.55);
    let margin = generated["minimum_emitted_bead_edge_margin_mm"].as_f64().context("no bead margin")?;
    let mut rows = Vec::new();
    for (row, planned) in plates.iter().zip(planned) {
        let i = planned["plate"].as_i64().context("the plan has no plate number")?;
        ensure!(row["id"] == i, "the slicer changed the plate order");
        let parts: Vec<&Value> = generated["parts"].as_array().into_iter().flatten().filter(|p| p["plate"].as_i64() == Some(i)).collect();
        let names: Vec<&Value> = parts.iter().map(|p| &p["name"]).collect();
        let objects: Vec<&Value> = row["objects"].as_array().into_iter().flatten().map(|o| &o["name"]).collect();
        if row["warning_message"].as_str().is_some_and(|w| !w.is_empty()) || objects != names {
            bail!("plate {i} warns or holds other objects");
        }
        for name in &names {
            let settings = config.children_named("object").map(|object| {
                object.children_named("metadata").filter_map(|m| Some((m.attribute("key")?, m.attribute("value")?)))
                    .collect::<BTreeMap<_, _>>()
            }).find(|settings| settings.get("name").copied() == name.as_str()).context("no native settings for planned object")?;
            for (key, value) in planned["object_settings"].as_object().context("no planned object settings")? {
                ensure!(settings.get(key.as_str()).copied() == value.as_str(), "plate {i} lost object setting {key} for {name}");
            }
        }
        let name = format!("Metadata/plate_{i}.gcode");
        let data = members.get(&name).with_context(|| format!("no {name}"))?;
        if md5_hex(data) != String::from_utf8_lossy(&members[&format!("{name}.md5")]).trim().to_lowercase() {
            bail!("plate {i}'s G-code does not match its MD5");
        }
        let text = std::str::from_utf8(data)?;
        let lines: Vec<&str> = text.lines().collect();
        let features: BTreeSet<&str> = lines.iter().filter_map(|l| l.strip_prefix("; FEATURE: ")).filter(|f| !["Custom", "Support", "Support interface"].contains(f)).collect();
        let mut assignment = Map::new();
        for (key, expected) in ASSIGNMENT {
            let prefix = format!("; {key} = ");
            let found = lines.iter().find_map(|l| l.strip_prefix(prefix.as_str())).map(str::trim);
            if found != Some(expected) {
                bail!("plate {i}'s {key} does not match the fixed left nozzle");
            }
            assignment.insert(key.into(), json!(expected));
        }
        let trims: Vec<&str> = lines.iter().map(|l| l.trim_start()).filter(|l| l.starts_with("G29.1 Z")).collect();
        if trims != TRIMS {
            bail!("plate {i} emits unexpected Engineering Plate Z trims {trims:?}");
        }
        let layers: Vec<(f64, f64)> = lines.windows(3).filter(|w| w[0] == "; CHANGE_LAYER").filter_map(|w| {
            Some((w[1].strip_prefix("; Z_HEIGHT: ")?.parse().ok()?, w[2].strip_prefix("; LAYER_HEIGHT: ")?.parse().ok()?))
        }).collect();
        let top = parts.iter().filter_map(|p| p["plate_bounds_mm"][1][2].as_f64()).fold(f64::NEG_INFINITY, f64::max);
        if layers.is_empty() || layers[0].1 != FIRST_LAYER || layers[1..].iter().any(|l| (l.1 - LAYER).abs() > 2e-5) || (layers[layers.len() - 1].0 - top).abs() >= LAYER {
            bail!("plate {i}'s layers are not the recipe's");
        }
        if row["feature_type_times"]["Ironing"].as_f64().unwrap_or(0.0) != 0.0 {
            bail!("plate {i}'s estimate includes ironing");
        }
        let ids = parts.iter().map(|p| p["object_id"].as_i64().context("missing object ID")).collect::<Result<Vec<_>>>()?;
        let body = names.iter().any(|n| n.as_str().is_some_and(|s| !s.starts_with("reservoir-cap-")));
        let (placement, cooling) = toolpaths(text, &ids, bed, margin, body.then_some(fans))?;
        ensure!(planned["enable_support"] != "0" || placement["support_move_count"] == 0,
            "plate {i} emits support with the support-free cap recipe");
        let support = faucet::read_json(&folder.join(format!("plate_{i}-supports.json")))?["summary"].clone();
        if support["bed_rooted_bodies"] != support["support_bodies"] || support["model_rooted_bodies"].as_i64() != Some(0) {
            bail!("plate {i}'s supports root on the model");
        }
        let round = |v: f64| (v * 1000.0).round() / 1000.0;
        rows.push(json!({"plate": i, "parts": names, "estimated_seconds": round(row["total_predication"].as_f64().unwrap_or(0.0)),
            "estimated_mass_g": round(row["filaments"].as_array().into_iter().flatten().filter_map(|f| f["total_used_g"].as_f64()).sum()),
            "ironing_estimated_seconds": 0, "ironing_enable_commands": 0, "ironing_feature_paths": 0, "layer_count": layers.len(),
            "first_layer_height_mm": FIRST_LAYER, "normal_layer_height_mm": LAYER, "model_features": features,
            "wall_generator": source["wall_generator"], "requested_wall_loops": source["wall_loops"].as_str().and_then(|v| v.parse::<i64>().ok()),
            "infill_wall_overlap": planned["infill_wall_overlap"], "enable_support": planned["enable_support"],
            "settings_source": planned["settings"], "settings_source_sha256": planned["settings_sha256"],
            "wall_transition_angle_degrees": source["wall_transition_angle"].as_str().and_then(|v| v.parse::<f64>().ok()),
            "warning_message": row["warning_message"], "gcode_sha256": sha256_hex(data), "embedded_gcode_md5_verified": true,
            "emitted_nozzle_assignment": assignment, "z_trim_commands": trims, "placement": placement,
            "wall_cooling_above_cap_pwm_values": cooling, "support_summary": support,
            "support_scope": "All detected support bodies start at the bed. Bodies without explicit interface labels have no inferred contact build-up."}));
    }
    let review = json!({"project": "reservoir.3mf", "project_sha256": project_sha, "recipe": "print-settings.json",
        "archive": format!("{FOLDER}/{ARCHIVE}"), "archive_sha256": faucet::file_sha(&folder.join(ARCHIVE))?,
        "slicer_version": text_version(&members), "return_code": 0, "physical_settings_match_saved_project": true,
        "slicer_added_metadata": added, "plates": rows,
        "scope": "Native slice of current body/cap geometry with ironing off. Coupon finish selection and the historical water-hold acceptance apply to their tested articles; this slice supplies no new physical sealing result."});
    std::fs::write(here.join("slice-review.json"), serde_json::to_string_pretty(&review)? + "\n")?;
    println!("{}", serde_json::to_string_pretty(&json!({"project_sha256": review["project_sha256"], "plates": review["plates"].as_array().map(|p| p.len())}))?);
    Ok(())
}

/// The slicer's version, as the first plate's G-code names it.
fn text_version(members: &BTreeMap<String, Vec<u8>>) -> String {
    members.get("Metadata/plate_1.gcode").and_then(|g| std::str::from_utf8(g).ok())
        .and_then(|t| t.lines().find_map(|l| l.strip_prefix("; BambuStudio ")).map(str::trim).map(String::from)).unwrap_or_default()
}
