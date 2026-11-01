//! The guided one-piece ASA Aero float and its RC62 insertion views.
//! `all_aero_float.py` holds the dimensions and writes these numbers.
use anyhow::{ensure, Result};
use hsm_kernel::part::{args, write_part, write_shown, Numbers};
use hsm_kernel::*;

fn annulus(outer: f64, inner: f64, bottom: f64, top: f64) -> Result<Solid> {
    let section = Profile::circle(v2(0.0, 0.0), outer).with_hole(Loop::circle(v2(0.0, 0.0), inner));
    Plane::XY
        .at(v3(0.0, 0.0, bottom))
        .extrude(&section, top - bottom)
}

fn build(n: &Numbers) -> Result<(Solid, Solid)> {
    let body = annulus(
        n.f("diameter")? / 2.0,
        n.f("bore_diameter")? / 2.0,
        0.0,
        n.f("height")?,
    )?
    .cut(&annulus(
        n.f("pocket_od")? / 2.0,
        n.f("pocket_id")? / 2.0,
        n.f("magnet_seat")?,
        n.f("pocket_roof")?,
    )?)?;
    let magnet = annulus(
        n.f("magnet_od")? / 2.0,
        n.f("magnet_id")? / 2.0,
        n.f("magnet_seat")?,
        n.f("magnet_seat")? + n.f("magnet_thickness")?,
    )?;
    body.check()?;
    ensure!(
        body.components().len() == 1,
        "float-aero is one connected body"
    );
    ensure!(
        body.intersect(&magnet)?.volume() < 1e-7,
        "RC62 intrudes into the float body"
    );
    Ok((body, magnet))
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let (body, magnet) = build(&n)?;
    let (aero, metal) = (n.color("color_aero")?, n.color("color_magnet")?);
    let (diameter, height) = (n.f("diameter")?, n.f("height")?);
    println!(
        "{}",
        write_part(
            &out,
            "float-aero",
            &[Body {
                name: "float-aero",
                color: Some(aero),
                solid: &body
            },]
        )?
    );

    let half = Solid::cuboid(
        v3(-diameter / 2.0 - 1.0, -diameter, -1.0),
        v3(diameter / 2.0 + 1.0, 0.0, height + 1.0),
    );
    let cut_body = body.intersect(&half)?;
    let cut_magnet = magnet.intersect(&half)?;
    // Open the same annular pocket through the insertion view's top plane.
    // Extending its cutter to the existing full height avoids retaining the
    // coincident roof as a zero-thickness internal sheet.
    let open_body = annulus(
        diameter / 2.0,
        n.f("bore_diameter")? / 2.0,
        0.0,
        n.f("pocket_roof")?,
    )?
    .cut(&annulus(
        n.f("pocket_od")? / 2.0,
        n.f("pocket_id")? / 2.0,
        n.f("magnet_seat")?,
        height,
    )?)?;
    let raised_magnet = magnet.translate(v3(0.0, 0.0, n.f("insertion_lift")?));
    for (name, shown) in [
        (
            "assembly",
            vec![
                Body {
                    name: "float-aero",
                    color: Some(aero),
                    solid: &body,
                },
                Body {
                    name: "RC62",
                    color: Some(metal),
                    solid: &magnet,
                },
            ],
        ),
        (
            "section",
            vec![
                Body {
                    name: "float-aero",
                    color: Some(aero),
                    solid: &cut_body,
                },
                Body {
                    name: "RC62",
                    color: Some(metal),
                    solid: &cut_magnet,
                },
            ],
        ),
        (
            "insertion",
            vec![
                Body {
                    name: "printed-open-pocket",
                    color: Some(aero),
                    solid: &open_body,
                },
                Body {
                    name: "insert-RC62",
                    color: Some(metal),
                    solid: &raised_magnet,
                },
            ],
        ),
    ] {
        println!("{}", write_shown(&out, name, &shown)?);
    }
    Ok(())
}
