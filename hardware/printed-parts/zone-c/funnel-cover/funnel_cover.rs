//! The lift-off funnel cover: a solid plate, its front lifting relief, and the shallow locating
//! skirt, as it sits on the funnel and as it prints, flat exterior down.
//!
//!     funnel-cover [<output directory>]
#[path = "../funnel/zone_files.rs"]
#[allow(dead_code)]
mod zone_files;
use anyhow::Result;
use hsm_kernel::part::write_part;
use hsm_kernel::{Body, Loop, Plane, Profile, Region, Seg, Solid, V3, v2, v3};
use hsm_zone_c_numbers::cover::{Cover, Section, cover};

/// Square front corners toward the display and round aft corners over the silicone brim.
fn plate_plan(n: &Cover) -> Result<Profile> {
    let (x, y) = n.plate_half_size;
    let r = n.plate_corner_radius;
    let front = n.front_extension;
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

fn skirt_section(&[w, d, r, z]: &Section) -> Result<Region> {
    let profile = Profile::new(Loop::rounded_rect(v2(0.0, 0.0), w, d, r)?);
    Ok(profile.place(&Plane::XY.at(v3(0.0, 0.0, z))))
}

/// The cover in the assembly frame: Z = 0 is the brim-bearing underside of the plate.
fn build(n: &Cover) -> Result<Solid> {
    let plate = Plane::XY.extrude(&plate_plan(n)?, n.plate_thickness)?;
    let (relief_w, relief_d) = n.relief_size;
    let (relief_z0, relief_z1) = n.relief_z;
    let relief = Plane::XY.at(v3(0.0, n.relief_center_y, (relief_z0 + relief_z1) / 2.0)).cuboid(relief_w, relief_d, relief_z1 - relief_z0);
    let plate = plate.cut(&relief)?;
    let sections = n.skirt_sections.iter().map(skirt_section).collect::<Result<Vec<_>>>()?;
    let outside = Solid::loft(&sections)?;
    let [w, d, r, z0, z1] = n.skirt_inside;
    let inside = Plane::XY.at(v3(0.0, 0.0, z0)).extrude(&Profile::new(Loop::rounded_rect(v2(0.0, 0.0), w, d, r)?), z1 - z0)?;
    plate.union(&outside.cut(&inside)?)
}

fn main() -> Result<()> {
    let out = zone_files::out_dir("hardware/printed-parts/zone-c/funnel-cover")?;
    let n = cover();
    let seated = build(&n)?;
    // Flat exterior on the bed, with the skirt growing upward.
    let printed = seated.rotate(V3::ZERO, V3::X, 180.0).translate(v3(0.0, 0.0, n.plate_thickness));
    for (file_name, solid) in [("funnel-cover", &seated), ("funnel-cover-print", &printed)] {
        println!("{}", write_part(&out, file_name, &[Body { name: "funnel-cover", color: Some(n.color), solid }])?);
    }
    Ok(())
}
