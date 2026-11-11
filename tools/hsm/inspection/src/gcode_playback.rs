//! On-demand playback turns consecutive sliced layers into an accelerating H2C motion study.
use super::super::{arc, layer_range, slice_text, word};
use super::{base64, render};
use anyhow::{Context, Result, ensure};
use clap::Args;
use hsm_print_prep::gcode::words;
use serde_json::json;
use sha2::{Digest, Sha256};
use std::{fs, path::PathBuf};

const TEMPLATE: &str = include_str!("../../../gcode/playback-page.html");
const THEME: &str = include_str!("../../../viz/inline-mobile/assets/theme.js");
const COORDINATE_SCALE: f64 = 100.;

#[derive(Args)]
pub struct Options {
    slice: PathBuf,
    /// Consecutive layers in Bambu Studio's numbering.
    #[arg(long)]
    layers: String,
    #[arg(long, default_value_t = 1)]
    plate: usize,
    #[arg(long, default_value_t = 30.)]
    speed: f64,
    /// Optional binary STL of the printer's build plate.
    #[arg(long)]
    bed_model: Option<PathBuf>,
    #[arg(long)]
    title: String,
    #[arg(long)]
    out: PathBuf,
}

#[derive(Clone, Debug)]
struct Move {
    start: [f64; 3],
    end: [f64; 3],
    unit: [f64; 4],
    length: f64,
    cruise: f64,
    acceleration: f64,
    jerk: [f64; 4],
    layer: usize,
    width: f64,
    height: f64,
    feature: usize,
    extrusion: bool,
    stop_after: bool,
    entry: f64,
    peak: f64,
    exit: f64,
    seconds: f64,
}

struct Motion {
    moves: Vec<Move>,
    features: Vec<String>,
    bed: [f64; 2],
}

fn distance(a: [f64; 3], b: [f64; 3]) -> f64 {
    a.iter()
        .zip(b)
        .map(|(a, b)| (a - b).powi(2))
        .sum::<f64>()
        .sqrt()
}

