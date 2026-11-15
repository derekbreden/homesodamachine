//! faucet-cover-print-project — the faucet's display cover on its own PET-GF plate.
//! Never contacts a printer.
//!
//!     faucet-cover-print-project [--project P] [--printer Mark1|Mark2] [--filament-colour #RRGGBB]
//!
//! The cover is the shared cover in the faucet plate's pose, with the approved cover print's
//! settings and object settings, the printer's Z trim, and the plate's first bed layer and later
//! layers.

use anyhow::{bail, Context, Result};
use hsm_print_prep::profile::{first_text, petgf_infill_pattern, relative, settings_bytes, SETTINGS_MEMBER};
use hsm_print_prep::faucet_plate::{self, COVER};
use hsm_print_prep::refresh::{self, Part};
use hsm_print_prep::{faucet::text, root, sha256_hex, xml};
use serde_json::{json, Value};
use std::io::Read;
use std::path::{Path, PathBuf};

const HERE: &str = "hardware/printed-parts/faucet/faucet-display-cover";
/// Derek's approval of the shared tip and cover, which the report cites.
const SELECTION: &str = "hardware/printed-parts/faucet/industrial/production-selection.json";
/// The approved cover print, whose settings and object settings the project keeps.
const SETTINGS_SOURCE: &str = "hardware/printed-parts/faucet/faucet-display-cover/prints/2026-10-25-front-overlap-black-mark2/2026-10-25-sculpted-cover-front-overlap-black-left04-z004-mark2.3mf";
/// The plate's black filament.
const COLOUR: &str = "#161616";
const TITLE: &str = "Faucet display cover";
/// The cover keeps this far inside the plate's edge.
const PLATE_BORDER: f64 = 80.0;

fn member(path: &Path, name: &str) -> Result<Vec<u8>> {
    let mut archive = zip::ZipArchive::new(std::fs::File::open(path).with_context(|| format!("opening {}", path.display()))?)?;
    let mut bytes = Vec::new();
    archive.by_name(name)?.read_to_end(&mut bytes)?;
    Ok(bytes)
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
    let plate = faucet_plate::selection(&root)?;
    let finish: Value = serde_json::from_slice(&std::fs::read(root.join(plate["finish_selection"].as_str().context("the standing finish selection")?))?)?;
    let source = root.join(SETTINGS_SOURCE);
    let part = Part::new(COVER.name, root.join(COVER.stl), faucet_plate::COVER_ROTATION_DEGREES);
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
    let colour = colour.unwrap_or_else(|| COLOUR.to_string());
    r.plate.settings["filament_colour"] = json!([colour]);
    let mut changes = r.profile.changes.clone();
    for (key, value) in [
        ("initial_layer_print_height", text(&finish["first_bed_layer_height_mm"])),
        ("layer_height", text(&finish["layer_height_mm"])),
        ("sparse_infill_pattern", petgf_infill_pattern(&root)?),
    ] {
        let old = r.plate.settings[key].clone();
        if old != json!(value) {
            changes.insert(key.into(), json!({"from": old, "to": value}));
            r.plate.settings[key] = json!(value);
        }
    }
    let first: f64 = first_text(&r.plate.settings, "initial_layer_print_height").unwrap_or("0").parse()?;
    let layer: f64 = first_text(&r.plate.settings, "layer_height").unwrap_or("0").parse()?;
    let preserved = r.plate.settings == serde_json::from_slice::<Value>(&member(&source, SETTINGS_MEMBER)?)?;
    for (k, v) in [("printer", json!(printer)), ("requested_z_trim_mm", json!(trim)), ("active_nozzle", json!(0)),
                   ("first_bed_layer_height_mm", json!(first)), ("layer_height_mm", json!(layer)), ("layer_ranges", json!([])),
                   ("production_selection", json!(SELECTION)), ("physical_approval", selection["physical_result"].clone()),
                   ("accepted_cosmetic_condition", selection["accepted_cosmetic_condition"].clone()),
                   ("launch_authorized", json!(false)), ("submitted", json!(false))] {
        r.extra.insert(k.into(), v);
    }
    if let Some(parent) = project.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut report = r.write(&root, &project)?;
    report["settings_changes"] = json!(changes);
    report["settings_preserved"] = json!(preserved);
    report["settings_sha256"] = json!(sha256_hex(&settings_bytes(&r.plate.settings)?));
    std::fs::write(project.with_extension("print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    println!("{}: display cover; {first:.2} mm first layer, {layer:.2} mm later layers; {printer}", relative(&project, &root));
    Ok(())
}
