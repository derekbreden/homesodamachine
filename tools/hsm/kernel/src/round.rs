//! Rounds and chamfers along a solid's edges, as CadQuery's `fillet` and `chamfer` make them.
//!
//! Each edge gets one tool. Its section square to the edge is the corner between the two faces
//! less the circle of the round's radius touching both; a chamfer's is the triangle cut off the
//! distance along each face. The tool carries that section along the edge: straight along a line,
//! turned about the axis of a circle. A convex edge's tool is cut from the solid and a concave
//! edge's is added to it. A round along a line is a cylinder face and along a circle a torus; a
//! chamfer is a plane or a cone.
//!
//! The tool's sides stand `STANDOFF` off the two faces, out into the air for a cut and into the
//! material for a fill, so neither side lies on a face of the solid. Nothing else of the solid is
//! touched unless it lies nearer those faces than that.
//!
//! A round runs on along every edge that continues tangent from a picked one, as OCCT's does, so
//! a box's top edges after its vertical edges are rounded make one round. Where a round ends, its
//! tool either ends square on the face there, or runs on past that face where the face looks out
//! into air (into material, for a fill), until its whole section has passed the face. Where two
//! rounds meet at a corner, both tools run on past it and trim it between them, which is OCCT's
//! corner of two rounds.
//!
//! The kernel rounds an edge between two planes, or between planes, cylinders and cones turned
//! about one axis. It refuses three rounds meeting at a corner, which OCCT closes with a patch of
//! its own. It also refuses a round that ends on a slanted face where it may not run on, and a
//! round wider than a face it lies on.
//! `rolling_fillet` separately solves tangent balls against analytic face patches and carries
//! their contacts onto adjoining faces along noncircular intersections.
use crate::boolean::{Op, boolean};
use crate::build::{prism, revolve};
use crate::edge::{Edges, Graph, graph, rotate, turn_about};
use crate::face::{Src, Surface};
use crate::math::{PI, TAU, V3, acos, degrees, sin, tan};
use crate::plane::Plane;
use crate::profile::{Curve, Pen, Profile, Region};
use crate::rule::LINEAR;
use crate::solid::{Solid, point_triangle};
use anyhow::{Result, anyhow, bail, ensure};
use std::collections::HashMap;
use std::panic::Location;

mod rolled;

/// mm a tool's sides stand off the faces it runs along.
pub const STANDOFF: f64 = 1e-3;

/// rad. An edge that turns less than this onto the next continues it.
const TANGENT: f64 = 1e-5;

#[derive(Clone, Copy, Debug)]
enum Blend {
    Round(f64),
    Chamfer(f64),
}

impl Blend {
    fn op(self) -> &'static str {
        match self {
            Blend::Round(_) => "fillet",
            Blend::Chamfer(_) => "chamfer",
        }
    }
}

impl std::fmt::Display for Blend {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match *self {
            Blend::Round(r) => write!(f, "a round of radius {r}"),
            Blend::Chamfer(d) => write!(f, "a chamfer of {d}"),
        }
    }
}

impl Solid {
    /// A rolling-ball round along analytic surfaces whose intersection is not covered by
    /// the prism/revolution tools. Contacts can continue onto adjoining analytic faces.
    /// Existing planar and coaxial rounds retain `fillet`'s construction.
    #[track_caller]
    pub fn rolling_fillet(&self, edges: &Edges, r: f64) -> Result<Solid> {
        ensure!(r > 0.0, "a round of radius {r}");
        rolled::blend(self, edges, r, Location::caller())
    }

    /// `edges` rounded to radius `r`, and every edge running on tangent from them; CadQuery's
    /// `fillet`.
    #[track_caller]
    pub fn fillet(&self, edges: &Edges, r: f64) -> Result<Solid> {
        ensure!(r > 0.0, "a round of radius {r}");
        blend(self, edges, Blend::Round(r), Location::caller())
    }

