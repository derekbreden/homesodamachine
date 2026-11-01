//! The six sliding rear identification tiles, in their individual fitting frames.
//! `rear_identification.py` reads their exact bores and grid datums from above-core.json.
use anyhow::{Result, anyhow, ensure};
use hsm_enclosure_components::write_colored_part;
use hsm_kernel::part::{Numbers, args};
use hsm_kernel::{Body, Font, HAlign, Kind, Plane, Solid, V3, VAlign, v3};
use serde_json::{Value, json};

fn f(v: &Value, key: &str) -> Result<f64> {
    v[key].as_f64().ok_or_else(|| anyhow!("`{key}` is not a number"))
}

fn text<'a>(v: &'a Value, key: &str) -> Result<&'a str> {
    v[key].as_str().ok_or_else(|| anyhow!("`{key}` is not text"))
}

fn color(v: &Value, key: &str) -> Result<[f64; 3]> {
    let a = v[key].as_array().ok_or_else(|| anyhow!("`{key}` is not a color"))?;
    ensure!(a.len() == 3, "a color has three channels");
    Ok([a[0].as_f64().unwrap(), a[1].as_f64().unwrap(), a[2].as_f64().unwrap()])
}

fn build(n: &Numbers, station: &Value, font: &Font) -> Result<(Solid, Solid, Solid)> {
    let (thick, depth, rise) = (n.f("thick")?, n.f("word_depth")?, n.f("word_raise")?);
    let profiles = font.profiles_with_kerning(text(station, "word")?, n.f("word_size")?,
                                               HAlign::Center, VAlign::Center, false)?;
    let glyphs = profiles.iter().map(|p| Plane::XY.extrude(p, depth + rise))
        .collect::<Result<Vec<_>>>()?;
    let letters = Solid::compose(&glyphs)
        .rotate(V3::ZERO, V3::X, 90.0).rotate(V3::ZERO, V3::Z, 180.0);
    let bounds = letters.bounds();
    let word = letters.translate(v3(
        -(bounds.min.x + bounds.max.x) / 2.0,
        thick - depth - bounds.min.y,
        (n.f("word_band_bottom")? + f(station, "top")?) / 2.0
            - (bounds.min.z + bounds.max.z) / 2.0,
    ));
    let blank = Solid::cuboid(v3(-n.f("width")? / 2.0, 0.0, -n.f("bottom")?),
                              v3(n.f("width")? / 2.0, thick, f(station, "top")?));
    let bore = Solid::cylinder(v3(f(station, "bore_x")?, -n.f("bore_overrun")?,
                                  f(station, "bore_z")?), V3::Y,
                               f(station, "bore_diameter")? / 2.0,
                               thick + 2.0 * n.f("bore_overrun")?)?;
    let body = blank.cut_all(&[bore.clone(), word.clone()])?;
    // The single-material print joins the word through its full inlay depth.
    let exterior = blank.cut(&bore)?.union(&word)?;
    Ok((body, word, exterior))
}

fn main() -> Result<()> {
    let check = std::env::args().nth(2).as_deref() == Some("--check");
    let (n, out) = if check {
        (Numbers::read(std::env::args().nth(1).unwrap_or_default())?, std::path::PathBuf::new())
    } else {
        args()?
    };
    let kind = match n.text("word_kind")? {
        "regular" => Kind::Regular,
        "bold" => Kind::Bold,
        "italic" => Kind::Italic,
        "bolditalic" | "bold-italic" => Kind::BoldItalic,
        other => return Err(anyhow!("unsupported font kind {other}")),
    };
    let font = Font::find(n.text("word_font")?, kind)?;
    let mut checks = vec![];
    for station in n.get("stations")?.as_array().ok_or_else(|| anyhow!("stations is not a list"))? {
        let (body, word, exterior) = build(&n, station, &font)?;
        let name = text(station, "name")?;
        if check {
            body.check()?;
            word.check()?;
            exterior.check()?;
            let overlap = body.intersect(&word)?.volume();
            ensure!(body.components().len() == 1 && overlap < 1e-6,
                    "{name} must have one body with no shared filament volume");
            let width = word.bounds().size().x;
            ensure!((width - f(station, "word_width")?).abs() <= 1e-3,
                    "{name} resolves to a different font face: width {width}");
            checks.push(json!({"name": name, "body_components": 1, "overlap_mm3": overlap,
                                "word_width_mm": width, "font": font.name}));
            continue;
        }
        let bodies = [
            Body { name: text(station, "body_name")?, color: Some(color(station, "chip_color")?), solid: &body },
            Body { name: text(station, "word_name")?, color: Some(color(station, "word_color")?), solid: &word },
        ];
        println!("{}", write_colored_part(&out, name, &bodies, &exterior)?);
    }
    if check {
        println!("{}", json!({"labels": checks}));
    }
    Ok(())
}
