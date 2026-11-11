//! sculpted-faucet-print-project — the complete Sculpted faucet on a PET-GF plate for the
//! selected H2C's hardened left nozzle.
//!
//!     sculpted-faucet-print-project <project.3mf> [--slice-output DIRECTORY]
//!                                 [--printer Mark1|Mark2] [--filament-colour '#RRGGBB']
//!                                 [--base-section SECTION.stl]
//!
//! The five rigid parts are the faucet shell's base and tip, the display cover, the
//! above-counter plate and the side-down lever. Their object settings, the solid foot regions
//! and the finishing steps are the Industrial project's, by part. The Sculpted rim has
//! a shared interface roof and clear mounting insert recesses. The tip's first mating-lip
//! perimeter follows the inclined seat above a dense tree interface.

mod rim_supports;

use anyhow::{bail, Context, Result};
use hsm_faucet_numbers::shell::{FOOT_DEPTH, FOOT_WIDTH, PRINT_BASE_BUILD_ROT, PRINT_TIP_BUILD_ROT};
use hsm_print_prep::faucet::{add_tip_root_anchor, apply_overhang_recipe, archive_members, enforce_rear_seam, file_sha, read_json, recorded_member};
use hsm_print_prep::faucet_contact::{add_base_rim_fins, add_tip_dispense_contact, add_tip_rim_contact, apply_rim_contour, apply_tip_rim_contour, ContactBand};
use hsm_print_prep::faucet_recesses::block_plate_counterbores;
use hsm_print_prep::json::Json;
use hsm_print_prep::profile::{cooling_hook, petgf_infill_pattern, relative};
use hsm_print_prep::refresh::{self, Part, Region};
use hsm_print_prep::rim_contour::RimSpec;
use hsm_print_prep::{root, sha256_hex, slice, xml};
use serde_json::{json, Map, Value};
use std::io::Cursor;
use std::path::PathBuf;

const FAUCET: &str = "hardware/printed-parts/faucet";
const PROFILE: &str = "hardware/printed-parts/faucet/industrial/prints/2026-10-15-all-learnings/mark2/2026-10-15-complete-faucet-all-learnings-mark2-base-arcs-z004.3mf";
const FINISH: &str = "hardware/printed-parts/faucet/sculpted/finish-selection.json";
/// Each part's own space from the shared plate's centre, for its brim and supports.
const OFFSETS: [[f64; 2]; 5] = [[-77.0, 0.0], [20.0, 47.0], [89.0, 76.0], [43.0, -52.0], [-17.5, -60.0]];
/// Each Sculpted part and the Industrial part whose object settings it takes.
const PART_NAMES: [(&str, &str); 5] = [("faucet-shell-base", "industrial-shell-base"), ("faucet-shell-tip", "faucet-shell-tip"),
    ("faucet-display-cover", "sculpted-display-cover"), ("above-counter-plate", "industrial-above-counter-plate"), ("lever-replica", "lever-replica")];
