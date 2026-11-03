use super::model::{Frame, Model};
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use std::path::{Path, PathBuf};

const KEYS: [&str; 6] = ["pos", "nrm", "idx", "fac", "col", "uv"];

#[derive(Clone)]
pub struct Entry {
    pub meta: Value,
    pub arrays: std::collections::BTreeMap<String, Vec<u8>>,
}

impl Entry {
    pub fn name(&self) -> &str {
        self.meta["name"].as_str().unwrap()
    }
    pub fn body(&self) -> &str {
        body(self.name())
    }
    pub fn floats(&self, key: &str) -> Vec<f32> {
        self.arrays[key]
            .chunks_exact(4)
            .map(|s| f32::from_le_bytes(s.try_into().unwrap()))
            .collect()
    }
    pub fn ints(&self, key: &str) -> Vec<u32> {
        self.arrays[key]
            .chunks_exact(4)
            .map(|s| u32::from_le_bytes(s.try_into().unwrap()))
            .collect()
    }
    pub fn carried(mut self, frame: &Frame) -> Self {
        if frame.identity() {
            return self;
        }
        for key in ["pos", "nrm"] {
            let old = self.floats(key);
            let values = old
                .chunks_exact(3)
                .flat_map(|v| {
                    let p = [v[0] as f64, v[1] as f64, v[2] as f64];
                    let p = if key == "pos" {
                        frame.point(p)
                    } else if frame.rigid() {
                        frame.direction(p)
                    } else {
                        frame.normal(p)
                    };
                    p.into_iter().flat_map(|x| (x as f32).to_le_bytes())
                })
                .collect();
            self.arrays.insert(key.into(), values);
        }
        if frame.det() < 0.0 {
            let mut indices = self.ints("idx");
            for tri in indices.chunks_exact_mut(3) {
                tri.swap(1, 2);
            }
            self.arrays.insert(
                "idx".into(),
                indices.into_iter().flat_map(u32::to_le_bytes).collect(),
            );
        }
        self
    }
}

pub fn body(name: &str) -> &str {
    match name.rsplit_once('/') {
        Some((base, index)) if !index.is_empty() && index.bytes().all(|c| c.is_ascii_digit()) => {
            base
        }
        _ => name,
    }
}

pub struct Payload {
    pub header: Value,
    pub meshes: Vec<Entry>,
}

impl Payload {
    pub fn read(path: &Path) -> Result<Self> {
        Self::decode(&super::read(path)?)
    }
    pub fn decode(raw: &[u8]) -> Result<Self> {
        ensure!(raw.len() >= 4, "truncated payload");
        let count = u32::from_le_bytes(raw[..4].try_into()?) as usize;
        ensure!(
            count % 4 == 0 && count + 4 <= raw.len(),
            "bad payload header"
        );
        let mut header: Value = serde_json::from_slice(&raw[4..4 + count])?;
        ensure!(
            matches!(header["v"].as_u64(), Some(2 | 3)),
            "unsupported payload version"
        );
        let rows = header["meshes"].as_array_mut().context("payload meshes")?;
        let blob = &raw[4 + count..];
        let mut meshes = Vec::with_capacity(rows.len());
        for row in rows.iter() {
            ensure!(row["name"].is_string(), "payload mesh name");
            let mut arrays = std::collections::BTreeMap::new();
            for key in KEYS {
                if row.get(key).is_none() {
                    continue;
                }
                let a = row[key].as_array().context("payload span")?;
                ensure!(a.len() == 2, "payload span needs offset and count");
                let at = a[0].as_u64().context("payload offset")? as usize;
                let len = a[1].as_u64().context("payload count")? as usize;
                ensure!(at % 4 == 0, "unaligned payload span");
                let end = at
                    .checked_add(len.checked_mul(4).context("payload span overflow")?)
                    .context("payload span overflow")?;
                arrays.insert(
                    key.into(),
                    blob.get(at..end)
                        .context("truncated payload span")?
                        .to_vec(),
                );
            }
            for key in ["pos", "nrm", "idx", "fac"] {
                ensure!(arrays.contains_key(key), "missing {key}");
            }
            let entry = Entry {
                meta: row.clone(),
                arrays,
            };
            let pos = entry.floats("pos");
            let normals = entry.floats("nrm");
            let indices = entry.ints("idx");
            ensure!(
                !pos.is_empty() && pos.len() % 3 == 0 && normals.len() == pos.len(),
                "bad vectors"
            );
            ensure!(
                pos.iter().chain(&normals).all(|x| x.is_finite()),
                "non-finite payload vector"
            );
            ensure!(
                !indices.is_empty()
                    && indices.len() % 3 == 0
                    && indices.iter().all(|&i| (i as usize) < pos.len() / 3),
                "bad indices"
            );
            meshes.push(entry);
        }
        header["meshes"] = json!([]);
        Ok(Self { header, meshes })
    }

