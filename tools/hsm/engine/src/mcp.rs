//! Newline-delimited JSON-RPC over stdio. Geometry stays in the shared daemon.
use crate::{Client, scene_path, service::Request};
use anyhow::{Context, Result, bail};
use serde_json::{Value, json};
use std::io::{self, BufRead, Write};

fn tools() -> Vec<Value> {
    let definitions = [
        (
            "where",
            "Find solids by name or #index and read world bounds and dimensions.",
            json!({"pattern":{"type":"string"}}),
            vec![],
        ),
        (
            "gap",
            "Triangle distance, closest points and solid clearance between two unique solids, in mm.",
            json!({"a":{"type":"string"},"b":{"type":"string"}}),
            vec!["a", "b"],
        ),
        (
            "overlap",
            "Manifold intersection volume in mm^3, including containment. Invalid solids return an error.",
            json!({"a":{"type":"string"},"b":{"type":"string"}}),
            vec!["a", "b"],
        ),
        (
            "move",
            "Test a translation in world mm against the scene, without changing any part.",
            json!({"part":{"type":"string"},"by":{"type":"array","items":{"type":"number"},"minItems":3,"maxItems":3},"against":{"type":"string"},"min_volume":{"type":"number","minimum":0,"default":1e-6}}),
            vec!["part", "by"],
        ),
        (
            "section",
            "Triangle segments and viewer face IDs where normal.dot(point) = offset, in mm.",
            json!({"part":{"type":"string"},"normal":{"type":"array","items":{"type":"number"},"minItems":3,"maxItems":3},"offset":{"type":"number"}}),
            vec!["part", "normal", "offset"],
        ),
        (
            "ray",
            "Nearest scene hit with viewer triangle and face IDs; direction is normalized.",
            json!({"origin":{"type":"array","items":{"type":"number"},"minItems":3,"maxItems":3},"direction":{"type":"array","items":{"type":"number"},"minItems":3,"maxItems":3},"max_distance":{"type":"number","exclusiveMinimum":0}}),
            vec!["origin", "direction"],
        ),
    ];
    definitions.into_iter().map(|(name, description, mut props, required)| {
        props["scene"] = json!({"type":"string","description":"machine (default), faucet, enclosure, or a local .step.mesh path"});
        props["root"] = json!({"type":"string","description":"Absolute checkout/worktree root"});
        json!({"name":format!("hsm_{name}"),"description":description,
            "inputSchema":{"type":"object","properties":props,"required":required,"additionalProperties":false},
            "annotations":{"readOnlyHint":true,"openWorldHint":false}})
    }).collect()
}

fn call(client: &Client, params: &Value) -> Result<Value> {
    let name = params["name"].as_str().context("missing tool name")?;
    let op = name.strip_prefix("hsm_").context("unknown tool")?;
    if !["where", "gap", "overlap", "move", "section", "ray"].contains(&op) {
        bail!("unknown tool {name}");
    }
    let mut arguments = params.get("arguments").cloned().unwrap_or(json!({}));
    let arguments = arguments
        .as_object_mut()
        .context("arguments must be an object")?;
    let root = arguments
        .remove("root")
        .map(|v| {
            v.as_str()
                .map(std::path::PathBuf::from)
                .context("root must be a string")
        })
        .transpose()?
        .unwrap_or_else(|| client.root.clone());
    let scene = arguments
        .remove("scene")
        .map(|v| {
            v.as_str()
                .map(str::to_owned)
                .context("scene must be a string")
        })
        .transpose()?
        .unwrap_or_else(|| client.scene.clone());
    arguments.insert("op".into(), json!(op));
    arguments.insert("scene".into(), json!(scene_path(&root, &scene)));
    let request: Request = serde_json::from_value(json!(arguments))?;
    let result = client.call(&request)?;
    Ok(
        json!({"content":[{"type":"text","text":serde_json::to_string(&result)?}],
        "structuredContent":result,"isError":result["ok"] != true}),
    )
}

pub fn serve(client: &Client) -> Result<()> {
    let mut output = io::stdout().lock();
    for line in io::stdin().lock().lines() {
        let line = line?;
        let message: Value = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(e) => {
                writeln!(
                    output,
                    "{}",
                    json!({"jsonrpc":"2.0","id":null,"error":{"code":-32700,"message":e.to_string()}})
                )?;
                output.flush()?;
                continue;
            }
        };
        let Some(id) = message.get("id") else {
            continue;
        };
        let response = match message["method"].as_str() {
            Some("initialize") => Ok(
                json!({"protocolVersion":"2024-11-05","capabilities":{"tools":{"listChanged":false}},
                "serverInfo":{"name":"hsm","version":env!("CARGO_PKG_VERSION")}}),
            ),
            Some("ping") => Ok(json!({})),
            Some("tools/list") => Ok(json!({"tools":tools()})),
            Some("tools/call") => match call(client, &message["params"]) {
                Ok(v) => Ok(v),
                Err(e) => {
                    Ok(json!({"content":[{"type":"text","text":format!("{e:#}")}],"isError":true}))
                }
            },
            _ => Err(json!({"code":-32601,"message":"method not found"})),
        };
        let response = match response {
            Ok(result) => json!({"jsonrpc":"2.0","id":id,"result":result}),
            Err(error) => json!({"jsonrpc":"2.0","id":id,"error":error}),
        };
        writeln!(output, "{response}")?;
        output.flush()?;
    }
    Ok(())
}
