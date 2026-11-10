//! Placed above-core equipment, installed pump joints and warm-side tube solids.
//!
//! Purchased models retain their fine triangles. Parameter-dependent mating stock,
//! hardware, insulation and tube paths are constructed on the Rust kernel.
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::{Affine, Body, Imported, Path as SweepPath, Plane, Profile, Solid, V2, V3,
                 import, part, step, v2, v3};
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::sync::Arc;

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
fn frame(v: &Value) -> Result<Affine> {
    let rows = array(v)?;
    ensure!(rows.len() == 3, "three installed rows");
    let mut m = [[0.; 4]; 3];
    for i in 0..3 {
        let row = array(&rows[i])?;
        ensure!(row.len() == 4, "four installed columns");
        for j in 0..4 { m[i][j] = row[j].as_f64().context("installed coordinate")?; }
    }
    Ok(Affine { m })
}
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
/// An unplaced construction depends on its recipe, selected model entries and
/// numeric dimensions. Identity, installed frame, material and presentation are
/// applied separately for every instance. Keep cuffs on their authored CSG path.
fn construction_key(item: &Value) -> Option<String> {
    if item.get("op").and_then(Value::as_str) == Some("pump-tube") { return None; }
    let mut recipe = item.as_object()?.clone();
    for field in ["name", "transform", "color", "presentation"] {
        recipe.remove(field);
    }
    Some(Value::Object(recipe).to_string())
}

