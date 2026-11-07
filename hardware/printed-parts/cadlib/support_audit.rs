//! support-audit — the support-removal topology of one sliced plate.
//!
//!     support-audit --piece P --gcode <plate.gcode | archive.gcode.3mf> [--model STL] [--profile 3MF]
//!     support-audit --piece P --slice-current --model STL --profile 3MF [--refreshed-profile-out 3MF]
//!     common: [--profile-label L] [--slicer PATH] [--json-out FILE] [--include-unlabelled-support]
//!
//! It follows the support paths through the layers and reports each connected support body,
//! where it starts, how far it climbs before its first model interface, and its separate interface
//! islands (`hsm_print_prep::audit`). These are measurements of one slice; removal effort and
//! contact finish are observations of the physical print.
//!
//! `--slice-current` puts the model into a temporary copy of the profile project and slices that:
//! loading a project's settings any other way lets installed presets fill gaps, so the project
//! itself is authoritative. Bambu Studio first converts the STL into its normalised object
//! member; that member alone replaces the template's mesh, and every process, printer, filament
//! and plate setting stays the profile's own. `--profile-label` names the profile in the record
//! when `--profile` is a copy, for example `git:<hash>:<path>` for a project kept only in history.

use anyhow::{bail, Context, Result};
use hsm_print_prep::audit::{self, Transform};
use hsm_print_prep::{sha256_hex, slice, xml};
use serde_json::json;
use std::io::{Read, Write};
use std::path::{Path, PathBuf};

fn members(path: &Path) -> Result<Vec<(String, Vec<u8>)>> {
    let mut archive = zip::ZipArchive::new(std::fs::File::open(path).with_context(|| format!("opening {}", path.display()))?)?;
    let mut out = Vec::new();
    for i in 0..archive.len() {
        let mut entry = archive.by_index(i)?;
        let name = entry.name()?.to_string();
        let mut bytes = Vec::new();
        entry.read_to_end(&mut bytes)?;
        out.push((name, bytes));
    }
    Ok(out)
}

fn member<'a>(all: &'a [(String, Vec<u8>)], name: &str) -> Result<&'a [u8]> {
    all.iter().find(|(n, _)| n == name).map(|(_, b)| b.as_slice()).with_context(|| format!("no {name}"))
}

fn transform(value: Option<&str>) -> Transform {
    let mut out = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0];
    if let Some(text) = value {
        for (i, v) in text.split_whitespace().filter_map(|v| v.parse::<f64>().ok()).take(12).enumerate() {
            out[i] = v;
        }
    }
    out
}

fn first<'a>(root: &'a xml::Element, local: &str) -> Option<&'a xml::Element> {
    root.descendants().into_iter().find(|e| e.local() == local)
}

/// Plate coordinates back into the CAD frame, from a project's first object.
fn profile_cad_transform(profile: &Path) -> Result<Option<Transform>> {
    let all = members(profile)?;
    let settings = xml::parse(std::str::from_utf8(member(&all, "Metadata/model_settings.config")?)?)?;
    let mut source = [None; 3];
    for m in settings.descendants() {
        if m.local() == "metadata" {
            for (i, key) in ["source_offset_x", "source_offset_y", "source_offset_z"].iter().enumerate() {
                if m.attribute("key") == Some(key) {
                    source[i] = m.attribute("value").and_then(|v| v.parse::<f64>().ok());
                }
            }
        }
    }
    let model = xml::parse(std::str::from_utf8(member(&all, "3D/3dmodel.model")?)?)?;
    let (Some(item), Some(component)) = (first(&model, "item"), first(&model, "component")) else { return Ok(None) };
    let (Some(sx), Some(sy), Some(sz)) = (source[0], source[1], source[2]) else { return Ok(None) };
    let local_to_plate = audit::compose(&transform(component.attribute("transform")), &transform(item.attribute("transform")));
    let mut out = audit::inverse(&local_to_plate).context("the profile has a singular object transform")?;
    out[9] += sx;
    out[10] += sy;
    out[11] += sz;
    Ok(Some(out))
}

