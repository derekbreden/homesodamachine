//! Enclosure-private numerical construction plan, releasing each last-used intermediate.
#[path = "enclosure_structure.rs"]
#[allow(dead_code)]
mod structure;
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::part::Numbers;
use hsm_kernel::*;
use serde_json::Value;

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
pub(crate) fn build(n: &Numbers) -> Result<Solid> {
    let recipe = n.get("panel")?;
    let nodes = recipe["nodes"].as_array().context("panel nodes")?;
    let result = recipe["result"].as_u64().context("panel result")? as usize;
    let mut users = vec![0_usize; nodes.len()];
    users[result] += 1;
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
                "cone" => {
                    let k = axis(v)?;
                    let c = array(&v["centre"])?;
                    let z = array(&v["span"])?;
                    let radii = array(&v["radii"])?;
                    let mut p = [0.; 3];
                    let mut a = [0.; 3];
                    a[k] = 1.;
                    p[k] = z[0];
                    let other: Vec<_> = (0..3).filter(|&j| j != k).collect();
                    p[other[0]] = c[0];
                    p[other[1]] = c[1];
                    Solid::cone(V3::from(p), V3::from(a), radii[0], radii[1], z[1] - z[0])?
                }
                "prism" => prism(v, false)?,
                "corner-prism" => prism(v, true)?,
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
                _ => bail!("unsupported enclosure operation {op}"),
            })
        })()
        .with_context(|| format!("enclosure node {i} ({op})"))?;
        live[i] = Some(shape);
        for k in inputs {
            users[k] -= 1;
            if users[k] == 0 {
                live[k] = None;
            }
        }
    }
    live[result].take().context("finished enclosure plan")
}
