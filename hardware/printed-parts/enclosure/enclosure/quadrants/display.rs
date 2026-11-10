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

/// The X the glass is centred on: the box's middle, moved by the display's slide toward −X, which
/// leaves the facet's far run to the status plate.
pub fn centre_x(outer: &Bounds) -> f64 {
    (outer[0] + outer[1]) / 2.0 + mount::SLIDE_X
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
    for [x, y] in mount::STATIONS.into_iter().chain(mount::STATUS_STATIONS) {
        let pilot = g.zcyl(mount::PILOT_DIA / 2.0, x, y, BACK - mount::PILOT_DEPTH, BACK + 0.01);
        result = g.union(result, &[pilot]);
    }
    let status = status_cuts(g);
    g.union(result, &[status])
}

/// The round lamp pocket and its diamond lead channel share their lower faces.
fn status_cuts(g: &mut Graph) -> Shape {
    let seat = rounded_prism(g, mount::STATUS_WIDTH + 2.0 * BODY_X_AIR, mount::STATUS_HEIGHT + 2.0 * BODY_Y_AIR,
                             mount::CORNER + BODY_Y_AIR, BACK, 1.0, mount::STATUS_CX, 0.0);
    let tilt = crate::structure::ANGLE.to_radians();
    let (up, across) = ([tilt.sin(), tilt.cos()], [tilt.cos(), -tilt.sin()]);
    // Expanding down from the retained roof planes deepens the bottom without a roof step.
    let expansion = mount::LED_POCKET_DEPTH / (2.0 * up[1]);
    let r = mount::LEAD_HALF_SPAN + expansion;
    let c = [
        mount::LIGHT_Y - expansion * up[0],
        GLASS_SEAT - mount::BACKING - mount::LEAD_HALF_SPAN * up[1] - expansion * up[1],
    ];
    let section = vec![
        [c[0] + r * up[0], c[1] + r * up[1]],
        [c[0] + r * across[0], c[1] + r * across[1]],
        [c[0] - r * up[0], c[1] - r * up[1]],
        [c[0] - r * across[0], c[1] - r * across[1]],
    ];
    let radius = mount::LED_BORE_DIA / 2.0;
    let cylinder = g.zcyl(radius, mount::STATUS_CX, mount::LIGHT_Y, section[2][1] - 0.01, BACK + 0.01);
    let above_floor = g.prism(0, mount::STATUS_CX - radius - 0.01, mount::STATUS_CX + radius + 0.01, vec![
        section[3], section[2], section[1],
        [section[1][0], BACK + 0.01], [section[3][0], BACK + 0.01],
    ]);
    let bore = g.intersect(cylinder, &[above_floor]);
    let bore = g.feature(bore, "status-led-bore", "Status LED bulb pocket", &["status-plate"]);
    let pcb_edge = BODY_OFFSET_X + pcb_x() / 2.0;
    let channel = g.prism(0, pcb_edge - 1.0, mount::STATUS_CX, section);
    let channel = g.feature(channel, "status-led-wire-channel", "Status LED lead channel", &["status-plate"]);
    g.union(seat, &[bore, channel])
}

/// The display and its side-screw pilots, placed on the display plane.
pub fn display_cut(g: &mut Graph, outer: &Bounds) -> Shape {
    let (rotation, translation) = frame(outer);
    let local = cuts(g, FACET_THICKNESS + pcb_cut_through());
    place(g, local, rotation, translation)
}