fn read(text: &str, first: usize, last: usize) -> Result<Motion> {
    let mut position = [0.; 3];
    let mut e = 0.;
    let (mut absolute, mut relative_e) = (true, true);
    let (mut layer, mut width, mut height, mut feature) = (0, 0.42, 0.24, 0);
    let mut features = vec!["Travel".to_string()];
    let mut axis_acceleration = [20000., 20000., 500., 5000.];
    let mut max_speed = [1000., 1000., 30., 50.];
    let mut jerk = [9., 9., 3., 2.5];
    let mut acceleration = [20000., 5000., 9000.];
    let (mut feed, mut multiplier) = (0., 1.);
    let mut moves: Vec<Move> = Vec::new();
    let mut bed = [330_f64, 320_f64];
    let mut xy_plane = true;
    for (index, raw) in text.lines().enumerate() {
        let raw = raw.trim();
        if let Some(comment) = raw.strip_prefix(';').map(str::trim) {
            if let Some(value) = comment.strip_prefix("Z_HEIGHT:") {
                value.trim().parse::<f64>().context("invalid layer Z")?;
                layer += 1;
                if layer > last.saturating_add(1) {
                    break;
                }
            } else if let Some(value) = comment.strip_prefix("LAYER_HEIGHT:") {
                height = value.trim().parse()?;
            } else if let Some(value) = comment.strip_prefix("LINE_WIDTH:") {
                width = value.trim().parse()?;
            } else if let Some(value) = comment.strip_prefix("FEATURE:") {
                let value = value.trim();
                feature = features.iter().position(|v| v == value).unwrap_or_else(|| {
                    features.push(value.to_string());
                    features.len() - 1
                });
            } else if let Some(value) = comment.strip_prefix("printable_area =") {
                for point in value.trim().split(',') {
                    if let Some((x, y)) = point.split_once('x') {
                        bed[0] = bed[0].max(x.parse::<f64>()?);
                        bed[1] = bed[1].max(y.parse::<f64>()?);
                    }
                }
            }
            continue;
        }
        let code = raw.split(';').next().unwrap_or("").trim();
        let Some(command) = code.split_whitespace().next() else {
            continue;
        };
        let values = words(&code[command.len()..]);
        match command {
            "G90" => absolute = true,
            "G91" => absolute = false,
            "M82" => relative_e = false,
            "M83" => relative_e = true,
            "G17" => xy_plane = true,
            "G18" | "G19" => xy_plane = false,
            "G92" => {
                for (i, key) in b"XYZ".iter().enumerate() {
                    position[i] = word(&values, *key).unwrap_or(position[i]);
                }
                e = word(&values, b'E').unwrap_or(e);
            }
            "M201" | "M203" | "M205" => {
                let target = match command {
                    "M201" => &mut axis_acceleration,
                    "M203" => &mut max_speed,
                    _ => &mut jerk,
                };
                for (i, key) in b"XYZE".iter().enumerate() {
                    if let Some(value) = word(&values, *key).filter(|v| *v > 0.) {
                        target[i] = value;
                    }
                }
            }
            "M204" => {
                if let Some(value) = word(&values, b'S').filter(|v| *v > 0.) {
                    acceleration[0] = value;
                    acceleration[2] = value;
                }
                for (i, key) in b"PRT".iter().enumerate() {
                    if let Some(value) = word(&values, *key).filter(|v| *v > 0.) {
                        acceleration[i] = value;
                    }
                }
            }
            "M220" => {
                multiplier = word(&values, b'S').unwrap_or(100.) / 100.;
            }
            "M400" | "G4" | "G28" => {
                if let Some(last) = moves.last_mut() {
                    last.stop_after = true;
                }
            }
            "G0" | "G1" | "G2" | "G3" => {
                if let Some(value) = word(&values, b'F') {
                    feed = value / 60.;
                }
                let mut end = position;
                for (i, key) in b"XYZ".iter().enumerate() {
                    if let Some(value) = word(&values, *key) {
                        end[i] = if absolute { value } else { position[i] + value };
                    }
                }
                let delta_e = word(&values, b'E').map_or(0., |value| {
                    let delta = if relative_e { value } else { value - e };
                    e = if relative_e { e + value } else { value };
                    delta
                });
                if layer >= first.saturating_sub(1).max(1) && layer > 0 {
                    let points = if command == "G2" || command == "G3" {
                        ensure!(
                            xy_plane,
                            "playback supports XY-plane arcs; other plane at line {}",
                            index + 1
                        );
                        arc(position, end, &values, command == "G2")
                    } else {
                        vec![end]
                    };
                    let full_length = points
                        .iter()
                        .fold((position, 0.), |(previous, sum), p| {
                            (*p, sum + distance(previous, *p))
                        })
                        .1;
                    let mut start = position;
                    let count = points.len();
                    for end in points {
                        let xyz_length = distance(start, end);
                        let piece_e = if full_length > 1e-12 {
                            delta_e * xyz_length / full_length
                        } else {
                            delta_e / count as f64
                        };
                        let length = if xyz_length > 1e-12 {
                            xyz_length
                        } else {
                            piece_e.abs()
                        };
                        if length > 1e-12 {
                            ensure!(
                                feed > 0. && multiplier > 0.,
                                "move has no positive feed at line {}",
                                index + 1
                            );
                            let unit = [
                                (end[0] - start[0]) / length,
                                (end[1] - start[1]) / length,
                                (end[2] - start[2]) / length,
                                piece_e / length,
                            ];
                            let mut cruise = feed * multiplier;
                            let mut a = acceleration[if xyz_length < 1e-12 {
                                1
                            } else if piece_e > 0. {
                                0
                            } else {
                                2
                            }];
                            for axis in 0..4 {
                                if unit[axis].abs() > 1e-12 {
                                    cruise = cruise.min(max_speed[axis] / unit[axis].abs());
                                    a = a.min(axis_acceleration[axis] / unit[axis].abs());
                                }
                            }
                            moves.push(Move {
                                start,
                                end,
                                unit,
                                length,
                                cruise,
                                acceleration: a,
                                jerk,
                                layer,
                                width,
                                height,
                                feature,
                                extrusion: piece_e > 0. && xyz_length > 1e-12,
                                stop_after: false,
                                entry: 0.,
                                peak: 0.,
                                exit: 0.,
                                seconds: 0.,
                            });
                        }
                        start = end;
                    }
                }
                position = end;
            }
            _ => {}
        }
    }
    ensure!(!moves.is_empty(), "no moves in the requested layers");
    plan(&mut moves);
    moves.retain(|m| m.layer >= first && m.layer <= last);
    ensure!(!moves.is_empty(), "no moves in the requested layers");
    Ok(Motion {
        moves,
        features,
        bed,
    })
}

