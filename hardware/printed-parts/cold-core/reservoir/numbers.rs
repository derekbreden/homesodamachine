//! The flavour reservoirs' numbers, in millimetres: the open-top PETG cup that stands on the floor
//! of each of the foam shell's bag pockets, the cap screwed down on it through a gasket, the level
//! rod the two hold between them, and the flush TPU grips and air tubes the cap's ports take. The
//! frame is the foam shell's: +Z up, +X out along the side +1 pocket's axis; the side −1 reservoir
//! is the mirror of side +1 across X = 0, except where a number says it is stated per side. The
//! foam cap, the cold core's assembly and internal routes, the reservoir float rod's drawing, the
//! BOM and the docs take these by name.
use hsm_aero_float_numbers as float;
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as core;

// --- The cap's ports ---------------------------------------------------------------------------

/// The cap's flat plate, which captures the flush grips.
pub const PLATE_THICKNESS: f64 = 4.;

/// A flush TPU grip: a waist through the plate with a flare into each face's countersink, and the
/// tube's bore through it with a lead-in at each end.
#[derive(Clone, Copy, Debug)]
pub struct Grip {
    /// The waist through the plate.
    pub waist_d: f64,
    /// The flares, at the plate's faces.
    pub flare_d: f64,
    /// The bore the tube takes.
    pub bore_d: f64,
    /// The bore's lead-in at each face, and its depth.
    pub lead_d: f64,
    pub lead_h: f64,
}

/// The grip the fill and draw lines each take.
pub const LIQUID_GRIP: Grip = Grip { waist_d: 9., flare_d: 11., bore_d: 6.2, lead_d: 7., lead_h: 0.4 };
/// The grip the reservoir's air tube takes.
pub const AIR_GRIP: Grip = Grip { waist_d: 6., flare_d: 8., bore_d: 3.9, lead_d: 4.5, lead_h: 0.3 };

/// Each reservoir's air port in the shell's frame, by side, tabled as the interface tables the fill
/// and draw ports (`hsm_cold_core_interface::reservoir_port` reads it).
pub const AIR_PORT: [(i64, [f64; 2]); 2] = [(1, [120., -26.]), (-1, [-109., -32.5])];

/// The air tube, how far it reaches under the cap's underside, and how far it stands out of the
/// casing.
pub const AIR_TUBE_OD: f64 = 4.;
pub const AIR_TUBE_ID: f64 = 2.5;
pub const AIR_TUBE_BELOW_LID: f64 = 1.;
pub const AIR_TUBE_ABOVE_CASING: f64 = 6.;
/// The passage the foam cap leaves each air tube.
pub const AIR_PASSAGE_DIAMETER: f64 = 5.2;

// --- The cup -----------------------------------------------------------------------------------

/// The reservoirs: one fill port each.
pub const COUNT: usize = core::RESERVOIR_FILL_PORT.len();

/// The floor and every wall, one PETG thickness: the floor the shell's pocket is cut to take.
pub const WALL_THICKNESS: f64 = core::RESERVOIR_FLOOR_THICKNESS;
/// The rounds where the centreward curve meets the ±Y walls, outside and in the cavity. The outer
/// round is at least the screw bosses' radius, so the bosses on its centres stay inside the wall.
pub const OUTER_ROUND: f64 = 6.;
pub const INNER_ROUND: f64 = 6.;

/// The cup slides into its pocket on the running fit.
pub fn clearance() -> f64 {
    core::reservoir_clearance(&catalog::fits())
}

/// The cup's outline in plan: its far face, its ±Y faces and its centreward curve's radius, the
/// pocket's own less the running fit. The cap and the gasket share it.
pub fn outer_far_x() -> f64 {
    core::BAG_POCKET_FAR_INNER_X - clearance()
}

pub fn outer_y() -> f64 {
    core::BAG_POCKET_Y_INNER_MAX - clearance()
}

pub fn outer_radius() -> f64 {
    core::POCKET_CENTERWARD_ARC_OUTER_RADIUS + clearance()
}

/// The cavity's outline: one wall in on the straight faces and one wall out on the curve.
pub fn inner_far_x() -> f64 {
    outer_far_x() - WALL_THICKNESS
}

pub fn inner_y() -> f64 {
    outer_y() - WALL_THICKNESS
}

pub fn inner_radius() -> f64 {
    outer_radius() + WALL_THICKNESS
}

// --- The cap and the gasket --------------------------------------------------------------------

/// The cap's perimeter wall, which hangs from its plate round the gasket joint, and its width.
pub const CAP_WALL_HEIGHT: f64 = 5.;
pub const CAP_WALL_WIDTH: f64 = 6.;
/// The cap's plate: it spans the cavity unsupported and takes the screw heads' counterbores.
pub const CAP_PLATE_THICKNESS: f64 = PLATE_THICKNESS;
/// The cap from its wall's foot, its own Z = 0, to its plate's top.
pub const CAP_HEIGHT: f64 = CAP_WALL_HEIGHT + CAP_PLATE_THICKNESS;
/// The gasket, and its strip: over the cup's rim and in over the cavity's mouth.
pub const GASKET_THICKNESS: f64 = 2.;
pub const GASKET_STRIP_WIDTH: f64 = 5.;
/// What stands on the cup's rim: the gasket, the cap's wall and its plate.
pub const CAP_STACK_HEIGHT: f64 = GASKET_THICKNESS + CAP_WALL_HEIGHT + CAP_PLATE_THICKNESS;

