//! The footage workflow aligns recorded sound, clusters speech and times captions against edited cuts.
mod edit;
use crate::{Args, json, output, run, write};
use anyhow::{Context, Result, ensure};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::{
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
    process::Command,
};

pub fn main(command: &str, args: Args) -> Result<()> {
    match command {
        "sync" => sync(args),
        "segment" => segment(args),
        "make-subtitles" => subtitles(args),
        "cut" => edit::cut(args),
        "overlays" => edit::overlays(args),
        _ => unreachable!(),
    }
}
#[derive(Clone, Deserialize, Serialize)]
pub struct Word {
    pub start: f64,
    pub end: f64,
    pub word: String,
    #[serde(flatten)]
    pub extra: BTreeMap<String, Value>,
}
#[derive(Clone, Deserialize, Serialize)]
pub struct Segment {
    pub start: f64,
    pub end: f64,
    #[serde(default)]
    pub text: String,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub words: Vec<Word>,
    #[serde(flatten)]
    pub extra: BTreeMap<String, Value>,
}
#[derive(Deserialize)]
struct Transcript {
    #[serde(default)]
    segments: Vec<Segment>,
}
pub fn filler(text: &str, duration: f64) -> bool {
    let text = text.trim().to_lowercase();
    if text.is_empty() {
        return true;
    }
    if duration > 3. {
        return false;
    }
    text.split_whitespace().all(|w| {
        ["so", "um", "uh", "uhh", "hmm", "mm", "mhm", "ah"]
            .contains(&w.trim_matches([',', '.', '?', '!']))
    })
}
#[derive(Serialize)]
struct Scene {
    scene_start: f64,
    scene_end: f64,
    speech_start: f64,
    speech_end: f64,
    segments: Vec<Segment>,
    duration: f64,
    text: String,
}
fn segment(mut args: Args) -> Result<()> {
    let out = args.take(&["-o", "--output"]);
    let gap = args.number(&["--gap"], 10.)?;
    let before = args.number(&["--pad-before"], 30.)?;
    let after = args.number(&["--pad-after"], 30.)?;
    let no_filter = args.flag("--no-filter");
    let source = args.positional(0)?;
    let transcript: Transcript = serde_json::from_value(json(source)?)?;
    let end = transcript.segments.iter().map(|s| s.end).fold(0., f64::max);
    let mut clusters: Vec<Vec<Segment>> = Vec::new();
    for seg in transcript.segments {
        if !no_filter && (seg.end - seg.start < 0.05 || filler(&seg.text, seg.end - seg.start)) {
            continue;
        }
        if let Some(cluster) = clusters
            .last_mut()
            .filter(|c| seg.start - c.last().unwrap().end <= gap)
        {
            cluster.push(seg);
        } else {
            clusters.push(vec![seg]);
        }
    }
    let mut scenes: Vec<Scene> = Vec::new();
    for cluster in clusters {
        let first = cluster[0].start;
        let last = cluster.last().unwrap().end;
        let start = (first - before).max(0.);
        let finish = (last + after).min(end);
        if let Some(scene) = scenes.last_mut().filter(|s| start <= s.scene_end) {
            scene.scene_end = scene.scene_end.max(finish);
            scene.speech_end = scene.speech_end.max(last);
            scene.segments.extend(cluster);
        } else {
            scenes.push(Scene {
                scene_start: start,
                scene_end: finish,
                speech_start: first,
                speech_end: last,
                segments: cluster,
                duration: 0.,
                text: String::new(),
            });
        }
    }
    for scene in &mut scenes {
        scene.duration = scene.scene_end - scene.scene_start;
        scene.text = scene
            .segments
            .iter()
            .map(|s| s.text.trim())
            .collect::<Vec<_>>()
            .join(" ");
    }
    let out = out.unwrap_or_else(|| format!("{source}.scenes.json"));
    write(
        &out,
        serde_json::to_vec_pretty(
            &json!({"input":source,"scenes":scenes,"params":{"gap_s":gap,"pad_before_s":before,"pad_after_s":after}}),
        )?,
    )?;
    println!("{out}");
    Ok(())
}

