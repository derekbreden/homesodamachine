//! The tip audit measures the Sculpted tip's deposited courses on a sliced plate against the tip's
//! mesh in its warp's pose: each course's incline and fit to the warp's field, the waterways'
//! clear passages, the support contacts under the nose and shoulders, and the backing the mating
//! shoulder's beads have from the courses laid before them.
//!
//! It reads nominal centerlines and modeled bead sections, so its readings are of the plate's
//! paths, not of the print.

use crate::course_field::{distance, mix, ShoulderHold};
use crate::mesh::{bounds, Mesh};
use crate::tip_warp::CANONICAL_POINT;
use crate::{apply, gcode, sha256_hex};
use anyhow::{ensure, Context, Result};
use hsm_faucet_numbers::{paths, shell};
use serde_json::{json, Value};
use std::collections::{BTreeMap, HashMap};
use std::path::Path;
use std::rc::Rc;

type P = [f64; 3];
/// The tip's object on the plate.
const TIP: i64 = 1902;
/// How far above a support road the audit looks for the tip's underside.
const SUPPORT_SEARCH: f64 = 2.;
/// The flow ratio and bridge flow the slicer's nominal bead sections are read back with.
const NOMINAL_FLOW: f64 = 0.9555;
const NOMINAL_BRIDGE_MULTIPLIER: f64 = 1.25;
/// How far inside a bead's modeled section a passage sample must lie to count as stock.
const PROBE_MARGIN: f64 = 0.01;

fn add(a: P, b: P) -> P {
    std::array::from_fn(|i| a[i] + b[i])
}
fn sub(a: P, b: P) -> P {
    std::array::from_fn(|i| a[i] - b[i])
}
fn scale(a: P, s: f64) -> P {
    a.map(|v| v * s)
}
fn dot(a: P, b: P) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}
fn cross(a: P, b: P) -> P {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}
fn unit(a: P) -> P {
    scale(a, 1. / dot(a, a).sqrt())
}
fn cell(x: f64, y: f64) -> (i32, i32) {
    (x.floor() as i32, y.floor() as i32)
}

struct Bead {
    a: P,
    b: P,
    width: f64,
    height: f64,
    kind: Rc<str>,
    u: f64,
}

impl Bead {
    fn section(&self, x: f64, y: f64) -> Option<[f64; 2]> {
        let d = sub(self.b, self.a);
        let xy2 = d[0] * d[0] + d[1] * d[1];
        if xy2 <= 1e-12 {
            return None;
        }
        let t = (((x - self.a[0]) * d[0] + (y - self.a[1]) * d[1]) / xy2).clamp(0., 1.);
        let p = mix(self.a, self.b, t);
        let r = self.width * 0.5;
        let away = (p[0] - x).hypot(p[1] - y);
        if away >= r {
            return None;
        }
        let flat = (0.5 * (self.width - self.height)).max(0.);
        let curl = ((away - flat) / (r - flat).max(1e-8)).clamp(0., 1.);
        let half = 0.5 * self.height;
        let chord = half * (1. - curl * curl).sqrt();
        Some([p[2] - half - chord, p[2] - half + chord])
    }

    fn normal_ray(&self, p: P, n: P, low: f64, high: f64) -> Option<f64> {
        let ap = dot(sub(p, self.a), n);
        let bp = dot(sub(p, self.b), n);
        let side = n[1].abs() * self.width * 0.5 + 1e-6;
        let low = low.max(ap.min(bp) - side);
        let high = high.min(ap.max(bp) + side + n[2] * self.height);
        if high <= low {
            return None;
        }
        let inside = |t: f64| {
            let spot = sub(p, scale(n, t));
            self.section(spot[0], spot[1]).is_some_and(|[l, h]| (l..=h).contains(&spot[2]))
        };
        let steps = ((high - low) / 0.025).ceil() as usize;
        let mut vacant = low;
        for i in 0..=steps {
            let t = low + (high - low) * i as f64 / steps as f64;
            if inside(t) {
                let mut occupied = t;
                for _ in 0..12 {
                    let mid = 0.5 * (vacant + occupied);
                    if inside(mid) {
                        occupied = mid;
                    } else {
                        vacant = mid;
                    }
                }
                return Some(occupied);
            }
            vacant = t;
        }
        None
    }
}

struct ContactRay {
    length: f64,
    gap: Option<f64>,
    feature: Rc<str>,
    sample: P,
    u: f64,
}

/// The mating shoulder's beads and the earlier stock under each, along the bearing plane's normal.
struct ShoulderBacking {
    p: P,
    n: P,
    v: P,
    shoulder_u: f64,
    stock: Vec<Bead>,
    bins: HashMap<(i32, i32), Vec<usize>>,
    traces: BTreeMap<(Rc<str>, i64, bool), Vec<ContactRay>>,
}

