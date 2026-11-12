//! The faucet shell's numbers, in millimetres: the printed shroud round the harvested Westbrass,
//! the flavor tubes and the lever's swing, with its gooseneck carrying the tubes to the glass and
//! the display on its tip. World +Z is up, ±X lateral and symmetric about X = 0, -Y forward toward
//! the glass; the Westbrass's shank stands on Z at (0, 0). Zone 1 is the foot, zone 2 the donor's
//! body, zone 3 its arches, zones 4 and 5 the shoulder up to the seam the gooseneck is swept from.
//!
//! The display's tip frame is x across the neck, s back up it from the tube exit and n out
//! through the glass.

use crate::catalog::slip;
use crate::interface::*;
use crate::paths::{self, Kind, LOWER_BUNDLE_X, LOWER_END_Z, LOWER_RIBBON_Y, LOWER_START_Z};
use crate::snap;
use crate::{P2, P3};
use std::f64::consts::PI;

// The Westbrass and its bore.

/// The shell's centre in Y, behind the shank.
pub const SHELL_CENTER_Y: f64 = 3.175;
/// What every bore clears the donor by.
pub const BORE_CLEARANCE: f64 = 0.25;
/// The donor's round body, and the shell's bore for it.
pub const WESTBRASS_DIAMETER: f64 = 31.5;
pub const WESTBRASS_BORE_DIAMETER: f64 = WESTBRASS_DIAMETER + 2.0 * BORE_CLEARANCE;
pub const WESTBRASS_BORE_X: f64 = 0.0;
pub const WESTBRASS_BORE_Y: f64 = 0.0;
/// The donor's rectangular body in zone 2, and its bore.
pub const WESTBRASS_RECT_LONG_Y: f64 = 31.5;
pub const WESTBRASS_RECT_SHORT_X: f64 = 17.0;
pub const WESTBRASS_BORE_RECT_LONG_Y: f64 = WESTBRASS_RECT_LONG_Y + 2.0 * BORE_CLEARANCE;
pub const WESTBRASS_BORE_RECT_SHORT_X: f64 = WESTBRASS_RECT_SHORT_X + 2.0 * BORE_CLEARANCE;
/// The coves on the rectangle's ±X faces.
pub const COVE_R: f64 = 6.0;
/// How far a bore's cutter runs past the faces it opens.
pub const BORE_OVERRUN: f64 = 2.0;

// Walls.

/// The thinnest wall anywhere on the shell.
pub const WALL_THICKNESS_MIN: f64 = 2.0;
/// The show wall over the donor.
pub const SHOW_WALL: f64 = 4.2;
/// The lip the outer stock keeps over a bore.
pub const SHELL_OUTER_LIP: f64 = WALL_THICKNESS_MIN + BORE_CLEARANCE;

// Zones, up from the counter.

pub const ZONE1_Z_BOTTOM: f64 = 0.0;
pub const ZONE1_Z_TOP: f64 = 13.0;
pub const ZONE1_HEIGHT: f64 = ZONE1_Z_TOP - ZONE1_Z_BOTTOM;
pub const ZONE2_Z_BOTTOM: f64 = ZONE1_Z_TOP;
pub const ZONE2_Z_TOP: f64 = 39.0;
pub const ZONE2_HEIGHT: f64 = ZONE2_Z_TOP - ZONE2_Z_BOTTOM;
/// Where the rectangular bore starts, over the round one.
pub const ZONE2_BORE_Z_BOTTOM: f64 = ZONE1_Z_TOP + BORE_CLEARANCE;
pub const ZONE3_Z_BOTTOM: f64 = ZONE2_Z_TOP;
/// The donor's arches either side of the lever: their feet and their peak.
pub const ARCH_Z_BASE: f64 = 41.0;
pub const ARCH_Z_PEAK: f64 = 46.0;
pub const WESTBRASS_ARCH_INNER_X: f64 = 7.0;
pub const WESTBRASS_ARCH_OUTER_X: f64 = 8.5;
pub const SHELL_ARCH_BORE_INNER_X: f64 = WESTBRASS_ARCH_INNER_X - BORE_CLEARANCE;
pub const SHELL_ARCH_BORE_OUTER_X: f64 = WESTBRASS_ARCH_OUTER_X + BORE_CLEARANCE;
pub const SHELL_ARCH_BORE_Z_FOOT_TOP: f64 = ARCH_Z_BASE + BORE_CLEARANCE;
pub const SHELL_ARCH_BORE_Z_PEAK: f64 = ARCH_Z_PEAK + BORE_CLEARANCE;
pub const SHELL_ARCH_Z_FOOT_TOP: f64 = ARCH_Z_BASE + SHELL_OUTER_LIP;
pub const ZONE4_Z_BOTTOM: f64 = SHELL_ARCH_Z_FOOT_TOP;
pub const ZONE4_Z_TOP: f64 = 57.5;
pub const ZONE5_Z_BOTTOM: f64 = ZONE4_Z_TOP;
/// The seam the gooseneck is swept from.
pub const ZONE5_Z_TOP: f64 = ZONE4_Z_TOP + 10.0;

