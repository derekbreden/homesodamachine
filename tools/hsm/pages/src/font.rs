//! A TrueType font as text is measured and set in it: each character's glyph and advance, and
//! the glyph outlines pixels are drawn from. The whole font file is embedded where it is used.
use anyhow::{Context, Result};
use std::collections::HashMap;

pub struct Font {
    /// The font's name in a PDF.
    pub name: String,
    pub data: Vec<u8>,
    units_per_em: f64,
    glyphs: HashMap<char, u16>,
    /// Advance widths in thousandths of an em, by glyph.
    advances: Vec<f64>,
    /// Ascent, descent and capital height, in thousandths of an em.
    pub ascent: f64,
    pub descent: f64,
    pub cap_height: f64,
    /// The bounding box of every glyph, in thousandths of an em.
    pub bbox: [f64; 4],
    pub italic_angle: f64,
}

impl Font {
    pub fn new(name: &str, data: Vec<u8>) -> Result<Font> {
        let face = ttf_parser::Face::parse(&data, 0).with_context(|| format!("{name}: a TrueType font"))?;
        let units_per_em = face.units_per_em() as f64;
        let k = 1000.0 / units_per_em;
        let advances = (0..face.number_of_glyphs())
            .map(|g| face.glyph_hor_advance(ttf_parser::GlyphId(g)).unwrap_or(0) as f64 * k)
            .collect();
        let mut glyphs = HashMap::new();
        if let Some(cmap) = face.tables().cmap {
            for table in cmap.subtables.into_iter().filter(|t| t.is_unicode()) {
                table.codepoints(|code| {
                    if let (Some(c), Some(g)) = (char::from_u32(code), table.glyph_index(code)) {
                        glyphs.entry(c).or_insert(g.0);
                    }
                });
            }
        }
        // A no-break space is set as a space and keeps words together.
        if let Some(&space) = glyphs.get(&' ') {
            glyphs.insert('\u{a0}', space);
        }
        let b = face.global_bounding_box();
        Ok(Font {
            name: name.to_owned(),
            units_per_em,
            glyphs,
            advances,
            ascent: face.typographic_ascender().unwrap_or(face.ascender()) as f64 * k,
            descent: face.typographic_descender().unwrap_or(face.descender()) as f64 * k,
            cap_height: face.capital_height().unwrap_or(face.ascender()) as f64 * k,
            bbox: [b.x_min, b.y_min, b.x_max, b.y_max].map(|v| v as f64 * k),
            italic_angle: face.italic_angle() as f64,
            data,
        })
    }

    /// The glyph a character is set in; glyph 0 when the font has none.
    pub fn glyph(&self, c: char) -> u16 {
        self.glyphs.get(&c).copied().unwrap_or(0)
    }

    /// A glyph's advance, in thousandths of an em.
    pub fn advance(&self, glyph: u16) -> f64 {
        self.advances.get(glyph as usize).copied().unwrap_or(0.0)
    }

    pub fn glyph_count(&self) -> usize {
        self.advances.len()
    }

    /// The width of `text` set at `size` points, with no kerning.
    pub fn width(&self, text: &str, size: f64) -> f64 {
        0.001 * size * text.chars().map(|c| self.advance(self.glyph(c))).sum::<f64>()
    }

    /// A glyph's outline in em units scaled to `size`, with its origin at `origin` and y up.
    pub fn outline(&self, glyph: u16, size: f64, origin: [f64; 2], to: &mut tiny_skia::PathBuilder) {
        let face = ttf_parser::Face::parse(&self.data, 0).expect("parsed when the font was read");
        let s = size / self.units_per_em;
        let mut sink = Outline { to, s, origin };
        face.outline_glyph(ttf_parser::GlyphId(glyph), &mut sink);
    }
}

struct Outline<'a> {
    to: &'a mut tiny_skia::PathBuilder,
    s: f64,
    origin: [f64; 2],
}

impl Outline<'_> {
    fn at(&self, x: f32, y: f32) -> (f32, f32) {
        ((self.origin[0] + x as f64 * self.s) as f32, (self.origin[1] + y as f64 * self.s) as f32)
    }
}

impl ttf_parser::OutlineBuilder for Outline<'_> {
    fn move_to(&mut self, x: f32, y: f32) {
        let (x, y) = self.at(x, y);
        self.to.move_to(x, y);
    }
    fn line_to(&mut self, x: f32, y: f32) {
        let (x, y) = self.at(x, y);
        self.to.line_to(x, y);
    }
    fn quad_to(&mut self, x1: f32, y1: f32, x: f32, y: f32) {
        let (x1, y1) = self.at(x1, y1);
        let (x, y) = self.at(x, y);
        self.to.quad_to(x1, y1, x, y);
    }
    fn curve_to(&mut self, x1: f32, y1: f32, x2: f32, y2: f32, x: f32, y: f32) {
        let (x1, y1) = self.at(x1, y1);
        let (x2, y2) = self.at(x2, y2);
        let (x, y) = self.at(x, y);
        self.to.cubic_to(x1, y1, x2, y2, x, y);
    }
    fn close(&mut self) {
        self.to.close();
    }
}