impl ShoulderBacking {
    fn new(field: &ShoulderHold) -> Self {
        let n = unit([0., field.tangent, 1.]);
        Self {
            p: field.shoulder,
            n,
            v: [0., n[2], -n[1]],
            shoulder_u: field.shoulder[2],
            stock: Vec::new(),
            bins: HashMap::new(),
            traces: BTreeMap::new(),
        }
    }

    fn trace(&mut self, bead: &Bead, rays: &MeshRays) {
        let a_u = dot(sub(bead.a, self.p), self.n);
        let b_u = dot(sub(bead.b, self.p), self.n);
        if a_u.max(b_u) < -1.65 || a_u.min(b_u) > 0.75 || bead.height < 0.025 {
            return;
        }
        let support = is_support(&bead.kind);
        let width = bead.width;
        if !support
            && a_u.min(b_u) <= 0.34
            && a_u.max(b_u) >= -0.01
            && (self.shoulder_u - 0.03..=self.shoulder_u + 0.26).contains(&bead.u)
            && gcode::MODEL.contains(&bead.kind.as_ref())
        {
            let length = distance(bead.a, bead.b);
            let count = ((length / 0.12).ceil() as usize).max(1);
            let d = sub(bead.b, bead.a);
            let lateral = unit([-d[1], d[0], 0.]);
            for i in 0..count {
                // The centerline and a point to each side of it read backing under one side of a bead.
                let mid = mix(bead.a, bead.b, (i as f64 + 0.5) / count as f64);
                for fraction in [-0.25, 0., 0.25] {
                    let point = add(mid, scale(lateral, width * fraction));
                    let near = dot(sub(point, self.p), self.n);
                    if !(-0.01..=0.34).contains(&near) {
                        continue;
                    }
                    let on = add(point, scale(self.n, -near));
                    if !rays.hits(on[0], on[1]).iter().any(|(z, n)| (*z - on[2]).abs() < 0.045 && dot(*n, self.n) < -0.995) {
                        continue;
                    }
                    let Some([z, _]) = bead.section(point[0], point[1]) else { continue };
                    let bottom = [point[0], point[1], z];
                    let base = dot(sub(bottom, self.p), self.n);
                    if !(-0.24..=0.14).contains(&base) {
                        continue;
                    }
                    let uv = self.uv(bottom);
                    let cell = cell(uv[0], uv[1]);
                    let local = add(sub(on, self.p), scale(self.v, -4.024));
                    let tool_release = local[0].abs() > 0.3 && dot(local, self.v).abs() <= 0.0699268 * local[0].abs();
                    let mut gap = None;
                    let mut material = Rc::from("none");
                    if let Some(plate) = self.bins.get(&cell) {
                        for &i in plate {
                            let stock = &self.stock[i];
                            if stock.u >= bead.u - 0.04 {
                                continue;
                            }
                            let Some(next) = stock.normal_ray(bottom, self.n, -0.45, gap.unwrap_or(1.5)) else { continue };
                            gap = Some(next);
                            material = stock.kind.clone();
                        }
                    }
                    let key = (bead.kind.clone(), (bead.u * 10000.).round() as i64, tool_release);
                    self.traces.entry(key).or_default().push(ContactRay {
                        length: length / count as f64 / 3.,
                        gap,
                        feature: material,
                        sample: bottom,
                        u: bead.u,
                    });
                }
            }
        }
    }

    fn uv(&self, p: P) -> [f64; 2] {
        [p[0], dot(sub(p, self.p), self.v)]
    }

    fn observe(&mut self, bead: Bead, rays: &MeshRays) {
        let aa = dot(sub(bead.a, self.p), self.n);
        let bb = dot(sub(bead.b, self.p), self.n);
        if aa.max(bb) < -1.85 || aa.min(bb) > 0.76 || bead.height < 0.025 {
            return;
        }
        self.trace(&bead, rays);
        let a = self.uv(bead.a);
        let b = self.uv(bead.b);
        let r = bead.width * 0.5 + bead.height * self.n[1].abs();
        let lo = cell(a[0].min(b[0]) - r, a[1].min(b[1]) - r);
        let hi = cell(a[0].max(b[0]) + r, a[1].max(b[1]) + r);
        for u in lo.0..=hi.0 {
            for v in lo.1..=hi.1 {
                self.bins.entry((u, v)).or_default().push(self.stock.len());
            }
        }
        self.stock.push(bead);
    }

