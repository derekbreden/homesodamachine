//! A solid's edges, as CadQuery's `edges()` lists them, and CadQuery's string selectors over
//! its edges and faces.
//!
//! The faces are `topo::faces`: connected runs of triangles on one surface. An edge is a run of
//! mesh edges between one pair of faces, broken wherever a third face meets it, so a box has
//! twelve edges and a box with its vertical edges rounded has eight round its top. An edge whose
//! points lie on one line is a LINE, on one circle a CIRCLE, and any other is OTHER. A circle's
//! center, axis and radius come from its faces' records where one is a plane and the other a
//! cylinder, cone or sphere about the plane's normal, and from its points otherwise.
//!
//! The selectors are CadQuery's, with its precedence: `and` before `or` before `exc`, and `not`
//! last of all, so `not |Z and >Y` is not (`|Z and >Y`).
//! - `|D` parallel and `#D` square to D: lines by their direction, planes by their normal.
//! - `+D`, `-D` and a bare D: planes facing D.
//! - `>D` and `<D`: the farthest and nearest along D by center. `>D[n]` is the n-th, among the
//!   lines or planes parallel to D, counted as CadQuery counts it; `>>D[n]` and `<<D[n]` count
//!   among all of them.
//! - `%TYPE`: LINE, CIRCLE or OTHER for an edge, its surface's kind for a face.
//! - The named views `front`, `back`, `left`, `right`, `top` and `bottom`.
//! - `and`, `or`, `exc` (or `except`) and `not`, with parentheses.
//!
//! D is X, Y, Z, XY, YZ, XZ or (x, y, z). Centers are CadQuery's `Center()`: a line's midpoint,
//! an arc's center of mass, a face's area centroid. Centers within 1e-4 along D are one rank.
use crate::face::Surface;
use crate::math::{PI, TAU, V3, acos, atan2, cos, sin, v3};
use crate::profile::Curve;
use crate::rule::{TOLERANCE, canonical_axis};
use crate::solid::Solid;
use crate::topo::{Faces, faces};
use anyhow::{Result, anyhow, bail, ensure};
use std::collections::{BTreeMap, HashMap, HashSet};
use std::fmt;

/// mm. An edge's points lie this near its line or circle.
const ON: f64 = 1e-6;

/// CadQuery's selector tolerance: on a direction's sine or angle, and between centers of one rank.
const PICK: f64 = 1e-4;

/// Where two faces of a solid meet.
#[derive(Clone, Debug, PartialEq)]
pub struct Edge {
    /// `Curve::Line` from the first point to the last, `Curve::Circle`, or `Curve::Free("OTHER")`.
    pub curve: Curve,
    /// Its points, the way the boundary of the first of its faces runs. A closed edge's first
    /// point is not repeated at its end.
    pub pts: Vec<V3>,
    pub closed: bool,
    /// CadQuery's `Center()`: a line's midpoint, a circle's center, an arc's center of mass.
    pub center: V3,
    /// Its two faces, as `topo::faces` numbers them.
    pub faces: [u32; 2],
    /// Its points as the solid's vertices.
    pub(crate) ids: Vec<u32>,
}

