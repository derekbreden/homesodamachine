//! Offline slicing through Bambu Studio's command line, and the cooling stage on what it emits.
//! Nothing here contacts a printer.

use crate::ids::md5_hex;
use crate::json::Json;
use crate::profile::SETTINGS_MEMBER;
use crate::sha256_hex;
use anyhow::{bail, Context, Result};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::io::{Read, Write};
use std::path::{Path, PathBuf};

pub const SLICER: &str = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio";
const PACKAGED_REPORT: &str = "Metadata/hsm_cooling.json";

fn is_cooling_hook(script: &str) -> bool {
    script.ends_with("/petgf-cooling") || script.contains("/cadlib/petgf_cooling.py")
}

/// The project as the command line takes it: the same archive without the cooling hook, which
/// the caller applies to the emitted archive itself. The project itself is left as it is.
pub fn cli_project(project: &Path, directory: &Path) -> Result<PathBuf> {
    let file = std::fs::File::open(project)?;
    let mut archive = zip::ZipArchive::new(file)?;
    let mut settings = {
        let mut data = String::new();
        archive.by_name(SETTINGS_MEMBER)?.read_to_string(&mut data)?;
        Json::parse(&data)?
    };
    let scripts: Vec<String> = settings.get("post_process").map(Json::list).unwrap_or(&[])
        .iter().filter_map(Json::text).map(String::from).collect();
    if scripts.iter().all(|s| s.is_empty()) {
        return Ok(project.to_path_buf());
    }
    if scripts.iter().any(|s| !s.is_empty() && !is_cooling_hook(s)) {
        bail!("The native CLI cannot execute this project's additional post-processing scripts");
    }
    settings.set("post_process", Json::List(Vec::new()));
    let stem = project.file_stem().and_then(|s| s.to_str()).unwrap_or("project");
    let output = directory.join(format!("{stem}.cli.3mf"));
    let mut target = zip::ZipWriter::new(std::fs::File::create(&output)?);
    for i in 0..archive.len() {
        let entry = archive.by_index_raw(i)?;
        if entry.name()? == SETTINGS_MEMBER {
            let options = zip::write::SimpleFileOptions::default()
                .compression_method(entry.compression())
                .last_modified_time(entry.last_modified().unwrap_or_default());
            drop(entry);
            target.start_file(SETTINGS_MEMBER, options)?;
            target.write_all((settings.dumps() + "\n").as_bytes())?;
        } else {
            target.raw_copy_file(entry)?;
        }
    }
    target.finish()?;
    Ok(output)
}

/// Slice every plate of `project` into `directory`; the log is `bambu-cli.log` there.
pub fn run(slicer: &Path, project: &Path, directory: &Path) -> Result<()> {
    std::fs::create_dir_all(directory)?;
    let directory = directory.canonicalize()?;
    let cli = cli_project(&project.canonicalize()?, &directory)?;
    let stem = project.file_stem().and_then(|s| s.to_str()).unwrap_or("project");
    let log = std::fs::File::create(directory.join("bambu-cli.log"))?;
    let status = std::process::Command::new(slicer)
        .args(["--slice", "0", "--arrange", "0", "--orient", "0", "--outputdir"])
        .arg(&directory)
        .arg("--export-3mf")
        .arg(format!("{stem}.gcode.3mf"))
        .arg(&cli)
        .current_dir(&directory)
        .stdout(log.try_clone()?)
        .stderr(log)
        .status()
        .with_context(|| format!("running {}", slicer.display()))?;
    println!("Offline slice exited {}; {}", status.code().unwrap_or(-1), directory.join("bambu-cli.log").display());
    if !status.success() {
        bail!("Bambu slice exited {}", status.code().unwrap_or(-1));
    }
    Ok(())
}

