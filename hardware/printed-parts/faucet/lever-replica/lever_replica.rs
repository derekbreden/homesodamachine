//! The scan-derived faucet lever: the measured silhouette, its open channel and its ruled reliefs,
//! the measured stations joined by their shape-preserving cubics. It prints on its side: the
//! side-down STL is the print, and the part's own STL is those same triangles turned back into the
//! part's frame, so the page and the slicer draw one surface.
//!
//!     lever-replica [<output directory>]
use anyhow::{Context, Result, ensure};
use hsm_faucet_numbers::catalog;
use hsm_kernel::part::write_printed;
use hsm_kernel::*;
use hsm_lever_replica_numbers::{self as lever, P2};
use hsm_print_payload::printed;
use serde_json::Value;

const NAME: &str = "lever-replica";
const SIDE_DOWN: &str = "lever-replica-side-down.stl";

fn p(q: P2) -> V2 {
    v2(q[0], q[1])
}

/// A closed outline drawn edge by edge.
struct Wire {
    first: V2,
    at: V2,
    edges: Vec<Seg>,
}

impl Wire {
    fn new(at: V2) -> Self {
        Self { first: at, at, edges: vec![] }
    }

    fn line(&mut self, b: V2) {
        self.edges.push(Seg::Line { a: self.at, b });
        self.at = b;
    }

    fn arc(&mut self, mid: V2, b: V2) -> Result<()> {
        let arc = Pen::new(self.at).arc_through(mid, b)?.close()?.segs[0];
        self.edges.push(arc);
        self.at = b;
        Ok(())
    }

    fn radius(&mut self, b: V2, r: f64) -> Result<()> {
        let arc = Pen::new(self.at).radius_arc(b, r)?.close()?.segs[0];
        self.edges.push(arc);
        self.at = b;
        Ok(())
    }

    /// Through the stations `[x, y, dy/dx]`, each span the cubic with those end slopes.
    fn pchip(&mut self, stations: &[[f64; 3]]) -> Result<()> {
        for w in stations.windows(2) {
            let (a, ma, b, mb) = (v2(w[0][0], w[0][1]), w[0][2], v2(w[1][0], w[1][1]), w[1][2]);
            ensure!((self.at - a).norm() < 1e-9, "a shape-preserving span starts where the outline is");
            let span = (b.x - a.x) / 3.0;
            self.edges.push(Seg::Cubic { a, c1: a + v2(span, ma * span), c2: b - v2(span, mb * span), b });
            self.at = b;
        }
        Ok(())
    }

    /// On through `next` on the interpolating spline, each span its cubic.
    fn spline(&mut self, next: &[V2]) -> Result<()> {
        let pts: Vec<V3> = std::iter::once(self.at).chain(next.iter().copied()).map(|v| v3(v.x, v.y, 0.0)).collect();
        let s = Spline::through(&pts)?;
        let mut t = 0.0;
        for w in pts.windows(2) {
            let h = (w[1] - w[0]).norm();
            let (a, b) = (v2(w[0].x, w[0].y), v2(w[1].x, w[1].y));
            let (ma, mb) = (s.derivative(t), s.derivative(t + h));
            self.edges.push(Seg::Cubic { a, c1: a + v2(ma.x, ma.y) * (h / 3.0), c2: b - v2(mb.x, mb.y) * (h / 3.0), b });
            self.at = b;
            t += h;
        }
        Ok(())
    }

    fn profile(mut self) -> Result<Profile> {
        if (self.at - self.first).norm() > 1e-12 {
            self.line(self.first);
        }
        Ok(Profile::new(Loop::new(self.edges)?))
    }
}

/// Steps along each relief's splines: the stations' chord error stays far under a micron.
const RELIEF_STEPS: usize = 128;

/// `n` points along the spline through `p`, at one normalized parameter for every section, so the
/// ruled loft joins the sections where a native ruled loft would.
fn sampled_spline(p: &[V2], n: usize) -> Result<Vec<V2>> {
    let pts: Vec<V3> = p.iter().map(|q| v3(q.x, q.y, 0.0)).collect();
    let s = Spline::through(&pts)?;
    let (a, b) = s.range();
    Ok((1..=n)
        .map(|j| {
            let q = s.point(a + (b - a) * j as f64 / n as f64);
            v2(q.x, q.y)
        })
        .collect())
}

