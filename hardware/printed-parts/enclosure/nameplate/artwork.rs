//! The plate's artwork, read from its masters on every run: the wordmark's outlined text from
//! `wordmark.svg`, the unit's identification line set from the frozen letterforms, and the brand
//! mark's faucet and drop from `brand/mark.svg`, each in the plate's X/Z frame.
use anyhow::{Context, Result, anyhow, bail, ensure};
use serde_json::Value;

pub type P2 = [f64; 2];

/// One segment of an outline, by its control points: a line, a quadratic or cubic Bézier, or a
/// semicircle through its middle point.
#[derive(Clone, Debug, PartialEq)]
pub enum Seg {
    Line(P2, P2),
    Quad(P2, P2, P2),
    Cubic(P2, P2, P2, P2),
    Arc(P2, P2, P2),
}

pub type Contour = Vec<Seg>;

/// The masters, compiled in, so the program's build names them among its inputs.
const WORDMARK: &str = include_str!("wordmark.svg");
const MARK: &str = include_str!("../../../../brand/mark.svg");
const GLYPHS: &str = include_str!("identification-glyphs.json");

/// An SVG path's closed contours, as a pen reads them: each point mapped by `point`, a line back
/// to the start closing each contour, and lines of no length left out.
fn contours(d: &str, point: &dyn Fn(P2) -> P2) -> Result<Vec<Contour>> {
    let mut tokens = Tokens::new(d);
    let (mut out, mut segments) = (vec![], vec![]);
    let (mut start, mut last): (P2, P2) = ([0.0; 2], [0.0; 2]);
    let mut command = None;
    let line = |segments: &mut Contour, last: &mut P2, p: P2| {
        if p != *last {
            segments.push(Seg::Line(point(*last), point(p)));
        }
        *last = p;
    };
    while let Some(next) = tokens.command_or_number()? {
        let c = match next {
            Token::Command(c) => c,
            Token::Number => command.context("a path's numbers follow a command")?,
        };
        if let Token::Command(_) = next {
            command = Some(c);
        }
        match c {
            'M' => {
                start = [tokens.number()?, tokens.number()?];
                last = start;
                segments = vec![];
                // Further pairs after a move are lines.
                command = Some('L');
            }
            'L' => {
                let p = [tokens.number()?, tokens.number()?];
                line(&mut segments, &mut last, p);
            }
            'H' => {
                let p = [tokens.number()?, last[1]];
                line(&mut segments, &mut last, p);
            }
            'V' => {
                let p = [last[0], tokens.number()?];
                line(&mut segments, &mut last, p);
            }
            'Q' => {
                let (c1, p) = ([tokens.number()?, tokens.number()?], [tokens.number()?, tokens.number()?]);
                segments.push(Seg::Quad(point(last), point(c1), point(p)));
                last = p;
            }
            'C' => {
                let (c1, c2, p) = (
                    [tokens.number()?, tokens.number()?],
                    [tokens.number()?, tokens.number()?],
                    [tokens.number()?, tokens.number()?],
                );
                segments.push(Seg::Cubic(point(last), point(c1), point(c2), point(p)));
                last = p;
            }
            'A' => {
                let (rx, ry, rotation) = (tokens.number()?, tokens.number()?, tokens.number()?);
                let (_large, sweep) = (tokens.number()?, tokens.number()?);
                let p = [tokens.number()?, tokens.number()?];
                let (dx, dy) = (p[0] - last[0], p[1] - last[1]);
                let close = |a: f64, b: f64| (a - b).abs() <= 1e-9 * a.abs().max(b.abs());
                ensure!(close(rx, ry) && rotation.abs() <= 1e-9 && close(dx.hypot(dy), 2.0 * rx),
                        "the mark's arcs are unrotated semicircles");
                let direction = if sweep != 0.0 { 1.0 } else { -1.0 };
                let middle = [(last[0] + p[0] + direction * dy) / 2.0, (last[1] + p[1] - direction * dx) / 2.0];
                segments.push(Seg::Arc(point(last), point(middle), point(p)));
                last = p;
            }
            'Z' | 'z' => {
                line(&mut segments, &mut last, start);
                out.push(std::mem::take(&mut segments));
                last = start;
                command = None;
            }
            other => bail!("the artwork's paths use no {other:?}"),
        }
    }
    ensure!(segments.is_empty(), "the artwork's contours are closed");
    Ok(out)
}

