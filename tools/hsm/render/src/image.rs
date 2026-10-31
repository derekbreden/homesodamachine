//! A frame once it is off the GPU: straight-alpha RGBA, trimmed and fitted as sharp trims and
//! fits, written as PNG, and two frames joined into one picture.

use anyhow::{Context, Result};
use std::io::Cursor;

#[derive(Clone)]
pub struct Image {
    pub width: u32,
    pub height: u32,
    /// Straight-alpha RGBA, top row first.
    pub rgba: Vec<u8>,
    /// Every pixel is opaque, so the PNG is written without an alpha channel.
    pub opaque: bool,
}

/// A twin's ground, the site navy, and the hairline that parts its two frames.
const TWIN_BG: [u8; 3] = [0x1a, 0x1a, 0x2e];
const TWIN_HAIRLINE: [u8; 3] = [0x3a, 0x3a, 0x5a];
const TWIN_GAP: u32 = 3;

impl Image {
    /// The frame as the GPU blended it. Over a clear background the colour comes back
    /// premultiplied by its coverage, and is divided back out.
    pub fn from_frame(mut rgba: Vec<u8>, width: u32, height: u32, transparent: bool) -> Image {
        if transparent {
            for px in rgba.chunks_exact_mut(4) {
                let a = px[3] as u32;
                if a != 0 && a != 255 {
                    for c in &mut px[..3] {
                        *c = ((*c as u32 * 255 + a / 2) / a).min(255) as u8;
                    }
                }
            }
        } else {
            for px in rgba.chunks_exact_mut(4) {
                px[3] = 255;
            }
        }
        Image {
            width,
            height,
            rgba,
            opaque: !transparent,
        }
    }

    fn crop(&self, x: u32, y: u32, w: u32, h: u32) -> Image {
        let mut rgba = Vec::with_capacity((w * h * 4) as usize);
        for row in y..y + h {
            let at = ((row * self.width + x) * 4) as usize;
            rgba.extend_from_slice(&self.rgba[at..at + (w * 4) as usize]);
        }
        Image {
            width: w,
            height: h,
            rgba,
            opaque: self.opaque,
        }
    }

    /// sharp's `trim({background, threshold})`: libvips `find_trim` on the frame flattened onto
    /// the background and, for a frame with alpha, on its alpha against clear, cropped to the box
    /// holding both. A frame with nothing on it is kept.
    pub fn trim(&self, background: [u8; 3], threshold: u8) -> Image {
        let (w, h) = (self.width as usize, self.height as usize);
        let rgba = &self.rgba;
        let opaque = self.opaque;
        let flat = |i: usize| -> [u8; 3] {
            let p = &rgba[4 * i..4 * i + 4];
            if opaque {
                return [p[0], p[1], p[2]];
            }
            let a = p[3] as u32;
            std::array::from_fn(|c| ((p[c] as u32 * a + background[c] as u32 * (255 - a) + 127) / 255) as u8)
        };
        let colour = trim_box(w, h, threshold, background, flat);
        let alpha = if opaque { None } else { trim_box(w, h, threshold, [0], |i| [rgba[4 * i + 3]]) };
        let (x0, y0, x1, y1) = match (colour, alpha) {
            (Some(c), Some(a)) => (c.0.min(a.0), c.1.min(a.1), c.2.max(a.2), c.3.max(a.3)),
            (Some(b), None) | (None, Some(b)) => b,
            (None, None) => return self.clone(),
        };
        self.crop(x0 as u32, y0 as u32, (x1 - x0 + 1) as u32, (y1 - y0 + 1) as u32)
    }

    /// sharp's `resize({width: max, height: max, fit: "inside", withoutEnlargement: true})`:
    /// the long side brought down to `max`, Lanczos-3, and never up.
    pub fn fit_inside(&self, max: u32) -> Image {
        let scale = (max as f64 / self.width as f64).min(max as f64 / self.height as f64);
        if scale >= 1.0 {
            return self.clone();
        }
        let w = ((self.width as f64 * scale).round() as u32).max(1);
        let h = ((self.height as f64 * scale).round() as u32).max(1);
        self.resample(w, h)
    }

