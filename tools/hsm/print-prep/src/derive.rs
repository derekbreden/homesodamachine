//! Print features read from a piece's mesh in its print frame: the layer bands, painted facets,
//! fin volumes and review windows a project needs, found from faces chosen by orientation and by
//! place on the part's own bounds. A feature whose faces are missing, or whose measured extent
//! leaves its declared range, is an error naming what was found.

use crate::mesh::vertex_components;
use anyhow::{bail, Result};
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, HashMap};

pub const FIRST_LAYER: f64 = 0.20;
pub const LAYER: f64 = 0.24;
/// The normal's Z on an additive chamfer tangent to an expanding round, at the outward run per
/// millimetre of rise `cadlib/overhang_round.py` gives it.
pub fn chamfer_nz() -> f64 { -1.0 / 5f64.sqrt() }
/// The chamfer's rise per radius, and the arc retained above it.
pub fn rise_per_radius() -> f64 { 1.0 - 0.5 / 1.25f64.sqrt() }
pub fn arc_per_radius() -> f64 { 0.5 / 1.25f64.sqrt() }

pub struct Geometry {
    pub t: Vec<[[f64; 3]; 3]>,
    pub faces: Vec<[usize; 3]>,
    pub n: Vec<[f64; 3]>,
    pub a: Vec<f64>,
    pub c: Vec<[f64; 3]>,
    pub zlo: Vec<f64>,
    pub zhi: Vec<f64>,
    pub low: [f64; 3],
    pub high: [f64; 3],
    /// Source-frame distance to a declared straight wall, independent of projecting corners.
    pub wall_x: Vec<f64>,
}

/// A feature's record, the facets it paints for support, and its per-facet paint codes.
pub struct Feature {
    pub record: Map<String, Value>,
    pub paint_faces: Vec<usize>,
    pub paint_codes: BTreeMap<usize, String>,
    /// A ceiling's boundary points, for the fins that follow it.
    pub boundary_points: Vec<[f64; 2]>,
}

impl Feature {
    pub fn kind(&self) -> &str { self.record.get("kind").and_then(Value::as_str).unwrap_or("") }
    pub fn enabled(&self) -> bool { self.record.get("enabled") != Some(&Value::Bool(false)) }
    fn plain(record: Map<String, Value>) -> Feature {
        Feature { record, paint_faces: vec![], paint_codes: BTreeMap::new(), boundary_points: vec![] }
    }
}

fn num(v: &Value, key: &str) -> Option<f64> { v.get(key).and_then(Value::as_f64) }
fn round3(v: f64) -> f64 { (v * 1000.0).round() / 1000.0 }

