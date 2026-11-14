//! The bridge stitch across the Sculpted base's shaft on the course where its ease ends: the
//! base's own section at the join, inset from its walls, crossed by bridge roads a bead apart
//! where native infill would start.

use crate::course_field::Move;
use crate::mesh::{stl_corners, Mesh};
use crate::sloped_courses::{section, Region};
use anyhow::{Context, Result, ensure};
use serde_json::{json, Value};
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

/// The spans of the level line at `y` that lie in `region`, each from its low X to its high X.
fn spans(region: &Region, y: f64) -> Vec<(f64, f64)> {
    let mut xs = Vec::new();
    for ring in region.rings() {
        for (i, a) in ring.iter().enumerate() {
            let b = ring[(i + 1) % ring.len()];
            if (a[1] > y) != (b[1] > y) {
                xs.push(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]));
            }
        }
    }
    xs.sort_by(f64::total_cmp);
    xs.chunks_exact(2).map(|c| (c[0], c[1])).collect()
}

/// The stitch's bridge roads across the shaft at plate height `z`, on the base posed at `pose`
/// and turned about X, as donor-course moves of course `layer`; and the stitch's report.
pub fn ties(mesh: &Path, z: f64, pose: [f64; 3], sin: f64, cos: f64, height: f64, layer: &str) -> Result<(Vec<Move>, Value)> {
    let stl = std::fs::read(mesh).with_context(|| format!("reading {}", mesh.display()))?;
    let mut base = Mesh::from_corners(&stl_corners(&stl).with_context(|| format!("reading {}", mesh.display()))?);
    for v in &mut base.vertices {
        let [x, y, n] = *v;
        *v = [pose[0] + x, pose[1] + cos * y + sin * n, pose[2] - sin * y + cos * n];
    }
    let shape = Region::from_rings(&section(&base, z)?);
    let bore = shape.holes();
    ensure!(shape.pieces() == 1 && bore.len() == 1, "Shaft stitch requires a single unbroken through-bore");
    let inset = shape.offset(-WALL_INSET);
    ensure!(!inset.is_empty(), "the shaft's wall erodes away");
    let (low, high) = inset.bounds();
    let first = (low[1] / TIE_SPACING - TIE_PHASE).ceil() as i64;
    let last = (high[1] / TIE_SPACING - TIE_PHASE).floor() as i64;
    ensure!(height == 0.24, "the stitch's bead height is the donor's nominal course");
    let bead_area = height * (TIE_WIDTH - height) + std::f64::consts::PI * (height / 2.0).powi(2);
    let e_per_mm = FILAMENT_FLOW * bead_area / (std::f64::consts::PI * 0.875f64.powi(2));
    let (width, bead, layer, feature): (Rc<str>, Rc<str>, Rc<str>, Rc<str>) =
        (Rc::from("0.42"), Rc::from("0.24"), Rc::from(layer), Rc::from("Bridge"));
    let mut output: Vec<Move> = Vec::new();
    for index in first..=last {
        let y = (index as f64 + TIE_PHASE) * TIE_SPACING;
        for (a, b) in spans(&inset, y) {
            if b - a < MINIMUM_TIE_LENGTH {
                continue;
            }
            let (from, to) = if index.rem_euclid(2) == 0 { (a, b) } else { (b, a) };
            output.push(Move {
                start: [from, y, z], end: [to, y, z], feed: BRIDGE_FEED, e: Some((b - a) * e_per_mm), arc: None,
                feature: feature.clone(), width: width.clone(), bead_height: bead.clone(), fan: BRIDGE_FAN,
                acceleration: BRIDGE_ACCEL, layer: layer.clone(),
            });
        }
    }
    let report = json!({
        "inside_exact_model_section_mm2": shape.area(),
        "through_bore_mm2": bore[0].area(),
        "inset_mm": WALL_INSET,
        "width_mm": TIE_WIDTH,
        "pitch_mm": TIE_SPACING,
        "feed_mm_per_s": BRIDGE_FEED / 60.0,
        "bridge_count": output.len(),
        "bridge_length_mm": output.iter().map(|m| (m.start[0] - m.end[0]).abs()).sum::<f64>(),
        "filament_length_mm": output.iter().filter_map(|m| m.e).sum::<f64>(),
        "physical_course_mm": z,
        "model_sha256": crate::sha256_hex(&stl),
    });
    Ok((output, report))
}
