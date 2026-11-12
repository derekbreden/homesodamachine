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

/// Why the tubes `names` could not be laid out, where the request says.
fn reasons(metadata: &Value, names: &[Value]) -> Option<String> {
    let said: Vec<&str> = rows_or_empty(metadata, "unrouted")
        .into_iter()
        .filter(|tube| names.contains(&tube["name"]))
        .filter_map(|tube| tube["reason"].as_str())
        .collect();
    (!said.is_empty()).then(|| said.join("; "))
}

/// The machine's runs, then its tubes as drawn. A connection is incomplete when a tube or a
/// fitting it names is not in the machine, and so is a tube the request lists as one that could
/// not be laid out.
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
        let why = reasons(metadata, &missing);
        let mut row = json!({"id":name,"frm":group["from"],"to":group["to"],"length":if complete {json!(length)} else {Value::Null},
            "corners":rows.iter().map(|row|row["corners"].as_u64().unwrap()).sum::<u64>(),"bend":bend,
            "diam":rows.iter().filter_map(|row|row["diam"].as_f64()).reduce(f64::max).unwrap_or(0.),"made":group["made"],
            "native_routes":route_names,"fittings":fittings,"status":if complete {"complete"} else {"incomplete"},
            "missing_native_routes":missing,"missing_fittings":missing_fittings});
        if let Some(why) = why {
            row["why"] = json!(why);
        }
        runs.push(row);
    }
    for name in &route_order {
        if !grouped.contains(name.as_str()) {
            let mut row = native[name].clone();
            row["status"] = json!("complete");
            runs.push(row);
        }
    }
    // A tube that could not be laid out and that no connection names is its own incomplete run.
    for tube in rows_or_empty(metadata, "unrouted") {
        let name = text(&tube["name"])?;
        if grouped.contains(name) || native.contains_key(name) || runs.iter().any(|row| row["id"] == name) {
            continue;
        }
        runs.push(json!({"id":name,"frm":tube["from"],"to":tube["to"],"length":Value::Null,"corners":0,
            "bend":0.,"diam":0.,"made":"drawn","status":"incomplete",
            "missing_native_routes":[name],"missing_fittings":[],"why":tube["reason"]}));
    }
    Ok(json!([
        runs,
        route_order
            .iter()
            .map(|name| native[name].clone())
            .collect::<Vec<_>>()
    ]))
}

/// The fields the BOM, the fluid diagrams and the install guide read: the Box fields named in
/// `box_fact_order`, the placed bodies and their bounds, the card ports, the drawn runs and the
/// constants the request carries.
pub fn facts(request: &Value) -> Result<Value> {
    const RUN_FIELDS: [&str; 10] = [
        "id",
        "frm",
        "to",
        "made",
        "length",
        "corners",
        "status",
        "missing_native_routes",
        "missing_fittings",
        "why",
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

#[cfg(test)]
mod tests {
    use super::*;

    /// A connection whose tube could not be laid out is incomplete and says why, and a left-out
    /// tube that no connection names is an incomplete run of its own.
    #[test]
    fn a_tube_left_out_marks_its_run_incomplete() {
        let metadata = json!({
            "native_route_specs": {}, "native_route_order": [], "route_lengths": {}, "runs": [],
            "raw_bounds": {},
            "native_connections": {"fluid-26": {"from": "foam-assembly.reservoir-b", "to": "valve-v-h.inlet",
                "made": "drawn", "native_routes": ["fluid-26"], "fittings": []}},
            "unrouted": [
                {"name": "fluid-26", "from": "foam-assembly.reservoir-b", "to": "valve-v-h.inlet",
                 "reason": "missing station valve-v-h.inlet"},
                {"name": "refrig-2", "from": "condenser+fan.refrig-outlet", "to": "foam-assembly.evap-inlet",
                 "reason": "its sweep: tube path has no finite span"},
            ],
        });
        let rows = route_rows(&metadata).unwrap();
        let runs = rows[0].as_array().unwrap();
        assert_eq!(runs.len(), 2);
        assert_eq!(runs[0]["id"], "fluid-26");
        assert_eq!(runs[0]["status"], "incomplete");
        assert_eq!(runs[0]["missing_native_routes"], json!(["fluid-26"]));
        assert_eq!(runs[0]["why"], "missing station valve-v-h.inlet");
        assert_eq!(runs[1]["id"], "refrig-2");
        assert_eq!(runs[1]["frm"], "condenser+fan.refrig-outlet");
        assert_eq!(runs[1]["status"], "incomplete");
        assert_eq!(runs[1]["missing_native_routes"], json!(["refrig-2"]));

        // With nothing left out, the connection whose tube is in the machine is complete and
        // carries no reason.
        let whole = json!({
            "native_route_specs": {"fluid-26": {"owners": ["foam-assembly", "valve-v-h"], "segments": [], "od_mm": 6.35}},
            "native_route_order": ["fluid-26"], "route_lengths": {"fluid-26": 248.}, "runs": [], "raw_bounds": {},
            "native_connections": metadata["native_connections"],
        });
        let rows = route_rows(&whole).unwrap();
        let runs = rows[0].as_array().unwrap();
        assert_eq!(runs.len(), 1);
        assert_eq!(runs[0]["status"], "complete");
        assert!(runs[0].get("why").is_none());
    }
}
