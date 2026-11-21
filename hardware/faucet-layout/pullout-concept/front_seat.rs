//! Turns the wet end of the balanced valve around a flat, captive seat washer.
use anyhow::Result;
use hsm_kernel::{Plane, Profile, Solid, V3, v2, v3};
use std::f64::consts::PI;

pub const OUTLET_S: f64 = -1.0;
pub const SEAT_S: f64 = 0.8;
pub const SEAT_D: f64 = 4.08;
pub const STEM_R: f64 = 0.8;
pub const VENT_R: f64 = 0.30;
pub const BORE_R: f64 = 1.90;
pub const THROAT_R: f64 = 1.80;
pub const KEEPER_BORE_R: f64 = 2.68;
pub const POPPET_R: f64 = 2.15;
pub const PRESSURE_SLEEVE_R: f64 = 4.3;
pub const PRESSURE_SLEEVE_BORE_R: f64 = 3.7;
pub const CAP_R: f64 = 5.22;
pub const LINER_START_S: f64 = 3.0;
pub const SLEEVE_BORE_START_S: f64 = 2.90;
pub const SHEET_T: f64 = 25.4 / 32.0;
pub const WASHER_R: f64 = 25.4 / 8.0;
pub const CLAMP_HEIGHT: f64 = 0.66;
pub const FLOOR_S: f64 = SEAT_S - SHEET_T;
pub const CLAMP_S: f64 = FLOOR_S + CLAMP_HEIGHT;
pub const THREAD_D: f64 = 8.0;
pub const THREAD_PITCH: f64 = 0.50;

const THREAD_R: f64 = (THREAD_D - 0.649519 * THREAD_PITCH) / 2.0;
const THREAD_START_S: f64 = 0.91;
const THREAD_END_S: f64 = 2.63;
const CAP_END_S: f64 = 2.76;
const SLEEVE_SHOULDER_S: f64 = 2.82;
const RIM_LOCATOR_R: f64 = WASHER_R + 0.04;
const RELIEF_S: f64 = FLOOR_S + 0.15;
pub const RELIEF_R: f64 = 3.40;
const EXPOSED_R: f64 = 2.28;
const TAPER_START_S: f64 = -0.46;
const TAPER_END_S: f64 = -0.24;
pub const LIP_HALF_WIDTH: f64 = 0.035;
const LIP_CREST_IN_R: f64 = SEAT_D / 2.0 - LIP_HALF_WIDTH;
const LIP_CREST_OUT_R: f64 = SEAT_D / 2.0 + LIP_HALF_WIDTH;
pub const CREST_DIAMETERS: [f64; 2] = [LIP_CREST_IN_R * 2., LIP_CREST_OUT_R * 2.];
const LIP_ROOT_IN_R: f64 = 1.88;
const RECESS_DEPTH: f64 = 0.12;
const RECESS_S: f64 = SEAT_S + RECESS_DEPTH;
const STEM_END_S: f64 = 36.1;
const BALANCE_PORT_S: f64 = 14.9;

fn cyl(radius: f64, start: f64, length: f64) -> Result<Solid> {
    Solid::cylinder(v3(0., start, 0.), V3::Y, radius, length)
}

fn turn(section: &[(f64, f64)]) -> Result<Solid> {
    let profile: Vec<_> = section.iter().map(|&(r, s)| v2(r, s)).collect();
    Plane::XY.revolve(&Profile::polygon(&profile), 360., v2(0., 0.), v2(0., 1.))
}

/// The mouth and its flat clamping face form one continuous pressure wall.
pub fn pressure_sleeve(length: f64) -> Result<Solid> {
    turn(&[
        (KEEPER_BORE_R, CLAMP_S), (THREAD_R - 0.06, CLAMP_S),
        (THREAD_R, THREAD_START_S), (THREAD_R, THREAD_END_S),
        (THREAD_R - 0.15, THREAD_END_S + 0.08),
        (THREAD_R - 0.15, SLEEVE_SHOULDER_S),
        (PRESSURE_SLEEVE_R, SLEEVE_SHOULDER_S), (PRESSURE_SLEEVE_R, length),
        (PRESSURE_SLEEVE_BORE_R, length), (PRESSURE_SLEEVE_BORE_R, SLEEVE_BORE_START_S),
        (KEEPER_BORE_R, SLEEVE_BORE_START_S),
    ])
}

