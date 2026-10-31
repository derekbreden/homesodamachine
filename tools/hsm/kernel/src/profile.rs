//! Planar profiles drawn exactly — lines, arcs, circles and Béziers — then placed on a
//! workplane and cut into points by the rule.
//!
//! A `Loop` is a closed chain of segments, each starting where the last one ends. A `Profile`
//! is an outer loop and the holes inside it. `Profile::place` puts it on a `Plane` and returns
//! a `Region`: the loops as points, each segment naming the curve it came from, so an arc
//! becomes one cylinder face when extruded and one torus or sphere when revolved, whatever
//! number of segments the rule cut it into.
use crate::math::{PI, TAU, V2, V3, atan2, cos, sin, tan, v2};
use crate::plane::Plane;
use crate::rule::{ANGULAR, LINEAR, arc_points, circle_points};
use anyhow::{Result, bail, ensure};

/// One segment of a loop. An arc runs from `a` to `b` about `c`, counterclockwise when `ccw`;
/// its radius is `|a - c|`. A circle is a loop by itself.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Seg {
    Line { a: V2, b: V2 },
    Arc { a: V2, b: V2, c: V2, ccw: bool },
    Circle { c: V2, r: f64 },
    Quad { a: V2, c: V2, b: V2 },
    Cubic { a: V2, c1: V2, c2: V2, b: V2 },
}

impl Seg {
    pub fn start(&self) -> V2 {
        match *self {
            Seg::Line { a, .. } | Seg::Arc { a, .. } | Seg::Quad { a, .. } | Seg::Cubic { a, .. } => a,
            Seg::Circle { c, r } => c + v2(r, 0.0),
        }
    }

    pub fn end(&self) -> V2 {
        match *self {
            Seg::Line { b, .. } | Seg::Arc { b, .. } | Seg::Quad { b, .. } | Seg::Cubic { b, .. } => b,
            Seg::Circle { c, r } => c + v2(r, 0.0),
        }
    }

    pub fn reversed(&self) -> Seg {
        match *self {
            Seg::Line { a, b } => Seg::Line { a: b, b: a },
            Seg::Arc { a, b, c, ccw } => Seg::Arc { a: b, b: a, c, ccw: !ccw },
            Seg::Circle { c, r } => Seg::Circle { c, r },
            Seg::Quad { a, c, b } => Seg::Quad { a: b, c, b: a },
            Seg::Cubic { a, c1, c2, b } => Seg::Cubic { a: b, c1: c2, c2: c1, b: a },
        }
    }

    /// The signed turn of an arc, positive counterclockwise, in (0, 2π] by magnitude.
    fn sweep(a: V2, b: V2, c: V2, ccw: bool) -> f64 {
        let t0 = (a - c).angle();
        let t1 = (b - c).angle();
        let mut s = t1 - t0;
        if ccw {
            while s <= 1e-12 {
                s += TAU;
            }
        } else {
            while s >= -1e-12 {
                s -= TAU;
            }
        }
        s
    }

    /// ½∮(x dy − y dx) along the segment: summed round a loop, its signed area.
    fn area_term(&self) -> f64 {
        match *self {
            Seg::Line { a, b } => 0.5 * a.cross(b),
            Seg::Arc { a, b, c, ccw } => {
                let r = (a - c).norm();
                0.5 * (c.cross(b - a) + r * r * Seg::sweep(a, b, c, ccw))
            }
            Seg::Circle { r, .. } => PI * r * r,
            Seg::Quad { a, c, b } => (2.0 * a.cross(c) + 2.0 * c.cross(b) + a.cross(b)) / 6.0,
            Seg::Cubic { a, c1, c2, b } => {
                (6.0 * a.cross(c1) + 3.0 * a.cross(c2) + a.cross(b) + 3.0 * c1.cross(c2)
                    + 3.0 * c1.cross(b)
                    + 6.0 * c2.cross(b))
                    / 20.0
            }
        }
    }

