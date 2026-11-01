//! Sweeps and lofts.
//!
//! A sweep carries a profile along a path of lines, arcs and curves through points in a
//! rotation-minimizing frame (the double-reflection method), one copy of the profile per path
//! point. An arc is cut into points by the rule at its radius plus the profile's reach from the
//! path's start, so the outermost fiber of a bend holds the rule, and a curve where its turn at
//! that radius uses the rule up (`spline`). The walls a curve carries a profile edge over are one
//! free surface.
//!
//! A loft rules consecutive sections edge by edge: the point a share t along one section's edge
//! meets the point the same share along the next section's — its length on a line, its angle on
//! an arc, its parameter on a free curve. Each band is cut along its rulings where its normal
//! turns and across them where it twists, until it lies within the rule of the ruled surface.
//!
//! A wall is recorded on the surface it lies on — a plane, a cylinder, a cone or a torus — when
//! every vertex of it, and every ruling of a loft band, lies on that surface; otherwise it is a
//! free surface.
use crate::build::{Part, cleaned, orient};
use crate::face::{Face, Src, Surface, SurfaceKey};
use crate::mass::signed_volume;
use crate::math::{TAU, V2, V3, acos, atan2, cos, sin, v2, v3};
use crate::plane::Plane;
use crate::profile::{Curve, Profile, RLoop, Region};
use crate::rule::{ANGULAR, LINEAR, canonical_axis, plane_frame, ring_count_at};
use crate::solid::Solid;
use crate::spline::Spline;
use crate::triangulate::triangulate;
use anyhow::{Result, ensure};
use std::collections::HashMap;
use std::panic::Location;

/// One leg of a sweep path.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Leg {
    Line { a: V3, b: V3 },
    /// From `a` to `b` about the axis through `c` along unit `d`, `turn` radians counterclockwise
    /// about `d`.
    Arc { a: V3, b: V3, c: V3, d: V3, turn: f64 },
    /// From `a` to `b` along the path's curve `k`.
    Curve { a: V3, b: V3, k: usize },
}

/// `v` turned `angle` radians counterclockwise about the unit axis `d`.
fn rotate(v: V3, d: V3, angle: f64) -> V3 {
    let (s, c) = (sin(angle), cos(angle));
    v * c + d.cross(v) * s + d * (d.dot(v) * (1.0 - c))
}

impl Leg {
    pub fn start(&self) -> V3 {
        match *self {
            Leg::Line { a, .. } | Leg::Arc { a, .. } | Leg::Curve { a, .. } => a,
        }
    }

    pub fn end(&self) -> V3 {
        match *self {
            Leg::Line { b, .. } | Leg::Arc { b, .. } | Leg::Curve { b, .. } => b,
        }
    }

    /// The point a share `s` along the leg: of its length on a line, of its turn on an arc.
    fn point(&self, s: f64) -> V3 {
        match *self {
            Leg::Line { a, b } => {
                if s >= 1.0 {
                    b
                } else {
                    a + (b - a) * s
                }
            }
            Leg::Arc { a, b, c, d, turn } => {
                if s <= 0.0 {
                    a
                } else if s >= 1.0 {
                    b
                } else {
                    c + rotate(a - c, d, turn * s)
                }
            }
            Leg::Curve { .. } => unreachable!("a curve leg is cut by its curve"),
        }
    }

    /// The direction of travel a share `s` along the leg.
    fn tangent(&self, s: f64) -> V3 {
        match *self {
            Leg::Line { a, b } => (b - a).unit(),
            Leg::Arc { a, c, d, turn, .. } => d.cross(rotate(a - c, d, turn * s)).unit(),
            Leg::Curve { .. } => unreachable!("a curve leg is cut by its curve"),
        }
    }
}

/// A sweep path: legs end to end from a start point.
#[derive(Clone, Debug, PartialEq)]
pub struct Path {
    pub legs: Vec<Leg>,
    pub curves: Vec<Spline>,
    at: V3,
}

/// The arc from `a` to `b` about `c`, counterclockwise about `d`; a whole turn when `b` is `a`.
fn arc(a: V3, b: V3, c: V3, d: V3) -> Leg {
    let (u, v) = (a - c, b - c);
    let mut turn = atan2(u.cross(v).dot(d), u.dot(v));
    if turn <= 1e-12 {
        turn += TAU;
    }
    Leg::Arc { a, b, c, d, turn }
}

impl Path {
    pub fn new(start: V3) -> Path {
        Path { legs: vec![], curves: vec![], at: start }
    }

    /// Where the path ends so far.
    pub fn at(&self) -> V3 {
        self.at
    }

    pub fn line_to(mut self, p: V3) -> Path {
        self.legs.push(Leg::Line { a: self.at, b: p });
        self.at = p;
        self
    }