enum Token {
    Command(char),
    Number,
}

/// A path's commands and numbers.
struct Tokens<'a> {
    rest: &'a str,
}

impl<'a> Tokens<'a> {
    fn new(d: &'a str) -> Self {
        Tokens { rest: d }
    }
    fn skip(&mut self) {
        self.rest = self.rest.trim_start_matches(|c: char| c.is_whitespace() || c == ',');
    }
    fn command_or_number(&mut self) -> Result<Option<Token>> {
        self.skip();
        let Some(c) = self.rest.chars().next() else { return Ok(None) };
        if c.is_ascii_alphabetic() {
            self.rest = &self.rest[1..];
            Ok(Some(Token::Command(c)))
        } else {
            Ok(Some(Token::Number))
        }
    }
    fn number(&mut self) -> Result<f64> {
        self.skip();
        let end = self
            .rest
            .char_indices()
            .find(|&(i, c)| !(c.is_ascii_digit() || c == '.' || ((c == '-' || c == '+') && i == 0) || c == 'e' || c == 'E'))
            .map(|(i, _)| i)
            .unwrap_or(self.rest.len());
        let (text, rest) = self.rest.split_at(end);
        self.rest = rest;
        text.parse().map_err(|_| anyhow!("{text:?} in a path is not a number"))
    }
}

/// An attribute's value on an element's opening tag.
fn attribute<'a>(tag: &'a str, name: &str) -> Option<&'a str> {
    let at = tag.find(&format!(" {name}=\""))? + name.len() + 3;
    tag[at..].find('"').map(|end| &tag[at..at + end])
}

/// The wordmark's groups: each lettered group's paths, offset by the group's translation and
/// carried into the plate's frame.
pub fn wordmark(width: f64, height: f64) -> Result<Vec<Vec<Contour>>> {
    let mut groups = vec![];
    let mut rest = WORDMARK;
    while let Some(open) = rest.find("<g ") {
        let tag_end = rest[open..].find('>').context("an open group tag")? + open;
        let tag = &rest[open..=tag_end];
        let close = rest[tag_end..].find("</g>").context("a closed group")? + tag_end;
        let body = &rest[tag_end + 1..close];
        rest = &rest[close + 4..];
        if attribute(tag, "aria-label").is_none() || attribute(tag, "data-variable").is_some() {
            continue;
        }
        let transform = attribute(tag, "transform").context("a lettered group's translation")?;
        let inner = transform.strip_prefix("translate(").and_then(|t| t.strip_suffix(')')).context("a translation")?;
        let mut parts = inner.split_whitespace().map(str::parse::<f64>);
        let (tx, ty) = (parts.next().context("x")??, parts.next().context("y")??);
        let point = |p: P2| [width / 2.0 - p[0] - tx, height / 2.0 - p[1] - ty];
        let mut loops = vec![];
        let mut paths = body;
        while let Some(at) = paths.find("<path ") {
            let end = paths[at..].find('>').context("a path tag")? + at;
            let d = attribute(&paths[at..=end], "d").context("a path's outline")?;
            loops.extend(contours(d, &point)?);
            paths = &paths[end + 1..];
        }
        groups.push(loops);
    }
    Ok(groups)
}

/// Rounded to the micron's thousandth, as the plate's artwork is written.
fn round6(x: f64) -> f64 {
    format!("{x:.6}").parse().expect("a formatted number parses")
}

