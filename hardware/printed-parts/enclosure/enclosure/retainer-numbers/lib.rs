//! The lower pump retainer's numbers: its snap wings' section, catch and spread, the cartridge's
//! planes in the machine frame, and the snap's end planes and the receivers' faces, which
//! front-top's pump mount takes.
use hsm_enclosure_numbers::catalog::{clearance, running};
use hsm_enclosure_numbers::layout::{snap_tip_air, snap_tip_rise};
use hsm_enclosure_numbers::pump::tray;
use hsm_enclosure_numbers::shell::{FRONT_PLANE_Y, FRONT_TOP_FLANK_T, WALL, Z_SEAM, shell};
use hsm_enclosure_numbers::spec::Box;

pub const WING_THICK: f64 = 2.0;
pub const WING_LENGTH: f64 = 22.25;
pub const ROOT_RADIUS: f64 = 1.5;
pub const CATCH_OVERLAP: f64 = 2.6;
pub const CATCH_AIR: f64 = 0.4;
pub const PRY_WIDTH: f64 = 5.0;
pub const RELAXED_SPREAD: f64 = 0.35;
pub const SEATED_SPREAD: f64 = 0.10;

/// The cartridge's planes in the machine frame.
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
    let e = shell();
    let trays = &b.pack.pump_trays;
    let flange = trays.iter().map(|t| t[2]).fold(f64::INFINITY, f64::min) - e.pump_seated_drop;
    let grown = FRONT_TOP_FLANK_T - WALL;
    let head_y = trays.iter().map(|t| t[1]).sum::<f64>() / trays.len() as f64;
    Datums {
        flange_z: flange,
        bearing_z: flange + clearance(false, true, false),
        retainer_top_z: flange - running(),
        bottom_z: e.bay_floor_z(trays).1,
        x0: b.inner[0] + grown + running(),
        x1: b.inner[1] - grown - running(),
        y0: FRONT_PLANE_Y + running(),
        y1: e.pump_cartridge_aft_y(trays, &b.pack.collet_plate),
        head_y,
        motor_y: head_y + tray().rear_axis_y_shift,
    }
}

/// The snap's common end planes, its spring section and the receivers' bearing and access faces.
pub struct SnapDatums {
    pub carrier_inner_x: f64,
    pub wing_inner_x: f64,
    pub wing_outer_x: f64,
    pub hook_outer_x: f64,
    pub hook_ramp_z: f64,
    pub root_z: f64,
    pub floor_z: f64,
    pub receiver_floor_z: f64,
    pub receiver_inner_x: f64,
    pub receiver_back_x: f64,
    pub receiver_outer_x: f64,
    pub receiver_y0: f64,
    pub receiver_y1: f64,
    pub receiver_z0: f64,
    pub receiver_z1: f64,
    pub receiver_roof_z: f64,
    pub port_inner_x: f64,
    pub port_outer_x: f64,
    pub port_y0: f64,
    pub port_y1: f64,
    pub port_z0: f64,
}

pub fn snap_datums(b: &Box) -> SnapDatums {
    let d = datums(b);
    let outer = d.x1;
    let floor = d.bottom_z;
    let cy = (d.y0 + d.y1) / 2.0;
    let edge = outer + running();
    let hook = edge + CATCH_OVERLAP - SEATED_SPREAD;
    let inward = hook + RELAXED_SPREAD - edge + 0.5;
    SnapDatums {
        carrier_inner_x: outer - WING_THICK - inward,
        wing_inner_x: outer - WING_THICK,
        wing_outer_x: outer,
        hook_outer_x: hook,
        hook_ramp_z: floor + snap_tip_rise(),
        root_z: floor + WING_LENGTH,
        floor_z: floor,
        receiver_floor_z: floor - CATCH_AIR,
        receiver_inner_x: edge,
        receiver_back_x: hook + SEATED_SPREAD,
        receiver_outer_x: b.outer[1],
        receiver_y0: d.y0 - running(),
        receiver_y1: d.y1 + running(),
        receiver_z0: Z_SEAM + running(),
        receiver_z1: floor + WING_LENGTH + 3.0 * WALL,
        receiver_roof_z: floor + snap_tip_rise() + snap_tip_air(),
        port_inner_x: outer + running(),
        port_outer_x: b.outer[1] - WALL,
        port_y0: cy - PRY_WIDTH / 2.0,
        port_y1: cy + PRY_WIDTH / 2.0,
        port_z0: floor - 5.0,
    }
}
