//! The back-top structural panel, from enclosure-private placed construction records.
#[path = "enclosure_skin.rs"]
#[allow(dead_code)]
mod skin;
#[path = "enclosure_structure.rs"]
#[allow(dead_code)]
mod structure;
use anyhow::{bail, ensure, Context, Result};
use hsm_kernel::part::{args, write_shown, Numbers};
use hsm_kernel::*;
use manifold_csg::Manifold;
use serde_json::Value;
use std::io::Write;

fn f(v: &Value, key: &str) -> Result<f64> {
    v[key].as_f64().with_context(|| format!("missing {key}"))
}
fn array(v: &Value) -> Result<Vec<f64>> {
    v.as_array()
        .context("array")?
        .iter()
        .map(|x| x.as_f64().context("number"))
        .collect()
}
fn vector(v: &Value) -> Result<V3> {
    let a = array(v)?;
    ensure!(a.len() == 3, "three-vector");
    Ok(v3(a[0], a[1], a[2]))
}
fn point(v: &Value) -> Result<V2> {
    let a = array(v)?;
    ensure!(a.len() == 2, "two-vector");
    Ok(v2(a[0], a[1]))
}
fn points(v: &Value) -> Result<Vec<V2>> {
    v.as_array()
        .context("profile points")?
        .iter()
        .map(point)
        .collect()
}
fn box_corners(v: &Value) -> Result<(V3, V3)> {
    let b = array(v)?;
    ensure!(b.len() == 6, "six box limits");
    Ok((v3(b[0], b[2], b[4]), v3(b[1], b[3], b[5])))
}
fn axis(v: &Value) -> Result<usize> {
    let k = v["axis"].as_u64().context("axis")? as usize;
    ensure!(k < 3, "principal axis");
    Ok(k)
}
fn extruded(v: &Value, outline: Loop) -> Result<Solid> {
    let z = array(&v["span"])?;
    let (plane, distance) = match axis(v)? {
        0 => (Plane::YZ.at(v3(z[0], 0., 0.)), z[1] - z[0]),
        1 => (Plane::XZ.at(v3(0., z[0], 0.)), -(z[1] - z[0])),
        _ => (Plane::XY.at(v3(0., 0., z[0])), z[1] - z[0]),
    };
    plane.extrude(&Profile::new(outline), distance)
}
fn prism(v: &Value, rounded: bool) -> Result<Solid> {
    let points = points(&v["section"])?;
    let mut outline = Loop::polygon(&points);
    if rounded && f(v, "radius")? > 0. {
        // Private records name vertices; the kernel names the segment ending there.
        let corners = v["corners"]
            .as_array()
            .context("rounded vertices")?
            .iter()
            .map(|i| {
                i.as_u64()
                    .map(|k| (k as usize + points.len() - 1) % points.len())
                    .context("vertex index")
            })
            .collect::<Result<Vec<_>>>()?;
        outline = outline.fillet_corners(&corners, f(v, "radius")?)?;
    }
    if let Some(offset) = v["offset"].as_f64() {
        outline = outline.ccw().offset(offset, true)?;
    }
    extruded(v, outline)
}
fn arc_prism(v: &Value) -> Result<Solid> {
    let mut pen = Pen::new(point(&v["start"])?);
    for segment in v["segments"].as_array().context("arc profile")? {
        pen = if segment.get("arc").is_some() {
            pen.arc_through(point(&segment["arc"][0])?, point(&segment["arc"][1])?)?
        } else {
            pen.line_to(point(&segment["line"])?)
        };
    }
    extruded(v, pen.close()?)
}
fn flange(v: &Value) -> Result<Solid> {
    let p = &v["landmarks"];
    let a = point(&p["shoulder"])?;
    let m = point(&p["round_mid"])?;
    let q = point(&p["tangent_start"])?;
    let t = point(&p["ear_tangent"])?;
    let nose = point(&p["nose"])?;
    let reflect = |v: V2, x: f64, y: f64| v2(v.x * x, v.y * y);
    let outline = Pen::new(v2(-a.x, a.y))
        .line_to(a)
        .arc_through(m, q)?
        .line_to(t)
        .arc_through(nose, reflect(t, 1., -1.))?
        .line_to(reflect(q, 1., -1.))
        .arc_through(reflect(m, 1., -1.), reflect(a, 1., -1.))?
        .line_to(-a)
        .arc_through(-m, -q)?
        .line_to(-t)
        .arc_through(-nose, reflect(t, -1., 1.))?
        .line_to(reflect(q, -1., 1.))
        .arc_through(reflect(m, -1., 1.), reflect(a, -1., 1.))?
        .close()?;
    let outline = outline.ccw().offset(f(v, "clearance")?, true)?;
    let z = array(&v["span"])?;
    Plane::XZ
        .at(v3(0., z[0], 0.))
        .extrude(&Profile::new(outline), -(z[1] - z[0]))
}
fn turned(v: &Value) -> Result<Solid> {
    let runs = v["profile"].as_array().context("radial runs")?;
    let mut profile = vec![v2(runs[0][0].as_f64().context("run start")?, 0.)];
    for r in runs {
        let a = array(r)?;
        for p in [v2(a[0], a[2]), v2(a[1], a[2])] {
            if (*profile.last().unwrap() - p).norm() > 1e-9 {
                profile.push(p);
            }
        }
    }
    profile.push(v2(runs.last().unwrap()[1].as_f64().context("run end")?, 0.));
    let c = array(&v["centre"])?;
    Ok(Plane::XY
        .revolve(&Profile::polygon(&profile), 360., V2::ZERO, v2(1., 0.))?
        .rotate(V3::ZERO, V3::Z, 90.)
        .translate(v3(c[0], 0., c[1])))
}
fn radial_profile(v: &Value) -> Result<Solid> {
    let points = points(&v["points"])?;
    let mut profile = vec![v2(points.first().context("radial profile start")?.x, 0.)];
    profile.extend_from_slice(&points);
    profile.push(v2(points.last().context("radial profile end")?.x, 0.));
    Plane::XY.revolve(&Profile::polygon(&profile), 360., V2::ZERO, v2(1., 0.))
}
fn stadium(v: &Value) -> Result<Solid> {
    let (y, z, r) = (f(v, "y")?, f(v, "z")?, f(v, "radius")?);
    let (a, b) = (y - f(v, "fore")?, y + f(v, "aft")?);
    let outline = Pen::new(v2(a, z - r))
        .line_to(v2(b, z - r))
        .arc_through(v2(b + r, z), v2(b, z + r))?
        .line_to(v2(a, z + r))
        .arc_through(v2(a - r, z), v2(a, z - r))?
        .close()?;
    let x = array(&v["span"])?;
    Plane::YZ
        .at(v3(x[0], 0., 0.))
        .extrude(&Profile::new(outline), x[1] - x[0])
}

