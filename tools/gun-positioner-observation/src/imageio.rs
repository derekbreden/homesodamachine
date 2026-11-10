//! Saved frames preserve their sample depth, channel order and camera JPEG tables.
use crate::capture::Codec;
use anyhow::{Context, Result, bail, ensure};
use serde::{Deserialize, Serialize};
use std::{fs, io::Cursor, path::Path};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Depth {
    U8,
    U16,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Image {
    pub width: usize,
    pub height: usize,
    pub channels: usize,
    pub depth: Depth,
    pub pixels: Vec<u16>,
}

impl Image {
    pub fn gray8(width: usize, height: usize, pixels: Vec<u8>) -> Result<Self> {
        let image = Self {
            width,
            height,
            channels: 1,
            depth: Depth::U8,
            pixels: pixels.into_iter().map(u16::from).collect(),
        };
        image.validate()?;
        Ok(image)
    }

    pub fn validate(&self) -> Result<()> {
        ensure!(self.channels > 0, "an image needs a channel");
        let count = self
            .width
            .checked_mul(self.height)
            .and_then(|n| n.checked_mul(self.channels))
            .context("image dimensions overflow")?;
        ensure!(
            self.pixels.len() == count,
            "image sample count does not match its dimensions"
        );
        ensure!(
            self.depth != Depth::U8 || self.pixels.iter().all(|&p| p <= 255),
            "a byte image contains a sample outside its range"
        );
        Ok(())
    }
}

#[derive(Clone, Copy, Debug)]
pub struct JpegSegment<'a> {
    pub marker: u8,
    pub offset: usize,
    pub payload: &'a [u8],
}

fn scan_jpeg<'a>(
    data: &'a [u8],
    mut visit: impl FnMut(JpegSegment<'a>) -> Result<bool>,
) -> Result<()> {
    ensure!(
        data.len() >= 4 && data[..2] == [0xff, 0xd8],
        "JPEG is missing SOI"
    );
    let mut i = 2;
    while i < data.len() {
        ensure!(data[i] == 0xff, "expected a JPEG marker at byte {i}");
        while i < data.len() && data[i] == 0xff {
            i += 1;
        }
        if i == data.len() {
            break;
        }
        let marker = data[i];
        i += 1;
        if marker == 0xd8 || marker == 0x01 || (0xd0..=0xd7).contains(&marker) {
            continue;
        }
        if marker == 0xd9 {
            break;
        }
        ensure!(i + 2 <= data.len(), "truncated JPEG segment length");
        let length = u16::from_be_bytes([data[i], data[i + 1]]) as usize;
        ensure!(
            length >= 2 && length <= data.len() - i,
            "JPEG segment exceeds the frame"
        );
        let segment = JpegSegment {
            marker,
            offset: i - 2,
            payload: &data[i + 2..i + length],
        };
        if !visit(segment)? || marker == 0xda {
            break;
        }
        i += length;
    }
    Ok(())
}

pub fn jpeg_segments(data: &[u8]) -> Result<Vec<JpegSegment<'_>>> {
    let mut out = Vec::new();
    scan_jpeg(data, |segment| {
        out.push(segment);
        Ok(true)
    })?;
    Ok(out)
}

pub fn jpeg_dimensions(data: &[u8]) -> Result<(usize, usize)> {
    let mut dimensions = None;
    scan_jpeg(data, |segment| {
        if matches!(
            segment.marker,
            0xc0 | 0xc1
                | 0xc2
                | 0xc3
                | 0xc5
                | 0xc6
                | 0xc7
                | 0xc9
                | 0xca
                | 0xcb
                | 0xcd
                | 0xce
                | 0xcf
        ) {
            ensure!(segment.payload.len() >= 5, "short JPEG SOF segment");
            dimensions = Some((
                u16::from_be_bytes([segment.payload[3], segment.payload[4]]) as usize,
                u16::from_be_bytes([segment.payload[1], segment.payload[2]]) as usize,
            ));
            return Ok(false);
        }
        Ok(true)
    })?;
    dimensions.context("JPEG has no SOF before scan data")
}

pub fn has_huffman_tables(data: &[u8]) -> Result<bool> {
    let mut found = false;
    scan_jpeg(data, |segment| {
        found = segment.marker == 0xc4;
        Ok(!found)
    })?;
    Ok(found)
}

