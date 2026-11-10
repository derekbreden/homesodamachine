//! Repository tools maintain scratch, read explicit checks and answer timing and prototype calibration questions on request.
pub mod cache;
pub mod checks;
pub mod discovery;
pub mod drawing_review;
pub mod integrity;
pub mod mating;
pub mod model;
pub mod paths;
pub mod timing;

use anyhow::{Context, Result};
use std::{
    path::{Path, PathBuf},
    process::{Command, Output},
    time::{SystemTime, UNIX_EPOCH},
};

pub fn root(explicit: Option<PathBuf>) -> Result<PathBuf> {
    if let Some(root) = explicit {
        return Ok(std::path::absolute(root)?);
    }
    let cwd = std::env::current_dir()?;
    if let Some(root) = cwd
        .ancestors()
        .find(|p| p.join("tools/hsm/Cargo.toml").is_file())
    {
        return Ok(root.to_path_buf());
    }
    Ok(Path::new(env!("CARGO_MANIFEST_DIR"))
        .ancestors()
        .nth(3)
        .context("repository root")?
        .to_path_buf())
}
pub fn now() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}
pub fn text(path: impl AsRef<Path>) -> Result<String> {
    std::fs::read_to_string(path.as_ref())
        .with_context(|| format!("read {}", path.as_ref().display()))
}
pub fn command(root: &Path, program: &str, args: &[&str]) -> Result<Output> {
    Command::new(program)
        .args(args)
        .current_dir(root)
        .output()
        .with_context(|| format!("run {program}"))
}
pub fn git(root: &Path, args: &[&str]) -> Result<String> {
    Ok(String::from_utf8_lossy(&command(root, "git", args)?.stdout)
        .trim_end()
        .to_owned())
}
pub fn program(root: &Path, name: &str) -> Result<PathBuf> {
    let built = root.join("tools/hsm/target/release").join(name);
    if built.is_file() {
        return Ok(built);
    }
    if let Some(home) = std::env::var_os("HOME") {
        let installed = PathBuf::from(home).join(".local/bin").join(name);
        if installed.is_file() {
            return Ok(installed);
        }
    }
    if let Some(path) = std::env::var_os("PATH") {
        for directory in std::env::split_paths(&path) {
            let installed = directory.join(name);
            if installed.is_file() {
                return Ok(installed);
            }
        }
    }
    anyhow::bail!(
        "{name} is not installed; explicitly build its native package through tools/run before this reading"
    )
}
pub fn write_json(path: &Path, value: &impl serde::Serialize) -> Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    if std::fs::read(path).ok().as_deref() != Some(bytes.as_slice()) {
        std::fs::write(path, bytes)?;
    }
    Ok(())
}
pub fn files(root: &Path) -> Vec<PathBuf> {
    let mut out = Vec::new();
    let mut stack = vec![root.to_path_buf()];
    while let Some(dir) = stack.pop() {
        let Ok(entries) = std::fs::read_dir(dir) else {
            continue;
        };
        for entry in entries.flatten() {
            let path = entry.path();
            let Ok(kind) = entry.file_type() else {
                continue;
            };
            if kind.is_dir() {
                stack.push(path)
            } else if kind.is_file() {
                out.push(path)
            }
        }
    }
    out.sort();
    out
}
pub fn html_unescape(text: &str) -> String {
    let mut out = String::new();
    let mut rest = text;
    while let Some(at) = rest.find('&') {
        out.push_str(&rest[..at]);
        rest = &rest[at..];
        let Some(end) = rest.find(';').filter(|n| *n < 16) else {
            out.push('&');
            rest = &rest[1..];
            continue;
        };
        let entity = &rest[1..end];
        let ch = match entity {
            "amp" => Some('&'),
            "lt" => Some('<'),
            "gt" => Some('>'),
            "quot" => Some('"'),
            "apos" | "#39" => Some('\''),
            "nbsp" => Some('\u{a0}'),
            _ => entity
                .strip_prefix("#x")
                .or_else(|| entity.strip_prefix("#X"))
                .and_then(|n| u32::from_str_radix(n, 16).ok())
                .or_else(|| entity.strip_prefix('#').and_then(|n| n.parse().ok()))
                .and_then(char::from_u32),
        };
        if let Some(ch) = ch {
            out.push(ch);
            rest = &rest[end + 1..]
        } else {
            out.push('&');
            rest = &rest[1..]
        }
    }
    out.push_str(rest);
    out
}
pub fn wildcard(pattern: &str, value: &str) -> bool {
    let p: Vec<_> = pattern.chars().collect();
    let v: Vec<_> = value.chars().collect();
    let (mut i, mut j, mut mark) = (0, 0, 0);
    let mut star = None;
    while i < v.len() {
        if j < p.len() && (p[j] == '?' || p[j] == v[i]) {
            i += 1;
            j += 1;
        } else if j < p.len() && p[j] == '*' {
            star = Some(j);
            mark = i;
            j += 1;
        } else if let Some(s) = star {
            mark += 1;
            i = mark;
            j = s + 1;
        } else {
            return false;
        }
    }
    while j < p.len() && p[j] == '*' {
        j += 1;
    }
    j == p.len()
}
