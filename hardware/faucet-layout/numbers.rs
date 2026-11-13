//! The faucet assembly's numbers, in millimetres: the faucet and its umbilical as the bench bags
//! them, in the faucet's frame (+Z up, Z = 0 the above-counter plate's top). The Westbrass stands
//! on the plateau; the soda tube runs from its port up the gooseneck; the flavor pair, the drain
//! and the cable come down through the mounting stack and the countertop, step over to the
//! organizer, gather onto the soda umbilical in its foam, run the braided pack down, and splay to
//! the four square-cut tails the collars ride.
use hsm_faucet_numbers::countertop;
use hsm_faucet_numbers::interface::{DRAIN_TUBE_OD, FLAVOR_TUBE_DEPTH, FLAVOR_TUBE_X_OFFSET};
use hsm_faucet_numbers::paths::{FLAVOR_OD, LOWER_BUNDLE_X, RIBBON_DEPTH, RIBBON_WIDTH, WATER_Y};
use hsm_faucet_numbers::{P2, shell};
use hsm_tube_collar_numbers as collar;
use hsm_umbilical_organizer_numbers as organizer;

// The donor and the soda tube.

/// The Westbrass's water port, behind the shank: the water's centreline.
pub const PORT_CENTER_DEPTH: f64 = WATER_Y;
/// The plateau the donor stands its arches on.
pub const PLATEAU_Z: f64 = 39.0;
/// The donor's round body and its threaded shank.
pub const WESTBRASS_OD: f64 = 31.5;
pub const SHANK_OD: f64 = 11.0;
pub const SHANK_LENGTH: f64 = 50.0;
/// The 3/8" soda tube: how far it reaches into the port and above the plateau.
pub const SODA_FAUCET_TUBE_R: f64 = shell::SODA_FAUCET_TUBE_OD / 2.0;
pub const SODA_FAUCET_TUBE_INTO_PORT: f64 = 15.0;
pub const SODA_FAUCET_TUBE_ABOVE_PLATEAU: f64 = 40.0;
pub const SODA_FAUCET_TUBE_Z_BOTTOM: f64 = PLATEAU_Z - SODA_FAUCET_TUBE_INTO_PORT;
pub const SODA_FAUCET_TUBE_Z_TOP: f64 = PLATEAU_Z + SODA_FAUCET_TUBE_ABOVE_PLATEAU;
/// The flavor tubes.
pub const FLAVOR_TUBE_R: f64 = FLAVOR_OD / 2.0;
/// The drain tube and its bore.
pub const DRAIN_TUBE_R: f64 = DRAIN_TUBE_OD / 2.0;
pub const DRAIN_TUBE_R_IN: f64 = 2.5 / 2.0;
/// The drain's tightest bend.
pub const DRAIN_BEND_RADIUS: f64 = 25.0;

// Under the counter.

/// The under-counter plate's sheet, and where it sits under the slab.
pub const UNDER_COUNTER_PLATE_THICKNESS: f64 = hsm_under_counter_plate_numbers::THICKNESS;
pub const UNDER_COUNTER_PLATE_BOTTOM_Z: f64 = countertop::BOTTOM_Z - UNDER_COUNTER_PLATE_THICKNESS;
/// Where the tubes turn back under the thickest counter.
pub const MOUNT_RETURN_START_Z: f64 = (countertop::TOP_Z - countertop::MAX_THICKNESS) - UNDER_COUNTER_PLATE_THICKNESS;
pub const MOUNT_RETURN_LEAD: f64 = UNDER_COUNTER_PLATE_BOTTOM_Z - MOUNT_RETURN_START_Z;
/// The flavor pair's step over to the organizer.
pub const STEP_BEND_RADIUS: f64 = 30.0;
/// The organizer under the stack: its top, its bottom, the gap below it and where the tubes
/// leave it.
pub const ORGANIZER_TOP_Z: f64 = -88.0;
pub const ORGANIZER_BOTTOM_Z: f64 = ORGANIZER_TOP_Z - organizer::LENGTH;
pub const ORGANIZER_GATHER_GAP: f64 = 7.0;
pub const ORGANIZER_RETURN_START_Z: f64 = ORGANIZER_BOTTOM_Z - 3.0;

