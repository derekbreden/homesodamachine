//! Assembly facts, route handoff and scene documents from live scalar providers.
use anyhow::{Context, Result, ensure};
use serde_json::{Map, Value, json};
use std::collections::{BTreeMap, BTreeSet};

fn object(value: &Value) -> Result<&Map<String, Value>> {
    value.as_object().context("report expects an object")
}
fn array(value: &Value) -> Result<&Vec<Value>> {
    value.as_array().context("report expects an array")
}
fn text(value: &Value) -> Result<&str> {
    value.as_str().context("report expects text")
}
fn number(value: &Value) -> Result<f64> {
    value.as_f64().context("report expects a number")
}
fn get<'a>(value: &'a Value, key: &str) -> Result<&'a Value> {
    value
        .get(key)
        .with_context(|| format!("report has no {key}"))
}
fn vec3(value: &Value) -> Result<[f64; 3]> {
    let rows = array(value)?;
    ensure!(rows.len() == 3, "report vector needs three coordinates");
    Ok([number(&rows[0])?, number(&rows[1])?, number(&rows[2])?])
}
fn point(frame: &Value, value: [f64; 3]) -> Result<[f64; 3]> {
    let frame = array(frame)?;
    let mut out = [0.; 3];
    for i in 0..3 {
        let row = array(&frame[i])?;
        out[i] = (0..3)
            .map(|j| number(&row[j]).map(|v| v * value[j]))
            .collect::<Result<Vec<_>>>()?
            .iter()
            .sum::<f64>()
            + number(&row[3])?;
    }
    Ok(out)
}
fn direction(frame: &Value, value: [f64; 3]) -> Result<[f64; 3]> {
    let frame = array(frame)?;
    let mut out = [0.; 3];
    for i in 0..3 {
        out[i] = (0..3)
            .map(|j| number(&frame[i][j]).map(|v| v * value[j]))
            .collect::<Result<Vec<_>>>()?
            .iter()
            .sum();
    }
    Ok(out)
}
fn distance(a: [f64; 3], b: [f64; 3]) -> f64 {
    a.into_iter()
        .zip(b)
        .map(|(a, b)| (a - b) * (a - b))
        .sum::<f64>()
        .sqrt()
}
fn unit(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    let d = distance(a, b);
    std::array::from_fn(|i| (b[i] - a[i]) / d)
}
fn rounded(value: f64, digits: usize) -> f64 {
    format!("{value:.digits$}").parse().unwrap()
}
fn rows_or_empty<'a>(value: &'a Value, key: &str) -> Vec<&'a Value> {
    value
        .get(key)
        .and_then(Value::as_array)
        .map(|rows| rows.iter().collect())
        .unwrap_or_default()
}
fn keys_in_order(value: &Value, order: Option<&Value>) -> Result<Vec<String>> {
    if let Some(order) = order.filter(|v| v.is_array()) {
        array(order)?
            .iter()
            .map(|v| text(v).map(str::to_owned))
            .collect()
    } else {
        Ok(object(value)?.keys().cloned().collect())
    }
}
pub(crate) fn plain(value: &Value) -> Result<Value> {
    match value {
        Value::Array(rows) => rows
            .iter()
            .map(plain)
            .collect::<Result<Vec<_>>>()
            .map(Value::Array),
        Value::Object(row) => {
            if let Some(fields) = row
                .get("fields")
                .filter(|_| row.contains_key("__hsm_namedtuple__"))
            {
                let fields = array(fields)?;
                let values = array(get(value, "values")?)?;
                ensure!(fields.len() == values.len(), "named record length");
                let mut out = Map::new();
                for (key, value) in fields.iter().zip(values) {
                    out.insert(text(key)?.to_owned(), plain(value)?);
                }
                Ok(Value::Object(out))
            } else if let Some(values) = row.get("__hsm_dict__") {
                let mut out = Map::new();
                for pair in array(values)? {
                    let pair = array(pair)?;
                    ensure!(pair.len() == 2, "dictionary pair");
                    out.insert(text(&pair[0])?.to_owned(), plain(&pair[1])?);
                }
                Ok(Value::Object(out))
            } else if let Some(values) = row.get("__hsm_list__") {
                plain(values)
            } else {
                row.iter()
                    .map(|(key, value)| Ok((key.clone(), plain(value)?)))
                    .collect::<Result<Map<_, _>>>()
                    .map(Value::Object)
            }
        }
        _ => Ok(value.clone()),
    }
}

