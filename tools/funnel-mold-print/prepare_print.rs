//! funnel-mold-print-project — the silicone funnel mold's cavity and core, each on its own plate
//! of a Bambu Studio project composed from the installed system presets and the mold's recipe,
//! and optionally its offline slice. Never contacts a printer.
//!
//!     funnel-mold-print-project --models DIR --output PROJECT.3mf [--z-trim MM] [--label TEXT]
//!         [--nozzle 0.4|0.8] [--only cavity|core] [--settings-from SAVED.3mf] [--slice]
//!
//! `recipes.json` holds each nozzle's recipe, every setting it changes with its reason. Beside
//! the project go its provenance, naming where each setting came from, and the recipe as a
//! preset bundle Bambu Studio imports. `--settings-from` keeps a saved project's settings once
//! they agree with the recipe. `--slice` slices every plate into `native/` beside the project.

use anyhow::{bail, Context, Result};
use hsm_print_prep::mesh::Mesh;
use hsm_print_prep::preset::system_preset;
use hsm_print_prep::profile::{trimmed_start_gcode, PRESETS, SETTINGS_MEMBER};
use hsm_print_prep::project::{self, Plate, Range};
use hsm_print_prep::{faucet, root, sha256_hex, slice};
use serde_json::{json, Map, Value};
use std::collections::BTreeMap;
use std::io::Write;
use std::path::{Path, PathBuf};

const RECIPES: &str = "tools/funnel-mold-print/recipes.json";
/// Bambu Studio's offset between neighbouring plates on the H2C's bed.
const PLATE_STRIDE: f64 = 396.0;
const BED: &str = "Textured PEI Plate";
const PIECES: [&str; 2] = ["cavity", "core"];

fn field<'a>(value: &'a Value, key: &str) -> Result<&'a str> {
    value[key].as_str().with_context(|| format!("no {key}"))
}

/// A number, or a setting's text that holds one.
fn float(value: &Value) -> Option<f64> {
    match value {
        Value::String(s) => s.trim().parse().ok(),
        other => other.as_f64(),
    }
}

/// The settings of a recipe group, a preset or a saved project, by key.
fn entries(value: &Value) -> impl Iterator<Item = (&String, &Value)> {
    value.as_object().into_iter().flatten()
}

fn side(recipe: &Value) -> Result<usize> {
    match field(recipe, "side")? {
        "left" => Ok(0),
        "right" => Ok(1),
        other => bail!("no hotend side {other}"),
    }
}

/// Each hotend's flow type, left first: the recipe's nozzle on its side, Standard opposite.
fn volume_types(recipe: &Value) -> Result<Vec<String>> {
    let mut volumes = vec!["Standard".to_string(); 2];
    volumes[side(recipe)?] = field(recipe, "nozzle_type")?.to_string();
    Ok(volumes)
}

fn nozzle(recipe: &Value) -> Result<f64> {
    float(&recipe["nozzle_mm"]).context("the recipe names no nozzle size")
}

fn printer_name(recipe: &Value, trim: f64) -> Result<String> {
    Ok(format!("Bambu Lab H2C {} {} +{trim:.2} Z trim", nozzle(recipe)?, field(recipe, "nozzle_type")?))
}

fn trims(recipe: &Value) -> Vec<f64> {
    recipe["z_trim"]["available_mm"].as_array().into_iter().flatten().filter_map(float).collect()
}

fn presets(recipe: &Value) -> Result<&Value> {
    recipe.get("system_presets").context("the recipe names no system presets")
}

/// The machine preset itself, then one printer per available Z trim.
fn printer_names(recipe: &Value) -> Result<Vec<String>> {
    let mut names = vec![field(presets(recipe)?, "machine")?.to_string()];
    for trim in trims(recipe) {
        names.push(printer_name(recipe, trim)?);
    }
    Ok(names)
}

