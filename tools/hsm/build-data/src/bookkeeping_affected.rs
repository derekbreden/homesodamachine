//! Declared producer metadata scopes native artifact rebuilds and publication exclusions.
use crate::bookkeeping_common::*;
use crate::inventory;
use serde_json::{Value, json};
use std::collections::BTreeSet;
pub fn normalized(raw: &str) -> Option<Value> {
    let value = serde_json::from_str::<Value>(raw).ok()?;
    let mut out = serde_json::Map::new();
    for (generator, node) in value.as_object()? {
        let row = node.as_object()?;
        if row
            .keys()
            .any(|key| !["reads", "writes", "rewritten", "program"].contains(&key.as_str()))
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
            if program
                .keys()
                .any(|key| !["crate", "name", "sources", "runtime_inputs"].contains(&key.as_str()))
                || !["crate", "name"]
                    .iter()
                    .all(|key| program.get(*key).is_some_and(Value::is_string))
            {
                return None;
            }
            let mut held = serde_json::Map::new();
            for key in ["crate", "name"] {
                held.insert(key.into(), program[key].clone());
            }
            for key in ["sources", "runtime_inputs"] {
                if let Some(value) = program.get(key) {
                    if !value.as_array()?.iter().all(Value::is_string) {
                        return None;
                    }
                    held.insert(key.into(), json!(set(value)));
                } else if key == "sources" {
                    return None;
                }
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
pub fn global(path: &str) -> bool {
    if [
        ".dockerignore",
        "tools/hsm/build-data/src/inventory.rs",
        "tools/hsm/build-data/src/bookkeeping_common.rs",
    ]
    .contains(&path)
        || path.starts_with(".github/workflows/")
    {
        return true;
    }
    if [
        "tools/hsm/build-plan/src/affected.rs",
        "tools/hsm/build-plan/src/sync.rs",
    ]
    .contains(&path)
        || path.starts_with("tools/hsm/publication/")
    {
        return false;
    }
    ["tools/hsm/build-plan/", "tools/ci-image/"]
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
        let declared = graph
            .as_object()
            .into_iter()
            .flatten()
            .flat_map(|(_, row)| strings(&row["writes"]))
            .collect();
        let kinds = graph.as_object().map(|rows| {
            rows.values()
                .flat_map(|row| strings(&row["reads"]))
                .map(|path| suffix(&path).to_lowercase())
                .collect()
        });
        Self {
            config,
            graph,
            artifact_gens: artifact_gens(inventory),
            declared,
            kinds,
        }
    }
    pub fn presentation(&self, path: &str) -> bool {
        presentation(path, self)
    }
    pub fn read_kind(&self, path: &str) -> bool {
        read_kind(path, self)
    }
    pub fn unknown(&self, path: &str, artifacts_only: bool) -> bool {
        unknown(path, artifacts_only, self)
    }
    pub fn filter_moved(&self, paths: &BTreeSet<String>, artifacts_only: bool) -> BTreeSet<String> {
        paths
            .iter()
            .filter(|path| {
                !inventory::inert(path, &self.config)
                    && (!artifacts_only
                        || !self.presentation(path)
                            && !(path.ends_with(".scorecard.json")
                                && self.declared.contains(*path)))
            })
            .cloned()
            .collect()
    }
    pub fn risky(
        &self,
        paths: &BTreeSet<String>,
        known: &BTreeSet<String>,
        safe: &BTreeSet<String>,
        artifacts_only: bool,
    ) -> Vec<String> {
        paths
            .iter()
            .filter(|path| {
                !safe.contains(*path)
                    && (global(path)
                        || !known.contains(*path) && self.unknown(path, artifacts_only))
            })
            .cloned()
            .collect()
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
        && context
            .kinds
            .as_ref()
            .is_none_or(|kinds| kinds.contains(&suffix(path).to_lowercase()))
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
        || ["tools/ci-image/", "tools/render/", "web/"]
            .iter()
            .any(|p| path.starts_with(p))
}
