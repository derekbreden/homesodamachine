//! The editor assembles range and freeze cuts, then applies authored overlays and sound cues.
use super::{Scratch, cuts};
use crate::{Args, draw, json, output, run, write};
use anyhow::{Context, Result, bail, ensure};
use serde::Deserialize;
use std::{path::Path, process::Command};
use tiny_skia::{Pixmap, Transform};

#[derive(Deserialize)]
#[serde(untagged)]
enum Position {
    Name(String),
    Point([f64; 2]),
}
#[derive(Deserialize)]
#[serde(untagged)]
enum Size {
    Text(f64),
    Image([f64; 2]),
}
#[derive(Deserialize, Clone, Copy, PartialEq)]
#[serde(rename_all = "snake_case")]
enum Kind {
    Text,
    Stamp,
    LowerThird,
    Hud,
    Box,
    Pip,
    Magnifier,
    Arrow,
    Param,
    Title,
}
#[derive(Deserialize)]
struct Overlay {
    #[serde(rename = "type")]
    kind: Kind,
    t: [f64; 2],
    #[serde(default)]
    fade: Option<f64>,
    #[serde(default)]
    position: Option<Position>,
    #[serde(default)]
    size: Option<Size>,
    #[serde(default)]
    text: String,
    #[serde(default)]
    primary: String,
    #[serde(default)]
    secondary: String,
    #[serde(default)]
    label: String,
    #[serde(default)]
    value: String,
    #[serde(default)]
    note: String,
    #[serde(default)]
    subtitle: String,
    #[serde(default)]
    color: Option<String>,
    #[serde(default)]
    bg: Option<String>,
    #[serde(default)]
    bg_alpha: Option<f64>,
    #[serde(default)]
    border: Option<serde_json::Value>,
    #[serde(default)]
    border_w: Option<f64>,
    #[serde(default)]
    accent_color: Option<String>,
    #[serde(default)]
    text_size: Option<f64>,
    #[serde(default)]
    subtitle_size: Option<f64>,
    #[serde(default)]
    primary_size: Option<f64>,
    #[serde(default)]
    secondary_size: Option<f64>,
    #[serde(default)]
    row_size: Option<f64>,
    #[serde(default)]
    rows: Vec<[String; 2]>,
    #[serde(default)]
    label_col_w: Option<f64>,
    #[serde(default)]
    label_color: Option<String>,
    #[serde(default)]
    value_color: Option<String>,
    #[serde(default)]
    rect: Option<[f64; 4]>,
    #[serde(default)]
    source_rect: Option<[f64; 4]>,
    #[serde(default)]
    dest_rect: Option<[f64; 4]>,
    #[serde(default)]
    source: Option<String>,
    #[serde(default, rename = "from")]
    from: Option<[f64; 2]>,
    #[serde(default)]
    to: Option<[f64; 2]>,
    #[serde(default)]
    thickness: Option<f64>,
    #[serde(default)]
    arrowhead_size: Option<f64>,
}
#[derive(Deserialize)]
struct Sound {
    file: String,
    t: f64,
    #[serde(default = "one")]
    volume: f64,
    #[serde(default)]
    fade_in: f64,
    #[serde(default)]
    fade_out: f64,
}
fn one() -> f64 {
    1.
}
#[derive(Deserialize)]
struct Sidecar {
    #[serde(default)]
    default_font: Option<String>,
    #[serde(default)]
    overlays: Vec<Overlay>,
    #[serde(default)]
    sounds: Vec<Sound>,
}
fn escape(text: &str) -> String {
    text.replace('\\', "\\\\")
        .replace(':', "\\:")
        .replace('\'', "’")
        .replace('\n', "\\n")
}
fn filter_path(path: &str) -> String {
    escape(path).replace('[', "\\[").replace(']', "\\]")
}
fn probe(path: &str) -> Result<(u32, u32, String)> {
    let out = output(Command::new("ffprobe").args([
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate",
        "-of",
        "json",
        path,
    ]))?;
    let meta: serde_json::Value = serde_json::from_slice(&out.stdout)?;
    let stream = &meta["streams"][0];
    Ok((
        stream["width"].as_u64().context("video width")? as u32,
        stream["height"].as_u64().context("video height")? as u32,
        stream["r_frame_rate"]
            .as_str()
            .context("video frame rate")?
            .into(),
    ))
}
fn duration(path: &str) -> Result<f64> {
    let out = output(Command::new("ffprobe").args([
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        path,
    ]))?;
    Ok(std::str::from_utf8(&out.stdout)?.trim().parse()?)
}
fn encode(cmd: &mut Command, preset: &str, crf: f64) {
    cmd.args([
        "-c:v",
        "libx264",
        "-preset",
        preset,
        "-crf",
        &format!("{crf}"),
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-loglevel",
        "error",
    ]);
}
fn position(
    pos: Option<&Position>,
    default: &str,
    w: f64,
    h: f64,
    ow: f64,
    oh: f64,
    margin: f64,
) -> Result<[f64; 2]> {
    if let Some(Position::Point(p)) = pos {
        return Ok(*p);
    }
    let name = match pos {
        Some(Position::Name(n)) => n.as_str(),
        _ => default,
    };
    let x = if name.contains("left") {
        margin
    } else if name.contains("right") {
        w - ow - margin
    } else if name == "center" || name.contains("center") {
        (w - ow) / 2.
    } else {
        bail!("unknown position {name}");
    };
    let y = if name.starts_with("top") {
        margin
    } else if name.starts_with("bottom") {
        h - oh - margin
    } else {
        (h - oh) / 2.
    };
    Ok([x, y])
}
fn anchored(pos: Option<&Position>, default: &str) -> Result<(String, String)> {
    if let Some(Position::Point(p)) = pos {
        return Ok((p[0].to_string(), p[1].to_string()));
    }
    let name = match pos {
        Some(Position::Name(n)) => n.as_str(),
        _ => default,
    };
    let x = if name.contains("left") {
        "40"
    } else if name.contains("right") {
        "w-text_w-40"
    } else {
        "(w-text_w)/2"
    };
    let y = if name.starts_with("top") {
        "40"
    } else if name.starts_with("bottom") {
        "h-text_h-40"
    } else {
        "(h-text_h)/2"
    };
    Ok((x.into(), y.into()))
}
fn text_filter(
    text: &str,
    size: f64,
    color: &str,
    font: &str,
    x: &str,
    y: &str,
    entry: &Overlay,
    border: f64,
) -> String {
    let [start, end] = entry.t;
    let fade = entry.fade.unwrap_or(0.25);
    let alpha = if fade > 0. {
        format!(":alpha='min(1\\,min((t-{start})/{fade}\\,({end}-t)/{fade}))'")
    } else {
        String::new()
    };
    format!(
        "drawtext=expansion=none:text='{}':font='{}':fontsize={size}:fontcolor={color}:bordercolor=black:borderw={border}:x={x}:y={y}:enable='between(t\\,{start}\\,{end})'{alpha}",
        escape(text),
        escape(font)
    )
}
fn panel(entry: &Overlay, width: u32, height: u32) -> Result<Pixmap> {
    let title = entry.kind == Kind::Title;
    let mut pixels = Pixmap::new(width, height).context("overlay dimensions")?;
    let path = Path::new("/System/Library/Fonts/Avenir Next.ttc");
    let font = |index| {
        draw::Typeface::new(path, index).or_else(|_| {
            draw::Typeface::new(
                Path::new("/System/Library/Fonts/Helvetica.ttc"),
                if index == 2 {
                    1
                } else if index == 4 {
                    2
                } else {
                    0
                },
            )
        })
    };
    let large = font(2)?;
    let small = font(4)?;
    let label = font(5)?;
    let (heading, value, note) = if title {
        ("", entry.text.as_str(), entry.subtitle.as_str())
    } else {
        (
            entry.label.as_str(),
            entry.value.as_str(),
            entry.note.as_str(),
        )
    };
    let size = entry.text_size.unwrap_or(if title { 100. } else { 88. });
    let note_size = entry.subtitle_size.unwrap_or(if title { 38. } else { 26. });
    let stripe = if title { 12. } else { 8. };
    let pad = if title { 56. } else { 32. };
    let inset = if title { 48. } else { 36. };
    let content = large
        .width(value, size, 0.)
        .max(small.width(note, note_size, 0.))
        .max(label.width(heading, 28., 0.));
    let mut pw = stripe + inset + content + pad;
    if title {
        pw = pw
            .min(width as f64 - 240.)
            .max(800.)
            .min(width as f64 - 80.);
    }
    let ph = pad * 2.
        + size * 1.35
        + if title { 0. } else { 28. * 1.35 + 16. }
        + if note.is_empty() {
            0.
        } else {
            16. + note_size * 1.35
        };
    let margin = if title { 140. } else { 60. };
    let [x, y] = position(
        entry.position.as_ref(),
        if title { "bottom-center" } else { "left-mid" },
        width as f64,
        height as f64,
        pw,
        ph,
        margin,
    )?;
    let transform = Transform::identity();
    draw::rect(
        &mut pixels,
        [x - 8., y + 6., pw + 16., ph + 8.],
        22.,
        draw::rgba("#00000065"),
        transform,
    );
    draw::blur(&mut pixels, if title { 16. } else { 14. });
    draw::rect(
        &mut pixels,
        [x, y, pw, ph],
        if title { 12. } else { 10. },
        draw::rgba(if title { "#0a0a0af0" } else { "#0c0c0ceb" }),
        transform,
    );
    draw::rect(
        &mut pixels,
        [x, y, stripe, ph],
        0.,
        draw::rgba(entry.accent_color.as_deref().unwrap_or("#ff7a2d")),
        transform,
    );
    let tx = x + stripe + inset;
    let mut cy = y + pad;
    if !title {
        let heading = heading.to_uppercase();
        label.center(
            &mut pixels,
            &heading,
            28.,
            0.,
            [tx + label.width(&heading, 28., 0.) / 2., cy + 28. * 0.7],
            0.,
            draw::rgba("#a0a0a0"),
            transform,
        );
        cy += 28. * 1.35 + 16.;
    }
    large.center(
        &mut pixels,
        value,
        size,
        0.,
        [tx + large.width(value, size, 0.) / 2., cy + size * 0.7],
        0.,
        draw::rgba("white"),
        transform,
    );
    if !note.is_empty() {
        cy += size * 1.35 + 16.;
        small.center(
            &mut pixels,
            note,
            note_size,
            0.,
            [
                tx + small.width(note, note_size, 0.) / 2.,
                cy + note_size * 0.7,
            ],
            0.,
            draw::rgba("#aaaaaa"),
            transform,
        );
    }
    Ok(pixels)
}
fn arrow(entry: &Overlay, width: u32, height: u32) -> Result<Pixmap> {
    let mut pixels = Pixmap::new(width, height).context("arrow dimensions")?;
    let a = entry.from.context("arrow from")?;
    let b = entry.to.context("arrow to")?;
    let dx = b[0] - a[0];
    let dy = b[1] - a[1];
    let len = dx.hypot(dy);
    ensure!(len > 0., "arrow has no length");
    let u = [dx / len, dy / len];
    let head = entry.arrowhead_size.unwrap_or(30.);
    let base = [b[0] - u[0] * head, b[1] - u[1] * head];
    let color = draw::rgba(entry.color.as_deref().unwrap_or("yellow"));
    draw::polygon(
        &mut pixels,
        &[a, base],
        color,
        Some(entry.thickness.unwrap_or(6.)),
        Transform::identity(),
    );
    draw::polygon(
        &mut pixels,
        &[
            b,
            [base[0] - u[1] * head * 0.5, base[1] + u[0] * head * 0.5],
            [base[0] + u[1] * head * 0.5, base[1] - u[0] * head * 0.5],
        ],
        color,
        None,
        Transform::identity(),
    );
    Ok(pixels)
}

