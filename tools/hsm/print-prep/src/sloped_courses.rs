//! Cuts the paths a sloped course is laid in: a solid's sections parallel to a face, and each
//! section's rings, narrow strips and fill lines, every path climbing the slope.
//!
//! A region lies in the face's own plane, `a` across the slope and `b` up it, as Clipper2's
//! rings: outer rings anticlockwise and holes clockwise, so the stock is on the left of travel.

use crate::mesh::Mesh;
use anyhow::{Context, Result, ensure};
use clipper2_rust::{ClipType, ClipperD, EndType, FillRule, JoinType, PathD, PathsD, PointD};
use std::collections::{BTreeMap, HashSet};

pub type Point = [f64; 2];

/// The decimal places Clipper2 keeps of every coordinate.
const PRECISION: i32 = 6;
/// The spacing a foot's rings and pieces are resampled at.
const STEP: f64 = 0.35;
/// The spacing a skin's ring halves are resampled at.
const HALF_STEP: f64 = 0.4;
/// How far a path may dip against its climb before it is cut there.
const CLIMB_TOLERANCE: f64 = 0.03;

fn path(points: &[Point]) -> PathD {
    points.iter().map(|p| PointD::new(p[0], p[1])).collect()
}

fn points(path: &PathD) -> Vec<Point> {
    path.iter().map(|p| [p.x, p.y]).collect()
}

fn dist(p: Point, q: Point) -> f64 {
    (q[0] - p[0]).hypot(q[1] - p[1])
}

fn length(line: &[Point]) -> f64 {
    line.windows(2).map(|w| dist(w[0], w[1])).sum()
}

/// Twice the signed area a ring encloses, positive when it runs anticlockwise.
fn twice_area(ring: &[Point]) -> f64 {
    (0..ring.len()).map(|i| {
        let (p, q) = (ring[i], ring[(i + 1) % ring.len()]);
        p[0] * q[1] - q[0] * p[1]
    }).sum()
}

/// Stock in the face's plane.
#[derive(Clone, Debug, Default)]
pub struct Region(PathsD);

impl Region {
    /// The stock a set of rings encloses where their windings do not cancel.
    pub fn from_rings(rings: &[Vec<Point>]) -> Region {
        let paths: PathsD = rings.iter().filter(|r| r.len() >= 3).map(|r| path(r)).collect();
        Region(clipper2_rust::union_subjects_d(&paths, FillRule::NonZero, PRECISION))
    }

    /// An ellipse about the origin with `count` corners.
    pub fn ellipse(ra: f64, rb: f64, count: usize) -> Region {
        let ring: Vec<Point> = (0..count).map(|i| {
            let t = std::f64::consts::TAU * i as f64 / count as f64;
            [ra * t.cos(), rb * t.sin()]
        }).collect();
        Region::from_rings(&[ring])
    }

    pub fn is_empty(&self) -> bool {
        self.0.is_empty()
    }

    /// The region grown by `delta`, or shrunk where `delta` is negative, with round corners.
    pub fn offset(&self, delta: f64) -> Region {
        if self.is_empty() {
            return Region::default();
        }
        Region(clipper2_rust::inflate_paths_d(&self.0, delta, JoinType::Round, EndType::Polygon, 2.0, PRECISION, 0.0))
    }

    pub fn union(&self, other: &Region) -> Region {
        Region(clipper2_rust::union_d(&self.0, &other.0, FillRule::NonZero, PRECISION))
    }

    pub fn minus(&self, other: &Region) -> Region {
        if other.is_empty() {
            return self.clone();
        }
        Region(clipper2_rust::difference_d(&self.0, &other.0, FillRule::NonZero, PRECISION))
    }

    pub fn and(&self, other: &Region) -> Region {
        Region(clipper2_rust::intersect_d(&self.0, &other.0, FillRule::NonZero, PRECISION))
    }

    /// The region at or above `b` on the slope.
    pub fn above(&self, b: f64) -> Region {
        let band = vec![path(&[[-200.0, b], [200.0, b], [200.0, 200.0], [-200.0, 200.0]])];
        Region(clipper2_rust::intersect_d(&self.0, &band, FillRule::NonZero, PRECISION))
    }

    /// Every ring, with the stock on its left.
    pub fn rings(&self) -> Vec<Vec<Point>> {
        self.0.iter().map(points).filter(|r| r.len() >= 3).collect()
    }

