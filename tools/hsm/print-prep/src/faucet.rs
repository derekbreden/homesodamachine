//! The faucet's finishing steps on a refreshed plate, as its production selection names them:
//! the overhang and bridge recipe over the localized cooling, rear seams painted on the build
//! pose's silhouette, and the accepted support parts carried in from the projects that proved
//! them.

use crate::json::{python_number, Json};
use crate::project::Paint;
use crate::refresh::Refreshed;
use crate::{cooling, sha256_hex, xml};
use anyhow::{Context, Result, ensure};
use hsm_faucet_numbers::paths as faucet_paths;
use serde_json::{json, Map, Value};
use std::collections::BTreeMap;
use std::io::{Cursor, Read, Seek};
use std::path::Path;

pub fn read_json(path: &Path) -> Result<Value> {
    Ok(serde_json::from_slice(&std::fs::read(path).with_context(|| format!("reading {}", path.display()))?)?)
}

pub fn file_sha(path: &Path) -> Result<String> {
    Ok(sha256_hex(&std::fs::read(path).with_context(|| format!("reading {}", path.display()))?))
}

/// Every member of a project.
pub fn members(path: &Path) -> Result<BTreeMap<String, Vec<u8>>> {
    archive_members(std::fs::File::open(path).with_context(|| format!("opening {}", path.display()))?)
}

/// Read the members of an open project or a retained project blob.
pub fn archive_members(input: impl Read + Seek) -> Result<BTreeMap<String, Vec<u8>>> {
    let mut archive = zip::ZipArchive::new(input)?;
    let mut out = BTreeMap::new();
    for i in 0..archive.len() {
        let mut entry = archive.by_index(i)?;
        let name = entry.name()?.to_string();
        let mut bytes = Vec::new();
        entry.read_to_end(&mut bytes)?;
        out.insert(name, bytes);
    }
    Ok(out)
}

/// Read a production recipe's immutable evidence from its recorded Git revision.
pub fn recorded_member(root: &Path, record: &Value, key: &str) -> Result<Vec<u8>> {
    let path = record[key].as_str().with_context(|| format!("missing recorded evidence {key}"))?;
    let commit = record["source_commit"].as_str().context("recorded evidence revision")?;
    let result = std::process::Command::new("git")
        .args(["show", &format!("{commit}:{path}")])
        .current_dir(root)
        .output()?;
    ensure!(result.status.success(), "reading the retained evidence {commit}:{path}");
    Ok(result.stdout)
}

/// A JSON value as Python's `str` writes it into a setting.
pub fn text(v: &Value) -> String {
    match v {
        Value::String(s) => s.clone(),
        Value::Number(n) if n.is_i64() || n.is_u64() => n.to_string(),
        Value::Number(n) => python_number(n.as_f64().unwrap_or(0.0)),
        Value::Bool(b) => if *b { "True".into() } else { "False".into() },
        other => other.to_string(),
    }
}

pub fn as_texts(v: &Json) -> Vec<String> {
    v.list().iter().filter_map(Json::text).map(String::from).collect()
}

pub fn texts(items: &[String]) -> Json {
    Json::List(items.iter().map(|s| Json::Text(s.clone())).collect())
}

