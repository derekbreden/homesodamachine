//! Manual printed-mesh inspection ranks local geometry anomalies and preserves their source bindings.
mod planes;
mod sources;
#[path = "../../print-prep/src/mesh.rs"]
#[allow(dead_code)]
mod stl;
#[cfg(test)]
mod tests;
mod thin;

use anyhow::{Context, Result, ensure};
use hsm_kernel::math::{V3, v3};
use parry3d_f64::{bounding_volume::Aabb, math::Point, query::PointQuery};
use serde::Serialize;
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::{
    collections::{BTreeMap, BTreeSet, HashMap},
    path::{Path, PathBuf},
};
use stl::Mesh;

pub const CLASSES: [&str; 7] = [
    "step", "bump", "sliver", "ceiling", "slope", "thin", "ledge",
];
pub(crate) const OFFSET: f64 = 0.02;
pub(crate) const CEILING_AREA: f64 = 20.;
pub(crate) const OFF_BED: f64 = 0.5;
pub(crate) fn xyz(p: V3) -> [f64; 3] {
    [p.x, p.y, p.z]
}
pub(crate) fn point(p: [f64; 3]) -> V3 {
    v3(p[0], p[1], p[2])
}
pub(crate) fn unit(p: V3) -> V3 {
    if p.norm() > 1e-12 {
        p / p.norm()
    } else {
        V3::ZERO
    }
}
pub(crate) fn min3(a: V3, b: V3) -> V3 {
    v3(a.x.min(b.x), a.y.min(b.y), a.z.min(b.z))
}
pub(crate) fn max3(a: V3, b: V3) -> V3 {
    v3(a.x.max(b.x), a.y.max(b.y), a.z.max(b.z))
}
pub(crate) fn basis(n: V3) -> (V3, V3) {
    let u = unit(n.cross(if n.z.abs() < 0.9 {
        v3(0., 0., 1.)
    } else {
        v3(1., 0., 0.)
    }));
    (u, n.cross(u))
}
pub(crate) fn click(p: V3) -> String {
    format!("click: x={:.3} y={:.3} z={:.3}", p.x, p.y, p.z)
}
pub(crate) fn face(n: V3, p: V3, label: &str) -> String {
    format!(
        "{label}: plane · n x={:.3} y={:.3} z={:.3} · thru x={:.3} y={:.3} z={:.3}",
        n.x, n.y, n.z, p.x, p.y, p.z
    )
}

#[derive(Clone, Serialize)]
pub struct Finding {
    #[serde(rename = "class")]
    pub class: String,
    pub score: f64,
    pub line: String,
    pub pick: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sources: Option<Vec<Value>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub answer: Option<String>,
    #[serde(skip)]
    pub(crate) facets: Vec<usize>,
}
impl Finding {
    pub(crate) fn new(
        class: &str,
        score: f64,
        line: String,
        pick: Vec<String>,
        facets: Vec<usize>,
    ) -> Self {
        Self {
            class: class.into(),
            score,
            line,
            pick,
            facets,
            sources: None,
            answer: None,
        }
    }
}