fn standard_huffman_tables() -> Vec<u8> {
    let dc_lum = [0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0];
    let dc_chr = [0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0];
    let ac_lum = [0, 2, 1, 3, 3, 2, 4, 3, 5, 5, 4, 4, 0, 0, 1, 0x7d];
    let ac_chr = [0, 2, 1, 2, 4, 4, 3, 4, 7, 5, 4, 4, 0, 1, 2, 0x77];
    let ac_lum_values = concat!(
        "0102030004110512",
        "2131410613516107",
        "227114328191a108",
        "2342b1c11552d1f0",
        "2433627282090a16",
        "1718191a25262728",
        "292a343536373839",
        "3a43444546474849",
        "4a53545556575859",
        "5a63646566676869",
        "6a73747576777879",
        "7a83848586878889",
        "8a92939495969798",
        "999aa2a3a4a5a6a7",
        "a8a9aab2b3b4b5b6",
        "b7b8b9bac2c3c4c5",
        "c6c7c8c9cad2d3d4",
        "d5d6d7d8d9dae1e2",
        "e3e4e5e6e7e8e9ea",
        "f1f2f3f4f5f6f7f8",
        "f9fa"
    );
    let ac_chr_values = concat!(
        "0001020311040521",
        "3106124151076171",
        "1322328108144291",
        "a1b1c109233352f0",
        "156272d10a162434",
        "e125f11718191a26",
        "2728292a35363738",
        "393a434445464748",
        "494a535455565758",
        "595a636465666768",
        "696a737475767778",
        "797a828384858687",
        "88898a9293949596",
        "9798999aa2a3a4a5",
        "a6a7a8a9aab2b3b4",
        "b5b6b7b8b9bac2c3",
        "c4c5c6c7c8c9cad2",
        "d3d4d5d6d7d8d9da",
        "e2e3e4e5e6e7e8e9",
        "eaf2f3f4f5f6f7f8",
        "f9fa"
    );
    let dc_values: Vec<u8> = (0..12).collect();
    let hex = |s: &str| -> Vec<u8> {
        s.as_bytes()
            .chunks_exact(2)
            .map(|p| {
                let n = |v: u8| if v <= b'9' { v - b'0' } else { v - b'a' + 10 };
                (n(p[0]) << 4) | n(p[1])
            })
            .collect()
    };
    let mut payload = Vec::new();
    for (id, bits, values) in [
        (0, dc_lum, dc_values.clone()),
        (0x10, ac_lum, hex(ac_lum_values)),
        (1, dc_chr, dc_values),
        (0x11, ac_chr, hex(ac_chr_values)),
    ] {
        payload.push(id);
        payload.extend_from_slice(&bits);
        payload.extend_from_slice(&values);
    }
    let mut segment = vec![0xff, 0xc4];
    segment.extend_from_slice(&((payload.len() + 2) as u16).to_be_bytes());
    segment.extend_from_slice(&payload);
    segment
}

pub fn with_standard_huffman_tables(data: &[u8]) -> Result<Vec<u8>> {
    if has_huffman_tables(data)? {
        return Ok(data.to_vec());
    }
    let mut sos = None;
    for segment in jpeg_segments(data)? {
        if segment.marker == 0xda {
            sos = Some(segment.offset);
        }
    }
    let offset = sos.context("JPEG has no scan segment")?;
    let mut out = data[..offset].to_vec();
    out.extend_from_slice(&standard_huffman_tables());
    out.extend_from_slice(&data[offset..]);
    Ok(out)
}

