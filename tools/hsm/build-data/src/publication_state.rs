//! Publication plans, ordered provenance records and pointer-file transformations.
use super::{archive, frozen_assets, member, names, starts, strings, truthy, website_paths};
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::Path,
};

const KEYS: [&str; 10] = [
    "_", "release", "store", "bundle", "solids", "sidecars", "website", "mesh_assets", "moved", "made",
];
const NOTE: &str = "The pointer file: main points at these bytes on the release, by hash. Written by tools/cad-artifacts/pack.py; web/scripts/fetch-cad-artifacts.mjs reads it at deploy.";
type Pairs = Vec<(String, Value)>;
fn pairs(v: &Value) -> Pairs {
    v["_publication_pairs"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|r| Some((r[0].as_str()?.into(), r[1].clone())))
                .collect()
        })
        .unwrap_or_default()
}
fn ordered(p: Pairs) -> Value {
    json!({"_publication_pairs":p})
}
fn field(v: &Value, key: &str) -> Option<Value> {
    pairs(v).into_iter().find(|(k, _)| k == key).map(|(_, v)| v)
}
fn object(v: &Value) -> Value {
    ordered(
        v.as_object()
            .map(|m| {
                m.iter()
                    .map(|(k, v)| (k.clone(), if v.is_object() { object(v) } else { v.clone() }))
                    .collect()
            })
            .unwrap_or_default(),
    )
}
fn line(inputs: Option<&Value>, commit: Option<&Value>, unproven: bool) -> Value {
    let mut out = Vec::new();
    if let Some(v) = inputs.filter(|v| truthy(v)) {
        out.push(("inputs".into(), v.clone()));
    }
    if let Some(v) = commit.filter(|v| truthy(v)) {
        out.push(("commit".into(), v.clone()));
    }
    if unproven {
        out.push(("unproven".into(), json!(true)));
    }
    ordered(out)
}
fn made_lines(v: &Value) -> Value {
    let held_order = &v["held_order"];
    let derived = names(&v["derived"]);
    let moved = names(&v["moved"]);
    let refuted = names(&v["refuted"]);
    let mut out = Vec::new();
    for rel in names(&v["members"]) {
        let held = &v["held"][&rel];
        let tree = &v["tree"][&rel];
        let prior = field(held_order, &rel).unwrap_or_else(|| object(held));
        let value = if derived.contains(&rel) {
            let cut = &v["cut"][&rel];
            line(Some(cut), Some(&v["head"]), cut != tree)
        } else if moved.contains(&rel) || !held.is_object() || !truthy(held) {
            line(None, Some(&v["head"]), true)
        } else if !truthy(&held["inputs"]) {
            prior
        } else if held["inputs"] == *tree && !refuted.contains(&rel) {
            if truthy(&held["unproven"]) {
                line(Some(&held["inputs"]), Some(&v["head"]), false)
            } else {
                prior
            }
        } else if truthy(&held["unproven"]) {
            prior
        } else {
            line(Some(&held["inputs"]), held.get("commit"), true)
        };
        out.push((rel, value));
    }
    ordered(out)
}
fn made_for(v: &Value) -> Value {
    let mut args = v.clone();
    args["members"] = json!(
        v["tree"]
            .as_object()
            .map(|m| m.keys().cloned().collect::<Vec<_>>())
            .unwrap_or_default()
    );
    let mut out: BTreeMap<_, _> = pairs(&made_lines(&args)).into_iter().collect();
    if let Some(held) = v["held"].as_object() {
        for (rel, value) in held {
            if v["lines"].get(rel).is_some() && !out.contains_key(rel) {
                out.insert(
                    rel.clone(),
                    field(&v["held_order"], rel).unwrap_or_else(|| object(value)),
                );
            }
        }
    }
    let moved = names(&v["moved"]);
    for rel in names(&v["frozen"]) {
        if v["lines"].get(&rel).is_some() && (moved.contains(&rel) || !out.contains_key(&rel)) {
            out.insert(rel, line(None, Some(&v["head"]), true));
        }
    }
    ordered(out.into_iter().collect())
}
fn pretty(v: &Value, depth: usize) -> Result<String> {
    let object = v.get("_publication_pairs").is_some();
    if object || v.is_array() {
        let indent = "  ".repeat(depth + 1);
        let values = if object {
            pairs(v)
                .into_iter()
                .map(|(k, v)| {
                    Ok(format!(
                        "{}: {}",
                        ascii_json(&serde_json::to_string(&k)?),
                        pretty(&v, depth + 1)?
                    ))
                })
                .collect::<Result<Vec<_>>>()?
        } else {
            v.as_array()
                .unwrap()
                .iter()
                .map(|v| pretty(v, depth + 1))
                .collect::<Result<Vec<_>>>()?
        };
        let (open, close) = if object { ('{', '}') } else { ('[', ']') };
        return Ok(if values.is_empty() {
            format!("{open}{close}")
        } else {
            format!(
                "{open}\n{indent}{}\n{}{close}",
                values.join(&format!(",\n{indent}")),
                "  ".repeat(depth)
            )
        });
    }
    if v.as_number().is_some_and(serde_json::Number::is_f64) {
        return hsm_documents::interop::Val::decode(v.clone())?.str();
    }
    Ok(ascii_json(&serde_json::to_string(v)?))
}
fn ascii_json(text: &str) -> String {
    crate::payload::ascii_json(text).replace('\x7f', "\\u007f")
}
fn pointer_file(v: &Value) -> Value {
    let mut out = Vec::new();
    for key in KEYS {
        if let Some(value) = field(v, key).filter(|v| !v.is_null()) {
            let value = if matches!(key, "solids" | "sidecars") {
                let mut entries = pairs(&value);
                entries.sort_by(|a, b| a.0.cmp(&b.0));
                ordered(entries)
            } else {
                value
            };
            out.push((key.into(), value));
        }
    }
    ordered(out)
}
fn website(root: &Path, data: &Value, config: &Value) -> Result<Value> {
    let available = data["solids"]
        .as_object()
        .map(|m| m.keys().cloned().collect::<Vec<_>>())
        .unwrap_or_default();
    let allowed = website_paths(root, &available, config)?;
    let mut out = serde_json::Map::new();
    for kind in ["solids", "sidecars"] {
        out.insert(
            kind.into(),
            Value::Object(
                data[kind]
                    .as_object()
                    .map(|m| {
                        m.iter()
                            .filter(|(p, _)| allowed.contains(*p))
                            .map(|(p, d)| (p.clone(), d.clone()))
                            .collect()
                    })
                    .unwrap_or_default(),
            ),
        );
    }
    Ok(Value::Object(out))
}
fn read_ordered(bytes: Vec<u8>) -> Result<Value> {
    use hsm_documents::interop::{self, Val};
    interop::builtin_module("json")
        .context("native JSON module")?
        .attr("loads")?
        .call(vec![Val::Bytes(bytes)], vec![])?
        .encode()
}
fn read_pointers(root: &Path) -> Value {
    fs::read(root.join("hardware/cad-artifacts.json"))
        .ok()
        .and_then(|b| serde_json::from_slice(&b).ok())
        .unwrap_or_else(|| json!({}))
}
fn graph_file(root: &Path) -> Option<Value> {
    fs::read(root.join("tools/bazel/graph.json"))
        .ok()
        .and_then(|b| serde_json::from_slice(&b).ok())
}
fn declared(root: &Path, config: &Value, same_root: bool) -> Result<BTreeSet<String>> {
    let frozen = frozen_assets(root)?
        .keys()
        .cloned()
        .collect::<BTreeSet<_>>();
    let mut declared = frozen.clone();
    let Some(graph) = graph_file(root) else {
        return Ok(declared);
    };
    if let Some(rows) = graph.as_object() {
        for row in rows.values() {
            declared.extend(names(&row["writes"]));
        }
    }
    if same_root {
        if let Some(entries) = config["IMPLICIT_SOLIDS"].as_object() {
            for paths in entries.values() {
                declared.extend(names(paths));
            }
        }
        let middle = names(&config["ACTION_INTERMEDIATE"]);
        declared.retain(|p| !middle.contains(p));
    }
    let catalog = if root.join("hardware/ledger/materials.json").is_file() {
        website_paths(root, &[], config)?
    } else {
        BTreeSet::new()
    };
    declared.retain(|p| member(p, root, &frozen, &catalog, config));
    Ok(declared)
}
fn sidecars(root: &Path, graph: &Value) -> BTreeSet<String> {
    let keys = if let Some(writers) = graph["writers"].as_object() {
        writers.keys().cloned().collect()
    } else {
        graph_file(root)
            .and_then(|g| {
                g.as_object().map(|m| {
                    m.values()
                        .flat_map(|r| names(&r["writes"]))
                        .collect::<BTreeSet<_>>()
                })
            })
            .unwrap_or_default()
    };
    keys.into_iter()
        .filter(|p| p.ends_with(".scorecard.json"))
        .collect()
}
fn object_asset(prefix: &str, digest: &str) -> String {
    format!("{prefix}{digest}.gz")
}
fn pointer_assets(held: &Value, prefix: &str) -> BTreeSet<String> {
    let mut names = BTreeSet::new();
    for kind in ["solids", "sidecars"] {
        if let Some(m) = held[kind].as_object() {
            for digest in m.values().filter_map(Value::as_str) {
                names.insert(object_asset(prefix, digest));
            }
        }
    }
    if let Some(asset) = held["release"]["asset"].as_str().filter(|s| !s.is_empty()) {
        names.insert(asset.into());
    }
    names
}
fn origin_slug(url: &str) -> String {
    let slug = url
        .trim()
        .split_once("github.com")
        .map(|(_, s)| s)
        .unwrap_or(url.trim())
        .trim_start_matches([':', '/']);
    slug.strip_suffix(".git").unwrap_or(slug).into()
}
fn object_url(held: &Value, digest: &str) -> Option<String> {
    let store = &held["store"];
    if truthy(&store["url"]) && truthy(&store["objects"]) {
        return Some(format!(
            "{}{}{digest}.gz",
            store["url"].as_str()?,
            store["objects"].as_str()?
        ));
    }
    let release = &held["release"];
    let url = release["url"].as_str().unwrap_or("");
    if !truthy(&release["objects"]) {
        return None;
    }
    let index = url.rfind('/')?;
    Some(format!(
        "{}{}{digest}.gz",
        &url[..index + 1],
        release["objects"].as_str()?
    ))
}
fn line_times(held: &Value, hashes: &Value, stamp: &Value) -> Value {
    let mut out = serde_json::Map::new();
    if let Some(hashes) = hashes.as_object() {
        for (rel, digest) in hashes {
            out.insert(
                rel.clone(),
                if held["solids"].get(rel) == Some(digest) && held["moved"].get(rel).is_some() {
                    held["moved"][rel].clone()
                } else {
                    stamp.clone()
                },
            );
        }
    }
    Value::Object(out)
}
fn pointers(v: &Value) -> Result<Value> {
    let digest = v["digest"].as_str().context("bundle digest")?;
    let asset = format!("cad-{}.tar.gz", digest.chars().take(16).collect::<String>());
    let slug = v["slug"].as_str().context("repository slug")?;
    let tag = v["tag"].as_str().context("release tag")?;
    let made = if truthy(&v["made"]) {
        v["made_order"].clone()
    } else {
        Value::Null
    };
    Ok(ordered(vec![
        ("_".into(), json!(NOTE)),
        (
            "release".into(),
            ordered(vec![
                ("tag".into(), json!(tag)),
                ("asset".into(), json!(asset)),
                (
                    "url".into(),
                    json!(format!(
                        "https://github.com/{slug}/releases/download/{tag}/{asset}"
                    )),
                ),
            ]),
        ),
        (
            "store".into(),
            ordered(vec![
                ("url".into(), v["store_url"].clone()),
                ("objects".into(), v["prefix"].clone()),
            ]),
        ),
        (
            "bundle".into(),
            ordered(vec![
                ("sha256".into(), json!(digest)),
                ("bytes".into(), v["size"].clone()),
                ("solids".into(), json!(strings(&v["rels"]).len())),
            ]),
        ),
        ("solids".into(), v["hashes_order"].clone()),
        ("sidecars".into(), v["sidecar_order"].clone()),
        ("mesh_assets".into(), v["held"]["mesh_assets"].clone()),
        (
            "moved".into(),
            object(&line_times(&v["held"], &v["hashes"], &v["stamp"])),
        ),
        ("made".into(), made),
    ]))
}

