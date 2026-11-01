//! Lofts through closed sections as OCCT's `BRepOffsetAPI_ThruSections` makes them, which is how
//! CadQuery's `loft` makes them.
//!
//! OCCT first makes the sections compatible (`BRepFill_CompatibleWires`): every section gets the
//! same number of edges, each starting where the matching edges of the others start. When the
//! sections' edge counts differ, or every junction of every section is C1 in its curves' own
//! parameters (a lone circle or ellipse is), it cuts them by the polar method: each vertex is
//! carried into the neighbouring section's plane, and the ray from that section's centre through
//! it cuts the section there, or lands on the vertex already there when it falls within a tenth
//! of an edge of it. Otherwise it turns each section after the first to start at, and run the
//! way of, the vertex sequence nearest the section before it.
//!
//! Two sections, or `ruled`, are ruled edge by edge (`Solid::loft`). More are one smooth surface.
//! OCCT makes every section one polynomial B-spline: a conic edge becomes the
//! `GeomConvert_ApproxCurve` of its own parameter (1e-7, C1, degree at most 14), a line its two
//! poles, edge `i` lies on `[i, i + 1]` of one parameter `u`, and every section is raised to the
//! highest degree D any edge needed. The sections' poles are then fitted in v by
//! `Approx_BSplComputeLine` at chord-length parameters: the cumulative distance between
//! successive sections' poles, all of a section's poles taken as one point. It tries one span,
//! then two, then more, knots at parameters spaced evenly by section count, each with degree 2
//! to 8 and C2 joins: a least-squares fit pinned to the end sections, taken once every pole lies
//! within 1e-6 of it. Through at most nine sections that is the polynomial through all of them.
//! When a try would need more poles than there are sections it interpolates instead: a cubic
//! spline knotted at every section, its end slopes those of the polynomials through the first
//! and last nine, each with its far section moved to the far end of the parameter, as OCCT's
//! Bezier through them has it. Every fit mixes the sections linearly, so the surface is
//!
//! ```text
//! S(u, v) = Σ_j W_j(v) C_j(u)
//! ```
//!
//! with `C_j` section j and `W_j` its weight along v.
//!
//! The degree a conic needs is OCCT's own reduction (`PLib_JacobiPolynomial::ReduceDegree`): the
//! remainder after matching the end points and slopes, expanded in Jacobi polynomials, its
//! highest terms dropped while their summed bound stays under the tolerance.
use crate::build::Part;
use crate::face::{Face, Src, Surface};
use crate::mass::signed_volume;
use crate::math::{PI, TAU, V2, V3, acos, asin, cos, sin, v2};
use crate::profile::{Curve, RLoop, Region};
use crate::rule::{ANGULAR, LINEAR, arc_points, plane_frame};
use crate::solid::Solid;
use crate::triangulate::triangulate;
use anyhow::{Result, anyhow, bail, ensure};
use std::panic::Location;
use std::sync::OnceLock;

/// One edge of a loft section, walked from its start to its end.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum LoftEdge {
    Line { a: V3, b: V3 },
    /// `c + x cos t + y sin t` for `t` from `t0` to `t1`: a circle when `x` and `y` are square
    /// and of one length, an ellipse otherwise, with `t` the angle OCCT parameterises it by.
    Conic { c: V3, x: V3, y: V3, t0: f64, t1: f64 },
}

impl LoftEdge {
    /// The point a fraction `s` of the way along the edge's own parameter.
    pub fn at(&self, s: f64) -> V3 {
        match *self {
            LoftEdge::Line { a, b } => a.lerp(b, s),
            LoftEdge::Conic { c, x, y, t0, t1 } => {
                let t = t0 + (t1 - t0) * s;
                c + x * cos(t) + y * sin(t)
            }
        }
    }

    pub fn start(&self) -> V3 {
        self.at(0.0)
    }

    pub fn end(&self) -> V3 {
        self.at(1.0)
    }

    /// The same curve walked the other way.
    pub fn reversed(&self) -> LoftEdge {
        match *self {
            LoftEdge::Line { a, b } => LoftEdge::Line { a: b, b: a },
            LoftEdge::Conic { c, x, y, t0, t1 } => LoftEdge::Conic { c, x, y, t0: t1, t1: t0 },
        }
    }

    /// The part from fraction `s0` to `s1` of the way along.
    pub fn piece(&self, s0: f64, s1: f64) -> LoftEdge {
        match *self {
            LoftEdge::Line { .. } => LoftEdge::Line { a: self.at(s0), b: self.at(s1) },
            LoftEdge::Conic { c, x, y, t0, t1 } => {
                LoftEdge::Conic { c, x, y, t0: t0 + (t1 - t0) * s0, t1: t0 + (t1 - t0) * s1 }
            }
        }
    }

    /// The span of the edge's own parameter: its length on a line, its angle on a conic.
    fn range(&self) -> f64 {
        match *self {
            LoftEdge::Line { a, b } => (b - a).norm(),
            LoftEdge::Conic { t0, t1, .. } => (t1 - t0).abs(),
        }
    }

    /// The derivative along the edge's own parameter, the way the edge is walked.
    fn d1(&self, s: f64) -> V3 {
        match *self {
            LoftEdge::Line { a, b } => (b - a).unit(),
            LoftEdge::Conic { x, y, t0, t1, .. } => {
                let t = t0 + (t1 - t0) * s;
                (y * cos(t) - x * sin(t)) * (t1 - t0).signum()
            }
        }
    }

    /// The edge's length and its points integrated over its length.
    fn moments(&self) -> (f64, V3) {
        match *self {
            LoftEdge::Line { a, b } => {
                let l = (b - a).norm();
                (l, (a + b) * (0.5 * l))
            }
            LoftEdge::Conic { .. } => {
                let (x, w) = gauss16();
                let spans = 64;
                let (mut len, mut mom) = (0.0, V3::ZERO);
                for k in 0..spans {
                    for i in 0..16 {
                        let s = (k as f64 + (x[i] + 1.0) / 2.0) / spans as f64;
                        let wt = w[i] / 2.0 / spans as f64 * self.d1(s).norm() * self.range();
                        len += wt;
                        mom += self.at(s) * wt;
                    }
                }
                (len, mom)
            }
        }
    }

    /// The degree OCCT's approximation gives the edge.
    fn degree(&self) -> Result<usize> {
        match *self {
            LoftEdge::Line { .. } => Ok(1),
            LoftEdge::Conic { c, x, y, t0, t1 } => conic_degree(c, x, y, t0, t1),
        }
    }

    /// The edge's poles at degree `d`: its degree-`d` polynomial on `[0, 1]` in Bernstein form.
    fn poles(&self, d: usize) -> Vec<V3> {
        match *self {
            LoftEdge::Line { a, b } => (0..=d).map(|i| a.lerp(b, i as f64 / d as f64)).collect(),
            LoftEdge::Conic { .. } => bernstein_fit(|s| self.at(s), d),
        }
    }

