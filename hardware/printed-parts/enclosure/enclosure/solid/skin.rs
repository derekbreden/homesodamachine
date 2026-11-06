//! The enclosure's print flute field, cut from the smooth mesh along its rail stations.
//! The structural model and its callers remain separate from this print surface.
use crate::numbers::{Field, Rail};
use crate::plan::Bounds;
use anyhow::{Context, Result, ensure};
use manifold_csg::Manifold;
use serde_json::json;
use std::collections::HashMap;

type P2 = [f64; 2];
type P3 = [f64; 3];

struct Mesh {
    points: Vec<P3>,
    triangles: Vec<[usize; 3]>,
}

impl Mesh {
    fn manifold(&self) -> Result<Manifold> {
        // Trimesh's Manifold backend takes float32 positions. Preserve that boundary.
        let v: Vec<f32> = self.points.iter().flatten().map(|&x| x as f32).collect();
        let t: Vec<u32> = self.triangles.iter().flatten().map(|&i| i as u32).collect();
        Manifold::from_mesh_f32(&v, 3, &t).context("the print mesh is accepted by Manifold")
    }

    fn bounds(&self) -> (P3, P3) {
        let mut lo = [f64::INFINITY; 3];
        let mut hi = [f64::NEG_INFINITY; 3];
        for p in &self.points {
            for k in 0..3 {
                lo[k] = lo[k].min(p[k]);
                hi[k] = hi[k].max(p[k]);
            }
        }
        (lo, hi)
    }
}

fn sub(a: P2, b: P2) -> P2 {
    [a[0] - b[0], a[1] - b[1]]
}
fn norm(p: P2) -> f64 {
    p[0].hypot(p[1])
}

fn smooth_corner(rail: &Rail, i: usize) -> bool {
    let n=rail.normal.len();
    let curved=|j:usize| rail.normal[j][0].abs()>1e-6 && rail.normal[j][1].abs()>1e-6;
    let before=if rail.closed {(i+n-1)%n} else {i.saturating_sub(1)};
    let after=if rail.closed {(i+1)%n} else {(i+1).min(n-1)};
    curved(i) || curved(before) || curved(after)
}

/// The intersection of one triangle with a horizontal plane. Coplanar facets contribute
/// nothing; an on-plane edge belongs to the facet on its positive side, as in mesh_plane.
fn section(mesh: &Mesh, triangle: &[usize; 3], z: f64) -> Option<[P2; 2]> {
    let p = triangle.map(|i| mesh.points[i]);
    let d = p.map(|v| v[2] - z);
    let sign = d.map(|v| {
        if v.abs() <= 1e-8 {
            0
        } else if v > 0.0 {
            1
        } else {
            -1
        }
    });
    let mut hits = Vec::with_capacity(2);
    let zero = sign.iter().filter(|&&s| s == 0).count();
    if zero == 3 {
        return None;
    }
    if zero == 2 {
        if !sign.contains(&1) {
            return None;
        }
        for i in 0..3 {
            if sign[i] == 0 {
                hits.push([p[i][0], p[i][1]]);
            }
        }
    } else {
        if !sign.contains(&1) || !sign.contains(&-1) {
            return None;
        }
        for i in 0..3 {
            if sign[i] == 0 {
                hits.push([p[i][0], p[i][1]]);
            }
            let j = (i + 1) % 3;
            if sign[i] * sign[j] < 0 {
                let t = d[i] / (d[i] - d[j]);
                hits.push([
                    p[i][0] + t * (p[j][0] - p[i][0]),
                    p[i][1] + t * (p[j][1] - p[i][1]),
                ]);
            }
        }
    }
    (hits.len() == 2).then(|| [hits[0], hits[1]])
}

