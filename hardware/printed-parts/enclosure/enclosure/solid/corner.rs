//! The retained analytic front corner, normalized to the live enclosure datums.
use crate::numbers::{CornerSurface, FrontCorners};
use anyhow::{ensure, Result};
use hsm_kernel::*;

fn vector(p: [f64; 3]) -> V3 {
    v3(p[0], p[1], p[2])
}

fn knots(surface: &CornerSurface, axis: usize) -> Result<Vec<f64>> {
    let k = &surface.knots[axis];
    let counts = &surface.multiplicities[axis];
    ensure!(k.len() == counts.len(), "corner knot multiplicities");
    let mut out = vec![];
    for (&k, &count) in k.iter().zip(counts) {
        out.extend(std::iter::repeat_n(k, count));
    }
    Ok(out)
}

fn basis(knots: &[f64], degree: usize, count: usize, t: f64) -> Vec<f64> {
    if t >= knots[count] {
        let mut out = vec![0.; count];
        out[count - 1] = 1.;
        return out;
    }
    let mut old: Vec<f64> = knots
        .windows(2)
        .map(|k| if k[0] <= t && t < k[1] { 1. } else { 0. })
        .collect();
    for p in 1..=degree {
        let mut next = vec![0.; old.len() - 1];
        for i in 0..next.len() {
            let a = knots[i + p] - knots[i];
            let b = knots[i + p + 1] - knots[i + 1];
            if a > 0. {
                next[i] += (t - knots[i]) / a * old[i];
            }
            if b > 0. {
                next[i] += (knots[i + p + 1] - t) / b * old[i + 1];
            }
        }
        old = next;
    }
    old.truncate(count);
    old
}

struct Patch {
    poles: Vec<Vec<V3>>,
    weights: Vec<Vec<f64>>,
    knots: [Vec<f64>; 2],
    degree: [usize; 2],
    seeds: Vec<(f64, f64, V3)>,
}

impl Patch {
    fn read(surface: &CornerSurface) -> Result<Self> {
        let poles: Vec<Vec<V3>> = surface
            .poles
            .iter()
            .map(|row| row.iter().map(|&p| vector(p)).collect())
            .collect();
        let weights = surface.weights.clone();
        let degree = surface.degree;
        ensure!(
            weights.len() == poles.len()
                && poles.iter().zip(&weights).all(|(p, w)| p.len() == w.len()),
            "pole weights"
        );
        let mut out = Self {
            poles,
            weights,
            knots: [knots(surface, 0)?, knots(surface, 1)?],
            degree,
            seeds: vec![],
        };
        for i in 0..=8 {
            for j in 0..=32 {
                let (u, v) = (i as f64 / 8., j as f64 / 32.);
                out.seeds.push((u, v, out.at(u, v)));
            }
        }
        Ok(out)
    }

    fn at(&self, u: f64, v: f64) -> V3 {
        let a = basis(&self.knots[0], self.degree[0], self.poles.len(), u);
        let b = basis(&self.knots[1], self.degree[1], self.poles[0].len(), v);
        let mut point = V3::ZERO;
        let mut weight = 0.;
        for (i, &a) in a.iter().enumerate() {
            for (j, &b) in b.iter().enumerate() {
                let c = a * b * self.weights[i][j];
                point += self.poles[i][j] * c;
                weight += c;
            }
        }
        point / weight
    }

