//! The Y-joint screw stacks: interleaved knuckles on each flank that the M5 rods pass through,
//! one stack below the Z seam and one above it.
use crate::catalog::{m5_thread_pass_dia, running, slip, supported};
use crate::funnel;
use crate::handholds::handhold_levels;
use crate::plan::{Bounds, Graph, Shape};
use crate::quadrant::{Quadrant, Y, sorted};
use crate::rails::rail_x;
use crate::shell::*;
use crate::walls::back_flank_start;

/// One knuckle's place in a stack: the piece that carries it, its Z span, and the gaps it keeps
/// below and above to its neighbours.
#[derive(Clone, Copy, Debug)]
pub struct Row {
    pub piece: Quadrant,
    pub z0: f64,
    pub z1: f64,
    pub below: f64,
    pub above: f64,
}

/// The gap between two knuckles: running clearance plus each supported face's allowance.
pub fn y_stack_gap(down_supported: bool, up_supported: bool) -> f64 {
    running() + supported() * (down_supported as u8 + up_supported as u8) as f64
}

/// The lower and upper stacks' knuckles, bottom to top.
pub fn y_stack(inner: &Bounds) -> ([Row; 3], [Row; 3]) {
    let [_, ceiling, crown] = handhold_levels(inner);
    let sloped = running() * 2f64.sqrt();
    let seated = y_stack_gap(false, false);
    let top = Z_SEAM;
    let lower_seat = top + Y_STACK_SCREW_LENGTH_TOLERANCE - LOWER_ROD_LEN;
    let fb0 = (crown + sloped - slip()).max(lower_seat + Y_STACK_LOWER_PLANE_OVER_SEAT + sloped);
    let bb0 = top - Y_STACK_LOWER_ANCHOR_FACE_DROP + sloped;
    let row = |piece, z0, z1, below, above| Row { piece, z0, z1, below, above };
    let lower = [
        row(Quadrant::BACK_BOTTOM, ceiling, fb0 - sloped, 0.0, sloped),
        row(Quadrant::FRONT_BOTTOM, fb0, bb0 - sloped, sloped, sloped),
        row(Quadrant::BACK_BOTTOM, bb0, top, sloped, 0.0),
    ];
    let roof = inner[5] + WALL;
    let datum = Y_STACK_UPPER_DATUM;
    let head_seat = roof - Y_STACK_HEAD_RECESS - Y_STACK_HEAD_H;
    let pilot_bottom = (datum - FLOOR_HEATSET_DEPTH - MOUNT_BORE_RELIEF)
        .min(head_seat - UPPER_ROD_LEN - Y_STACK_TIP_CLEARANCE);
    let front_floor = pilot_bottom - Y_STACK_AXIS_IN - FLOOR_HEATSET_DIA / 2.0 - WALL - slip();
    let upper = [
        row(Quadrant::FRONT_TOP, front_floor, datum, 0.0, seated),
        row(Quadrant::BACK_TOP, datum + seated, Y_STACK_UPPER_HEAD_DATUM - sloped, seated, sloped),
        row(Quadrant::FRONT_TOP, Y_STACK_UPPER_HEAD_DATUM, roof, sloped, 0.0),
    ];
    (lower, upper)
}

/// A stack's rod: its head seat, its tip, and the insert it threads into.
#[derive(Clone, Copy, Debug)]
pub struct Rod {
    pub seat: f64,
    pub tip: f64,
    pub insert: [f64; 2],
}

pub fn y_stack_rods(inner: &Bounds) -> [Rod; 2] {
    let (lower, upper) = y_stack(inner);
    let top = lower[2].z1;
    let seat = top + Y_STACK_SCREW_LENGTH_TOLERANCE - LOWER_ROD_LEN;
    let low = Rod { seat, tip: seat + LOWER_ROD_LEN, insert: [top - FLOOR_HEATSET_DEPTH, top] };
    let (roof, datum) = (upper[2].z1, upper[0].z1);
    let seat = roof - Y_STACK_HEAD_RECESS - Y_STACK_HEAD_H;
    let high = Rod { seat, tip: seat - UPPER_ROD_LEN, insert: [datum - FLOOR_HEATSET_DEPTH, datum] };
    [low, high]
}

/// A stack's rod axis in plan, at the middle of the Y joint's lip.
pub fn y_stack_axis(x_in: f64, sx: f64, y_joint: f64, lower: bool) -> [f64; 2] {
    let inset = if lower { Y_STACK_LOWER_AXIS_IN } else { Y_STACK_AXIS_IN };
    [x_in + sx * inset, y_joint + LIP_LEN / 2.0]
}

/// How a knuckle's face runs: sloping aft, sloping inboard, or level.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Face {
    Aft,
    In,
    Level,
}

