//! A print's viewer payload, cut from its STL triangles at the viewer's surface policy.
pub mod printed;
mod quadric;
use anyhow::{Result, ensure};
use hsm_geometry::parry::{math::Point, query::PointQuery, shape::TriMesh};
use hsm_kernel::{V3, v3};
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::sync::Arc;

/// A print surface welded from its STL: points and the triangles that name them.
pub struct Mesh {
    pub points: Vec<V3>,
    pub faces: Vec<[u32; 3]>,
}
struct Edge {
    a: u32,
    b: u32,
    face: usize,
}
/// Each triangle's contributor records: shared records, the groups that cite them, and each
/// triangle's group.
pub struct Lineage {
    records: Arc<Vec<Value>>,
    groups: Vec<Vec<usize>>,
    faces: Vec<usize>,
}

/// The binary STL's triangles welded at its float32 positions, and whether every weld kept
/// each corner's exact position.
pub fn weld(bytes: &[u8]) -> Result<(Mesh, bool)> {
    ensure!(bytes.len() >= 84, "binary print STL header");
    let count = u32::from_le_bytes(bytes[80..84].try_into()?) as usize;
    ensure!(bytes.len() == 84 + count * 50, "binary print STL triangle count");
    let mut weld = HashMap::<[i64; 3], u32>::with_capacity(count / 2 + 1);
    let mut points = Vec::with_capacity(count / 2 + 1);
    let mut faces = Vec::with_capacity(count);
    let mut exact = true;
    for i in 0..count {
        let mut triangle = [0; 3];
        for j in 0..3 {
            let p: [f64; 3] = std::array::from_fn(|k| {
                let start = 84 + i * 50 + 12 + j * 12 + k * 4;
                f32::from_le_bytes(bytes[start..start + 4].try_into().unwrap()) as f64
            });
            ensure!(p.iter().all(|x| x.is_finite()), "finite print vertices");
            let key = p.map(|x| (x * 1.0e8).round_ties_even() as i64);
            let id = *weld.entry(key).or_insert_with(|| {
                points.push(V3::from(p));
                (points.len() - 1) as u32
            });
            exact &= points[id as usize].to_array().map(|x| (x as f32).to_bits()) == p.map(|x| (x as f32).to_bits());
            triangle[j] = id;
        }
        faces.push(triangle);
    }
    Ok((Mesh { points, faces }, exact))
}

fn geometry(mesh: &Mesh) -> (Vec<V3>, Vec<f64>, Vec<Edge>) {
    let mut normals = Vec::with_capacity(mesh.faces.len());
    let mut areas = Vec::with_capacity(mesh.faces.len());
    let mut edges = Vec::with_capacity(mesh.faces.len() * 3);
    for (i, t) in mesh.faces.iter().enumerate() {
        let [a, b, c] = t.map(|k| mesh.points[k as usize]);
        let cross = (b - a).cross(c - a);
        let len = cross.norm();
        normals.push(if len > 1.0e-15 { cross / len } else { V3::ZERO });
        areas.push(len / 2.);
        for k in 0..3 {
            edges.push(Edge { a: t[k].min(t[(k + 1) % 3]), b: t[k].max(t[(k + 1) % 3]), face: i });
        }
    }
    edges.sort_unstable_by_key(|e| (e.a, e.b, e.face));
    (normals, areas, edges)
}

pub struct Random {
    state: u128,
    high: Option<u32>,
}
impl Random {
    // NumPy PCG64's SeedSequence(0), with its uint32 buffering and Lemire bounds.
    pub fn new() -> Self {
        Self { state: 35399562948360463058890781895381311971, high: None }
    }
    fn next(&mut self) -> u64 {
        self.state = self.state.wrapping_mul(0x2360ed051fc65da44385df649fccf645).wrapping_add(87136372517582989555478159403783844777);
        (((self.state >> 64) as u64) ^ (self.state as u64)).rotate_right((self.state >> 122) as u32)
    }
    fn next32(&mut self) -> u32 {
        if let Some(high) = self.high.take() {
            high
        } else {
            let n = self.next();
            self.high = Some((n >> 32) as u32);
            n as u32
        }
    }
    pub fn bounded(&mut self, max: usize) -> usize {
        if max == 0 {
            return 0;
        }
        let range = max as u64 + 1;
        if max < u32::MAX as usize {
            let threshold = ((u32::MAX as u64 - max as u64) % range) as u32;
            loop {
                let m = self.next32() as u64 * range;
                if m as u32 >= threshold {
                    return (m >> 32) as usize;
                }
            }
        } else {
            let threshold = (u64::MAX - max as u64) % range;
            loop {
                let m = self.next() as u128 * range as u128;
                if m as u64 >= threshold {
                    return (m >> 64) as usize;
                }
            }
        }
    }
}
impl Default for Random {
    fn default() -> Self {
        Self::new()
    }
}

