//! The shell's interior faces in X: the interior, each quadrant's flank face, the lip's inner
//! face, where the back flanks start, and the corner columns' arcs.
use crate::Bounds;
use crate::shell::*;

pub fn interior_x() -> [f64; 2] {
    [-(APPLIANCE_WIDTH / 2.0 - WALL), APPLIANCE_WIDTH / 2.0 - WALL]
}

fn flank_face(flank_t: f64) -> [f64; 2] {
    let [ix0, ix1] = interior_x();
    let grown = flank_t - WALL;
    [ix0 + grown, ix1 - grown]
}

pub fn back_top_flank_face() -> [f64; 2] {
    flank_face(BACK_TOP_FLANK_T)
}
pub fn back_bottom_flank_face() -> [f64; 2] {
    flank_face(BACK_BOTTOM_FLANK_T)
}
pub fn front_bottom_flank_face() -> [f64; 2] {
    flank_face(FRONT_BOTTOM_FLANK_T)
}
pub fn front_top_flank_face() -> [f64; 2] {
    flank_face(FRONT_TOP_FLANK_T)
}

/// The lip's inner face: one wall in from the interior.
pub fn lip_face_x() -> [f64; 2] {
    let [ix0, ix1] = interior_x();
    [ix0 + WALL, ix1 - WALL]
}

/// Where the back flanks start behind the Y joint's lip and its seam margin.
pub fn back_flank_start(y_joint: f64) -> f64 {
    y_joint + LIP_LEN + Z_LIP_Y_MARGIN
}

pub fn column_arc(inner: &Bounds, sx: f64, sy: f64) -> [f64; 2] {
    [if sx < 0.0 { inner[0] } else { inner[1] }, if sy < 0.0 { inner[2] } else { inner[3] }]
}