    /// Separable Lanczos-3, the kernel widened by the reduction: across each row from the 8-bit
    /// frame, then down the columns of that, back to 8 bits. A frame with any clear pixel is
    /// resampled premultiplied, so a clear pixel lends its neighbours no colour.
    fn resample(&self, ow: u32, oh: u32) -> Image {
        let (iw, ih, ow, oh) = (self.width as usize, self.height as usize, ow as usize, oh as usize);
        let ch = if self.opaque { 3 } else { 4 };
        let across = taps(iw, ow);
        let mut mid = vec![0f32; ow * ih * ch];
        let rgba = &self.rgba;
        by_rows(&mut mid, ow * ch, |y, row| {
            let line = &rgba[y * iw * 4..(y + 1) * iw * 4];
            for (x, (lo, weights)) in across.iter().enumerate() {
                let mut acc = [0f32; 4];
                for (k, wgt) in weights.iter().enumerate() {
                    let p = &line[(lo + k) * 4..(lo + k) * 4 + 4];
                    let a = if ch == 4 { p[3] as f32 / 255.0 } else { 1.0 };
                    for c in 0..3 {
                        acc[c] += wgt * p[c] as f32 * a;
                    }
                    acc[3] += wgt * p[3] as f32;
                }
                row[x * ch..x * ch + ch].copy_from_slice(&acc[..ch]);
            }
        });
        let down = taps(ih, oh);
        let mut out = vec![0f32; ow * oh * ch];
        by_rows(&mut out, ow * ch, |y, row| {
            let (lo, weights) = &down[y];
            for (k, wgt) in weights.iter().enumerate() {
                let line = &mid[(lo + k) * ow * ch..(lo + k + 1) * ow * ch];
                for (o, v) in row.iter_mut().zip(line) {
                    *o += wgt * v;
                }
            }
        });
        let byte = |v: f32| v.round().clamp(0.0, 255.0) as u8;
        let rgba = out
            .chunks_exact(ch)
            .flat_map(|p| {
                if ch == 3 {
                    [byte(p[0]), byte(p[1]), byte(p[2]), 255]
                } else {
                    let a = p[3].clamp(0.0, 255.0);
                    let k = if a > 0.0 { 255.0 / a } else { 0.0 };
                    [byte(p[0] * k), byte(p[1] * k), byte(p[2] * k), byte(a)]
                }
            })
            .collect();
        Image {
            width: ow as u32,
            height: oh as u32,
            rgba,
            opaque: self.opaque,
        }
    }

    pub fn png(&self) -> Result<Vec<u8>> {
        let mut out = Vec::new();
        let mut encoder = png::Encoder::new(&mut out, self.width, self.height);
        encoder.set_color(if self.opaque { png::ColorType::Rgb } else { png::ColorType::Rgba });
        encoder.set_depth(png::BitDepth::Eight);
        encoder.set_compression(png::Compression::Fast);
        let mut writer = encoder.write_header()?;
        if self.opaque {
            let rgb: Vec<u8> = self.rgba.chunks_exact(4).flat_map(|p| [p[0], p[1], p[2]]).collect();
            writer.write_image_data(&rgb)?;
        } else {
            writer.write_image_data(&self.rgba)?;
        }
        writer.finish()?;
        Ok(out)
    }

    pub fn decode(bytes: &[u8]) -> Result<Image> {
        let mut decoder = png::Decoder::new(Cursor::new(bytes));
        decoder.set_transformations(png::Transformations::EXPAND | png::Transformations::STRIP_16);
        let mut reader = decoder.read_info()?;
        let mut buf = vec![0; reader.output_buffer_size().context("a PNG too large to hold")?];
        let info = reader.next_frame(&mut buf)?;
        buf.truncate(info.buffer_size());
        let rgba: Vec<u8> = match info.color_type {
            png::ColorType::Rgba => buf,
            png::ColorType::Rgb => buf.chunks_exact(3).flat_map(|p| [p[0], p[1], p[2], 255]).collect(),
            png::ColorType::GrayscaleAlpha => buf.chunks_exact(2).flat_map(|p| [p[0], p[0], p[0], p[1]]).collect(),
            png::ColorType::Grayscale => buf.iter().flat_map(|&g| [g, g, g, 255]).collect(),
            png::ColorType::Indexed => anyhow::bail!("an indexed PNG survived expansion"),
        };
        let opaque = rgba.chunks_exact(4).all(|p| p[3] == 255);
        Ok(Image {
            width: info.width,
            height: info.height,
            rgba,
            opaque,
        })
    }

