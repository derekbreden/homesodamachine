//! sculpted-faucet-print-project — the complete Sculpted faucet on one white PET-GF plate, with
//! the selected Industrial print process, on Mark2's right nozzle. Run by hand; slicing and
//! printer submission are separate operations.
//!
//!     sculpted-faucet-print-project <project.3mf>
//!
//! The five rigid parts are the faucet shell's base and tip, the display cover, the
//! above-counter plate and the side-down lever. Their object settings, the solid foot regions
//! and the finishing steps are the Industrial project's, by part. The layout is centred in the
//! right nozzle's own reachable area, and the accepted rim arcs are fitted to the Sculpted foot's
//! ellipse.

use anyhow::{Context, Result};
use hsm_faucet_numbers::shell::{PRINT_BASE_BUILD_ROT, PRINT_TIP_BUILD_ROT};
use hsm_print_prep::faucet::{add_selected_base_rim, add_selected_tip_supports, apply_overhang_recipe, enforce_rear_seam, file_sha, members, read_json};
use hsm_print_prep::json::Json;
use hsm_print_prep::profile::{cooling_hook, relative};
use hsm_print_prep::refresh::{self, Part, Region};
use hsm_print_prep::{root, xml};
use serde_json::{json, Map, Value};
use std::path::PathBuf;

const FAUCET: &str = "hardware/printed-parts/faucet";
const PARENT: &str = "hardware/printed-parts/faucet/industrial/faucet-industrial-petgf.3mf";
const PROFILE: &str = "hardware/printed-parts/faucet/industrial/prints/2026-10-15-all-learnings/mark2/2026-10-15-complete-faucet-all-learnings-mark2-base-arcs-z004.3mf";
const FINISH: &str = "hardware/printed-parts/faucet/sculpted/finish-selection.json";
const REGISTRATION: &str = "hardware/printed-parts/calibration/dual-nozzle-registration/mark2-registration.json";
const TITLE: &str = "Complete Sculpted white faucet PET-GF right Mark2";
/// Each part's own space from the shared plate's centre, for its brim and supports.
const OFFSETS: [[f64; 2]; 5] = [[-77.0, 0.0], [20.0, 47.0], [89.0, 76.0], [43.0, -52.0], [-17.5, -60.0]];
/// Each Sculpted part and the Industrial part whose object settings it takes.
const PART_NAMES: [(&str, &str); 5] = [("faucet-shell-base", "industrial-shell-base"), ("faucet-shell-tip", "faucet-shell-tip"),
    ("faucet-display-cover", "sculpted-display-cover"), ("above-counter-plate", "industrial-above-counter-plate"), ("lever-replica", "lever-replica")];
/// The Sculpted foot's span across X and along Y, and the accepted Industrial rim's diameter.
const SCULPTED_FOOT: [f64; 2] = [58.0, 59.0];
const INDUSTRIAL_RIM: f64 = 59.0;
/// Mark2's right nozzle's native offset, as the registration measured it.
const RIGHT_TOOL_OFFSET: [f64; 3] = [-0.5, 0.7, 0.0];