    /// The arc from the path's end through `mid` to `end`.
    pub fn arc_through(mut self, mid: V3, end: V3) -> Result<Path> {
        let a = self.at;
        let (u, v) = (mid - a, end - a);
        let w = u.cross(v);
        ensure!(w.norm() > 1e-12 * u.norm() * v.norm(), "an arc through three points on a line");
        let c = a + (v * u.norm2() - u * v.norm2()).cross(w) / (2.0 * w.norm2());
        self.legs.push(arc(a, end, c, (mid - a).cross(end - mid).unit()));
        self.at = end;
        Ok(self)
    }

    /// The arc from the path's end about the center `c` to `end`, counterclockwise about `axis`.
    pub fn arc_center(mut self, c: V3, end: V3, axis: V3) -> Result<Path> {
        let (a, d) = (self.at, axis.unit());
        let (ra, rb) = ((a - c).norm(), (end - c).norm());
        ensure!(ra > 1e-9 && (ra - rb).abs() <= 1e-9 * ra.max(1.0), "an arc from radius {ra} to radius {rb}");
        ensure!(
            (a - c).dot(d).abs() <= 1e-9 * ra.max(1.0) && (end - c).dot(d).abs() <= 1e-9 * ra.max(1.0),
            "an arc whose ends are off the plane square to its axis"
        );
        self.legs.push(arc(a, end, c, d));
        self.at = end;
        Ok(self)
    }

    /// The curve from the path's end through `points`, whose first is that end
    /// (`Spline::through`).
    pub fn spline_through(self, points: &[V3]) -> Result<Path> {
        ensure!(
            points.first().is_some_and(|&p| (p - self.at).norm() < 1e-7),
            "a spline that does not start where the path ends"
        );
        let mut pts = points.to_vec();
        pts[0] = self.at;
        Ok(self.curve(Spline::through(&pts)?))
    }

    /// The cubic from the path's end to `end`, leaving along `t0` and arriving along `t1`
    /// (`Spline::hermite`).
    pub fn spline_to(self, end: V3, t0: V3, t1: V3) -> Result<Path> {
        let curve = Spline::hermite(self.at, end, t0, t1)?;
        Ok(self.curve(curve))
    }

    /// A Bézier whose first control point is the path's end (`Spline::bezier`).
    pub fn bezier(self, points: &[V3]) -> Result<Path> {
        ensure!(points.first().is_some_and(|&p| (p - self.at).norm() < 1e-7),
                "a Bézier that does not start where the path ends");
        let mut points = points.to_vec();
        points[0] = self.at;
        Ok(self.curve(Spline::bezier(&points)?))
    }

    fn curve(mut self, curve: Spline) -> Path {
        let (a, b) = (self.at, curve.end());
        self.legs.push(Leg::Curve { a, b, k: self.curves.len() });
        self.curves.push(curve);
        self.at = b;
        self
    }
}

/// Points along a path with the direction of travel at each, and the leg each band between
/// consecutive points lies on. Where two legs meet, one point stands for both, its direction
/// halfway between theirs.
struct Track {
    p: Vec<V3>,
    t: Vec<V3>,
    band: Vec<usize>,
}

/// An arc cut by the rule at its radius plus `reach`.
fn track(path: &Path, reach: f64, linear: f64) -> Track {
    let (mut p, mut t, mut leg): (Vec<V3>, Vec<V3>, Vec<usize>) = (vec![], vec![], vec![]);
    for (e, l) in path.legs.iter().enumerate() {
        let (mut lp, mut lt): (Vec<V3>, Vec<V3>) = match *l {
            Leg::Curve { k, .. } => if linear == LINEAR {
                path.curves[k].track(reach)
            } else {
                path.curves[k].track_at(reach, linear)
            },
            _ => {
                let n = match *l {
                    Leg::Arc { a, c, turn, .. } => {
                        ((ring_count_at((a - c).norm() + reach, linear) as f64 * turn / TAU - 1e-9).ceil() as usize).max(1)
                    }
                    _ => 1,
                };
                (0..=n).map(|i| (l.point(i as f64 / n as f64), l.tangent(i as f64 / n as f64))).unzip()
            }
        };
        if let (Some(&last), Some(joint)) = (p.last(), t.last_mut()) {
            if (last - lp[0]).norm() < 1e-7 {
                *joint = (*joint + lt[0]).unit();
                lp.remove(0);
                lt.remove(0);
            }
        }
        leg.extend(std::iter::repeat_n(e, lp.len()));
        p.extend(lp);
        t.extend(lt);
    }
    let band = if leg.len() > 1 { leg[1..].to_vec() } else { leg };
    Track { p, t, band }
}

