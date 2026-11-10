//! The clamping bands follow convex head sections of the pinned scan envelope.
use anyhow::{Result, ensure};
use hsm_kernel::{V2, v2};
use hsm_pgfun_positioner::{Design, SCAN, load_meshes};
use std::{
    f64::consts::{FRAC_PI_2, PI, TAU},
    path::Path,
};

pub struct Contact {
    pub x: f64,
    pub outer: Vec<V2>,
    pub inner: Vec<V2>,
}

pub fn contacts(root: &Path, design: &Design) -> Result<Vec<Contact>> {
    let source = load_meshes(root.join(SCAN))?;
    let housing = &source["housing"].vertices;
    design
        .cradle_bands_x
        .iter()
        .map(|&x| {
            let points: Vec<_> = housing
                .iter()
                .filter(|p| (p[0] - x).abs() <= 8.1 && p[2] > -24.)
                .map(|p| v2(p[1], p[2]))
                .collect();
            let boundary = hull(&points);
            ensure!(boundary.len() >= 3, "no head section at the clamping band");
            let outer = simplify(
                &buffer(&boundary, design.contact_clearance + design.liner_thickness),
                0.12,
            );
            let inner = inset(&outer, design.liner_thickness);
            Ok(Contact { x, outer, inner })
        })
        .collect()
}

/// A convex contour, clockwise from its lowest point, as the source envelope is wound.
pub fn hull(points: &[V2]) -> Vec<V2> {
    let mut p = points.to_vec();
    p.sort_by(|a, b| a.x.total_cmp(&b.x).then(a.y.total_cmp(&b.y)));
    p.dedup();
    if p.len() < 3 {
        return p;
    }
    let mut low: Vec<V2> = vec![];
    for &point in &p {
        while low.len() > 1
            && (low[low.len() - 1] - low[low.len() - 2]).cross(point - low[low.len() - 1]) <= 0.
        {
            low.pop();
        }
        low.push(point);
    }
    let mut high: Vec<V2> = vec![];
    for &point in p.iter().rev() {
        while high.len() > 1
            && (high[high.len() - 1] - high[high.len() - 2]).cross(point - high[high.len() - 1])
                <= 0.
        {
            high.pop();
        }
        high.push(point);
    }
    low.pop();
    high.pop();
    low.extend(high);
    low.reverse();
    let first = (0..low.len())
        .min_by(|&a, &b| {
            low[a]
                .y
                .total_cmp(&low[b].y)
                .then(low[a].x.total_cmp(&low[b].x))
        })
        .unwrap();
    low.rotate_left(first);
    low
}

/// The received contour's rounded outward allowance at its authored buffer resolution.
fn buffer(p: &[V2], distance: f64) -> Vec<V2> {
    let mut out = vec![];
    for i in 0..p.len() {
        let a = (p[i] - p[(i + p.len() - 1) % p.len()]).unit().perp();
        let b = (p[(i + 1) % p.len()] - p[i]).unit().perp();
        let angle_a = a.y.atan2(a.x);
        let mut sweep = b.y.atan2(b.x) - angle_a;
        while sweep > 0. {
            sweep -= TAU;
        }
        while sweep < -PI {
            sweep += TAU;
        }
        let count = ((sweep.abs() / (FRAC_PI_2 / 3.) + 0.5) as usize).max(1);
        for j in 0..=count {
            let angle = angle_a + sweep * j as f64 / count as f64;
            out.push(p[i] + v2(angle.cos(), angle.sin()) * distance);
        }
    }
    out
}

fn segment_distance(p: V2, a: V2, b: V2) -> f64 {
    let direction = b - a;
    if direction.dot(direction) == 0. {
        return (p - a).norm();
    }
    let parameter = ((p - a).dot(direction) / direction.dot(direction)).clamp(0., 1.);
    (p - (a + direction * parameter)).norm()
}

fn simplify(p: &[V2], tolerance: f64) -> Vec<V2> {
    fn section(p: &[V2], a: usize, b: usize, tolerance: f64, keep: &mut [bool]) {
        if b <= a + 1 {
            return;
        }
        let (at, distance) = (a + 1..b)
            .map(|i| (i, segment_distance(p[i], p[a], p[b])))
            .max_by(|a, b| a.1.total_cmp(&b.1).then(b.0.cmp(&a.0)))
            .unwrap();
        if distance <= tolerance {
            for value in &mut keep[a + 1..b] {
                *value = false;
            }
        } else {
            section(p, a, at, tolerance, keep);
            section(p, at, b, tolerance, keep);
        }
    }
    let mut closed = p.to_vec();
    closed.push(p[0]);
    let mut keep = vec![true; closed.len()];
    section(&closed, 0, closed.len() - 1, tolerance, &mut keep);
    let mut out: Vec<_> = closed
        .into_iter()
        .zip(keep)
        .filter_map(|(p, k)| k.then_some(p))
        .collect();
    out.pop();
    if out.len() > 3 && segment_distance(out[0], out[out.len() - 1], out[1]) <= tolerance {
        out.remove(0);
    }
    out
}

/// An inward offset of a convex polygon joins adjacent straight carriers at their crossing.
fn inset(p: &[V2], distance: f64) -> Vec<V2> {
    (0..p.len())
        .map(|i| {
            let (previous, here, next) =
                (p[(i + p.len() - 1) % p.len()], p[i], p[(i + 1) % p.len()]);
            let (a, b) = ((here - previous).unit(), (next - here).unit());
            let normal_a = a.perp();
            let normal_b = b.perp();
            let at = here - normal_a * distance;
            let next_at = here - normal_b * distance;
            let t = (next_at - at).cross(b) / a.cross(b);
            at + a * t
        })
        .collect()
}
