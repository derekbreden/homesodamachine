//! sculpted-faucet-print-project — the complete Sculpted faucet on a PET-GF plate for the
//! selected H2C's hardened left nozzle.
//!
//!     sculpted-faucet-print-project <project.3mf> [--slice-output DIRECTORY]
//!                                 [--printer Mark1|Mark2] [--filament-colour '#RRGGBB']
//!                                 [--base-only] [--base-section SECTION.stl | --tip-only | --tip-and-cover]
//!                                 [--filled-base FILLED.stl | --physical-base]
//!                                 [--tip-mesh TIP.stl --cover-mesh COVER.stl]
//!                                 [--warp-donor --tip-mesh TIP.stl [--warp-settings SETTINGS.json]]
//!                                 [--finish SELECTION.json]
//!
//! The five rigid parts are the faucet shell's base and tip, the display cover, the
//! above-counter plate and the side-down lever. Their object settings, the solid foot regions
//! and the finishing steps are the Industrial project's, by part. The base starts on a
//! sloped scaffold and keeps its mounting insert recesses clear. The tip's first mating-lip
//! perimeter follows the inclined seat above a dense tree interface, and its model paths by the
//! dispense face take part cooling. `--filled-base` gives the slicer the base with the space under
//! its mounting face filled to the bed, for the stage that prints that space as a scaffold with a
//! sloped roof and skin: the base then takes no rim supports and no contact band here, and the
//! lever stands clear of the toolhead's reach over that scaffold. `--physical-base` writes that
//! layout's editable project with the actual base. `--tip-mesh` and `--cover-mesh` put a trial's
//! tip and cover on that plate; `--warp-donor` slices a warped tip alone, in fine course bands
//! with a removable roof under its virtual shoulder, for the stage that lays its courses back
//! onto the real shoulder. `--warp-settings` supplies the donor's course bands and support
//! regions in the warped mesh's coordinates. `--finish` reads a trial's finish selection in
//! place of the standing one.

mod rim_supports;

use anyhow::{bail, ensure, Context, Result};
use hsm_faucet_numbers::shell::{FOOT_DEPTH, FOOT_WIDTH, PRINT_BASE_BUILD_ROT, PRINT_TIP_BUILD_ROT};
use hsm_print_prep::faucet::{add_tip_root_anchor, apply_overhang_recipe, archive_members, enforce_rear_seam, file_sha, read_json, recorded_member};
use hsm_print_prep::faucet_contact::{add_base_rim_fins, add_tip_dispense_contact, add_tip_rim_contact, apply_rim_contour, apply_stretch_cooling, apply_tip_rim_contour, closed_rim_strip, tip_end_stretch, ContactBand};
use hsm_print_prep::faucet_recesses::block_plate_counterbores;
use hsm_print_prep::faucet_underside::{self, Underside};
use hsm_print_prep::json::Json;
use hsm_print_prep::profile::{cooling_hook, petgf_infill_pattern, relative};
use hsm_print_prep::refresh::{self, Part, Refreshed, Region};
use hsm_print_prep::rim_contour::RimSpec;
use hsm_print_prep::{apply, root, sha256_hex, slice, xml};
use serde_json::{json, Map, Value};
use std::io::Cursor;
use std::path::{Path, PathBuf};

