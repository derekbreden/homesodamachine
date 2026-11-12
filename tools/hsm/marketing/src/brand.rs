//! The brand factory renders web, app, PCB and display artwork from the checked-in identity.
use crate::{Args, draw, json, root, write};
use anyhow::{Context, Result, ensure};
use serde::Serialize;
use serde_json::{Value, json};
use std::{
    fs,
    path::{Path, PathBuf},
};
use tiny_skia::{Pixmap, Transform};

#[derive(Serialize, Clone, Copy)]
pub struct Drop {
    pub cx: f64,
    pub cy: f64,
    pub r: f64,
}
pub struct Mark {
    pub faucet: String,
    pub drop: Drop,
    pub palette: Value,
}
#[derive(Default)]
struct Style<'a> {
    background: Option<&'a str>,
    radius: f64,
    scale: Option<f64>,
    faucet: Option<&'a str>,
    drop: Option<&'a str>,
    circles: Option<Vec<Drop>>,
}
impl Mark {
    pub fn read() -> Result<Self> {
        let source = fs::read_to_string(root().join("brand/mark.svg"))?;
        let faucet = draw::tags(&source, "path").next().context("brand faucet")?;
        let drop = draw::tags(&source, "circle").next().context("brand drop")?;
        Ok(Self {
            faucet: draw::attribute(faucet, "d")?.into(),
            drop: Drop {
                cx: draw::attribute(drop, "cx")?.parse()?,
                cy: draw::attribute(drop, "cy")?.parse()?,
                r: draw::attribute(drop, "r")?.parse()?,
            },
            palette: json(root().join("brand/palette.json"))?,
        })
    }
    fn color(&self, name: &str) -> &str {
        self.palette[name].as_str().unwrap()
    }
    fn svg(&self, style: &Style) -> String {
        let mut shape = format!(
            "<path id=\"faucet\" fill=\"{}\" d=\"{}\"/>\n",
            style.faucet.unwrap_or(self.color("ice")),
            self.faucet
        );
        let circles = style
            .circles
            .as_deref()
            .unwrap_or(std::slice::from_ref(&self.drop));
        for d in circles {
            shape.push_str(&format!(
                "<circle fill=\"{}\" cx=\"{}\" cy=\"{}\" r=\"{}\"/>\n",
                style.drop.unwrap_or(self.color("orange")),
                d.cx,
                d.cy,
                d.r
            ));
        }
        if let Some(scale) = style.scale {
            shape = format!(
                "<g transform=\"translate(512 512) scale({scale}) translate(-512 -512)\">{shape}</g>\n"
            );
        }
        let background = style
            .background
            .map(|color| {
                format!(
                    "<rect width=\"1024\" height=\"1024\" rx=\"{}\" fill=\"{color}\"/>\n",
                    style.radius
                )
            })
            .unwrap_or_default();
        format!(
            "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1024 1024\" role=\"img\" aria-label=\"Home Soda Machine\">\n{background}{shape}</svg>\n"
        )
    }
    fn render(&self, style: &Style, size: u32) -> Result<Pixmap> {
        let mut pixels = Pixmap::new(size, size).context("brand image size")?;
        let s = size as f32 / 1024.;
        let transform = Transform::from_scale(s, s);
        if let Some(background) = style.background {
            draw::rect(
                &mut pixels,
                [0., 0., 1024., 1024.],
                style.radius,
                draw::rgba(background),
                transform,
            );
        }
        let transform = if let Some(scale) = style.scale {
            transform
                .pre_translate(512., 512.)
                .pre_scale(scale as f32, scale as f32)
                .pre_translate(-512., -512.)
        } else {
            transform
        };
        draw::path(
            &mut pixels,
            &draw::svg_path(&self.faucet)?.0,
            draw::rgba(style.faucet.unwrap_or(self.color("ice"))),
            transform,
        );
        for d in style
            .circles
            .as_deref()
            .unwrap_or(std::slice::from_ref(&self.drop))
        {
            draw::circle(
                &mut pixels,
                [d.cx, d.cy],
                d.r,
                draw::rgba(style.drop.unwrap_or(self.color("orange"))),
                None,
                transform,
            );
        }
        Ok(pixels)
    }
    fn wordmark(&self, stacked: bool, reverse: bool) -> Result<String> {
        let source = fs::read_to_string(root().join("brand/wordmark-lettering.svg"))?;
        let paths: Vec<_> = draw::tags(&source, "path").collect();
        ensure!(paths.len() == 2, "wordmark lettering paths");
        let color = self.color(if reverse { "ice" } else { "cobalt" });
        let text_color = self.color(if reverse { "ice" } else { "navy" });
        let mark = self.svg(&Style {
            faucet: Some(color),
            ..Default::default()
        });
        let shapes = &mark[mark.find('>').unwrap() + 1..mark.rfind("</svg>").unwrap()];
        let (dims, transform) = if stacked {
            ("0 0 1024 1000", "translate(192 -56) scale(.625)")
        } else {
            ("0 0 1680 640", "translate(0 0) scale(.625)")
        };
        let mut text = String::new();
        for (i, path) in paths.iter().enumerate() {
            let (x, y) = if stacked {
                (
                    512. - draw::attribute(path, "data-width")?.parse::<f64>()? / 2.,
                    [700., 848.][i],
                )
            } else {
                (662., [300., 475.][i])
            };
            text.push_str(&format!(
                "<path d=\"{}\" transform=\"translate({x} {y})\"/>",
                draw::attribute(path, "d")?
            ));
        }
        Ok(format!(
            "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"{dims}\" role=\"img\" aria-label=\"Home Soda Machine\">\n<g transform=\"{transform}\">{shapes}</g>\n<g fill=\"{text_color}\">{text}</g>\n</svg>\n"
        ))
    }
}
fn png(out: &Path, mark: &Mark, style: &Style, size: u32) -> Result<()> {
    write(out, mark.render(style, size)?.encode_png()?)
}
fn generated() -> &'static str {
    "hsm-marketing brand-assets"
}