    /// The circle the edge lies on, when it is one: centre, axis turning the way it is walked,
    /// and radius.
    fn circle(&self) -> Option<(V3, V3, f64)> {
        match *self {
            LoftEdge::Conic { c, x, y, t0, t1 } => {
                let r = x.norm();
                ((y.norm() - r).abs() <= 1e-12 * r.max(1.0) && x.dot(y).abs() <= 1e-12 * r * r)
                    .then(|| (c, x.cross(y).unit() * (t1 - t0).signum(), r))
            }
            LoftEdge::Line { .. } => None,
        }
    }
}

/// A closed section, its edges end to end.
#[derive(Clone, Debug, PartialEq)]
pub struct LoftSection {
    pub edges: Vec<LoftEdge>,
}

impl LoftSection {
    pub fn new(edges: Vec<LoftEdge>) -> LoftSection {
        LoftSection { edges }
    }

    /// One whole ellipse about `c` with semi-axes `x` and `y`, starting on `x`.
    pub fn ellipse(c: V3, x: V3, y: V3) -> LoftSection {
        LoftSection { edges: vec![LoftEdge::Conic { c, x, y, t0: 0.0, t1: TAU }] }
    }

    /// The point at `u` of the section's parameter: edge `floor(u)`, the rest of the way along it.
    pub fn at(&self, u: f64) -> V3 {
        let n = self.edges.len();
        let i = (u.floor().max(0.0) as usize).min(n - 1);
        self.edges[i].at(u - i as f64)
    }

    /// Where OCCT's `PlaneOfWire` centres the section: a lone circle or ellipse at its centre,
    /// any other section at the centre of its length.
    fn centre(&self) -> V3 {
        if let [LoftEdge::Conic { c, .. }] = self.edges[..] {
            return c;
        }
        let (mut l, mut m) = (0.0, V3::ZERO);
        for e in &self.edges {
            let (a, b) = e.moments();
            l += a;
            m += b;
        }
        m / l
    }

    fn samples(&self, per_edge: usize) -> Vec<V3> {
        self.edges
            .iter()
            .flat_map(|e| (0..per_edge).map(move |k| e.at(k as f64 / per_edge as f64)))
            .collect()
    }

    fn normal(&self) -> V3 {
        newell(&self.samples(32))
    }

    /// The section cut into points by the rule, each edge on a curve of its own, for the ruled
    /// loft: a line by its ends, a circle on the rule's angles, an ellipse in equal steps of its
    /// angle.
    pub fn region(&self) -> Region {
        let mut pts = vec![];
        let mut seg = vec![];
        let mut curves = vec![];
        for e in &self.edges {
            let ci = curves.len() as u32;
            let p: Vec<V3> = match (e, e.circle()) {
                (LoftEdge::Line { a, .. }, _) => {
                    curves.push(Curve::Line);
                    vec![*a]
                }
                (_, Some((c, axis, r))) => {
                    curves.push(Curve::Circle { c, axis, r });
                    let mut p = arc_points(c, axis, r, e.start(), e.end(), axis);
                    p.pop();
                    p
                }
                _ => {
                    curves.push(Curve::Free("ELLIPSE"));
                    let samples: Vec<V3> = (0..=256).map(|k| e.at(k as f64 / 256.0)).collect();
                    let n = steps_for(&samples, LINEAR);
                    (0..n).map(|k| e.at(k as f64 / n as f64)).collect()
                }
            };
            seg.extend(std::iter::repeat(ci).take(p.len()));
            pts.extend(p);
        }
        Region { loops: vec![RLoop { pts, seg }], curves }
    }
}

fn newell(p: &[V3]) -> V3 {
    let mut n = V3::ZERO;
    for i in 0..p.len() {
        n += p[i].cross(p[(i + 1) % p.len()]);
    }
    n.unit()
}

/// The angle between two vectors, as `gp_Vec::Angle` takes it.
fn angle(a: V3, b: V3) -> f64 {
    let (a, b) = (a.unit(), b.unit());
    let cosine = a.dot(b);
    if cosine > -0.70710678118655 && cosine < 0.70710678118655 {
        acos(cosine)
    } else {
        let sine = a.cross(b).norm();
        if cosine < 0.0 { PI - asin(sine) } else { asin(sine) }
    }
}

/// OCCT's `BRepLProp::Continuity` at least C1 at every junction of the section: each edge leaves
/// with the derivative the one before arrived with, in their own parameters. A lone closed edge
/// is.
fn c1_throughout(s: &LoftSection) -> bool {
    let m = s.edges.len();
    m == 1
        || (0..m).all(|k| {
            let (d1, d2) = (s.edges[k].d1(1.0), s.edges[(k + 1) % m].d1(0.0));
            (d1.norm() - d2.norm()).abs() <= 2e-7 && angle(d1, d2) <= 1e-12
        })
}

/// The sections made compatible as OCCT's `BRepFill_CompatibleWires` makes them: the same
/// number of edges each, edge `i` of every section matching edge `i` of the others.
pub fn compatible(sections: &[LoftSection]) -> Result<Vec<LoftSection>> {
    ensure!(sections.len() >= 2, "a loft of {} sections", sections.len());
    for s in sections {
        let m = s.edges.len();
        ensure!(m > 0, "a loft section of no edges");
        for k in 0..m {
            let gap = (s.edges[k].end() - s.edges[(k + 1) % m].start()).norm();
            ensure!(gap < 1e-6, "a loft section open by {gap:e} after edge {k}");
        }
    }
    let counts: Vec<usize> = sections.iter().map(|s| s.edges.len()).collect();
    let differ = counts.iter().any(|&c| c != counts[0]);
    if differ || sections.iter().all(c1_throughout) { polar(sections) } else { Ok(origin(sections)) }
}

/// `p` carried from the plane through `pos1` normal to `ax1` into the plane through `pos2`
/// normal to `ax2`, as OCCT's `Transform` carries it (with rotation).
fn transform(p: V3, pos1: V3, ax1: V3, pos2: V3, ax2: V3) -> V3 {
    let moved = p + (pos2 - pos1);
    let a = angle(ax1, ax2);
    if a <= 1e-4 || PI - a <= 1e-4 {
        return moved;
    }
    let vt = pos2 - pos1;
    let (mut a1, mut a2) = (ax1.unit(), ax2.unit());
    if vt.dot(a1) < -1e-7 {
        a1 = -a1;
    }
    if vt.dot(a2) < 1e-7 {
        a2 = -a2;
    }
    let norm2 = a1.cross(a2);
    let vsign = a2 * vt.dot(a1) - a1 * vt.dot(a2);
    let (alpha, beta) = (vsign.dot(a1), vsign.dot(a2));
    let sign = if alpha * beta > 0.0 && alpha.abs() > 1e-4 && beta.abs() > 1e-4 { -1.0 } else { 1.0 };
    let turn = angle(a1, a2) * sign;
    let d = norm2.unit();
    let v = moved - pos2;
    let (s, c) = (sin(turn), cos(turn));
    pos2 + v * c + d.cross(v) * s + d * (d.dot(v) * (1.0 - c))
}

