//! The artwork the raised lettering is set from.
use crate::plan::P2;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::BTreeMap;

#[derive(Clone, Debug, PartialEq)]
pub struct Artwork {
    /// The artwork document, as the evaluator reads its outlines.
    pub source: Value,
}

impl Artwork {
    /// The artwork's glyph outlines.
    pub fn font(&self) -> anyhow::Result<Font> {
        Ok(Font::deserialize(&self.source)?)
    }
}

/// A face's glyph outlines in font units, with the arithmetic that sets them.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Font {
    pub family: String,
    pub kind: String,
    pub units_per_em: f64,
    pub cap_height_at_one: f64,
    pub baseline_units: f64,
    pub glyphs: BTreeMap<char, Glyph>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Glyph {
    pub advance: f64,
    pub profiles: Vec<GlyphProfile>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct GlyphProfile {
    pub outer: Vec<Curve>,
    pub holes: Vec<Vec<Curve>>,
}

/// One outline curve: a line, a quadratic or a cubic, by its control points.
#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
#[serde(try_from = "Vec<Mark>", into = "Vec<Mark>")]
pub enum Curve {
    Line(P2, P2),
    Quad(P2, P2, P2),
    Cubic(P2, P2, P2, P2),
}

/// A curve's letter, then its points, as the artwork writes them.
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(untagged)]
pub enum Mark {
    Letter(String),
    Point(P2),
}

impl TryFrom<Vec<Mark>> for Curve {
    type Error = String;
    fn try_from(marks: Vec<Mark>) -> Result<Self, String> {
        let letter = match marks.first() {
            Some(Mark::Letter(l)) => l.clone(),
            _ => return Err("an outline curve starts with its letter".into()),
        };
        let points: Vec<P2> = marks[1..]
            .iter()
            .map(|m| match m {
                Mark::Point(p) => Ok(*p),
                Mark::Letter(_) => Err("an outline curve's points follow its letter".to_string()),
            })
            .collect::<Result<_, _>>()?;
        match (letter.as_str(), points.as_slice()) {
            ("L", &[a, b]) => Ok(Curve::Line(a, b)),
            ("Q", &[a, c, b]) => Ok(Curve::Quad(a, c, b)),
            ("C", &[a, c1, c2, b]) => Ok(Curve::Cubic(a, c1, c2, b)),
            (other, _) => Err(format!("unsupported outline curve {other} of {} points", points.len())),
        }
    }
}

impl From<Curve> for Vec<Mark> {
    fn from(c: Curve) -> Self {
        let (letter, points) = match c {
            Curve::Line(a, b) => ("L", vec![a, b]),
            Curve::Quad(a, c, b) => ("Q", vec![a, c, b]),
            Curve::Cubic(a, c1, c2, b) => ("C", vec![a, c1, c2, b]),
        };
        std::iter::once(Mark::Letter(letter.into())).chain(points.into_iter().map(Mark::Point)).collect()
    }
}
