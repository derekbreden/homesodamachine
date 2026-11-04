//! Native value types for stored envelopes and printed holder declarations.
use super::*;

fn field(value: &Value, key: &str) -> Value {
    let record = value
        .get("$env")
        .or_else(|| value.get("$holder"))
        .or_else(|| value.get("$namespace"))
        .unwrap_or(value);
    if record.get("$dict").is_some() {
        ix(record.clone(), json!(key))
    } else {
        record
            .get(key)
            .unwrap_or_else(|| panic!("Unknown storage field {key}"))
            .clone()
    }
}
fn env(kind: &str, args: &[Value], kwargs: &Value) -> Result<Value> {
    let name = argument(args, kwargs, 0, "name");
    let x = argument(args, kwargs, 1, "x");
    let y = argument(args, kwargs, 2, "y");
    let z = argument(args, kwargs, 3, "z");
    let bound = argument(args, kwargs, 4, "bound");
    let source = argument(args, kwargs, 5, "source");
    let bounds = if tuple(&bound) {
        seq(bound.clone())
    } else {
        vec![bound.clone(); 3]
    };
    if bounds.len() != 3 || bounds.iter().any(|b| b != "exact" && b != "most") {
        bail!(
            "{}: bound {} is not exact or most",
            string(&name),
            string(&bound)
        )
    }
    for (axis, v) in [("x", &x), ("y", &y), ("z", &z)] {
        if n(v) <= 0.0 {
            bail!("{}: {axis} is {}", string(&name), string(v))
        }
    }
    Ok(
        json!({"$env":{"kind":kind,"name":name,"x":x,"y":y,"z":z,"bound":t(bounds),"source":source}}),
    )
}
fn holder(args: &[Value], kwargs: &Value) -> Result<Value> {
    let mut values = serde_json::Map::new();
    for (i, key) in ["name", "shape", "x_u", "y_u", "height_u"]
        .into_iter()
        .enumerate()
    {
        values.insert(key.into(), argument(args, kwargs, i, key));
    }
    let mut takes = args
        .get(5)
        .cloned()
        .or_else(|| kwarg(kwargs, "takes"))
        .unwrap_or_else(|| t(vec![]));
    let note = args
        .get(6)
        .cloned()
        .or_else(|| kwarg(kwargs, "note"))
        .unwrap_or(json!(""));
    let opts = args
        .get(7)
        .cloned()
        .or_else(|| kwarg(kwargs, "opts"))
        .unwrap_or_else(|| object(vec![]));
    if values["shape"] == "index" && !truth(&takes) {
        let mut contents = vec![];
        for row in seq(ix(opts.clone(), json!("rows"))) {
            for cell in seq(row) {
                let value = ix(cell, json!(0));
                if !contents.iter().any(|p| equal(p, &value)) {
                    contents.push(value)
                }
            }
        }
        takes = t(contents);
    }
    values.insert("takes".into(), takes);
    values.insert("note".into(), note);
    values.insert("opts".into(), opts);
    Ok(json!({"$holder":Value::Object(values)}))
}
pub(super) fn attribute(value: &Value, key: &str) -> Value {
    if value.get("$env").is_some() {
        match key {
            "thinnest" => j([
                n(&field(value, "x")),
                n(&field(value, "y")),
                n(&field(value, "z")),
            ]
            .into_iter()
            .reduce(f64::min)
            .unwrap()),
            "longest" => j([
                n(&field(value, "x")),
                n(&field(value, "y")),
                n(&field(value, "z")),
            ]
            .into_iter()
            .reduce(f64::max)
            .unwrap()),
            "volume" => b(
                "*",
                b("*", field(value, "x"), field(value, "y")),
                field(value, "z"),
            ),
            "exact_everywhere" => json!(seq(field(value, "bound")).iter().all(|b| b == "exact")),
            _ => field(value, key),
        }
    } else if value.get("$holder").is_some() && key == "cells" {
        let opts = field(value, "opts");
        let get = |key| kwarg(&opts, key).unwrap_or(json!(0));
        b(
            "*",
            b("+", get("length_div"), json!(1)),
            b("+", get("width_div"), json!(1)),
        )
    } else {
        field(value, key)
    }
}
pub(super) fn kind(value: &Value) -> Option<&str> {
    if let Some(record) = value.get("$env") {
        record["kind"].as_str()
    } else if value.get("$holder").is_some() {
        Some("Holder")
    } else {
        None
    }
}
pub(super) fn display(value: &Value) -> String {
    let bounds = seq(field(value, "bound"));
    let parts = ["x", "y", "z"]
        .into_iter()
        .zip(&bounds)
        .map(|(key, reading)| {
            format!(
                "{}{}",
                hsm_documents::format_number(n(&field(value, key)), ".1f").unwrap(),
                if reading == "exact" { "" } else { "-" }
            )
        })
        .collect::<Vec<_>>();
    parts.join(" x ")
        + " mm"
        + if truth(&attribute(value, "exact_everywhere")) {
            ""
        } else {
            "  (- is a parcel: no more than that)"
        }
}
pub(super) fn method(value: Value, name: &str, args: Vec<Value>) -> Result<Value> {
    match name {
        "reading" => {
            let axis = string(&args[0]);
            let i = "xyz"
                .find(&axis)
                .ok_or_else(|| anyhow::anyhow!("Unknown envelope axis {axis}"))?;
            Ok(ix(field(&value, "bound"), json!(i)))
        }
        "most" => Ok(field(&value, &string(&args[0]))),
        "least" | "size" => {
            let axis = string(&args[0]);
            if method(value.clone(), "reading", args.clone())? != "exact" {
                bail!(
                    "{}: {} is a parcel, so it says the thing is no bigger than {} mm in {axis} and nothing about how small it is. Geometry that needs a floor under {axis} wants an exact figure — a standard, or the maker's own drawing — or a holder that does not ask.",
                    string(&field(&value, "name")),
                    string(&field(&value, "source")),
                    hsm_documents::format_number(n(&field(&value, &axis)), ".1f")?
                );
            }
            Ok(field(&value, &axis))
        }
        "footprint" => Ok(t(vec![field(&value, "x"), field(&value, "y")])),
        "rotated" => env(
            "Env",
            &[
                field(&value, "name"),
                field(&value, "y"),
                field(&value, "x"),
                field(&value, "z"),
                field(&value, "bound"),
                field(&value, "source"),
            ],
            &json!({}),
        ),
        _ => bail!("Unknown envelope method {name}"),
    }
}
pub(super) fn assign(value: &mut Value, key: &str, item: Value) {
    let record = if value.get("$holder").is_some() {
        &mut value["$holder"]
    } else {
        &mut value["$env"]
    };
    record[key] = item;
}
pub(super) fn manual(
    cx: &mut Context,
    module: &str,
    name: &str,
    args: Vec<Value>,
    kwargs: Value,
) -> Result<Value> {
    match (module, name) {
        ("_bound", "Env") | ("_bound", "Heap") => env(name, &args, &kwargs),
        ("holders", "Holder") => holder(&args, &kwargs),
        ("_kit", "SimpleNamespace") => Ok(json!({"$namespace":kwargs})),
        ("_bound", "attribute") => Ok(attribute(
            &argument(&args, &kwargs, 0, "value"),
            argument(&args, &kwargs, 1, "name").as_str().unwrap(),
        )),
        ("_bound", "method") => {
            let value = argument(&args, &kwargs, 0, "value");
            let method = argument(&args, &kwargs, 1, "name");
            let rest = seq(argument(&args, &kwargs, 2, "args"));
            self::method(value, method.as_str().unwrap(), rest)
        }
        ("_bound", "display") => Ok(json!(display(&argument(&args, &kwargs, 0, "value")))),
        _ => bail!("Unknown storage function {module}.{name}"),
    }
}
