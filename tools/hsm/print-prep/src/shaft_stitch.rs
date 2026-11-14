//! The bridge stitch across the Sculpted base's shaft on the course where its ease ends: the
//! base's own section at the join, inset from its walls, crossed by bridge roads a bead apart
//! where native infill would start.
//!
//! The section's loops are read as GEOS merges and polygonizes them: each starts at its least
//! vertex, the wall clockwise and the bore counterclockwise. The inset is GEOS's buffer of that
//! annulus, and each road ends where GEOS's intersector crosses the inset.

use crate::base_courses::{float, int};
use crate::python_text::{round, sum};
use crate::course_field::Move;
use crate::json::Json;
use crate::ring_offset::{Point, Polygon, buffer_edges, clip_segment, inside, signed_area};
use anyhow::{Context, Result, bail, ensure};
use std::collections::HashMap;
use std::path::Path;
use std::rc::Rc;

const TIE_WIDTH: f64 = 0.42;
const TIE_SPACING: f64 = TIE_WIDTH;
const TIE_PHASE: f64 = 2.0 / 3.0;
const WALL_INSET: f64 = 0.65;
const BRIDGE_FEED: f64 = 15.0 * 60.0;
const BRIDGE_FAN: i64 = 178;
const BRIDGE_ACCEL: i64 = 8000;
const FILAMENT_FLOW: f64 = 0.9555;
const MINIMUM_TIE_LENGTH: f64 = 0.1;
/// The quadrant segments Shapely's buffer asks GEOS for.
const QUADRANT_SEGMENTS: u32 = 16;

/// The plate-frame section of the base's STL, posed at `pose` and turned about X, through the
/// level plane at `z`: a segment for each crossing triangle, its ends rounded as the stitch reads
/// them.
fn section(stl: &[u8], z: f64, pose: [f64; 3], sin: f64, cos: f64) -> Result<Vec<(Point, Point)>> {
    ensure!(stl.len() >= 84 && (stl.len() - 84) % 50 == 0, "the shaft STL is not a binary STL");
    let count = u32::from_le_bytes([stl[80], stl[81], stl[82], stl[83]]);
    ensure!(count != 0, "Shaft STL contains no triangles");
    let [x0, y0, z0] = pose;
    let mut out = Vec::new();
    for t in stl[84..].chunks_exact(50) {
        let f = |i: usize| f32::from_le_bytes([t[4 * i], t[4 * i + 1], t[4 * i + 2], t[4 * i + 3]]) as f64;
        let corners: [[f64; 3]; 3] = std::array::from_fn(|k| {
            let (x, y, n) = (f(3 + 3 * k), f(4 + 3 * k), f(5 + 3 * k));
            [x0 + x, y0 + cos * y + sin * n, z0 - sin * y + cos * n]
        });
        let below = corners.map(|p| p[2] < z);
        if below.iter().all(|b| *b) || !below.iter().any(|b| *b) {
            continue;
        }
        let mut crossings: Vec<Point> = Vec::new();
        for k in 0..3 {
            let (a, b) = (corners[k], corners[(k + 1) % 3]);
            if (a[2] < z) == (b[2] < z) {
                continue;
            }
            let t = (z - a[2]) / (b[2] - a[2]);
            crossings.push([0, 1].map(|i| round(a[i] + t * (b[i] - a[i]), 5)));
        }
        let distinct = crossings.len() == 2 && crossings[0] != crossings[1];
        if distinct {
            out.push((crossings[0], crossings[1]));
        }
    }
    Ok(out)
}

fn key(p: Point) -> (u64, u64) {
    ((p[0] + 0.0).to_bits(), (p[1] + 0.0).to_bits())
}

/// The section's closed loops, each from its least vertex by X then Y.
fn loops(segments: &[(Point, Point)]) -> Result<Vec<Vec<Point>>> {
    let mut at: HashMap<(u64, u64), Vec<usize>> = HashMap::new();
    for (i, (a, b)) in segments.iter().enumerate() {
        at.entry(key(*a)).or_default().push(i);
        at.entry(key(*b)).or_default().push(i);
    }
    ensure!(at.values().all(|v| v.len() == 2), "the shaft section is not made of closed loops");
    let mut used = vec![false; segments.len()];
    let mut out = Vec::new();
    for start in 0..segments.len() {
        if used[start] {
            continue;
        }
        used[start] = true;
        let (first, mut here) = segments[start];
        let mut ring = vec![first, here];
        while key(here) != key(first) {
            let next = at[&key(here)].iter().copied().find(|&i| !used[i]).context("a broken section loop")?;
            used[next] = true;
            let (a, b) = segments[next];
            here = if key(a) == key(here) { b } else { a };
            ring.push(here);
        }
        ring.pop();
        let least = (0..ring.len()).min_by(|&i, &j| {
            let (a, b) = (ring[i], ring[j]);
            a[0].partial_cmp(&b[0]).unwrap().then(a[1].partial_cmp(&b[1]).unwrap())
        }).context("an empty loop")?;
        ring.rotate_left(least);
        out.push(ring);
    }
    Ok(out)
}

