//! The evaporator coil's answers for the Python readers that still ask: the finished winding, its
//! ride over the reed bridge, its tangent tail forms and the copper ledger, from the coil's
//! numbers crate.

use anyhow::{Context, Result, bail};
use hsm_coil_numbers::{self as coil, Segment, Tail};
use serde_json::{Value, json};

fn constants() -> Value {
    let [(edge, plateau), (outer_edge, wall)] = coil::ride_radii();
    json!({
        "TUBE_R": coil::TUBE_RADIUS, "WIND_R": coil::WIND_RADIUS, "TOTAL_WRAPS": coil::WRAPS,
        "COPPER_BEND": coil::bend_floor(), "AZ_IN": coil::INLET_AZIMUTH, "AZ_OUT": coil::OUTLET_AZIMUTH,
        "WIND_HEIGHT": coil::WIND_HEIGHT, "PITCH": coil::PITCH, "BRIDGE_LIFT": coil::bridge_lift(),
        "BRIDGE_RAMP": coil::bridge_ramp(), "BRIDGE_ARC_RUNOUT": coil::bridge_arc_runout(),
        "RIDE_RADII": [[edge, plateau], [outer_edge, wall]],
        "BRIDGE_Z": coil::bridge_z(),
        "BRIDGE_AXIAL_RAMP": coil::bridge_axial_ramp(),
        "WRAP_SAMPLES_PER_TURN": coil::SAMPLES_PER_TURN, "TAIL_BEND_R": coil::TAIL_BEND_RADIUS,
        "STUB_TAIL_TOL": coil::STUB_TAIL_TOLERANCE
    })
}

fn segment(segment: &Segment, with_midpoints: bool) -> Value {
    match segment {
        Segment::Bend { id, start, end, mid, radius, degrees, tangent, normal } => {
            let mut value = json!({"id": id, "kind": "bend", "start": start, "end": end,
                "radius": radius, "angle": degrees, "tangent": tangent, "normal": normal});
            if with_midpoints {
                value["mid"] = json!(mid);
            }
            value
        }
        Segment::Straight { id, start, end, length } => {
            json!({"id": id, "kind": "straight", "start": start, "end": end, "length": length})
        }
    }
}

fn tail_layout(tail: Tail, working_tail: bool, with_midpoints: bool) -> Value {
    let form = coil::tail_form(tail, working_tail);
    let segments: Vec<Value> = form.segments.iter().map(|s| segment(s, with_midpoints)).collect();
    if with_midpoints {
        json!({"segments": segments, "point": form.point, "tangent": form.tangent})
    } else {
        json!(segments)
    }
}

fn report(input: &Value) -> String {
    use std::fmt::Write;
    let f = super::formatted;
    let wrap = input["laid_length"].as_f64().unwrap_or_else(coil::wrap_length);
    let stock_name = input["stock_name"].as_str().unwrap_or("");
    let stock_source = input["stock_source"].as_str().unwrap_or("");
    let carbonator = hsm_cold_core_interface::CARBONATOR_OUTER_RADIUS;
    let mut out = String::new();
    writeln!(out, "  evaporator coil").unwrap();
    writeln!(
        out,
        "    stock           {stock_name}, min bend {} — {stock_source}",
        f(coil::bend_floor(), ".2f")
    )
    .unwrap();
    writeln!(
        out,
        "    wound at        r {} (carbonator {} + tube {}); the mandrel winds at r {}",
        f(coil::WIND_RADIUS, ".3f"),
        f(carbonator, ".1f"),
        f(coil::TUBE_RADIUS, ".3f"),
        f(coil::MANDREL_WIND_RADIUS, ".3f")
    )
    .unwrap();
    writeln!(
        out,
        "    wraps           {} at {} mm pitch, z {}..{}",
        f(coil::WRAPS, ".3f"),
        f(coil::PITCH, ".4g"),
        f(coil::LOW_Z, ".1f"),
        f(coil::HIGH_Z, ".1f")
    )
    .unwrap();
    writeln!(
        out,
        "    azimuths        inlet {}°, outlet {}°, CCW delta {}°",
        f(coil::INLET_AZIMUTH, "+.2f"),
        f(coil::OUTLET_AZIMUTH, "+.2f"),
        f((coil::OUTLET_AZIMUTH - coil::INLET_AZIMUTH).rem_euclid(360.), ".2f")
    )
    .unwrap();
    writeln!(
        out,
        "    wrap laid       {} mm ({} ft) — mandrel {}, sprung {}, reed bridge {}",
        f(wrap, ".0f"),
        f(wrap / 304.8, ".2f"),
        f(coil::mandrel_wrap_length(), ".0f"),
        f(coil::fitted_wrap_length(), ".0f"),
        f(wrap - coil::plain_wrap_length(), "+.0f")
    )
    .unwrap();
    for tail in Tail::BOTH {
        let end = tail.name();
        let length = input["tail_lengths"][end].as_f64().unwrap_or_else(|| coil::tail_length(tail));
        writeln!(
            out,
            "    {:15} {} mm allowed = {} mm drawn in-shell ({} billed) + {} protruding",
            format!("{end} stub"),
            f(coil::stub_allowance(tail), ".1f"),
            f(length, ".1f"),
            f(coil::tail_in_shell(tail), ".1f"),
            f(coil::stub_protrusion(tail), ".0f")
        )
        .unwrap();
    }
    let cut = wrap + coil::stub_total();
    let rolls = f64::from(coil::CARBONATORS_PER_ROLL);
    let spare = coil::ROLL_LENGTH_FT - rolls * cut / 304.8;
    writeln!(
        out,
        "    cut per carb    {} mm ({} ft); {} per {} ft roll leaves {} ft ({} mm)",
        f(cut, ".1f"),
        f(cut / 304.8, ".3f"),
        f(rolls, "g"),
        f(coil::ROLL_LENGTH_FT, ".0f"),
        f(spare, "+.3f"),
        f(spare * 304.8, "+.0f")
    )
    .unwrap();
    out
}

