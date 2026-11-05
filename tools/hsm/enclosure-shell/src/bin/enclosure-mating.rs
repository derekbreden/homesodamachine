//! The fit gaps where the four printed enclosure quadrants meet, read off their fine models.
//!
//! `hardware/scripts/check_enclosure_mating_clearance.py` writes the numbers: each quadrant's
//! model and the way it prints, the fits, and the required gaps the enclosure recipe places.
//!
//! A triangle lies on a plane when its face record is that plane and its corners are on it
//! within the kernel's tolerance; coplanar triangles that share an edge are one patch. Two
//! patches of different quadrants that face each other, no farther apart than the largest fit a
//! pair can require and overlapping by more than an edge's sliver, are a mating pair. A pair
//! needs static clearance head-on in Y and running clearance otherwise, plus the supported-face
//! allowance for each of its faces that prints facing down above the bed. A required gap names a
//! point on one quadrant's face, the way across to the other's and the gap; it holds when both
//! faces are there and the gap between them is air.
//!
//! ```text
//! enclosure-mating <numbers.json> --check
//! ```
use anyhow::{Context, Result, ensure};
use hsm_kernel::part::args;
use hsm_kernel::{Surface, TOLERANCE, V2, V3, src_line, v2, v3};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::Path;

/// An overlap smaller than this is two faces meeting along an edge.
const LEAST_AREA: f64 = 0.05;

struct Fits {
    slip: f64,
    running: f64,
    supported: f64,
}

struct Patch {
    n: V3,
    d: f64,
    tris: Vec<usize>,
    lo: V3,
    hi: V3,
    sources: BTreeSet<String>,
}

struct Piece {
    name: String,
    up: f64,
    verts: Vec<V3>,
    tris: Vec<[usize; 3]>,
    /// The plane each triangle lies on, as its unit normal and offset along it.
    planes: Vec<Option<(V3, f64)>>,
    bed: f64,
    patches: Vec<Patch>,
}

fn q(x: f64, decimals: i32) -> i64 {
    (x * 10f64.powi(decimals)).round() as i64
}

fn facing(n: V3) -> [i64; 3] {
    [q(n.x, 5), q(n.y, 5), q(n.z, 5)]
}

fn vector(v: &Value) -> Result<V3> {
    let a = v.as_array().context("three coordinates")?;
    ensure!(a.len() == 3, "three coordinates");
    let c = a.iter().map(|x| x.as_f64().context("a coordinate")).collect::<Result<Vec<_>>>()?;
    Ok(v3(c[0], c[1], c[2]))
}

fn array(p: V3) -> Value {
    json!([p.x, p.y, p.z])
}

/// The plane triangle `tri` lies on: its face record's, when its corners are on that plane and
/// it faces the plane's way.
fn on_plane(verts: &[V3], tri: [usize; 3], surface: &Surface) -> Option<(V3, f64)> {
    let Surface::Plane { p, n } = *surface else { return None };
    let n = n.unit();
    let d = n.dot(p);
    let [a, b, c] = tri.map(|k| verts[k]);
    if [a, b, c].iter().any(|&corner| (n.dot(corner) - d).abs() > TOLERANCE) {
        return None;
    }
    ((b - a).cross(c - a).dot(n) > 0.0).then_some((n, d))
}

fn find(parent: &mut [usize], mut i: usize) -> usize {
    while parent[i] != i {
        parent[i] = parent[parent[i]];
        i = parent[i];
    }
    i
}

