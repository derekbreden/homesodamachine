//! The flavour manifold's valve decks: each tray a plate of valve seats standing wall to wall
//! across a top piece, sunk with each valve's four post sockets and cleared for its body and port.
use crate::walls::{STATED_BOUND_TOL, flank_bedding_cut};
use crate::plan::{Bounds, Graph, Shape};
use crate::quadrant::{Quadrant, Y};
use crate::rails::{Run, rail_channel_span, z_rail_runs};
use crate::shapes::rounded;
use crate::shell::{Z_RISE, shell, slide_slip};
use crate::spec::Box;
use crate::walls::{front_top_flank_face, lip_face_x};

/// The Beduan solenoid valve, calipered. Its frame's Z = 0 is the plane of its four mounting
/// posts' ends, +Z up through the body, the port on Y.
pub mod valve {
    pub const CORNER_INSET_X: f64 = 24.4 / 2.0;
    pub const CORNER_INSET_Y: f64 = 24.85 / 2.0;
    pub const CORNER_BOSS_RADIUS: f64 = 3.45;
    pub const POST_SHOULDER_Z: f64 = 11.0;
    pub const UPPER_CORNER_RADIUS: f64 = 3.8;
    pub const BODY_RADIUS: f64 = 15.5;
    pub const BEARING_RADIUS: f64 = 12.15;
    pub const BEARING_Z: [f64; 2] = [5.2, 14.4];
    pub const BODY_MAIN_Z: [f64; 2] = [11.0, 24.5];
    pub const CAP_WIDTH_X: f64 = 33.5;
    pub const CAP_DEPTH_Y: f64 = 33.8;
    pub const CAP_CORNER_RADIUS: f64 = 4.5;
    pub const TOP_BOX_Z: [f64; 2] = [24.3, 26.0];
    pub const BODY_TOP_Z: f64 = TOP_BOX_Z[1];
    pub const PORT_RADIUS: f64 = 7.6;
    pub const PORT_CENTER_Z: f64 = 11.05;
}

/// The valve seat: four blind sockets the valve's corner posts press into, sunk to the plane
/// the valve's bearing boss lands on.
pub mod seat {
    use super::valve;
    use crate::catalog::slip;

    pub const SOCKET_RADIUS: f64 = 6.9 / 2.0;
    pub const WALL: f64 = 3.0;
    pub const SOCKET_FLOOR_Z: f64 = -1.0;
    pub const SEAT_TOP_Z: f64 = valve::BEARING_Z[0];
    pub const PORT_AIR: f64 = 0.5;
    pub const SOCKET_DEPTH: f64 = SEAT_TOP_Z - SOCKET_FLOOR_Z;

    /// The seat's reach along its port axis off the valve's centre.
    pub fn half_y() -> f64 {
        valve::CORNER_INSET_Y + valve::CORNER_BOSS_RADIUS + slip() + WALL
    }
}

/// The plate is one socket and one wall thick.
const THICK: f64 = seat::SOCKET_DEPTH + seat::WALL;
/// The plate runs this far past its outermost seats' reach.
const MARGIN: f64 = 3.0;
/// The valve-side face stands at the seat's landing plane.
const SEAT: f64 = -seat::SEAT_TOP_Z;
const PORT_SLIP: f64 = seat::PORT_AIR;

/// The seats' complete row span along the plate, their reach, and one margin past each end.
fn height(seats: &[[f64; 2]]) -> f64 {
    let (lo, hi) = span(seats.iter().map(|s| s[1]));
    hi - lo + 2.0 * (seat::half_y() + MARGIN)
}

fn span(values: impl Iterator<Item = f64>) -> (f64, f64) {
    values.fold((f64::INFINITY, f64::NEG_INFINITY), |(lo, hi), v| (lo.min(v), hi.max(v)))
}

/// The plate's lower edge at each wall, west then east, under that side's outermost valve row.
fn wall_root_floors(seats: &[[f64; 2]]) -> [f64; 2] {
    let (lo, hi) = span(seats.iter().map(|s| s[0]));
    [lo, hi].map(|edge| {
        let floor = seats
            .iter()
            .filter(|s| (s[0] - edge).abs() < 1e-6)
            .map(|s| s[1])
            .fold(f64::INFINITY, f64::min);
        floor - seat::half_y() - MARGIN
    })
}

