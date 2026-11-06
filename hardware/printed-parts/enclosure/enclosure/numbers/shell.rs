//! The enclosure shell's own dimensions: its walls, seams and the bays it holds the pack in.
use crate::catalog::{clearance, running};
use crate::pump::tray;
use crate::spec::ColletPlate;
pub use hsm_enclosure_interface::{
    HEATSET_DIA, HEATSET_LONG_LEN, REAR_PLANE_Y, WALL, Y_STACK_HIGH_DEPTH, funnel_collar_air, slide_slip,
};
use hsm_enclosure_interface::{PUMP_STATION_DROP, pump_seated_drop};
use std::sync::OnceLock;

/// The one level line the bottom and top pieces part at.
pub const Z_SEAM: f64 = 160.0;
/// The show edges' round, and the plan corners' round twice that.
pub use hsm_enclosure_interface::swept::SHOW_EDGE_R;
pub const CORNER_ROUND: f64 = 2.0 * SHOW_EDGE_R;
/// The corner columns stand on the cavity's corners at the plan round.
pub const COLUMN_ROUND: f64 = CORNER_ROUND;
pub const COLUMN_CORNERS: [(f64, f64); 4] = [(-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0)];
pub const APPLIANCE_WIDTH: f64 = 215.0;
/// The floor slab, before its seat drop.
pub const FLOOR_T: f64 = 6.0;
/// The Y joint's lip, and the margin the seam keeps behind it.
pub const LIP_LEN: f64 = 17.8;
pub const Z_LIP_Y_MARGIN: f64 = 2.0;
/// Each quadrant's flank: its wall and grown band together.
pub const BACK_TOP_FLANK_T: f64 = 9.0;
pub const BACK_BOTTOM_FLANK_T: f64 = 9.0;
pub const FRONT_BOTTOM_FLANK_T: f64 = 9.0;
pub const FRONT_TOP_FLANK_T: f64 = 9.0;
/// The front wall's interior datum and its wall.
pub const FRONT_PLANE_Y: f64 = 14.0;
/// The Y joint the declared halves part at.
pub const Y_SEAM: f64 = 200.0;
pub const FRONT_WALL: f64 = 9.0;
/// The back-top's rear wall and ceiling sections.
pub const BACK_TOP_WALL_T: f64 = 9.0;
pub const BACK_TOP_CEILING_T: f64 = 9.0;
pub const APPLIANCE_HEIGHT: f64 = 361.0;
/// The side bands' inset from the flank face.
pub const SIDE_BAND_INSET: f64 = 14.0;

/// The Z rails: the hook's foot over the seam, its lap and arm, the rise of its head.
pub const HOOK_FOOT: f64 = 8.7;
pub const HOOK_LAP: f64 = 2.0;
pub const Z_RISE: f64 = 14.8;
pub const HOOK_ARM: f64 = 4.5;
pub const RAIL_STOP_LEN: f64 = 4.0;
pub const RAIL_ENTRY: f64 = 5.0;
pub const RAIL_LEAD: f64 = 2.0;
pub const FRONT_HOOK_LAP: f64 = HOOK_LAP + (FRONT_BOTTOM_FLANK_T - 2.0 * WALL);
pub const BACK_HOOK_LAP: f64 = HOOK_LAP + (BACK_BOTTOM_FLANK_T - 2.0 * WALL);

/// The handholds under each flank.
pub const HANDHOLD_Y: f64 = 214.0;
pub const HANDHOLD_LENGTH: f64 = 80.0;
pub const HANDHOLD_HEIGHT: f64 = 35.0;
pub const HANDHOLD_WALL: f64 = WALL;
pub const HANDHOLD_ROOF: f64 = 4.0 * WALL;
pub const HANDHOLD_CORNER_R: f64 = SHOW_EDGE_R;
pub const HANDHOLD_EDGE_R: f64 = SHOW_EDGE_R;

/// The Y-joint screw stacks: axes, bores, rods and their datums.
pub const Y_STACK_AXIS_IN: f64 = 6.8;
pub const Y_STACK_LOWER_AXIS_IN: f64 = 6.25;
pub const Y_STACK_FRONT_ROOT: f64 = WALL;
pub const Y_STACK_CBORE_DIA: f64 = 9.0;
pub const Y_STACK_HEAD_RECESS: f64 = 3.0;
pub const Y_STACK_HEAD_H: f64 = 5.0;
pub const Y_STACK_CBORE_DEPTH: f64 = Y_STACK_HEAD_RECESS + Y_STACK_HEAD_H;
pub const Y_STACK_TIP_CLEARANCE: f64 = 2.5;
pub const Y_STACK_SCREW_LENGTH_TOLERANCE: f64 = 0.8;
pub const Y_STACK_UPPER_CHAMFER: f64 = 5.1;
pub const LOWER_ROD_LEN: f64 = 100.0;
pub const UPPER_ROD_LEN: f64 = LOWER_ROD_LEN;
pub const Y_STACK_LOWER_ANCHOR_FACE_DROP: f64 = 34.05;
pub const Y_STACK_LOWER_PLANE_OVER_SEAT: f64 = 0.3;
pub const Y_STACK_UPPER_DATUM: f64 = 265.0;
pub const Y_STACK_UPPER_HEAD_DATUM: f64 = 321.5;

