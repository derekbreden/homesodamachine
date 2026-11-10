//! Cargo configuration fingerprints compiler settings and external packages without workspace membership churn.
use anyhow::{Context, Result, bail};
use serde::Deserialize;
use sha2::{Digest, Sha256};
use std::{collections::BTreeMap, fs, io::Write, path::Path, sync::Once};

static READS_BEGUN: Once = Once::new();

fn read(path: &Path) -> Result<String> {
    let bytes = fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    if let Some(log) = std::env::var_os("HSM_READS") {
        READS_BEGUN.call_once(|| { let _ = fs::write(&log, "hsm-reads 1\n"); });
        let absolute = std::env::current_dir()?.join(path);
        if let Ok(mut file) = fs::OpenOptions::new().append(true).open(log) {
            let _ = writeln!(file, "{}\t{:x}", absolute.display(), Sha256::digest(&bytes));
        }
    }
    Ok(String::from_utf8(bytes)?)
}

#[derive(Deserialize)]
struct Lockfile {
    #[serde(default)] version: Option<i64>,
    #[serde(default, rename = "package")] packages: Vec<Package>,
}

#[derive(Deserialize)]
struct Package {
    #[serde(default)] source: Option<String>,
    #[serde(flatten)] fields: BTreeMap<String, toml::Value>,
}

enum Canonical {
    Null, Boolean(bool), Integer(i64), Float(f64), String(String),
    Array(Vec<Canonical>), Table(BTreeMap<String, Canonical>),
}

impl TryFrom<toml::Value> for Canonical {
    type Error = anyhow::Error;
    fn try_from(value: toml::Value) -> Result<Self> {
        Ok(match value {
            toml::Value::String(value) => Self::String(value),
            toml::Value::Integer(value) => Self::Integer(value),
            toml::Value::Float(value) => Self::Float(value),
            toml::Value::Boolean(value) => Self::Boolean(value),
            toml::Value::Array(values) => Self::Array(values.into_iter().map(Self::try_from).collect::<Result<_>>()?),
            toml::Value::Table(values) => Self::Table(values.into_iter().map(|(key, value)| Ok((key, Self::try_from(value)?))).collect::<Result<_>>()?),
            toml::Value::Datetime(_) => bail!("Cargo configuration dates cannot be represented by the retained JSON fingerprint"),
        })
    }
}

fn quoted(value: &str) -> String {
    let mut result = String::new();
    for character in serde_json::to_string(value).unwrap().chars() {
        if character.is_ascii() { result.push(character); }
        else { for unit in character.encode_utf16(&mut [0; 2]) { result.push_str(&format!("\\u{unit:04x}")); } }
    }
    result
}

fn float(value: f64) -> String {
    if value.is_nan() { return "NaN".to_owned(); }
    if value == f64::INFINITY { return "Infinity".to_owned(); }
    if value == f64::NEG_INFINITY { return "-Infinity".to_owned(); }
    let value = format!("{value:?}");
    if let Some((number, exponent)) = value.split_once('e') {
        let exponent: i32 = exponent.parse().unwrap();
        format!("{number}e{}{magnitude:02}", if exponent < 0 { '-' } else { '+' }, magnitude = exponent.unsigned_abs())
    } else { value }
}

fn render(value: &Canonical, depth: usize, output: &mut String) {
    match value {
        Canonical::Null => output.push_str("null"),
        Canonical::Boolean(value) => output.push_str(if *value { "true" } else { "false" }),
        Canonical::Integer(value) => output.push_str(&value.to_string()),
        Canonical::Float(value) => output.push_str(&float(*value)),
        Canonical::String(value) => output.push_str(&quoted(value)),
        Canonical::Array(values) => {
            output.push('[');
            for (index, value) in values.iter().enumerate() {
                output.push('\n'); output.push_str(&" ".repeat(depth + 1)); render(value, depth + 1, output);
                if index + 1 < values.len() { output.push(','); }
            }
            if !values.is_empty() { output.push('\n'); output.push_str(&" ".repeat(depth)); }
            output.push(']');
        }
        Canonical::Table(values) => {
            output.push('{');
            for (index, (key, value)) in values.iter().enumerate() {
                output.push('\n'); output.push_str(&" ".repeat(depth + 1)); output.push_str(&quoted(key)); output.push_str(": "); render(value, depth + 1, output);
                if index + 1 < values.len() { output.push(','); }
            }
            if !values.is_empty() { output.push('\n'); output.push_str(&" ".repeat(depth)); }
            output.push('}');
        }
    }
}

