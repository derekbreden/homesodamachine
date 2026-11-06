//! The anchor cap and the tube anchor rib it closes: the seat, the rib's span along the tube,
//! and the slot and headroom the cap's wings take in the face the rib roots on.
use crate::WALL;
use crate::fits::slip;

/// The beverage tube's outer diameter, which the rib and the cap seat.
pub const TUBE_OD: f64 = 6.35;
/// The cap's length along the tube.
pub const CAP_LEN: f64 = 10.0;
/// Each spring wing, and its lip's reach off the wing.
pub const WING: f64 = 1.5;
pub const ENGAGE: f64 = 1.2;
/// The wings' tops above the axis plane, and the headroom over them to the root face.
pub const WING_TOP: f64 = 10.3;
pub const HEADROOM: f64 = 0.6;
/// The end webs round the catch windows.
pub const END_WEB: f64 = WALL;

/// The seat's radius, and the rib's half-width round it.
pub fn seat_r() -> f64 {
    TUBE_OD / 2.0 + slip()
}

pub fn rib_r() -> f64 {
    seat_r() + WALL
}

/// The air at each end of the cap, and between each wing and the rib's flank.
pub fn end_air() -> f64 {
    slip()
}

pub fn wing_air() -> f64 {
    slip()
}

/// The catch window's length along the tube, and the rib's with its end webs.
pub fn window_len() -> f64 {
    CAP_LEN + 2.0 * end_air()
}

pub fn rib_len() -> f64 {
    window_len() + 2.0 * END_WEB
}

/// The slot each wing takes in the root face: its width, and its top above the axis plane.
pub fn slot_w() -> f64 {
    wing_air() + WING + ENGAGE + 2.0 * slip()
}

pub fn slot_top() -> f64 {
    WING_TOP + HEADROOM
}