pub(crate) struct Built {
    solid: Solid,
    receiver: Solid,
}
pub(crate) fn build(n: &Numbers) -> Result<Built> {
    let recipe = n.get("panel")?;
    let nodes = recipe["nodes"].as_array().context("panel nodes")?;
    let result = recipe["result"].as_u64().context("panel result")? as usize;
    let mut users = vec![0_usize; nodes.len()];
    users[result] += 1;
    let receiver = recipe["extras"]["receiver_field"]
        .as_u64()
        .context("receiver field")? as usize;
    users[receiver] += 1;
    for node in nodes {
        for input in node["inputs"].as_array().context("node inputs")? {
            users[input.as_u64().context("input index")? as usize] += 1;
        }
    }
    let mut live: Vec<Option<Solid>> = vec![None; nodes.len()];
    for (i, v) in nodes.iter().enumerate() {
        let inputs = v["inputs"]
            .as_array()
            .context("node inputs")?
            .iter()
            .map(|x| x.as_u64().map(|k| k as usize).context("node index"))
            .collect::<Result<Vec<_>>>()?;
        ensure!(inputs.iter().all(|&k| k < i), "construction order");
        let input = |k: usize| live[inputs[k]].as_ref().expect("referenced solid is live");
        let op = v["op"].as_str().context("node operation")?;
        let shape = (|| -> Result<Solid> {
            Ok(match op {
                "empty" => Solid::empty(),
                "silhouette" => structure::silhouette(n)?,
                "box" => {
                    let (lo, hi) = box_corners(&v["box"])?;
                    Solid::cuboid(lo, hi)
                }
                "rounded-box" => {
                    let (lo, hi) = box_corners(&v["box"])?;
                    Plane::XY
                        .at(v3((lo.x + hi.x) / 2., (lo.y + hi.y) / 2., lo.z))
                        .extrude(
                            &Profile::new(Loop::rounded_rect(
                                V2::ZERO,
                                hi.x - lo.x,
                                hi.y - lo.y,
                                f(v, "radius")?,
                            )?),
                            hi.z - lo.z,
                        )?
                }
                "cylinder" => {
                    let k = axis(v)?;
                    let c = array(&v["centre"])?;
                    let z = array(&v["span"])?;
                    let mut p = [0.; 3];
                    let mut a = [0.; 3];
                    a[k] = 1.;
                    p[k] = z[0];
                    let other: Vec<_> = (0..3).filter(|&j| j != k).collect();
                    p[other[0]] = c[0];
                    p[other[1]] = c[1];
                    Solid::cylinder(V3::from(p), V3::from(a), f(v, "radius")?, z[1] - z[0])?
                }
                "prism" => prism(v, false)?,
                "corner-prism" => prism(v, true)?,
                "arc-prism" => arc_prism(v)?,
                "inlet-flange" => flange(v)?,
                "turned-runs" => turned(v)?,
                "radial-profile" => radial_profile(v)?,
                "stadium-x" => stadium(v)?,
                "union" | "cut" | "intersect" => {
                    let mut s = input(0).clone();
                    for k in 1..inputs.len() {
                        s = match op {
                            "union" => s.union(input(k))?,
                            "cut" => s.cut(input(k))?,
                            _ => s.intersect(input(k))?,
                        };
                    }
                    s
                }
                "translate" => input(0).translate(vector(&v["delta"])?),
                "rotate" => {
                    let origin = vector(&v["origin"])?;
                    input(0).rotate(origin, vector(&v["end"])? - origin, f(v, "angle")?)
                }
                "mirror" => {
                    let mut a = [0.; 3];
                    a[axis(v)?] = 1.;
                    input(0).mirror(V3::ZERO, V3::from(a))
                }
                "placed" => {
                    let r = &v["frame"]["rotation"];
                    let t = vector(&v["frame"]["translation_mm"])?;
                    let column = |k| -> Result<V3> {
                        Ok(v3(
                            r[0][k].as_f64().context("frame x")?,
                            r[1][k].as_f64().context("frame y")?,
                            r[2][k].as_f64().context("frame z")?,
                        ))
                    };
                    input(0).transformed(&Affine::from_columns(
                        column(0)?,
                        column(1)?,
                        column(2)?,
                        t,
                    ))
                }
                _ => bail!("unsupported back-top operation {op}"),
            })
        })()
        .with_context(|| format!("back-top node {i} ({op})"))?;
        live[i] = Some(shape);
        for k in inputs {
            users[k] -= 1;
            if users[k] == 0 {
                live[k] = None;
            }
        }
    }
    Ok(Built {
        solid: live[result]
            .take()
            .context("finished structural back-top")?,
        receiver: live[receiver]
            .take()
            .context("constructed receiver field")?,
    })
}

