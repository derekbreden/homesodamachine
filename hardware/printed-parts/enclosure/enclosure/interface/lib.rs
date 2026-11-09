//! The enclosure's numbers a part that mates with the shell takes without building the
//! enclosure: the wall and datums it meets, the pump and manifold stations it stands at, the
//! screws and inserts it shares, the fits they are cut to, the swept exterior's section, and the
//! anchor cap that closes the tube anchors. The enclosure's own numbers build on these.
pub mod anchor_cap;
pub mod fits;
pub mod input;
pub mod swept;

use fits::{running, slip, supported};

/// The printed wall section.
pub const WALL: f64 = 3.0;
/// The rear wall's interior datum, and what a part behind the rear seam keeps clear of it.
pub const REAR_PLANE_Y: f64 = 468.3;
pub const REAR_SEAM_CLEAR: f64 = 3.0;
/// The air the enclosure's condenser fin keeps off the block.
pub const COND_MOUNT_CLEAR: f64 = 1.0;
/// How deep the upper Y stacks reach into the side band, which the funnel pocket shares.
pub const Y_STACK_HIGH_DEPTH: f64 = 13.0;
/// The M3 insert's bore, and the long insert's length everywhere a station can take it.
pub const HEATSET_DIA: f64 = 4.0;
pub const HEATSET_LONG_LEN: f64 = 5.7;

/// Faces that slide along the seams take the running allowance.
pub fn slide_slip() -> f64 {
    running()
}

/// The funnel collar's running air in the roof.
pub fn funnel_collar_air() -> f64 {
    running()
}

/// The CO2 axis's drop: one supported face's allowance.
pub fn co2_axis_drop() -> f64 {
    supported()
}

/// An M3 screw's clearance bore, and its head's counterbore.
pub fn screw_clear_dia() -> f64 {
    3.0 + 2.0 * slip()
}

pub fn head_cbore_dia() -> f64 {
    5.5 + 2.0 * slip()
}

/// The signed pump-to-deck offset. The manifold subtracts it from the pump-outlet station and
/// adds it to the placement span, so the fixed tee deck keeps its own plane.
pub const PUMP_STATION_LEAD: f64 = -0.074;
/// The pumps' vertical service datum: how far the pump stations stand below their declared Z.
pub const PUMP_STATION_DROP: f64 = 3.0;

/// How far the seated pump's flange stands below the holder's station datum: the running fit,
/// and the upper well's Boolean overlap.
pub fn pump_seated_drop() -> f64 {
    running() + 0.001
}

/// The manifold's own rise, carried by its tees, valve seats and stationary tube endpoints.
pub const MANIFOLD_RISE: f64 = 2.0;
/// How far the two source limbs, with their tees and aft valves, stand below the outer limbs,
/// so the funnel's bowl ramp clears the valves under its sloping floor.
pub const INNER_LIMB_DROP: f64 = 9.5;
