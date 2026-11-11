//! reservoir-print-project prepares the current reservoir bodies and open-port caps on their
//! production plates for offline slicing.
//!
//!     reservoir-print-project
//!
//! `print-settings.json` selects the native process for each plate. The float integration record
//! binds each STEP and its fine model, which in turn binds the print mesh.

use anyhow::{bail, ensure, Context, Result};
use hsm_print_prep::json::Json;
use hsm_print_prep::mesh::{Mesh, stl_corners};
use hsm_print_prep::profile::{relative, SETTINGS_MEMBER};
use hsm_print_prep::project::{MeshStyle, Plate};
use hsm_print_prep::{apply, faucet, npz, root, sha256_hex};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::Path;

const HERE: &str = "hardware/printed-parts/cold-core/reservoir";
const INTEGRATION: &str = "hardware/printed-parts/cold-core/magnetic-float/all-aero/integration-check.json";
const TITLE: &str = "Flavor reservoirs";
/// Every part keeps this far inside the left nozzle's usable bed.
const MIN_EDGE_MARGIN: f64 = 70.0;
/// Bambu Studio's logical plate grid pitch on the H2C.
const PLATE_STRIDE: [f64; 2] = [396.0, 384.0];
/// The paired caps stand this far either side of the bed's centre.
const PAIR_OFFSET: f64 = 43.5;
const SCOPE: &str = "Current CAD and selected native recipes. Historical water holds belong to the identified articles.";

fn object_settings(base: &Value, selected: &Value) -> Result<Vec<(String, String)>> {
    let base = base.as_object().context("reservoir base settings must be an object")?;
    let selected = selected.as_object().context("reservoir plate settings must be an object")?;
    ensure!(base.keys().eq(selected.keys()), "reservoir profiles have different settings keys");
    let mut overrides = Vec::new();
    for (key, value) in selected {
        if value == &base[key] || key == "print_settings_id" {
            continue;
        }
        ensure!(matches!(key.as_str(), "enable_support" | "infill_wall_overlap"),
            "reservoir plate setting {key} requires a separate native project");
        overrides.push((key.clone(), value.as_str().context("reservoir object setting must be text")?.into()));
    }
    Ok(overrides)
}

/// The print triangles bound to the part's fine model by the float integration record.
fn print_mesh(root: &Path, source: &Path, bound: &Value) -> Result<(Mesh, String, String)> {
    let fine = source.with_file_name(format!("{}.npz", source.file_name().unwrap_or_default().to_string_lossy()));
    let model_sha = faucet::file_sha(&fine)?;
    if bound[relative(&fine, root)].as_str() != Some(model_sha.as_str()) {
        bail!("{} differs from the float integration record", fine.file_name().unwrap_or_default().to_string_lossy());
    }
    let arrays = npz::read_arrays(&fine)?;
    let document: Value = serde_json::from_slice(arrays.get("document").and_then(|a| a.bytes()).context("the fine model has no document")?)?;
    let printed = &document["printed"];
    let emitted = fine.with_file_name(printed["path"].as_str().context("the fine model names no print mesh")?);
    let bytes = std::fs::read(&emitted)?;
    let stl_sha = sha256_hex(&bytes);
    if printed["sha256"].as_str() != Some(stl_sha.as_str()) {
        bail!("{} differs from its current fine model", emitted.file_name().unwrap_or_default().to_string_lossy());
    }
    Ok((Mesh::from_corners(&stl_corners(&bytes)?), model_sha, stl_sha))
}

