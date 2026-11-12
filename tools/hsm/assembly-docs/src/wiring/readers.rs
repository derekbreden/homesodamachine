use super::*;
use model::{V, v};
pub fn bodies(rows_input: &Value, grid: Option<f64>) -> Result<Value> {
    let suffix = regex::Regex::new(r"/\d+$")?;
    let mut grouped: BTreeMap<String, Vec<&Value>> = BTreeMap::new();
    for row in rows(rows_input)? {
        grouped
            .entry(suffix.replace(string(&row["name"])?, "").into_owned())
            .or_default()
            .push(row);
    }
    let mut out = json!({});
    let bound = |value: &Value| -> Result<V> {
        let mut p = v(value)?;
        if let Some(grid) = grid {
            for value in &mut p {
                *value = (value.abs() / grid).round_ties_even()
                    * grid
                    * if value.is_sign_negative() { -1. } else { 1. };
            }
        }
        Ok(p)
    };
    for (name, found) in grouped {
        let mut solids = Vec::new();
        let mut color = Value::Null;
        for row in found {
            if color.is_null() && !row["color"].is_null() {
                color = row["color"].clone();
            }
            let components = row
                .get("components")
                .map(rows)
                .transpose()?
                .cloned()
                .unwrap_or_else(|| vec![row.clone()]);
            for s in components {
                solids.push(json!({"lower":bound(&s["min"] )?,"upper":bound(&s["max"] )?,"volume_mm3":s["volume"]}));
            }
        }
        out[name] = json!([{"solids":solids},color]);
    }
    Ok(out)
}
/// The bounds of the reference STEP at `path` turned by `rotation`: from its frozen native
/// queries where the reference keeps them, else from its fine model.
pub fn reference(path: &Path, rotation: &[V; 3]) -> Result<(V, V)> {
    let queries = path.with_file_name("native-queries.json");
    if queries.is_file() {
        let raw = std::fs::read(&queries)?;
        hsm_kernel::reads::read(&queries, &raw);
        let data: Value = serde_json::from_slice(&raw)?;
        let row = &data["references"][path.file_name().unwrap().to_string_lossy().as_ref()];
        let manifest = path.with_file_name("frozen-asset.json");
        let raw = std::fs::read(&manifest)?;
        hsm_kernel::reads::read(&manifest, &raw);
        let identity: Value = serde_json::from_slice(&raw)?;
        ensure!(
            identity["members"][path.file_name().unwrap().to_string_lossy().as_ref()]
                == row["step_sha256"],
            "{}: reference bounds name a different frozen asset",
            path.display()
        );
        let lo = v(&row["bounds_mm"][0])?;
        let hi = v(&row["bounds_mm"][1])?;
        let mut source = Vec::new();
        if let Some(support) = row.get("yz_support_mm") {
            for (i, j) in [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)] {
                ensure!(
                    (rotation[i][j] - if i == 0 && j == 0 { 1. } else { 0. }).abs() <= 1e-12,
                    "{}: reference supports X-axis turns",
                    path.display()
                );
            }
            for x in [lo[0], hi[0]] {
                for yz in rows(support)? {
                    source.push([x, number(&yz[0])?, number(&yz[1])?]);
                }
            }
        } else {
            for axis in rotation {
                ensure!(
                    (axis.iter().map(|v| v.abs()).sum::<f64>() - 1.).abs() <= 1e-12
                        && axis
                            .iter()
                            .all(|v| v.abs().min((v.abs() - 1.).abs()) <= 1e-12),
                    "{}: reference supports axis-aligned turns",
                    path.display()
                );
            }
            for x in [lo[0], hi[0]] {
                for y in [lo[1], hi[1]] {
                    for z in [lo[2], hi[2]] {
                        source.push([x, y, z]);
                    }
                }
            }
        }
        let mut lower = [f64::INFINITY; 3];
        let mut upper = [f64::NEG_INFINITY; 3];
        for point in source {
            let p = terminals::rotate(rotation, point);
            for i in 0..3 {
                lower[i] = lower[i].min(p[i]);
                upper[i] = upper[i].max(p[i]);
            }
        }
        return Ok((lower, upper));
    }
    let model = format!("{}.npz", path.display());
    let m = rotation.map(|row| [row[0], row[1], row[2], 0.]);
    ensure!(
        m.iter().flatten().all(|v| v.is_finite()),
        "a placement holds a non-finite number"
    );
    let bodies = measure::summaries(
        Path::new(&model),
        Some(&hsm_kernel::Affine { m }),
        &BTreeSet::new(),
    )?;
    let mut lo = [f64::INFINITY; 3];
    let mut hi = [f64::NEG_INFINITY; 3];
    for row in &bodies {
        let (a, b) = (v(&row["min"])?, v(&row["max"])?);
        for i in 0..3 {
            lo[i] = lo[i].min(a[i]);
            hi[i] = hi[i].max(b[i]);
        }
    }
    Ok((lo, hi))
}

/// The request the installed wires are cut from: each route as a wire of its stock's diameter
/// and colour, and each body with its colour made linear.
pub fn wire_numbers(
    src: &sources::Sources,
    routes: &[model::Route],
    stock: &BTreeMap<String, model::Stock>,
    bodies: Vec<model::Body>,
) -> Result<wire_request::Request> {
    let mut wires = Vec::new();
    for r in routes {
        let material = model::stock_of(stock, &r.connection)?;
        wires.push(wire_request::Wire {
            name: format!("wire-{}", r.connection.id),
            diameter_mm: material.od_mm,
            linear_rgb: model::Colour::Srgb(material.color).linear(),
            segments: r.segments.clone(),
        });
    }
    Ok(wire_request::Request {
        name: "installed-wiring".into(),
        file_stem: None,
        presentation_deflection_ratio: src.presentation_deflection_ratio()?,
        presentation_angular_deflection_rad: src.presentation_angular_deflection()?,
        routes: wires,
        components: bodies
            .into_iter()
            .map(|body| wire_request::Part {
                name: body.name,
                linear_rgb: body.colour.linear(),
                shape: body.shape,
            })
            .collect(),
    })
}
