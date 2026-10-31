//! The contact shadow's falloff, drawn as scene.js `shadowTexture` draws it into a canvas: 256 px
//! on the long side at the model's footprint aspect, a wide soft pass leaning away from the key
//! and a tight dark one under the footprint, each a rounded rectangle blurred and laid over the
//! last. Only the alpha is kept; the colour is black.

/// Where the key stands (scene.js KEY_DIR); the soft pass is thrown off it.
use std::sync::{Arc, Mutex};

const KEY_DIR: [f64; 3] = [1.0, -1.2, 2.0];
const PX: f64 = 256.0;
/// The fraction of the texture the falloff runs out over.
const PAD: f64 = 0.34;
/// How far past the footprint the soft pass reaches.
const SPREAD: f64 = 0.06;
/// How much of a point light's throw the soft pass keeps.
const LEAN: f64 = 0.14;

pub struct ShadowMap {
    pub width: u32,
    pub height: u32,
    /// The mip chain, finest first, one byte of alpha a texel.
    pub levels: Vec<Vec<u8>>,
}

/// The quad's scale over the footprint: the footprint fills the middle `1 - 2·PAD` of it.
pub const QUAD_OVER_FOOTPRINT: f64 = 1.0 / (1.0 - 2.0 * PAD);

/// `aspect` is the footprint's depth over its width. A falloff depends on its height alone, so
/// each one drawn is kept for the next picture of the same footprint.
pub fn falloff(aspect: f64) -> Arc<ShadowMap> {
    static DRAWN: Mutex<Vec<Arc<ShadowMap>>> = Mutex::new(Vec::new());
    let h = ((PX * aspect).round() as usize).max(64);
    let mut drawn = DRAWN.lock().unwrap_or_else(|e| e.into_inner());
    if let Some(m) = drawn.iter().find(|m| m.height as usize == h) {
        return m.clone();
    }
    let m = Arc::new(draw(h));
    drawn.push(m.clone());
    m
}

fn draw(h: usize) -> ShadowMap {
    let w = PX as usize;
    let (wf, hf) = (w as f64, h as f64);
    let footprint = [wf * PAD, hf * PAD, wf * (1.0 - 2.0 * PAD), hf * (1.0 - 2.0 * PAD)];
    // Canvas +x is world +X and canvas +y is world -Y; the throw runs opposite the key.
    let throw_x = -(KEY_DIR[0] / KEY_DIR[2]) * LEAN * wf;
    let throw_y = (KEY_DIR[1] / KEY_DIR[2]) * LEAN * hf;
    let grown = [
        footprint[0] - wf * SPREAD + throw_x,
        footprint[1] - hf * SPREAD + throw_y,
        footprint[2] + wf * SPREAD * 2.0,
        footprint[3] + hf * SPREAD * 2.0,
    ];
    let mut canvas = vec![0f32; w * h];
    let soft = blur(rounded_rect(w, h, grown, wf * 0.06, 0.42), w, h, (wf * 0.10).round());
    over(&mut canvas, &soft);
    let tight = blur(rounded_rect(w, h, footprint, wf * 0.03, 0.82), w, h, (wf * 0.05).round());
    over(&mut canvas, &tight);

    let mut levels = vec![canvas.iter().map(|a| (a * 255.0).round().clamp(0.0, 255.0) as u8).collect::<Vec<_>>()];
    let (mut lw, mut lh) = (w, h);
    while lw > 1 || lh > 1 {
        let (nw, nh) = ((lw / 2).max(1), (lh / 2).max(1));
        let src = levels.last().unwrap();
        let mut next = vec![0u8; nw * nh];
        for y in 0..nh {
            for x in 0..nw {
                let mut sum = 0u32;
                let mut n = 0u32;
                for sy in [2 * y, 2 * y + 1] {
                    for sx in [2 * x, 2 * x + 1] {
                        if sx < lw && sy < lh {
                            sum += src[sy * lw + sx] as u32;
                            n += 1;
                        }
                    }
                }
                next[y * nw + x] = ((sum + n / 2) / n) as u8;
            }
        }
        levels.push(next);
        (lw, lh) = (nw, nh);
    }
    ShadowMap {
        width: w as u32,
        height: h as u32,
        levels,
    }
}

/// Coverage of a filled rounded rectangle at each pixel centre, antialiased over a pixel.
fn rounded_rect(w: usize, h: usize, [x, y, rw, rh]: [f64; 4], radius: f64, alpha: f64) -> Vec<f32> {
    let r = radius.min(rw / 2.0).min(rh / 2.0).max(0.0);
    let (cx, cy) = (x + rw / 2.0, y + rh / 2.0);
    let (hx, hy) = (rw / 2.0 - r, rh / 2.0 - r);
    let mut out = vec![0f32; w * h];
    for py in 0..h {
        for px in 0..w {
            let dx = ((px as f64 + 0.5 - cx).abs() - hx).max(0.0);
            let dy = ((py as f64 + 0.5 - cy).abs() - hy).max(0.0);
            let inside = ((px as f64 + 0.5 - cx).abs() - hx).max((py as f64 + 0.5 - cy).abs() - hy).min(0.0);
            let distance = (dx * dx + dy * dy).sqrt() + inside - r;
            out[py * w + px] = ((0.5 - distance).clamp(0.0, 1.0) * alpha) as f32;
        }
    }
    out
}

/// The canvas `blur(σ px)` filter: a Gaussian of that standard deviation, nothing past the edge.
fn blur(src: Vec<f32>, w: usize, h: usize, sigma: f64) -> Vec<f32> {
    if sigma <= 0.0 {
        return src;
    }
    let radius = (3.0 * sigma).ceil() as isize;
    let kernel: Vec<f32> = (-radius..=radius)
        .map(|i| (-(i * i) as f64 / (2.0 * sigma * sigma)).exp())
        .map(|k| k as f32)
        .collect();
    let total: f32 = kernel.iter().sum();
    let kernel: Vec<f32> = kernel.iter().map(|k| k / total).collect();
    let pass = |src: &[f32], stride: usize, along: usize, across: usize| -> Vec<f32> {
        let mut out = vec![0f32; src.len()];
        for a in 0..across {
            for i in 0..along {
                let mut acc = 0f32;
                for (k, wgt) in kernel.iter().enumerate() {
                    let j = i as isize + k as isize - radius;
                    if j >= 0 && (j as usize) < along {
                        let (x, y) = if stride == 1 { (j as usize, a) } else { (a, j as usize) };
                        acc += wgt * src[y * w + x];
                    }
                }
                let (x, y) = if stride == 1 { (i, a) } else { (a, i) };
                out[y * w + x] = acc;
            }
        }
        out
    };
    let rows = pass(&src, 1, w, h);
    pass(&rows, w, h, w)
}

/// Source-over, alpha only.
fn over(dst: &mut [f32], src: &[f32]) {
    for (d, s) in dst.iter_mut().zip(src) {
        *d = s + *d * (1.0 - s);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_falloff_is_dark_under_the_footprint_and_clear_at_the_rim() {
        let m = falloff(1.5);
        assert_eq!((m.width, m.height), (256, 384));
        let a = &m.levels[0];
        let at = |x: usize, y: usize| a[y * 256 + x];
        assert!(at(128, 192) > 200, "centre {}", at(128, 192));
        assert_eq!(at(0, 0), 0);
        assert_eq!(m.levels.last().unwrap().len(), 1);
    }
}
