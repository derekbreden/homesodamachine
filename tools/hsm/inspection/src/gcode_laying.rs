//! How one part is laid, height by height, on one or more plates side by side: the length laid,
//! the share laid with the part fan on, the length in each commanded speed band with the fan off
//! and on, the slow laying under the fan, the mean speed and the plastic per millimetre.

use crate::gcode::slice_text;
use crate::gcode::walk::{self, walk};
use anyhow::{Result, ensure};
use clap::Args;
use serde::Serialize;
use std::collections::BTreeMap;
use std::path::PathBuf;

/// The part fan counts as on from this share, in percent.
const FAN_ON: f64 = 5.;
/// Slow laying under the fan: at or below this speed, in mm/s, with at least `SLOW_FAN` percent.
const SLOW: f64 = 16.;
const SLOW_FAN: f64 = 60.;
/// The speed bands, in mm/s: under the first, up to the second, over it.
const BANDS: [f64; 2] = [40., 150.];
const WALLS: [&str; 2] = ["Outer wall", "Overhang wall"];

#[derive(Args)]
pub struct Options {
    /// Plates as `.gcode` files or `.gcode.3mf` archives, each as LABEL=PATH or PATH.
    plates: Vec<String>,
    /// The part's object id on the plates.
    #[arg(long)]
    object: i64,
    /// The height of each band, in mm of the move's end Z.
    #[arg(long, default_value_t = 10.)]
    step: f64,
    /// Read only from this height up.
    #[arg(long)]
    from: Option<f64>,
    /// Read only below this height.
    #[arg(long)]
    to: Option<f64>,
    /// Read only the outer and overhang walls.
    #[arg(long)]
    walls: bool,
    /// Read only the walls on the part's outside: beyond the middle of each layer's wall radii
    /// about the layer's wall centroid.
    #[arg(long, requires = "walls")]
    outside: bool,
    /// Write every band to this file.
    #[arg(long)]
    json: Option<PathBuf>,
}

/// One extruding move of the part.
struct Laid {
    mid: [f64; 2],
    z: f64,
    length: f64,
    feed: f64,
    fan: f64,
    e: f64,
}

#[derive(Default, Serialize, Clone)]
struct Band {
    laid_m: f64,
    fan_on_m: f64,
    /// Length in each speed band with the fan off, then with it on, in m.
    fan_off_speed_m: [f64; 3],
    fan_on_speed_m: [f64; 3],
    slow_under_fan_m: f64,
    mean_mm_s: f64,
    e_per_mm: f64,
    #[serde(skip)]
    feed_length: f64,
    #[serde(skip)]
    e: f64,
}

impl Band {
    fn add(&mut self, m: &Laid) {
        let metres = m.length / 1000.;
        self.laid_m += metres;
        self.feed_length += m.feed * m.length;
        self.e += m.e;
        let speed = if m.feed < BANDS[0] { 0 } else if m.feed <= BANDS[1] { 1 } else { 2 };
        if m.fan >= FAN_ON {
            self.fan_on_m += metres;
            self.fan_on_speed_m[speed] += metres;
        } else {
            self.fan_off_speed_m[speed] += metres;
        }
        if m.fan >= SLOW_FAN && m.feed <= SLOW {
            self.slow_under_fan_m += metres;
        }
    }

    fn finish(&mut self) {
        let mm = self.laid_m * 1000.;
        if mm > 0. {
            self.mean_mm_s = self.feed_length / mm;
            self.e_per_mm = self.e / mm;
        }
    }
}

