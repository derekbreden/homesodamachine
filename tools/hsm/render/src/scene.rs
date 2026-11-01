//! A payload as the renderer holds it: every solid's triangles in one vertex and index array,
//! its feature edges, its box, and the body name a role or a label addresses it by.

use crate::payload;
use anyhow::{Context, Result};
use bytemuck::{Pod, Zeroable};
use std::{
    collections::HashMap,
    ops::Range,
    path::{Path, PathBuf},
    sync::atomic::{AtomicUsize, Ordering},
    time::SystemTime,
};

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Aabb {
    pub min: [f64; 3],
    pub max: [f64; 3],
}

impl Aabb {
    pub const EMPTY: Aabb = Aabb {
        min: [f64::INFINITY; 3],
        max: [f64::NEG_INFINITY; 3],
    };

    pub fn is_empty(&self) -> bool {
        (0..3).any(|a| self.min[a] > self.max[a])
    }

    pub fn add_point(&mut self, p: [f64; 3]) {
        for a in 0..3 {
            self.min[a] = self.min[a].min(p[a]);
            self.max[a] = self.max[a].max(p[a]);
        }
    }

    pub fn union(&mut self, other: &Aabb) {
        if other.is_empty() {
            return;
        }
        self.add_point(other.min);
        self.add_point(other.max);
    }

    pub fn center(&self) -> [f64; 3] {
        std::array::from_fn(|a| (self.min[a] + self.max[a]) / 2.0)
    }

    pub fn size(&self) -> [f64; 3] {
        std::array::from_fn(|a| self.max[a] - self.min[a])
    }

    pub fn max_dim(&self) -> f64 {
        let s = self.size();
        s[0].max(s[1]).max(s[2])
    }

    /// Half the diagonal: the radius of the sphere three.js's `Box3.getBoundingSphere` returns.
    pub fn radius(&self) -> f64 {
        let s = self.size();
        (s[0] * s[0] + s[1] * s[1] + s[2] * s[2]).sqrt() / 2.0
    }
}

/// One feature-edge segment, as the line shader reads it.
#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
pub struct Segment {
    pub a: [f32; 3],
    pub mesh: u32,
    pub b: [f32; 3],
    pub pad: u32,
}

/// One solid of the payload: one draw.
pub struct Mesh {
    pub name: String,
    pub body: usize,
    /// Linear RGB, or none when the STEP carried no colour.
    pub color: Option<[f64; 3]>,
    pub has_colors: bool,
    pub has_uv: bool,
    pub vertices: Range<u32>,
    pub indices: Range<u32>,
    pub segments: Range<u32>,
    pub bbox: Aabb,
}

/// A body is what the viewer's picker names: the solids `<body>/<n>` share one body.
pub struct Body {
    pub name: String,
    pub meshes: Vec<usize>,
    pub bbox: Aabb,
}

/// Optional render-only vertex data. Ordinary CAD payloads allocate none.
#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
pub struct VertexAux {
    pub color: [f32; 4],
    pub uv: [f32; 4],
}

pub struct Scene {
    pub path: PathBuf,
    pub stamp: (u64, SystemTime),
    pub meshes: Vec<Mesh>,
    pub bodies: Vec<Body>,
    pub positions: Vec<[f32; 3]>,
    pub normals: Vec<[f32; 3]>,
    pub attributes: Vec<VertexAux>,
    pub indices: Vec<u32>,
    pub segments: Vec<Segment>,
    pub bbox: Aabb,
}

pub fn stamp(path: &Path) -> Result<(u64, SystemTime)> {
    let meta = std::fs::metadata(path).with_context(|| format!("no payload at {}", path.display()))?;
    Ok((meta.len(), meta.modified()?))
}

/// `<body>/<n>` names one solid of a body of several (`_per_solid_color` in
/// hardware/scripts/_cadq_export.py); the body is the name without the index.
pub fn body_name(name: &str) -> &str {
    match name.rfind('/') {
        Some(i) if i + 1 < name.len() && name[i + 1..].bytes().all(|b| b.is_ascii_digit()) => {
            &name[..i]
        }
        _ => name,
    }
}

