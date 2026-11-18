//! Integral rear alignment keys enter corbelled receivers at the end of the upper half's slide.
use crate::plan::{Bounds, Graph, Shape};
use crate::shapes::corner_prism;

pub const KEY_ROOT_Z: f64 = 171.8;
pub const KEY_TOP_Z: f64 = 183.0;
pub const KEY_HEIGHT_Z: f64 = KEY_TOP_Z - KEY_ROOT_Z;
pub const BASE_Y_TO_HEIGHT_Z_RATIO: f64 = 1.5;
pub const KEY_LENGTH_Y: f64 = BASE_Y_TO_HEIGHT_Z_RATIO * KEY_HEIGHT_Z;
pub const KEY_FORE_Y: f64 = 230.0;
pub const KEY_AFT_Y: f64 = KEY_FORE_Y + KEY_LENGTH_Y;
pub const KEY_X: [f64; 2] = [94.5, 97.5];
pub const KEY_NORTH_RADIUS: f64 = 1.0;
pub const SIDE_AIR: f64 = 0.25;
pub const END_AIR: f64 = 0.25;
pub const ROOF_AIR: f64 = 0.3;
pub const SLOT_X: [f64; 2] = [KEY_X[0] - SIDE_AIR, KEY_X[1] + SIDE_AIR];
pub const SLOT_MOUTH_X: [f64; 2] = [93.5, 98.5];
pub const RECEIVER_FORE_Y: f64 = 224.0;
pub const SLOT_FLARE_END_Y: f64 = 227.0;
pub const SLOT_END_Y: f64 = KEY_AFT_Y + END_AIR;
pub const SLOT_ROOF_Z: f64 = KEY_TOP_Z + ROOF_AIR;
pub const SLOT_NORTH_RADIUS: f64 = KEY_NORTH_RADIUS + SIDE_AIR;
pub const RECEIVER_BACK_WALL: f64 = 3.0;
pub const RECEIVER_AFT_Y: f64 = SLOT_END_Y + RECEIVER_BACK_WALL;
pub const RECEIVER_BOTTOM_Z: f64 = 175.3;
pub const RECEIVER_X: [f64; 2] = [90.5, 98.52];
pub const RECEIVER_RAMP_Z: [f64; 2] = [186.3, 194.32];

fn mirrored_bounds(mut bounds: Bounds, sign: f64) -> Bounds {
    if sign < 0.0 {
        (bounds[0], bounds[1]) = (-bounds[1], -bounds[0]);
    }
    bounds
}

/// The complete lower key, including the stock embedded in the rail head.
pub fn key_bounds(sign: f64) -> Bounds {
    mirrored_bounds([KEY_X[0], KEY_X[1], KEY_FORE_Y, KEY_AFT_Y, KEY_ROOT_Z, KEY_TOP_Z], sign)
}

/// The receiver's continuous outer stock, including its wall overlap.
pub fn receiver_bounds(sign: f64) -> Bounds {
    mirrored_bounds([RECEIVER_X[0], RECEIVER_X[1], RECEIVER_FORE_Y, RECEIVER_AFT_Y,
        RECEIVER_BOTTOM_Z, RECEIVER_RAMP_Z[1]], sign)
}

/// The groove's void within the receiver; its lower opening stays above the rail supports.
pub fn groove_bounds(sign: f64) -> Bounds {
    mirrored_bounds([SLOT_MOUTH_X[0], SLOT_MOUTH_X[1], RECEIVER_FORE_Y, SLOT_END_Y,
        RECEIVER_BOTTOM_Z, SLOT_ROOF_Z], sign)
}

fn east_key(g: &mut Graph) -> Shape {
    corner_prism(g, 2, KEY_ROOT_Z, KEY_TOP_Z,
        vec![[KEY_X[0], KEY_FORE_Y], [KEY_X[1], KEY_FORE_Y],
             [KEY_X[1], KEY_AFT_Y], [KEY_X[0], KEY_AFT_Y]],
        KEY_NORTH_RADIUS, &[2, 3])
}

fn east_receiver(g: &mut Graph) -> Shape {
    g.xz_prism(RECEIVER_FORE_Y, RECEIVER_AFT_Y,
        vec![[RECEIVER_X[0], RECEIVER_BOTTOM_Z], [RECEIVER_X[1], RECEIVER_BOTTOM_Z],
             [RECEIVER_X[1], RECEIVER_RAMP_Z[1]], [RECEIVER_X[0], RECEIVER_RAMP_Z[0]]])
}

fn east_groove(g: &mut Graph) -> Shape {
    corner_prism(g, 2, RECEIVER_BOTTOM_Z - 1.3, SLOT_ROOF_Z,
        vec![[SLOT_MOUTH_X[0], RECEIVER_FORE_Y - 1.0],
             [SLOT_MOUTH_X[1], RECEIVER_FORE_Y - 1.0],
             [SLOT_MOUTH_X[1], RECEIVER_FORE_Y],
             [SLOT_X[1], SLOT_FLARE_END_Y], [SLOT_X[1], SLOT_END_Y],
             [SLOT_X[0], SLOT_END_Y], [SLOT_X[0], SLOT_FLARE_END_Y],
             [SLOT_MOUTH_X[0], RECEIVER_FORE_Y]],
        SLOT_NORTH_RADIUS, &[4, 5])
}

/// Each lower rail carries a rounded, broad-based key with a named picking identity.
pub fn lower(g: &mut Graph, mut piece: Shape) -> Shape {
    let east = east_key(g);
    for (side, sign) in [("west", -1.0), ("east", 1.0)] {
        let key = if sign < 0.0 { g.mirror(east, 0) } else { east };
        let key = g.feature(key, format!("{side}-alignment-key"),
            format!("{side} alignment key"), &[]);
        piece = g.union(piece, &[key]);
    }
    piece
}

/// Each upper wall carries a continuous corbelled receiver and its named receiving groove.
pub fn upper(g: &mut Graph, mut piece: Shape) -> Shape {
    let east_stock = east_receiver(g);
    let east_air = east_groove(g);
    for (side, sign) in [("west", -1.0), ("east", 1.0)] {
        let stock = if sign < 0.0 { g.mirror(east_stock, 0) } else { east_stock };
        let air = if sign < 0.0 { g.mirror(east_air, 0) } else { east_air };
        let stock = g.feature(stock, format!("{side}-alignment-receiver"),
            format!("{side} alignment receiver"), &[]);
        let air = g.feature(air, format!("{side}-alignment-groove"),
            format!("{side} alignment groove"), &[]);
        let receiver = g.cut(stock, &[air]);
        piece = g.union(piece, &[receiver]);
    }
    piece
}
