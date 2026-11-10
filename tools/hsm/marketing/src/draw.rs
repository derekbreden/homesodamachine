//! Vector paths and font outlines draw the on-demand artwork through the shared page rasterizer.
use anyhow::{Context, Result, bail};
use std::{fs, path::Path};
use tiny_skia::{Color, FillRule, Paint, PathBuilder, Pixmap, Stroke, Transform};

pub fn rgba(value: &str) -> Color {
    let s = value.trim_start_matches('#');
    let named = match s {
        "white" => "ffffff",
        "black" => "000000",
        "yellow" => "ffff00",
        "red" => "ff0000",
        "orange" => "ff7a2d",
        _ => s,
    };
    let hex = u32::from_str_radix(named, 16).unwrap_or(0xffffff);
    if named.len() == 8 {
        Color::from_rgba8(
            (hex >> 24) as u8,
            (hex >> 16) as u8,
            (hex >> 8) as u8,
            hex as u8,
        )
    } else {
        Color::from_rgba8((hex >> 16) as u8, (hex >> 8) as u8, hex as u8, 255)
    }
}
pub fn paint(color: Color) -> Paint<'static> {
    let mut p = Paint::default();
    p.set_color(color);
    p
}
pub fn path(pixels: &mut Pixmap, shape: &tiny_skia::Path, color: Color, transform: Transform) {
    pixels.fill_path(shape, &paint(color), FillRule::Winding, transform, None);
}
pub fn line(
    pixels: &mut Pixmap,
    shape: &tiny_skia::Path,
    color: Color,
    width: f64,
    transform: Transform,
) {
    pixels.stroke_path(
        shape,
        &paint(color),
        &Stroke {
            width: width as f32,
            ..Stroke::default()
        },
        transform,
        None,
    );
}
pub fn source_path(
    pixels: &mut Pixmap,
    shape: &tiny_skia::Path,
    color: Color,
    width: Option<f64>,
    transform: Transform,
) {
    let mut paint = paint(color);
    paint.blend_mode = tiny_skia::BlendMode::Source;
    if let Some(width) = width {
        pixels.stroke_path(
            shape,
            &paint,
            &Stroke {
                width: width as f32,
                ..Default::default()
            },
            transform,
            None,
        );
    } else {
        pixels.fill_path(shape, &paint, FillRule::Winding, transform, None);
    }
}
pub fn rect(pixels: &mut Pixmap, xywh: [f64; 4], radius: f64, color: Color, transform: Transform) {
    let [x, y, w, h] = xywh;
    let page = hsm_pages::page::Path::round_rect(x, y, w, h, radius);
    let mut builder = PathBuilder::new();
    for seg in page.segs {
        use hsm_pages::page::Seg;
        match seg {
            Seg::Move(p) => builder.move_to(p[0] as f32, p[1] as f32),
            Seg::Line(p) => builder.line_to(p[0] as f32, p[1] as f32),
            Seg::Cubic(a, b, c) => builder.cubic_to(
                a[0] as f32,
                a[1] as f32,
                b[0] as f32,
                b[1] as f32,
                c[0] as f32,
                c[1] as f32,
            ),
            Seg::Close => builder.close(),
        }
    }
    if let Some(shape) = builder.finish() {
        path(pixels, &shape, color, transform);
    }
}
pub fn circle(
    pixels: &mut Pixmap,
    center: [f64; 2],
    radius: f64,
    color: Color,
    width: Option<f64>,
    transform: Transform,
) {
    if radius <= 0.0 {
        return;
    }
    if let Some(shape) = PathBuilder::from_circle(center[0] as f32, center[1] as f32, radius as f32)
    {
        if let Some(width) = width {
            line(pixels, &shape, color, width, transform);
        } else {
            path(pixels, &shape, color, transform);
        }
    }
}
pub fn polygon(
    pixels: &mut Pixmap,
    points: &[[f64; 2]],
    color: Color,
    width: Option<f64>,
    transform: Transform,
) {
    if points.is_empty() {
        return;
    }
    let mut builder = PathBuilder::new();
    builder.move_to(points[0][0] as f32, points[0][1] as f32);
    for point in &points[1..] {
        builder.line_to(point[0] as f32, point[1] as f32);
    }
    if width.is_none() || points.len() > 2 {
        builder.close();
    }
    if let Some(shape) = builder.finish() {
        if let Some(width) = width {
            line(pixels, &shape, color, width, transform);
        } else {
            path(pixels, &shape, color, transform);
        }
    }
}

