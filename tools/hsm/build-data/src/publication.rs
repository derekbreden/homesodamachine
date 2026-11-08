//! Catalog membership, published-file selection and producer provenance lines.
use crate::{artifact_cache::Cache, artifacts::names};
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::{Component, Path},
};
#[path = "publication_archive.rs"]
mod archive;
#[path = "publication_state.rs"]
mod state;
#[path = "publication_zlib.rs"]
mod zlib;
pub use state::target_name;

fn strings(v: &Value) -> Vec<String> {
    v.as_array()
        .map(|a| {
            a.iter()
                .filter_map(Value::as_str)
                .map(str::to_owned)
                .collect()
        })
        .unwrap_or_default()
}
fn starts(path: &str, roots: &Value) -> bool {
    strings(roots)
        .iter()
        .any(|root| path.starts_with(&format!("{root}/")))
}
fn ends(path: &str, suffixes: &Value) -> bool {
    strings(suffixes)
        .iter()
        .any(|suffix| path.ends_with(suffix))
}
fn normalized(path: &Path) -> String {
    let mut result = std::path::PathBuf::new();
    for part in path
        .components()
        .filter(|c| !matches!(c, Component::CurDir))
    {
        result.push(part.as_os_str());
    }
    if result.as_os_str().is_empty() {
        ".".into()
    } else {
        result.to_string_lossy().into_owned()
    }
}
fn filename(path: &str) -> String {
    let path = normalized(Path::new(path));
    if path == "." || path == "/" {
        String::new()
    } else {
        path.rsplit('/').next().unwrap_or("").into()
    }
}
fn sibling(path: &str, extension: &str) -> String {
    let name = stem(path) + extension;
    normalized(&Path::new(&parent(path)).join(name))
}
pub fn retired(root: &Path, relative: &str) -> bool {
    let mut parent = Path::new(relative).parent();
    while let Some(path) = parent {
        if path.as_os_str().is_empty() || path == Path::new(".") {
            break;
        }
        if root.join(path).join(".retired").is_file() {
            return true;
        }
        parent = path.parent();
    }
    false
}
fn unquote(text: &str) -> String {
    let mut bytes = Vec::new();
    let raw = text.as_bytes();
    let mut i = 0;
    while i < raw.len() {
        if raw[i] == b'%' && i + 2 < raw.len() {
            if let Ok(hex) = std::str::from_utf8(&raw[i + 1..i + 3]) {
                if let Ok(value) = u8::from_str_radix(hex, 16) {
                    bytes.push(value);
                    i += 3;
                    continue;
                }
            }
        }
        bytes.push(raw[i]);
        i += 1;
    }
    String::from_utf8_lossy(&bytes).into_owned()
}
fn url_path(text: &str) -> String {
    let clean = text
        .trim_start_matches(|c: char| c <= ' ')
        .replace(['\t', '\r', '\n'], "");
    let text = clean.split(['?', '#']).next().unwrap_or("");
    let mut path = text;
    if let Some((scheme, after)) = text.split_once(':') {
        if scheme.starts_with(|c: char| c.is_ascii_alphabetic())
            && scheme
                .chars()
                .all(|c| c.is_ascii_alphanumeric() || matches!(c, '+' | '-' | '.'))
        {
            path = after;
        }
    }
    if let Some(after) = path.strip_prefix("//") {
        path = after.find('/').map(|i| &after[i..]).unwrap_or("");
    }
    unquote(path)
}

fn parent(path: &str) -> String {
    normalized(Path::new(path).parent().unwrap_or(Path::new(".")))
}
fn stem(path: &str) -> String {
    let name = filename(path);
    if let Some(index) = name.rfind('.').filter(|&i| i > 0 && i + 1 < name.len()) {
        name[..index].into()
    } else {
        name
    }
}
fn has_parent(path: &str) -> bool {
    Path::new(path)
        .components()
        .any(|c| c == Component::ParentDir)
}

