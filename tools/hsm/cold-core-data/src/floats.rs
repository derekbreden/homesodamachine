//! Shared ASA Aero float sizing and guide/reed clearances.

use serde_json::{Value, json};
use std::f64::consts::PI;

pub fn aero_datums() -> Value {
    let diameter: f64 = 36.;
    let bore_diameter: f64 = 4.8;
    let guide_diameter = 3.175;
    let magnet_od = 19.05;
    let magnet_id = 9.525;
    let magnet_thickness = 3.175;
    let magnet_tolerance = 0.1;
    let magnet_mass = 5.09;
    let pocket_od: f64 = 19.35;
    let pocket_id: f64 = 9.225;
    let pocket_depth = 3.6;
    let water_density = 0.9997;
    let design_foam_density = 0.65;
    let minimum_reserve_lift_g = 5.;
    let height_increment = 1.;
    let layer_height = 0.2;
    let xy_contour_compensation = 0.05;
    let xy_hole_compensation = -0.05;
    let annular_area = PI * ((diameter / 2.).powi(2) - (bore_diameter / 2.).powi(2));
    let pocket_volume = PI * ((pocket_od / 2.).powi(2) - (pocket_id / 2.).powi(2)) * pocket_depth;
    let minimum_height = (minimum_reserve_lift_g + magnet_mass
        - design_foam_density * pocket_volume / 1000.)
        / ((water_density - design_foam_density) * annular_area / 1000.);
    let height = (minimum_height / height_increment).ceil() * height_increment;
    let magnet_midplane = height / 2.;
    let magnet_seat = magnet_midplane - magnet_thickness / 2.;
    let pocket_roof = magnet_seat + pocket_depth;
    let pause_before_z = (pocket_roof / layer_height - 1e-9).ceil() * layer_height;
    let displacement_cc = annular_area * height / 1000.;
    let foam_cc = displacement_cc - pocket_volume / 1000.;
    let design_mass_g = foam_cc * design_foam_density + magnet_mass;
    let wall_clearance = 2.;
    let rod_axis_from_inner_wall = diameter / 2. + wall_clearance;
    let guide_radial_clearance = (bore_diameter - guide_diameter) / 2.;
    assert!(wall_clearance - guide_radial_clearance > 1.0);
    assert!(height == 28.0 && magnet_midplane == 14.0);
    json!({
        "diameter": diameter, "bore_diameter": bore_diameter, "guide_diameter": guide_diameter,
        "magnet_od": magnet_od, "magnet_id": magnet_id, "magnet_thickness": magnet_thickness,
        "magnet_tolerance": magnet_tolerance, "magnet_mass": magnet_mass,
        "pocket_od": pocket_od, "pocket_id": pocket_id, "pocket_depth": pocket_depth,
        "water_density": water_density, "design_foam_density": design_foam_density,
        "minimum_reserve_lift_g": minimum_reserve_lift_g, "height_increment": height_increment,
        "layer_height": layer_height, "xy_contour_compensation": xy_contour_compensation,
        "xy_hole_compensation": xy_hole_compensation, "annular_area": annular_area,
        "pocket_volume": pocket_volume, "minimum_height": minimum_height, "height": height,
        "magnet_midplane": magnet_midplane, "magnet_seat": magnet_seat, "pocket_roof": pocket_roof,
        "pause_before_z": pause_before_z, "displacement_cc": displacement_cc, "foam_cc": foam_cc,
        "design_mass_g": design_mass_g, "wall_clearance": wall_clearance,
        "rod_axis_from_inner_wall": rod_axis_from_inner_wall,
        "guide_radial_clearance": guide_radial_clearance,
        "minimum_wall_clearance": wall_clearance - guide_radial_clearance,
        "maximum_wall_clearance": wall_clearance + guide_radial_clearance,
        "magnet_edge_inset": (diameter - magnet_od) / 2.,
        "reed_model": "Littelfuse MDSR-7-10-15", "reed_mount_length": 14.,
        "reed_mount_diameter": 2.5, "bench_edge_distance": 30., "bench_stable_travel": 30.,
        "bench_scope": "One bare RC62 and one MDSR-7-10-15, axial reed; nearest magnet edge datum; no installed-wall calibration",
        "float_edge_reported_usable_limit": 20., "float_edge_design_maximum": 18.,
        "float_edge_evidence": "magnetic-float/all-aero/physical-observations.json#reed_reach_report"
    })
}

/// Guided dry upright float; measured mass and liquid density can replace the design seeds.
pub fn waterline(mass_g: Option<f64>, liquid_density: Option<f64>) -> f64 {
    let d = aero_datums();
    let n = |key: &str| d[key].as_f64().unwrap();
    n("magnet_midplane")
        - mass_g.unwrap_or_else(|| n("design_mass_g"))
            / (liquid_density.unwrap_or_else(|| n("water_density")) * n("annular_area") / 1000.)
}

pub fn edge_distance(rod_axis: f64, reed_axis: f64, float_edge: bool) -> f64 {
    let d = aero_datums();
    (reed_axis - rod_axis).abs() + d["guide_radial_clearance"].as_f64().unwrap()
        - d[if float_edge { "diameter" } else { "magnet_od" }]
            .as_f64()
            .unwrap()
            / 2.
}

