//! Archive compact elapsed-time chamber footage without changing the printer's native recordings.
use crate::{config, digest, ftp::Ftp, gc, mqtt, Args};
use anyhow::{bail, Context, Result};
use serde_json::{json, Value};
use std::{
    fs::{self, File},
    io::Write,
    path::{Path, PathBuf},
    process::Command,
    time::{Duration, SystemTime, UNIX_EPOCH},
};

const SAMPLE_FPS: u32 = 1;
const PLAYBACK_FPS: u32 = 30;
const MAX_WIDTH: u32 = 1280;
const MIN_AGE_SECONDS: i64 = 60;

struct Scratch(PathBuf);
impl Drop for Scratch {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn write_json(path: &Path, value: &Value) -> Result<()> {
    let temporary = path.with_extension("json.part");
    let mut file = File::create(&temporary)?;
    file.write_all(&serde_json::to_vec_pretty(value)?)?;
    file.write_all(b"\n")?;
    file.sync_all()?;
    fs::rename(temporary, path)?;
    gc::sync_directory(path.parent().context("Receipt has no parent")?)?;
    Ok(())
}

fn probe(path: &Path, count: bool) -> Result<Value> {
    let mut command = Command::new("ffprobe");
    command.args(["-v", "error", "-select_streams", "v:0"]);
    if count {
        command.arg("-count_frames");
    }
    let output = command
        .args([
            "-show_entries",
            "stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames:format=duration",
            "-of",
            "json",
        ])
        .arg(path)
        .output()
        .context("Start ffprobe")?;
    if !output.status.success() {
        bail!(
            "Cannot inspect recording {}: {}",
            path.display(),
            String::from_utf8_lossy(&output.stderr)
        )
    }
    Ok(serde_json::from_slice(&output.stdout)?)
}

fn duration(probe: &Value) -> Result<f64> {
    let seconds = probe["format"]["duration"]
        .as_str()
        .context("Recording has no duration")?
        .parse::<f64>()?;
    if !seconds.is_finite() || seconds <= 0. {
        bail!("Recording duration must be finite and positive")
    }
    Ok(seconds)
}

fn playback_name(clip: &gc::Clip) -> Result<String> {
    let stem = Path::new(&clip.name)
        .file_stem()
        .and_then(|s| s.to_str())
        .context("Recording has no filename")?;
    Ok(format!("{stem}-{}x.mp4", PLAYBACK_FPS / SAMPLE_FPS))
}

fn resident_or_cloud_placeholder(path: &Path) -> bool {
    path.exists()
        || path.file_name().is_some_and(|name| {
            path.with_file_name(format!(".{}.icloud", name.to_string_lossy()))
                .exists()
        })
}

fn saved(clip: &gc::Clip, destination: &Path, receipt: &Path) -> Result<bool> {
    if !receipt.exists() || !resident_or_cloud_placeholder(destination) {
        return Ok(false);
    }
    let previous: Value = serde_json::from_slice(&fs::read(receipt)?)?;
    Ok(previous["source"]["bytes"] == clip.size
        && previous["source"]["modified_unix"].as_i64() == clip.mtime
        && previous["sample_fps"] == SAMPLE_FPS
        && previous["playback_fps"] == PLAYBACK_FPS)
}

fn encode(root: &Path, source: &Path, output: &Path) -> Result<(Value, u64)> {
    let source_probe = probe(source, false)?;
    let source_seconds = duration(&source_probe)?;
    let filter = format!(
        "fps={SAMPLE_FPS}:start_time=0:round=near:eof_action=pass,scale='min({MAX_WIDTH},iw)':-2,drawtext=fontfile=/System/Library/Fonts/Helvetica.ttc:text='Recording +%{{pts\\:hms}}':fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=6:x=12:y=h-th-12,settb=AVTB,setpts=N/({PLAYBACK_FPS}*TB)"
    );
    let result = Command::new(root.join("tools/run"))
        .args([
            "--",
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-n",
            "-threads",
            "2",
            "-i",
        ])
        .arg(source)
        .args([
            "-an",
            "-vf",
            &filter,
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-threads",
            "2",
            "-pix_fmt",
            "yuv420p",
            "-r",
            &PLAYBACK_FPS.to_string(),
            "-fps_mode",
            "cfr",
            "-movflags",
            "+faststart",
        ])
        .arg(output)
        .output()
        .context("Start sampled camera playback encoder")?;
    if !result.status.success() {
        bail!(
            "Camera playback encoding failed: {}",
            String::from_utf8_lossy(&result.stderr)
        )
    }
    File::open(output)?.sync_all()?;
    let output_probe = probe(output, true)?;
    let frames = output_probe["streams"][0]["nb_read_frames"]
        .as_str()
        .context("Playback has no decoded frame count")?
        .parse::<u64>()?;
    if frames == 0
        || (frames as f64 - source_seconds * f64::from(SAMPLE_FPS)).abs() > 2.
        || (duration(&output_probe)? - frames as f64 / f64::from(PLAYBACK_FPS)).abs() > 0.05
    {
        bail!("Sampled playback does not cover the source recording")
    }
    Ok((
        json!({"duration_seconds":source_seconds,"video":source_probe["streams"][0]}),
        frames,
    ))
}

fn archive_printer(
    root: &Path,
    printer: &config::Printer,
    directory: &Path,
    state_dir: &Path,
    limit: usize,
) -> Result<Value> {
    let label = if printer.name == "H2C" {
        "Mark1"
    } else {
        &printer.name
    };
    let output_dir = directory.join(label);
    let state_dir = state_dir.join(label);
    fs::create_dir_all(&output_dir)?;
    fs::create_dir_all(&state_dir)?;
    let status = mqtt::Connection::open(printer, Duration::from_secs(12))?.status()?;
    let printing = matches!(
        status["gcode_state"].as_str(),
        Some("RUNNING" | "PREPARE" | "PAUSE")
    );
    let mut remote = Ftp::new(
        printer.host.clone(),
        990,
        "bblp".into(),
        printer.access_code.clone(),
        Duration::from_secs(30),
    )?;
    let mut clips = remote.list("ipcam", "*.mp4")?;
    clips.sort_by_key(|clip| clip.mtime);
    let active = printing
        .then(|| clips.last().map(|clip| clip.name.clone()))
        .flatten();
    let now = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs() as i64;
    let mut archived = Vec::new();
    let mut unchanged = 0;
    let mut protected = 0;
    for clip in clips {
        if clip.size == 0
            || clip.name.to_ascii_lowercase().starts_with("temp")
            || clip.mtime.is_none_or(|time| now - time < MIN_AGE_SECONDS)
            || active.as_ref() == Some(&clip.name)
        {
            protected += 1;
            continue;
        }
        let name = playback_name(&clip)?;
        let output = output_dir.join(&name);
        let receipt_name = format!("{name}.json");
        let local_receipt = state_dir.join(&receipt_name);
        if saved(&clip, &output, &local_receipt)? {
            unchanged += 1;
            continue;
        }
        if archived.len() >= limit {
            break;
        }
        let cloud_receipt = output_dir.join(&receipt_name);
        if saved(&clip, &output, &cloud_receipt)? {
            write_json(
                &local_receipt,
                &serde_json::from_slice(&fs::read(cloud_receipt)?)?,
            )?;
            unchanged += 1;
            continue;
        }
        if resident_or_cloud_placeholder(&output) {
            bail!(
                "Playback already exists without a matching receipt: {}",
                output.display()
            )
        }
        let run_id = SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos();
        let scratch = Scratch(
            root.join(".cache/runs")
                .join(format!("camera-archive-{label}-{run_id}")),
        );
        fs::create_dir_all(&scratch.0)?;
        let (raw, source_sha) = gc::archive(&mut remote, &clip, &scratch.0)?;
        let temporary = scratch.0.join("playback.mp4");
        let (source_info, frames) = encode(root, &raw, &temporary)?;
        let sha = digest(&temporary)?;
        let bytes = temporary.metadata()?.len();
        let receipt = json!({
            "purpose":"This receipt identifies the native camera segment and its sampled playback.",
            "printer":label,"archived_at":crate::now(),
            "source":{"filename":clip.name,"bytes":clip.size,"modified_unix":clip.mtime,"sha256":source_sha,"media":source_info},
            "sample_fps":SAMPLE_FPS,"playback_fps":PLAYBACK_FPS,"frames":frames,
            "playback":{"filename":name,"bytes":bytes,"sha256":sha},
            "printer_at_archive":{"state":status["gcode_state"],"job":status["subtask_name"],"layer":status["layer_num"]}
        });
        let incoming = output_dir.join(format!(".{name}.part"));
        fs::copy(&temporary, &incoming)?;
        File::open(&incoming)?.sync_all()?;
        if digest(&incoming)? != sha {
            bail!("Playback archive checksum mismatch")
        }
        write_json(&cloud_receipt, &receipt)?;
        fs::rename(incoming, &output)?;
        gc::sync_directory(&output_dir)?;
        write_json(&local_receipt, &receipt)?;
        archived.push(json!({"path":output,"frames":frames,"bytes":bytes,"source_seconds":source_info["duration_seconds"]}));
    }
    Ok(
        json!({"printer":label,"archived":archived,"already_archived":unchanged,"active_or_recent":protected}),
    )
}

pub fn run(root: &Path, args: &mut Args) -> Result<()> {
    let directory = args
        .option("--archive-dir")
        .map(|path| crate::expand(&path));
    let limit = args.number("--limit", 8_usize)?;
    let name = if args.values.is_empty() {
        "all".to_owned()
    } else {
        args.positional("printer")?
    };
    args.finish()?;
    let home = crate::home()?;
    let directory = if let Some(directory) = directory {
        directory
    } else {
        let cloud = home.join("Library/Mobile Documents/com~apple~CloudDocs");
        if !cloud.is_dir() {
            bail!("iCloud Drive is unavailable; pass --archive-dir")
        }
        cloud.join("Bambu-recordings")
    };
    let state_dir = home.join(".config/h2c-recordings");
    let _lock = gc::ArchiveLock::open(&state_dir)?;
    let printers = config::configured(&home)?;
    let selected: Vec<_> = if name == "all" {
        printers.values().collect()
    } else {
        vec![printers.get(&name).context("Unknown configured printer")?]
    };
    let mut failed = false;
    for printer in selected {
        match archive_printer(root, printer, &directory, &state_dir, limit) {
            Ok(result) => println!("{}", serde_json::to_string_pretty(&result)?),
            Err(error) => {
                eprintln!("{}: {error:#}", printer.name);
                failed = true;
            }
        }
    }
    if failed {
        bail!("Some camera recordings could not be archived; native files remain on the printers")
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn archived_cloud_placeholders_do_not_need_video_downloads() {
        let root = std::env::temp_dir().join(format!("hsm-camera-receipt-{}", std::process::id()));
        fs::create_dir_all(&root).unwrap();
        let clip = gc::Clip {
            name: "record.mp4".into(),
            path: "/ipcam/record.mp4".into(),
            size: 120,
            mtime: Some(60),
        };
        let output = root.join(playback_name(&clip).unwrap());
        let receipt = root.join("receipt.json");
        write_json(&receipt, &json!({"source":{"bytes":120,"modified_unix":60},"sample_fps":SAMPLE_FPS,"playback_fps":PLAYBACK_FPS})).unwrap();
        assert!(!saved(&clip, &output, &receipt).unwrap());
        fs::write(
            root.join(format!(
                ".{}.icloud",
                output.file_name().unwrap().to_string_lossy()
            )),
            b"placeholder",
        )
        .unwrap();
        assert!(saved(&clip, &output, &receipt).unwrap());
        let mut changed = clip.clone();
        changed.size += 1;
        assert!(!saved(&changed, &output, &receipt).unwrap());
        fs::remove_dir_all(root).unwrap();
    }
}