pub struct Typeface {
    data: Vec<u8>,
    index: u32,
    weight: Option<f32>,
}
impl Typeface {
    pub fn new(path: &Path, index: u32) -> Result<Self> {
        let data = fs::read(path).with_context(|| format!("font {}", path.display()))?;
        ttf_parser::Face::parse(&data, index).context("font face")?;
        Ok(Self {
            data,
            index,
            weight: None,
        })
    }
    fn face(&self) -> ttf_parser::Face<'_> {
        let mut face = ttf_parser::Face::parse(&self.data, self.index).unwrap();
        if let Some(weight) = self.weight {
            face.set_variation(ttf_parser::Tag::from_bytes(b"wght"), weight);
        }
        face
    }
    pub fn weight(mut self, weight: f32) -> Self {
        self.weight = Some(weight);
        self
    }
    pub fn top_left(&self, pixels: &mut Pixmap, text: &str, size: f64, at: [f64; 2], color: Color) {
        if let Some(shape) = self.outline(text, size, 0.) {
            let bounds = shape.bounds();
            path(
                pixels,
                &shape,
                color,
                Transform::from_translate(
                    at[0] as f32 - bounds.left(),
                    at[1] as f32 - bounds.top(),
                ),
            );
        }
    }
    pub fn width(&self, text: &str, size: f64, tracking: f64) -> f64 {
        let face = self.face();
        text.chars()
            .map(|c| {
                face.glyph_index(c)
                    .and_then(|id| face.glyph_hor_advance(id))
                    .unwrap_or(0) as f64
                    * size
                    / face.units_per_em() as f64
            })
            .sum::<f64>()
            + text.chars().count().saturating_sub(1) as f64 * tracking
    }
    pub fn outline(&self, text: &str, size: f64, tracking: f64) -> Option<tiny_skia::Path> {
        let face = self.face();
        let scale = size / face.units_per_em() as f64;
        let mut sink = Glyph {
            builder: PathBuilder::new(),
            scale,
            x: 0.0,
        };
        for c in text.chars() {
            if let Some(id) = face.glyph_index(c) {
                face.outline_glyph(id, &mut sink);
                sink.x += face.glyph_hor_advance(id).unwrap_or(0) as f64 * scale + tracking;
            }
        }
        sink.builder.finish()
    }
    pub fn center(
        &self,
        pixels: &mut Pixmap,
        text: &str,
        size: f64,
        tracking: f64,
        center: [f64; 2],
        rotate: f64,
        color: Color,
        transform: Transform,
    ) {
        if let Some(shape) = self.outline(text, size, tracking) {
            let bounds = shape.bounds();
            let local = Transform::from_translate(center[0] as f32, center[1] as f32)
                .pre_rotate(-(rotate as f32))
                .pre_translate(
                    -(bounds.left() + bounds.width() / 2.),
                    -(bounds.top() + bounds.height() / 2.),
                );
            path(pixels, &shape, color, transform.pre_concat(local));
        }
    }
}
struct Glyph {
    builder: PathBuilder,
    scale: f64,
    x: f64,
}
impl Glyph {
    fn p(&self, x: f32, y: f32) -> (f32, f32) {
        (
            (self.x + x as f64 * self.scale) as f32,
            (-y as f64 * self.scale) as f32,
        )
    }
}
impl ttf_parser::OutlineBuilder for Glyph {
    fn move_to(&mut self, x: f32, y: f32) {
        let (x, y) = self.p(x, y);
        self.builder.move_to(x, y);
    }
    fn line_to(&mut self, x: f32, y: f32) {
        let (x, y) = self.p(x, y);
        self.builder.line_to(x, y);
    }
    fn quad_to(&mut self, x1: f32, y1: f32, x: f32, y: f32) {
        let a = self.p(x1, y1);
        let b = self.p(x, y);
        self.builder.quad_to(a.0, a.1, b.0, b.1);
    }
    fn curve_to(&mut self, x1: f32, y1: f32, x2: f32, y2: f32, x: f32, y: f32) {
        let a = self.p(x1, y1);
        let b = self.p(x2, y2);
        let c = self.p(x, y);
        self.builder.cubic_to(a.0, a.1, b.0, b.1, c.0, c.1);
    }
    fn close(&mut self) {
        self.builder.close();
    }
}

