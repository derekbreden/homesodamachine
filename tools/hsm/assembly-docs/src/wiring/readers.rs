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
pub fn reference(path: &Path, rotation: &Value) -> Result<Value> {
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
                    (number(&rotation[i][j])? - if i == 0 && j == 0 { 1. } else { 0. }).abs()
                        <= 1e-12,
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
            for row in rows(rotation)? {
                let axis = v(row)?;
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
            let p = terminals::rotate(rotation, point)?;
            for i in 0..3 {
                lower[i] = lower[i].min(p[i]);
                upper[i] = upper[i].max(p[i]);
            }
        }
        return Ok(json!({"bounds":[lower,upper],"query_sources":[queries,manifest]}));
    }
    let transform = rows(rotation)?
        .iter()
        .map(|row| {
            let mut a = rows(row)?.clone();
            a.push(json!(0.));
            Ok(a)
        })
        .collect::<Result<Vec<_>>>()?;
    let result = provider(
        json!({"kind":"measure","instances":[{"model":format!("{}.npz",path.display()),"transform":transform}],"queries":[],"component_names":[]}),
    )?;
    let mut lo = [f64::INFINITY; 3];
    let mut hi = [f64::NEG_INFINITY; 3];
    for row in rows(&result["bodies"])? {
        let (a, b) = (v(&row["min"])?, v(&row["max"])?);
        for i in 0..3 {
            lo[i] = lo[i].min(a[i]);
            hi[i] = hi[i].max(b[i]);
        }
    }
    Ok(json!({"bounds":[lo,hi],"query_sources":[]}))
}
fn rgb(value: &Value) -> Result<Value> {
    if let Some(linear) = value.get("$linear") {
        return Ok(linear.clone());
    }
    let mut color = v(value)?;
    for c in &mut color {
        let v = if *c <= 0.04045 {
            *c / 12.92
        } else {
            ((*c + 0.055) / 1.055).powf(2.4)
        };
        *c = v as f32 as f64;
    }
    Ok(json!(color))
}
pub fn wire_numbers(routes: &Value, stock: &Value, components: &Value) -> Result<Value> {
    let mut wires = Vec::new();
    for r in rows(routes)? {
        let material = &stock[string(&r["stock"])?];
        wires.push(json!({"name":format!("wire-{}",string(&r["id"])?),"diameter_mm":material["od_mm"],"linear_rgb":rgb(&material["color"] )?,"segments":r["segments"]}));
    }
    let mut out = json!({"name":"installed-wiring","presentation_deflection_ratio":get("_payload_rules","LINEAR_DEFLECTION_RATIO")?,"presentation_angular_deflection_rad":get("_mesh_payload","ANGULAR_DEFLECTION")?,"routes":wires});
    if !components.is_null() && !rows(components)?.is_empty() {
        let mut output = Vec::new();
        for row in rows(components)? {
            let mut recipe = row[1].clone();
            recipe["name"] = row[0].clone();
            recipe["linear_rgb"] = rgb(&row[2])?;
            if recipe["kind"] == "import" {
                recipe["step"] = provider(json!({"kind":"step","path":recipe["step"]}))?;
            }
            output.push(recipe);
        }
        out["components"] = json!(output);
    }
    Ok(out)
}