pub fn bounds(spec: &Value) -> Result<Value> {
    let metadata = get(spec, "metadata")?;
    let aliases = spec.get("aliases").and_then(Value::as_object);
    let external: BTreeSet<&str> = metadata
        .get("core_external_names")
        .or_else(|| metadata.get("core_external_components"))
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
        .collect();
    let mut out: BTreeMap<String, [f64; 6]> = BTreeMap::new();
    for (source, value) in object(get(metadata, "raw_bounds")?)? {
        let mut name = aliases
            .and_then(|rows| rows.get(source))
            .and_then(Value::as_str)
            .unwrap_or(source);
        if let Some(leaf) = name.strip_prefix("cold-core/") {
            if !external.contains(leaf) {
                continue;
            }
            name = leaf;
        }
        if ["wire-", "wiring-", "terminal-"]
            .iter()
            .any(|prefix| name.starts_with(prefix))
        {
            continue;
        }
        let row = array(value)?;
        let (low, high) = if row.len() == 6 {
            (vec3(&json!(&row[..3]))?, vec3(&json!(&row[3..]))?)
        } else {
            (vec3(&row[0])?, vec3(&row[1])?)
        };
        let mut bb = [low[0], low[1], low[2], high[0], high[1], high[2]];
        if let Some(held) = out.get(name) {
            for i in 0..3 {
                bb[i] = bb[i].min(held[i]);
                bb[i + 3] = bb[i + 3].max(held[i + 3]);
            }
        }
        out.insert(name.to_owned(), bb);
    }
    if let Some(bb) = metadata
        .get("frames")
        .and_then(|f| f.get("foam-assembly"))
        .and_then(|f| f.get("bb"))
    {
        let bb = array(bb)?;
        ensure!(bb.len() == 6, "foam frame bounds");
        out.insert(
            "foam-assembly".to_owned(),
            [
                number(&bb[0])?,
                number(&bb[2])?,
                number(&bb[4])?,
                number(&bb[1])?,
                number(&bb[3])?,
                number(&bb[5])?,
            ],
        );
    }
    Ok(json!(out))
}

pub fn ports(frame: &Value) -> Result<Value> {
    let mut out = Map::new();
    if let Some(rows) = frame.get("ports").and_then(Value::as_object) {
        for (name, row) in rows {
            let (pos, axis, diam) = if row.is_object() {
                (get(row, "pos")?, get(row, "axis")?, get(row, "diam")?)
            } else {
                let row = array(row)?;
                (&row[0], &row[1], &row[2])
            };
            out.insert(
                name.clone(),
                json!({"pos":plain(pos)?,"axis":plain(axis)?,"diam":number(diam)?}),
            );
        }
    }
    Ok(Value::Object(out))
}

pub fn run_length(row: &Value) -> Result<f64> {
    if let Some(value) = row.get("length") {
        return number(value);
    }
    let points = array(get(row, "pts")?)?
        .iter()
        .map(vec3)
        .collect::<Result<Vec<_>>>()?;
    let straight: f64 = points.windows(2).map(|p| distance(p[0], p[1])).sum();
    let mut reduction = 0.;
    for bend in array(get(row, "bends")?)? {
        let bend = array(bend)?;
        let index = bend[0].as_u64().context("bend index")?.to_string();
        let radius = number(get(&row["radii"], &index)?)?;
        let angle = number(&bend[1])?.to_radians();
        reduction += 2. * radius * (angle / 2.).tan() - radius * angle;
    }
    Ok(straight - reduction)
}

