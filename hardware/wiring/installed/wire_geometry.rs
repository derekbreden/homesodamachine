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
    for face in solid
        .faces()
        .iter()
        .filter(|face| !matches!(face.surface, Surface::Plane { .. }))
    {
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
        Surface::Free {
            kind: "PRESENTATION",
        },
        "",
        hsm_kernel::face::unknown_src(),
    )
    .with_contributors(&Value::Array(origins))?;
    let mut faces = vec![face];
    let face_indices: Vec<u32> = solid
        .faces()
        .iter()
        .map(|face| {
            if matches!(face.surface, Surface::Plane { .. }) {
                faces.push(*face);
                faces.len() as u32 - 1
            } else {
                0
            }
        })
        .collect();
    let face_of: Vec<u32> = solid
        .face_of()
        .iter()
        .map(|&face| face_indices[face as usize])
        .collect();
    let mut skin = Solid::from_mesh(solid.verts(), solid.tris(), &face_of, &faces)?;
    let mut shown = skin.simplified_to(tolerance)?;
    skin.forget_backend();
    shown.forget_backend();
    Ok(shown)
}

mod wire_components;

fn main() -> Result<()> {
    let (numbers, output) = part::args()?;
    let mut result = run(&numbers, &output)?;
    if output != std::path::Path::new("--check") {
        let root = numbers.text("name")?;
        let name = numbers
            .get("file_stem")
            .ok()
            .and_then(Value::as_str)
            .unwrap_or(root);
        let mesh = output.join(format!("{name}.step.mesh"));
        let shown = hsm_kernel::import::payload(&mesh)?;
        let bodies: Vec<_> = shown
            .iter()
            .map(|body| hsm_kernel::Body {
                name: &body.name,
                color: body.color,
                solid: &body.solid,
            })
            .collect();
        let step = hsm_kernel::step_bytes(&bodies, root)?;
        hsm_model_export::put(&output.join(format!("{name}.step")), &step)?;
        let mut head = hsm_geometry::scene::pack(&std::fs::read(&mesh)?)?;
        head["src"] = json!(hsm_model_export::digest(&step));
        head["source_kind"] = json!("step");
        head["step_export"] = json!(true);
        hsm_geometry::scene::persist(&mesh, &head)?;
        hsm_model_export::model::bind(&output.join(format!("{name}.step.npz")), &mesh)?;
        result["files"]
            .as_array_mut()
            .context("wire output files")?
            .push(json!(format!("{name}.step")));
    }
    println!("{result}");
    Ok(())
}

#[path = "wire_retained.rs"]
mod retained;

/// The installed conductors reuse unchanged fine and presentation entries between route edits.
pub fn run(numbers: &part::Numbers, output: &std::path::Path) -> Result<Value> {
    retained::run(numbers, output)
}
