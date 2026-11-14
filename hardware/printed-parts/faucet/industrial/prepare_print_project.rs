//! industrial-faucet-print-project — the approved Industrial faucet's five rigid parts on one
//! PET-GF plate, and optionally its offline slice. Never contacts a printer.
//!
//!     industrial-faucet-print-project [--project P] [--settings-from S] [--printer Mark1|Mark2]
//!                                     [--filament-colour #RRGGBB] [--slice-output DIR] [--slicer PATH]
//!
//! The parts are the generated meshes the production selection names, posed as it poses them. The settings are the approved cover print's, with the selected finish: the
//! printer's Z trim, Bambu's first bed layer and uniform later layers, the overhang and bridge
//! recipe over the localized cooling, rear seams on the base, tip and plate and aligned seams on
//! the cover and lever. The base starts on a sloped scaffold, roof and skin.
//! The base's insert recesses and the plate's
//! counterbores use bridges. The tip uses a contoured perimeter and dense trees at its
//! mating lip and a removable disc at its hidden root.

use anyhow::{bail, Context, Result};
use hsm_faucet_numbers::shell::{FOOT_DEPTH, FOOT_WIDTH};
use hsm_print_prep::faucet::{add_tip_root_anchor, apply_overhang_recipe, as_texts, cross, enforce_rear_seam,
                             file_sha, mat, members, read_json, recorded_member, sub, text, texts, times};
use hsm_print_prep::faucet_contact::{add_tip_dispense_contact, add_tip_rim_contact, apply_stretch_cooling,
                                     apply_tip_rim_contour, tip_end_stretch, ContactBand};
use hsm_print_prep::faucet_recesses::block_plate_counterbores;
use hsm_print_prep::faucet_underside::{self, Underside};
use hsm_print_prep::json::{python_number, Json};
use hsm_print_prep::profile::{cooling_hook, petgf_infill_pattern, relative, SETTINGS_MEMBER};
use hsm_print_prep::refresh::{self, Part, Refreshed, Region};
use hsm_print_prep::{cooling, root, sha256_hex, slice, xml};
use serde_json::{json, Map, Value};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

const HERE: &str = "hardware/printed-parts/faucet/industrial";
const TITLE: &str = "Industrial faucet PET-GF";
/// Each part's own space for its brim and automatically generated supports, from the shared
/// plate's centre.
const PART_OFFSETS: [[f64; 2]; 5] = [[-77.0, 0.0], [24.0, 47.0], [89.0, 76.0], [43.0, -52.0], [94.0, -58.0]];
/// The model keeps this far inside the plate's edge.
const PLATE_BORDER: f64 = 40.0;




/// The settings and filament members a profile is.
fn profile_members(path: &Path) -> Result<BTreeMap<String, Vec<u8>>> {
    Ok(members(path)?.into_iter().filter(|(n, _)| n == SETTINGS_MEMBER || (n.starts_with("Metadata/filament_settings_") && n.ends_with(".config"))).collect())
}

