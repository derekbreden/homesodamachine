//! The bench float's calculations as `design.json` carries them for its print setup, its
//! verification and its pressure screen: the dimensions, the magnet, each piece's true volume, the
//! lift across Aero densities, and the fit and pocket clearances.
use hsm_magnetic_float_numbers as float;
use serde::Serialize;
use std::f64::consts::PI;

/// The Aero densities the lift table runs over, in g/cc.
const AERO_DENSITIES: [f64; 6] = [0.46, 0.53, 0.55, 0.60, 0.65, 0.70];

#[derive(Serialize)]
struct Design {
    dimensions_mm: Dimensions,
    magnet: Magnet,
    volume_cc: Volumes,
    water_displacement_g: f64,
    petg_material: &'static str,
    petg_density_g_cc: f64,
    buoyancy: Vec<Lift>,
    neutral_aero_density_g_cc: f64,
    nominal_unfilled_volume_cc: f64,
    aero_material: &'static str,
    core_print_fit_allowance_radial_mm: f64,
    insert_print_fit_allowance_radial_mm: f64,
    minimum_seated_magnet_top_to_roof_bottom_mm: f64,
    magnet_pocket_minimum_compensated_radial_clearance_mm: f64,
    magnet_pocket_minimum_depth_clearance_mm: f64,
    fit: &'static str,
    pressure_rating: &'static str,
}

#[derive(Serialize)]
struct Dimensions {
    diameter: f64,
    height: f64,
    bore: f64,
    petg_outer_wall: f64,
    petg_bore_wall: f64,
    petg_floor: f64,
    petg_roof: f64,
    insert_height: f64,
    insert_top: f64,
    insert_bottom: f64,
    magnet_seat: f64,
    roof_bottom: f64,
    magnet_pocket_od: f64,
    magnet_pocket_id: f64,
    magnet_pocket_height: f64,
    aero_lower_lead_in: f64,
    insert_od: f64,
    insert_id: f64,
}

#[derive(Serialize)]
struct Magnet {
    model: &'static str,
    mass_g: f64,
    od_mm: f64,
    id_mm: f64,
    height_mm: f64,
    maximum_dimensional_tolerance_mm: f64,
    source: &'static str,
}

/// Each piece's volume in cc: the true solid's, which the kernel's facets approach.
#[derive(Serialize)]
struct Volumes {
    #[serde(rename = "body-petg")]
    body_petg: f64,
    #[serde(rename = "body-aero")]
    body_aero: f64,
    #[serde(rename = "insert-aero")]
    insert_aero: f64,
    magnet: f64,
}

/// The assembled float at one Aero density: its mass, the lift it has to spare in water and the
/// freeboard that leaves it upright on the guide.
#[derive(Serialize)]
struct Lift {
    aero_density_g_cc: f64,
    assembled_mass_g: f64,
    reserve_lift_g: f64,
    upright_freeboard_mm: f64,
}

/// The volume of the ring between two radii, standing from `bottom` to `top`.
fn ring(outer: f64, inner: f64, bottom: f64, top: f64) -> f64 {
    PI * (outer * outer - inner * inner) * (top - bottom)
}

/// The ring less its two lower chamfers: each a right triangle of the insertion lead's legs turned
/// about the bore.
fn led_ring(outer: f64, inner: f64, bottom: f64, top: f64) -> f64 {
    let lead = float::INSERTION_LEAD;
    ring(outer, inner, bottom, top) - PI * (lead * lead) * (outer + inner)
}

