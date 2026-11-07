//! The reed bridge's numbers, in millimetres: the printed PETG interposer that holds the
//! carbonator's level reeds, CLO and CHI, against the tube's bare wall on the register azimuth
//! and stands the evaporator coil off their glass, the water levels its reeds are set to, and
//! the setting gauge that places it. Frame: +Z is the carbonator's axis, Z = 0 at the tube's
//! bottom rim, and +X the register azimuth. The bridge's own files and the evaporator coil,
//! which rides over it, take these by name.
use hsm_aero_float_numbers as float;
use hsm_carbonator_tube_numbers as tube;
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as casing;
use hsm_endcap_circular_numbers as cap;
use std::f64::consts::PI;

// --- The water column the reeds read ---------------------------------------------------------

/// Each end plate is a bore-fit plug recessed its own thickness below its tube end, so the wetted
/// column runs between the plates' inside faces.
pub const PLATE_THICKNESS: f64 = cap::THICKNESS_IN * cap::INCH;
pub const PLATE_RECESS: f64 = PLATE_THICKNESS;
pub const INTERIOR_FLOOR_Z: f64 = PLATE_RECESS + PLATE_THICKNESS;
pub const INTERIOR_CEILING_Z: f64 = casing::CARBONATOR_HEIGHT - PLATE_RECESS - PLATE_THICKNESS;
pub const INTERIOR_HEIGHT: f64 = INTERIOR_CEILING_Z - INTERIOR_FLOOR_Z;

/// The column's water per millimetre of level, in mL: the tube's bore round the float's rod.
pub fn volume_per_mm() -> f64 {
    PI / 4. * (tube::ID.powi(2) - float::GUIDE_DIAMETER.powi(2)) / 1000.
}

/// A serving: the app's default glass of finished soda, and the carbonated water in it at the
/// syrup's dilution, in mL.
pub const SERVING_ML: f64 = 355.;
pub const SYRUP_DILUTION: f64 = 20.;
pub const WATER_PER_SERVING_ML: f64 = SERVING_ML * SYRUP_DILUTION / (SYRUP_DILUTION + 1.);

/// The level one serving takes off the column.
pub fn serving_level_rise() -> f64 {
    WATER_PER_SERVING_ML / volume_per_mm()
}

/// The pump stops (CHI) at this fraction of the wetted height; the rest is the CO2 headspace the
/// inlet jet discharges into.
pub const HIGH_FILL_FRACTION: f64 = 0.65;
pub const HIGH_LEVEL_Z: f64 = INTERIOR_FLOOR_Z + HIGH_FILL_FRACTION * INTERIOR_HEIGHT;

/// The pump starts (CLO) one serving below the stop.
pub fn low_level_z() -> f64 {
    HIGH_LEVEL_Z - serving_level_rise()
}

/// Where the float's magnet midplane stands off the water's surface, for the design float.
pub fn magnet_lead() -> f64 {
    float::magnet_above_waterline(float::design_mass_g(), float::WATER_DENSITY)
}

/// The reeds' centres: each level, plus the magnet's lead over it.
pub fn reed_low_z() -> f64 {
    low_level_z() + magnet_lead()
}

pub fn reed_high_z() -> f64 {
    HIGH_LEVEL_Z + magnet_lead()
}

// --- The bridge ------------------------------------------------------------------------------

/// The reed's mounting envelope: the MDSR-7-10-15's glass with its tape and leads.
pub const REED_GLASS_LENGTH: f64 = 14.;
pub const REED_GLASS_DIAMETER: f64 = 2.5;

/// The bridge's bore seats on the tube on the slip fit.
pub fn inner_radius() -> f64 {
    casing::CARBONATOR_OUTER_RADIUS + catalog::fits().slip
}

/// The skirt the bridge keeps round its bore under the ramps.
pub const SKIRT_THICKNESS: f64 = 0.8;

pub fn skirt_radius() -> f64 {
    inner_radius() + SKIRT_THICKNESS
}

/// What a wrap crossing the plateau clears the glass by. The plateau stands the supported-surface
/// allowance further out, the room the lead groove's floor takes printing over its bridged
/// strands, so the bore, the glass's bearing and the skirt stay where they are.
pub const GLASS_CLEARANCE: f64 = 0.5;

/// The plateau's face off the tube's wall.
pub fn pocket_depth() -> f64 {
    REED_GLASS_DIAMETER + (GLASS_CLEARANCE + catalog::fits().supported_surface)
}

pub fn plateau_radius() -> f64 {
    casing::CARBONATOR_OUTER_RADIUS + pocket_depth()
}