    fn continuation(&self, point: V3, axis: V3, end: bool) -> Option<(f64, f64, f64)> {
        let v = if end { 1. } else { 0. };
        let residual = |u| {
            let r = point - self.at(u, v);
            r - axis * r.dot(axis)
        };
        let mut u = 0.;
        let mut best = f64::INFINITY;
        for k in 0..=16 {
            let a = k as f64 / 16.;
            let d = residual(a).dot(residual(a));
            if d < best {
                best = d;
                u = a;
            }
        }
        for _ in 0..32 {
            let (a, b) = ((u - 1e-5).max(0.), (u + 1e-5).min(1.));
            let d = (self.at(b, v) - self.at(a, v)) / (b - a);
            let d = d - axis * d.dot(axis);
            let step = residual(u).dot(d) / d.dot(d);
            let mut fraction = 1.;
            let mut advanced = false;
            for _ in 0..16 {
                let next = (u + fraction * step).clamp(0., 1.);
                let error = residual(next).dot(residual(next));
                if error < best {
                    u = next;
                    best = error;
                    advanced = true;
                    break;
                }
                fraction *= 0.5;
            }
            if !advanced || (fraction * step).abs() < 1e-12 {
                break;
            }
        }
        let t = (point - self.at(u, v)).dot(axis);
        if (end && t >= -1e-8) || (!end && t <= 1e-8) {
            Some((u, t, best.sqrt()))
        } else {
            None
        }
    }

    fn project(
        &self,
        point: V3,
        surfaces: &[Surface],
        origin: V3,
        sign: f64,
        scale: f64,
    ) -> (V3, f64, f64, f64, f64) {
        let world = |p: V3| origin + v3(sign * p.x, p.y, p.z) * scale;
        let objective = |q: V3| {
            (q - point).dot(q - point)
                + 1e8
                    * surfaces
                        .iter()
                        .map(|s| s.distance(q).unwrap().powi(2))
                        .sum::<f64>()
        };
        let mut u = 0.;
        let mut v = 0.;
        let mut best = f64::INFINITY;
        for &(a, b, p) in &self.seeds {
            let distance = objective(world(p));
            if distance < best {
                best = distance;
                u = a;
                v = b;
            }
        }
        for _ in 0..40 {
            let q = world(self.at(u, v));
            let (u0, u1) = ((u - 1e-5).max(0.), (u + 1e-5).min(1.));
            let (v0, v1) = ((v - 1e-5).max(0.), (v + 1e-5).min(1.));
            let du = (world(self.at(u1, v)) - world(self.at(u0, v))) / (u1 - u0);
            let dv = (world(self.at(u, v1)) - world(self.at(u, v0))) / (v1 - v0);
            let r = point - q;
            let (mut a, mut b, mut c) = (du.dot(du), du.dot(dv), dv.dot(dv));
            let (mut x, mut y) = (r.dot(du), r.dot(dv));
            for surface in surfaces {
                let normal = surface.normal_at(q).unwrap();
                let (gu, gv, g) = (normal.dot(du), normal.dot(dv), surface.distance(q).unwrap());
                a += 1e8 * gu * gu;
                b += 1e8 * gu * gv;
                c += 1e8 * gv * gv;
                x -= 1e8 * g * gu;
                y -= 1e8 * g * gv;
            }
            let det = a * c - b * b;
            if det.abs() < 1e-24 {
                break;
            }
            let step = ((x * c - y * b) / det, (y * a - x * b) / det);
            let mut fraction = 1.;
            let mut advanced = false;
            for _ in 0..18 {
                let (next_u, next_v) = (
                    (u + fraction * step.0).clamp(0., 1.),
                    (v + fraction * step.1).clamp(0., 1.),
                );
                let distance = objective(world(self.at(next_u, next_v)));
                if distance < best - 1e-22 {
                    u = next_u;
                    v = next_v;
                    best = distance;
                    advanced = true;
                    break;
                }
                fraction *= 0.5;
            }
            if !advanced || fraction * (step.0.abs() + step.1.abs()) < 1e-11 {
                break;
            }
        }
        let point = world(self.at(u, v));
        let error = surfaces
            .iter()
            .map(|s| s.distance(point).unwrap().abs())
            .fold(0_f64, f64::max);
        (point, best, u, v, error)
    }
}

fn in_corner(point: V3, frames: &[(V3, f64)], scale: f64) -> bool {
    frames.iter().any(|&(origin, sign)| {
        let q = point - origin;
        let q = v3(sign * q.x, q.y, q.z) / scale;
        (-0.03..=2.03).contains(&q.x)
            && (-2.03..=0.7).contains(&q.y)
            && (-0.03..=2.7).contains(&q.z)
    })
}

