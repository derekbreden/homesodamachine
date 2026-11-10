//! Member-wise pointer merges keep matching provenance and explain concurrent replacements.
use anyhow::{Context, Result, ensure};
use hsm_build_data::publication::parse_ordered;
use serde_json::{Value, json};
use std::{collections::BTreeSet, fs};

const KEYS: [&str; 8] = [
    "_", "release", "store", "bundle", "solids", "sidecars", "moved", "made",
];

fn pairs(v: &Value) -> Vec<(String, Value)> {
    if let Some(rows) = v.get("_publication_pairs").and_then(Value::as_array) {
        rows.iter()
            .filter_map(|r| Some((r[0].as_str()?.into(), r[1].clone())))
            .collect()
    } else {
        v.as_object()
            .map(|m| {
                m.iter()
                    .map(|(k, v)| (k.clone(), crate::ordered(v)))
                    .collect()
            })
            .unwrap_or_default()
    }
}
fn object(rows: Vec<(String, Value)>) -> Value {
    json!({"_publication_pairs":rows})
}
fn empty() -> Value {
    object(vec![])
}
fn at<'a>(v: &'a Value, key: &str) -> &'a Value {
    if let Some(rows) = v.get("_publication_pairs").and_then(Value::as_array) {
        rows.iter()
            .find(|row| row[0].as_str() == Some(key))
            .map(|row| &row[1])
            .unwrap_or(&Value::Null)
    } else {
        v.get(key).unwrap_or(&Value::Null)
    }
}
fn get(v: &Value, key: &str) -> Value {
    at(v, key).clone()
}
fn has(v: &Value, key: &str) -> bool {
    if let Some(rows) = v.get("_publication_pairs").and_then(Value::as_array) {
        rows.iter().any(|row| row[0].as_str() == Some(key))
    } else {
        v.get(key).is_some()
    }
}
fn keys(v: &Value) -> Vec<String> {
    if let Some(rows) = v.get("_publication_pairs").and_then(Value::as_array) {
        rows.iter()
            .filter_map(|row| row[0].as_str().map(str::to_owned))
            .collect()
    } else {
        v.as_object()
            .map(|m| m.keys().cloned().collect())
            .unwrap_or_default()
    }
}
fn put(v: &mut Value, key: &str, value: Value) {
    if v.get("_publication_pairs")
        .and_then(Value::as_array)
        .is_none()
    {
        *v = object(pairs(v));
    }
    let rows = v["_publication_pairs"].as_array_mut().unwrap();
    if let Some(row) = rows.iter_mut().find(|row| row[0].as_str() == Some(key)) {
        row[1] = value;
    } else {
        rows.push(json!([key, value]));
    }
}
fn remove(v: &mut Value, key: &str) {
    if let Some(rows) = v
        .get_mut("_publication_pairs")
        .and_then(Value::as_array_mut)
    {
        rows.retain(|row| row[0].as_str() != Some(key));
    } else if let Some(map) = v.as_object_mut() {
        map.remove(key);
    }
}
fn eq(a: &Value, b: &Value) -> bool {
    crate::plain(a.clone()) == crate::plain(b.clone())
}
fn truth(v: &Value) -> bool {
    match crate::plain(v.clone()) {
        Value::Null => false,
        Value::Bool(v) => v,
        Value::Number(v) => v.as_f64() != Some(0.),
        Value::String(v) => !v.is_empty(),
        Value::Array(v) => !v.is_empty(),
        Value::Object(v) => !v.is_empty(),
    }
}
fn first(values: &[Value]) -> Value {
    values
        .iter()
        .find(|v| truth(v))
        .cloned()
        .unwrap_or_else(|| values.last().cloned().unwrap_or(Value::Null))
}
fn members(base: &Value, ours: &Value, theirs: &Value) -> (Value, BTreeSet<String>, Vec<String>) {
    let mut out = empty();
    let mut both = BTreeSet::new();
    let mut notes = vec![];
    for key in keys(base)
        .into_iter()
        .chain(keys(ours))
        .chain(keys(theirs))
        .collect::<BTreeSet<_>>()
    {
        let (vb, vo, vt) = (get(base, &key), get(ours, &key), get(theirs, &key));
        let value = if eq(&vo, &vt) || eq(&vt, &vb) {
            vo
        } else if eq(&vo, &vb) {
            vt
        } else {
            both.insert(key.clone());
            if vt.is_null() {
                notes.push(format!(
                    "{key}: retired on the incoming side and moved on main; main's stands"
                ));
                vo
            } else if vo.is_null() {
                notes.push(format!("{key}: retired on main and moved on the incoming side; the incoming hash stands"));
                vt
            } else {
                notes.push(format!("{key}: moved on both sides; the incoming hash stands and its `made` line is unproven"));
                vt
            }
        };
        if !value.is_null() {
            put(&mut out, &key, value);
        }
    }
    (out, both, notes)
}
fn proves(line: &Value) -> bool {
    crate::plain(line.clone()).is_object()
        && truth(&get(line, "inputs"))
        && !truth(&get(line, "unproven"))
}
fn made(ours: &Value, theirs: &Value, lines: &Value, both: &BTreeSet<String>) -> Value {
    let mut out = empty();
    for relative in keys(lines).into_iter().collect::<BTreeSet<_>>() {
        let digest = get(lines, &relative);
        let mut found = vec![];
        for side in [theirs, ours] {
            let records = at(side, "made");
            let sidecars = at(side, "sidecars");
            let actual = if has(sidecars, &relative) {
                at(sidecars, &relative)
            } else {
                at(at(side, "solids"), &relative)
            };
            if has(records, &relative) && eq(actual, &digest) {
                found.push(get(records, &relative));
            }
        }
        if let Some(line) = found.iter().find(|v| proves(v)).or_else(|| found.first()) {
            let mut line = line.clone();
            if both.contains(&relative) {
                put(&mut line, "unproven", json!(true));
            }
            put(&mut out, &relative, line);
        }
    }
    out
}
fn seat(out: Value, ours: &Value, theirs: &Value) -> Value {
    let mut order = KEYS
        .iter()
        .filter(|k| !get(&out, k).is_null())
        .map(|s| s.to_string())
        .collect::<Vec<_>>();
    let ours_keys = keys(ours);
    let mut out = out;
    for (i, key) in ours_keys.iter().enumerate() {
        if KEYS.contains(&key.as_str())
            || !has(theirs, key)
            || !eq(&get(theirs, key), &get(ours, key))
        {
            continue;
        }
        let at = order
            .iter()
            .enumerate()
            .filter(|(_, k)| ours_keys[..i].contains(k))
            .map(|(j, _)| j + 1)
            .max()
            .unwrap_or(0);
        order.insert(at, key.clone());
        put(&mut out, key, get(ours, key));
    }
    object(order.iter().map(|k| (k.clone(), get(&out, k))).collect())
}
fn merge_ordered(base: &Value, ours: &Value, theirs: &Value) -> (Value, Vec<String>) {
    if !truth(ours) {
        return (theirs.clone(), vec![]);
    }
    if !truth(theirs) {
        return (ours.clone(), vec![]);
    }
    let (solids, both_s, mut notes) = members(
        &get(base, "solids"),
        &get(ours, "solids"),
        &get(theirs, "solids"),
    );
    let (sidecars, both_c, n) = members(
        &get(base, "sidecars"),
        &get(ours, "sidecars"),
        &get(theirs, "sidecars"),
    );
    notes.extend(n);
    let digest = get(&get(base, "bundle"), "sha256");
    let ours_new = !eq(&get(&get(ours, "bundle"), "sha256"), &digest);
    let theirs_new = !eq(&get(&get(theirs, "bundle"), "sha256"), &digest);
    let mut side = if theirs_new && !ours_new {
        theirs
    } else {
        ours
    };
    if !truth(&get(side, "bundle")) {
        side = if truth(&get(theirs, "bundle")) {
            theirs
        } else {
            ours
        };
    }
    let mut release = empty();
    for key in ["tag", "asset", "url"] {
        if has(&get(side, "release"), key) {
            put(&mut release, key, get(&get(side, "release"), key));
        }
    }
    let objects_o = get(&get(ours, "release"), "objects");
    let objects_t = get(&get(theirs, "release"), "objects");
    if truth(&objects_o) && truth(&objects_t) {
        put(&mut release, "objects", objects_o);
    }
    let mut bundle = get(side, "bundle");
    if !truth(&bundle) {
        bundle = empty();
    }
    let behind =
        truth(&get(&bundle, "behind")) || !eq(&solids, &first(&[get(side, "solids"), empty()]));
    remove(&mut bundle, "behind");
    if behind && truth(&bundle) {
        put(&mut bundle, "behind", json!(true));
    }
    let mut moved = empty();
    for relative in keys(&solids) {
        let hash = get(&solids, &relative);
        let mut times = vec![];
        for side in [ours, theirs] {
            if eq(at(at(side, "solids"), &relative), &hash) && has(at(side, "moved"), &relative) {
                times.push(get(at(side, "moved"), &relative));
            }
        }
        if let Some(stamp) = times.into_iter().max_by(|a, b| {
            a.as_f64()
                .unwrap_or(0.)
                .total_cmp(&b.as_f64().unwrap_or(0.))
        }) {
            put(&mut moved, &relative, stamp);
        }
    }
    let mut all = solids.clone();
    for (key, value) in pairs(&sidecars) {
        put(&mut all, &key, value);
    }
    let lines = made(
        ours,
        theirs,
        &all,
        &both_s.union(&both_c).cloned().collect(),
    );
    let mut out = empty();
    let note = first(&[get(ours, "_"), get(theirs, "_"), get(base, "_")]);
    if !note.is_null() {
        put(&mut out, "_", note);
    }
    put(&mut out, "release", release);
    let store = first(&[get(ours, "store"), get(theirs, "store")]);
    if truth(&store) {
        put(&mut out, "store", store);
    }
    put(&mut out, "bundle", bundle);
    put(&mut out, "solids", solids);
    put(&mut out, "sidecars", sidecars);
    if truth(&moved) {
        put(&mut out, "moved", moved);
    }
    if truth(&lines) {
        put(&mut out, "made", lines);
    }
    (seat(out, ours, theirs), notes)
}
fn render(v: &Value, depth: usize) -> Result<String> {
    let is_object = v.get("_publication_pairs").is_some();
    if is_object || v.is_array() {
        let rows = if is_object {
            pairs(v)
                .into_iter()
                .map(|(k, v)| {
                    Ok(format!(
                        "{}: {}",
                        ascii(&serde_json::to_string(&k)?),
                        render(&v, depth + 1)?
                    ))
                })
                .collect::<Result<Vec<_>>>()?
        } else {
            v.as_array()
                .unwrap()
                .iter()
                .map(|v| render(v, depth + 1))
                .collect::<Result<Vec<_>>>()?
        };
        let (open, close) = if is_object { ('{', '}') } else { ('[', ']') };
        return Ok(if rows.is_empty() {
            format!("{open}{close}")
        } else {
            let indent = "  ".repeat(depth + 1);
            format!(
                "{open}\n{indent}{}\n{}{close}",
                rows.join(&format!(",\n{indent}")),
                "  ".repeat(depth)
            )
        });
    }
    Ok(ascii(&serde_json::to_string(v)?))
}
fn ascii(text: &str) -> String {
    hsm_build_data::payload::ascii_json(text).replace('\x7f', "\\u007f")
}
/// Plain JSON callers use the same member and provenance decisions as the Git driver.
pub fn merge_values(base: &Value, ours: &Value, theirs: &Value) -> (Value, Vec<String>) {
    let (out, notes) = merge_ordered(
        &crate::ordered(base),
        &crate::ordered(ours),
        &crate::ordered(theirs),
    );
    (crate::plain(out), notes)
}
pub fn merge_texts(base: &str, ours: &str, theirs: &str) -> Result<(String, Vec<String>)> {
    let parse = |s: &str| {
        if s.trim().is_empty() {
            Ok(empty())
        } else {
            let value = parse_ordered(s.as_bytes())?;
            ensure!(
                value.get("_publication_pairs").is_some(),
                "pointer file is not an object"
            );
            Ok(value)
        }
    };
    let (out, notes) = merge_ordered(&parse(base)?, &parse(ours)?, &parse(theirs)?);
    Ok((render(&out, 0)? + "\n", notes))
}
pub fn run(_ctx: &crate::ContextData, args: &[String]) -> Result<i32> {
    if args == ["--help"] || args == ["-h"] {
        println!("hsm-merge-pointers BASE OURS THEIRS");
        return Ok(0);
    }
    if args.len() != 3 {
        eprintln!("usage: hsm-merge-pointers BASE OURS THEIRS");
        return Ok(2);
    }
    let result = (|| -> Result<_> {
        let base = fs::read_to_string(&args[0])?;
        let ours = fs::read_to_string(&args[1])?;
        let theirs = fs::read_to_string(&args[2])?;
        let (text, notes) = merge_texts(&base, &ours, &theirs)?;
        fs::write(&args[1], text).context("writing merged pointers")?;
        Ok(notes)
    })();
    match result {
        Ok(notes) => {
            for note in notes {
                eprintln!("merge_pointers: {note}");
            }
            Ok(0)
        }
        Err(error) => {
            eprintln!("merge_pointers: {error:#}");
            Ok(1)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn pointer(solids: Value) -> Value {
        json!({"_":"note","release":{"tag":"cad-artifacts","asset":"cad-d0.tar.gz","url":"https://example/d0","objects":"s-"},"bundle":{"sha256":"d0","bytes":1,"solids":solids.as_object().unwrap().len()},"solids":solids,"sidecars":{}})
    }
    #[test]
    fn disjoint_members_and_conflicting_retirement() {
        let base = pointer(json!({"m":"h0","n":"h0"}));
        let ours = pointer(json!({"m":"ha","n":"h0","a":"x"}));
        let mut theirs = pointer(json!({"n":"h0","b":"y"}));
        theirs["made"] = json!({"b":{"inputs":"tb","commit":"cb"}});
        let (got, notes) = merge_values(&base, &ours, &theirs);
        assert_eq!(got["solids"], json!({"a":"x","b":"y","m":"ha","n":"h0"}));
        assert_eq!(got["bundle"]["behind"], true);
        assert_eq!(notes.len(), 1);
        assert!(notes[0].contains("retired on the incoming side"));
        assert_eq!(got["made"]["b"]["inputs"], "tb");
        let (retired, _) = merge_values(&base, &pointer(json!({"n":"h0"})), &base);
        assert!(retired["solids"].get("m").is_none());
    }
    #[test]
    fn provenance_follows_winning_hash_and_matching_proof() {
        let base = pointer(json!({"m":"h0","n":"h0"}));
        let mut ours = pointer(json!({"m":"ha","n":"h0"}));
        let mut theirs = pointer(json!({"m":"hb","n":"h0"}));
        ours["made"] =
            json!({"m":{"inputs":"ta","commit":"ca"},"n":{"commit":"ca","unproven":true}});
        theirs["made"] =
            json!({"m":{"inputs":"tb","commit":"cb"},"n":{"inputs":"tn","commit":"cn"}});
        ours["moved"] = json!({"m":20,"n":5});
        theirs["moved"] = json!({"m":1,"n":7});
        let (got, notes) = merge_values(&base, &ours, &theirs);
        assert_eq!(
            got["made"]["m"],
            json!({"inputs":"tb","commit":"cb","unproven":true})
        );
        assert_eq!(got["made"]["n"]["inputs"], "tn");
        assert_eq!(got["moved"], json!({"m":1,"n":7}));
        assert_eq!(notes.len(), 1);
    }
    #[test]
    fn bundle_selection_and_object_promise() {
        let base = pointer(json!({"m":"h0"}));
        let mut ours = base.clone();
        ours["release"].as_object_mut().unwrap().remove("objects");
        let mut theirs = pointer(json!({"m":"h0","b":"hb"}));
        theirs["bundle"]["sha256"] = json!("db");
        theirs["release"]["asset"] = json!("cad-db.tar.gz");
        let (got, _) = merge_values(&base, &ours, &theirs);
        assert_eq!(got["release"]["asset"], "cad-db.tar.gz");
        assert!(got["release"].get("objects").is_none());
        assert!(got["bundle"].get("behind").is_none());
    }
    #[test]
    fn ordered_unknown_fields_and_empty_creation() {
        let original = "{\n  \"_\": \"note\",\n  \"release\": {\n    \"asset\": \"cad-d0.tar.gz\"\n  },\n  \"source\": {\n    \"commit\": \"c0\"\n  },\n  \"bundle\": {\n    \"sha256\": \"d0\"\n  },\n  \"solids\": {\n    \"m\": \"h0\"\n  },\n  \"sidecars\": {}\n}\n";
        assert_eq!(
            merge_texts(original, original, original).unwrap(),
            (original.into(), vec![])
        );
        assert_eq!(merge_texts("", "", original).unwrap().0, original);
        assert!(merge_texts("{}", "<<<<<<< not json", "{}").is_err());
        let removed = original.replace("  \"source\": {\n    \"commit\": \"c0\"\n  },\n", "");
        assert!(
            !merge_texts(original, original, &removed)
                .unwrap()
                .0
                .contains("source")
        );
    }
}