#[derive(Clone)]
pub(crate) struct Plane {
    pub n: V3,
    pub o: f64,
    pub f: Vec<usize>,
    pub gid: usize,
    pub lo: V3,
    pub hi: V3,
    pub u: V3,
    pub v: V3,
    pub uv_lo: [f64; 2],
    pub uv_hi: [f64; 2],
    pub area: f64,
}
impl Plane {
    pub fn new(d: &Data, n: V3, o: f64, f: Vec<usize>, gid: usize) -> Self {
        let (u, v) = basis(n);
        let mut lo = v3(f64::INFINITY, f64::INFINITY, f64::INFINITY);
        let mut hi = -lo;
        let mut uv_lo = [f64::INFINITY; 2];
        let mut uv_hi = [f64::NEG_INFINITY; 2];
        for &i in &f {
            for p in d.tri[i] {
                lo = min3(lo, p);
                hi = max3(hi, p);
                for (j, a) in [u, v].into_iter().enumerate() {
                    uv_lo[j] = uv_lo[j].min(p.dot(a));
                    uv_hi[j] = uv_hi[j].max(p.dot(a));
                }
            }
        }
        let area = f.iter().map(|&i| d.area[i]).sum();
        Self {
            n,
            o,
            f,
            gid,
            lo,
            hi,
            u,
            v,
            uv_lo,
            uv_hi,
            area,
        }
    }
    pub fn center(&self) -> V3 {
        (self.lo + self.hi) / 2.
    }
    pub fn thru(&self) -> V3 {
        let p = self.center();
        p + self.n * (self.o - p.dot(self.n))
    }
    pub fn width(&self) -> [f64; 2] {
        [self.uv_hi[0] - self.uv_lo[0], self.uv_hi[1] - self.uv_lo[1]]
    }
    pub fn soft_frac(&self, d: &Data) -> f64 {
        let a: f64 = self.f.iter().map(|&i| d.soft[i]).sum();
        let b: f64 = self.f.iter().map(|&i| d.sharp[i]).sum();
        if a + b > 0. { a / (a + b) } else { 0. }
    }
    pub fn components(&self, d: &Data) -> Vec<Self> {
        let allowed: BTreeSet<_> = self.f.iter().copied().collect();
        let mut todo = allowed.clone();
        let mut parts = Vec::new();
        while let Some(&start) = todo.iter().next() {
            todo.remove(&start);
            let mut f = vec![start];
            let mut at = 0;
            while at < f.len() {
                for &v in &d.vid[f[at]] {
                    for &j in &d.touch[v] {
                        if allowed.contains(&j) && todo.remove(&j) {
                            f.push(j);
                        }
                    }
                }
                at += 1;
            }
            parts.push(Self::new(d, self.n, self.o, f, self.gid));
        }
        parts.sort_by(|a, b| b.area.total_cmp(&a.area));
        parts
    }
}