    /// Two frames side by side, unresized and top-aligned, on the site navy with a
    /// one-pixel hairline in the three between them.
    pub fn twin(left: &Image, right: &Image) -> Image {
        let height = left.height.max(right.height);
        let width = left.width + TWIN_GAP + right.width;
        let mut rgba = Vec::with_capacity((width * height * 4) as usize);
        for _ in 0..width * height {
            rgba.extend_from_slice(&[TWIN_BG[0], TWIN_BG[1], TWIN_BG[2], 255]);
        }
        let mut out = Image {
            width,
            height,
            rgba,
            opaque: true,
        };
        out.over(left, 0);
        for y in 0..height {
            let at = ((y * width + left.width + 1) * 4) as usize;
            out.rgba[at..at + 3].copy_from_slice(&TWIN_HAIRLINE);
        }
        out.over(right, left.width + TWIN_GAP);
        out
    }

    /// Source-over at column `x0`, row 0.
    fn over(&mut self, src: &Image, x0: u32) {
        for y in 0..src.height.min(self.height) {
            for x in 0..src.width.min(self.width.saturating_sub(x0)) {
                let s = ((y * src.width + x) * 4) as usize;
                let d = ((y * self.width + x0 + x) * 4) as usize;
                let a = src.rgba[s + 3] as u32;
                for c in 0..3 {
                    let v = src.rgba[s + c] as u32 * a + self.rgba[d + c] as u32 * (255 - a);
                    self.rgba[d + c] = ((v + 127) / 255) as u8;
                }
            }
        }
    }
}

/// libvips `find_trim` over the `N` bands `at` gives each pixel: the box, inclusive, of every
/// pixel whose 3×3 median in some band stands `threshold` or more off `background`.
fn trim_box<const N: usize>(
    w: usize,
    h: usize,
    threshold: u8,
    background: [u8; N],
    at: impl Fn(usize) -> [u8; N],
) -> Option<(usize, usize, usize, usize)> {
    // A median of nine values none of which stands `threshold` off the background stands within
    // it too, so only a window holding a pixel that does is worth sorting; and the box is found
    // by walking in from each side, which stops at the first pixel it meets.
    let off: Vec<bool> = (0..w * h)
        .map(|i| {
            let p = at(i);
            (0..N).any(|b| p[b].abs_diff(background[b]) >= threshold)
        })
        .collect();
    let differs = |x: usize, y: usize| {
        let rows = [y.saturating_sub(1), y, (y + 1).min(h - 1)];
        let cols = [x.saturating_sub(1), x, (x + 1).min(w - 1)];
        if !rows.iter().any(|&r| cols.iter().any(|&c| off[r * w + c])) {
            return false;
        }
        (0..N).any(|b| {
            let mut window = [0u8; 9];
            for (k, (r, c)) in rows.iter().flat_map(|&r| cols.iter().map(move |&c| (r, c))).enumerate() {
                window[k] = at(r * w + c)[b];
            }
            window.sort_unstable();
            window[4].abs_diff(background[b]) >= threshold
        })
    };
    let y0 = (0..h).find(|&y| (0..w).any(|x| differs(x, y)))?;
    let y1 = (y0..h).rev().find(|&y| (0..w).any(|x| differs(x, y))).unwrap_or(y0);
    let x0 = (0..w).find(|&x| (y0..=y1).any(|y| differs(x, y))).unwrap_or(0);
    let x1 = (x0..w).rev().find(|&x| (y0..=y1).any(|y| differs(x, y))).unwrap_or(x0);
    Some((x0, y0, x1, y1))
}

fn lanczos3(x: f64) -> f64 {
    if x == 0.0 {
        1.0
    } else if x.abs() < 3.0 {
        let px = std::f64::consts::PI * x;
        3.0 * px.sin() * (px / 3.0).sin() / (px * px)
    } else {
        0.0
    }
}

