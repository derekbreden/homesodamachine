//! The above-counter plate the faucet's base stands on and the gasket under it, each on the
//! base's own foot: the Sculpted's oval or the Industrial's disc.
use crate::shell::{PAST, ellipse, level, lower_bundle_opening};
use anyhow::Result;
use hsm_faucet_numbers::interface::{PILL_LENGTH_X, PILL_WIDTH_Y};
use hsm_faucet_numbers::shell::*;
use hsm_faucet_numbers::stack::*;
use hsm_kernel::*;

/// The Sculpted's oval foot from `z0` to `z1`, the outline the shell's foot stands on.
pub fn oval(z0: f64, z1: f64) -> Result<Solid> {
    let ring = ellipse(v3(0.0, FOOT_CENTER_Y, z0), FOOT_WIDTH / 2.0, FOOT_DEPTH / 2.0);
    Solid::extrude(&ring.region(), V3::Z, v3(0.0, 0.0, z1 - z0))
}

/// The shank hole, the flavor pill and the cable lane, through from `z0` to `z1`.
pub fn through(z0: f64, z1: f64) -> Result<Vec<Solid>> {
    let (bottom, h) = (z0 - PAST, z1 - z0 + 2.0 * PAST);
    let [cx, cy] = SHANK_HOLE_CENTER;
    let shank = Solid::cylinder(v3(cx, cy, bottom), V3::Z, SHANK_HOLE_RADIUS, h)?;
    let [px, py] = PILL_SLOT_CENTER;
    let pill = Loop::slot(v2(px, py), PILL_LENGTH_X, PILL_WIDTH_Y, 0.0);
    let pill = level(bottom).extrude(&Profile::new(pill), h)?;
    Ok(vec![shank, pill, lower_bundle_opening()?])
}

/// The plate the base stands on: `foot` from the plate's bottom to its top, a pedestal under
/// each mounting pod, chamfered round its top, bored for the pod's screw and counterbored from
/// below, and the holes through.
pub fn plate(foot: impl Fn(f64, f64) -> Result<Solid>) -> Result<Solid> {
    let [z0, z1] = PLATE_Z;
    let (h, chamfer) = (BASE_PEDESTAL_HEIGHT, BASE_PEDESTAL_CHAMFER);
    let mut stock = vec![foot(z0, z1)?];
    let mut cutters = through(z0, z1)?;
    for [x, y] in BASE_POD_CENTERS {
        // Standing from inside the foot, so its own foot meets no face of it.
        let mid = 0.5 * (z0 + z1);
        let pedestal = Solid::cylinder(v3(x, y, mid), V3::Z, BASE_PEDESTAL_DIA / 2.0, h - mid)?;
        stock.push(pedestal.chamfer(&pedestal.edges(">Z")?, chamfer)?);
        cutters.push(Solid::cylinder(v3(x, y, z0 - PAST), V3::Z, BASE_POD_SHANK_DIA / 2.0, h - z0 + 2.0 * PAST)?);
        let counterbore = BASE_POD_COUNTERBORE_DIA / 2.0;
        cutters.push(Solid::cylinder(v3(x, y, z0 - PAST), V3::Z, counterbore, BASE_SCREW_COUNTERBORE_DEPTH + PAST)?);
    }
    Solid::union_all(&stock)?.cut_all(&cutters)
}

/// The gasket under the plate: `foot` from the gasket's bottom to its top, with the same holes
/// through.
pub fn gasket(foot: impl Fn(f64, f64) -> Result<Solid>) -> Result<Solid> {
    let [z0, z1] = GASKET_Z;
    foot(z0, z1)?.cut_all(&through(z0, z1)?)
}