/// The loop closed and turned the way GEOS's polygonizer turns it.
fn ring(mut points: Vec<Point>, clockwise: bool) -> Vec<Point> {
    points.push(points[0]);
    if (signed_area(&points) > 0.0) != clockwise {
        points.reverse();
    }
    points
}

/// The shaft's annulus at `z`: its outer wall and its bore.
fn annulus(stl: &[u8], z: f64, pose: [f64; 3], sin: f64, cos: f64) -> Result<Polygon> {
    let mut found = loops(&section(stl, z, pose, sin, cos)?)?;
    if found.len() != 2 {
        bail!("Shaft stitch requires a single unbroken through-bore");
    }
    found.sort_by(|a, b| {
        let area = |r: &Vec<Point>| signed_area(&ring(r.clone(), true)).abs();
        area(b).partial_cmp(&area(a)).unwrap()
    });
    let mut found = found.into_iter();
    let shell = ring(found.next().unwrap(), true);
    let hole = ring(found.next().unwrap(), false);
    ensure!(inside(hole[0], &shell), "Shaft stitch requires a single unbroken through-bore");
    Ok(Polygon { shell, holes: vec![hole] })
}

fn bounds(ring: &[Point]) -> [f64; 4] {
    ring.iter().fold([f64::INFINITY, f64::INFINITY, f64::NEG_INFINITY, f64::NEG_INFINITY],
        |b, p| [b[0].min(p[0]), b[1].min(p[1]), b[2].max(p[0]), b[3].max(p[1])])
}

fn ring_area(ring: &[Point]) -> f64 {
    signed_area(ring).abs()
}

/// The stitch's bridge roads across the shaft at plate height `z`, on the base posed at `pose`,
/// as donor-course moves of course `layer`; and the stitch's report.
pub fn ties(mesh: &Path, z: f64, pose: [f64; 3], sin: f64, cos: f64, height: f64, layer: &str) -> Result<(Vec<Move>, Json)> {
    let stl = std::fs::read(mesh).with_context(|| format!("reading {}", mesh.display()))?;
    let shape = annulus(&stl, z, pose, sin, cos)?;
    let patched = buffer_edges(&shape, -WALL_INSET, QUADRANT_SEGMENTS)?;
    ensure!(!patched.is_empty(), "the shaft's wall erodes away");
    let ends: Vec<Point> = patched.iter().flat_map(|(a, b)| [*a, *b]).collect();
    let [x1, y1, x2, y2] = bounds(&ends);
    let first = (y1 / TIE_SPACING - TIE_PHASE).ceil() as i64;
    let last = (y2 / TIE_SPACING - TIE_PHASE).floor() as i64;
    let bead_area = height * (TIE_WIDTH - height) + std::f64::consts::PI * ((height / 2.0) * (height / 2.0));
    let filament_area = std::f64::consts::PI * (0.875 * 0.875);
    let e_per_mm = FILAMENT_FLOW * bead_area / filament_area;
    let (width, bead, layer): (Rc<str>, Rc<str>, Rc<str>) = (Rc::from("0.42"), Rc::from("0.24"), Rc::from(layer));
    let feature: Rc<str> = Rc::from("Bridge");
    ensure!(height == 0.24, "the stitch's bead height is the donor's nominal course");
    let mut output: Vec<Move> = Vec::new();
    for index in first..=last {
        let y = (index as f64 + TIE_PHASE) * TIE_SPACING;
        for (a, b) in clip_segment([x1, y], [x2, y], &patched)? {
            let (dx, dy) = (b[0] - a[0], b[1] - a[1]);
            let length = (dx * dx + dy * dy).sqrt();
            if length < MINIMUM_TIE_LENGTH {
                continue;
            }
            let (lo, hi) = (a[0].min(b[0]), a[0].max(b[0]));
            let (from, to) = if index.rem_euclid(2) == 0 { (lo, hi) } else { (hi, lo) };
            output.push(Move {
                start: [from, y, z], end: [to, y, z], feed: BRIDGE_FEED, e: Some(length * e_per_mm), arc: None,
                feature: feature.clone(), width: width.clone(), bead_height: bead.clone(), fan: BRIDGE_FAN,
                acceleration: BRIDGE_ACCEL, layer: layer.clone(),
            });
        }
    }
    let shell_area = ring_area(&shape.shell);
    let bore = ring_area(&shape.holes[0]);
    let report = Json::Map(vec![
        ("inside_exact_model_section_mm2".into(), float(shell_area - bore)),
        ("through_bore_mm2".into(), float(bore)),
        ("inset_mm".into(), float(WALL_INSET)),
        ("width_mm".into(), float(TIE_WIDTH)),
        ("pitch_mm".into(), float(TIE_SPACING)),
        ("feed_mm_per_s".into(), float(BRIDGE_FEED / 60.0)),
        ("bridge_count".into(), int(output.len() as i64)),
        ("bridge_length_mm".into(), float(sum(&output.iter().map(|m| (m.start[0] - m.end[0]).abs()).collect::<Vec<_>>()))),
        ("filament_length_mm".into(), float(sum(&output.iter().map(|m| m.e.unwrap_or(0.0)).collect::<Vec<_>>()))),
        ("physical_course_mm".into(), float(z)),
        ("model_sha256".into(), Json::Text(crate::sha256_hex(&stl))),
    ]);
    Ok((output, report))
}