    /// The unit tangent leaving the start and arriving at the end.
    fn tangents(&self) -> (V2, V2) {
        match *self {
            Seg::Line { a, b } => {
                let t = (b - a).unit();
                (t, t)
            }
            Seg::Arc { a, b, c, ccw } => {
                let s = if ccw { 1.0 } else { -1.0 };
                ((a - c).perp().unit() * s, (b - c).perp().unit() * s)
            }
            Seg::Circle { .. } => (v2(0.0, 1.0), v2(0.0, 1.0)),
            Seg::Quad { a, c, b } => (lead(a, &[c, b]), lead(b, &[c, a]) * -1.0),
            Seg::Cubic { a, c1, c2, b } => (lead(a, &[c1, c2, b]), lead(b, &[c2, c1, a]) * -1.0),
        }
    }
}

/// The direction from `p` to the first of `next` that is not `p` itself.
fn lead(p: V2, next: &[V2]) -> V2 {
    for &q in next {
        if (q - p).norm() > 1e-12 {
            return (q - p).unit();
        }
    }
    v2(1.0, 0.0)
}

/// A closed chain of segments.
#[derive(Clone, Debug, PartialEq)]
pub struct Loop {
    pub segs: Vec<Seg>,
}

impl Loop {
    pub fn new(segs: Vec<Seg>) -> Result<Loop> {
        ensure!(!segs.is_empty(), "a loop needs a segment");
        if segs.len() == 1 {
            ensure!(
                matches!(segs[0], Seg::Circle { .. }) || (segs[0].start() - segs[0].end()).norm() < 1e-9,
                "a loop of one segment closes on itself"
            );
        } else {
            for i in 0..segs.len() {
                let (s, t) = (&segs[i], &segs[(i + 1) % segs.len()]);
                let gap = (s.end() - t.start()).norm();
                ensure!(gap < 1e-9, "loop segment {i} ends {gap:e} mm from where the next starts");
                ensure!(!matches!(s, Seg::Circle { .. }), "a circle is a loop by itself");
            }
        }
        Ok(Loop { segs })
    }

    /// Straight lines through `pts`, closing back to the first.
    pub fn polygon(pts: &[V2]) -> Loop {
        let mut pts: Vec<V2> = pts.to_vec();
        if pts.len() > 1 && pts[0] == pts[pts.len() - 1] {
            pts.pop();
        }
        let n = pts.len();
        Loop {
            segs: (0..n).map(|i| Seg::Line { a: pts[i], b: pts[(i + 1) % n] }).collect(),
        }
    }

    pub fn circle(c: V2, r: f64) -> Loop {
        Loop { segs: vec![Seg::Circle { c, r }] }
    }

    /// A `w` by `h` rectangle centered on `c`.
    pub fn rect(c: V2, w: f64, h: f64) -> Loop {
        let (x0, x1, y0, y1) = (c.x - w / 2.0, c.x + w / 2.0, c.y - h / 2.0, c.y + h / 2.0);
        Loop::polygon(&[v2(x0, y0), v2(x1, y0), v2(x1, y1), v2(x0, y1)])
    }

    /// A `w` by `h` rectangle centered on `c` with its corners rounded to `r`.
    pub fn rounded_rect(c: V2, w: f64, h: f64, r: f64) -> Result<Loop> {
        Loop::rect(c, w, h).fillet(r)
    }

    /// CadQuery's `slot2D`: `length` end to end, `width` across, its axis at `angle` degrees.
    pub fn slot(c: V2, length: f64, width: f64, angle_deg: f64) -> Loop {
        let r = width / 2.0;
        let half = length / 2.0 - r;
        let a = crate::math::radians(angle_deg);
        let u = v2(cos(a), sin(a));
        let n = u.perp();
        let (p0, p1) = (c - u * half, c + u * half);
        Loop {
            segs: vec![
                Seg::Line { a: p0 - n * r, b: p1 - n * r },
                Seg::Arc { a: p1 - n * r, b: p1 + n * r, c: p1, ccw: true },
                Seg::Line { a: p1 + n * r, b: p0 + n * r },
                Seg::Arc { a: p0 + n * r, b: p0 - n * r, c: p0, ccw: true },
            ],
        }
    }

    /// The regular `n`-gon whose circumscribed circle has diameter `d`, CadQuery's `polygon`.
    pub fn regular(c: V2, n: usize, d: f64) -> Loop {
        let pts: Vec<V2> = (0..n)
            .map(|i| {
                let a = TAU * i as f64 / n as f64;
                c + v2(cos(a), sin(a)) * (d / 2.0)
            })
            .collect();
        Loop::polygon(&pts)
    }