pub fn overlays(mut args: Args) -> Result<()> {
    let captions = args.take(&["--captions"]);
    let preset = args.take(&["--preset"]).unwrap_or_else(|| "medium".into());
    let crf = args.number(&["--crf"], 18.)?;
    let dry = args.flag("--dry-run");
    render_overlays(
        args.positional(0)?,
        Path::new(args.positional(1)?),
        args.positional(2)?,
        captions.as_deref(),
        &preset,
        crf,
        dry,
    )
}
fn render_overlays(
    source: &str,
    sidecar: &Path,
    out: &str,
    captions: Option<&str>,
    preset: &str,
    crf: f64,
    dry: bool,
) -> Result<()> {
    let data: Sidecar = serde_json::from_value(json(sidecar)?)?;
    let parent = sidecar.parent().unwrap_or(Path::new("."));
    let (width, height, _) = probe(source)?;
    let scratch = Scratch::new(out, false)?;
    let mut command = Command::new("ffmpeg");
    command.args(["-y", "-i", source]);
    let mut filters = Vec::new();
    let mut current = "0:v".to_string();
    let mut input = 1;
    let font = data.default_font.as_deref().unwrap_or("Helvetica");
    for (i, entry) in data.overlays.iter().enumerate() {
        ensure!(entry.t[1] > entry.t[0], "overlay has nonpositive duration");
        let next = format!("v{i}");
        let [start, end] = entry.t;
        let mut drawlike = Vec::new();
        match entry.kind {
            Kind::Text | Kind::Stamp => {
                let (x, y) = anchored(
                    entry.position.as_ref(),
                    if entry.kind == Kind::Stamp {
                        "center"
                    } else {
                        "top-left"
                    },
                )?;
                let size = match entry.size {
                    Some(Size::Text(n)) => n,
                    _ => {
                        if entry.kind == Kind::Stamp {
                            200.
                        } else {
                            56.
                        }
                    }
                };
                let mut text = text_filter(
                    &entry.text,
                    size,
                    entry.color.as_deref().unwrap_or("white"),
                    font,
                    &x,
                    &y,
                    entry,
                    if entry.border.as_ref().and_then(|b| b.as_bool()) == Some(false) {
                        0.
                    } else {
                        4.
                    },
                );
                if let Some(bg) = &entry.bg {
                    text.push_str(&format!(
                        ":box=1:boxcolor={bg}@{}:boxborderw=40",
                        entry.bg_alpha.unwrap_or(0.85)
                    ));
                }
                drawlike.push(text);
            }
            Kind::LowerThird => {
                let (x, _) = anchored(entry.position.as_ref(), "bottom-left")?;
                let size = entry.primary_size.unwrap_or(64.);
                let bottom = match &entry.position {
                    Some(Position::Name(p)) => p.starts_with("bottom"),
                    _ => true,
                };
                let y = if bottom {
                    format!("h-text_h-{}", 40. + size * 1.15)
                } else {
                    "40".into()
                };
                drawlike.push(text_filter(
                    &entry.primary,
                    size,
                    "white",
                    font,
                    &x,
                    &y,
                    entry,
                    4.,
                ));
                if !entry.secondary.is_empty() {
                    let y = if bottom {
                        "h-text_h-40".into()
                    } else {
                        format!("{}", 40. + size * 1.15)
                    };
                    drawlike.push(text_filter(
                        &entry.secondary,
                        entry.secondary_size.unwrap_or(36.),
                        "#cccccc",
                        font,
                        &x,
                        &y,
                        entry,
                        3.,
                    ));
                }
            }
            Kind::Hud => {
                let size = entry.row_size.unwrap_or(36.);
                let col = entry.label_col_w.unwrap_or(size * 6.);
                let name = match &entry.position {
                    Some(Position::Name(p)) => p.as_str(),
                    _ => "top-right",
                };
                for (j, row) in entry.rows.iter().enumerate() {
                    let y = if name.starts_with("top") {
                        format!("{}", 40. + j as f64 * size * 1.3)
                    } else {
                        format!(
                            "h-{}",
                            size + 40. + (entry.rows.len() - 1 - j) as f64 * size * 1.3
                        )
                    };
                    let (lx, vx) = if name.ends_with("center") {
                        (format!("w/2-{col}+({col}-text_w)/2"), "w/2+20".into())
                    } else if name.ends_with("right") {
                        (format!("w-{col}-240"), "w-text_w-40".into())
                    } else {
                        ("40".into(), format!("{}", 40. + col))
                    };
                    drawlike.push(text_filter(
                        &row[0],
                        size,
                        entry.label_color.as_deref().unwrap_or("#aaaaaa"),
                        font,
                        &lx,
                        &y,
                        entry,
                        3.,
                    ));
                    drawlike.push(text_filter(
                        &row[1],
                        size,
                        entry.value_color.as_deref().unwrap_or("white"),
                        font,
                        &vx,
                        &y,
                        entry,
                        3.,
                    ));
                }
            }
            Kind::Box => {
                let [x, y, w, h] = entry.rect.context("box rect")?;
                drawlike.push(format!("drawbox=x={x}:y={y}:w={w}:h={h}:color={}:thickness={}:enable='between(t\\,{start}\\,{end})'",entry.color.as_deref().unwrap_or("yellow"),entry.thickness.unwrap_or(4.)));
            }
            Kind::Magnifier => {
                let [x, y, w, h] = entry.source_rect.context("magnifier source_rect")?;
                let [dx, dy, dw, dh] = entry.dest_rect.context("magnifier dest_rect")?;
                let border = entry
                    .border
                    .as_ref()
                    .and_then(|b| b.as_str())
                    .unwrap_or("white");
                let bw = entry.border_w.unwrap_or(4.);
                filters.push(format!("[{current}]split[base{i}][zoom{i}];[zoom{i}]crop={w}:{h}:{x}:{y},scale={dw}:{dh},pad=iw+{}:ih+{}:{bw}:{bw}:color={border}[inset{i}];[base{i}][inset{i}]overlay=x={}:y={}:enable='between(t\\,{start}\\,{end})'[{next}]",2.*bw,2.*bw,dx-bw,dy-bw));
            }
            Kind::Pip | Kind::Arrow | Kind::Param | Kind::Title => {
                let (path, x, y, scale) = if entry.kind == Kind::Pip {
                    let source = entry.source.as_ref().context("pip source")?;
                    let size = match entry.size {
                        Some(Size::Image(s)) => s,
                        _ => [480., 270.],
                    };
                    let [x, y] = position(
                        entry.position.as_ref(),
                        "bottom-right",
                        width as f64,
                        height as f64,
                        size[0],
                        size[1],
                        40.,
                    )?;
                    (
                        parent.join(source),
                        x,
                        y,
                        format!("scale={}:{}", size[0], size[1]),
                    )
                } else {
                    let path = scratch.0.join(format!("overlay-{i}.png"));
                    let pixels = if entry.kind == Kind::Arrow {
                        arrow(entry, width, height)?
                    } else {
                        panel(entry, width, height)?
                    };
                    write(&path, pixels.encode_png()?)?;
                    (path, 0., 0., "null".into())
                };
                command.args(["-loop", "1", "-i"]).arg(&path);
                let fade = entry
                    .fade
                    .unwrap_or(if entry.kind == Kind::Title { 0.6 } else { 0.25 });
                let alpha = if fade > 0. {
                    format!(
                        ",fade=t=in:st={start}:d={fade}:alpha=1,fade=t=out:st={}:d={fade}:alpha=1",
                        end - fade
                    )
                } else {
                    String::new()
                };
                let border = if entry.kind == Kind::Pip {
                    entry
                        .border
                        .as_ref()
                        .and_then(|b| b.as_str())
                        .map(|c| {
                            let bw = entry.border_w.unwrap_or(4.);
                            format!(",pad=iw+{}:ih+{}:{bw}:{bw}:color={c}", 2. * bw, 2. * bw)
                        })
                        .unwrap_or_default()
                } else {
                    String::new()
                };
                filters.push(format!("[{input}:v]{scale},format=rgba{border}{alpha}[image{i}];[{current}][image{i}]overlay=x={x}:y={y}:enable='between(t\\,{start}\\,{end})'[{next}]"));
                input += 1;
            }
        }
        if !drawlike.is_empty() {
            filters.push(format!("[{current}]{}[{next}]", drawlike.join(",")));
        }
        current = next;
    }
    if let Some(captions) = captions {
        filters.push(format!(
            "[{current}]subtitles='{}'[vout]",
            filter_path(captions)
        ));
    } else {
        filters.push(format!("[{current}]null[vout]"));
    }
    let mut audios = vec!["[0:a]".to_string()];
    for (i, sound) in data.sounds.iter().enumerate() {
        let path = parent.join(&sound.file);
        let length = duration(&path.to_string_lossy())?;
        command.arg("-i").arg(path);
        let mut chain = format!("[{input}:a]volume={}", sound.volume);
        if sound.fade_in > 0. {
            chain.push_str(&format!(",afade=t=in:st=0:d={}", sound.fade_in));
        }
        if sound.fade_out > 0. {
            chain.push_str(&format!(
                ",afade=t=out:st={}:d={}",
                (length - sound.fade_out).max(0.),
                sound.fade_out
            ));
        }
        chain.push_str(&format!(
            ",adelay={}|{}[sfx{i}]",
            (sound.t * 1000.).round(),
            (sound.t * 1000.).round()
        ));
        filters.push(chain);
        audios.push(format!("[sfx{i}]"));
        input += 1;
    }
    if !data.sounds.is_empty() {
        filters.push(format!(
            "{}amix=inputs={}:duration=first:normalize=0[aout]",
            audios.join(""),
            audios.len()
        ));
    }
    command.args([
        "-filter_complex",
        &filters.join(";"),
        "-map",
        "[vout]",
        "-map",
        if data.sounds.is_empty() {
            "0:a"
        } else {
            "[aout]"
        },
        "-c:a",
        if data.sounds.is_empty() {
            "copy"
        } else {
            "aac"
        },
        "-c:v",
        "libx264",
        "-preset",
        preset,
        "-crf",
        &format!("{crf}"),
        "-pix_fmt",
        "yuv420p",
        "-shortest",
        "-loglevel",
        "error",
    ]);
    if !data.sounds.is_empty() {
        command.args(["-b:a", "192k"]);
    }
    command.arg(out);
    if dry {
        println!("{command:?}");
        Ok(())
    } else {
        run(&mut command)
    }
}