fn probes(mesh: &Mesh, normals: &[V3], edges: &[Edge], angle: f64) -> Vec<usize> {
    let n = mesh.points.len();
    let size = n.min(40000);
    let mut rng = Random::new();
    let mut selected = BTreeSet::new();
    if n <= size {
        selected.extend(0..n);
    } else if n > 10000 && size > n / 50 {
        let mut ids = (0..n).collect::<Vec<_>>();
        for i in ((n - size).max(1)..n).rev() {
            let j = rng.bounded(i);
            ids.swap(i, j);
        }
        selected.extend(ids[n - size..].iter().copied());
    } else {
        for j in n - size..n {
            let v = rng.bounded(j);
            if !selected.insert(v) {
                selected.insert(j);
            }
        }
    }
    let mut i = 0;
    while i < edges.len() {
        let mut j = i + 1;
        while j < edges.len() && edges[j].a == edges[i].a && edges[j].b == edges[i].b {
            j += 1;
        }
        if j - i == 2 {
            let dot = normals[edges[i].face].dot(normals[edges[i + 1].face]).clamp(-1., 1.);
            if dot.acos() >= angle {
                selected.insert(edges[i].a as usize);
                selected.insert(edges[i].b as usize);
            }
        }
        i = j;
    }
    selected.into_iter().collect()
}
fn deviation(original: &Mesh, reduced: &Mesh, probes: &[usize]) -> Result<f64> {
    let shape = TriMesh::new(reduced.points.iter().map(|p| Point::new(p.x, p.y, p.z)).collect(), reduced.faces.clone())
        .map_err(|e| anyhow::anyhow!("reduced print mesh: {e}"))?;
    let mut worst: f64 = 0.;
    for &i in probes {
        let p = original.points[i];
        let point = Point::new(p.x, p.y, p.z);
        let q = shape.project_local_point(&point, false).point;
        worst = worst.max((v3(q.x, q.y, q.z) - p).norm());
    }
    Ok(worst)
}
fn valid_contributor(v: &Value) -> bool {
    if v.is_null() {
        return true;
    }
    let Some(m) = v.as_object() else { return false };
    if !m.get("op").is_some_and(Value::is_string) || !m.get("src").is_some_and(|v| v.is_null() || v.is_string()) {
        return false;
    }
    m.get("via").is_none_or(|v| {
        v.is_null()
            || v.as_object().is_some_and(|m| {
                m.get("op").is_some_and(Value::is_string) && m.get("src").is_some_and(|v| v.is_null() || v.is_string())
            })
    })
}

