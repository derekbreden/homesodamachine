//! What two plates command differently, apart from where their beads lie: by part and feature,
//! the length laid at each feed, part-fan level, nozzle temperature and acceleration; the
//! printer-side commands; the retractions, primes, lifts and travels between beads; the heating
//! commands; and the moves that follow the same path under other settings.

use crate::gcode::slice_text;
use crate::gcode::walk::walk;
use anyhow::Result;
use clap::Args;
use serde_json::{Value, json};
use std::collections::{BTreeMap, HashMap};
use std::hash::{DefaultHasher, Hash, Hasher};
use std::path::PathBuf;

#[derive(Args)]
pub struct Options {
    /// The reference plate, a `.gcode` file or a `.gcode.3mf` archive.
    a: PathBuf,
    /// The plate read against it.
    b: PathBuf,
    /// How many differing values to list for each reading.
    #[arg(long, default_value_t = 6)]
    limit: usize,
    /// Write every reading to this file.
    #[arg(long)]
    json: Option<PathBuf>,
}

#[derive(Default)]
struct Group {
    length: f64,
    /// Length laid at each rounded value, in mm.
    by: [BTreeMap<i64, f64>; 4],
}
const READINGS: [(&str, &str); 4] = [("feed", "mm/s"), ("part fan", "%"), ("nozzle", "C"), ("acceleration", "mm/s2")];

#[derive(Default)]
struct Plate {
    groups: BTreeMap<(String, String), Group>,
    commands: BTreeMap<String, usize>,
    travels: BTreeMap<String, usize>,
    heats: Vec<String>,
    /// Each part's extruding moves by their rounded path: the feed, part fan and acceleration.
    paths: HashMap<(i64, u64), Vec<[i64; 3]>>,
}

fn part(object: Option<i64>) -> String {
    match object {
        Some(1901) => "base".into(),
        Some(1902) => "tip".into(),
        Some(1903) => "cover".into(),
        Some(1904) => "mounting plate".into(),
        Some(1905) => "lever".into(),
        Some(id) => id.to_string(),
        None => "between parts".into(),
    }
}

fn read(path: &PathBuf) -> Result<Plate> {
    let text = slice_text(path, 1)?;
    let mut plate = Plate::default();
    walk(&text, |state, line, from, to| {
        if !state.started {
            return;
        }
        if !line.is_move() {
            let mut name = line.command.to_string();
            if matches!(line.command, "M104" | "M109" | "M140" | "M190") {
                plate.heats.push(format!("{} at layer {}", line.code, state.layer));
            }
            let letters: String = line.words.iter().map(|(k, _)| *k as char).collect();
            if !letters.is_empty() {
                name = format!("{name} {letters}");
            }
            *plate.commands.entry(name).or_default() += 1;
            return;
        }
        let xy = (to[0] - from[0]).hypot(to[1] - from[1]);
        let dz = to[2] - from[2];
        let feed = state.feed.round() as i64;
        let e = line.word(b'E');
        let travel = match e {
            Some(e) if e < 0. && xy < 1e-6 => Some(format!("retract {:.3} mm at {feed} mm/s", -e)),
            Some(e) if e > 0. && xy < 1e-6 && dz.abs() < 1e-6 => Some(format!("prime {e:.3} mm at {feed} mm/s")),
            None if matches!(line.command, "G2" | "G3") && line.word(b'X').is_none() && line.word(b'Y').is_none() =>
                Some(format!("spiral lift {dz:+.2} mm at {feed} mm/s")),
            None if xy < 1e-6 && dz.abs() > 1e-6 => Some(format!("lift {dz:+.2} mm at {feed} mm/s")),
            None if xy > 0. => Some(format!("travel at {feed} mm/s")),
            _ => None,
        };
        if let Some(kind) = travel {
            *plate.travels.entry(kind).or_default() += 1;
            return;
        }
        let Some(e) = e.filter(|e| *e >= 0. && (xy > 1e-6 || dz.abs() > 1e-6)) else {
            return;
        };
        let length = xy.hypot(dz);
        let group = plate.groups.entry((part(state.object), state.feature.clone())).or_default();
        group.length += length;
        let values = [state.feed, state.fans[0], state.temperature.unwrap_or(0.), state.acceleration.unwrap_or(0.)];
        for (map, value) in group.by.iter_mut().zip(values) {
            *map.entry(value.round() as i64).or_default() += length;
        }
        if let (Some(object), "G1") = (state.object, line.command) {
            let mut hash = DefaultHasher::new();
            [from, to].iter().flatten().map(|v| (v * 100.).round() as i64).for_each(|v| v.hash(&mut hash));
            ((e * 1e4).round() as i64).hash(&mut hash);
            let settings = [feed, state.fans[0].round() as i64, state.acceleration.unwrap_or(0.).round() as i64];
            plate.paths.entry((object, hash.finish())).or_default().push(settings);
        }
    });
    Ok(plate)
}

/// The values two length maps lay differently, largest difference first.
fn differing(a: &BTreeMap<i64, f64>, b: &BTreeMap<i64, f64>, limit: usize) -> Vec<(i64, f64, f64)> {
    let mut rows: Vec<(i64, f64, f64)> = a.keys().chain(b.keys()).collect::<std::collections::BTreeSet<_>>().into_iter()
        .map(|k| (*k, a.get(k).copied().unwrap_or(0.), b.get(k).copied().unwrap_or(0.)))
        .filter(|(_, x, y)| (x - y).abs() >= 1.)
        .collect();
    rows.sort_by(|p, q| (q.1 - q.2).abs().total_cmp(&(p.1 - p.2).abs()));
    rows.truncate(limit);
    rows
}

