//! Camera projection and alpha-aware resampling place the guide screen inside its current bezel.
use anyhow::{Context, Result, ensure};
use hsm_pages::RgbaImage;

pub fn project(point: [f64; 3], matrix: &[f64; 16], size: [u32; 2]) -> Result<[f64; 2]> {
    let p = [point[0], point[1], point[2], 1.];
    let q: [f64; 4] =
        std::array::from_fn(|row| (0..4).map(|col| matrix[col * 4 + row] * p[col]).sum());
    ensure!(
        q.iter().all(|v| v.is_finite()) && q[3].abs() > f64::EPSILON,
        "camera cannot project this anchor"
    );
    Ok([
        (q[0] / q[3] + 1.) * size[0] as f64 / 2.,
        (1. - q[1] / q[3]) * size[1] as f64 / 2.,
    ])
}

fn homography(corners: [[f64; 2]; 4], size: [u32; 2]) -> Result<[f64; 8]> {
    let (w, h) = (size[0] as f64, size[1] as f64);
    let mut a = [[0.; 9]; 8];
    for (i, ([x, y], [u, v])) in corners
        .into_iter()
        .zip([[0., 0.], [w, 0.], [w, h], [0., h]])
        .enumerate()
    {
        a[i * 2] = [x, y, 1., 0., 0., 0., -u * x, -u * y, u];
        a[i * 2 + 1] = [0., 0., 0., x, y, 1., -v * x, -v * y, v];
    }
    for col in 0..8 {
        let pivot = (col..8)
            .max_by(|&i, &j| a[i][col].abs().total_cmp(&a[j][col].abs()))
            .context("screen projection pivot")?;
        a.swap(col, pivot);
        ensure!(
            a[col][col].abs() > 1e-12,
            "screen corners collapse in this camera"
        );
        let scale = a[col][col];
        for v in &mut a[col][col..] {
            *v /= scale;
        }
        for row in 0..8 {
            if row == col {
                continue;
            }
            let scale = a[row][col];
            for k in col..9 {
                a[row][k] -= scale * a[col][k];
            }
        }
    }
    Ok(std::array::from_fn(|i| a[i][8]))
}

fn cubic(x: f64) -> f64 {
    let x = x.abs();
    if x < 1. {
        1.5 * x.powi(3) - 2.5 * x.powi(2) + 1.
    } else if x < 2. {
        -0.5 * x.powi(3) + 2.5 * x.powi(2) - 4. * x + 2.
    } else {
        0.
    }
}

/// A premultiplied sample avoids a fringe from colours hidden behind transparent pixels.
fn sample(image: &RgbaImage, u: f64, v: f64) -> [f64; 4] {
    if u < 0. || v < 0. || u >= image.width as f64 || v >= image.height as f64 {
        return [0.; 4];
    }
    let (x, y) = (u - 0.5, v - 0.5);
    let (ix, iy) = (x.floor() as i64, y.floor() as i64);
    let mut out = [0.; 4];
    for sy in iy - 1..=iy + 2 {
        let wy = cubic(y - sy as f64);
        for sx in ix - 1..=ix + 2 {
            let weight = wy * cubic(x - sx as f64);
            let px = sx.clamp(0, image.width as i64 - 1) as usize;
            let py = sy.clamp(0, image.height as i64 - 1) as usize;
            let pixel = &image.data[(py * image.width as usize + px) * 4..][..4];
            let alpha = pixel[3] as f64 / 255.;
            for c in 0..3 {
                out[c] += pixel[c] as f64 / 255. * alpha * weight;
            }
            out[3] += alpha * weight;
        }
    }
    out[3] = out[3].clamp(0., 1.);
    for c in 0..3 {
        out[c] = out[c].clamp(0., out[3]);
    }
    out
}

pub fn overlay(image: &mut RgbaImage, art: &RgbaImage, corners: [[f64; 2]; 4]) -> Result<()> {
    ensure!(art.width > 0 && art.height > 0, "screen artwork is empty");
    let a = homography(corners, [art.width, art.height])?;
    let min = std::array::from_fn::<_, 2, _>(|i| {
        corners
            .iter()
            .map(|p| p[i])
            .fold(f64::INFINITY, f64::min)
            .floor()
            .max(0.) as u32
    });
    let max = std::array::from_fn::<_, 2, _>(|i| {
        corners
            .iter()
            .map(|p| p[i])
            .fold(f64::NEG_INFINITY, f64::max)
            .ceil()
            .max(0.) as u32
    });
    for y in min[1]..max[1].min(image.height) {
        for x in min[0]..max[0].min(image.width) {
            let (px, py) = (x as f64 + 0.5, y as f64 + 0.5);
            let denominator = a[6] * px + a[7] * py + 1.;
            if denominator.abs() < f64::EPSILON {
                continue;
            }
            let source = sample(
                art,
                (a[0] * px + a[1] * py + a[2]) / denominator,
                (a[3] * px + a[4] * py + a[5]) / denominator,
            );
            if source[3] == 0. {
                continue;
            }
            let dest = &mut image.data[((y * image.width + x) * 4) as usize..][..4];
            let under = dest[3] as f64 / 255. * (1. - source[3]);
            let alpha = source[3] + under;
            for c in 0..3 {
                dest[c] = ((source[c] + dest[c] as f64 / 255. * under) / alpha * 255.)
                    .round()
                    .clamp(0., 255.) as u8;
            }
            dest[3] = (alpha * 255.).round().clamp(0., 255.) as u8;
        }
    }
    Ok(())
}

