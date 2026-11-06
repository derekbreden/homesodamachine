//! The drip funnel the roof seats and the frame that carries it: their declared sizes, the
//! frame's datums and fasteners, and the shell air each one takes.
use crate::plan::{Bounds, Graph, P2, Shape};
use crate::quadrant::{Y, sorted};
use crate::shapes::{corner_prism, rounded, rounded_prism};
use crate::shell::*;
use crate::structure::FUNNEL_SEAT;
use crate::ystacks::y_stack_axis;

pub const COLLAR_W: f64 = 165.0;
const FORWARD: f64 = 41.6085;
const AFT: f64 = 35.0;
pub const COLLAR_D: f64 = 81.78301584656256 + FORWARD + AFT;
const MOUTH_R: f64 = 14.0;
pub const COLLAR_R: f64 = MOUTH_R + 6.0;
pub const BRIM_R: f64 = COLLAR_R + 7.0;
pub const OVERHANG: f64 = 7.0;
pub const BRIM_T: f64 = 6.0;
pub const DROP: f64 = 46.1;

/// The frame's declared centre in Y and its own sizes.
pub const CENTER_Y: f64 = 182.5 + (AFT - FORWARD) / 2.0;
pub const FRAME_WEB: f64 = 3.0;
pub const FRAME_WIDTH: f64 = 196.5;
pub const BODY_WIDTH: f64 = 176.5;
pub const FRAME_DEPTH: f64 = COLLAR_D + 24.6;
pub const REAR_ACCESS: f64 = 5.0;
pub const FRAME_CORNER: f64 = 6.0;
pub const RAIL_BELOW: f64 = 42.1;
pub const SCREW_GRIP: f64 = 5.8;
pub const HEAD_H: f64 = 3.0;
pub const PAD_HALF_Y: f64 = 6.0;
pub const PILOT_RELIEF: f64 = 1.5;
pub const CORBEL_FOOT_HALF_DEPTH: f64 = 27.5 + (FORWARD + AFT) / 2.0;
/// The Y joint the frame's own records are drawn against.
pub const FRAME_Y_JOINT: f64 = 200.0;

pub fn corbel_slope() -> f64 {
    30_f64.to_radians().tan()
}

/// The brim's seat in the roof: its top face.
pub fn seat_z(outer: &Bounds) -> f64 {
    outer[5] - BRIM_T
}

/// The funnel's brim outline, grown by `grow`, over a Z span; its two aft corners round.
pub fn brim_plan(g: &mut Graph, grow: f64, z0: f64, z1: f64, [cx, cy]: P2, front: f64) -> Shape {
    let x = COLLAR_W / 2.0 + OVERHANG + grow;
    let y = COLLAR_D / 2.0 + OVERHANG + grow;
    rounded(g, 2, [cx - x, cx + x, cy - y - front, cy + y, z0, z1], BRIM_R + grow, &[2, 3])
}

/// The frame's web floor, its plug face and the rail under the seat.
pub fn datums(seat: f64) -> [f64; 3] {
    [seat - DROP - FRAME_WEB, seat - DROP, seat - RAIL_BELOW]
}

/// The frame's roof: its plan run and the Z it spans.
#[derive(Clone, Copy, Debug)]
pub struct Roof {
    pub width: f64,
    pub front: f64,
    pub back: f64,
    pub floor: f64,
    pub top: f64,
}

/// The frame roof's front edge, the brim's.
fn roof_front(cy: f64) -> f64 {
    cy - COLLAR_D / 2.0 - OVERHANG
}

pub fn roof_datums([_cx, cy]: P2, seat: f64) -> Roof {
    Roof {
        width: FRAME_WIDTH,
        front: roof_front(cy),
        back: cy + FRAME_DEPTH / 2.0 + REAR_ACCESS,
        floor: seat - FRAME_WEB,
        top: seat + BRIM_T,
    }
}

/// One of the frame's four screws into the shell's ledges.
#[derive(Clone, Copy, Debug)]
pub struct Fastener {
    pub col: Y,
    pub side: f64,
    pub x: f64,
    pub y: f64,
    pub ledge_z: f64,
    pub head_seat_z: f64,
    pub insert_top_z: f64,
    pub bore_bottom_z: f64,
    pub host_bottom_z: f64,
    pub host_radius: f64,
}