// The foot and its mounting pods.

/// The oval foot on the above-counter plate.
pub const FOOT_WIDTH: f64 = 58.0;
pub const FOOT_DEPTH: f64 = 59.0;
pub const FOOT_CENTER_Y: f64 = 0.0;
/// The base's three pods: a heat-set insert in each, screwed from under the plate.
pub const BASE_POD_CENTER_X: f64 = 22.5;
pub const BASE_POD_CENTER_Y: f64 = -2.0;
pub const BASE_POD_FRONT_CENTER_X: f64 = 0.0;
pub const BASE_POD_FRONT_CENTER_Y: f64 = -22.3;
pub const BASE_POD_CENTERS: [P2; 3] = [
    [BASE_POD_CENTER_X, BASE_POD_CENTER_Y],
    [-BASE_POD_CENTER_X, BASE_POD_CENTER_Y],
    [BASE_POD_FRONT_CENTER_X, BASE_POD_FRONT_CENTER_Y],
];
pub const BASE_POD_Z_BOTTOM: f64 = ZONE1_Z_BOTTOM;
pub const BASE_POD_WALL: f64 = WALL_THICKNESS_MIN;
/// The M3 screw's clearance through the pedestal and the head's counterbore.
pub const BASE_POD_SHANK_DIA: f64 = 3.9;
pub const BASE_POD_COUNTERBORE_DIA: f64 = 6.15;
/// The insert's pilot, its outside and its length.
pub const BASE_POD_INSERT_DIA: f64 = 4.0;
pub const BASE_INSERT_OUTER_DIA: f64 = 4.6;
pub const BASE_INSERT_LENGTH: f64 = 4.0;
/// The plate's pedestal under each pod, which locates the base.
pub const BASE_PEDESTAL_DIA: f64 = BASE_POD_SHANK_DIA + 2.0 * BASE_POD_WALL;
pub const BASE_PEDESTAL_HEIGHT: f64 = 2.2;
pub const BASE_PEDESTAL_CHAMFER: f64 = 0.4;
/// The socket each pedestal seats in.
pub const BASE_POD_HOLE_DEPTH: f64 = BASE_PEDESTAL_HEIGHT + 1.0;
pub const BASE_INSERT_BOTTOM_Z: f64 = BASE_POD_Z_BOTTOM + BASE_POD_HOLE_DEPTH;
pub const BASE_POD_INSERT_DEPTH: f64 = BASE_INSERT_LENGTH + 1.25;
pub const BASE_POD_Z_TOP: f64 = BASE_INSERT_BOTTOM_Z + BASE_POD_INSERT_DEPTH + BASE_POD_WALL;
pub const BASE_POD_RADIUS: f64 = BASE_INSERT_OUTER_DIA / 2.0 + BASE_POD_WALL;
/// The screw and where its head seats in the plate.
pub const BASE_SCREW_LENGTH: f64 = 8.0;
pub const BASE_SCREW_HEAD_HEIGHT: f64 = 3.0;
pub const BASE_SCREW_HEAD_RECESS: f64 = 0.2;
pub const BASE_SCREW_COUNTERBORE_DEPTH: f64 = BASE_SCREW_HEAD_HEIGHT + BASE_SCREW_HEAD_RECESS;
pub const BASE_SCREW_SEAT_Z: f64 = -ABOVE_COUNTER_PLATE_THICKNESS + BASE_SCREW_COUNTERBORE_DEPTH;
/// The printed wall the screw head bears on.
pub const BASE_PLATE_SEAT_THICKNESS: f64 = BASE_PEDESTAL_HEIGHT - BASE_SCREW_SEAT_Z;

/// The socket each pedestal seats in, across.
pub fn base_pod_hole_dia() -> f64 {
    BASE_PEDESTAL_DIA + 2.0 * slip()
}

// The lever.

