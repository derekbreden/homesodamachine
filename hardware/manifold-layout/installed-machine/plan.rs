//! The installed machine's plan: every placement run in this process, the equipment and its
//! routes merged in, and the metadata the facts and the scene views read.
use crate::design;
use anyhow::{Context, Result};
use serde_json::{Map, Value, json};
use std::collections::BTreeSet;
use std::path::Path;

/// One run of the placement program on `request`, in `dir`, with each raw reference model given
/// the drawing its frozen manifest keeps.
pub fn place(request: &Value, dir: &Path) -> Result<Value> {
    std::fs::create_dir_all(dir)?;
    let dir = std::path::absolute(dir)?;
    let mut plan = crate::layout::run(request, &dir.join("machine-layout.json"))?;
    bind_presentations(&mut plan)?;
    Ok(plan)
}

/// Adds, for each instance read from a frozen reference's own fine model, the frozen drawing
/// its manifest names, once.
pub fn bind_presentations(plan: &mut Value) -> Result<()> {
    let mut skins = plan["presentation"].as_array().cloned().unwrap_or_default();
    let mut seen: BTreeSet<String> = skins.iter().map(canonical).collect();
    for row in plan["instances"].as_array().into_iter().flatten() {
        let Some(model) = row["model"].as_str().map(Path::new) else { continue };
        let manifest = model.parent().context("a model's directory")?.join("frozen-asset.json");
        if !manifest.is_file() {
            continue;
        }
        let manifest = design::read(&manifest)?;
        let file = model.file_name().map(|n| n.to_string_lossy().into_owned());
        if manifest["fine_model"]["path"].as_str() != file.as_deref() {
            continue;
        }
        let payload = manifest["fine_payload"]["path"].as_str().context("a frozen drawing's path")?;
        let skin = json!({"payload": model.parent().unwrap().join(payload), "indices": row.get("indices"),
            "transform": row["transform"], "targets": [row["name"]]});
        if seen.insert(canonical(&skin)) {
            skins.push(skin);
        }
    }
    plan["presentation"] = Value::Array(skins);
    Ok(())
}

/// A value as text with its keys sorted, so two equal skins compare equal.
fn canonical(value: &Value) -> String {
    fn sorted(value: &Value) -> Value {
        match value {
            Value::Object(map) => {
                let mut keys: Vec<_> = map.keys().collect();
                keys.sort();
                Value::Object(keys.into_iter().map(|k| (k.clone(), sorted(&map[k]))).collect())
            }
            Value::Array(rows) => Value::Array(rows.iter().map(sorted).collect()),
            other => other.clone(),
        }
    }
    sorted(value).to_string()
}

/// The equipment the complete placement takes: the equipment program's plan with the routed
/// tubes added, the route lengths written back, the frames and ports it places, the junctions,
/// and the metadata the plan carries.
pub fn equipment_block(
    equipment_request: &Value,
    equipment: Value,
    routes: &Value,
    junctions: Vec<Value>,
    metadata: Value,
) -> Result<Value> {
    let mut equipment = equipment;
    let mut instances = equipment["instances"].as_array().cloned().unwrap_or_default();
    instances.extend(routes["instances"].as_array().cloned().unwrap_or_default());
    equipment["instances"] = Value::Array(instances);
    equipment["route_specs"] = equipment_request["routes"].clone();
    equipment["metadata"] = metadata;
    equipment["core_equipment"] = equipment_request["core_equipment"].clone();
    equipment["component_order"] = equipment_request["component_order"].clone();
    let mut frames = Map::new();
    for (name, row) in equipment_request["frames"].as_object().context("equipment frames")? {
        let mut ports = Map::new();
        for (port, at) in equipment_request["world_ports"][name].as_object().into_iter().flatten() {
            ports.insert(port.clone(), json!({"pos": at[0], "axis": at[1], "diam": at[2]}));
        }
        frames.insert(name.clone(), json!({"transform": row["transform"], "ports": ports}));
    }
    equipment["frames"] = Value::Object(frames);
    equipment["junctions"] = Value::Array(junctions);
    Ok(equipment)
}

