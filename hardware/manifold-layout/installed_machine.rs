//! The installed machine: every body of the appliance where it goes, placed from the machine's
//! written-down design and its parts' own files, with shared website meshes, native construction
//! models, facts and scene views.
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::path::Path;

#[path = "installed-machine/cache.rs"]
mod cache;
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
#[path = "installed-machine/progress.rs"]
mod progress;
#[path = "installed-machine/routes_plan.rs"]
mod routes_plan;
#[path = "installed-machine/scenes.rs"]
mod scenes;
#[path = "installed-machine/wiring.rs"]
mod wiring;

#[path = "../../tools/hsm/shared-data/src/color.rs"]
mod color;
#[allow(dead_code)]
#[path = "../../tools/hsm/shared-data/src/common.rs"]
mod common;
#[path = "../../tools/hsm/machine-data/src/equipment.rs"]
mod equipment;
#[path = "../../tools/hsm/machine-data/src/equipment_ports.rs"]
mod equipment_ports;
#[path = "machine_equipment.rs"]
mod equipment_program;
#[allow(dead_code)]
#[path = "machine_layout.rs"]
mod layout;
#[path = "../../tools/hsm/machine-data/src/reporting.rs"]
mod reporting;
#[path = "machine_routes.rs"]
mod routes_program;
#[allow(dead_code)]
#[path = "../wiring/installed/wire_geometry.rs"]
mod wires_program;
use wires_program::wire_request;

/// Retained stages use the shared writable geometry cache across staged build directories.
const WORK: &str = ".cache/realized/installed-machine";

/// Writes `value` as JSON with its keys sorted, one space to a level.
fn write_json(path: &Path, value: &Value) -> Result<()> {
    let mut out = Vec::new();
    let mut writer = serde_json::Serializer::with_formatter(
        &mut out,
        serde_json::ser::PrettyFormatter::with_indent(b" "),
    );
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
            Value::Object(
                keys.into_iter()
                    .map(|k| (k.clone(), sorted(&map[k])))
                    .collect(),
            )
        }
        Value::Array(rows) => Value::Array(rows.iter().map(sorted).collect()),
        other => other.clone(),
    }
}