    /// The number of separate pieces of stock.
    pub fn pieces(&self) -> usize {
        self.rings().iter().filter(|r| twice_area(r) > 0.0).count()
    }

    /// Each hole, as stock of its own.
    pub fn holes(&self) -> Vec<Region> {
        self.rings().into_iter().filter(|r| twice_area(r) < 0.0).map(|mut r| {
            r.reverse();
            Region::from_rings(&[r])
        }).collect()
    }

    pub fn area(&self) -> f64 {
        self.rings().iter().map(|r| twice_area(r)).sum::<f64>() / 2.0
    }

    pub fn bounds(&self) -> ([f64; 2], [f64; 2]) {
        let mut lo = [f64::INFINITY; 2];
        let mut hi = [f64::NEG_INFINITY; 2];
        for p in self.0.iter().flatten() {
            lo = [lo[0].min(p.x), lo[1].min(p.y)];
            hi = [hi[0].max(p.x), hi[1].max(p.y)];
        }
        (lo, hi)
    }

    /// The parts of the open lines inside the region, or outside it for a difference.
    fn clip_lines(&self, lines: &[Vec<Point>], op: ClipType) -> Vec<Vec<Point>> {
        let mut clipper = ClipperD::new(PRECISION);
        clipper.add_open_subject(&lines.iter().map(|l| path(l)).collect());
        clipper.add_clip(&self.0);
        let (mut closed, mut open) = (PathsD::new(), PathsD::new());
        clipper.execute(op, FillRule::NonZero, &mut closed, Some(&mut open));
        open.iter().map(points).filter(|l| l.len() >= 2).collect()
    }

    /// Whether the point lies in the region.
    pub fn contains(&self, p: Point) -> bool {
        let mut winding = 0;
        for ring in &self.0 {
            for i in 0..ring.len() {
                let (a, b) = (&ring[i], &ring[(i + 1) % ring.len()]);
                let side = (b.x - a.x) * (p[1] - a.y) - (p[0] - a.x) * (b.y - a.y);
                if a.y <= p[1] && b.y > p[1] && side > 0.0 {
                    winding += 1;
                } else if a.y > p[1] && b.y <= p[1] && side < 0.0 {
                    winding -= 1;
                }
            }
        }
        winding != 0
    }

    /// Whether the line lies wholly in the region, its boundary included.
    pub fn covers(&self, line: &[Point]) -> bool {
        self.clip_lines(&[line.to_vec()], ClipType::Difference).iter().map(|l| length(l)).sum::<f64>() < 1e-4
    }
}

/// The solid cut by the plane at height `z`, as rings in its own x and y wound as its faces
/// are: outer rings anticlockwise seen from above.
pub fn section(mesh: &Mesh, z: f64) -> Result<Vec<Vec<Point>>> {
    let above = |i: usize| mesh.vertices[i][2] >= z;
    let key = |u: usize, v: usize| (u.min(v), u.max(v));
    let crossing = |(u, v): (usize, usize)| {
        let (p, q) = (mesh.vertices[u], mesh.vertices[v]);
        let t = (z - p[2]) / (q[2] - p[2]);
        [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t]
    };
    // Each face the plane crosses carries the outline from the edge its winding takes down
    // through the plane to the edge it takes back up, the face beyond that edge onward.
    let mut next: BTreeMap<(usize, usize), (usize, usize)> = BTreeMap::new();
    for f in &mesh.faces {
        let (mut down, mut up) = (None, None);
        for k in 0..3 {
            let (u, v) = (f[k], f[(k + 1) % 3]);
            match (above(u), above(v)) {
                (true, false) => down = Some(key(u, v)),
                (false, true) => up = Some(key(u, v)),
                _ => {}
            }
        }
        if let (Some(d), Some(u)) = (down, up) {
            ensure!(next.insert(d, u).is_none(), "the mesh is not closed where the plane at {z} crosses it");
        }
    }
    let mut seen = HashSet::new();
    let mut rings = Vec::new();
    for &start in next.keys() {
        if seen.contains(&start) {
            continue;
        }
        let mut ring = Vec::new();
        let mut at = start;
        loop {
            seen.insert(at);
            ring.push(crossing(at));
            at = *next.get(&at).context("the section does not close")?;
            if at == start {
                break;
            }
            ensure!(!seen.contains(&at), "the section crosses itself at height {z}");
        }
        rings.push(ring);
    }
    Ok(rings)
}

