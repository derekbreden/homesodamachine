//! Manual native-scale scan reconstruction of the ACVUS44 exterior.
use anyhow::{Context, Result};
use hsm_kernel::part::{args, write_part};
use hsm_kernel::{Body, Plane, Profile, Solid, V2, V3, v2, v3};

fn main() -> Result<()> {
    let (n, out) = args()?;
    let length = n.f("length_mm")?;
    let rows = n.get("profile_x_radius_mm")?.as_array().context("profile")?;
    let mut profile = vec![V2::ZERO];
    for row in rows {
        profile.push(v2(row[0].as_f64().context("station")?,
                        row[1].as_f64().context("radius")?));
    }
    profile.push(v2(length, 0.));
    let body = Plane::XY.revolve(&Profile::polygon(&profile), 360., V2::ZERO, v2(1., 0.))?
        .cut(&Solid::cylinder(v3(-0.1, 0., 0.), V3::X,
                              n.f("through_bore_display_mm")? / 2., length+0.2)?)?
        .cut(&Solid::cylinder(v3(length+0.1, 0., 0.), -V3::X,
                              n.f("socket_display_diameter_mm")? / 2.,
                              n.f("socket_insertion_estimate_mm")?+0.1)?)?;
    println!("{}", write_part(&out, "neofit-acvus44-check", &[
        Body { name: "stem-check", color: Some(n.color("color")?), solid: &body },
    ])?);
    Ok(())
}
