//! The water-inlet jet drilling fixture's numbers, in millimetres: two printed jaws that hold the
//! jet cap's stainless rod upright under the drill press. The rod and the passage drilled down it
//! are the jet's, taken from the carbonator's numbers by name.
use hsm_carbonator_numbers::jet;

/// The rod the jaws grip: the jet cap's stock.
pub const STOCK_DIAMETER: f64 = jet::CAP_DIAMETER;
/// The drill the passage takes.
pub const DRILL_DIAMETER: f64 = jet::PASSAGE_DIAMETER;
/// What each jaw's groove clears the rod by, radially.
pub const RADIAL_SLIP: f64 = 0.15;
/// The groove half each jaw carries.
pub const GROOVE_RADIUS: f64 = STOCK_DIAMETER / 2. + RADIAL_SLIP;
/// The gap the jaws stand open at before the clamps close them.
pub const GAP: f64 = 1.;
/// The fixed jaw's base on the drill table: across, deep and thick.
pub const BASE: [f64; 3] = [120., 90., 8.];
/// Each jaw: across, deep, and how high it grips the rod.
pub const JAW: [f64; 3] = [64., 25., 30.];
/// The shortest rod blank the jaws are drilled in.
pub const MINIMUM_BLANK: f64 = 40.;
/// The handling blank and clamp stations used by the manual drilling setup.
pub const HANDLING_BLANK: f64 = 50.;
pub const JAW_CLAMP_X: f64 = 20.;
pub const BASE_CLAMP_X: f64 = 46.;
/// The tolerance the stock's diameter is checked over, either side.
pub const STOCK_TOLERANCE: f64 = 0.1;
