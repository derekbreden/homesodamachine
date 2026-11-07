//! The plumbing charts' readers, their checks against the machine, and the labels and figures
//! the program writes into them.
use super::*;
use regex::Regex;

const MANIFOLD: &str = "hardware/topology/fluid-topology-manifold.mmd";
const LIMBS: &str = "hardware/topology/fluid-topology-limbs.mmd";
const CARBONATOR: &str = "hardware/topology/fluid-topology-carbonator.mmd";
const TOPOLOGY: &str = "hardware/topology/fluid-topology.md";
const LIMB_BOXES: [(&str, &str); 4] = [("LA1", "A1"), ("LA2", "A2"), ("LB1", "B1"), ("LB2", "B2")];
const UNPLACED: [&str; 15] = [
    "Faucet",
    "Gooseneck",
    "Tap",
    "CO2",
    "Vent",
    "PRVOut",
    "LevelSense",
    "P1",
    "P2",
    "P3",
    "P4",
    "WaterJet",
    "Headspace",
    "Water",
    "Float",
];

#[derive(Serialize, Deserialize, Clone)]
struct Seg {
    id: String,
    ends: Vec<String>,
    made: String,
    length: Option<f64>,
    corners: u64,
    developed: Option<f64>,
    status: String,
    missing: Vec<String>,
}
impl Seg {
    fn label(&self) -> String {
        if self.status != "complete" {
            return format!("{}<br/>incomplete", self.id);
        }
        if self.length.is_some_and(|v| v != 0.0) {
            self.id.clone()
        } else {
            format!("{}<br/>{}", self.id, self.made)
        }
    }
}
#[derive(Serialize, Deserialize, Clone)]
struct Edge {
    lineno: usize,
    a: String,
    b: String,
    arrow: String,
    label: Option<String>,
    rid: Option<String>,
}
struct Patterns {
    edge: Regex,
    arrowish: Regex,
    label: Regex,
    linkstyle: Regex,
    group: Regex,
    subgraph: Regex,
    node: Regex,
    class: Regex,
    table: Regex,
}
impl Patterns {
    fn new() -> Result<Self> {
        Ok(Self {
            edge: Regex::new(
                r#"^\s*(?P<a>\w+)\s*(?P<arrow><-->|-->|-\.->|==>)\s*(?:\|"(?P<label>[^"]*)"\|\s*)?(?P<b>\w+)\s*$"#,
            )?,
            arrowish: Regex::new(r"-->|-\.->|<-->|==>")?,
            label: Regex::new(r"^(?P<id>[a-z][a-z0-9]*-\d+)(?P<rest>(?s:.*))$")?,
            linkstyle: Regex::new(
                r"^(?P<lead>\s*linkStyle\s+)(?P<idx>[\d,\s]+?)(?P<style>\s+\S.*)$",
            )?,
            group: Regex::new(r"\(group:(?P<name>[\w-]+)\)")?,
            subgraph: Regex::new(r#"^\s*subgraph\s+(?P<id>\w+)\s*\["(?P<label>[^"]*)"\]\s*$"#)?,
            node: Regex::new(r"^\s*(?P<id>\w+)\s*[\[\{\(]")?,
            class: Regex::new(r"^\s*class\s+(?P<ids>[\w,\s]+?)\s+(?P<name>\w+)\s*;?\s*$")?,
            table: Regex::new(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")?,
        })
    }
}
fn segment_no(id: &str) -> Result<u64> {
    Ok(id.rsplit('-').next().context("segment id")?.parse()?)
}
fn made_as(made: &str) -> bool {
    MADE_AS.iter().any(|(name, _)| *name == made)
}
/// Every segment the charts label: the machine's own runs, then the manifold's connections it
/// does not draw itself, then the manifold's open mouths.
fn segments(machine: &Machine) -> Result<Vec<Seg>> {
    let mut segments: Vec<Seg> = Vec::new();
    let mut seen = BTreeSet::new();
    for run in &machine.runs {
        ensure!(made_as(&run.made), "{} is made {:?}, which is no way the charts name", run.id, run.made);
        let seg = Seg {
            id: run.id.clone(),
            ends: vec![run.frm.clone(), run.to.clone()],
            made: run.made.clone(),
            length: run.length,
            corners: run.corners,
            developed: None,
            status: run.status.clone(),
            missing: run.missing_native_routes.iter().chain(&run.missing_fittings).cloned().collect(),
        };
        if let Some(index) = segments.iter().position(|s| s.id == run.id) {
            segments[index] = seg;
        } else {
            segments.push(seg);
        }
        seen.insert(run.id.clone());
    }
    for c in &machine.interior {
        let id = format!("fluid-{}", c.run);
        if seen.contains(&id) {
            continue;
        }
        segments.push(Seg {
            id: id.clone(),
            ends: vec![c.from.clone(), c.to.clone()],
            made: c.made.to_owned(),
            length: Some(c.length),
            corners: c.corners,
            developed: None,
            status: "complete".into(),
            missing: vec![],
        });
        seen.insert(id);
    }
    for (id, port) in &machine.mouths {
        if seen.contains(id) {
            continue;
        }
        segments.push(Seg {
            id: id.clone(),
            ends: vec![port.clone()],
            made: "not drawn".into(),
            length: None,
            corners: 0,
            developed: None,
            status: "complete".into(),
            missing: vec![],
        });
        seen.insert(id.clone());
    }
    for segment in &segments {
        ensure!(made_as(&segment.made), "{} is made {:?}, which is no way the charts name", segment.id, segment.made);
    }
    Ok(segments)
}
fn nodes(machine: &Machine) -> Result<Sets> {
    let mut nodes = Sets::new();
    for (name, body, ports) in [
        ("Funnel", "funnel", vec!["drain"]),
        ("Split", "water-split", vec!["supply", "to-flavor", "to-vk"]),
        ("FlowReg", "flow-regulator", vec!["inlet", "outlet"]),
        ("VK", "vk-solenoid", vec!["inlet", "outlet"]),
        ("JointS", "suction-reducer", vec!["tube"]),
        ("JointD", "discharge-reducer", vec!["tube"]),
        ("ResA", "foam-assembly", vec!["reservoir-a"]),
        ("ResAFill", "foam-assembly", vec!["reservoir-a-fill"]),
        ("ResB", "foam-assembly", vec!["reservoir-b"]),
        ("ResBFill", "foam-assembly", vec!["reservoir-b-fill"]),
        ("BhA", "bulkhead-flavor-a", vec!["tube-in", "tube-out"]),
        ("BhB", "bulkhead-flavor-b", vec!["tube-in", "tube-out"]),
        ("BhW", "bulkhead-water", vec!["inboard", "outboard"]),
        (
            "BFP",
            "asse1022-assembly",
            vec!["tube-in", "tube-out", "vent-tip"],
        ),
        (
            "DischChain",
            "discharge-chain",
            vec!["inlet", "outlet", "tube-port"],
        ),
        ("PW", "g-ganen-pump", vec!["suction", "discharge"]),
        ("CO2In", "co2-inlet", vec!["inboard", "outboard"]),
        ("GasCheck", "gas-check", vec!["inlet", "outlet"]),
        ("GasReg", "gas-regulator", vec!["inlet", "outlet"]),
        ("FlowMeter", "digiten-flow", vec!["inlet", "outlet"]),
        ("BhCarb", "bulkhead-carb", vec!["tube-in", "tube-out"]),
        ("CapWater", "foam-assembly", vec!["water-in"]),
        ("CapCO2", "foam-assembly", vec!["co2-in"]),
        ("CapCarb", "foam-assembly", vec!["carb-water-out"]),
    ] {
        nodes.insert(
            name.into(),
            ports
                .into_iter()
                .map(|port| format!("{body}.{port}"))
                .collect(),
        );
    }
    nodes.get_mut("Funnel").unwrap().extend([
        "funnel-drain-union.stub".into(),
        "funnel-drain-union.outlet".into(),
    ]);
    nodes
        .get_mut("BFP")
        .unwrap()
        .extend(["asse-inlet-tpu.tube".into(), "asse-outlet-tpu.tube".into()]);
    for valve in &machine.valves {
        nodes.insert(
            format!("V{}", valve.chars().last().context("valve name")?),
            [
                format!("valve-{}.inlet", valve.to_lowercase()),
                format!("valve-{}.outlet", valve.to_lowercase()),
                format!("{valve}-I"),
                format!("{valve}-O"),
            ]
            .into_iter()
            .collect(),
        );
    }
    for station in machine.stations.iter().map(|(name, _)| name).filter(|n| n.starts_with("Y-")) {
        nodes.insert(
            format!("Y{}", station.chars().last().unwrap()),
            (1..4).map(|i| format!("{station}-{i}")).collect(),
        );
    }
    for pump in &machine.pumps {
        let suffix = pump.chars().last().context("pump name")?.to_uppercase();
        let suffix = suffix.to_string();
        nodes.insert(
            format!("P{suffix}"),
            [format!("P-{suffix}-I"), format!("P-{suffix}-O")]
                .into_iter()
                .collect(),
        );
    }
    Ok(nodes)
}
fn class_members(machine: &Machine) -> Sets {
    let short = |n: &str| format!("{}{}", &n[..1], &n[2..]);
    BTreeMap::from([
        ("tee".into(), machine.stations.iter().filter(|(n, _)| n.starts_with("Y-")).map(|(n, _)| short(n)).collect()),
        ("upper".into(), machine.stations.iter().filter(|(_, fold)| *fold).map(|(n, _)| short(n)).collect()),
    ])
}
fn read_edges(path: &str, text: &str, p: &Patterns) -> Result<(Vec<String>, Vec<Edge>)> {
    let lines = text.lines().map(str::to_owned).collect::<Vec<_>>();
    let mut edges = Vec::new();
    for (lineno, line) in lines.iter().enumerate() {
        if line.trim_start().starts_with("%%") {
            continue;
        }
        if let Some(c) = p.edge.captures(line) {
            let label = c.name("label").map(|m| m.as_str().to_owned());
            let rid = label
                .as_ref()
                .and_then(|v| p.label.captures(v))
                .map(|c| c["id"].to_owned());
            edges.push(Edge {
                lineno,
                a: c["a"].into(),
                b: c["b"].into(),
                arrow: c["arrow"].into(),
                label,
                rid,
            });
        } else if p.arrowish.is_match(line) {
            bail!(
                "{path} line {}: an edge this driver cannot read —\n    {}\n  Charts it gates carry ONE edge per line, `A -->|\"label\"| B`, with no chaining: the link index every linkStyle names is the count of edges before it, and a line holding two would put every later index out.",
                lineno + 1,
                line.trim()
            );
        }
    }
    Ok((lines, edges))
}
fn check_comments(path: &str, text: &str) -> Vec<String> {
    text.lines().enumerate().filter(|(_,line)|line.trim()=="%%").map(|(i,_)|format!("  {path} line {}: a bare `%%` — mermaid draws this as a node, not a comment. Use a blank line for a paragraph break.",i+1)).collect()
}
fn check_graph(
    edges: &[Edge],
    segments: &[Seg],
    nodes: &Sets,
    owes_ids: bool,
) -> Result<Vec<String>> {
    let mut bad = Vec::new();
    let mut seen = BTreeMap::new();
    let empty = BTreeSet::new();
    for e in edges {
        let mut unknown = false;
        for node in [&e.a, &e.b] {
            if !nodes.contains_key(node) && !UNPLACED.contains(&node.as_str()) {
                bad.push(format!("  line {}: node '{}' is in no table — add it to NODES with the anchors it stands for",e.lineno+1,node));
                unknown = true;
            }
        }
        if unknown {
            continue;
        }
        let held = [
            nodes.get(&e.a).unwrap_or(&empty),
            nodes.get(&e.b).unwrap_or(&empty),
        ];
        let Some(id) = &e.rid else {
            if !owes_ids || UNPLACED.contains(&e.a.as_str()) || UNPLACED.contains(&e.b.as_str()) {
                continue;
            }
            if MADE_UP.iter().any(|[a, b]| {
                (held[0].contains(*a) && held[1].contains(*b))
                    || (held[0].contains(*b) && held[1].contains(*a))
            }) {
                continue;
            }
            bad.push(format!("  line {}: {} → {} carries no route id, but the machine knows both ends — every segment between two of them has one",e.lineno+1,e.a,e.b));
            continue;
        };
        if let Some(line) = seen.get(id) {
            bad.push(format!(
                "  line {}: {id} drawn twice (also line {})",
                e.lineno + 1,
                line + 1
            ));
            continue;
        }
        seen.insert(id, e.lineno);
        let Some(seg) = segments.iter().find(|s| s.id == *id) else {
            bad.push(format!(
                "  line {}: {id} is drawn here and the machine builds nothing by that name",
                e.lineno + 1
            ));
            continue;
        };
        if seg.ends.len() == 1 {
            if !held.iter().any(|h| h.contains(&seg.ends[0])) {
                bad.push(format!("  line {}: {id} is drawn {} → {}; the machine builds it off {} and neither node holds that",e.lineno+1,e.a,e.b,seg.ends[0]));
            } else if !UNPLACED.contains(&e.a.as_str()) && !UNPLACED.contains(&e.b.as_str()) {
                bad.push(format!("  line {}: {id} is drawn between two placed nodes and the machine draws only its {} end",e.lineno+1,seg.ends[0]));
            }
            continue;
        }
        if UNPLACED.contains(&e.a.as_str()) || UNPLACED.contains(&e.b.as_str()) {
            bad.push(format!("  line {}: {id} reaches {} → {}, and the machine places no body for one of them, yet builds the segment end to end",e.lineno+1,e.a,e.b));
            continue;
        }
        ensure!(seg.ends.len() == 2, "segment endpoints");
        let (from, to) = (&seg.ends[0], &seg.ends[1]);
        if !(held[0].contains(from) && held[1].contains(to))
            && !(held[1].contains(from) && held[0].contains(to))
        {
            bad.push(format!(
                "  line {}: {id} is drawn {} → {}; the machine builds it {from} → {to}",
                e.lineno + 1,
                e.a,
                e.b
            ));
        }
    }
    Ok(bad)
}
fn check_linkstyle_cover(
    path: &str,
    lines: &[String],
    edges: &[Edge],
    p: &Patterns,
) -> Result<Vec<String>> {
    let mut seen = BTreeMap::new();
    let mut bad = Vec::new();
    for (i, line) in lines.iter().enumerate() {
        if line.trim_start().starts_with("%%") {
            continue;
        }
        let Some(c) = p.linkstyle.captures(line) else {
            continue;
        };
        for token in c["idx"].split(',').map(str::trim).filter(|s| !s.is_empty()) {
            let n = token.parse::<usize>()?;
            if n >= edges.len() {
                bad.push(format!(
                    "  {path} line {}: linkStyle names edge {n} and the chart draws {}",
                    i + 1,
                    edges.len()
                ));
            } else if let Some(line) = seen.get(&n) {
                bad.push(format!(
                    "  {path} line {}: edge {n} is styled twice (also line {})",
                    i + 1,
                    line + 1
                ));
            } else {
                seen.insert(n, i);
            }
        }
    }
    for (n, e) in edges.iter().enumerate() {
        if !seen.contains_key(&n) {
            bad.push(format!("  {path} line {}: edge {n} ({} → {}) is in no linkStyle — it renders in the default colour",e.lineno+1,e.a,e.b));
        }
    }
    Ok(bad)
}
fn owed(text: &str, p: &Patterns) -> BTreeMap<String, (String, String)> {
    text.lines()
        .filter_map(|line| p.table.captures(line))
        .map(|c| {
            (
                format!("fluid-{}", &c[1]),
                (c[2].trim().into(), c[3].trim().into()),
            )
        })
        .collect()
}
fn check_inventory(
    edges: &[Edge],
    segments: &[Seg],
    owed: &BTreeMap<String, (String, String)>,
) -> Result<Vec<String>> {
    let named = owed.keys().cloned().collect::<BTreeSet<_>>();
    let built = segments
        .iter()
        .filter(|s| s.id.starts_with("fluid-"))
        .map(|s| s.id.clone())
        .collect::<BTreeSet<_>>();
    let drawn = edges
        .iter()
        .filter_map(|e| e.rid.clone())
        .collect::<BTreeSet<_>>();
    let mut bad = Vec::new();
    for (left, right, tail) in [
        (
            &named,
            &built,
            "has a row in fluid-topology.md and the machine builds nothing by that name",
        ),
        (
            &built,
            &named,
            "is built by the machine and fluid-topology.md's tables have no row for it",
        ),
        (
            &built,
            &drawn,
            "is built by the machine and the chart does not draw it",
        ),
    ] {
        let mut missing = left.difference(right).collect::<Vec<_>>();
        missing.sort_by_key(|id| segment_no(id).unwrap_or(0));
        for id in missing {
            bad.push(format!("  {id} {tail}"));
        }
    }
    Ok(bad)
}
fn py_list(set: &BTreeSet<String>) -> String {
    format!(
        "[{}]",
        set.iter()
            .map(|s| format!("'{s}'"))
            .collect::<Vec<_>>()
            .join(", ")
    )
}
fn check_boxes(
    path: &str,
    text: &str,
    strict: bool,
    nodes: &Sets,
    limbs: &Sets,
    p: &Patterns,
) -> Vec<String> {
    let mut bad = Vec::new();
    let mut stack: Vec<(String, String, usize, BTreeSet<String>)> = Vec::new();
    let mut drawn = BTreeSet::new();
    for (i, line) in text.lines().enumerate() {
        if line.trim_start().starts_with("%%") {
            continue;
        }
        if let Some(c) = p.subgraph.captures(line) {
            stack.push((c["id"].into(), c["label"].into(), i, BTreeSet::new()));
            drawn.insert(c["id"].to_owned());
            continue;
        }
        if line.trim() == "end" {
            let Some((box_id, label, at, held)) = stack.pop() else {
                bad.push(format!(
                    "  {path} line {}: an `end` closing no subgraph",
                    i + 1
                ));
                continue;
            };
            let Some((_, limb)) = LIMB_BOXES.iter().find(|(id, _)| *id == box_id) else {
                if strict {
                    bad.push(format!("  {path} line {}: subgraph '{box_id}' is in no table — add it to LIMB_BOXES, or take it out of a chart that is nothing but limbs",at+1));
                }
                continue;
            };
            if !limbs.contains_key(*limb) {
                bad.push(format!(
                    "  {path} line {}: {box_id} — the manifold chains no '{limb}'",
                    at + 1
                ));
            } else if held != limbs[*limb] {
                bad.push(format!(
                    "  {path} line {}: {box_id} ({limb}) draws {}; the limb chains {}",
                    at + 1,
                    if held.is_empty() {
                        "—".into()
                    } else {
                        py_list(&held)
                    },
                    py_list(&limbs[*limb])
                ));
            }
            if !label.starts_with(limb) {
                bad.push(format!("  {path} line {}: {box_id} is drawn '{label}' and holds limb '{limb}' — the title a reader sees must name the limb",at+1));
            }
            continue;
        }
        if let Some(c) = p.node.captures(line) {
            if let Some(last) = stack.last_mut() {
                let node = &c["id"];
                if nodes.contains_key(node) {
                    last.3.insert(if node.len() == 2 {
                        format!("{}-{}", &node[..1], &node[1..])
                    } else {
                        node.into()
                    });
                }
            }
        }
    }
    if !stack.is_empty() {
        bad.push(format!(
            "  {path}: {} subgraph(s) never closed",
            stack.len()
        ));
    }
    for (id, limb) in LIMB_BOXES {
        if !drawn.contains(id) {
            bad.push(format!(
                "  {path}: limb {limb} is chained in the manifold and has no box in the chart"
            ));
        }
    }
    for limb in limbs.keys() {
        if !LIMB_BOXES.iter().any(|(_, name)| name == limb) {
            bad.push(format!("  the manifold chains limb '{limb}' and no chart box claims it — add it to LIMB_BOXES and draw it"));
        }
    }
    bad
}
fn check_classes(path: &str, text: &str, want: &Sets, p: &Patterns) -> Vec<String> {
    let mut bad = Vec::new();
    let mut seen = BTreeSet::new();
    for (i, line) in text.lines().enumerate() {
        if line.trim_start().starts_with("%%") {
            continue;
        }
        let Some(c) = p.class.captures(line) else {
            continue;
        };
        let name = &c["name"];
        if let Some(expected) = want.get(name) {
            let drawn = c["ids"]
                .split(',')
                .map(str::trim)
                .filter(|s| !s.is_empty())
                .map(str::to_owned)
                .collect::<BTreeSet<_>>();
            seen.insert(name.to_owned());
            if drawn != *expected {
                bad.push(format!(
                    "  {path} line {}: class {name} draws {}; the pack has {}",
                    i + 1,
                    py_list(&drawn),
                    py_list(expected)
                ));
            }
        }
    }
    // class_members authors tee first, then upper; preserve that diagnostic order.
    for name in ["tee", "upper"] {
        if let Some(expected) = want.get(name) {
            if !seen.contains(name) {
                bad.push(format!(
                    "  {path}: nothing is classed '{name}', and the pack has {}",
                    py_list(expected)
                ));
            }
        }
    }
    bad
}
fn edge_group(edge: &Edge) -> Result<&'static str> {
    let Some(id) = &edge.rid else {
        return Ok("outside");
    };
    if !id.starts_with("fluid-") {
        return Ok("carbonator");
    }
    match segment_no(id)? {
        1..=8 => Ok("shared"),
        9..=18 => Ok("channel-a"),
        19..=28 => Ok("channel-b"),
        _ => bail!("{id}: outside every group in FLUID_GROUPS"),
    }
}
fn rewrite_labels(lines: &mut [String], edges: &mut [Edge], segments: &[Seg]) -> Result<()> {
    for edge in edges {
        if let Some(id) = &edge.rid {
            let want = segments
                .iter()
                .find(|s| s.id == *id)
                .with_context(|| format!("segment {id}"))?
                .label();
            if edge.label.as_deref() != Some(&want) {
                if let Some(label) = &edge.label {
                    lines[edge.lineno] = lines[edge.lineno]
                        .replace(&format!("|\"{label}\"|"), &format!("|\"{want}\"|"));
                }
                edge.label = Some(want);
            }
        }
    }
    Ok(())
}
fn rewrite_linkstyles(lines: &mut [String], edges: &[Edge], p: &Patterns) -> Result<Vec<String>> {
    let mut groups: BTreeMap<&str, Vec<usize>> = BTreeMap::new();
    for (i, e) in edges.iter().enumerate() {
        groups.entry(edge_group(e)?).or_default().push(i);
    }
    let mut problems = Vec::new();
    let mut pending: Option<String> = None;
    let mut written = BTreeSet::new();
    for (i, line) in lines.iter_mut().enumerate() {
        if line.trim_start().starts_with("%%") {
            if let Some(c) = p.group.captures(line) {
                pending = Some(c["name"].into());
                continue;
            }
        }
        let Some(c) = p.linkstyle.captures(line) else {
            continue;
        };
        let Some(group) = pending.take() else {
            problems.push(format!("  line {}: a linkStyle with no (group:NAME) in the comment above it — this driver writes its indices and cannot tell which edges it is for",i+1));
            continue;
        };
        if let Some(indices) = groups.get(group.as_str()) {
            *line = format!(
                "{}{}{}",
                &c["lead"],
                indices
                    .iter()
                    .map(usize::to_string)
                    .collect::<Vec<_>>()
                    .join(","),
                &c["style"]
            );
            written.insert(group);
        } else {
            problems.push(format!(
                "  line {}: group '{group}' matches no edge in the chart",
                i + 1
            ));
        }
    }
    for (group, indices) in groups {
        if !written.contains(group) {
            problems.push(format!("  {} edges are in group '{group}' and no linkStyle claims it — they render in the default colour",indices.len()));
        }
    }
    Ok(problems)
}
fn limb_variables(machine: &Machine, limbs: &Sets) -> Result<Variables> {
    let members = limbs
        .values()
        .flat_map(|set| set.iter())
        .collect::<BTreeSet<_>>();
    Ok(BTreeMap::from([
        ("LIMB_COUNT".into(), limbs.len().to_string()),
        (
            "LIMB_VALVES".into(),
            members
                .iter()
                .filter(|s| s.starts_with("V-"))
                .count()
                .to_string(),
        ),
        (
            "TEE_COUNT".into(),
            members
                .iter()
                .filter(|s| s.starts_with("Y-"))
                .count()
                .to_string(),
        ),
        (
            "PURCHASED_TEE_COUNT".into(),
            machine.purchased_tees.to_string(),
        ),
        (
            "PUMP_TEE_COUNT".into(),
            machine.pump_tees.to_string(),
        ),
        (
            "UPPER_COUNT".into(),
            machine.stations.iter().filter(|(_, fold)| *fold).count().to_string(),
        ),
        (
            "LOWER_COUNT".into(),
            machine.stations.iter().filter(|(_, fold)| !*fold).count().to_string(),
        ),
        ("PUMP_COUNT".into(), machine.pumps.len().to_string()),
    ]))
}
fn name(path: &str) -> &str {
    path.rsplit('/').next().unwrap()
}
fn failure(problems: Vec<String>, heading: &str) -> Output {
    Output { status: 1, stdout: format!("{heading}\n{}\n", problems.join("\n")), ..Output::default() }
}
pub fn run(request: &Request) -> Result<Output> {
    let machine = &request.machine;
    let p = Patterns::new()?;
    let segments = segments(machine)?;
    let nodes = nodes(machine)?;
    let limbs = &machine.limbs;
    let classes = class_members(machine);
    let mut texts = BTreeMap::new();
    for path in [MANIFOLD, LIMBS, CARBONATOR, TOPOLOGY] {
        texts.insert(path, read_text(&request.root.join(path))?);
    }
    let owed = owed(&texts[TOPOLOGY], &p);
    let limb_vars = limb_variables(machine, limbs)?;
    let mut output = Output::default();
    let (mut lines, mut edges) = read_edges(name(MANIFOLD), &texts[MANIFOLD], &p)?;
    let (mut carb_lines, mut carb_edges) = read_edges(name(CARBONATOR), &texts[CARBONATOR], &p)?;
    let (limb_lines, limb_edges) = read_edges(name(LIMBS), &texts[LIMBS], &p)?;
    let mut problems = Vec::new();
    for chart in [MANIFOLD, LIMBS, CARBONATOR] {
        problems.extend(check_comments(name(chart), &texts[chart]));
    }
    problems.extend(check_graph(&edges, &segments, &nodes, true)?);
    problems.extend(check_graph(&carb_edges, &segments, &nodes, false)?);
    problems.extend(check_inventory(&edges, &segments, &owed)?);
    problems.extend(check_boxes(
        name(MANIFOLD),
        &texts[MANIFOLD],
        false,
        &nodes,
        limbs,
        &p,
    ));
    problems.extend(check_boxes(
        name(LIMBS),
        &texts[LIMBS],
        true,
        &nodes,
        limbs,
        &p,
    ));
    problems.extend(check_classes(
        name(MANIFOLD),
        &texts[MANIFOLD],
        &classes,
        &p,
    ));
    problems.extend(check_classes(name(LIMBS), &texts[LIMBS], &classes, &p));
    problems.extend(check_linkstyle_cover(
        name(CARBONATOR),
        &carb_lines,
        &carb_edges,
        &p,
    )?);
    problems.extend(check_linkstyle_cover(
        name(LIMBS),
        &limb_lines,
        &limb_edges,
        &p,
    )?);
    if !problems.is_empty() {
        return Ok(failure(
            problems,
            "fluid-topology charts disagree with the enclosure assembly:",
        ));
    }
    let before = lines.clone();
    let carb_before = carb_lines.clone();
    rewrite_labels(&mut lines, &mut edges, &segments)?;
    rewrite_labels(&mut carb_lines, &mut carb_edges, &segments)?;
    problems.extend(rewrite_linkstyles(&mut lines, &edges, &p)?);
    problems.extend(check_linkstyle_cover(name(MANIFOLD), &lines, &edges, &p)?);
    if !problems.is_empty() {
        return Ok(failure(problems, "fluid-topology-manifold.mmd linkStyle:"));
    }
    if request.operation == "check" {
        let mut stale = Vec::new();
        for (path, was, now) in [
            (MANIFOLD, &before, &lines),
            (CARBONATOR, &carb_before, &carb_lines),
        ] {
            for (i, (b, a)) in was.iter().zip(now).enumerate() {
                if b != a {
                    stale.push(format!("  {} line {}: {}", name(path), i + 1, b.trim()));
                }
            }
        }
        if !stale.is_empty() {
            return Ok(failure(
                stale,
                "fluid-topology charts are stale — run the fluid-topology program:",
            ));
        }
        output.stdout = "fluid-topology ✓\n".into();
        return Ok(output);
    }
    if request.write {
        for (path, now) in [(MANIFOLD, &lines), (CARBONATOR, &carb_lines)] {
            let target = request.out.join(path);
            if let Some(parent) = target.parent() {
                std::fs::create_dir_all(parent)?;
            }
            hsm_documents::write_if_changed(&target, (now.join("\n") + "\n").as_bytes())?;
            output.maintained.push(path.into());
        }
    }
    let mut fluid = segments
        .iter()
        .filter(|s| s.id.starts_with("fluid-"))
        .collect::<Vec<_>>();
    fluid.sort_by_key(|s| segment_no(&s.id).unwrap_or(0));
    for s in &fluid {
        let length = if let Some(length) = s.length {
            format!("{:>7} mm", fmt(length, ".1f")?)
        } else if let Some(length) = s.developed {
            format!(
                "{:>7} mm exposed; add both fitting insertions",
                fmt(length, ".1f")?
            )
        } else {
            "        —".into()
        };
        output.stdout.push_str(&format!(
            "  {:<9} {length}  {} corners  {:<9} {}\n",
            s.id,
            s.corners,
            s.made,
            s.ends.join(" → ")
        ));
        if s.status != "complete" {
            output.stdout.push_str(&format!(
                "    incomplete: missing {}\n",
                s.missing.join(", ")
            ));
        }
    }
    output.stdout.push_str(&format!("  {:<9} {:>7} mm over {} segments; add actual fitting insertions to mouth-to-mouth paths; prepared pump tubes excluded\n","REPORTED",fmt(fluid.iter().map(|s|s.length.unwrap_or(0.0)).sum(),".1f")?,fluid.len()));
    output.stdout.push_str(&format!(
        "  limbs {}, valves {}, junctions {}, pumps {} ({} upper-deck bodies, {} lower)\n",
        limb_vars["LIMB_COUNT"],
        limb_vars["LIMB_VALVES"],
        limb_vars["TEE_COUNT"],
        limb_vars["PUMP_COUNT"],
        limb_vars["UPPER_COUNT"],
        limb_vars["LOWER_COUNT"]
    ));
    Ok(output)
}