/// An edge of a section being cut by the polar method, between two vertices by number.
#[derive(Clone, Copy, Debug)]
struct WEdge {
    e: LoftEdge,
    a: usize,
    b: usize,
}

/// Lists of vertices keyed by vertex, in the order they were bound.
type VMap = Vec<(usize, Vec<usize>)>;

fn search_root(v: usize, map: &VMap) -> Option<usize> {
    map.iter().find(|(_, l)| l.contains(&v)).map(|(k, _)| *k)
}

fn entry(map: &mut VMap, k: usize) -> &mut Vec<usize> {
    let i = map.iter().position(|(key, _)| *key == k).expect("a bound vertex");
    &mut map[i].1
}

/// The wire's vertices in the order its edges name them, each once.
fn vertices(w: &[WEdge]) -> Vec<usize> {
    let mut s = vec![];
    for e in w {
        for v in [e.a, e.b] {
            if !s.contains(&v) {
                s.push(v);
            }
        }
    }
    s
}

struct Wires {
    pts: Vec<V3>,
    wires: Vec<Vec<WEdge>>,
    pos: Vec<V3>,
    axe: Vec<V3>,
}

impl Wires {
    fn new(sections: &[LoftSection]) -> Wires {
        let mut pts = vec![];
        let mut wires = vec![];
        for s in sections {
            let base = pts.len();
            let m = s.edges.len();
            pts.extend(s.edges.iter().map(LoftEdge::start));
            wires.push((0..m).map(|k| WEdge { e: s.edges[k], a: base + k, b: base + (k + 1) % m }).collect());
        }
        Wires {
            pts,
            wires,
            pos: sections.iter().map(LoftSection::centre).collect(),
            axe: sections.iter().map(LoftSection::normal).collect(),
        }
    }

    /// OCCT's `EdgeIntersectOnWire`: where the ray from `p1` through `p2` crosses wire `w`. The
    /// crossing nearest `p2` is a vertex already there when it falls on one, or within a tenth of
    /// its edge of one no list of `map` holds; otherwise the edge is cut there.
    fn intersect(&mut self, w: usize, p1: V3, p2: V3, map: &VMap) -> Result<usize> {
        let dir = (p2 - p1).unit();
        let n = self.axe[w];
        let (mut lo, mut hi) = (V3::from([f64::INFINITY; 3]), V3::from([f64::NEG_INFINITY; 3]));
        for we in &self.wires[w] {
            for k in 0..=32 {
                let p = we.e.at(k as f64 / 32.0);
                lo = lo.min(p);
                hi = hi.max(p);
            }
        }
        let diag = (hi - lo).norm();
        let zero = 1e-12 * diag.max(1.0);
        let side = |p: V3| {
            let f = (p - p1).cross(dir).dot(n);
            if f.abs() <= zero { 0.0 } else { f }
        };
        let mut best: Option<(usize, f64, f64)> = None;
        for (k, we) in self.wires[w].iter().enumerate() {
            const N: usize = 512;
            let f: Vec<f64> = (0..=N).map(|i| side(we.e.at(i as f64 / N as f64))).collect();
            for i in 0..=N {
                let root = if f[i] == 0.0 {
                    i as f64 / N as f64
                } else if i < N && (f[i] < 0.0) != (f[i + 1] < 0.0) && f[i + 1] != 0.0 {
                    let (mut a, mut b) = (i as f64 / N as f64, (i + 1) as f64 / N as f64);
                    for _ in 0..100 {
                        let mid = 0.5 * (a + b);
                        if (side(we.e.at(mid)) < 0.0) == (f[i] < 0.0) {
                            a = mid;
                        } else {
                            b = mid;
                        }
                    }
                    0.5 * (a + b)
                } else {
                    continue;
                };
                let p = we.e.at(root);
                let along = (p - p1).dot(dir);
                if along < -1e-9 || along > diag {
                    continue;
                }
                let d = (p - p2).norm();
                if best.is_none_or(|(_, _, bd)| d < bd) {
                    best = Some((k, root, d));
                }
            }
        }
        let (k, s, _) = best.ok_or_else(|| anyhow!("a loft section no ray from its centre crosses"))?;
        let we = self.wires[w][k];
        let exact = 1e-7 / we.e.range();
        if s <= exact {
            return Ok(we.a);
        }
        if s >= 1.0 - exact {
            return Ok(we.b);
        }
        let near = if s < 0.1 {
            Some(we.a)
        } else if s > 0.9 {
            Some(we.b)
        } else {
            None
        };
        if let Some(v) = near.filter(|&v| search_root(v, map).is_none()) {
            return Ok(v);
        }
        let v = self.pts.len();
        self.pts.push(we.e.at(s));
        self.wires[w].splice(
            k..=k,
            [WEdge { e: we.e.piece(0.0, s), a: we.a, b: v }, WEdge { e: we.e.piece(s, 1.0), a: v, b: we.b }],
        );
        Ok(v)
    }

    /// `p` carried from section `i`'s plane back into the first section's.
    fn back(&self, p: V3, i: usize) -> V3 {
        let mut q = p;
        for r in (1..=i).rev() {
            q = transform(q, self.pos[r], self.axe[r], self.pos[r - 1], self.axe[r - 1]);
        }
        q
    }
}