fn selected(v: &Value, name: &str) -> bool {
    let included = v.get("select").and_then(Value::as_array).map(|selected|
        selected.iter().any(|n| n.as_str().is_some_and(|n|
            name == n || name.strip_prefix(n).is_some_and(|rest| rest.starts_with('/')))))
        .unwrap_or(true);
    let excluded = v.get("exclude").and_then(Value::as_array).is_some_and(|excluded|
        excluded.iter().any(|n| n.as_str().is_some_and(|n| name.contains(n))));
    included && !excluded
}
fn source(v: &Value, cache: &mut BTreeMap<String, Vec<Imported>>) -> Result<Vec<Solid>> {
    let path = text(v, "source")?;
    if !cache.contains_key(path) {
        let bodies = if path.ends_with(".npz") { import::model(path)? }
                     else { import::payload(path)? };
        cache.insert(path.to_owned(), bodies);
    }
    let mut solids = vec![];
    for body in &cache[path] {
        if selected(v,&body.name) { solids.push(body.solid.clone()); }
    }
    ensure!(!solids.is_empty(), "{} selected no bodies in {path}", text(v, "name")?);
    Ok(solids)
}
fn profile_rows(v: &Value) -> Result<Vec<V2>> {
    array(v)?.iter().map(|row| {
        let row = array(row)?;
        Ok(v2(row[0].as_f64().context("axial coordinate")?,
              row[1].as_f64().context("profile radius")?))
    }).collect()
}
fn turned(profile: &[V2], filled: bool) -> Result<Solid> {
    let mut outline = Vec::new();
    if filled { outline.push(v2(profile[0].x, 0.)); }
    outline.extend_from_slice(profile);
    if filled { outline.push(v2(profile.last().unwrap().x, 0.)); }
    Plane::XY.revolve(&Profile::polygon(&outline), 360., V2::ZERO, v2(1., 0.))
}
fn tube_turn(rows: &[V2], od: f64, id: f64) -> Result<Solid> {
    let mut clean = vec![];
    for &row in rows {
        if clean.last().is_none_or(|last: &V2|
            (row.x-last.x).abs()>1e-6 || (row.y-last.y).abs()>1e-6) { clean.push(row); }
    }
    let mut outline: Vec<_> = clean.iter().map(|p|
        v2(p.x, (p.y * p.y + (od * od - id * id) / 4.).sqrt())).collect();
    outline.extend(clean.iter().rev().copied());
    turned(&outline, false)
}
fn start_and_tangent(segments: &Value) -> Result<(V3, V3)> {
    for s in array(segments)? {
        let points = array(if s["kind"] == "bezier" { &s["control_points_mm"] }
                           else { &s["points_mm"] })?;
        let start = point(&points[0])?;
        if s["kind"] == "arc" {
            let (u, v) = (point(&points[1])? - start, point(&points[2])? - start);
            let w = u.cross(v);
            let center = start + (v * u.norm2() - u * v.norm2()).cross(w) / (2. * w.norm2());
            return Ok((start, w.unit().cross(start - center).unit()));
        }
        for p in &points[1..] {
            let d = point(p)? - start;
            if d.norm() > 1e-8 { return Ok((start, d.unit())); }
        }
    }
    bail!("tube path has no finite span")
}
fn sweep(segments: &Value, outer: f64, inner: Option<f64>) -> Result<Solid> {
    let (start, tangent) = start_and_tangent(segments)?;
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
            other => bail!("unknown equipment path {other}"),
        }
    }
    let wide = if tangent.x.abs() < 0.9 { V3::X } else { V3::Y };
    let mut profile = Profile::circle(V2::ZERO, outer);
    if let Some(inner) = inner { profile = profile.with_hole(Profile::circle(V2::ZERO, inner).outer); }
    Plane::new(start, wide, tangent)?.sweep(&profile, &path)
}
fn pump_tube(v: &Value) -> Result<Solid> {
    let j = &v["joint"];
    let rows = profile_rows(&j["bore"])?;
    let (od, id) = (f(j, "tube_od_mm")?, f(j, "tube_id_mm")?);
    let end = datum(&v["bend"]["end_frame"])?;
    if v["side"] == "suction" {
        let mut segments = v["bend"]["segments"].clone();
        for segment in segments.as_array_mut().context("suction arcs")? {
            segment["kind"] = json!("arc");
        }
        let span = sweep(&segments, od / 2., Some(id / 2.))?;
        let on_barb = tube_turn(&rows[..rows.len() - 2], od, id)?;
        let on_stem = tube_turn(&[v2(0., rows.last().unwrap().y),
                                 v2(10., rows.last().unwrap().y)], od, id)?.transformed(&end);
        Solid::union_all(&[on_barb,span,on_stem])
    } else {
        let direction = end.vector(V3::X);
        let angle = direction.x.clamp(-1., 1.).acos();
        let axis = V3::X.cross(direction).unit();
        let radial = v3(0., direction.y, direction.z).unit();
        let pivot = radial * -f(j, "pivot_z")?;
        let half = Affine::rotation(pivot, axis, angle.to_degrees() / 2.);
        let crease = Solid::cuboid(v3(-100., -100., -100.), v3(0., 100., 100.)).transformed(&half);
        let past = od * (angle / 2.).tan() + 1.;
        let mut barb = rows[..rows.len() - 2].to_vec();
        barb.push(v2(past, rows[rows.len() - 3].y));
        let on_barb = tube_turn(&barb, od, id)?.intersect(&crease)?;
        let on_stem = tube_turn(&[v2(-past, rows.last().unwrap().y), *rows.last().unwrap()], od, id)?
            .transformed(&end).cut(&crease)?;
        on_barb.union(&on_stem)
    }
}
fn key_outline() -> Vec<V2> {
    // Same 48 samples on each of the two authored circles as the native key.
    let mut p = vec![];
    for (center, width) in [(4., 8.), (14., 26.)] {
        for i in 0..48 {
            let a = i as f64 * std::f64::consts::TAU / 48.;
            p.push(v2(center + width / 2. * a.cos(), width / 2. * a.sin()));
        }
    }
    p.sort_by(|a, b| a.x.total_cmp(&b.x).then(a.y.total_cmp(&b.y)));
    let mut hull: Vec<V2> = vec![];
    for &v in &p {
        while hull.len() > 1 && (hull[hull.len()-1]-hull[hull.len()-2]).cross(v-hull[hull.len()-1]) <= 0. {
            hull.pop();
        }
        hull.push(v);
    }
    let lower = hull.len();
    for &v in p.iter().rev().skip(1) {
        while hull.len() > lower && (hull[hull.len()-1]-hull[hull.len()-2]).cross(v-hull[hull.len()-1]) <= 0. {
            hull.pop();
        }
        hull.push(v);
    }
    hull.pop();
    hull
}
fn pump_clamp(v: &Value) -> Result<Solid> {
    let (r, xc, keys) = (f(v, "diameter")? / 2., f(v, "xc")?, f(v, "keys")?);
    let top = r + 0.6 + 7.;
    let screw_z = r + 0.6 + 3.5;
    if v["kind"] == "key" {
        let start = keys * (13. / 2. + 3.);
        let outline: Vec<_> = key_outline().iter().map(|p| v2(start + keys * p.x, screw_z + p.y)).collect();
        return Plane::YZ.at(v3(xc - 2.5, 0., 0.)).extrude(&Profile::polygon(&outline), 5.);
    }
    let band = Solid::cylinder(v3(xc - 4.5, 0., 0.), V3::X, r + 0.6, 9.)?
        .cut(&Solid::cylinder(v3(xc - 4.5, 0., 0.), V3::X, r, 9.)?)?;
    let housing = Solid::cuboid(v3(xc - 5., -6.5, 0.), v3(xc + 5., 6.5, top))
        .cut(&Solid::cylinder(v3(xc - 5., 0., 0.), V3::X, r + 0.6, 10.)?)?;
    let neck = Solid::cylinder(v3(xc, keys * 6.5, screw_z), V3::Y * keys, 3., 3.)?;
    band.union(&housing)?.union(&neck)
}
fn bulkhead(v: &Value, sources: &mut BTreeMap<String, Vec<Imported>>) -> Result<Solid> {
    let mut request = v.clone();
    request["select"] = json!(["fitting"]);
    let stock = Solid::compose(&source(&request, sources)?);
    let radius = 15. / 2.;
    let outside = Solid::cuboid(v3(-21., 0., -21.), v3(21., 11.827402874737649, 21.));
    let inside = Solid::cylinder(v3(0., -21.461096075301846, 0.), V3::Y,
                                 radius, 21.461096075301846)?;
    stock.intersect(&outside.union(&inside)?)
}
fn nut(v: &Value) -> Result<Solid> {
    let d = &v["data"];
    let center = v3(f(d, "x")?, f(d, "flange_y")? - 6., f(d, "z")?);
    let mut p = Profile::new(hsm_kernel::Loop::regular(V2::ZERO, 6,
        f(d, "nut_af_mm")? / (std::f64::consts::PI / 6.).cos()));
    p = p.with_hole(Profile::circle(V2::ZERO, f(d, "barrel_d_mm")? / 2.).outer);
    Ok(Plane::new(center, V3::X, -V3::Y)?.extrude(&p, f(d, "nut_depth_mm")?)?
        .rotate(v3(center.x, 0., center.z), V3::Y, 30.))
}
fn mounting(v: &Value) -> Result<Solid> {
    let axis = point(&v["axis"])?;
    let p = point(&v["point"])?;
    if v["kind"] == "insert" {
        let face = p - axis * f(v, "setback")?;
        return Solid::cylinder(face, -axis, 2.3, 4.)?
            .cut(&Solid::cylinder(face + axis * 0.1, -axis, 1.25, 4.2)?);
    }
    let head = p + axis * f(v, "head_reach")?;
    let length = f(v, "length")?;
    let stock = Solid::cylinder(head - axis * length, axis, 1.5, length)?
        .union(&Solid::cylinder(head, axis, 2.75, 3.)?)?;
    let wide = if axis.x.abs() < 0.9 { V3::X } else { V3::Y };
    let socket = Profile::new(hsm_kernel::Loop::regular(V2::ZERO, 6,
        2.5 / (std::f64::consts::PI / 6.).cos()));
    stock.cut(&Plane::new(head + axis * 1.5, wide, axis)?.extrude(&socket, 1.6)?)
}
fn vent_adapter(v: &Value) -> Result<Solid> {
    let (rb, rt) = (((14. * 14. + 7.7 * 7.7 - 6.1 * 6.1) as f64).sqrt() / 2.,
                    ((11.7 * 11.7 + 4. * 4. - 3.8 * 3.8) as f64).sqrt() / 2.);
    let (drop, reach, bend) = (9.55, 25.4, 4.05);
    let cup = Solid::cylinder(v3(0., 0., -drop - rt), V3::Z, rb, 8.6 + drop + rt)?;
    let socket = Solid::cylinder(v3(0., 0., -drop), -V3::X, rt, reach)?;
    let channel = sweep(&json!([{"kind":"arc","points_mm":[
        [0.,0.,-5.5],[-bend+bend/2_f64.sqrt(),0.,-5.5-bend/2_f64.sqrt()],[-bend,0.,-drop]]}]),
        2., None)?;
    let bore = Solid::cylinder(v3(-bend, 0., -drop), -V3::X, 2., reach - bend + 0.1)?;
    let transition = Solid::cone(v3(0., 0., -5.5), V3::Z, 2., 7.7 / 2., 5.5)?;
    let barb = Solid::cylinder(V3::ZERO, V3::Z, 7.7 / 2., 8.7)?;
    let mut body = cup.union(&socket)?.cut(&barb)?.cut(&transition)?.cut(&channel)?.cut(&bore)?;
    for (i, (center, radius)) in [(3.1, rb), (19.4, rt)].into_iter().enumerate() {
        let (lo, hi) = (center - 1.4, center + 1.4);
        let points = [v2(radius, lo - 1.), v2(radius - 0.5, lo), v2(radius - 0.5, hi),
                      v2(radius, hi + 1.), v2(radius + 1., hi + 1.), v2(radius + 1., lo - 1.)];
        let mut groove = Plane::XZ.revolve(&Profile::polygon(&points), 360., V2::ZERO, v2(0.,1.))?;
        if i == 1 { groove = groove.rotate(V3::ZERO, V3::Y, -90.).translate(v3(0.,0.,-drop)); }
        body = body.cut(&groove)?;
    }
    let flat_z = -(rb + drop + rt) / 2_f64.sqrt() + 0.6;
    body = body.rotate(V3::ZERO, V3::Y, 45.)
        .cut(&Solid::cuboid(v3(-50.,-50.,flat_z-1.),v3(50.,50.,flat_z)))?
        .rotate(V3::ZERO, V3::Y, -45.);
    Ok(body.translate(point(&v["vent_tip"])?))
}
fn main() -> Result<()> {
    let (n, output) = part::args()?;
    println!("{}", run(&n, &output)?);
    Ok(())
}

