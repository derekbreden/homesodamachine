//! Scalar construction recipes for the water-inlet jet's drilling jaws, the valve seat and zone C,
//! and the reference parts' providers.
#![recursion_limit = "512"]
use anyhow::{Context, Result, bail};
use hsm_documents::format_number;
use serde_json::{Value, json};
use std::{
    collections::BTreeMap,
    io::{self, BufRead, Write},
};

mod zone;
mod reference;

fn num(v: &Value, key: &str) -> Result<f64> {
    v[key]
        .as_f64()
        .with_context(|| format!("Missing number {key}"))
}
fn opt(v: &Value, key: &str, fallback: f64) -> f64 {
    v[key].as_f64().unwrap_or(fallback)
}
fn point(v: &Value) -> Result<[f64; 3]> {
    let a = v.as_array().context("Expected three coordinates")?;
    if a.len() != 3 {
        bail!("Expected three coordinates")
    }
    Ok([
        a[0].as_f64().context("coordinate")?,
        a[1].as_f64().context("coordinate")?,
        a[2].as_f64().context("coordinate")?,
    ])
}
fn variables(rows: &[(&str, f64, &str, &str)]) -> Result<Value> {
    let mut out = BTreeMap::new();
    for &(key, value, spec, suffix) in rows {
        out.insert(key, format!("{}{suffix}", format_number(value, spec)?));
    }
    Ok(serde_json::to_value(out)?)
}
fn color(v: &Value) -> Value {
    v.get("color").cloned().unwrap_or(Value::Null)
}

fn jet_fixture(v: &Value) -> Result<Value> {
    let rod = num(v, "cap_diameter")?;
    let drill = num(v, "passage_diameter")?;
    let (slip, gap, base_x, base_y, base_t, jaw_x, jaw_depth, grip) =
        (0.15, 1.0, 120.0, 90.0, 8.0, 64.0, 25.0, 30.0);
    let groove = rod / 2.0 + slip;
    let mut vars = variables(&[
        ("JET_FIXTURE_GRIP", grip, "g", " mm"),
        ("JET_FIXTURE_GROOVE", 2.0 * groove, "g", " mm"),
        ("JET_FIXTURE_GAP", gap, "g", " mm"),
        ("JET_FIXTURE_BLANK", 50.0, "g", " mm"),
        ("JET_FIXTURE_MIN_BLANK", 40.0, "g", " mm"),
    ])?;
    vars["JET_FIXTURE_BASE"] = json!(format!(
        "{} × {} × {} mm",
        format_number(base_x, "g")?,
        format_number(base_y, "g")?,
        format_number(base_t, "g")?
    ));
    vars["JET_FIXTURE_JAW_CLAMP_X"] = json!("±20 mm");
    vars["JET_FIXTURE_BASE_CLAMP_X"] = json!("±46 mm");
    Ok(
        json!({"values":{"ROD_D":rod,"GROOVE_RADIAL_SLIP":slip,"GROOVE_R":groove,"OPEN_JAW_GAP":gap,
        "BASE_X":base_x,"BASE_Y":base_y,"BASE_T":base_t,"JAW_X":jaw_x,"JAW_DEPTH":jaw_depth,"GRIP_Z":grip,
        "HANDLING_BLANK_L":50.0,"MIN_HANDLING_BLANK_L":40.0,"JAW_CLAMP_X":20.0,"BASE_CLAMP_X":46.0,
        "MESH_TOLERANCE":0.02,"MESH_ANGLE":0.15},
        "numbers":{"base":[base_x,base_y,base_t],"jaw":[jaw_x,jaw_depth,grip],"gap":gap,
            "groove_radius":groove,"stock_diameter":rod,"radial_slip":slip,"minimum_blank":40.0,
            "drill_diameter":drill,"color":color(v)},"variables":vars}),
    )
}

