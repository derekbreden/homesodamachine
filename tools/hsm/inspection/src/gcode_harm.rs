//! Where the head could hit plastic it laid earlier on one plate: travels whose nozzle tip passes
//! below the top of earlier plastic or within a tenth of a millimetre of it, drops onto a part,
//! and waits with the nozzle over a part. A height map keeps the tallest bead top laid so far in
//! every cell of the plate; each travel between beads is sampled along its path against it.

use crate::gcode::slice_text;
use crate::gcode::walk::{self, walk};
use anyhow::Result;
use clap::Args;
use serde::Serialize;
use std::collections::BTreeMap;
use std::path::PathBuf;

const CELL: f64 = 0.2;
const CELLS: usize = 1800;
const SAMPLE: f64 = 0.1;
/// The ends of each travel, where it leaves and reaches a bead, are not judged.
const ENDS: f64 = 0.6;
const NEAR: f64 = 0.1;
const BELOW: f64 = -0.05;
/// The courses laid tilted or ahead of the slicer's layers.
const TILTED: [&str; 6] = ["sloped course", "underside deck bedding", "underside roof course", "scaffold layer",
    "tip shoulder entry", "tip yellow shoulder"];

#[derive(Args)]
pub struct Options {
    /// The plate, a `.gcode` file or a `.gcode.3mf` archive.
    slice: PathBuf,
    /// Read only the travels that leave or reach this object's beads.
    #[arg(long)]
    object: Option<i64>,
    /// Read only the travels whose closest approach lies at or above this height, in mm.
    #[arg(long)]
    above: Option<f64>,
    /// How many of the worst travels, drops and waits to list.
    #[arg(long, default_value_t = 4)]
    limit: usize,
    /// Write every travel, drop and wait the reading keeps to this file.
    #[arg(long)]
    json: Option<PathBuf>,
}

struct Grid(Vec<f32>);

impl Grid {
    fn index(v: f64) -> usize {
        ((v / CELL) as i64).clamp(1, CELLS as i64 - 2) as usize
    }

    fn lay(&mut self, p: [f64; 3]) {
        let (i, j) = (Self::index(p[0]), Self::index(p[1]));
        for di in [i - 1, i, i + 1] {
            for dj in [j - 1, j, j + 1] {
                let cell = &mut self.0[di * CELLS + dj];
                *cell = cell.max(p[2] as f32);
            }
        }
    }

    fn top(&self, x: f64, y: f64) -> f64 {
        let (i, j) = (Self::index(x), Self::index(y));
        let mut top = f32::MIN;
        for di in [i - 1, i, i + 1] {
            for dj in [j - 1, j, j + 1] {
                top = top.max(self.0[di * CELLS + dj]);
            }
        }
        top as f64
    }
}

/// Points every `SAMPLE` along a straight piece, its start included when `start` is set.
fn samples(p0: [f64; 3], p1: [f64; 3], length: f64, start: bool) -> impl Iterator<Item = (f64, [f64; 3])> {
    let n = ((length / SAMPLE) as usize + 1).max(2);
    (usize::from(!start)..n).map(move |k| {
        let t = k as f64 / (n - 1) as f64;
        (t, [0, 1, 2].map(|a| p0[a] + (p1[a] - p0[a]) * t))
    })
}

/// The points an arc travel passes through, every `SAMPLE` along it: a whole turn when it names
/// no end in XY, as a spiral lift does.
fn arc_points(line: &walk::Line, p0: [f64; 3], p1: [f64; 3]) -> Vec<[f64; 3]> {
    let (i, j) = (line.word(b'I').unwrap_or(0.), line.word(b'J').unwrap_or(0.));
    let (cx, cy) = (p0[0] + i, p0[1] + j);
    let r = i.hypot(j);
    let (a0, a1) = ((p0[1] - cy).atan2(p0[0] - cx), (p1[1] - cy).atan2(p1[0] - cx));
    let clockwise = line.command == "G2";
    let mut sweep = if clockwise { a0 - a1 } else { a1 - a0 };
    if sweep <= 1e-9 || (line.word(b'X').is_none() && line.word(b'Y').is_none()) {
        sweep += std::f64::consts::TAU;
    }
    let n = ((sweep * r / SAMPLE) as usize + 1).max(2);
    let sign = if clockwise { -1. } else { 1. };
    (1..n).map(|k| {
        let t = k as f64 / (n - 1) as f64;
        let a = a0 + sign * sweep * t;
        [cx + r * a.cos(), cy + r * a.sin(), p0[2] + (p1[2] - p0[2]) * t]
    }).collect()
}

