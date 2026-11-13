//! The reed sweep rig's numbers, in millimetres: the bench fixture that drives a finished float
//! along a bare carbonator tube, past reeds lying under its wall, so every closure and release is
//! logged against the magnet's place. Frame: +X runs along the tube's axis, from the rim that
//! faces the slide into the tube. That rim stands for the carbonator's bottom rim, so X is the
//! height above it. Y = 0 is the plane through the tube's axis and the reeds, and +Z is up from
//! the bench.
use hsm_aero_float_numbers as float;
use hsm_carbonator_tube_numbers as tube;
use hsm_reed_bridge_numbers as bridge;

// --- The print ---------------------------------------------------------------------------------

/// The layers the pieces are sliced at: the one on the bed, and those above it.
pub const BED_LAYER: f64 = 0.2;
pub const LAYER: f64 = 0.24;

// --- The bought slide --------------------------------------------------------------------------

/// The Befenybay ball-screw stage, from its maker's drawing: the frame without its motor, the
/// plate at each end, the block the screw's bearing sits in, and the carriage with its four
/// tapped holes.
pub mod slide {
    pub const FRAME_LENGTH: f64 = 320.;
    pub const BASE_WIDTH: f64 = 43.;
    pub const BASE_HEIGHT: f64 = 25.;
    pub const END_PLATE: f64 = 8.;
    pub const END_PLATE_HEIGHT: f64 = 57.;
    pub const MOTOR_PLATE_WIDTH: f64 = 56.;
    pub const MOTOR_PLATE_HEIGHT: f64 = 70.;
    pub const COUPLING_BAY: f64 = 35.;
    pub const BEARING_BLOCK: f64 = 9.;
    pub const CARRIAGE_LENGTH: f64 = 60.;
    pub const CARRIAGE_WIDTH: f64 = 42.;
    pub const CARRIAGE_HEIGHT: f64 = 32.;
    pub const CARRIAGE_BOTTOM: f64 = 27.;
    pub const CARRIAGE_TOP: f64 = CARRIAGE_BOTTOM + CARRIAGE_HEIGHT;
    /// The carriage's tapped M4 holes stand on a square of this side, centred on its top.
    pub const HOLE_PITCH: f64 = 30.;
    pub const SCREW_AXIS: f64 = 42.;
    pub const SCREW_DIAMETER: f64 = 16.;
    /// How far the carriage runs between the bearing block and the far plate.
    pub const TRAVEL: f64 = FRAME_LENGTH - 2. * END_PLATE - COUPLING_BAY - BEARING_BLOCK - CARRIAGE_LENGTH;
    /// The screw's lead, and the motor's full steps in a turn.
    pub const SCREW_LEAD: f64 = 5.;
    pub const MOTOR_STEPS: f64 = 200.;
    /// The motor as the assembly draws it.
    pub const MOTOR_FACE: f64 = 42.3;
    pub const MOTOR_LENGTH: f64 = 40.;
}

/// The bought home switch, a Makerbot-pattern board: the board, the two holes that flank its
/// switch, how far they stand in from the switch's edge, and how high the lever's middle rides
/// over the board's top.
pub mod switch {
    pub const BOARD_LENGTH: f64 = 40.;
    pub const BOARD_WIDTH: f64 = 16.;
    pub const BOARD_THICKNESS: f64 = 1.6;
    pub const HOLE_PITCH: f64 = 19.;
    pub const HOLE_INSET: f64 = 2.75;
    pub const LEVER_HEIGHT: f64 = 2.9;
    pub const BODY_LENGTH: f64 = 12.8;
    pub const BODY_WIDTH: f64 = 6.5;
    pub const BODY_HEIGHT: f64 = 5.8;
}

/// The hole a ruthex M3 insert is melted into, and how deep it is drilled.
pub const INSERT_HOLE: f64 = 4.;
pub const INSERT_DEPTH: f64 = 7.;
/// The hole an M4 screw drops through.
pub const M4_CLEARANCE: f64 = 4.5;

// --- The reed comb -----------------------------------------------------------------------------

