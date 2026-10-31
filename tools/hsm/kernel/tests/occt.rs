//! Every builder and operation against OCCT's volume and bounds for the same model, within the
//! tessellation rule: the mesh volume is OCCT's to within LINEAR × the surface area, the bounds
//! to within LINEAR, and every plane face points where its record says. A builder puts every
//! vertex on the exact surface its face record names; a boolean's new vertices lie on the
//! operands' facets, within twice LINEAR of the surface.
mod common;
use common::matches_occt;
use hsm_kernel::*;

const Z: V3 = V3::Z;

fn report(name: &str, s: &Solid, on_surface: f64) {
    let (rel, off) = matches_occt(name, s, on_surface);
    println!("{name:16} {:7} triangles  volume off OCCT's by {rel:+.2e}  farthest vertex off its surface {off:.1e}", s.tris().len());
}

fn check(name: &str, s: Solid) {
    report(name, &s, 1e-6);
}

fn check_boolean(name: &str, s: Solid) {
    report(name, &s, 2.0 * LINEAR);
}

#[test]
fn box_() {
    check("box", Solid::cuboid(V3::ZERO, v3(10.0, 20.0, 30.0)));
}

#[test]
fn cylinders() -> anyhow::Result<()> {
    check("cylinder", Solid::cylinder(V3::ZERO, Z, 5.0, 12.0)?);
    check("cylinder_tilted", Solid::cylinder(v3(1.0, 2.0, 3.0), v3(1.0, 1.0, 0.5), 3.2, 7.0)?);
    check("cylinder_sector", Solid::cylinder_sector(V3::ZERO, Z, 5.0, 10.0, 120.0)?);
    Ok(())
}

#[test]
fn cones() -> anyhow::Result<()> {
    check("cone", Solid::cone(V3::ZERO, Z, 6.0, 2.0, 9.0)?);
    check("cone_point", Solid::cone(V3::ZERO, Z, 4.0, 0.0, 5.0)?);
    Ok(())
}

#[test]
fn sphere_and_torus() -> anyhow::Result<()> {
    check("sphere", Solid::sphere(V3::ZERO, 7.0)?);
    check("torus", Solid::torus(V3::ZERO, Z, 10.0, 3.0)?);
    Ok(())
}

#[test]
fn wedge() -> anyhow::Result<()> {
    check("wedge", Solid::wedge(&Plane::XY, 10.0, 8.0, 6.0, 2.0, 1.0, 7.0, 4.0)?);
    Ok(())
}

#[test]
fn extrusions() -> anyhow::Result<()> {
    let holed = Profile::rect(V2::ZERO, 20.0, 10.0).with_hole(Loop::circle(V2::ZERO, 3.0));
    check("extrude_holed", Plane::XY.extrude(&holed, 5.0)?);
    check("extrude_slot", Plane::XY.extrude(&Profile::new(Loop::slot(V2::ZERO, 30.0, 8.0, 20.0)), 4.0)?);
    let rounded = Profile::new(Loop::rounded_rect(V2::ZERO, 20.0, 12.0, 3.0)?);
    check("extrude_rounded", Plane::XY.extrude(&rounded, 3.0)?);
    let grown = Profile::rect(V2::ZERO, 20.0, 12.0).offset(2.0, true)?;
    check("extrude_offset", Plane::XY.extrude(&grown, 3.0)?);
    let section = Profile::polygon(&[v2(0.0, 0.0), v2(6.0, 0.0), v2(6.0, 3.0), v2(2.0, 5.0), v2(0.0, 5.0)]);
    check("extrude_yz", Plane::YZ.at(v3(-2.0, 0.0, 0.0)).extrude(&section, 4.0)?);
    Ok(())
}

#[test]
fn revolutions() -> anyhow::Result<()> {
    let ring = Profile::polygon(&[v2(5.0, 0.0), v2(9.0, 0.0), v2(9.0, 6.0), v2(5.0, 6.0)]);
    check("revolve_partial", Plane::XZ.revolve(&ring, 270.0, v2(0.0, 0.0), v2(0.0, 1.0))?);
    let bulged = Pen::new(v2(3.0, 0.0))
        .line_to(v2(8.0, 0.0))
        .arc_through(v2(10.0, 2.0), v2(8.0, 4.0))?
        .line_to(v2(3.0, 4.0))
        .close()?;
    check("revolve_arc", Plane::XZ.revolve(&Profile::new(bulged), 360.0, v2(0.0, 0.0), v2(0.0, 1.0))?);
    Ok(())
}

#[test]
fn drafts() -> anyhow::Result<()> {
    check("drafted_rect", Plane::XY.extrude_drafted(&Profile::rect(V2::ZERO, 20.0, 10.0), 8.0, 5.0)?);
    check("drafted_circle", Plane::XY.extrude_drafted(&Profile::circle(V2::ZERO, 6.0), 5.0, 10.0)?);
    Ok(())
}

