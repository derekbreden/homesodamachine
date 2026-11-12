//! The main board's deck columns: four posts integral to the lid under the board's mounting
//! holes, each bored for an RX-M3x5.7 heat-set insert that an M3 screw down through the board
//! reaches the whole of. The board stands where the above-core design places it.
use crate::design::above_core;
use hsm_cold_core_interface as core;
use hsm_cold_core_layout::cap::{cap_face_z, world_to_cap};

/// The main board's mounting holes MH1 to MH4 in its PCB frame, the outline whose centre the
/// board is drawn about, and its thickness. The board's design (`hardware/pcb/pcba/pcba.tsx`)
/// and the PCBA tray (`hsm-pcba-numbers`) own these.
pub const BOARD_HOLES: [[f64; 2]; 4] = [[-64.5, 33.0], [13.5, 33.0], [13.5, -33.3], [-64.5, -33.3]];
pub const BOARD_OUTLINE_X: [f64; 2] = [-68.0, 17.0];
pub const BOARD_OUTLINE_Y: [f64; 2] = [-36.3, 36.5];
pub const BOARD_THICKNESS: f64 = 1.6;
/// The M3 screw each column takes through the board.
pub const SCREW_LENGTH: f64 = 8.0;

/// A column: its centre in the cap's own frame, and its top's height over the lid's underside.
#[derive(Clone, Copy, Debug)]
pub struct Column {
    pub xy: [f64; 2],
    pub top: f64,
}

/// The board's holes in the cap's own frame, by X then Y.
pub fn hole_xy() -> Vec<[f64; 2]> {
    let pose = above_core().parts.pcba.pose();
    let centre = [
        (BOARD_OUTLINE_X[0] + BOARD_OUTLINE_X[1]) / 2.,
        (BOARD_OUTLINE_Y[0] + BOARD_OUTLINE_Y[1]) / 2.,
    ];
    let mut points: Vec<[f64; 2]> = BOARD_HOLES
        .iter()
        .map(|h| {
            let [x, y, _] = world_to_cap(pose.point([h[0] - centre[0], h[1] - centre[1], 0.]));
            [x, y]
        })
        .collect();
    points.sort_by(|a, b| a.partial_cmp(b).expect("the holes stand at real points"));
    points.dedup();
    points
}

/// How far proud of the lid's face the board's underside stands: where the design places it, to
/// the micrometre.
pub fn standoff() -> f64 {
    let board = world_to_cap(above_core().parts.pcba.translation_mm)[2];
    let face = world_to_cap([0., 0., cap_face_z()])[2];
    let rounded: f64 = format!("{:.4}", board - face).parse().expect("a rounded height");
    if rounded == 0. { 0. } else { rounded }
}

/// The columns, their tops at the board's underside.
pub fn columns() -> Vec<Column> {
    let top = core::foam_cap_lid_height(&crate::fits()) + standoff();
    hole_xy().into_iter().map(|xy| Column { xy, top }).collect()
}

/// The lid's thickness and its seat on the cap, which a screw crosses before it reaches a column
/// that stops flush beneath the lid; a standing column meets its screw at the board.
fn lid_in_the_way() -> f64 {
    let fits = crate::fits();
    if standoff() == 0. { core::foam_cap_lid_height(&fits) + core::cap_lid_clearance(&fits) } else { 0. }
}

/// How far a seated screw runs into its column, past the board and whatever lid it crosses.
pub fn reach() -> f64 {
    SCREW_LENGTH - (BOARD_THICKNESS + lid_in_the_way())
}

/// The pilot each column is bored to: the insert and its relief, or as deep as a screw through the
/// board can reach and the relief, whichever is deeper. A column whose top is flush takes the
/// whole lid in the screw's way.
pub fn bore_depth() -> f64 {
    (core::DECK_MOUNT_INSERT_LENGTH + core::DECK_MOUNT_BORE_RELIEF)
        .max(SCREW_LENGTH - BOARD_THICKNESS - lid_in_the_way() + core::DECK_MOUNT_BORE_RELIEF)
}