    /// Signed area, positive counterclockwise.
    pub fn area(&self) -> f64 {
        self.segs.iter().map(Seg::area_term).sum()
    }

    pub fn reversed(&self) -> Loop {
        Loop { segs: self.segs.iter().rev().map(Seg::reversed).collect() }
    }

    pub fn ccw(&self) -> Loop {
        if self.area() < 0.0 { self.reversed() } else { self.clone() }
    }

    pub fn translated(&self, d: V2) -> Loop {
        let m = |p: V2| p + d;
        Loop { segs: self.segs.iter().map(|s| map_seg(s, m)).collect() }
    }

    /// Every corner between two segments rounded to radius `r`.
    pub fn fillet(&self, r: f64) -> Result<Loop> {
        let all: Vec<usize> = (0..self.segs.len()).collect();
        self.fillet_corners(&all, r)
    }

    /// The corners `which` rounded to radius `r`. Corner `i` is where segment `i` ends and
    /// segment `i + 1` begins. A corner whose segments already meet tangent is left as it is.
    pub fn fillet_corners(&self, which: &[usize], r: f64) -> Result<Loop> {
        ensure!(r > 0.0, "a fillet radius is positive");
        let n = self.segs.len();
        let mut segs = self.segs.clone();
        let mut arcs: Vec<Option<Seg>> = vec![None; n];
        for &i in which {
            ensure!(i < n, "corner {i} of a loop of {n} segments");
            let j = (i + 1) % n;
            let (s, t) = (segs[i], segs[j]);
            let (_, tin) = s.tangents();
            let (tout, _) = t.tangents();
            let turn = tin.cross(tout);
            if turn.abs() < 1e-9 && tin.dot(tout) > 0.0 {
                continue;
            }
            let (s2, arc, t2) = fillet_corner(&s, &t, r, turn > 0.0)
                .map_err(|e| anyhow::anyhow!("corner {i}: {e}"))?;
            segs[i] = s2;
            segs[j] = t2;
            arcs[i] = Some(arc);
        }
        let mut out = Vec::with_capacity(n * 2);
        for i in 0..n {
            out.push(segs[i]);
            if let Some(a) = arcs[i] {
                out.push(a);
            }
        }
        Loop::new(out)
    }

    /// The loop moved `d` outward from the region it bounds when counterclockwise (inward when
    /// `d` is negative), each line staying a line and each arc an arc about its own center.
    /// `round` joins the corners that open with arcs about the corner; otherwise the
    /// neighbours run on to meet.
    pub fn offset(&self, d: f64, round: bool) -> Result<Loop> {
        if d == 0.0 {
            return Ok(self.clone());
        }
        if let [Seg::Circle { c, r }] = self.segs[..] {
            let s = if self.area() > 0.0 { 1.0 } else { -1.0 };
            let r2 = r + s * d;
            ensure!(r2 > 0.0, "an offset of {d} closes a circle of radius {r}");
            return Ok(Loop::circle(c, r2));
        }
        // Each segment moved to its right: outward for a counterclockwise loop.
        let mut moved: Vec<Option<Seg>> = Vec::with_capacity(self.segs.len());
        for s in &self.segs {
            moved.push(match *s {
                Seg::Line { a, b } => {
                    let n = (b - a).unit().perp() * -1.0;
                    Some(Seg::Line { a: a + n * d, b: b + n * d })
                }
                Seg::Arc { a, b, c, ccw } => {
                    let r = (a - c).norm();
                    let r2 = if ccw { r + d } else { r - d };
                    if r2 <= 1e-9 {
                        None
                    } else {
                        Some(Seg::Arc { a: c + (a - c) * (r2 / r), b: c + (b - c) * (r2 / r), c, ccw })
                    }
                }
                _ => bail!("an offset of a loop with a {} segment", seg_kind(s)),
            });
        }
        let n = self.segs.len();
        let kept: Vec<usize> = (0..n).filter(|&i| moved[i].is_some()).collect();
        ensure!(kept.len() >= 2, "an offset of {d} closes the loop");
        let mut segs: Vec<Seg> = kept.iter().map(|&i| moved[i].unwrap()).collect();
        let m = segs.len();
        let mut joins: Vec<Option<Seg>> = vec![None; m];
        for k in 0..m {
            let (i, j) = (kept[k], kept[(k + 1) % m]);
            let corner = self.segs[i].end();
            let (s, t) = (segs[k], segs[(k + 1) % m]);
            let (_, tin) = s.tangents();
            let (tout, _) = t.tangents();
            let gap = (s.end() - t.start()).norm();
            let skipped = (i + 1) % n != j;
            if gap < 1e-9 && !skipped {
                let p = s.end();
                segs[(k + 1) % m] = with_start(&t, p);
                continue;
            }
            let opens = tin.cross(tout) * d > 0.0 && !skipped;
            if opens && round {
                joins[k] = Some(Seg::Arc { a: s.end(), b: t.start(), c: corner, ccw: d > 0.0 });
                continue;
            }
            let near = (s.end() + t.start()) * 0.5;
            let p = meet(&s, &t, near)
                .ok_or_else(|| anyhow::anyhow!("offset {d}: segments {i} and {j} no longer meet"))?;
            segs[k] = with_end(&segs[k], p);
            segs[(k + 1) % m] = with_start(&segs[(k + 1) % m], p);
        }
        let mut out = Vec::with_capacity(2 * m);
        for k in 0..m {
            out.push(segs[k]);
            if let Some(j) = joins[k] {
                out.push(j);
            }
        }
        let lp = Loop::new(out)?;
        ensure!(lp.area() * self.area() > 0.0, "an offset of {d} turns the loop inside out");
        Ok(lp)
    }
}