    fn report(&self) -> Value {
        let mut features: BTreeMap<&str, Vec<&ContactRay>> = BTreeMap::new();
        let summarize = |probes: &[&ContactRay]| {
            let mut kinds: BTreeMap<&str, [f64; 4]> = BTreeMap::new();
            let mut finite = Vec::new();
            let mut tight: Vec<_> = probes.iter().filter(|r| r.gap.is_some_and(|g| g < 0.)).collect();
            tight.sort_by(|a, b| a.gap.unwrap_or(0.).total_cmp(&b.gap.unwrap_or(0.)));
            let full = probes.iter().map(|r| r.length).sum::<f64>();
            for r in probes {
                let hit = kinds.entry(&r.feature).or_default();
                hit[0] += r.length;
                if let Some(g) = r.gap {
                    finite.push(g);
                    if g <= 0.28 {
                        hit[1] += r.length;
                    }
                    if g <= 0.34 {
                        hit[2] += r.length;
                    }
                    if g < 0. {
                        hit[3] += r.length;
                    }
                }
            }
            finite.sort_by(f64::total_cmp);
            let pct = |q: f64| finite.get((q * finite.len().saturating_sub(1) as f64).round() as usize).copied();
            json!({"sampled_road_mm": full,
                "coverage_within_0p28": kinds.values().map(|k| k[1]).sum::<f64>() / full,
                "coverage_within_0p34": kinds.values().map(|k| k[2]).sum::<f64>() / full,
                "length_by_stock_feature_mm": kinds.into_iter()
                    .map(|(k, v)| (k, json!({"total": v[0], "within_0p28": v[1], "within_0p34": v[2], "touching": v[3]})))
                    .collect::<BTreeMap<_, _>>(),
                "finite_gap_quantiles_mm": [pct(0.), pct(0.1), pct(0.5), pct(0.9), pct(1.)],
                "overlap_witnesses": tight.into_iter().take(5)
                    .map(|r| json!({"bottom_xyz_mm": r.sample, "previous_feature": r.feature.as_ref(), "gap_mm": r.gap, "virtual_z_mm": r.u}))
                    .collect::<Vec<_>>()})
        };
        let mut by_course = Vec::new();
        for ((kind, u, slot), rays) in &self.traces {
            features.entry(kind).or_default().extend(rays.iter());
            by_course.push(json!({"feature": kind.as_ref(), "virtual_z_mm": *u as f64 / 10000., "release_slot": slot,
                "backing": summarize(&rays.iter().collect::<Vec<_>>())}));
        }
        json!({"sample_step_mm": 0.12, "normal": self.n,
            "scope": "Ray intersection from deposited bead underside with previously laid bead solids in a different course. The largest finite search is 1.5 mm.",
            "by_course": by_course,
            "by_feature": features.iter().map(|(k, r)| (*k, summarize(r))).collect::<BTreeMap<_, _>>()})
    }
}

/// The tip's pose on the plate, from its warp receipt.
struct Pose {
    rotation: [[f64; 3]; 3],
    inverse: [[f64; 3]; 3],
    shift: P,
}

impl Pose {
    fn new(receipt: &Value) -> Result<Self> {
        let rotation: [[f64; 3]; 3] =
            serde_json::from_value(receipt["physical_rotation"].clone()).context("the warp's physical_rotation")?;
        let inverse = std::array::from_fn(|i| std::array::from_fn(|j| rotation[j][i]));
        let shift = serde_json::from_value(receipt["physical_cad_to_plate_translation"].clone())
            .context("the warp's physical_cad_to_plate_translation")?;
        Ok(Self { rotation, inverse, shift })
    }

    fn placed(&self, p: P) -> P {
        add(apply(&self.rotation, p), self.shift)
    }

    fn cad(&self, p: P) -> P {
        apply(&self.inverse, sub(p, self.shift))
    }
}

struct Facet {
    xyz: [P; 3],
    normal: P,
}

/// The placed mesh's facets, binned in plan for vertical rays.
struct MeshRays {
    mesh_box: [P; 2],
    facets: Vec<Facet>,
    bins: HashMap<(i32, i32), Vec<usize>>,
}

impl MeshRays {
    fn new(source: &Mesh, pose: &Pose) -> Self {
        let placed: Vec<_> = source.vertices.iter().map(|&p| pose.placed(p)).collect();
        let (low, high) = bounds(&placed);
        let mut facets = Vec::new();
        let mut bins: HashMap<(i32, i32), Vec<usize>> = HashMap::new();
        for row in &source.faces {
            let xyz = row.map(|i| placed[i]);
            let n = cross(sub(xyz[1], xyz[0]), sub(xyz[2], xyz[0]));
            if n[2].abs() <= 1e-10 {
                continue;
            }
            let (a, b) = bounds(&xyz);
            let from = cell(a[0], a[1]);
            let to = cell(b[0], b[1]);
            for x in from.0..=to.0 {
                for y in from.1..=to.1 {
                    bins.entry((x, y)).or_default().push(facets.len());
                }
            }
            facets.push(Facet { xyz, normal: unit(n) });
        }
        Self { mesh_box: [low, high], facets, bins }
    }

