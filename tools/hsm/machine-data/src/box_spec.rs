//! Placement-description structure and numeric comparison, independent of Python records.
use anyhow::{Context, Result, bail, ensure};
use serde_json::{Value, json};
use std::collections::BTreeSet;

const SCHEMA: u64 = 5;
const RECORD: &str = "__hsm_namedtuple__";
const LIST: &str = "__hsm_list__";
const DICT: &str = "__hsm_dict__";

fn keys(value: &Value) -> Result<BTreeSet<&str>> {
    Ok(value
        .as_object()
        .context("enclosure-box object")?
        .keys()
        .map(String::as_str)
        .collect())
}
fn strings(value: &Value) -> Result<Vec<&str>> {
    value
        .as_array()
        .context("enclosure-box fields must be an array")?
        .iter()
        .map(|v| v.as_str().context("enclosure-box field must be a string"))
        .collect()
}
fn tagged(value: &Value, types: &Value) -> Result<()> {
    match value {
        Value::Array(rows) => {
            for row in rows {
                tagged(row, types)?;
            }
        }
        Value::Object(row) => {
            if let Some(name) = row.get(RECORD) {
                ensure!(
                    keys(value)? == BTreeSet::from([RECORD, "fields", "values"]),
                    "enclosure-box has a malformed tagged record"
                );
                let name = name
                    .as_str()
                    .context("enclosure-box record type is not a string")?;
                let fields = types
                    .get(name)
                    .with_context(|| format!("enclosure-box names unknown record type {name:?}"))?;
                ensure!(
                    value["fields"].is_array() && value["values"].is_array(),
                    "enclosure-box {name} fields and values must be arrays"
                );
                ensure!(
                    value["fields"] == *fields,
                    "enclosure-box {name} fields {:?}, expected {fields:?}",
                    value["fields"]
                );
                let values = value["values"].as_array().unwrap();
                ensure!(
                    values.len() == fields.as_array().context("record fields")?.len(),
                    "enclosure-box {name} has {} values for {} fields",
                    values.len(),
                    fields.as_array().unwrap().len()
                );
                for item in values {
                    tagged(item, types)?;
                }
            } else if let Some(rows) = row.get(LIST) {
                ensure!(
                    keys(value)? == BTreeSet::from([LIST]) && rows.is_array(),
                    "enclosure-box has a malformed tagged list"
                );
                for item in rows.as_array().unwrap() {
                    tagged(item, types)?;
                }
            } else if let Some(rows) = row.get(DICT) {
                ensure!(
                    keys(value)? == BTreeSet::from([DICT]) && rows.is_array(),
                    "enclosure-box has a malformed tagged dictionary"
                );
                let mut names = BTreeSet::new();
                for (i, pair) in rows.as_array().unwrap().iter().enumerate() {
                    let pair = pair
                        .as_array()
                        .filter(|pair| pair.len() == 2 && pair[0].is_string())
                        .with_context(|| {
                            format!("enclosure-box dictionary pair {i} is malformed")
                        })?;
                    let name = pair[0].as_str().unwrap();
                    ensure!(
                        names.insert(name),
                        "enclosure-box dictionary repeats key {name:?}"
                    );
                    tagged(&pair[1], types)?;
                }
            } else {
                if let Some(types) = types.as_object() {
                    let held = keys(value)?;
                    for (name, fields) in types {
                        if strings(fields)?
                            .into_iter()
                            .all(|field| held.contains(field))
                        {
                            bail!("enclosure-box carries untagged {name} fields");
                        }
                    }
                }
                bail!("enclosure-box carries an untagged dictionary");
            }
        }
        _ => {}
    }
    Ok(())
}

pub fn validate(request: &Value) -> Result<Value> {
    let value = if let Some(path) = request.get("path").and_then(Value::as_str) {
        serde_json::from_slice(&std::fs::read(path).with_context(|| format!("reading {path}"))?)?
    } else {
        request["value"].clone()
    };
    let types = &request["types"];
    if request["mode"] == "value" {
        tagged(&value, types)?;
        return Ok(value);
    }
    ensure!(
        keys(&value)? == BTreeSet::from(["schema", "box_fields", "box", "bounds"]),
        "enclosure-box does not have the exact enclosure-box document shape"
    );
    ensure!(
        value["schema"].as_u64() == Some(SCHEMA),
        "enclosure-box schema {:?}, expected {SCHEMA}",
        value["schema"]
    );
    let fields = strings(&request["box_fields"])?;
    ensure!(
        value["box_fields"].is_array(),
        "enclosure-box box_fields is not an array"
    );
    ensure!(
        strings(&value["box_fields"])? == fields,
        "enclosure-box field list differs from this source"
    );
    ensure!(
        keys(&value["box"])? == fields.into_iter().collect(),
        "enclosure-box does not carry exactly one value for every Box field"
    );
    for row in value["box"].as_object().unwrap().values() {
        tagged(row, types)?;
    }
    let bounds = value["bounds"]
        .as_array()
        .context("enclosure-box bounds is not an array")?;
    if let Some(fields) = request.get("bound_fields").filter(|v| !v.is_null()) {
        let expected: BTreeSet<_> = strings(fields)?.into_iter().collect();
        for (i, row) in bounds.iter().enumerate() {
            ensure!(
                keys(row)? == expected,
                "enclosure-box bound {i} does not match its source fields"
            );
            for value in row.as_object().unwrap().values() {
                tagged(value, types)?;
            }
        }
    }
    Ok(value)
}

pub fn document(request: &Value) -> Result<Value> {
    let fields = strings(&request["box_fields"])?;
    ensure!(
        !fields.is_empty(),
        "the enclosure description is not a named tuple"
    );
    Ok(json!({"schema":SCHEMA,"box_fields":fields,"box":request["box"],"bounds":request["bounds"]}))
}

fn number(v: &Value) -> Option<f64> {
    if let Value::Bool(v) = v {
        Some(if *v { 1. } else { 0. })
    } else {
        v.as_f64()
    }
}
fn exact(left: &Value, right: &Value) -> bool {
    match (left, right) {
        (Value::Array(a), Value::Array(b)) => {
            a.len() == b.len() && a.iter().zip(b).all(|(a, b)| exact(a, b))
        }
        (Value::Object(a), Value::Object(b)) => {
            a.len() == b.len() && a.iter().all(|(k, a)| b.get(k).is_some_and(|b| exact(a, b)))
        }
        _ if number(left).is_some() && number(right).is_some() => number(left) == number(right),
        _ => left == right,
    }
}
pub fn same(left: &Value, right: &Value) -> bool {
    if exact(left, right) {
        return true;
    }
    match (left, right) {
        (Value::Number(a), Value::Number(b)) if a.is_f64() && b.is_f64() => {
            (a.as_f64().unwrap() - b.as_f64().unwrap()).abs() <= 1e-6
        }
        (Value::Array(a), Value::Array(b)) => {
            a.len() == b.len() && a.iter().zip(b).all(|(a, b)| same(a, b))
        }
        (Value::Object(a), Value::Object(b)) => {
            a.len() == b.len() && a.iter().all(|(k, a)| b.get(k).is_some_and(|b| same(a, b)))
        }
        _ => false,
    }
}
