//! Rolling balls against the original analytic faces, then ruled tools between their contacts.
//! The stations, contact-patch allowance and thinning are meshcad's `fillet._rolled` rule.
use super::{Blend, Link, lies_on_lines, section, tool};
use crate::boolean::{Op, boolean};
use crate::build::Part;
use crate::edge::{Edge, Edges, Graph, graph};
use crate::face::{Face, Src, Surface};
use crate::math::{TAU, V3, acos, cos, sin, tan, v2};
use crate::rule::{ANGULAR, LINEAR, plane_frame, ring_count};
use crate::solid::{Solid, point_triangle};
use crate::triangulate::triangulate;
use anyhow::{Context, Result, ensure};

const REACH: f64 = 0.02;

#[derive(Clone, Copy)]
struct Patch {
    face: u32,
    surface: Surface,
    sign: f64,
}

impl Patch {
    fn new(s: &Solid, g: &Graph, face: u32, near: V3) -> Option<Patch> {
        let surface = s.faces[g.faces.record[face as usize] as usize].surface;
        if !surface.is_analytic() {
            return None;
        }
        let &t = g.faces.tris[face as usize].iter().min_by(|&&a, &&b| {
            let center = |i: u32| {
                let [a, b, c] = s.tris[i as usize].map(|v| s.verts[v as usize]);
                (a + b + c) / 3.0
            };
            (center(a) - near)
                .norm()
                .total_cmp(&(center(b) - near).norm())
        })?;
        let [a, b, c] = s.tris[t as usize].map(|i| s.verts[i as usize]);
        let normal = surface.normal_at((a + b + c) / 3.0)?;
        Some(Patch {
            face,
            surface,
            sign: if normal.dot((b - a).cross(c - a)) > 0.0 {
                1.0
            } else {
                -1.0
            },
        })
    }

    fn distance(self, p: V3) -> f64 {
        self.sign * self.surface.distance(p).unwrap()
    }
    fn normal(self, p: V3) -> V3 {
        self.surface.normal_at(p).unwrap() * self.sign
    }
    fn foot(self, p: V3) -> V3 {
        p - self.surface.normal_at(p).unwrap() * self.surface.distance(p).unwrap()
    }

    fn holds(self, s: &Solid, g: &Graph, p: V3) -> bool {
        g.faces.tris[self.face as usize].iter().any(|&t| {
            let [a, b, c] = s.tris[t as usize].map(|i| s.verts[i as usize]);
            point_triangle(p, a, b, c) <= 2.0 * LINEAR + 1e-6
        })
    }

    fn sagitta(self, d: f64) -> f64 {
        let r = match self.surface {
            Surface::Plane { .. } => return REACH,
            Surface::Cylinder { r, .. } | Surface::Cone { r, .. } | Surface::Sphere { r, .. } => r,
            Surface::Torus { minor, .. } => minor,
            Surface::Free { .. } => unreachable!(),
        };
        if d >= r {
            r + REACH
        } else {
            d * d / (2.0 * r) + REACH
        }
    }
}

/// The ball constrained to the plane across the edge at `e`; three scalar equations.
fn ball(a: Patch, b: Patch, e: V3, t: V3, target: f64) -> Option<V3> {
    let (na, nb) = (a.normal(e), b.normal(e));
    let dot = na.dot(nb);
    if 1.0 + dot < 1e-9 {
        return None;
    }
    let mut c = e + (na + nb) * (target / (1.0 + dot));
    for _ in 0..40 {
        let f = [
            a.distance(c) - target,
            b.distance(c) - target,
            (c - e).dot(t),
        ];
        if f.iter().all(|x| x.abs() < 1e-11) {
            return Some(c);
        }
        let (u, v) = (a.normal(c), b.normal(c));
        let det = u.dot(v.cross(t));
        if det.abs() < 1e-15 {
            return None;
        }
        c -= (v.cross(t) * f[0] + t.cross(u) * f[1] + u.cross(v) * f[2]) / det;
    }
    None
}

fn neighbours(g: &Graph, face: u32) -> Vec<u32> {
    let mut out = vec![];
    for edge in &g.edges {
        if edge.faces.contains(&face) {
            for &other in &edge.faces {
                if other != face && !out.contains(&other) {
                    out.push(other);
                }
            }
        }
    }
    out
}