/// The cap locates the washer at its floor and leaves room above the locating step for rubber displacement.
pub fn cap() -> Result<Solid> {
    let mut cap = turn(&[
        (BORE_R, OUTLET_S), (PRESSURE_SLEEVE_R, OUTLET_S),
        (PRESSURE_SLEEVE_R, -0.87), (CAP_R, -0.66), (CAP_R, CAP_END_S),
        (THREAD_D / 2.0 + 0.03, CAP_END_S), (THREAD_R, THREAD_END_S),
        (THREAD_R, CLAMP_S), (RELIEF_R, CLAMP_S),
        (RELIEF_R, RELIEF_S), (RIM_LOCATOR_R, RELIEF_S),
        (RIM_LOCATOR_R, FLOOR_S), (THROAT_R, FLOOR_S), (THROAT_R, TAPER_END_S),
        (BORE_R, TAPER_START_S),
    ])?;
    for x in [-3.55, 3.55] {
        let drive = Solid::cylinder(v3(x, OUTLET_S - 0.06, 0.), V3::Y, 0.46, 0.66)?;
        cap = cap.cut(&drive)?;
    }
    Ok(cap)
}

pub fn washer_blank() -> Result<Solid> {
    turn(&[(THROAT_R, FLOOR_S), (WASHER_R, FLOOR_S), (WASHER_R, SEAT_S), (THROAT_R, SEAT_S)])
}

/// A volume-preserving illustration of the squeezed rim, with the sealing band left at nominal height.
pub fn installed_washer() -> Result<Solid> {
    let flat = washer_blank()?;
    let section = |rim| turn(&[
        (THROAT_R, FLOOR_S), (WASHER_R, FLOOR_S),
        (WASHER_R, RELIEF_S), (rim, RELIEF_S), (rim, CLAMP_S),
        (KEEPER_BORE_R, CLAMP_S), (EXPOSED_R, SEAT_S), (THROAT_R, SEAT_S),
    ]);
    let unswelled = turn(&[
        (THROAT_R, FLOOR_S), (WASHER_R, FLOOR_S), (WASHER_R, CLAMP_S),
        (KEEPER_BORE_R, CLAMP_S), (EXPOSED_R, SEAT_S), (THROAT_R, SEAT_S),
    ])?;
    let rim_area = (flat.volume() - unswelled.volume()) / (CLAMP_S - RELIEF_S);
    section((WASHER_R.powi(2) + rim_area / PI).sqrt())
}

/// The poppet carries the metal sealing lip and connects the outlet to the balance chamber.
pub fn poppet() -> Result<Solid> {
    let rear_of_head = 1.53;
    let head = turn(&[
        (VENT_R, RECESS_S), (LIP_ROOT_IN_R, RECESS_S),
        (LIP_CREST_IN_R, SEAT_S), (LIP_CREST_OUT_R, SEAT_S),
        (POPPET_R, SEAT_S + 0.14), (POPPET_R, rear_of_head),
        (VENT_R, rear_of_head),
    ])?;
    let stem = cyl(STEM_R, rear_of_head - 0.02, STEM_END_S - rear_of_head + 0.02)?;
    head.union(&stem)?.union(&crate::balance::piston()?)?
        .cut(&cyl(VENT_R, RECESS_S - 0.03, BALANCE_PORT_S - RECESS_S + VENT_R + 0.03)?)?
        .cut(&Solid::cylinder(v3(-0.9, BALANCE_PORT_S, 0.), V3::X, VENT_R, 1.8)?)
}

pub fn balance_passage() -> Result<Solid> {
    let axial = cyl(VENT_R, RECESS_S, BALANCE_PORT_S + VENT_R - RECESS_S)?;
    let cross = Solid::cylinder(v3(-STEM_R, BALANCE_PORT_S, 0.), V3::X, VENT_R, 2.0 * STEM_R)?;
    axial.union(&cross)
}

pub fn outlet_volume() -> Result<Solid> {
    turn(&[
        (0., OUTLET_S), (BORE_R, OUTLET_S), (BORE_R, TAPER_START_S),
        (THROAT_R, TAPER_END_S), (THROAT_R, SEAT_S), (LIP_CREST_IN_R, SEAT_S),
        (LIP_ROOT_IN_R, RECESS_S), (0., RECESS_S),
    ])
}
