//! Compares the beads two slices lay, to tell whether a change to a print stage changed what
//! prints: per feature and per layer, how much of each slice's bead length lies on the other's
//! beads of the same feature, the plastic each lays, and the longest stretches only one lays.
//! Beads are matched where they lie, so sloped courses compare as level ones do.

use crate::gcode::slice_text;
use anyhow::Result;
use clap::Args;
use hsm_print_prep::gcode as beads;
use serde::Serialize;
use std::collections::{BTreeMap, HashMap};
use std::path::PathBuf;

#[derive(Args)]
pub struct Options {
    /// The reference slice, a `.gcode` file or a `.gcode.3mf` archive.
    a: PathBuf,
    /// The slice compared with it.
    b: PathBuf,
    /// How far a bead may lie from the other slice's bead of its feature and count as on it, in mm.
    #[arg(long, default_value_t = 0.05)]
    tolerance: f64,
    /// List every layer, not only the layers whose beads differ.
    #[arg(long)]
    all: bool,
    /// How many layers and stretches to list.
    #[arg(long, default_value_t = 20)]
    limit: usize,
    /// Write every group and stretch to this file.
    #[arg(long)]
    json: Option<PathBuf>,
}

/// One straight piece of bead.
struct Bead {
    layer: usize,
    top: f64,
    feature: u16,
    p0: [f64; 3],
    p1: [f64; 3],
    e: f64,
}

fn read(gcode: &[u8], features: &mut Vec<String>) -> Vec<Bead> {
    let mut out = Vec::new();
    let mut layer = 0;
    beads::layers(gcode, |l| {
        layer += 1;
        for r in l.roads {
            let feature = match features.iter().position(|f| **f == *r.feature) {
                Some(i) => i,
                None => {
                    features.push(r.feature.to_string());
                    features.len() - 1
                }
            } as u16;
            out.push(Bead { layer, top: l.z, feature, p0: [r.x0, r.y0, r.z0], p1: [r.x1, r.y1, r.z1], e: r.e });
        }
    });
    out
}

fn sub(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

fn length(b: &Bead) -> f64 {
    dot(sub(b.p1, b.p0), sub(b.p1, b.p0)).sqrt()
}

fn at(b: &Bead, t: f64) -> [f64; 3] {
    [b.p0[0] + (b.p1[0] - b.p0[0]) * t, b.p0[1] + (b.p1[1] - b.p0[1]) * t, b.p0[2] + (b.p1[2] - b.p0[2]) * t]
}

/// The beads of one slice, by feature and by the cells their centrelines pass through.
struct Index<'a> {
    beads: &'a [Bead],
    cell: f64,
    cells: HashMap<(u16, [i64; 3]), Vec<u32>>,
}

impl<'a> Index<'a> {
    fn new(beads: &'a [Bead], cell: f64) -> Self {
        let mut cells: HashMap<(u16, [i64; 3]), Vec<u32>> = HashMap::new();
        for (i, b) in beads.iter().enumerate() {
            let steps = (length(b) / (cell / 2.0)).ceil() as usize;
            let mut last = None;
            for k in 0..=steps {
                let key = (b.feature, Self::key(cell, at(b, k as f64 / steps.max(1) as f64)));
                if last != Some(key) {
                    let list = cells.entry(key).or_default();
                    if list.last() != Some(&(i as u32)) {
                        list.push(i as u32);
                    }
                    last = Some(key);
                }
            }
        }
        Index { beads, cell, cells }
    }

    fn key(cell: f64, p: [f64; 3]) -> [i64; 3] {
        p.map(|v| (v / cell).floor() as i64)
    }

    /// Whether a bead of `feature` lies within `tolerance` of `p`.
    fn near(&self, feature: u16, p: [f64; 3], tolerance: f64) -> bool {
        let [x, y, z] = Self::key(self.cell, p);
        for dx in -1..=1 {
            for dy in -1..=1 {
                for dz in -1..=1 {
                    let Some(list) = self.cells.get(&(feature, [x + dx, y + dy, z + dz])) else { continue };
                    for &i in list {
                        let b = &self.beads[i as usize];
                        let d = sub(b.p1, b.p0);
                        let span = dot(d, d);
                        let t = if span > 0.0 { (dot(sub(p, b.p0), d) / span).clamp(0.0, 1.0) } else { 0.0 };
                        let q = sub(p, at(b, t));
                        if dot(q, q) <= tolerance * tolerance {
                            return true;
                        }
                    }
                }
            }
        }
        false
    }
}