fn seg_kind(s: &Seg) -> &'static str {
    match s {
        Seg::Line { .. } => "line",
        Seg::Arc { .. } => "arc",
        Seg::Circle { .. } => "circle",
        Seg::Quad { .. } => "quadratic Bézier",
        Seg::Cubic { .. } => "cubic Bézier",
    }
}

fn map_seg(s: &Seg, m: impl Fn(V2) -> V2) -> Seg {
    match *s {
        Seg::Line { a, b } => Seg::Line { a: m(a), b: m(b) },
        Seg::Arc { a, b, c, ccw } => Seg::Arc { a: m(a), b: m(b), c: m(c), ccw },
        Seg::Circle { c, r } => Seg::Circle { c: m(c), r },
        Seg::Quad { a, c, b } => Seg::Quad { a: m(a), c: m(c), b: m(b) },
        Seg::Cubic { a, c1, c2, b } => Seg::Cubic { a: m(a), c1: m(c1), c2: m(c2), b: m(b) },
    }
}

fn with_start(s: &Seg, p: V2) -> Seg {
    match *s {
        Seg::Line { b, .. } => Seg::Line { a: p, b },
        Seg::Arc { b, c, ccw, .. } => Seg::Arc { a: p, b, c, ccw },
        other => other,
    }
}

fn with_end(s: &Seg, p: V2) -> Seg {
    match *s {
        Seg::Line { a, .. } => Seg::Line { a, b: p },
        Seg::Arc { a, c, ccw, .. } => Seg::Arc { a, b: p, c, ccw },
        other => other,
    }
}

/// A line or a circle, the carrier of a line or arc segment.
#[derive(Clone, Copy, Debug)]
enum Carrier {
    /// Points `x` with `n·x = off`, `n` unit.
    Line { n: V2, off: f64 },
    Circle { c: V2, r: f64 },
}

fn carrier(s: &Seg) -> Option<Carrier> {
    match *s {
        Seg::Line { a, b } => {
            let n = (b - a).unit().perp();
            Some(Carrier::Line { n, off: n.dot(a) })
        }
        Seg::Arc { a, c, .. } => Some(Carrier::Circle { c, r: (a - c).norm() }),
        _ => None,
    }
}

