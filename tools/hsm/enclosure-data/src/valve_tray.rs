//! Standing valve plate dimensions, stock and document readings.
use super::{array, f, text};
use anyhow::{Result, anyhow, ensure};
use hsm_enclosure_numbers::shell;
use serde_json::{Value, json};

fn settings(source: &Value) -> Result<Value> {
    Ok(
        json!({"THICK":f(source,"socket_depth")?+f(source,"wall")?,"MARGIN":shell::VALVE_TRAY_MARGIN,
              "SEAT":-f(source,"seat_top_z")?,"PORT_SLIP":source["port_air"]}),
    )
}

fn coordinates(v: &Value) -> Result<Vec<[f64; 2]>> {
    v.as_array()
        .ok_or_else(|| anyhow!("seats is an array"))?
        .iter()
        .map(|p| {
            ensure!(
                p.as_array().is_some_and(|p| p.len() == 2),
                "seat has X and Y"
            );
            Ok([
                p[0].as_f64().ok_or_else(|| anyhow!("seat X is numeric"))?,
                p[1].as_f64().ok_or_else(|| anyhow!("seat Y is numeric"))?,
            ])
        })
        .collect()
}

fn span(ys: impl Iterator<Item = f64>) -> Option<(f64, f64)> {
    ys.fold(None, |range, y| {
        Some(match range {
            Some((lo, hi)) => (lo.min(y), hi.max(y)),
            None => (y, y),
        })
    })
}

fn height(v: &Value, seats: &[[f64; 2]]) -> Result<f64> {
    let range = span(seats.iter().map(|p| p[1]));
    Ok(range.map_or(0., |(lo, hi)| hi - lo)
        + 2. * (f(&v["source"], "seat_half_y")? + f(&v["stock"], "MARGIN")?))
}

fn sockets(v: &Value, x: f64, y: f64, shift: f64) -> Result<Vec<[f64; 5]>> {
    let s = &v["source"];
    let mut result = Vec::new();
    for sx in [-1., 1.] {
        for sy in [-1., 1.] {
            result.push([
                x + sx * f(s, "corner_inset_x")?,
                y + sy * f(s, "corner_inset_y")?,
                f(s, "socket_floor_z")? + shift,
                f(s, "socket_radius")?,
                f(s, "seat_top_z")? - f(s, "socket_floor_z")? + 1.,
            ]);
        }
    }
    Ok(result)
}

fn stock(v: &Value, width: f64, seats: &[[f64; 2]]) -> Result<Value> {
    let (lo, hi) =
        span(seats.iter().map(|p| p[1])).ok_or_else(|| anyhow!("tray stock has seats"))?;
    let mid = (lo + hi) / 2.;
    let h = height(v, seats)?;
    let seat = f(&v["stock"], "SEAT")?;
    let mut cuts = Vec::new();
    let mut channels = Vec::new();
    for &[x, y] in seats {
        cuts.extend(sockets(v, x, y, seat)?);
        channels.push([
            x,
            y,
            f(&v["source"], "port_center_z")? + seat,
            f(&v["source"], "port_radius")? + f(&v["stock"], "PORT_SLIP")?,
            h + 2. * (y - mid).abs() + 2.,
        ]);
    }
    Ok(
        json!({"slab":[[-width/2.,mid-h/2.,-f(&v["stock"],"THICK")?],
                        [width/2.,mid+h/2.,0.]],"sockets":cuts,"channels":channels}),
    )
}

fn recipe(v: &Value) -> Result<Value> {
    let trays = v["trays"]
        .as_object()
        .ok_or_else(|| anyhow!("trays is a mapping"))?;
    let mut plans = Vec::new();
    for (name, row) in trays {
        let width = row[0]
            .as_f64()
            .ok_or_else(|| anyhow!("tray width is numeric"))?;
        let mut plan = stock(v, width, &coordinates(&row[1])?)?;
        plan["name"] = json!(name);
        plans.push(plan);
    }
    Ok(json!({"trays":plans,"extrusion_w":v["extrusion_w"],
        "web_sockets":sockets(v,0.,0.,0.)?,
        "web_channel":[0.,0.,v["source"]["port_center_z"],
            f(&v["source"],"port_radius")?+f(&v["stock"],"PORT_SLIP")?,height(v,&[])?+2.]}))
}

fn segment(radius: f64, over: f64) -> f64 {
    if over >= radius {
        0.
    } else {
        radius.powi(2) * (over / radius).acos() - over * (radius.powi(2) - over.powi(2)).sqrt()
    }
}

