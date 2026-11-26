//! Locate the rigid outlet shoulder against the existing inlet-side fixed stop.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Affine, Solid, V3, v3};
use serde_json::{Value, json};

const LIP_ADVANCE: f64 = 0.24;
const POCKET_ADVANCE: f64 = 0.12;

/// Carry an existing solid end face forward, including its fitted bore and its full backing.
fn advance_end(stock: &Solid, corner: V3, opposite: V3, advance: f64) -> Result<Solid> {
    let scale = (opposite.y - corner.y + advance) / (opposite.y - corner.y);
    stock
        .intersect(&Solid::cuboid(corner, opposite))?
        .mapped(&Affine {
            m: [
                [1., 0., 0., 0.],
                [0., scale, 0., corner.y * (1. - scale)],
                [0., 0., 1., 0.],
            ],
        })
}

pub(super) fn stops(
    cover: Solid,
    receiver: Solid,
    axis: f64,
    axis_z: f64,
    mouth: f64,
    outer: f64,
) -> Result<(Solid, Solid, Value)> {
    let bounds = cover.bounds();
    let lip = cover
        .verts()
        .iter()
        .filter(|p| (p.z - axis_z).abs() < 1e-5 && (p.x - axis).abs() < 10.0)
        .map(|p| p.y)
        .reduce(f64::max)
        .context("end face of the raised short-outlet neck lip")?;
    ensure!(
        lip > mouth && lip < mouth + 6.,
        "locate the rigid outlet shoulder near the cover nose"
    );
    let lip_half = cover
        .verts()
        .iter()
        .filter(|p| (p.y - bounds.min.y).abs() < 1e-5 && (p.z - axis_z).abs() < 1e-5)
        .map(|p| p.x - axis)
        .reduce(f64::max)
        .context("outer edge of the supported neck lip")?;
    let lip_stock = advance_end(
        &cover,
        v3(axis - lip_half, lip - 0.03, bounds.min.z + 0.6),
        v3(axis + lip_half, lip, axis_z + 0.01),
        LIP_ADVANCE,
    )?;
    let new_cover = cover.union(&lip_stock)?;
    // Only the two outboard spring lanes transmit the cap's forward load to the fixed receiver.
    let wall = advance_end(
        &receiver,
        v3(axis + outer - 4.0, mouth - 0.05, axis_z + 3.5),
        v3(axis + outer + 0.35, mouth, receiver.bounds().max.z),
        POCKET_ADVANCE,
    )?;
    let new_receiver = receiver
        .union(&wall)?
        .union(&wall.mirror(v3(axis, 0., 0.), V3::X))?;
    let record = json!({"previous_rigid_outlet_lip_y_mm":lip,"new_rigid_outlet_lip_y_mm":lip+LIP_ADVANCE,
        "previous_wing_forward_stop_y_mm":mouth,"new_wing_forward_stop_y_mm":mouth+POCKET_ADVANCE,
        "rigid_outlet_lip_advance_mm":LIP_ADVANCE,"wing_forward_stop_advance_mm":POCKET_ADVANCE,
        "total_nominal_grip_reduction_mm":LIP_ADVANCE+POCKET_ADVANCE,
        "lip_added_mm3":new_cover.volume()-cover.volume(),"wing_end_walls_added_mm3":new_receiver.volume()-receiver.volume()});
    Ok((new_cover, new_receiver, record))
}
