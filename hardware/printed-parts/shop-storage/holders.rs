//! Gridfinity stock profiles extended to the catalog's heights and cut for each holder.
use anyhow::{Context, Result, ensure};
use hsm_kernel::part::{args, write_part, write_shown};
use hsm_kernel::*;
use serde_json::Value;
use std::collections::{BTreeMap, HashMap};

fn f(row: &Value, key: &str) -> Result<f64> {
    row[key].as_f64().with_context(|| format!("missing number {key}"))
}
fn point(row: &Value) -> Result<V3> {
    let p = row.as_array().context("coordinate triple")?;
    ensure!(p.len() == 3, "three coordinates");
    Ok(v3(p[0].as_f64().context("x")?, p[1].as_f64().context("y")?, p[2].as_f64().context("z")?))
}

// Extrude the split's existing cap. Its boundary vertices meet both halves point
// for point, including the stock's rounded corners and each divided compartment.
#[track_caller]
fn cap_extrusion(lower: &Solid, z: f64, height: f64) -> Result<Solid> {
    let mut old_to_new = BTreeMap::new();
    let mut vertices = Vec::new();
    let mut cap = Vec::new();
    let mut edge_uses: BTreeMap<(u32, u32), Vec<(u32, u32)>> = BTreeMap::new();
    let mut side_records = BTreeMap::new();
    for (t, &face) in lower.tris().iter().zip(lower.face_of()) {
        let on = t.iter().all(|&i| (lower.verts()[i as usize].z - z).abs() < 1e-8);
        if on {
            let triangle = t.map(|old| *old_to_new.entry(old).or_insert_with(|| {
                vertices.push(lower.verts()[old as usize]);
                vertices.len() as u32 - 1
            }));
            cap.push(triangle);
            for j in 0..3 {
                let (a, b) = (t[j], t[(j + 1) % 3]);
                edge_uses.entry((a.min(b), a.max(b))).or_default().push((a, b));
            }
        } else {
            for j in 0..3 {
                let (a, b) = (t[j], t[(j + 1) % 3]);
                if [a,b].iter().all(|&i| (lower.verts()[i as usize].z - z).abs() < 1e-8) {
                    side_records.insert((a.min(b), a.max(b)), face);
                }
            }
        }
    }
    ensure!(!cap.is_empty(), "the stock split has a cap");
    let count = vertices.len() as u32;
    vertices.extend(vertices.clone().iter().map(|&p| p + V3::Z * height));
    let mut faces = lower.faces().to_vec();
    let source = std::panic::Location::caller();
    let bottom = faces.len() as u32;
    faces.push(Face::new(Surface::Plane { p: v3(0.0,0.0,z), n: -V3::Z }, "extend", source));
    let top = faces.len() as u32;
    faces.push(Face::new(Surface::Plane { p: v3(0.0,0.0,z+height), n: V3::Z }, "extend", source));
    let mut triangles = Vec::new();
    let mut face_of = Vec::new();
    for t in cap {
        triangles.push([t[0],t[2],t[1]]); face_of.push(bottom);
        triangles.push(t.map(|i| i + count)); face_of.push(top);
    }
    for (key, uses) in edge_uses {
        if uses.len() != 1 { continue; }
        let (a,b) = uses[0];
        let (a,b) = (old_to_new[&a], old_to_new[&b]);
        let face = *side_records.get(&key).context("cap boundary meets the stock's wall")?;
        triangles.extend([[a,b,b+count], [a,b+count,a+count]]);
        face_of.extend([face,face]);
    }
    Solid::from_mesh(&vertices, &triangles, &face_of, &faces)
}

fn extended(stock: &Solid, z: f64, height: f64) -> Result<Solid> {
    if height == 0.0 { return Ok(stock.clone()); }
    ensure!(height > 0.0, "stock is extended above its minimum height");
    let (upper, lower) = stock.split(&Plane::XY.offset(z))?;
    let middle = cap_extrusion(&lower, z, height)?;
    Solid::union_all(&[lower, middle, upper.translate(V3::Z * height)])
}

fn prism(row: &Value) -> Result<Solid> {
    let plane = Plane::by_name(row["plane"].as_str().context("profile plane")?, V3::ZERO)?;
    let points = row["profile"].as_array().context("profile points")?.iter().map(|p| {
        let p = p.as_array().context("profile coordinate pair")?;
        Ok(v2(p[0].as_f64().context("profile x")?, p[1].as_f64().context("profile y")?))
    }).collect::<Result<Vec<_>>>()?;
    let length = f(row, "length")?;
    plane.offset(-length / 2.0).extrude(&Profile::polygon(&points), length)
}

