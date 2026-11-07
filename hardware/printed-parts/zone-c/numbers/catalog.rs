//! The shared catalogs zone C takes from: the materials' colours, as the files carry them, and the
//! viewer's surface tolerance.
use crate::Color;
use serde::Deserialize;
use std::collections::HashMap;
use std::sync::OnceLock;

#[derive(Deserialize)]
struct Materials {
    colors: HashMap<String, serde_json::Value>,
    aliases: HashMap<String, String>,
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

/// An sRGB colour as the files carry it: linear RGB at single precision.
pub fn linear(srgb: [f64; 3]) -> Color {
    srgb.map(|c| curve(c) as f32 as f64)
}

/// The catalog colour `name`, through its alias: given in fractions, or in bytes.
pub fn color(name: &str) -> Color {
    let m = materials();
    let key = m.aliases.get(name).map(String::as_str).unwrap_or(name);
    let entry = m.colors.get(key).unwrap_or_else(|| panic!("the materials catalog has no {key}"));
    let channel = |i: usize| match (entry["args"][i].as_f64(), entry["bytes"][i].as_f64()) {
        (Some(fraction), _) => fraction,
        (None, Some(byte)) => byte / 255.0,
        _ => panic!("{key} has no channels"),
    };
    linear([channel(0), channel(1), channel(2)])
}

fn curve32(v: f32) -> f32 {
    if v <= 0.04045_f32 { v / 12.92_f32 } else { ((v + 0.055_f32) / 1.055_f32).powf(2.4_f32) }
}

/// A `#RRGGBB` colour as the files carry it, converted at single precision throughout.
pub fn hex(code: &str) -> Color {
    let channel = |i: usize| {
        let byte = u8::from_str_radix(&code[1 + 2 * i..3 + 2 * i], 16).expect("a hex colour");
        curve32(byte as f32 / 255_f32) as f64
    };
    [channel(0), channel(1), channel(2)]
}

/// The black silicone the funnel is cast in.
pub fn silicone_black() -> Color {
    color("M_SILICONE_BLACK")
}

/// The black glass-filled PET the frame and the cradle print in.
pub fn petgf_black() -> Color {
    color("M_PETGF_BLACK")
}

/// The black PETG the cover prints in.
pub fn petg_black() -> Color {
    color("M_PETG_BLACK")
}

/// How far the viewer's surface may stand from the solid, per millimetre of the part's mean size.
pub const VIEWER_DEFLECTION_RATIO: f64 = 0.001;
