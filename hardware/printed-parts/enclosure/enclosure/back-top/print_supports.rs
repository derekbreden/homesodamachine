//! Removable print stock supports the exposed nameplate receiver and roots each rail cap in its own open cavity.

use anyhow::{Context, Result, ensure};
use hsm_kernel::{Face, Plane, Profile, Solid, Surface, file_src, v2, v3};
use serde::Deserialize;
use serde_json::Value;

#[derive(Deserialize)]
#[serde(tag = "shape", rename_all = "snake_case")]
enum Stock {
    NameplatePanel(NameplateContact),
    RailStrips {
        center_x_mm: f64,
        span_y_mm: [f64; 2],
        contact_source_z_mm: f64,
        root_source_z_mm: f64,
    },
}

#[derive(Deserialize)]
struct NameplateContact {
    center_x_mm: f64,
    center_z_mm: f64,
    face_y_mm: f64,
    frame_top_mm: f64,
    frame_half_width_mm: f64,
    frame_corner_mm: f64,
    field_proud_mm: f64,
    mouth_floor_mm: f64,
    mouth_half_width_mm: f64,
    mouth_corner_mm: f64,
    bed_source_z_mm: f64,
}

/// A separate printable solid and its slicer settings, in the enclosure source frame.
pub fn removable_stock(spec: &Value, gap: f64) -> Result<(Solid, Vec<(String, String)>)> {
    let mut settings = vec![("wall_loops".into(), "2".into())];
    let solid =
        match serde_json::from_value(spec.clone()).context("rear enclosure support stock")? {
            Stock::NameplatePanel(contact) => {
                settings.extend([
                    ("sparse_infill_density".into(), "15%".into()),
                    ("top_shell_layers".into(), "3".into()),
                    ("top_shell_thickness".into(), "0.72".into()),
                ]);
                nameplate_panel(contact, gap)?
            }
            Stock::RailStrips {
                center_x_mm,
                span_y_mm,
                contact_source_z_mm,
                root_source_z_mm,
            } => {
                settings.push(("sparse_infill_density".into(), "100%".into()));
                rail_supports(
                    center_x_mm,
                    span_y_mm,
                    contact_source_z_mm,
                    root_source_z_mm,
                    gap,
                )?
            }
        };
    Ok((solid, settings))
}

fn box_solid(lo: [f64; 3], hi: [f64; 3]) -> Solid {
    Solid::cuboid(v3(lo[0], lo[1], lo[2]), v3(hi[0], hi[1], hi[2]))
}

fn subdivisions(low: f64, high: f64, step: f64, mut breaks: Vec<f64>) -> Vec<f64> {
    let cells = ((high - low) / step).ceil() as usize;
    breaks.extend((0..=cells).map(|i| low + (high - low) * i as f64 / cells as f64));
    breaks.sort_by(f64::total_cmp);
    breaks.dedup_by(|a, b| (*a - *b).abs() < 1e-7);
    breaks
}

/// A closed solid between the receiver's sampled contact surface and its buttress.
fn contact_solid(
    xs: &[f64],
    ys: &[f64],
    contact: impl Fn(f64, f64) -> f64,
    ramp: impl Fn(f64) -> f64,
    gap: f64,
) -> Result<Solid> {
    let nx = xs.len() as u32;
    let ny = ys.len() as u32;
    let level = nx * ny;
    let mut vertices = Vec::new();
    for &y in ys {
        for &x in xs {
            let z = contact(x, y) + gap;
            ensure!(
                z < ramp(y),
                "support ramp does not reach the contact surface"
            );
            vertices.push(v3(x, y, z));
        }
    }
    for &y in ys {
        for &x in xs {
            vertices.push(v3(x, y, ramp(y)));
        }
    }
    let mut triangles = Vec::new();
    for j in 0..ny - 1 {
        for i in 0..nx - 1 {
            let a = j * nx + i;
            let [b, c, d] = [a + 1, a + nx + 1, a + nx];
            triangles.extend([
                [a, c, b],
                [a, d, c],
                [a + level, b + level, c + level],
                [a + level, c + level, d + level],
            ]);
        }
    }
    let rim: Vec<u32> = (0..nx)
        .chain((1..ny).map(|row| row * nx + nx - 1))
        .chain((0..nx - 1).rev().map(|column| (ny - 1) * nx + column))
        .chain((1..ny - 1).rev().map(|row| row * nx))
        .collect();
    for (&a, &b) in rim.iter().zip(rim.iter().cycle().skip(1)) {
        triangles.extend([[a, b, b + level], [a, b + level, a + level]]);
    }
    let face = Face::new(
        Surface::Free {
            kind: "support contact",
        },
        "contact_solid",
        file_src(file!()),
    );
    Solid::from_mesh(&vertices, &triangles, &vec![0; triangles.len()], &[face])
}

