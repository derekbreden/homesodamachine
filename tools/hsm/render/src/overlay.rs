//! A look's annotations drawn over its frame, element for element as an SVG of them would draw:
//! inks, plates and strokes, in Menlo at 12 px.

use crate::annotate::{Annotations, Line, label_ink};
use crate::image::Image;
use crate::plan::hex_css;
use ab_glyph::{Font, FontVec, PxScale, ScaleFont, point};
use anyhow::{Result, anyhow};
use std::sync::OnceLock;
use tiny_skia::{FillRule, IntSize, Paint, Path, PathBuilder, Pixmap, Rect, Stroke, StrokeDash, Transform};

/// The regular and bold faces, each a file and its index in it. Menlo.ttc holds Regular, Bold,
/// Italic and Bold Italic, in that order. Off a Mac it is DejaVu Sans Mono, which Menlo is drawn
/// from: the same em, ascent, descent and advance, so every plate is the size it is on a Mac.
/// The CI image installs it with `fonts-dejavu-core`.
#[cfg(target_os = "macos")]
const FACES: [(&str, u32); 2] = [("/System/Library/Fonts/Menlo.ttc", 0), ("/System/Library/Fonts/Menlo.ttc", 1)];
#[cfg(not(target_os = "macos"))]
const FACES: [(&str, u32); 2] = [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 0),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 0),
];
const FONT_PX: f32 = 12.0;
/// The advance of one 12 px monospace character, which every plate is sized by.
const CH: f64 = 7.22;

struct Fonts {
    regular: FontVec,
    bold: FontVec,
}

fn fonts() -> Result<&'static Fonts> {
    static FONTS: OnceLock<Result<Fonts, String>> = OnceLock::new();
    FONTS
        .get_or_init(|| {
            let face = |(path, i): (&str, u32)| {
                let data = std::fs::read(path).map_err(|e| format!("{path}: {e}"))?;
                FontVec::try_from_vec_and_index(data, i).map_err(|e| format!("{path} face {i}: {e}"))
            };
            Ok(Fonts {
                regular: face(FACES[0])?,
                bold: face(FACES[1])?,
            })
        })
        .as_ref()
        .map_err(|e| anyhow!("the annotations' font: {e}"))
}

#[derive(Clone, Copy)]
enum Anchor {
    Start,
    Middle,
    End,
}

fn rgb(css: &str) -> [u8; 3] {
    let v = u32::from_str_radix(css.trim_start_matches('#'), 16).unwrap_or(0xffffff);
    [(v >> 16) as u8, (v >> 8) as u8, v as u8]
}

fn paint(css: &str, alpha: f64) -> Paint<'static> {
    let [r, g, b] = rgb(css);
    let mut p = Paint::default();
    p.set_color_rgba8(r, g, b, (alpha.clamp(0.0, 1.0) * 255.0).round() as u8);
    p.anti_alias = true;
    p
}

fn round_rect(x: f64, y: f64, w: f64, h: f64, r: f64) -> Option<Path> {
    let (x, y, w, h) = (x as f32, y as f32, w as f32, h as f32);
    let r = (r as f32).min(w / 2.0).min(h / 2.0).max(0.0);
    if r == 0.0 {
        return Some(PathBuilder::from_rect(Rect::from_xywh(x, y, w, h)?));
    }
    let k = 0.552_284_8 * r;
    let mut pb = PathBuilder::new();
    pb.move_to(x + r, y);
    pb.line_to(x + w - r, y);
    pb.cubic_to(x + w - r + k, y, x + w, y + r - k, x + w, y + r);
    pb.line_to(x + w, y + h - r);
    pb.cubic_to(x + w, y + h - r + k, x + w - r + k, y + h, x + w - r, y + h);
    pb.line_to(x + r, y + h);
    pb.cubic_to(x + r - k, y + h, x, y + h - r + k, x, y + h - r);
    pb.line_to(x, y + r);
    pb.cubic_to(x, y + r - k, x + r - k, y, x + r, y);
    pb.close();
    pb.finish()
}

