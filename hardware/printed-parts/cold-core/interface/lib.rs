//! The cold core's interface: what its casing presents to the parts that mate with it, without
//! building the casing. The casing's stock and cavity envelope, the reservoirs' ports, the cap's
//! clamp stack and attachment stations, the carbonator's port datums, the lanes the lines run
//! in, and the cap's conduits, anchors and side anchors. The cold core's own recipes and every
//! part that meets the casing take them from here.
//!
//! A number cut to a printed fit takes the fit as an argument, from the shared fits catalog the
//! caller reads.

use hsm_carbonator_tube_numbers as tube;

/// The shared fits a printed face is cut to.
#[derive(Clone, Copy, Debug)]
pub struct Fits {
    /// Head-on seats.
    pub slip: f64,
    /// Faces that slide past their mates.
    pub running: f64,
    /// A face printed over support.
    pub supported_surface: f64,
    /// The printed passage a fully threaded M5 screw takes.
    pub m5_thread_pass_dia: f64,
}

// --- The carbonator and the casing round it ---------------------------------------------------

/// The carbonator vessel the casing is cut round: its tube's outer radius and length.
pub const CARBONATOR_OUTER_RADIUS: f64 = tube::OUTER_RADIUS;
pub const CARBONATOR_HEIGHT: f64 = tube::LENGTH;
/// The casing's printed wall and floor.
pub const WALL_THICKNESS: f64 = 2.38;
pub const FLOOR_THICKNESS: f64 = 2.;
pub const WALL_AND_FLOOR_THICKNESS: f64 = FLOOR_THICKNESS;
/// How far a port's axis stands in from the face it leaves.
pub const HOLE_SHIFT_FROM_EDGE: f64 = 15.;
pub const OUTER_SHELL_WALL: f64 = WALL_THICKNESS;
/// The evaporator coil's air round the vessel, and the envelope it winds in.
pub const COIL_RADIAL_CLEARANCE: f64 = 7.;
pub const CARBONATOR_COIL_ENVELOPE_RADIUS: f64 = CARBONATOR_OUTER_RADIUS + COIL_RADIAL_CLEARANCE;
/// The reservoir pockets' centreward arc, and the foam it leaves round the vessel.
pub const POCKET_CENTERWARD_ARC_OUTER_RADIUS: f64 = 80.5;
pub const FOAM_THICKNESS_AROUND_CYLINDER: f64 =
    POCKET_CENTERWARD_ARC_OUTER_RADIUS - WALL_THICKNESS - CARBONATOR_OUTER_RADIUS;
/// The bands below and above the vessel its elbows turn in, and the foam shell's height.
pub const BELOW_CARBONATOR_ELBOWS_HEIGHT: f64 = 30.;
pub const ABOVE_CARBONATOR_ELBOWS_HEIGHT: f64 = 30.;
pub const FOAM_SHELL_OUTER_HEIGHT: f64 =
    CARBONATOR_HEIGHT + BELOW_CARBONATOR_ELBOWS_HEIGHT + ABOVE_CARBONATOR_ELBOWS_HEIGHT + 1.;
/// The ring the vessel stands on.
pub const CARBONATOR_SUPPORT_RING_HEIGHT: f64 = 30.;
pub const SUPPORT_RING_RADIAL_WIDTH: f64 = 9.;
/// The measured tube every shell penetration passes, and the bore it takes.
pub const PASSAGE_TUBE_OD: f64 = 6.5;
pub const PORT_HOLE_RADIUS: f64 = PASSAGE_TUBE_OD / 2. + 0.5;
/// A reed channel's depth and half-width, and the float rod's station.
pub const REED_X_DEPTH: f64 = 6.;
pub const REED_Y_HALF_W: f64 = 4.;
pub const LEVEL_ROD_Y: f64 = 32.5;

// --- The reservoir pockets ---------------------------------------------------------------------