/// The donor's lever: its half width, the clearance round it and its swing.
pub const LEVER_X_HALF: f64 = 6.5;
pub const LEVER_FIT_CLEARANCE: f64 = 0.35;
pub const LEVER_SWEEP_ALLOWANCE: f64 = 0.005;
/// The straight corridor the lever goes in by, from the front.
pub const LEVER_INSERTION_FRONT_Y: f64 = -65.0;
/// The lever's back and top at rest.
pub const LEVER_REST_BACK_Y: f64 = 9.0;
pub const LEVER_REST_TOP_Z: f64 = ZONE2_Z_TOP + 13.0;
pub const LEVER_CLEARANCE_X_HALF: f64 = LEVER_X_HALF + LEVER_FIT_CLEARANCE;
pub const LEVER_CLEARANCE_Y_BACK: f64 = LEVER_REST_BACK_Y + LEVER_FIT_CLEARANCE + LEVER_SWEEP_ALLOWANCE;
/// The lever's side profile at rest, in (Y, Z): its paddle and its root over the donor.
pub const LEVER_PROFILE: [P2; 6] = [
    [-42.0, ZONE2_Z_TOP + 10.0],
    [-42.0, LEVER_REST_TOP_Z],
    [LEVER_REST_BACK_Y, LEVER_REST_TOP_Z],
    [LEVER_REST_BACK_Y, ZONE2_Z_TOP + 1.0],
    [-6.0, ZONE2_Z_TOP + 1.0],
    [-6.0, ZONE2_Z_TOP + 4.5],
];
/// The lever's pivot, in (Y, Z).
pub const LEVER_PIVOT: P2 = [1.5, ZONE2_Z_TOP + 7.0];
/// How far it swings, in whole degrees.
pub const LEVER_SWING_DEG: usize = 18;
/// The corridor under the paddle, in front of the root: its rear Y.
pub const LEVER_CORRIDOR_REAR_Y: f64 = -5.9;
/// Where the plateau over the donor's top stands, just below zone 2's top.
pub const LEVER_PLATEAU_Z: f64 = ZONE2_Z_TOP - 0.01;
/// The fill behind the donor, which the lever's back clears.
pub const FILL_Y_MIN: f64 = 10.46;

// The tubes through the shell.

/// The soda tube, on the water's centreline.
pub const SODA_FAUCET_TUBE_Y: f64 = paths::WATER_Y;
pub const SODA_FAUCET_TUBE_OD: f64 = 0.375 * 25.4;
pub const SODA_FAUCET_HOLE_DIAMETER: f64 = SODA_FAUCET_TUBE_OD + 2.0 * BORE_CLEARANCE + 0.2;
/// The flavor pill's centre, where the mounting stack holds the pair.
pub const FLAVOR_PILL_CENTER: P2 = [BUNDLE_SLOT_CENTER_X, FLAVOR_TUBE_DEPTH];
/// The cable's flat lane up the stack: its width, depth and centre along the normal.
pub const SIGNAL_LANE_WIDTH: f64 = 5.0;
pub const SIGNAL_LANE_DEPTH: f64 = 1.8;
pub const SIGNAL_LANE_CENTER_N: f64 = 11.55;
/// The lane in the mounting stack: its exit, its angle and the heights it runs between.
pub const SIGNAL_LOWER_EXIT: P2 = [LOWER_BUNDLE_X, LOWER_RIBBON_Y];
pub const SIGNAL_LOWER_EXIT_ANGLE: f64 = 0.0;
pub const SIGNAL_LANE_BOTTOM_Z: f64 = -6.2;
pub const SIGNAL_LANE_TOP_Z: f64 = 39.0;
/// The straight lands below and above the opening that gathers the tubes into the neck.
pub const BUNDLE_LAND_BELOW: f64 = 0.5;
pub const BUNDLE_LAND_ABOVE: f64 = 0.2;
pub const BUNDLE_LAND_BOTTOM_Z: f64 = ZONE3_Z_BOTTOM - BUNDLE_LAND_BELOW;
/// How far the soda and flavor outlets run back up past where the cable leaves.
pub const BEVERAGE_LEAD: f64 = 0.5;
/// How far the drain's relief starts behind its square end.
pub const DRAIN_RELIEF_LEAD: f64 = 0.25;
/// How far the vent outlet reaches into the soda bore.
pub const VENT_OUTLET_REACH: f64 = 0.6;

/// The pill's edge toward -Y, filled out flat: inside the bore and the pill both.
pub fn flavor_pill_y_minus_edge() -> f64 {
    let reach = BUNDLE_SLOT_LEFT_X.abs().max(BUNDLE_SLOT_RIGHT_X.abs());
    (FLAVOR_TUBE_DEPTH - PILL_WIDTH_Y / 2.0).min(((WESTBRASS_BORE_DIAMETER / 2.0).powi(2) - reach.powi(2)).sqrt())
}

// The outer stock below the seam.

/// The lower shell's sections, `[z, width, depth, centre y]`, lofted up onto the neck.
pub const LOWER_OUTER_SECTIONS: [[f64; 4]; 6] = [
    [0.0, FOOT_WIDTH, FOOT_DEPTH, FOOT_CENTER_Y],
    [8.5, FOOT_WIDTH, FOOT_DEPTH, FOOT_CENTER_Y],
    [20.0, 48.0, 53.5, 4.25],
    [34.0, 44.0, 52.5, 5.25],
    [43.0, 38.0, 50.0, 5.0],
    [59.0, 30.0, 31.0, 11.5],
];
/// Where the loft meets the round neck, and how far the neck's land runs on past the seam.
pub const LOWER_NECK_Z: f64 = 65.0;
pub const NECK_LAND_OVERRUN: f64 = 0.2;