/// OCCT's `SameNumberByPolarMethod`.
fn polar(sections: &[LoftSection]) -> Result<Vec<LoftSection>> {
    let n = sections.len();
    let mut w = Wires::new(sections);
    // Every vertex of each section, from the last, onto the section before it.
    let mut images: VMap = vec![];
    for i in (1..n).rev() {
        for vi in vertices(&w.wires[i]) {
            images.retain(|(k, _)| *k != vi);
            images.push((vi, vec![]));
            let p = transform(w.pts[vi], w.pos[i], w.axe[i], w.pos[i - 1], w.axe[i - 1]);
            if (p - w.pos[i - 1]).norm() > 1e-7 {
                let v = w.intersect(i - 1, w.pos[i - 1], p, &images)?;
                entry(&mut images, vi).push(v);
            }
        }
    }
    // The chain of vertices each first-section vertex is the image of.
    let mut chains: VMap = vec![];
    for vi in vertices(&w.wires[0]) {
        let mut chain = vec![vi];
        let mut v0 = vi;
        while let Some(v1) = search_root(v0, &images) {
            chain.push(v1);
            if v1 == vi || chain.len() >= n {
                break;
            }
            v0 = v1;
        }
        chains.push((vi, chain));
    }
    // Every chain carried on into each section it has no vertex on.
    for i in 0..n - 1 {
        for vi in vertices(&w.wires[i]) {
            let root = search_root(vi, &chains);
            let next = vertices(&w.wires[i + 1]);
            let missing = match root {
                Some(r) => {
                    let chain = &chains.iter().find(|(k, _)| *k == r).unwrap().1;
                    !next.iter().any(|v| chain.contains(v))
                }
                None => true,
            };
            if missing {
                let p = transform(w.pts[vi], w.pos[i], w.axe[i], w.pos[i + 1], w.axe[i + 1]);
                if (p - w.pos[i + 1]).norm() > 1e-7 {
                    let v = w.intersect(i + 1, w.pos[i + 1], p, &chains)?;
                    let r = root.ok_or_else(|| anyhow!("a loft vertex on no chain"))?;
                    entry(&mut chains, r).push(v);
                }
            }
        }
    }
    // Each section after the first from the vertex matching the first section's start, the way
    // the first runs.
    let first = w.wires[0][0];
    let ns = (first.e.at(0.9) - w.pos[0]).unit();
    let mut out = vec![LoftSection::new(w.wires[0].iter().map(|we| we.e).collect())];
    for i in 1..n {
        let (cf, cl) = (entry(&mut chains, first.a).clone(), entry(&mut chains, first.b).clone());
        ensure!(cf.len() > i && cl.len() > i, "a loft section the polar method left unmatched");
        let (v1, v2) = (cf[i], cl[i]);
        let wire = &w.wires[i];
        let mut best: Option<(usize, bool)> = None;
        let mut most = 0.0;
        for (k, we) in wire.iter().enumerate() {
            if (we.a == v1 && we.b == v2) || (we.a == v2 && we.b == v1) {
                for (s, rev) in [(0.9, false), (0.1, true)] {
                    let scal = (w.back(we.e.at(s), i) - w.pos[0]).unit().dot(ns);
                    if scal > most {
                        most = scal;
                        best = Some((k, rev));
                    }
                }
            }
        }
        let (k0, rev) = best.ok_or_else(|| anyhow!("loft sections OCCT finds inconsistent"))?;
        let m = wire.len();
        let edges: Vec<LoftEdge> = if rev {
            (0..m).map(|j| wire[(k0 + m - j) % m].e.reversed()).collect()
        } else {
            (0..m).map(|j| wire[(k0 + j) % m].e).collect()
        };
        ensure!(edges.len() == out[0].edges.len(), "loft sections of {} and {} edges after cutting", out[0].edges.len(), edges.len());
        out.push(LoftSection::new(edges));
    }
    Ok(out)
}

/// OCCT's `ComputeOrigin`: each section after the first started at, and walked the way of, the
/// vertex sequence whose vertices lie nearest the section before it's, the two centres brought
/// together in the first section's plane. Sections of two edges or fewer compare points along
/// the edges too.
fn origin(sections: &[LoftSection]) -> Vec<LoftSection> {
    let l = sections[0].edges.len();
    let samples = if l <= 2 { 4 } else { 0 };
    let normal = sections[0].normal();
    let mut prev = sections[0].clone();
    let mut prev_bary = sections[0].centre();
    let mut out = vec![prev.clone()];
    for s in &sections[1..] {
        let bary = s.centre();
        let bary = bary - normal * (bary - prev_bary).dot(normal);
        let offset = prev_bary - bary;
        let cost = |cand: &LoftSection| -> f64 {
            let mut sum = 0.0;
            for (pe, ce) in prev.edges.iter().zip(&cand.edges) {
                sum += (pe.start() - (ce.start() + offset)).norm();
                for k in 1..samples {
                    let f = k as f64 / samples as f64;
                    sum += (pe.at(f) - (ce.at(f) + offset)).norm();
                }
            }
            sum
        };
        let mut best: Option<(f64, LoftSection)> = None;
        for j in 0..l {
            let forward = LoftSection::new((0..l).map(|k| s.edges[(j + k) % l]).collect());
            let backward = LoftSection::new((0..l).map(|k| s.edges[(j + 2 * l - 1 - k) % l].reversed()).collect());
            for cand in [forward, backward] {
                let c = cost(&cand);
                if best.as_ref().is_none_or(|(b, _)| c < *b) {
                    best = Some((c, cand));
                }
            }
        }
        prev = best.unwrap().1;
        prev_bary = bary;
        out.push(prev.clone());
    }
    out
}

// --- OCCT's degree for a conic ------------------------------------------------------------

/// `GeomConvert_ApproxCurve`'s tolerance and largest degree in OCCT's loft.
const APPROX_TOL: f64 = 1e-7;
const MAX_DEGREE: usize = 14;
/// Jacobi terms past the cubic that matches the ends: degree 14 less the four constraints.
const JACOBI_TERMS: usize = MAX_DEGREE - 3;
/// Terms through degree 20: those past 14 are what one span of degree 14 leaves out.
const TAIL_TERMS: usize = JACOBI_TERMS + 6;

fn gauss_legendre(n: usize) -> (Vec<f64>, Vec<f64>) {
    let legendre = |t: f64| -> (f64, f64) {
        let (mut p0, mut p1) = (1.0, t);
        for k in 2..=n {
            let p2 = ((2 * k - 1) as f64 * t * p1 - (k - 1) as f64 * p0) / k as f64;
            p0 = p1;
            p1 = p2;
        }
        (p1, n as f64 * (t * p1 - p0) / (t * t - 1.0))
    };
    let mut x = vec![0.0; n];
    let mut w = vec![0.0; n];
    for i in 0..n {
        let mut t = cos(PI * (i as f64 + 0.75) / (n as f64 + 0.5));
        for _ in 0..100 {
            let (p, dp) = legendre(t);
            let dt = p / dp;
            t -= dt;
            if dt.abs() < 1e-16 {
                break;
            }
        }
        let (_, dp) = legendre(t);
        x[i] = t;
        w[i] = 2.0 / ((1.0 - t * t) * dp * dp);
    }
    (x, w)
}

fn gauss16() -> &'static (Vec<f64>, Vec<f64>) {
    static G: OnceLock<(Vec<f64>, Vec<f64>)> = OnceLock::new();
    G.get_or_init(|| gauss_legendre(16))
}

struct Jacobi {
    nodes: Vec<f64>,
    weights: Vec<f64>,
    /// `j[k][i]`: the k-th polynomial orthonormal under (1 − t²)⁴ at `nodes[i]`.
    j: Vec<Vec<f64>>,
    /// The largest |(1 − t²)² J_k(t)| on [-1, 1]: what dropping term k can cost.
    tabmax: Vec<f64>,
}

