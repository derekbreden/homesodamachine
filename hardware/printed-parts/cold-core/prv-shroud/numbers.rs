//! The PRV shroud's numbers, in millimetres. The cup's axis is Z, its open end at Z = 0 and its
//! closed cap above. The cold core's assembly and its internal routes take the cup's outside
//! diameter, its length and the vent's station from here.
use hsm_cold_core_catalog as catalog;

/// The TAISHER elbow's smooth cylinder the cup seats on, measured at the install.
pub const ELBOW_SEAT_DIAMETER: f64 = 18.8;
/// The cup's wall round the valve.
pub const WALL_THICKNESS: f64 = 2.;
/// The closed end.
pub const CAP_THICKNESS: f64 = 2.;
/// From the elbow seat's bottom to the tip of the valve's pull-ring.
pub const CAVITY_LENGTH: f64 = 44.;
/// The overall length, cap included.
pub const TOTAL_LENGTH: f64 = CAVITY_LENGTH + CAP_THICKNESS;
/// The vent line the cup's radial socket holds.
pub const VENT_TUBE_OD: f64 = 6.5;
/// Where the radial vent stands along the barrel from the open end: the mouth-to-lane gap that
/// lands the vent on the foam shell's west lane.
pub const VENT_STATION_Z: f64 = 37.88;
/// How far each cutter overruns the face it opens.
pub const OVERCUT: f64 = 0.1;

/// The bore: the seat on the slip fit each side.
pub fn inner_diameter() -> f64 {
    ELBOW_SEAT_DIAMETER + 2. * catalog::fits().slip
}

/// The outside of the barrel.
pub fn outer_diameter() -> f64 {
    inner_diameter() + 2. * WALL_THICKNESS
}

/// The vent socket: the tube on the slip fit each side, which holds the installed line.
pub fn vent_hole_diameter() -> f64 {
    VENT_TUBE_OD + 2. * catalog::fits().slip
}

/// The cup prints in black PETG.
pub fn colour() -> catalog::Colour {
    catalog::petg_black()
}
