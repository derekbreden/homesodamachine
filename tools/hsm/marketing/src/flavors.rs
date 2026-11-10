//! The flavor factory draws the display and demo app's source portraits with native font outlines.
use crate::{Args, draw, root, write};
use anyhow::{Context, Result};
use std::{
    f64::consts::{PI, TAU},
    path::{Path, PathBuf},
};
use tiny_skia::{Color, Pixmap, Transform};

const MASTER: u32 = 512;
const SCALE: f64 = 1.5;
fn font(name: &str) -> Result<draw::Typeface> {
    let (file, index) = match name {
        "didot" => ("Didot.ttc", 2),
        "copperplate" => ("Copperplate.ttc", 2),
        "futura" => ("Futura.ttc", 2),
        "futura_xb" => ("Futura.ttc", 4),
        "rounded" => ("Arial Rounded Bold.ttf", 0),
        "phosphate" => ("Phosphate.ttc", 1),
        _ => ("Phosphate.ttc", 0),
    };
    draw::Typeface::new(
        &Path::new("/System/Library/Fonts/Supplemental").join(file),
        index,
    )
}
fn color(hex: &str, alpha: u8) -> Color {
    let c = draw::rgba(hex);
    Color::from_rgba(c.red(), c.green(), c.blue(), alpha as f32 / 255.).unwrap()
}
fn transform() -> Transform {
    Transform::from_scale(SCALE as f32, SCALE as f32)
}
fn gradient(center: [f64; 2], end: [f64; 2], radius: Option<f64>, stops: [&str; 3]) -> Pixmap {
    let mut pixels = Pixmap::new(MASTER * 3, MASTER * 3).unwrap();
    let colors = stops.map(draw::rgba);
    let d = [end[0] - center[0], end[1] - center[1]];
    for y in 0..pixels.height() {
        for x in 0..pixels.width() {
            let v = [x as f64 - center[0], y as f64 - center[1]];
            let t = radius
                .map_or_else(
                    || (v[0] * d[0] + v[1] * d[1]) / (d[0] * d[0] + d[1] * d[1]),
                    |r| v[0].hypot(v[1]) / r,
                )
                .clamp(0., 1.)
                * 2.;
            let i = (t.floor() as usize).min(1);
            let f = (t - i as f64) as f32;
            let rgb = |a: f32, b: f32| ((a + (b - a) * f) * 255.) as u8;
            pixels.pixels_mut()[(y * MASTER * 3 + x) as usize] =
                tiny_skia::PremultipliedColorU8::from_rgba(
                    rgb(colors[i].red(), colors[i + 1].red()),
                    rgb(colors[i].green(), colors[i + 1].green()),
                    rgb(colors[i].blue(), colors[i + 1].blue()),
                    255,
                )
                .unwrap();
        }
    }
    pixels
}
fn vignette(pixels: &mut Pixmap, strength: f64) {
    let width = pixels.width();
    let half = width as f64 / 2.;
    for y in 0..width {
        for x in 0..width {
            let d = (x as f64 - half).hypot(y as f64 - half) / half;
            let a = ((((d - 0.55) / 0.45).clamp(0., 1.).powf(1.6) * strength * 255.) as u8) as f64
                / 255.;
            let i = (y * width + x) as usize;
            let p = pixels.pixels()[i];
            let alpha = a + (p.alpha() as f64 / 255.) * (1. - a);
            let channel = |v: u8| {
                if alpha > 0. {
                    (v as f64 * (1. - a) / alpha).min(255.) as u8
                } else {
                    0
                }
            };
            pixels.pixels_mut()[i] = tiny_skia::PremultipliedColorU8::from_rgba(
                channel(p.red()),
                channel(p.green()),
                channel(p.blue()),
                255,
            )
            .unwrap();
        }
    }
}
fn ring(pixels: &mut Pixmap, c: [f64; 2], r: f64, width: f64, col: Color) {
    if let Some(path) = tiny_skia::PathBuilder::from_circle(c[0] as f32, c[1] as f32, r as f32) {
        draw::source_path(pixels, &path, col, Some(width), transform());
    }
}
fn source_poly(pixels: &mut Pixmap, points: &[[f64; 2]], color: Color, width: Option<f64>) {
    let mut path = tiny_skia::PathBuilder::new();
    path.move_to(points[0][0] as f32, points[0][1] as f32);
    for point in &points[1..] {
        path.line_to(point[0] as f32, point[1] as f32);
    }
    if points.len() > 2 {
        path.close();
    }
    if let Some(path) = path.finish() {
        draw::source_path(pixels, &path, color, width, transform());
    }
}
fn star(pixels: &mut Pixmap, c: [f64; 2], r: f64, col: Color) {
    let [x, y] = c;
    let w = r * 0.3;
    source_poly(
        pixels,
        &[
            [x, y - r],
            [x + w, y - w],
            [x + r, y],
            [x + w, y + w],
            [x, y + r],
            [x - w, y + w],
            [x - r, y],
            [x - w, y - w],
        ],
        col,
        None,
    );
}
fn text(
    pixels: &mut Pixmap,
    value: &str,
    face: &str,
    size: f64,
    tracking: f64,
    center: [f64; 2],
    rotate: f64,
    col: Color,
    shadow: Option<(&str, u8, f64, [f64; 2])>,
) -> Result<()> {
    let font = font(face)?;
    if let Some((hex, alpha, blur, offset)) = shadow {
        let mut mask = Pixmap::new(pixels.width(), pixels.height()).unwrap();
        font.center(
            &mut mask,
            value,
            size / SCALE,
            tracking / SCALE,
            [center[0] + offset[0], center[1] + offset[1]],
            rotate,
            color(hex, alpha),
            transform(),
        );
        draw::blur(&mut mask, blur * SCALE);
        pixels.draw_pixmap(
            0,
            0,
            mask.as_ref(),
            &Default::default(),
            Transform::identity(),
            None,
        );
    }
    font.center(
        pixels,
        value,
        size / SCALE,
        tracking / SCALE,
        center,
        rotate,
        col,
        transform(),
    );
    Ok(())
}