pub fn build(mut args: Args) -> Result<()> {
    let preview = args.flag("--preview");
    let dest = args
        .take(&["--out-root"])
        .map(PathBuf::from)
        .unwrap_or_else(root);
    let mark = Mark::read()?;
    let cobalt = mark.color("cobalt");
    let icon = Style {
        background: Some(cobalt),
        ..Default::default()
    };
    let rounded = Style {
        background: Some(cobalt),
        radius: 192.,
        ..Default::default()
    };
    let maskable = Style {
        background: Some(cobalt),
        scale: Some(0.84),
        ..Default::default()
    };
    let public = dest.join("web/public/brand");
    for (name, svg) in [
        ("mark.svg", mark.svg(&Style::default())),
        (
            "mark-blue.svg",
            mark.svg(&Style {
                faucet: Some(cobalt),
                ..Default::default()
            }),
        ),
        (
            "mark-mono.svg",
            mark.svg(&Style {
                faucet: Some("currentColor"),
                drop: Some("currentColor"),
                ..Default::default()
            }),
        ),
        (
            "mark-white.svg",
            mark.svg(&Style {
                faucet: Some(mark.color("white")),
                drop: Some(mark.color("white")),
                ..Default::default()
            }),
        ),
        ("icon.svg", mark.svg(&rounded)),
        ("icon-square.svg", mark.svg(&icon)),
        ("wordmark.svg", mark.wordmark(false, false)?),
        ("wordmark-stacked.svg", mark.wordmark(true, false)?),
        ("wordmark-reverse.svg", mark.wordmark(false, true)?),
    ] {
        write(public.join(name), svg)?;
    }
    write(
        public.join("palette.json"),
        serde_json::to_vec_pretty(&mark.palette)?,
    )?;
    write(
        public.join("geometry.json"),
        serde_json::to_vec_pretty(
            &json!({"viewBox":[0,0,1024,1024],"faucet":mark.faucet,"drop":mark.drop}),
        )?,
    )?;
    write(dest.join("ios/AppIcon.svg"), mark.svg(&icon))?;
    let composer = dest.join("ios/SodaMachine/SodaMachine/AppIcon.icon");
    for (name, shape) in [
        (
            "faucet",
            format!(
                "<path fill=\"{}\" d=\"{}\"/>",
                mark.color("ice"),
                mark.faucet
            ),
        ),
        (
            "drop",
            format!(
                "<circle fill=\"{}\" cx=\"{}\" cy=\"{}\" r=\"{}\"/>",
                mark.color("orange"),
                mark.drop.cx,
                mark.drop.cy,
                mark.drop.r
            ),
        ),
    ] {
        write(
            composer.join(format!("Assets/{name}.svg")),
            format!(
                "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1024\" height=\"1024\" viewBox=\"0 0 1024 1024\">\n{shape}\n</svg>\n"
            ),
        )?;
    }
    let mut spec = json(root().join("ios/SodaMachine/SodaMachine/AppIcon.icon/icon.json"))?;
    let color = draw::rgba(cobalt);
    spec["fill"] = json!({"solid":format!("srgb:{:.5},{:.5},{:.5},1.00000",color.red(),color.green(),color.blue())});
    write(
        composer.join("icon.json"),
        serde_json::to_vec_pretty(&spec)?,
    )?;
    let assets = dest.join("ios/SodaMachine/SodaMachine/Assets.xcassets");
    png(
        &assets.join("LaunchIcon.imageset/LaunchIcon.png"),
        &mark,
        &Style::default(),
        1024,
    )?;
    let hex = cobalt.trim_start_matches('#');
    write(
        assets.join("LaunchBackground.colorset/Contents.json"),
        serde_json::to_vec_pretty(
            &json!({"colors":[{"color":{"color-space":"srgb","components":{"red":format!("0x{}",&hex[0..2]),"green":format!("0x{}",&hex[2..4]),"blue":format!("0x{}",&hex[4..6]),"alpha":"1.000"}},"idiom":"universal"}],"info":{"author":"xcode","version":1}}),
        )?,
    )?;
    let pwa = dest.join("web/public/pwa-icons");
    for size in [192, 512] {
        png(&pwa.join(format!("icon-{size}.png")), &mark, &icon, size)?;
    }
    png(&pwa.join("icon-512-maskable.png"), &mark, &maskable, 512)?;
    for size in [152, 167, 180] {
        png(
            &pwa.join(format!("apple-touch-icon-{size}.png")),
            &mark,
            &icon,
            size,
        )?;
    }
    for size in [32, 64] {
        png(
            &pwa.join(format!("favicon-{size}.png")),
            &mark,
            &rounded,
            size,
        )?;
    }
    for (name, style) in [
        ("icon-1024.png", &rounded),
        ("avatar-1024.png", &maskable),
        ("mark-1024.png", &Style::default()),
        (
            "mark-blue-1024.png",
            &Style {
                faucet: Some(cobalt),
                ..Default::default()
            },
        ),
    ] {
        png(&public.join(name), &mark, style, 1024)?;
    }
    let d = mark.drop;
    let contour = draw::svg_path(&mark.faucet)?.1;
    let min = |axis: usize| {
        contour
            .iter()
            .map(|p| p[axis])
            .fold(f64::INFINITY, f64::min)
    };
    let max = |axis: usize| {
        contour
            .iter()
            .map(|p| p[axis])
            .fold(f64::NEG_INFINITY, f64::max)
    };
    let geometry = json!({"faucet":contour,"drop":d,"bounds":{"left":min(0).min(d.cx-d.r),"top":min(1).min(d.cy-d.r),"right":max(0).max(d.cx+d.r),"bottom":max(1).max(d.cy+d.r)}});
    write(
        dest.join("hardware/pcb/pcba/logo-geometry.ts"),
        format!(
            "/** Generated from brand/mark.svg by {}. */\nexport const logoGeometry = {} as const\n",
            generated(),
            serde_json::to_string(&geometry)?
        ),
    )?;
    if preview {
        preview_sheet(&dest, &mark)?;
    }
    println!("Brand exports: {}", dest.display());
    Ok(())
}