pub fn route_rows(metadata: &Value) -> Result<Value> {
    let empty = json!({});
    let specs = metadata
        .get("native_route_specs")
        .or_else(|| metadata.get("routes"))
        .unwrap_or(&empty);
    let mut native = Map::new();
    let route_order = keys_in_order(specs, metadata.get("native_route_order"))?;
    for name in &route_order {
        let spec = get(specs, name)?;
        let owners = spec.get("owners").cloned().unwrap_or_else(|| json!([""]));
        let owners = array(&owners)?;
        let from = spec
            .get("frm")
            .or_else(|| spec.get("from"))
            .unwrap_or(&owners[0]);
        let to = spec.get("to").unwrap_or_else(|| owners.last().unwrap());
        let segments = get(spec, "segments")?;
        native.insert(
            name.clone(),
            json!({"id":name,"frm":from,"to":to,
            "length":number(get(&metadata["route_lengths"],name)?)?,
            "corners":array(segments)?.iter().filter(|row|row["kind"]!="line").count(),
            "bend":spec["minimum_radius_mm"].as_f64().unwrap_or(0.),"diam":number(&spec["od_mm"])?,
            "made":"drawn","segments":plain(segments)?,"spool":spec.get("spool")}),
        );
    }
    let mut runs = Vec::new();
    for row in rows_or_empty(metadata, "runs") {
        let id = text(&row["id"])?;
        if specs.get(id).is_none() {
            runs.push(json!({"id":id,"frm":row["frm"],"to":row["to"],"length":run_length(row)?,
            "corners":array(&row["bends"])?.len(),"bend":number(&row["bend"])?,"diam":number(&row["diam"])?,"made":"drawn","status":"complete"}));
        }
    }
    let groups = metadata.get("native_connections").unwrap_or(&empty);
    let mut names: BTreeSet<String> = object(&metadata["raw_bounds"])?.keys().cloned().collect();
    for name in names.clone() {
        names.insert(name.rsplit('/').next().unwrap().to_owned());
    }
    let grouped: BTreeSet<&str> = object(groups)?
        .values()
        .flat_map(|row| {
            row["native_routes"]
                .as_array()
                .into_iter()
                .flatten()
                .filter_map(Value::as_str)
        })
        .collect();
    for name in keys_in_order(
        groups,
        metadata
            .get("connection_order")
            .or_else(|| metadata.get("native_connection_order")),
    )? {
        let group = get(groups, &name)?;
        let route_names = array(&group["native_routes"])?;
        let rows = route_names
            .iter()
            .filter_map(|key| native.get(key.as_str()?))
            .collect::<Vec<_>>();
        let missing = route_names
            .iter()
            .filter(|key| native.get(key.as_str().unwrap_or("")).is_none())
            .cloned()
            .collect::<Vec<_>>();
        let fittings = rows_or_empty(group, "fittings");
        let missing_fittings = fittings
            .iter()
            .filter(|key| !names.contains(key.as_str().unwrap_or("")))
            .cloned()
            .cloned()
            .collect::<Vec<_>>();
        let complete = missing.is_empty() && missing_fittings.is_empty();
        let length = rows
            .iter()
            .map(|row| row["length"].as_f64().unwrap())
            .sum::<f64>();
        let bend = rows
            .iter()
            .filter_map(|row| row["bend"].as_f64().filter(|v| *v > 0.))
            .reduce(f64::min)
            .unwrap_or(0.);
        runs.push(json!({"id":name,"frm":group["from"],"to":group["to"],"length":if complete {json!(length)} else {Value::Null},
            "corners":rows.iter().map(|row|row["corners"].as_u64().unwrap()).sum::<u64>(),"bend":bend,
            "diam":rows.iter().filter_map(|row|row["diam"].as_f64()).reduce(f64::max).unwrap_or(0.),"made":group["made"],
            "native_routes":route_names,"fittings":fittings,"status":if complete {"complete"} else {"incomplete"},
            "missing_native_routes":missing,"missing_fittings":missing_fittings}));
    }
    for name in &route_order {
        if !grouped.contains(name.as_str()) {
            let mut row = native[name].clone();
            row["status"] = json!("complete");
            runs.push(row);
        }
    }
    Ok(json!([
        runs,
        route_order
            .iter()
            .map(|name| native[name].clone())
            .collect::<Vec<_>>()
    ]))
}

