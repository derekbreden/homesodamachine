//! The independent pump retainers share their flange bearings, screw stations and loading rooms with front-top.
use hsm_enclosure_numbers::catalog::{clearance, running};
use hsm_enclosure_numbers::pump::tray;
use hsm_enclosure_numbers::shell::{FRONT_PLANE_Y, FRONT_TOP_FLANK_T, WALL};
use hsm_enclosure_numbers::spec::Box;

pub const HALF_X: f64 = 45.5;
pub const SCREW_OFFSET_X: f64 = 39.0;
pub const POST_HALF_X: f64 = 6.5;
pub const SCREW_Y: f64 = 22.0;
pub const BAR_AFT_Y: f64 = 28.05;
pub const NOTCH_FORE_Y: f64 = 18.25;
pub const NOTCH_HALF_X: f64 = 27.5;
pub const BAR_HEIGHT: f64 = 21.0;
pub const LOWER_BEARING_AIR: f64 = 0.15;
pub const HEAD_WELL_HALF: f64 = 32.5;
pub const OUTLET_ROOM_HALF: f64 = 7.4;
pub const OUTLET_ROOM_FORE: f64 = 3.0;
pub const ADAPTER_RADIUS: f64 = 27.5;
pub const ADAPTER_TOP: f64 = 21.2;
pub const TERMINAL_KEY_X: f64 = 13.4;
pub const TERMINAL_KEY_Y: f64 = -12.8;
pub const TERMINAL_KEY_RADIUS: f64 = 5.0;
pub const TERMINAL_KEY_TOP: f64 = 69.2;
pub const UPPER_STOP_HALF_X: f64 = 18.0;
pub const UPPER_STOP_FORE_Y: f64 = 13.5;
pub const UPPER_STOP_AFT_Y: f64 = 17.75;
pub const POST_BOTTOM: f64 = -7.174;
pub const POST_TOP: f64 = 18.326;
pub const POST_FORE_Y: f64 = 18.0;
pub const POST_AFT_Y: f64 = 26.2;
pub const INSERT_LENGTH: f64 = 4.0;
pub const INSERT_DIAMETER: f64 = 4.6;
pub const PILOT_DIAMETER: f64 = 4.0;
pub const TIP_ROOM: f64 = 8.0;
pub const SCREW_LENGTH: f64 = 25.0;
pub const SCREW_DIAMETER: f64 = 3.0;
pub const CLEARANCE_DIAMETER: f64 = 3.4;
pub const HEAD_DIAMETER: f64 = 5.5;
pub const HEAD_HEIGHT: f64 = 3.0;
pub const COUNTERBORE_DIAMETER: f64 = 6.2;
pub const COUNTERBORE_DEPTH: f64 = 1.0;
pub const HEX_KEY: f64 = 2.5;

/// The mount's bearing planes and the retainer's envelope in the machine frame.
pub struct Datums {
    pub flange_z: f64,
    pub bearing_z: f64,
    pub retainer_top_z: f64,
    pub bottom_z: f64,
    pub x0: f64,
    pub x1: f64,
    pub y0: f64,
    pub y1: f64,
    pub head_y: f64,
    pub motor_y: f64,
}

pub fn datums(b: &Box) -> Datums {
    let trays = &b.pack.pump_trays;
    let flange = trays.iter().map(|p| p[2]).fold(f64::INFINITY, f64::min)
        - hsm_enclosure_numbers::shell::shell().pump_seated_drop;
    let top = flange - tray().skirt_depth - LOWER_BEARING_AIR;
    let head_y = trays.iter().map(|p| p[1]).sum::<f64>() / trays.len() as f64;
    let grown = FRONT_TOP_FLANK_T - WALL;
    Datums {
        flange_z: flange,
        bearing_z: flange + clearance(false, true, false),
        retainer_top_z: top,
        bottom_z: top - BAR_HEIGHT,
        x0: b.inner[0] + grown + running(),
        x1: b.inner[1] - grown - running(),
        y0: FRONT_PLANE_Y + running(),
        y1: BAR_AFT_Y,
        head_y,
        motor_y: head_y + tray().rear_axis_y_shift,
    }
}

pub fn screw_xs(centre: f64) -> [f64; 2] {
    [centre - SCREW_OFFSET_X, centre + SCREW_OFFSET_X]
}

pub fn guide_start(b: &Box) -> f64 {
    datums(b).flange_z + ADAPTER_TOP + ADAPTER_RADIUS - tray().can_half
}

pub fn guide_end(b: &Box) -> f64 {
    datums(b).flange_z + tray().motor_crown - WALL
}

pub fn insert_start(b: &Box) -> f64 {
    datums(b).flange_z + POST_BOTTOM
}
