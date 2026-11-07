//! The coil mandrel's answers for the Python readers that still ask: the undersized
//! rough-forming mandrel, the winding it gives the copper and the tails' copper allowances,
//! from the coil's and the mandrel's numbers crates.

use hsm_coil_mandrel_numbers as mandrel;
use hsm_coil_numbers::{self as coil, Tail};
use serde_json::{Value, json};

pub fn datums() -> Value {
    let carbonator_od = 2. * hsm_cold_core_interface::CARBONATOR_OUTER_RADIUS;
    let mandrel_od = 2. * mandrel::RADIUS;
    let by_tail = |number: fn(Tail) -> f64| json!({"inlet": number(Tail::Inlet), "outlet": number(Tail::Outlet)});
    let [wind_bottom, wind_top] = mandrel::WIND_Z;
    json!({
        "evap_tail_low_z": coil::LOW_Z, "evap_tail_high_z": coil::HIGH_Z,
        "tube_od_in": coil::TUBE_OD_IN, "tube_radius": coil::TUBE_RADIUS, "carbonator_od": carbonator_od,
        "carbonator_radius": carbonator_od / 2., "net_undersize": coil::MANDREL_UNDERSIZE,
        "groove_depth": mandrel::GROOVE_DEPTH, "groove_profile_radius": mandrel::GROOVE_PROFILE_RADIUS,
        "groove_offset": mandrel::GROOVE_OFFSET, "mandrel_radius": mandrel::RADIUS, "mandrel_od": mandrel_od,
        "helix_path_radius": coil::MANDREL_WIND_RADIUS,
        "groove_bottom_od": mandrel_od - 2. * mandrel::GROOVE_DEPTH,
        "wall": mandrel::WALL, "mandrel_inner_radius": mandrel::INNER_RADIUS,
        "mandrel_r_range": [mandrel::INNER_RADIUS, mandrel::RADIUS],
        "tail_inlet_x": coil::MANDREL_INLET_STATION[0], "tail_inlet_y": coil::LOW_Z,
        "tail_inlet_z": coil::MANDREL_INLET_STATION[1],
        "tail_outlet_x": coil::MANDREL_OUTLET_STATION[0], "tail_outlet_y": coil::HIGH_Z,
        "tail_outlet_z": coil::MANDREL_OUTLET_STATION[1],
        "wind_length": mandrel::WIND_LENGTH, "tail_inlet_azimuth": coil::mandrel_inlet_azimuth(),
        "tail_outlet_azimuth": coil::mandrel_outlet_azimuth(), "tail_ccw_delta": coil::mandrel_arc(),
        "full_wraps": coil::MANDREL_FULL_WRAPS, "total_wraps": coil::mandrel_wraps(),
        "pitch": coil::mandrel_pitch(), "mandrel_wrap_length": coil::mandrel_wrap_length(),
        "fitted_wrap_radius": coil::WIND_RADIUS, "fitted_wrap_length": coil::fitted_wrap_length(),
        "wrap_length": coil::fitted_wrap_length(),
        "spring_gain": coil::fitted_wrap_length() - coil::mandrel_wrap_length(),
        "stub_protrusion": by_tail(coil::stub_protrusion), "tail_in_shell": by_tail(coil::tail_in_shell),
        "stub_allowance": by_tail(coil::stub_allowance), "stub_total": coil::stub_total(),
        "carbonators_per_roll": coil::CARBONATORS_PER_ROLL, "roll_length_ft": coil::ROLL_LENGTH_FT,
        "handle_length_in": mandrel::HANDLE_LENGTH_IN, "handle_length": mandrel::HANDLE_LENGTH,
        "total_length": mandrel::LENGTH,
        "mandrel_z_range": [0, mandrel::LENGTH], "lower_handle_z_range": [0, wind_bottom],
        "wind_z_range": [wind_bottom, wind_top],
        "upper_handle_z_range": [wind_top, mandrel::LENGTH]
    })
}

