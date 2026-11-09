use anyhow::{Context, Result, ensure};
use hsm_geometry::payload::{self, Payload};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeMap,
    fs,
    os::unix::fs::MetadataExt,
    path::{Path, PathBuf},
    sync::Arc,
};

// The daemon's build ID carries this, so a changed reader or dependency lock replaces it.
pub fn geometry_version() -> String {
    let mut h = Sha256::new();
    h.update(include_str!("../../geometry/src/payload.rs"));
    h.update(include_str!("../../geometry/src/scene.rs"));
    h.update(include_str!("../../geometry/src/queries.rs"));
    h.update(include_str!("../../geometry/src/lib.rs"));
    h.update(include_str!("../../geometry/Cargo.toml"));
    h.update(include_str!("../../Cargo.toml"));
    h.update(include_str!("../../Cargo.lock"));
    format!("{:x}", h.finalize())
}

fn signature(path: &Path) -> Result<[u64; 7]> {
    let m = path.metadata()?;
    Ok([
        m.dev(),
        m.ino(),
        m.len(),
        m.mtime() as u64,
        m.mtime_nsec() as u64,
        m.ctime() as u64,
        m.ctime_nsec() as u64,
    ])
}

/// A scene catalog resolves names and source references before query geometry is allocated.
pub struct Catalog {
    path: PathBuf,
    bytes: Vec<u8>,
    head: Value,
    pub digest: String,
    pub shared: bool,
    pub parts: Vec<CatalogPart>,
}

pub struct CatalogPart {
    pub name: String,
    node: Option<usize>,
    entry: usize,
}

impl Catalog {
    pub fn read(path: &Path) -> Result<Self> {
        let before = signature(path)?;
        let bytes = fs::read(path)?;
        ensure!(before == signature(path)?, "payload changed while loading; retry the query");
        let (head, _) = hsm_geometry::scene::header(&bytes)?;
        let shared = head["v"] == 4;
        ensure!(shared || head["v"] == 3, "unsupported query payload version");
        let mut parts = Vec::new();
        for (i, row) in head["meshes"].as_array().context("payload meshes")?.iter().enumerate() {
            if shared {
                for (entry, instance) in row["entries"].as_array().context("instance entries")?.iter().enumerate() {
                    parts.push(CatalogPart {name: instance["name"].as_str().context("instance name")?.into(), node: Some(i), entry});
                }
            } else {
                parts.push(CatalogPart {name: row["name"].as_str().context("mesh name")?.into(), node: None, entry: i});
            }
        }
        Ok(Self {path: path.into(), digest: hsm_geometry::scene::digest(&bytes), bytes, head, shared, parts})
    }

    pub fn matches(&self, selector: &str) -> Vec<usize> {
        if selector.is_empty() { return (0..self.parts.len()).collect(); }
        if let Some(index) = selector.strip_prefix('#').and_then(|s|s.parse::<usize>().ok()) {
            return (index < self.parts.len()).then_some(index).into_iter().collect();
        }
        let needle = selector.to_lowercase();
        let exact = self.parts.iter().enumerate().filter(|(_,p)|p.name.to_lowercase()==needle).map(|(i,_)|i).collect::<Vec<_>>();
        if !exact.is_empty() { return exact; }
        self.parts.iter().enumerate().filter(|(_,p)|p.name.to_lowercase().contains(&needle)).map(|(i,_)|i).collect()
    }

    pub fn one(&self, selector: &str) -> Result<usize> {
        let ids = self.matches(selector);
        ensure!(!ids.is_empty(), "no part matches {selector:?}; use hsm where to list names");
        ensure!(ids.len()==1, "{selector:?} matches {} solids: {}; select a unique name or #index", ids.len(),
            ids.iter().take(12).map(|&i|format!("#{i} {}",self.parts[i].name)).collect::<Vec<_>>().join(", "));
        Ok(ids[0])
    }