impl Scene {
    pub fn load(path: &Path) -> Result<Scene> {
        let stamp = stamp(path)?;
        let bytes = std::fs::read(path).with_context(|| format!("read {}", path.display()))?;
        let raw = payload::decode(&bytes).with_context(|| format!("decode {}", path.display()))?;
        drop(bytes);
        let edges = edges_of_all(&raw);
        let attributes = raw.iter().any(|m| m.colors.is_some() || m.uv.is_some());

        let mut scene = Scene {
            path: path.to_owned(),
            stamp,
            meshes: Vec::with_capacity(raw.len()),
            bodies: Vec::new(),
            positions: Vec::new(),
            normals: Vec::new(),
            attributes: Vec::new(),
            indices: Vec::new(),
            segments: Vec::new(),
            bbox: Aabb::EMPTY,
        };
        let mut body_of: HashMap<String, usize> = HashMap::new();
        for (i, (m, segs)) in raw.into_iter().zip(edges).enumerate() {
            let v0 = scene.positions.len() as u32;
            let i0 = scene.indices.len() as u32;
            let s0 = scene.segments.len() as u32;
            let mut bbox = Aabb::EMPTY;
            for p in &m.positions {
                bbox.add_point([p[0] as f64, p[1] as f64, p[2] as f64]);
            }
            scene.positions.extend_from_slice(&m.positions);
            scene.normals.extend_from_slice(&m.normals);
            if attributes {
                scene.attributes.extend((0..m.positions.len()).map(|i| {
                    let [r, g, b] = m.colors.as_ref().map_or([1.0; 3], |c| c[i]);
                    let [u, v] = m.uv.as_ref().map_or([0.0; 2], |uv| uv[i]);
                    VertexAux { color: [r, g, b, 1.0], uv: [u, v, 0.0, 0.0] }
                }));
            }
            scene.indices.extend_from_slice(&m.indices);
            scene.segments.extend(segs.into_iter().map(|[a, b]| Segment {
                a,
                mesh: i as u32,
                b,
                pad: 0,
            }));
            let body = body_name(&m.name).to_owned();
            let next = scene.bodies.len();
            let b = *body_of.entry(body.clone()).or_insert(next);
            if b == next {
                scene.bodies.push(Body {
                    name: body,
                    meshes: Vec::new(),
                    bbox: Aabb::EMPTY,
                });
            }
            scene.bodies[b].meshes.push(i);
            scene.bodies[b].bbox.union(&bbox);
            scene.bbox.union(&bbox);
            scene.meshes.push(Mesh {
                name: m.name,
                body: b,
                color: m.color,
                has_colors: m.colors.is_some(),
                has_uv: m.uv.is_some(),
                vertices: v0..scene.positions.len() as u32,
                indices: i0..scene.indices.len() as u32,
                segments: s0..scene.segments.len() as u32,
                bbox,
            });
        }
        Ok(scene)
    }

    /// How many feature-edge segments the scene draws, kept once the segments are on the GPU.
    pub fn segment_count(&self) -> u32 {
        self.meshes.last().map_or(0, |m| m.segments.end)
    }

    /// The triangle corners of one mesh, in world coordinates.
    pub fn triangles(&self, mesh: usize) -> impl Iterator<Item = [[f32; 3]; 3]> + '_ {
        let m = &self.meshes[mesh];
        let base = m.vertices.start as usize;
        self.indices[m.indices.start as usize..m.indices.end as usize]
            .chunks_exact(3)
            .map(move |t| std::array::from_fn(|k| self.positions[base + t[k] as usize]))
    }
}

/// Feature edges for every mesh, several meshes at once.
fn edges_of_all(raw: &[payload::RawMesh]) -> Vec<Vec<[[f32; 3]; 2]>> {
    let next = AtomicUsize::new(0);
    let workers = std::thread::available_parallelism()
        .map(|n| n.get())
        .unwrap_or(1)
        .clamp(1, 4);
    let mut out: Vec<Vec<[[f32; 3]; 2]>> = (0..raw.len()).map(|_| Vec::new()).collect();
    let done: Vec<Vec<(usize, Vec<[[f32; 3]; 2]>)>> = std::thread::scope(|s| {
        let handles: Vec<_> = (0..workers)
            .map(|_| {
                s.spawn(|| {
                    let mut mine = Vec::new();
                    loop {
                        let i = next.fetch_add(1, Ordering::Relaxed);
                        let Some(m) = raw.get(i) else { break };
                        mine.push((i, feature_edges(&m.positions, &m.indices, &m.faces)));
                    }
                    mine
                })
            })
            .collect();
        handles.into_iter().map(|h| h.join().unwrap()).collect()
    });
    for (i, segs) in done.into_iter().flatten() {
        out[i] = segs;
    }
    out
}

/// The cosine the viewer's `EdgesGeometry(geometry, 30)` creases at.
const CREASE_COS: f32 = 0.866_025_4;

