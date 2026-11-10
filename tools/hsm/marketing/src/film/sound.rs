//! Native sound synthesis and source-sample edits build the films' saved narration, score and effects.
use super::clock::{self, Story};
use crate::scene::Random;
use crate::{Args, json, output, run, write};
use anyhow::{Context, Result, ensure};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    f64::consts::{PI, TAU},
    fs,
    path::{Path, PathBuf},
    process::Command,
};

pub const RATE: usize = 48000;
pub type Stereo = Vec<[f64; 2]>;
#[derive(Clone, Serialize, Deserialize)]
pub struct Caption {
    pub start: f64,
    pub spoken_end: f64,
    pub end: f64,
    pub text: String,
}
#[derive(Deserialize)]
pub struct Aligned {
    pub word: String,
    pub start: f64,
    pub end: f64,
}
pub fn hash(path: &Path) -> Result<String> {
    Ok(format!("{:x}", Sha256::digest(fs::read(path)?)))
}
pub fn stamp(t: f64, separator: char) -> String {
    let n = (t.max(0.) * 1000.).round() as u64;
    format!(
        "{:02}:{:02}:{:02}{separator}{:03}",
        n / 3600000,
        n / 60000 % 60,
        n / 1000 % 60,
        n % 1000
    )
}
pub fn tokens(text: &str) -> Vec<String> {
    text.replace('’', "'")
        .to_lowercase()
        .split(|c: char| !c.is_ascii_alphanumeric() && c != '\'' && c != '-')
        .filter(|s| !s.is_empty())
        .map(str::to_owned)
        .collect()
}
pub fn captions(out: &Path, captions: &[Caption]) -> Result<()> {
    for (ext, separator) in [("vtt", '.'), ("srt", ',')] {
        let mut text = if ext == "vtt" {
            "WEBVTT\n\n".to_string()
        } else {
            String::new()
        };
        for (i, cap) in captions.iter().enumerate() {
            if ext == "srt" {
                text.push_str(&format!("{}\n", i + 1));
            }
            text.push_str(&format!(
                "{} --> {}\n{}\n\n",
                stamp(cap.start, separator),
                stamp(cap.end, separator),
                wrap(&cap.text, 42)
            ));
        }
        write(out.join(format!("film.{ext}")), text)?;
    }
    Ok(())
}
fn wrap(text: &str, width: usize) -> String {
    let mut lines = Vec::new();
    let mut line = String::new();
    for word in text.split_whitespace() {
        if !line.is_empty() && line.chars().count() + word.chars().count() + 1 > width {
            lines.push(line);
            line = String::new();
        }
        if !line.is_empty() {
            line.push(' ');
        }
        line.push_str(word);
    }
    if !line.is_empty() {
        lines.push(line);
    }
    lines.join("\n")
}
pub fn read_mono(path: &Path, rate: usize) -> Result<Vec<f64>> {
    let out = output(
        Command::new("ffmpeg")
            .args(["-v", "error", "-i"])
            .arg(path)
            .args(["-f", "f64le", "-ac", "1", "-ar", &rate.to_string(), "-"]),
    )?;
    Ok(out
        .stdout
        .chunks_exact(8)
        .map(|p| f64::from_le_bytes(p.try_into().unwrap()))
        .collect())
}
fn read_stereo(path: &Path) -> Result<Stereo> {
    let out = output(
        Command::new("ffmpeg")
            .args(["-v", "error", "-i"])
            .arg(path)
            .args(["-f", "f64le", "-ac", "2", "-ar", "48000", "-"]),
    )?;
    Ok(out
        .stdout
        .chunks_exact(16)
        .map(|p| {
            [
                f64::from_le_bytes(p[..8].try_into().unwrap()),
                f64::from_le_bytes(p[8..].try_into().unwrap()),
            ]
        })
        .collect())
}
pub fn sample_rate(path: &Path) -> Result<usize> {
    let out = output(
        Command::new("ffprobe")
            .args([
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=sample_rate",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
            ])
            .arg(path),
    )?;
    Ok(std::str::from_utf8(&out.stdout)?.trim().parse()?)
}
pub fn wav(path: &Path, samples: &[[f64; 2]]) -> Result<()> {
    let mut out = Vec::with_capacity(44 + samples.len() * 4);
    out.extend_from_slice(b"RIFF");
    out.extend_from_slice(&(36 + samples.len() as u32 * 4).to_le_bytes());
    out.extend_from_slice(b"WAVEfmt ");
    out.extend_from_slice(&16_u32.to_le_bytes());
    for n in [1_u16, 2] {
        out.extend_from_slice(&n.to_le_bytes());
    }
    out.extend_from_slice(&(RATE as u32).to_le_bytes());
    out.extend_from_slice(&(RATE as u32 * 4).to_le_bytes());
    out.extend_from_slice(&4_u16.to_le_bytes());
    out.extend_from_slice(&16_u16.to_le_bytes());
    out.extend_from_slice(b"data");
    out.extend_from_slice(&(samples.len() as u32 * 4).to_le_bytes());
    for value in samples.iter().flatten() {
        out.extend_from_slice(&((value.clamp(-1., 1.) * 32767.) as i16).to_le_bytes());
    }
    write(path, out)
}
pub fn wav_mono(path: &Path, samples: &[f64], rate: usize) -> Result<()> {
    let raw = path.with_extension("f64");
    let mut bytes = Vec::with_capacity(samples.len() * 8);
    for x in samples {
        bytes.extend_from_slice(&x.to_le_bytes());
    }
    write(&raw, bytes)?;
    let result = run(Command::new("ffmpeg")
        .args([
            "-v",
            "error",
            "-y",
            "-f",
            "f64le",
            "-ar",
            &rate.to_string(),
            "-ac",
            "1",
            "-i",
        ])
        .arg(&raw)
        .args(["-c:a", "pcm_s16le"])
        .arg(path));
    let _ = fs::remove_file(raw);
    result
}
pub fn measure(path: &Path, target: f64, peak: f64, lra: f64) -> Result<Value> {
    let out = output(
        Command::new("ffmpeg")
            .args(["-hide_banner", "-i"])
            .arg(path)
            .args([
                "-af",
                &format!("loudnorm=I={target}:TP={peak}:LRA={lra}:print_format=json"),
                "-f",
                "null",
                "-",
            ]),
    )?;
    let stderr = String::from_utf8(out.stderr)?;
    let start = stderr.rfind('{').context("loudness report")?;
    Ok(serde_json::from_str(
        &stderr[start
            ..stderr[start..]
                .find('}')
                .map(|n| start + n + 1)
                .context("loudness report end")?],
    )?)
}
fn normalize(
    source: &Path,
    target: &Path,
    integrated: f64,
    peak: f64,
    lra: f64,
    bits: usize,
) -> Result<Value> {
    let levels = measure(source, integrated, peak, lra)?;
    let mut filter = format!("loudnorm=I={integrated}:TP={peak}:LRA={lra}:linear=true");
    for (key, value) in [
        ("measured_I", "input_i"),
        ("measured_TP", "input_tp"),
        ("measured_LRA", "input_lra"),
        ("measured_thresh", "input_thresh"),
        ("offset", "target_offset"),
    ] {
        filter.push_str(&format!(
            ":{key}={}",
            levels[value].as_str().context("loudness value")?
        ));
    }
    run(Command::new("ffmpeg")
        .args(["-v", "error", "-y", "-i"])
        .arg(source)
        .args([
            "-af",
            &filter,
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            if bits == 24 { "pcm_s24le" } else { "pcm_s16le" },
        ])
        .arg(target))?;
    Ok(levels)
}
pub fn taper(samples: &mut [f64], attack: f64, release: f64, rate: usize) {
    let a = ((attack * rate as f64).round() as usize).min(samples.len());
    let r = ((release * rate as f64).round() as usize).min(samples.len());
    for i in 0..a {
        samples[i] *= (PI * 0.5 * i as f64 / a.saturating_sub(1).max(1) as f64)
            .sin()
            .powi(2);
    }
    let len = samples.len();
    for i in 0..r {
        samples[len - r + i] *= (PI * 0.5 * i as f64 / r.saturating_sub(1).max(1) as f64)
            .cos()
            .powi(2);
    }
}
fn biquad(samples: &mut [f64], frequency: f64, high: bool) {
    let w = TAU * frequency / RATE as f64;
    let c = w.cos();
    let alpha = w.sin() / 2_f64.sqrt();
    let a0 = 1. + alpha;
    let sign = if high { -1. } else { 1. };
    let b0 = (1. - sign * c) / 2. / a0;
    let b1 = sign * (1. - sign * c) / a0;
    let b2 = b0;
    let a1 = -2. * c / a0;
    let a2 = (1. - alpha) / a0;
    let (mut z1, mut z2) = (0., 0.);
    for x in samples {
        let y = b0 * *x + z1;
        z1 = b1 * *x - a1 * y + z2;
        z2 = b2 * *x - a2 * y;
        *x = y;
    }
}
fn filter(samples: &mut [f64], lo: Option<f64>, hi: Option<f64>) {
    if let Some(lo) = lo {
        biquad(samples, lo, true);
    }
    if let Some(hi) = hi {
        biquad(samples, hi, false);
    }
}
fn stereo_filter(samples: &mut [[f64; 2]], lo: f64, hi: f64) {
    for ch in 0..2 {
        let mut channel: Vec<_> = samples.iter().map(|p| p[ch]).collect();
        filter(&mut channel, Some(lo), Some(hi));
        for (p, x) in samples.iter_mut().zip(channel) {
            p[ch] = x;
        }
    }
}
fn add(dest: &mut [[f64; 2]], source: &[f64], at: f64, gain: f64, pan: f64) {
    if at < 0. {
        return;
    }
    let start = (at * RATE as f64).round() as usize;
    if start >= dest.len() {
        return;
    }
    let angle = (pan.clamp(-1., 1.) + 1.) * PI / 4.;
    for (out, &x) in dest[start..].iter_mut().zip(source) {
        out[0] += x * gain * angle.cos();
        out[1] += x * gain * angle.sin();
    }
}
fn rms(values: impl Iterator<Item = f64>) -> f64 {
    let mut sum = 0.;
    let mut count = 0;
    for v in values {
        sum += v * v;
        count += 1;
    }
    (sum / count.max(1) as f64).sqrt()
}
fn peak_normalize(values: &mut [f64]) {
    let peak = values.iter().map(|x| x.abs()).fold(1e-9, f64::max);
    for v in values {
        *v /= peak;
    }
}
struct Synth {
    rng: Random,
}
impl Synth {
    fn new(seed: u64) -> Self {
        Self {
            rng: Random::new(seed),
        }
    }
    fn noise(&mut self, seconds: f64, lo: f64, hi: f64, unit: bool) -> Vec<f64> {
        let mut samples = (0..(seconds * RATE as f64).round() as usize)
            .map(|_| {
                let a = self.rng.uniform(1e-12, 1.);
                let b = self.rng.uniform(0., TAU);
                (-2. * a.ln()).sqrt() * b.cos()
            })
            .collect::<Vec<_>>();
        filter(&mut samples, Some(lo), Some(hi));
        if unit {
            let gain = rms(samples.iter().copied()).max(1e-8);
            for x in &mut samples {
                *x /= gain;
            }
        }
        samples
    }
    fn pluck(&mut self, midi: f64, seconds: f64, damped: bool, decay: Option<f64>) -> Vec<f64> {
        let f = 440. * 2_f64.powf((midi - 69.) / 12.);
        let life = decay.unwrap_or(if damped { 0.30 } else { 0.78 });
        let mut samples = self.noise(seconds, 700., 5300., false);
        for (i, x) in samples.iter_mut().enumerate() {
            let t = i as f64 / RATE as f64;
            *x *= (-t / 0.008).exp() * 0.048;
            for partial in 1..=8 {
                let p = partial as f64;
                let amp = if partial % 3 == 0 { -1. } else { 1. } * 0.78_f64.powi(partial - 1) / p;
                *x += amp
                    * (-t / (life / (1. + 0.31 * (p - 1.)))).exp()
                    * ((TAU * f * p * t).sin() + 0.29 * (TAU * f * p * 1.0024 * t + 0.17).sin());
            }
        }
        filter(&mut samples, None, Some(4700.));
        taper(&mut samples, 0.0025, 0.14, RATE);
        samples
    }
    fn struck(&mut self, midi: f64, seconds: f64) -> Vec<f64> {
        let f = 440. * 2_f64.powf((midi - 69.) / 12.);
        let mut samples = (0..(seconds * RATE as f64).round() as usize)
            .map(|i| {
                let t = i as f64 / RATE as f64;
                (TAU * f * t).sin() * (-t / 1.30).exp()
                    + 0.20 * (TAU * f * 2.002 * t).sin() * (-t / 0.55).exp()
                    + 0.055 * (TAU * f * 3.006 * t).sin() * (-t / 0.24).exp()
            })
            .collect::<Vec<_>>();
        taper(&mut samples, 0.009, 0.24, RATE);
        samples
    }
    fn bass(&mut self, midi: f64) -> Vec<f64> {
        let f = 440. * 2_f64.powf((midi - 69.) / 12.);
        let mut samples = (0..(0.85 * RATE as f64) as usize)
            .map(|i| {
                let t = i as f64 / RATE as f64;
                ((TAU * f * t).sin() + 0.19 * (2. * TAU * f * t).sin()) * (-t / 0.27).exp()
            })
            .collect::<Vec<_>>();
        taper(&mut samples, 0.009, 0.07, RATE);
        samples
    }
    fn rim(&mut self) -> Vec<f64> {
        let mut samples = self.noise(0.075, 850., 3800., false);
        for (i, x) in samples.iter_mut().enumerate() {
            let t = i as f64 / RATE as f64;
            *x = *x * (-t / 0.008).exp() + 0.13 * (TAU * 410. * t).sin() * (-t / 0.014).exp();
        }
        taper(&mut samples, 0.0007, 0.015, RATE);
        samples
    }
    fn contact(&mut self, index: usize, can: bool, seconds: f64) -> Vec<f64> {
        let k = index % 3;
        let mut samples = self.noise(
            seconds,
            if can { 90. } else { 180. },
            if can { 1900. } else { 2900. },
            false,
        );
        for (i, x) in samples.iter_mut().enumerate() {
            let t = i as f64 / RATE as f64;
            if can {
                let v = [1., 0.975, 1.022][k];
                *x = *x * (-t / 0.012).exp() * 0.58
                    + 0.46 * (TAU * 155. * v * t).sin() * (-t / 0.036).exp();
                for (f, a, d) in [
                    (484., 0.30, 0.055),
                    (913., 0.15, 0.043),
                    (1741., 0.055, 0.025),
                ] {
                    *x += a * (TAU * f * v * t).sin() * (-t / d).exp();
                }
            } else {
                let f = [155., 126., 102.][k];
                *x = *x * (-t / 0.014).exp() * 0.44
                    + 0.58 * (TAU * f * t).sin() * (-t / (0.027 + k as f64 * 0.006)).exp()
                    + 0.18 * (TAU * f * 2.19 * t).sin() * (-t / 0.018).exp();
            }
        }
        taper(
            &mut samples,
            if can { 0.001 } else { 0.0007 },
            if can { 0.06 } else { 0.05 },
            RATE,
        );
        peak_normalize(&mut samples);
        samples
    }
    fn movement(&mut self, seconds: f64, load: bool) -> Vec<f64> {
        let mut samples = self.noise(
            seconds,
            if load { 100. } else { 220. },
            if load { 780. } else { 2700. },
            false,
        );
        for (i, x) in samples.iter_mut().enumerate() {
            let t = i as f64 / RATE as f64;
            *x *= (PI * t / seconds).sin().powi(2)
                * if load {
                    0.72 + 0.28 * (TAU * 6.8 * t).sin().powi(2)
                } else {
                    1.
                };
        }
        taper(
            &mut samples,
            if load { 0.08 } else { 0.012 },
            if load { 0.12 } else { 0.045 },
            RATE,
        );
        peak_normalize(&mut samples);
        samples
    }
    fn fizz(&mut self, seconds: f64, strength: f64) -> Vec<f64> {
        let mut samples = self.noise(seconds, 3600., 11200., false);
        for x in &mut samples {
            *x *= 0.0033;
        }
        let mut at = 0.;
        while at < seconds - 0.025 {
            at += self.rng.uniform(0.016, 0.068);
            let f = self.rng.uniform(2700., 7100.);
            let gain = self.rng.uniform(0.002, 0.008);
            let mut grain = (0..(0.022 * RATE as f64).round() as usize)
                .map(|i| {
                    let t = i as f64 / RATE as f64;
                    (TAU * f * (t - 4. * t * t)).sin() * (-t / 0.0025).exp() * gain
                })
                .collect::<Vec<_>>();
            taper(&mut grain, 0.0003, 0.004, RATE);
            let start = (at * RATE as f64).round() as usize;
            if start >= samples.len() {
                break;
            }
            for (x, g) in samples[start..].iter_mut().zip(grain) {
                *x += g;
            }
        }
        for (i, x) in samples.iter_mut().enumerate() {
            *x *= (0.65 + 0.35 * (-(i as f64 / RATE as f64) / 1.8).exp()) * strength;
        }
        taper(&mut samples, 0.004, 0.48_f64.min(seconds * 0.22), RATE);
        samples
    }
    fn pour(&mut self, seconds: f64) -> Vec<f64> {
        let air = self.noise(seconds, 1850., 8800., false);
        let body = self.noise(seconds, 180., 1350., false);
        let splash = self.noise(seconds, 620., 4700., false);
        let mut samples = air
            .into_iter()
            .zip(body)
            .zip(splash)
            .enumerate()
            .map(|(i, ((a, b), s))| {
                let t = i as f64 / RATE as f64;
                let u = t / seconds;
                let movement =
                    0.92 + 0.055 * (TAU * 2.17 * t).sin() + 0.035 * (TAU * 6.13 * t + 0.8).sin();
                (0.034 * a * (1. - 0.18 * u) + 0.080 * s + 0.052 * b * (0.7 + 0.3 * u)) * movement
                    + 0.006
                        * (TAU * (1050. * t - 290. * t * t / (2. * seconds))).sin()
                        * (0.7 + 0.3 * (TAU * 9.7 * t).sin().powi(2))
            })
            .collect::<Vec<_>>();
        let mut at = 0.;
        while at < seconds - 0.05 {
            at += self.rng.uniform(0.065, 0.16);
            let f = self.rng.uniform(900., 2400.) * (1. - 0.13 * at / seconds);
            let gain = self.rng.uniform(0.003, 0.009);
            let mut grain = (0..(0.035 * RATE as f64).round() as usize)
                .map(|i| {
                    let t = i as f64 / RATE as f64;
                    (TAU * f * (t - 5. * t * t)).sin() * (-t / 0.004).exp() * gain
                })
                .collect::<Vec<_>>();
            taper(&mut grain, 0.0004, 0.005, RATE);
            let start = (at * RATE as f64).round() as usize;
            if start >= samples.len() {
                break;
            }
            for (x, g) in samples[start..].iter_mut().zip(grain) {
                *x += g;
            }
        }
        taper(&mut samples, 0.002, 0.012, RATE);
        samples
    }
}
fn speech_rms(samples: &[f64], rate: usize) -> Result<f64> {
    let active: Vec<_> = samples
        .chunks((0.020 * rate as f64).round() as usize)
        .filter(|c| rms(c.iter().copied()) > 0.01)
        .flatten()
        .copied()
        .collect();
    ensure!(!active.is_empty(), "active pickup speech");
    Ok(rms(active.into_iter()))
}
fn voice(out: &Path, story: &Story, count: usize) -> Result<(Stereo, Vec<Caption>, Value)> {
    let here = clock::here();
    let source = here.join("audio/narration.wav");
    let rate = sample_rate(&source)?;
    let original = read_mono(&source, rate)?;
    let mut samples = original.clone();
    let mut pauses = story.narration_pauses.clone();
    pauses.sort_by_key(|p| p.source_sample);
    let mut edited = Vec::new();
    let mut cursor = 0;
    for pause in &pauses {
        let at = pause.source_sample;
        ensure!(
            at > 0 && at < samples.len(),
            "narration pause within source"
        );
        let fade = (0.003 * rate as f64).round() as usize;
        let before = at.saturating_sub(fade);
        taper(&mut samples[before..at], 0., 0.003, rate);
        let after = (at + fade).min(samples.len());
        taper(&mut samples[at..after], 0.003, 0., rate);
        edited.extend_from_slice(&samples[cursor..at]);
        edited.resize(
            edited.len() + (pause.frames as f64 * rate as f64 / story.fps).round() as usize,
            0.,
        );
        cursor = at;
    }
    edited.extend_from_slice(&samples[cursor..]);
    let edited_path = out.join("voice-source-edit.wav");
    wav_mono(&edited_path, &edited, rate)?;
    let edited = read_mono(&edited_path, RATE)?;
    let mut voice = vec![[0.; 2]; count];
    ensure!(
        (story.narration_offset * RATE as f64).round() as usize + edited.len() <= count,
        "voice extends past picture"
    );
    add(
        &mut voice,
        &edited,
        story.narration_offset,
        2_f64.sqrt(),
        0.,
    );
    let mut pickup_report = Value::Null;
    if let Some(pickup) = &story.narration_pickup {
        let path = here.join(&pickup.source);
        let prate = sample_rate(&path)?;
        let recording = read_mono(&path, prate)?;
        let clips: Vec<_> = pickup
            .phrases
            .iter()
            .map(|p| {
                recording[(p.source_start * prate as f64).round() as usize
                    ..(p.source_end * prate as f64).round() as usize]
                    .to_vec()
            })
            .collect();
        let reference = &original[(pickup.replace_source[0] * rate as f64).round() as usize
            ..(pickup.replace_source[1] * rate as f64).round() as usize];
        let gain = speech_rms(reference, rate)?
            / speech_rms(&clips.iter().flatten().copied().collect::<Vec<_>>(), prate)?;
        let lo = (story.picture_time(pickup.replace_source[0], rate as f64) * RATE as f64).round()
            as usize;
        let hi = (story.picture_time(pickup.replace_source[1], rate as f64) * RATE as f64).round()
            as usize;
        voice[lo..hi].fill([0.; 2]);
        let fade = (0.003 * RATE as f64).round() as usize;
        for ch in 0..2 {
            for i in 0..fade {
                if lo >= fade {
                    voice[lo - fade + i][ch] *=
                        (PI * 0.5 * i as f64 / (fade - 1) as f64).cos().powi(2);
                }
                if hi + i < voice.len() {
                    voice[hi + i][ch] *= (PI * 0.5 * i as f64 / (fade - 1) as f64).sin().powi(2);
                }
            }
        }
        for (p, clip) in pickup.phrases.iter().zip(clips) {
            wav_mono(&edited_path, &clip, prate)?;
            let mut clip = read_mono(&edited_path, RATE)?;
            taper(&mut clip, 0.003, 0.003, RATE);
            let start = story.shot(&p.scene)?.start + p.at;
            add(&mut voice, &clip, start, gain * 2_f64.sqrt(), 0.);
        }
        pickup_report = json!({"source":pickup.source,"source_sha256":hash(&path)?,"gain_db":20.*gain.log10(),"muted_picture_start":lo as f64/RATE as f64,"muted_picture_end":hi as f64/RATE as f64});
    }
    wav(&out.join("voice-edited.wav"), &voice)?;
    run(Command::new("ffmpeg")
        .args(["-v", "error", "-y", "-i"])
        .arg(out.join("voice-edited.wav"))
        .args([
            "-af",
            "highpass=f=65,loudnorm=I=-18.5:TP=-3:LRA=14",
            "-ar",
            "48000",
            "-c:a",
            "pcm_s16le",
        ])
        .arg(out.join("voice-master.wav")))?;
    let words: Vec<Aligned> = serde_json::from_value(json(here.join("narration-words.json"))?)?;
    let config = json(here.join("narration.json"))?;
    let word_tokens: Vec<_> = words
        .iter()
        .flat_map(|word| {
            tokens(&word.word)
                .into_iter()
                .map(move |token| (token, word))
        })
        .collect();
    ensure!(
        word_tokens.iter().map(|p| p.0.clone()).collect::<Vec<_>>()
            == tokens(config["text"].as_str().context("narration text")?),
        "saved alignment matches script"
    );
    let mut phrases: Vec<String> = config["caption_phrases"]
        .as_array()
        .context("caption phrases")?
        .iter()
        .map(|p| p.as_str().unwrap().into())
        .collect();
    if story.separate_benefit_captions {
        phrases = phrases
            .into_iter()
            .flat_map(|p| {
                if tokens(&p) == ["cold", "fully", "carbonated"] {
                    vec!["Cold.".into(), "Fully carbonated.".into()]
                } else {
                    vec![p]
                }
            })
            .collect();
    }
    let mut caps = Vec::new();
    let mut cursor = 0;
    let mut occurrences = std::collections::BTreeMap::new();
    for phrase in phrases {
        let key = tokens(&phrase);
        let selected = &word_tokens[cursor..cursor + key.len()];
        let occurrence = occurrences.entry(key.clone()).or_insert(0);
        *occurrence += 1;
        let mut source_start = selected[0].1.start;
        for onset in &story.caption_source_onsets {
            if tokens(&onset.text) == key && onset.occurrence.unwrap_or(1) == *occurrence {
                source_start = onset.source_time;
            }
        }
        let mut start = story.picture_time(source_start, rate as f64);
        let mut end = story.picture_time(selected.last().unwrap().1.end, rate as f64);
        if let Some(pickup) = &story.narration_pickup {
            for p in &pickup.phrases {
                if tokens(&p.text) == key {
                    let at = story.shot(&p.scene)?.start + p.at;
                    start = at + p.first_word - p.source_start;
                    end = at + p.last_word - p.source_start;
                }
            }
        }
        caps.push(Caption {
            start: (start * 1000.).round() / 1000.,
            spoken_end: (end * 1000.).round() / 1000.,
            end: 0.,
            text: phrase,
        });
        cursor += key.len();
    }
    for i in 0..caps.len() {
        let next = caps.get(i + 1).map_or(story.duration - 0.2, |c| c.start);
        caps[i].end = ((next - 0.08).min((caps[i].spoken_end + 0.24).max(caps[i].start + 1.15))
            * 1000.)
            .round()
            / 1000.;
    }
    captions(out, &caps)?;
    let _ = fs::remove_file(edited_path);
    let report = json!({"source":"audio/narration.wav","source_sha256":hash(&source)?,"start":story.narration_offset,"last_word_at":story.picture_time(words.last().context("spoken words")?.end,rate as f64),"timeline_insertions":pauses,"handling_pickup":pickup_report,"recorded_word_speed_changed":false});
    Ok((read_stereo(&out.join("voice-master.wav"))?, caps, report))
}
pub fn studio(mut args: Args) -> Result<()> {
    let timing = args.take(&["--timing"]).map(PathBuf::from);
    let out = args
        .take(&["--out"])
        .map(PathBuf::from)
        .unwrap_or_else(|| clock::here().join("out"));
    fs::create_dir_all(&out)?;
    let story = Story::read(timing.as_deref())?;
    let count = (story.duration * RATE as f64).round() as usize;
    let (voice, caps, performance) = voice(&out, &story, count)?;
    let base = Story::read(None)?;
    let rate = sample_rate(&clock::here().join("audio/narration.wav"))?;
    let mut synth = Synth::new(301814);
    let mut score = vec![[0.; 2]; count];
    let mut tail = score.clone();
    let mut effects = score.clone();
    let mut events = Vec::<Value>::new();
    let reveal = story.shot("hero")?.start;
    let water = story.shot("pour")?.start;
    let sensory = story.shot("sensory")?.start;
    let serve = story.shot("serve")?.start;
    let routine = base.shot("case")?.start;
    let base_reveal = base.shot("hero")?.start;
    let tempo = story.score["tempo_bpm"].as_f64().unwrap_or(60. / 0.5625);
    let beat = 60. / tempo;
    let origin = routine + 0.125;
    let score_time = |time: f64| story.picture_time(time - story.narration_offset, rate as f64);
    let notes = [66., 69., 64., 66., 71., 69., 66., 64.];
    for i in 0..((base_reveal - origin) / beat).ceil().max(0.) as usize {
        let at = origin + i as f64 * beat;
        let progress = ((at - routine) / (base_reveal - routine).max(0.01)).clamp(0., 1.);
        let at = score_time(at);
        let gain = if i % 2 == 0 { 0.016 } else { 0.012 } * (1. + 0.24 * progress);
        add(
            &mut score,
            &synth.pluck(notes[i % 8], 0.88, true, None),
            at,
            gain,
            if i % 2 == 0 { -0.16 } else { 0.16 },
        );
        add(
            &mut score,
            &synth.rim(),
            at,
            if i % 2 == 0 { 0.0045 } else { 0.0025 } * (1. + 0.20 * progress),
            0.14,
        );
        if i % 2 == 0 {
            add(
                &mut score,
                &synth.bass([47., 43., 45., 47.][(i / 8) % 4]),
                at,
                0.019 * (1. + 0.22 * progress),
                -0.025,
            );
        }
    }
    for (i, midi) in [50., 57., 64., 66.].into_iter().enumerate() {
        add(
            &mut score,
            &synth.pluck(midi, 1.7, false, None),
            i as f64 * 0.019,
            0.015 * (1. - i as f64 * 0.08),
            (i as f64 - 1.5) * 0.12,
        );
    }
    let voicings = [
        [47., 54., 57., 62.],
        [43., 54., 57., 62.],
        [45., 52., 55., 62.],
        [47., 54., 57., 62.],
    ];
    let cells = ((base_reveal - routine) / 4.5).ceil() as usize;
    let carry = story.score["reveal_transition"] == "decay";
    for cell in 0..cells {
        let at = score_time(routine + cell as f64 * 4.5);
        for (i, midi) in voicings[cell % 4].into_iter().enumerate() {
            let is_tail = carry && cell == cells - 1;
            let duration = if is_tail {
                reveal + 0.35 - at - i as f64 * 0.019
            } else {
                1.7
            };
            add(
                if is_tail { &mut tail } else { &mut score },
                &synth.pluck(
                    midi,
                    duration,
                    false,
                    if is_tail { Some(1.25) } else { None },
                ),
                at + i as f64 * 0.019,
                0.015 * (1. - i as f64 * 0.08),
                (i as f64 - 1.5) * 0.12,
            );
        }
    }
    let extra = story.shot("question")?.extra_frames.unwrap_or(0) as f64 / story.fps;
    let clear = ((reveal - extra - 0.20).max(0.) * RATE as f64).round() as usize;
    let fade = clear.saturating_sub((0.22 * RATE as f64).round() as usize);
    for i in fade..clear {
        let gain = (PI * 0.5 * (i - fade) as f64 / (clear - fade).max(1) as f64)
            .cos()
            .powi(2);
        for x in &mut score[i] {
            *x *= gain;
        }
    }
    score[clear..].fill([0.; 2]);
    if carry {
        for (x, y) in score.iter_mut().zip(tail) {
            x[0] += y[0];
            x[1] += y[1];
        }
    }
    let mut chords = vec![
        (
            reveal,
            vec![50., 57., 59., 64., 66.],
            0.027,
            3.1_f64.max(water - reveal + 0.35),
        ),
        (water, vec![47., 57., 62., 66.], 0.014, 2.5),
        (
            sensory,
            vec![43., 54., 59., 62.],
            0.018,
            if story.shot("sensory")?.extra_frames.is_some() {
                2.5_f64.max(serve - sensory + 0.20)
            } else {
                2.5
            },
        ),
        (serve, vec![50., 57., 62., 66.], 0.021, 2.6),
    ];
    let last = caps.last().context("closing caption")?;
    if last.start - serve > 0.65 {
        chords.push((last.start + 0.08, vec![50., 57., 62., 66.], 0.021, 2.65));
    }
    for (at, notes, gain, duration) in chords {
        for (i, &midi) in notes.iter().enumerate() {
            add(
                &mut score,
                &synth.struck(midi, duration),
                at + i as f64 * 0.021,
                gain * (1. - i as f64 * 0.10),
                (i as f64 - (notes.len() - 1) as f64 / 2.) * 0.12,
            );
        }
    }
    let last_note = (last.spoken_end + 0.82).min(story.duration - 1.55);
    add(
        &mut score,
        &synth.struck(69., 1.65),
        serve.max(last_note - 0.65),
        0.014,
        0.14,
    );
    add(
        &mut score,
        &synth.struck(62., 1.65),
        (serve + 0.10).max(last_note),
        0.021,
        -0.08,
    );
    let dry = score.clone();
    for ch in 0..2 {
        for (delay, gain) in [(0.043, 0.14), (0.079, 0.075), (0.131, 0.04), (0.197, 0.021)] {
            let n = ((delay + ch as f64 * 0.004) * RATE as f64).round() as usize;
            for i in n..score.len() {
                score[i][ch] += dry[i - n][ch] * gain * 0.30;
            }
        }
    }
    stereo_filter(&mut score, 40., 7300.);
    let last = (story.duration - 0.42) * RATE as f64;
    for i in last.round() as usize..count {
        let gain = (PI * 0.5 * (i as f64 - last) / (count as f64 - last))
            .cos()
            .powi(2);
        for x in &mut score[i] {
            *x *= gain;
        }
    }
    score[count - (0.06 * RATE as f64).round() as usize..].fill([0.; 2]);
    add(
        &mut effects,
        &synth.fizz(story.shot("opening")?.end, 1.7),
        0.,
        4.,
        0.08,
    );
    for (i, event) in story.sound_events.iter().enumerate() {
        let frame = event
            .frame
            .unwrap_or_else(|| (event.time.unwrap() * story.fps - 1e-7).ceil() as usize);
        let at = frame as f64 / story.fps;
        let variation = event.variation.unwrap_or(i);
        let (sound, gain) = match event.kind.as_str() {
            "can_contact" => (
                synth.contact(variation, true, event.duration.unwrap_or(0.35)),
                0.048,
            ),
            "case_contact" => (
                synth.contact(variation, false, 0.25 + (variation % 3) as f64 * 0.025),
                0.060,
            ),
            "carton_move" => (synth.movement(event.duration.unwrap_or(0.28), false), 0.022),
            "load_movement" => (synth.movement(event.duration.unwrap_or(0.65), true), 0.015),
            other => anyhow::bail!("unknown picture sound {other}"),
        };
        add(
            &mut effects,
            &sound,
            at,
            event.gain.unwrap_or(gain),
            event.pan.unwrap_or(0.),
        );
        events.push(json!({"id":event.id,"kind":event.kind,"start":at,"end":(at+sound.len() as f64/RATE as f64).min(story.duration),"picture_frame":frame}));
    }
    add(
        &mut effects,
        &synth.pour(story.shot("pour")?.end - water),
        water,
        0.76,
        0.045,
    );
    let mut fizz = synth.fizz(story.duration - sensory, 1.);
    for (i, x) in fizz.iter_mut().enumerate() {
        let t = sensory + i as f64 / RATE as f64;
        let gain = if t < serve - 0.3 {
            6.
        } else if t < serve {
            6. - 2.5 * (t - (serve - 0.3)) / 0.3
        } else if t < story.duration - 0.65 {
            3.5
        } else {
            3.5 * (story.duration - t) / 0.65
        };
        *x *= gain;
    }
    add(&mut effects, &fizz, sensory, 1., 0.07);
    stereo_filter(&mut effects, 65., 11500.);
    for i in 0..count {
        let t = i as f64 / RATE as f64;
        let mut duck = 1_f64;
        for cap in &caps {
            let attack = ((t - (cap.start - 0.13)) / 0.13).clamp(0., 1.);
            let release = ((cap.spoken_end + 0.34 - t) / 0.34).clamp(0., 1.);
            duck = duck.min(1. - (1. - 10_f64.powf(-3. / 20.)) * attack.min(release));
        }
        for ch in 0..2 {
            score[i][ch] *= 2.6 * duck;
        }
    }
    wav(&out.join("score.wav"), &score)?;
    wav(&out.join("effects.wav"), &effects)?;
    let mix: Stereo = (0..count)
        .map(|i| {
            [
                voice[i][0] + score[i][0] + effects[i][0],
                voice[i][1] + score[i][1] + effects[i][1],
            ]
        })
        .collect();
    wav(&out.join("mix-premaster.wav"), &mix)?;
    normalize(
        &out.join("mix-premaster.wav"),
        &out.join("mix-master.wav"),
        -17.,
        -1.5,
        14.,
        16,
    )?;
    run(Command::new("ffmpeg")
        .args(["-v", "error", "-y", "-i"])
        .arg(out.join("mix-master.wav"))
        .args(["-c:a", "libmp3lame", "-b:a", "192k"])
        .arg(out.join("audio-review.mp3")))?;
    let levels = measure(&out.join("mix-master.wav"), -17., -1.5, 14.)?;
    let report = json!({"duration_seconds":story.duration,"sample_rate":RATE,"channels":2,"bits_per_sample":16,"picture_frames":(story.duration*story.fps).round(),"picture_fps":story.fps,"narration_edits":[performance],"captions":caps,"events":events,"levels":levels,"master_sha256":hash(&out.join("mix-master.wav"))?});
    write(
        out.join("audio-report.json"),
        serde_json::to_vec_pretty(&report)?,
    )?;
    write(
        out.join("audio-plan.json"),
        serde_json::to_vec_pretty(&report)?,
    )?;
    println!("{}", out.join("mix-master.wav").display());
    Ok(())
}

