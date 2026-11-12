//! Local equipment stations and scanned pump-cuff dimensions.
use anyhow::{Context, Result, ensure};
use hsm_layout_data::{self as layout, *};
use serde_json::{Value, json};

pub fn frame(rotation: Option<&Value>, translation: Option<&Value>) -> Value {
    json!({"rotation":rotation.cloned().unwrap_or_else(||json!([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])),
        "translation_mm":translation.cloned().unwrap_or_else(||json!([0.,0.,0.]))})
}
pub fn transform(pose: &Value) -> Result<Value> {
    let mut rows = Vec::new();
    for i in 0..3 {
        let mut row = pose["rotation"][i]
            .as_array()
            .context("equipment rotation")?
            .clone();
        ensure!(row.len() == 3, "equipment rotation must be 3x3");
        row.push(pose["translation_mm"][i].clone());
        rows.push(row);
    }
    Ok(json!(rows))
}
pub fn along_y(point: V3, axis: V3) -> Result<Value> {
    let end = unit(axis)?;
    let cross = [end[2], 0., -end[0]];
    let sine = norm(cross);
    let rotation = if sine < 1e-9 {
        if end[1] >= 0. {
            json!([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        } else {
            json!([[1., 0., 0.], [0., -1., 0.], [0., 0., -1.]])
        }
    } else {
        let u = mul(cross, 1. / sine);
        let cosine = end[1].clamp(-1., 1.);
        let skew = [[0., -u[2], u[1]], [u[2], 0., -u[0]], [-u[1], u[0], 0.]];
        json!(std::array::from_fn::<_, 3, _>(|i| std::array::from_fn::<
            _,
            3,
            _,
        >(|j| cosine
            * if i == j { 1. } else { 0. }
            + (1. - cosine) * u[i] * u[j]
            + sine * skew[i][j])))
    };
    Ok(frame(Some(&rotation), Some(&json!(point))))
}
pub fn chain_inlet(data: &Value) -> Result<Value> {
    let row = &data["chain"]["components"]["pp010822e"];
    let x = number(&row["visible_profile"][0][0])?;
    let origin = xyz(&row["origin_mm"])?;
    let mut point = [0.; 3];
    let mut axis = [0.; 3];
    for i in 0..3 {
        point[i] = origin[i] + number(&row["rotation"][i][0])? * x;
        axis[i] = -number(&row["rotation"][i][0])?;
    }
    Ok(json!([point, axis]))
}
pub fn reducer_insertion(data: &Value) -> Result<f64> {
    let d = &data["reducer"];
    Ok(number(&d["length_mm"])? - number(&d["body_face_x_mm"])?
        + number(&d["body_face_to_stop_display_mm"])?)
}
pub fn local_ports(name: &str, data: &Value, spec: &Value) -> Result<Value> {
    let stem = &data["stem"];
    let reducer = &data["reducer"];
    let check = &data["check"];
    Ok(match name {
        "bulkhead-water" => {
            let inlet = chain_inlet(data)?;
            let p = &inlet[0];
            let u = xyz(&inlet[1])?;
            json!({"outboard":[p,u,6.35],"inboard":[p,mul(u,-1.),6.35]})
        }
        "gas-regulator" | "co2-inlet" => {
            json!({"inlet":[[0.,0.,0.],[0.,0.,-1.],6.35],"outlet":[[0.,0.,62.814],[0.,0.,1.],6.35],"outboard":[[0.,0.,0.],[0.,0.,-1.],6.35],"inboard":[[0.,0.,62.814],[0.,0.,1.],6.35]})
        }
        "gas-check" | "discharge-chain" => {
            let end = number(&check["length_mm"])?;
            json!({"inlet":[[0.,0.,0.],[-1.,0.,0.],6.35],"outlet":[[end,0.,0.],[1.,0.,0.],6.35],"tube-port":[[end,0.,0.],[1.,0.,0.],6.35]})
        }
        "water-split" => {
            json!({"supply":[[0.,19.5,0.],[0.,1.,0.],6.35],"to-vk":[[0.,0.,19.5],[0.,0.,1.],6.35],"to-flavor":[[0.,0.,-19.5],[0.,0.,-1.],6.35]})
        }
        "suction-reducer" | "discharge-reducer" => {
            let mouth = number(&reducer["length_mm"])?
                - (number(&reducer["nominal_free_stem_to_shoulder_mm"])? - 10.);
            json!({"tube":[[mouth,0.,0.],[1.,0.,0.],6.35]})
        }
        "jg-pp061208w" => {
            let row = &data["chain"]["components"]["pp061208w"];
            let x = number(&row["visible_axial_range_mm"][1])?;
            let origin = xyz(&row["origin_mm"])?;
            let mut p = [0.; 3];
            let mut u = [0.; 3];
            for i in 0..3 {
                u[i] = number(&row["rotation"][i][0])?;
                p[i] = origin[i] + u[i] * x;
            }
            json!({"tube":[p,u,6.35]})
        }
        "valve-v-a" | "valve-v-b" | "vk-solenoid" => {
            json!({"inlet":[[0.,-29.75,11.05],[0.,-1.,0.],6.35],"outlet":[[0.,29.75,11.05],[0.,1.,0.],6.35]})
        }
        "asse1022-assembly" => {
            let rows = &data["multiplex_ports"];
            json!({"tube-in":[rows["inlet"][0],rows["inlet"][1],17.15],"tube-out":[rows["outlet"][0],rows["outlet"][1],15.88],"vent-tip":[rows["vent"][0],rows["vent"][1],7.7]})
        }
        "flow-regulator" => {
            json!({"inlet":[[0.,0.,0.],[-1.,0.,0.],6.35],"outlet":[[68.117,0.,0.],[1.,0.,0.],6.35]})
        }
        "asse-drain-adapter" => {
            let p = xyz(&data["multiplex_ports"]["vent"][0])?;
            json!({"tube":[[p[0]-25.4,p[1],p[2]-9.55],[-1.,0.,0.],4.]})
        }
        "g-ganen-pump" => {
            let ports = data["pump"]["ports"].as_object().context("pump ports")?;
            let mut crest = 0.0_f64;
            for port in ports.values() {
                for row in port["profile"].as_array().context("pump profile")? {
                    if -number(&row["distance_from_tip_mm"])? <= 11. {
                        crest = crest.max(2. * number(&row["radius_mm"])?);
                    }
                }
            }
            let diameter = (14.6_f64.powi(2) + crest.powi(2) - 9.0_f64.powi(2)).sqrt() + 1.2;
            json!({"suction":[ports["port_yminus"]["tip_mm"],ports["port_yminus"]["outward_axis"],diameter],"discharge":[ports["port_yplus"]["tip_mm"],ports["port_yplus"]["outward_axis"],diameter]})
        }
        "digiten-flow" => {
            json!({"inlet":[[-30.5,0.,0.],[-1.,0.,0.],6.35],"outlet":[[30.5,0.,0.],[1.,0.,0.],6.35]})
        }
        _ => {
            let stems = layout::stem_elbow_names(&spec["snapshots"]);
            let hosts = layout::gates();
            if stems.contains(&name) || hosts.get(name).is_some() {
                json!({"socket":[[0.,number(&stem["socket_mouth_y_mm"])?,0.],[0.,1.,0.],6.35]})
            } else {
                let rows = layout::grid(spec)?;
                let selected = rows.iter().find(|row| row["name"] == name);
                if let Some(row) = selected {
                    let d = if row["native_kind"] == "quarter" {
                        &data["jg"]
                    } else {
                        &data["drain"]
                    };
                    let a = number(&d["near_ring_face_y_mm"])?;
                    let b = number(&d["far_ring_face_y_mm"])?;
                    let diameter = number(&row["tube_od_mm"])?;
                    if name == "bulkhead-drain" {
                        json!({"outboard":[[0.,a,0.],[0.,1.,0.],diameter],"inboard":[[0.,b,0.],[0.,-1.,0.],diameter]})
                    } else {
                        json!({"tube-out":[[0.,a,0.],[0.,1.,0.],diameter],"tube-in":[[0.,b,0.],[0.,-1.,0.],diameter]})
                    }
                } else {
                    json!({})
                }
            }
        }
    })
}
fn interp(x: f64, rows: &[(f64, f64)]) -> f64 {
    if x < rows[0].0 {
        return rows[0].1;
    }
    if x > rows.last().unwrap().0 {
        return rows.last().unwrap().1;
    }
    let upper = rows.partition_point(|row| row.0 <= x);
    if upper == rows.len() {
        return rows[upper - 1].1;
    }
    if upper == 0 {
        return rows[0].1;
    }
    let (a, ra) = rows[upper - 1];
    let (b, rb) = rows[upper];
    if a == x {
        return ra;
    }
    let slope = (rb - ra) / (b - a);
    slope * (x - a) + ra
}
pub fn joint(port: &str, data: &Value) -> Result<Value> {
    let profile = &data["pump"]["ports"][if port == "suction" {
        "port_yminus"
    } else {
        "port_yplus"
    }]["profile"];
    let mut rows = profile
        .as_array()
        .context("pump profile")?
        .iter()
        .map(|row| {
            Ok((
                number(&row["distance_from_tip_mm"])?,
                number(&row["radius_mm"])?,
            ))
        })
        .collect::<Result<Vec<_>>>()?;
    rows.sort_by(|a, b| a.0.total_cmp(&b.0).then_with(|| a.1.total_cmp(&b.1)));
    ensure!(!rows.is_empty(), "empty pump profile");
    let start = rows[0].0 + 0.9;
    let first = (start, interp(start, &rows));
    rows.retain(|row| row.0 > start);
    rows.insert(0, first);
    let r0 = 9.525 / 2.;
    let mut bore = Vec::new();
    for pair in rows.windows(2) {
        let ((x, a), (y, b)) = (pair[0], pair[1]);
        bore.push((x, a.max(r0)));
        if (a - r0) * (b - r0) < 0. {
            bore.push((x + (r0 - a) / (b - a) * (y - x), r0));
        }
    }
    let stem = number(&data["reducer"]["nominal_stem_diameter_mm"])? / 2.;
    bore.extend([
        (0., rows.last().unwrap().1.max(r0)),
        (0., stem),
        (10., stem),
    ]);
    let mut bands = serde_json::Map::new();
    for (name, xc) in [("barb", start / 2.), ("stem", 5.)] {
        let mut radius = f64::NEG_INFINITY;
        for i in 0..181 {
            let x = if i == 180 {
                xc + 4.5
            } else {
                xc - 4.5 + i as f64 * (9. / 180.)
            };
            radius = radius.max(interp(x, &bore));
        }
        let opened = (radius * radius + (15.088_f64.powi(2) - 9.525_f64.powi(2)) / 4.).sqrt();
        bands.insert(name.to_owned(), json!([xc, 2. * opened]));
    }
    Ok(
        json!({"bore":bore,"bands":bands,"pivot_z":-rows.last().unwrap().1,"tube_od_mm":15.088,"tube_id_mm":9.525}),
    )
}

pub fn order(name: &str, ports: &Value) -> Vec<String> {
    let preferred: &[&str] = match name {
        "bulkhead-water" => &["outboard", "inboard"],
        "gas-regulator" | "co2-inlet" => &["inlet", "outlet", "outboard", "inboard"],
        "gas-check" | "discharge-chain" => &["inlet", "outlet", "tube-port"],
        "water-split" => &["supply", "to-vk", "to-flavor"],
        "asse1022-assembly" => &["tube-in", "tube-out", "vent-tip"],
        "g-ganen-pump" => &["suction", "discharge"],
        "valve-v-a" | "valve-v-b" | "vk-solenoid" | "flow-regulator" | "digiten-flow" => {
            &["inlet", "outlet"]
        }
        "bulkhead-drain" => &["outboard", "inboard"],
        _ => &["tube", "socket", "tube-out", "tube-in"],
    };
    preferred
        .iter()
        .filter(|name| ports.get(**name).is_some())
        .map(|name| name.to_string())
        .collect()
}