pub fn route_metadata(request: &Value) -> Result<Value> {
    let metadata = &request["spec"]["metadata"];
    let checked = &request["checked"];
    if let Some(mut value) = metadata.get("route_metadata").cloned() {
        value["unsupported_spans"] =
            checked
                .get("unsupported_spans")
                .cloned()
                .unwrap_or_else(|| {
                    value
                        .get("unsupported_spans")
                        .cloned()
                        .unwrap_or_else(|| json!({}))
                });
        return plain(&value);
    }
    let empty = json!({});
    let specs = metadata
        .get("native_route_specs")
        .or_else(|| metadata.get("routes"))
        .unwrap_or(&empty);
    let mut frames = Map::new();
    if let Some(rows) = metadata.get("world_ports").and_then(Value::as_object) {
        for (name, table) in rows {
            frames.insert(name.clone(), ports(&json!({"ports":table}))?);
        }
    }
    for (name, frame) in object(&metadata["frames"])? {
        frames.insert(name.clone(), ports(frame)?);
    }
    let mut ends = Map::new();
    let ids: BTreeSet<&str> = rows_or_empty(metadata, "runs")
        .iter()
        .filter_map(|row| row["id"].as_str())
        .collect();
    for run in rows_or_empty(metadata, "runs") {
        let name = text(&run["id"])?;
        let pts = array(&run["pts"])?;
        ensure!(pts.len() >= 2, "route endpoints need two points");
        let mut pairs = Map::new();
        for (which, owner, at, toward) in [
            ("frm", text(&run["frm"])?, vec3(&pts[0])?, vec3(&pts[1])?),
            (
                "to",
                text(&run["to"])?,
                vec3(pts.last().unwrap())?,
                vec3(&pts[pts.len() - 2])?,
            ),
        ] {
            let (component, port) = owner.split_once('.').unwrap_or((owner, ""));
            let table = frames.get(component).and_then(Value::as_object);
            let row = if let Some(table) = table.filter(|table| !table.is_empty()) {
                let selected = if port.is_empty() {
                    // Port order is explicit because equal-distance endpoints retain the source's first port.
                    let order = request
                        .get("port_order")
                        .and_then(|v| v.get(component))
                        .and_then(Value::as_array);
                    let names: Vec<&str> = order
                        .map(|rows| rows.iter().filter_map(Value::as_str).collect())
                        .unwrap_or_else(|| table.keys().map(String::as_str).collect());
                    names
                        .into_iter()
                        .map(|name| Ok((name, distance(vec3(&table[name]["pos"])?, at))))
                        .collect::<Result<Vec<_>>>()?
                        .into_iter()
                        .min_by(|a, b| a.1.total_cmp(&b.1))
                        .context("port table empty")?
                        .0
                } else {
                    port
                };
                let held = table.get(selected).with_context(|| {
                    format!("{component}.{selected}: placement plan has no named port")
                })?;
                json!({"frame":component,"port":selected,"at":held["pos"],"normal":held["axis"],"diam":held["diam"]})
            } else {
                ensure!(
                    port.is_empty(),
                    "{component}.{port}: the placement plan has no named port frame"
                );
                json!({"frame":component,"port":"socket","at":at,"normal":unit(at,toward),"diam":run["diam"]})
            };
            pairs.insert(which.to_owned(), row);
        }
        ends.insert(name.to_owned(), Value::Object(pairs));
    }
    let mut cap = Map::new();
    let mut side = Map::new();
    for (key, target) in [
        ("cap_local_points", &mut cap),
        ("cap_side_local_points", &mut side),
    ] {
        if let Some(rows) = request.get(key).and_then(Value::as_object) {
            for (name, row) in rows {
                if ids.contains(name.as_str()) {
                    target.insert(
                        name.clone(),
                        json!(point(&metadata["core_carry"], vec3(row)?)?),
                    );
                }
            }
        }
    }
    Ok(json!({"schema":1,"native_route_specs":specs,
        "anchor_sites":metadata.get("anchor_sites").unwrap_or(&request["anchor_sites"]),
        "tube_anchor_sites":metadata.get("tube_anchor_sites"),"ends":ends,"cap_anchor_points":cap,"cap_side_anchor_points":side,
        "spools":request["spools"],"unsupported_spans":checked["unsupported_spans"]}))
}