fn preview_sheet(dest: &Path, mark: &Mark) -> Result<()> {
    let mut pixels = Pixmap::new(1440, 1000).unwrap();
    pixels.fill(draw::rgba("#F3F6FF"));
    let font = draw::Typeface::new(Path::new("/System/Library/Fonts/Supplemental/Arial.ttf"), 0)?;
    font.center(
        &mut pixels,
        "Home Soda Machine / On tap",
        28.,
        0.,
        [380., 55.],
        0.,
        draw::rgba(mark.color("navy")),
        Transform::identity(),
    );
    for (x, y, size, style, label) in [
        (
            64,
            125,
            480,
            Style {
                background: Some(mark.color("cobalt")),
                radius: 192.,
                ..Default::default()
            },
            "App icon",
        ),
        (
            640,
            125,
            360,
            Style {
                faucet: Some(mark.color("cobalt")),
                ..Default::default()
            },
            "Full color mark",
        ),
        (
            1070,
            165,
            256,
            Style {
                faucet: Some(mark.color("navy")),
                drop: Some(mark.color("navy")),
                ..Default::default()
            },
            "One color",
        ),
    ] {
        let art = mark.render(&style, size)?;
        pixels.draw_pixmap(
            x,
            y,
            art.as_ref(),
            &Default::default(),
            Transform::identity(),
            None,
        );
        font.center(
            &mut pixels,
            label,
            20.,
            0.,
            [x as f64 + size as f64 / 2., y as f64 + size as f64 + 40.],
            0.,
            draw::rgba(mark.color("navy")),
            Transform::identity(),
        );
    }
    let mut x = 64;
    for size in [180, 64, 48, 32, 16] {
        let art = mark.render(
            &Style {
                background: Some(mark.color("cobalt")),
                radius: 192.,
                ..Default::default()
            },
            size,
        )?;
        pixels.draw_pixmap(
            x,
            720,
            art.as_ref(),
            &Default::default(),
            Transform::identity(),
            None,
        );
        x += (size as i32 + 40).max(100);
    }
    for (i, name) in ["cobalt", "navy", "ice", "orange", "white"]
        .iter()
        .enumerate()
    {
        let x = 875. + i as f64 * 92.;
        draw::rect(
            &mut pixels,
            [x, 730., 68., 68.],
            10.,
            draw::rgba(mark.color(name)),
            Transform::identity(),
        );
        font.center(
            &mut pixels,
            name,
            20.,
            0.,
            [x + 34., 830.],
            0.,
            draw::rgba(mark.color("navy")),
            Transform::identity(),
        );
    }
    write(dest.join("brand/preview.png"), pixels.encode_png()?)
}

