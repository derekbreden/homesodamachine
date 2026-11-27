//! The screw stations shared by the funnel frame and its ledges in the shell.

pub const REAR_ACCESS: f64 = 5.0;
pub const SCREW_GRIP: f64 = 5.8;
pub const PAD_HALF_Y: f64 = 6.0;

/// The back row's seats fall inward from the roof pocket's flanks at this rise per run, so
/// back-top grows them ceiling-down and the frame its matching faces upright, each without
/// support. The back screw is the deep M3 and its tip passes this far beyond its insert, which
/// presses in from the ledge's flat underside below the seat. Where the bore crosses a seat it
/// runs on as a slot of its own width, closed by a face square to the seat that lands this far
/// past the bore wall.
pub const BACK_SEAT_SLOPE: f64 = 1.0;
pub const BACK_SCREW_LENGTH: f64 = crate::fasteners::M3_DEEP_SCREW_LENGTH;
pub const BACK_TIP_PASS: f64 = 0.5;
pub const BACK_BORE_LAND: f64 = 1.0;

/// A back insert's entrance on its ledge's underside, under a ledge plane at `ledge`.
pub fn back_insert_entry(ledge: f64) -> f64 {
    ledge + SCREW_GRIP - BACK_SCREW_LENGTH + BACK_TIP_PASS
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
