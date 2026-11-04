//! Installed-wiring scalar providers and composition.
#![recursion_limit = "512"]
use anyhow::{Context, Result, bail, ensure};
use serde::Deserialize;
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    io::{self, Write},
    path::{Path, PathBuf},
};
mod build;
mod bundles;
mod graph;
mod model;
mod readers;
mod routes;
mod scenes;
mod step;
mod terminals;
mod terminations;
#[allow(dead_code)]
#[path = "../../../../../hardware/wiring/installed/wire_route_samples.rs"]
mod wire_samples;
#[derive(Deserialize)]
struct Request {
    op: String,
    #[serde(default)]
    data: Value,
    root: PathBuf,
}
fn dispatch(request: &Request) -> Result<Value> {
    let data = &request.data;
    match request.op.as_str() {
        "stock" => model::stock(),
        "add" => Ok(json!(model::add(
            model::v(&data["a"])?,
            model::v(&data["b"])?
        ))),
        "sub" => Ok(json!(model::sub(
            model::v(&data["a"])?,
            model::v(&data["b"])?
        ))),
        "mul" => Ok(json!(model::mul(
            model::v(&data["a"])?,
            number(&data["t"])?
        ))),
        "dot" => Ok(json!(model::dot(
            model::v(&data["a"])?,
            model::v(&data["b"])?
        ))),
        "norm" => Ok(json!(model::norm(model::v(&data["a"])?))),
        "unit" => Ok(json!(model::unit(model::v(&data["a"])?))),
        "round_segments" => model::rounded(
            &data["points"],
            optional(data, "radius", 4.),
            boolean(data, "keep_collinear", false),
            optional(data, "endpoint_tangent_fraction", 0.44),
        ),
        "spline_segment" => model::spline(
            &data["points"],
            &data["tangents"],
            boolean(data, "chord_length", false),
        ),
        "spline_measure" => wire_samples::measure(data),
        "sampled_segments" => Ok(json!(model::sample(
            &data["segments"],
            optional(data, "step", 1.)
        )?)),
        "route_record" => model::record(data),
        "finish" => model::finish(data),
        "connections" | "graph_constants" | "owner" | "interfaces" => graph::request(request),
        op if op.starts_with("model_") || op == "file_digest" || op == "wire_numbers" => {
            readers::request(request)
        }
        op if op.starts_with("termination_") => terminations::request(request),
        op if op.starts_with("build_") => build::request(request),
        op if op.starts_with("step_") => step::request(request),
        op if op.starts_with("scene_") => scenes::request(request),
        op if op.starts_with("terminal_") => terminals::request(request),
        op if op.starts_with("bundle_") => bundles::request(request),
        op if op.starts_with("route_") || op.starts_with("retainer_") => routes::request(request),
        _ => bail!("unknown wiring operation {}", request.op),
    }
}
fn number(value: &Value) -> Result<f64> {
    value.as_f64().context("wiring numeric value")
}
fn string<'a>(value: &'a Value) -> Result<&'a str> {
    value.as_str().context("wiring text")
}
fn rows(value: &Value) -> Result<&Vec<Value>> {
    value.as_array().context("wiring rows")
}
fn optional(data: &Value, key: &str, default: f64) -> f64 {
    data.get(key).and_then(Value::as_f64).unwrap_or(default)
}
fn boolean(data: &Value, key: &str, default: bool) -> bool {
    data.get(key).and_then(Value::as_bool).unwrap_or(default)
}
fn load(root: &Path, path: &str) -> Result<Value> {
    Ok(serde_json::from_str(&std::fs::read_to_string(
        root.join(path),
    )?)?)
}
fn load_ordered(root: &Path, path: &str) -> Result<Vec<(String, Value)>> {
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
    let raw = std::fs::read_to_string(root.join(path))?;
    Ok(serde::Deserializer::deserialize_map(
        &mut serde_json::Deserializer::from_str(&raw),
        Ordered,
    )?)
}
fn py_round(value: f64, digits: i32) -> Result<f64> {
    Ok(hsm_documents::format_number(value, &format!(".{digits}f"))?.parse()?)
}
fn provider(query: Value) -> Result<Value> {
    {
        let mut output = io::stdout().lock();
        serde_json::to_writer(&mut output, &json!({"_hsm_callback":query}))?;
        writeln!(output)?;
        output.flush()?;
    }
    let mut line = String::new();
    ensure!(
        io::stdin().read_line(&mut line)? > 0,
        "raw provider closed its stream"
    );
    let reply: Value = serde_json::from_str(&line)?;
    if let Some(error) = reply.get("_hsm_callback_error") {
        bail!(
            "raw provider: {}",
            error.as_str().unwrap_or("unknown error")
        );
    }
    reply
        .get("_hsm_callback_result")
        .cloned()
        .context("raw provider reply")
}
fn get(base: &str, path: &str) -> Result<Value> {
    provider(json!({"kind":"get","base":base,"path":path}))
}
fn call(base: &str, path: &str, args: Value) -> Result<Value> {
    provider(json!({"kind":"get","base":base,"path":path,"args":args}))
}
fn main() -> Result<()> {
    let serve = std::env::args().nth(1).as_deref() == Some("--serve");
    loop {
        let mut line = String::new();
        if io::stdin().read_line(&mut line)? == 0 {
            break;
        }
        let result = serde_json::from_str::<Request>(&line)
            .context("wiring request")
            .and_then(|q| dispatch(&q));
        let response = match result {
            Ok(value) => value,
            Err(error) => json!({"error":format!("{error:#}")}),
        };
        let mut output = io::stdout().lock();
        serde_json::to_writer(&mut output, &response)?;
        writeln!(output)?;
        output.flush()?;
        if !serve {
            break;
        }
    }
    Ok(())
}
