//! The shared catalogs the cold core's parts are cut and coloured from: the fits a printed face is
//! cut to, from the scalars catalog, and the colours of the materials the parts are made of, from
//! the materials catalog, as the viewer's files carry them.
use hsm_cold_core_interface::Fits;
use serde::Deserialize;
use std::sync::OnceLock;

#[derive(Deserialize)]
struct CatalogFits {
    slip: f64,
    sliding_extra: f64,
    supported_surface: f64,
    m5_thread_pass_dia: f64,
}

#[derive(Deserialize)]
struct Scalars {
    fits: CatalogFits,
}

/// The shared fits, as every printed part on the machine is cut to them.
pub fn fits() -> Fits {
    static FITS: OnceLock<Fits> = OnceLock::new();
    *FITS.get_or_init(|| {
        let catalog: Scalars =
            serde_json::from_str(include_str!("../../../../tools/hsm/shared-data/catalog/scalars.json"))
                .expect("the shared scalars catalog parses");
        let f = catalog.fits;
        Fits {
            slip: f.slip,
            running: f.slip + f.sliding_extra,
            supported_surface: f.supported_surface,
            m5_thread_pass_dia: f.m5_thread_pass_dia,
        }
    })
}

/// A catalog colour, as the catalog writes it: eight-bit sRGB, sRGB channels with an optional
/// alpha, or an sRGB hex string.
#[derive(Deserialize)]
#[serde(untagged)]
enum Swatch {
    Bytes { bytes: [u8; 3] },
    Channels { args: Vec<f64> },
    Hex { args: (String,) },
}

impl Swatch {
    /// The colour's sRGB channels, and its alpha where the stock is see-through.
    fn srgb(&self) -> ([f64; 3], f64) {
        match self {
            Swatch::Bytes { bytes } => (bytes.map(|b| f64::from(b) / 255.), 1.),
            Swatch::Channels { args } => ([args[0], args[1], args[2]], args.get(3).copied().unwrap_or(1.)),
            Swatch::Hex { args: (hex,) } => {
                let hex = hex.trim_start_matches('#');
                let byte = |i: usize| {
                    f64::from(u8::from_str_radix(&hex[i..i + 2], 16).expect("a catalog hex colour")) / 255.
                };
                ([byte(0), byte(2), byte(4)], 1.)
            }
        }
    }
}

/// The catalog materials the cold core is made of.
#[derive(Deserialize)]
#[allow(non_snake_case)]
struct Colors {
    M_PETG_BLACK: Swatch,
    M_PETGF_BLACK: Swatch,
    M_PETG_TRANSLUCENT: Swatch,
    M_SILICONE_CLEAR: Swatch,
    M_TPU_BLACK: Swatch,
    M_ASA_AERO_WHITE: Swatch,
    M_STAINLESS: Swatch,
    M_COPPER: Swatch,
    M_BRASS: Swatch,
    M_GLASS: Swatch,
    M_EPOXY_BLACK: Swatch,
    M_JG_BLACK_PP: Swatch,
    M_NEOFIT_ACETAL: Swatch,
    M_DONOR_BLACK: Swatch,
}

#[derive(Deserialize)]
struct Materials {
    colors: Colors,
}

fn colors() -> &'static Colors {
    static MATERIALS: OnceLock<Materials> = OnceLock::new();
    &MATERIALS
        .get_or_init(|| {
            serde_json::from_str(include_str!("../../../../tools/hsm/shared-data/catalog/materials.json"))
                .expect("the shared materials catalog parses")
        })
        .colors
}

fn curve(v: f64) -> f64 {
    if v <= 0.04045 { v / 12.92 } else { ((v + 0.055) / 1.055).powf(2.4) }
}

/// A material's colour as the viewer's files carry it: linear RGB at single precision, and the
/// alpha a see-through stock draws at.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Colour {
    pub linear: [f64; 3],
    pub alpha: f64,
}

fn colour(swatch: &Swatch) -> Colour {
    let (srgb, alpha) = swatch.srgb();
    Colour { linear: srgb.map(|c| curve(c) as f32 as f64), alpha }
}

/// Black PETG: the shroud, the mandrel, the reed bridge and the printed plugs.
pub fn petg_black() -> Colour {
    colour(&colors().M_PETG_BLACK)
}

/// Black glass-filled PETG: the foam shell and its caps.
pub fn petgf_black() -> Colour {
    colour(&colors().M_PETGF_BLACK)
}

/// PETG Translucent Clear: the reservoirs and their caps.
pub fn petg_translucent() -> Colour {
    colour(&colors().M_PETG_TRANSLUCENT)
}

/// Clear silicone: the reservoirs' gaskets.
pub fn silicone_clear() -> Colour {
    colour(&colors().M_SILICONE_CLEAR)
}

/// Black TPU: the tube grips.
pub fn tpu_black() -> Colour {
    colour(&colors().M_TPU_BLACK)
}

/// White ASA Aero: the floats.
pub fn asa_aero_white() -> Colour {
    colour(&colors().M_ASA_AERO_WHITE)
}

/// 316 stainless: the carbonator, its fittings and the float rods.
pub fn stainless() -> Colour {
    colour(&colors().M_STAINLESS)
}

/// Copper: the evaporator coil.
pub fn copper() -> Colour {
    colour(&colors().M_COPPER)
}

/// Brass fittings.
pub fn brass() -> Colour {
    colour(&colors().M_BRASS)
}

/// The reed switches' glass.
pub fn glass() -> Colour {
    colour(&colors().M_GLASS)
}

/// Black epoxy.
pub fn epoxy_black() -> Colour {
    colour(&colors().M_EPOXY_BLACK)
}

/// John Guest's black polypropylene.
pub fn jg_black_pp() -> Colour {
    colour(&colors().M_JG_BLACK_PP)
}

/// NeoFit's black acetal.
pub fn neofit_acetal() -> Colour {
    colour(&colors().M_NEOFIT_ACETAL)
}

/// The black of a donor part's moulding.
pub fn donor_black() -> Colour {
    colour(&colors().M_DONOR_BLACK)
}
