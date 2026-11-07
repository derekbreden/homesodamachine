//! reservoir-print-project — the flavor reservoirs' current bodies and caps, each body with its
//! cap on a plate of its own, in the frozen PETG recipe with ironing off. Never contacts a
//! printer, and slices nothing: a slice belongs in an ignored review directory.
//!
//!     reservoir-print-project
//!
//! `print-settings.json` is the recipe: a frozen native base and the changes declared on it,
//! every other setting the base's own. Each STEP and its fine model must be the ones the float's
//! integration record binds, and each print mesh the one its fine model emitted. Writes
//! `reservoir.3mf` and `reservoir.print.json` beside the recipe.

use anyhow::{bail, Context, Result};
use hsm_print_prep::json::Json;
use hsm_print_prep::mesh::Mesh;
use hsm_print_prep::profile::{relative, SETTINGS_MEMBER};
use hsm_print_prep::project::{MeshStyle, Plate};
use hsm_print_prep::{apply, faucet, npz, root, sha256_hex};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::Path;

const HERE: &str = "hardware/printed-parts/cold-core/reservoir";
const INTEGRATION: &str = "hardware/printed-parts/cold-core/magnetic-float/all-aero/integration-check.json";
const CACHE: &str = ".cache/reservoir-current-print";
const TITLE: &str = "Flavor reservoirs - PETG 0.24 mm";
/// Every part keeps this far inside the right nozzle's usable bed.
const MIN_EDGE_MARGIN: f64 = 70.0;
/// Bambu Studio's offset between neighbouring plates on the H2C's bed.
const PLATE_STRIDE: f64 = 396.0;
/// A body and its cap stand this far either side of the bed's centre.
const PAIR_OFFSET: f64 = 43.5;
/// The declared changes on the frozen base; the first is required.
const CHANGES: [&str; 5] = ["identity_changes", "process_changes", "filament_changes", "assignment_changes", "machine_changes"];
const SCOPE: &str = "Current CAD and declared no-ironing recipe. Historical water holds belong to their identified articles; physical outcomes belong to the print records.";

/// The settings as Python's `json.dumps(sort_keys=True, separators=(",", ":"))` writes them.
fn canonical(settings: &Value) -> Result<Vec<u8>> {
    Ok(serde_json::to_vec(settings)?)
}

/// The recipe's settings, checked against its frozen base and its declared choices.
fn check_recipe(recipe: &Value) -> Result<()> {
    let settings = recipe["project_settings"].as_object().context("the recipe has no project settings")?;
    let mut restored = settings.clone();
    for (n, group) in CHANGES.iter().enumerate() {
        let changes = match recipe.get(*group) {
            Some(Value::Object(changes)) => changes.clone(),
            None if n > 0 => Default::default(),
            _ => bail!("the recipe has no {group}"),
        };
        for (key, change) in changes {
            if settings.get(&key) != change.get("to") {
                bail!("Unexpected declared setting: {key}");
            }
            restored.insert(key, change.get("from").cloned().context("a declared change without its base value")?);
        }
    }
    if Some(sha256_hex(&canonical(&Value::Object(restored))?).as_str()) != recipe["historical_source"]["project_settings_sha256"].as_str() {
        bail!("Undeclared settings differ from the frozen native base");
    }
    if settings.get("ironing_type") != Some(&json!("no ironing")) || settings.get("enable_support_ironing") != Some(&json!("0")) {
        bail!("The current reservoir recipe must disable model and support ironing");
    }
    if settings.get("filament_map_mode") != Some(&json!("Manual")) || settings.get("filament_map") != Some(&json!(["2"]))
        || settings.get("filament_nozzle_map") != Some(&json!(["1"])) {
        bail!("The current reservoir recipe must select the right nozzle manually");
    }
    Ok(())
}

/// The print triangles the part's fine model emitted, the model and its mesh as the float's
/// integration record and the model bind them, copied into the cache.
fn print_mesh(root: &Path, source: &Path, bound: &Value) -> Result<Mesh> {
    let fine = source.with_file_name(format!("{}.npz", source.file_name().unwrap_or_default().to_string_lossy()));
    if bound[relative(&fine, root)].as_str() != Some(faucet::file_sha(&fine)?.as_str()) {
        bail!("{} differs from the float integration record", fine.file_name().unwrap_or_default().to_string_lossy());
    }
    let arrays = npz::read_arrays(&fine)?;
    let document: Value = serde_json::from_slice(arrays.get("document").and_then(|a| a.bytes()).context("the fine model has no document")?)?;
    let printed = &document["printed"];
    let emitted = fine.with_file_name(printed["path"].as_str().context("the fine model names no print mesh")?);
    if printed["sha256"].as_str() != Some(faucet::file_sha(&emitted)?.as_str()) {
        bail!("{} differs from its current fine model", emitted.file_name().unwrap_or_default().to_string_lossy());
    }
    let target = root.join(CACHE).join(format!("{}.stl", source.file_stem().unwrap_or_default().to_string_lossy()));
    std::fs::copy(&emitted, &target)?;
    Mesh::read_stl(&target)
}

