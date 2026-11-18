//! The screw stations shared by the funnel frame and its ledges in the shell.

pub const REAR_ACCESS: f64 = 5.0;
pub const SCREW_GRIP: f64 = 5.8;
pub const PAD_HALF_Y: f64 = 6.0;

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
