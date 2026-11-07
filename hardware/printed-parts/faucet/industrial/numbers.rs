//! The Industrial faucet's numbers, in millimetres: the shell's gooseneck and cutters on round
//! stock of its own below the zone-5 seam (a foot disc, a body over the Westbrass and the neck
//! standing on it), its round above-counter plate and gasket, and its rectangular display cover,
//! in the tip frame (x across the neck, s back up it, n out through the glass).

use hsm_faucet_numbers::interface::{DISPLAY_CORNER_R, DISPLAY_COVER_OVER_FACE, DISPLAY_HOUSING_WIDTH, display_cover_slip};
use hsm_faucet_numbers::shell::*;
use hsm_faucet_numbers::snap;

// The base.

/// The round foot the base, the plate and the gasket share.
pub const FOOT_RADIUS: f64 = FOOT_WIDTH.max(FOOT_DEPTH) / 2.0;
/// The foot disc's top.
pub const FOOT_TOP: f64 = 14.0;
/// The body over the Westbrass: its centre behind the shank, and the stock it leaves the cable's
/// turn.
pub const BODY_CENTER_Y: f64 = 5.4;
pub const SIGNAL_TURN_STOCK_ALLOWANCE: f64 = 1.0;
pub const BODY_RADIUS: f64 = WESTBRASS_BORE_DIAMETER / 2.0 + BODY_CENTER_Y + WALL_THICKNESS_MIN + SIGNAL_TURN_STOCK_ALLOWANCE;
pub const BODY_TOP: f64 = ZONE4_Z_TOP;
/// The neck standing on the body up to the seam, and how far it runs on past it.
pub const NECK_CENTER_Y: f64 = SODA_FAUCET_TUBE_Y + TUBE_SHELL_CENTER_Y;
pub const NECK_RADIUS: f64 = TUBE_SHELL_OUTER_R;
pub const NECK_JOIN_OVERLAP: f64 = 0.2;

// The display cover.

/// The cover's plate: across, along s, and its walls.
pub const COVER_WIDTH: f64 = 29.8;
pub const COVER_LENGTH: f64 = 49.75;
pub const COVER_UPPER_SIDE_WALL: f64 = WALL_THICKNESS_MIN;
pub const COVER_LOWER_SIDE_WALL: f64 = 1.25;
pub const COVER_REAR_WALL: f64 = WALL_THICKNESS_MIN;
pub const COVER_FRONT_WALL: f64 = DISPENSE_FACE_THICKNESS;
/// The cover's underside, along n, and how far its wings stand past the shell's cover.
pub const COVER_N_BOTTOM: f64 = DISPLAY_COVER_BOTTOM_N;
pub const WING_EXTENSION: f64 = 0.50;
/// The cover's top and the bezel's underside, along n.
pub const COVER_N_TOP: f64 = DISPLAY_COVER_TOP_N + WING_EXTENSION;
pub const BEZEL_N_BOTTOM: f64 = DISPLAY_FACE_N + DISPLAY_COVER_OVER_FACE + WING_EXTENSION;
/// How far the window stands in from the display's housing all round.
pub const WINDOW_INSET: f64 = 2.0;
pub const WINDOW_HALF_X: f64 = DISPLAY_HOUSING_WIDTH / 2.0 - WINDOW_INSET;
pub const WINDOW_CORNER_R: f64 = DISPLAY_CORNER_R - WINDOW_INSET;
/// What the lips' inner corners are relieved by, and their radius about the neck.
pub const LIP_RELIEF: f64 = snap::LIP_INNER_EDGE_RELIEF;
pub const LIP_R: f64 = DISPLAY_NECK_OUTER_R - (DISPLAY_NECK_OUTER_R - DISPLAY_CLIP_LIP_RADIUS);

/// The window along s.
pub fn window_s() -> [f64; 2] {
    [display_s_bottom() + DISPLAY_CRADLE_CLEARANCE + WINDOW_INSET, display_s_top() - DISPLAY_CRADLE_CLEARANCE - WINDOW_INSET]
}

/// The window along n.
pub fn window_n() -> [f64; 2] {
    [BEZEL_N_BOTTOM - 0.1, COVER_N_TOP + 1.0]
}

/// What the cover's arch clears the neck by.
pub fn neck_clearance_r() -> f64 {
    DISPLAY_NECK_OUTER_R + display_cover_slip()
}

/// How far each wing leans in per millimetre down from the bezel.
pub fn wing_slope() -> f64 {
    snap::X_PRELOAD / (BEZEL_N_BOTTOM - DISPLAY_CLIP_TOP_N)
}

/// The wing's inward lean at `n`: its preload, falling off up to the bezel.
pub fn preload(n: f64) -> f64 {
    (snap::X_PRELOAD * (BEZEL_N_BOTTOM - n) / (BEZEL_N_BOTTOM - DISPLAY_CLIP_TOP_N)).max(0.0)
}

/// The cavity's sections, `[half x, n]`: straight from under the cover to the display's feet,
/// leaning in from there to the bezel.
pub fn cavity_sections() -> [[f64; 2]; 3] {
    let upper = COVER_WIDTH / 2.0 - COVER_UPPER_SIDE_WALL;
    let lower = (upper + preload(DISPLAY_FEET_N)).min(COVER_WIDTH / 2.0 - COVER_LOWER_SIDE_WALL);
    [[lower, COVER_N_BOTTOM - 1.0], [lower, DISPLAY_FEET_N], [upper, BEZEL_N_BOTTOM]]
}

/// The cavity's span along s, from the front wall to the rear.
pub const COVER_CAVITY_S: [f64; 2] = [COVER_FRONT_WALL, COVER_LENGTH - COVER_REAR_WALL];