impl Edge {
    pub fn kind(&self) -> &'static str {
        match self.curve {
            Curve::Line => "LINE",
            Curve::Circle { .. } => "CIRCLE",
            Curve::Free(k) => k,
        }
    }

    pub fn length(&self) -> f64 {
        let n = self.pts.len();
        let open: f64 = self.pts.windows(2).map(|w| (w[1] - w[0]).norm()).sum();
        if self.closed { open + (self.pts[0] - self.pts[n - 1]).norm() } else { open }
    }

    /// For a circle, the sense it runs about its axis (1 counterclockwise, -1 clockwise) and the
    /// angle it turns from its first point to its last, a whole turn for a closed one.
    pub(crate) fn arc(&self) -> Option<(f64, f64)> {
        let Curve::Circle { c, axis, .. } = self.curve else { return None };
        let n = self.pts.len();
        let sense = if (self.pts[0] - c).cross(self.pts[1] - c).dot(axis) > 0.0 { 1.0 } else { -1.0 };
        let turn = if self.closed { TAU } else { turn_about(c, axis * sense, self.pts[0], self.pts[n - 1]) };
        Some((sense, turn))
    }

    /// The direction the edge runs at its start (`end` 0) or its end (`end` 1).
    pub(crate) fn tangent(&self, end: usize) -> V3 {
        let n = self.pts.len();
        let p = if end == 0 { self.pts[0] } else { self.pts[n - 1] };
        match self.curve {
            Curve::Line => (self.pts[n - 1] - self.pts[0]).unit(),
            Curve::Circle { c, axis, .. } => {
                let (sense, _) = self.arc().unwrap();
                (axis * sense).cross(p - c).unit()
            }
            Curve::Free(_) => {
                if end == 0 {
                    (self.pts[1] - self.pts[0]).unit()
                } else {
                    (self.pts[n - 1] - self.pts[n - 2]).unit()
                }
            }
        }
    }
}

impl fmt::Display for Edge {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let p = |q: V3| format!("({:.3}, {:.3}, {:.3})", q.x, q.y, q.z);
        match self.curve {
            Curve::Line => write!(f, "the line from {} to {}", p(self.pts[0]), p(self.pts[self.pts.len() - 1])),
            Curve::Circle { c, r, .. } if self.closed => write!(f, "the circle of radius {r:.3} about {}", p(c)),
            Curve::Circle { c, r, .. } => write!(f, "the arc of radius {r:.3} about {} from {}", p(c), p(self.pts[0])),
            Curve::Free(_) => write!(f, "the edge from {}", p(self.pts[0])),
        }
    }
}

/// Edges of one solid, in the order `Solid::edges` lists them.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Edges(pub Vec<Edge>);

impl std::ops::Deref for Edges {
    type Target = Vec<Edge>;
    fn deref(&self) -> &Vec<Edge> {
        &self.0
    }
}

impl Edges {
    /// The edges among these that `sel` picks; an empty `sel` picks them all.
    pub fn select(&self, sel: &str) -> Result<Edges> {
        if sel.trim().is_empty() {
            return Ok(self.clone());
        }
        let items: Vec<Item> = self.iter().map(edge_item).collect();
        let all: Vec<usize> = (0..items.len()).collect();
        let picked = pick(&parse(sel)?, &items, &all).map_err(|e| anyhow!("the selector {sel:?}: {e}"))?;
        Ok(Edges(picked.into_iter().map(|i| self[i].clone()).collect()))
    }

    /// The edge whose center lies nearest `p`, CadQuery's `NearestToPointSelector`.
    pub fn nearest(&self, p: V3) -> Result<Edges> {
        let best = self
            .iter()
            .min_by(|a, b| (a.center - p).norm().total_cmp(&(b.center - p).norm()))
            .ok_or_else(|| anyhow!("no edge to pick the nearest of"))?;
        Ok(Edges(vec![best.clone()]))
    }
}

impl Solid {
    /// The edges `sel` picks, CadQuery's `edges(sel)`; an empty `sel` picks them all.
    pub fn edges(&self, sel: &str) -> Result<Edges> {
        Edges(graph(self).edges).select(sel)
    }

    /// The edges of the faces `sel` picks, CadQuery's `faces(sel).edges()`.
    pub fn face_edges(&self, sel: &str) -> Result<Edges> {
        let g = graph(self);
        let items = face_items(self, &g.faces);
        let all: Vec<usize> = (0..items.len()).collect();
        let picked = pick(&parse(sel)?, &items, &all).map_err(|e| anyhow!("the selector {sel:?}: {e}"))?;
        let picked: HashSet<u32> = picked.into_iter().map(|f| f as u32).collect();
        Ok(Edges(g.edges.into_iter().filter(|e| e.faces.iter().any(|f| picked.contains(f))).collect()))
    }
}

