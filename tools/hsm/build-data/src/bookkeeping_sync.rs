//! Carry only generated figures into authored files; select all other outputs explicitly.
use crate::bookkeeping_common::*;
use anyhow::{Context, Result, bail};
use hsm_build_data::inventory;
use regex::Regex;
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    io::{Read, Write},
    path::Path,
};
fn runtime(path: &str) -> bool {
    CAD.iter().any(|s| path.ends_with(s)) || path.ends_with(".scorecard.json")
}
fn publisher(path: &str, cfg: &Value) -> bool {
    runtime(path)
        || [
            ".npz",
            ".facts.json",
            ".numbers.json",
            ".print.json",
            ".readiness.json",
        ]
        .iter()
        .any(|s| path.ends_with(s))
        || [
            "hardware/cad-artifacts.json",
            "web/public/tube-routes.json",
        ]
        .contains(&path)
        || (path.starts_with("hardware/")
            && ["design.json", "geometry-check.json"]
                .contains(&path.rsplit('/').next().unwrap_or("")))
        || (path.starts_with("hardware/print-tests/")
            && path.contains("/prints/")
            && path.ends_with(".json"))
        || inventory::inert(path, cfg)
}
fn whole(path: &str) -> bool {
    [".json", ".png"].contains(&suffix(path)) || path == "hardware/ledger/purchases.export.csv"
}
fn managed(text: &str, kind: &str, names: Option<&BTreeSet<String>>) -> Vec<(usize, usize)> {
    if kind == ".md" {
        return vec![(0, text.len())];
    }
    if kind == ".mmd" {
        let mut at = 0;
        return text
            .split_inclusive('\n')
            .filter_map(|line| {
                let start = at;
                at += line.len();
                line.trim_start().starts_with("%%").then_some((start, at))
            })
            .collect();
    }
    hsm_documents::python_regions_checked(text)
        .unwrap_or_default()
        .into_iter()
        .filter(|(a, b, comment)| {
            *comment
                || names.is_none()
                || hsm_documents::markers(&text[*a..*b])
                    .iter()
                    .any(|(_, _, _, name)| names.unwrap().contains(*name))
        })
        .map(|(a, b, _)| (a, b))
        .collect()
}
fn figures(text: &str, kind: &str) -> BTreeMap<String, String> {
    let mut out = BTreeMap::new();
    for (a, b) in managed(text, kind, None) {
        for (_, _, value, name) in hsm_documents::markers(&text[a..b]) {
            out.insert(name.into(), value.into());
        }
    }
    out
}
fn fill(text: &str, figures: &BTreeMap<String, String>) -> String {
    let mut out = String::new();
    let mut at = 0;
    for (a, b, _, name) in hsm_documents::markers(text) {
        out.push_str(&text[at..a]);
        if let Some(value) = figures.get(name) {
            out.push_str(&format!("[{value}]({name})"));
        } else {
            out.push_str(&text[a..b]);
        }
        at = b;
    }
    out.push_str(&text[at..]);
    out
}
pub fn carried(built: &str, tracked: &str, kind: &str) -> String {
    let values = figures(built, kind);
    let names = values.keys().cloned().collect();
    let mut out = tracked.to_owned();
    let spans = managed(tracked, kind, Some(&names))
        .into_iter()
        .collect::<BTreeSet<_>>();
    for (a, b) in spans.into_iter().rev() {
        out.replace_range(a..b, &fill(&out[a..b], &values));
    }
    if kind == ".md" {
        let valid = |text: &str| {
            hsm_documents::sources_section(text)
                .filter(|(_, b)| *b > 0 && text.as_bytes()[*b - 1] == b'\n')
        };
        if let Some((a, b)) = valid(built) {
            let section = &built[a..b];
            if let Some((a, b)) = valid(&out) {
                out.replace_range(a..b, section);
            } else {
                out = out.trim_end().to_owned() + "\n\n" + section;
            }
        }
    }
    out
}
fn same(a: &Path, b: &Path) -> Result<bool> {
    let mut a = fs::File::open(a)?;
    let mut b = fs::File::open(b)?;
    let (mut x, mut y) = ([0_u8; 65536], [0_u8; 65536]);
    loop {
        let n = a.read(&mut x)?;
        let m = b.read(&mut y)?;
        if n != m || x[..n] != y[..m] {
            return Ok(false);
        }
        if n == 0 {
            return Ok(true);
        }
    }
}
fn carry(r: &Value) -> Result<Value> {
    let root = Path::new(text(r, "root"));
    let mut pairs = r["pairs"].as_object().cloned().unwrap_or_default();
    let mut output = String::new();
    let write = r["write"] == true;
    let rewritten = set(&r["rewritten"]);
    let failed = set(&r["failed"]);
    if r["runtime_only"] == true {
        pairs.retain(|_, p| runtime(p.as_str().unwrap_or("")));
    }
    if r["derived_only"] == true && !pairs.is_empty() {
        let all = pairs.len();
        pairs.retain(|_, p| !publisher(p.as_str().unwrap_or(""), &r["config"]));
        output += &format!(
            "  {} publisher-owned output(s) left in the tree\n",
            all - pairs.len()
        );
        if pairs.is_empty() {
            output += "  no derived outputs in the requested slice\n";
            return Ok(json!({"output":output,"status":0}));
        }
    }
    if pairs.is_empty() {
        output += "  nothing built — run the requested `bazel build` first\n";
        return Ok(json!({"output":output,"status":1}));
    }
    if r["scope_only"] == true {
        return Ok(json!({"pairs":pairs,"output":output,"status":null}));
    }
    if !failed.is_empty() {
        let all = pairs.len();
        let re = Regex::new(r"/bin/out/([^/]+)/")?;
        pairs.retain(|p, _| !re.captures(p).is_some_and(|m| failed.contains(&m[1])));
        output += &format!(
            "  {} output(s) held back, cut by {} target(s) that failed this run: {}\n",
            all - pairs.len(),
            failed.len(),
            failed.iter().cloned().collect::<Vec<_>>().join(", ")
        );
    }
    let (mut differs, mut missing, mut unknown) = (vec![], vec![], vec![]);
    for (built, relative) in &pairs {
        let relative = relative.as_str().context("carried tree path is text")?;
        let b = Path::new(built);
        let t = root.join(relative);
        let kind = suffix(relative);
        let spliceable = rewritten.contains(relative) && [".md", ".mmd", ".py"].contains(&kind);
        if !b.is_file() {
            missing.push(relative.to_owned());
        } else if rewritten.contains(relative) && !spliceable && !whole(relative) {
            unknown.push(relative.to_owned());
        } else if spliceable && t.is_file() {
            let old = read_text(&t)?;
            let want = carried(&read_text(b)?, &old, kind);
            if want != old {
                differs.push((built.clone(), t, relative.to_owned(), Some(want)));
            }
        } else if !t.is_file() || !same(b, &t)? {
            differs.push((built.clone(), t, relative.to_owned(), None));
        }
    }
    for (_, _, relative, _) in differs.iter().take(20) {
        output += &format!("  {relative}\n");
    }
    if differs.len() > 20 {
        output += &format!("  …and {} more\n", differs.len() - 20);
    }
    for relative in &unknown {
        output += &format!(
            "  {relative} is read back over and {} has no splice here — left alone rather than carried whole\n",
            suffix(relative)
        );
    }
    if write {
        for (b, t, _, want) in &differs {
            if let Some(parent) = t.parent() {
                fs::create_dir_all(parent)?;
            }
            let mut file = fs::OpenOptions::new()
                .write(true)
                .create(true)
                .truncate(true)
                .open(t)?;
            if let Some(want) = want {
                file.write_all(want.as_bytes())?;
            } else {
                std::io::copy(&mut fs::File::open(b)?, &mut file)?;
            }
        }
        output += &format!(
            "{} carried into the tree{}\n",
            differs.len(),
            if missing.is_empty() {
                String::new()
            } else {
                format!(", {} declared output(s) absent", missing.len())
            }
        );
    } else {
        output += &format!(
            "{}/{} artifacts in the tree are the ones the build cut{}{}\n",
            pairs.len() - differs.len() - missing.len() - unknown.len(),
            pairs.len(),
            if missing.is_empty() {
                String::new()
            } else {
                format!(", {} not built", missing.len())
            },
            if unknown.is_empty() {
                String::new()
            } else {
                format!(", {} with no splice", unknown.len())
            }
        );
    }
    Ok(
        json!({"output":output,"status":usize::from(!unknown.is_empty()||!missing.is_empty()||!write&&!differs.is_empty()),"written":if write{differs.iter().map(|(_,_,r,_)|r.clone()).collect::<Vec<_>>()}else{vec![]}}),
    )
}
pub fn dispatch(op: &str, r: &Value) -> Result<Value> {
    Ok(match op {
        "runtime" => json!(runtime(text(r, "path"))),
        "publisher" => json!(publisher(text(r, "path"), &r["config"])),
        "whole" => json!(whole(text(r, "path"))),
        "labels" => json!(labels(text(r, "raw"))),
        "failed_labels" => json!(
            text(r, "raw")
                .split(',')
                .map(str::trim)
                .filter(|s| !s.is_empty())
                .map(|s| s.trim_start_matches('/').trim_start_matches(':').to_owned())
                .collect::<BTreeSet<_>>()
        ),
        "managed" => {
            let text = text(r, "text");
            let names = (!r["names"].is_null()).then(|| {
                if r["names"].is_object() {
                    names(&r["names"])
                } else {
                    set(&r["names"])
                }
            });
            json!(
                managed(
                    text,
                    crate::bookkeeping_common::text(r, "suffix"),
                    names.as_ref()
                )
                .iter()
                .map(|(a, b)| (text[..*a].chars().count(), text[..*b].chars().count()))
                .collect::<Vec<_>>()
            )
        }
        "figures" => json!(figures(text(r, "text"), text(r, "suffix"))),
        "carried" => json!(carried(
            text(r, "built"),
            text(r, "tracked"),
            text(r, "suffix")
        )),
        "rewritten" => {
            let source=graph(text(r,"path")).with_context(||format!("  no build graph to read, so which files are rewritten in place is\n  unknown, and copying one whole lands a build's text over an\n  author's: {}",text(r,"path")))?;
            json!(
                source
                    .as_object()
                    .into_iter()
                    .flatten()
                    .flat_map(|(_, v)| strings(&v["rewritten"]))
                    .collect::<BTreeSet<_>>()
            )
        }
        "targets" => {
            let re = Regex::new(r"/bin/out/[^/]+/(.+)$")?;
            let mut out = serde_json::Map::new();
            let mut claimed = BTreeMap::new();
            let mut collided = BTreeSet::new();
            let intermediates = set(&r["intermediate"]);
            let mut output = String::new();
            for line in text(r, "stdout").split_whitespace() {
                if let Some(m) = re.captures(line) {
                    let hit = &m[1];
                    if intermediates.contains(hit) {
                        continue;
                    }
                    if let Some(before) = claimed.get(hit) {
                        output += &format!(
                            "  {hit} is cut by two targets: {before} and {line}\n  — carried by neither; the tree keeps the copy it holds.\n"
                        );
                        collided.insert(hit.to_owned());
                        continue;
                    }
                    claimed.insert(hit.to_owned(), line.to_owned());
                    out.insert(
                        Path::new(text(r, "root"))
                            .join(line)
                            .to_string_lossy()
                            .into_owned(),
                        json!(hit),
                    );
                }
            }
            out.retain(|_, v| !collided.contains(v.as_str().unwrap_or("")));
            json!({"pairs":out,"output":output})
        }
        "freshness" => {
            let failed = set(&r["failed"]);
            let owed = text(r, "stderr")
                .lines()
                .filter(|s| s.contains("not up-to-date"))
                .collect::<Vec<_>>();
            let re = Regex::new(r"//:([^\s']+)")?;
            let stale = owed
                .iter()
                .copied()
                .filter(|s| {
                    !s.contains("BazelWorkspaceStatusAction")
                        && !re.captures(s).is_some_and(|m| failed.contains(&m[1]))
                })
                .collect::<Vec<_>>();
            let refused = r["status"] != 0 && (!stale.is_empty() || owed.is_empty());
            let mut output = String::new();
            if refused {
                output += "  the build is not up to date, so what is in bazel-bin is not what these\n  sources make — carrying it into the tree would write stale bytes over\n  whatever is there. Build the requested target slice first.\n";
                let lines = if stale.is_empty() { &owed } else { &stale };
                for line in lines.iter().take(5) {
                    output += &format!("  {}\n", line.trim());
                }
                if lines.len() > 5 {
                    output += &format!("  …and {} more\n", lines.len() - 5);
                }
            }
            json!({"refused":refused,"output":output})
        }
        "stage" => {
            let bytes = serde_json::from_value::<Vec<u8>>(r["status_bytes"].clone())?;
            let (mut paths, mut held, mut staged, mut tracked) = (vec![], vec![], vec![], vec![]);
            for entry in bytes.split(|b| *b == 0).filter(|b| !b.is_empty()) {
                if entry.len() < 3 {
                    continue;
                }
                let path = &entry[3..];
                if publisher(&String::from_utf8_lossy(path), &r["config"]) {
                    held.push(path.to_vec());
                    if ![b' ', b'?'].contains(&entry[0]) {
                        staged.push(path.to_vec());
                    }
                    if &entry[..2] != b"??" && entry[0] != b'A' {
                        tracked.push(path.to_vec());
                    }
                } else {
                    paths.push(path.to_vec());
                }
            }
            json!({"paths":paths,"held":held,"staged":staged,"tracked":tracked})
        }
        "carry" => return carry(r),
        _ => bail!("unknown sync operation {op}"),
    })
}
pub fn drop_dispatch(op: &str, r: &Value) -> Result<Value> {
    Ok(match op {
        "made" => {
            let g = graph(text(r, "path")).context("reading build graph")?;
            json!(
                g.as_object()
                    .into_iter()
                    .flatten()
                    .flat_map(|(_, v)| strings(&v["writes"])
                        .into_iter()
                        .chain(strings(&v["rewritten"])))
                    .collect::<BTreeSet<_>>()
            )
        }
        "split" => {
            let made = set(&r["made"]);
            let mut drop = vec![];
            let mut keep = vec![];
            for path in strings(&r["dirty"]) {
                if glob("hardware/**/*.py", &path) || path == "tools/bazel/graph.json" {
                    keep.push(path)
                } else if made.contains(&path) {
                    drop.push(path)
                } else {
                    keep.push(path)
                }
            }
            json!([drop, keep])
        }
        _ => bail!("unknown derived restore operation {op}"),
    })
}