fn wav24(path: &Path, samples: &[[f64; 2]]) -> Result<()> {
    let raw = path.with_extension("f32");
    let mut data = Vec::with_capacity(samples.len() * 8);
    for &sample in samples.iter().flatten() {
        data.extend_from_slice(&(sample as f32).to_le_bytes());
    }
    write(&raw, data)?;
    let result = run(Command::new("ffmpeg")
        .args([
            "-v", "error", "-y", "-f", "f32le", "-ar", "48000", "-ac", "2", "-i",
        ])
        .arg(&raw)
        .args(["-c:a", "pcm_s24le"])
        .arg(path));
    let _ = fs::remove_file(raw);
    result
}
fn fade_noise(
    synth: &mut Synth,
    seconds: f64,
    lo: f64,
    hi: f64,
    attack: f64,
    release: f64,
) -> Vec<f64> {
    let mut values = synth.noise(seconds, lo, hi, true);
    taper(&mut values, attack, release, RATE);
    values
}
fn bubble(radius: f64) -> Vec<f64> {
    let seconds = 0.035 + 0.025 * radius;
    let f = 1400. / radius;
    let mut values = (0..(seconds * RATE as f64).round() as usize)
        .map(|i| {
            let t = i as f64 / RATE as f64;
            (TAU * (f * t - f * 0.36 * t * t / seconds)).sin()
                * (1. - (-t / 0.0008).exp())
                * (-t / (seconds * 0.18)).exp()
        })
        .collect::<Vec<_>>();
    taper(&mut values, 0.001, 0.012, RATE);
    values
}
fn bell(frequency: f64, seconds: f64) -> Vec<f64> {
    let mut values = (0..(seconds * RATE as f64).round() as usize)
        .map(|i| {
            let t = i as f64 / RATE as f64;
            (TAU * frequency * t).sin() * (-t * 1.8).exp()
                + 0.17 * (TAU * frequency * 2.005 * t).sin() * (-t * 3.7).exp()
                + 0.045 * (TAU * frequency * 3.997 * t).sin() * (-t * 7.).exp()
        })
        .collect::<Vec<_>>();
    taper(&mut values, 0.006, 0.45, RATE);
    values
}
pub fn explainer(mut args: Args) -> Result<()> {
    let out = args
        .take(&["--out"])
        .map(PathBuf::from)
        .unwrap_or_else(|| super::explainer::here().join("audio"));
    fs::create_dir_all(&out)?;
    let timing = json(out.join("timing.json"))?;
    let duration = timing["frames"].as_f64().context("picture frames")?
        / timing["fps"].as_f64().context("picture fps")?;
    let count = (duration * RATE as f64).round() as usize;
    let mut score = vec![[0.; 2]; count];
    let mut effects = score.clone();
    let mut voice = read_mono(&out.join("voice-master.wav"), RATE)?;
    voice.resize(count, 0.);
    let mut synth = Synth::new(20261027);
    let harmony = [
        (0., 22., [146.832, 220., 329.628, 369.994]),
        (19., 43.5, [123.471, 184.997, 246.942, 293.665]),
        (40., 71.8, [130.813, 195.998, 293.665, 369.994]),
        (68.5, 85.4, [164.814, 246.942, 329.628, 391.995]),
        (81.5, duration, [146.832, 220., 293.665, 369.994]),
    ];
    for (start, end, frequencies) in harmony {
        let size = ((end - start) * RATE as f64).round() as usize;
        let mut env = vec![1.; size];
        taper(&mut env, 2.3, 3_f64.min((end - start) / 3.), RATE);
        for (j, f) in frequencies.into_iter().enumerate() {
            let phase = j as f64 * 0.91;
            for (ch, detune) in [(0, 0.9997), (1, 1.0003)] {
                let lo = (start * RATE as f64).round() as usize;
                for i in 0..size.min(count - lo) {
                    let t = i as f64 / RATE as f64;
                    let slow = 0.88 + 0.12 * (TAU * (0.047 + j as f64 * 0.007) * t + phase).sin();
                    let tone = (TAU * f * detune * t + phase).sin()
                        + 0.065 * (TAU * f * 2.002 * detune * t + phase).sin();
                    score[lo + i][ch] += tone * env[i] * slow * 0.0028;
                }
            }
        }
    }
    let notes = [
        (0.15, 587.33, -0.22),
        (0.82, 880., 0.18),
        (7.9, 659.26, -0.1),
        (10., 587.33, 0.2),
        (19.7, 493.88, -0.15),
        (31., 739.99, 0.1),
        (41.1, 587.33, -0.1),
        (55.05, 659.26, 0.15),
        (69.25, 783.99, -0.2),
        (82.8, 739.99, 0.16),
        (96.4, 587.33, -0.12),
        (100.1, 440., 0.12),
        (100.35, 587.33, -0.1),
    ];
    for (at, f, pan) in notes {
        let tone = bell(f, 2.8);
        add(&mut score, &tone, at, 0.012, pan);
        add(&mut score, &tone, at + 0.143, 0.0015, -pan);
    }
    let gain = 0.012 / rms(score.iter().flatten().copied()).max(1e-8);
    for x in score.iter_mut().flatten() {
        *x *= gain;
    }
    add(
        &mut effects,
        &fade_noise(&mut synth, 3.1, 280., 5200., 0.75, 1.2),
        10.,
        0.007,
        -0.3,
    );
    for (at, pan) in [(10.35, -0.35), (11.10, 0.25), (12.05, 0.1)] {
        let mut tick = (0..(0.12 * RATE as f64).round() as usize)
            .map(|i| {
                let t = i as f64 / RATE as f64;
                ((TAU * 340. * t).sin() + 0.3 * (TAU * 690. * t).sin()) * (-t * 62.).exp()
            })
            .collect::<Vec<_>>();
        taper(&mut tick, 0.002, 0.03, RATE);
        add(&mut effects, &tick, at, 0.012, pan);
    }
    let (gas_start, gas_end) = (20.7, 30.4);
    add(
        &mut effects,
        &fade_noise(&mut synth, gas_end - gas_start, 350., 2300., 0.65, 1.),
        gas_start,
        0.0025,
        -0.24,
    );
    let mut at = gas_start + 0.10;
    while at < gas_end - 0.4 {
        let t = at + synth.rng.uniform(-0.03, 0.03);
        let r = synth.rng.uniform(0.85, 1.8);
        let gain = synth.rng.uniform(0.005, 0.013);
        let pan = synth.rng.uniform(-0.4, 0.08);
        add(&mut effects, &bubble(r), t, gain, pan);
        at += 0.105;
    }
    let (jet_start, jet_end) = (32.6, 68.5);
    let mut jet = fade_noise(&mut synth, jet_end - jet_start, 800., 8500., 1.15, 0.75);
    for (i, x) in jet.iter_mut().enumerate() {
        let t = i as f64 / RATE as f64;
        *x *= 0.82 + 0.10 * (TAU * 3.1 * t).sin() + 0.08 * (TAU * 9.3 * t).sin();
    }
    add(&mut effects, &jet, jet_start, 0.0058, -0.08);
    let (mix_start, mix_end) = (42.5, 61.4);
    add(
        &mut effects,
        &fade_noise(&mut synth, mix_end - mix_start, 260., 3100., 1., 1.6),
        mix_start,
        0.0035,
        0.08,
    );
    let mut at = mix_start;
    while at < mix_end {
        let r = synth.rng.uniform(0.55, 1.1);
        let t = at + synth.rng.uniform(-0.015, 0.015);
        let gain = synth.rng.uniform(0.0018, 0.006);
        let pan = synth.rng.uniform(-0.32, 0.32);
        add(&mut effects, &bubble(r), t, gain, pan);
        at += 0.065;
    }
    add(
        &mut effects,
        &fade_noise(&mut synth, 12., 230., 1900., 1.5, 2.),
        70.5,
        0.0038,
        0.18,
    );
    let (pour_start, pour_end) = (87.5, 95.3);
    let mut pour = fade_noise(&mut synth, pour_end - pour_start, 280., 7800., 0.30, 0.22);
    for (i, x) in pour.iter_mut().enumerate() {
        let t = i as f64 / RATE as f64;
        *x *= 0.8 + 0.12 * (TAU * 5.3 * t).sin() + 0.08 * (TAU * 13.1 * t).sin();
    }
    add(&mut effects, &pour, pour_start, 0.0088, 0.05);
    let mut at = pour_start + 0.15;
    while at < pour_end {
        let r = synth.rng.uniform(0.5, 0.9);
        let pan = synth.rng.uniform(-0.2, 0.25);
        add(&mut effects, &bubble(r), at, 0.003, pan);
        at += 0.09;
    }
    for (start, end, gain) in [(0.45, 7.8, 0.0011), (95.3, 101.65, 0.0019)] {
        add(
            &mut effects,
            &fade_noise(&mut synth, end - start, 3200., 11500., 0.6, 1.2),
            start,
            gain,
            0.04,
        );
    }
    let blocks: Vec<_> = voice
        .chunks(480)
        .map(|chunk| (rms(chunk.iter().copied()) / 0.025).min(1.))
        .collect();
    let mut smooth = vec![0.; blocks.len()];
    for i in 0..blocks.len() {
        let mut weight = 0.;
        for j in i.saturating_sub(40)..(i + 41).min(blocks.len()) {
            let w = (-0.5 * ((j as f64 - i as f64) / 10.).powi(2)).exp();
            smooth[i] += blocks[j] * w;
            weight += w;
        }
        smooth[i] /= weight;
    }
    for i in 0..count {
        let t = i as f64 / RATE as f64;
        let block = i / 480;
        let f = (i % 480) as f64 / 480.;
        let speech = smooth[block] * (1. - f) + smooth[(block + 1).min(smooth.len() - 1)] * f;
        let final_fade = (PI * 0.5 * (t / 0.05).min(1.)).sin().powi(2)
            * if t > duration - 1. {
                (PI * 0.5 * (duration - t)).sin().powi(2)
            } else {
                1.
            };
        for ch in 0..2 {
            score[i][ch] *= (1. - 0.40 * speech) * final_fade;
            effects[i][ch] *= (1. - 0.22 * speech) * final_fade;
        }
    }
    wav24(&out.join("score-stem.wav"), &score)?;
    wav24(&out.join("effects-stem.wav"), &effects)?;
    let premix: Stereo = (0..count)
        .map(|i| {
            [
                voice[i] + score[i][0] + effects[i][0],
                voice[i] + score[i][1] + effects[i][1],
            ]
        })
        .collect();
    let source = out.join("mix-premaster.wav");
    wav24(&source, &premix)?;
    let levels = normalize(&source, &out.join("mix-master.wav"), -16., -1., 8., 24)?;
    let final_levels = measure(&out.join("mix-master.wav"), -16., -1., 8.)?;
    let provenance = json(super::explainer::here().join("audio/provenance.json"))?;
    let report = json!({"duration":duration,"sample_rate":RATE,"channels":2,"bit_depth":24,"voice_service":provenance["service"],"voice_model":provenance["model"],"voice":provenance["voice"],"score":"Original procedural ambient composition","effects":"Original procedural scene-following textures","stock_assets":[],"random_seed":20261027,"master_integrated_lufs":final_levels["input_i"].as_str().unwrap().parse::<f64>()?,"master_true_peak_dbtp":final_levels["input_tp"].as_str().unwrap().parse::<f64>()?,"master_loudness_range_lu":final_levels["input_lra"].as_str().unwrap().parse::<f64>()?,"premix_loudness":levels,"voice_word_speed_changed":false,"master_sha256":hash(&out.join("mix-master.wav"))?,"sound_clock":{"enclosure":[10.,13.1],"gas_admission":[gas_start,gas_end],"jet":[jet_start,jet_end],"entrainment":[mix_start,mix_end],"evaporator_flow":[70.5,82.5],"pour":[pour_start,pour_end],"closing_fizz":[95.3,101.65]},"stems":{"voice":"voice-master.wav","score":"score-stem.wav","effects":"effects-stem.wav"}});
    write(
        out.join("audio-report.json"),
        serde_json::to_vec_pretty(&report)?,
    )?;
    let _ = fs::remove_file(source);
    println!("{}", out.join("mix-master.wav").display());
    Ok(())
}