/// Canonical bytes retain semantic compiler configuration and source-bearing lock entries.
pub fn config(manifest: &str, lock: &str) -> Result<String> {
    let mut manifest = toml::from_str::<toml::Table>(manifest).context("parse Cargo workspace manifest")?;
    if let Some(workspace) = manifest.get_mut("workspace").and_then(toml::Value::as_table_mut) { workspace.remove("members"); }
    let lock: Lockfile = toml::from_str(lock).context("parse Cargo lock file")?;
    let external = lock.packages.into_iter().filter_map(|mut package| package.source.map(|source| {
        package.fields.insert("source".to_owned(), toml::Value::String(source));
        Canonical::try_from(toml::Value::Table(package.fields.into_iter().collect()))
    })).collect::<Result<Vec<_>>>()?;
    let value = Canonical::Table(BTreeMap::from([
        ("lock".to_owned(), Canonical::Table(BTreeMap::from([
            ("external".to_owned(), Canonical::Array(external)),
            ("version".to_owned(), lock.version.map_or(Canonical::Null, Canonical::Integer)),
        ]))),
        ("manifest".to_owned(), Canonical::try_from(toml::Value::Table(manifest))?),
    ]));
    let mut output = String::new(); render(&value, 0, &mut output); output.push('\n'); Ok(output)
}

/// Unchanged canonical bytes retain the existing output and its timestamp.
pub fn write(root: &Path, output: &Path) -> Result<bool> {
    let hsm = root.join("tools/hsm");
    let bytes = config(&read(&hsm.join("Cargo.toml"))?, &read(&hsm.join("Cargo.lock"))?)?;
    if fs::read(output).is_ok_and(|existing| existing == bytes.as_bytes()) { return Ok(false); }
    fs::create_dir_all(output.parent().context("configuration output parent")?)?;
    fs::write(output, bytes)?;
    Ok(true)
}

#[cfg(test)]
mod tests {
    use super::*;
    const MANIFEST: &str = "[workspace]\nmembers = ['first', 'second']\nresolver = '2'\n[workspace.package]\nedition = '2024'\n[profile.release]\ndebug = 1\n";
    const LOCK: &str = "version = 4\n[[package]]\nname = 'first'\nversion = '0.1.0'\n[[package]]\nname = 'library'\nversion = '1.2.3'\nsource = 'registry+https://example.test'\nchecksum = 'hash'\ndependencies = ['other']\n";

    #[test]
    fn adding_workspace_members_and_local_packages_keeps_config_identical() {
        let baseline = config(MANIFEST, LOCK).unwrap();
        let manifest = MANIFEST.replace("'first', 'second'", "'first', 'second', 'new-program'");
        let lock = format!("{LOCK}\n[[package]]\nname = 'new-program'\nversion = '0.1.0'\n");
        assert_eq!(config(&manifest, &lock).unwrap(), baseline);
        assert_ne!(config(&MANIFEST.replace("debug = 1", "debug = 0"), LOCK).unwrap(), baseline);
        assert_ne!(config(MANIFEST, &LOCK.replace("version = '1.2.3'", "version = '1.2.4'")).unwrap(), baseline);
    }

    #[test]
    fn canonical_json_sorts_keys_escapes_unicode_and_retains_external_package_order() {
        let text = config(&format!("{MANIFEST}\n[workspace.metadata]\nauthor = 'Dérék 🍋'\nsmall = 0.000001\nlarge = 10000000000000000.0\n"), LOCK).unwrap();
        assert!(text.starts_with("{\n \"lock\": {\n  \"external\": [\n"));
        assert!(text.contains("\"author\": \"D\\u00e9r\\u00e9k \\ud83c\\udf4b\""));
        assert!(text.contains("\"small\": 1e-06"));
        assert!(text.contains("\"large\": 1e+16"));
        let value: serde_json::Value = serde_json::from_str(&text).unwrap();
        assert_eq!(value["lock"]["external"][0]["name"], "library");
        assert!(value["manifest"]["workspace"].get("members").is_none());
        assert_eq!(value["manifest"]["profile"]["release"]["debug"], 1);
    }
}