pub fn aero_numbers(colors: &Value) -> Value {
    let d = aero_datums();
    let mut out = json!({"insertion_lift": 9.0,
        "color_aero": colors["aero"], "color_magnet": colors["magnet"]});
    for key in [
        "diameter",
        "height",
        "bore_diameter",
        "pocket_od",
        "pocket_id",
        "magnet_seat",
        "pocket_roof",
        "magnet_od",
        "magnet_id",
        "magnet_thickness",
    ] {
        out[key] = d[key].clone();
    }
    out
}

pub fn aero_measurements() -> Value {
    let d = aero_datums();
    let n = |key: &str| d[key].as_f64().unwrap();
    let displacement_cc = n("annular_area") * n("height") / 1000.;
    let foam_cc = displacement_cc - n("pocket_volume") / 1000.;
    let table: Vec<_> = [0.46, 0.53, 0.55, 0.60, 0.65, 0.70].iter().map(|density| {
        let mass = foam_cc * density + n("magnet_mass");
        let reserve = displacement_cc * n("water_density") - mass;
        json!({"foam_density_g_cc": density, "assembled_mass_g": mass,
            "reserve_lift_g": reserve,
            "guided_upright_freeboard_mm": reserve / (n("water_density") * n("annular_area") / 1000.)})
    }).collect();
    json!({
        "article": "One-piece ASA Aero guided bench float; RC62 inserted during printing",
        "cad_revision": "v2-upper-clearance",
        "accepted_print_reference": "mark2-print/v1/float-preflight.json; immutable v1 source commit and snapshot",
        "dimensions_mm": {"diameter": d["diameter"], "height": d["height"], "guide_bore": d["bore_diameter"],
            "bench_guide": d["guide_diameter"], "guide_radial_clearance": d["guide_radial_clearance"],
            "magnet_midplane": d["magnet_midplane"], "magnet_seat": d["magnet_seat"],
            "pocket_roof": d["pocket_roof"], "pocket_od": d["pocket_od"],
            "pocket_id": d["pocket_id"], "pocket_depth": d["pocket_depth"],
            "bore_side_collar": (n("pocket_id") - n("bore_diameter")) / 2.,
            "outer_band_beside_magnet": (n("diameter") - n("pocket_od")) / 2.,
            "foam_below_magnet": d["magnet_seat"], "foam_above_pocket": n("height") - n("pocket_roof")},
        "sizing": {"outcome": "Positive guided lift with a 5 g allowance for density and absorbed-water variation in a bench trial",
            "water_density_g_cc": d["water_density"], "design_foam_density_g_cc": d["design_foam_density"],
            "minimum_reserve_lift_g": d["minimum_reserve_lift_g"],
            "minimum_calculated_height_mm": d["minimum_height"], "upward_height_rounding_mm": d["height_increment"],
            "equation": "H = (reserve + magnet_mass - foam_density * pocket_volume) / ((water_density - foam_density) * annular_area)",
            "scope": "Foam density is an engineering assumption, not a measured tolerance or a water-absorption allowance proven adequate for service."},
        "volumes_cc": {"external_displacement_excluding_open_bore": displacement_cc,
            "asa_aero": foam_cc, "magnet_pocket": n("pocket_volume") / 1000.},
        "magnet": {"model": "K&J RC62", "od_mm": d["magnet_od"], "id_mm": d["magnet_id"],
            "thickness_mm": d["magnet_thickness"], "dimensional_tolerance_mm": d["magnet_tolerance"],
            "mass_g": d["magnet_mass"], "grade": "N42", "continuous_operating_limit_c": 80,
            "source": "https://www.kjmagnetics.com/rc62-neodymium-ring-magnet"},
        "installation": {"rod_axis_from_inner_wall_mm": d["rod_axis_from_inner_wall"],
            "body_wall_clearance_range_mm": [d["minimum_wall_clearance"], d["maximum_wall_clearance"]],
            "design_magnet_above_waterline_mm": waterline(None, None),
            "scope": "Upright geometric clearances; liquid switching heights require finished-float and installed-reed calibration"},
        "buoyancy": table,
        "neutral_foam_density_g_cc": (displacement_cc * n("water_density") - n("magnet_mass")) / foam_cc,
        "print_intent": {"layer_height_mm": d["layer_height"], "wall_loops": 300,
            "pause_before_layer_z_mm": d["pause_before_z"],
            "xy_contour_compensation_mm": d["xy_contour_compensation"],
            "xy_hole_compensation_mm": d["xy_hole_compensation"],
            "minimum_compensated_radial_magnet_clearance_mm":
                ((n("pocket_od") - n("magnet_od") - n("magnet_tolerance")) / 2. + n("xy_hole_compensation")).min(
                (n("magnet_id") - n("magnet_tolerance") - n("pocket_id")) / 2. - n("xy_contour_compensation")),
            "minimum_nominal_pocket_depth_clearance_mm": n("pocket_depth") - n("magnet_thickness") - n("magnet_tolerance"),
            "scope": "Native slicing must verify the printed seat, last open-pocket layer, pause and first covering deposition. CAD midpoint is exact; the physical center depends on layer quantization and actual magnet thickness."},
        "qualification": {"density_measured": false, "buoyancy_measured": false,
            "paused_magnet_retention_verified": false, "magnet_heat_exposure_verified": false,
            "pressure_rating": "Unqualified bench prototype",
            "wetted_service": "Not qualified; no water uptake, pressure endurance or material-contact acceptance is recorded",
            "upright_scope": "Guided on the bench rod; no free-floating upright stability claim"}
    })
}