pub fn website_paths(
    root: &Path,
    available: &[String],
    config: &Value,
) -> Result<BTreeSet<String>> {
    let catalog: Value =
        serde_json::from_slice(&fs::read(root.join("hardware/ledger/materials.json"))?)?;
    let mut models = BTreeSet::new();
    let mut own = BTreeSet::new();
    if let Some(materials) = catalog["materials"].as_array() {
        for material in materials {
            if !material["id"].as_str().unwrap_or("").starts_with("HSM-") {
                continue;
            }
            if let Some(entries) = material["models"].as_array() {
                for model in entries {
                    let file = url_path(model["file"].as_str().unwrap_or(""));
                    if file.is_empty() {
                        continue;
                    }
                    let relative = format!(
                        "hardware/{}",
                        file.strip_prefix("hardware/").unwrap_or(&file)
                    );
                    if has_parent(&relative) || retired(root, &relative) {
                        continue;
                    }
                    models.insert(relative.clone());
                    if !truthy(&model["context"]) {
                        own.insert(relative);
                    }
                }
            }
        }
    }
    let mut allowed = models.clone();
    for relative in &models {
        for suffix in [".mesh", ".json", ".png"] {
            allowed.insert(format!("{relative}{suffix}"));
        }
        for suffix in [".scorecard.json", ".facts.json", ".frame.json"] {
            allowed.insert(sibling(relative, suffix));
        }
    }
    let stls: BTreeSet<_> = own.iter().map(|p| sibling(p, ".stl")).collect();
    allowed.extend(stls.iter().cloned());
    let by_name: BTreeSet<_> = own.iter().map(|p| (parent(p), stem(p))).collect();
    let directories: BTreeSet<_> = own.iter().map(|p| parent(p)).collect();
    for directory in directories {
        let mut records = fs::read_dir(root.join(&directory))
            .into_iter()
            .flatten()
            .filter_map(Result::ok)
            .map(|e| e.path())
            .filter(|p| {
                p.file_name()
                    .is_some_and(|name| name.to_string_lossy().ends_with(".print.json"))
            })
            .collect::<Vec<_>>();
        records.sort();
        for record in records {
            let relative = record.strip_prefix(root)?.to_string_lossy();
            if retired(root, &relative) {
                continue;
            }
            let Some(report) = fs::read(&record)
                .ok()
                .and_then(|b| serde_json::from_slice::<Value>(&b).ok())
            else {
                continue;
            };
            let Some(parts) = report["parts"].as_array().filter(|a| !a.is_empty()) else {
                continue;
            };
            let mut sources = Vec::new();
            let mut valid = true;
            for part in parts {
                if !part.is_object() {
                    valid = false;
                    break;
                }
                let mut source = pystr(part.get("source").unwrap_or(&json!("")));
                if !source.starts_with("hardware/") {
                    source = normalized(&Path::new(&directory).join(source));
                }
                let named = part["name"]
                    .as_str()
                    .is_some_and(|name| by_name.contains(&(directory.clone(), name.into())));
                if has_parent(&source)
                    || parent(&source) != directory
                    || (!stls.contains(&source) && !named)
                {
                    valid = false;
                    break;
                }
                sources.push(source);
            }
            if valid {
                allowed.extend(sources);
                if let Some(project) = report["project"].as_str() {
                    if filename(project) == project {
                        allowed.insert(normalized(&Path::new(&directory).join(project)));
                    }
                }
            }
        }
    }
    let boards = strings(&config["BUNDLED_BOARD_DIRS"])
        .into_iter()
        .filter(|d| models.iter().any(|m| m.starts_with(&format!("{d}/"))))
        .collect::<Vec<_>>();
    for relative in available {
        if starts(relative, &config["BUNDLED_ART_DIRS"])
            && ends(relative, &config["BUNDLED_ART_SUFFIXES"])
            || starts(relative, &config["BUNDLED_GLB_DIRS"]) && (relative.ends_with(".glb") || relative.ends_with(".glb.mesh"))
            || boards
                .iter()
                .any(|d| relative.starts_with(&format!("{d}/")))
                && !ends(relative, &json!([".step", ".stl", ".mesh", ".glb", ".npz"]))
            || names(&config["BUNDLED_ART_FILES"]).contains(relative)
        {
            allowed.insert(relative.clone());
        }
    }
    allowed.retain(|p| !retired(root, p));
    Ok(allowed)
}

pub fn frozen_assets(root: &Path) -> Result<BTreeMap<String, String>> {
    let mut todo = vec![root.join("hardware/reference")];
    let mut paths = Vec::new();
    while let Some(path) = todo.pop() {
        if let Ok(entries) = fs::read_dir(path) {
            for entry in entries {
                let entry = entry?;
                let kind = entry.file_type()?;
                if kind.is_dir() {
                    todo.push(entry.path());
                } else if kind.is_file() && entry.file_name() == "frozen-asset.json" {
                    paths.push(entry.path());
                }
            }
        }
    }
    paths.sort();
    let mut members = BTreeMap::new();
    for path in paths {
        let record: Value = serde_json::from_slice(&fs::read(&path)?)?;
        for (name, digest) in record["members"]
            .as_object()
            .context("frozen asset members")?
        {
            members.insert(
                path.parent()
                    .unwrap()
                    .join(name)
                    .strip_prefix(root)?
                    .to_string_lossy()
                    .into_owned(),
                digest.as_str().context("frozen digest")?.into(),
            );
        }
    }
    Ok(members)
}

