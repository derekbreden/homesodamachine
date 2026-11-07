//! The foam shell's own numbers, in millimetres, in the shell's frame: Z up from its base, X along
//! its length with the front wall at −X, the carbonator's axis on Z. They are the reservoir
//! pockets' walls, the carbonator's support ring, reservoir B's reed cable outlet, and the shell's
//! ports: the evaporator copper's feed-throughs and the CO2 inlet's reach. The casing's stock,
//! pockets, clamp stack and reed channels are the cold core's interface's, and the shell takes
//! them from there. The cold core's assemblies and its internal routes take the ports from here.
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as core;

// --- The reservoir pockets' walls --------------------------------------------------------------

/// Where each pocket's centreward wall hands off from its middle arc, which wraps the carbonator
/// and coil, to the transition arcs that swing it out to the pocket's ±Y walls.
pub const POCKET_CENTERWARD_ARC_TRANSITION_Y: f64 = 60.;
/// The middle arc's cavity face: the pockets' centreward arc.
pub const ARC_CAVITY_RADIUS: f64 = core::POCKET_CENTERWARD_ARC_OUTER_RADIUS;
/// The transition arcs' centre: along X the mating profile's datum, independent of the stock
/// outside the cavity; across Y halfway between the hand-off and the pocket's ±Y wall.
pub const TRANSITION_CENTER_X: f64 = 56.655020677894306;
pub const TRANSITION_CENTER_Y: f64 =
    (core::BAG_POCKET_Y_INNER_MAX + POCKET_CENTERWARD_ARC_TRANSITION_Y) / 2.;

/// Where the middle arc's cavity face hands off to the transition arcs, along X.
pub fn middle_cavity_x() -> f64 {
    (ARC_CAVITY_RADIUS.powi(2) - POCKET_CENTERWARD_ARC_TRANSITION_Y.powi(2)).sqrt()
}

/// A transition arc's cavity face: from its centre to both of its ends, the middle arc's and the
/// ±Y wall's, which stand at the same X.
pub fn transition_cavity_radius() -> f64 {
    let chord_half_y = (core::BAG_POCKET_Y_INNER_MAX - POCKET_CENTERWARD_ARC_TRANSITION_Y) / 2.;
    ((TRANSITION_CENTER_X - middle_cavity_x()).powi(2) + chord_half_y.powi(2)).sqrt()
}

/// A transition arc's apex, its cavity face's nearest reach toward the carbonator, along X.
pub fn transition_apex_x() -> f64 {
    TRANSITION_CENTER_X - transition_cavity_radius()
}

// --- The carbonator's support ring -------------------------------------------------------------

/// The ring the carbonator stands on: its outer face on the carbonator and coil envelope, its
/// inner face a ring's width in, its foot on the floor and its top under the carbonator's rim.
pub const SUPPORT_RING_OUTER_RADIUS: f64 = core::CARBONATOR_COIL_ENVELOPE_RADIUS;
pub const SUPPORT_RING_INNER_RADIUS: f64 = SUPPORT_RING_OUTER_RADIUS - core::SUPPORT_RING_RADIAL_WIDTH;
pub const SUPPORT_RING_BOTTOM_Z: f64 = core::WALL_AND_FLOOR_THICKNESS;
pub const SUPPORT_RING_TOP_Z: f64 = SUPPORT_RING_BOTTOM_Z + core::CARBONATOR_SUPPORT_RING_HEIGHT;
/// The slots the pour reaches the floor under the carbonator through, and each one's width in
/// degrees.
pub const SLOT_COUNT: usize = 4;
pub const SLOT_ANGULAR_WIDTH: f64 = 30.;
/// The slots stand between the diagonals, clocked off them by this many degrees, so the two lines
/// that cross the ring under the carbonator each cross inside one: the CO2's lean in from the
/// port lane, and the carbonated water's climb out.
pub const SLOT_CLOCK: f64 = -8.;
/// How far a slot's cutter overruns each of the ring's faces.
pub const SLOT_RADIAL_MARGIN: f64 = 1.;

/// Each slot's start and end, in degrees about +Z from +X.
pub fn slot_spans() -> [[f64; 2]; SLOT_COUNT] {
    std::array::from_fn(|i| {
        let centre = 360. / SLOT_COUNT as f64 * (i as f64 + 0.5) + SLOT_CLOCK;
        [centre - SLOT_ANGULAR_WIDTH / 2., centre + SLOT_ANGULAR_WIDTH / 2.]
    })
}

// --- Reservoir B's reed cable outlet -----------------------------------------------------------

