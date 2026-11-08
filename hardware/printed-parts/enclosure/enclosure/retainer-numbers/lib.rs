//! The pump cartridge's bearing channels and the cavity the enclosure grows over them.
use hsm_enclosure_numbers::catalog::{clearance, running};
use hsm_enclosure_numbers::pump::tray;
use hsm_enclosure_numbers::shell::{FRONT_PLANE_Y, FRONT_TOP_FLANK_T, WALL, shell};
use hsm_enclosure_numbers::spec::Box;

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

/// The slide-in cartridge's section, shared with its corbeled enclosure cavity.
pub struct Channels {
    pub x0: f64,
    pub x1: f64,
    pub end_x: f64,
    pub fore_y: f64,
    pub aft_y: f64,
    pub fore_groove_y: f64,
    pub aft_groove_y: f64,
    pub lower_fore_y: f64,
    pub lower_aft_y: f64,
    pub upper_fore_y: f64,
    pub upper_aft_y: f64,
    pub support_z: f64,
    pub bearing_z: f64,
    pub bottom_z: f64,
    pub top_z: f64,
}

pub fn channels(b: &Box) -> Channels {
    let (d, e, t) = (datums(b), shell(), tray());
    let support = e.pump_skirt_support_z(&b.pack.pump_trays);
    Channels {
        x0: d.x0,
        x1: d.x1,
        end_x: d.x1 - WALL,
        fore_y: FRONT_PLANE_Y - WALL - running(),
        aft_y: d.y1,
        fore_groove_y: d.head_y - t.head_half - e.cap_pump_air,
        aft_groove_y: d.head_y + t.skirt_open_y_max,
        lower_fore_y: d.head_y + t.skirt_body_open_y_bounds[0],
        lower_aft_y: d.head_y + t.skirt_body_open_y_bounds[1],
        upper_fore_y: d.motor_y - t.boss_half - e.cap_boss_air,
        upper_aft_y: d.motor_y + t.boss_half + e.cap_boss_air,
        support_z: support,
        bearing_z: d.bearing_z,
        bottom_z: support - 2.0 * WALL,
        top_z: d.bearing_z + 2.0 * WALL,
    }
}