    /// Every facet a vertical line through `x`, `y` crosses: its height and the facet's normal,
    /// lowest first.
    fn hits(&self, x: f64, y: f64) -> Vec<(f64, P)> {
        let mut out = Vec::new();
        if let Some(bin) = self.bins.get(&cell(x, y)) {
            for &index in bin {
                let Facet { xyz: [a, b, c], normal } = self.facets[index];
                let p = sub(b, a);
                let q = sub(c, a);
                let r = [x - a[0], y - a[1], 0.0];
                let det = p[0] * q[1] - p[1] * q[0];
                if det.abs() <= 1e-10 {
                    continue;
                }
                let t = (r[0] * q[1] - r[1] * q[0]) / det;
                let u = (p[0] * r[1] - p[1] * r[0]) / det;
                if t >= -1e-8 && u >= -1e-8 && t + u <= 1. + 1e-8 {
                    out.push((a[2] + t * p[2] + u * q[2], normal));
                }
            }
        }
        out.sort_unstable_by(|a, b| a.0.total_cmp(&b.0));
        out.dedup_by(|a, b| (a.0 - b.0).abs() < 1e-6);
        out
    }
}

struct Probe {
    path: &'static str,
    depth: f64,
    radius: f64,
    pos: P,
    cad_open: bool,
    model: bool,
    support: bool,
}

/// Sample points down the waterways and the drain vent, each marked once a bead's section holds it.
struct Probes {
    samples: Vec<Probe>,
    bins: HashMap<(i32, i32), Vec<usize>>,
}

impl Probes {
    fn new(pose: &Pose, rays: &MeshRays) -> Self {
        let mut out = Self { samples: Vec::new(), bins: HashMap::new() };
        let mut cylinder = |name, center, axes: [P; 3], depths: &[f64], radii: &[f64]| {
            for &depth in depths {
                for &radius in radii {
                    let count = if radius > 0. { 64 } else { 1 };
                    for s in 0..count {
                        let angle = s as f64 * std::f64::consts::TAU / count as f64;
                        let shift = add(scale(axes[0], radius * angle.cos()), scale(axes[1], radius * angle.sin()));
                        let pos = pose.placed(add(add(center, scale(axes[2], depth)), shift));
                        let cad_open = rays.hits(pos[0], pos[1]).into_iter().filter(|(z, _)| *z > pos[2] + 0.001).count() % 2 == 0;
                        out.bins.entry(cell(pos[0], pos[1])).or_default().push(out.samples.len());
                        out.samples.push(Probe { path: name, depth, radius, pos, cad_open, model: false, support: false });
                    }
                }
            }
        };
        let [exit, into, front] = shell::tip_frame();
        let section = [0.1, 0.3, 0.5, 0.75, 1., 1.25, 1.5, 1.75, 2., 2.25, 2.5, 3., 4.];
        let e_x = [1., 0., 0.];
        for (i, [x, n, r]) in shell::beverage_circles().into_iter().enumerate() {
            let name = ["water", "flavor left", "flavor right"][i];
            let center = add(exit, add(scale(e_x, x), scale(front, n)));
            cylinder(name, center, [e_x, front, into], &section, &[0., r * 0.5, r * 0.75, r * 0.9, r]);
        }
        let (origin, normal, _) = shell::vent_outlet();
        let mouth = add(origin, scale(normal, shell::TUBE_SHELL_OUTER_R));
        let vent_depth: Vec<_> = (-16..=0).map(|d| d as f64 * 0.5).collect();
        cylinder("drain vent", mouth, [e_x, cross(e_x, normal), normal], &vent_depth, &[0., 0.5, 1., 1.4, 1.7, 1.85]);
        out
    }

    fn record(&mut self, a: P, b: P, width: f64, height: f64, is_support: bool) {
        let r = width * 0.5;
        let low = cell(a[0].min(b[0]) - r, a[1].min(b[1]) - r);
        let high = cell(a[0].max(b[0]) + r, a[1].max(b[1]) + r);
        let p = sub(b, a);
        let len = p[0] * p[0] + p[1] * p[1];
        if len <= 1e-9 || height <= PROBE_MARGIN {
            return;
        }
        for x in low.0..=high.0 {
            for y in low.1..=high.1 {
                let Some(index) = self.bins.get(&(x, y)) else { continue };
                for &i in index {
                    let q = &mut self.samples[i];
                    if !q.cad_open
                        || (if is_support { q.support } else { q.model })
                        || q.pos[2] < a[2].min(b[2]) - height
                        || q.pos[2] > a[2].max(b[2])
                    {
                        continue;
                    }
                    let rel = sub(q.pos, a);
                    let at = ((rel[0] * p[0] + rel[1] * p[1]) / len).clamp(0., 1.);
                    let offset = (rel[0] - at * p[0]).hypot(rel[1] - at * p[1]);
                    if offset > r - PROBE_MARGIN {
                        continue;
                    }
                    let flat = ((width - height) * 0.5).max(0.);
                    let curve = ((offset - flat) / (r - flat).max(1e-8)).clamp(0., 1.);
                    let top = 0.5 * height * (1. - curve * curve).sqrt();
                    let over = rel[2] - at * p[2] + 0.5 * height;
                    if over.abs() <= top - PROBE_MARGIN {
                        if is_support {
                            q.support = true
                        } else {
                            q.model = true
                        }
                    }
                }
            }
        }
    }

