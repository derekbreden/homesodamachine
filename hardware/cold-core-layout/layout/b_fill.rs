//! Reservoir B's fill tube through the cap: it enters the cap's front face level, turns down on
//! the accepted R14 bend holder's arc, and drops straight into the reservoir's fill seat. The cap
//! cuts the tube's channel and holds the bend holder; the shell cuts the channel's air where the
//! cup meets it. Points are in enclosure (world) millimetres.
use crate::cap::cap_lid_pose;
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as core;

/// The bend's centreline radius: the accepted holder's.
pub const BEND_RADIUS: f64 = 14.;
/// The channel's bore, the holder's wall round it, and the channel's centre off the holder's back.
pub const CHANNEL_DIAMETER: f64 = 6.8;
pub const CHANNEL_RADIUS: f64 = CHANNEL_DIAMETER / 2.;
pub const WALL: f64 = 2.;
pub const CHANNEL_CENTRE: f64 = WALL + CHANNEL_RADIUS;
/// The holder's domed back rises this far over a square one, to print without support.
pub const DOME_LIFT: f64 = (std::f64::consts::SQRT_2 - 1.) * CHANNEL_RADIUS;
/// The insertion lead-in at each mouth.
pub const MOUTH: f64 = 0.5;
/// The lead-in's cone starts this far outside its face, wide enough that its surface crosses the
/// face at the lead-in's radius, and ends this far past the lead-in's depth, just inside the bore.
pub const MOUTH_OVERRUN: f64 = 0.3;
pub const MOUTH_MERGE: f64 = 0.05;
/// How far under the cup's floor the tube's tip reaches into the reservoir's fill seat.
pub const TIP_DROP: f64 = 5.4;
/// The cap stock round the passage, beside it and beyond its turn.
pub const STOCK_HALF_WIDTH: f64 = 16.5;
pub const STOCK_BEYOND_TURN: f64 = 15.;

/// The passage, worked from the cap lid's pose and the casing.
#[derive(Clone, Copy, Debug)]
pub struct Passage {
    /// Where the tube enters the cap's front face, and the way it points out of it.
    pub entry: [f64; 3],
    pub outward: [f64; 3],
    /// The route's corners: the entry, the bend's corner and the tip.
    pub route: [[f64; 3]; 3],
    /// Where the bend's arc ends, pointing straight down.
    pub bend_end: [f64; 3],
    /// Where the tube leaves the cup's floor, and its tip in the seat.
    pub outlet: [f64; 3],
    pub tip: [f64; 3],
    /// The cup's floor and top, the lid's underside and its face.
    pub cup_floor_z: f64,
    pub cup_top_z: f64,
    pub lid_bottom_z: f64,
    pub lid_face_z: f64,
    /// The allowance the channel's roof takes, printed over support toward print-up.
    pub roof_allowance: f64,
    /// The cap stock the passage is cut through.
    pub stock_min: [f64; 3],
    pub stock_max: [f64; 3],
}

impl Passage {
    /// The stock left over the channel's throat, and over its entry lead-in.
    pub fn throat_roof_stock(&self) -> f64 {
        self.lid_face_z - (self.entry[2] + CHANNEL_RADIUS + self.roof_allowance)
    }

    pub fn entry_leadin_roof_stock(&self) -> f64 {
        self.lid_face_z - (self.entry[2] + CHANNEL_RADIUS + MOUTH + self.roof_allowance)
    }

    /// The straight leg from the entry to where the bend begins.
    pub fn inlet_leg(&self) -> f64 {
        self.bend_end[1] - BEND_RADIUS - self.entry[1]
    }
}

/// Reservoir B's fill conduit, in the cap's frame: over the reservoir's fill bore, the cap spun a
/// half turn on the shell.
pub fn conduit_xy() -> [f64; 2] {
    let side = -1;
    let port = core::reservoir_port(&core::RESERVOIR_FILL_PORT, side).expect("reservoir B's fill port");
    [-port[0], -port[1]]
}

pub fn passage() -> Passage {
    let fits = catalog::fits();
    let pose = cap_lid_pose();
    let lid_bottom = pose.translation[2];
    let floor = lid_bottom - core::top_cap_height(&fits) + core::cap_shell_clearance(&fits);
    let [cx, cy] = conduit_xy();
    let [x, y, _] = pose.point([cx, cy, 0.]);
    let front = pose.point([core::OUTER_SHELL_X_LENGTH / 2., 0., 0.])[1];
    let face = crate::cap::cap_face_z();
    let entry = [x, front, floor + BEND_RADIUS];
    let tip = [x, y, floor - TIP_DROP];
    Passage {
        entry,
        outward: [0., -1., 0.],
        route: [entry, [x, y, entry[2]], tip],
        bend_end: [x, y, floor],
        outlet: [x, y, floor],
        tip,
        cup_floor_z: floor,
        cup_top_z: lid_bottom - core::cap_lid_clearance(&fits),
        lid_bottom_z: lid_bottom,
        lid_face_z: face,
        roof_allowance: fits.supported_surface,
        stock_min: [x - STOCK_HALF_WIDTH, front, floor],
        stock_max: [x + STOCK_HALF_WIDTH, y + STOCK_BEYOND_TURN, face],
    }
}