pub fn numbers(color: &Value) -> Value {
    let d = datums();
    let mut out = json!({"name": "coil-mandrel", "color": color});
    for key in [
        "mandrel_r_range",
        "mandrel_z_range",
        "lower_handle_z_range",
        "upper_handle_z_range",
        "wind_z_range",
        "wind_length",
        "pitch",
        "helix_path_radius",
        "groove_profile_radius",
    ] {
        out[key] = d[key].clone();
    }
    out
}

pub fn variables() -> Value {
    let d = datums();
    let n = |key: &str| d[key].as_f64().unwrap();
    let mut result = serde_json::Map::new();
    for (name, value, spec, unit) in [
        ("TUBE_R", n("tube_radius"), ".4g", " mm"),
        ("TANK_R", n("carbonator_radius"), ".4g", " mm"),
        ("GROOVE_OFFSET", n("groove_offset"), ".4g", " mm"),
        ("MANDREL_R", n("mandrel_radius"), ".4g", " mm"),
        ("MANDREL_OD", n("mandrel_od"), ".4g", " mm"),
        ("MANDREL_INNER_R", n("mandrel_inner_radius"), ".4g", " mm"),
        ("WIND_LENGTH", n("wind_length"), ".4g", " mm"),
        ("PITCH", n("pitch"), ".4g", " mm"),
        ("PITCH_IN", n("pitch") / 25.4, ".3g", " in"),
        ("MANDREL_LEN", n("mandrel_wrap_length") / 1000., ".4g", " m"),
        ("MANDREL_FT", n("mandrel_wrap_length") / 304.8, ".4g", " ft"),
        ("SPRUNG_LEN", n("fitted_wrap_length") / 1000., ".4g", " m"),
        ("SPRUNG_FT", n("fitted_wrap_length") / 304.8, ".4g", " ft"),
        ("SPRING_GAIN", n("spring_gain"), ".0f", " mm"),
        (
            "SHELL_TAIL_INLET",
            d["tail_in_shell"]["inlet"].as_f64().unwrap(),
            ".4g",
            " mm",
        ),
        (
            "SHELL_TAIL_OUTLET",
            d["tail_in_shell"]["outlet"].as_f64().unwrap(),
            ".4g",
            " mm",
        ),
        (
            "PROT_INLET",
            d["stub_protrusion"]["inlet"].as_f64().unwrap(),
            ".4g",
            " mm",
        ),
        (
            "PROT_OUTLET",
            d["stub_protrusion"]["outlet"].as_f64().unwrap(),
            ".4g",
            " mm",
        ),
        (
            "STUB_INLET",
            d["stub_allowance"]["inlet"].as_f64().unwrap(),
            ".4g",
            " mm",
        ),
        (
            "STUB_OUTLET",
            d["stub_allowance"]["outlet"].as_f64().unwrap(),
            ".4g",
            " mm",
        ),
        ("HANDLE_LENGTH", n("handle_length"), ".4g", " mm"),
        ("TOTAL_LENGTH", n("total_length"), ".4g", " mm"),
        ("GROOVE_BOTTOM_OD", n("groove_bottom_od"), ".4g", " mm"),
        ("FULL_WRAPS", n("full_wraps"), ".4g", ""),
        ("WALL", n("wall"), ".4g", " mm"),
        ("GROOVE_DEPTH", n("groove_depth"), ".4g", " mm"),
    ] {
        result.insert(name.to_owned(), json!(super::formatted(value, spec) + unit));
    }
    result.insert(
        "ROLL_SHARE".into(),
        json!(format!("1/{}", d["carbonators_per_roll"])),
    );
    Value::Object(result)
}