fn crossings(p: Carrier, q: Carrier) -> Vec<V2> {
    match (p, q) {
        (Carrier::Line { n: n1, off: o1 }, Carrier::Line { n: n2, off: o2 }) => {
            let det = n1.cross(n2);
            if det.abs() < 1e-14 {
                return vec![];
            }
            vec![v2((o1 * n2.y - o2 * n1.y) / det, (n1.x * o2 - n2.x * o1) / det)]
        }
        (Carrier::Circle { .. }, Carrier::Line { .. }) => crossings(q, p),
        (Carrier::Line { n, off }, Carrier::Circle { c, r }) => {
            let foot = c + n * (off - n.dot(c));
            let h2 = r * r - (foot - c).dot(foot - c);
            if h2 < -1e-12 {
                return vec![];
            }
            let h = h2.max(0.0).sqrt();
            let t = n.perp();
            vec![foot + t * h, foot - t * h]
        }
        (Carrier::Circle { c: c1, r: r1 }, Carrier::Circle { c: c2, r: r2 }) => {
            let dv = c2 - c1;
            let dist = dv.norm();
            if dist < 1e-14 {
                return vec![];
            }
            let a = (r1 * r1 - r2 * r2 + dist * dist) / (2.0 * dist);
            let h2 = r1 * r1 - a * a;
            if h2 < -1e-12 {
                return vec![];
            }
            let base = c1 + dv * (a / dist);
            let perp = dv.perp() / dist;
            let h = h2.max(0.0).sqrt();
            vec![base + perp * h, base - perp * h]
        }
    }
}

/// Where the carriers of `s` and `t` cross nearest `near`.
fn meet(s: &Seg, t: &Seg, near: V2) -> Option<V2> {
    let (p, q) = (carrier(s)?, carrier(t)?);
    crossings(p, q)
        .into_iter()
        .min_by(|a, b| (*a - near).norm().total_cmp(&(*b - near).norm()))
}

/// `c` moved `r` to the left of travel along `s` (to the right when `left` is false).
fn shifted(s: &Seg, r: f64, left: bool) -> Option<Carrier> {
    let side = if left { 1.0 } else { -1.0 };
    match *s {
        Seg::Line { a, b } => {
            let n = (b - a).unit().perp();
            Some(Carrier::Line { n, off: n.dot(a) + side * r })
        }
        Seg::Arc { a, c, ccw, .. } => {
            let r0 = (a - c).norm();
            // Left of a counterclockwise arc is its center.
            let toward = if ccw { side } else { -side };
            Some(Carrier::Circle { c, r: r0 - toward * r })
        }
        _ => None,
    }
}

fn foot(s: &Seg, x: V2) -> V2 {
    match *s {
        Seg::Line { a, b } => {
            let u = (b - a).unit();
            a + u * (x - a).dot(u)
        }
        Seg::Arc { a, c, .. } => {
            let r = (a - c).norm();
            c + (x - c).unit() * r
        }
        _ => x,
    }
}

/// Whether `p`, on the carrier of `s`, lies on the segment itself.
fn holds(s: &Seg, p: V2) -> bool {
    match *s {
        Seg::Line { a, b } => {
            let u = b - a;
            let t = (p - a).dot(u) / u.dot(u);
            (-1e-9..=1.0 + 1e-9).contains(&t)
        }
        Seg::Arc { a, b, c, ccw } => {
            let total = Seg::sweep(a, b, c, ccw).abs();
            let part = Seg::sweep(a, p, c, ccw).abs();
            (p - a).norm() < 1e-9 || (p - b).norm() < 1e-9 || part <= total + 1e-12
        }
        _ => false,
    }
}

