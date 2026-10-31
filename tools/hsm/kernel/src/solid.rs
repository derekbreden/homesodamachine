//! A solid: triangles that close a volume, each naming the face record it lies on.
//!
//! The mesh is canonical. Triangles run face by face, in the order of the face table; within a
//! face they are sorted by their corners' coordinates, each triangle starting at its least
//! corner; vertices are numbered by first use. Two solids with the same triangles on the same
//! faces are the same arrays, whatever order a builder or a boolean produced them in.
use crate::face::Face;
use crate::mass::{self, Mass};
use crate::math::{Affine, V3};
use crate::plane::Plane;
use crate::rule::snap3;
use anyhow::{Result, bail};
use std::cmp::Ordering;
use std::collections::HashMap;
use std::fmt;

#[derive(Clone)]
pub struct Solid {
    pub(crate) verts: Vec<V3>,
    pub(crate) tris: Vec<[u32; 3]>,
    pub(crate) face_of: Vec<u32>,
    pub(crate) faces: Vec<Face>,
    #[cfg(feature = "manifold")]
    pub(crate) built: std::sync::OnceLock<Result<crate::boolean::Built, String>>,
}

/// An axis-aligned box.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Bounds {
    pub min: V3,
    pub max: V3,
}

impl Bounds {
    pub fn size(&self) -> V3 {
        self.max - self.min
    }
    pub fn center(&self) -> V3 {
        (self.min + self.max) * 0.5
    }
    pub fn diagonal(&self) -> f64 {
        self.size().norm()
    }
}

impl fmt::Debug for Solid {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Solid({} vertices, {} triangles, {} faces)",
            self.verts.len(),
            self.tris.len(),
            self.faces.len()
        )
    }
}

impl Solid {
    pub fn empty() -> Solid {
        Solid::raw(vec![], vec![], vec![], vec![])
    }

    pub(crate) fn raw(verts: Vec<V3>, tris: Vec<[u32; 3]>, face_of: Vec<u32>, faces: Vec<Face>) -> Solid {
        Solid {
            verts,
            tris,
            face_of,
            faces,
            #[cfg(feature = "manifold")]
            built: std::sync::OnceLock::new(),
        }
    }

    /// A builder's triangles as a solid: every vertex on the rule's grid, wound so the volume is
    /// positive, put in canonical order.
    pub(crate) fn built(verts: Vec<V3>, tris: Vec<[u32; 3]>, face_of: Vec<u32>, faces: Vec<Face>) -> Solid {
        let verts: Vec<V3> = verts.into_iter().map(snap3).collect();
        let mut tris = tris;
        if mass::signed_volume(&verts, &tris) < 0.0 {
            for t in &mut tris {
                t.swap(1, 2);
            }
        }
        canonical(&verts, &tris, &face_of, &faces)
    }

    pub fn is_empty(&self) -> bool {
        self.tris.is_empty()
    }

    pub fn verts(&self) -> &[V3] {
        &self.verts
    }

    pub fn tris(&self) -> &[[u32; 3]] {
        &self.tris
    }

    /// The face record index of each triangle.
    pub fn face_of(&self) -> &[u32] {
        &self.face_of
    }

    pub fn faces(&self) -> &[Face] {
        &self.faces
    }

    /// The face record triangle `t` lies on.
    pub fn face_at(&self, t: usize) -> &Face {
        &self.faces[self.face_of[t] as usize]
    }

    /// The face record of the triangle nearest `p`, and how far `p` is from it.
    pub fn face_near(&self, p: V3) -> Option<(&Face, f64)> {
        let mut best: Option<(usize, f64)> = None;
        for (i, t) in self.tris.iter().enumerate() {
            let d = point_triangle(p, self.verts[t[0] as usize], self.verts[t[1] as usize], self.verts[t[2] as usize]);
            if best.is_none_or(|(_, b)| d < b) {
                best = Some((i, d));
            }
        }
        best.map(|(i, d)| (self.face_at(i), d))
    }

