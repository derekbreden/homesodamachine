//! Optional narration recording calls Gemini and the installed alignment application on demand.
use super::{clock, explainer, sound};
use crate::{Args, json, output, root, run, write};
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{env, fs, os::unix::fs::PermissionsExt, path::PathBuf, process::Command};

fn base64(data: &str) -> Result<Vec<u8>> {
    let mut out = Vec::new();
    let mut accumulator = 0_u32;
    let mut bits = 0;
    for b in data.bytes().filter(|b| !b.is_ascii_whitespace()) {
        if b == b'=' {
            break;
        }
        let value = match b {
            b'A'..=b'Z' => b - b'A',
            b'a'..=b'z' => b - b'a' + 26,
            b'0'..=b'9' => b - b'0' + 52,
            b'+' => 62,
            b'/' => 63,
            _ => anyhow::bail!("invalid audio encoding"),
        };
        accumulator = (accumulator << 6) | value as u32;
        bits += 6;
        if bits >= 8 {
            bits -= 8;
            out.push((accumulator >> bits) as u8);
        }
    }
    Ok(out)
}
pub fn main(mut args: Args) -> Result<()> {
    let film = args.take(&["--film"]).unwrap_or_else(|| "explainer".into());
    let here = if film == "studio" {
        clock::here()
    } else {
        explainer::here()
    };
    let config_path = args
        .take(&["--config"])
        .map(PathBuf::from)
        .unwrap_or_else(|| here.join("narration.json"));
    let mut config = json(config_path)?;
    if let Some(voice) = args.take(&["--voice"]) {
        config["voice"] = json!(voice);
    }
    let output_dir = args.take(&["--output-dir"]);
    let default_output = output_dir.is_none();
    let out = output_dir
        .map(PathBuf::from)
        .unwrap_or_else(|| here.join("audio"));
    fs::create_dir_all(&out)?;
    let align_only = args.flag("--align-only");
    let no_align = args.flag("--no-align");
    let model = args
        .take(&["--whisper-model"])
        .unwrap_or_else(|| "mlx-community/whisper-base.en-mlx".into());
    let source = args
        .take(&["--output"])
        .map(PathBuf::from)
        .unwrap_or_else(|| {
            out.join(if film == "studio" {
                "narration.wav"
            } else {
                "narration-source.wav"
            })
        });
    if !align_only {
        let home = env::var_os("HOME").context("user home")?;
        let key_file = args
            .take(&["--key-file"])
            .map(PathBuf::from)
            .unwrap_or_else(|| PathBuf::from(home).join("Developer/.gemini_key"));
        let mut key = env::var("GEMINI_API_KEY")
            .or_else(|_| env::var("GOOGLE_API_KEY"))
            .or_else(|_| fs::read_to_string(key_file))?
            .trim()
            .to_owned();
        if key.starts_with("export ")
            || key.starts_with("GEMINI_API_KEY=")
            || key.starts_with("GOOGLE_API_KEY=")
        {
            key = key
                .split_once('=')
                .context("credential assignment")?
                .1
                .trim()
                .trim_matches(['\'', '"'])
                .into();
        }
        ensure!(!key.is_empty(), "configured local narration credential");
        let scratch = crate::video::Scratch::new("film-narration", false)?;
        let header = scratch.0.join("headers");
        write(
            &header,
            format!("Content-Type: application/json\nx-goog-api-key: {key}\n"),
        )?;
        fs::set_permissions(&header, fs::Permissions::from_mode(0o600))?;
        let request = scratch.0.join("request.json");
        write(
            &request,
            serde_json::to_vec(
                &json!({"model":config["model"],"input":[{"type":"user_input","content":[{"type":"text","text":config["text"],"annotations":[{"type":"speech_metadata","style":config["style"]}]}]}],"response_format":{"type":"audio","mime_type":"audio/wav","sample_rate":24000},"generation_config":{"speech_config":[{"voice":config["voice"]}]}}),
            )?,
        )?;
        let response = output(
            Command::new("curl")
                .args([
                    "--silent",
                    "--show-error",
                    "--fail-with-body",
                    "--max-time",
                    "600",
                    "--header",
                ])
                .arg(format!("@{}", header.display()))
                .arg("--data-binary")
                .arg(format!("@{}", request.display()))
                .arg("https://generativelanguage.googleapis.com/v1beta/interactions"),
        )?;
        let result: Value = serde_json::from_slice(&response.stdout)?;
        let blocks: Vec<_> = result["steps"]
            .as_array()
            .context("narration response steps")?
            .iter()
            .filter(|s| s["type"] == "model_output")
            .flat_map(|s| s["content"].as_array().into_iter().flatten())
            .filter(|b| b["type"] == "audio")
            .collect();
        let block = blocks.last().context("service audio output")?;
        let recording = base64(block["data"].as_str().context("encoded service audio")?)?;
        ensure!(
            recording.starts_with(b"RIFF"),
            "service returns requested WAV audio"
        );
        write(&source, &recording)?;
        let generated = output(Command::new("date").args(["-u", "+%Y-%m-%dT%H:%M:%SZ"]))?;
        write(
            out.join("provenance.json"),
            serde_json::to_vec_pretty(
                &json!({"service":"Google Gemini Interactions API","model":config["model"],"voice":config["voice"],"generated_at":String::from_utf8(generated.stdout)?.trim(),"script_sha256":format!("{:x}",Sha256::digest(config["text"].as_str().unwrap())),"source_sha256":sound::hash(&source)?}),
            )?,
        )?;
        if film != "studio" {
            run(Command::new("ffmpeg")
                .args(["-v", "error", "-y", "-i"])
                .arg(&source)
                .args(["-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le"])
                .arg(out.join("narration.wav")))?;
        }
    }
    if !no_align {
        let alignment_out = if film == "studio" && default_output {
            here.clone()
        } else {
            out.clone()
        };
        fs::create_dir_all(&alignment_out)?;
        run(
            Command::new(root().join("tools/video-venv/bin/mlx_whisper"))
                .arg(&source)
                .args([
                    "--model",
                    &model,
                    "--language",
                    "en",
                    "--word-timestamps",
                    "True",
                    "--condition-on-previous-text",
                    "False",
                    "--verbose",
                    "False",
                    "--temperature",
                    "0",
                    "--initial-prompt",
                    config["text"].as_str().context("script")?,
                    "--output-format",
                    "json",
                    "--output-name",
                    "transcription",
                    "--output-dir",
                ])
                .arg(&alignment_out),
        )?;
        let transcription = json(alignment_out.join("transcription.json"))?;
        let words:Vec<Value>=transcription["segments"].as_array().context("aligned segments")?.iter().flat_map(|s|s["words"].as_array().into_iter().flatten()).filter(|w|w["word"].as_str().is_some_and(|w|!w.trim().is_empty())).map(|w|json!({"word":w["word"].as_str().unwrap().trim(),"start":w["start"],"end":w["end"],"probability":w["probability"]})).collect();
        write(
            alignment_out.join("narration-words.json"),
            serde_json::to_vec_pretty(&words)?,
        )?;
        if let Some(phrases) = config["caption_phrases"].as_array() {
            let aligned: Vec<sound::Aligned> = serde_json::from_value(json!(words))?;
            let expected: Vec<_> = config["text"]
                .as_str()
                .unwrap()
                .split_whitespace()
                .map(str::to_owned)
                .collect();
            let mapping = explainer::match_words(&expected, &aligned)?;
            let mut cursor = 0;
            let mut captions = Vec::new();
            for phrase in phrases {
                let text = phrase.as_str().context("caption phrase")?;
                let count = text.split_whitespace().count();
                let (first, _) = mapping[cursor];
                let (_, last) = mapping[cursor + count - 1];
                captions.push(sound::Caption {
                    start: aligned[first].start,
                    spoken_end: aligned[last].end,
                    end: aligned[last].end + 0.18,
                    text: text.into(),
                });
                cursor += count;
            }
            for i in 0..captions.len().saturating_sub(1) {
                captions[i].end = captions[i]
                    .spoken_end
                    .max(captions[i].end.min(captions[i + 1].start - 0.035));
            }
            write(
                alignment_out.join("captions.json"),
                serde_json::to_vec_pretty(&captions)?,
            )?;
            sound::captions(&alignment_out, &captions)?;
        }
    }
    println!("{}", source.display());
    Ok(())
}
