//! The DATA trim: the black identification plate round the data jack, its white lettering raised
//! through the face, and the two flat wings it seats by, in its own fitting frame.
//!
//!     data-ring [<output directory>]
use anyhow::{Result, anyhow, ensure};
use hsm_enclosure_components::{output, port_colors, write_colored_part};
use hsm_enclosure_numbers::rear_wall;
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V2, V3, v2, v3};
use serde_json::Value;

/// The plate's face: its width, how far it stands above and below the jack's centre, its lower
/// corners' radius and its depth; the opening round the jack, and how far that cut runs past
/// both faces.
const WIDTH: f64 = 32.0;
const TOP: f64 = 18.789;
const BOTTOM: f64 = 11.0;
const CORNER: f64 = 2.0;
const THICK: f64 = WING_THICK;
const OPENING: [f64; 3] = [20.8, 18.3, 0.4];
const OVERRUN: f64 = 0.01;
const CENTER_Z: f64 = (TOP - BOTTOM) / 2.0;

/// The wings, the wing nameplate's: their depth, how far each projects past the face, their
/// rounded ends, and the span they leave, short of the face's ends by the nameplate's own insets.
const WING_THICK: f64 = 1.68;
const PROJECTION: f64 = rear_wall::WING_PROJECTION;
const WING_END_RADIUS: f64 = 0.6;
const NAMEPLATE_HEIGHT: f64 = 38.0;
const WING_END_INSET: f64 = (NAMEPLATE_HEIGHT - rear_wall::WING_SPAN) / 2.0;
const WING_SPAN: f64 = TOP + BOTTOM - 2.0 * WING_END_INSET;

/// The lettering: how far it sinks into the face and stands proud of it, the bulkhead rings'
/// letter size, and the foot of the band it centres in.
const WORD_DEPTH: f64 = 0.72;
const WORD_RAISE: f64 = 0.48;
const WORD_SIZE: f64 = 6.5;
const WORD_BAND_BOTTOM: f64 = 11.0;

/// The word's outlines, set once in its typeface, at their em.
const WORD: &str = include_str!("data-word.json");

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

fn blank() -> Result<Solid> {
    let half = WIDTH / 2.0;
    let top = TOP;
    let bottom = BOTTOM;
    let r = CORNER;
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
        -THICK,
    )?;
    for side in [-1.0, 1.0] {
        let centre = v2(
            side * (half + (PROJECTION - 1.0) / 2.0),
            CENTER_Z,
        );
        body = body.union(&rounded(
            PROJECTION + 1.0,
            WING_SPAN,
            WING_END_RADIUS,
            centre,
            0.0,
            WING_THICK,
        )?)?;
    }
    let cut = rounded(
        OPENING[0],
        OPENING[1],
        OPENING[2],
        V2::ZERO,
        -OVERRUN,
        THICK + OVERRUN,
    )?;
    body.cut(&cut)
}

fn main() -> Result<()> {
    let out = output("data-ring", "hardware/printed-parts/enclosure/data-ring")?;
    let word: Value = serde_json::from_str(WORD)?;
    let em = word["em_mm"].as_f64().ok_or_else(|| anyhow!("the word names its em"))?;
    let glyphs = word_profiles(&word["profiles"], WORD_SIZE / em)?;
    let letters = glyphs
        .iter()
        .map(|p| Plane::XY.extrude(p, WORD_DEPTH + WORD_RAISE))
        .collect::<Result<Vec<_>>>()?;
    let letters = Solid::compose(&letters)
        .rotate(V3::ZERO, V3::X, 90.0)
        .rotate(V3::ZERO, V3::Z, 180.0);
    let b = letters.bounds();
    let word = letters.translate(v3(
        -(b.min.x + b.max.x) / 2.0,
        THICK - WORD_DEPTH - b.min.y,
        (WORD_BAND_BOTTOM + TOP) / 2.0 - (b.min.z + b.max.z) / 2.0,
    ));
    let plain = blank()?;
    // The trim prints in the flavor chips' black, its word in their white.
    let (chip, ink) = port_colors("flavor")?;
    let body = plain.cut(&word)?;
    let exterior = plain.union(&word)?;
    let bodies = [
        Body {
            name: "data-ring",
            color: Some(chip),
            solid: &body,
        },
        Body {
            name: "data-ring-word",
            color: Some(ink),
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