/// The stepped valve body with its slip all round, in the valve's frame.
fn body_clearance(g: &mut Graph) -> Shape {
    use valve::*;
    let s = PORT_SLIP;
    let mut body = g.zcyl(BEARING_RADIUS + s, 0.0, 0.0, seat::SEAT_TOP_Z, BEARING_Z[1] + s);
    let main = g.zcyl(BODY_RADIUS + s, 0.0, 0.0, BODY_MAIN_Z[0] - s, BODY_MAIN_Z[1] + s);
    body = g.union(body, &[main]);
    for sx in [-1.0, 1.0] {
        for sy in [-1.0, 1.0] {
            let (x, y) = (sx * CORNER_INSET_X, sy * CORNER_INSET_Y);
            let boss = g.zcyl(CORNER_BOSS_RADIUS + s, x, y, seat::SEAT_TOP_Z, POST_SHOULDER_Z + s);
            body = g.union(body, &[boss]);
            let upper = g.zcyl(UPPER_CORNER_RADIUS + s, x, y, POST_SHOULDER_Z - s, BODY_TOP_Z + s);
            body = g.union(body, &[upper]);
        }
    }
    let cap = rounded(g, 2, [-CAP_WIDTH_X / 2.0 - s, CAP_WIDTH_X / 2.0 + s, -CAP_DEPTH_Y / 2.0 - s,
                             CAP_DEPTH_Y / 2.0 + s, TOP_BOX_Z[0] - s, TOP_BOX_Z[0] + (BODY_TOP_Z - TOP_BOX_Z[0]) + s],
                      CAP_CORNER_RADIUS + s, &[0, 1, 2, 3]);
    g.union(body, &[cap])
}

/// One valve's port channel in its own frame: the barrel and its slip, run `length` along Y.
fn port_channel(g: &mut Graph, length: f64) -> Shape {
    g.ycyl(valve::PORT_RADIUS + PORT_SLIP, 0.0, valve::PORT_CENTER_Z, -length / 2.0, length / 2.0)
}

/// A valve-frame shape turned onto its deck: the valve's +Z along the deck's sign in Y.
fn placed(g: &mut Graph, shape: Shape, plane: f64, sign: f64, x: f64, z: f64) -> Shape {
    let turned = g.rotate(shape, [0.0; 3], [1.0, 0.0, 0.0], if sign > 0.0 { -90.0 } else { 90.0 });
    g.translate(turned, [x, plane, z])
}

/// Each corner post's socket, its round room carried into a tangent teardrop roof.
fn socket_cutters(g: &mut Graph, plane: f64, sign: f64, x: f64, z: f64) -> Vec<Shape> {
    let (y0, y1) = crate::quadrant::sorted(plane + sign * seat::SOCKET_FLOOR_Z, plane + sign * (seat::SEAT_TOP_Z + 1.0));
    let mut out = Vec::new();
    for dx in [-valve::CORNER_INSET_X, valve::CORNER_INSET_X] {
        for dz in [-valve::CORNER_INSET_Y, valve::CORNER_INSET_Y] {
            out.push(g.teardrop_y(shell().teardrop_roof_angle, seat::SOCKET_RADIUS, x + dx, z - sign * dz, y0, y1, 1.0));
        }
    }
    out
}

/// Whether a valve tray's plane and mid height fall in these bands.
fn in_bands(plane: f64, seats: &[[f64; 2]], [y0, y1, z0, z1]: [f64; 4]) -> bool {
    let (lo, hi) = span(seats.iter().map(|s| s[1]));
    let mid = (lo + hi) / 2.0;
    y0 <= plane && plane <= y1 && z0 <= mid && mid <= z1
}

