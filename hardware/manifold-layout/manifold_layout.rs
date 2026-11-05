//! The fixed manifold from Python's reference selections, frames and tube centrelines.
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::{Affine, Bounds, Imported, Loop, Path, Plane, Profile, Solid, V2, V3, part, v3};
use serde_json::{Value, json};
use std::collections::HashMap;

fn rows(v: &Value) -> Result<&Vec<Value>> { v.as_array().context("expected an array") }
fn num(v: &Value) -> Result<f64> { v.as_f64().context("expected a number") }
fn text(v: &Value) -> Result<&str> { v.as_str().context("expected text") }
fn point(v: &Value) -> Result<V3> {
    let a = rows(v)?;
    ensure!(a.len()==3, "a point has three coordinates");
    Ok(v3(num(&a[0])?,num(&a[1])?,num(&a[2])?))
}
fn xyz(v: V3) -> [f64;3] { [v.x,v.y,v.z] }
fn frame(v: &Value) -> Result<Affine> {
    let rows = rows(v)?;
    ensure!(rows.len()==3,"a frame has three rows");
    let mut m = [[0.;4];3];
    for (i,row) in rows.iter().enumerate() {
        let a = self::rows(row)?;
        ensure!(a.len()==4,"a frame row has four coordinates");
        for (j,v) in a.iter().enumerate() { m[i][j] = num(v)?; }
    }
    Ok(Affine { m })
}
fn bounds(b: Bounds) -> [f64;6] { [b.min.x,b.min.y,b.min.z,b.max.x,b.max.y,b.max.z] }
fn box_shape(v: &Value) -> Result<Solid> {
    let a = point(&v["origin"])?;
    Ok(Solid::cuboid(a,a+point(&v["size"])?))
}

fn reference(spec: &Value, imported: &[Imported]) -> Result<Solid> {
    let mut groups = vec![];
    for group in rows(&spec["groups"])? {
        let names = group.get("names").map(rows).transpose()?;
        let mut parts: Vec<Solid> = imported.iter().filter(|body| {
            names.is_none_or(|names| names.iter().any(|n| n.as_str()==Some(&body.name)))
        }).map(|body| body.solid.clone()).collect();
        ensure!(!parts.is_empty(),"{} selects no reference body; available {:?}",spec["name"],imported.iter().map(|b|&b.name).collect::<Vec<_>>());
        if let Some(names) = names {
            for name in names { ensure!(imported.iter().any(|b| Some(b.name.as_str())==name.as_str()),"missing selected body {name}"); }
        }
        let mut part = if group["union"]==true { Solid::union_all(&parts)? }
                       else { Solid::compose(&parts) };
        parts.clear();
        if let Some(cut) = group.get("cut_box") { part = part.cut(&box_shape(cut)?)?; }
        groups.push(part);
    }
    Ok(Solid::compose(&groups))
}

fn tube(v: &Value) -> Result<Solid> {
    let segments = rows(&v["segments"])?;
    ensure!(!segments.is_empty(),"a tube has a centreline");
    let first = rows(&segments[0]["points"])?;
    let mut path = Path::new(point(&first[0])?);
    for segment in segments {
        let p = rows(&segment["points"])?;
        path = match text(&segment["kind"])? {
            "line" => { ensure!(p.len()==2,"a line has two points"); path.line_to(point(&p[1])?) },
            "arc" => { ensure!(p.len()==3,"an arc has three points"); path.arc_through(point(&p[1])?,point(&p[2])?)? },
            kind => bail!("unknown centreline {kind}"),
        };
    }
    let z = point(&v["normal"])?.unit();
    let x = if z.x.abs()<0.8 { V3::X } else { V3::Y };
    let plane = Plane::new(point(&first[0])?,x,z)?;
    let mut profile = Profile::circle(V2::ZERO,num(&v["od"])?/2.);
    if !v["id"].is_null() { profile = profile.with_hole(Loop::circle(V2::ZERO,num(&v["id"])?/2.)); }
    Solid::sweep_with_tolerance(&profile.place(&plane),&path,0.003)
}

struct Placed { name: String, color: [f64;3], solid: Solid }

fn bodies(n: &part::Numbers) -> Result<Vec<Placed>> {
    let mut sources: HashMap<String,Vec<Imported>> = HashMap::new();
    for (key,path) in n.get("sources")?.as_object().context("sources is an object")? {
        sources.insert(key.clone(),hsm_kernel::import::step(text(path)?)?);
    }
    let mut prototypes: HashMap<String,Solid> = HashMap::new();
    let mut out = vec![];
    for row in rows(n.get("bodies")?)? {
        let name = text(&row["name"])?.to_owned();
        let solid = match text(&row["kind"])? {
            "reference" => {
                let source = text(&row["source"])?;
                let key = format!("{source}:{}",row["groups"]);
                if !prototypes.contains_key(&key) {
                    prototypes.insert(key.clone(),reference(row,sources.get(source).context("unknown reference")?)?);
                }
                prototypes[&key].transformed(&frame(&row["transform"])?)
            },
            "tube" => tube(row)?,
            kind => bail!("unknown body kind {kind}"),
        };
        let c = point(&row["color"])?;
        out.push(Placed { name, color:xyz(c), solid });
    }
    Ok(out)
}

/// The envelope of every placed body, stubs included: the scale of the presentation tolerance.
fn reach(bodies: &[Placed]) -> Value {
    let mut low = v3(f64::INFINITY,f64::INFINITY,f64::INFINITY);
    let mut high = -low;
    for body in bodies {
        let b = body.solid.bounds();
        low = low.min(b.min); high = high.max(b.max);
    }
    json!(bounds(Bounds { min:low,max:high }))
}

fn main() -> Result<()> {
    let (n,out) = part::args()?;
    let mut placed = bodies(&n)?;
    let reach = reach(&placed);
    let b = rows(&reach)?;
    let extent = ((num(&b[3])?-num(&b[0])?) + (num(&b[4])?-num(&b[1])?)
                  + (num(&b[5])?-num(&b[2])?))/3.0;
    let tolerance = (extent*n.f("presentation_ratio")?).max(hsm_kernel::TOLERANCE);
    let drawing: Vec<Solid> = placed.iter_mut().map(|b| {
        let mut drawn = b.solid.simplified_to(tolerance/2.)?;
        b.solid.forget_backend();
        drawn.forget_backend();
        Ok(drawn)
    }).collect::<Result<_>>()?;
    let bodies: Vec<part::AssemblyBody> = placed.iter().zip(&drawing).map(|(b,drawn)| part::AssemblyBody {
        name:&b.name,color:Some(b.color),fine:&b.solid,presentation:drawn
    }).collect();
    let document = json!({"presentation_tolerance_mm":tolerance,
                          "presentation_simplification_tolerance_mm":tolerance/2.});
    let said = part::write_assembly(&out,n.text("name")?,&bodies,Some(&document))?;
    println!("{said}");
    Ok(())
}
