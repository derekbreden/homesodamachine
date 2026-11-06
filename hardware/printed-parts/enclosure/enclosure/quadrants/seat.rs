//! The funnel's seat in the top pieces' roof: the seat's stock under the brim, the frame's
//! receivers, the funnel's air and the frame's clearances and screw bores, and on front-top the
//! display let in again through the housing it shares.
use crate::display::display_cut;
use crate::walls::{CEILING_LIP_DROP, y_lip_channel};
use crate::funnel::{self, BRIM_R, COLLAR_D, COLLAR_W, OVERHANG};
use crate::plan::{Graph, Shape};
use crate::quadrant::{Quadrant, Y};
use crate::shapes::rounded_prism;
use crate::shell::*;
use crate::spec::Box;
use crate::structure::FUNNEL_SEAT;
use crate::catalog::running;

/// The air front-top's ceiling tongue runs in over the Y joint.
pub fn ceiling_tongue_air(g: &mut Graph, inner: &crate::plan::Bounds, y_joint: f64) -> Shape {
    let lip_top = inner[5] - CEILING_LIP_DROP;
    g.box_([inner[0] + Y_STACK_HIGH_DEPTH, inner[1] - Y_STACK_HIGH_DEPTH, y_joint - WALL, y_joint + LIP_LEN + 1.0,
            lip_top - WALL - running() - 1.0, lip_top + 1.0])
}

/// The seat and the funnel frame's fits in one top quadrant.
pub fn funnel_seat(g: &mut Graph, mut piece: Shape, b: &Box, q: Quadrant, silhouette: Shape, up: f64) -> Shape {
    let (inner, outer, y_joint) = (&b.inner, &b.outer, b.y_joint);
    let centre = b.pack.funnel;
    let [cx, cy] = centre;
    let seat = funnel::seat_z(outer);
    let brim_front = cy - COLLAR_D / 2.0 - OVERHANG;
    let brim_back = cy + COLLAR_D / 2.0 + OVERHANG;
    let housing_face = funnel::housing_back_y(funnel::CENTER_Y);
    let seat_front = if q.y == Y::Front { housing_face } else { brim_front - FUNNEL_SEAT };
    let mut stock = g.box_([inner[0], inner[1], seat_front, brim_back + FUNNEL_SEAT, seat - FUNNEL_SEAT, outer[5]]);
    if q.y == Y::Back {
        let bearing = rounded_prism(g, COLLAR_W + 2.0 * OVERHANG + 2.0 * WALL, COLLAR_D + 2.0 * OVERHANG + 2.0 * WALL,
                                    BRIM_R + WALL, seat - FUNNEL_SEAT, seat, cx, cy);
        let floor = seat - FUNNEL_SEAT;
        for &(_, x0, x1, y0, y1, top) in &b.pack.ceiling_reliefs {
            let roof = top.min(inner[5]);
            if roof > floor {
                let relief = g.box_([x0, x1, y0, y1, floor - 1.0, roof]);
                let relief = g.cut(relief, &[bearing]);
                stock = g.cut(stock, &[relief]);
            }
        }
    }
    let [ylo, yhi, zlo, zhi] = q.bands(b);
    let own = g.box_([outer[0] - 1.0, outer[1] + 1.0, ylo, yhi, zlo, zhi]);
    let stock = g.intersect(stock, &[own]);
    let stock = g.intersect(stock, &[silhouette]);
    piece = g.union(piece, &[stock]);
    if q.y == Y::Front {
        let channel = y_lip_channel(g, inner, y_joint);
        piece = g.cut(piece, &[channel]);
    }
    if let Some(receivers) = funnel::receivers(g, inner, outer, centre, seat, q.y, Some(up)) {
        piece = g.union(piece, &[receivers]);
    }
    let air = funnel::funnel_cut(g, inner, outer, centre);
    piece = g.cut(piece, &[air]);
    if q.y == Y::Front {
        let tongue = ceiling_tongue_air(g, inner, y_joint);
        piece = g.cut(piece, &[tongue]);
    }
    let roof = funnel::front_roof_clearance(g, inner, centre, seat, y_joint);
    piece = g.cut(piece, &[roof]);
    if let Some(bores) = funnel::shell_screw_cuts(g, centre, seat, q.y) {
        piece = g.cut(piece, &[bores]);
    }
    if q.y == Y::Front {
        let channel = y_lip_channel(g, inner, y_joint);
        piece = g.cut(piece, &[channel]);
        let display = display_cut(g, outer);
        piece = g.cut(piece, &[display]);
        let plate = &b.pack.collet_plate;
        let root = b.pump_bay[2] + (housing_face - plate.wall_aft_y).abs();
        let grown = FRONT_TOP_FLANK_T - WALL;
        let surround = g.box_([inner[0] + grown, inner[1] - grown, housing_face, brim_front, root, outer[5] + 1.0]);
        piece = g.cut(piece, &[surround]);
    }
    piece
}