fn main() -> Result<()> {
    let root = root();
    let mut args = std::env::args_os().skip(1);
    let project = PathBuf::from(args.next().context("expected a Sculpted .3mf output path")?);
    let mut slice_output = None;
    let mut base_section = None;
    let mut printer = "Mark2".to_owned();
    let mut colour = "#FFFFFF".to_owned();
    while let Some(arg) = args.next() {
        let value = args.next().with_context(|| format!("{} needs a value", arg.to_string_lossy()))?;
        match arg.to_str() {
            Some("--slice-output") => slice_output = Some(PathBuf::from(value)),
            Some("--base-section") => base_section = Some(PathBuf::from(value)),
            Some("--printer") => printer = value.into_string().ok().context("printer name")?,
            Some("--filament-colour") => colour = value.into_string().ok().context("filament colour")?,
            _ => bail!("unknown argument {}", arg.to_string_lossy()),
        }
    }
    let trim = match printer.as_str() {
        "Mark1" => 0.18,
        "Mark2" => 0.04,
        _ => bail!("expected Mark1 or Mark2, got {printer}"),
    };
    let title = if base_section.is_some() {
        format!("Sculpted faucet support and fit PET-GF left {printer}")
    } else if printer == "Mark2" && colour == "#FFFFFF" {
        "Complete Sculpted white faucet PET-GF left Mark2".to_owned()
    } else {
        format!("Complete Sculpted faucet PET-GF left {printer}")
    };
    let faucet = root.join(FAUCET);
    let selection = read_json(&root.join(FINISH))?;
    let is_section = base_section.is_some();
    let mut parts = vec![
        Part::new("faucet-shell-base", base_section.unwrap_or_else(|| faucet.join("faucet-shell/faucet-shell-base.stl")), -PRINT_BASE_BUILD_ROT.to_degrees()),
        Part::new("faucet-shell-tip", faucet.join("faucet-shell/faucet-shell-tip.stl"), -PRINT_TIP_BUILD_ROT.to_degrees()),
        Part::new("faucet-display-cover", faucet.join("faucet-display-cover/faucet-display-cover.stl"), -50.0),
    ];
    if !is_section {
        parts.extend([
            Part::new("above-counter-plate", faucet.join("above-counter-plate/above-counter-plate.stl"), 0.0),
            Part::new("lever-replica", faucet.join("lever-replica/lever-replica-side-down.stl"), 0.0),
        ]);
    }
    let mut r = refresh::refresh(&root, &root.join(PROFILE), &parts, &OFFSETS[..parts.len()], &title, Some(trim), 40.0)?;
    let parent = &selection["industrial_recipe"];
    let parent_project_source = parent["project"].as_str().context("Industrial parent project")?;
    let parent_report_source = parent["report"].as_str().context("Industrial parent report")?;
    let parent_revision = parent["source_commit"].as_str().context("Industrial parent revision")?;
    let parent_project_bytes = recorded_member(&root, parent, "project")?;
    let parent_report_bytes = recorded_member(&root, parent, "report")?;
    let parent_report: Value = serde_json::from_slice(&parent_report_bytes)?;
    let regions: Vec<Region> = parent_report["local_solid_regions"].as_array().into_iter().flatten().map(|row| {
        let b = &row["source_bounds_mm"];
        let mut declared = row.as_object().cloned().unwrap_or_default();
        declared.insert("part".into(), json!("faucet-shell-base"));
        declared.insert("clip_to_part_bounds".into(), json!(false));
        Ok(Region { part: "faucet-shell-base".into(), name: row["name"].as_str().context("region name")?.to_string(),
                    low: [0, 1, 2].map(|k| b[0][k].as_f64().unwrap_or(f64::NAN)), high: [0, 1, 2].map(|k| b[1][k].as_f64().unwrap_or(f64::NAN)),
                    clip_to_part_bounds: false, declared: Value::Object(declared) })
    }).collect::<Result<_>>()?;
    r.add_local_solid_regions(&regions)?;
    let parent = archive_members(Cursor::new(&parent_project_bytes))?;
    let parent_config = xml::parse(std::str::from_utf8(&parent["Metadata/model_settings.config"])?)?;
    let shell_gap = selection["shell_ordinary_seam_gap"].as_str().context("shell seam gap")?;
    for obj in r.plate.objects.iter_mut() {
        let industrial = PART_NAMES.iter().find(|(s, _)| *s == obj.name).map(|(_, i)| *i).context("a part without its Industrial counterpart")?;
        let source = parent_config.children_named("object")
            .find(|o| o.children_named("metadata").any(|m| m.attribute("key") == Some("name") && m.attribute("value") == Some(industrial)))
            .with_context(|| format!("the Industrial project has no {industrial}"))?;
        for m in source.children_named("metadata") {
            if let (Some(k), Some(v)) = (m.attribute("key"), m.attribute("value")) {
                if k != "name" && k != "extruder" && !hsm_print_prep::profile::PETGF_SUPPORT_KEYS.contains(&k) {
                    obj.settings.push((k.to_string(), v.to_string()));
                }
            }
        }
        if matches!(obj.name.as_str(), "faucet-shell-base" | "faucet-shell-tip") {
            obj.settings.retain(|(key, _)| key != "seam_gap");
            obj.settings.push(("seam_gap".into(), shell_gap.into()));
        }
    }
    let original = r.plate.settings.clone();
    let hook = cooling_hook(&root);
    apply_overhang_recipe(&mut r.plate.settings, &selection["overhang_recipe"], &hook)?;
    r.plate.settings.set("sparse_infill_pattern", Json::Text(petgf_infill_pattern(&root)?));
    let text = |s: &str| Json::Text(s.into());
    let list = |items: &[&str]| Json::List(items.iter().map(|s| Json::Text(s.to_string())).collect());
    r.plate.settings.set("filament_map", list(&["1"]));
    r.plate.settings.set("filament_nozzle_map", list(&["0"]));
    r.plate.settings.set("filament_map_mode", text("Manual"));
    r.plate.settings.set("filament_colour", list(&[&colour]));
    if r.plate.settings.get("filament_multi_colour").is_some() {
        r.plate.settings.set("filament_multi_colour", list(&[&colour]));
    }
    r.plate.filament_map_mode = "Manual".into();
    for key in ["rear_seam_enforcement", "tip_rear_seam_enforcement"] {
        let record = enforce_rear_seam(&mut r, &selection[key])?;
        r.extra.insert(key.into(), record);
    }
    let base = r.row("faucet-shell-base")?.index;
    let mut rim = rim_supports::add(&mut r, &selection["base_rim_supports"])?;
    let contact = &selection["base_rim_supports"]["nonplanar_contact"];
    let mapping_source = contact["parameters_source"].as_str().context("contact parameters source")?;
    let mapping_revision = contact["source_commit"].as_str().context("contact parameters revision")?;
    let mapping_bytes = recorded_member(&root, contact, "parameters_source")?;
    let mapping: Value = serde_json::from_slice(&mapping_bytes)?;
    let center: [f64; 3] = serde_json::from_value(rim["seat_print_world_center_mm"].clone())?;
    let supported_angles = serde_json::from_value(selection["base_rim_supports"]["rim_enforcer_angle_degrees"].clone())?;
    let contour = RimSpec {
        identify_id: r.plate.objects[base].identify_id as u64,
        center_mm: center,
        seat_fall_angle_degrees: PRINT_BASE_BUILD_ROT.to_degrees(),
        semi_axes_mm: [FOOT_WIDTH / 2.0, FOOT_DEPTH / 2.0],
        supported_angles_degrees: supported_angles,
    };
    rim["fin_layout"] = add_base_rim_fins(&root, &mut r, base, contour, &selection["base_rim_supports"])?;
    let half_span = FOOT_WIDTH.max(FOOT_DEPTH) / 2.0;
    let margin = contact["scope_margin_mm"].as_f64().context("contact scope margin")?;
    let bounds = [-1.0, 1.0].map(|direction| {
        [0, 1].map(|axis| center[axis] + direction * (half_span + margin))
    });
    let mut base_parameters = mapping["parameters"].clone();
    let mesh_error = base_parameters["maximum_mesh_mapping_error_mm"].as_f64().context("contact mesh tolerance")?;
    base_parameters["maximum_mesh_mapping_error_mm"] = json!(mesh_error / 2.);
    let contact_spec = json!({
        "part": "faucet-shell-base",
        "parameters": base_parameters,
        "plane_normal": rim["seat_print_world_outward_normal"],
        "seat_plate_mm": center,
        "bounds_mm": bounds,
        "edge_blend_mm": contact["edge_blend_mm"],
        "rim_semi_axes_mm": contour.semi_axes_mm,
        "rim_inboard_blend_mm": [0.85, 2.85],
        "refine_mesh_interiors": true,
        "supported_angles_degrees": supported_angles,
    });
    r.extra.insert("base_rim_supports".into(), rim);
    r.extra.insert("nonplanar_contact".into(), contact_spec.clone());
    if !is_section {
        let pocket_recipe = &selection["mounting_plate_counterbores"];
        let radial_clearance = pocket_recipe["blocker_radial_clearance_mm"].as_f64().context("counterbore blocker clearance")?;
        let depth_allowance = serde_json::from_value(pocket_recipe["blocker_depth_allowance_mm"].clone())?;
        let counterbores = block_plate_counterbores(&mut r, "above-counter-plate", radial_clearance, depth_allowance)?;
        r.extra.insert("mounting_plate_counterbores".into(), counterbores);
    }
    let tip = add_tip_root_anchor(&root, &mut r, &selection["tip_supports"])?;
    r.extra.insert("tip_supports".into(), tip);
    let tip_index = r.row("faucet-shell-tip")?.index;
    let tip_contact = add_tip_dispense_contact(&mut r, &selection["tip_dispense_contact"], &mapping["parameters"])?;
    let tip_band_spec = tip_contact["band"].clone();
    r.extra.insert("tip_dispense_contact".into(), tip_contact);
    let (tip_rim, joint) = add_tip_rim_contact(&mut r, &selection["tip_supports"], &mapping["parameters"])?;
    let joint_band_spec = joint["band"].clone();
    r.extra.insert("tip_rim_contact".into(), joint);

    let mut changes = r.profile.changes.clone();
    if let Json::Map(entries) = &r.plate.settings {
        for (key, value) in entries {
            if original.get(key) != Some(value) {
                changes.insert(key.clone(), json!({"from": original.get(key).map(Json::to_value), "to": value.to_value()}));
            }
        }
    }
    let mut sources = Map::new();
    sources.insert(format!("{mapping_revision}:{mapping_source}"), json!(sha256_hex(&mapping_bytes)));
    sources.insert(format!("{parent_revision}:{parent_project_source}"), json!(sha256_hex(&parent_project_bytes)));
    sources.insert(format!("{parent_revision}:{parent_report_source}"), json!(sha256_hex(&parent_report_bytes)));
    let rim_footprint = selection["base_rim_supports"]["source_preparation"].as_str().context("accepted fin footprint source")?;
    for p in ["hardware/printed-parts/faucet/sculpted/prepare_print_project.rs",
        "hardware/printed-parts/faucet/sculpted/rim_supports.rs",
        "tools/hsm/print-prep/src/faucet.rs", "tools/hsm/print-prep/src/faucet_contact.rs", "tools/hsm/print-prep/src/faucet_recesses.rs",
        "tools/hsm/print-prep/src/profile.rs", "tools/hsm/print-prep/src/rim_contour.rs",
        FINISH, PROFILE, rim_footprint].iter().map(|p| root.join(p))
        .chain(parts.iter().map(|p| p.source.clone())) {
        sources.insert(relative(&p, &root), json!(file_sha(&p)?));
    }
    if let Some(parent) = project.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut report = r.write(&root, &project)?;
    for (k, v) in [
        ("project", json!(relative(&project, &root))), ("native_settings_sha256", report["settings_sha256"].clone()),
        ("printer", json!(printer)), ("active_nozzle", json!(0)), ("external_spool", json!(254)), ("requested_z_trim_mm", json!(trim)),
        ("filament_colour", json!(colour)), ("parent_project", json!(parent_project_source)),
        ("parent_project_sha256", json!(sha256_hex(&parent_project_bytes))), ("parent_project_source_commit", json!(parent_revision)),
        ("profile_source", json!(PROFILE)), ("profile_source_sha256", json!(file_sha(&root.join(PROFILE))?)),
        ("finish_selection", json!(FINISH)), ("finish_selection_sha256", json!(file_sha(&root.join(FINISH))?)), ("selected_finish", selection.clone()),
        ("layer_config_ranges", json!([])),
        ("layer_scope", json!("Use the shared first and ordinary layer heights across the plate.")),
        ("settings_changes", json!(changes)), ("rigid_part_count", json!(parts.len())),
        ("preparation_only", json!(true)), ("submitted", json!(false)), ("send_attempted", json!(false)),
        ("source_sha256", json!(sources)),
    ] {
        report[k] = v;
    }
    std::fs::write(project.with_extension("print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    println!("{}", project.display());
    if let Some(directory) = slice_output {
        let band = ContactBand::new(&contact_spec)?;
        let tip_band = ContactBand::new(&tip_band_spec)?;
        let joint = ContactBand::new(&joint_band_spec)?;
        let motion = ContactBand::slice_bands(&mut r.plate, &[(base, &band), (tip_index, &tip_band), (tip_index, &joint)], &project, &directory,
            std::path::Path::new(slice::SLICER))?;
        let rim = apply_rim_contour(&project, &directory, contour, &band)?;
        let tip_contour = apply_tip_rim_contour(&project, &directory, tip_rim, &joint)?;
        report["nonplanar_motion"] = motion;
        report["rim_contour"] = rim;
        report["tip_rim_contour"] = tip_contour;
        report["preparation_only"] = json!(false);
        std::fs::write(project.with_extension("print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    }
    Ok(())
}