pub fn attribute<'a>(tag: &'a str, name: &str) -> Result<&'a str> {
    let prefix = format!("{name}=\"");
    let start = tag
        .match_indices(&prefix)
        .find(|(index, _)| *index == 0 || tag.as_bytes()[index - 1].is_ascii_whitespace())
        .map(|(index, _)| index)
        .with_context(|| format!("attribute {name}"))?
        + prefix.len();
    Ok(&tag[start..start + tag[start..].find('"').context("closing attribute quote")?])
}
pub fn tags<'a>(svg: &'a str, name: &'a str) -> impl Iterator<Item = &'a str> {
    let prefix = format!("<{name} ");
    svg.match_indices('<').filter_map(move |(start, _)| {
        let tag = &svg[start..];
        tag.starts_with(&prefix)
            .then(|| tag.find('>').map(|end| &tag[..end + 1]))
            .flatten()
    })
}

#[derive(Clone, Copy)]
enum Token {
    Command(char),
    Number(f64),
}
fn tokens(text: &str) -> Result<Vec<Token>> {
    let bytes = text.as_bytes();
    let mut i = 0;
    let mut out = Vec::new();
    while i < bytes.len() {
        if bytes[i].is_ascii_whitespace() || bytes[i] == b',' {
            i += 1;
            continue;
        }
        if bytes[i].is_ascii_alphabetic() {
            out.push(Token::Command(bytes[i] as char));
            i += 1;
            continue;
        }
        let start = i;
        if matches!(bytes[i], b'+' | b'-') {
            i += 1;
        }
        while i < bytes.len() && (bytes[i].is_ascii_digit() || bytes[i] == b'.') {
            i += 1;
        }
        if i < bytes.len() && matches!(bytes[i], b'e' | b'E') {
            i += 1;
            if i < bytes.len() && matches!(bytes[i], b'+' | b'-') {
                i += 1;
            }
            while i < bytes.len() && bytes[i].is_ascii_digit() {
                i += 1;
            }
        }
        if start == i {
            bail!("invalid SVG path at {}", &text[i..]);
        }
        out.push(Token::Number(text[start..i].parse()?));
    }
    Ok(out)
}
fn next_number(tokens: &[Token], i: &mut usize) -> Result<f64> {
    let Some(Token::Number(n)) = tokens.get(*i) else {
        bail!("SVG path number");
    };
    *i += 1;
    Ok(*n)
}