pub(crate) struct Data {
    pub mesh: Mesh,
    pub tri: Vec<[V3; 3]>,
    pub n: Vec<V3>,
    pub area: Vec<f64>,
    pub centers: Vec<V3>,
    pub vid: Vec<[usize; 3]>,
    pub touch: Vec<Vec<usize>>,
    pub planes: Vec<Plane>,
    pub gid: Vec<usize>,
    pub soft: Vec<f64>,
    pub sharp: Vec<f64>,
    pub boundary: HashMap<(usize, usize), (f64, f64)>,
    pub query: hsm_geometry::payload::Mesh,
}
impl Data {
    pub fn new(mesh: Mesh) -> Result<Self> {
        ensure!(!mesh.faces.is_empty(), "STL contains no facets");
        let tri = mesh
            .faces
            .iter()
            .map(|f| f.map(|i| point(mesh.vertices[i])))
            .collect::<Vec<_>>();
        let cross = tri
            .iter()
            .map(|t| (t[1] - t[0]).cross(t[2] - t[0]))
            .collect::<Vec<_>>();
        let n = cross.iter().copied().map(unit).collect();
        let area = cross.iter().map(|n| n.norm() / 2.).collect();
        let centers = tri.iter().map(|t| (t[0] + t[1] + t[2]) / 3.).collect();
        let mut ids = HashMap::new();
        let mut touch: Vec<Vec<usize>> = Vec::new();
        let vid = tri
            .iter()
            .enumerate()
            .map(|(fi, t)| {
                t.map(|p| {
                    let key = xyz(p).map(|x| (x * 100.).round() as i64);
                    let next = ids.len();
                    let id = *ids.entry(key).or_insert(next);
                    if id == touch.len() {
                        touch.push(Vec::new());
                    }
                    touch[id].push(fi);
                    id
                })
            })
            .collect();
        let query = hsm_geometry::payload::Mesh::from_arrays(
            "printed STL",
            mesh.vertices.clone(),
            mesh.faces.iter().map(|f| f.map(|i| i as u32)).collect(),
        )?;
        let count = tri.len();
        let mut d = Self {
            mesh,
            tri,
            n,
            area,
            centers,
            vid,
            touch,
            planes: Vec::new(),
            gid: vec![usize::MAX; count],
            soft: vec![0.; count],
            sharp: vec![0.; count],
            boundary: HashMap::new(),
            query,
        };
        d.group();
        Ok(d)
    }
    fn group(&mut self) {
        let mut normals: BTreeMap<[i64; 3], Vec<usize>> = BTreeMap::new();
        for (i, n) in self.n.iter().enumerate() {
            if n.norm() > 0.5 {
                normals
                    .entry(xyz(*n).map(|x| (x * 1000.).round() as i64))
                    .or_default()
                    .push(i);
            }
        }
        for (_, facets) in normals {
            let n = self.n[facets[0]];
            let mut rows = facets
                .into_iter()
                .map(|i| (self.n[i].dot(self.tri[i][0]), i))
                .collect::<Vec<_>>();
            rows.sort_by(|a, b| a.0.total_cmp(&b.0));
            let mut at = 0;
            while at < rows.len() {
                let start = at;
                at += 1;
                while at < rows.len() && rows[at].0 - rows[at - 1].0 <= OFFSET {
                    at += 1;
                }
                let f = rows[start..at].iter().map(|r| r.1).collect::<Vec<_>>();
                let o = rows[start..at].iter().map(|r| r.0).sum::<f64>() / (at - start) as f64;
                let gid = self.planes.len();
                for &i in &f {
                    self.gid[i] = gid;
                }
                self.planes.push(Plane::new(self, n, o, f, gid));
            }
        }
        let mut edges: HashMap<(usize, usize), Vec<usize>> = HashMap::new();
        for (i, f) in self.vid.iter().enumerate() {
            for k in 0..3 {
                let (a, b) = (f[k], f[(k + 1) % 3]);
                edges.entry((a.min(b), a.max(b))).or_default().push(i);
            }
        }
        for pair in edges.into_values().filter(|p| p.len() == 2) {
            let (a, b) = (pair[0], pair[1]);
            let (ga, gb) = (self.gid[a], self.gid[b]);
            if ga == gb || ga == usize::MAX || gb == usize::MAX {
                continue;
            }
            let shared = self.vid[a]
                .iter()
                .copied()
                .filter(|v| self.vid[b].contains(v))
                .collect::<Vec<_>>();
            if shared.len() != 2 {
                continue;
            }
            let locate = |v| self.tri[a][self.vid[a].iter().position(|&i| i == v).unwrap()];
            let delta = locate(shared[0]) - locate(shared[1]);
            let len = delta.norm();
            let values = if self.n[a].dot(self.n[b]) > (20f64.to_radians()).cos() {
                &mut self.soft
            } else {
                &mut self.sharp
            };
            values[a] += len;
            values[b] += len;
            let boundary = self.boundary.entry((ga.min(gb), ga.max(gb))).or_default();
            boundary.0 += len;
            if delta.z.abs() / len.max(1e-9) < 0.3 {
                boundary.1 += len;
            }
        }
    }
    pub fn candidates(&self, lo: V3, hi: V3) -> Vec<usize> {
        let box_ = Aabb::new(Point::from(xyz(lo)), Point::from(xyz(hi)));
        self.query
            .shape
            .bvh()
            .intersect_aabb(&box_)
            .map(|i| i as usize)
            .collect()
    }
    pub fn nearest(&self, i: usize, p: V3) -> V3 {
        point(
            self.query
                .shape
                .triangle(i as u32)
                .project_local_point(&Point::from(xyz(p)), false)
                .point
                .into(),
        )
    }
    pub fn banded(&self, p: &Plane, group: &Plane, allowed: usize, split_ok: bool) -> bool {
        let pad = v3(0.05, 0.05, 0.05);
        let ids = self
            .candidates(p.lo - pad, p.hi + pad)
            .into_iter()
            .map(|i| self.gid[i])
            .collect::<BTreeSet<_>>();
        let mut count = 0;
        for id in ids {
            let Some(other) = self.planes.get(id) else {
                continue;
            };
            let cos = other.n.dot(group.n);
            let off = (other.n.dot(p.thru()) - other.o).abs();
            if cos <= 0.9063 || off >= 0.6 {
                continue;
            }
            if split_ok && cos > (2f64.to_radians()).cos() && off < 2. * OFFSET {
                continue;
            }
            count += 1;
        }
        count
            > if split_ok {
                allowed.saturating_sub(1)
            } else {
                allowed
            }
    }
    pub fn touching(&self, facets: &[usize]) -> BTreeSet<usize> {
        facets
            .iter()
            .flat_map(|&i| self.vid[i])
            .flat_map(|v| self.touch[v].iter().copied())
            .collect()
    }
}