impl Geometry {
    pub fn new(t: Vec<[[f64; 3]; 3]>, faces: Vec<[usize; 3]>) -> Geometry {
        let mut n = Vec::with_capacity(t.len());
        let mut a = Vec::with_capacity(t.len());
        let mut c = Vec::with_capacity(t.len());
        let (mut zlo, mut zhi) = (Vec::with_capacity(t.len()), Vec::with_capacity(t.len()));
        let (mut low, mut high) = ([f64::INFINITY; 3], [f64::NEG_INFINITY; 3]);
        for tri in &t {
            let (u, w) = (sub(tri[1], tri[0]), sub(tri[2], tri[0]));
            let cross = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]];
            let length = (cross[0] * cross[0] + cross[1] * cross[1] + cross[2] * cross[2]).sqrt();
            n.push(cross.map(|x| x / length.max(1e-30)));
            a.push(length / 2.0);
            c.push([0, 1, 2].map(|k| (tri[0][k] + tri[1][k] + tri[2][k]) / 3.0));
            zlo.push(tri[0][2].min(tri[1][2]).min(tri[2][2]));
            zhi.push(tri[0][2].max(tri[1][2]).max(tri[2][2]));
            for p in tri {
                for k in 0..3 {
                    low[k] = low[k].min(p[k]);
                    high[k] = high[k].max(p[k]);
                }
            }
        }
        Geometry { t, faces, n, a, c, zlo, zhi, low, high, wall_x: vec![] }
    }

    pub fn select(&self, spec: &Value) -> Vec<bool> {
        let mut mask = vec![true; self.t.len()];
        let middle = (self.low[2] + self.high[2]) / 2.0;
        for i in 0..self.t.len() {
            let (n, c) = (self.n[i], self.c[i]);
            let mut keep = true;
            if let Some(range) = spec.get("normal_z").and_then(Value::as_array) {
                let (lo, hi) = (range[0].as_f64().unwrap_or(-1.0), range[1].as_f64().unwrap_or(1.0));
                keep &= n[2] >= lo && n[2] <= hi;
            }
            for (axis, key) in [(0usize, "x"), (1, "y")] {
                if let Some(m) = num(spec, &format!("abs_normal_{key}_max")) { keep &= n[axis].abs() <= m; }
                if let Some(m) = num(spec, &format!("normal_{key}_min")) { keep &= n[axis] >= m; }
                if let Some(m) = num(spec, &format!("normal_{key}_max")) { keep &= n[axis] <= m; }
            }
            if let Some(m) = num(spec, "top_mm") { keep &= c[2] >= self.high[2] - m; }
            if let Some(m) = num(spec, "bottom_mm") { keep &= c[2] <= self.low[2] + m; }
            let side_x = (c[0] - self.low[0]).min(self.high[0] - c[0]);
            let side_y = (c[1] - self.low[1]).min(self.high[1] - c[1]);
            if let Some(m) = num(spec, "exterior_x_mm") { keep &= side_x <= m; }
            if let Some(m) = num(spec, "wall_x_mm") { keep &= self.wall_x.get(i).is_some_and(|d| *d <= m); }
            if let Some(m) = num(spec, "exterior_y_mm") { keep &= side_y <= m; }
            if let Some(half) = spec.get("half").and_then(Value::as_str) {
                keep &= if half == "lower" { c[2] < middle } else { c[2] >= middle };
            }
            mask[i] = keep;
        }
        mask
    }

    /// The masked faces in vertex-connected groups, each ascending, ordered by first face.
    pub fn components(&self, mask: &[bool]) -> Vec<Vec<usize>> {
        let index: Vec<usize> = (0..mask.len()).filter(|&i| mask[i]).collect();
        if index.is_empty() {
            return vec![];
        }
        let faces: Vec<[usize; 3]> = index.iter().map(|&i| self.faces[i]).collect();
        let labels = vertex_components(&faces);
        let count = labels.iter().max().map_or(0, |m| m + 1);
        let mut groups = vec![Vec::new(); count];
        for (k, &label) in labels.iter().enumerate() {
            groups[label].push(index[k]);
        }
        groups
    }

    fn record(&self, faces: &[usize]) -> Value {
        let (mut low, mut high) = ([f64::INFINITY; 3], [f64::NEG_INFINITY; 3]);
        for &f in faces {
            for p in &self.t[f] {
                for k in 0..3 {
                    low[k] = low[k].min(p[k]);
                    high[k] = high[k].max(p[k]);
                }
            }
        }
        let area: f64 = faces.iter().map(|&f| self.a[f]).sum();
        json!({"faces": faces.len(), "area_mm2": round3(area),
               "bounds_print_mm": [low.map(round3), high.map(round3)]})
    }
}

fn sub(a: [f64; 3], b: [f64; 3]) -> [f64; 3] { [a[0] - b[0], a[1] - b[1], a[2] - b[2]] }

fn check(feature: &Value, name: &str, value: f64, key: &str) -> Result<()> {
    if let Some(bounds) = feature.get("expect").and_then(|e| e.get(key)).and_then(Value::as_array) {
        let (lo, hi) = (bounds[0].as_f64().unwrap_or(f64::NEG_INFINITY), bounds[1].as_f64().unwrap_or(f64::INFINITY));
        if !(lo <= value && value <= hi) {
            bail!("{}: {name} {value:.3} is outside the declared [{lo}, {hi}]", feature["name"].as_str().unwrap_or(""));
        }
    }
    Ok(())
}

fn base(feature: &Value, kind: &str) -> Map<String, Value> {
    let mut m = Map::new();
    m.insert("name".into(), feature["name"].clone());
    m.insert("kind".into(), json!(kind));
    m
}