/// Writes each tube's length, as the routing measured it, into the equipment's routes.
pub fn write_route_lengths(equipment_request: &mut Value, routes: &Value) {
    let lengths = routes.get("lengths").or_else(|| routes.get("route_lengths")).cloned().unwrap_or(json!({}));
    for (name, length) in lengths.as_object().into_iter().flatten() {
        if let Some(route) = equipment_request["routes"].get_mut(name) {
            route["length_mm"] = length.clone();
        }
    }
}

/// The equipment program's plan, read from `dir`, its bodies named by the model it wrote there.
pub fn equipment_plan(dir: &Path, name: &str) -> Result<Value> {
    let mut plan = design::read(dir.join(format!("{name}.json")))?;
    let model = json!(std::path::absolute(dir.join(format!("{name}.step.npz")))?);
    for instance in plan["instances"].as_array_mut().into_iter().flatten() {
        instance["model"] = model.clone();
    }
    plan["model"] = model;
    Ok(plan)
}

/// One wiring connector where the piece that holds it cuts its well: its name, catalog size,
/// host, and rotation rows and translation in the machine's frame.
struct Junction {
    name: String,
    size: String,
    host: String,
    rotation: Value,
    translation: Value,
}

/// The wiring's connectors: the top pieces' from the enclosure's junction table, the cold core's
/// from the wells its foam cap publishes, in the wiring's placement order.
fn junction_poses(root: &Path) -> Result<Vec<Junction>> {
    use hsm_enclosure_numbers::{junctions::junctions, quadrant::Y};
    let top = |host: Y, owner: &'static str| {
        junctions().iter().filter(move |j| j.host == host).map(move |j| Junction {
            name: j.name.clone(), size: j.wago.size.into(), host: owner.into(),
            rotation: json!(j.rotation), translation: json!(j.translation),
        })
    };
    let mut rows: Vec<Junction> = top(Y::Back, "back-top").collect();
    let cap = design::read(root.join("hardware/printed-parts/cold-core/foam-cap/foam-cap.numbers.json"))?;
    for well in cap["wells"].as_array().context("the foam cap's wells")? {
        let pose = &well["pose"];
        let text = |v: &Value, what: &str| v.as_str().map(str::to_owned).with_context(|| format!("a well's {what}"));
        rows.push(Junction {
            name: text(&well["name"], "name")?, size: text(&pose["size"], "connector size")?,
            host: text(&pose["parent"], "host")?, rotation: pose["rotation"].clone(),
            translation: pose["translation_mm"].clone(),
        });
    }
    rows.extend(top(Y::Front, "front-top"));
    Ok(rows)
}

/// The wiring's connectors as placed bodies: each connector's reference model at its pose.
pub fn junctions(root: &Path) -> Result<Vec<Value>> {
    junction_poses(root)?
        .into_iter()
        .map(|j| {
            let relative = format!("reference/wago-221/wago-221-{}.step", j.size);
            let transform: Vec<Value> = (0..3)
                .map(|i| json!([j.rotation[i][0], j.rotation[i][1], j.rotation[i][2], j.translation[i]]))
                .collect();
            Ok(json!({"model": design::source(root, &relative, design::Use::Layout)?,
                      "name": j.name, "owner": j.host, "transform": transform}))
        })
        .collect()
}

/// The wiring's connectors as the wiring reads them, by name: size, host and pose.
pub fn wiring_placements(root: &Path) -> Result<Value> {
    Ok(Value::Object(
        junction_poses(root)?
            .into_iter()
            .map(|j| (j.name, json!({"parent": j.host, "rotation": j.rotation, "size": j.size, "translation_mm": j.translation})))
            .collect(),
    ))
}

/// The route lengths of the routes whose length the routing measured.
pub fn route_lengths(routes: &Value) -> Value {
    Value::Object(
        routes
            .as_object()
            .into_iter()
            .flatten()
            .filter_map(|(name, row)| row.get("length_mm").map(|l| (name.clone(), l.clone())))
            .collect(),
    )
}

