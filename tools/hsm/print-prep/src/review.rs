//! Reading an enclosure preparation back against its record.
//!
//! `check_project` reads the written project: embedded meshes against their STLs, part and
//! modifier counts, painted facets and layer ranges. `review` reads the sliced archive: its
//! integrity and Z trim, fine-layer coverage of each measured round span, layer heights through
//! each transition band, the bead envelope against the bed border, support beads near the painted
//! show faces and inside tie-channel windows and declared support-free interiors, deposition in
//! the solid-host modifiers, optional unbacked-road statistics, the first-to-second layer bead
//! stack, and each object's support topology. Removal lanes for the reported support bodies
//! remain a reading of their positions against the part.
//!
//! A bead is the road's centreline swept by half its width: a capsule. Areas of beads and of
//! sections are measured on a sampling grid; lengths of road outside beads are exact.

use crate::gcode::{self, Road, MODEL, WALLS};
use crate::mesh::Mesh;
use crate::{audit, npz, profile, sha256_hex, xml};
use anyhow::{bail, Context, Result};
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::io::Read;
use std::path::Path;

fn read_json(path: &Path) -> Result<Value> {
    Ok(serde_json::from_slice(&std::fs::read(path).with_context(|| format!("reading {}", path.display()))?)?)
}

fn file_sha(path: &Path) -> Result<String> {
    Ok(sha256_hex(&std::fs::read(path).with_context(|| format!("reading {}", path.display()))?))
}

fn save(path: &Path, value: &Value) -> Result<()> {
    std::fs::write(path, serde_json::to_string_pretty(value)? + "\n")?;
    Ok(())
}

fn vec3(v: &Value) -> [f64; 3] {
    [0, 1, 2].map(|i| v[i].as_f64().unwrap_or(0.0))
}

fn mat3(v: &Value) -> [[f64; 3]; 3] {
    [0, 1, 2].map(|i| vec3(&v[i]))
}

/// Source frame into plate: `R (p - centre) + t`.
fn to_plate(p: [f64; 3], r: &[[f64; 3]; 3], centre: [f64; 3], t: [f64; 3]) -> [f64; 3] {
    let d = [p[0] - centre[0], p[1] - centre[1], p[2] - centre[2]];
    [0, 1, 2].map(|i| r[i][0] * d[0] + r[i][1] * d[1] + r[i][2] * d[2] + t[i])
}

/// Plate into the source frame: `Rᵀ (p - t) + centre`.
fn to_source(p: [f64; 3], r: &[[f64; 3]; 3], centre: [f64; 3], t: [f64; 3]) -> [f64; 3] {
    let d = [p[0] - t[0], p[1] - t[1], p[2] - t[2]];
    [0, 1, 2].map(|i| r[0][i] * d[0] + r[1][i] * d[1] + r[2][i] * d[2] + centre[i])
}

/// Every member of a zip, read whole, so a damaged member fails its check on reading.
fn members(path: &Path) -> Result<BTreeMap<String, Vec<u8>>> {
    let mut archive = zip::ZipArchive::new(std::fs::File::open(path).with_context(|| format!("opening {}", path.display()))?)?;
    let mut out = BTreeMap::new();
    for i in 0..archive.len() {
        let mut entry = archive.by_index(i)?;
        let name = entry.name()?.to_string();
        let mut bytes = Vec::new();
        entry.read_to_end(&mut bytes).with_context(|| format!("{name} in {} is damaged", path.display()))?;
        out.insert(name, bytes);
    }
    Ok(out)
}

/// The values of every `key="…"` attribute in `text`, in order.
fn attribute_values<'a>(text: &'a str, key: &'a str) -> impl Iterator<Item = &'a str> + 'a {
    let needle = format!(" {key}=\"");
    let mut rest = text;
    std::iter::from_fn(move || {
        let at = rest.find(&needle)? + needle.len();
        let end = rest[at..].find('"')? + at;
        let value = &rest[at..end];
        rest = &rest[end..];
        Some(value)
    })
}

/// The vertices and triangles a Bambu object member holds.
fn object_mesh(text: &str) -> (Vec<[f64; 3]>, Vec<[usize; 3]>) {
    let mut vertices = Vec::new();
    for chunk in text.split("<vertex ").skip(1) {
        let end = chunk.find('>').unwrap_or(chunk.len());
        let tag = format!(" {}", &chunk[..end]);
        let get = |k: &str| attribute_values(&tag, k).next().and_then(|v| v.parse::<f64>().ok()).unwrap_or(0.0);
        vertices.push([get("x"), get("y"), get("z")]);
    }
    let mut faces = Vec::new();
    for chunk in text.split("<triangle ").skip(1) {
        let end = chunk.find('>').unwrap_or(chunk.len());
        let tag = format!(" {}", &chunk[..end]);
        let get = |k: &str| attribute_values(&tag, k).next().and_then(|v| v.parse::<usize>().ok()).unwrap_or(0);
        faces.push([get("v1"), get("v2"), get("v3")]);
    }
    (vertices, faces)
}

fn sub(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

/// The distance from `p` to triangle `abc`, by the region of the triangle's plane `p` projects
/// into.
pub fn point_triangle(p: [f64; 3], a: [f64; 3], b: [f64; 3], c: [f64; 3]) -> f64 {
    let (ab, ac, ap) = (sub(b, a), sub(c, a), sub(p, a));
    let (d1, d2) = (dot(ab, ap), dot(ac, ap));
    let near = |q: [f64; 3]| dot(sub(p, q), sub(p, q)).sqrt();
    if d1 <= 0.0 && d2 <= 0.0 {
        return near(a);
    }
    let bp = sub(p, b);
    let (d3, d4) = (dot(ab, bp), dot(ac, bp));
    if d3 >= 0.0 && d4 <= d3 {
        return near(b);
    }
    let vc = d1 * d4 - d3 * d2;
    if vc <= 0.0 && d1 >= 0.0 && d3 <= 0.0 {
        let v = d1 / (d1 - d3);
        return near([a[0] + v * ab[0], a[1] + v * ab[1], a[2] + v * ab[2]]);
    }
    let cp = sub(p, c);
    let (d5, d6) = (dot(ab, cp), dot(ac, cp));
    if d6 >= 0.0 && d5 <= d6 {
        return near(c);
    }
    let vb = d5 * d2 - d1 * d6;
    if vb <= 0.0 && d2 >= 0.0 && d6 <= 0.0 {
        let w = d2 / (d2 - d6);
        return near([a[0] + w * ac[0], a[1] + w * ac[1], a[2] + w * ac[2]]);
    }
    let va = d3 * d6 - d5 * d4;
    if va <= 0.0 && (d4 - d3) >= 0.0 && (d5 - d6) >= 0.0 {
        let w = (d4 - d3) / ((d4 - d3) + (d5 - d6));
        let bc = sub(c, b);
        return near([b[0] + w * bc[0], b[1] + w * bc[1], b[2] + w * bc[2]]);
    }
    let denom = 1.0 / (va + vb + vc);
    let (v, w) = (vb * denom, vc * denom);
    near([a[0] + ab[0] * v + ac[0] * w, a[1] + ab[1] * v + ac[1] * w, a[2] + ab[2] * v + ac[2] * w])
}

/// Triangles binned in a uniform grid, for the nearest surface to a point.
struct Surface<'a> {
    triangles: &'a [[[f64; 3]; 3]],
    cell: f64,
    bins: HashMap<[i64; 3], Vec<usize>>,
}