pub struct Options {
    pub classes: Vec<String>,
    pub up: Option<f64>,
    pub tilt_x: Option<f64>,
    pub sources: Option<PathBuf>,
}
impl Default for Options {
    fn default() -> Self {
        Self {
            classes: CLASSES.iter().map(|s| (*s).into()).collect(),
            up: None,
            tilt_x: None,
            sources: None,
        }
    }
}
#[derive(Serialize)]
pub struct Report {
    pub file: PathBuf,
    pub sha256: String,
    pub facets: usize,
    pub print_up: f64,
    pub print_tilt_x_degrees: f64,
    pub source_binding: String,
    pub findings: BTreeMap<String, Vec<Finding>>,
    pub answered: Vec<Finding>,
}

/// Inspect the saved print bytes without rebuilding the part or changing its mesh.
pub fn review(stl: &Path, options: &Options) -> Result<Report> {
    let bytes = std::fs::read(stl).with_context(|| format!("reading {}", stl.display()))?;
    let hash = format!("{:x}", Sha256::digest(&bytes));
    let mesh = Mesh::from_corners(&stl::stl_corners(&bytes)?);
    let d = Data::new(mesh)?;
    let (base_up, base_tilt) = pose(stl);
    let up = options.up.unwrap_or(base_up);
    let tilt = options.tilt_x.unwrap_or(base_tilt);
    ensure!(up == 1. || up == -1., "print up must be +1 or -1");
    ensure!(tilt.is_finite(), "print tilt must be finite");
    let source = sources::Sources::load(options.sources.as_deref(), &hash, d.tri.len());
    let mut findings = BTreeMap::new();
    for class in &options.classes {
        ensure!(
            CLASSES.contains(&class.as_str()),
            "unknown anomaly class {class}"
        );
        let mut rows = if class == "thin" {
            thin::find(&d)
        } else {
            planes::find(&d, class, up, tilt)
        }?;
        for row in &mut rows {
            row.sources = options
                .sources
                .as_ref()
                .map(|_| source.for_facets(&row.facets));
        }
        rows.sort_by(|a, b| b.score.total_cmp(&a.score));
        findings.insert(class.clone(), rows);
    }
    let mut report = Report {
        file: stl.into(),
        sha256: hash,
        facets: d.tri.len(),
        print_up: up,
        print_tilt_x_degrees: tilt,
        source_binding: source.status,
        findings,
        answered: Vec::new(),
    };
    apply_answers(&mut report);
    Ok(report)
}

fn pose(stl: &Path) -> (f64, f64) {
    let stem = stl.file_stem().and_then(|n| n.to_str()).unwrap_or("");
    let parent = stl
        .parent()
        .and_then(|p| p.file_name())
        .and_then(|n| n.to_str())
        .unwrap_or("");
    let up = if matches!(
        stem,
        "enclosure-back-top"
            | "enclosure-pump-retainer"
            | "reservoir-cap-left"
            | "reservoir-cap-right"
            | "prv-shroud"
            | "asse-inlet-cuff"
            | "asse-outlet-cuff"
            | "core"
    ) || parent == "tube-collar"
    {
        -1.
    } else {
        1.
    };
    let tilt = if matches!(stem, "faucet-shell-base" | "industrial-shell-base") {
        -hsm_faucet_numbers::shell::PRINT_BASE_BUILD_ROT.to_degrees()
    } else if stem == "nameplate-001" || parent == "rear-identification" {
        90.
    } else {
        0.
    };
    (up, tilt)
}

