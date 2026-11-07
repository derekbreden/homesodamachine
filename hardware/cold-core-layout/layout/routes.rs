//! The lines inside the cold core, as the corners of their centrelines in the shell's frame, and
//! the bend every one of them turns at: the ¼" LLDPE's least bend, from the routing catalog.
//!
//! Each line runs from the fitting or reservoir it is made up on to the cap's face, where the
//! machine's own run to that conduit starts, except the CO2's, which comes down from its cap guide
//! to the carbonator, and the PRV's vent, which leaves by the shell's +Y flank. Every line fits its
//! corridor at the stock bend, so each of its corners turns at it. Corners laid out with the
//! above-core guides the lines climb to are written in the enclosure's frame, as those guides are,
//! and carried into the shell's through the cap lid's pose.
use crate::{b_fill, cap};
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as core;
use hsm_foam_shell_numbers as shell;
use hsm_prv_shroud_numbers as shroud;
use hsm_reservoir_numbers as reservoir;
use serde::Deserialize;
use std::sync::OnceLock;

/// A point or a direction.
pub type P3 = [f64; 3];

/// The bend the lines turn at.
pub fn bend_radius() -> f64 {
    catalog::fluid_stock(core::LLDPE_TUBE_OD).min_bend
}

/// The PRV's relief: out of the shroud's underside pointing down, one corner, and straight out of
/// the shell's +Y flank into the socket the appliance's chase holds. The shroud lies on the west
/// lane, its axis on the top-plate elbows' band.
pub fn prv_vent() -> [[f64; 3]; 3] {
    let lane_y = core::WEST_LANE_MID_Y;
    let start = [0., lane_y, core::CARBONATOR_TOP_PLATE_Z + core::HOLE_SHIFT_FROM_EDGE - shroud::outer_diameter() / 2.];
    let flank_y = core::OUTER_SHELL_Y_LENGTH / 2.;
    // The fall clears the bend by this much before the line turns out.
    let fall_margin = 2.;
    let cross_z = start[2] - (bend_radius() + fall_margin);
    // How far the line runs on past the flank, into its socket.
    let reach = bend_radius() - (flank_y - lane_y) + 1.;
    [start, [start[0], lane_y, cross_z], [start[0], flank_y + reach, cross_z]]
}

/// The +Y face the PRV's vent leaves the shell by; the line is cut flush with it.
pub const PRV_VENT_FLANK_Y: f64 = core::OUTER_SHELL_Y_LENGTH / 2.;

/// The tube every line is: the ¼" LLDPE's radius.
pub fn line_radius() -> f64 {
    core::LLDPE_TUBE_OD / 2.
}

/// The foam a laid line keeps between it and the next solid, so the pour reaches between them.
pub const LINE_HUG: f64 = 2.;

/// The storey the top-plate elbows turn their lines onto, a port's shift over the carbonator's top.
pub const TOP_BAND_Z: f64 = core::CARBONATOR_TOP_PLATE_Z + core::HOLE_SHIFT_FROM_EDGE;

/// Where a riser comes out of the cap: the lid's face, in the shell's frame.
pub fn conduit_mouth_z() -> f64 {
    core::cap_face_z(&catalog::fits())
}

/// One line: its name and its centreline's corners.
#[derive(Clone, Debug, PartialEq)]
pub struct Line {
    pub name: &'static str,
    pub points: Vec<P3>,
}

/// Every line inside the casing, by name.
pub fn lines() -> Vec<Line> {
    let line = |name, points| Line { name, points };
    vec![
        line("carb-water-out", carb_water_out()),
        line("co2-in", co2_in()),
        line("prv-vent", prv_vent().to_vec()),
        line("reservoir-a", reservoir_a()),
        line("reservoir-a-fill", reservoir_a_fill()),
        line("reservoir-b", reservoir_b()),
        line("reservoir-b-fill", reservoir_b_fill()),
        line("water-in", water_in()),
    ]
}

// --- The above-core guides the lines climb to --------------------------------------------------

