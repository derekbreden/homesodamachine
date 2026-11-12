//! The installed terminations and jackets, cut from their shapes.
use super::wire_request::{Cylinder, Pose, Segment, Shape};
use super::{route_path, start_frame, wire};
use anyhow::{Result, ensure};
use hsm_kernel::{Affine, Loop, Plane, Profile, Solid, V2, V3, import};

fn cylinder(recipe: &Cylinder) -> Result<Solid> {
    Solid::cylinder(
        V3::from(recipe.base_mm),
        V3::from(recipe.axis),
        recipe.radius_mm,
        recipe.height_mm,
    )
}

fn pose(recipe: &Pose) -> Affine {
    let [a, b, c] = recipe.rotation.map(V3::from);
    Affine::from_columns(
        V3::from([a.x, b.x, c.x]),
        V3::from([a.y, b.y, c.y]),
        V3::from([a.z, b.z, c.z]),
        V3::from(recipe.translation_mm),
    )
}

/// A jacket of `outer` diameter and `inner` bore along `segments`.
fn annular(segments: &[Segment], outer: f64, inner: f64) -> Result<Solid> {
    let path = route_path(segments)?;
    ensure!(
        outer > inner && inner > 0.0,
        "jacket diameters do not enclose an annulus"
    );
    let section =
        Profile::circle(V2::ZERO, outer / 2.0).with_hole(Loop::circle(V2::ZERO, inner / 2.0));
    start_frame(&path, V3::from(segments[0].start())).sweep(&section, &path)
}

/// The solids of one termination or jacket.
pub(super) fn build(shape: &Shape) -> Result<Vec<Solid>> {
    let solid = match shape {
        Shape::Import { step, pose: placed } => {
            // The display payload beside a B-rep STEP is not an input to `import::step`.
            let transform = pose(placed);
            return Ok(import::step(step)?
                .into_iter()
                .map(|p| p.solid.transformed(&transform))
                .collect());
        }
        Shape::Ring {
            eye,
            bore,
            barrel,
            origin_mm,
            x_dir,
            normal,
        } => cylinder(eye)?
            .cut(&cylinder(bore)?)?
            .union(&cylinder(barrel)?)?
            .transformed(
                &Plane::new(V3::from(*origin_mm), V3::from(*x_dir), V3::from(*normal))?.to_world(),
            ),
        Shape::Housing {
            origin_mm,
            x_dir,
            normal,
            dimensions_mm,
            bores,
        } => {
            let dims = V3::from(*dimensions_mm);
            let mut body = Plane::new(V3::from(*origin_mm), V3::from(*x_dir), V3::from(*normal))?
                .offset(dims.z / 2.0)
                .cuboid(dims.x, dims.y, dims.z);
            for bore in bores {
                body = body.cut(&cylinder(bore)?)?;
            }
            body
        }
        Shape::Sweep {
            segments,
            diameter_mm,
            ..
        } => wire(segments, *diameter_mm)?,
        Shape::Sleeve { outer, inner } => cylinder(outer)?.cut(&cylinder(inner)?)?,
        Shape::AnnularSweep {
            segments,
            diameter_mm,
            inner_diameter_mm,
            ..
        } => annular(segments, *diameter_mm, *inner_diameter_mm)?,
    };
    Ok(vec![solid])
}
