//! The main board's numbers, in millimetres, in its own PCB frame (pcbX and pcbY as
//! `hardware/pcb/pcba/pcba.tsx` lays the board out), with Z up from the board's underside: the
//! outline, the MH1–MH4 mounting holes, the thickness, the through-hole tail envelope below the
//! underside, and how the populated board's component boxes are read off its fab model.

/// The board's outline.
pub const OUTLINE_X: [f64; 2] = [-68.0, 17.0];
pub const OUTLINE_Y: [f64; 2] = [-36.3, 36.5];
/// MH1–MH4, the board's electrically isolated plated mounting holes, and their bore.
pub const HOLES: [[f64; 2]; 4] = [[-64.5, 33.0], [13.5, 33.0], [13.5, -33.3], [-64.5, -33.3]];
pub const HOLE_DIAMETER: f64 = 3.2;
/// The bare board's thickness.
pub const THICKNESS: f64 = 1.6;
/// How far the through-hole tails reach below the underside.
pub const PIN_DROP: f64 = 2.0;
/// Within this of a mounting hole the underside carries only the board's own solder joints.
pub const HOLE_REACH: f64 = 8.0;

/// A through-hole solder joint near a mounting hole: its pin, its place, and its diameter.
pub struct Joint {
    pub pin: &'static str,
    pub at: [f64; 2],
    pub diameter: f64,
}

/// The joints within `HOLE_REACH` of a mounting hole.
pub const JOINTS: [Joint; 6] = [
    Joint { pin: "J1.1", at: [11.0, 26.48], diameter: 1.6 },
    Joint { pin: "J8.4", at: [5.05, 31.0], diameter: 1.5 },
    Joint { pin: "J7.1", at: [7.0, -30.3], diameter: 1.8 },
    Joint { pin: "J11.1", at: [-62.0, -27.6], diameter: 1.5 },
    Joint { pin: "J11.2", at: [-62.0, -25.1], diameter: 1.5 },
    Joint { pin: "J3.4", at: [-56.0, -30.3], diameter: 1.5 },
];

/// The fab model's board stands on its mid-plane: its faces are this far either side.
pub const FAB_HALF_THICKNESS: f64 = 0.7;
/// A component box counts above or below the board once it passes a face by more than this.
pub const FAB_FACE_MARGIN: f64 = 0.05;
/// A box thinner than this along any axis is a marking, not a component.
pub const FAB_LEAST_BOX: f64 = 0.2;
/// A box this large a share of the outline both ways is the fab model's own board.
pub const FAB_BOARD_SHARE: f64 = 0.95;

/// The outline's width along X.
pub fn width() -> f64 {
    OUTLINE_X[1] - OUTLINE_X[0]
}

/// The outline's depth along Y.
pub fn depth() -> f64 {
    OUTLINE_Y[1] - OUTLINE_Y[0]
}

/// The outline's centre, which the board's model is centred on.
pub fn centre() -> [f64; 2] {
    [(OUTLINE_X[0] + OUTLINE_X[1]) / 2.0, (OUTLINE_Y[0] + OUTLINE_Y[1]) / 2.0]
}
