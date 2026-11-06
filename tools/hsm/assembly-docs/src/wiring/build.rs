use super::*;
fn counts(values: impl Iterator<Item = String>) -> Value {
    let mut out = BTreeMap::new();
    for value in values {
        *out.entry(value).or_insert(0usize) += 1;
    }
    json!(out)
}
pub fn manifest(
    at: &Value,
    graph: &Value,
    routes: &Value,
    terminations: &Value,
    bundles: &Value,
) -> Result<Value> {
    let graph_rows = rows(graph)?;
    let route_rows = rows(routes)?;
    let used = graph_rows
        .iter()
        .flat_map(|c| [c["start"].as_str().unwrap(), c["end"].as_str().unwrap()])
        .collect::<BTreeSet<_>>();
    let terminals = used
        .iter()
        .map(|id| ((*id).to_owned(), at["terminals"][*id].clone()))
        .collect::<BTreeMap<_, _>>();
    let constants = graph::request(&Request {
        op: "graph_constants".into(),
        data: Value::Null,
        root: PathBuf::new(),
    })?;
    Ok(
        json!({"schema":1,"units":"mm","frame":"Enclosure assembly XYZ; Z up","scope":"Installed enclosure wiring, including embedded core leads. External cord, faucet and umbilical end at the enclosure interfaces.","connection_count":graph_rows.len(),"harnesses":counts(graph_rows.iter().map(|c|c["harness"].as_str().unwrap().to_owned())),"route_status_counts":counts(route_rows.iter().map(|r|r["status"].as_str().unwrap().to_owned())),"stock":model::stock()?,"unused":constants["UNUSED"],"boundaries":constants["BOUNDARIES"],"interfaces":graph::interfaces(&at["terminals"],graph)?,"terminal_status_counts":counts(used.iter().map(|id|at["terminals"][*id]["status"].as_str().unwrap().to_owned())),"terminals":terminals,"reference_frames":at["frame_checks"],"cable_passages":at["passages"],"pcb_reference":at["pcb_reference"],"terminations":terminations,"bundles":bundles,"routes":route_rows.iter().map(model::record).collect::<Result<Vec<_>>>()?,"limits":serde_json::from_str::<Value>(include_str!("manifest-limits.json"))?}),
    )
}
pub fn numeric(root: &Path, at: &Value) -> Result<(Value, Value)> {
    let graph = graph::connections();
    let routes = routes::routed(root, &graph, at)?;
    let terminations = terminations::inputs(at, &graph)?;
    let bundles = bundles::Context::new(root, at)?.inputs()?;
    let mut components = rows(&terminations[0])?.clone();
    components.extend(rows(&bundles[0])?.clone());
    let records = rows(&routes)?
        .iter()
        .map(model::record)
        .collect::<Result<Vec<_>>>()?;
    let numbers = readers::wire_numbers(&json!(records), &model::stock()?, &json!(components))?;
    let manifest = manifest(at, &graph, &routes, &terminations[1], &bundles[1])?;
    Ok((numbers, manifest))
}
fn source_paths(root: &Path, numbers: &Value) -> Result<Vec<String>> {
    let mut paths = BTreeSet::new();
    for raw in rows(&provider(json!({"kind":"module_files"}))?)? {
        paths.insert(PathBuf::from(string(raw)?));
    }
    for path in [
        "hardware/manifold-layout/above-core.json",
        "hardware/manifold-layout/enclosure-box.json",
        "hardware/reference/g-ganen-pump/reference-parameters.json",
        "hardware/reference/g-ganen-pump/under-head-clearance.json",
        "hardware/reference/g-ganen-pump/underside-observation/rigid-underside.json",
    ] {
        paths.insert(root.join(path));
    }
    if let Some(components) = numbers.get("components") {
        for row in rows(components)? {
            if row["kind"] == "import" {
                paths.insert(root.join(string(&row["step"])?));
            }
        }
    }
    let mut output = BTreeSet::new();
    for path in paths {
        let path = path.canonicalize().unwrap_or(path);
        if let Ok(relative) = path.strip_prefix(root) {
            if path.is_file() {
                output.insert(relative.to_string_lossy().into_owned());
            }
        }
    }
    Ok(output.into_iter().collect())
}
fn csv_field(value: &Value) -> String {
    let text = if let Some(s) = value.as_str() {
        s.to_owned()
    } else if value.is_null() {
        String::new()
    } else {
        value.to_string()
    };
    if text.contains([',', '"', '\r', '\n']) {
        format!("\"{}\"", text.replace('"', "\"\""))
    } else {
        text
    }
}
pub fn write_manifest(
    root: &Path,
    mut manifest: Value,
    scene: &Path,
    output: &Path,
    additional: &Value,
    physical: Option<&str>,
) -> Result<Value> {
    let physical = if let Some(value) = physical {
        value.to_owned()
    } else {
        use sha2::{Digest, Sha256};
        format!(
            "{:x}",
            Sha256::digest(step::base_document(&std::fs::read_to_string(scene)?)?.as_bytes())
        )
    };
    manifest["physical_scene_sha256"] = json!(physical);
    let base: Vec<String> = serde_json::from_str(include_str!("manifest-sources.json"))?;
    let mut paths = Vec::new();
    let mut seen = BTreeSet::new();
    for path in base.into_iter().map(|p| root.join(p)).chain(
        rows(additional)?
            .iter()
            .map(|v| PathBuf::from(v.as_str().unwrap())),
    ) {
        if seen.insert(path.clone()) {
            paths.push(path);
        }
    }
    let mut source_sha = json!({});
    let mut source_code = json!({});
    for path in paths {
        let rel = path
            .strip_prefix(root)
            .with_context(|| format!("manifest source outside checkout: {}", path.display()))?
            .to_string_lossy()
            .into_owned();
        source_sha[&rel] = json!(readers::digest(&path)?);
        if path.extension().is_some_and(|e| e == "py") {
            source_code[&rel] = provider(json!({"kind":"code_digest","path":path}))?;
        }
    }
    manifest["source_sha256"] = source_sha;
    manifest["source_code_digest_algorithm"] = json!("_realized.code_digest");
    manifest["source_code_digest"] = source_code;
    std::fs::write(
        output.with_extension("json"),
        serde_json::to_string_pretty(&manifest)? + "\n",
    )?;
    let stock = model::stock()?;
    let mut csv = String::from(
        "wire_id,harness,net,from_terminal,to_terminal,awg,modeled_length_mm,route_status,start_status,end_status,service\n",
    );
    for row in rows(&manifest["routes"])? {
        let values = vec![
            row["id"].clone(),
            row["harness"].clone(),
            row["net"].clone(),
            row["start"].clone(),
            row["end"].clone(),
            stock[string(&row["stock"])?]["awg"].clone(),
            row["length_mm"].clone(),
            row["route_status"].clone(),
            manifest["terminals"][string(&row["start"])?]["status"].clone(),
            manifest["terminals"][string(&row["end"])?]["status"].clone(),
            row["service"].clone(),
        ];
        csv.push_str(&values.iter().map(csv_field).collect::<Vec<_>>().join(","));
        csv.push('\n');
    }
    std::fs::write(output.with_extension("csv"), csv)?;
    Ok(manifest)
}
fn new_attachments(root: &Path, scene: Value) -> Result<Value> {
    let mut raw = json!({});
    for (name, row) in scene.as_object().context("measured physical scene")? {
        raw[name] = row[0].clone();
    }
    let at = terminals::init(&raw)?;
    terminals::request(&Request {
        root: root.into(),
        op: "terminal_resolve".into(),
        data: json!({"state":at}),
    })
}
fn read_model(root: &Path, model: &Path, reading: &Value) -> Result<Value> {
    readers::request(&Request {
        root: root.into(),
        op: "model_read".into(),
        data: json!({"path":model,"reading":reading}),
    })
}
fn build_export(request: &Request, kernel: bool, numbers_only: bool) -> Result<Value> {
    let d = &request.data;
    let target = PathBuf::from(string(&d["target"])?);
    let model = d
        .get("model")
        .and_then(Value::as_str)
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(format!("{}.npz", target.display())));
    let scene = read_model(
        &request.root,
        &model,
        d.get("reading").unwrap_or(&Value::Null),
    )?;
    let at = new_attachments(&request.root, scene)?;
    let (mut numbers, mut manifest) = numeric(&request.root, &at)?;
    let output = if kernel {
        PathBuf::from(string(&d["output"])?).join("enclosure-wiring")
    } else {
        PathBuf::from(string(&d["output"])?)
    };
    let stem = output
        .file_name()
        .context("wiring output stem")?
        .to_string_lossy();
    let parent = output.parent().context("wiring output directory")?;
    std::fs::create_dir_all(parent)?;
    numbers["file_stem"] = json!(stem);
    let fine_digest = readers::digest(&model)?;
    numbers["physical_fine_model_sha256"] = json!(fine_digest);
    manifest["physical_fine_model_sha256"] = json!(fine_digest);
    let source_names = if kernel {
        source_paths(&request.root, &numbers)?
    } else {
        Vec::new()
    };
    if numbers_only {
        let data = json!({"numbers":numbers,"manifest":manifest,"sources":source_names});
        std::fs::write(
            Path::new(string(&d["numbers_output"])?),
            serde_json::to_string(&data)? + "\n",
        )?;
        return Ok(data);
    }
    provider(
        json!({"kind":"cut","crate":"machine","name":"installed-wires","numbers":numbers,"output":parent,"numbers_name":stem}),
    )?;
    let wire = PathBuf::from(format!("{}.step", output.display()));
    let wire_model = PathBuf::from(format!("{}.step.npz", output.display()));
    if !kernel {
        // The assembly build cuts and installs the wires and stops there: the resolved model
        // and the worksheet are written when the wiring is materialized by hand.
        let receipt = provider(
            json!({"kind":"append_wiring","host":target,"wire_step":wire,"wire_model":wire_model}),
        )?;
        return Ok(json!({"receipt":receipt}));
    }
    let receipt = step::install(
        &json!({"host":target,"wire_step":wire,"wire_model":wire_model,"verify_retained":boolean(d,"verify_retained",false)}),
    )?;
    manifest["wiring_fine_model_sha256"] = receipt["wiring_fine_model"]["sha256"].clone();
    manifest["wiring_numbers_sha256"] =
        json!(readers::digest(&output.with_extension("numbers.json"))?);
    let mut sources = source_names
        .iter()
        .map(|p| request.root.join(p))
        .collect::<Vec<_>>();
    for path in rows(&provider(json!({"kind":"compiled_sources"}))?)? {
        let path = request.root.join(string(path)?);
        if path.is_file() {
            sources.push(path);
        }
    }
    sources.insert(
        0,
        request
            .root
            .join("hardware/wiring/installed/wire_geometry.py"),
    );
    let additional = json!(sources);
    manifest = write_manifest(&request.root, manifest, &target, &output, &additional, None)?;
    let residual = manifest["reference_frames"]
        .as_object()
        .context("wiring reference frames")?
        .values()
        .filter_map(|r| r["maximum_extent_residual_mm"].as_f64())
        .fold(f64::NEG_INFINITY, f64::max);
    Ok(
        json!({"conductors":manifest["connection_count"],"harnesses":manifest["harnesses"].as_object().unwrap().len(),"terminal_status":manifest["terminal_status_counts"],"frame_max_residual_mm":residual}),
    )
}
pub fn request(request: &Request) -> Result<Value> {
    let d = &request.data;
    match request.op.as_str() {
        "build_wire_geometry" => {
            let data: Value = serde_json::from_str(&std::fs::read_to_string(Path::new(string(
                &d["manifest"],
            )?))?)?;
            let numbers = readers::wire_numbers(&data["routes"], &data["stock"], &json!([]))?;
            provider(
                json!({"kind":"cut","crate":"machine","name":"installed-wires","numbers":numbers,"output":d["output"],"numbers_name":"installed-wires"}),
            )
        }
        "build_manifest" => manifest(
            &d["state"],
            &d["graph"],
            &d["routes"],
            &d["terminations"],
            &d["bundles"],
        ),
        "build_numeric" => {
            let (a, b) = numeric(&request.root, &d["state"])?;
            Ok(json!([a, b]))
        }
        "build_sources" => Ok(json!(source_paths(&request.root, &d["numbers"])?)),
        "build_write_manifest" => write_manifest(
            &request.root,
            d["manifest"].clone(),
            Path::new(string(&d["scene_step"])?),
            Path::new(string(&d["output"])?),
            &d["additional_sources"],
            d.get("physical_sha256").and_then(Value::as_str),
        ),
        "build_export" => build_export(request, false, false),
        "build_kernel" => build_export(request, true, false),
        "build_numbers_output" => build_export(request, true, true),
        _ => bail!("build operation {}", request.op),
    }
}