const FAUCET: &str = "hardware/printed-parts/faucet";
const PROFILE: &str = "hardware/printed-parts/faucet/industrial/prints/2026-10-15-all-learnings/mark2/2026-10-15-complete-faucet-all-learnings-mark2-base-arcs-z004.3mf";
const FINISH: &str = "hardware/printed-parts/faucet/sculpted/finish-selection.json";
/// Each part's own space from the shared plate's centre, for its brim and supports.
const OFFSETS: [[f64; 2]; 5] = [[-77.0, 0.0], [20.0, 47.0], [89.0, 76.0], [43.0, -52.0], [-17.5, -60.0]];
const TIP_AND_COVER_OFFSETS: [[f64; 2]; 2] = [[-31.0, 0.0], [31.0, 0.0]];
/// The full plate's spaces when the base's scaffold stands before the other parts start: the
/// lever beyond the above-counter plate, where the toolhead over it stays off the scaffold.
const FILLED_BASE_OFFSETS: [[f64; 2]; 5] = [[-77.0, 0.0], [24.0, 47.0], [89.0, 76.0], [43.0, -52.0], [94.0, -58.0]];
/// A warp donor tip's virtual course bands: from and to slicing height, and the layer height,
/// finer through the slopes into and out of its flat virtual shoulder.
const WARP_DONOR_BANDS: [[f64; 3]; 2] = [[0.20, 21.80, 0.16], [23.96, 62.12, 0.18]];
/// Each Sculpted part and the Industrial part whose object settings it takes.
const PART_NAMES: [(&str, &str); 5] = [("faucet-shell-base", "industrial-shell-base"), ("faucet-shell-tip", "faucet-shell-tip"),
    ("faucet-display-cover", "sculpted-display-cover"), ("above-counter-plate", "industrial-above-counter-plate"), ("lever-replica", "lever-replica")];