/// A transform value with twelve significant digits, trailing zeros dropped.
fn g12(v: f64) -> String {
    if v == 0.0 || !v.is_finite() {
        return if v == 0.0 { "0".into() } else { v.to_string() };
    }
    let exponent = v.abs().log10().floor() as i32;
    let decimals = (11 - exponent).max(0) as usize;
    let text = format!("{v:.decimals$}");
    if text.contains('.') { text.trim_end_matches('0').trim_end_matches('.').to_string() } else { text }
}

fn find(haystack: &[u8], needle: &[u8], from: usize) -> Option<usize> {
    haystack[from.min(haystack.len())..].windows(needle.len()).position(|w| w == needle).map(|i| i + from)
}

/// The first `  <object …>…  </object>` block, as Bambu Studio indents its object settings.
fn object_block(settings: &[u8]) -> Option<(usize, usize)> {
    let start = find(settings, b"  <object ", 0).or_else(|| find(settings, b"  <object>", 0))?;
    let end = find(settings, b"  </object>", start)? + b"  </object>".len();
    Some((start, end))
}

fn object_uuid(object: &[u8]) -> Option<Vec<u8>> {
    let at = find(object, b"<object id=\"1\" p:UUID=\"", 0)? + b"<object id=\"1\" p:UUID=\"".len();
    let end = find(object, b"\"", at)?;
    Some(object[at..end].to_vec())
}

/// Move the replacement object's lowest transformed vertex back onto plate Z zero.
fn reseat_build_item(model: &[u8], object: &[u8]) -> Result<(Vec<u8>, f64)> {
    let text = std::str::from_utf8(model)?;
    let root = xml::parse(text)?;
    let item = first(&root, "item").context("the project has no build item")?;
    let component = first(&root, "component").context("the project has no component")?;
    let old = item.attribute("transform").context("the project has no replaceable build-item transform")?.to_string();
    let mut build = transform(Some(&old));
    let combined = audit::compose(&transform(component.attribute("transform")), &build);
    let body = std::str::from_utf8(object)?;
    let mut lowest = f64::INFINITY;
    for chunk in body.split("<vertex ").skip(1) {
        let tag = &chunk[..chunk.find('>').unwrap_or(chunk.len())];
        let get = |k: &str| -> f64 {
            let needle = format!("{k}=\"");
            tag.find(&needle).and_then(|at| {
                let rest = &tag[at + needle.len()..];
                rest[..rest.find('"')?].parse().ok()
            }).unwrap_or(0.0)
        };
        lowest = lowest.min(audit::apply([get("x"), get("y"), get("z")], &combined)[2]);
    }
    let shift = if lowest.is_finite() && lowest.abs() > 1e-6 { -lowest } else { 0.0 };
    if shift == 0.0 {
        return Ok((model.to_vec(), 0.0));
    }
    build[11] += shift;
    let new = build.iter().map(|v| g12(*v)).collect::<Vec<_>>().join(" ");
    let pattern = format!("transform=\"{old}\"");
    let at = text.find("<item").and_then(|i| text[i..].find(&pattern).map(|j| i + j)).context("the project has no replaceable build-item transform")?;
    let out = format!("{}transform=\"{new}\"{}", &text[..at], &text[at + pattern.len()..]);
    Ok((out.into_bytes(), shift))
}