fn jacobi() -> &'static Jacobi {
    static J: OnceLock<Jacobi> = OnceLock::new();
    J.get_or_init(|| {
        let (nodes, weights) = gauss_legendre(120);
        let grid: Vec<f64> = (0..=8000).map(|i| -1.0 + 2.0 * i as f64 / 8000.0).collect();
        // Legendre polynomials, by their recurrence, orthonormalized under (1 − t²)⁴.
        let legendre = |t: f64| -> Vec<f64> {
            let mut p = vec![1.0, t];
            for k in 2..TAIL_TERMS {
                p.push(((2 * k - 1) as f64 * t * p[k - 1] - (k - 1) as f64 * p[k - 2]) / k as f64);
            }
            p.truncate(TAIL_TERMS);
            p
        };
        let at_nodes: Vec<Vec<f64>> = nodes.iter().map(|&t| legendre(t)).collect();
        let at_grid: Vec<Vec<f64>> = grid.iter().map(|&t| legendre(t)).collect();
        let w2: Vec<f64> = nodes.iter().map(|t| (1.0 - t * t).powi(4)).collect();
        let dot = |a: &[f64], b: &[f64]| -> f64 { (0..nodes.len()).map(|i| weights[i] * w2[i] * a[i] * b[i]).sum() };
        let mut j: Vec<Vec<f64>> = vec![];
        let mut g: Vec<Vec<f64>> = vec![];
        for k in 0..TAIL_TERMS {
            let mut v: Vec<f64> = at_nodes.iter().map(|p| p[k]).collect();
            let mut vg: Vec<f64> = at_grid.iter().map(|p| p[k]).collect();
            for (q, qg) in j.iter().zip(&g) {
                let c = dot(&v, q);
                for i in 0..v.len() {
                    v[i] -= c * q[i];
                }
                for i in 0..vg.len() {
                    vg[i] -= c * qg[i];
                }
            }
            let n = dot(&v, &v).sqrt();
            v.iter_mut().for_each(|x| *x /= n);
            vg.iter_mut().for_each(|x| *x /= n);
            j.push(v);
            g.push(vg);
        }
        let tabmax = g
            .iter()
            .map(|vg| grid.iter().zip(vg).map(|(t, v)| ((1.0 - t * t).powi(2) * v).abs()).fold(0.0, f64::max))
            .collect();
        Jacobi { nodes, weights, j, tabmax }
    })
}

/// The degree `GeomConvert_ApproxCurve` settles on for `c + x cos t + y sin t` over [t0, t1].
fn conic_degree(c: V3, x: V3, y: V3, t0: f64, t1: f64) -> Result<usize> {
    let jac = jacobi();
    let h = (t1 - t0) / 2.0;
    let f = |t: f64| c + x * cos(t) + y * sin(t);
    let df = |t: f64| (y * cos(t) - x * sin(t)) * h;
    let (f0, f1, d0, d1) = (f(t0), f(t1), df(t0), df(t1));
    let mut coeff = vec![V3::ZERO; TAIL_TERMS];
    for (i, &s) in jac.nodes.iter().enumerate() {
        let h00 = (2.0 + s) * (1.0 - s) * (1.0 - s) / 4.0;
        let h10 = (1.0 + s) * (1.0 - s) * (1.0 - s) / 4.0;
        let h01 = (2.0 - s) * (1.0 + s) * (1.0 + s) / 4.0;
        let h11 = -(1.0 - s) * (1.0 + s) * (1.0 + s) / 4.0;
        let hermite = f0 * h00 + d0 * h10 + f1 * h01 + d1 * h11;
        let r = f(t0 + (s + 1.0) * h) - hermite;
        let w = jac.weights[i] * (1.0 - s * s).powi(2);
        for k in 0..TAIL_TERMS {
            coeff[k] += r * (w * jac.j[k][i]);
        }
    }
    let tail: f64 = (JACOBI_TERMS..TAIL_TERMS).map(|k| coeff[k].norm() * jac.tabmax[k]).sum();
    if tail > APPROX_TOL {
        bail!("a conic edge needs more than one degree-{MAX_DEGREE} span; OCCT would cut it");
    }
    let mut err = 0.0;
    for k in (0..JACOBI_TERMS).rev() {
        err += coeff[k].norm() * jac.tabmax[k];
        if err > APPROX_TOL {
            return Ok(k + 4);
        }
    }
    Ok(3)
}

/// The degree-`d` polynomial through `f` at Chebyshev points of [0, 1], as Bernstein poles.
fn bernstein_fit(f: impl Fn(f64) -> V3, d: usize) -> Vec<V3> {
    let n = d + 1;
    let s: Vec<f64> = (0..n).map(|k| (1.0 + cos((2 * k + 1) as f64 * PI / (2 * n) as f64)) / 2.0).collect();
    let mut binom = vec![1.0f64; n];
    for i in 1..n {
        binom[i] = binom[i - 1] * (d + 1 - i) as f64 / i as f64;
    }
    let mut a: Vec<Vec<f64>> = s
        .iter()
        .map(|&t| (0..n).map(|i| binom[i] * t.powi(i as i32) * (1.0 - t).powi((d - i) as i32)).collect())
        .collect();
    let mut b: Vec<V3> = s.iter().map(|&t| f(t)).collect();
    for col in 0..n {
        let piv = (col..n).max_by(|&i, &j| a[i][col].abs().total_cmp(&a[j][col].abs())).unwrap();
        a.swap(col, piv);
        b.swap(col, piv);
        for row in col + 1..n {
            let m = a[row][col] / a[col][col];
            if m != 0.0 {
                for k in col..n {
                    a[row][k] -= m * a[col][k];
                }
                let bc = b[col];
                b[row] -= bc * m;
            }
        }
    }
    let mut x = vec![V3::ZERO; n];
    for row in (0..n).rev() {
        let mut acc = b[row];
        for k in row + 1..n {
            acc -= x[k] * a[row][k];
        }
        x[row] = acc / a[row][row];
    }
    x
}

// --- The smooth surface --------------------------------------------------------------------

/// OCCT's smooth loft surface through compatible sections.
#[derive(Clone, Debug)]
pub struct SmoothLoft {
    pub sections: Vec<LoftSection>,
    /// Chord-length parameters, 0 at the first section and 1 at the last.
    pub params: Vec<f64>,
    /// The degree every section was raised to.
    pub degree: usize,
    /// The fit along v.
    pub fit: VFit,
}

/// A B-spline along v whose poles mix the sections: `mix[p][j]` is section j's share of pole p.
#[derive(Clone, Debug)]
pub struct VFit {
    pub knots: Vec<f64>,
    pub degree: usize,
    pub mix: Vec<Vec<f64>>,
}

impl VFit {
    fn weights(&self, v: f64) -> Vec<f64> {
        let (first, basis) = bspline_basis(&self.knots, self.degree, v);
        let n = self.mix[0].len();
        let mut w = vec![0.0; n];
        for (k, b) in basis.iter().enumerate() {
            for (j, m) in self.mix[first + k].iter().enumerate() {
                w[j] += b * m;
            }
        }
        w
    }
}

/// The `degree + 1` B-spline basis functions not zero at `t`, and the index of the first.
fn bspline_basis(knots: &[f64], degree: usize, t: f64) -> (usize, Vec<f64>) {
    let np = knots.len() - degree - 1;
    let t = t.clamp(knots[degree], knots[np]);
    let mut span = degree;
    while span + 1 < np && knots[span + 1] <= t {
        span += 1;
    }
    let mut n = vec![0.0; degree + 1];
    let mut left = vec![0.0; degree + 1];
    let mut right = vec![0.0; degree + 1];
    n[0] = 1.0;
    for j in 1..=degree {
        left[j] = t - knots[span + 1 - j];
        right[j] = knots[span + j] - t;
        let mut saved = 0.0;
        for r in 0..j {
            let temp = n[r] / (right[r + 1] + left[j - r]);
            n[r] = saved + right[r + 1] * temp;
            saved = left[j - r] * temp;
        }
        n[j] = saved;
    }
    (span - degree, n)
}