/// At least `least` points spaced evenly along a path from its first point, no more than `step`
/// apart, and the path's length. A closed path returns to its first point; an open one keeps its
/// last.
fn resample(line: &[Point], closed: bool, step: f64, least: usize) -> (Vec<Point>, f64) {
    let mut path = line.to_vec();
    if closed {
        path.push(line[0]);
    }
    let mut cum = vec![0.0];
    for w in path.windows(2) {
        cum.push(cum.last().unwrap() + dist(w[0], w[1]));
    }
    let total = *cum.last().unwrap();
    let count = ((total / step).ceil() as usize + usize::from(!closed)).max(least);
    let spacing = if closed { total / count as f64 } else { total / (count - 1) as f64 };
    let mut out = Vec::with_capacity(count);
    let mut j = 0;
    for i in 0..count {
        let at = if !closed && i == count - 1 { total } else { i as f64 * spacing };
        while j + 2 < cum.len() && cum[j + 1] < at {
            j += 1;
        }
        let span = cum[j + 1] - cum[j];
        let t = if span > 0.0 { ((at - cum[j]) / span).clamp(0.0, 1.0) } else { 0.0 };
        out.push([path[j][0] + (path[j + 1][0] - path[j][0]) * t, path[j][1] + (path[j + 1][1] - path[j][1]) * t]);
    }
    (out, total)
}

/// The stretch of a line from `start` to `end` along it.
fn substring(line: &[Point], start: f64, end: f64) -> Vec<Point> {
    let mut out: Vec<Point> = Vec::new();
    let mut at = 0.0;
    for w in line.windows(2) {
        let span = dist(w[0], w[1]);
        let (s, e) = (at, at + span);
        at = e;
        if span <= 0.0 || e <= start || s >= end {
            continue;
        }
        let lerp = |t: f64| [w[0][0] + (w[1][0] - w[0][0]) * t, w[0][1] + (w[1][1] - w[0][1]) * t];
        if out.is_empty() {
            out.push(lerp(((start - s) / span).max(0.0)));
        }
        out.push(lerp(((end - s) / span).min(1.0)));
    }
    out
}

/// An open path as pieces that each climb the slope: cut at a low or high point inside it.
pub fn climbing(pts: &[Point], depth: usize) -> Vec<Vec<Point>> {
    if pts.len() < 2 {
        return Vec::new();
    }
    let last = pts.len() - 1;
    let (mut lo, mut hi) = (0, 0);
    for (i, p) in pts.iter().enumerate() {
        if p[1] < pts[lo][1] {
            lo = i;
        }
        if p[1] > pts[hi][1] {
            hi = i;
        }
    }
    let (first_b, last_b) = (pts[0][1], pts[last][1]);
    if depth < 4 {
        if 0 < lo && lo < last && pts[lo][1] < first_b.min(last_b) - CLIMB_TOLERANCE {
            let down: Vec<Point> = pts[..=lo].iter().rev().copied().collect();
            return [climbing(&down, depth + 1), climbing(&pts[lo..], depth + 1)].concat();
        }
        if 0 < hi && hi < last && pts[hi][1] > first_b.max(last_b) + CLIMB_TOLERANCE {
            let back: Vec<Point> = pts[hi..].iter().rev().copied().collect();
            return [climbing(&pts[..=hi], depth + 1), climbing(&back, depth + 1)].concat();
        }
    }
    let mut out = pts.to_vec();
    if last_b < first_b {
        out.reverse();
    }
    vec![out]
}

/// A climbing path with the share of the flow at each of its points.
pub type Piece = (Vec<Point>, Vec<f64>);

