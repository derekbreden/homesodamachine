//! Flavor headers contain the center-cropped logo pixels the display firmware compiles.
use crate::{option, validate_args, write};
use anyhow::{Context, Result, bail, ensure};
use std::{
    f64::consts::PI,
    fmt::Write as _,
    fs::File,
    io::BufReader,
    path::{Path, PathBuf},
};

pub(crate) struct Image {
    pub(crate) width: usize,
    pub(crate) height: usize,
    pub(crate) rgb: Vec<u8>,
}

pub fn run(root: &Path, args: &[String]) -> Result<()> {
    ensure!(
        validate_args(args, &[], &["--out-root"])?.is_empty(),
        "png-to-rgb565 [--out-root DIRECTORY]"
    );
    let destination = option(args, "--out-root")?
        .map(PathBuf::from)
        .unwrap_or_else(|| root.to_owned());
    for index in 0..4 {
        let filename = format!("flavor_{}.png", index + 1);
        let source = root.join("images").join(&filename);
        if !source.is_file() {
            println!("SKIP {filename} (missing)");
            continue;
        }
        let image = read(&source)?;
        for (suffix, width, height, tree) in [
            ("anchor", 172, 320, "src_front"),
            ("card", 129, 240, "src_front"),
            ("tile", 86, 160, "src_front"),
            ("faucet", 172, 320, "src_faucet"),
        ] {
            let variable = format!("flavor{index}_{suffix}");
            let rgb = fit(&image, width, height);
            let text = header(
                &filename,
                &format!("flavor_{}", index + 1),
                &variable,
                width,
                height,
                &rgb,
            )?;
            let path = destination
                .join("firmware")
                .join(tree)
                .join("images")
                .join(format!("{variable}.h"));
            write(&path, text.as_bytes())?;
            println!("{} ({} bytes)", path.display(), text.len());
        }
    }
    Ok(())
}

pub(crate) fn read(path: &Path) -> Result<Image> {
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

fn header(
    source: &str,
    label: &str,
    variable: &str,
    width: usize,
    height: usize,
    rgb: &[u8],
) -> Result<String> {
    let mut text = format!(
        "// {label} - {width}x{height} RGB565 bitmap\n// Auto-generated from {source} by hsm-peripheral png-to-rgb565\n#pragma once\n\n#include <Arduino.h>\n\nconst uint16_t {variable}[{width} * {height}] PROGMEM = {{\n"
    );
    for row in rgb.chunks(16 * 3) {
        text.push_str("    ");
        for (index, pixel) in row.chunks_exact(3).enumerate() {
            if index != 0 {
                text.push_str(", ");
            }
            let value = ((u16::from(pixel[0]) & 0xf8) << 8)
                | ((u16::from(pixel[1]) & 0xfc) << 3)
                | (u16::from(pixel[2]) >> 3);
            write!(text, "0x{value:04X}")?;
        }
        text.push_str(",\n");
    }
    text.push_str("};\n");
    Ok(text)
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

fn fit(image: &Image, width: usize, height: usize) -> Vec<u8> {
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