/// How much of each bead's length lies on the other slice's beads.
fn coverage(own: &[Bead], other: &Index, tolerance: f64) -> Vec<f64> {
    let step = (2.0 * tolerance).min(0.1);
    own.iter().map(|b| {
        let span = length(b);
        let n = ((span / step).ceil() as usize).max(1);
        let on = (0..n).filter(|k| other.near(b.feature, at(b, (*k as f64 + 0.5) / n as f64), tolerance)).count();
        span * on as f64 / n as f64
    }).collect()
}

#[derive(Default, Serialize, Clone)]
struct Tally {
    length_a: f64,
    length_b: f64,
    on_b: f64,
    on_a: f64,
    plastic_a: f64,
    plastic_b: f64,
}

impl Tally {
    fn share(on: f64, of: f64) -> f64 {
        if of > 0.0 { on / of } else { 1.0 }
    }

    fn differs(&self) -> bool {
        Self::share(self.on_b, self.length_a) < 0.9995 || Self::share(self.on_a, self.length_b) < 0.9995
            || (self.plastic_a - self.plastic_b).abs() > 1e-4_f64.max(5e-4 * self.plastic_a)
    }

    fn plastic(&self) -> String {
        if self.plastic_a > 0.0 {
            format!("{:+.3}%", 100.0 * (self.plastic_b - self.plastic_a) / self.plastic_a)
        } else {
            "new".into()
        }
    }

    fn row(&self) -> String {
        format!("{:11.1} {:11.1} {:>9} {:>8.3}% {:>8.3}%", self.length_a, self.length_b, self.plastic(),
            100.0 * Self::share(self.on_b, self.length_a), 100.0 * Self::share(self.on_a, self.length_b))
    }

    fn add(&mut self, other: &Tally) {
        self.length_a += other.length_a;
        self.length_b += other.length_b;
        self.on_b += other.on_b;
        self.on_a += other.on_a;
        self.plastic_a += other.plastic_a;
        self.plastic_b += other.plastic_b;
    }
}

/// A stretch of bead one slice lays where the other lays none of that feature.
#[derive(Serialize)]
struct Stretch {
    only_in: char,
    layer: usize,
    feature: String,
    length: f64,
    from: [f64; 3],
    to: [f64; 3],
}

/// Consecutive beads laid off the other slice, joined where one ends where the next begins.
fn stretches(own: &[Bead], on: &[f64], side: char, features: &[String]) -> Vec<Stretch> {
    let mut out: Vec<Stretch> = Vec::new();
    let mut joined = false;
    for (b, on) in own.iter().zip(on) {
        let off = length(b) - on;
        if off < 1e-6 {
            joined = false;
            continue;
        }
        match out.last_mut() {
            Some(s) if joined && dot(sub(s.to, b.p0), sub(s.to, b.p0)) < 1e-8 && s.layer == b.layer => {
                s.length += off;
                s.to = b.p1;
            }
            _ => out.push(Stretch { only_in: side, layer: b.layer, feature: features[b.feature as usize].clone(), length: off,
                                    from: b.p0, to: b.p1 }),
        }
        joined = off > length(b) - 1e-6;
    }
    out
}

/// Two slices' beads matched where they lie: by feature, by layer and feature, in all, and the
/// stretches only one lays, longest first.
pub struct Comparison {
    by_feature: BTreeMap<String, Tally>,
    /// Keyed by the layer's top, rounded, and the feature.
    by_layer: BTreeMap<(i64, String), (usize, f64, Tally)>,
    whole: Tally,
    only: Vec<Stretch>,
}

impl Comparison {
    /// The layer and feature groups whose beads or plastic differ.
    pub fn groups_differing(&self) -> usize {
        self.by_layer.values().filter(|(_, _, t)| t.differs()).count()
    }

    /// How many groups differ, and how much of all the beads lies on the other slice's.
    pub fn summary(&self) -> String {
        let w = &self.whole;
        format!("{} of {} layer and feature groups differ; of all beads, A on B {:.3}%, B on A {:.3}%, plastic {}",
            self.groups_differing(), self.by_layer.len(), 100.0 * Tally::share(w.on_b, w.length_a),
            100.0 * Tally::share(w.on_a, w.length_b), w.plastic())
    }
}