fn chart_at(patches: &[Patch], axis: V3, u: f64, v: f64) -> V3 {
    let inner = u.clamp(0., 1.);
    let p = if v <= 0. {
        patches[0].at(inner, 0.) + v3(v, 0., 0.)
    } else if v >= patches.len() as f64 {
        patches[patches.len() - 1].at(inner, 1.) + axis * (v - patches.len() as f64)
    } else {
        let k = v.floor() as usize;
        patches[k].at(inner, v - k as f64)
    };
    if u < 0. {
        p + v3(u, 0., 0.)
    } else if u > 1. {
        p - v3(0., 0., u - 1.)
    } else {
        p
    }
}

fn boundary_extension(
    patches: &[Patch],
    axis: V3,
    point: V3,
    lower: bool,
) -> Option<(f64, f64, f64)> {
    let u = if lower { 1. } else { 0. };
    let direction = if lower {
        v3(0., 0., -1.)
    } else {
        v3(1., 0., 0.)
    };
    let residual = |v| {
        let r = point - chart_at(patches, axis, u, v);
        r - direction * r.dot(direction)
    };
    let mut v = 0.;
    let mut best = f64::INFINITY;
    let end = patches.len() as f64;
    for k in 0..=64 {
        let q = end * k as f64 / 64.;
        let d = residual(q).dot(residual(q));
        if d < best {
            best = d;
            v = q;
        }
    }
    for q in [-1., end + 1.] {
        let d = residual(q).dot(residual(q));
        if d < best {
            best = d;
            v = q;
        }
    }
    for _ in 0..40 {
        let (a, b) = ((v - 1e-5).max(-1.), (v + 1e-5).min(end + 1.));
        let d = (chart_at(patches, axis, u, b) - chart_at(patches, axis, u, a)) / (b - a);
        let d = d - direction * d.dot(direction);
        if d.dot(d) < 1e-24 {
            break;
        }
        let step = residual(v).dot(d) / d.dot(d);
        let mut fraction = 1.;
        let mut advanced = false;
        for _ in 0..18 {
            let next = (v + fraction * step).clamp(-1., end + 1.);
            let e = residual(next).dot(residual(next));
            if e < best {
                v = next;
                best = e;
                advanced = true;
                break;
            }
            fraction *= 0.5;
        }
        if !advanced || (fraction * step).abs() < 1e-12 {
            break;
        }
    }
    let t = (point - chart_at(patches, axis, u, v)).dot(direction);
    if (lower && t >= -1e-8) || (!lower && t <= 1e-8) {
        Some((u + t, v, best.sqrt()))
    } else {
        None
    }
}

fn point_key(point: V3) -> [u64; 3] {
    let point = rule::snap3(point) + V3::ZERO;
    [point.x.to_bits(), point.y.to_bits(), point.z.to_bits()]
}

