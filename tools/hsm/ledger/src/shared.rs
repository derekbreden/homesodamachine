use anyhow::{Context as _, Result};
use hsm_documents::{Kind, Variables};
use regex::Regex;
use serde_json::{Value, json};
use std::{
    collections::BTreeSet,
    path::{Path, PathBuf},
};

pub struct Context {
    pub root: PathBuf,
    pub reads: BTreeSet<String>,
    pub rewritten: BTreeSet<String>,
}

impl Context {
    pub fn new(request: &Value) -> Self {
        Self {
            root: PathBuf::from(request["root"].as_str().unwrap_or(".")),
            reads: BTreeSet::new(),
            rewritten: BTreeSet::new(),
        }
    }
    pub fn path(&self, request: &Value, key: &str, default: &str) -> PathBuf {
        request[key]
            .as_str()
            .map(PathBuf::from)
            .unwrap_or_else(|| self.root.join(default))
    }
    pub fn read(&mut self, path: impl AsRef<Path>) -> Result<String> {
        let path = path.as_ref();
        self.reads.insert(path.to_string_lossy().into_owned());
        std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))
    }
    pub fn json(&mut self, path: impl AsRef<Path>) -> Result<Value> {
        let path = path.as_ref();
        serde_json::from_str(&self.read(path)?)
            .with_context(|| format!("parsing {}", path.display()))
    }
    pub fn write(&mut self, path: &Path, bytes: &[u8]) -> Result<()> {
        self.rewritten.insert(path.to_string_lossy().into_owned());
        hsm_documents::write_if_changed(path, bytes)?;
        Ok(())
    }
    pub fn substitute(&mut self, path: &Path, variables: &Variables, caller: &str) -> Result<()> {
        self.reads.insert(path.to_string_lossy().into_owned());
        let sidecar = path.with_extension("figures.json");
        if sidecar.is_file() {
            self.reads.insert(sidecar.to_string_lossy().into_owned());
        }
        let result =
            hsm_documents::substitute(path, Kind::Markdown, variables, Some(caller), true)?;
        for path in result.maintained {
            self.rewritten.insert(path.to_string_lossy().into_owned());
        }
        Ok(())
    }
}

pub fn re(pattern: &str) -> Regex {
    Regex::new(pattern).expect("authored ledger pattern")
}
pub fn cells(row: &str) -> Vec<String> {
    hsm_documents::cells(row)
}
pub fn num(value: &Value) -> Result<f64> {
    value
        .as_f64()
        .or_else(|| value.as_str().and_then(|s| s.parse().ok()))
        .context("expected a number")
}
pub fn strings(value: &Value) -> Result<Vec<String>> {
    value
        .as_array()
        .context("expected an array")?
        .iter()
        .map(|s| Ok(s.as_str().context("expected text")?.to_owned()))
        .collect()
}
pub fn arg<'a>(request: &'a Value, key: &str) -> Result<&'a str> {
    request[key]
        .as_str()
        .with_context(|| format!("missing {key}"))
}
pub fn fmt(value: f64, spec: &str) -> String {
    hsm_documents::format_number(value, spec).expect("authored ledger format")
}
pub fn money(value: f64) -> String {
    format!("${}", fmt(value, ",.2f"))
}
pub fn round(value: f64, places: i32) -> f64 {
    if places >= 0 {
        // Decimal formatting rounds the binary input itself. Multiplying by
        // 10^places first can move a value onto the wrong side of a tie.
        fmt(value, &format!(".{places}f")).parse().unwrap_or(value)
    } else {
        let factor = 10f64.powi(-places);
        (value / factor).round_ties_even() * factor
    }
}
pub fn separator(cells: &[String]) -> bool {
    cells
        .iter()
        .all(|s| s.chars().all(|c| matches!(c, '-' | ':' | ' ')))
}
pub fn section(line: &str) -> Option<i64> {
    re(r"^## (\d+)\.")
        .captures(line)
        .and_then(|c| c[1].parse().ok())
}
pub fn stale(text: &str, variables: &Variables) -> Vec<String> {
    variables
        .iter()
        .filter_map(|(name, want)| {
            let pattern = format!(r"\[([^\]]*)\]\({}\)", regex::escape(name));
            let caps = re(&pattern).captures(text)?;
            let got = &caps[1];
            (got != want).then(|| format!("  [{got}]({name}) should be [{want}]({name})"))
        })
        .collect()
}
pub fn main_result(status: i32, output: String) -> Value {
    json!({"status":status,"output":output})
}
pub fn text_prefix(text: &str, count: usize) -> String {
    text.chars().take(count).collect()
}
