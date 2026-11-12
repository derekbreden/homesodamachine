//! Installed conductors cut from the recorded native line/arc/clamped-spline routes.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Face, Leg, Path, Plane, Profile, Solid, Surface, V2, V3, part, src_line};
use serde::Deserialize;
use serde_json::{Value, json};
use wire_request::{Request, Segment};

/// The request the wires are cut from: each conductor's centreline and each termination's
/// shape.
pub(crate) mod wire_request;

/// The path a centreline's segments trace, end to end.
fn route_path(segments: &[Segment]) -> Result<Path> {
    let first = segments.first().context("wire has no segments")?;
    let mut path = Path::new(V3::from(first.start()));
    for segment in segments {
        ensure!(
            (path.at() - V3::from(segment.start())).norm() < 1e-7,
            "wire segments do not meet"
        );
        path = match segment {
            Segment::Line { end_mm, .. } => path.line_to(V3::from(*end_mm)),
            Segment::Arc {
                midpoint_mm,
                end_mm,
                ..
            } => path.arc_through(V3::from(*midpoint_mm), V3::from(*end_mm))?,
            Segment::Spline(spline) => {
                let points: Vec<V3> = spline
                    .interpolation_points_mm
                    .iter()
                    .map(|&p| V3::from(p))
                    .collect();
                path.clamped_spline(
                    &points,
                    &spline.parameters,
                    spline.endpoint_derivatives.map(V3::from),
                )?
            }
        };
    }
    Ok(path)
}

/// The frame a section is swept from: at the path's start, its normal along the path.
fn start_frame(path: &Path, origin: V3) -> Plane {
    let tangent = match path.legs[0] {
        Leg::Line { a, b } => (b - a).unit(),
        Leg::Arc { a, c, d, .. } => d.cross(a - c).unit(),
        Leg::Curve { k, .. } => path.curves[k].derivative(path.curves[k].range().0).unit(),
    };
    let (z, x, y) = hsm_kernel::rule::plane_frame(tangent);
    Plane { origin, x, y, z }
}

/// A round wire of `diameter` along `segments`.
fn wire(segments: &[Segment], diameter: f64) -> Result<Solid> {
    ensure!(
        diameter.is_finite() && diameter > 0.0,
        "wire diameter must be positive"
    );
    let path = route_path(segments)?;
    start_frame(&path, V3::from(segments[0].start()))
        .sweep(&Profile::circle(V2::ZERO, diameter / 2.0), &path)
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
    let request = Request {
        name: numbers.text("name")?.to_owned(),
        file_stem: numbers
            .get("file_stem")
            .ok()
            .and_then(Value::as_str)
            .map(str::to_owned),
        presentation_deflection_ratio: numbers.f("presentation_deflection_ratio")?,
        presentation_angular_deflection_rad: numbers.f("presentation_angular_deflection_rad")?,
        routes: Vec::deserialize(numbers.get("routes")?).context("ordered wire routes")?,
        components: match numbers.get("components") {
            Ok(components) => Vec::deserialize(components).context("wire components")?,
            Err(_) => Vec::new(),
        },
    };
    let mut result = run(&request, &output)?;
    if output != std::path::Path::new("--check") {
        let root = request.name.as_str();
        let name = request.file_stem.as_deref().unwrap_or(root);
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
pub fn run(request: &Request, output: &std::path::Path) -> Result<Value> {
    retained::run(request, output)
}