/// Rotation-minimizing frames along the points: the first normal square to the first direction,
/// each next one carried by two reflections (Wang, Jüttler, Zheng and Liu's double reflection).
fn frames(p: &[V3], t: &[V3]) -> Vec<V3> {
    let t0 = t[0];
    let mut r = vec![(if t0.z.abs() < 0.9 { t0.cross(V3::Z) } else { t0.cross(V3::X) }).unit()];
    for i in 0..p.len() - 1 {
        let v1 = p[i + 1] - p[i];
        let c1 = v1.dot(v1);
        let rl = r[i] - v1 * (2.0 / c1 * v1.dot(r[i]));
        let tl = t[i] - v1 * (2.0 / c1 * v1.dot(t[i]));
        let v2 = t[i + 1] - tl;
        let c2 = v2.dot(v2);
        r.push(if c2 > 1e-30 { rl - v2 * (2.0 / c2 * v2.dot(rl)) } else { rl });
    }
    r
}

/// The unit normal a closed polygon winds counterclockwise about.
fn newell(p: &[V3]) -> V3 {
    let c = p.iter().fold(V3::ZERO, |s, &q| s + q) / p.len() as f64;
    let mut n = V3::ZERO;
    for i in 0..p.len() {
        n += (p[i] - c).cross(p[(i + 1) % p.len()] - c);
    }
    n.unit()
}

/// A plane face record capping one end, across all of `rings` (the outer first) at once.
fn cap(rings: &[&[V3]], ids: &[Vec<u32>], outward_of: f64, src: Src, op: &'static str, part: &mut Part) -> Result<()> {
    let mut nrm = newell(rings[0]);
    let (_, x, y) = plane_frame(nrm);
    let flat: Vec<Vec<V2>> = rings.iter().map(|r| r.iter().map(|p| v2(p.dot(x), p.dot(y))).collect()).collect();
    let glob: Vec<u32> = ids.concat();
    let flip = outward_of < 0.0;
    if flip {
        nrm = -nrm;
    }
    part.faces.push(Face::new(Surface::Plane { p: rings[0][0], n: nrm }, op, src));
    let f = part.faces.len() as u32 - 1;
    for t in triangulate(&flat)? {
        let g = [glob[t[0] as usize], glob[t[1] as usize], glob[t[2] as usize]];
        part.tris.push(if flip { [g[0], g[2], g[1]] } else { g });
        part.fids.push(f);
    }
    Ok(())
}

/// Every triangle turned around when the part is inside out, and its planes with them.
fn outward(part: &mut Part) {
    if signed_volume(&part.verts, &part.tris) < 0.0 {
        for t in &mut part.tris {
            t.swap(1, 2);
        }
        for f in &mut part.faces {
            if let Surface::Plane { n, .. } = &mut f.surface {
                *n = -*n;
            }
        }
    }
}

/// Per face record, its vertices and the sum of its triangles' area vectors.
fn record_points(part: &Part) -> (Vec<Vec<u32>>, Vec<V3>) {
    let mut pts = vec![vec![]; part.faces.len()];
    let mut area = vec![V3::ZERO; part.faces.len()];
    for (t, &f) in part.tris.iter().zip(&part.fids) {
        pts[f as usize].extend_from_slice(t);
        let (a, b, c) = (part.verts[t[0] as usize], part.verts[t[1] as usize], part.verts[t[2] as usize]);
        area[f as usize] += (b - a).cross(c - a);
    }
    for p in &mut pts {
        p.sort_unstable();
        p.dedup();
    }
    (pts, area)
}

/// Whether every point lies on the surface.
fn holds(s: &Surface, pts: impl IntoIterator<Item = V3>) -> bool {
    pts.into_iter().all(|q| s.distance(q).is_some_and(|d| d.abs() <= 1e-6))
}

/// The plane through a face's vertices, facing the way its triangles do.
fn plane_of(verts: &[V3], ids: &[u32], area: V3) -> Option<Surface> {
    (area.norm() > 1e-12).then(|| Surface::Plane { p: verts[ids[0] as usize], n: area.unit() })
}

/// The surface a profile line turned about the axis through `c` along `d` sweeps: a plane, a
/// cylinder or a cone when the line and the axis lie in one plane.
fn turned_line(verts: &[V3], ids: &[u32], c: V3, d: V3, area: V3) -> Option<Surface> {
    let hr = |i: u32| {
        let v = verts[i as usize] - c;
        (v.dot(d), v.reject(d).norm())
    };
    let (h0, r0) = hr(ids[0]);
    let far = ids.iter().map(|&i| hr(i)).max_by(|a, b| (a.0 - h0).abs().total_cmp(&(b.0 - h0).abs()))?;
    if (far.0 - h0).abs() <= 1e-9 {
        return plane_of(verts, ids, area);
    }
    let slope = (far.1 - r0) / (far.0 - h0);
    Some(if slope.abs() <= 1e-12 {
        Surface::Cylinder { p: c, d: canonical_axis(d), r: r0 }
    } else {
        Surface::Cone { p: c + d * h0, d, r: r0, slope }
    })
}