    /// `edges` chamfered `d` along each face, and every edge running on tangent from them;
    /// CadQuery's `chamfer`.
    #[track_caller]
    pub fn chamfer(&self, edges: &Edges, d: f64) -> Result<Solid> {
        ensure!(d > 0.0, "a chamfer of {d}");
        blend(self, edges, Blend::Chamfer(d), Location::caller())
    }
}

/// An edge of a chain, and whether the chain walks it the way its points run.
#[derive(Clone, Copy, Debug, PartialEq)]
struct Link {
    edge: usize,
    forward: bool,
}

impl Link {
    /// Its two faces, the first the one whose boundary runs the way the chain does.
    fn faces(self, g: &Graph) -> [u32; 2] {
        let f = g.edges[self.edge].faces;
        if self.forward { f } else { [f[1], f[0]] }
    }

    /// Its vertex where the chain enters it (`end` 0) or leaves it (`end` 1).
    fn vertex(self, g: &Graph, end: usize) -> u32 {
        let ids = &g.edges[self.edge].ids;
        if (end == 0) == self.forward { ids[0] } else { ids[ids.len() - 1] }
    }

    fn point(self, g: &Graph, s: &Solid, end: usize) -> V3 {
        s.verts[self.vertex(g, end) as usize]
    }

    /// The way the chain runs where it enters the link (`end` 0) or leaves it (`end` 1).
    fn tangent(self, g: &Graph, end: usize) -> V3 {
        let e = &g.edges[self.edge];
        if self.forward { e.tangent(end) } else { -e.tangent(1 - end) }
    }

    /// The link's middle point and the way the chain runs there.
    fn middle(self, g: &Graph, s: &Solid) -> (V3, V3) {
        let e = &g.edges[self.edge];
        let p = s.verts[e.ids[e.ids.len() / 2] as usize];
        let t = match e.curve {
            Curve::Circle { c, axis, .. } => (axis * e.arc().unwrap().0).cross(p - c).unit(),
            _ => e.tangent(0),
        };
        (p, if self.forward { t } else { -t })
    }
}

struct Chain {
    links: Vec<Link>,
    closed: bool,
}

/// The corner square to an edge at `o`, the chain running along `e` there: the unit directions
/// into its two faces, their outward normals, and whether the material lies between the faces.
#[derive(Clone, Copy, Debug)]
struct Section {
    o: V3,
    e: V3,
    ua: V3,
    ub: V3,
    na: V3,
    nb: V3,
    convex: bool,
}