    pub fn bounds(&self) -> Bounds {
        let mut lo = V3::from([f64::INFINITY; 3]);
        let mut hi = V3::from([f64::NEG_INFINITY; 3]);
        for t in &self.tris {
            for &v in t {
                let p = self.verts[v as usize];
                lo = lo.min(p);
                hi = hi.max(p);
            }
        }
        Bounds { min: lo, max: hi }
    }

    pub fn mass(&self) -> Mass {
        mass::of(&self.verts, &self.tris)
    }

    pub fn volume(&self) -> f64 {
        self.mass().volume
    }

    pub fn area(&self) -> f64 {
        mass::area(&self.verts, &self.tris)
    }

    pub fn centroid(&self) -> V3 {
        self.mass().centroid
    }

    /// Moved by `t`, which may scale uniformly and mirror. Face records move with it.
    pub fn transformed(&self, t: &Affine) -> Solid {
        let verts = self.verts.iter().map(|&p| t.point(p)).collect();
        let tris = if t.det() < 0.0 {
            self.tris.iter().map(|&[a, b, c]| [a, c, b]).collect()
        } else {
            self.tris.clone()
        };
        let faces = self.faces.iter().map(|f| f.transformed(t)).collect();
        Solid::raw(verts, tris, self.face_of.clone(), faces)
    }

    pub fn translate(&self, d: V3) -> Solid {
        self.transformed(&Affine::translation(d))
    }

    /// Turned `degrees` counterclockwise about the axis through `p` along `axis`.
    pub fn rotate(&self, p: V3, axis: V3, degrees: f64) -> Solid {
        self.transformed(&Affine::rotation(p, axis, degrees))
    }

    /// Reflected through the plane through `p` with normal `n`.
    pub fn mirror(&self, p: V3, n: V3) -> Solid {
        self.transformed(&Affine::mirror(p, n))
    }

    /// Scaled by `s` about the origin.
    pub fn scale(&self, s: f64) -> Solid {
        self.transformed(&Affine::scale(s))
    }

    /// Carried from `from`'s frame to `to`'s.
    pub fn placed(&self, from: &Plane, to: &Plane) -> Solid {
        let back = from.to_world();
        let inv = invert(&back);
        self.transformed(&to.to_world().then_after(&inv))
    }

    /// Whether every edge is shared by exactly two triangles walking it in opposite directions,
    /// and the volume is positive.
    pub fn check(&self) -> Result<()> {
        let mut edges: HashMap<(u32, u32), i32> = HashMap::new();
        for t in &self.tris {
            for k in 0..3 {
                let (a, b) = (t[k], t[(k + 1) % 3]);
                if a == b {
                    bail!("a triangle repeats a vertex");
                }
                *edges.entry((a, b)).or_default() += 1;
            }
        }
        for (&(a, b), &n) in &edges {
            if n != 1 || edges.get(&(b, a)) != Some(&1) {
                let p = self.verts[a as usize];
                bail!("the surface is open or folded at ({:.4}, {:.4}, {:.4})", p.x, p.y, p.z);
            }
        }
        if !self.is_empty() && self.volume() <= 0.0 {
            bail!("the solid is inside out");
        }
        Ok(())
    }