fn poly_normal(points: &[V3]) -> V3 {
    let center = points.iter().copied().fold(V3::ZERO, |a, b| a + b) / points.len() as f64;
    (0..points.len())
        .map(|i| (points[i] - center).cross(points[(i + 1) % points.len()] - center))
        .fold(V3::ZERO, |a, b| a + b)
        .unit()
}

struct Station {
    c: V3,
    u: V3,
    v: V3,
    phi: f64,
    t: V3,
}

fn thin(sections: &[Vec<V3>], normals: &[(V3, V3)]) -> Vec<Vec<V3>> {
    let mut kept = vec![0];
    let mut i = 0;
    while i + 1 < sections.len() {
        let mut j = i + 1;
        while j + 1 < sections.len() {
            let candidate = j + 1;
            let mut ok = true;
            for q in i + 1..candidate {
                for k in 0..sections[i].len() {
                    let ab = sections[candidate][k] - sections[i][k];
                    let ap = sections[q][k] - sections[i][k];
                    let t = (ap.dot(ab) / ab.dot(ab).max(1e-30)).clamp(0.0, 1.0);
                    if (ap - ab * t).norm() > LINEAR {
                        ok = false;
                        break;
                    }
                }
                if !ok {
                    break;
                }
            }
            if ok {
                for (a, b) in [
                    (normals[i].0, normals[candidate].0),
                    (normals[i].1, normals[candidate].1),
                ] {
                    if acos(a.dot(b).clamp(-1.0, 1.0)) > ANGULAR {
                        ok = false;
                    }
                }
            }
            if !ok {
                break;
            }
            j = candidate;
        }
        kept.push(j);
        i = j;
    }
    kept.into_iter().map(|i| sections[i].clone()).collect()
}

/// Corresponding polygon sections, with the same two triangles per ruled quad as meshcad.
fn ruled(sections: &[Vec<V3>], arc_segments: usize, src: Src) -> Result<Solid> {
    let m = sections[0].len();
    let verts: Vec<V3> = sections.iter().flatten().copied().collect();
    let mut tris = vec![];
    let mut fids = vec![];
    let mut faces = vec![Face::new(Surface::Free { kind: "BSPLINE" }, "fillet", src); 2];
    for i in 0..sections.len() - 1 {
        let (a, b) = (i * m, (i + 1) * m);
        for k in 0..m {
            let next = (k + 1) % m;
            tris.extend([
                [
                    a as u32 + k as u32,
                    a as u32 + next as u32,
                    b as u32 + next as u32,
                ],
                [
                    a as u32 + k as u32,
                    b as u32 + next as u32,
                    b as u32 + k as u32,
                ],
            ]);
            let f = u32::from(1 <= k && k <= arc_segments);
            fids.extend([f, f]);
        }
    }
    let mean = |p: &[V3]| p.iter().copied().fold(V3::ZERO, |a, b| a + b) / p.len() as f64;
    let along = mean(sections.last().unwrap()) - mean(&sections[0]);
    if poly_normal(&sections[0]).dot(along) < 0.0 {
        for t in &mut tris {
            t.swap(1, 2);
        }
    }
    for (i, start) in [(0, true), (sections.len() - 1, false)] {
        let section = &sections[i];
        let n = poly_normal(section);
        let (_, x, y) = plane_frame(n);
        let points = section.iter().map(|&p| v2(p.dot(x), p.dot(y))).collect();
        let mut cap = triangulate(&[points])?;
        let flip = (n.dot(along) > 0.0) == start;
        if flip {
            for t in &mut cap {
                t.swap(1, 2);
            }
        }
        let f = faces.len() as u32;
        faces.push(Face::new(
            Surface::Plane {
                p: section[0],
                n: if flip { -n } else { n },
            },
            "fillet",
            src,
        ));
        for t in cap {
            tris.push(t.map(|k| k + (i * m) as u32));
            fids.push(f);
        }
    }
    let solid = Part {
        verts,
        tris,
        fids,
        faces,
    }
    .solid();
    solid.check()?;
    Ok(solid)
}

