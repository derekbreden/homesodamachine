//! Scalar source readers, placement descriptions and assembly reports.
use anyhow::{Context, Result, bail};
use serde_json::{Value, json};
use std::io::{BufRead, Write};

mod archive;
mod box_spec;
mod equipment;
mod equipment_ports;
mod queries;
mod reporting;
mod source;

fn answer(request: &Value) -> Result<Value> {
    let op = request["op"]
        .as_str()
        .context("machine-data request needs op")?;
    match op {
        "model_source" => source::model(request),
        op if op.starts_with("equipment_") => equipment::request(request),
        "query_groups" => queries::groups(request),
        "query_box_plan" => queries::box_plan(request),
        "query_box_result" => queries::box_result(request),
        "archive_metadata" => archive::metadata(request),
        "read_json" => {
            let path = request["path"].as_str().context("JSON reader path")?;
            let result = std::fs::read(path)
                .context("JSON reader file")
                .and_then(|raw| serde_json::from_slice(&raw).context("JSON reader content"));
            if request["optional"] == true {
                Ok(result.unwrap_or_else(|_| json!({})))
            } else {
                result
            }
        }
        "box_validate" => box_spec::validate(request),
        "box_document" => box_spec::document(request),
        "same_document" => Ok(json!(box_spec::same(&request["left"], &request["right"]))),
        "facts_sources" => Ok(json!(source_names(&request["graph"]))),
        "report_bounds" => reporting::bounds(&request["spec"]),
        "report_ports" => reporting::ports(&request["frame"]),
        "report_routes" => reporting::route_rows(&request["metadata"]),
        "report_run_length" => Ok(json!(reporting::run_length(&request["row"])?)),
        "report_route_metadata" => reporting::route_metadata(request),
        "report_scene" => reporting::scene(request),
        "report_trays" => reporting::trays(request),
        "report_facts" => reporting::facts(request),
        _ => bail!("unknown machine-data operation {op:?}"),
    }
}

fn source_names(graph: &Value) -> Vec<String> {
    use std::collections::BTreeSet;
    const GENERATOR: &str = "hardware/manifold-layout/enclosure_assembly.py";
    let Some(entry) = graph.get(GENERATOR).filter(|v| !v.is_null()) else {
        return vec![];
    };
    let mut derived = BTreeSet::new();
    if let Some(graph) = graph.as_object() {
        for entry in graph.values() {
            for key in ["writes", "rewritten"] {
                for name in entry
                    .get(key)
                    .and_then(Value::as_array)
                    .into_iter()
                    .flatten()
                {
                    if let Some(name) = name.as_str() {
                        derived.insert(name);
                    }
                }
            }
        }
    }
    entry
        .get("reads")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
        .filter(|name| *name != "tools/bazel/graph.json" && !derived.contains(name))
        .map(str::to_owned)
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect()
}

fn main() -> Result<()> {
    if std::env::args().nth(1).as_deref() != Some("--serve") {
        bail!("usage: machine-data --serve");
    }
    let stdin = std::io::stdin();
    let mut stdout = std::io::BufWriter::new(std::io::stdout().lock());
    for line in stdin.lock().lines() {
        let line = line?;
        let result = serde_json::from_str(&line)
            .context("machine-data JSON request")
            .and_then(|v| answer(&v));
        let value = result.unwrap_or_else(|error| json!({"error":format!("{error:#}")}));
        serde_json::to_writer(&mut stdout, &value)?;
        writeln!(stdout)?;
        stdout.flush()?;
    }
    Ok(())
}
