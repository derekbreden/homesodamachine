//! The above-counter plate the faucet's base stands on and the gasket under it, each on the
//! base's own foot: the Sculpted's oval or the Industrial's disc.
use crate::shell::{PAST, ellipse, level, lower_bundle_opening};
use crate::{pair, rows};
use anyhow::Result;
use hsm_kernel::part::Numbers;
use hsm_kernel::*;

/// The Sculpted's oval foot from `z0` to `z1`, the outline `build_foot_outline` draws.
pub fn oval(n: &Numbers, z0: f64, z1: f64) -> Result<Solid> {
    let ring = ellipse(v3(0.0, n.f("foot_center_y")?, z0), n.f("foot_width")? / 2.0, n.f("foot_depth")? / 2.0);
    Solid::extrude(&ring.region(), V3::Z, v3(0.0, 0.0, z1 - z0))
}

/// The shank hole, the flavor pill and the cable lane, through from `z0` to `z1`.
pub fn through(n: &Numbers, z0: f64, z1: f64) -> Result<Vec<Solid>> {
    let (bottom, h) = (z0 - PAST, z1 - z0 + 2.0 * PAST);
    let (cx, cy) = n.pair("shank_hole_center")?;
    let shank = Solid::cylinder(v3(cx, cy, bottom), V3::Z, n.f("shank_hole_radius")?, h)?;
    let (px, py) = n.pair("pill_slot_center")?;
    let pill = Loop::slot(v2(px, py), n.f("pill_length_x")?, n.f("pill_width_y")?, 0.0);
    let pill = level(bottom).extrude(&Profile::new(pill), h)?;
    Ok(vec![shank, pill, lower_bundle_opening(n)?])
}

/// The plate the base stands on: `foot` from the plate's bottom to its top, a pedestal under
/// each mounting pod, chamfered round its top, bored for the pod's screw and counterbored from
/// below, and the holes through.
pub fn plate(n: &Numbers, foot: impl Fn(f64, f64) -> Result<Solid>) -> Result<Solid> {
    let (z0, z1) = n.pair("plate_z")?;
    let (h, chamfer) = (n.f("base_pedestal_height")?, n.f("base_pedestal_chamfer")?);
    let mut stock = vec![foot(z0, z1)?];
    let mut cutters = through(n, z0, z1)?;
    for c in rows(n.get("base_pod_centers")?)? {
        let (x, y) = pair(c)?;
        // Standing from inside the foot, so its own foot meets no face of it.
        let mid = 0.5 * (z0 + z1);
        let pedestal = Solid::cylinder(v3(x, y, mid), V3::Z, n.f("base_pedestal_dia")? / 2.0, h - mid)?;
        stock.push(pedestal.chamfer(&pedestal.edges(">Z")?, chamfer)?);
        let shank = n.f("base_pod_shank_dia")? / 2.0;
        cutters.push(Solid::cylinder(v3(x, y, z0 - PAST), V3::Z, shank, h - z0 + 2.0 * PAST)?);
        let counterbore = n.f("base_pod_counterbore_dia")? / 2.0;
        cutters.push(Solid::cylinder(v3(x, y, z0 - PAST), V3::Z, counterbore, n.f("base_screw_counterbore_depth")? + PAST)?);
    }
    Solid::union_all(&stock)?.cut_all(&cutters)
}

/// The gasket under the plate: `foot` from the gasket's bottom to its top, with the same holes
/// through.
pub fn gasket(n: &Numbers, foot: impl Fn(f64, f64) -> Result<Solid>) -> Result<Solid> {
    let (z0, z1) = n.pair("gasket_z")?;
    foot(z0, z1)?.cut_all(&through(n, z0, z1)?)
}