fn show_mask(mesh: &Mesh, rail: &Rail, rows: &[f64], field: &Field) -> Vec<bool> {
    let (n, h) = (rail.point.len(), rows.len());
    let mut mask = vec![false; n * h];
    let cell = field.face_tol;
    let key = |p: P2| ((p[0] / cell).floor() as i64, (p[1] / cell).floor() as i64);
    // Put the query stations in the grid once. Each outline sample then touches only its
    // neighboring cells; no slice constructs the many sampled points it will never read.
    let mut grid: HashMap<(i64, i64), Vec<usize>> = HashMap::new();
    for (i, &p) in rail.point.iter().enumerate() {
        grid.entry(key(p)).or_default().push(i);
    }
    let ranges: Vec<(f64, f64)> = mesh
        .triangles
        .iter()
        .map(|t| {
            let z = t.map(|i| mesh.points[i][2]);
            (
                z.into_iter().fold(f64::INFINITY, f64::min),
                z.into_iter().fold(f64::NEG_INFINITY, f64::max),
            )
        })
        .collect();
    for (j, &z) in rows.iter().enumerate() {
        let mut sample = |p: P2| {
            let (x, y) = key(p);
            for dx in -1..=1 {
                for dy in -1..=1 {
                    if let Some(indices) = grid.get(&(x + dx, y + dy)) {
                        for &i in indices {
                            if !mask[i * h + j] && norm(sub(p, rail.point[i])) < cell {
                                mask[i * h + j] = true;
                            }
                        }
                    }
                }
            }
        };
        for (t, &(lo, hi)) in mesh.triangles.iter().zip(&ranges) {
            if z < lo - 1e-8 || z > hi + 1e-8 {
                continue;
            }
            if let Some([a, b]) = section(mesh, t, z) {
                let length = norm(sub(b, a));
                let count = ((length / (cell / 2.0)) as usize).max(1);
                for k in 0..count {
                    let s = k as f64 / count as f64;
                    sample([a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s]);
                }
                sample(b);
            }
        }
    }
    mask
}

fn bridge_grooves(mask: &mut [bool], rail: &Rail, h: usize, f: &Field) {
    let n = rail.s.len();
    let span = rail.s[n - 1] + rail.s[1] - 2.0 * rail.s[0];
    for j in 0..h {
        let indices: Vec<usize> = (0..n).filter(|&i| !mask[i * h + j]).collect();
        if indices.is_empty() || indices.len() == n {
            continue;
        }
        let mut groups: Vec<Vec<usize>> = Vec::new();
        for i in indices {
            if groups.last().is_none_or(|g| g[g.len() - 1] + 1 != i) {
                groups.push(Vec::new());
            }
            groups.last_mut().unwrap().push(i);
        }
        if rail.closed
            && groups.len() > 1
            && groups[0][0] == 0
            && groups.last().unwrap().last() == Some(&(n - 1))
        {
            let mut wrap = groups.pop().unwrap();
            wrap.append(&mut groups[0]);
            groups[0] = wrap;
        }
        for group in groups {
            let first = group[0];
            let last = *group.last().unwrap();
            let a = rail.s[first] - f.across / 2.0;
            let mut b = rail.s[last] + f.across / 2.0;
            if first > last {
                b += span;
            }
            let centre = (a / f.pitch).round_ties_even() * f.pitch;
            if (a - centre).abs() <= f.width / 2.0 && (b - centre).abs() <= f.width / 2.0 {
                for i in group {
                    mask[i * h + j] = true;
                }
            }
        }
    }
}

/// The lower envelope of equal-curvature parabolas: the exact squared Euclidean distance
/// transform in one axis, with the axis's physical station spacing.
fn edt(line: &[f64], step: f64) -> Vec<f64> {
    let n = line.len();
    let mut sites = vec![0usize; n];
    let mut joins = vec![f64::INFINITY; n + 1];
    joins[0] = f64::NEG_INFINITY;
    let mut k = 0;
    let q = step * step;
    for i in 1..n {
        let mut split;
        loop {
            let p = sites[k];
            split = ((line[i] + q * (i * i) as f64) - (line[p] + q * (p * p) as f64))
                / (2.0 * q * (i - p) as f64);
            if split > joins[k] || k == 0 {
                break;
            }
            k -= 1;
        }
        k += 1;
        sites[k] = i;
        joins[k] = split;
        joins[k + 1] = f64::INFINITY;
    }
    k = 0;
    (0..n)
        .map(|i| {
            while joins[k + 1] < i as f64 {
                k += 1;
            }
            let d = i as f64 - sites[k] as f64;
            line[sites[k]] + q * d * d
        })
        .collect()
}