fn blend(s: &Solid, edges: &Edges, how: Blend, src: Src) -> Result<Solid> {
    ensure!(!edges.is_empty(), "{how} along no edge");
    let g = graph(s);
    let picked = edges.iter().map(|e| g.find(e)).collect::<Result<Vec<_>>>()?;
    let chains = chains(&g, &picked)?;
    let (mut cuts, mut fills) = (vec![], vec![]);
    let mut corners: HashMap<u32, Vec<bool>> = HashMap::new();
    for chain in &chains {
        let n = chain.links.len();
        let mut sections = vec![];
        for &link in &chain.links {
            lies_on_lines(s, &g, link.edge)?;
            let (p0, p1) = (link.point(&g, s, 0), link.point(&g, s, 1));
            let (pm, tm) = link.middle(&g, s);
            let at0 = section(s, &g, link, p0, link.tangent(&g, 0))?;
            let at1 = section(s, &g, link, p1, link.tangent(&g, 1))?;
            for at in [&at0, &section(s, &g, link, pm, tm)?, &at1] {
                fits(s, &g, link, at, how)?;
            }
            sections.push((at0, at1));
        }
        let convex = sections[0].0.convex;
        for (i, (a, b)) in sections.iter().enumerate() {
            let edge = &g.edges[chain.links[i].edge];
            ensure!(a.convex == convex && b.convex == convex, "{how} turns from convex to concave along {edge}");
            // A whole circle's last point is the one before its first, so it is not compared.
            let next = if i + 1 < n { Some(sections[i + 1].0) } else if chain.closed && n > 1 { Some(sections[0].0) } else { None };
            if let Some(c) = next {
                let same = (b.ua - c.ua).norm() < 1e-6 && (b.ub - c.ub).norm() < 1e-6;
                ensure!(same, "{how} meets a crease where {edge} runs on into the next edge at {}", show(b.o));
            }
        }
        let mut ext = vec![[0.0; 2]; n];
        if !chain.closed {
            for (end, i) in [(0, 0), (1, n - 1)] {
                let link = chain.links[i];
                let at = if end == 0 { sections[i].0 } else { sections[i].1 };
                let run = run_on(s, &g, link, end, &at, how)?;
                corners.entry(link.vertex(&g, end)).or_default().push(run > 0.0);
                ext[i][end] = run;
            }
        }
        for (i, &link) in chain.links.iter().enumerate() {
            let t = tool(s, &g, link, chain.closed && n == 1, ext[i], how, src)?;
            if convex { cuts.push(t) } else { fills.push(t) }
        }
    }
    for (v, runs) in &corners {
        let p = show(s.verts[*v as usize]);
        ensure!(runs.len() <= 2, "three rounds meet at {p}; the kernel has no corner patch for them");
        ensure!(runs.len() < 2 || runs.iter().all(|&r| r), "two rounds meet at {p} in a corner that turns in");
    }
    let mut out = s.clone();
    if !cuts.is_empty() {
        let ops: Vec<&Solid> = std::iter::once(s).chain(&cuts).collect();
        out = boolean(&ops, Op::Cut, src)?;
    }
    if !fills.is_empty() {
        let ops: Vec<&Solid> = std::iter::once(&out).chain(&fills).collect();
        out = boolean(&ops, Op::Union, src)?;
    }
    for f in &mut out.faces {
        if f.op == how.op() && f.src == src && f.via.is_some_and(|v| v.src == src) {
            f.via = None;
        }
    }
    Ok(out)
}

fn show(p: V3) -> String {
    format!("({:.3}, {:.3}, {:.3})", p.x, p.y, p.z)
}

/// Whether the edge's two faces meet it in straight lines across its section: two planes along a
/// line, or planes, cylinders and cones turned about a circle's axis.
fn lies_on_lines(s: &Solid, g: &Graph, e: usize) -> Result<()> {
    let edge = &g.edges[e];
    for f in edge.faces {
        let surface = s.faces[g.faces.record[f as usize] as usize].surface;
        let square = match (edge.curve, surface) {
            (Curve::Line, Surface::Plane { .. }) => true,
            (Curve::Circle { axis, .. }, Surface::Plane { n, .. }) => n.unit().cross(axis).norm() < 1e-9,
            (Curve::Circle { c, axis, .. }, Surface::Cylinder { p, d, .. } | Surface::Cone { p, d, .. }) => {
                d.cross(axis).norm() < 1e-9 && (p - c).cross(axis).norm() < 1e-7
            }
            _ => false,
        };
        ensure!(
            square,
            "{edge} runs along a {} face; the kernel rounds edges between planes, and between planes, cylinders and cones about one axis",
            surface.kind()
        );
    }
    Ok(())
}

/// The picked edges in chains, each run on along every edge continuing it tangent.
fn chains(g: &Graph, picked: &[usize]) -> Result<Vec<Chain>> {
    let mut taken = vec![false; g.edges.len()];
    let mut out = vec![];
    for &e in picked {
        if taken[e] {
            continue;
        }
        taken[e] = true;
        let mut links = vec![Link { edge: e, forward: true }];
        let mut closed = g.edges[e].closed;
        while !closed {
            let Some(l) = next(g, *links.last().unwrap(), 1)? else { break };
            if l.edge == links[0].edge {
                closed = true;
            } else {
                ensure!(!taken[l.edge], "{} runs into a round twice", g.edges[l.edge]);
                taken[l.edge] = true;
                links.push(l);
            }
        }
        while !closed {
            let Some(l) = next(g, links[0], 0)? else { break };
            ensure!(!taken[l.edge], "{} runs into a round twice", g.edges[l.edge]);
            taken[l.edge] = true;
            links.insert(0, l);
        }
        out.push(Chain { links, closed });
    }
    Ok(out)
}

