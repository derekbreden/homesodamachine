//! The localized PET-GF cooling policy, from the shared crate's one copy of it: the values set in a
//! project's filament slots, the hook Bambu Studio runs after slicing, and the foundation stage
//! that rewrites a sliced plate's G-code.

use crate::json::Json;
use anyhow::{Context, Result};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::Path;

#[allow(dead_code)]
#[path = "../../shared-data/src/cooling.rs"]
mod policy;

const PROJECT: &str = crate::profile::SETTINGS_MEMBER;

/// Apply the cooling values to the project's settings and its filament presets; the project's
/// settings also take the hook. Returns each changed member's changes.
pub fn apply_members(members: &mut BTreeMap<String, Vec<u8>>, hook: &str) -> Result<Value> {
    let names: Vec<String> = members.keys().cloned().collect();
    let chosen = policy::dispatch("member_names", &json!({"names": names}))?;
    let mut changes = serde_json::Map::new();
    for name in chosen.as_array().cloned().unwrap_or_default() {
        let name = name.as_str().context("member name")?.to_string();
        let mut settings = Json::parse(std::str::from_utf8(&members[&name])?)?;
        let command = if name == PROJECT { json!(hook) } else { Value::Null };
        let reply = policy::dispatch("apply", &json!({"settings": settings.to_value(), "post_process_command": command}))?;
        let mut changed = serde_json::Map::new();
        for update in reply["updates"].as_array().cloned().unwrap_or_default() {
            let key = update[0].as_str().context("update key")?.to_string();
            settings.set(&key, Json::from_value(&update[1]["to"]));
            changed.insert(key, update[1].clone());
        }
        if !changed.is_empty() {
            members.insert(name.clone(), (settings.dumps() + "\n").into_bytes());
            changes.insert(name, Value::Object(changed));
        }
    }
    Ok(Value::Object(changes))
}

/// The foundation stage on one G-code file: writes `output` when it changes anything.
pub fn foundation(input: &Path, output: &Path, settings: &Value) -> Result<Value> {
    let policy_values = policy::dispatch("foundation_policy", &json!({}))?;
    policy::dispatch("foundation", &json!({
        "input": input.display().to_string(),
        "output": output.display().to_string(),
        "settings": settings,
        "policy": policy_values,
    }))
}