    fn describe(&self, index: usize, bytes: &[u8], row: &Value) -> Result<Value> {
        let part = &self.parts[index];
        let node = part.node.map(|i|&self.head["meshes"][i]);
        let origin = node.or_else(||row.get("_scene")).unwrap_or(&Value::Null);
        let transform = &origin["transform"];
        let [min,max] = hsm_geometry::scene::entry_bounds(bytes, row, if self.shared {transform} else {&Value::Null})?;
        let mut color = node.map(|node|node["entries"][part.entry]["color"].clone()).unwrap_or_else(||row["color"].clone());
        if color.as_array().is_some_and(|color|color.len()>3) {color=json!(&color.as_array().unwrap()[..3]);}
        let triangles = row["idx"][1].as_u64().context("triangle index count")?;
        let faces = row["fac"][1].as_u64().context("face range count")?;
        ensure!(triangles%3==0 && faces%2==0,"invalid mesh array counts");
        Ok(json!({"id":format!("#{index}"),"name":part.name,"min_mm":min,"max_mm":max,
            "size_mm":[max[0]-min[0],max[1]-min[1],max[2]-min[2]],"color":color,
            "triangles":triangles/3,"faces":faces/2,"source":origin["source"],
            "source_name":origin["source_name"],"source_sha256":origin["source_sha256"],
            "asset":origin["asset"],"transform":transform}))
    }

    pub fn where_data(&self, ids: &[usize]) -> Result<Value> {
        let mut parts = BTreeMap::new();
        if self.shared {
            let mut objects: BTreeMap<String,Vec<usize>> = BTreeMap::new();
            for &i in ids {
                let node = &self.head["meshes"][self.parts[i].node.unwrap()];
                objects.entry(node["asset"].as_str().context("mesh object")?.into()).or_default().push(i);
            }
            for (hash, ids) in objects {
                let bytes = hsm_geometry::scene::load_asset(&hash)?;
                ensure!(hsm_geometry::scene::digest(&bytes)==hash,"mesh object digest mismatch");
                let (head, _) = hsm_geometry::scene::header(&bytes)?;
                for i in ids {
                    let row = head["meshes"].get(self.parts[i].entry).context("missing object entry")?;
                    parts.insert(i, self.describe(i,&bytes,row)?);
                }
            }
        } else {
            for &i in ids { parts.insert(i,self.describe(i,&self.bytes,&self.head["meshes"][self.parts[i].entry])?); }
        }
        let parts = parts.into_values().collect::<Vec<_>>();
        let triangles = parts.iter().map(|p|p["triangles"].as_u64().unwrap()).sum::<u64>();
        Ok(json!({"parts":parts,"scene_solids":self.parts.len(),"selected_triangles":triangles,
            "scene_triangles":if ids.len()==self.parts.len() {Some(triangles)} else {None}}))
    }

    /// Construction children use their installed body's placement and immutable surface revision.
    pub fn features_data(&self, pattern: &str) -> Result<Value> {
        let needle = pattern.to_lowercase();
        let body_pattern = pattern.split_once("::").map(|(body, _)| body);
        let bodies = self.matches(body_pattern.unwrap_or(pattern));
        let mut assets = BTreeMap::<String, Vec<u8>>::new();
        let mut features = Vec::new();
        for (index, part) in self.parts.iter().enumerate() {
            if body_pattern.is_some_and(|body| !part.name.eq_ignore_ascii_case(body)) { continue; }
            let origin = part.node.map(|i| &self.head["meshes"][i]).unwrap_or(&Value::Null);
            if !bodies.is_empty() && !bodies.contains(&index) { continue; }
            if bodies.is_empty() && self.shared && origin["feature_count"].as_u64().unwrap_or(0) == 0 { continue; }
            let bytes = if self.shared {
                let hash = origin["asset"].as_str().context("feature mesh object")?;
                if !assets.contains_key(hash) { assets.insert(hash.into(), hsm_geometry::scene::load_asset(hash)?); }
                &assets[hash]
            } else { &self.bytes };
            let (head, _) = hsm_geometry::scene::header(bytes)?;
            let row = &head["meshes"][part.entry];
            for record in row["features"].as_array().into_iter().flatten() {
                let id = record["id"].as_str().context("feature identity")?;
                let key = format!("{}::{id}",part.name);
                let text = format!("{key} {} {}", record["label"].as_str().unwrap_or(""), record["related"]);
                if bodies.is_empty() && !needle.is_empty() && !text.to_lowercase().contains(&needle) { continue; }
                if body_pattern.is_some() && !key.eq_ignore_ascii_case(pattern) { continue; }
                let [min, max] = hsm_geometry::scene::feature_bounds(bytes, row, record, &origin["transform"])?;
                let mut feature = record.clone();
                feature["name"] = json!(key); feature["body"] = json!(part.name);
                feature["body_index"] = json!(index); feature["asset"] = origin["asset"].clone();
                feature["transform"] = origin["transform"].clone();
                feature["min_mm"] = json!(min); feature["max_mm"] = json!(max);
                feature["size_mm"] = json!([max[0]-min[0],max[1]-min[1],max[2]-min[2]]);
                feature["triangle_count"] = json!(record["triangles"].as_array().into_iter().flatten().map(|r| r[1].as_u64().unwrap()-r[0].as_u64().unwrap()+1).sum::<u64>());
                features.push(feature);
            }
        }
        Ok(json!({"features":features,"scope":"Authored surface selections of the exported body; no separate printable solids."}))
    }