/// The print's lineage from its triangles' source groups, when every triangle of `count`
/// has one, every record is a contributor and the weld kept each corner exactly.
pub fn lineage(records: &[Vec<Value>], triangles: &[usize], count: usize, exact: bool) -> Option<Lineage> {
    if !exact || triangles.len() != count || !records.iter().all(|r| r.iter().all(valid_contributor)) {
        return None;
    }
    // Keep contributor records once, rather than cloning their JSON for every triangle.
    // Canonical-key order is the same order used by each final face's source union.
    let mut catalog = BTreeMap::from([("null".to_owned(), Value::Null)]);
    for group in records {
        for record in group {
            catalog.entry(serde_json::to_string(record).ok()?).or_insert_with(|| record.clone());
        }
    }
    let mut values = Vec::with_capacity(catalog.len());
    let mut lookup = HashMap::new();
    for (key, value) in catalog {
        lookup.insert(key, values.len());
        values.push(value);
    }
    let empty = lookup["null"];
    let groups = records
        .iter()
        .map(|group| {
            let mut ids = group.iter().map(|record| Some(lookup[&serde_json::to_string(record).ok()?])).collect::<Option<Vec<_>>>()?;
            ids.sort_unstable();
            ids.dedup();
            if ids.is_empty() {
                ids.push(empty);
            }
            Some(ids)
        })
        .collect::<Option<Vec<_>>>()?;
    let faces = triangles
        .iter()
        .map(|&id| {
            groups.get(id)?;
            Some(id)
        })
        .collect::<Option<Vec<_>>>()?;
    Some(Lineage { records: Arc::new(values), groups, faces })
}
fn source_union(sources: &Lineage, faces: &[usize]) -> Vec<Value> {
    let mut ids = Vec::new();
    for &face in faces {
        ids.extend_from_slice(&sources.groups[sources.faces[face]]);
    }
    ids.sort_unstable();
    ids.dedup();
    if ids.is_empty() { vec![Value::Null] } else { ids.into_iter().map(|id| sources.records[id].clone()).collect() }
}
fn collapsed_sources(original: &Mesh, reduced: &Mesh, collapses: &[[u32; 2]], sources: &Lineage) -> Lineage {
    let mut parent = (0..original.points.len() as u32).collect::<Vec<_>>();
    for &[a, b] in collapses {
        parent[b as usize] = a;
    }
    for i in 0..parent.len() {
        let mut root = parent[i];
        while parent[root as usize] != root {
            root = parent[root as usize];
        }
        parent[i] = root;
    }
    let mapped = original.faces.iter().map(|t| t.map(|i| parent[i as usize])).collect::<Vec<_>>();
    let good = |t: &[u32; 3]| t[0] != t[1] && t[1] != t[2] && t[2] != t[0];
    let used = mapped.iter().filter(|t| good(t)).flatten().copied().collect::<BTreeSet<_>>();
    let remap = used.into_iter().enumerate().map(|(i, k)| (k, i as u32)).collect::<HashMap<_, _>>();
    let mut by_triangle = HashMap::<[u32; 3], Vec<usize>>::new();
    for (i, t) in mapped.iter().enumerate() {
        if !good(t) {
            continue;
        }
        let mut key = t.map(|i| remap[&i]);
        key.sort_unstable();
        by_triangle.entry(key).or_default().extend_from_slice(&sources.groups[sources.faces[i]]);
    }
    for ids in by_triangle.values_mut() {
        ids.sort_unstable();
        ids.dedup();
    }
    let empty = sources.records.iter().position(Value::is_null).unwrap();
    let mut groups = Vec::new();
    let mut intern = HashMap::new();
    let mut faces = Vec::with_capacity(reduced.faces.len());
    for t in &reduced.faces {
        let mut key = *t;
        key.sort_unstable();
        let ids = by_triangle.get(&key).cloned().unwrap_or_else(|| vec![empty]);
        let next = groups.len();
        let id = *intern.entry(ids.clone()).or_insert_with(|| {
            groups.push(ids);
            next
        });
        faces.push(id);
    }
    Lineage { records: Arc::clone(&sources.records), groups, faces }
}
fn root(parent: &mut [usize], mut i: usize) -> usize {
    while parent[i] != i {
        parent[i] = parent[parent[i]];
        i = parent[i];
    }
    i
}
type Arrays = (Vec<f32>, Vec<f32>, Vec<u32>, Vec<u32>, Option<Vec<Vec<Value>>>);
fn creased(mesh: &Mesh, angle: f64, sources: Option<&Lineage>) -> Arrays {
    let (normals, areas, edges) = geometry(mesh);
    let mut parent = (0..mesh.faces.len()).collect::<Vec<_>>();
    let mut i = 0;
    while i < edges.len() {
        let mut j = i + 1;
        while j < edges.len() && edges[j].a == edges[i].a && edges[j].b == edges[i].b {
            j += 1;
        }
        if j - i == 2 && normals[edges[i].face].dot(normals[edges[i + 1].face]).clamp(-1., 1.).acos() <= angle {
            let a = root(&mut parent, edges[i].face);
            let b = root(&mut parent, edges[i + 1].face);
            parent[a.max(b)] = a.min(b);
        }
        i = j;
    }
    let mut regions = HashMap::new();
    let mut labels = Vec::with_capacity(parent.len());
    for i in 0..parent.len() {
        let r = root(&mut parent, i);
        let next = regions.len();
        labels.push(*regions.entry(r).or_insert(next));
    }
    // Counting by region retains face order without sorting all triangles. A packed
    // (vertex, region) key retains the existing lexicographic corner order.
    let mut starts = vec![0; regions.len() + 1];
    for &label in &labels {
        starts[label + 1] += 1;
    }
    for i in 1..starts.len() {
        starts[i] += starts[i - 1];
    }
    let mut next = starts[..regions.len()].to_vec();
    let mut order = vec![0; mesh.faces.len()];
    for (i, &label) in labels.iter().enumerate() {
        order[next[label]] = i;
        next[label] += 1;
    }
    let mut corners = order.iter().flat_map(|&i| mesh.faces[i].map(|v| ((v as u64) << 32) | labels[i] as u64)).collect::<Vec<_>>();
    corners.sort_unstable();
    corners.dedup();
    let mut offsets = vec![0; mesh.points.len() + 1];
    for &key in &corners {
        offsets[(key >> 32) as usize + 1] += 1;
    }
    for i in 1..offsets.len() {
        offsets[i] += offsets[i - 1];
    }
    let positions = corners.iter().flat_map(|&key| mesh.points[(key >> 32) as usize].to_array().map(|x| x as f32)).collect();
    let mut sums = vec![V3::ZERO; corners.len()];
    let mut first_normal = vec![None; corners.len()];
    let mut indices = Vec::with_capacity(mesh.faces.len() * 3);
    let mut ranges = Vec::new();
    let mut groups = Vec::new();
    let mut begin = 0;
    for (position, &face) in order.iter().enumerate() {
        let weighted = normals[face] * areas[face];
        for &v in &mesh.faces[face] {
            let begin = offsets[v as usize];
            let end = offsets[v as usize + 1];
            let key = ((v as u64) << 32) | labels[face] as u64;
            let k = begin + corners[begin..end].binary_search(&key).unwrap();
            indices.push(k as u32);
            sums[k] += weighted;
            if first_normal[k].is_none() {
                first_normal[k] = Some(normals[face]);
            }
        }
        if position + 1 == order.len() || labels[order[position + 1]] != labels[face] {
            ranges.extend([begin as u32, position as u32]);
            if let Some(s) = sources {
                groups.push(source_union(s, &order[begin..=position]));
            }
            begin = position + 1;
        }
    }
    let blanks = sums.iter().filter(|n| n.norm() < 1.0e-12).count();
    let shade = sums
        .iter()
        .enumerate()
        .flat_map(|(k, n)| {
            let p = if n.norm() < 1.0e-12 {
                if blanks == 1 { first_normal[k].unwrap_or(V3::Z).unit() } else { V3::Z }
            } else {
                n.unit()
            };
            p.to_array().map(|x| x as f32)
        })
        .collect();
    (positions, shade, indices, ranges, sources.map(|_| groups))
}
fn payload(name: Value, color: Value, src: &str, bound: f64, dev: f64, arrays: Arrays, unknown: bool) -> Result<Vec<u8>> {
    let (pos, nrm, idx, fac, sources) = arrays;
    let mut offset = 0;
    let mut entry = json!({"name": name, "color": color});
    for (key, count) in [("pos", pos.len()), ("nrm", nrm.len()), ("idx", idx.len()), ("fac", fac.len())] {
        entry[key] = json!([offset, count]);
        offset += count * 4;
    }
    let faces = fac.len() / 2;
    if let Some(s) = sources {
        entry["face_sources"] = json!(s);
    } else if unknown {
        entry["face_sources"] = json!(vec![vec![Value::Null]; faces]);
    }
    let round = |x: f64| format!("{x:.4}").parse::<f64>().unwrap();
    let header = json!({"v": 3, "meshes": [entry], "src": src, "cut": {"dev": round(dev), "bound": round(bound)}});
    let mut text = serde_json::to_vec(&header)?;
    while (text.len() + 4) % 4 != 0 {
        text.push(b' ');
    }
    let mut out = Vec::with_capacity(4 + text.len() + offset);
    out.extend_from_slice(&(text.len() as u32).to_le_bytes());
    out.extend_from_slice(&text);
    for values in [&pos[..], &nrm[..]] {
        for value in values {
            out.extend_from_slice(&value.to_le_bytes());
        }
    }
    for values in [&idx[..], &fac[..]] {
        for value in values {
            out.extend_from_slice(&value.to_le_bytes());
        }
    }
    Ok(out)
}