impl<'a> Surface<'a> {
    fn new(triangles: &'a [[[f64; 3]; 3]], cell: f64) -> Surface<'a> {
        let mut bins: HashMap<[i64; 3], Vec<usize>> = HashMap::new();
        for (i, t) in triangles.iter().enumerate() {
            let lo = [0, 1, 2].map(|k| (t.iter().map(|p| p[k]).fold(f64::INFINITY, f64::min) / cell).floor() as i64);
            let hi = [0, 1, 2].map(|k| (t.iter().map(|p| p[k]).fold(f64::NEG_INFINITY, f64::max) / cell).floor() as i64);
            for x in lo[0]..=hi[0] {
                for y in lo[1]..=hi[1] {
                    for z in lo[2]..=hi[2] {
                        bins.entry([x, y, z]).or_default().push(i);
                    }
                }
            }
        }
        Surface { triangles, cell, bins }
    }

    fn distance(&self, p: [f64; 3]) -> f64 {
        let at = p.map(|v| (v / self.cell).floor() as i64);
        let mut best = f64::INFINITY;
        for reach in 1..64i64 {
            for x in at[0] - reach..=at[0] + reach {
                for y in at[1] - reach..=at[1] + reach {
                    for z in at[2] - reach..=at[2] + reach {
                        let shell = (x - at[0]).abs() == reach || (y - at[1]).abs() == reach || (z - at[2]).abs() == reach;
                        if reach > 1 && !shell {
                            continue;
                        }
                        for &i in self.bins.get(&[x, y, z]).into_iter().flatten() {
                            let t = &self.triangles[i];
                            best = best.min(point_triangle(p, t[0], t[1], t[2]));
                        }
                    }
                }
            }
            if best <= (reach - 1) as f64 * self.cell || best.is_finite() && reach > 2 {
                return best;
            }
        }
        best
    }
}

pub fn check_project(root: &Path, directory: &Path) -> Result<Value> {
    let preparation = read_json(&directory.join("preparation.json"))?;
    let project = root.join(preparation["project"].as_str().context("project")?);
    let matches = Some(file_sha(&project)?.as_str()) == preparation["project_sha256"].as_str();
    let members = members(&project)?;
    let text = |name: &str| -> Result<&str> { Ok(std::str::from_utf8(members.get(name).with_context(|| format!("the project has no {name}"))?)?) };
    let model = xml::parse(text("3D/3dmodel.model")?)?;
    let config = xml::parse(text("Metadata/model_settings.config")?)?;
    let ranges = match members.get("Metadata/layer_config_ranges.xml") {
        Some(bytes) => xml::parse(std::str::from_utf8(bytes)?)?,
        None => xml::Element::default(),
    };
    let settings: Value = serde_json::from_slice(members.get(profile::SETTINGS_MEMBER).context("no settings")?)?;
    let resources = model.child("resources").context("no resources")?;
    let items: HashMap<String, String> = model.child("build").into_iter().flat_map(|b| b.children_named("item"))
        .filter_map(|i| Some((i.attribute("objectid")?.to_string(), i.attribute("transform")?.to_string()))).collect();
    let mut rows = Vec::new();
    for (order, record) in preparation["objects"].as_array().into_iter().flatten().enumerate() {
        let order = order + 1;
        let id = record["object_id"].to_string();
        let owner = resources.children_named("object").find(|o| o.attribute("id") == Some(&id)).with_context(|| format!("no object {id}"))?;
        let main = owner.child("components").and_then(|c| c.children.first()).context("no components")?;
        let member = main.attribute("p:path").context("no component path")?.trim_start_matches('/');
        let body = text(member)?;
        let (vertices, faces) = object_mesh(body);
        let painted = body.matches("paint_supports=\"8\"").count();
        let coded = attribute_values(body, "paint_supports").filter(|v| v.len() >= 2 && v.chars().all(|c| c.is_ascii_hexdigit())).count();
        let t: Vec<f64> = items.get(&id).context("no build item")?.split_whitespace().filter_map(|v| v.parse().ok()).collect();
        let placed: Vec<[f64; 3]> = vertices.iter().map(|v| [0, 1, 2].map(|c| v[0] * t[c] + v[1] * t[3 + c] + v[2] * t[6 + c] + t[9 + c])).collect();
        let stl = root.join(record["stl"].as_str().context("stl")?);
        let source = Mesh::read_stl_exact(&stl)?;
        let (r, centre, translation) = (mat3(&record["build_rotation"]), vec3(&record["source_center_mm"]), vec3(&record["translation_mm"]));
        let mut comparison = "source vertices in order";
        let mut error = if placed.len() == source.vertices.len() {
            placed.iter().zip(&source.vertices).map(|(p, s)| {
                let e = to_plate(*s, &r, centre, translation);
                (0..3).map(|k| (p[k] - e[k]).abs()).fold(0.0, f64::max)
            }).fold(0.0, f64::max)
        } else {
            f64::INFINITY
        };
        if !record["seam_enforcer"].is_null() {
            // A seam strip subdivides existing facets: read its surface independently of the
            // splitter, through the facets' interiors as well as the new vertices.
            let triangles: Vec<[[f64; 3]; 3]> = source.faces.iter().map(|f| f.map(|i| source.vertices[i])).collect();
            let (lo, hi) = crate::mesh::bounds(&source.vertices);
            let diagonal = dot(sub(hi, lo), sub(hi, lo)).sqrt();
            let surface = Surface::new(&triangles, (diagonal / 100.0).max(0.5));
            let native: Vec<[f64; 3]> = vertices.iter().map(|v| [v[0] + centre[0], v[1] + centre[1], v[2] + centre[2]]).collect();
            let centroids = faces.iter().map(|f| [0, 1, 2].map(|k| (native[f[0]][k] + native[f[1]][k] + native[f[2]][k]) / 3.0));
            error = native.iter().copied().chain(centroids).map(|p| surface.distance(p)).fold(0.0, f64::max);
            comparison = "vertices and facet centroids against the source STL surface";
        }
        let object_config = config.children_named("object").find(|o| o.attribute("id") == Some(&id));
        let mut subtypes: BTreeMap<String, usize> = BTreeMap::new();
        for part in object_config.into_iter().flat_map(|o| o.children_named("part")) {
            *subtypes.entry(part.attribute("subtype").unwrap_or("").to_string()).or_default() += 1;
        }
        let order_id = order.to_string();
        let written: Vec<Value> = ranges.children_named("object").filter(|o| o.attribute("id") == Some(&order_id))
            .flat_map(|o| o.children_named("range")).map(|band| {
                let options: Map<String, Value> = band.children_named("option").map(|o| (o.attribute("opt_key").unwrap_or("").to_string(), json!(o.text))).collect();
                json!([band.attribute("min_z").and_then(|v| v.parse::<f64>().ok()), band.attribute("max_z").and_then(|v| v.parse::<f64>().ok()), options])
            }).collect();
        let (lo, hi) = crate::mesh::bounds(&placed);
        rows.push(json!({
            "name": record["name"], "vertices": vertices.len(),
            "source_sha256_matches": Some(file_sha(&stl)?.as_str()) == record["stl_sha256"].as_str(),
            "embedded_vertex_error_mm": if error.is_finite() { json!(error) } else { json!("inf") }, "source_comparison": comparison,
            "seam_painted_facets": body.matches("paint_seam=\"4\"").count(),
            "placed_bounds_mm": [lo, hi], "bed_contact_z_mm": lo[2],
            "blocked_facets": painted, "partially_painted_facets": coded, "parts": subtypes,
            "layer_ranges": written,
            "modifiers_expected": record["modifiers"].as_array().map_or(0, Vec::len),
        }));
    }
    let start = settings["machine_start_gcode"].as_str().unwrap_or("");
    let trims: Vec<&str> = start.match_indices("G29.1 Z{").filter_map(|(at, m)| {
        let rest = &start[at + m.len()..];
        rest.find('}').map(|end| &rest[..end])
    }).collect();
    let pick = |keys: &[&str]| -> Map<String, Value> { keys.iter().map(|k| (k.to_string(), settings.get(*k).cloned().unwrap_or(Value::Null))).collect() };
    let mut problems = Vec::new();
    for row in &rows {
        let name = row["name"].as_str().unwrap_or("");
        if row["source_sha256_matches"] != json!(true) {
            problems.push(format!("{name}: the STL changed after preparation"));
        }
        let error = row["embedded_vertex_error_mm"].as_f64().unwrap_or(f64::INFINITY);
        if error > 1e-4 {
            problems.push(format!("{name}: embedded vertices differ from the STL by {error:.2e} mm"));
        }
        let contact = row["bed_contact_z_mm"].as_f64().unwrap_or(0.0);
        if contact.abs() > 1e-4 {
            problems.push(format!("{name}: the lowest vertex is at Z{contact:.4}"));
        }
        let modifiers = row["parts"]["modifier_part"].as_u64().unwrap_or(0);
        if modifiers != row["modifiers_expected"].as_u64().unwrap_or(0) {
            problems.push(format!("{name}: {modifiers} modifiers for {} declared", row["modifiers_expected"]));
        }
    }
    let pass = matches && problems.is_empty();
    let result = json!({
        "project_sha256_matches": matches, "objects": rows, "z_trim_block": trims,
        "cooling": pick(&["fan_min_speed", "fan_max_speed", "overhang_fan_speed", "overhang_fan_threshold", "additional_cooling_fan_speed"]),
        "support": pick(&["support_type", "support_style", "support_object_xy_distance", "max_bridge_length", "tree_support_branch_diameter",
                          "tree_support_branch_diameter_angle", "brim_type"]),
        "problems": problems, "pass": pass,
    });
    save(&directory.join("project-check.json"), &result)?;
    Ok(result)
}

/// A road's bead: the set within `r` of the segment from `a` to `b`.
#[derive(Clone, Copy)]
struct Capsule {
    a: [f64; 2],
    b: [f64; 2],
    r: f64,
}

impl Capsule {
    fn of(road: &Road) -> Capsule {
        Capsule { a: [road.x0, road.y0], b: [road.x1, road.y1], r: road.width / 2.0 }
    }