/// The corner between `s` (ending there) and `t` (starting there) rounded to `r`: `s` cut back,
/// the arc, and `t` cut back.
fn fillet_corner(s: &Seg, t: &Seg, r: f64, left: bool) -> Result<(Seg, Seg, Seg)> {
    let corner = s.end();
    if let (Seg::Line { a, .. }, Seg::Line { b, .. }) = (*s, *t) {
        let u = (corner - a).unit();
        let w = (b - corner).unit();
        let theta = (-u).dot(w).clamp(-1.0, 1.0).acos();
        let back = r / tan(theta / 2.0);
        ensure!(
            back <= (corner - a).norm() + 1e-9 && back <= (b - corner).norm() + 1e-9,
            "a fillet of radius {r} needs {back:.4} mm of each side"
        );
        let p1 = corner - u * back;
        let p2 = corner + w * back;
        let bis = (w - u).unit();
        let c = corner + bis * (r / sin(theta / 2.0));
        return Ok((with_end(s, p1), Seg::Arc { a: p1, b: p2, c, ccw: left }, with_start(t, p2)));
    }
    let (p, q) = match (shifted(s, r, left), shifted(t, r, left)) {
        (Some(p), Some(q)) => (p, q),
        _ => bail!("a fillet between a {} and a {}", seg_kind(s), seg_kind(t)),
    };
    let c = crossings(p, q)
        .into_iter()
        .filter(|x| holds(s, foot(s, *x)) && holds(t, foot(t, *x)))
        .min_by(|a, b| (*a - corner).norm().total_cmp(&(*b - corner).norm()))
        .ok_or_else(|| anyhow::anyhow!("no fillet of radius {r} fits this corner"))?;
    let (p1, p2) = (foot(s, c), foot(t, c));
    Ok((with_end(s, p1), Seg::Arc { a: p1, b: p2, c, ccw: left }, with_start(t, p2)))
}

/// An outer loop and the holes inside it.
#[derive(Clone, Debug, PartialEq)]
pub struct Profile {
    pub outer: Loop,
    pub holes: Vec<Loop>,
}

impl Profile {
    pub fn new(outer: Loop) -> Profile {
        Profile { outer, holes: vec![] }
    }

    pub fn with_hole(mut self, hole: Loop) -> Profile {
        self.holes.push(hole);
        self
    }

    pub fn polygon(pts: &[V2]) -> Profile {
        Profile::new(Loop::polygon(pts))
    }

    pub fn circle(c: V2, r: f64) -> Profile {
        Profile::new(Loop::circle(c, r))
    }

    pub fn rect(c: V2, w: f64, h: f64) -> Profile {
        Profile::new(Loop::rect(c, w, h))
    }

    /// The region's area: the outer loop's less its holes'.
    pub fn area(&self) -> f64 {
        self.outer.area().abs() - self.holes.iter().map(|h| h.area().abs()).sum::<f64>()
    }

    pub fn translated(&self, d: V2) -> Profile {
        Profile {
            outer: self.outer.translated(d),
            holes: self.holes.iter().map(|h| h.translated(d)).collect(),
        }
    }

    /// Grown by `d` (shrunk when negative): the outer loop moves out, the holes in.
    pub fn offset(&self, d: f64, round: bool) -> Result<Profile> {
        Ok(Profile {
            outer: self.outer.ccw().offset(d, round)?,
            holes: self
                .holes
                .iter()
                .map(|h| h.ccw().reversed().offset(d, round))
                .collect::<Result<_>>()?,
        })
    }

    /// The profile on `plane`, cut into points by the rule.
    pub fn place(&self, plane: &Plane) -> Region {
        let mut region = Region { loops: vec![], curves: vec![] };
        for lp in std::iter::once(&self.outer).chain(&self.holes) {
            region.add(lp, plane);
        }
        region
    }
}

/// What a region segment lies on.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Curve {
    Line,
    Circle { c: V3, axis: V3, r: f64 },
    Free(&'static str),
}

/// A closed polygon of a region: `seg[i]` names the curve of the segment from point `i` to
/// point `i + 1`.
#[derive(Clone, Debug, PartialEq)]
pub struct RLoop {
    pub pts: Vec<V3>,
    pub seg: Vec<u32>,
}

/// A profile cut into points: loops, the outer first, and the curves their segments lie on.
#[derive(Clone, Debug, PartialEq)]
pub struct Region {
    pub loops: Vec<RLoop>,
    pub curves: Vec<Curve>,
}

impl Region {
    fn add(&mut self, lp: &Loop, plane: &Plane) {
        let mut pts = vec![];
        let mut seg = vec![];
        for s in &lp.segs {
            let ci = self.curves.len() as u32;
            let (mut p, curve) = seg_points(s, plane);
            if !matches!(s, Seg::Circle { .. }) {
                p.pop();
            }
            seg.extend(std::iter::repeat_n(ci, p.len()));
            pts.extend(p);
            self.curves.push(curve);
        }
        self.loops.push(RLoop { pts, seg });
    }

