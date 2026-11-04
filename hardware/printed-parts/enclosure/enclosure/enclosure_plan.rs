//! Enclosure-private numerical construction plan, releasing each last-used intermediate.
#[path = "enclosure_structure.rs"]
#[allow(dead_code)]
mod structure;
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::part::Numbers;
use hsm_kernel::*;
use manifold_csg::Manifold;
use serde_json::Value;
use std::f64::consts::PI;
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

fn stationed_cylinder(v: &Value) -> Result<Solid> {
    let c = point(&v["centre"])?;
    let r = f(v, "radius")?;
    let mut angles = array(&v["stations"])?;
    angles.extend([0., PI / 2., PI, 3. * PI / 2.]);
    for a in &mut angles {
        *a = a.rem_euclid(2. * PI);
    }
    angles.sort_by(f64::total_cmp);
    angles.dedup_by(|a, b| (*a - *b).abs() < 1e-12);
    angles.push(2. * PI);
    let at = |a: f64| c + v2(r * math::cos(a), r * math::sin(a));
    let mut profile = Pen::new(at(0.));
    for pair in angles.windows(2) {
        profile = profile.arc_through(at((pair[0] + pair[1]) / 2.), at(pair[1]))?;
    }
    extruded(v, profile.close()?)
}

fn handhold_cutter(v: &Value) -> Result<Solid> {
    let (lo, hi) = box_corners(&v["box"])?;
    let outline = Loop::polygon(&[
        v2(lo.y, lo.z),
        v2(hi.y, lo.z),
        v2(hi.y, hi.z),
        v2(lo.y, hi.z),
    ])
    .fillet_corners(&[1, 2], f(v, "radius")?)?;
    Plane::YZ
        .at(v3(lo.x, 0.0, 0.0))
        .extrude(&Profile::new(outline), hi.x - lo.x)
}

// The handhold's native mesh loft uses GCPnts_TangentialDeflection on its ellipses.
// Preserve its adaptive stations (including the adjusted penultimate point) before
// ruling adjacent sections. OCCT 7.8.1 algorithm reference:
// https://github.com/Open-Cascade-SAS/OCCT/blob/V7_8_1/src/GCPnts/GCPnts_TangentialDeflection.cxx
fn ellipse_stations(edge: LoftEdge) -> Result<Vec<f64>> {
    let LoftEdge::Conic { c, x, y, t0, t1 } = edge else {
        return Ok(vec![0.0, 1.0]);
    };
    let first = t0.min(t1);
    let last = t0.max(t1);
    let at = |u: f64| c + x * math::cos(u) + y * math::sin(u);
    let step = |u: f64| {
        let tangent = x * (-math::sin(u)) + y * math::cos(u);
        let second = x * (-math::cos(u)) - y * math::sin(u);
        (8.0 * LINEAR / (second.cross(tangent).norm() / tangent.norm())).sqrt()
    };
    let mut du = step(first).min((last - first) / 3.0);
    let mut saved = du;
    let mut u1 = first;
    let mut u2 = first;
    let mut previous = at(first);
    let mut marked = vec![first];
    let mut check_saved = false;
    let mut more = true;
    let mut guard = 0;
    while more {
        guard += 1;
        ensure!(guard < 100000, "handhold ellipse station convergence");
        u2 += du;
        if u2 >= last {
            u2 = last;
            du = u2 - u1;
            saved = du;
        }
        let mut current = at(u2);
        let mut large = false;
        let mut small = false;
        let (fcoef, acoef) = loop {
            let mid = (u1 + u2) * 0.5;
            let p = at(mid);
            let chord = current - previous;
            let half = p - previous;
            let fcoef = if chord.norm() > 1e-7 {
                chord.cross(half).norm() / (chord.norm() * LINEAR)
            } else {
                0.0
            };
            let last_half = current - p;
            let acoef = if last_half.norm() > 1e-7 && half.norm() > 1e-7 {
                last_half.cross(half).norm() / (last_half.norm() * half.norm() * (ANGULAR / 2.0))
            } else {
                0.0
            };
            let coef = fcoef.max(acoef);
            if check_saved && coef < 0.55 {
                check_saved = false;
                du = saved;
                u2 = (u1 + du).min(last);
                current = at(u2);
                continue;
            }
            if coef <= 1.0 {
                if (last - u2).abs() < 1e-9 {
                    marked.push(last);
                    more = false;
                    break (fcoef, acoef);
                }
                if coef >= 0.55 || large {
                    marked.push(u2);
                    previous = current;
                    check_saved = true;
                    break (fcoef, acoef);
                }
                if small {
                    previous = current;
                    break (fcoef, acoef);
                }
                small = true;
                du += ((u2 - u1) * (1.0 - coef)).min(du / 3.0);
                u2 = (u1 + du).min(last);
                current = at(u2);
            } else if coef >= 1.5 {
                if (previous - at(*marked.last().unwrap())).norm() > 1e-7 {
                    marked.push(u1);
                }
                u2 = mid;
                du = u2 - u1;
                current = p;
            } else {
                du *= 0.9;
                u2 = u1 + du;
                current = at(u2);
                large = true;
            }
        };
        du = u2 - u1;
        if more {
            if u1 > first {
                du = if fcoef > acoef {
                    step(u2)
                } else {
                    (du + (du - saved) * (du / saved)).clamp(0.75 * saved, 1.5 * saved)
                };
            }
            if du < 1e-9 {
                du = last - u2;
                if du < 1e-9 {
                    marked.push(last);
                    more = false;
                } else if du / 3.0 > 1e-9 {
                    du /= 3.0;
                }
            }
            u1 = u2;
            saved = du;
        }
    }
    if marked.len() >= 3 {
        let n = marked.len();
        marked[n - 2] = (last + marked[n - 3]) * 0.5;
    }
    if t0 > t1 {
        marked.reverse();
    }
    Ok(marked.into_iter().map(|u| (u - t0) / (t1 - t0)).collect())
}