/// Each plane's triangles, split where they stop sharing edges.
fn patches(verts: &[V3], tris: &[[usize; 3]], planes: &[Option<(V3, f64)>], sources: &[String]) -> Vec<Patch> {
    let mut groups: BTreeMap<[i64; 4], Vec<usize>> = BTreeMap::new();
    for (t, plane) in planes.iter().enumerate() {
        if let Some((n, d)) = plane {
            groups.entry([q(n.x, 6), q(n.y, 6), q(n.z, 6), q(*d, 5)]).or_default().push(t);
        }
    }
    let mut out = vec![];
    for members in groups.into_values() {
        let mut parent: Vec<usize> = (0..members.len()).collect();
        let mut edges: HashMap<(usize, usize), usize> = HashMap::new();
        for (i, &t) in members.iter().enumerate() {
            let [a, b, c] = tris[t];
            for (u, w) in [(a, b), (b, c), (c, a)] {
                match edges.get(&(u.min(w), u.max(w))) {
                    Some(&j) => {
                        let (ri, rj) = (find(&mut parent, i), find(&mut parent, j));
                        parent[ri.max(rj)] = ri.min(rj);
                    }
                    None => {
                        edges.insert((u.min(w), u.max(w)), i);
                    }
                }
            }
        }
        let mut parts: BTreeMap<usize, Vec<usize>> = BTreeMap::new();
        for i in 0..members.len() {
            let root = find(&mut parent, i);
            parts.entry(root).or_default().push(members[i]);
        }
        for tris_of in parts.into_values() {
            let (n, d) = planes[tris_of[0]].unwrap();
            let mut lo = v3(f64::INFINITY, f64::INFINITY, f64::INFINITY);
            let mut hi = -lo;
            for &t in &tris_of {
                for k in tris[t] {
                    lo = lo.min(verts[k]);
                    hi = hi.max(verts[k]);
                }
            }
            let sources = tris_of.iter().map(|&t| sources[t].clone()).filter(|s| !s.is_empty()).collect();
            out.push(Patch { n, d, tris: tris_of, lo, hi, sources });
        }
    }
    out
}

fn piece(spec: &Value, digests: &mut BTreeMap<String, String>) -> Result<Piece> {
    let name = spec["name"].as_str().context("a piece's name")?.to_owned();
    let path = spec["model"].as_str().context("a piece's model")?;
    let up = spec["print_up"].as_f64().context("a piece's print direction")?;
    ensure!(up == 1.0 || up == -1.0, "{name} prints with +Z up (1) or down (-1)");
    let bytes = std::fs::read(path).with_context(|| format!("reading {path}"))?;
    hsm_kernel::reads::read(Path::new(path), &bytes);
    digests.insert(path.to_owned(), format!("{:x}", Sha256::digest(&bytes)));
    let bodies = hsm_kernel::import::model_bodies(&bytes).with_context(|| format!("reading {path}"))?;
    ensure!(!bodies.is_empty(), "{path} holds no body");
    let (mut verts, mut tris, mut planes, mut sources) = (vec![], vec![], vec![], vec![]);
    for body in &bodies {
        let solid = &body.solid;
        let base = verts.len();
        verts.extend_from_slice(solid.verts());
        for (t, tri) in solid.tris().iter().enumerate() {
            let tri = tri.map(|k| base + k as usize);
            let face = solid.face_at(t);
            planes.push(on_plane(&verts, tri, &face.surface));
            sources.push(src_line(face.src));
            tris.push(tri);
        }
    }
    let used = tris.iter().flatten().map(|&k| verts[k].z);
    let bed = if up > 0.0 { used.fold(f64::INFINITY, f64::min) } else { used.fold(f64::NEG_INFINITY, f64::max) };
    let patches = patches(&verts, &tris, &planes, &sources);
    Ok(Piece { name, up, verts, tris, planes, bed, patches })
}

/// Two unit vectors that complete `n` to a right-handed frame, so a triangle facing `n` runs
/// counter-clockwise in them.
fn frame(n: V3) -> (V3, V3) {
    let helper = if n.x.abs() < 0.9 { V3::X } else { V3::Y };
    let u = n.cross(helper).unit();
    (u, n.cross(u))
}

fn counter_clockwise(mut t: [V2; 3]) -> [V2; 3] {
    if (t[1] - t[0]).cross(t[2] - t[0]) < 0.0 {
        t.swap(1, 2);
    }
    t
}

