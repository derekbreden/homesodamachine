//! Machine fit readings over the immutable installed fine model.
//!
//! Placement supplies frames and scalar construction ledgers. This reader owns
//! the overlap census, finite nominal mating masks, clearance ranking, drain
//! readings and scorecard. No Python geometry object enters this boundary.
#![allow(dead_code)]
#[path = "machine_check_bounds.rs"]
mod construction;
#[path = "machine_check_drain.rs"]
mod drain;
#[path = "enclosure_assembly.rs"]
mod fine;
#[path = "machine_check_geometry.rs"]
mod geometry;
#[path = "machine_check_report.rs"]
mod report;
#[path = "machine_check_routes.rs"]
mod routes;
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::{Affine, Imported, Solid, V3, face::Surface, part};
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

pub fn array(v: &Value) -> &[Value] {
    v.as_array().map(Vec::as_slice).unwrap_or(&[])
}
pub fn obj(v: &Value) -> BTreeMap<String, Value> {
    v.as_object()
        .map(|o| o.iter().map(|(k, v)| (k.clone(), v.clone())).collect())
        .unwrap_or_default()
}
pub fn num(v: &Value) -> f64 {
    v.as_f64().unwrap_or(0.)
}
pub fn string(v: &Value) -> String {
    v.as_str().unwrap_or("").to_owned()
}
pub fn strings(v: &Value) -> Vec<String> {
    array(v).iter().map(string).collect()
}
pub fn names(v: &Value) -> BTreeSet<String> {
    strings(v).into_iter().collect()
}
pub fn round(x: f64, places: i32) -> f64 {
    let k = 10_f64.powi(places);
    (x * k).round_ties_even() / k
}
pub fn vector(v: &Value) -> Result<V3> {
    let a = array(v);
    ensure!(a.len() == 3, "a point has three coordinates");
    let p = V3::from([num(&a[0]), num(&a[1]), num(&a[2])]);
    ensure!(
        [p.x, p.y, p.z].iter().all(|x| x.is_finite()),
        "a point must be finite"
    );
    Ok(p)
}
pub fn base(name: &str) -> &str {
    match name.rsplit_once('/') {
        Some((head, tail)) if !tail.is_empty() && tail.chars().all(|c| c.is_ascii_digit()) => head,
        _ => name,
    }
}
pub fn pair(a: &str, b: &str) -> (String, String) {
    if a <= b {
        (a.to_owned(), b.to_owned())
    } else {
        (b.to_owned(), a.to_owned())
    }
}
pub fn pretty(v: f64) -> String {
    if v.fract() == 0. {
        format!("{v:.0}")
    } else {
        v.to_string()
    }
}
pub fn bounds(s: &Solid) -> [f64; 6] {
    let b = s.bounds();
    [b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z]
}
pub fn box_gap(a: &[f64; 6], b: &[f64; 6]) -> f64 {
    (0..3)
        .map(|i| (a[i] - b[i + 3]).max(b[i] - a[i + 3]).max(0.).powi(2))
        .sum::<f64>()
        .sqrt()
}
pub fn overlap(a: &[f64; 6], b: &[f64; 6], margin: f64) -> bool {
    !(0..3).any(|i| a[i + 3] + margin < b[i] || b[i + 3] + margin < a[i])
}
#[derive(Clone)]
pub struct Group {
    pub name: String,
    pub indices: Vec<usize>,
    pub bounds: [f64; 6],
}
pub struct World {
    pub parts: Vec<Imported>,
    pub groups: Vec<Group>,
    pub index: BTreeMap<String, usize>,
    pub populations: [Vec<String>; 3],
    pub role: Vec<(String, usize, String)>,
    pub models: BTreeMap<String, Value>,
}
impl World {
    pub fn load(spec: &Value) -> Result<Self> {
        let physical = spec
            .get("physical_model")
            .or_else(|| spec.get("model"))
            .and_then(Value::as_str)
            .context("checks need the physical fine model")?;
        let mut models = BTreeMap::new();
        let envelope = &spec["envelope"];
        let mut inputs = vec![("physical", json!({"model":physical}))];
        if let Some(wire) = spec.get("wiring_model").and_then(Value::as_str) {
            inputs.push(("wiring", json!({"model":wire})));
        }
        let env_path = envelope
            .get("model")
            .or_else(|| envelope.get("path"))
            .and_then(Value::as_str)
            .context("checks need the exact casing model")?;
        let frame = fine::transform(envelope.get("transform"))?.unwrap_or(Affine::IDENTITY);
        ensure!(
            (frame.det() - 1.).abs() <= 1e-10,
            "casing frame must be rigid"
        );
        for i in 0..3 {
            for j in 0..3 {
                let dot = (0..3).map(|k| frame.m[i][k] * frame.m[j][k]).sum::<f64>();
                ensure!(
                    (dot - if i == j { 1. } else { 0. }).abs() <= 1e-10,
                    "casing frame must be rigid"
                );
            }
        }
        inputs.push((
            "envelope",
            json!({"model":env_path,"name":"foam-assembly","transform":envelope["transform"]}),
        ));
        let aliases = obj(&spec["aliases"]);
        let mut parts = Vec::new();
        let mut role = Vec::new();
        let mut groups: Vec<Group> = Vec::new();
        let mut index = BTreeMap::new();
        for (kind, instance) in inputs {
            let mut raw_instance = instance.clone();
            if kind == "envelope" {
                raw_instance.as_object_mut().unwrap().remove("name");
            }
            let local = fine::assemble(&json!([raw_instance]))?;
            for (entry, mut part) in local.into_iter().enumerate() {
                let qualified = part.name.clone();
                if kind == "envelope" {
                    part.name = "foam-assembly".to_owned();
                }
                let name = if kind == "envelope" {
                    "foam-assembly".to_owned()
                } else if kind == "physical" {
                    aliases
                        .get(base(&part.name))
                        .map(string)
                        .unwrap_or_else(|| base(&part.name).to_owned())
                } else {
                    base(&part.name).to_owned()
                };
                let bb = bounds(&part.solid);
                let at = parts.len();
                let g = *index.entry(name.clone()).or_insert_with(|| {
                    groups.push(Group {
                        name: name.clone(),
                        indices: Vec::new(),
                        bounds: bb,
                    });
                    groups.len() - 1
                });
                groups[g].indices.push(at);
                for i in 0..3 {
                    groups[g].bounds[i] = groups[g].bounds[i].min(bb[i]);
                    groups[g].bounds[i + 3] = groups[g].bounds[i + 3].max(bb[i + 3]);
                }
                role.push((kind.to_owned(), entry, qualified));
                parts.push(part);
            }
            models.insert(kind.to_owned(), instance);
        }
        let metadata = &spec["metadata"];
        let mut populations: [Vec<String>; 3] = Default::default();
        if let Some(given) = metadata.get("populations").and_then(Value::as_array) {
            ensure!(
                given.len() == 3,
                "populations are bodies, tubes, printed pieces"
            );
            for i in 0..3 {
                populations[i] = strings(&given[i]);
            }
        } else {
            let core = names(&metadata["core_body_names"]);
            let ext = names(&metadata["core_external_names"]);
            let wires = names(&metadata["wiring_names"]);
            for g in &groups {
                if wires.contains(&g.name)
                    || g.name.rsplit('/').next().unwrap_or("").starts_with("wire-")
                {
                    continue;
                }
                if core.contains(&g.name) && !ext.contains(g.name.rsplit('/').next().unwrap_or(""))
                {
                    continue;
                }
                // Internal cold-core names are omitted from pack questions but remain
                // in the authoritative world used by the dedicated drain reading.
                if g.name.starts_with("cold-core/")
                    && !ext.contains(g.name.rsplit('/').next().unwrap_or(""))
                {
                    continue;
                }
                let population = if g.name.starts_with("enclosure-") {
                    2
                } else if ["tube-", "turn-", "step-", "stub-"]
                    .iter()
                    .any(|p| g.name.starts_with(p))
                {
                    1
                } else {
                    0
                };
                populations[population].push(g.name.clone());
            }
        }
        for n in populations.iter().flatten() {
            ensure!(index.contains_key(n), "unknown population member {n}");
        }
        Ok(Self {
            parts,
            groups,
            index,
            populations,
            role,
            models,
        })
    }
    pub fn g(&self, n: &str) -> Result<&Group> {
        self.index
            .get(n)
            .map(|&i| &self.groups[i])
            .with_context(|| format!("unknown fine member {n}"))
    }
    pub fn operand(&self, n: &str) -> Result<Value> {
        Ok(json!(self.g(n)?.indices))
    }
    pub fn measure(&mut self, queries: Vec<Value>) -> Result<Vec<Value>> {
        let result = fine::retained_query(
            &mut self.parts,
            &json!(queries),
            fine::SearchRetention {
                array_bytes: 64 * 1024 * 1024,
                reuse_queries: 64,
            },
        );
        // A later phase may ask about any raw member again. It receives those
        // exact arrays, not native search state left by an earlier question.
        self.forget_search();
        result
    }
    pub fn forget_search(&mut self) {
        for part in &mut self.parts {
            part.solid.forget_backend();
        }
    }
    pub fn retain_raw(&mut self, needed: &BTreeSet<usize>) {
        for (i, part) in self.parts.iter_mut().enumerate() {
            if !needed.contains(&i) {
                part.solid = Solid::empty();
            }
        }
    }
    pub fn solid(&self, n: &str) -> Result<Solid> {
        let g = self.g(n)?;
        if g.indices.len() == 1 {
            return Ok(self.parts[g.indices[0]].solid.clone());
        }
        Solid::union_all(
            &g.indices
                .iter()
                .map(|&i| self.parts[i].solid.clone())
                .collect::<Vec<_>>(),
        )
    }
    pub fn q(&self, kind: &str, a: &str, b: &str) -> Result<Value> {
        Ok(
            json!({"kind":kind,"a":self.operand(a)?,"b":self.operand(b)?,"retain_until_last_use":true}),
        )
    }
}

