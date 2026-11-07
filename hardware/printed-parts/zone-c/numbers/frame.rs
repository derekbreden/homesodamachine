//! The PET-GF frame the funnel drops into under the roof, with its screw seats into the shell's
//! ledges and the cradle's snap socket under the drain. Its numbers are in its own frame: its
//! flat underside at Z = 0, under the funnel's plan centre. Its seat is the funnel brim's bearing
//! plane in the machine.
use crate::{Color, P2, catalog, cradle, funnel};
use hsm_enclosure_interface as interface;

/// The funnel's plan centre in the machine's Y.
pub const CENTER_Y: f64 = 182.5 + (funnel::AFT - funnel::FORWARD) / 2.0;
/// The frame's bottom web, under the plug's socket.
pub const WEB: f64 = 3.0;
/// The roof's width and the body's, and the frame's depth with the rear roof's access.
pub const WIDTH: f64 = 196.5;
pub const BODY_WIDTH: f64 = 176.5;
pub const DEPTH: f64 = funnel::COLLAR_D + 24.6;
pub const REAR_ACCESS: f64 = 5.0;
pub const CORNER: f64 = 6.0;
/// The socket the funnel's plug drops into.
pub const SOCKET_DEPTH: f64 = 19.0;
/// The M3 screws into the shell's ledges: their length, their grip and their heads.
pub const SCREW_LENGTH: f64 = 12.0;
pub const SCREW_GRIP: f64 = 5.8;
pub const HEAD_D: f64 = 5.5;
/// The ledge pads' half depth along Y, and the relief under each insert's pilot.
pub const PAD_HALF_Y: f64 = 6.0;
pub const PILOT_RELIEF: f64 = 1.5;
/// The interior the frame is drawn against, the brim's seat in it, and the shell's Y seam.
pub const INNER: [f64; 6] = [-104.5, 104.5, 0.0, 290.0, 0.0, 352.0];
pub const SEAT: f64 = 349.0;
pub const Y_JOINT: f64 = 200.0;
/// The air the funnel's forming envelope keeps.
pub const FORMING_AIR: f64 = 0.3;
/// The corbels that carry the roof: their half depth at the foot, and their slope.
pub const CORBEL_HALF_DEPTH: f64 = 27.5 + (funnel::FORWARD + funnel::AFT) / 2.0;

/// The frame's underside and the socket's floor, in the machine's Z.
fn datums() -> (f64, f64) {
    (SEAT - funnel::DROP - WEB, SEAT - funnel::DROP)
}

/// The roof: its front and back in the machine's Y, its floor and its top.
struct Roof {
    front: f64,
    back: f64,
    floor: f64,
    top: f64,
}

fn roof() -> Roof {
    let cy = CENTER_Y;
    Roof {
        front: cy - funnel::COLLAR_D / 2.0 - funnel::OVERHANG,
        back: cy + DEPTH / 2.0 + REAR_ACCESS,
        floor: SEAT - WEB,
        top: SEAT + funnel::BRIM_T,
    }
}

/// A screw seat in the machine's frame: where it stands, its side, whether it is a front one, the
/// head's seat and the insert's host.
struct Fastener {
    x: f64,
    y: f64,
    side: f64,
    front: bool,
    head_seat_z: f64,
    host_radius: f64,
}

fn fasteners() -> Vec<Fastener> {
    let cx = 0.0;
    let r = roof();
    let head_seat = r.floor + SCREW_GRIP;
    let mut rows = vec![];
    for (front, x, y) in [(true, 93.0, r.front + 32.0), (false, 87.7, r.back - REAR_ACCESS - 11.2)] {
        for side in [-1.0, 1.0] {
            rows.push(Fastener { x: cx + side * x, y, side, front, head_seat_z: head_seat, host_radius: interface::HEATSET_DIA / 2.0 + interface::WALL });
        }
    }
    rows
}

/// The body's half width: inside the front screws' hosts with the slide's slip.
fn body_half() -> f64 {
    let cx = 0.0;
    fasteners()
        .iter()
        .filter(|r| r.front)
        .map(|r| (r.x - cx).abs() - r.host_radius - interface::slide_slip())
        .reduce(f64::min)
        .expect("the frame's front screws")
}