fn rolled(s: &Solid, g: &Graph, edge: &Edge, r: f64, src: Src) -> Result<Option<(Solid, bool)>> {
    ensure!(
        !edge.closed,
        "a rolling-ball round along a closed curved edge"
    );
    let mut cumulative = vec![0.0];
    for p in edge.pts.windows(2) {
        cumulative.push(cumulative.last().unwrap() + (p[1] - p[0]).norm());
    }
    let length = *cumulative.last().unwrap();
    let step = 0.2f64.min((8.0 * LINEAR * r).sqrt() / 2.0);
    let count = ((length / step).ceil() as usize + 1).max(3);
    let mut points = Vec::with_capacity(count);
    let mut k = 0;
    for i in 0..count {
        let at = length * i as f64 / (count - 1) as f64;
        while k + 2 < cumulative.len() && cumulative[k + 1] < at {
            k += 1;
        }
        let t = (at - cumulative[k]) / (cumulative[k + 1] - cumulative[k]);
        points.push(edge.pts[k].lerp(edge.pts[k + 1], t));
    }
    let tangents: Vec<V3> = (0..count)
        .map(|i| {
            {
                if i == 0 {
                    points[1] - points[0]
                } else if i + 1 == count {
                    points[i] - points[i - 1]
                } else {
                    points[i + 1] - points[i - 1]
                }
            }
            .unit()
        })
        .collect();
    let mid = points[count / 2];
    let a = Patch::new(s, g, edge.faces[0], mid)
        .with_context(|| format!("a rolling-ball round needs an analytic face on {edge}"))?;
    let b = Patch::new(s, g, edge.faces[1], mid)
        .with_context(|| format!("a rolling-ball round needs an analytic face on {edge}"))?;
    let edge_index = g.find(edge)?;
    let sec = section(
        s,
        g,
        Link {
            edge: edge_index,
            forward: true,
        },
        mid,
        tangents[count / 2],
    )?;
    let convex = sec.convex;
    let target = if convex { -r } else { r };
    let least = (8.0 * 0.25 * LINEAR / r).sqrt();
    let mut patches: Vec<Option<Patch>> = vec![None; g.faces.tris.len()];
    patches[a.face as usize] = Some(a);
    patches[b.face as usize] = Some(b);
    let mut current = (a, b);
    let mut last = None;
    let solve = |a: Patch, b: Patch, e: V3, t: V3| -> Option<(V3, V3, V3)> {
        let c = ball(a, b, e, t, target)?;
        if (c - e).norm() > 3.0 * r {
            return None;
        }
        let (ca, cb) = (a.foot(c), b.foot(c));
        (a.holds(s, g, ca) && b.holds(s, g, cb)).then_some((c, ca, cb))
    };
    let mut stations = vec![];
    for (&e, &t) in points.iter().zip(&tangents) {
        if acos(a.normal(e).dot(b.normal(e)).clamp(-1.0, 1.0)) < least {
            continue;
        }
        let mut got = solve(current.0, current.1, e, t);
        if got.is_none() {
            let mut candidates = |face: Patch, original: Patch| {
                let mut ids = vec![face.face];
                if original.face != face.face {
                    ids.push(original.face);
                }
                for f in neighbours(g, face.face) {
                    if !ids.contains(&f) {
                        ids.push(f);
                    }
                }
                ids.into_iter()
                    .filter_map(|i| {
                        if patches[i as usize].is_none() {
                            patches[i as usize] = Patch::new(s, g, i, e);
                        }
                        patches[i as usize]
                    })
                    .collect::<Vec<_>>()
            };
            let aa = candidates(current.0, a);
            let bb = candidates(current.1, b);
            let near = last.unwrap_or(e);
            let mut best = None;
            let mut distance = f64::INFINITY;
            for ca in &aa {
                for cb in &bb {
                    if ca.face == cb.face {
                        continue;
                    }
                    if let Some(value) = solve(*ca, *cb, e, t) {
                        let d = (value.0 - near).norm();
                        if d < distance {
                            distance = d;
                            best = Some(((*ca, *cb), value));
                        }
                    }
                }
            }
            let Some((pair, value)) = best else {
                continue;
            };
            current = pair;
            got = Some(value);
        }
        let (c, ca, cb) = got.unwrap();
        last = Some(c);
        let (u, v) = ((ca - c) / r, (cb - c) / r);
        let phi = acos(u.dot(v).clamp(-1.0, 1.0));
        if phi >= least {
            stations.push(Station { c, u, v, phi, t });
        }
    }
    if stations.len() < 2 {
        return Ok(None);
    }
    let phi = stations.iter().map(|s| s.phi).fold(0.0, f64::max);
    let arc_segments = ((phi / (TAU / ring_count(r) as f64)).ceil() as usize).max(2);
    let span = r * tan(phi / 2.0);
    let reach = REACH
        + patches
            .iter()
            .flatten()
            .map(|p| p.sagitta(span))
            .fold(0.0, f64::max);
    let mut sections: Vec<Vec<V3>> = vec![];
    let mut normals = vec![];
    for Station { c, u, v, phi, t } in stations {
        let w = (v - u * u.dot(v)).unit();
        let arc: Vec<V3> = (0..=arc_segments)
            .map(|i| {
                let a = phi * i as f64 / arc_segments as f64;
                c + (u * cos(a) + w * sin(a)) * r
            })
            .collect();
        let far = c + (u + v).unit() * ((r + reach) / cos(phi / 2.0));
        let mut sec = vec![arc[0] + u * reach];
        sec.extend_from_slice(&arc);
        sec.extend([arc[arc_segments] + v * reach, far]);
        if let Some(previous) = sections.last() {
            if sec
                .iter()
                .zip(previous)
                .any(|(&p, &q)| (p - q).dot(t) <= 0.0)
                || poly_normal(&sec).dot(t) * poly_normal(previous).dot(t) <= 0.0
            {
                continue;
            }
        }
        sections.push(sec);
        normals.push((u, v));
    }
    if sections.len() < 2 {
        return Ok(None);
    }
    let mut sections = thin(&sections, &normals);
    let shift = |sec: &Vec<V3>, next: &Vec<V3>| {
        let mean = |s: &[V3]| s.iter().copied().fold(V3::ZERO, |a, b| a + b) / s.len() as f64;
        let d = (mean(&sec[1..sec.len() - 3]) - mean(&next[1..next.len() - 3])).unit() * 0.002;
        sec.iter().map(|&p| p + d).collect::<Vec<_>>()
    };
    let start = shift(&sections[0], &sections[1]);
    let end = shift(sections.last().unwrap(), &sections[sections.len() - 2]);
    sections.insert(0, start);
    sections.push(end);
    Ok(Some((ruled(&sections, arc_segments, src)?, convex)))
}

