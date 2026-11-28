//! The wiring's junctions on the two top pieces, where the wiring model places them: each one's
//! connector, the piece that holds it, its frame, and how far its well's mouth stands back of the
//! lever face. The pieces cut their wells round them, and the machine places the connectors in
//! them.
use crate::{Bounds, P3};
use crate::quadrant::Y;
use serde::Deserialize;
use std::sync::OnceLock;

/// A Wago 221 lever connector, by its body: across its poles, along its wire axis, and its
/// height, with the catalog size its reference model is named by.
#[derive(Clone, Copy)]
pub struct Wago {
    pub size: &'static str,
    pub width: f64,
    pub depth: f64,
    pub height: f64,
    /// The printed opening, short side between cheeks × long side across the poles.
    pub well_opening: [f64; 2],
}

pub const WAGO_413: Wago = Wago {
    size: "413",
    width: 18.8,
    depth: 18.6,
    height: 8.4,
    well_opening: [8.20, 18.70],
};
pub const WAGO_415: Wago = Wago {
    size: "415",
    width: 30.0,
    depth: 18.6,
    height: 8.4,
    well_opening: [8.10, 30.20],
};
pub const WAGO_420: Wago = Wago {
    size: "420",
    width: 29.8,
    depth: 18.3,
    height: 15.8,
    well_opening: [15.70, 30.10],
};

impl Wago {
    /// The blind pocket in the connector frame. A relieved roof shifts the long-axis
    /// centre by half its one-sided allowance while keeping the finished opening to size.
    pub fn well_cut(self, stop_clearance: f64, end: f64, roof_relief: f64) -> Bounds {
        let [short, long] = self.well_opening;
        [
            (roof_relief - long) / 2.0, (roof_relief + long) / 2.0,
            -self.depth / 2.0 - stop_clearance, end,
            (self.height - short) / 2.0, (self.height + short) / 2.0,
        ]
    }
}

/// One junction the wiring model mounts on a top piece: its connector, where it stands, and how
/// far its well's mouth stands back of the lever face.
pub struct Junction {
    pub name: String,
    pub wago: Wago,
    pub host: Y,
    pub rotation: [P3; 3],
    pub translation: P3,
    pub mouth: f64,
    pub fit: f64,
}

#[derive(Deserialize)]
struct Placement {
    name: String,
    size: String,
    host: String,
    rotation: [P3; 3],
    translation_mm: P3,
    mouth_mm: f64,
}

#[derive(Deserialize)]
struct Document {
    well_fit_mm: f64,
    junctions: Vec<Placement>,
}

/// The electrical join ID of a through-funnel connector in the common west-wall bank.
pub fn final_join_id(body: &str) -> Option<&str> {
    body.strip_prefix("wiring-junction-")
}

/// The connectors and their printed pockets share these runtime design placements.
pub fn junctions() -> &'static [Junction] {
    static JUNCTIONS: OnceLock<Vec<Junction>> = OnceLock::new();
    JUNCTIONS.get_or_init(|| {
        let document: Document = crate::input::json("hardware/manifold-layout/junctions.json")
            .expect("the enclosure junction placements parse");
        document
            .junctions
            .into_iter()
            .map(|j| Junction {
                name: j.name,
                wago: match j.size.as_str() {
                    "413" => WAGO_413,
                    "415" => WAGO_415,
                    "420" => WAGO_420,
                    size => panic!("no enclosure connector dimensions for WAGO {size}"),
                },
                host: match j.host.as_str() {
                    "front-top" => Y::Front,
                    "back-top" => Y::Back,
                    host => panic!("no enclosure junction host {host}"),
                },
                rotation: j.rotation,
                translation: j.translation_mm,
                mouth: j.mouth_mm,
                fit: document.well_fit_mm,
            })
            .collect()
    })
}