    fn report(&self) -> Value {
        let mut areas: BTreeMap<&str, BTreeMap<(i32, i32), [usize; 4]>> = BTreeMap::new();
        for q in &self.samples {
            let hit = areas.entry(q.path).or_default()
                .entry(((q.depth * 10000.).round() as i32, (q.radius * 10000.).round() as i32))
                .or_default();
            hit[0] += 1;
            hit[1] += usize::from(q.cad_open);
            hit[2] += usize::from(q.model);
            hit[3] += usize::from(q.support);
        }
        json!(areas.into_iter().map(|(name, cells)| {
            let mut per_depth: BTreeMap<i32, Vec<Value>> = BTreeMap::new();
            for ((depth, radius), [n, open, model, support]) in cells {
                per_depth.entry(depth).or_default().push(json!({"radius_mm": radius as f64 / 10000., "samples": n, "cad_open": open,
                    "model_stock_samples": model, "removable_support_stock_samples": support}));
            }
            let levels: Vec<_> = per_depth.into_iter().map(|(depth, rings)| json!({"axial_mm": depth as f64 / 10000., "rings": rings})).collect();
            (name, levels)
        }).collect::<BTreeMap<_, _>>())
    }
}

fn is_support(feature: &str) -> bool {
    gcode::SUPPORT.contains(&feature) || feature == "Support base"
}

/// The part of the nose a support contact meets, from its CAD point and facet normal.
fn nose_zone(hit: P, normal: P, [exit, into, out]: [P; 3]) -> Option<&'static str> {
    let delta = sub(hit, exit);
    let s = dot(delta, into);
    let n = dot(delta, out);
    let r = delta[0].hypot(n - shell::TUBE_SHELL_CENTER_Y);
    if !(-0.15..=30.).contains(&s) {
        return None;
    }
    if (s - shell::DISPENSE_FACE_THICKNESS).abs() < 0.06 && dot(normal, into) > 0.995 {
        Some("painted inner face")
    } else if s <= 26.5 && (r - shell::TUBE_SHELL_OUTER_R).abs() < 0.18 && dot(normal, into).abs() < 0.15 {
        Some("exterior barrel")
    } else if s <= 3. && r > 9. {
        Some("dispense lip")
    } else if s <= 10. {
        Some("outlet and blends")
    } else {
        Some("other nose ledge")
    }
}