    fn bounds(&self) -> ([f64; 2], [f64; 2]) {
        ([self.a[0].min(self.b[0]) - self.r, self.a[1].min(self.b[1]) - self.r],
         [self.a[0].max(self.b[0]) + self.r, self.a[1].max(self.b[1]) + self.r])
    }

    fn contains(&self, p: [f64; 2]) -> bool {
        point_segment_2d(p, self.a, self.b) <= self.r
    }

    /// The span of `p + t (q - p)`, `t` in `[0, 1]`, inside the capsule: a disc at each end and
    /// the band between them. The capsule is convex, so the span is one interval.
    fn span(&self, p: [f64; 2], q: [f64; 2]) -> Option<(f64, f64)> {
        let d = [q[0] - p[0], q[1] - p[1]];
        let mut lo = f64::INFINITY;
        let mut hi = f64::NEG_INFINITY;
        let mut take = |s: Option<(f64, f64)>| {
            if let Some((a, b)) = s {
                lo = lo.min(a);
                hi = hi.max(b);
            }
        };
        for c in [self.a, self.b] {
            let f = [p[0] - c[0], p[1] - c[1]];
            let (qa, qb, qc) = (d[0] * d[0] + d[1] * d[1], 2.0 * (f[0] * d[0] + f[1] * d[1]), f[0] * f[0] + f[1] * f[1] - self.r * self.r);
            if qa == 0.0 {
                if qc <= 0.0 {
                    take(Some((0.0, 1.0)));
                }
                continue;
            }
            let disc = qb * qb - 4.0 * qa * qc;
            if disc >= 0.0 {
                let s = disc.sqrt();
                let (t0, t1) = ((-qb - s) / (2.0 * qa), (-qb + s) / (2.0 * qa));
                if t1 >= 0.0 && t0 <= 1.0 {
                    take(Some((t0.max(0.0), t1.min(1.0))));
                }
            }
        }
        let axis = [self.b[0] - self.a[0], self.b[1] - self.a[1]];
        let length = (axis[0] * axis[0] + axis[1] * axis[1]).sqrt();
        if length > 0.0 {
            let (u, n) = ([axis[0] / length, axis[1] / length], [-axis[1] / length, axis[0] / length]);
            // Clip against `0 ≤ u·(x - a) ≤ length` and `|n·(x - a)| ≤ r`.
            let (mut t0, mut t1) = (0.0f64, 1.0f64);
            let base = [p[0] - self.a[0], p[1] - self.a[1]];
            let mut ok = true;
            for (dir, low, high) in [(u, 0.0, length), (n, -self.r, self.r)] {
                let start = base[0] * dir[0] + base[1] * dir[1];
                let rate = d[0] * dir[0] + d[1] * dir[1];
                if rate.abs() < 1e-15 {
                    if start < low || start > high {
                        ok = false;
                    }
                    continue;
                }
                let (ta, tb) = ((low - start) / rate, (high - start) / rate);
                t0 = t0.max(ta.min(tb));
                t1 = t1.min(ta.max(tb));
            }
            if ok && t0 <= t1 {
                take(Some((t0, t1)));
            }
        }
        (lo <= hi).then_some((lo, hi))
    }
}

fn point_segment_2d(p: [f64; 2], a: [f64; 2], b: [f64; 2]) -> f64 {
    let (dx, dy) = (b[0] - a[0], b[1] - a[1]);
    let l2 = dx * dx + dy * dy;
    let t = if l2 > 0.0 { (((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2).clamp(0.0, 1.0) } else { 0.0 };
    (p[0] - a[0] - t * dx).hypot(p[1] - a[1] - t * dy)
}

/// Whether a bead meets the box `lo..hi` in plan.
fn capsule_meets_box(c: &Capsule, lo: [f64; 2], hi: [f64; 2]) -> bool {
    let inside = |p: [f64; 2]| p[0] >= lo[0] && p[0] <= hi[0] && p[1] >= lo[1] && p[1] <= hi[1];
    if inside(c.a) || inside(c.b) {
        return true;
    }
    let corners = [[lo[0], lo[1]], [hi[0], lo[1]], [hi[0], hi[1]], [lo[0], hi[1]]];
    // The segment crossing a box edge, or coming within the radius of one.
    (0..4).any(|i| {
        let (p, q) = (corners[i], corners[(i + 1) % 4]);
        segments_distance(c.a, c.b, p, q) <= c.r
    })
}

fn segments_distance(a: [f64; 2], b: [f64; 2], c: [f64; 2], d: [f64; 2]) -> f64 {
    let orient = |p: [f64; 2], q: [f64; 2], r: [f64; 2]| (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]);
    let (d1, d2, d3, d4) = (orient(c, d, a), orient(c, d, b), orient(a, b, c), orient(a, b, d));
    if ((d1 > 0.0) != (d2 > 0.0)) && ((d3 > 0.0) != (d4 > 0.0)) {
        return 0.0;
    }
    point_segment_2d(a, c, d).min(point_segment_2d(b, c, d)).min(point_segment_2d(c, a, b)).min(point_segment_2d(d, a, b))
}

/// Beads binned in plan, for the beads near a point or a road.
struct Beads {
    capsules: Vec<Capsule>,
    cell: f64,
    bins: HashMap<(i64, i64), Vec<usize>>,
}

impl Beads {
    fn new(capsules: Vec<Capsule>) -> Beads {
        let cell = 2.0;
        let mut bins: HashMap<(i64, i64), Vec<usize>> = HashMap::new();
        for (i, c) in capsules.iter().enumerate() {
            let (lo, hi) = c.bounds();
            for x in (lo[0] / cell).floor() as i64..=(hi[0] / cell).floor() as i64 {
                for y in (lo[1] / cell).floor() as i64..=(hi[1] / cell).floor() as i64 {
                    bins.entry((x, y)).or_default().push(i);
                }
            }
        }
        Beads { capsules, cell, bins }
    }

    fn near(&self, lo: [f64; 2], hi: [f64; 2]) -> BTreeSet<usize> {
        let mut out = BTreeSet::new();
        for x in (lo[0] / self.cell).floor() as i64..=(hi[0] / self.cell).floor() as i64 {
            for y in (lo[1] / self.cell).floor() as i64..=(hi[1] / self.cell).floor() as i64 {
                out.extend(self.bins.get(&(x, y)).into_iter().flatten().copied());
            }
        }
        out
    }

    fn covers(&self, p: [f64; 2]) -> bool {
        let key = ((p[0] / self.cell).floor() as i64, (p[1] / self.cell).floor() as i64);
        self.bins.get(&key).into_iter().flatten().any(|&i| self.capsules[i].contains(p))
    }

    /// The pieces of the road from `p` to `q` outside every bead, as lengths.
    fn uncovered(&self, p: [f64; 2], q: [f64; 2]) -> Vec<f64> {
        let length = (q[0] - p[0]).hypot(q[1] - p[1]);
        if length == 0.0 {
            return Vec::new();
        }
        let lo = [p[0].min(q[0]), p[1].min(q[1])];
        let hi = [p[0].max(q[0]), p[1].max(q[1])];
        let mut spans: Vec<(f64, f64)> = self.near(lo, hi).into_iter().filter_map(|i| self.capsules[i].span(p, q)).collect();
        spans.sort_by(|a, b| a.partial_cmp(b).unwrap());
        let (mut out, mut cursor) = (Vec::new(), 0.0);
        for (a, b) in spans {
            if a > cursor {
                out.push((a - cursor) * length);
            }
            cursor = f64::max(cursor, b);
        }
        if cursor < 1.0 {
            out.push((1.0 - cursor) * length);
        }
        out.retain(|v| *v > 1e-9);
        out
    }

    /// Lengths of the union of beads along the line at height `y`, between `x0` and `x1`.
    fn runs(&self, y: f64, x0: f64, x1: f64) -> Vec<(f64, f64)> {
        let mut spans: Vec<(f64, f64)> = self.near([x0, y], [x1, y]).into_iter()
            .filter_map(|i| self.capsules[i].span([x0, y], [x1, y]))
            .map(|(a, b)| (x0 + a * (x1 - x0), x0 + b * (x1 - x0))).collect();
        spans.sort_by(|a, b| a.partial_cmp(b).unwrap());
        let mut merged: Vec<(f64, f64)> = Vec::new();
        for (a, b) in spans {
            match merged.last_mut() {
                Some(last) if a <= last.1 => last.1 = last.1.max(b),
                _ => merged.push((a, b)),
            }
        }
        merged
    }

    fn extent(&self) -> Option<([f64; 2], [f64; 2])> {
        let mut lo = [f64::INFINITY; 2];
        let mut hi = [f64::NEG_INFINITY; 2];
        for c in &self.capsules {
            let (a, b) = c.bounds();
            lo = [lo[0].min(a[0]), lo[1].min(a[1])];
            hi = [hi[0].max(b[0]), hi[1].max(b[1])];
        }
        (lo[0] <= hi[0]).then_some((lo, hi))
    }
}

fn run_length(runs: &[(f64, f64)]) -> f64 {
    runs.iter().map(|(a, b)| b - a).sum()
}

fn overlap(a: &[(f64, f64)], b: &[(f64, f64)]) -> f64 {
    let (mut i, mut j, mut total) = (0, 0, 0.0);
    while i < a.len() && j < b.len() {
        let (lo, hi) = (a[i].0.max(b[j].0), a[i].1.min(b[j].1));
        if hi > lo {
            total += hi - lo;
        }
        if a[i].1 < b[j].1 { i += 1 } else { j += 1 }
    }
    total
}

/// Scanline spacing for bead areas.
const SCAN: f64 = 0.02;

/// A cross-section at height `z`: its boundary segments, read by even-odd crossings. A plane
/// through mesh vertices is read just above them, where the count cannot take a hole's loop for
/// the section.
struct Section {
    segments: Vec<[[f64; 2]; 2]>,
    row: f64,
    rows: HashMap<i64, Vec<usize>>,
}

impl Section {
    fn new(triangles: &[[[f64; 3]; 3]], z: f64) -> Section {
        let z = if triangles.iter().any(|t| t.iter().any(|p| (p[2] - z).abs() < 1e-7)) { z + 1e-5 } else { z };
        let mut segments = Vec::new();
        for t in triangles {
            let mut points = Vec::new();
            for k in 0..3 {
                let (p, q) = (t[k], t[(k + 1) % 3]);
                if (p[2] > z) != (q[2] > z) {
                    let f = (z - p[2]) / (q[2] - p[2]);
                    points.push([p[0] + f * (q[0] - p[0]), p[1] + f * (q[1] - p[1])]);
                }
            }
            if points.len() == 2 {
                segments.push([points[0], points[1]]);
            }
        }
        let row = 0.5;
        let mut rows: HashMap<i64, Vec<usize>> = HashMap::new();
        for (i, s) in segments.iter().enumerate() {
            let (lo, hi) = (s[0][1].min(s[1][1]), s[0][1].max(s[1][1]));
            for r in (lo / row).floor() as i64..=(hi / row).floor() as i64 {
                rows.entry(r).or_default().push(i);
            }
        }
        Section { segments, row, rows }
    }

    fn contains(&self, p: [f64; 2]) -> bool {
        let mut inside = false;
        for &i in self.rows.get(&((p[1] / self.row).floor() as i64)).into_iter().flatten() {
            let [a, b] = self.segments[i];
            if (a[1] > p[1]) != (b[1] > p[1]) {
                let x = a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1]);
                if x > p[0] {
                    inside = !inside;
                }
            }
        }
        inside
    }