/// One record for the faces of one builder call that lie on one surface, a plane's taking its
/// sense too.
fn merged(part: Part) -> Part {
    let mut first: HashMap<(SurfaceKey, bool), u32> = HashMap::new();
    let mut faces = vec![];
    let map: Vec<u32> = part
        .faces
        .iter()
        .map(|f| {
            let mut push = || {
                faces.push(*f);
                faces.len() as u32 - 1
            };
            match f.surface.key() {
                Some(k) => *first.entry((k, f.surface.sense())).or_insert_with(push),
                None => push(),
            }
        })
        .collect();
    Part { fids: part.fids.iter().map(|&f| map[f as usize]).collect(), faces, ..part }
}

/// `region` carried along `path`; capped at both ends unless the path closes on itself.
pub(crate) fn sweep(region: &Region, path: &Path, src: Src, op: &'static str) -> Result<Part> {
    sweep_at(region, path, src, op, LINEAR)
}

fn sweep_at(region: &Region, path: &Path, src: Src, op: &'static str, linear: f64) -> Result<Part> {
    ensure!(!path.legs.is_empty(), "a {op} along no path");
    let loops = cleaned(region)?;
    let normal = newell(&loops[0].pts);
    let start = path.legs[0].start();
    let reach = loops[0].pts.iter().map(|&q| (q - start).norm()).fold(0.0, f64::max);
    let Track { mut p, mut t, band } = track(path, reach, linear);
    let lean = t[0].dot(normal);
    ensure!(lean.abs() > 1e-9, "a {op} whose profile's plane holds the path's first direction");
    let (loops, _) = orient(&loops, if lean > 0.0 { normal } else { -normal });
    let closed = p.len() > 2 && (p[0] - p[p.len() - 1]).norm() < 1e-7;
    if closed {
        p.pop();
        t.pop();
    }
    let r = frames(&p, &t);
    let (t0, r0) = (t[0], r[0]);
    let s0 = t0.cross(r0);
    let local = |q: V3| {
        let d = q - p[0];
        v3(d.dot(t0), d.dot(r0), d.dot(s0))
    };
    let place = |i: usize, l: V3| p[i] + t[i] * l.x + r[i] * l.y + t[i].cross(r[i]) * l.z;
    let ns = p.len();
    let nb = if closed { ns } else { ns - 1 };
    let mut part = Part { verts: vec![], tris: vec![], fids: vec![], faces: vec![] };
    let mut whose: Vec<(usize, u32)> = vec![];
    let mut ids: Vec<Vec<Vec<u32>>> = vec![];
    for lp in &loops {
        let m = lp.pts.len() as u32;
        let ls: Vec<V3> = lp.pts.iter().map(|&q| local(q)).collect();
        let base = part.verts.len() as u32;
        part.verts.extend_from_slice(&lp.pts);
        for i in 1..ns {
            part.verts.extend(ls.iter().map(|&q| place(i, q)));
        }
        ids.push((0..ns as u32).map(|i| (0..m).map(|k| base + i * m + k).collect()).collect());
        let mut record: HashMap<(usize, u32), u32> = HashMap::new();
        for i in 0..nb {
            let (a0, b0) = (base + i as u32 * m, base + ((i + 1) % ns) as u32 * m);
            let wall = match path.legs[band[i]] {
                Leg::Curve { .. } => ns + band[i],
                _ => i,
            };
            for k in 0..m {
                let k1 = (k + 1) % m;
                let curve = lp.seg[k as usize];
                let f = *record.entry((wall, curve)).or_insert_with(|| {
                    part.faces.push(Face::new(Surface::Free { kind: "BSPLINE" }, op, src));
                    whose.push((i, curve));
                    part.faces.len() as u32 - 1
                });
                part.tris.push([a0 + k, a0 + k1, b0 + k1]);
                part.tris.push([a0 + k, b0 + k1, b0 + k]);
                part.fids.extend([f, f]);
            }
        }
    }
    if !closed {
        for (i, sense) in [(0, -1.0), (ns - 1, 1.0)] {
            let rings: Vec<Vec<V3>> = ids.iter().map(|l| l[i].iter().map(|&k| part.verts[k as usize]).collect()).collect();
            let refs: Vec<&[V3]> = rings.iter().map(Vec::as_slice).collect();
            let at: Vec<Vec<u32>> = ids.iter().map(|l| l[i].clone()).collect();
            let along = newell(&rings[0]).dot(t[i]) * sense;
            cap(&refs, &at, along, src, op, &mut part)?;
        }
    }
    outward(&mut part);
    let (pts, area) = record_points(&part);
    for (f, &(i, curve)) in whose.iter().enumerate() {
        let leg = path.legs[band[i]];
        let surface = match (region.curves[curve as usize], leg) {
            (Curve::Line, Leg::Line { .. }) => plane_of(&part.verts, &pts[f], area[f]),
            (Curve::Line, Leg::Arc { c, d, .. }) => turned_line(&part.verts, &pts[f], c, d, area[f]),
            (Curve::Circle { c: cc, axis, r: cr }, _) if canonical_axis(axis).cross(t0).norm() < 1e-9 => {
                let q = place(i, local(cc));
                match leg {
                    Leg::Line { a, b } => Some(Surface::Cylinder { p: q, d: canonical_axis(b - a), r: cr }),
                    Leg::Arc { c, d, .. } => Some(Surface::Torus {
                        c: c + d * (q - c).dot(d),
                        d,
                        major: (q - c).reject(d).norm(),
                        minor: cr,
                    }),
                    Leg::Curve { .. } => None,
                }
            }
            _ => None,
        };
        if let Some(s) = surface.filter(|s| holds(s, pts[f].iter().map(|&k| part.verts[k as usize]))) {
            part.faces[f].surface = s;
        }
    }
    Ok(merged(part))
}

