//! The removable V-G tube clip and the blind snap pocket in the dry underside of the funnel frame.
use anyhow::Result;
use hsm_kernel::{Plane, Profile, Solid, v2, v3};
use hsm_layout_data::{bezier_at, rear::flavor_a_rise};
use hsm_zone_c_numbers::frame::{CENTER_Y, Frame, SEAT};

pub const NAME: &str = "funnel-dispense-clip";
const HALF_LENGTH: f64 = 3.2;
const OUTSIDE: f64 = 4.65;
const LEAF: f64 = 1.50;
const BOSS: f64 = 5.50;
const HOOK_START: f64 = 1.75;
const CREST_LAND: f64 = 1.40;
const TOP: f64 = 12.2;
const ROOF_LAND: f64 = 1.8;
const RUNNING: f64 = 0.25;

pub struct Station {
    pub frame_xy: [f64; 2],
    tube_fore: f64,
    tube_aft: f64,
}

impl Station {
    pub fn new(frame: &Frame) -> Self {
        let rise = flavor_a_rise();
        let t = 0.60;
        let half = HALF_LENGTH / (rise[5][1] - rise[0][1]);
        let [x, y, _] = bezier_at(&rise, t);
        let floor = SEAT - frame.seat;
        Self {
            frame_xy: [x, y - CENTER_Y],
            tube_fore: bezier_at(&rise, t - half)[2] - floor,
            tube_aft: bezier_at(&rise, t + half)[2] - floor,
        }
    }
}

/// An XZ half-outline from the centre out and back, reflected across the tube lane.
fn symmetric_band(half: &[(f64, f64)], length: f64) -> Result<Solid> {
    let mut points: Vec<_> = half.iter().map(|&(x, z)| v2(x, z)).collect();
    points.extend(half[1..half.len() - 1].iter().rev().map(|&(x, z)| v2(-x, z)));
    Plane::XZ.at(v3(0., length / 2., 0.)).extrude(&Profile::polygon(&points), length)
}

/// The two 45-degree roof planes run across the short dimension of the socket.
fn under_roof(apex: f64) -> Result<Solid> {
    let span = HALF_LENGTH + RUNNING + 1.;
    let yz = [v2(-span, -20.), v2(span, -20.), v2(span, apex - span),
              v2(0., apex), v2(-span, apex - span)];
    Plane::YZ.at(v3(-8., 0., 0.)).extrude(&Profile::polygon(&yz), 16.)
}

pub fn receiver(station: &Station) -> Result<Solid> {
    let throat = OUTSIDE + RUNNING;
    let pocket = BOSS + RUNNING;
    let mouth = 0.60;
    let catch = HOOK_START + (throat - OUTSIDE) - 0.10;
    let upper = HOOK_START + (BOSS - OUTSIDE) + CREST_LAND + RUNNING;
    let apex = TOP + ROOF_LAND + 0.10;
    let cutter = symmetric_band(&[
        (0., -1.), (throat + mouth, -1.), (throat + mouth, 0.), (throat, mouth),
        (throat, catch), (pocket, catch + pocket - throat), (pocket, upper),
        (throat, upper + pocket - throat), (throat, apex + 1.), (0., apex + 1.),
    ], 2. * (HALF_LENGTH + RUNNING))?.intersect(&under_roof(apex)?)?;
    let [x, y] = station.frame_xy;
    Ok(cutter.translate(v3(x, y, 0.)))
}

pub fn keeper(station: &Station) -> Result<Solid> {
    let inside = OUTSIDE - LEAF;
    let crest = HOOK_START + BOSS - OUTSIDE;
    let root = TOP - 2.;
    let side = 2.10;
    let throat = 1.60;
    let diagonal = 3.00;
    let tongue = 1.55;
    let mouth = 3.00;
    let lip_land = 1.20;
    let fore = station.tube_fore;
    let aft = station.tube_aft;
    let lip = fore + throat - diagonal;
    let end = lip - lip_land - (mouth - throat);
    let bearing = aft + 2.18;
    let body = symmetric_band(&[
        (0., TOP), (OUTSIDE, TOP), (OUTSIDE, crest + CREST_LAND + BOSS - OUTSIDE),
        (BOSS, crest + CREST_LAND), (BOSS, crest), (OUTSIDE, HOOK_START),
        (OUTSIDE, end + 0.50), (OUTSIDE - 0.50, end), (mouth, end),
        (throat, lip - lip_land), (throat, lip), (side, fore + side - diagonal),
        (side, aft + 1.), (inside, aft + 1. + inside - side),
        (inside, root - 0.60), (inside - 0.60, root), (tongue, root),
        (tongue, bearing + 0.60), (tongue - 0.60, bearing), (0., bearing),
    ], 2. * HALF_LENGTH)?;
    body.intersect(&under_roof(TOP + ROOF_LAND)?)
}