/// The rings of `region` as climbing pieces with a flow for every point: first the pieces
/// with the stock uphill of them, then those with it downhill. Where two pieces meet, each
/// runs on past the joint with its flow fading out as the other's fades in, so a joint is a lap
/// and not a butt.
pub fn edge_pieces(region: &Region, taper: f64) -> (Vec<Piece>, Vec<Piece>) {
    let (mut first, mut last) = (Vec::new(), Vec::new());
    for ring in region.rings() {
        let (pts, total) = resample(&ring, true, STEP, 4);
        let n = pts.len();
        if total < 1.5 {
            continue;
        }
        // which way each segment runs across the slope; one straight up or down takes its
        // predecessor's way
        let mut side: Vec<i32> = (0..n).map(|i| {
            let ta = pts[(i + 1) % n][0] - pts[i][0];
            if ta > 1e-9 { 1 } else if ta < -1e-9 { -1 } else { 0 }
        }).collect();
        for i in 0..n {
            if side[i] == 0 {
                let before = side[(i + n - 1) % n];
                side[i] = if before != 0 { before } else { 1 };
            }
        }
        // runs of one way, as [start vertex, vertex count, way]; short runs join the run before
        let mut cuts: Vec<usize> = (0..n).filter(|&i| side[i] != side[(i + n - 1) % n]).collect();
        if cuts.is_empty() {
            cuts.push(0);
        }
        let seglen = total / n as f64;
        let mut merged: Vec<(usize, usize, i32)> = Vec::new();
        for (j, &c) in cuts.iter().enumerate() {
            let end = cuts[(j + 1) % cuts.len()];
            let count = match (end + n - c) % n {
                0 => n,
                k => k,
            };
            match merged.last_mut() {
                Some(run) if count as f64 * seglen < 0.8 => run.1 += count,
                _ => merged.push((c, count, side[c])),
            }
        }
        if merged.len() > 1 && merged[0].1 as f64 * seglen < 0.8 {
            let head = merged.remove(0);
            merged.last_mut().unwrap().1 += head.1;
        }
        // joints: the run boundaries, and a low or high point inside a run
        let mut joints: Vec<(usize, i32)> = Vec::new();
        for &(c, count, s) in &merged {
            let idx: Vec<usize> = (0..=count).map(|i| (c + i) % n).collect();
            let b: Vec<f64> = idx.iter().map(|&i| pts[i][1]).collect();
            let mut inner = vec![idx[0]];
            split_run(&b, &idx, 0, count, 0, &mut inner);
            joints.extend(inner.into_iter().map(|v| (v, s)));
        }
        if joints.len() < 2 {
            joints = vec![(0, 1), (n / 2, -1)];
        }
        let doubled: Vec<Point> = pts.iter().chain(&pts).chain(&pts).chain(&pts[..1]).copied().collect();
        for (j, &(v, s)) in joints.iter().enumerate() {
            let v2 = joints[(j + 1) % joints.len()].0;
            let sa = v as f64 * seglen;
            let mut sb = v2 as f64 * seglen;
            if sb <= sa {
                sb += total;
            }
            let span = sb - sa;
            if span < 0.4 {
                continue;
            }
            let fade = taper.min(0.3 * span);
            let (mut p, plen) = resample(&substring(&doubled, total + sa - fade, total + sb + fade), false, STEP, 2);
            let count = p.len();
            let at: Vec<f64> = (0..count).map(|i| plen * i as f64 / (count - 1) as f64).collect();
            let mut flows: Vec<f64> = at.iter().map(|&t| (t / (2.0 * fade)).min((plen - t) / (2.0 * fade)).clamp(0.0, 1.0)).collect();
            let core: Vec<Point> = p.iter().zip(&at).filter(|(_, t)| **t >= fade && **t <= plen - fade).map(|(q, _)| *q).collect();
            if core.len() >= 2 && core[core.len() - 1][1] < core[0][1] {
                p.reverse();
                flows.reverse();
            }
            if s > 0 { first.push((p, flows)) } else { last.push((p, flows)) }
        }
    }
    (first, last)
}

/// A ring as its two halves, each from the ring's lowest point up to its highest, the second
/// starting a little above the low point so the halves lap there without doubling, and each
/// stopping short of the top.
pub fn uphill_halves(ring: &[Point]) -> Vec<Vec<Point>> {
    const TRIM_TOP: f64 = 0.1;
    const TRIM_LOW: f64 = 0.25;
    let (pts, _) = resample(ring, true, HALF_STEP, 8);
    let n = pts.len();
    let (mut lo, mut hi) = (0, 0);
    for (i, p) in pts.iter().enumerate() {
        if p[1] < pts[lo][1] {
            lo = i;
        }
        if p[1] > pts[hi][1] {
            hi = i;
        }
    }
    let forward: Vec<Point> = (0..=(hi + n - lo) % n).map(|i| pts[(lo + i) % n]).collect();
    let backward: Vec<Point> = (0..=(lo + n - hi) % n).map(|i| pts[(lo + n - i) % n]).collect();
    let mut halves = Vec::new();
    for (k, half) in [forward, backward].into_iter().enumerate() {
        if half.len() < 2 {
            continue;
        }
        let span = length(&half);
        let start = if k == 1 { TRIM_LOW } else { 0.0 };
        if span - TRIM_TOP - start >= 0.5 {
            halves.push(substring(&half, start, span - TRIM_TOP));
        }
    }
    halves
}

