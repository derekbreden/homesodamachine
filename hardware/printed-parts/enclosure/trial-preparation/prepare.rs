//! enclosure-print-prep — native Bambu Studio projects for the printed pieces `pieces.json`
//! declares, from the current meshes. Never contacts a printer.
//!
//!     enclosure-print-prep list
//!     enclosure-print-prep <piece> [--printer P] [--part STL[,quantity=N][,turns=x:90][,walls=N][,infill=N][,name=..]]
//!                          [--slice] [--review] [--output DIR] [--border MM]
//!     enclosure-print-prep all --slice
//!
//! `pieces.json` declares every piece: its meshes, pose, printer, recipe changes with their
//! reasons, and the named features read from each mesh. Preparation writes the project, its
//! `preparation.json` record and the show faces; `--slice` slices it with the installed Bambu
//! Studio command line and runs the cooling stage; `--review` reads the emitted archive.

use anyhow::{bail, Context, Result};
use hsm_print_prep::derive::{self, Feature, Geometry};
use hsm_print_prep::json::{python_number, Json};
use hsm_print_prep::mesh::{closed_check, Mesh as RawMesh};
use hsm_print_prep::profile::{self, relative};
use hsm_print_prep::project::{Paint, Plate, Range};
use hsm_print_prep::{npz, seam, sha256_hex, slice};
use serde_json::{json, Map, Value};
use std::collections::{BTreeSet, HashMap};
use std::path::{Path, PathBuf};

const HERE: &str = "hardware/printed-parts/enclosure/trial-preparation";

fn read_json(path: &Path) -> Result<Value> {
    Ok(serde_json::from_slice(&std::fs::read(path).with_context(|| format!("reading {}", path.display()))?)?)
}

fn file_sha(path: &Path) -> Result<String> {
    Ok(sha256_hex(&std::fs::read(path).with_context(|| format!("reading {}", path.display()))?))
}

/// One STL, read once, posed into its print frame.
struct Mesh {
    sha256: String,
    step_sha256: Option<String>,
    vertices: Vec<[f64; 3]>,
    faces: Vec<[usize; 3]>,
    seam_record: Value,
    seam_paint: Vec<Option<Paint>>,
    closed: Value,
    center: [f64; 3],
    rotation: [[f64; 3]; 3],
    lift: f64,
    print_vertices: Vec<[f64; 3]>,
}

fn mat_vec(m: &[[f64; 3]; 3], v: [f64; 3]) -> [f64; 3] {
    [0, 1, 2].map(|i| m[i][0] * v[0] + m[i][1] * v[1] + m[i][2] * v[2])
}

fn mat_t_vec(m: &[[f64; 3]; 3], v: [f64; 3]) -> [f64; 3] {
    [0, 1, 2].map(|i| m[0][i] * v[0] + m[1][i] * v[1] + m[2][i] * v[2])
}

fn mat_mul(a: &[[f64; 3]; 3], b: &[[f64; 3]; 3]) -> [[f64; 3]; 3] {
    let mut out = [[0.0; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            out[i][j] = (0..3).map(|k| a[i][k] * b[k][j]).sum();
        }
    }
    out
}

/// A rotation from a declared pose: a matrix, or ordered turns about x, y and z in degrees.
fn pose_rotation(spec: &Value) -> Result<[[f64; 3]; 3]> {
    let mut m = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]];
    if spec.is_null() {
        return Ok(m);
    }
    if let Some(rows) = spec.get("matrix").and_then(Value::as_array) {
        for i in 0..3 {
            for j in 0..3 {
                m[i][j] = rows[i][j].as_f64().context("pose matrix")?;
            }
        }
    } else {
        for turn in spec.get("turns").and_then(Value::as_array).into_iter().flatten() {
            let axis = turn[0].as_str().context("turn axis")?;
            let degrees = turn[1].as_f64().context("turn degrees")?;
            let (s, c) = degrees.to_radians().sin_cos();
            let t = match axis {
                "x" => [[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]],
                "y" => [[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]],
                _ => [[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]],
            };
            m = mat_mul(&t, &m);
        }
    }
    for row in m.iter_mut() {
        for v in row.iter_mut() {
            if v.abs() < 1e-12 {
                *v = 0.0;
            }
        }
    }
    let mt = mat_mul(&m, &[[m[0][0], m[1][0], m[2][0]], [m[0][1], m[1][1], m[2][1]], [m[0][2], m[1][2], m[2][2]]]);
    let det = m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
    let identity_error = (0..3).flat_map(|i| (0..3).map(move |j| (i, j))).map(|(i, j)| (mt[i][j] - if i == j { 1.0 } else { 0.0 }).abs()).fold(0.0, f64::max);
    if identity_error > 1e-9 || det < 0.0 {
        bail!("pose is not a proper rotation: {spec}");
    }
    Ok(m)
}

impl Mesh {
    fn new(root: &Path, path: &Path, pose: &Value, seam_spec: &Value) -> Result<Mesh> {
        let sha256 = file_sha(path)?;
        let step = path.with_extension("step");
        let step_sha256 = if step.is_file() { Some(file_sha(&step)?) } else { None };
        let raw = RawMesh::read_stl_exact(path)?;
        let (mut vertices, mut faces) = (raw.vertices, raw.faces);
        let mut seam_record = Value::Null;
        let mut seam_paint = vec![None; faces.len()];
        if !seam_spec.is_null() {
            let (v, f, p, record) = seam::strip(&vertices, &faces, seam_spec)?;
            vertices = v;
            faces = f;
            seam_paint = p;
            seam_record = record;
        }
        let closed = closed_check(&faces);
        if closed["closed_oriented_single_body"] != json!(true) {
            bail!("{} is not one closed, oriented body: {closed}", relative(path, root));
        }
        let (low, high) = hsm_print_prep::mesh::bounds(&vertices);
        let center = [0, 1, 2].map(|k| (low[k] + high[k]) / 2.0);
        let rotation = pose_rotation(pose)?;
        let mut placed: Vec<[f64; 3]> = vertices.iter().map(|v| mat_vec(&rotation, [v[0] - center[0], v[1] - center[1], v[2] - center[2]])).collect();
        let lift = -placed.iter().map(|p| p[2]).fold(f64::INFINITY, f64::min);
        for p in placed.iter_mut() {
            p[2] += lift;
        }
        Ok(Mesh { sha256, step_sha256, vertices, faces, seam_record, seam_paint, closed, center, rotation, lift, print_vertices: placed })
    }

    fn geometry(&self) -> Geometry {
        Geometry::new(self.faces.iter().map(|f| f.map(|i| self.print_vertices[i])).collect(), self.faces.clone())
    }

    /// Print-frame points into the stored local frame (the source frame less its center).
    fn print_to_local(&self, p: [f64; 3]) -> [f64; 3] {
        mat_t_vec(&self.rotation, [p[0], p[1], p[2] - self.lift])
    }
}