/// The document as the setup and the checks read it, pretty-printed.
pub fn json() -> serde_json::Result<String> {
    let (outer, inner) = (float::CORE_OUTER_RADIUS, float::CORE_INNER_RADIUS);
    let pocket = ring(float::POCKET_OD / 2., float::POCKET_ID / 2., float::MAGNET_SEAT, float::INSERT_BOTTOM);
    let magnet_top = float::MAGNET_SEAT + float::MAGNET_THICKNESS;
    let volume_cc = Volumes {
        body_petg: (ring(float::OUTER_RADIUS, float::BORE_RADIUS, 0., float::HEIGHT)
            - ring(outer, inner, float::FLOOR, float::ROOF_BOTTOM))
            / 1000.,
        body_aero: (led_ring(outer, inner, float::FLOOR, float::INSERT_BOTTOM) - pocket) / 1000.,
        insert_aero: led_ring(outer, inner, float::INSERT_BOTTOM, float::INSERT_TOP) / 1000.,
        magnet: ring(float::MAGNET_OD / 2., float::MAGNET_ID / 2., float::MAGNET_SEAT, magnet_top) / 1000.,
    };
    let (rim, bore) = (float::OUTER_RADIUS, float::BORE_RADIUS);
    let displaced = PI * (rim * rim - bore * bore) * float::HEIGHT / 1000.;
    let petg = volume_cc.body_petg;
    let aero = volume_cc.body_aero + volume_cc.insert_aero;
    let buoyancy = AERO_DENSITIES
        .iter()
        .map(|&density| {
            let mass = petg * float::PETG_DENSITY + aero * density + float::MAGNET_MASS;
            let reserve = displaced * float::WATER_DENSITY - mass;
            Lift {
                aero_density_g_cc: density,
                assembled_mass_g: mass,
                reserve_lift_g: reserve,
                upright_freeboard_mm: float::HEIGHT * reserve / displaced,
            }
        })
        .collect();
    let filled = volume_cc.body_petg + volume_cc.body_aero + volume_cc.insert_aero + volume_cc.magnet;
    let fit = float::CORE_FIT_ALLOWANCE;
    let design = Design {
        dimensions_mm: Dimensions {
            diameter: float::DIAMETER,
            height: float::HEIGHT,
            bore: float::BORE_DIAMETER,
            petg_outer_wall: float::OUTER_WALL,
            petg_bore_wall: float::BORE_WALL,
            petg_floor: float::FLOOR,
            petg_roof: float::ROOF,
            insert_height: float::INSERT_HEIGHT,
            insert_top: float::INSERT_TOP,
            insert_bottom: float::INSERT_BOTTOM,
            magnet_seat: float::MAGNET_SEAT,
            roof_bottom: float::ROOF_BOTTOM,
            magnet_pocket_od: float::POCKET_OD,
            magnet_pocket_id: float::POCKET_ID,
            magnet_pocket_height: float::POCKET_DEPTH,
            aero_lower_lead_in: float::INSERTION_LEAD,
            insert_od: 2. * outer,
            insert_id: 2. * inner,
        },
        magnet: Magnet {
            model: "K&J RC62",
            mass_g: float::MAGNET_MASS,
            od_mm: float::MAGNET_OD,
            id_mm: float::MAGNET_ID,
            height_mm: float::MAGNET_THICKNESS,
            maximum_dimensional_tolerance_mm: float::MAGNET_TOLERANCE,
            source: "https://www.kjmagnetics.com/rc62-neodymium-ring-magnet",
        },
        volume_cc,
        water_displacement_g: displaced * float::WATER_DENSITY,
        petg_material: "Bambu PETG Translucent Clear 32101",
        petg_density_g_cc: float::PETG_DENSITY,
        buoyancy,
        neutral_aero_density_g_cc: (displaced * float::WATER_DENSITY
            - petg * float::PETG_DENSITY
            - float::MAGNET_MASS)
            / aero,
        nominal_unfilled_volume_cc: (displaced - filled).max(0.),
        aero_material: "Bambu ASA Aero White 46100",
        core_print_fit_allowance_radial_mm: float::CORE_FIT_ALLOWANCE,
        insert_print_fit_allowance_radial_mm: float::INSERT_FIT_ALLOWANCE,
        minimum_seated_magnet_top_to_roof_bottom_mm: float::ROOF_BOTTOM
            - float::MAGNET_SEAT
            - float::MAGNET_THICKNESS
            - float::MAGNET_TOLERANCE,
        magnet_pocket_minimum_compensated_radial_clearance_mm: ((float::POCKET_OD
            - float::MAGNET_OD
            - float::MAGNET_TOLERANCE)
            / 2.
            - fit)
            .min((float::MAGNET_ID - float::MAGNET_TOLERANCE - float::POCKET_ID) / 2. - fit),
        magnet_pocket_minimum_depth_clearance_mm: float::POCKET_DEPTH
            - float::MAGNET_THICKNESS
            - float::MAGNET_TOLERANCE,
        fit: "The Aero pieces have 0.5 mm lower outer/bore lead-ins and 0.05 mm radial contour \
              expansion and bore reduction on their straight lands. The RC62 seats in a clearance \
              pocket below the insert. The insert top supports the full roof. Intentional unfilled \
              volume comprises lower lead-ins and magnet-pocket clearance.",
        pressure_rating: "Unqualified prototype; no hydrostatic test recorded.",
    };
    Ok(serde_json::to_string_pretty(&design)? + "\n")
}
