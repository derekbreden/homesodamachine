//! The raised disposal warning on the rear face, set in its artwork's glyph outlines.
use crate::plan::{Bounds, Graph, Letters, Op, Shape};
use crate::shell::*;
use serde::Deserialize;
use serde_json::Value;
use hsm_enclosure_solid::text::Artwork;
use std::collections::HashMap;
use std::rc::Rc;
use std::sync::OnceLock;

fn artwork() -> Rc<Artwork> {
    static SOURCE: OnceLock<Value> = OnceLock::new();
    let source = SOURCE.get_or_init(|| {
        let v: Value = serde_json::from_str(include_str!("../disposal-warning-artwork.json"))
            .expect("the disposal warning's artwork parses");
        assert!(
            v["family"] == DISPOSAL_FONT && v["kind"] == "bold",
            "the disposal warning needs artwork for its selected face"
        );
        v
    });
    Rc::new(Artwork { source: source.clone() })
}

/// The warning's raised letters on the rear face, embedded a little into the wall.
pub fn disposal_letters(g: &mut Graph, outer: &Bounds) -> Shape {
    let letters = Letters {
        outer: *outer,
        lines: DISPOSAL_LINES.iter().map(|s| s.to_string()).collect(),
        family: DISPOSAL_FONT.to_string(),
        artwork: artwork(),
        cap_height: DISPOSAL_CAP_HEIGHT,
        depth: DISPOSAL_RAISE + DISPOSAL_EMBED,
        embed: DISPOSAL_EMBED,
        line_gap: DISPOSAL_LINE_GAP,
        bottom: DISPOSAL_BOTTOM,
    };
    g.add(Op::DisposalLetters(Rc::new(letters)), vec![], None)
}

/// The artwork's metrics: each glyph's advance and ink bounds, in font units, and the scale and
/// baseline its outlines are set at.
#[derive(Deserialize)]
struct Metrics {
    baseline_units: f64,
    cap_height_at_one: f64,
    units_per_em: f64,
    glyphs: HashMap<String, Glyph>,
}

#[derive(Deserialize)]
struct Glyph {
    advance: f64,
    bounds: Option<[f64; 4]>,
}

fn metrics() -> &'static Metrics {
    static METRICS: OnceLock<Metrics> = OnceLock::new();
    METRICS.get_or_init(|| {
        serde_json::from_str(include_str!("../disposal-warning-artwork.json"))
            .expect("the disposal warning's artwork parses")
    })
}

/// The flat wall under the warning, a quiet margin round its letters on all four sides, from
/// the wall's inner face out to the letters' face.
pub fn disposal_field(outer: &Bounds) -> Bounds {
    let art = metrics();
    let scale = (DISPOSAL_CAP_HEIGHT / art.cap_height_at_one) / art.units_per_em;
    let base = art.baseline_units * scale;
    let glyph = |c: char| art.glyphs.get(c.to_string().as_str()).expect("the artwork sets every character");
    let rows: Vec<(f64, f64)> = DISPOSAL_LINES
        .iter()
        .map(|line| {
            let advance: f64 = line.chars().map(|c| glyph(c).advance).sum();
            let mut pen = 0.0;
            let mut ink = [f64::INFINITY, f64::NEG_INFINITY, f64::INFINITY, f64::NEG_INFINITY];
            for c in line.chars() {
                let g = glyph(c);
                if let Some([x0, x1, y0, y1]) = g.bounds {
                    let at = (-advance / 2.0 + pen) * scale;
                    ink = [ink[0].min(at + x0 * scale), ink[1].max(at + x1 * scale),
                           ink[2].min(base + y0 * scale), ink[3].max(base + y1 * scale)];
                }
                pen += g.advance;
            }
            (ink[1] - ink[0], ink[3] - ink[2])
        })
        .collect();
    let row_height = rows.iter().map(|r| r.1).fold(f64::NEG_INFINITY, f64::max);
    let width = rows.iter().map(|r| r.0).fold(f64::NEG_INFINITY, f64::max);
    let leading = row_height + DISPOSAL_LINE_GAP;
    let depth = DISPOSAL_RAISE + DISPOSAL_EMBED;
    let (z0, z1) = rows.iter().rev().enumerate().fold((f64::INFINITY, f64::NEG_INFINITY), |(lo, hi), (i, &(_, h))| {
        let a = i as f64 * leading + (row_height - h) / 2.0;
        (lo.min(a), hi.max(a + h + depth))
    });
    let centre = (outer[0] + outer[1]) / 2.0;
    let bottom = outer[4] + DISPOSAL_BOTTOM;
    [centre - width / 2.0 - DISPOSAL_MARGIN, centre + width / 2.0 + DISPOSAL_MARGIN, outer[3] - WALL,
     outer[3] + DISPOSAL_RAISE, bottom + z0 - DISPOSAL_MARGIN, bottom + z1 + DISPOSAL_MARGIN]
}