/// `a x = b` for every column of `b`, by Gaussian elimination with partial pivoting.
fn solve(mut a: Vec<Vec<f64>>, mut b: Vec<Vec<f64>>) -> Result<Vec<Vec<f64>>> {
    let n = a.len();
    for col in 0..n {
        let piv = (col..n).max_by(|&i, &j| a[i][col].abs().total_cmp(&a[j][col].abs())).unwrap();
        ensure!(a[piv][col].abs() > 1e-300, "a singular fit along a loft");
        a.swap(col, piv);
        b.swap(col, piv);
        for row in col + 1..n {
            let f = a[row][col] / a[col][col];
            if f != 0.0 {
                for k in col..n {
                    a[row][k] -= f * a[col][k];
                }
                for k in 0..b[row].len() {
                    b[row][k] -= f * b[col][k];
                }
            }
        }
    }
    for row in (0..n).rev() {
        for k in 0..b[row].len() {
            let mut acc = b[row][k];
            for c in row + 1..n {
                acc -= a[row][c] * b[c][k];
            }
            b[row][k] = acc / a[row][row];
        }
    }
    Ok(b)
}

/// The least-squares B-spline on `knots` through the sections at `params`, its end poles the end
/// sections, as each pole's mix of the sections.
fn least_squares(params: &[f64], knots: &[f64], degree: usize) -> Result<Vec<Vec<f64>>> {
    let n = params.len();
    let np = knots.len() - degree - 1;
    let mut a = vec![vec![0.0; np]; n];
    for (i, &t) in params.iter().enumerate() {
        let (first, basis) = bspline_basis(knots, degree, t);
        for (k, b) in basis.iter().enumerate() {
            a[i][first + k] = *b;
        }
    }
    // The data less what the pinned end poles already give, as mixes of the sections.
    let rhs: Vec<Vec<f64>> = (0..n)
        .map(|i| {
            let mut r = vec![0.0; n];
            r[i] += 1.0;
            r[0] -= a[i][0];
            r[n - 1] -= a[i][np - 1];
            r
        })
        .collect();
    let inner = np - 2;
    let g: Vec<Vec<f64>> =
        (1..np - 1).map(|p| (1..np - 1).map(|q| (0..n).map(|i| a[i][p] * a[i][q]).sum()).collect()).collect();
    let atb: Vec<Vec<f64>> =
        (1..np - 1).map(|p| (0..n).map(|j| (0..n).map(|i| a[i][p] * rhs[i][j]).sum()).collect()).collect();
    let x = if inner > 0 { solve(g, atb)? } else { vec![] };
    let mut mix = vec![vec![0.0; n]; np];
    mix[0][0] = 1.0;
    mix[np - 1][n - 1] = 1.0;
    for p in 0..inner {
        mix[p + 1] = x[p].clone();
    }
    Ok(mix)
}

/// The derivative at `t` of the polynomial through the sections at `params`, as each section's
/// share of it.
fn lagrange_slope(params: &[f64], t: f64) -> Vec<f64> {
    let n = params.len();
    (0..n)
        .map(|j| {
            let mut sum = 0.0;
            for m in 0..n {
                if m == j {
                    continue;
                }
                let mut term = 1.0 / (params[j] - params[m]);
                for k in 0..n {
                    if k != j && k != m {
                        term *= (t - params[k]) / (params[j] - params[k]);
                    }
                }
                sum += term;
            }
            sum
        })
        .collect()
}

/// `Approx_BSplComputeLine::Interpol`: the cubic spline knotted at every section and through
/// each, its slope at each end that of the polynomial through the nine sections nearest it. That
/// polynomial is OCCT's Bezier through those sections: the inner ones at their own parameters,
/// the near end at its own and the far end at the Bezier's other end, 0 or 1.
fn interpolate(params: &[f64]) -> Result<VFit> {
    let n = params.len();
    ensure!(n > 4, "a loft of {n} sections reached OCCT's short interpolation");
    let mut knots = vec![0.0; 4];
    knots.extend_from_slice(&params[1..n - 1]);
    knots.extend([1.0; 4]);
    let np = n + 2;
    let near = n.min(9);
    let mut nodes = params[..near].to_vec();
    nodes[near - 1] = 1.0;
    let head = lagrange_slope(&nodes, 0.0);
    let mut nodes = params[n - near..].to_vec();
    nodes[0] = 0.0;
    let tail = lagrange_slope(&nodes, 1.0);
    let (l1, l2) = ((params[1] - params[0]) / 3.0, (params[n - 1] - params[n - 2]) / 3.0);
    let mut mix = vec![vec![0.0; n]; np];
    mix[0][0] = 1.0;
    mix[1][0] = 1.0;
    for (j, s) in head.iter().enumerate() {
        mix[1][j] += l1 * s;
    }
    mix[np - 1][n - 1] = 1.0;
    mix[np - 2][n - 1] = 1.0;
    for (j, s) in tail.iter().enumerate() {
        mix[np - 2][n - near + j] -= l2 * s;
    }
    // The poles between, from passing through every inner section.
    let inner = n - 2;
    let mut a = vec![vec![0.0; inner]; inner];
    let mut b = vec![vec![0.0; n]; inner];
    for i in 1..n - 1 {
        let (first, basis) = bspline_basis(&knots, 3, params[i]);
        b[i - 1][i] = 1.0;
        for (k, v) in basis.iter().enumerate() {
            let p = first + k;
            if (2..np - 2).contains(&p) {
                a[i - 1][p - 2] += v;
            } else {
                for j in 0..n {
                    b[i - 1][j] -= v * mix[p][j];
                }
            }
        }
    }
    let x = solve(a, b)?;
    for p in 0..inner {
        mix[p + 2] = x[p].clone();
    }
    Ok(VFit { knots, degree: 3, mix })
}

/// OCCT's fit along v of the sections' poles at `params`.
fn v_fit(params: &[f64], poles: &[Vec<V3>]) -> Result<VFit> {
    const TOL: f64 = 1e-6;
    let n = params.len();
    for nbknots in 2..=n + 1 {
        let mut inner_knots = vec![];
        for i in 2..nbknots {
            let l = (n - 1) as f64 * (i - 1) as f64 / (nbknots - 1) as f64;
            let ll = l as usize;
            let a = l - ll as f64;
            inner_knots.push((1.0 - a) * params[ll] + a * params[ll + 1]);
        }
        for degree in 2..=8usize {
            let mult = degree.saturating_sub(2).max(1);
            let np = degree + 1 + inner_knots.len() * mult;
            if np > n {
                return interpolate(params);
            }
            let mut knots = vec![0.0; degree + 1];
            for &k in &inner_knots {
                knots.extend(std::iter::repeat(k).take(mult));
            }
            knots.extend(std::iter::repeat(1.0).take(degree + 1));
            let mix = least_squares(params, &knots, degree)?;
            let fit = VFit { knots, degree, mix };
            let mut worst = 0.0f64;
            for (i, &t) in params.iter().enumerate() {
                let w = fit.weights(t);
                for k in 0..poles[0].len() {
                    let p = w.iter().zip(poles).fold(V3::ZERO, |acc, (wj, pj)| acc + pj[k] * *wj);
                    worst = worst.max((p - poles[i][k]).norm());
                }
            }
            if worst <= TOL {
                return Ok(fit);
            }
        }
    }
    bail!("no fit along the loft within {TOL}")
}

