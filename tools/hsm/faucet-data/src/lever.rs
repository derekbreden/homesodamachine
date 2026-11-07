//! The lever replica's datums and shape-preserving slopes, from its numbers crate, for the Python
//! readers that still draw it.

use anyhow::{Context, Result};
use hsm_lever_replica_numbers as n;
use serde_json::{Value, json};

pub fn pchip_request(request: &Value) -> Result<Value> {
    let points: Vec<[f64; 2]> = request["points"]
        .as_array()
        .context("PCHIP points")?
        .iter()
        .map(|v| Ok([v[0].as_f64().context("PCHIP X")?, v[1].as_f64().context("PCHIP Y")?]))
        .collect::<Result<_>>()?;
    Ok(json!(n::pchip(&points)))
}

pub fn data() -> Value {
    json!({"datums":{
        "PRINTED_OUTSIDE_WIDTH":n::PRINTED_OUTSIDE_WIDTH,"CHANNEL_PRINTED_WIDTH":n::CHANNEL_PRINTED_WIDTH,
        "FLOOR_Z":n::FLOOR_Z,"LEDGE_TOP":n::LEDGE_TOP,"LOWER_SLOT_HALF_WIDTH":n::LOWER_SLOT_HALF_WIDTH,
        "CUT_BELOW":n::CUT_BELOW,"CUT_ABOVE":n::CUT_ABOVE,"CUT_FRONT":n::CUT_FRONT,"CUT_REAR":n::CUT_REAR,
        "STL_TOLERANCE":0.035,"STL_ANGLE_TOLERANCE":0.12,
        "SHOW_PROFILE":n::SHOW_PROFILE,"REAR_BOTTOM_PROFILE":n::REAR_BOTTOM_PROFILE,
        "RAIL_BOTTOM_PROFILE":n::RAIL_BOTTOM_PROFILE,"STOP_TAIL":n::STOP_TAIL,
        "PRINTED_STOP_PROFILE":n::stop_profile(),"POCKET_START_Y":n::POCKET_START_Y,
        "POCKET_FRONT_RADIUS":n::POCKET_FRONT_RADIUS,"POCKET_STOP_JOIN_Y":n::POCKET_STOP_JOIN_Y,
        "POCKET_CEILING":n::POCKET_CEILING,"LEDGE_LIP_START":n::LEDGE_LIP_START,
        "LEDGE_LIP_MID":n::LEDGE_LIP_MID,"LEDGE_LIP_END":n::LEDGE_LIP_END,
        "LOWER_RELIEF":n::LOWER_RELIEF,"UPPER_RELIEF":n::UPPER_RELIEF},
        "half_outer":n::PRINTED_OUTSIDE_WIDTH/2.0,"half_channel":n::CHANNEL_PRINTED_WIDTH/2.0})
}