fn main() -> Result<()> {
    let root = root();
    let mut args = std::env::args_os().skip(1);
    let project = PathBuf::from(args.next().context("expected a Sculpted .3mf output path")?);
    let mut slice_output = None;
    let mut base_section = None;
    let mut filled_base = None;
    let mut physical_base = false;
    let mut tip_mesh = None;
    let mut cover_mesh = None;
    let mut warp_donor = false;
    let mut warp_settings_path = None;
    let mut finish = PathBuf::from(FINISH);
    let mut base_only = false;
    let mut tip_only = false;
    let mut tip_and_cover = false;
    let mut printer = "Mark2".to_owned();
    let mut colour = "#FFFFFF".to_owned();
    while let Some(arg) = args.next() {
        if arg == "--physical-base" {
            physical_base = true;
            continue;
        }
        if arg == "--warp-donor" {
            tip_only = true;
            warp_donor = true;
            continue;
        }
        if arg == "--base-only" {
            base_only = true;
            continue;
        }
        if arg == "--tip-only" {
            tip_only = true;
            continue;
        }
        if arg == "--tip-and-cover" {
            tip_and_cover = true;
            continue;
        }
        let value = args.next().with_context(|| format!("{} needs a value", arg.to_string_lossy()))?;
        match arg.to_str() {
            Some("--slice-output") => slice_output = Some(PathBuf::from(value)),
            Some("--base-section") => base_section = Some(PathBuf::from(value)),
            Some("--filled-base") => filled_base = Some(PathBuf::from(value)),
            Some("--tip-mesh") => tip_mesh = Some(PathBuf::from(value)),
            Some("--cover-mesh") => cover_mesh = Some(PathBuf::from(value)),
            Some("--warp-settings") => warp_settings_path = Some(PathBuf::from(value)),
            Some("--finish") => finish = PathBuf::from(value),
            Some("--printer") => printer = value.into_string().ok().context("printer name")?,
            Some("--filament-colour") => colour = value.into_string().ok().context("filament colour")?,
            _ => bail!("unknown argument {}", arg.to_string_lossy()),
        }
    }
    let include_base = !tip_only && !tip_and_cover;
    let sloped_layout = filled_base.is_some() || physical_base;
    ensure!(!physical_base || (filled_base.is_none() && slice_output.is_none()),
        "--physical-base writes the editable project with the actual base mesh");
    ensure!(!sloped_layout || (include_base && !base_only && base_section.is_none()),
        "the sloped layout prepares the complete plate");
    if warp_donor {
        ensure!(tip_mesh.is_some() && cover_mesh.is_none(), "a donor needs only the tip mesh");
    } else {
        ensure!(tip_mesh.is_some() == cover_mesh.is_some() && (tip_mesh.is_none() || sloped_layout),
            "the two trial head meshes replace the tip and cover on the sloped plate");
    }
    ensure!(!(tip_only && tip_and_cover) && (include_base || (!base_only && base_section.is_none())),
        "--base-only and --base-section cannot be combined with a tip plate");
    ensure!(warp_donor || warp_settings_path.is_none(), "--warp-settings requires --warp-donor");
    let warp_settings = warp_settings_path.as_deref().map(WarpSettings::read).transpose()?;
    let trim = hsm_print_prep::profile::petgf_z_trim(&root, &printer)?;
    let title = if base_only {
        format!("Sculpted faucet base PET-GF left {printer}")
    } else if warp_donor {
        format!("Sculpted faucet tip inverse warp donor PET-GF left {printer}")
    } else if tip_only {
        format!("Sculpted faucet tip PET-GF left {printer}")
    } else if tip_and_cover {
        format!("Sculpted faucet tip and display cover PET-GF left {printer}")
    } else if base_section.is_some() {
        format!("Sculpted faucet support and fit PET-GF left {printer}")
    } else if sloped_layout {
        format!("Complete Sculpted faucet sloped underside PET-GF left {printer}")
    } else if printer == "Mark2" && colour == "#FFFFFF" {
        "Complete Sculpted white faucet PET-GF left Mark2".to_owned()
    } else {
        format!("Complete Sculpted faucet PET-GF left {printer}")
    };
    let faucet = root.join(FAUCET);
    let finish = relative(&root.join(&finish), &root);
    let selection = read_json(&root.join(&finish))?;
    let full_plate = include_base && !base_only && base_section.is_none();
    let mut parts = Vec::new();
    if include_base {
        let source = filled_base.clone().or(base_section).unwrap_or_else(|| faucet.join("faucet-shell/faucet-shell-base.stl"));
        parts.push(Part::new("faucet-shell-base", source, -PRINT_BASE_BUILD_ROT.to_degrees()));
    }
    if !base_only {
        let source = tip_mesh.unwrap_or_else(|| faucet.join("faucet-shell/faucet-shell-tip.stl"));
        parts.push(Part::new("faucet-shell-tip", source, -PRINT_TIP_BUILD_ROT.to_degrees()));
    }
    if !base_only && !tip_only {
        let source = cover_mesh.unwrap_or_else(|| faucet.join("faucet-display-cover/faucet-display-cover.stl"));
        parts.push(Part::new("faucet-display-cover", source, -50.0));
    }
    if full_plate {
        parts.extend([
            Part::new("above-counter-plate", faucet.join("above-counter-plate/above-counter-plate.stl"), 0.0),
            Part::new("lever-replica", faucet.join("lever-replica/lever-replica-side-down.stl"), 0.0),
        ]);
    }
    let offsets = if base_only || tip_only {
        &[[0.0, 0.0]][..]
    } else if tip_and_cover {
        &TIP_AND_COVER_OFFSETS[..]
    } else if full_plate {
        &FILLED_BASE_OFFSETS[..]
    } else {
        &OFFSETS[..parts.len()]
    };
    let mut r = refresh::refresh(&root, &root.join(PROFILE), &parts, offsets, &title, Some(trim), 40.0)?;
    let parent = &selection["industrial_recipe"];
    let parent_project_source = parent["project"].as_str().context("Industrial parent project")?;
    let parent_report_source = parent["report"].as_str().context("Industrial parent report")?;
    let parent_revision = parent["source_commit"].as_str().context("Industrial parent revision")?;
    let parent_project_bytes = recorded_member(&root, parent, "project")?;
    let parent_report_bytes = recorded_member(&root, parent, "report")?;
    if include_base {
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
    }
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
        if (sloped_layout && obj.name == "faucet-shell-base") || (warp_donor && obj.name == "faucet-shell-tip") {
            obj.settings.retain(|(key, _)| key != "seam_slope_type");
            obj.settings.push(("seam_slope_type".into(), "none".into()));
        }
        if tip_and_cover && obj.name == "faucet-shell-tip" {
            // Anchor the tip's small bed contacts with an attached outer brim.
            let brim = [("brim_type", "outer_only"), ("brim_width", "7"), ("brim_object_gap", "0")];
            obj.settings.retain(|(key, _)| !brim.iter().any(|(setting, _)| key == setting));
            obj.settings.extend(brim.map(|(key, value)| (key.into(), value.into())));
        }
    }
    let original = r.plate.settings.clone();
    if warp_donor {
        let bands = warp_settings.as_ref().map_or(WARP_DONOR_BANDS.as_slice(), |settings| settings.course_bands_mm.as_slice());
        let index = r.row("faucet-shell-tip")?.index;
        r.plate.objects[index].ranges = bands.iter().copied().map(|[min_z, max_z, height]|
            hsm_print_prep::project::Range {
                min_z, max_z, options: vec![("layer_height".into(), height.to_string())],
            }).collect();
        r.extra.insert("tip_virtual_course_bands_mm".into(), json!(bands));
    }
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
    let seam_keys = if base_only {
        &["rear_seam_enforcement"][..]
    } else if tip_only {
        &["tip_rear_seam_enforcement"][..]
    } else if tip_and_cover {
        &["tip_rear_seam_enforcement", "cover_rear_seam_enforcement"][..]
    } else {
        &["rear_seam_enforcement", "tip_rear_seam_enforcement", "cover_rear_seam_enforcement"][..]
    };
    for &key in seam_keys {
        let record = enforce_rear_seam(&mut r, &selection[key])?;
        r.extra.insert(key.into(), record);
    }
    let contact = &selection["base_rim_supports"]["nonplanar_contact"];
    let mapping_source = contact["parameters_source"].as_str().context("contact parameters source")?;
    let mapping_revision = contact["source_commit"].as_str().context("contact parameters revision")?;
    let mapping_bytes = recorded_member(&root, contact, "parameters_source")?;
    let mapping: Value = serde_json::from_slice(&mapping_bytes)?;
    let underside = if include_base && !sloped_layout && (full_plate || base_only) {
        Some(Underside::prepare(&mut r, "faucet-shell-base",
            [FOOT_WIDTH / 2.0, FOOT_DEPTH / 2.0], &selection["base_underside"])?)
    } else {
        None
    };
    let base_contact = if sloped_layout {
        // The fill stands where the rim's supports would: only the insert recesses' blockers and
        // the base's support settings apply.
        let seat = rim_supports::add(&mut r, &selection["base_rim_supports"], false)?;
        r.extra.insert("base_rim_supports".into(), seat);
        None
    } else {
        (include_base && underside.is_none())
            .then(|| prepare_base_contact(&root, &mut r, &selection["base_rim_supports"], &mapping["parameters"]))
            .transpose()?
    };
    if full_plate {
        let pocket_recipe = &selection["mounting_plate_counterbores"];
        let radial_clearance = pocket_recipe["blocker_radial_clearance_mm"].as_f64().context("counterbore blocker clearance")?;
        let depth_allowance = serde_json::from_value(pocket_recipe["blocker_depth_allowance_mm"].clone())?;
        let counterbores = block_plate_counterbores(&mut r, "above-counter-plate", radial_clearance, depth_allowance)?;
        r.extra.insert("mounting_plate_counterbores".into(), counterbores);
    }
    let tip_finish = if base_only {
        None
    } else {
        let tip = add_tip_root_anchor(&root, &mut r, &selection["tip_supports"])?;
        r.extra.insert("tip_supports".into(), tip);
        let index = r.row("faucet-shell-tip")?.index;
        let contact = add_tip_dispense_contact(&mut r, &selection["tip_dispense_contact"], &mapping["parameters"])?;
        let band = ContactBand::new(&contact["band"])?;
        r.extra.insert("tip_dispense_contact".into(), contact);
        let lip = if warp_donor {
            let support = match &warp_settings {
                Some(settings) => settings.add_support(&mut r)?,
                None => add_warp_shoulder_support(&mut r)?,
            };
            r.extra.insert("warp_shoulder_support".into(), support);
            None
        } else {
            let (rim, joint) = add_tip_rim_contact(&mut r, &selection["tip_supports"], &mapping["parameters"])?;
            let joint_band = ContactBand::new(&joint["band"])?;
            r.extra.insert("tip_rim_contact".into(), joint);
            Some((rim, joint_band))
        };
        let cooling = tip_end_stretch(&r, &selection["tip_end_cooling"])?;
        Some((index, band, lip, cooling))
    };

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
        "tools/hsm/print-prep/src/profile.rs", "tools/hsm/print-prep/src/rim_contour.rs", "tools/hsm/print-prep/src/seam.rs",
        "tools/hsm/print-prep/src/stretch_cooling.rs",
        finish.as_str(), PROFILE, rim_footprint].iter().map(|p| root.join(p))
        .chain(parts.iter().map(|p| p.source.clone())) {
        sources.insert(relative(&p, &root), json!(file_sha(&p)?));
    }
    if let Some(path) = warp_settings_path {
        sources.insert(relative(&path, &root), json!(file_sha(&path)?));
    }
    if underside.is_some() {
        for source in faucet_underside::SOURCES {
            sources.insert(source.into(), json!(file_sha(&root.join(source))?));
        }
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
        ("finish_selection", json!(finish)), ("finish_selection_sha256", json!(file_sha(&root.join(&finish))?)), ("selected_finish", selection.clone()),
        ("layer_config_ranges", json!([])),
        ("layer_scope", json!("Use the shared first and ordinary layer heights across the plate.")),
        ("settings_changes", json!(changes)), ("rigid_part_count", json!(parts.len())),
        ("inverse_warp_donor", json!(warp_donor)),
        ("preparation_only", json!(true)), ("submitted", json!(false)), ("send_attempted", json!(false)),
        ("source_sha256", json!(sources)),
    ] {
        if k == "inverse_warp_donor" && !(sloped_layout || warp_donor) {
            continue;
        }
        report[k] = v;
    }
    std::fs::write(project.with_extension("print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    println!("{}", project.display());
    if let Some(directory) = slice_output {
        let mut bands = Vec::new();
        if let Some((index, band, lip, _)) = &tip_finish {
            bands.push((*index, band));
            if let Some((_, joint)) = lip {
                bands.push((*index, joint));
            }
        }
        if let Some((base, _, band)) = &base_contact {
            bands.insert(0, (*base, band));
        }
        let slicer = Path::new(slice::SLICER);
        let mut motion = match &underside {
            Some(stage) => stage.slice_bands(&root, &mut r, &bands, &project, &directory, slicer, &selection["rear_seam_enforcement"])?,
            None => ContactBand::slice_bands(&mut r.plate, &bands, &project, &directory, slicer)?,
        };
        if underside.is_some() {
            let record = motion.as_object_mut().context("contact motion report")?;
            record.remove("archive");
            record.insert("archive_scope".into(), json!("Sliced contact-stage archive before the scaffold, roof and skin are inserted."));
        }
        if let Some((_, contour, band)) = &base_contact {
            report["rim_contour"] = apply_rim_contour(&project, &directory, *contour, band)?;
        }
        report["nonplanar_motion"] = motion;
        if let Some((_, _, lip, cooling)) = &tip_finish {
            if let Some((rim, joint)) = lip {
                report["tip_rim_contour"] = apply_tip_rim_contour(&project, &directory, *rim, joint)?;
            }
            report["tip_end_cooling"] = apply_stretch_cooling(&project, &directory, "tip-end-cooling", cooling)?;
        }
        if let Some(stage) = underside {
            let native_supports = full_plate.then(|| refresh::slice_review(&root, &project, &report, &directory)).transpose()?;
            report["sloped_underside"] = stage.finish(&root, &project, &directory, &report)?;
            if let Some(mut reading) = native_supports {
                reading["native_slice_scope"] = json!("Native toolpaths before the scaffold and skin replace the fill.");
                // Keep the native envelope and source binding for each object.
                reading["parts"] = json!(reading["parts"].as_array().into_iter().flatten().map(|part|
                    json!({"piece": part["piece"], "inputs": part["inputs"], "toolpaths": part["toolpaths"]})
                ).collect::<Vec<_>>());
                reading["sloped_underside"] = report["sloped_underside"].clone();
                let stage = report["sloped_underside"].clone();
                let readiness = json!({
                    "status": "editable project and complete offline slice prepared",
                    "project": relative(&project, &root), "project_sha256": report["project_sha256"],
                    "source_stls": report["parts"].clone(),
                    "physical_base_record": report["base_underside"]["physical_reference"],
                    "offline_slice": {
                        "archive_sha256": stage["archive_sha256"],
                        "gcode_sha256": stage["gcode_sha256"],
                        "fit": stage["fit"],
                    },
                    "submitted": false,
                });
                std::fs::write(project.with_extension("support-audit.json"), serde_json::to_string_pretty(&reading)? + "\n")?;
                std::fs::write(project.with_extension("readiness.json"), serde_json::to_string_pretty(&readiness)? + "\n")?;
            }
        }
        report["preparation_only"] = json!(false);
        std::fs::write(project.with_extension("print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    }
    Ok(())
}

fn prepare_base_contact(root: &Path, r: &mut Refreshed, recipe: &Value, parameters: &Value) -> Result<(usize, RimSpec, ContactBand)> {
    let base = r.row("faucet-shell-base")?.index;
    let mut rim = rim_supports::add(r, recipe, true)?;
    let contact = &recipe["nonplanar_contact"];
    let center: [f64; 3] = serde_json::from_value(rim["seat_print_world_center_mm"].clone())?;
    let supported_angles = serde_json::from_value(recipe["rim_enforcer_angle_degrees"].clone())?;
    let contour = RimSpec {
        identify_id: r.plate.objects[base].identify_id as u64,
        center_mm: center,
        seat_fall_angle_degrees: PRINT_BASE_BUILD_ROT.to_degrees(),
        semi_axes_mm: [FOOT_WIDTH / 2.0, FOOT_DEPTH / 2.0],
        supported_angles_degrees: supported_angles,
    };
    rim["fin_layout"] = add_base_rim_fins(root, r, base, contour, recipe)?;
    let half_span = FOOT_WIDTH.max(FOOT_DEPTH) / 2.0;
    let margin = contact["scope_margin_mm"].as_f64().context("contact scope margin")?;
    let bounds = [-1.0, 1.0].map(|direction| {
        [0, 1].map(|axis| center[axis] + direction * (half_span + margin))
    });
    let mut parameters = parameters.clone();
    let mesh_error = parameters["maximum_mesh_mapping_error_mm"].as_f64().context("contact mesh tolerance")?;
    parameters["maximum_mesh_mapping_error_mm"] = json!(mesh_error / 2.);
    let spec = json!({
        "part": "faucet-shell-base",
        "parameters": parameters,
        "plane_normal": rim["seat_print_world_outward_normal"],
        "seat_plate_mm": center,
        "bounds_mm": bounds,
        "edge_blend_mm": contact["edge_blend_mm"],
        "rim_semi_axes_mm": contour.semi_axes_mm,
        "rim_inboard_blend_mm": [0.85, 2.85],
        "refine_mesh_interiors": true,
        "supported_angles_degrees": supported_angles,
    });
    let band = ContactBand::new(&spec)?;
    r.extra.insert("base_rim_supports".into(), rim);
    r.extra.insert("nonplanar_contact".into(), spec);
    Ok((base, contour, band))
}

struct WarpSupport {
    name: String,
    role: String,
    stl: PathBuf,
}

struct WarpSettings {
    course_bands_mm: Vec<[f64; 3]>,
    support_parts: Vec<WarpSupport>,
}

impl WarpSettings {
    fn read(path: &Path) -> Result<Self> {
        let recipe = read_json(path)?;
        let course_bands_mm: Vec<[f64; 3]> =
            serde_json::from_value(recipe["course_bands_mm"].clone()).context("course_bands_mm")?;
        ensure!(course_bands_mm.iter().all(|[lo, hi, pitch]|
                [lo, hi, pitch].into_iter().all(|value| value.is_finite())
                    && *lo >= 0. && lo < hi && *pitch > 0.),
            "course bands need ordered, nonnegative bounds and positive layer heights");
        ensure!(course_bands_mm.windows(2).all(|pair| pair[0][1] <= pair[1][0]),
            "course bands must be sorted and disjoint");
        let folder = path.parent().context("warp settings directory")?;
        let support_parts = recipe["support_parts"].as_array().context("support_parts")?
            .iter().map(|part| {
                let name = part["name"].as_str().context("support part name")?.to_owned();
                let role = part["role"].as_str().context("support part role")?.to_owned();
                let stl = folder.join(part["stl"].as_str().context("support part STL")?);
                ensure!(!name.trim().is_empty() && matches!(role.as_str(), "support_enforcer" | "support_blocker"),
                    "each support part needs a name and a native support subtype");
                Ok(WarpSupport { name, role, stl })
            }).collect::<Result<_>>()?;
        Ok(Self { course_bands_mm, support_parts })
    }

    fn add_support(&self, project: &mut Refreshed) -> Result<Value> {
        let row = project.row("faucet-shell-tip")?;
        let center = row.center;
        let index = row.index;
        let mut regions = Vec::new();
        for source in &self.support_parts {
            let mut mesh = hsm_print_prep::mesh::Mesh::read_stl(&source.stl)?;
            mesh.check_closed_single_body(&source.name)?;
            for point in &mut mesh.vertices {
                *point = [0, 1, 2].map(|axis| point[axis] - center[axis]);
            }
            let component = project.plate.add_part(index, &source.name, mesh.vertices, mesh.faces,
                &source.role, Vec::new(), None);
            regions.push(json!({"name": source.name, "role": source.role, "component_id": component,
                "mesh_sha256": file_sha(&source.stl)?}));
        }
        Ok(json!({"selected_support_parts": regions, "mesh_coordinates": "warp donor source CAD"}))
    }
}

/// Ask the native tree slicer for a removable annular roof below a warp donor's virtual shoulder:
/// two half-ring roofs parted by release gaps, and a keep-out around the plug they ring.
fn add_warp_shoulder_support(project: &mut Refreshed) -> Result<Value> {
    const SHOULDER_Z: f64 = 22.28;
    const HALF_DEPTH: f64 = 0.70;
    const ENFORCER_RADII: [f64; 2] = [12.05, 14.10];
    const RELEASE_HALF_ANGLE: f64 = 2.5;
    const PLUG_KEEP_RADIUS: f64 = 11.35;
    const PLUG_XY_GAP: f64 = 0.55;
    let row = project.row("faucet-shell-tip")?;
    let index = row.index;
    let object = &project.plate.objects[index];
    let matrix = object.rotation;
    let translation = object.translation;
    let inverse = [0, 1, 2].map(|axis| [0, 1, 2].map(|j| matrix[j][axis]));
    let local = |p: [f64; 3]| apply(&inverse, [0, 1, 2].map(|i| p[i] - translation[i]));
    let place = |p: [f64; 3]| {
        let q = apply(&matrix, [0, 1, 2].map(|i| p[i] - row.center[i]));
        [0, 1, 2].map(|i| q[i] + translation[i])
    };
    let mut xy_low = [f64::INFINITY; 2];
    let mut xy_high = [f64::NEG_INFINITY; 2];
    for face in &row.mesh.faces {
        let points = face.map(|i| place(row.mesh.vertices[i]));
        if points.iter().all(|p| (p[2] - SHOULDER_Z).abs() < 0.002) {
            for point in points {
                for axis in 0..2 {
                    xy_low[axis] = xy_low[axis].min(point[axis]);
                    xy_high[axis] = xy_high[axis].max(point[axis]);
                }
            }
        }
    }
    ensure!((xy_high[0] - xy_low[0] - 27.).abs() < 0.03, "expected complete virtual mating shoulder");
    let [cx, cy] = [0, 1].map(|axis| (xy_low[axis] + xy_high[axis]) / 2.);
    let axis_ratio = (xy_high[1] - xy_low[1]) / (xy_high[0] - xy_low[0]);
    let strip = |start: f64, stop: f64, radii: [f64; 2]| {
        let count = (stop - start).ceil() as usize;
        let sections: Vec<_> = (0..=count).map(|i| {
            let t = start + (stop - start) * i as f64 / count as f64;
            let (sine, cosine) = t.to_radians().sin_cos();
            let [inner, outer] = radii;
            [[inner, -HALF_DEPTH], [outer, -HALF_DEPTH], [outer, HALF_DEPTH], [inner, HALF_DEPTH]]
                .map(|[radius, dz]| local([cx + radius * cosine, cy + radius * axis_ratio * sine, SHOULDER_Z + dz]))
        }).collect();
        closed_rim_strip(&sections)
    };
    let add = |project: &mut Refreshed, name: &str, subtype: &str, mesh: hsm_print_prep::mesh::Mesh| {
        mesh.check_closed_single_body(name)?;
        Ok::<_, anyhow::Error>(project.plate.add_part(index, name, mesh.vertices, mesh.faces,
            subtype, Vec::new(), None))
    };
    let mut roofs = Vec::new();
    let mut gaps = Vec::new();
    for (number, at) in [0., 180.].into_iter().enumerate() {
        roofs.push(add(project, &format!("Virtual shoulder roof {}", number + 1), "support_enforcer",
            strip(at + RELEASE_HALF_ANGLE, at + 180. - RELEASE_HALF_ANGLE, ENFORCER_RADII))?);
        gaps.push(add(project, &format!("Virtual shoulder roof release {}", number + 1), "support_blocker",
            strip(at - RELEASE_HALF_ANGLE, at + RELEASE_HALF_ANGLE, ENFORCER_RADII))?);
    }
    let n = 96;
    let mut vertices = Vec::with_capacity(2 * n + 2);
    let radius = PLUG_KEEP_RADIUS + PLUG_XY_GAP;
    let z = [SHOULDER_Z - 1.2, SHOULDER_Z + HALF_DEPTH];
    for depth in z {
        for i in 0..n {
            let (sine, cosine) = (std::f64::consts::TAU * i as f64 / n as f64).sin_cos();
            vertices.push(local([cx + radius * cosine, cy + radius * axis_ratio * sine, depth]));
        }
    }
    vertices.extend(z.map(|depth| local([cx, cy, depth])));
    let mut faces = Vec::with_capacity(4 * n);
    for i in 0..n {
        let j = (i + 1) % n;
        faces.extend([[i, j, n + j], [i, n + j, n + i], [2*n, j, i], [2*n+1, n+i, n+j]]);
    }
    let plug = add(project, "Virtual shoulder plug keepout", "support_blocker",
        hsm_print_prep::mesh::Mesh { vertices, faces })?;
    Ok(json!({"roof_enforcers": roofs, "release_blockers": gaps, "plug_keepout": plug,
        "virtual_seat_center_mm": [cx, cy, SHOULDER_Z], "plate_axis_ratio": axis_ratio,
        "support_radial_mm": ENFORCER_RADII, "release_angle_half_degrees": RELEASE_HALF_ANGLE,
        "virtual_plug_keepout_radial_mm": radius, "virtual_plug_z_mm": z}))
}
