//! Identification collar stock, fit readings, lettering recipes and documentation.
use anyhow::{Context, Result, bail};
use serde_json::{Value, json};
fn f(v: &Value, k: &str) -> Result<f64> {
    v[k].as_f64()
        .with_context(|| format!("collar source has no {k}"))
}
fn g(v: f64) -> String {
    hsm_documents::format_number(v, "g").unwrap()
}
/// The bulkhead ring's lettering and stations, as its numbers hold them.
fn ring_numbers() -> Value {
    use hsm_bulkhead_ring_numbers as n;
    let words: serde_json::Map<String, Value> = n::WORD_WIDTHS.iter().map(|&(w, x)| (w.into(), json!(x))).collect();
    let stations: serde_json::Map<String, Value> = n::STATIONS.iter().map(|&(s, w, _)| (s.into(), json!(w))).collect();
    let fluids: serde_json::Map<String, Value> = n::STATIONS.iter().map(|&(s, _, f)| (s.into(), json!(f))).collect();
    json!({"RING_W":n::RING_W,"THICK":n::THICK,"RISE":n::RISE,"WORD_FONT":n::WORD_FONT,"WORD_KIND":n::WORD_KIND,
           "WORD_SIZE":n::WORD_SIZE,"WORD_CAP":n::WORD_CAP,"WORD_DEPTH":n::WORD_DEPTH,"WORD_RAISE":n::WORD_RAISE,
           "WORD_MARGIN":n::WORD_MARGIN,"WORD_WIDTHS":words,"STATIONS":stations,"FLUIDS":fluids})
}
pub fn dispatch(r: &Value) -> Result<Value> {
    let ring = &ring_numbers();
    let od: f64 = 12.0;
    let tube_od: f64 = 6.35;
    let tolerance: f64 = 0.13;
    let shrink: f64 = 0.10;
    let slip: f64 = 0.10;
    let bore = tube_od + tolerance + shrink + slip;
    let rise = f(ring, "RING_W")?;
    let length: f64 = 30.0;
    let depth = f(ring, "WORD_DEPTH")?;
    let margin = f(ring, "WORD_MARGIN")?;
    let printed = bore - shrink;
    let wall = (od - bore) / 2.0;
    let backing = wall - depth;
    let reach = (od / 2.0).hypot(rise);
    let clearance = printed - (tube_od - tolerance);
    let rock = clearance.atan2(length) * (180.0 / std::f64::consts::PI);
    let sway = rise * (rock * (std::f64::consts::PI / 180.0)).tan();
    let mut stations = vec![];
    for (name, tube, fitted) in [
        (
            "water",
            "the customer's tap-water run, up to their angle stop",
            "pack bench",
        ),
        (
            "carb",
            "the umbilical's blue carbonated-water tail",
            "faucet bench",
        ),
        (
            "co2",
            "the customer's red tether, +Y wall of back-top to regulator",
            "pack bench",
        ),
        (
            "flavor-a",
            "the umbilical's first black flavour tail",
            "faucet bench",
        ),
        (
            "flavor-b",
            "the umbilical's second black flavour tail",
            "faucet bench",
        ),
        (
            "drain",
            "the umbilical's white 4 mm vent tail",
            "faucet bench",
        ),
    ] {
        stations.push(json!({"name":name,"word":ring["STATIONS"][name],"fluid":ring["FLUIDS"][name],"tube":tube,"fitted":fitted}));
    }
    let datum = json!({"TUBE_OD":tube_od,"LLDPE_TOL":tolerance,"BORE_SHRINK":shrink,"SLIP":slip,"BORE":bore,"OD":od,"RISE":rise,"LENGTH":length,"WORD_DEPTH":depth,"WORD_MARGIN":margin,"FACES":["top","+x","-x"]});
    let fn_name = r["fn"].as_str().unwrap_or("datums");
    let band = |face: &str| {
        [
            length - 2.0 * margin,
            (if face == "top" { od } else { rise }) - 2.0 * margin,
        ]
    };
    let bore_d = |which: &str| {
        if ["drain", "flavor-a", "flavor-b"].contains(&which) {
            4.0 + 0.0762 + shrink + slip
        } else {
            bore
        }
    };
    let scalar = match fn_name {
        "bore_printed" => Some(printed),
        "wall" => Some(wall),
        "backing" => Some(backing),
        "reach" => Some(reach),
        "clearance" => Some(clearance),
        "rock" => Some(rock),
        "flag_sway" => Some(sway),
        "bore_d" => Some(bore_d(r["which"].as_str().unwrap_or("water"))),
        _ => None,
    };
    if let Some(x) = scalar {
        return Ok(json!(x));
    }
    if fn_name == "word_band" {
        return Ok(json!(band(r["face"].as_str().unwrap_or("top"))));
    }
    if fn_name == "datums" {
        return Ok(json!({"datums":datum,"stations":stations,"ring":ring}));
    }
    if fn_name == "numbers" {
        let artwork: Value = serde_json::from_slice(&std::fs::read(
            r["artwork"].as_str().context("collar artwork path")?,
        )?)?;
        let rows:Vec<_>=stations.iter().map(|station|{let name=station["name"].as_str().unwrap();let word=station["word"].as_str().unwrap();let fluid=station["fluid"].as_str().unwrap();json!({"name":format!("tube-collar-{name}"),"word":word,"word_profiles":artwork["words"][word],"bore":bore_d(name),"color":hsm_shared_data::color::rgb8_linear(&r["palette"][fluid]["color"],true).unwrap(),"word_color":hsm_shared_data::color::rgb8_linear(&r["palette"][fluid]["word_color"],true).unwrap()})}).collect();
        return Ok(
            json!({"od":od,"rise":rise,"length":length,"word_depth":depth,"word_size":ring["WORD_SIZE"],"word_profiles_em":artwork["em_mm"],"stations":rows}),
        );
    }
    if fn_name == "report" {
        let bodies = r["bodies"].as_array().context("collar report bodies")?;
        let body = |name: &str| {
            bodies
                .iter()
                .find(|x| x["name"] == name)
                .with_context(|| format!("no collar body {name}"))
        };
        let mut lines = vec![];
        for station in &stations {
            let which = station["name"].as_str().unwrap();
            let name = format!("tube-collar-{which}");
            let collar = body(&name)?;
            let lo = &collar["min"];
            let hi = &collar["max"];
            let n = |a: &Value, i: usize| a[i].as_f64().unwrap();
            lines.push(format!(
                "Tube collar — {which} station, '{}'",
                station["word"].as_str().unwrap()
            ));
            lines.push(format!("  Ø{} wide × {} tall × {} along the tube / bore Ø{} modelled, Ø{} printed, on Ø{} LLDPE",g(od),g(od/2.0+rise),g(length),g(bore),g(printed),g(tube_od)));
            lines.push(format!(
                "  Wall {} mm, {} mm of colour behind the lettering",
                g(wall),
                g(backing)
            ));
            lines.push(format!("  Canonical-frame bounding box: X [{:.2}, {:.2}]  Y [{:.2}, {:.2}]  Z [{:.2}, {:.2}]",n(lo,0),n(hi,0),n(lo,1),n(hi,1),n(lo,2),n(hi,2)));
            lines.push(format!("-> {name}.step"));
        }
        let thick = f(ring, "THICK")?;
        let chip_rock = clearance.atan2(thick) * (180.0 / std::f64::consts::PI);
        lines.push(format!(
            "  Slips {} mm on the biggest tube a spool runs (Ø{})",
            g(slip),
            g(tube_od + tolerance)
        ));
        lines.push(format!("  Cocks {rock:.4}° on its loosest tube ({clearance:.3} mm of play over {} mm of bore), {:.0} µm at the flag's face",g(length),sway*1000.0));
        lines.push(format!(
            "  A {} mm chip on the same tube: {chip_rock:.3}°",
            g(thick)
        ));
        let volume = f(body("tube-collar-flavor-a")?, "volume")? / 1000.0;
        let word_volume = f(body("tube-collar-flavor-a-word")?, "volume")? / 1000.0;
        let variables = crate::formatted(&[
            ("COLLAR_TUBE_OD", tube_od, "g", ""),
            ("COLLAR_TUBE_HIGH", tube_od + tolerance, "g", ""),
            ("COLLAR_BORE", bore, "g", ""),
            ("COLLAR_BORE_PRINTED", printed, "g", ""),
            ("COLLAR_SHRINK", shrink, "g", ""),
            ("COLLAR_SLIP", slip, "g", ""),
            ("COLLAR_OD", od, "g", ""),
            ("COLLAR_RISE", rise, "g", ""),
            ("COLLAR_TALL", od / 2.0 + rise, "g", ""),
            ("COLLAR_LENGTH", length, "g", " mm"),
            ("COLLAR_WALL", wall, "g", ""),
            ("COLLAR_BACKING", backing, "g", ""),
            ("COLLAR_VOL", volume, ".2f", ""),
            ("COLLAR_WORD_VOL", word_volume, ".2f", ""),
            ("COLLAR_CLEARANCE", clearance, ".2f", ""),
            ("COLLAR_LLDPE_TOL", tolerance, "g", ""),
            ("COLLAR_ROCK", rock, ".2f", ""),
            ("COLLAR_CHIP_THICK", thick, "g", ""),
            ("COLLAR_CHIP_ROCK", chip_rock, ".2f", ""),
            ("COLLAR_SWAY", sway * 1000.0, ".0f", ""),
            ("COLLAR_WORD_DEPTH", depth, "g", ""),
            ("COLLAR_WORD_MARGIN", margin, "g", ""),
            ("COLLAR_WORD_SIZE", f(ring, "WORD_SIZE")?, "g", ""),
            ("COLLAR_WORD_CAP", f(ring, "WORD_CAP")?, "g", ""),
            ("COLLAR_BAND_ALONG", band("top")[0], "g", ""),
            ("COLLAR_BAND_ACROSS", band("top")[1], "g", ""),
        ]);
        return Ok(json!({"lines":lines,"variables":variables}));
    }
    bail!("unknown collar scalar operation {fn_name}")
}
