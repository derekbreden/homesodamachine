use anyhow::{Context as _, Result};
use hsm_documents::Variables;
use regex::Regex;
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    path::{Path, PathBuf},
};

/// The programs that write the ledgers' figures, as each document's Sources names them.
pub const BOM_PROGRAM: &str = "/hardware/ledger/bom.rs";
pub const PURCHASES_PROGRAM: &str = "/hardware/ledger/purchases.rs";
pub const MACHINE_TIME_PROGRAM: &str = "/hardware/ledger/machine_time.rs";

/// What a ledger run reads and writes. Inputs are read under `root`; a program given an output
/// directory writes its documents there, at their paths under `root`, and every later read of
/// a document this run wrote sees what it wrote. The build's trace is told each file read.
pub struct Context {
    pub root: PathBuf,
    pub out: Option<PathBuf>,
    pub reads: BTreeSet<String>,
    pub rewritten: BTreeSet<String>,
    written: BTreeMap<PathBuf, Vec<u8>>,
    /// The figures this run has written into each Markdown document, by the document.
    figures: BTreeMap<PathBuf, Variables>,
}

impl Context {
    pub fn new(request: &Value) -> Self {
        Self::at(PathBuf::from(request["root"].as_str().unwrap_or(".")), None)
    }
    /// A run reading under `root` and writing under `out`, or in place when there is none.
    pub fn at(root: PathBuf, out: Option<PathBuf>) -> Self {
        Self {
            root,
            out,
            reads: BTreeSet::new(),
            rewritten: BTreeSet::new(),
            written: BTreeMap::new(),
            figures: BTreeMap::new(),
        }
    }
    pub fn path(&self, request: &Value, key: &str, default: &str) -> PathBuf {
        request[key]
            .as_str()
            .map(PathBuf::from)
            .unwrap_or_else(|| self.root.join(default))
    }
    fn bytes(&mut self, path: &Path) -> Result<Vec<u8>> {
        self.reads.insert(path.to_string_lossy().into_owned());
        if let Some(bytes) = self.written.get(path) {
            return Ok(bytes.clone());
        }
        let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
        hsm_kernel::reads::read(path, &bytes);
        Ok(bytes)
    }
    pub fn read(&mut self, path: impl AsRef<Path>) -> Result<String> {
        let path = path.as_ref();
        let bytes = self.bytes(path)?;
        String::from_utf8(bytes).with_context(|| format!("reading {}", path.display()))
    }
    pub fn json(&mut self, path: impl AsRef<Path>) -> Result<Value> {
        let path = path.as_ref();
        serde_json::from_str(&self.read(path)?)
            .with_context(|| format!("parsing {}", path.display()))
    }
    /// Whether `path` is there to read, this run's own writes included.
    pub fn exists(&self, path: &Path) -> bool {
        self.written.contains_key(path) || path.is_file()
    }
    /// Where a document read at `path` is written: the same path, or its place under `out`.
    fn target(&self, path: &Path) -> PathBuf {
        match &self.out {
            Some(out) => out.join(path.strip_prefix(&self.root).unwrap_or(path)),
            None => path.to_owned(),
        }
    }
    pub fn write(&mut self, path: &Path, bytes: &[u8]) -> Result<()> {
        self.rewritten.insert(path.to_string_lossy().into_owned());
        let target = self.target(path);
        if let Some(parent) = target.parent() {
            std::fs::create_dir_all(parent)?;
        }
        hsm_documents::write_if_changed(&target, bytes)?;
        self.written.insert(path.to_owned(), bytes.to_vec());
        Ok(())
    }
    /// Writes `variables` into the `[value](NAME)` markers of the Markdown at `path`, names
    /// `caller` in its Sources, and records in its figures sidecar every figure this run has
    /// written into it.
    pub fn substitute(&mut self, path: &Path, variables: &Variables, caller: &str) -> Result<()> {
        let text = self.read(path)?.replace("\r\n", "\n").replace('\r', "\n");
        let (text, carried) = hsm_documents::markdown(&text, variables, Some(caller));
        self.write(path, text.as_bytes())?;
        let figures = self.figures.entry(path.to_owned()).or_default();
        figures.extend(carried);
        let figures = figures.clone();
        let sidecar = path.with_extension("figures.json");
        let mut held: BTreeMap<String, Variables> = if self.exists(&sidecar) {
            serde_json::from_str(&self.read(&sidecar)?).unwrap_or_default()
        } else {
            BTreeMap::new()
        };
        held.insert(caller.to_owned(), figures);
        let json = ascii_json(&serde_json::to_string_pretty(&held)?) + "\n";
        self.write(&sidecar, json.as_bytes())
    }
}

/// JSON with every character past ASCII escaped, as the sidecars have always been written.
fn ascii_json(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    for c in text.chars() {
        if (c as u32) < 0x7f {
            out.push(c);
        } else {
            let mut buf = [0_u16; 2];
            for value in c.encode_utf16(&mut buf) {
                out.push_str(&format!("\\u{value:04x}"));
            }
        }
    }
    out
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
