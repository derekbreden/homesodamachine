//! The explainer's native sound edit preserves recorded words and follows the saved picture clock.
use super::{
    sound,
    sound::{Aligned, Caption},
};
use crate::{Args, json, root, run, write};
use anyhow::{Context, Result, ensure};
use serde_json::json;
use std::{fs, path::PathBuf, process::Command};

pub fn here() -> PathBuf {
    root().join("marketing/video/how-carbonation-works")
}
fn normalize(text: &str) -> String {
    text.to_lowercase()
        .replace('₂', "2")
        .chars()
        .filter(char::is_ascii_alphanumeric)
        .collect()
}
pub fn match_words(expected: &[String], heard: &[Aligned]) -> Result<Vec<(usize, usize)>> {
    let a: Vec<_> = expected.iter().map(|w| normalize(w)).collect();
    let b: Vec<_> = heard.iter().map(|w| normalize(&w.word)).collect();
    let width = b.len() + 1;
    let mut table = vec![0_u32; (a.len() + 1) * width];
    for i in (0..a.len()).rev() {
        for j in (0..b.len()).rev() {
            table[i * width + j] = if a[i] == b[j] {
                1 + table[(i + 1) * width + j + 1]
            } else {
                table[(i + 1) * width + j].max(table[i * width + j + 1])
            };
        }
    }
    let mut result = vec![None; a.len()];
    let (mut i, mut j) = (0, 0);
    while i < a.len() && j < b.len() {
        if a[i] == b[j] {
            result[i] = Some((j, j));
            i += 1;
            j += 1;
        } else if table[(i + 1) * width + j] >= table[i * width + j + 1] {
            i += 1;
        } else {
            j += 1;
        }
    }
    let mut start = 0;
    while start < result.len() {
        if result[start].is_some() {
            start += 1;
            continue;
        }
        let mut end = start + 1;
        while end < result.len() && result[end].is_none() {
            end += 1;
        }
        let lo = if start == 0 {
            0
        } else {
            result[start - 1].unwrap().1 + 1
        };
        let hi = if end == result.len() {
            heard.len()
        } else {
            result[end].unwrap().0
        };
        ensure!(
            hi > lo,
            "script word has no recognition match: {}",
            expected[start..end].join(" ")
        );
        for k in start..end {
            let a = lo + (k - start) * (hi - lo) / (end - start);
            let b = lo + (((k - start + 1) * (hi - lo) / (end - start)).max(1)) - 1;
            result[k] = Some((a, b.min(hi - 1)));
        }
        start = end;
    }
    result
        .into_iter()
        .map(|p| p.context("script alignment"))
        .collect()
}
fn round(v: f64, places: i32) -> f64 {
    let scale = 10_f64.powi(places);
    (v * scale).round() / scale
}
fn caption_lines(text: &str) -> String {
    let custom = [
        (
            "At its center is a stainless steel carbonator:",
            "At its center is a\nstainless steel carbonator:",
        ),
        (
            "Carbon dioxide enters through a port at the bottom.",
            "Carbon dioxide enters\nthrough a port at the bottom.",
        ),
        (
            "As the pressures balance, gas admission stops.",
            "As the pressures balance,\ngas admission stops.",
        ),
        (
            "As the level rises, a magnetic float follows it.",
            "As the level rises,\na magnetic float follows it.",
        ),
        (
            "At the high-level signal, the refill pump stops.",
            "At the high-level signal,\nthe refill pump stops.",
        ),
        (
            "through the coil and the stainless steel wall.",
            "through the coil\nand the stainless steel wall.",
        ),
        (
            "The refrigeration loop carries that heat away.",
            "The refrigeration loop\ncarries that heat away.",
        ),
        (
            "Cold water can hold more dissolved carbon dioxide.",
            "Cold water can hold\nmore dissolved carbon dioxide.",
        ),
        (
            "ready for a separate stream of flavor at the faucet.",
            "ready for a separate stream\nof flavor at the faucet.",
        ),
    ];
    if let Some((_, lines)) = custom.iter().find(|(source, _)| *source == text) {
        return (*lines).into();
    }
    if text.len() <= 42 {
        return text.into();
    }
    let words: Vec<_> = text.split_whitespace().collect();
    let choice = (2..words.len().saturating_sub(1))
        .filter_map(|i| {
            let a = words[..i].join(" ");
            let b = words[i..].join(" ");
            (a.len().max(b.len()) <= 44).then_some((a.len().abs_diff(b.len()), a, b))
        })
        .min_by_key(|c| c.0);
    choice.map_or_else(|| text.into(), |(_, a, b)| format!("{a}\n{b}"))
}
pub fn edit(mut args: Args) -> Result<()> {
    let out = args
        .take(&["--out"])
        .map(PathBuf::from)
        .unwrap_or_else(|| here().join("audio"));
    fs::create_dir_all(&out)?;
    let audio = here().join("audio");
    let raw_captions = json(audio.join("captions.json"))?;
    let captions = raw_captions.as_array().context("source captions")?;
    let words: Vec<Aligned> = serde_json::from_value(json(audio.join("narration-words.json"))?)?;
    let config = json(here().join("narration.json"))?;
    let story = json(here().join("story.json"))?;
    let source = audio.join("narration-source.wav");
    let rate = sound::sample_rate(&source)?;
    let samples = sound::read_mono(&source, rate)?;
    let mut inserts = vec![json!({"source_at":0.,"added":1.25,"purpose":"opening handle"})];
    for (phrase, seconds) in [
        (3, 1.40),
        (8, 1.60),
        (13, 1.55),
        (17, 1.25),
        (23, 1.50),
        (24, 0.55),
        (26, 1.25),
        (28, 1.65),
        (30, 0.55),
        (32, 0.70),
        (33, 1.30),
        (34, 0.70),
        (37, 1.05),
    ] {
        let a = captions[phrase]["spoken_end"].as_f64().unwrap() + 0.065;
        let b = captions[phrase + 1]["start"].as_f64().unwrap() - 0.065;
        let half = (rate as f64 * 0.008).round() as usize;
        let start = (a * rate as f64).round().max(0.) as usize;
        let end = (b * rate as f64).round().max(0.) as usize;
        let step = ((rate as f64 * 0.005).round() as usize).max(1);
        let cut = if start < end {
            (start..end)
                .step_by(step)
                .min_by(|&a, &b| {
                    let energy = |x: usize| {
                        let values =
                            &samples[x.saturating_sub(half)..(x + half).min(samples.len())];
                        values.iter().map(|v| v.abs()).sum::<f64>() / values.len().max(1) as f64
                    };
                    energy(a).total_cmp(&energy(b))
                })
                .unwrap()
        } else {
            ((a + b) / 2. * rate as f64).round() as usize
        };
        inserts.push(json!({"source_at":round(cut as f64/rate as f64,6),"added":seconds,"after_caption":phrase,"after_text":captions[phrase]["text"],"purpose":"picture breath"}));
    }
    inserts.push(json!({"source_at":samples.len() as f64/rate as f64,"added":1.40,"purpose":"closing handle"}));
    let mut edited = Vec::new();
    let mut cursor = 0;
    let mut added = 0.;
    for item in &mut inserts {
        let frame = (item["source_at"].as_f64().unwrap() * rate as f64).round() as usize;
        edited.extend_from_slice(&samples[cursor..frame]);
        edited.resize(
            edited.len() + (item["added"].as_f64().unwrap() * rate as f64).round() as usize,
            0.,
        );
        item["edited_at"] = json!(round(item["source_at"].as_f64().unwrap() + added, 6));
        added += item["added"].as_f64().unwrap();
        cursor = frame;
    }
    edited.extend_from_slice(&samples[cursor..]);
    let duration = edited.len() as f64 / rate as f64;
    let shift = |t: f64| {
        round(
            t + inserts
                .iter()
                .filter(|p| p["source_at"].as_f64().unwrap() <= t + 1e-8)
                .map(|p| p["added"].as_f64().unwrap())
                .sum::<f64>(),
            3,
        )
    };
    let mut edited_captions = Vec::new();
    let mut caps = Vec::new();
    for c in captions {
        let start = shift(c["start"].as_f64().unwrap());
        let end = shift(c["spoken_end"].as_f64().unwrap());
        caps.push(Caption {
            start,
            spoken_end: end,
            end: round((end + 0.45).max(start + 1.8), 3),
            text: c["text"].as_str().unwrap().into(),
        });
    }
    for i in 0..caps.len() - 1 {
        caps[i].end = caps[i].end.min(round(caps[i + 1].start - 0.04, 3));
    }
    for cap in &caps {
        edited_captions.push(json!({"text":cap.text,"start":cap.start,"spoken_end":cap.spoken_end,"end":cap.end,"lines":caption_lines(&cap.text).lines().collect::<Vec<_>>()}));
    }
    let expected: Vec<_> = config["text"]
        .as_str()
        .context("script")?
        .split_whitespace()
        .map(str::to_owned)
        .collect();
    let mapping = match_words(&expected, &words)?;
    let canonical:Vec<_>=expected.iter().zip(mapping).map(|(word,(lo,hi))|json!({"word":word,"start":shift(words[lo].start),"end":shift(words[hi].end)})).collect();
    let mut scenes = Vec::new();
    for scene in story["scenes"].as_array().unwrap() {
        let first = caps
            .iter()
            .position(|c| c.text == scene["narration_start"])
            .context("scene opening caption")?;
        let last = caps
            .iter()
            .position(|c| c.text == scene["narration_end"])
            .context("scene closing caption")?;
        scenes.push(json!({"id":scene["id"],"caption_range":[first,last],"voice_start":caps[first].start,"voice_end":caps[last].spoken_end}));
    }
    let fps = story["format"]["fps"].as_f64().unwrap();
    scenes[0]["start"] = json!(0.);
    for i in 1..scenes.len() {
        let at = round(
            ((scenes[i - 1]["voice_end"].as_f64().unwrap()
                + scenes[i]["voice_start"].as_f64().unwrap())
                / 2.
                * fps)
                .round()
                / fps,
            6,
        );
        scenes[i]["start"] = json!(at);
        scenes[i - 1]["end"] = json!(at);
    }
    scenes.last_mut().unwrap()["end"] = json!(duration);
    let raw = out.join("voice-edit-source.wav");
    sound::wav_mono(&raw, &edited, rate)?;
    let final_path = out.join("voice-master.wav");
    run(Command::new("ffmpeg")
        .args(["-v", "error", "-y", "-i"])
        .arg(&raw)
        .args([
            "-af",
            "highpass=f=65,loudnorm=I=-17:TP=-2:LRA=8",
            "-ar",
            "48000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s24le",
        ])
        .arg(&final_path))?;
    let _ = fs::remove_file(raw);
    write(
        out.join("edit-plan.json"),
        serde_json::to_vec_pretty(
            &json!({"source":"narration-source.wav","master":"voice-master.wav","source_sha256":sound::hash(&source)?,"master_sha256":sound::hash(&final_path)?,"source_duration":samples.len() as f64/rate as f64,"duration":duration,"added_seconds":added,"speed_change":false,"insertions":inserts}),
        )?,
    )?;
    for (name, value) in [
        ("captions-edited.json", json!(edited_captions)),
        ("narration-edited-words.json", json!(canonical)),
        (
            "timing.json",
            json!({"duration":duration,"fps":fps,"frames":(duration*fps).round(),"scenes":scenes}),
        ),
    ] {
        write(out.join(name), serde_json::to_vec_pretty(&value)?)?;
    }
    sound::captions(&out, &caps)?;
    println!("{}", final_path.display());
    Ok(())
}