/// Each selected upward shoulder of the base, read off its current STL.
fn shoulder_readings(r: &Refreshed, recipe_report: &Value, layer_height: f64) -> Result<Vec<Value>> {
    let row = &r.rows[0];
    let obj = &r.plate.objects[row.index];
    let rotation = mat(&obj.transform_values());
    let mut readings = Vec::new();
    for reference in recipe_report["selected_faces"].as_array().into_iter().flatten() {
        let z = reference["cad_z_mm"].as_f64().context("selected face height")?;
        let (mut area, mut lo, mut hi, mut zlo, mut zhi) = (0.0, [f64::INFINITY; 3], [f64::NEG_INFINITY; 3], f64::INFINITY, f64::NEG_INFINITY);
        let mut any = false;
        for f in &row.mesh.faces {
            let p = f.map(|i| row.mesh.vertices[i]);
            let c = cross(sub(p[1], p[0]), sub(p[2], p[0]));
            let length = (c[0] * c[0] + c[1] * c[1] + c[2] * c[2]).sqrt();
            if !(p.iter().all(|q| (q[2] - z).abs() < 1e-5) && length > 0.0 && c[2] / length > 0.9999) {
                continue;
            }
            any = true;
            area += length / 2.0;
            for q in p {
                for k in 0..3 {
                    lo[k] = lo[k].min(q[k]);
                    hi[k] = hi[k].max(q[k]);
                }
                let placed = times(sub(q, row.center), &rotation)[2] + row.translation[2];
                zlo = zlo.min(placed);
                zhi = zhi.max(placed);
            }
        }
        if !any {
            bail!("the current base has no upward shoulder at CAD Z{}", python_number(z));
        }
        readings.push(json!({"cad_z_mm": z, "pick_mm": reference["pick_mm"],
            "measurement": "Current source STL upward planar facets at the selected CAD Z", "area_mm2": area,
            "cad_bounds_mm": [lo, hi], "print_z_span_mm": [zlo, zhi], "model_layer_height_mm": layer_height}));
    }
    Ok(readings)
}

