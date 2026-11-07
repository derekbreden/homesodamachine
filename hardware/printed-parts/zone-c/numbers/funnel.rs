//! The cast silicone funnel, in its own frame: the collar's centre at the origin, Z = 0 the
//! brim's frame-bearing underside. The collar and ramp lead down to a square-cornered plug whose
//! flat underside bears on the cradle's hook tops, and a straight bore grips the elbow's stem.
use crate::{P2, cradle};

/// The collar's plan, and how far it reaches forward and aft of its seat.
pub const COLLAR_W: f64 = 165.0;
pub const FORWARD: f64 = 41.6085;
pub const AFT: f64 = 35.0;
pub const COLLAR_D: f64 = 81.78301584656256 + FORWARD + AFT;
/// The mouth's corners, the collar's and the brim's.
pub const MOUTH_R: f64 = 14.0;
pub const COLLAR_R: f64 = MOUTH_R + 6.0;
pub const BRIM_R: f64 = COLLAR_R + 7.0;
/// How far the brim reaches past the collar, and its thickness.
pub const OVERHANG: f64 = 7.0;
pub const BRIM_T: f64 = 6.0;
/// The roof apron over the brim.
pub const APRON_RISE: f64 = 3.0;
pub const APRON_W: f64 = 215.0;
pub const APRON_D: f64 = COLLAR_D + 32.0;
pub const APRON_Y: f64 = 3.0;
pub const APRON_R: f64 = 6.0;
pub const COLLAR_WALL: f64 = 6.0;
/// The chute down to the ramp, and the ramp's fall to the spout.
pub const CHUTE: f64 = 23.485946291005064;
pub const RAMP_RISE: f64 = 14.199233063709995;
/// The spout's bore, which grips the elbow's stem, and its wall.
pub const SPOUT_ID: f64 = 6.0;
pub const SPOUT_WALL: f64 = 4.5;
/// The plug under the spout: its width, how far it stands off the cradle, and its height.
pub const PLUG_W: f64 = 36.0;
pub const PLUG_LIFT: f64 = 3.15;
pub const PLUG_H: f64 = 16.0 - PLUG_LIFT;
/// How far the spout drops below the brim.
pub const DROP: f64 = 46.1;
pub const SPOUT_LAND: f64 = BRIM_T - CHUTE - RAMP_RISE;
/// How much of the stem the bore grips.
pub const STEM_ENGAGEMENT: f64 = SPOUT_LAND + DROP - PLUG_LIFT;

/// The plug's half length along Y for a half width `half`: the cradle socket's, less the side
/// clearance the socket leaves it.
pub fn plug_half_length(half: f64) -> f64 {
    cradle::socket_half_length() - (cradle::SOCKET_HALF - half)
}

/// The funnel's dimensions, as its geometry draws them.
#[derive(Clone, Debug)]
pub struct Dimensions {
    pub bore_size: P2,
    pub mouth_radius: f64,
    pub ramp_z: P2,
    pub bore_radius: f64,
    pub drain_xy: P2,
    pub collar_wall: f64,
    pub end_z: f64,
    pub top_z: f64,
    pub spout_radius: f64,
    pub brim_size: P2,
    pub brim_radius: f64,
    pub brim_height: f64,
    pub apron_size: P2,
    pub apron_z: P2,
    pub apron_radius: f64,
    pub apron_y: f64,
    pub plug_size: P2,
    pub plug_height: f64,
}

/// The funnel as cast.
pub fn dimensions() -> Dimensions {
    Dimensions {
        bore_size: (COLLAR_W - 2.0 * COLLAR_WALL, COLLAR_D - 2.0 * COLLAR_WALL),
        mouth_radius: MOUTH_R,
        ramp_z: (BRIM_T - CHUTE, SPOUT_LAND),
        bore_radius: SPOUT_ID / 2.0,
        drain_xy: (0.0, 0.0),
        collar_wall: COLLAR_WALL,
        end_z: -DROP + PLUG_LIFT,
        top_z: BRIM_T + APRON_RISE,
        spout_radius: SPOUT_ID / 2.0 + SPOUT_WALL,
        brim_size: (COLLAR_W + 2.0 * OVERHANG, COLLAR_D + 2.0 * OVERHANG),
        brim_radius: BRIM_R,
        brim_height: BRIM_T,
        apron_size: (APRON_W, APRON_D),
        apron_z: (BRIM_T, BRIM_T + APRON_RISE),
        apron_radius: APRON_R,
        apron_y: APRON_Y,
        plug_size: (PLUG_W, 2.0 * plug_half_length(PLUG_W / 2.0)),
        plug_height: PLUG_H,
    }
}
