//! Connected planar faces and their neighbours identify local print-surface anomalies.
use super::*;
use std::collections::HashSet;

pub fn find(d: &Data, class: &str, up: f64, tilt: f64) -> Result<Vec<Finding>> {
    Ok(match class {
        "step" => steps(d),
        "bump" => bumps(d),
        "sliver" => slivers(d, up),
        "ceiling" => ceilings(d, up),
        "slope" => slopes(d, up),
        "ledge" => ledges(d, up, tilt),
        _ => Vec::new(),
    })
}
fn extrema(d: &Data, up: f64) -> f64 {
    d.mesh
        .vertices
        .iter()
        .map(|p| up * p[2])
        .fold(f64::INFINITY, f64::min)
}
fn uv(p: &Plane, v: V3) -> [f64; 2] {
    [v.dot(p.u), v.dot(p.v)]
}
fn widths(a: &Plane, b: &Plane) -> ([f64; 2], [f64; 2], [f64; 2]) {
    let lo = [a.uv_lo[0].max(b.uv_lo[0]), a.uv_lo[1].max(b.uv_lo[1])];
    let hi = [a.uv_hi[0].min(b.uv_hi[0]), a.uv_hi[1].min(b.uv_hi[1])];
    (lo, hi, [hi[0] - lo[0], hi[1] - lo[1]])
}
fn cross(a: [f64; 2], b: [f64; 2], p: [f64; 2]) -> f64 {
    (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
}
fn holds(t: [[f64; 2]; 3], p: [f64; 2]) -> bool {
    let s = [
        cross(t[0], t[1], p),
        cross(t[1], t[2], p),
        cross(t[2], t[0], p),
    ];
    s.iter().all(|s| *s >= -1e-9) || s.iter().all(|s| *s <= 1e-9)
}
fn on_facets(d: &Data, p: &Plane, lo: [f64; 2], hi: [f64; 2]) -> Option<V3> {
    let center = [(lo[0] + hi[0]) / 2., (lo[1] + hi[1]) / 2.];
    let mut nearest = None;
    let mut distance = f64::INFINITY;
    for &i in &p.f {
        if holds(d.tri[i].map(|v| uv(p, v)), center) {
            return Some(p.u * center[0] + p.v * center[1] + p.n * p.o);
        }
        let c = uv(p, d.centers[i]);
        if (0..2).all(|j| c[j] >= lo[j] - 1e-6 && c[j] <= hi[j] + 1e-6) {
            let delta = (c[0] - center[0]).powi(2) + (c[1] - center[1]).powi(2);
            if delta < distance {
                distance = delta;
                nearest = Some(d.centers[i]);
            }
        }
    }
    nearest
}
fn point_edge(p: [f64; 2], a: [f64; 2], b: [f64; 2]) -> f64 {
    let delta = [b[0] - a[0], b[1] - a[1]];
    let len = delta[0] * delta[0] + delta[1] * delta[1];
    let t = if len > 0. {
        (((p[0] - a[0]) * delta[0] + (p[1] - a[1]) * delta[1]) / len).clamp(0., 1.)
    } else {
        0.
    };
    ((p[0] - a[0] - t * delta[0]).powi(2) + (p[1] - a[1] - t * delta[1]).powi(2)).sqrt()
}
fn footprint_gap(d: &Data, a: &Plane, b: &Plane) -> f64 {
    let mut best = f64::INFINITY;
    for &i in &a.f {
        let ta = d.tri[i].map(|p| uv(a, p));
        for &j in &b.f {
            let tb = d.tri[j].map(|p| uv(a, p));
            if ta.iter().any(|p| holds(tb, *p)) || tb.iter().any(|p| holds(ta, *p)) {
                return 0.;
            }
            for k in 0..3 {
                for l in 0..3 {
                    let x = cross(ta[k], ta[(k + 1) % 3], tb[l]);
                    let y = cross(ta[k], ta[(k + 1) % 3], tb[(l + 1) % 3]);
                    let z = cross(tb[l], tb[(l + 1) % 3], ta[k]);
                    let w = cross(tb[l], tb[(l + 1) % 3], ta[(k + 1) % 3]);
                    if x * y < 0. && z * w < 0. {
                        return 0.;
                    }
                    best = best
                        .min(point_edge(ta[k], tb[l], tb[(l + 1) % 3]))
                        .min(point_edge(tb[l], ta[k], ta[(k + 1) % 3]));
                }
            }
        }
    }
    best
}
fn steps(d: &Data) -> Vec<Finding> {
    let mut out = Vec::new();
    let mut groups: BTreeMap<[i64; 3], Vec<&Plane>> = BTreeMap::new();
    for p in &d.planes {
        groups
            .entry(xyz(p.n).map(|x| (x * 1000.).round() as i64))
            .or_default()
            .push(p);
    }
    let mut islands: HashMap<usize, Vec<Plane>> = HashMap::new();
    for group in groups.values_mut() {
        group.sort_by(|a, b| a.o.total_cmp(&b.o));
        for pair in group.windows(2) {
            let (a, b) = (pair[0], pair[1]);
            let delta = b.o - a.o;
            if delta <= OFFSET || delta > 1. || a.area.min(b.area) < 0.5 {
                continue;
            }
            let (_, _, w) = widths(a, b);
            if w[0].min(w[1]) < 0.2 || w[0].max(w[1]) < 2. {
                continue;
            }
            islands.entry(a.gid).or_insert_with(|| a.components(d));
            islands.entry(b.gid).or_insert_with(|| b.components(d));
            let mut pairs = Vec::new();
            for ia in &islands[&a.gid] {
                for ib in &islands[&b.gid] {
                    let (lo, hi, w) = widths(ia, ib);
                    if ia.area.min(ib.area) >= 0.5 && w[0].min(w[1]) >= 0.2 && w[0].max(w[1]) >= 2.
                    {
                        pairs.push((ia, ib, lo, hi, w));
                    }
                }
            }
            pairs.sort_by(|a, b| b.4[0].max(b.4[1]).total_cmp(&a.4[0].max(a.4[1])));
            for (ia, ib, lo, hi, w) in pairs {
                if ia.soft_frac(d) > 0.75 || ib.soft_frac(d) > 0.75 {
                    continue;
                }
                let small = if ia.area <= ib.area { ia } else { ib };
                if d.banded(small, small, 2, false) {
                    continue;
                }
                let Some(at) = on_facets(d, small, lo, hi) else {
                    continue;
                };
                if footprint_gap(d, ia, ib) > 1. {
                    continue;
                }
                out.push(Finding::new(
                    "step",
                    w[0].max(w[1]) / delta,
                    format!(
                        "Δ{delta:.3} mm between parallel planes · footprint met {:.1} × {:.1} mm",
                        w[0].max(w[1]),
                        w[0].min(w[1])
                    ),
                    vec![
                        face(ia.n, ia.thru(), "faceA"),
                        face(ib.n, ib.thru(), "faceB"),
                        click(at),
                    ],
                    ia.f.iter().chain(&ib.f).copied().collect(),
                ));
                break;
            }
        }
    }
    out
}
fn bumps(d: &Data) -> Vec<Finding> {
    let flats = d
        .planes
        .iter()
        .filter(|p| p.area >= 1. && !(p.soft_frac(d) > 0.75 && p.width()[0].min(p.width()[1]) < 2.))
        .collect::<Vec<_>>();
    let mut flat_n = vec![V3::ZERO; d.tri.len()];
    for p in &flats {
        for &i in &p.f {
            flat_n[i] = p.n;
        }
    }
    let mut out = Vec::new();
    let mut seen = HashSet::new();
    for flat in flats {
        let mine = flat.f.iter().copied().collect::<BTreeSet<_>>();
        let rises = |i: usize| {
            let h = d.centers[i].dot(flat.n) - flat.o;
            !mine.contains(&i)
                && d.n[i].dot(flat.n) >= (70f64.to_radians()).cos()
                && flat_n[i].dot(flat.n) < (3f64.to_radians()).cos()
                && h > 0.01
                && h <= 1.
                && d.tri[i]
                    .iter()
                    .map(|p| p.dot(flat.n) - flat.o)
                    .fold(f64::INFINITY, f64::min)
                    >= -0.01
        };
        let flat_vertices = flat
            .f
            .iter()
            .flat_map(|&i| d.vid[i])
            .collect::<BTreeSet<_>>();
        let mut todo = d
            .touching(&flat.f)
            .into_iter()
            .filter(|&i| rises(i))
            .collect::<BTreeSet<_>>();
        while let Some(&start) = todo.iter().next() {
            todo.remove(&start);
            let mut patch = vec![start];
            let mut held = BTreeSet::from([start]);
            let mut at = 0;
            while at < patch.len() {
                for &v in &d.vid[patch[at]] {
                    for &j in &d.touch[v] {
                        if !held.contains(&j) && rises(j) {
                            held.insert(j);
                            patch.push(j);
                            todo.remove(&j);
                        }
                    }
                }
                at += 1;
            }
            patch.sort_unstable();
            if seen.contains(&patch) {
                continue;
            }
            let pts = patch.iter().flat_map(|&i| d.tri[i]).collect::<Vec<_>>();
            let (top_i, top) = pts
                .iter()
                .enumerate()
                .map(|(i, p)| (i, p.dot(flat.n) - flat.o))
                .max_by(|a, b| a.1.total_cmp(&b.1))
                .unwrap();
            if top <= 0.02
                || top > 1.
                || patch
                    .iter()
                    .all(|&i| d.n[i].dot(flat.n) > (5f64.to_radians()).cos())
            {
                continue;
            }
            if d.touching(&patch).into_iter().any(|i| {
                !mine.contains(&i)
                    && flat_n[i].dot(flat.n) >= (3f64.to_radians()).cos()
                    && d.centers[i].dot(flat.n) - flat.o > 0.02
            }) {
                continue;
            }
            let values = pts.iter().map(|p| uv(flat, *p)).collect::<Vec<_>>();
            let mean = [
                values.iter().map(|p| p[0]).sum::<f64>() / values.len() as f64,
                values.iter().map(|p| p[1]).sum::<f64>() / values.len() as f64,
            ];
            let (mut xx, mut yy, mut xy) = (0., 0., 0.);
            for p in &values {
                let (x, y) = (p[0] - mean[0], p[1] - mean[1]);
                xx += x * x;
                yy += y * y;
                xy += x * y;
            }
            let angle = (2. * xy).atan2(xx - yy) / 2.;
            let (sn, cs) = angle.sin_cos();
            let axes = values
                .iter()
                .map(|p| {
                    let (x, y) = (p[0] - mean[0], p[1] - mean[1]);
                    [cs * x + sn * y, -sn * x + cs * y]
                })
                .collect::<Vec<_>>();
            let lo = axes.iter().map(|p| p[0]).fold(f64::INFINITY, f64::min);
            let hi = axes.iter().map(|p| p[0]).fold(f64::NEG_INFINITY, f64::max);
            let across_lo = axes.iter().map(|p| p[1]).fold(f64::INFINITY, f64::min);
            let across_hi = axes.iter().map(|p| p[1]).fold(f64::NEG_INFINITY, f64::max);
            let length = hi - lo;
            let width = across_hi - across_lo;
            if length < 0.5 || width < 0.3 {
                continue;
            }
            let met = patch
                .iter()
                .flat_map(|&i| d.vid[i])
                .map(|v| flat_vertices.contains(&v))
                .collect::<Vec<_>>();
            let mut bins: [Option<(usize, usize)>; 8] = [None; 8];
            for (i, p) in axes.iter().enumerate() {
                let k = (((p[0] - lo) / length * 8.).floor() as usize).min(7);
                let (mut low, mut high) = bins[k].unwrap_or((i, i));
                if p[1] < axes[low][1] {
                    low = i;
                }
                if p[1] > axes[high][1] {
                    high = i;
                }
                bins[k] = Some((low, high));
            }
            let slices = bins
                .iter()
                .flatten()
                .copied()
                .filter(|(a, b)| a != b)
                .collect::<Vec<_>>();
            if slices.is_empty()
                || (slices.iter().filter(|&&(a, b)| met[a] && met[b]).count() as f64)
                    < 0.75 * slices.len() as f64
            {
                continue;
            }
            seen.insert(patch.clone());
            out.push(Finding::new(
                "bump",
                length / top,
                format!("{top:.3} mm bump off a flat face · {length:.1} × {width:.1} mm"),
                vec![face(flat.n, flat.thru(), "faceA"), click(pts[top_i])],
                flat.f.iter().copied().chain(patch).collect(),
            ));
        }
    }
    out
}
fn slivers(d: &Data, up: f64) -> Vec<Finding> {
    let bed = extrema(d, up);
    let mut out = Vec::new();
    for whole in &d.planes {
        let n = whole.n;
        if !((n.z.abs() - 1.).abs() < 0.01 || n.z.abs() < 0.01) || whole.soft_frac(d) > 0.75 {
            continue;
        }
        if up * n.z < -0.99 && (up * whole.o / n.z - bed).abs() < 0.05 {
            continue;
        }
        for p in whole.components(d) {
            let w = p.width();
            let (minor, major) = (w[0].min(w[1]), w[0].max(w[1]));
            if minor > 1.6
                || major < 4.
                || major < 4. * minor
                || p.area < 0.8 * minor * major
                || d.banded(&p, whole, 1, false)
            {
                continue;
            }
            let axis = if w[0] >= w[1] { p.u } else { p.v };
            let c = p.thru();
            let a = c - axis * (major / 2.);
            let b = c + axis * (major / 2.);
            let edge = format!(
                "edge: x={:.3} y={:.3} z={:.3} → x={:.3} y={:.3} z={:.3} · len {major:.3} · straight",
                a.x, a.y, a.z, b.x, b.y, b.z
            );
            out.push(Finding::new(
                "sliver",
                major,
                format!("{minor:.3} mm strip, {major:.1} mm long"),
                vec![face(n, c, "face"), edge, click(c)],
                p.f,
            ));
        }
    }
    out
}
fn z_in(t: [V3; 3], x: f64, y: f64) -> Option<f64> {
    let [a, b, c] = t;
    let det = (b.y - c.y) * (a.x - c.x) + (c.x - b.x) * (a.y - c.y);
    if det.abs() < 1e-12 {
        return None;
    }
    let w1 = ((b.y - c.y) * (x - c.x) + (c.x - b.x) * (y - c.y)) / det;
    let w2 = ((c.y - a.y) * (x - c.x) + (a.x - c.x) * (y - c.y)) / det;
    let w3 = 1. - w1 - w2;
    (w1.min(w2).min(w3) >= -1e-6).then_some(w1 * a.z + w2 * b.z + w3 * c.z)
}
fn ceilings(d: &Data, up: f64) -> Vec<Finding> {
    let bed = extrema(d, up);
    let bounds = d.mesh.bounds();
    let mut out = Vec::new();
    for whole in &d.planes {
        if up * whole.n.z >= -0.99
            || whole.area < CEILING_AREA
            || up * whole.o / whole.n.z <= bed + OFF_BED
            || whole.soft_frac(d) > 0.75
        {
            continue;
        }
        for p in whole
            .components(d)
            .into_iter()
            .filter(|p| p.area >= CEILING_AREA)
        {
            let z0 = p.o / p.n.z;
            let q0 = up * z0;
            let mut gaps = Vec::new();
            for &i in p.f.iter().step_by((p.f.len() / 12).max(1)).take(12) {
                let sample = d.centers[i];
                let lo = v3(sample.x, sample.y, if up > 0. { bounds.0[2] } else { z0 });
                let hi = v3(sample.x, sample.y, if up > 0. { z0 } else { bounds.1[2] });
                let mut best = f64::NEG_INFINITY;
                for j in d.candidates(lo, hi) {
                    if up * d.n[j].z <= 0.1
                        || d.tri[j]
                            .iter()
                            .map(|v| up * v.z)
                            .fold(f64::NEG_INFINITY, f64::max)
                            >= q0 - 1e-6
                    {
                        continue;
                    }
                    if let Some(z) = z_in(d.tri[j], sample.x, sample.y) {
                        best = best.max(up * z);
                    }
                }
                if best.is_finite() {
                    gaps.push(q0 - best);
                }
            }
            let max_gap = gaps.iter().copied().fold(f64::NEG_INFINITY, f64::max);
            let min_gap = gaps.iter().copied().fold(f64::INFINITY, f64::min);
            let drop = if gaps.is_empty() {
                format!("open to the bed ({:.1} mm up)", q0 - bed)
            } else {
                format!("drop {min_gap:.1}–{max_gap:.1} mm to material below")
            };
            let w = p.width();
            let c = p.thru();
            out.push(Finding::new(
                "ceiling",
                p.area.sqrt() * if gaps.is_empty() { q0 - bed } else { max_gap },
                format!(
                    "{:.0} mm² flat print-down face at z={z0:.3} · {:.1} × {:.1} mm · {drop}",
                    p.area,
                    w[0].max(w[1]),
                    w[0].min(w[1])
                ),
                vec![face(p.n, c, "face"), click(c)],
                p.f,
            ));
        }
    }
    out
}
fn slopes(d: &Data, up: f64) -> Vec<Finding> {
    let mut out = Vec::new();
    for p in &d.planes {
        if up * p.n.z < -0.80 || up * p.n.z > -0.60 || p.area < 15. || p.soft_frac(d) > 0.75 {
            continue;
        }
        let mut contacts = Vec::new();
        for (&(a, b), &(len, level)) in &d.boundary {
            let other = if a == p.gid {
                Some(b)
            } else if b == p.gid {
                Some(a)
            } else {
                None
            };
            if let Some(i) = other {
                let wall = &d.planes[i];
                if wall.n.z.abs() <= 0.05 && len >= 0.5 {
                    contacts.push((len, level, wall));
                }
            }
        }
        if contacts.iter().any(|t| t.1 >= 0.5) {
            continue;
        }
        let Some((len, _, wall)) = contacts.into_iter().max_by(|a, b| a.0.total_cmp(&b.0)) else {
            continue;
        };
        let h = unit(v3(p.n.x, p.n.y, 0.));
        let w = unit(v3(wall.n.x, wall.n.y, 0.));
        if h.dot(w).abs() > 0.35 {
            continue;
        }
        out.push(Finding::new("slope",p.area,format!("45° underside runs along a wall with no level foot · slope dir {:+.2},{:+.2} vs wall n {:+.2},{:+.2} · along {len:.1} mm · {:.0} mm²",h.x,h.y,w.x,w.y,p.area),vec![face(p.n,p.thru(),"faceA"),face(wall.n,wall.thru(),"faceB"),click(p.thru())],p.f.iter().chain(&wall.f).copied().collect()));
    }
    out
}
fn whole_face(d: &Data, p: &Plane) -> Plane {
    let mut facets = p.f.clone();
    let mut seen = facets.iter().copied().collect::<BTreeSet<_>>();
    let mut at = 0;
    while at < facets.len() {
        for &v in &d.vid[facets[at]] {
            for &i in &d.touch[v] {
                if seen.contains(&i) {
                    continue;
                }
                let Some(other) = d.planes.get(d.gid[i]) else {
                    continue;
                };
                if other.n.dot(p.n) > (2f64.to_radians()).cos()
                    && (other.n.dot(p.thru()) - other.o).abs() < 2. * OFFSET
                {
                    seen.insert(i);
                    facets.push(i);
                }
            }
        }
        at += 1;
    }
    Plane::new(d, p.n, p.o, facets, p.gid)
}
fn ledges(d: &Data, up: f64, tilt: f64) -> Vec<Finding> {
    let (sn, cs) = tilt.to_radians().sin_cos();
    let height = |p: V3| up * (sn * p.y + cs * p.z);
    let bed = d
        .mesh
        .vertices
        .iter()
        .map(|&p| height(point(p)))
        .fold(f64::INFINITY, f64::min);
    let mut out = Vec::new();
    let mut seen = BTreeSet::new();
    for whole in &d.planes {
        let facing = height(whole.n);
        if facing > -(30f64.to_radians()).cos() || whole.soft_frac(d) > 0.75 {
            continue;
        }
        for island in whole.components(d) {
            if island.area >= CEILING_AREA || island.soft_frac(d) > 0.75 {
                continue;
            }
            let touching = d.touching(&island.f);
            if touching.iter().any(|&i| {
                island.f.iter().any(|&j| {
                    let cos = d.n[i].dot(d.n[j]);
                    cos > 0.9063 && cos < (2f64.to_radians()).cos()
                })
            }) {
                continue;
            }
            if d.banded(&island, whole, 1, true) {
                continue;
            }
            let p = whole_face(d, &island);
            let key = *p.f.iter().min().unwrap();
            if !seen.insert(key) || p.area >= CEILING_AREA {
                continue;
            }
            let above =
                p.f.iter()
                    .flat_map(|&i| d.tri[i])
                    .map(height)
                    .fold(f64::INFINITY, f64::min)
                    - bed;
            let w = p.width();
            if above < OFF_BED || p.area / w[0].max(w[1]).max(1e-9) < 0.01 {
                continue;
            }
            let mine = p.f.iter().copied().collect::<BTreeSet<_>>();
            if d.touching(&p.f)
                .into_iter()
                .any(|i| !mine.contains(&i) && d.n[i].dot(p.n) > 0.9063)
            {
                continue;
            }
            let at =
                p.f.iter()
                    .map(|&i| d.centers[i])
                    .min_by(|a, b| {
                        (*a - p.center())
                            .norm()
                            .total_cmp(&(*b - p.center()).norm())
                    })
                    .unwrap();
            out.push(Finding::new("ledge",-p.area,format!("{:.2} mm² flat face {:.0}° off facing the bed · {:.1} × {:.1} mm · {above:.1} mm up",p.area,(-facing).clamp(-1.,1.).acos().to_degrees(),w[0].max(w[1]),w[0].min(w[1])),vec![face(p.n,at,"face"),click(at)],p.f));
        }
    }
    out
}
