//! funnel-cover-print-project — the funnel cover's black PETG project, sliced offline, with its
//! review receipt beside it. Never contacts a printer.
//!
//!     funnel-cover-print-project
//!
//! The cover takes the shared PET-GF project's printer, process and the H2C's Z trim, Bambu's
//! stock PETG Basic filament preset, and a solid recipe: full zig-zag infill, no supports, no
//! brim. The slice must lay only the cover's own roads, from the left hotend, with its second
//! layer standing on its first.

use anyhow::{bail, Context, Result};
use hsm_print_prep::gcode;
use hsm_print_prep::ids::md5_hex;
use hsm_print_prep::json::Json;
use hsm_print_prep::preset::system_preset;
use hsm_print_prep::profile::{relative, SETTINGS_MEMBER};
use hsm_print_prep::refresh::{self, Part};
use hsm_print_prep::{faucet, review, root, sha256_hex, slice};
use serde_json::{json, Value};
use std::collections::BTreeSet;
use std::path::Path;

const HERE: &str = "hardware/printed-parts/zone-c/funnel-cover";
const PROFILE: &str = "hardware/printed-parts/petgf.3mf";
const JOB: &str = ".cache/prints/funnel-cover-petg-native";
const ARCHIVE: &str = "funnel-cover.gcode.3mf";
const TITLE: &str = "Funnel cover - black PETG - unsent";
const PROCESS: &str = "Funnel cover - solid PETG - 0.24 mm";
const FILAMENT: &str = "Bambu PETG Basic @BBL H2C";
const MATERIAL: &str = "Bambu PETG Basic Black";
const Z_TRIM: f64 = 0.18;
/// The model and every emitted bead keep this far inside the plate's edge.
const PLATE_BORDER: f64 = 15.0;
const FIRST_LAYER: f64 = 0.2;
const LAYER: f64 = 0.24;
/// The least share of the second layer's bead area that must lie over the first layer's.
const STACKED: f64 = 0.95;

fn text(value: &str) -> Json {
    Json::Text(value.into())
}

fn texts(values: &[&str]) -> Json {
    Json::List(values.iter().map(|v| text(v)).collect())
}

/// The cover's recipe over the shared project's settings: the stock PETG preset, then the
/// solid process. Returns the stock preset files read.
fn petg(settings: &mut Json) -> Result<Json> {
    let mut files = Json::Map(Vec::new());
    let preset = system_preset("filament", FILAMENT, &mut files)?;
    if let Json::Map(values) = preset.values {
        for (key, value) in values {
            settings.set(&key, value);
        }
    }
    let filament_id = preset.ids.get("filament_id").cloned().context("the PETG preset has no filament ID")?;
    let process = [("wall_loops", "3"), ("sparse_infill_density", "100%"), ("sparse_infill_pattern", "zig-zag"), ("enable_support", "0"),
                   ("brim_type", "no_brim"), ("brim_width", "0"), ("layer_height", "0.24"), ("initial_layer_print_height", "0.2"),
                   ("enable_prime_tower", "0")];
    for (key, value) in process {
        settings.set(key, text(value));
    }
    for (key, value) in [("filament_colour", texts(&["#000000"])), ("filament_type", texts(&["PETG"])),
                         ("filament_settings_id", texts(&[FILAMENT])), ("filament_ids", Json::List(vec![filament_id])),
                         ("filament_nozzle_map", texts(&["0"])), ("filament_map", texts(&["1"])), ("filament_map_2", texts(&["1"])),
                         ("filament_map_mode", text("Manual")), ("support_filament", text("1")), ("support_interface_filament", text("1")),
                         ("extruder_ams_count", texts(&["1#0|4#0", "1#0|4#0"])), ("flush_into_support", text("0"))] {
        settings.set(key, value);
    }
    // The material selector inherits the PETG preset rather than the exterior's spool.
    let mut inherits = settings.get("inherits_group").map(Json::list).unwrap_or(&[]).to_vec();
    if inherits.len() < 2 {
        bail!("the shared project names no filament preset to inherit");
    }
    inherits[1] = text(FILAMENT);
    settings.set("inherits_group", Json::List(inherits));
    let mut different = settings.get("different_settings_to_system").map(Json::list).unwrap_or(&[]).to_vec();
    let process_keys: BTreeSet<String> = different.first().and_then(Json::text).context("no process differences")?
        .split(';').map(String::from).chain(process.iter().map(|(k, _)| k.to_string())).collect();
    different[0] = text(&process_keys.into_iter().collect::<Vec<_>>().join(";"));
    settings.set("different_settings_to_system", Json::List(different));
    settings.set("print_settings_id", text(PROCESS));
    Ok(files)
}