/// Keep ordinary PET-GF paths uncooled; cool bridges and qualifying overhangs.
pub fn apply_overhang_recipe(settings: &mut Json, selected: &Value, hook: &str) -> Result<Map<String, Value>> {
    let mut changes = cooling::apply(settings, Some(hook))?.as_object().cloned().unwrap_or_default();
    let mut put = |settings: &mut Json, key: &str, value: &Value| -> Result<()> {
        let old = settings.get(key).cloned().with_context(|| format!("the profile has no {key}"))?;
        let new = match &old {
            Json::List(items) => texts(&vec![text(value); items.len()]),
            _ => Json::Text(text(value)),
        };
        if old != new {
            changes.insert(key.into(), json!({"from": old.to_value(), "to": new.to_value()}));
            settings.set(key, new);
        }
        Ok(())
    };
    put(settings, "overhang_fan_speed", &selected["fan_percent"])?;
    put(settings, "overhang_fan_threshold", &selected["fan_threshold"])?;
    for key in ["close_fan_the_first_x_layers", "close_additional_fan_first_x_layers"] {
        put(settings, key, &selected["fan_off_bed_layers"])?;
    }
    for key in ["first_x_layer_fan_speed", "first_x_layer_part_fan_speed"] {
        put(settings, key, &json!(0))?;
    }
    let maximum = &selected["maximum_overhang_speed_mm_s"];
    let limit = maximum.as_f64().context("maximum overhang speed")?;
    for prefix in ["", "filament_"] {
        for kind in ["1_4", "2_4", "3_4", "4_4", "totally"] {
            let key = format!("{prefix}overhang_{kind}_speed");
            let old = settings.get(&key).cloned().with_context(|| format!("the profile has no {key}"))?;
            // A slower saved limit stays; a faster or unset one takes the recipe's.
            let new: Vec<String> = as_texts(&old).iter().map(|v| {
                let speed: f64 = v.parse().unwrap_or(0.0);
                if speed > 0.0 && speed <= limit { python_number(speed) } else { text(maximum) }
            }).collect();
            if as_texts(&old) != new {
                changes.insert(key.clone(), json!({"from": old.to_value(), "to": new}));
                settings.set(&key, texts(&new));
            }
        }
    }
    Ok(changes)
}

pub fn mat(build: &[f64; 12]) -> [[f64; 3]; 3] {
    [[build[0], build[1], build[2]], [build[3], build[4], build[5]], [build[6], build[7], build[8]]]
}

/// Row vector times matrix.
pub fn times(p: [f64; 3], m: &[[f64; 3]; 3]) -> [f64; 3] {
    [0, 1, 2].map(|c| p[0] * m[0][c] + p[1] * m[1][c] + p[2] * m[2][c])
}

pub fn sub(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

pub fn cross(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}

pub fn unit(v: [f64; 3]) -> [f64; 3] {
    let l = (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]).sqrt().max(1e-12);
    v.map(|c| c / l)
}

/// The project's copy of a part's vertices, back in its source frame: what the member holds, to
/// its nine decimals, plus the source centre.
pub fn source_vertices(r: &Refreshed, index: usize) -> Vec<[f64; 3]> {
    let obj = &r.plate.objects[index];
    obj.vertices.iter().map(|v| [0, 1, 2].map(|k| format!("{:.9}", v[k]).parse::<f64>().unwrap() + obj.source_center[k])).collect()
}

pub fn set_paint(paint: &mut Paint, key: &str, value: &str) {
    match paint.iter_mut().find(|(k, _)| k == key) {
        Some(slot) => slot.1 = value.to_string(),
        None => paint.push((key.to_string(), value.to_string())),
    }
}

pub fn paint_of(r: &mut Refreshed, index: usize) -> &mut Vec<Paint> {
    let obj = &mut r.plate.objects[index];
    let faces = obj.faces.len();
    obj.paint.get_or_insert_with(|| vec![Vec::new(); faces])
}