    /// The solids apart, each with the voids inside it.
    pub fn components(&self) -> Vec<Solid> {
        let n = self.verts.len();
        let mut parent: Vec<u32> = (0..n as u32).collect();
        fn find(p: &mut [u32], mut x: u32) -> u32 {
            while p[x as usize] != x {
                p[x as usize] = p[p[x as usize] as usize];
                x = p[x as usize];
            }
            x
        }
        for t in &self.tris {
            for k in 1..3 {
                let (a, b) = (find(&mut parent, t[0]), find(&mut parent, t[k]));
                if a != b {
                    parent[a.max(b) as usize] = a.min(b);
                }
            }
        }
        let mut label: HashMap<u32, usize> = HashMap::new();
        let mut groups: Vec<Vec<usize>> = vec![];
        for (i, t) in self.tris.iter().enumerate() {
            let r = find(&mut parent, t[0]);
            let g = *label.entry(r).or_insert_with(|| {
                groups.push(vec![]);
                groups.len() - 1
            });
            groups[g].push(i);
        }
        if groups.len() <= 1 {
            return if self.is_empty() { vec![] } else { vec![self.clone()] };
        }
        let parts: Vec<Solid> = groups.iter().map(|g| self.subset(g)).collect();
        let vols: Vec<f64> = parts.iter().map(|s| mass::signed_volume(&s.verts, &s.tris)).collect();
        let boxes: Vec<Bounds> = parts.iter().map(Solid::bounds).collect();
        let solids: Vec<usize> = (0..parts.len()).filter(|&i| vols[i] > 0.0).collect();
        let mut held: Vec<Vec<usize>> = solids.iter().map(|&i| vec![i]).collect();
        for v in (0..parts.len()).filter(|&i| vols[i] <= 0.0) {
            let b = boxes[v];
            let around = solids
                .iter()
                .enumerate()
                .filter(|&(_, &s)| {
                    let o = boxes[s];
                    o.min.x <= b.min.x && o.min.y <= b.min.y && o.min.z <= b.min.z
                        && o.max.x >= b.max.x && o.max.y >= b.max.y && o.max.z >= b.max.z
                })
                .min_by(|a, b| {
                    let (sa, sb) = (boxes[*a.1].size(), boxes[*b.1].size());
                    (sa.x * sa.y * sa.z).total_cmp(&(sb.x * sb.y * sb.z))
                });
            if let Some((k, _)) = around {
                held[k].push(v);
            }
        }
        held.iter()
            .map(|g| {
                let tris: Vec<usize> = g.iter().flat_map(|&p| groups[p].iter().copied()).collect();
                self.subset(&tris)
            })
            .collect()
    }

    /// Disjoint solids as one, with no boolean between them.
    pub fn compose(solids: &[Solid]) -> Solid {
        let mut verts = vec![];
        let mut tris = vec![];
        let mut face_of = vec![];
        let mut faces = vec![];
        for s in solids {
            let (vb, fb) = (verts.len() as u32, faces.len() as u32);
            verts.extend_from_slice(&s.verts);
            tris.extend(s.tris.iter().map(|t| [t[0] + vb, t[1] + vb, t[2] + vb]));
            face_of.extend(s.face_of.iter().map(|f| f + fb));
            faces.extend_from_slice(&s.faces);
        }
        canonical(&verts, &tris, &face_of, &faces)
    }

    /// The triangles `keep` of this solid, as a solid of their own.
    pub(crate) fn subset(&self, keep: &[usize]) -> Solid {
        let tris: Vec<[u32; 3]> = keep.iter().map(|&i| self.tris[i]).collect();
        let face_of: Vec<u32> = keep.iter().map(|&i| self.face_of[i]).collect();
        canonical(&self.verts, &tris, &face_of, &self.faces)
    }
}

fn invert(a: &Affine) -> Affine {
    let m = &a.m;
    let det = a.det();
    let inv = |r: usize, c: usize| -> f64 {
        let (r0, r1) = ((c + 1) % 3, (c + 2) % 3);
        let (c0, c1) = ((r + 1) % 3, (r + 2) % 3);
        (m[r0][c0] * m[r1][c1] - m[r0][c1] * m[r1][c0]) / det
    };
    let mut out = Affine::IDENTITY;
    for r in 0..3 {
        for c in 0..3 {
            out.m[r][c] = inv(r, c);
        }
    }
    let t = V3::from([m[0][3], m[1][3], m[2][3]]);
    let ti = out.vector(t);
    out.m[0][3] = -ti.x;
    out.m[1][3] = -ti.y;
    out.m[2][3] = -ti.z;
    out
}