    pub fn encode(&self) -> Result<Vec<u8>> {
        let mut blob = Vec::new();
        let mut entries = Vec::new();
        for mesh in &self.meshes {
            let mut row = mesh.meta.clone();
            for key in KEYS {
                if let Some(bytes) = mesh.arrays.get(key) {
                    row[key] = json!([blob.len(), bytes.len() / 4]);
                    blob.extend_from_slice(bytes);
                }
            }
            entries.push(row);
        }
        let mut header = self.header.clone();
        header["v"] = json!(3);
        header["meshes"] = json!(entries);
        let mut head = serde_json::to_vec(&header)?;
        while head.len() % 4 != 0 {
            head.push(b' ');
        }
        let mut bytes = Vec::with_capacity(4 + head.len() + blob.len());
        bytes.extend_from_slice(&(head.len() as u32).to_le_bytes());
        bytes.extend(head);
        bytes.extend(blob);
        Ok(bytes)
    }

    pub fn write(&self, path: &Path) -> Result<()> {
        super::put(path, &self.encode()?)
    }

    pub fn graft(&mut self, skins: &Value) -> Result<usize> {
        let mut grafted = 0;
        for skin in skins.as_array().context("skins is an ordered array")? {
            let source_model = skin
                .get("model")
                .and_then(Value::as_str)
                .map(|path| Model::open(Path::new(path)))
                .transpose()?;
            let path = if let Some(model) = &source_model {
                let file = Path::new(super::text(skin, "model")?);
                model.document["presentation"]["path"]
                    .as_str()
                    .map(|relative| file.parent().unwrap().join(relative))
                    .unwrap_or_else(|| {
                        PathBuf::from(
                            file.to_string_lossy().trim_end_matches(".npz").to_owned() + ".mesh",
                        )
                    })
            } else {
                PathBuf::from(super::text(skin, "payload")?)
            };
            let bytes = super::read(&path)?;
            if let Some(expected) = source_model
                .as_ref()
                .and_then(|model| model.document["presentation"]["sha256"].as_str())
            {
                ensure!(
                    super::digest(&bytes) == expected,
                    "source presentation changed: {}",
                    path.display()
                );
            }
            let shown = Self::decode(&bytes)?;
            if let Some(expected) = skin.get("source_sha256").and_then(Value::as_str) {
                ensure!(
                    shown.header["src"].as_str() == Some(expected),
                    "stale skin {}",
                    path.display()
                );
            } else {
                let source =
                    PathBuf::from(path.to_string_lossy().strip_suffix(".mesh").unwrap_or(""));
                if source.is_file() {
                    let expected = super::digest(&super::read(&source)?);
                    ensure!(
                        shown.header["src"].as_str() == Some(expected.as_str()),
                        "stale skin {}",
                        path.display()
                    );
                }
            }
            let indices = if let Some(model) = &source_model {
                model.selected(skin)?
            } else {
                (0..shown.meshes.len())
                    .filter(|i| {
                        skin.get("indices")
                            .and_then(Value::as_array)
                            .is_none_or(|rows| rows.iter().any(|v| v.as_u64() == Some(*i as u64)))
                    })
                    .collect()
            };
            let targets = skin.get("targets").and_then(Value::as_array);
            if let Some(targets) = targets {
                ensure!(
                    targets.len() == indices.len(),
                    "one target per selected skin leaf"
                );
            }
            let frame = Frame::read(skin.get("transform"))?;
            let names = skin.get("names").and_then(Value::as_object);
            let prefix = skin.get("prefix").and_then(Value::as_str).unwrap_or("");
            for (ordinal, index) in indices.into_iter().enumerate() {
                let surface = shown.meshes.get(index).context("skin entry index")?.clone();
                let target = targets
                    .and_then(|rows| rows[ordinal].as_str())
                    .map(str::to_owned)
                    .or_else(|| {
                        names
                            .and_then(|m| m.get(surface.name()).or_else(|| m.get(surface.body())))
                            .and_then(Value::as_str)
                            .map(str::to_owned)
                    })
                    .unwrap_or_else(|| format!("{prefix}{}", surface.body()));
                let surface = surface.carried(&frame);
                for host in &mut self.meshes {
                    if host.name() != target && host.body() != target {
                        continue;
                    }
                    for key in KEYS {
                        if let Some(value) = surface.arrays.get(key) {
                            host.arrays.insert(key.into(), value.clone());
                        }
                    }
                    if let Some(value) = surface.meta.get("face_sources") {
                        host.meta["face_sources"] = value.clone();
                    } else {
                        host.meta.as_object_mut().unwrap().remove("face_sources");
                    }
                    grafted += 1;
                }
            }
        }
        Ok(grafted)
    }
}