/// The placed equipment cut into `output`, and what it wrote there.
pub fn run(n: &part::Numbers, output: &std::path::Path) -> Result<Value> {
    let mut sources = BTreeMap::new();
    let mut placed: Vec<(String,Option<[f64;3]>,Solid)> = vec![];
    let mut groups = serde_json::Map::new();
    let mut presentation = vec![];
    let items = array(n.get("items")?)?;
    let keys: Vec<_> = items.iter().map(construction_key).collect();
    let mut last_construction = BTreeMap::new();
    let mut last_source = BTreeMap::new();
    for (index, (item, key)) in items.iter().zip(&keys).enumerate() {
        if let Some(key) = key.as_deref() { last_construction.insert(key, index); }
        if let Some(path) = item.get("source").and_then(Value::as_str) {
            last_source.insert(path, index);
        }
    }
    let mut constructions: BTreeMap<&str, Arc<[Solid]>> = BTreeMap::new();
    for (index, item) in items.iter().enumerate() {
        let name = text(item,"name")?;
        let op = text(item,"op")?;
        let key = keys[index].as_deref();
        let raw = if let Some(raw) = key.and_then(|key| constructions.get(key)) {
            Arc::clone(raw)
        } else {
            let raw: Arc<[Solid]> = (|| -> Result<Vec<Solid>> { Ok(match op {
                "reference" => source(item,&mut sources)?,
                "valve" => {
                    let original = source(item,&mut sources)?;
                    let mut solids = vec![];
                    for body in original {
                        for mut solid in body.components() {
                            let b = solid.bounds();
                            let port = if b.max.y < -22.25 {Some("inlet")}
                                       else if b.min.y > 22.25 {Some("outlet")} else {None};
                            if let Some(angle) = port.and_then(|p|item["clock"][p].as_f64()).filter(|a|*a!=0.) {
                                solid=solid.rotate(v3(0.,0.,11.05),V3::Y,angle);
                            }
                            solids.push(solid);
                        }
                    }
                    solids
                }
                "stem-elbow" => {
                    let trim = Solid::cuboid(v3(-100.,-50.,-50.),v3(f(item,"tip_x")?,50.,50.));
                    source(item,&mut sources)?.iter().map(|s|s.cut(&trim)).collect::<Result<Vec<_>>>()?
                }
                "pump-tube" => vec![pump_tube(item)?],
                "pump-reducer" => {
                    let cut = f(item,"cut_x")?;
                    let trim = Solid::cuboid(v3(-100.,-50.,-50.),v3(cut,50.,50.));
                    source(item,&mut sources)?.iter().map(|s|Ok(s.cut(&trim)?.translate(v3(-cut,0.,0.))))
                        .collect::<Result<Vec<_>>>()?
                }
                "pump-clamp" => vec![pump_clamp(item)?],
                "bulkhead" => vec![bulkhead(item,&mut sources)?],
                "bulkhead-nut" => vec![nut(item)?],
                "mount-hardware" => vec![mounting(item)?],
                "vent-adapter" => vec![vent_adapter(item)?],
                _ => bail!("unknown equipment operation {op}"),
            }) })().with_context(||format!("equipment {name}"))?.into();
            if let Some(key) = key.filter(|key| last_construction.get(*key).copied().unwrap() > index) {
                constructions.insert(key, Arc::clone(&raw));
            }
            raw
        };
        let installed = frame(&item["transform"])?;
        let rgb = color(&item["color"])?;
        let start = placed.len();
        if op == "reference" && item.get("presentation").and_then(Value::as_bool)!=Some(false) {
            let path = text(item,"source")?;
            if path.ends_with(".npz") {
                let indices: Vec<_> = sources[path].iter().enumerate()
                    .filter_map(|(i,b)|selected(item,&b.name).then_some(i)).collect();
                let targets: Vec<_> = (0..raw.len()).map(|i|if raw.len()==1 {name.to_owned()}
                    else {format!("{name}/{}",i+1)}).collect();
                presentation.push(json!({"model":path,"indices":indices,
                    "targets":targets,"transform":item["transform"]}));
            } else {
                let bytes=std::fs::read(path)?;
                let size=u32::from_le_bytes(bytes[..4].try_into()?) as usize;
                let header:Value=serde_json::from_slice(&bytes[4..4+size])?;
                let indices:Vec<_>=array(&header["meshes"] )?.iter().enumerate()
                    .filter_map(|(i,b)|selected(item,b["name"].as_str().unwrap_or("")).then_some(i)).collect();
                if indices.len()==raw.len() {
                    let targets:Vec<_>=(0..raw.len()).map(|i|if raw.len()==1 {name.to_owned()}
                        else {format!("{name}/{}",i+1)}).collect();
                    presentation.push(json!({"payload":path,"indices":indices,
                        "targets":targets,"transform":item["transform"],"source_sha256":header["src"]}));
                }
            }
        }
        let source_colors: Vec<_> = if op == "reference" && rgb.is_none() {
            sources[text(item, "source")?].iter()
                .filter(|body| selected(item, &body.name)).map(|body| body.color).collect()
        } else { Vec::new() };
        placed.extend(raw.iter().enumerate().map(|(index, solid)|
            (name.to_owned(), rgb.or_else(|| source_colors.get(index).copied().flatten()),
             solid.transformed(&installed))));
        groups.insert(name.to_owned(),json!((start..placed.len()).collect::<Vec<_>>()));
        if let Some(key) = key.filter(|key| last_construction.get(*key).copied() == Some(index)) {
            constructions.remove(key);
        }
        if let Some(path) = item.get("source").and_then(Value::as_str)
                .filter(|path| last_source.get(*path).copied() == Some(index)) {
            sources.remove(path);
        }
    }
    // Input geometry is released before the output tables and archive are written.
    drop(sources);
    let routes = n.get("routes")?.clone();
    let bodies = placed.iter().map(|(name,color,solid)|Body{name,color:*color,solid}).collect::<Vec<_>>();
    let name = n.text("name")?;
    let model = output.join(format!("{name}.step.npz"));
    let mut document = json!({"equipment":n.get("items")?,"frames":n.get("frames")?,
        "world_ports":n.get("world_ports")?,"routes":routes,"component_order":n.get("component_order")?,
        "core_equipment":n.get("core_equipment")?,"groups":groups,
        "native_route_specs":n.get("native_route_specs")?,"native_connections":n.get("native_connections")?,
        "native_route_order":n.get("native_route_order")?,
        "keystone_station":n.get("keystone_station")?,"keystone_clearances":n.get("keystone_clearances")?});
    step::write_model(&model,&bodies)?;
    let instances: Vec<_> = array(n.get("component_order")?)?.iter().map(|value| {
        let name=value.as_str().unwrap();
        json!({"model":model,"indices":groups[name],"name":name})
    }).collect();
    document["instances"]=json!(instances);
    document["presentation"]=json!(presentation);
    document["insulation"]=n.get("insulation")?.clone();
    document["route_order"]=n.get("route_order")?.clone();
    document["bodies"]=json!(placed.iter().map(|(name,color,solid)| {
        let bounds=solid.bounds();
        let mass=solid.mass();
        json!({"name":name,"color":color,"min":bounds.min.to_array(),"max":bounds.max.to_array(),
            "volume":mass.volume,"centroid":mass.centroid.to_array(),
            "vertices":solid.verts().len(),"triangles":solid.tris().len()})
    }).collect::<Vec<_>>());
    std::fs::write(output.join(format!("{name}.json")),serde_json::to_vec_pretty(&document)?)?;
    Ok(json!({"files":[format!("{name}.step.npz"),format!("{name}.json")],
        "bodies":document["bodies"],"groups":groups}))
}
