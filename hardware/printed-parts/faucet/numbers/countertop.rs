//! The kitchen countertop the faucet's stack clamps through, in millimetres: the slab the faucet
//! assembly and the install guide stand the faucet on, and the hole drilled through it. Its top is
//! the gasket's underside.

use crate::interface::{DRAIN_TUBE_OD, FLAVOR_TUBE_DEPTH, FLAVOR_TUBE_X_OFFSET};
use crate::paths::{FLAVOR_OD, LOWER_BUNDLE_X, LOWER_DRAIN_Y, RIBBON_DEPTH, RIBBON_WIDTH};
use crate::shell::SIGNAL_LOWER_EXIT;
use crate::stack::GASKET_Z;

/// The slab drawn: a laminate countertop is about 32 mm, a granite one about 38.
pub const THICKNESS: f64 = 30.0;
/// The thinnest and thickest counters the stack clamps through.
pub const MIN_THICKNESS: f64 = 19.0;
pub const MAX_THICKNESS: f64 = 38.0;
/// The slab's top, under the gasket, and its underside.
pub const TOP_Z: f64 = GASKET_Z[0];
pub const BOTTOM_Z: f64 = TOP_Z - THICKNESS;
/// The slab drawn, square, across.
pub const SLAB: f64 = 120.0;
/// The hole a faucet is mounted through.
pub const HOLE_DIAMETER: f64 = 34.93;
pub const HOLE_RADIUS: f64 = HOLE_DIAMETER / 2.0;

/// The hole's centre in Y, as far forward as the flavor pair, the drain and the cable through the
/// stack allow: each passes the hole with its own clearance.
pub fn hole_center_y() -> f64 {
    let (flavor_r, drain_r) = (FLAVOR_OD / 2.0, DRAIN_TUBE_OD / 2.0);
    let rows = [
        [LOWER_BUNDLE_X + FLAVOR_TUBE_X_OFFSET, FLAVOR_TUBE_DEPTH, flavor_r],
        [LOWER_BUNDLE_X - FLAVOR_TUBE_X_OFFSET, FLAVOR_TUBE_DEPTH, flavor_r],
        [LOWER_BUNDLE_X, LOWER_DRAIN_Y, drain_r],
    ];
    let mut limits: Vec<f64> = rows.iter().map(|&[x, y, r]| y - ((HOLE_RADIUS - r).powi(2) - x * x).sqrt()).collect();
    let [ex, ey] = SIGNAL_LOWER_EXIT;
    for dx in [-RIBBON_WIDTH / 2.0, RIBBON_WIDTH / 2.0] {
        for dy in [-RIBBON_DEPTH / 2.0, RIBBON_DEPTH / 2.0] {
            limits.push(ey + dy - (HOLE_RADIUS.powi(2) - (ex + dx).powi(2)).sqrt());
        }
    }
    limits.into_iter().fold(f64::NEG_INFINITY, f64::max)
}