fn depth_field(mask: &[bool], rail: &Rail, h: usize, f: &Field) -> Vec<f64> {
    let n = rail.s.len();
    // A finite sentinel above the greatest useful squared distance avoids infinity minus
    // infinity in the envelope. Distances beyond rise produce exactly the same full depth.
    let far = f.rise * f.rise + 1.0;
    let mut distance = vec![0.0; n * h];
    for i in 0..n {
        let mut line = vec![0.0; h + 2];
        for j in 0..h {
            line[j + 1] = if mask[i * h + j] { far } else { 0.0 };
        }
        distance[i * h..(i + 1) * h].copy_from_slice(&edt(&line, f.along)[1..h + 1]);
    }
    for j in 0..h {
        let line = if rail.closed {
            (0..3 * n)
                .map(|i| distance[(i % n) * h + j])
                .collect::<Vec<_>>()
        } else {
            let mut line = vec![0.0; n + 2];
            for i in 0..n {
                line[i + 1] = distance[i * h + j];
            }
            line
        };
        let line = edt(&line, f.across);
        let start = if rail.closed { n } else { 1 };
        for i in 0..n {
            distance[i * h + j] = line[start + i];
        }
    }
    for i in 0..n {
        let offset = (rail.s[i] + f.pitch / 2.0).rem_euclid(f.pitch) - f.pitch / 2.0;
        let groove = (1.0 - (offset / (f.width / 2.0)).powi(2)).max(0.0).sqrt();
        for j in 0..h {
            let along = (distance[i * h + j].sqrt() / f.rise).min(1.0);
            distance[i * h + j] = if mask[i * h + j] {
                f.depth * groove * along * along * (3.0 - 2.0 * along)
            } else {
                0.0
            };
        }
    }
    distance
}

fn chord_error(points: &[P2], first: usize, last: usize) -> f64 {
    if last - first < 2 {
        return 0.0;
    }
    let a = points[first];
    let run = sub(points[last], a);
    let span = norm(run);
    points[first + 1..last]
        .iter()
        .map(|&p| {
            let off = sub(p, a);
            if span < 1e-12 {
                norm(off)
            } else {
                (off[0] * run[1] - off[1] * run[0]).abs() / span
            }
        })
        .fold(0.0, f64::max)
}

fn thin(depth: &[f64], rail: &Rail, h: usize, plan_tol: f64) -> (Vec<usize>, Vec<usize>) {
    let n = rail.s.len();
    let mut rows = vec![0];
    for j in 1..h {
        if (0..n).any(|i| (depth[i * h + j] - depth[i * h + rows[rows.len() - 1]]).abs() > 0.01) {
            if j - 1 != rows[rows.len() - 1] {
                rows.push(j - 1);
            }
            rows.push(j);
        }
    }
    if rows[rows.len() - 1] != h - 1 {
        rows.push(h - 1);
    }
    let mut cols = vec![0];
    for i in 1..n {
        let last = cols[cols.len() - 1];
        let moved = (0..h).any(|j| (depth[i * h + j] - depth[last * h + j]).abs() > 0.01);
        if !moved && chord_error(&rail.point, last, i) <= plan_tol {
            continue;
        }
        if i - 1 != last {
            cols.push(i - 1);
        }
        cols.push(i);
    }
    if cols[cols.len() - 1] != n - 1 {
        cols.push(n - 1);
    }
    (cols, rows)
}