pub fn decode_jpeg(data: &[u8], gray: bool) -> Result<Image> {
    let bytes = with_standard_huffman_tables(data)?;
    let mut decoder = jpeg_decoder::Decoder::new(Cursor::new(bytes));
    let raw = decoder.decode().context("decode camera JPEG")?;
    let info = decoder
        .info()
        .context("JPEG dimensions absent after decoding")?;
    let mut pixels = Vec::new();
    let depth = match info.pixel_format {
        jpeg_decoder::PixelFormat::L8 => {
            if gray {
                pixels.extend(raw.iter().map(|&p| p as u16));
            } else {
                for &p in &raw {
                    pixels.extend([p as u16; 3]);
                }
            }
            Depth::U8
        }
        jpeg_decoder::PixelFormat::L16 => {
            for p in raw.chunks_exact(2) {
                let v = u16::from_ne_bytes([p[0], p[1]]);
                if gray {
                    pixels.push(v);
                } else {
                    pixels.extend([v; 3]);
                }
            }
            Depth::U16
        }
        jpeg_decoder::PixelFormat::RGB24 => {
            for p in raw.chunks_exact(3) {
                if gray {
                    pixels.push(
                        ((p[0] as u32 * 19595 + p[1] as u32 * 38470 + p[2] as u32 * 7471 + 32768)
                            >> 16) as u16,
                    );
                } else {
                    pixels.extend(p.iter().map(|&p| p as u16));
                }
            }
            Depth::U8
        }
        jpeg_decoder::PixelFormat::CMYK32 => {
            for p in raw.chunks_exact(4) {
                let rgb = [0, 1, 2]
                    .map(|i| (((255 - p[i] as u32) * (255 - p[3] as u32) + 127) / 255) as u16);
                if gray {
                    pixels.push(
                        ((rgb[0] as u32 * 19595
                            + rgb[1] as u32 * 38470
                            + rgb[2] as u32 * 7471
                            + 32768)
                            >> 16) as u16,
                    );
                } else {
                    pixels.extend(rgb);
                }
            }
            Depth::U8
        }
    };
    let image = Image {
        width: info.width as usize,
        height: info.height as usize,
        channels: if gray { 1 } else { 3 },
        depth,
        pixels,
    };
    image.validate()?;
    Ok(image)
}

pub fn encode_pgm(image: &Image) -> Result<Vec<u8>> {
    image.validate()?;
    ensure!(image.channels == 1, "PGM holds one channel");
    let max = if image.depth == Depth::U8 { 255 } else { 65535 };
    let mut bytes = format!("P5\n{} {}\n{max}\n", image.width, image.height).into_bytes();
    for &p in &image.pixels {
        if image.depth == Depth::U8 {
            bytes.push(p as u8);
        } else {
            bytes.extend_from_slice(&p.to_be_bytes());
        }
    }
    Ok(bytes)
}

pub fn decode_pgm(data: &[u8]) -> Result<Image> {
    let mut at = 0;
    let mut tokens = Vec::new();
    while tokens.len() < 4 {
        while at < data.len() && data[at].is_ascii_whitespace() {
            at += 1;
        }
        if at < data.len() && data[at] == b'#' {
            while at < data.len() && data[at] != b'\n' {
                at += 1;
            }
            continue;
        }
        let start = at;
        while at < data.len() && !data[at].is_ascii_whitespace() {
            at += 1;
        }
        ensure!(at > start && at < data.len(), "truncated PGM header");
        tokens.push(&data[start..at]);
    }
    at += 1;
    ensure!(tokens[0] == b"P5", "only binary PGM frames are read");
    let integer = |p| -> Result<usize> { Ok(std::str::from_utf8(p)?.parse()?) };
    let width = integer(tokens[1])?;
    let height = integer(tokens[2])?;
    let max = integer(tokens[3])?;
    let depth = if max < 256 { Depth::U8 } else { Depth::U16 };
    let count = width
        .checked_mul(height)
        .context("PGM dimensions overflow")?;
    let length = count
        .checked_mul(if depth == Depth::U8 { 1 } else { 2 })
        .context("PGM size overflows")?;
    ensure!(length <= data.len() - at, "truncated PGM samples");
    let body = &data[at..at + length];
    let pixels = if depth == Depth::U8 {
        body.iter().map(|&p| p as u16).collect()
    } else {
        body.chunks_exact(2)
            .map(|p| u16::from_be_bytes([p[0], p[1]]))
            .collect()
    };
    Ok(Image {
        width,
        height,
        channels: 1,
        depth,
        pixels,
    })
}

pub fn encode_png(image: &Image) -> Result<Vec<u8>> {
    image.validate()?;
    let color = match image.channels {
        1 => png::ColorType::Grayscale,
        2 => png::ColorType::GrayscaleAlpha,
        3 => png::ColorType::Rgb,
        4 => png::ColorType::Rgba,
        _ => bail!("PNG needs gray, gray-alpha, RGB or RGBA samples"),
    };
    let width = u32::try_from(image.width)?;
    let height = u32::try_from(image.height)?;
    let mut output = Vec::new();
    {
        let mut encoder = png::Encoder::new(&mut output, width, height);
        encoder.set_color(color);
        encoder.set_depth(if image.depth == Depth::U8 {
            png::BitDepth::Eight
        } else {
            png::BitDepth::Sixteen
        });
        encoder.set_compression(png::Compression::Fast);
        let mut writer = encoder.write_header()?;
        let mut raw = Vec::new();
        for &p in &image.pixels {
            if image.depth == Depth::U8 {
                raw.push(p as u8);
            } else {
                raw.extend_from_slice(&p.to_be_bytes());
            }
        }
        writer.write_image_data(&raw)?;
    }
    Ok(output)
}

