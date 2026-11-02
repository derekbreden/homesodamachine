//! The complete production display head and cover, shortened only beyond the head.
use anyhow::{Context, Result, ensure};
use hsm_kernel::part::{Numbers, args, write_shown};
use hsm_kernel::write::PrintOutput;
use hsm_kernel::*;
use std::collections::{BTreeMap, BTreeSet};
use std::f64::consts::FRAC_PI_2;

fn point(values: &[f64]) -> Result<V3> {
    ensure!(values.len() == 3, "a coordinate triple is required");
    Ok(v3(values[0], values[1], values[2]))
}

fn outline(row: &[f64]) -> Result<LoftSection> {
    ensure!(row.len() == 5, "an outline has width, length, radius, height and centre");
    let (w, l, r, z, centre) = (row[0], row[1], row[2], row[3], row[4]);
    let (h, a, b) = (w / 2.0, centre - l / 2.0, centre + l / 2.0);
    let at = |x, y| v3(x, y, z);
    let line = |a, b| LoftEdge::Line { a, b };
    let arc = |c, x: V3, y: V3| LoftEdge::Conic { c, x: x * r, y: y * r, t0: 0.0, t1: FRAC_PI_2 };
    Ok(LoftSection::new(vec![
        line(at(-h+r, a), at(h-r, a)),
        arc(at(h-r, a+r), -V3::Y, V3::X),
        line(at(h, a+r), at(h, b-r)),
        arc(at(h-r, b-r), V3::X, V3::Y),
        line(at(h-r, b), at(-h+r, b)),
        arc(at(-h+r, b-r), V3::Y, -V3::X),
        line(at(-h, b-r), at(-h, a+r)),
        arc(at(-h+r, a+r), -V3::X, -V3::Y),
    ]))
}

// The three authored shroud sections produce a quadratic along the loft.
// The midpoint of its rear straight edge carries the maximum local S.
fn head_end(n: &Numbers) -> Result<f64> {
    let sections = n.get("head_outline_rows")?.as_array().context("outline rows")?.iter()
        .map(|row| {
            let values = row.as_array().context("outline row")?.iter()
                .map(|v| v.as_f64().context("outline coordinate")).collect::<Result<Vec<_>>>()?;
            outline(&values)
        }).collect::<Result<Vec<_>>>()?;
    let surface = SmoothLoft::new(&compatible(&sections)?)?;
    let (y0, ym, y1) = (surface.at(4.5, 0.0).y, surface.at(4.5, 0.5).y, surface.at(4.5, 1.0).y);
    let a = 2.0 * (y1 + y0 - 2.0 * ym);
    let b = y1 - y0 - a;
    let mut end = y0.max(y1);
    if a < 0.0 {
        let at = -b / (2.0 * a);
        if at > 0.0 && at < 1.0 { end = end.max(surface.at(4.5, at).y); }
    }
    Ok(end.min(n.f("head_clip_s")?).max(n.f("pad_end_s")?).max(n.f("lip_end_s")?))
}

fn region(frame: &Plane, end: f64) -> Solid {
    Solid::cuboid(v3(-100.0, -5.0, -150.0), v3(100.0, end, 100.0))
        .placed(&Plane::XY, frame)
}

fn printed(solid: &Solid, angle: f64) -> (Solid, V3) {
    let turned = solid.rotate(V3::ZERO, V3::X, angle);
    let b = turned.bounds();
    let shift = v3(-(b.min.x + b.max.x) / 2.0, -(b.min.y + b.max.y) / 2.0, -b.min.z);
    (turned.translate(shift), shift)
}