fn counts(a: &BTreeMap<String, usize>, b: &BTreeMap<String, usize>) -> Vec<(String, usize, usize)> {
    a.keys().chain(b.keys()).collect::<std::collections::BTreeSet<_>>().into_iter()
        .map(|k| (k.clone(), a.get(k).copied().unwrap_or(0), b.get(k).copied().unwrap_or(0)))
        .filter(|(_, x, y)| x != y)
        .collect()
}

pub fn run(args: Options) -> Result<i32> {
    let (a, b) = (read(&args.a)?, read(&args.b)?);
    println!("A {}\nB {}", args.a.display(), args.b.display());
    let mut out = json!({"a": args.a, "b": args.b});

    println!("\nby part and feature, where what is commanded differs (lengths in m):");
    let mut groups = Vec::new();
    let keys: std::collections::BTreeSet<_> = a.groups.keys().chain(b.groups.keys()).collect();
    let empty = Group::default();
    for key in keys {
        let (ga, gb) = (a.groups.get(key).unwrap_or(&empty), b.groups.get(key).unwrap_or(&empty));
        let rows: Vec<_> = (0..4).map(|i| differing(&ga.by[i], &gb.by[i], args.limit)).collect();
        if rows.iter().all(Vec::is_empty) {
            continue;
        }
        println!("  {} / {}: A {:.2}, B {:.2}", key.0, key.1, ga.length / 1000., gb.length / 1000.);
        let mut reading = serde_json::Map::new();
        for ((name, unit), rows) in READINGS.iter().zip(&rows) {
            if rows.is_empty() {
                continue;
            }
            let text: Vec<String> = rows.iter().map(|(v, x, y)| format!("{v} {unit} A {:.2} B {:.2}", x / 1000., y / 1000.)).collect();
            println!("    {name}: {}", text.join("; "));
            reading.insert(name.to_string(), json!(rows.iter().map(|(v, x, y)| json!({"value": v, "a_mm": x, "b_mm": y})).collect::<Vec<_>>()));
        }
        groups.push(json!({"part": key.0, "feature": key.1, "a_mm": ga.length, "b_mm": gb.length, "differing": reading}));
    }
    out["by_part_and_feature"] = json!(groups);

    for (title, name, (x, y)) in [("printer-side commands", "commands", (&a.commands, &b.commands)),
                                  ("retractions, primes, lifts and travels", "travels", (&a.travels, &b.travels))] {
        let rows = counts(x, y);
        println!("\n{title} whose counts differ:{}", if rows.is_empty() { " none" } else { "" });
        for (k, m, n) in rows.iter().take(4 * args.limit) {
            println!("  {k}: A {m}, B {n}");
        }
        out[name] = json!(rows.iter().map(|(k, m, n)| json!({"kind": k, "a": m, "b": n})).collect::<Vec<_>>());
    }

    let same = a.heats == b.heats;
    println!("\nheating commands: {}", if same { "the same".to_string() } else { format!("A {:?}\n                  B {:?}", a.heats, b.heats) });
    out["heating"] = json!({"a": a.heats, "b": b.heats});

    println!("\nmoves on the same path under other settings, by part:");
    let mut parts: BTreeMap<i64, (usize, usize, usize, BTreeMap<String, usize>)> = BTreeMap::new();
    for ((object, key), va) in &a.paths {
        let entry = parts.entry(*object).or_default();
        entry.0 += va.len();
        let Some(vb) = b.paths.get(&(*object, *key)) else { continue };
        let (mut sa, mut sb) = (va.clone(), vb.clone());
        sa.sort();
        sb.sort();
        for (p, q) in sa.iter().zip(&sb) {
            if p != q {
                entry.2 += 1;
                *entry.3.entry(format!("feed {}->{} mm/s, fan {}->{}%, acceleration {}->{}", p[0], q[0], p[1], q[1], p[2], q[2])).or_default() += 1;
            }
        }
    }
    for ((object, _), vb) in &b.paths {
        parts.entry(*object).or_default().1 += vb.len();
    }
    let mut same_path = Vec::new();
    for (object, (na, nb, other, patterns)) in &parts {
        println!("  {}: moves A {na}, B {nb}; same path, other settings {other}", part(Some(*object)));
        let mut patterns: Vec<_> = patterns.iter().collect();
        patterns.sort_by(|p, q| q.1.cmp(p.1));
        for (pattern, n) in patterns.iter().take(args.limit) {
            println!("      {n} x {pattern}");
        }
        same_path.push(json!({"part": part(Some(*object)), "a_moves": na, "b_moves": nb, "same_path_other_settings": other,
            "patterns": patterns.iter().map(|(p, n)| json!({"settings": p, "moves": n})).collect::<Vec<Value>>()}));
    }
    out["same_path_other_settings"] = json!(same_path);
    if let Some(path) = &args.json {
        std::fs::write(path, serde_json::to_string_pretty(&out)? + "\n")?;
    }
    Ok(0)
}
