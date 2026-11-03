//! World-placed warm fluid/gas tube paths and their occupied insulation.
//!
//! The caller supplies the selected authored route segments and installed
//! equipment groups that bound foam compression. No Python CAD is constructed.
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::{Affine, Body, Leg, Path as SweepPath, Plane, Profile,
                 Solid, Spline, V2, V3, import, part, step, v3};
use hsm_kernel::part::Numbers;
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

fn f(v: &Value, key: &str) -> Result<f64> {
    v[key].as_f64().with_context(|| format!("numeric {key}"))
}

fn point(v: &Value) -> Result<V3> {
    let a = v.as_array().context("three-vector")?;
    ensure!(a.len() == 3, "three-vector");
    Ok(v3(a[0].as_f64().context("x")?, a[1].as_f64().context("y")?,
          a[2].as_f64().context("z")?))
}

fn text<'a>(v: &'a Value, key: &str) -> Result<&'a str> {
    v[key].as_str().with_context(|| format!("text {key}"))
}

fn array(v: &Value) -> Result<&Vec<Value>> { v.as_array().context("array") }

fn datum(v: &Value) -> Result<Affine> {
    let r = array(&v["rotation"])?;
    let t = point(&v["translation_mm"])?;
    let mut m = [[0.; 4]; 3];
    for i in 0..3 {
        for j in 0..3 { m[i][j] = r[i][j].as_f64().context("rotation")?; }
        m[i][3] = t[i];
    }
    Ok(Affine { m })
}

fn color(v: &Value) -> Result<Option<[f64; 3]>> {
    Ok(if v.is_null() { None } else { Some(point(v)?.to_array()) })
}

fn start_and_tangent(segments: &Value) -> Result<(V3, V3)> {
    for s in array(segments)? {
        let points = array(if s["kind"] == "bezier" { &s["control_points_mm"] }
                           else { &s["points_mm"] })?;
        let start = point(&points[0])?;
        if s["kind"] == "arc" {
            let middle = point(&points[1])?;
            let end = point(&points[2])?;
            let (u, v) = (middle - start, end - start);
            let cross = u.cross(v);
            let center = start + (v * u.norm2() - u * v.norm2()).cross(cross)
                / (2. * cross.norm2());
            let axis = u.cross(end - middle).unit();
            return Ok((start, axis.cross(start - center).unit()));
        }
        for p in &points[1..] {
            let d = point(p)? - start;
            if d.norm() > 1e-8 { return Ok((start, d.unit())); }
        }
    }
    bail!("tube path has no finite span")
}

fn route_path(segments: &Value) -> Result<SweepPath> {
    let (start, _) = start_and_tangent(segments)?;
    let mut path = SweepPath::new(start);
    for segment in array(segments)? {
        match text(segment, "kind")? {
            "line" => {
                let end = point(&segment["points_mm"][1])?;
                if (end - path.at()).norm() > 1e-6 { path = path.line_to(end); }
            }
            "arc" => path = path.arc_through(point(&segment["points_mm"][1])?,
                                              point(&segment["points_mm"][2])?)?,
            "bezier" => {
                let controls = array(&segment["control_points_mm"])?
                    .iter().map(point).collect::<Result<Vec<_>>>()?;
                path = path.bezier(&controls)?;
            }
            other => bail!("unknown warm tube path {other}"),
        }
    }
    Ok(path)
}

fn sweep(segments: &Value, outer: f64, inner: Option<f64>) -> Result<Solid> {
    let (start, tangent) = start_and_tangent(segments)?;
    let path = route_path(segments)?;
    let wide = if tangent.x.abs() < 0.9 { V3::X } else { V3::Y };
    let mut profile = Profile::circle(V2::ZERO, outer);
    if let Some(inner) = inner { profile = profile.with_hole(Profile::circle(V2::ZERO, inner).outer); }
    Plane::new(start, wide, tangent)?.sweep(&profile, &path)
}

