//! Installed conductors cut from the recorded native line/arc/clamped-spline routes.
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::{Face, Leg, Path, Plane, Profile, Solid, Surface, V2, V3, part, src_line};
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

fn presentation(solid: &Solid, tolerance: f64) -> Result<Solid> {
    // Surface partitions describe the fine model, not boundaries in the drawn skin.
    // Preserve their complete attribution on the separate presentation surface.
    let source = |src: hsm_kernel::Src| {
        if src.recorded() {
            Value::String(src_line(src))
        } else {
            Value::Null
        }
    };
    let mut origins = Vec::new();
    for face in solid.faces().iter().filter(|face| !matches!(face.surface, Surface::Plane { .. })) {
        let inherited = face.src.contributors();
        let records = if face.record_null {
            vec![Value::Null]
        } else if let Some(records) = inherited {
            records.to_vec()
        } else {
            vec![json!({"src":source(face.src),"op":face.op})]
        };
        for mut record in records {
            if let (Some(record), Some(via)) = (record.as_object_mut(), face.via) {
                record.insert("via".into(), json!({"src":source(via.src),"op":via.op}));
            }
            origins.push(record);
        }
    }
    let face = Face::new(
        Surface::Free { kind: "PRESENTATION" },
        "",
        hsm_kernel::face::unknown_src(),
    )
    .with_contributors(&Value::Array(origins))?;
    let mut faces = vec![face];
    let face_indices: Vec<u32> = solid.faces().iter().map(|face| {
        if matches!(face.surface, Surface::Plane { .. }) {
            faces.push(*face);
            faces.len() as u32 - 1
        } else {
            0
        }
    }).collect();
    let face_of: Vec<u32> = solid.face_of().iter().map(|&face| face_indices[face as usize]).collect();
    let mut skin = Solid::from_mesh(solid.verts(), solid.tris(), &face_of, &faces)?;
    let mut shown = skin.simplified_to(tolerance)?;
    skin.forget_backend();
    shown.forget_backend();
    Ok(shown)
}

mod wire_components;

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
        let mut solid = wire(segments, diameter).with_context(|| format!("building {name}"))?;
        solid.forget_backend();
        names.push(name);
        colors.push(rgb);
        fine.push(solid);
    }
    let mut component_diameters = Vec::new();
    if let Ok(components) = numbers.get("components") {
        for component in components
            .as_array()
            .context("ordered installed components")?
        {
            let name = component["name"]
                .as_str()
                .context("installed component name")?;
            let rgb = point(&component["linear_rgb"])?.to_array();
            let parts =
                wire_components::build(component).with_context(|| format!("building {name}"))?;
            for mut solid in parts {
                solid.forget_backend();
                names.push(name);
                colors.push(rgb);
                fine.push(solid);
                component_diameters.push(component["diameter_mm"].as_f64());
            }
        }
    }
    if output == std::path::Path::new("--check") {
        let rows: Vec<Value> = fine
            .iter()
            .zip(&names)
            .zip(&colors)
            .map(|((s, name), color)| {
                let b = s.bounds();
                json!({"name":name,"color":color,"min":b.min.to_array(),"max":b.max.to_array(),
                   "volume":s.volume(),"center":s.centroid().to_array(),
                   "vertices":s.verts().len(),"triangles":s.tris().len(),
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
    let angular = numbers.f("presentation_angular_deflection_rad")?;
    let radius = routes
        .iter()
        .filter_map(|route| route["diameter_mm"].as_f64())
        .fold(f64::INFINITY, f64::min)
        / 2.0;
    let presentation_tolerance = deflection.min(radius * (1.0 - (angular / 2.0).cos()));
    let angular_tolerance = |diameter: f64| {
        deflection.min(diameter / 2.0 * (1.0 - (angular / 2.0).cos()))
    };
    let tolerances: Vec<f64> = routes.iter()
        .map(|route| angular_tolerance(route["diameter_mm"].as_f64().unwrap()))
        .chain(component_diameters.iter().map(|diameter| {
            diameter.map_or(presentation_tolerance, |d| {
                angular_tolerance(d)
            })
        }))
        .collect();
    let presentation: Vec<Solid> = fine
        .iter_mut()
        .zip(&tolerances)
        .map(|(solid, tolerance)| {
            let shown = presentation(solid, *tolerance)?;
            solid.forget_backend();
            Ok(shown)
        })
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
                          "presentation_angular_deflection_rad":angular,
                          "presentation_surface_partitions":"coalesced with complete fine-face contributors",
                          "presentation_tolerance_by_name_mm":names.iter().zip(&tolerances)
                              .map(|(name,tolerance)|((*name).to_owned(),json!(tolerance)))
                              .collect::<serde_json::Map<_,_>>(),
                          "alpha_by_name":names.iter().map(|name|((*name).to_owned(),json!(1.0))).collect::<serde_json::Map<_,_>>()});
    let root_name = numbers.text("name")?;
    let file_stem = match numbers.get("file_stem") {
        Ok(value) => value.as_str().context("assembly file stem")?,
        Err(_) => root_name,
    };
    let said = part::write_assembly_with_root(
        &output, file_stem, root_name, &bodies, Some(&document),
    )?;
    println!("{said}");
    Ok(())
}
