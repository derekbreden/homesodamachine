//! Panel camera analysis maps the captured display onto its pixel grid and reads its test patterns.
use crate::{
    option,
    rgb565::{self, Image},
    validate_args,
};
use anyhow::{Context, Result, bail, ensure};
use std::{
    collections::{BTreeMap, VecDeque},
    f64::consts::PI,
    fs,
    path::Path,
};

const SQUARES: [[f64; 2]; 4] = [[32., 32.], [768., 32.], [768., 448.], [32., 448.]];
const NAMES: [&str; 4] = ["TL", "TR", "BR", "BL"];
type Point = [f64; 2];
fn save(path: &Path, image: &Image) -> Result<()> {
    if let Some(parent) = path.parent().filter(|p| !p.as_os_str().is_empty()) {
        fs::create_dir_all(parent)?;
    }
    let mut encoder = png::Encoder::new(
        fs::File::create(path)?,
        image.width as u32,
        image.height as u32,
    );
    encoder.set_color(png::ColorType::Rgb);
    encoder.set_depth(png::BitDepth::Eight);
    encoder.write_header()?.write_image_data(&image.rgb)?;
    Ok(())
}
fn luma(image: &Image) -> Vec<f64> {
    image
        .rgb
        .chunks_exact(3)
        .map(|p| {
            ((19595 * u32::from(p[0]) + 38470 * u32::from(p[1]) + 7471 * u32::from(p[2]) + 32768)
                >> 16) as f64
        })
        .collect()
}
fn quantile(values: &[f64], p: f64) -> f64 {
    let mut values = values.to_vec();
    values.sort_by(f64::total_cmp);
    if values.is_empty() {
        return f64::NAN;
    }
    let at = (values.len() - 1) as f64 * p;
    let i = at.floor() as usize;
    values[i] + (values[at.ceil() as usize] - values[i]) * (at - i as f64)
}
fn homography(src: [Point; 4], dst: [Point; 4]) -> Result<[f64; 8]> {
    let mut matrix = [[0.; 9]; 8];
    for (i, ([u, v], [x, y])) in dst.into_iter().zip(src).enumerate() {
        matrix[i * 2] = [u, v, 1., 0., 0., 0., -u * x, -v * x, x];
        matrix[i * 2 + 1] = [0., 0., 0., u, v, 1., -u * y, -v * y, y];
    }
    for column in 0..8 {
        let pivot = (column..8)
            .max_by(|a, b| {
                matrix[*a][column]
                    .abs()
                    .total_cmp(&matrix[*b][column].abs())
            })
            .unwrap();
        matrix.swap(column, pivot);
        ensure!(
            matrix[column][column].abs() > 1e-15,
            "panel corners define a singular homography"
        );
        let scale = matrix[column][column];
        for j in column..9 {
            matrix[column][j] /= scale;
        }
        for row in 0..8 {
            if row == column {
                continue;
            }
            let factor = matrix[row][column];
            for j in column..9 {
                matrix[row][j] -= factor * matrix[column][j];
            }
        }
    }
    Ok(std::array::from_fn(|i| matrix[i][8]))
}
fn project(coefficients: [f64; 8], x: f64, y: f64) -> Point {
    let [a, b, c, d, e, f, g, h] = coefficients;
    let w = g * x + h * y + 1.;
    [(a * x + b * y + c) / w, (d * x + e * y + f) / w]
}
fn cubic([a, b, c, d]: [f64; 4], t: f64) -> f64 {
    let coefficients = [b, -a + c, 2. * (a - b) + c - d, -a + b - c + d];
    coefficients[0] + t * (coefficients[1] + t * (coefficients[2] + t * coefficients[3]))
}
fn warp(image: &Image, corners: [Point; 4], panel: [usize; 2], scale: usize) -> Result<Image> {
    let (width, height) = (panel[0] * scale, panel[1] * scale);
    let coefficients = homography(
        corners,
        [
            [0., 0.],
            [width as f64, 0.],
            [width as f64, height as f64],
            [0., height as f64],
        ],
    )?;
    let mut rgb = vec![0; width * height * 3];
    for y in 0..height {
        for x in 0..width {
            let [sx, sy] = project(coefficients, x as f64 + 0.5, y as f64 + 0.5);
            if sx < 0. || sy < 0. || sx >= image.width as f64 || sy >= image.height as f64 {
                continue;
            }
            let (ix, iy) = ((sx - 0.5).floor() as isize, (sy - 0.5).floor() as isize);
            let (dx, dy) = (sx - 0.5 - ix as f64, sy - 0.5 - iy as f64);
            for channel in 0..3 {
                let rows = std::array::from_fn(|row| {
                    let yy = (iy - 1 + row as isize).clamp(0, image.height as isize - 1) as usize;
                    let pixels = std::array::from_fn(|column| {
                        let xx =
                            (ix - 1 + column as isize).clamp(0, image.width as isize - 1) as usize;
                        image.rgb[(yy * image.width + xx) * 3 + channel] as f64
                    });
                    cubic(pixels, dx)
                });
                rgb[(y * width + x) * 3 + channel] = cubic(rows, dy).clamp(0., 255.) as u8;
            }
        }
    }
    Ok(Image { width, height, rgb })
}
fn blocks(image: &Image, scale: usize) -> (usize, usize, Vec<[f64; 3]>) {
    let (width, height) = (image.width / scale, image.height / scale);
    let mut pixels = vec![[0.; 3]; width * height];
    for y in 0..height {
        for x in 0..width {
            for dy in 0..scale {
                for dx in 0..scale {
                    for channel in 0..3 {
                        pixels[y * width + x][channel] += f64::from(
                            image.rgb
                                [((y * scale + dy) * image.width + x * scale + dx) * 3 + channel],
                        );
                    }
                }
            }
        }
    }
    for pixel in &mut pixels {
        for channel in pixel {
            *channel /= (scale * scale) as f64;
        }
    }
    (width, height, pixels)
}
fn reduce(image: &Image, scale: usize) -> Image {
    let (width, height, pixels) = blocks(image, scale);
    Image {
        width,
        height,
        rgb: pixels
            .into_iter()
            .flatten()
            .map(|v| v.round_ties_even().clamp(0., 255.) as u8)
            .collect(),
    }
}
fn find(image: &Image) -> Result<()> {
    let luma = luma(image);
    let mut visited = vec![false; luma.len()];
    let mut objects = vec![];
    for seed in 0..luma.len() {
        if visited[seed] || luma[seed] <= 64.0 {
            continue;
        }
        visited[seed] = true;
        let mut queue = VecDeque::from([seed]);
        let (mut x0, mut y0, mut x1, mut y1, mut area) = (image.width, image.height, 0, 0, 0usize);
        while let Some(i) = queue.pop_front() {
            let (x, y) = (i % image.width, i / image.width);
            x0 = x0.min(x);
            x1 = x1.max(x + 1);
            y0 = y0.min(y);
            y1 = y1.max(y + 1);
            area += 1;
            for (dx, dy) in [(1, 0), (-1, 0), (0, 1), (0, -1)] {
                let (xx, yy) = (x as isize + dx, y as isize + dy);
                if xx >= 0 && xx < image.width as isize && yy >= 0 && yy < image.height as isize {
                    let j = yy as usize * image.width + xx as usize;
                    if !visited[j] && luma[j] > 64. {
                        visited[j] = true;
                        queue.push_back(j);
                    }
                }
            }
        }
        objects.push((x0, y0, x1, y1, area));
    }
    let ring = objects
        .iter()
        .enumerate()
        .max_by_key(|(_, (x0, y0, x1, y1, _))| (x1 - x0) * (y1 - y0))
        .map(|(i, _)| i)
        .context("nothing white in the frame: is the test screen up?")?;
    let (rx0, ry0, rx1, ry1, _) = objects[ring];
    let expected = (32. * (rx1 - rx0) as f64 / 800.).powi(2);
    let mut found = [None; 4];
    for (i, (x0, y0, x1, y1, area)) in objects.into_iter().enumerate() {
        if i == ring || area as f64 <= 0.5 * expected || area as f64 >= 1.5 * expected {
            continue;
        }
        let ratio = (x1 - x0) as f64 / (y1 - y0) as f64;
        if ratio <= 0.8 || ratio >= 1.25 || x0 < rx0 || x1 > rx1 || y0 < ry0 || y1 > ry1 {
            continue;
        }
        let (x0, x1, y0, y1) = (
            x0.saturating_sub(24),
            (x1 + 24).min(image.width),
            y0.saturating_sub(24),
            (y1 + 24).min(image.height),
        );
        let mut border = vec![];
        for x in x0..x1 {
            border.push(luma[y0 * image.width + x]);
            border.push(luma[(y1 - 1) * image.width + x]);
        }
        for y in y0..y1 {
            border.push(luma[y * image.width + x0]);
            border.push(luma[y * image.width + x1 - 1]);
        }
        let black = quantile(&border, 0.5);
        let (mut sx, mut sy, mut total) = (0., 0., 0.);
        for y in y0..y1 {
            for x in x0..x1 {
                let weight = (luma[y * image.width + x] - black).max(0.);
                sx += weight * (x as f64 + 0.5);
                sy += weight * (y as f64 + 0.5);
                total += weight;
            }
        }
        ensure!(total > 0., "corner fiducial has no light above its border");
        let (cx, cy) = (sx / total, sy / total);
        if (cx - rx0 as f64).min(rx1 as f64 - cx) > 0.15 * (rx1 - rx0) as f64
            || (cy - ry0 as f64).min(ry1 as f64 - cy) > 0.15 * (ry1 - ry0) as f64
        {
            continue;
        }
        let index = match (cy < (ry0 + ry1) as f64 / 2., cx < (rx0 + rx1) as f64 / 2.) {
            (true, true) => 0,
            (true, false) => 1,
            (false, false) => 2,
            (false, true) => 3,
        };
        ensure!(
            found[index].is_none(),
            "two squares in the {} quarter of the frame",
            NAMES[index]
        );
        found[index] = Some([cx, cy]);
    }
    ensure!(
        found.iter().all(Option::is_some),
        "{} of the corner squares found",
        found.iter().filter(|v| v.is_some()).count()
    );
    let centers = found.map(Option::unwrap);
    let coefficients = homography(centers, SQUARES)?;
    let corners =
        [[0., 0.], [800., 0.], [800., 480.], [0., 480.]].map(|[x, y]| project(coefficients, x, y));
    let x0 = corners
        .iter()
        .map(|p| p[0])
        .fold(f64::INFINITY, f64::min)
        .floor() as i64;
    let y0 = corners
        .iter()
        .map(|p| p[1])
        .fold(f64::INFINITY, f64::min)
        .floor() as i64;
    let x1 = corners
        .iter()
        .map(|p| p[0])
        .fold(f64::NEG_INFINITY, f64::max)
        .ceil() as i64;
    let y1 = corners
        .iter()
        .map(|p| p[1])
        .fold(f64::NEG_INFINITY, f64::max)
        .ceil() as i64;
    println!(
        "corners {}",
        corners
            .iter()
            .map(|[x, y]| format!("{x:.1},{y:.1}"))
            .collect::<Vec<_>>()
            .join(" ")
    );
    println!("score {}:{}:{x0}:{y0}", x1 - x0, y1 - y0);
    println!(
        "squares {}",
        centers
            .iter()
            .enumerate()
            .map(|(i, [x, y])| format!("{} {x:.1},{y:.1}", NAMES[i]))
            .collect::<Vec<_>>()
            .join("  ")
    );
    Ok(())
}
fn firmware_palette(root: &Path) -> Result<Vec<(String, u32)>> {
    let source = fs::read_to_string(root.join("firmware/src_front/main.cpp"))?;
    let mut definitions = BTreeMap::new();
    for line in source.lines() {
        if let Some(rest) = line.strip_prefix("#define") {
            let rest = rest.trim_start();
            if let Some(index) = rest.find(char::is_whitespace) {
                definitions.insert(
                    rest[..index].to_owned(),
                    rest[index..]
                        .split('/')
                        .next()
                        .unwrap_or("")
                        .trim()
                        .to_owned(),
                );
            }
        }
    }
    fn resolve(
        name: &str,
        definitions: &BTreeMap<String, String>,
        seen: &mut Vec<String>,
    ) -> Result<u32> {
        ensure!(
            !seen.iter().any(|v| v == name),
            "cyclic enclosure palette alias {name}"
        );
        let value = definitions
            .get(name)
            .with_context(|| format!("cannot resolve enclosure palette color {name}"))?;
        let value = value
            .strip_prefix("lv_color_hex(")
            .and_then(|v| v.strip_suffix(')'))
            .unwrap_or(value);
        if let Some(hex) = value
            .strip_prefix("0x")
            .or_else(|| value.strip_prefix("0X"))
        {
            return Ok(u32::from_str_radix(hex, 16)?);
        }
        seen.push(name.to_owned());
        resolve(value, definitions, seen)
    }
    let mut entries = vec![];
    for name in [
        "THEME_BG",
        "COL_CARD",
        "COL_CARD_ON",
        "COL_ACCENT",
        "COL_TEXT",
        "COL_DIM",
        "COL_OFF",
        "COL_GOOD",
        "COL_WARN",
    ] {
        entries.push((name.to_owned(), resolve(name, &definitions, &mut vec![])?));
    }
    entries.push(("gray".into(), 0x808080));
    Ok(entries)
}
fn rgb(value: u32) -> [f64; 3] {
    [
        (value >> 16 & 255) as f64,
        (value >> 8 & 255) as f64,
        (value & 255) as f64,
    ]
}
fn palette(root: &Path, image: &Image, scale: usize) -> Result<()> {
    let (width, height, pixels) = blocks(image, scale);
    let patch = |x: usize, y: usize| -> Result<[f64; 3]> {
        ensure!(
            x + 52 <= width && y + 38 <= height,
            "image does not contain the palette patches"
        );
        let mut sum = [0.; 3];
        for yy in y + 10..y + 38 {
            for xx in x + 12..x + 52 {
                for channel in 0..3 {
                    sum[channel] += pixels[yy * width + xx][channel] / 1120.;
                }
            }
        }
        Ok(sum)
    };
    let mut entries = firmware_palette(root)?
        .into_iter()
        .enumerate()
        .map(|(i, (name, value))| Ok((name, value, patch(80 + 64 * i, 168)?)))
        .collect::<Result<Vec<_>>>()?;
    entries.push(("black".into(), 0, patch(144, 56)?));
    entries.push(("white".into(), 0xffffff, patch(144 + 64 * 7, 56)?));
    println!(
        "palette {}",
        entries
            .iter()
            .map(|(name, value, p)| format!(
                "{name}:{value:06x}:{:02x}{:02x}{:02x}",
                (p[0] + 0.5) as u8,
                (p[1] + 0.5) as u8,
                (p[2] + 0.5) as u8
            ))
            .collect::<Vec<_>>()
            .join(" ")
    );
    let mut closest = (f64::INFINITY, 0, 0);
    for (i, (_, _, a)) in entries.iter().enumerate() {
        for (j, (_, _, b)) in entries.iter().enumerate() {
            if i == j {
                continue;
            }
            let distance = (0..3).map(|k| (a[k] - b[k]).powi(2)).sum::<f64>().sqrt();
            if distance < closest.0 {
                closest = (distance, i, j);
            }
        }
    }
    println!(
        "closest as captured: {} and {}, {:.1} levels apart",
        entries[closest.1].0, entries[closest.2].0, closest.0
    );
    Ok(())
}
fn classify(image: &Image, spec: &str, within: f64) -> Result<Image> {
    let entries = spec
        .split_whitespace()
        .map(|part| -> Result<([f64; 3], [f64; 3])> {
            let values = part.split(':').collect::<Vec<_>>();
            ensure!(
                values.len() == 3,
                "palette entries must be NAME:DRAWN:CAPTURED"
            );
            Ok((
                rgb(u32::from_str_radix(values[1], 16)?),
                rgb(u32::from_str_radix(values[2], 16)?),
            ))
        })
        .collect::<Result<Vec<_>>>()?;
    ensure!(!entries.is_empty(), "palette is empty");
    let mut out = image.rgb.clone();
    let mut matched = 0usize;
    for (pixel, result) in image.rgb.chunks_exact(3).zip(out.chunks_exact_mut(3)) {
        let (index, distance) = entries
            .iter()
            .enumerate()
            .map(|(i, (_, capture))| {
                (
                    i,
                    (0..3)
                        .map(|k| (f64::from(pixel[k]) - capture[k]).powi(2))
                        .sum::<f64>(),
                )
            })
            .min_by(|a, b| a.1.total_cmp(&b.1))
            .unwrap();
        if distance.sqrt() <= within {
            for k in 0..3 {
                result[k] = entries[index].0[k] as u8;
            }
            matched += 1;
        }
    }
    println!(
        "{:.0}% of the panel within {within} levels of a palette colour as the camera renders it",
        100. * matched as f64 / (image.width * image.height) as f64
    );
    Ok(Image {
        width: image.width,
        height: image.height,
        rgb: out,
    })
}