/// Slice `model` through a temporary copy of `profile` with only its mesh refreshed.
fn current_profile_slice(model: &Path, profile: &Path, slicer: &Path, directory: &Path) -> Result<(PathBuf, PathBuf, f64)> {
    let mesh_project = directory.join("current-mesh.3mf");
    // Bambu Studio writes its result ledger where it runs; both runs stay in this directory.
    let status = std::process::Command::new(slicer).arg("--export-3mf").arg(&mesh_project).args(["--arrange", "0", "--orient", "0"])
        .arg(model.canonicalize()?).current_dir(directory).status()?;
    if !status.success() {
        bail!("Bambu Studio could not convert {}", model.display());
    }
    let template = members(profile)?;
    let current = members(&mesh_project)?;
    let is_object = |n: &str| n.starts_with("3D/Objects/") && n.ends_with(".model");
    let template_object = template.iter().find(|(n, _)| is_object(n)).map(|(n, _)| n.clone()).context("the profile has no object member")?;
    let new_object = current.iter().find(|(n, _)| is_object(n)).map(|(_, b)| b.clone()).context("the converted model has no object member")?;
    let (Some(old_uuid), Some(new_uuid)) = (object_uuid(member(&template, &template_object)?), object_uuid(&new_object)) else {
        bail!("the template or current 3MF has no replaceable object UUID");
    };
    let at = find(&new_object, &new_uuid, 0).unwrap();
    let new_object = [&new_object[..at], &old_uuid[..], &new_object[at + new_uuid.len()..]].concat();
    let new_settings = member(&current, "Metadata/model_settings.config")?;
    let (s0, s1) = object_block(new_settings).context("the replacement project has no object settings")?;
    let offsets = xml::parse(std::str::from_utf8(new_settings)?)?;
    for key in ["source_offset_x", "source_offset_y", "source_offset_z"] {
        if !offsets.descendants().iter().any(|m| m.local() == "metadata" && m.attribute("key") == Some(key)) {
            bail!("the replacement project has no {key} metadata");
        }
    }
    let (build_model, shift) = reseat_build_item(member(&template, "3D/3dmodel.model")?, &new_object)?;
    let current_project = directory.join("current-profile.3mf");
    {
        let mut out = zip::ZipWriter::new(std::fs::File::create(&current_project)?);
        for (name, bytes) in &template {
            let payload: Vec<u8> = if *name == template_object {
                new_object.clone()
            } else if name == "3D/3dmodel.model" {
                build_model.clone()
            } else if name == "Metadata/model_settings.config" {
                let (t0, t1) = object_block(bytes).context("the profile has no replaceable object settings")?;
                [&bytes[..t0], &new_settings[s0..s1], &bytes[t1..]].concat()
            } else {
                bytes.clone()
            };
            out.start_file(name.as_str(), hsm_print_prep::project::options())?;
            out.write_all(&payload)?;
        }
        out.finish()?;
    }
    let output = directory.join("slice");
    std::fs::create_dir(&output)?;
    let status = std::process::Command::new(slicer).args(["--slice", "0", "--outputdir"]).arg(&output).arg(&current_project)
        .current_dir(directory).status()?;
    if !status.success() {
        bail!("Bambu Studio could not slice the refreshed profile");
    }
    let mut plates: Vec<PathBuf> = std::fs::read_dir(&output)?.filter_map(|e| e.ok().map(|e| e.path()))
        .filter(|p| p.file_name().and_then(|n| n.to_str()).is_some_and(|n| n.starts_with("plate_") && n.ends_with(".gcode"))).collect();
    plates.sort();
    if plates.len() != 1 {
        bail!("expected one plate G-code, found {} in {}", plates.len(), output.display());
    }
    Ok((plates.remove(0), current_project, shift))
}

fn file_sha(path: &Path) -> Result<String> {
    Ok(sha256_hex(&std::fs::read(path).with_context(|| format!("reading {}", path.display()))?))
}