/// Parse source SVG commands into cubics; the flattened contour feeds the PCB's source silhouette.
pub fn svg_path(text: &str) -> Result<(tiny_skia::Path, Vec<[f64; 2]>)> {
    let tokens = tokens(text)?;
    let mut i = 0;
    let mut command = 'M';
    let mut current = [0., 0.];
    let mut start = current;
    let mut control = current;
    let mut previous = 'M';
    let mut builder = PathBuilder::new();
    let mut points = Vec::new();
    while i < tokens.len() {
        if let Token::Command(c) = tokens[i] {
            command = c;
            i += 1;
        }
        let relative = command.is_ascii_lowercase();
        let upper = command.to_ascii_uppercase();
        if upper == 'Z' {
            builder.close();
            current = start;
            points.push(start);
            previous = upper;
            continue;
        }
        let origin = current;
        let mut number = || next_number(&tokens, &mut i);
        let mut pair = || -> Result<[f64; 2]> {
            let x = number()?;
            let y = number()?;
            Ok(if relative {
                [origin[0] + x, origin[1] + y]
            } else {
                [x, y]
            })
        };
        match upper {
            'M' | 'L' => {
                let p = pair()?;
                if upper == 'M' {
                    builder.move_to(p[0] as f32, p[1] as f32);
                    start = p;
                    command = if relative { 'l' } else { 'L' };
                } else {
                    builder.line_to(p[0] as f32, p[1] as f32);
                }
                current = p;
                points.push(p);
            }
            'H' | 'V' => {
                let v = number()?;
                current[if upper == 'H' { 0 } else { 1 }] = v + if relative {
                    origin[if upper == 'H' { 0 } else { 1 }]
                } else {
                    0.
                };
                builder.line_to(current[0] as f32, current[1] as f32);
                points.push(current);
            }
            'C' | 'S' => {
                let a = if upper == 'C' {
                    pair()?
                } else if matches!(previous, 'C' | 'S') {
                    [2. * origin[0] - control[0], 2. * origin[1] - control[1]]
                } else {
                    origin
                };
                let b = pair()?;
                let p = pair()?;
                cubic(&mut builder, &mut points, origin, a, b, p);
                current = p;
                control = b;
            }
            'Q' | 'T' => {
                let a = if upper == 'Q' {
                    pair()?
                } else if matches!(previous, 'Q' | 'T') {
                    [2. * origin[0] - control[0], 2. * origin[1] - control[1]]
                } else {
                    origin
                };
                let p = pair()?;
                let c1 = std::array::from_fn(|k| origin[k] + (a[k] - origin[k]) * 2. / 3.);
                let c2 = std::array::from_fn(|k| p[k] + (a[k] - p[k]) * 2. / 3.);
                cubic(&mut builder, &mut points, origin, c1, c2, p);
                current = p;
                control = a;
            }
            'A' => {
                let rx = number()?.abs();
                let ry = number()?.abs();
                let angle = number()?.to_radians();
                let large = number()? != 0.;
                let sweep = number()? != 0.;
                let x = number()?;
                let y = number()?;
                let p = if relative {
                    [origin[0] + x, origin[1] + y]
                } else {
                    [x, y]
                };
                arc(
                    &mut builder,
                    &mut points,
                    origin,
                    p,
                    rx,
                    ry,
                    angle,
                    large,
                    sweep,
                );
                current = p;
            }
            _ => bail!("unsupported SVG path command {command}"),
        }
        previous = upper;
    }
    Ok((builder.finish().context("nonempty SVG path")?, points))
}
fn cubic(
    builder: &mut PathBuilder,
    points: &mut Vec<[f64; 2]>,
    p: [f64; 2],
    a: [f64; 2],
    b: [f64; 2],
    to: [f64; 2],
) {
    builder.cubic_to(
        a[0] as f32,
        a[1] as f32,
        b[0] as f32,
        b[1] as f32,
        to[0] as f32,
        to[1] as f32,
    );
    for n in 1..=16 {
        let t = n as f64 / 16.;
        let u = 1. - t;
        points.push(std::array::from_fn(|k| {
            u * u * u * p[k] + 3. * u * u * t * a[k] + 3. * u * t * t * b[k] + t * t * t * to[k]
        }));
    }
}
fn arc(
    builder: &mut PathBuilder,
    points: &mut Vec<[f64; 2]>,
    from: [f64; 2],
    to: [f64; 2],
    mut rx: f64,
    mut ry: f64,
    angle: f64,
    large: bool,
    sweep: bool,
) {
    if rx == 0. || ry == 0. || from == to {
        builder.line_to(to[0] as f32, to[1] as f32);
        points.push(to);
        return;
    }
    let (sin, cos) = angle.sin_cos();
    let dx = (from[0] - to[0]) / 2.;
    let dy = (from[1] - to[1]) / 2.;
    let x = cos * dx + sin * dy;
    let y = -sin * dx + cos * dy;
    let radii = x * x / (rx * rx) + y * y / (ry * ry);
    if radii > 1. {
        let s = radii.sqrt();
        rx *= s;
        ry *= s;
    }
    let factor = (((rx * rx * ry * ry - rx * rx * y * y - ry * ry * x * x)
        / (rx * rx * y * y + ry * ry * x * x))
        .max(0.))
    .sqrt()
        * if large == sweep { -1. } else { 1. };
    let cx1 = factor * rx * y / ry;
    let cy1 = -factor * ry * x / rx;
    let center = [
        cos * cx1 - sin * cy1 + (from[0] + to[0]) / 2.,
        sin * cx1 + cos * cy1 + (from[1] + to[1]) / 2.,
    ];
    let begin = ((y - cy1) / ry).atan2((x - cx1) / rx);
    let end = ((-y - cy1) / ry).atan2((-x - cx1) / rx);
    let mut delta = end - begin;
    if sweep && delta < 0. {
        delta += std::f64::consts::TAU;
    }
    if !sweep && delta > 0. {
        delta -= std::f64::consts::TAU;
    }
    let count = (delta.abs() / std::f64::consts::FRAC_PI_2).ceil() as usize;
    let mut p = from;
    let at = |theta: f64| {
        [
            center[0] + rx * cos * theta.cos() - ry * sin * theta.sin(),
            center[1] + rx * sin * theta.cos() + ry * cos * theta.sin(),
        ]
    };
    let tangent = |theta: f64| {
        [
            -rx * cos * theta.sin() - ry * sin * theta.cos(),
            -rx * sin * theta.sin() + ry * cos * theta.cos(),
        ]
    };
    for j in 0..count {
        let a = begin + delta * j as f64 / count as f64;
        let b = begin + delta * (j + 1) as f64 / count as f64;
        let k = 4. / 3. * ((b - a) / 4.).tan();
        let q = at(b);
        let ta = tangent(a);
        let tb = tangent(b);
        cubic(
            builder,
            points,
            p,
            [p[0] + k * ta[0], p[1] + k * ta[1]],
            [q[0] - k * tb[0], q[1] - k * tb[1]],
            q,
        );
        p = q;
    }
}