/// The recipe over its system presets, with the Z trim in the start G-code, and the provenance
/// of every value.
fn fresh_settings(recipe: &Value, trim: f64) -> Result<(Value, Value)> {
    let (mut values, mut sources, mut files) = (Map::new(), Map::new(), Map::new());
    let named = presets(recipe)?;
    let mut filament_id = None;
    // A filament's value wins over the process's and the printer's where both set a key.
    for kind in ["machine", "process", "filament"] {
        let resolved = system_preset(kind, field(named, kind)?, &mut files)?;
        values.extend(resolved.values);
        sources.extend(resolved.sources);
        if kind == "filament" {
            filament_id = resolved.ids.get("filament_id").cloned();
        }
    }
    for group in ["process_settings", "filament_settings"] {
        for (key, choice) in entries(&recipe[group]) {
            let reason = choice["reason"].as_str().filter(|r| !r.is_empty()).with_context(|| format!("{key} has no reason"))?;
            values.insert(key.clone(), choice.get("value").cloned().with_context(|| format!("{key} has no value"))?);
            sources.insert(key.clone(), json!({"recipe": group, "reason": reason}));
        }
    }
    let lane = side(recipe)?;
    let volumes = volume_types(recipe)?;
    let keys = |group: &str| entries(&recipe[group]).map(|(k, _)| k.as_str()).collect::<Vec<_>>().join(";");
    let lanes = values.get("filament_extruder_variant").and_then(Value::as_array).map_or(0, Vec::len);
    let stats: Vec<String> = volumes.iter().map(|v| format!("{v}#1")).collect();
    let filament_id = filament_id.context("the filament preset has no filament ID")?;
    let volume_map = if field(recipe, "nozzle_type")? == "High Flow" { "1" } else { "0" };
    let assignment = [
        ("printer_settings_id", json!(printer_name(recipe, trim)?)),
        ("print_settings_id", json!(field(recipe, "process_name")?)),
        ("filament_settings_id", json!([field(recipe, "filament_name")?])),
        ("inherits_group", json!([field(named, "process")?, field(named, "filament")?, field(named, "machine")?])),
        ("different_settings_to_system", json!([keys("process_settings"), keys("filament_settings"),
                                                "machine_start_gcode;default_nozzle_volume_type;nozzle_volume_type"])),
        ("filament_ids", json!([filament_id])),
        ("filament_colour", json!(["#DDEBF0"])),
        ("filament_map_mode", json!("Manual")),
        ("filament_map", json!([(lane + 1).to_string()])),
        ("filament_map_2", json!([(lane + 1).to_string()])),
        ("filament_nozzle_map", json!([lane.to_string()])),
        ("filament_self_index", json!(vec!["1"; lanes])),
        ("filament_volume_map", json!([volume_map])),
        ("nozzle_volume_type", json!(volumes)),
        ("default_nozzle_volume_type", json!(volumes)),
        ("extruder_nozzle_stats", json!(stats)),
        ("extruder_nozzle_stats_new", json!(stats)),
        ("curr_bed_type", json!(BED)),
        ("print_compatible_printers", json!(printer_names(recipe)?)),
    ];
    let reason = format!("One PETG filament on the {} hotend, textured PEI; named source presets.", field(recipe, "side")?);
    for (key, value) in assignment {
        values.insert(key.into(), value);
        sources.insert(key.into(), json!({"generator": "fresh_settings", "reason": reason}));
    }
    let start = values.get("machine_start_gcode").and_then(Value::as_str).context("the machine preset has no start G-code")?.to_string();
    values.insert("machine_start_gcode".into(), json!(trimmed_start_gcode(&start, trim)?));
    let preset = sources.get("machine_start_gcode").map_or(Value::Null, |s| s["preset"].clone());
    sources.insert("machine_start_gcode".into(), json!({"preset": preset, "generator": "trimmed_start_gcode", "z_trim_mm": trim,
                                                        "reason": recipe["z_trim"]["reason"]}));
    let mut supplied = Map::new();
    for (key, value) in &values {
        let mut row = sources.get(key).and_then(Value::as_object).cloned().unwrap_or_default();
        row.insert("value".into(), value.clone());
        supplied.insert(key.clone(), Value::Object(row));
    }
    Ok((Value::Object(values), json!({"system_preset_sha256": files, "supplied_settings": supplied})))
}