/// One payload and what its reduction cost.
pub struct Cut {
    pub payload: Vec<u8>,
    pub printed_triangles: usize,
    pub drawing_triangles: usize,
    pub bound: f64,
    pub deviation: f64,
    pub reduction: f64,
    pub probe_vertices: usize,
    pub watertight: bool,
    pub non_manifold_edges: usize,
}

/// The viewer's crease angle, in degrees: wider dihedral angles shade as separate regions.
pub const CREASE_DEG: f64 = 30.0;
/// The payload's distance budget per millimetre of the model's mean extent.
pub const LINEAR_DEFLECTION_RATIO: f64 = 0.001;
/// The angular deflection, in radians, the viewer's STEP reader takes when it is given none.
pub const ANGULAR_DEFLECTION: f64 = 0.5;

/// What a payload is cut from, besides the print's triangles: the body it names, the digest
/// of the file it answers to, and the surface policy.
pub struct Request<'a> {
    pub name: Value,
    pub color: Value,
    pub src: &'a str,
    pub crease_deg: f64,
    pub deflection_ratio: f64,
    /// Keep every printed triangle.
    pub preserve: bool,
    /// Without lineage, mark every region's source unknown.
    pub unknown: bool,
    /// Refuse a print that is not closed and manifold.
    pub check: bool,
}