/// One edge of a loft section: its points and each one's share along it.
struct Edge {
    t: Vec<f64>,
    p: Vec<V3>,
    curve: Curve,
}

/// The loop's edges, each a run of points on one curve ending at the next run's first point. A
/// loop on one curve is one closed edge.
fn edges(lp: &RLoop, curves: &[Curve]) -> Vec<Edge> {
    let m = lp.pts.len();
    let mut runs: Vec<(u32, Vec<V3>)> = vec![];
    if lp.seg.iter().all(|&s| s == lp.seg[0]) {
        let mut p = lp.pts.clone();
        p.push(lp.pts[0]);
        runs.push((lp.seg[0], p));
    } else {
        let first = (0..m).find(|&i| lp.seg[i] != lp.seg[(i + m - 1) % m]).unwrap_or(0);
        for k in 0..m {
            let i = (first + k) % m;
            if k == 0 || lp.seg[i] != lp.seg[(i + m - 1) % m] {
                if let Some(last) = runs.last_mut() {
                    last.1.push(lp.pts[i]);
                }
                runs.push((lp.seg[i], vec![lp.pts[i]]));
            } else {
                runs.last_mut().unwrap().1.push(lp.pts[i]);
            }
        }
        runs.last_mut().unwrap().1.push(lp.pts[first]);
    }
    runs.into_iter()
        .map(|(s, p)| {
            let curve = curves[s as usize];
            let n = p.len() - 1;
            let step: Vec<f64> = match curve {
                Curve::Circle { c, .. } => (0..n)
                    .map(|k| {
                        let (u, v) = (p[k] - c, p[k + 1] - c);
                        atan2(u.cross(v).norm(), u.dot(v))
                    })
                    .collect(),
                Curve::Line => (0..n).map(|k| (p[k + 1] - p[k]).norm()).collect(),
                Curve::Free(_) => vec![1.0; n],
            };
            let total: f64 = step.iter().sum();
            let mut t = Vec::with_capacity(n + 1);
            let mut acc = 0.0;
            t.push(0.0);
            for s in &step {
                acc += s;
                t.push(acc / total);
            }
            t[n] = 1.0;
            Edge { t, p, curve }
        })
        .collect()
}

/// The loop walked the other way from the same first point.
fn reversed_from_start(lp: &RLoop) -> RLoop {
    let m = lp.pts.len();
    RLoop {
        pts: (0..m).map(|k| lp.pts[(m - k) % m]).collect(),
        seg: (0..m).map(|k| lp.seg[m - 1 - k]).collect(),
    }
}

fn interp(x: f64, t: &[f64], p: &[V3]) -> V3 {
    if x <= t[0] {
        return p[0];
    }
    if x >= t[t.len() - 1] {
        return p[p.len() - 1];
    }
    let j = t.partition_point(|&s| s <= x) - 1;
    p[j] + (p[j + 1] - p[j]) * ((x - t[j]) / (t[j + 1] - t[j]))
}

/// The points at shares `u` along the polyline through `p` at shares `t`, each of its own
/// points exactly where its share falls.
fn at(u: &[f64], t: &[f64], p: &[V3]) -> Vec<V3> {
    let mut out: Vec<V3> = u.iter().map(|&x| interp(x, t, p)).collect();
    for (m, &tm) in t.iter().enumerate() {
        let k = u.partition_point(|&x| x <= tm);
        if k > 0 {
            out[k - 1] = p[m];
        }
    }
    out
}