    /// Whether any boundary lies within `r` of `p`.
    fn within(&self, p: [f64; 2], r: f64) -> bool {
        let (lo, hi) = (((p[1] - r) / self.row).floor() as i64, ((p[1] + r) / self.row).floor() as i64);
        (lo..=hi).any(|row| self.rows.get(&row).into_iter().flatten().any(|&i| {
            let [a, b] = self.segments[i];
            point_segment_2d(p, a, b) < r
        }))
    }

    fn bounds(&self) -> Option<([f64; 2], [f64; 2])> {
        let mut lo = [f64::INFINITY; 2];
        let mut hi = [f64::NEG_INFINITY; 2];
        for s in &self.segments {
            for p in s {
                lo = [lo[0].min(p[0]), lo[1].min(p[1])];
                hi = [hi[0].max(p[0]), hi[1].max(p[1])];
            }
        }
        (lo[0] <= hi[0]).then_some((lo, hi))
    }
}

fn box_triangles(lo: [f64; 3], hi: [f64; 3]) -> Vec<[[f64; 3]; 3]> {
    let ([x0, y0, z0], [x1, y1, z1]) = (lo, hi);
    let v = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]];
    [[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]]
        .iter().map(|f: &[usize; 3]| f.map(|i| v[i])).collect()
}

/// Whether a support road lies inside the named passage, its solid bounding-box corners aside.
fn support_in_void(road: &Road, z: f64, height: f64, region: &Value, record: &Value) -> Result<bool> {
    let (x0, y0, x1, y1, width) = (road.x0, road.y0, road.x1, road.y1, road.width);
    let length = (x1 - x0).hypot(y1 - y0);
    let n = ((length / 0.15).ceil() as usize + 1).max(2);
    let normal = if length > 0.0 { [-(y1 - y0) / length, (x1 - x0) / length] } else { [1.0, 0.0] };
    let (r, centre, t) = (mat3(&record["build_rotation"]), vec3(&record["source_center_mm"]), vec3(&record["translation_mm"]));
    let mut source = Vec::new();
    for level in [z - height + 0.02, z - height / 2.0, z - 0.02] {
        for offset in [-width / 2.0, 0.0, width / 2.0] {
            for i in 0..n {
                let f = i as f64 / (n - 1) as f64;
                let p = [x0 + (x1 - x0) * f + normal[0] * offset, y0 + (y1 - y0) * f + normal[1] * offset, level];
                source.push(to_source(p, &r, centre, t));
            }
        }
    }
    let shape = &region["void_source"];
    if shape.is_null() {
        let b: Vec<f64> = region["bounds_source_mm"].as_array().context("passage bounds")?.iter().filter_map(Value::as_f64).collect();
        return Ok(source.iter().any(|p| (0..3).all(|k| p[k] > b[2 * k] + 0.02 && p[k] < b[2 * k + 1] - 0.02)));
    }
    let span = |key: &str| -> (f64, f64) {
        let s: Vec<f64> = shape[key].as_array().into_iter().flatten().filter_map(Value::as_f64).collect();
        (s[0].min(s[1]), s[0].max(s[1]))
    };
    match shape["kind"].as_str() {
        Some("teardrop_y") => {
            let c = [shape["centre_xz_mm"][0].as_f64().unwrap_or(0.0), shape["centre_xz_mm"][1].as_f64().unwrap_or(0.0)];
            let radius = shape["radius_mm"].as_f64().unwrap_or(0.0);
            let angle = shape["roof_angle_deg"].as_f64().unwrap_or(45.0).to_radians();
            let apex = radius / angle.cos();
            let (low, high) = span("span_y_mm");
            Ok(source.iter().any(|p| {
                let (dx, rise) = (p[0] - c[0], c[1] - p[2]);
                let round = dx * dx + rise * rise < (radius - 0.02).powi(2);
                let roof = rise >= radius * angle.cos() && rise < apex - 0.02 && dx.abs() < (apex - rise) / angle.tan() - 0.02;
                (round || roof) && p[1] > low + 0.02 && p[1] < high - 0.02
            }))
        }
        Some("cylinder") => {
            let (a, b) = (vec3(&shape["start_mm"]), vec3(&shape["end_mm"]));
            let axis = sub(b, a);
            let radius = shape["radius_mm"].as_f64().unwrap_or(0.0);
            Ok(source.iter().any(|p| {
                let along = dot(sub(*p, a), axis) / dot(axis, axis);
                let radial = sub(sub(*p, a), axis.map(|v| v * along));
                along > 0.0 && along < 1.0 && dot(radial, radial) < (radius - 0.02).powi(2)
            }))
        }
        Some("prism_y") => {
            let profile: Vec<[f64; 2]> = shape["profile_xz_mm"].as_array().context("prism profile")?.iter()
                .map(|p| [p[0].as_f64().unwrap_or(0.0), p[1].as_f64().unwrap_or(0.0)]).collect();
            let (low, high) = span("span_y_mm");
            let inside = |q: [f64; 2]| {
                let mut odd = false;
                for i in 0..profile.len() {
                    let (a, b) = (profile[i], profile[(i + 1) % profile.len()]);
                    if (a[1] > q[1]) != (b[1] > q[1]) && a[0] + (q[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1]) > q[0] {
                        odd = !odd;
                    }
                }
                // The profile less a skin, as the passage's own surface.
                odd && (0..profile.len()).all(|i| point_segment_2d(q, profile[i], profile[(i + 1) % profile.len()]) > 0.02)
            };
            Ok(source.iter().any(|p| inside([p[0], p[2]]) && p[1] > low + 0.02 && p[1] < high - 0.02))
        }
        other => bail!("unknown support-free passage: {other:?}"),
    }
}

