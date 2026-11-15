//! The acceleration planner that times a sliced plate's moves: hsm-gcode's playback draws them,
//! and the trial plates take their motion estimate, first-course time and printer progress from it.
use crate::gcode::words;
use anyhow::{Context, Result, ensure};

#[derive(Clone, Debug)]
pub struct Move {
    pub start: [f64; 3],
    pub end: [f64; 3],
    pub unit: [f64; 4],
    pub length: f64,
    pub cruise: f64,
    pub acceleration: f64,
    pub jerk: [f64; 4],
    pub layer: usize,
    pub width: f64,
    pub height: f64,
    pub feature: usize,
    pub extrusion: bool,
    pub stop_after: bool,
    pub entry: f64,
    pub peak: f64,
    pub exit: f64,
    pub seconds: f64,
    /// The G-code line the move comes from, counted from one.
    pub line: usize,
}

pub struct Motion {
    pub moves: Vec<Move>,
    pub features: Vec<String>,
    pub bed: [f64; 2],
}

pub fn distance(a: [f64; 3], b: [f64; 3]) -> f64 {
    a.iter()
        .zip(b)
        .map(|(a, b)| (a - b).powi(2))
        .sum::<f64>()
        .sqrt()
}

fn word(words: &[(u8, f64)], key: u8) -> Option<f64> {
    words.iter().find(|(k, _)| *k == key).map(|(_, v)| *v)
}

/// The points an XY-plane arc passes through, ending on its commanded end.
pub fn arc(start: [f64; 3], end: [f64; 3], words: &[(u8, f64)], clockwise: bool) -> Vec<[f64; 3]> {
    let centre = [
        start[0] + word(words, b'I').unwrap_or(0.),
        start[1] + word(words, b'J').unwrap_or(0.),
    ];
    let radius = (start[0] - centre[0]).hypot(start[1] - centre[1]);
    let first = (start[1] - centre[1]).atan2(start[0] - centre[0]);
    let mut sweep = (end[1] - centre[1]).atan2(end[0] - centre[0]) - first;
    if clockwise {
        if sweep >= -1e-9 {
            sweep -= std::f64::consts::TAU;
        }
    } else if sweep <= 1e-9 {
        sweep += std::f64::consts::TAU;
    }
    let count = ((sweep.abs() * radius / 0.25).ceil() as usize).max(1);
    let mut points = (1..=count)
        .map(|i| {
            let t = i as f64 / count as f64;
            let angle = first + sweep * t;
            [
                centre[0] + radius * angle.cos(),
                centre[1] + radius * angle.sin(),
                start[2] + (end[2] - start[2]) * t,
            ]
        })
        .collect::<Vec<_>>();
    points[count - 1] = end;
    points
}

/// The planned moves of layers `first` to `last`, in Bambu Studio's numbering.
pub fn read(text: &str, first: usize, last: usize) -> Result<Motion> {
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
                                line: index + 1,
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

/// A whole plate's motion estimate: its planned seconds, the span from the first to the last
/// deposition of the plate's objects on the first bed layer, and each move's line and end time.
pub struct Timing {
    pub seconds: f64,
    pub first_course_seconds: f64,
    pub ends: Vec<(usize, f64)>,
}

pub fn timing(text: &str) -> Result<Timing> {
    let motion = read(text, 1, usize::MAX)?;
    let mut object = Vec::with_capacity(text.len() / 32);
    let mut current = false;
    for line in text.lines() {
        if line.starts_with("; start printing object, unique label id: ") {
            current = true;
        } else if line.starts_with("; stop printing object, unique label id: ") {
            current = false;
        }
        object.push(current);
    }
    let mut at = 0.;
    let mut ends = Vec::with_capacity(motion.moves.len());
    let mut deposits = Vec::new();
    for m in &motion.moves {
        let start = at;
        at += m.seconds;
        ends.push((m.line, at));
        if m.extrusion && object[m.line - 1] {
            deposits.push((m.start[2], m.end[2], start, at));
        }
    }
    let bed = deposits.iter().map(|d| d.0.max(d.1)).fold(f64::INFINITY, f64::min);
    let course: Vec<_> = deposits.iter().filter(|d| (d.0 - bed).abs() < 1e-5 && (d.1 - bed).abs() < 1e-5).collect();
    let (first, last) = (course.first().context("the plate deposits nothing on the bed")?, course.last().unwrap());
    ensure!(at > 0., "the motion estimate takes no time");
    Ok(Timing { seconds: at, first_course_seconds: last.3 - first.2, ends })
}