/// Every share of any of `shares`, ascending, those within 10⁻⁹ of the one before dropped.
fn union(shares: &[&[f64]]) -> Vec<f64> {
    let mut every: Vec<f64> = shares.concat();
    every.sort_by(f64::total_cmp);
    let mut u: Vec<f64> = (0..every.len()).filter(|&i| i == 0 || every[i] - every[i - 1] > 1e-9).map(|i| every[i]).collect();
    let n = u.len();
    u[0] = 0.0;
    u[n - 1] = 1.0;
    u
}

/// A section's points at `shares` along each of its edges, in ring order, and each point's
/// place: its edge's index plus its share along it.
fn ring(marks: &[Edge], shares: &[Vec<f64>]) -> (Vec<V3>, Vec<f64>) {
    let mut pts = vec![];
    let mut place = vec![];
    for (j, (e, f)) in marks.iter().zip(shares).enumerate() {
        let p = at(f, &e.t, &e.p);
        pts.extend_from_slice(&p[..p.len() - 1]);
        place.extend(f[..f.len() - 1].iter().map(|&x| j as f64 + x));
    }
    (pts, place)
}

/// `shares` with as many more between neighbours as keep every quad of the band between
/// sections `ma` and `mb`, cut along its rulings at `v`, within LINEAR / 2 of the ruled surface:
/// a bilinear patch's center sits a quarter of its twist off the two triangles that stand for
/// it, and a quad's twist shrinks with its width.
fn twist_split(ma: &[Edge], mb: &[Edge], mut shares: Vec<Vec<f64>>, v: &[f64]) -> Vec<Vec<f64>> {
    for _ in 0..8 {
        let (a, b) = (ring(ma, &shares).0, ring(mb, &shares).0);
        let n = a.len();
        let need: Vec<usize> = (0..n)
            .map(|k| {
                let (an, bn) = (a[(k + 1) % n], b[(k + 1) % n]);
                let twist = (an - a[k]) - (bn - b[k]);
                let mut worst = 0.0f64;
                for w in v.windows(2) {
                    let (v0, v1) = (w[0], w[1]);
                    let nn = (an + (bn - an) * v1 - a[k] - (b[k] - a[k]) * v0)
                        .cross(a[k] + (b[k] - a[k]) * v1 - an - (bn - an) * v0);
                    let size = nn.norm();
                    let off = twist.dot(nn).abs() / if size > 0.0 { size } else { 1.0 };
                    worst = worst.max((v1 - v0) * off / 4.0);
                }
                (worst / (LINEAR / 2.0) - 1e-9).ceil().clamp(0.0, 64.0) as usize
            })
            .collect();
        if need.iter().all(|&x| x <= 1) {
            return shares;
        }
        let mut out = vec![];
        let mut k = 0;
        for f in &shares {
            let mut parts = vec![f[0]];
            for q in 0..f.len() - 1 {
                let nq = need[k + q];
                for s in 1..nq.max(1) {
                    parts.push(f[q] + (f[q + 1] - f[q]) * s as f64 / nq as f64);
                }
                parts.push(f[q + 1]);
            }
            k += f.len() - 1;
            out.push(parts);
        }
        shares = out;
    }
    shares
}

/// Shares along the rulings between rings `p0` and `p1`, from 0 to 1, to cut the band at: halved
/// until no quad's normal turns more than ANGULAR from one cut to the next, and no finer than a
/// 64th. A quad's normal turns with the mix of its two chords, so the cuts gather where the
/// longer chord stops outweighing the shorter. A quad whose ends' normals are a quarter turn or
/// more apart is folded: its normal swings round through nearly nothing somewhere along the
/// ruling, no count of cuts brings that swing under ANGULAR, and it is left out.
fn ruling_cuts(p0: &[V3], p1: &[V3]) -> Vec<f64> {
    let n = p0.len();
    let quads: Vec<(V3, V3, V3)> = (0..n)
        .map(|k| (p1[k] - p0[k], p0[(k + 1) % n] - p0[k], p1[(k + 1) % n] - p1[k]))
        .filter(|&(r, da, db)| da.cross(r).dot(db.cross(r)) > 0.0)
        .collect();
    let turn = |v0: f64, v1: f64| -> f64 {
        let mut worst = 0.0f64;
        for &(r, da, db) in &quads {
            let n0 = (da * (1.0 - v0) + db * v0).cross(r);
            let n1 = (da * (1.0 - v1) + db * v1).cross(r);
            let (s0, s1) = (n0.norm(), n1.norm());
            if s0 > 1e-12 && s1 > 1e-12 {
                worst = worst.max(acos((n0.dot(n1) / (s0 * s1)).clamp(-1.0, 1.0)));
            }
        }
        worst
    };
    let mut cuts = vec![0.0];
    let mut todo = vec![(0.0, 1.0)];
    while let Some((v0, v1)) = todo.pop() {
        if v1 - v0 > 1.0 / 64.0 && turn(v0, v1) > ANGULAR {
            let mid = (v0 + v1) / 2.0;
            todo.push((mid, v1));
            todo.push((v0, mid));
        } else {
            cuts.push(v1);
        }
    }
    cuts
}