fn main() -> Result<()> {
    let root = root();
    if let Some(arg) = std::env::args().nth(1) {
        bail!("unknown argument {arg}");
    }
    let here = root.join(HERE);
    let recipe = faucet::read_json(&here.join("print-settings.json"))?;
    let recipes = recipe["plates"].as_array().context("the recipe has no plates")?;
    let profile_path = |entry: &Value| -> Result<_> {
        Ok(here.join(entry["settings"].as_str().context("the plate has no native settings")?))
    };
    let base_path = profile_path(recipes.first().context("the recipe has no base plate")?)?;
    let text = std::fs::read_to_string(&base_path)?;
    let base: Value = serde_json::from_str(&text)?;
    ensure!(base["filament_map_mode"] == "Manual" && base["filament_map"] == json!(["1"])
        && base["filament_nozzle_map"] == json!(["0"]) && base["nozzle_diameter"][0] == "0.8",
        "the reservoir process needs the fixed left nozzle");
    ensure!(base["curr_bed_type"] == "Engineering Plate" && base["ironing_type"] == "no ironing"
        && base["enable_support_ironing"] == "0", "the reservoir process needs Engineering Plate with ironing off");
    let settings = Json::parse(&text)?;
    let integration = faucet::read_json(&root.join(INTEGRATION))?;
    let bound = &integration["files_sha256"];
    let area = settings.get("extruder_printable_area").map(Json::list).and_then(|a| a.first()).and_then(Json::text)
        .context("the printer has no printable area for the left nozzle")?;
    let (mut low, mut high) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
    for point in area.split(',') {
        let (x, y) = point.split_once('x').context("an area point without an x")?;
        for (k, v) in [x, y].into_iter().enumerate() {
            let v: f64 = v.trim().parse()?;
            low[k] = low[k].min(v);
            high[k] = high[k].max(v);
        }
    }
    let centre = [(low[0] + high[0]) / 2.0, (low[1] + high[1]) / 2.0];
    let height: f64 = settings.first_text("printable_height").context("the printer has no printable height")?.parse()?;
    let mut plate = Plate::with_settings(TITLE, settings, BTreeMap::new(), "homesodamachine/reservoir/");
    plate.mesh_style = MeshStyle::Element;
    plate.filament_map_mode = "Manual".into();
    plate.filament_volume_maps = "0".into();
    let mut parts = Vec::new();
    let mut profiles = Vec::new();
    let columns = (recipes.len() as f64).sqrt().ceil() as usize;
    for (index, entry) in recipes.iter().enumerate() {
        let path = profile_path(entry)?;
        let selected = faucet::read_json(&path)?;
        let overrides = object_settings(&base, &selected)?;
        let names = entry["parts"].as_array().context("the plate has no reservoir parts")?;
        plate.plates.push(entry["name"].as_str().context("the plate has no name")?.into());
        let origin = [(index % columns) as f64 * PLATE_STRIDE[0], -((index / columns) as f64) * PLATE_STRIDE[1], 0.0];
        profiles.push(json!({"plate": index + 1, "settings": relative(&path, &root), "settings_sha256": faucet::file_sha(&path)?,
            "enable_support": selected["enable_support"], "infill_wall_overlap": selected["infill_wall_overlap"],
            "evidence": entry["evidence"], "project_origin_mm": origin,
            "object_settings": overrides.iter().cloned().collect::<BTreeMap<_, _>>() }));
        for (part_index, name) in names.iter().enumerate() {
            let name = name.as_str().context("invalid reservoir part name")?;
            let cap = name.starts_with("reservoir-cap-");
            let source = here.join(format!("{name}.step"));
            let source_sha = faucet::file_sha(&source)?;
            if bound[relative(&source, &root)].as_str() != Some(source_sha.as_str()) {
                bail!("{name}.step differs from the float integration record");
            }
            let (mesh, model_sha, stl_sha) = print_mesh(&root, &source, bound)?;
            mesh.check_closed_single_body(name)?;
            let center = mesh.center();
            let local: Vec<[f64; 3]> = mesh.vertices.iter().map(|v| [v[0] - center[0], v[1] - center[1], v[2] - center[2]]).collect();
            // The body prints mouth up; the cap exterior face down, its gasket rim up.
            let rotation = if cap { [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]] } else { [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]] };
            let rotated: Vec<[f64; 3]> = local.iter().map(|v| apply(&rotation, *v)).collect();
            let (rlow, _) = hsm_print_prep::mesh::bounds(&rotated);
            let offset = if names.len() == 1 { 0.0 } else { (2.0 * part_index as f64 - 1.0) * PAIR_OFFSET };
            let translation = [centre[0] + offset, centre[1], -rlow[2]];
            let placed: Vec<[f64; 3]> = rotated.iter().map(|v| [v[0] + translation[0], v[1] + translation[1], v[2] + translation[2]]).collect();
            let (plow, phigh) = hsm_print_prep::mesh::bounds(&placed);
            if (0..2).any(|k| plow[k] < low[k] + MIN_EDGE_MARGIN || phigh[k] > high[k] - MIN_EDGE_MARGIN) || phigh[2] > height {
                bail!("{name} exceeds the left nozzle's usable bed/height");
            }
            let at = plate.add_object(name, local, mesh.faces.clone(), &format!("{name}.step"), center, rotation,
                                      [0, 1, 2].map(|k| translation[k] + origin[k]), None, overrides.clone());
            let object_id = 2401 + at;
            plate.objects[at].identify_id = object_id;
            plate.objects[at].plate = index;
            parts.push(json!({"name": name, "plate": index + 1, "object_id": object_id,
                              "source": relative(&source, &root), "step_sha256": source_sha, "model_sha256": model_sha, "stl_sha256": stl_sha,
                              "triangles": mesh.faces.len(), "watertight": true, "body_count": 1,
                              "print_orientation": if cap { "exterior face down" } else { "mouth up" }, "plate_bounds_mm": [plow, phigh]}));
        }
    }
    let project = here.join("reservoir.3mf");
    plate.write(&project)?;
    let saved: Value = serde_json::from_slice(faucet::members(&project)?.get(SETTINGS_MEMBER).context("the project lost its settings")?)?;
    if saved != base {
        bail!("Saved project did not preserve the recipe");
    }
    let report = json!({
        "project": "reservoir.3mf", "recipe": "print-settings.json", "material": recipe["material"],
        "base_settings_sha256": sha256_hex(&serde_json::to_vec(&base)?),
        "minimum_emitted_bead_edge_margin_mm": MIN_EDGE_MARGIN, "plate_count": recipes.len(), "plates": profiles,
        "parts": parts, "scope": SCOPE, "project_sha256": faucet::file_sha(&project)?,
    });
    std::fs::write(here.join("reservoir.print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    println!("{}", serde_json::to_string_pretty(&json!({"project": project.display().to_string(), "plates": recipes.len(), "parts": report["parts"]}))?);
    Ok(())
}