#[derive(Clone, Serialize)]
struct Context {
    object: Option<i64>,
    phase: String,
    feature: String,
    line: usize,
}

#[derive(Serialize)]
struct Travel {
    worst_mm: f64,
    at: [f64; 3],
    line: usize,
    feed_mm_s: f64,
    low_mm: f64,
    below_mm: f64,
    length_mm: f64,
    left: Option<Context>,
    reached: Context,
}

#[derive(Serialize)]
struct Drop {
    line: usize,
    descent_mm: f64,
    feed_mm_s: f64,
    above_plastic_mm: f64,
    at: [f64; 3],
    object: Option<i64>,
    phase: String,
}

#[derive(Serialize)]
struct Wait {
    line: usize,
    command: String,
    above_plastic_mm: f64,
    at: [f64; 3],
    object: Option<i64>,
    phase: String,
}

fn phase(context: &Option<Context>) -> String {
    context.as_ref().map_or("start".into(), |c| if c.phase.is_empty() { "level or native".into() } else { c.phase.clone() })
}

pub fn run(args: Options) -> Result<i32> {
    let text = slice_text(&args.slice, 1)?;
    let mut grid = Grid(vec![-100.; CELLS * CELLS]);
    let mut travel: Vec<([f64; 3], [f64; 3], f64, usize)> = Vec::new();
    let mut left: Option<Context> = None;
    let (mut travels, mut drops, mut waits) = (Vec::new(), Vec::new(), Vec::new());
    let mut handovers = 0usize;
    walk(&text, |state, line, from, to| {
        if !state.started {
            return;
        }
        if matches!(line.command, "M109" | "M190" | "G4" | "M400") {
            waits.push(Wait { line: line.number, command: line.code.to_string(), above_plastic_mm: from[2] - grid.top(from[0], from[1]),
                at: from, object: state.object, phase: state.phase.clone() });
            return;
        }
        if !line.is_move() || from == to {
            return;
        }
        let e = line.word(b'E');
        if e == Some(0.) {
            return;
        }
        if e.is_some_and(|e| e > 0.) {
            let here = Context { object: state.object, phase: state.phase.clone(), feature: state.feature.clone(), line: line.number };
            if !travel.is_empty() {
                handovers += 1;
                let total: f64 = travel.iter().map(|(a, b, _, _)| walk_length(*a, *b)).sum();
                let (mut worst, mut at, mut at_line, mut feed) = (f64::INFINITY, [0.; 3], 0, 0.);
                let (mut low, mut below, mut along) = (0., 0., 0.);
                for (k, (a, b, f, n)) in travel.iter().enumerate() {
                    let length = walk_length(*a, *b);
                    for (t, p) in samples(*a, *b, length, k == 0) {
                        let d = along + t * length;
                        if d <= ENDS || d >= total - ENDS {
                            continue;
                        }
                        let clearance = p[2] - grid.top(p[0], p[1]);
                        if clearance < worst {
                            (worst, at, at_line, feed) = (clearance, p, *n, *f);
                        }
                        low += if clearance < NEAR { SAMPLE } else { 0. };
                        below += if clearance < BELOW { SAMPLE } else { 0. };
                    }
                    along += length;
                }
                if worst < NEAR {
                    travels.push(Travel { worst_mm: worst, at, line: at_line, feed_mm_s: feed, low_mm: low, below_mm: below,
                        length_mm: total, left: left.clone(), reached: here.clone() });
                }
                travel.clear();
            }
            let mut start = from;
            for p in walk::path(line, from, to) {
                for (_, q) in samples(start, p, (p[0] - start[0]).hypot(p[1] - start[1]), true) {
                    grid.lay(q);
                }
                start = p;
            }
            left = Some(here);
            return;
        }
        if (to[0] - from[0]).hypot(to[1] - from[1]) < 1e-6 && to[2] < from[2] {
            let thousandths = |v: f64| (v * 1000.).round() / 1000.;
            drops.push(Drop { line: line.number, descent_mm: thousandths(from[2] - to[2]), feed_mm_s: state.feed,
                above_plastic_mm: thousandths(to[2] - grid.top(to[0], to[1])), at: to, object: state.object, phase: state.phase.clone() });
        }
        let points = if matches!(line.command, "G2" | "G3") { arc_points(line, from, to) } else { vec![to] };
        let mut start = from;
        for p in points {
            travel.push((start, p, state.feed, line.number));
            start = p;
        }
    });

    let keep = |t: &Travel| {
        args.object.is_none_or(|o| t.left.as_ref().is_some_and(|c| c.object == Some(o)) || t.reached.object == Some(o))
            && args.above.is_none_or(|z| t.at[2] >= z)
    };
    let kept: Vec<&Travel> = travels.iter().filter(|t| keep(t)).collect();
    let below: Vec<&&Travel> = kept.iter().filter(|t| t.worst_mm < BELOW).collect();
    let tilted = |t: &Travel| TILTED.contains(&phase(&t.left).as_str()) || TILTED.contains(&t.reached.phase.as_str());
    println!("{}", args.slice.display());
    if args.object.is_some() || args.above.is_some() {
        println!("travels that leave or reach object {} with their closest approach at or above {} mm",
            args.object.map_or("any".into(), |o| o.to_string()), args.above.map_or("any height".into(), |z| z.to_string()));
    }
    println!("travels between beads {handovers}; nozzle within {NEAR} mm of earlier plastic {}; below a top {} (in tilted courses {})",
        kept.len(), below.len(), below.iter().filter(|t| tilted(t)).count());
    let mut by_phase: BTreeMap<String, usize> = BTreeMap::new();
    for t in &kept {
        *by_phase.entry(phase(&t.left)).or_default() += 1;
    }
    println!("  within {NEAR} mm, by the phase of the bead left: {by_phase:?}");
    let long: Vec<&&Travel> = kept.iter().filter(|t| t.low_mm >= 2.).collect();
    println!("  with 2 mm or more of travel within {NEAR} mm: {}", long.len());
    let mut worst: Vec<&&&Travel> = below.iter().filter(|t| !tilted(t)).collect();
    worst.sort_by(|p, q| p.worst_mm.total_cmp(&q.worst_mm));
    for t in worst.iter().take(args.limit) {
        println!("    below a top outside tilted courses: {:+.3} mm at line {} ({:.2}, {:.2}, {:.3}) at {:.0} mm/s, from {} to {}",
            t.worst_mm, t.line, t.at[0], t.at[1], t.at[2], t.feed_mm_s, phase(&t.left), t.reached.phase);
    }
    let mut longest: Vec<&&&Travel> = long.iter().collect();
    longest.sort_by(|p, q| q.low_mm.total_cmp(&p.low_mm));
    for t in longest.iter().take(args.limit) {
        println!("    long low stretch {:.1} mm (worst {:+.3} mm) at line {} ({:.1}, {:.1}, {:.2})",
            t.low_mm, t.worst_mm, t.line, t.at[0], t.at[1], t.at[2]);
    }
    let onto: Vec<&Drop> = drops.iter().filter(|d| d.descent_mm >= 1. && d.above_plastic_mm < 0.6).collect();
    let mut bands: BTreeMap<(String, i64), usize> = BTreeMap::new();
    for d in &onto {
        let band = if d.descent_mm < 2. { "1-2" } else if d.descent_mm < 5. { "2-5" } else { "5+" };
        *bands.entry((band.into(), d.feed_mm_s.round() as i64)).or_default() += 1;
    }
    println!("  drops of 1 mm or more ending within 0.6 mm of plastic: {}; by (descent in mm, feed in mm/s): {bands:?}", onto.len());
    let mut fast: Vec<&&Drop> = onto.iter().filter(|d| d.feed_mm_s >= 30.).collect();
    fast.sort_by(|p, q| q.descent_mm.total_cmp(&p.descent_mm));
    for d in fast.iter().take(args.limit) {
        println!("    fast drop {:.2} mm at {:.0} mm/s, line {}, ending {:.3} mm above plastic at ({:.2}, {:.2}, {:.2})",
            d.descent_mm, d.feed_mm_s, d.line, d.above_plastic_mm, d.at[0], d.at[1], d.at[2]);
    }
    let close: Vec<&Wait> = waits.iter().filter(|w| w.above_plastic_mm < 5.).collect();
    println!("  waits with the nozzle within 5 mm of plastic: {}", close.len());
    for w in close.iter().take(args.limit) {
        println!("    line {} {} {:.3} mm above plastic, {}", w.line, w.command, w.above_plastic_mm, w.phase);
    }
    if let Some(path) = &args.json {
        let out = serde_json::json!({"plate": args.slice, "travels_between_beads": handovers, "travels": kept, "drops": onto, "waits": close});
        std::fs::write(path, serde_json::to_string_pretty(&out)? + "\n")?;
    }
    Ok(0)
}

fn walk_length(a: [f64; 3], b: [f64; 3]) -> f64 {
    [0, 1, 2].map(|i| (b[i] - a[i]).powi(2)).iter().sum::<f64>().sqrt()
}
