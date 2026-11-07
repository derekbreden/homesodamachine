//! The counter-opening picture: the faucet's four tube tails, display cable and shank held over
//! the one round hole in the counter, drawn on this Mac's GPU from the faucet's current model.
//! Beside it, the outline of the faucet's parts in the same frame, which the booklet draws where
//! the parts cross the counter.
use anyhow::{Context, Result, ensure};
use hsm_faucet_numbers::countertop;
use hsm_kernel::write::{Body, payload_bytes};
use hsm_kernel::*;
use hsm_pages::RgbaImage;
use hsm_render::job::Job;
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::fmt::Write as _;
use std::path::{Path as FilePath, PathBuf};


/// The picture's palette, in sRGB.
const STONE: [f32; 3] = [0.55, 0.55, 0.58];
const STEEL: [f32; 3] = [0.78, 0.79, 0.82];
const WHITE_TUBE: [f32; 3] = [0.90, 0.90, 0.93];
const BLUE_TUBE: [f32; 3] = [0.16, 0.40, 0.75];
const BLACK_PART: [f32; 3] = [0.10, 0.10, 0.12];

/// A colour as a model carries it: linear RGB, as OCCT converts it in single precision.
fn linear(c: [f32; 3]) -> [f64; 3] {
    c.map(|v| (if v <= 0.04045 { v / 12.92 } else { ((v + 0.055) / 1.055).powf(2.4) }) as f64)
}

/// The faucet's parts below the counter seen in the picture, the paint each takes, and the
/// name the picture gives it.
const TAILS: [(&str, [f32; 3], &str); 6] = [
    ("flavor_tube_pos_x", BLACK_PART, "flavor_tube_pos_x"),
    ("flavor_tube_neg_x", BLACK_PART, "flavor_tube_neg_x"),
    ("soda_umbilical_tube", BLUE_TUBE, "soda_umbilical_tube"),
    ("drain_tube", WHITE_TUBE, "drain_tube"),
    ("display_signal_ribbon", BLACK_PART, "display_signal_ribbon"),
    ("westbrass", STEEL, "shank"),
];

/// The faucet's height band the picture keeps, and how far over the counter it is held.
const BAND: [f64; 2] = [-70.0, 40.0];
const LIFT: f64 = 128.0;

/// The counter with its hole, as the faucet assembly clamps through it, and the faucet's tails
/// held over it.
fn scene() -> Result<Vec<(String, Solid, [f64; 3])>> {
    let (bottom, top) = (countertop::BOTTOM_Z, countertop::TOP_Z);
    let (hole_y, hole_r) = (countertop::hole_center_y(), countertop::HOLE_RADIUS);
    let slab = Solid::cuboid(v3(-160., -105., bottom), v3(160., 105., top));
    let hole = Solid::cylinder(v3(0., hole_y, bottom - 1.), V3::Z, hole_r, top - bottom + 2.)?;
    let mut out = vec![("countertop".to_owned(), slab.cut(&hole)?, linear(STONE))];
    let bodies = import::payload("hardware/faucet-layout/faucet-assembly.step.mesh")?;
    let clip = Solid::cuboid(v3(-300., -300., BAND[0]), v3(300., 300., BAND[1]));
    for (name, paint, shown) in TAILS {
        for body in bodies.iter().filter(|b| b.name == name) {
            let b = body.solid.bounds();
            if b.max.z <= BAND[0] || b.min.z >= BAND[1] {
                continue;
            }
            let cropped = body.solid.intersect(&clip)?.translate(v3(0., 0., LIFT));
            if !cropped.tris().is_empty() {
                out.push((shown.to_owned(), cropped, linear(paint)));
            }
        }
    }
    Ok(out)
}

/// The picture's camera, frame and look.
fn job(payload: PathBuf, out: PathBuf) -> Job {
    Job {
        payload: Some(payload),
        out: Some(out),
        cam: Some([0.42, -0.80, 0.95]),
        target: Some([0.0, 0.0, 24.0]),
        up: Some([0.0, 0.0, 1.0]),
        span: Some(120.0),
        zoom: Some(10.0),
        ortho: true,
        size: "3800x3200".into(),
        bg: "#f2eee8".into(),
        transparent: true,
        solid: true,
        trim: false,
        ground: false,
        fog: false,
        ..Job::default()
    }
}

/// Fill every hole in `mask`: whatever empty pixel the border cannot reach, stepping across
/// edges only.
fn fill_holes(mask: &mut [bool], w: usize, h: usize) {
    let mut outside = vec![false; w * h];
    let mut todo: Vec<usize> = Vec::new();
    for x in 0..w {
        todo.extend([x, (h - 1) * w + x]);
    }
    for y in 0..h {
        todo.extend([y * w, y * w + w - 1]);
    }
    while let Some(i) = todo.pop() {
        if mask[i] || outside[i] {
            continue;
        }
        outside[i] = true;
        let (x, y) = (i % w, i / w);
        if x > 0 {
            todo.push(i - 1);
        }
        if x + 1 < w {
            todo.push(i + 1);
        }
        if y > 0 {
            todo.push(i - w);
        }
        if y + 1 < h {
            todo.push(i + w);
        }
    }
    for (m, o) in mask.iter_mut().zip(outside) {
        *m = !o;
    }
}

