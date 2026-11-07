//! The one-piece ASA Aero float's calculations as `design.json` carries them for the float build
//! guide and the print setup: its dimensions, how its height was sized, its volumes, the magnet,
//! where it rides in the vessels, its lift across foam densities, what its print has to hold and
//! what is not yet qualified. Every dimension is the Aero float's crate's.
use hsm_aero_float_numbers as float;
use serde::Serialize;

/// The foam densities the lift table runs over, in g/cc.
const FOAM_DENSITIES: [f64; 6] = [0.46, 0.53, 0.55, 0.60, 0.65, 0.70];

#[derive(Serialize)]
struct Design {
    accepted_print_reference: &'static str,
    article: &'static str,
    buoyancy: Vec<Lift>,
    cad_revision: &'static str,
    dimensions_mm: Dimensions,
    installation: Installation,
    magnet: Magnet,
    neutral_foam_density_g_cc: f64,
    print_intent: PrintIntent,
    qualification: Qualification,
    sizing: Sizing,
    volumes_cc: Volumes,
}

/// The float at one foam density: its mass, the lift it has to spare and the freeboard it rides
/// at, guided upright.
#[derive(Serialize)]
struct Lift {
    assembled_mass_g: f64,
    foam_density_g_cc: f64,
    guided_upright_freeboard_mm: f64,
    reserve_lift_g: f64,
}

#[derive(Serialize)]
struct Dimensions {
    bench_guide: f64,
    bore_side_collar: f64,
    diameter: f64,
    foam_above_pocket: f64,
    foam_below_magnet: f64,
    guide_bore: f64,
    guide_radial_clearance: f64,
    height: f64,
    magnet_midplane: f64,
    magnet_seat: f64,
    outer_band_beside_magnet: f64,
    pocket_depth: f64,
    pocket_id: f64,
    pocket_od: f64,
    pocket_roof: f64,
}

#[derive(Serialize)]
struct Installation {
    body_wall_clearance_range_mm: [f64; 2],
    design_magnet_above_waterline_mm: f64,
    rod_axis_from_inner_wall_mm: f64,
    scope: &'static str,
}

#[derive(Serialize)]
struct Magnet {
    continuous_operating_limit_c: u32,
    dimensional_tolerance_mm: f64,
    grade: &'static str,
    id_mm: f64,
    mass_g: f64,
    model: &'static str,
    od_mm: f64,
    source: &'static str,
    thickness_mm: f64,
}

#[derive(Serialize)]
struct PrintIntent {
    layer_height_mm: f64,
    minimum_compensated_radial_magnet_clearance_mm: f64,
    minimum_nominal_pocket_depth_clearance_mm: f64,
    pause_before_layer_z_mm: f64,
    scope: &'static str,
    wall_loops: u32,
    xy_contour_compensation_mm: f64,
    xy_hole_compensation_mm: f64,
}

#[derive(Serialize)]
struct Qualification {
    buoyancy_measured: bool,
    density_measured: bool,
    magnet_heat_exposure_verified: bool,
    paused_magnet_retention_verified: bool,
    pressure_rating: &'static str,
    upright_scope: &'static str,
    wetted_service: &'static str,
}

#[derive(Serialize)]
struct Sizing {
    design_foam_density_g_cc: f64,
    equation: &'static str,
    minimum_calculated_height_mm: f64,
    minimum_reserve_lift_g: f64,
    outcome: &'static str,
    scope: &'static str,
    upward_height_rounding_mm: f64,
    water_density_g_cc: f64,
}

#[derive(Serialize)]
struct Volumes {
    asa_aero: f64,
    external_displacement_excluding_open_bore: f64,
    magnet_pocket: f64,
}