fn cylinder(radius: f64, start: V3, direction: V3, length: f64, margin: bool) -> Result<Solid> {
    let m = if margin { 1e-6 } else { 0. };
    Solid::cylinder(
        start - direction * m,
        direction,
        radius + m,
        length + 2. * m,
    )
}
fn annulus(
    inner: f64,
    outer: f64,
    start: V3,
    direction: V3,
    length: f64,
    margin: bool,
) -> Result<Solid> {
    cylinder(outer, start, direction, length, margin)?
        .cut(&cylinder(inner, start, direction, length, margin)?)
}
fn inverse_rigid(frame: Affine) -> Affine {
    let mut m = [[0.; 4]; 3];
    for i in 0..3 {
        for j in 0..3 {
            m[i][j] = frame.m[j][i];
        }
        m[i][3] = -(0..3).map(|j| m[i][j] * frame.m[j][3]).sum::<f64>();
    }
    Affine { m }
}
fn stem_region(solid: &Solid, profile: &Value, reducer: bool) -> Result<Solid> {
    let radius = if reducer {
        3.175
    } else {
        num(&profile["stem_od_mm"]) / 2.
    };
    let mut axis = None;
    let mut ts = Vec::new();
    for (fi, face) in solid.faces().iter().enumerate() {
        if let Surface::Cylinder { p, d, r, .. } = face.surface {
            if (r - radius).abs() >= 1e-3 {
                continue;
            }
            let triangles = solid
                .tris()
                .iter()
                .zip(solid.face_of())
                .filter(|(_, f)| **f as usize == fi)
                .map(|(tri, _)| tri)
                .collect::<Vec<_>>();
            let verts = triangles
                .iter()
                .flat_map(|tri| tri.iter().map(|&i| solid.verts()[i as usize]))
                .collect::<Vec<_>>();
            if verts.is_empty() {
                continue;
            }
            if !reducer {
                let off = (verts[0] - p) - d * (verts[0] - p).dot(d);
                let tri = triangles[0];
                let a = solid.verts()[tri[0] as usize];
                let b = solid.verts()[tri[1] as usize];
                let c = solid.verts()[tri[2] as usize];
                if (b - a).cross(c - a).dot(off) <= 0. {
                    continue;
                }
            }
            let (o, dir) = *axis.get_or_insert((p, d));
            ts.extend(verts.into_iter().map(|v| (v - o).dot(dir)));
        }
    }
    let (o, d) = axis.context("selected stem has no outer cylindrical land")?;
    let lo = ts.iter().copied().fold(f64::INFINITY, f64::min);
    let hi = ts.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    if reducer {
        return cylinder(radius + 0.01, o + d * (lo - 0.01), d, hi - lo + 0.02, false);
    }
    let profile = array(&profile["profiles"]["stem_x"]);
    let straight = profile
        .iter()
        .filter(|v| (num(&v[1]) - radius).abs() < 1e-6)
        .map(|v| num(&v[0]))
        .collect::<Vec<_>>();
    let tip = straight.iter().copied().fold(f64::INFINITY, f64::min) - num(&profile[0][0]);
    let end = profile
        .iter()
        .filter(|v| num(&v[0]) < 0. && num(&v[1]) > radius)
        .map(|v| num(&v[0]))
        .fold(f64::NEG_INFINITY, f64::max);
    let root = end - straight.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    let r = profile
        .iter()
        .filter(|v| num(&v[0]) <= end)
        .map(|v| num(&v[1]))
        .fold(0., f64::max);
    let stem = cylinder(
        radius + 0.01,
        o + d * (lo - tip - 0.01),
        d,
        hi - lo + 2. * tip + 0.02,
        false,
    )?;
    let center = (solid.centroid() - o).dot(d);
    let outward = if (center - hi).abs() < (center - lo).abs() {
        1.
    } else {
        -1.
    };
    let cap = if outward > 0. { hi } else { lo };
    stem.union(&cylinder(
        r + 0.01,
        o + d * (cap - outward * 0.01),
        d * outward,
        root + 0.02,
        false,
    )?)
}

fn main() -> Result<()> {
    let (numbers, output) = part::args()?;
    ensure!(
        output == std::path::Path::new("--check"),
        "machine-checks returns readings and writes no models"
    );
    let request = numbers.get("request")?;
    let mut world = World::load(request)?;
    let mut result = json!({});
    let mode = request.get("mode").and_then(Value::as_str).unwrap_or("all");
    if mode == "construction" {
        println!("{}", construction::construction_only(&mut world, request)?);
        return Ok(());
    }
    if mode == "clearance" {
        println!("{}", report::clearance_only(&mut world, request)?);
        return Ok(());
    }
    if mode != "drain" {
        result = report::build(&mut world, request)?;
    }
    if mode != "scorecard" && request.get("drain").and_then(Value::as_bool) != Some(false) {
        result["drain"] = drain::final_read(&mut world, request)?;
    }
    println!("{result}");
    Ok(())
}