/// An exterior panel carries both contact bands and pulls straight aft away from the rear wall.
fn nameplate_panel(contact: NameplateContact, gap: f64) -> Result<Solid> {
    let NameplateContact {
        center_x_mm: center,
        center_z_mm: center_z,
        face_y_mm: face,
        frame_top_mm: frame_top,
        frame_half_width_mm: frame_half_width,
        frame_corner_mm: frame_corner,
        field_proud_mm: field_proud,
        mouth_floor_mm: mouth_floor,
        mouth_half_width_mm: mouth_half_width,
        mouth_corner_mm: mouth_corner,
        bed_source_z_mm: bed,
    } = contact;
    let half = mouth_half_width - 1.7;
    let [x0, x1] = [center - half, center + half];
    let [frame_round, mouth_round] = [
        frame_half_width - frame_corner,
        mouth_half_width - mouth_corner,
    ];
    let breaks = [-frame_round, -mouth_round, mouth_round, frame_round];
    let xs = subdivisions(
        x0,
        x1,
        0.5,
        breaks.into_iter().map(|x| x + center).collect(),
    );
    let [upper_y, lower_y] = [face - 1.75, face - 3.1];
    let stem_y = face + 1.70;
    let upper = contact_solid(
        &xs,
        &subdivisions(upper_y, stem_y + 0.08, 0.21, vec![face]),
        |x, y| {
            let d = ((x - center).abs() - frame_round).max(0.0);
            let round = frame_top - frame_corner + (frame_corner.powi(2) - d.powi(2)).sqrt();
            let crown = frame_top - (y.min(face) - (face - field_proud));
            round.min(crown)
        },
        |y| center_z + 50.9 + (y - upper_y),
        gap,
    )?;
    let lower = contact_solid(
        &xs,
        &subdivisions(lower_y, stem_y + 0.08, 0.35, Vec::new()),
        |x, _| {
            let d = ((x - center).abs() - mouth_round).max(0.0);
            mouth_floor + mouth_corner - (mouth_corner.powi(2) - d.powi(2)).sqrt()
        },
        |y| center_z - 39.75 + (y - lower_y),
        gap,
    )?;
    let base = mouth_floor + gap;
    let mut pieces = vec![
        upper,
        lower,
        box_solid([x0, stem_y, base], [x1, stem_y + 2.0, bed]),
        box_solid([x0, stem_y - 0.2, bed - 2.4], [x1, stem_y + 3.2, bed]),
    ];
    let mut x = x0 + 4.0;
    while x < x1 - 1.0 {
        pieces.push(box_solid(
            [x - 0.75, stem_y + 1.95, base],
            [x + 0.75, stem_y + 2.8, bed],
        ));
        x += 11.5;
    }
    Solid::union_all(&pieces)?.simplified()
}

/// Narrow breakaway necks carry a dense cap directly from the open rail cavity floor.
fn rail_strip(x: f64, y0: f64, y1: f64, contact: f64, floor: f64, gap: f64) -> Result<Solid> {
    let cap_top = contact + gap;
    let cap_bottom = cap_top + 0.72;
    let stem_top = cap_bottom + 1.55;
    let stem_bottom = floor - 2.17;
    let neck_top = floor - 0.65;
    let section = Profile::polygon(&[
        v2(x - 2.15, cap_top),
        v2(x + 2.15, cap_top),
        v2(x + 2.15, cap_bottom),
        v2(x + 0.60, stem_top),
        v2(x + 0.60, stem_bottom),
        v2(x - 0.60, stem_bottom),
        v2(x - 0.60, stem_top),
        v2(x - 2.15, cap_bottom),
    ]);
    let cap = Plane::XZ.at(v3(0.0, y0, 0.0)).extrude(&section, y0 - y1)?;
    let mut pieces = vec![cap];
    let roots = ((y1 - y0) / 4.8).ceil() as usize;
    for i in 0..roots {
        let y = y0 + (y1 - y0) * (i as f64 + 0.5) / roots as f64;
        pieces.push(box_solid(
            [x - 0.60, y - 0.82, stem_bottom - 0.04],
            [x + 0.60, y + 0.82, neck_top + 0.04],
        ));
        pieces.push(box_solid(
            [x - 0.47, y - 0.49, neck_top],
            [x + 0.47, y + 0.49, floor + 0.02],
        ));
    }
    Solid::union_all(&pieces)?.simplified()
}

fn rail_supports(
    x: f64,
    [low, high]: [f64; 2],
    contact: f64,
    floor: f64,
    gap: f64,
) -> Result<Solid> {
    let strips = ((high - low) / 16.0).ceil() as usize;
    let pitch = (high - low) / strips as f64;
    let parts: Vec<_> = (0..strips)
        .map(|i| {
            let a = low + pitch * i as f64;
            rail_strip(x, a + 0.3, a + pitch - 0.3, contact, floor, gap)
        })
        .collect::<Result<_>>()?;
    Ok(Solid::compose(&parts))
}