/// A solid's faces and edges, and how they meet.
pub(crate) struct Graph {
    pub faces: Faces,
    pub edges: Vec<Edge>,
    /// Per vertex where three or more faces meet, those faces in ascending order.
    pub corners: HashMap<u32, Vec<u32>>,
    /// Per vertex, the open edges ending there: (edge, 0 where it starts, 1 where it ends).
    pub ends: HashMap<u32, Vec<(usize, usize)>>,
    /// Per directed mesh edge, the triangle walking it.
    pub walks: HashMap<(u32, u32), u32>,
}

impl Graph {
    /// The index of `e` among this solid's edges.
    pub fn find(&self, e: &Edge) -> Result<usize> {
        self.edges
            .iter()
            .position(|x| x.faces == e.faces && x.ids == e.ids)
            .ok_or_else(|| anyhow!("{e} is no edge of this solid"))
    }
}

pub(crate) fn graph(s: &Solid) -> Graph {
    let fs = faces(s);
    let mut walks = HashMap::with_capacity(3 * s.tris.len());
    for (i, t) in s.tris.iter().enumerate() {
        for k in 0..3 {
            walks.insert((t[k], t[(k + 1) % 3]), i as u32);
        }
    }
    let mut runs: BTreeMap<(u32, u32), Vec<(u32, u32)>> = BTreeMap::new();
    let mut around: HashMap<u32, Vec<u32>> = HashMap::new();
    for (i, t) in s.tris.iter().enumerate() {
        let fa = fs.of[i];
        for k in 0..3 {
            let (a, b) = (t[k], t[(k + 1) % 3]);
            let Some(&j) = walks.get(&(b, a)) else { continue };
            let fb = fs.of[j as usize];
            if fa < fb {
                runs.entry((fa, fb)).or_default().push((a, b));
                for v in [a, b] {
                    let f = around.entry(v).or_default();
                    for x in [fa, fb] {
                        if !f.contains(&x) {
                            f.push(x);
                        }
                    }
                }
            }
        }
    }
    let corners: HashMap<u32, Vec<u32>> = around
        .into_iter()
        .filter(|(_, f)| f.len() >= 3)
        .map(|(v, mut f)| {
            f.sort_unstable();
            (v, f)
        })
        .collect();
    let mut edges = vec![];
    for (&(fa, fb), segs) in &runs {
        let mut next: HashMap<u32, Vec<u32>> = HashMap::new();
        let mut into: HashMap<u32, usize> = HashMap::new();
        for &(a, b) in segs {
            next.entry(a).or_default().push(b);
            *into.entry(b).or_default() += 1;
        }
        let breaks = |v: u32| {
            corners.contains_key(&v) || next.get(&v).map_or(0, Vec::len) != 1 || into.get(&v).copied().unwrap_or(0) != 1
        };
        let mut used: HashSet<(u32, u32)> = HashSet::new();
        let mut starts: Vec<u32> = segs.iter().map(|&(a, _)| a).filter(|&a| breaks(a)).collect();
        starts.sort_unstable();
        starts.dedup();
        for &v in &starts {
            let mut outs = next[&v].clone();
            outs.sort_unstable();
            for b in outs {
                if !used.insert((v, b)) {
                    continue;
                }
                let mut ids = vec![v, b];
                let mut at = b;
                while !breaks(at) && at != v {
                    let n = next[&at][0];
                    used.insert((at, n));
                    ids.push(n);
                    at = n;
                }
                edges.push(edge(s, &fs, [fa, fb], ids, false));
            }
        }
        let mut rest: Vec<(u32, u32)> = segs.iter().copied().filter(|e| !used.contains(e)).collect();
        rest.sort_unstable();
        for (a, b) in rest {
            if !used.insert((a, b)) {
                continue;
            }
            let mut ids = vec![a];
            let mut at = b;
            while at != a {
                ids.push(at);
                let n = next[&at][0];
                used.insert((at, n));
                at = n;
            }
            edges.push(edge(s, &fs, [fa, fb], ids, true));
        }
    }
    edges.retain(|e| e.length() >= TOLERANCE);
    let mut ends: HashMap<u32, Vec<(usize, usize)>> = HashMap::new();
    for (i, e) in edges.iter().enumerate() {
        if !e.closed {
            ends.entry(e.ids[0]).or_default().push((i, 0));
            ends.entry(e.ids[e.ids.len() - 1]).or_default().push((i, 1));
        }
    }
    Graph { faces: fs, edges, corners, ends, walks }
}

