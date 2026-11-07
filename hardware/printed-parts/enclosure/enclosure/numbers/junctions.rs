//! The wiring's junctions on the two top pieces, where the wiring model places them: each one's
//! connector, the piece that holds it, its frame, and how far its well's mouth stands back of the
//! lever face. The pieces cut their wells round them, and the machine places the connectors in
//! them.
use crate::P3;
use crate::quadrant::Y;

/// A Wago 221 lever connector, by its body: across its poles, along its wire axis, and its
/// height, with the catalog size its reference model is named by.
#[derive(Clone, Copy)]
pub struct Wago {
    pub size: &'static str,
    pub width: f64,
    pub depth: f64,
    pub height: f64,
}

pub const WAGO_413: Wago = Wago { size: "413", width: 18.8, depth: 18.6, height: 8.4 };
pub const WAGO_415: Wago = Wago { size: "415", width: 30.0, depth: 18.6, height: 8.4 };
pub const WAGO_420: Wago = Wago { size: "420", width: 29.8, depth: 18.3, height: 15.8 };

/// The wiring model's frames, by rotation rows: lever ports fore, the same stood on end, and
/// lying on the east flank.
pub const PORTS_FORE: [P3; 3] = [[-1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]];
pub const UPRIGHT_PORTS_FORE: [P3; 3] = [[0.0, 0.0, 1.0], [0.0, -1.0, 0.0], [1.0, 0.0, 0.0]];
pub const EAST_FLANK: [P3; 3] = [[0.0, -1.0, 0.0], [0.0, 0.0, -1.0], [1.0, 0.0, 0.0]];

/// One junction the wiring model mounts on a top piece: its connector, where it stands, and how
/// far its well's mouth stands back of the lever face.
pub struct Junction {
    pub name: &'static str,
    pub wago: Wago,
    pub host: Y,
    pub rotation: [P3; 3],
    pub translation: P3,
    pub mouth: f64,
}

/// The wiring model's junctions on the two top pieces, in its placement order: the mains live,
/// earth and neutral buses under the ceiling PSU, and the two valve-manifold commons.
pub const JUNCTIONS: [Junction; 5] = [
    Junction { name: "wago-h", wago: WAGO_413, host: Y::Back, rotation: PORTS_FORE,
               translation: [-81.0, 456.5, 264.0], mouth: 0.0 },
    Junction { name: "wago-g", wago: WAGO_413, host: Y::Back, rotation: UPRIGHT_PORTS_FORE,
               translation: [-90.6, 457.5, 295.5], mouth: 0.0 },
    Junction { name: "wago-n", wago: WAGO_413, host: Y::Back, rotation: UPRIGHT_PORTS_FORE,
               translation: [-65.4, 456.5, 267.5], mouth: 0.0 },
    Junction { name: "wago-mana", wago: WAGO_420, host: Y::Front, rotation: EAST_FLANK,
               translation: [95.20, 185.05, 277.0], mouth: -0.75 },
    Junction { name: "wago-manb", wago: WAGO_415, host: Y::Front, rotation: EAST_FLANK,
               translation: [95.05, 177.65, 243.0], mouth: -0.75 },
];