/// Wall layers an object prints: each layer's top and height where its walls extrude.
fn wall_layers(gcode: &[u8], object: i64) -> Vec<(f64, f64)> {
    let mut layers: BTreeSet<(u64, u64)> = BTreeSet::new();
    let (mut z, mut height, mut current, mut feature): (Option<f64>, Option<f64>, Option<i64>, String) = (None, None, None, String::new());
    let r6 = |v: f64| (v * 1e6).round() / 1e6;
    for raw in gcode.split(|b| *b == b'\n') {
        let line = String::from_utf8_lossy(raw);
        if let Some(v) = line.strip_prefix("; Z_HEIGHT:") {
            z = v.trim().parse().ok();
            height = None;
            current = None;
        } else if let Some(v) = line.strip_prefix("; LAYER_HEIGHT:") {
            height = v.trim().parse().ok();
        } else if let Some(v) = line.strip_prefix("; OBJECT_ID:") {
            current = v.trim().parse().ok();
        } else if let Some(v) = line.strip_prefix("; FEATURE:") {
            feature = v.trim().to_string();
        } else if (line.starts_with("G1 ") || line.starts_with("G2 ") || line.starts_with("G3 ")) && current == Some(object) && WALLS.contains(&feature.as_str()) {
            let (Some(z), Some(h)) = (z, height) else { continue };
            let code = line.split(';').next().unwrap_or("");
            let mut tokens = code.split_whitespace().skip(1);
            let moves = code.split_whitespace().skip(1).any(|w| (w.starts_with('X') || w.starts_with('Y')) && w.len() > 1);
            let extrusion = tokens.find_map(|w| w.strip_prefix('E')).and_then(|v| v.parse::<f64>().ok());
            if moves && extrusion.is_some_and(|e| e > 0.0) {
                layers.insert((r6(z).to_bits(), r6(h).to_bits()));
            }
        }
    }
    let mut out: Vec<(f64, f64)> = layers.into_iter().map(|(a, b)| (f64::from_bits(a), f64::from_bits(b))).collect();
    out.sort_by(|a, b| a.partial_cmp(b).unwrap());
    out
}

fn check_span(layers: &[(f64, f64)], name: &Value, low: f64, high: f64, target: f64, tolerance: f64, bed: Option<f64>) -> Value {
    let hits: Vec<(f64, f64)> = layers.iter().copied().filter(|&(z, h)| z > low && z - h < high).collect();
    let accepted = |z: f64, h: f64| (h - target).abs() <= tolerance || bed.is_some_and(|b| (z - h).abs() <= tolerance && (h - b).abs() <= tolerance);
    let bad: Vec<Value> = hits.iter().filter(|&&(z, h)| !accepted(z, h)).map(|&(z, h)| json!({"z_mm": z, "height_mm": h})).collect();
    let mut coverage: Vec<(f64, f64)> = hits.iter().filter(|&&(z, h)| accepted(z, h)).map(|&(z, h)| (low.max(z - h), high.min(z))).collect();
    coverage.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let r6 = |v: f64| (v * 1e6).round() / 1e6;
    let (mut cursor, mut gaps) = (low, Vec::new());
    for (start, end) in coverage {
        if start - cursor > 0.02 {
            gaps.push(json!([r6(cursor), r6(start)]));
        }
        cursor = cursor.max(end);
    }
    if high - cursor > 0.02 {
        gaps.push(json!([r6(cursor), r6(high)]));
    }
    json!({"name": name, "print_z_mm": [low, high], "wall_layer_count": hits.len(),
           "first_wall_layer": hits.first().map(|h| json!([h.0, h.1])), "last_wall_layer": hits.last().map(|h| json!([h.0, h.1])),
           "declared_bed_layer_height_mm": bed, "wrong_height_layers": bad, "uncovered_intervals_mm": gaps,
           "pass": !hits.is_empty() && bad.is_empty() && gaps.is_empty()})
}

