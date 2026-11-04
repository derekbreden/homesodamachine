use crate::shared::*;
use anyhow::{Context as _, Result, bail};
use hsm_documents::Variables;
use serde_json::{Value, json};
use std::collections::BTreeSet;

fn definitions() -> Value {
    serde_json::from_str(include_str!("../catalog/tools.json")).expect("tool declarations")
}
fn load(text: &str) -> Vec<Value> {
    let statuses = [
        "ACQUIRED",
        "ON-ORDER",
        "MISSING",
        "CANCELLED",
        "NOT NEEDED",
        "alt option",
    ];
    let mut rows = vec![];
    let mut sec: Option<String> = None;
    for line in text.lines() {
        if line.starts_with("## ") {
            sec = section(line).map(|n| n.to_string());
            continue;
        }
        if !line.starts_with('|') {
            continue;
        }
        let c: Vec<_> = line
            .trim()
            .trim_matches('|')
            .split('|')
            .map(str::trim)
            .collect();
        if c.len() < 3
            || c.iter()
                .all(|s| s.chars().all(|c| matches!(c, '-' | ':' | ' ')))
        {
            continue;
        }
        let Some(si) = c
            .iter()
            .rposition(|cell| statuses.iter().any(|status| cell.contains(status)))
        else {
            continue;
        };
        let Some(di) = (0..si).rev().find(|i| c[*i].contains('$')) else {
            continue;
        };
        let Some(m) = re(r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)").captures(c[di]) else {
            continue;
        };
        let mut cost: f64 = m[1].replace(',', "").parse().unwrap();
        if c[di].split_whitespace().last() == Some("ea") && di > 0 {
            if let Some(q) = re(r"^\s*([0-9]+)")
                .captures(c[di - 1])
                .and_then(|c| c[1].parse::<i64>().ok())
                .filter(|v| *v != 0)
            {
                cost *= q as f64;
            }
        }
        let asins: BTreeSet<_> = re(r"B0[A-Z0-9]{8}")
            .find_iter(line)
            .map(|m| m.as_str().to_owned())
            .collect();
        rows.push(json!({"section":sec,"text":line,"cost":cost,"status":c[si],"asins":asins}));
    }
    rows
}
fn pick<'a>(matches: Vec<&'a Value>, label: &str) -> Result<f64> {
    if matches.len() != 1 {
        bail!("  !! {label}: expected 1 line, found {}", matches.len())
    }
    num(&matches[0]["cost"])
}
fn resolve(spec: &Value, rows: &[Value]) -> Result<f64> {
    let (kind, value) = spec
        .as_object()
        .context("tool resolver object")?
        .iter()
        .next()
        .context("empty resolver")?;
    match kind.as_str() {
        "FIXED" => num(value),
        "sum" | "A2" => value
            .as_array()
            .context("resolver list")?
            .iter()
            .map(|v| {
                resolve(
                    &if kind == "A2" {
                        json!({"A":v})
                    } else {
                        v.clone()
                    },
                    rows,
                )
            })
            .sum(),
        "divide" => Ok(resolve(&value[0], rows)? / num(&value[1])?),
        "A" | "AN" => {
            let matches: Vec<_> = rows
                .iter()
                .filter(|r| r["asins"].as_array().is_some_and(|a| a.contains(value)))
                .collect();
            if kind == "A" {
                pick(matches, value.as_str().unwrap_or(""))
            } else {
                matches.iter().map(|r| num(&r["cost"])).sum()
            }
        }
        "line" => {
            let matches = rows
                .iter()
                .filter(|r| {
                    ["order", "contains", "section", "status"]
                        .iter()
                        .all(|key| {
                            let Some(s) = value[key].as_str().filter(|s| !s.is_empty()) else {
                                return true;
                            };
                            let field = match *key {
                                "section" => "section",
                                "status" => "status",
                                _ => "text",
                            };
                            let text = r[field].as_str().unwrap_or("");
                            if *key == "section" {
                                text == s
                            } else {
                                text.contains(s)
                            }
                        })
                })
                .collect();
            pick(
                matches,
                value["contains"]
                    .as_str()
                    .or(value["order"].as_str())
                    .unwrap_or("None"),
            )
        }
        _ => bail!("unknown tool resolver: {kind}"),
    }
}
fn compute(rows: &[Value]) -> Result<Vec<Value>> {
    definitions()
        .as_array()
        .unwrap()
        .iter()
        .map(|tool| {
            Ok(json!([
                tool["match"],
                tool["marker"],
                round(resolve(&tool["resolver"], rows)?, 2)
            ]))
        })
        .collect()
}
fn inject(text: &str) -> Result<String> {
    let defs = definitions();
    let defs = defs.as_array().unwrap();
    let mut out = vec![];
    let mut inside = false;
    let mut used = BTreeSet::new();
    for line in text.split('\n') {
        if line.starts_with("## ") {
            inside = false;
            out.push(line.to_owned());
            continue;
        }
        if line.trim() == "| Tool | Source | Notes |" {
            inside = true;
            out.push("| Tool | Source | Notes | $ |".into());
            continue;
        }
        if inside
            && line.starts_with('|')
            && line.chars().all(|c| matches!(c, '|' | '-' | ':' | ' '))
        {
            out.push(format!("{line}---:|"));
            continue;
        }
        if inside && line.starts_with("| **") {
            let name = line.split('|').nth(1).unwrap_or("");
            let matches: Vec<_> = defs
                .iter()
                .filter(|d| name.contains(d["match"].as_str().unwrap()))
                .collect();
            if matches.len() != 1 {
                bail!(
                    "inject: {} TOOLS match {:?}",
                    matches.len(),
                    text_prefix(line, 55)
                )
            }
            let marker = matches[0]["marker"].as_str().unwrap();
            used.insert(marker);
            out.push(format!("{} [$0.00]({marker}) |", line.trim_end()));
            continue;
        }
        out.push(line.to_owned());
    }
    let missing: Vec<_> = defs
        .iter()
        .filter_map(|d| d["marker"].as_str())
        .filter(|d| !used.contains(d))
        .collect();
    if !missing.is_empty() {
        bail!("inject: not located in tools.md: {missing:?}")
    }
    Ok(out.join("\n").replacen(
        "## Sources",
        "## Tools total\n\nTotal acquired tooling: **[$0.00](TOOLS_TOTAL)**\n\n## Sources",
        1,
    ))
}