fn derive_features(root: &Path, mesh: &Mesh, declared: &[Value]) -> Result<Vec<Feature>> {
    let geo = mesh.geometry();
    let mut found: Vec<Feature> = Vec::new();
    let mut foot: Option<f64> = None;
    for feature in declared {
        let kind = feature["kind"].as_str().unwrap_or("");
        if feature.get("enabled") == Some(&Value::Bool(false)) {
            let mut m = Map::new();
            m.insert("name".into(), feature["name"].clone());
            m.insert("kind".into(), json!(kind));
            m.insert("enabled".into(), json!(false));
            m.insert("reason".into(), feature["reason"].clone());
            found.push(Feature { record: m, paint_faces: vec![], paint_codes: Default::default(), boundary_points: vec![] });
            continue;
        }
        match kind {
            "fine_band" => found.push(derive::fine_band(&geo, feature)?),
            "transition_band" => {
                let f = derive::transition_band(&geo, feature)?;
                foot = f.record["foot_print_z_mm"].as_f64();
                found.push(f);
            }
            "ceiling_inset" => {
                let z = foot.with_context(|| format!("{}: declare its transition band first", feature["name"]))?;
                found.push(derive::ceiling_inset(&geo, feature, z)?);
            }
            "tie_windows" => found.push(derive::tie_windows(&geo, feature)?),
            "edge_fins" => {
                let ceiling = found.iter().find(|f| f.kind() == "ceiling_inset").with_context(|| format!("{}: declare its ceiling first", feature["name"]))?;
                let f = derive::edge_fins(&geo, feature, ceiling)?;
                found.push(f);
            }
            "native_support_free" => {
                let path = root.join(feature["record"].as_str().context("record path")?);
                let native = read_json(&path)?;
                if native["source_stl_sha256"].as_str() != Some(&mesh.sha256) {
                    bail!("{} describes a different STL; rebuild {}", relative(&path, root), native["producer"]);
                }
                let centres: Vec<[f64; 3]> = geo.c.iter().map(|c| {
                    let l = mesh.print_to_local(*c);
                    [l[0] + mesh.center[0], l[1] + mesh.center[1], l[2] + mesh.center[2]]
                }).collect();
                let overlap = native["boundary_overlap_mm"].as_f64().unwrap_or(0.0);
                let record_sha = file_sha(&path)?;
                let mut regions: Vec<(&str, &Value)> = Vec::new();
                for (k, key) in [("support_free", "support_free_regions"), ("bridge_direction", "bridge_regions"), ("support_required", "support_regions")] {
                    for r in native.get(key).and_then(Value::as_array).into_iter().flatten() {
                        regions.push((k, r));
                    }
                }
                for (region_kind, region) in regions {
                    if let Some(up) = region.get("support_print_up_source").and_then(Value::as_array) {
                        let print_up = mat_t_vec(&mesh.rotation, [0.0, 0.0, 1.0]);
                        let dot: f64 = (0..3).map(|k| print_up[k] * up[k].as_f64().unwrap_or(0.0)).sum();
                        if dot < region.get("support_direction_cosine_min").and_then(Value::as_f64).unwrap_or(0.99) {
                            continue;
                        }
                    }
                    let b = region.get("blocking_bounds_source_mm").unwrap_or(&region["bounds_source_mm"]);
                    let flat: Vec<f64> = b.as_array().context("region bounds")?.iter().flat_map(|v| v.as_array().map(|a| a.iter().filter_map(Value::as_f64).collect::<Vec<_>>()).unwrap_or_else(|| v.as_f64().into_iter().collect())).collect();
                    let low = [flat[0] - overlap, flat[2] - overlap, flat[4] - overlap];
                    let high = [flat[1] + overlap, flat[3] + overlap, flat[5] + overlap];
                    let faces: Vec<usize> = if region_kind == "support_free" {
                        (0..centres.len()).filter(|&i| (0..3).all(|k| centres[i][k] >= low[k] && centres[i][k] <= high[k]) && geo.n[i][2] < 0.0).collect()
                    } else {
                        vec![]
                    };
                    let mut m = region.as_object().cloned().unwrap_or_default();
                    m.insert("kind".into(), json!(region_kind));
                    m.insert("record".into(), json!(relative(&path, root)));
                    m.insert("record_sha256".into(), json!(record_sha));
                    m.insert("painted_faces".into(), json!(faces.len()));
                    m.insert("blocker_source_mm".into(), json!([low, high]));
                    found.push(Feature { record: m, paint_faces: faces, paint_codes: Default::default(), boundary_points: vec![] });
                }
            }
            other => bail!("unknown feature kind {other}"),
        }
    }
    Ok(found)
}

/// Yaw and plate-centre XY for each footprint, packed in rows and centred.
fn layout(footprints: &[[f64; 2]], low: [f64; 2], high: [f64; 2], spacing: f64, yaw_choice: &Value) -> Vec<(f64, f64, f64)> {
    let (width, depth) = (high[0] - low[0], high[1] - low[1]);
    let (cx, cy) = ((low[0] + high[0]) / 2.0, (low[1] + high[1]) / 2.0);
    if footprints.len() == 1 {
        let [dx, dy] = footprints[0];
        let options: Vec<f64> = match yaw_choice.as_str() {
            Some("auto") | None if yaw_choice.as_f64().is_none() => vec![0.0, 90.0],
            _ => vec![yaw_choice.as_f64().or_else(|| yaw_choice.as_str().and_then(|s| s.parse().ok())).unwrap_or(0.0).trunc()],
        };
        let margin = |yaw: f64| ((width - if yaw == 0.0 { dx } else { dy }).min(depth - if yaw == 0.0 { dy } else { dx })) / 2.0;
        let yaw = options.iter().cloned().max_by(|a, b| {
            let (ma, mb) = ((margin(*a) * 1e6).round(), (margin(*b) * 1e6).round());
            ma.partial_cmp(&mb).unwrap().then((-a).partial_cmp(&-b).unwrap())
        }).unwrap();
        return vec![(yaw, cx, cy)];
    }
    let mut order: Vec<usize> = (0..footprints.len()).collect();
    order.sort_by(|&a, &b| footprints[b][1].partial_cmp(&footprints[a][1]).unwrap());
    let (mut rows, mut row, mut x): (Vec<Vec<(usize, f64, f64, f64)>>, Vec<(usize, f64, f64, f64)>, f64) = (vec![], vec![], 0.0);
    for i in order {
        let [dx, dy] = footprints[i];
        if !row.is_empty() && x + dx > width - 40.0 {
            rows.push(std::mem::take(&mut row));
            x = 0.0;
        }
        row.push((i, x, dx, dy));
        x += dx + spacing;
    }
    rows.push(row);
    let mut placed = vec![(0.0, 0.0); footprints.len()];
    let mut y = 0.0;
    for row in &rows {
        let row_depth = row.iter().map(|r| r.3).fold(f64::NEG_INFINITY, f64::max);
        let last = row.last().unwrap();
        let row_width = last.1 + last.2;
        for &(i, x0, dx, _) in row {
            placed[i] = (x0 + dx / 2.0 - row_width / 2.0, y + row_depth / 2.0);
        }
        y += row_depth + spacing;
    }
    let total = y - spacing;
    (0..footprints.len()).map(|i| (0.0, cx + placed[i].0, cy + placed[i].1 - total / 2.0)).collect()
}

fn yaw_matrix(degrees: f64) -> [[f64; 3]; 3] {
    pose_rotation(&json!({"turns": [["z", degrees]]})).unwrap()
}

