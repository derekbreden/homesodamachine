use super::*;
fn counts(values: impl Iterator<Item = String>) -> Value {
    let mut out = BTreeMap::new();
    for value in values {
        *out.entry(value).or_insert(0usize) += 1;
    }
    json!(out)
}
/// The review of the routed wiring: its connections, terminals, passages, terminations, shared
/// cables and routes, with their counts by harness and status.
pub fn manifest(
    at: &terminals::State,
    graph: &[graph::Connection],
    routes: &[model::Route],
    terminations: &BTreeMap<String, Value>,
    bundles: &BTreeMap<String, bundles::Record>,
) -> Result<Value> {
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
        json!({"schema":1,"units":"mm","frame":"Enclosure assembly XYZ; Z up","scope":"Installed enclosure wiring, including embedded core leads. External cord, faucet and umbilical end at the enclosure interfaces.","connection_count":graph.len(),"harnesses":counts(graph.iter().map(|c|c.harness.clone())),"route_status_counts":counts(routes.iter().map(|r|r.status.clone())),"stock":model::stock()?,"unused":constants["UNUSED"],"boundaries":constants["BOUNDARIES"],"interfaces":graph::interfaces(&at.terminals,graph)?,"terminal_status_counts":counts(used.iter().map(|id|at.terminals[*id].status.clone())),"terminals":terminals,"reference_frames":at.frame_checks,"cable_passages":at.passages,"pcb_reference":at.pcb_reference,"terminations":terminations,"bundles":bundles,"routes":routes.iter().map(model::Route::record).collect::<Result<Vec<_>>>()?,"limits":hsm_kernel::reads::json("tools/hsm/assembly-docs/src/wiring/manifest-limits.json")?}),
    )
}
/// The request the installed wires are cut from, with the review of the routed wiring.
pub fn numeric(
    src: &sources::Sources,
    root: &Path,
    at: &terminals::State,
) -> Result<(wire_request::Request, Value)> {
    let (numbers, manifest) = numeric_request(src, root, at, true)?;
    Ok((numbers, manifest.context("the wiring review")?))
}

/// The request the installed wires are cut from.
pub fn numeric_only(
    src: &sources::Sources,
    root: &Path,
    at: &terminals::State,
) -> Result<wire_request::Request> {
    numeric_request(src, root, at, false).map(|(numbers, _)| numbers)
}

fn numeric_request(
    src: &sources::Sources,
    root: &Path,
    at: &terminals::State,
    review: bool,
) -> Result<(wire_request::Request, Option<Value>)> {
    let graph = graph::connections();
    let routes = routes::routed(src, root, &graph, at)?;
    let (mut bodies, terminations) = terminations::inputs(src, at, &graph)?;
    let (jackets, bundles) = bundles::Context::new(src, root, at)?.inputs()?;
    bodies.extend(jackets);
    let numbers = readers::wire_numbers(src, &routes, &model::stock()?, bodies)?;
    let manifest = if review {
        Some(manifest(at, &graph, &routes, &terminations, &bundles)?)
    } else {
        None
    };
    Ok((numbers, manifest))
}