#[derive(Deserialize, Clone)]
pub struct Cut {
    #[serde(default)]
    pub source: Option<String>,
    #[serde(default, rename = "type")]
    pub kind: Option<String>,
    #[serde(default)]
    pub start: Option<f64>,
    #[serde(default)]
    pub end: Option<f64>,
    #[serde(default)]
    pub at: Option<f64>,
    #[serde(default)]
    pub duration: Option<f64>,
    #[serde(default)]
    pub section: Option<String>,
    #[serde(default)]
    pub tool: Option<String>,
    #[serde(default)]
    pub transcript: Option<String>,
    #[serde(default)]
    pub sync_offset: Option<f64>,
}
impl Cut {
    pub fn frozen(&self) -> bool {
        self.kind.as_deref() == Some("freeze")
    }
    pub fn duration(&self) -> Result<f64> {
        let n = if self.frozen() {
            self.duration.context("freeze duration")?
        } else {
            self.end.context("cut end")? - self.start.context("cut start")?
        };
        ensure!(n > 0., "cut has nonpositive duration");
        Ok(n)
    }
}
pub fn cuts(path: &Path) -> Result<(Vec<Cut>, Value)> {
    let raw = json(path)?;
    let cuts = serde_json::from_value(if raw.is_array() {
        raw.clone()
    } else {
        raw["cuts"].clone()
    })?;
    Ok((cuts, raw.get("sources").cloned().unwrap_or(json!({}))))
}
const ASS_HEADER: &str = "[Script Info]\nScriptType: v4.00+\nWrapStyle: 2\nScaledBorderAndShadow: yes\nPlayResX: 1920\nPlayResY: 1080\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Helvetica,54,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,4,1,2,80,80,90,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n";
fn ass_time(t: f64) -> String {
    let n = (t * 100.).round().max(0.) as u64;
    format!(
        "{}:{:02}:{:02}.{:02}",
        n / 360000,
        n / 6000 % 60,
        n / 100 % 60,
        n % 100
    )
}
fn subtitles(mut args: Args) -> Result<()> {
    let fade = args.number(&["--fade"], 0.)?;
    let title = args.number(&["--title-duration"], 0.)?;
    let (cuts, sources) = cuts(Path::new(args.positional(0)?))?;
    let mut clock = title;
    let mut cues: Vec<(f64, f64, String)> = Vec::new();
    for (i, cut) in cuts.iter().enumerate() {
        if i > 0 || title > 0. {
            clock -= fade;
        }
        let duration = cut.duration()?;
        if cut.frozen() {
            clock += duration;
            continue;
        }
        let source = cut.source.as_deref().context("caption cut source")?;
        let meta = &sources[source];
        let transcript = cut
            .transcript
            .clone()
            .or_else(|| meta["transcript"].as_str().map(str::to_owned))
            .unwrap_or_else(|| {
                format!(
                    "transcripts/{}.json",
                    Path::new(source).file_stem().unwrap().to_string_lossy()
                )
            });
        let offset = cut
            .sync_offset
            .or_else(|| meta["sync_offset"].as_f64())
            .unwrap_or_else(|| {
                json(format!("{source}.sync.json"))
                    .ok()
                    .and_then(|s| s["offset_seconds"].as_f64())
                    .unwrap_or(0.)
            });
        if !Path::new(&transcript).exists() {
            eprintln!("transcript absent: {transcript}");
            clock += duration;
            continue;
        }
        let start = cut.start.unwrap();
        let end = cut.end.unwrap();
        let transcript: Transcript = serde_json::from_value(json(&transcript)?)?;
        for segment in transcript.segments {
            if segment.end - offset <= start || segment.start - offset >= end {
                continue;
            }
            if segment.words.is_empty() {
                let a = (segment.start - offset).max(start);
                let b = (segment.end - offset).min(end);
                if !filler(&segment.text, b - a) {
                    cues.push((
                        clock + a - start,
                        clock + b - start,
                        segment.text.trim().into(),
                    ));
                }
                continue;
            }
            let words: Vec<_> = segment
                .words
                .into_iter()
                .filter(|w| w.start - offset >= start && w.end - offset <= end)
                .collect();
            let mut chunk: Vec<Word> = Vec::new();
            let mut emit = |chunk: &mut Vec<Word>| {
                if chunk.is_empty() {
                    return;
                }
                let a = chunk[0].start - offset;
                let b = chunk.last().unwrap().end - offset;
                let text = chunk.iter().map(|w| w.word.as_str()).collect::<String>();
                if !filler(&text, b - a) {
                    cues.push((clock + a - start, clock + b - start, text.trim().into()));
                }
                chunk.clear();
            };
            for word in words {
                if !chunk.is_empty()
                    && (word.end - chunk[0].start > 3.5
                        || chunk.len() >= 7
                        || chunk
                            .last()
                            .unwrap()
                            .word
                            .trim_end()
                            .ends_with(['.', '!', '?']))
                {
                    emit(&mut chunk);
                }
                chunk.push(word);
            }
            emit(&mut chunk);
        }
        clock += duration;
    }
    cues.sort_by(|a, b| a.0.total_cmp(&b.0));
    let mut text = ASS_HEADER.to_owned();
    text.push('\n');
    for (i, (start, end, caption)) in cues.iter().enumerate() {
        let end = cues.get(i + 1).map_or(*end, |next| end.min(next.0));
        if end - start < 0.15 {
            continue;
        }
        let caption = caption
            .replace('\\', "\\\\")
            .replace('{', "\\{")
            .replace('}', "\\}")
            .replace('\n', "\\N");
        text.push_str(&format!(
            "Dialogue: 0,{},{},Default,,0,0,0,,{caption}\n",
            ass_time(*start),
            ass_time(end)
        ));
    }
    write(args.positional(1)?, text)
}