pub(super) fn blend(s: &Solid, edges: &Edges, r: f64, src: Src) -> Result<Solid> {
    ensure!(!edges.is_empty(), "a rolling-ball round along no edge");
    let g = graph(s);
    let mut cuts = vec![];
    let mut fills = vec![];
    for edge in edges.iter() {
        let index = g.find(edge)?;
        let value = if lies_on_lines(s, &g, index).is_ok() {
            let link = Link {
                edge: index,
                forward: true,
            };
            let (o, t) = link.middle(&g, s);
            let convex = section(s, &g, link, o, t)?.convex;
            Some((
                tool(s, &g, link, edge.closed, [0.0, 0.0], Blend::Round(r), src)?,
                convex,
            ))
        } else {
            rolled(s, &g, edge, r, src)?
        };
        if let Some((tool, convex)) = value {
            if convex {
                cuts.push(tool);
            } else {
                fills.push(tool);
            }
        }
    }
    let mut out = s.clone();
    if !cuts.is_empty() {
        let operands: Vec<&Solid> = std::iter::once(s).chain(cuts.iter()).collect();
        out = boolean(&operands, Op::Cut, src)?;
    }
    if !fills.is_empty() {
        let operands: Vec<&Solid> = std::iter::once(&out).chain(fills.iter()).collect();
        out = boolean(&operands, Op::Union, src)?;
    }
    for f in &mut out.faces {
        if f.op == "fillet" && f.src == src && f.via.is_some_and(|v| v.src == src) {
            f.via = None;
        }
    }
    Ok(out)
}