pub fn scene(request: &Value) -> Result<Value> {
    let metadata = &request["spec"]["metadata"];
    let mut frames = Map::new();
    for (name, frame) in object(&metadata["frames"])? {
        let bb = if let Some(bb) = frame.get("bb") {
            bb.clone()
        } else {
            let raw = array(get(&metadata["raw_bounds"], name)?)?;
            let low = array(&raw[0])?;
            let high = array(&raw[1])?;
            json!([low[0], high[0], low[1], high[1], low[2], high[2]])
        };
        let ports = object(&ports(frame)?)?
            .iter()
            .map(|(name, row)| (name.clone(), json!([row["pos"], row["axis"], row["diam"]])))
            .collect::<Map<_, _>>();
        frames.insert(name.clone(), json!({"ports":ports,"bb":bb}));
    }
    let fields: BTreeSet<&str> = array(&request["run_fields"])?
        .iter()
        .filter_map(Value::as_str)
        .collect();
    let runs = rows_or_empty(metadata, "runs")
        .iter()
        .map(|row| {
            object(row).map(|row| {
                row.iter()
                    .filter(|(key, _)| fields.contains(key.as_str()))
                    .map(|(key, value)| (key.clone(), value.clone()))
                    .collect::<Map<_, _>>()
            })
        })
        .collect::<Result<Vec<_>>>()?;
    let mut anchors = Map::new();
    for key in ["tube_anchors", "cap_tube_anchors", "body_anchors"] {
        anchors.insert(
            key.to_owned(),
            metadata
                .get(key)
                .or_else(|| metadata.get("anchors").and_then(|v| v.get(key)))
                .cloned()
                .unwrap_or_else(|| json!([])),
        );
    }
    let mut bb = metadata.get("box").cloned().unwrap_or(Value::Null);
    if bb.get("box_fields").is_some() {
        bb["bounds"] = json!([]);
    }
    let mut result = plain(
        &json!({"schema":1,"taken":request["taken"],"sources":request["sources"],"solids":metadata.get("solids").cloned().unwrap_or_else(||json!([])),
        "core":metadata.get("core_body_names").cloned().unwrap_or_else(||json!([])),"runs":runs,"frames":frames,"anchors":anchors,
        "card":request["checked"]["scorecard"],"drain":request["checked"]["drain"]}),
    )?;
    result["box"] = bb;
    Ok(result)
}