/// A bag pocket's inner reach along X and across Y, and the pocket they make.
pub const BAG_POCKET_FAR_INNER_X: f64 = 129.5;
pub const BAG_POCKET_Y_INNER_MAX: f64 = 70.5;
pub const BAG_POCKET_WIDTH: f64 = 2. * (BAG_POCKET_Y_INNER_MAX + WALL_THICKNESS);
pub const BAG_POCKET_DEPTH: f64 =
    BAG_POCKET_FAR_INNER_X - POCKET_CENTERWARD_ARC_OUTER_RADIUS + 2. * WALL_THICKNESS;
pub const BAG_POCKET_FLOOR_TOP_Z: f64 = FLOOR_THICKNESS;
pub const BAG_POCKET_WALLS_TOP_Z: f64 = FOAM_SHELL_OUTER_HEIGHT;
/// The reed channel's inner face, and the reed column's axis off it.
pub const REED_CHANNEL_INNER_X: f64 = 131.5;
pub const REED_COLUMN_AXIS_X: f64 = REED_CHANNEL_INNER_X + REED_X_DEPTH / 2.;

// --- The reed channels -------------------------------------------------------------------------

/// The reeds each reservoir's channel holds, one above another.
pub const REEDS_PER_RESERVOIR: usize = 4;
/// The channel's axis across Y: the float rod's station.
pub const REED_Y_CENTER: f64 = LEVEL_ROD_Y;
/// The reed cavity across Y, and the envelope its walls make round it.
pub const REED_CAVITY_Y_RANGE: [f64; 2] = [REED_Y_CENTER - REED_Y_HALF_W, REED_Y_CENTER + REED_Y_HALF_W];
pub const REED_ENVELOPE_Y_RANGE: [f64; 2] =
    [REED_CAVITY_Y_RANGE[0] - WALL_THICKNESS, REED_CAVITY_Y_RANGE[1] + WALL_THICKNESS];

/// Up the shell: the cavity from the floor's top to the rim, the envelope from the base.
pub fn reed_cavity_z_range(fits: &Fits) -> [f64; 2] {
    [WALL_AND_FLOOR_THICKNESS, foam_shell_rim_z(fits)]
}

pub fn reed_envelope_z_range(fits: &Fits) -> [f64; 2] {
    [0., foam_shell_rim_z(fits)]
}

/// The reservoir slides into its pocket on the running fit.
pub fn reservoir_clearance(fits: &Fits) -> f64 {
    fits.running
}

pub fn bag_pocket_corner_inner_radius(fits: &Fits) -> f64 {
    6. + reservoir_clearance(fits)
}

pub const RESERVOIR_FLOOR_THICKNESS: f64 = 3.;
/// Each reservoir's fill and draw ports in the shell's frame, by side.
pub const RESERVOIR_FILL_PORT: [(i64, [f64; 2]); 2] = [(-1, [-90.5, 43.5]), (1, [102.5, -61.])];
pub const RESERVOIR_FILL_SIDES: [i64; 2] = [-1, 1];
pub const RESERVOIR_DRAW_PORT: [(i64, [f64; 2]); 2] = [(-1, [-94.3, 6.]), (1, [84.2, -45.])];

/// A side's port off one of the tables above.
pub fn reservoir_port(ports: &[(i64, [f64; 2])], side: i64) -> Option<[f64; 2]> {
    ports.iter().find(|(s, _)| *s == side).map(|(_, xy)| *xy)
}

// --- The outer shell ---------------------------------------------------------------------------

/// The foil the casing is wrapped in, and the land it laps.
pub const CASING_FOIL_ALLOWANCE: f64 = 0.30;
pub const CASING_FOIL_LAND: f64 = 13.;
/// The outer shell's footprint.
pub const OUTER_SHELL_X_LENGTH: f64 = 282.4;
pub const OUTER_SHELL_Y_LENGTH: f64 = 180.4;
/// The seam channel a line runs in along a joint face.
pub const SEAM_CHANNEL_LAND: f64 = 1.;
pub const SEAM_CHANNEL_WIDTH: f64 = 2. * (PORT_HOLE_RADIUS + SEAM_CHANNEL_LAND);
pub const SEAM_CHANNEL_DEPTH: f64 = 1.5;
pub const BAG_POCKET_OUTERMOST_X: f64 = BAG_POCKET_FAR_INNER_X + WALL_THICKNESS;
/// The foam between the outer shell and the pockets, across Y and in the forward band.
pub const OUTER_SHELL_FOAM_GAP: f64 =
    OUTER_SHELL_Y_LENGTH / 2. - OUTER_SHELL_WALL - BAG_POCKET_WIDTH / 2.;
