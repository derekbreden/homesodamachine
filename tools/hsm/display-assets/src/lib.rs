//! Display artwork shares one lossless PNG reader, exact crop/resample and RGB565 conversion.
use anyhow::{Context, Result, bail, ensure};
use std::{
    f64::consts::PI,
    fs::File,
    io::BufReader,
    path::{Path, PathBuf},
};

pub const FACTORY_FLAVORS: usize = 4;
pub const ANIMATION_SOURCE: &str = "brand/display-animation.png";
pub const ANIMATION_FRAMES: usize = 16;
pub const ANIMATION_WIDTH: usize = 360;
pub const ANIMATION_HEIGHT: usize = 360;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Image {
    pub width: usize,
    pub height: usize,
    pub rgb: Vec<u8>,
}
impl Image {
    pub fn validate(&self) -> Result<()> {
        ensure!(
            self.width > 0 && self.height > 0,
            "image dimensions must be nonempty"
        );
        ensure!(
            self.width
                .checked_mul(self.height)
                .and_then(|n| n.checked_mul(3))
                == Some(self.rgb.len()),
            "RGB sample count does not match image dimensions"
        );
        Ok(())
    }
    pub fn png(&self) -> Result<Vec<u8>> {
        self.validate()?;
        let mut bytes = Vec::new();
        {
            let mut encoder =
                png::Encoder::new(&mut bytes, self.width.try_into()?, self.height.try_into()?);
            encoder.set_color(png::ColorType::Rgb);
            encoder.set_depth(png::BitDepth::Eight);
            encoder.write_header()?.write_image_data(&self.rgb)?;
        }
        Ok(bytes)
    }
    pub fn crop(&self, x: usize, y: usize, width: usize, height: usize) -> Result<Image> {
        self.validate()?;
        ensure!(
            width > 0
                && height > 0
                && x.checked_add(width).is_some_and(|r| r <= self.width)
                && y.checked_add(height).is_some_and(|r| r <= self.height),
            "crop exceeds image"
        );
        let mut rgb = Vec::with_capacity(width * height * 3);
        for row in y..y + height {
            rgb.extend_from_slice(
                &self.rgb[(row * self.width + x) * 3..(row * self.width + x + width) * 3],
            );
        }
        Ok(Image { width, height, rgb })
    }
    pub fn rgb565(&self) -> Result<Vec<u8>> {
        self.validate()?;
        pack_rgb565(&self.rgb)
    }
}