fn plan(moves: &mut [Move]) {
    let mut boundary = vec![0.; moves.len() + 1];
    for i in 1..moves.len() {
        let (previous, current) = (&moves[i - 1], &moves[i]);
        if previous.stop_after {
            continue;
        }
        let mut cap = previous.cruise.min(current.cruise);
        for axis in 0..4 {
            let change = (current.unit[axis] - previous.unit[axis]).abs();
            if change > 1e-12 {
                cap = cap.min(previous.jerk[axis].min(current.jerk[axis]) / change);
            }
        }
        let (previous_xy, current_xy) = (
            previous.unit[0].hypot(previous.unit[1]),
            current.unit[0].hypot(current.unit[1]),
        );
        if previous_xy > 1e-9 && current_xy > 1e-9 {
            let cosine = ((previous.unit[0] * current.unit[0]
                + previous.unit[1] * current.unit[1])
                / (previous_xy * current_xy))
                .clamp(-1., 1.);
            let sine_half = ((1. - cosine) / 2.).max(0.).sqrt();
            if sine_half > 1e-5 && sine_half < 0.25 {
                let radius = (previous.length * previous_xy).min(current.length * current_xy)
                    / (2. * sine_half);
                cap = cap.min((previous.acceleration.min(current.acceleration) * radius).sqrt());
            }
        }
        boundary[i] = cap;
    }
    for i in (0..moves.len()).rev() {
        boundary[i] = boundary[i]
            .min((boundary[i + 1].powi(2) + 2. * moves[i].acceleration * moves[i].length).sqrt());
    }
    for i in 0..moves.len() {
        boundary[i + 1] = boundary[i + 1]
            .min((boundary[i].powi(2) + 2. * moves[i].acceleration * moves[i].length).sqrt());
        let m = &mut moves[i];
        m.entry = boundary[i];
        m.exit = boundary[i + 1];
        m.peak = m
            .cruise
            .min((m.acceleration * m.length + (m.entry.powi(2) + m.exit.powi(2)) / 2.).sqrt());
        let accelerating = (m.peak.powi(2) - m.entry.powi(2)) / (2. * m.acceleration);
        let braking = (m.peak.powi(2) - m.exit.powi(2)) / (2. * m.acceleration);
        m.seconds = (m.peak - m.entry) / m.acceleration
            + (m.peak - m.exit) / m.acceleration
            + (m.length - accelerating - braking).max(0.) / m.peak;
    }
}

fn bed_triangles(path: &PathBuf, origin: [f64; 3]) -> Result<String> {
    let bytes = fs::read(path)?;
    ensure!(bytes.len() >= 84, "bed model is not a binary STL");
    let count = u32::from_le_bytes(bytes[80..84].try_into()?) as usize;
    ensure!(
        count.checked_mul(50).and_then(|n| n.checked_add(84)) == Some(bytes.len()),
        "bed model is not a binary STL"
    );
    let mut points = Vec::new();
    for triangle in bytes[84..].chunks_exact(50) {
        for point in triangle[12..48].chunks_exact(12) {
            for (axis, coordinate) in point.chunks_exact(4).enumerate() {
                let value = f32::from_le_bytes(coordinate.try_into()?) as f64 - origin[axis];
                ensure!(
                    value.is_finite() && (value * COORDINATE_SCALE).abs() <= i16::MAX as f64,
                    "bed model coordinate exceeds the playback range"
                );
                points
                    .extend_from_slice(&((value * COORDINATE_SCALE).round() as i16).to_le_bytes());
            }
        }
    }
    Ok(base64(&points))
}