pub fn request(input: &Value) -> Result<Value> {
    let n = |key: &str| super::number(input, key);
    let tail = || -> Result<Tail> {
        match input["which"].as_str().context("coil tail needs which")? {
            "inlet" => Ok(Tail::Inlet),
            "outlet" => Ok(Tail::Outlet),
            side => bail!("unknown coil tail {side}"),
        }
    };
    match input["action"].as_str().context("coil request needs action")? {
        "constants" => Ok(constants()),
        "at" => Ok(json!(coil::at(
            n("azimuth_deg")?,
            n("z")?,
            input["radius"].as_f64().unwrap_or(coil::WIND_RADIUS)
        ))),
        "ease" => Ok(json!(coil::ease(n("t")?))),
        "ride-radius" => Ok(json!(coil::ride_radius(n("azimuth_deg")?, n("z")?))),
        "wrap-points" => Ok(json!(coil::wrap_points())),
        "wrap-length" => Ok(json!(coil::wrap_length())),
        "bridge-lift-length" => Ok(json!(coil::bridge_lift_length())),
        "gap-z-near" => Ok(json!(coil::gap_z_near(n("azimuth_deg")?, n("target_z")?))),
        action @ ("tail-layout" | "tail-edges") => Ok(tail_layout(
            tail()?,
            input["working_tail"].as_bool().unwrap_or(false),
            action == "tail-edges",
        )),
        "tail-length" => Ok(json!(coil::tail_length(tail()?))),
        "tail-ledger" => {
            let tolerance = coil::STUB_TAIL_TOLERANCE;
            let rows: Vec<_> = Tail::BOTH.iter().map(|&tail| {
                let end = tail.name();
                let drawn = coil::tail_length(tail);
                let billed = coil::tail_in_shell(tail);
                json!({"holds": (drawn - billed).abs() <= tolerance,
                    "detail": format!("{end} tail draws {} mm against the {} mm `coil_mandrel.tail_in_shell` bills — {} mm out of the {} mm that end has to protrude with",
                        super::formatted(drawn, ".1f"), super::formatted(billed, ".1f"),
                        super::formatted(drawn - billed, "+.1f"),
                        super::formatted(coil::stub_protrusion(tail), ".0f"))})
            }).collect();
            Ok(
                json!({"label": "Each coil tail's in-shell run is the one its stub allowance bills",
                "target": format!("within {} mm of `coil_mandrel.tail_in_shell`", super::formatted(tolerance, ".1f")),
                "rows": rows}),
            )
        }
        "tail-points" => {
            let form = coil::tail_form(tail()?, false);
            let mut points = vec![form.segments[0].start()];
            points.extend(form.segments.iter().map(Segment::end));
            Ok(json!(points))
        }
        "cut-length" => Ok(json!(coil::cut_length())),
        "roll-spare-ft" => Ok(json!(coil::roll_spare_ft())),
        "report" => Ok(json!(report(input))),
        action => bail!("unknown coil action {action}"),
    }
}