pub const FORWARD_BAND_WIDTH: f64 =
    OUTER_SHELL_X_LENGTH / 2. - OUTER_SHELL_WALL - BAG_POCKET_OUTERMOST_X;
pub const FORWARD_BAND_MID_X: f64 = BAG_POCKET_OUTERMOST_X + FORWARD_BAND_WIDTH / 2.;
/// The pour band's two faces.
pub const POUR_BAND_POCKET_SIDE_Y: f64 = -(BAG_POCKET_WIDTH / 2.);
pub const POUR_BAND_SHELL_SIDE_Y: f64 = -(OUTER_SHELL_Y_LENGTH / 2. - OUTER_SHELL_WALL);

// --- The caps ----------------------------------------------------------------------------------

/// The foam cap's interior and its height over the floor.
pub const FOAM_CAP_INTERIOR_HEIGHT: f64 = 16.;
pub const FOAM_CAP_HEIGHT: f64 = FOAM_CAP_INTERIOR_HEIGHT + WALL_AND_FLOOR_THICKNESS;
/// The lid's pour and vent holes, the pour's inset from the shell's end, and the vent's setback.
pub const FOAM_CAP_LID_POUR_RADIUS: f64 = 10.;
pub const FOAM_CAP_LID_VENT_RADIUS: f64 = 3.;
pub const FOAM_CAP_LID_HOLE_INSET: f64 = 30.;
pub const TOP_LID_POUR_XY: [f64; 2] = [OUTER_SHELL_X_LENGTH / 2. - FOAM_CAP_LID_HOLE_INSET, -73.];
pub const TOP_LID_VENT_SETBACK: f64 = 2.5;

// --- The carbonator's ports --------------------------------------------------------------------

/// The ports' offset off the vessel's axis, the level sensor's azimuth and axis, and the float's
/// top stop.
pub const CARBONATOR_PORT_OFFSET: f64 = 0.750 * 25.4;
pub const CARBONATOR_SENSOR_AZIMUTH: f64 = -90.;
pub const CARBONATOR_SENSOR_AXIS: [f64; 2] = [0., -1.];
pub const CARBONATOR_FLOAT_TOP_STOP_HEIGHT: f64 = 4.;
pub const CARBONATOR_FLOAT_TOP_STOP_DIAMETER: f64 = 9.5;
pub const CO2_INLET_Y: f64 = -CARBONATOR_PORT_OFFSET;
pub const CO2_INLET_TUBE_RADIUS: f64 = PORT_HOLE_RADIUS;
pub const WATER_INLET_PORT_Y: f64 = -CARBONATOR_PORT_OFFSET;
pub const PRV_PORT_Y: f64 = CARBONATOR_PORT_OFFSET;

// --- The clamp stack ---------------------------------------------------------------------------

/// Each cap seats on the shell, and the lid on the cap, on the slip fit.
pub fn cap_shell_clearance(fits: &Fits) -> f64 {
    fits.slip
}

pub fn cap_lid_clearance(fits: &Fits) -> f64 {
    fits.slip
}

/// The M5 clamp screw's passage.
pub fn screw_clearance_radius(fits: &Fits) -> f64 {
    fits.m5_thread_pass_dia / 2.
}

/// The heat-set insert's pocket, the boss round it and the guard over it.
pub const INSERT_POCKET_RADIUS: f64 = 3.2;
pub const INSERT_POCKET_DEPTH: f64 = 10.5;
pub const SCREW_BOSS_SIZE: f64 = 11.6;
pub const SCREW_GUARD_DIAMETER: f64 = SCREW_BOSS_SIZE;
/// The screw's head, the recess it seats in, its counterbore and the pad under it.
pub const SCREW_HEAD_HEIGHT: f64 = 5.;
pub const HEAD_CBORE_RADIUS: f64 = 4.5;

