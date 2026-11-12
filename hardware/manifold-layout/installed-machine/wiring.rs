//! The installed wiring's request: the conductors, terminations and jackets the installed-wires
//! program cuts, resolved against the machine's physical fine model.
//!
//! The routing is the assembly-docs wiring code, included here. `sources` gives it each value
//! from the file or the plan that owns it.
use anyhow::{Context, Result, bail, ensure};
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

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
/// Every terminal's point and outward direction on the installed bodies.
#[allow(dead_code, unused_imports)]
#[path = "../../../tools/hsm/assembly-docs/src/wiring/terminals.rs"]
mod terminals;
/// The connector housings, final joins, fuse leads and earth ring at the terminals.
#[allow(dead_code, unused_imports)]
#[path = "../../../tools/hsm/assembly-docs/src/wiring/terminations.rs"]
mod terminations;
/// The request the installed-wires program reads: wires, terminations and jackets.
#[allow(dead_code)]
#[path = "../../wiring/installed/wire_request.rs"]
mod wire_request;
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
pub fn wiring_request(
    root: &Path,
    spec: &Value,
    physical_model: &Path,
    cache: &mut crate::cache::Cache,
) -> Result<Value> {
    let sources = sources::Sources::read(root, spec)?;
    let recipe = json!({"plan":spec,"physical_model":physical_model,
        "fits":{"slip":hsm_enclosure_numbers::catalog::slip(),"running":hsm_enclosure_numbers::catalog::running(),
            "supported":hsm_enclosure_numbers::catalog::supported(),"m5_thread_pass":hsm_enclosure_numbers::catalog::m5_thread_pass_dia()}});
    let attachments = cache.run("wire attachments", &recipe, &[], || {
        Ok(serde_json::to_value(attachments(&sources, root, physical_model)?)?)
    })?;
    let attachments: terminals::State =
        serde_json::from_value(attachments).context("the retained wire attachments")?;
    let mut numbers = build::numeric_only(&sources, root, &attachments)?;
    numbers.file_stem = Some(FILE_STEM.into());
    Ok(serde_json::to_value(numbers)?)
}

/// The request the wiring is cut from and the review of it, resolved against the placed
/// physical model.
pub fn manual_request(root: &Path, spec: &Value, physical_model: &Path) -> Result<(Value, Value)> {
    let sources = sources::Sources::read(root, spec)?;
    let (numbers, review) = build::numeric(&sources, root, &attachments(&sources, root, physical_model)?)?;
    Ok((serde_json::to_value(numbers)?, review))
}

/// Every terminal, reference frame, fuse lead and cable passage of the wiring, resolved onto
/// the bodies of the physical fine model at `physical_model`.
fn attachments(
    sources: &sources::Sources,
    root: &Path,
    physical_model: &Path,
) -> Result<terminals::State> {
    let rows = measure::summaries(physical_model, None, &solids_read())?;
    let grouped = readers::bodies(&Value::Array(rows), Some(hsm_kernel::GRID))?;
    let mut scene = BTreeMap::new();
    for (name, row) in grouped.as_object().context("the physical model's bodies")? {
        let body = serde_json::from_value(row[0].clone())
            .with_context(|| format!("the installed body {name}"))?;
        scene.insert(name.clone(), body);
    }
    terminals::resolve(sources, terminals::init(scene), root)
}

/// The bodies whose separate solids the terminals read, under both names the model may give
/// them: the valves' and coils' spade tabs and the compressor's power cover.
fn solids_read() -> BTreeSet<String> {
    let mut hosts = vec![
        "compressor".to_owned(),
        "valve-v-a".into(),
        "valve-v-b".into(),
        "vk-solenoid".into(),
    ];
    hosts.extend("cdefghij".chars().map(|c| format!("coil-v-{c}")));
    hosts
        .iter()
        .flat_map(|h| [h.clone(), format!("cold-core/{h}")])
        .collect()
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

/// A JSON file of the checkout, by its path under `root`.
fn load(root: &Path, path: &str) -> Result<Value> {
    crate::design::read(root.join(path))
}

/// A JSON object of the checkout as its entries in written order.
fn load_ordered<T: serde::de::DeserializeOwned>(root: &Path, path: &str) -> Result<Vec<(String, T)>> {
    /// Reads a JSON object's entries in the order they are written.
    struct Ordered<T>(std::marker::PhantomData<T>);
    impl<'de, T: serde::de::DeserializeOwned> serde::de::Visitor<'de> for Ordered<T> {
        type Value = Vec<(String, T)>;
        fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
            f.write_str("ordered source object")
        }
        fn visit_map<A: serde::de::MapAccess<'de>>(
            self,
            mut map: A,
        ) -> std::result::Result<Self::Value, A::Error> {
            let mut out = Vec::new();
            while let Some(pair) = map.next_entry::<String, T>()? {
                out.push(pair);
            }
            Ok(out)
        }
    }
    let path = root.join(path);
    let bytes = std::fs::read(&path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(&path, &bytes);
    serde::Deserializer::deserialize_map(
        &mut serde_json::Deserializer::from_slice(&bytes),
        Ordered(std::marker::PhantomData),
    )
    .with_context(|| format!("reading {}", path.display()))
}

/// `value` rounded to `digits` decimal places, as the route records state their lengths.
fn places(value: f64, digits: i32) -> Result<f64> {
    Ok(hsm_documents::format_number(value, &format!(".{digits}f"))?.parse()?)
}