fn extent(t: &[V2; 3]) -> (V2, V2) {
    let lo = v2(t[0].x.min(t[1].x).min(t[2].x), t[0].y.min(t[1].y).min(t[2].y));
    let hi = v2(t[0].x.max(t[1].x).max(t[2].x), t[0].y.max(t[1].y).max(t[2].y));
    (lo, hi)
}

/// What of triangle `subject` lies inside the counter-clockwise triangle `window`.
fn clip(subject: &[V2; 3], window: &[V2; 3]) -> Vec<V2> {
    let mut out = subject.to_vec();
    for k in 0..3 {
        let (e0, e1) = (window[k], window[(k + 1) % 3]);
        let side = |p: V2| (e1 - e0).cross(p - e0);
        let input = std::mem::take(&mut out);
        for i in 0..input.len() {
            let (p, r) = (input[i], input[(i + 1) % input.len()]);
            let (sp, sr) = (side(p), side(r));
            if sp >= 0.0 {
                out.push(p);
            }
            if (sp >= 0.0) != (sr >= 0.0) {
                out.push(p + (r - p) * (sp / (sp - sr)));
            }
        }
        if out.len() < 3 {
            return vec![];
        }
    }
    out
}

/// A polygon's area and centroid.
fn polygon(p: &[V2]) -> (f64, V2) {
    let (mut twice, mut moment) = (0.0, V2::ZERO);
    for i in 0..p.len() {
        let (s, t) = (p[i], p[(i + 1) % p.len()]);
        let w = s.cross(t);
        twice += w;
        moment += (s + t) * w;
    }
    if twice <= 0.0 { (0.0, V2::ZERO) } else { (twice / 2.0, moment / (3.0 * twice)) }
}

struct Common {
    area: f64,
    center: V3,
    lo: V3,
    hi: V3,
}

/// Where patch `b`, moved onto `a`'s plane, covers `a`.
fn overlap(pa: &Piece, a: &Patch, pb: &Piece, b: &Patch) -> Option<Common> {
    let (u, w) = frame(a.n);
    let flat = |p: V3| v2(p.dot(u), p.dot(w));
    let window: Vec<([V2; 3], V2, V2)> = b.tris.iter().map(|&t| {
        let tri = counter_clockwise(pb.tris[t].map(|k| flat(pb.verts[k])));
        let (lo, hi) = extent(&tri);
        (tri, lo, hi)
    }).collect();
    let origin = a.n * a.d;
    let (mut area, mut moment) = (0.0, V2::ZERO);
    let mut lo = v3(f64::INFINITY, f64::INFINITY, f64::INFINITY);
    let mut hi = -lo;
    for &t in &a.tris {
        let tri = counter_clockwise(pa.tris[t].map(|k| flat(pa.verts[k])));
        let (tlo, thi) = extent(&tri);
        for (other, olo, ohi) in &window {
            if tlo.x > ohi.x || olo.x > thi.x || tlo.y > ohi.y || olo.y > thi.y {
                continue;
            }
            let shared = clip(&tri, other);
            let (piece_area, centroid) = polygon(&shared);
            if piece_area <= 0.0 {
                continue;
            }
            area += piece_area;
            moment += centroid * piece_area;
            for p in shared {
                let at = origin + u * p.x + w * p.y;
                lo = lo.min(at);
                hi = hi.max(at);
            }
        }
    }
    (area > 0.0).then(|| {
        let c = moment / area;
        Common { area, center: origin + u * c.x + w * c.y, lo, hi }
    })
}

fn bedded(patch: &Patch, bed: f64) -> bool {
    (patch.lo.z - bed).abs() < TOLERANCE && (patch.hi.z - bed).abs() < TOLERANCE
}

/// A face printed facing down that does not rest on the bed prints on supports.
fn rough(piece: &Piece, patch: &Patch) -> bool {
    patch.n.z * piece.up < -0.99 && !bedded(patch, piece.bed)
}