pub fn head_seat_recess(fits: &Fits) -> f64 {
    fits.slip
}

pub fn head_cbore_depth(fits: &Fits) -> f64 {
    SCREW_HEAD_HEIGHT + head_seat_recess(fits)
}

pub fn head_pad_height(fits: &Fits) -> f64 {
    head_cbore_depth(fits) + fits.supported_surface
}

pub fn head_pad_slip(fits: &Fits) -> f64 {
    fits.slip
}

/// The lid's height, its underside, the shell's rim under it, and the bottom cap's height.
pub fn foam_cap_lid_height(fits: &Fits) -> f64 {
    WALL_AND_FLOOR_THICKNESS + head_pad_height(fits)
}

pub fn top_lid_bottom_z(fits: &Fits) -> f64 {
    FOAM_SHELL_OUTER_HEIGHT + FOAM_CAP_HEIGHT - head_pad_height(fits)
}

pub fn foam_shell_rim_z(fits: &Fits) -> f64 {
    top_lid_bottom_z(fits) - cap_lid_clearance(fits)
}

pub fn bottom_cap_height(fits: &Fits) -> f64 {
    FOAM_CAP_HEIGHT + WALL_AND_FLOOR_THICKNESS - cap_shell_clearance(fits)
}

/// The bottom cap's pour holes.
pub const BOTTOM_POUR_RADIUS: f64 = 15.;

pub fn bottom_pour_positions() -> Vec<[f64; 2]> {
    [-75., 75.].iter().flat_map(|x| [-40., 40.].map(|y| [*x, y])).collect()
}

// --- The lanes ---------------------------------------------------------------------------------

/// The front wall's datum, the port lane's two faces and its middle, the west lane's middle, and
/// the evaporator tails' two heights.
pub const FRONT_WALL_X: f64 = -141.5;
pub const PORT_LANE_OUTER_Y: f64 = -82.5;
pub const PORT_LANE_INNER_Y: f64 = -72.5;
pub const PORT_LANE_MID_Y: f64 = (PORT_LANE_OUTER_Y + PORT_LANE_INNER_Y) / 2.;
pub const WEST_LANE_MID_Y: f64 = -PORT_LANE_MID_Y;
pub const EVAP_TAIL_LOW_Z: f64 =
    HOLE_SHIFT_FROM_EDGE + WALL_AND_FLOOR_THICKNESS + BELOW_CARBONATOR_ELBOWS_HEIGHT;
pub const EVAP_TAIL_HIGH_Z: f64 = FOAM_SHELL_OUTER_HEIGHT
    - HOLE_SHIFT_FROM_EDGE
    - WALL_AND_FLOOR_THICKNESS
    - ABOVE_CARBONATOR_ELBOWS_HEIGHT;
/// The casing's corner round.
pub const CORNER_ROUND_RADIUS: f64 = 11.7;

// --- The attachment stations -------------------------------------------------------------------

/// The walls the clamp bosses stand on, and the middle screws' offset.
pub const BOSS_WALL_Y: f64 = 84.4;
pub const BOSS_WALL_X: f64 = 135.4;
pub const MID_SCREW_X_OFFSET: f64 = 45.;

/// The clamp screws' stations, each with the wall, `"x"` or `"y"`, its boss stands on.
pub fn attachment_stations() -> Vec<([f64; 2], &'static str)> {
    let mut stations = vec![];
    for x in [-BOSS_WALL_X, BOSS_WALL_X] {
        for y in [-60., 0., 60.] {
            stations.push(([x, y], "x"));
        }
    }
    for x in [45., 110.] {
        for y in [-BOSS_WALL_Y, BOSS_WALL_Y] {
            stations.push(([x, y], "y"));
        }
    }
    stations
}