fn edge(s: &Solid, fs: &Faces, faces: [u32; 2], ids: Vec<u32>, closed: bool) -> Edge {
    let pts: Vec<V3> = ids.iter().map(|&i| s.verts[i as usize]).collect();
    let surface = |f: u32| s.faces[fs.record[f as usize] as usize].surface;
    let curve = curve(surface(faces[0]), surface(faces[1]), &pts, closed);
    let mut e = Edge { curve, pts, closed, center: V3::ZERO, faces, ids };
    e.center = center(&e);
    e
}

fn curve(sa: Surface, sb: Surface, pts: &[V3], closed: bool) -> Curve {
    let n = pts.len();
    if !closed {
        let (a, d) = (pts[0], pts[n - 1] - pts[0]);
        if d.norm() > ON && pts.iter().all(|&p| (p - a).cross(d).norm() <= ON * d.norm()) {
            return Curve::Line;
        }
    }
    let on = |(c, axis, r): (V3, V3, f64)| {
        pts.iter().all(|&p| {
            let v = p - c;
            v.dot(axis).abs() <= ON && (v.reject(axis).norm() - r).abs() <= ON
        })
    };
    let circle = [round_of(sa, sb), round_of(sb, sa), fit(pts, closed)].into_iter().flatten().find(|&c| on(c));
    match circle {
        Some((c, axis, r)) => Curve::Circle { c, axis, r },
        None => Curve::Free("OTHER"),
    }
}

/// The circle a plane cuts from a surface turned about its normal: center, axis, radius.
fn round_of(p: Surface, q: Surface) -> Option<(V3, V3, f64)> {
    let Surface::Plane { p: o, n } = p else { return None };
    let along = |d: V3| d.unit().cross(n.unit()).norm() < 1e-9;
    match q {
        Surface::Cylinder { p: a, d, r } if along(d) => Some((a + d * (o - a).dot(d), canonical_axis(d), r)),
        Surface::Cone { p: a, d, r, slope } if along(d) => {
            let h = (o - a).dot(d);
            Some((a + d * h, canonical_axis(d), r + slope * h))
        }
        Surface::Sphere { c, r } => {
            let n = n.unit();
            let h = (c - o).dot(n);
            (r * r > h * h).then(|| (c - n * h, canonical_axis(n), (r * r - h * h).sqrt()))
        }
        _ => None,
    }
}

/// The circle through three of the points, spread along them.
fn fit(pts: &[V3], closed: bool) -> Option<(V3, V3, f64)> {
    let n = pts.len();
    if n < 3 {
        return None;
    }
    let (a, b, c) = if closed { (pts[0], pts[n / 3], pts[2 * n / 3]) } else { (pts[0], pts[n / 2], pts[n - 1]) };
    let (u, v) = (b - a, c - a);
    let w = u.cross(v);
    if w.norm() <= 1e-12 * u.norm() * v.norm() {
        return None;
    }
    let center = a + (v * u.norm2() - u * v.norm2()).cross(w) / (2.0 * w.norm2());
    Some((center, canonical_axis(w), (a - center).norm()))
}