/// A show surface's complete print-Z span takes the fine layer height.
pub fn fine_band(geo: &Geometry, feature: &Value) -> Result<Feature> {
    let (mut kept, mut records) = (Vec::new(), Vec::new());
    for members in geo.components(&geo.select(&feature["select"])) {
        let area: f64 = members.iter().map(|&f| geo.a[f]).sum();
        if area < num(feature, "min_component_area_mm2").unwrap_or(10.0) { continue; }
        let nz = members.iter().map(|&f| geo.n[f][2]).fold(f64::NEG_INFINITY, f64::max);
        if nz < num(feature, "rolls_to_normal_z").unwrap_or(0.0) { continue; }
        records.push(geo.record(&members));
        kept.push(members);
    }
    if kept.is_empty() {
        bail!("{}: no faces match {}", feature["name"].as_str().unwrap_or(""), feature["select"]);
    }
    let faces: Vec<usize> = kept.concat();
    let low = faces.iter().map(|&f| geo.zlo[f]).fold(f64::INFINITY, f64::min);
    let high = faces.iter().map(|&f| geo.zhi[f]).fold(f64::NEG_INFINITY, f64::max);
    check(feature, "span height", high - low, "span_mm")?;
    check(feature, "component count", kept.len() as f64, "components")?;
    check(feature, "area", faces.iter().map(|&f| geo.a[f]).sum(), "area_mm2")?;
    let mut m = base(feature, "fine_band");
    m.insert("span_print_z_mm".into(), json!([low, high]));
    m.insert("layer_height_mm".into(), json!(num(feature, "layer_height_mm").unwrap_or(0.08)));
    m.insert("components".into(), json!(records));
    m.insert("reason".into(), feature["reason"].clone());
    let allow = feature.get("allow_support").and_then(Value::as_bool).unwrap_or(false);
    Ok(Feature { record: m, paint_faces: if allow { vec![] } else { faces }, paint_codes: BTreeMap::new(), boundary_points: vec![] })
}

/// An expanding print-down round with its additive chamfer: more walls through its rise.
pub fn transition_band(geo: &Geometry, feature: &Value) -> Result<Feature> {
    let zone = geo.select(&feature["select"]);
    let tolerance = num(feature, "chamfer_normal_tolerance").unwrap_or(0.003);
    let chamfer: Vec<bool> = (0..zone.len()).map(|i| zone[i] && (geo.n[i][2] - chamfer_nz()).abs() < tolerance).collect();
    let area: f64 = (0..zone.len()).filter(|&i| chamfer[i]).map(|i| geo.a[i]).sum();
    let name = feature["name"].as_str().unwrap_or("");
    if !chamfer.iter().any(|&b| b) {
        bail!("{name}: no 0.5:1 chamfer faces in {}", feature["select"]);
    }
    check(feature, "chamfer area", area, "chamfer_area_mm2")?;
    // The chamfer starts at its lowest geometric edge; interior splits do not give it a foot.
    let significant: Vec<usize> = (0..zone.len()).filter(|&i| chamfer[i] && geo.a[i] >= 0.05).collect();
    let lowest = significant.iter().map(|&i| geo.zlo[i]).fold(f64::INFINITY, f64::min);
    let top = significant.iter().map(|&i| geo.zhi[i]).fold(f64::NEG_INFINITY, f64::max);
    // The straight run reaches the top, and its faces reach down to the run's foot, where the
    // round meets its ceiling. A corner return follows its arc lower; the band covers it, but
    // the run alone measures the round.
    let foot = significant.iter().filter(|&&i| geo.zhi[i] >= top - 1e-3).map(|&i| geo.zlo[i]).fold(f64::INFINITY, f64::min);
    let radius = num(feature, "radius_mm").unwrap_or(0.0);
    let measured = (top - foot) / rise_per_radius();
    if (measured / radius - 1.0).abs() > num(feature, "radius_tolerance").unwrap_or(0.1) {
        bail!("{name}: the chamfer rises {:.3} mm above its foot at print Z{foot:.3}, an R{measured:.2} transition against the declared R{radius}", top - foot);
    }
    let (low, high) = (lowest, top + arc_per_radius() * radius);
    let paint: Vec<usize> = (0..zone.len()).filter(|&i| zone[i] && geo.n[i][2] < -0.02 && geo.n[i][2] > -0.999
        && geo.zhi[i] >= low - 0.01 && geo.zlo[i] <= high + 0.01).collect();
    let mut m = base(feature, "transition_band");
    m.insert("span_print_z_mm".into(), json!([low, high]));
    m.insert("foot_print_z_mm".into(), json!(foot));
    m.insert("radius_mm".into(), json!(radius));
    m.insert("chamfer_area_mm2".into(), json!(area));
    m.insert("wall_loops".into(), json!(feature.get("wall_loops").and_then(Value::as_i64).unwrap_or(6)));
    m.insert("painted".into(), geo.record(&paint));
    m.insert("reason".into(), feature["reason"].clone());
    Ok(Feature { record: m, paint_faces: paint, paint_codes: BTreeMap::new(), boundary_points: vec![] })
}