fn member(
    relative: &str,
    root: &Path,
    frozen: &BTreeSet<String>,
    catalog: &BTreeSet<String>,
    config: &Value,
) -> bool {
    let name = relative.rsplit('/').next().unwrap_or("");
    if !relative.starts_with("hardware/")
        || relative.contains("/node_modules/")
        || retired(root, relative)
    {
        return false;
    }
    if catalog.contains(relative) {
        return true;
    }
    if starts(relative, &config["NOT_BUNDLED_DIRS"]) {
        return false;
    }
    if names(&config["HARVESTED"]).contains(relative) && !frozen.contains(relative) {
        return false;
    }
    if starts(relative, &config["BUNDLED_BOARD_DIRS"]) {
        return !ends(name, &config["BOARD_NOT_BUNDLED"]);
    }
    if name.starts_with('.') {
        return false;
    }
    name.ends_with(".step")
        || name.ends_with(".stl") && starts(relative, &config["BUNDLED_MESH_DIRS"])
        || name.ends_with(".step.mesh") && starts(relative, &config["BUNDLED_PAYLOAD_DIRS"])
        || (name.ends_with(".glb") || name.ends_with(".glb.mesh")) && starts(relative, &config["BUNDLED_GLB_DIRS"])
        || ends(name, &config["BUNDLED_ART_SUFFIXES"])
            && starts(relative, &config["BUNDLED_ART_DIRS"])
        || names(&config["BUNDLED_PAYLOAD_FILES"]).contains(relative)
        || names(&config["BUNDLED_ART_FILES"]).contains(relative)
        || frozen.contains(relative)
}

pub fn solids(root: &Path, config: &Value) -> Result<BTreeSet<String>> {
    if !root.join("hardware").is_dir() {
        return Ok(BTreeSet::new());
    }
    let frozen = frozen_assets(root)?
        .keys()
        .cloned()
        .collect::<BTreeSet<_>>();
    let has_catalog = root.join("hardware/ledger/materials.json").is_file();
    let catalog = if has_catalog {
        website_paths(root, &[], config)?
    } else {
        BTreeSet::new()
    };
    let mut listings = Cache::new(root, true);
    let mut todo = vec!["hardware".to_owned()];
    let mut out = BTreeSet::new();
    while let Some(here) = todo.pop() {
        let Some((dirs, files)) = listings.listing(&here)? else {
            continue;
        };
        if files.iter().any(|name| name == ".retired") {
            continue;
        }
        for name in dirs {
            let relative = format!("{here}/{name}");
            if name != "node_modules"
                && !starts(&format!("{relative}/x"), &config["NOT_BUNDLED_DIRS"])
            {
                todo.push(relative);
            }
        }
        for name in files {
            let relative = format!("{here}/{name}");
            if member(&relative, root, &frozen, &catalog, config) {
                out.insert(relative);
            }
        }
    }
    listings.save()?;
    if has_catalog {
        let allowed = website_paths(root, &out.iter().cloned().collect::<Vec<_>>(), config)?;
        out.extend(allowed.iter().filter(|p| root.join(p).is_file()).cloned());
        let graph: Value = serde_json::from_slice(&fs::read(root.join("tools/bazel/graph.json"))?)?;
        let mut required = frozen;
        if let Some(rows) = graph.as_object() {
            for row in rows.values() {
                required.extend(names(&row["reads"]));
                required.extend(names(&row["writes"]));
            }
        }
        if let Some(entries) = config["IMPLICIT_SOLIDS"].as_object() {
            for paths in entries.values() {
                required.extend(names(paths));
            }
        }
        out.retain(|p| allowed.contains(p) || required.contains(p));
    }
    Ok(out)
}

fn truthy(v: &Value) -> bool {
    match v {
        Value::Null => false,
        Value::Bool(v) => *v,
        Value::Number(v) => v.as_f64() != Some(0.),
        Value::String(s) => !s.is_empty(),
        Value::Array(a) => !a.is_empty(),
        Value::Object(m) => !m.is_empty(),
    }
}
fn pystr(v: &Value) -> String {
    match v {
        Value::Null => "None".into(),
        Value::Bool(true) => "True".into(),
        Value::Bool(false) => "False".into(),
        Value::String(s) => s.clone(),
        _ => v.to_string(),
    }
}
fn line(inputs: Option<&Value>, commit: Option<&Value>, unproven: bool) -> Value {
    let mut out = serde_json::Map::new();
    if let Some(v) = inputs.filter(|v| truthy(v)) {
        out.insert("inputs".into(), v.clone());
    }
    if let Some(v) = commit.filter(|v| truthy(v)) {
        out.insert("commit".into(), v.clone());
    }
    if unproven {
        out.insert("unproven".into(), json!(true));
    }
    Value::Object(out)
}

