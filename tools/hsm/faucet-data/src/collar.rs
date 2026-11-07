//! The tube collars' datums and fit readings, from their numbers crate, for the Python readers
//! that still draw them.
use anyhow::{Result, bail};
use hsm_tube_collar_numbers as n;
use serde_json::{Value, json};

/// The bulkhead ring's lettering and stations, as its numbers hold them.
fn ring_numbers() -> Value {
    use hsm_bulkhead_ring_numbers as r;
    let words: serde_json::Map<String, Value> = r::WORD_WIDTHS.iter().map(|&(w, x)| (w.into(), json!(x))).collect();
    let stations: serde_json::Map<String, Value> = r::STATIONS.iter().map(|&(s, w, _)| (s.into(), json!(w))).collect();
    let fluids: serde_json::Map<String, Value> = r::STATIONS.iter().map(|&(s, _, f)| (s.into(), json!(f))).collect();
    json!({"RING_W":r::RING_W,"THICK":r::THICK,"RISE":r::RISE,"WORD_FONT":r::WORD_FONT,"WORD_KIND":r::WORD_KIND,
           "WORD_SIZE":r::WORD_SIZE,"WORD_CAP":r::WORD_CAP,"WORD_DEPTH":r::WORD_DEPTH,"WORD_RAISE":r::WORD_RAISE,
           "WORD_MARGIN":r::WORD_MARGIN,"WORD_WIDTHS":words,"STATIONS":stations,"FLUIDS":fluids})
}

pub fn dispatch(r: &Value) -> Result<Value> {
    let reach = (n::OD / 2.0).hypot(n::RISE);
    let rock = n::CLEARANCE.atan2(n::LENGTH) * (180.0 / std::f64::consts::PI);
    let sway = n::RISE * (rock * (std::f64::consts::PI / 180.0)).tan();
    let band = |face: &str| [n::LENGTH - 2.0 * n::WORD_MARGIN, (if face == "top" { n::OD } else { n::RISE }) - 2.0 * n::WORD_MARGIN];
    let fn_name = r["fn"].as_str().unwrap_or("datums");
    let scalar = match fn_name {
        "bore_printed" => Some(n::BORE_PRINTED),
        "wall" => Some(n::WALL),
        "backing" => Some(n::BACKING),
        "reach" => Some(reach),
        "clearance" => Some(n::CLEARANCE),
        "rock" => Some(rock),
        "flag_sway" => Some(sway),
        "bore_d" => Some(n::bore(r["which"].as_str().unwrap_or("water"))),
        _ => None,
    };
    if let Some(x) = scalar {
        return Ok(json!(x));
    }
    match fn_name {
        "word_band" => Ok(json!(band(r["face"].as_str().unwrap_or("top")))),
        "datums" => {
            let stations: Vec<Value> = n::COLLARS
                .iter()
                .map(|&(name, tube, fitted)| {
                    let (word, fluid) = n::word_and_fluid(name);
                    json!({"name":name,"word":word,"fluid":fluid,"tube":tube,"fitted":fitted})
                })
                .collect();
            let datum = json!({"TUBE_OD":n::TUBE_OD,"LLDPE_TOL":n::LLDPE_TOL,"BORE_SHRINK":n::BORE_SHRINK,"SLIP":n::SLIP,
                "BORE":n::BORE,"OD":n::OD,"RISE":n::RISE,"LENGTH":n::LENGTH,"WORD_DEPTH":n::WORD_DEPTH,
                "WORD_MARGIN":n::WORD_MARGIN,"FACES":n::FACES});
            Ok(json!({"datums":datum,"stations":stations,"ring":ring_numbers()}))
        }
        _ => bail!("unknown collar scalar operation {fn_name}"),
    }
}
