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
use std::collections::{BTreeMap, BTreeSet};
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
    machine: Machine,
    write: bool,
    operation: String,
}

/// What a chart run found and says, and the charts it wrote.
#[derive(Default)]
struct Output {
    status: i64,
    stdout: String,
    maintained: Vec<String>,
}

/// Each name and the names it holds.
type Sets = BTreeMap<String, BTreeSet<String>>;

/// One run the installed machine draws, as its facts state it.
#[derive(Deserialize)]
struct Run {
    id: String,
    frm: String,
    to: String,
    #[serde(default = "drawn")]
    made: String,
    length: Option<f64>,
    corners: u64,
    #[serde(default = "complete")]
    status: String,
    #[serde(default)]
    missing_native_routes: Vec<String>,
    #[serde(default)]
    missing_fittings: Vec<String>,
}

fn drawn() -> String {
    "drawn".into()
}
fn complete() -> String {
    "complete".into()
}

/// One of the manifold's connections, how it is made and its tube's length and corners.
struct Interior {
    run: u32,
    from: String,
    to: String,
    made: &'static str,
    length: f64,
    corners: u64,
}

/// What the charts are checked against and labelled from: the machine's runs, the manifold's
/// connections and mouths, its valves, tees, pumps and limbs.
struct Machine {
    runs: Vec<Run>,
    interior: Vec<Interior>,
    mouths: Vec<(String, String)>,
    valves: Vec<String>,
    stations: Vec<(String, bool)>,
    pumps: Vec<String>,
    limbs: Sets,
    purchased_tees: usize,
    pump_tees: usize,
}

/// A text file of the tree, read whole and named to the build as read.
fn read_text(path: &Path) -> Result<String> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(path, &bytes);
    Ok(String::from_utf8(bytes)?)
}

fn fmt(number: f64, spec: &str) -> Result<String> {
    hsm_documents::format_number(number, spec)
}

/// How one of the manifold's connections is made, and its tube's length and corners.
fn interior(c: &manifold::Connection) -> (&'static str, f64, u64) {
    let tube = |name: String| manifold::length(manifold::tube(&name));
    match c.made {
        Made::Turn => ("turn", tube(format!("turn-fluid-{}", c.run)) + tube(format!("step-fluid-{}", c.run)), 3),
        Made::Crossbar | Made::Butt => ("butt", 0.0, 0),
        Made::LowerReturn { .. } => {
            let arcs = manifold::tube(&format!("tube-fluid-{}", c.run)).path.iter().filter(|s| matches!(s, Seg::Arc(_))).count();
            ("elbows", manifold::lower_return_cut(c.run), arcs as u64)
        }
        Made::Upper { .. } => ("straight", tube(format!("tube-fluid-{}", c.run)), 0),
        Made::PumpTube { .. } => ("pump-dock", 0.0, 0),
    }
}

/// The machine as the charts take it: its runs from the installed machine's facts, and the
/// manifold's connections, mouths, stations and limbs from its numbers.
fn machine(root: &Path) -> Result<Machine> {
    #[derive(Deserialize)]
    struct Facts {
        runs: Vec<Run>,
    }
    let facts: Facts = serde_json::from_str(&read_text(&root.join(FACTS))?)?;
    let interior = CONNECTIONS
        .iter()
        .map(|c| {
            let (made, length, corners) = interior(c);
            Interior { run: c.run, from: c.from.into(), to: c.to.into(), made, length, corners }
        })
        .collect();
    let stations: Vec<(String, bool)> = manifold::stations().map(|(n, _, fold)| (n.to_owned(), fold)).collect();
    let mut valves: Vec<String> = stations.iter().map(|(n, _)| n.clone()).filter(|n| n.starts_with("V-")).collect();
    valves.sort();
    Ok(Machine {
        runs: facts.runs,
        interior,
        mouths: MOUTHS.iter().map(|m| (m.run.to_owned(), m.port.to_owned())).collect(),
        valves,
        stations,
        pumps: PUMPS.iter().map(|p| p.to_string()).collect(),
        limbs: LIMBS.iter().map(|l| (l.name.to_owned(), l.chain.iter().map(|n| n.to_string()).collect())).collect(),
        purchased_tees: manifold::purchased_tees().count(),
        pump_tees: manifold::pump_junctions().count(),
    })
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
        machine: machine(&root)?,
        write: !check,
        operation: if check { "check" } else { "document" }.into(),
        root,
    };
    let output = chart::run(&request)?;
    print!("{}", output.stdout);
    ensure!(output.status == 0 || check, "the plumbing charts disagree with the machine");
    std::process::exit(output.status as i32)
}
