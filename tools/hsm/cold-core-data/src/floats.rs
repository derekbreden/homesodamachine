//! Shared ASA Aero float sizing and guide/reed clearances.

use serde_json::{Value, json};

pub fn aero_datums() -> Value {
    use hsm_aero_float_numbers as f;
    json!({
        "diameter": f::DIAMETER, "bore_diameter": f::BORE_DIAMETER, "guide_diameter": f::GUIDE_DIAMETER,
        "magnet_od": f::MAGNET_OD, "magnet_id": f::MAGNET_ID, "magnet_thickness": f::MAGNET_THICKNESS,
        "magnet_tolerance": f::MAGNET_TOLERANCE, "magnet_mass": f::MAGNET_MASS,
        "pocket_od": f::POCKET_OD, "pocket_id": f::POCKET_ID, "pocket_depth": f::POCKET_DEPTH,
        "water_density": f::WATER_DENSITY, "design_foam_density": f::DESIGN_FOAM_DENSITY,
        "minimum_reserve_lift_g": f::MINIMUM_RESERVE_LIFT_G, "height_increment": f::HEIGHT_INCREMENT,
        "layer_height": f::LAYER_HEIGHT, "xy_contour_compensation": f::XY_CONTOUR_COMPENSATION,
        "xy_hole_compensation": f::XY_HOLE_COMPENSATION, "annular_area": f::annular_area(),
        "pocket_volume": f::pocket_volume(), "minimum_height": f::minimum_height(), "height": f::height(),
        "magnet_midplane": f::magnet_midplane(), "magnet_seat": f::magnet_seat(), "pocket_roof": f::pocket_roof(),
        "pause_before_z": f::pause_before_z(), "displacement_cc": f::displacement_cc(), "foam_cc": f::foam_cc(),
        "design_mass_g": f::design_mass_g(), "wall_clearance": f::WALL_CLEARANCE,
        "rod_axis_from_inner_wall": f::ROD_AXIS_FROM_INNER_WALL,
        "guide_radial_clearance": f::GUIDE_RADIAL_CLEARANCE,
        "minimum_wall_clearance": f::MINIMUM_WALL_CLEARANCE,
        "maximum_wall_clearance": f::MAXIMUM_WALL_CLEARANCE,
        "magnet_edge_inset": f::MAGNET_EDGE_INSET,
        "reed_model": "Littelfuse MDSR-7-10-15", "reed_mount_length": 14.,
        "reed_mount_diameter": 2.5, "bench_edge_distance": 30., "bench_stable_travel": 30.,
        "bench_scope": "One bare RC62 and one MDSR-7-10-15, axial reed; nearest magnet edge datum; no installed-wall calibration",
        "float_edge_reported_usable_limit": 20., "float_edge_design_maximum": 18.,
        "float_edge_evidence": "magnetic-float/all-aero/physical-observations.json#reed_reach_report"
    })
}

/// Guided dry upright float; measured mass and liquid density can replace the design seeds.
pub fn waterline(mass_g: Option<f64>, liquid_density: Option<f64>) -> f64 {
    use hsm_aero_float_numbers as f;
    f::magnet_above_waterline(mass_g.unwrap_or_else(f::design_mass_g), liquid_density.unwrap_or(f::WATER_DENSITY))
}

pub fn edge_distance(rod_axis: f64, reed_axis: f64, float_edge: bool) -> f64 {
    hsm_aero_float_numbers::edge_distance(rod_axis, reed_axis, float_edge)
}