/// The Lanczos-3 taps for each output position along a line `len` long brought to `out`: the
/// first input it reads, and the weights from there.
fn taps(len: usize, out: usize) -> Vec<(usize, Vec<f32>)> {
    let scale = len as f64 / out as f64;
    let support = 3.0 * scale.max(1.0);
    (0..out)
        .map(|i| {
            let center = (i as f64 + 0.5) * scale;
            let lo = ((center - support).floor().max(0.0)) as usize;
            let hi = ((center + support).ceil() as usize).min(len);
            let mut weights: Vec<f64> = (lo..hi)
                .map(|j| lanczos3((j as f64 + 0.5 - center) / scale.max(1.0)))
                .collect();
            let total: f64 = weights.iter().sum();
            if total != 0.0 {
                for v in &mut weights {
                    *v /= total;
                }
            }
            (lo, weights.into_iter().map(|v| v as f32).collect())
        })
        .collect()
}

/// Fill `dst` row by row, `width` values a row, a band of rows a thread.
fn by_rows(dst: &mut [f32], width: usize, fill: impl Fn(usize, &mut [f32]) + Sync) {
    let rows = dst.len() / width.max(1);
    let threads = std::thread::available_parallelism().map_or(1, |n| n.get()).clamp(1, 4);
    let band = rows.div_ceil(threads).max(1);
    std::thread::scope(|scope| {
        for (b, chunk) in dst.chunks_mut(band * width).enumerate() {
            let fill = &fill;
            scope.spawn(move || {
                for (r, row) in chunk.chunks_mut(width).enumerate() {
                    fill(b * band + r, row);
                }
            });
        }
    });
}

/// The bytes of a PNG file, or what is wrong with them.
pub fn read_png(path: &std::path::Path) -> Result<Image> {
    let bytes = std::fs::read(path).with_context(|| format!("no frame at {}", path.display()))?;
    Image::decode(&bytes).with_context(|| format!("decode {}", path.display()))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn solid(w: u32, h: u32, c: [u8; 4]) -> Image {
        Image {
            width: w,
            height: h,
            rgba: (0..w * h).flat_map(|_| c).collect(),
            opaque: c[3] == 255,
        }
    }

    #[test]
    fn trim_finds_the_subject_and_ignores_a_stray_pixel() {
        let mut img = solid(40, 30, [26, 26, 46, 255]);
        for y in 10..20 {
            for x in 5..15 {
                let at = ((y * 40 + x) * 4) as usize;
                img.rgba[at..at + 4].copy_from_slice(&[200, 100, 50, 255]);
            }
        }
        let at = ((2 * 40 + 35) * 4) as usize;
        img.rgba[at..at + 4].copy_from_slice(&[255, 255, 255, 255]);
        let t = img.trim([26, 26, 46], 10);
        assert_eq!((t.width, t.height), (10, 10));
    }

    #[test]
    fn a_clear_frame_trims_to_black_by_its_alpha() {
        let mut img = solid(40, 30, [0, 0, 0, 0]);
        for y in 4..12 {
            for x in 20..36 {
                let at = ((y * 40 + x) * 4) as usize;
                img.rgba[at..at + 4].copy_from_slice(&[3, 3, 4, 255]);
            }
        }
        let t = img.trim([0, 0, 0], 10);
        assert_eq!((t.width, t.height), (16, 8));
    }

    #[test]
    fn png_round_trips() {
        let img = solid(17, 9, [1, 2, 3, 255]);
        let back = Image::decode(&img.png().unwrap()).unwrap();
        assert_eq!((back.width, back.height), (17, 9));
        assert_eq!(back.rgba, img.rgba);
    }

    #[test]
    fn a_fit_keeps_a_flat_colour_flat() {
        let img = solid(3200, 1000, [90, 120, 150, 255]);
        let f = img.fit_inside(1600);
        assert_eq!((f.width, f.height), (1600, 500));
        assert!(f.rgba.chunks_exact(4).all(|p| p == [90, 120, 150, 255]));
    }

    #[test]
    fn twins_sit_side_by_side_on_the_navy() {
        let t = Image::twin(&solid(4, 2, [255, 0, 0, 255]), &solid(5, 3, [0, 255, 0, 255]));
        assert_eq!((t.width, t.height), (12, 3));
        let px = |x: u32, y: u32| &t.rgba[((y * 12 + x) * 4) as usize..][..3];
        assert_eq!(px(5, 0), TWIN_HAIRLINE);
        assert_eq!(px(4, 0), TWIN_BG);
        assert_eq!(px(0, 2), TWIN_BG);
        assert_eq!(px(7, 2), [0, 255, 0]);
    }
}