/// The cooling stage over every sliced archive in `directory`, with the plates' time estimates
/// in `result.json` carried forward.
pub fn apply_directory(directory: &Path, project: &Path) -> Result<BTreeMap<String, Value>> {
    let mut reports = BTreeMap::new();
    let mut archives: Vec<PathBuf> = std::fs::read_dir(directory)?
        .filter_map(|e| e.ok().map(|e| e.path()))
        .filter(|p| p.file_name().and_then(|n| n.to_str()).is_some_and(|n| n.ends_with(".gcode.3mf")))
        .collect();
    archives.sort();
    for path in archives {
        let name = path.file_name().unwrap().to_string_lossy().to_string();
        reports.insert(name, apply_archive(&path, Some(project))?);
    }
    let result_path = directory.join("result.json");
    if result_path.is_file() {
        let mut result = Json::parse(&std::fs::read_to_string(&result_path)?)?;
        if let Some(Json::List(plates)) = result.get("sliced_plates").cloned() {
            let mut plates = plates;
            for row in plates.iter_mut() {
                let id = row.get("id").map(|v| match v { Json::Number(t, _) => t.clone(), Json::Text(s) => s.clone(), _ => String::new() }).unwrap_or_default();
                let mut added = 0.0f64;
                for reading in reports.values() {
                    if reading["changed"].as_bool() != Some(true) {
                        continue;
                    }
                    for member in reading["members"].as_array().into_iter().flatten() {
                        if member["member"].as_str() == Some(&format!("Metadata/plate_{id}.gcode")) {
                            added = added.max(member["added_commanded_motion_seconds"].as_f64().unwrap_or(0.0));
                        }
                    }
                }
                if let Some(Json::Number(_, total)) = row.get("total_predication").cloned() {
                    let sum = total + added;
                    row.set("total_predication", Json::Number(crate::json::python_number(sum), sum));
                }
            }
            result.set("sliced_plates", Json::List(plates));
        }
        std::fs::write(&result_path, result.dumps() + "\n")?;
    }
    Ok(reports)
}

/// Package the processed paths and their checksums without altering the model meshes.
pub fn apply_archive(path: &Path, project: Option<&Path>) -> Result<Value> {
    let original_hash = sha256_hex(&std::fs::read(path)?);
    let mut archive = zip::ZipArchive::new(std::fs::File::open(path)?)?;
    if let Ok(mut packaged) = archive.by_name(PACKAGED_REPORT) {
        let mut data = String::new();
        packaged.read_to_string(&mut data)?;
        let mut result: Value = serde_json::from_str(&data)?;
        result["archive_sha256"] = json!(original_hash);
        result["changed"] = json!(false);
        result["already_processed"] = json!(true);
        return Ok(result);
    }
    let settings: Value = {
        let mut source = zip::ZipArchive::new(std::fs::File::open(project.unwrap_or(path))?)?;
        let mut data = String::new();
        source.by_name(SETTINGS_MEMBER)?.read_to_string(&mut data)?;
        serde_json::from_str(&data)?
    };
    let scratch = path.parent().unwrap_or(Path::new(".")).join(format!(".cooling-{}", std::process::id()));
    std::fs::create_dir_all(&scratch)?;
    let mut reports = Vec::new();
    let mut replaced: BTreeMap<String, Vec<u8>> = BTreeMap::new();
    let names: Vec<String> = archive.file_names().map(|n| n.map(|s| s.to_string())).collect::<Result<_, _>>()?;
    for member in names.iter().filter(|n| n.ends_with(".gcode")) {
        let base = Path::new(member).file_name().unwrap().to_string_lossy().to_string();
        let source = scratch.join(&base);
        {
            let mut entry = archive.by_name(member)?;
            let mut data = Vec::new();
            entry.read_to_end(&mut data)?;
            std::fs::write(&source, data)?;
        }
        let output = source.with_extension("processed.gcode");
        let mut reading = crate::cooling::foundation(&source, &output, &settings)?;
        let input_digest = sha256_hex(&std::fs::read(&source)?);
        reading["member"] = json!(member);
        reading["input_gcode_sha256"] = json!(input_digest);
        let changed = reading["changed"].as_bool() == Some(true);
        if changed || reading["already_processed"].as_bool() == Some(true) {
            let processed = std::fs::read(if changed { &output } else { &source })?;
            reading["output_gcode_sha256"] = json!(sha256_hex(&processed));
            replaced.insert(format!("{member}.md5"), md5_hex(&processed).into_bytes());
            let raw = path.parent().unwrap_or(Path::new(".")).join(&base);
            if changed && raw.is_file() && sha256_hex(&std::fs::read(&raw)?) == input_digest {
                std::fs::write(&raw, &processed)?;
            }
            if changed {
                replaced.insert(member.clone(), processed);
            }
        }
        reports.push(reading);
    }
    let added: f64 = reports.iter().map(|r| r["added_commanded_motion_seconds"].as_f64().unwrap_or(0.0)).sum();
    let any = replaced.keys().any(|k| !k.ends_with(".md5")) || !replaced.is_empty();
    let mut result = json!({
        "input_archive_sha256": original_hash, "changed": any, "members": reports,
        "added_commanded_motion_seconds": added,
        "estimate_scope": "Native estimate plus the added constant-feed motion time; acceleration and fan spin-up are not simulated.",
    });
    if !replaced.is_empty() {
        if names.iter().any(|n| n == "Metadata/slice_info.config") {
            let mut info = String::new();
            archive.by_name("Metadata/slice_info.config")?.read_to_string(&mut info)?;
            replaced.insert("Metadata/slice_info.config".into(), add_predictions(&info, &result["members"])?.into_bytes());
        }
        let temporary = scratch.join("processed.3mf");
        {
            let mut target = zip::ZipWriter::new(std::fs::File::create(&temporary)?);
            for i in 0..archive.len() {
                let entry = archive.by_index_raw(i)?;
                let name = entry.name()?.to_string();
                if let Some(data) = replaced.get(&name) {
                    let options = zip::write::SimpleFileOptions::default()
                        .compression_method(entry.compression())
                        .last_modified_time(entry.last_modified().unwrap_or_default())
                        .large_file(data.len() as u64 > u32::MAX as u64);
                    drop(entry);
                    target.start_file(name.as_str(), options)?;
                    target.write_all(data)?;
                } else {
                    target.raw_copy_file(entry)?;
                }
            }
            target.start_file(PACKAGED_REPORT, zip::write::SimpleFileOptions::default().compression_method(zip::CompressionMethod::Deflated))?;
            target.write_all((serde_json::to_string_pretty(&result)? + "\n").as_bytes())?;
            target.finish()?;
        }
        std::fs::rename(&temporary, path)?;
    }
    let _ = std::fs::remove_dir_all(&scratch);
    result["archive_sha256"] = json!(sha256_hex(&std::fs::read(path)?));
    let report = path.with_extension("cooling.json");
    std::fs::write(&report, serde_json::to_string_pretty(&result)? + "\n")?;
    Ok(result)
}

