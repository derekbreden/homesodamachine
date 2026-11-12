//! The Sculpted display cover's numbers, in millimetres, in the tip frame: x across the neck, s
//! back up it from the tube exit, n out through the glass. The cover is a skin lofted from its
//! skirt round the neck up to its face over the display, its window opened for the glass, its
//! lips snapping into the shell's grooves, printed with its wings leaned in.

use hsm_faucet_numbers::interface::{DISPLAY_CORNER_R, DISPLAY_COVER_OVER_FACE, DISPLAY_HOUSING_WIDTH, display_cover_slip};
use hsm_faucet_numbers::shell::*;
use hsm_faucet_numbers::snap;

/// How far the window stands in from the display's housing all round.
pub const WINDOW_INSET: f64 = 2.0;
/// The window, across and its corner radius.
pub const WINDOW_HALF_X: f64 = DISPLAY_HOUSING_WIDTH / 2.0 - WINDOW_INSET;
pub const WINDOW_CORNER_R: f64 = DISPLAY_CORNER_R - WINDOW_INSET;
/// The reach from the lip seating lands to the raised bezel and skirt shoulder.
pub const WING_REACH: f64 = 0.83;
/// The bezel's underside, over the glass, and its top.
pub const BEZEL_N_BOTTOM: f64 = DISPLAY_FACE_N + DISPLAY_COVER_OVER_FACE + WING_REACH;
pub const BEZEL_N_TOP: f64 = DISPLAY_COVER_TOP_N + WING_REACH;
/// The cover's lower front edge: where it starts up from the open underside, along n, and its
/// slope up per millimetre along s.
pub const FRONT_RIM_N: f64 = 14.0;
pub const FRONT_RIM_SLOPE: f64 = 1.8;
/// How far the skirt runs on past the face toward the base.
pub const REAR_SKIRT_EXTENSION: f64 = 1.2;
/// The lower rear edge: where it starts along s, and how far back it runs per millimetre up.
pub const REAR_TRIM_S0: f64 = 42.1;
pub const REAR_TRIM_DS_DN: f64 = 0.6;
/// What the lips' inner corners are relieved by.
pub const LIP_RELIEF: f64 = snap::LIP_INNER_EDGE_RELIEF;
/// Radial clearance for the printed lip to settle against the groove floor under spring preload.
pub const LIP_ROOT_CLEARANCE: f64 = 0.2;
pub const LIP_R: f64 = DISPLAY_CLIP_LIP_RADIUS + LIP_ROOT_CLEARANCE;
/// Clearance above the dispense cap at the front of the cover.
pub const NOSE_ARCH_LIFT: f64 = 0.5;
/// Clearance over the curved neck at the rear skirt, aft of both snap lips.
pub const REAR_ARCH_LIFT: f64 = 0.5;

/// The window along s.
pub fn window_s() -> [f64; 2] {
    [display_s_bottom() + DISPLAY_CRADLE_CLEARANCE + WINDOW_INSET, display_s_top() - DISPLAY_CRADLE_CLEARANCE - WINDOW_INSET]
}

/// The window along n: from under the bezel out past the cover's face.
pub fn window_n() -> [f64; 2] {
    [BEZEL_N_BOTTOM - 0.1, BEZEL_N_TOP + 1.0]
}

/// What the cover clears the neck by.
pub fn neck_clearance_r() -> f64 {
    DISPLAY_NECK_OUTER_R + display_cover_slip()
}

/// How far each wing leans in per millimetre down from the bezel: its preload, over its run from
/// the bezel to the lips' tops.
pub fn wing_slope() -> f64 {
    snap::X_PRELOAD / (BEZEL_N_BOTTOM - DISPLAY_CLIP_TOP_N)
}

/// The skin's outline rows, `[width, length, corner r, n, centre s]`: the skirt at its bottom and
/// at its shoulder, then the face.
pub fn outer_rows() -> [[f64; 5]; 3] {
    let skirt_width = display_cover_skirt_width();
    let skirt_length = display_cover_skirt_length() + REAR_SKIRT_EXTENSION;
    let skirt_s = display_cover_center_s() + REAR_SKIRT_EXTENSION / 2.0;
    [
        [skirt_width, skirt_length, DISPLAY_COVER_SKIRT_R, DISPLAY_COVER_BOTTOM_N, skirt_s],
        [skirt_width, skirt_length, DISPLAY_COVER_SKIRT_R, DISPLAY_COVER_SHOULDER_N + WING_REACH, skirt_s],
        [DISPLAY_COVER_FACE_WIDTH, display_cover_face_length(), DISPLAY_COVER_FACE_R, BEZEL_N_TOP, display_cover_center_s()],
    ]
}

/// The prism the skin is clamped to, `[half x, s0, s1, n0, n1]`.
pub fn outer_clamp() -> [f64; 5] {
    [30.0, DISPLAY_HEAD_S_MIN, display_head_s_max() + REAR_SKIRT_EXTENSION + 1.0, -30.0, 40.0]
}

/// The cavity's outline rows, each the shell's with the housing's centre along s.
pub fn cavity_rows() -> [[f64; 5]; 3] {
    let centre = display_housing_center_s();
    let [skirt, mut shoulder, mut ceiling] = display_cover_inner_rows();
    shoulder[3] += WING_REACH;
    ceiling[3] = BEZEL_N_BOTTOM;
    [skirt, shoulder, ceiling].map(|[w, l, r, n]| [w, l, r, n, centre])
}

/// The prisms the cavity is clamped to: the shell's, and the dispense face's.
pub fn cavity_clamps() -> [[f64; 5]; 2] {
    [display_cover_inner_clamp(), [50.0, DISPENSE_FACE_THICKNESS, display_head_s_max() + 1.0, -30.0, 40.0]]
}

/// The band the lips are cut from, `[half x, s0, s1, n0, n1]`.
pub fn lip_band() -> [f64; 5] {
    [display_cover_skirt_width() / 2.0 + 1.0, display_clip_s_bottom(), display_clip_s_top(), DISPLAY_CLIP_BOTTOM_N, DISPLAY_CLIP_TOP_N]
}
