//! The machined end cap's numbers, in inches as its drawing gives them. The cap takes the tube's
//! bore and the float rod's place from those parts, by name. The carbonator's plates, the cap's
//! laser file and its drawing take these.
use hsm_aero_float_numbers as float;
use hsm_carbonator_tube_numbers as tube;

/// Millimetres in an inch.
pub const INCH: f64 = 25.4;
/// The tube's bore, which the disc closes.
pub const TUBE_ID_IN: f64 = tube::ID / INCH;
/// What the disc's diameter clears the bore by.
pub const BORE_CLEARANCE_IN: f64 = 0.010;
/// The disc's diameter.
pub const DIAMETER_IN: f64 = TUBE_ID_IN - BORE_CLEARANCE_IN;
/// The disc's thickness.
pub const THICKNESS_IN: f64 = 0.25;
/// The NPT tap drill, through the disc.
pub const HOLE_DIAMETER_IN: f64 = 0.438;
/// The two tapped holes' spacing, centre to centre.
pub const HOLE_SPACING_IN: f64 = 1.5;
/// The rod register's drill.
pub const REGISTER_DRILL_IN: f64 = 0.140625;
/// How deep the register goes into the inside face.
pub const REGISTER_DEPTH_IN: f64 = 0.1;
/// The register's distance from the cap's centre: under the float rod's axis.
pub const REGISTER_RADIUS_IN: f64 = TUBE_ID_IN / 2. - float::ROD_AXIS_FROM_INNER_WALL / INCH;
