//! A plate of whole parts in a saved project's complete settings, each turned about X onto the
//! bed and set at its offset from the centre of the plate its nozzles reach: the faucet's
//! projects and the bench parts that share their writer. A slice of one reads back per part —
//! its toolpaths' envelope, the parts' clearances, and each part's support topology.

use crate::json::{python_number, Json};
use crate::mesh::{bounds, Mesh};
use crate::profile::{self, relative, Profile};
use crate::project::{MeshStyle, Plate};
use crate::{apply, audit, cooling, gcode, rotation_x, sha256_hex};
use anyhow::{bail, Context, Result};
use serde_json::{json, Map, Value};
use std::path::{Path, PathBuf};

/// One part: its name, its STL, and the turn about X, in degrees, that lays it on the bed.
#[derive(Clone)]
pub struct Part {
    pub name: String,
    pub source: PathBuf,
    pub angle: f64,
}

impl Part {
    pub fn new(name: &str, source: PathBuf, angle: f64) -> Part {
        Part { name: name.to_string(), source, angle }
    }
}

/// A part as the project holds it.
pub struct Row {
    pub name: String,
    /// Its object's index in the plate.
    pub index: usize,
    pub source: PathBuf,
    pub mesh: Mesh,
    pub center: [f64; 3],
    pub angle: f64,
    pub translation: [f64; 3],
    pub low: [f64; 3],
    pub high: [f64; 3],
    pub stl_sha256: String,
}

pub struct Refreshed {
    pub plate: Plate,
    pub profile: Profile,
    pub rows: Vec<Row>,
    pub settings_from: PathBuf,
    pub plate_border: f64,
    /// Report fields beyond the plate's own, in the order they are added.
    pub extra: Map<String, Value>,
}

fn number(settings: &Json, key: &str) -> Result<f64> {
    Ok(settings.first_text(key).with_context(|| format!("the profile has no {key}"))?.trim_end_matches('%').parse()?)
}

/// Lay `parts` on one plate in `settings_from`'s settings (`z_trim` replacing its plate
/// compensation), the cooling stage applied. A part must clear `plate_border` inside the plate.
pub fn refresh(root: &Path, settings_from: &Path, parts: &[Part], offsets: &[[f64; 2]], title: &str,
               z_trim: Option<f64>, plate_border: f64) -> Result<Refreshed> {
    if parts.len() != offsets.len() {
        bail!("each print-project part needs one bed-position offset");
    }
    let settings_from = settings_from.canonicalize().with_context(|| format!("{}", settings_from.display()))?;
    let profile = profile::load(&settings_from, z_trim, None, root)?;
    let mut plate = Plate::new(title, &profile, "homesodamachine/faucet/");
    plate.filament_maps = Some("1".into());
    plate.build_name = Some("build".into());
    plate.mesh_style = MeshStyle::Element;
    let (low, high) = (profile.usable_low, profile.usable_high);
    let height = number(&profile.settings, "printable_height")?;
    let mut rows = Vec::new();
    for (part, offset) in parts.iter().zip(offsets) {
        let payload = std::fs::read(&part.source).with_context(|| format!("reading {}", part.source.display()))?;
        let mesh = Mesh::read_stl(&part.source)?;
        mesh.check_closed_single_body(&part.source.file_name().unwrap().to_string_lossy())?;
        let center = mesh.center();
        let local: Vec<[f64; 3]> = mesh.vertices.iter().map(|v| [v[0] - center[0], v[1] - center[1], v[2] - center[2]]).collect();
        let rotation = rotation_x(part.angle);
        let rotated: Vec<[f64; 3]> = local.iter().map(|v| apply(&rotation, *v)).collect();
        let (rlow, rhigh) = bounds(&rotated);
        let plate_center = [(low[0] + high[0]) / 2.0 + offset[0], (low[1] + high[1]) / 2.0 + offset[1]];
        let translation = [plate_center[0] - (rlow[0] + rhigh[0]) / 2.0, plate_center[1] - (rlow[1] + rhigh[1]) / 2.0, -rlow[2]];
        let placed: Vec<[f64; 3]> = rotated.iter().map(|v| [v[0] + translation[0], v[1] + translation[1], v[2] + translation[2]]).collect();
        let (plow, phigh) = bounds(&placed);
        if plow[0] < low[0] + plate_border || plow[1] < low[1] + plate_border || phigh[0] > high[0] - plate_border || phigh[1] > high[1] - plate_border {
            bail!("{} extends into the {} mm plate border", part.name, python_number(plate_border).trim_end_matches(".0"));
        }
        if phigh[2] > height {
            bail!("{} exceeds the printer height", part.name);
        }
        let index = plate.add_object(&part.name, local, mesh.faces.clone(), &part.source.file_name().unwrap().to_string_lossy(),
                                     center, rotation, translation, None, Vec::new());
        rows.push(Row { name: part.name.clone(), index, source: part.source.clone(), mesh, center, angle: part.angle, translation,
                        low: plow, high: phigh, stl_sha256: sha256_hex(&payload) });
    }
    Ok(Refreshed { plate, profile, rows, settings_from, plate_border, extra: Map::new() })
}