/// A relief's section at height `z`: its right side's stations mirrored to the left, closed past
/// the lateral faces and the attachment.
fn relief_section(z: f64, right: &[V2], reach: f64, back: f64) -> Result<LoftSection> {
    let first = right[0];
    let last = *right.last().context("a relief of no stations")?;
    let mut p = vec![v2(-first.x, first.y), first, right[1]];
    p.extend(sampled_spline(&right[1..], RELIEF_STEPS)?);
    p.extend([v2(reach, back), v2(-reach, back), v2(-last.x, last.y)]);
    let left: Vec<V2> = right[1..].iter().rev().map(|q| v2(-q.x, q.y)).collect();
    p.extend(sampled_spline(&left, RELIEF_STEPS)?);
    Ok(LoftSection::new(
        (0..p.len()).map(|i| LoftEdge::Line { a: v3(p[i].x, p[i].y, z), b: v3(p[(i + 1) % p.len()].x, p[(i + 1) % p.len()].y, z) }).collect(),
    ))
}

fn lever_body() -> Result<Solid> {
    let width = lever::PRINTED_OUTSIDE_WIDTH;
    let reach = width / 2.0;
    let (below, above) = (lever::CUT_BELOW, lever::CUT_ABOVE);
    let (front, back) = (lever::CUT_FRONT, lever::CUT_REAR);

    // The silhouette, side on, across the whole width.
    let start = p(lever::OUTER_START);
    let mut w = Wire::new(start);
    w.arc(p(lever::TIP_ARC[0]), p(lever::TIP_ARC[1]))?;
    w.pchip(&lever::pchip(&lever::SHOW_PROFILE))?;
    w.arc(p(lever::REAR_ARC[0]), p(lever::REAR_ARC[1]))?;
    w.spline(&lever::REAR_BOTTOM_PROFILE.map(p))?;
    let corner = lever::OUTER_CORNER.map(p);
    w.line(corner[0]);
    w.arc(corner[1], corner[2])?;
    w.line(p(lever::RAIL_START));
    w.pchip(&lever::pchip(&lever::rail_profile()))?;
    w.arc(p(lever::TIP_RETURN_MID), start)?;
    let outer = Plane::YZ.at(v3(-reach, 0.0, 0.0)).extrude(&w.profile()?, width)?;

    // The channel's outline from above, its stop at the attachment.
    let (y, r, half) = (lever::POCKET_START_Y, lever::POCKET_FRONT_RADIUS, lever::CHANNEL_PRINTED_WIDTH / 2.0);
    let stop: Vec<V2> = lever::stop_profile().into_iter().map(p).collect();
    let join = lever::POCKET_STOP_JOIN_Y;
    let last = *stop.last().context("a stop of no stations")?;
    let mut w = Wire::new(v2(-half + r, y));
    w.line(v2(half - r, y));
    w.radius(v2(half, y + r), -r)?;
    w.line(stop[0]);
    w.spline(&stop[1..])?;
    w.line(v2(0.0, join));
    w.line(v2(-last.x, last.y));
    let mirrored: Vec<V2> = stop[..stop.len() - 1].iter().rev().map(|q| v2(-q.x, q.y)).collect();
    w.spline(&mirrored)?;
    w.line(v2(-half, y + r));
    w.radius(v2(-half + r, y), -r)?;
    let outline = Plane::XY.offset(below).extrude(&w.profile()?, above - below)?;

    // The channel's depth, side on: its floor, its ceiling and the ledge's lip.
    let (floor, ledge) = (lever::FLOOR_Z, lever::LEDGE_TOP);
    let mut w = Wire::new(v2(front, floor));
    w.line(p(lever::POCKET_FLOOR_END));
    w.spline(&lever::POCKET_CEILING.map(p))?;
    w.line(v2(join, ledge));
    w.line(p(lever::LEDGE_LIP_END));
    w.arc(p(lever::LEDGE_LIP_MID), p(lever::LEDGE_LIP_START))?;
    w.line(p(lever::POCKET_LOWER_CORNER));
    w.line(v2(front, below));
    let height = Plane::YZ.at(v3(-(reach + 1.0), 0.0, 0.0)).extrude(&w.profile()?, 2.0 * (reach + 1.0))?;

    let mut body = outer.cut(&outline.intersect(&height)?)?;
    for reliefs in [lever::LOWER_RELIEF, lever::UPPER_RELIEF] {
        let sections: Vec<LoftSection> =
            reliefs.iter().map(|(z, right)| relief_section(*z, &right.map(p), reach + 3.0, back)).collect::<Result<_>>()?;
        body = body.cut(&Solid::thru_sections(&sections, true)?)?;
    }
    Ok(body)
}

