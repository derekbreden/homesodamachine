//! Removable print stock carries each rail cap from its own open cavity.

use anyhow::{Context, Result};
use hsm_kernel::{Plane, Profile, Solid, v2, v3};
use serde::Deserialize;
use serde_json::Value;

#[derive(Deserialize)]
#[serde(tag = "shape", rename_all = "snake_case")]
enum Stock {
    RailStrips {
        center_x_mm: f64,
        span_y_mm: [f64; 2],
        contact_source_z_mm: f64,
        root_source_z_mm: f64,
    },
}

/// A separate printable solid and its slicer settings, in the enclosure source frame.
pub fn removable_stock(spec: &Value, gap: f64) -> Result<(Solid, Vec<(String, String)>)> {
    let Stock::RailStrips {
        center_x_mm,
        span_y_mm,
        contact_source_z_mm,
        root_source_z_mm,
    } = serde_json::from_value(spec.clone()).context("rear enclosure support stock")?;
    let solid = rail_supports(center_x_mm, span_y_mm, contact_source_z_mm, root_source_z_mm, gap)?;
    let settings = vec![
        ("wall_loops".into(), "2".into()),
        ("sparse_infill_density".into(), "100%".into()),
    ];
    Ok((solid, settings))
}

fn box_solid(lo: [f64; 3], hi: [f64; 3]) -> Solid {
    Solid::cuboid(v3(lo[0], lo[1], lo[2]), v3(hi[0], hi[1], hi[2]))
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