struct Canvas<'a> {
    pixmap: Pixmap,
    fonts: &'a Fonts,
}

impl Canvas<'_> {
    fn stroke(&mut self, path: Option<Path>, css: &str, width: f64, alpha: f64, dash: Option<[f32; 2]>) {
        let Some(path) = path else { return };
        let stroke = Stroke {
            width: width as f32,
            dash: dash.and_then(|d| StrokeDash::new(d.to_vec(), 0.0)),
            ..Default::default()
        };
        self.pixmap.stroke_path(&path, &paint(css, alpha), &stroke, Transform::identity(), None);
    }

    fn fill(&mut self, path: Option<Path>, css: &str, alpha: f64) {
        let Some(path) = path else { return };
        self.pixmap.fill_path(&path, &paint(css, alpha), FillRule::Winding, Transform::identity(), None);
    }

    fn line(&mut self, (x1, y1): (f64, f64), (x2, y2): (f64, f64), css: &str, width: f64, alpha: f64, dash: Option<[f32; 2]>) {
        let mut pb = PathBuilder::new();
        pb.move_to(x1 as f32, y1 as f32);
        pb.line_to(x2 as f32, y2 as f32);
        self.stroke(pb.finish(), css, width, alpha, dash);
    }

    fn segment(&mut self, l: &Line, css: &str, width: f64, alpha: f64, dash: Option<[f32; 2]>) {
        self.line(l.a, l.b, css, width, alpha, dash);
    }

    fn circle(&mut self, x: f64, y: f64, r: f64) -> Option<Path> {
        PathBuilder::from_circle(x as f32, y as f32, r as f32)
    }

    /// A plate: a filled rounded rectangle, and its border when it has one.
    fn plate(&mut self, x: f64, y: f64, w: f64, h: f64, r: f64, fill: (&str, f64), border: Option<(&str, f64)>) {
        self.fill(round_rect(x, y, w, h, r), fill.0, fill.1);
        if let Some((css, width)) = border {
            self.stroke(round_rect(x, y, w, h, r), css, width, 1.0, None);
        }
    }

    /// SVG `<text>`: `y` is the baseline.
    fn text(&mut self, x: f64, y: f64, s: &str, css: &str, bold: bool, anchor: Anchor) {
        // An SVG <text>'s own spacing: ends trimmed, each run of spaces drawn as one.
        let s = &s.split_whitespace().collect::<Vec<_>>().join(" ");
        let fonts: &Fonts = self.fonts;
        let font = if bold { &fonts.bold } else { &fonts.regular };
        let scale = PxScale::from(FONT_PX * font.height_unscaled() / font.units_per_em().unwrap_or(2048.0));
        let scaled = font.as_scaled(scale);
        let width: f32 = s.chars().map(|c| scaled.h_advance(scaled.glyph_id(c))).sum();
        let mut pen = x as f32
            - match anchor {
                Anchor::Start => 0.0,
                Anchor::Middle => width / 2.0,
                Anchor::End => width,
            };
        let [r, g, b] = rgb(css);
        let (w, h) = (self.pixmap.width() as i32, self.pixmap.height() as i32);
        let data = self.pixmap.data_mut();
        for c in s.chars() {
            let id = scaled.glyph_id(c);
            let glyph = id.with_scale_and_position(scale, point(pen, y as f32));
            pen += scaled.h_advance(id);
            let Some(outlined) = font.outline_glyph(glyph) else { continue };
            let bounds = outlined.px_bounds();
            outlined.draw(|gx, gy, coverage| {
                let px = bounds.min.x as i32 + gx as i32;
                let py = bounds.min.y as i32 + gy as i32;
                if px < 0 || py < 0 || px >= w || py >= h {
                    return;
                }
                let a = coverage.clamp(0.0, 1.0);
                let at = ((py * w + px) * 4) as usize;
                for (k, src) in [r, g, b, 255].into_iter().enumerate() {
                    let d = data[at + k] as f32;
                    data[at + k] = (src as f32 * a + d * (1.0 - a)).round() as u8;
                }
            });
        }
    }
}

