//! The installed wiring's request: the conductors, terminations and jackets the installed-wires
//! program cuts, resolved against the machine's physical fine model.
//!
//! The routing is the assembly-docs wiring code, included here unchanged. Everything it asks its
//! host for is answered by `sources`, from the file or the plan that owns the value.
use anyhow::{Context, Result, bail, ensure};
use serde::Deserialize;
use serde_json::{Value, json};
use std::cell::RefCell;
use std::collections::{BTreeMap, BTreeSet};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::rc::Rc;

/// The request and review the routed wiring is written up as.
#[allow(dead_code, unused_imports)]
#[path = "../../../tools/hsm/assembly-docs/src/wiring/build.rs"]
mod build;
/// The shared cable jackets and looms, and the cores they carry.
#[allow(dead_code, unused_imports)]
#[path = "../../../tools/hsm/assembly-docs/src/wiring/bundles.rs"]
mod bundles;
/// The installed connection graph: which terminal each conductor joins to which.
#[allow(dead_code, unused_imports)]
#[path = "../../../tools/hsm/assembly-docs/src/wiring/graph.rs"]
mod graph;
/// The stock, the rounded and spline segments, and the route records.
#[allow(dead_code, unused_imports)]
#[path = "../../../tools/hsm/assembly-docs/src/wiring/model.rs"]
mod model;
/// The fine model's bodies grouped by name, reference bounds and the conductors' stock.
#[allow(dead_code, unused_imports)]
#[path = "../../../tools/hsm/assembly-docs/src/wiring/readers.rs"]
mod readers;
/// Each conductor's routed course between its two terminals.
#[allow(dead_code, unused_imports)]
#[path = "../../../tools/hsm/assembly-docs/src/wiring/routes.rs"]
mod routes;
/// STEP records of the wiring, which the request leaves out.
#[allow(dead_code, unused_imports)]
#[path = "../../../tools/hsm/assembly-docs/src/wiring/step.rs"]
mod step;
/// Every terminal's point and outward direction on the installed bodies.
#[allow(dead_code, unused_imports)]
#[path = "../../../tools/hsm/assembly-docs/src/wiring/terminals.rs"]
mod terminals;
/// The connector housings, final joins, fuse leads and earth ring at the terminals.
#[allow(dead_code, unused_imports)]
#[path = "../../../tools/hsm/assembly-docs/src/wiring/terminations.rs"]
mod terminations;
/// Lengths and bend samples of the spline segments.
#[allow(dead_code, unused_imports)]
#[path = "../../wiring/installed/wire_route_samples.rs"]
mod wire_samples;

#[path = "wiring/corridors.rs"]
mod corridors;
#[path = "wiring/measure.rs"]
mod measure;
#[path = "wiring/sources.rs"]
mod sources;

/// The name the installed-wires program writes its STEP, model and payload under.
const FILE_STEM: &str = "enclosure-wiring";

/// The request the installed-wires program cuts the machine's wiring from: every conductor's
/// routed segments and every termination and jacket, resolved against the bodies of the
/// physical fine model at `physical_model` as the plan `spec` placed them.
pub fn wiring_request(root: &Path, spec: &Value, physical_model: &Path) -> Result<Value> {
    let _host = Host::enter(sources::Sources::read(root, spec)?);
    let rows = measure::summaries(physical_model, None, &solids_read())?;
    let grouped = readers::request(&Request {
        op: "model_bodies".into(),
        data: json!({"rows": rows, "grid": hsm_kernel::GRID}),
        root: root.into(),
    })?;
    let mut scene = json!({});
    for (name, row) in grouped.as_object().context("the physical model's bodies")? {
        scene[name] = row[0].clone();
    }
    let attachments = terminals::init(&scene)?;
    let attachments = terminals::request(&Request {
        op: "terminal_resolve".into(),
        data: json!({"state": attachments}),
        root: root.into(),
    })?;
    let (mut numbers, _review) = build::numeric(root, &attachments)?;
    numbers["file_stem"] = json!(FILE_STEM);
    Ok(numbers)
}

