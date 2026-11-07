//! A part's printed mesh, read from its STL.
//!
//! Corners that land on the same point, to the hundred-millionth of a millimetre, become one
//! vertex, kept where it first appears: the vertices and faces trimesh gives the Python
//! preparers, so a project carries the same mesh either way.

use anyhow::{bail, Context, Result};
use std::collections::HashMap;
use std::path::Path;

#[derive(Clone, Debug)]
pub struct Mesh {
    pub vertices: Vec<[f64; 3]>,
    pub faces: Vec<[usize; 3]>,
}

impl Mesh {
    pub fn read_stl(path: &Path) -> Result<Mesh> {
        let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
        let corners = stl_corners(&bytes).with_context(|| format!("reading {}", path.display()))?;
        Ok(Mesh::from_corners(&corners))
    }

    pub fn from_corners(corners: &[[f64; 3]]) -> Mesh {
        let mut index: HashMap<[i64; 3], usize> = HashMap::new();
        let mut vertices = Vec::new();
        let mut flat = Vec::with_capacity(corners.len());
        for corner in corners {
            let key = corner.map(|v| (v * 1e8).round() as i64);
            let at = *index.entry(key).or_insert_with(|| {
                vertices.push(*corner);
                vertices.len() - 1
            });
            flat.push(at);
        }
        let faces = flat.chunks(3).map(|c| [c[0], c[1], c[2]]).collect();
        Mesh { vertices, faces }
    }

    pub fn bounds(&self) -> ([f64; 3], [f64; 3]) {
        bounds(&self.vertices)
    }

    /// The centre of the bounding box.
    pub fn center(&self) -> [f64; 3] {
        let (low, high) = self.bounds();
        [0, 1, 2].map(|i| (low[i] + high[i]) / 2.0)
    }

    /// The enclosed volume, positive for outward-facing triangles.
    pub fn volume(&self) -> f64 {
        self.faces
            .iter()
            .map(|f| {
                let [a, b, c] = f.map(|i| self.vertices[i]);
                (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
            })
            .sum()
    }

    /// One closed, consistently wound, positive volume in one piece; the Python preparers
    /// refuse any other.
    pub fn check_closed_single_body(&self, name: &str) -> Result<()> {
        let mut directed: HashMap<(usize, usize), usize> = HashMap::new();
        for f in &self.faces {
            for k in 0..3 {
                *directed.entry((f[k], f[(k + 1) % 3])).or_default() += 1;
            }
        }
        for (&(a, b), &count) in &directed {
            if count != 1 || directed.get(&(b, a)) != Some(&1) {
                bail!("{name} is not one closed, oriented volume");
            }
        }
        if self.volume() <= 0.0 {
            bail!("{name} is not one closed, oriented volume");
        }
        if self.body_count() != 1 {
            bail!("{name} is not one closed, oriented volume");
        }
        Ok(())
    }

    /// Pieces joined through shared edges.
    pub fn body_count(&self) -> usize {
        let mut parent: Vec<usize> = (0..self.faces.len()).collect();
        fn root(parent: &mut [usize], mut i: usize) -> usize {
            while parent[i] != i {
                parent[i] = parent[parent[i]];
                i = parent[i];
            }
            i
        }
        let mut by_edge: HashMap<(usize, usize), usize> = HashMap::new();
        for (fi, f) in self.faces.iter().enumerate() {
            for k in 0..3 {
                let (a, b) = (f[k], f[(k + 1) % 3]);
                let key = (a.min(b), a.max(b));
                if let Some(&other) = by_edge.get(&key) {
                    let (ra, rb) = (root(&mut parent, fi), root(&mut parent, other));
                    parent[ra] = rb;
                } else {
                    by_edge.insert(key, fi);
                }
            }
        }
        (0..self.faces.len()).filter(|&i| root(&mut parent, i) == i).count()
    }
}

pub fn bounds(points: &[[f64; 3]]) -> ([f64; 3], [f64; 3]) {
    let mut low = [f64::INFINITY; 3];
    let mut high = [f64::NEG_INFINITY; 3];
    for p in points {
        for i in 0..3 {
            low[i] = low[i].min(p[i]);
            high[i] = high[i].max(p[i]);
        }
    }
    (low, high)
}

/// Every triangle's three corners in file order, binary or ASCII.
fn stl_corners(bytes: &[u8]) -> Result<Vec<[f64; 3]>> {
    if bytes.len() >= 84 {
        let count = u32::from_le_bytes([bytes[80], bytes[81], bytes[82], bytes[83]]) as usize;
        if bytes.len() == 84 + count * 50 {
            let mut corners = Vec::with_capacity(count * 3);
            for t in 0..count {
                let base = 84 + t * 50 + 12;
                for c in 0..3 {
                    let at = base + c * 12;
                    let f = |o: usize| f32::from_le_bytes([bytes[at + o], bytes[at + o + 1], bytes[at + o + 2], bytes[at + o + 3]]) as f64;
                    corners.push([f(0), f(4), f(8)]);
                }
            }
            return Ok(corners);
        }
    }
    let text = std::str::from_utf8(bytes).context("an STL that is neither binary nor text")?;
    let mut corners = Vec::new();
    for line in text.lines() {
        let mut words = line.split_whitespace();
        if words.next() == Some("vertex") {
            let v: Vec<f64> = words.map(|w| w.parse()).collect::<Result<_, _>>()?;
            if v.len() != 3 {
                bail!("a vertex line without three numbers");
            }
            corners.push([v[0], v[1], v[2]]);
        }
    }
    if corners.len() % 3 != 0 || corners.is_empty() {
        bail!("an STL whose corners do not make whole triangles");
    }
    Ok(corners)
}