/// The same stations in the lid's frame: the lid installs spun a half turn.
pub fn lid_attachment_stations() -> Vec<([f64; 2], &'static str)> {
    attachment_stations().iter().map(|(xy, wall)| ([-xy[0], -xy[1]], *wall)).collect()
}

/// The clamp screw, the insert it reaches, and how far it reaches past each face.
pub const CAP_SCREW_LENGTH: f64 = 100.;
pub const INSERT_LENGTH: f64 = 9.5;
pub const CAP_SCREW_TIP_AIR: f64 = 2.5;

pub fn cap_screw_beyond_face(fits: &Fits) -> f64 {
    CAP_SCREW_LENGTH - (WALL_AND_FLOOR_THICKNESS + (FOAM_CAP_HEIGHT - head_pad_height(fits)))
}

pub fn top_lid_screw_beyond_face(fits: &Fits) -> f64 {
    CAP_SCREW_LENGTH
        - (foam_cap_lid_height(fits) - head_cbore_depth(fits) + cap_lid_clearance(fits))
}

pub fn bottom_screw_bore_depth(fits: &Fits) -> f64 {
    cap_screw_beyond_face(fits) + CAP_SCREW_TIP_AIR
}

pub fn top_screw_bore_depth(fits: &Fits) -> f64 {
    top_lid_screw_beyond_face(fits) + CAP_SCREW_TIP_AIR
}

// --- The deck mounts ---------------------------------------------------------------------------

/// A deck mount's boss and bore, its insert, the relief under the insert, and the gap it keeps
/// off the cap.
pub const DECK_MOUNT_BOSS_RADIUS: f64 = 5.;
pub const DECK_MOUNT_BORE_RADIUS: f64 = 2.;
pub const DECK_MOUNT_INSERT_LENGTH: f64 = 5.7;
pub const DECK_MOUNT_BORE_RELIEF: f64 = 1.;
pub const DECK_MOUNT_CAP_GAP: f64 = 1.5;

/// A standing column passes the lid's clearance hole on the slip fit.
pub fn deck_mount_lid_slip(fits: &Fits) -> f64 {
    fits.slip
}

// --- The cap's conduits ------------------------------------------------------------------------

/// The air a valve cradle's plinth keeps off every other opening on the lid.
pub const CAP_CRADLE_ROOM_GAP: f64 = 1.0;
/// The line every fluid port on the core takes.
pub const LLDPE_TUBE_OD: f64 = 6.35;
/// A conduit's bore, the reservoir A fill's wider straight bore, the wall round a bore and the
/// boss it makes.
pub const CAP_CONDUIT_BORE_RADIUS: f64 = PORT_HOLE_RADIUS;
pub const CAP_CONDUIT_BORE_RADII: [(&str, f64); 1] = [("reservoir-a-fill", 5.5)];
pub const CAP_CONDUIT_WALL: f64 = WALL_THICKNESS;
pub const CAP_CONDUIT_BOSS_RADIUS: f64 = CAP_CONDUIT_BORE_RADIUS + CAP_CONDUIT_WALL;

pub fn cap_conduit_lid_slip(fits: &Fits) -> f64 {
    deck_mount_lid_slip(fits)
}

/// How far off its bore's axis a line leaves a conduit, in degrees: the lid's hole is countersunk
/// to it.
pub const CAP_CONDUIT_ENTRY_SKEW: f64 = 38.0;

/// The countersink's mouth on the lid's outer face: the bore opened at the entry skew through the
/// lid's plate.
pub fn cap_conduit_entry_relief_radius() -> f64 {
    CAP_CONDUIT_BORE_RADIUS + WALL_AND_FLOOR_THICKNESS * radians(CAP_CONDUIT_ENTRY_SKEW).tan()
}

/// The steepest entry skew the boss's wall carries over the countersink's cone, in degrees.
pub fn cap_conduit_entry_skew_ceiling() -> f64 {
    degrees(CAP_CONDUIT_WALL.atan2(WALL_AND_FLOOR_THICKNESS))
}

