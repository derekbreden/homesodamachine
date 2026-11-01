//! The enclosure's R6 display-side roll where a standing R12 cylinder meets its 30° plane.
//! `HSM_ROLLING_REFERENCE` optionally names the native fixture directory for the surface proof.
mod common;
use anyhow::{Result, ensure};
use hsm_kernel::*;

fn preblend() -> Result<Solid> {
    let (x0, x1, y0, y1, z0, z1) = (
        -107.5,
        107.5,
        5.0,
        471.3,
        -6.000000099651519,
        354.9999999003485,
    );
    let (standing, front, top, flat, angle) = (12.0, 12.0, 18.0, 87.0, math::radians(30.0));
    let foot =
        z1 - front * math::cos(angle) - flat * math::sin(angle) - top * (1.0 - math::cos(angle));
    let start = v2(
        y0 + front * (1.0 - math::sin(angle)),
        foot + front * math::cos(angle),
    );
    let end = start + v2(math::cos(angle), math::sin(angle)) * flat;
    let roof = v2(end.x + top * math::sin(angle), z1);
    let outline = Pen::new(v2(y0, z0))
        .line_to(v2(y0, foot))
        .arc_through(
            v2(
                y0 + front + front * math::cos(math::radians(150.0)),
                foot + front * math::sin(math::radians(150.0)),
            ),
            start,
        )?
        .line_to(end)
        .arc_through(
            v2(
                roof.x - top * math::sin(angle / 2.0),
                z1 - top + top * math::cos(angle / 2.0),
            ),
            roof,
        )?
        .line_to(v2(y1, z1))
        .line_to(v2(y1, z0))
        .close()?;
    let envelope = Plane::YZ
        .at(v3(x0, 0.0, 0.0))
        .extrude(&Profile::new(outline), x1 - x0)?;
    let rounded = Plane::XY.at(v3(0.0, (y0 + y1) / 2.0, z0)).extrude(
        &Profile::new(Loop::rounded_rect(V2::ZERO, x1 - x0, y1 - y0, standing)?),
        z1 - z0,
    )?;
    let rear = Solid::cuboid(v3(x0, y0 + standing, z0), v3(x1, y1, z1));
    envelope.intersect(&rounded.union(&rear)?)
}

fn display_corner(s: &Solid) -> Result<Edges> {
    let edges = s.edges("")?;
    let selected: Vec<_> = edges
        .iter()
        .filter(|e| {
            matches!(e.curve, Curve::Free(_))
                && e.pts
                    .iter()
                    .all(|p| p.x < -105.8 && p.y >= 11.0 - 1e-5 && p.y <= 17.0 + 1e-5)
        })
        .cloned()
        .collect();
    ensure!(
        selected.len() == 1,
        "the display corner is one analytic intersection, found{}",
        selected.len()
    );
    Ok(Edges(selected))
}

#[test]
fn display_roll_continues_from_the_cylinder_to_its_neighboring_faces() -> Result<()> {
    let body = preblend()?;
    let corner = display_corner(&body)?;
    assert!(
        body.fillet(&corner, 6.0).is_err(),
        "ordinary round keeps its original supported domain"
    );
    let result = body.rolling_fillet(&corner, 6.0)?;
    result.check()?;
    assert!(common::off_surface("display corner", &result) <= 2.0 * LINEAR);
    assert!(
        result.volume() < body.volume(),
        "the convex R6 round removes its corner"
    );
    let b = result.bounds();
    assert_eq!(b.min, body.bounds().min);
    assert_eq!(b.max, body.bounds().max);
    if let Some(directory) = std::env::var_os("HSM_ROLLING_REFERENCE") {
        let directory = std::path::Path::new(&directory);
        let before = import::model(directory.join("preblend.npz"))?
            .remove(0)
            .solid;
        let native = import::model(directory.join("one-edge-native.npz"))?
            .remove(0)
            .solid;
        let starting =
            common::hausdorff((body.verts(), body.tris()), (before.verts(), before.tris()));
        let from_native = before.rolling_fillet(&display_corner(&before)?, 6.0)?;
        let algorithm = common::hausdorff(
            (from_native.verts(), from_native.tris()),
            (native.verts(), native.tris()),
        );
        let surface = common::hausdorff(
            (result.verts(), result.tris()),
            (native.verts(), native.tris()),
        );
        println!(
            "starting surface{starting:.9}mm, rolling algorithm{algorithm:.9}mm, numeric fixture{surface:.9}mm; native volume{}, Rust volume{}",
            native.volume(),
            result.volume()
        );
        assert!(
            starting <= LINEAR,
            "the numeric profile matches its native fixture"
        );
        assert!(
            algorithm <= LINEAR,
            "rolling contacts match the native construction: {algorithm}"
        );
        assert!(
            surface <= LINEAR,
            "native-free display roll stays within the print rule: {surface}"
        );
    }
    Ok(())
}