/// Paint the part's complete rear silhouette, in the actual build pose, as a seam: the facets
/// crossing CAD X = 0 within the declared half-width whose crossing lies on the section's rear
/// boundary at its build height, including tilted stage shoulders. The mesh is unchanged.
pub fn enforce_rear_seam(r: &mut Refreshed, target: &Value) -> Result<Value> {
    let name = target["part"].as_str().context("seam part")?;
    let index = r.row(name)?.index;
    let vertices = source_vertices(r, index);
    let faces = r.plate.objects[index].faces.clone();
    let rotation = mat(&r.plate.objects[index].transform_values());
    let build: Vec<[f64; 3]> = vertices.iter().map(|v| times(*v, &rotation)).collect();
    let half = target["half_width_mm"].as_f64().unwrap_or(0.0);
    let curved = target["surface"].as_str() == Some("curved_outer_arc");
    let arc_center = [faucet_paths::WATER_Y - faucet_paths::water_radius(), faucet_paths::arc_start_z()];
    let arc_radius = faucet_paths::water_radius() + faucet_paths::SHELL_CENTER_N + faucet_paths::SHELL_RADIUS;
    // The mesh's section by the plane CAD X = 0, in the build frame. A vertex within merging
    // distance of the plane lies on it: an edge on the plane is a segment, and so is a vertex on
    // it with the opposite edge crossing it.
    const ON_PLANE: f64 = 1e-8;
    let side = |x: f64| if x.abs() < ON_PLANE { 0 } else if x > 0.0 { 1 } else { -1 };
    let mut segments: Vec<[[f64; 3]; 2]> = Vec::new();
    for f in &faces {
        let p = f.map(|i| build[i]);
        let sides = p.map(|q| side(q[0]));
        if sides.iter().all(|s| *s == 0) {
            continue;
        }
        let mut points: Vec<[f64; 3]> = Vec::new();
        for k in 0..3 {
            if sides[k] == 0 {
                points.push(p[k]);
            }
        }
        for k in 0..3 {
            let (a, b) = (p[k], p[(k + 1) % 3]);
            if sides[k] * sides[(k + 1) % 3] < 0 {
                let t = a[0] / (a[0] - b[0]);
                points.push([0.0, a[1] + t * (b[1] - a[1]), a[2] + t * (b[2] - a[2])]);
            }
        }
        if points.len() == 2 {
            segments.push([points[0], points[1]]);
        }
    }
    let mut selected = 0usize;
    let (mut lo, mut hi) = ([f64::INFINITY; 3], [f64::NEG_INFINITY; 3]);
    let mut picked = Vec::new();
    for (fi, f) in faces.iter().enumerate() {
        let source = f.map(|i| vertices[i]);
        let triangle = f.map(|i| build[i]);
        let normal = unit(cross(sub(triangle[1], triangle[0]), sub(triangle[2], triangle[0])));
        let xs = source.map(|p| p[0]);
        if !(normal[1] > 1e-5 && normal[0].abs() < 0.35 && xs.iter().copied().fold(f64::INFINITY, f64::min) <= half
             && xs.iter().copied().fold(f64::NEG_INFINITY, f64::max) >= -half) {
            continue;
        }
        let (xmin, xmax) = (triangle.iter().map(|p| p[0]).fold(f64::INFINITY, f64::min), triangle.iter().map(|p| p[0]).fold(f64::NEG_INFINITY, f64::max));
        let x = (0.0f64.max(xmin + 1e-9)).min(xmax - 1e-9);
        let mut cuts = Vec::new();
        for k in 0..3 {
            let (a, b) = (triangle[k], triangle[(k + 1) % 3]);
            if (a[0] - x) * (b[0] - x) <= 0.0 && (a[0] - b[0]).abs() > 1e-10 {
                let t = (x - a[0]) / (b[0] - a[0]);
                cuts.push([a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]), a[2] + t * (b[2] - a[2])]);
            }
        }
        if cuts.len() < 2 {
            continue;
        }
        let n = cuts.len() as f64;
        let midpoint = [0, 1, 2].map(|k| cuts.iter().map(|c| c[k]).sum::<f64>() / n);
        if curved {
            // Back into CAD: the transpose of the build turn.
            let cad = [0, 1, 2].map(|i| (0..3).map(|j| midpoint[j] * rotation[i][j]).sum::<f64>());
            if ((cad[1] - arc_center[0]).hypot(cad[2] - arc_center[1]) - arc_radius).abs() > 0.15 {
                continue;
            }
        }
        let z = midpoint[2];
        let ys: Vec<f64> = segments.iter().filter(|s| s[0][2].min(s[1][2]) <= z && s[0][2].max(s[1][2]) >= z && (s[1][2] - s[0][2]).abs() > 1e-8)
            .map(|s| s[0][1] + (z - s[0][2]) / (s[1][2] - s[0][2]) * (s[1][1] - s[0][1])).collect();
        let top = ys.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        if ys.is_empty() || (midpoint[1] - top).abs() > 0.15 {
            continue;
        }
        selected += 1;
        picked.push(fi);
        for p in source {
            for k in 0..3 {
                lo[k] = lo[k].min(p[k]);
                hi[k] = hi[k].max(p[k]);
            }
        }
    }
    let paint = paint_of(r, index);
    for fi in picked {
        set_paint(&mut paint[fi], "paint_seam", "4");
    }
    if !r.plate.model_metadata.iter().any(|(k, _)| k == "BambuStudio:SeamPaintingVersion") {
        r.plate.model_metadata.push(("BambuStudio:SeamPaintingVersion".into(), "0".into()));
    }
    let mut record = target.as_object().cloned().unwrap_or_default();
    record.insert("enforced_triangles".into(), json!(selected));
    record.insert("painted_facet_bounds_cad_mm".into(), json!([lo, hi]));
    record.insert("mesh_vertices_and_triangle_indices_unchanged".into(), json!(true));
    Ok(Value::Object(record))
}