/// Whether a saved setting is the value supplied, as Bambu Studio rewrites a few on saving.
fn equivalent(key: &str, supplied: &Value, effective: &Value) -> bool {
    if supplied == effective {
        return true;
    }
    if key == "extruder_nozzle_stats" || key == "extruder_nozzle_stats_new" {
        let installed = |lanes: &Value| -> Vec<Vec<String>> {
            lanes.as_array().into_iter().flatten().map(|lane| {
                let mut kept: Vec<String> = lane.as_str().unwrap_or("").split('|')
                    .filter(|e| e.rsplit_once('#').and_then(|(_, n)| n.parse::<i64>().ok()).is_some_and(|n| n != 0))
                    .map(String::from).collect();
                kept.sort();
                kept
            }).collect()
        };
        return installed(supplied) == installed(effective);
    }
    if key == "best_object_pos" {
        return supplied.as_str().map(|s| s.replace('x', ",")).as_deref() == effective.as_str();
    }
    if key == "enable_long_retraction_when_cut" {
        return *supplied == json!([effective]);
    }
    if matches!(key, "top_surface_density" | "bottom_surface_density" | "monotonic_travel_into_wall") {
        let percent = |v: &Value| v.as_str().and_then(|s| s.trim_end_matches('%').parse::<f64>().ok());
        return percent(supplied).is_some() && percent(supplied) == percent(effective);
    }
    if let (Value::Array(a), Value::Array(b)) = (supplied, effective) {
        return a.len() == b.len() && a.iter().zip(b).all(|(x, y)| equivalent(key, x, y));
    }
    match (float(supplied), float(effective)) {
        (Some(a), Some(b)) => (a - b).abs() <= f64::max(1e-9 * f64::max(a.abs(), b.abs()), 1e-9),
        _ => false,
    }
}