/// The payload of a printed mesh: the coarsest reduction inside the deflection budget, its
/// regions creased at the viewer's angle, its lineage carried through the collapses.
pub fn cut(mesh: &Mesh, lineage: Option<Lineage>, r: Request) -> Result<Cut> {
    ensure!(!mesh.faces.is_empty(), "printed mesh has triangles");
    let (normals, _, edges) = geometry(mesh);
    let mut non_manifold = 0;
    let mut watertight = true;
    let mut i = 0;
    while i < edges.len() {
        let mut j = i + 1;
        while j < edges.len() && edges[j].a == edges[i].a && edges[j].b == edges[i].b {
            j += 1;
        }
        if j - i > 2 {
            non_manifold += 1;
        }
        if j - i != 2 {
            watertight = false;
        }
        i = j;
    }
    if r.check {
        ensure!(non_manifold == 0 && watertight, "{non_manifold} non-manifold edge(s), watertight={watertight}");
    }
    let angle = r.crease_deg.to_radians();
    let probe = if r.preserve { Vec::new() } else { probes(mesh, &normals, &edges, angle) };
    drop(normals);
    drop(edges);
    let mut lo = v3(f64::INFINITY, f64::INFINITY, f64::INFINITY);
    let mut hi = -lo;
    for &p in &mesh.points {
        lo = lo.min(p);
        hi = hi.max(p);
    }
    let size = hi - lo;
    let bound = (size.x + size.y + size.z) / 3. * r.deflection_ratio;
    let mut accepted = None;
    for reduction in [0.97, 0.95, 0.90, 0.80, 0.75, 0.60].into_iter().filter(|_| !r.preserve) {
        let (points, faces, collapses) = quadric::simplify(&mesh.points, &mesh.faces, reduction, 4.);
        let reduced = Mesh { points, faces };
        let dev = deviation(mesh, &reduced, &probe)?;
        if dev <= bound {
            let sources = lineage.as_ref().map(|s| collapsed_sources(mesh, &reduced, &collapses, s));
            accepted = Some((reduced, dev, sources, reduction));
            break;
        }
    }
    let (reduced, dev, sources, reduction) = match accepted {
        Some(a) => a,
        None => (Mesh { points: mesh.points.clone(), faces: mesh.faces.clone() }, 0., lineage, 0.),
    };
    let arrays = creased(&reduced, angle, sources.as_ref());
    Ok(Cut {
        payload: payload(r.name, r.color, r.src, bound, dev, arrays, r.unknown)?,
        printed_triangles: mesh.faces.len(),
        drawing_triangles: reduced.faces.len(),
        bound,
        deviation: dev,
        reduction,
        probe_vertices: probe.len(),
        watertight,
        non_manifold_edges: non_manifold,
    })
}