/// One tray's plate: wall to wall across the interior, footed onto the lip when it hangs over
/// the band's floor, its wall roots raised to the outermost rows, and on front-top bedded under
/// the grown flanks and their rail channels.
#[allow(clippy::too_many_arguments)]
fn plate(g: &mut Graph, inner: &Bounds, near: f64, far: f64, floor: f64, top: f64, wedge_depth: f64,
         foot_z0: f64, footed: bool, roots: [f64; 2], bed: Option<(f64, [Run; 2])>) -> Shape {
    let mut tray = g.box_([inner[0], inner[1], near, far, floor, top]);
    if wedge_depth > 0.0 {
        let wedge = g.yz_prism(inner[0], inner[1], vec![[far, floor], [near, floor], [(near + far) / 2.0, floor - wedge_depth]]);
        tray = g.union(tray, &[wedge]);
    }
    let [lx0, lx1] = lip_face_x();
    if footed {
        let footing = g.box_([lx0, lx1, near, far, foot_z0, floor]);
        tray = g.union(tray, &[footing]);
    }
    for ((outside, inside), root) in [(inner[0], lx0), (inner[1], lx1)].into_iter().zip(roots) {
        if root > floor + 1e-9 {
            let low = foot_z0.min(floor - wedge_depth) - 1.0;
            let raise = g.box_([outside.min(inside), outside.max(inside), near - 1.0, far + 1.0, low, root]);
            tray = g.cut(tray, &[raise]);
        }
    }
    if let Some((zj, runs)) = bed {
        let bedding = flank_bedding_cut(g, inner, near - 1.0, far + 1.0, zj);
        tray = g.cut(tray, &[bedding]);
        for run in runs {
            let (ya, yb) = (near.max(run.y0.min(run.lane_aft)), far.min(run.y0.max(run.lane_aft)));
            if yb <= ya {
                continue;
            }
            let [x_open, x_face, x_deep] = rail_channel_span(run.sx, Y::Front);
            let roof = zj + Z_RISE + slide_slip();
            let gable = roof + (x_deep - x_open).abs() / 2.0;
            let bedding = zj + Z_RISE + (run.x_in - x_face).abs();
            if bedding - gable > STATED_BOUND_TOL {
                let channel = g.xz_prism(ya, yb, vec![[x_face, gable], [x_face, bedding], [x_deep, roof]]);
                tray = g.cut(tray, &[channel]);
            }
        }
    }
    tray
}

/// Every valve deck whose plane and mid height fall in this quadrant's bands, fused with its
/// valves' clearances, sockets and port channels cut.
pub fn valve_trays(g: &mut Graph, mut piece: Shape, b: &Box, q: Quadrant, bands: [f64; 4]) -> Shape {
    let inner = &b.inner;
    let plate_aft = b.pack.collet_plate.wall_aft_y;
    let front_top = q == Quadrant::FRONT_TOP;
    let bed = front_top.then(|| (q.zj(b), z_rail_runs(inner, b.y_joint, Y::Front, Some(&b.pack.collet_plate))));
    for (plane, sign, seats) in &b.pack.valve_trays {
        let (plane, sign) = (*plane, *sign);
        if !in_bands(plane, seats, bands) {
            continue;
        }
        let (lo, hi) = span(seats.iter().map(|s| s[1]));
        let mid = (lo + hi) / 2.0;
        let half = height(seats) / 2.0;
        let face = plane - sign * SEAT;
        let (near, far) = crate::quadrant::sorted(face, face - sign * THICK);
        let (floor, top) = (mid - half, mid + half);
        let wedge_depth = if near < plate_aft && plate_aft < far { (far - near) / 2.0 } else { 0.0 };
        let foot_z0 = bands[2].max(inner[4]);
        let footed = sign < 0.0 && foot_z0 < floor - 1e-9;
        let tray = plate(g, inner, near, far, floor, top, wedge_depth, foot_z0, footed, wall_root_floors(seats), bed);
        piece = g.union(piece, &[tray]);
        for &[x, z] in seats {
            let body = body_clearance(g);
            let mut clearance = placed(g, body, plane, sign, x, z);
            if front_top {
                let [fx0, fx1] = front_top_flank_face();
                let keep = g.box_([fx0, fx1, near - 100.0, far + 100.0, z - 100.0, z + 100.0]);
                clearance = g.intersect(clearance, &[keep]);
            }
            piece = g.cut(piece, &[clearance]);
            for socket in socket_cutters(g, plane, sign, x, z) {
                piece = g.cut(piece, &[socket]);
            }
            let length = 2.0 * (half + (z - mid).abs()).max(top - z) + 2.0 * wedge_depth;
            let channel = port_channel(g, length + 2.0);
            let channel = placed(g, channel, plane, sign, x, z);
            piece = g.cut(piece, &[channel]);
        }
    }
    piece
}