pub fn cut(mut args: Args) -> Result<()> {
    let keep = args.flag("--keep-parts");
    let preset = args.take(&["--preset"]).unwrap_or_else(|| "medium".into());
    let crf = args.number(&["--crf"], 18.)?;
    let fade = args.number(&["--fade"], 0.)?;
    let title = args.take(&["--title"]);
    let title_duration = args.number(&["--title-duration"], 2.)?;
    let captions = args.take(&["--captions"]);
    let overlays = args.take(&["--overlays"]);
    let no_overlays = args.flag("--no-overlays");
    ensure!(
        overlays.is_some() || no_overlays,
        "supply --overlays SIDECAR or --no-overlays"
    );
    let default = args.positional(0)?;
    let out = args.positional(2)?;
    let (cuts, _) = cuts(Path::new(args.positional(1)?))?;
    ensure!(!cuts.is_empty(), "empty cut list");
    let scratch = Scratch::new(out, keep)?;
    let mut parts = Vec::new();
    let (width, height, fps) = probe(cuts[0].source.as_deref().unwrap_or(default))?;
    if let Some(title) = title {
        let path = scratch.0.join("part-000-title.mp4");
        let mut cmd = Command::new("ffmpeg");
        cmd.args(["-y","-f","lavfi","-i",&format!("color=c=0x0a0a0a:s={width}x{height}:r={fps}:d={title_duration}"),"-f","lavfi","-i","anullsrc=channel_layout=stereo:sample_rate=48000","-vf",&format!("drawtext=expansion=none:text='{}':font=Helvetica:fontsize=180:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2",escape(&title)),"-t",&title_duration.to_string()]);
        encode(&mut cmd, &preset, crf);
        cmd.arg(&path);
        run(&mut cmd)?;
        parts.push((path, title_duration));
    }
    for (i, cut) in cuts.iter().enumerate() {
        let source = cut.source.as_deref().unwrap_or(default);
        let duration = cut.duration()?;
        let path = scratch.0.join(format!("part-{:03}.mp4", i + 1));
        let mut cmd = Command::new("ffmpeg");
        cmd.arg("-y");
        let mut vf = Vec::new();
        if cut.frozen() {
            let frame = scratch.0.join(format!("freeze-{i}.png"));
            run(Command::new("ffmpeg")
                .args([
                    "-y",
                    "-ss",
                    &cut.at.context("freeze at")?.to_string(),
                    "-i",
                    source,
                    "-frames:v",
                    "1",
                    "-update",
                    "1",
                    "-loglevel",
                    "error",
                ])
                .arg(&frame))?;
            cmd.args(["-loop", "1", "-i"]).arg(frame).args([
                "-f",
                "lavfi",
                "-i",
                "anullsrc=channel_layout=stereo:sample_rate=48000",
                "-t",
                &duration.to_string(),
            ]);
            vf.extend([
                format!("fps={fps}"),
                format!("scale={width}:{height}"),
                "format=yuv420p".into(),
            ]);
        } else {
            cmd.args([
                "-ss",
                &cut.start.unwrap().to_string(),
                "-to",
                &cut.end.unwrap().to_string(),
                "-i",
                source,
            ]);
        }
        if let Some(section) = &cut.section {
            vf.push(format!("drawtext=expansion=none:text='{}':font=Helvetica:fontsize=72:fontcolor=white:bordercolor=black:borderw=4:x=80:y=h-th-180:enable='lt(t\\,3)'",escape(section)));
        }
        if let Some(tool) = &cut.tool {
            vf.push(format!("drawtext=expansion=none:text='{}':font=Helvetica:fontsize=44:fontcolor=white:bordercolor=black:borderw=3:x=w-tw-80:y=80:enable='lt(t\\,3.5)'",escape(tool)));
        }
        if !vf.is_empty() {
            cmd.args(["-vf", &vf.join(",")]);
        }
        encode(&mut cmd, &preset, crf);
        cmd.arg(&path);
        run(&mut cmd)?;
        parts.push((path, duration));
    }
    let concat = if overlays.is_some() {
        scratch.0.join("concat.mp4")
    } else {
        Path::new(out).to_path_buf()
    };
    let caps = if overlays.is_none() {
        captions.as_deref()
    } else {
        None
    };
    let mut cmd = Command::new("ffmpeg");
    cmd.arg("-y");
    for (path, _) in &parts {
        cmd.arg("-i").arg(path);
    }
    let mut graph = Vec::new();
    let mut v = "v0".to_string();
    let mut a = "0:a".to_string();
    if fade > 0. && parts.len() > 1 {
        for i in 0..parts.len() {
            graph.push(format!("[{i}:v]fps={fps},format=yuv420p[v{i}]"));
        }
        let mut at = 0.;
        for i in 1..parts.len() {
            ensure!(
                fade < parts[i - 1].1.min(parts[i].1),
                "fade must be shorter than each cut"
            );
            at += parts[i - 1].1 - fade;
            let nv = format!("xf{i}");
            let na = format!("af{i}");
            graph.push(format!("[{v}][v{i}]xfade=transition=fade:duration={fade}:offset={at},format=yuv420p,fps={fps}[{nv}]"));
            graph.push(format!("[{a}][{i}:a]acrossfade=d={fade}[{na}]"));
            v = nv;
            a = na;
        }
    } else {
        let streams = (0..parts.len())
            .map(|i| format!("[{i}:v][{i}:a]"))
            .collect::<String>();
        graph.push(format!("{streams}concat=n={}:v=1:a=1[v0][a0]", parts.len()));
        a = "a0".into();
    }
    if let Some(captions) = caps {
        graph.push(format!("[{v}]subtitles='{}'[vout]", filter_path(captions)));
        v = "vout".into();
    }
    cmd.args([
        "-filter_complex",
        &graph.join(";"),
        "-map",
        &format!("[{v}]"),
        "-map",
        &format!("[{a}]"),
    ]);
    encode(&mut cmd, &preset, crf);
    cmd.arg(&concat);
    run(&mut cmd)?;
    if let Some(sidecar) = overlays {
        render_overlays(
            &concat.to_string_lossy(),
            Path::new(&sidecar),
            out,
            captions.as_deref(),
            &preset,
            crf,
            false,
        )?;
    }
    println!("{out}");
    Ok(())
}