pub fn report() -> String {
    use std::fmt::Write;
    let d = datums();
    let (low, high) = (coil::LOW_Z, coil::HIGH_Z);
    let n = |key: &str| d[key].as_f64().unwrap();
    let f = |key: &str, spec: &str| super::formatted(n(key), spec);
    let mut out = String::new();
    writeln!(
        out,
        "Carbonator OD:               {} mm (R = {})",
        f("carbonator_od", ".1f"),
        f("carbonator_radius", ".2f")
    )
    .unwrap();
    writeln!(
        out,
        "As-wound undersize:    {} mm radial stretch",
        f("net_undersize", ".1f")
    )
    .unwrap();
    writeln!(
        out,
        "Mandrel surface OD:    {} mm (R = {})",
        f("mandrel_od", ".2f"),
        f("mandrel_radius", ".3f")
    )
    .unwrap();
    writeln!(
        out,
        "Groove bottom OD:      {} mm (= carbonator_od − 2·undersize = {})",
        f("groove_bottom_od", ".2f"),
        super::formatted(n("carbonator_od") - 2. * n("net_undersize"), ".1f")
    )
    .unwrap();
    writeln!(
        out,
        "Wall thickness:        {} mm  (groove backing: {} mm)",
        f("wall", ".1f"),
        super::formatted(n("wall") - n("groove_depth"), ".1f")
    )
    .unwrap();
    writeln!(
        out,
        "Groove:                profile R={} mm, offset {} mm, depth {} mm",
        n("groove_profile_radius"),
        f("groove_offset", ".3f"),
        f("groove_depth", ".1f")
    )
    .unwrap();
    writeln!(
        out,
        "Wind length:           {} mm  (coil tail Y span: {:?} → {:?})",
        f("wind_length", ".1f"),
        low,
        high
    )
    .unwrap();
    writeln!(
        out,
        "Inlet tail azimuth:    {}°",
        f("tail_inlet_azimuth", ".2f")
    )
    .unwrap();
    writeln!(
        out,
        "Outlet tail azimuth:   {}°",
        f("tail_outlet_azimuth", ".2f")
    )
    .unwrap();
    writeln!(
        out,
        "CCW alignment delta:   {}°",
        f("tail_ccw_delta", ".2f")
    )
    .unwrap();
    writeln!(
        out,
        "Wraps:                 {}  ({} full + {}° fractional)",
        f("total_wraps", ".4f"),
        d["full_wraps"],
        f("tail_ccw_delta", ".2f")
    )
    .unwrap();
    writeln!(
        out,
        "Pitch:                 {} mm  ({}\")",
        f("pitch", ".3f"),
        super::formatted(n("pitch") / 25.4, ".4f")
    )
    .unwrap();
    writeln!(
        out,
        "Wrap copper (mandrel): {} mm  ({} ft)",
        f("mandrel_wrap_length", ".0f"),
        super::formatted(n("mandrel_wrap_length") / 304.8, ".2f")
    )
    .unwrap();
    writeln!(
        out,
        "Wrap copper (fitted):  {} mm  ({} ft)  — {} mm of spring",
        f("wrap_length", ".0f"),
        super::formatted(n("wrap_length") / 304.8, ".2f"),
        f("spring_gain", "+.0f")
    )
    .unwrap();
    for end in ["inlet", "outlet"] {
        writeln!(
            out,
            "Stub allowance ({:<8} {} mm  ({} in-shell + {} protruding)",
            format!("{end}):"),
            super::formatted(d["stub_allowance"][end].as_f64().unwrap(), ".1f"),
            super::formatted(d["tail_in_shell"][end].as_f64().unwrap(), ".1f"),
            super::formatted(d["stub_protrusion"][end].as_f64().unwrap(), ".0f")
        )
        .unwrap();
    }
    writeln!(out, "Cut per carbonator:        the LAID wrap + {} mm of stub — struck in `cold-core-layout/_coil.cut_length`,\n                       {} per {} ft roll",
        f("stub_total", ".1f"), d["carbonators_per_roll"], f("roll_length_ft", ".0f")).unwrap();
    writeln!(
        out,
        "Total mandrel Z:       {} mm  (handle {} + wind {} + handle {})",
        f("total_length", ".1f"),
        f("handle_length", ".2f"),
        f("wind_length", ".1f"),
        f("handle_length", ".2f")
    )
    .unwrap();
    out
}