/// The cap guides the above-core design places on the lid's face (`hardware/manifold-layout/
/// above-core.json`), in the enclosure's frame.
#[derive(Deserialize)]
struct CapGuides {
    #[serde(rename = "water-in")]
    water_in: P3,
    #[serde(rename = "carb-water-out")]
    carb_water_out: P3,
    #[serde(rename = "A-fill")]
    a_fill: P3,
    #[serde(rename = "B-draw")]
    b_draw: P3,
}

#[derive(Deserialize)]
struct Guides {
    gas_guide_world_mm: P3,
    cap_guides_world_mm: CapGuides,
}

fn guides() -> &'static Guides {
    static DESIGN: OnceLock<Guides> = OnceLock::new();
    DESIGN.get_or_init(|| {
        serde_json::from_str(include_str!("../../manifold-layout/above-core.json"))
            .expect("the above-core design parses")
    })
}

/// A guide's station in the shell's plan.
fn shell_xy(world: P3) -> [f64; 2] {
    let [x, y, _] = cap::world_to_shell(world);
    [x, y]
}

/// A station of the shell's plan, in the enclosure's.
fn world_xy(xy: [f64; 2]) -> [f64; 2] {
    let [x, y, _] = cap::cap_to_world([-xy[0], -xy[1], 0.]);
    [x, y]
}

fn at(xy: [f64; 2], z: f64) -> P3 {
    [xy[0], xy[1], z]
}

/// The distance between two plan stations.
fn plan_distance(a: [f64; 2], b: [f64; 2]) -> f64 {
    0f64.hypot(a[0] - b[0]).hypot(a[1] - b[1])
}

// --- The carbonator's lines ---------------------------------------------------------------------

/// The CO2's run: straight down from its cap guide, through the cup and the lid, then a pair of
/// stock turns that shifts the descent out to the CO2's column beyond the copper wrap, down that
/// column to the shell's floor storey, and the lean in to the bottom plate's lane-side port.
pub fn co2_in() -> Vec<P3> {
    let guide = guides().gas_guide_world_mm;
    let r = bend_radius();
    let lower = world_xy([shell::CO2_INLET_LANE_XYZ[0], shell::CO2_INLET_LANE_XYZ[1]]);
    let shift = plan_distance([guide[0], guide[1]], lower);
    let theta = (1.0 - shift / (2.0 * r)).acos();
    let setback = r * (theta / 2.0).tan();
    let drop = 2.0 * r * theta.sin();
    let w = cap::world_to_shell;
    vec![
        w(guide),
        w([guide[0], guide[1], CO2_TURN_Z - setback]),
        w([lower[0], lower[1], CO2_TURN_Z - drop + setback]),
        shell::CO2_INLET_LANE_XYZ,
        shell::CO2_INLET_XYZ,
    ]
}

/// The height, in the enclosure's frame, the CO2's pair of turns centres on, under the cup.
pub const CO2_TURN_Z: f64 = 230.4;

/// The −Y a riser at `x` stands on to clear the carbonator and its coil by one hug: the clearance
/// is radial, to the envelope's surface on the riser's own azimuth.
pub fn coil_standoff_y(x: f64) -> f64 {
    let clear = core::CARBONATOR_COIL_ENVELOPE_RADIUS + line_radius() + LINE_HUG;
    let reach = clear.powi(2) - x.powi(2);
    if reach > 0.0 { -reach.sqrt() } else { 0.0 }
}

/// The −Y a riser at `x` stands on midway across the annulus between the carbonator's coil
/// envelope and a reservoir pocket's centreward wall, radially.
pub fn annulus_y(x: f64) -> f64 {
    let mid = (core::CARBONATOR_COIL_ENVELOPE_RADIUS + core::POCKET_CENTERWARD_ARC_OUTER_RADIUS
        - core::WALL_AND_FLOOR_THICKNESS)
        / 2.0;
    let reach = mid.powi(2) - x.powi(2);
    if reach > 0.0 { -reach.sqrt() } else { 0.0 }
}

