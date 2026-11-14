//! course-field lays a donor slice's roads through a course field and prints every piece it
//! lays, or prints where the field places a grid of donor points.
//!
//!   course-field roads FIELD RECEIPT DONOR.gcode [--incline DEG] [--displacement X,Y,Z] [--piece MM]
//!   course-field sample FIELD RECEIPT --y FROM:TO:STEPS --u FROM:TO:STEPS [--x X] [field options]
//!
//! FIELD is `shaft-ease` (the base, from a shaft transition receipt, with the base's incline) or
//! `shoulder-hold` (the tip, from a tip warp receipt, with the donor's displacement onto the
//! plate). `roads` writes one tab-separated row per laid piece: course, feature, start, end and
//! extrusion. `sample` writes each grid point and the plate point the field places it at.

use anyhow::{Context, Result, bail};
use hsm_print_prep::course_field::{field_from_receipt, lay, read_moves};
use std::io::{BufWriter, Write};

fn option<'a>(args: &'a [String], name: &str) -> Option<&'a str> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).map(String::as_str)
}

fn numbers(text: &str, sep: char) -> Result<Vec<f64>> {
    text.split(sep).map(|v| v.trim().parse::<f64>().with_context(|| format!("{v} is not a number"))).collect()
}

fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let (command, kind, receipt) = match args.as_slice() {
        [c, k, r, ..] => (c.as_str(), k.as_str(), r.as_str()),
        _ => bail!("usage: course-field roads|sample FIELD RECEIPT ..."),
    };
    let receipt: serde_json::Value =
        serde_json::from_slice(&std::fs::read(receipt).with_context(|| format!("reading {receipt}"))?)?;
    let incline = option(&args, "--incline").map(str::parse::<f64>).transpose()?;
    let displacement = match option(&args, "--displacement") {
        Some(text) => {
            let v = numbers(text, ',')?;
            [v[0], v[1], v[2]]
        }
        None => [0.0; 3],
    };
    let piece = option(&args, "--piece").map(str::parse::<f64>).transpose()?.unwrap_or(1.0);
    let field = field_from_receipt(kind, &receipt, incline, displacement, piece)?;
    let mut out = BufWriter::new(std::io::stdout().lock());
    match command {
        "roads" => {
            let donor = args.get(3).context("roads needs a donor G-code")?;
            let text = std::fs::read_to_string(donor).with_context(|| format!("reading {donor}"))?;
            for m in read_moves(&text)?.iter().filter(|m| m.deposition()) {
                for r in lay(m, field.as_ref()) {
                    let [a, b] = [r.start, r.end];
                    writeln!(out, "{}\t{}\t{:?}\t{:?}\t{:?}\t{:?}\t{:?}\t{:?}\t{:?}",
                        m.layer, m.feature, a[0], a[1], a[2], b[0], b[1], b[2], r.e)?;
                }
            }
        }
        "sample" => {
            let grid = |name: &str| -> Result<Vec<f64>> {
                let v = numbers(option(&args, name).with_context(|| format!("sample needs {name}"))?, ':')?;
                let steps = v[2] as usize;
                Ok((0..=steps).map(|i| v[0] + (v[1] - v[0]) * i as f64 / steps as f64).collect())
            };
            let x = option(&args, "--x").map(str::parse::<f64>).transpose()?.unwrap_or(0.0);
            for y in grid("--y")? {
                for u in grid("--u")? {
                    let p = field.place([x, y, u]);
                    writeln!(out, "{y:?}\t{u:?}\t{:?}\t{:?}\t{:?}", p[0], p[1], p[2])?;
                }
            }
        }
        _ => bail!("course-field knows roads and sample"),
    }
    Ok(())
}