/// The comb lies under the tube on the reed line and carries the tube's weight on its crown.
pub const COMB_HALF_WIDTH: f64 = 13.;
/// What the comb keeps under a reed's glass: the bed layer and nine more. Its wire grooves and
/// lead notches go deeper, down to the bed layer and three more, so a soldered joint has room
/// under the tube.
pub const COMB_FLOOR: f64 = BED_LAYER + 9. * LAYER;
pub const GROOVE_FLOOR: f64 = BED_LAYER + 3. * LAYER;
/// A reed's pocket, eleven layers deep. The glass lies on its floor.
pub const REED_POCKET_DEPTH: f64 = 11. * LAYER;
/// The comb's thickness on the reed line.
pub const COMB_CROWN: f64 = COMB_FLOOR + REED_POCKET_DEPTH;
/// The comb carries the tube on a flat land along the reed line, this far each side of it. Off
/// the land the saddle is cut over the tube's own radius, and deeper than the land by more than
/// the half layer a sliced curve stands proud, so no layer's edge reaches the tube before the
/// land does.
pub const CROWN_LAND: f64 = 3.;
pub const SADDLE_CLEARANCE: f64 = 0.2;
pub const SADDLE_RELIEF: f64 = LAYER / 2. + 0.01;
/// The tab at the comb's near end: the tube's rim seats against its inner face, and it stands
/// this far above the bore's lowest line so the sled stops on the same face.
pub const TAB: f64 = 4.;
pub const TAB_RISE: f64 = 3.5;
/// How far the comb runs on past the tube's far rim, where its wires leave.
pub const COMB_OVERRUN: f64 = 6.;
/// A reed's lead runs straight out of its pocket this far in a slit, then turns into a notch.
pub const LEAD_RUN: f64 = 5.;
pub const LEAD_SLIT: f64 = 1.2;
pub const LEAD_NOTCH: f64 = 3.;
/// The slit's floor under the lead's own line.
pub const LEAD_DROP: f64 = 0.6;
/// The wire grooves each side of the pocket column, as Y from and to: the signal wires on one
/// side, the shared return on the other.
pub const SIGNAL_GROOVE: (f64, f64) = (3., 10.5);
pub const RETURN_GROOVE: (f64, f64) = (-8., -3.);
/// The station numbers, counted from the tab, cut into the land beside the return groove.
pub const STATION_LABEL_Y: f64 = -10.5;
pub const STATION_LABEL_SIZE: f64 = 3.5;
pub const STATION_LABEL_DEPTH: f64 = 0.5;

/// How far the glass stands below the tube's wall when it lies on the pocket's floor.
pub fn reed_recess() -> f64 {
    REED_POCKET_DEPTH - bridge::REED_GLASS_DIAMETER
}

pub fn saddle_radius() -> f64 {
    tube::OUTER_RADIUS + SADDLE_CLEARANCE
}

pub fn comb_end() -> f64 {
    tube::LENGTH + COMB_OVERRUN
}

