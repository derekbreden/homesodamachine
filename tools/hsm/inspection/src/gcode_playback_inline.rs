//! Pack a whole-plate motion timeline and deposited bead paths for playback.
use super::{Motion, Move, base64, bead_dimensions, coordinates, distance, playback_page};
use anyhow::{Result, bail};
use flate2::{Compression, write::GzEncoder};
use serde_json::{Value, json};
use std::{io::Write, ops::Range};

const INLINE_BYTES: usize = 1_000_000;
const ARCHIVE_BYTES: usize = 8_000_000;
const ARCHIVE_BEAD_ROADS: usize = 350_000;
const SAMPLE_SECONDS: f64 = 0.25;
const MAX_SAMPLE_INTERVALS: usize = 32_768;
const ROAD_TOLERANCES_MM: [f64; 3] = [0.12, 0.22, 0.35];
const SURFACE_TOLERANCE_MM: f64 = 0.22;
const Z_WEIGHT: f64 = 4.;
const MAX_RUN_MOVES: usize = 512;

#[repr(u8)]
#[derive(Clone, Copy, PartialEq, Eq)]
enum RoadKind {
    Model = 0,
    Support = 1,
    Interface = 2,
    Bridge = 3,
}

impl RoadKind {
    fn from_feature(feature: &str) -> Self {
        match feature {
            "Support interface" => Self::Interface,
            "Bridge" | "Internal Bridge" => Self::Bridge,
            other if other.starts_with("Support") => Self::Support,
            _ => Self::Model,
        }
    }

    fn is_support(self) -> bool {
        matches!(self, Self::Support | Self::Interface)
    }
}

fn compressed(bytes: &[u8]) -> Result<String> {
    let mut encoder = GzEncoder::new(Vec::new(), Compression::default());
    encoder.write_all(bytes)?;
    Ok(base64(&encoder.finish()?))
}

fn separation_squared(point: [f64; 3], start: [f64; 3], end: [f64; 3]) -> f64 {
    let edge = [
        end[0] - start[0],
        end[1] - start[1],
        (end[2] - start[2]) * Z_WEIGHT,
    ];
    let offset = [
        point[0] - start[0],
        point[1] - start[1],
        (point[2] - start[2]) * Z_WEIGHT,
    ];
    let length_squared: f64 = edge.iter().map(|component| component * component).sum();
    let fraction = if length_squared > 0. {
        (edge.iter().zip(offset).map(|(a, b)| a * b).sum::<f64>() / length_squared).clamp(0., 1.)
    } else {
        0.
    };
    edge.iter()
        .zip(offset)
        .map(|(a, b)| (b - a * fraction).powi(2))
        .sum()
}

fn simplify(moves: &[Move], run: Range<usize>, tolerance: f64, roads: &mut Vec<Range<usize>>) {
    let mut pending = vec![run];
    while let Some(span) = pending.pop() {
        let start = moves[span.start].start;
        let end = moves[span.end - 1].end;
        let mut worst = tolerance * tolerance;
        let mut split = None;
        for (offset, movement) in moves[span.start..span.end - 1].iter().enumerate() {
            let error = separation_squared(movement.end, start, end);
            if error > worst {
                worst = error;
                split = Some(span.start + offset + 1);
            }
        }
        if let Some(split) = split {
            pending.push(split..span.end);
            pending.push(span.start..split);
        } else {
            roads.push(span);
        }
    }
}

fn deposition(
    motion: &Motion,
    kinds: &[RoadKind],
    tolerance: f64,
    surface_paths: bool,
) -> Vec<Range<usize>> {
    let mut roads = Vec::new();
    let visible: Vec<_> = motion
        .features
        .iter()
        .map(|name| {
            !surface_paths
                || !matches!(
                    name.as_str(),
                    "Inner wall" | "Sparse infill" | "Internal solid infill" | "Gap infill"
                )
        })
        .collect();
    let deposits = |movement: &Move| movement.extrusion && visible[movement.feature];
    let mut start = 0;
    while start < motion.moves.len() {
        let first = &motion.moves[start];
        if !deposits(first) {
            start += 1;
            continue;
        }
        let dimensions = bead_dimensions(first);
        let mut end = start + 1;
        while end < motion.moves.len() && end - start < MAX_RUN_MOVES {
            let next = &motion.moves[end];
            if !deposits(next)
                || next.layer != first.layer
                || bead_dimensions(next) != dimensions
                || kinds[next.feature] != kinds[first.feature]
                || next.start != motion.moves[end - 1].end
            {
                break;
            }
            end += 1;
        }
        simplify(&motion.moves, start..end, tolerance, &mut roads);
        start = end;
    }
    roads
}

fn sampled_position(movement: &Move, elapsed: f64) -> ([f64; 3], f64) {
    let acceleration = movement.acceleration;
    let accelerate = ((movement.peak - movement.entry) / acceleration).max(0.);
    let brake = ((movement.peak - movement.exit) / acceleration).max(0.);
    let distance_up = (movement.peak.powi(2) - movement.entry.powi(2)) / (2. * acceleration);
    let distance_down = (movement.peak.powi(2) - movement.exit.powi(2)) / (2. * acceleration);
    let cruise = (movement.length - distance_up - distance_down).max(0.) / movement.peak;
    let (travelled, speed) = if elapsed < accelerate {
        (
            movement.entry * elapsed + acceleration * elapsed.powi(2) / 2.,
            movement.entry + acceleration * elapsed,
        )
    } else if elapsed < accelerate + cruise {
        (
            distance_up + movement.peak * (elapsed - accelerate),
            movement.peak,
        )
    } else {
        let time = (elapsed - accelerate - cruise).clamp(0., brake);
        (
            movement.length - distance_down + movement.peak * time
                - acceleration * time.powi(2) / 2.,
            (movement.peak - acceleration * time).max(movement.exit),
        )
    };
    let fraction = (travelled / movement.length).clamp(0., 1.);
    let point = std::array::from_fn(|axis| {
        movement.start[axis] + (movement.end[axis] - movement.start[axis]) * fraction
    });
    (
        point,
        speed * distance(movement.start, movement.end) / movement.length,
    )
}