/// One part of a proving project, carried into a part of this plate: its mesh shifted from its
/// source object's frame into the target's, its settings and its facets' paint.
struct Carried {
    name: String,
    subtype: String,
    vertices: Vec<[f64; 3]>,
    faces: Vec<[usize; 3]>,
    paint: Vec<Paint>,
    settings: Vec<(String, String)>,
    source_member: String,
    source_member_sha256: String,
}

fn carry(source: &BTreeMap<String, Vec<u8>>, origin_object: &str, component: i64, shift: [f64; 3]) -> Result<Carried> {
    let model = xml::parse(std::str::from_utf8(&source["3D/3dmodel.model"])?)?;
    let resources = model.child("resources").context("no resources")?;
    let owner = resources.children_named("object").find(|o| o.attribute("id") == Some(origin_object)).context("no source object")?;
    let id = component.to_string();
    let entry = owner.child("components").into_iter().flat_map(|c| c.children_named("component")).find(|c| c.attribute("objectid") == Some(&id))
        .with_context(|| format!("no source component {id}"))?;
    let member = entry.attribute("p:path").context("component path")?.trim_start_matches('/').to_string();
    let raw = source.get(&member).with_context(|| format!("no member {member}"))?;
    let doc = xml::parse(std::str::from_utf8(raw)?)?;
    let mesh = doc.descendants().into_iter().find(|e| e.local() == "mesh").context("no mesh")?;
    let vertices: Vec<[f64; 3]> = mesh.child("vertices").into_iter().flat_map(|v| v.children_named("vertex"))
        .map(|v| [0, 1, 2].map(|k| v.attribute(["x", "y", "z"][k]).and_then(|s| s.parse::<f64>().ok()).unwrap_or(0.0) + shift[k])).collect();
    let mut faces = Vec::new();
    let mut paint = Vec::new();
    for t in mesh.child("triangles").into_iter().flat_map(|t| t.children_named("triangle")) {
        faces.push([0, 1, 2].map(|k| t.attribute(["v1", "v2", "v3"][k]).and_then(|s| s.parse::<usize>().ok()).unwrap_or(0)));
        paint.push(t.attributes.iter().filter(|(k, _)| k.starts_with("paint_")).cloned().collect());
    }
    let config = xml::parse(std::str::from_utf8(&source["Metadata/model_settings.config"])?)?;
    let object = config.children_named("object").find(|o| o.attribute("id") == Some(origin_object)).context("no source object settings")?;
    let part = object.children_named("part").find(|p| p.attribute("id") == Some(&id)).with_context(|| format!("no source part {id}"))?;
    let settings: Vec<(String, String)> = part.children_named("metadata")
        .filter_map(|m| Some((m.attribute("key")?.to_string(), m.attribute("value")?.to_string())))
        .filter(|(k, _)| k != "name" && k != "matrix").collect();
    Ok(Carried { name: String::new(), subtype: part.attribute("subtype").unwrap_or("normal_part").to_string(), vertices, faces, paint, settings,
                 source_member: member, source_member_sha256: sha256_hex(raw) })
}