    fn selection(&self, selector: &str) -> Result<(MeshSelection, usize)> {
        let (body, feature) = selector.split_once("::").map_or((selector,None), |(b,f)| (b,Some(f)));
        let index = self.one(body)?;
        if let Some(feature_id) = feature {
            let part = &self.parts[index];
            let origin = part.node.map(|i| &self.head["meshes"][i]).unwrap_or(&Value::Null);
            let bytes = if self.shared { hsm_geometry::scene::load_asset(origin["asset"].as_str().context("feature object")?)? } else {self.bytes.clone()};
            let (head, _) = hsm_geometry::scene::header(&bytes)?;
            let row = &head["meshes"][part.entry];
            let feature = row["features"].as_array().into_iter().flatten().find(|f|f["id"].as_str().is_some_and(|id|id.eq_ignore_ascii_case(feature_id)))
                .with_context(|| format!("no feature {feature_id:?} on {body:?}; use hsm features {body}"))?;
            let surface = hsm_geometry::scene::feature_surface(&bytes,row,feature,&origin["transform"])?;
            let mut mesh = payload::Mesh::from_arrays(selector,surface.vertices,surface.triangles)?;
            mesh.triangle_ids = Some(surface.triangle_ids); mesh.faces=surface.faces; mesh.face_sources=surface.face_sources;
            mesh.features=vec![feature.clone()];
            Ok((MeshSelection::Feature(mesh),index))
        } else {
            let bytes = hsm_geometry::scene::flatten_selected_with(&self.bytes,&[index],hsm_geometry::scene::load_asset)?;
            Ok((MeshSelection::Bytes(bytes),index))
        }
    }

    pub fn response(&self, data: Value, load_ms: f64) -> Value {
        json!({"scene":self.path,"payload_sha256":self.digest,"source_sha256":self.head["src"],
            "step_sha256":if self.shared {Value::Null} else {self.head["src"].clone()},
            "cut":self.head["cut"],"units":"mm","frame":"payload world coordinates","load_ms":load_ms,"data":data})
    }
}

struct Resident {
    payload: Arc<Payload>,
    used: u64,
    budget: u64,
}

enum MeshSelection { Feature(hsm_geometry::payload::Mesh), Bytes(Vec<u8>) }

pub struct Store {
    paths: BTreeMap<PathBuf, ([u64; 7], String)>,
    resident: BTreeMap<String, Resident>,
    tick: u64,
    budget: u64,
    pub loads: u64,
}

impl Store {
    pub fn new(budget_mb: u64) -> Result<Self> {
        Ok(Self {
            paths: BTreeMap::new(),
            resident: BTreeMap::new(),
            tick: 0,
            budget: budget_mb
                .checked_mul(1024 * 1024)
                .context("cache budget overflow")?,
            loads: 0,
        })
    }

    pub fn status(&self) -> serde_json::Value {
        json!({"resident_payloads": self.resident.len(), "payload_loads": self.loads,
            "cache_budget_bytes": self.budget,
            "estimated_resident_bytes": self.resident.values().map(|v| v.budget).sum::<u64>()})
    }

    /// Feature queries build only the requested surface subsets and retain their viewer IDs.
    pub fn load_features(&mut self, catalog: &Catalog, selectors: &[&str]) -> Result<(Arc<Payload>,Vec<usize>)> {
        let key = format!("{}:{selectors:?}",catalog.digest);
        self.tick += 1;
        let indices = selectors.iter().map(|s| catalog.one(s.split_once("::").map_or(*s,|(body,_)|body))).collect::<Result<Vec<_>>>()?;
        if let Some(held) = self.resident.get_mut(&key) { held.used=self.tick; return Ok((held.payload.clone(),indices)); }
        let mut meshes = Vec::new(); let mut budget = 0;
        for selector in selectors {
            let (selection,_) = catalog.selection(selector)?;
            let mesh = match selection {
                MeshSelection::Feature(mesh) => mesh,
                MeshSelection::Bytes(bytes) => {
                    ensure!(bytes.len() as u64*3 <= self.budget,"selected geometry exceeds daemon cache budget");
                    payload::decode(&bytes)?.meshes.pop().context("selected mesh")?
                }
            };
            budget += mesh.shape.vertices().len() as u64*72 + mesh.shape.indices().len() as u64*128;
            ensure!(budget <= self.budget,"selected geometry exceeds daemon cache budget");
            meshes.push(mesh);
        }
        while self.resident.values().map(|v|v.budget).sum::<u64>()+budget>self.budget {
            let oldest=self.resident.iter().min_by_key(|(_,v)|v.used).map(|(k,_)|k.clone());
            if let Some(key)=oldest {self.resident.remove(&key);} else {break;}
        }
        let result = Arc::new(Payload { digest:catalog.digest.clone(),source:catalog.head["src"].as_str().map(str::to_owned),
            cut: catalog.head.get("cut").map(Value::to_string),meshes,shared:catalog.shared });
        self.loads+=1;self.resident.insert(key,Resident {payload:result.clone(),used:self.tick,budget});
        Ok((result,indices))
    }