/// Solid-host infill inside each posed modifier: the share of its section an object's model
/// beads cover, through the infill core a bead radius inside the section's edge, and through the
/// whole section.
fn dense_regions(root: &Path, preparation: &Value, gcode: &[u8]) -> Result<Vec<Value>> {
    struct Row { object: i64, record: usize, modifier: usize, samples: Vec<Value> }
    let objects = preparation["objects"].as_array().cloned().unwrap_or_default();
    let mut meshes: HashMap<i64, Vec<[[f64; 3]; 3]>> = HashMap::new();
    let mut rows: Vec<Row> = Vec::new();
    let mut wanted: BTreeMap<i64, Vec<usize>> = BTreeMap::new();
    let key = |z: f64| (z * 1000.0).round() as i64;
    for (ri, record) in objects.iter().enumerate() {
        let modifiers = record["modifiers"].as_array().cloned().unwrap_or_default();
        if modifiers.is_empty() {
            continue;
        }
        let oid = record["identify_id"].as_i64().unwrap_or(0);
        let stl = crate::mesh::stl_corners(&std::fs::read(root.join(record["stl"].as_str().unwrap_or("")))?)?;
        let (r, centre, t) = (mat3(&record["build_rotation"]), vec3(&record["source_center_mm"]), vec3(&record["translation_mm"]));
        let placed: Vec<[f64; 3]> = stl.iter().map(|p| to_plate(p.map(|v| v as f32 as f64), &r, centre, t)).collect();
        meshes.insert(oid, placed.chunks(3).map(|c| [c[0], c[1], c[2]]).collect());
        for (mi, modifier) in modifiers.iter().enumerate() {
            let (lo, hi) = (vec3(&modifier["plate_bounds_mm"][0]), vec3(&modifier["plate_bounds_mm"][1]));
            let samples: BTreeSet<i64> = [lo[2] + 0.36, (lo[2] + hi[2]) / 2.0, hi[2] - 0.36].iter().map(|&z| key(z)).collect();
            rows.push(Row { object: oid, record: ri, modifier: mi, samples: Vec::new() });
            for z in samples {
                let zf = z as f64 / 1000.0;
                if lo[2] < zf && zf < hi[2] {
                    wanted.entry(z).or_default().push(rows.len() - 1);
                }
            }
        }
    }
    if rows.is_empty() {
        return Ok(Vec::new());
    }
    let mut stop = false;
    gcode::layers(gcode, |layer| {
        if stop || wanted.is_empty() {
            stop = true;
            return;
        }
        let mid = layer.z - layer.height / 2.0;
        let hits: Vec<i64> = wanted.keys().copied().filter(|&t| {
            let tf = t as f64 / 1000.0;
            mid - layer.height / 2.0 < tf && tf <= mid + layer.height / 2.0
        }).collect();
        if hits.is_empty() {
            return;
        }
        // Tree supports print on their own layer heights between the objects' layers; a sample
        // waits for a layer on which its object prints.
        let printed: BTreeSet<i64> = layer.roads.iter().filter(|r| MODEL.contains(&&*r.feature)).filter_map(|r| r.object).collect();
        let mut sections: HashMap<i64, Section> = HashMap::new();
        for target in hits {
            let mut waiting = Vec::new();
            for index in wanted.remove(&target).unwrap_or_default() {
                let oid = rows[index].object;
                if !printed.contains(&oid) {
                    waiting.push(index);
                    continue;
                }
                let record = &objects[rows[index].record];
                let modifier = &record["modifiers"][rows[index].modifier];
                let section = sections.entry(oid).or_insert_with(|| Section::new(&meshes[&oid], mid));
                let (r, centre, t) = (mat3(&record["build_rotation"]), vec3(&record["source_center_mm"]), vec3(&record["translation_mm"]));
                let (blo, bhi) = (vec3(&modifier["source_bounds_mm"][0]), vec3(&modifier["source_bounds_mm"][1]));
                let corners: Vec<[[f64; 3]; 3]> = box_triangles(blo, bhi).iter().map(|tri| tri.map(|p| to_plate(p, &r, centre, t))).collect();
                let host = Section::new(&corners, mid);
                let own: Vec<Capsule> = layer.roads.iter().filter(|r| r.object == Some(oid) && MODEL.contains(&&*r.feature)).map(Capsule::of).collect();
                let reach = own.iter().map(|c| c.r).fold(0.0, f64::max);
                let Some((hlo, hhi)) = host.bounds() else { continue };
                let nearby: Vec<Capsule> = own.iter().copied().filter(|c| {
                    let (a, b) = c.bounds();
                    a[0] <= hhi[0] + reach && b[0] >= hlo[0] - reach && a[1] <= hhi[1] + reach && b[1] >= hlo[1] - reach
                }).collect();
                let radius = if nearby.is_empty() { reach } else { nearby.iter().map(|c| c.r).fold(0.0, f64::max) };
                let beads = Beads::new(nearby);
                let area = (hhi[0] - hlo[0]) * (hhi[1] - hlo[1]);
                let step = (area / 250_000.0).sqrt().max(0.05);
                let (mut stock, mut core, mut stock_covered, mut core_covered) = (0usize, 0usize, 0usize, 0usize);
                let mut y = hlo[1] + step / 2.0;
                while y < hhi[1] {
                    let mut x = hlo[0] + step / 2.0;
                    while x < hhi[0] {
                        let p = [x, y];
                        if host.contains(p) && section.contains(p) {
                            stock += 1;
                            let covered = beads.covers(p);
                            stock_covered += covered as usize;
                            if !host.within(p, radius) && !section.within(p, radius) {
                                core += 1;
                                core_covered += covered as usize;
                            }
                        }
                        x += step;
                    }
                    y += step;
                }
                let cell = step * step;
                let (stock_area, core_area) = (stock as f64 * cell, core as f64 * cell);
                if stock_area <= 0.05 {
                    continue;
                }
                rows[index].samples.push(json!({"print_z_mm": layer.z,
                    "coverage": (core_area > 0.05).then(|| core_covered as f64 / core as f64),
                    "outline_coverage": stock_covered as f64 / stock as f64, "stock_mm2": stock_area,
                    "infill_core_mm2": core_area, "bead_radius_inset_mm": radius, "sampling_step_mm": step}));
            }
            if !waiting.is_empty() {
                wanted.insert(target, waiting);
            }
        }
    });
    Ok(rows.into_iter().map(|row| {
        let record = &objects[row.record];
        let modifier = &record["modifiers"][row.modifier];
        let coverage: Vec<f64> = row.samples.iter().filter_map(|s| s["coverage"].as_f64()).collect();
        let outline: Vec<f64> = row.samples.iter().filter_map(|s| s["outline_coverage"].as_f64()).collect();
        json!({"object": row.object, "name": modifier["name"], "plate_bounds_mm": modifier["plate_bounds_mm"],
               "source_bounds_mm": modifier["source_bounds_mm"], "samples": row.samples,
               "minimum_coverage": coverage.iter().copied().fold(None, |m: Option<f64>, v| Some(m.map_or(v, |m| m.min(v)))),
               "minimum_outline_coverage": outline.iter().copied().fold(None, |m: Option<f64>, v| Some(m.map_or(v, |m| m.min(v))))})
    }).collect())
}

/// The plate-to-CAD transform of one object's record, as a 3MF row-vector transform.
fn plate_to_cad(record: &Value) -> audit::Transform {
    let (r, centre, t) = (mat3(&record["build_rotation"]), vec3(&record["source_center_mm"]), vec3(&record["translation_mm"]));
    // cad = Rᵀ (plate - t) + centre; as a row vector, plate · R + (centre - Rᵀ t).
    let mut out = [0.0; 12];
    for row in 0..3 {
        for col in 0..3 {
            out[row * 3 + col] = r[row][col];
        }
    }
    for i in 0..3 {
        out[9 + i] = centre[i] - (r[0][i] * t[0] + r[1][i] * t[1] + r[2][i] * t[2]);
    }
    out
}