fn valve_seat(v: &Value) -> Result<Value> {
    use hsm_valve_seat_numbers::{self as seat, valve};
    let (inset_x, inset_y) = (valve::CORNER_INSET_X, valve::CORNER_INSET_Y);
    let post_r = valve::CORNER_BOSS_RADIUS;
    let seat_top = seat::SEAT_TOP_Z;
    let (port_r, port_z) = (valve::PORT_RADIUS, valve::PORT_CENTER_Z);
    let slip = num(v, "slip")?;
    let (socket_d, alternate_d, wall, floor, corner, air) = (
        seat::SOCKET_DIAMETER,
        seat::ALTERNATE_SOCKET_DIAMETER,
        seat::WALL,
        seat::SOCKET_FLOOR_Z,
        seat::CORNER_RADIUS,
        seat::PORT_AIR,
    );
    let socket_r = seat::SOCKET_RADIUS;
    let clearance = socket_r - post_r;
    let boss_r = seat::boss_radius(slip);
    let (hx, hy) = (seat::half_x(slip), seat::half_y(slip));
    let socket_depth = seat::SOCKET_DEPTH;
    let area = 4.0 * hx * hy - (4.0 - std::f64::consts::PI) * corner * corner;
    let r = port_r + air;
    let d = port_z - seat_top;
    let section = r * r * (d / r).acos() - d * (r * r - d * d).sqrt();
    let seat = opt(v, "seat", -floor);
    let volume = area * (seat + seat_top)
        - 4.0 * std::f64::consts::PI * socket_r * socket_r * socket_depth
        - 2.0 * hy * section;
    let gap = (port_z - port_r) - (port_z - (port_r + air));
    let method = v["method"].as_str().unwrap_or("state");
    if method == "volume" {
        return Ok(json!(volume));
    }
    if method == "socket_depth" {
        return Ok(json!(socket_depth));
    }
    if method == "port_clearance" {
        return Ok(json!(gap));
    }
    if method == "main" && (gap - air).abs() > 1e-6_f64.max(1e-9 * air.abs()) {
        bail!("port channel clearance {gap}")
    }
    Ok(
        json!({"values":{"corner_inset_x":inset_x,"corner_inset_y":inset_y,"corner_post_radius":post_r,
        "seat_top_z":seat_top,"socket_diameter":socket_d,"alternate_socket_diameter":alternate_d,
        "socket_radius":socket_r,"socket_clearance":clearance,"wall":wall,"socket_floor_z":floor,
        "boss_radius":boss_r,"seat_half_x":hx,"seat_half_y":hy,"seat_corner_radius":corner,"port_air":air},
        "variables":variables(&[("POST_DIA",2.0*post_r,".4g",""),("SOCKET_DIA",2.0*socket_r,".4g",""),
            ("PLINTH_WIDTH",2.0*hx,".4g",""),("PLINTH_DEPTH",2.0*hy,".4g",""),("PLINTH_CORNER",corner,".4g",""),
            ("BOSS_DIA",2.0*boss_r,".4g",""),("SOCKET_CLEAR",clearance,".4g"," mm"),("WALL",wall,".4g"," mm"),
            ("CORNER_PITCH_X",2.0*inset_x,"g",""),("CORNER_PITCH_Y",2.0*inset_y,"g",""),
            ("SEAT_TOP_Z",seat_top,".4g",""),("SOCKET_FLOOR_Z",floor,".4g",""),("SOCKET_DEPTH",socket_depth,".4g",""),
            ("PORT_DIA",2.0*port_r,".4g",""),("PORT_CLEARANCE",gap,".3f"," mm")])?,
        "report":format!("seat at {} mm: {} mm^3, port clearance {} mm",format_number(-floor,"g")?,format_number(volume,".1f")?,format_number(gap,".4f")?)}),
    )
}

fn request(v: &Value) -> Result<Value> {
    match v["part"].as_str().context("Missing part name")? {
        "reference" => reference::request(v),
        "water-inlet-jet-fixture" => jet_fixture(v),
        "valve-seat" => valve_seat(v),
        "funnel" | "elbow-cradle" | "funnel-frame" | "funnel-cover" | "funnel-mold" => {
            zone::request(v)
        }
        other => bail!("Unknown part-data provider {other}"),
    }
}

fn answer(line: &str) -> Value {
    let result = serde_json::from_str(line)
        .context("Invalid request JSON")
        .and_then(|v| request(&v));
    result.unwrap_or_else(|e| json!({"error":format!("{e:#}")}))
}
fn main() -> Result<()> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.as_slice() == ["--serve"] {
        let stdin = io::stdin();
        let stdout = io::stdout();
        let mut out = stdout.lock();
        for line in stdin.lock().lines() {
            writeln!(out, "{}", answer(&line?))?;
            out.flush()?;
        }
    } else if let [payload] = args.as_slice() {
        println!("{}", request(&serde_json::from_str(payload)?)?);
    } else {
        bail!("usage: part-data --serve | '<request JSON>'");
    }
    Ok(())
}