fn add_carried(r: &mut Refreshed, index: usize, carried: Carried) -> usize {
    let id = r.plate.add_part(index, &carried.name, carried.vertices, carried.faces, &carried.subtype, carried.settings, None);
    if carried.paint.iter().any(|p| !p.is_empty()) {
        if let Some(part) = r.plate.objects[index].parts.last_mut() {
            part.paint = Some(carried.paint);
        }
    }
    id
}

fn origin_shift(root: &Path, r: &Refreshed, selected: &Value) -> Result<(Value, Value, [f64; 3], usize)> {
    let preparation = read_json(&root.join(selected["source_preparation"].as_str().context("source preparation")?))?;
    let origin = preparation["parts"][0].clone();
    let target = r.row(selected["part"].as_str().context("part")?)?;
    let c = [0, 1, 2].map(|k| origin["source_center_mm"][k].as_f64().unwrap_or(0.0));
    Ok((preparation, origin, [c[0] - target.center[0], c[1] - target.center[1], c[2] - target.center[2]], target.index))
}

/// The accepted curved rim walls and their narrow blocker strips, on the base only.
pub fn add_selected_base_rim(root: &Path, r: &mut Refreshed, selected: &Value) -> Result<Value> {
    let source_path = root.join(selected["source_project"].as_str().context("source project")?);
    let source = members(&source_path)?;
    let (preparation, origin, shift, index) = origin_shift(root, r, selected)?;
    let origin_object = origin["object_id"].as_str().map(String::from).unwrap_or_else(|| origin["object_id"].to_string());
    let mut transferred = Vec::new();
    for arc in preparation["rim_arcs"].as_array().into_iter().flatten() {
        for (key, kind) in [("component_id", "arc"), ("blocker_component_id", "contact-blocker")] {
            let original = arc[key].as_i64().context("rim component")?;
            let mut carried = carry(&source, &origin_object, original, shift)?;
            carried.name = format!("base-rim-{kind}-{original}");
            let (member, sha, subtype) = (carried.source_member.clone(), carried.source_member_sha256.clone(), carried.subtype.clone());
            let id = add_carried(r, index, carried);
            transferred.push(json!({"kind": kind, "source_component_id": original, "component_id": id, "source_member": member,
                                    "source_member_sha256": sha, "subtype": subtype}));
        }
    }
    Ok(json!({"part": selected["part"], "source_project": selected["source_project"], "source_project_sha256": file_sha(&source_path)?,
              "source_preparation": selected["source_preparation"], "physical_result": selected["physical_result"],
              "source_local_to_target_local_translation_mm": shift, "arc_count": preparation["rim_arcs"].as_array().map_or(0, Vec::len),
              "components": transferred,
              "scope": "Exact accepted curved rim walls and their narrow blocker strips on the base only. Tree(auto)/Default remains elsewhere. The part meshes, poses, seams and layer bands are retained."}))
}

