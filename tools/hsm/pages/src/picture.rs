//! Raster pictures: PNG artwork, cropped, resampled to print resolution, outlined and flattened.
//!
//! An outlined picture is its artwork at 432 pixels per inch with a fixed-width outline around
//! the artwork's silhouette, the band of the silhouette grown by the pen width that the artwork
//! does not cover. A side where the crop cuts through the artwork fades to white instead.
use crate::Rgb;
use anyhow::{Context, Result};
use std::io::Cursor;
use tiny_skia::{Paint, PathBuilder, Pixmap, Stroke, Transform};

/// The margin around an outlined picture, in points, that holds its outline.
pub const PAD: f64 = 3.0;
/// The resolution an outlined picture is drawn at.
pub const PPI: f64 = 432.0;

/// An opaque picture, 8-bit RGB rows from the top.
#[derive(Clone)]
pub struct RgbImage {
    pub width: u32,
    pub height: u32,
    pub data: Vec<u8>,
}

/// A picture with straight (unpremultiplied) 8-bit alpha, rows from the top.
#[derive(Clone)]
pub struct RgbaImage {
    pub width: u32,
    pub height: u32,
    pub data: Vec<u8>,
}

impl RgbImage {
    pub fn pixmap(&self) -> Option<Pixmap> {
        let rgba = self.data.chunks_exact(3).flat_map(|p| [p[0], p[1], p[2], 255]).collect();
        Pixmap::from_vec(rgba, tiny_skia::IntSize::from_wh(self.width, self.height)?)
    }

    pub fn png(&self) -> Result<Vec<u8>> {
        encode(self.width, self.height, png::ColorType::Rgb, &self.data)
    }

    /// The pixels of an opaque pixmap.
    pub fn from_pixmap(p: &Pixmap) -> RgbImage {
        RgbImage {
            width: p.width(),
            height: p.height(),
            data: p.data().chunks_exact(4).flat_map(|q| [q[0], q[1], q[2]]).collect(),
        }
    }
}

fn encode(width: u32, height: u32, color: png::ColorType, data: &[u8]) -> Result<Vec<u8>> {
    let mut out = Vec::new();
    let mut encoder = png::Encoder::new(&mut out, width, height);
    encoder.set_color(color);
    encoder.set_depth(png::BitDepth::Eight);
    let mut writer = encoder.write_header()?;
    writer.write_image_data(data)?;
    writer.finish()?;
    Ok(out)
}

impl RgbaImage {
    pub fn read_png(bytes: &[u8]) -> Result<RgbaImage> {
        let mut decoder = png::Decoder::new(Cursor::new(bytes));
        decoder.set_transformations(png::Transformations::EXPAND | png::Transformations::STRIP_16);
        let mut reader = decoder.read_info()?;
        let mut buf = vec![0; reader.output_buffer_size().context("a PNG too large to hold")?];
        let info = reader.next_frame(&mut buf)?;
        buf.truncate(info.buffer_size());
        let data = match info.color_type {
            png::ColorType::Rgba => buf,
            png::ColorType::Rgb => buf.chunks_exact(3).flat_map(|p| [p[0], p[1], p[2], 255]).collect(),
            png::ColorType::GrayscaleAlpha => buf.chunks_exact(2).flat_map(|p| [p[0], p[0], p[0], p[1]]).collect(),
            png::ColorType::Grayscale => buf.iter().flat_map(|&g| [g, g, g, 255]).collect(),
            png::ColorType::Indexed => anyhow::bail!("an indexed PNG survived expansion"),
        };
        Ok(RgbaImage { width: info.width, height: info.height, data })
    }

    pub fn png(&self) -> Result<Vec<u8>> {
        encode(self.width, self.height, png::ColorType::Rgba, &self.data)
    }

    fn alpha(&self, x: u32, y: u32) -> u8 {
        self.data[(y * self.width + x) as usize * 4 + 3]
    }

    /// The smallest box `[x0, y0, x1, y1)` holding every pixel with any alpha.
    pub fn alpha_bounds(&self) -> Option<[u32; 4]> {
        self.alpha_bounds_over(0)
    }

