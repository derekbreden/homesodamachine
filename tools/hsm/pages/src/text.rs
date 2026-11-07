//! Paragraphs: words in a base face and its bold, broken into lines the way ReportLab's Paragraph
//! breaks them, so a page keeps the line breaks it was laid out with. A word goes on the line
//! while the line, spaces included, fits the width plus a twentieth of its spaces; `<b>` sets
//! words bold, `<br/>` ends a line and `&nbsp;` holds two words together. A space is as wide as
//! the face it is set in, so the space after a bold phrase is a regular one.
use crate::font::Font;
use crate::page::{Page, Run};
use crate::Rgb;
use std::sync::Arc;

/// The characters a line may break at: every whitespace character but the no-break space.
fn breaks(c: char) -> bool {
    c.is_whitespace() && c != '\u{a0}'
}

#[derive(Clone, Copy, PartialEq)]
enum Face {
    Base,
    Bold,
}

enum Item {
    /// A word, and the face of the space after it when one follows.
    Word { frags: Vec<(Face, String)>, space: Option<Face> },
    Break,
}

/// The words and breaks of `markup`.
fn items(markup: &str) -> Vec<Item> {
    let mut out = Vec::new();
    let mut frags: Vec<(Face, String)> = Vec::new();
    let mut face = Face::Base;
    let finish = |frags: &mut Vec<(Face, String)>, out: &mut Vec<Item>, space: Option<Face>| {
        if !frags.is_empty() {
            out.push(Item::Word { frags: std::mem::take(frags), space });
        }
    };
    let mut rest = markup;
    while let Some(c) = rest.chars().next() {
        let tag = ["<b>", "</b>", "<br/>", "&nbsp;", "&amp;", "&lt;", "&gt;"].into_iter().find(|t| rest.starts_with(t));
        let ch = match tag {
            Some("<b>") => {
                face = Face::Bold;
                None
            }
            Some("</b>") => {
                face = Face::Base;
                None
            }
            Some("<br/>") => {
                finish(&mut frags, &mut out, None);
                out.push(Item::Break);
                None
            }
            Some("&nbsp;") => Some('\u{a0}'),
            Some("&amp;") => Some('&'),
            Some("&lt;") => Some('<'),
            Some("&gt;") => Some('>'),
            _ => Some(c),
        };
        rest = &rest[tag.map_or(c.len_utf8(), str::len)..];
        let Some(ch) = ch else { continue };
        if breaks(ch) {
            finish(&mut frags, &mut out, Some(face));
        } else {
            match frags.last_mut() {
                Some((f, text)) if *f == face => text.push(ch),
                _ => frags.push((face, ch.to_string())),
            }
        }
    }
    finish(&mut frags, &mut out, None);
    out
}

/// One line: its runs of text, spaces included, and its width.
pub struct Line {
    pub runs: Vec<(Arc<Font>, String)>,
    pub width: f64,
}

pub struct Paragraph {
    pub lines: Vec<Line>,
    pub size: f64,
    pub leading: f64,
}

impl Paragraph {
    /// `markup` set in `base` and `bold` at `size`, broken to `width`.
    pub fn new(markup: &str, width: f64, base: &Arc<Font>, bold: &Arc<Font>, size: f64, leading: f64) -> Paragraph {
        let font = |f: Face| if f == Face::Base { base } else { bold };
        let mut lines = Vec::new();
        // The line being filled: its words, width without the space after the last word, that
        // space, and the spaces between its words.
        let mut words: Vec<(Vec<(Face, String)>, Option<Face>)> = Vec::new();
        let (mut used, mut pending, mut spaces) = (0.0, 0.0, 0.0);
        let close = |words: &mut Vec<(Vec<(Face, String)>, Option<Face>)>, used: f64, lines: &mut Vec<Line>| {
            let mut runs: Vec<(Arc<Font>, String)> = Vec::new();
            let count = words.len();
            for (i, (mut frags, space)) in words.drain(..).enumerate() {
                if let (Some(face), true) = (space, i + 1 < count) {
                    frags.push((face, " ".into()));
                }
                for (face, text) in frags {
                    let f = font(face);
                    match runs.last_mut() {
                        Some((g, t)) if Arc::ptr_eq(g, f) => t.push_str(&text),
                        _ => runs.push((f.clone(), text)),
                    }
                }
            }
            lines.push(Line { runs, width: used });
        };
        for item in items(markup) {
            match item {
                Item::Break => {
                    close(&mut words, used, &mut lines);
                    (used, pending, spaces) = (0.0, 0.0, 0.0);
                }
                Item::Word { frags, space: face } => {
                    let w: f64 = frags.iter().map(|(f, t)| font(*f).width(t, size)).sum();
                    let space = face.map_or(0.0, |f| font(f).width(" ", size));
                    if words.is_empty() {
                        (used, pending, spaces) = (w, space, 0.0);
                    } else if used + pending + w > width + 0.05 * (pending + spaces) {
                        close(&mut words, used, &mut lines);
                        (used, pending, spaces) = (w, space, 0.0);
                    } else {
                        used += pending + w;
                        spaces += pending;
                        pending = space;
                    }
                    words.push((frags, face));
                }
            }
        }
        if !words.is_empty() {
            close(&mut words, used, &mut lines);
        }
        Paragraph { lines, size, leading }
    }

    pub fn height(&self) -> f64 {
        self.lines.len() as f64 * self.leading
    }

    /// Set the lines from `top`, the paragraph's upper edge, each at `x` or centred in `width`.
    /// A line wider than `width` starts at `x` with its spaces closed up to fit, shared among
    /// its spaces and no-break spaces, though a no-break space keeps its width.
    pub fn draw(&self, page: &mut Page, x: f64, top: f64, width: f64, color: Rgb, centred: bool) {
        for (i, line) in self.lines.iter().enumerate() {
            let y = top - self.size - i as f64 * self.leading;
            let extra = width - line.width;
            let count = |c: char| line.runs.iter().map(|(_, t)| t.matches(c).count()).sum::<usize>();
            let spaces = count(' ') + count('\u{a0}');
            let squeeze = extra < -1e-8 && spaces > 0;
            let word_space = if squeeze { extra / spaces as f64 } else { 0.0 };
            let mut at = x + if centred && !squeeze { extra / 2.0 } else { 0.0 };
            for (font, text) in &line.runs {
                let run = Run { font: font.clone(), size: self.size, at: [at, y], color, char_space: 0.0, word_space, text: text.clone() };
                page.text(run);
                at += font.width(text, self.size) + word_space * text.matches(' ').count() as f64;
            }
        }
    }
}