/// The edge continuing the chain tangent past `link`'s end (`end` 1) or before its start (0).
fn next(g: &Graph, link: Link, end: usize) -> Result<Option<Link>> {
    let v = link.vertex(g, end);
    let t = link.tangent(g, end);
    let mut found = vec![];
    for &(e, k) in g.ends.get(&v).map(Vec::as_slice).unwrap_or(&[]) {
        if e == link.edge {
            continue;
        }
        let other = &g.edges[e];
        // Along the chain's way through the vertex, leaving it after `link` or entering before.
        let along = if (k == 0) == (end == 1) { other.tangent(k) } else { -other.tangent(k) };
        if t.dot(along) > (1.0 - TANGENT * TANGENT / 2.0) {
            found.push(Link { edge: e, forward: (k == 0) == (end == 1) });
        }
    }
    ensure!(found.len() <= 1, "{} runs on tangent into {} edges at once", g.edges[link.edge], found.len());
    Ok(found.pop())
}

/// The unit normal of face `f` at `o`, out of the solid, on the side its triangle at the link's
/// edge faces.
fn outward(s: &Solid, g: &Graph, link: Link, f: u32, o: V3) -> Result<V3> {
    let edge = &g.edges[link.edge];
    let surface = s.faces[g.faces.record[f as usize] as usize].surface;
    let (a, b) = (edge.ids[0], edge.ids[1]);
    let walk = if f == edge.faces[0] { (a, b) } else { (b, a) };
    let t = g.walks[&walk] as usize;
    let [p, q, r] = s.tris[t].map(|i| s.verts[i as usize]);
    let n = surface.normal_at(o).ok_or_else(|| anyhow!("{edge} runs along a face with no normal"))?;
    let at = surface.normal_at((p + q + r) / 3.0).unwrap();
    Ok(if (q - p).cross(r - p).dot(at) < 0.0 { -n } else { n })
}

fn section(s: &Solid, g: &Graph, link: Link, o: V3, e: V3) -> Result<Section> {
    let [fa, fb] = link.faces(g);
    let (na, nb) = (outward(s, g, link, fa, o)?, outward(s, g, link, fb, o)?);
    let (ua, ub) = (na.cross(e).unit(), e.cross(nb).unit());
    Ok(Section { o, e, ua, ub, na, nb, convex: na.dot(ub) < 0.0 })
}

/// The points where the blend leaves each face, and a round's center, across `sec`.
fn touches(sec: &Section, how: Blend) -> Result<(V3, V3, Option<V3>)> {
    let phi = acos(sec.ua.dot(sec.ub).clamp(-1.0, 1.0));
    let meet = if phi <= 1e-6 { "fold onto each other" } else { "meet tangent" };
    ensure!(phi > 1e-6 && phi < PI - 1e-6, "the faces {meet} at {}; there is no corner for {how}", show(sec.o));
    Ok(match how {
        Blend::Round(r) => {
            let t = r / tan(phi / 2.0);
            let c = sec.o + (sec.ua + sec.ub).unit() * (r / sin(phi / 2.0));
            (sec.o + sec.ua * t, sec.o + sec.ub * t, Some(c))
        }
        Blend::Chamfer(d) => (sec.o + sec.ua * d, sec.o + sec.ub * d, None),
    })
}