fn handhold_loft(sections: &[LoftSection]) -> Result<Solid> {
    let sections = compatible(sections)?;
    let mut regions = vec![];
    for section in &sections {
        let mut points = vec![];
        let mut segment = vec![];
        let mut curves = vec![];
        for (k, &edge) in section.edges.iter().enumerate() {
            let stations = match edge {
                LoftEdge::Line { .. } => vec![0.0, 1.0],
                _ => ellipse_stations(edge)?,
            };
            for &t in &stations[..stations.len() - 1] {
                points.push(edge.at(t));
                segment.push(k as u32);
            }
            curves.push(match edge {
                LoftEdge::Line { .. } => Curve::Line,
                _ => Curve::Free("ELLIPSE"),
            });
        }
        regions.push(Region {
            loops: vec![profile::RLoop {
                pts: points,
                seg: segment,
            }],
            curves,
        });
    }
    // meshcad.sweep.loft rules each pair even when its caller says ruled=False.
    Solid::loft(&regions)
}

fn handhold_air(v: &Value) -> Result<Solid> {
    let (bed, roof, crown) = (f(v, "bed")?, f(v, "roof")?, f(v, "crown")?);
    let y = array(&v["y"])?;
    let (corner, radius, depth) = (f(v, "corner")?, f(v, "radius")?, f(v, "depth")?);
    let slope = f(v, "slope")?;
    let height = radius - radius * slope / (1.0_f64 + slope * slope).sqrt();
    let foot = radius - radius / (1.0_f64 + slope * slope).sqrt() + slope * height;
    let tangent_depth = foot - slope * height;
    let mut depths: Vec<f64> = (0..=90)
        .step_by(2)
        .map(|a| radius * (1.0 - math::sin(math::radians(a as f64))))
        .collect();
    depths.extend([0.0, radius, foot, tangent_depth, foot - 0.01, foot + 0.01]);
    depths.sort_by(f64::total_cmp);
    depths.dedup_by(|a, b| *a == *b);
    let (left, right, zl) = (y[0] + corner, y[1] - corner, roof - corner);
    let section = |d: f64, ceiling: bool| -> LoftSection {
        let side = radius - (radius * radius - (radius - d).powi(2)).max(0.0).sqrt();
        let top = if d <= tangent_depth {
            side
        } else {
            ((foot - d) / slope).max(0.0)
        };
        let at = |y, z| v3(d, y, z);
        let line = |a, b| LoftEdge::Line { a, b };
        let arc = |cy, a0, a1| LoftEdge::Conic {
            c: at(cy, zl),
            x: v3(0.0, corner + side, 0.0),
            y: v3(0.0, 0.0, corner + top),
            t0: math::radians(a0),
            t1: math::radians(a1),
        };
        let low = bed - 1.0;
        let mut edges = vec![
            line(at(y[0] - side, low), at(y[1] + side, low)),
            line(at(y[1] + side, low), at(y[1] + side, zl)),
            arc(right, 0.0, 90.0),
        ];
        if ceiling {
            edges.push(line(at(right, roof + top), at(left, roof + top)));
        } else {
            edges.extend([
                line(at(right, roof), at(right, zl)),
                line(at(right, zl), at(left, zl)),
                line(at(left, zl), at(left, roof)),
            ]);
        }
        edges.extend([
            arc(left, 90.0, 180.0),
            line(at(y[0] - side, zl), at(y[0] - side, low)),
        ]);
        LoftSection::new(edges)
    };
    let with_roof: Vec<_> = depths
        .iter()
        .filter(|&&d| d <= foot)
        .map(|&d| section(d, true))
        .collect();
    let returns: Vec<_> = depths
        .iter()
        .filter(|&&d| d >= foot)
        .map(|&d| section(d, false))
        .collect();
    let roof_air = handhold_loft(&with_roof)?;
    let side_air = handhold_loft(&returns)?;
    let basic = handhold_cutter(&serde_json::json!({
        "box":[-1.0,f(v,"cutter_depth")?,y[0],y[1],bed-1.0,roof],"radius":corner}))?;
    // _handhold_finish_air is the blank's share of the ordinary opening and both rim lofts.
    let end = f(v, "end_stock")?;
    let blank = Solid::cuboid(v3(0.0, y[0] - end, bed), v3(depth, y[1] + end, crown));
    basic.union(&roof_air)?.union(&side_air)?.intersect(&blank)
}


