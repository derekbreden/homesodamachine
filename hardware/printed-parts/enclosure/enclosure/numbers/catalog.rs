//! The shared fits and material colours, from the catalogs every program reads.
pub use hsm_enclosure_interface::fits::{running, slip, supported};
use serde::Deserialize;
use std::sync::OnceLock;

#[derive(Deserialize)]
struct Fits {
    slip: f64,
    sliding_extra: f64,
    supported_surface: f64,
    layer_transition: f64,
    m5_thread_pass_dia: f64,
}

#[derive(Deserialize)]
struct Scalars {
    fits: Fits,
    overhang_round: OverhangRound,
    reeding: Reeding,
    flute_skin: FluteSkin,
    route_snap: RouteSnap,
}

#[derive(Deserialize)]
#[allow(non_snake_case)]
struct RouteSnap {
    TUBE_TIP_DEGREES: f64,
    ROOT_OVERLAP: f64,
}

#[derive(Deserialize)]
struct Reeding {
    flute_width: f64,
    pierce_width: f64,
}

/// The exterior field's sampling and cutting tolerances.
#[derive(Clone, Copy, Debug, Deserialize)]
pub struct FluteSkin {
    pub grid_across: f64,
    pub grid_along: f64,
    pub cut_margin: f64,
    pub cut_overrun: f64,
    pub plan_tol: f64,
    pub face_tol: f64,
}

#[derive(Deserialize)]
#[allow(non_snake_case)]
struct OverhangRound {
    OUTWARD_PER_HEIGHT: f64,
}

fn scalars() -> &'static Scalars {
    static SCALARS: OnceLock<Scalars> = OnceLock::new();
    SCALARS.get_or_init(|| {
        serde_json::from_str(include_str!("../../../../../tools/hsm/shared-data/catalog/scalars.json"))
            .expect("the shared scalars catalog parses")
    })
}


/// One mating face's allowance: motion, a supported overhang's finish and a cavity floor's turn.
pub fn clearance(sliding: bool, supported: bool, at_floor: bool) -> f64 {
    let f = &scalars().fits;
    f.slip
        + if sliding { f.sliding_extra } else { 0.0 }
        + if supported { f.supported_surface } else { 0.0 }
        + if at_floor { f.layer_transition } else { 0.0 }
}


pub fn m5_thread_pass_dia() -> f64 {
    scalars().fits.m5_thread_pass_dia
}

/// How far a print-down show round grows outward per millimetre of build rise.
pub fn outward_per_height() -> f64 {
    scalars().overhang_round.OUTWARD_PER_HEIGHT
}

/// A flute's width across the field.
pub fn flute_width() -> f64 {
    scalars().reeding.flute_width
}

/// A vent slot's width across its groove.
pub fn pierce_width() -> f64 {
    scalars().reeding.pierce_width
}

/// How far a route snap's root runs into the wall it grows from.
pub fn route_root_overlap() -> f64 {
    scalars().route_snap.ROOT_OVERLAP
}

/// The arc a tube seat's spring wings wrap round the tube, each side of its mouth.
pub fn route_tube_tip_degrees() -> f64 {
    scalars().route_snap.TUBE_TIP_DEGREES
}

pub fn flute_skin() -> FluteSkin {
    scalars().flute_skin
}

/// A catalog colour: its sRGB triple.
#[derive(Deserialize)]
struct Srgb {
    args: [f64; 3],
}

/// The catalog colours the enclosure step draws.
#[derive(Deserialize)]
#[allow(non_snake_case)]
struct Colors {
    M_PETGF_BLACK: Srgb,
    M_JG_BLACK_PP: Srgb,
    M_NEOFIT_WHITE_ACETAL: Srgb,
}

#[derive(Deserialize)]
struct Materials {
    colors: Colors,
}

fn colors() -> &'static Colors {
    static MATERIALS: OnceLock<Materials> = OnceLock::new();
    &MATERIALS
        .get_or_init(|| {
            serde_json::from_str(include_str!("../../../../../tools/hsm/shared-data/catalog/materials.json"))
                .expect("the shared materials catalog parses")
        })
        .colors
}

fn curve(v: f64) -> f64 {
    if v <= 0.04045 { v / 12.92 } else { ((v + 0.055) / 1.055).powf(2.4) }
}

/// A catalog colour as the payload carries it: linear RGB at single precision.
fn linear(color: &Srgb) -> [f64; 3] {
    color.args.map(|c| curve(c) as f32 as f64)
}

/// Every enclosure wall piece prints in glass-filled PET.
pub fn wall_color() -> [f64; 3] {
    linear(&colors().M_PETGF_BLACK)
}

/// The dock's John Guest tees: black polypropylene.
pub fn tee_color() -> [f64; 3] {
    linear(&colors().M_JG_BLACK_PP)
}

/// The returns' NeoFit stem elbows: white acetal.
pub fn elbow_color() -> [f64; 3] {
    linear(&colors().M_NEOFIT_WHITE_ACETAL)
}

/// A colour rounded to the decimal places the jig and the enclosure model carry.
pub fn digits(color: [f64; 3]) -> [f64; 3] {
    color.map(|c| format!("{c:.9}").parse().expect("a formatted number parses"))
}