    /// A region of one polygon whose every segment is a line.
    pub fn polygon(pts: Vec<V3>) -> Region {
        let n = pts.len();
        Region {
            loops: vec![RLoop { pts, seg: (0..n as u32).collect() }],
            curves: vec![Curve::Line; n],
        }
    }
}

/// The rule's points along a segment placed on `plane`, from its start to its end inclusive
/// (a circle's whole ring, unclosed), and the curve it lies on.
fn seg_points(s: &Seg, plane: &Plane) -> (Vec<V3>, Curve) {
    let z = plane.z;
    match *s {
        Seg::Line { a, b } => (vec![plane.point(a), plane.point(b)], Curve::Line),
        Seg::Arc { a, b, c, ccw } => {
            let r = (a - c).norm();
            let (c3, a3, b3) = (plane.point(c), plane.point(a), plane.point(b));
            let pts = arc_points(c3, z, r, a3, b3, if ccw { z } else { -z });
            (pts, Curve::Circle { c: c3, axis: z, r })
        }
        Seg::Circle { c, r } => {
            let c3 = plane.point(c);
            (circle_points(c3, z, r), Curve::Circle { c: c3, axis: z, r })
        }
        Seg::Quad { a, c, b } => {
            let n = bezier_steps(&[a, c, b]);
            let pts = (0..=n)
                .map(|i| {
                    let t = i as f64 / n as f64;
                    let u = 1.0 - t;
                    plane.point(a * (u * u) + c * (2.0 * u * t) + b * (t * t))
                })
                .collect();
            (pts, Curve::Free("BSPLINE"))
        }
        Seg::Cubic { a, c1, c2, b } => {
            let n = bezier_steps(&[a, c1, c2, b]);
            let pts = (0..=n)
                .map(|i| {
                    let t = i as f64 / n as f64;
                    let u = 1.0 - t;
                    plane.point(
                        a * (u * u * u) + c1 * (3.0 * u * u * t) + c2 * (3.0 * u * t * t) + b * (t * t * t),
                    )
                })
                .collect();
            (pts, Curve::Free("BSPLINE"))
        }
    }
}

/// Equal parameter steps that keep a Bézier within the rule: a span h of a curve whose second
/// derivative is at most M strays at most M h²/8 from its chord, and the tangent turns no more
/// than the control polygon does.
fn bezier_steps(ctrl: &[V2]) -> usize {
    let deg = (ctrl.len() - 1) as f64;
    let mut m: f64 = 0.0;
    for w in ctrl.windows(3) {
        m = m.max((w[0] - w[1] * 2.0 + w[2]).norm());
    }
    let m = m * deg * (deg - 1.0);
    let mut turn = 0.0;
    for w in ctrl.windows(3) {
        let (u, v) = (w[1] - w[0], w[2] - w[1]);
        if u.norm() > 1e-12 && v.norm() > 1e-12 {
            turn += atan2(u.cross(v), u.dot(v)).abs();
        }
    }
    let by_chord = (m / (8.0 * LINEAR)).sqrt().ceil();
    let by_turn = (turn / ANGULAR).ceil();
    (by_chord.max(by_turn).max(1.0)) as usize
}

/// A pen that draws a loop segment by segment from a start point.
#[derive(Clone, Debug)]
pub struct Pen {
    start: V2,
    at: V2,
    segs: Vec<Seg>,
}

impl Pen {
    pub fn new(start: V2) -> Pen {
        Pen { start, at: start, segs: vec![] }
    }

    pub fn at(&self) -> V2 {
        self.at
    }

    pub fn line_to(mut self, p: V2) -> Pen {
        self.segs.push(Seg::Line { a: self.at, b: p });
        self.at = p;
        self
    }

    pub fn line_by(self, d: V2) -> Pen {
        let p = self.at + d;
        self.line_to(p)
    }

    /// An arc about `c` to `p`, counterclockwise when `ccw`.
    pub fn arc_center(mut self, c: V2, p: V2, ccw: bool) -> Pen {
        self.segs.push(Seg::Arc { a: self.at, b: p, c, ccw });
        self.at = p;
        self
    }