/// M3 and M5 inserts and their bosses.
pub const HEATSET_DEPTH: f64 = 5.25;
pub const MOUNT_BOSS_DIA: f64 = 8.0;
pub const MOUNT_BORE_RELIEF: f64 = 1.0;
pub const FLOOR_HEATSET_DIA: f64 = 6.4;
pub const FLOOR_HEATSET_DEPTH: f64 = 9.5;
pub const FLOOR_HEATSET_MIN_WALL: f64 = 2.6;
pub const RELIEF_CHAMFER: f64 = 45.0;

/// The MQ6 card's rails.
pub const MQ6_RAIL_WALL: f64 = 3.0;
pub const MQ6_GRIP: f64 = 5.0;
pub const MQ6_HEADER_RELIEF: f64 = 2.0;

/// The condenser's slot cradles and mount.
pub const COND_RAIL_WALL: f64 = 3.0;
pub const COND_SLOT_GRIP: f64 = 3.0;
pub const COND_SCREW_LEN: f64 = 8.0;
pub const COND_BORE_DEPTH: f64 = COND_SCREW_LEN + MOUNT_BORE_RELIEF;
pub const COND_BOSS_T: f64 = COND_BORE_DEPTH + COND_RAIL_WALL;
/// The lands under the collet plate's ends: their reach inboard, run, section and corbel.
pub const PLATE_FOOT_REACH: f64 = 10.0;
pub const PLATE_FOOT_Y: f64 = 20.0;
pub const PLATE_FOOT_T: f64 = 3.0;
pub const PLATE_FOOT_CORBEL_ANGLE: f64 = 45.0;

/// The fridge's reliefs the front strip and the power box take: `[x0, x1, z0, z1, face]`.
pub const FRIDGE_RELIEFS: [[f64; 5]; 2] = [[-71.0, 29.0, 0.0, 17.0, 11.0], [-45.5, 3.5, 28.0, 77.0, 11.0]];

/// The core's stops and holds.
pub const CORE_STOP_WEB: f64 = 6.0;
pub const CORE_STOP_RISE: f64 = 40.0;
pub const CORE_HOLD_REACH: f64 = 12.0;
pub const CORE_HOLD_LAND: f64 = 8.0;
pub const CORE_HOLD_RISE: f64 = 40.0;

/// The PRV chase on the west wall.
pub const VENT_CHANNEL_W: f64 = 12.0;
pub const VENT_RIB_WALL: f64 = 3.0;
pub const VENT_DUCT_DROP: f64 = 25.0;
pub const VENT_GROOVE_DROP: f64 = 25.0;
pub const VENT_RAMP_ANGLE: f64 = RELIEF_CHAMFER;

/// The raised disposal warning on the rear face.
pub const DISPOSAL_LINES: [&str; 6] = [
    "CAUTION",
    "RISK OF FIRE OR EXPLOSION.",
    "DISPOSE OF PROPERLY IN",
    "ACCORDANCE WITH THE APPLICABLE",
    "FEDERAL OR LOCAL REGULATIONS.",
    "FLAMMABLE REFRIGERANT USED.",
];
pub const DISPOSAL_FONT: &str = "Helvetica";
pub const DISPOSAL_CAP_HEIGHT: f64 = 6.5;
pub const DISPOSAL_RAISE: f64 = 0.6;
pub const DISPOSAL_EMBED: f64 = 0.1;
pub const DISPOSAL_LINE_GAP: f64 = 2.5;
pub const DISPOSAL_BOTTOM: f64 = 14.0;
pub const DISPOSAL_MARGIN: f64 = 5.0;

/// The exterior flutes.
pub const FLUTE_COUNT: f64 = 272.0;
pub const FLUTE_DEPTH: f64 = 1.2;
pub const FLUTE_RISE: f64 = 5.0;

/// The back-top wall's interior face.
pub fn back_top_wall_face() -> f64 {
    REAR_PLANE_Y - (BACK_TOP_WALL_T - WALL)
}

/// The back-top ceiling's underside.
pub fn back_top_ceiling_face() -> f64 {
    APPLIANCE_HEIGHT - FLOOR_T - BACK_TOP_CEILING_T
}

/// The floor slab under the seat drop a sliding floor fit takes.
pub fn slab_t() -> f64 {
    FLOOR_T - clearance(true, false, true)
}

/// How far a rail's flare drops under its head, from the arm's end back to the wall.
pub fn rail_flare_drop() -> f64 {
    slide_slip() + HOOK_ARM + 0.5
}

/// The lower Y stacks stand in the side band, a running fit off its face.
pub fn y_stack_low_depth() -> f64 {
    SIDE_BAND_INSET - running()
}

