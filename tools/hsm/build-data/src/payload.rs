//! The viewer's little-endian, four-byte-aligned surface payload.
use anyhow::{Context, Result, ensure};
use serde::{Deserialize, Serialize};
use serde_json::{Value, value::RawValue};
use sha2::{Digest, Sha256};
use std::{fs, io::Read, path::Path};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Mesh {
    pub name: String,
    pub color: Value,
    pub pos: Vec<f64>,
    pub nrm: Vec<f64>,
    pub idx: Vec<u32>,
    pub fac: Vec<u32>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub col: Option<Vec<f64>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub uv: Option<Vec<f64>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub face_sources: Option<Box<RawValue>>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Payload {
    #[serde(rename = "v")]
    pub version: u32,
    pub meshes: Vec<Mesh>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub src: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub cut: Option<Box<RawValue>>,
}

#[derive(Serialize, Deserialize)]
struct Entry {
    name: String,
    color: Value,
    pos: [usize; 2],
    nrm: [usize; 2],
    idx: [usize; 2],
    fac: [usize; 2],
    #[serde(default, skip_serializing_if = "Option::is_none")]
    col: Option<[usize; 2]>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    uv: Option<[usize; 2]>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    face_sources: Option<Box<RawValue>>,
}

#[derive(Serialize, Deserialize)]
struct Header {
    v: u32,
    meshes: Vec<Entry>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    src: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    cut: Option<Box<RawValue>>,
}

pub fn header(path: impl AsRef<Path>) -> Result<Value> {
    let mut file = fs::File::open(path)?;
    let mut prefix = [0; 4];
    file.read_exact(&mut prefix)?;
    let count = u32::from_le_bytes(prefix) as usize;
    let mut data = vec![0; count];
    file.read_exact(&mut data)?;
    Ok(serde_json::from_slice(&data)?)
}

pub fn digest(path: impl AsRef<Path>) -> Result<String> {
    let mut file = fs::File::open(path)?;
    let mut hash = Sha256::new();
    let mut buffer = [0; 1 << 16];
    loop {
        let size = file.read(&mut buffer)?;
        if size == 0 { break; }
        hash.update(&buffer[..size]);
    }
    Ok(format!("{:x}", hash.finalize()))
}

pub fn aligned_sources(value: Option<&Value>, ranges: usize) -> Option<Value> {
    let groups = value?.as_array()?;
    (groups.len() == ranges && groups.iter().all(Value::is_array)).then(|| value.unwrap().clone())
}

fn aligned_raw(value: Option<Box<RawValue>>, ranges: usize) -> Option<Box<RawValue>> {
    let parsed: Value = serde_json::from_str(value.as_ref()?.get()).ok()?;
    aligned_sources(Some(&parsed), ranges)?;
    value
}

pub fn record_sources(record: &Value) -> Value {
    let Some(record) = record.as_object() else { return serde_json::json!([null]); };
    let mut sources: Vec<Value> = if let Some(contributors) = record.get("contributors").and_then(Value::as_array) {
        contributors.iter().map(|row| {
            if row.is_object() && row["op"].is_string() && (row["src"].is_null() || row["src"].is_string()) {
                row.clone()
            } else { Value::Null }
        }).collect()
    } else if record.contains_key("src") && record.get("op").is_some_and(Value::is_string) {
        vec![serde_json::json!({"src":record["src"],"op":record["op"]})]
    } else { return serde_json::json!([null]); };
    let mut via = record.get("via").cloned().unwrap_or(Value::Null);
    if let Some((op, src)) = via.as_str().and_then(|text| text.split_once(" at ")) {
        via = serde_json::json!({"op":op,"src":if src.is_empty() {Value::Null} else {Value::String(src.into())}});
    }
    if via.is_object() {
        for source in &mut sources {
            if let Some(source) = source.as_object_mut() { source.insert("via".into(), via.clone()); }
        }
    }
    Value::Array(sources)
}

pub fn read(path: impl AsRef<Path>) -> Result<Payload> {
    decode(&fs::read(path)?)
}

pub fn decode(data: &[u8]) -> Result<Payload> {
    ensure!(data.len() >= 4, "truncated payload header");
    let size = u32::from_le_bytes(data[..4].try_into()?) as usize;
    let end = 4usize.checked_add(size).context("payload header overflow")?;
    let header: Header = serde_json::from_slice(data.get(4..end).context("truncated payload header")?)?;
    ensure!(matches!(header.v, 2 | 3), "unsupported payload version {}", header.v);
    let blob = &data[end..];
    let bytes = |[offset, count]: [usize; 2]| -> Result<&[u8]> {
        let end = count.checked_mul(4).and_then(|n| offset.checked_add(n)).context("payload array overflow")?;
        blob.get(offset..end).context("payload array beyond the file")
    };
    let floats = |range| -> Result<Vec<f64>> {
        Ok(bytes(range)?.chunks_exact(4).map(|b| f32::from_le_bytes(b.try_into().unwrap()) as f64).collect())
    };
    let ints = |range| -> Result<Vec<u32>> {
        Ok(bytes(range)?.chunks_exact(4).map(|b| u32::from_le_bytes(b.try_into().unwrap())).collect())
    };
    let meshes = header.meshes.into_iter().map(|row| {
        Ok(Mesh { name: row.name, color: row.color,
            pos: floats(row.pos)?, nrm: floats(row.nrm)?, idx: ints(row.idx)?, fac: ints(row.fac)?,
            col: row.col.map(floats).transpose()?, uv: row.uv.map(floats).transpose()?,
            face_sources: aligned_raw(row.face_sources, row.fac[1] / 2) })
    }).collect::<Result<_>>()?;
    Ok(Payload { version: header.v, meshes, src: header.src, cut: header.cut })
}

pub fn encode(payload: &Payload) -> Result<Vec<u8>> {
    let mut blob = Vec::new();
    fn floats(blob: &mut Vec<u8>, array: &[f64]) -> [usize; 2] {
        let range = [blob.len(), array.len()];
        blob.extend(array.iter().flat_map(|&v| (v as f32).to_le_bytes()));
        range
    }
    fn ints(blob: &mut Vec<u8>, array: &[u32]) -> [usize; 2] {
        let range = [blob.len(), array.len()];
        blob.extend(array.iter().flat_map(|v| v.to_le_bytes()));
        range
    }
    let mut entries = Vec::with_capacity(payload.meshes.len());
    for mesh in &payload.meshes {
        let pos = floats(&mut blob, &mesh.pos);
        let nrm = floats(&mut blob, &mesh.nrm);
        let idx = ints(&mut blob, &mesh.idx);
        let fac = ints(&mut blob, &mesh.fac);
        for (key, array, components) in [("col", &mesh.col, 3), ("uv", &mesh.uv, 2)] {
            if let Some(array) = array {
                ensure!(array.len() == mesh.pos.len() / 3 * components, "{}: invalid {key} vertex count", mesh.name);
            }
        }
        entries.push(Entry { name:mesh.name.clone(), color:mesh.color.clone(), pos,nrm,idx,fac,
            col: mesh.col.as_deref().map(|a| floats(&mut blob, a)),
            uv: mesh.uv.as_deref().map(|a| floats(&mut blob, a)),
            face_sources: aligned_raw(mesh.face_sources.clone(), mesh.fac.len() / 2) });
    }
    let header = Header {v:payload.version,meshes:entries,src:payload.src.clone(),cut:payload.cut.clone()};
    let mut head = ascii_json(&serde_json::to_string(&header)?).into_bytes();
    head.resize((head.len() + 3) / 4 * 4, b' ');
    let mut output = (u32::try_from(head.len())?).to_le_bytes().to_vec();
    output.extend(head);
    output.extend(blob);
    Ok(output)
}

pub fn ascii_json(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    for character in text.chars() {
        if character.is_ascii() {out.push(character);} else {
            let mut units = [0; 2];
            for unit in character.encode_utf16(&mut units) {
                use std::fmt::Write;
                write!(out, "\\u{unit:04x}").unwrap();
            }
        }
    }
    out
}

pub fn write(path: impl AsRef<Path>, payload: &Payload) -> Result<()> {
    fs::write(path, encode(payload)?)?;
    Ok(())
}