fn knuckle_faces(piece: Quadrant, below: f64, above: f64) -> (Face, Face) {
    match piece {
        Quadrant::FRONT_BOTTOM => (Face::Aft, Face::In),
        Quadrant::BACK_BOTTOM => (
            if below != 0.0 { Face::In } else { Face::Level },
            if above != 0.0 { Face::Aft } else { Face::Level },
        ),
        Quadrant::FRONT_TOP => (if below != 0.0 { Face::Aft } else { Face::In }, Face::Level),
        _ => (Face::Level, Face::Aft),
    }
}

/// Where the flank's geometry around one knuckle stands: the wall it reaches in from.
#[derive(Clone, Copy)]
struct Flank {
    x_in: f64,
    sx: f64,
    y_joint: f64,
}

impl Flank {
    fn face_z(&self, kind: Face, level: f64, x: f64, y: f64) -> f64 {
        match kind {
            Face::Aft => level + (y - self.y_joint),
            Face::In => level + self.sx * (x - self.x_in),
            Face::Level => level,
        }
    }

    fn under_face(&self, g: &mut Graph, kind: Face, level: f64, x: (f64, f64), y: (f64, f64), z_floor: f64) -> Shape {
        let ((xa, xb), (ya, yb)) = (x, y);
        match kind {
            Face::Aft => g.yz_prism(xa, xb, vec![[ya, z_floor], [yb, z_floor], [yb, level + (yb - self.y_joint)],
                                                 [ya, level + (ya - self.y_joint)]]),
            Face::In => g.xz_prism(ya, yb, vec![[xa, z_floor], [xb, z_floor], [xb, level + self.sx * (xb - self.x_in)],
                                                [xa, level + self.sx * (xa - self.x_in)]]),
            Face::Level => g.box_([xa, xb, ya, yb, z_floor, level]),
        }
    }

    /// The stock between a lower face and an upper one over a plan rectangle.
    #[allow(clippy::too_many_arguments)]
    fn between(&self, g: &mut Graph, bottom: Face, z0: f64, top: Face, z1: f64, x: (f64, f64), y: (f64, f64),
               cap: Option<f64>) -> Shape {
        let corners = [(x.0, y.0), (x.0, y.1), (x.1, y.0), (x.1, y.1)];
        let low = corners.iter().map(|&(cx, cy)| self.face_z(bottom, z0, cx, cy)).fold(f64::INFINITY, f64::min) - 1.0;
        let upper = self.under_face(g, top, z1, x, y, low);
        let lower = self.under_face(g, bottom, z0, x, y, low - 1.0);
        let body = g.cut(upper, &[lower]);
        match cap {
            None => body,
            Some(c) => {
                let limit = g.box_([x.0, x.1, y.0, y.1, low - 1.0, c]);
                g.intersect(body, &[limit])
            }
        }
    }

    fn xs(&self, d0: f64, d1: f64) -> (f64, f64) {
        sorted(self.x_in + self.sx * d0, self.x_in + self.sx * d1)
    }
}

fn top_cap(top: Face, z1: f64, depth: f64) -> Option<f64> {
    match top {
        Face::In => Some(z1 + depth - WALL),
        Face::Aft => Some(z1 + LIP_LEN - WALL),
        Face::Level => None,
    }
}

#[allow(clippy::too_many_arguments)]
fn knuckle(g: &mut Graph, inner: &Bounds, silhouette: Shape, f: Flank, row: &Row, depth: f64) -> Shape {
    let (piece, z0, z1) = (row.piece, row.z0, row.z1);
    let (bottom, top) = knuckle_faces(piece, row.below, row.above);
    let cap = top_cap(top, z1, depth);
    let y_joint = f.y_joint;
    let body = if piece.y == Y::Front {
        let head = piece == Quadrant::FRONT_TOP && row.below > 0.0;
        let x = f.xs(if head { -WALL } else { running() }, depth);
        let root = y_joint - Y_STACK_FRONT_ROOT;
        let aft = y_joint + LIP_LEN;
        let mut body = if bottom == Face::Aft {
            let body = f.between(g, bottom, z0, top, z1, x, (y_joint - 0.01, aft), cap);
            let root_bottom = if head { Face::In } else { Face::Level };
            let root_z = if head { y_stack(inner).1[0].z0 } else { handhold_levels(inner)[2] - 0.01 };
            let root_body = f.between(g, root_bottom, root_z, top, z1, x, (root, y_joint), cap);
            g.union(body, &[root_body])
        } else {
            f.between(g, bottom, z0, top, z1, x, (root, y_joint + LIP_LEN), cap)
        };
        if piece == Quadrant::FRONT_TOP && f.sx > 0.0 && !head {
            let (sx, c) = (f.sx, Y_STACK_UPPER_CHAMFER);
            let (ex, ey) = (f.x_in + sx * depth, y_joint + LIP_LEN);
            let (zlo, zhi) = (z0.min(z1) - 1.0, z0.max(z1) + depth + 1.0);
            let corner = g.xy_prism(zlo, zhi, vec![[ex + sx, ey + 1.0], [ex - sx * (c + 1.0), ey + 1.0],
                                                   [ex + sx, ey - c - 1.0]]);
            body = g.cut(body, &[corner]);
        }
        body
    } else {
        let x = f.xs(-1.0, depth);
        let full = piece == Quadrant::BACK_BOTTOM && top == Face::Level;
        let start = back_flank_start(y_joint);
        let end = if full { start } else { y_joint + LIP_LEN };
        let mut body = f.between(g, bottom, z0, top, z1, x, (y_joint, end), cap);
        let x = f.xs(-1.0, BACK_BOTTOM_FLANK_T - WALL);
        let flank = f.between(g, bottom, z0, top, z1, x, (y_joint + LIP_LEN - 0.01, start + 0.01), cap);
        body = g.union(body, &[flank]);
        if piece == Quadrant::BACK_TOP {
            let tail = g.box_([x.0, x.1, y_joint + LIP_LEN + running(), start + 0.01, z0, inner[5] + WALL]);
            body = g.union(body, &[tail]);
        }
        if full {
            let x = f.xs(-1.0, (rail_x(f.sx, Y::Back).arm_end - f.x_in).abs());
            let stop = f.between(g, bottom, z0, top, z1, x, (start - 0.01, start + RAIL_STOP_LEN - slide_slip()), cap);
            body = g.union(body, &[stop]);
        }
        body
    };
    g.intersect(body, &[silhouette])
}