/// The unit's identification line, its number of the edition's size, set from the frozen
/// letterforms and centred on the plate at the line's height.
pub fn unit_line(unit: u32) -> Result<Vec<Contour>> {
    let data: Value = serde_json::from_str(GLYPHS)?;
    let total = data["total_units"].as_u64().context("the edition's size")?;
    ensure!((1..=total).contains(&(unit as u64)), "First Edition nameplates are numbered 1 through {total}");
    let number = |v: &Value| v.as_f64().ok_or_else(|| anyhow!("a letterform number"));
    let (tracking, centre_z) = (number(&data["tracking_mm"])?, number(&data["center_z_mm"])?);
    let mut cursor = 0.0;
    let mut loops: Vec<Vec<(String, Vec<P2>)>> = vec![];
    for c in format!("UNIT {unit:02} OF {total}").chars() {
        let glyph = &data["glyphs"][c.to_string()];
        for lp in glyph["loops"].as_array().with_context(|| format!("no letterform for {c:?}"))? {
            let mut segments = vec![];
            for seg in lp.as_array().context("a letterform loop")? {
                let (kind, points) = seg.as_object().and_then(|o| o.iter().next()).context("a letterform segment")?;
                let points = points
                    .as_array()
                    .context("a segment's points")?
                    .iter()
                    .map(|p| Ok([number(&p[0])? + cursor, number(&p[1])?]))
                    .collect::<Result<Vec<_>>>()?;
                segments.push((kind.clone(), points));
            }
            loops.push(segments);
        }
        cursor += number(&glyph["advance_mm"])? + tracking;
    }
    let all: Vec<P2> = loops.iter().flatten().flat_map(|(_, p)| p.iter().copied()).collect();
    let span = |k: usize| {
        let lo = all.iter().map(|p| p[k]).fold(f64::INFINITY, f64::min);
        let hi = all.iter().map(|p| p[k]).fold(f64::NEG_INFINITY, f64::max);
        (lo + hi) / 2.0
    };
    let (cx, cz) = (span(0), span(1));
    let place = |p: &P2| [round6(cx - p[0]), round6(p[1] - cz + centre_z)];
    loops
        .iter()
        .map(|lp| {
            lp.iter()
                .map(|(kind, p)| {
                    let q: Vec<P2> = p.iter().map(place).collect();
                    Ok(match (kind.as_str(), q.as_slice()) {
                        ("line", &[a, b]) => Seg::Line(a, b),
                        ("quad", &[a, c, b]) => Seg::Quad(a, c, b),
                        ("cubic", &[a, c1, c2, b]) => Seg::Cubic(a, c1, c2, b),
                        _ => bail!("invalid letterform {kind} segment"),
                    })
                })
                .collect()
        })
        .collect()
}

/// The brand mark on the plate: the faucet's outline and the drop's centre and radius, scaled to
/// `logo_h` tall, its left edge `left` in from the plate's edge and centred at `centre_z`.
pub struct Logo {
    pub faucet: Contour,
    pub drop_center: P2,
    pub drop_radius: f64,
}

pub fn logo(width: f64, left: f64, logo_h: f64, centre_z: f64) -> Result<Logo> {
    let tag = |id: &str| -> Result<&str> {
        let at = MARK.find(&format!("id=\"{id}\"")).with_context(|| format!("the brand mark has no {id}"))?;
        let open = MARK[..at].rfind('<').context("an element")?;
        let end = MARK[at..].find('>').context("an element's end")? + at;
        Ok(&MARK[open..=end])
    };
    let (faucet, drop) = (tag("faucet")?, tag("drop")?);
    let d = attribute(faucet, "d").context("the faucet's outline")?;
    let value = |name: &str| -> Result<f64> { Ok(attribute(drop, name).with_context(|| format!("the drop's {name}"))?.parse()?) };
    let (cx, cy, radius) = (value("cx")?, value("cy")?, value("r")?);
    let raw = contours(d, &|p| p)?;
    let mut points: Vec<P2> = raw.iter().flatten().flat_map(|s| match s {
        Seg::Line(a, b) => vec![*a, *b],
        Seg::Quad(a, c, b) => vec![*a, *c, *b],
        Seg::Cubic(a, c1, c2, b) => vec![*a, *c1, *c2, *b],
        Seg::Arc(a, m, b) => vec![*a, *m, *b],
    }).collect();
    points.push([cx - radius, cy - radius]);
    points.push([cx + radius, cy + radius]);
    let fold = |k: usize, min: bool| points.iter().map(|p| p[k]).fold(if min { f64::INFINITY } else { f64::NEG_INFINITY }, |a, b| if min { a.min(b) } else { a.max(b) });
    let (low_x, bottom, top) = (fold(0, true), fold(1, true), fold(1, false));
    let scale = logo_h / (top - bottom);
    let place = move |p: P2| [width / 2.0 - left - (p[0] - low_x) * scale, centre_z + ((bottom + top) / 2.0 - p[1]) * scale];
    let mut placed = contours(d, &place)?;
    ensure!(placed.len() == 1, "the faucet is one silhouette");
    Ok(Logo { faucet: placed.remove(0), drop_center: place([cx, cy]), drop_radius: radius * scale })
}