/// The metadata the equipment hands the complete placement, which carries it into the plan:
/// the runs as drawn, the routes and their lengths, the ports, the connections the routes make,
/// the connectors and mounts, and the names and holders the facts and the scene views sort
/// bodies by.
pub fn placement_metadata(root: &Path, equipment_request: &Value, runs: Vec<Value>) -> Result<Value> {
    let above = design::read(root.join("hardware/manifold-layout/above-core.json"))?;
    let routes = &equipment_request["routes"];
    let keystone = &above["rear_wall"]["dry_openings"]["keystone"]["face_center_mm"];
    let core = design::read_document(&root.join("hardware/cold-core-layout/cold-core-assembly.scene.npz"))?;
    let core_equipment = hsm_layout_data::request(json!({"op": "equipment-names"}))?;
    let cap = design::read(root.join("hardware/printed-parts/cold-core/foam-cap/foam-cap.numbers.json"))?;
    let casing = design::read(root.join("hardware/printed-parts/cold-core/foam-assembly/foam-assembly.numbers.json"))?;
    let probes: Vec<Value> = casing["report"]["probes"].as_array().context("the casing's probes")?
        .iter().map(|probe| probe["name"].clone()).collect();
    let holders = design::read(root.join("hardware/manifold-layout/manifold-tube-holders.json"))?;
    Ok(json!({
        "runs": runs,
        "native_route_specs": routes,
        "native_route_order": equipment_request["route_order"],
        "route_lengths": route_lengths(routes),
        "world_ports": equipment_request["world_ports"],
        "native_connections": above["logical_connections"],
        "selected_fitting_names": equipment_request["component_order"],
        "fluid_grid_assignment": above["fluid_grid"]["assignment"],
        "soft_neighbors": equipment_request["insulation"].get("neighbors").cloned().unwrap_or(json!([])),
        "keystone_station": [keystone[0], keystone[2]],
        "keystone_clearances": [],
        "core_equipment_names": core_equipment,
        "core_alpha_by_name": core.get("alpha_by_name").cloned().unwrap_or(json!({})),
        "wiring_placements": wiring_placements(root)?,
        "wall_mount_datums": wall_mounts(equipment_request)?,
        "union_supports": cap["union_supports"],
        "cap_conduits": probes,
        "manifold_tube_holders": holders["holders"],
    }))
}

/// The piece the above-core layout hangs its wall-mounted parts from.
const WALL_HOST: &str = "enclosure-back-top";

/// The parts the above-core layout hangs from the back top's wall, each with the stations its
/// screws thread into, from the mount hardware the equipment places.
fn wall_mounts(equipment_request: &Value) -> Result<Value> {
    let mut mounts = Map::new();
    for item in equipment_request["items"].as_array().context("the equipment's items")? {
        if item["op"] != "mount-hardware" || item["kind"] != "screw" {
            continue;
        }
        let name = item["name"].as_str().context("a mount's screw name")?;
        let part = name.rsplit_once("-screw-").map(|(part, _)| part).context("a mount's screw is named for its part")?;
        let mount = mounts.entry(part.to_owned()).or_insert_with(|| json!({"parent": WALL_HOST, "stations": []}));
        mount["stations"].as_array_mut().context("a mount's stations")?.push(
            json!({"threaded": true, "position_world_mm": item["point"], "axis_world": item["axis"]}),
        );
    }
    Ok(Value::Object(mounts))
}

/// The complete placement's request: the pack's request, the installed parts, the pump dock as
/// placed, the pack as placed and the equipment.
pub fn complete_request(pack: &Value, installed: &Value, dock: Value, prepared: Value, equipment: Value) -> Result<Value> {
    let mut request = pack.clone();
    for (name, path) in installed["sources"].as_object().context("the installed sources")? {
        request["sources"][name] = path.clone();
    }
    request["piece_models"] = installed["piece_models"].clone();
    request["installed_datums"] = installed["datums"].clone();
    request["installed"] = installed["instances"].clone();
    request["dock"] = dock;
    request["prepared"] = prepared;
    request["equipment"] = equipment;
    request["stage"] = json!("installed");
    Ok(request)
}