// The umbilical.

/// The CARGEN foam on the soda umbilical.
pub const FOAM_OD: f64 = 25.4;
pub const FOAM_R: f64 = FOAM_OD / 2.0;
/// The drain's tail, in the pack and where it passes the organizer.
pub const DRAIN_TAIL_X: f64 = 0.0;
pub const DRAIN_BYPASS_Y: f64 = 8.9;
/// The gather's and the splay's bends.
pub const UMBILICAL_BEND_RADIUS: f64 = 30.0;
pub const SPLAY_BEND_RADIUS: f64 = 30.0;
/// The blue soda umbilical as cut, and how much is drawn past the counter.
pub const BLUE_CUT_LENGTH: f64 = 1540.0;
pub const UMBILICAL_DRAWN: f64 = 300.0;
pub const SODA_UMBILICAL_TUBE_OD: f64 = 6.35;
pub const SODA_UMBILICAL_TUBE_R: f64 = SODA_UMBILICAL_TUBE_OD / 2.0;
pub const SODA_UMBILICAL_TUBE_Z_TOP: f64 = -SHANK_LENGTH;
pub const UMBILICAL_TAIL_Z: f64 = SODA_UMBILICAL_TUBE_Z_TOP - UMBILICAL_DRAWN;
/// The foam is bare at the wall, where the installer's trim takes a segment.
pub const FOAM_BARE_AT_WALL: f64 = 75.0;
pub const FOAM_Z_BOTTOM: f64 = UMBILICAL_TAIL_Z + FOAM_BARE_AT_WALL;
/// The cable lane through the bundle, and the cable's width.
pub const CABLE_LANE: f64 = RIBBON_DEPTH;
pub const CABLE_WIDTH: f64 = RIBBON_WIDTH;
/// The PET braid over the pack.
pub const SLEEVE_WALL: f64 = 1.0;
pub const SLEEVE_Z_TOP: f64 = ORGANIZER_TOP_Z;
pub const SLEEVE_Z_BOTTOM: f64 = FOAM_Z_BOTTOM;
pub const SPLAY_TOP_Z: f64 = SLEEVE_Z_BOTTOM;
/// The air between neighbouring collars.
pub const COLLAR_AIR: f64 = 2.0;

// The lever, the base's fasteners and the display.

/// The lever's top, and its back at rest.
pub const LEVER_TOP_Z: f64 = PLATEAU_Z + 13.0;
pub const LEVER_AFT_Y: f64 = 9.0;
/// The M3 socket screws under the base, and the heat-set inserts' bore.
pub const BASE_SCREW_SHAFT_R: f64 = 1.5;
pub const BASE_SCREW_HEAD_R: f64 = 2.75;
pub const BASE_SCREW_SOCKET_AF: f64 = 2.5;
pub const BASE_SCREW_SOCKET_DEPTH: f64 = 1.6;
pub const BASE_SCREW_SOCKET_BELOW: f64 = 0.1;
pub const BASE_INSERT_INNER_R: f64 = 1.5;
/// The height over which the signal ribbon eases under the display's PCB.
pub const RIBBON_BLEND_HEIGHT: f64 = 0.35;
/// The display's glass, under its recess in the housing.
pub const DISPLAY_SCREEN_WIDTH: f64 = 17.75;
pub const DISPLAY_SCREEN_LENGTH: f64 = 32.93;
pub const DISPLAY_SCREEN_DEPTH: f64 = 0.4;
pub const DISPLAY_SCREEN_CORNER_R: f64 = 2.0;
/// The display's vendor model's components and buttons.
pub const DISPLAY_COMPONENTS: &str = "hardware/reference/touch-flo-faucet/display-reference/component-envelopes.json";
pub const DISPLAY_BUTTONS: &str = "hardware/reference/touch-flo-faucet/display-reference/buttons.json";
pub const DISPLAY_REFERENCE: &str = "hardware/reference/touch-flo-faucet/display-reference";
/// The lever's own bounds in its part frame, which seat it.
pub const LEVER_FRAME: &str = "hardware/printed-parts/faucet/lever-replica/lever-replica.frame.json";

