//! What the faucet's stack shares at its interfaces, in millimetres: the tubes through the mounting
//! stack, the flavor pill they pass in, the countertop stack's layers, and the display the tip
//! carries.

use crate::paths::{FLAVOR_OD, LOWER_BUNDLE_X, LOWER_DRAIN_Y, LOWER_FLAVOR_X, LOWER_Y};

/// What a flavor or drain tube's hole clears it by.
pub const TUBE_HOLE_CLEARANCE: f64 = 0.9;
/// The flavor tubes' hole.
pub const FLAVOR_TUBE_HOLE_DIA: f64 = FLAVOR_OD + TUBE_HOLE_CLEARANCE;
/// The flavor tubes' offset in X from the bundle's centre.
pub const FLAVOR_TUBE_X_OFFSET: f64 = LOWER_FLAVOR_X;
/// The pill the tubes, drain and cable pass the mounting stack in: its length across X.
pub const PILL_LENGTH_X: f64 = 18.15;
/// Its width in Y.
pub const PILL_WIDTH_Y: f64 = 7.25;
/// The pill's ends in X.
pub const BUNDLE_SLOT_LEFT_X: f64 = LOWER_BUNDLE_X - PILL_LENGTH_X / 2.0;
pub const BUNDLE_SLOT_RIGHT_X: f64 = LOWER_BUNDLE_X + PILL_LENGTH_X / 2.0;
/// The pill's centre in X.
pub const BUNDLE_SLOT_CENTER_X: f64 = (BUNDLE_SLOT_RIGHT_X + BUNDLE_SLOT_LEFT_X) / 2.0;
/// The pill's centre in Y: the flavor pair's.
pub const FLAVOR_TUBE_DEPTH: f64 = LOWER_Y;
/// The drain tube's outside diameter.
pub const DRAIN_TUBE_OD: f64 = 4.0;
/// The drain's hole.
pub const DRAIN_TUBE_HOLE_DIA: f64 = DRAIN_TUBE_OD + TUBE_HOLE_CLEARANCE;
/// The drain's Y in the mounting stack.
pub const DRAIN_TUBE_Y: f64 = LOWER_DRAIN_Y;
/// The hole the Westbrass's shank passes the countertop stack in.
pub const SHANK_HOLE_DIAMETER: f64 = 12.6;
/// The above-counter plate's thickness.
pub const ABOVE_COUNTER_PLATE_THICKNESS: f64 = 4.0;
/// The above-counter gasket's thickness.
pub const ABOVE_COUNTER_GASKET_THICKNESS: f64 = 2.0;
/// The display's housing, across.
pub const DISPLAY_HOUSING_WIDTH: f64 = 24.50;
/// The display's housing, along the tip.
pub const DISPLAY_HOUSING_LENGTH: f64 = 44.50;
/// The display's PCB, across.
pub const DISPLAY_PCB_WIDTH: f64 = 23.95;
/// The display's PCB, along the tip.
pub const DISPLAY_PCB_LENGTH: f64 = 43.95;
/// The housing's corner radius.
pub const DISPLAY_CORNER_R: f64 = 5.75;
/// The PCB's corner radius.
pub const DISPLAY_PCB_CORNER_R: f64 = DISPLAY_CORNER_R - (DISPLAY_HOUSING_WIDTH - DISPLAY_PCB_WIDTH) / 2.0;
/// The display's depth from its feet to its glass.
pub const DISPLAY_TOTAL_DEPTH: f64 = 10.35;
/// The housing's depth.
pub const DISPLAY_HOUSING_DEPTH: f64 = 5.0;
/// The PCB's underside, from the glass.
pub const DISPLAY_PCB_BOTTOM_FROM_FRONT: f64 = 6.45;
/// The PCB's underside, from the display's feet.
pub const DISPLAY_PCB_BOTTOM_Z: f64 = DISPLAY_TOTAL_DEPTH - DISPLAY_PCB_BOTTOM_FROM_FRONT;
/// The PCB's top, from the display's feet.
pub const DISPLAY_PCB_TOP_Z: f64 = DISPLAY_TOTAL_DEPTH - DISPLAY_HOUSING_DEPTH;
/// The display cover's lap over the shell.
pub const DISPLAY_COVER_LAP: f64 = 2.0;
/// How far the cover stands over the display's glass.
pub const DISPLAY_COVER_OVER_FACE: f64 = 0.10;

/// What the display cover clears the neck by: the shared head-on seat.
pub fn display_cover_slip() -> f64 {
    crate::catalog::slip()
}