/// The centre of the selected hotend's printable area, each plate's model centre.
fn bed_centre(settings: &Value, lane: usize) -> Result<[f64; 2]> {
    let area = settings["extruder_printable_area"][lane].as_str()
        .context("the printer has no printable area for the hotend")?;
    let (mut lo, mut hi) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
    for point in area.split(',') {
        let (x, y) = point.split_once('x').context("an area point without an x")?;
        for (k, v) in [x, y].into_iter().enumerate() {
            let v: f64 = v.trim().parse()?;
            lo[k] = lo[k].min(v);
            hi[k] = hi[k].max(v);
        }
    }
    Ok([(lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0])
}

/// The installed Bambu Studio's version.
fn slicer_version() -> Result<String> {
    let plist = Path::new(PRESETS).ancestors().nth(3).context("no application folder")?.join("Info.plist");
    let text = std::fs::read_to_string(&plist).with_context(|| format!("reading {}", plist.display()))?;
    let after = text.split_once("<key>CFBundleShortVersionString</key>").context("the application names no version")?.1;
    let value = after.split_once("<string>").and_then(|(_, rest)| rest.split_once("</string>")).context("the application's version is not a string")?.0;
    Ok(value.trim().to_string())
}

/// Every selector's preset, the stock parent named and the recipe's edits on it, as one bundle
/// Bambu Studio imports.
fn preset_bundle(recipe: &Value, version: &str, destination: &Path) -> Result<()> {
    let named = presets(recipe)?;
    let mut scratch = Map::new();
    let machine = field(named, "machine")?;
    let stock = system_preset("machine", machine, &mut scratch)?;
    let start = stock.values.get("machine_start_gcode").and_then(Value::as_str).context("no machine_start_gcode")?.to_string();
    let mut profiles = Vec::new();
    for offset in trims(recipe) {
        let name = printer_name(recipe, offset)?;
        profiles.push(json!({"from": "User", "inherits": machine, "name": name, "printer_settings_id": name, "version": version,
                             "machine_start_gcode": trimmed_start_gcode(&start, offset)?, "default_nozzle_volume_type": volume_types(recipe)?}));
    }
    for (kind, identity) in [("process", "print_settings_id"), ("filament", "filament_settings_id")] {
        let name = field(recipe, &format!("{kind}_name"))?;
        if name.contains('/') || name.contains('\\') {
            bail!("Preset names must also be valid filenames.");
        }
        let mut profile = json!({"from": "User", "inherits": field(named, kind)?, "name": name, "version": version});
        profile[identity] = if kind == "filament" { json!([name]) } else { json!(name) };
        for (key, choice) in entries(&recipe[format!("{kind}_settings").as_str()]) {
            profile[key.as_str()] = choice["value"].clone();
        }
        if kind == "process" {
            profile["compatible_printers"] = json!(printer_names(recipe)?);
        } else {
            let ids = system_preset(kind, field(named, kind)?, &mut scratch)?.ids;
            profile["filament_id"] = ids.get("filament_id").cloned().context("the filament preset has no filament ID")?;
        }
        profiles.push(profile);
    }
    let mut archive = zip::ZipWriter::new(std::fs::File::create(destination).with_context(|| format!("writing {}", destination.display()))?);
    for profile in &profiles {
        archive.start_file(format!("{}.json", field(profile, "name")?), project::options())?;
        archive.write_all((serde_json::to_string_pretty(profile)? + "\n").as_bytes())?;
    }
    archive.finish()?;
    Ok(())
}

/// Every plate sliced into `native/` beside the project, each plate's estimate printed.
fn slice_project(project: &Path) -> Result<()> {
    let native = project.parent().context("the project has no folder")?.join("native");
    std::fs::create_dir_all(&native)?;
    let name = project.file_name().context("the project has no name")?.to_string_lossy().replace(".3mf", ".gcode.3mf");
    let log = std::fs::File::create(native.join("slice.log"))?;
    let status = std::process::Command::new(slice::SLICER)
        .args(["--slice", "0", "--arrange", "0", "--orient", "0", "--outputdir"]).arg(&native)
        .args(["--export-3mf", &name]).arg(project)
        .current_dir(&native).stdout(log.try_clone()?).stderr(log).status()?;
    let result = if native.join("result.json").is_file() { faucet::read_json(&native.join("result.json"))? } else { serde_json::json!({}) };
    if !status.success() || result["return_code"].as_i64() != Some(0) {
        bail!("slice failed ({}): {}; see {}", status.code().unwrap_or(-1), result["error_string"], native.join("slice.log").display());
    }
    for plate in result["sliced_plates"].as_array().into_iter().flatten() {
        let grams: f64 = plate["filaments"].as_array().into_iter().flatten().filter_map(|f| f["total_used_g"].as_f64()).sum();
        println!("plate {}: {:.1} h, {grams:.0} g", plate["id"], plate["total_predication"].as_f64().unwrap_or(0.0) / 3600.0);
    }
    println!("{}", native.join(&name).display());
    Ok(())
}

fn main() -> Result<()> {
    let root = root();
    let (mut models, mut output, mut z_trim, mut label, mut nozzle_mm, mut only, mut settings_from, mut do_slice) =
        (None::<PathBuf>, None::<PathBuf>, None::<f64>, None::<String>, 0.4, None::<String>, None::<PathBuf>, false);
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        let mut value = || args.next().with_context(|| format!("{arg} needs a value"));
        match arg.as_str() {
            "--models" => models = Some(PathBuf::from(value()?)),
            "--output" => output = Some(PathBuf::from(value()?)),
            "--z-trim" => z_trim = Some(value()?.parse()?),
            "--label" => label = Some(value()?),
            "--nozzle" => nozzle_mm = value()?.parse()?,
            "--only" => only = Some(value()?),
            "--settings-from" => settings_from = Some(PathBuf::from(value()?)),
            "--slice" => do_slice = true,
            _ => bail!("unknown argument {arg}"),
        }
    }
    let models = models.context("--models names the folder holding cavity.stl and core.stl")?;
    let output = output.context("--output names the project to write")?;
    let recipes: Value = serde_json::from_slice(&std::fs::read(root.join(RECIPES))?)?;
    let recipe = recipes.get(&nozzle_mm.to_string()).with_context(|| format!("no recipe for the {nozzle_mm} mm nozzle"))?;
    let trim = match z_trim {
        Some(t) if trims(recipe).contains(&t) => t,
        Some(t) => bail!("no +{t} mm Z trim; the recipe offers {:?}", trims(recipe)),
        None => float(&recipe["z_trim"]["default_mm"]).context("the recipe has no default Z trim")?,
    };
    let names: Vec<&str> = match only.as_deref() {
        Some(piece) if PIECES.contains(&piece) => vec![piece],
        Some(piece) => bail!("no piece {piece}; cavity or core"),
        None => PIECES.to_vec(),
    };
    let (mut settings, mut provenance) = fresh_settings(recipe, trim)?;
    if let Some(saved) = &settings_from {
        let members = faucet::members(saved)?;
        let payload = members.get(SETTINGS_MEMBER).context("the saved project has no settings")?;
        let preserved: Value = serde_json::from_slice(payload)?;
        for group in ["process_settings", "filament_settings"] {
            for (key, expected) in entries(&recipe[group]) {
                let have = preserved.get(key).with_context(|| format!("the saved project has no {key}"))?;
                if !equivalent(key, &expected["value"], have) {
                    bail!("the saved project's {key} is {have}");
                }
            }
        }
        for key in ["printer_settings_id", "print_settings_id", "filament_settings_id", "machine_start_gcode", "curr_bed_type",
                    "nozzle_diameter", "nozzle_volume_type", "filament_volume_map"] {
            let have = preserved.get(key).with_context(|| format!("the saved project has no {key}"))?;
            if !equivalent(key, &settings[key], have) {
                bail!("the saved project's {key} is {have}");
            }
        }
        let source = json!({"project": saved.file_name().unwrap_or_default().to_string_lossy(), "project_sha256": faucet::file_sha(saved)?});
        let mut record = source.clone();
        record["settings_sha256"] = json!(sha256_hex(payload));
        provenance["settings_source"] = record;
        let mut supplied = Map::new();
        for (key, value) in entries(&preserved) {
            let mut row = source.clone();
            row["value"] = value.clone();
            supplied.insert(key.clone(), row);
        }
        provenance["supplied_settings"] = Value::Object(supplied);
        settings = preserved;
    }
    let version = slicer_version()?;
    let lane = side(recipe)?;
    let centre = bed_centre(&settings, lane)?;
    let side_map = (lane + 1).to_string();
    if settings.get("filament_map") != Some(&json!([side_map])) {
        bail!("the settings map the filament to {}, not the recipe's hotend", settings["filament_map"]);
    }
    let label = label.unwrap_or_else(|| "Funnel mold".into());
    let mut plate = Plate::with_settings(&label, settings, BTreeMap::new(), "homesodamachine/funnel-mold/");
    plate.application = format!("BambuStudio-{version}");
    plate.filament_maps = Some(side_map);
    plate.filament_map_mode = "Manual".into();
    plate.filament_volume_maps = if field(recipe, "nozzle_type")? == "High Flow" { "1" } else { "0" }.into();
    let mut meshes = Map::new();
    for (i, name) in names.iter().enumerate() {
        let index = i + 1;
        let path = models.join(format!("{name}.stl"));
        let mesh = Mesh::read_stl(&path)?;
        mesh.check_closed_single_body(&format!("{name}.stl"))?;
        let center = mesh.center();
        let (low, high) = mesh.bounds();
        let local: Vec<[f64; 3]> = mesh.vertices.iter().map(|v| [v[0] - center[0], v[1] - center[1], v[2] - center[2]]).collect();
        // The cavity prints upright; the core prints inverted on its dry back.
        let rotation = if *name == "core" { [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]] } else { [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]] };
        let translation = [centre[0] + i as f64 * PLATE_STRIDE, centre[1], (high[2] - low[2]) / 2.0];
        let at = plate.add_object(&format!("{label} {name}"), local, mesh.faces.clone(), &format!("{name}.stl"), center, rotation, translation,
                                  None, Vec::new());
        plate.objects[at].identify_id = 1800 + index;
        plate.objects[at].plate = i;
        for band in recipe["layer_ranges_mm"][*name].as_array().into_iter().flatten() {
            let (Some(bottom), Some(top)) = (float(&band[0]), float(&band[1])) else { bail!("a layer range needs a bottom and a top") };
            plate.objects[at].ranges.push(Range { min_z: bottom, max_z: top, options: vec![("layer_height".into(), "0.16".into())] });
        }
        meshes.insert(name.to_string(), json!(faucet::file_sha(&path)?));
    }
    plate.plates = names.iter().map(|name| format!("{label} {name}")).collect();
    plate.write(&output)?;
    provenance["mesh_sha256"] = Value::Object(meshes);
    provenance["parts"] = json!(names);
    provenance["recipe"] = recipe.clone();
    provenance["slicer_version"] = json!(version);
    std::fs::write(output.with_extension("provenance.json"), serde_json::to_string_pretty(&provenance)? + "\n")?;
    preset_bundle(recipe, &version, &output.parent().unwrap_or(Path::new(".")).join("funnel-mold-presets.bbscfg"))?;
    println!("{}", output.display());
    if do_slice {
        // Bambu Studio's slice is one of the Mac's heavy runs.
        hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
        slice_project(&std::path::absolute(&output)?)?;
    }
    Ok(())
}