fn box_mesh(low: [f64; 3], high: [f64; 3]) -> (Vec<[f64; 3]>, Vec<[usize; 3]>) {
    let ([x0, y0, z0], [x1, y1, z1]) = (low, high);
    (vec![[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]],
     vec![[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
}

fn corners(low: [f64; 3], high: [f64; 3]) -> Vec<[f64; 3]> {
    let mut out = Vec::new();
    for x in [low[0], high[0]] {
        for y in [low[1], high[1]] {
            for z in [low[2], high[2]] {
                out.push([x, y, z]);
            }
        }
    }
    out
}

fn bbox(points: &[[f64; 3]]) -> ([f64; 3], [f64; 3]) { hsm_print_prep::mesh::bounds(points) }

fn pair(v: &Value) -> Result<([f64; 3], [f64; 3])> {
    let a = |i: usize| -> Result<[f64; 3]> {
        let row = v[i].as_array().context("box corner")?;
        Ok([row[0].as_f64().unwrap_or(0.0), row[1].as_f64().unwrap_or(0.0), row[2].as_f64().unwrap_or(0.0)])
    };
    Ok((a(0)?, a(1)?))
}

fn setting_text(v: &Value) -> String {
    match v {
        Value::String(s) => s.clone(),
        Value::Number(n) => n.as_f64().map(python_number).filter(|_| n.is_f64()).unwrap_or_else(|| n.to_string()),
        other => other.to_string(),
    }
}

/// The declared hotend against the one the recipe slices for and the side its filament maps to.
fn check_nozzle(name: &str, piece: &Value, settings: &Json, profile_path: &str) -> Result<Value> {
    let nozzle = &piece["nozzle"];
    let side = match nozzle["side"].as_str() { Some("right") => 1, _ => 0 };
    let diameter: f64 = settings.get("nozzle_diameter").map(Json::list).unwrap_or(&[]).get(side).and_then(Json::text).context("nozzle diameter")?.parse()?;
    if (diameter - nozzle["diameter_mm"].as_f64().unwrap_or(0.0)).abs() > 1e-6 {
        bail!("{name} declares a {} mm {} nozzle; {profile_path} slices {diameter} mm there", nozzle["diameter_mm"], nozzle["side"]);
    }
    let volume: Vec<String> = settings.get("nozzle_volume_type").map(Json::list).unwrap_or(&[]).iter().filter_map(Json::text).map(String::from).collect();
    if let Some(flow) = nozzle.get("flow").and_then(Value::as_str) {
        if volume.len() > side && volume[side] != flow {
            bail!("{name} declares a {flow} {} nozzle; {profile_path} slices {}", nozzle["side"], volume[side]);
        }
    }
    let mapped: BTreeSet<i64> = match settings.get("filament_map") {
        Some(m) => m.list().iter().filter_map(|v| match v { Json::Text(s) => s.parse().ok(), Json::Number(_, n) => Some(*n as i64), _ => None }).collect(),
        None => [1].into(),
    };
    if mapped != [side as i64 + 1].into() {
        bail!("{name} prints on the {} nozzle; the recipe maps its filament to {:?}", nozzle["side"], mapped);
    }
    let mut out = nozzle.as_object().cloned().unwrap_or_default();
    out.insert("sliced_diameter_mm".into(), json!(diameter));
    out.insert("sliced_volume_type".into(), volume.get(side).map(|s| json!(s)).unwrap_or(Value::Null));
    Ok(Value::Object(out))
}

/// A part declared on the command line, and the order of its object settings.
fn parse_part(text: &str) -> Result<(Value, Vec<String>)> {
    let mut items = text.split(',');
    let path = items.next().context("part path")?;
    let mut part = json!({"stl": path, "quantity": 1});
    let mut order: Vec<String> = Vec::new();
    let declare = |order: &mut Vec<String>, key: &str| if !order.iter().any(|k| k == key) { order.push(key.to_string()) };
    for option in items {
        let (key, value) = option.split_once('=').context("part option without '='")?;
        match key {
            "quantity" => part["quantity"] = json!(value.parse::<i64>()?),
            "turns" => {
                let turns: Vec<Value> = value.split('+').map(|t| {
                    let (axis, deg) = t.split_once(':').unwrap_or((t, "0"));
                    json!([axis, deg.parse::<f64>().unwrap_or(0.0)])
                }).collect();
                part["pose"] = json!({"turns": turns});
            }
            "walls" => {
                part["object_settings"]["wall_loops"] = json!({"value": value, "reason": "Command-line part declaration."});
                declare(&mut order, "wall_loops");
            }
            "infill" => {
                part["object_settings"]["sparse_infill_density"] = json!({"value": format!("{value}%"), "reason": "Command-line part declaration."});
                part["object_settings"]["sparse_infill_pattern"] = json!({"value": "zig-zag", "reason": "Command-line part declaration."});
                declare(&mut order, "sparse_infill_density");
                declare(&mut order, "sparse_infill_pattern");
            }
            "name" => part["name"] = json!(value),
            _ => bail!("unknown part option {key}"),
        }
    }
    Ok((part, order))
}

/// pieces.json in its own key order, which serde_json's sorted maps lose: settings added to a
/// recipe go in as declared.
fn read_order(path: &Path) -> Result<Json> {
    Json::parse(&std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?)
}

fn keys_at(order: &Json, path: &[&str]) -> Vec<String> {
    let mut at = order;
    for key in path {
        match at.get(key) {
            Some(next) => at = next,
            None => return Vec::new(),
        }
    }
    at.keys()
}

#[derive(Clone)]
enum Cell {
    None,
    Code(String),
    Attrs(Vec<(String, String)>),
}

fn prepare(root: &Path, name: &str, printer: Option<&str>, parts: Option<Vec<(Value, Vec<String>)>>, output: Option<&Path>, border: Option<f64>) -> Result<PathBuf> {
    let here = root.join(HERE);
    let spec_path = here.join("pieces.json");
    let spec = read_json(&spec_path)?;
    let order = read_order(&spec_path)?;
    let piece = spec["pieces"].get(name).with_context(|| format!("no piece {name}"))?;
    if piece.get("external").is_some() {
        bail!("{name} is prepared by {}", piece["external"]["command"]);
    }
    let printer = printer.map(String::from).unwrap_or_else(|| piece["printer"].as_str().unwrap_or("").to_string());
    let machine = &spec["printers"][&printer];
    let profile_rel = piece.get("profile").or(spec.get("profile")).and_then(Value::as_str).context("no profile")?;
    let profile_path = root.join(profile_rel);
    let z_trim = piece.get("z_trim_mm").and_then(|z| z["value"].as_f64()).or(machine["z_trim_mm"].as_f64()).context("no Z trim")?;
    let filament_from = piece.get("filament_from").and_then(Value::as_str).filter(|s| !s.is_empty()).map(|s| root.join(s));
    let profile = profile::load(&profile_path, Some(z_trim), filament_from.as_deref(), root)?;
    let title = format!("{name}; {printer}");
    let mut plate = Plate::new(&title, &profile, "homesodamachine/enclosure-trial/");
    let mut changes = Map::new();
    let put = |plate: &mut Plate, changes: &mut Map<String, Value>, key: &str, value: &Value, reason: &Value| {
        let from = profile.settings.get(key).map(Json::to_value).unwrap_or(Value::Null);
        changes.insert(key.into(), json!({"from": from, "to": value, "reason": reason}));
        plate.settings.set(key, Json::from_value(value));
    };
    let default_mapping = json!({"value": spec["filament_mapping"], "reason": "Single external black PET-GF spool on the fixed left nozzle for model, support and interface."});
    let (mapping, mapping_keys) = match piece.get("filament_mapping") {
        Some(m) => (m, keys_at(&order, &["pieces", name, "filament_mapping", "value"])),
        None => (&default_mapping, keys_at(&order, &["filament_mapping"])),
    };
    for key in &mapping_keys {
        put(&mut plate, &mut changes, key, &mapping["value"][key], &mapping["reason"]);
    }
    let default_colour = json!({"value": machine["filament_colour"], "reason": format!("{printer}'s loaded black PET-GF colour reading.")});
    let colour = piece.get("filament_colour").unwrap_or(&default_colour);
    put(&mut plate, &mut changes, "filament_colour", &json!([colour["value"]]), &colour["reason"]);
    if let Some(z) = piece.get("z_trim_mm") {
        changes.insert("requested_z_trim_mm".into(), json!({"from": machine["z_trim_mm"], "to": z_trim, "reason": z["reason"]}));
    }
    for key in keys_at(&order, &["pieces", name, "settings"]) {
        let declared = &piece["settings"][&key];
        put(&mut plate, &mut changes, &key, &declared["value"], &declared["reason"]);
    }
    if piece.get("cap_finish_lifts").and_then(|c| c.get("value")).and_then(Value::as_bool) == Some(true) {
        let height: f64 = plate.settings.first_text("printable_height").context("printable height")?.parse()?;
        let limit = height - z_trim.max(0.0);
        let end = plate.settings.get("machine_end_gcode").and_then(Json::text).unwrap_or("").to_string();
        let mut out = String::new();
        let mut rest = end.as_str();
        // The end routine's two clearance lifts over the last layer stop under the printer's ceiling.
        while let Some(at) = rest.find("{max_layer_z") {
            out.push_str(&rest[..at]);
            let tail = &rest[at..];
            let close = tail.find('}').unwrap_or(tail.len() - 1);
            let inner = &tail[1..close];
            let addend = inner.trim_start_matches("max_layer_z").trim().trim_start_matches('+').trim();
            if (addend == "0.4" || addend == "10") && inner.contains('+') {
                out.push_str(&format!("{{min(max_layer_z + {addend}, {})}}", derive::g(limit)));
            } else {
                out.push_str(&tail[..=close]);
            }
            rest = &tail[close + 1..];
        }
        out.push_str(rest);
        put(&mut plate, &mut changes, "machine_end_gcode", &json!(out), &piece["cap_finish_lifts"]["reason"]);
    }
    let nozzle = check_nozzle(name, piece, &plate.settings, &relative(&profile_path, root))?;

    let declared_parts: Vec<(Value, Vec<String>)> = match parts {
        Some(p) => p,
        None => {
            let ordered = order.get("pieces").and_then(|p| p.get(name)).and_then(|p| p.get("parts")).map(Json::list).unwrap_or(&[]);
            piece["parts"].as_array().into_iter().flatten().enumerate()
                .map(|(i, part)| (part.clone(), ordered.get(i).and_then(|p| p.get("object_settings")).map(Json::keys).unwrap_or_default()))
                .collect()
        }
    };
    let mut meshes: HashMap<String, std::rc::Rc<Mesh>> = HashMap::new();
    let mut derived: HashMap<String, std::rc::Rc<Vec<Feature>>> = HashMap::new();
    struct Instance { part: Value, settings_order: Vec<String>, mesh: std::rc::Rc<Mesh>, features: std::rc::Rc<Vec<Feature>>, regions: Option<Value>, name: String }
    let mut instances: Vec<Instance> = Vec::new();
    for (part, settings_order) in &declared_parts {
        let stl = part["stl"].as_str().context("part stl")?;
        let path = root.join(stl);
        if !path.is_file() {
            bail!("{stl} is not exported");
        }
        let key = format!("{stl}|{}|{}", part.get("pose").unwrap_or(&Value::Null), part.get("seam_enforcer").unwrap_or(&Value::Null));
        if !meshes.contains_key(&key) {
            meshes.insert(key.clone(), std::rc::Rc::new(Mesh::new(root, &path, part.get("pose").unwrap_or(&Value::Null), part.get("seam_enforcer").unwrap_or(&Value::Null))?));
        }
        let mesh = meshes[&key].clone();
        let declared = part.get("features").and_then(Value::as_array).cloned().unwrap_or_default();
        let dkey = format!("{key}|{}", serde_json::to_string(&declared)?);
        if !derived.contains_key(&dkey) {
            derived.insert(dkey.clone(), std::rc::Rc::new(derive_features(root, &mesh, &declared)?));
        }
        let features = derived[&dkey].clone();
        let regions = match part.get("regions").and_then(Value::as_str) {
            Some(key) => {
                let file = part.get("regions_file").and_then(Value::as_str).or(spec["regions"].as_str()).context("regions file")?;
                let path = root.join(file);
                let record = read_json(&path)?;
                let bound = record["native_artifact_sha256"].get(key).with_context(|| format!("{} has no regions for {key}", relative(&path, root)))?;
                if bound[".stl"].as_str() != Some(&mesh.sha256) || (mesh.step_sha256.is_some() && bound[".step"].as_str() != mesh.step_sha256.as_deref()) {
                    bail!("{} binds {key} to other exports; regenerate it with {} from the current geometry", relative(&path, root),
                          record.get("producer").and_then(Value::as_str).unwrap_or("heat-set-review/print_regions.py"));
                }
                Some(json!({"record": relative(&path, root), "record_sha256": file_sha(&path)?, "rows": record["pieces"][key],
                            "part_process_overrides": record.get("part_process_overrides").and_then(|o| o.get(key)).cloned().unwrap_or(Value::Null)}))
            }
            None => None,
        };
        let quantity = part.get("quantity").and_then(Value::as_i64).unwrap_or(1);
        let stem = Path::new(stl).file_stem().unwrap().to_string_lossy().to_string();
        let base = part.get("name").and_then(Value::as_str).map(String::from).unwrap_or(stem);
        for copy in 0..quantity {
            let name = if quantity > 1 { format!("{base}-{}", copy + 1) } else { base.clone() };
            instances.push(Instance { part: part.clone(), settings_order: settings_order.clone(), mesh: mesh.clone(), features: features.clone(), regions: regions.clone(), name });
        }
    }
    let (usable_low, usable_high) = (profile.usable_low, profile.usable_high);
    let footprints: Vec<[f64; 2]> = instances.iter().map(|inst| {
        let p = &inst.mesh.print_vertices;
        let (lo, hi) = bbox(p);
        [hi[0] - lo[0], hi[1] - lo[1]]
    }).collect();
    let spacing = piece.get("spacing_mm").and_then(Value::as_f64).unwrap_or(12.0);
    let yaw_choice = piece.get("yaw_degrees").cloned().unwrap_or(json!("auto"));
    let offset = piece.get("plate_offset_mm").and_then(|o| o.get("value")).and_then(Value::as_array)
        .map(|a| [a[0].as_f64().unwrap_or(0.0), a[1].as_f64().unwrap_or(0.0)]).unwrap_or([0.0, 0.0]);
    let placements: Vec<(f64, f64, f64)> = layout(&footprints, usable_low, usable_high, spacing, &yaw_choice)
        .into_iter().map(|(y, cx, cy)| (y, cx + offset[0], cy + offset[1])).collect();
    let border = border.unwrap_or_else(|| piece.get("plate_border_mm").and_then(Value::as_f64).unwrap_or(20.0));
    let brim_type = plate.settings.first_text("brim_type").unwrap_or("").to_string();
    let brim = if brim_type == "outer_only" || brim_type == "outer_and_inner" {
        plate.settings.first_text("brim_width").and_then(|s| s.parse::<f64>().ok()).unwrap_or(5.0) + 0.5
    } else { 0.0 };

    let mut records: Vec<Value> = Vec::new();
    for (inst, &(yaw, cx, cy)) in instances.iter().zip(&placements) {
        let mesh = &inst.mesh;
        let part = &inst.part;
        let r_yaw = yaw_matrix(yaw);
        let p: Vec<[f64; 3]> = mesh.print_vertices.iter().map(|v| mat_vec(&r_yaw, *v)).collect();
        let (plo, phi) = bbox(&p);
        let mid = [(plo[0] + phi[0]) / 2.0, (plo[1] + phi[1]) / 2.0];
        let translation = [cx - mid[0], cy - mid[1], mesh.lift];
        let (low, high) = ([plo[0] + translation[0], plo[1] + translation[1], plo[2]], [phi[0] + translation[0], phi[1] + translation[1], phi[2]]);
        let margin = (low[0] - usable_low[0]).min(low[1] - usable_low[1]).min(usable_high[0] - high[0]).min(usable_high[1] - high[1]);
        if margin - brim < border {
            bail!("{}: the model footprint leaves {margin:.2} mm to the usable plate; with {brim} mm of brim that is inside the {border} mm bed border", inst.name);
        }
        let build_rotation = mat_mul(&r_yaw, &mesh.rotation);
        let to_plate = |q: [f64; 3]| { let r = mat_vec(&r_yaw, q); [r[0] + translation[0], r[1] + translation[1], r[2]] };
        let source_to_plate = |q: [f64; 3]| {
            let r = mat_vec(&build_rotation, [q[0] - mesh.center[0], q[1] - mesh.center[1], q[2] - mesh.center[2]]);
            [r[0] + translation[0], r[1] + translation[1], r[2] + translation[2]]
        };
        let mut paint: Vec<Cell> = mesh.seam_paint.iter().map(|p| match p { Some(a) => Cell::Attrs(a.clone()), None => Cell::None }).collect();
        fn paint_support(cell: &mut Cell, code: &str) {
            match cell {
                Cell::Attrs(a) => {
                    if let Some(slot) = a.iter_mut().find(|(k, _)| k == "paint_supports") { slot.1 = code.into(); } else { a.push(("paint_supports".into(), code.into())); }
                }
                other => *other = Cell::Code(code.into()),
            }
        }
        for f in inst.features.iter() {
            for &i in &f.paint_faces {
                paint_support(&mut paint[i], "8");
            }
            for (&i, code) in &f.paint_codes {
                if matches!(paint[i], Cell::None | Cell::Attrs(_)) {
                    paint_support(&mut paint[i], code);
                }
            }
        }
        let cells: Vec<Paint> = paint.iter().map(|c| match c {
            Cell::None => vec![],
            Cell::Code(code) => vec![("paint_supports".to_string(), code.clone())],
            Cell::Attrs(a) => a.clone(),
        }).collect();
        let object_settings: Vec<(String, String)> = inst.settings_order.iter()
            .map(|k| (k.clone(), setting_text(&part["object_settings"][k]["value"]))).collect();
        let local: Vec<[f64; 3]> = mesh.vertices.iter().map(|v| [v[0] - mesh.center[0], v[1] - mesh.center[1], v[2] - mesh.center[2]]).collect();
        let index = plate.add_object(&inst.name, local, mesh.faces.clone(), &Path::new(part["stl"].as_str().unwrap()).file_name().unwrap().to_string_lossy(),
                                     mesh.center, build_rotation, translation, Some(cells), object_settings);
        let (object_id, identify_id) = (plate.objects[index].object_id, plate.objects[index].identify_id);
        let mut record = json!({"name": inst.name, "identify_id": identify_id, "object_id": object_id,
            "stl": part["stl"], "stl_sha256": mesh.sha256, "step_sha256": mesh.step_sha256,
            "facets": mesh.faces.len(), "closed": mesh.closed, "pose": part.get("pose").cloned().unwrap_or(Value::Null),
            "pose_rotation": mesh.rotation, "yaw_degrees": yaw, "source_center_mm": mesh.center,
            "build_rotation": build_rotation, "translation_mm": translation,
            "plate_bounds_mm": [low, high], "model_bed_margin_mm": margin, "seam_enforcer": mesh.seam_record,
            "object_settings": part.get("object_settings").cloned().unwrap_or(json!({})), "features": [], "ranges": [],
            "verify_spans": [], "ribbons": [], "tie_windows": [], "modifiers": [], "fins": [], "support_free_regions": []});
        for f in inst.features.iter() {
            let mut entry = f.record.clone();
            for k in ["ribbons", "windows", "fins"] {
                entry.remove(k);
            }
            record["features"].as_array_mut().unwrap().push(Value::Object(entry.clone()));
            if !f.enabled() {
                continue;
            }
            match f.kind() {
                "fine_band" => record["verify_spans"].as_array_mut().unwrap().push(json!({"name": f.record["name"],
                    "print_z_mm": f.record["span_print_z_mm"], "layer_height_mm": f.record["layer_height_mm"]})),
                "support_free" => {
                    let (lo, hi) = pair(&f.record["blocker_source_mm"])?;
                    let (v, fc) = box_mesh(sub3(lo, mesh.center), sub3(hi, mesh.center));
                    plate.add_part(index, &format!("{} support exclusion", f.record["name"].as_str().unwrap_or("")), v, fc, "support_blocker", vec![], None);
                    if f.record.get("review_interior") != Some(&Value::Bool(false)) {
                        let placed: Vec<[f64; 3]> = corners(lo, hi).into_iter().map(source_to_plate).collect();
                        let (a, b) = bbox(&placed);
                        let mut row = json!({"name": f.record["name"], "box_plate_mm": [a, b], "bounds_source_mm": f.record["bounds_source_mm"]});
                        if let Some(v) = f.record.get("void_source") { row["void_source"] = v.clone(); }
                        row["reason"] = f.record["reason"].clone();
                        record["support_free_regions"].as_array_mut().unwrap().push(row);
                    }
                }
                "support_required" => {
                    let (lo, hi) = pair(&f.record["blocker_source_mm"])?;
                    let (v, fc) = box_mesh(sub3(lo, mesh.center), sub3(hi, mesh.center));
                    plate.add_part(index, &format!("{} support target", f.record["name"].as_str().unwrap_or("")), v, fc, "support_enforcer", vec![], None);
                    record.as_object_mut().unwrap().entry("support_targets").or_insert(json!([])).as_array_mut().unwrap().push(Value::Object(entry.clone()));
                }
                "tie_windows" => {
                    let overlap = f.record["blocker_roof_overlap_mm"].as_f64().unwrap_or(0.0);
                    for window in f.record["windows"].as_array().into_iter().flatten() {
                        let (lo, hi) = pair(&window["box_print_mm"])?;
                        let cs = corners(lo, hi);
                        let placed: Vec<[f64; 3]> = cs.iter().map(|c| to_plate(*c)).collect();
                        let (a, b) = bbox(&placed);
                        let mut w = window.clone();
                        w["box_plate_mm"] = json!([a, b]);
                        record["tie_windows"].as_array_mut().unwrap().push(w);
                        if f.record["blockers"].as_bool() == Some(true) {
                            // Intersect the requesting roof; a blocker ending under it leaves supports inside.
                            let raised: Vec<[f64; 3]> = cs.iter().map(|c| if c[2] == hi[2] { [c[0], c[1], c[2] + overlap] } else { *c }).collect();
                            let local: Vec<[f64; 3]> = raised.iter().map(|c| mesh.print_to_local(*c)).collect();
                            let (llo, lhi) = bbox(&local);
                            let (v, fc) = box_mesh(llo, lhi);
                            plate.add_part(index, "Tie channel support exclusion", v, fc, "support_blocker", vec![], None);
                        }
                    }
                }
                "edge_fins" => {
                    for fin in f.record["fins"].as_array().into_iter().flatten() {
                        let mut boxes = vec![("normal_part", "box_print_mm"), ("support_blocker", "blocker_print_mm")];
                        if fin.get("foot_print_mm").is_some() {
                            boxes.push(("normal_part", "foot_print_mm"));
                        }
                        for (kind, key) in boxes {
                            let (lo, hi) = pair(&fin[key])?;
                            let local: Vec<[f64; 3]> = corners(lo, hi).iter().map(|c| mesh.print_to_local(*c)).collect();
                            let (llo, lhi) = bbox(&local);
                            let (v, fc) = box_mesh(llo, lhi);
                            let normal = kind == "normal_part";
                            plate.add_part(index, if normal { "Removable edge fin" } else { "Edge fin contact strip" }, v, fc, kind,
                                           if normal { vec![("wall_loops".into(), "2".into()), ("sparse_infill_density".into(), "0%".into())] } else { vec![] },
                                           if normal { Some("8") } else { None });
                        }
                        let (lo, hi) = pair(&fin["box_print_mm"])?;
                        let placed = [to_plate(lo), to_plate(hi)];
                        let (a, b) = bbox(&placed);
                        let mut row = fin.clone();
                        row["box_plate_mm"] = json!([a, b]);
                        record["fins"].as_array_mut().unwrap().push(row);
                    }
                }
                _ => {}
            }
        }
        if part.get("pause").is_some() {
            bail!("{}: pieces.json declares a pause, and preparation does not pause a print", inst.name);
        }
        if let Some(regions) = &inst.regions {
            let mut kept = regions.as_object().cloned().unwrap_or_default();
            kept.remove("rows");
            if !regions["part_process_overrides"].is_null() {
                kept.insert("whole_part_settings_apply".into(), json!(true));
            } else {
                let (slo, shi) = bbox(&mesh.vertices);
                for row in regions["rows"].as_array().into_iter().flatten() {
                    let b = row.get("applied_source_bounds_mm").unwrap_or(&row["machine_bounds_mm"]);
                    let flat: Vec<f64> = b.as_array().context("region bounds")?.iter().flat_map(|v| v.as_array().map(|a| a.iter().filter_map(Value::as_f64).collect::<Vec<_>>()).unwrap_or_else(|| v.as_f64().into_iter().collect())).collect();
                    let lo = [flat[0].max(slo[0] + 0.001), flat[2].max(slo[1] + 0.001), flat[4].max(slo[2] + 0.001)];
                    let hi = [flat[1].min(shi[0] - 0.001), flat[3].min(shi[1] - 0.001), flat[5].min(shi[2] - 0.001)];
                    if (0..3).any(|k| hi[k] <= lo[k]) {
                        bail!("{}: region {} lies outside the mesh", inst.name, row["name"]);
                    }
                    if (0..3).all(|k| hi[k] - lo[k] > 1e-6) {
                        let (v, fc) = box_mesh(sub3(lo, mesh.center), sub3(hi, mesh.center));
                        let density = row.get("sparse_infill_density").and_then(Value::as_str).unwrap_or("100%").to_string();
                        let pattern = row.get("sparse_infill_pattern").and_then(Value::as_str).unwrap_or("zig-zag").to_string();
                        plate.add_part(index, row["name"].as_str().unwrap_or(""), v, fc, "modifier_part",
                                       vec![("sparse_infill_density".into(), density.clone()), ("sparse_infill_pattern".into(), pattern)], None);
                        let placed: Vec<[f64; 3]> = corners(lo, hi).into_iter().map(source_to_plate).collect();
                        let (a, b) = bbox(&placed);
                        record["modifiers"].as_array_mut().unwrap().push(json!({"name": row["name"], "source_bounds_mm": [lo, hi],
                            "plate_bounds_mm": [a, b], "sparse_infill_density": density}));
                    }
                }
            }
            record["regions"] = Value::Object(kept);
        }
        for f in inst.features.iter() {
            let Some(axis) = f.record.get("bridge_print_axis_source").and_then(Value::as_array) else { continue };
            let axis = mat_vec(&build_rotation, [axis[0].as_f64().unwrap_or(0.0), axis[1].as_f64().unwrap_or(0.0), axis[2].as_f64().unwrap_or(0.0)]);
            let mut angle = axis[1].atan2(axis[0]).to_degrees().rem_euclid(180.0);
            if angle == 0.0 { angle = 180.0; }
            let (mut lo, mut hi) = pair(&f.record["blocker_source_mm"])?;
            let (slo, shi) = bbox(&mesh.vertices);
            for k in 0..3 {
                lo[k] = lo[k].max(slo[k] + 0.001);
                hi[k] = hi[k].min(shi[k] - 0.001);
            }
            let (v, fc) = box_mesh(sub3(lo, mesh.center), sub3(hi, mesh.center));
            let name = format!("{} transverse bridge", f.record["name"].as_str().unwrap_or(""));
            plate.add_part(index, &name, v, fc, "modifier_part", vec![("bridge_angle".into(), python_number(angle)),
                ("sparse_infill_density".into(), "100%".into()), ("sparse_infill_pattern".into(), "zig-zag".into())], None);
            let placed: Vec<[f64; 3]> = corners(lo, hi).into_iter().map(source_to_plate).collect();
            let (a, b) = bbox(&placed);
            record["modifiers"].as_array_mut().unwrap().push(json!({"name": name, "source_bounds_mm": [lo, hi],
                "plate_bounds_mm": [a, b], "sparse_infill_density": "100%", "bridge_angle_deg": angle}));
        }
        let ranges = derive::layer_ranges(&inst.features);
        plate.objects[index].ranges = ranges.iter().map(|r| Range {
            min_z: r["min_z"].as_f64().unwrap(), max_z: r["max_z"].as_f64().unwrap(),
            options: r["options"].as_object().unwrap().iter().map(|(k, v)| (k.clone(), v.as_str().unwrap_or("").to_string())).collect(),
        }).collect();
        record["ranges"] = json!(ranges);
        records.push(record);
    }
    let sources: BTreeSet<String> = records.iter().filter_map(|r| r["stl_sha256"].as_str().map(String::from)).collect();
    let stamp = String::from_utf8(std::process::Command::new("date").arg("+%Y-%m-%d").output()?.stdout)?.trim().to_string();
    let stem = format!("{stamp}-{name}-{}-{}", printer.to_lowercase(), &sha256_hex(sources.into_iter().collect::<String>().as_bytes())[..8]);
    let base = output.map(Path::to_path_buf).unwrap_or_else(|| root.join(".cache/prints/trial"));
    std::fs::create_dir_all(&base)?;
    let directory = base.canonicalize()?.join(&stem);
    if directory.exists() {
        bail!("{} exists; a preparation directory is written once", relative(&directory, root));
    }
    std::fs::create_dir_all(&directory)?;
    let project = directory.join(format!("{stem}.3mf"));
    plate.write(&project)?;
    let mut painted = Vec::new();
    for (inst, record) in instances.iter().zip(&records) {
        let index: BTreeSet<usize> = inst.features.iter().flat_map(|f| f.paint_faces.iter().cloned()).collect();
        let r: Vec<Vec<f64>> = serde_json::from_value(record["build_rotation"].clone())?;
        let rot = [[r[0][0], r[0][1], r[0][2]], [r[1][0], r[1][1], r[1][2]], [r[2][0], r[2][1], r[2][2]]];
        let t: Vec<f64> = serde_json::from_value(record["translation_mm"].clone())?;
        let mesh = &inst.mesh;
        let triangles: Vec<[[f64; 3]; 3]> = index.iter().map(|&f| mesh.faces[f].map(|i| {
            let v = mat_vec(&rot, sub3(mesh.vertices[i], mesh.center));
            [v[0] + t[0], v[1] + t[1], v[2] + t[2]]
        })).collect();
        painted.push((record["identify_id"].to_string(), triangles));
    }
    npz::write_triangles(&directory.join("show-faces.npz"), &painted)?;
    let bed = plate.settings.first_text("curr_bed_type").unwrap_or("").to_string();
    let settings_text = plate.settings.dumps() + "\n";
    let mut tools = Map::new();
    for path in [root.join(HERE).join("prepare.rs")].into_iter().chain(std::fs::read_dir(root.join("tools/hsm/print-prep/src"))?.filter_map(|e| e.ok().map(|e| e.path()))) {
        tools.insert(relative(&path, root), json!(file_sha(&path)?));
    }
    let preparation = json!({
        "piece": name, "printer": printer, "connection_key": machine.get("connection_key").cloned().unwrap_or(json!(printer)),
        "nozzle": nozzle, "material": piece["material"], "bed_type": bed, "requested_z_trim_mm": z_trim,
        // Bambu's Textured PEI compensation emits less than the request, by the amount here;
        // other plates emit the request.
        "emitted_textured_trim_mm": ((z_trim - if bed == "Textured PEI Plate" { 0.02 } else { 0.0 }) * 1000.0).round() / 1000.0,
        "project": relative(&project, root), "project_sha256": file_sha(&project)?,
        "profile": relative(&profile_path, root), "profile_sha256": file_sha(&profile_path)?,
        "settings_sha256": sha256_hex(settings_text.as_bytes()), "settings_changes": changes, "profile_changes": profile.changes,
        "usable_plate_mm": [usable_low, usable_high], "plate_border_mm": border, "brim_allowance_mm": brim,
        "plate_offset_mm": piece.get("plate_offset_mm").cloned().unwrap_or(Value::Null), "objects": records, "pause": Value::Null,
        "show_faces": relative(&directory.join("show-faces.npz"), root),
        "spec": relative(&spec_path, root), "spec_sha256": file_sha(&spec_path)?, "tool_sha256": tools,
        "prepared_utc": String::from_utf8(std::process::Command::new("date").args(["-u", "+%Y-%m-%dT%H:%M:%S+00:00"]).output()?.stdout)?.trim(),
        "sliced": false, "submitted": false,
    });
    std::fs::write(directory.join("preparation.json"), serde_json::to_string_pretty(&preparation)? + "\n")?;
    println!("{}", relative(&project, root));
    for record in &records {
        println!("  {}: yaw {}, model margin {:.1} mm, ranges {}, tie windows {}, modifiers {}", record["name"].as_str().unwrap_or(""),
                 record["yaw_degrees"], record["model_bed_margin_mm"].as_f64().unwrap_or(0.0), record["ranges"].as_array().map_or(0, Vec::len),
                 record["tie_windows"].as_array().map_or(0, Vec::len), record["modifiers"].as_array().map_or(0, Vec::len));
    }
    Ok(directory)
}

fn sub3(a: [f64; 3], b: [f64; 3]) -> [f64; 3] { [a[0] - b[0], a[1] - b[1], a[2] - b[2]] }

/// Slice a preparation with the installed Bambu Studio command line, then run the cooling stage.
fn slice_project(root: &Path, directory: &Path, slicer: &Path) -> Result<PathBuf> {
    let path = directory.join("preparation.json");
    let mut preparation = read_json(&path)?;
    let project = root.join(preparation["project"].as_str().context("project")?);
    if Some(file_sha(&project)?.as_str()) != preparation["project_sha256"].as_str() {
        bail!("the project changed after preparation");
    }
    let archive_name = project.file_name().unwrap().to_string_lossy().replace(".3mf", ".gcode.3mf");
    let native = directory.join("native");
    std::fs::create_dir(&native)?;
    let cli = slice::cli_project(&project, &native)?;
    let command = vec![slicer.display().to_string(), "--slice".into(), "0".into(), "--arrange".into(), "0".into(), "--orient".into(), "0".into(),
                       "--outputdir".into(), native.display().to_string(), "--export-3mf".into(), archive_name.clone(), cli.display().to_string()];
    let log = std::fs::File::create(native.join("slice.log"))?;
    let status = std::process::Command::new(&command[0]).args(&command[1..]).current_dir(&native)
        .env("OMP_NUM_THREADS", "1").env("OPENBLAS_NUM_THREADS", "1")
        .stdout(log.try_clone()?).stderr(log).status()?;
    if !status.success() {
        bail!("Bambu Studio exited {}; see {}", status.code().unwrap_or(-1), relative(&native.join("slice.log"), root));
    }
    let sliced = read_json(&native.join("result.json"))?;
    if sliced["return_code"].as_i64() != Some(0) {
        bail!("Bambu Studio reported {}", sliced["error_string"]);
    }
    slice::apply_directory(&native, &project)?;
    let sliced = read_json(&native.join("result.json"))?;
    std::fs::write(directory.join("slice-command.json"), serde_json::to_string_pretty(&command)? + "\n")?;
    let archive = directory.join(&archive_name);
    std::fs::copy(native.join(&archive_name), &archive)?;
    let mut zip = zip::ZipArchive::new(std::fs::File::open(&archive)?)?;
    let mut gcode = Vec::new();
    std::io::Read::read_to_end(&mut zip.by_name("Metadata/plate_1.gcode")?, &mut gcode)?;
    let mut md5 = String::new();
    std::io::Read::read_to_string(&mut zip.by_name("Metadata/plate_1.gcode.md5")?, &mut md5)?;
    if hsm_print_prep::ids::md5_hex(&gcode) != md5.trim().to_lowercase() {
        bail!("the embedded G-code does not match its MD5");
    }
    std::fs::write(directory.join("slice-result.json"), serde_json::to_string_pretty(&sliced)? + "\n")?;
    let cooling = native.join(Path::new(&archive_name).with_extension("cooling.json"));
    if cooling.is_file() {
        preparation["cooling_recovery"] = read_json(&cooling)?;
    }
    let plates = sliced["sliced_plates"].as_array().cloned().unwrap_or_default();
    preparation["sliced"] = json!(true);
    preparation["archive"] = json!(relative(&archive, root));
    preparation["archive_sha256"] = json!(file_sha(&archive)?);
    preparation["gcode_sha256"] = json!(sha256_hex(&gcode));
    preparation["estimated_seconds"] = json!(plates.iter().map(|p| p["total_predication"].as_f64().unwrap_or(0.0)).sum::<f64>());
    preparation["slicer_warnings"] = json!(plates.iter().filter_map(|p| p["warning_message"].as_str()).filter(|s| !s.is_empty()).collect::<Vec<_>>());
    std::fs::write(&path, serde_json::to_string_pretty(&preparation)? + "\n")?;
    println!("{}", relative(&archive, root));
    Ok(archive)
}

fn listing(root: &Path) -> Result<()> {
    let spec_path = root.join(HERE).join("pieces.json");
    let spec = read_json(&spec_path)?;
    let mut region_files: HashMap<String, Value> = HashMap::new();
    for name in keys_at(&read_order(&spec_path)?, &["pieces"]) {
        let piece = &spec["pieces"][&name];
        let nozzle = &piece["nozzle"];
        let head = format!("{name:22} {:6} {:5} {} mm {}, {}", piece["printer"].as_str().unwrap_or(""), nozzle["side"].as_str().unwrap_or("-"),
                           nozzle["diameter_mm"].as_f64().map(derive::g).unwrap_or("0".into()), nozzle["flow"].as_str().unwrap_or(""), piece["material"].as_str().unwrap_or("-"));
        if let Some(external) = piece.get("external") {
            println!("{head}\n    external: {}", external["command"].as_array().map(|c| c.iter().filter_map(Value::as_str).collect::<Vec<_>>().join(" ")).unwrap_or_default());
            continue;
        }
        if let Some(archive) = piece.get("archive") {
            println!("{head}\n    archive: {}  {}", archive["path"].as_str().unwrap_or(""), check_archive(root, piece)?);
            continue;
        }
        println!("{head}");
        for part in piece["parts"].as_array().into_iter().flatten() {
            let stl = part["stl"].as_str().unwrap_or("");
            let path = root.join(stl);
            let state = if path.is_file() { file_sha(&path)?[..12].to_string() } else { "missing".into() };
            let mut binding = String::new();
            if let (Some(key), true) = (part.get("regions").and_then(Value::as_str), path.is_file()) {
                let file = part.get("regions_file").and_then(Value::as_str).or(spec["regions"].as_str()).unwrap_or("").to_string();
                if !region_files.contains_key(&file) {
                    region_files.insert(file.clone(), read_json(&root.join(&file))?["native_artifact_sha256"].clone());
                }
                let bound = region_files[&file].get(key).and_then(|b| b.get(".stl")).and_then(Value::as_str);
                binding = if bound == Some(file_sha(&path)?.as_str()) { "regions bound".into() } else { "regions stale".into() };
            }
            println!("    {} x {stl}  {state}  {binding}", part.get("quantity").and_then(Value::as_i64).unwrap_or(1));
        }
    }
    Ok(())
}

fn check_archive(root: &Path, piece: &Value) -> Result<&'static str> {
    let path = root.join(piece["archive"]["path"].as_str().unwrap_or(""));
    if !path.is_file() {
        return Ok("missing");
    }
    Ok(if Some(file_sha(&path)?.as_str()) == piece["archive"]["sha256"].as_str() { "bound" } else { "CHANGED" })
}

/// A piece prepared by its own program: a Python script, run with the checkout's Python, or a
/// program named by its path in the checkout.
fn run_external(root: &Path, piece: &Value) -> Result<()> {
    let mut command: Vec<String> = piece["external"]["command"].as_array().into_iter().flatten().filter_map(Value::as_str).map(|c| {
        if c.ends_with(".py") { root.join(c).display().to_string() } else { c.to_string() }
    }).collect();
    if command.is_empty() {
        bail!("the external command is empty");
    }
    if !command[0].ends_with(".py") {
        command[0] = root.join(&command[0]).display().to_string();
    } else {
        command.insert(0, root.join("tools/cad-venv/bin/python").display().to_string());
    }
    println!("{}", command.join(" "));
    let status = std::process::Command::new(&command[0]).args(&command[1..]).current_dir(root).status()?;
    if !status.success() {
        bail!("{} exited {}", command.first().cloned().unwrap_or_default(), status.code().unwrap_or(-1));
    }
    Ok(())
}

fn main() -> Result<()> {
    let root = hsm_print_prep::root();
    let mut args = std::env::args().skip(1);
    let target = args.next().context("usage: enclosure-print-prep list|all|<piece> [options]")?;
    let (mut printer, mut parts, mut do_slice, mut review, mut output, mut border) = (None, Vec::new(), false, false, None, None);
    while let Some(arg) = args.next() {
        let mut value = || args.next().with_context(|| format!("{arg} needs a value"));
        match arg.as_str() {
            "--printer" => printer = Some(value()?),
            "--part" => parts.push(parse_part(&value()?)?),
            "--slice" => do_slice = true,
            "--review" => review = true,
            "--output" => output = Some(PathBuf::from(value()?)),
            "--border" => border = Some(value()?.parse::<f64>()?),
            _ => bail!("unknown argument {arg}"),
        }
    }
    if target == "list" {
        return listing(&root);
    }
    // Preparing reads large meshes and slicing runs Bambu Studio: one of the Mac's heavy runs.
    hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
    let spec_path = root.join(HERE).join("pieces.json");
    let spec = read_json(&spec_path)?;
    let names: Vec<String> = if target == "all" { keys_at(&read_order(&spec_path)?, &["pieces"]) } else { vec![target.clone()] };
    if !parts.is_empty() && names.len() > 1 {
        bail!("--part names one plate's parts");
    }
    let mut failed = Vec::new();
    for name in &names {
        let piece = &spec["pieces"][name];
        let result: Result<()> = (|| {
            if piece.get("archive").is_some() {
                let state = check_archive(&root, piece)?;
                println!("{name}: prints from {} ({state}); nothing to prepare", piece["archive"]["path"].as_str().unwrap_or(""));
                if state != "bound" { bail!("the archive is {state}"); }
                return Ok(());
            }
            if piece.get("external").is_some() {
                if do_slice || target == *name { run_external(&root, piece)?; }
                else { println!("{name}: prepared and sliced by its own command (--slice runs it)"); }
                return Ok(());
            }
            let directory = prepare(&root, name, printer.as_deref(), (!parts.is_empty()).then(|| parts.clone()), output.as_deref(), border)?;
            if do_slice {
                slice_project(&root, &directory, Path::new(slice::SLICER))?;
            }
            if review {
                let mut command = vec![root.join(HERE).join("review.py").display().to_string(), directory.display().to_string()];
                if !do_slice { command.push("--project-only".into()); }
                let status = std::process::Command::new(root.join("tools/cad-venv/bin/python")).args(&command).current_dir(&root).status()?;
                if !status.success() { bail!("review exited {}", status.code().unwrap_or(-1)); }
            }
            Ok(())
        })();
        if let Err(error) = result {
            if names.len() == 1 { return Err(error); }
            println!("{name}: {error}");
            failed.push(name.clone());
        }
    }
    if !failed.is_empty() {
        bail!("{} piece(s) not prepared: {}", failed.len(), failed.join(", "));
    }
    Ok(())
}
