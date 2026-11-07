//! The six tube collars: each the flat-topped stock round its bore, its station's word recessed in
//! three faces, and the word as a body of its own in the second filament; the STL is the collar's
//! blank, its bore through and no word cut.
//!
//!     tube-collar [<output directory>]
use anyhow::{Context, Result, anyhow};
use hsm_kernel::part::write_shown;
use hsm_kernel::*;
use hsm_print_payload::printed;
use hsm_tube_collar_numbers as collar;
use serde_json::Value;

/// The word outlines in the artwork, each `{"outer": [segments], "holes": [[segments]]}` with a
/// segment `{"line"|"quad"|"cubic": [[x, y], ...]}`, scaled into millimetres.
fn profiles(value: &Value, scale: f64) -> Result<Vec<Profile>> {
    let point = |v: &Value| -> Result<V2> {
        Ok(v2(v[0].as_f64().context("a word point's x")?, v[1].as_f64().context("a word point's y")?) * scale)
    };
    let outline = |value: &Value| -> Result<Loop> {
        let segs = value.as_array().context("a word outline")?.iter().map(|seg| {
            let (kind, values) = seg.as_object().and_then(|o| o.iter().next()).context("a word segment")?;
            let p = values.as_array().context("a word segment's points")?.iter().map(point).collect::<Result<Vec<_>>>()?;
            Ok(match (kind.as_str(), p.as_slice()) {
                ("line", &[a, b]) => Seg::Line { a, b },
                ("quad", &[a, c, b]) => Seg::Quad { a, c, b },
                ("cubic", &[a, c1, c2, b]) => Seg::Cubic { a, c1, c2, b },
                _ => return Err(anyhow!("a word's {kind} segment of {} points", p.len())),
            })
        });
        Loop::new(segs.collect::<Result<_>>()?)
    };
    value
        .as_array()
        .context("a word's profiles")?
        .iter()
        .map(|p| {
            let holes = p["holes"].as_array().context("a word profile's holes")?.iter().map(&outline);
            Ok(Profile { outer: outline(&p["outer"])?, holes: holes.collect::<Result<_>>()? })
        })
        .collect()
}

/// A colour of the machine's chip table, rgb8, as the files carry it.
fn chip(rgb: &Value) -> Result<[f64; 3]> {
    hsm_shared_data::color::rgb8_linear(rgb, true)
}

fn main() -> Result<()> {
    let out = printed::out_dir("hardware/printed-parts/faucet/tube-collar")?;
    let bytes = std::fs::read(collar::ARTWORK).with_context(|| format!("reading {}", collar::ARTWORK))?;
    hsm_kernel::reads::read(std::path::Path::new(collar::ARTWORK), &bytes);
    let artwork: Value = serde_json::from_slice(&bytes)?;
    let scale = collar::WORD_SIZE / artwork["em_mm"].as_f64().context("the artwork's em")?;
    let chips = hsm_shared_data::color::chips()?;

    let (r, rise, length, depth) = (collar::OD / 2.0, collar::RISE, collar::LENGTH, collar::WORD_DEPTH);
    let outline = Profile::new(
        Pen::new(v2(-r, 0.0)).line_to(v2(-r, rise)).line_to(v2(r, rise)).line_to(v2(r, 0.0)).arc_through(v2(0.0, -r), v2(-r, 0.0))?.close()?,
    );
    let stock = Plane::new(v3(0.0, length, 0.0), V3::X, -V3::Y)?.extrude(&outline, length)?;
    for (station, _, _) in collar::COLLARS {
        let name = format!("tube-collar-{station}");
        let (word, fluid) = collar::word_and_fluid(station);
        let blank = stock.cut(&Solid::cylinder(V3::ZERO, V3::Y, collar::bore(station) / 2.0, length)?)?;
        let flat = Solid::compose(
            &profiles(&artwork["words"][word], scale)?.iter().map(|p| Plane::XY.extrude(p, depth)).collect::<Result<Vec<_>>>()?,
        );
        let mut letters = vec![];
        for face in [0, 1, -1] {
            let turned = if face == 0 {
                flat.rotate(V3::ZERO, V3::Z, 90.0)
            } else {
                let side = flat.rotate(V3::ZERO, V3::X, 90.0).rotate(V3::ZERO, V3::Z, 90.0);
                if face < 0 { side.rotate(V3::ZERO, V3::Z, 180.0) } else { side }
            };
            let b = turned.bounds();
            let shift = if face == 0 {
                v3(-(b.min.x + b.max.x) / 2.0, length / 2.0 - (b.min.y + b.max.y) / 2.0, rise - depth - b.min.z)
            } else {
                v3(
                    if face > 0 { r - b.max.x } else { -r - b.min.x },
                    length / 2.0 - (b.min.y + b.max.y) / 2.0,
                    rise / 2.0 - (b.min.z + b.max.z) / 2.0,
                )
            };
            letters.push(turned.translate(shift));
        }
        let word_body = Solid::compose(&letters);
        let body = blank.cut(&word_body)?;
        let word_name = format!("{name}-word");
        let color = chip(&chips["chip_filaments"][fluid][1])?;
        let word_color = chip(&chips["chip_word_colors"][fluid])?;
        let mut said = write_shown(
            &out,
            &name,
            &[Body { name: &name, color: Some(color), solid: &body }, Body { name: &word_name, color: Some(word_color), solid: &word_body }],
        )?;
        let stl = format!("{name}.stl");
        write_stl(out.join(&stl), &[&blank])?;
        said["files"].as_array_mut().context("the files written")?.push(Value::String(stl));
        println!("{said}");
    }
    Ok(())
}