/// The shell's outer radius about its centre: the farther of the bore and the pill, and the show
/// wall.
pub fn shell_outer_r() -> f64 {
    let bore = (SHELL_CENTER_Y - WESTBRASS_BORE_Y) + WESTBRASS_BORE_DIAMETER / 2.0;
    let pill = ((LOWER_BUNDLE_X.abs() + FLAVOR_TUBE_X_OFFSET).hypot(FLAVOR_TUBE_DEPTH - SHELL_CENTER_Y)) + PILL_WIDTH_Y / 2.0;
    bore.max(pill) + SHOW_WALL
}

fn shell_rect_y_min() -> f64 {
    SHELL_CENTER_Y - shell_outer_r()
}

fn shell_rect_y_max() -> f64 {
    SHELL_CENTER_Y + shell_outer_r()
}

/// The arch over the lever's back, from zone 3's floor to zone 4's top: its centre's height and
/// its radius about `FILL_Y_MIN`.
pub fn back_arch_center_z() -> f64 {
    let dy = FILL_Y_MIN - shell_rect_y_min();
    (ZONE4_Z_TOP + ZONE3_Z_BOTTOM) / 2.0 - dy.powi(2) / (2.0 * (ZONE4_Z_TOP - ZONE3_Z_BOTTOM))
}

pub fn back_arch_r() -> f64 {
    ZONE4_Z_TOP - back_arch_center_z()
}

/// The front of the shoulder between zones 4 and 5.
pub fn zone45_front_y() -> f64 {
    let z5_y_min = (SODA_FAUCET_TUBE_Y + TUBE_SHELL_CENTER_Y) - TUBE_SHELL_OUTER_R;
    let z5_y_max = (SODA_FAUCET_TUBE_Y + TUBE_SHELL_CENTER_Y) + TUBE_SHELL_OUTER_R;
    (z5_y_min - (shell_rect_y_max() - z5_y_max)).min((SODA_FAUCET_TUBE_Y - SODA_FAUCET_HOLE_DIAMETER / 2.0) - 4.0 * WALL_THICKNESS_MIN)
}

// The gooseneck.

/// The tube shell round the neck: its centre, out along the normal, and its radius.
pub const TUBE_SHELL_CENTER_Y: f64 = paths::SHELL_CENTER_N;
pub const TUBE_SHELL_OUTER_R: f64 = paths::SHELL_RADIUS;
/// The bend's two sweeps and the straight tip.
pub const GN_BEND1_SWEEP_RAD: f64 = 30.0 * (PI / 180.0);
pub const GN_BEND2_SWEEP_RAD: f64 = 110.0 * (PI / 180.0);
pub const GN_MID_STRAIGHT_LEN: f64 = 0.0;
pub const GN_TIP_STRAIGHT_LEN: f64 = 25.0;
/// The dispense outlet.
pub const GN_OUTLET_Y: f64 = paths::OUTLET_Y;
pub const GN_OUTLET_Z: f64 = paths::OUTLET_Z;
pub const PATH_TOTAL_ROT: f64 = GN_BEND1_SWEEP_RAD + GN_BEND2_SWEEP_RAD;
/// The split joint between the base and the tip prints, round the bend.
pub const SPLIT_JUNCTION_ROT: f64 = paths::JOINT_ANGLE;
/// The base's socket and the tip's plug, along the bend, and their walls.
pub const SPLIT_SOCKET_OVERLAP_LEN: f64 = 20.0;
pub const SPLIT_PLUG_OVERLAP_LEN: f64 = 18.0;
pub const SPLIT_SOCKET_WALL: f64 = WALL_THICKNESS_MIN;
pub const SPLIT_PLUG_WALL: f64 = WALL_THICKNESS_MIN;
pub const SPLIT_SOCKET_SHRINK: f64 = SPLIT_SOCKET_WALL;
/// Each piece's print pose.
pub const PRINT_BASE_BUILD_ROT: f64 = 15.0 * (PI / 180.0);
pub const PRINT_TIP_BUILD_ROT: f64 = (SPLIT_JUNCTION_ROT + PATH_TOTAL_ROT) / 2.0;

/// The joint's slip between socket and plug.
pub fn split_slip() -> f64 {
    2.0 * slip()
}

/// How far the plug is shrunk inside the tube shell.
pub fn split_plug_shrink() -> f64 {
    SPLIT_SOCKET_SHRINK + split_slip() / 2.0
}

/// The bend's radius, from the seam over to the straight tip at the outlet.
pub fn gn_bend1_r() -> f64 {
    ((SODA_FAUCET_TUBE_Y - GN_OUTLET_Y) - GN_TIP_STRAIGHT_LEN * PATH_TOTAL_ROT.sin()) / (1.0 - PATH_TOTAL_ROT.cos())
}

pub fn gn_bend2_r() -> f64 {
    gn_bend1_r()
}

/// Where the bend starts, in Z.
pub fn gn_bend1_z_start() -> f64 {
    (GN_OUTLET_Z - gn_bend1_r() * PATH_TOTAL_ROT.sin()) - GN_TIP_STRAIGHT_LEN * PATH_TOTAL_ROT.cos()
}

