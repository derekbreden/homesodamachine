//! The six sliding rear identification tiles, in their individual fitting frames.
//! `rear_identification.py` reads their exact bores and grid datums from above-core.json.
use anyhow::{Result, anyhow, ensure};
use hsm_enclosure_components::write_colored_part;
use hsm_kernel::part::{Numbers, args};
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V2, V3, v2, v3};
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

fn build(n: &Numbers, station: &Value) -> Result<(Solid, Solid, Solid)> {
    let (thick, depth, rise) = (n.f("thick")?, n.f("word_depth")?, n.f("word_raise")?);
    let profiles = word_profiles(station, n.f("word_size")? / n.f("word_profiles_em")?)?;
    let glyphs = profiles.iter().map(|p| Plane::XY.extrude(p, depth + rise))
        .collect::<Result<Vec<_>>>()?;
    let letters = Solid::compose(&glyphs)
        .rotate(V3::ZERO, V3::X, 90.0).rotate(V3::ZERO, V3::Z, 180.0);
    let bounds = letters.bounds();
    let word = letters.translate(v3(
        -(bounds.min.x + bounds.max.x) / 2.0,
        thick - depth - bounds.min.y,
        f(station, "word_center_z")?
            - (bounds.min.z + bounds.max.z) / 2.0,
    ));
    let blank = Solid::cuboid(v3(-n.f("width")? / 2.0, 0.0, -f(station,"bottom")?),
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
    let mut checks = vec![];
    for station in n.get("stations")?.as_array().ok_or_else(|| anyhow!("stations is not a list"))? {
        let (body, word, exterior) = build(&n, station)?;
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
                                "word_width_mm": width, "font": n.text("word_font")?}));
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

/// The label artwork's original line and Bézier controls, with counters already nested.
fn word_profiles(station: &Value, scale: f64) -> Result<Vec<Profile>> {
    fn list(v: &Value) -> Result<&Vec<Value>> {
        v.as_array().ok_or_else(|| anyhow!("label contours are a list"))
    }
    let point = |v: &Value| -> Result<V2> {
        let a = v.as_array().ok_or_else(|| anyhow!("a label point has two coordinates"))?;
        ensure!(a.len() == 2, "a label point has two coordinates");
        Ok(v2(a[0].as_f64().ok_or_else(|| anyhow!("label X is numeric"))?,
              a[1].as_f64().ok_or_else(|| anyhow!("label Y is numeric"))?) * scale)
    };
    let outline = |v: &Value| -> Result<Loop> {
        let segs = list(v)?.iter().map(|v| {
            let (kind, controls) = v.as_object().and_then(|v| v.iter().next())
                .ok_or_else(|| anyhow!("a label segment has controls"))?;
            let p = list(controls)?.iter().map(&point).collect::<Result<Vec<_>>>()?;
            Ok(match (kind.as_str(), p.as_slice()) {
                ("line", &[a,b]) => Seg::Line { a,b },
                ("quad", &[a,c,b]) => Seg::Quad { a,c,b },
                ("cubic", &[a,c1,c2,b]) => Seg::Cubic { a,c1,c2,b },
                _ => return Err(anyhow!("invalid label {kind} segment")),
            })
        }).collect::<Result<Vec<_>>>()?;
        Loop::new(segs)
    };
    list(&station["word_profiles"])?.iter().map(|p| {
        Ok(Profile { outer: outline(&p["outer"])?,
                     holes: list(&p["holes"])?.iter().map(&outline).collect::<Result<Vec<_>>>()? })
    }).collect()
}