#[derive(Clone, Copy, Default)]
struct Complex {
    r: f64,
    i: f64,
}
impl Complex {
    fn phase(angle: f64) -> Self {
        let (i, r) = angle.sin_cos();
        Self { r, i }
    }
    fn add(self, b: Self) -> Self {
        Self {
            r: self.r + b.r,
            i: self.i + b.i,
        }
    }
    fn sub(self, b: Self) -> Self {
        Self {
            r: self.r - b.r,
            i: self.i - b.i,
        }
    }
    fn mul(self, b: Self) -> Self {
        Self {
            r: self.r * b.r - self.i * b.i,
            i: self.r * b.i + self.i * b.r,
        }
    }
    fn conjugate(self) -> Self {
        Self {
            r: self.r,
            i: -self.i,
        }
    }
    fn norm(self) -> f64 {
        self.r.hypot(self.i)
    }
}
fn fft(values: &mut [Complex], inverse: bool) {
    let n = values.len();
    let mut j = 0;
    for i in 1..n {
        let mut bit = n >> 1;
        while j & bit != 0 {
            j ^= bit;
            bit >>= 1;
        }
        j ^= bit;
        if i < j {
            values.swap(i, j);
        }
    }
    let mut size = 2;
    while size <= n {
        let root = Complex::phase(if inverse { 2.0 } else { -2.0 } * PI / size as f64);
        for block in values.chunks_exact_mut(size) {
            let mut phase = Complex { r: 1., i: 0. };
            for i in 0..size / 2 {
                let a = block[i];
                let b = block[i + size / 2].mul(phase);
                block[i] = a.add(b);
                block[i + size / 2] = a.sub(b);
                phase = phase.mul(root);
            }
        }
        size *= 2;
    }
    if inverse {
        for value in values {
            value.r /= n as f64;
            value.i /= n as f64;
        }
    }
}
struct Fourier {
    chirp: Vec<Complex>,
    kernel: Vec<Complex>,
}
impl Fourier {
    fn new(n: usize) -> Self {
        let length = (2 * n - 1).next_power_of_two();
        let chirp = (0..n)
            .map(|i| Complex::phase(-PI * (i * i) as f64 / n as f64))
            .collect::<Vec<_>>();
        let mut kernel = vec![Complex::default(); length];
        kernel[0] = Complex { r: 1., i: 0. };
        for i in 1..n {
            kernel[i] = chirp[i].conjugate();
            kernel[length - i] = chirp[i].conjugate();
        }
        fft(&mut kernel, false);
        Self { chirp, kernel }
    }
    fn spectrum(&self, samples: &[f64]) -> Vec<f64> {
        let n = samples.len();
        let mean = samples.iter().sum::<f64>() / n as f64;
        let mut work = vec![Complex::default(); self.kernel.len()];
        for i in 0..n {
            let sample =
                (samples[i] - mean) * (0.5 - 0.5 * (2. * PI * i as f64 / (n - 1) as f64).cos());
            work[i] = self.chirp[i].mul(Complex { r: sample, i: 0. });
        }
        fft(&mut work, false);
        for (i, value) in work.iter_mut().enumerate() {
            *value = value.mul(self.kernel[i]);
        }
        fft(&mut work, true);
        (0..=n / 2)
            .map(|i| work[i].mul(self.chirp[i]).norm())
            .collect()
    }
}
fn period(rows: &[Vec<f64>]) -> Result<f64> {
    let n = rows.first().context("empty image region")?.len();
    ensure!(n > 4, "image region too narrow for lattice measurement");
    let plan = Fourier::new(n);
    let mut spectrum = vec![0.; n / 2 + 1];
    for row in rows {
        for (i, value) in plan.spectrum(row).into_iter().enumerate() {
            spectrum[i] += value / rows.len() as f64;
        }
    }
    let peak = (1..spectrum.len() - 1)
        .filter(|i| {
            let frequency = *i as f64 / n as f64;
            frequency > 1. / 4.5 && frequency < 1. / 2.2
        })
        .max_by(|a, b| spectrum[*a].total_cmp(&spectrum[*b]))
        .context("no lattice frequency band")?;
    let (a, b, c) = (spectrum[peak - 1], spectrum[peak], spectrum[peak + 1]);
    Ok(n as f64 / (peak as f64 + 0.5 * (a - c) / (a - 2. * b + c)))
}
fn crossings(profile: &[f64], start: isize, rising: bool) -> Vec<f64> {
    let mid = (quantile(profile, 0.05) + quantile(profile, 0.95)) / 2.;
    profile
        .windows(2)
        .enumerate()
        .filter_map(|(i, p)| {
            let crossed = if rising {
                p[0] < mid && p[1] >= mid
            } else {
                p[0] >= mid && p[1] < mid
            };
            crossed.then(|| start as f64 + i as f64 + 0.5 + (mid - p[0]) / (p[1] - p[0]))
        })
        .collect()
}
fn check(image: &Image, scale: usize) -> Result<()> {
    let luma = luma(image);
    let (x0, x1, y0, y1) = (
        image.width / 8,
        image.width - image.width / 8,
        image.height / 8,
        image.height - image.height / 8,
    );
    let horizontal = (y0..y1)
        .map(|y| luma[y * image.width + x0..y * image.width + x1].to_vec())
        .collect::<Vec<_>>();
    let vertical = (x0..x1)
        .map(|x| {
            (y0..y1)
                .map(|y| luma[y * image.width + x])
                .collect::<Vec<_>>()
        })
        .collect::<Vec<_>>();
    println!(
        "lattice {:.3} x {:.3} px per panel px",
        period(&horizontal)?,
        period(&vertical)?
    );
    let (width, height) = (image.width / scale, image.height / scale);
    ensure!(
        width >= 560 && height >= 448,
        "image does not contain the complete panel test patterns"
    );
    let mut panel = vec![0.; width * height];
    for y in 0..height {
        for x in 0..width {
            for dy in 0..scale {
                for dx in 0..scale {
                    panel[y * width + x] += luma[(y * scale + dy) * image.width + x * scale + dx]
                        / (scale * scale) as f64;
                }
            }
        }
    }
    let columns = (240..304)
        .map(|x| (276..324).map(|y| panel[y * width + x]).sum::<f64>() / 48.)
        .collect::<Vec<_>>();
    let rows = (268..332)
        .map(|y| (376..424).map(|x| panel[y * width + x]).sum::<f64>() / 48.)
        .collect::<Vec<_>>();
    let average = |v: &[f64], offset: usize| {
        v.iter().skip(offset).step_by(2).sum::<f64>() / (v.len() / 2) as f64
    };
    let (ve, vo, he, ho) = (
        average(&columns, 0),
        average(&columns, 1),
        average(&rows, 0),
        average(&rows, 1),
    );
    println!(
        "stripes: one-pixel columns {ve:.0} / {vo:.0}, rows {he:.0} / {ho:.0}  (modulation {:.2}, {:.2})",
        (ve - vo).abs() / (ve + vo),
        (he - ho).abs() / (he + ho)
    );
    let mut offsets = vec![];
    let mut widths = vec![];
    for (i, [cx, cy]) in SQUARES.into_iter().enumerate() {
        let (x0, x1, y0, y1) = (
            ((cx - 16.) * scale as f64) as isize,
            ((cx + 16.) * scale as f64) as isize,
            ((cy - 16.) * scale as f64) as isize,
            ((cy + 16.) * scale as f64) as isize,
        );
        let mut left = vec![];
        let mut right = vec![];
        let mut top = vec![];
        let mut bottom = vec![];
        let wrap = |coordinate: isize, length: usize| -> Result<usize> {
            let wrapped = if coordinate < 0 {
                length as isize + coordinate
            } else {
                coordinate
            };
            ensure!(
                wrapped >= 0 && wrapped < length as isize,
                "square profile is outside image"
            );
            Ok(wrapped as usize)
        };
        for y in (y0 + 20..y1 - 20).step_by(4) {
            let profile = (x0 - 30..x1 + 30)
                .map(|x| Ok(luma[wrap(y, image.height)? * image.width + wrap(x, image.width)?]))
                .collect::<Result<Vec<_>>>()?;
            if let Some(v) = crossings(&profile, x0 - 30, true).first() {
                left.push(*v);
            }
            if let Some(v) = crossings(&profile, x0 - 30, false).last() {
                right.push(*v);
            }
        }
        for x in (x0 + 20..x1 - 20).step_by(4) {
            let profile = (y0 - 30..y1 + 30)
                .map(|y| Ok(luma[wrap(y, image.height)? * image.width + wrap(x, image.width)?]))
                .collect::<Result<Vec<_>>>()?;
            if let Some(v) = crossings(&profile, y0 - 30, true).first() {
                top.push(*v);
            }
            if let Some(v) = crossings(&profile, y0 - 30, false).last() {
                bottom.push(*v);
            }
        }
        let (l, r, t, b) = (
            quantile(&left, 0.5),
            quantile(&right, 0.5),
            quantile(&top, 0.5),
            quantile(&bottom, 0.5),
        );
        offsets.push(format!(
            "{} {:+.2},{:+.2}",
            NAMES[i],
            (l + r) / 2. - (x0 + x1) as f64 / 2.,
            (t + b) / 2. - (y0 + y1) as f64 / 2.
        ));
        widths.extend([r - l, b - t]);
    }
    println!(
        "squares: {} px off centre; {:.1}..{:.1} px wide for {}",
        offsets.join("  "),
        widths.iter().copied().fold(f64::INFINITY, f64::min),
        widths.iter().copied().fold(f64::NEG_INFINITY, f64::max),
        32 * scale
    );
    Ok(())
}