/// The placed machine's metadata as the facts and the views read it: the pack's written-down
/// fields, the names of the pack's bodies, and the funnel's and seam's fasteners.
pub fn normal_metadata(mut plan: Value, request: &Value) -> Result<Value> {
    let metadata = plan["metadata"].as_object_mut().context("the plan's metadata")?;
    let written = design::plain(&request["box"]["box"]["pack"]);
    let pack = metadata.get_mut("pack").and_then(Value::as_object_mut).context("the plan's pack")?;
    for (field, value) in written.as_object().context("the written-down pack")? {
        if field != "placed" && pack.get(field) != Some(value) {
            pack.insert(field.clone(), value.clone());
        }
    }
    let mut placed: Vec<String> = pack["placed"].as_object().map(|m| m.keys().cloned().collect()).unwrap_or_default();
    placed.sort();
    metadata.insert("enclosure_pack_body_names".into(), json!(placed));
    let mut bodies: Vec<String> = request["manifold_numbers"]["bodies"]
        .as_array()
        .into_iter()
        .flatten()
        .filter_map(|row| row["name"].as_str())
        .filter(|name| !["tube-", "turn-", "step-", "stub-"].iter().any(|p| name.starts_with(p)))
        .map(str::to_owned)
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect();
    bodies.sort();
    metadata.insert("pack_body_names".into(), json!(bodies));
    if let Some(frames) = metadata.get_mut("frames").and_then(Value::as_object_mut) {
        frames.remove("__pack_base");
    }
    let installed = &request["installed_datums"];
    metadata.insert("funnel_fasteners".into(), installed.get("funnel_fasteners").cloned().unwrap_or(json!([])));
    metadata.insert("funnel_seal".into(), installed.get("funnel_seal").cloned().unwrap_or(Value::Null));
    let inserts: Vec<Value> = installed["y_seam"]
        .as_array()
        .into_iter()
        .flatten()
        .map(|row| {
            json!({"name": format!("{}-insert", row["name"].as_str().unwrap_or_default()),
                   "host": format!("enclosure-{}", row["owner"].as_str().unwrap_or_default()),
                   "x": row["x"], "y": row["y"], "z0": row["insert0"], "z1": row["insert1"]})
        })
        .collect();
    metadata.insert("y_seam_insert_datums".into(), json!(inserts));
    Ok(plan)
}

/// What the wiring takes beside the placed machine: the front top's cable passages from the
/// wiring's own routing files, the fuse's lead from its reference, and the viewer's payload rule.
pub fn wiring_context(root: &Path) -> Result<Value> {
    let fuse = design::read(root.join("hardware/reference/sf76e-thermal-fuse/reference-parameters.json"))?;
    Ok(json!({
        "fixed_passages": design::read(root.join("hardware/wiring/installed/fixed-passages.json"))?,
        "fuse_lead_diameter_mm": fuse["lead_diameter_mm"],
        "presentation_deflection_ratio": hsm_print_payload::LINEAR_DEFLECTION_RATIO,
        "presentation_angular_deflection_rad": hsm_print_payload::ANGULAR_DEFLECTION,
    }))
}

/// The wiring's bodies as the scene views name them: each conductor and terminal once, without
/// the index a split body's pieces carry.
pub fn wiring_names(wire_model: &Path) -> Result<Value> {
    let names: BTreeSet<String> = design::read_names(wire_model)?
        .into_iter()
        .map(|name| match name.rsplit_once('/') {
            Some((stem, tail)) if !tail.is_empty() && tail.bytes().all(|b| b.is_ascii_digit()) => stem.to_owned(),
            _ => name,
        })
        .collect();
    Ok(json!(names))
}

/// The plan as the export takes it: its bodies, drawings and metadata, named for the machine.
pub fn physical_spec(plan: &Value) -> Value {
    let mut spec = plan.clone();
    spec["op"] = json!("physical");
    spec
}
