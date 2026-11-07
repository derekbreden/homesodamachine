//! Bambu Studio's own system presets, resolved from the installed application: the parent
//! first, then each included template, then the preset's own values. No user profile or saved
//! project is read.

use crate::json::Json;
use crate::profile::PRESETS;
use crate::sha256_hex;
use anyhow::{Context, Result};
use std::path::Path;

/// Keys that name, place or describe a preset rather than set the printer.
const METADATA: [&str; 13] = ["type", "name", "inherits", "include", "from", "setting_id", "instantiation",
    "description", "alias", "filament_id", "version", "rename", "compatible_printers"];

pub struct Resolved {
    /// Every setting, a later writer replacing an earlier one in its place.
    pub values: Json,
    /// The preset file that last wrote each setting, as `{"preset": "<kind>/<file>"}`.
    pub sources: Json,
    /// The preset's `filament_id` and `setting_id`, or its parents'.
    pub ids: Json,
}

fn entries(map: Json) -> Vec<(String, Json)> {
    match map {
        Json::Map(entries) => entries,
        _ => Vec::new(),
    }
}

/// The `kind` preset (`machine`, `process` or `filament`) named `name`. `files` gains each
/// preset file read, with its SHA-256, the named one first.
pub fn system_preset(kind: &str, name: &str, files: &mut Json) -> Result<Resolved> {
    let path = Path::new(PRESETS).join(kind).join(format!("{name}.json"));
    let raw = std::fs::read(&path).with_context(|| format!("reading {}", path.display()))?;
    let data = Json::parse(std::str::from_utf8(&raw)?).with_context(|| format!("parsing {}", path.display()))?;
    let source = format!("{kind}/{name}.json");
    files.set(&source, Json::Text(sha256_hex(&raw)));
    let mut resolved = Resolved { values: Json::Map(Vec::new()), sources: Json::Map(Vec::new()), ids: Json::Map(Vec::new()) };
    if let Some(parent) = data.get("inherits").and_then(Json::text).filter(|p| !p.is_empty()) {
        resolved = system_preset(kind, parent, files)?;
    }
    for include in data.get("include").map(Json::list).unwrap_or(&[]).iter().filter_map(Json::text) {
        let template = system_preset(kind, include, files)?;
        for (key, value) in entries(template.values) {
            resolved.values.set(&key, value);
        }
        for (key, value) in entries(template.sources) {
            resolved.sources.set(&key, value);
        }
    }
    if let Json::Map(own) = &data {
        for (key, value) in own {
            if !METADATA.contains(&key.as_str()) {
                resolved.values.set(key, value.clone());
                resolved.sources.set(key, Json::Map(vec![("preset".into(), Json::Text(source.clone()))]));
            }
        }
    }
    for key in ["filament_id", "setting_id"] {
        if let Some(value) = data.get(key) {
            resolved.ids.set(key, value.clone());
        }
    }
    Ok(resolved)
}