pub fn run(args: Options) -> Result<i32> {
    ensure!(
        args.speed.is_finite() && args.speed > 0.,
        "playback speed must be positive"
    );
    let selected = layer_range(&args.layers)?;
    let text = slice_text(&args.slice, args.plate)?;
    let gcode_sha256 = format!("{:x}", Sha256::digest(text.as_bytes()));
    let motion = read(&text, *selected.start(), *selected.end())?;
    let origin = [motion.bed[0] / 2., motion.bed[1] / 2., 0.];
    let mut positions = Vec::new();
    for p in std::iter::once(motion.moves[0].start).chain(motion.moves.iter().map(|m| m.end)) {
        for (axis, value) in p.iter().enumerate() {
            let coordinate = (value - origin[axis]) * COORDINATE_SCALE;
            ensure!(
                coordinate.is_finite() && coordinate.abs() <= i16::MAX as f64,
                "selected coordinates exceed the playback range"
            );
            positions.extend_from_slice(&(coordinate.round() as i16).to_le_bytes());
        }
    }
    let mut kinematics = Vec::new();
    let mut layers = Vec::new();
    let mut flags = Vec::new();
    let mut dimensions = Vec::new();
    let mut features = Vec::new();
    let mut seconds = 0.;
    for m in &motion.moves {
        seconds += m.seconds;
        for value in [seconds, m.length, m.entry, m.peak, m.exit, m.acceleration] {
            ensure!(value.is_finite(), "non-finite playback timing");
            kinematics.extend_from_slice(&(value as f32).to_le_bytes());
        }
        layers.extend_from_slice(&u16::try_from(m.layer)?.to_le_bytes());
        flags.push(u8::from(m.extrusion));
        dimensions.push((m.width * 100.).clamp(1., 255.).round() as u8);
        dimensions.push((m.height * 100.).clamp(1., 255.).round() as u8);
        features.push(u8::try_from(m.feature)?);
    }
    let data = json!({ "positions":base64(&positions), "kinematics":base64(&kinematics), "layers":base64(&layers),
        "flags":base64(&flags), "dimensions":base64(&dimensions), "feature_ids":base64(&features), "features":motion.features,
        "bed":motion.bed, "bed_mesh":args.bed_model.as_ref().map(|p|bed_triangles(p,origin)).transpose()?,
        "origin":origin, "speed":args.speed, "seconds":seconds, "gcode_sha256":gcode_sha256,
        "source":args.slice.file_name().unwrap_or_default().to_string_lossy(), "selected_layers":[selected.start(),selected.end()] });
    let page = render(TEMPLATE, &args.title, "", &data)?.replace("/*THEME*/", THEME);
    fs::write(&args.out, &page).with_context(|| format!("writing {}", args.out.display()))?;
    println!(
        "{}  {:.1} MB · {} moves · {:.1} estimated motion seconds",
        args.out.display(),
        page.len() as f64 / 1e6,
        motion.moves.len(),
        seconds
    );
    Ok(0)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn short_moves_accelerate_and_turns_obey_junction_limits() -> Result<()> {
        let code = "M83\nM201 X100 Y100 Z100 E100\nM203 X100 Y100 Z100 E100\nM204 S100\nM205 X2 Y2 Z2 E2\n; Z_HEIGHT: .2\nG1 X0 Y0 Z.2 F6000\nG1 X10 E1\nG1 X20 E1\nG1 Y10 E1\n";
        let motion = read(code, 1, 1)?;
        let m = &motion.moves;
        assert!(m[1].peak < m[1].cruise);
        assert!(m[1].exit > m[2].exit);
        assert!(m[2].exit <= 2.);
        assert!(m.iter().all(|m| m.seconds >= m.length / m.cruise));
        assert_eq!(m.last().unwrap().exit, 0.);
        Ok(())
    }
    #[test]
    fn consecutive_layers_keep_relative_motion_and_nonplanar_z() -> Result<()> {
        let code = "M83\nG1 X10 Y10 Z.2 F600\n; Z_HEIGHT: .2\nG1 X11 E.1\n; Z_HEIGHT: .4\nG91\nG1 X1 Z.3 E.1\nG90\n; Z_HEIGHT: .6\nG1 X13 Z.6 E.1\n";
        let motion = read(code, 2, 3)?;
        assert_eq!(motion.moves.len(), 2);
        assert_eq!(motion.moves[0].start, [11., 10., 0.2]);
        assert_eq!(motion.moves[0].end, [12., 10., 0.5]);
        assert_eq!(motion.moves[1].layer, 3);
        Ok(())
    }
}
