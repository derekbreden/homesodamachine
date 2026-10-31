//! The cold core's printed parts on the kernel.
//!
//! A part's Python module derives every number its geometry needs — from the cold core's
//! interface, the fits, the parts it mates with — and writes them to one JSON file. The part's
//! program reads that file and nothing else, so each number has one home and the Python
//! readers of it keep reading the same module.
use anyhow::{Context, Result, anyhow};
use serde_json::Value;
use std::path::Path;

/// One part's numbers, as its Python module wrote them.
pub struct Numbers {
    v: Value,
    path: String,
}

impl Numbers {
    pub fn read(path: impl AsRef<Path>) -> Result<Numbers> {
        let path = path.as_ref();
        let text = std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?;
        let v = serde_json::from_str(&text).with_context(|| format!("parsing {}", path.display()))?;
        Ok(Numbers { v, path: path.display().to_string() })
    }

    pub fn get(&self, key: &str) -> Result<&Value> {
        self.v.get(key).ok_or_else(|| anyhow!("{} has no `{key}`", self.path))
    }

    pub fn f(&self, key: &str) -> Result<f64> {
        self.get(key)?.as_f64().ok_or_else(|| anyhow!("{}: `{key}` is not a number", self.path))
    }

    pub fn list(&self, key: &str) -> Result<Vec<f64>> {
        let a = self.get(key)?.as_array().ok_or_else(|| anyhow!("{}: `{key}` is not a list", self.path))?;
        a.iter()
            .map(|x| x.as_f64().ok_or_else(|| anyhow!("{}: `{key}` holds a non-number", self.path)))
            .collect()
    }

    pub fn pair(&self, key: &str) -> Result<(f64, f64)> {
        match self.list(key)?[..] {
            [a, b] => Ok((a, b)),
            _ => Err(anyhow!("{}: `{key}` is not a pair", self.path)),
        }
    }

    /// A body's colour, linear RGB.
    pub fn color(&self, key: &str) -> Result<[f64; 3]> {
        match self.list(key)?[..] {
            [r, g, b] => Ok([r, g, b]),
            _ => Err(anyhow!("{}: `{key}` is not a colour", self.path)),
        }
    }

    pub fn text(&self, key: &str) -> Result<&str> {
        self.get(key)?.as_str().ok_or_else(|| anyhow!("{}: `{key}` is not text", self.path))
    }
}

/// `numbers.json` and the directory a part's files go to, from the command line.
pub fn args() -> Result<(Numbers, std::path::PathBuf)> {
    let a: Vec<String> = std::env::args().collect();
    anyhow::ensure!(a.len() == 3, "usage: {} <numbers.json> <out dir>", a[0]);
    Ok((Numbers::read(&a[1])?, a[2].clone().into()))
}