/// Where the socket and the plug start, round the bend.
pub fn path_socket_start_rot() -> f64 {
    SPLIT_JUNCTION_ROT - SPLIT_SOCKET_OVERLAP_LEN / gn_bend2_r()
}

pub fn path_plug_start_rot() -> f64 {
    SPLIT_JUNCTION_ROT - SPLIT_PLUG_OVERLAP_LEN / gn_bend2_r()
}

/// The tube exit, the direction back up the gooseneck and the outward normal through the
/// display face.
pub fn tip_frame() -> [P3; 3] {
    let (r1, r2) = (gn_bend1_r(), gn_bend2_r());
    let tan1 = [GN_BEND1_SWEEP_RAD.sin(), GN_BEND1_SWEEP_RAD.cos()];
    let tan2 = [PATH_TOTAL_ROT.sin(), PATH_TOTAL_ROT.cos()];
    let lift = gn_bend1_z_start() - ZONE5_Z_TOP;
    let p2 = [r1 * (1.0 - GN_BEND1_SWEEP_RAD.cos()), lift + r1 * GN_BEND1_SWEEP_RAD.sin()];
    let p3 = [p2[0] + GN_MID_STRAIGHT_LEN * tan1[0], p2[1] + GN_MID_STRAIGHT_LEN * tan1[1]];
    let c2 = [p3[0] + r2 * GN_BEND1_SWEEP_RAD.cos(), p3[1] - r2 * GN_BEND1_SWEEP_RAD.sin()];
    let p4 = [c2[0] - r2 * PATH_TOTAL_ROT.cos(), c2[1] + r2 * PATH_TOTAL_ROT.sin()];
    let p5 = [p4[0] + GN_TIP_STRAIGHT_LEN * tan2[0], p4[1] + GN_TIP_STRAIGHT_LEN * tan2[1]];
    let (ta, tb) = (tan2[0], tan2[1]);
    [[0.0, SODA_FAUCET_TUBE_Y - p5[0], ZONE5_Z_TOP + p5[1]], [0.0, ta, -tb], [0.0, tb, ta]]
}

// The passages up the neck.

/// The circles a section of the tube passage hulls at station `s`: the soda tube, the flavor
/// pair and, with `signal`, the cable's two rounded ends, `[x, n, r]` in the section's plane.
pub fn tube_circles(signal: bool, s: f64) -> Vec<[f64; 3]> {
    let [x, n, _, ribbon, _] = paths::positions(s);
    let mut rows = vec![
        [0.0, 0.0, SODA_FAUCET_HOLE_DIAMETER / 2.0],
        [-x, n, FLAVOR_TUBE_HOLE_DIA / 2.0],
        [x, n, FLAVOR_TUBE_HOLE_DIA / 2.0],
    ];
    if signal {
        let half = (SIGNAL_LANE_WIDTH - SIGNAL_LANE_DEPTH) / 2.0;
        for x in [-half, half] {
            rows.push([x, ribbon, SIGNAL_LANE_DEPTH / 2.0]);
        }
    }
    rows
}

/// A section of a smooth passage: its plane, origin, x direction and normal, and the circles it
/// hulls in it.
#[derive(Clone, Debug)]
pub struct Section {
    pub origin: P3,
    pub xdir: P3,
    pub normal: P3,
    pub circles: Vec<[f64; 3]>,
}

/// Stations from `s0` to `s1`, at most 2 mm apart and at least two spans.
pub fn bundle_stations(s0: f64, s1: f64) -> Vec<f64> {
    let n = (((s1 - s0) / 2.0).ceil() as usize).max(2);
    (0..=n).map(|i| s0 + (s1 - s0) * i as f64 / n as f64).collect()
}

/// Where the tubes finish converging onto the dispense face.
pub fn converged_s() -> f64 {
    paths::converge_start_s() + paths::CONVERGE_LENGTH
}

/// The passage's sections through the tubes' convergence.
pub fn passage_sections() -> Vec<Section> {
    bundle_stations(paths::converge_start_s(), converged_s())
        .into_iter()
        .map(|s| {
            let [origin, xdir, normal] = paths::station_plane(s, 0.0);
            Section { origin, xdir, normal, circles: tube_circles(true, s) }
        })
        .collect()
}

/// The soda opening and the flavor capsule out to the tip, past where the cable leaves.
pub fn beverage_circles() -> Vec<[f64; 3]> {
    tube_circles(false, converged_s())
}

/// The station where the cable leaves the passage for the display.
pub fn ribbon_end_s() -> f64 {
    let angle = PATH_TOTAL_ROT - ((DISPLAY_RIBBON_JOIN_S - GN_TIP_STRAIGHT_LEN) / (gn_bend1_r() + SIGNAL_LANE_CENTER_N)).asin();
    (angle - paths::JOINT_ANGLE) * paths::water_radius()
}