/// The bodies whose separate solids the terminals read, under both names the model may give
/// them: the valves' and coils' spade tabs and the compressor's power cover.
fn solids_read() -> BTreeSet<String> {
    let mut hosts = vec!["compressor".to_owned(), "valve-v-a".into(), "valve-v-b".into(), "vk-solenoid".into()];
    hosts.extend("cdefghij".chars().map(|c| format!("coil-v-{c}")));
    hosts.iter().flat_map(|h| [h.clone(), format!("cold-core/{h}")]).collect()
}

/// One operation of the included wiring code, as its own dispatchers take it.
#[derive(Deserialize)]
struct Request {
    op: String,
    #[serde(default)]
    data: Value,
    root: PathBuf,
}

thread_local! {
    /// The sources the included wiring code is answered from while a request is built.
    static SOURCES: RefCell<Option<Rc<sources::Sources>>> = const { RefCell::new(None) };
}

/// Holds this thread's sources for the included wiring code until it is dropped.
struct Host;

impl Host {
    /// Answers the included wiring code from `sources` until the returned guard drops.
    fn enter(sources: sources::Sources) -> Self {
        SOURCES.with(|slot| *slot.borrow_mut() = Some(Rc::new(sources)));
        Host
    }
}

impl Drop for Host {
    /// Leaves no sources behind for a later request to read by mistake.
    fn drop(&mut self) {
        SOURCES.with(|slot| *slot.borrow_mut() = None);
    }
}

/// The sources the current request is built from.
fn current() -> Result<Rc<sources::Sources>> {
    SOURCES
        .with(|slot| slot.borrow().clone())
        .context("the wiring's sources are read only while its request is built")
}

/// Answers one of the included code's provider queries: a measurement, a reference's bounds,
/// a STEP's checkout name, a fixed passage set.
fn provider(query: Value) -> Result<Value> {
    current()?.answer(&query)
}

/// A value the included code names by module and attribute, such as `ea` `PSU_STEP`.
fn get(base: &str, path: &str) -> Result<Value> {
    current()?.value(base, path, None)
}

/// A value the included code computes by module function, such as `above_core` `cap_lid_pose`.
fn call(base: &str, path: &str, args: Value) -> Result<Value> {
    current()?.value(base, path, Some(&args))
}

/// A number of the included code's records.
fn number(value: &Value) -> Result<f64> {
    value.as_f64().context("wiring numeric value")
}

/// A text of the included code's records.
fn string(value: &Value) -> Result<&str> {
    value.as_str().context("wiring text")
}

/// The rows of one of the included code's lists.
fn rows(value: &Value) -> Result<&Vec<Value>> {
    value.as_array().context("wiring rows")
}

/// A record's number at `key`, or `default` where it states none.
fn optional(data: &Value, key: &str, default: f64) -> f64 {
    data.get(key).and_then(Value::as_f64).unwrap_or(default)
}

/// A record's flag at `key`, or `default` where it states none.
fn boolean(data: &Value, key: &str, default: bool) -> bool {
    data.get(key).and_then(Value::as_bool).unwrap_or(default)
}

/// A JSON file of the checkout, by its path under `root`.
fn load(root: &Path, path: &str) -> Result<Value> {
    crate::design::read(root.join(path))
}

/// A JSON object of the checkout as its entries in written order.
fn load_ordered(root: &Path, path: &str) -> Result<Vec<(String, Value)>> {
    /// Reads a JSON object's entries in the order they are written.
    struct Ordered;
    impl<'de> serde::de::Visitor<'de> for Ordered {
        type Value = Vec<(String, Value)>;
        fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
            f.write_str("ordered source object")
        }
        fn visit_map<A: serde::de::MapAccess<'de>>(
            self,
            mut map: A,
        ) -> std::result::Result<Self::Value, A::Error> {
            let mut out = Vec::new();
            while let Some(pair) = map.next_entry::<String, Value>()? {
                out.push(pair);
            }
            Ok(out)
        }
    }
    let path = root.join(path);
    let bytes = std::fs::read(&path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(&path, &bytes);
    Ok(serde::Deserializer::deserialize_map(
        &mut serde_json::Deserializer::from_slice(&bytes),
        Ordered,
    )?)
}

/// `value` rounded to `digits` places half to even, as the route records state their lengths.
fn py_round(value: f64, digits: i32) -> Result<f64> {
    Ok(hsm_documents::format_number(value, &format!(".{digits}f"))?.parse()?)
}