/// Cuts a run at its low or high points, nearest first, into `inner`.
fn split_run(b: &[f64], idx: &[usize], lo: usize, hi: usize, depth: usize, inner: &mut Vec<usize>) {
    if hi - lo < 3 || depth > 3 {
        return;
    }
    let (mut kmin, mut kmax) = (lo, lo);
    for k in lo..=hi {
        if b[k] < b[kmin] {
            kmin = k;
        }
        if b[k] > b[kmax] {
            kmax = k;
        }
    }
    if lo < kmin && kmin < hi && b[kmin] < b[lo].min(b[hi]) - CLIMB_TOLERANCE {
        split_run(b, idx, lo, kmin, depth + 1, inner);
        inner.push(idx[kmin]);
        split_run(b, idx, kmin, hi, depth + 1, inner);
    } else if lo < kmax && kmax < hi && b[kmax] > b[lo].max(b[hi]) + CLIMB_TOLERANCE {
        split_run(b, idx, lo, kmax, depth + 1, inner);
        inner.push(idx[kmax]);
        split_run(b, idx, kmax, hi, depth + 1, inner);
    }
}

/// Lines that meet end to end, joined into one.
fn merge_lines(mut pieces: Vec<Vec<Point>>) -> Vec<Vec<Point>> {
    let meet = |p: Point, q: Point| dist(p, q) < 1e-5;
    let mut out = Vec::new();
    while let Some(mut line) = pieces.pop() {
        while let Some(i) = pieces.iter().position(|o| {
            let (a, z) = (o[0], o[o.len() - 1]);
            meet(a, line[line.len() - 1]) || meet(z, line[line.len() - 1]) || meet(a, line[0]) || meet(z, line[0])
        }) {
            let mut other = pieces.swap_remove(i);
            let end = line[line.len() - 1];
            if meet(other[0], end) {
                line.extend_from_slice(&other[1..]);
            } else if meet(other[other.len() - 1], end) {
                other.reverse();
                line.extend_from_slice(&other[1..]);
            } else {
                if meet(other[0], line[0]) {
                    other.reverse();
                }
                other.extend_from_slice(&line[1..]);
                line = other;
            }
        }
        out.push(line);
    }
    out
}

/// Rings for the strips of `region` too narrow for its fill, lowest first.
pub fn narrow_pieces(region: &Region, width: f64, pitch: f64, fill: &Region) -> Vec<Piece> {
    let inside = region.offset(-(width - 0.02));
    let rest = if fill.is_empty() { inside } else { inside.minus(&fill.offset(pitch * 0.55)) };
    let rest = rest.offset(-0.06).offset(0.06);
    if rest.is_empty() {
        return Vec::new();
    }
    let reach = rest.offset(pitch * 0.5);
    let mut out: Vec<Piece> = Vec::new();
    for level in 1..=8 {
        let ring_stock = region.offset(-(width / 2.0 + level as f64 * pitch));
        if ring_stock.is_empty() {
            break;
        }
        for ring in ring_stock.rings() {
            let mut closed = ring.clone();
            closed.push(ring[0]);
            for piece in merge_lines(reach.clip_lines(&[closed], ClipType::Intersection)) {
                if length(&piece) < 0.8 {
                    continue;
                }
                let (p, _) = resample(&piece, false, STEP, 2);
                for part in climbing(&p, 0) {
                    if part.len() >= 2 && length(&part) >= 0.6 {
                        let flows = vec![1.0; part.len()];
                        out.push((part, flows));
                    }
                }
            }
        }
    }
    let mean = |p: &[Point]| p.iter().map(|q| q[1]).sum::<f64>() / p.len() as f64;
    out.sort_by(|x, y| mean(&x.0).total_cmp(&mean(&y.0)));
    out
}