pub fn fasteners(centre: P2, seat: f64) -> [Fastener; 4] {
    let r = roof_datums(centre, seat);
    let ledge = r.floor;
    let bore_bottom = ledge - HEATSET_LONG_LEN - PILOT_RELIEF;
    let row = |col, side: f64, x: f64, y| Fastener {
        col,
        side,
        x: centre[0] + side * x,
        y,
        ledge_z: ledge,
        head_seat_z: ledge + SCREW_GRIP,
        insert_top_z: ledge,
        bore_bottom_z: bore_bottom,
        host_bottom_z: bore_bottom - WALL,
        host_radius: HEATSET_DIA / 2.0 + WALL,
    };
    let (front, back) = (r.front + 32.0, r.back - REAR_ACCESS - 11.2);
    [row(Y::Front, -1.0, 93.0, front), row(Y::Front, 1.0, 93.0, front),
     row(Y::Back, -1.0, 87.7, back), row(Y::Back, 1.0, 87.7, back)]
}

/// The frame's plan blank, stepped in behind the Y stacks when it is wider than their reach.
fn blank(g: &mut Graph, w: f64, front: f64, back: f64, z: P2, cx: f64, radius: f64, inner: &Bounds,
         y_joint: f64, air: f64) -> Shape {
    let half = w / 2.0;
    let limit = inner[1] - Y_STACK_HIGH_DEPTH - slide_slip() + air;
    let y0 = y_joint - slide_slip() + air;
    let (section, corners): (Vec<P2>, &[usize]) = if half <= limit {
        (vec![[cx - half, front], [cx + half, front], [cx + half, back], [cx - half, back]], &[2, 3])
    } else {
        (vec![[cx - half, front], [cx + half, front], [cx + half, y0], [limit, y0], [limit, back],
              [-limit, back], [-limit, y0], [cx - half, y0]], &[4, 5])
    };
    corner_prism(g, 2, z[0], z[1], section, radius, corners)
}

/// The frame's roof plate, grown by `air`.
pub fn roof_blank(g: &mut Graph, inner: &Bounds, centre: P2, seat: f64, air: f64, y_joint: f64) -> Shape {
    let r = roof_datums(centre, seat);
    blank(g, r.width + 2.0 * air, r.front - air, r.back + air, [r.floor, r.top + air], centre[0],
          FRAME_CORNER + air, inner, y_joint, air)
}

/// The frame's body under its roof, less the screw pads and the corbels' faces, grown by `air`.
pub fn body_blank(g: &mut Graph, centre: P2, seat: f64, air: f64, inner: &Bounds, y_joint: f64) -> Shape {
    let [cx, cy] = centre;
    let floor = datums(seat)[0];
    let r = roof_datums(centre, seat);
    let mut stock = blank(g, BODY_WIDTH + 2.0 * air, r.front - air, r.back + air, [floor - air, seat + air],
                          cx, FRAME_CORNER + air, inner, y_joint, air);
    for row in fasteners(centre, seat) {
        let inside = row.x - row.side * (row.host_radius + slide_slip() - air);
        let (xa, xb) = sorted(inside, cx + row.side * 150.0);
        let start = row.y - PAD_HALF_Y - slide_slip() + air;
        let end = match row.col {
            Y::Back => r.back + air + 1.0,
            Y::Front => row.y + PAD_HALF_Y + slide_slip() - air,
        };
        let pad = g.box_([xa, xb, start, end, floor - 1.0, r.floor]);
        stock = g.cut(stock, &[pad]);
    }
    for sign in [-1.0, 1.0] {
        let (low, high) = (floor - 2.0, floor + 80.0);
        let foot = CORBEL_FOOT_HALF_DEPTH + air / 30_f64.to_radians().cos();
        let y0 = cy + sign * (foot + corbel_slope() * (low - floor));
        let y1 = cy + sign * (foot + corbel_slope() * (high - floor));
        let outside = cy + sign * 400.0;
        let face = g.yz_prism(cx - 150.0, cx + 150.0, vec![[y0, low], [outside, low], [outside, high], [y1, high]]);
        stock = g.cut(stock, &[face]);
    }
    let roof = roof_blank(g, inner, centre, seat, air, y_joint);
    g.union(stock, &[roof])
}

/// The air the shell leaves round the frame's body.
pub fn shell_clearance(g: &mut Graph, centre: P2, seat: f64, inner: &Bounds) -> Shape {
    body_blank(g, centre, seat, slide_slip(), inner, FRAME_Y_JOINT)
}

/// The air the shell leaves round the frame's roof plate.
pub fn front_roof_clearance(g: &mut Graph, inner: &Bounds, centre: P2, seat: f64, y_joint: f64) -> Shape {
    roof_blank(g, inner, centre, seat, slide_slip(), y_joint)
}