/// A plate's G-code, from a G-code file or a sliced archive.
fn gcode_bytes(path: &Path) -> Result<Vec<u8>> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    if bytes.starts_with(b"PK") {
        return hsm_print_prep::gcode::plate_gcode(path);
    }
    Ok(bytes)
}

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let (mut piece, mut gcode, mut model, mut profile, mut slice_current, mut refreshed, mut label, mut json_out, mut unlabelled) =
        (None, None, None, None, false, None, None, None, false);
    let mut slicer = PathBuf::from(slice::SLICER);
    while let Some(arg) = args.next() {
        let mut value = || args.next().with_context(|| format!("{arg} needs a value"));
        match arg.as_str() {
            "--piece" => piece = Some(value()?),
            "--gcode" => gcode = Some(PathBuf::from(value()?)),
            "--model" => model = Some(PathBuf::from(value()?)),
            "--profile" => profile = Some(PathBuf::from(value()?)),
            "--slice-current" => slice_current = true,
            "--refreshed-profile-out" => refreshed = Some(PathBuf::from(value()?)),
            "--profile-label" => label = Some(value()?),
            "--slicer" => slicer = PathBuf::from(value()?),
            "--json-out" => json_out = Some(PathBuf::from(value()?)),
            "--include-unlabelled-support" => unlabelled = true,
            _ => bail!("unknown argument {arg}"),
        }
    }
    let piece = piece.context("--piece is required")?;
    if slice_current && gcode.is_some() {
        bail!("use either --gcode or --slice-current, not both");
    }
    if refreshed.is_some() && !slice_current {
        bail!("--refreshed-profile-out requires --slice-current");
    }
    if slice_current && (model.is_none() || profile.is_none()) {
        bail!("--slice-current requires --model and --profile");
    }
    if !slice_current && gcode.is_none() {
        bail!("--gcode is required unless --slice-current is used");
    }
    for path in [&gcode, &model, &profile].into_iter().flatten() {
        if !path.is_file() {
            bail!("not a file: {}", path.display());
        }
    }
    let inputs = |gcode_name: String, gcode: &[u8]| -> Result<serde_json::Value> {
        Ok(json!({"gcode": gcode_name, "gcode_sha256": sha256_hex(gcode),
                  "model": model.as_ref().map(|m| m.display().to_string()),
                  "model_sha256": model.as_ref().map(|m| file_sha(m)).transpose()?,
                  "profile": label.clone().or_else(|| profile.as_ref().map(|p| p.display().to_string())),
                  "profile_sha256": profile.as_ref().map(|p| file_sha(p)).transpose()?}))
    };
    let result = if slice_current {
        // Slicing is one of the Mac's heavy runs.
        hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
        let directory = std::env::temp_dir().join(format!("support-audit-{}", std::process::id()));
        std::fs::create_dir_all(&directory)?;
        let outcome = (|| -> Result<serde_json::Value> {
            let (plate, coordinates, reseat) = current_profile_slice(model.as_ref().unwrap(), profile.as_ref().unwrap(), &slicer, &directory)?;
            let bytes = std::fs::read(&plate)?;
            let options = audit::Options { piece: piece.clone(), object: None, include_unlabelled: unlabelled,
                cad_transform: profile_cad_transform(&coordinates)?, bed_reseat: Some(reseat),
                inputs: inputs(plate.file_name().unwrap().to_string_lossy().to_string(), &bytes)? };
            if let Some(out) = &refreshed {
                std::fs::copy(&coordinates, out)?;
            }
            Ok(audit::audit(&bytes, &options))
        })();
        let _ = std::fs::remove_dir_all(&directory);
        outcome?
    } else {
        let path = gcode.as_ref().unwrap();
        let bytes = gcode_bytes(path)?;
        let cad = match &profile { Some(p) => profile_cad_transform(p)?, None => None };
        let options = audit::Options { piece: piece.clone(), object: None, include_unlabelled: unlabelled, cad_transform: cad, bed_reseat: None,
            inputs: inputs(path.file_name().unwrap().to_string_lossy().to_string(), &bytes)? };
        audit::audit(&bytes, &options)
    };
    let encoded = serde_json::to_string_pretty(&result)? + "\n";
    if let Some(out) = json_out {
        std::fs::write(out, &encoded)?;
    }
    print!("{encoded}");
    Ok(())
}