/// One knuckle on the flank that reaches in from `x_in`, before its bores and the funnel's trim:
/// the stock the print regions fill solid.
#[allow(clippy::too_many_arguments)]
pub fn y_knuckle(g: &mut Graph, inner: &Bounds, silhouette: Shape, x_in: f64, sx: f64, y_joint: f64, row: &Row,
                 depth: f64) -> Shape {
    knuckle(g, inner, silhouette, Flank { x_in, sx, y_joint }, row, depth)
}

/// The air a knuckle of the other half takes out of this piece, with its gaps.
fn knuckle_air(g: &mut Graph, f: Flank, row: &Row, depth: f64) -> Shape {
    let (bottom, top) = knuckle_faces(row.piece, row.below, row.above);
    let y_joint = f.y_joint;
    let (x, y) = if row.piece.y == Y::Front {
        let x = if row.piece == Quadrant::FRONT_TOP && row.below > 0.0 {
            f.xs(-(WALL + 1.0), depth + 1.0)
        } else {
            f.xs(0.0, depth + 1.0)
        };
        (x, (y_joint - 1.0, y_joint + LIP_LEN + running()))
    } else {
        (f.xs(0.0, depth + 1.0), (y_joint, back_flank_start(y_joint) + 1.0))
    };
    f.between(g, bottom, row.z0 - row.below, top, row.z1 + row.above, x, y, None)
}

/// The bores each flank's two rods pass through: head access, clearance and insert pilots.
pub fn y_stack_bores(g: &mut Graph, x_in: f64, sx: f64, y_joint: f64, inner: &Bounds) -> [Shape; 6] {
    let [lx, ly] = y_stack_axis(x_in, sx, y_joint, true);
    let [ux, uy] = y_stack_axis(x_in, sx, y_joint, false);
    let (lower, upper) = y_stack(inner);
    let (ceiling, roof) = (lower[0].z0, upper[2].z1);
    let [low, high] = y_stack_rods(inner);
    let (rc, rp, ri) = (Y_STACK_CBORE_DIA / 2.0, m5_thread_pass_dia() / 2.0, FLOOR_HEATSET_DIA / 2.0);
    let head_access = |g: &mut Graph, ax: f64, ay: f64, z0: f64, z1: f64, x_end: f64| {
        let (xa, xb) = sorted(ax, x_end);
        let bore = g.zcyl(rc, ax, ay, z0, z1);
        let slot = g.box_([xa, xb, ay - rc, ay + rc, z0, z1]);
        g.union(bore, &[slot])
    };
    let wall_face = x_in + sx * (y_stack_low_depth() - HANDHOLD_WALL);
    let mouth = x_in + sx * (x_in.abs() - funnel::COLLAR_W / 2.0);
    let upper_head = head_access(g, ux, uy, roof - Y_STACK_CBORE_DEPTH, roof + 1.0, mouth);
    let (xa, xb) = sorted(ux, mouth);
    let slot = g.box_([xa, xb, uy - rc, y_joint + LIP_LEN + running(), roof - Y_STACK_CBORE_DEPTH, roof + 1.0]);
    let upper_head = g.union(upper_head, &[slot]);
    let lower_head = head_access(g, lx, ly, ceiling - 0.01, low.seat, wall_face);
    [
        lower_head,
        g.zcyl(rp, lx, ly, low.seat - 0.01, low.insert[0] + 0.01),
        g.zcyl(ri, lx, ly, low.insert[0] - MOUNT_BORE_RELIEF, low.insert[1] + 1.0),
        upper_head,
        g.zcyl(rp, ux, uy, high.insert[1] - 0.01, roof - Y_STACK_CBORE_DEPTH + 0.01),
        g.zcyl(ri, ux, uy, (high.insert[0] - MOUNT_BORE_RELIEF).min(high.tip - Y_STACK_TIP_CLEARANCE), high.insert[1]),
    ]
}