/// A solid-infill region: a box in the part's source frame, the part's own stock clipped to it.
pub struct Region {
    pub part: String,
    pub name: String,
    pub low: [f64; 3],
    pub high: [f64; 3],
    /// Clip the box to the part's mesh bounds; otherwise deposition alone clips it.
    pub clip_to_part_bounds: bool,
    /// The region as declared, carried into the record.
    pub declared: Value,
}

impl Refreshed {
    pub fn row(&self, name: &str) -> Result<&Row> {
        self.rows.iter().find(|r| r.name == name).with_context(|| format!("no part {name} on the plate"))
    }

    /// Solid-infill regions as modifier parts of their parts' objects.
    pub fn add_local_solid_regions(&mut self, regions: &[Region]) -> Result<()> {
        let mut records = Vec::new();
        for region in regions {
            let row = self.rows.iter().find(|r| r.name == region.part).with_context(|| format!("no part {}", region.part))?;
            let (low, high) = if region.clip_to_part_bounds {
                let (mlo, mhi) = row.mesh.bounds();
                ([0, 1, 2].map(|k| region.low[k].max(mlo[k] + 0.001)), [0, 1, 2].map(|k| region.high[k].min(mhi[k] - 0.001)))
            } else {
                (region.low, region.high)
            };
            if region.low.iter().chain(&region.high).any(|v| !v.is_finite()) || (0..3).any(|k| high[k] <= low[k]) {
                bail!("invalid solid modifier bounds: {}", region.name);
            }
            let c = row.center;
            let local = |p: [f64; 3]| [p[0] - c[0], p[1] - c[1], p[2] - c[2]];
            let (v, f) = box_mesh(local(low), local(high));
            let index = row.index;
            let id = self.plate.add_part(index, &region.name, v, f, "modifier_part",
                vec![("sparse_infill_density".into(), "100%".into()), ("sparse_infill_pattern".into(), "zig-zag".into())], None);
            let mut record = region.declared.as_object().cloned().unwrap_or_default();
            record.insert("applied_source_bounds_mm".into(), json!([low, high]));
            record.insert("modifier_part_id".into(), json!(id.to_string()));
            record.insert("wall_loops".into(), Value::Null);
            record.insert("sparse_infill_percent".into(), json!(100));
            record.insert("sparse_infill_pattern".into(), json!("zig-zag"));
            records.push(Value::Object(record));
        }
        self.extra.insert("local_solid_regions".into(), json!(records));
        Ok(())
    }

