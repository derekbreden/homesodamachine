//! What the installed machine is made from, read one way for every request it builds: the
//! design files written down for it, the files the parts' own steps publish, the materials
//! catalog's colours, and the file each placed model is read from.
use anyhow::{Context, Result, ensure};
use serde_json::{Map, Value};
use std::path::{Path, PathBuf};

/// A JSON file of the tree, read whole.
pub fn read(path: impl AsRef<Path>) -> Result<Value> {
    let path = path.as_ref();
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(path, &bytes);
    serde_json::from_slice(&bytes).with_context(|| format!("parsing {}", path.display()))
}

/// A value as Python's records were written down, with their named tuples, ordered maps and
/// lists as plain JSON objects and arrays.
pub fn plain(value: &Value) -> Value {
    match value {
        Value::Array(rows) => Value::Array(rows.iter().map(plain).collect()),
        Value::Object(map) => {
            if let (Some(fields), Some(values)) = (map.get("fields"), map.get("values"))
                && map.contains_key("__hsm_namedtuple__")
            {
                let fields = fields.as_array().into_iter().flatten().filter_map(Value::as_str);
                let values = values.as_array().into_iter().flatten();
                return Value::Object(fields.zip(values).map(|(k, v)| (k.to_owned(), plain(v))).collect());
            }
            if let Some(Value::Array(pairs)) = map.get("__hsm_dict__") {
                let mut out = Map::new();
                for pair in pairs {
                    let key = match &pair[0] {
                        Value::String(text) => text.clone(),
                        other => other.to_string(),
                    };
                    out.insert(key, plain(&pair[1]));
                }
                return Value::Object(out);
            }
            if let Some(rows) = map.get("__hsm_list__") {
                return plain(rows);
            }
            Value::Object(map.iter().map(|(k, v)| (k.clone(), plain(v))).collect())
        }
        other => other.clone(),
    }
}

/// Records that the program read `path`, when the run is asked to name what it reads, so the
/// build declares the file as one of the step's inputs.
pub fn record(path: &Path) {
    if std::env::var_os("HSM_READS").is_none() {
        return;
    }
    use sha2::{Digest, Sha256};
    if let Ok(bytes) = std::fs::read(path) {
        hsm_kernel::reads::digest(path, &format!("{:x}", Sha256::digest(&bytes)));
    }
}

/// The document a model file carries beside its bodies (its colours' alphas, its presentation),
/// or an empty object when it carries none.
pub fn read_document(model: &Path) -> Result<Value> {
    record(model);
    use std::io::Read;
    let file = std::fs::File::open(model).with_context(|| format!("opening {}", model.display()))?;
    let mut archive = zip::ZipArchive::new(file)?;
    let Ok(mut member) = archive.by_name("document.npy") else { return Ok(Value::Object(Map::new())) };
    let mut raw = Vec::new();
    member.read_to_end(&mut raw)?;
    ensure!(raw.starts_with(b"\x93NUMPY") && raw.len() > 10, "{} holds no document array", model.display());
    let (start, size) = if raw[6] == 1 {
        (10, u16::from_le_bytes([raw[8], raw[9]]) as usize)
    } else {
        (12, u32::from_le_bytes([raw[8], raw[9], raw[10], raw[11]]) as usize)
    };
    ensure!(start + size <= raw.len(), "{} has a truncated document", model.display());
    Ok(serde_json::from_slice(&raw[start + size..])?)
}

/// The names a model file's bodies carry, in its order.
pub fn read_names(model: &Path) -> Result<Vec<String>> {
    record(model);
    use std::io::Read;
    let file = std::fs::File::open(model).with_context(|| format!("opening {}", model.display()))?;
    let mut archive = zip::ZipArchive::new(file)?;
    let mut member = archive.by_name("names.npy").with_context(|| format!("{} names no bodies", model.display()))?;
    let mut raw = Vec::new();
    member.read_to_end(&mut raw)?;
    ensure!(raw.starts_with(b"\x93NUMPY") && raw.len() > 10, "{} holds no names array", model.display());
    let (start, size) = if raw[6] == 1 {
        (10, u16::from_le_bytes([raw[8], raw[9]]) as usize)
    } else {
        (12, u32::from_le_bytes([raw[8], raw[9], raw[10], raw[11]]) as usize)
    };
    Ok(serde_json::from_slice(&raw[start + size..])?)
}