fn volume(v: &Value, width: f64, seats: &[[f64; 2]]) -> Result<f64> {
    let s = &v["source"];
    let st = &v["stock"];
    let socket = std::f64::consts::PI * f(s, "socket_radius")?.powi(2) * f(s, "socket_depth")?;
    let channel = height(v, seats)?
        * segment(
            f(s, "port_radius")? + f(st, "PORT_SLIP")?,
            f(s, "port_center_z")? - f(s, "seat_top_z")?,
        );
    Ok(width * height(v, seats)? * f(st, "THICK")? - seats.len() as f64 * (4. * socket + channel))
}

fn scalar(v: &Value, op: &str) -> Result<f64> {
    let s = &v["source"];
    let st = &v["stock"];
    Ok(match op {
        "reach" => f(s, "seat_half_y")?,
        "grip" => f(s, "seat_top_z")?,
        "depth" => f(st, "THICK")?,
        "port-drop" => f(s, "seat_top_z")? - (f(s, "port_center_z")? - f(s, "port_radius")?),
        "channel-depth" => scalar(v, "port-drop")? + f(st, "PORT_SLIP")?,
        "channel-floor" => f(st, "THICK")? - scalar(v, "channel-depth")?,
        _ => return Err(anyhow!("unknown valve tray scalar {op}")),
    })
}

fn number(x: f64, spec: &str) -> Result<String> {
    hsm_documents::format_number(x, spec)
}

fn report(v: &Value) -> Result<Value> {
    let trays = v["trays"]
        .as_object()
        .ok_or_else(|| anyhow!("trays is a mapping"))?;
    let rows = array(&v["measured"], "trays")?;
    let mut lines = vec![format!(
        "Valve tray — {} stood in enclosure-front-top: {}",
        trays.len(),
        trays.keys().cloned().collect::<Vec<_>>().join(", ")
    )];
    let mut total = 0.;
    for row in rows {
        let name = text(row, "name")?;
        let plan = &trays[name];
        let width = plan[0]
            .as_f64()
            .ok_or_else(|| anyhow!("tray width is numeric"))?;
        let seats = coordinates(&plan[1])?;
        let material = f(row, "volume")?;
        total += material;
        let poses = seats
            .iter()
            .map(|p| {
                Ok(format!(
                    "({}, {})",
                    number(p[0], ".3f")?,
                    number(p[1], ".3f")?
                ))
            })
            .collect::<Result<Vec<_>>>()?
            .join(", ");
        lines.push(format!(
            "  {name}: {} x {} x {}, {} seats at {poses}",
            number(width, "g")?,
            number(height(v, &seats)?, "g")?,
            number(f(&v["stock"], "THICK")?, "g")?,
            seats.len()
        ));
        let valid = if row["valid"] == true {
            "True"
        } else {
            "False"
        };
        lines.push(format!(
            "    material {} cm^3, closed form {} cm^3, valid {valid}",
            number(material / 1000., ".2f")?,
            number(volume(v, width, &seats)? / 1000., ".2f")?
        ));
    }
    let first = trays
        .values()
        .min_by(|a, b| {
            a[0].as_f64()
                .unwrap_or(0.)
                .total_cmp(&b[0].as_f64().unwrap_or(0.))
                .then_with(|| {
                    // Python sorts the (width, seats) pairs lexicographically.
                    coordinates(&a[1])
                        .unwrap_or_default()
                        .partial_cmp(&coordinates(&b[1]).unwrap_or_default())
                        .unwrap_or(std::cmp::Ordering::Equal)
                })
        })
        .ok_or_else(|| anyhow!("valve tray report has trays"))?;
    let width = first[0]
        .as_f64()
        .ok_or_else(|| anyhow!("tray width is numeric"))?;
    let seats = coordinates(&first[1])?;
    let source = &v["source"];
    let stock = &v["stock"];
    let ext = f(&v["measured"], "extrusion_w")?;
    let web = f(&v["measured"], "web")?;
    lines.push(format!(
        "  a post stands {} mm in the plate of {} mm",
        number(scalar(v, "grip")?, ".3f")?,
        number(f(source, "seat_top_z")?, "g")?
    ));
    lines.push(format!(
        "  socket to port channel: {} mm — {}% of a {} bead",
        number(web, ".4f")?,
        number(100. * web / ext, ".0f")?,
        number(ext, "g")?
    ));
    let mut heights = trays
        .values()
        .map(|p| height(v, &coordinates(&p[1])?))
        .collect::<Result<Vec<_>>>()?;
    heights.sort_by(f64::total_cmp);
    heights.dedup();
    let mut steps = Vec::new();
    for plan in trays.values() {
        let s = coordinates(&plan[1])?;
        let (lo, hi) = span(s.iter().map(|p| p[1])).ok_or_else(|| anyhow!("tray has seats"))?;
        if hi - lo > 1e-9 {
            steps.push(number(hi - lo, "g")?);
        }
    }
    let mut variables = serde_json::Map::new();
    for (key, x, spec) in [
        ("TRAY_W", width, "g"),
        ("TRAY_T", f(stock, "THICK")?, "g"),
        ("TRAY_D", scalar(v, "depth")?, "g"),
        ("TRAY_SEAT", f(stock, "SEAT")?, "g"),
        ("TRAY_MARGIN", f(stock, "MARGIN")?, "g"),
        ("TRAY_REACH", scalar(v, "reach")?, "g"),
        ("TRAY_VOL", total / 1000., ".2f"),
        ("SOCKET_DIA", 2. * f(source, "socket_radius")?, ".4g"),
        ("SOCKET_DEPTH", f(source, "socket_depth")?, "g"),
        (
            "SOCKET_FLOOR",
            f(stock, "THICK")? - f(source, "socket_depth")?,
            "g",
        ),
        (
            "CHANNEL_DIA",
            2. * (f(source, "port_radius")? + f(stock, "PORT_SLIP")?),
            ".4g",
        ),
        ("CHANNEL_DEPTH", scalar(v, "channel-depth")?, ".2f"),
        ("CHANNEL_FLOOR", scalar(v, "channel-floor")?, ".2f"),
        ("PORT_DROP", scalar(v, "port-drop")?, ".2f"),
        ("PORT_SLIP", f(stock, "PORT_SLIP")?, "g"),
        ("TRAY_POST", f(source, "seat_top_z")?, "g"),
        ("TRAY_GRIP", scalar(v, "grip")?, ".3f"),
        ("TRAY_WEB", web, ".3f"),
        ("TRAY_PORT_SLIP", f(stock, "PORT_SLIP")?, "g"),
        ("TRAY_EXTRUSION", ext, "g"),
        ("TRAY_WEB_PCT", 100. * web / ext, ".0f"),
    ] {
        variables.insert(key.into(), json!(number(x, spec)?));
    }
    variables.insert(
        "TRAY_H".into(),
        json!(
            heights
                .iter()
                .map(|h| number(*h, "g"))
                .collect::<Result<Vec<_>>>()?
                .join("/")
        ),
    );
    variables.insert("TRAY_AFT_STEP".into(), json!(steps.join("/")));
    variables.insert("TRAY_COUNT".into(), json!(trays.len().to_string()));
    variables.insert("TRAY_SEATS".into(), json!(seats.len().to_string()));
    Ok(json!({"lines":lines,"variables":variables}))
}

