//! Fine-model source selection from producer paths and frozen-reference manifests.
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::path::{Path, PathBuf};

pub fn model(request: &Value) -> Result<Value> {
    let root = Path::new(
        request["input_root"]
            .as_str()
            .context("source input root")?,
    );
    let authored = Path::new(
        request["authored_root"]
            .as_str()
            .context("source authored root")?,
    );
    let relative = request["relative"]
        .as_str()
        .context("source relative path")?;
    let mode = request["mode"].as_str().unwrap_or("equipment");
    let path = root.join(relative);
    let original = authored.join(relative);
    let manifests = if mode == "layout" {
        vec![
            path.parent().unwrap().join("frozen-asset.json"),
            original.parent().unwrap().join("frozen-asset.json"),
        ]
    } else {
        vec![original.parent().unwrap().join("frozen-asset.json")]
    };
    for manifest in manifests {
        if !manifest.is_file() {
            continue;
        }
        let data: Value = serde_json::from_slice(&std::fs::read(&manifest)?)?;
        let filename = path.file_name().unwrap().to_string_lossy();
        let mut selected = data["fine_models"]
            .get(filename.as_ref())
            .cloned()
            .unwrap_or(Value::Null);
        if selected.is_null()
            && mode == "layout"
            && data["members"].get(filename.as_ref()).is_some()
        {
            selected = data["fine_model"].clone();
        }
        if let Some(selected) = selected.get("path").and_then(Value::as_str) {
            let supplied = path.parent().unwrap().join(selected);
            let result = if supplied.is_file() {
                supplied
            } else {
                original.parent().unwrap().join(selected)
            };
            return Ok(json!(result));
        }
    }
    let fine = PathBuf::from(format!("{}.npz", path.display()));
    if fine.is_file() || mode == "equipment" && relative.starts_with("printed-parts/") {
        Ok(json!(fine))
    } else {
        Ok(json!(format!("{}.mesh", path.display())))
    }
}
