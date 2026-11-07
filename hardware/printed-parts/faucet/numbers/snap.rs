//! The display cover's snap onto the neck: its preloaded wings carry broad lips round the rigid
//! neck, bearing against the groove roots, their bottoms seated on the groove floors and their tops
//! caught under the shoulders. Insertion force, retention and PET-GF durability are print trials.

/// How far a lip reaches into its groove.
pub const ENGAGEMENT: f64 = 1.2;
/// What the groove's root clears the lip by.
pub const RADIAL_SLIP: f64 = 0.0;
/// How far each wing is preloaded inward.
pub const X_PRELOAD: f64 = 1.25;
/// What the groove's roof clears the lip by.
pub const BEARING_SLIP: f64 = 0.48;
/// What the groove clears the lip by at each end.
pub const END_SLIP: f64 = 0.30;
/// How far the lips stop short of the skirt's ends.
pub const END_MARGIN: f64 = 3.0;
/// The lips' height.
pub const LIP_HEIGHT: f64 = 3.0;
/// The relief on each lip's inner edges.
pub const LIP_INNER_EDGE_RELIEF: f64 = 0.25;
