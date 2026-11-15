//! Bambu Studio's own system presets, resolved from the installed application: the parent
//! first, then each included template, then the preset's own values. No user profile or saved
//! project is read.

use crate::profile::PRESETS;
use crate::sha256_hex;
use anyhow::{Context, Result};
use serde_json::{json, Map, Value};
use std::path::Path;

/// Keys that name, place or describe a preset rather than set the printer.
const METADATA: [&str; 13] = ["type", "name", "inherits", "include", "from", "setting_id", "instantiation",
    "description", "alias", "filament_id", "version", "rename", "compatible_printers"];

pub struct Resolved {
    /// Every setting, a later writer replacing an earlier one.
    pub values: Map<String, Value>,
    /// The preset file that last wrote each setting, as `{"preset": "<kind>/<file>"}`.
    pub sources: Map<String, Value>,
    /// The preset's `filament_id` and `setting_id`, or its parents'.
    pub ids: Map<String, Value>,
}

/// The `kind` preset (`machine`, `process` or `filament`) named `name`. `files` gains each
/// preset file read, with its SHA-256.
pub fn system_preset(kind: &str, name: &str, files: &mut Map<String, Value>) -> Result<Resolved> {
    let path = Path::new(PRESETS).join(kind).join(format!("{name}.json"));
    let raw = std::fs::read(&path).with_context(|| format!("reading {}", path.display()))?;
    let data: Value = serde_json::from_slice(&raw).with_context(|| format!("parsing {}", path.display()))?;
    let source = format!("{kind}/{name}.json");
    files.insert(source.clone(), json!(sha256_hex(&raw)));
    let mut resolved = Resolved { values: Map::new(), sources: Map::new(), ids: Map::new() };
    if let Some(parent) = data["inherits"].as_str().filter(|p| !p.is_empty()) {
        resolved = system_preset(kind, parent, files)?;
    }
    for include in data["include"].as_array().into_iter().flatten().filter_map(Value::as_str) {
        let template = system_preset(kind, include, files)?;
        resolved.values.extend(template.values);
        resolved.sources.extend(template.sources);
    }
    for (key, value) in data.as_object().into_iter().flatten() {
        if !METADATA.contains(&key.as_str()) {
            resolved.values.insert(key.clone(), value.clone());
            resolved.sources.insert(key.clone(), json!({"preset": source}));
        }
    }
    for key in ["filament_id", "setting_id"] {
        if let Some(value) = data.get(key) {
            resolved.ids.insert(key.into(), value.clone());
        }
    }
    Ok(resolved)
}
