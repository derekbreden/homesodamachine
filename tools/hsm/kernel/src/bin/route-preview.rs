//! Hollow tubes from the production route JSON, without Python or CadQuery.
//! cargo run --release -p hsm-kernel --bin route-preview -- routes.json tubes.step.mesh
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::*;
use serde_json::{Value, json};
use std::{fs, time::Instant};

fn point(v: &Value) -> Result<V3> {
    let a = v.as_array().context("a route point is not an array")?;
    ensure!(a.len() == 3, "a route point needs three coordinates");
    let mut p = [0.0; 3];
    for (i, value) in a.iter().enumerate() {
        p[i] = value.as_f64().context("a route coordinate is not a number")?;
        ensure!(p[i].is_finite(), "a route coordinate is not finite");
    }
    Ok(V3::from(p))
}

fn points(v: &Value) -> Result<Vec<V3>> {
    v.as_array().context("route points are not an array")?.iter().map(point).collect()
}

fn path(route: &Value) -> Result<(Path, V3)> {
    let segments = route["segments"].as_array().context("a route has no segments")?;
    let mut path: Option<Path> = None;
    let mut heading = None;
    for (index, segment) in segments.iter().enumerate() {
        let kind = segment["kind"].as_str().context("a segment has no kind")?;
        let pts = points(&segment[if kind == "bezier" { "control_points_mm" } else { "points_mm" }])?;
        let start = *pts.first().context("a segment has no points")?;
        // The native wire omits coincident illustrative mouth points.
        if kind == "line" && pts.len() == 2 && (pts[1] - start).norm() <= 1e-6 {
            continue;
        }
        let current = path.take().unwrap_or_else(|| Path::new(start));
        ensure!((current.at() - start).norm() < 1e-7, "segment {index} leaves an open join");
        let next = match (kind, pts.as_slice()) {
            ("line", [_, b]) => current.line_to(*b),
            ("arc", [_, mid, b]) => current.arc_through(*mid, *b)?,
            ("bezier", _) => current.bezier(&pts)?,
            _ => bail!("unsupported {kind} segment with {} points", pts.len()),
        };
        if heading.is_none() {
            let direction = match next.legs[0] {
                Leg::Line { a, b } => b - a,
                Leg::Arc { a, c, d, .. } => d.cross(a - c),
                Leg::Curve { k, .. } => next.curves[k].derivative(next.curves[k].range().0),
            };
            ensure!(direction.norm() > 1e-12, "the route has no initial tangent");
            heading = Some(direction.unit());
        }
        path = Some(next);
    }
    Ok((path.context("a route has no nonzero segments")?, heading.context("a route has no tangent")?))
}

fn tube(route: &Value) -> Result<Solid> {
    let od = route["od_mm"].as_f64().context("a route has no od_mm")?;
    let id = route["id_mm"].as_f64().context("a route has no id_mm")?;
    ensure!(od.is_finite() && id.is_finite() && od > id && id > 0.0,
            "a hollow route needs finite 0 < id_mm < od_mm");
    let (path, heading) = path(route)?;
    let across = if heading.cross(V3::X).norm() > 1e-6 { V3::X } else { V3::Y };
    let profile = Profile::circle(v2(0.0, 0.0), od / 2.0)
        .with_hole(Loop::circle(v2(0.0, 0.0), id / 2.0));
    let solid = Plane::new(path.legs[0].start(), across, heading)?.sweep(&profile, &path)?;
    solid.check()?;
    Ok(solid)
}

fn main() -> Result<()> {
    let started = Instant::now();
    let args: Vec<String> = std::env::args().collect();
    ensure!(args.len() == 3, "usage: route-preview <routes.json> <tubes.step.mesh>");
    let raw = fs::read(&args[1])?;
    let value: Value = serde_json::from_slice(&raw)?;
    let routes = value.as_object().context("routes must be an object keyed by route name")?;
    ensure!(!routes.is_empty(), "no routes were supplied");
    let names: Vec<String> = routes.keys().map(|n| if n.starts_with("tube-") { n.clone() } else { format!("tube-{n}") }).collect();
    let solids: Vec<Solid> = routes.iter().map(|(name, route)| tube(route).with_context(|| format!("route {name}"))).collect::<Result<_>>()?;
    let bodies: Vec<Body> = names.iter().zip(&solids).map(|(name, solid)| Body { name, solid, color: Some([0.4, 0.5, 0.6]) }).collect();
    write_payload(&args[2], &bodies, None, None)?;
    let stats: Vec<Value> = names.iter().zip(&solids).map(|(name, solid)| {
        let bounds = solid.bounds();
        json!({"name": name, "volume_mm3": solid.volume(),
               "bounds_mm": [[bounds.min.x, bounds.min.y, bounds.min.z], [bounds.max.x, bounds.max.y, bounds.max.z]]})
    }).collect();
    println!("{}", json!({"payload": args[2], "linear_mm": LINEAR, "angular_rad": ANGULAR,
                            "elapsed_ms": started.elapsed().as_secs_f64() * 1000.0, "bodies": stats}));
    Ok(())
}
