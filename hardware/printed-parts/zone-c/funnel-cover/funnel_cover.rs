//! The lift-off funnel cover: a solid plate, its front lifting relief, and the shallow
//! locating skirt. `funnel_cover.py` supplies the dimensions from the funnel it closes on.
use anyhow::{Context, Result, ensure};
use hsm_kernel::part::{Numbers, args, write_part};
use hsm_kernel::{Body, Loop, Plane, Profile, Region, Seg, Solid, V3, v2, v3};
use serde_json::Value;

/// Square front corners toward the display and round aft corners over the silicone brim.
fn plate_plan(n: &Numbers) -> Result<Profile> {
    let (x, y) = n.pair("plate_half_size")?;
    let r = n.f("plate_corner_radius")?;
    let front = n.f("front_extension")?;
    let a = v2(-x, -y - front);
    let b = v2(x, -y - front);
    let c = v2(x, y - r);
    let d = v2(x - r, y);
    let e = v2(-x + r, y);
    let f = v2(-x, y - r);
    Ok(Profile::new(Loop::new(vec![
        Seg::Line { a, b },
        Seg::Line { a: b, b: c },
        Seg::Arc { a: c, b: d, c: v2(x - r, y - r), ccw: true },
        Seg::Line { a: d, b: e },
        Seg::Arc { a: e, b: f, c: v2(-x + r, y - r), ccw: true },
        Seg::Line { a: f, b: a },
    ])?))
}

fn row(value: &Value) -> Result<Vec<f64>> {
    value.as_array().context("a skirt section is [width, depth, radius, z]")?.iter()
        .map(|v| v.as_f64().context("a skirt section holds numbers"))
        .collect()
}

fn skirt_section(value: &Value) -> Result<Region> {
    let a = row(value)?;
    ensure!(a.len() == 4, "a skirt section is [width, depth, radius, z]");
    let profile = Profile::new(Loop::rounded_rect(v2(0.0, 0.0), a[0], a[1], a[2])?);
    Ok(profile.place(&Plane::XY.at(v3(0.0, 0.0, a[3]))))
}

/// The cover in the assembly frame: Z=0 is the brim-bearing underside of the plate.
pub fn build(n: &Numbers) -> Result<Solid> {
    let plate = Plane::XY.extrude(&plate_plan(n)?, n.f("plate_thickness")?)?;
    let (relief_w, relief_d) = n.pair("relief_size")?;
    let (relief_z0, relief_z1) = n.pair("relief_z")?;
    let relief = Plane::XY.at(v3(0.0, n.f("relief_center_y")?, (relief_z0 + relief_z1) / 2.0))
        .cuboid(relief_w, relief_d, relief_z1 - relief_z0);
    let plate = plate.cut(&relief)?;

    let sections = n.get("skirt_sections")?.as_array().context("skirt_sections is a list")?
        .iter().map(skirt_section).collect::<Result<Vec<_>>>()?;
    let outside = Solid::loft(&sections)?;
    let inside_size = n.list("skirt_inside")?;
    ensure!(inside_size.len() == 5, "skirt_inside is [width, depth, radius, z0, z1]");
    let inside = Profile::new(Loop::rounded_rect(
        v2(0.0, 0.0), inside_size[0], inside_size[1], inside_size[2],
    )?);
    let inside = Plane::XY.at(v3(0.0, 0.0, inside_size[3]))
        .extrude(&inside, inside_size[4] - inside_size[3])?;
    let skirt = outside.cut(&inside)?;
    plate.union(&skirt)
}

/// Flat exterior on the bed, with the skirt growing upward.
pub fn print_shape(n: &Numbers, cover: &Solid) -> Result<Solid> {
    Ok(cover.rotate(V3::ZERO, V3::X, 180.0).translate(v3(0.0, 0.0, n.f("plate_thickness")?)))
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let cover = build(&n)?;
    let printed = print_shape(&n, &cover)?;
    let color = Some(n.color("color")?);
    let body_name = n.text("name")?;
    for (file_name, solid) in [(body_name, &cover), (n.text("print_name")?, &printed)] {
        println!("{}", write_part(&out, file_name, &[Body { name: body_name, color, solid }])?);
    }
    Ok(())
}