fn flank_vents(v: &Value, stock: &Solid, cutters: &[&Solid]) -> Result<Solid> {
    let columns = v["columns"].as_array().context("vent columns")?;
    let courses = v["courses"]
        .as_array()
        .context("vent courses")?
        .iter()
        .map(array)
        .collect::<Result<Vec<_>>>()?;
    let clearance = f(v, "clearance")?;
    let tolerance = f(v, "tolerance")?;
    let minimum = v["island_min"].as_u64().context("vent island count")? as usize;
    let sides = columns
        .iter()
        .map(|column| f(column, "side"))
        .collect::<Result<Vec<_>>>()?;
    let mut present = Vec::new();
    for column in columns {
        let (lo, hi) = box_corners(&column["probe"])?;
        let occupied = stock
            .intersect(&Solid::cuboid(lo, hi))?
            .components()
            .iter()
            .map(|component| {
                let bounds = component.bounds();
                (bounds.min.z - clearance, bounds.max.z + clearance)
            })
            .collect::<Vec<_>>();
        present.push(
            courses
                .iter()
                .map(|course| {
                    !occupied
                        .iter()
                        .any(|&(lo, hi)| course[0].max(lo) < course[1].min(hi) - tolerance)
                })
                .collect::<Vec<_>>(),
        );
    }
    let mut selected = Vec::new();
    for (i, column) in columns.iter().enumerate() {
        let tools = column["cutters"].as_array().context("vent cutters")?;
        ensure!(tools.len() == courses.len(), "vent course cutters");
        for k in 0..courses.len() {
            let neighbours = usize::from(i > 0 && sides[i - 1] == sides[i] && present[i - 1][k])
                + usize::from(
                    i + 1 < columns.len() && sides[i + 1] == sides[i] && present[i + 1][k],
                );
            if present[i][k] && neighbours >= minimum.saturating_sub(1) {
                let index = tools[k].as_u64().context("vent cutter index")? as usize;
                selected.push(cutters[index].clone());
            }
        }
    }
    if selected.is_empty() {
        return Ok(stock.clone());
    }
    stock.cut(&Solid::compose(&selected))
}

fn bezier_prism(v: &Value) -> Result<Solid> {
    let segments = v["segments"].as_array().context("line/cubic profile")?;
    let mut edges = Vec::new();
    for segment in segments {
        if let Some(line) = segment.get("line") {
            edges.push(Seg::Line { a: point(&line[0])?, b: point(&line[1])? });
        } else {
            let cubic = &segment["cubic"];
            edges.push(Seg::Cubic {
                a: point(&cubic[0])?, c1: point(&cubic[1])?,
                c2: point(&cubic[2])?, b: point(&cubic[3])?,
            });
        }
    }
    extruded(v, Loop::new(edges)?)
}