/// A flavor tube's mounting X, `s` its side.
pub fn flavor_mount_x(s: f64) -> f64 {
    LOWER_BUNDLE_X + s * FLAVOR_TUBE_X_OFFSET
}

/// Where a flavor tube comes back to after the organizer, in X.
pub fn return_x(s: f64) -> f64 {
    s * FLAVOR_TUBE_X_OFFSET
}

/// An organizer passage's axis.
pub fn organizer_axis(name: &str) -> P2 {
    organizer::BORES.iter().find(|(n, _, _)| *n == name).map(|(_, xy, _)| *xy).expect("an organizer passage")
}

/// The flavor tube's passage through the organizer.
pub fn organizer_flavor_xy(s: f64) -> P2 {
    organizer_axis(if s > 0.0 { "F1" } else { "F2" })
}

fn d2(a: P2, b: P2) -> f64 {
    (a[0] - b[0]).hypot(a[1] - b[1])
}

/// A flavor tube's step over to the organizer: the angle of each of its two bends.
pub fn step_theta(s: f64) -> f64 {
    let offset = d2(organizer_flavor_xy(s), [return_x(s), FLAVOR_TUBE_DEPTH]);
    (1.0 - offset / (2.0 * STEP_BEND_RADIUS)).acos()
}

/// The steeper step's rise.
pub fn step_rise() -> f64 {
    2.0 * STEP_BEND_RADIUS * step_theta(1.0).max(step_theta(-1.0)).sin()
}

/// The flavor pair's depth in the pack, tight round the foam.
pub fn pack_flavor_depth() -> f64 {
    ((FOAM_R + FLAVOR_TUBE_R).powi(2) - FLAVOR_TUBE_X_OFFSET.powi(2)).sqrt()
}

/// The drain's Y in the pack, tight round the foam.
pub fn drain_pack_y() -> f64 {
    -((FOAM_R + DRAIN_TUBE_R).powi(2) - DRAIN_TAIL_X.powi(2)).sqrt()
}

/// The drain's tail in Y.
pub fn drain_tail_y() -> f64 {
    drain_pack_y() - 20.0
}

/// The rise of an S-bend of two arcs of radius `r` that steps `offset` sideways.
fn s_rise(offset: f64, r: f64) -> f64 {
    2.0 * r * (1.0 - offset / (2.0 * r)).acos().sin()
}

/// Where the tubes start gathering onto the umbilical.
pub fn gather_start_z() -> f64 {
    let drain_rise = s_rise(d2([DRAIN_TAIL_X, DRAIN_BYPASS_Y], organizer_axis("D")), DRAIN_BEND_RADIUS);
    (ORGANIZER_RETURN_START_Z - step_rise().max(drain_rise)) - ORGANIZER_GATHER_GAP
}

/// A flavor tube's gather onto the pack: how far it steps, the angle of its bends and its rise.
pub fn gather_offset(s: f64) -> f64 {
    (s * FLAVOR_TUBE_X_OFFSET - return_x(s)).hypot(pack_flavor_depth() - FLAVOR_TUBE_DEPTH)
}

pub fn gather_theta(s: f64) -> f64 {
    (1.0 - gather_offset(s) / (2.0 * UMBILICAL_BEND_RADIUS)).acos()
}

pub fn gather_rise(s: f64) -> f64 {
    2.0 * UMBILICAL_BEND_RADIUS * gather_theta(s).sin()
}

/// Where the pack starts below the gather.
pub fn umbilical_z_bottom() -> f64 {
    let drain = s_rise((drain_pack_y() - DRAIN_BYPASS_Y).abs(), DRAIN_BEND_RADIUS);
    gather_start_z() - gather_rise(1.0).max(gather_rise(-1.0)).max(drain)
}