/// The flat lifting ceiling at a transition's foot keeps tree contacts off its boundary strip:
/// a point of it may take a contact when it lies at least the inset from the ceiling's edge.
pub fn ceiling_inset(geo: &Geometry, feature: &Value, foot_z: f64) -> Result<Feature> {
    let zone = geo.select(&feature["select"]);
    let flat: Vec<usize> = (0..zone.len()).filter(|&i| zone[i] && geo.n[i][2] < -0.999 && (geo.c[i][2] - foot_z).abs() < 0.01).collect();
    let name = feature["name"].as_str().unwrap_or("");
    if flat.is_empty() {
        bail!("{name}: no flat ceiling at print Z{foot_z:.3}");
    }
    let (boundary, points) = outline(geo, &flat);
    let area: f64 = flat.iter().map(|&f| tri_area(xy(&geo.t[f]))).sum();
    check(feature, "ceiling area", area, "area_mm2")?;
    let inset = num(feature, "inset_mm").unwrap_or(0.0);
    let depth_limit = feature.get("paint_depth").and_then(Value::as_u64).unwrap_or(7) as usize;
    let mut blocked = 0.0;
    let mut codes = BTreeMap::new();
    for &f in &flat {
        let code = encode(xy(&geo.t[f]), 0, depth_limit, inset, &boundary, &mut blocked);
        if code != "0" {
            codes.insert(f, code);
        }
    }
    let mut m = base(feature, "ceiling_inset");
    m.insert("ceiling_print_z_mm".into(), json!(foot_z));
    m.insert("ceiling_area_mm2".into(), json!(area));
    m.insert("inset_mm".into(), json!(inset));
    m.insert("blocked_area_mm2".into(), json!(blocked));
    m.insert("reason".into(), feature["reason"].clone());
    Ok(Feature { record: m, paint_faces: vec![], paint_codes: codes, boundary_points: points })
}

fn xy(t: &[[f64; 3]; 3]) -> [[f64; 2]; 3] { t.map(|p| [p[0], p[1]]) }

/// The outline of the union of `flat`'s facets in plan, as segments, and their end points.
///
/// An edge no other facet shares is on the outline unless facets continue past it, as they do
/// across a T-junction, where neighbours meet one long edge with several short ones. Each such
/// edge is cut at the vertices lying along it, and a piece is kept when no facet covers the
/// point just outside its middle.
fn outline(geo: &Geometry, flat: &[usize]) -> (Vec<[[f64; 2]; 2]>, Vec<[f64; 2]>) {
    // Past float32 rounding of the vertices, short of any real gap.
    const NEAR: f64 = 1e-4;
    let mut uses: HashMap<(usize, usize), (usize, [usize; 2])> = HashMap::new();
    for &f in flat {
        let face = geo.faces[f];
        for k in 0..3 {
            let (a, b) = (face[k], face[(k + 1) % 3]);
            uses.entry((a.min(b), a.max(b))).or_insert((0, [f, k])).0 += 1;
        }
    }
    let plan: Vec<[[f64; 2]; 3]> = flat.iter().map(|&f| xy(&geo.t[f])).collect();
    let corners: Vec<[f64; 2]> = plan.iter().flatten().copied().collect();
    let mut edges: Vec<(usize, usize)> = uses.iter().filter(|(_, (n, _))| *n == 1).map(|(_, (_, [f, k]))| (*f, *k)).collect();
    edges.sort_unstable();
    let (mut boundary, mut points) = (Vec::new(), Vec::new());
    for (f, k) in edges {
        let t = xy(&geo.t[f]);
        let (p, q, r) = (t[k], t[(k + 1) % 3], t[(k + 2) % 3]);
        let d = [q[0] - p[0], q[1] - p[1]];
        let length = (d[0] * d[0] + d[1] * d[1]).sqrt();
        if length == 0.0 {
            continue;
        }
        let mut cuts = vec![0.0, 1.0];
        for v in &corners {
            let along = ((v[0] - p[0]) * d[0] + (v[1] - p[1]) * d[1]) / (length * length);
            let off = ((v[0] - p[0]) * d[1] - (v[1] - p[1]) * d[0]).abs() / length;
            if off < NEAR && along * length > NEAR && (1.0 - along) * length > NEAR {
                cuts.push(along);
            }
        }
        cuts.sort_by(|a, b| a.partial_cmp(b).unwrap());
        cuts.dedup_by(|a, b| (*a - *b) * length < NEAR);
        let mut out = [d[1] / length, -d[0] / length];
        if (r[0] - p[0]) * out[0] + (r[1] - p[1]) * out[1] > 0.0 {
            out = [-out[0], -out[1]];
        }
        for w in cuts.windows(2) {
            let middle = (w[0] + w[1]) / 2.0;
            let probe = [p[0] + middle * d[0] + out[0] * NEAR, p[1] + middle * d[1] + out[1] * NEAR];
            let covered = plan.iter().zip(flat).any(|(u, &g)| g != f && tri_area(*u) > 0.0 && inside_triangle(probe, *u));
            if !covered {
                let (a, b) = ([p[0] + w[0] * d[0], p[1] + w[0] * d[1]], [p[0] + w[1] * d[0], p[1] + w[1] * d[1]]);
                boundary.push([a, b]);
                points.push(a);
                points.push(b);
            }
        }
    }
    (boundary, points)
}