    /// The arc through `mid` to `p`, CadQuery's `threePointArc`.
    pub fn arc_through(self, mid: V2, p: V2) -> Result<Pen> {
        let a = self.at;
        let (b1, b2) = (mid - a, p - a);
        let d = 2.0 * b1.cross(b2);
        ensure!(d.abs() > 1e-14, "three collinear points make no arc");
        let c = a + v2(
            (b2.y * b1.dot(b1) - b1.y * b2.dot(b2)) / d,
            (b1.x * b2.dot(b2) - b2.x * b1.dot(b1)) / d,
        );
        let ccw = (mid - a).cross(p - mid) > 0.0;
        Ok(self.arc_center(c, p, ccw))
    }

    /// CadQuery's `radiusArc`: the arc of radius |r| to `p`, its center on the right of the
    /// chord for positive `r`.
    pub fn radius_arc(self, p: V2, r: f64) -> Result<Pen> {
        let a = self.at;
        let chord = p - a;
        let half = chord.norm() / 2.0;
        ensure!(r.abs() >= half - 1e-12, "radius {r} is shorter than half the chord {half}");
        let h = (r * r - half * half).max(0.0).sqrt();
        let mid = (a + p) * 0.5;
        let right = chord.unit().perp() * -1.0;
        let c = if r > 0.0 { mid + right * h } else { mid - right * h };
        Ok(self.arc_center(c, p, r < 0.0))
    }

    /// The arc to `p` leaving tangent to the last segment.
    pub fn tangent_arc(self, p: V2) -> Result<Pen> {
        let a = self.at;
        let t = match self.segs.last() {
            Some(s) => s.tangents().1,
            None => bail!("a tangent arc needs a segment before it"),
        };
        let chord = p - a;
        let denom = 2.0 * t.perp().dot(chord);
        ensure!(denom.abs() > 1e-14, "a tangent arc to a point straight ahead is a line");
        let c = a + t.perp() * (chord.dot(chord) / denom);
        let ccw = t.cross(chord) > 0.0;
        Ok(self.arc_center(c, p, ccw))
    }

    /// The loop, closed with a line back to the start when the pen is elsewhere.
    pub fn close(mut self) -> Result<Loop> {
        if (self.at - self.start).norm() > 1e-12 {
            self.segs.push(Seg::Line { a: self.at, b: self.start });
        } else if let Some(last) = self.segs.pop() {
            self.segs.push(with_end(&last, self.start));
        }
        Loop::new(self.segs)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exact_areas() {
        assert!((Loop::rect(V2::ZERO, 3.0, 2.0).area() - 6.0).abs() < 1e-12);
        assert!((Loop::circle(V2::ZERO, 2.0).area() - 4.0 * PI).abs() < 1e-12);
        let slot = Loop::slot(V2::ZERO, 10.0, 2.0, 30.0);
        assert!((slot.area() - (8.0 * 2.0 + PI)).abs() < 1e-12);
        let rr = Loop::rounded_rect(V2::ZERO, 10.0, 6.0, 1.0).unwrap();
        assert!((rr.area() - (60.0 - (4.0 - PI))).abs() < 1e-12);
    }

    #[test]
    fn offsets_keep_lines_and_arcs() {
        let rr = Loop::rounded_rect(V2::ZERO, 10.0, 6.0, 1.0).unwrap();
        let out = rr.offset(0.5, true).unwrap();
        assert!((out.area() - (11.0 * 7.0 - (4.0 - PI) * 2.25)).abs() < 1e-9);
        let inner = rr.offset(-2.0, true).unwrap();
        assert!((inner.area() - 6.0 * 2.0).abs() < 1e-9, "{}", inner.area());
        let sq = Loop::rect(V2::ZERO, 2.0, 2.0);
        let grown = sq.offset(1.0, true).unwrap();
        assert!((grown.area() - (4.0 + 8.0 + PI)).abs() < 1e-9);
        let mitred = sq.offset(1.0, false).unwrap();
        assert!((mitred.area() - 16.0).abs() < 1e-9);
    }

    #[test]
    fn pen_arcs() {
        let lp = Pen::new(v2(0.0, 0.0))
            .line_to(v2(2.0, 0.0))
            .arc_through(v2(3.0, 1.0), v2(2.0, 2.0))
            .unwrap()
            .line_to(v2(0.0, 2.0))
            .close()
            .unwrap();
        assert!((lp.area() - (4.0 + PI / 2.0)).abs() < 1e-12);
    }
}
