//! Computes seated loads from the projected areas of the wet boundaries.
use crate::{balance, calibration_inputs, front_seat};
use serde_json::{Value, json};
use std::f64::consts::PI;

pub const DESIGN_PRESSURE_BAR: f64 = 16.0;
pub const SPRING_PRELOAD_N: f64 = 1.2;
pub const ACTUATOR_TARGET_N: f64 = 4.0;
pub const PISTON_DRAG_N: f64 = 0.50;
pub const ROD_DRAG_N: f64 = 0.15;
const RELIEF_PSI: f64 = 125.0;

fn disk(radius: f64) -> f64 {
    PI * radius.powi(2)
}

fn seat_area(diameter: f64) -> f64 {
    disk(diameter / 2.)
}

pub fn opening_force(pressure_bar: f64, seat_diameter: f64) -> f64 {
    pressure_bar / 10. * (disk(balance::BORE_R) - seat_area(seat_diameter))
}

pub fn worst_crack_open_load() -> f64 {
    SPRING_PRELOAD_N + PISTON_DRAG_N + ROD_DRAG_N
        - opening_force(DESIGN_PRESSURE_BAR, front_seat::CREST_DIAMETERS[1])
}

pub fn at_pressure(pressure_bar: f64) -> Value {
    let p = pressure_bar / 10.;
    let stem = disk(front_seat::STEM_R);
    let piston = disk(balance::BORE_R);
    let seat = seat_area(front_seat::SEAT_D);
    let washer = disk(front_seat::KEEPER_BORE_R) - seat;
    let poppet_force = opening_force(pressure_bar, front_seat::SEAT_D);
    let seat_contact = SPRING_PRELOAD_N - poppet_force;
    let crest_ends = front_seat::CREST_DIAMETERS.map(|diameter| opening_force(pressure_bar, diameter));
    json!({
        "supply_bar_gauge": pressure_bar,
        "poppet_back_force_toward_seat_n": p * (disk(front_seat::POPPET_R) - stem),
        "poppet_outer_underside_force_away_from_seat_n": p * (disk(front_seat::POPPET_R) - seat),
        "poppet_head_supply_force_toward_seat_n": p * (seat - stem),
        "balance_piston_supply_force_away_from_seat_n": p * (piston - stem),
        "net_hydraulic_force_toward_open_n": poppet_force,
        "net_hydraulic_force_toward_open_at_crest_edges_n": crest_ends,
        "seat_contact_n_before_drag": seat_contact,
        "washer_pressure_load_into_cap_n": p * washer,
        "cap_external_separating_load_n_excluding_assembly_preload": p * washer + seat_contact,
        "cap_separating_load_if_pressure_reaches_outer_relief_n":
            p * (disk(front_seat::RELIEF_R) - seat) + seat_contact,
        "crack_open_load_crest_outer_edge_including_allocated_drag_n":
            SPRING_PRELOAD_N - crest_ends[1] + PISTON_DRAG_N + ROD_DRAG_N,
    })
}

pub fn report(lift: f64) -> Value {
    let stem = disk(front_seat::STEM_R);
    let piston = disk(balance::BORE_R);
    let seat = seat_area(front_seat::SEAT_D);
    let passage = disk(front_seat::VENT_R);
    json!({
        "scope": "Quasistatic closed valve with an unrestricted atmospheric outlet, atmospheric dry chamber, sealed piston and equal balance and outlet pressures. Projected areas and crest edges are a sensitivity screen. The actual hydraulic diameter, drag and force during flow require measurement.",
        "sign": "Positive net force on the poppet is away from the outlet and opens the valve.",
        "lip_crest_diameters_mm": front_seat::CREST_DIAMETERS,
        "projected_areas_mm2": {
            "seal_circle": seat, "piston_bore": piston, "rod": stem, "axial_drill": passage,
            "poppet_head_net_supply": seat - stem,
            "balance_piston_net_supply": piston - stem,
            "exposed_washer": disk(front_seat::KEEPER_BORE_R) - seat,
        },
        "cases": {
            "nominal_regulator_reference": at_pressure(calibration_inputs::SECONDARY_REGULATOR_BAR),
            "carbonator_relief_reference": at_pressure(RELIEF_PSI / calibration_inputs::PSI_PER_BAR),
            "valve_design_target": at_pressure(DESIGN_PRESSURE_BAR),
        },
        "stroke_displacement_of_balance_chamber_ul": (piston - stem) * lift,
        "additional_closing_force_per_bar_balance_above_outlet_n": (piston - stem - passage) / 10.,
        "additional_opening_force_per_bar_outlet_above_dry_n_with_balance_equal_to_outlet": stem / 10.,
    })
}
