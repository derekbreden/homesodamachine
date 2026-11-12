use super::*;
fn counts(values: impl Iterator<Item = String>) -> Value {
    let mut out = BTreeMap::new();
    for value in values {
        *out.entry(value).or_insert(0usize) += 1;
    }
    json!(out)
}
pub fn manifest(
    at: &Value,
    graph: &Value,
    routes: &Value,
    terminations: &Value,
    bundles: &Value,
) -> Result<Value> {
    let graph_rows = rows(graph)?;
    let route_rows = rows(routes)?;
    let used = graph_rows
        .iter()
        .flat_map(|c| [c["start"].as_str().unwrap(), c["end"].as_str().unwrap()])
        .collect::<BTreeSet<_>>();
    let terminals = used
        .iter()
        .map(|id| ((*id).to_owned(), at["terminals"][*id].clone()))
        .collect::<BTreeMap<_, _>>();
    let constants = graph::constants()?;
    Ok(
        json!({"schema":1,"units":"mm","frame":"Enclosure assembly XYZ; Z up","scope":"Installed enclosure wiring, including embedded core leads. External cord, faucet and umbilical end at the enclosure interfaces.","connection_count":graph_rows.len(),"harnesses":counts(graph_rows.iter().map(|c|c["harness"].as_str().unwrap().to_owned())),"route_status_counts":counts(route_rows.iter().map(|r|r["status"].as_str().unwrap().to_owned())),"stock":model::stock()?,"unused":constants["UNUSED"],"boundaries":constants["BOUNDARIES"],"interfaces":graph::interfaces(&at["terminals"],graph)?,"terminal_status_counts":counts(used.iter().map(|id|at["terminals"][*id]["status"].as_str().unwrap().to_owned())),"terminals":terminals,"reference_frames":at["frame_checks"],"cable_passages":at["passages"],"pcb_reference":at["pcb_reference"],"terminations":terminations,"bundles":bundles,"routes":route_rows.iter().map(model::record).collect::<Result<Vec<_>>>()?,"limits":hsm_kernel::reads::json("tools/hsm/assembly-docs/src/wiring/manifest-limits.json")?}),
    )
}
pub fn numeric(root: &Path, at: &Value) -> Result<(Value, Value)> {
    numeric_request(root, at, true)
}

/// Production consumes the routing recipe without constructing an unused review manifest.
pub fn numeric_only(root: &Path, at: &Value) -> Result<Value> {
    numeric_request(root, at, false).map(|(numbers, _)| numbers)
}

fn numeric_request(root: &Path, at: &Value, review: bool) -> Result<(Value, Value)> {
    let graph = graph::connections();
    let routes = routes::routed(root, &graph, at)?;
    let terminations = terminations::inputs(at, &graph)?;
    let bundles = bundles::Context::new(root, at)?.inputs()?;
    let mut components = rows(&terminations[0])?.clone();
    components.extend(rows(&bundles[0])?.clone());
    let records = rows(&routes)?
        .iter()
        .map(model::record)
        .collect::<Result<Vec<_>>>()?;
    let numbers = readers::wire_numbers(&json!(records), &model::stock()?, &json!(components))?;
    let manifest = if review {
        manifest(at, &graph, &routes, &terminations[1], &bundles[1])?
    } else {
        Value::Null
    };
    Ok((numbers, manifest))
}