fn smoothstep(t: f64) -> f64 {
    let t = t.clamp(0., 1.);
    t * t * (3. - 2. * t)
}
fn circles(mark: &Mark, frame: usize, variant: &str) -> Vec<Drop> {
    let t = frame as f64 / 16.;
    let pulse = (1. - (std::f64::consts::TAU * t).cos()) / 2.;
    let mut d = mark.drop;
    match variant {
        "pulse" => {
            d.cy += 16. * pulse;
            d.r += 6. * pulse;
            vec![d]
        }
        "float" => {
            d.cy += 36. * pulse;
            vec![d]
        }
        _ => {
            if frame == 0 {
                return vec![d];
            }
            let handoff = smoothstep((t - 0.625) / 0.375);
            let radius = d.r;
            let top = d.cy - radius;
            d.cy += 192. * smoothstep(t / 0.875);
            d.r = radius * (1. - handoff).sqrt();
            let mut out = vec![d];
            if handoff > 0. {
                let r = radius * handoff.sqrt();
                out.push(Drop {
                    cx: d.cx,
                    cy: top + r,
                    r,
                });
            }
            out
        }
    }
}
pub fn animation(mut args: Args) -> Result<()> {
    let from_svg = args.flag("--from-svg");
    let dest = args
        .take(&["--out-root"])
        .map(PathBuf::from)
        .unwrap_or_else(root);
    let mark = Mark::read()?;
    for variant in ["fall", "pulse", "float"] {
        let output = dest.join(format!("web/public/brand/motion/{variant}.png"));
        if variant == "fall" && !from_svg {
            write(
                &output,
                fs::read(root().join(hsm_display_assets::ANIMATION_SOURCE))?,
            )?;
            continue;
        }
        let mut sprite = Pixmap::new(360 * 16, 360).unwrap();
        for frame in 0..16 {
            let pixels = mark.render(
                &Style {
                    background: Some(mark.color("cobalt")),
                    circles: Some(circles(&mark, frame, variant)),
                    ..Default::default()
                },
                360,
            )?;
            let rgb = pixels
                .pixels()
                .iter()
                .flat_map(|p| [p.red(), p.green(), p.blue()])
                .collect::<Vec<_>>();
            let packed = hsm_display_assets::pack_rgb565(&rgb)?;
            let decoded = hsm_display_assets::decode_rgb565(360, 360, &packed)?;
            let mut preview = Pixmap::new(360, 360).unwrap();
            for (pixel, rgb) in preview
                .pixels_mut()
                .iter_mut()
                .zip(decoded.rgb.chunks_exact(3))
            {
                *pixel = tiny_skia::PremultipliedColorU8::from_rgba(rgb[0], rgb[1], rgb[2], 255)
                    .unwrap();
            }
            sprite.draw_pixmap(
                (frame * 360) as i32,
                0,
                preview.as_ref(),
                &Default::default(),
                Transform::identity(),
                None,
            );
        }
        let png = sprite.encode_png()?;
        if variant == "fall" {
            write(dest.join(hsm_display_assets::ANIMATION_SOURCE), &png)?;
        }
        write(&output, &png)?;
    }
    write(
        dest.join("web/public/brand/motion.html"),
        fs::read(root().join("brand/motion.html"))?,
    )?;
    println!("Animation exports: {}", dest.display());
    Ok(())
}