fn main() -> Result<()> {
    let root = root();
    let project = PathBuf::from(std::env::args().nth(1).context("usage: sculpted-faucet-print-project <project.3mf>")?);
    let faucet = root.join(FAUCET);
    let selection = read_json(&root.join(FINISH))?;
    let parts = vec![
        Part::new("faucet-shell-base", faucet.join("faucet-shell/faucet-shell-base.stl"), -PRINT_BASE_BUILD_ROT.to_degrees()),
        Part::new("faucet-shell-tip", faucet.join("faucet-shell/faucet-shell-tip.stl"), -PRINT_TIP_BUILD_ROT.to_degrees()),
        Part::new("faucet-display-cover", faucet.join("faucet-display-cover/faucet-display-cover.stl"), -50.0),
        Part::new("above-counter-plate", faucet.join("above-counter-plate/above-counter-plate.stl"), 0.0),
        Part::new("lever-replica", faucet.join("lever-replica/lever-replica-side-down.stl"), 0.0),
    ];
    let mut r = refresh::refresh(&root, &root.join(PROFILE), &parts, &OFFSETS, TITLE, Some(0.04), 40.0)?;
    let parent_report = read_json(&root.join(PARENT).with_extension("print.json"))?;
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
    let parent = members(&root.join(PARENT))?;
    let parent_config = xml::parse(std::str::from_utf8(&parent["Metadata/model_settings.config"])?)?;
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
    }
    let original = r.plate.settings.clone();
    let hook = cooling_hook(&root);
    apply_overhang_recipe(&mut r.plate.settings, &selection["overhang_recipe"], &hook)?;
    let text = |s: &str| Json::Text(s.into());
    let list = |items: &[&str]| Json::List(items.iter().map(|s| Json::Text(s.to_string())).collect());
    r.plate.settings.set("filament_map", list(&["2"]));
    r.plate.settings.set("filament_nozzle_map", list(&["1"]));
    r.plate.settings.set("filament_map_mode", text("Manual"));
    // Both of Mark2's hotends are hardened; this preset's saved mask names only the left one.
    r.plate.settings.set("filament_printable", list(&["3"]));
    r.plate.settings.set("filament_colour", list(&["#FFFFFF"]));
    if r.plate.settings.get("filament_multi_colour").is_some() {
        r.plate.settings.set("filament_multi_colour", list(&["#FFFFFF"]));
    }
    let registration = read_json(&root.join(REGISTRATION))?;
    r.plate.settings.set("extruder_offset", Json::from_value(&registration["native_extruder_offset"]));
    // The refresh started from the left nozzle's profile: centre the layout in the right
    // nozzle's own reachable area before the aids go on.
    let area = r.plate.settings.get("extruder_printable_area").map(Json::list).and_then(|l| l.get(1)).and_then(Json::text).context("the right nozzle's area")?;
    let points: Vec<[f64; 2]> = area.split(',').map(|p| {
        let (x, y) = p.split_once('x').context("an area point")?;
        Ok([x.trim().parse()?, y.trim().parse()?])
    }).collect::<Result<_>>()?;
    let low = [points.iter().map(|p| p[0]).fold(f64::INFINITY, f64::min), points.iter().map(|p| p[1]).fold(f64::INFINITY, f64::min)];
    let high = [points.iter().map(|p| p[0]).fold(f64::NEG_INFINITY, f64::max), points.iter().map(|p| p[1]).fold(f64::NEG_INFINITY, f64::max)];
    let shared = (r.profile.usable_low, r.profile.usable_high);
    let delta = [(low[0] + high[0]) / 2.0 - (shared.0[0] + shared.1[0]) / 2.0, (low[1] + high[1]) / 2.0 - (shared.0[1] + shared.1[1]) / 2.0];
    for row in r.rows.iter_mut() {
        for k in 0..2 {
            row.translation[k] += delta[k];
            row.low[k] += delta[k];
            row.high[k] += delta[k];
        }
        r.plate.objects[row.index].translation = row.translation;
    }
    r.plate.filament_maps = Some("2".into());
    r.plate.filament_map_mode = "Manual".into();
    for key in ["rear_seam_enforcement", "tip_rear_seam_enforcement"] {
        let record = enforce_rear_seam(&mut r, &selection[key])?;
        r.extra.insert(key.into(), record);
    }
    let base = r.row("faucet-shell-base")?.index;
    let before = r.plate.objects[base].parts.len();
    let mut rim = add_selected_base_rim(&root, &mut r, &selection["base_rim_supports"])?;
    // The accepted rim is round; the Sculpted foot is an ellipse. Fit the same contact and
    // release arrangement to it.
    let scale = SCULPTED_FOOT[0] / INDUSTRIAL_RIM;
    let cx = r.plate.objects[base].source_center[0];
    for part in r.plate.objects[base].parts[before..].iter_mut() {
        for v in part.vertices.iter_mut() {
            v[0] = (v[0] + cx) * scale - cx;
        }
    }
    rim["cad_scale"] = json!([scale, 1.0, 1.0]);
    rim["target_foot_xy_mm"] = json!(SCULPTED_FOOT);
    rim["scope"] = json!("Accepted seven segmented rim arcs and local contact blockers fitted to the Sculpted elliptical rim. Build Z, release angles and requested gap are retained; Tree(auto)/Default elsewhere.");
    r.extra.insert("base_rim_supports".into(), rim);
    let tip = add_selected_tip_supports(&root, &mut r, &selection["tip_supports"])?;
    r.extra.insert("tip_supports".into(), tip);

    let mut changes = r.profile.changes.clone();
    if let Json::Map(entries) = &r.plate.settings {
        for (key, value) in entries {
            if original.get(key) != Some(value) {
                changes.insert(key.clone(), json!({"from": original.get(key).map(Json::to_value), "to": value.to_value()}));
            }
        }
    }
    let mut sources = Map::new();
    for p in ["hardware/printed-parts/faucet/sculpted/prepare_print_project.rs", FINISH, PARENT, PROFILE, REGISTRATION].iter().map(|p| root.join(p))
        .chain(parts.iter().map(|p| p.source.clone())) {
        sources.insert(relative(&p, &root), json!(file_sha(&p)?));
    }
    if let Some(parent) = project.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut report = r.write(&root, &project)?;
    for (k, v) in [
        ("project", json!(relative(&project, &root))), ("native_settings_sha256", report["settings_sha256"].clone()),
        ("printer", json!("Mark2")), ("active_nozzle", json!(1)), ("external_spool", json!(255)), ("requested_z_trim_mm", json!(0.04)),
        ("filament_colour", json!("#FFFFFF")), ("parent_project", json!(PARENT)), ("parent_project_sha256", json!(file_sha(&root.join(PARENT))?)),
        ("profile_source", json!(PROFILE)), ("profile_source_sha256", json!(file_sha(&root.join(PROFILE))?)),
        ("finish_selection", json!(FINISH)), ("finish_selection_sha256", json!(file_sha(&root.join(FINISH))?)), ("selected_finish", selection.clone()),
        ("layer_config_ranges", json!([])),
        ("layer_scope", json!("0.20 mm first bed layer; 0.24 mm thereafter on all five parts. No Industrial shoulder bands or separate eight-layer override.")),
        ("settings_changes", json!(changes)), ("native_right_tool_offset_mm", json!(RIGHT_TOOL_OFFSET)), ("rigid_part_count", json!(5)),
        ("preparation_only", json!(true)), ("submitted", json!(false)), ("send_attempted", json!(false)),
        ("authorization_quote", selection["authorization_quote"].clone()), ("source_sha256", json!(sources)),
        ("shared_printable_area_mm", json!([low, high])), ("printable_area_extruders", json!([1])),
        ("right_nozzle_layout_translation_xy_mm", json!(delta)),
    ] {
        report[k] = v;
    }
    std::fs::write(project.with_extension("print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    println!("{}", project.display());
    Ok(())
}