impl SmoothLoft {
    /// The surface through `sections`, which must already be compatible (see [`compatible`]).
    pub fn new(sections: &[LoftSection]) -> Result<SmoothLoft> {
        ensure!(sections.len() >= 2, "a loft needs two sections");
        let m = sections[0].edges.len();
        ensure!(sections.iter().all(|s| s.edges.len() == m), "loft sections of different edge counts");
        let mut degree = 1;
        for s in sections {
            for e in &s.edges {
                degree = degree.max(e.degree()?);
            }
        }
        let poles: Vec<Vec<V3>> = sections
            .iter()
            .map(|s| {
                let mut p = vec![];
                for (k, e) in s.edges.iter().enumerate() {
                    let q = e.poles(degree);
                    p.extend_from_slice(if k == 0 { &q[..] } else { &q[1..] });
                }
                p
            })
            .collect();
        let mut params = vec![0.0];
        for j in 1..poles.len() {
            let d2: f64 = poles[j].iter().zip(&poles[j - 1]).map(|(a, b)| (*a - *b).norm2()).sum();
            params.push(params[j - 1] + d2.sqrt());
        }
        let total = params[params.len() - 1];
        ensure!(total > 0.0, "loft sections that do not move");
        params.iter_mut().for_each(|p| *p /= total);
        let fit = v_fit(&params, &poles)?;
        Ok(SmoothLoft { sections: sections.to_vec(), params, degree, fit })
    }

    /// The weight of each section at `v`.
    pub fn weights(&self, v: f64) -> Vec<f64> {
        self.fit.weights(v)
    }

    pub fn at(&self, u: f64, v: f64) -> V3 {
        self.weights(v).iter().zip(&self.sections).fold(V3::ZERO, |p, (w, s)| p + s.at(u) * *w)
    }

    /// Each section's point at `u`: what every point of the surface at `u` blends, whatever its
    /// `v`.
    fn ring(&self, u: f64) -> Vec<V3> {
        self.sections.iter().map(|s| s.at(u)).collect()
    }

    /// The parameters the solid is cut at: `u` in equal steps along each edge, `v` in equal steps
    /// from 0 to 1, as many as keep every triangle within LINEAR of the surface and every turn
    /// within ANGULAR.
    pub fn grid(&self) -> (Vec<f64>, Vec<f64>) {
        let m = self.sections[0].edges.len();
        let mut probe_v = self.params.clone();
        for w in self.params.windows(2) {
            probe_v.extend((1..8).map(|k| w[0] + (w[1] - w[0]) * k as f64 / 8.0));
        }
        let probe_w: Vec<Vec<f64>> = probe_v.iter().map(|&v| self.weights(v)).collect();
        let mut counts = vec![1usize; m];
        for (e, count) in counts.iter_mut().enumerate() {
            let rings: Vec<Vec<V3>> = (0..=256).map(|k| self.ring(e as f64 + k as f64 / 256.0)).collect();
            for w in &probe_w {
                let samples: Vec<V3> = rings.iter().map(|r| mix(w, r)).collect();
                *count = (*count).max(steps_for(&samples, LINEAR / 2.0));
            }
        }
        let fine = 64 * (self.params.len() - 1);
        let weights: Vec<Vec<f64>> = (0..=fine).map(|k| self.weights(k as f64 / fine as f64)).collect();
        let mut nv = 1;
        for e in 0..m {
            for q in 0..4 {
                let u = e as f64 + q as f64 / 4.0;
                let ring = self.ring(u);
                let samples: Vec<V3> = weights.iter().map(|w| mix(w, &ring)).collect();
                nv = nv.max(steps_for(&samples, LINEAR / 2.0));
            }
        }
        for _ in 0..8 {
            let us = cuts(&counts);
            let vs: Vec<f64> = (0..=nv).map(|k| k as f64 / nv as f64).collect();
            let (per_edge, across) = self.sag(&us, &vs);
            let mut done = true;
            if across > LINEAR / 2.0 {
                nv = (nv as f64 * (across / (LINEAR / 2.0)).sqrt() * 1.05).ceil() as usize;
                done = false;
            }
            for (c, &w) in counts.iter_mut().zip(&per_edge) {
                if w > LINEAR {
                    *c = (*c as f64 * w / LINEAR * 1.05).ceil() as usize;
                    done = false;
                }
            }
            if done {
                return (us, vs);
            }
        }
        (cuts(&counts), (0..=nv).map(|k| k as f64 / nv as f64).collect())
    }

    /// How far the surface strays from the grid's triangles: for each edge the worst of its
    /// quads, at their middles and along their sides in `u`, and over every quad the worst
    /// along their sides in `v`.
    fn sag(&self, us: &[f64], vs: &[f64]) -> (Vec<f64>, f64) {
        let nu = us.len();
        let m = self.sections[0].edges.len();
        let mut per_edge = vec![0.0f64; m];
        let mut across = 0.0f64;
        let at_us: Vec<Vec<V3>> = us.iter().map(|&u| self.ring(u)).collect();
        let at_mids: Vec<Vec<V3>> = (0..nu).map(|i| self.ring(mid_u(us, i, m))).collect();
        let row_w: Vec<Vec<f64>> = vs.iter().map(|&v| self.weights(v)).collect();
        let rows: Vec<Vec<V3>> = row_w.iter().map(|w| at_us.iter().map(|ring| mix(w, ring)).collect()).collect();
        for r in 0..vs.len() - 1 {
            let w = self.weights(0.5 * (vs[r] + vs[r + 1]));
            for i in 0..nu {
                let j = (i + 1) % nu;
                let (a, b, c, d) = (rows[r][i], rows[r][j], rows[r + 1][j], rows[r + 1][i]);
                let mid = mix(&w, &at_mids[i]);
                let diag = (mid - (a + c) * 0.5).norm().min((mid - (b + d) * 0.5).norm());
                let along = (mix(&row_w[r], &at_mids[i]) - (a + b) * 0.5).norm();
                across = across.max((mix(&w, &at_us[i]) - (a + d) * 0.5).norm());
                let e = us[i].floor() as usize;
                per_edge[e] = per_edge[e].max(diag).max(along);
            }
        }
        (per_edge, across)
    }

    /// The loft as a solid: its side cut on the grid, points on the exact surface, one face per
    /// edge, and its two end sections capped flat.
    #[track_caller]
    pub fn solid(&self) -> Result<Solid> {
        self.solid_at(Location::caller())
    }

    fn solid_at(&self, src: Src) -> Result<Solid> {
        let (us, vs) = self.grid();
        self.solid_grid(&us, &vs, src)
    }