pub fn review(root: &Path, directory: &Path, audit_supports: bool, unbacked: bool) -> Result<Value> {
    let preparation = read_json(&directory.join("preparation.json"))?;
    let archive = root.join(preparation["archive"].as_str().context("the preparation is not sliced")?);
    if Some(file_sha(&archive)?.as_str()) != preparation["archive_sha256"].as_str() {
        bail!("the sliced archive changed after slicing");
    }
    let project_check = check_project(root, directory)?;
    let project = root.join(preparation["project"].as_str().context("project")?);
    let settings: Value = {
        let mut zip = zip::ZipArchive::new(std::fs::File::open(&project)?)?;
        let mut text = Vec::new();
        zip.by_name(profile::SETTINGS_MEMBER)?.read_to_end(&mut text)?;
        serde_json::from_slice(&text)?
    };
    let bed_layer_height: Option<f64> = settings["initial_layer_print_height"].as_str().and_then(|v| v.parse().ok());
    let gcode = gcode::plate_gcode(&archive)?;
    let md5 = {
        let mut zip = zip::ZipArchive::new(std::fs::File::open(&archive)?)?;
        let mut text = String::new();
        zip.by_name("Metadata/plate_1.gcode.md5")?.read_to_string(&mut text)?;
        text.trim().to_lowercase()
    };
    let integrity = crate::ids::md5_hex(&gcode) == md5;
    let head = String::from_utf8_lossy(&gcode[..gcode.len().min(400_000)]).to_string();
    let trims: Vec<f64> = head.lines().filter_map(|l| l.trim_start().strip_prefix("G29.1 Z"))
        .filter_map(|v| v.split(|c: char| !(c.is_ascii_digit() || c == '.' || c == '-' || c == '+')).next()?.parse().ok()).collect();
    let records = preparation["objects"].as_array().cloned().unwrap_or_default();
    let objects: BTreeMap<i64, &Value> = records.iter().map(|r| (r["identify_id"].as_i64().unwrap_or(0), r)).collect();
    let border = preparation["plate_border_mm"].as_f64().unwrap_or(20.0);
    let area: Vec<Vec<f64>> = serde_json::from_value(preparation["usable_plate_mm"].clone())?;
    let show = npz::read_arrays(&root.join(preparation["show_faces"].as_str().context("show faces")?))?;
    let mut show_faces: HashMap<i64, Vec<[[f64; 3]; 3]>> = HashMap::new();
    for (key, array) in &show {
        let values = array.f64().context("show faces")?;
        show_faces.insert(key.parse()?, values.chunks(9).map(|c| [[c[0], c[1], c[2]], [c[3], c[4], c[5]], [c[6], c[7], c[8]]]).collect());
    }
    // Painted faces binned in plan.
    const SHOW_CELL: f64 = 4.0;
    let mut grid: HashMap<(i64, i64), Vec<(i64, usize)>> = HashMap::new();
    for (oid, triangles) in &show_faces {
        for (index, t) in triangles.iter().enumerate() {
            let lo = [0, 1].map(|k| (t.iter().map(|p| p[k]).fold(f64::INFINITY, f64::min) / SHOW_CELL).floor() as i64);
            let hi = [0, 1].map(|k| (t.iter().map(|p| p[k]).fold(f64::NEG_INFINITY, f64::max) / SHOW_CELL).floor() as i64);
            for gx in lo[0]..=hi[0] {
                for gy in lo[1]..=hi[1] {
                    grid.entry((gx, gy)).or_default().push((*oid, index));
                }
            }
        }
    }
    let windows: Vec<(i64, &Value)> = objects.iter().flat_map(|(o, r)| r["tie_windows"].as_array().into_iter().flatten().map(move |w| (*o, w))).collect();
    let excluded: Vec<(i64, &Value)> = objects.iter().flat_map(|(o, r)| r["support_free_regions"].as_array().into_iter().flatten().map(move |w| (*o, w))).collect();
    let fine: Vec<(i64, &Value)> = objects.iter().flat_map(|(o, r)| r["verify_spans"].as_array().into_iter().flatten().map(move |s| (*o, s))).collect();
    let span = |s: &Value| (s["print_z_mm"][0].as_f64().unwrap_or(0.0), s["print_z_mm"][1].as_f64().unwrap_or(0.0));
    let mut layers_seen = 0usize;
    let (mut bead_low, mut bead_high) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
    let mut support_roads = 0usize;
    let mut show_min: Option<f64> = None;
    let (mut show_contacts, mut window_crossings, mut excluded_support) = (Vec::new(), Vec::new(), Vec::new());
    let mut unbacked_rows: BTreeMap<(i64, String), [f64; 5]> = BTreeMap::new();
    let mut previous: Option<Beads> = None;
    let mut first_two: BTreeMap<i64, Vec<(Beads, Vec<Capsule>)>> = BTreeMap::new();
    let mut problem: Option<anyhow::Error> = None;
    gcode::layers(&gcode, |layer| {
        layers_seen += 1;
        let (z, height) = (layer.z, layer.height);
        if layer.roads.is_empty() {
            previous = None;
            return;
        }
        let reach = layer.roads.iter().map(|r| r.width).fold(0.0, f64::max) / 2.0;
        for road in &layer.roads {
            bead_low = [bead_low[0].min(road.x0.min(road.x1) - reach), bead_low[1].min(road.y0.min(road.y1) - reach)];
            bead_high = [bead_high[0].max(road.x0.max(road.x1) + reach), bead_high[1].max(road.y0.max(road.y1) + reach)];
        }
        let road_json = |r: &Road| json!([r.x0, r.y0, r.x1, r.y1, r.width]);
        for road in layer.roads.iter().filter(|r| r.is_support()) {
            support_roads += 1;
            let radius = road.width.hypot(height) / 2.0;
            let mut cells: BTreeSet<(i64, usize)> = BTreeSet::new();
            for gx in (road.x0.min(road.x1) / SHOW_CELL).floor() as i64..=(road.x0.max(road.x1) / SHOW_CELL).floor() as i64 {
                for gy in (road.y0.min(road.y1) / SHOW_CELL).floor() as i64..=(road.y0.max(road.y1) / SHOW_CELL).floor() as i64 {
                    cells.extend(grid.get(&(gx, gy)).into_iter().flatten().copied());
                }
            }
            let near: Vec<&[[f64; 3]; 3]> = cells.iter().map(|(o, i)| &show_faces[o][*i])
                .filter(|t| t.iter().map(|p| p[2]).fold(f64::INFINITY, f64::min) <= z + radius && t.iter().map(|p| p[2]).fold(f64::NEG_INFINITY, f64::max) >= z - height - radius)
                .collect();
            if !near.is_empty() {
                let length = (road.x1 - road.x0).hypot(road.y1 - road.y0);
                let n = ((length / 0.2) as usize + 1).max(2);
                let mut clearance = f64::INFINITY;
                for i in 0..n {
                    let f = i as f64 / (n - 1) as f64;
                    let p = [road.x0 + (road.x1 - road.x0) * f, road.y0 + (road.y1 - road.y0) * f, z - height / 2.0];
                    for t in &near {
                        clearance = clearance.min(point_triangle(p, t[0], t[1], t[2]));
                    }
                }
                let clearance = clearance - radius;
                if show_min.is_none_or(|m| clearance < m) {
                    show_min = Some(clearance);
                }
                if clearance <= 0.0 && show_contacts.len() < 200 {
                    show_contacts.push(json!({"z_mm": z, "road": road_json(road), "feature": &*road.feature, "bead_clearance_mm": clearance}));
                }
            }
            let bead = Capsule::of(road);
            for (oid, region) in &excluded {
                let (lo, hi) = (vec3(&region["box_plate_mm"][0]), vec3(&region["box_plate_mm"][1]));
                if z - height < hi[2] - 0.02 && z > lo[2] + 0.02 && capsule_meets_box(&bead, [lo[0] + 0.02, lo[1] + 0.02], [hi[0] - 0.02, hi[1] - 0.02]) {
                    match support_in_void(road, z, height, region, objects[oid]) {
                        Ok(true) => excluded_support.push(json!({"object": oid, "name": region["name"], "z_mm": z, "road": road_json(road), "feature": &*road.feature})),
                        Ok(false) => {}
                        Err(e) => { problem.get_or_insert(e); }
                    }
                }
            }
            for (oid, window) in &windows {
                let (lo, hi) = (vec3(&window["box_plate_mm"][0]), vec3(&window["box_plate_mm"][1]));
                if z - height < hi[2] - 0.02 && z > lo[2] + 0.02 && capsule_meets_box(&bead, [lo[0] + 0.02, lo[1] + 0.02], [hi[0] - 0.02, hi[1] - 0.02]) {
                    window_crossings.push(json!({"object": oid, "z_mm": z, "window": window["box_plate_mm"], "road": road_json(road), "feature": &*road.feature}));
                }
            }
        }
        let mid = z - height / 2.0;
        let needs = layers_seen <= 2 || unbacked && fine.iter().any(|(_, s)| { let (a, b) = span(s); a - 0.5 <= mid && mid <= b + 0.08 });
        if !needs {
            previous = None;
            return;
        }
        if layers_seen <= 2 {
            for oid in objects.keys() {
                let own: Vec<&Road> = layer.roads.iter().filter(|r| r.object == Some(*oid)).collect();
                let beads = Beads::new(own.iter().map(|r| Capsule::of(r)).collect());
                let model: Vec<Capsule> = own.iter().filter(|r| MODEL.contains(&&*r.feature)).map(|r| Capsule::of(r)).collect();
                first_two.entry(*oid).or_default().push((beads, model));
            }
        }
        if unbacked {
            for (oid, s) in &fine {
                let (a, b) = span(s);
                let Some(below) = &previous else { continue };
                if !(a <= mid && mid <= b + 0.08) {
                    continue;
                }
                let own: Vec<&Road> = layer.roads.iter().filter(|r| r.object == Some(*oid) && MODEL.contains(&&*r.feature)).collect();
                if own.is_empty() {
                    continue;
                }
                let entry = unbacked_rows.entry((*oid, s["name"].as_str().unwrap_or("").to_string())).or_insert([0.0; 5]);
                entry[4] += 1.0;
                for road in own {
                    let free = below.uncovered([road.x0, road.y0], [road.x1, road.y1]);
                    entry[0] += 1.0;
                    let total: f64 = free.iter().sum();
                    if total > 1e-6 {
                        if &*road.feature == "Bridge" {
                            entry[3] += total;
                        } else {
                            entry[1] += total;
                            entry[2] = entry[2].max(free.iter().copied().fold(0.0, f64::max));
                        }
                    }
                }
            }
        }
        previous = Some(Beads::new(layer.roads.iter().map(Capsule::of).collect()));
    });
    if let Some(e) = problem {
        return Err(e);
    }
    let margins = json!({"left": bead_low[0] - area[0][0], "front": bead_low[1] - area[0][1], "right": area[1][0] - bead_high[0], "back": area[1][1] - bead_high[1]});
    let minimum = margins.as_object().unwrap().values().filter_map(Value::as_f64).fold(f64::INFINITY, f64::min);
    let mut stack = Map::new();
    for (oid, rows) in &first_two {
        if rows.len() < 2 || rows[0].0.capsules.is_empty() || rows[1].1.is_empty() {
            continue;
        }
        let (first, second) = (&rows[0].0, Beads::new(rows[1].1.clone()));
        let Some((lo, hi)) = second.extent() else { continue };
        let (mut second_area, mut shared) = (0.0, 0.0);
        let mut y = lo[1] + SCAN / 2.0;
        while y < hi[1] {
            let runs = second.runs(y, lo[0] - 1.0, hi[0] + 1.0);
            second_area += run_length(&runs) * SCAN;
            shared += overlap(&runs, &first.runs(y, lo[0] - 1.0, hi[0] + 1.0)) * SCAN;
            y += SCAN;
        }
        // + 0.0: an empty sum is -0.0.
        let outside: f64 = rows[1].1.iter().map(|c| first.uncovered(c.a, c.b).iter().sum::<f64>()).sum::<f64>() + 0.0;
        stack.insert(oid.to_string(), json!({"second_layer_model_bead_area_mm2": second_area,
            "fraction_over_first_layer": if second_area > 0.0 { shared / second_area } else { 0.0 },
            "second_layer_centerline_outside_first_mm": outside}));
    }
    let mut band_results = Vec::new();
    for (oid, record) in &objects {
        let walls = wall_layers(&gcode, *oid);
        for s in record["verify_spans"].as_array().into_iter().flatten() {
            let (a, b) = span(s);
            let mut row = check_span(&walls, &s["name"], a, b, s["layer_height_mm"].as_f64().unwrap_or(0.08), 0.001, bed_layer_height);
            row["object"] = json!(oid);
            band_results.push(row);
        }
        for range in record["ranges"].as_array().into_iter().flatten() {
            if range["options"].get("wall_loops").is_none() {
                continue;
            }
            let (lo, hi) = (range["min_z"].as_f64().unwrap_or(0.0), range["max_z"].as_f64().unwrap_or(0.0));
            let inside: Vec<(f64, f64)> = walls.iter().copied().filter(|&(z, _)| lo < z && z <= hi).collect();
            let heights: BTreeSet<u64> = inside.iter().map(|(_, h)| h.to_bits()).collect();
            band_results.push(json!({"object": oid, "name": range["feature"], "transition_band_mm": [lo, hi],
                "emitted_wall_layer_heights_mm": heights.into_iter().map(f64::from_bits).collect::<Vec<_>>(),
                "pass": inside.iter().all(|&(z, h)| (h - 0.24).abs() < 0.001 || (z - 0.2).abs() < 0.001)}));
        }
    }
    let dense = dense_regions(root, &preparation, &gcode)?;
    let mut audits = Map::new();
    if audit_supports {
        for (oid, record) in &objects {
            let stl = root.join(record["stl"].as_str().unwrap_or(""));
            let options = audit::Options {
                piece: record["name"].as_str().unwrap_or("").to_string(), object: Some(*oid), include_unlabelled: true,
                cad_transform: Some(plate_to_cad(record)), bed_reseat: None,
                inputs: json!({"gcode": format!("{} plate_1.gcode, object {oid}", preparation["archive"].as_str().unwrap_or("")),
                               "gcode_sha256": sha256_hex(&gcode), "model": record["stl"], "model_sha256": file_sha(&stl)?,
                               "profile": preparation["project"], "profile_sha256": file_sha(&project)?}),
            };
            let reading = audit::audit(&gcode, &options);
            save(&directory.join(format!("support-audit-{oid}.json")), &reading)?;
            audits.insert(oid.to_string(), reading["summary"].clone());
        }
    }
    let unbacked_json: Vec<Value> = unbacked_rows.iter().map(|((oid, band), v)| json!({"object": oid, "band": band,
        "roads": v[0], "unbacked_mm": v[1], "longest_mm": v[2], "bridge_mm": v[3], "layers": v[4]})).collect();
    let emitted = preparation["emitted_textured_trim_mm"].as_f64().unwrap_or(0.0);
    let mut checks = json!({
        "archive": integrity && project_check["pass"] == json!(true),
        "z_trim": trims.last().is_some_and(|t| (t - emitted).abs() < 0.005),
        "bed_border": minimum >= border,
        "fine_and_transition_bands": band_results.iter().all(|r| r["pass"] == json!(true)),
        "show_faces_support_free": show_contacts.is_empty(),
        "tie_windows_support_free": window_crossings.is_empty(),
        "solid_hosts_sampled": dense.iter().all(|r| r["minimum_coverage"].as_f64().is_none_or(|c| c >= 0.9)),
    });
    let mut result = json!({
        "archive": preparation["archive"], "archive_sha256": preparation["archive_sha256"],
        "fine_band_unbacked_statistics_requested": unbacked,
        "gcode_md5_matches": integrity, "emitted_z_trim_mm": trims, "expected_emitted_textured_trim_mm": emitted,
        "layers": layers_seen, "project_check": project_check["pass"],
        "bead_envelope_plate_mm": [bead_low, bead_high], "bed_margins_mm": margins, "minimum_bed_margin_mm": minimum,
        "bed_border_mm": border, "fine_and_transition_bands": band_results, "support_roads": support_roads,
        "show_face_minimum_bead_clearance_mm": show_min, "show_face_contacts": show_contacts,
        "tie_window_support_crossings": window_crossings.iter().take(200).collect::<Vec<_>>(),
        "fine_band_unbacked_roads": unbacked_json, "first_second_layer_stack": stack,
        "solid_host_deposition": dense, "support_topology": audits,
        "scope": "Commanded paths and bead envelopes from this archive. Support removal, surface finish, fit and strength are physical observations.",
    });
    if !excluded.is_empty() {
        let mut counts = Map::new();
        for (_, region) in &excluded {
            let name = region["name"].as_str().unwrap_or("");
            counts.insert(name.to_string(), json!(excluded_support.iter().filter(|r| r["name"].as_str() == Some(name)).count()));
        }
        result["support_free_regions"] = json!(excluded.iter().map(|(oid, region)| {
            let mut row = (*region).clone();
            row["object"] = json!(oid);
            row
        }).collect::<Vec<_>>());
        result["excluded_support_crossings"] = json!(excluded_support.iter().take(200).collect::<Vec<_>>());
        result["excluded_support_crossing_count"] = json!(excluded_support.len());
        result["excluded_support_counts_by_region"] = Value::Object(counts);
        checks["declared_interiors_support_free"] = json!(excluded_support.is_empty());
    }
    let pass = checks.as_object().unwrap().values().all(|v| v == &json!(true));
    result["checks"] = checks.clone();
    result["pass"] = json!(pass);
    save(&directory.join("review.json"), &result)?;
    println!("{}", serde_json::to_string_pretty(&json!({"checks": checks, "minimum_bed_margin_mm": minimum, "support_topology": result["support_topology"]}))?);
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_road_through_a_bead_leaves_its_ends() {
        let beads = Beads::new(vec![Capsule { a: [0.0, 0.0], b: [1.0, 0.0], r: 0.5 }]);
        let free: f64 = beads.uncovered([-2.0, 0.0], [3.0, 0.0]).iter().sum();
        assert!((free - 3.0).abs() < 1e-9, "{free}");
    }

    #[test]
    fn a_bead_area_is_its_capsule() {
        let beads = Beads::new(vec![Capsule { a: [0.0, 0.0], b: [2.0, 0.0], r: 0.5 }]);
        let mut area = 0.0;
        let mut y = -0.5 + SCAN / 2.0;
        while y < 0.5 {
            area += run_length(&beads.runs(y, -2.0, 4.0)) * SCAN;
            y += SCAN;
        }
        let exact = 2.0 + std::f64::consts::PI * 0.25;
        assert!((area - exact).abs() < 2e-3, "{area} vs {exact}");
    }

    #[test]
    fn the_nearest_point_of_a_triangle() {
        let (a, b, c) = ([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]);
        assert!((point_triangle([0.2, 0.2, 1.0], a, b, c) - 1.0).abs() < 1e-12);
        assert!((point_triangle([2.0, 0.0, 0.0], a, b, c) - 1.0).abs() < 1e-12);
    }
}