#[derive(Clone, Copy, Debug)]
pub enum Rendition {
    Anchor,
    Card,
    Tile,
}
impl Rendition {
    pub const ALL: [Self; 3] = [Self::Anchor, Self::Card, Self::Tile];
    pub fn name(self) -> &'static str {
        match self {
            Self::Anchor => "anchor",
            Self::Card => "card",
            Self::Tile => "tile",
        }
    }
    pub fn dimensions(self) -> (usize, usize) {
        match self {
            Self::Anchor => (172, 320),
            Self::Card => (129, 240),
            Self::Tile => (86, 160),
        }
    }
}
pub fn flavor_source(root: &Path, face: usize) -> Result<PathBuf> {
    ensure!(face < FACTORY_FLAVORS, "unknown factory flavor");
    Ok(root.join(format!("images/flavor_{}.png", face + 1)))
}
pub fn pack_rgb565(rgb: &[u8]) -> Result<Vec<u8>> {
    ensure!(rgb.len() % 3 == 0, "RGB channels must be interleaved");
    let mut bytes = Vec::with_capacity(rgb.len() / 3 * 2);
    for p in rgb.chunks_exact(3) {
        let word = ((u16::from(p[0]) & 0xf8) << 8)
            | ((u16::from(p[1]) & 0xfc) << 3)
            | (u16::from(p[2]) >> 3);
        bytes.extend_from_slice(&word.to_le_bytes());
    }
    Ok(bytes)
}
pub fn decode_rgb565(width: usize, height: usize, bytes: &[u8]) -> Result<Image> {
    ensure!(
        width.checked_mul(height).and_then(|n| n.checked_mul(2)) == Some(bytes.len()),
        "RGB565 pixel count does not match dimensions"
    );
    let mut rgb = Vec::with_capacity(width * height * 3);
    for word in bytes.chunks_exact(2) {
        let word = u16::from_le_bytes([word[0], word[1]]);
        rgb.extend([
            (((word >> 11) & 31) * 255 / 31) as u8,
            (((word >> 5) & 63) * 255 / 63) as u8,
            ((word & 31) * 255 / 31) as u8,
        ]);
    }
    let image = Image { width, height, rgb };
    image.validate()?;
    Ok(image)
}
pub fn rendition(image: &Image, size: Rendition) -> Result<Vec<u8>> {
    image.validate()?;
    let (w, h) = size.dimensions();
    pack_rgb565(&fit(image, w, h))
}
pub fn factory_rendition(root: &Path, face: usize, size: Rendition) -> Result<Vec<u8>> {
    rendition(&read_png(&flavor_source(root, face)?)?, size)
}
pub fn factory_bundle(root: &Path, face: usize) -> Result<Vec<u8>> {
    let image = read_png(&flavor_source(root, face)?)?;
    let mut bytes = Vec::new();
    for size in Rendition::ALL {
        bytes.extend(rendition(&image, size)?);
    }
    Ok(bytes)
}
pub fn animation_frames(root: &Path) -> Result<Vec<Vec<u8>>> {
    let image = read_png(&root.join(ANIMATION_SOURCE))?;
    ensure!(
        image.width == ANIMATION_WIDTH * ANIMATION_FRAMES && image.height == ANIMATION_HEIGHT,
        "display animation master dimensions"
    );
    (0..ANIMATION_FRAMES)
        .map(|frame| {
            image
                .crop(
                    frame * ANIMATION_WIDTH,
                    0,
                    ANIMATION_WIDTH,
                    ANIMATION_HEIGHT,
                )?
                .rgb565()
        })
        .collect()
}

pub fn read_png(path: &Path) -> Result<Image> {
    let mut decoder = png::Decoder::new(BufReader::new(File::open(path)?));
    decoder.set_transformations(png::Transformations::EXPAND | png::Transformations::STRIP_16);
    let mut reader = decoder.read_info()?;
    let mut bytes = vec![
        0;
        reader
            .output_buffer_size()
            .context("PNG image is too large")?
    ];
    let info = reader.next_frame(&mut bytes)?;
    let input = &bytes[..info.buffer_size()];
    let mut rgb = Vec::with_capacity(info.width as usize * info.height as usize * 3);
    match info.color_type {
        png::ColorType::Rgb => rgb.extend_from_slice(input),
        png::ColorType::Rgba => {
            for pixel in input.chunks_exact(4) {
                rgb.extend_from_slice(&pixel[..3]);
            }
        }
        png::ColorType::Grayscale => {
            for value in input {
                rgb.extend_from_slice(&[*value; 3]);
            }
        }
        png::ColorType::GrayscaleAlpha => {
            for pixel in input.chunks_exact(2) {
                rgb.extend_from_slice(&[pixel[0]; 3]);
            }
        }
        _ => bail!("unsupported decoded PNG color type {:?}", info.color_type),
    }
    Ok(Image {
        width: info.width as usize,
        height: info.height as usize,
        rgb,
    })
}

fn sinc(value: f64) -> f64 {
    if value == 0.0 {
        1.0
    } else {
        let radians = value * PI;
        radians.sin() / radians
    }
}

struct Weights {
    first: usize,
    coefficients: Vec<i32>,
}

fn weights(length: usize, low: f32, high: f32, target: usize) -> Vec<Weights> {
    let scale = f64::from(high - low) / target as f64;
    let stretch = scale.max(1.0);
    let support = 3.0 * stretch;
    (0..target)
        .map(|index| {
            let center = f64::from(low) + (index as f64 + 0.5) * scale;
            let first = ((center - support + 0.5) as isize).max(0) as usize;
            let last = ((center + support + 0.5) as usize).min(length);
            let raw = (first..last)
                .map(|sample| {
                    let position = (sample as f64 - center + 0.5) / stretch;
                    if (-3.0..3.0).contains(&position) {
                        sinc(position) * sinc(position / 3.0)
                    } else {
                        0.0
                    }
                })
                .collect::<Vec<_>>();
            let total = raw.iter().sum::<f64>();
            let coefficients = raw
                .into_iter()
                .map(|v| (v / total * f64::from(1 << 22)).round() as i32)
                .collect();
            Weights {
                first,
                coefficients,
            }
        })
        .collect()
}

