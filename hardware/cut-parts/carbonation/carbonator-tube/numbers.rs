//! The carbonator tube's stock, in millimetres. The parts that close on the tube take these by
//! name.

/// The tube's outer radius.
pub const OUTER_RADIUS: f64 = 63.5;
/// The tube's length, which is the carbonator's height.
pub const LENGTH: f64 = 152.4;
/// The tube's outer diameter.
pub const OD: f64 = 2. * OUTER_RADIUS;
/// The tube's wall.
pub const WALL: f64 = 0.065 * 25.4;
/// The tube's bore.
pub const ID: f64 = OD - 2. * WALL;