/// The drain's square end: the point on its centreline, the section's x direction and the
/// normal along the bend.
pub fn drain_relief() -> [P3; 3] {
    let s = paths::drain_cut_s();
    let [_, xdir, normal] = paths::station_plane(s, 0.0);
    [paths::tube_arc_point(s, Kind::Drain, 1.0), xdir, normal]
}

/// The vent's round underside outlet: its origin on the shell's centre, its normal down out of
/// the bend, and how far along that normal the hole starts.
pub fn vent_outlet() -> (P3, P3, f64) {
    let station = paths::drip_hole_s();
    let angle = SPLIT_JUNCTION_ROT + station / gn_bend1_r();
    let origin = paths::station_point(station, 0.0, TUBE_SHELL_CENTER_Y);
    let offset = TUBE_SHELL_CENTER_Y + SODA_FAUCET_HOLE_DIAMETER / 2.0 - VENT_OUTLET_REACH;
    (origin, [0.0, -angle.cos(), -angle.sin()], offset)
}

// The opening through the mounting stack.

/// The heights the lower opening is sampled at, about 0.4 mm apart.
pub fn lower_heights() -> Vec<f64> {
    let (z0, z1) = (LOWER_START_Z, LOWER_END_Z);
    let n = ((z1 - z0) / 0.4).ceil() as usize;
    (0..=n).map(|i| z0 + (z1 - z0) * i as f64 / n as f64).collect()
}

/// The circles the lower opening hulls at height `z`, `[x, y, r]`: the soda tube, the flavor
/// pair, the drain and the cable's two ends.
pub fn lower_circles(z: f64) -> Vec<[f64; 3]> {
    let left = paths::lower_point(z, Kind::Flavor, -1.0);
    let right = paths::lower_point(z, Kind::Flavor, 1.0);
    let ribbon = paths::lower_point(z, Kind::Ribbon, 1.0);
    let drain = paths::lower_point(z, Kind::Drain, 1.0);
    let half = (SIGNAL_LANE_WIDTH - SIGNAL_LANE_DEPTH) / 2.0;
    vec![
        [0.0, SODA_FAUCET_TUBE_Y, SODA_FAUCET_HOLE_DIAMETER / 2.0],
        [left[0], left[1], FLAVOR_TUBE_HOLE_DIA / 2.0],
        [right[0], right[1], FLAVOR_TUBE_HOLE_DIA / 2.0],
        [drain[0], drain[1], DRAIN_TUBE_HOLE_DIA / 2.0],
        [ribbon[0] - half, ribbon[1], SIGNAL_LANE_DEPTH / 2.0],
        [ribbon[0] + half, ribbon[1], SIGNAL_LANE_DEPTH / 2.0],
    ]
}

/// The lower opening's sections, `(z, circles)`.
pub fn lower_opening_sections() -> Vec<(f64, Vec<[f64; 3]>)> {
    lower_heights().into_iter().map(|z| (z, lower_circles(z))).collect()
}

// The display on the tip.