    /// The smallest box holding every pixel whose alpha is above `threshold`.
    pub fn alpha_bounds_over(&self, threshold: u8) -> Option<[u32; 4]> {
        let mut b = [u32::MAX, u32::MAX, 0, 0];
        for y in 0..self.height {
            for x in 0..self.width {
                if self.alpha(x, y) > threshold {
                    b = [b[0].min(x), b[1].min(y), b[2].max(x + 1), b[3].max(y + 1)];
                }
            }
        }
        (b[0] != u32::MAX).then_some(b)
    }

    /// The pixels inside `[x0, y0, x1, y1)`, transparent where the box leaves the picture.
    pub fn crop(&self, b: [i64; 4]) -> RgbaImage {
        let (w, h) = ((b[2] - b[0]).max(0) as u32, (b[3] - b[1]).max(0) as u32);
        let mut data = vec![0; (w * h * 4) as usize];
        for y in 0..h as i64 {
            let sy = y + b[1];
            if sy < 0 || sy >= self.height as i64 {
                continue;
            }
            for x in 0..w as i64 {
                let sx = x + b[0];
                if sx < 0 || sx >= self.width as i64 {
                    continue;
                }
                let s = (sy as usize * self.width as usize + sx as usize) * 4;
                let d = (y as usize * w as usize + x as usize) * 4;
                data[d..d + 4].copy_from_slice(&self.data[s..s + 4]);
            }
        }
        RgbaImage { width: w, height: h, data }
    }

    /// The picture over a solid `ground`.
    pub fn flatten(&self, ground: Rgb) -> RgbImage {
        let g = ground.bytes().map(|v| v as u32);
        let data = self
            .data
            .chunks_exact(4)
            .flat_map(|p| {
                let a = p[3] as u32;
                [0, 1, 2].map(|i| ((p[i] as u32 * a + g[i] * (255 - a) + 127) / 255) as u8)
            })
            .collect();
        RgbImage { width: self.width, height: self.height, data }
    }
}

/// The taps that resample one axis of `n` source samples onto `out` samples. Output sample
/// `i` sits at source position `(i + 0.5 - offset) / scale`; outside the source is transparent.
///
/// Each output pixel averages the source pixels its own width covers, each taken as a square:
/// a box as wide as the shrink, spread by one source pixel. Shrinking by less than a third,
/// or enlarging, that is bilinear.
struct Taps {
    first: Vec<usize>,
    weights: Vec<Vec<f32>>,
}

fn taps(n: usize, out: usize, offset: f64, scale: f64) -> Taps {
    let width = if 1.0 / scale < 1.0 / 0.75 { 1.0 } else { 1.0 / scale };
    let half = (width + 1.0) / 2.0;
    let mut first = Vec::with_capacity(out);
    let mut weights = Vec::with_capacity(out);
    for i in 0..out {
        let u = (i as f64 + 0.5 - offset) / scale;
        let lo = (u - half - 0.5).floor() as i64;
        let hi = (u + half - 0.5).ceil() as i64;
        let weight = |j: i64| (half - (j as f64 + 0.5 - u).abs()).min(width.min(1.0)).max(0.0);
        let total: f64 = (lo..=hi).map(weight).sum();
        let (a, b) = (lo.max(0), hi.min(n as i64 - 1));
        if total <= 0.0 || a > b {
            first.push(0);
            weights.push(Vec::new());
            continue;
        }
        first.push(a as usize);
        weights.push((a..=b).map(|j| (weight(j) / total) as f32).collect());
    }
    Taps { first, weights }
}

/// Premultiplied RGBA in floats from 0 to 1, rows from the top.
struct Layer {
    px: Vec<[f32; 4]>,
}

impl Layer {
    fn new(width: usize, height: usize) -> Layer {
        Layer { px: vec![[0.0; 4]; width * height] }
    }