/// The written-down interior the enclosure is cut around: `enclosure-box.json`'s Box, plain.
pub fn enclosure_box(root: &Path) -> Result<Value> {
    let document = read(root.join("hardware/manifold-layout/enclosure-box.json"))?;
    Ok(plain(&document["box"]))
}

fn curve(c: f64) -> f64 {
    if c <= 0.04045 { c / 12.92 } else { ((c + 0.055) / 1.055).powf(2.4) }
}

fn curve32(c: f32) -> f32 {
    if c <= 0.04045_f32 { c / 12.92_f32 } else { ((c + 0.055_f32) / 1.055_f32).powf(2.4_f32) }
}

/// A colour of the materials catalog by name, such as `M_PETG_BLACK`, as the viewer's files carry
/// it: linear RGB at single precision.
pub fn material(name: &str) -> Result<[f64; 3]> {
    let catalog: Value = serde_json::from_str(include_str!("../../../tools/hsm/shared-data/catalog/materials.json"))?;
    let color = catalog["colors"].get(name).with_context(|| format!("no colour {name} in the materials catalog"))?;
    if let Some(bytes) = color["bytes"].as_array() {
        let channels: Vec<f64> = bytes.iter().filter_map(Value::as_f64).collect();
        ensure!(channels.len() == 3, "{name} does not hold three channels");
        return Ok([0, 1, 2].map(|i| curve(channels[i] / 255.) as f32 as f64));
    }
    let args = color["args"].as_array().context("a colour's channels")?;
    if let Some(hex) = args.first().and_then(Value::as_str) {
        ensure!(hex.len() == 7 && hex.starts_with('#'), "{name} is not a #RRGGBB colour");
        let byte = |at: usize| u8::from_str_radix(&hex[at..at + 2], 16);
        return Ok([byte(1)?, byte(3)?, byte(5)?].map(|b| curve32(b as f32 / 255_f32) as f64));
    }
    let srgb = args.len() < 5 || args[4].as_bool().unwrap_or_else(|| args[4].as_f64().is_some_and(|n| n != 0.));
    let channels: Vec<f64> = args.iter().take(3).filter_map(Value::as_f64).collect();
    ensure!(channels.len() == 3, "{name} does not hold three channels");
    Ok([0, 1, 2].map(|i| if srgb { curve(channels[i]) } else { channels[i] } as f32 as f64))
}

/// Which file a placed model is read from: a placement takes a frozen reference's own fine model
/// or its member's, equipment takes the fine model a manifest names for that file.
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Use {
    Layout,
    Equipment,
}

/// The file `relative` (under `hardware/`) is read from: the fine model its reference's
/// `frozen-asset.json` names, else the part's own `.npz` beside it, else its viewer payload.
pub fn source(root: &Path, relative: &str, usage: Use) -> Result<PathBuf> {
    let path = root.join("hardware").join(relative);
    let manifest = path.parent().context("a model's directory")?.join("frozen-asset.json");
    if manifest.is_file() {
        let data = read(&manifest)?;
        let filename = path.file_name().context("a model's file name")?.to_string_lossy().into_owned();
        let mut selected = data["fine_models"].get(&filename).cloned().unwrap_or(Value::Null);
        if selected.is_null() && usage == Use::Layout && data["members"].get(&filename).is_some() {
            selected = data["fine_model"].clone();
        }
        if let Some(name) = selected.get("path").and_then(Value::as_str) {
            return Ok(path.parent().unwrap().join(name));
        }
    }
    let fine = PathBuf::from(format!("{}.npz", path.display()));
    if fine.is_file() || usage == Use::Equipment && relative.starts_with("printed-parts/") {
        Ok(fine)
    } else {
        Ok(PathBuf::from(format!("{}.mesh", path.display())))
    }
}