pub fn resized(source: &Pixmap, width: u32, height: u32) -> Result<Pixmap> {
    if width <= source.width() && height <= source.height() {
        let source_image = hsm_render::image::Image::from_frame(
            source.data().to_vec(),
            source.width(),
            source.height(),
            true,
        );
        let resized = source_image.fit_inside(width.max(height));
        if resized.width == width && resized.height == height {
            let mut pixels = Pixmap::new(width, height).context("image dimensions")?;
            for (pixel, rgba) in pixels
                .pixels_mut()
                .iter_mut()
                .zip(resized.rgba.chunks_exact(4))
            {
                let a = rgba[3] as u32;
                *pixel = tiny_skia::PremultipliedColorU8::from_rgba(
                    ((rgba[0] as u32 * a + 127) / 255) as u8,
                    ((rgba[1] as u32 * a + 127) / 255) as u8,
                    ((rgba[2] as u32 * a + 127) / 255) as u8,
                    rgba[3],
                )
                .unwrap();
            }
            return Ok(pixels);
        }
    }
    let mut out = Pixmap::new(width, height).context("image dimensions")?;
    out.draw_pixmap(
        0,
        0,
        source.as_ref(),
        &tiny_skia::PixmapPaint {
            quality: tiny_skia::FilterQuality::Bicubic,
            ..Default::default()
        },
        Transform::from_scale(
            width as f32 / source.width() as f32,
            height as f32 / source.height() as f32,
        ),
        None,
    );
    Ok(out)
}

pub fn blur(pixels: &mut Pixmap, sigma: f64) {
    let w = pixels.width() as usize;
    let h = pixels.height() as usize;
    let r = (sigma * 0.95).ceil() as usize;
    let mut data: Vec<[f64; 4]> = pixels
        .pixels()
        .iter()
        .map(|p| {
            [
                p.red() as f64,
                p.green() as f64,
                p.blue() as f64,
                p.alpha() as f64,
            ]
        })
        .collect();
    let mut out = data.clone();
    for _ in 0..3 {
        for axis in 0..2 {
            let (n, m) = if axis == 0 { (w, h) } else { (h, w) };
            for j in 0..m {
                let index = |i: usize| if axis == 0 { j * w + i } else { i * w + j };
                let mut sum = [0.; 4];
                for i in 0..=r.min(n - 1) {
                    for c in 0..4 {
                        sum[c] += data[index(i)][c];
                    }
                }
                for i in 0..n {
                    if i > 0 {
                        if i + r < n {
                            for c in 0..4 {
                                sum[c] += data[index(i + r)][c];
                            }
                        }
                        if i > r {
                            for c in 0..4 {
                                sum[c] -= data[index(i - r - 1)][c];
                            }
                        }
                    }
                    out[index(i)] = sum.map(|x| x / (2 * r + 1) as f64);
                }
            }
            std::mem::swap(&mut data, &mut out);
        }
    }
    for (p, c) in pixels.pixels_mut().iter_mut().zip(data) {
        *p = tiny_skia::PremultipliedColorU8::from_rgba(
            c[0] as u8, c[1] as u8, c[2] as u8, c[3] as u8,
        )
        .unwrap();
    }
}