// Use the STL reader's f32 weld before removing collapsed triangles. A straight
// edge can then have a vertex on just one side; split its opposite triangle at
// that existing vertex so both sides retain the same surface and face record.
fn print_surface(solid: &Solid) -> Result<Solid> {
    let simple = solid.simplified()?;
    let mut vertices = Vec::new();
    let mut welded = BTreeMap::new();
    let ids = simple.verts().iter().map(|p| {
        let p = v3(p.x as f32 as f64, p.y as f32 as f64, p.z as f32 as f64);
        let key = [p.x, p.y, p.z].map(|v| (v * 1e8).round_ties_even() as i64);
        *welded.entry(key).or_insert_with(|| {
            vertices.push(p);
            vertices.len() as u32 - 1
        })
    }).collect::<Vec<_>>();
    let mut triangles = Vec::new();
    let mut records = Vec::new();
    for (t, &face) in simple.tris().iter().zip(simple.face_of()) {
        let t = t.map(|i| ids[i as usize]);
        let [a, b, c] = t.map(|i| vertices[i as usize]);
        if (b - a).cross(c - a).norm2() > 0.0 {
            triangles.push(t);
            records.push(face);
        }
    }
    loop {
        let mut edges = BTreeMap::new();
        for (i, t) in triangles.iter().enumerate() {
            for j in 0..3 {
                let (a, b) = (t[j], t[(j + 1) % 3]);
                edges.entry((a.min(b), a.max(b))).or_insert_with(Vec::new).push((i, j));
            }
        }
        let boundary = edges.iter().filter(|(_, uses)| uses.len() == 1).collect::<Vec<_>>();
        let corners = boundary.iter().flat_map(|entry| [entry.0.0, entry.0.1]).collect::<BTreeSet<_>>();
        let mut split = None;
        'find: for (&(a, b), uses) in boundary {
            let start = vertices[a as usize];
            let edge = vertices[b as usize] - start;
            for &v in &corners {
                if v == a || v == b { continue; }
                let along = vertices[v as usize] - start;
                let t = along.dot(edge) / edge.norm2();
                if t > 0.0 && t < 1.0 && along.cross(edge).norm2() <= 1e-16 * edge.norm2() {
                    split = Some((uses[0].0, uses[0].1, v));
                    break 'find;
                }
            }
        }
        let Some((i, j, v)) = split else { break; };
        let t = triangles[i];
        let (a, b, c) = (t[j], t[(j + 1) % 3], t[(j + 2) % 3]);
        triangles[i] = [a, v, c];
        triangles.push([v, b, c]);
        records.push(records[i]);
    }
    Solid::from_mesh(&vertices, &triangles, &records, simple.faces())
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let frame = Plane::new(point(&n.list("origin")?)?, V3::X, point(&n.list("normal")?)?)?;
    let head = head_end(&n)?;
    let end = head.max(n.f("ribbon_start_s")?) + n.f("neck_stub")?;
    let clip = region(&frame, end);
    let tip_models = import::model(n.text("tip_model")?)?;
    ensure!(tip_models.len() == 1, "the production tip has one body");
    let tip = &tip_models[0].solid;
    let housing = tip.intersect(&clip)?;
    let witness = tip.intersect(&region(&frame, head + 1.0))?;
    let missing = witness.cut(&housing)?.volume();
    ensure!(missing <= 1e-5, "the trial removes {missing} mm3 from the complete head");
    let cover_models = import::model(n.text("cover_model")?)?;
    ensure!(cover_models.len() == 1, "the production printable cover has one body");
    let cover = &cover_models[0].solid;
    let black = Some(n.color("black")?);
    for (name, solid, angle) in [
        ("display-trial-housing", &housing, n.f("housing_angle")?),
        ("display-trial-cover", cover, n.f("cover_angle")?),
    ] {
        ensure!(solid.components().len() == 1, "{name} is one closed solid");
        let (print, shift) = printed(solid, angle);
        let fine = [Body { name, color: black, solid: &print }];
        let mut said = write_shown(&out, name, &fine)?;
        let filed = print_surface(&print)?;
        let actual = PrintOutput::new(&[Body { name, color: black, solid: &filed }]);
        let stl = format!("{name}.stl");
        std::fs::write(out.join(&stl), actual.stl_bytes())?;
        std::fs::write(out.join(format!("{name}.step.npz")), actual.model_bytes(&fine, &stl, None)?)?;
        said["files"].as_array_mut().unwrap().push(stl.into());
        said["bodies"][0]["source_translation_mm"] = vec![shift.x, shift.y, shift.z].into();
        if name == "display-trial-housing" {
            let body = &mut said["bodies"][0];
            body["complete_head_end_s_mm"] = head.into();
            body["neck_cut_s_mm"] = end.into();
            body["missing_head_material_mm3"] = missing.into();
        }
        println!("{said}");
    }

    let seated = import::model(n.text("seated_model")?)?;
    ensure!(seated.len() == 1, "the seated cover has one body");
    let mut context = vec![
        ("trial_housing".to_owned(), black, housing),
        ("trial_cover_seated".to_owned(), black, seated[0].solid.clone()),
    ];
    let selected = n.get("context")?.as_array().context("context bodies")?;
    let mut found = std::collections::HashMap::new();
    import::visit_model(n.text("assembly_model")?, |_, body| {
        for row in selected {
            if row["source"].as_str() != Some(body.name.as_str()) { continue; }
            let name = row["name"].as_str().context("context body name")?.to_owned();
            let color = Some(n.color(row["color"].as_str().context("context color")?)?);
            let solid = if row["clip"].as_bool().unwrap_or(false) { body.solid.intersect(&clip)? } else { body.solid.clone() };
            found.insert(name, (color, solid));
        }
        Ok(())
    })?;
    for row in selected {
        let name = row["name"].as_str().context("context body name")?;
        let (color, solid) = found.remove(name).context("the fixture context body was found")?;
        context.push((name.to_owned(), color, solid));
    }
    ensure!(context.len() == selected.len() + 2, "all fixture context bodies were found");
    let shown = context.iter().map(|(name, color, solid)| Body { name, color: *color, solid }).collect::<Vec<_>>();
    println!("{}", write_shown(&out, "faucet-display-fit-trial", &shown)?);
    Ok(())
}
