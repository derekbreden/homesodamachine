//! The two-body PETG mold the funnel is cast in, in the funnel's frame: the cavity takes the
//! funnel's outside with a finish allowance, the core its wet inside, and a stainless rod forms
//! the spout's bore. Both bodies print on flat bases under steep corbels; bolts through the flange
//! clamp them, locators register them, and the core carries the fill and vent ports.
use crate::{Color, P2, catalog, funnel};

/// The allowance the cavity and core stand off the finished funnel, and the forming join's.
pub const FINISH: f64 = 0.30;
pub const JOIN_ALLOWANCE: f64 = 0.01;
/// The shells' wall, their corbels' run per rise, and the cavity's base.
pub const SHELL: f64 = 5.0;
pub const CORBEL: f64 = 0.5;
pub const BASE: f64 = 5.0;
/// The flange: its thickness, its margin past the apron and its corners.
pub const FLANGE_T: f64 = 5.0;
pub const FLANGE_MARGIN: f64 = 16.0;
pub const FLANGE_R: f64 = 47.0;
/// The clamping bolts: their bore, their edge margin, their stations and their side pockets.
pub const BOLT_DIAMETER: f64 = 5.0;
pub const BOLT_EDGE: f64 = 6.0;
pub const BOLT_STATION: f64 = 50.0;
pub const BOLT_POCKET_WIDTH: f64 = 12.0;
/// The locator pegs: their diameter, height, lead-in, clearance, slot travel and stations.
pub const LOCATOR_D: f64 = 8.0;
pub const LOCATOR_H: f64 = 3.0;
pub const LOCATOR_LEADIN: f64 = 1.0;
pub const LOCATOR_CLEAR: f64 = 0.60;
pub const LOCATOR_TRAVEL: f64 = 1.5;
pub const LOCATOR_X: f64 = 25.0;
pub const LOCATOR_FRONT: f64 = 11.0;
/// The stainless rod that forms the spout's bore, the guide it slides in and its floor seat.
pub const ROD_DIAMETER: f64 = funnel::SPOUT_ID;
pub const ROD_LENGTH: f64 = 25.0;
pub const ROD_CLEAR: f64 = 0.40;
pub const ROD_GUIDE: f64 = 8.0;
pub const ROD_SOCKET: f64 = 1.5;
/// The fill and vent ports through the core.
pub const POUR_DIAMETER: f64 = 11.0;
pub const VENT_DIAMETER: f64 = 4.0;
/// The pry notches round the cavity's rim.
pub const PRY_WIDTH: f64 = 16.0;
pub const PRY_DEPTH: f64 = 5.0;
pub const PRY_HEIGHT: f64 = 1.0;
/// The reserve under the rod's seat.
pub const FLOOR_RESERVE: f64 = 0.7;
/// The vacuum chamber the closed mold goes into.
pub const CHAMBER_D: f64 = 299.72;
/// The overlap the checks allow between bodies that must not meet.
pub const TOLERANCE: f64 = 0.0001;

/// The mold's numbers, as its geometry draws it, in the funnel's frame.
pub struct Mold {
    pub funnel: funnel::Dimensions,
    pub floor_z: f64,
    pub back_z: f64,
    pub flange_size: P2,
    pub base_size: P2,
    pub base_radius: f64,
    pub corbel_z: P2,
    pub bolt_limits: P2,
    pub bolt_xy: Vec<P2>,
    pub locator_xy: [P2; 2],
    pub pour_xy: P2,
    pub vent_xy: [P2; 5],
    pub cavity_color: Color,
    pub core_color: Color,
    pub funnel_color: Color,
    pub rod_color: Color,
}

/// The mold round the funnel as cast.
pub fn mold() -> Mold {
    let f = funnel::dimensions();
    let (top, end) = (f.top_z, f.end_z);
    let floor = end - ROD_SOCKET - SHELL - FLOOR_RESERVE;
    let back = top + FLANGE_T;
    let width = funnel::APRON_W + 2.0 * FLANGE_MARGIN;
    let depth = funnel::APRON_D + 2.0 * funnel::APRON_Y.abs() + 2.0 * FLANGE_MARGIN;
    let (bx, by) = (width / 2.0 - BOLT_EDGE, depth / 2.0 - BOLT_EDGE);
    let (z0, z1) = (floor + BASE, top - FLANGE_T);
    let run = (z1 - z0) * CORBEL;
    let port_x = funnel::APRON_W / 2.0 - 14.5;
    let front_y = funnel::APRON_Y - funnel::APRON_D / 2.0 + 10.0;
    let rear_y = funnel::APRON_Y + funnel::APRON_D / 2.0 - 12.0;
    let locator_front = funnel::APRON_Y - funnel::APRON_D / 2.0 - LOCATOR_FRONT;
    let mut bolts = vec![];
    for side in [-1.0, 1.0] {
        for station in [-1.0, 1.0] {
            bolts.push((side * bx, station * BOLT_STATION));
        }
    }
    for side in [-1.0, 1.0] {
        for station in [-1.0, 1.0] {
            bolts.push((station * BOLT_STATION, side * by));
        }
    }
    Mold {
        funnel: f,
        floor_z: floor,
        back_z: back,
        flange_size: (width, depth),
        base_size: (width - 2.0 * run, depth - 2.0 * run),
        base_radius: FLANGE_R - run,
        corbel_z: (z0, z1),
        bolt_limits: (bx, by),
        bolt_xy: bolts,
        locator_xy: [(LOCATOR_X, locator_front), (-LOCATOR_X, locator_front)],
        pour_xy: (-port_x, front_y),
        vent_xy: [(port_x, front_y), (port_x, rear_y), (-port_x, rear_y), (-funnel::APRON_W / 2.0 + 7.0, 0.0), (funnel::APRON_W / 2.0 - 7.0, 0.0)],
        cavity_color: catalog::hex("#3D9998"),
        core_color: catalog::hex("#D8A751"),
        funnel_color: catalog::hex("#555C68"),
        rod_color: catalog::hex("#AAB9C8"),
    }
}