fn cutter(mesh: &Mesh, rail: &Rail, f: &Field) -> Result<Option<(Mesh, serde_json::Value)>> {
    ensure!(
        rail.s.len() == rail.point.len() && rail.s.len() == rail.normal.len() && rail.s.len() >= 3,
        "rail samples have matching stations, points and normals"
    );
    let (lo, hi) = mesh.bounds();
    let reach = f.margin + f.depth + f.face_tol;
    for k in 0..2 {
        if rail
            .point
            .iter()
            .map(|p| p[k])
            .fold(f64::INFINITY, f64::min)
            - reach
            > hi[k]
            || rail
                .point
                .iter()
                .map(|p| p[k])
                .fold(f64::NEG_INFINITY, f64::max)
                + reach
                < lo[k]
        {
            return Ok(None);
        }
    }
    let (start, stop) = if let Some([a, b]) = rail.band {
        (
            lo[2].max(a + f.overrun),
            hi[2].min(b - f.overrun) + f.along / 2.0,
        )
    } else {
        (lo[2] + f.along, hi[2] - f.along / 2.0)
    };
    let count = ((stop - start) / f.along).ceil().max(0.0) as usize;
    let rows: Vec<f64> = (0..count).map(|i| start + i as f64 * f.along).collect();
    if rows.len() < 4 {
        return Ok(None);
    }
    let (n, h) = (rail.s.len(), rows.len());
    let mut mask = show_mask(mesh, rail, &rows, f);
    if !mask.contains(&true) {
        return Ok(None);
    }
    bridge_grooves(&mut mask, rail, h, f);
    // Retain the complete outer quarter-rounds at the enclosure's four
    // vertical corners. Their surface is the same envelope as the flute tips;
    // the existing distance field eases the adjacent straight-wall grooves out.
    for i in 0..n {
        if smooth_corner(rail,i) {
            mask[i * h..(i + 1) * h].fill(false);
        }
    }
    for &[x0, x1, y0, y1, z0, z1] in &rail.plain {
        for (i, &[x, y]) in rail.point.iter().enumerate() {
            if x >= x0 && x <= x1 && y >= y0 && y <= y1 {
                for (j, &z) in rows.iter().enumerate() {
                    if z >= z0 && z <= z1 {
                        mask[i * h + j] = false;
                    }
                }
            }
        }
    }
    let mut depth = depth_field(&mask, rail, h, f);
    if !depth.iter().any(|&d| d > 0.0) {
        return Ok(None);
    }
    if !rail.closed {
        depth[..h].fill(0.0);
        depth[(n - 1) * h..].fill(0.0);
    }
    if rail.band.is_some() {
        for i in 0..n {
            depth[i * h] = 0.0;
            depth[(i + 1) * h - 1] = 0.0;
        }
    }
    let (cols, kept_rows) = thin(&depth, rail, h, f.plan_tol);
    let mut z: Vec<f64> = kept_rows.iter().map(|&j| rows[j]).collect();
    if rail.band.is_none() {
        z.insert(0, z[0] - f.overrun);
        z.push(z[z.len() - 1] + f.overrun);
    }
    let (nc, nh) = (cols.len(), z.len());
    let base = nc * nh;
    let mut points = vec![[0.0; 3]; 2 * base];
    for (i, &col) in cols.iter().enumerate() {
        for (j, &height) in z.iter().enumerate() {
            // Keep the cutter off the retained corner, rather than coincident
            // with its differently sampled analytic surface.
            let d = if smooth_corner(rail,col) {
                -f.margin/2.0
            } else if rail.band.is_none() && (j == 0 || j == nh - 1) {
                0.0
            } else {
                depth[col * h + kept_rows[j - usize::from(rail.band.is_none())]]
            };
            let (p, normal) = (rail.point[col], rail.normal[col]);
            points[i * nh + j] = [
                p[0] + normal[0] * f.margin,
                p[1] + normal[1] * f.margin,
                height,
            ];
            points[base + i * nh + j] = [p[0] - normal[0] * d, p[1] - normal[1] * d, height];
        }
    }
    let mut triangles = Vec::new();
    let mut quad_half = |a, b, c, d, second| {
        triangles.push(if second { [a, c, d] } else { [a, b, c] });
    };
    let rungs = if rail.closed { nc } else { nc - 1 };
    // Preserve the field's own array order: first triangle of every outer quad, then
    // its second triangles, followed by the inner skin and the two height caps.
    // The payload's deterministic reducer reads this order after the final repair.
    for surface in 0..4 {
        for second in [false, true] {
            for i in 0..rungs {
                let next = (i + 1) % nc;
                if surface < 2 {
                    for j in 0..nh - 1 {
                        let (a, b) = (i * nh + j, next * nh + j);
                        if surface == 0 {
                            quad_half(a, a + 1, b + 1, b, second);
                        } else {
                            quad_half(base + a, base + b, base + b + 1, base + a + 1, second);
                        }
                    }
                } else {
                    let (a, b) = (i * nh, next * nh);
                    if surface == 2 {
                        quad_half(a, b, base + b, base + a, second);
                    } else {
                        let (a, b) = (a + nh - 1, b + nh - 1);
                        quad_half(a, base + a, base + b, b, second);
                    }
                }
            }
        }
    }
    if !rail.closed {
        for far in [false, true] {
            for second in [false, true] {
                for j in 0..nh - 1 {
                    if far {
                        let a = (nc - 1) * nh + j;
                        quad_half(a, a + 1, base + a + 1, base + a, second);
                    } else {
                        quad_half(j, base + j, base + j + 1, j + 1, second);
                    }
                }
            }
        }
    }
    let volume: f64 = triangles
        .iter()
        .map(|&[a, b, c]| {
            let (a, b, c) = (points[a], points[b], points[c]);
            a[0] * (b[1] * c[2] - b[2] * c[1])
                + a[1] * (b[2] * c[0] - b[0] * c[2])
                + a[2] * (b[0] * c[1] - b[1] * c[0])
        })
        .sum();
    if volume < 0.0 {
        for t in &mut triangles {
            t.swap(0, 2);
        }
    }
    let source = json!({"src": hsm_kernel::src_line(std::panic::Location::caller()),
                        "op": "flute cut"});
    Ok(Some((Mesh { points, triangles }, source)))
}

