//! On-demand film commands rebuild the saved studio and explainer from their source clocks and media.
mod assets;
mod beverage;
mod clock;
mod explainer;
mod finish;
mod narration;
mod routine;
mod sound;

use crate::{Args, json, root, run, write};
use anyhow::{Result, ensure};
use serde_json::json;
use std::{
    fs,
    path::{Path, PathBuf},
    process::Command,
};

pub fn main(command: &str, args: Args) -> Result<()> {
    match command {
        "studio-stage" => stage(args),
        "studio-render" => render(args),
        "studio-audio" => sound::studio(args),
        "studio-finish" => finish::main(args),
        "studio-clock" => print_clock(args),
        "explainer-edit" => explainer::edit(args),
        "explainer-audio" => sound::explainer(args),
        "explainer-assets" => assets::main(args),
        "film-narration" => narration::main(args),
        _ => unreachable!(),
    }
}
fn print_clock(mut args: Args) -> Result<()> {
    let timing = args.take(&["--timing"]).map(PathBuf::from);
    let story = clock::Story::read(timing.as_deref())?;
    let bytes = serde_json::to_vec_pretty(&story)?;
    if let Some(out) = args.take(&["--out"]) {
        write(out, bytes)?;
    } else {
        println!("{}", String::from_utf8(bytes)?);
    }
    Ok(())
}
fn blender(
    scene: &mut crate::scene::Scene,
    path: &Path,
    executable: &str,
    describe: bool,
) -> Result<()> {
    scene.write(path)?;
    if !describe {
        run(Command::new(executable)
            .args([
                "--background",
                "--factory-startup",
                "--python-exit-code",
                "1",
                "--python",
            ])
            .arg(root().join("tools/render/blender_adapter.py"))
            .arg("--")
            .arg(path))?;
    }
    Ok(())
}
fn stage(mut args: Args) -> Result<()> {
    let stills = args.flag("--stills");
    let fps = args.number(&["--fps"], 24.)?;
    let width = args.number(&["--width"], 1920.)? as u32;
    let samples = args.number(&["--samples"], 32.)? as usize;
    let start = args.number(&["--start-frame"], 0.)? as usize;
    let end = args
        .take(&["--end-frame"])
        .map(|n| n.parse::<usize>())
        .transpose()?;
    let time = args
        .take(&["--time"])
        .map(|n| n.parse::<f64>())
        .transpose()?;
    let out = args
        .take(&["--out"])
        .map(PathBuf::from)
        .unwrap_or_else(|| clock::here().join("out"));
    fs::create_dir_all(&out)?;
    let out = fs::canonicalize(out)?;
    let frames = args
        .take(&["--frames-root"])
        .map(PathBuf::from)
        .unwrap_or_else(|| out.join("frames"));
    let story = args.take(&["--story"]).map(PathBuf::from);
    let timing = args.take(&["--timing"]).map(PathBuf::from);
    let story: clock::Story = if let Some(path) = story {
        serde_json::from_value(json(path)?)?
    } else {
        clock::Story::read(timing.as_deref())?
    };
    let describe = args.flag("--describe-only");
    let executable = args
        .take(&["--blender"])
        .unwrap_or_else(|| "/Applications/Blender.app/Contents/MacOS/Blender".into());
    let selected = if args.flag("--shots") {
        args.0
    } else {
        vec!["hero".into(), "pour".into(), "serve".into()]
    };
    for shot in selected {
        let shot = story.shot(&shot)?;
        ensure!(
            ["can", "studio"].contains(&shot.kind.as_str()),
            "CG studio or routine shot required"
        );
        let duration = shot.end - shot.start;
        let sequence: Vec<_> = if stills {
            let time = time.unwrap_or(duration * 0.55);
            vec![((time * fps).round() as usize, time)]
        } else {
            let count = if shot.hold {
                1
            } else {
                (duration * fps).round() as usize
            };
            (start..count.min(end.unwrap_or(count)))
                .map(|i| (i, i as f64 / fps))
                .collect()
        };
        let folder = if stills {
            out.join("stills")
        } else {
            frames.join(&shot.id)
        };
        fs::create_dir_all(&folder)?;
        let sequence: Vec<_> = sequence
            .into_iter()
            .map(|(i, t)| {
                let file = folder.join(if stills {
                    format!("{}-{i:05}.png", shot.id)
                } else {
                    format!("{i:05}.png")
                });
                (i, t, file)
            })
            .filter(|(_, _, file)| stills || !file.exists())
            .collect();
        if sequence.is_empty() {
            continue;
        }
        let path = out.join(format!("{}-{start}.scene.json", shot.id));
        if shot.kind == "can" {
            let mut model = routine::Routine::new(&out, samples)?;
            for (i, t, file) in sequence {
                model.frame(shot, i, t, width, &file)?;
            }
            blender(&mut model.scene, &path, &executable, describe)?;
        } else {
            let mut model = beverage::Beverage::new(&out, samples)?;
            for (i, t, file) in sequence {
                model.frame(shot, i, t, width, &file)?;
            }
            blender(&mut model.scene, &path, &executable, describe)?;
        }
        if !describe {
            let _ = fs::remove_file(path.with_extension("bin"));
            let _ = fs::remove_file(path);
        }
        println!("{}", folder.display());
    }
    Ok(())
}
fn render(mut args: Args) -> Result<()> {
    let fps = args.number(&["--fps"], 24.)?;
    let pour_fps = args.number(&["--pour-fps"], 24.)?;
    let width = args.number(&["--width"], 1920.)? as u32;
    let samples = args.number(&["--samples"], 32.)? as usize;
    let timing = args.take(&["--timing"]).map(PathBuf::from);
    let profile = args
        .take(&["--profile"])
        .unwrap_or_else(|| "story-loop".into());
    let out = args
        .take(&["--out"])
        .map(PathBuf::from)
        .unwrap_or_else(|| clock::here().join("out"));
    let chunk = args.number(&["--chunk-frames"], 32.)? as usize;
    let fresh = args.flag("--fresh");
    let picture_only = args.flag("--picture-only");
    let finish_only = args.flag("--finish-only");
    let draft = args.flag("--draft");
    let describe = args.flag("--describe-only");
    let executable = args
        .take(&["--blender"])
        .unwrap_or_else(|| "/Applications/Blender.app/Contents/MacOS/Blender".into());
    let selected = if args.flag("--shots") {
        Some(args.0)
    } else {
        None
    };
    fs::create_dir_all(&out)?;
    let out = fs::canonicalize(out)?;
    let story = clock::Story::read(timing.as_deref())?;
    let source = story.source();
    let clock = out.join("native-source-clock.json");
    write(&clock, serde_json::to_vec_pretty(&source)?)?;
    let frames = clock::here().join(format!(
        "out/frames/{profile}-{fps}-{pour_fps}fps-{width}px-{samples}spp"
    ));
    let rates: std::collections::BTreeMap<_, _> = source
        .scenes
        .iter()
        .filter(|s| ["can", "studio"].contains(&s.kind.as_str()))
        .map(|s| (s.id.clone(), if s.id == "pour" { pour_fps } else { fps }))
        .collect();
    write(
        out.join("render-plan.json"),
        serde_json::to_vec_pretty(
            &json!({"width":width,"height":(width as f64*9./16.).round(),"samples":samples,"source_fps":rates,"frames":frames,"profile":profile,"source_clock":clock,"delivery_fps":24,"duration":story.duration,"max_frames_per_process":chunk}),
        )?,
    )?;
    if !finish_only {
        for shot in source.scenes.iter().filter(|s| rates.contains_key(&s.id)) {
            if selected
                .as_ref()
                .is_some_and(|list| !list.contains(&shot.id))
            {
                continue;
            }
            let rate = rates[&shot.id];
            let folder = frames.join(&shot.id);
            if fresh && folder.exists() {
                fs::remove_dir_all(&folder)?;
            }
            let count = if shot.hold {
                1
            } else {
                (shot.frames as f64 * rate / 24.).round() as usize
            };
            let chunk = if chunk == 0 { count } else { chunk };
            for start in (0..count).step_by(chunk) {
                let end = count.min(start + chunk);
                if (start..end).all(|i| folder.join(format!("{i:05}.png")).exists()) {
                    continue;
                }
                let mut next = vec![
                    "--story".into(),
                    clock.to_string_lossy().into(),
                    "--out".into(),
                    out.to_string_lossy().into(),
                    "--frames-root".into(),
                    frames.to_string_lossy().into(),
                    "--fps".into(),
                    rate.to_string(),
                    "--width".into(),
                    width.to_string(),
                    "--samples".into(),
                    samples.to_string(),
                    "--start-frame".into(),
                    start.to_string(),
                    "--end-frame".into(),
                    end.to_string(),
                    "--blender".into(),
                    executable.clone(),
                ];
                if describe {
                    next.push("--describe-only".into());
                }
                next.extend(["--shots".into(), shot.id.clone()]);
                stage(Args(next))?;
            }
        }
    }
    if !picture_only && !describe {
        let mut audio = vec!["--out".into(), out.to_string_lossy().into()];
        if let Some(timing) = &timing {
            audio.extend(["--timing".into(), timing.to_string_lossy().into()]);
        }
        sound::studio(Args(audio))?;
        let mut finish = vec![
            "--out".into(),
            out.to_string_lossy().into(),
            "--frames".into(),
            frames.to_string_lossy().into(),
            "--fps".into(),
            fps.to_string(),
            "--source-fps".into(),
            format!("pour={pour_fps}"),
            "--audio".into(),
            out.join("mix-master.wav").to_string_lossy().into(),
        ];
        if let Some(timing) = &timing {
            finish.extend(["--timing".into(), timing.to_string_lossy().into()]);
        }
        if draft {
            finish.push("--draft".into());
        }
        finish::main(Args(finish))?;
    }
    Ok(())
}
