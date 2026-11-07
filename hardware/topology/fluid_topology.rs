//! The plumbing charts' labels: every connection in the manifold and carbonator charts labelled
//! with how the machine makes it, each chart's graph checked against the machine's runs and the
//! manifold's connections, and the counts and lengths the charts state. The connections come
//! from the manifold's numbers and the runs from the installed machine's facts.
//!
//!     fluid-topology [--check] [<output directory>]
#[path = "fluid-topology/chart.rs"]
mod chart;

use anyhow::{Context, Result, bail, ensure};
use hsm_documents::Variables;
use hsm_manifold_numbers::{self as manifold, CONNECTIONS, LIMBS, MOUTHS, Made, PUMPS, Seg};
use serde::{Deserialize, Serialize};
use serde_json::{Map, Value, json};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf, absolute};

/// The installed machine's facts, whose runs the charts label.
const FACTS: &str = "hardware/manifold-layout/enclosure-assembly.facts.json";

/// The ways a run is made, as the charts name them.
const MADE_AS: [(&str, &str); 9] = [
    ("butt", "made by a butt between two collets"),
    ("drawn", "drawn as a run"),
    ("elbows", "made by a stem elbow in each collet and one straight LLDPE tube between them"),
    ("mate", "made up across the plane its two bodies share"),
    ("not drawn", "still to route"),
    ("pump-dock", "made by a prepared pump's LLDPE tube through the collet plate into a tee"),
    ("straight", "made by a lane's own straight"),
    ("threaded", "made up on its fittings' threads"),
    ("turn", "made by a quarter turn and the step off it"),
];

/// Ports joined where their two bodies meet, with no run between them.
const MADE_UP: [[&str; 2]; 1] = [["funnel.drain", "funnel-drain-union.stub"]];

/// What the charts are made from and asked to do.
struct Request {
    root: PathBuf,
    out: PathBuf,
    input: Value,
    write: bool,
    operation: String,
}

/// What a chart run found: its status and figures, what it says, and the charts it wrote.
#[derive(Default)]
struct Output {
    exports: BTreeMap<String, Value>,
    stdout: String,
    #[allow(dead_code)]
    data_reads: Vec<String>,
    maintained: Vec<String>,
}

/// A text file of the tree, read whole and named to the build as read.
fn read_text(path: &Path) -> Result<String> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(path, &bytes);
    Ok(String::from_utf8(bytes)?)
}

fn n(input: &Value, name: &str) -> Result<f64> {
    input.get(name).and_then(Value::as_f64).with_context(|| format!("missing number {name}"))
}

fn list<'a>(input: &'a Value, name: &str) -> Result<&'a Vec<Value>> {
    input.get(name).and_then(Value::as_array).with_context(|| format!("missing list {name}"))
}

fn fmt(number: f64, spec: &str) -> Result<String> {
    if spec.is_empty() {
        return Ok(if number.fract() == 0. { format!("{}", number as i64) } else { number.to_string() });
    }
    hsm_documents::format_number(number, spec)
}

/// The ends of a straight tube's centreline.
fn ends(tube: &manifold::Tube) -> Result<Value> {
    match tube.path {
        [Seg::Line([a, b])] => Ok(json!([a, b])),
        _ => bail!("{} is not one straight", tube.name),
    }
}