fn refine(
    shape: Solid,
    patches: &[Patch],
    frames: &[(V3, f64)],
    scale: f64,
    axis: V3,
    cache: &mut std::collections::HashMap<([u64; 3], usize), Option<(f64, f64)>>,
) -> Result<Solid> {
    use std::collections::{HashMap, HashSet};
    let near: Vec<bool> = shape
        .verts()
        .iter()
        .map(|&p| in_corner(p, frames, scale))
        .collect();
    let mut locations = vec![vec![None; shape.verts().len()]; frames.len()];
    for (fi, &(origin, sign)) in frames.iter().enumerate() {
        for (i, &point) in shape.verts().iter().enumerate() {
            if !in_corner(point, &[(origin, sign)], scale) {
                continue;
            }
            let key = (point_key(point), fi);
            if let Some(&uv) = cache.get(&key) {
                locations[fi][i] = uv;
                continue;
            }
            let mut best = LINEAR;
            for (pi, patch) in patches.iter().enumerate() {
                let (projected, _, u, v, _) = patch.project(point, &[], origin, sign, scale);
                let distance = (projected - point).norm();
                if distance <= best {
                    best = distance;
                    locations[fi][i] = Some((u, pi as f64 + v));
                }
            }
            if best > 8. * GRID {
                let q = point - origin;
                let q = v3(sign * q.x, q.y, q.z) / scale;
                for (patch, direction, end) in [
                    (&patches[0], v3(1., 0., 0.), false),
                    (&patches[patches.len() - 1], axis, true),
                ] {
                    if let Some((u, t, error)) = patch.continuation(q, direction, end) {
                        if error * scale <= best {
                            best = error * scale;
                            locations[fi][i] =
                                Some((u, if end { patches.len() as f64 + t } else { t }));
                        }
                    }
                }
                for lower in [false, true] {
                    if let Some((u, v, error)) = boundary_extension(patches, axis, q, lower) {
                        if error * scale <= best {
                            best = error * scale;
                            locations[fi][i] = Some((u, v));
                        }
                    }
                }
            }
            cache.insert(key, locations[fi][i]);
        }
    }
    let charts: Vec<_> = shape
        .tris()
        .iter()
        .map(|triangle| {
            locations.iter().enumerate().find_map(|(chart, at)| {
                let uv = [
                    at[triangle[0] as usize]?,
                    at[triangle[1] as usize]?,
                    at[triangle[2] as usize]?,
                ];
                let area = (uv[1].0 - uv[0].0) * (uv[2].1 - uv[0].1)
                    - (uv[2].0 - uv[0].0) * (uv[1].1 - uv[0].1);
                (area.abs() > 1e-13).then_some((chart, uv))
            })
        })
        .collect();
    let edge = |a: u32, b: u32| if a < b { (a, b) } else { (b, a) };
    let world = |chart: usize, u: f64, v: f64| {
        let (origin, sign) = frames[chart];
        let p = chart_at(patches, axis, u, v);
        origin + v3(sign * p.x, p.y, p.z) * scale
    };
    let mut vertices = shape.verts().to_vec();
    let mut occupied: HashSet<_> = vertices.iter().map(|&p| point_key(p)).collect();
    let mut edges = HashMap::<(u32, u32), u32>::new();
    let selected: Vec<bool> = shape
        .tris()
        .iter()
        .zip(shape.face_of())
        .zip(&charts)
        .map(|((triangle, &face), chart)| {
            let face = shape.faces()[face as usize];
            chart.is_some()
                && face.op == "fillet"
                && matches!(face.surface, Surface::Free { kind: "BSPLINE" })
                && triangle.iter().any(|&i| near[i as usize])
                && [
                    (triangle[0], triangle[1]),
                    (triangle[1], triangle[2]),
                    (triangle[2], triangle[0]),
                ]
                .iter()
                .any(|&(a, b)| {
                    (vertices[a as usize] - vertices[b as usize]).norm()
                        > (8. * scale * LINEAR).sqrt()
                })
        })
        .collect();
    for ((triangle, chart), &selected) in shape.tris().iter().zip(&charts).zip(&selected) {
        if !selected {
            continue;
        }
        let (chart, uv) = chart.unwrap();
        for (a, b) in [(0, 1), (1, 2), (2, 0)] {
            let key = edge(triangle[a], triangle[b]);
            if (vertices[triangle[a] as usize] - vertices[triangle[b] as usize]).norm()
                <= (8. * scale * LINEAR).sqrt()
            {
                continue;
            }
            if edges.contains_key(&key) {
                continue;
            }
            // Each knot stays on the authored surface. An alternate interior
            // parameter avoids identifying unrelated vertices on the rule's grid.
            for t in [
                0.5,
                0.375,
                0.625,
                1. / 3.,
                2. / 3.,
                0.4,
                0.6,
                2_f64.sqrt() - 1.,
            ] {
                let point = world(
                    chart,
                    uv[a].0 * (1. - t) + uv[b].0 * t,
                    uv[a].1 * (1. - t) + uv[b].1 * t,
                );
                if occupied.insert(point_key(point)) {
                    let i = vertices.len() as u32;
                    cache.insert(
                        (point_key(point), chart),
                        Some((
                            uv[a].0 * (1. - t) + uv[b].0 * t,
                            uv[a].1 * (1. - t) + uv[b].1 * t,
                        )),
                    );
                    vertices.push(point);
                    edges.insert(key, i);
                    break;
                }
            }
        }
    }
    subdivide(&shape, vertices, &edges)
}