pub fn dispatch(op: &str, request: &Value, context: &mut Context) -> Result<Value> {
    if op == "definitions" {
        return Ok(definitions());
    }
    if op == "inject" {
        return Ok(json!(inject(arg(request, "text")?)?));
    }
    if op == "pick" {
        return Ok(json!(pick(
            request["matches"]
                .as_array()
                .context("purchase matches")?
                .iter()
                .collect(),
            arg(request, "label")?
        )?));
    }
    let rows = if let Some(rows) = request["rows"].as_array() {
        rows.clone()
    } else {
        let path = context.path(request, "purchases", "hardware/ledger/purchases.md");
        load(&context.read(path)?)
    };
    if op == "load" {
        return Ok(json!(rows));
    }
    if op == "resolve" {
        return Ok(json!(resolve(&request["resolver"], &rows)?));
    }
    let resolved = compute(&rows)?;
    if op == "compute" {
        return Ok(json!(resolved));
    }
    if op != "main" {
        bail!("unknown tools operation: {op}")
    }
    let total = round(resolved.iter().map(|v| v[2].as_f64().unwrap()).sum(), 2);
    if !request["dry"].as_bool().unwrap_or(false) {
        let path = context.path(request, "tools", "hardware/ledger/tools.md");
        let text = context.read(&path)?;
        if !text.contains("TOOLS_TOTAL") {
            context.write(&path, inject(&text)?.as_bytes())?;
        }
        let mut vars: Variables = resolved
            .iter()
            .map(|v| {
                let n = v[2].as_f64().unwrap();
                (
                    v[1].as_str().unwrap().to_owned(),
                    if n == 0. { "—".into() } else { money(n) },
                )
            })
            .collect();
        vars.insert("TOOLS_TOTAL".into(), money(total));
        context.substitute(&path, &vars, "/hardware/scripts/_tools_totals.py")?;
    }
    let mut out = String::new();
    for v in &resolved {
        let n = v[2].as_f64().unwrap();
        out += &format!(
            "  {:>10}  {}\n",
            if n == 0. { "—".into() } else { money(n) },
            v[1].as_str().unwrap()
        );
    }
    out += &format!(
        "\n  TOOLS_TOTAL  {}   ({} tools)\n",
        money(total),
        resolved.len()
    );
    Ok(main_result(0, out))
}
