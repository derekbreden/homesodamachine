#![recursion_limit = "512"]
//! Scalar source readers, placement descriptions and assembly reports.
use anyhow::{Context, Result, bail};
use serde_json::{Value, json};
use std::io::Write;

mod archive;
mod box_spec;
mod equipment;
mod equipment_ports;
mod queries;
mod reporting;
mod source;
mod io;

fn answer(request: &Value) -> Result<Value> {
    let op = request["op"]
        .as_str()
        .context("machine-data request needs op")?;
    match op {
        "write_json"|"json_text" => io::request(request),
        "model_source" => source::model(request),
        op if op.starts_with("equipment_") => equipment::request(request),
        "query_groups" => queries::groups(request),
        "query_box_plan" => queries::box_plan(request),
        "query_box_result" => queries::box_result(request),
        "archive_metadata" => archive::metadata(request),
        "archive_entry" => archive::entry(request),
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
        "report_bounds" => reporting::bounds(&request["spec"]),
        "report_ports" => reporting::ports(&request["frame"]),
        "report_routes" => reporting::route_rows(&request["metadata"]),
        "report_run_length" => Ok(json!(reporting::run_length(&request["row"])?)),
        "report_scene" => reporting::scene(request),
        "report_facts" => reporting::facts(request),
        _ => bail!("unknown machine-data operation {op:?}"),
    }
}

fn main() -> Result<()> {
    if std::env::args().nth(1).as_deref() != Some("--serve") {
        bail!("usage: machine-data --serve");
    }
    let stdin = std::io::stdin();
    loop {
        let mut line = String::new();
        if stdin.read_line(&mut line)? == 0 { break; }
        let result = serde_json::from_str(&line).context("machine-data JSON request").and_then(|v| answer(&v));
        let value = result.unwrap_or_else(|error| json!({"error":format!("{error:#}")}));
        let mut stdout = std::io::stdout().lock();
        serde_json::to_writer(&mut stdout, &value)?;
        writeln!(stdout)?;
        stdout.flush()?;
    }
    Ok(())
}