fn subdivide(
    shape: &Solid,
    vertices: Vec<V3>,
    edges: &std::collections::HashMap<(u32, u32), u32>,
) -> Result<Solid> {
    let edge = |a: u32, b: u32| if a < b { (a, b) } else { (b, a) };
    let mut triangles = Vec::new();
    let mut records = Vec::new();
    for (triangle, &face) in shape.tris().iter().zip(shape.face_of()) {
        let mids = [
            edges.get(&edge(triangle[0], triangle[1])).copied(),
            edges.get(&edge(triangle[1], triangle[2])).copied(),
            edges.get(&edge(triangle[2], triangle[0])).copied(),
        ];
        let count = mids.iter().flatten().count();
        let pieces = match count {
            0 => vec![*triangle],
            1 => {
                let k = mids.iter().position(Option::is_some).unwrap();
                let (a, b, c) = (triangle[k], triangle[(k + 1) % 3], triangle[(k + 2) % 3]);
                let m = mids[k].unwrap();
                vec![[a, m, c], [m, b, c]]
            }
            2 => {
                let k = (mids.iter().position(Option::is_none).unwrap() + 1) % 3;
                let (a, b, c) = (triangle[k], triangle[(k + 1) % 3], triangle[(k + 2) % 3]);
                let (ab, bc) = (mids[k].unwrap(), mids[(k + 1) % 3].unwrap());
                vec![[a, ab, c], [ab, bc, c], [ab, b, bc]]
            }
            _ => {
                let [a, b, c] = *triangle;
                let (ab, bc, ca) = (mids[0].unwrap(), mids[1].unwrap(), mids[2].unwrap());
                vec![[a, ab, ca], [ab, b, bc], [ca, bc, c], [ab, bc, ca]]
            }
        };
        for t in pieces {
            triangles.push(t);
            records.push(face);
        }
    }
    Solid::from_mesh(&vertices, &triangles, &records, shape.faces())
}

