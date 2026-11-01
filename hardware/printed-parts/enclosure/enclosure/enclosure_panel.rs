//! The enclosure's structural back-bottom panel from its private Python recipe.
#[path = "enclosure_skin.rs"]
#[allow(dead_code)]
mod skin;
#[path = "enclosure_structure.rs"]
#[allow(dead_code)]
mod structure;
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::part::{Numbers, args, write_shown};
use hsm_kernel::*;
use manifold_csg::Manifold;
use serde_json::Value;
use std::io::Write;

fn f(v: &Value, key: &str) -> Result<f64> {
    v[key]
        .as_f64()
        .with_context(|| format!("missing number {key}"))
}
fn array(v: &Value) -> Result<Vec<f64>> {
    v.as_array()
        .context("numeric array")?
        .iter()
        .map(|x| x.as_f64().context("number in array"))
        .collect()
}
fn vector(v: &Value) -> Result<V3> {
    let a = array(v)?;
    ensure!(a.len() == 3, "three-vector");
    Ok(v3(a[0], a[1], a[2]))
}
fn axis(v: &Value) -> Result<usize> {
    let k = v["axis"].as_u64().context("axis index")? as usize;
    ensure!(k < 3, "axis in 0..3");
    Ok(k)
}
fn box_corners(v: &Value) -> Result<(V3, V3)> {
    let b = array(v)?;
    ensure!(b.len() == 6, "six box limits");
    Ok((v3(b[0], b[2], b[4]), v3(b[1], b[3], b[5])))
}
fn prism(v: &Value) -> Result<Solid> {
    let k = axis(v)?;
    let span = array(&v["span"])?;
    let points = v["section"]
        .as_array()
        .context("prism section")?
        .iter()
        .map(|p| {
            Ok(v2(
                p[0].as_f64().context("profile x")?,
                p[1].as_f64().context("profile y")?,
            ))
        })
        .collect::<Result<Vec<_>>>()?;
    let (plane, distance) = match k {
        0 => (Plane::YZ.at(v3(span[0], 0.0, 0.0)), span[1] - span[0]),
        1 => (Plane::XZ.at(v3(0.0, span[0], 0.0)), -(span[1] - span[0])),
        _ => (Plane::XY.at(v3(0.0, 0.0, span[0])), span[1] - span[0]),
    };
    plane.extrude(&Profile::polygon(&points), distance)
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

fn polynomial_roots(a: f64, b: f64, c: f64) -> Vec<f64> {
    if a.abs() < 1e-14 {
        return if b.abs() < 1e-14 {
            vec![]
        } else {
            vec![-c / b]
        };
    }
    let d = b * b - 4.0 * a * c;
    if d < 0.0 {
        return vec![];
    }
    vec![(-b - d.sqrt()) / (2.0 * a), (-b + d.sqrt()) / (2.0 * a)]
}
fn split_segment(s: Seg, t: f64) -> (Seg, Seg) {
    match s {
        Seg::Quad { a, c, b } => {
            let ac = a.lerp(c, t);
            let cb = c.lerp(b, t);
            let p = ac.lerp(cb, t);
            (Seg::Quad { a, c: ac, b: p }, Seg::Quad { a: p, c: cb, b })
        }
        Seg::Cubic { a, c1, c2, b } => {
            let ac = a.lerp(c1, t);
            let cc = c1.lerp(c2, t);
            let cb = c2.lerp(b, t);
            let p = ac.lerp(cc, t);
            let q = cc.lerp(cb, t);
            let mid = p.lerp(q, t);
            (
                Seg::Cubic {
                    a,
                    c1: ac,
                    c2: p,
                    b: mid,
                },
                Seg::Cubic {
                    a: mid,
                    c1: q,
                    c2: cb,
                    b,
                },
            )
        }
        _ => (s, s),
    }
}
fn extrema(s: Seg, axis: usize) -> Vec<f64> {
    let at = |p: V2| if axis == 0 { p.x } else { p.y };
    let roots = match s {
        Seg::Quad { a, c, b } => polynomial_roots(0.0, at(a) - 2.0 * at(c) + at(b), at(c) - at(a)),
        Seg::Cubic { a, c1, c2, b } => polynomial_roots(
            -at(a) + 3.0 * at(c1) - 3.0 * at(c2) + at(b),
            2.0 * at(a) - 4.0 * at(c1) + 2.0 * at(c2),
            at(c1) - at(a),
        ),
        _ => vec![],
    };
    roots
        .into_iter()
        .filter(|&t| t > 1e-12 && t < 1.0 - 1e-12)
        .collect()
}
fn point(s: Seg, t: f64) -> V2 {
    match s {
        Seg::Line { a, b } => a.lerp(b, t),
        Seg::Quad { a, c, b } => a * (1.0 - t).powi(2) + c * (2.0 * t * (1.0 - t)) + b * t * t,
        Seg::Cubic { a, c1, c2, b } => {
            a * (1.0 - t).powi(3)
                + c1 * (3.0 * t * (1.0 - t).powi(2))
                + c2 * (3.0 * t * t * (1.0 - t))
                + b * t.powi(3)
        }
        _ => s.start(),
    }
}
fn profile_bounds(profiles: &[Profile]) -> (V2, V2) {
    let mut lo = v2(f64::INFINITY, f64::INFINITY);
    let mut hi = -lo;
    for p in profiles {
        for lp in std::iter::once(&p.outer).chain(&p.holes) {
            for &s in &lp.segs {
                for q in [s.start(), s.end()].into_iter().chain(
                    extrema(s, 0)
                        .into_iter()
                        .chain(extrema(s, 1))
                        .map(|t| point(s, t)),
                ) {
                    lo = v2(lo.x.min(q.x), lo.y.min(q.y));
                    hi = v2(hi.x.max(q.x), hi.y.max(q.y));
                }
            }
        }
    }
    (lo, hi)
}
fn split_caps(lp: &Loop) -> Loop {
    let mut segs = vec![];
    for &original in &lp.segs {
        let mut roots = extrema(original, 0);
        roots.sort_by(f64::total_cmp);
        roots.dedup_by(|a, b| (*a - *b).abs() < 1e-12);
        let mut s = original;
        let mut previous = 0.0;
        for t in roots {
            let (a, b) = split_segment(s, (t - previous) / (1.0 - previous));
            segs.push(a);
            s = b;
            previous = t;
        }
        segs.push(s);
    }
    Loop { segs }
}
fn raked(profile: &Profile, depth: f64) -> Result<Solid> {
    let p = Profile {
        outer: split_caps(&profile.outer.ccw()).translated(v2(0.0, depth)),
        holes: profile
            .holes
            .iter()
            .map(|lp| split_caps(&lp.ccw().reversed()).translated(v2(0.0, depth)))
            .collect(),
    };
    let region = p.place(&Plane::XY);
    let level = Solid::extrude(&region, V3::Z, V3::Z * depth)?;
    let bounds = level.bounds();
    let mut stock = vec![level];
    for lp in &region.loops {
        for (i, &a) in lp.pts.iter().enumerate() {
            let b = lp.pts[(i + 1) % lp.pts.len()];
            let normal = (b - a).cross(V3::Z).unit();
            if normal.y >= -1e-9 {
                continue;
            }
            let side = Region::polygon(vec![a, b, b + V3::Z * depth, a + V3::Z * depth]);
            stock.push(Solid::extrude(&side, normal, v3(0.0, -depth, -depth))?);
        }
    }
    let root = Solid::cuboid(
        v3(bounds.min.x - 1.0, bounds.min.y - depth - 1.0, 0.0),
        v3(bounds.max.x + 1.0, bounds.max.y + depth + 1.0, depth),
    );
    Solid::union_all(&stock)?.intersect(&root)
}
fn disposal(v: &Value) -> Result<Solid> {
    let font = Font::find(v["family"].as_str().context("warning font")?, Kind::Bold)?;
    let h = font.profiles_with_kerning("H", 1.0, HAlign::Center, VAlign::Center, false)?;
    let (lo, hi) = profile_bounds(&h);
    let size = f(v, "cap_height")? / (hi.y - lo.y);
    let rows = v["lines"]
        .as_array()
        .context("warning lines")?
        .iter()
        .map(|line| {
            font.profiles_with_kerning(
                line.as_str().context("warning line")?,
                size,
                HAlign::Center,
                VAlign::Center,
                false,
            )
        })
        .collect::<Result<Vec<_>>>()?;
    let row_height = rows
        .iter()
        .map(|row| {
            let (lo, hi) = profile_bounds(row);
            hi.y - lo.y
        })
        .fold(0.0_f64, f64::max);
    let leading = row_height + f(v, "line_gap")?;
    let depth = f(v, "depth")?;
    let mut cached = std::collections::HashMap::<String, Solid>::new();
    let mut letters = vec![];
    for (index, row) in rows.iter().rev().enumerate() {
        let (lo, hi) = profile_bounds(row);
        let shift = v2(
            -(lo.x + hi.x) / 2.0,
            index as f64 * leading + (row_height - (hi.y - lo.y)) / 2.0 - lo.y,
        );
        for p in row {
            let (corner, _) = profile_bounds(std::slice::from_ref(p));
            let normalized = p.translated(-corner);
            let key = std::iter::once(&normalized.outer)
                .chain(&normalized.holes)
                .flat_map(|lp| lp.segs.iter())
                .map(|s| format!("{s:.9?}"))
                .collect::<Vec<_>>()
                .join("/");
            if !cached.contains_key(&key) {
                cached.insert(key.clone(), raked(&normalized, depth)?);
            }
            let d = corner + shift;
            letters.push(cached[&key].translate(v3(d.x, d.y, 0.0)));
        }
    }
    let o = array(&v["outer"])?;
    Ok(Solid::compose(&letters)
        .rotate(V3::ZERO, V3::X, 90.0)
        .rotate(V3::ZERO, V3::Z, 180.0)
        .translate(v3(
            (o[0] + o[1]) / 2.0,
            o[3] - f(v, "embed")?,
            o[4] + f(v, "bottom")?,
        )))
}

struct Panel {
    solid: Solid,
    relief: Option<Solid>,
}

fn panel(n: &Numbers) -> Result<Panel> {
    let recipe = n.get("panel")?;
    let nodes = recipe["nodes"].as_array().context("panel recipe nodes")?;
    let result = recipe["result"].as_u64().context("panel result")? as usize;
    let mut users = vec![0_usize; nodes.len()];
    users[result] += 1;
    for node in nodes {
        for input in node["inputs"].as_array().context("node inputs")? {
            users[input.as_u64().context("input index")? as usize] += 1;
        }
    }
    let mut live: Vec<Option<Solid>> = vec![None; nodes.len()];
    let mut relief = None;
    for (i, v) in nodes.iter().enumerate() {
        let inputs = v["inputs"]
            .as_array()
            .context("node inputs")?
            .iter()
            .map(|x| x.as_u64().map(|k| k as usize).context("node input"))
            .collect::<Result<Vec<_>>>()?;
        ensure!(
            inputs.iter().all(|&k| k < i),
            "numeric recipe is in construction order"
        );
        let input = |k: usize| -> &Solid {
            live[inputs[k]]
                .as_ref()
                .expect("a referenced solid is live")
        };
        let op = v["op"].as_str().context("node operation")?;
        let shape = (|| -> Result<Solid> {
            Ok(match op {
                "silhouette" => structure::silhouette(n)?,
                "box" => {
                    let (lo, hi) = box_corners(&v["box"])?;
                    Solid::cuboid(lo, hi)
                }
                "rounded-box" => {
                    let (lo, hi) = box_corners(&v["box"])?;
                    Plane::XY
                        .at(v3((lo.x + hi.x) / 2.0, (lo.y + hi.y) / 2.0, lo.z))
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
                    let mut p = [0.0; 3];
                    let mut a = [0.0; 3];
                    a[k] = 1.0;
                    p[k] = z[0];
                    let other: Vec<_> = (0..3).filter(|&j| j != k).collect();
                    p[other[0]] = c[0];
                    p[other[1]] = c[1];
                    Solid::cylinder(V3::from(p), V3::from(a), f(v, "radius")?, z[1] - z[0])?
                }
                "prism" => prism(v)?,
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
                "mirror" => {
                    let mut a = [0.0; 3];
                    a[axis(v)?] = 1.0;
                    input(0).mirror(V3::ZERO, V3::from(a))
                }
                "handhold-cutter" => handhold_cutter(v)?,
                "handhold-finish-air" => handhold_air(v)?,
                "disposal-letters" => disposal(v)?,
                _ => bail!("unsupported panel operation {op}"),
            })
        })()
        .with_context(|| format!("enclosure panel node {i} ({op})"))?;
        if op == "disposal-letters" {
            relief = Some(shape.clone());
        }
        live[i] = Some(shape);
        for k in inputs {
            users[k] -= 1;
            if users[k] == 0 {
                live[k] = None;
            }
        }
    }
    Ok(Panel {
        solid: live[result].take().context("finished structural panel")?,
        relief,
    })
}

fn manifold(s: &Solid) -> Result<Manifold> {
    let vertices: Vec<f32> = s
        .verts()
        .iter()
        .flat_map(|p| p.to_array().map(|v| v as f32))
        .collect();
    let triangles: Vec<u32> = s.tris().iter().flatten().copied().collect();
    Ok(Manifold::from_mesh_f32(&vertices, 3, &triangles)?)
}

fn printed(panel: &Panel, n: &Numbers) -> Result<Manifold> {
    let relief = panel
        .relief
        .as_ref()
        .context("back-bottom warning relief")?;
    let o = n.list("outer")?;
    let p = n.get("print")?;
    let b = relief.bounds();
    let margin = f(p, "warning_margin")?;
    let field = [
        b.min.x - margin,
        b.max.x + margin,
        o[3] - f(p, "wall")?,
        o[3] + f(p, "warning_raise")?,
        b.min.z - margin,
        b.max.z + margin,
    ];
    let smooth = panel.solid.cut(&Solid::cuboid(
        v3(field[0], o[3], field[4]),
        v3(field[1], o[3] + f(p, "warning_raise")? + 1.0, field[5]),
    ))?;
    let fluted = skin::flute_solid(&smooth.simplified()?, n, &[field])?;
    let joined = fluted.union(&manifold(relief)?);
    let (v, props, t) = joined.to_mesh_f32();
    // finish_print_mesh reads the same float32 positions once more before its final union.
    Ok(Manifold::from_mesh_f32(&v, props, &t)?)
}

fn print_stl(path: &std::path::Path, shape: &Manifold) -> Result<()> {
    let (v, props, t) = shape.to_mesh_f32();
    let temporary = path.with_file_name(format!(
        ".{}.{}.stl",
        path.file_stem().unwrap().to_string_lossy(),
        std::process::id()
    ));
    let mut out = std::io::BufWriter::new(std::fs::File::create(&temporary)?);
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
    std::fs::rename(temporary, path)?;
    Ok(())
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let built = panel(&n)?;
    let mut said = write_shown(
        &out,
        "enclosure-back-bottom",
        &[Body {
            name: "enclosure-back-bottom",
            color: Some(n.color("color")?),
            solid: &built.solid,
        }],
    )?;
    if n.get("print").is_ok() {
        let shape = printed(&built, &n)?;
        print_stl(&out.join("enclosure-back-bottom.stl"), &shape)?;
        said["files"]
            .as_array_mut()
            .context("part files")?
            .push(serde_json::json!("enclosure-back-bottom.stl"));
        said["print"] = serde_json::json!({"volume":shape.volume(),"triangles":shape.num_tri()});
    }
    println!("{said}");
    Ok(())
}
