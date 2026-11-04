//! Semantic artifact scope and reverse dependencies from the declared action plan.
use crate::bookkeeping_common::*;
use anyhow::{Result, bail};
use hsm_build_data::inventory;
use regex::Regex;
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet, VecDeque},
    path::Path,
};
fn normalized(raw: &str) -> Option<Value> {
    let value = serde_json::from_str::<Value>(raw).ok()?;
    let mut out = serde_json::Map::new();
    for (generator, node) in value.as_object()? {
        let row = node.as_object()?;
        if row.len() != 3
            || !["reads", "writes", "rewritten"]
                .iter()
                .all(|k| row.contains_key(*k))
        {
            return None;
        }
        let mut next = serde_json::Map::new();
        for key in ["reads", "writes", "rewritten"] {
            let paths = row[key].as_array()?;
            if !paths.iter().all(Value::is_string) {
                return None;
            }
            next.insert(key.into(), json!(set(&row[key])));
        }
        out.insert(generator.clone(), json!(next));
    }
    Some(json!(out))
}
fn projection(g: &Value, cfg: &Value) -> Value {
    let rows = g.as_object().cloned().unwrap_or_default();
    let artifacts = rows
        .iter()
        .filter(|(generator, row)| {
            cfg["implicit_solids"].get(*generator).is_some()
                || strings(&row["writes"])
                    .iter()
                    .any(|p| CAD.iter().any(|s| p.ends_with(s)))
        })
        .map(|(generator, _)| generator.clone())
        .collect::<BTreeSet<_>>();
    let mut held = artifacts.clone();
    loop {
        let inputs = held
            .iter()
            .flat_map(|g| {
                ["reads", "rewritten", "writes"]
                    .into_iter()
                    .flat_map(|k| strings(&rows[g][k]))
            })
            .collect::<BTreeSet<_>>();
        let more = rows
            .iter()
            .filter(|(g, row)| !held.contains(*g) && !set(&row["writes"]).is_disjoint(&inputs))
            .map(|(g, _)| g.clone())
            .collect::<BTreeSet<_>>();
        if more.is_empty() {
            break;
        }
        held.extend(more);
    }
    let shared = shared_stems(rows.keys().map(String::as_str));
    let names = artifacts
        .iter()
        .map(|g| target_name(g, &shared))
        .collect::<BTreeSet<_>>();
    let out = rows
        .into_iter()
        .filter(|(g, _)| held.contains(g))
        .collect::<serde_json::Map<_, _>>();
    json!([out, names])
}
fn build_projection(text: &str, roots: &Value) -> Option<Value> {
    let name = Regex::new(r#"(?m)^\s*name = "([^"]+)",\s*$"#).unwrap();
    let outs = Regex::new(r"(?s)\bouts\s*=\s*\[(.*?)\]\s*,").unwrap();
    let quoted = Regex::new(r#""([^"]+)""#).unwrap();
    let mut blocks = BTreeMap::new();
    let mut outputs = BTreeMap::new();
    let mut globals = vec![];
    for block in text.split("\n\n") {
        if let Some(m) = name.captures(block) {
            let n = m[1].to_owned();
            blocks.insert(n.clone(), block);
            if let Some(m) = outs.captures(block) {
                for p in quoted.captures_iter(&m[1]) {
                    outputs.insert(p[1].to_owned(), n.clone());
                }
            }
        } else {
            globals.push(block)
        }
    }
    let mut held = BTreeMap::from([("__global__".to_owned(), globals.join("\n\n"))]);
    let mut pending = strings(roots);
    while let Some(n) = pending.pop() {
        if held.contains_key(&n) {
            continue;
        }
        let block = *blocks.get(&n)?;
        held.insert(n, block.into());
        for dep in quoted.captures_iter(block) {
            let d = dep[1].strip_prefix(':').unwrap_or(&dep[1]);
            let provider = if blocks.contains_key(d) {
                Some(d)
            } else {
                outputs.get(d).map(String::as_str)
            };
            if let Some(p) = provider {
                if !held.contains_key(p) {
                    pending.push(p.into());
                }
            }
        }
    }
    Some(json!(held))
}
fn inv_groups(v: &Value) -> Vec<(Vec<String>, Value)> {
    v.as_array()
        .into_iter()
        .flatten()
        .map(|row| (strings(&row[0]), row[1].clone()))
        .collect()
}
fn artifact_targets(inv: &Value) -> BTreeSet<String> {
    let rows = inv_groups(inv);
    let shared = shared_stems(
        rows.iter()
            .flat_map(|(gens, _)| gens.iter().map(String::as_str)),
    );
    rows.into_iter()
        .filter(|(_, v)| {
            strings(&v["solids"])
                .iter()
                .any(|p| CAD.iter().any(|s| p.ends_with(s)))
        })
        .filter_map(|(gens, _)| {
            gens.first()
                .map(|g| format!("//:{}", target_name(g, &shared)))
        })
        .collect()
}
fn artifact_gens(inv: &Value) -> BTreeSet<String> {
    inv_groups(inv)
        .into_iter()
        .filter(|(_, v)| {
            strings(&v["solids"])
                .iter()
                .any(|p| CAD.iter().any(|s| p.ends_with(s)))
        })
        .flat_map(|(gens, _)| gens)
        .collect()
}
fn artifact_roots(g: &Value, inv: &Value, cfg: &Value) -> BTreeSet<String> {
    let held = names(&projection(g, cfg)[0]);
    let rows = inv_groups(inv);
    let shared = shared_stems(
        rows.iter()
            .flat_map(|(gens, _)| gens.iter().map(String::as_str)),
    );
    rows.into_iter()
        .filter(|(gens, _)| gens.iter().any(|g| held.contains(g)))
        .filter_map(|(gens, _)| gens.first().map(|g| target_name(g, &shared)))
        .collect()
}
fn global(path: &str) -> bool {
    if [
        ".bazelrc",
        ".bazelversion",
        ".dockerignore",
        "BUILD.bazel",
        "MODULE.bazel",
        "MODULE.bazel.lock",
        "tools/cad-requirements.txt",
    ]
    .contains(&path)
        || path.starts_with(".github/workflows/")
    {
        return true;
    }
    if [
        "tools/bazel/affected.py",
        "tools/bazel/sync_tree.py",
        "tools/cad-artifacts/pack.py",
    ]
    .contains(&path)
    {
        return false;
    }
    [
        "tools/bazel/",
        "tools/cad-artifacts/",
        "tools/cad-venv-site/",
        "tools/ci-image/",
    ]
    .iter()
    .any(|p| path.starts_with(p))
}
fn presentation(path: &str, r: &Value) -> bool {
    if inventory::inert(path, &r["config"]) {
        return true;
    }
    if !path.starts_with("hardware/")
        || ![
            ".md",
            ".mmd",
            ".html",
            ".png",
            ".svg",
            ".pdf",
            ".css",
            ".figures.json",
            ".scene.json",
            ".pdf.json",
        ]
        .iter()
        .any(|s| path.ends_with(s))
    {
        return false;
    }
    let Some(graph) = r["graph"].as_object().filter(|g| !g.is_empty()) else {
        return false;
    };
    let artifacts = set(&r["artifact_gens"]);
    let writers = graph
        .iter()
        .filter(|(_, v)| set(&v["rewritten"]).contains(path))
        .map(|(g, _)| g)
        .collect::<BTreeSet<_>>();
    graph.iter().all(|(g, v)| {
        !artifacts.contains(g) || !set(&v["reads"]).contains(path) || writers.contains(g)
    })
}
fn read_kind(path: &str, r: &Value) -> bool {
    !inventory::inert(path, &r["config"])
        && (r["kinds"].is_null() || set(&r["kinds"]).contains(&suffix(path).to_lowercase()))
}
fn unknown(path: &str, artifacts_only: bool, r: &Value) -> bool {
    if inventory::inert(path, &r["config"])
        || path == "hardware/cad-artifacts.json"
        || path.ends_with(".lint-answers")
        || path.starts_with("hardware/quickstart/studies/")
        || path.ends_with("/.gitignore")
        || set(&r["declared"]).contains(path)
    {
        return false;
    }
    if path.starts_with("hardware/") {
        return !(artifacts_only && presentation(path, r)) && read_kind(path, r);
    }
    global(path)
        || [
            "tools/bazel/",
            "tools/cad-artifacts/",
            "tools/cad-venv-site/",
            "tools/ci-image/",
            "tools/docgen/",
            "tools/render/",
            "web/",
        ]
        .iter()
        .any(|p| path.starts_with(p))
}
fn risky(r: &Value) -> Vec<String> {
    let known = set(&r["known"]);
    let safe = set(&r["safe"]);
    let mut out = strings(&r["paths"])
        .into_iter()
        .filter(|p| {
            !safe.contains(p)
                && (global(p) || !known.contains(p) && unknown(p, r["artifacts_only"] == true, r))
        })
        .collect::<Vec<_>>();
    out.sort();
    out
}
fn manifest(paths: &Value, rules: &Value) -> Value {
    let rows = rules.as_object().cloned().unwrap_or_default();
    let mut owners = BTreeMap::new();
    let mut globs = vec![];
    for (name, rule) in &rows {
        for out in strings(&rule["outs"]) {
            owners.insert(out, name.clone());
        }
        for pair in rule["globs"].as_array().into_iter().flatten() {
            globs.push((name.clone(), strings(&pair[0]), strings(&pair[1])));
        }
    }
    let mut readers: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    let mut artifacts = BTreeSet::new();
    let mut known = BTreeSet::new();
    for (name, rule) in &rows {
        if strings(&rule["outs"])
            .iter()
            .any(|p| CAD.iter().any(|s| p.ends_with(s)))
        {
            artifacts.insert(name.clone());
        }
        for path in ["srcs", "tools", "data"]
            .into_iter()
            .flat_map(|k| strings(&rule[k]))
        {
            let path = path
                .strip_prefix("//:")
                .unwrap_or(&path)
                .strip_prefix(':')
                .unwrap_or(path.strip_prefix("//:").unwrap_or(&path))
                .to_owned();
            known.insert(path.clone());
            readers
                .entry(owners.get(&path).unwrap_or(&path).clone())
                .or_default()
                .insert(name.clone());
        }
    }
    let paths = strings(paths);
    let mut pending = VecDeque::from_iter(paths.iter().map(|p| owners.get(p).unwrap_or(p).clone()));
    for path in &paths {
        for (name, includes, excludes) in &globs {
            if includes.iter().any(|p| glob(p, path)) && !excludes.iter().any(|p| glob(p, path)) {
                known.insert(path.clone());
                pending.push_back(name.clone());
            }
        }
    }
    let mut seen = BTreeSet::new();
    while let Some(p) = pending.pop_front() {
        if seen.insert(p.clone()) {
            if let Some(next) = readers.get(&p) {
                pending.extend(next.iter().cloned());
            }
        }
    }
    json!([
        seen.intersection(&artifacts)
            .map(|n| format!("//:{n}"))
            .collect::<Vec<_>>(),
        paths
            .into_iter()
            .filter(|p| known.contains(p))
            .collect::<BTreeSet<_>>()
    ])
}
pub fn dispatch(op: &str, r: &Value) -> Result<Value> {
    Ok(match op {
        "diff_paths" => {
            let mut out = BTreeSet::new();
            for line in strings(&r["lines"]) {
                let f = line.split('\t').collect::<Vec<_>>();
                if f.len() >= 3 && (f[0].starts_with('R') || f[0].starts_with('C')) {
                    out.extend(f[1..3].iter().map(|s| s.to_string()));
                } else if f.len() >= 2 {
                    out.insert(f[1].into());
                }
            }
            out.retain(|p| !p.is_empty() && !p.ends_with('/'));
            json!(out)
        }
        "split_paths" => json!(
            text(r, "text")
                .split('\0')
                .filter(|s| !s.is_empty())
                .collect::<BTreeSet<_>>()
        ),
        "changed" => json!(
            set(&r["diff"])
                .union(&set(&r["untracked"]))
                .filter(|s| !s.is_empty())
                .cloned()
                .collect::<BTreeSet<_>>()
        ),
        "normalized_graph" => json!(normalized(text(r, "text"))),
        "artifact_projection" => projection(&r["graph"], &r["config"]),
        "graph_delta" => json!(
            match (normalized(text(r, "before")), normalized(text(r, "after"))) {
                (Some(a), Some(b)) => projection(&a, &r["config"]) == projection(&b, &r["config"]),
                _ => false,
            }
        ),
        "build_projection" => json!(build_projection(text(r, "text"), &r["roots"])),
        "build_delta" => json!(match (
            build_projection(text(r, "before"), &r["roots"]),
            build_projection(text(r, "after"), &r["roots"])
        ) {
            (Some(a), Some(b)) => a == b,
            _ => false,
        }),
        "artifact_roots" => json!(artifact_roots(&r["graph"], &r["inventory"], &r["config"])),
        "artifact_targets" => json!(artifact_targets(&r["inventory"])),
        "presentation_context" => {
            let g = graph(text(r, "path")).unwrap_or(json!({}));
            if truthy(&g) {
                json!([g, artifact_gens(&r["inventory"])])
            } else {
                json!([{}, []])
            }
        }
        "declared" => json!(
            graph(text(r, "path"))
                .and_then(|g| g.as_object().cloned())
                .into_iter()
                .flatten()
                .flat_map(|(_, v)| strings(&v["writes"]))
                .collect::<BTreeSet<_>>()
        ),
        "kinds" => json!(graph(text(r, "path")).map(|g| {
            g.as_object()
                .into_iter()
                .flatten()
                .flat_map(|(_, v)| strings(&v["reads"]))
                .map(|p| suffix(&p).to_lowercase())
                .collect::<BTreeSet<_>>()
        })),
        "read_kind" => json!(read_kind(text(r, "path"), r)),
        "sidecar" => json!(
            text(r, "path").ends_with(".scorecard.json")
                && set(&r["declared"]).contains(text(r, "path"))
        ),
        "global" => json!(global(text(r, "path"))),
        "presentation" => json!(presentation(text(r, "path"), r)),
        "unknown" => json!(unknown(text(r, "path"), r["artifacts_only"] == true, r)),
        "risky" => json!(risky(r)),
        "metadata_needed" => json!(
            r["artifacts_only"] == true && set(&r["paths"]).contains("tools/bazel/graph.json")
        ),
        "read_metadata" => {
            let root = Path::new(text(r, "root"));
            let after = crate::bookkeeping_common::read_text(&root.join("tools/bazel/graph.json"));
            let build = crate::bookkeeping_common::read_text(&root.join("BUILD.bazel"));
            json!(match (after, build) {
                (Ok(a), Ok(b)) => [Some(a), Some(b)],
                _ => [None, None],
            })
        }
        "metadata" => {
            let before = r["before"].as_str().and_then(normalized);
            let after = r["after"].as_str().and_then(normalized);
            let graph_safe = match (&before, &after) {
                (Some(a), Some(b)) => projection(a, &r["config"]) == projection(b, &r["config"]),
                _ => false,
            };
            let roots = after
                .as_ref()
                .map(|g| artifact_roots(g, &r["inventory"], &r["config"]))
                .unwrap_or_default();
            let build_safe = !roots.is_empty()
                && match (r["before_build"].as_str(), r["build_text"].as_str()) {
                    (Some(a), Some(b)) => match (
                        build_projection(a, &json!(roots)),
                        build_projection(b, &json!(roots)),
                    ) {
                        (Some(a), Some(b)) => a == b,
                        _ => false,
                    },
                    _ => false,
                };
            let mut q = r.clone();
            q["graph_safe"] = json!(graph_safe);
            q["build_safe"] = json!(build_safe);
            return dispatch("safe_paths", &q);
        }
        "safe_paths" => {
            let paths = set(&r["paths"]);
            let mut safe = BTreeSet::new();
            if r["artifacts_only"] == true
                && paths.contains("tools/bazel/graph.json")
                && r["graph_safe"] == true
            {
                safe.insert("tools/bazel/graph.json");
                if r["build_generated"] == true && r["build_safe"] != false {
                    for p in ["BUILD.bazel", "tools/bazel/gen_build.py"] {
                        if paths.contains(p) {
                            safe.insert(p);
                        }
                    }
                }
            }
            json!(safe)
        }
        "sentinels" => {
            let paths = set(&r["paths"]);
            json!(if paths.contains("tools/bazel/sync_tree.py")
                || paths.contains("tools/cad-artifacts/pack.py")
            {
                BTreeSet::from(["//:cold-core-assembly", "//:enclosure-assembly"])
            } else {
                BTreeSet::new()
            })
        }
        "manifest" => manifest(&r["paths"], &r["rules"]),
        "known" => {
            let seen = text(r, "stdout")
                .lines()
                .filter(|s| s.starts_with("//:"))
                .map(str::trim)
                .collect::<BTreeSet<_>>();
            let (hit, miss): (Vec<_>, Vec<_>) = strings(&r["paths"])
                .into_iter()
                .partition(|p| seen.contains(format!("//:{p}").as_str()));
            json!([hit, miss])
        }
        "query_targets" => json!(
            text(r, "stdout")
                .lines()
                .map(str::trim)
                .filter(|s| s.starts_with("//:")
                    && ![
                        ".py", ".js", ".json", ".md", ".step", ".mmd", ".html", ".css", ".svg",
                        ".png", ".dxf", ".glb", ".pdf", ".3mf", ".stl", ".ts", ".tsx", ".sh"
                    ]
                    .iter()
                    .any(|e| s.ends_with(e)))
                .collect::<BTreeSet<_>>()
        ),
        "target_text" => {
            let found = strings(&r["found"]);
            json!(if found.is_empty() {
                String::new()
            } else {
                found.join("\n") + "\n"
            })
        }
        "filter_moved" => json!(
            strings(&r["paths"])
                .into_iter()
                .filter(|p| !inventory::inert(p, &r["config"])
                    && (!(r["artifacts_only"] == true)
                        || !presentation(p, r)
                            && !(p.ends_with(".scorecard.json")
                                && set(&r["declared"]).contains(p))))
                .collect::<Vec<_>>()
        ),
        "final_targets" => {
            let artifacts = set(&r["artifact_targets"]);
            let found = set(&r["found"]);
            json!(if r["risky"].as_array().is_some_and(|v| !v.is_empty()) {
                if r["artifacts_only"] == true {
                    artifacts
                } else {
                    BTreeSet::from(["//:everything".into()])
                }
            } else if r["artifacts_only"] == true {
                found.intersection(&artifacts).cloned().collect()
            } else {
                found
            })
        }
        "why" => {
            let mut out = String::new();
            for target in strings(&r["found"]) {
                let reach = strings(&r["paths"])
                    .into_iter()
                    .filter(|p| set(&r["reach"][p]).contains(&target))
                    .collect::<Vec<_>>();
                out += &format!("{target}\n    {}\n", reach.join("\n    "));
            }
            json!(out)
        }
        "equal" => json!(r["a"] == r["b"]),
        _ => bail!("unknown affected operation {op}"),
    })
}
