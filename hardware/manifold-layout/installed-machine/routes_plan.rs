//! The request the routes program sweeps from, and the run records the plan's metadata carries:
//! the copper runs first, then every warm-side tube the equipment request routes.
use crate::copper;
use crate::equipment::Equipment;
use crate::routes_program::{Bodies, Insulation, Pose, Request, Sweep};
use anyhow::{Context, Result};
use hsm_layout_data::tube::Segment;
use serde::Deserialize;
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::path::Path;

/// The program's name for its request and the files it writes.
const NAME: &str = "machine-routes";

/// The body the soda inlet's tube bends through, which its foam sleeve is cut around.
const HOLDER: &str = "soda-bend-holder";

/// What the routes program sweeps of one tube the equipment request routes.
#[derive(Deserialize)]
struct Routed {
    segments: Vec<Segment>,
    od_mm: f64,
    id_mm: f64,
    color: Option<[f64; 3]>,
}

/// What the routes program reads of the equipment request's soda insulation.
#[derive(Deserialize)]
struct Sleeve {
    plan: SleevePlan,
    neighbors: Vec<String>,
    valve_pose: Pose,
    color: Option<[f64; 3]>,
}

/// The foam and the tube it covers, as the soda inlet's plan gives them.
#[derive(Deserialize)]
struct SleevePlan {
    foam_segments: Vec<Segment>,
    nominal_foam_od_mm: f64,
    nominal_foam_id_mm: f64,
    tube_segments: Vec<Segment>,
    tube_od_mm: f64,
    tube_id_mm: f64,
}

/// The routes program's request: the copper runs, the equipment request's tubes, and the soda foam.
///
/// A tube the equipment request routes under a copper run's name takes that run's place. The
/// foam is cut around bodies of the model the equipment stage wrote (`equipment_model`), found
/// by the `groups` it placed them in.
pub fn routes_request(
    equipment_request: &Equipment,
    equipment_model: &Path,
    groups: &BTreeMap<String, Vec<usize>>,
    copper: &[copper::Run],
) -> Result<Request> {
    let mut tubes = vec![];
    for run in copper {
        tubes.push(run.sweep()?);
    }
    for key in &equipment_request.route_order {
        let route = equipment_request.routes.get(key).with_context(|| format!("no route {key}"))?;
        let Routed { segments, od_mm, id_mm, color } =
            Routed::deserialize(route).with_context(|| format!("the route {key}"))?;
        let tube = Sweep { name: key.to_owned(), segments, od_mm, id_mm, color };
        match tubes.iter_mut().find(|held| &held.name == key) {
            Some(held) => *held = tube,
            None => tubes.push(tube),
        }
    }
    let mut insulation = None;
    let mut components = BTreeMap::new();
    if !equipment_request.insulation.is_null() {
        let sleeve = Sleeve::deserialize(&equipment_request.insulation).context("the soda insulation")?;
        for name in std::iter::once(HOLDER).chain(sleeve.neighbors.iter().map(String::as_str)) {
            let indices = groups.get(name).with_context(|| format!("the equipment model holds no {name}"))?;
            components.insert(name.to_owned(), Bodies { model: equipment_model.to_owned(), indices: indices.clone() });
        }
        insulation = Some(Insulation {
            foam_segments: sleeve.plan.foam_segments,
            foam_od_mm: sleeve.plan.nominal_foam_od_mm,
            foam_id_mm: sleeve.plan.nominal_foam_id_mm,
            tube_segments: sleeve.plan.tube_segments,
            tube_od_mm: sleeve.plan.tube_od_mm,
            tube_id_mm: sleeve.plan.tube_id_mm,
            valve_pose: sleeve.valve_pose,
            neighbors: sleeve.neighbors,
            color: sleeve.color,
        });
    }
    Ok(Request { name: NAME.to_owned(), tubes, insulation, components })
}

/// Writes each tube's length, as the routing measured it, into the equipment request's routes.
pub fn write_route_lengths(equipment_request: &mut Equipment, routes: &crate::routes_program::Routed) {
    for (name, length) in &routes.lengths {
        if let Some(route) = equipment_request.routes.get_mut(name) {
            route["length_mm"] = json!(length);
        }
    }
}

/// The swept bodies as the placement plan lists a placed body.
pub fn placed(routes: &crate::routes_program::Routed) -> Result<Vec<Value>> {
    routes.instances.iter().map(|instance| Ok(serde_json::to_value(instance)?)).collect()
}

/// The length of a centreline drawn through `points`.
fn polyline_length(points: &[Value]) -> Result<f64> {
    let mut total = 0.;
    for pair in points.windows(2) {
        let mut square = 0.;
        for axis in 0..3 {
            let coordinate = |point: &Value| point[axis].as_f64().context("a route point");
            let delta = coordinate(&pair[1])? - coordinate(&pair[0])?;
            square += delta * delta;
        }
        total += square.sqrt();
    }
    Ok(total)
}

/// One authored tube as the plan's metadata records it.
fn route_record(name: &str, route: &Value) -> Result<Option<Value>> {
    let Some(points) = route.get("points_mm").or_else(|| route.get("centerline_mm")) else {
        return Ok(None);
    };
    let owners = route["owners"].as_array();
    let owner = |end: Option<&Value>| end.cloned().unwrap_or(json!(""));
    let from = route.get("frm").or_else(|| route.get("from")).cloned();
    let from = from.unwrap_or_else(|| owner(owners.and_then(|o| o.first())));
    let to = route.get("to").cloned().unwrap_or_else(|| owner(owners.and_then(|o| o.last())));
    let rows = points.as_array().with_context(|| format!("route {name}'s points"))?;
    let bend = route["minimum_radius_mm"].as_f64().unwrap_or(0.);
    let note = route.get("basis").cloned().unwrap_or(json!(""));
    Ok(Some(json!({"id": name, "kind": "fluid", "frm": from, "to": to, "pts": points, "diam": route["od_mm"],
        "bend": bend, "note": note, "min_bend": null, "bends": [], "radii": {}, "caps": {},
        "length": polyline_length(rows)?})))
}

/// The run records the plan's metadata carries: the copper runs, then the equipment request's tubes.
pub fn run_records(copper: &[copper::Run], equipment_request: &Equipment) -> Result<Vec<Value>> {
    let mut records: Vec<Value> = copper.iter().map(copper::Run::record).collect();
    for name in &equipment_request.route_order {
        let route = equipment_request.routes.get(name).with_context(|| format!("no route {name}"))?;
        records.extend(route_record(name, route)?);
    }
    Ok(records)
}