fn tri_area(t: [[f64; 2]; 3]) -> f64 {
    ((t[1][0] - t[0][0]) * (t[2][1] - t[0][1]) - (t[2][0] - t[0][0]) * (t[1][1] - t[0][1])).abs() / 2.0
}

fn encode(t: [[f64; 2]; 3], depth: usize, limit: usize, inset: f64, boundary: &[[[f64; 2]; 2]], blocked: &mut f64) -> String {
    if covers(t, inset, boundary) {
        return "0".into();
    }
    if !may_intersect(t, inset, boundary) || depth == limit {
        *blocked += tri_area(t);
        return "8".into();
    }
    let [a, b, c] = t;
    let mid = |p: [f64; 2], q: [f64; 2]| [(p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0];
    let (ab, bc, ca) = (mid(a, b), mid(b, c), mid(c, a));
    let mut out = String::new();
    for child in [[a, ab, ca], [ab, b, bc], [bc, c, ca], [ab, bc, ca]] {
        out.push_str(&encode(child, depth + 1, limit, inset, boundary, blocked));
    }
    out.push('3');
    out
}

/// Every point of the facet lies at least `inset` from the ceiling's edge.
fn covers(t: [[f64; 2]; 3], inset: f64, boundary: &[[[f64; 2]; 2]]) -> bool {
    boundary.iter().all(|s| segment_triangle_distance(*s, t) >= inset)
}

/// Some point of the facet may lie at least `inset` from the edge; certain when a sampled point
/// does, and ruled out only when no point can.
fn may_intersect(t: [[f64; 2]; 3], inset: f64, boundary: &[[[f64; 2]; 2]]) -> bool {
    let [a, b, c] = t;
    let centroid = [(a[0] + b[0] + c[0]) / 3.0, (a[1] + b[1] + c[1]) / 3.0];
    let samples = [a, b, c, centroid];
    let best = samples.iter().map(|p| boundary.iter().map(|s| point_segment(*p, *s)).fold(f64::INFINITY, f64::min)).fold(0.0, f64::max);
    if best >= inset {
        return true;
    }
    // Distance moves no faster than the point does, and every point lies within the farthest
    // corner's distance of the centroid.
    let reach = [a, b, c].iter().map(|p| ((p[0] - centroid[0]).powi(2) + (p[1] - centroid[1]).powi(2)).sqrt()).fold(0.0, f64::max);
    best + reach >= inset
}

fn point_segment(p: [f64; 2], s: [[f64; 2]; 2]) -> f64 {
    let (a, b) = (s[0], s[1]);
    let (dx, dy) = (b[0] - a[0], b[1] - a[1]);
    let len2 = dx * dx + dy * dy;
    let t = if len2 > 0.0 { (((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / len2).clamp(0.0, 1.0) } else { 0.0 };
    ((p[0] - a[0] - t * dx).powi(2) + (p[1] - a[1] - t * dy).powi(2)).sqrt()
}

fn orient(a: [f64; 2], b: [f64; 2], c: [f64; 2]) -> f64 {
    (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
}

fn segments_cross(p: [[f64; 2]; 2], q: [[f64; 2]; 2]) -> bool {
    let (d1, d2) = (orient(q[0], q[1], p[0]), orient(q[0], q[1], p[1]));
    let (d3, d4) = (orient(p[0], p[1], q[0]), orient(p[0], p[1], q[1]));
    ((d1 > 0.0) != (d2 > 0.0)) && ((d3 > 0.0) != (d4 > 0.0))
}

fn inside_triangle(p: [f64; 2], t: [[f64; 2]; 3]) -> bool {
    let (d1, d2, d3) = (orient(t[0], t[1], p), orient(t[1], t[2], p), orient(t[2], t[0], p));
    let (neg, pos) = (d1 < 0.0 || d2 < 0.0 || d3 < 0.0, d1 > 0.0 || d2 > 0.0 || d3 > 0.0);
    !(neg && pos)
}

fn segment_triangle_distance(s: [[f64; 2]; 2], t: [[f64; 2]; 3]) -> f64 {
    if inside_triangle(s[0], t) || inside_triangle(s[1], t) {
        return 0.0;
    }
    let edges = [[t[0], t[1]], [t[1], t[2]], [t[2], t[0]]];
    if edges.iter().any(|e| segments_cross(s, *e)) {
        return 0.0;
    }
    let mut d = f64::INFINITY;
    for e in edges {
        d = d.min(point_segment(s[0], e)).min(point_segment(s[1], e));
    }
    for p in t {
        d = d.min(point_segment(p, s));
    }
    d
}

pub fn layer_index_below(z: f64) -> i64 { ((z - FIRST_LAYER + LAYER / 2.0) / LAYER).floor() as i64 }

/// The room under each zip-tie channel roof, as a box from the roof down to its floor or the
/// declared cavity depth.
pub fn tie_windows(geo: &Geometry, feature: &Value) -> Result<Feature> {
    let zone = geo.select(feature.get("select").unwrap_or(&json!({})));
    let up: Vec<usize> = (0..geo.t.len()).filter(|&i| geo.n[i][2] > 0.999).collect();
    let depth = num(feature, "cavity_depth_mm").unwrap_or(0.0);
    let widths: Vec<f64> = feature["channel_widths_mm"].as_array().map(|a| a.iter().filter_map(Value::as_f64).collect()).unwrap_or_default();
    let mask: Vec<bool> = (0..zone.len()).map(|i| zone[i] && geo.n[i][2] < -0.999).collect();
    let mut windows = Vec::new();
    for members in geo.components(&mask) {
        let (mut low, mut high) = ([f64::INFINITY; 3], [f64::NEG_INFINITY; 3]);
        for &f in &members {
            for p in &geo.t[f] {
                for k in 0..3 { low[k] = low[k].min(p[k]); high[k] = high[k].max(p[k]); }
            }
        }
        let size = [high[0] - low[0], high[1] - low[1]];
        let short = size[0].min(size[1]);
        let closest = widths.iter().map(|w| (w - short).abs()).fold(f64::INFINITY, f64::min);
        if closest > num(feature, "width_tolerance_mm").unwrap_or(0.06) || size[0].max(size[1]) > num(feature, "long_side_max_mm").unwrap_or(f64::INFINITY) {
            continue;
        }
        if low[0] < geo.low[0] + 0.5 || low[1] < geo.low[1] + 0.5 || high[0] > geo.high[0] - 0.5 || high[1] > geo.high[1] - 0.5 {
            continue;
        }
        if members.iter().map(|&f| geo.a[f]).sum::<f64>() < 0.85 * size[0] * size[1] {
            continue;
        }
        let mut zs: Vec<f64> = members.iter().map(|&f| geo.c[f][2]).collect();
        zs.sort_by(|a, b| a.partial_cmp(b).unwrap());
        let roof = if zs.len() % 2 == 1 { zs[zs.len() / 2] } else { (zs[zs.len() / 2 - 1] + zs[zs.len() / 2]) / 2.0 };
        if roof - geo.low[2] < depth {
            continue;
        }
        let floors: Vec<f64> = up.iter().filter(|&&i| {
            let c = geo.c[i];
            c[0] > low[0] && c[0] < high[0] && c[1] > low[1] && c[1] < high[1] && c[2] < roof && c[2] >= roof - depth
        }).map(|&i| geo.c[i][2]).collect();
        let floor = floors.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        let floor = if floors.is_empty() { roof - depth } else { floor };
        windows.push(json!({"roof_print_z_mm": roof, "floor_print_z_mm": floor,
            "box_print_mm": [[low[0], low[1], floor], [high[0], high[1], roof]], "roof": geo.record(&members)}));
    }
    check(feature, "window count", windows.len() as f64, "count")?;
    let mut m = base(feature, "tie_windows");
    m.insert("windows".into(), json!(windows));
    m.insert("blockers".into(), json!(feature.get("blockers").and_then(Value::as_bool).unwrap_or(false)));
    m.insert("blocker_roof_overlap_mm".into(), json!(num(feature, "blocker_roof_overlap_mm").unwrap_or(0.0)));
    m.insert("reason".into(), feature["reason"].clone());
    Ok(Feature::plain(m))
}

/// Interrupted removable walls from the bed to a flat ceiling's exterior edge.
pub fn edge_fins(geo: &Geometry, feature: &Value, ceiling: &Feature) -> Result<Feature> {
    let xs = &ceiling.boundary_points;
    let (width, overhang, gap) = (num(feature, "wall_mm").unwrap_or(0.0), num(feature, "outboard_mm").unwrap_or(0.0), num(feature, "top_gap_mm").unwrap_or(0.0));
    let ceiling_z = ceiling.record["ceiling_print_z_mm"].as_f64().unwrap_or(0.0);
    let top = ceiling_z - gap;
    let mut fins = Vec::new();
    for side in [-1.0f64, 1.0] {
        let edge_x = if side > 0.0 { xs.iter().map(|p| p[0]).fold(f64::NEG_INFINITY, f64::max) } else { xs.iter().map(|p| p[0]).fold(f64::INFINITY, f64::min) };
        let on_edge: Vec<&[f64; 2]> = xs.iter().filter(|p| (p[0] - edge_x).abs() < 0.05).collect();
        if on_edge.len() < 2 || (side > 0.0) != (edge_x > (geo.low[0] + geo.high[0]) / 2.0) {
            continue;
        }
        let inset = num(feature, "end_inset_mm").unwrap_or(0.0);
        let y0 = on_edge.iter().map(|p| p[1]).fold(f64::INFINITY, f64::min) + inset;
        let y1 = on_edge.iter().map(|p| p[1]).fold(f64::NEG_INFINITY, f64::max) - inset;
        let (length, segment, release) = (y1 - y0, num(feature, "segment_mm").unwrap_or(1.0), num(feature, "release_gap_mm").unwrap_or(0.0));
        let count = (((length + release) / (segment + release)).round() as i64).max(1);
        let actual = (length - (count - 1) as f64 * release) / count as f64;
        let x_out = edge_x + side * overhang;
        let x_in = x_out - side * width;
        for k in 0..count {
            let a = y0 + k as f64 * (actual + release);
            let mut fin = json!({"side": side, "box_print_mm": [[x_in.min(x_out), a, 0.0], [x_in.max(x_out), a + actual, top]],
                "blocker_print_mm": [[x_in.min(x_out) - 0.2, a - 0.2, top - 0.85], [x_in.max(x_out) + 0.2, a + actual + 0.2, ceiling_z + 0.85]]});
            if let Some(foot_h) = num(feature, "foot_height_mm").filter(|h| *h != 0.0) {
                let foot = (x_out + side * num(feature, "foot_outboard_mm").unwrap_or(0.0), x_in - side * num(feature, "foot_inboard_mm").unwrap_or(0.0));
                fin["foot_print_mm"] = json!([[foot.0.min(foot.1), a, 0.0], [foot.0.max(foot.1), a + actual, foot_h]]);
            }
            fins.push(fin);
        }
    }
    if fins.is_empty() {
        bail!("{}: no exterior ceiling edge found", feature["name"].as_str().unwrap_or(""));
    }
    let mut m = base(feature, "edge_fins");
    m.insert("fins".into(), json!(fins));
    m.insert("reason".into(), feature["reason"].clone());
    Ok(Feature::plain(m))
}

/// The bands a project's layer ranges take from its features: fine layers through each fine
/// band, more walls through each transition, overlapping bands joined.
pub fn layer_ranges(features: &[Feature]) -> Vec<Value> {
    let mut bands: Vec<(f64, f64, f64, i64, String)> = Vec::new();
    for f in features {
        let span = f.record.get("span_print_z_mm").and_then(Value::as_array);
        let name = f.record["name"].as_str().unwrap_or("").to_string();
        match (f.kind(), span) {
            ("fine_band", Some(s)) => {
                let (low, high) = (s[0].as_f64().unwrap(), s[1].as_f64().unwrap());
                let h = f.record["layer_height_mm"].as_f64().unwrap_or(0.08);
                // One fine layer past the top: the slicer ends a range on its last whole layer.
                bands.push(((low - LAYER).max(0.0), high + h, h, 0, name));
            }
            ("transition_band", Some(s)) => {
                let (low, high) = (s[0].as_f64().unwrap(), s[1].as_f64().unwrap());
                bands.push(((low - LAYER).max(0.0), high + 0.1, 0.24, f.record["wall_loops"].as_i64().unwrap_or(6), name));
            }
            _ => {}
        }
    }
    bands.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
    let mut merged: Vec<(f64, f64, f64, i64, String)> = Vec::new();
    for band in bands {
        if let Some(last) = merged.last_mut().filter(|l| band.0 <= l.1) {
            last.1 = last.1.max(band.1);
            last.2 = last.2.min(band.2);
            last.3 = last.3.max(band.3);
            last.4 = format!("{} + {}", last.4, band.4);
        } else {
            merged.push(band);
        }
    }
    merged.into_iter().map(|(lo, hi, h, walls, feature)| {
        let mut options = Map::new();
        options.insert("layer_height".into(), json!(g(h)));
        if walls > 0 {
            options.insert("wall_loops".into(), json!(walls.to_string()));
        }
        json!({"min_z": lo, "max_z": hi, "options": options, "feature": feature})
    }).collect()
}

/// Layer ranges that put a layer top exactly on each face height in `tops`, as (low, high,
/// layer height).
///
/// The schedule starts with the first layer and continues in ordinary layers. A face height off
/// that grid takes equal fine layers from the grid top below it, one step further down when the
/// remainder is under `finest`. Fine ranges within one ordinary layer of each other join at their
/// finest height when their joined span divides evenly by it.
pub fn closing_schedule(tops: &[f64], finest: f64, coarsest_fine: f64) -> Result<Vec<[f64; 3]>> {
    let r4 = |v: f64| (v * 1e4).round() / 1e4;
    let mut targets: Vec<f64> = tops.iter().map(|&t| r4(t)).collect();
    targets.sort_by(|a, b| a.partial_cmp(b).unwrap());
    targets.dedup();
    let (mut ranges, mut level): (Vec<[f64; 3]>, f64) = (Vec::new(), FIRST_LAYER);
    for &top in &targets {
        if top <= level + 1e-6 {
            if (top - level).abs() > 1e-6 {
                bail!("face at {top} mm lies below the scheduled layer top {level} mm");
            }
            continue;
        }
        let steps = ((top - level) / LAYER + 1e-9).floor();
        let mut start = level + steps * LAYER;
        if (top - start).abs() < 1e-6 {
            level = top;
            continue;
        }
        if top - start < finest - 1e-6 {
            start -= LAYER;
        }
        let count = ((top - start) / coarsest_fine - 1e-9).ceil();
        let height = (top - start) / count;
        if height < finest - 1e-6 || start < FIRST_LAYER - 1e-6 {
            bail!("no layer schedule closes {top} mm");
        }
        ranges.push([r4(start), r4(top), r4(height)]);
        level = top;
    }
    let mut joined: Vec<[f64; 3]> = Vec::new();
    for [low, high, height] in ranges {
        if let Some(last) = joined.last_mut() {
            if low - last[1] <= LAYER + 1e-6 {
                let finest_height = height.min(last[2]);
                let start = last[0];
                let even = targets.iter().filter(|&&t| start < t && t <= high + 1e-6)
                    .all(|&t| ((t - start) / finest_height - ((t - start) / finest_height).round()).abs() < 1e-6);
                if even {
                    *last = [start, high, finest_height];
                    continue;
                }
            }
        }
        joined.push([low, high, height]);
    }
    Ok(joined)
}

/// Python's `f"{x:g}"` for the layer heights the ranges name.
pub fn g(x: f64) -> String {
    let s = format!("{}", (x * 1e6).round() / 1e6);
    s
}
