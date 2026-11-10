//! Rich paragraphs keep font spans and clickable references while breaking words to a page width.
use crate::{Font, Page, Path, Pen, Rgb, Run, Target};
use std::sync::Arc;

pub struct Fonts {
    pub base: Arc<Font>,
    pub bold: Arc<Font>,
    pub mono: Arc<Font>,
}

#[derive(Clone)]
struct Style {
    font: Arc<Font>,
    color: Rgb,
    underline: bool,
    link: Option<String>,
}
#[derive(Clone)]
struct Fragment {
    text: String,
    style: Style,
}
struct Word {
    fragments: Vec<Fragment>,
    space: Option<Style>,
}
enum Item {
    Word(Word),
    Break,
}

fn attribute(tag: &str, key: &str) -> Option<String> {
    let (_, rest) = tag.split_once(&format!("{key}="))?;
    let quote = rest.chars().next()?;
    if quote == '\'' || quote == '"' {
        Some(decode(rest[1..].split(quote).next()?))
    } else {
        Some(decode(
            rest.split_ascii_whitespace().next()?.trim_end_matches('>'),
        ))
    }
}

fn decode(mut value: &str) -> String {
    let mut out = String::new();
    while let Some(ch) = value.chars().next() {
        if ch == '&' {
            if let Some((decoded, length)) = entity(value) {
                out.push(decoded);
                value = &value[length..];
                continue;
            }
        }
        out.push(ch);
        value = &value[ch.len_utf8()..];
    }
    out
}

fn entity(rest: &str) -> Option<(char, usize)> {
    let end = rest.find(';')?;
    let name = &rest[1..end];
    let value = match name {
        "amp" => '&',
        "lt" => '<',
        "gt" => '>',
        "quot" => '"',
        "apos" => '\'',
        "nbsp" => '\u{a0}',
        "times" => '×',
        "deg" => '°',
        "middot" => '·',
        "plusmn" => '±',
        "sup3" => '³',
        _ if name.starts_with("#x") => char::from_u32(u32::from_str_radix(&name[2..], 16).ok()?)?,
        _ if name.starts_with('#') => char::from_u32(name[1..].parse().ok()?)?,
        _ => return None,
    };
    Some((value, end + 1))
}

fn items(markup: &str, fonts: &Fonts, color: Rgb) -> Vec<Item> {
    let mut style = Style {
        font: fonts.base.clone(),
        color,
        underline: false,
        link: None,
    };
    let mut stack: Vec<(String, Style)> = Vec::new();
    let mut out = Vec::new();
    let mut fragments: Vec<Fragment> = Vec::new();
    let flush = |fragments: &mut Vec<Fragment>, out: &mut Vec<Item>, space: Option<Style>| {
        if !fragments.is_empty() {
            out.push(Item::Word(Word {
                fragments: std::mem::take(fragments),
                space,
            }));
        }
    };
    let mut rest = markup;
    while let Some(mut ch) = rest.chars().next() {
        if ch == '<' {
            if let Some(end) = rest.find('>') {
                let tag = rest[1..end].trim();
                rest = &rest[end + 1..];
                let name = tag
                    .split_ascii_whitespace()
                    .next()
                    .unwrap_or("")
                    .trim_end_matches('/');
                if name == "br" {
                    flush(&mut fragments, &mut out, None);
                    out.push(Item::Break);
                    continue;
                }
                if let Some(close) = name.strip_prefix('/') {
                    if let Some(index) = stack.iter().rposition(|(name, _)| name == close) {
                        style = stack[index].1.clone();
                        stack.truncate(index);
                    }
                } else {
                    stack.push((name.into(), style.clone()));
                    match name {
                        "b" | "strong" => style.font = fonts.bold.clone(),
                        "u" => style.underline = true,
                        "link" | "a" => {
                            style.link = attribute(tag, "href");
                            style.color = attribute(tag, "color")
                                .filter(|v| v.len() == 7 && v.starts_with('#'))
                                .map_or(Rgb::hex("#1749D1"), |v| Rgb::hex(&v));
                        }
                        "font" => {
                            if let Some(name) = attribute(tag, "name") {
                                style.font = if name.contains("Mono") {
                                    fonts.mono.clone()
                                } else if name.contains("Bold") || name.contains("Semi") {
                                    fonts.bold.clone()
                                } else {
                                    fonts.base.clone()
                                };
                            }
                            if let Some(value) = attribute(tag, "color")
                                .filter(|v| v.len() == 7 && v.starts_with('#'))
                            {
                                style.color = Rgb::hex(&value);
                            }
                        }
                        _ => (),
                    }
                }
                continue;
            }
        }
        let advance = if ch == '&' {
            if let Some((decoded, count)) = entity(rest) {
                ch = decoded;
                count
            } else {
                ch.len_utf8()
            }
        } else {
            ch.len_utf8()
        };
        rest = &rest[advance..];
        if ch.is_whitespace() && ch != '\u{a0}' {
            flush(&mut fragments, &mut out, Some(style.clone()));
        } else {
            if let Some(last) = fragments.last_mut().filter(|f| {
                Arc::ptr_eq(&f.style.font, &style.font)
                    && f.style.color == style.color
                    && f.style.link == style.link
                    && f.style.underline == style.underline
            }) {
                last.text.push(ch);
            } else {
                fragments.push(Fragment {
                    text: ch.to_string(),
                    style: style.clone(),
                });
            }
        }
    }
    flush(&mut fragments, &mut out, None);
    out
}

