//! The installed termination and jacket geometry supplied by their Python source.
use super::{point, route_path, wire};
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::{Affine, Leg, Loop, Plane, Profile, Solid, V2, V3, import};
use serde_json::Value;

fn scalar(recipe: &Value, key: &str) -> Result<f64> {
    recipe[key]
        .as_f64()
        .with_context(|| format!("component {key}"))
}

fn plane(recipe: &Value) -> Result<Plane> {
    Plane::new(
        point(&recipe["origin_mm"])?,
        point(&recipe["x_dir"])?,
        point(&recipe["normal"])?,
    )
}

fn cylinder(recipe: &Value) -> Result<Solid> {
    Solid::cylinder(
        point(&recipe["base_mm"])?,
        point(&recipe["axis"])?,
        scalar(recipe, "radius_mm")?,
        scalar(recipe, "height_mm")?,
    )
}

fn pose(recipe: &Value) -> Result<Affine> {
    let r = &recipe["rotation"];
    let (a, b, c) = (point(&r[0])?, point(&r[1])?, point(&r[2])?);
    Ok(Affine::from_columns(
        V3::from([a.x, b.x, c.x]),
        V3::from([a.y, b.y, c.y]),
        V3::from([a.z, b.z, c.z]),
        point(&recipe["translation_mm"])?,
    ))
}

fn annular(recipe: &Value) -> Result<Solid> {
    let segments = recipe["segments"].as_array().context("jacket segments")?;
    let path = route_path(segments)?;
    let tangent = match path.legs[0] {
        Leg::Line { a, b } => (b - a).unit(),
        Leg::Arc { a, c, d, .. } => d.cross(a - c).unit(),
        Leg::Curve { k, .. } => path.curves[k].derivative(path.curves[k].range().0).unit(),
    };
    let (z, x, y) = hsm_kernel::rule::plane_frame(tangent);
    let frame = Plane {
        origin: point(&segments[0]["start_mm"])?,
        x,
        y,
        z,
    };
    let (outer, inner) = (
        scalar(recipe, "diameter_mm")?,
        scalar(recipe, "inner_diameter_mm")?,
    );
    ensure!(
        outer > inner && inner > 0.0,
        "jacket diameters do not enclose an annulus"
    );
    let section =
        Profile::circle(V2::ZERO, outer / 2.0).with_hole(Loop::circle(V2::ZERO, inner / 2.0));
    frame.sweep(&section, &path)
}

pub(super) fn build(recipe: &Value) -> Result<Vec<Solid>> {
    let solid = match recipe["kind"].as_str().context("component geometry kind")? {
        "import" => {
            // `_rust_part.step` supplies the fine native-STEP tessellation. The display
            // payload adjacent to a B-rep STEP is not an input to `import::step`.
            let parts = import::step(recipe["step"].as_str().context("component STEP")?)?;
            let transform = pose(&recipe["pose"])?;
            return Ok(parts
                .into_iter()
                .map(|p| p.solid.transformed(&transform))
                .collect());
        }
        "ring" => cylinder(&recipe["eye"])?
            .cut(&cylinder(&recipe["bore"])?)?
            .union(&cylinder(&recipe["barrel"])?)?
            .transformed(&plane(recipe)?.to_world()),
        "housing" => {
            let dims = point(&recipe["dimensions_mm"])?;
            let mut body = plane(recipe)?
                .offset(dims.z / 2.0)
                .cuboid(dims.x, dims.y, dims.z);
            for bore in recipe["bores"].as_array().context("housing bores")? {
                body = body.cut(&cylinder(bore)?)?;
            }
            body
        }
        "sweep" => wire(
            recipe["segments"].as_array().context("lead segments")?,
            scalar(recipe, "diameter_mm")?,
        )?,
        "sleeve" => cylinder(&recipe["outer"])?.cut(&cylinder(&recipe["inner"])?)?,
        "annular_sweep" => annular(recipe)?,
        kind => bail!("unsupported installed component {kind:?}"),
    };
    Ok(vec![solid])
}
