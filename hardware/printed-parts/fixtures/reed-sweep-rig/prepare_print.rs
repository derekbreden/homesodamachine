//! reed-sweep-rig-print-project — the reed sweep rig's native print projects, offline.
//!
//!     reed-sweep-rig-print-project [--plate ID] [--slice-output DIR]
//!
//! Run by hand after generating the rig's pieces. Each plate of `print-layout.json` takes the
//! shared PET-GF settings with supports off, its printer's Z trim and its spool's colour.
//! `--slice-output` slices each plate into its own empty directory under it, checks the emitted
//! trim and bead margin and that the slice draws no support, and writes the plate's ready
//! archive. It neither submits a print nor joins the build.

use anyhow::{bail, Context, Result};
use hsm_print_prep::json::{python_number, Json};
use hsm_print_prep::profile::{relative, SETTINGS_MEMBER};
use hsm_print_prep::refresh::{self, Part};
use hsm_print_prep::{faucet, root, sha256_hex};
use serde_json::{json, Map, Value};
use std::io::Write;
use std::path::{Path, PathBuf};

const HERE: &str = "hardware/printed-parts/fixtures/reed-sweep-rig";
/// The model and every emitted bead keep this far inside the plate's edge.
const PLATE_BORDER: f64 = 20.0;
/// Where a plate's settings project is written on its way to the plate writer.
const SETTINGS_RUN: &str = ".cache/runs/reed-sweep-rig-print-settings";

/// The plate's settings, written as a project the plate writer reads: the shared process as it
/// stands, for this printer's trim and spool, with supports and the prime tower off.
fn settings_project(root: &Path, spec: &Value) -> Result<(PathBuf, Map<String, Value>)> {
    let source = root.join(spec["settings_source"].as_str().context("settings source")?);
    let mut members = faucet::members(&source)?;
    let mut settings = Json::parse(std::str::from_utf8(&members[SETTINGS_MEMBER])?)?;
    let mut changes = Map::new();
    let nozzle: f64 = settings.first_text("nozzle_diameter").context("nozzle diameter")?.parse()?;
    let nozzle_text = python_number(nozzle).trim_end_matches(".0").to_string();
    let trim = spec["z_trim_mm"].as_f64().context("Z trim")?;
    let compatible = [format!("Bambu Lab H2C {nozzle_text} Standard +{trim:.2} Z trim"), format!("Bambu Lab H2C {nozzle_text} nozzle")];
    settings.set("print_compatible_printers", Json::List(compatible.iter().cloned().map(Json::Text).collect()));
    if let Some(colour) = spec["filament_colour"].as_str() {
        settings.set("filament_colour", Json::List(vec![Json::Text(colour.into())]));
    }
    let id = spec["id"].as_str().unwrap_or("");
    for (key, value) in [("enable_support", "0".to_string()), ("enable_prime_tower", "0".into()), ("print_settings_id", format!("0.24mm PET-GF reed sweep rig - {id}"))] {
        if settings.get(key).and_then(Json::text) != Some(value.as_str()) {
            changes.insert(key.into(), json!({"from": settings.get(key).map(Json::to_value), "to": value}));
            settings.set(key, Json::Text(value));
        }
    }
    members.insert(SETTINGS_MEMBER.into(), (settings.dumps() + "\n").into_bytes());
    let profile = root.join(SETTINGS_RUN).join(format!("{id}-settings.3mf"));
    std::fs::create_dir_all(profile.parent().unwrap())?;
    let mut archive = zip::ZipWriter::new(std::fs::File::create(&profile)?);
    for (name, data) in &members {
        archive.start_file(name.as_str(), hsm_print_prep::project::options())?;
        archive.write_all(data)?;
    }
    archive.finish()?;
    Ok((profile, changes))
}

fn prepare(root: &Path, spec: &Value) -> Result<(PathBuf, Value)> {
    let here = root.join(HERE);
    let (profile, changes) = settings_project(root, spec)?;
    let rows = spec["parts"].as_array().context("plate parts")?;
    let parts: Vec<Part> = rows.iter().map(|row| Ok(Part::new(row["name"].as_str().context("part name")?, here.join(row["source"].as_str().context("part source")?), 0.0))).collect::<Result<_>>()?;
    let offsets: Vec<[f64; 2]> = rows.iter().map(|row| [row["offset_mm"][0].as_f64().unwrap_or(0.0), row["offset_mm"][1].as_f64().unwrap_or(0.0)]).collect();
    let mut r = refresh::refresh(root, &profile, &parts, &offsets, spec["title"].as_str().unwrap_or(""), spec["z_trim_mm"].as_f64(), PLATE_BORDER)?;
    let source = root.join(spec["settings_source"].as_str().unwrap_or(""));
    for (k, v) in [("status", json!("offline project preparation; no printer submission")), ("printer_submission", json!(false)),
                   ("intended_printer", spec["printer"].clone()), ("material", spec["material"].clone()), ("nozzle_mapping", spec["nozzle_mapping"].clone()),
                   ("original_settings_source", spec["settings_source"].clone()), ("original_settings_source_sha256", json!(sha256_hex(&std::fs::read(&source)?))),
                   ("task_process_changes", json!(changes)), ("print_pose", json!("each piece on the face its STL stands on; no support"))] {
        r.extra.insert(k.into(), v);
    }
    let project = here.join("ready").join(spec["project"].as_str().context("project")?);
    let report = r.write(root, &project)?;
    Ok((project, report))
}

fn main() -> Result<()> {
    let root = root();
    let (mut only, mut slice_output) = (None::<String>, None::<PathBuf>);
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        let mut value = || args.next().with_context(|| format!("{arg} needs a value"));
        match arg.as_str() {
            "--plate" => only = Some(value()?),
            "--slice-output" => slice_output = Some(PathBuf::from(value()?)),
            _ => bail!("unknown argument {arg}"),
        }
    }
    let layout = faucet::read_json(&root.join(HERE).join("print-layout.json"))?;
    let selected: Vec<&Value> = layout["plates"].as_array().into_iter().flatten().filter(|s| only.as_deref().is_none_or(|id| s["id"] == id)).collect();
    if selected.is_empty() {
        bail!("unknown plate ID");
    }
    if slice_output.is_some() {
        // Bambu Studio's slices are the Mac's heavy runs.
        hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
    }
    for spec in selected {
        let (project, report) = prepare(&root, spec)?;
        println!("{}", relative(&project, &root));
        if let Some(base) = &slice_output {
            std::fs::create_dir_all(base)?;
            let record = refresh::slice_bench_plate(&project, &report, spec, &base.canonicalize()?.join(spec["id"].as_str().unwrap_or("plate")), None, PLATE_BORDER)?;
            if record["support_generated"] == json!(true) {
                bail!("the {} slice draws support: {}", spec["id"], record["features"]);
            }
            println!("{}", json!({"archive": record["archive"], "layers": record["layers"], "estimated_seconds": record["estimated_seconds"],
                "estimated_filament_g": record["estimated_filament_g"], "features": record["features"], "bead_margin_mm": record["bead_margin_mm"],
                "slicer_warning": record["slicer_warning"]}));
        }
    }
    Ok(())
}