/// The cup's underside and rim: the running fit over the pocket's floor, and the stack under the
/// pocket's walls' top with the running fit over it.
pub fn outer_z() -> [f64; 2] {
    [
        core::BAG_POCKET_FLOOR_TOP_Z + clearance(),
        core::BAG_POCKET_WALLS_TOP_Z - clearance() - CAP_STACK_HEIGHT,
    ]
}

/// The cavity, from the floor's top up through the rim.
pub fn inner_z() -> [f64; 2] {
    let [bottom, rim] = outer_z();
    [bottom + WALL_THICKNESS, rim]
}

/// The wet floor: flat, the floor's top.
pub fn floor_z() -> f64 {
    inner_z()[0]
}

/// Where the cap's own Z = 0 lands when it is screwed down: on the gasket on the rim.
pub fn cap_assembly_lift() -> f64 {
    outer_z()[1] + GASKET_THICKNESS
}

/// The dip tube's mouth: its cut's centre, one tube radius over the floor its tip rests on.
pub fn dip_tube_mouth_z() -> f64 {
    floor_z() + core::LLDPE_TUBE_OD / 2.
}

// --- The screws --------------------------------------------------------------------------------

/// The cap screw's shank and head, which the clearance holes and the counterbores take on the slip
/// fit.
pub const SCREW_DIAMETER: f64 = 3.;
pub const SCREW_HEAD_DIAMETER: f64 = 5.5;

pub fn clearance_hole_diameter() -> f64 {
    SCREW_DIAMETER + 2. * catalog::fits().slip
}

pub fn counterbore_diameter() -> f64 {
    SCREW_HEAD_DIAMETER + 2. * catalog::fits().slip
}

/// The cap prints plate-down: the counterbore goes through the plate, and the head's seat in the
/// wall below it is a face printed over support.
pub fn counterbore_depth() -> f64 {
    CAP_PLATE_THICKNESS + catalog::fits().supported_surface
}

/// The heat-set insert's pocket under each station of the rim: longer than the insert, so the
/// screw is thread-limited, not pocket-limited.
pub const INSERT_POCKET_RADIUS: f64 = 2.;
pub const INSERT_POCKET_DEPTH: f64 = 7.;
/// The PETG round the pocket, which carries the insert's grip and the clamp's load.
pub const BOSS_ANNULUS: f64 = 3.;
/// The cup's boss, the cap's boss and the gasket's pad at each station, one footprint: the clamp
/// compresses one uniform disc.
pub const BOSS_RADIUS: f64 = INSERT_POCKET_RADIUS + BOSS_ANNULUS;
/// The cup's bosses hang this far from its rim, the pocket and solid under it. Each is cut off
/// underneath by a flat that rises away from its wall at the printable overhang, from a cylinder
/// built this much longer.
pub const BOSS_HEIGHT: f64 = 15.;
pub const BOSS_OVERRUN: f64 = 5.;
/// How far the stations stand in from the outer faces: the outer round, so the corner stations sit
/// on its centres.
pub const SCREW_SETBACK: f64 = OUTER_ROUND;
/// How far from a curve corner's boss its flat pivots, toward the cavity's corner: the corner
/// itself lies too far off for the flat to stay clear of the insert's pocket.
pub const CURVE_CORNER_PIVOT: f64 = 2.;

/// A boss's flat: where its plane crosses the wall at the boss's bottom, and the unit direction
/// in plan from the boss toward that wall. The plane rises away from the wall; the boss keeps what
/// is above it.
#[derive(Clone, Copy, Debug)]
pub struct Flat {
    pub pivot: [f64; 2],
    pub toward: [f64; 2],
}

/// A screw's station on the side +1 cup, cap and gasket, and its cup boss's flat.
#[derive(Clone, Copy, Debug)]
pub struct Station {
    pub xy: [f64; 2],
    pub flat: Flat,
}

