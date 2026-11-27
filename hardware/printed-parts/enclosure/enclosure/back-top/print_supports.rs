//! Removable print stock for the enclosure rails, tube wing, and WAGO wells.

use anyhow::{Context, Result, ensure};
use hsm_kernel::{Plane, Profile, Solid, v2, v3};
use serde::Deserialize;
use serde_json::Value;

#[derive(Deserialize)]
#[serde(tag = "shape", rename_all = "snake_case")]
enum Stock {
    RailStrips {
        center_x_mm: f64,
        #[serde(default)]
        cap_span_x_mm: Option<[f64; 2]>,
        span_y_mm: [f64; 2],
        contact_source_z_mm: f64,
        root_source_z_mm: f64,
    },
    TubeWingStrips {
        centre_source_mm: [f64; 3],
        bore_radius_mm: f64,
        wing_thickness_mm: f64,
        upper_wing_lift_mm: f64,
        tip_degrees: f64,
        span_y_mm: [f64; 2],
    },
    PocketFloorTree {
        bounds_source_mm: [f64; 6],
        print_up_source: [i8; 3],
        mouth_direction_source: [i8; 3],
    },
}

pub const POCKET_INTERFACE_THICKNESS: f64 = 0.72;
pub const POCKET_RELEASE_GAP: f64 = 0.24;

/// A separate printable solid and its slicer settings, in the enclosure source frame.
pub fn removable_stock(spec: &Value, gap: f64) -> Result<(Solid, Vec<(String, String)>)> {
    let stock: Stock = serde_json::from_value(spec.clone()).context("enclosure support stock")?;
    let solid = match stock {
        Stock::PocketFloorTree { bounds_source_mm, print_up_source, mouth_direction_source } => {
            let tree = pocket_floor_tree(bounds_source_mm, print_up_source, mouth_direction_source)?;
            let settings = [
                ("wall_loops", "2"),
                ("sparse_infill_density", "15%"),
                ("top_shell_layers", "3"),
                ("top_shell_thickness", "0"),
                ("bottom_shell_layers", "2"),
                ("bottom_shell_thickness", "0"),
            ].into_iter().map(|(k, v)| (k.to_owned(), v.to_owned())).collect();
            return Ok((tree, settings));
        }
        Stock::RailStrips { center_x_mm, cap_span_x_mm, span_y_mm, contact_source_z_mm, root_source_z_mm } => {
            let cap_span = cap_span_x_mm.unwrap_or([center_x_mm - 2.15, center_x_mm + 2.15]);
            rail_supports(center_x_mm, cap_span, span_y_mm, contact_source_z_mm, root_source_z_mm, gap)?
        }
        Stock::TubeWingStrips { centre_source_mm, bore_radius_mm, wing_thickness_mm,
                                upper_wing_lift_mm, tip_degrees, span_y_mm } => {
            tube_wing_strips(centre_source_mm, bore_radius_mm, wing_thickness_mm,
                             upper_wing_lift_mm, tip_degrees, span_y_mm, gap)?
        }
    };
    let settings = vec![
        ("wall_loops".into(), "2".into()),
        ("sparse_infill_density".into(), "100%".into()),
    ];
    Ok((solid, settings))
}

/// One breakaway foot printed on the well floor. The sloping shoulder can print from
/// the stem and leaves the full-width cap free to slide out through the side mouth.
fn pocket_floor_tree(bounds: [f64; 6], up: [i8; 3], mouth: [i8; 3]) -> Result<Solid> {
    let unit_axis = |direction: [i8; 3]| direction.map(|k| i16::from(k).abs()).iter().sum::<i16>() == 1;
    ensure!(unit_axis(up) && unit_axis(mouth), "WAGO tree requires signed principal print and mouth axes");
    let w = up.iter().position(|&k| k != 0).unwrap();
    ensure!(mouth[w] == 0, "WAGO mouth must face sideways in print position");
    let (u, v) = ((w + 1) % 3, (w + 2) % 3);
    let size = |i: usize| bounds[2 * i + 1] - bounds[2 * i];
    let middle = |i: usize| (bounds[2 * i] + bounds[2 * i + 1]) / 2.0;
    let floor = bounds[2 * w + usize::from(up[w] < 0)];
    // The mouth has no wall. Extending this single edge 0.24 mm past the lip
    // catches the first outside perimeter, whose center is only 0.21 mm inside.
    let offset = |i: usize| 0.36 * f64::from(mouth[i]);
    let (du, dv) = (offset(u), offset(v));
    let (cap_u, cap_v) = (size(u) / 2.0 - 0.48 + du.abs(), size(v) / 2.0 - 0.48 + dv.abs());
    let cap_top = size(w) - POCKET_RELEASE_GAP;
    let cap_base = cap_top - POCKET_INTERFACE_THICKNESS;
    // Even the corners can grow at no more than 45 degrees from the nearest stem.
    let fan_start = cap_base - ((cap_u + du.abs()).hypot(cap_v + dv.abs()) - 1.35);
    ensure!(cap_u > 1.8 && cap_v > 1.8 && fan_start > 1.35, "WAGO tree does not fit pocket {bounds:?}");
    let octagon = |z: f64, a: f64, b: f64, cut: f64, dx: f64, dy: f64| {
        [(-a + cut,-b), (a - cut,-b), (a,-b + cut), (a,b - cut),
         (a - cut,b), (-a + cut,b), (-a,b - cut), (-a,-b + cut)].map(|(x,y)| {
            let mut p = [0.0; 3];
            p[u] = middle(u) + x + dx;
            p[v] = middle(v) + y + dy;
            p[w] = floor + f64::from(up[w]) * z;
            v3(p[0], p[1], p[2])
        })
    };
    let rings = [
        octagon(POCKET_RELEASE_GAP, 1.65, 1.65, 0.96, 0.0, 0.0),
        octagon(0.75, 1.65, 1.65, 0.96, 0.0, 0.0),
        octagon(1.35, 1.35, 1.35, 0.79, 0.0, 0.0),
        octagon(fan_start, 1.35, 1.35, 0.79, 0.0, 0.0),
        octagon(cap_base, cap_u, cap_v, 0.15, du, dv),
        octagon(cap_top, cap_u, cap_v, 0.15, du, dv),
    ];
    let sections = rings.windows(2).map(|neighbor| {
        let points: Vec<_> = neighbor[0].iter().chain(&neighbor[1]).copied().collect();
        Solid::hull(&points)
    }).collect::<Result<Vec<_>>>()?;
    Solid::union_all(&sections)?.simplified()
}

