use super::model::{Frame, Model, Models};
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use std::path::{Path, PathBuf};

/// The scene payload format whose bodies reference retained native part meshes.
pub const SCENE_PAYLOAD_VERSION: u32 = 4;

fn publication_source(path:&Path)->Option<String> {
    let text=path.to_string_lossy();
    if text.starts_with("hardware/"){Some(text.into_owned())}
    else{text.find("/hardware/").map(|at|text[at+1..].to_owned())}
}

const KEYS: [&str; 6] = ["pos", "nrm", "idx", "fac", "col", "uv"];

#[derive(Clone)]
pub struct Entry {
    pub meta: Value,
    pub arrays: std::collections::BTreeMap<String, Vec<u8>>,
}

impl Entry {
    /// A source binding retains its body identity before an installed instance is renamed.
    fn bind_source(&mut self, source: &str, sha: &str) {
        *self = self.clone().carried(&Frame::read(None).unwrap());
        if self.meta["_scene"]["source"].is_null() {
            self.meta["_scene"]["source_name"] = self.meta["_scene"]["name"].clone();
            self.meta["_scene"]["source"] = json!(source);
            self.meta["_scene"]["source_sha256"] = json!(sha);
        }
    }

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
        if self.meta.get("_scene").is_none() {
            let one=Payload {header:json!({"v":hsm_kernel::write::MESH_PAYLOAD_VERSION}),meshes:vec![self.clone()]};
            if let Ok(bytes)=one.encode() {
                if let Ok(head)=hsm_geometry::scene::pack(&bytes) {self.meta["_scene"]=head["meshes"][0].clone();}
            }
        }
        if frame.identity() {
            return self;
        }
        if self.meta.get("_scene").is_some() {
            let old=Frame::read(self.meta["_scene"].get("transform")).unwrap();
            let placed: [[f64;4];3]=std::array::from_fn(|r|std::array::from_fn(|c| {
                (0..3).map(|k|frame.0[r][k]*old.0[k][c]).sum::<f64>()+if c==3{frame.0[r][3]}else{0.}
            }));
            self.meta["_scene"]["transform"]=json!(placed);
        }
        let rigid = frame.rigid();
        for key in ["pos", "nrm"] {
            for xyz in self.arrays.get_mut(key).unwrap().chunks_exact_mut(12) {
                let p = std::array::from_fn(|c| {
                    f32::from_le_bytes(xyz[c * 4..c * 4 + 4].try_into().unwrap()) as f64
                });
                let p = if key == "pos" {
                    frame.point(p)
                } else if rigid {
                    frame.direction(p)
                } else {
                    frame.normal(p)
                };
                for c in 0..3 {
                    xyz[c * 4..c * 4 + 4].copy_from_slice(&(p[c] as f32).to_le_bytes());
                }
            }
        }
        if frame.det() < 0.0 {
            for tri in self.arrays.get_mut("idx").unwrap().chunks_exact_mut(12) {
                for c in 0..4 {
                    tri.swap(4 + c, 8 + c);
                }
            }
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
        if hsm_geometry::scene::is_scene(raw) {return Self::decode(&hsm_geometry::scene::flatten(raw)?);}
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
            let pos = &entry.arrays["pos"];
            let normals = &entry.arrays["nrm"];
            let indices = &entry.arrays["idx"];
            ensure!(
                !pos.is_empty() && pos.len() % 12 == 0 && normals.len() == pos.len(),
                "bad vectors"
            );
            ensure!(
                pos.chunks_exact(4).chain(normals.chunks_exact(4))
                    .all(|x| f32::from_le_bytes(x.try_into().unwrap()).is_finite()),
                "non-finite payload vector"
            );
            ensure!(
                !indices.is_empty()
                    && indices.len() % 12 == 0
                    && indices.chunks_exact(4).all(|i| {
                        (u32::from_le_bytes(i.try_into().unwrap()) as usize) < pos.len() / 12
                    }),
                "bad indices"
            );
            meshes.push(entry);
        }
        header["meshes"] = json!([]);
        Ok(Self { header, meshes })
    }

    fn framing(&self) -> Result<(Vec<u8>, usize)> {
        let mut size = 0;
        let mut entries = Vec::new();
        for mesh in &self.meshes {
            let mut row = mesh.meta.clone();
            for key in KEYS {
                if let Some(bytes) = mesh.arrays.get(key) {
                    row[key] = json!([size, bytes.len() / 4]);
                    size += bytes.len();
                }
            }
            entries.push(row);
        }
        let mut header = self.header.clone();
        header["v"] = json!(hsm_kernel::write::MESH_PAYLOAD_VERSION);
        header["meshes"] = json!(entries);
        let mut head = serde_json::to_vec(&header)?;
        while head.len() % 4 != 0 {
            head.push(b' ');
        }
        Ok((head, size))
    }

    pub fn encode(&self) -> Result<Vec<u8>> {
        let (head, size) = self.framing()?;
        let mut bytes = Vec::with_capacity(4 + head.len() + size);
        bytes.extend_from_slice(&(head.len() as u32).to_le_bytes());
        bytes.extend(head);
        for mesh in &self.meshes {
            for key in KEYS {
                if let Some(array) = mesh.arrays.get(key) {
                    bytes.extend_from_slice(array);
                }
            }
        }
        Ok(bytes)
    }

    pub fn write(&self, path: &Path) -> Result<()> {
        let mut groups: Vec<(String,Vec<Entry>)>=Vec::new();
        for entry in &self.meshes {
            let name=entry.body();let index=groups.iter().position(|(n,_)|n==name).unwrap_or_else(||{groups.push((name.into(),Vec::new()));groups.len()-1});
            groups[index].1.push(entry.clone());
        }
        let mut nodes=Vec::new();let mut sources=serde_json::Map::new();
        for (_,entries) in groups {
            let part=Payload{header:json!({"v":hsm_kernel::write::MESH_PAYLOAD_VERSION}),meshes:entries};
            let head=hsm_geometry::scene::pack(&part.encode()?)?;
            for node in head["meshes"].as_array().unwrap() {
                if let (Some(source),Some(hash))=(node["source"].as_str(),node["source_sha256"].as_str()) {sources.insert(source.into(),json!(hash));}
                nodes.push(node.clone());
            }
        }
        let mut head=self.header.clone();head["v"]=json!(SCENE_PAYLOAD_VERSION);head["meshes"]=json!(nodes);head["sources"]=json!(sources);
        hsm_geometry::scene::persist(path,&head)
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
            let mut shown = Self::decode(&bytes)?;
            if let Some(source)=publication_source(&path) {
                let sha=super::digest(&bytes);
                for entry in &mut shown.meshes {
                    entry.bind_source(&source, &sha);
                }
            }
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
                    host.meta["_scene"] = surface.meta["_scene"].clone();
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

/// The payload of `fine`, entry by entry: a stored entry's own presentation, carried to its
/// frame, where its model has one; otherwise a drawing of the entry's solid.
pub fn placed_surfaces(
    placed: &[Option<(PathBuf, usize, Frame)>], fine: &mut Model, models: &mut Models,
) -> Result<Payload> {
    let mut selected = Vec::new();
    let mut presentations = std::collections::BTreeMap::new();
    let mut remaining = std::collections::BTreeMap::new();
    for (path, _, _) in placed.iter().flatten() {
        *remaining.entry(path.clone()).or_insert(0usize) += 1;
    }
    for entry in placed {
        let Some((path, index, frame)) = entry else {
            selected.push(None);
            continue;
        };
        if !models.contains_key(path) {
            models.insert(path.clone(), Model::open(path)?);
        }
        let source = &models[path];
        if !presentations.contains_key(path) {
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
                let mut shown=Payload::decode(&bytes)?.meshes;
                if let Some(relative)=publication_source(&payload_path) {
                    let sha=super::digest(&bytes);
                    for entry in &mut shown {
                        entry.bind_source(&relative, &sha);
                    }
                }
                Some(shown)
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
        selected.push(presentations[path].as_ref().map(|rows| rows[*index].clone().carried(frame)));
        let count = remaining.get_mut(path).unwrap();
        *count -= 1;
        if *count == 0 {
            models.remove(path);
            presentations.remove(path);
        }
    }
    ensure!(
        selected.len() == fine.names.len(),
        "presentation and fine entry counts differ"
    );
    let mut totals = std::collections::BTreeMap::new();
    for name in &fine.names {
        *totals.entry(name.clone()).or_insert(0usize) += 1;
    }
    let mut ordinals = std::collections::BTreeMap::new();
    let mut meshes = Vec::new();
    for (ordinal, surface) in selected.into_iter().enumerate() {
        let source_name = &fine.names[ordinal];
        let color: Option<[f64; 3]> = serde_json::from_value(fine.colors[ordinal].clone())?;
        let index = ordinals.entry(source_name.clone()).or_insert(0usize);
        *index += 1;
        let name = if totals[source_name] == 1 {
            source_name.clone()
        } else {
            format!("{source_name}/{}", index)
        };
        let mut surface = match surface {
            Some(surface) => surface,
            None => {
                let part = fine.imported(ordinal)?;
                let body = hsm_kernel::write::Body {
                    name: &name,
                    color,
                    solid: &part.solid,
                };
                SelfPayload::one(&body)?
            }
        };
        surface.meta["name"] = json!(name);
        surface.meta["color"] = json!(color);
        meshes.push(surface);
    }
    Ok(Payload {
        header: json!({"v":hsm_kernel::write::MESH_PAYLOAD_VERSION,"meshes":[]}),
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

#[cfg(test)]
mod tests {
    use super::*;
    use hsm_kernel::{plane::Plane, write::Body};

    #[test]
    fn installed_aliases_refresh_their_source_bodies_in_their_authored_frames() -> Result<()> {
        let root = std::env::temp_dir().join(format!("hsm-alias-refresh-{}", std::process::id()));
        let source = root.join("hardware/reference/union");
        std::fs::create_dir_all(&source)?;
        let fitting = Plane::XY.cuboid(8., 6., 4.);
        let nut = Plane::XY.cuboid(10., 8., 2.);
        let bodies = [Body {name:"fitting", color:None, solid:&fitting}, Body {name:"nut", color:None, solid:&nut}];
        let model = source.join("union.step.npz");
        let payload = source.join("union.step.mesh");
        std::fs::write(&model, hsm_kernel::step::model_bytes(&bodies))?;
        let raw = hsm_kernel::write::payload_bytes_with_sources(&bodies, None, None);
        hsm_geometry::scene::store(&raw)?;
        std::fs::write(&payload, &raw)?;
        let frame = json!([[0.,-1.,0.,31.],[1.,0.,0.,52.],[0.,0.,1.,73.]]);
        let nut_frame = json!([[1.,0.,0.,31.],[0.,1.,0.,51.],[0.,0.,1.,73.]]);
        let relative = "hardware/reference/union/union.step.mesh";
        for graft in [false, true] {
            let output = root.join(if graft {"graft"} else {"reference"});
            let mut spec = json!({"instances":[
                {"model":model,"indices":[0],"name":"bulkhead-carb","transform":frame},
                {"model":model,"indices":[1],"name":"bulkhead-carb-nut","transform":nut_frame}
            ]});
            if graft {
                spec["presentation"] = json!([
                    {"model":model,"indices":[0],"targets":["bulkhead-carb"],"transform":frame},
                    {"model":model,"indices":[1],"targets":["bulkhead-carb-nut"],"transform":nut_frame}
                ]);
            }
            super::super::model::physical(&spec, &output)?;
            let bytes = std::fs::read(output.join("enclosure-assembly.step.mesh"))?;
            let mut head = hsm_geometry::scene::header(&bytes)?.0;
            let before = head["meshes"].as_array().unwrap().clone();
            for (node, original) in before.iter().zip(["fitting", "nut"]) {
                assert_eq!(node["source"], relative);
                assert_eq!(node["source_name"], original);
            }
            let bigger = Plane::XY.cuboid(12., 6., 4.);
            let changed = [Body {name:"fitting", color:None, solid:&bigger}, bodies[1], Body {name:"spare", color:None, solid:&nut}];
            let next = hsm_kernel::write::payload_bytes_with_sources(&changed, None, None);
            assert!(hsm_geometry::scene::replace_selected(&mut head, relative, &next)? > 0);
            let after = head["meshes"].as_array().unwrap();
            assert_eq!(after.len(), before.len());
            assert_ne!(after[0]["asset"], before[0]["asset"]);
            for (a, b) in after.iter().zip(&before) {
                assert_eq!(a["name"], b["name"]);
                assert_eq!(a["transform"], b["transform"]);
                assert_eq!(a["source_sha256"], super::super::digest(&next));
            }
            let removed = hsm_kernel::write::payload_bytes_with_sources(&changed[..1], None, None);
            hsm_geometry::scene::replace_selected(&mut head, relative, &removed)?;
            assert_eq!(head["meshes"].as_array().unwrap().len(), 1);
            assert_eq!(head["meshes"][0]["name"], "bulkhead-carb");
        }
        std::fs::remove_dir_all(root)?;
        Ok(())
    }
}
