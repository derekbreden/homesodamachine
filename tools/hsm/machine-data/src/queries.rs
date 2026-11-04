//! Ordered selection planning and scalar aggregation for fine-model questions.
use anyhow::{Context, Result, ensure};
use serde_json::{Map, Value, json};
use std::collections::{BTreeMap, BTreeSet};

fn rows(value: &Value) -> Result<&Vec<Value>> {
    value.as_array().context("fine query expects an array")
}
fn name(value: &Value) -> Result<&str> {
    value
        .as_str()
        .context("fine query expects a reference name")
}
fn object(value: &Value) -> Result<&Map<String, Value>> {
    value.as_object().context("fine query expects an object")
}
fn source(reference: &Value) -> Result<Value> {
    Ok(Value::Object(
        object(reference)?
            .iter()
            .filter(|(key, _)| key.as_str() != "indices")
            .map(|(key, value)| (key.clone(), value.clone()))
            .collect(),
    ))
}
fn indices(reference: &Value) -> Result<Vec<usize>> {
    rows(&reference["indices"])?
        .iter()
        .map(|v| v.as_u64().map(|v| v as usize).context("fine query index"))
        .collect()
}

pub fn groups(request: &Value) -> Result<Value> {
    let references = object(&request["references"])?;
    let queries = rows(&request["queries"])?;
    let mut used = Vec::new();
    let mut seen = BTreeSet::new();
    for query in queries {
        let mut names = vec![name(&query["a"])?, name(&query["b"])?];
        if let Some(stages) = query.get("fine_mask_stages") {
            for stage in rows(stages)? {
                for value in rows(&stage["references"])? {
                    names.push(name(value)?);
                }
            }
        }
        for name in names {
            if seen.insert(name) {
                used.push(name);
            }
        }
    }
    let mut sources: Vec<(String, Value, BTreeSet<usize>)> = Vec::new();
    for name in &used {
        let reference = references
            .get(*name)
            .with_context(|| format!("no fine reference {name}"))?;
        let source = source(reference)?;
        let key = serde_json::to_string(&source)?;
        if let Some(row) = sources.iter_mut().find(|row| row.0 == key) {
            row.2.extend(indices(reference)?);
        } else {
            sources.push((key, source, indices(reference)?.into_iter().collect()));
        }
    }
    let mut instances = Vec::new();
    let mut slots = BTreeMap::new();
    let mut offset = 0;
    for (key, source, selection) in sources {
        let mut instance = source;
        for index in &selection {
            slots.insert((key.clone(), *index), offset);
            offset += 1;
        }
        instance["indices"] = json!(selection);
        instances.push(instance);
    }
    let operand = |name: &str| -> Result<Value> {
        let reference = references
            .get(name)
            .with_context(|| format!("no fine reference {name}"))?;
        let key = serde_json::to_string(&source(reference)?)?;
        let indices = indices(reference)?
            .iter()
            .map(|index| {
                slots
                    .get(&(key.clone(), *index))
                    .copied()
                    .context("fine query slot missing")
            })
            .collect::<Result<Vec<_>>>()?;
        Ok(if indices.len() == 1 {
            json!(indices[0])
        } else {
            json!(indices)
        })
    };
    let mut numbered = Vec::new();
    for query in queries {
        let mut row = query.clone();
        row["a"] = operand(name(&query["a"])?)?;
        row["b"] = operand(name(&query["b"])?)?;
        if let Some(stages) = query.get("fine_mask_stages") {
            let mut numbered_stages = Vec::new();
            for stage in rows(stages)? {
                let mut mapped = Value::Object(
                    object(stage)?
                        .iter()
                        .filter(|(key, _)| key.as_str() != "references")
                        .map(|(key, value)| (key.clone(), value.clone()))
                        .collect(),
                );
                let mut indices = Vec::new();
                for reference in rows(&stage["references"])? {
                    let value = operand(name(reference)?)?;
                    if value.is_array() {
                        indices.extend(rows(&value)?.iter().cloned());
                    } else {
                        indices.push(value);
                    }
                }
                mapped["indices"] = json!(indices);
                numbered_stages.push(mapped);
            }
            row["fine_mask_stages"] = json!(numbered_stages);
        }
        numbered.push(row);
    }
    Ok(json!({"instances":instances,"queries":numbered}))
}

pub fn box_plan(request: &Value) -> Result<Value> {
    let requests = rows(&request["requests"])?;
    let mut selected = BTreeSet::new();
    for row in requests {
        let indices = indices(row)?;
        ensure!(!indices.is_empty(), "A box common needs a fine model entry");
        selected.extend(indices);
    }
    let selected = selected.into_iter().collect::<Vec<_>>();
    let slots = selected
        .iter()
        .enumerate()
        .map(|(i, index)| (*index, i))
        .collect::<BTreeMap<_, _>>();
    let mut queries = Vec::new();
    let mut owners = Vec::new();
    for (owner, row) in requests.iter().enumerate() {
        for index in indices(row)? {
            let mut query = json!({"kind":"common","a":slots[&index],"b_box":row["box"]});
            if row["positive_components"] == true {
                query["positive_components"] = json!(true);
            }
            queries.push(query);
            owners.push(owner);
        }
    }
    Ok(json!({"indices":selected,"queries":queries,"owners":owners}))
}

pub fn box_result(request: &Value) -> Result<Value> {
    let requests = rows(&request["requests"])?;
    let readings = rows(&request["readings"])?;
    let owners = rows(&request["owners"])?;
    ensure!(
        readings.len() == owners.len(),
        "Box common coverage differs from the requested entries"
    );
    let mut grouped = vec![Vec::new(); requests.len()];
    for (owner, row) in owners.iter().zip(readings) {
        ensure!(row.get("error").is_none(), "{}", row["error"]);
        grouped[owner.as_u64().context("box common owner")? as usize].push(&row["common"]["raw"]);
    }
    let mut out = Vec::new();
    for (request, readings) in requests.iter().zip(grouped) {
        let material = readings
            .iter()
            .filter(|row| !row["min"].is_null())
            .collect::<Vec<_>>();
        let mut raw = json!({"volume_mm3":readings.iter().map(|row|row["volume_mm3"].as_f64().context("common volume")).collect::<Result<Vec<_>>>()?.iter().sum::<f64>(),
            "min":if material.is_empty(){Value::Null}else{json!((0..3).map(|axis|material.iter().map(|row|row["min"][axis].as_f64().unwrap()).reduce(f64::min).unwrap()).collect::<Vec<_>>())},
            "max":if material.is_empty(){Value::Null}else{json!((0..3).map(|axis|material.iter().map(|row|row["max"][axis].as_f64().unwrap()).reduce(f64::max).unwrap()).collect::<Vec<_>>())}});
        if request["positive_components"] == true {
            let components = readings
                .iter()
                .map(|row| rows(&row["components"]))
                .collect::<Result<Vec<_>>>()?
                .into_iter()
                .flatten()
                .collect::<Vec<_>>();
            raw["components"] = json!(components);
        }
        out.push(json!({"indices":request["indices"],"box":request["box"],"raw":raw}));
    }
    Ok(json!(out))
}
