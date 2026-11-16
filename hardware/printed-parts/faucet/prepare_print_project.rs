//! faucet-print-project — a faucet style's complete plate, or its warped donor tip, as a PET-GF
//! project for the selected H2C's hardened left nozzle, on the bed the plate's selections name.
//! `faucet-plate` runs it for each of the plate's projects. Never contacts a printer.
//!
//!     faucet-print-project <project.3mf> [--style sculpted|industrial]
//!                          [--printer Mark1|Mark2] [--filament-colour '#RRGGBB'] [--finish SELECTION.json]
//!                          (--physical-base | --filled-base FILLED.stl
//!                           | --warp-donor --tip-mesh TIP.stl --warp-settings SETTINGS.json --slice-output DIRECTORY)
//!
//! The complete plate's five rigid parts are the style's base, the shared tip and display cover,
//! the style's above-counter plate and the side-down lever; the Sculpted style unless `--style`
//! names the other. Their object settings and the solid foot regions are the parent recipe's, by
//! part. `--physical-base` writes the editable project with the actual base. `--filled-base` gives
//! the slicer the base with the space under its mounting face filled to the bed, for the stage
//! that lays that space and the foot itself; the base keeps its mounting insert recesses clear and
//! the lever stands clear of the toolhead's reach over the foundation. The tip's first mating-lip
//! perimeter follows the inclined seat above a dense tree interface. `--warp-donor` slices the
//! warped tip `--tip-mesh` alone, in the course bands and with the support regions `--warp-settings`
//! gives in the warped mesh's coordinates, for the stage that lays its courses back onto the real
//! shoulder. `--finish` reads the selections from that file in place of the plate's.

mod base_seat;

use anyhow::{bail, ensure, Context, Result};
use hsm_faucet_numbers::shell::PRINT_BASE_BUILD_ROT;
use hsm_print_prep::faucet::{add_tip_root_anchor, apply_overhang_recipe, archive_members, enforce_rear_seam, file_sha, read_json, recorded_member};
use hsm_print_prep::faucet_contact::{add_tip_dispense_contact, add_tip_rim_contact, apply_stretch_cooling, tip_end_stretch, ContactBand};
use hsm_print_prep::faucet_plate::{self, Style, COVER, LEVER, PARENT, TIP};
use hsm_print_prep::faucet_recesses::block_plate_counterbores;
use hsm_print_prep::profile::{cooling_hook, petgf_infill_pattern, relative};
use hsm_print_prep::refresh::{self, Part, Refreshed, Region};
use hsm_print_prep::{root, sha256_hex, slice, xml};
use serde_json::{json, Map, Value};
use std::io::Cursor;
use std::path::{Path, PathBuf};

const PROFILE: &str = "hardware/printed-parts/faucet/industrial/prints/2026-10-15-all-learnings/mark2/2026-10-15-complete-faucet-all-learnings-mark2-base-arcs-z004.3mf";
/// Each part's own space from the shared plate's centre, for its brim and supports: the lever
/// beyond the above-counter plate, where the toolhead over it stays off the base's foundation.
const OFFSETS: [[f64; 2]; 5] = [[-77.0, 0.0], [24.0, 47.0], [89.0, 76.0], [43.0, -52.0], [94.0, -58.0]];

