use crate::store::Store;
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
        origin: [f64; 3],
        direction: [f64; 3],
        #[serde(default = "ray_max")]
        max_distance: f64,
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

pub fn matches(payload: &Payload, selector: &str) -> Vec<usize> {
    if selector.is_empty() {
        return (0..payload.meshes.len()).collect();
    }
    if let Some(index) = selector
        .strip_prefix('#')
        .and_then(|s| s.parse::<usize>().ok())
    {
        return if index < payload.meshes.len() {
            vec![index]
        } else {
            vec![]
        };
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

fn one(payload: &Payload, selector: &str) -> Result<usize> {
    let ids = matches(payload, selector);
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
            .map(|&i| format!("#{i} {}", payload.meshes[i].name))
            .collect::<Vec<_>>()
            .join(", ")
    );
    Ok(ids[0])
}

fn named(index: usize, mesh: &Mesh) -> Value {
    json!({"id": format!("#{index}"), "name": mesh.name})
}

pub fn execute(store: &mut Store, request: Request, build_id: &str) -> Result<Value> {
    match request.query {
        Query::Ping => {
            return Ok(
                json!({"build_id": build_id, "pid": std::process::id(), "protocol": 1, "cache": store.status()}),
            );
        }
        Query::Status => {
            return Ok(
                json!({"build_id": build_id, "pid": std::process::id(), "cache": store.status()}),
            );
        }
        Query::Shutdown => return Ok(json!({"stopping": true})),
        _ => (),
    }
    let started = Instant::now();
    let payload = store.load(&request.scene)?;
    let load_ms = started.elapsed().as_secs_f64() * 1000.0;
    let meshes = &payload.meshes;
    let result = match request.query {
        Query::Where { pattern } => {
            let parts: Vec<_> = matches(&payload, &pattern)
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
            let (a, b) = (one(&payload, &a)?, one(&payload, &b)?);
            json!({"a": named(a, &meshes[a]), "b": named(b, &meshes[b]),
                "gap": queries::gap(&meshes[a], &meshes[b], [0.0; 3])?})
        }
        Query::Overlap { a, b } => {
            let (a, b) = (one(&payload, &a)?, one(&payload, &b)?);
            json!({"a": named(a, &meshes[a]), "b": named(b, &meshes[b]),
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
            let a = one(&payload, &part)?;
            let candidates = if let Some(b) = against {
                vec![one(&payload, &b)?]
            } else {
                (0..meshes.len()).filter(|&i| i != a).collect()
            };
            let mut overlaps = Vec::new();
            let mut unknown = Vec::new();
            for b in candidates {
                match queries::overlap(&meshes[a], &meshes[b], by) {
                    Ok(v) if v > min_volume => {
                        overlaps.push(json!({"part": named(b, &meshes[b]), "volume_mm3": v}))
                    }
                    Ok(_) => (),
                    Err(e) => {
                        unknown.push(json!({"part": named(b, &meshes[b]), "error": e.to_string()}))
                    }
                }
            }
            json!({"part": named(a, &meshes[a]), "translation_mm": by, "bounds_mm": meshes[a].bounds(by),
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
            let a = one(&payload, &part)?;
            json!({"part": named(a, &meshes[a]), "section": queries::section(&meshes[a], normal, offset)?})
        }
        Query::Ray {
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
                        closest = Some(json!({"part": named(i, mesh), "hit": hit}));
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
        json!({"scene": request.scene, "payload_sha256": payload.digest, "step_sha256": payload.source,
        "cut": payload.cut.as_ref().and_then(|s| serde_json::from_str::<Value>(s).ok()),
        "units": "mm", "frame": "payload world coordinates", "load_ms": load_ms, "data": result}),
    )
}