    /// The loft as a solid cut on `us` and `vs`, a grid from [`SmoothLoft::grid`]: a caller that
    /// meets the loft's end with a solid of its own builds that solid on the same points
    /// ([`SmoothLoft::end_region`]).
    #[track_caller]
    pub fn solid_on(&self, us: &[f64], vs: &[f64]) -> Result<Solid> {
        self.solid_grid(us, vs, Location::caller())
    }

    /// The first section, or the last, cut at `us` as the loft's own cap is: the region a solid
    /// that meets the loft's end is extruded or swept from, so the two meet point for point.
    pub fn end_region(&self, last: bool, us: &[f64]) -> Region {
        let s = if last { &self.sections[self.sections.len() - 1] } else { &self.sections[0] };
        let curves = s
            .edges
            .iter()
            .map(|e| match (e, e.circle()) {
                (LoftEdge::Line { .. }, _) => Curve::Line,
                (_, Some((c, axis, r))) => Curve::Circle { c, axis, r },
                _ => Curve::Free("ELLIPSE"),
            })
            .collect();
        let last_edge = s.edges.len() as u32 - 1;
        Region {
            loops: vec![RLoop {
                pts: us.iter().map(|&u| s.at(u)).collect(),
                seg: us.iter().map(|&u| (u.floor().max(0.0) as u32).min(last_edge)).collect(),
            }],
            curves,
        }
    }

    fn solid_grid(&self, us: &[f64], vs: &[f64], src: Src) -> Result<Solid> {
        let m = self.sections[0].edges.len();
        let (nu, nv) = (us.len(), vs.len() - 1);
        let at_us: Vec<Vec<V3>> = us.iter().map(|&u| self.ring(u)).collect();
        let at_mids: Vec<Vec<V3>> = (0..nu).map(|i| self.ring(mid_u(us, i, m))).collect();
        let mut verts = Vec::with_capacity(nu * vs.len());
        for (r, &v) in vs.iter().enumerate() {
            if r == 0 || r == nv {
                let k = if r == 0 { 0 } else { self.sections.len() - 1 };
                verts.extend(at_us.iter().map(|ring| ring[k]));
            } else {
                let w = self.weights(v);
                verts.extend(at_us.iter().map(|ring| mix(&w, ring)));
            }
        }
        let mut faces: Vec<Face> = (0..m).map(|_| Face::new(Surface::Free { kind: "BSPLINE" }, "loft", src)).collect();
        let mut tris: Vec<[u32; 3]> = vec![];
        let mut fids: Vec<u32> = vec![];
        for r in 0..nv {
            let w = self.weights(0.5 * (vs[r] + vs[r + 1]));
            for i in 0..nu {
                let j = (i + 1) % nu;
                let (a, b, c, d) = (r * nu + i, r * nu + j, (r + 1) * nu + j, (r + 1) * nu + i);
                let mid = mix(&w, &at_mids[i]);
                let (pa, pb, pc, pd) = (verts[a], verts[b], verts[c], verts[d]);
                let f = us[i].floor() as u32;
                if (mid - (pa + pc) * 0.5).norm() <= (mid - (pb + pd) * 0.5).norm() {
                    tris.push([a as u32, b as u32, c as u32]);
                    tris.push([a as u32, c as u32, d as u32]);
                } else {
                    tris.push([a as u32, b as u32, d as u32]);
                    tris.push([b as u32, c as u32, d as u32]);
                }
                fids.extend([f, f]);
            }
        }
        let mut caps = vec![];
        for (row, flip) in [(0usize, true), (nv, false)] {
            let ring: Vec<V3> = (0..nu).map(|i| verts[row * nu + i]).collect();
            let normal = newell(&ring);
            let (_, x, y) = plane_frame(normal);
            let flat: Vec<V2> = ring.iter().map(|p| v2(p.dot(x), p.dot(y))).collect();
            let fid = faces.len() as u32;
            faces.push(Face::new(Surface::Plane { p: ring[0], n: if flip { -normal } else { normal } }, "loft", src));
            for t in triangulate(&[flat])? {
                let t = t.map(|k| k + (row * nu) as u32);
                tris.push(if flip { [t[0], t[2], t[1]] } else { t });
                fids.push(fid);
            }
            caps.push(fid);
        }
        if signed_volume(&verts, &tris) < 0.0 {
            for t in &mut tris {
                t.swap(1, 2);
            }
            for &fid in &caps {
                if let Surface::Plane { p, n } = faces[fid as usize].surface {
                    faces[fid as usize].surface = Surface::Plane { p, n: -n };
                }
            }
        }
        Ok(Part { verts, tris, fids, faces }.solid())
    }
}

/// The points of `ring` blended by the weights `w`, in order.
fn mix(w: &[f64], ring: &[V3]) -> V3 {
    let mut p = V3::ZERO;
    for (wj, r) in w.iter().zip(ring) {
        p += *r * *wj;
    }
    p
}

/// The middle in `u` of the quad from `us[i]` to the next cut, the last running round to `m`.
fn mid_u(us: &[f64], i: usize, m: usize) -> f64 {
    let j = (i + 1) % us.len();
    let u1 = if j == 0 { m as f64 } else { us[j] };
    0.5 * (us[i] + u1)
}

/// Equal steps along each edge, `counts[e]` of them along edge `e`.
fn cuts(counts: &[usize]) -> Vec<f64> {
    let mut us = vec![];
    for (e, &c) in counts.iter().enumerate() {
        us.extend((0..c).map(|k| e as f64 + k as f64 / c as f64));
    }
    us
}

/// Equal steps along a sampled curve that keep its chords within `tol` of it and its turns
/// within ANGULAR: the largest second difference over the samples bounds the sag.
fn steps_for(samples: &[V3], tol: f64) -> usize {
    let n = samples.len() - 1;
    let mut m2: f64 = 0.0;
    let mut turn = 0.0;
    for w in samples.windows(3) {
        m2 = m2.max((w[0] - w[1] * 2.0 + w[2]).norm() * (n * n) as f64);
        let (a, b) = (w[1] - w[0], w[2] - w[1]);
        if a.norm() > 1e-12 && b.norm() > 1e-12 {
            turn += angle(a, b);
        }
    }
    let by_chord = (m2 / (8.0 * tol)).sqrt().ceil();
    let by_turn = (turn / ANGULAR).ceil();
    by_chord.max(by_turn).max(1.0) as usize
}

impl Solid {
    /// CadQuery's `Solid.makeLoft`: the sections made compatible as OCCT makes them, then ruled
    /// edge by edge when `ruled` or when there are only two, one smooth surface otherwise.
    #[track_caller]
    pub fn thru_sections(sections: &[LoftSection], ruled: bool) -> Result<Solid> {
        let src: Src = Location::caller();
        let sections = compatible(sections)?;
        if ruled || sections.len() == 2 {
            let regions: Vec<Region> = sections.iter().map(LoftSection::region).collect();
            Ok(crate::sweep::loft(&regions, src, "loft")?.solid())
        } else {
            SmoothLoft::new(&sections)?.solid_at(src)
        }
    }
}