fn civil_days(year: i64, month: i64, day: i64) -> i64 {
    let year = year - i64::from(month <= 2);
    let era = year.div_euclid(400);
    let y = year - era * 400;
    let m = month + if month > 2 { -3 } else { 9 };
    let doy = (153 * m + 2) / 5 + day - 1;
    era * 146097 + y * 365 + y / 4 - y / 100 + doy - 719468
}
fn week_ordinal(year: i64, week: i64, weekday: i64) -> Option<i64> {
    if !(1..=9999).contains(&year) || !(1..=7).contains(&weekday) {
        return None;
    }
    let first = |y| {
        let jan4 = civil_days(y, 1, 4);
        jan4 - (jan4 + 3).rem_euclid(7)
    };
    if week < 1 || week > (first(year + 1) - first(year)) / 7 {
        return None;
    }
    Some(first(year) + (week - 1) * 7 + weekday - 1 - civil_days(year, 1, 1) + 1)
}
fn timestamp(text: &str) -> Option<f64> {
    // GitHub timestamps use RFC3339; retain Python's basic ISO calendar/time spellings too.
    let (year, month, day, date, week_date): (i64, i64, i64, &str, bool) = if text.len() >= 8
        && text.as_bytes().get(4) == Some(&b'-')
        && text.as_bytes().get(5) == Some(&b'W')
    {
        let year = text.get(..4)?.parse::<i64>().ok()?;
        let week = text.get(6..8)?.parse::<i64>().ok()?;
        let (day, end) = if text.as_bytes().get(8) == Some(&b'-') {
            (text.get(9..10)?.parse::<i64>().ok()?, 10)
        } else {
            (1, 8)
        };
        let ordinal = week_ordinal(year, week, day)?;
        (year, 1, ordinal, text.get(end..)?, true)
    } else if text.len() >= 7 && text.as_bytes().get(4) == Some(&b'W') {
        let year = text.get(..4)?.parse::<i64>().ok()?;
        let week = text.get(5..7)?.parse::<i64>().ok()?;
        let (day, end) = if text.as_bytes().get(7).is_some_and(u8::is_ascii_digit) {
            (text.get(7..8)?.parse::<i64>().ok()?, 8)
        } else {
            (1, 7)
        };
        let ordinal = week_ordinal(year, week, day)?;
        (year, 1, ordinal, text.get(end..)?, true)
    } else if text.len() >= 10
        && text.as_bytes().get(4) == Some(&b'-')
        && text.as_bytes().get(7) == Some(&b'-')
    {
        (
            text.get(..4)?.parse().ok()?,
            text.get(5..7)?.parse().ok()?,
            text.get(8..10)?.parse().ok()?,
            text.get(10..)?,
            false,
        )
    } else if text.len() >= 8 && text.as_bytes()[..8].iter().all(u8::is_ascii_digit) {
        (
            text.get(..4)?.parse().ok()?,
            text.get(4..6)?.parse().ok()?,
            text.get(6..8)?.parse().ok()?,
            text.get(8..)?,
            false,
        )
    } else {
        return None;
    };
    let local = |clock: f64| {
        let whole = clock.trunc() as i64;
        let mut tm = unsafe { std::mem::zeroed::<libc::tm>() };
        tm.tm_year = (year - 1900) as i32;
        tm.tm_mon = (month - 1) as i32;
        tm.tm_mday = day as i32;
        tm.tm_hour = (whole / 3600) as i32;
        tm.tm_min = ((whole / 60) % 60) as i32;
        tm.tm_sec = (whole % 60) as i32;
        tm.tm_isdst = -1;
        (unsafe { libc::mktime(&mut tm) }) as f64 + clock.fract()
    };
    if !(1..=9999).contains(&year) || !(1..=12).contains(&month) {
        return None;
    }
    let leap = year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
    let limit = [
        31,
        if leap { 29 } else { 28 },
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ][month as usize - 1];
    if !week_date && (day < 1 || day > limit) {
        return None;
    }
    let days = civil_days(year, month, day) as f64;
    if date.is_empty() {
        return Some(local(0.));
    }
    let mut chars = date.chars();
    chars.next()?;
    let time = chars.as_str();
    if time.is_empty() {
        return None;
    }
    let zone_index = time.find(['+', '-', 'Z']);
    let (clock, zone) = zone_index
        .map(|i| (&time[..i], &time[i..]))
        .unwrap_or((time, ""));
    fn hms(text: &str) -> Option<f64> {
        let (main, fraction) = text
            .split_once(['.', ','])
            .map(|(a, b)| (a, Some(b)))
            .unwrap_or((text, None));
        let values = if main.contains(':') {
            main.split(':')
                .map(str::parse::<u32>)
                .collect::<std::result::Result<Vec<_>, _>>()
                .ok()?
        } else {
            if main.len() % 2 != 0 {
                return None;
            }
            main.as_bytes()
                .chunks(2)
                .map(|p| std::str::from_utf8(p).ok()?.parse::<u32>().ok())
                .collect::<Option<Vec<_>>>()?
        };
        if values.is_empty()
            || values.len() > 3
            || values[0] > 23
            || values.get(1).is_some_and(|m| *m > 59)
            || values.get(2).is_some_and(|s| *s > 59)
        {
            return None;
        }
        let frac = if let Some(f) = fraction {
            if f.is_empty() || !f.bytes().all(|b| b.is_ascii_digit()) {
                return None;
            }
            format!("0.{}", f.chars().take(6).collect::<String>())
                .parse::<f64>()
                .ok()?
        } else {
            0.
        };
        Some(
            f64::from(values[0]) * 3600.
                + f64::from(*values.get(1).unwrap_or(&0)) * 60.
                + f64::from(*values.get(2).unwrap_or(&0))
                + frac,
        )
    }
    let clock = hms(clock)?;
    if zone.is_empty() {
        return Some(local(clock));
    }
    let offset = if zone == "Z" {
        0.
    } else {
        let seconds = hms(&zone[1..])?;
        if zone.starts_with('-') {
            -seconds
        } else {
            seconds
        }
    };
    Some(days * 86400. + clock - offset)
}
fn too_new(assets: &Value, now: f64, floor: f64) -> BTreeSet<String> {
    assets
        .as_array()
        .into_iter()
        .flatten()
        .filter(|a| {
            a["createdAt"]
                .as_str()
                .and_then(timestamp)
                .is_none_or(|born| now - born < floor)
        })
        .map(|a| a["name"].as_str().unwrap_or("").into())
        .collect()
}
pub fn target_name(generator: &str, shared: &BTreeSet<String>) -> String {
    let path = Path::new(generator);
    let stem = path
        .file_stem()
        .unwrap_or_default()
        .to_string_lossy()
        .trim_matches('_')
        .replace('_', "-");
    if stem == "build" || shared.contains(&stem) {
        format!(
            "{}-{stem}",
            path.parent()
                .and_then(Path::file_name)
                .unwrap_or_default()
                .to_string_lossy()
        )
    } else {
        stem
    }
}
fn inventory_targets(rows: &Value) -> Vec<(String, BTreeSet<String>)> {
    let mut seen = BTreeSet::new();
    let mut shared = BTreeSet::new();
    if let Some(rows) = rows.as_array() {
        for row in rows {
            for generator in strings(&row[0]) {
                let stem = Path::new(&generator)
                    .file_stem()
                    .unwrap_or_default()
                    .to_string_lossy()
                    .trim_matches('_')
                    .replace('_', "-");
                if !seen.insert(stem.clone()) {
                    shared.insert(stem);
                }
            }
        }
    }
    let mut out = Vec::new();
    if let Some(rows) = rows.as_array() {
        for row in rows {
            if let Some(generator) = row[0][0].as_str() {
                out.push((
                    format!("//:{}", target_name(generator, &shared)),
                    names(&row[1]["solids"]),
                ));
            }
        }
    }
    out
}
fn tree_digests(v: &Value) -> Result<Value> {
    let mut no_callback = |_: Value| -> Result<Value> {
        anyhow::bail!("native identity unexpectedly requested a callback")
    };
    let id = crate::artifacts::dispatch(&json!({"op":"artifact-identity-id"}), &mut no_callback)?
        .context("identity id")?;
    let mut out = Vec::new();
    for rel in strings(&v["line_order"]) {
        if v["graph"]["writers"].get(&rel).is_none() {
            continue;
        }
        let digest=crate::artifacts::dispatch(&json!({"op":"artifact-digest","graph":v["graph"],"path":rel,"identity":{"kind":"committed","index":v["index"],"lines":v["lines"]},"id":id}),&mut no_callback)?.context("input digest")?;
        out.push((rel, digest));
    }
    Ok(ordered(out))
}
fn bytes_drifted(v: &Value) -> Vec<String> {
    let mut out = Vec::new();
    for (kind, now) in [("solids", &v["hashes"]), ("sidecars", &v["sidecar_hashes"])] {
        if let Some(now) = now.as_object() {
            for (rel, digest) in now {
                if v["held"][kind].get(rel) != Some(digest) {
                    out.push(rel.clone());
                }
            }
        }
    }
    out.sort();
    out
}
fn sidecar_paths(root: &Path, held: &Value) -> Vec<String> {
    held["sidecars"]
        .as_object()
        .map(|m| {
            m.keys()
                .filter(|p| root.join(p).is_file())
                .cloned()
                .collect()
        })
        .unwrap_or_default()
}
fn heal(root: &Path, held: &Value, index: &Value, pointers: &str) -> Vec<String> {
    std::iter::once(pointers.to_owned())
        .chain(sidecar_paths(root, held))
        .filter(|p| index[p].as_str() != Some(crate::artifacts::blob_id(&root.join(p)).as_str()))
        .collect()
}

