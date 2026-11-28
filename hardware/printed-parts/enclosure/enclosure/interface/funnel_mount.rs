//! The screw stations shared by the funnel frame and its ledges in the shell.

pub const REAR_ACCESS: f64 = 5.0;
pub const SCREW_GRIP: f64 = 5.8;
pub const PAD_HALF_Y: f64 = 6.0;

/// The back row's seats fall inward from the roof pocket's flanks at this rise per run, so
/// back-top grows them ceiling-down and the frame its matching faces upright, each without
/// support. Each back screw stands square to its seat and crosses it at its station, so its
/// clamp runs straight through the two faces and pushes neither part sideways. It is the regular
/// M3, its insert opens flush on the seat, and the frame's head seat stands `BACK_SCREW_GRIP`
/// from the seat along the screw, low enough that the head stays clear of the funnel brim's aft
/// corner. The pilot runs `BACK_PILOT_RELIEF` past the insert for the longer reach that leaves.
pub const BACK_SEAT_SLOPE: f64 = 1.0;
pub const BACK_SCREW_GRIP: f64 = 4.5;
pub const BACK_PILOT_RELIEF: f64 = 3.0;

/// A back screw's axis on the side `side`: its seat's normal, up and inward.
pub fn back_axis(side: f64) -> [f64; 3] {
    let k = BACK_SEAT_SLOPE.hypot(1.0);
    [-side * BACK_SEAT_SLOPE / k, 0.0, 1.0 / k]
}

/// How far a back screw turns from upright toward its seat's normal, in degrees, as a turn
/// about +Y: positive on the west side.
pub fn back_tilt_degrees(side: f64) -> f64 {
    -side * BACK_SEAT_SLOPE.atan().to_degrees()
}

/// Each row names a mirrored pair by its X axis and offset from the corresponding roof edge.
const ROWS: [(&str, bool, f64, f64); 3] = [
    ("front", true, 93.0, 32.0),
    ("front-aft", true, 93.0, 75.0),
    ("back", false, 87.7, -REAR_ACCESS - 11.2),
];

pub struct Station {
    pub row: &'static str,
    pub front: bool,
    pub x: f64,
    pub y: f64,
    pub side: f64,
}

pub fn stations(front: f64, back: f64) -> impl Iterator<Item = Station> {
    ROWS.into_iter().flat_map(move |(row, is_front, axis, offset)| {
        let y = (if is_front { front } else { back }) + offset;
        [-1.0, 1.0].map(move |side| Station {
            row,
            front: is_front,
            x: side * axis,
            y,
            side,
        })
    })
}