/// Triangles joining ring a to ring b, both closed and ordered by place from 0 to `period`, each
/// wound from a's chord toward b; and the place each one's chord starts at. Where the two rings
/// share their places it is the quads' own split.
fn zip(ia: &[u32], ga: &[f64], ib: &[u32], gb: &[f64], period: f64) -> (Vec<[u32; 3]>, Vec<f64>) {
    let ia: Vec<u32> = ia.iter().copied().chain([ia[0]]).collect();
    let ga: Vec<f64> = ga.iter().copied().chain([period]).collect();
    let ib: Vec<u32> = ib.iter().copied().chain([ib[0]]).collect();
    let gb: Vec<f64> = gb.iter().copied().chain([period]).collect();
    let (mut tris, mut start) = (vec![], vec![]);
    let (mut i, mut j) = (0, 0);
    while i < ga.len() - 1 || j < gb.len() - 1 {
        if i < ga.len() - 1 && (j == gb.len() - 1 || ga[i + 1] < gb[j + 1] - 1e-9) {
            tris.push([ia[i], ia[i + 1], ib[j]]);
            start.push(ga[i]);
            i += 1;
        } else {
            tris.push([ia[i], ib[j + 1], ib[j]]);
            start.push(gb[j]);
            j += 1;
        }
    }
    (tris, start)
}