fn flute_mesh_observed(
    mesh: &Mesh,
    field: &Field,
    rails: &[Rail],
    extra_plain: &[Bounds],
    mut observer: Option<&mut dyn FluteObserver>,
) -> Result<Manifold> {
    let mut rails = rails.to_vec();
    for rail in &mut rails {
        rail.plain.extend_from_slice(extra_plain);
    }
    let mut operands = vec![mesh.manifold()?];
    if let Some(watch) = observer.as_mut() {
        watch.base(&operands[0]);
    }
    for rail in &rails {
        if let Some((tool, source)) = cutter(mesh, rail, field)? {
            let tool = tool.manifold()?;
            if let Some(watch) = observer.as_mut() {
                watch.cutter(&tool, source);
            }
            operands.push(tool);
        }
    }
    let out = if operands.len() == 1 {
        if let Some(watch) = observer.as_mut() {
            watch.cut(&operands[0]);
        }
        operands.remove(0)
    } else {
        let cut = if operands.len() == 2 {
            operands[0].difference(&operands[1])
        } else {
            operands[0].difference(&Manifold::batch_union(&operands[1..]))
        };
        drop(operands);
        if let Some(watch) = observer.as_mut() {
            watch.cut(&cut);
        }
        let (vertices, props, triangles) = cut.to_mesh_f32();
        drop(cut);
        // A second construction from the positions its STL can store.
        Manifold::from_mesh_f32(&vertices, props, &triangles)?
    };
    if let Some(watch) = observer.as_mut() {
        watch.finished(&out);
    }
    Ok(out)
}

fn mesh(solid: &hsm_kernel::Solid) -> Mesh {
    Mesh {
        points: solid.verts().iter().map(|p| p.to_array()).collect(),
        triangles: solid.tris().iter().map(|t| t.map(|i| i as usize)).collect(),
    }
}

/// The print field cut into a structural kernel body; `extra_plain` lands stay smooth.
pub fn flute_solid(solid: &hsm_kernel::Solid, field: &Field, rails: &[Rail], extra_plain: &[Bounds]) -> Result<Manifold> {
    flute_mesh_observed(&mesh(solid), field, rails, extra_plain, None)
}

/// Observers read relations beside the print path; they cannot supply or alter its meshes.
pub trait FluteObserver {
    fn base(&mut self, shape: &Manifold);
    fn cutter(&mut self, shape: &Manifold, source: serde_json::Value);
    fn cut(&mut self, shape: &Manifold);
    fn finished(&mut self, shape: &Manifold);
}

pub fn flute_solid_observed(
    solid: &hsm_kernel::Solid,
    field: &Field,
    rails: &[Rail],
    extra_plain: &[Bounds],
    observer: &mut dyn FluteObserver,
) -> Result<Manifold> {
    flute_mesh_observed(&mesh(solid), field, rails, extra_plain, Some(observer))
}