fn main() -> Result<()> {
    let mut placements_only = false;
    let mut destination = None;
    for argument in std::env::args().skip(1) {
        match argument.as_str() {
            "--placements-only" => placements_only = true,
            "--help" | "-h" => {
                println!(
                    "Usage: installed-machine [--placements-only] [OUTPUT]\nPlacement-only requests reuse retained prerequisites without constructing geometry."
                );
                return Ok(());
            }
            _ if !argument.starts_with('-') && destination.is_none() => {
                destination = Some(argument)
            }
            _ => anyhow::bail!("unknown installed-machine argument {argument:?}"),
        }
    }
    let root = std::path::absolute(".")?;
    let workspace = std::env::var_os("HSM_WORKSPACE")
        .map(std::path::PathBuf::from)
        .unwrap_or_else(|| root.clone());
    let work = workspace.join(WORK);
    let out = std::path::absolute(destination.unwrap_or_else(|| ".".into()))?;
    let _work_lock = if placements_only {
        match cache::try_lock(&work)? {
            Some(lock) => lock,
            None => {
                println!(
                    "{}",
                    json!({"stage":"placements","changed":false,"pending":"assembly work is busy"})
                );
                return Ok(());
            }
        }
    } else {
        cache::lock(&work)?
    };
    let mut cache = cache::Cache::new(&root, &work)?;
    if placements_only
        && cache
            .previous("presentation-state")
            .is_none_or(|previous| previous["implementation"] != cache.implementation())
    {
        println!(
            "{}",
            json!({"stage":"placements","changed":false,"pending":"retained placement baseline"})
        );
        return Ok(());
    }
    let shown = out.join("hardware/manifold-layout");
    std::fs::create_dir_all(&shown)?;
    let payload = shown.join("enclosure-assembly.step.mesh");
    let previous_scene = work.join("installed.step.mesh");

    // Where the pack sits.
    let pack = pack::pack_request(&root)?;
    let mut pack_recipe = pack.clone();
    pack_recipe["above_core"] = json!({"ceiling_pockets":pack["above_core"]["ceiling_pockets"],
        "rear_wall":{"interior_panel_relief":pack["above_core"]["rear_wall"]["interior_panel_relief"]}});
    let references = work.join("references");
    let files = [references.join("machine-layout.parts.npz")];
    let prepared = if placements_only {
        match cache.try_reuse("references", &pack_recipe, &files)? {
            Some(value) => value,
            None => {
                println!(
                    "{}",
                    json!({"stage":"placements","changed":false,"pending":"retained reference placement"})
                );
                return Ok(());
            }
        }
    } else {
        cache.run("references", &pack_recipe, &files, || {
            plan::place(&pack, &references)
        })?
    };

    // The equipment above the core, and the tubes that join it.
    let mut equipment_request = equipment_plan::equipment_request(&root, &prepared)?;
    let junctions = plan::junctions(&root)?;
    let placement_state = progress::state(&mut cache, &equipment_request, &junctions)?;
    let changed = progress::placements(
        &mut cache,
        &root,
        &placement_state,
        &previous_scene,
        &payload,
    )?;
    if placements_only {
        println!(
            "{}",
            json!({"stage":"placements","changed":changed,"complete":false,"pending":["mechanical geometry","wiring"]})
        );
        return Ok(());
    }
    let name = equipment_request.name.clone();
    let equipment_dir = work.join("equipment");
    std::fs::create_dir_all(&equipment_dir)?;
    let equipment_items = equipment_program::Request {
        name: name.clone(),
        items: equipment_request.items.clone(),
    };
    let equipment_model = equipment_dir.join(format!("{name}.step.npz"));
    let placed: equipment_program::Placed = serde_json::from_value(cache.run(
        "equipment",
        &serde_json::to_value(&equipment_items)?,
        &[equipment_model.clone()],
        || Ok(serde_json::to_value(equipment_program::run(&equipment_items, &equipment_dir)?)?),
    )?)
    .context("the retained equipment")?;
    let (mut copper, unsolved) = copper::runs(&root, &prepared)?;
    let routes_request =
        routes_plan::routes_request(&equipment_request, &equipment_model, &placed.groups, &copper)?;
    let routes_dir = work.join("routes");
    std::fs::create_dir_all(&routes_dir)?;
    let routes: routes_program::Routed = serde_json::from_value(cache.run(
        "routes",
        &serde_json::to_value(&routes_request)?,
        &[routes_dir.join(format!("{}.step.npz", routes_request.name))],
        || Ok(serde_json::to_value(routes_program::run(&routes_request, &routes_dir)?)?),
    )?)
    .context("the retained routes")?;
    routes_plan::leave_out(&mut equipment_request, &mut copper, unsolved, &routes);
    for tube in &equipment_request.unrouted {
        eprintln!("installed-machine: left out {}, {} to {}: {}", tube.name, tube.from, tube.to, tube.reason);
    }
    routes_plan::write_route_lengths(&mut equipment_request, &routes);
    let runs = routes_plan::run_records(&copper, &equipment_request)?;
    let metadata = plan::placement_metadata(&root, &equipment_request, runs)?;
    let equipment = plan::equipment_block(
        &equipment_request,
        &placed,
        &equipment_model,
        routes_plan::placed(&routes)?,
        junctions,
        metadata,
    )?;

    // Everything installed around the pack, the pump dock's fittings, and the whole machine placed.
    let installed = json!({
        "sources": installed::installed_sources(&root)?,
        "piece_models": installed::piece_models(&root)?,
        "datums": installed::installed_datums(&root)?,
        "instances": installed::installed_instances(&root)?,
    });
    let dock_request = pack::dock_request(&root)?;
    let dock_dir = work.join("dock");
    let dock = cache.run(
        "dock",
        &dock_request,
        &[dock_dir.join("machine-layout.parts.npz")],
        || plan::place(&dock_request, &dock_dir),
    )?;
    let complete = plan::complete_request(&pack, &installed, dock, prepared, equipment)?;
    let complete_dir = work.join("complete");
    let plan = cache.run(
        "placement",
        &complete,
        &[complete_dir.join("machine-layout.parts.npz")],
        || plan::normal_metadata(plan::place(&complete, &complete_dir)?, &complete),
    )?;

    // The machine's model and STEP, with its wiring in them.
    let mut plan = plan;
    let model_dir = work.join("mechanics");
    std::fs::create_dir_all(&model_dir)?;
    let fine = model_dir.join("enclosure-assembly.step.npz");
    let mechanical_mesh = model_dir.join("enclosure-assembly.step.mesh");
    let physical = plan::physical_spec(&plan);
    cache.run(
        "mechanical model",
        &physical,
        &[fine.clone(), mechanical_mesh.clone()],
        || hsm_model_export::model::physical(&physical, &model_dir),
    )?;
    progress::mechanics(&mechanical_mesh, &previous_scene, &payload)?;
    let wiring_dir = work.join("wiring");
    std::fs::create_dir_all(&wiring_dir)?;
    let wiring_request = wiring::wiring_request(&root, &plan, &fine, &mut cache)?;
    write_json(
        &wiring_dir.join("request.json"),
        &serde_json::to_value(&wiring_request)?,
    )?;
    wires_program::run(&wiring_request, &wiring_dir)?;
    progress::complete(
        &mechanical_mesh,
        &wiring_dir.join("enclosure-wiring.step.mesh"),
        &payload,
    )?;

    // The scene views, cut from the finished model.
    plan["metadata"]["wiring_names"] =
        plan::wiring_names(&wiring_dir.join("enclosure-wiring.step.npz"))?;
    let glb = out.join("hardware/assembly/scenes/glb");
    std::fs::create_dir_all(&glb)?;
    let views = scenes::views_spec(&root, &plan, &fine, &payload)?;
    hsm_model_export::gltf::write_views(&views, &glb)?;

    // The facts.
    let squeeze = pack["datums"]["floor_grommet_squeeze"]
        .as_f64()
        .context("the floor grommets' squeeze")?;
    write_json(
        &shown.join("enclosure-assembly.facts.json"),
        &facts::facts(&root, &plan, squeeze)?,
    )?;
    progress::remember(&mut cache, placement_state, &payload, &previous_scene)?;
    Ok(())
}