pub struct Shell {
    /// The pump stations' drop below their declared Z, and the seated pump's below the cap.
    pub pump_station_drop: f64,
    pub pump_seated_drop: f64,
    pub pump_relief_z_air: f64,
    pub pump_cartridge_z_clearance: f64,
    pub pump_bay_floor_relief: f64,
    /// The cartridge's kiss against the collet plate, and what a station may take of it.
    pub cap_kiss: f64,
    pub cap_kiss_station_allowance: f64,
    /// The pump wells' air off the case, and the outlet tube opening's half width.
    pub cap_pump_air: f64,
    pub cap_boss_air: f64,
    pub cap_fitting_half: f64,
    pub teardrop_roof_angle: f64,
}

pub fn shell() -> &'static Shell {
    static SHELL: OnceLock<Shell> = OnceLock::new();
    SHELL.get_or_init(|| Shell {
        pump_station_drop: PUMP_STATION_DROP,
        pump_seated_drop: pump_seated_drop(),
        pump_relief_z_air: 1.0,
        pump_cartridge_z_clearance: running(),
        pump_bay_floor_relief: 2.6,
        cap_kiss: running(),
        cap_kiss_station_allowance: 0.01,
        cap_pump_air: 0.4,
        cap_boss_air: running(),
        cap_fitting_half: tray().shaft_w / 2.0,
        teardrop_roof_angle: 36.0,
    })
}

impl Shell {
    /// The cap splits at the highest pump station's declared plane.
    pub fn cap_split_z(&self, trays: &[[f64; 3]]) -> f64 {
        trays.iter().map(|t| t[2]).fold(f64::INFINITY, f64::min)
    }

    /// Where the seated pump skirt bears on the retainer's lands.
    pub fn pump_skirt_support_z(&self, trays: &[[f64; 3]]) -> f64 {
        self.cap_split_z(trays) - tray().skirt_depth - self.pump_seated_drop
    }

    /// The aft end of the skirt opening's upper band behind the pumps.
    pub fn pump_skirt_band_aft_y(&self, trays: &[[f64; 3]]) -> f64 {
        let t = tray();
        trays.iter().map(|p| p[1] + t.skirt_open_y_max + t.skirt_upper_band).fold(f64::NEG_INFINITY, f64::max)
    }

    pub fn bay_back_y(&self, plate: &ColletPlate) -> f64 {
        plate.fore_y
    }

    /// The pump cartridge's aft face: a kiss off the bay bulkhead, behind the skirt's band.
    pub fn pump_cartridge_aft_y(&self, trays: &[[f64; 3]], plate: &ColletPlate) -> f64 {
        let nominal = self.bay_back_y(plate) - self.cap_kiss;
        let band = self.pump_skirt_band_aft_y(trays);
        let aft = nominal.max(band);
        let air = self.bay_back_y(plate) - aft;
        assert!(
            air >= self.cap_kiss - self.cap_kiss_station_allowance - 1e-9,
            "the bay bulkhead at Y{} stands inside the skirt opening's upper band, which ends at Y{band}",
            self.bay_back_y(plate)
        );
        aft
    }

    /// Each pump's relief region: X span, Z span, and the relief floor.
    pub fn pump_relief_z0(&self, trays: &[[f64; 3]]) -> f64 {
        let t = tray();
        trays.iter().map(|p| p[2] - t.head_depth - self.pump_relief_z_air).fold(f64::INFINITY, f64::min)
    }

    /// The pump bay's floor under the heads, below the Z seam.
    pub fn bay_floor_z(&self, trays: &[[f64; 3]]) -> (f64, f64) {
        (
            Z_SEAM,
            self.pump_relief_z0(trays) - self.pump_cartridge_z_clearance + self.pump_station_drop
                - self.pump_bay_floor_relief,
        )
    }
}

/// The roof skin over the lip's ceiling run.
pub const CEILING_SKIN: f64 = 3.0;
/// A stated bound within this of zero reads as the pack's floor.
pub const STATED_BOUND_TOL: f64 = 1e-6;

/// The vent's root clearance round anything standing on the flank, and how far inboard the
/// flank is read for what stands on it.
pub const COND_VENT_CLEAR: f64 = WALL;
pub const COND_VENT_PROBE: f64 = WALL;
/// One opening marooned past a solid land is a nick, not a grille.
pub const COND_VENT_ISLAND_MIN: usize = 2;
/// The fan's bottom over the block's base, and its top under the block's crown.
pub const COND_FAN_RISE: f64 = 22.0;
pub const COND_FAN_DROP: f64 = 5.0;
/// The unpierced bands crossing the vent, each tying every mullion and both jambs together.
pub const COND_VENT_TRANSOMS: usize = 3;
pub const COND_VENT_TRANSOM_H: f64 = 4.0;

/// A Wago well's stock round its pocket.
pub const WAGO_WELL_WALL: f64 = 3.0;
/// A valve tray's plate runs this far past its outermost seats' reach.
pub const VALVE_TRAY_MARGIN: f64 = 3.0;