#[derive(Clone, Copy, Default)]
struct Complex {
    real: f64,
    imag: f64,
}
impl Complex {
    fn add(self, b: Self) -> Self {
        Self {
            real: self.real + b.real,
            imag: self.imag + b.imag,
        }
    }
    fn sub(self, b: Self) -> Self {
        Self {
            real: self.real - b.real,
            imag: self.imag - b.imag,
        }
    }
    fn mul(self, b: Self) -> Self {
        Self {
            real: self.real * b.real - self.imag * b.imag,
            imag: self.real * b.imag + self.imag * b.real,
        }
    }
}
fn fft(data: &mut [Complex], inverse: bool) {
    let n = data.len();
    let mut j = 0;
    for i in 1..n {
        let mut bit = n >> 1;
        while j & bit != 0 {
            j ^= bit;
            bit >>= 1;
        }
        j ^= bit;
        if i < j {
            data.swap(i, j);
        }
    }
    let mut len = 2;
    while len <= n {
        let angle = std::f64::consts::TAU / len as f64 * if inverse { -1. } else { 1. };
        let step = Complex {
            real: angle.cos(),
            imag: angle.sin(),
        };
        for base in (0..n).step_by(len) {
            let mut factor = Complex { real: 1., imag: 0. };
            for i in 0..len / 2 {
                let a = data[base + i];
                let b = data[base + i + len / 2].mul(factor);
                data[base + i] = a.add(b);
                data[base + i + len / 2] = a.sub(b);
                factor = factor.mul(step);
            }
        }
        len *= 2;
    }
    if inverse {
        for value in data {
            value.real /= n as f64;
            value.imag /= n as f64;
        }
    }
}
fn decode(path: &str, seconds: f64) -> Result<Vec<f64>> {
    let out = output(Command::new("ffmpeg").args([
        "-i",
        path,
        "-t",
        &format!("{seconds:.3}"),
        "-f",
        "s16le",
        "-ac",
        "1",
        "-ar",
        "8000",
        "-loglevel",
        "error",
        "pipe:1",
    ]))?;
    Ok(out
        .stdout
        .chunks_exact(2)
        .map(|b| i16::from_le_bytes([b[0], b[1]]) as f64 / 32768.)
        .collect())
}
fn correlate(a: &[f64], b: &[f64]) -> Result<(f64, f64)> {
    ensure!(
        !a.is_empty() && !b.is_empty(),
        "recording has no decoded audio"
    );
    let len = a.len() + b.len() - 1;
    let n = len.next_power_of_two();
    let mut fa = vec![Complex::default(); n];
    let mut fb = fa.clone();
    let ma = a.iter().sum::<f64>() / a.len() as f64;
    let mb = b.iter().sum::<f64>() / b.len() as f64;
    for (value, x) in fa.iter_mut().zip(a) {
        value.real = x - ma;
    }
    for (value, x) in fb.iter_mut().zip(b.iter().rev()) {
        value.real = x - mb;
    }
    fft(&mut fa, false);
    fft(&mut fb, false);
    for (x, y) in fa.iter_mut().zip(fb) {
        *x = x.mul(y);
    }
    fft(&mut fa, true);
    let peak = (0..len)
        .max_by(|&i, &j| fa[i].real.abs().total_cmp(&fa[j].real.abs()))
        .unwrap();
    let second = (0..len)
        .filter(|i| i.abs_diff(peak) > 4000)
        .map(|i| fa[i].real.abs())
        .fold(0., f64::max);
    let lag = peak as i64 - (b.len() as i64 - 1);
    Ok((
        -lag as f64 / 8000.,
        fa[peak].real.abs() / if second > 0. { second } else { 1. },
    ))
}
fn sync(mut args: Args) -> Result<()> {
    let out = args.take(&["-o", "--output"]);
    let seconds = args.number(&["--search-seconds"], 120.)?;
    let video = args.positional(0)?;
    let audio = args.positional(1)?;
    let (offset, confidence) = correlate(&decode(video, seconds)?, &decode(audio, seconds)?)?;
    let sidecar = serde_json::to_vec_pretty(
        &json!({"video":video,"audio":audio,"offset_seconds":offset,"confidence":confidence,"search_seconds":seconds,"sample_rate_hz":8000}),
    )?;
    write(format!("{video}.sync.json"), &sidecar)?;
    println!("{offset:.6}");
    eprintln!("confidence {confidence:.2}");
    if let Some(out) = out {
        let mut cmd = Command::new("ffmpeg");
        cmd.args(["-y", "-i", video]);
        cmd.args([
            if offset >= 0. { "-ss" } else { "-itsoffset" },
            &format!("{:.3}", offset.abs()),
            "-i",
            audio,
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            &out,
        ]);
        run(&mut cmd)?;
        write(format!("{out}.sync.json"), sidecar)?;
    }
    Ok(())
}

pub struct Scratch(pub PathBuf, pub bool);
impl Scratch {
    pub fn new(output: &str, keep: bool) -> Result<Self> {
        let path = if keep {
            PathBuf::from(format!("{output}.parts"))
        } else {
            crate::root().join(format!(
                ".cache/runs/marketing-{}-{}",
                std::process::id(),
                std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)?
                    .as_nanos()
            ))
        };
        fs::create_dir_all(&path)?;
        Ok(Self(path, keep))
    }
}
impl Drop for Scratch {
    fn drop(&mut self) {
        if !self.1 {
            let _ = fs::remove_dir_all(&self.0);
        }
    }
}