/// LINE ART ALONG FACE BOUNDARIES. A payload states which B-rep face each triangle came from, so
/// an edge between two faces is drawn and an edge inside one is not, however coarsely the face
/// was tessellated; an edge with one triangle is the rim of an open shell and is drawn too. A
/// mesh that states no faces falls back to the viewer's own 30° crease. Corners are welded on a
/// 1e-4 lattice, as `EdgesGeometry` welds them, since each face carries its own copy of the
/// vertices along its boundary.
pub fn feature_edges(pos: &[[f32; 3]], idx: &[u32], faces: &[[u32; 2]]) -> Vec<[[f32; 3]; 2]> {
    let mut weld: HashMap<[i64; 3], u32> = HashMap::with_capacity(pos.len());
    let welded: Vec<u32> = pos
        .iter()
        .map(|p| {
            let key = [0, 1, 2].map(|a| (p[a] as f64 * 1e4).round() as i64);
            let next = weld.len() as u32;
            *weld.entry(key).or_insert(next)
        })
        .collect();
    let ntri = idx.len() / 3;
    let mut face_of = vec![u32::MAX; ntri];
    for (f, &[a, b]) in faces.iter().enumerate() {
        for t in a as usize..=(b as usize).min(ntri.saturating_sub(1)) {
            face_of[t] = f as u32;
        }
    }
    let crease = faces.is_empty();
    let normal = |t: usize| -> [f32; 3] {
        let [a, b, c] = [0, 1, 2].map(|k| pos[idx[3 * t + k] as usize]);
        let u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
        let v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
        let n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
        let l = (n[0] * n[0] + n[1] * n[1] + n[2] * n[2]).sqrt();
        if l > 0.0 { n.map(|x| x / l) } else { n }
    };
    let mut half: Vec<(u64, u32, u32, u32)> = Vec::with_capacity(idx.len());
    for t in 0..ntri {
        let v = [0, 1, 2].map(|k| idx[3 * t + k]);
        let w = v.map(|i| welded[i as usize]);
        if w[0] == w[1] || w[1] == w[2] || w[2] == w[0] {
            continue;
        }
        for k in 0..3 {
            let (a, b) = (w[k], w[(k + 1) % 3]);
            let key = ((a.min(b) as u64) << 32) | a.max(b) as u64;
            half.push((key, t as u32, v[k], v[(k + 1) % 3]));
        }
    }
    half.sort_unstable_by_key(|h| (h.0, h.1));
    let mut out = Vec::new();
    let mut i = 0;
    while i < half.len() {
        let mut j = i + 1;
        while j < half.len() && half[j].0 == half[i].0 {
            j += 1;
        }
        let group = &half[i..j];
        let drawn = if group.len() == 1 {
            true
        } else if crease {
            let n0 = normal(group[0].1 as usize);
            group[1..].iter().any(|h| {
                let n = normal(h.1 as usize);
                n0[0] * n[0] + n0[1] * n[1] + n0[2] * n[2] <= CREASE_COS
            })
        } else {
            let f0 = face_of[group[0].1 as usize];
            f0 == u32::MAX || group[1..].iter().any(|h| face_of[h.1 as usize] != f0)
        };
        if drawn {
            let (_, _, a, b) = group[0];
            out.push([pos[a as usize], pos[b as usize]]);
        }
        i = j;
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn body_names() {
        assert_eq!(body_name("cold-core/3"), "cold-core");
        assert_eq!(body_name("tee-y-a"), "tee-y-a");
        assert_eq!(body_name("a/b"), "a/b");
        assert_eq!(body_name("a/"), "a/");
    }

    #[test]
    fn a_cube_of_two_triangle_faces_has_twelve_edges() {
        // Each face its own four vertices, as a B-rep tessellation writes them.
        let mut pos = Vec::new();
        let mut idx = Vec::new();
        let mut faces = Vec::new();
        for axis in 0..3 {
            for side in [0.0f32, 1.0] {
                let base = pos.len() as u32;
                for (u, v) in [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)] {
                    let mut p = [0.0f32; 3];
                    p[axis] = side;
                    p[(axis + 1) % 3] = u;
                    p[(axis + 2) % 3] = v;
                    pos.push(p);
                }
                let t = (idx.len() / 3) as u32;
                idx.extend([base, base + 1, base + 2, base, base + 2, base + 3]);
                faces.push([t, t + 1]);
            }
        }
        assert_eq!(feature_edges(&pos, &idx, &faces).len(), 12);
        // Without faces, the 30° crease finds the same twelve and not the diagonals.
        assert_eq!(feature_edges(&pos, &idx, &[]).len(), 12);
    }
}