fn contact_footprint(contact_grid: &BTreeMap<(&'static str, i32, i32), f64>) -> BTreeMap<&'static str, Value> {
    let mut by_zone: BTreeMap<&str, Vec<f64>> = BTreeMap::new();
    for (&(zone, _, _), &gap) in contact_grid {
        by_zone.entry(zone).or_default().push(gap);
    }
    by_zone.into_iter().map(|(zone, mut gaps)| {
        gaps.sort_by(f64::total_cmp);
        let quantile = |at: f64| gaps[((gaps.len() - 1) as f64 * at).round() as usize];
        (zone, json!({"distinct_support_interface_cells": gaps.len(),
            "xy_sampling_cell_mm": 0.25, "normal_gap_quantiles_mm": [quantile(0.), quantile(0.1), quantile(0.5), quantile(0.9), quantile(1.)],
            "cells_at_or_below_0p15mm": gaps.iter().filter(|v| **v <= 0.15).count(),
            "cells_0p15_to_0p35mm": gaps.iter().filter(|v| **v > 0.15 && **v <= 0.35).count(),
            "cells_above_0p35mm": gaps.iter().filter(|v| **v > 0.35).count()}))
    }).collect()
}

fn footprint(contact_grid: &mut BTreeMap<(&'static str, i32, i32), f64>, zone: &'static str, point: P, desired_gap: f64) {
    let key = (zone, (point[0] * 4.).floor() as i32, (point[1] * 4.).floor() as i32);
    contact_grid.entry(key).and_modify(|v| *v = v.min(desired_gap)).or_insert(desired_gap);
}

/// The shallow outer dispense barrel's wall roads of one feature.
#[derive(Default)]
struct NoseWall {
    road_mm: f64,
    line_width_mm: f64,
    at_z: Option<[f64; 2]>,
    flow_mm3_per_mm: f64,
    steepest_run_thickness_mm: f64,
    one_world_road: [P; 2],
    smallest_local_incline: f64,
}

impl NoseWall {
    fn note(&mut self, length: f64, width: f64, height: f64, a: P, b: P, world_incline: f64) {
        self.road_mm += length;
        self.line_width_mm += length * width;
        self.flow_mm3_per_mm += length * height;
        let range = self.at_z.get_or_insert([a[2], b[2]]);
        range[0] = range[0].min(a[2].min(b[2]));
        range[1] = range[1].max(a[2].max(b[2]));
        if self.one_world_road == [[0.; 3]; 2] || world_incline < self.smallest_local_incline {
            self.one_world_road = [a, b];
            self.smallest_local_incline = world_incline;
            self.steepest_run_thickness_mm = height;
        }
    }

    fn json(&self) -> Value {
        json!({"road_mm": self.road_mm, "mean_width_mm": (self.road_mm > 0.).then(|| self.line_width_mm / self.road_mm),
            "mean_bead_height_mm": (self.road_mm > 0.).then(|| self.flow_mm3_per_mm / self.road_mm),
            "world_z_range_mm": self.at_z, "shallowest_local_incline_degrees": self.smallest_local_incline,
            "height_at_shallowest_run_mm": self.steepest_run_thickness_mm, "one_world_road_mm": self.one_world_road})
    }
}

/// Support roads under one zone of the tip, and their gaps to it.
#[derive(Default)]
struct Contact {
    traced_mm: f64,
    gap_sum: f64,
    max_gap: f64,
    max_overlap: f64,
    first: P,
}

impl Contact {
    fn note(&mut self, length: f64, gap: f64, hit: P) {
        if self.traced_mm == 0. {
            self.first = hit;
        }
        self.traced_mm += length;
        self.gap_sum += length * gap;
        self.max_gap = self.max_gap.max(gap);
        self.max_overlap = self.max_overlap.max(-gap);
    }

    fn json(&self) -> Value {
        json!({"traced_road_mm": self.traced_mm, "mean_gap_mm": self.gap_sum / self.traced_mm,
            "largest_vertical_gap_mm": self.max_gap, "deepest_nominal_overlap_mm": self.max_overlap, "first_cad_hit_mm": self.first})
    }
}

/// A course group's markers, from its layer's comments.
#[derive(Default)]
struct Meta<'a> {
    group: &'a str,
    phase: &'a str,
    u: Option<f64>,
    course: Option<i32>,
}

/// One course's roads and how closely they follow the warp's field.
#[derive(Default)]
struct Pitch {
    model_mm: f64,
    support_mm: f64,
    interface_mm: f64,
    first_layer_model_mm: f64,
    first_layer_support_mm: f64,
    dy_dz: f64,
    dy2: f64,
    residual: f64,
    residual_filter_mm: f64,
    lateral_weight: f64,
    z_range: Option<[f64; 2]>,
    group_label: String,
}

fn maxabs_pair(a: f64, b: f64) -> f64 {
    a.abs().max(b.abs())
}

/// The audit of the tip mesh `stl` in the pose of `warp`, on the plate in `tape`: a sliced
/// archive, or its plate's G-code.
pub fn audit(stl: &Path, warp: &Path, tape: &Path) -> Result<Value> {
    let warp: Value = serde_json::from_slice(&std::fs::read(warp).with_context(|| format!("reading {}", warp.display()))?)?;
    let pose = Pose::new(&warp)?;
    let field = ShoulderHold::from_receipt(&warp, [0.; 3], 1.)?;
    let mesh = Mesh::read_stl(stl)?;
    let rays = MeshRays::new(&mesh, &pose);
    let mut probes = Probes::new(&pose, &rays);
    let nose = shell::tip_frame();
    let shoulder_normal = [0., -paths::JOINT_ANGLE.sin(), paths::JOINT_ANGLE.cos()];
    let nose_bed_box: Vec<_> = mesh.vertices.iter()
        .filter(|&&p| (-0.15..30.).contains(&dot(sub(p, nose[0]), nose[1])))
        .map(|&p| pose.placed(p))
        .collect();
    let (nose_below, nose_above) = bounds(&nose_bed_box);
    let bytes = if tape.extension().is_some_and(|x| x == "3mf") {
        gcode::plate_gcode(tape)?
    } else {
        std::fs::read(tape).with_context(|| format!("reading {}", tape.display()))?
    };
    let text = std::str::from_utf8(&bytes)?;
    let mut groups: Vec<Meta<'_>> = Vec::new();
    for row in text.lines() {
        if row.starts_with("; Z_HEIGHT: ") {
            groups.push(Meta::default());
        } else if let Some(last) = groups.last_mut() {
            if let Some(v) = row.strip_prefix("; HSM_PHASE: ") {
                last.phase = v;
            }
            if let Some(v) = row.strip_prefix("; HSM_NEXT_GROUP: ") {
                last.group = v;
            }
            if let Some(v) = row.strip_prefix("; HSM_TIP_VIRTUAL_Z: ") {
                last.u = v.parse().ok();
            }
            if let Some(v) = row.strip_prefix("; HSM_TIP_COURSE: ") {
                last.course = v.parse().ok();
            }
        }
    }
    let mut k = 0;
    let mut contact: BTreeMap<(&str, Rc<str>), Contact> = BTreeMap::new();
    let mut footprints = BTreeMap::new();
    let mut backing = ShoulderBacking::new(&field);
    let mut exterior: BTreeMap<Rc<str>, NoseWall> = BTreeMap::new();
    let mut layers_out = Vec::new();
    let mut first_flat = 0.;
    let mut first_tilt = None;
    gcode::layers(&bytes, |layer| {
        k += 1;
        let Some(meta) = groups.get(k - 1) else { return };
        let mut pitch = Pitch { group_label: meta.group.to_owned(), ..Default::default() };
        for road in layer.roads.into_iter().filter(|road| road.object == Some(TIP)) {
            let a = [road.x0, road.y0, road.z0];
            let b = [road.x1, road.y1, road.z1];
            let length = distance(a, b);
            let kind = road.feature.as_ref();
            let support = is_support(kind);
            if support {
                pitch.support_mm += length;
            } else {
                pitch.model_mm += length;
            }
            if kind == "Support interface" {
                pitch.interface_mm += length;
            }
            let extent = pitch.z_range.get_or_insert([f64::INFINITY, f64::NEG_INFINITY]);
            extent[0] = extent[0].min(a[2].min(b[2]));
            extent[1] = extent[1].max(a[2].max(b[2]));
            if maxabs_pair(a[2] - 0.2, b[2] - 0.2) < 0.001 {
                if support {
                    pitch.first_layer_support_mm += length;
                } else {
                    pitch.first_layer_model_mm += length;
                }
            }
            if let Some(u) = meta.u {
                let dz = b[2] - a[2];
                let dy = b[1] - a[1];
                if a[1].min(b[1]) >= field.exact_y[0] && a[1].max(b[1]) <= field.exact_y[1] && dy.abs() > 0.025 {
                    pitch.dy_dz += dy * dz;
                    pitch.dy2 += dy * dy;
                }
                let residual = maxabs_pair(a[2] - field.forward(a[1], u), b[2] - field.forward(b[1], u));
                pitch.residual = pitch.residual.max(residual);
                pitch.lateral_weight += length;
                if residual > 0.00035 {
                    pitch.residual_filter_mm += length;
                }
            }
            if length < 1e-6 {
                continue;
            }
            let flow = road.e * std::f64::consts::PI * (1.75_f64 / 2.).powi(2) / length / NOMINAL_FLOW
                / if kind == "Bridge" { NOMINAL_BRIDGE_MULTIPLIER } else { 1. };
            let k = 1. - std::f64::consts::PI / 4.;
            let height = ((road.width - (road.width * road.width - 4. * k * flow).max(0.).sqrt()) / (2. * k)).clamp(0., road.width);
            probes.record(a, b, road.width, height, support);
            if let Some(u) = meta.u.filter(|v| (field.shoulder[2] - 2.5..=field.shoulder[2] + 0.8).contains(v)) {
                let xy = (a[0] - b[0]).hypot(a[1] - b[1]);
                if xy > 1e-6 {
                    let flow = flow * length / xy;
                    let vertical_height = ((road.width - (road.width * road.width - 4. * k * flow).max(0.).sqrt()) / (2. * k)).clamp(0., road.width);
                    backing.observe(Bead { a, b, width: road.width, height: vertical_height, kind: road.feature.clone(), u }, &rays);
                }
            }
            if !support {
                if kind == "Outer wall" || kind == "Overhang wall" {
                    let mid = mix(a, b, 0.5);
                    let rel = sub(pose.cad(mid), nose[0]);
                    let along = dot(rel, nose[1]);
                    let axis_out = dot(rel, nose[2]) - shell::TUBE_SHELL_CENTER_Y;
                    let barrel_radius = rel[0].hypot(axis_out);
                    if (0.1..=shell::GN_TIP_STRAIGHT_LEN - 0.15).contains(&along)
                        && (shell::TUBE_SHELL_OUTER_R - 0.45..=shell::TUBE_SHELL_OUTER_R + 0.09).contains(&barrel_radius)
                    {
                        let norm = unit(add([rel[0], 0., 0.], scale(nose[2], axis_out)));
                        let vertical = apply(&pose.rotation, norm)[2];
                        let incline = (-vertical).clamp(0., 1.).acos().to_degrees();
                        if incline <= 45.5 {
                            exterior.entry(road.feature.clone()).or_default().note(length, road.width, height, a, b, incline);
                        }
                    }
                }
                continue;
            }
            let shoulder_near = a[2].min(b[2]) <= field.shoulder[2] + 10.;
            let nose_near = a[2].max(b[2]) + SUPPORT_SEARCH >= nose_below[2]
                && a[1].max(b[1]) >= nose_below[1] - 0.25
                && a[1].min(b[1]) <= nose_above[1] + 0.25;
            if !shoulder_near && !nose_near {
                continue;
            }
            let count = ((length / 0.30).ceil() as usize).max(1);
            for step in 0..count {
                let spot = mix(a, b, (step as f64 + 0.5) / count as f64);
                let Some((z, n)) = rays.hits(spot[0], spot[1]).into_iter().find(|(z, n)| *z - spot[2] >= -0.02 && n[2] < -0.001) else {
                    continue;
                };
                let gap = z - spot[2];
                if gap > SUPPORT_SEARCH {
                    continue;
                }
                let hit = pose.cad([spot[0], spot[1], z]);
                let normal = apply(&pose.inverse, n);
                if let Some(tag) = nose_zone(hit, normal, nose) {
                    contact.entry((tag, road.feature.clone())).or_default().note(length / count as f64, gap, hit);
                    if kind == "Support interface" {
                        footprint(&mut footprints, tag, spot, gap * n[2].abs());
                    }
                } else if dot(sub(hit, CANONICAL_POINT), shoulder_normal).abs() < 0.045 && dot(normal, shoulder_normal) < -0.99 {
                    contact.entry(("mating shoulder", road.feature.clone())).or_default().note(length / count as f64, gap, hit);
                    if kind == "Support interface" {
                        footprint(&mut footprints, "mating shoulder", spot, gap * n[2].abs());
                    }
                } else {
                    let [point, _, normal] = paths::station_plane((shell::path_plug_start_rot() - paths::JOINT_ANGLE) * paths::water_radius(), 0.);
                    if dot(sub(hit, point), normal).abs() < 0.15 && dot(apply(&pose.inverse, n), normal) < -0.99 {
                        contact.entry(("free plug end", road.feature.clone())).or_default().note(length / count as f64, gap, hit);
                        if kind == "Support interface" {
                            footprint(&mut footprints, "free plug end", spot, gap * n[2].abs());
                        }
                    }
                }
            }
        }
        if pitch.model_mm + pitch.support_mm <= 0. {
            return;
        }
        let angle = (pitch.dy2 > 0.).then(|| (-pitch.dy_dz / pitch.dy2).atan().to_degrees());
        if first_tilt.is_none() && angle.is_some_and(|a| a.abs() > 0.025) {
            first_tilt = Some((meta.u, angle));
        }
        first_flat += pitch.first_layer_model_mm;
        let u = meta.u;
        layers_out.push(json!({"course": meta.course, "phase": meta.phase, "group": pitch.group_label, "virtual_z_mm": u,
            "measured_yz_angle_degrees": angle,
            "modeled_angle_degrees": u.map(|z| (field.parameters_at(z).0 * field.tangent).atan().to_degrees()),
            "minimum_and_maximum_z_mm": pitch.z_range, "model_mm": pitch.model_mm, "support_mm": pitch.support_mm,
            "interface_mm": pitch.interface_mm, "first_bed_model_mm": pitch.first_layer_model_mm,
            "first_bed_support_mm": pitch.first_layer_support_mm,
            "largest_field_fit_residual_mm": pitch.residual, "road_mm_above_small_fit_residual": pitch.residual_filter_mm,
            "tested_road_mm": pitch.lateral_weight}));
    });
    ensure!(k == groups.len(), "the plate has {k} layers and {} layer markers", groups.len());
    let summaries = contact.into_iter().map(|((zone, kind), read)| (format!("{zone} / {kind}"), read.json())).collect::<BTreeMap<_, _>>();
    Ok(json!({
        "purpose": "Checks modeled tip waterways, support contacts and the inclination of the emitted print courses.",
        "source_sha256": sha256_hex(&bytes), "cad_to_plate_origin_mm": pose.shift,
        "off_cad_tolerance_mm_for_bead_samples": PROBE_MARGIN,
        "mesh_bounds_on_plate_mm": rays.mesh_box,
        "first_flat_tip_deposition_mm": first_flat, "first_tilt_by_regressing_deposited_roads": first_tilt,
        "passages": probes.report(), "support_surface_hits": summaries, "closest_local_interface_readings": contact_footprint(&footprints),
        "mating_shoulder_bead_backing": backing.report(),
        "shallow_outer_dispense_barrel_roads": exterior.into_iter().map(|(kind, reading)| (kind.to_string(), reading.json())).collect::<BTreeMap<_, _>>(),
        "tip_course_measurements": layers_out,
        "scope": "For nominal centerlines and modeled bead dimensions. Near-contact support is a vertical CAD ray from deposited stock within the selected inspection envelope."
    }))
}