pub fn dispatch(v: &Value) -> Result<Value> {
    let op = text(v, "op")?
        .strip_prefix("valve-tray-")
        .ok_or_else(|| anyhow!("valve tray op"))?;
    Ok(match op {
        "defaults" => settings(&v["source"])?,
        "height" => json!(height(v, &coordinates(&v["seats"])?)?),
        "wall-root-floors" => {
            let seats = coordinates(&v["seats"])?;
            let (lo, hi) =
                span(seats.iter().map(|p| p[0])).ok_or_else(|| anyhow!("wall roots have seats"))?;
            let mut floors = Vec::new();
            for edge in [lo, hi] {
                let floor = seats
                    .iter()
                    .filter(|p| (p[0] - edge).abs() < 1e-6)
                    .map(|p| p[1])
                    .min_by(f64::total_cmp)
                    .ok_or_else(|| anyhow!("wall has an outer row"))?;
                floors.push(floor - scalar(v, "reach")? - f(&v["stock"], "MARGIN")?);
            }
            json!(floors)
        }
        "sockets" => json!(sockets(v, f(v, "x")?, f(v, "y")?, f(v, "shift")?)?),
        "stock" => stock(v, f(v, "width")?, &coordinates(&v["seats"])?)?,
        "recipe" => recipe(v)?,
        "segment" => json!(segment(f(v, "radius")?, f(v, "over")?)),
        "volume" => json!(volume(v, f(v, "width")?, &coordinates(&v["seats"])?)?),
        "report" => report(v)?,
        _ => json!(scalar(v, op)?),
    })
}
