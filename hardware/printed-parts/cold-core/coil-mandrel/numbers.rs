//! The coil mandrel's numbers, in millimetres: the hollow PETG ring the evaporator's copper is
//! rough-formed on by hand, the helical groove that cradles the copper, and the plain handle ring
//! at either end of the groove. The mandrel's axis is Z, its lower end at Z = 0. The groove winds
//! the copper to the helix the coil's numbers give.
use hsm_coil_numbers as coil;
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as casing;

/// The ring's wall.
pub const WALL: f64 = 5.;
/// How deep the groove sinks the copper into the ring's face, and the groove's section: the
/// copper's own.
pub const GROOVE_DEPTH: f64 = 1.;
pub const GROOVE_PROFILE_RADIUS: f64 = coil::TUBE_RADIUS;
/// The groove's floor, where the copper's inside lies, and the ring's face above it.
pub const GROOVE_FLOOR_RADIUS: f64 = casing::CARBONATOR_OUTER_RADIUS - coil::MANDREL_UNDERSIZE;
pub const RADIUS: f64 = GROOVE_FLOOR_RADIUS + GROOVE_DEPTH;
pub const INNER_RADIUS: f64 = RADIUS - WALL;
/// How far the copper's centreline stands outside the ring's face.
pub const GROOVE_OFFSET: f64 = GROOVE_PROFILE_RADIUS - GROOVE_DEPTH;

/// Each handle ring's length, in inches and in millimetres.
pub const HANDLE_LENGTH_IN: f64 = 0.75;
pub const HANDLE_LENGTH: f64 = HANDLE_LENGTH_IN * 25.4;
/// The groove's zone between the handles: the coil's winding height.
pub const WIND_LENGTH: f64 = coil::WIND_HEIGHT;
pub const WIND_Z: [f64; 2] = [HANDLE_LENGTH, HANDLE_LENGTH + WIND_LENGTH];
/// The mandrel's length, handle to handle.
pub const LENGTH: f64 = HANDLE_LENGTH + WIND_LENGTH + HANDLE_LENGTH;

/// The mandrel prints in black PETG.
pub fn colour() -> catalog::Colour {
    catalog::petg_black()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_groove_lays_the_copper_on_the_coils_mandrel_helix() {
        assert_eq!(RADIUS + GROOVE_OFFSET, coil::MANDREL_WIND_RADIUS);
    }
}