struct Stock<'a> {
    assets: &'a Value,
    models: HashMap<String, Solid>,
    previous: Option<(String, u64, Solid)>,
    z: f64,
}
impl Stock<'_> {
    fn read(&mut self, key: &str) -> Result<Solid> {
        if let Some(s) = self.models.get(key) { return Ok(s.clone()); }
        let path = self.assets[key].as_str().context("stock model path")?;
        let model = import::model(path)?;
        ensure!(model.len() == 1, "one stock profile body");
        let solid = model[0].solid.simplified()?;
        if key.starts_with("dock-") { self.models.insert(key.to_owned(), solid.clone()); }
        Ok(solid)
    }
    fn body(&mut self, key: &str, height: f64) -> Result<Solid> {
        if let Some((old_key, old_height, solid)) = &self.previous {
            if old_key == key && *old_height == height.to_bits() { return Ok(solid.clone()); }
        }
        self.previous = None;
        let solid = extended(&self.read(key)?, self.z, height)?;
        self.previous = Some((key.to_owned(), height.to_bits(), solid.clone()));
        Ok(solid)
    }
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let color = Some(n.color("color")?);
    let limits = point(n.get("limits")?)?;
    let mut stock = Stock { assets: n.get("assets")?, models: HashMap::new(), previous: None, z: n.f("extension_z")? };
    let mut reel_cradle = None;
    for row in n.get("holders")?.as_array().context("holders")? {
        let name = row["name"].as_str().context("holder name")?;
        let kind = row["kind"].as_str().context("holder kind")?;
        let mut solid = if kind == "spacer" { prism(&row["prism"])? } else {
            stock.body(row["stock"].as_str().context("holder stock")?, f(row,"height_delta")?)?
        };
        let mut cutters = Vec::new();
        for cut in row["cuts"].as_array().context("holder cuts")? {
            cutters.push(if cut["kind"] == "bore" {
                Solid::cylinder(point(&cut["origin"])?, V3::Z, f(cut,"diameter")? / 2.0, f(cut,"height")?)?
            } else { prism(cut)? });
        }
        if !cutters.is_empty() { solid = solid.cut_all(&cutters)?; }
        ensure!(solid.components().len() == 1, "{name}: expected one solid");
        let size = solid.bounds().size();
        ensure!(size.x <= limits.x+1e-6 && size.y <= limits.y+1e-6 && size.z <= limits.z+1e-6, "{name}: exceeds the printer envelope");
        let mut seating = None;
        if !row["seat"].is_null() {
            let seat = &row["seat"];
            let plate = stock.read(seat["dock"].as_str().context("dock stock")?)?;
            let placed = solid.translate(V3::Z * f(seat,"z")?);
            let overlap = plate.intersect(&placed)?.volume();
            let (a,b) = (point(&seat["plate_point"])?, point(&seat["body_point"])?);
            let gap_bound = plate.face_near(a).context("dock surface")?.1 + (a-b).norm()
                + placed.face_near(b).context("holder seating surface")?.1;
            ensure!(overlap <= n.f("max_overlap")?, "{name}: {overlap} mm3 interface overlap");
            ensure!(gap_bound <= n.f("max_gap")?, "{name}: {gap_bound} mm interface gap bound");
            seating = Some((overlap,gap_bound));
        }
        if name == "reel-cradle" { reel_cradle = Some(solid.clone()); }
        let mut said = write_part(&out, name, &[Body { name, color, solid: &solid }])?;
        if let Some((overlap,gap)) = seating {
            said["bodies"][0]["dock_overlap_mm3"] = overlap.into();
            said["bodies"][0]["dock_gap_upper_bound_mm"] = gap.into();
        }
        println!("{said}");
    }
    let mut witness = vec![("reel-cradle".to_owned(), color, reel_cradle.context("reel cradle")?)];
    let grey = Some(n.color("witness_color")?);
    for row in n.get("reels")?.as_array().context("witness reels")? {
        let origin = point(&row["origin"])?;
        let width = f(row,"width")?;
        let reel = Solid::cylinder(origin - V3::X * width / 2.0, V3::X, f(row,"diameter")? / 2.0, width)?;
        witness.push((row["name"].as_str().context("reel name")?.to_owned(), grey, reel));
    }
    let bodies = witness.iter().map(|(name,color,solid)| Body { name, color:*color, solid }).collect::<Vec<_>>();
    println!("{}",write_shown(&out,"reel-cradle-witness",&bodies)?);
    Ok(())
}
