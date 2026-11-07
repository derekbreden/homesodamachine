//! The soda bend holder's numbers, in millimetres: the PET-GF holder that carries the continuous
//! soda tube round its quarter turn into the core-mounted flow meter, a teardrop channel through
//! a D-backed section swept round the bend, with a straight leg at each end. Print frame: the
//! flat back on the bed at Z = 0, the bend about the Z axis.
//!
//! The inlet plan writes the holder's design down in `hardware/manifold-layout/above-core.json`
//! (`soda_inlet.holder`); this crate states what the holder makes of it.
use serde::Deserialize;

/// The inlet plan's holder, as `above-core.json` writes it.
#[derive(Clone, Copy, Debug, Deserialize)]
pub struct Holder {
    /// The least wall round the channel.
    pub wall_mm: f64,
    /// Each straight leg past the bend.
    pub leg_mm: f64,
    /// The channel's round, the tube with its clearance.
    pub channel_d_mm: f64,
    /// The tube's bend radius at its centreline.
    pub centreline_bend_r_mm: f64,
    /// The bend's turn.
    pub turn_degrees: f64,
}

/// Each mouth's flare: two teardrop sections lofted, at these stations along the leg, opened past
/// the channel by the first flare and closed inside it by the second.
pub const MOUTH_STATIONS: [f64; 2] = [-0.3, 0.55];
pub const MOUTH_FLARE: [f64; 2] = [0.8, -0.05];

impl Holder {
    /// The channel's radius.
    pub fn channel_radius(&self) -> f64 {
        self.channel_d_mm / 2.
    }

    /// The section's outside radius: the channel and its wall.
    pub fn outer_radius(&self) -> f64 {
        self.channel_radius() + self.wall_mm
    }

    /// The channel's centre above the flat back: one wall under it.
    pub fn channel_z(&self) -> f64 {
        self.wall_mm + self.channel_radius()
    }

    /// Where the section's straight sides meet its round crown, above the back: level with the
    /// teardrop's flanks.
    pub fn stock_arc_z(&self) -> f64 {
        self.channel_z() + (2f64.sqrt() - 1.) * self.channel_radius()
    }

    /// The normal of the plane the bend is mirrored across, at half its turn.
    pub fn mirror_normal(&self) -> [f64; 3] {
        let half = (self.turn_degrees / 2.).to_radians();
        [half.sin(), -half.cos(), 0.]
    }

    /// Each mouth's teardrop radii, at `MOUTH_STATIONS`.
    pub fn mouth_radii(&self) -> [f64; 2] {
        MOUTH_FLARE.map(|flare| self.channel_radius() + flare)
    }
}