    /// `image` drawn so its pixel `(u, v)` lands at `(origin + scale·u, origin + scale·v)`.
    fn draw(image: &RgbaImage, width: usize, height: usize, origin: [f64; 2], scale: f64) -> Layer {
        let mut layer = Layer::new(width, height);
        let (w, h) = (image.width as usize, image.height as usize);
        let across = taps(w, width, origin[0], scale);
        let down = taps(h, height, origin[1], scale);
        let used: Vec<usize> = (0..width).filter(|&x| !across.weights[x].is_empty()).collect();
        let Some(&x0) = used.first() else { return layer };
        let lo = across.first[x0];
        let hi = used.iter().map(|&x| across.first[x] + across.weights[x].len()).max().unwrap_or(lo);
        let mut row = vec![[0.0f32; 4]; hi - lo];
        for y in 0..height {
            if down.weights[y].is_empty() {
                continue;
            }
            row.iter_mut().for_each(|p| *p = [0.0; 4]);
            for (k, &wy) in down.weights[y].iter().enumerate() {
                let sy = down.first[y] + k;
                let src = &image.data[sy * w * 4..(sy + 1) * w * 4];
                for (i, p) in row.iter_mut().enumerate() {
                    let s = &src[(lo + i) * 4..(lo + i) * 4 + 4];
                    let a = s[3] as f32 / 255.0;
                    let f = wy * a / 255.0;
                    p[0] += s[0] as f32 * f;
                    p[1] += s[1] as f32 * f;
                    p[2] += s[2] as f32 * f;
                    p[3] += wy * a;
                }
            }
            for &x in &used {
                let mut acc = [0.0f32; 4];
                for (k, &wx) in across.weights[x].iter().enumerate() {
                    let p = row[across.first[x] + k - lo];
                    for c in 0..4 {
                        acc[c] += p[c] * wx;
                    }
                }
                layer.px[y * width + x] = acc.map(|v| v.clamp(0.0, 1.0));
            }
        }
        layer
    }

    /// `top` over this layer.
    fn under(&mut self, top: &Layer) {
        for (p, t) in self.px.iter_mut().zip(&top.px) {
            let k = 1.0 - t[3];
            for c in 0..4 {
                p[c] = t[c] + p[c] * k;
            }
        }
    }

    fn from_pixmap(p: &Pixmap) -> Layer {
        Layer {
            px: p.data().chunks_exact(4).map(|q| [q[0], q[1], q[2], q[3]].map(|v| v as f32 / 255.0)).collect(),
        }
    }
}

/// The greatest (`grow`) or least value within `radius` pixels along both axes, a square
/// window. Past the edge counts as empty.
fn morph(values: &[f32], width: usize, height: usize, radius: usize, grow: bool) -> Vec<f32> {
    let window = |line: &[f32], i: usize| -> f32 {
        let n = line.len();
        if !grow && (i < radius || i + radius >= n) {
            return 0.0;
        }
        let w = &line[i.saturating_sub(radius)..=(i + radius).min(n - 1)];
        if grow { w.iter().copied().fold(0.0, f32::max) } else { w.iter().copied().fold(1.0, f32::min) }
    };
    let mut across = vec![0.0; values.len()];
    for y in 0..height {
        let row = &values[y * width..(y + 1) * width];
        for x in 0..width {
            across[y * width + x] = window(row, x);
        }
    }
    let mut out = vec![0.0; values.len()];
    let mut column = vec![0.0; height];
    for x in 0..width {
        for y in 0..height {
            column[y] = across[y * width + x];
        }
        for y in 0..height {
            out[y * width + x] = window(&column, y);
        }
    }
    out
}

/// A fade along one side of a picture: the gradient's value at `t` across its extent.
fn fade(t: f64, from: f64, to: f64, f: f64) -> f64 {
    let t = t.clamp(0.0, 1.0);
    if t < f {
        from + (1.0 - from) * t / f
    } else if t > 1.0 - f {
        1.0 + (to - 1.0) * (t - (1.0 - f)) / f
    } else {
        1.0
    }
}

/// One axis of the fade over `n` pixels: the band from `lo` to `hi`, in the picture's points
/// at `k` pixels a point from `offset`, carries the gradient and nothing shows outside it.
///
/// The fade lands where the outlined pictures first printed it: their renderer held the
/// gradient's step across a pixel to sixteen binary places, measured from the band's centre,
/// which on a picture this wide moves each end of the fade by up to a point and a half.
fn fade_axis(n: usize, offset: f64, k: f64, lo: f64, hi: f64, ends: [f64; 2], f: f64) -> Vec<f64> {
    let (left, right) = (offset + k * lo, offset + k * hi);
    let step = (65536.0 / (right - left)).round() / 65536.0;
    let centre = (left + right) / 2.0;
    (0..n)
        .map(|i| {
            let x = i as f64 + 0.5;
            let cover = ((x + 0.5).min(right) - (x - 0.5).max(left)).clamp(0.0, 1.0);
            cover * fade(0.5 + step * (x - centre), ends[0], ends[1], f)
        })
        .collect()
}

