//! The request the routes program sweeps from, and the run records the plan's metadata carries:
//! the copper runs first, then every warm-side tube the equipment request routes.
use crate::copper;
use anyhow::{Context, Result};
use serde_json::{Map, Value, json};
use std::path::{Path, PathBuf};

/// The program's name for its request and the files it writes.
const NAME: &str = "machine-routes";

/// The body the soda inlet's tube bends through, which its foam sleeve is cut around.
const HOLDER: &str = "soda-bend-holder";

/// The model the equipment program wrote into `output`, by the name its request gives it.
fn equipment_model(equipment_request: &Value, output: &Path) -> Result<PathBuf> {
    let name = equipment_request["name"].as_str().context("the equipment request's name")?;
    Ok(output.join(format!("{name}.step.npz")))
}

/// The routes program's request: the copper runs, the equipment request's tubes, and the soda foam.
///
/// The foam is cut around bodies of the model the equipment program wrote into `equipment_output`,
/// found by the groups its result (`equipment_result`) names.
pub fn routes_request(
    equipment_request: &Value,
    equipment_output: &Path,
    equipment_result: &Value,
    copper: &[copper::Run],
) -> Result<Value> {
    let mut routes = Map::new();
    let mut order = vec![];
    for run in copper {
        routes.insert(run.id.to_owned(), run.route()?);
        order.push(json!(run.id));
    }
    let authored = &equipment_request["routes"];
    for name in equipment_request["route_order"].as_array().context("the equipment request's route order")? {
        let key = name.as_str().context("a route name")?;
        if !routes.contains_key(key) {
            order.push(name.clone());
        }
        routes.insert(key.to_owned(), authored.get(key).with_context(|| format!("no route {key}"))?.clone());
    }
    let insulation = equipment_request["insulation"].clone();
    let model = equipment_model(equipment_request, equipment_output)?;
    let mut components = Map::new();
    if !insulation.is_null() {
        let neighbors = insulation["neighbors"].as_array().context("the insulation's neighbours")?;
        for name in std::iter::once(HOLDER).chain(neighbors.iter().filter_map(Value::as_str)) {
            let indices = equipment_result["groups"]
                .get(name)
                .with_context(|| format!("the equipment model holds no {name}"))?;
            components.insert(name.to_owned(), json!({"model": model, "indices": indices}));
        }
    }
    Ok(json!({"name": NAME, "routes": routes, "route_order": order, "insulation": insulation,
        "components": components}))
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
pub fn run_records(copper: &[copper::Run], equipment_request: &Value) -> Result<Vec<Value>> {
    let mut records: Vec<Value> = copper.iter().map(copper::Run::record).collect();
    let routes = &equipment_request["routes"];
    for name in equipment_request["route_order"].as_array().context("the equipment request's route order")? {
        let name = name.as_str().context("a route name")?;
        let route = routes.get(name).with_context(|| format!("no route {name}"))?;
        records.extend(route_record(name, route)?);
    }
    Ok(records)
}