pub fn decode_png(data: &[u8]) -> Result<Image> {
    let decoder = png::Decoder::new(Cursor::new(data));
    let mut reader = decoder.read_info()?;
    let mut bytes = vec![
        0;
        reader
            .output_buffer_size()
            .context("PNG image is too large")?
    ];
    let info = reader.next_frame(&mut bytes)?;
    let bytes = &bytes[..info.buffer_size()];
    let width = info.width as usize;
    let height = info.height as usize;
    let channels = match info.color_type {
        png::ColorType::Grayscale | png::ColorType::Indexed => 1,
        png::ColorType::GrayscaleAlpha => 2,
        png::ColorType::Rgb => 3,
        png::ColorType::Rgba => 4,
    };
    let bits = info.bit_depth as usize;
    let pixels = if bits == 16 {
        bytes
            .chunks_exact(2)
            .map(|p| u16::from_be_bytes([p[0], p[1]]))
            .collect()
    } else if bits == 8 {
        bytes.iter().map(|&p| p as u16).collect()
    } else {
        let mask = (1u8 << bits) - 1;
        let row_bytes = (width * channels * bits).div_ceil(8);
        let mut pixels = Vec::with_capacity(width * height * channels);
        for row in bytes.chunks_exact(row_bytes) {
            for i in 0..width * channels {
                let shift = 8 - bits - (i * bits) % 8;
                let mut value = ((row[i * bits / 8] >> shift) & mask) as u16;
                if info.color_type == png::ColorType::Grayscale && bits != 1 {
                    value = value * 255 / mask as u16;
                }
                pixels.push(value);
            }
        }
        pixels
    };
    let image = Image {
        width,
        height,
        channels,
        depth: if bits == 16 { Depth::U16 } else { Depth::U8 },
        pixels,
    };
    image.validate()?;
    Ok(image)
}

pub fn nv12_to_rgb(
    width: usize,
    height: usize,
    y: &[u8],
    uv: &[u8],
    video_range: bool,
) -> Result<Image> {
    ensure!(
        width > 0 && width % 2 == 0 && height > 0,
        "NV12 needs a nonempty luma plane and paired chroma columns"
    );
    let size = width
        .checked_mul(height)
        .context("NV12 dimensions overflow")?;
    ensure!(
        y.len() >= size && uv.len() >= width * height.div_ceil(2),
        "truncated NV12 planes"
    );
    let mut pixels = Vec::with_capacity(size * 3);
    for row in 0..height {
        for col in 0..width {
            let at = (row / 2) * width + (col / 2) * 2;
            let mut luma = y[row * width + col] as f64;
            let mut cb = uv[at] as f64 - 128.;
            let mut cr = uv[at + 1] as f64 - 128.;
            if video_range {
                luma = (luma - 16.) * 255. / 219.;
                cb = cb * 255. / 224.;
                cr = cr * 255. / 224.;
            }
            for v in [
                luma + 1.5748 * cr,
                luma - 0.1873 * cb - 0.4681 * cr,
                luma + 1.8556 * cb,
            ] {
                pixels.push(v.round_ties_even().clamp(0., 255.) as u16);
            }
        }
    }
    Ok(Image {
        width,
        height,
        channels: 3,
        depth: Depth::U8,
        pixels,
    })
}

