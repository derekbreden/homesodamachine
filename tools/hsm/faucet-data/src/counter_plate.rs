//! The under-counter plate's datums, rim and corners, from its numbers crate, for the Python
//! readers that still draw it. `under_counter_plate.rs` writes its laser file.

use anyhow::{Context, Result, bail};
use hsm_under_counter_plate_numbers::{self as n, Edge};
use serde_json::{Value, json};

fn datums() -> Value {
    json!({"shank_cx":n::SHANK_CX,"shank_cy":n::SHANK_CY,
        "shank_diameter":n::SHANK_DIAMETER,"shank_radius":n::SHANK_RADIUS,
        "pill_cx":n::PILL_CX,"pill_cy":n::PILL_CY,"pill_long_y":n::PILL_LONG_Y,
        "pill_short_x":n::PILL_SHORT_X,"pill_half_long":n::PILL_HALF_LONG,
        "pill_half_short":n::PILL_HALF_SHORT,"pill_cap_radius":n::PILL_CAP_RADIUS,
        "pill_top_cap_cy":n::PILL_TOP_CAP_CY,"pill_bot_cap_cy":n::PILL_BOT_CAP_CY,
        "pill_left_x":n::PILL_LEFT_X,"pill_right_x":n::PILL_RIGHT_X,
        "bore_front_x":n::BORE_FRONT_X,"disc_reach_margin":n::DISC_REACH_MARGIN,
        "disc_cx":n::DISC_CX,"disc_cy":n::DISC_CY,"disc_radius":n::DISC_RADIUS,
        "disc_diameter":n::DISC_DIAMETER,"fillet_radius":n::FILLET_RADIUS})
}

fn value(edge: &Edge) -> Value {
    match edge {
        Edge::Line(a, b) => json!({"type":"LINE","start":[a[0],a[1],0.0],"end":[b[0],b[1],0.0],"layer":"0"}),
        Edge::Arc(c, r, start, end) => json!({"type":"ARC","center":[c[0],c[1],0.0],"radius":r,
            "start_angle":start,"end_angle":end,"layer":"0"}),
    }
}

pub fn dispatch(request: &Value) -> Result<Value> {
    if let Some(x) = request["rim_x"].as_f64() {
        let Some(y) = n::rim_y_lower(x) else { bail!("math domain error") };
        return Ok(json!(y));
    }
    if let Some(wall) = request["wall_x"].as_f64() {
        let side = request["material_side"].as_f64().context("corner material side")?;
        let radius = request["radius"].as_f64().unwrap_or(n::FILLET_RADIUS);
        let Some(corner) = n::corner(wall, side, radius) else { bail!("math domain error") };
        return Ok(json!(corner));
    }
    if let Some(arc) = request.get("arc") {
        let point = |key: &str| -> Result<[f64; 2]> {
            Ok([arc[key][0].as_f64().context("arc X")?, arc[key][1].as_f64().context("arc Y")?])
        };
        let radius = arc["radius"].as_f64().context("arc radius")?;
        return Ok(value(&Edge::ccw_arc(point("center")?, radius, point("start")?, point("end")?)));
    }
    Ok(json!({"datums":datums(),"entities":n::outline().iter().map(value).collect::<Vec<_>>(),
        "version":"AC1024","units":4}))
}
