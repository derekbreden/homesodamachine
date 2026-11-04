//! The undersized rough-forming mandrel and its two individual tie-in allowances.

use serde_json::{Value, json};
use std::f64::consts::PI;

pub fn datums(evap_tail_low_z: f64, evap_tail_high_z: f64) -> Value {
    let tube_od_in = 0.250;
    let tube_radius = (tube_od_in / 2.) * 25.4;
    let carbonator_od = 127.;
    let carbonator_radius = carbonator_od / 2.;
    let net_undersize = 3.;
    let groove_depth = 1.;
    let groove_profile_radius = tube_radius;
    let groove_offset = groove_profile_radius - groove_depth;
    let mandrel_radius = carbonator_radius - net_undersize + groove_depth;
    let mandrel_od = 2. * mandrel_radius;
    let helix_path_radius = mandrel_radius + groove_offset;
    let groove_bottom_od = mandrel_od - 2. * groove_depth;
    let wall = 5.;
    let mandrel_inner_radius = mandrel_radius - wall;
    let (tail_inlet_x, tail_inlet_y, tail_inlet_z): (f64, f64, f64) = (-30., evap_tail_low_z, 20.);
    let (tail_outlet_x, tail_outlet_y, tail_outlet_z): (f64, f64, f64) =
        (30., evap_tail_high_z, 20.);
    let wind_length = tail_outlet_y - tail_inlet_y;
    let tail_inlet_azimuth = tail_inlet_z.atan2(tail_inlet_x).to_degrees();
    let tail_outlet_azimuth = tail_outlet_z.atan2(tail_outlet_x).to_degrees();
    let tail_ccw_delta = (tail_outlet_azimuth - tail_inlet_azimuth).rem_euclid(360.);
    let full_wraps = 9;
    let total_wraps = full_wraps as f64 + tail_ccw_delta / 360.;
    let pitch = wind_length / total_wraps;
    let mandrel_wrap_length = total_wraps * (2. * PI * helix_path_radius).hypot(pitch);
    let fitted_wrap_radius = carbonator_radius + tube_radius;
    let fitted_wrap_length = total_wraps * (2. * PI * fitted_wrap_radius).hypot(pitch);
    let spring_gain = fitted_wrap_length - mandrel_wrap_length;
    let stub_protrusion = json!({"inlet": 200., "outlet": 175.});
    let tail_in_shell = json!({"inlet": 154.4, "outlet": 271.9});
    let allowance = |side: &str| {
        tail_in_shell[side].as_f64().unwrap() + stub_protrusion[side].as_f64().unwrap()
    };
    let stub_allowance = json!({"inlet": allowance("inlet"), "outlet": allowance("outlet")});
    let stub_total = allowance("inlet") + allowance("outlet");
    let handle_length_in = 0.75;
    let handle_length = handle_length_in * 25.4;
    let total_length = handle_length + wind_length + handle_length;
    json!({
        "evap_tail_low_z": evap_tail_low_z, "evap_tail_high_z": evap_tail_high_z,
        "tube_od_in": tube_od_in, "tube_radius": tube_radius, "carbonator_od": carbonator_od,
        "carbonator_radius": carbonator_radius, "net_undersize": net_undersize,
        "groove_depth": groove_depth, "groove_profile_radius": groove_profile_radius,
        "groove_offset": groove_offset, "mandrel_radius": mandrel_radius, "mandrel_od": mandrel_od,
        "helix_path_radius": helix_path_radius, "groove_bottom_od": groove_bottom_od,
        "wall": wall, "mandrel_inner_radius": mandrel_inner_radius,
        "mandrel_r_range": [mandrel_inner_radius, mandrel_radius],
        "tail_inlet_x": tail_inlet_x, "tail_inlet_y": tail_inlet_y, "tail_inlet_z": tail_inlet_z,
        "tail_outlet_x": tail_outlet_x, "tail_outlet_y": tail_outlet_y, "tail_outlet_z": tail_outlet_z,
        "wind_length": wind_length, "tail_inlet_azimuth": tail_inlet_azimuth,
        "tail_outlet_azimuth": tail_outlet_azimuth, "tail_ccw_delta": tail_ccw_delta,
        "full_wraps": full_wraps, "total_wraps": total_wraps, "pitch": pitch,
        "mandrel_wrap_length": mandrel_wrap_length, "fitted_wrap_radius": fitted_wrap_radius,
        "fitted_wrap_length": fitted_wrap_length, "wrap_length": fitted_wrap_length,
        "spring_gain": spring_gain, "stub_protrusion": stub_protrusion,
        "tail_in_shell": tail_in_shell, "stub_allowance": stub_allowance, "stub_total": stub_total,
        "carbonators_per_roll": 3, "roll_length_ft": 50., "handle_length_in": handle_length_in,
        "handle_length": handle_length, "total_length": total_length,
        "mandrel_z_range": [0, total_length], "lower_handle_z_range": [0, handle_length],
        "wind_z_range": [handle_length, handle_length + wind_length],
        "upper_handle_z_range": [handle_length + wind_length, total_length]
    })
}

pub fn numbers(evap_tail_low_z: f64, evap_tail_high_z: f64, color: &Value) -> Value {
    let d = datums(evap_tail_low_z, evap_tail_high_z);
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

pub fn variables(low: f64, high: f64) -> Value {
    let d = datums(low, high);
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

pub fn report(low: f64, high: f64) -> String {
    use std::fmt::Write;
    let d = datums(low, high);
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