/// Place the common interface and bridge-only recess masks on the full base's CAD seat.
pub fn add_common_base_rim(root: &Path, r: &mut Refreshed, selected: &Value) -> Result<Value> {
    let target = r.row(selected["part"].as_str().context("rim part")?)?;
    ensure!(selected["base_stl_sha256"].as_str() == Some(&target.stl_sha256), "the rim aids require the bound production base");
    let index = target.index;
    let rotation = r.plate.objects[index].rotation;
    let translation = r.plate.objects[index].translation;
    let seat = crate::apply(&rotation, target.center.map(|value| -value));
    let seat = [0, 1, 2].map(|axis| seat[axis] + translation[axis]);
    let normal = crate::apply(&rotation, [0., 0., -1.]);

    let retained = recorded_member(root, selected, "source_archive")?;
    ensure!(selected["source_archive_sha256"].as_str() == Some(&sha256_hex(&retained)), "the rim evidence archive digest differs");
    let source = archive_members(Cursor::new(retained))?;
    let geometry: Value = serde_json::from_slice(&recorded_member(root, selected, "geometry_review")?)?;
    let cavities: Value = serde_json::from_slice(&recorded_member(root, selected, "cavities")?)?;
    let mapping: Value = serde_json::from_slice(&recorded_member(root, selected, "mapping")?)?;
    let trial_normal: [f64; 3] = serde_json::from_value(mapping["plane_normal"].clone())?;
    ensure!((0..3).all(|axis| (trial_normal[axis] - normal[axis]).abs() < 1e-5), "the full base and retained rim have different orientations");
    let axes: [[f64; 3]; 3] = serde_json::from_value(cavities["frame"].clone())?;
    let [u, v]: [f64; 2] = serde_json::from_value(cavities["outer_rim"]["center"].clone())?;
    let depth = cavities["seat_offset"].as_f64().context("trial seat offset")?;
    let trial_seat = [0, 1, 2].map(|axis| u * axes[0][axis] + v * axes[1][axis] + depth * axes[2][axis]);
    let shift = sub(seat, trial_seat);
    ensure!(shift[2].abs() < 1e-5, "the rim fins would move off the first bed plane");

    let model = xml::parse(std::str::from_utf8(&source["3D/3dmodel.model"])?)?;
    let item = model.child("build").and_then(|build| build.child("item")).context("rim evidence build item")?;
    let transform: Vec<f64> = item.attribute("transform").context("rim evidence transform")?
        .split_whitespace().map(str::parse).collect::<std::result::Result<_, _>>()?;
    let transform: [f64; 12] = transform.try_into().map_err(|_| anyhow::anyhow!("invalid rim evidence transform"))?;
    let trial_rotation = mat(&transform);
    let trial_translation = [transform[9], transform[10], transform[11]];
    let owner = item.attribute("objectid").context("rim evidence object")?;
    let inverse = [0, 1, 2].map(|axis| [0, 1, 2].map(|other| rotation[other][axis]));
    let components = geometry["components"].as_array().context("rim evidence components")?;
    let reference = components.first().context("rim evidence reference model")?;
    let keep_fins = selected["segmented_fins"].as_bool().unwrap_or(true);
    let mut transferred = Vec::new();
    for record in &components[1..] {
        if !keep_fins && record["subtype"].as_str() == Some("normal_part") {
            continue;
        }
        let original = record["id"].as_i64().context("rim component ID")?;
        let mut aid = carry(&source, owner, original, [0.; 3])?;
        ensure!(record["subtype"].as_str() == Some(&aid.subtype), "rim component type differs from its geometry review");
        aid.name = record["name"].as_str().context("rim component name")?.into();
        for vertex in &mut aid.vertices {
            let source = crate::apply(&trial_rotation, *vertex);
            let target = [0, 1, 2].map(|axis| source[axis] + trial_translation[axis] + shift[axis] - translation[axis]);
            *vertex = crate::apply(&inverse, target);
        }
        let reading = json!({"name": aid.name, "subtype": aid.subtype, "source_member_sha256": aid.source_member_sha256});
        let id = add_carried(r, index, aid);
        transferred.push(json!({"component_id": id, "source_component_id": original, "geometry": reading}));
    }
    let config = xml::parse(std::str::from_utf8(&source["Metadata/model_settings.config"])?)?;
    let trial = config.children_named("object").find(|object| object.attribute("id") == Some(owner)).context("rim evidence settings")?;
    let settings = ["support_style", "support_type", "support_object_xy_distance", "support_on_build_plate_only",
        "tree_support_branch_angle", "support_bottom_z_distance", "support_top_z_distance", "support_interface_top_layers", "support_interface_spacing"];
    let applied: Map<String, Value> = trial.children_named("metadata").filter_map(|setting| {
        let key = setting.attribute("key")?;
        let value = setting.attribute("value")?;
        settings.contains(&key).then(|| (key.to_string(), json!(value)))
    }).collect();
    ensure!(applied.len() == settings.len(), "the rim evidence is missing a support setting");
    let object = &mut r.plate.objects[index];
    object.settings.retain(|(key, _)| !applied.contains_key(key));
    object.settings.extend(applied.iter().map(|(key, value)| (key.clone(), text(value))));

    let trial_bounds: [[f64; 3]; 2] = serde_json::from_value(reference["bounds_mm"].clone())?;
    let margin = selected["mapping_margin_mm"].as_f64().context("rim mapping margin")?;
    let bounds = [[trial_bounds[0][0] + shift[0] - margin, trial_bounds[0][1] + shift[1] - margin],
                  [trial_bounds[1][0] + shift[0] + margin, trial_bounds[1][1] + shift[1] + margin]];
    let pockets = cavities["pockets"].as_array().context("rim evidence recesses")?.iter().map(|pocket| {
        let [u, v]: [f64; 2] = serde_json::from_value(pocket["center"].clone())?;
        let mouth = [0, 1, 2].map(|axis| u * axes[0][axis] + v * axes[1][axis] + depth * axes[2][axis] + shift[axis]);
        Ok(json!({"mouth_plate_mm": mouth, "mouth_radius_mm": pocket["mouth_radius_mm"],
            "pilot_radius_mm": pocket["pilot_radius_mm"], "shoulder_depth_mm": pocket["shoulder_depth_mm"],
            "blind_roof_depth_mm": pocket["blind_roof_depth_mm"], "blocker_radius_mm": pocket["blocker_radius_mm"],
            "blocker_depth_mm": pocket["blocker_depth_mm"]}))
    }).collect::<Result<Vec<_>>>()?;
    let mut parameters = mapping["parameters"].clone();
    if let Some(entries) = parameters.as_object_mut() {
        entries.remove("purpose");
    }
    Ok(json!({"part": selected["part"], "source_archive": selected["source_archive"],
        "source_commit": selected["source_commit"], "source_archive_sha256": selected["source_archive_sha256"],
        "source_to_production_plate_translation_mm": shift, "components": transferred, "segmented_fins": keep_fins,
        "rim_seat_plate_mm": seat, "rim_radius_mm": cavities["outer_rim"]["radius"],
        "support_settings": applied, "recesses": pockets,
        "band": {"parameters": parameters, "plane_normal": normal, "seat_plate_mm": seat,
                 "bounds_mm": bounds, "edge_blend_mm": selected["mapping_edge_blend_mm"]}}))
}