/// The tool's section across `sec`, in the plane square to the edge at `sec.o`, and the five
/// points its outline runs through.
fn tool_section(sec: &Section, how: Blend) -> Result<(Region, [V3; 5])> {
    let (ta, tb, center) = touches(sec, how)?;
    let side = if sec.convex { STANDOFF } else { -STANDOFF };
    let (pa, pb) = (ta + sec.na * side, tb + sec.nb * side);
    let x = sec.o + (sec.na + sec.nb) * (side / (1.0 + sec.na.dot(sec.nb)));
    let plane = Plane::new(sec.o, sec.ua, sec.e)?;
    let q = |p: V3| plane.local(p).0;
    let pen = match center {
        Some(c) => Pen::new(q(ta)).arc_center(q(c), q(tb), (ta - c).cross(tb - c).dot(sec.e) > 0.0),
        None => Pen::new(q(ta)).line_to(q(tb)),
    };
    let lp = pen.line_to(q(pb)).line_to(q(x)).line_to(q(pa)).close()?;
    Ok((Profile::new(lp).place(&plane), [ta, tb, pa, pb, x]))
}

/// Whether the blend across `sec` leaves each of the link's faces inside that face.
fn fits(s: &Solid, g: &Graph, link: Link, sec: &Section, how: Blend) -> Result<()> {
    let (ta, tb, _) = touches(sec, how)?;
    for (f, p) in link.faces(g).into_iter().zip([ta, tb]) {
        let curved = !matches!(s.faces[g.faces.record[f as usize] as usize].surface, Surface::Plane { .. });
        let tol = if curved { LINEAR + 1e-6 } else { 1e-6 };
        let near = g.faces.tris[f as usize]
            .iter()
            .map(|&t| {
                let [a, b, c] = s.tris[t as usize].map(|i| s.verts[i as usize]);
                point_triangle(p, a, b, c)
            })
            .fold(f64::INFINITY, f64::min);
        ensure!(near <= tol, "{how} along {} leaves a face {near:.4} mm past its edge at {}", g.edges[link.edge], show(p));
    }
    Ok(())
}

/// How far the tool at one end of an open chain runs on past it: none where the face there is
/// square to the edge and the tool may not run into what lies beyond it, else until every corner
/// of its section has passed that face by STANDOFF. Along a circle, as an angle.
fn run_on(s: &Solid, g: &Graph, link: Link, end: usize, sec: &Section, how: Blend) -> Result<f64> {
    let v = link.vertex(g, end);
    let edge = &g.edges[link.edge];
    let p = show(s.verts[v as usize]);
    let faces = g.corners.get(&v).ok_or_else(|| anyhow!("{how} along {edge} ends at {p}, where no face closes it"))?;
    let own = link.faces(g);
    let others: Vec<u32> = faces.iter().copied().filter(|f| !own.contains(f)).collect();
    ensure!(others.len() == 1, "{how} along {edge} ends at {p}, a corner of {} faces", faces.len());
    let Some(nc) = plane_out(s, g, others[0]) else {
        bail!("{how} along {edge} ends at {p} on a face that is no plane");
    };
    let out = if end == 1 { sec.e } else { -sec.e };
    let sign = if sec.convex { 1.0 } else { -1.0 };
    let square = nc.cross(out).norm() < 1e-9;
    let k = sign * nc.dot(out);
    if k <= 1e-9 {
        ensure!(square, "{how} along {edge} ends at {p} on a face at a slant");
        return Ok(0.0);
    }
    if let Curve::Circle { c, axis, .. } = edge.curve {
        ensure!(square, "{how} along {edge} ends at {p} on a face at a slant");
        let (_, corners) = tool_section(sec, how)?;
        let near = corners.iter().map(|&q| (q - c).reject(axis).norm()).fold(f64::INFINITY, f64::min);
        ensure!(near > STANDOFF, "{how} along {edge} reaches the circle's axis");
        return Ok(STANDOFF / near);
    }
    let (_, corners) = tool_section(sec, how)?;
    let o = sec.o;
    Ok(corners.iter().map(|&q| (STANDOFF - sign * (q - o).dot(nc)) / k).fold(STANDOFF, f64::max))
}

/// The unit normal of plane face `f`, out of the solid.
fn plane_out(s: &Solid, g: &Graph, f: u32) -> Option<V3> {
    let Surface::Plane { n, .. } = s.faces[g.faces.record[f as usize] as usize].surface else { return None };
    let mut area = V3::ZERO;
    for &t in &g.faces.tris[f as usize] {
        let [a, b, c] = s.tris[t as usize].map(|i| s.verts[i as usize]);
        area += (b - a).cross(c - a);
    }
    Some(if area.dot(n) < 0.0 { -n.unit() } else { n.unit() })
}

