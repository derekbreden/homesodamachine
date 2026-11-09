use crate::store::{Catalog, Store};
use anyhow::{Result, anyhow, ensure};
use hsm_geometry::{
    payload::{Mesh, Payload},
    queries,
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::{path::PathBuf, time::Instant};

#[derive(Debug, Deserialize, Serialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
pub enum Query {
    Ping,
    Status,
    Shutdown,
    Where {
        #[serde(default)]
        pattern: String,
    },
    Features {
        #[serde(default)]
        pattern: String,
    },
    Gap {
        a: String,
        b: String,
    },
    Overlap {
        a: String,
        b: String,
    },
    Move {
        part: String,
        by: [f64; 3],
        against: Option<String>,
        #[serde(default = "move_min_volume")]
        min_volume: f64,
    },
    Section {
        part: String,
        normal: [f64; 3],
        offset: f64,
    },
    Ray {
        #[serde(default)]
        part: Option<String>,
        origin: [f64; 3],
        direction: [f64; 3],
        #[serde(default = "ray_max")]
        max_distance: f64,
    },
    /// A picture drawn by the resident renderer, or with `list` the bodies it would draw.
    Render {
        root: PathBuf,
        job: Box<hsm_render::job::Job>,
        #[serde(default)]
        list: bool,
    },
    /// A run of a part's program, answered from the kept runs where one still holds (`build`).
    Run {
        workspace: PathBuf,
        root: PathBuf,
        #[serde(rename = "crate")]
        krate: String,
        name: String,
        #[serde(default)]
        args: Vec<String>,
    },
    /// A declared Python generator action, staged and kept by the existing part store.
    Generate {
        workspace: PathBuf,
        target: String,
        #[serde(default)]
        output: Option<PathBuf>,
        #[serde(default)]
        python: Option<PathBuf>,
    },
}

fn ray_max() -> f64 {
    1e6
}
fn move_min_volume() -> f64 {
    1e-6
}

#[derive(Deserialize, Serialize)]
pub struct Request {
    #[serde(default)]
    pub scene: PathBuf,
    #[serde(flatten)]
    pub query: Query,
}

impl Query {
    pub fn needs_scene(&self) -> bool {
        matches!(self, Self::Where { .. } | Self::Features { .. } | Self::Gap { .. } | Self::Overlap { .. }
            | Self::Move { .. } | Self::Section { .. } | Self::Ray { .. })
    }
}

pub fn matches(payload: &Payload, selector: &str, indices: &[usize]) -> Vec<usize> {
    if selector.is_empty() {
        return (0..payload.meshes.len()).collect();
    }
    if let Some(index) = selector
        .strip_prefix('#')
        .and_then(|s| s.parse::<usize>().ok())
    {
        return indices.iter().position(|&id|id==index).into_iter().collect();
    }
    let needle = selector.to_lowercase();
    let exact: Vec<_> = payload
        .meshes
        .iter()
        .enumerate()
        .filter(|(_, m)| m.name.to_lowercase() == needle)
        .map(|(i, _)| i)
        .collect();
    if !exact.is_empty() {
        return exact;
    }
    payload
        .meshes
        .iter()
        .enumerate()
        .filter(|(_, m)| m.name.to_lowercase().contains(&needle))
        .map(|(i, _)| i)
        .collect()
}

fn one(payload: &Payload, selector: &str, indices: &[usize]) -> Result<usize> {
    let ids = matches(payload, selector, indices);
    ensure!(
        !ids.is_empty(),
        "no part matches {selector:?}; use hsm where to list names"
    );
    ensure!(
        ids.len() == 1,
        "{selector:?} matches {} solids: {}; select a unique name or #index",
        ids.len(),
        ids.iter()
            .take(12)
            .map(|&i| format!("#{} {}", indices[i], payload.meshes[i].name))
            .collect::<Vec<_>>()
            .join(", ")
    );
    Ok(ids[0])
}

fn named(index: usize, mesh: &Mesh, indices: &[usize]) -> Value {
    if mesh.triangle_ids.is_some() { return json!({"id":mesh.name,"name":mesh.name,"body_id":format!("#{}",indices[index])}); }
    json!({"id": format!("#{}",indices[index]), "name": mesh.name})
}

pub fn execute(store: &mut Store, builds: &crate::build::Builder, request: Request, build_id: &str) -> Result<Value> {
    match request.query {
        Query::Ping => {
            return Ok(
                json!({"build_id": build_id, "pid": std::process::id(), "protocol": 1, "run_slots": 1, "cache": store.status()}),
            );
        }
        Query::Status => {
            return Ok(
                json!({"build_id": build_id, "pid": std::process::id(), "run_slots": 1, "cache": store.status(),
                "render": crate::render::status(), "builds": builds.status()}),
            );
        }
        Query::Shutdown => return Ok(json!({"stopping": true})),
        Query::Render { .. } => return Err(anyhow!("a render is answered off the query loop")),
        Query::Run { .. } | Query::Generate { .. } => return Err(anyhow!("a run is answered off the query loop")),
        _ => (),
    }
    let started = Instant::now();
    if let Query::Features { pattern } = &request.query {
        let catalog = Catalog::read(&request.scene)?;
        return Ok(catalog.response(catalog.features_data(pattern)?, started.elapsed().as_secs_f64()*1000.));
    }
    if let Query::Where { pattern } = &request.query {
        let catalog=Catalog::read(&request.scene)?;
        let data=if pattern.contains("::") { catalog.features_data(pattern)? } else { catalog.where_data(&catalog.matches(pattern))? };
        return Ok(catalog.response(data,started.elapsed().as_secs_f64()*1000.));
    }
    let selectors = match &request.query {
        Query::Gap { a,b } | Query::Overlap { a,b } => Some(vec![a.as_str(),b.as_str()]),
        Query::Section { part,.. } => Some(vec![part.as_str()]),
        Query::Move { part,against:Some(against),.. } => Some(vec![part.as_str(),against.as_str()]),
        Query::Ray { part: Some(part), .. } => Some(vec![part.as_str()]),
        _ => None,
    };
    let (payload,indices)=if let Some(selectors)=selectors {
        let catalog=Catalog::read(&request.scene)?;
        if selectors.iter().any(|s|s.contains("::")) {
            store.load_features(&catalog,&selectors)?
        } else {
        let mut ids=selectors.into_iter().map(|selector|catalog.one(selector)).collect::<Result<Vec<_>>>()?;
        ids.sort_unstable();ids.dedup();
        (store.load_selected(&catalog,&ids)?,ids)
        }
    } else {
        let payload=store.load(&request.scene)?;
        let ids=(0..payload.meshes.len()).collect();
        (payload,ids)
    };
    let load_ms = started.elapsed().as_secs_f64() * 1000.0;
    let meshes = &payload.meshes;
    let result = match request.query {
        Query::Features { .. } => unreachable!("feature metadata returns before geometry loading"),
        Query::Where { pattern } => {
            let parts: Vec<_> = matches(&payload, &pattern, &indices)
                .iter()
                .map(|&i| {
                    let mesh = &meshes[i];
                    let (min, max) = mesh.bounds([0.0; 3]);
                    json!({"id": format!("#{i}"), "name": mesh.name, "min_mm": min, "max_mm": max,
                    "size_mm": [max[0]-min[0],max[1]-min[1],max[2]-min[2]], "color": mesh.color,
                    "triangles": mesh.shape.indices().len(), "faces": mesh.faces.len()})
                })
                .collect();
            json!({"parts": parts, "scene_solids": meshes.len(),
                "scene_triangles": meshes.iter().map(|m| m.shape.indices().len()).sum::<usize>()})
        }
        Query::Gap { a, b } => {
            let (a, b) = (one(&payload, &a, &indices)?, one(&payload, &b, &indices)?);
            json!({"a": named(a, &meshes[a], &indices), "b": named(b, &meshes[b], &indices),
                "gap": queries::gap(&meshes[a], &meshes[b], [0.0; 3])?})
        }
        Query::Overlap { a, b } => {
            let (a, b) = (one(&payload, &a, &indices)?, one(&payload, &b, &indices)?);
            json!({"a": named(a, &meshes[a], &indices), "b": named(b, &meshes[b], &indices),
                "volume_mm3": queries::overlap(&meshes[a], &meshes[b], [0.0; 3])?})
        }
        Query::Move {
            part,
            by,
            against,
            min_volume,
        } => {
            ensure!(
                by.iter().all(|n| n.is_finite()),
                "translation must be finite"
            );
            ensure!(
                min_volume.is_finite() && min_volume >= 0.0,
                "minimum volume must be finite and nonnegative"
            );
            let a = one(&payload, &part, &indices)?;
            let candidates = if let Some(b) = against {
                vec![one(&payload, &b, &indices)?]
            } else {
                (0..meshes.len()).filter(|&i| i != a).collect()
            };
            let mut overlaps = Vec::new();
            let mut unknown = Vec::new();
            for b in candidates {
                match queries::overlap(&meshes[a], &meshes[b], by) {
                    Ok(v) if v > min_volume => {
                        overlaps.push(json!({"part": named(b, &meshes[b], &indices), "volume_mm3": v}))
                    }
                    Ok(_) => (),
                    Err(e) => {
                        unknown.push(json!({"part": named(b, &meshes[b], &indices), "error": e.to_string()}))
                    }
                }
            }
            json!({"part": named(a, &meshes[a], &indices), "translation_mm": by, "bounds_mm": meshes[a].bounds(by),
                "overlaps": overlaps, "min_volume_mm3": min_volume, "unknown": unknown, "complete": unknown.is_empty()})
        }
        Query::Section {
            part,
            normal,
            offset,
        } => {
            ensure!(
                normal.iter().all(|v| v.is_finite()) && offset.is_finite(),
                "plane must be finite"
            );
            let a = one(&payload, &part, &indices)?;
            json!({"part": named(a, &meshes[a], &indices), "section": queries::section(&meshes[a], normal, offset)?})
        }
        Query::Ray {
            part: _,
            origin,
            direction,
            max_distance,
        } => {
            ensure!(
                origin.iter().chain(&direction).all(|v| v.is_finite()) && max_distance.is_finite(),
                "ray must be finite"
            );
            let mut closest = None;
            let mut limit = max_distance;
            // Strictly closer hits win; a tie keeps payload order.
            for (i, mesh) in meshes.iter().enumerate() {
                if let Some(hit) = queries::ray(mesh, origin, direction, limit)? {
                    if closest.is_none() || hit.distance_mm < limit {
                        limit = hit.distance_mm;
                        closest = Some(json!({"part": named(i, mesh, &indices), "hit": hit}));
                        if limit == 0.0 {
                            break;
                        }
                    }
                }
            }
            json!({"closest": closest})
        }
        _ => return Err(anyhow!("unsupported scene operation")),
    };
    Ok(
        json!({"scene": request.scene, "payload_sha256": payload.digest, "source_sha256":payload.source,
        "step_sha256":if payload.shared {None} else {payload.source.as_ref()},
        "cut": payload.cut.as_ref().and_then(|s| serde_json::from_str::<Value>(s).ok()),
        "units": "mm", "frame": "payload world coordinates", "load_ms": load_ms, "data": result}),
    )
}

#[cfg(test)]
mod lookup_tests {
    use super::*;
    use hsm_geometry::scene;
    use std::{fs, sync::atomic::{AtomicU64, Ordering}};
    static NEXT: AtomicU64 = AtomicU64::new(0);

    // Each fixture isolates its build store and leaves only immutable geometry in the shared cache.
    struct Fixture {dir: PathBuf, scene: PathBuf}
    impl Drop for Fixture {fn drop(&mut self) {let _=fs::remove_dir_all(&self.dir);}}
    fn fixture() -> Result<Fixture> {
        let root=std::path::Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(3).unwrap();
        let dir=root.join(format!(".cache/runs/hsm-lookup-test-{}-{}",std::process::id(),NEXT.fetch_add(1,Ordering::Relaxed)));
        fs::create_dir_all(&dir)?;
        let mut blob=Vec::new();
        for v in [0f32,0.,0.,1.,0.,0.,0.,1.,0.,0.,0.,1.,0.,0.,1.,0.,0.,1.] {blob.extend_from_slice(&v.to_le_bytes());}
        for v in [0u32,1,2,0,0] {blob.extend_from_slice(&v.to_le_bytes());}
        let bytes=scene::encode(&json!({"v":3,"meshes":[{"name":"shape","pos":[0,9],"nrm":[36,9],"idx":[72,3],"fac":[84,2]}]}),&blob)?;
        let packed=scene::pack(&bytes)?;
        let original=&packed["meshes"][0];
        let mut nodes=Vec::new();
        for (i,name) in ["unavailable","pump-a","pump-b","nameplate"].into_iter().enumerate() {
            let mut node=original.clone();node["name"]=json!(name);node["entries"][0]["name"]=json!(name);
            node["transform"]=json!([[1.,0.,0.,i as f64*100.],[0.,1.,0.,0.],[0.,0.,1.,0.]]);
            node["source"]=json!("hardware/part.step.mesh");node["source_name"]=json!("shape");node["source_sha256"]=json!("authored-source");
            node["bytes"]=json!(1_000_000_000u64);
            if i==0 {node["asset"]=json!("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff");}
            nodes.push(node);
        }
        let path=dir.join("fixture.step.mesh");
        fs::write(&path,scene::encode(&json!({"v":4,"meshes":nodes,"src":"scene-source","source_kind":"scene"}),&[])?)?;
        Ok(Fixture {dir,scene:path})
    }

    #[test]
    fn lookup_bounds_skip_missing_neighbors_and_the_geometry_budget() -> Result<()> {
        let f=fixture()?;let mut store=Store::new(0)?;let builds=crate::build::Builder::new(&f.dir,0)?;
        let result=execute(&mut store,&builds,Request {scene:f.scene.clone(),query:Query::Where {pattern:"pump-a".into()}},"test")?;
        let part=&result["data"]["parts"][0];
        assert_eq!(part["id"],"#1");assert_eq!(part["min_mm"],json!([100.,0.,0.]));
        assert_eq!(part["max_mm"],json!([101.,1.,0.]));assert_eq!(part["source"],"hardware/part.step.mesh");
        assert_eq!(part["source_name"],"shape");assert_eq!(part["source_sha256"],"authored-source");
        assert_eq!(result["payload_sha256"],scene::digest(&fs::read(&f.scene)?));
        assert_eq!(result["source_sha256"],"scene-source");assert!(result["step_sha256"].is_null());
        assert_eq!(result["data"]["scene_solids"],4);assert_eq!(result["data"]["selected_triangles"],1);
        assert_eq!(store.loads,0);
        Ok(())
    }

    #[test]
    fn lookup_pair_and_section_preserve_global_indices_and_cached_selection() -> Result<()> {
        let f=fixture()?;let mut store=Store::new(1)?;let builds=crate::build::Builder::new(&f.dir,0)?;
        let gap=||Request {scene:f.scene.clone(),query:Query::Gap {a:"#3".into(),b:"#1".into()}};
        let result=execute(&mut store,&builds,gap(),"test")?;
        assert_eq!(result["data"]["a"]["name"],"nameplate");assert_eq!(result["data"]["a"]["id"],"#3");
        assert_eq!(result["data"]["b"]["id"],"#1");assert_eq!(result["data"]["gap"]["surface_distance_mm"],199.);
        let loads=store.loads;execute(&mut store,&builds,gap(),"test")?;assert_eq!(store.loads,loads);
        let result=execute(&mut store,&builds,Request {scene:f.scene.clone(),query:Query::Section {part:"#2".into(),normal:[1.,0.,0.],offset:200.5}},"test")?;
        assert_eq!(result["data"]["part"]["name"],"pump-b");assert_eq!(result["data"]["part"]["id"],"#2");
        let error=execute(&mut store,&builds,Request {scene:f.scene.clone(),query:Query::Gap {a:"pump".into(),b:"nameplate".into()}},"test").unwrap_err().to_string();
        assert!(error.contains("#1 pump-a, #2 pump-b"),"{error}");
        Ok(())
    }
}