/// Rows of straight lines across `region` at `angle` degrees from the `a` axis, `pitch` apart,
/// each line running along the angle. The rows never run down the slope.
pub fn hatch(region: &Region, angle: f64, pitch: f64, shortest: f64) -> Vec<Vec<(Point, Point)>> {
    if region.is_empty() {
        return Vec::new();
    }
    let (s, c) = angle.to_radians().sin_cos();
    let (d, nrm) = ([c, s], [-s, c]);
    let (lo, hi) = region.bounds();
    let offsets = [lo, [lo[0], hi[1]], [hi[0], lo[1]], hi].map(|p| p[0] * nrm[0] + p[1] * nrm[1]);
    let k0 = (offsets.iter().copied().fold(f64::INFINITY, f64::min) / pitch).floor() as i64 - 1;
    let k1 = (offsets.iter().copied().fold(f64::NEG_INFINITY, f64::max) / pitch).ceil() as i64 + 1;
    let offset = |k: i64| (k as f64 + 0.5) * pitch;
    let lines: Vec<Vec<Point>> = (k0..=k1).map(|k| {
        let o = offset(k);
        [-300.0, 300.0].map(|t| [o * nrm[0] + t * d[0], o * nrm[1] + t * d[1]]).to_vec()
    }).collect();
    let along = |p: Point| p[0] * d[0] + p[1] * d[1];
    let mut spans: BTreeMap<i64, Vec<(f64, f64)>> = BTreeMap::new();
    for piece in region.clip_lines(&lines, ClipType::Intersection) {
        let (p, q) = (piece[0], piece[piece.len() - 1]);
        let k = (((p[0] + q[0]) / 2.0 * nrm[0] + (p[1] + q[1]) / 2.0 * nrm[1]) / pitch - 0.5).round() as i64;
        let (t0, t1) = (along(p), along(q));
        spans.entry(k).or_default().push((t0.min(t1), t0.max(t1)));
    }
    let mut rows = Vec::new();
    for (k, mut row) in spans {
        row.sort_by(|x, y| x.0.total_cmp(&y.0));
        let mut joined: Vec<(f64, f64)> = Vec::new();
        for (t0, t1) in row {
            match joined.last_mut() {
                Some(last) if t0 - last.1 < 1e-5 => last.1 = last.1.max(t1),
                _ => joined.push((t0, t1)),
            }
        }
        let o = offset(k);
        let at = |t: f64| [o * nrm[0] + t * d[0], o * nrm[1] + t * d[1]];
        let pieces: Vec<(Point, Point)> = joined.into_iter().filter(|(t0, t1)| t1 - t0 >= shortest).map(|(t0, t1)| (at(t0), at(t1))).collect();
        if !pieces.is_empty() {
            rows.push(pieces);
        }
    }
    if nrm[1] < -1e-9 {
        rows.reverse();
    }
    rows
}

/// Level lines in an order that lays every line after the lines just downhill of it, taking
/// the nearest such line each time, so a strip beside an opening is finished before crossing.
pub fn level_order(rows: &[Vec<(Point, Point)>]) -> Vec<(Point, Point)> {
    let mut items: Vec<(usize, Point, Point)> = Vec::new();
    for (r, pieces) in rows.iter().enumerate() {
        for &(a, b) in pieces {
            items.push(if a[0] <= b[0] { (r, a, b) } else { (r, b, a) });
        }
    }
    let needs: Vec<Vec<usize>> = items.iter().map(|&(r, lo, hi)| {
        (0..items.len()).filter(|&j| {
            let (rj, ljo, ljh) = items[j];
            r >= 1 && rj == r - 1 && ljo[0] < hi[0] + 0.3 && ljh[0] > lo[0] - 0.3
        }).collect()
    }).collect();
    let mut done = vec![false; items.len()];
    let mut out = Vec::with_capacity(items.len());
    let mut pos: Option<Point> = None;
    for _ in 0..items.len() {
        let mut best: Option<(f64, usize, Point, Point)> = None;
        for (i, &(r, lo, hi)) in items.iter().enumerate() {
            if done[i] || needs[i].iter().any(|&q| !done[q]) {
                continue;
            }
            for (a, b) in [(lo, hi), (hi, lo)] {
                let cost = r as f64 * 1e-3 + pos.map_or(0.0, |p| dist(p, a));
                if best.is_none_or(|x| cost < x.0) {
                    best = Some((cost, i, a, b));
                }
            }
        }
        let Some((_, i, a, b)) = best else { break };
        done[i] = true;
        out.push((a, b));
        pos = Some(b);
    }
    out
}