pub struct Line {
    fragments: Vec<Fragment>,
    width: f64,
}
pub struct Paragraph {
    pub lines: Vec<Line>,
    pub size: f64,
    pub leading: f64,
}

impl Paragraph {
    pub fn new(
        markup: &str,
        width: f64,
        fonts: &Fonts,
        size: f64,
        leading: f64,
        color: Rgb,
    ) -> Self {
        let mut lines = Vec::new();
        let mut words: Vec<Word> = Vec::new();
        let (mut used, mut pending, mut spaces) = (0., 0., 0.);
        let close = |words: &mut Vec<Word>, used: f64, lines: &mut Vec<Line>| {
            let count = words.len();
            let mut fragments = Vec::new();
            for (i, word) in words.drain(..).enumerate() {
                fragments.extend(word.fragments);
                if i + 1 < count {
                    if let Some(style) = word.space {
                        fragments.push(Fragment {
                            text: " ".into(),
                            style,
                        });
                    }
                }
            }
            lines.push(Line {
                fragments,
                width: used,
            });
        };
        for item in items(markup, fonts, color) {
            match item {
                Item::Break => {
                    close(&mut words, used, &mut lines);
                    (used, pending, spaces) = (0., 0., 0.);
                }
                Item::Word(word) => {
                    let w = word
                        .fragments
                        .iter()
                        .map(|f| f.style.font.width(&f.text, size))
                        .sum::<f64>();
                    let space = word.space.as_ref().map_or(0., |s| s.font.width(" ", size));
                    if words.is_empty() {
                        (used, pending, spaces) = (w, space, 0.);
                    } else if used + pending + w > width + 0.05 * (pending + spaces) {
                        close(&mut words, used, &mut lines);
                        (used, pending, spaces) = (w, space, 0.);
                    } else {
                        used += pending + w;
                        spaces += pending;
                        pending = space;
                    }
                    words.push(word);
                }
            }
        }
        if !words.is_empty() {
            close(&mut words, used, &mut lines);
        }
        Self {
            lines,
            size,
            leading,
        }
    }
    pub fn height(&self) -> f64 {
        self.lines.len() as f64 * self.leading
    }
    pub fn draw(&self, page: &mut Page, x: f64, top: f64, width: f64, centred: bool) {
        for (i, line) in self.lines.iter().enumerate() {
            let y = top - self.size - i as f64 * self.leading;
            let spaces = line
                .fragments
                .iter()
                .map(|f| f.text.matches(' ').count() + f.text.matches('\u{a0}').count())
                .sum::<usize>();
            let squeeze = width < line.width && spaces > 0;
            let word_space = if squeeze {
                (width - line.width) / spaces as f64
            } else {
                0.
            };
            let mut at = x + if centred && !squeeze {
                (width - line.width) / 2.
            } else {
                0.
            };
            for fragment in &line.fragments {
                let span = fragment.style.font.width(&fragment.text, self.size)
                    + word_space * fragment.text.matches(' ').count() as f64;
                page.text(Run {
                    font: fragment.style.font.clone(),
                    size: self.size,
                    at: [at, y],
                    color: fragment.style.color,
                    char_space: 0.,
                    word_space,
                    text: fragment.text.clone(),
                });
                if fragment.style.underline {
                    page.stroke(
                        Path::polyline(
                            &[
                                [at, y - self.size * 0.12],
                                [at + span, y - self.size * 0.12],
                            ],
                            false,
                        ),
                        Pen::new(fragment.style.color, self.size * 0.05),
                    );
                }
                if let Some(uri) = &fragment.style.link {
                    page.link(
                        [at, y - self.size * 0.2, at + span, y + self.size],
                        Target::Uri(uri.clone()),
                    );
                }
                at += span;
            }
        }
    }
}
