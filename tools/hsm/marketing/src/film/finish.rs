//! The native finisher sets the film's typography, maps held frames and encodes its picture and player.
use super::clock::{self, Shot, Story};
use crate::{Args, draw, json, root, run, write};
use anyhow::{Context, Result, ensure};
use serde_json::json;
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeMap,
    fs,
    io::Write,
    path::{Path, PathBuf},
    process::{Command, Stdio},
    time::UNIX_EPOCH,
};
use tiny_skia::{Color, Pixmap, Transform};

const W: u32 = 1920;
const H: u32 = 1080;
const FPS: usize = 24;
const COLOR: &str = "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709,setsar=1";
fn ffmpeg() -> Command {
    let mut command = Command::new("ffmpeg");
    command.args([
        "-hide_banner",
        "-loglevel",
        "warning",
        "-filter_complex_threads",
        "2",
        "-nostdin",
        "-y",
    ]);
    command
}
fn encoder(command: &mut Command, draft: bool) {
    command.args([
        "-c:v",
        "libx264",
        "-preset",
        if draft { "veryfast" } else { "slow" },
        "-crf",
        if draft { "19" } else { "16" },
        "-threads",
        if draft { "2" } else { "0" },
        "-r",
        "24",
        "-video_track_timescale",
        "24000",
        "-color_range",
        "tv",
        "-color_primaries",
        "bt709",
        "-color_trc",
        "bt709",
        "-colorspace",
        "bt709",
        "-movflags",
        "+faststart",
    ]);
}
struct Type {
    path: PathBuf,
    start: f64,
    fade: f64,
    end: Option<f64>,
}
fn layer(
    lines: &[&str],
    size: f64,
    weight: f32,
    color: &str,
    at: [f64; 2],
    leading: f64,
) -> Result<Pixmap> {
    let mut pixels = Pixmap::new(W, H).unwrap();
    let font = draw::Typeface::new(&clock::here().join("fonts/Montserrat.ttf"), 0)?.weight(weight);
    for (i, line) in lines.iter().enumerate() {
        font.top_left(
            &mut pixels,
            line,
            size,
            [at[0], at[1] + i as f64 * size * leading],
            draw::rgba(color),
        );
    }
    Ok(pixels)
}
fn wordmark() -> Result<Pixmap> {
    let mut full = Pixmap::new(1680, 640).unwrap();
    let source = fs::read_to_string(root().join("brand/mark.svg"))?;
    let path = draw::tags(&source, "path").next().context("mark path")?;
    let t = Transform::from_scale(0.625, 0.625);
    draw::path(
        &mut full,
        &draw::svg_path(draw::attribute(path, "d")?)?.0,
        draw::rgba("#1749D1"),
        t,
    );
    let circle = draw::tags(&source, "circle").next().context("mark drop")?;
    draw::circle(
        &mut full,
        [
            draw::attribute(circle, "cx")?.parse()?,
            draw::attribute(circle, "cy")?.parse()?,
        ],
        draw::attribute(circle, "r")?.parse()?,
        draw::rgba("#FF9152"),
        None,
        t,
    );
    let lettering = fs::read_to_string(root().join("brand/wordmark-lettering.svg"))?;
    for (i, path) in draw::tags(&lettering, "path").enumerate() {
        draw::path(
            &mut full,
            &draw::svg_path(draw::attribute(path, "d")?)?.0,
            draw::rgba("#10319C"),
            Transform::from_translate(662., [300., 475.][i]),
        );
    }
    let mut left = full.width();
    let mut top = full.height();
    let mut right = 0;
    let mut bottom = 0;
    for y in 0..full.height() {
        for x in 0..full.width() {
            if full.pixels()[(y * full.width() + x) as usize].alpha() > 2 {
                left = left.min(x);
                top = top.min(y);
                right = right.max(x);
                bottom = bottom.max(y);
            }
        }
    }
    let image = full
        .clone_rect(
            tiny_skia::IntRect::from_ltrb(
                left as i32,
                top as i32,
                right as i32 + 1,
                bottom as i32 + 1,
            )
            .context("wordmark bounds")?,
        )
        .context("wordmark crop")?;
    draw::resized(
        &image,
        340,
        ((bottom - top + 1) as f64 * 340. / (right - left + 1) as f64).round() as u32,
    )
}
fn types(work: &Path, story: &Story) -> Result<BTreeMap<String, Vec<Type>>> {
    let mut all: BTreeMap<String, Vec<Type>> = BTreeMap::new();
    let mut put = |shot: &str,
                   lines: &[&str],
                   size: f64,
                   weight: f32,
                   color: &str,
                   at: [f64; 2],
                   leading: f64,
                   start: f64,
                   fade: f64,
                   end: Option<f64>|
     -> Result<()> {
        let pixels = layer(lines, size, weight, color, at, leading)?;
        let entries = all.entry(shot.into()).or_default();
        let path = work.join(format!("{shot}-type-{}.png", entries.len()));
        write(&path, pixels.encode_png()?)?;
        entries.push(Type {
            path,
            start: story.local_time(shot, start)?,
            fade,
            end: end.map(|end| story.local_time(shot, end)).transpose()?,
        });
        Ok(())
    };
    put(
        "opening",
        &["A glass", "of soda."],
        88.,
        550.,
        "#1749D1",
        [128., 325.],
        1.02,
        0.55,
        0.22,
        None,
    )?;
    put(
        "opening",
        &["IN DEVELOPMENT  ·  PRODUCT VISUALIZATION"],
        22.,
        500.,
        "#1749D1",
        [135., 80.],
        1.05,
        0.,
        0.15,
        None,
    )?;
    put(
        "case",
        &["Somehow,"],
        92.,
        550.,
        "white",
        [128., 325.],
        1.05,
        0.08,
        0.18,
        None,
    )?;
    put(
        "case",
        &["a trip to the store."],
        38.,
        450.,
        "#DCE6FF",
        [135., 480.],
        1.05,
        story.type_timing["case_store"].as_f64().unwrap_or(1.05),
        0.18,
        None,
    )?;
    put(
        "car",
        &["Into the car."],
        64.,
        500.,
        "white",
        [128., 380.],
        1.05,
        0.02,
        0.12,
        None,
    )?;
    put(
        "kitchen",
        &["Into the", "kitchen."],
        64.,
        500.,
        "#1749D1",
        [128., 350.],
        1.05,
        0.02,
        0.12,
        None,
    )?;
    put(
        "shelf",
        &["Onto a shelf."],
        64.,
        500.,
        "white",
        [128., 380.],
        1.05,
        0.02,
        0.12,
        None,
    )?;
    for (i, (text, start, default)) in [
        ("Another trip.", 1.90, 2.50),
        ("And another.", 3.00, 3.58),
        ("And another.", 3.80, 4.45),
    ]
    .into_iter()
    .enumerate()
    {
        put(
            "repeat",
            &[text],
            78.,
            500.,
            "white",
            [128., 300.],
            1.05,
            start,
            0.12,
            Some(
                story.type_timing["repeat_type_ends"][i]
                    .as_f64()
                    .unwrap_or(default),
            ),
        )?;
    }
    put(
        "question",
        &["What if the", "next glass was", "already waiting?"],
        62.,
        500.,
        "white",
        [128., 300.],
        1.15,
        0.10,
        0.20,
        None,
    )?;
    if let Some(start) = story.type_timing["hero_cold_frame"].as_f64() {
        let end = story.type_timing["hero_carbonated_frame"].as_f64();
        put(
            "hero",
            &["Cold"],
            112.,
            550.,
            "#1749D1",
            [128., 391.],
            1.05,
            start / 24.,
            3. / 24.,
            end.map(|t| t / 24.),
        )?;
        if let Some(start) = end {
            put(
                "hero",
                &["Carbonated"],
                112.,
                550.,
                "#1749D1",
                [128., 391.],
                1.05,
                start / 24.,
                3. / 24.,
                None,
            )?;
        }
    } else {
        put(
            "hero",
            &["Already", "here."],
            112.,
            550.,
            "#1749D1",
            [128., 314.],
            1.03,
            0.08,
            0.22,
            None,
        )?;
    }
    put(
        "hero",
        &["IN DEVELOPMENT  ·  PRODUCT VISUALIZATION"],
        22.,
        500.,
        "#1749D1",
        [135., 80.],
        1.05,
        0.,
        0.15,
        None,
    )?;
    put(
        "serve",
        &["One less", "errand."],
        111.,
        550.,
        "#1749D1",
        [126., 391.],
        1.03,
        1.65,
        0.22,
        None,
    )?;
    put(
        "serve",
        &["Explore the machine"],
        32.,
        500.,
        "#1749D1",
        [135., 710.],
        1.05,
        2.40,
        0.18,
        None,
    )?;
    put(
        "serve",
        &["homesodamachine.com"],
        36.,
        600.,
        "#1749D1",
        [135., 763.],
        1.05,
        2.40,
        0.18,
        None,
    )?;
    put(
        "serve",
        &["IN DEVELOPMENT  ·  PRODUCT VISUALIZATION"],
        22.,
        500.,
        "#1749D1",
        [135., 80.],
        1.05,
        0.,
        0.15,
        None,
    )?;
    let mut pixels = Pixmap::new(W, H).unwrap();
    let logo = wordmark()?;
    pixels.draw_pixmap(
        133,
        194,
        logo.as_ref(),
        &Default::default(),
        Transform::identity(),
        None,
    );
    let path = work.join("serve-wordmark.png");
    write(&path, pixels.encode_png()?)?;
    all.get_mut("serve").unwrap().insert(
        0,
        Type {
            path,
            start: 0.,
            fade: 0.15,
            end: None,
        },
    );
    Ok(all)
}
struct Particle {
    x: f64,
    phase: f64,
    speed: f64,
    radius: f64,
    sway: f64,
    frequency: f64,
    angle: f64,
    strength: f64,
}
fn particles() -> Vec<Particle> {
    let mut rng = crate::scene::Random::new(640173);
    let mut particles = Vec::new();
    for lane in [0.525, 0.591, 0.657, 0.724, 0.791, 0.858, 0.934] {
        let offset = rng.uniform(0., 1.);
        for i in 0..4 {
            let radius = rng.uniform(1.15, 2.85);
            let speed = (35. + (radius - 1.15) * 38. + rng.uniform(-9., 9.)).clamp(35., 110.);
            particles.push(Particle {
                x: lane * W as f64 + rng.uniform(-14., 14.),
                phase: (offset + (i as f64 + rng.uniform(-0.22, 0.22)) / 4.).rem_euclid(1.),
                speed,
                radius,
                sway: rng.uniform(4., 10.),
                frequency: rng.uniform(0.45, 0.85),
                angle: rng.uniform(0., std::f64::consts::TAU),
                strength: rng.uniform(0.62, 0.95),
            });
        }
    }
    particles
}
fn carbonation(shot: &Shot, target: &Path) -> Result<()> {
    let mut command = ffmpeg();
    command
        .args([
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgba",
            "-s",
            "1920x1080",
            "-framerate",
            "24",
            "-i",
            "pipe:0",
            "-an",
            "-c:v",
            "qtrle",
            "-pix_fmt",
            "argb",
            "-threads",
            "2",
        ])
        .arg(target)
        .stdin(Stdio::piped());
    let mut process = command.spawn()?;
    let particles = particles();
    let mut pipe = process.stdin.take().context("carbonation encoder input")?;
    let mut bytes = vec![0_u8; (W * H * 4) as usize];
    for i in 0..shot.frames {
        let t = shot.start + i as f64 / 24.;
        let mut pixels = Pixmap::new(W, H).unwrap();
        for p in &particles {
            let progress = (t * p.speed / (1075. - 494.) + p.phase).rem_euclid(1.);
            let y = 1075. - progress * (1075. - 494.);
            let x = p.x
                + p.sway * (t * p.frequency + p.angle).sin()
                + p.sway * 0.28 * (t * 0.31 + p.angle * 1.7).sin();
            let opacity = p.strength
                * crate::scene::ease((y - 494.) / 62.)
                * crate::scene::ease((1075. - y) / 64.);
            let color = Color::from_rgba8(125, 169, 74, (140. * opacity) as u8);
            draw::circle(
                &mut pixels,
                [x, y],
                p.radius,
                color,
                Some(0.5),
                Transform::identity(),
            );
            draw::circle(
                &mut pixels,
                [x - p.radius * 0.4, y - p.radius * 0.5],
                p.radius * 0.22,
                Color::from_rgba8(255, 255, 226, (188. * opacity) as u8),
                None,
                Transform::identity(),
            );
        }
        for (dst, src) in bytes.chunks_exact_mut(4).zip(pixels.pixels()) {
            let c = src.demultiply();
            dst.copy_from_slice(&[c.red(), c.green(), c.blue(), c.alpha()]);
        }
        if let Err(error) = pipe.write_all(&bytes) {
            let _ = process.kill();
            let _ = process.wait();
            return Err(error.into());
        }
    }
    drop(pipe);
    ensure!(process.wait()?.success(), "carbonation overlay encode");
    Ok(())
}
fn pngs(folder: &Path) -> Result<Vec<PathBuf>> {
    if !folder.exists() {
        return Ok(Vec::new());
    }
    let mut files = fs::read_dir(folder)?
        .filter_map(|e| e.ok().map(|e| e.path()))
        .filter(|p| {
            p.extension().is_some_and(|e| e == "png")
                && p.file_stem()
                    .is_some_and(|s| s.to_string_lossy().chars().all(|c| c.is_ascii_digit()))
        })
        .collect::<Vec<_>>();
    files.sort();
    Ok(files)
}
fn picture(
    shot: &Shot,
    target: &Path,
    frames: &Path,
    work: &Path,
    rate: f64,
    animatic: bool,
    draft: bool,
    layers: Option<&Vec<Type>>,
) -> Result<()> {
    let duration = shot.frames as f64 / 24.;
    let mut folder = frames.join(&shot.id);
    let files = pngs(&folder)?;
    let mut command = ffmpeg();
    let (prefix, source, input_count, cadence) = if shot.kind == "photograph" {
        let bubbles = work.join(format!("{}-carbonation.mov", shot.id));
        carbonation(shot, &bubbles)?;
        command
            .args(["-loop", "1", "-framerate", "24", "-i"])
            .arg(clock::here().join(shot.asset.as_ref().context("photograph source")?))
            .arg("-i")
            .arg(bubbles);
        let (base, travel, focus) = if shot.id == "sensory" {
            (1.32, 0.028, 0.91)
        } else {
            (1.005, 0.018, 0.62)
        };
        (
            format!(
                "[0:v]scale={W}:{H}:flags=lanczos[plate];[plate][1:v]overlay=shortest=1:format=auto[animated];"
            ),
            "animated".to_string(),
            2,
            format!(
                "scale=2304:1296:flags=lanczos,zoompan=z={base}+{travel}*on/{}:x=(iw-iw/zoom)*{focus}:y=(ih-ih/zoom)*0.45:d=1:s={W}x{H}:fps=24,trim=duration={duration},setpts=PTS-STARTPTS",
                shot.frames
            ),
        )
    } else if animatic || shot.hold {
        ensure!(!files.is_empty(), "no source frame for {}", shot.id);
        command
            .args(["-loop", "1", "-framerate", "24", "-i"])
            .arg(&files[files.len() / 2]);
        (
            String::new(),
            "0:v".into(),
            1,
            format!("fps=24,trim=duration={duration},setpts=PTS-STARTPTS"),
        )
    } else {
        let needed =
            (shot.source_frames.unwrap_or(shot.frames) as f64 / 24. * rate).ceil() as usize;
        for i in 0..needed {
            ensure!(
                folder.join(format!("{i:05}.png")).exists(),
                "{}: missing source frame {i}",
                shot.id
            );
        }
        if !shot.frame_holds.is_empty() {
            ensure!(rate == 24., "settled holds require native source cadence");
            let mapped = work.join("frame-maps").join(&shot.id);
            fs::create_dir_all(&mapped)?;
            let mut n = 0;
            for i in 0..needed {
                let count = 1 + shot
                    .frame_holds
                    .iter()
                    .filter(|h| h.source_frame == i)
                    .map(|h| h.frames)
                    .sum::<usize>();
                for _ in 0..count {
                    let link = mapped.join(format!("{n:05}.png"));
                    if fs::symlink_metadata(&link).is_ok() {
                        fs::remove_file(&link)?;
                    }
                    std::os::unix::fs::symlink(
                        fs::canonicalize(folder.join(format!("{i:05}.png")))?,
                        link,
                    )?;
                    n += 1;
                }
            }
            folder = mapped;
        }
        command
            .args(["-framerate", &rate.to_string(), "-i"])
            .arg(folder.join("%05d.png"));
        let cadence = if rate < 24. {
            let pre = 2. / rate;
            let post = 3. / rate;
            format!(
                "tpad=start_mode=clone:start_duration={pre}:stop_mode=clone:stop_duration={post},minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:me=epzs:mb_size=16:search_param=24:vsbmc=1,trim=start={pre}:duration={duration},setpts=PTS-STARTPTS"
            )
        } else {
            format!("fps=24,trim=duration={duration},setpts=PTS-STARTPTS")
        };
        (String::new(), "0:v".into(), 1, cadence)
    };
    let mut graph =
        format!("{prefix}[{source}]{cadence},scale={W}:{H}:flags=lanczos,setsar=1[p0];");
    let mut previous = "p0".to_string();
    if let Some(layers) = layers {
        for (i, layer) in layers.iter().enumerate() {
            command
                .args(["-loop", "1", "-framerate", "24", "-i"])
                .arg(&layer.path);
            let index = i + 1;
            let mut fade = format!(
                "format=rgba,fade=t=in:st={}:d={}:alpha=1",
                layer.start, layer.fade
            );
            if let Some(end) = layer.end {
                fade.push_str(&format!(
                    ",fade=t=out:st={}:d={}:alpha=1",
                    end - layer.fade,
                    layer.fade
                ));
            }
            graph.push_str(&format!("[{}:v]{fade}[t{index}];[{previous}][t{index}]overlay=shortest=1:format=auto[p{index}];",i+input_count));
            previous = format!("p{index}");
        }
    }
    graph.push_str(&format!("[{previous}]{COLOR}[out]"));
    command.args([
        "-filter_complex",
        &graph,
        "-map",
        "[out]",
        "-an",
        "-frames:v",
        &shot.frames.to_string(),
    ]);
    encoder(&mut command, draft);
    command.arg(target);
    run(&mut command)
}
pub fn main(mut args: Args) -> Result<()> {
    let frames = args
        .take(&["--frames"])
        .map(PathBuf::from)
        .unwrap_or_else(|| clock::here().join("out/frames"));
    let audio = args
        .take(&["--audio"])
        .map(PathBuf::from)
        .unwrap_or_else(|| clock::here().join("out/mix-master.wav"));
    let out = args
        .take(&["--out"])
        .map(PathBuf::from)
        .unwrap_or_else(|| clock::here().join("out"));
    let timing = args.take(&["--timing"]).map(PathBuf::from);
    let draft = args.flag("--draft");
    let force = args.flag("--force");
    let animatic = args.flag("--animatic");
    let fps = args.number(&["--fps"], 24.)?;
    let mut rates = BTreeMap::new();
    while let Some(value) = args.take(&["--source-fps"]) {
        let (name, rate) = value.split_once('=').context("--source-fps name=rate")?;
        rates.insert(name.to_owned(), rate.parse::<f64>()?);
    }
    let story = Story::read(timing.as_deref())?;
    fs::create_dir_all(&out)?;
    let out = fs::canonicalize(out)?;
    let work = out.join("finish-assets");
    let segments = out.join("segments");
    fs::create_dir_all(&work)?;
    fs::create_dir_all(&segments)?;
    ensure!(audio.exists(), "missing sound master {}", audio.display());
    let typography = types(&work, &story)?;
    let cache_path = out.join(".finish-cache.json");
    let mut cache = json(&cache_path).unwrap_or(json!({}));
    let mut targets = Vec::new();
    let code = format!(
        "{:x}",
        Sha256::digest(
            [
                include_str!("finish.rs"),
                include_str!("../draw.rs"),
                include_str!("clock.rs")
            ]
            .join("")
        )
    );
    for shot in &story.scenes {
        let mut files = pngs(&frames.join(&shot.id))?;
        if shot.kind == "photograph" {
            files.push(clock::here().join(shot.asset.as_ref().unwrap()));
        }
        let modified = files
            .iter()
            .filter_map(|p| {
                p.metadata()
                    .ok()?
                    .modified()
                    .ok()?
                    .duration_since(UNIX_EPOCH)
                    .ok()
                    .map(|d| d.as_nanos())
            })
            .max()
            .unwrap_or(0);
        let rate = rates.get(&shot.id).copied().unwrap_or(fps);
        let signature = format!(
            "{:x}",
            Sha256::digest(serde_json::to_vec(
                &json!({"shot":shot,"code":code,"animatic":animatic,"rate":rate,"draft":draft,"source":frames,"type_timing":story.type_timing,"frames":files.len(),"modified":modified})
            )?)
        );
        let target = segments.join(format!("{}.mp4", shot.id));
        if force || cache[&shot.id] != signature || !target.exists() {
            picture(
                shot,
                &target,
                &frames,
                &work,
                rate,
                animatic,
                draft,
                typography.get(&shot.id),
            )?;
            cache[&shot.id] = json!(signature);
            write(&cache_path, serde_json::to_vec_pretty(&cache)?)?;
        }
        targets.push(target);
    }
    let sequence = work.join("sequence.ffconcat");
    write(
        &sequence,
        format!(
            "ffconcat version 1.0\n{}",
            targets
                .iter()
                .map(|p| format!("file '{}'\n", p.to_string_lossy().replace('\'', "'\\''")))
                .collect::<String>()
        ),
    )?;
    run(ffmpeg()
        .args(["-f", "concat", "-safe", "0", "-i"])
        .arg(sequence)
        .arg("-i")
        .arg(&audio)
        .args([
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "320k",
            "-ar",
            "48000",
            "-t",
            &story.duration.to_string(),
            "-movflags",
            "+faststart",
            "-metadata",
            "title=One less errand. — Home Soda Machine",
            "-metadata",
            "comment=In development · Product visualization",
        ])
        .arg(out.join("film.mp4")))?;
    let closing = story.shot("serve")?;
    let at = closing.start + (closing.end - closing.start) * 0.75;
    run(ffmpeg()
        .args(["-ss", &at.to_string(), "-i"])
        .arg(out.join("film.mp4"))
        .args(["-frames:v", "1", "-update", "1", "-q:v", "2"])
        .arg(out.join("poster.jpg")))?;
    let mut samples = Vec::new();
    for shot in &story.scenes {
        let fractions: &[f64] = match shot.id.as_str() {
            "case" => &[0.25, 0.90],
            "repeat" => &[0.15, 0.45, 0.85],
            "serve" => &[0.15, 0.80],
            _ => &[0.55],
        };
        for &p in fractions {
            samples
                .push(((shot.start + (shot.end - shot.start) * p) * FPS as f64).round() as usize);
        }
    }
    samples.sort_unstable();
    samples.dedup();
    let selected = samples
        .iter()
        .map(|n| format!("eq(n,{n})"))
        .collect::<Vec<_>>()
        .join("+");
    run(ffmpeg()
        .arg("-i")
        .arg(out.join("film.mp4"))
        .args([
            "-vf",
            &format!(
                "select='{selected}',scale=480:270,tile=3x{}",
                samples.len().div_ceil(3)
            ),
            "-frames:v",
            "1",
            "-update",
            "1",
            "-q:v",
            "2",
        ])
        .arg(out.join("contact-sheet.jpg")))?;
    fs::copy(
        clock::here().join("fonts/Montserrat.ttf"),
        out.join("Montserrat.ttf"),
    )?;
    fs::copy(
        root().join("web/public/brand/wordmark-reverse.svg"),
        out.join("brand.svg"),
    )?;
    let seconds = story.duration.ceil() as usize;
    write(
        out.join("index.html"),
        fs::read_to_string(clock::here().join("preview.html"))?.replace(
            "{{DURATION}}",
            &format!("{}:{:02}", seconds / 60, seconds % 60),
        ),
    )?;
    write(
        out.join("picture-clock.json"),
        serde_json::to_vec_pretty(&story)?,
    )?;
    for name in ["film.vtt", "film.srt"] {
        let source = audio.parent().unwrap().join(name);
        let target = out.join(name);
        if source.exists() && fs::canonicalize(&source).ok() != fs::canonicalize(&target).ok() {
            fs::copy(source, target)?;
        }
    }
    println!("{}", out.join("film.mp4").display());
    Ok(())
}
