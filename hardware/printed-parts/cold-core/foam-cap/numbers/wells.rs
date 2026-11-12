//! The wiring's junctions on the lid: four lever connectors in two rows on the board-facing back
//! of V-B's wall, levers opening west and wire mouths away from the shared holder stock. Each
//! well holds its connector's blank rear half in closed stock, both lever faces free, and the
//! connector goes in butt first along its own −Y. The machine places the connectors in them.
use crate::P3;
use crate::valve;
pub use hsm_enclosure_numbers::junctions::{WAGO_413, Wago};
use hsm_enclosure_numbers::shell::WAGO_WELL_WALL;

/// The host the wiring model names for the lid's junctions.
pub const HOST: &str = "cold-core";

/// The stock a well keeps round its connector: the enclosure's wells' own.
pub const WALL: f64 = WAGO_WELL_WALL;

/// The fit a well holds its connector on: the shared head-on fit.
pub fn fit() -> f64 {
    crate::fits().slip
}

/// How far the pocket runs past the well's open front.
pub const POCKET_OVERRUN: f64 = 1.;

/// The wiring model's frames on V-B's wall, by rotation rows: wire mouths fore, and aft.
pub const WALL_BACK_FORE: [P3; 3] = [[0., 0., -1.], [0., -1., 0.], [-1., 0., 0.]];
pub const WALL_BACK_AFT: [P3; 3] = [[0., 0., -1.], [0., 1., 0.], [1., 0., 0.]];

/// One junction as the wiring model places it on V-B's wall: its name, its connector, where it
/// stands in V-B's frame, its frame, and what it joins. The wiring model's placement owns these.
pub struct Junction {
    pub name: &'static str,
    pub wago: Wago,
    pub at: P3,
    pub rotation: [P3; 3],
    pub purpose: &'static str,
}

pub const JUNCTIONS: [Junction; 4] = [
    Junction { name: "wago-sensors", wago: WAGO_413, at: [-6.69, -11.05434, -11.], rotation: WALL_BACK_FORE,
               purpose: "PCB J4 / temperature bus / flow meter common" },
    Junction { name: "wago-v12", wago: WAGO_413, at: [15.41, -11.05434, -11.], rotation: WALL_BACK_FORE,
               purpose: "PSU secondary / relay 2 COM / PCB J10 V12" },
    Junction { name: "wago-gnd", wago: WAGO_413, at: [15.41, 10.94566, -11.], rotation: WALL_BACK_AFT,
               purpose: "PSU secondary / pump negative / PCB J10 GND" },
    Junction { name: "wago-reeds-b", wago: WAGO_413, at: [-6.69, 10.94566, -11.], rotation: WALL_BACK_AFT,
               purpose: "PCB J7 / reservoir B / carbonator reed common" },
];

/// A well's connector in the enclosure: its junction's name, its connector, and its frame.
#[derive(Clone, Copy)]
pub struct Well {
    pub name: &'static str,
    pub wago: Wago,
    pub rotation: [P3; 3],
    pub translation: P3,
}

/// The lid's wells, in the wiring model's order.
pub fn wells() -> Vec<Well> {
    let vb = valve::pose();
    JUNCTIONS
        .iter()
        .map(|j| Well { name: j.name, wago: j.wago, rotation: j.rotation, translation: vb.point(j.at) })
        .collect()
}
