//! Defines the pressure boundaries around the turned balance piston and dry rod.
use anyhow::Result;
use hsm_kernel::{Plane, Profile, Solid, V3, v2, v3};

use crate::front_seat::STEM_R;

pub const BORE_R: f64 = 2.0;
pub const PISTON_S: f64 = 12.0;
pub const PISTON_END_S: f64 = 14.2;
pub const PISTON_R: f64 = 1.97;
pub const PISTON_GROOVE_R: f64 = 1.57;
pub const PISTON_GROOVE_WIDTH: f64 = 0.68;
pub const PISTON_SEAL_S: f64 = PISTON_GROOVE_S + PISTON_GROOVE_WIDTH / 2.;
pub const PISTON_RING_ID: f64 = 3.0;
pub const PISTON_RING_SECTION: f64 = 0.50;
pub const LOW_CHAMBER_END_S: f64 = 16.05;
pub const ROD_GUIDE_R: f64 = 0.875;
pub const ROD_GROOVE_R: f64 = 1.67;
pub const ROD_GROOVE_S: f64 = 16.30;
pub const ROD_GROOVE_WIDTH: f64 = 1.27;
pub const ROD_RING_ID: f64 = 1.50;
pub const ROD_RING_SECTION: f64 = 1.00;
pub const DRY_BORE_S: f64 = 17.70;

const LEAD_IN_S: f64 = PISTON_S - 0.24;
const LEAD_IN_R: f64 = 2.16;
const PISTON_GROOVE_S: f64 = 12.78;

fn cyl(r: f64, s: f64, length: f64) -> Result<Solid> {
    Solid::cylinder(v3(0., s, 0.), V3::Y, r, length)
}

fn turn(section: &[(f64, f64)]) -> Result<Solid> {
    let points: Vec<_> = section.iter().map(|&(r, s)| v2(r, s)).collect();
    Plane::XY.revolve(&Profile::polygon(&points), 360., v2(0., 0.), v2(0., 1.))
}

pub fn piston() -> Result<Solid> {
    let groove_end = PISTON_GROOVE_S + PISTON_GROOVE_WIDTH;
    turn(&[
        (STEM_R - 0.03, PISTON_S), (PISTON_R - 0.08, PISTON_S),
        (PISTON_R, PISTON_S + 0.10), (PISTON_R, PISTON_GROOVE_S),
        (PISTON_GROOVE_R, PISTON_GROOVE_S), (PISTON_GROOVE_R, groove_end),
        (PISTON_R, groove_end), (PISTON_R, PISTON_END_S - 0.08),
        (PISTON_R - 0.08, PISTON_END_S), (STEM_R - 0.03, PISTON_END_S),
    ])
}

pub fn liner_bore(liner_start: f64, liner_end: f64) -> Result<Solid> {
    let shoulder = LEAD_IN_S - 0.035;
    turn(&[
        (0., liner_start - 0.1), (2.5, liner_start - 0.1), (2.5, shoulder),
        (LEAD_IN_R, shoulder), (LEAD_IN_R, LEAD_IN_S), (BORE_R, PISTON_S),
        (BORE_R, LOW_CHAMBER_END_S), (ROD_GUIDE_R, LOW_CHAMBER_END_S),
        (ROD_GUIDE_R, ROD_GROOVE_S), (ROD_GROOVE_R, ROD_GROOVE_S),
        (ROD_GROOVE_R, ROD_GROOVE_S + ROD_GROOVE_WIDTH),
        (ROD_GUIDE_R, ROD_GROOVE_S + ROD_GROOVE_WIDTH),
        (ROD_GUIDE_R, DRY_BORE_S), (2.6, DRY_BORE_S), (2.6, liner_end + 0.1),
        (0., liner_end + 0.1),
    ])
}

/// Revolves a volume-equivalent section between the gland root and its mating surface.
fn compressed_ring(id: f64, section: f64, inner: f64, outer: f64, station: f64) -> Result<Solid> {
    let radial = (outer - inner) / 2.;
    let major = (outer + inner) / 2.;
    let axial = (id + section) / 2. * (section / 2.).powi(2) / (radial * major);
    let points: Vec<_> = (0..48).map(|i| {
        let theta = std::f64::consts::TAU * i as f64 / 48.;
        (major + radial * theta.cos(), station + axial * theta.sin())
    }).collect();
    turn(&points)
}

pub fn piston_seal() -> Result<Solid> {
    compressed_ring(PISTON_RING_ID, PISTON_RING_SECTION, PISTON_GROOVE_R, BORE_R, PISTON_SEAL_S)
}

pub fn rod_seal() -> Result<Solid> {
    compressed_ring(ROD_RING_ID, ROD_RING_SECTION, STEM_R, ROD_GROOVE_R,
        ROD_GROOVE_S + ROD_GROOVE_WIDTH / 2.)
}

pub fn relief_water(lift: f64, poppet: &Solid, seal: &Solid) -> Result<Solid> {
    let start = PISTON_SEAL_S + lift;
    cyl(BORE_R, start, LOW_CHAMBER_END_S - start)?.cut(poppet)?.cut(seal)
}