fn arc_text(
    pixels: &mut Pixmap,
    value: &str,
    face: &str,
    size: f64,
    radius: f64,
    col: Color,
    flip: bool,
    gap: f64,
) -> Result<()> {
    let font = font(face)?;
    let angles: Vec<_> = value
        .chars()
        .map(|c| font.width(&c.to_string(), size / SCALE, 0.) / radius + gap.to_radians())
        .collect();
    let span: f64 = angles.iter().sum();
    let mut angle = if flip {
        PI / 2. + span / 2.
    } else {
        -PI / 2. - span / 2.
    };
    for (c, da) in value.chars().zip(angles) {
        let middle = if flip {
            angle - da / 2.
        } else {
            angle + da / 2.
        };
        let center = [512. + radius * middle.cos(), 512. + radius * middle.sin()];
        let rotate = if flip {
            -(middle.to_degrees() - 90.)
        } else {
            -(middle.to_degrees() + 90.)
        };
        font.center(
            pixels,
            &c.to_string(),
            size / SCALE,
            0.,
            center,
            rotate,
            col,
            transform(),
        );
        angle += if flip { -da } else { da };
    }
    Ok(())
}
pub fn design(n: usize) -> Result<Pixmap> {
    let mut pixels = match n {
        0 => gradient(
            [430., 380.],
            [0., 0.],
            Some(760.),
            ["#ff7a6b", "#e0314f", "#7d1330"],
        ),
        1 => gradient(
            [120., 120.],
            [920., 940.],
            None,
            ["#e6fb8a", "#74d64f", "#0d9a5f"],
        ),
        2 => gradient(
            [512., 470.],
            [0., 0.],
            Some(720.),
            ["#ffe07a", "#ff9e2c", "#e8531f"],
        ),
        _ => gradient(
            [512., 460.],
            [0., 0.],
            Some(760.),
            ["#9a80f0", "#5d39b8", "#220a42"],
        ),
    };
    match n {
        0 => {
            let cream = color("#ffe9c9", 255);
            ring(&mut pixels, [512., 512.], 470., 3., color("#ffe9c9", 90));
            ring(&mut pixels, [512., 512.], 452., 9., cream);
            ring(&mut pixels, [512., 512.], 434., 3., color("#ffe9c9", 120));
            arc_text(
                &mut pixels,
                "FLAVOR",
                "copperplate",
                74.,
                392.,
                cream,
                false,
                3.,
            )?;
            arc_text(
                &mut pixels,
                "ORIGINAL",
                "copperplate",
                52.,
                392.,
                color("#ffe9c9", 225),
                true,
                4.,
            )?;
            for angle in [0., PI] {
                star(
                    &mut pixels,
                    [512. + 392. * angle.cos(), 512. + 392. * angle.sin()],
                    14.,
                    cream,
                );
            }
            text(
                &mut pixels,
                "1",
                "didot",
                500.,
                0.,
                [512., 512.],
                0.,
                cream,
                Some(("#3c0618", 150, 7., [0., 5.])),
            )?;
            vignette(&mut pixels, 0.45);
        }
        1 => {
            ring(&mut pixels, [812., 812.], 132., 6., color("white", 55));
            for i in 0..8 {
                let a = i as f64 / 8. * TAU;
                source_poly(
                    &mut pixels,
                    &[[812., 812.], [812. + 132. * a.cos(), 812. + 132. * a.sin()]],
                    color("white", 45),
                    Some(3.),
                );
            }
            for (x, y, r) in [(250., 250., 30.), (800., 250., 18.), (235., 815., 15.)] {
                star(&mut pixels, [x, y], r, color("white", 235));
            }
            for (x, y, r, a) in [(360., 650., 22., 90), (700., 470., 16., 80)] {
                ring(&mut pixels, [x, y], r, 5., color("white", a));
            }
            text(
                &mut pixels,
                "FLAVOR",
                "futura",
                92.,
                18.,
                [470., 372.],
                7.,
                color("white", 255),
                Some(("#0a461e", 150, 6., [0., 5.])),
            )?;
            text(
                &mut pixels,
                "2",
                "futura_xb",
                580.,
                0.,
                [520., 600.],
                7.,
                color("white", 255),
                Some(("#0a461e", 150, 6., [0., 5.])),
            )?;
            vignette(&mut pixels, 0.26);
        }
        2 => {
            for i in (0..24).step_by(2) {
                let a = i as f64 / 24. * TAU;
                let b = (i + 1) as f64 / 24. * TAU;
                draw::polygon(
                    &mut pixels,
                    &[
                        [512., 545.],
                        [512. + 780. * a.cos(), 545. + 780. * a.sin()],
                        [512. + 780. * b.cos(), 545. + 780. * b.sin()],
                    ],
                    color("white", 34),
                    None,
                    transform(),
                );
            }
            let face = font("rounded")?;
            let width = face.width("FLAVOR", 66. / SCALE, 10. / SCALE);
            let height = 66. / SCALE;
            draw::rect(
                &mut pixels,
                [
                    512. - (width + height) / 2.,
                    348. - height * 0.75,
                    width + height,
                    height * 1.5,
                ],
                height * 0.75,
                color("white", 255),
                transform(),
            );
            text(
                &mut pixels,
                "FLAVOR",
                "rounded",
                66.,
                10.,
                [512., 348.],
                0.,
                color("#e4541a", 255),
                None,
            )?;
            text(
                &mut pixels,
                "3",
                "rounded",
                540.,
                0.,
                [512., 605.],
                0.,
                color("white", 255),
                Some(("#963700", 160, 7., [0., 6.])),
            )?;
            vignette(&mut pixels, 0.30);
        }
        _ => {
            draw::polygon(
                &mut pixels,
                &[[512., 152.], [872., 512.], [512., 872.], [152., 512.]],
                color("#eee7ff", 110),
                Some(2.5),
                transform(),
            );
            for (x, y, r) in [
                (512., 140., 15.),
                (250., 512., 11.),
                (774., 512., 11.),
                (385., 882., 8.),
                (642., 884., 10.),
            ] {
                star(&mut pixels, [x, y], r, color("white", 220));
            }
            text(
                &mut pixels,
                "FLAVOR",
                "phosphate",
                76.,
                18.,
                [512., 372.],
                0.,
                color("#eee7ff", 255),
                Some(("#0a041e", 160, 8., [0., 6.])),
            )?;
            for (a, b) in [(150., 286.), (738., 874.)] {
                source_poly(
                    &mut pixels,
                    &[[a, 372.], [b, 372.]],
                    color("#eee7ff", 150),
                    Some(2.),
                );
            }
            text(
                &mut pixels,
                "4",
                "phosphate_in",
                540.,
                0.,
                [512., 600.],
                0.,
                color("white", 255),
                Some(("#0a041e", 160, 8., [0., 6.])),
            )?;
            vignette(&mut pixels, 0.40);
        }
    }
    draw::resized(&pixels, MASTER, MASTER)
}
pub fn build(mut args: Args) -> Result<()> {
    let preview = args.flag("--preview");
    let dest = args
        .take(&["--out-root"])
        .map(PathBuf::from)
        .unwrap_or_else(root);
    let mut masters = Vec::new();
    for n in 0..4 {
        let pixels = design(n)?;
        write(
            dest.join(format!("images/flavor_{}.png", n + 1)),
            pixels.encode_png()?,
        )?;
        masters.push(pixels);
    }
    if preview {
        let mut sheet = Pixmap::new(528, 1128).context("flavor preview")?;
        sheet.fill(draw::rgba("#0c0c14"));
        for (i, master) in masters.iter().enumerate() {
            let square = draw::resized(master, 240, 240)?;
            let mut circle = square.clone();
            for y in 0..240 {
                for x in 0..240 {
                    if (x as f64 - 119.5).hypot(y as f64 - 119.5) > 120. {
                        circle.pixels_mut()[(y * 240 + x) as usize] =
                            tiny_skia::PremultipliedColorU8::from_rgba(26, 26, 46, 255).unwrap();
                    }
                }
            }
            for (x, pixels) in [(16, &square), (272, &circle)] {
                sheet.draw_pixmap(
                    x,
                    38 + i as i32 * 278,
                    pixels.as_ref(),
                    &Default::default(),
                    Transform::identity(),
                    None,
                );
            }
        }
        write(dest.join("tools/flavor_preview.png"), sheet.encode_png()?)?;
    }
    println!("Flavor portraits: {}", dest.join("images").display());
    Ok(())
}