fn patch(data: &Value, path: &[String], value: &Value, remove: bool) -> Result<Value> {
    if path.is_empty() {
        return Ok(value.clone());
    }
    let mut entries = pairs(data);
    let key = &path[0];
    let previous = entries.iter().position(|(k, _)| k == key);
    if path.len() == 1 && remove {
        entries.retain(|(k, _)| k != key);
    } else {
        let old = previous
            .map(|i| entries[i].1.clone())
            .unwrap_or_else(|| ordered(Vec::new()));
        let changed = patch(&old, &path[1..], value, remove)?;
        if let Some(index) = previous {
            entries[index].1 = changed;
        } else {
            entries.push((key.clone(), changed));
        }
    }
    Ok(ordered(entries))
}
fn identity_id() -> Result<Value> {
    crate::artifacts::dispatch(&json!({"op":"artifact-identity-id"}), &mut |_| {
        anyhow::bail!("identity callback")
    })?
    .context("identity id")
}
fn input_digests(
    graph: &Value,
    identity: &Value,
    paths: impl IntoIterator<Item = String>,
) -> Result<Value> {
    let id = identity_id()?;
    let mut out = serde_json::Map::new();
    for rel in paths {
        let digest = crate::artifacts::dispatch(
            &json!({"op":"artifact-digest","graph":graph,"path":rel,"identity":identity,"id":id}),
            &mut |_| anyhow::bail!("identity callback"),
        )?
        .context("input digest")?;
        out.insert(rel, digest);
    }
    Ok(Value::Object(out))
}
fn cut_after(root: &Path, rel: &str, graph: &crate::artifacts::Graph, skew: i64) -> bool {
    let Ok(written) = crate::artifact_cache::identity(&root.join(rel)) else {
        return false;
    };
    graph.inputs(rel).iter().all(|input| {
        crate::artifact_cache::identity(&root.join(input))
            .ok()
            .is_none_or(|changed| {
                changed[3]
                    <= written[3]
                        + if graph.writers.contains_key(input) {
                            skew
                        } else {
                            0
                        }
            })
    })
}
fn made_here(v: &Value) -> Result<Value> {
    let root = Path::new(v["root"].as_str().context("root")?);
    let graph: crate::artifacts::Graph = serde_json::from_value(v["graph"].clone())?;
    let paths = v["lines"]
        .as_object()
        .map(|m| {
            m.keys()
                .filter(|p| graph.writers.contains_key(*p))
                .cloned()
                .collect::<BTreeSet<_>>()
        })
        .unwrap_or_default();
    let tree = input_digests(
        &v["graph"],
        &json!({"kind":"committed","index":v["index"],"lines":v["lines"]}),
        paths.iter().cloned(),
    )?;
    let moved = names(&v["moved"]);
    let grafted = names(&v["grafted"]);
    let derived = moved
        .intersection(&paths)
        .filter(|p| {
            !grafted.contains(*p) && cut_after(root, p, &graph, v["skew_ns"].as_i64().unwrap_or(0))
        })
        .cloned()
        .collect::<BTreeSet<_>>();
    let cut = input_digests(
        &v["graph"],
        &json!({"kind":"on_disk","root":v["root"],"index":v["index"],"lines":v["lines"],"members":v["walked"]}),
        derived.iter().cloned(),
    )?;
    let mut args = v.clone();
    args["tree"] = tree;
    args["cut"] = cut;
    args["held"] = v["held"]["made"]
        .as_object()
        .map(|m| Value::Object(m.clone()))
        .unwrap_or_else(|| json!({}));
    args["held_order"] = field(&v["held_order"], "made").unwrap_or_else(|| ordered(vec![]));
    args["derived"] = json!(derived);
    args["moved"] = json!(moved.difference(&derived).cloned().collect::<Vec<_>>());
    Ok(made_for(&args))
}
fn map_changes(old: &Value, new: &Value) -> Value {
    let moved = new
        .as_object()
        .into_iter()
        .flatten()
        .filter(|(k, d)| old.get(*k).is_some_and(|x| x != *d))
        .map(|(k, _)| k.clone())
        .collect::<Vec<_>>();
    let fresh = new
        .as_object()
        .into_iter()
        .flatten()
        .filter(|(k, _)| old.get(*k).is_none())
        .map(|(k, _)| k.clone())
        .collect::<Vec<_>>();
    let gone = old
        .as_object()
        .into_iter()
        .flatten()
        .filter(|(k, _)| new.get(*k).is_none())
        .map(|(k, _)| k.clone())
        .collect::<Vec<_>>();
    json!([moved, fresh, gone])
}
fn held_state(v: &Value) -> Value {
    let held = &v["held"];
    let now = &v["now"];
    let mut pinned = strings(&v["rels"]);
    let mut built = Vec::new();
    let mut fresh = Vec::new();
    let mut stale = Vec::new();
    let mut absent = Vec::new();
    if truthy(&held["solids"]) {
        for rel in strings(&v["rels"]) {
            let Some(old) = held["solids"].get(&rel) else {
                fresh.push(rel);
                continue;
            };
            if *old != now[&rel] {
                if v["mtimes"][&rel].as_f64().unwrap_or(0.)
                    > held["moved"][&rel].as_f64().unwrap_or(0.)
                {
                    built.push(rel);
                } else {
                    stale.push(rel);
                }
            }
        }
        absent = held["solids"]
            .as_object()
            .into_iter()
            .flatten()
            .filter(|(p, _)| now.get(*p).is_none())
            .map(|(p, _)| p.clone())
            .collect();
        pinned = built.iter().chain(&fresh).cloned().collect();
    }
    let side_moved = v["sidecar_now"]
        .as_object()
        .into_iter()
        .flatten()
        .filter(|(p, d)| held["sidecars"].get(*p) != Some(*d))
        .map(|(p, _)| p.clone())
        .collect::<Vec<_>>();
    let mut lines = held["solids"].as_object().cloned().unwrap_or_default();
    for rel in &pinned {
        lines.insert(rel.clone(), now[rel].clone());
    }
    let moved = pinned
        .iter()
        .chain(&side_moved)
        .cloned()
        .collect::<BTreeSet<_>>();
    let mut whole = now.as_object().cloned().unwrap_or_default();
    whole.extend(v["sidecar_now"].as_object().cloned().unwrap_or_default());
    json!({"pinned":pinned,"built":built,"fresh":fresh,"stale":stale,"absent":absent,"side_moved":side_moved,"lines":lines,"moved":moved,"whole":whole})
}