/// Slice `project` into `job` as the printer takes it. The command line refuses the project's
/// cooling hook, so it slices a copy without it and the cooling stage runs on what it emits.
fn slice_project(project: &Path, job: &Path) -> Result<()> {
    let cli = slice::cli_project(project, job)?;
    let log = std::fs::File::create(job.join("bambu-cli.log"))?;
    let status = std::process::Command::new(slice::SLICER)
        .args(["--slice", "0", "--arrange", "0", "--orient", "0", "--outputdir"]).arg(job)
        .args(["--export-3mf", ARCHIVE]).arg(&cli)
        .current_dir(job).stdout(log.try_clone()?).stderr(log).status()?;
    if !status.success() {
        bail!("the offline slice exited {}; {}", status.code().unwrap_or(-1), job.join("bambu-cli.log").display());
    }
    slice::apply_directory(job, project)?;
    Ok(())
}

fn main() -> Result<()> {
    let root = root();
    if let Some(arg) = std::env::args().nth(1) {
        bail!("unknown argument {arg}");
    }
    let here = root.join(HERE);
    let job = root.join(JOB);
    std::fs::create_dir_all(&job)?;
    let project = here.join("funnel-cover-petg.3mf");
    let stl = here.join("funnel-cover-print.stl");
    let mut r = refresh::refresh(&root, &root.join(PROFILE), &[Part::new("funnel-cover", stl.clone(), 0.0)], &[[0.0, 0.0]], TITLE,
                                 Some(Z_TRIM), PLATE_BORDER)?;
    let files = petg(&mut r.plate.settings)?;
    r.extra.insert("source_mesh_sha256".into(), json!(faucet::file_sha(&stl)?));
    r.extra.insert("material".into(), json!(MATERIAL));
    r.extra.insert("filament_preset_sha256".into(), files.to_value());
    let mut report = r.write(&root, &project)?;
    let object = report["parts"][0]["identify_id"].as_i64().context("the cover has no object ID")?;

    // Bambu Studio's slice is one of the Mac's heavy runs.
    hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
    slice_project(&project, &job)?;
    let native = job.join(ARCHIVE);
    let members = faucet::members(&native)?;
    let member = |name: &str| members.get(name).with_context(|| format!("the sliced archive has no {name}"));
    let emitted = member("Metadata/plate_1.gcode")?;
    if md5_hex(emitted) != String::from_utf8_lossy(member("Metadata/plate_1.gcode.md5")?).trim().to_lowercase() {
        bail!("the sliced G-code does not match its MD5");
    }
    std::fs::write(job.join("plate_1.gcode"), emitted)?;
    let effective: Value = serde_json::from_slice(member(SETTINGS_MEMBER)?)?;
    if emitted.windows(18).any(|w| w == b"; FEATURE: Support") {
        bail!("the slice lays supports");
    }
    let (mut objects, mut tools, mut heights) = (BTreeSet::new(), BTreeSet::new(), Vec::new());
    let mut first_two: Vec<Vec<gcode::Road>> = Vec::new();
    gcode::layers(emitted, |layer| {
        let own: Vec<gcode::Road> = layer.roads.into_iter().filter(|road| road.object.is_some()).collect();
        if own.is_empty() {
            return;
        }
        for road in &own {
            objects.insert(road.object.unwrap_or_default());
            tools.insert(road.tool);
        }
        heights.push(layer.z);
        if first_two.len() < 2 {
            first_two.push(own);
        }
    });
    if objects != BTreeSet::from([object]) {
        bail!("the slice lays roads for objects {objects:?}, not only the cover's {object}");
    }
    if tools != BTreeSet::from([0]) {
        bail!("the slice lays roads from tools {tools:?}, not only the left hotend");
    }
    heights.sort_by(f64::total_cmp);
    heights.dedup();
    if heights.len() < 2 || heights[0] != FIRST_LAYER || heights[1] != FIRST_LAYER + LAYER {
        bail!("the first two layers top at {:?}", &heights[..heights.len().min(2)]);
    }
    let (_, stacked) = review::bead_stack(&first_two[0], &first_two[1]).context("the second layer lays no bead")?;
    if stacked <= STACKED {
        bail!("only {stacked} of the second layer's beads lie over the first layer");
    }
    for (key, value) in [("wall_loops", json!("3")), ("sparse_infill_density", json!("100%")), ("enable_support", json!("0")),
                         ("filament_type", json!(["PETG"])), ("filament_nozzle_map", json!(["0"])), ("layer_height", json!("0.24")),
                         ("initial_layer_print_height", json!("0.2")), ("enable_arc_fitting", json!("0"))] {
        if effective[key] != value {
            bail!("the slice's {key} is {}, not {value}", effective[key]);
        }
    }
    let result = faucet::read_json(&job.join("result.json"))?;
    if result["return_code"].as_i64() != Some(0) {
        bail!("the slice failed: {}", result["error_string"]);
    }
    let plates = result["sliced_plates"].as_array().context("the slice names no plates")?;
    let [sliced] = plates.as_slice() else { bail!("the slice made {} plates", plates.len()) };
    if sliced["warning_message"].as_str().is_some_and(|w| !w.is_empty()) {
        bail!("the slice warns: {}", sliced["warning_message"]);
    }

    let source_files = [here.join("prepare_print.rs"), stl.clone(), here.join("funnel-cover-print.step"), root.join(PROFILE)];
    let mut sources = serde_json::Map::new();
    for path in &source_files {
        sources.insert(relative(path, &root), json!(faucet::file_sha(path)?));
    }
    let grams: f64 = sliced["filaments"].as_array().into_iter().flatten().filter_map(|f| f["total_used_g"].as_f64()).sum();
    for (key, value) in [("source_sha256", json!(sources)), ("stock_filament_preset_sha256", files.to_value()),
                         ("native_archive", json!(relative(&native, &root))), ("native_sha256", json!(faucet::file_sha(&native)?)),
                         ("gcode_sha256", json!(sha256_hex(emitted))), ("settings_verified", json!(true)),
                         ("process", json!({"first_layer_mm": FIRST_LAYER, "layer_mm": LAYER, "walls": 3, "infill_percent": 100,
                                            "supports": false, "material": MATERIAL})),
                         ("support_paths", json!(0)), ("estimated_seconds", sliced["total_predication"].clone()),
                         ("estimated_grams", json!(grams)), ("first_two_layer_heights_mm", json!(&heights[..2])),
                         ("first_to_second_bead_footprint_overlap_fraction", json!(stacked)), ("model_layers", json!(heights.len())),
                         ("model_tools", json!(tools)), ("submitted", json!(false)),
                         ("physical_retention_and_drip_exclusion", json!("Unqualified"))] {
        report[key] = value;
    }
    std::fs::write(here.join("native-slice-review.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    std::fs::write(here.join("native-slice-preview.png"), member("Metadata/plate_1.png")?)?;
    println!("Native cover slice: no supports, solid PETG, {} s; unsent.", report["estimated_seconds"]);
    Ok(())
}
