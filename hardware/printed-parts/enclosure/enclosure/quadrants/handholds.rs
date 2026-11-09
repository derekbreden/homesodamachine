//! The lifting handholds under each flank of the bottom pieces.
use crate::catalog::{outward_per_height, running, supported};
use crate::plan::{Bounds, Graph, HandholdAir, Op, Shape};
use crate::quadrant::{Y, sorted};
use crate::shell::*;
use crate::ystacks::y_stack_gap;

/// The handhold's bed, its lifting roof and the crown over it.
pub fn handhold_levels(inner: &Bounds) -> [f64; 3] {
    let bed = inner[4] - slab_t();
    let roof = bed + HANDHOLD_HEIGHT + supported();
    [bed, roof, roof + HANDHOLD_ROOF]
}

/// The flank's grown face and the side band's cap, from the exterior face inward.
pub fn band_x(x_ext: f64, sx: f64) -> [f64; 2] {
    [x_ext + sx * BACK_BOTTOM_FLANK_T, x_ext + sx * (WALL + y_stack_low_depth())]
}

pub fn handhold_y() -> [f64; 2] {
    [HANDHOLD_Y - HANDHOLD_LENGTH / 2.0, HANDHOLD_Y + HANDHOLD_LENGTH / 2.0]
}

/// Where the handhold's inner wall backing ends at the Y joint.
pub fn handhold_backing_end(y_joint: f64, side: Y) -> f64 {
    y_joint + LIP_LEN - HANDHOLD_WALL - if side == Y::Front { running() } else { 0.0 }
}

/// The inner wall's piece across the Y joint.
pub fn handhold_backing_joint(g: &mut Graph, inner: &Bounds, y_joint: f64, x_ext: f64, sx: f64, side: Y) -> Shape {
    let [bed, roof, _] = handhold_levels(inner);
    let [_, cap] = band_x(x_ext, sx);
    let (xa, xb) = sorted(cap, cap - sx * HANDHOLD_WALL);
    let floor = bed - if side == Y::Front { 1.0 } else { 0.0 };
    g.box_([xa, xb, handhold_backing_end(y_joint, side), y_joint + LIP_LEN + WALL, floor, roof])
}

/// The handhold's stock in the side band: its end post, roof and inner wall.
pub fn handhold_frame(g: &mut Graph, inner: &Bounds, y_joint: f64, x_ext: f64, sx: f64, side: Y) -> Shape {
    let [bed, roof, crown] = handhold_levels(inner);
    let [y0, y1] = handhold_y();
    let [_, cap] = band_x(x_ext, sx);
    let (xa, xb) = sorted(x_ext, cap);
    let (start, end) = match side {
        Y::Front => (y0 - HANDHOLD_WALL, y_joint),
        Y::Back => (y_joint, y1 + HANDHOLD_WALL),
    };
    let frame = g.box_([xa, xb, start, end, bed, crown]);
    let (wa, wb) = sorted(cap, cap - sx * HANDHOLD_WALL);
    match side {
        Y::Front => {
            let backing = g.box_([wa, wb, y_joint - 1.0, handhold_backing_end(y_joint, Y::Front), inner[4],
                                  roof - y_stack_gap(false, true)]);
            g.union(frame, &[backing])
        }
        Y::Back => {
            let r = running();
            let gap = g.box_([wa - r, wb + r, y_joint, handhold_backing_end(y_joint, Y::Back), bed - 1.0, roof]);
            let frame = g.cut(frame, &[gap]);
            let joint = handhold_backing_joint(g, inner, y_joint, x_ext, sx, side);
            g.union(frame, &[joint])
        }
    }
}

/// The opening under the handhold's roof, rounded on its corners.
pub fn handhold_cutter(g: &mut Graph, inner: &Bounds, x_ext: f64, sx: f64) -> Shape {
    let [bed, roof, _] = handhold_levels(inner);
    let [y0, y1] = handhold_y();
    let [_, cap] = band_x(x_ext, sx);
    let (xa, xb) = sorted(cap - sx * HANDHOLD_WALL, x_ext - sx);
    let b = [xa, xb, y0, y1, bed - 1.0, roof];
    g.add(Op::HandholdCutter { b, radius: HANDHOLD_CORNER_R }, vec![], Some(b))
}

pub fn handholds(g: &mut Graph, mut solid: Shape, inner: &Bounds, y_joint: f64, side: Y) -> Shape {
    for (x_in, sx) in [(inner[0], 1.0), (inner[1], -1.0)] {
        let x_ext = x_in - sx * WALL;
        let frame = handhold_frame(g, inner, y_joint, x_ext, sx, side);
        let name = if sx > 0.0 { "west" } else { "east" };
        let frame = g.feature(frame, format!("{name}-handhold"), format!("{name} lifting handhold"), &[]);
        solid = g.union(solid, &[frame]);
        let cutter = handhold_cutter(g, inner, x_ext, sx);
        let cutter = g.feature(cutter, format!("{name}-handhold"), format!("{name} lifting handhold"), &[]);
        solid = g.cut(solid, &[cutter]);
        if side == Y::Front {
            let joint = handhold_backing_joint(g, inner, y_joint, x_ext, sx, side);
            solid = g.cut(solid, &[joint]);
        }
    }
    solid
}

/// The rounded show edges the handhold's opening takes, in the west handhold's frame.
pub fn handhold_finish_air(g: &mut Graph, inner: &Bounds) -> Shape {
    let [bed, roof, crown] = handhold_levels(inner);
    let [y0, y1] = handhold_y();
    let depth = WALL + y_stack_low_depth();
    let end = HANDHOLD_CORNER_R + HANDHOLD_EDGE_R + HANDHOLD_WALL;
    let air = HandholdAir {
        bed,
        roof,
        crown,
        y: [y0, y1],
        depth,
        corner: HANDHOLD_CORNER_R,
        radius: HANDHOLD_EDGE_R,
        end_stock: end,
        cutter_depth: depth - HANDHOLD_WALL,
        slope: outward_per_height(),
    };
    g.add(Op::HandholdFinishAir(air), vec![], Some([0.0, depth, y0 - end, y1 + end, bed, crown]))
}

pub fn finish_handholds(g: &mut Graph, mut solid: Shape, inner: &Bounds) -> Shape {
    let air = handhold_finish_air(g, inner);
    for (x_in, sx) in [(inner[0], 1.0), (inner[1], -1.0)] {
        let placed = if sx > 0.0 { air } else { g.mirror(air, 0) };
        let placed = g.translate(placed, [x_in - sx * WALL, 0.0, 0.0]);
        let name = if sx > 0.0 { "west" } else { "east" };
        let placed = g.feature(placed, format!("{name}-handhold"), format!("{name} lifting handhold"), &[]);
        solid = g.cut(solid, &[placed]);
    }
    solid
}