fn center(e: &Edge) -> V3 {
    let n = e.pts.len();
    match e.curve {
        Curve::Line => (e.pts[0] + e.pts[n - 1]) * 0.5,
        Curve::Circle { c, .. } if e.closed => c,
        Curve::Circle { c, axis, r } => {
            let (sense, turn) = e.arc().unwrap();
            let mid = rotate((e.pts[0] - c).reject(axis).unit(), axis * sense, turn / 2.0);
            c + mid * (r * sin(turn / 2.0) / (turn / 2.0))
        }
        Curve::Free(_) => {
            let m = if e.closed { n } else { n - 1 };
            let (mut sum, mut len) = (V3::ZERO, 0.0);
            for i in 0..m {
                let (a, b) = (e.pts[i], e.pts[(i + 1) % n]);
                let l = (b - a).norm();
                sum += (a + b) * (0.5 * l);
                len += l;
            }
            if len > 0.0 { sum / len } else { e.pts[0] }
        }
    }
}

/// `v` turned `angle` radians counterclockwise about the unit axis `d`.
pub(crate) fn rotate(v: V3, d: V3, angle: f64) -> V3 {
    let (s, c) = (sin(angle), cos(angle));
    v * c + d.cross(v) * s + d * (d.dot(v) * (1.0 - c))
}

/// The angle from `a` to `b` about the axis through `c` along unit `d`, counterclockwise, in
/// (0, 2π]; a whole turn when they are one point.
pub(crate) fn turn_about(c: V3, d: V3, a: V3, b: V3) -> f64 {
    let (u, v) = ((a - c).reject(d), (b - c).reject(d));
    let t = atan2(u.cross(v).dot(d), u.dot(v));
    if t <= 1e-12 { t + TAU } else { t }
}

/// What a selector reads off an edge or a face.
struct Item {
    /// A line's direction or a plane's outward normal.
    dir: Option<V3>,
    center: V3,
    kind: &'static str,
    edge: bool,
}

fn edge_item(e: &Edge) -> Item {
    let dir = matches!(e.curve, Curve::Line).then(|| e.tangent(0));
    Item { dir, center: e.center, kind: e.kind(), edge: true }
}

fn face_items(s: &Solid, fs: &Faces) -> Vec<Item> {
    fs.tris
        .iter()
        .zip(&fs.record)
        .map(|(tris, &rec)| {
            let surface = s.faces[rec as usize].surface;
            let (mut sum, mut area, mut normal) = (V3::ZERO, 0.0, V3::ZERO);
            for &t in tris {
                let [a, b, c] = s.tris[t as usize].map(|i| s.verts[i as usize]);
                let n = (b - a).cross(c - a);
                sum += (a + b + c) * (n.norm() / 6.0);
                area += n.norm() / 2.0;
                normal += n;
            }
            let dir = match surface {
                Surface::Plane { n, .. } => Some(if n.dot(normal) < 0.0 { -n.unit() } else { n.unit() }),
                _ => None,
            };
            let center = if area > 0.0 { sum / area } else { V3::ZERO };
            Item { dir, center, kind: surface.kind(), edge: false }
        })
        .collect()
}

#[derive(Debug)]
enum Sel {
    Facing(V3),
    Parallel(V3),
    Square(V3),
    Kind(String),
    /// The n-th rank by center along `d`, CadQuery's `_NthSelector`; `parallel` first keeps
    /// only the lines or planes parallel to `d`.
    Rank { d: V3, max: bool, n: i64, parallel: bool },
    And(Box<Sel>, Box<Sel>),
    Or(Box<Sel>, Box<Sel>),
    Exc(Box<Sel>, Box<Sel>),
    Not(Box<Sel>),
}

fn angle(a: V3, b: V3) -> f64 {
    acos((a.dot(b) / (a.norm() * b.norm())).clamp(-1.0, 1.0))
}