// The profile sweep and side round compose two chord approximations. Share
// their seam residual, then draw additional knots on the exact outer roll.
fn roof_rolls(mut shape: Solid, radius: f64, angle: f64) -> Result<Solid> {
    use std::collections::{HashMap, HashSet};
    let wanted = |s: Surface| {
        matches!(s,Surface::Torus {major,minor,..}
        if (major-2.*radius).abs()<1e-8 && (minor-radius).abs()<1e-8)
    };
    let mut rolls = Vec::new();
    for &face in shape.face_of() {
        let surface = shape.faces()[face as usize].surface;
        if wanted(surface) && !rolls.iter().any(|s: &Surface| s.key() == surface.key()) {
            rolls.push(surface);
        }
    }
    let angle = math::radians(angle);
    let mut vertices = shape.verts().to_vec();
    let mut occupied: HashSet<_> = vertices.iter().map(|&p| point_key(p)).collect();
    for point in &mut vertices {
        for &surface in &rolls {
            let Surface::Torus {
                c, major, minor, ..
            } = surface
            else {
                unreachable!()
            };
            let q = *point - c;
            let outward = if c.x < 0. { -q.x } else { q.x };
            let phi = math::atan2(-q.y, q.z);
            if outward < 0. || outward > minor || q.y.hypot(q.z) < major || phi < 0. || phi > angle
            {
                continue;
            }
            let error = surface.distance(*point).unwrap();
            if error >= -LINEAR / 2. || error < -4. * LINEAR {
                continue;
            }
            let original = *point;
            occupied.remove(&point_key(original));
            let normal = surface.normal_at(original).unwrap();
            for share in [0.5, 0.625, 0.75, 0.55, 0.65, 0.7] {
                let p = original - normal * (error * share);
                if occupied.insert(point_key(p)) {
                    *point = p;
                    break;
                }
            }
            occupied.insert(point_key(*point));
            break;
        }
    }
    shape = Solid::from_mesh(&vertices, shape.tris(), shape.face_of(), shape.faces())?;
    let edge = |a: u32, b: u32| if a < b { (a, b) } else { (b, a) };
    for _ in 0..2 {
        let mut vertices = shape.verts().to_vec();
        let mut occupied: HashSet<_> = vertices.iter().map(|&p| point_key(p)).collect();
        let mut edges = HashMap::new();
        for (triangle, &face) in shape.tris().iter().zip(shape.face_of()) {
            let surface = shape.faces()[face as usize].surface;
            if !wanted(surface) {
                continue;
            }
            for (a, b) in [
                (triangle[0], triangle[1]),
                (triangle[1], triangle[2]),
                (triangle[2], triangle[0]),
            ] {
                let key = edge(a, b);
                if edges.contains_key(&key)
                    || (vertices[a as usize] - vertices[b as usize]).norm()
                        <= (radius * LINEAR).sqrt()
                {
                    continue;
                }
                for t in [
                    0.5,
                    0.375,
                    0.625,
                    1. / 3.,
                    2. / 3.,
                    0.4,
                    0.6,
                    2_f64.sqrt() - 1.,
                ] {
                    let p = vertices[a as usize].lerp(vertices[b as usize], t);
                    let p = p - surface.normal_at(p).unwrap() * surface.distance(p).unwrap();
                    if occupied.insert(point_key(p)) {
                        let i = vertices.len() as u32;
                        vertices.push(p);
                        edges.insert(key, i);
                        break;
                    }
                }
            }
        }
        shape = subdivide(&shape, vertices, &edges)?;
    }
    Ok(shape)
}

/// Retain the rounded body's topology while drawing its finite front corner on
/// the authored analytic controls. Shared seams stay on their adjoining face.
#[track_caller]
fn project(shape: Solid, corners: &FrontCorners) -> Result<Solid> {
    let scale = corners.scale_mm;
    let patches = corners.surfaces.iter().map(Patch::read).collect::<Result<Vec<_>>>()?;
    let (mut vertices, triangles, source_faces) = (
        shape.verts().to_vec(),
        shape.tris().to_vec(),
        shape.face_of().to_vec(),
    );
    let mut round = vec![false; vertices.len()];
    let mut constraints = vec![Vec::<Surface>::new(); vertices.len()];
    for (triangle, &face) in triangles.iter().zip(&source_faces) {
        let f = shape.faces()[face as usize];
        let fillet = f.op == "fillet" && matches!(f.surface, Surface::Free { kind: "BSPLINE" });
        for &i in triangle {
            if fillet {
                round[i as usize] = true;
            }
            if f.surface.is_analytic()
                && !matches!((f.op, f.surface), ("fillet", Surface::Plane { .. }))
                && !constraints[i as usize]
                    .iter()
                    .any(|s| s.key() == f.surface.key())
            {
                constraints[i as usize].push(f.surface);
            }
        }
    }
    let mut moved = vec![false; vertices.len()];
    for frame in &corners.frames {
        let origin = vector(frame.origin);
        let sign = frame.x_sign;
        for (i, p) in vertices.iter_mut().enumerate() {
            // Keep the shared cylinder seam fixed. Sliding its vertices along
            // the cylinder folds the adjoining tall wall triangles.
            if !round[i] || constraints[i].iter()
                .any(|surface| matches!(surface, Surface::Cylinder { .. })) {
                continue;
            }
            let q = *p - origin;
            let point = v3(sign * q.x, q.y, q.z) / scale;
            if point.x < -0.03
                || point.x > 2.03
                || point.y < -2.03
                || point.y > 0.7
                || point.z < -0.03
                || point.z > 2.7
            {
                continue;
            }
            let mut best = None;
            let mut distance = f64::INFINITY;
            for (k, patch) in patches.iter().enumerate() {
                let result = patch.project(*p, &constraints[i], origin, sign, scale);
                if result.1 < distance {
                    distance = result.1;
                    best = Some((k, result));
                }
            }
            let Some((k, (projected, _, u, v, error))) = best else {
                continue;
            };
            if (projected - *p).norm() > 0.25 || error > 2e-6 {
                continue;
            }
            if k + 1 == patches.len() && v >= 1. - 1e-8 {
                let tangent = patches[k].at(u, 1.) - patches[k].at(u, 1. - 1e-5);
                let local = projected - origin;
                let local = v3(sign * local.x, local.y, local.z) / scale;
                if (point - local).dot(tangent) > 0. {
                    continue;
                }
            }
            let next = projected;
            *p = next;
            moved[i] = true;
        }
    }
    let mut faces = shape.faces().to_vec();
    let index = faces.len() as u32;
    faces.push(Face::new(
        Surface::Free { kind: "BSPLINE" },
        "fillet",
        std::panic::Location::caller(),
    ));
    let mut records = source_faces;
    for (triangle, face) in triangles.iter().zip(&mut records) {
        if shape.faces()[*face as usize].op == "fillet"
            && triangle.iter().all(|&i| moved[i as usize])
        {
            *face = index;
        }
    }
    Solid::from_mesh(&vertices, &triangles, &records, &faces)
}