fn cmp3(a: V3, b: V3) -> Ordering {
    a.x.total_cmp(&b.x).then(a.y.total_cmp(&b.y)).then(a.z.total_cmp(&b.z))
}

/// The canonical solid on the triangles `tris` of `verts`: faces with no triangle dropped and the
/// rest renumbered in table order, triangles sorted, vertices numbered by first use.
pub(crate) fn canonical(verts: &[V3], tris: &[[u32; 3]], face_of: &[u32], faces: &[Face]) -> Solid {
    let mut keyed: Vec<(u32, [u32; 3])> = tris
        .iter()
        .zip(face_of)
        .map(|(t, &f)| {
            let p = |k: usize| verts[t[k] as usize];
            let mut r = 0;
            for k in 1..3 {
                if cmp3(p(k), p(r)) == Ordering::Less {
                    r = k;
                }
            }
            (f, [t[r], t[(r + 1) % 3], t[(r + 2) % 3]])
        })
        .collect();
    keyed.sort_by(|(fa, ta), (fb, tb)| {
        fa.cmp(fb).then_with(|| {
            (0..3)
                .map(|k| cmp3(verts[ta[k] as usize], verts[tb[k] as usize]))
                .find(|o| *o != Ordering::Equal)
                .unwrap_or(Ordering::Equal)
        })
    });
    let mut face_new = vec![u32::MAX; faces.len()];
    let mut out_faces = vec![];
    let mut vert_new = vec![u32::MAX; verts.len()];
    let mut out_verts = vec![];
    let mut out_tris = Vec::with_capacity(keyed.len());
    let mut out_face_of = Vec::with_capacity(keyed.len());
    for (f, t) in keyed {
        if face_new[f as usize] == u32::MAX {
            face_new[f as usize] = out_faces.len() as u32;
            out_faces.push(faces[f as usize]);
        }
        let mut nt = [0u32; 3];
        for k in 0..3 {
            let v = t[k] as usize;
            if vert_new[v] == u32::MAX {
                vert_new[v] = out_verts.len() as u32;
                out_verts.push(verts[v]);
            }
            nt[k] = vert_new[v];
        }
        out_tris.push(nt);
        out_face_of.push(face_new[f as usize]);
    }
    Solid::raw(out_verts, out_tris, out_face_of, out_faces)
}

/// The distance from `p` to the triangle `abc`.
pub(crate) fn point_triangle(p: V3, a: V3, b: V3, c: V3) -> f64 {
    let (ab, ac, ap) = (b - a, c - a, p - a);
    let (d1, d2) = (ab.dot(ap), ac.dot(ap));
    if d1 <= 0.0 && d2 <= 0.0 {
        return ap.norm();
    }
    let bp = p - b;
    let (d3, d4) = (ab.dot(bp), ac.dot(bp));
    if d3 >= 0.0 && d4 <= d3 {
        return bp.norm();
    }
    let vc = d1 * d4 - d3 * d2;
    if vc <= 0.0 && d1 >= 0.0 && d3 <= 0.0 {
        let v = d1 / (d1 - d3);
        return (p - (a + ab * v)).norm();
    }
    let cp = p - c;
    let (d5, d6) = (ab.dot(cp), ac.dot(cp));
    if d6 >= 0.0 && d5 <= d6 {
        return cp.norm();
    }
    let vb = d5 * d2 - d1 * d6;
    if vb <= 0.0 && d2 >= 0.0 && d6 <= 0.0 {
        let w = d2 / (d2 - d6);
        return (p - (a + ac * w)).norm();
    }
    let va = d3 * d6 - d5 * d4;
    if va <= 0.0 && (d4 - d3) >= 0.0 && (d5 - d6) >= 0.0 {
        let w = (d4 - d3) / ((d4 - d3) + (d5 - d6));
        return (p - (b + (c - b) * w)).norm();
    }
    let denom = 1.0 / (va + vb + vc);
    let (v, w) = (vb * denom, vc * denom);
    (p - (a + ab * v + ac * w)).norm()
}
