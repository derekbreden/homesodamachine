//! The structural enclosure exterior from Python's display and roof stations.
use anyhow::{Context, Result, ensure};
use hsm_kernel::part::{Numbers, args, write_shown};
use hsm_kernel::*;
use serde_json::Value;

fn f(v: &Value, key: &str) -> Result<f64> {
    v[key].as_f64().with_context(|| format!("no number{key}"))
}
fn p2(v: &Value) -> Result<V2> {
    Ok(v2(
        v[0].as_f64().context("point x")?,
        v[1].as_f64().context("point y")?,
    ))
}

pub fn preblend(n: &Numbers) -> Result<(Solid, Solid)> {
    let o = n.list("outer")?;
    ensure!(o.len() == 6, "six exterior bounds");
    let (x0, x1, y0, y1, z0, z1) = (o[0], o[1], o[2], o[3], o[4], o[5]);
    let p = n.get("profile")?;
    let outline = Pen::new(v2(y0, z0))
        .line_to(p2(&p["foot"])?)
        .arc_through(p2(&p["front_mid"])?, p2(&p["start"])?)?
        .line_to(p2(&p["end"])?)
        .arc_through(p2(&p["top_mid"])?, p2(&p["roof"])?)?
        .line_to(v2(y1, z1))
        .line_to(v2(y1, z0))
        .close()?;
    let envelope = Plane::YZ
        .at(v3(x0, 0.0, 0.0))
        .extrude(&Profile::new(outline), x1 - x0)?;
    let r = n.f("standing_radius")?;
    let rounded = Plane::XY
        .at(v3((x0 + x1) / 2.0, (y0 + y1) / 2.0, z0))
        .extrude(
            &Profile::new(Loop::rounded_rect(V2::ZERO, x1 - x0, y1 - y0, r)?),
            z1 - z0,
        )?;
    let rear = Solid::cuboid(v3(x0, y0 + r, z0), v3(x1, y1, z1));
    Ok((envelope.intersect(&rounded.union(&rear)?)?, rounded))
}

pub fn roof_fill(n: &Numbers) -> Result<Solid> {
    let mut fills = vec![];
    let angle = math::radians(n.f("angle")?);
    for side in n
        .get("roof_fill_sections")?
        .as_array()
        .context("two roof edge fills")?
    {
        let mut regions = vec![];
        for s in side.as_array().context("roof fill sections")? {
            let x = f(s, "x")?;
            let c = p2(&s["centre"])?;
            let ellipse = &s["ellipse"];
            let b = ellipse[0].as_f64().context("ellipse major radius")?;
            let a = ellipse[1].as_f64().context("ellipse minor radius")?;
            let theta = math::radians(ellipse[2].as_f64().context("ellipse turn")?);
            let inner = f(s, "inner_radius")?;
            let at = |key: &str| -> Result<V3> {
                let p = p2(&s[key])?;
                Ok(v3(x, p.x, p.y))
            };
            let center = v3(x, c.x, c.y);
            let line = |a, b| LoftEdge::Line { a, b };
            let section = LoftSection::new(vec![
                line(at("start")?, at("top_tangent")?),
                LoftEdge::Conic {
                    c: center,
                    x: v3(0.0, 0.0, b),
                    y: v3(0.0, -a, 0.0),
                    t0: theta,
                    t1: 0.0,
                },
                line(at("upper_roof")?, at("upper_aft")?),
                line(at("upper_aft")?, at("lower_aft")?),
                line(at("lower_aft")?, at("lower_roof")?),
                LoftEdge::Conic {
                    c: center,
                    x: v3(0.0, 0.0, inner),
                    y: v3(0.0, -inner, 0.0),
                    t0: 0.0,
                    t1: angle,
                },
                line(at("inner_end")?, at("inner_start")?),
                line(at("inner_start")?, at("start")?),
            ]);
            let mut region = section.region();
            // The elliptical edge and the ruled band both contribute chord error. Bisect
            // this edge's parameter intervals so their combined surface stays inside LINEAR.
            let old = &region.loops[0];
            let mut points = vec![];
            let mut segments = vec![];
            for (i, edge) in section.edges.iter().enumerate() {
                let indices: Vec<usize> = old
                    .seg
                    .iter()
                    .enumerate()
                    .filter_map(|(k, &curve)| (curve == i as u32).then_some(k))
                    .collect();
                if matches!(region.curves[i], Curve::Free("ELLIPSE")) {
                    let count = 2 * indices.len();
                    for k in 0..count {
                        points.push(edge.at(k as f64 / count as f64));
                    }
                    segments.extend(std::iter::repeat_n(i as u32, count));
                } else {
                    for k in indices {
                        points.push(old.pts[k]);
                        segments.push(i as u32);
                    }
                }
            }
            region.loops = vec![profile::RLoop {
                pts: points,
                seg: segments,
            }];
            regions.push(region);
        }
        // Native _roof_fill disables compatibility: these eight edges already correspond.
        fills.push(Solid::loft(&regions)?);
    }
    Ok(Solid::compose(&fills))
}