/// Place the retained shared vertices first; refine that closed surface locally.
#[track_caller]
pub fn replace(shape: Solid, corners: &FrontCorners, side_radius: f64, angle: f64) -> Result<Solid> {
    let scale = corners.scale_mm;
    let patches = corners.surfaces.iter().map(Patch::read).collect::<Result<Vec<_>>>()?;
    let frames: Vec<(V3, f64)> = corners.frames.iter().map(|f| (vector(f.origin), f.x_sign)).collect();
    let degrees = angle;
    let angle = math::radians(angle);
    let axis = v3(0., math::cos(angle), math::sin(angle));
    let mut shape = project(shape, corners)?;
    let mut cache = std::collections::HashMap::new();
    for _ in 0..4 {
        shape = refine(shape, &patches, &frames, scale, axis, &mut cache)?;
    }
    let shape = roof_rolls(shape, side_radius, degrees)?;
    // Projecting the blend changes the edge of its tangent planes too. Join
    // those local triangles into one patch before simplifying; keeping their
    // former face boundaries pins a folded strip along the analytic seam.
    // Other faces retain their original analytic boundaries.
    let mut original = shape.faces().to_vec();
    let patch = original.len() as u32;
    original.push(Face::new(
        Surface::Free { kind: "BSPLINE" },
        "fillet",
        std::panic::Location::caller(),
    ));
    // Keep every triangle outside the corner fixed during this local cleanup.
    // Separate temporary runs pin their edges; restore the analytic face
    // records after simplification so the export retains its normal records.
    let mut faces = original.clone();
    let records: Vec<_> = shape.tris().iter().zip(shape.face_of())
        .map(|(triangle, &face)| {
            if triangle.iter().all(|&i| in_corner(shape.verts()[i as usize], &frames, scale)) {
                patch
            } else {
                let fixed = faces.len() as u32;
                faces.push(original[face as usize]);
                fixed
            }
        }).collect();
    let cleaned = Solid::from_mesh(shape.verts(), shape.tris(), &records, &faces)?
        .simplified_to(LINEAR)?;
    let restored: Vec<_> = cleaned.faces().iter()
        .map(|face| original.iter().position(|old| old == face).unwrap() as u32)
        .collect();
    let records: Vec<_> = cleaned.face_of().iter().map(|&f| restored[f as usize]).collect();
    Solid::from_mesh(cleaned.verts(), cleaned.tris(), &records, &original)
}
