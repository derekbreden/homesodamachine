//! The swept exterior's section, which every quadrant is trimmed to and the drawings of the
//! machine show: the front round, the display plane and the round onto the roof.
use serde::{Deserialize, Serialize};

/// The show edges' round.
pub const SHOW_EDGE_R: f64 = 6.0;
/// The display plane's tilt from level.
pub const ANGLE: f64 = 30.0;
/// The display plane's flat run, and the rounds at its foot, onto the roof and along its sides.
pub const FLAT: f64 = 87.0;
pub const FRONT_RADIUS: f64 = 2.0 * SHOW_EDGE_R;
pub const TOP_RADIUS: f64 = 3.0 * SHOW_EDGE_R;
pub const SIDE_RADIUS: f64 = SHOW_EDGE_R;

/// YZ stations of the front round, the display plane and the round onto the roof.
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Profile {
    pub foot: [f64; 2],
    pub front_mid: [f64; 2],
    pub start: [f64; 2],
    pub end: [f64; 2],
    pub top_mid: [f64; 2],
    pub roof: [f64; 2],
    pub origin: [f64; 3],
    pub normal: [f64; 3],
}

/// The section at `outer`, an axis-aligned box given as its X, Y and Z spans, each low then high.
pub fn profile(outer: &[f64; 6]) -> Profile {
    let (yf, zt) = (outer[2], outer[5]);
    let a = ANGLE.to_radians();
    let (rb, rt) = (FRONT_RADIUS, TOP_RADIUS);
    let zb = zt - rb * a.cos() - FLAT * a.sin() - rt * (1.0 - a.cos());
    let start = [yf + rb * (1.0 - a.sin()), zb + rb * a.cos()];
    let end = [start[0] + FLAT * a.cos(), start[1] + FLAT * a.sin()];
    let roof = [end[0] + rt * a.sin(), zt];
    let amid = (180.0 - (90.0 - ANGLE) / 2.0).to_radians();
    Profile {
        foot: [yf, zb],
        front_mid: [yf + rb + rb * amid.cos(), zb + rb * amid.sin()],
        start,
        end,
        top_mid: [roof[0] - rt * (a / 2.0).sin(), zt - rt + rt * (a / 2.0).cos()],
        roof,
        origin: [0.0, (start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0],
        normal: [0.0, -a.sin(), a.cos()],
    }
}