/// The side-down print's triangles turned back into the part's frame: each corner read at single
/// precision, turned at double, written at single, its facet's normal taken from the turned
/// corners.
fn authored_from_print(print: &[u8]) -> Result<Vec<u8>> {
    ensure!(print.len() >= 84, "the side-down print has no STL header");
    let count = u32::from_le_bytes(print[80..84].try_into()?) as usize;
    ensure!(print.len() == 84 + count * 50, "the side-down print's facets run short");
    let mut out = vec![0; 84 + count * 50];
    out[80..84].copy_from_slice(&(count as u32).to_le_bytes());
    let read = |row: &[u8], i: usize| f32::from_le_bytes(row[i..i + 4].try_into().expect("four bytes")) as f64;
    // Negative zero comes back positive.
    let single = |v: f64| if v == 0.0 { 0.0_f32 } else { v as f32 };
    let half = lever::PRINTED_OUTSIDE_WIDTH / 2.0;
    for (facet, row) in print[84..].chunks_exact(50).zip(out[84..].chunks_exact_mut(50)) {
        let mut corners = [[0.0; 3]; 3];
        for (i, corner) in corners.iter_mut().enumerate() {
            let base = 12 + i * 12;
            *corner = [half - read(facet, base + 8), read(facet, base + 4), read(facet, base)];
            for v in corner.iter_mut() {
                if *v == 0.0 {
                    *v = 0.0;
                }
            }
            for (k, v) in corner.iter().enumerate() {
                row[base + 4 * k..base + 4 * k + 4].copy_from_slice(&single(*v).to_le_bytes());
            }
        }
        let [p0, p1, p2] = corners;
        let a = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]];
        let b = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]];
        let cross = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
        let norm = ((cross[0] * cross[0] + cross[1] * cross[1]) + cross[2] * cross[2]).sqrt();
        let normal = if norm > 1e-13 { cross.map(|v| v * (1.0 / norm)) } else { [0.0; 3] };
        for (i, v) in normal.iter().enumerate() {
            row[i * 4..i * 4 + 4].copy_from_slice(&(*v as f32).to_le_bytes());
        }
    }
    Ok(out)
}

fn main() -> Result<()> {
    let out = printed::out_dir("hardware/printed-parts/faucet/lever-replica")?;
    let body = lever_body()?;
    let color = Some(catalog::linear(lever::SRGB));
    let shown = Body { name: "lever", color, solid: &body };
    let mut said = write_printed(&out, NAME, &[shown])?;
    let print = body.rotate(V3::ZERO, V3::Y, 90.0).translate(v3(0.0, 0.0, lever::PRINTED_OUTSIDE_WIDTH / 2.0));
    write_stl(out.join(SIDE_DOWN), &[&print])?;
    let stl = authored_from_print(&std::fs::read(out.join(SIDE_DOWN))?)?;
    printed::keep(&out.join(format!("{NAME}.stl")), &stl)?;
    let step = std::fs::read(out.join(format!("{NAME}.step")))?;
    printed::keep(&out.join(format!("{NAME}.step.mesh")), &printed::payload(shown, &step, &stl)?)?;
    let files = said["files"].as_array_mut().context("the files written")?;
    files.push(Value::from(SIDE_DOWN));
    files.push(Value::from(format!("{NAME}.step.mesh")));
    println!("{said}");
    Ok(())
}