pub fn load_frame(
    path: &Path,
    codec: &Codec,
    height: Option<usize>,
    video_range: bool,
) -> Result<Image> {
    let data = fs::read(path).with_context(|| format!("read saved frame {}", path.display()))?;
    if *codec == Codec::Jpeg {
        return decode_jpeg(&data, true);
    }
    let raw = if path.extension().is_some_and(|p| p == "png") {
        decode_png(&data)?
    } else {
        decode_pgm(&data)?
    };
    match codec {
        Codec::Gray8 | Codec::Gray16 => Ok(raw),
        Codec::Nv12 => {
            ensure!(
                raw.channels == 1 && raw.pixels.iter().all(|&p| p <= 255),
                "NV12 storage needs byte luma and chroma samples"
            );
            let height = height.unwrap_or(raw.height * 2 / 3);
            let split = height
                .checked_mul(raw.width)
                .context("NV12 dimensions overflow")?;
            ensure!(
                split <= raw.pixels.len(),
                "NV12 height exceeds stored frame"
            );
            let bytes: Vec<u8> = raw.pixels.into_iter().map(|p| p as u8).collect();
            nv12_to_rgb(
                raw.width,
                height,
                &bytes[..split],
                &bytes[split..],
                video_range,
            )
        }
        _ => bail!("no saved-frame reader for codec {codec:?}"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pgm_preserves_depth_byte_order_and_header_boundary() {
        for image in [
            Image::gray8(4, 1, vec![10, 32, 35, 255]).unwrap(),
            Image {
                width: 4,
                height: 1,
                channels: 1,
                depth: Depth::U16,
                pixels: vec![0, 256, 32768, 65535],
            },
        ] {
            assert_eq!(decode_pgm(&encode_pgm(&image).unwrap()).unwrap(), image);
        }
        assert_eq!(
            decode_pgm(b"P5\n# frame\n2 1\n255\n\n ").unwrap().pixels,
            vec![10, 32]
        );
        assert!(decode_pgm(b"P5\n2 2\n255\n\x00").is_err());
        assert!(decode_pgm(b"P5 # incomplete").is_err());
    }

    #[test]
    fn png_preserves_interleaved_channels_and_gray_sample_range() {
        for image in [
            Image {
                width: 2,
                height: 1,
                channels: 1,
                depth: Depth::U16,
                pixels: vec![256, 65000],
            },
            Image {
                width: 2,
                height: 1,
                channels: 3,
                depth: Depth::U8,
                pixels: vec![255, 0, 1, 2, 100, 200],
            },
            Image {
                width: 1,
                height: 1,
                channels: 4,
                depth: Depth::U8,
                pixels: vec![1, 2, 3, 4],
            },
        ] {
            assert_eq!(decode_png(&encode_png(&image).unwrap()).unwrap(), image);
        }
    }

    #[test]
    fn png_subbyte_samples_keep_palette_indices_and_grayscale_values() {
        let encode = |color, depth, samples: &[u8]| {
            let mut data = Vec::new();
            {
                let mut encoder = png::Encoder::new(&mut data, 4, 1);
                encoder.set_color(color);
                encoder.set_depth(depth);
                if color == png::ColorType::Indexed {
                    encoder.set_palette(vec![255, 0, 0, 0, 255, 0, 0, 0, 255, 255, 255, 255]);
                }
                let mut writer = encoder.write_header().unwrap();
                writer.write_image_data(samples).unwrap();
            }
            data
        };
        assert_eq!(
            decode_png(&encode(
                png::ColorType::Grayscale,
                png::BitDepth::Two,
                &[0b00011011]
            ))
            .unwrap()
            .pixels,
            [0, 85, 170, 255]
        );
        assert_eq!(
            decode_png(&encode(
                png::ColorType::Grayscale,
                png::BitDepth::One,
                &[0b01010000]
            ))
            .unwrap()
            .pixels,
            [0, 1, 0, 1]
        );
        assert_eq!(
            decode_png(&encode(
                png::ColorType::Indexed,
                png::BitDepth::Two,
                &[0b00011011]
            ))
            .unwrap()
            .pixels,
            [0, 1, 2, 3]
        );
    }

    #[test]
    #[ignore = "on-demand saved JPEG comparison; set PGFUN_SAVED_CODEC_BASELINE"]
    fn saved_jpeg_baseline() {
        let root = std::path::PathBuf::from(
            std::env::var_os("PGFUN_SAVED_CODEC_BASELINE").expect("saved JPEG baseline directory"),
        );
        let mut results = Vec::new();
        for kind in ["rgb", "gray", "cmyk"] {
            let full = fs::read(root.join(format!("{kind}.jpg"))).unwrap();
            let stripped = fs::read(root.join(format!("{kind}-stripped.jpg"))).unwrap();
            assert!(has_huffman_tables(&full).unwrap());
            assert!(!has_huffman_tables(&stripped).unwrap());
            for gray in [false, true] {
                let native = decode_jpeg(&full, gray).unwrap();
                assert_eq!(decode_jpeg(&stripped, gray).unwrap(), native);
                let expected = if gray {
                    decode_pgm(&fs::read(root.join(format!("{kind}-gray.pgm"))).unwrap()).unwrap()
                } else {
                    decode_png(&fs::read(root.join(format!("{kind}-rgb.png"))).unwrap()).unwrap()
                };
                assert_eq!(
                    (native.width, native.height, native.channels, native.depth),
                    (
                        expected.width,
                        expected.height,
                        expected.channels,
                        expected.depth
                    )
                );
                let error: Vec<_> = native
                    .pixels
                    .iter()
                    .zip(&expected.pixels)
                    .map(|(&a, &b)| a.abs_diff(b) as f64)
                    .collect();
                let maximum = error.iter().copied().fold(0., f64::max);
                let mean = error.iter().sum::<f64>() / error.len() as f64;
                println!("{kind} gray={gray}: Pillow sample difference max={maximum}, mean={mean}");
                fs::write(
                    root.join(format!("native-{kind}-{gray}.png")),
                    encode_png(&native).unwrap(),
                )
                .unwrap();
                results.push(serde_json::json!({
                    "kind":kind,"gray":gray,"maximum_sample_difference":maximum,"mean_sample_difference":mean,
                    "samples":error.len(),"changed_samples":error.iter().filter(|&&e|e>0.).count(),
                    "full_and_missing_dht_identical":true,
                }));
            }
        }
        fs::write(
            root.join("native-jpeg-report.json"),
            serde_json::to_vec_pretty(&results).unwrap(),
        )
        .unwrap();
        // Independent inverse-transform and chroma-conversion rounding is retained.
        assert!(
            results.iter().all(|r| {
                let limit = if r["gray"].as_bool().unwrap() { 1. } else { 3. };
                r["maximum_sample_difference"].as_f64().unwrap() <= limit
                    && r["mean_sample_difference"].as_f64().unwrap() < 0.1
            }),
            "JPEG sample comparison: {results:?}"
        );
    }

    #[test]
    fn jpeg_headers_and_missing_tables_are_checked_without_pixel_decode() {
        let data = [
            0xff, 0xd8, 0xff, 0xc0, 0, 7, 8, 0, 48, 0, 64, 0xff, 0xda, 0, 2, 0xff, 0xd9,
        ];
        assert_eq!(jpeg_dimensions(&data).unwrap(), (64, 48));
        assert!(!has_huffman_tables(&data).unwrap());
        let restored = with_standard_huffman_tables(&data).unwrap();
        assert!(has_huffman_tables(&restored).unwrap());
        assert_eq!(with_standard_huffman_tables(&restored).unwrap(), restored);
        assert_eq!(jpeg_dimensions(&restored).unwrap(), (64, 48));
        let mut header = data[..11].to_vec();
        header.extend_from_slice(&[0xff, 0xda, 0]);
        assert_eq!(jpeg_dimensions(&header).unwrap(), (64, 48));
        assert!(jpeg_segments(&header).is_err());
        assert!(jpeg_segments(&[0xff, 0xd8, 0xff, 0xc0, 0]).is_err());
        assert!(with_standard_huffman_tables(&[0xff, 0xd8, 0xff, 0xd9]).is_err());
    }

    #[test]
    fn nv12_applies_declared_range_and_chroma_order() {
        let rgb = nv12_to_rgb(
            6,
            4,
            &[126; 24],
            &[90, 240, 90, 240, 90, 240, 90, 240, 90, 240, 90, 240],
            true,
        )
        .unwrap();
        assert!(rgb.pixels.chunks_exact(3).all(|p| p[0] > 200 && p[2] < 100));
        assert!(
            nv12_to_rgb(2, 2, &[235; 4], &[128, 128], true)
                .unwrap()
                .pixels
                .iter()
                .all(|&p| p == 255)
        );
        assert!(
            nv12_to_rgb(2, 2, &[235; 4], &[128, 128], false)
                .unwrap()
                .pixels
                .iter()
                .all(|&p| p == 235)
        );
        assert!(nv12_to_rgb(2, 2, &[235; 3], &[128, 128], true).is_err());
    }
}
