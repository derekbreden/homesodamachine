//! The enclosure's structural back-bottom panel from its private Python recipe.
#[path = "enclosure_structure.rs"]
#[allow(dead_code)]
mod structure;
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::part::{Numbers, args, write_shown};
use hsm_kernel::*;
use serde_json::Value;

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
    let roof_air = Solid::thru_sections(&with_roof, false)?;
    let side_air = Solid::thru_sections(&returns, false)?;
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

pub fn panel(n: &Numbers) -> Result<Solid> {
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
        live[i] = Some(shape);
        for k in inputs {
            users[k] -= 1;
            if users[k] == 0 {
                live[k] = None;
            }
        }
    }
    live[result].take().context("finished structural panel")
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let shape = panel(&n)?;
    println!(
        "{}",
        write_shown(
            &out,
            "enclosure-back-bottom",
            &[Body {
                name: "enclosure-back-bottom",
                color: Some(n.color("color")?),
                solid: &shape
            }]
        )?
    );
    Ok(())
}
