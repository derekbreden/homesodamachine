//! Small fine-model metadata reads. Geometry members are never opened.
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use std::{fs::File, io::Read};
use zip::ZipArchive;

fn npy_data(raw: &[u8]) -> Result<&[u8]> {
    ensure!(
        raw.starts_with(b"\x93NUMPY") && raw.len() > 10,
        "invalid metadata npy"
    );
    let start = if raw[6] == 1 { 10 } else { 12 };
    ensure!(raw.len() >= start, "truncated metadata npy");
    let size = if start == 10 {
        u16::from_le_bytes(raw[8..10].try_into()?) as usize
    } else {
        u32::from_le_bytes(raw[8..12].try_into()?) as usize
    };
    ensure!(start + size <= raw.len(), "truncated metadata npy header");
    Ok(&raw[start + size..])
}
fn member(archive: &mut ZipArchive<File>, name: &str) -> Result<Value> {
    let mut bytes = Vec::new();
    archive
        .by_name(&format!("{name}.npy"))?
        .read_to_end(&mut bytes)?;
    serde_json::from_slice(npy_data(&bytes)?).with_context(|| format!("fine-model {name}"))
}
pub fn metadata(request: &Value) -> Result<Value> {
    let path = request["path"].as_str().context("metadata path")?;
    let mut archive = ZipArchive::new(File::open(path).with_context(|| format!("model {path}"))?)?;
    match request["kind"].as_str().context("metadata kind")? {
        "document" => {
            if archive
                .file_names()
                .any(|name| name.is_ok_and(|name| name == "document.npy"))
            {
                member(&mut archive, "document")
            } else {
                Ok(json!({}))
            }
        }
        "identity" => {
            let names = member(&mut archive, "names")?;
            let colors = member(&mut archive, "colors")?;
            let names = names.as_array().context("fine-model names")?;
            let colors = colors.as_array().context("fine-model colors")?;
            ensure!(
                names.len() == colors.len(),
                "fine-model names and colors have different lengths"
            );
            Ok(json!(names.iter().zip(colors).collect::<Vec<_>>()))
        }
        other => anyhow::bail!("unknown fine metadata {other:?}"),
    }
}
