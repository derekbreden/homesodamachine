//! The ASA Aero float's numbers that other parts take by name, in millimetres.

/// The float's diameter.
pub const DIAMETER: f64 = 36.;
/// What the float clears the tube's inner wall by.
pub const WALL_CLEARANCE: f64 = 2.;
/// Where the float's guide rod stands: its axis, measured in from the tube's inner wall.
pub const ROD_AXIS_FROM_INNER_WALL: f64 = DIAMETER / 2. + WALL_CLEARANCE;