/// The chamfered reliefs where a rod's clearance bore crosses a sloping knuckle face.
pub fn y_bore_reliefs(g: &mut Graph, x_in: f64, sx: f64, y_joint: f64, inner: &Bounds, name: Quadrant) -> Vec<Shape> {
    let rp = m5_thread_pass_dia() / 2.0;
    let f = Flank { x_in, sx, y_joint };
    let (lower_rows, upper_rows) = y_stack(inner);
    let rods = y_stack_rods(inner);
    let mut out = vec![];
    for (index, (lower, inset, rows)) in
        [(true, Y_STACK_LOWER_AXIS_IN, lower_rows), (false, Y_STACK_AXIS_IN, upper_rows)].into_iter().enumerate()
    {
        let [lx, ly] = y_stack_axis(x_in, sx, y_joint, lower);
        let stock = inset - running() - rp;
        let seat = rods[index].seat;
        let run = rp + stock / 2f64.sqrt();
        for row in rows.iter().filter(|r| r.piece == name) {
            if !lower && row.piece == Quadrant::FRONT_TOP && row.below == 0.0 {
                continue;
            }
            let (bottom, top) = knuckle_faces(row.piece, row.below, row.above);
            for (kind, level, t) in [(bottom, row.z0, 1.0), (top, row.z1, -1.0)] {
                if kind == Face::Level {
                    continue;
                }
                let f0 = f.face_z(kind, level, lx, ly);
                let section: [[f64; 2]; 4] = if t > 0.0 {
                    [[0.0, f0 - 1.0], [0.0, f0 + 2.0 * run], [run, f0 + run], [run, f0 + run - 1.0]]
                } else {
                    let edge = if kind == Face::In { (lx - x_in).abs() - running() } else { ly - y_joint };
                    let floor = if lower { (f0 - edge).max(seat + stock) } else { f0 - edge };
                    let reach = f0 - floor + 1.0;
                    [[0.0, floor], [reach, floor], [reach, f0 + 1.0], [0.0, f0 + 1.0]]
                };
                out.push(if kind == Face::Aft {
                    g.yz_prism(lx - rp, lx + rp, section.iter().map(|&[u, z]| [ly + t * u, z]).collect())
                } else {
                    g.xz_prism(ly - rp, ly + rp, section.iter().map(|&[u, z]| [lx + sx * t * u, z]).collect())
                });
            }
        }
    }
    out
}

/// Each flank's stacks in this piece: the other half's knuckles cleared, this piece's knuckles
/// added, and the rods' bores cut. `funnel_cut` trims front-top's head knuckle.
pub fn y_stacks(
    g: &mut Graph,
    mut piece: Shape,
    inner: &Bounds,
    silhouette: Shape,
    y_joint: f64,
    name: Quadrant,
    funnel_cut: Option<Shape>,
) -> Shape {
    let (lower, upper) = y_stack(inner);
    let rows: Vec<(Row, f64)> = lower.iter().map(|r| (*r, y_stack_low_depth()))
        .chain(upper.iter().map(|r| (*r, Y_STACK_HIGH_DEPTH)))
        .collect();
    for (x_in, sx) in [(inner[0], 1.0), (inner[1], -1.0)] {
        let f = Flank { x_in, sx, y_joint };
        for (row, depth) in &rows {
            if row.piece.y != name.y {
                let air = knuckle_air(g, f, row, *depth);
                piece = g.cut(piece, &[air]);
            }
        }
        for (row, depth) in &rows {
            if row.piece == name {
                let mut k = knuckle(g, inner, silhouette, f, row, *depth);
                if row.piece == Quadrant::FRONT_TOP && row.z0 == Y_STACK_UPPER_HEAD_DATUM {
                    if let Some(cut) = funnel_cut {
                        k = g.cut(k, &[cut]);
                    }
                }
                piece = g.union(piece, &[k]);
            }
        }
        for cutter in y_stack_bores(g, x_in, sx, y_joint, inner) {
            piece = g.cut(piece, &[cutter]);
        }
        for cutter in y_bore_reliefs(g, x_in, sx, y_joint, inner, name) {
            piece = g.cut(piece, &[cutter]);
        }
    }
    piece
}