fn census(pieces: &[Piece], fits: &Fits, reach: f64) -> Vec<Value> {
    let mut readings = vec![];
    for (i, pa) in pieces.iter().enumerate() {
        for pb in &pieces[i + 1..] {
            let mut by_facing: HashMap<[i64; 3], Vec<&Patch>> = HashMap::new();
            for b in &pb.patches {
                by_facing.entry(facing(b.n)).or_default().push(b);
            }
            for a in &pa.patches {
                for &b in by_facing.get(&facing(-a.n)).into_iter().flatten() {
                    let gap = -b.d - a.d;
                    if gap < -TOLERANCE || gap > reach + TOLERANCE {
                        continue;
                    }
                    let shift = a.n * -gap;
                    let (blo, bhi) = (b.lo + shift, b.hi + shift);
                    if (0..3).any(|k| a.lo[k] > bhi[k] + TOLERANCE || blo[k] > a.hi[k] + TOLERANCE) {
                        continue;
                    }
                    let Some(common) = overlap(pa, a, pb, b) else { continue };
                    if common.area < LEAST_AREA {
                        continue;
                    }
                    let rough = rough(pa, a) as u32 + rough(pb, b) as u32;
                    let head_on = a.n.y.abs() > 0.999;
                    let ordinary = if head_on { fits.slip } else { fits.running };
                    let minimum = ordinary + rough as f64 * fits.supported;
                    let gap = gap.max(0.0);
                    readings.push(json!({
                        "parts": [pa.name, pb.name],
                        "sources": [a.sources, b.sources],
                        "gap_mm": gap,
                        "minimum_mm": minimum,
                        "pass": gap + TOLERANCE >= minimum,
                        "classification": if head_on { "Head-on closure clearance" } else { "Assembly sliding clearance" },
                        "rough_faces_counted": rough,
                        "area_mm2": common.area,
                        "center_mm": array(common.center),
                        "normal_from_first": array(a.n),
                        "bounds_mm": [common.lo.x, common.lo.y, common.lo.z, common.hi.x, common.hi.y, common.hi.z],
                    }));
                }
            }
        }
    }
    readings
}

fn closest(p: V3, [a, b, c]: [V3; 3]) -> V3 {
    let (ab, ac, ap) = (b - a, c - a, p - a);
    let (d1, d2) = (ab.dot(ap), ac.dot(ap));
    if d1 <= 0.0 && d2 <= 0.0 {
        return a;
    }
    let bp = p - b;
    let (d3, d4) = (ab.dot(bp), ac.dot(bp));
    if d3 >= 0.0 && d4 <= d3 {
        return b;
    }
    let vc = d1 * d4 - d3 * d2;
    if vc <= 0.0 && d1 >= 0.0 && d3 <= 0.0 {
        return a + ab * (d1 / (d1 - d3));
    }
    let cp = p - c;
    let (d5, d6) = (ab.dot(cp), ac.dot(cp));
    if d6 >= 0.0 && d5 <= d6 {
        return c;
    }
    let vb = d5 * d2 - d1 * d6;
    if vb <= 0.0 && d2 >= 0.0 && d6 <= 0.0 {
        return a + ac * (d2 / (d2 - d6));
    }
    let va = d3 * d6 - d5 * d4;
    if va <= 0.0 && d4 - d3 >= 0.0 && d5 - d6 >= 0.0 {
        return b + (c - b) * ((d4 - d3) / ((d4 - d3) + (d5 - d6)));
    }
    let sum = va + vb + vc;
    a + ab * (vb / sum) + ac * (vc / sum)
}

/// How far `p` is from the nearest planar face of `piece` that faces `direction`.
fn surface_error(piece: &Piece, p: V3, direction: V3) -> Option<f64> {
    piece.planes.iter().zip(&piece.tris)
        .filter(|(plane, _)| plane.is_some_and(|(n, _)| n.dot(direction) > 0.999))
        .map(|(_, tri)| (closest(p, tri.map(|k| piece.verts[k])) - p).norm())
        .min_by(f64::total_cmp)
}