pub fn placed_surfaces(instances: &Value, fine: &[hsm_kernel::Imported]) -> Result<Payload> {
    let mut selected = Vec::new();
    let mut models = std::collections::BTreeMap::new();
    let mut presentations = std::collections::BTreeMap::new();
    for instance in instances.as_array().context("instances")? {
        let path = PathBuf::from(super::text(instance, "model")?);
        if !models.contains_key(&path) {
            models.insert(path.clone(), Model::open(&path)?);
        }
        let source = &models[&path];
        if !presentations.contains_key(&path) {
            let binding = source.document.get("presentation");
            let payload_path = binding
                .and_then(|v| v["path"].as_str())
                .map(|rel| path.parent().unwrap().join(rel))
                .unwrap_or_else(|| {
                    PathBuf::from(
                        path.to_string_lossy().trim_end_matches(".npz").to_owned() + ".mesh",
                    )
                });
            let surfaces = if payload_path.is_file() {
                let bytes = super::read(&payload_path)?;
                if let Some(expected) = binding.and_then(|v| v["sha256"].as_str()) {
                    ensure!(
                        super::digest(&bytes) == expected,
                        "bound presentation changed"
                    );
                }
                Some(Payload::decode(&bytes)?.meshes)
            } else {
                None
            };
            if let Some(rows) = &surfaces {
                ensure!(
                    rows.len() == source.names.len(),
                    "presentation entry count differs from model"
                );
            }
            presentations.insert(path.clone(), surfaces);
        }
        let surfaces = &presentations[&path];
        let frame = Frame::read(instance.get("transform"))?;
        for index in source.selected(instance)? {
            if instance["split_components"].as_bool().unwrap_or(false) {
                selected.extend((0..super::model::component_count(&path, index)?).map(|_| None));
            } else {
                selected.push(
                    surfaces
                        .as_ref()
                        .map(|rows| rows[index].clone().carried(&frame)),
                );
            }
        }
    }
    ensure!(
        selected.len() == fine.len(),
        "presentation and fine entry counts differ"
    );
    let mut totals = std::collections::BTreeMap::new();
    for part in fine {
        *totals.entry(part.name.as_str()).or_insert(0usize) += 1;
    }
    let mut ordinals = std::collections::BTreeMap::new();
    let mut meshes = Vec::new();
    for (part, surface) in fine.iter().zip(selected) {
        let index = ordinals.entry(part.name.as_str()).or_insert(0usize);
        *index += 1;
        let name = if totals[part.name.as_str()] == 1 {
            part.name.clone()
        } else {
            format!("{}/{}", part.name, index)
        };
        let mut surface = match surface {
            Some(surface) => surface,
            None => {
                let body = hsm_kernel::write::Body {
                    name: &name,
                    color: part.color,
                    solid: &part.solid,
                };
                SelfPayload::one(&body)?
            }
        };
        surface.meta["name"] = json!(name);
        surface.meta["color"] = json!(part.color);
        meshes.push(surface);
    }
    Ok(Payload {
        header: json!({"v":3,"meshes":[]}),
        meshes,
    })
}

struct SelfPayload;
impl SelfPayload {
    fn one(body: &hsm_kernel::write::Body<'_>) -> Result<Entry> {
        Ok(
            Payload::decode(&hsm_kernel::write::payload_bytes_with_sources(
                &[*body],
                None,
                None,
            ))?
            .meshes
            .remove(0),
        )
    }
}
