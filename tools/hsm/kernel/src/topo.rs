//! The faces a reader sees: connected runs of triangles on one surface. Triangles from different
//! builders and booleans that lie on the same plane or cylinder and touch are one face, as
//! OCCT's `clean()` leaves them. A face narrower than the rule resolves — a boolean leaves one
//! wherever two surfaces meet at a tangent the rule cut into different points — joins the
//! neighbour it shares the most boundary with.
use crate::face::SurfaceKey;
use crate::rule::LINEAR;
use crate::solid::Solid;
use std::collections::HashMap;

pub struct Faces {
    /// Per triangle, its face; faces are numbered in the order of their first triangle.
    pub of: Vec<u32>,
    /// Per face, the face record of its first triangle.
    pub record: Vec<u32>,
    /// Per face, its triangles in the solid's order.
    pub tris: Vec<Vec<u32>>,
}

#[derive(Clone, PartialEq, Eq, Hash)]
enum Key {
    /// The surface, and for a plane which way it faces.
    Surface(SurfaceKey, bool),
    Own(u32),
}

/// Pairs of triangles that share an edge, and the edge's length.
fn neighbours(s: &Solid) -> Vec<(u32, u32, f64)> {
    let mut half: Vec<(u32, u32, u32)> = Vec::with_capacity(3 * s.tris.len());
    for (i, t) in s.tris.iter().enumerate() {
        for k in 0..3 {
            let (a, b) = (t[k], t[(k + 1) % 3]);
            half.push((a.min(b), a.max(b), i as u32));
        }
    }
    half.sort_unstable();
    let mut out = vec![];
    let mut i = 0;
    while i < half.len() {
        let mut j = i + 1;
        while j < half.len() && (half[j].0, half[j].1) == (half[i].0, half[i].1) {
            j += 1;
        }
        let len = (s.verts[half[i].1 as usize] - s.verts[half[i].0 as usize]).norm();
        for k in (i..j).step_by(2) {
            if k + 1 < j {
                out.push((half[k].2, half[k + 1].2, len));
            }
        }
        i = j;
    }
    out
}

fn find(p: &mut [u32], mut x: u32) -> u32 {
    while p[x as usize] != x {
        p[x as usize] = p[p[x as usize] as usize];
        x = p[x as usize];
    }
    x
}

/// Components of the triangles joined across edges whose sides carry one label, numbered in
/// the order of their first triangle.
fn joined(n: usize, pairs: &[(u32, u32, f64)], label: &[u32]) -> (Vec<u32>, usize) {
    let mut parent: Vec<u32> = (0..n as u32).collect();
    for &(a, b, _) in pairs {
        if label[a as usize] == label[b as usize] {
            let (ra, rb) = (find(&mut parent, a), find(&mut parent, b));
            if ra != rb {
                parent[ra.max(rb) as usize] = ra.min(rb);
            }
        }
    }
    let mut number = vec![u32::MAX; n];
    let mut count = 0u32;
    let comp = (0..n as u32)
        .map(|t| {
            let r = find(&mut parent, t) as usize;
            if number[r] == u32::MAX {
                number[r] = count;
                count += 1;
            }
            number[r]
        })
        .collect();
    (comp, count as usize)
}

pub fn faces(s: &Solid) -> Faces {
    let n = s.tris.len();
    let mut labels: HashMap<Key, u32> = HashMap::new();
    let face_label: Vec<u32> = s
        .faces
        .iter()
        .enumerate()
        .map(|(i, f)| {
            let key = f.surface.key().map(|k| Key::Surface(k, f.surface.sense())).unwrap_or(Key::Own(i as u32));
            let next = labels.len() as u32;
            *labels.entry(key).or_insert(next)
        })
        .collect();
    let mut label: Vec<u32> = s.face_of.iter().map(|&f| face_label[f as usize]).collect();
    let pairs = neighbours(s);
    let (mut comp, mut nf) = joined(n, &pairs, &label);
    if n > 0 {
        let mut area = vec![0.0; nf];
        for (t, &c) in s.tris.iter().zip(&comp) {
            let (a, b, cc) = (s.verts[t[0] as usize], s.verts[t[1] as usize], s.verts[t[2] as usize]);
            area[c as usize] += 0.5 * (b - a).cross(cc - a).norm();
        }
        let mut perim = vec![0.0; nf];
        let mut border: HashMap<(u32, u32), f64> = HashMap::new();
        for &(a, b, len) in &pairs {
            let (ca, cb) = (comp[a as usize], comp[b as usize]);
            if ca != cb {
                perim[ca as usize] += len;
                perim[cb as usize] += len;
                *border.entry((ca, cb)).or_default() += len;
                *border.entry((cb, ca)).or_default() += len;
            }
        }
        let thin: Vec<bool> = (0..nf).map(|f| perim[f] > 0.0 && 2.0 * area[f] < LINEAR * perim[f]).collect();
        if thin.iter().any(|&t| t) {
            let mut into: HashMap<u32, (u32, f64)> = HashMap::new();
            let mut keys: Vec<(&(u32, u32), &f64)> = border.iter().collect();
            keys.sort_by(|a, b| a.0.cmp(b.0));
            for (&(f, g), &len) in keys {
                if !thin[f as usize] {
                    continue;
                }
                let w = if thin[g as usize] { len * 1e-6 } else { len };
                let e = into.entry(f).or_insert((g, w));
                if w > e.1 {
                    *e = (g, w);
                }
            }
            let mut comp_label = vec![0u32; nf];
            for (t, &c) in comp.iter().enumerate() {
                comp_label[c as usize] = label[t];
            }
            let mut merged = comp_label.clone();
            for (&f, &(g0, _)) in &into {
                let mut g = g0;
                let mut seen = vec![f];
                while let Some(&(h, _)) = into.get(&g) {
                    if seen.contains(&g) {
                        break;
                    }
                    seen.push(g);
                    g = h;
                }
                merged[f as usize] = comp_label[g as usize];
            }
            label = comp.iter().map(|&c| merged[c as usize]).collect();
            (comp, nf) = joined(n, &pairs, &label);
        }
    }
    let mut record = vec![u32::MAX; nf];
    let mut tris = vec![vec![]; nf];
    for (t, &c) in comp.iter().enumerate() {
        if record[c as usize] == u32::MAX {
            record[c as usize] = s.face_of[t];
        }
        tris[c as usize].push(t as u32);
    }
    Faces { of: comp, record, tris }
}
