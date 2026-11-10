//! Package the reviewed idle-printer maintenance program without sending it to a printer.
use crate::{xml, Args};
use anyhow::{bail, Context, Result};
use serde_json::{json, Value};
use std::{
    collections::BTreeMap,
    fs::{self, File},
    io::{Read, Write},
    path::Path,
};
use zip::{write::SimpleFileOptions, CompressionMethod, DateTime, ZipArchive, ZipWriter};

pub fn verify(gcode: &[u8]) -> Result<Value> {
    let text = std::str::from_utf8(gcode)?;
    let commands: Vec<_> = text
        .lines()
        .map(|line| line.split(';').next().unwrap().trim())
        .filter(|line| !line.is_empty())
        .collect();
    let mut depth = 0;
    for command in &commands {
        if command.starts_with("M622 ") {
            depth += 1
        } else if *command == "M623" {
            depth -= 1
        }
        if depth < 0 {
            bail!("Unbalanced firmware conditional")
        }
    }
    if depth != 0 {
        bail!("Unclosed firmware conditional")
    }
    let extrusions: Vec<_> = commands
        .iter()
        .copied()
        .filter(|line| {
            line.split_whitespace()
                .next()
                .is_some_and(|key| matches!(key, "G0" | "G1" | "G2" | "G3"))
                && line
                    .split_whitespace()
                    .skip(1)
                    .any(|word| word.starts_with('E'))
        })
        .collect();
    if extrusions != ["G1 E45 F449.008", "G1 E-3 F1800"] {
        bail!("Unexpected maintenance extrusions: {extrusions:?}")
    }
    let position = |line: &str| {
        commands
            .iter()
            .position(|command| *command == line)
            .with_context(|| format!("Missing maintenance command {line}"))
    };
    let extrude = position("G1 E45 F449.008")?;
    if commands.last() != Some(&"M73 P100 R0")
        || !commands.contains(&"M83")
        || position("M109 S280")? > extrude
        || position("G28 Z P0 T250")? > extrude
        || position("T0 H-1")? > extrude
    {
        bail!("Maintenance preparation order changed")
    }
    if commands.iter().any(|line| {
        [
            "M190", "G29 A", "G383", "M983.3", "M500", "T65535", "T65279",
        ]
        .iter()
        .any(|prefix| line.starts_with(prefix))
            || line.contains(['{', '}'])
            || (line.starts_with("M140 ") && *line != "M140 S0")
            || (line.starts_with("M141 ") && *line != "M141 S0")
    }) {
        bail!("Maintenance program contains an unexpected calibration, heater or unload command")
    }
    let cleanup = &commands[position("M73 P95 R0")?..];
    for command in [
        "M104 S0 T0",
        "M104 S0 T1",
        "M140 S0",
        "M141 S0",
        "M211 X1 Y1 Z1",
        "M18",
    ] {
        if !cleanup.contains(&command) {
            bail!("Missing maintenance cleanup {command}")
        }
    }
    Ok(
        json!({"gcode_sha256":crate::hash(gcode),"explicit_extrusions":extrusions,"explicit_purge_temperature_c":280,"material_prepare_flush_temperature_c":300,"bed_heating":false,"chamber_heating":false,"bed_deposition":false,"print_end_unload":false,"firmware_conditionals_balanced":true,"heater_shutdown_present":true,"nozzle_wipe_present":commands.contains(&"G150 T265"),"physical_validation":"required"}),
    )
}
pub fn run(root: &Path, args: &mut Args) -> Result<()> {
    let output = args
        .option("--output")
        .map(|s| crate::expand(&s))
        .unwrap_or_else(|| root.join(".cache/h2c-purge-v1/h2c-left-petgf-purge-v1.gcode.3mf"));
    args.finish()?;
    let directory = root.join("tools/h2c-purge");
    let source: Value = serde_json::from_slice(&fs::read(directory.join("source.json"))?)?;
    let gcode = fs::read(directory.join("h2c-left-petgf-purge.gcode"))?;
    let mut receipt = verify(&gcode)?;
    let metadata: BTreeMap<String, String> =
        serde_json::from_slice(&fs::read(directory.join("package-metadata.json"))?)?;
    let mut entries: BTreeMap<String, Vec<u8>> = metadata
        .into_iter()
        .map(|(name, body)| (name, body.into_bytes()))
        .collect();
    let mut settings: Value = serde_json::from_slice(
        entries
            .get("Metadata/project_settings.config")
            .context("Missing project settings")?,
    )?;
    let mapping = settings["filament_map"]
        .as_array()
        .context("Missing filament map")?;
    if mapping.len() != 1
        || crate::state::text(&mapping[0]) != "1"
        || settings["printer_model"] != "Bambu Lab H2C"
    {
        bail!("Maintenance metadata must name the fixed left H2C nozzle")
    }
    settings["machine_start_gcode"] = json!(std::str::from_utf8(&gcode)?);
    settings["machine_end_gcode"] = json!("");
    entries.insert(
        "Metadata/project_settings.config".into(),
        serde_json::to_vec_pretty(&settings)?,
    );
    entries.insert("Metadata/plate_1.gcode".into(), gcode.clone());
    entries.insert(
        "Metadata/plate_1.gcode.md5".into(),
        crate::archive::md5(&gcode).into_bytes(),
    );
    let thumbnail: &[u8] = &[
        137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0, 13, 73, 72, 68, 82, 0, 0, 0, 1, 0, 0, 0, 1, 8, 4,
        0, 0, 0, 181, 28, 12, 2, 0, 0, 0, 11, 73, 68, 65, 84, 120, 218, 99, 100, 248, 15, 0, 1, 5,
        1, 1, 39, 24, 227, 102, 0, 0, 0, 0, 73, 69, 78, 68, 174, 66, 96, 130,
    ];
    for name in [
        "plate_1.png",
        "plate_1_small.png",
        "plate_no_light_1.png",
        "top_1.png",
        "pick_1.png",
    ] {
        entries.insert(format!("Metadata/{name}"), thumbnail.to_vec());
    }
    if let Some(parent) = output.parent() {
        fs::create_dir_all(parent)?;
    }
    let mut archive = ZipWriter::new(File::create(&output)?);
    let options = SimpleFileOptions::default()
        .compression_method(CompressionMethod::Deflated)
        .last_modified_time(
            DateTime::from_date_and_time(2026, 10, 1, 0, 0, 0)
                .map_err(|_| anyhow::anyhow!("Invalid archive date"))?,
        );
    for (name, body) in &entries {
        archive.start_file(name, options)?;
        archive.write_all(body)?;
    }
    archive.finish()?.sync_all()?;
    let mut archive = ZipArchive::new(File::open(&output)?)?;
    for index in 0..archive.len() {
        let mut member = archive.by_index(index)?;
        let mut bytes = Vec::new();
        member.read_to_end(&mut bytes)?;
        if entries.get(member.name()?.as_ref()) != Some(&bytes) {
            bail!("Maintenance archive member changed")
        }
    }
    let slice = xml::parse(std::str::from_utf8(
        entries
            .get("Metadata/slice_info.config")
            .context("Missing slice info")?,
    )?)?;
    if slice
        .children_named("plate")
        .any(|plate| plate.children_named("object").next().is_some())
    {
        bail!("Maintenance archive contains a model object")
    }
    receipt["archive"] = json!(output.strip_prefix(root).unwrap_or(&output));
    receipt["archive_sha256"] = json!(crate::digest(&output)?);
    receipt["source_archive_sha256"] = source["native_archive_sha256"].clone();
    receipt["objects"] = json!(0);
    receipt["active_nozzle"] = json!("fixed left hardened 0.4 mm");
    receipt["expected_external_spool"] = json!(254);
    let text = format!("{}\n", serde_json::to_string_pretty(&receipt)?);
    fs::write(
        output
            .parent()
            .context("Output has no parent")?
            .join("preflight.json"),
        &text,
    )?;
    print!("{text}");
    Ok(())
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn reviewed_program_rejects_extra_extrusion_and_missing_shutdown() {
        let source = include_bytes!("../../../h2c-purge/h2c-left-petgf-purge.gcode");
        assert!(verify(source).is_ok());
        let text = std::str::from_utf8(source).unwrap();
        assert!(verify(
            text.replace("G1 E45 F449.008", "G1 E46 F449.008")
                .as_bytes()
        )
        .is_err());
        assert!(verify(text.replace("M104 S0 T1", "").as_bytes()).is_err());
    }
}