fn road_bytes(
    motion: &Motion,
    origin: [f64; 3],
    roads: &[Range<usize>],
    kinds: &[RoadKind],
) -> Result<(Vec<u8>, Vec<u8>)> {
    let mut bytes = Vec::new();
    let mut road_kinds = Vec::with_capacity(roads.len());
    let mut previous_end = [0_i16; 3];
    for span in roads {
        let first = &motion.moves[span.start];
        let start = coordinates(first.start, origin)?;
        let end = coordinates(motion.moves[span.end - 1].end, origin)?;
        for axis in 0..3 {
            bytes.extend_from_slice(&start[axis].wrapping_sub(previous_end[axis]).to_le_bytes());
        }
        for axis in 0..3 {
            bytes.extend_from_slice(&end[axis].wrapping_sub(start[axis]).to_le_bytes());
        }
        bytes.extend_from_slice(&bead_dimensions(first));
        let kind = kinds[first.feature];
        bytes.push(u8::from(kind.is_support()));
        road_kinds.push(kind as u8);
        previous_end = end;
    }
    Ok((bytes, road_kinds))
}

fn track_bytes(
    motion: &Motion,
    origin: [f64; 3],
    end_times: &[f64],
    roads: &[Range<usize>],
    intervals: usize,
    interval: f64,
) -> Result<Vec<u8>> {
    let duration = *end_times.last().unwrap();
    let mut movement_index = 0;
    let mut deposited = 0;
    let mut bytes = Vec::new();
    for sample in 0..=intervals {
        let time = if sample == intervals {
            duration
        } else {
            sample as f64 * interval
        };
        while end_times[movement_index] < time {
            movement_index += 1;
        }
        while deposited < roads.len() && end_times[roads[deposited].end - 1] <= time {
            deposited += 1;
        }
        let movement = &motion.moves[movement_index];
        let start = if movement_index == 0 {
            0.
        } else {
            end_times[movement_index - 1]
        };
        let (point, speed) = sampled_position(movement, time - start);
        for coordinate in coordinates(point, origin)? {
            bytes.extend_from_slice(&coordinate.to_le_bytes());
        }
        bytes.extend_from_slice(&(speed.round() as u16).to_le_bytes());
        bytes.extend_from_slice(&u16::try_from(movement.layer)?.to_le_bytes());
        bytes.push(if movement.extrusion {
            u8::try_from(movement.feature)?
        } else {
            0
        });
        bytes.extend_from_slice(&u32::try_from(deposited)?.to_le_bytes());
    }
    Ok(bytes)
}

pub(super) fn sampled_output(
    title: &str,
    data: &mut Value,
    motion: &Motion,
    origin: [f64; 3],
    end_times: &[f64],
    data_only: bool,
) -> Result<String> {
    let duration = *end_times.last().unwrap();
    let intervals = ((duration / SAMPLE_SECONDS).ceil() as usize).clamp(1, MAX_SAMPLE_INTERVALS);
    let interval = duration / intervals as f64;
    let byte_limit = if data_only {
        ARCHIVE_BYTES
    } else {
        INLINE_BYTES
    };
    let attempts = ROAD_TOLERANCES_MM
        .into_iter()
        .map(|tolerance| (tolerance, false))
        .chain(data_only.then_some((SURFACE_TOLERANCE_MM, true)));
    let kinds: Vec<_> = motion
        .features
        .iter()
        .map(|name| RoadKind::from_feature(name))
        .collect();
    for (tolerance, surface_paths) in attempts {
        let roads = deposition(motion, &kinds, tolerance, surface_paths);
        if data_only && !surface_paths && roads.len() > ARCHIVE_BEAD_ROADS {
            continue;
        }
        let (road_bytes, road_kinds) = road_bytes(motion, origin, &roads, &kinds)?;
        let mut sampled = json!({
            "interval": interval,
            "road_tolerance_mm": tolerance,
            "surface_paths": surface_paths,
            "track": compressed(&track_bytes(motion, origin, end_times, &roads, intervals, interval)?)?,
            "roads": compressed(&road_bytes)?,
        });
        // The support byte stays readable by deployed players while the catalog updates.
        if road_kinds
            .iter()
            .any(|&kind| kind > RoadKind::Support as u8)
        {
            sampled["road_kinds"] = json!(compressed(&road_kinds)?);
        }
        data["sampled"] = sampled;
        let output = if data_only {
            serde_json::to_string(data)?
        } else {
            playback_page(title, data)?
        };
        if output.len() < byte_limit {
            return Ok(output);
        }
    }
    let destination = if data_only {
        "website archive"
    } else {
        "inline visualization"
    };
    bail!("The selected playback exceeds the {destination} size limit. Select fewer layers.")
}
