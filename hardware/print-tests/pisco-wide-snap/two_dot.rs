//! Move the supported Pisco body cradle toward the regulator, and mark the pair on its exterior.
use super::{BEARING_LENGTH, number};
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Affine, Solid, V3, reads, v3};
use serde_json::{Value, json};

const CLOSING_MOVE: f64 = 0.20;
const LEAD_LENGTH: f64 = 0.60;
const LAYOUT: &str = "hardware/manifold-layout/above-core.json";

pub(super) fn supported_saddle(cover: &Solid, axis: f64, axis_z: f64, base: &Value) -> Result<(Solid, Value)> {
    let b = cover.bounds();
    let half = cover
        .verts()
        .iter()
        .filter(|p| (p.y - b.min.y).abs() < 1e-5 && (p.z - axis_z).abs() < 1e-5)
        .map(|p| p.x - axis)
        .reduce(f64::max)
        .context("outside of the rigid outlet lip and saddle")?;
    let candidates = reads::json(base["housing_scan"].as_str().context("Pisco scan")?)?;
    let body_end = candidates["pisco_rvfup_quarter"]["fitted_exterior"]["component_ranges_mm"]["body"][1]
        .as_f64()
        .context("end of the molded housing")?;
    let mouth = reads::json(LAYOUT)?["rear_plumbing"]["gas_frame"]["translation_mm"][1]
        .as_f64()
        .context("installed inlet")?;
    let junction = mouth - body_end;
    let full = junction + LEAD_LENGTH;
    let bearing_y = number(base, "section_y_mm")?;
    ensure!(
        full < bearing_y && full > bearing_y - BEARING_LENGTH / 2.,
        "the lead ends on the bearing before its widest contact"
    );
    let cradle = |y0, y1| {
        Solid::cuboid(
            v3(axis - half, y0, b.min.z + 0.65),
            v3(axis + half, y1, axis_z + 0.01),
        )
    };
    let slope = CLOSING_MOVE / LEAD_LENGTH;
    let ramp = cover.intersect(&cradle(junction, full))?.mapped(&Affine {
        m: [
            [1., 0., 0., 0.],
            [0., 1., 0., 0.],
            [0., slope, 1., -slope * junction],
        ],
    })?;
    let lifted = cover
        .intersect(&cradle(full, b.max.y + 0.01))?
        .translate(V3::Z * CLOSING_MOVE);
    let raised = cover.union(&ramp)?.union(&lifted)?;
    let record = json!({"working_surface_move_machine_xyz_mm":[0.,0.,CLOSING_MOVE],
      "body_to_outlet_fitting_junction_y_mm":junction,"axial_lead_length_mm":LEAD_LENGTH,
      "full_height_y_mm":[full,b.max.y],"backed_cradle_width_mm":2.*half,"added_stock_mm3":raised.volume()-cover.volume()});
    Ok((raised, record))
}

/// Match the shallow exterior marks on the selected coupon.
pub(super) fn dots(stock: &Solid, marks: &Value, which: &str, offsets: &[f64], outside: V3) -> Result<Solid> {
    let center: [f64; 3] = serde_json::from_value(marks[which].clone())?;
    let depth = number(marks, "depth_mm")?;
    let pitch = number(marks, "pitch_mm")?;
    let radius = number(marks, "opening_diameter_mm")? / 2.;
    let height = depth + 0.15;
    let cutters: Vec<Solid> = offsets
        .iter()
        .map(|n| {
            Solid::cone(
                V3::from(center) + V3::Y * (n * pitch) - outside * depth,
                outside,
                0.,
                radius * height / depth,
                height,
            )
        })
        .collect::<Result<_>>()?;
    stock.cut_all(&cutters)
}
