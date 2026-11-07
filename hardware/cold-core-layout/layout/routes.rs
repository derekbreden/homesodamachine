//! The lines inside the cold core, as the corners of their centrelines in the shell's frame, and
//! the bend every one of them turns at: the ¼" LLDPE's least bend, from the routing catalog.
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as core;
use hsm_prv_shroud_numbers as shroud;

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