#[test]
fn booleans() -> anyhow::Result<()> {
    let cube = Plane::XY.cuboid(10.0, 10.0, 10.0);
    check_boolean("union_boxes", cube.union(&cube.translate(v3(5.0, 5.0, 5.0)))?);
    let bore = Solid::cylinder(v3(0.0, 0.0, -6.0), Z, 4.0, 12.0)?;
    check_boolean("cut_bore", Plane::XY.cuboid(20.0, 20.0, 10.0).cut(&bore)?);
    check_boolean("intersect_ball", cube.intersect(&Solid::sphere(V3::ZERO, 6.5)?)?);
    let block = Solid::cuboid(V3::ZERO, v3(100.0, 60.0, 10.0));
    let pins: Vec<Solid> = (0..10)
        .flat_map(|i| (0..6).map(move |j| (i, j)))
        .map(|(i, j)| Solid::cylinder(v3(5.0 + 10.0 * i as f64, 5.0 + 10.0 * j as f64, -1.0), Z, 2.5, 12.0))
        .collect::<anyhow::Result<_>>()?;
    check_boolean("holes_60", block.cut_all(&pins)?);
    let (top, bottom) = Solid::cuboid(V3::ZERO, v3(10.0, 10.0, 10.0)).split(&Plane::XY.at(v3(0.0, 0.0, 3.0)))?;
    check_boolean("split_top", top);
    check_boolean("split_bottom", bottom);
    Ok(())
}

/// Every face of `s` on an exact surface, and how many of each kind.
fn analytic(name: &str, s: &Solid) -> std::collections::BTreeMap<&'static str, usize> {
    let mut kinds = std::collections::BTreeMap::new();
    for f in s.faces() {
        assert!(f.surface.is_analytic(), "{name}: {f}");
        *kinds.entry(f.surface.kind()).or_insert(0) += 1;
    }
    println!("{name:16} face records {kinds:?}");
    kinds
}

#[test]
fn sweeps() -> anyhow::Result<()> {
    let q = std::f64::consts::PI / 4.0;
    let bend = Path::new(V3::ZERO)
        .line_to(v3(0.0, 0.0, 20.0))
        .arc_through(v3(10.0 - 10.0 * q.cos(), 0.0, 20.0 + 10.0 * q.sin()), v3(10.0, 0.0, 30.0))?;
    let rod = Plane::XY.sweep(&Profile::circle(V2::ZERO, 2.0), &bend)?;
    let kinds = analytic("sweep_bend", &rod);
    assert_eq!((kinds["CYLINDER"], kinds["TORUS"], kinds["PLANE"]), (1, 1, 2));
    check("sweep_bend", rod);
    let annulus = Profile::circle(V2::ZERO, 3.0).with_hole(Loop::circle(V2::ZERO, 2.0));
    let tube = Plane::XY.sweep(&annulus, &bend.line_to(v3(25.0, 0.0, 30.0)))?;
    let kinds = analytic("sweep_tube", &tube);
    assert_eq!((kinds["CYLINDER"], kinds["TORUS"], kinds["PLANE"]), (4, 2, 2));
    check("sweep_tube", tube);
    Ok(())
}

#[test]
fn lofts() -> anyhow::Result<()> {
    let rects = [
        Profile::rect(V2::ZERO, 10.0, 10.0).place(&Plane::XY),
        Profile::rect(V2::ZERO, 6.0, 6.0).place(&Plane::XY.offset(8.0)),
    ];
    let frustum = Solid::loft(&rects)?;
    assert_eq!(analytic("loft_rects", &frustum)["PLANE"], 6);
    check("loft_rects", frustum);
    let circles = [
        Profile::circle(V2::ZERO, 5.0).place(&Plane::XY),
        Profile::circle(V2::ZERO, 3.0).place(&Plane::XY.offset(10.0)),
    ];
    let cone = Solid::loft(&circles)?;
    let kinds = analytic("loft_circles", &cone);
    assert_eq!((kinds["CONE"], kinds["PLANE"]), (1, 2));
    check("loft_circles", cone);
    Ok(())
}

/// Text in the system's Arial and Helvetica, the faces OCCT's font manager finds for the same
/// family and kind.
#[test]
fn text() -> anyhow::Result<()> {
    let arial = Font::find("Arial", Kind::Regular)?;
    let arial_bold = Font::find("Arial", Kind::Bold)?;
    let helvetica_bold = Font::find("Helvetica", Kind::Bold)?;
    println!("faces: {}, {}, {}", arial.name, arial_bold.name, helvetica_bold.name);
    let (c, l, r, t, b) = (HAlign::Center, HAlign::Left, HAlign::Right, VAlign::Top, VAlign::Bottom);
    check("text", Plane::XY.text(&arial, "HSM", 10.0, 2.0, c, VAlign::Center)?);
    check("text_left", Plane::XY.text(&arial, "go", 8.0, 1.5, l, b)?);
    check("text_right_top", Plane::XY.text(&arial, "HSM", 6.0, 1.0, r, t)?);
    check("text_arial_bold", Plane::XY.text(&arial_bold, "AV Ta", 4.0, 0.6, c, VAlign::Center)?);
    check("text_helvetica_bold", Plane::XY.text(&helvetica_bold, "Ab8", 5.0, 0.48, c, VAlign::Center)?);
    Ok(())
}