/// The display's USB connector, from the vendor's model
/// (`ESP32-S3-Touch-LCD-1_47_20250411.stp`, SHA-256 15fddd5d…0059e): its bounds in the display's
/// frame.
pub const DISPLAY_USB_REFERENCE_BOUNDS: [P3; 2] = [[-4.799962, -22.484226, 0.750479], [4.780038, -14.954223, 4.910479]];
/// The dispense face's thickness at the tip.
pub const DISPENSE_FACE_THICKNESS: f64 = 2.0;
/// The display's seat on the tip, along n.
pub const DISPLAY_SEAT_REFERENCE_N: f64 = 10.1;
/// What the display stands clear of the tubes by, past its seat.
pub const DISPLAY_ADDITIONAL_TUBE_CLEARANCE: f64 = 1.5;
/// The display's feet, along n.
pub const DISPLAY_FEET_N: f64 = DISPLAY_SEAT_REFERENCE_N + DISPLAY_ADDITIONAL_TUBE_CLEARANCE;
/// What the cradle clears the display by.
pub const DISPLAY_CRADLE_CLEARANCE: f64 = 0.25;
/// The display's glass, along n.
pub const DISPLAY_FACE_N: f64 = DISPLAY_FEET_N + DISPLAY_TOTAL_DEPTH;
/// The cover's show wall over the glass.
pub const DISPLAY_COSMETIC_WALL: f64 = 1.3;
/// The cover's top, along n.
pub const DISPLAY_COVER_TOP_N: f64 = DISPLAY_FACE_N + DISPLAY_COVER_OVER_FACE + DISPLAY_COSMETIC_WALL;
/// The cover's skirt bottom and its shoulder, along n.
pub const DISPLAY_COVER_BOTTOM_N: f64 = DISPLAY_SEAT_REFERENCE_N - 6.8;
pub const DISPLAY_COVER_SHOULDER_N: f64 = DISPLAY_SEAT_REFERENCE_N + 0.5;
/// The cover's face, across, and its margin past the display's end.
pub const DISPLAY_COVER_FACE_WIDTH: f64 = 27.5;
pub const DISPLAY_COVER_END_MARGIN: f64 = 1.25;
/// The cover's face and skirt corner radii.
pub const DISPLAY_COVER_FACE_R: f64 = 7.25;
pub const DISPLAY_COVER_SKIRT_R: f64 = 10.0;
/// The front skirt's lower trim plane in the display frame, set by its intercept and slope.
pub const DISPLAY_COVER_FRONT_RIM_N: f64 = 14.0;
pub const DISPLAY_COVER_FRONT_RIM_SLOPE: f64 = 1.8;
/// The rear skirt's lower trim plane in the display frame, set by its intercept and slope.
pub const DISPLAY_COVER_REAR_TRIM_S0: f64 = 42.1;
pub const DISPLAY_COVER_REAR_TRIM_DS_DN: f64 = 0.6;
/// The display's neck: the tube shell.
pub const DISPLAY_NECK_OUTER_R: f64 = TUBE_SHELL_OUTER_R;
/// The cover's head, along s.
pub const DISPLAY_HEAD_S_MIN: f64 = 0.0;
/// The lips that snap the cover on: their band along n, and their radii about the neck.
pub const DISPLAY_CLIP_BOTTOM_N: f64 = DISPLAY_COVER_BOTTOM_N;
pub const DISPLAY_CLIP_TOP_N: f64 = DISPLAY_CLIP_BOTTOM_N + snap::LIP_HEIGHT;
pub const DISPLAY_CLIP_LIP_RADIUS: f64 = DISPLAY_NECK_OUTER_R - snap::ENGAGEMENT;
pub const DISPLAY_CLIP_GROOVE_RADIUS: f64 = DISPLAY_CLIP_LIP_RADIUS - snap::RADIAL_SLIP;
/// The bearing pads under the display: their width and depth.
pub const DISPLAY_FOOT_PAD_WIDTH: f64 = 3.0;
pub const DISPLAY_FOOT_PAD_DEPTH: f64 = WALL_THICKNESS_MIN + DISPLAY_ADDITIONAL_TUBE_CLEARANCE;
/// The pads' places on the housing, from its centre: `[x, s]` offsets.
pub const DISPLAY_FOOT_OFFSETS: [P2; 4] = [[-8.5, -19.5], [-8.5, 19.5], [8.5, -19.5], [8.5, 19.5]];
/// The open channel under the display.
pub const DISPLAY_CHANNEL_HALF_WIDTH: f64 = 6.75;
/// How far the grooves reach past the neck, the pocket past the cover's top and the channel up
/// into the seat.
pub const DISPLAY_GROOVE_REACH: f64 = 1.0;
pub const DISPLAY_POCKET_OVERRUN: f64 = 1.0;
pub const DISPLAY_CHANNEL_OVERLAP: f64 = 0.1;
/// The cable to the display: where it joins the PCB's side, along s; its side run's offset,
/// radius, drop and lift; the gap it keeps to the PCB; and the PCB's terminal.
pub const DISPLAY_WIRE_BEND_RADIUS: f64 = 2.5;
pub const DISPLAY_RIBBON_JOIN_S: f64 = 46.0;
pub const DISPLAY_RIBBON_REFERENCE_START_S: f64 = DISPLAY_RIBBON_JOIN_S + 0.5;
pub const DISPLAY_RIBBON_SIDE_X: f64 = -8.2;
pub const DISPLAY_RIBBON_SIDE_RADIUS: f64 = 8.0;
pub const DISPLAY_RIBBON_SIDE_DROP: f64 = 0.0;
pub const DISPLAY_RIBBON_SIDE_LIFT: f64 = 0.4;
pub const DISPLAY_RIBBON_SIDE_RUN_N: f64 = DISPLAY_SEAT_REFERENCE_N + 1.0;
pub const DISPLAY_RIBBON_PCB_GAP: f64 = 0.3;
pub const DISPLAY_RIBBON_TERMINAL_Y: f64 = -11.0;
pub const DISPLAY_RIBBON_TOP_N: f64 = DISPLAY_FEET_N + DISPLAY_PCB_BOTTOM_Z - DISPLAY_RIBBON_PCB_GAP;

/// The connector's span along the display, rounded out to 0.01 mm.
pub fn display_usb_y_range() -> P2 {
    let [low, high] = DISPLAY_USB_REFERENCE_BOUNDS;
    [(low[1] * 100.0).floor() / 100.0, (high[1] * 100.0).ceil() / 100.0]
}

/// The display's near end along s, its connector clear of the dispense face.
pub fn display_s_bottom() -> f64 {
    (DISPENSE_FACE_THICKNESS - display_usb_y_range()[0]) - DISPLAY_HOUSING_LENGTH / 2.0
}

/// The cradle's far end along s.
pub fn display_s_top() -> f64 {
    (display_s_bottom() + DISPLAY_HOUSING_LENGTH) + 2.0 * DISPLAY_CRADLE_CLEARANCE
}