/// Reservoir B's reed cable turns out of the top of its channel through a peaked window in the
/// front face, below the rim, before the top cap seats. The window drops this far below the
/// pockets' top, and its straight sides run on this far above it before its roof peaks across
/// the channel's width, which it prints over without support.
pub const REED_B_OUTLET_DEPTH: f64 = 6.;
pub const REED_B_OUTLET_SHOULDER_RISE: f64 = 0.25;
/// The window's axis: the reed column's, in plan.
pub const REED_B_OUTLET_AXIS: [f64; 2] = [-core::REED_COLUMN_AXIS_X, core::LEVEL_ROD_Y];
pub const REED_B_OUTLET_BOTTOM_Z: f64 = core::FOAM_SHELL_OUTER_HEIGHT - REED_B_OUTLET_DEPTH;
pub const REED_B_OUTLET_SHOULDER_Z: f64 = core::FOAM_SHELL_OUTER_HEIGHT + REED_B_OUTLET_SHOULDER_RISE;
pub const REED_B_OUTLET_PEAK_Z: f64 = REED_B_OUTLET_SHOULDER_Z + 2. * core::REED_Y_HALF_W;
/// The window's cutter runs from past the front face, by this much, to the reed column's axis;
/// the reed cavity stays behind the mouth.
pub const REED_B_OUTLET_OVERCUT: f64 = 1.;
pub const REED_B_OUTLET_MIN: [f64; 3] = [
    -core::OUTER_SHELL_X_LENGTH / 2. - REED_B_OUTLET_OVERCUT,
    REED_B_OUTLET_AXIS[1] - core::REED_Y_HALF_W,
    REED_B_OUTLET_BOTTOM_Z,
];
pub const REED_B_OUTLET_MAX: [f64; 3] =
    [REED_B_OUTLET_AXIS[0], REED_B_OUTLET_AXIS[1] + core::REED_Y_HALF_W, REED_B_OUTLET_PEAK_Z];

// --- The ports ---------------------------------------------------------------------------------

/// The round bore each evaporator copper tail passes the front wall through.
pub const COPPER_HOLE_RADIUS: f64 = 3.75;

/// A copper feed-through: the tail's name, where its axis crosses the front wall's datum, and the
/// way it points out of the shell.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CopperStation {
    pub name: &'static str,
    pub origin: [f64; 3],
    pub outward: [f64; 3],
}

/// The evaporator's two tails, straight out through the front wall: the inlet on the port lane,
/// the outlet on the west lane.
pub fn copper_stations() -> [CopperStation; 2] {
    let outward = [-1., 0., 0.];
    [
        CopperStation {
            name: "evap-inlet",
            origin: [core::FRONT_WALL_X, core::PORT_LANE_MID_Y, core::EVAP_CROSS_Z],
            outward,
        },
        CopperStation {
            name: "evap-outlet",
            origin: [core::FRONT_WALL_X, core::WEST_LANE_MID_Y, core::EVAP_CROSS_Z],
            outward,
        },
    ]
}

/// How far below the carbonator tube's bottom end the bottom plate's lines leave: the socket
/// axis of the push-fit male elbow each bottom port carries, its reach off the plate less the
/// plate's recess into the tube.
pub const BOTTOM_PORT_DROP: f64 = 11.2;
/// The height the bottom plate's two lines leave their elbows at, the carbonated water's outlet
/// and the CO2's inlet, one either side of the plate's axis in Y.
pub const FRONT_FACE_PORT_Z: f64 =
    core::WALL_AND_FLOOR_THICKNESS + core::CARBONATOR_SUPPORT_RING_HEIGHT - BOTTOM_PORT_DROP;
/// The CO2 inlet's reach: straight in from the port lane, where the line's fall lands, to the
/// bottom plate's lane-side port. It leans, so its lane end lands under the CO2's cap conduit
/// rather than on the shell's centreline, and crosses the support ring inside one slot.
pub const CO2_INLET_XYZ: [f64; 3] = [0., core::CO2_INLET_Y, FRONT_FACE_PORT_Z];
/// The reach's lane end, where the lean starts: on the CO2's column, this far inboard of the
/// copper lane's middle, clear of the clamp screws' hosts.
pub const CO2_LANE_INBOARD: f64 = 2.5;
pub const CO2_INLET_LANE_XYZ: [f64; 3] =
    [core::CO2_LANE_X, core::PORT_LANE_MID_Y + CO2_LANE_INBOARD, FRONT_FACE_PORT_Z];

/// The shell prints in black glass-filled PETG.
pub fn colour() -> catalog::Colour {
    catalog::petgf_black()
}