fn read(path: &PathBuf, args: &Options) -> Result<Vec<Laid>> {
    let text = slice_text(path, 1)?;
    let mut out = Vec::new();
    walk(&text, |state, line, from, to| {
        if !line.is_move() || state.object != Some(args.object) || (args.walls && !WALLS.contains(&state.feature.as_str())) {
            return;
        }
        let e = line.word(b'E').unwrap_or(0.);
        let length = walk::xy_length(line, from, to);
        if e <= 0. || length <= 1e-6 || args.from.is_some_and(|z| to[2] < z) || args.to.is_some_and(|z| to[2] >= z) {
            return;
        }
        out.push(Laid { mid: [(from[0] + to[0]) / 2., (from[1] + to[1]) / 2.], z: to[2], length, feed: state.feed, fan: state.fans[0], e });
    });
    if args.outside {
        // the layer's outside: beyond the middle of its wall radii about its centroid
        let mut layers: BTreeMap<i64, Vec<usize>> = BTreeMap::new();
        for (i, m) in out.iter().enumerate() {
            layers.entry((m.z * 10.).round() as i64).or_default().push(i);
        }
        let mut keep = vec![false; out.len()];
        for moves in layers.values() {
            let total: f64 = moves.iter().map(|&i| out[i].length).sum();
            let centre = [0, 1].map(|k| moves.iter().map(|&i| out[i].mid[k] * out[i].length).sum::<f64>() / total);
            let radius = |i: usize| (out[i].mid[0] - centre[0]).hypot(out[i].mid[1] - centre[1]);
            let mut radii: Vec<f64> = moves.iter().map(|&i| radius(i)).collect();
            radii.sort_by(f64::total_cmp);
            let (low, high) = (radii.len() / 10, radii.len() - radii.len().div_ceil(10) - 1);
            let middle = (radii[low] + radii[high]) / 2.;
            for &i in moves {
                keep[i] = radius(i) > middle;
            }
        }
        let mut kept = keep.iter();
        out.retain(|_| *kept.next().unwrap());
    }
    Ok(out)
}

pub fn run(args: Options) -> Result<i32> {
    ensure!(!args.plates.is_empty(), "name at least one plate");
    ensure!(args.step > 0. && args.step.is_finite(), "the band height must be positive");
    let mut plates = Vec::new();
    for (n, plate) in args.plates.iter().enumerate() {
        let (label, path) = match plate.split_once('=') {
            Some((label, path)) => (label.to_string(), PathBuf::from(path)),
            None => (char::from(b'A' + n as u8).to_string(), PathBuf::from(plate)),
        };
        let moves = read(&path, &args)?;
        let mut bands: BTreeMap<i64, Band> = BTreeMap::new();
        let mut total = Band::default();
        for m in &moves {
            bands.entry((m.z / args.step).floor() as i64).or_default().add(m);
            total.add(m);
        }
        bands.values_mut().for_each(Band::finish);
        total.finish();
        println!("{label}  {}", path.display());
        plates.push((label, path, bands, total));
    }
    let keys: std::collections::BTreeSet<i64> = plates.iter().flat_map(|p| p.2.keys().copied()).collect();
    println!("object {}{}; speeds in mm/s, lengths in m; fan on from {FAN_ON}%, slow under the fan at or below {SLOW} mm/s with {SLOW_FAN}% or more",
        args.object, if args.outside { ", outside walls" } else if args.walls { ", walls" } else { "" });
    println!("{:>12} {:>3} {:>8} {:>7} | {:>6} {:>6} {:>6} | {:>6} {:>6} {:>6} | {:>8} {:>6} {:>7}",
        "Z band", "", "laid", "fan on", "off<40", "40-150", ">150", "on<40", "40-150", ">150", "slow+fan", "mean", "E/mm");
    let row = |name: &str, label: &str, b: &Band| {
        println!("{name:>12} {label:>3} {:8.2} {:6.1}% | {:6.2} {:6.2} {:6.2} | {:6.2} {:6.2} {:6.2} | {:8.2} {:6.0} {:7.4}",
            b.laid_m, 100. * b.fan_on_m / b.laid_m.max(1e-12), b.fan_off_speed_m[0], b.fan_off_speed_m[1], b.fan_off_speed_m[2],
            b.fan_on_speed_m[0], b.fan_on_speed_m[1], b.fan_on_speed_m[2], b.slow_under_fan_m, b.mean_mm_s, b.e_per_mm);
    };
    for key in &keys {
        let name = format!("{:.0}-{:.0}", *key as f64 * args.step, (*key + 1) as f64 * args.step);
        for (label, _, bands, _) in &plates {
            if let Some(b) = bands.get(key) {
                row(&name, label, b);
            }
        }
    }
    for (label, _, _, total) in &plates {
        row("all", label, total);
    }
    if let Some(path) = &args.json {
        let out: Vec<_> = plates.iter().map(|(label, path, bands, total)| serde_json::json!({
            "label": label, "plate": path, "object": args.object, "step_mm": args.step,
            "bands": bands.iter().map(|(k, b)| (format!("{:.3}", *k as f64 * args.step), b.clone())).collect::<BTreeMap<_, _>>(),
            "all": total,
        })).collect();
        std::fs::write(path, serde_json::to_string_pretty(&out)? + "\n")?;
    }
    Ok(0)
}
