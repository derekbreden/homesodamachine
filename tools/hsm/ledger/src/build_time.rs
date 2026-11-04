use crate::shared::*;
use anyhow::{Result, bail};
use hsm_documents::Variables;
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    path::Path,
};

const WINDOW: usize = 5;
const BAND: f64 = 0.10;

fn marker(generator: &str) -> String {
    format!(
        "BT_{}",
        Path::new(generator)
            .file_stem()
            .unwrap_or_default()
            .to_string_lossy()
            .trim_matches('_')
            .to_uppercase()
    )
}
fn seconds(value: f64) -> String {
    if value < 10. {
        fmt(value, ".1f")
    } else {
        fmt(value.round_ties_even(), ".0f")
    }
}
fn settle(standing: Option<&str>, got: f64) -> String {
    if let Some((text, was)) = standing.and_then(|s| s.parse::<f64>().ok().map(|v| (s, v))) {
        if was != 0. && (got - was).abs() / was < BAND {
            return text.to_owned();
        }
    }
    seconds(got)
}
fn rows(text: &str) -> Vec<(String, String, Option<String>)> {
    let mut rows = vec![];
    for line in text.lines().filter(|s| s.starts_with('|')) {
        let c = cells(line);
        if c.len() < 3 || separator(&c) {
            continue;
        }
        if let Some(caps) = re(r"\((/[^)]+\.py)\)").captures(&c[0]) {
            let generator = caps[1].trim_start_matches('/').to_owned();
            let mark = marker(&generator);
            let standing = re(&format!(r"\[([^\]]*)\]\({}\)", regex::escape(&mark)))
                .captures(line)
                .map(|c| c[1].to_owned());
            rows.push((generator, mark, standing));
        }
    }
    rows
}
fn held(data: &Value) -> BTreeMap<String, f64> {
    data.as_object()
        .into_iter()
        .flatten()
        .filter_map(|(k, v)| {
            let min = v
                .as_array()?
                .iter()
                .filter_map(|v| num(v).ok())
                .reduce(f64::min)?;
            Some((k.clone(), min))
        })
        .collect()
}
fn figures(text: &str, data: &Value) -> (Variables, Vec<String>) {
    let seen = held(data);
    let mut vars = Variables::from([
        ("BT_WINDOW".into(), WINDOW.to_string()),
        ("BT_BAND".into(), "10".into()),
    ]);
    let mut carried = BTreeSet::new();
    for (generator, mk, standing) in rows(text) {
        vars.insert(
            mk,
            seen.get(&generator)
                .map(|n| settle(standing.as_deref(), *n))
                .unwrap_or_else(|| standing.unwrap_or_else(|| "—".into())),
        );
        carried.insert(generator);
    }
    let slowest = carried
        .iter()
        .filter_map(|g| seen.get(g))
        .copied()
        .fold(0., f64::max);
    let orphans = seen
        .iter()
        .filter(|(g, v)| !carried.contains(*g) && **v > slowest)
        .map(|(g, _)| g.clone())
        .collect();
    (vars, orphans)
}

pub fn dispatch(op: &str, request: &Value, context: &mut Context) -> Result<Value> {
    if op == "marker" {
        return Ok(json!(marker(arg(request, "gen")?)));
    }
    if op == "fmt" {
        return Ok(json!(seconds(num(&request["seconds"])?)));
    }
    if op == "settle" {
        return Ok(json!(settle(
            request["standing"].as_str(),
            num(&request["seconds"])?
        )));
    }
    let samples = context.path(
        request,
        "samples",
        "hardware/ledger/.build-time.samples.json",
    );
    if op == "record" {
        let mut data = context
            .json(&samples)
            .ok()
            .filter(|v| v.is_object())
            .unwrap_or_else(|| json!({}));
        let label = arg(request, "label")?;
        let mut runs = data[label].as_array().cloned().unwrap_or_default();
        if runs.len() >= WINDOW {
            runs.drain(..runs.len() - (WINDOW - 1));
        }
        runs.push(json!(round(num(&request["seconds"])?, 2)));
        data[label] = json!(runs);
        if let Ok(mut text) = serde_json::to_string_pretty(&data) {
            text.push('\n');
            let _ = context.write(&samples, text.as_bytes());
        }
        return Ok(Value::Null);
    }
    let data = context
        .json(&samples)
        .ok()
        .filter(|v| v.is_object())
        .unwrap_or_else(|| json!({}));
    if op == "held" {
        return Ok(json!(held(&data)));
    }
    let path = context.path(request, "build_time", "hardware/ledger/build-time.md");
    let text = context.read(&path)?;
    if op == "rows" {
        return Ok(json!(rows(&text)));
    }
    let (vars, orphans) = figures(&text, &data);
    if op == "figures" {
        return Ok(json!([vars, orphans]));
    }
    if op != "main" {
        bail!("unknown build-time operation: {op}")
    }
    let seen = held(&data);
    if request["check"].as_bool().unwrap_or(false) {
        if !orphans.is_empty() {
            let mut out = "generators with readings and no row in build-time.md:\n".to_owned();
            for generator in orphans {
                out += &format!("  {generator}  {} s\n", seconds(seen[&generator]));
            }
            return Ok(main_result(1, out));
        }
        let stale = stale(&text, &vars);
        return Ok(if stale.is_empty() {
            main_result(0, "build-time.md figures ✓\n".into())
        } else {
            main_result(
                1,
                format!(
                    "build-time.md markers are stale — run _build_time.py:\n{}\n",
                    stale.join("\n")
                ),
            )
        });
    }
    context.substitute(&path, &vars, "/hardware/scripts/_build_time.py")?;
    let mut out = String::new();
    for (generator, mk, _) in rows(&text) {
        let suffix = if seen.contains_key(&generator) {
            format!(
                "   (window min of {})",
                data[&generator].as_array().map_or(0, Vec::len)
            )
        } else {
            String::new()
        };
        out += &format!("  {:>5} s  {generator}{suffix}\n", vars[&mk]);
    }
    if !orphans.is_empty() {
        out += "\nreadings with no row:\n";
        for generator in orphans {
            out += &format!("  {generator}  {} s\n", seconds(seen[&generator]));
        }
    }
    Ok(main_result(0, out))
}