    /// Selected entries share the scene revision and keep their global payload indices.
    pub fn load_selected(&mut self, catalog: &Catalog, ids: &[usize]) -> Result<Arc<Payload>> {
        let key = format!("{}:{ids:?}",catalog.digest);
        self.tick += 1;
        if let Some(held) = self.resident.get_mut(&key) {held.used=self.tick;return Ok(held.payload.clone());}
        let bytes = hsm_geometry::scene::flatten_selected_with(&catalog.bytes,ids,hsm_geometry::scene::load_asset)?;
        let budget = (bytes.len() as u64).checked_mul(if catalog.shared {3} else {12}).context("query budget overflow")?;
        ensure!(budget<=self.budget,"selected geometry needs an estimated {} MiB cache; daemon budget is {} MiB",budget/1048576,self.budget/1048576);
        while self.resident.values().map(|v|v.budget).sum::<u64>()+budget>self.budget {
            let oldest=self.resident.iter().min_by_key(|(_,v)|v.used).map(|(k,_)|k.clone());
            if let Some(key)=oldest {self.resident.remove(&key);} else {break;}
        }
        let mut payload = payload::decode(&bytes)?;
        payload.digest=catalog.digest.clone();payload.shared=catalog.shared;
        let payload=Arc::new(payload);self.loads+=1;
        self.resident.insert(key,Resident {payload:payload.clone(),used:self.tick,budget});
        Ok(payload)
    }

    pub fn load(&mut self, path: &Path) -> Result<Arc<Payload>> {
        let path = path
            .canonicalize()
            .with_context(|| format!("payload not found: {}", path.display()))?;
        self.tick += 1;
        let before = signature(&path)?;
        if let Some((stamp, digest)) = self.paths.get(&path) {
            if stamp == &before {
                if let Some(held) = self.resident.get_mut(digest) {
                    held.used = self.tick;
                    return Ok(held.payload.clone());
                }
            }
        }
        let bytes = fs::read(&path)?;
        let budget = if hsm_geometry::scene::is_scene(&bytes) {
            let (head,_)=hsm_geometry::scene::header(&bytes)?;
            head["meshes"].as_array().into_iter().flatten().map(|row|row["bytes"].as_u64().unwrap_or(0)).sum::<u64>()
                .checked_mul(3).context("scene budget overflow")?
        } else {before[2].checked_mul(12).context("scene budget overflow")?};
        ensure!(
            budget <= self.budget,
            "scene needs an estimated {} MiB cache; daemon budget is {} MiB",
            budget / 1048576,
            self.budget / 1048576
        );
        ensure!(
            before == signature(&path)?,
            "payload changed while loading; retry the query"
        );
        let digest = format!("{:x}", Sha256::digest(&bytes));
        self.paths.insert(path, (before, digest.clone()));
        if let Some(held) = self.resident.get_mut(&digest) {
            held.used = self.tick;
            return Ok(held.payload.clone());
        }
        // Conservative cache accounting includes lazy Manifold copies. This is
        // a cache budget, not a hard limit on process RSS or a query's scratch.
        while self.resident.values().map(|v| v.budget).sum::<u64>() + budget > self.budget {
            let oldest = self
                .resident
                .iter()
                .min_by_key(|(_, v)| v.used)
                .map(|(k, _)| k.clone());
            if let Some(key) = oldest {
                self.resident.remove(&key);
            } else {
                break;
            }
        }
        let payload = Arc::new(payload::decode(&bytes)?);
        self.loads += 1;
        self.resident.insert(
            digest,
            Resident {
                payload: payload.clone(),
                used: self.tick,
                budget,
            },
        );
        Ok(payload)
    }
}