pub fn trays(request: &Value) -> Result<Value> {
    let bounds = object(&request["bounds"])?;
    let excluded: BTreeSet<&str> = array(&request["excluded_valves"])?
        .iter()
        .filter_map(Value::as_str)
        .collect();
    let mut groups: Vec<(usize, f64, f64, Vec<(String, [f64; 3])>)> = Vec::new();
    for (name, bb) in bounds {
        if !name.starts_with("valve-v-") || excluded.contains(name.as_str()) {
            continue;
        }
        let bb = array(bb)?;
        let coil = array(get(
            &request["bounds"],
            &name.replacen("valve-", "coil-", 1),
        )?)?;
        let delta = (0..3)
            .map(|i| {
                Ok((number(&coil[i])? + number(&coil[i + 3])?
                    - number(&bb[i])?
                    - number(&bb[i + 3])?)
                    / 2.)
            })
            .collect::<Result<Vec<_>>>()?;
        let axis = (0..3)
            .max_by(|a, b| {
                delta[*a]
                    .abs()
                    .total_cmp(&delta[*b].abs())
                    .then_with(|| b.cmp(a))
            })
            .unwrap();
        let sign = if delta[axis] > 0. { 1. } else { -1. };
        let plane = rounded(number(&bb[if sign > 0. { axis } else { axis + 3 }])?, 6);
        let center =
            std::array::from_fn(|i| (number(&bb[i]).unwrap() + number(&bb[i + 3]).unwrap()) / 2.);
        if let Some(row) = groups
            .iter_mut()
            .find(|row| row.0 == axis && row.1 == sign && row.2 == plane)
        {
            row.3.push((name.clone(), center));
        } else {
            groups.push((axis, sign, plane, vec![(name.clone(), center)]));
        }
    }
    groups.sort_by(|a, b| {
        a.0.cmp(&b.0)
            .then_with(|| a.1.total_cmp(&b.1))
            .then_with(|| a.2.total_cmp(&b.2))
    });
    let (x0, x1) = (
        number(&request["interior_x"][0])?,
        number(&request["interior_x"][1])?,
    );
    let mut plans = Map::new();
    let mut stations = Vec::new();
    for (axis, sign, plane, mut members) in groups {
        members.sort_by(|a, b| a.0.cmp(&b.0));
        let across = if axis != 0 { 0 } else { 1 };
        let along = (0..3).find(|i| *i != axis && *i != across).unwrap();
        let side = match (axis, sign > 0.) {
            (0, true) => "west",
            (0, false) => "east",
            (1, true) => "fore",
            (1, false) => "aft",
            (2, true) => "bottom",
            _ => "top",
        };
        let mut name = format!("valve-tray-{side}");
        if plans.contains_key(&name) {
            name += &format!("-{plane:.0}");
        }
        let middle = (members
            .iter()
            .map(|row| row.1[along])
            .reduce(f64::min)
            .unwrap()
            + members
                .iter()
                .map(|row| row.1[along])
                .reduce(f64::max)
                .unwrap())
            / 2.;
        plans.insert(
            name,
            json!([
                x1 - x0,
                members
                    .iter()
                    .map(|row| [
                        rounded(row.1[across] - (x0 + x1) / 2., 6),
                        rounded(row.1[along] - middle, 6)
                    ])
                    .collect::<Vec<_>>()
            ]),
        );
        stations.push(json!([
            plane,
            sign,
            members
                .iter()
                .map(|row| [rounded(row.1[across], 6), rounded(row.1[along], 6)])
                .collect::<Vec<_>>()
        ]));
    }
    let mut pumps = Map::new();
    for (name, head) in bounds {
        if !name.starts_with("pump-") || !name.ends_with("-head") {
            continue;
        }
        let head = array(head)?;
        let can = array(get(&request["bounds"], &name.replace("-head", "-motor"))?)?;
        let delta = (0..3)
            .map(|i| {
                (number(&can[i]).unwrap() + number(&can[i + 3]).unwrap()
                    - number(&head[i]).unwrap()
                    - number(&head[i + 3]).unwrap())
                    / 2.
            })
            .collect::<Vec<_>>();
        let axis = (0..3)
            .max_by(|a, b| {
                delta[*a]
                    .abs()
                    .total_cmp(&delta[*b].abs())
                    .then_with(|| b.cmp(a))
            })
            .unwrap();
        let sign = if delta[axis] > 0. { 1. } else { -1. };
        let mut center: [f64; 3] =
            std::array::from_fn(|i| (number(&can[i]).unwrap() + number(&can[i + 3]).unwrap()) / 2.);
        center[axis] = number(&head[if sign > 0. { axis + 3 } else { axis }])?;
        if axis == 2 && sign == 1. {
            center[1] -= number(&request["rear_axis_y_shift"])?;
            center[2] += number(&request["pump_seated_drop"])?;
        }
        pumps.insert(
            name.clone(),
            json!(rounded(
                rounded(center[1], 6) - number(&request["pump_relief_floor"])?,
                6
            )),
        );
    }
    Ok(json!([plans, stations, pumps]))
}

