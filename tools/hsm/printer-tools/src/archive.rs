//! Read reviewed sliced plates and make print-only containers with unchanged toolpaths.
use crate::{digest, state, xml};
use anyhow::{bail, Context, Result};
use md5::{Digest as _, Md5};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs::{self, File, OpenOptions},
    io::{Read, Write},
    path::Path,
};
use zip::{write::SimpleFileOptions, CompressionMethod, ZipArchive, ZipWriter};

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct Filament {
    #[serde(rename = "type")]
    pub kind: String,
    pub colour: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Details {
    pub name: String,
    pub sha256: String,
    pub gcode_sha256: String,
    pub slots: BTreeMap<u8, Filament>,
    pub objects: Vec<String>,
}
fn entries(path: &Path) -> Result<Vec<(String, Vec<u8>)>> {
    let mut archive = ZipArchive::new(File::open(path)?)?;
    let mut entries = Vec::new();
    let mut names = BTreeSet::new();
    for i in 0..archive.len() {
        let mut entry = archive.by_index(i)?;
        let name = entry.name()?.into_owned();
        if !names.insert(name.clone()) {
            bail!("Duplicate ZIP entry: {name}")
        }
        let mut data = Vec::new();
        entry
            .read_to_end(&mut data)
            .context("Read and verify ZIP checksum")?;
        entries.push((name, data));
    }
    Ok(entries)
}
fn member<'a>(entries: &'a [(String, Vec<u8>)], name: &str) -> Result<&'a [u8]> {
    entries
        .iter()
        .find(|(key, _)| key == name)
        .map(|(_, bytes)| bytes.as_slice())
        .with_context(|| format!("Missing ZIP entry {name}"))
}
pub(crate) fn md5(bytes: &[u8]) -> String {
    Md5::digest(bytes)
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}
fn gcode_verified(entries: &[(String, Vec<u8>)], name: &str) -> Result<()> {
    let actual = md5(member(entries, name)?);
    let expected = std::str::from_utf8(member(entries, &format!("{name}.md5"))?)?
        .trim()
        .to_ascii_lowercase();
    if actual != expected {
        bail!("G-code checksum failed: {name}")
    }
    Ok(())
}
pub fn details(path: &Path) -> Result<Details> {
    let data = entries(path)?;
    let root = xml::parse(std::str::from_utf8(member(
        &data,
        "Metadata/slice_info.config",
    )?)?)?;
    let plates: Vec<_> = root.children_named("plate").collect();
    if plates.len() != 1 {
        bail!("This sender takes a single sliced plate")
    }
    let settings: Value =
        serde_json::from_slice(member(&data, "Metadata/project_settings.config")?)?;
    if settings["printer_model"] != "Bambu Lab H2C" {
        bail!("The plate must be sliced for the H2C printers")
    }
    gcode_verified(&data, "Metadata/plate_1.gcode")?;
    let mut slots = BTreeMap::new();
    for filament in plates[0].children_named("filament") {
        let index = filament
            .attribute("id")
            .context("Filament has no id")?
            .parse::<usize>()?
            .checked_sub(1)
            .context("Invalid filament id")?;
        let nozzle: u8 = state::text(&settings["filament_map"][index]).parse()?;
        if !matches!(nozzle, 1 | 2) || slots.contains_key(&nozzle) {
            bail!("Each active nozzle must use one external spool")
        }
        slots.insert(
            nozzle,
            Filament {
                kind: filament
                    .attribute("type")
                    .context("Filament has no type")?
                    .to_owned(),
                colour: filament
                    .attribute("color")
                    .context("Filament has no colour")?
                    .trim_start_matches('#')
                    .to_ascii_uppercase()
                    .chars()
                    .take(6)
                    .collect(),
            },
        );
    }
    if slots.is_empty() {
        bail!("The archive has no active filament")
    }
    Ok(Details {
        name: path
            .file_name()
            .context("Archive has no filename")?
            .to_string_lossy()
            .into_owned(),
        sha256: digest(path)?,
        gcode_sha256: crate::hash(member(&data, "Metadata/plate_1.gcode")?),
        slots,
        objects: plates[0]
            .children_named("object")
            .filter(|obj| obj.attribute("skipped") != Some("true"))
            .map(|obj| obj.attribute("name").unwrap_or("").to_owned())
            .collect(),
    })
}
pub fn verify_spools(details: &Details, reading: &Value) -> Result<()> {
    for (nozzle, expected) in &details.slots {
        let slot = (253 + u16::from(*nozzle)).to_string();
        let tray = reading["vir_slot"]
            .as_array()
            .and_then(|trays| trays.iter().find(|tray| state::text(&tray["id"]) == slot));
        let actual = tray.map(|tray| Filament {
            kind: state::text(&tray["tray_type"]),
            colour: state::text(&tray["tray_color"])
                .to_ascii_uppercase()
                .chars()
                .take(6)
                .collect(),
        });
        if actual.as_ref() != Some(expected) {
            bail!("External spool {slot} does not match the slice type and colour")
        }
    }
    Ok(())
}
fn serialize(element: &xml::Element, out: &mut String) {
    fn escape(text: &str) -> String {
        text.replace('&', "&amp;")
            .replace('<', "&lt;")
            .replace('>', "&gt;")
            .replace('"', "&quot;")
    }
    out.push('<');
    out.push_str(&element.name);
    for (key, value) in &element.attributes {
        out.push(' ');
        out.push_str(key);
        out.push_str("=\"");
        out.push_str(&escape(value));
        out.push('"');
    }
    if element.children.is_empty() && element.text.is_empty() {
        out.push_str(" />");
        return;
    }
    out.push('>');
    out.push_str(&escape(&element.text));
    for child in &element.children {
        serialize(child, out);
    }
    out.push_str("</");
    out.push_str(&element.name);
    out.push('>');
}
fn document(element: &xml::Element) -> Vec<u8> {
    let mut out = String::from("<?xml version='1.0' encoding='utf-8'?>\n");
    serialize(element, &mut out);
    out.into_bytes()
}
pub fn package(source: &Path, destination: &Path) -> Result<Value> {
    if destination.exists() || destination == source {
        bail!("Use a new destination; preserve the reviewed source archive")
    }
    let data = entries(source)?;
    let gcodes: Vec<_> = data
        .iter()
        .filter(|(name, _)| name.ends_with(".gcode"))
        .collect();
    if gcodes.is_empty() {
        bail!("The source contains no sliced G-code")
    }
    for (name, _) in &gcodes {
        gcode_verified(&data, name)?;
    }
    let mut model = xml::parse(std::str::from_utf8(member(&data, "3D/3dmodel.model")?)?)?;
    for tag in ["resources", "build"] {
        let child = model
            .children
            .iter_mut()
            .find(|e| e.local() == tag)
            .with_context(|| format!("Model has no {tag}"))?;
        child.attributes.clear();
        child.children.clear();
        child.text.clear();
    }
    model
        .attributes
        .retain(|(key, _)| key != "requiredextensions");
    let mut config = xml::parse(std::str::from_utf8(member(
        &data,
        "Metadata/model_settings.config",
    )?)?)?;
    config
        .children
        .retain(|e| !matches!(e.local(), "object" | "assemble"));
    for plate in config.children.iter_mut().filter(|e| e.local() == "plate") {
        plate.children.retain(|e| e.local() != "model_instance");
    }
    let changed = BTreeMap::from([
        ("3D/3dmodel.model", document(&model)),
        ("Metadata/model_settings.config", document(&config)),
    ]);
    let omitted: BTreeSet<_> = data
        .iter()
        .map(|(name, _)| name.as_str())
        .filter(|name| {
            name.starts_with("3D/Objects/")
                || name.starts_with("3D/_rels/")
                || matches!(
                    *name,
                    "Metadata/layer_config_ranges.xml" | "Metadata/cut_information.xml"
                )
        })
        .collect();
    let output = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(destination)?;
    let write_result = (|| -> Result<()> {
        let mut archive = ZipWriter::new(output);
        let options = SimpleFileOptions::default()
            .compression_method(CompressionMethod::Deflated)
            .compression_level(Some(6));
        for (name, body) in &data {
            if omitted.contains(name.as_str()) {
                continue;
            }
            archive.start_file(name, options)?;
            archive.write_all(changed.get(name.as_str()).unwrap_or(body))?;
        }
        archive.finish()?.sync_all()?;
        let verified = entries(destination)?;
        for (name, body) in &verified {
            if !changed.contains_key(name.as_str()) && body.as_slice() != member(&data, name)? {
                bail!("Unexpected change to {name}")
            }
        }
        Ok(())
    })();
    if let Err(error) = write_result {
        let _ = fs::remove_file(destination);
        return Err(error);
    }
    let gcode_hashes: BTreeMap<_, _> = gcodes
        .iter()
        .map(|(name, body)| (name.as_str(), crate::hash(body)))
        .collect();
    Ok(
        json!({"source_archive":source,"source_archive_sha256":digest(source)?,"print_only_archive":destination,"print_only_archive_sha256":digest(destination)?,"gcode_sha256":gcode_hashes,"gcode_byte_identical":true,"changed_container_entries":["3D/3dmodel.model","Metadata/model_settings.config"],"omitted_editable_geometry_entries":omitted}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::{SystemTime, UNIX_EPOCH};
    #[test]
    fn print_only_copy_keeps_reviewed_toolpaths_and_requires_matching_external_spools() {
        let root = std::env::temp_dir().join(format!(
            "hsm-printer-archive-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir_all(&root).unwrap();
        let source = root.join("reviewed.gcode.3mf");
        let output = root.join("print-only.gcode.3mf");
        let gcode = b"; reviewed fixture\nG28\nM400\n";
        let files = vec![
            ("3D/3dmodel.model",b"<model xmlns=\"http://schemas.microsoft.com/3dmanufacturing/core/2015/02\" requiredextensions=\"p\"><resources><object id=\"1\"/></resources><build><item objectid=\"1\"/></build></model>".to_vec()),
            ("3D/Objects/fixture.model",b"editable fixture".to_vec()),
            ("3D/_rels/3dmodel.model.rels",b"editable relationships".to_vec()),
            ("Metadata/model_settings.config",b"<config><object id=\"1\"/><plate><metadata key=\"plater_id\" value=\"1\"/><model_instance/></plate><assemble/></config>".to_vec()),
            ("Metadata/slice_info.config",b"<config><plate><filament id=\"1\" type=\"PETG\" color=\"#aabbccff\"/><object name=\"fixture\"/><object name=\"skipped\" skipped=\"true\"/></plate></config>".to_vec()),
            ("Metadata/project_settings.config",br#"{"printer_model":"Bambu Lab H2C","filament_map":["2"]}"#.to_vec()),
            ("Metadata/plate_1.gcode",gcode.to_vec()),
            ("Metadata/plate_1.gcode.md5",format!("{}\n",md5(gcode)).into_bytes()),
            ("Metadata/plate_1.png",b"retained thumbnail bytes".to_vec()),
        ];
        let mut zip = ZipWriter::new(File::create(&source).unwrap());
        for (name, body) in &files {
            zip.start_file(name, SimpleFileOptions::default()).unwrap();
            zip.write_all(body).unwrap();
        }
        zip.finish().unwrap();
        let original = fs::read(&source).unwrap();
        let details = details(&source).unwrap();
        assert_eq!(details.objects, ["fixture"]);
        assert_eq!(
            details.slots[&2],
            Filament {
                kind: "PETG".into(),
                colour: "AABBCC".into()
            }
        );
        assert!(verify_spools(
            &details,
            &json!({"vir_slot":[{"id":255,"tray_type":"PETG","tray_color":"aabbccff"}]})
        )
        .is_ok());
        assert!(verify_spools(
            &details,
            &json!({"vir_slot":[{"id":254,"tray_type":"PETG","tray_color":"AABBCCFF"}]})
        )
        .is_err());
        let receipt = package(&source, &output).unwrap();
        assert_eq!(receipt["gcode_byte_identical"], true);
        let result = entries(&output).unwrap();
        assert_eq!(member(&result, "Metadata/plate_1.gcode").unwrap(), gcode);
        assert!(member(&result, "3D/Objects/fixture.model").is_err());
        assert_eq!(fs::read(&source).unwrap(), original);
        let model =
            xml::parse(std::str::from_utf8(member(&result, "3D/3dmodel.model").unwrap()).unwrap())
                .unwrap();
        assert!(model.child("resources").unwrap().children.is_empty());
        assert!(model.child("build").unwrap().children.is_empty());
        assert!(model.attribute("requiredextensions").is_none());
        let config = xml::parse(
            std::str::from_utf8(member(&result, "Metadata/model_settings.config").unwrap())
                .unwrap(),
        )
        .unwrap();
        assert!(config.child("object").is_none());
        assert!(config.child("assemble").is_none());
        assert!(config
            .child("plate")
            .unwrap()
            .child("model_instance")
            .is_none());
        assert!(package(&source, &output).is_err());
        fs::remove_dir_all(root).unwrap();
    }
}