/// The Y the CO2's lean in stands at, at `x`, or none where the lean does not reach `x`.
pub fn co2_run_y(x: f64) -> Option<f64> {
    let ([x0, y0, _], [x1, y1, _]) = (shell::CO2_INLET_LANE_XYZ, shell::CO2_INLET_XYZ);
    if !(x0.min(x1) - 1e-9 <= x && x <= x0.max(x1) + 1e-9) {
        return None;
    }
    Some(y0 + (y1 - y0) * (x - x0) / (x1 - x0))
}

/// The carbonated water's run: out of the bottom plate's elbow flat on its storey to its climb's
/// column, through one of the support ring's slots to the annulus beside the coil, up clear of
/// the inlet copper, drifting along the coil's standoff to its upper column, up to the top
/// plate's band, across to its cap guide's column and up through the cap. Where its climb crosses
/// the CO2's lean it rises over it by a tube and a hug at the crossing.
pub fn carb_water_out() -> Vec<P3> {
    let x = core::WATER_OUTLET_CLIMB_X;
    let riser_y = annulus_y(x);
    let upper_x = core::WATER_OUTLET_UPPER_CLIMB_X;
    let upper_y = coil_standoff_y(upper_x);
    let mid_x = (x + upper_x) / 2.0;
    let port_y = core::CARBONATOR_PORT_OFFSET;
    let rise = match co2_run_y(x) {
        None => 0.0,
        Some(co2_y) => (core::LLDPE_TUBE_OD + LINE_HUG) * ((port_y - riser_y) / (port_y - co2_y)),
    };
    let storey = shell::FRONT_FACE_PORT_Z;
    let [low, high] = core::WATER_OUTLET_DRIFT_Z;
    let guide = shell_xy(guides().cap_guides_world_mm.carb_water_out);
    vec![
        [0.0, port_y, storey],
        [x, port_y, storey],
        [x, riser_y, storey + rise],
        [x, riser_y, low],
        [mid_x, coil_standoff_y(mid_x), (low + high) / 2.0],
        [upper_x, upper_y, high],
        [upper_x, upper_y, TOP_BAND_Z],
        at(guide, TOP_BAND_Z),
        at(guide, conduit_mouth_z()),
    ]
}

/// The water inlet's run, in the enclosure's frame: from the top plate's elbow level on its band
/// toward the cap's aft side, an oblique turn that falls to the low storey while it turns in plan,
/// along the low storey over the carbonator, a shift onto the inlet's lane, along the lane to its
/// guide's column, and straight up through the cap's guide.
pub mod water_in {
    /// The storeys the run takes in the enclosure's frame: the elbow's band, and the low storey
    /// its oblique turn falls to over the carbonator.
    pub const HIGH_Z: f64 = 219.4;
    pub const FALL: f64 = 14.9;
    pub const LOW_Z: f64 = HIGH_Z - FALL;
    /// The level leg's end and the storey it runs on, toward the aft guide.
    pub const AFT_X: f64 = -20.0;
    pub const AFT_Y: f64 = 283.0;
    /// The X the oblique turn lands the run on: the low storey's line over the carbonator.
    pub const TURN_X: f64 = -70.5;
    /// The inlet's lane, and the Y its shift onto the lane starts from.
    pub const LANE_X: f64 = -78.5;
    pub const RETURN_Y: f64 = 363.0;
    /// Where the lane hands the run to its guide's column.
    pub const LANE_END_Y: f64 = 385.0;
}