fn pick(sel: &Sel, items: &[Item], among: &[usize]) -> Result<Vec<usize>> {
    let by_dir = |test: &dyn Fn(V3) -> bool| -> Vec<usize> {
        among.iter().copied().filter(|&i| items[i].dir.is_some_and(test)).collect()
    };
    let parallel = |d: V3| move |v: V3| d.cross(v).norm() < PICK;
    Ok(match sel {
        Sel::Facing(d) => {
            ensure!(among.iter().all(|&i| !items[i].edge), "an edge faces no way of its own; + and - pick faces");
            by_dir(&|v| angle(*d, v) < PICK)
        }
        Sel::Parallel(d) => by_dir(&parallel(*d)),
        Sel::Square(d) => by_dir(&|v| (angle(*d, v) - PI / 2.0).abs() < PICK),
        Sel::Kind(k) => among.iter().copied().filter(|&i| items[i].kind == k).collect(),
        Sel::Rank { d, max, n, parallel: first } => {
            let pool = if *first { by_dir(&parallel(*d)) } else { among.to_vec() };
            ensure!(!pool.is_empty(), "nothing to rank along ({}, {}, {})", d.x, d.y, d.z);
            let mut keyed: Vec<(f64, usize)> = pool.iter().map(|&i| (items[i].center.dot(*d), i)).collect();
            keyed.sort_by(|a, b| a.0.total_cmp(&b.0));
            let mut ranks: Vec<Vec<usize>> = vec![];
            let mut start = f64::NEG_INFINITY;
            for (k, i) in keyed {
                if ranks.is_empty() || k - start > PICK {
                    ranks.push(vec![]);
                    start = k;
                }
                ranks.last_mut().unwrap().push(i);
            }
            if !max {
                ranks.reverse();
            }
            let m = ranks.len() as i64;
            let at = if *n < 0 { m + n } else { *n };
            ensure!((0..m).contains(&at), "no rank {n} of {m}");
            let mut out = ranks.swap_remove(at as usize);
            out.sort_unstable();
            out
        }
        Sel::And(a, b) => {
            let (a, b) = (pick(a, items, among)?, pick(b, items, among)?);
            a.into_iter().filter(|i| b.contains(i)).collect()
        }
        Sel::Or(a, b) => {
            let (a, b) = (pick(a, items, among)?, pick(b, items, among)?);
            among.iter().copied().filter(|i| a.contains(i) || b.contains(i)).collect()
        }
        Sel::Exc(a, b) => {
            let (a, b) = (pick(a, items, among)?, pick(b, items, among)?);
            a.into_iter().filter(|i| !b.contains(i)).collect()
        }
        Sel::Not(a) => {
            let a = pick(a, items, among)?;
            among.iter().copied().filter(|i| !a.contains(i)).collect()
        }
    })
}

fn parse(sel: &str) -> Result<Sel> {
    let mut p = Parser { s: sel.as_bytes(), i: 0 };
    let out = p.expr()?;
    p.ws();
    ensure!(p.i == p.s.len(), "the selector {sel:?} has more after {:?}", &sel[..p.i]);
    Ok(out)
}

struct Parser<'a> {
    s: &'a [u8],
    i: usize,
}

