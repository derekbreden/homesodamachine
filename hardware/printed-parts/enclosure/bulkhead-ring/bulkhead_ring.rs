//! The six fitting-frame rear chips and their inlaid, raised words.
use anyhow::{Result, anyhow, ensure};
use hsm_enclosure_components::write_colored_part;
use hsm_kernel::part::{Numbers, args};
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V2, V3, v2, v3};
use serde_json::{Value, json};

fn f(v: &Value, key: &str) -> Result<f64> {
    v[key].as_f64().ok_or_else(|| anyhow!("`{key}` is numeric"))
}

fn text<'a>(v: &'a Value, key: &str) -> Result<&'a str> {
    v[key].as_str().ok_or_else(|| anyhow!("`{key}` is text"))
}

fn color(v: &Value, key: &str) -> Result<[f64; 3]> {
    let a = v[key]
        .as_array()
        .ok_or_else(|| anyhow!("`{key}` is a color"))?;
    ensure!(a.len() == 3, "a color has three channels");
    let values = a
        .iter()
        .map(|v| {
            v.as_f64()
                .ok_or_else(|| anyhow!("a color channel is numeric"))
        })
        .collect::<Result<Vec<_>>>()?;
    Ok([values[0], values[1], values[2]])
}

fn blank(n: &Numbers, station: &Value) -> Result<Solid> {
    let half = f(station, "width")? / 2.0;
    let top = f(station, "top")?;
    let bottom = f(station, "bottom")?;
    let r = n.f("lower_corner_radius")?;
    let a = v2(-half, top);
    let b = v2(-half, -bottom + r);
    let c = v2(-half + r, -bottom);
    let d = v2(half - r, -bottom);
    let e = v2(half, -bottom + r);
    let g = v2(half, top);
    let outline = Loop::new(vec![
        Seg::Line { a, b },
        Seg::Arc {
            a: b,
            b: c,
            c: v2(-half + r, -bottom + r),
            ccw: true,
        },
        Seg::Line { a: c, b: d },
        Seg::Arc {
            a: d,
            b: e,
            c: v2(half - r, -bottom + r),
            ccw: true,
        },
        Seg::Line { a: e, b: g },
        Seg::Line { a: g, b: a },
    ])?;
    Plane::XZ.extrude(
        &Profile {
            outer: outline,
            holes: vec![],
        },
        -n.f("thick")?,
    )
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let (thick, depth, raise) = (n.f("thick")?, n.f("word_depth")?, n.f("word_raise")?);
    for station in n
        .get("stations")?
        .as_array()
        .ok_or_else(|| anyhow!("stations is a list"))?
    {
        let profiles = word_profiles(station, n.f("word_scale")?)?;
        let glyphs = profiles
            .iter()
            .map(|p| Plane::XY.extrude(p, depth + raise))
            .collect::<Result<Vec<_>>>()?;
        let letters = Solid::compose(&glyphs)
            .rotate(V3::ZERO, V3::X, 90.0)
            .rotate(V3::ZERO, V3::Z, 180.0);
        let bounds = letters.bounds();
        let word = letters.translate(v3(
            -(bounds.min.x + bounds.max.x) / 2.0,
            thick - depth - bounds.min.y,
            (f(station, "flange_radius")? + f(station, "top")?) / 2.0
                - (bounds.min.z + bounds.max.z) / 2.0,
        ));
        let bore = Solid::cylinder(V3::ZERO, V3::Y, f(station, "bore_diameter")? / 2.0, thick)?;
        let plain = blank(&n, station)?.cut(&bore)?;
        let body = plain.cut(&word)?;
        let exterior = plain.union(&word)?;
        let flange = Solid::cylinder(
            v3(0.0, thick, 0.0),
            V3::Y,
            f(station, "flange_radius")?,
            depth + raise,
        )?;
        let clearance = word.gap(&flange)?;
        let name = text(station, "name")?;
        let bodies = [
            Body {
                name,
                color: Some(color(station, "chip_color")?),
                solid: &body,
            },
            Body {
                name: text(station, "word_name")?,
                color: Some(color(station, "word_color")?),
                solid: &word,
            },
        ];
        let mut said = write_colored_part(&out, name, &bodies, &exterior)?;
        said["bodies"][0]["word_flange_clearance_mm"] = json!(clearance);
        println!("{said}");
    }
    Ok(())
}

/// The shared label artwork's line and Bézier controls, with counters already nested.
fn word_profiles(station: &Value, scale: f64) -> Result<Vec<Profile>> {
    fn list(v: &Value) -> Result<&Vec<Value>> {
        v.as_array()
            .ok_or_else(|| anyhow!("label contours are a list"))
    }
    let point = |v: &Value| -> Result<V2> {
        let a = list(v)?;
        ensure!(a.len() == 2, "a label point has two coordinates");
        Ok(v2(
            a[0].as_f64().ok_or_else(|| anyhow!("label X is numeric"))?,
            a[1].as_f64().ok_or_else(|| anyhow!("label Y is numeric"))?,
        ) * scale)
    };
    let outline = |v: &Value| -> Result<Loop> {
        let segs = list(v)?
            .iter()
            .map(|v| {
                let (kind, controls) = v
                    .as_object()
                    .and_then(|v| v.iter().next())
                    .ok_or_else(|| anyhow!("a label segment has controls"))?;
                let p = list(controls)?
                    .iter()
                    .map(&point)
                    .collect::<Result<Vec<_>>>()?;
                Ok(match (kind.as_str(), p.as_slice()) {
                    ("line", &[a, b]) => Seg::Line { a, b },
                    ("quad", &[a, c, b]) => Seg::Quad { a, c, b },
                    ("cubic", &[a, c1, c2, b]) => Seg::Cubic { a, c1, c2, b },
                    _ => return Err(anyhow!("invalid label {kind} segment")),
                })
            })
            .collect::<Result<Vec<_>>>()?;
        Loop::new(segs)
    };
    list(&station["word_profiles"])?
        .iter()
        .map(|p| {
            Ok(Profile {
                outer: outline(&p["outer"])?,
                holes: list(&p["holes"])?
                    .iter()
                    .map(&outline)
                    .collect::<Result<Vec<_>>>()?,
            })
        })
        .collect()
}