pub fn run(root: &Path, args: &[String]) -> Result<()> {
    let positional = validate_args(
        args,
        &[],
        &["--scale", "--corners", "--panel", "--palette", "--within"],
    )?;
    ensure!(
        positional.len() >= 2,
        "panelcam-rectify find|warp|reduce|check|palette|classify IMAGE [OUTPUT] [OPTIONS]"
    );
    let scale = option(args, "--scale")?
        .unwrap_or_else(|| "3".into())
        .parse::<usize>()?;
    ensure!(scale > 0, "scale must be positive");
    let image = rgb565::read(Path::new(&positional[1]))?;
    match positional[0].as_str() {
        "find" => find(&image),
        "reduce" => {
            ensure!(positional.len() == 3, "reduce requires an output image");
            save(Path::new(&positional[2]), &reduce(&image, scale))
        }
        "palette" => palette(root, &image, scale),
        "classify" => {
            ensure!(positional.len() == 3, "classify requires an output image");
            let within = option(args, "--within")?
                .unwrap_or_else(|| "28".into())
                .parse::<f64>()?;
            save(
                Path::new(&positional[2]),
                &classify(
                    &image,
                    &option(args, "--palette")?.unwrap_or_default(),
                    within,
                )?,
            )
        }
        "warp" => {
            ensure!(positional.len() == 3, "warp requires an output image");
            let points = option(args, "--corners")?
                .context("--corners is required")?
                .split_whitespace()
                .map(|pair| -> Result<Point> {
                    let (x, y) = pair.split_once(',').context("corner must be x,y")?;
                    Ok([x.parse()?, y.parse()?])
                })
                .collect::<Result<Vec<_>>>()?;
            let corners: [Point; 4] = points.try_into().map_err(|_| {
                anyhow::anyhow!("corners must contain the panel corners in TL TR BR BL order")
            })?;
            let panel = option(args, "--panel")?.unwrap_or_else(|| "800x480".into());
            let (w, h) = panel.split_once('x').context("panel must be WxH")?;
            save(
                Path::new(&positional[2]),
                &warp(&image, corners, [w.parse()?, h.parse()?], scale)?,
            )
        }
        "check" => check(&image, scale),
        other => bail!("unknown panel analysis command {other}"),
    }
}
