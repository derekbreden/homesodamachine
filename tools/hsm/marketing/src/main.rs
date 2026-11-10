//! On-demand marketing commands prepare display artwork, brand exports and edited media.
mod art;
mod brand;
mod draw;
mod film;
mod flavors;
mod kitchen;
mod scene;
mod video;

use anyhow::{Context, Result, bail};
use std::{
    fs,
    path::{Path, PathBuf},
    process::{Command, Output},
};

pub struct Args(pub Vec<String>);
impl Args {
    pub fn take(&mut self, flags: &[&str]) -> Option<String> {
        let i = self.0.iter().position(|a| flags.contains(&a.as_str()))?;
        self.0.remove(i);
        if i < self.0.len() {
            Some(self.0.remove(i))
        } else {
            None
        }
    }
    pub fn flag(&mut self, flag: &str) -> bool {
        self.0.iter().position(|a| a == flag).is_some_and(|i| {
            self.0.remove(i);
            true
        })
    }
    pub fn number(&mut self, flags: &[&str], default: f64) -> Result<f64> {
        self.take(flags).map_or(Ok(default), |s| {
            s.parse().with_context(|| format!("{}: a number", flags[0]))
        })
    }
    pub fn positional(&self, n: usize) -> Result<&str> {
        self.0
            .get(n)
            .map(String::as_str)
            .with_context(|| format!("missing argument {}", n + 1))
    }
}

pub fn root() -> PathBuf {
    std::env::var_os("HSM_ROOT")
        .map(PathBuf::from)
        .unwrap_or_else(|| {
            Path::new(env!("CARGO_MANIFEST_DIR"))
                .ancestors()
                .nth(3)
                .unwrap()
                .to_path_buf()
        })
}
pub fn write(path: impl AsRef<Path>, data: impl AsRef<[u8]>) -> Result<()> {
    let path = path.as_ref();
    if let Some(parent) = path.parent().filter(|p| !p.as_os_str().is_empty()) {
        fs::create_dir_all(parent)?;
    }
    fs::write(path, data).with_context(|| format!("write {}", path.display()))
}
pub fn json(path: impl AsRef<Path>) -> Result<serde_json::Value> {
    let path = path.as_ref();
    serde_json::from_slice(&fs::read(path).with_context(|| format!("read {}", path.display()))?)
        .with_context(|| format!("JSON in {}", path.display()))
}
pub fn run(command: &mut Command) -> Result<()> {
    let status = command
        .status()
        .with_context(|| format!("start {command:?}"))?;
    anyhow::ensure!(status.success(), "command failed ({status}): {command:?}");
    Ok(())
}
pub fn output(command: &mut Command) -> Result<Output> {
    let out = command
        .output()
        .with_context(|| format!("start {command:?}"))?;
    anyhow::ensure!(
        out.status.success(),
        "command failed: {command:?}\n{}",
        String::from_utf8_lossy(&out.stderr)
    );
    Ok(out)
}

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let command = args.next().unwrap_or_else(|| "help".into());
    let args = Args(args.collect());
    if args.0.iter().any(|arg| arg == "--help" || arg == "-h") {
        let usage = match command.as_str() {
            "make-art" => "enclosure [-o PATH] [-q]",
            "make-logos" => "-o PATH [--store] [--partitions CSV] [-q]",
            "brand-assets" | "flavor-placeholders" => "[--preview] [--out-root DIR]",
            "animation-frames" => "[--from-svg] [--out-root DIR]",
            "sync" => "VIDEO AUDIO [-o VIDEO] [--search-seconds SECONDS]",
            "segment" => {
                "TRANSCRIPT [-o JSON] [--gap SECONDS] [--pad-before SECONDS] [--pad-after SECONDS] [--no-filter]"
            }
            "make-subtitles" => "CUTS OUTPUT.ass [--fade SECONDS] [--title-duration SECONDS]",
            "cut" => {
                "SOURCE CUTS OUTPUT [--overlays JSON|--no-overlays] [--captions ASS] [--fade SECONDS] [--title TEXT] [--title-duration SECONDS] [--preset NAME] [--crf NUMBER] [--keep-parts]"
            }
            "overlays" => {
                "SOURCE SIDECAR OUTPUT [--captions ASS] [--preset NAME] [--crf NUMBER] [--dry-run]"
            }
            "kitchen-scene" => {
                "[--preview] [--out DIR] [--width PIXELS] [--samples COUNT] [--scene-only] [--describe-only] [--shots kitchen faucet cabinet]"
            }
            "studio-stage" => {
                "[--stills] [--time SECONDS] [--fps RATE] [--width PIXELS] [--samples COUNT] [--timing JSON] [--out DIR] [--frames-root DIR] [--start-frame FRAME] [--end-frame FRAME] [--describe-only] [--shots SHOT ...]"
            }
            "studio-render" => {
                "[--timing JSON] [--profile NAME] [--chunk-frames COUNT] [--out DIR] [--fps RATE] [--pour-fps RATE] [--width PIXELS] [--samples COUNT] [--fresh] [--picture-only] [--finish-only] [--draft] [--shots SHOT ...]"
            }
            "studio-finish" => {
                "[--frames DIR] [--audio WAV] [--out DIR] [--timing JSON] [--fps RATE] [--source-fps SHOT=RATE] [--animatic] [--draft] [--force]"
            }
            "studio-audio" | "studio-clock" => "[--timing JSON] [--out PATH]",
            "explainer-edit" | "explainer-audio" => "[--out DIR]",
            "explainer-assets" => {
                "[--out DIR] [--bundle all|enclosure|cold-core|faucet|coil|carbonator]"
            }
            "film-narration" => {
                "[--film studio|explainer] [--config JSON] [--key-file PATH] [--output-dir DIR] [--output WAV] [--voice NAME] [--align-only] [--no-align] [--whisper-model NAME]"
            }
            _ => "[arguments]",
        };
        println!("hsm-marketing {command} {usage}");
        return Ok(());
    }
    if matches!(
        command.as_str(),
        "brand-assets"
            | "animation-frames"
            | "flavor-placeholders"
            | "sync"
            | "cut"
            | "overlays"
            | "kitchen-scene"
            | "studio-stage"
            | "studio-render"
            | "studio-audio"
            | "studio-finish"
            | "explainer-edit"
            | "explainer-audio"
            | "explainer-assets"
            | "film-narration"
    ) {
        hsm_run_slots::process_enter(&format!("marketing/{command}"))?;
    }
    match command.as_str() {
        "make-art" => art::make_art(args),
        "make-logos" => art::make_logos(args),
        "brand-assets" => brand::build(args),
        "animation-frames" => brand::animation(args),
        "flavor-placeholders" => flavors::build(args),
        "kitchen-scene" => kitchen::main(args),
        "studio-stage" | "studio-render" | "studio-audio" | "studio-finish" | "studio-clock"
        | "explainer-edit" | "explainer-audio" | "explainer-assets" | "film-narration" => {
            film::main(&command, args)
        }
        "sync" | "segment" | "make-subtitles" | "cut" | "overlays" => video::main(&command, args),
        "help" | "--help" | "-h" => {
            println!(
                "hsm-marketing <make-art|make-logos|brand-assets|animation-frames|flavor-placeholders|sync|segment|make-subtitles|cut|overlays|kitchen-scene|studio-stage|studio-render|studio-audio|studio-finish|studio-clock|explainer-edit|explainer-audio|explainer-assets|film-narration> [arguments]"
            );
            Ok(())
        }
        _ => bail!("unknown marketing command: {command}"),
    }
}
