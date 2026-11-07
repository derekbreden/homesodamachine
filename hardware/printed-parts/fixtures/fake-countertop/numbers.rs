//! The fake countertop's numbers, in millimetres: the bench stand that stands in for a counter,
//! an inverted U as deep as the H2C's bed with its legs as far apart as the cavity under Derek's
//! counter, one faucet through its hole and the umbilical hanging under it. Print frame: X across
//! the legs, Y along the front edge, +Z up from the bed, the show face at Z = 0.

/// The H2C plate the left nozzle reaches, and the border the print project keeps inside it
/// (`faucet/refresh_print_project.py`, `plate_border`).
pub const LEFT_REACH_X: f64 = 325.;
pub const LEFT_REACH_Y: f64 = 320.;
pub const PLATE_BORDER: f64 = 5.;
/// The counter hole the faucet's shank is sized for: one and three-eighths inches.
pub const HOLE_DIAMETER: f64 = 1.375 * 25.4;
/// How far the umbilical hangs below the counter's top face, the radius it bends on under that,
/// and the room a hand needs below the bend.
pub const UMBILICAL_BELOW_COUNTER: f64 = 80. - 6.;
pub const UMBILICAL_BEND_RADIUS: f64 = 30.;
pub const HAND_ROOM: f64 = 60.;
/// One thickness throughout: the slab's and each leg's.
pub const THICKNESS: f64 = 30.;
/// The stand's height, slab included.
pub const HEIGHT: f64 = 220.;
/// Between the legs: the narrow under-counter cavity.
pub const CAVITY: f64 = 130.;
/// The rounds: the slab's four outer corners, the legs' roots and the feet.
pub const CORNER_RADIUS: f64 = 6.;
pub const ROOT_RADIUS: f64 = 6.;
pub const FOOT_RADIUS: f64 = 3.;

/// The slab across the legs: the cavity and a leg each side.
pub fn slab_x() -> f64 {
    CAVITY + 2. * THICKNESS
}

/// The slab along the front edge: the plate's reach inside its border.
pub fn slab_y() -> f64 {
    LEFT_REACH_Y - 2. * PLATE_BORDER
}