/// Each plate's predicted time in slice_info.config, with the cooling stage's added seconds.
pub(crate) fn add_predictions(info: &str, members: &Value) -> Result<String> {
    let mut out = String::with_capacity(info.len());
    let mut rest = info;
    while let Some(start) = rest.find("<plate>") {
        let end = rest[start..].find("</plate>").map(|e| start + e + "</plate>".len()).context("unclosed plate")?;
        out.push_str(&rest[..start]);
        let mut block = rest[start..end].to_string();
        if let Some(index) = attribute_value(&block, "index") {
            let seconds: f64 = members.as_array().into_iter().flatten()
                .filter(|r| r["member"].as_str() == Some(&format!("Metadata/plate_{index}.gcode")))
                .map(|r| r["added_commanded_motion_seconds"].as_f64().unwrap_or(0.0))
                .sum();
            if let Some(prediction) = attribute_value(&block, "prediction") {
                let value: f64 = prediction.parse().unwrap_or(0.0);
                let new = format!("{}", (value + seconds).ceil() as i64);
                block = block.replacen(&format!("key=\"prediction\" value=\"{prediction}\""), &format!("key=\"prediction\" value=\"{new}\""), 1);
            }
        }
        out.push_str(&block);
        rest = &rest[end..];
    }
    out.push_str(rest);
    Ok(out)
}

fn attribute_value(block: &str, key: &str) -> Option<String> {
    let marker = format!("key=\"{key}\" value=\"");
    let at = block.find(&marker)? + marker.len();
    let end = block[at..].find('"')?;
    Some(block[at..at + end].to_string())
}

/// The settings Bambu Studio hands a post-processing script, through SLIC3R_* variables.
pub fn environment_settings() -> Value {
    let mut settings = serde_json::Map::new();
    for key in ["filament_settings_id", "overhang_fan_speed", "filament_bridge_speed", "bridge_speed"] {
        let raw = std::env::var(format!("SLIC3R_{}", key.to_uppercase())).unwrap_or_default();
        let value = match serde_json::from_str::<Value>(&raw) {
            Ok(Value::Array(items)) => Value::Array(items),
            Ok(other) => Value::Array(vec![other]),
            Err(_) if raw.is_empty() => Value::Array(Vec::new()),
            Err(_) => {
                let delimiter = if key == "filament_settings_id" || raw.contains(';') { ';' } else { ',' };
                Value::Array(raw.split(delimiter).map(|s| Value::String(s.to_string())).collect())
            }
        };
        settings.insert(key.into(), value);
    }
    Value::Object(settings)
}
