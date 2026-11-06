//! Physical model, presentation and scene output from explicit file references and frames.
use anyhow::{Result, bail};
use hsm_kernel::part;
use hsm_model_export::{digest, model, output_name, payload, put, read, text};
use serde_json::{Value, json};
use std::path::{Path, PathBuf};

#[path = "model_export/gltf.rs"]
mod gltf;
#[path = "model_export/merge.rs"]
mod merge;

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