/// An outlined picture's makings.
pub struct Outlined<'a> {
    pub artwork: &'a RgbaImage,
    /// The crop `[x0, y0, x1, y1]`, in artwork pixels.
    pub crop: [f64; 4],
    /// The width the crop is drawn at, in points.
    pub width: f64,
    /// Fade the sides where the crop cuts through the artwork.
    pub fade_crops: bool,
    pub color: Rgb,
    pub pen: f64,
    /// More silhouette, in the artwork's own frame, drawn nowhere else.
    pub silhouette: Option<&'a RgbaImage>,
    /// A closed line stroked over the picture, in its points from the padded picture's corner.
    pub stroke: Option<Vec<[f64; 2]>>,
    /// Lines in artwork pixels, stroked with round ends where they fall inside the silhouette.
    pub inner: Vec<Vec<[f64; 2]>>,
}

impl Outlined<'_> {
    /// The crop's height in points.
    pub fn height(&self) -> f64 {
        (self.crop[3] - self.crop[1]) * self.width / (self.crop[2] - self.crop[0])
    }

    /// The padded picture's size in points: the crop with `PAD` on every side.
    pub fn size(&self) -> [f64; 2] {
        [self.width + 2.0 * PAD, self.height() + 2.0 * PAD]
    }

    /// Where the whole artwork lands, `[x, y, w, h]` in the padded picture's points.
    pub fn placement(&self) -> [f64; 4] {
        let s = self.width / (self.crop[2] - self.crop[0]);
        [
            PAD - self.crop[0] * s,
            PAD - self.crop[1] * s,
            self.artwork.width as f64 * s,
            self.artwork.height as f64 * s,
        ]
    }

    /// Whether each side, left, right, top and bottom, cuts through the artwork.
    fn cuts(&self) -> [bool; 4] {
        if !self.fade_crops {
            return [false; 4];
        }
        let (w, h) = (self.artwork.width as f64, self.artwork.height as f64);
        let [a, b, c, d] = [self.crop[0].max(0.0), self.crop[1].max(0.0), self.crop[2].min(w), self.crop[3].min(h)];
        let bands = [[a, b, a + 1.0, d], [c - 1.0, b, c, d], [a, b, c, b + 1.0], [a, d - 1.0, c, d]];
        bands.map(|band| {
            let [x0, y0, x1, y1] = band.map(|v| v.round() as i64);
            let mut most = 0;
            for y in y0.max(0)..y1.min(h as i64) {
                for x in x0.max(0)..x1.min(w as i64) {
                    most = most.max(self.artwork.alpha(x as u32, y as u32));
                }
            }
            most > 100
        })
    }

    /// The padded picture at `PPI`, on white.
    pub fn draw(&self) -> RgbImage {
        let [pw, ph] = self.size();
        let (iw, ih) = (self.width, self.height());
        let (cols, rows) = ((pw * PPI / 72.0).ceil() as usize, (ph * PPI / 72.0).ceil() as usize);
        let k = (cols as f64 / pw).min(rows as f64 / ph);
        let (tx, ty) = ((cols as f64 - pw * k) / 2.0, (rows as f64 - ph * k) / 2.0);
        let [x, y, w, _] = self.placement();
        let s = w / self.artwork.width as f64;
        // The outline's reach in pixels, a whole pixel past the pen's width.
        let radius = (self.pen * k).ceil() as usize;

        // The silhouette, over a margin wide enough for the outline to reach in from past the
        // picture's edge.
        let m = radius + 2;
        let (ew, eh) = (cols + 2 * m, rows + 2 * m);
        let origin = [tx + k * x + m as f64, ty + k * y + m as f64];
        let art = Layer::draw(self.artwork, ew, eh, origin, k * s);
        let mut cover: Vec<f32> = art.px.iter().map(|p| p[3]).collect();
        if let Some(more) = self.silhouette {
            let more = Layer::draw(more, ew, eh, origin, k * s);
            for (c, p) in cover.iter_mut().zip(&more.px) {
                *c += p[3] * (1.0 - *c);
            }
        }
        let solid: Vec<f32> = cover.iter().map(|a| (a * 40.0).min(1.0)).collect();
        let grown = morph(&solid, ew, eh, radius, true);
        let inside = if self.inner.is_empty() { Vec::new() } else { morph(&solid, ew, eh, radius, false) };

        // The outline band, then the artwork over it.
        let [cr, cg, cb] = [self.color.r, self.color.g, self.color.b].map(|v| v as f32);
        let mut picture = Layer::new(cols, rows);
        for yy in 0..rows {
            for xx in 0..cols {
                let e = (yy + m) * ew + xx + m;
                let band = grown[e] * (1.0 - solid[e]);
                let a = art.px[e];
                let under = [cr * band, cg * band, cb * band, band];
                let kk = 1.0 - a[3];
                picture.px[yy * cols + xx] = [0, 1, 2, 3].map(|c| a[c] + under[c] * kk);
            }
        }

        let place = Transform::from_row(k as f32, 0.0, 0.0, k as f32, tx as f32, ty as f32);
        let [r8, g8, b8] = self.color.bytes();
        let mut paint = Paint::default();
        paint.set_color_rgba8(r8, g8, b8, 255);
        paint.anti_alias = true;
        if let Some(line) = &self.stroke {
            let mut pb = PathBuilder::new();
            for (i, p) in line.iter().enumerate() {
                if i == 0 {
                    pb.move_to(p[0] as f32, p[1] as f32);
                } else {
                    pb.line_to(p[0] as f32, p[1] as f32);
                }
            }
            pb.close();
            if let (Some(path), Some(mut layer)) = (pb.finish(), Pixmap::new(cols as u32, rows as u32)) {
                let pen = Stroke { width: self.pen as f32, miter_limit: 4.0, ..Stroke::default() };
                layer.stroke_path(&path, &paint, &pen, place, None);
                picture.under(&Layer::from_pixmap(&layer));
            }
        }
        if !self.inner.is_empty() {
            let mut pb = PathBuilder::new();
            for line in &self.inner {
                for (i, p) in line.iter().enumerate() {
                    let (px, py) = ((x + s * p[0]) as f32, (y + s * p[1]) as f32);
                    if i == 0 {
                        pb.move_to(px, py);
                    } else {
                        pb.line_to(px, py);
                    }
                }
                pb.close();
            }
            if let (Some(path), Some(mut layer)) = (pb.finish(), Pixmap::new(cols as u32, rows as u32)) {
                let pen = Stroke {
                    width: self.pen as f32,
                    line_cap: tiny_skia::LineCap::Round,
                    line_join: tiny_skia::LineJoin::Round,
                    ..Stroke::default()
                };
                layer.stroke_path(&path, &paint, &pen, place, None);
                let mut lines = Layer::from_pixmap(&layer);
                for yy in 0..rows {
                    for xx in 0..cols {
                        let keep = inside[(yy + m) * ew + xx + m];
                        lines.px[yy * cols + xx] = lines.px[yy * cols + xx].map(|v| v * keep);
                    }
                }
                picture.under(&lines);
            }
        }
        // Fade each cut side to nothing over a few points, then lay the picture on white.
        let cut = self.cuts();
        let (fx, fy) = ((3.2f64).min(iw * 0.035) / iw, (3.2f64).min(ih * 0.05) / ih);
        let (x0, x1) = (if cut[0] { PAD } else { 0.0 }, if cut[1] { PAD + iw } else { pw });
        let (y0, y1) = (if cut[2] { PAD } else { 0.0 }, if cut[3] { PAD + ih } else { ph });
        let ends = |a: bool, b: bool| [a, b].map(|c| if c { 0.0 } else { 1.0 });
        let across = fade_axis(cols, tx, k, x0, x1, ends(cut[0], cut[1]), fx);
        let down = fade_axis(rows, ty, k, y0, y1, ends(cut[2], cut[3]), fy);
        let mut data = Vec::with_capacity(cols * rows * 3);
        for yy in 0..rows {
            for xx in 0..cols {
                let f = (across[xx] * down[yy]) as f32;
                let p = picture.px[yy * cols + xx];
                let a = p[3] * f;
                for c in 0..3 {
                    data.push(((p[c] * f + (1.0 - a)) * 255.0).round().clamp(0.0, 255.0) as u8);
                }
            }
        }
        RgbImage { width: cols as u32, height: rows as u32, data }
    }
}