/// The reed stations along the comb: the two the bridge seeds, and one more a pitch beyond each.
pub fn stations() -> [(&'static str, f64); 4] {
    let (low, high) = (bridge::reed_low_z(), bridge::reed_high_z());
    let pitch = high - low;
    [("below", low - pitch), ("low", low), ("high", high), ("above", high + pitch)]
}

// --- The cradle --------------------------------------------------------------------------------

/// The slab the cradle's stations stand on, and what it keeps under the comb's pocket: the bed
/// layer and sixteen more.
pub const SLAB: f64 = 8.;
pub const POCKET_FLOOR: f64 = BED_LAYER + 16. * LAYER;
pub const CRADLE_HALF_WIDTH: f64 = 50.;
/// The pocket's room round the comb.
pub const COMB_CLEARANCE: f64 = 0.2;
/// The slab from the tube's near rim to the slide's far plate, and on past the tube's far rim.
pub const NOSE: f64 = 45.;
pub const TAIL: f64 = 26.;
/// The two keepers that stop the tube rolling off the comb: where each stands, how far it stops
/// short of each rim, and what its inner top edge clears the tube by.
pub const KEEPER_INNER: f64 = 38.;
pub const KEEPER_OUTER: f64 = 46.;
pub const KEEPER_INSET: f64 = 5.;
pub const KEEPER_CLEARANCE: f64 = 0.55;
/// The trough the comb's wires leave by, as Y from and to.
pub const WIRE_TROUGH: (f64, f64) = (-9., 11.5);
/// The slide stands beside the tube's axis by this much, so the rod's bar runs along the
/// carriage's side and its roller meets the sled on the reed line.
pub const SLIDE_OFFSET: f64 = 27.5;
/// The cheeks that take the slide's far end between them.
pub const CHEEK: f64 = 5.;
pub const CHEEK_HEIGHT: f64 = 12.;
pub const CHEEK_LENGTH: f64 = 20.;
pub const CHEEK_ROOT: f64 = 10.;
pub const CHEEK_CLEARANCE: f64 = 0.5;
/// The home switch's pad: the board's switch edge faces the tube from here, and the pad runs
/// this far past the board each way.
pub const SWITCH_EDGE_X: f64 = -15.;
pub const SWITCH_PAD_MARGIN: f64 = 1.;
pub const SWITCH_PAD_LEAD: f64 = 2.;

pub const TUBE_BOTTOM_Z: f64 = POCKET_FLOOR + COMB_CROWN;
pub const BORE_BOTTOM_Z: f64 = TUBE_BOTTOM_Z + tube::WALL;
pub const TUBE_AXIS_Z: f64 = TUBE_BOTTOM_Z + tube::OUTER_RADIUS;
pub const BORE_RADIUS: f64 = tube::ID / 2.;

pub fn saddle_axis_z() -> f64 {
    TUBE_BOTTOM_Z - SADDLE_RELIEF + saddle_radius()
}

/// The keepers' tops: as high as their inner edge may stand and still clear the tube.
pub fn keeper_top() -> f64 {
    TUBE_AXIS_Z - ((tube::OUTER_RADIUS + KEEPER_CLEARANCE).powi(2) - KEEPER_INNER.powi(2)).sqrt()
}

// --- The float sled ----------------------------------------------------------------------------
// The sled's own heights are measured up from the bore's lowest line, and its lengths from its
// near face.

pub const SLED_HALF_WIDTH: f64 = 26.5;
pub const SLED_TOP: f64 = 18.;
/// What the sled's underside clears the bore by, away from its two runners.
pub const SLED_UNDER: f64 = 1.2;
/// The runners: each is a flat land under the sled with a square outer edge, and the edge rides
/// the bore. The sled prints top down, so the land is a top face of the print: it lies this many
/// layers above the bed layer, and the edge stands where the bore passes that height.
pub const RUNNER_LAYERS: f64 = 57.;
pub const RUNNER_WIDTH: f64 = 5.;
pub const RUNNER_DEPTH: f64 = 4.;
/// Along the sled: the wall in front of the roller's slot, the slot, the wall the float's bottom
/// face seats on, the leaf that presses the float onto it, the room the leaf bends into, and the
/// wall behind that. The roller rests on the slot's floor, and the two walls beside the slot stop
/// short of the sled's top across the slot's span, where the rod's leg comes down.
pub const FRONT_WALL: f64 = 3.;
pub const SLOT: f64 = 5.4;
pub const SLOT_HALF_SPAN: f64 = 10.;
pub const SLOT_FLOOR: f64 = 4.;
pub const SLOT_WALL_TOP: f64 = 11.;
pub const DATUM_WALL: f64 = 3.;
pub const LEAF: f64 = 0.9;
pub const LEAF_PAD: f64 = 0.6;
pub const LEAF_PAD_HALF_WIDTH: f64 = 2.;
pub const LEAF_PAD_RISE: f64 = 3.;
pub const LEAF_PRELOAD: f64 = 0.5;
pub const LEAF_ROOM: f64 = 1.6;
pub const LEAF_BOTTOM: f64 = 6.;
pub const LEAF_SLIT: f64 = 1.2;
pub const LEAF_ROOT: f64 = 0.3;
pub const BACK_WALL: f64 = 2.5;
/// The sled is open under the float this far each side of the reed line.
pub const OPEN_HALF_WIDTH: f64 = 9.5;
/// The window in the back wall that a gauge pin goes under the float through.
pub const GAUGE_WINDOW_HALF_WIDTH: f64 = 4.;
pub const GAUGE_WINDOW_HEIGHT: f64 = 5.;
/// The lettering on the sled's sides.
pub const LABEL_SIZE: f64 = 5.;
pub const LABEL_DEPTH: f64 = 0.5;
/// The lowest the sled's side stands, where the lettering's band begins.
pub const LABEL_FLOOR: f64 = 9.5;

/// The three sleds: each seats the float this far off its rod's place, away from the reeds when
/// positive. The float's bore lets it wander that far on its rod.
pub fn sleds() -> [(&'static str, f64); 3] {
    [("near", -float::GUIDE_RADIAL_CLEARANCE), ("nominal", 0.), ("far", float::GUIDE_RADIAL_CLEARANCE)]
}

/// The float's axis above the bore's lowest line on a sled. The nominal sled sets it lower than
/// the rod stands by the reed's recess, so the magnet's axis keeps the machine's distance to the
/// glass's centre.
pub fn seat_axis(offset: f64) -> f64 {
    float::ROD_AXIS_FROM_INNER_WALL - reed_recess() + offset
}

/// Where the float's bottom face seats, from the sled's near face.
pub const fn seat_start() -> f64 {
    FRONT_WALL + SLOT + DATUM_WALL
}

/// The leaf's near face: it stands in the float's way by the preload.
pub fn leaf_start() -> f64 {
    seat_start() + float::height() + LEAF_PAD - LEAF_PRELOAD
}

pub fn back_wall_start() -> f64 {
    leaf_start() + LEAF + LEAF_ROOM
}

pub fn sled_length() -> f64 {
    back_wall_start() + BACK_WALL
}

/// The magnet's midplane, from the sled's near face.
pub fn magnet_from_sled_face() -> f64 {
    seat_start() + float::magnet_midplane()
}

/// A runner's land above the bore's lowest line.
pub const fn runner_land() -> f64 {
    SLED_TOP - BED_LAYER - RUNNER_LAYERS * LAYER
}

/// A runner's edge off the reed line: where the bore stands as high as the land.
pub fn runner_edge() -> f64 {
    (BORE_RADIUS.powi(2) - (BORE_RADIUS - runner_land()).powi(2)).sqrt()
}

/// The apex of the vee the float lies in, above the bore's lowest line. The vee's faces print as
/// overhangs whose layer edges stand half a layer proud of the face, so the vee is cut that much
/// deeper and the edges are where the float is meant to rest.
pub fn vee_apex(offset: f64) -> f64 {
    seat_axis(offset) - float::DIAMETER / 2. * std::f64::consts::SQRT_2 - LAYER / 2.
}

/// The roller's axis in the slot, from the sled's near face and above the bore's lowest line.
pub const fn roller_from_sled_face() -> f64 {
    FRONT_WALL + SLOT / 2.
}

/// The roller's axis above the bore's lowest line when it rests on the slot's floor.
pub const ROLLER_RISE: f64 = SLOT_FLOOR + ROLLER / 2.;

// --- The push rod ------------------------------------------------------------------------------

/// The rod's bar and everything cut with it are this thick across the rig.
pub const ROD_THICKNESS: f64 = 8.;
pub const BAR: f64 = 10.;
pub const PAD: f64 = 6.;
/// The flexure: past the pad the bar thins to a strip that bends up and down and nothing else,
/// so the roller rides the sled's slot at whatever height the carriage stands and lifts out by
/// hand. It starts this far past the pad, tapers in and out over this much, and is this long.
pub const FLEXURE: f64 = 2.;
pub const FLEXURE_START: f64 = 5.;
pub const FLEXURE_LENGTH: f64 = 50.;
pub const FLEXURE_TAPER: f64 = 5.;
/// How far below the slot's floor the roller would hang if the rod were rigid: the flexure bends
/// that much to seat it.
pub const ROLLER_PRELOAD: f64 = 1.5;
/// From the carriage's middle to the roller's axis.
pub const ROD_REACH: f64 = 200.;
/// The leg that comes down to the sled: how far it stands behind the roller's axis and ahead of
/// it, where it stops short of the float, and what its foot clears the sled's top by.
pub const LEG_BEHIND: f64 = 8.;
pub const LEG_AHEAD: f64 = 4.;
pub const LEG_CLEARANCE: f64 = 3.;
/// The stem and the roller that stand in the sled's slot.
pub const STEM: f64 = 4.6;
pub const ROLLER: f64 = 5.;
/// The finger that carries the striker screw out to the home switch. The screw's hole takes its
/// whole thread, so the screw reaches from seated on the finger to as far out as its insert
/// still holds it, and the finger's length puts the switch in the middle of that reach.
pub const FINGER: f64 = 7.;
pub const FINGER_HEIGHT: f64 = 8.;
pub const STRIKER_HOLE_DEPTH: f64 = 13.5;
/// The striker, an M3 socket-head screw, as the assembly draws it: its head, its thread, and how
/// far its head stands off the finger at the middle of its reach.
pub const STRIKER_HEAD: f64 = 5.5;
pub const STRIKER_HEAD_HEIGHT: f64 = 3.;
pub const STRIKER_SHANK: f64 = 3.;
pub const STRIKER_LENGTH: f64 = 12.;
pub const STRIKER_PROUD: f64 = 3.;

pub const fn leg_bottom() -> f64 {
    BORE_BOTTOM_Z + SLOT_WALL_TOP + LEG_CLEARANCE
}

/// The striker screw's axis, which is the height of the switch lever's middle.
pub const fn striker_z() -> f64 {
    leg_bottom() + FINGER_HEIGHT / 2.
}

pub const fn switch_pad_top() -> f64 {
    striker_z() - switch::LEVER_HEIGHT - switch::BOARD_THICKNESS
}

// --- Where things stand ------------------------------------------------------------------------

/// The sled's near face at the comb's tab, at its home, and at the deepest it goes with all of
/// it still in the tube.
pub const SLED_AT_TAB: f64 = 0.;
pub const HOME_BEFORE_TAB: f64 = 1.;

pub fn sled_deepest() -> f64 {
    tube::LENGTH - sled_length()
}