fn manifold(s: &Solid) -> Result<Manifold> {
    let vertices: Vec<f32> = s
        .verts()
        .iter()
        .flat_map(|p| p.to_array().map(|x| x as f32))
        .collect();
    let triangles: Vec<u32> = s.tris().iter().flatten().copied().collect();
    Ok(Manifold::from_mesh_f32(&vertices, 3, &triangles)?)
}
pub(crate) fn print_surfaces(built: &Built, n: &Numbers) -> Result<(Solid, Solid, [f64; 6])> {
    let o = n.list("outer")?;
    let p = n.get("print")?;
    let proud = built.receiver.intersect(&Solid::cuboid(
        v3(-200., o[3], 0.),
        v3(200., o[3] + 20., 400.),
    ))?;
    ensure!(
        !proud.tris().is_empty(),
        "the accepted nameplate field stands proud"
    );
    let b = proud.bounds();
    let field = [b.min.x, b.max.x, o[3] - 3., o[3] + 1., b.min.z, b.max.z];
    let mut fields = vec![field];
    for bounds in p["raised_bounds"].as_array().context("raised rails")? {
        let a = array(bounds)?;
        ensure!(a.len() == 6, "six land limits");
        fields.push(a.try_into().unwrap());
    }
    let mut smooth = built.solid.clone();
    let mut relief = vec![];
    for b in &fields {
        smooth = smooth.cut(&Solid::cuboid(
            v3(b[0], o[3], b[4]),
            v3(b[1], o[3] + 10., b[5]),
        ))?;
        relief.push(built.solid.intersect(&Solid::cuboid(
            v3(b[0], o[3] - f(p, "embed")?, b[4]),
            v3(b[1], o[3] + 10., b[5]),
        ))?);
    }
    Ok((smooth, Solid::union_all(&relief)?, field))
}
fn printed(built: &Built, n: &Numbers) -> Result<Manifold> {
    let (smooth, relief, field) = print_surfaces(built, n)?;
    let fluted = skin::flute_solid(&smooth.simplified()?, n, &[field])?;
    let joined = fluted.union(&manifold(&relief)?);
    let (v, props, t) = joined.to_mesh_f32();
    Ok(Manifold::from_mesh_f32(&v, props, &t)?)
}
fn print_stl(path: &std::path::Path, shape: &Manifold) -> Result<()> {
    let (v, props, t) = shape.to_mesh_f32();
    let tmp = path.with_file_name(format!(
        ".{}.{}.stl",
        path.file_stem().unwrap().to_string_lossy(),
        std::process::id()
    ));
    let mut out = std::io::BufWriter::new(std::fs::File::create(&tmp)?);
    let mut header = [b' '; 80];
    let title = b"hsm enclosure print surface";
    header[..title.len()].copy_from_slice(title);
    out.write_all(&header)?;
    out.write_all(&(t.len() as u32 / 3).to_le_bytes())?;
    for triangle in t.chunks_exact(3) {
        let points: Vec<_> = triangle
            .iter()
            .map(|&i| {
                let k = i as usize * props;
                v3(v[k] as f64, v[k + 1] as f64, v[k + 2] as f64)
            })
            .collect();
        let normal = (points[1] - points[0]).cross(points[2] - points[0]).unit();
        for value in normal
            .to_array()
            .into_iter()
            .map(|x| x as f32)
            .chain(points.iter().flat_map(|p| p.to_array().map(|x| x as f32)))
        {
            out.write_all(&value.to_le_bytes())?;
        }
        out.write_all(&[0, 0])?;
    }
    out.flush()?;
    drop(out);
    std::fs::rename(tmp, path)?;
    Ok(())
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let built = build(&n)?;
    let mut said = write_shown(
        &out,
        "enclosure-back-top",
        &[Body {
            name: "enclosure-back-top",
            color: Some(n.color("color")?),
            solid: &built.solid,
        }],
    )?;
    if n.get("print").is_ok() {
        let shape = printed(&built, &n)?;
        print_stl(&out.join("enclosure-back-top.stl"), &shape)?;
        said["files"]
            .as_array_mut()
            .context("part files")?
            .push(serde_json::json!("enclosure-back-top.stl"));
        said["print"] = serde_json::json!({"volume":shape.volume(),"triangles":shape.num_tri()});
    }
    println!("{said}");
    Ok(())
}