/// Ruled bands between consecutive sections, capped at both ends. Each band is cut along its
/// rulings where its normal turns and across them where it twists, on its own. A section holds
/// the points of the bands on both its sides, the rule's points on its own edges and the rest on
/// the chords joining them, so its cap meets a face cut from the same loop point for point.
pub(crate) fn loft(sections: &[Region], src: Src, op: &'static str) -> Result<Part> {
    ensure!(sections.len() >= 2, "a {op} of {} sections", sections.len());
    let mut loops = vec![];
    for r in sections {
        let l = cleaned(r)?;
        ensure!(l.len() == 1, "a {op} section with holes");
        loops.push(l.into_iter().next().unwrap());
    }
    let mean = |p: &[V3]| p.iter().fold(V3::ZERO, |s, &q| s + q) / p.len() as f64;
    let axis = mean(&loops[loops.len() - 1].pts) - mean(&loops[0].pts);
    let loops: Vec<RLoop> = loops
        .iter()
        .map(|lp| if newell(&lp.pts).dot(axis) < 0.0 { reversed_from_start(lp) } else { lp.clone() })
        .collect();
    let marks: Vec<Vec<Edge>> = loops.iter().zip(sections).map(|(lp, r)| edges(lp, &r.curves)).collect();
    let (ns, ne) = (marks.len(), marks[0].len());
    ensure!(
        marks.iter().all(|m| m.len() == ne),
        "{op} sections of {:?} edges",
        marks.iter().map(Vec::len).collect::<Vec<_>>()
    );
    let mut bands: Vec<(Vec<Vec<f64>>, Vec<f64>)> = vec![];
    for b in 0..ns - 1 {
        let shares: Vec<Vec<f64>> = (0..ne).map(|j| union(&[&marks[b][j].t, &marks[b + 1][j].t])).collect();
        let v = ruling_cuts(&ring(&marks[b], &shares).0, &ring(&marks[b + 1], &shares).0);
        bands.push((twist_split(&marks[b], &marks[b + 1], shares, &v), v));
    }
    let mut part = Part { verts: vec![], tris: vec![], fids: vec![], faces: vec![] };
    fn add(verts: &mut Vec<V3>, pts: &[V3]) -> Vec<u32> {
        let s = verts.len() as u32;
        verts.extend_from_slice(pts);
        (s..verts.len() as u32).collect()
    }
    let mut rings: Vec<(Vec<u32>, Vec<f64>, Vec<V3>)> = vec![];
    for i in 0..ns {
        let side: Vec<&Vec<Vec<f64>>> = [i.wrapping_sub(1), i].iter().filter(|&&k| k < ns - 1).map(|&k| &bands[k].0).collect();
        let shares: Vec<Vec<f64>> =
            (0..ne).map(|j| union(&side.iter().map(|s| s[j].as_slice()).collect::<Vec<_>>())).collect();
        let (pts, place) = ring(&marks[i], &shares);
        rings.push((add(&mut part.verts, &pts), place, pts));
    }
    let axis = mean(&rings[ns - 1].2) - mean(&rings[0].2);
    let out = newell(&rings[0].2).dot(axis) >= 0.0;
    let mut rulings: Vec<Vec<(V3, V3)>> = vec![];
    for (b, (shares, v)) in bands.iter().enumerate() {
        let first = part.faces.len() as u32;
        for _ in 0..ne {
            part.faces.push(Face::new(Surface::Free { kind: "BSPLINE" }, op, src));
            rulings.push(vec![]);
        }
        let (a, place) = ring(&marks[b], shares);
        let bb = ring(&marks[b + 1], shares).0;
        for k in 0..a.len() {
            rulings[first as usize + place[k].floor() as usize].push((a[k], bb[k]));
        }
        let mut lower = (rings[b].0.clone(), rings[b].1.clone());
        let join = |lower: &(Vec<u32>, Vec<f64>), upper: (&[u32], &[f64]), part: &mut Part| {
            let (tris, start) = zip(&lower.0, &lower.1, upper.0, upper.1, ne as f64);
            part.tris.extend(tris);
            part.fids.extend(start.iter().map(|&s| first + (s.floor() as u32).min(ne as u32 - 1)));
        };
        for &cut in &v[1..v.len() - 1] {
            let pts: Vec<V3> = a.iter().zip(&bb).map(|(&p, &q)| p + (q - p) * cut).collect();
            let upper = (add(&mut part.verts, &pts), place.clone());
            join(&lower, (&upper.0, &upper.1), &mut part);
            lower = upper;
        }
        join(&lower, (&rings[b + 1].0, &rings[b + 1].1), &mut part);
    }
    if !out {
        for t in &mut part.tris {
            t.swap(1, 2);
        }
    }
    for (i, sense) in [(0, -1.0), (ns - 1, 1.0)] {
        let along = newell(&rings[i].2).dot(axis) * sense;
        let (pts, ids) = (rings[i].2.clone(), rings[i].0.clone());
        cap(&[&pts], &[ids], along, src, op, &mut part)?;
    }
    outward(&mut part);
    let (pts, area) = record_points(&part);
    for b in 0..ns - 1 {
        for j in 0..ne {
            let f = b * ne + j;
            let surface = match (marks[b][j].curve, marks[b + 1][j].curve) {
                (Curve::Line, Curve::Line) => plane_of(&part.verts, &pts[f], area[f]),
                (Curve::Circle { c: ca, axis: da, r: ra }, Curve::Circle { c: cb, axis: db, r: rb }) => {
                    let d = canonical_axis(da);
                    let h = (cb - ca).dot(d);
                    (canonical_axis(db).cross(d).norm() < 1e-9 && (cb - ca).reject(d).norm() < 1e-9 && h.abs() > 1e-9)
                        .then(|| {
                            if (rb - ra).abs() <= 1e-12 {
                                Surface::Cylinder { p: ca, d, r: ra }
                            } else {
                                Surface::Cone { p: ca, d, r: ra, slope: (rb - ra) / h }
                            }
                        })
                }
                _ => None,
            };
            if let Some(s) = surface.filter(|s| {
                holds(s, pts[f].iter().map(|&k| part.verts[k as usize]))
                    && holds(s, rulings[f].iter().map(|&(p, q)| (p + q) * 0.5))
            }) {
                part.faces[f].surface = s;
            }
        }
    }
    Ok(merged(part))
}

impl Solid {
    /// `region` carried along `path` in a rotation-minimizing frame, capped at both ends unless
    /// the path closes on itself.
    #[track_caller]
    pub fn sweep(region: &Region, path: &Path) -> Result<Solid> {
        Ok(sweep(region, path, Location::caller(), "sweep")?.solid())
    }

    /// A sweep with an explicit path chord budget in mm. The region retains its supplied samples.
    #[track_caller]
    pub fn sweep_with_tolerance(region: &Region, path: &Path, linear: f64) -> Result<Solid> {
        ensure!(linear.is_finite() && linear > 0., "a positive finite path chord budget");
        Ok(sweep_at(region, path, Location::caller(), "sweep", linear)?.solid())
    }

    /// Ruled bands between consecutive sections, capped at both ends. Each section is one loop
    /// with as many edges as every other; edge j of each, from its first point, meets edge j of
    /// the next.
    #[track_caller]
    pub fn loft(sections: &[Region]) -> Result<Solid> {
        Ok(loft(sections, Location::caller(), "loft")?.solid())
    }
}

impl Plane {
    /// `profile`, drawn in this plane's coordinates, swept along `path`.
    #[track_caller]
    pub fn sweep(&self, profile: &Profile, path: &Path) -> Result<Solid> {
        Ok(sweep(&profile.place(self), path, Location::caller(), "sweep")?.solid())
    }
}