pub fn made_lines(v: &Value) -> Result<Value> {
    let mut out = serde_json::Map::new();
    let derived = names(&v["derived"]);
    let moved = names(&v["moved"]);
    let refuted = names(&v["refuted"]);
    for relative in names(&v["members"]) {
        let held = &v["held"][&relative];
        let tree = &v["tree"][&relative];
        let value = if derived.contains(&relative) {
            let cut = &v["cut"][&relative];
            line(Some(cut), Some(&v["head"]), cut != tree)
        } else if moved.contains(&relative) || !held.is_object() || !truthy(held) {
            line(None, Some(&v["head"]), true)
        } else if !truthy(&held["inputs"]) {
            held.clone()
        } else if held["inputs"] == *tree && !refuted.contains(&relative) {
            if truthy(&held["unproven"]) {
                line(Some(&held["inputs"]), Some(&v["head"]), false)
            } else {
                held.clone()
            }
        } else if truthy(&held["unproven"]) {
            held.clone()
        } else {
            line(Some(&held["inputs"]), held.get("commit"), true)
        };
        out.insert(relative, value);
    }
    Ok(Value::Object(out))
}

pub fn dispatch(v: &Value) -> Result<Option<Value>> {
    if let Some(result) = state::dispatch(v)? {
        return Ok(Some(result));
    }
    let text = |key: &str| v[key].as_str().with_context(|| format!("{key} is text"));
    let result = match text("op")? {
        "publication-retired" => json!(retired(Path::new(text("root")?), text("path")?)),
        "publication-website-paths" => json!(website_paths(
            Path::new(text("root")?),
            &strings(&v["available"]),
            &v["config"]
        )?),
        "publication-solids" => json!(solids(Path::new(text("root")?), &v["config"])?),
        "publication-frozen-assets" => json!(frozen_assets(Path::new(text("root")?))?),
        "publication-member" => {
            let root = Path::new(text("root")?);
            let catalog = if root.join("hardware/ledger/materials.json").is_file() {
                website_paths(root, &[], &v["config"])?
            } else {
                BTreeSet::new()
            };
            json!(member(
                text("path")?,
                root,
                &names(&v["frozen"]),
                &catalog,
                &v["config"]
            ))
        }
        "publication-line" => line(v.get("inputs"), v.get("commit"), truthy(&v["unproven"])),
        "publication-line-times" => {
            let mut out = serde_json::Map::new();
            for (relative, digest) in v["hashes"].as_object().context("solid hashes")? {
                let old = &v["held"]["solids"][relative];
                let time = v["held"]["moved"].get(relative);
                out.insert(
                    relative.clone(),
                    if old == digest && time.is_some() {
                        time.unwrap().clone()
                    } else {
                        v["stamp"].clone()
                    },
                );
            }
            Value::Object(out)
        }
        "publication-held-plan" => {
            let (mut built, mut fresh, mut stale) = (Vec::new(), Vec::new(), Vec::new());
            for relative in strings(&v["rels"]) {
                let Some(old) = v["held"]["solids"].get(&relative) else {
                    fresh.push(relative);
                    continue;
                };
                if *old != v["now"][&relative] {
                    if v["mtimes"][&relative].as_f64().unwrap_or(0.)
                        > v["held"]["moved"][&relative].as_f64().unwrap_or(0.)
                    {
                        built.push(relative);
                    } else {
                        stale.push(relative);
                    }
                }
            }
            let absent = v["held"]["solids"]
                .as_object()
                .map(|m| {
                    m.keys()
                        .filter(|k| v["now"].get(*k).is_none())
                        .cloned()
                        .collect::<Vec<_>>()
                })
                .unwrap_or_default();
            json!([built, fresh, stale, absent])
        }
        "publication-made-lines" => made_lines(v)?,
        "publication-made-moves" => {
            let mut out = Vec::new();
            for (relative, digest) in v["tree"].as_object().context("tree digests")? {
                let held = &v["held"][relative];
                if !held.is_object()
                    || truthy(&held["inputs"])
                        && ((held["inputs"] == *digest) == truthy(&held["unproven"]))
                {
                    out.push(relative.clone());
                }
            }
            json!(out)
        }
        "publication-cut-after-inputs" => {
            let root = Path::new(text("root")?);
            let written = crate::artifact_cache::identity(&root.join(text("path")?)).ok();
            let writers = names(&v["writers"]);
            let skew = v["skew_ns"].as_i64().unwrap_or(0);
            json!(
                written.is_some_and(|written| strings(&v["inputs"]).iter().all(|input| {
                    crate::artifact_cache::identity(&root.join(input))
                        .ok()
                        .is_none_or(|changed| {
                            changed[3]
                                <= written[3] + if writers.contains(input) { skew } else { 0 }
                        })
                }))
            )
        }
        _ => return Ok(None),
    };
    Ok(Some(result))
}
