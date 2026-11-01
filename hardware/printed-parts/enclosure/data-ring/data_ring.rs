//! The DATA trim in its original fitting frame, with continuous flat wings.
use anyhow::{Result, anyhow, ensure};
use hsm_enclosure_components::write_colored_part;
use hsm_kernel::part::{Numbers, args};
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V2, V3, v2, v3};
use serde_json::Value;

fn rounded(width: f64, height: f64, radius: f64, centre: V2, y0: f64, y1: f64) -> Result<Solid> {
    let outer = Loop::rounded_rect(centre, width, height, radius)?;
    Plane::XZ.at(v3(0.0, y0, 0.0)).extrude(
        &Profile {
            outer,
            holes: vec![],
        },
        -(y1 - y0),
    )
}

fn blank(n: &Numbers) -> Result<Solid> {
    let half = n.f("width")? / 2.0;
    let top = n.f("top")?;
    let bottom = n.f("bottom")?;
    let r = n.f("corner_radius")?;
    let a = v2(-half, top);
    let b = v2(-half, -bottom + r);
    let c = v2(-half + r, -bottom);
    let d = v2(half - r, -bottom);
    let e = v2(half, -bottom + r);
    let g = v2(half, top);
    let outer = Loop::new(vec![
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
    let mut body = Plane::XZ.extrude(
        &Profile {
            outer,
            holes: vec![],
        },
        -n.f("thick")?,
    )?;
    for side in [-1.0, 1.0] {
        let centre = v2(
            side * (half + (n.f("projection")? - 1.0) / 2.0),
            n.f("center_z")?,
        );
        body = body.union(&rounded(
            n.f("projection")? + 1.0,
            n.f("wing_span")?,
            n.f("wing_end_radius")?,
            centre,
            0.0,
            n.f("wing_thick")?,
        )?)?;
    }
    let cut = rounded(
        n.f("opening_width")?,
        n.f("opening_height")?,
        n.f("opening_radius")?,
        V2::ZERO,
        -n.f("opening_overrun")?,
        n.f("thick")? + n.f("opening_overrun")?,
    )?;
    body.cut(&cut)
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let glyphs = word_profiles(n.get("word_profiles")?, n.f("word_scale")?)?;
    let letters = glyphs
        .iter()
        .map(|p| Plane::XY.extrude(p, n.f("word_depth")? + n.f("word_raise")?))
        .collect::<Result<Vec<_>>>()?;
    let letters = Solid::compose(&letters)
        .rotate(V3::ZERO, V3::X, 90.0)
        .rotate(V3::ZERO, V3::Z, 180.0);
    let b = letters.bounds();
    let word = letters.translate(v3(
        -(b.min.x + b.max.x) / 2.0,
        n.f("thick")? - n.f("word_depth")? - b.min.y,
        (n.f("word_band_bottom")? + n.f("top")?) / 2.0 - (b.min.z + b.max.z) / 2.0,
    ));
    let plain = blank(&n)?;
    let body = plain.cut(&word)?;
    let exterior = plain.union(&word)?;
    let bodies = [
        Body {
            name: "data-ring",
            color: Some(n.color("chip_color")?),
            solid: &body,
        },
        Body {
            name: "data-ring-word",
            color: Some(n.color("word_color")?),
            solid: &word,
        },
    ];
    println!(
        "{}",
        write_colored_part(&out, "data-ring", &bodies, &exterior)?
    );
    Ok(())
}

/// The shared label artwork's line and Bézier controls, with counters already nested.
fn word_profiles(profiles: &Value, scale: f64) -> Result<Vec<Profile>> {
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
    list(profiles)?
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