/// Carry the accepted removable tip anchor beneath the hidden plug end.
pub fn add_tip_root_anchor(root: &Path, r: &mut Refreshed, selected: &Value) -> Result<Value> {
    let source_path = root.join(selected["source_project"].as_str().context("source project")?);
    let source = members(&source_path)?;
    let (_, origin, shift, index) = origin_shift(root, r, selected)?;
    let origin_object = origin["object_id"].as_str().map(String::from).unwrap_or_else(|| origin["object_id"].to_string());
    let old = selected["root_anchor_component_id"].as_i64().context("tip root anchor component")?;
    let mut carried = carry(&source, &origin_object, old, shift)?;
    carried.name = "tip-hidden-root-disc".into();
    let (member, sha) = (carried.source_member.clone(), carried.source_member_sha256.clone());
    let id = add_carried(r, index, carried);
    let anchor = json!({"source_component_id": old, "component_id": id, "source_member": member, "source_member_sha256": sha});
    Ok(json!({"part": selected["part"], "source_project": selected["source_project"], "source_project_sha256": file_sha(&source_path)?,
              "source_preparation": selected["source_preparation"], "physical_result": selected["physical_result"], "components": [anchor],
              "source_local_to_target_local_translation_mm": shift, "joint_plane": selected["joint_plane"],
              "root_contact_scope": selected["root_contact_scope"]}))
}