/// The document as the guide and the setup read it, pretty-printed.
pub fn json() -> serde_json::Result<String> {
    let water = float::WATER_DENSITY;
    let (displaced, foam) = (float::displacement_cc(), float::foam_cc());
    let buoyancy = FOAM_DENSITIES
        .iter()
        .map(|&density| {
            let mass = foam * density + float::MAGNET_MASS;
            let reserve = displaced * water - mass;
            Lift {
                assembled_mass_g: mass,
                foam_density_g_cc: density,
                guided_upright_freeboard_mm: reserve / (water * float::annular_area() / 1000.),
                reserve_lift_g: reserve,
            }
        })
        .collect();
    let tolerance = float::MAGNET_TOLERANCE;
    let design = Design {
        accepted_print_reference: "mark2-print/v1/float-preflight.json; immutable v1 source commit and snapshot",
        article: "One-piece ASA Aero guided bench float; RC62 inserted during printing",
        buoyancy,
        cad_revision: "v2-upper-clearance",
        dimensions_mm: Dimensions {
            bench_guide: float::GUIDE_DIAMETER,
            bore_side_collar: (float::POCKET_ID - float::BORE_DIAMETER) / 2.,
            diameter: float::DIAMETER,
            foam_above_pocket: float::height() - float::pocket_roof(),
            foam_below_magnet: float::magnet_seat(),
            guide_bore: float::BORE_DIAMETER,
            guide_radial_clearance: float::GUIDE_RADIAL_CLEARANCE,
            height: float::height(),
            magnet_midplane: float::magnet_midplane(),
            magnet_seat: float::magnet_seat(),
            outer_band_beside_magnet: (float::DIAMETER - float::POCKET_OD) / 2.,
            pocket_depth: float::POCKET_DEPTH,
            pocket_id: float::POCKET_ID,
            pocket_od: float::POCKET_OD,
            pocket_roof: float::pocket_roof(),
        },
        installation: Installation {
            body_wall_clearance_range_mm: [float::MINIMUM_WALL_CLEARANCE, float::MAXIMUM_WALL_CLEARANCE],
            design_magnet_above_waterline_mm: float::magnet_above_waterline(float::design_mass_g(), water),
            rod_axis_from_inner_wall_mm: float::ROD_AXIS_FROM_INNER_WALL,
            scope: "Upright geometric clearances; liquid switching heights require finished-float and \
                    installed-reed calibration",
        },
        magnet: Magnet {
            continuous_operating_limit_c: 80,
            dimensional_tolerance_mm: tolerance,
            grade: "N42",
            id_mm: float::MAGNET_ID,
            mass_g: float::MAGNET_MASS,
            model: "K&J RC62",
            od_mm: float::MAGNET_OD,
            source: "https://www.kjmagnetics.com/rc62-neodymium-ring-magnet",
            thickness_mm: float::MAGNET_THICKNESS,
        },
        neutral_foam_density_g_cc: (displaced * water - float::MAGNET_MASS) / foam,
        print_intent: PrintIntent {
            layer_height_mm: float::LAYER_HEIGHT,
            minimum_compensated_radial_magnet_clearance_mm: ((float::POCKET_OD - float::MAGNET_OD - tolerance) / 2.
                + float::XY_HOLE_COMPENSATION)
                .min((float::MAGNET_ID - tolerance - float::POCKET_ID) / 2. - float::XY_CONTOUR_COMPENSATION),
            minimum_nominal_pocket_depth_clearance_mm: float::POCKET_DEPTH - float::MAGNET_THICKNESS - tolerance,
            pause_before_layer_z_mm: float::pause_before_z(),
            scope: "Native slicing must verify the printed seat, last open-pocket layer, pause and first \
                    covering deposition. CAD midpoint is exact; the physical center depends on layer \
                    quantization and actual magnet thickness.",
            wall_loops: 300,
            xy_contour_compensation_mm: float::XY_CONTOUR_COMPENSATION,
            xy_hole_compensation_mm: float::XY_HOLE_COMPENSATION,
        },
        qualification: Qualification {
            buoyancy_measured: false,
            density_measured: false,
            magnet_heat_exposure_verified: false,
            paused_magnet_retention_verified: false,
            pressure_rating: "Unqualified bench prototype",
            upright_scope: "Guided on the bench rod; no free-floating upright stability claim",
            wetted_service: "Not qualified; no water uptake, pressure endurance or material-contact \
                             acceptance is recorded",
        },
        sizing: Sizing {
            design_foam_density_g_cc: float::DESIGN_FOAM_DENSITY,
            equation: "H = (reserve + magnet_mass - foam_density * pocket_volume) / ((water_density - \
                       foam_density) * annular_area)",
            minimum_calculated_height_mm: float::minimum_height(),
            minimum_reserve_lift_g: float::MINIMUM_RESERVE_LIFT_G,
            outcome: "Positive guided lift with a 5 g allowance for density and absorbed-water variation \
                      in a bench trial",
            scope: "Foam density is an engineering assumption, not a measured tolerance or a \
                    water-absorption allowance proven adequate for service.",
            upward_height_rounding_mm: float::HEIGHT_INCREMENT,
            water_density_g_cc: water,
        },
        volumes_cc: Volumes {
            asa_aero: foam,
            external_displacement_excluding_open_bore: displaced,
            magnet_pocket: float::pocket_volume() / 1000.,
        },
    };
    Ok(serde_json::to_string_pretty(&design)? + "\n")
}