/// The foam's top, where the pack starts.
pub fn foam_z_top() -> f64 {
    umbilical_z_bottom()
}

/// How far apart two tails stand so their collars pass, and each flavor tail's X.
pub fn tail_half_x() -> f64 {
    let clear = 2.0 * (collar::OD / 2.0).hypot(collar::RISE) + COLLAR_AIR;
    (clear / 2.0).max(0.0_f64.max(clear.powi(2) - pack_flavor_depth().powi(2)).sqrt())
}

/// The splay's bends out to the tails, and its rise.
pub fn splay_theta() -> f64 {
    (1.0 - (tail_half_x() - FLAVOR_TUBE_X_OFFSET) / (2.0 * SPLAY_BEND_RADIUS)).acos()
}

pub fn splay_rise() -> f64 {
    2.0 * SPLAY_BEND_RADIUS * splay_theta().sin()
}

/// Where the collars' tops sit, below the splay's.
pub fn collar_top_z() -> f64 {
    let drain = s_rise((drain_tail_y() - drain_pack_y()).abs(), DRAIN_BEND_RADIUS);
    SPLAY_TOP_Z - splay_rise().max(drain)
}

/// The four tails the collars ride: each collar's station and its tail's place.
pub fn collar_tails() -> [(&'static str, f64, f64); 4] {
    [
        ("carb", 0.0, 0.0),
        ("flavor-a", tail_half_x(), pack_flavor_depth()),
        ("flavor-b", -tail_half_x(), pack_flavor_depth()),
        ("drain", DRAIN_TAIL_X, drain_tail_y()),
    ]
}

/// The pack's circles, `[x, y, r]`, grown `g`: the foam, the flavor pair and the drain.
pub fn bundle_circles(g: f64) -> Vec<[f64; 3]> {
    vec![
        [0.0, 0.0, FOAM_R + g],
        [FLAVOR_TUBE_X_OFFSET, pack_flavor_depth(), FLAVOR_TUBE_R + g],
        [-FLAVOR_TUBE_X_OFFSET, pack_flavor_depth(), FLAVOR_TUBE_R + g],
        [DRAIN_TAIL_X, drain_pack_y(), DRAIN_TUBE_R + g],
    ]
}

/// The bare tubes' circles below the organizer, grown `g`.
pub fn bare_circles(g: f64) -> Vec<[f64; 3]> {
    vec![
        [0.0, 0.0, SODA_UMBILICAL_TUBE_R + g],
        [return_x(1.0), FLAVOR_TUBE_DEPTH, FLAVOR_TUBE_R + g],
        [return_x(-1.0), FLAVOR_TUBE_DEPTH, FLAVOR_TUBE_R + g],
        [DRAIN_TAIL_X, DRAIN_BYPASS_Y, DRAIN_TUBE_R + g],
    ]
}

/// The gather's circles, grown `g`: everything the braid passes over through the gather, less any
/// circle another holds.
pub fn gather_circles(g: f64) -> Vec<[f64; 3]> {
    let mut c = vec![[0.0, 0.0, FOAM_R + g]];
    for [x, y] in [
        [return_x(1.0), FLAVOR_TUBE_DEPTH],
        [return_x(-1.0), FLAVOR_TUBE_DEPTH],
        [FLAVOR_TUBE_X_OFFSET, pack_flavor_depth()],
        [-FLAVOR_TUBE_X_OFFSET, pack_flavor_depth()],
    ] {
        c.push([x, y, FLAVOR_TUBE_R + g]);
    }
    for y in [drain_pack_y(), DRAIN_BYPASS_Y] {
        c.push([DRAIN_TAIL_X, y, DRAIN_TUBE_R + g]);
    }
    c.iter()
        .enumerate()
        .filter(|(i, q)| !c.iter().enumerate().any(|(j, o)| j != *i && (q[0] - o[0]).hypot(q[1] - o[1]) + q[2] <= o[2] + 1e-9))
        .map(|(_, v)| *v)
        .collect()
}
