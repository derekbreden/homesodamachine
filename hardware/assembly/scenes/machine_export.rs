//! Physical model, presentation and scene output from explicit file references and frames.
use anyhow::{Context, Result, bail};
use hsm_kernel::part;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};

#[path = "model_export/component_order.rs"]
mod component_order;
#[path = "model_export/gltf.rs"]
mod gltf;
#[path = "model_export/merge.rs"]
mod merge;
#[path = "model_export/model.rs"]
mod model;
#[path = "model_export/payload.rs"]
mod payload;

pub fn text<'a>(value: &'a Value, key: &str) -> Result<&'a str> {
    value
        .get(key)
        .and_then(Value::as_str)
        .with_context(|| format!("missing text {key}"))
}

pub fn read(path: &Path) -> Result<Vec<u8>> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(path, &bytes);
    Ok(bytes)
}

pub fn digest(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

pub fn put(path: &Path, bytes: &[u8]) -> Result<()> {
    if path.is_file()
        && std::fs::metadata(path)?.len() == bytes.len() as u64
        && std::fs::read(path)? == bytes
    {
        return Ok(());
    }
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let temp = path.with_file_name(format!(
        ".{}.{}.tmp",
        path.file_name().unwrap().to_string_lossy(),
        std::process::id()
    ));
    std::fs::write(&temp, bytes)?;
    std::fs::rename(&temp, path)?;
    Ok(())
}

pub fn output_name(path: &Path, output: &Path) -> String {
    path.strip_prefix(output)
        .unwrap_or(path)
        .to_string_lossy()
        .into_owned()
}

fn main() -> Result<()> {
    let (numbers, output) = part::args()?;
    let spec = numbers.get("spec")?;
    std::fs::create_dir_all(&output)?;
    let op = spec.get("op").and_then(Value::as_str).unwrap_or("physical");
    let result = match op {
        "physical" => model::physical(spec, &output)?,
        "scene" => model::scene(spec, &output)?,
        "entries" => model::entries(spec, &output)?,
        "graft" => {
            let target = PathBuf::from(text(spec, "target_payload")?);
            let mut host = payload::Payload::read(&target)?;
            let grafted = host.graft(spec.get("skins").unwrap_or(&json!([])))?;
            host.write(&target)?;
            let mut files = vec![output_name(&target, &output)];
            if let Some(path) = spec.get("model").and_then(Value::as_str) {
                model::bind(Path::new(path), &target)?;
                files.push(output_name(Path::new(path), &output));
            }
            json!({"files":files,"bodies":[],"grafted":grafted})
        }
        "views" => gltf::write_views(spec, &output)?,
        "append" => merge::append(spec, &output)?,
        other => bail!("unknown export operation {other:?}"),
    };
    println!("{}", result);
    Ok(())
}