/// How many times the closed surface of `piece` wraps `p`: one inside, none outside.
fn winding(piece: &Piece, p: V3) -> f64 {
    let mut solid_angle = 0.0;
    for tri in &piece.tris {
        let [a, b, c] = tri.map(|k| piece.verts[k] - p);
        let (la, lb, lc) = (a.norm(), b.norm(), c.norm());
        let det = a.dot(b.cross(c));
        let div = la * lb * lc + a.dot(b) * lc + b.dot(c) * la + c.dot(a) * lb;
        solid_angle += 2.0 * det.atan2(div);
    }
    solid_angle / (4.0 * std::f64::consts::PI)
}

fn probe(pieces: &[Piece], spec: &Value) -> Result<Value> {
    let feature = spec["feature"].as_str().context("a required gap's feature")?;
    let parts = spec["parts"].as_array().context("a required gap's parts")?;
    ensure!(parts.len() == 2, "{feature} names two parts");
    let named = |v: &Value| -> Result<&Piece> {
        let name = v.as_str().context("a part's name")?;
        pieces.iter().find(|p| p.name == name).with_context(|| format!("{feature} names {name}, which is not measured"))
    };
    let (first, second) = (named(&parts[0])?, named(&parts[1])?);
    let point = vector(&spec["point"])?;
    let normal = vector(&spec["normal"])?.unit();
    let gap = spec["gap"].as_f64().context("a required gap's size")?;
    let other = point + normal * gap;
    let errors = [surface_error(first, point, normal), surface_error(second, other, -normal)];
    let error = errors.iter().try_fold(0.0_f64, |most, e| e.map(|e| most.max(e)));
    let middle = point + normal * (gap / 2.0);
    let air = winding(first, middle) < 0.5 && winding(second, middle) < 0.5;
    Ok(json!({
        "feature": feature,
        "parts": [first.name, second.name],
        "face_points_mm": [array(point), array(other)],
        "gap_mm": gap,
        "maximum_surface_error_mm": error,
        "gap_contains_air": air,
        "pass": error.is_some_and(|e| e < TOLERANCE) && air,
    }))
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    ensure!(out == Path::new("--check"), "usage: enclosure-mating <numbers.json> --check");
    let given = n.get("fits")?;
    let fit = |key: &str| given[key].as_f64().with_context(|| format!("the `{key}` fit"));
    let fits = Fits { slip: fit("slip")?, running: fit("running")?, supported: fit("supported_surface")? };
    let reach = fits.slip.max(fits.running) + 2.0 * fits.supported;
    let mut digests = BTreeMap::new();
    let pieces = n.get("pieces")?.as_array().context("the pieces")?.iter()
        .map(|spec| piece(spec, &mut digests)).collect::<Result<Vec<_>>>()?;
    let patches = census(&pieces, &fits, reach);
    let probes = n.get("probes")?.as_array().context("the required gaps")?.iter()
        .map(|spec| probe(&pieces, spec)).collect::<Result<Vec<_>>>()?;
    let failures: Vec<&Value> = patches.iter().chain(&probes).filter(|r| r["pass"] != true).collect();
    let report = json!({
        "status": if failures.is_empty() { "pass" } else { "fail" },
        "source_sha256": digests,
        "scope": format!("Opposed parallel planar patches above {LEAST_AREA} mm2, gaps up to {reach} mm, \
            on the {} finished quadrants' fine models. Excludes curved/nonparallel contacts, insertion \
            sweeps, accessories and physical support quality.", pieces.len()),
        "checked_patches": patches.len(),
        "failures": failures,
        "required_gaps": probes,
        "patches": patches,
    });
    println!("{}", serde_json::to_string(&report)?);
    Ok(())
}

