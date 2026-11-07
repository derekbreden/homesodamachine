//! The seam fits: the core's pocket through the floors, and the band each piece keeps clear of
//! the Y joint's slip.
use crate::catalog::{running, slip};
use crate::plan::{Graph, Shape};
use crate::quadrant::{Quadrant, Y, Z};
use crate::spec::Box;

/// The core's footprint through every piece: its stops' posts and its holds' aft line, at a
/// running fit.
pub fn core_fit_pocket(g: &mut Graph, b: &Box) -> Option<Shape> {
    let (stops, holds) = (&b.pack.core_stops, &b.pack.core_holds);
    if stops.is_empty() || holds.is_empty() {
        return None;
    }
    let r = stops[0][2];
    let (aft, crown) = (holds[0][2], holds[0][3]);
    assert!(
        stops.iter().all(|s| (s[2] - r).abs() < 1e-6),
        "the core's stops share one post radius"
    );
    assert!(
        holds
            .iter()
            .all(|h| (h[2] - aft).abs() < 1e-6 && (h[3] - crown).abs() < 1e-6),
        "the core's holds share one aft line and crown"
    );
    let x0 = stops
        .iter()
        .map(|s| s[0] - s[2])
        .fold(f64::INFINITY, f64::min);
    let x1 = stops
        .iter()
        .map(|s| s[0] + s[2])
        .fold(f64::NEG_INFINITY, f64::max);
    let fore = stops
        .iter()
        .map(|s| s[1] - s[2])
        .fold(f64::INFINITY, f64::min);
    let air = running();
    let (z0, z1) = (b.inner[4], crown + running());
    let (xa, xb, ya, yb) = (x0 + r, x1 - r, fore + r, aft - r);
    let along = g.box_([xa, xb, fore - air, aft + air, z0, z1]);
    let mut rest = vec![g.box_([x0 - air, x1 + air, ya, yb, z0, z1])];
    for x in [xa, xb] {
        for y in [ya, yb] {
            rest.push(g.zcyl(r + air, x, y, z0, z1));
        }
    }
    Some(g.union(along, &rest))
}

/// Cut the core's pocket, then keep each piece inside its own band past the joint's slip.
/// `rear` adds back-top's identification lands to its band.
pub fn seam_fit_reliefs(
    g: &mut Graph,
    mut piece: Shape,
    b: &Box,
    q: Quadrant,
    rear: &[Shape],
) -> Shape {
    if let Some(pocket) = core_fit_pocket(g, b) {
        piece = g.cut(piece, &[pocket]);
    }
    let [x0, x1, y0, y1, z0, z1] = b.exterior_bounds();
    if q.y == Y::Back || q.z == Z::Top {
        let fore = if q.y == Y::Back {
            b.y_joint + slip()
        } else {
            y0 - 1.0
        };
        let bottom = if q.z == Z::Top {
            q.zj(b) + running()
        } else {
            z0 - 1.0
        };
        let mut band = g.box_([x0 - 1.0, x1 + 1.0, fore, y1 + 1.0, bottom, z1 + 1.0]);
        if q == Quadrant::BACK_TOP {
            band = g.union(band, rear);
        }
        piece = g.intersect(piece, &[band]);
    }
    piece
}