fn width_of(s: &str) -> f64 {
    s.chars().count() as f64 * CH
}

pub fn draw(image: &mut Image, a: &Annotations) -> Result<()> {
    let fonts = fonts()?;
    let size = IntSize::from_wh(image.width, image.height).ok_or_else(|| anyhow!("an empty frame"))?;
    // tiny-skia works in premultiplied light.
    let premul: Vec<u8> = image
        .rgba
        .chunks_exact(4)
        .flat_map(|p| {
            let al = p[3] as u32;
            [p[0], p[1], p[2]].map(|c| ((c as u32 * al + 127) / 255) as u8).into_iter().chain([p[3]])
        })
        .collect();
    let pixmap = Pixmap::from_vec(premul, size).ok_or_else(|| anyhow!("a frame tiny-skia cannot hold"))?;
    let mut cv = Canvas { pixmap, fonts };
    let (w, h) = (a.width, a.height);

    for g in &a.grid_lines {
        let (ink, width) = if g.zero { ("#5a7099", 1.5) } else { ("#38436b", 1.0) };
        cv.segment(&g.line, ink, width, 0.85, None);
    }
    for t in &a.ticks {
        let tw = width_of(&t.text) + 6.0;
        cv.plate(t.x - tw / 2.0, t.y - 11.0, tw, 15.0, 2.0, ("#1a1a2e", 0.8), None);
        cv.text(t.x, t.y, &t.text, "#8b9dc0", false, Anchor::Middle);
    }

    for l in &a.labels {
        let swatch = if l.tint.is_some() { 12.0 } else { 0.0 };
        let ink = label_ink(l.tint);
        if l.on_screen {
            let jx = if l.left { 22.0 } else { w - 22.0 };
            cv.line(l.anchor, (jx, l.y - 4.0), &ink, 1.0, 0.85, Some([3.0, 3.0]));
            let dot = cv.circle(l.anchor.0, l.anchor.1, 3.2);
            cv.fill(dot.clone(), &ink, 1.0);
            cv.stroke(dot, "#0c0e1c", 0.8, 1.0, None);
        }
        let pw = width_of(&l.name) + 10.0 + swatch;
        let rx = if l.left { 11.0 } else { w - 11.0 - pw };
        cv.plate(rx, l.y - 12.0, pw, 17.0, 3.0, ("#0c0e1c", 0.9), Some(("#3d4a75", 1.0)));
        if let Some(t) = l.tint {
            let sx = if l.left { rx + 5.0 } else { rx + pw - 12.0 };
            cv.plate(sx, l.y - 9.0, 7.0, 11.0, 1.5, (&hex_css(t), 1.0), None);
        }
        let (tx, anchor) = if l.left { (rx + 5.0 + swatch, Anchor::Start) } else { (rx + pw - 5.0 - swatch, Anchor::End) };
        cv.text(tx, l.y, &l.name, "#eaf0fa", true, anchor);
    }

    for d in &a.dims {
        let ((x1, y1), (x2, y2)) = (d.line.a, d.line.b);
        let (mx, my) = ((x1 + x2) / 2.0, (y1 + y2) / 2.0);
        let len = (x2 - x1).hypot(y2 - y1);
        let len = if len == 0.0 { 1.0 } else { len };
        let (px, py) = (-(y2 - y1) / len * 9.0, (x2 - x1) / len * 9.0);
        let ink = "#ffd479";
        cv.segment(&d.line, ink, 1.6, 1.0, None);
        cv.line((x1 - px, y1 - py), (x1 + px, y1 + py), ink, 1.6, 1.0, None);
        cv.line((x2 - px, y2 - py), (x2 + px, y2 + py), ink, 1.6, 1.0, None);
        for f in &d.faces {
            cv.segment(f, ink, 1.0, 0.5, Some([7.0, 5.0]));
        }
        let tw = width_of(&d.text) + 8.0;
        cv.plate(mx + 12.0, my - 9.0, tw, 16.0, 3.0, ("#1a1a2e", 0.92), Some((ink, 1.0)));
        cv.text(mx + 16.0, my + 3.0, &d.text, ink, true, Anchor::Start);
    }

    for c in &a.casts {
        let ((x1, y1), (x2, y2)) = (c.line.a, c.line.b);
        let len = (x2 - x1).hypot(y2 - y1);
        let len = if len == 0.0 { 1.0 } else { len };
        let (px, py) = (-(y2 - y1) / len * 8.0, (x2 - x1) / len * 8.0);
        let ink = if c.hit { "#6fd6a6" } else { "#ff8fa3" };
        cv.segment(&c.line, ink, 1.8, 1.0, None);
        let start = cv.circle(x1, y1, 3.4);
        cv.stroke(start, ink, 1.6, 1.0, None);
        cv.line((x2 - px, y2 - py), (x2 + px, y2 + py), ink, 1.8, 1.0, None);
        let tw = width_of(&c.text) + 8.0;
        let (mx, my) = ((x1 + x2) / 2.0, (y1 + y2) / 2.0);
        cv.plate(mx - tw / 2.0, my + 8.0, tw, 16.0, 3.0, ("#1a1a2e", 0.94), Some((ink, 1.0)));
        cv.text(mx - tw / 2.0 + 4.0, my + 20.0, &c.text, ink, true, Anchor::Start);
    }

    for k in &a.picks {
        let ink = if k.name.is_some() { "#ffa733" } else { "#ff8fa3" };
        let txt = k.name.as_deref().unwrap_or("nothing here");
        let tw = width_of(txt) + 10.0;
        let lx = (k.x + 14.0).max(6.0).min(w - tw - 6.0);
        let ly = (k.y - 16.0).max(6.0).min(h - 26.0);
        let ring = cv.circle(k.x, k.y, 9.0);
        cv.stroke(ring, ink, 1.8, 1.0, None);
        for (a0, a1) in [
            ((k.x - 16.0, k.y), (k.x - 4.0, k.y)),
            ((k.x + 4.0, k.y), (k.x + 16.0, k.y)),
            ((k.x, k.y - 16.0), (k.x, k.y - 4.0)),
            ((k.x, k.y + 4.0), (k.x, k.y + 16.0)),
        ] {
            cv.line(a0, a1, ink, 1.8, 1.0, None);
        }
        cv.plate(lx, ly, tw, 19.0, 3.0, ("#1a1a2e", 0.94), Some((ink, 1.2)));
        cv.text(lx + 5.0, ly + 14.0, txt, ink, true, Anchor::Start);
    }

    let s = &a.scale;
    let ink = "#eaf0fa";
    cv.line((s.x, s.y), (s.x + s.px, s.y), ink, 2.0, 1.0, None);
    cv.line((s.x, s.y - 5.0), (s.x, s.y + 5.0), ink, 2.0, 1.0, None);
    cv.line((s.x + s.px, s.y - 5.0), (s.x + s.px, s.y + 5.0), ink, 2.0, 1.0, None);
    cv.text(s.x + s.px / 2.0, s.y - 9.0, &format!("{} mm", crate::annotate::js(s.mm)), ink, true, Anchor::Middle);

    const LH: f64 = 17.0;
    let lw = a.legend.iter().map(|t| width_of(t)).fold(0.0, f64::max) + 22.0;
    cv.plate(12.0, 10.0, lw, a.legend.len() as f64 * LH + 14.0, 6.0, ("#0c0e1c", 0.86), Some(("#3d4a75", 1.0)));
    for (i, t) in a.legend.iter().enumerate() {
        let ink = if i == 0 { "#eaf0fa" } else { "#b3c1da" };
        cv.text(23.0, 28.0 + i as f64 * LH, t, ink, i == 0, Anchor::Start);
    }

    image.rgba = cv.pixmap.take_demultiplied();
    Ok(())
}
