use super::*;
const UNIONS: [&str; 4] = [
    "bulkhead-carb",
    "bulkhead-flavor-a",
    "bulkhead-flavor-b",
    "bulkhead-water",
];
const RINGS: [&str; 5] = [
    "bulkhead-ring-carb",
    "bulkhead-ring-co2",
    "bulkhead-ring-flavor-a",
    "bulkhead-ring-flavor-b",
    "bulkhead-ring-water",
];
const CABINET_CLEAR_H: f64 = 755.7;
const TURN_IN_LEAD_BEND: f64 = 38.5 + 25.0;
const TOL: f64 = 0.01;

fn agreed(what: &str, readings: &Value) -> Result<f64> {
    let readings = readings.as_object().context("installed-body readings")?;
    let mut lo = f64::INFINITY;
    let mut hi = f64::NEG_INFINITY;
    for value in readings.values() {
        let value = value.as_f64().context("body reading")?;
        lo = lo.min(value);
        hi = hi.max(value);
    }
    ensure!(!readings.is_empty(), "no {what} readings");
    if hi - lo > TOL {
        let spread = readings
            .iter()
            .map(|(name, value)| {
                Ok(format!(
                    "{name} {}",
                    fmt(value.as_f64().context("body reading")?, ".4f")?
                ))
            })
            .collect::<Result<Vec<_>>>()?
            .join(", ");
        bail!(
            "  the {what} no longer stand one figure off the face they are read from:\n    {spread}\n  install-envelope.md states one number for all of them. Say which, or say why they differ, before this page tells a customer either."
        );
    }
    Ok(hi)
}
fn install_envelope(request: &Request) -> Result<Output> {
    let input = &request.input;
    if request.operation == "settings" {
        return Ok(Output {
            exports: BTreeMap::from([
                ("CABINET_CLEAR_H".into(), json!(CABINET_CLEAR_H)),
                ("TURN_IN_LEAD_BEND".into(), json!(TURN_IN_LEAD_BEND)),
                ("TOL".into(), json!(TOL)),
                ("UNIONS".into(), json!(UNIONS)),
                ("BULKHEAD_RINGS".into(), json!(RINGS)),
            ]),
            ..Output::default()
        });
    }
    if request.operation == "agreed" {
        let value = agreed(
            input["what"].as_str().context("reading description")?,
            &input["readings"],
        )?;
        return Ok(Output {
            exports: BTreeMap::from([("value".into(), json!(value))]),
            ..Output::default()
        });
    }
    let rear = n(input, "rear")?;
    let bounds = input["bounds"]
        .as_object()
        .context("installed body bounds")?;
    let ymax = |name: &str| {
        bounds
            .get(name)
            .and_then(|v| v.get(4))
            .and_then(Value::as_f64)
            .with_context(|| format!("installed body {name} ymax"))
    };
    let ymin = |name: &str| {
        bounds
            .get(name)
            .and_then(|v| v.get(1))
            .and_then(Value::as_f64)
            .with_context(|| format!("installed body {name} ymin"))
    };
    let collet = UNIONS
        .iter()
        .map(|name| Ok(ymax(name)? - rear))
        .collect::<Result<Vec<f64>>>()?
        .into_iter()
        .fold(f64::NEG_INFINITY, f64::max);
    let ring_readings = RINGS
        .iter()
        .map(|name| Ok(((*name).into(), json!(ymax(name)? - ymin(name)?))))
        .collect::<Result<serde_json::Map<String, Value>>>()?;
    let recess_readings = RINGS
        .iter()
        .map(|name| Ok(((*name).into(), json!(rear - ymax(name)?))))
        .collect::<Result<serde_json::Map<String, Value>>>()?;
    let ring = agreed("wall's bulkhead rings", &Value::Object(ring_readings))?;
    let recess = agreed(
        "identification tile insets",
        &Value::Object(recess_readings),
    )?;
    let variables = BTreeMap::from([
        (
            "CABINET_CLEAR_H".into(),
            fmt(CABINET_CLEAR_H, ".4g")? + " mm",
        ),
        ("COLLET_PROUD".into(), fmt(collet, "g")? + " mm"),
        ("BULKHEAD_RING_THICK".into(), fmt(ring, "g")? + " mm"),
        ("BULKHEAD_RING_RECESS".into(), fmt(recess, "g")? + " mm"),
        (
            "TURN_IN".into(),
            fmt(TURN_IN_LEAD_BEND + collet, "g")? + " mm",
        ),
    ]);
    let mut output = Output::document("marketing/install-envelope.md", variables);
    output.exports = BTreeMap::from([
        ("CABINET_CLEAR_H".into(), json!(CABINET_CLEAR_H)),
        ("TURN_IN_LEAD_BEND".into(), json!(TURN_IN_LEAD_BEND)),
        ("TOL".into(), json!(TOL)),
        ("UNIONS".into(), json!(UNIONS)),
        ("BULKHEAD_RINGS".into(), json!(RINGS)),
        ("behind_the_rear_face".into(), json!([collet, ring, recess])),
    ]);
    output.stdout = "-> marketing/install-envelope.md\n".into();
    Ok(output)
}
const WANTED: [(&str, &str); 7] = [
    ("BOM_GRAND", "bom"),
    ("LAB_HM", "labor"),
    ("LAB_USD", "labor"),
    ("LABOR_RATE", "labor"),
    ("MT_H_PRINT", "machine-time"),
    ("MT_UNITS_YEAR", "machine-time"),
    ("MT_DUTY", "machine-time"),
];
fn figures(root: &Path, stem: &str) -> Result<Variables> {
    let name = format!("hardware/ledger/{stem}.figures.json");
    let text=std::fs::read_to_string(root.join(&name)).with_context(||format!("{name} is not there; target-market.md takes its figures from the ledgers; run that ledger's driver first"))?;
    let held: Value = serde_json::from_str(&text)?;
    let mut out = Variables::new();
    for driver in held.as_object().context("ledger figures")?.values() {
        for (name, value) in driver.as_object().context("ledger driver figures")? {
            out.insert(
                name.clone(),
                value.as_str().context("ledger figure text")?.to_owned(),
            );
        }
    }
    Ok(out)
}
fn target_market(request: &Request) -> Result<Output> {
    if request.operation == "settings" {
        return Ok(Output {
            exports: BTreeMap::from([(
                "WANTED".into(),
                json!(WANTED.into_iter().collect::<BTreeMap<_, _>>()),
            )]),
            ..Output::default()
        });
    }
    if request.operation == "figures" {
        let stem = request.input["stem"].as_str().context("ledger stem")?;
        return Ok(Output {
            exports: BTreeMap::from([("figures".into(), json!(figures(&request.root, stem)?))]),
            data_reads: vec![format!("hardware/ledger/{stem}.figures.json")],
            ..Output::default()
        });
    }
    let mut read = BTreeMap::new();
    for (_, stem) in WANTED {
        if !read.contains_key(stem) {
            read.insert(stem, figures(&request.root, stem)?);
        }
    }
    let mut variables = Variables::new();
    for (name, stem) in WANTED {
        let value=read[stem].get(name).with_context(||format!("{stem}.figures.json no longer holds {name}, which target-market.md states. Either that ledger stopped deriving it, or the page is asking for a figure nothing counts. Say which before this page tells a buyer either."))?;
        variables.insert(name.into(), value.clone());
    }
    let price = |name: &str| -> Result<f64> {
        Ok(variables[name]
            .trim_start_matches('$')
            .replace(',', "")
            .parse()?)
    };
    variables.insert(
        "UNIT_COST".into(),
        "$".to_owned() + &fmt(round(price("BOM_GRAND")? + price("LAB_USD")?, -2), ",.0f")?,
    );
    let mut output = Output::document("marketing/target-market.md", variables);
    output.exports.insert(
        "WANTED".into(),
        json!(WANTED.into_iter().collect::<BTreeMap<_, _>>()),
    );
    output.data_reads = read
        .keys()
        .map(|stem| format!("hardware/ledger/{stem}.figures.json"))
        .collect();
    output.stdout = "-> marketing/target-market.md\n".into();
    Ok(output)
}
pub fn run(request: &Request) -> Result<Output> {
    match request.driver.as_str() {
        "install-envelope" => install_envelope(request),
        "target-market" => target_market(request),
        _ => bail!("unknown marketing document"),
    }
}