/// A screw in the frame's own frame: its X and Y, its head's seat above the underside, its
/// insert's host, its side and whether it is a front one.
pub type Screw = (f64, f64, f64, f64, f64, bool);

/// The frame's numbers, as its geometry draws it.
pub struct Frame {
    pub color: Color,
    pub roof_width: f64,
    pub body_width: f64,
    pub front: f64,
    pub back: f64,
    pub roof_floor: f64,
    pub roof_top: f64,
    pub seat: f64,
    pub corner_radius: f64,
    pub rear_limits: P2,
    pub rear_start: f64,
    pub corbel_half_depth: f64,
    pub corbel_slope: f64,
    pub ledge_pad_half_y: f64,
    pub slide_slip: f64,
    pub screw_clear_radius: f64,
    pub head_radius: f64,
    pub rear_pad_radius: f64,
    pub front_head_inside: f64,
    pub screws: Vec<Screw>,
    pub body_half_width: f64,
    pub brim_half_size: P2,
    pub brim_radius: f64,
    pub drain_xy: P2,
    pub socket_size: P2,
    pub socket_radius: f64,
    pub socket_z: f64,
    pub socket_height: f64,
    pub socket_flare: P2,
    pub hole_radius: f64,
    pub web_cut_z: P2,
    pub slot_x: P2,
    pub slot_y: P2,
    pub funnel: funnel::Dimensions,
    pub forming_air: f64,
    pub forming_clip_z: P2,
}

/// The frame.
pub fn frame() -> Frame {
    let (cx, cy) = (0.0, CENTER_Y);
    let (floor, plug) = datums();
    let r = roof();
    let snap = cradle::stations();
    let half = funnel::PLUG_W / 2.0;
    let gap = (2.0 * cradle::SOCKET_HALF - funnel::PLUG_W) / 2.0;
    let rear_limit = INNER[1] - interface::Y_STACK_HIGH_DEPTH - interface::slide_slip();
    let air = interface::funnel_collar_air();
    Frame {
        color: catalog::petgf_black(),
        roof_width: WIDTH,
        body_width: BODY_WIDTH,
        front: r.front - cy,
        back: r.back - cy,
        roof_floor: r.floor - floor,
        roof_top: r.top - floor,
        seat: SEAT - floor,
        corner_radius: CORNER,
        rear_limits: (-rear_limit - cx, rear_limit - cx),
        rear_start: Y_JOINT - interface::slide_slip() - cy,
        corbel_half_depth: CORBEL_HALF_DEPTH,
        corbel_slope: 30_f64.to_radians().tan(),
        ledge_pad_half_y: PAD_HALF_Y,
        slide_slip: interface::slide_slip(),
        screw_clear_radius: interface::screw_clear_dia() / 2.0,
        head_radius: interface::head_cbore_dia() / 2.0,
        rear_pad_radius: HEAD_D / 2.0,
        front_head_inside: funnel::COLLAR_W / 2.0 + funnel::OVERHANG + air,
        screws: fasteners().iter().map(|f| (f.x - cx, f.y - cy, f.head_seat_z - floor, f.host_radius, f.side, f.front)).collect(),
        body_half_width: body_half(),
        brim_half_size: (funnel::COLLAR_W / 2.0 + funnel::OVERHANG + air, funnel::COLLAR_D / 2.0 + funnel::OVERHANG + air),
        brim_radius: funnel::BRIM_R + air,
        drain_xy: (0.0, 0.0),
        socket_size: (2.0 * (half + gap), 2.0 * (funnel::plug_half_length(half) + gap)),
        socket_radius: cradle::SOCKET_CORNER,
        socket_z: cradle::WEB,
        socket_height: SOCKET_DEPTH,
        socket_flare: (2.0, 1.0),
        hole_radius: cradle::HOLE_D / 2.0,
        web_cut_z: (-1.0, cradle::WEB + 1.0),
        slot_x: (snap.slot_in, snap.slot_out),
        slot_y: (cradle::SLOT_FORE - cradle::END_SLIP, cradle::SLOT_AFT + cradle::END_SLIP),
        funnel: funnel::dimensions(),
        forming_air: FORMING_AIR,
        forming_clip_z: (plug - floor, SEAT - floor),
    }
}