/// The closed loops along the pixel edges between `mask` and what is outside it, clockwise,
/// keeping only the corners.
fn outlines(mask: &[bool], w: usize, h: usize) -> Vec<Vec<[u32; 2]>> {
    let at = |x: i64, y: i64| x >= 0 && y >= 0 && (x as usize) < w && (y as usize) < h && mask[y as usize * w + x as usize];
    let mut edges: HashMap<[u32; 2], Vec<[u32; 2]>> = HashMap::new();
    let mut order: Vec<[u32; 2]> = Vec::new();
    for side in 0..4 {
        for y in 0..h as i64 {
            for x in 0..w as i64 {
                if !at(x, y) {
                    continue;
                }
                let (nx, ny) = [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)][side];
                if at(nx, ny) {
                    continue;
                }
                let (x, y) = (x as u32, y as u32);
                let (a, b) = [
                    ([x, y], [x + 1, y]),
                    ([x + 1, y], [x + 1, y + 1]),
                    ([x + 1, y + 1], [x, y + 1]),
                    ([x, y + 1], [x, y]),
                ][side];
                let next = edges.entry(a).or_default();
                if next.is_empty() {
                    order.push(a);
                }
                next.push(b);
            }
        }
    }
    let mut loops = Vec::new();
    for &start in &order {
        if !edges.contains_key(&start) {
            continue;
        }
        let mut point = start;
        let mut path = vec![point];
        loop {
            let options = edges.get_mut(&point).expect("every edge's end starts another");
            let following = options.pop().expect("an edge out of every point on a loop");
            if options.is_empty() {
                edges.remove(&point);
            }
            path.push(following);
            point = following;
            if point == start {
                break;
            }
        }
        let mut keep = vec![path[0]];
        for i in 1..path.len() - 1 {
            let (a, p, b) = (path[i - 1], path[i], path[i + 1]);
            let turn = (p[0] as i64 - a[0] as i64) * (b[1] as i64 - p[1] as i64) - (p[1] as i64 - a[1] as i64) * (b[0] as i64 - p[0] as i64);
            if turn != 0 {
                keep.push(p);
            }
        }
        if keep.len() >= 3 {
            loops.push(keep);
        }
    }
    loops
}

fn write(path: &FilePath, bytes: &[u8]) -> Result<()> {
    std::fs::write(path, bytes).with_context(|| format!("writing {}", path.display()))
}

fn main() -> Result<()> {
    let root = std::path::absolute(".")?;
    let out = std::path::absolute(std::env::args().nth(1).unwrap_or_else(|| ".".into()))?;
    let assets = out.join("hardware/install-guide/assets");
    std::fs::create_dir_all(&assets)?;
    // The renderer reads the viewer's finishes beside the checkout; name the read.
    let finishes = FilePath::new("web/public/finishes.json");
    hsm_kernel::reads::read(finishes, &std::fs::read(finishes).context("the viewer's finishes")?);

    let shown = scene()?;
    let scratch = std::env::temp_dir().join(format!("hsm-opening-scene-{}", std::process::id()));
    std::fs::create_dir_all(&scratch)?;
    let mut renderer = hsm_render::Renderer::new();
    let mut pictures = Vec::new();
    for (name, keep_counter) in [("scene", true), ("components", false)] {
        let bodies: Vec<Body> = shown
            .iter()
            .filter(|(n, _, _)| keep_counter || n != "countertop")
            .map(|(name, solid, color)| Body { name, solid, color: Some(*color) })
            .collect();
        let payload = scratch.join(format!("{name}.mesh"));
        write(&payload, &payload_bytes(&bodies, None, None))?;
        let png = scratch.join(format!("{name}.png"));
        renderer.render(&root, &job(payload, png.clone()))?;
        pictures.push(RgbaImage::read_png(&std::fs::read(&png)?)?);
    }
    let _ = std::fs::remove_dir_all(&scratch);
    let (picture, components) = (&pictures[0], &pictures[1]);

    let crop = picture.alpha_bounds_over(11).context("the opening picture drew nothing")?;
    let cropped = picture.crop(crop.map(i64::from));
    let png = cropped.png()?;
    write(&assets.join("opening.png"), &png)?;

    let parts = components.crop(crop.map(i64::from));
    let (w, h) = (parts.width as usize, parts.height as usize);
    let mut mask: Vec<bool> = parts.data.chunks_exact(4).map(|p| p[3] >= 128).collect();
    fill_holes(&mut mask, w, h);
    let loops = outlines(&mask, w, h);
    ensure!(!loops.is_empty(), "the faucet's parts left no outline");
    let mut svg = format!(
        "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{w}\" height=\"{h}\" viewBox=\"0 0 {w} {h}\" data-source-sha256=\"{:x}\">\n\
         <title>Current faucet shank, four tubes and display cable</title>\n",
        Sha256::digest(&png)
    );
    for l in &loops {
        let points: Vec<String> = l.iter().map(|p| format!("{} {}", p[0], p[1])).collect();
        let _ = writeln!(svg, "<path fill=\"none\" stroke=\"#46515b\" stroke-width=\"8.72\" d=\"M{} Z\"/>", points.join(" L"));
    }
    svg.push_str("</svg>\n");
    write(&assets.join("opening-faucet-outline.svg"), svg.as_bytes())?;
    Ok(())
}
