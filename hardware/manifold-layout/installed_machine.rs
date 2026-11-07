//! The installed machine: every body of the appliance where it goes, placed from the machine's
//! written-down design and its parts' own files, and written as the STEP and the model the
//! website shows, its facts and its scene views.
use anyhow::{Context, Result};
use hsm_kernel::part::Numbers;
use serde_json::{Value, json};
use std::path::Path;

#[path = "installed-machine/copper.rs"]
mod copper;
#[path = "installed-machine/design.rs"]
mod design;
#[path = "installed-machine/equipment_plan.rs"]
mod equipment_plan;
#[path = "installed-machine/facts.rs"]
mod facts;
#[path = "installed-machine/installed.rs"]
mod installed;
#[path = "installed-machine/pack.rs"]
mod pack;
#[path = "installed-machine/plan.rs"]
mod plan;
#[path = "installed-machine/routes_plan.rs"]
mod routes_plan;
#[path = "installed-machine/scenes.rs"]
mod scenes;
#[path = "installed-machine/wiring.rs"]
mod wiring;

#[allow(dead_code)]
#[path = "machine_layout.rs"]
mod layout;
#[allow(dead_code)]
#[path = "machine_equipment.rs"]
mod equipment_program;
#[allow(dead_code)]
#[path = "machine_routes.rs"]
mod routes_program;
#[allow(dead_code)]
#[path = "../wiring/installed/wire_geometry.rs"]
mod wires_program;
#[allow(dead_code)]
#[path = "../../tools/hsm/machine-data/src/reporting.rs"]
mod reporting;
#[allow(dead_code)]
#[path = "../../tools/hsm/machine-data/src/equipment.rs"]
mod equipment;
#[allow(dead_code)]
#[path = "../../tools/hsm/machine-data/src/equipment_ports.rs"]
mod equipment_ports;
#[allow(dead_code)]
#[path = "../../tools/hsm/shared-data/src/common.rs"]
mod common;
#[allow(dead_code)]
#[path = "../../tools/hsm/shared-data/src/color.rs"]
mod color;

/// Where the program keeps the models it cuts on the way to the machine's own files, which it
/// writes under the directory it is given, or here.
const WORK: &str = "tmp/installed-machine";

/// Writes `value` as JSON with its keys sorted, one space to a level.
fn write_json(path: &Path, value: &Value) -> Result<()> {
    let mut out = Vec::new();
    let mut writer = serde_json::Serializer::with_formatter(&mut out, serde_json::ser::PrettyFormatter::with_indent(b" "));
    serde::Serialize::serialize(&sorted(value), &mut writer)?;
    out.push(b'\n');
    hsm_model_export::put(path, &out)
}

/// `value` with every object's keys in sorted order.
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

fn main() -> Result<()> {
    let root = std::path::absolute(".")?;
    let work = root.join(WORK);
    let out = std::path::absolute(std::env::args().nth(1).unwrap_or_else(|| ".".into()))?;

    // Where the pack sits.
    let pack = pack::pack_request(&root)?;
    let prepared = plan::place(&pack, &work.join("references"))?;

    // The equipment above the core, and the tubes that join it.
    let mut equipment_request = equipment_plan::equipment_request(&root, &prepared)?;
    let name = equipment_request["name"].as_str().unwrap_or("machine-equipment").to_owned();
    let equipment_dir = work.join("equipment");
    std::fs::create_dir_all(&equipment_dir)?;
    equipment_program::run(&Numbers::from_value(equipment_request.clone()), &equipment_dir)?;
    let equipment = plan::equipment_plan(&equipment_dir, &name)?;
    let copper = copper::runs(&root, &prepared)?;
    let routes_request = routes_plan::routes_request(&equipment_request, &equipment_dir, &equipment, &copper)?;
    let routes_dir = work.join("routes");
    std::fs::create_dir_all(&routes_dir)?;
    let routes = routes_program::run(&Numbers::from_value(routes_request), &routes_dir)?;
    plan::write_route_lengths(&mut equipment_request, &routes);
    let runs = routes_plan::run_records(&copper, &equipment_request)?;
    let metadata = plan::placement_metadata(&root, &equipment_request, runs)?;
    let junctions = plan::junctions(&root)?;
    let equipment = plan::equipment_block(&equipment_request, equipment, &routes, junctions, metadata)?;

    // Everything installed around the pack, the pump dock's fittings, and the whole machine placed.
    let installed = json!({
        "sources": installed::installed_sources(&root)?,
        "piece_models": installed::piece_models(&root)?,
        "datums": installed::installed_datums(&root)?,
        "instances": installed::installed_instances(&root)?,
    });
    let dock = plan::place(&pack::dock_request(&root)?, &work.join("dock"))?;
    let complete = plan::complete_request(&pack, &installed, dock, prepared, equipment)?;
    let plan = plan::normal_metadata(plan::place(&complete, &work.join("complete"))?, &complete)?;

    // The machine's model and STEP, with its wiring in them.
    let mut plan = plan;
    plan["metadata"]["wiring_context"] = plan::wiring_context(&root)?;
    let model_dir = work.join("model");
    std::fs::create_dir_all(&model_dir)?;
    hsm_model_export::model::physical(&plan::physical_spec(&plan), &model_dir)?;
    let fine = model_dir.join("enclosure-assembly.step.npz");
    let wiring_dir = work.join("wiring");
    std::fs::create_dir_all(&wiring_dir)?;
    let wiring_request = wiring::wiring_request(&root, &plan, &fine)?;
    wires_program::run(&Numbers::from_value(wiring_request), &wiring_dir)?;
    hsm_model_export::merge::append(
        &json!({"host_step": model_dir.join("enclosure-assembly.step"),
                "wire_step": wiring_dir.join("enclosure-wiring.step"),
                "wire_model": wiring_dir.join("enclosure-wiring.step.npz")}),
        &model_dir,
    )?;
    let shown = out.join("hardware/manifold-layout");
    std::fs::create_dir_all(&shown)?;
    for name in ["enclosure-assembly.step", "enclosure-assembly.step.mesh"] {
        publish(&model_dir.join(name), &shown.join(name))?;
    }

    // The scene views, cut from the finished model.
    plan["metadata"]["wiring_names"] = plan::wiring_names(&wiring_dir.join("enclosure-wiring.step.npz"))?;
    let glb = out.join("hardware/assembly/scenes/glb");
    std::fs::create_dir_all(&glb)?;
    let payload = shown.join("enclosure-assembly.step.mesh");
    let views = scenes::views_spec(&root, &plan, &fine, &payload)?;
    hsm_model_export::gltf::write_views(&views, &glb)?;

    // The facts.
    let squeeze = pack["datums"]["floor_grommet_squeeze"].as_f64().context("the floor grommets' squeeze")?;
    write_json(&shown.join("enclosure-assembly.facts.json"), &facts::facts(&root, &plan, squeeze)?)?;
    Ok(())
}

/// Moves a finished file to where it is published, copying it when the two are on different disks.
fn publish(from: &Path, to: &Path) -> Result<()> {
    if std::fs::rename(from, to).is_err() {
        std::fs::copy(from, to).with_context(|| format!("publishing {}", to.display()))?;
        std::fs::remove_file(from)?;
    }
    Ok(())
}
