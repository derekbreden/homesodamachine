//! The shared catalogs the faucet takes from: the materials' colours and the printed fits.

use crate::Color;
use serde::Deserialize;
use std::sync::OnceLock;

#[derive(Deserialize)]
struct Materials {
    colors: std::collections::HashMap<String, serde_json::Value>,
    aliases: std::collections::HashMap<String, String>,
}

fn materials() -> &'static Materials {
    static MATERIALS: OnceLock<Materials> = OnceLock::new();
    MATERIALS.get_or_init(|| {
        serde_json::from_str(include_str!("../../../../tools/hsm/shared-data/catalog/materials.json"))
            .expect("the shared materials catalog parses")
    })
}

fn curve(v: f64) -> f64 {
    if v <= 0.04045 { v / 12.92 } else { ((v + 0.055) / 1.055).powf(2.4) }
}

/// The catalog colour `name`'s sRGB channels as fractions, through its alias, alpha included where
/// it has one.
pub fn srgb(name: &str) -> Vec<f64> {
    let m = materials();
    let key = m.aliases.get(name).map(String::as_str).unwrap_or(name);
    let entry = m.colors.get(key).unwrap_or_else(|| panic!("the materials catalog has no {key}"));
    entry["args"]
        .as_array()
        .and_then(|a| a.iter().map(serde_json::Value::as_f64).collect::<Option<Vec<_>>>())
        .unwrap_or_else(|| panic!("the materials catalog gives {key} no fractional channels"))
}

/// The catalog colour `name` as the files carry it: linear RGB at single precision.
pub fn color(name: &str) -> Color {
    let srgb = srgb(name);
    linear([srgb[0], srgb[1], srgb[2]])
}

/// An sRGB colour as the files carry it: linear RGB at single precision.
pub fn linear(srgb: [f64; 3]) -> Color {
    srgb.map(|c| curve(c) as f32 as f64)
}

#[derive(Deserialize)]
struct Fits {
    slip: f64,
}

#[derive(Deserialize)]
struct Scalars {
    fits: Fits,
}

fn scalars() -> &'static Scalars {
    static SCALARS: OnceLock<Scalars> = OnceLock::new();
    SCALARS.get_or_init(|| {
        serde_json::from_str(include_str!("../../../../tools/hsm/shared-data/catalog/scalars.json"))
            .expect("the shared scalars catalog parses")
    })
}

/// What two printed faces pressed together on a head-on seat clear each other by.
pub fn slip() -> f64 {
    scalars().fits.slip
}

/// The faucet's printed black: glass-filled PET.
pub fn faucet_black() -> Color {
    color("C_FAUCET_BLACK")
}

/// The black TPU of the gasket and the thimble.
pub fn tpu_black() -> Color {
    color("M_TPU_BLACK")
}
