//! The shared catalogs as typed values: the fits a printed face is cut to, from the scalars
//! catalog, and the colours of the materials parts are made of, from the materials catalog, as the
//! viewer's files carry them.
use serde::Deserialize;
use std::sync::OnceLock;

/// The allowances a printed face is cut to (`hardware/printed-parts/cadlib/fits.py` says what
/// each one is for).
#[derive(Clone, Copy, Debug, Deserialize)]
pub struct Fits {
    /// What two printed faces pressed together add to their nominal stack: a seat.
    pub slip: f64,
    /// What a face that slides past its mate adds beyond the seat.
    pub sliding_extra: f64,
    /// What a supported overhang's underside adds.
    pub supported_surface: f64,
    /// The bore an M5 screw's thread passes through.
    pub m5_thread_pass_dia: f64,
}

impl Fits {
    /// A face that slides past its mate.
    pub fn running(&self) -> f64 {
        self.slip + self.sliding_extra
    }
}

#[derive(Deserialize)]
struct Scalars {
    fits: Fits,
}

/// The shared fits.
pub fn fits() -> Fits {
    static FITS: OnceLock<Fits> = OnceLock::new();
    *FITS.get_or_init(|| {
        serde_json::from_str::<Scalars>(include_str!("../../shared-data/catalog/scalars.json"))
            .expect("the shared scalars catalog parses")
            .fits
    })
}

/// A catalog colour as the catalog writes it: sRGB channels, or eight-bit sRGB.
#[derive(Deserialize)]
#[serde(untagged)]
enum Swatch {
    Channels { args: Vec<f64> },
    Bytes { bytes: [u8; 3] },
}

/// The materials these parts are made of.
#[derive(Deserialize)]
#[allow(non_snake_case)]
struct Colors {
    M_PETGF_BLACK: Swatch,
    M_PETG_BLACK: Swatch,
    M_TPU_BLACK: Swatch,
    M_STAINLESS: Swatch,
    M_ALUMINIUM: Swatch,
    M_COPPER: Swatch,
    C_PCBA: Swatch,
}

#[derive(Deserialize)]
struct Materials {
    colors: Colors,
}

fn colors() -> &'static Colors {
    static MATERIALS: OnceLock<Materials> = OnceLock::new();
    &MATERIALS
        .get_or_init(|| {
            serde_json::from_str(include_str!("../../shared-data/catalog/materials.json"))
                .expect("the shared materials catalog parses")
        })
        .colors
}

/// An sRGB colour as the viewer's files carry it: each channel turned linear at double precision
/// and kept at single.
pub fn linear(srgb: [f64; 3]) -> [f64; 3] {
    srgb.map(|c| (if c <= 0.04045 { c / 12.92 } else { ((c + 0.055) / 1.055).powf(2.4) }) as f32 as f64)
}

fn colour(swatch: &Swatch) -> [f64; 3] {
    match swatch {
        Swatch::Channels { args } => linear([args[0], args[1], args[2]]),
        Swatch::Bytes { bytes } => linear(bytes.map(|b| f64::from(b) / 255.)),
    }
}

/// Black glass-filled PETG: the shop's printed tools.
pub fn petgf_black() -> [f64; 3] {
    colour(&colors().M_PETGF_BLACK)
}

/// Black PETG.
pub fn petg_black() -> [f64; 3] {
    colour(&colors().M_PETG_BLACK)
}

/// Black TPU: the compliant fittings.
pub fn tpu_black() -> [f64; 3] {
    colour(&colors().M_TPU_BLACK)
}

/// Stainless steel.
pub fn stainless() -> [f64; 3] {
    colour(&colors().M_STAINLESS)
}

/// Aluminium.
pub fn aluminium() -> [f64; 3] {
    colour(&colors().M_ALUMINIUM)
}

/// Copper.
pub fn copper() -> [f64; 3] {
    colour(&colors().M_COPPER)
}

/// The assembled main board's solder mask.
pub fn pcba() -> [f64; 3] {
    colour(&colors().C_PCBA)
}
