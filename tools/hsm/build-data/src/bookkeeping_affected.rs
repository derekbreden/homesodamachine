//! Declared producer metadata scopes native artifact rebuilds and publication exclusions.
use crate::bookkeeping_common::*;
use crate::inventory;
use regex::Regex;
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet, VecDeque},
};
pub fn normalized(raw: &str) -> Option<Value> {
    let value = serde_json::from_str::<Value>(raw).ok()?;
    let mut out = serde_json::Map::new();
    for (generator, node) in value.as_object()? {
        let row = node.as_object()?;
        if row.keys().any(|key| !["reads", "writes", "rewritten", "program"].contains(&key.as_str()))
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
        if let Some(program) = row.get("program") {
            let program = program.as_object()?;
            if program.keys().any(|key| !["crate", "name", "sources", "runtime_inputs"].contains(&key.as_str()))
                || !["crate", "name"].iter().all(|key| program.get(*key).is_some_and(Value::is_string)) { return None; }
            let mut held = serde_json::Map::new();
            for key in ["crate", "name"] { held.insert(key.into(), program[key].clone()); }
            for key in ["sources", "runtime_inputs"] {
                if let Some(value) = program.get(key) {
                    if !value.as_array()?.iter().all(Value::is_string) { return None; }
                    held.insert(key.into(), json!(set(value)));
                } else if key == "sources" { return None; }
            }
            next.insert("program".into(), Value::Object(held));
        }
        out.insert(generator.clone(), json!(next));
    }
    Some(json!(out))
}
pub fn projection(g: &Value, cfg: &Value) -> Value {
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
pub fn build_projection(text: &str, roots: &Value) -> Option<Value> {
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
pub fn artifact_targets(inv: &Value) -> BTreeSet<String> {
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
pub fn artifact_gens(inv: &Value) -> BTreeSet<String> {
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
pub fn artifact_roots(g: &Value, inv: &Value, cfg: &Value) -> BTreeSet<String> {
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
pub fn global(path: &str) -> bool {
    if [
        ".bazelrc",
        ".bazelversion",
        ".dockerignore",
        "BUILD.bazel",
        "MODULE.bazel",
        "MODULE.bazel.lock",
        "tools/hsm/build-data/src/inventory.rs",
        "tools/hsm/build-data/src/bookkeeping_common.rs",
    ]
    .contains(&path)
        || path.starts_with(".github/workflows/")
    {
        return true;
    }
    if ["tools/hsm/build-plan/src/affected.rs", "tools/hsm/build-plan/src/sync.rs"].contains(&path)
        || path.starts_with("tools/hsm/publication/")
    {
        return false;
    }
    [
        "tools/hsm/build-plan/",
        "tools/ci-image/",
    ]
    .iter()
    .any(|p| path.starts_with(p))
}
/// Declared producers distinguish presentation data, geometry inputs and files outside the graph.
pub struct Classification {
    pub config: Value,
    pub graph: Value,
    pub artifact_gens: BTreeSet<String>,
    pub declared: BTreeSet<String>,
    pub kinds: Option<BTreeSet<String>>,
}

impl Classification {
    pub fn new(config: Value, graph: Value, inventory: &Value) -> Self {
        let declared = graph.as_object().into_iter().flatten().flat_map(|(_, row)| strings(&row["writes"])).collect();
        let kinds = graph.as_object().map(|rows| rows.values().flat_map(|row| strings(&row["reads"]))
            .map(|path| suffix(&path).to_lowercase()).collect());
        Self { config, graph, artifact_gens: artifact_gens(inventory), declared, kinds }
    }
    pub fn presentation(&self, path: &str) -> bool { presentation(path, self) }
    pub fn read_kind(&self, path: &str) -> bool { read_kind(path, self) }
    pub fn unknown(&self, path: &str, artifacts_only: bool) -> bool { unknown(path, artifacts_only, self) }
    pub fn filter_moved(&self, paths: &BTreeSet<String>, artifacts_only: bool) -> BTreeSet<String> {
        paths.iter().filter(|path| !inventory::inert(path, &self.config)
            && (!artifacts_only || !self.presentation(path) && !(path.ends_with(".scorecard.json") && self.declared.contains(*path))))
            .cloned().collect()
    }
    pub fn risky(&self, paths: &BTreeSet<String>, known: &BTreeSet<String>, safe: &BTreeSet<String>, artifacts_only: bool) -> Vec<String> {
        paths.iter().filter(|path| !safe.contains(*path) && (global(path) || !known.contains(*path) && self.unknown(path, artifacts_only))).cloned().collect()
    }
}

fn presentation(path: &str, context: &Classification) -> bool {
    if inventory::inert(path, &context.config) {
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
    let Some(graph) = context.graph.as_object().filter(|g| !g.is_empty()) else {
        return false;
    };
    let artifacts = &context.artifact_gens;
    let writers = graph
        .iter()
        .filter(|(_, v)| set(&v["rewritten"]).contains(path))
        .map(|(g, _)| g)
        .collect::<BTreeSet<_>>();
    graph.iter().all(|(g, v)| {
        !artifacts.contains(g) || !set(&v["reads"]).contains(path) || writers.contains(g)
    })
}
fn read_kind(path: &str, context: &Classification) -> bool {
    !inventory::inert(path, &context.config)
        && context.kinds.as_ref().is_none_or(|kinds| kinds.contains(&suffix(path).to_lowercase()))
}
fn unknown(path: &str, artifacts_only: bool, context: &Classification) -> bool {
    if inventory::inert(path, &context.config)
        || path == "hardware/cad-artifacts.json"
        || path.ends_with(".lint-answers")
        || path.starts_with("hardware/quickstart/studies/")
        || path.ends_with("/.gitignore")
        || context.declared.contains(path)
    {
        return false;
    }
    if path.starts_with("hardware/") {
        return !(artifacts_only && presentation(path, context)) && read_kind(path, context);
    }
    global(path)
        || [
            "tools/bazel/",
            "tools/cad-venv-site/",
            "tools/ci-image/",
            "tools/docgen/",
            "tools/render/",
            "web/",
        ]
        .iter()
        .any(|p| path.starts_with(p))
}
pub fn manifest(paths: &Value, rules: &Value) -> Value {
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