fn curve_length(curve: &Spline) -> f64 {
    fn refine(curve: &Spline, a: f64, b: f64, values: [f64; 3], whole: f64,
              tolerance: f64, remaining: u32) -> f64 {
        let middle = (a + b) / 2.;
        let left_middle = curve.derivative((a + middle) / 2.).norm();
        let right_middle = curve.derivative((middle + b) / 2.).norm();
        let left = (middle - a) * (values[0] + 4. * left_middle + values[1]) / 6.;
        let right = (b - middle) * (values[1] + 4. * right_middle + values[2]) / 6.;
        let error = left + right - whole;
        if remaining == 0 || error.abs() <= 15. * tolerance {
            left + right + error / 15.
        } else {
            refine(curve, a, middle, [values[0], left_middle, values[1]], left,
                   tolerance / 2., remaining - 1)
                + refine(curve, middle, b, [values[1], right_middle, values[2]], right,
                         tolerance / 2., remaining - 1)
        }
    }
    let (a, b) = curve.range();
    let values = [curve.derivative(a).norm(), curve.derivative((a + b) / 2.).norm(),
                  curve.derivative(b).norm()];
    let whole = (b - a) * (values[0] + 4. * values[1] + values[2]) / 6.;
    refine(curve, a, b, values, whole, 1e-9, 20)
}

fn route_length(path: &SweepPath) -> f64 {
    path.legs.iter().map(|leg| match *leg {
        Leg::Line { a, b } => (b - a).norm(),
        Leg::Arc { a, c, turn, .. } => (a - c).norm() * turn,
        Leg::Curve { k, .. } => curve_length(&path.curves[k]),
    }).sum()
}

fn lead_exits(v: &Value) -> Result<Vec<Solid>> {
    let pose = datum(&v["valve_pose"])?;
    let mut exits = vec![];
    for x in [-7.45,7.45] {
        let tip = pose.point(v3(x,27.1,52.2));
        // The existing R3 corner between downward and aft-facing lead stations.
        let a = tip + v3(0.,0.,2.);
        let before = tip + v3(0.,0.,-3.);
        let after = tip + v3(0.,-3.,-6.);
        let middle = tip + v3(0.,-3.+3./2_f64.sqrt(),-3.-3./2_f64.sqrt());
        exits.push(sweep(&json!([
            {"kind":"line","points_mm":[a.to_array(),before.to_array()]},
            {"kind":"arc","points_mm":[before.to_array(),middle.to_array(),after.to_array()]},
            {"kind":"line","points_mm":[after.to_array(),(tip+v3(0.,-12.,-6.)).to_array()]}
        ]),2.,None)?);
    }
    Ok(exits)
}

fn insulation(v: &Value, parts: &BTreeMap<String, Vec<Solid>>) -> Result<Solid> {
    let p = &v["plan"];
    let mut foam = sweep(&p["foam_segments"], f(p,"nominal_foam_od_mm")?/2.,
                         Some(f(p,"nominal_foam_id_mm")?/2.))?;
    let tube = sweep(&p["tube_segments"],f(p,"tube_od_mm")?/2.,Some(f(p,"tube_id_mm")?/2.))?;
    let mut tools: Vec<&Solid> = parts.get("soda-bend-holder").context("soda holder")?.iter().collect();
    tools.push(&tube);
    let exits = lead_exits(v)?;
    tools.extend(exits.iter());
    for name in array(&v["neighbors"])? {
        tools.extend(parts.get(name.as_str().context("foam neighbor")?)
            .context("placed foam neighbor")?.iter());
    }
    for tool in tools {
        for solid in tool.components() { foam = foam.cut(&solid)?; }
    }
    Ok(Solid::compose(&foam.components().into_iter().filter(|s|s.volume()>1.).collect::<Vec<_>>()))
}

