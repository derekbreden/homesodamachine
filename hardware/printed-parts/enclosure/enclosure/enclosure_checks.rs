//! Enclosure questions on the existing fine models and their numeric tool recipes.
//!
//! Python supplies stations and formats the existing reports. Model import, tool
//! construction, intersections, connected components and face readings stay here.
use anyhow::{bail, ensure, Context, Result};
use hsm_kernel::*;
use serde_json::{json, Value};
use std::collections::{BTreeSet, HashMap};

fn number(v: &Value, key: &str) -> Result<f64> {
    v[key].as_f64().with_context(|| format!("number {key}"))
}
fn array(v: &Value) -> Result<Vec<f64>> {
    v.as_array().context("numeric array")?.iter()
        .map(|n| n.as_f64().context("number")).collect()
}
fn vector(v: &Value) -> Result<V3> {
    let a = array(v)?;
    ensure!(a.len() == 3, "three coordinates");
    Ok(v3(a[0], a[1], a[2]))
}
fn point(v: &Value) -> Result<V2> {
    let a = array(v)?;
    ensure!(a.len() == 2, "two coordinates");
    Ok(v2(a[0], a[1]))
}
fn corners(v: &Value) -> Result<(V3, V3)> {
    let b = array(v)?;
    ensure!(b.len() == 6, "six box limits");
    Ok((v3(b[0], b[2], b[4]), v3(b[1], b[3], b[5])))
}
fn axis(v: &Value) -> Result<usize> {
    let k = v["axis"].as_u64().context("axis")? as usize;
    ensure!(k < 3, "principal axis");
    Ok(k)
}
fn prism(v: &Value) -> Result<Solid> {
    let points = v["section"].as_array().context("section")?.iter()
        .map(point).collect::<Result<Vec<_>>>()?;
    let mut outline = Loop::polygon(&points);
    if v["op"] == "corner-prism" && number(v, "radius")? > 0. {
        let selected = v["corners"].as_array().context("rounded vertices")?.iter()
            .map(|k| Ok((k.as_u64().context("vertex")? as usize + points.len() - 1) % points.len()))
            .collect::<Result<Vec<_>>>()?;
        outline = outline.fillet_corners(&selected, number(v, "radius")?)?;
    }
    if let Some(offset) = v["offset"].as_f64() {
        outline = outline.ccw().offset(offset, true)?;
    }
    let z = array(&v["span"])?;
    let (plane, length) = match axis(v)? {
        0 => (Plane::YZ.at(v3(z[0], 0., 0.)), z[1] - z[0]),
        1 => (Plane::XZ.at(v3(0., z[0], 0.)), -(z[1] - z[0])),
        _ => (Plane::XY.at(v3(0., 0., z[0])), z[1] - z[0]),
    };
    plane.extrude(&Profile::new(outline), length)
}
fn frame(v: &Value) -> Result<Affine> {
    let m = v.as_array().context("3 by 4 frame")?;
    ensure!(m.len() == 3, "three frame rows");
    let row = m.iter().map(array).collect::<Result<Vec<_>>>()?;
    ensure!(row.iter().all(|r| r.len() == 4), "four frame columns");
    Ok(Affine::from_columns(v3(row[0][0], row[1][0], row[2][0]),
        v3(row[0][1], row[1][1], row[2][1]),
        v3(row[0][2], row[1][2], row[2][2]),
        v3(row[0][3], row[1][3], row[2][3])))
}
fn model(v: &Value) -> Result<Solid> {
    let reference = &v["reference"];
    let path = reference["model"].as_str().context("model path")?;
    let selected = reference.get("indices").map(|v| -> Result<BTreeSet<usize>> {
        v.as_array().context("model selection")?.iter()
            .map(|i| Ok(i.as_u64().context("source index")? as usize)).collect()
    }).transpose()?;
    let placement = reference.get("transform").map(frame).transpose()?;
    let mut parts = Vec::new();
    let mut visit = |_index, mut part: Imported| {
        if let Some(t) = &placement { part.solid = part.solid.transformed(t); }
        parts.push(part.solid);
        Ok(())
    };
    let count = if let Some(indices) = &selected {
        hsm_kernel::import::visit_model_indices(path, indices, &mut visit)?
    } else {
        hsm_kernel::import::visit_model(path, &mut visit)?
    };
    if let Some(indices) = &selected {
        ensure!(indices.iter().all(|&i| i < count), "selected index exceeds {path}'s {count} entries");
    }
    Solid::union_all(&parts)
}
fn residual(s: &Solid) -> Value {
    if s.is_empty() { json!({"volume_mm3":0., "min":null, "max":null}) }
    else {
        let b = s.bounds();
        json!({"volume_mm3":s.volume(), "min":b.min.to_array(), "max":b.max.to_array()})
    }
}
fn faces(s: &Solid) -> Value {
    let topology = hsm_kernel::topo::faces(s);
    json!(topology.tris.iter().zip(&topology.record).map(|(triangles, &record)| {
        let mut area = 0.;
        let mut weighted = V3::ZERO;
        let mut normal = V3::ZERO;
        let mut lo = v3(f64::INFINITY, f64::INFINITY, f64::INFINITY);
        let mut hi = -lo;
        let mut first_normal = V3::ZERO;
        for &index in triangles {
            let t = s.tris()[index as usize];
            let [a, b, c] = t.map(|i| s.verts()[i as usize]);
            let cross = (b-a).cross(c-a);
            let weight = cross.norm()/2.;
            if area == 0. && weight > 0. { first_normal = cross.unit(); }
            area += weight;
            weighted += (a+b+c)*(weight/3.);
            normal += cross/2.;
            lo = lo.min(a).min(b).min(c);
            hi = hi.max(a).max(b).max(c);
        }
        let surface = &s.faces()[record as usize].surface;
        let centre = if area > 0. { weighted/area } else { (lo+hi)/2. };
        let plane = matches!(surface, Surface::Plane { .. });
        let n = if plane && normal.norm() > 0. { normal.unit() } else {
            // MeshFace.normalAt() selects the nearest triangle for a curved face.
            triangles.iter().map(|&i| {
                let t = s.tris()[i as usize];
                let [a,b,c] = t.map(|k| s.verts()[k as usize]);
                (((a+b+c)/3.-centre).norm2(), (b-a).cross(c-a))
            }).min_by(|a,b| a.0.total_cmp(&b.0))
                .filter(|(_,n)| n.norm()>0.).map(|(_,n)| n.unit()).unwrap_or(first_normal)
        };
        json!({"area":area, "centre":centre.to_array(), "normal":n.to_array(),
            "min":lo.to_array(), "max":hi.to_array(),
            "kind":if plane {"PLANE"} else {surface.kind()}})
    }).collect::<Vec<_>>())
}
fn reading(s: &Solid, query: &Value) -> Value {
    if query["kind"] == "faces" { return faces(s); }
    let mut out = residual(s);
    if query["components"].as_bool().unwrap_or(false) {
        out["components"] = json!(s.components().iter().map(residual).collect::<Vec<_>>());
    }
    if query["valid"].as_bool().unwrap_or(false) { out["valid"] = json!(s.check().is_ok()); }
    out
}
fn evaluate(document: &Value) -> Result<Value> {
    let nodes = document["nodes"].as_array().context("recipe nodes")?;
    let queries = document["queries"].as_array().context("queries")?;
    let mut users = vec![0_usize; nodes.len()];
    let mut at: HashMap<usize, Vec<&Value>> = HashMap::new();
    for query in queries {
        let k = query["node"].as_u64().context("query node")? as usize;
        ensure!(k < nodes.len(), "query node is in the recipe");
        at.entry(k).or_default().push(query);
    }
    for (i, node) in nodes.iter().enumerate() {
        for child in node["inputs"].as_array().context("node inputs")? {
            let k = child.as_u64().context("node input")? as usize;
            ensure!(k < i, "recipe is in construction order");
            users[k] += 1;
        }
    }
    let mut live: Vec<Option<Solid>> = vec![None; nodes.len()];
    let mut answers = serde_json::Map::new();
    for (i, v) in nodes.iter().enumerate() {
        let inputs = v["inputs"].as_array().context("inputs")?.iter()
            .map(|k| Ok(k.as_u64().context("input")? as usize)).collect::<Result<Vec<_>>>()?;
        let get = |k: usize| live[inputs[k]].as_ref().expect("referenced solid is live");
        let op = v["op"].as_str().context("operation")?;
        let s = (|| -> Result<Solid> { Ok(match op {
            "empty" => Solid::empty(),
            "model" => model(v)?,
            "box" => { let (lo, hi) = corners(&v["box"])?; Solid::cuboid(lo, hi) },
            "rounded-box" => {
                let (lo, hi) = corners(&v["box"])?;
                Plane::XY.at(v3((lo.x+hi.x)/2., (lo.y+hi.y)/2., lo.z))
                    .extrude(&Profile::new(Loop::rounded_rect(V2::ZERO, hi.x-lo.x,
                        hi.y-lo.y, number(v,"radius")?)?), hi.z-lo.z)?
            },
            "cylinder" => {
                let k = axis(v)?;
                let c = array(&v["centre"])?;
                let z = array(&v["span"])?;
                let other = (0..3).filter(|&j| j != k).collect::<Vec<_>>();
                let mut p = [0.;3]; let mut direction = [0.;3];
                p[k] = z[0]; p[other[0]] = c[0]; p[other[1]] = c[1]; direction[k] = 1.;
                Solid::cylinder(V3::from(p), V3::from(direction), number(v,"radius")?, z[1]-z[0])?
            },
            "prism" | "corner-prism" => prism(v)?,
            "union" | "cut" | "intersect" => {
                let mut result = get(0).clone();
                for k in 1..inputs.len() {
                    result = match op { "union" => result.union(get(k))?,
                        "cut" => result.cut(get(k))?, _ => result.intersect(get(k))? };
                }
                result
            },
            "compose" => Solid::compose(&inputs.iter().map(|&k| live[k].as_ref().unwrap().clone()).collect::<Vec<_>>()),
            "translate" => get(0).translate(vector(&v["delta"])?),
            "rotate" => { let p = vector(&v["origin"])?;
                get(0).rotate(p, vector(&v["end"])?-p, number(v,"angle")?) },
            "mirror" => { let mut n = [0.;3]; n[axis(v)?] = 1.;
                get(0).mirror(V3::ZERO, V3::from(n)) },
            _ => bail!("unsupported enclosure question operation {op}"),
        }) })().with_context(|| format!("enclosure question node {i} ({op})"))?;
        if let Some(questions) = at.get(&i) {
            for query in questions {
                let key = query["key"].as_str().context("query key")?;
                answers.insert(key.to_owned(), reading(&s, query));
            }
        }
        live[i] = (users[i] > 0).then_some(s);
        for k in inputs { users[k] -= 1; if users[k] == 0 { live[k] = None; } }
    }
    Ok(json!({"answers":answers}))
}
fn main() -> Result<()> {
    let arguments = std::env::args().collect::<Vec<_>>();
    ensure!(arguments.len() == 3 && arguments[2] == "--check",
        "usage: enclosure-checks <numbers.json> --check");
    let path = std::path::Path::new(&arguments[1]);
    let bytes = std::fs::read(path)?;
    hsm_kernel::reads::read(path, &bytes);
    let document: Value = serde_json::from_slice(&bytes)?;
    println!("{}", serde_json::to_string(&evaluate(&document)?)?);
    Ok(())
}
