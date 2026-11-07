//! The stack the faucet's base stands on above the counter, in millimetres: the printed plate on
//! the TPU gasket, each the base's foot with the shank hole, the flavor pill and the cable lane
//! through it. Z = 0 is the plate's top, where the base stands.

use crate::P2;
use crate::interface::{ABOVE_COUNTER_GASKET_THICKNESS, ABOVE_COUNTER_PLATE_THICKNESS, SHANK_HOLE_DIAMETER};
use crate::paths::{LOWER_BUNDLE_X, LOWER_Y};

/// The plate, bottom to top.
pub const PLATE_Z: P2 = [-ABOVE_COUNTER_PLATE_THICKNESS, 0.0];
/// The gasket under it, bottom to top.
pub const GASKET_Z: P2 = [-ABOVE_COUNTER_PLATE_THICKNESS - ABOVE_COUNTER_GASKET_THICKNESS, -ABOVE_COUNTER_PLATE_THICKNESS];
/// The Westbrass shank's hole through both.
pub const SHANK_HOLE_CENTER: P2 = [0.0, 0.0];
pub const SHANK_HOLE_RADIUS: f64 = SHANK_HOLE_DIAMETER / 2.0;
/// The flavor pill's centre, over the flavor pair.
pub const PILL_SLOT_CENTER: P2 = [LOWER_BUNDLE_X, LOWER_Y];