/// The housing's centre along s.
pub fn display_housing_center_s() -> f64 {
    (display_s_bottom() + DISPLAY_CRADLE_CLEARANCE) + DISPLAY_HOUSING_LENGTH / 2.0
}

/// The bearing pads' centres, `[x, s]`.
pub fn display_foot_centers() -> Vec<P2> {
    DISPLAY_FOOT_OFFSETS
        .iter()
        .map(|[x, s]| [*x, ((display_s_bottom() + DISPLAY_CRADLE_CLEARANCE) + DISPLAY_HOUSING_LENGTH / 2.0) + s])
        .collect()
}

/// The display pocket's top, along n.
pub const DISPLAY_POCKET_TOP_N: f64 = DISPLAY_COVER_TOP_N + DISPLAY_POCKET_OVERRUN;
/// The open channel's top, along n.
pub const DISPLAY_CHANNEL_TOP_N: f64 = DISPLAY_SEAT_REFERENCE_N + DISPLAY_CHANNEL_OVERLAP;
/// The grooves' half width and the core they leave round the neck.
pub const DISPLAY_GROOVE_HALF_X: f64 = DISPLAY_NECK_OUTER_R + DISPLAY_GROOVE_REACH;
pub const DISPLAY_GROOVE_CORE_R: f64 = DISPLAY_NECK_OUTER_R - (DISPLAY_NECK_OUTER_R - DISPLAY_CLIP_GROOVE_RADIUS);
/// Extra clearance along the display face at each end of the groove.
pub const DISPLAY_GROOVE_END_CLEARANCE: f64 = 0.25;
/// Extra depth towards the center of the neck on each side.
pub const DISPLAY_GROOVE_X_CLEARANCE: f64 = 0.75;
/// Inward travel available at the two lower corners of each Sculpted display wing.
pub const DISPLAY_WING_CORNER_GROOVE_DEPTH: f64 = 1.1;
/// The groove's transverse half span, including the blend to the tube skin.
pub const DISPLAY_WING_CORNER_GROOVE_HALF_WIDTH: f64 = 1.4;
/// The groove's run from a corner along the skirt's bottom edge toward the blade.
pub const DISPLAY_WING_CORNER_GROOVE_RUN: f64 = 1.75;
/// The height at which the rear groove fades into the arch.
pub const DISPLAY_WING_CORNER_GROOVE_REAR_END_N: f64 = 8.6;

/// The cover's face along s.
pub fn display_cover_face_length() -> f64 {
    display_s_top() + DISPLAY_COVER_END_MARGIN
}

/// The cover's centre along s.
pub fn display_cover_center_s() -> f64 {
    display_cover_face_length() / 2.0
}

/// The cover's skirt round the neck: across, and along s.
pub fn display_cover_skirt_width() -> f64 {
    2.0 * ((DISPLAY_NECK_OUTER_R + display_cover_slip()) + DISPLAY_COSMETIC_WALL)
}

pub fn display_cover_skirt_length() -> f64 {
    display_cover_face_length() + 5.1
}

/// The skirt's rear end along s.
pub fn display_cover_skirt_rear_s() -> f64 {
    display_cover_center_s() + display_cover_skirt_length() / 2.0
}

/// The cover's head's far end along s.
pub fn display_head_s_max() -> f64 {
    display_cover_skirt_rear_s() + 0.2
}

/// The lips' span along s.
pub fn display_clip_s_bottom() -> f64 {
    ((display_cover_center_s() - display_cover_skirt_length() / 2.0) + DISPLAY_COVER_SKIRT_R) + snap::END_MARGIN
}

pub fn display_clip_s_top() -> f64 {
    ((display_cover_center_s() + display_cover_skirt_length() / 2.0) - DISPLAY_COVER_SKIRT_R) - snap::END_MARGIN
}

/// The cover's cavity, as rows `[width, length, corner r, n]` of its outline, from under the
/// skirt up to over the glass.
pub fn display_cover_inner_rows() -> [[f64; 4]; 3] {
    let skirt = display_cover_skirt_width() - 2.0 * DISPLAY_COSMETIC_WALL;
    [
        [skirt, 50.0, 8.7, DISPLAY_COVER_BOTTOM_N - 1.0],
        [skirt, 50.0, 8.7, DISPLAY_COVER_SHOULDER_N],
        [
            DISPLAY_HOUSING_WIDTH + 2.0 * DISPLAY_CRADLE_CLEARANCE,
            DISPLAY_HOUSING_LENGTH + 2.0 * DISPLAY_CRADLE_CLEARANCE,
            DISPLAY_CORNER_R + DISPLAY_CRADLE_CLEARANCE,
            DISPLAY_FACE_N + DISPLAY_COVER_OVER_FACE,
        ],
    ]
}

/// The prism the cavity is clamped to, `[half x, s0, s1, n0, n1]`.
pub fn display_cover_inner_clamp() -> [f64; 5] {
    [50.0, -20.0, display_s_top(), -30.0, 40.0]
}