/// The native pump skirt's explicit, planar ruled correspondence. Repeated
/// points are collapsed transition vertices, not epsilon edges.
fn ruled_stack(v: &Value) -> Result<Solid> {
    let sections = v["sections"].as_array().context("ruled sections")?
        .iter().map(|row| -> Result<Vec<V3>> {
            row.as_array().context("ruled section")?.iter().map(vector).collect()
        }).collect::<Result<Vec<_>>>()?;
    ensure!(sections.len() >= 2, "a ruled stack needs two sections");
    let n = sections[0].len();
    ensure!(n >= 3 && sections.iter().all(|row| row.len() == n), "ruled correspondence count");
    let rise = sections.last().unwrap()[0].z-sections[0][0].z;
    ensure!(rise != 0.0, "a ruled stack needs distinct end planes");
    let area: f64 = (0..n).map(|i| {
        let (a,b) = (sections[0][i], sections[0][(i+1)%n]);
        a.x*b.y-b.x*a.y
    }).sum();
    let flip_side = (rise > 0.0) != (area < 0.0);
    let verts: Vec<_> = sections.iter().flatten().copied().collect();
    let mut tris = Vec::new();
    let mut faces = Vec::new();
    let mut face_of = Vec::new();
    let source = &v["source"];
    let src = hsm_kernel::face::record_src(&format!("{}:{}",
        source["path"].as_str().context("ruled source path")?,
        source["line"].as_u64().context("ruled source line")?));
    for (i, sense) in [(0, -rise.signum()), (sections.len()-1, rise.signum())] {
        let row = &sections[i];
        let flat = row.iter().map(|p|v2(p.x,p.y)).collect();
        let cap = hsm_kernel::triangulate::triangulate(&[flat])?;
        let face = faces.len() as u32;
        faces.push(Face::new(Surface::Plane { p: row[0], n: V3::Z*sense }, "ruled skirt cap", src));
        for mut t in cap {
            t.iter_mut().for_each(|k|*k += (i*n) as u32);
            if sense < 0.0 { t.swap(1,2); }
            tris.push(t); face_of.push(face);
        }
    }
    for i in 0..sections.len()-1 {
        for k in 0..n {
            let next = (k+1)%n;
            let ids = [(i*n+k) as u32,((i+1)*n+k) as u32,
                       ((i+1)*n+next) as u32,(i*n+next) as u32];
            let mut triangles = Vec::new();
            for mut t in [[ids[0],ids[1],ids[2]], [ids[0],ids[2],ids[3]]] {
                if flip_side { t.swap(1,2); }
                let (a,b,c) = (verts[t[0] as usize],verts[t[1] as usize],verts[t[2] as usize]);
                if (b-a).cross(c-a).norm() > 1e-12 { triangles.push(t); }
            }
            if triangles.is_empty() { continue; }
            let t = triangles[0];
            let (a,b,c) = (verts[t[0] as usize],verts[t[1] as usize],verts[t[2] as usize]);
            let normal = (b-a).cross(c-a).unit();
            ensure!(ids.iter().all(|&j|(verts[j as usize]-a).dot(normal).abs() < 1e-7),
                    "the native ruled skirt face is no longer planar");
            let face = faces.len() as u32;
            faces.push(Face::new(Surface::Plane { p:a, n:normal }, "ruled skirt", src));
            for t in triangles { tris.push(t); face_of.push(face); }
        }
    }
    Solid::from_mesh(&verts,&tris,&face_of,&faces)
}
pub(crate) fn build(n: &Numbers) -> Result<Solid> {
    let recipe = n.get("panel")?;
    let nodes = recipe["nodes"].as_array().context("panel nodes")?;
    let shared = recipe::Shared::new(nodes)?;
    let result = shared.aliases[recipe["result"].as_u64().context("panel result")? as usize];
    let mut users = vec![0_usize; nodes.len()];
    users[result] += 1;
    for (i, inputs) in shared.inputs.iter().enumerate() {
        if shared.aliases[i] != i { continue; }
        for &input in inputs {
            users[input] += 1;
        }
    }
    let mut live: Vec<Option<Solid>> = vec![None; nodes.len()];
    for (i, v) in nodes.iter().enumerate() {
        if shared.aliases[i] != i { continue; }
        let inputs = &shared.inputs[i];
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
                    if v["stations"].is_array() {
                        return stationed_cylinder(v);
                    }
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
                "handhold-cutter" => handhold_cutter(v)?,
                "handhold-finish-air" => handhold_air(v)?,
                "flank-vents" => {
                    let tools = (1..inputs.len()).map(input).collect::<Vec<_>>();
                    flank_vents(v,input(0),&tools)?
                }
                "bezier-prism" => bezier_prism(v)?,
                "ruled-stack" => ruled_stack(v)?,
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
        for &k in inputs {
            users[k] -= 1;
            if users[k] == 0 {
                live[k] = None;
            }
        }
    }
    live[result].take().context("finished enclosure plan")
}

#[path = "enclosure_recipe.rs"]
mod recipe;

pub(crate) fn write_print_stl(path: &std::path::Path, shape: &Manifold) -> Result<()> {
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
