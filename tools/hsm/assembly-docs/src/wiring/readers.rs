use super::*;
use model::{V, cross, dot, sub, v};
use sha2::{Digest, Sha256};
use std::io::Read;
pub fn digest(path: &Path) -> Result<String> {
    let mut file = std::fs::File::open(path)?;
    let mut hash = Sha256::new();
    let mut buffer = [0u8; 1 << 16];
    loop {
        let read = file.read(&mut buffer)?;
        if read == 0 {
            break;
        }
        hash.update(&buffer[..read]);
    }
    let hex = format!("{:x}", hash.finalize());
    hsm_kernel::reads::digest(path, &hex);
    Ok(hex)
}
fn components(vertices: &Value, triangles: &Value) -> Result<Value> {
    let vertices = model::points(vertices)?;
    fn indices(value: &Value, out: &mut Vec<usize>) -> Result<()> {
        if let Some(rows) = value.as_array() {
            for row in rows {
                indices(row, out)?;
            }
        } else {
            out.push(value.as_u64().context("triangle index")? as usize);
        }
        Ok(())
    }
    let mut indices_flat = Vec::new();
    indices(triangles, &mut indices_flat)?;
    ensure!(indices_flat.len() % 3 == 0, "triangle indices");
    if indices_flat.is_empty() {
        return Ok(json!([]));
    }
    let mut parent = (0..vertices.len()).collect::<Vec<_>>();
    fn find(parent: &mut [usize], i: usize) -> usize {
        if parent[i] != i {
            parent[i] = find(parent, parent[i]);
        }
        parent[i]
    }
    fn join(parent: &mut [usize], a: usize, b: usize) {
        let (a, b) = (find(parent, a), find(parent, b));
        if a != b {
            parent[a.max(b)] = a.min(b);
        }
    }
    let triangles = indices_flat
        .chunks_exact(3)
        .map(|row| [row[0], row[1], row[2]])
        .collect::<Vec<_>>();
    for face in &triangles {
        ensure!(
            face.iter().all(|&i| i < vertices.len()),
            "triangle vertex index"
        );
        join(&mut parent, face[0], face[1]);
        join(&mut parent, face[1], face[2]);
    }
    let mut labels = BTreeMap::new();
    for i in 0..vertices.len() {
        let root = find(&mut parent, i);
        let count = labels.len();
        labels.entry(root).or_insert(count);
    }
    let count = labels.len();
    let mut volumes = vec![0.; count];
    let mut lower = vec![[f64::INFINITY; 3]; count];
    let mut upper = vec![[f64::NEG_INFINITY; 3]; count];
    for (i, p) in vertices.iter().enumerate() {
        let label = labels[&find(&mut parent, i)];
        for k in 0..3 {
            lower[label][k] = lower[label][k].min(p[k]);
            upper[label][k] = upper[label][k].max(p[k]);
        }
    }
    let origin = vertices[0];
    for face in triangles {
        let label = labels[&find(&mut parent, face[0])];
        let (a, b, c) = (
            sub(vertices[face[0]], origin),
            sub(vertices[face[1]], origin),
            sub(vertices[face[2]], origin),
        );
        volumes[label] += dot(a, cross(b, c)) / 6.;
    }
    let positive = (0..count).filter(|&i| volumes[i] > 0.).collect::<Vec<_>>();
    let sizes = positive
        .iter()
        .map(|&i| (0..3).map(|k| upper[i][k] - lower[i][k]).product::<f64>())
        .collect::<Vec<_>>();
    for i in 0..count {
        if volumes[i] >= 0. {
            continue;
        }
        let around = positive
            .iter()
            .enumerate()
            .filter(|(_, j)| {
                (0..3).all(|k| lower[**j][k] <= lower[i][k] && upper[**j][k] >= upper[i][k])
            })
            .min_by(|(a, _), (b, _)| sizes[*a].total_cmp(&sizes[*b]));
        if let Some((_, &outside)) = around {
            volumes[outside] += volumes[i];
        }
    }
    Ok(json!(
        positive
            .into_iter()
            .map(|i| json!({"lower":lower[i],"upper":upper[i],"volume_mm3":volumes[i]}))
            .collect::<Vec<_>>()
    ))
}
fn bodies(rows_input: &Value, grid: Option<f64>) -> Result<Value> {
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
fn measurements(path: &Path, names: &Value) -> Result<Value> {
    let mut components = if names.is_null() {
        BTreeSet::new()
    } else {
        rows(names)?
            .iter()
            .map(|v| string(v).map(str::to_owned))
            .collect::<Result<BTreeSet<_>>>()?
    };
    let mut hosts = vec![
        "compressor".into(),
        "valve-v-a".into(),
        "valve-v-b".into(),
        "vk-solenoid".into(),
    ];
    hosts.extend("cdefghij".chars().map(|c| format!("coil-v-{c}")));
    for host in hosts {
        components.insert(host.clone());
        components.insert(format!("cold-core/{host}"));
    }
    let result = provider(
        json!({"kind":"measure","instances":[{"model":path}],"queries":[],"component_names":components}),
    )?;
    Ok(json!({"path":path,"sha256":digest(path)?,"bodies":result["bodies"]}))
}
fn reference(path: &Path, rotation: &Value) -> Result<Value> {
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
pub fn request(request: &Request) -> Result<Value> {
    let d = &request.data;
    match request.op.as_str() {
        "file_digest" => Ok(json!(digest(Path::new(string(&d["path"])?))?)),
        "model_components" => components(&d["vertices"], &d["triangles"]),
        "model_bodies" => bodies(&d["rows"], d.get("grid").and_then(Value::as_f64)),
        "model_measurements" => measurements(Path::new(string(&d["path"])?), &d["component_names"]),
        "model_read" => {
            let path = Path::new(string(&d["path"])?);
            let reading = if d["reading"].is_null() {
                measurements(path, &Value::Null)?
            } else {
                d["reading"].clone()
            };
            ensure!(
                reading["path"] == path.to_string_lossy().as_ref(),
                "Physical measurements belong to another model"
            );
            ensure!(
                reading["sha256"] == digest(path)?,
                "Physical model changed after its measurements"
            );
            bodies(&reading["bodies"], Some(2_f64.powi(-30)))
        }
        "model_reference_bounds" => reference(Path::new(string(&d["path"])?), &d["rotation"]),
        "wire_numbers" => wire_numbers(&d["routes"], &d["stock"], &d["components"]),
        _ => bail!("wiring reader operation {}", request.op),
    }
}