fn main() -> Result<()> {
    let root = root();
    let here = root.join(HERE);
    let acceptance_path = here.join("physical-acceptance.json");
    let production_path = here.join("production-selection.json");
    let finish_path = here.join("finish-selection.json");
    let accepted = read_json(&acceptance_path)?;
    let production = read_json(&production_path)?;
    let finish = read_json(&finish_path)?;
    let recipe = root.join(accepted["prepared_project"].as_str().context("prepared project")?);
    let protected: Vec<PathBuf> = ["3mf", "print.json", "support-audit.json", "readiness.json"].iter()
        .map(|s| root.join("hardware/printed-parts/faucet/faucet-petgf").with_extension(s)).collect();
    let (mut project, mut settings_from) = (here.join("faucet-industrial-petgf.3mf"), root.join(production["settings_source"].as_str().context("settings source")?));
    let (mut printer, mut colour, mut slice_output, mut slicer) = (None, None, None::<PathBuf>, PathBuf::from(slice::SLICER));
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        let mut value = || args.next().with_context(|| format!("{arg} needs a value"));
        match arg.as_str() {
            "--project" => project = PathBuf::from(value()?),
            "--settings-from" => settings_from = PathBuf::from(value()?),
            "--printer" => printer = Some(value()?),
            "--filament-colour" => colour = Some(value()?),
            "--slice-output" => slice_output = Some(PathBuf::from(value()?)),
            "--slicer" => slicer = PathBuf::from(value()?),
            _ => bail!("unknown argument {arg}"),
        }
    }
    let printer = printer.unwrap_or_else(|| finish["default_printer"].as_str().unwrap_or("Mark2").to_string());
    let trim = hsm_print_prep::profile::petgf_z_trim(&root, &printer)?;
    let colour = colour.unwrap_or_else(|| finish["default_filament_colour"].as_str().unwrap_or("#161616").to_string());
    if project.extension().and_then(|e| e.to_str()).map(str::to_lowercase).as_deref() != Some("3mf") {
        bail!("the Industrial project needs a .3mf filename");
    }
    std::fs::create_dir_all(project.parent().unwrap_or(Path::new(".")))?;
    let project = project.parent().unwrap().canonicalize()?.join(project.file_name().unwrap());
    let settings_from = settings_from.canonicalize()?;
    let same = |a: &Path, b: &Path| a.canonicalize().ok().is_some_and(|x| b.canonicalize().ok() == Some(x)) || a == b;
    if same(&project, &settings_from) || same(&project, &recipe) || protected.iter().any(|p| same(&project, p)) {
        bail!("the Industrial output must not replace its settings source or the Sculpted project");
    }
    if Some(file_sha(&recipe)?.as_str()) != accepted["prepared_project_sha256"].as_str() {
        bail!("the accepted five-part recipe has changed");
    }
    let recipe_report = read_json(&recipe.parent().unwrap().join("preparation.json"))?;
    let preserved = profile_members(&settings_from)?;
    let parts: Vec<Part> = production["parts"].as_array().context("production parts")?.iter().map(|row| {
        Ok(Part::new(row["name"].as_str().context("part name")?, root.join(row["source"].as_str().context("part source")?),
                     row["rotation_x_degrees"].as_f64().context("part rotation")?))
    }).collect::<Result<_>>()?;
    let missing: Vec<String> = parts.iter().filter(|p| !p.source.is_file()).map(|p| relative(&p.source, &root)).collect();
    if !missing.is_empty() {
        bail!("generate the Industrial STLs before preparing the project: {}", missing.join(", "));
    }
    let mut r = refresh::refresh(&root, &settings_from, &parts, &PART_OFFSETS, TITLE, Some(trim), PLATE_BORDER)?;
    // The complete foot takes solid infill with the ordinary wall settings.
    let regions: Vec<Region> = recipe_report["local_solid_regions"].as_array().into_iter().flatten().map(|row| {
        let b = &row["source_bounds_mm"];
        Ok(Region { part: row["part"].as_str().context("region part")?.to_string(), name: row["name"].as_str().context("region name")?.to_string(),
                    low: [0, 1, 2].map(|k| b[0][k].as_f64().unwrap_or(f64::NAN)), high: [0, 1, 2].map(|k| b[1][k].as_f64().unwrap_or(f64::NAN)),
                    clip_to_part_bounds: false,
                    declared: json!({"part": row["part"], "name": row["name"], "source_bounds_mm": row["source_bounds_mm"], "clip_to_part_bounds": false})})
    }).collect::<Result<_>>()?;
    r.add_local_solid_regions(&regions)?;

    // The accepted recipe's object settings, and the selected seams.
    let recipe_members = members(&recipe)?;
    let recipe_config = xml::parse(std::str::from_utf8(&recipe_members["Metadata/model_settings.config"])?)?;
    let seam_parts: Vec<String> = finish["seam_parts"].as_array().into_iter().flatten().filter_map(|v| v.as_str().map(String::from)).collect();
    for obj in r.plate.objects.iter_mut() {
        let recipe_name = if obj.name == "sculpted-display-cover" { "industrial-display-cover".to_string() } else { obj.name.clone() };
        let source = recipe_config.children_named("object")
            .find(|o| o.children_named("metadata").any(|m| m.attribute("key") == Some("name") && m.attribute("value") == Some(&recipe_name)))
            .with_context(|| format!("the accepted recipe has no object {recipe_name}"))?;
        for m in source.children_named("metadata") {
            if let (Some(k), Some(v)) = (m.attribute("key"), m.attribute("value")) {
                if k != "name" && k != "extruder" && !hsm_print_prep::profile::PETGF_SUPPORT_KEYS.contains(&k) {
                    obj.settings.push((k.to_string(), v.to_string()));
                }
            }
        }
        obj.settings.retain(|(k, _)| !(k.starts_with("seam_") || k == "scarf_angle_threshold" || k == "override_filament_scarf_seam_setting"));
        let overrides = if seam_parts.contains(&obj.name) { &finish["seam_object_overrides"] } else { &finish["corner_seam_object_overrides"] };
        for (k, v) in overrides.as_object().into_iter().flatten() {
            obj.settings.push((k.clone(), text(v)));
        }
    }

    let settings = &mut r.plate.settings;
    let original_colour = settings.get("filament_colour").map(Json::to_value);
    settings.set("filament_colour", texts(&[colour.clone()]));
    settings.set("sparse_infill_pattern", Json::Text(petgf_infill_pattern(&root)?));
    for (key, value) in finish["filament_overrides"].as_object().into_iter().flatten() {
        let mut items = as_texts(settings.get(key).with_context(|| format!("the profile has no {key}"))?);
        if items.is_empty() {
            bail!("{key} has no first slot");
        }
        items[0] = text(value);
        settings.set(key, texts(&items));
    }
    let mut layer_changes = Map::new();
    for (key, value) in [("layer_height", text(&finish["normal_layer_height_mm"])), ("initial_layer_print_height", text(&finish["first_bed_layer_height_mm"])),
                         ("independent_support_layer_height", "0".to_string())] {
        let old = settings.get(key).cloned().unwrap_or(Json::Null);
        if old != Json::Text(value.clone()) {
            layer_changes.insert(key.into(), json!({"from": old.to_value(), "to": value}));
            settings.set(key, Json::Text(value));
        }
    }
    let hook = cooling_hook(&root);
    let overhang_changes = apply_overhang_recipe(settings, &finish["overhang_recipe"], &hook)?;
    let bands: Vec<[f64; 2]> = finish["base_fine_bands_print_z_mm"].as_array().into_iter().flatten()
        .map(|b| [b[0].as_f64().unwrap_or(0.0), b[1].as_f64().unwrap_or(0.0)]).collect();
    if !bands.is_empty() {
        let base = r.row("industrial-shell-base")?.index;
        let height = text(&finish["fine_layer_height_mm"]);
        r.plate.objects[base].ranges = bands.iter().map(|[lo, hi]| hsm_print_prep::project::Range {
            min_z: *lo, max_z: *hi, options: vec![("layer_height".into(), height.clone())] }).collect();
    }
    if finish["rear_seam_enforcement"].is_object() {
        let record = enforce_rear_seam(&mut r, &finish["rear_seam_enforcement"])?;
        r.extra.insert("rear_seam_enforcement".into(), record);
    }
    if finish["tip_rear_seam_enforcement"].is_object() {
        let record = enforce_rear_seam(&mut r, &finish["tip_rear_seam_enforcement"])?;
        r.extra.insert("tip_rear_seam_enforcement".into(), record);
    }
    let radius = FOOT_WIDTH.max(FOOT_DEPTH) / 2.0;
    let underside = Underside::prepare(&mut r, "industrial-shell-base", [radius; 2], &finish["base_underside"])?;
    let plate_recesses = &finish["mounting_plate_counterbores"];
    let counterbores = block_plate_counterbores(&mut r, plate_recesses["part"].as_str().context("mounting plate identity")?,
        plate_recesses["radial_clearance_mm"].as_f64().context("counterbore radial clearance")?,
        serde_json::from_value(plate_recesses["axial_allowance_mm"].clone())?)?;
    r.extra.insert("mounting_plate_counterbores".into(), counterbores);
    if finish["tip_supports"].is_object() {
        let record = add_tip_root_anchor(&root, &mut r, &finish["tip_supports"])?;
        r.extra.insert("tip_supports".into(), record);
    }
    let motion_source = &finish["tip_contact_parameters"];
    let motion_bytes = recorded_member(&root, motion_source, "parameters_source")?;
    let mapping: Value = serde_json::from_slice(&motion_bytes)?;
    let mut parameters = mapping["parameters"].clone();
    if let Some(entries) = parameters.as_object_mut() {
        entries.remove("purpose");
    }
    let tip_contact = add_tip_dispense_contact(&mut r, &finish["tip_dispense_contact"], &parameters)?;
    r.extra.insert("tip_dispense_contact".into(), tip_contact);
    let (tip_rim, joint) = add_tip_rim_contact(&mut r, &finish["tip_supports"], &parameters)?;
    r.extra.insert("tip_rim_contact".into(), joint);
    let tip_cooling = tip_end_stretch(&r, &finish["tip_end_cooling"])?;
    if r.rows.len() != 5 {
        bail!("the complete Industrial project needs five rigid parts on one plate");
    }

    // What the profile may change: the trim, its printer identity and that identity's
    // compatibility, the colour, the filament overrides, the layers, the overhang recipe and the
    // shared infill and support settings and cooling stage with its hook.
    let before_settings: Value = serde_json::from_slice(&preserved[SETTINGS_MEMBER])?;
    let after_settings = r.plate.settings.to_value();
    let mut allowed: Vec<String> = ["machine_start_gcode", "printer_settings_id", "print_compatible_printers", "filament_colour", "post_process", "sparse_infill_pattern"]
        .iter().map(|s| s.to_string()).collect();
    allowed.extend(finish["filament_overrides"].as_object().into_iter().flatten().map(|(k, _)| k.clone()));
    allowed.extend(overhang_changes.keys().cloned());
    allowed.extend(layer_changes.keys().cloned());
    allowed.extend(cooling::value_names()?);
    allowed.extend(hsm_print_prep::profile::PETGF_SUPPORT_KEYS.iter().map(|key| key.to_string()));
    let keys: std::collections::BTreeSet<&String> = before_settings.as_object().unwrap().keys().chain(after_settings.as_object().unwrap().keys()).collect();
    let unexpected: Vec<&String> = keys.into_iter().filter(|k| before_settings.get(k.as_str()) != after_settings.get(k.as_str()) && !allowed.contains(k)).collect();
    if !unexpected.is_empty() {
        bail!("unexpected change to the complete PET-GF profile: {unexpected:?}");
    }
    let mut normalized = preserved.clone();
    hsm_print_prep::profile::apply_petgf_support(&mut normalized, &root)?;
    cooling::apply_members(&mut normalized, &hook)?;
    for (name, data) in &normalized {
        if name != SETTINGS_MEMBER && r.plate.members.get(name) != Some(data) {
            bail!("an unrelated PET-GF filament setting changed in {name}");
        }
    }
    let layer_height: f64 = text(&after_settings["layer_height"]).parse()?;
    let first_layer: f64 = text(&after_settings["initial_layer_print_height"]).parse()?;
    let mut changes = r.profile.changes.clone();
    for key in finish["filament_overrides"].as_object().into_iter().flatten().map(|(key, _)| key.as_str()).chain(["sparse_infill_pattern"]) {
        if before_settings.get(key) != after_settings.get(key) {
            changes.insert(key.to_owned(), json!({"from": before_settings.get(key), "to": after_settings.get(key)}));
        }
    }
    changes.extend(overhang_changes);
    changes.extend(layer_changes);
    if original_colour.as_ref() != Some(&json!([colour])) {
        changes.insert("filament_colour".into(), json!({"from": original_colour, "to": [colour]}));
    }
    let selected_faces = shoulder_readings(&r, &recipe_report, layer_height)?;
    let mut source_sha = Map::new();
    let program = here.join("prepare_print_project.rs");
    for path in [program.clone(), recipe.clone(), acceptance_path.clone(), finish_path.clone(), production_path.clone()]
        .into_iter().chain(parts.iter().map(|p| p.source.clone())) {
        source_sha.insert(relative(&path, &root), json!(file_sha(&path)?));
    }
    for path in ["tools/hsm/print-prep/src/faucet.rs", "tools/hsm/print-prep/src/faucet_contact.rs",
        "tools/hsm/print-prep/src/faucet_recesses.rs", "tools/hsm/print-prep/src/profile.rs", "tools/hsm/print-prep/src/rim_contour.rs"] {
        source_sha.insert(path.into(), json!(file_sha(&root.join(path))?));
    }
    for path in faucet_underside::SOURCES {
        source_sha.insert(path.into(), json!(file_sha(&root.join(path))?));
    }
    if let Some(p) = finish["tip_supports"]["source_project"].as_str() {
        source_sha.insert(p.to_string(), json!(file_sha(&root.join(p))?));
    }
    let revision = motion_source["source_commit"].as_str().context("tip contact revision")?;
    let source = motion_source["parameters_source"].as_str().context("tip contact source")?;
    source_sha.insert(format!("{revision}:{source}"), json!(sha256_hex(&motion_bytes)));
    let scope = finish["scope"].clone();
    for (k, v) in [
        ("project_title", json!(TITLE)), ("profile_source", json!(relative(&settings_from, &root))),
        ("shared_tip_source", json!(relative(&parts[1].source, &root))),
        ("gasket_included", json!(false)), ("color_independent_geometry", json!(true)),
        ("accepted_recipe", json!(relative(&recipe, &root))), ("accepted_recipe_sha256", accepted["prepared_project_sha256"].clone()),
        ("approved_geometry_selection", json!(relative(&production_path, &root))), ("physical_production_approval", production["physical_result"].clone()),
        ("active_nozzle", json!(0)), ("printer", json!(printer)), ("requested_z_trim_mm", json!(trim)),
        ("first_bed_layer_height_mm", json!(first_layer)), ("selected_faces", json!(selected_faces)),
        ("insert_review_regions", recipe_report["insert_review_regions"].clone()), ("review_host_regions", recipe_report["review_host_regions"].clone()),
        ("preparation_only", json!(true)), ("launch_authorized", json!(false)), ("submitted", json!(false)), ("send_attempted", json!(false)),
        ("finish_choices_pending", json!([])), ("finish_selection", json!(relative(&finish_path, &root))), ("selected_finish", finish.clone()),
        ("selected_finish_scope", scope),
        ("base_layer_bands", json!(bands.iter().map(|b| json!({"print_z_mm": b, "layer_height_mm": finish["fine_layer_height_mm"]})).collect::<Vec<_>>())),
        ("source_sha256", json!(source_sha)),
    ] {
        r.extra.insert(k.into(), v);
    }
    let mut report = r.write(&root, &project)?;
    report["settings_changes"] = json!(changes);
    report["layer_height_mm"] = json!(layer_height);
    let actual = profile_members(&project)?;
    report["native_settings_sha256"] = json!(sha256_hex(&actual[SETTINGS_MEMBER]));
    report["all_profile_members_preserved_byte_for_byte"] = json!(actual == preserved);
    report["profile_member_sha256"] = json!(actual.iter().map(|(n, d)| (n.clone(), json!(sha256_hex(d)))).collect::<Map<_, _>>());
    for part in &parts {
        if Some(file_sha(&part.source)?) != r.row(&part.name).ok().map(|row| row.stl_sha256.clone()) {
            bail!("{} changed while preparing the project", part.name);
        }
    }
    std::fs::write(project.with_extension("print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    write_readiness(&root, &project, &report, &production, &finish_path, &production_path, None)?;
    println!("{}: five rigid parts on one plate; exact PET-GF settings {}", project.display(), report["settings_sha256"].as_str().unwrap_or(""));
    for row in &r.rows {
        println!("  {}: Rx {} degrees; {} triangles", row.name, python_number(row.angle), row.mesh.faces.len());
    }
    if let Some(directory) = slice_output {
        // Bambu Studio's slice is one of the Mac's heavy runs.
        hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
        let tip = r.row("faucet-shell-tip")?.index;
        let dispense = ContactBand::new(&r.extra["tip_dispense_contact"]["band"])?;
        let joint = ContactBand::new(&r.extra["tip_rim_contact"]["band"])?;
        let mut contact = underside.slice_bands(&root, &mut r, &[(tip, &dispense), (tip, &joint)],
            &project, &directory, &slicer, &finish["rear_seam_enforcement"])?;
        let contact_record = contact.as_object_mut().context("contact motion report")?;
        contact_record.remove("archive");
        contact_record.insert("archive_scope".into(), json!("Sliced contact-stage archive before the scaffold, roof and skin are inserted."));
        let tip_contour = apply_tip_rim_contour(&project, &directory, tip_rim, &joint)?;
        let tip_cooling = apply_stretch_cooling(&project, &directory, "tip-end-cooling", &tip_cooling)?;
        let mut reading = refresh::slice_review(&root, &project, &report, &directory)?;
        let sloped = underside.finish(&root, &project, &directory, &report)?;
        reading["topology_scope"] = json!("Native support paths before the authored scaffold and skin replace the fill.");
        reading["nonplanar_contact"] = contact;
        reading["sloped_underside"] = sloped;
        reading["tip_rim_contour"] = tip_contour;
        reading["tip_end_cooling"] = tip_cooling;
        std::fs::write(project.with_extension("support-audit.json"), serde_json::to_string_pretty(&reading)? + "\n")?;
        write_readiness(&root, &project, &report, &production, &finish_path, &production_path, Some(&reading))?;
        println!("{}", serde_json::to_string_pretty(&reading["sloped_underside"]["fit"])?);
    }
    Ok(())
}

/// What this offline preparation checked.
#[allow(clippy::too_many_arguments)]
fn write_readiness(root: &Path, project: &Path, report: &Value, production: &Value, finish: &Path, selection: &Path,
                   reading: Option<&Value>) -> Result<()> {
    let mut result = json!({
        "project_title": TITLE,
        "status": if reading.is_some() { "approved production geometry and selected-layer native slice reviewed" } else { "approved production geometry prepared; native review pending" },
        "preparation_only": true, "launch_authorized": false, "finish_choices_pending": [], "finish_selection": relative(finish, root),
        "project": relative(project, root), "project_sha256": report["project_sha256"], "settings_sha256": report["settings_sha256"],
        "print_report_sha256": file_sha(&project.with_extension("print.json"))?, "profile_source": report["profile_source"],
        "all_profile_members_preserved_byte_for_byte": report["all_profile_members_preserved_byte_for_byte"],
        "source_stls": report["parts"].as_array().into_iter().flatten().map(|p| (p["source"].as_str().unwrap_or("").to_string(), p["stl_sha256"].clone())).collect::<Map<_, _>>(),
        "mesh_and_placement": {"closed_oriented_single_body_meshes": true, "embedded_meshes_match_source_stls": true,
                               "parts": report["parts"].as_array().map_or(0, Vec::len), "plates": report["plate_count"],
                               "minimum_required_model_bed_margin_mm": PLATE_BORDER},
        "offline_slice": {"completed": reading.is_some()}, "printer_submission": {"performed_by_this_tool": false},
        "physical_print": {"approved_geometry_record": production["physical_result"], "approved_geometry_selection": relative(selection, root),
                           "first_bed_layer_height_mm": report["first_bed_layer_height_mm"], "normal_layer_height_mm": report["layer_height_mm"],
                           "accepted_cosmetic_condition": production["accepted_cosmetic_condition"], "this_archive_printed": false},
        "gasket": {"source": format!("{HERE}/industrial-above-counter-gasket.stl"), "material": "TPU", "included_in_petgf_project": false},
        "color": "The same meshes and project geometry serve black and white PET-GF.",
    });
    if let Some(reading) = reading {
        let slice = result["offline_slice"].as_object_mut().unwrap();
        slice.insert("slicer".into(), reading["slicer"].clone());
        slice.insert("archive_sha256".into(), reading["sloped_underside"]["archive_sha256"].clone());
        slice.insert("gcode_sha256".into(), reading["sloped_underside"]["gcode_sha256"].clone());
        slice.insert("support_audit_sha256".into(), json!(file_sha(&project.with_extension("support-audit.json"))?));
        slice.insert("plates".into(), reading["plates"].clone());
        slice.insert("fit".into(), reading["sloped_underside"]["fit"].clone());
        slice.insert("physical_support_removal_validated".into(), json!(false));
    }
    std::fs::write(project.with_extension("readiness.json"), serde_json::to_string_pretty(&result)? + "\n")?;
    Ok(())
}