/// The CO2 line's column, whose lean lands inside one of the support ring's slots.
pub const CO2_LANE_X: f64 = 48.0;
/// The carbonated water's climb, pinned to a slot of the support ring, the column it drifts to
/// once clear of the inlet tail, and the two heights it drifts between.
pub const WATER_OUTLET_CLIMB_X: f64 = -48.5;
pub const WATER_OUTLET_UPPER_CLIMB_X: f64 = -35.0;
pub const WATER_OUTLET_DRIFT_Z: [f64; 2] = [EVAP_TAIL_LOW_Z + LLDPE_TUBE_OD + 2.0, 140.0];
/// Reservoir A's reed ribbon leaves through the cap over its reed column.
pub const REED_CABLE_CONDUIT_X: f64 = REED_COLUMN_AXIS_X;
pub const REED_CABLE_CONDUIT_Y: f64 = LEVEL_ROD_Y;
/// Where the water inlet's and the carbonated water's cap conduits stand before the above-core
/// guides place them, and the shared sensor cable's passage.
pub const WATER_IN_CONDUIT_XY: [f64; 2] = [86.2532889963965, 32.80179966121266];
pub const CARB_WATER_OUT_CONDUIT_XY: [f64; 2] = [52.2, -PORT_LANE_MID_Y];
pub const SENSOR_CABLE_CONDUIT_XY: [f64; 2] = [-23.2, -48.0];
/// The web that closes a foam gap too narrow to pour between two columns.
pub const CAP_CONDUIT_LINK_WIDTH: f64 = 5.0;
/// The carbonator's top plate, and the band from a top-plate elbow's axis up to the cap's floor.
pub const CARBONATOR_TOP_PLATE_Z: f64 =
    WALL_AND_FLOOR_THICKNESS + CARBONATOR_SUPPORT_RING_HEIGHT + CARBONATOR_HEIGHT;
pub const TOP_BAND_TO_CAP: f64 =
    FOAM_SHELL_OUTER_HEIGHT - (CARBONATOR_TOP_PLATE_Z + HOLE_SHIFT_FROM_EDGE);
/// The line's stock bend radius.
pub const LLDPE_BEND_RADIUS: f64 = 4.0 * LLDPE_TUBE_OD;

// --- The cap's anchors and side anchors --------------------------------------------------------

/// The zip tie across its width, and the cavity it passes with its slip each side.
pub const CAP_ANCHOR_TIE_W: f64 = 2.5;

pub fn cap_anchor_cav_buffer(fits: &Fits) -> f64 {
    2.0 * fits.slip
}

pub fn cap_anchor_cav_w(fits: &Fits) -> f64 {
    CAP_ANCHOR_TIE_W + cap_anchor_cav_buffer(fits)
}

/// The solid a rib keeps at each end of its channel, along the run, and the rib's length.
pub const CAP_ANCHOR_CAV_WALL: f64 = 3.0;

pub fn cap_anchor_len(fits: &Fits) -> f64 {
    cap_anchor_cav_w(fits) + 2.0 * CAP_ANCHOR_CAV_WALL
}

/// A side anchor's post: one tie's tunnel and its two flanks along the run.
pub fn cap_side_len(fits: &Fits) -> f64 {
    cap_anchor_len(fits)
}

pub fn cap_side_cav_w(fits: &Fits) -> f64 {
    cap_anchor_cav_w(fits)
}

pub fn cap_side_flank(fits: &Fits) -> f64 {
    (cap_side_len(fits) - cap_side_cav_w(fits)) / 2.0
}

/// The zip tie through its thickness, the least printable stock under a window, and the tie's
/// channel down the post's back face.
pub const CAP_SIDE_TIE_T: f64 = 1.0;
pub const CAP_SIDE_CAV_BACKING_MIN: f64 = 1.0;
pub const CAP_SIDE_BACK_RELIEF: f64 = 1.2;

// Degrees to radians and back, rounded as the cold core's recipes round them.
fn radians(angle: f64) -> f64 {
    angle * std::f64::consts::PI / 180.
}

fn degrees(angle: f64) -> f64 {
    angle * 180. / std::f64::consts::PI
}
