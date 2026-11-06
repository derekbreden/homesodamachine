//! The display let into the front facet: the screw-mounted cover's receiver in display-local
//! coordinates (X across, Y up the slope, Z out of the face) and the frame that places it.
use crate::catalog::slip;
use crate::plan::{Bounds, Graph, P3, Shape};
use crate::shapes::{place, rounded_prism};
use crate::structure::profile;
use hsm_enclosure_numbers::display_mount as mount;

const BODY_X_AIR: f64 = 0.30;
const BODY_Y_AIR: f64 = 0.15;
const BACK: f64 = -mount::THICK;
/// The glass's seat under the cover's back.
pub const GLASS_SEAT: f64 = BACK - mount::GASKET_THICK - mount::GLASS_THICK;

/// The facet wall's depth, the display envelope's.
pub const FACET_THICKNESS: f64 = 19.0;
const BEZEL_DEPTH: f64 = -GLASS_SEAT;

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

/// The cover's inset, retained glass seat, PCB pocket and blind insert pilots.
fn cuts(g: &mut Graph, pcb_depth: f64) -> Shape {
    let inset = rounded_prism(g, mount::WIDTH + 2.0 * BODY_X_AIR, mount::HEIGHT + 2.0 * BODY_Y_AIR, mount::CORNER + BODY_Y_AIR,
                              BACK, 1.0, 0.0, 0.0);
    let glass = rounded_prism(g, 113.8, 77.3, 2.65, GLASS_SEAT, 1.0, 0.0, 0.0);
    let pcb = g.box_([BODY_OFFSET_X - pcb_x() / 2.0, BODY_OFFSET_X + pcb_x() / 2.0, BODY_OFFSET_SLOPE - pcb_slope() / 2.0,
                      BODY_OFFSET_SLOPE + pcb_slope() / 2.0, -pcb_depth, 1.0]);
    let mut result = g.union(inset, &[glass, pcb]);
    for [x, y] in mount::STATIONS {
        let pilot = g.zcyl(mount::PILOT_DIA / 2.0, x, y, BACK - mount::PILOT_DEPTH, BACK + 0.01);
        result = g.union(result, &[pilot]);
    }
    result
}

/// The display and its side-screw pilots, placed on the display plane.
pub fn display_cut(g: &mut Graph, outer: &Bounds) -> Shape {
    let (rotation, translation) = frame(outer);
    let local = cuts(g, FACET_THICKNESS + pcb_cut_through());
    place(g, local, rotation, translation)
}