/// What the charts take from the machine: its runs, and the manifold's connections, limbs,
/// mouths and the tubes its connections are made of, measured.
fn input(root: &Path) -> Result<Value> {
    let facts: Value = serde_json::from_str(&read_text(&root.join(FACTS))?)?;
    let tube = |run: u32| manifold::tube(&format!("tube-fluid-{run}"));
    let mut recipes = vec![];
    let (mut fore, mut fore_lengths, mut links, mut cuts, mut steps) = (Map::new(), Map::new(), Map::new(), Map::new(), Map::new());
    let mut barb_of = vec![];
    let mut quarter = None;
    for c in &CONNECTIONS {
        let how = match c.made {
            Made::Turn => {
                let turn = manifold::length(manifold::tube(&format!("turn-fluid-{}", c.run)));
                ensure!(quarter.is_none_or(|q: f64| (q - turn).abs() < 1e-9), "the source turns differ");
                quarter = Some(turn);
                let step = manifold::length(manifold::tube(&format!("step-fluid-{}", c.run)));
                steps.insert(c.run.to_string(), json!([0.0, 0.0, step]));
                "turn".to_owned()
            }
            Made::Crossbar => "crossbar".to_owned(),
            Made::Butt => "butt".to_owned(),
            Made::LowerReturn { .. } => {
                let kinds: Vec<Value> = tube(c.run)
                    .path
                    .iter()
                    .map(|s| json!({"kind": match s { Seg::Line(_) => "line", Seg::Arc(_) => "arc" }}))
                    .collect();
                links.insert(c.run.to_string(), json!(kinds));
                cuts.insert(c.run.to_string(), json!(manifold::lower_return_cut(c.run)));
                "spine".to_owned()
            }
            Made::Upper { tee } => {
                let name = format!("fore-{}", tee.to_lowercase());
                fore.insert(name.clone(), ends(tube(c.run))?);
                fore_lengths.insert(name.clone(), json!(manifold::length(tube(c.run))));
                name
            }
            Made::PumpTube { tee } => {
                barb_of.push(tee);
                tee.to_owned()
            }
        };
        recipes.push(json!([c.run, c.from, c.to, how]));
    }
    let mouths: Vec<Value> = MOUTHS
        .iter()
        .map(|m| {
            let [a, b] = match manifold::tube(&format!("stub-{}", m.run)).path {
                [Seg::Line(points)] => *points,
                _ => panic!("a mouth's stub is one straight"),
            };
            let axis = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
            let length = (axis[0] * axis[0] + axis[1] * axis[1] + axis[2] * axis[2]).sqrt();
            json!([m.run, m.port, m.what, a, axis.map(|c| c / length)])
        })
        .collect();
    let stations: Map<String, Value> = manifold::stations()
        .map(|(name, limb, fold)| (name.to_owned(), json!({"fold": fold, "limb": limb.name})))
        .collect();
    let limbs: Map<String, Value> = LIMBS
        .iter()
        .map(|l| (l.name.to_owned(), json!({"chain": l.chain.iter().map(|n| json!([n])).collect::<Vec<_>>()})))
        .collect();
    let lower: Map<String, Value> = manifold::lower_returns().map(|(run, tee)| (run.to_string(), json!(tee))).collect();
    let valves: Vec<&str> = manifold::stations().map(|(n, _, _)| n).filter(|n| n.starts_with("V-")).collect();
    let mut sorted_valves = valves.clone();
    sorted_valves.sort();
    let exposed = fore_lengths.values().next().cloned().context("the manifold has upper tubes")?;
    Ok(json!({
        "facts_runs": facts["runs"],
        "segment_recipes": recipes,
        "mouths": mouths,
        "barb_of": barb_of,
        "fore_stubs": fore,
        "fore_stub_lengths": fore_lengths,
        "fore_stub_exposed": exposed,
        "lower_links": links,
        "lower_lengths": cuts,
        "source_steps": steps,
        "quarter_length": quarter.context("the manifold has source turns")?,
        // The source tees' branch collets meet face to face: a crossbar with no tube.
        "runs": {"crossbar": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]},
        "made_as": MADE_AS.iter().map(|(k, v)| (k.to_string(), json!(v))).collect::<Map<_, _>>(),
        "made_up": MADE_UP,
        "stations": stations,
        "pumps": PUMPS,
        "limbs": limbs,
        "valves": sorted_valves,
        "purchased_tees": manifold::purchased_tees().collect::<Vec<_>>(),
        "pump_junctions": manifold::pump_junctions().collect::<Vec<_>>(),
        "lower_connections": lower,
    }))
}

fn main() -> Result<()> {
    hsm_kernel::reads::begin();
    let (mut check, mut out) = (false, None);
    for arg in std::env::args().skip(1) {
        match arg.as_str() {
            "--check" => check = true,
            other if other.starts_with("--") => bail!("unknown option {other}"),
            other => out = Some(absolute(PathBuf::from(other))?),
        }
    }
    let root = absolute(".")?;
    let request = Request {
        out: out.unwrap_or_else(|| root.clone()),
        input: input(&root)?,
        write: !check,
        operation: if check { "check" } else { "document" }.into(),
        root,
    };
    let output = chart::run(&request)?;
    print!("{}", output.stdout);
    let status = output.exports.get("status").and_then(Value::as_i64).unwrap_or(1);
    ensure!(status == 0 || check, "the plumbing charts disagree with the machine");
    std::process::exit(status as i32)
}