fn equipment(n: &Numbers) -> Result<BTreeMap<String, Vec<Solid>>> {
    let mut requested: BTreeMap<String, BTreeMap<usize, Vec<(String, usize)>>> = BTreeMap::new();
    let mut parts: BTreeMap<String, Vec<Option<Solid>>> = BTreeMap::new();
    for (name, reference) in n.get("components")?.as_object().context("named equipment references")? {
        let path = text(reference, "model")?;
        let indices = array(&reference["indices"])?;
        parts.insert(name.clone(), vec![None; indices.len()]);
        let model = requested.entry(path.to_owned()).or_default();
        for (slot, index) in indices.iter().enumerate() {
            let index = index.as_u64().context("equipment body index")? as usize;
            model.entry(index).or_default().push((name.clone(), slot));
        }
    }
    for (path, bodies) in requested {
        let indices: BTreeSet<_> = bodies.keys().copied().collect();
        import::visit_model_indices(&path, &indices, |index, body| {
            let (last, others) = bodies[&index].split_last().unwrap();
            for (name, slot) in others {
                parts.get_mut(name).unwrap()[*slot] = Some(body.solid.clone());
            }
            parts.get_mut(&last.0).unwrap()[last.1] = Some(body.solid);
            Ok(())
        })?;
    }
    parts.into_iter().map(|(name, bodies)| Ok((name,
        bodies.into_iter().map(|body| body.context("equipment body outside model"))
            .collect::<Result<Vec<_>>>()?))).collect()
}

fn main() -> Result<()> {
    let (n, output) = part::args()?;
    let mut placed: Vec<(String, Option<[f64; 3]>, Solid)> = vec![];
    let mut groups = serde_json::Map::new();
    let mut order = vec![];
    let insulation_request = n.get("insulation")?;
    if !insulation_request.is_null() {
        let parts = equipment(&n)?;
        let foam = insulation(insulation_request, &parts).context("occupied soda insulation")?;
        let name = "soda-continuous-insulation".to_owned();
        groups.insert(name.clone(), json!([placed.len()]));
        placed.push((name.clone(), color(&insulation_request["color"])?, foam));
        order.push(name);
    }
    let routes = n.get("routes")?;
    let mut lengths = serde_json::Map::new();
    for name in array(n.get("route_order")?)? {
        let identifier = name.as_str().context("ordered route name")?;
        let spec = &routes[identifier];
        lengths.insert(identifier.to_owned(), json!(route_length(&route_path(&spec["segments"])?)));
        let inside = f(spec, "id_mm")?;
        let body = sweep(&spec["segments"], f(spec, "od_mm")? / 2.,
                         (inside > 0.).then_some(inside / 2.))
            .with_context(|| format!("warm tube route {identifier}"))?;
        let name = format!("tube-{identifier}");
        groups.insert(name.clone(), json!([placed.len()]));
        placed.push((name.clone(), color(&spec["color"])?, body));
        order.push(name);
    }
    let bodies = placed.iter().map(|(name, color, solid)|
        Body { name, color: *color, solid }).collect::<Vec<_>>();
    let name = n.text("name")?;
    let model_name = format!("{name}.step.npz");
    let document_name = format!("{name}.json");
    let model = output.join(&model_name);
    step::write_model(&model, &bodies)?;
    let instances: Vec<_> = order.iter().map(|name| json!({"model": model,
        "indices": groups[name], "name": name})).collect();
    let reports: Vec<_> = placed.iter().map(|(name, color, solid)| {
        let bounds = solid.bounds();
        json!({"name":name, "color":color, "min":bounds.min.to_array(),
            "max":bounds.max.to_array(), "volume":solid.volume(),
            "centroid":solid.centroid().to_array(), "vertices":solid.verts().len(),
            "triangles":solid.tris().len()})
    }).collect();
    let document = json!({"routes":routes, "route_lengths":lengths, "lengths":lengths,
        "route_order":n.get("route_order")?, "body_order":order,
        "insulation":insulation_request, "components":n.get("components")?,
        "component_order":order, "groups":groups, "instances":instances, "bodies":reports});
    std::fs::write(output.join(&document_name), serde_json::to_vec_pretty(&document)?)?;
    println!("{}", json!({"files":[model_name, document_name], "bodies":reports,
        "groups":groups, "instances":instances, "lengths":lengths,
        "body_order":order, "routes":routes, "route_order":n.get("route_order")?}));
    Ok(())
}