/// The water inlet's run: from the top plate's elbow on its band, in the shell's frame.
pub fn water_in() -> Vec<P3> {
    use water_in::*;
    let r = bend_radius();
    let theta = std::f64::consts::PI / 4.0 + ((FALL / r - 1.0) / 2f64.sqrt()).asin();
    let setback = r * (theta / 2.0).tan();
    let turn_start = TURN_X + r * (theta.sin() + theta.cos());
    let return_theta = (1.0 - (LANE_X - TURN_X).abs() / (2.0 * r)).acos();
    let return_setback = r * (return_theta / 2.0).tan();
    let return_run = 2.0 * r * return_theta.sin();
    let guide = guides().cap_guides_world_mm.water_in;
    let world = [
        [AFT_X, AFT_Y, HIGH_Z],
        [turn_start - setback, AFT_Y, HIGH_Z],
        [TURN_X, AFT_Y, LOW_Z],
        [TURN_X, RETURN_Y + return_setback, LOW_Z],
        [LANE_X, RETURN_Y + return_run - return_setback, LOW_Z],
        [LANE_X, LANE_END_Y, LOW_Z],
        [guide[0], guide[1], LOW_Z],
        guide,
    ];
    let mut points = vec![[0., -core::CARBONATOR_PORT_OFFSET, TOP_BAND_Z]];
    points.extend(world.map(cap::world_to_shell));
    points
}

// --- The reservoirs' lines ----------------------------------------------------------------------

/// A reservoir line that turns from its port's column to its cap guide's: a pair of stock turns
/// that begin just over the cup's floor, the line upright at both ends. One whose guide stands
/// over its port runs straight.
pub fn guided(lower: [f64; 2], upper: [f64; 2], start_z: f64, end_z: f64) -> Vec<P3> {
    let fits = catalog::fits();
    let r = bend_radius();
    let turn_z = core::FOAM_SHELL_OUTER_HEIGHT + core::cap_shell_clearance(&fits)
        + core::WALL_AND_FLOOR_THICKNESS
        + GUIDED_TURN_LIFT;
    let distance = plan_distance(lower, upper);
    if distance < 1e-9 {
        return vec![at(lower, start_z), at(upper, end_z)];
    }
    let theta = (1.0 - distance / (2.0 * r)).acos();
    let setback = r * (theta / 2.0).tan();
    let rise = 2.0 * r * theta.sin();
    vec![at(lower, start_z), at(lower, turn_z + setback), at(upper, turn_z + rise - setback), at(upper, end_z)]
}

/// How far over the cup's floor a guided reservoir line's turns begin.
pub const GUIDED_TURN_LIFT: f64 = 0.25;

/// A side's port off one of the interface's port tables.
fn port(table: &[(i64, [f64; 2])], side: i64) -> [f64; 2] {
    core::reservoir_port(table, side).expect("the interface tables a port on each side")
}

/// Reservoir A's draw: its dip tube, straight up from its mouth on the floor through its cap's
/// draw grip and the cap over it.
pub fn reservoir_a() -> Vec<P3> {
    let xy = port(&core::RESERVOIR_DRAW_PORT, 1);
    vec![at(xy, reservoir::dip_tube_mouth_z()), at(xy, conduit_mouth_z())]
}

/// Reservoir B's draw: its dip tube, up from its mouth on the floor to its cap guide.
pub fn reservoir_b() -> Vec<P3> {
    let upper = shell_xy(guides().cap_guides_world_mm.b_draw);
    guided(port(&core::RESERVOIR_DRAW_PORT, -1), upper, reservoir::dip_tube_mouth_z(), conduit_mouth_z())
}

/// How far a fill line's tip reaches down past its reservoir cap's plate, into the headspace.
pub const FILL_TIP_DROP: f64 = 1.0;

/// Reservoir A's fill: from its tip in the headspace, up through its cap's fill grip to its guide.
pub fn reservoir_a_fill() -> Vec<P3> {
    let upper = shell_xy(guides().cap_guides_world_mm.a_fill);
    let tip = reservoir::cap_assembly_lift() + reservoir::CAP_WALL_HEIGHT - FILL_TIP_DROP;
    guided(port(&core::RESERVOIR_FILL_PORT, 1), upper, tip, conduit_mouth_z())
}

/// Reservoir B's fill: in through the cap's front face, down its holder's bend and straight into
/// the reservoir's fill seat.
pub fn reservoir_b_fill() -> Vec<P3> {
    b_fill::passage().route.map(cap::world_to_shell).to_vec()
}
