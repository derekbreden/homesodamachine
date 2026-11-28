//! The PET-GF frame the funnel drops into under the roof, with its screw seats into the shell's
//! ledges and the cradle's snap socket under the drain. Its numbers are in its own frame: its
//! flat underside at Z = 0, under the funnel's plan centre. Its seat is the funnel brim's bearing
//! plane in the machine.
use crate::{Color, P2, catalog, cradle, funnel};
use hsm_enclosure_interface as interface;
use interface::funnel_mount::{self, BACK_SCREW_GRIP, BACK_SEAT_SLOPE, PAD_HALF_Y, REAR_ACCESS, SCREW_GRIP};
pub use interface::funnel_mount::back_axis;

/// The funnel's plan centre in the machine's Y.
pub const CENTER_Y: f64 = 182.5 + (funnel::AFT - funnel::FORWARD) / 2.0;
/// The roof web beneath the brim's seat.
pub const ROOF_WEB: f64 = 3.0;
/// Relief above the shell's bearing ledges for the frame's printed flange underside.
pub const SEATING_RELIEF: f64 = 0.48;
/// The roof's width and the body's, and the frame's depth with the rear roof's access.
pub const WIDTH: f64 = 196.5;
pub const BODY_WIDTH: f64 = 176.5;
pub const DEPTH: f64 = funnel::COLLAR_D + 24.6;
pub const CORNER: f64 = 6.0;
/// The socket mouth's height above the cradle's hook ledges.
pub const SOCKET_DEPTH: f64 = 19.0;
/// The T-shaped stem guide stands this far above the hook ledges.
pub const SOCKET_FLOOR_RISE: f64 = 2.4;
/// The interior the frame is drawn against, the brim's seat in it, and the shell's Y seam.
pub const INNER: [f64; 6] = [-104.5, 104.5, 0.0, 290.0, 0.0, 352.0];
pub const SEAT: f64 = 349.0;
pub const Y_JOINT: f64 = 200.0;
/// The air the funnel's forming envelope keeps.
pub const FORMING_AIR: f64 = 0.3;
/// The corbels that carry the roof: their half depth at the foot, and their slope.
pub const CORBEL_HALF_DEPTH: f64 = 27.5 + (funnel::FORWARD + funnel::AFT) / 2.0;

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
        floor: SEAT - ROOF_WEB,
        top: SEAT + funnel::BRIM_T,
    }
}

/// A screw in the frame's own frame: its X and Y, its head's seat above the underside, its
/// insert's host, its side, which shell holds it, and its row's name in the assembly.
pub type Screw = (f64, f64, f64, f64, f64, bool, &'static str);

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
    pub front_head_inside: f64,
    pub screws: Vec<Screw>,
    /// The back ledges' seats: the pocket flank they fall from, |X| in the frame's own frame,
    /// their rise per run, and the slip the frame's matching faces keep square to them. A back
    /// screw stands square to its seat; its head seat stands `back_screw_grip` from the seat.
    pub back_seat_flank: f64,
    pub back_seat_slope: f64,
    pub back_seat_air: f64,
    pub back_screw_grip: f64,
    pub body_half_width: f64,
    pub brim_half_size: P2,
    pub brim_radius: f64,
    pub drain_xy: P2,
    pub socket_size: P2,
    pub socket_radius: f64,
    pub socket_z: f64,
    pub socket_floor_z: f64,
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
    let floor = SEAT - funnel::DROP - cradle::WEB;
    let socket_floor_z = cradle::WEB + SOCKET_FLOOR_RISE;
    let r = roof();
    let snap = cradle::stations();
    let half = funnel::PLUG_W / 2.0;
    let gap = (2.0 * cradle::SOCKET_HALF - funnel::PLUG_W) / 2.0;
    let rear_limit = INNER[1] - interface::Y_STACK_HIGH_DEPTH - interface::slide_slip();
    let air = interface::funnel_collar_air();
    let host_radius = interface::HEATSET_DIA / 2.0 + interface::WALL;
    let head_seat = r.floor + SCREW_GRIP - floor;
    let screws: Vec<Screw> = funnel_mount::stations(r.front, r.back)
        .map(|s| (s.x - cx, s.y - cy, head_seat, host_radius, s.side, s.front, s.row))
        .collect();
    let body_half_width = screws.iter()
        .filter(|s| s.5)
        .map(|s| s.0.abs() - s.3 - interface::slide_slip())
        .reduce(f64::min)
        .expect("the frame's front screws");
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
        front_head_inside: funnel::COLLAR_W / 2.0 + funnel::OVERHANG + air,
        screws,
        back_seat_flank: INNER[1] - interface::Y_STACK_HIGH_DEPTH - cx,
        back_seat_slope: BACK_SEAT_SLOPE,
        back_seat_air: interface::fits::slip(),
        back_screw_grip: BACK_SCREW_GRIP,
        body_half_width,
        brim_half_size: (funnel::COLLAR_W / 2.0 + funnel::OVERHANG + air, funnel::COLLAR_D / 2.0 + funnel::OVERHANG + air),
        brim_radius: funnel::BRIM_R + air,
        drain_xy: (0.0, 0.0),
        socket_size: (2.0 * (half + gap), 2.0 * (funnel::plug_half_length(half) + gap)),
        socket_radius: cradle::SOCKET_CORNER,
        socket_z: cradle::WEB,
        socket_floor_z,
        socket_height: SOCKET_DEPTH,
        socket_flare: (2.0, 1.0),
        hole_radius: cradle::stem_passage_radius(),
        web_cut_z: (-1.0, socket_floor_z + 1.0),
        slot_x: (snap.slot_in, snap.slot_out),
        slot_y: (cradle::SLOT_FORE - cradle::END_SLIP, cradle::SLOT_AFT + cradle::END_SLIP),
        funnel: funnel::dimensions(),
        forming_air: FORMING_AIR,
        forming_clip_z: (socket_floor_z, SEAT - floor),
    }
}