/// The ledges one column's frame screws land on, each rooted in its flank; print-up pieces
/// take a corbel under each.
pub fn receivers(g: &mut Graph, inner: &Bounds, outer: &Bounds, centre: P2, seat: f64, col: Y,
                 up: Option<f64>) -> Option<Shape> {
    let mut blocks = Vec::new();
    for row in fasteners(centre, seat).into_iter().filter(|r| r.col == col) {
        let side = row.side;
        let inside = row.x - side * row.host_radius;
        let (xa, xb) = sorted(inside, if side < 0.0 { outer[0] } else { outer[1] });
        let (y0, bottom) = (row.y - PAD_HALF_Y, row.host_bottom_z);
        let mut block = g.box_([xa, xb, y0, y0 + 2.0 * PAD_HALF_Y, bottom, row.ledge_z]);
        if up.is_some_and(|u| u > 0.0) {
            let wall_x = if side > 0.0 { inner[1] } else { inner[0] };
            let corbel = g.xz_prism(y0, y0 + 2.0 * PAD_HALF_Y,
                                    vec![[inside, bottom], [wall_x, bottom], [wall_x, bottom - (wall_x - inside).abs()]]);
            block = g.union(block, &[corbel]);
        }
        blocks.push(block);
    }
    let (first, rest) = blocks.split_first()?;
    Some(g.union(*first, rest))
}

/// The heat-set bores one column's frame screws take in the shell.
pub fn shell_screw_cuts(g: &mut Graph, centre: P2, seat: f64, col: Y) -> Option<Shape> {
    let bores: Vec<Shape> = fasteners(centre, seat)
        .into_iter()
        .filter(|r| r.col == col)
        .map(|r| g.zcyl(HEATSET_DIA / 2.0, r.x, r.y, r.bore_bottom_z, r.insert_top_z + 1.0))
        .collect();
    let (first, rest) = bores.split_first()?;
    Some(g.union(*first, rest))
}

/// The funnel's plumb run under the seat, back to the frame's rear access.
fn plumb(g: &mut Graph, half: f64, front: f64, back: f64, seat: f64) -> Shape {
    let b = [-half, half, front, back, seat - FUNNEL_SEAT - 1.0, seat + slide_slip()];
    rounded(g, 2, b, FRAME_CORNER + slide_slip(), &[2, 3])
}

/// The roof's air for the funnel: its brim pocket and the sides back to the Y stacks' mouths, the
/// collar's throat, the frame's body and its plumb run, less the rear ledges.
pub fn funnel_cut(g: &mut Graph, inner: &Bounds, outer: &Bounds, centre: P2) -> Shape {
    let [cx, cy] = centre;
    let seat = seat_z(outer);
    let air = funnel_collar_air();
    let pocket = brim_plan(g, air, seat, outer[5] + 1.0, centre, 0.0);
    let half_w = COLLAR_W / 2.0 + OVERHANG + air;
    let mouth = y_stack_axis(inner[1], -1.0, Y_SEAM, false)[1] - Y_STACK_CBORE_DIA / 2.0;
    let sides = g.box_([cx - half_w, cx + half_w, cy, mouth, seat, outer[5] + 1.0]);
    let throat = rounded_prism(g, COLLAR_W + 2.0 * air, COLLAR_D + 2.0 * air, COLLAR_R + air,
                               inner[5] - WALL - 1.0, seat + 0.01, cx, cy);
    let clearance = shell_clearance(g, centre, seat, inner);
    let half = inner[1] - Y_STACK_HIGH_DEPTH;
    let back = roof_datums(centre, seat).back + slide_slip();
    let mut plumb = plumb(g, half, cy, back, seat);
    for col in [Y::Front, Y::Back] {
        if let Some(stock) = receivers(g, inner, outer, centre, seat, col, None) {
            plumb = g.cut(plumb, &[stock]);
        }
    }
    let cut = g.union(pocket, &[sides]);
    let cut = g.union(cut, &[throat]);
    let keepout = shell_clearance(g, centre, seat, inner);
    let cut = g.union(cut, &[keepout]);
    let frame = g.union(clearance, &[plumb]);
    g.union(cut, &[frame])
}

/// The plane the display housing reaches back to: one running fit ahead of the frame's flat
/// front, for a frame centred on `cy`.
pub fn housing_back_y(cy: f64) -> f64 {
    roof_front(cy) - slide_slip()
}

/// The collar's opening in plan, `[x0, x1, y0, y1]`, one running clearance clear on all four faces.
pub fn cut_plan([cx, cy]: P2) -> [f64; 4] {
    let air = funnel_collar_air();
    [cx - COLLAR_W / 2.0 - air, cx + COLLAR_W / 2.0 + air, cy - COLLAR_D / 2.0 - air, cy + COLLAR_D / 2.0 + air]
}