fn lanczos(x: f64) -> f64 {
    let x = x.abs();
    if x < f64::EPSILON {
        return 1.;
    }
    if x >= 3. {
        return 0.;
    }
    let p = x * std::f64::consts::PI;
    p.sin() / p * (p / 3.).sin() / (p / 3.)
}

fn taps(source: u32, target: u32) -> Vec<Vec<(usize, f64)>> {
    let scale = source as f64 / target as f64;
    let spread = scale.max(1.);
    (0..target)
        .map(|i| {
            let center = (i as f64 + 0.5) * scale - 0.5;
            let lo = (center - 3. * spread).ceil().max(0.) as i64;
            let hi = (center + 3. * spread).floor().min(source as f64 - 1.) as i64;
            let mut rows: Vec<_> = (lo..=hi)
                .map(|j| (j as usize, lanczos((center - j as f64) / spread)))
                .collect();
            let total: f64 = rows.iter().map(|(_, w)| *w).sum();
            for (_, weight) in &mut rows {
                *weight /= total;
            }
            rows
        })
        .collect()
}

pub fn resize(image: &RgbaImage, size: [u32; 2]) -> Result<RgbaImage> {
    ensure!(
        size[0] > 0 && size[1] > 0,
        "reference image dimensions are empty"
    );
    if size == [image.width, image.height] {
        return Ok(image.clone());
    }
    let xs = taps(image.width, size[0]);
    let ys = taps(image.height, size[1]);
    let mut across = vec![[0f32; 4]; size[0] as usize * image.height as usize];
    for y in 0..image.height as usize {
        for (x, weights) in xs.iter().enumerate() {
            let out = &mut across[y * size[0] as usize + x];
            for &(sx, weight) in weights {
                let pixel = &image.data[(y * image.width as usize + sx) * 4..][..4];
                let alpha = pixel[3] as f32 / 255.;
                for c in 0..3 {
                    out[c] += pixel[c] as f32 * alpha * weight as f32;
                }
                out[3] += pixel[3] as f32 * weight as f32;
            }
        }
    }
    let mut out = RgbaImage {
        width: size[0],
        height: size[1],
        data: vec![0; size[0] as usize * size[1] as usize * 4],
    };
    for (y, weights) in ys.iter().enumerate() {
        for x in 0..size[0] as usize {
            let mut pixel = [0f32; 4];
            for &(sy, weight) in weights {
                for c in 0..4 {
                    pixel[c] += across[sy * size[0] as usize + x][c] * weight as f32;
                }
            }
            let target = &mut out.data[(y * size[0] as usize + x) * 4..][..4];
            if pixel[3] > 0. {
                for c in 0..3 {
                    target[c] = (pixel[c] * 255. / pixel[3]).round().clamp(0., 255.) as u8;
                }
            }
            target[3] = pixel[3].round().clamp(0., 255.) as u8;
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn renderer_projection_uses_its_column_major_matrix() {
        let matrix = [
            2., 0., 0., 0., 0., 3., 0., 0., 0., 0., 1., 0., 0.2, -0.4, 0., 1.,
        ];
        let pixel = project([0.1, 0.2, 0.], &matrix, [1000, 600]).unwrap();
        assert!((pixel[0] - 700.).abs() < 1e-9);
        assert!((pixel[1] - 240.).abs() < 1e-9);
    }

    #[test]
    fn perspective_screen_retains_its_edges_and_alpha() {
        let mut image = RgbaImage {
            width: 6,
            height: 6,
            data: [0, 0, 255, 255].repeat(36),
        };
        let art = RgbaImage {
            width: 2,
            height: 2,
            data: [255, 0, 0, 128].repeat(4),
        };
        overlay(&mut image, &art, [[1., 1.], [5., 1.], [4., 5.], [2., 5.]]).unwrap();
        assert_eq!(&image.data[0..4], &[0, 0, 255, 255]);
        assert_eq!(&image.data[(2 * 6 + 3) * 4..][..4], &[128, 0, 127, 255]);
        assert_eq!(&image.data[(4 * 6 + 1) * 4..][..4], &[0, 0, 255, 255]);
        let shrunk = resize(&art, [1, 1]).unwrap();
        assert_eq!(shrunk.data, vec![255, 0, 0, 128]);
    }
}