pub fn dispatch(v: &Value) -> Result<Option<Value>> {
    let text = |key: &str| v[key].as_str().with_context(|| format!("{key} is text"));
    let root = || -> Result<&Path> { Ok(Path::new(text("root")?)) };
    let result = match text("op")? {
        "publication-read-pointers-ordered" => {
            fs::read(root()?.join("hardware/cad-artifacts.json"))
                .ok()
                .and_then(|b| read_ordered(b).ok())
                .unwrap_or_else(|| json!({"$dict":[]}))
        }
        "publication-pointer-state-ordered" => match fs::read(root()?.join(text("pointers")?)) {
            Ok(bytes) => json!({"missing":false,"ordered":read_ordered(bytes)?}),
            Err(_) => json!({"missing":true}),
        },

        "publication-website-ordered" => {
            let data = website(root()?, &v["data"], &v["config"])?;
            ordered(
                ["solids", "sidecars"]
                    .into_iter()
                    .map(|kind| (kind.into(), object(&data[kind])))
                    .collect(),
            )
        }

        "publication-untracked-paths" => json!(
            strings(&v["paths"])
                .into_iter()
                .filter(|p| v["index"].get(p).is_none())
                .collect::<Vec<_>>()
        ),
        "publication-member-policy" => {
            let root = root()?;
            let catalog = if root.join("hardware/ledger/materials.json").is_file() {
                website_paths(root, &[], &v["config"])?
            } else {
                BTreeSet::new()
            };
            json!({"root":root,"catalog":catalog,"frozen":v["frozen"],"config":v["config"]})
        }
        "publication-member-prepared" => {
            let policy = &v["policy"];
            let mut config = policy["config"].clone();
            for key in ["HARVESTED", "BOARD_NOT_BUNDLED", "BUNDLED_ART_SUFFIXES"] {
                config[key] = v["config"][key].clone();
            }
            json!(member(
                text("path")?,
                Path::new(policy["root"].as_str().context("policy root")?),
                &names(&policy["frozen"]),
                &names(&policy["catalog"]),
                &config
            ))
        }

        "publication-reconcile-state" => {
            json!({"same_solids":v["held"]["solids"]==v["now"],"same_sidecars":v["held"]["sidecars"]==v["sidecars"],"solids":map_changes(&v["held"]["solids"],&v["now"]),"sidecars":map_changes(&v["held"]["sidecars"],&v["sidecars"])})
        }
        "publication-reconcile-records" => {
            let old = &v["held"]["release"]["objects"];
            let new = if truthy(&v["complete"]) {
                v["prefix"].clone()
            } else {
                Value::Null
            };
            let old_made = if truthy(&v["held"]["made"]) {
                v["held"]["made"].clone()
            } else {
                json!({})
            };
            let changed =
                old_made != v["made"] || *old != new || v["held"]["website"] != v["website"];
            let mut data = patch(
                &v["held_order"],
                &["release".into(), "objects".into()],
                &new,
                !truthy(&v["complete"]),
            )?;
            data = patch(&data, &["made".into()], &v["made_order"], false)?;
            json!({"changed":changed,"ordered":data})
        }

        "publication-patch" => {
            let mut data = v["ordered"].clone();
            for update in v["updates"].as_array().context("updates")? {
                data = patch(
                    &data,
                    &strings(&update["path"]),
                    &update["value"],
                    truthy(&update["delete"]),
                )?;
            }
            data
        }
        "publication-unique" => json!(names(&v["values"])),
        "publication-map-values" => json!(
            strings(&v["paths"])
                .iter()
                .map(|p| v["data"][p].clone())
                .collect::<Vec<_>>()
        ),
        "publication-release-state" => {
            let old = v["assets"]
                .as_array()
                .into_iter()
                .flatten()
                .filter(|a| a["name"] == v["asset"])
                .last();
            json!({"exists":old.is_some(),"matches":old.is_some_and(|a|a["state"]=="uploaded"&&a["size"]==v["size"]&&a["digest"]==json!(format!("sha256:{}",text("digest").unwrap_or(""))))})
        }

        "publication-zlib-info" => super::zlib::info()?,
        "publication-pointer-state" => {
            let path = root()?.join(text("pointers")?);
            match fs::read(path) {
                Ok(bytes) => {
                    json!({"missing":false,"held":serde_json::from_slice::<Value>(&bytes)?})
                }
                Err(_) => json!({"missing":true}),
            }
        }
        "publication-refresh-count" => json!(
            strings(&v["pieces"])
                .iter()
                .filter(|p| Path::new(p)
                    .file_stem()
                    .is_none_or(|s| s != "enclosure-pump-retainer"))
                .count()
        ),

        "publication-target-query" => json!(
            !strings(&v["members"]).is_empty()
                && root()?.canonicalize().ok() == Path::new(text("workspace")?).canonicalize().ok()
        ),
        "publication-made-here" => made_here(v)?,
        "publication-mtimes" => {
            let root = root()?;
            let mut out = serde_json::Map::new();
            for rel in strings(&v["rels"]) {
                let stat = crate::artifact_cache::identity(&root.join(&rel))?;
                out.insert(
                    rel,
                    json!(
                        (stat[3].div_euclid(1_000_000_000) as f64
                            + stat[3].rem_euclid(1_000_000_000) as f64 * 1e-9)
                            .trunc() as i64
                    ),
                );
            }
            Value::Object(out)
        }
        "publication-held-state" => held_state(v),
        "publication-held-record-state" => {
            let keys = v["made"]
                .as_object()
                .into_iter()
                .flatten()
                .map(|(p, _)| p.clone())
                .chain(
                    v["held"]["made"]
                        .as_object()
                        .into_iter()
                        .flatten()
                        .map(|(p, _)| p.clone()),
                )
                .collect::<BTreeSet<_>>();
            let shifted = keys
                .iter()
                .filter(|p| v["made"].get(*p) != v["held"]["made"].get(*p))
                .count();
            json!({"shifted":shifted,"unchanged":strings(&v["side_moved"]).is_empty()&&shifted==0&&v["website"]==v["held"]["website"]})
        }
        "publication-merge-lines" => {
            let mut out = serde_json::Map::new();
            for map in v["maps"].as_array().context("maps")? {
                out.extend(map.as_object().cloned().unwrap_or_default());
            }
            Value::Object(out)
        }
        "publication-updated-lines" => {
            let mut out = v["held"].as_object().cloned().unwrap_or_default();
            for p in strings(&v["paths"]) {
                out.insert(p.clone(), v["new"][&p].clone());
            }
            Value::Object(out)
        }
        "publication-changed-lines" => {
            let mut out = Vec::new();
            if let Some(now) = v["new"].as_object() {
                for (p, d) in now {
                    if v["old"].get(p) != Some(d) {
                        out.push(p.clone());
                    }
                }
            }
            json!(out)
        }
        "publication-set-plan" => {
            let first = names(&v["first"]);
            let second = names(&v["second"]);
            let third = names(&v["third"]);
            json!({"union":first.union(&second).cloned().collect::<BTreeSet<_>>(),"difference":first.difference(&second).cloned().collect::<BTreeSet<_>>(),"intersection":first.intersection(&second).cloned().collect::<BTreeSet<_>>(),"remaining":first.difference(&second).filter(|p|!third.contains(*p)).cloned().collect::<BTreeSet<_>>()})
        }
        "publication-dirty-inputs" => {
            let omit = names(&v["sidecars"])
                .union(&names(&v["held_sidecars"]))
                .cloned()
                .collect::<BTreeSet<_>>();
            let presentation = names(&v["presentation"]);
            json!(
                names(&v["moved"])
                    .into_iter()
                    .filter(|p| p != "hardware/cad-artifacts.json"
                        && !omit.contains(p)
                        && !presentation.contains(p))
                    .collect::<Vec<_>>()
            )
        }
        "publication-behind" => {
            let owed = text("stderr")?
                .lines()
                .filter(|s| s.contains("not up-to-date"))
                .collect::<Vec<_>>();
            json!(
                v["returncode"] != 0
                    && (!owed
                        .iter()
                        .all(|s| s.contains("BazelWorkspaceStatusAction"))
                        || owed.is_empty())
            )
        }
        "publication-unheld" => {
            let mut out = BTreeSet::new();
            for row in v["pairs"].as_array().context("cut pairs")? {
                if !truthy(&row[2]) {
                    continue;
                }
                let built = Path::new(row[0].as_str().context("built path")?);
                let relative = row[1].as_str().context("relative path")?;
                let here = root()?.join(relative);
                if built.is_file()
                    && (!here.is_file()
                        || crate::payload::digest(built)? != crate::payload::digest(here)?)
                {
                    out.insert(relative.to_owned());
                }
            }
            json!(out)
        }
        "publication-cut-digests" => input_digests(
            &v["graph"],
            &json!({"kind":"on_disk","root":v["root"],"index":v["index"],"lines":v["lines"],"members":v["members"]}),
            strings(&v["paths"]),
        )?,
        "publication-release-space" => {
            let held = v["assets"].as_array().map_or(0, |a| a.len()) as i64;
            json!([held, v["capacity"].as_i64().unwrap_or(1000) - held])
        }
        "publication-release-room" => {
            json!({"held":v["held"],"free":v["capacity"].as_i64().unwrap_or(1000)-v["held"].as_i64().unwrap_or(0),"unreachable":v["unreachable"],"superseded":v["superseded"]})
        }
        "publication-retire-plan" => {
            let mut going = strings(&v["state"]["unreachable"]);
            if !truthy(&v["unreachable_only"]) {
                going.extend(strings(&v["state"]["superseded"]));
            }
            json!(going)
        }
        "publication-copy-file" => {
            fs::copy(Path::new(text("source")?), Path::new(text("output")?))?;
            Value::Null
        }

        "publication-sha256" => json!(crate::payload::digest(Path::new(text("path")?))?),
        "publication-facets" => json!(archive::facets(Path::new(text("path")?))?),
        "publication-barren" => {
            let root = root()?;
            let mut out = Vec::new();
            let hashes = v["hashes"].as_object().context("solid hashes")?;
            for (rel, _) in hashes {
                if archive::facets(&root.join(rel))? == 0 {
                    out.push(format!(
                        "{rel} declares 0 facets — {} bytes, an empty solid",
                        root.join(rel).metadata()?.len()
                    ));
                }
            }
            let mut seen = BTreeMap::new();
            for (rel, sha) in hashes {
                if let Some(sha) = sha.as_str() {
                    if let Some(prior) = seen.get(sha) {
                        out.push(format!(
                            "{rel} carries the bytes {prior} carries — sha256 {}",
                            sha.chars().take(16).collect::<String>()
                        ));
                    } else {
                        seen.insert(sha, rel);
                    }
                }
            }
            json!(out)
        }
        "publication-build" => json!(archive::bundle(
            root()?,
            &strings(&v["rels"]),
            Path::new(text("output")?)
        )?),
        "publication-gzip" => {
            archive::gzip(
                Path::new(text("source")?),
                Path::new(text("output")?),
                v["level"].as_u64().unwrap_or(9) as u32,
            )?;
            Value::Null
        }
        "publication-gzip-many" => {
            let rows=v["files"].as_array().context("compression files")?;
            let level=v["level"].as_u64().unwrap_or(1) as u32;
            let next=std::sync::atomic::AtomicUsize::new(0);
            std::thread::scope(|scope| -> Result<()> {
                let workers=(0..rows.len().min(2)).map(|_|scope.spawn(|| -> Result<()> {
                    loop {
                        let index=next.fetch_add(1,std::sync::atomic::Ordering::Relaxed);
                        let Some(row)=rows.get(index) else {break;};
                        let source=Path::new(row["source"].as_str().context("compression source")?);
                        let output=Path::new(row["output"].as_str().context("compression output")?);
                        if output.is_file(){continue;}
                        fs::create_dir_all(output.parent().context("compression parent")?)?;
                        let temp=output.with_extension(format!("{}.tmp",std::process::id()));
                        archive::gzip(source,&temp,level)?;
                        fs::rename(temp,output)?;
                    }
                    Ok(())
                })).collect::<Vec<_>>();
                for worker in workers {worker.join().map_err(|_|anyhow::anyhow!("compression worker failed"))??;}
                Ok(())
            })?;
            Value::Null
        }
        "publication-freeze" => {
            let directory=Path::new(text("directory")?);fs::create_dir_all(directory)?;
            let mut out=Vec::new();
            for (index,row) in v["files"].as_array().context("publication files")?.iter().enumerate() {
                let source=Path::new(row["source"].as_str().context("publication source")?);
                let target=directory.join(format!("{index}.data"));
                fs::copy(source,&target)?;
                out.push(json!({"relative":row["relative"],"source":target,"sha256":crate::payload::digest(&target)?}));
            }
            json!(out)
        }
        "publication-decompress" => json!(archive::decompress(
            &serde_json::from_value::<Vec<u8>>(v["bytes"].clone())?
        )?),
        "publication-adopt-bytes" => json!(archive::adopt(
            root()?,
            text("path")?,
            text("digest")?,
            &serde_json::from_value::<Vec<u8>>(v["bytes"].clone())?
        )?),
        "publication-origin-slug" => json!(origin_slug(text("url")?)),
        "publication-object-asset" => json!(object_asset(text("prefix")?, text("digest")?)),
        "publication-object-url" => json!(object_url(&v["held"], text("digest")?)),
        "publication-line-ordered" => {
            line(v.get("inputs"), v.get("commit"), truthy(&v["unproven"]))
        }
        "publication-made-lines-ordered" => made_lines(v),
        "publication-made-for" => made_for(v),
        "publication-tree-digests" => tree_digests(v)?,
        "publication-pointers" => pointers(v)?,
        "publication-pointer-file" => pointer_file(&v["ordered"]),
        "publication-read-pointers" => read_pointers(root()?),
        "publication-website" => website(root()?, &v["data"], &v["config"])?,
        "publication-write-pointers" => {
            let root = root()?;
            let website = website(root, &v["data"], &v["config"])?;
            let mut entries = pairs(&v["ordered"]);
            entries.retain(|(k, _)| k != "website");
            entries.push((
                "website".into(),
                ordered(
                    ["solids", "sidecars"]
                        .into_iter()
                        .map(|k| (k.into(), object(&website[k])))
                        .collect(),
                ),
            ));
            let data = pointer_file(&ordered(entries));
            let path = Path::new(text("path")?);
            fs::create_dir_all(path.parent().context("pointer file parent")?)?;
            fs::write(path, pretty(&data, 0)? + "\n")?;
            Value::Null
        }
        "publication-declared" => json!(declared(root()?, &v["config"], truthy(&v["same_root"]))?),
        "publication-sidecars" => json!(sidecars(root()?, &v["graph"])),
        "publication-sidecar-lines" => {
            let root = root()?;
            let present = sidecars(root, &v["graph"])
                .into_iter()
                .filter(|p| root.join(p).is_file())
                .collect::<Vec<_>>();
            let here = present.iter().collect::<BTreeSet<_>>();
            let mut out = v["held"]["sidecars"]
                .as_object()
                .cloned()
                .unwrap_or_default();
            out.retain(|p, _| !here.contains(p));
            out.extend(
                crate::artifact_cache::hashes(root, &present)?
                    .into_iter()
                    .map(|(k, v)| (k, json!(v))),
            );
            Value::Object(out)
        }
        "publication-sidecar-debt" => {
            let root = root()?;
            let held = read_pointers(root);
            let mut out = Vec::new();
            for rel in sidecars(root, &Value::Null) {
                if !root.join(&rel).is_file()
                    || held["sidecars"][&rel].as_str()
                        != Some(crate::payload::digest(root.join(&rel))?.as_str())
                {
                    out.push(rel);
                }
            }
            json!(out)
        }
        "publication-graph-gaps" => {
            let declared = names(&v["declared"]);
            let present = names(&v["rels"])
                .into_iter()
                .filter(|p| !starts(p, &v["config"]["UNWATCHED_PRODUCERS"]))
                .collect::<BTreeSet<_>>();
            json!([
                present.difference(&declared).cloned().collect::<Vec<_>>(),
                declared.difference(&present).cloned().collect::<Vec<_>>()
            ])
        }
        "publication-retired-outputs" => {
            let held = read_pointers(root()?);
            let mut gone = held["solids"]
                .as_object()
                .map(|m| m.keys().cloned().collect::<BTreeSet<_>>())
                .unwrap_or_default();
            let declared = names(&v["declared"]);
            gone.retain(|p| !declared.contains(p));
            let cards = sidecars(root()?, &Value::Null);
            if let Some(m) = held["sidecars"].as_object() {
                gone.extend(m.keys().filter(|p| !cards.contains(*p)).cloned());
            }
            json!(gone)
        }
        "publication-retirement-groups" => {
            let made = &v["held"]["made"];
            let mut groups: BTreeMap<String, Vec<String>> = BTreeMap::new();
            for rel in strings(&v["retired"]) {
                groups
                    .entry(made[&rel]["commit"].as_str().unwrap_or("").into())
                    .or_default()
                    .push(rel);
            }
            json!(groups)
        }
        "publication-retirement-evidence" => {
            let root = root()?;
            let mut unexplained = Vec::new();
            for record in v["records"].as_array().context("retirement records")? {
                let graph = record["graph"]
                    .as_str()
                    .and_then(|s| serde_json::from_str::<Value>(s).ok());
                let Some(graph) =
                    graph.filter(|_| truthy(&record["graph_ok"]) && truthy(&record["diff_ok"]))
                else {
                    unexplained.extend(strings(&record["rels"]));
                    continue;
                };
                let changed = names(&record["changed"]);
                for rel in strings(&record["rels"]) {
                    let producers = graph
                        .as_object()
                        .into_iter()
                        .flatten()
                        .filter(|(_, row)| names(&row["writes"]).contains(&rel))
                        .map(|(generator, _)| generator.clone())
                        .collect::<BTreeSet<_>>();
                    let explained = if producers.is_empty() {
                        changed.contains("tools/bazel/inventory.py")
                    } else {
                        !producers.is_disjoint(&changed)
                            || !producers.iter().any(|p| root.join(p).is_file())
                    };
                    if !explained {
                        unexplained.push(rel);
                    }
                }
            }
            unexplained.extend(strings(&v["unrecorded"]));
            unexplained.sort();
            json!(unexplained)
        }
        "publication-prune" => {
            let root = root()?;
            let hardware = resolve_missing(&root.join("hardware"))?;
            let mut removed = Vec::new();
            for rel in strings(&v["retired"]) {
                let path = root.join(&rel);
                let resolved = resolve_missing(&path)?;
                ensure!(
                    resolved.starts_with(&hardware),
                    "refusing to prune a pointer file path outside hardware/: {rel}"
                );
                if path.is_file() || path.is_symlink() {
                    fs::remove_file(path)?;
                    removed.push(rel);
                }
            }
            json!(removed)
        }
        "publication-pointer-assets" => json!(pointer_assets(&v["held"], text("prefix")?)),
        "publication-too-new" => json!(too_new(
            &v["assets"],
            v["now"].as_f64().context("clock")?,
            v["floor"].as_f64().context("retirement floor")?
        )),
        "publication-retirable" => {
            let disk = names(&v["disk"]);
            let mut reachable = disk.clone();
            let mut kept = disk;
            let history = v["history"].as_array().context("history")?;
            let count = v["keep_cuts"].as_i64().unwrap_or(12);
            let count = if count < 0 {
                (history.len() as i64 + count).max(0) as usize
            } else {
                count as usize
            };
            for (i, cut) in history.iter().enumerate() {
                let cut = names(cut);
                reachable.extend(cut.iter().cloned());
                if i < count {
                    kept.extend(cut);
                }
            }
            let on_release = v["assets"]
                .as_array()
                .into_iter()
                .flatten()
                .filter_map(|a| a["name"].as_str().map(str::to_owned))
                .collect::<BTreeSet<_>>();
            let fresh = too_new(
                &v["assets"],
                v["now"].as_f64().context("clock")?,
                v["floor"].as_f64().context("retirement floor")?,
            );
            json!([
                on_release
                    .iter()
                    .filter(|n| !reachable.contains(*n) && !fresh.contains(*n))
                    .cloned()
                    .collect::<Vec<_>>(),
                on_release
                    .iter()
                    .filter(|n| reachable.contains(*n) && !kept.contains(*n) && !fresh.contains(*n))
                    .cloned()
                    .collect::<Vec<_>>()
            ])
        }
        "publication-release-match" => {
            let old = v["assets"]
                .as_array()
                .into_iter()
                .flatten()
                .filter(|a| a["name"] == v["asset"])
                .last();
            json!(old.is_some_and(|a| a["state"] == "uploaded"
                && a["size"] == v["size"]
                && a["digest"] == json!(format!("sha256:{}", text("digest").unwrap_or("")))))
        }
        "publication-objects-on-release" => {
            let prefix = text("prefix")?;
            json!(
                v["assets"]
                    .as_array()
                    .into_iter()
                    .flatten()
                    .filter(|a| a["state"] == "uploaded")
                    .filter_map(|a| a["name"]
                        .as_str()?
                        .strip_prefix(prefix)?
                        .strip_suffix(".gz")
                        .map(str::to_owned))
                    .collect::<BTreeSet<_>>()
            )
        }
        "publication-objects-to-send" => {
            let known = names(&v["known"]);
            let mut seen = BTreeSet::new();
            let mut out = Vec::new();
            for rel in strings(&v["rels"]) {
                let sha = v["hashes"][&rel].as_str().context("member hash")?;
                if !known.contains(sha) && seen.insert(sha.to_owned()) {
                    out.push(rel);
                }
            }
            json!(out)
        }
        "publication-object-count" => json!(
            v["extra"].as_u64().unwrap_or(0)
                + strings(&v["rels"])
                    .iter()
                    .filter(|rel| v["hashes"][*rel]
                        .as_str()
                        .is_none_or(|sha| !names(&v["known"]).contains(sha)))
                    .count() as u64
        ),
        "publication-target-members" => {
            let targets = names(&v["targets"]);
            let mut out = BTreeSet::new();
            for (label, members) in inventory_targets(&v["inventory"]) {
                if targets.contains(&label) {
                    out.extend(members);
                }
            }
            json!(out)
        }
        "publication-member-targets" => {
            let mut remaining = names(&v["members"]);
            let mut targets = BTreeSet::new();
            for (label, members) in inventory_targets(&v["inventory"]) {
                let owned = remaining
                    .intersection(&members)
                    .cloned()
                    .collect::<BTreeSet<_>>();
                if !owned.is_empty() {
                    targets.insert(label);
                    remaining.retain(|p| !owned.contains(p));
                }
            }
            json!([targets, remaining])
        }
        "publication-owed-members" => {
            let mut out = Vec::new();
            if let Some(tree) = v["tree"].as_object() {
                for (rel, digest) in tree {
                    let line = &v["made"][rel];
                    if !line.is_object()
                        || truthy(&line["unproven"])
                        || line.get("inputs") != Some(digest)
                    {
                        out.push(rel.clone());
                    }
                }
            }
            json!(out)
        }
        "publication-derived-members" => {
            let graph: crate::artifacts::Graph = serde_json::from_value(v["graph"].clone())?;
            let unheld = names(&v["unheld"]);
            json!(
                names(&v["members"])
                    .into_iter()
                    .filter(|p| v["tree"].get(p).is_some()
                        && !unheld.contains(p)
                        && graph.inputs(p).is_disjoint(&unheld))
                    .collect::<BTreeSet<_>>()
            )
        }
        "publication-unproven" => {
            let count = v["made"]
                .as_object()
                .into_iter()
                .flatten()
                .filter(|(_, line)| truthy(&line["unproven"]))
                .count();
            json!(if count > 0 {
                format!(
                    " — {count} of {} member(s) unproven",
                    v["made"].as_object().map_or(0, |m| m.len())
                )
            } else {
                String::new()
            })
        }
        "publication-total-bytes" => {
            let root = root()?;
            json!(
                strings(&v["rels"])
                    .iter()
                    .map(|p| root.join(p).metadata().map(|s| s.len()))
                    .collect::<std::io::Result<Vec<_>>>()?
                    .into_iter()
                    .sum::<u64>()
            )
        }
        "publication-existing" => json!(
            strings(&v["paths"])
                .into_iter()
                .filter(|p| root().is_ok_and(|r| r.join(p).is_file()))
                .collect::<Vec<_>>()
        ),
        "publication-bytes-drifted" => json!(bytes_drifted(v)),
        "publication-sidecar-paths" => json!(sidecar_paths(root()?, &v["held"])),
        "publication-heal" => json!(heal(root()?, &v["held"], &v["index"], text("pointers")?)),
        "publication-piece-payloads" => json!(
            strings(&v["moved"])
                .into_iter()
                .filter(|p| p.starts_with(v["prefix"].as_str().unwrap_or(""))
                    && p.ends_with(".step.mesh"))
                .collect::<Vec<_>>()
        ),
        "publication-owed" => {
            let moved = strings(&v["moved"]);
            let inputs = strings(&v["inputs"]);
            let mut reasons = Vec::new();
            if !moved.is_empty() {
                reasons.push(format!(
                    "{} member(s) on this disk are not the bytes the pointer file names",
                    moved.len()
                ));
            }
            if !inputs.is_empty() {
                reasons.push(format!(
                    "the tree moves the `made` line of {} member(s)",
                    inputs.len()
                ));
            }
            if truthy(&v["catalog_moved"]) {
                reasons.push("the numbered catalog changes the website files".into());
            }
            json!([
                reasons.join("; "),
                moved,
                inputs,
                heal(root()?, &v["held"], &v["index"], text("pointers")?)
            ])
        }
        "publication-catalog-moved" => json!(
            root()?.join("hardware/ledger/materials.json").is_file()
                && v["held"]["website"] != website(root()?, &v["held"], &v["config"])?
        ),
        "publication-commit-plan" => {
            let paths = heal(root()?, &v["held"], &v["index"], text("pointers")?);
            let fresh = paths
                .iter()
                .filter(|p| v["index"].get(*p).is_none())
                .cloned()
                .collect::<Vec<_>>();
            let served = strings(&v["served"])
                .iter()
                .any(|k| v["before"][k] != v["held"][k]);
            json!({"paths":paths,"fresh":fresh,"served":served,"message":if served{"cad-artifacts: cut here, and the pointer file moved"}else{"cad-artifacts: record which members' inputs moved"}})
        }
        "publication-refresh-selection" => {
            let keys = names(&v["keys"]);
            json!(
                names(&v["matches"])
                    .intersection(&keys)
                    .cloned()
                    .collect::<Vec<_>>()
            )
        }
        "publication-map-changes" => {
            let old = &v["old"];
            let new = &v["new"];
            let moved = new
                .as_object()
                .into_iter()
                .flatten()
                .filter(|(k, d)| old.get(*k).is_some_and(|x| x != *d))
                .map(|(k, _)| k.clone())
                .collect::<Vec<_>>();
            let fresh = new
                .as_object()
                .into_iter()
                .flatten()
                .filter(|(k, _)| old.get(*k).is_none())
                .map(|(k, _)| k.clone())
                .collect::<Vec<_>>();
            let gone = old
                .as_object()
                .into_iter()
                .flatten()
                .filter(|(k, _)| new.get(*k).is_none())
                .map(|(k, _)| k.clone())
                .collect::<Vec<_>>();
            json!([moved, fresh, gone])
        }
        _ => return Ok(None),
    };
    Ok(Some(result))
}
fn resolve_missing(path: &Path) -> Result<std::path::PathBuf> {
    fn walk(path: &Path, active: &mut BTreeSet<std::path::PathBuf>) -> Result<std::path::PathBuf> {
        let absolute = std::path::absolute(path)?;
        let mut out = std::path::PathBuf::new();
        for component in absolute.components() {
            match component {
                std::path::Component::CurDir => {}
                std::path::Component::ParentDir => {
                    out.pop();
                }
                std::path::Component::Normal(name) => {
                    let candidate = out.join(name);
                    if fs::symlink_metadata(&candidate).is_ok_and(|m| m.file_type().is_symlink()) {
                        ensure!(
                            active.insert(candidate.clone()),
                            "symlink loop: {}",
                            candidate.display()
                        );
                        let link = fs::read_link(&candidate)?;
                        out = walk(&out.join(link), active)?;
                        active.remove(&candidate);
                    } else {
                        out = candidate;
                    }
                }
                component => out.push(component.as_os_str()),
            }
        }
        Ok(out)
    }
    walk(path, &mut BTreeSet::new())
}
