//! Assembly facts and scene documents from live scalar providers.
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
fn distance(a: [f64; 3], b: [f64; 3]) -> f64 {
    a.into_iter()
        .zip(b)
        .map(|(a, b)| (a - b) * (a - b))
        .sum::<f64>()
        .sqrt()
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

/// The fields the BOM, the fluid diagrams and the install guide read: the Box fields named in
/// `box_fact_order`, the placed bodies and their bounds, the card ports, the drawn runs and the
/// constants the request carries.
pub fn facts(request: &Value) -> Result<Value> {
    const RUN_FIELDS: [&str; 9] = [
        "id",
        "frm",
        "to",
        "made",
        "length",
        "corners",
        "status",
        "missing_native_routes",
        "missing_fittings",
    ];
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
    let mut port_rows = Map::new();
    for name in array(&request["card_port_bodies"])? {
        let name = text(name)?;
        port_rows.insert(name.to_owned(), ports(get(&metadata["frames"], name)?)?);
    }
    let mut constants = request["constants"].clone();
    if let Some(extra) = metadata.get("constants").and_then(Value::as_object) {
        for (key, value) in extra {
            if constants.get(key).is_some() {
                constants[key] = value.clone();
            }
        }
    }
    let routes = route_rows(metadata)?;
    let runs = array(&routes[0])?
        .iter()
        .map(|row| {
            Ok(Value::Object(
                object(row)?
                    .iter()
                    .filter(|(key, _)| RUN_FIELDS.contains(&key.as_str()))
                    .map(|(key, value)| (key.clone(), value.clone()))
                    .collect(),
            ))
        })
        .collect::<Result<Vec<_>>>()?;
    let mut placed = if let Some(placements) = pack["placed"].as_object() {
        placements.keys().cloned().collect::<Vec<_>>()
    } else {
        array(&pack["placed"])?
            .iter()
            .map(|v| text(v).map(str::to_owned))
            .collect::<Result<Vec<_>>>()?
    };
    placed.sort();
    Ok(json!({"box":projected,"constants":constants,"pack":{"placed":placed},
        "bodies":bounds(spec)?,"card_ports":port_rows,"runs":runs}))
}

/// The fastening rows the scene GLBs place bodies by, made without the checks: the fastening
/// table's rows for the bodies the physical model holds, then a `pack` row for each body the
/// table does not name. The bodies are the model's components by their alias or base name, and
/// the casing, read as `machine-checks` reads its population: no wires, no cold-core internals,
/// no printed pieces and no tubes.
pub fn scene_mounts(request: &Value) -> Result<Value> {
    fn base(name: &str) -> &str {
        match name.rsplit_once('/') {
            Some((head, tail)) if !tail.is_empty() && tail.chars().all(|c| c.is_ascii_digit()) => {
                head
            }
            _ => name,
        }
    }
    fn last(name: &str) -> &str {
        name.rsplit('/').next().unwrap_or(name)
    }
    let names = |key: &str| -> Result<BTreeSet<String>> {
        rows_or_empty(request, key)
            .iter()
            .map(|v| text(v).map(str::to_owned))
            .collect()
    };
    let core = names("core_body_names")?;
    let external = names("core_external_names")?;
    let aliases = request["aliases"].as_object().cloned().unwrap_or_default();
    let mut have = BTreeSet::from(["foam-assembly".to_owned()]);
    for row in array(&request["identity"])? {
        let name = base(text(&row[0])?);
        have.insert(aliases.get(name).and_then(Value::as_str).unwrap_or(name).to_owned());
    }
    have.retain(|n| {
        !(n.starts_with("wire-") || last(n).starts_with("wire-"))
            && !(core.contains(n) && !external.contains(last(n)))
            && !(n.starts_with("cold-core/") && !external.contains(last(n)))
            && !n.starts_with("enclosure-")
            && !["tube-", "turn-", "step-", "stub-"].iter().any(|p| n.starts_with(p))
    });
    let mut rows = Vec::new();
    for row in array(&request["mounts"])?.iter().chain(array(&request["selected"])?) {
        if have.contains(text(&row[0])?) {
            rows.push(row.clone());
        }
    }
    let typed = rows
        .iter()
        .map(|r| text(&r[0]).map(str::to_owned))
        .collect::<Result<BTreeSet<_>>>()?;
    for name in have.difference(&typed) {
        rows.push(json!([name, null, "pack"]));
    }
    Ok(json!(rows))
}
