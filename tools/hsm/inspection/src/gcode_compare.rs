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

fn read(path: &PathBuf, features: &mut Vec<String>) -> Result<Vec<Bead>> {
    let text = slice_text(path, 1)?;
    let mut out = Vec::new();
    let mut layer = 0;
    beads::layers(text.as_bytes(), |l| {
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
    Ok(out)
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

    fn row(&self) -> String {
        let plastic = if self.plastic_a > 0.0 {
            format!("{:+.3}%", 100.0 * (self.plastic_b - self.plastic_a) / self.plastic_a)
        } else {
            "new".into()
        };
        format!("{:11.1} {:11.1} {:>9} {:>8.3}% {:>8.3}%", self.length_a, self.length_b, plastic,
            100.0 * Self::share(self.on_b, self.length_a), 100.0 * Self::share(self.on_a, self.length_b))
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

pub fn run(args: Options) -> Result<i32> {
    let mut features = Vec::new();
    let a = read(&args.a, &mut features)?;
    let b = read(&args.b, &mut features)?;
    let cell = (4.0 * args.tolerance).max(0.5);
    let (index_a, index_b) = (Index::new(&a, cell), Index::new(&b, cell));
    let (on_b, on_a) = (coverage(&a, &index_b, args.tolerance), coverage(&b, &index_a, args.tolerance));
    let mut by_feature: BTreeMap<String, Tally> = BTreeMap::new();
    let mut by_layer: BTreeMap<(i64, String), (usize, f64, Tally)> = BTreeMap::new();
    for (side, list, on) in [('a', &a, &on_b), ('b', &b, &on_a)] {
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
    println!("A {}\nB {}\nA bead counts as on B within {} mm of a B bead of its feature, and B on A the same way.",
        args.a.display(), args.b.display(), args.tolerance);
    let head = format!("{:11} {:11} {:>9} {:>9} {:>9}", "length A mm", "length B mm", "plastic", "A on B", "B on A");
    println!("\n{:24} {head}", "feature");
    let mut whole = Tally::default();
    for (name, t) in &by_feature {
        println!("{name:24} {}", t.row());
        whole.length_a += t.length_a;
        whole.length_b += t.length_b;
        whole.on_b += t.on_b;
        whole.on_a += t.on_a;
        whole.plastic_a += t.plastic_a;
        whole.plastic_b += t.plastic_b;
    }
    println!("{:24} {}", "all beads", whole.row());
    let rows: Vec<_> = by_layer.values().filter(|(_, _, t)| args.all || t.differs()).collect();
    let layers_differing = by_layer.values().filter(|(_, _, t)| t.differs()).count();
    println!("\n{} of {} layer and feature groups differ.", layers_differing, by_layer.len());
    if !rows.is_empty() {
        println!("{:>5} {:>8} {:24} {head}", "layer", "top", "feature");
    }
    let names: BTreeMap<_, _> = by_layer.keys().map(|k| (k, k.1.clone())).collect();
    for (key, (layer, top, t)) in by_layer.iter().filter(|(_, (_, _, t))| args.all || t.differs()).take(args.limit) {
        println!("{layer:5} {top:8.3} {:24} {}", names[key], t.row());
    }
    if rows.len() > args.limit {
        println!("... {} more; --limit lists more", rows.len() - args.limit);
    }
    let mut only: Vec<Stretch> = stretches(&a, &on_b, 'A', &features);
    only.extend(stretches(&b, &on_a, 'B', &features));
    only.sort_by(|x, y| y.length.total_cmp(&x.length));
    if !only.is_empty() {
        println!("\nThe longest stretches only one slice lays:");
        for s in only.iter().take(args.limit) {
            let p = |v: [f64; 3]| format!("({:.2}, {:.2}, {:.2})", v[0], v[1], v[2]);
            println!("  only in {} layer {:5} {:24} {:8.2} mm from {} to {}", s.only_in, s.layer, s.feature, s.length, p(s.from), p(s.to));
        }
    }
    if let Some(path) = args.json {
        let layers: Vec<_> = by_layer.iter().map(|(key, (layer, top, t))| {
            serde_json::json!({"layer": layer, "top": top, "feature": names[key], "tally": t})
        }).collect();
        let value = serde_json::json!({"a": args.a, "b": args.b, "tolerance_mm": args.tolerance, "features": by_feature,
            "all": whole, "layers": layers, "stretches": only});
        std::fs::write(&path, serde_json::to_string_pretty(&value)? + "\n")?;
    }
    Ok(0)
}
