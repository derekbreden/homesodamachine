//! The lid's two filled cable seats, where the wiring places them (`tools/hsm/assembly-docs/src/
//! wiring/manifold-bank.json` and `rear-level-hook.json`): the front manifold bank, two stepped
//! seats for the J1 and J2 leads, and the hook that holds reservoir A's level leads. Each is a
//! section in the enclosure's XZ plane, extruded along Y over its span.
use crate::P3;
use serde::Deserialize;
use std::sync::OnceLock;

/// The manifold bank: its section's origin on the lid's face, each seat's depth, the two seats'
/// heights, its span, its stock and its retaining lip.
#[derive(Clone, Copy, Debug, Deserialize)]
pub struct Bank {
    pub origin: P3,
    pub seat_depth: f64,
    pub seat_heights: [f64; 2],
    pub span: f64,
    pub stock: f64,
    pub beak: f64,
}

/// The level hook: one seat at its height.
#[derive(Clone, Copy, Debug, Deserialize)]
pub struct Hook {
    pub origin: P3,
    pub seat_depth: f64,
    pub seat_height: f64,
    pub span: f64,
    pub stock: f64,
    pub beak: f64,
}

pub fn manifold_bank() -> Bank {
    static SITE: OnceLock<Bank> = OnceLock::new();
    *SITE.get_or_init(|| {
        serde_json::from_str(include_str!("../../../../../tools/hsm/assembly-docs/src/wiring/manifold-bank.json"))
            .expect("the manifold bank's site parses")
    })
}

pub fn level_hook() -> Hook {
    static SITE: OnceLock<Hook> = OnceLock::new();
    *SITE.get_or_init(|| {
        serde_json::from_str(include_str!("../../../../../tools/hsm/assembly-docs/src/wiring/rear-level-hook.json"))
            .expect("the reservoir A level hook's site parses")
    })
}
