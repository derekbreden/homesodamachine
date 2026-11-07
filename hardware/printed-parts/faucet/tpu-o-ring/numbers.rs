//! The TPU thimble's numbers, in millimetres. It seals the 3/8" soda tube into the harvested
//! Westbrass's top water port: a cap whose Z = 0 face sits on the port's floor, with the tube
//! bottomed on it, and an open sleeve over the tube.

/// The sleeve's bore, which grips the tube.
pub const INNER_DIAMETER: f64 = 9.2;
/// The sleeve's outside, which the port squeezes.
pub const OUTER_DIAMETER: f64 = 10.44;
/// The hole through the cap.
pub const CAP_HOLE_DIAMETER: f64 = 6.50;
/// The cap the tube bottoms on.
pub const CAP_THICKNESS: f64 = 2.1;
/// The sleeve above the cap.
pub const CYLINDER_LENGTH: f64 = 13.5;
pub const TOTAL_HEIGHT: f64 = CAP_THICKNESS + CYLINDER_LENGTH;
/// The sleeve's wall.
pub const WALL_THICKNESS: f64 = (OUTER_DIAMETER - INNER_DIAMETER) / 2.0;
/// The soda tube it seals.
pub const LLDPE_OD: f64 = 9.525;
pub const LLDPE_ID: f64 = 6.35;
/// The Westbrass's top port, and how deep it is at least.
pub const WESTBRASS_PORT_DIAMETER: f64 = 10.0;
pub const PORT_DEPTH_MIN: f64 = 20.0;
/// The squeeze the port puts on the sleeve, and the sleeve's grip on the tube, per side.
pub const WESTBRASS_SQUEEZE: f64 = (OUTER_DIAMETER - WESTBRASS_PORT_DIAMETER) / 2.0;
pub const LLDPE_INTERFERENCE: f64 = (LLDPE_OD - INNER_DIAMETER) / 2.0;