fn main() -> Result<()> {
    let root = root();
    if let Some(arg) = std::env::args().nth(1) {
        bail!("unknown argument {arg}");
    }
    let here = root.join(HERE);
    std::fs::create_dir_all(root.join(CACHE))?;
    let text = std::fs::read_to_string(here.join("print-settings.json"))?;
    let recipe: Value = serde_json::from_str(&text)?;
    check_recipe(&recipe)?;
    let settings = Json::parse(&text)?.get("project_settings").cloned().context("the recipe has no project settings")?;
    let integration = faucet::read_json(&root.join(INTEGRATION))?;
    let bound = &integration["files_sha256"];
    let area = settings.get("extruder_printable_area").map(Json::list).and_then(|a| a.get(1)).and_then(Json::text)
        .context("the printer has no printable area for the right nozzle")?;
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
    let mut plate = Plate::with_settings(TITLE, settings.clone(), BTreeMap::new(), "homesodamachine/reservoir/");
    plate.mesh_style = MeshStyle::Element;
    plate.filament_maps = Some("2".into());
    plate.filament_map_mode = "Manual".into();
    plate.filament_volume_maps = "0".into();
    let mut parts = Vec::new();
    let mut number = 0;
    for (index, side) in ["left", "right"].into_iter().enumerate() {
        let mut name = side.chars();
        let title = name.next().map(|c| c.to_uppercase().collect::<String>() + name.as_str()).unwrap_or_default();
        plate.plates.push(format!("{title} body and cap"));
        for cap in [false, true] {
            number += 1;
            let name = format!("reservoir-{}{side}", if cap { "cap-" } else { "" });
            let source = here.join(format!("{name}.step"));
            let source_sha = faucet::file_sha(&source)?;
            if bound[relative(&source, &root)].as_str() != Some(source_sha.as_str()) {
                bail!("{name}.step differs from the float integration record");
            }
            let mesh = print_mesh(&root, &source, bound)?;
            mesh.check_closed_single_body(&name)?;
            if mesh.volume() <= 0.0 {
                bail!("{name} is not one closed, consistently oriented volume");
            }
            let center = mesh.center();
            let local: Vec<[f64; 3]> = mesh.vertices.iter().map(|v| [v[0] - center[0], v[1] - center[1], v[2] - center[2]]).collect();
            // The body prints mouth up; the cap exterior face down, its gasket rim up.
            let rotation = if cap { [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]] } else { [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]] };
            let rotated: Vec<[f64; 3]> = local.iter().map(|v| apply(&rotation, *v)).collect();
            let (rlow, _) = hsm_print_prep::mesh::bounds(&rotated);
            let translation = [centre[0] + if cap { -PAIR_OFFSET } else { PAIR_OFFSET }, centre[1], -rlow[2]];
            let placed: Vec<[f64; 3]> = rotated.iter().map(|v| [v[0] + translation[0], v[1] + translation[1], v[2] + translation[2]]).collect();
            let (plow, phigh) = hsm_print_prep::mesh::bounds(&placed);
            if (0..2).any(|k| plow[k] < low[k] + MIN_EDGE_MARGIN || phigh[k] > high[k] - MIN_EDGE_MARGIN) || phigh[2] > height {
                bail!("{name} exceeds the right nozzle's usable bed/height");
            }
            let origin = [index as f64 * PLATE_STRIDE, 0.0, 0.0];
            let at = plate.add_object(&name, local, mesh.faces.clone(), &format!("{name}.step"), center, rotation,
                                      [0, 1, 2].map(|k| translation[k] + origin[k]), None, Vec::new());
            plate.objects[at].identify_id = 2400 + number;
            plate.objects[at].plate = index;
            parts.push(json!({"name": name, "plate": index + 1, "source": relative(&source, &root), "step_sha256": source_sha,
                              "triangles": mesh.faces.len(), "watertight": true, "body_count": 1,
                              "print_orientation": if cap { "exterior face down" } else { "mouth up" }, "plate_bounds_mm": [plow, phigh]}));
        }
    }
    let project = here.join("reservoir.3mf");
    plate.write(&project)?;
    let saved: Value = serde_json::from_slice(faucet::members(&project)?.get(SETTINGS_MEMBER).context("the project lost its settings")?)?;
    if saved != recipe["project_settings"] {
        bail!("Saved project did not preserve the recipe");
    }
    let mut report = json!({
        "project": "reservoir.3mf", "recipe": "print-settings.json", "accepted_result_id": recipe["accepted_result_id"],
        "settings_sha256": sha256_hex(&canonical(&recipe["project_settings"])?),
        "settings_match_native_base_except_declared_changes": true,
        "minimum_emitted_bead_edge_margin_mm": MIN_EDGE_MARGIN, "plate_count": 2, "mesh_tolerance_mm": 0.025,
        "mesh_angular_tolerance_rad": 0.08, "physical_recipe_source": recipe.get("physical_recipe_source").cloned().unwrap_or(Value::Null),
        "parts": parts, "scope": SCOPE, "project_sha256": faucet::file_sha(&project)?,
    });
    for group in CHANGES {
        report[group] = recipe.get(group).cloned().unwrap_or_else(|| json!({}));
    }
    std::fs::write(here.join("reservoir.print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    println!("{}", serde_json::to_string_pretty(&json!({"project": project.display().to_string(), "plates": 2, "parts": report["parts"]}))?);
    Ok(())
}
