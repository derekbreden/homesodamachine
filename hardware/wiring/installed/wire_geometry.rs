//! Installed conductors cut from the recorded native line/arc/clamped-spline routes.
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::{Leg, Path, Plane, Profile, Solid, V2, V3, part};
use serde_json::{Value, json};

fn point(value: &Value) -> Result<V3> {
    let values = value
        .as_array()
        .context("wire point is three coordinates")?;
    ensure!(
        values.len() == 3,
        "wire point has {} coordinates",
        values.len()
    );
    let mut p = [0.0; 3];
    for (i, value) in values.iter().enumerate() {
        p[i] = value
            .as_f64()
            .filter(|v| v.is_finite())
            .context("wire point is not finite")?;
    }
    Ok(V3::from(p))
}

fn route_path(segments: &[Value]) -> Result<Path> {
    let first = segments.first().context("wire has no segments")?;
    let mut path = Path::new(point(&first["start_mm"])?);
    for segment in segments {
        let start = point(&segment["start_mm"])?;
        ensure!(
            (path.at() - start).norm() < 1e-7,
            "wire segments do not meet"
        );
        path = match segment["kind"].as_str().context("wire segment kind")? {
            "line" => path.line_to(point(&segment["end_mm"])?),
            "arc" => {
                path.arc_through(point(&segment["midpoint_mm"])?, point(&segment["end_mm"])?)?
            }
            "spline" => {
                let points: Vec<V3> = segment["interpolation_points_mm"]
                    .as_array()
                    .context("spline interpolation points")?
                    .iter()
                    .map(point)
                    .collect::<Result<_>>()?;
                let parameters: Vec<f64> = segment["parameters"]
                    .as_array()
                    .context("spline parameters")?
                    .iter()
                    .map(|v| v.as_f64().context("spline parameter is not numeric"))
                    .collect::<Result<_>>()?;
                let values = segment["endpoint_derivatives"]
                    .as_array()
                    .context("spline endpoint derivatives")?;
                ensure!(values.len() == 2, "spline needs two endpoint derivatives");
                path.clamped_spline(
                    &points,
                    &parameters,
                    [point(&values[0])?, point(&values[1])?],
                )?
            }
            kind => bail!("unsupported recorded wire segment {kind:?}"),
        };
    }
    Ok(path)
}

fn wire(segments: &[Value], diameter: f64) -> Result<Solid> {
    ensure!(
        diameter.is_finite() && diameter > 0.0,
        "wire diameter must be positive"
    );
    let path = route_path(segments)?;
    let tangent = match path.legs[0] {
        Leg::Line { a, b } => (b - a).unit(),
        Leg::Arc { a, c, d, .. } => d.cross(a - c).unit(),
        Leg::Curve { k, .. } => path.curves[k].derivative(path.curves[k].range().0).unit(),
    };
    let (z, x, y) = hsm_kernel::rule::plane_frame(tangent);
    let plane = Plane {
        origin: point(&segments[0]["start_mm"])?,
        x,
        y,
        z,
    };
    plane.sweep(&Profile::circle(V2::ZERO, diameter / 2.0), &path)
}

fn main() -> Result<()> {
    let (numbers, output) = part::args()?;
    let routes = numbers
        .get("routes")?
        .as_array()
        .context("routes is an ordered array")?;
    let mut fine = Vec::with_capacity(routes.len());
    let mut names = Vec::with_capacity(routes.len());
    let mut colors = Vec::with_capacity(routes.len());
    for route in routes {
        let name = route["name"].as_str().context("wire component name")?;
        let diameter = route["diameter_mm"].as_f64().context("wire diameter")?;
        let segments = route["segments"].as_array().context("wire segments")?;
        let color = route["linear_rgb"].as_array().context("wire linear RGB")?;
        ensure!(color.len() == 3, "wire RGB has {} channels", color.len());
        let mut rgb = [0.0; 3];
        for (i, channel) in color.iter().enumerate() {
            rgb[i] = channel
                .as_f64()
                .filter(|v| v.is_finite())
                .context("non-finite wire RGB")?;
        }
        let solid = wire(segments, diameter).with_context(|| format!("building {name}"))?;
        names.push(name);
        colors.push(rgb);
        fine.push(solid);
    }
    if output == std::path::Path::new("--check") {
        let rows: Vec<Value> = fine
            .iter()
            .zip(&names)
            .zip(&colors)
            .map(|((s, name), color)| {
                let b = s.bounds();
                json!({"name":name,"color":color,"min":b.min.to_array(),"max":b.max.to_array(),
                   "volume":s.volume(),"vertices":s.verts().len(),"triangles":s.tris().len(),
                   "faces":s.faces().len()})
            })
            .collect();
        println!("{}", json!({"files":[],"bodies":rows}));
        return Ok(());
    }
    let first = fine.first().context("wire assembly is empty")?.bounds();
    let (mut lower, mut upper) = (first.min, first.max);
    for solid in &fine {
        let b = solid.bounds();
        lower = lower.min(b.min);
        upper = upper.max(b.max);
    }
    let span = upper - lower;
    let deflection =
        (span.x + span.y + span.z) / 3.0 * numbers.f("presentation_deflection_ratio")?;
    let presentation_tolerance = deflection.min(hsm_kernel::LINEAR);
    let presentation: Vec<Solid> = fine
        .iter()
        .map(|solid| solid.simplified_to(presentation_tolerance))
        .collect::<Result<_>>()?;
    let bodies: Vec<part::AssemblyBody> = fine
        .iter()
        .zip(&presentation)
        .enumerate()
        .map(|(i, (fine, presentation))| part::AssemblyBody {
            name: names[i],
            color: Some(colors[i]),
            fine,
            presentation,
        })
        .collect();
    std::fs::create_dir_all(&output)?;
    let document = json!({"schema":"hsm-installed-wires-1","frame":"Enclosure assembly XYZ; Z up",
                          "presentation_tolerance_mm":presentation_tolerance,
                          "alpha_by_name":names.iter().map(|name|((*name).to_owned(),json!(1.0))).collect::<serde_json::Map<_,_>>()});
    let said = part::write_assembly(&output, numbers.text("name")?, &bodies, Some(&document))?;
    println!("{said}");
    Ok(())
}
