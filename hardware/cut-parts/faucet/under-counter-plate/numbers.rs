//! The under-counter plate's numbers, in millimetres, in its DXF's own frame: X is world depth and
//! Y world lateral, so the faucet assembly turns the outline a quarter about Z. A 316 stainless
//! disc, laser cut, that clamps the countertop from below: the Westbrass shank's pocket and the
//! flavor pill's pocket, each opened by a straight channel to the rim, the four wall-meets-rim
//! corners rounded.
use hsm_faucet_numbers::interface::{PILL_LENGTH_X, PILL_WIDTH_Y, SHANK_HOLE_DIAMETER};
use hsm_faucet_numbers::paths::LOWER_Y;

pub type P2 = [f64; 2];

/// The sheet: 0.060" 316 stainless.
pub const THICKNESS: f64 = 0.060 * 25.4;
/// The shank's pocket.
pub const SHANK_CX: f64 = 0.0;
pub const SHANK_CY: f64 = 0.0;
pub const SHANK_DIAMETER: f64 = SHANK_HOLE_DIAMETER;
pub const SHANK_RADIUS: f64 = SHANK_DIAMETER / 2.0;
/// The flavor pill's pocket, over the flavor pair, long along Y.
pub const PILL_CX: f64 = LOWER_Y;
pub const PILL_CY: f64 = 0.0;
pub const PILL_LONG_Y: f64 = PILL_LENGTH_X;
pub const PILL_SHORT_X: f64 = PILL_WIDTH_Y;
pub const PILL_HALF_LONG: f64 = PILL_LONG_Y / 2.0;
pub const PILL_HALF_SHORT: f64 = PILL_SHORT_X / 2.0;
pub const PILL_CAP_RADIUS: f64 = PILL_HALF_SHORT;
pub const PILL_TOP_CAP_CY: f64 = PILL_CY + (PILL_HALF_LONG - PILL_CAP_RADIUS);
pub const PILL_BOT_CAP_CY: f64 = PILL_CY - (PILL_HALF_LONG - PILL_CAP_RADIUS);
pub const PILL_LEFT_X: f64 = PILL_CX - PILL_HALF_SHORT;
pub const PILL_RIGHT_X: f64 = PILL_CX + PILL_HALF_SHORT;
/// The Westbrass's front bore, which the disc reaches past.
pub const BORE_FRONT_X: f64 = -16.0;
/// How far the disc reaches past the bore's front and the pill's far wall.
pub const DISC_REACH_MARGIN: f64 = 8.0;
pub const DISC_CX: f64 = (PILL_RIGHT_X + BORE_FRONT_X) / 2.0;
pub const DISC_CY: f64 = 0.0;
pub const DISC_RADIUS: f64 = (PILL_RIGHT_X - BORE_FRONT_X) / 2.0 + DISC_REACH_MARGIN;
pub const DISC_DIAMETER: f64 = 2.0 * DISC_RADIUS;
/// The rounding where a channel wall meets the rim.
pub const FILLET_RADIUS: f64 = 1.5;

/// The rim's lower Y at `x`.
pub fn rim_y_lower(x: f64) -> Option<f64> {
    let squared = DISC_RADIUS.powi(2) - (x - DISC_CX).powi(2);
    (squared >= 0.0).then(|| DISC_CY - squared.sqrt())
}

/// The fillet of radius `r` where the channel wall at `wall_x` meets the rim, on the material's
/// side (`-1` or `1`): its centre, its tangent on the wall and its tangent on the rim.
pub fn corner(wall_x: f64, material_side: f64, r: f64) -> Option<[P2; 3]> {
    let x_c = wall_x + material_side * r;
    let dx = x_c - DISC_CX;
    let inner_r = DISC_RADIUS - r;
    let squared = inner_r * inner_r - dx * dx;
    if squared < 0.0 || inner_r == 0.0 {
        return None;
    }
    let y_c = DISC_CY - squared.sqrt();
    let (ux, uy) = ((x_c - DISC_CX) / inner_r, (y_c - DISC_CY) / inner_r);
    Some([[x_c, y_c], [wall_x, y_c], [DISC_CX + DISC_RADIUS * ux, DISC_CY + DISC_RADIUS * uy]])
}

/// One edge of the outline: a line, or a circular arc about a centre at a radius, anticlockwise
/// from one angle to another in degrees.
#[derive(Clone, Copy, Debug)]
pub enum Edge {
    Line(P2, P2),
    Arc(P2, f64, f64, f64),
}

impl Edge {
    /// The arc about `center` anticlockwise from `start` to `end`.
    pub fn ccw_arc(center: P2, radius: f64, start: P2, end: P2) -> Self {
        let deg = 180.0 / std::f64::consts::PI;
        let start_angle = (start[1] - center[1]).atan2(start[0] - center[0]) * deg;
        let mut end_angle = (end[1] - center[1]).atan2(end[0] - center[0]) * deg;
        if end_angle <= start_angle {
            end_angle += 360.0;
        }
        Self::Arc(center, radius, start_angle, end_angle)
    }
}

/// The outline, anticlockwise from the top of the disc: the rim round to the shank's channel, the
/// channel and the pocket's half round, the rim on to the pill's channel, its channel and cap, and
/// the rim back to the top.
pub fn outline() -> Vec<Edge> {
    let top = [DISC_CX, DISC_CY + DISC_RADIUS];
    let (shank_left, shank_right) = (SHANK_CX - SHANK_RADIUS, SHANK_CX + SHANK_RADIUS);
    let disc = [DISC_CX, DISC_CY];
    let fillet = |wall: f64, side: f64| corner(wall, side, FILLET_RADIUS).expect("each channel meets the rim");
    let [sl_c, sl_wt, sl_rt] = fillet(shank_left, -1.0);
    let [sr_c, sr_wt, sr_rt] = fillet(shank_right, 1.0);
    let [pl_c, pl_wt, pl_rt] = fillet(PILL_LEFT_X, -1.0);
    let [pr_c, pr_wt, pr_rt] = fillet(PILL_RIGHT_X, 1.0);
    vec![
        Edge::ccw_arc(disc, DISC_RADIUS, top, sl_rt),
        Edge::ccw_arc(sl_c, FILLET_RADIUS, sl_rt, sl_wt),
        Edge::Line(sl_wt, [shank_left, SHANK_CY]),
        Edge::Arc([SHANK_CX, SHANK_CY], SHANK_RADIUS, 0.0, 180.0),
        Edge::Line([shank_right, SHANK_CY], sr_wt),
        Edge::ccw_arc(sr_c, FILLET_RADIUS, sr_wt, sr_rt),
        Edge::ccw_arc(disc, DISC_RADIUS, sr_rt, pl_rt),
        Edge::ccw_arc(pl_c, FILLET_RADIUS, pl_rt, pl_wt),
        Edge::Line(pl_wt, [PILL_LEFT_X, PILL_TOP_CAP_CY]),
        Edge::Arc([PILL_CX, PILL_TOP_CAP_CY], PILL_CAP_RADIUS, 0.0, 180.0),
        Edge::Line([PILL_RIGHT_X, PILL_TOP_CAP_CY], pr_wt),
        Edge::ccw_arc(pr_c, FILLET_RADIUS, pr_wt, pr_rt),
        Edge::ccw_arc(disc, DISC_RADIUS, pr_rt, top),
    ]
}