fn horizontal(image: &Image, weights: &[Weights]) -> Image {
    let width = weights.len();
    let mut rgb = vec![0; width * image.height * 3];
    for row in 0..image.height {
        for (column, filter) in weights.iter().enumerate() {
            for channel in 0..3 {
                let sum = filter.coefficients.iter().enumerate().fold(
                    1i64 << 21,
                    |sum, (offset, weight)| {
                        sum + i64::from(
                            image.rgb[(row * image.width + filter.first + offset) * 3 + channel],
                        ) * i64::from(*weight)
                    },
                );
                rgb[(row * width + column) * 3 + channel] = (sum >> 22).clamp(0, 255) as u8;
            }
        }
    }
    Image {
        width,
        height: image.height,
        rgb,
    }
}

fn vertical(image: &Image, weights: &[Weights]) -> Image {
    let height = weights.len();
    let mut rgb = vec![0; image.width * height * 3];
    for (row, filter) in weights.iter().enumerate() {
        for column in 0..image.width {
            for channel in 0..3 {
                let sum = filter.coefficients.iter().enumerate().fold(
                    1i64 << 21,
                    |sum, (offset, weight)| {
                        sum + i64::from(
                            image.rgb
                                [((filter.first + offset) * image.width + column) * 3 + channel],
                        ) * i64::from(*weight)
                    },
                );
                rgb[(row * image.width + column) * 3 + channel] = (sum >> 22).clamp(0, 255) as u8;
            }
        }
    }
    Image {
        width: image.width,
        height,
        rgb,
    }
}

pub fn fit(image: &Image, width: usize, height: usize) -> Vec<u8> {
    let ratio = width as f64 / height as f64;
    let (crop_width, crop_height) = if image.width as f64 / image.height as f64 >= ratio {
        (ratio * image.height as f64, image.height as f64)
    } else {
        (image.width as f64, image.width as f64 / ratio)
    };
    let x = (image.width as f64 - crop_width) / 2.0;
    let y = (image.height as f64 - crop_height) / 2.0;
    let columns = weights(image.width, x as f32, (x + crop_width) as f32, width);
    let rows = weights(image.height, y as f32, (y + crop_height) as f32, height);
    let need_horizontal = image.width != width || x != 0.0 || x + crop_width != width as f64;
    let need_vertical = image.height != height || y != 0.0 || y + crop_height != height as f64;
    let vertical_first = image.height as isize - height as isize > 0
        && image.height as isize - height as isize > (image.width as isize - width as isize) * 2;
    match (need_horizontal, need_vertical, vertical_first) {
        (true, true, true) => horizontal(&vertical(image, &rows), &columns).rgb,
        (true, true, false) => vertical(&horizontal(image, &columns), &rows).rgb,
        (true, false, _) => horizontal(image, &columns).rgb,
        (false, true, _) => vertical(image, &rows).rgb,
        (false, false, _) => image.rgb.clone(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn every_display_word_roundtrips_through_lossless_rgb() {
        let words: Vec<u8> = (0..=u16::MAX).flat_map(u16::to_le_bytes).collect();
        assert_eq!(
            decode_rgb565(256, 256, &words).unwrap().rgb565().unwrap(),
            words
        );
        assert!(decode_rgb565(2, 1, &words[..2]).is_err());
    }
    #[test]
    fn crop_keeps_row_order_and_fitting_keeps_matching_pixels() {
        let image = Image {
            width: 2,
            height: 2,
            rgb: vec![255, 0, 0, 0, 255, 0, 0, 0, 255, 255, 255, 255],
        };
        assert_eq!(
            image.crop(1, 0, 1, 2).unwrap().rgb,
            vec![0, 255, 0, 255, 255, 255]
        );
        assert_eq!(fit(&image, 2, 2), image.rgb);
        assert!(image.crop(2, 0, 1, 1).is_err());
    }
}