/// The cap follows the upper wing's nose and bore; slender feet break from the lower wing.
fn tube_wing_strips(
    [cx, _cy, cz]: [f64; 3], ri: f64, wing: f64, lift: f64,
    tip_degrees: f64, [y0, y1]: [f64; 2], gap: f64,
) -> Result<Solid> {
    let tip = tip_degrees.to_radians();
    let nose = wing / 2.0;
    let rm = ri + nose;
    let nose_y = rm * tip.cos();
    let nose_z = -rm * tip.sin();
    let inner_tip_x = cx + ri * tip.cos();
    let roof_z = |x: f64| -> f64 {
        let across = x - cx;
        let profile_z = if x <= inner_tip_x {
            nose_z + (nose * nose - (across - nose_y).powi(2)).max(0.0).sqrt()
        } else {
            -(ri * ri - across * across).max(0.0).sqrt()
        };
        cz - lift + profile_z + gap
    };
    let x_start = cx + nose_y - nose + 0.18;
    let x_end = cx + 1.2;
    let samples = ((x_end - x_start) / 0.15).ceil() as usize;
    let mut top: Vec<_> = (0..=samples).map(|i| {
        let x = x_start + (x_end - x_start) * i as f64 / samples as f64;
        v2(x, roof_z(x))
    }).collect();
    top.push(v2(inner_tip_x, roof_z(inner_tip_x)));
    top.sort_by(|a, b| a.x.total_cmp(&b.x));
    let z_stem_start = cz + ri - 1.3;
    let z_stem_end = cz + ri - 0.65;
    let z_root = cz + ri + 0.05;
    let mut outline = top.clone();
    outline.extend([
        v2(x_end, roof_z(x_end) + 0.72),
        v2(cx + 0.55, z_stem_start),
        v2(cx + 0.55, z_stem_end),
        v2(cx - 0.55, z_stem_end),
        v2(cx - 0.55, z_stem_start),
        v2(x_start, roof_z(x_start) + 0.72),
    ]);
    let margin = 0.15;
    let separation = 0.3;
    let count = 3;
    let width = (y1 - y0 - 2.0 * margin - separation * (count - 1) as f64) / count as f64;
    let mut parts = Vec::new();
    for i in 0..count {
        let a = y0 + margin + i as f64 * (width + separation);
        let b = a + width;
        let cap = Plane::XZ.at(v3(0.0, a, 0.0)).extrude(&Profile::polygon(&outline), a - b)?;
        let middle = (a + b) / 2.0;
        let neck = box_solid(
            [cx - 0.4, middle - 0.75, z_stem_end - 0.03],
            [cx + 0.4, middle + 0.75, z_root],
        );
        parts.push(Solid::union_all(&[cap, neck])?.simplified()?);
    }
    Ok(Solid::compose(&parts))
}

fn box_solid(lo: [f64; 3], hi: [f64; 3]) -> Solid {
    Solid::cuboid(v3(lo[0], lo[1], lo[2]), v3(hi[0], hi[1], hi[2]))
}

/// Narrow breakaway necks carry a dense cap directly from the open rail cavity floor.
fn rail_strip(x: f64, [x0, x1]: [f64; 2], y0: f64, y1: f64, contact: f64, floor: f64, gap: f64) -> Result<Solid> {
    let cap_top = contact + gap;
    let cap_bottom = cap_top + 0.72;
    let stem_top = cap_bottom + (x - 0.60 - x0).max(x1 - x - 0.60);
    let stem_bottom = floor - 2.17;
    let neck_top = floor - 0.65;
    let section = Profile::polygon(&[
        v2(x0, cap_top),
        v2(x1, cap_top),
        v2(x1, cap_bottom),
        v2(x + 0.60, stem_top),
        v2(x + 0.60, stem_bottom),
        v2(x - 0.60, stem_bottom),
        v2(x - 0.60, stem_top),
        v2(x0, cap_bottom),
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
    cap_span: [f64; 2],
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
            rail_strip(x, cap_span, a + 0.3, a + pitch - 0.3, contact, floor, gap)
        })
        .collect::<Result<_>>()?;
    Ok(Solid::compose(&parts))
}