/// The tool along one link: a prism along a line, a revolution about a circle's axis, run on
/// `ext` before its start and past its end (mm along a line, radians about a circle).
fn tool(s: &Solid, g: &Graph, link: Link, whole: bool, ext: [f64; 2], how: Blend, src: Src) -> Result<Solid> {
    let edge = &g.edges[link.edge];
    let (p0, p1) = (link.point(g, s, 0), link.point(g, s, 1));
    match edge.curve {
        Curve::Line => {
            let e = (p1 - p0).unit();
            let sec = section(s, g, link, p0 - e * ext[0], e)?;
            let (region, _) = tool_section(&sec, how)?;
            let len = (p1 - p0).norm() + ext[0] + ext[1];
            Ok(prism(&region, e, e * len, src, how.op())?.solid())
        }
        Curve::Circle { c, axis, .. } => {
            let about = if axis.cross(p0 - c).dot(link.tangent(g, 0)) > 0.0 { axis } else { -axis };
            let o = c + rotate(p0 - c, about, -ext[0]);
            let sec = section(s, g, link, o, about.cross(o - c).unit())?;
            let (region, _) = tool_section(&sec, how)?;
            let turn = if whole { TAU } else { turn_about(c, about, p0, p1) + ext[0] + ext[1] };
            Ok(revolve(&region, c, about, degrees(turn.min(TAU)), src, how.op())?.solid())
        }
        Curve::Free(_) => bail!("{edge} is neither a line nor a circle"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::math::v3;
    use std::collections::HashSet;

    #[test]
    fn a_box_edge_rounds_to_the_quarter_circle() {
        let b = Solid::cuboid(v3(0.0, 0.0, 0.0), v3(10.0, 10.0, 10.0));
        let r = 1.0;
        let out = b.fillet(&b.edges("|Z and >X and >Y").unwrap(), r).unwrap();
        out.check().unwrap();
        // The round's chords cut a little more than the circle: under 0.004 mm³ here.
        let want = 1000.0 - (r * r - PI * r * r / 4.0) * 10.0;
        assert!(out.volume() < want && want - out.volume() < 0.005, "volume {} against {want}", out.volume());
        let used: HashSet<u32> = out.face_of().iter().copied().collect();
        let rounds: Vec<_> = used.iter().map(|&f| out.faces()[f as usize]).filter(|f| f.op == "fillet").collect();
        assert!(!rounds.is_empty());
        assert!(rounds.iter().all(|f| f.surface.kind() == "CYLINDER" && f.via.is_none()), "{rounds:?}");
    }

    #[test]
    fn a_box_edge_chamfers_to_the_triangle() {
        let b = Solid::cuboid(v3(0.0, 0.0, 0.0), v3(10.0, 10.0, 10.0));
        let out = b.chamfer(&b.edges("|Z and >X and >Y").unwrap(), 1.0).unwrap();
        out.check().unwrap();
        assert!((out.volume() - 995.0).abs() < 1e-6, "volume {}", out.volume());
    }

    #[test]
    fn three_rounds_at_a_corner_are_refused() {
        let b = Solid::cuboid(v3(0.0, 0.0, 0.0), v3(10.0, 10.0, 10.0));
        let err = b.fillet(&b.edges("").unwrap(), 1.0).unwrap_err().to_string();
        assert!(err.contains("three rounds meet"), "{err}");
    }

    #[test]
    fn a_round_wider_than_its_face_is_refused() {
        let b = Solid::cuboid(v3(0.0, 0.0, 0.0), v3(10.0, 2.0, 10.0));
        let err = b.fillet(&b.edges("|Z and >X and >Y").unwrap(), 3.0).unwrap_err().to_string();
        assert!(err.contains("past its edge"), "{err}");
    }
}
