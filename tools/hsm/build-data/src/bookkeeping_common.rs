use anyhow::{Context, Result};
use regex::Regex;
use serde_json::{Value, json};
use std::{collections::BTreeSet, fs, path::Path};
pub const CAD: [&str; 4] = [".step", ".stl", ".glb", ".step.mesh"];
pub fn text<'a>(v: &'a Value, k: &str) -> &'a str {
    v[k].as_str().unwrap_or("")
}
pub fn strings(v: &Value) -> Vec<String> {
    v.as_array()
        .map(|v| {
            v.iter()
                .filter_map(Value::as_str)
                .map(str::to_owned)
                .collect()
        })
        .unwrap_or_default()
}
pub fn set(v: &Value) -> BTreeSet<String> {
    strings(v).into_iter().collect()
}
pub fn suffix(path: &str) -> &str {
    let name = path.rsplit('/').next().unwrap_or(path);
    match name.rfind('.') {
        Some(i) if i > 0 && i + 1 < name.len() => &name[i..],
        _ => "",
    }
}
pub fn truthy(v: &Value) -> bool {
    match v {
        Value::Null => false,
        Value::Bool(v) => *v,
        Value::String(v) => !v.is_empty(),
        Value::Number(v) => v.as_f64() != Some(0.),
        Value::Array(v) => !v.is_empty(),
        Value::Object(v) => !v.is_empty(),
    }
}
pub fn graph(path: &str) -> Option<Value> {
    fs::read(path)
        .ok()
        .and_then(|v| serde_json::from_slice(&v).ok())
}
pub fn names(v: &Value) -> BTreeSet<String> {
    v.as_object()
        .map(|v| v.keys().cloned().collect())
        .unwrap_or_default()
}
pub fn labels(raw: &str) -> Vec<String> {
    Regex::new(r"[\s,]+")
        .unwrap()
        .split(raw.trim())
        .filter(|s| !s.is_empty())
        .map(|s| {
            if s.starts_with("//") {
                s.into()
            } else {
                format!("//:{}", s.trim_start_matches(':'))
            }
        })
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect()
}
pub fn failed(v: &Value) -> Value {
    let mut out = BTreeSet::new();
    for line in strings(&v["lines"]) {
        if let Ok(event) = serde_json::from_str::<Value>(&line) {
            for (kind, state) in [
                ("targetCompleted", "completed"),
                ("actionCompleted", "action"),
            ] {
                if let Some(label) = event["id"][kind]["label"]
                    .as_str()
                    .filter(|s| !s.is_empty())
                {
                    if !truthy(&event[state]["success"]) {
                        out.insert(label.to_owned());
                    }
                }
            }
        }
    }
    json!(out)
}
pub fn target_name(path: &str, shared: &BTreeSet<String>) -> String {
    let path = Path::new(path);
    let own = path
        .file_stem()
        .unwrap_or_default()
        .to_string_lossy()
        .trim_matches('_')
        .replace('_', "-");
    if own == "build" || shared.contains(&own) {
        format!(
            "{}-{own}",
            path.parent()
                .and_then(Path::file_name)
                .unwrap_or_default()
                .to_string_lossy()
        )
    } else {
        own
    }
}
pub fn shared_stems<'a>(paths: impl Iterator<Item = &'a str>) -> BTreeSet<String> {
    let mut seen = BTreeSet::new();
    let mut shared = BTreeSet::new();
    for p in paths {
        let stem = Path::new(p)
            .file_stem()
            .unwrap_or_default()
            .to_string_lossy()
            .trim_matches('_')
            .replace('_', "-");
        if !seen.insert(stem.clone()) {
            shared.insert(stem);
        }
    }
    shared
}
pub fn glob(pattern: &str, path: &str) -> bool {
    fn segment(pattern: &str, value: &str) -> bool {
        let cs = pattern.chars().collect::<Vec<_>>();
        let mut at = 0;
        let mut re = String::from("(?s)^");
        while at < cs.len() {
            match cs[at] {
                '*' => re.push_str(".*"),
                '?' => re.push('.'),
                '[' => {
                    let mut end = at + 1;
                    if end < cs.len() && matches!(cs[end], '!' | '^') {
                        end += 1
                    }
                    if end < cs.len() && cs[end] == ']' {
                        end += 1
                    }
                    while end < cs.len() && cs[end] != ']' {
                        end += 1
                    }
                    if end == cs.len() {
                        re.push_str("\\[")
                    } else {
                        re.push('[');
                        let mut i = at + 1;
                        if cs[i] == '!' {
                            re.push('^');
                            i += 1
                        } else if cs[i] == '^' {
                            re.push_str("\\^");
                            i += 1
                        }
                        while i < end {
                            if cs[i] == '\\' {
                                re.push_str("\\\\")
                            } else {
                                re.push(cs[i]);
                            }
                            i += 1
                        }
                        re.push(']');
                        at = end;
                    }
                }
                c => re.push_str(&regex::escape(&c.to_string())),
            }
            at += 1;
        }
        re.push('$');
        Regex::new(&re).is_ok_and(|r| r.is_match(value))
    }
    let parts = pattern.split('/').collect::<Vec<_>>();
    let bits = path.split('/').collect::<Vec<_>>();
    let mut ends = BTreeSet::from([0]);
    for part in parts {
        if part == "**" {
            ends = (*ends.first().unwrap_or(&0)..=bits.len()).collect()
        } else {
            ends = ends
                .into_iter()
                .filter(|i| *i < bits.len() && segment(part, bits[*i]))
                .map(|i| i + 1)
                .collect()
        }
        if ends.is_empty() {
            return false;
        }
    }
    ends.contains(&bits.len())
}
pub fn read_text(path: &Path) -> Result<String> {
    Ok(fs::read_to_string(path)
        .with_context(|| format!("reading {}", path.display()))?
        .replace("\r\n", "\n")
        .replace('\r', "\n"))
}