impl Parser<'_> {
    fn ws(&mut self) {
        while self.s.get(self.i).is_some_and(u8::is_ascii_whitespace) {
            self.i += 1;
        }
    }

    /// Whether the keyword `w` comes next, taking it if so.
    fn word(&mut self, w: &str) -> bool {
        self.ws();
        let b = w.as_bytes();
        let ends = self.s.get(self.i + b.len()).is_none_or(|c| !c.is_ascii_alphanumeric());
        if self.s[self.i..].starts_with(b) && ends {
            self.i += b.len();
            true
        } else {
            false
        }
    }

    fn expr(&mut self) -> Result<Sel> {
        if self.word("not") {
            return Ok(Sel::Not(Box::new(self.expr()?)));
        }
        let mut left = self.or()?;
        while self.word("except") || self.word("exc") {
            left = Sel::Exc(Box::new(left), Box::new(self.or()?));
        }
        Ok(left)
    }

    fn or(&mut self) -> Result<Sel> {
        let mut left = self.and()?;
        while self.word("or") {
            left = Sel::Or(Box::new(left), Box::new(self.and()?));
        }
        Ok(left)
    }

    fn and(&mut self) -> Result<Sel> {
        let mut left = self.atom()?;
        while self.word("and") {
            left = Sel::And(Box::new(left), Box::new(self.atom()?));
        }
        Ok(left)
    }

    fn atom(&mut self) -> Result<Sel> {
        self.ws();
        if self.s.get(self.i) == Some(&b'(') && !self.vector_next() {
            self.i += 1;
            let inner = self.expr()?;
            self.ws();
            ensure!(self.s.get(self.i) == Some(&b')'), "a selector's parenthesis is not closed");
            self.i += 1;
            return Ok(inner);
        }
        self.simple()
    }

    /// Whether a vector `(x, y, z)` comes next rather than a parenthesized selector.
    fn vector_next(&self) -> bool {
        let rest = &self.s[self.i + 1..];
        let first = rest.iter().find(|c| !c.is_ascii_whitespace());
        first.is_some_and(|c| c.is_ascii_digit() || matches!(c, b'-' | b'+' | b'.'))
    }

    fn simple(&mut self) -> Result<Sel> {
        let rest = &self.s[self.i..];
        if rest.starts_with(b">>") || rest.starts_with(b"<<") {
            let max = rest[0] == b'>';
            self.i += 2;
            let d = self.dir()?;
            let n = self.index()?.unwrap_or(-1);
            return Ok(Sel::Rank { d, max, n, parallel: false });
        }
        let op = rest.first().copied();
        if matches!(op, Some(b'>' | b'<' | b'|' | b'#' | b'+' | b'-' | b'%')) {
            self.i += 1;
        }
        Ok(match op {
            Some(b'>' | b'<') => {
                let (d, max) = (self.dir()?, op == Some(b'>'));
                match self.index()? {
                    Some(n) => Sel::Rank { d, max, n, parallel: true },
                    None => Sel::Rank { d, max, n: -1, parallel: false },
                }
            }
            Some(b'|') => Sel::Parallel(self.dir()?),
            Some(b'#') => Sel::Square(self.dir()?),
            Some(b'+') => Sel::Facing(self.dir()?),
            Some(b'-') => Sel::Facing(-self.dir()?),
            Some(b'%') => {
                let start = self.i;
                while self.s.get(self.i).is_some_and(u8::is_ascii_alphabetic) {
                    self.i += 1;
                }
                ensure!(self.i > start, "a type selector names no type");
                Sel::Kind(String::from_utf8_lossy(&self.s[start..self.i]).to_uppercase())
            }
            _ => {
                for (name, d, max) in [
                    ("front", V3::Z, true),
                    ("back", V3::Z, false),
                    ("left", V3::X, false),
                    ("right", V3::X, true),
                    ("top", V3::Y, true),
                    ("bottom", V3::Y, false),
                ] {
                    if self.word(name) {
                        return Ok(Sel::Rank { d, max, n: -1, parallel: false });
                    }
                }
                Sel::Facing(self.dir()?)
            }
        })
    }

    fn dir(&mut self) -> Result<V3> {
        self.ws();
        if self.s.get(self.i) == Some(&b'(') {
            let close = self.s[self.i..].iter().position(|&c| c == b')').ok_or_else(|| anyhow!("a vector is not closed"))?;
            let text = String::from_utf8_lossy(&self.s[self.i + 1..self.i + close]).to_string();
            self.i += close + 1;
            let xyz: Vec<f64> = text.split(',').map(|t| t.trim().parse::<f64>()).collect::<Result<_, _>>()?;
            ensure!(xyz.len() == 3, "the vector ({text}) has {} components", xyz.len());
            return Ok(v3(xyz[0], xyz[1], xyz[2]));
        }
        for (name, d) in [
            ("XY", v3(1.0, 1.0, 0.0)),
            ("YZ", v3(0.0, 1.0, 1.0)),
            ("XZ", v3(1.0, 0.0, 1.0)),
            ("X", V3::X),
            ("Y", V3::Y),
            ("Z", V3::Z),
        ] {
            if self.word(name) {
                return Ok(d);
            }
        }
        let at = String::from_utf8_lossy(&self.s[self.i..]).to_string();
        bail!("no direction at {at:?}")
    }

    fn index(&mut self) -> Result<Option<i64>> {
        if self.s.get(self.i) != Some(&b'[') {
            return Ok(None);
        }
        let close = self.s[self.i..].iter().position(|&c| c == b']').ok_or_else(|| anyhow!("an index is not closed"))?;
        let text = String::from_utf8_lossy(&self.s[self.i + 1..self.i + close]).to_string();
        self.i += close + 1;
        Ok(Some(text.trim().parse()?))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::math::v3;

    fn count(s: &Solid, sel: &str) -> usize {
        s.edges(sel).unwrap().len()
    }

    #[test]
    fn a_box_has_twelve_edges() {
        let b = Solid::cuboid(v3(0.0, 0.0, 0.0), v3(20.0, 10.0, 5.0));
        let all = b.edges("").unwrap();
        assert_eq!(all.len(), 12);
        assert!(all.iter().all(|e| e.kind() == "LINE"));
        assert_eq!(count(&b, "|Z"), 4);
        assert_eq!(count(&b, ">Z"), 4);
        assert_eq!(count(&b, "|Z and >Y"), 2);
        assert_eq!(count(&b, "|Z and >Y and >X"), 1);
        assert_eq!(count(&b, "#Z"), 8);
        assert_eq!(count(&b, "not |Z"), 8);
        assert_eq!(count(&b, "not |Z and >Y"), 10);
        assert_eq!(count(&b, "|X or |Y"), 8);
        assert_eq!(count(&b, "|X exc >Z"), 2);
        assert_eq!(count(&b, "not(<X or >X or <Y or >Y)"), 0);
        assert!(b.edges(">X[-2]").is_err());
        assert_eq!(b.edges("|Y").unwrap().select(">Z").unwrap().select("<X").unwrap()[0].center, v3(0.0, 5.0, 5.0));
        let near = b.edges("|Z").unwrap().nearest(v3(21.0, 11.0, 0.0)).unwrap();
        assert_eq!(near[0].center, v3(20.0, 10.0, 2.5));
        assert_eq!(b.face_edges(">Z").unwrap().len(), 4);
        assert_eq!(b.face_edges("%PLANE").unwrap().len(), 12);
        assert!(b.edges("+Z").is_err());
        assert!(b.edges("|Z and not >Y").is_err());
    }

    #[test]
    fn a_cylinder_has_two_circles() {
        let c = Solid::cylinder(v3(1.0, 2.0, 0.0), V3::Z, 5.0, 10.0).unwrap();
        let all = c.edges("").unwrap();
        assert_eq!(all.len(), 2);
        for e in all.iter() {
            assert!(e.closed);
            let Curve::Circle { c: o, axis, r } = e.curve else { panic!("{e} is no circle") };
            assert_eq!((o.x, o.y, axis, r), (1.0, 2.0, V3::Z, 5.0));
        }
        assert_eq!(c.edges(">Z").unwrap()[0].center, v3(1.0, 2.0, 10.0));
        assert_eq!(count(&c, "%CIRCLE"), 2);
        assert_eq!(count(&c, "%LINE"), 0);
    }
}