/// Match the beads of two slices' G-code, each bead on the other's within `tolerance` mm.
pub fn compare(a: &[u8], b: &[u8], tolerance: f64) -> Comparison {
    let mut features = Vec::new();
    let a = read(a, &mut features);
    let b = read(b, &mut features);
    matched(&a, &b, &features, tolerance)
}

fn matched(a: &[Bead], b: &[Bead], features: &[String], tolerance: f64) -> Comparison {
    let cell = (4.0 * tolerance).max(0.5);
    let (index_a, index_b) = (Index::new(a, cell), Index::new(b, cell));
    let (on_b, on_a) = (coverage(a, &index_b, tolerance), coverage(b, &index_a, tolerance));
    let mut by_feature: BTreeMap<String, Tally> = BTreeMap::new();
    let mut by_layer: BTreeMap<(i64, String), (usize, f64, Tally)> = BTreeMap::new();
    for (side, list, on) in [('a', a, &on_b), ('b', b, &on_a)] {
        for (bead, on) in list.iter().zip(on.iter()) {
            let name = features[bead.feature as usize].clone();
            let layer = by_layer.entry(((bead.top * 1e4).round() as i64, name.clone())).or_insert((bead.layer, bead.top, Tally::default()));
            for t in [by_feature.entry(name).or_default(), &mut layer.2] {
                if side == 'a' {
                    t.length_a += length(bead);
                    t.on_b += on;
                    t.plastic_a += bead.e;
                } else {
                    t.length_b += length(bead);
                    t.on_a += on;
                    t.plastic_b += bead.e;
                }
            }
        }
    }
    let mut whole = Tally::default();
    by_feature.values().for_each(|t| whole.add(t));
    let mut only: Vec<Stretch> = stretches(a, &on_b, 'A', features);
    only.extend(stretches(b, &on_a, 'B', features));
    only.sort_by(|x, y| y.length.total_cmp(&x.length));
    Comparison { by_feature, by_layer, whole, only }
}

pub fn run(args: Options) -> Result<i32> {
    let mut features = Vec::new();
    let a = read(slice_text(&args.a, 1)?.as_bytes(), &mut features);
    let b = read(slice_text(&args.b, 1)?.as_bytes(), &mut features);
    let Comparison { by_feature, by_layer, whole, only } = matched(&a, &b, &features, args.tolerance);
    println!("A {}\nB {}\nA bead counts as on B within {} mm of a B bead of its feature, and B on A the same way.",
        args.a.display(), args.b.display(), args.tolerance);
    let head = format!("{:11} {:11} {:>9} {:>9} {:>9}", "length A mm", "length B mm", "plastic", "A on B", "B on A");
    println!("\n{:24} {head}", "feature");
    for (name, t) in &by_feature {
        println!("{name:24} {}", t.row());
    }
    println!("{:24} {}", "all beads", whole.row());
    let rows: Vec<_> = by_layer.values().filter(|(_, _, t)| args.all || t.differs()).collect();
    let layers_differing = by_layer.values().filter(|(_, _, t)| t.differs()).count();
    println!("\n{} of {} layer and feature groups differ.", layers_differing, by_layer.len());
    if !rows.is_empty() {
        println!("{:>5} {:>8} {:24} {head}", "layer", "top", "feature");
    }
    for ((_, feature), (layer, top, t)) in by_layer.iter().filter(|(_, (_, _, t))| args.all || t.differs()).take(args.limit) {
        println!("{layer:5} {top:8.3} {feature:24} {}", t.row());
    }
    if rows.len() > args.limit {
        println!("... {} more; --limit lists more", rows.len() - args.limit);
    }
    if !only.is_empty() {
        println!("\nThe longest stretches only one slice lays:");
        for s in only.iter().take(args.limit) {
            let p = |v: [f64; 3]| format!("({:.2}, {:.2}, {:.2})", v[0], v[1], v[2]);
            println!("  only in {} layer {:5} {:24} {:8.2} mm from {} to {}", s.only_in, s.layer, s.feature, s.length, p(s.from), p(s.to));
        }
    }
    if let Some(path) = args.json {
        let layers: Vec<_> = by_layer.iter().map(|((_, feature), (layer, top, t))| {
            serde_json::json!({"layer": layer, "top": top, "feature": feature, "tally": t})
        }).collect();
        let value = serde_json::json!({"a": args.a, "b": args.b, "tolerance_mm": args.tolerance, "features": by_feature,
            "all": whole, "layers": layers, "stretches": only});
        std::fs::write(&path, serde_json::to_string_pretty(&value)? + "\n")?;
    }
    Ok(0)
}