fn pick_points(text: &str) -> Vec<V3> {
    let mut out = Vec::new();
    for line in text.lines() {
        let line = line.trim();
        if line.starts_with("file:") || line.starts_with("solid:") {
            continue;
        }
        let words = line.split_whitespace().collect::<Vec<_>>();
        for i in 0..words.len().saturating_sub(2) {
            if i > 0 && matches!(words[i - 1], "n" | "dir" | "axis") {
                continue;
            }
            let values = ["x=", "y=", "z="].map(|axis| {
                let at = match axis {
                    "x=" => i,
                    "y=" => i + 1,
                    _ => i + 2,
                };
                words[at]
                    .strip_prefix(axis)?
                    .trim_end_matches(',')
                    .parse::<f64>()
                    .ok()
            });
            if let [Some(x), Some(y), Some(z)] = values {
                if [x, y, z].iter().all(|n| n.is_finite()) {
                    out.push(v3(x, y, z));
                }
            }
        }
    }
    out
}
fn apply_answers(report: &mut Report) {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"))
        .ancestors()
        .nth(3)
        .unwrap();
    let Ok(path) = report.file.canonicalize() else {
        return;
    };
    let Ok(rel) = path.strip_prefix(root.join("hardware/printed-parts")) else {
        return;
    };
    let path = root
        .join("hardware/printed-parts/lint-answers")
        .join(rel)
        .with_extension("lint-answers");
    let Ok(text) = std::fs::read_to_string(path) else {
        return;
    };
    let mut entries = Vec::new();
    for block in text.split("\n\n") {
        let lines = block
            .lines()
            .map(str::trim)
            .filter(|s| !s.is_empty())
            .collect::<Vec<_>>();
        let Some(first) = lines.first() else { continue };
        let Some((class, why)) = first.strip_prefix('[').and_then(|s| s.split_once(']')) else {
            continue;
        };
        let mut reason = why.trim().to_owned();
        for line in &lines[1..] {
            if line.starts_with("alternatives:")
                || (!line.contains("x=")
                    && !line.starts_with("file:")
                    && !line.starts_with("solid:"))
            {
                reason.push(' ');
                reason.push_str(line);
            }
        }
        entries.push((class.to_owned(), reason, pick_points(block)));
    }
    for (class, rows) in &mut report.findings {
        let mut keep = Vec::new();
        for mut row in rows.drain(..) {
            let points = pick_points(&row.pick.join("\n"));
            if let Some((_, why, _)) = entries.iter().find(|(kind, _, anchors)| {
                kind == class
                    && points
                        .iter()
                        .any(|p| anchors.iter().any(|a| (*p - *a).norm() <= 0.002))
            }) {
                row.answer = Some(why.clone());
                if class != "thin" && class != "ledge" {
                    report.answered.push(row);
                    continue;
                }
            }
            keep.push(row);
        }
        *rows = keep;
    }
}

/// Render findings as the viewer's Find text while keeping uncertainty in optional source maps.
pub fn print_report(report: &Report, top: usize, all: bool) {
    let count: usize = report.findings.values().map(Vec::len).sum();
    println!(
        "{} · {} printed facets · {count} findings · {} answered",
        report.file.display(),
        report.facets,
        report.answered.len()
    );
    println!("source map: {}", report.source_binding);
    let step = report.file.with_extension("step");
    let mut shown = 0;
    for class in CLASSES {
        for row in report
            .findings
            .get(class)
            .into_iter()
            .flatten()
            .take(if all {
                usize::MAX
            } else {
                top.max(3) / CLASSES.len() + 1
            })
        {
            if !all && shown >= top {
                break;
            }
            shown += 1;
            print_finding(row, &step);
        }
    }
    if all {
        for row in &report.answered {
            print_finding(row, &step);
        }
    }
}
fn print_finding(row: &Finding, step: &Path) {
    println!("\n  [{}] {}", row.class, row.line);
    let root = Path::new(env!("CARGO_MANIFEST_DIR"))
        .ancestors()
        .nth(3)
        .unwrap();
    println!(
        "    file: {}",
        step.strip_prefix(root).unwrap_or(step).display()
    );
    for line in &row.pick {
        println!("    {line}");
    }
    if let Some(sources) = &row.sources {
        let location = |value: &Value| value.as_str().unwrap_or("unknown source").to_owned();
        let lines = sources
            .iter()
            .map(|source| {
                if source.is_null() {
                    return "unknown source".into();
                }
                let op = source["op"].as_str().unwrap_or("");
                let mut line = if op.is_empty() {
                    location(&source["src"])
                } else {
                    format!("{op} at {}", location(&source["src"]))
                };
                if source["via"].is_object() {
                    let via = &source["via"];
                    line.push_str(&format!(
                        " · via {} at {}",
                        via["op"].as_str().unwrap_or(""),
                        location(&via["src"])
                    ));
                }
                line
            })
            .collect::<Vec<String>>();
        println!("    sources: {}", lines.join("; "));
    }
    if let Some(answer) = &row.answer {
        println!("    answered: {answer}");
    }
}