    /// The project and its `.print.json` report, written; returns the report.
    pub fn write(&self, root: &Path, output: &Path) -> Result<Value> {
        self.plate.write(output)?;
        let settings = &self.plate.settings;
        let get = |key: &str| settings.first_text(key).with_context(|| format!("the profile has no {key}"));
        let floats = |key: &str| -> Value {
            json!(settings.get(key).map(Json::list).unwrap_or(&[]).iter().filter_map(Json::text).filter_map(|s| s.parse::<f64>().ok()).collect::<Vec<_>>())
        };
        let payload = settings.dumps() + "\n";
        let mut parts = Vec::new();
        for row in &self.rows {
            let obj = &self.plate.objects[row.index];
            let error = row.mesh.vertices.iter().map(|v| {
                (0..3).map(|k| (format!("{:.9}", v[k] - row.center[k]).parse::<f64>().unwrap() + row.center[k] - v[k]).abs()).fold(0.0, f64::max)
            }).fold(0.0, f64::max);
            parts.push(json!({
                "name": row.name, "plate": 1, "object_id": obj.object_id.to_string(), "part_id": obj.part_id.to_string(),
                "member": obj.member, "identify_id": obj.identify_id, "source": relative(&row.source, root),
                "stl_sha256": row.stl_sha256, "triangles": row.mesh.faces.len(), "rotation_x_degrees": row.angle,
                "source_center_mm": row.center, "build_transform": obj.transform_values(),
                "plate_translation_mm": row.translation, "plate_origin_mm": [0.0, 0.0, 0.0],
                "plate_bounds_mm": [row.low, row.high], "watertight": true, "body_count": 1,
                "embedded_vertex_error_mm": error,
            }));
        }
        let line_widths: Map<String, Value> = ["outer_wall_line_width", "inner_wall_line_width", "sparse_infill_line_width",
            "internal_solid_infill_line_width", "top_surface_line_width", "support_line_width"]
            .iter().map(|k| Ok((k.to_string(), json!(number(settings, k)?)))).collect::<Result<_>>()?;
        let mut report = json!({
            "project": output.file_name().unwrap().to_string_lossy(),
            "settings_source": relative(&self.settings_from, root),
            "settings_source_sha256": sha256_hex(&std::fs::read(&self.settings_from)?),
            "settings_sha256": sha256_hex(payload.as_bytes()),
            "source_settings_sha256": sha256_hex(&self.profile.original_payload),
            "settings_changes": self.profile.changes,
            "printer": get("printer_settings_id")?, "process": get("print_settings_id")?,
            "filament": settings.get("filament_settings_id").map(Json::to_value).unwrap_or(Value::Null),
            "layer_height_mm": number(settings, "layer_height")?,
            "nozzle_diameter_mm": floats("nozzle_diameter"),
            "line_widths_mm": line_widths,
            "wall_loops": number(settings, "wall_loops")? as i64,
            "sparse_infill_percent": number(settings, "sparse_infill_density")?,
            "sparse_infill_pattern": get("sparse_infill_pattern")?,
            "saved_profile_filament_density_g_cm3": floats("filament_density"),
            "bed_type": get("curr_bed_type")?,
            "shared_printable_area_mm": [self.profile.usable_low, self.profile.usable_high],
            "printable_area_extruders": self.profile.printable_area_extruders,
            "plate_border_mm": self.plate_border, "plate_count": 1, "parts": parts,
            "project_sha256": sha256_hex(&std::fs::read(output)?),
            "settings_preserved_byte_for_byte": payload.as_bytes() == self.profile.original_payload.as_slice(),
        });
        for (k, v) in &self.extra {
            report[k] = v.clone();
        }
        std::fs::write(output.with_extension("print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
        Ok(report)
    }
}

pub fn box_mesh(low: [f64; 3], high: [f64; 3]) -> (Vec<[f64; 3]>, Vec<[usize; 3]>) {
    let ([x0, y0, z0], [x1, y1, z1]) = (low, high);
    (vec![[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]],
     vec![[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
}

/// The envelope of one object's extruded toolpaths, or of every object's when `identify` is
/// none, widened by the bead and the arc sampling's sagitta.
pub fn object_toolpaths(gcode: &[u8], identify: Option<i64>) -> Result<Value> {
    let (mut current, mut x, mut y, mut e) = (None::<i64>, 0.0, 0.0, 0.0);
    let (mut absolute, mut relative_e, mut layer_seen, mut selected_seen, mut width) = (true, true, false, false, 0.0f64);
    let (mut lo, mut hi) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
    let selected = |c: Option<i64>| identify.is_none() || c == identify;
    for raw in gcode.split(|b| *b == b'\n') {
        let text = String::from_utf8_lossy(raw);
        let line = text.trim();
        if let Some(v) = line.strip_prefix("; OBJECT_ID:") {
            current = v.trim().parse().ok();
            selected_seen |= selected(current);
        } else if let Some(v) = line.strip_prefix("; start printing object, unique label id: ") {
            current = v.trim().parse().ok();
            selected_seen |= selected(current);
        } else if line.starts_with("; stop printing object") {
            current = None;
        }
        if line.starts_with("; Z_HEIGHT:") {
            layer_seen = true;
        }
        if let Some(v) = line.strip_prefix("; LINE_WIDTH:") {
            if selected(current) {
                width = width.max(v.trim().parse().unwrap_or(0.0));
            }
        }
        let code = line.split(';').next().unwrap_or("").trim();
        let Some(command) = code.split_whitespace().next() else { continue };
        let words = gcode::words(code);
        let get = |k: u8| words.iter().find(|(c, _)| *c == k).map(|(_, v)| *v);
        match command {
            "G90" | "G91" => absolute = command == "G90",
            "M82" | "M83" => relative_e = command == "M83",
            "G92" => {
                x = get(b'X').unwrap_or(x);
                y = get(b'Y').unwrap_or(y);
                e = get(b'E').unwrap_or(e);
            }
            "G0" | "G1" | "G2" | "G3" => {
                let nx = if absolute { get(b'X').unwrap_or(x) } else { x + get(b'X').unwrap_or(0.0) };
                let ny = if absolute { get(b'Y').unwrap_or(y) } else { y + get(b'Y').unwrap_or(0.0) };
                let de = if relative_e { get(b'E').unwrap_or(0.0) } else { get(b'E').unwrap_or(e) - e };
                if selected(current) && layer_seen && de > 1e-9 && (nx != x || ny != y) {
                    let mut points = vec![(x, y)];
                    if command == "G0" || command == "G1" {
                        points.push((nx, ny));
                    } else {
                        points.extend(audit::arc_points((x, y), (nx, ny), &words, command == "G2"));
                    }
                    for (px, py) in points {
                        lo = [lo[0].min(px), lo[1].min(py)];
                        hi = [hi[0].max(px), hi[1].max(py)];
                    }
                }
                x = nx;
                y = ny;
                if let Some(v) = get(b'E') {
                    e = if relative_e { e + v } else { v };
                }
            }
            _ => {}
        }
    }
    if !selected_seen || !lo[0].is_finite() {
        bail!("no extrusion toolpaths for object label {identify:?}");
    }
    // The arc reader samples finely; the allowance covers its sagitta and the bead's half width.
    let padding = width.max(0.6) / 2.0 + 0.1;
    Ok(json!({"extrusion_bounds_xy_mm": [[lo[0] - padding, lo[1] - padding], [hi[0] + padding, hi[1] + padding]],
              "maximum_line_width_mm": width, "bounds_padding_mm": padding}))
}

/// Read each part's toolpaths and support topology in its own placement, the parts' clearances
/// and the complete plate's bead envelope; written beside the project as `.support-audit.json`.
pub fn slice_review(root: &Path, project: &Path, report: &Value, directory: &Path) -> Result<Value> {
    crate::slice::apply_directory(directory, project)?;
    if Some(sha256_hex(&std::fs::read(project)?).as_str()) != report["project_sha256"].as_str() {
        bail!("the project changed after it was written");
    }
    let sliced: Value = serde_json::from_slice(&std::fs::read(directory.join("result.json"))?)?;
    if sliced["return_code"].as_i64() != Some(0) {
        bail!("Bambu slice failed: {}", sliced["error_string"]);
    }
    let name = relative(project, root);
    let mut result = json!({
        "project": name, "project_sha256": report["project_sha256"], "settings_sha256": report["settings_sha256"],
        "slicer": Value::Null, "layer_height_mm": sliced["layer_height"], "wall_loops": sliced["wall_loops"],
        "sparse_infill_density_percent": sliced["sparse_infill_density"],
        "saved_profile_filament_density_g_cm3": report["saved_profile_filament_density_g_cm3"],
        "mass_estimate_note": "Slicer grams use the saved profile density, not a measured PET-GF part mass.",
        "plates": [], "parts": [],
    });
    for plate in sliced["sliced_plates"].as_array().into_iter().flatten() {
        let grams: f64 = plate["filaments"].as_array().into_iter().flatten().filter_map(|f| f["total_used_g"].as_f64()).sum();
        result["plates"].as_array_mut().unwrap().push(json!({"plate": plate["id"], "estimated_total_seconds": plate["total_predication"],
            "saved_profile_filament_estimate_g": grams, "slicer_warning": plate["warning_message"]}));
    }
    let project_sha = sha256_hex(&std::fs::read(project)?);
    let mut readings: Vec<Value> = Vec::new();
    for part in report["parts"].as_array().into_iter().flatten() {
        let source = root.join(part["source"].as_str().unwrap_or(""));
        if Some(sha256_hex(&std::fs::read(&source)?).as_str()) != part["stl_sha256"].as_str() {
            bail!("{} source changed after the project was written", part["name"]);
        }
        let plate_gcode = directory.join(format!("plate_{}.gcode", part["plate"]));
        let bytes = std::fs::read(&plate_gcode).with_context(|| format!("missing slice: {}", plate_gcode.display()))?;
        let identify = part["identify_id"].as_i64();
        let toolpaths = object_toolpaths(&bytes, identify)?;
        let build: Vec<f64> = part["build_transform"].as_array().into_iter().flatten().filter_map(Value::as_f64).collect();
        let translation: Vec<f64> = part["plate_translation_mm"].as_array().into_iter().flatten().filter_map(Value::as_f64).collect();
        let mut transform = [0.0; 12];
        transform[..9].copy_from_slice(&build[..9]);
        transform[9..].copy_from_slice(&translation[..3]);
        let mut cad = audit::inverse(&transform).context("a part's build transform is singular")?;
        let centre: Vec<f64> = part["source_center_mm"].as_array().into_iter().flatten().filter_map(Value::as_f64).collect();
        for k in 0..3 {
            cad[9 + k] += centre[k];
        }
        let options = audit::Options {
            piece: part["name"].as_str().unwrap_or("").to_string(), object: identify, include_unlabelled: true,
            cad_transform: Some(cad), bed_reseat: None,
            inputs: json!({"gcode": format!("plate_{}.gcode", part["plate"]), "gcode_sha256": sha256_hex(&bytes),
                           "model": relative(&source, root), "model_sha256": part["stl_sha256"],
                           "profile": name, "profile_sha256": project_sha,
                           "plate_gcode_sha256": sha256_hex(&bytes), "object_label": identify,
                           "feature_filter": "Other objects' feature labels are masked; coordinates and extrusion commands are retained."}),
        };
        let mut reading = audit::audit(&bytes, &options);
        if result["slicer"].is_null() {
            result["slicer"] = reading["slicer"].clone();
        } else if reading["slicer"] != result["slicer"] {
            bail!("plate G-code files come from different slicer versions");
        }
        reading["plate"] = part["plate"].clone();
        reading["rotation_x_degrees"] = part["rotation_x_degrees"].clone();
        reading["toolpaths"] = toolpaths;
        println!("  {}: {}", part["name"].as_str().unwrap_or(""), reading["summary"]);
        readings.push(reading);
    }
    let area: Vec<Vec<f64>> = serde_json::from_value(report["shared_printable_area_mm"].clone())?;
    let bounds_of = |v: &Value| -> ([f64; 2], [f64; 2]) {
        let b = &v["extrusion_bounds_xy_mm"];
        ([b[0][0].as_f64().unwrap_or(0.0), b[0][1].as_f64().unwrap_or(0.0)], [b[1][0].as_f64().unwrap_or(0.0), b[1][1].as_f64().unwrap_or(0.0)])
    };
    let margin = |lo: [f64; 2], hi: [f64; 2]| (lo[0] - area[0][0]).min(lo[1] - area[0][1]).min(area[1][0] - hi[0]).min(area[1][1] - hi[1]);
    let (mut margins, mut gaps) = (Vec::new(), Vec::new());
    for (i, reading) in readings.iter().enumerate() {
        let (lo, hi) = bounds_of(&reading["toolpaths"]);
        margins.push(margin(lo, hi));
        for other in &readings[..i] {
            let (olo, ohi) = bounds_of(&other["toolpaths"]);
            let d = [0.0f64.max((lo[0] - ohi[0]).max(olo[0] - hi[0])), 0.0f64.max((lo[1] - ohi[1]).max(olo[1] - hi[1]))];
            gaps.push(json!({"parts": [other["piece"], reading["piece"]], "separation_mm": d[0].hypot(d[1])}));
        }
    }
    let all = object_toolpaths(&std::fs::read(directory.join("plate_1.gcode"))?, None)?;
    let (alo, ahi) = bounds_of(&all);
    let all_margin = margin(alo, ahi);
    let border = report["plate_border_mm"].as_f64().unwrap_or(20.0);
    if all_margin < border {
        bail!("complete model/support/brim toolpaths enter the {} mm plate border", python_number(border).trim_end_matches(".0"));
    }
    result["parts"] = json!(readings);
    result["fit"] = json!({
        "minimum_shared_bed_margin_mm": margins.iter().copied().fold(f64::INFINITY, f64::min),
        "complete_layer_bead_bounds": all, "complete_layer_bead_minimum_bed_margin_mm": all_margin,
        "minimum_toolpath_separation_mm": gaps.iter().filter_map(|g| g["separation_mm"].as_f64()).fold(None, |m: Option<f64>, v| Some(m.map_or(v, |m| m.min(v)))),
        "pairwise_toolpath_separations": gaps,
    });
    std::fs::write(project.with_extension("support-audit.json"), serde_json::to_string_pretty(&result)? + "\n")?;
    Ok(result)
}

/// Slice `project` with the installed Bambu Studio command line into `directory`, then read it
/// back.
pub fn slice_and_review(root: &Path, project: &Path, report: &Value, directory: &Path, slicer: &Path) -> Result<Value> {
    if directory.exists() && std::fs::read_dir(directory)?.next().is_some() {
        bail!("the slice directory must be empty so the reading cannot take an earlier slice");
    }
    std::fs::create_dir_all(directory)?;
    let directory = directory.canonicalize()?;
    let stem = project.file_stem().and_then(|s| s.to_str()).unwrap_or("project");
    // The command line slices a copy without the hook; the cooling stage then runs on its output.
    let cli = crate::slice::cli_project(&project.canonicalize()?, &directory)?;
    let log = std::fs::File::create(directory.join("bambu-cli.log"))?;
    let status = std::process::Command::new(slicer).args(["--slice", "0", "--arrange", "0", "--orient", "0", "--outputdir"])
        .arg(&directory).arg("--export-3mf").arg(format!("{stem}.gcode.3mf")).arg(&cli).current_dir(&directory)
        .stdout(log.try_clone()?).stderr(log).status()?;
    println!("Offline slice exited {}; {}", status.code().unwrap_or(-1), directory.join("bambu-cli.log").display());
    if !status.success() {
        bail!("Bambu slice exited {}", status.code().unwrap_or(-1));
    }
    slice_review(root, project, report, &directory)
}

/// The cooling values' names, as the policy sets them on a PET-GF slot.
pub fn cooling_keys() -> Result<Vec<String>> {
    cooling::value_names()
}
