//! The display let into the front facet: the face-up cover's receiver in display-local
//! coordinates (X across, Y up the slope, Z out of the face) and the frame that places it.
use crate::catalog::slip;
use crate::plan::{Bounds, Graph, P3, Shape};
use crate::shapes::{place, rounded, rounded_prism};
use crate::shell::SHOW_EDGE_R;
use crate::structure::profile;

const THICK: f64 = 3.84;
const WING_THICK: f64 = 1.44;
const BEARING_AIR: f64 = 0.60;
const COVER_X: f64 = 125.5;
const COVER_Y: f64 = 83.0;
const CORNER_R: f64 = 6.0;
const WING_REACH: f64 = 3.60;
const WING_SPAN: f64 = 70.0;
const BODY_X_AIR: f64 = 0.30;
const BODY_Y_AIR: f64 = 0.15;
const TIP_AIR: f64 = 0.55;
const END_AIR: f64 = 0.15;
const BACK: f64 = -THICK;
/// The glass's seat under the cover's back.
pub const GLASS_SEAT: f64 = -THICK - 2.0;
/// The wing pockets' exits lean down the slope at the facet's angle, so supports leave
/// through the empty storey under the display.
const EXIT_ANGLE: f64 = 30.0;
/// How deep the wing pockets' exits run.
const EXIT_DEPTH: f64 = 12.0;

/// The facet wall's depth, the display envelope's.
pub const FACET_THICKNESS: f64 = 19.0;
const BEZEL_DEPTH: f64 = 5.84;
const INSET_X: f64 = 113.5 + 2.0 * 6.3;
const INSET_SLOPE: f64 = 83.3;
const INSET_DEPTH: f64 = 3.84;

/// The PCB body's offset from the centred glass: across, and down the slope.
pub const BODY_OFFSET_X: f64 = 0.5;
pub const BODY_OFFSET_SLOPE: f64 = -1.0;

/// The PCB body's through-hole, across and up the slope, a slip each side.
pub fn pcb_x() -> f64 {
    106.0 + 2.0 * slip()
}
pub fn pcb_slope() -> f64 {
    69.0 + 2.0 * slip()
}

/// The PCB pocket's reach past the facet wall: the module behind the glass and a millimetre
/// behind its envelope.
pub fn pcb_cut_through() -> f64 {
    BEZEL_DEPTH + 17.0 + 1.0 - FACET_THICKNESS
}

fn inset_corner_r() -> f64 {
    SHOW_EDGE_R + slip()
}

/// The X the glass is centred on: the box's middle, since the facet runs wall to wall.
pub fn centre_x(outer: &Bounds) -> f64 {
    (outer[0] + outer[1]) / 2.0
}

/// The display plane's frame: its +X the box's, +Y up the slope, +Z out at the user.
pub fn frame(outer: &Bounds) -> ([P3; 3], P3) {
    let p = profile(outer);
    let [nx, ny, nz] = p.normal;
    assert!(nx.abs() <= 1e-10, "the front display plane no longer has its declared X direction");
    ([[1.0, 0.0, 0.0], [0.0, nz, ny], [0.0, -ny, nz]], [centre_x(outer), p.origin[1], p.origin[2]])
}

fn wing_x(side: f64) -> (f64, f64) {
    let (a, b) = (side * (COVER_X / 2.0 - 0.1), side * (COVER_X / 2.0 + WING_REACH + TIP_AIR));
    if a <= b { (a, b) } else { (b, a) }
}

/// Each wing pocket's exit, run `depth` down the slope from the wing's bearing roof.
fn support_exits(g: &mut Graph, depth: f64) -> [Shape; 2] {
    let roof = BACK + WING_THICK + BEARING_AIR;
    let shift = -depth * EXIT_ANGLE.to_radians().tan();
    [-1.0, 1.0].map(|side| {
        let (xa, xb) = wing_x(side);
        let (y0, y1) = (-WING_SPAN / 2.0 - END_AIR, WING_SPAN / 2.0 + END_AIR);
        g.yz_prism(xa, xb, vec![[y0, roof], [y0 + shift, roof - depth], [y1 + shift, roof - depth], [y1, roof]])
    })
}

/// The cover's inset, the glass seat, the PCB pocket and both wing pockets with their exits.
fn cuts(g: &mut Graph, pcb_depth: f64, exit_depth: f64) -> Shape {
    let inset = rounded_prism(g, COVER_X + 2.0 * BODY_X_AIR, COVER_Y + 2.0 * BODY_Y_AIR, CORNER_R + BODY_Y_AIR,
                              BACK, 1.0, 0.0, 0.0);
    let glass = rounded_prism(g, 113.8, 77.3, 2.65, GLASS_SEAT, 1.0, 0.0, 0.0);
    let pcb = g.box_([BODY_OFFSET_X - pcb_x() / 2.0, BODY_OFFSET_X + pcb_x() / 2.0, BODY_OFFSET_SLOPE - pcb_slope() / 2.0,
                      BODY_OFFSET_SLOPE + pcb_slope() / 2.0, -pcb_depth, 1.0]);
    let mut result = g.union(inset, &[glass, pcb]);
    for side in [-1.0, 1.0] {
        let (xa, xb) = wing_x(side);
        let pocket = g.box_([xa, xb, -WING_SPAN / 2.0 - END_AIR, WING_SPAN / 2.0 + END_AIR, BACK,
                             BACK + WING_THICK + BEARING_AIR]);
        result = g.union(result, &[pocket]);
    }
    let exits = support_exits(g, exit_depth);
    g.union(result, &exits)
}

/// The display's air in the facet, placed on the display plane; the wing exits run on below
/// the cover's inset to the facet wall's back.
pub fn display_cut(g: &mut Graph, outer: &Bounds) -> Shape {
    let (rotation, translation) = frame(outer);
    let mut local = cuts(g, FACET_THICKNESS + pcb_cut_through(), EXIT_DEPTH);
    let radius = inset_corner_r();
    let below = rounded(g, 2, [-INSET_X / 2.0, INSET_X / 2.0, -INSET_SLOPE / 2.0, INSET_SLOPE / 2.0,
                               -FACET_THICKNESS, -INSET_DEPTH], radius, &[0, 1, 2, 3]);
    for exit in support_exits(g, EXIT_DEPTH) {
        let shifted = g.translate(exit, [0.0, -radius, 0.0]);
        let run = g.intersect(below, &[shifted]);
        local = g.union(local, &[run]);
    }
    place(g, local, rotation, translation)
}

/// The wing pockets' cleanouts either side of the PCB, from under the exits' run up to a wall
/// under the glass seat, placed on the display plane.
pub fn cleanouts(g: &mut Graph, outer: &Bounds) -> [Shape; 2] {
    let (rotation, translation) = frame(outer);
    let reach = COVER_X / 2.0 + WING_REACH + TIP_AIR;
    let roof = GLASS_SEAT - crate::shell::WALL;
    let floor = BACK + WING_THICK + BEARING_AIR - EXIT_DEPTH;
    let y0 = -WING_SPAN / 2.0 - END_AIR - EXIT_DEPTH * EXIT_ANGLE.to_radians().tan();
    let y1 = WING_SPAN / 2.0 + END_AIR;
    let (pcb0, pcb1) = (BODY_OFFSET_X - pcb_x() / 2.0, BODY_OFFSET_X + pcb_x() / 2.0);
    [(-reach, pcb0 + 0.01), (pcb1 - 0.01, reach)].map(|(x0, x1)| {
        let air = g.box_([x0, x1, y0, y1, floor, roof]);
        place(g, air, rotation, translation)
    })
}
