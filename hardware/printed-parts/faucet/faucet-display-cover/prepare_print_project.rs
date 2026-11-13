//! faucet-cover-print-project — one approved Sculpted faucet cover on its own PET-GF plate.
//! Never contacts a printer.
//!
//!     faucet-cover-print-project [--project P] [--printer Mark1|Mark2] [--filament-colour #RRGGBB]
//!
//! The cover is the exact approved STL in the production source set, in its approved pose, with
//! the approved cover print's settings and object settings, the printer's Z trim, and the
//! selection's first bed layer and later layers.

use anyhow::{bail, Context, Result};
use hsm_print_prep::json::{python_number, Json};
use hsm_print_prep::profile::{petgf_infill_pattern, relative, SETTINGS_MEMBER};
use hsm_print_prep::refresh::{self, Part};
use hsm_print_prep::{root, sha256_hex, xml};
use serde_json::{json, Value};
use std::io::Read;
use std::path::{Path, PathBuf};

const HERE: &str = "hardware/printed-parts/faucet/faucet-display-cover";
const SELECTION: &str = "hardware/printed-parts/faucet/industrial/production-selection.json";
const TITLE: &str = "Approved Sculpted faucet display cover";
/// The cover keeps this far inside the plate's edge.
const PLATE_BORDER: f64 = 80.0;

fn member(path: &Path, name: &str) -> Result<Vec<u8>> {
    let mut archive = zip::ZipArchive::new(std::fs::File::open(path).with_context(|| format!("opening {}", path.display()))?)?;
    let mut bytes = Vec::new();
    archive.by_name(name)?.read_to_end(&mut bytes)?;
    Ok(bytes)
}

fn text(v: &Value) -> String {
    match v {
        Value::String(s) => s.clone(),
        Value::Number(n) if n.is_i64() || n.is_u64() => n.to_string(),
        Value::Number(n) => python_number(n.as_f64().unwrap_or(0.0)),
        other => other.to_string(),
    }
}

fn main() -> Result<()> {
    let root = root();
    let (mut project, mut printer, mut colour) = (root.join(HERE).join("faucet-display-cover-petgf.3mf"), "Mark2".to_string(), None);
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        let mut value = || args.next().with_context(|| format!("{arg} needs a value"));
        match arg.as_str() {
            "--project" => project = PathBuf::from(value()?),
            "--printer" => printer = value()?,
            "--filament-colour" => colour = Some(value()?),
            _ => bail!("unknown argument {arg}"),
        }
    }
    let trim = hsm_print_prep::profile::petgf_z_trim(&root, &printer)?;
    let selection: Value = serde_json::from_slice(&std::fs::read(root.join(SELECTION))?)?;
    let row = selection["parts"].as_array().into_iter().flatten().find(|p| p["name"] == "sculpted-display-cover").context("no approved cover")?;
    let source = root.join(selection["settings_source"].as_str().context("settings source")?);
    let part = Part::new("sculpted-display-cover", root.join(row["source"].as_str().context("cover source")?), row["rotation_x_degrees"].as_f64().context("cover pose")?);
    let mut r = refresh::refresh(&root, &source, &[part], &[[0.0, 0.0]], TITLE, Some(trim), PLATE_BORDER)?;
    // The approved print's own object settings.
    let config = xml::parse(std::str::from_utf8(&member(&source, "Metadata/model_settings.config")?)?)?;
    let reference = config.child("object").context("the approved print has no object")?;
    for m in reference.children_named("metadata") {
        if let (Some(k), Some(v)) = (m.attribute("key"), m.attribute("value")) {
            if k != "name" && k != "extruder" && !hsm_print_prep::profile::PETGF_SUPPORT_KEYS.contains(&k) {
                r.plate.objects[0].settings.push((k.to_string(), v.to_string()));
            }
        }
    }
    let recipe = &selection["recipe"];
    let colour = colour.unwrap_or_else(|| recipe["filament_colour"].as_str().unwrap_or("#161616").to_string());
    r.plate.settings.set("filament_colour", Json::List(vec![Json::Text(colour)]));
    let mut changes = r.profile.changes.clone();
    for (key, value) in [
        ("initial_layer_print_height", text(&recipe["first_bed_layer_height_mm"])),
        ("layer_height", text(&recipe["layer_height_mm"])),
        ("sparse_infill_pattern", petgf_infill_pattern(&root)?),
    ] {
        let old = r.plate.settings.get(key).cloned().unwrap_or(Json::Null);
        if old != Json::Text(value.clone()) {
            changes.insert(key.into(), json!({"from": old.to_value(), "to": value}));
            r.plate.settings.set(key, Json::Text(value));
        }
    }
    let first: f64 = r.plate.settings.first_text("initial_layer_print_height").unwrap_or("0").parse()?;
    let layer: f64 = r.plate.settings.first_text("layer_height").unwrap_or("0").parse()?;
    let preserved = (r.plate.settings.dumps() + "\n").into_bytes() == member(&source, SETTINGS_MEMBER)?;
    for (k, v) in [("printer", json!(printer)), ("requested_z_trim_mm", json!(trim)), ("active_nozzle", json!(0)),
                   ("first_bed_layer_height_mm", json!(first)), ("layer_height_mm", json!(layer)), ("layer_ranges", json!([])),
                   ("production_selection", json!(SELECTION)), ("physical_approval", selection["physical_result"].clone()),
                   ("accepted_remaining_corner_gap", json!(true)), ("launch_authorized", json!(false)), ("submitted", json!(false))] {
        r.extra.insert(k.into(), v);
    }
    if let Some(parent) = project.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut report = r.write(&root, &project)?;
    report["settings_changes"] = json!(changes);
    report["settings_preserved_byte_for_byte"] = json!(preserved);
    report["settings_sha256"] = json!(sha256_hex((r.plate.settings.dumps() + "\n").as_bytes()));
    std::fs::write(project.with_extension("print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    println!("{}: approved cover; {first:.2} mm first layer, {layer:.2} mm later layers; {printer}", relative(&project, &root));
    Ok(())
}