pub fn facts(request: &Value) -> Result<Value> {
    let spec = &request["spec"];
    let metadata = &spec["metadata"];
    let raw_box = &metadata["box"];
    let mut bb = plain(if raw_box.get("box_fields").is_some() {
        &raw_box["box"]
    } else {
        raw_box
    })?;
    let mut pack = bb
        .as_object_mut()
        .context("fact box")?
        .remove("pack")
        .context("fact box has no pack")?;
    if let Some(extra) = metadata.get("pack") {
        object(&plain(extra)?)?.iter().for_each(|(key, value)| {
            pack[key] = value.clone();
        });
    }
    let mut projected = Map::new();
    for name in array(&request["box_fact_order"])? {
        let name = text(name)?;
        projected.insert(
            name.to_owned(),
            plain(
                bb.get(name)
                    .or_else(|| pack.get(name))
                    .with_context(|| format!("box has no fact field {name}"))?,
            )?,
        );
    }
    let bounds = bounds(spec)?;
    let mut tray_input = request["tray_inputs"].clone();
    tray_input["bounds"] = bounds.clone();
    let tray = trays(&tray_input)?;
    let mut wet = Map::new();
    for row in array(&request["wet_ports"])? {
        wet.insert(
            text(&row["name"])?.to_owned(),
            json!([
                "round",
                row["center_x_mm"],
                row["center_z_mm"],
                row["bore_diameter_mm"]
            ]),
        );
    }
    let mut port_rows = Map::new();
    for name in array(&request["card_port_bodies"])? {
        let name = text(name)?;
        port_rows.insert(name.to_owned(), ports(get(&metadata["frames"], name)?)?);
    }
    let mut mouths = Map::new();
    for (name, rows) in &port_rows {
        if name.starts_with("bulkhead-") && name != "bulkhead-water-nut" {
            let key = if rows.get("inboard").is_some() {
                "inboard"
            } else {
                "tube-in"
            };
            mouths.insert(name.clone(), rows[key]["pos"].clone());
        }
    }
    let mut constants = request["constants"].clone();
    let gap = number(&constants["PORT_NUT_GAP"])?;
    let slip = number(&request["fit_slip"])?;
    let pitch = (number(&request["union_panel_footprint"])? + gap + 7.5)
        .max(number(&request["bulkhead_ring_union_od"])? + 2. * slip + 3.);
    let west = number(&request["tray_inputs"]["interior_x"][0])?
        + number(&constants["side_band_inset"])?
        + 1.
        + number(&request["union_body_d"])? / 2.;
    constants["PANEL_X"] =
        json!({"bulkhead-flavor-b":west,"bulkhead-flavor-a":west+pitch,"bulkhead-carb":west+pitch});
    if let Some(extra) = metadata.get("constants").and_then(Value::as_object) {
        for (key, value) in extra {
            constants[key] = value.clone();
        }
    }
    let routes = route_rows(metadata)?;
    let mut pieces = Map::new();
    for name in [
        "front-bottom",
        "front-top",
        "back-bottom",
        "back-top",
        "pump-retainer",
    ] {
        let installed = format!("enclosure-{name}");
        if bounds.get(&installed).is_none() {
            continue;
        }
        let row = metadata
            .get("piece_bounds")
            .and_then(|rows| rows.get(name))
            .unwrap_or(&bounds[&installed]);
        if name == "pump-retainer" {
            ensure!(
                metadata["piece_bounds"].get(name).is_some(),
                "pump retainer source bounds absent"
            );
        }
        let grid = 2.0_f64.powi(-30);
        pieces.insert(name.to_owned(),json!({"box":array(row)?.iter().map(|v|number(v).map(|v|(v/grid).round_ties_even()*grid)).collect::<Result<Vec<_>>>()?}));
    }
    let mut carried = Map::new();
    if let Some(frame) = metadata["frames"].get("digiten-flow") {
        carried.insert("digiten-flow.wire_exit".to_owned(),json!({"pos":point(&frame["transform"],vec3(&request["digiten_wire_exit"][0])?)?,"axis":direction(&frame["transform"],vec3(&request["digiten_wire_exit"][1])?)?}));
    }
    let standalone: BTreeSet<&str> = array(&request["standalone_names"])?
        .iter()
        .filter_map(Value::as_str)
        .collect();
    let manifold = if let Some(manifold) = metadata.get("fact_manifold_names") {
        let mut names = array(manifold)?
            .iter()
            .map(|v| text(v).map(str::to_owned))
            .collect::<Result<Vec<_>>>()?;
        names.sort();
        names
    } else {
        let routed: BTreeSet<String> = if let Some(rows) = metadata.get("routed_body_names") {
            array(rows)?
                .iter()
                .map(|v| text(v).map(str::to_owned))
                .collect::<Result<_>>()?
        } else {
            rows_or_empty(metadata, "runs")
                .iter()
                .filter(|row| row["kind"] == "refrigerant")
                .map(|row| format!("tube-{}", row["id"].as_str().unwrap()))
                .collect()
        };
        object(&bounds)?
            .keys()
            .filter(|name| {
                !standalone.contains(name.as_str())
                    && !name.starts_with("enclosure-")
                    && !name.starts_with("anchor-cap-")
                    && !routed.contains(name.as_str())
            })
            .cloned()
            .collect::<Vec<_>>()
    };
    let center = vec![number(&pack["funnel"][0])?, number(&pack["funnel"][1])?];
    let width = number(&request["funnel_collar"][0])?;
    let depth = number(&request["funnel_collar"][1])?;
    let mut placed = if let Some(placements) = pack["placed"].as_object() {
        placements.keys().cloned().collect::<Vec<_>>()
    } else {
        array(&pack["placed"])?
            .iter()
            .map(|v| text(v).map(str::to_owned))
            .collect::<Result<Vec<_>>>()?
    };
    placed.sort();
    let cap = point(
        &metadata["core_carry"],
        [0., 0., number(&request["foam_cap_face_z"])?],
    )?[2];
    Ok(
        json!({"schema":2,"card":request["card_digest"],"step":request["step_digest"],"box":projected,"constants":constants,
        "hopper_hole":[center[0]-width/2.,center[0]+width/2.,center[1]-depth/2.,center[1]+depth/2.],"manifold_bodies":manifold,
        "valve_trays":tray[0],"valve_tray_stations":tray[1],"pump_trays":tray[2],"pack":{"placed":placed,"body_anchors":metadata.get("body_anchors").cloned().unwrap_or_else(||json!([])),"tube_anchors":metadata.get("tube_anchors").cloned().unwrap_or_else(||json!([]))},
        "bodies":bounds,"mouths":mouths,"card_ports":port_rows,"run_near":{},"runs":routes[0],"native_runs":routes[1],
        "tube_export":{"schema":1,"step":request["artifacts"]["step"],"fine_model":request["artifacts"]["fine_model"],"scene":request["artifacts"]["scene"],"routing":request["routing"]},
        "wall_ports":{"union":[wet["bulkhead-water"],wet["bulkhead-carb"],wet["bulkhead-flavor-a"],wet["bulkhead-flavor-b"]],"co2":wet["co2-inlet"],"drain":wet["bulkhead-drain"]},
        "pieces":pieces,"faces":{"foam-assembly.cap":rounded(cap,4)},"carried_points":carried,"gaps":{}}),
    )
}