fn main() -> Result<()> {
    let root = root();
    let mut args = std::env::args_os().skip(1);
    let project = PathBuf::from(args.next().context("expected a .3mf output path")?);
    let mut style: &Style = &faucet_plate::STYLES[0];
    let (mut slice_output, mut filled_base, mut tip_mesh, mut warp_settings_path) = (None, None, None, None);
    let (mut physical_base, mut warp_donor) = (false, false);
    let mut finish = None;
    let mut printer = "Mark2".to_owned();
    let mut colour = "#FFFFFF".to_owned();
    while let Some(arg) = args.next() {
        if arg == "--physical-base" {
            physical_base = true;
            continue;
        }
        if arg == "--warp-donor" {
            warp_donor = true;
            continue;
        }
        let value = args.next().with_context(|| format!("{} needs a value", arg.to_string_lossy()))?;
        match arg.to_str() {
            Some("--slice-output") => slice_output = Some(PathBuf::from(value)),
            Some("--filled-base") => filled_base = Some(PathBuf::from(value)),
            Some("--tip-mesh") => tip_mesh = Some(PathBuf::from(value)),
            Some("--warp-settings") => warp_settings_path = Some(PathBuf::from(value)),
            Some("--finish") => finish = Some(PathBuf::from(value)),
            Some("--style") => style = faucet_plate::style(value.to_str().context("style name")?)?,
            Some("--printer") => printer = value.into_string().ok().context("printer name")?,
            Some("--filament-colour") => colour = value.into_string().ok().context("filament colour")?,
            _ => bail!("unknown argument {}", arg.to_string_lossy()),
        }
    }
    ensure!([physical_base, filled_base.is_some(), warp_donor].iter().filter(|&&on| on).count() == 1,
        "prepare the editable plate, the slicer's plate or the warp donor");
    ensure!(warp_donor == (tip_mesh.is_some() && warp_settings_path.is_some() && slice_output.is_some())
        && (warp_donor || (tip_mesh.is_none() && warp_settings_path.is_none() && slice_output.is_none())),
        "the warp donor takes its warped tip, its warp settings and a slice directory");
    let warp_settings = warp_settings_path.as_deref().map(WarpSettings::read).transpose()?;
    let named = style.title;
    let title = if warp_donor {
        format!("{named} faucet tip inverse warp donor PET-GF left {printer}")
    } else {
        format!("Complete {named} faucet sloped underside PET-GF left {printer}")
    };
    let (finish, selection) = match finish {
        Some(path) => (relative(&root.join(&path), &root), read_json(&root.join(&path))?),
        None => (faucet_plate::SELECTION.to_owned(), faucet_plate::selection(&root)?),
    };
    let selection = style.finish(&selection);
    // the plate the selections put the faucet on, and the PET-GF Z trim the print setup gives the
    // printer for that plate
    let bed = selection["bed_type"].as_str().context("the plate's selections name no bed_type")?.to_owned();
    let trim = hsm_print_prep::profile::petgf_bed_z_trim(&root, &printer, &bed)?;
    let tip_part = Part::new(TIP.name, tip_mesh.unwrap_or_else(|| root.join(TIP.stl)), faucet_plate::TIP_ROTATION_DEGREES);
    let parts = if warp_donor {
        vec![tip_part]
    } else {
        vec![
            Part::new(style.base.name, filled_base.unwrap_or_else(|| root.join(style.base.stl)), -PRINT_BASE_BUILD_ROT.to_degrees()),
            tip_part,
            Part::new(COVER.name, root.join(COVER.stl), faucet_plate::COVER_ROTATION_DEGREES),
            Part::new(style.plate.name, root.join(style.plate.stl), 0.0),
            Part::new(LEVER.name, root.join(LEVER.stl), 0.0),
        ]
    };
    let offsets = if warp_donor { &[[0.0, 0.0]][..] } else { &OFFSETS[..] };
    let mut r = refresh::refresh(&root, &root.join(PROFILE), &parts, offsets, &title, Some(trim), 40.0)?;
    let parent = &selection["industrial_recipe"];
    let parent_project_source = parent["project"].as_str().context("Industrial parent project")?;
    let parent_report_source = parent["report"].as_str().context("Industrial parent report")?;
    let parent_revision = parent["source_commit"].as_str().context("Industrial parent revision")?;
    let parent_project_bytes = recorded_member(&root, parent, "project")?;
    let parent_report_bytes = recorded_member(&root, parent, "report")?;
    if !warp_donor {
        let parent_report: Value = serde_json::from_slice(&parent_report_bytes)?;
        let regions: Vec<Region> = parent_report["local_solid_regions"].as_array().into_iter().flatten().map(|row| {
            let b = &row["source_bounds_mm"];
            let mut declared = row.as_object().cloned().unwrap_or_default();
            declared.insert("part".into(), json!(style.base.name));
            declared.insert("clip_to_part_bounds".into(), json!(false));
            Ok(Region { part: style.base.name.into(), name: row["name"].as_str().context("region name")?.to_string(),
                        low: [0, 1, 2].map(|k| b[0][k].as_f64().unwrap_or(f64::NAN)), high: [0, 1, 2].map(|k| b[1][k].as_f64().unwrap_or(f64::NAN)),
                        clip_to_part_bounds: false, declared: Value::Object(declared) })
        }).collect::<Result<_>>()?;
        r.add_local_solid_regions(&regions)?;
    }
    let parent = archive_members(Cursor::new(&parent_project_bytes))?;
    let parent_config = xml::parse(std::str::from_utf8(&parent["Metadata/model_settings.config"])?)?;
    let shell_gap = selection["shell_ordinary_seam_gap"].as_str().context("shell seam gap")?;
    for obj in r.plate.objects.iter_mut() {
        let industrial = style.parts().iter().zip(PARENT).find(|(part, _)| part.name == obj.name).map(|(_, parent)| parent)
            .context("a part without its Industrial counterpart")?;
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
        if obj.name == style.base.name || obj.name == TIP.name {
            obj.settings.retain(|(key, _)| key != "seam_gap");
            obj.settings.push(("seam_gap".into(), shell_gap.into()));
        }
        if warp_donor && obj.name == TIP.name {
            obj.settings.retain(|(key, _)| key != "seam_slope_type");
            obj.settings.push(("seam_slope_type".into(), "none".into()));
        }
    }
    let original = r.plate.settings.clone();
    r.plate.settings["curr_bed_type"] = json!(bed);
    if let Some(settings) = &warp_settings {
        let index = r.row(TIP.name)?.index;
        r.plate.objects[index].ranges = settings.course_bands_mm.iter().copied().map(|[min_z, max_z, height]|
            hsm_print_prep::project::Range {
                min_z, max_z, options: vec![("layer_height".into(), height.to_string())],
            }).collect();
        r.extra.insert("tip_virtual_course_bands_mm".into(), json!(settings.course_bands_mm));
        if let Some(independent) = settings.independent_support_layer_height {
            r.plate.settings["independent_support_layer_height"] = json!(if independent { "1" } else { "0" });
        }
        if let Some(gap) = settings.support_top_gap_mm {
            r.plate.settings["support_top_z_distance"] = json!(gap.to_string());
        }
    }
    let hook = cooling_hook(&root);
    apply_overhang_recipe(&mut r.plate.settings, &selection["overhang_recipe"], &hook)?;
    if let Some(entry) = selection.get("shallow_overhang_wall_speed") {
        // The named parts lay walls at their own speed through these overhang points; the filament's
        // overhang speeds leave the process's, which hold the same values, to every object.
        let names = |key: &str| -> Result<Vec<String>> {
            entry[key].as_array().with_context(|| format!("the shallow overhang entry's {key}"))?.iter()
                .map(|v| v.as_str().map(String::from).with_context(|| format!("a name in {key}"))).collect()
        };
        let (parts, points) = (names("parts")?, names("points")?);
        for point in &points {
            let Some(Value::Array(variants)) = r.plate.settings.get(point) else { bail!("the process has no {point}") };
            let zeros = vec!["0"; variants.len()].join(",");
            for obj in r.plate.objects.iter_mut().filter(|o| parts.contains(&o.name)) {
                obj.settings.push((point.clone(), zeros.clone()));
            }
        }
        if let Some(Value::Array(flags)) = r.plate.settings.get("override_process_overhang_speed") {
            let off = json!(vec!["0"; flags.len()]);
            r.plate.settings["override_process_overhang_speed"] = off;
        }
    }
    r.plate.settings["sparse_infill_pattern"] = json!(petgf_infill_pattern(&root)?);
    r.plate.settings["filament_map"] = json!(["1"]);
    r.plate.settings["filament_nozzle_map"] = json!(["0"]);
    r.plate.settings["filament_map_mode"] = json!("Manual");
    r.plate.settings["filament_colour"] = json!([colour]);
    if r.plate.settings.get("filament_multi_colour").is_some() {
        r.plate.settings["filament_multi_colour"] = json!([colour]);
    }
    r.plate.filament_map_mode = "Manual".into();
    let seam_keys = if warp_donor {
        &["tip_rear_seam_enforcement"][..]
    } else {
        &["rear_seam_enforcement", "tip_rear_seam_enforcement", "cover_rear_seam_enforcement"][..]
    };
    for &key in seam_keys {
        let record = enforce_rear_seam(&mut r, &selection[key])?;
        r.extra.insert(key.into(), record);
    }
    if !warp_donor {
        // The fill stands where the rim's supports would: only the insert recesses' blockers and
        // the base's support settings apply.
        let seat = base_seat::add(&mut r, style.base.name, &selection["base_supports"])?;
        r.extra.insert("base_seat".into(), seat);
        let pocket_recipe = &selection["mounting_plate_counterbores"];
        let radial_clearance = pocket_recipe["blocker_radial_clearance_mm"].as_f64().context("counterbore blocker clearance")?;
        let depth_allowance = serde_json::from_value(pocket_recipe["blocker_depth_allowance_mm"].clone())?;
        let counterbores = block_plate_counterbores(&mut r, style.plate.name, radial_clearance, depth_allowance)?;
        r.extra.insert("mounting_plate_counterbores".into(), counterbores);
    }
    let tip = add_tip_root_anchor(&root, &mut r, &selection["tip_supports"])?;
    r.extra.insert("tip_supports".into(), tip);
    let contact = add_tip_dispense_contact(&mut r, &selection["tip_dispense_contact"])?;
    r.extra.insert("tip_dispense_contact".into(), contact);
    if let Some(settings) = &warp_settings {
        let support = settings.add_support(&mut r)?;
        r.extra.insert("warp_shoulder_support".into(), support);
    } else {
        let joint = add_tip_rim_contact(&mut r, &selection["tip_supports"])?;
        r.extra.insert("tip_rim_contact".into(), joint);
    }
    let cooling = tip_end_stretch(&r, &selection["tip_end_cooling"])?;

    let mut changes = r.profile.changes.clone();
    for (key, value) in r.plate.settings.as_object().into_iter().flatten() {
        if original.get(key) != Some(value) {
            changes.insert(key.clone(), json!({"from": original.get(key), "to": value}));
        }
    }
    let mut sources = Map::new();
    sources.insert(format!("{parent_revision}:{parent_project_source}"), json!(sha256_hex(&parent_project_bytes)));
    sources.insert(format!("{parent_revision}:{parent_report_source}"), json!(sha256_hex(&parent_report_bytes)));
    for p in ["hardware/printed-parts/faucet/prepare_print_project.rs", "hardware/printed-parts/faucet/base_seat.rs",
        "tools/hsm/print-prep/src/faucet.rs", "tools/hsm/print-prep/src/faucet_contact.rs", "tools/hsm/print-prep/src/faucet_recesses.rs",
        "tools/hsm/print-prep/src/profile.rs", "tools/hsm/print-prep/src/seam.rs",
        "tools/hsm/print-prep/src/stretch_cooling.rs",
        finish.as_str(), PROFILE].iter().map(|p| root.join(p))
        .chain(parts.iter().map(|p| p.source.clone())) {
        sources.insert(relative(&p, &root), json!(file_sha(&p)?));
    }
    if let Some(path) = warp_settings_path {
        sources.insert(relative(&path, &root), json!(file_sha(&path)?));
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
        ("finish_selection", json!(finish)), ("finish_selection_sha256", json!(file_sha(&root.join(&finish))?)),
        ("layer_config_ranges", json!([])),
        ("layer_scope", json!("Use the shared first and ordinary layer heights across the plate.")),
        ("settings_changes", json!(changes)), ("rigid_part_count", json!(parts.len())),
        ("inverse_warp_donor", json!(warp_donor)),
        ("preparation_only", json!(true)), ("submitted", json!(false)), ("send_attempted", json!(false)),
        ("source_sha256", json!(sources)),
    ] {
        report[k] = v;
    }
    std::fs::write(project.with_extension("print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    println!("{}", project.display());
    if let Some(directory) = slice_output {
        // the donor's slice: the contact-band slice path with no band on it
        report["nonplanar_motion"] = ContactBand::slice_bands(&mut r.plate, &[], &project, &directory, Path::new(slice::SLICER))?;
        report["tip_end_cooling"] = apply_stretch_cooling(&project, &directory, "tip-end-cooling", &cooling)?;
        report["preparation_only"] = json!(false);
        std::fs::write(project.with_extension("print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    }
    Ok(())
}

struct WarpSupport {
    name: String,
    role: String,
    stl: PathBuf,
}

struct WarpSettings {
    course_bands_mm: Vec<[f64; 3]>,
    support_parts: Vec<WarpSupport>,
    independent_support_layer_height: Option<bool>,
    support_top_gap_mm: Option<f64>,
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
        let independent_support_layer_height = recipe.get("independent_support_layer_height").map(|value|
            value.as_bool().context("independent_support_layer_height must be a boolean")).transpose()?;
        let support_top_gap_mm = recipe.get("support_top_gap_mm").map(|value|
            value.as_f64().filter(|gap| *gap >= 0. && gap.is_finite()).context("support_top_gap_mm must be nonnegative")).transpose()?;
        Ok(Self { course_bands_mm, support_parts, independent_support_layer_height, support_top_gap_mm })
    }

    fn add_support(&self, project: &mut Refreshed) -> Result<Value> {
        let row = project.row(TIP.name)?;
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