/// A reed's pocket, clear through to the wall: the glass on the slip fit each way, and the wall
/// the plateau keeps beyond each end.
pub fn pocket_length() -> f64 {
    REED_GLASS_LENGTH + 2. * catalog::fits().slip
}

pub fn pocket_width() -> f64 {
    REED_GLASS_DIAMETER + 2. * catalog::fits().slip
}

pub const POCKET_END_WALL: f64 = 3.;

/// The plateau runs from below the low reed's pocket to above the high reed's.
pub fn plateau_z_bottom() -> f64 {
    reed_low_z() - pocket_length() / 2. - POCKET_END_WALL
}

pub fn plateau_z_top() -> f64 {
    reed_high_z() + pocket_length() / 2. + POCKET_END_WALL
}

/// The ramps a wrap rides over as the coil is dragged down the carbonator, along the axis at
/// each end and round it at each side: long enough that the copper climbs instead of catching,
/// and bends well clear of its least radius.
pub const AXIAL_RAMP_LENGTH: f64 = 10.;
pub const ARC_RAMP_WIDTH: f64 = 16.;

pub fn bridge_z_bottom() -> f64 {
    plateau_z_bottom() - AXIAL_RAMP_LENGTH
}

pub fn bridge_z_top() -> f64 {
    plateau_z_top() + AXIAL_RAMP_LENGTH
}

/// The lead groove, wide enough for the reeds' conductors side by side (CLO, CHI and their shared
/// common), off the pocket column to +Y; and the cross-notch at each end of a pocket that brings
/// its reed's leads into the groove.
pub const LEAD_GROOVE_WIDTH: f64 = 5.6;
pub const LEAD_GROOVE_Y: f64 = 5.4;
pub const LEAD_NOTCH_LENGTH: f64 = 2.;
/// The land the plateau keeps outboard of the groove.
pub const GROOVE_LAND: f64 = 1.5;

/// Half the plateau's width, and half the bridge's with its arc ramps.
pub const PLATEAU_HALF_WIDTH: f64 = LEAD_GROOVE_Y + LEAD_GROOVE_WIDTH / 2. + GROOVE_LAND;
pub const BRIDGE_HALF_WIDTH: f64 = PLATEAU_HALF_WIDTH + ARC_RAMP_WIDTH;

/// The radius the angular footprint is laid out on: the plateau's, less the supported-surface
/// allowance, so the allowance narrows neither the skirt nor either ramp.
pub fn nominal_plateau_radius() -> f64 {
    plateau_radius() - catalog::fits().supported_surface
}

/// The plateau's and the bridge's half angles round the register azimuth, in radians.
pub fn plateau_half_angle() -> f64 {
    (PLATEAU_HALF_WIDTH / nominal_plateau_radius()).asin()
}

pub fn bridge_half_angle() -> f64 {
    (BRIDGE_HALF_WIDTH / nominal_plateau_radius()).asin()
}

/// The plan's radius at `angle` radians off the register azimuth: the plateau's across the
/// plateau, falling straight to the skirt's across each arc ramp.
pub fn plan_radius(angle: f64) -> f64 {
    let plateau = plateau_half_angle();
    if angle.abs() <= plateau {
        return plateau_radius();
    }
    let fraction = (angle.abs() - plateau) / (bridge_half_angle() - plateau);
    plateau_radius() - fraction * (plateau_radius() - skirt_radius())
}

/// The chords the plan's outline is cut into across the bridge's arc.
pub const PLAN_SEGMENTS: u32 = 48;

/// How far each cutter overruns the faces it opens.
pub const OVERCUT: f64 = 1.;

// --- The setting gauge -----------------------------------------------------------------------

/// A band round part of the tube that hangs on its bottom rim by an inward hook; its top face is
/// the bridge's bottom edge. Its wall is the nominal printed section, standing outward from the
/// bare tube.
pub const GAUGE_ARC_DEGREES: f64 = 60.;
pub const GAUGE_WALL: f64 = 3.;
pub const GAUGE_HOOK_DEPTH: f64 = 3.5;
pub const GAUGE_HOOK_HEIGHT: f64 = 4.;

/// The bridge and the gauge print in black PETG.
pub fn colour() -> catalog::Colour {
    catalog::petg_black()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_reeds_stand_within_the_floats_reach() {
        // The float lands on the rod's tack bead and stops under the top plate's stop.
        let tack_bead = 1.5;
        let lowest = INTERIOR_FLOOR_Z + tack_bead + float::height() / 2.;
        let highest =
            INTERIOR_CEILING_Z - casing::CARBONATOR_FLOAT_TOP_STOP_HEIGHT - float::height() / 2.;
        assert!(reed_low_z() > lowest);
        assert!(reed_high_z() < highest);
    }
}
