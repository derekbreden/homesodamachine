//! On-demand playback turns consecutive sliced layers into an accelerating H2C motion study.
use super::super::{layer_range, slice_text};
use super::{base64, render};
use anyhow::{Context, Result, ensure};
use clap::Args;
use hsm_print_prep::motion::{Motion, Move, distance, read};
use serde_json::json;
use sha2::{Digest, Sha256};
use std::{fs, path::PathBuf};

#[path = "gcode_playback_inline.rs"]
mod inline;

const TEMPLATE: &str = include_str!("../../../gcode/playback-page.html");
const THEME: &str = include_str!("../../../viz/inline-mobile/assets/theme.js");
const COORDINATE_SCALE: f64 = 100.;

#[derive(Args)]
pub struct Options {
    slice: PathBuf,
    /// Consecutive layers in Bambu Studio's numbering, or all.
    #[arg(long)]
    layers: String,
    /// Sample motion and simplify beads to fit the inline visualization limit.
    #[arg(long)]
    inline: bool,
    /// Write the sampled replay data for a shared player.
    #[arg(long, requires = "inline")]
    data: bool,
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

fn coordinates(point: [f64; 3], origin: [f64; 3]) -> Result<[i16; 3]> {
    let mut result = [0; 3];
    for axis in 0..3 {
        let coordinate = (point[axis] - origin[axis]) * COORDINATE_SCALE;
        ensure!(
            coordinate.is_finite() && coordinate.abs() <= i16::MAX as f64,
            "selected coordinates exceed the playback range"
        );
        result[axis] = coordinate.round() as i16;
    }
    Ok(result)
}

fn bead_dimensions(movement: &Move) -> [u8; 2] {
    [movement.width, movement.height].map(|value| {
        (value * COORDINATE_SCALE)
            .clamp(1., f64::from(u8::MAX))
            .round() as u8
    })
}

fn detailed_data(
    motion: &Motion,
    origin: [f64; 3],
    end_times: &[f64],
) -> Result<serde_json::Value> {
    let mut positions = Vec::new();
    for p in std::iter::once(motion.moves[0].start).chain(motion.moves.iter().map(|m| m.end)) {
        for coordinate in coordinates(p, origin)? {
            positions.extend_from_slice(&coordinate.to_le_bytes());
        }
    }
    let mut kinematics = Vec::new();
    let mut layers = Vec::new();
    let mut flags = Vec::new();
    let mut dimensions = Vec::new();
    let mut features = Vec::new();
    for (m, end_time) in motion.moves.iter().zip(end_times) {
        for value in [*end_time, m.length, m.entry, m.peak, m.exit, m.acceleration] {
            ensure!(value.is_finite(), "non-finite playback timing");
            kinematics.extend_from_slice(&(value as f32).to_le_bytes());
        }
        layers.extend_from_slice(&u16::try_from(m.layer)?.to_le_bytes());
        flags.push(u8::from(m.extrusion));
        dimensions.extend_from_slice(&bead_dimensions(m));
        features.push(u8::try_from(m.feature)?);
    }
    Ok(
        json!({ "positions":base64(&positions), "kinematics":base64(&kinematics), "layers":base64(&layers),
        "flags":base64(&flags), "dimensions":base64(&dimensions), "feature_ids":base64(&features) }),
    )
}

pub fn run(args: Options) -> Result<i32> {
    ensure!(
        args.speed.is_finite() && args.speed > 0.,
        "playback speed must be positive"
    );
    let selected = if args.layers == "all" {
        1..=usize::MAX
    } else {
        layer_range(&args.layers)?
    };
    let text = slice_text(&args.slice, args.plate)?;
    let gcode_sha256 = format!("{:x}", Sha256::digest(text.as_bytes()));
    let motion = read(&text, *selected.start(), *selected.end())?;
    let origin = [motion.bed[0] / 2., motion.bed[1] / 2., 0.];
    let end_times: Vec<_> = motion
        .moves
        .iter()
        .scan(0., |time, movement| {
            *time += movement.seconds;
            Some(*time)
        })
        .collect();
    let seconds = *end_times.last().unwrap();
    ensure!(
        seconds.is_finite() && seconds > 0.,
        "invalid playback duration"
    );
    let mut data = json!({ "version":1, "features":motion.features,
        "bed":motion.bed, "bed_mesh":args.bed_model.as_ref().map(|p|bed_triangles(p,origin)).transpose()?,
        "origin":origin, "speed":args.speed, "seconds":seconds, "gcode_sha256":gcode_sha256,
        "source":args.slice.file_name().unwrap_or_default().to_string_lossy(),
        "selected_layers":[motion.moves[0].layer,motion.moves.last().unwrap().layer] });
    let output = if args.inline {
        inline::sampled_output(
            &args.title,
            &mut data,
            &motion,
            origin,
            &end_times,
            args.data,
        )?
    } else {
        data["detail"] = detailed_data(&motion, origin, &end_times)?;
        playback_page(&args.title, &data)?
    };
    fs::write(&args.out, &output).with_context(|| format!("writing {}", args.out.display()))?;
    println!(
        "{}  {:.1} MB · {} moves · {:.1} estimated motion seconds",
        args.out.display(),
        output.len() as f64 / 1e6,
        motion.moves.len(),
        seconds
    );
    Ok(0)
}

fn playback_page(title: &str, data: &serde_json::Value) -> Result<String> {
    Ok(render(TEMPLATE, title, "", data)?.replace("/*THEME*/", THEME))
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
