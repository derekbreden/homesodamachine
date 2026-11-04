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
pub fn member(archive: &mut ZipArchive<File>, name: &str) -> Result<Value> {
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
        "names" | "records" => member(&mut archive, request["kind"].as_str().unwrap()),
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

/// Extract one entry's raw typed arrays. Python only hydrates their native array type.
pub fn entry(request: &Value) -> Result<Value> {
    use std::path::Path;
    let path=request["path"].as_str().context("array source path")?;
    let index=request["index"].as_u64().context("array source index")?;
    let target=Path::new(request["output"].as_str().context("array extraction directory")?);
    std::fs::create_dir_all(target)?;
    let mut archive=ZipArchive::new(File::open(path)?)?;
    let records=member(&mut archive,"records")?;
    let records=records.as_array().context("face record entries")?.get(index as usize).context("face entry out of range")?;
    let mut arrays=serde_json::Map::new();
    for kind in ["V","T","F"] {
        let mut raw=Vec::new();archive.by_name(&format!("{kind}{index}.npy"))?.read_to_end(&mut raw)?;
        let data=npy_data(&raw)?;
        let start=if raw[6]==1{10}else{12};let header_len=raw.len()-data.len()-start;
        let header=std::str::from_utf8(&raw[start..start+header_len])?;
        let order=if header.contains("'fortran_order': True"){"F"}else{"C"};
        let tail=header.split("'descr'").nth(1).context("array descriptor")?.split_once(':').context("array descriptor colon")?.1.trim_start();
        let quote=tail.chars().next().context("array descriptor quote")?;
        let dtype=tail[1..].split(quote).next().context("array descriptor value")?;
        let shape=header.split("'shape'").nth(1).context("array shape")?.split_once('(').context("array shape tuple")?.1.split(')').next().unwrap();
        let shape=shape.split(',').map(str::trim).filter(|part|!part.is_empty()).map(str::parse::<u64>).collect::<std::result::Result<Vec<_>,_>>()?;
        let file=target.join(format!("{kind}{index}.bin"));std::fs::write(&file,data)?;
        arrays.insert(kind.to_owned(),json!({"file":file,"dtype":dtype,"shape":shape,"order":order}));
    }
    Ok(json!({"arrays":arrays,"records":records}))
}