fn aft_cap(n: &Numbers) -> Result<Solid> {
    let o = n.list("outer")?;
    let p = n.get("profile")?;
    let y0 = p2(&p["roof"])?.x;
    let (y1, z) = (o[3], o[5]);
    let transition = n.get("roof_transition")?;
    let height = f(transition, "height")?;
    let foot = f(transition, "foot")?;
    let slope = f(transition, "outward_per_height")?;
    let radius = n.f("side_radius")?;
    let (left, right, bottom) = (o[0], o[1], o[4]);
    let centre_z = z - radius;
    let tangent_z = z - height;
    let theta = (radius-height).atan2(radius-foot+slope*height);
    let right_mid = v2(right-radius+radius*math::cos(theta/2.),
                       centre_z+radius*math::sin(theta/2.));
    let left_mid = v2(left+radius-radius*math::cos(theta/2.), right_mid.y);
    let outline = Pen::new(v2(left,bottom))
        .line_to(v2(right,bottom))
        .line_to(v2(right,centre_z))
        .arc_through(right_mid,v2(right-foot+slope*height,tangent_z))?
        .line_to(v2(right-foot,z))
        .line_to(v2(left+foot,z))
        .line_to(v2(left+foot-slope*height,tangent_z))
        .arc_through(left_mid,v2(left,centre_z))?
        .close()?;
    Plane::XZ.at(v3(0.,y0,0.))
        .extrude(&Profile::new(outline),-(y1-y0))
}

pub fn silhouette(n: &Numbers) -> Result<Solid> {
    let o = n.list("outer")?;
    let (body, rounded_box) = preblend(n)?;
    let standing = n.f("standing_radius")?;
    let foot = p2(&n.get("profile")?["foot"])?.y;
    let selected = Edges(
        body.edges("")?
            .iter()
            .filter(|e| {
                let lo = |k: usize| e.pts.iter().map(|p| p[k]).fold(f64::INFINITY, f64::min);
                let hi = |k: usize| e.pts.iter().map(|p| p[k]).fold(f64::NEG_INFINITY, f64::max);
                (lo(0) >= o[1] - standing - 1e-5 || hi(0) <= o[0] + standing + 1e-5)
                    && lo(2) >= foot - 1e-5
                    && lo(1) < o[3] - 1.0
            })
            .cloned()
            .collect(),
    );
    let rounded = body
        .rolling_fillet(&selected, n.f("side_radius")?)?
        .intersect(&rounded_box)?;
    let aft = aft_cap(n)?.intersect(&rounded_box)?;
    let fore = roof_fill(n)?.intersect(&body)?.intersect(&rounded_box)?;
    let roof_y = p2(&n.get("profile")?["roof"])?.x;
    let fore_limit = Solid::cuboid(v3(o[0]-1.,o[2]-1.,o[4]-1.),
                                   v3(o[1]+1.,roof_y,o[5]+1.));
    rounded.union(&fore)?.intersect(&fore_limit)?.union(&aft)
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let shape = silhouette(&n)?;
    println!(
        "{}",
        write_shown(
            &out,
            "enclosure-structure",
            &[Body {
                name: "enclosure-structure",
                color: None,
                solid: &shape
            }]
        )?
    );
    Ok(())
}
