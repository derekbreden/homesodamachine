use super::*;
fn counts(values: impl Iterator<Item = String>) -> Value {
    let mut out = BTreeMap::new();
    for value in values {
        *out.entry(value).or_insert(0usize) += 1;
    }
    json!(out)
}
pub fn manifest(
    at: &terminals::State,
    graph: &[graph::Connection],
    routes: &Value,
    terminations: &Value,
    bundles: &Value,
) -> Result<Value> {
    let route_rows = rows(routes)?;
    let used = graph
        .iter()
        .flat_map(|c| [c.start.as_str(), c.end.as_str()])
        .collect::<BTreeSet<_>>();
    let terminals = used
        .iter()
        .map(|id| ((*id).to_owned(), &at.terminals[*id]))
        .collect::<BTreeMap<_, _>>();
    let constants = graph::constants()?;
    Ok(
        json!({"schema":1,"units":"mm","frame":"Enclosure assembly XYZ; Z up","scope":"Installed enclosure wiring, including embedded core leads. External cord, faucet and umbilical end at the enclosure interfaces.","connection_count":graph.len(),"harnesses":counts(graph.iter().map(|c|c.harness.clone())),"route_status_counts":counts(route_rows.iter().map(|r|r["status"].as_str().unwrap().to_owned())),"stock":model::stock()?,"unused":constants["UNUSED"],"boundaries":constants["BOUNDARIES"],"interfaces":graph::interfaces(&at.terminals,graph)?,"terminal_status_counts":counts(used.iter().map(|id|at.terminals[*id].status.clone())),"terminals":terminals,"reference_frames":at.frame_checks,"cable_passages":at.passages,"pcb_reference":at.pcb_reference,"terminations":terminations,"bundles":bundles,"routes":route_rows.iter().map(model::record).collect::<Result<Vec<_>>>()?,"limits":hsm_kernel::reads::json("tools/hsm/assembly-docs/src/wiring/manifest-limits.json")?}),
    )
}
pub fn numeric(src: &sources::Sources, root: &Path, at: &terminals::State) -> Result<(Value, Value)> {
    numeric_request(src, root, at, true)
}

/// Production consumes the routing recipe without constructing an unused review manifest.
pub fn numeric_only(src: &sources::Sources, root: &Path, at: &terminals::State) -> Result<Value> {
    numeric_request(src, root, at, false).map(|(numbers, _)| numbers)
}

fn numeric_request(
    src: &sources::Sources,
    root: &Path,
    at: &terminals::State,
    review: bool,
) -> Result<(Value, Value)> {
    let graph = graph::connections();
    let routes = routes::routed(src, root, &graph, at)?;
    let terminations = terminations::inputs(src, at, &graph)?;
    let bundles = bundles::Context::new(src, root, at)?.inputs()?;
    let mut components = rows(&terminations[0])?.clone();
    components.extend(rows(&bundles[0])?.clone());
    let records = rows(&routes)?
        .iter()
        .map(model::record)
        .collect::<Result<Vec<_>>>()?;
    let numbers =
        readers::wire_numbers(src, &json!(records), &model::stock()?, &json!(components))?;
    let manifest = if review {
        manifest(at, &graph, &routes, &terminations[1], &bundles[1])?
    } else {
        Value::Null
    };
    Ok((numbers, manifest))
}