/// The stations: the far corners, the far face's middle, the curve's corners on the outer round's
/// centres, and the curve's apex. The far corners' flats aim at the cavity's far corners,
/// the middles' at their walls square on, and the curve corners' at the cavity's corner there,
/// pivoted short of it.
pub fn stations() -> [Station; 6] {
    let corner = [outer_far_x() - SCREW_SETBACK, outer_y() - SCREW_SETBACK];
    let far_mid = outer_far_x() - SCREW_SETBACK;
    let apex = outer_radius() + SCREW_SETBACK;
    let curve_corner_y = outer_y() - OUTER_ROUND;
    let curve_corner_r = outer_radius() + OUTER_ROUND;
    let curve_corner_x = (curve_corner_r * curve_corner_r - curve_corner_y * curve_corner_y).sqrt();
    let (wall_x, wall_y, wall_apex) = (inner_far_x(), inner_y(), inner_radius());
    let inner_corner_x = (wall_apex * wall_apex - wall_y * wall_y).sqrt();
    let (dx, dy) = (inner_corner_x - curve_corner_x, wall_y - curve_corner_y);
    let reach = (dx * dx + dy * dy).sqrt();
    let toward = [dx / reach, dy / reach];
    let pivot = [
        curve_corner_x + CURVE_CORNER_PIVOT * toward[0],
        curve_corner_y + CURVE_CORNER_PIVOT * toward[1],
    ];
    let diagonal = 1. / 2f64.sqrt();
    let station = |xy, pivot, toward| Station { xy, flat: Flat { pivot, toward } };
    [
        station(corner, [wall_x, wall_y], [diagonal, diagonal]),
        station([corner[0], -corner[1]], [wall_x, -wall_y], [diagonal, -diagonal]),
        station([far_mid, 0.], [wall_x, 0.], [1., 0.]),
        station([curve_corner_x, curve_corner_y], pivot, toward),
        station([curve_corner_x, -curve_corner_y], [pivot[0], -pivot[1]], [toward[0], -toward[1]]),
        station([apex, 0.], [wall_apex, 0.], [-1., 0.]),
    ]
}

// --- The level rod -----------------------------------------------------------------------------

/// The rod: the float's guide.
pub const ROD_DIAMETER: f64 = float::GUIDE_DIAMETER;

/// The seat the rod stands in at both ends, on the slip fit; the float's running bore is its own.
pub fn rod_bore() -> f64 {
    ROD_DIAMETER + 2. * catalog::fits().slip
}

/// The wall round the seat, in the floor's anchor boss and the cap's register boss alike.
pub const ROD_BOSS_WALL: f64 = 2.;

pub fn rod_boss_diameter() -> f64 {
    rod_bore() + 2. * ROD_BOSS_WALL
}

/// The floor's anchor boss, and the printed floor its blind seat keeps under the rod's tip.
pub const ROD_ANCHOR_HEIGHT: f64 = 6.;
pub const ROD_ANCHOR_FLOOR: f64 = 0.;
/// How far the cap's register boss reaches below the cap's wall.
pub const ROD_REGISTER_HEIGHT: f64 = 2.;

/// The rod's station on the side +1 cup: in from the cavity's far wall by the float's rod station,
/// and across on the level rod's line, which the reed column outside stands on too and which does
/// not mirror.
pub fn rod_x() -> f64 {
    inner_far_x() - float::ROD_AXIS_FROM_INNER_WALL
}

pub const ROD_Y: f64 = core::LEVEL_ROD_Y;

/// What the rod's cut length leaves between its ends and its seats, so it never holds the cap off
/// its gasket.
pub fn rod_end_clearance() -> f64 {
    catalog::fits().slip
}

/// The rod's cut length: from the anchor's seat floor to the cap's register seat, screwed down, less
/// the end clearance.
pub fn rod_length() -> f64 {
    (cap_assembly_lift() + CAP_WALL_HEIGHT) - (floor_z() + ROD_ANCHOR_FLOOR) - rod_end_clearance()
}

// --- Level sensing -----------------------------------------------------------------------------

/// The float's magnet centre between its end stops: the bosses are wider than the float's bore, so
/// it rests on the anchor boss and rises to the register boss.
pub fn float_magnet_travel_z() -> [f64; 2] {
    [
        floor_z() + ROD_ANCHOR_HEIGHT + float::magnet_midplane(),
        cap_assembly_lift() - ROD_REGISTER_HEIGHT - (float::height() - float::magnet_midplane()),
    ]
}

/// The reeds' pitch: the whole millimetres that span the travel with the channel's reeds.
pub fn reed_pitch() -> f64 {
    let [low, high] = float_magnet_travel_z();
    ((high - low) / (core::REEDS_PER_RESERVOIR - 1) as f64).floor()
}

/// The reeds' centres up the channel, about the travel's middle, end stop to end stop.
pub fn reed_centres_z() -> [f64; core::REEDS_PER_RESERVOIR] {
    let [low, high] = float_magnet_travel_z();
    let pitch = reed_pitch();
    let span = (core::REEDS_PER_RESERVOIR - 1) as f64 * pitch;
    let middle = (low + high) / 2.;
    std::array::from_fn(|i| middle - span / 2. + i as f64 * pitch)
}

// --- The materials -----------------------------------------------------------------------------

/// The cups and their caps print in PETG Translucent Clear.
pub fn cup_colour() -> catalog::Colour {
    catalog::petg_translucent()
}

pub fn cap_colour() -> catalog::Colour {
    catalog::petg_translucent()
}

/// The gasket is clear silicone.
pub fn gasket_colour() -> catalog::Colour {
    catalog::silicone_clear()
}

/// The grips print in black TPU.
pub fn grip_colour() -> catalog::Colour {
    catalog::tpu_black()
}
