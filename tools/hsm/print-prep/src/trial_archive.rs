//! Packages a trial plate as a print-only Mark2 archive bound to its sequenced motion.
//!
//! The native slice's archive supplies everything else: the archive carries the sequenced
//! G-code with its estimates and filament, and leaves out the editable geometry.

use crate::python_text::{sum, Json};
use anyhow::{bail, ensure, Context, Result};
use std::f64::consts::PI;
use std::fs;
use std::io::{Read, Write};
use std::path::Path;

const GCODE: &str = "Metadata/plate_1.gcode";
const SLICE: &str = "Metadata/slice_info.config";
const LAYOUT: &str = "Metadata/plate_1.json";
const MODEL: &str = "3D/3dmodel.model";
const SETTINGS: &str = "Metadata/model_settings.config";

fn duration(seconds: f64) -> String {
    let total = seconds.ceil() as i64;
    format!("{}h {}m {}s", total / 3600, total / 60 % 60, total % 60)
}

/// The first header line that is `key` followed by a plain decimal.
fn header_number(gcode: &[u8], key: &str) -> Result<f64> {
    for line in gcode.split(|b| *b == b'\n') {
        if let Some(value) = line.strip_prefix(key.as_bytes()) {
            if !value.is_empty() && value.iter().all(|c| *c == b'.' || c.is_ascii_digit()) {
                return Ok(std::str::from_utf8(value)?.parse()?);
            }
        }
    }
    bail!("The G-code has no {key:?}")
}

/// The G-code with the first line starting `key` made `line`.
fn replace_line(gcode: &[u8], key: &str, line: &str) -> Result<Vec<u8>> {
    let mut at = 0;
    while at <= gcode.len() {
        let end = gcode[at..].iter().position(|b| *b == b'\n').map_or(gcode.len(), |i| at + i);
        if gcode[at..end].starts_with(key.as_bytes()) {
            return Ok([&gcode[..at], line.as_bytes(), &gcode[end..]].concat());
        }
        at = end + 1;
    }
    bail!("The Bambu header has no {key:?}")
}

/// The startup's progress events, showing the remaining minutes of the sequenced motion.
fn startup_progress(gcode: &[u8], minutes: i64) -> Result<Vec<u8>> {
    const MARK: &[u8] = b"; MACHINE_START_GCODE_END\n";
    let split = gcode.windows(MARK.len()).position(|w| w == MARK).context("The G-code has no startup end")?;
    let mut out = Vec::with_capacity(gcode.len());
    for line in gcode[..split].split_inclusive(|b| *b == b'\n') {
        let digits = [b"M73 P0 R".as_slice(), b"M73 P1 R"].iter().find(|p| line.starts_with(p))
            .map(|p| line[p.len()..].iter().take_while(|c| c.is_ascii_digit()).count());
        match digits {
            Some(digits) if digits > 0 => {
                out.extend_from_slice(&line[..8]);
                out.extend_from_slice(minutes.to_string().as_bytes());
                out.extend_from_slice(&line[8 + digits..]);
            }
            _ => out.extend_from_slice(line),
        }
    }
    out.extend_from_slice(&gcode[split..]);
    Ok(out)
}

/// The number of non-overlapping places `pattern` occurs.
fn count(data: &[u8], pattern: &[u8]) -> usize {
    let (mut found, mut at) = (0, 0);
    while let Some(i) = data[at..].windows(pattern.len()).position(|w| w == pattern) {
        found += 1;
        at += i + pattern.len();
    }
    found
}

/// An element as Python's ElementTree holds one: the text before its first child and the tail
/// after its end.
#[derive(Default)]
struct Element {
    tag: String,
    attrib: Vec<(String, String)>,
    text: String,
    tail: String,
    children: Vec<Element>,
}

impl Element {
    fn set(&mut self, key: &str, value: String) {
        match self.attrib.iter_mut().find(|(k, _)| k == key) {
            Some(slot) => slot.1 = value,
            None => self.attrib.push((key.to_string(), value)),
        }
    }

    fn child(&mut self, tag: &str) -> Result<&mut Element> {
        self.children.iter_mut().find(|c| c.tag == tag).with_context(|| format!("No <{tag}>"))
    }
}

fn unescape(text: &str) -> Result<String> {
    let mut out = String::with_capacity(text.len());
    let mut rest = text;
    while let Some(at) = rest.find('&') {
        out.push_str(&rest[..at]);
        let end = rest[at..].find(';').context("An unterminated entity")? + at;
        let entity = &rest[at + 1..end];
        let c = match entity {
            "amp" => '&',
            "lt" => '<',
            "gt" => '>',
            "quot" => '"',
            "apos" => '\'',
            _ => {
                let code = match entity.strip_prefix("#x") {
                    Some(hex) => u32::from_str_radix(hex, 16)?,
                    None => entity.strip_prefix('#').context("An undefined entity")?.parse()?,
                };
                char::from_u32(code).context("A character reference out of range")?
            }
        };
        out.push(c);
        rest = &rest[end + 1..];
    }
    out.push_str(rest);
    Ok(out)
}

/// The document's root as `xml.etree.ElementTree.fromstring` reads it.
fn parse(text: &str) -> Result<Element> {
    let text = text.strip_prefix('\u{feff}').unwrap_or(text).replace("\r\n", "\n").replace('\r', "\n");
    let mut stack: Vec<Element> = Vec::new();
    let mut root = None;
    let mut at = 0;
    let data = |stack: &mut Vec<Element>, piece: &str| {
        if let Some(top) = stack.last_mut() {
            match top.children.last_mut() {
                Some(last) => last.tail.push_str(piece),
                None => top.text.push_str(piece),
            }
        }
    };
    while at < text.len() {
        let Some(open) = text[at..].find('<').map(|i| at + i) else {
            data(&mut stack, &unescape(&text[at..])?);
            break;
        };
        data(&mut stack, &unescape(&text[at..open])?);
        let rest = &text[open..];
        let skip = |end: &str| rest.find(end).map(|i| open + i + end.len()).context("An unterminated markup declaration");
        if rest.starts_with("<?") {
            at = skip("?>")?;
        } else if rest.starts_with("<!--") {
            at = skip("-->")?;
        } else if let Some(cdata) = rest.strip_prefix("<![CDATA[") {
            let end = cdata.find("]]>").context("An unterminated CDATA section")?;
            data(&mut stack, &cdata[..end]);
            at = open + 9 + end + 3;
        } else if rest.starts_with("<!") {
            at = skip(">")?;
        } else if let Some(name) = rest.strip_prefix("</") {
            let close = name.find('>').context("An unterminated end tag")?;
            let done = stack.pop().context("An end tag without its start")?;
            ensure!(done.tag == name[..close].trim(), "</{}> closes <{}>", name[..close].trim(), done.tag);
            match stack.last_mut() {
                Some(parent) => parent.children.push(done),
                None => root = Some(done),
            }
            at = open + 2 + close + 1;
        } else {
            let close = rest.find('>').context("An unterminated start tag")?;
            let inner = &rest[1..close];
            let empty = inner.ends_with('/');
            let inner = inner.strip_suffix('/').unwrap_or(inner);
            let split = inner.find(|c: char| c.is_ascii_whitespace()).unwrap_or(inner.len());
            let mut element = Element { tag: inner[..split].to_string(), ..Default::default() };
            let mut attributes = inner[split..].trim();
            while !attributes.is_empty() {
                let eq = attributes.find('=').context("An attribute without a value")?;
                let key = attributes[..eq].trim();
                let value = attributes[eq + 1..].trim_start();
                let quote = value.chars().next().filter(|c| *c == '"' || *c == '\'').context("An unquoted attribute")?;
                let end = value[1..].find(quote).context("An unterminated attribute")? + 1;
                let normalized = value[1..end].replace(['\t', '\n'], " ");
                element.attrib.push((key.to_string(), unescape(&normalized)?));
                attributes = value[end + 1..].trim_start();
            }
            if empty {
                match stack.last_mut() {
                    Some(parent) => parent.children.push(element),
                    None => root = Some(element),
                }
            } else {
                stack.push(element);
            }
            at = open + close + 1;
        }
    }
    ensure!(stack.is_empty(), "An element is not closed");
    root.context("No root element")
}

fn escape_text(text: &str) -> String {
    text.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;")
}

fn escape_attribute(text: &str) -> String {
    escape_text(text).replace('"', "&quot;").replace('\r', "&#13;").replace('\n', "&#10;").replace('\t', "&#09;")
}

fn serialize(element: &Element, out: &mut String) {
    out.push('<');
    out.push_str(&element.tag);
    for (key, value) in &element.attrib {
        out.push_str(&format!(" {key}=\"{}\"", escape_attribute(value)));
    }
    if element.text.is_empty() && element.children.is_empty() {
        out.push_str(" />");
    } else {
        out.push('>');
        out.push_str(&escape_text(&element.text));
        for child in &element.children {
            serialize(child, out);
        }
        out.push_str(&format!("</{}>", element.tag));
    }
    out.push_str(&escape_text(&element.tail));
}

/// `ElementTree.tostring(root, encoding="utf-8", xml_declaration=True)`.
fn document(root: &Element) -> Vec<u8> {
    let mut out = String::from("<?xml version='1.0' encoding='utf-8'?>\n");
    serialize(root, &mut out);
    out.into_bytes()
}

/// The slice record with the sequenced plate's prediction, weight, first-course time, filament
/// and course groups.
fn slice_info(template: &[u8], prediction: i64, grams: f64, first_course_seconds: f64, filament_mm: f64, groups: usize) -> Result<Vec<u8>> {
    let mut info = parse(std::str::from_utf8(template)?)?;
    let plate = info.child("plate")?;
    for (key, value) in [("prediction", prediction.to_string()), ("weight", format!("{grams:.2}")),
                         ("first_layer_time", format!("{first_course_seconds:.6}"))] {
        let mut found = None;
        for (n, child) in plate.children.iter().enumerate() {
            if child.tag == "metadata" {
                let name = child.attrib.iter().find(|(k, _)| k == "key").context("A metadata element without a key")?;
                if name.1 == key {
                    found = Some(n);
                }
            }
        }
        plate.children[found.with_context(|| format!("No {key} metadata"))?].set("value", value);
    }
    let filament = plate.child("filament")?;
    filament.set("used_m", format!("{:.2}", filament_mm / 1000.0));
    filament.set("used_g", format!("{grams:.2}"));
    let layers = plate.child("layer_filament_lists")?;
    *layers = Element { tag: layers.tag.clone(), ..Default::default() };
    layers.children.push(Element {
        tag: "layer_filament_list".into(),
        attrib: vec![("filament_list".into(), "0".into()), ("layer_ranges".into(), format!("0 {groups}"))],
        ..Default::default()
    });
    Ok(document(&info))
}

/// The model without its objects and build items, as a print-only archive carries it.
fn print_only_model(data: &[u8]) -> Result<Vec<u8>> {
    let mut model = crate::xml::parse(std::str::from_utf8(data)?)?;
    for tag in ["resources", "build"] {
        let child = model.children.iter_mut().find(|e| e.local() == tag).with_context(|| format!("Model has no {tag}"))?;
        child.attributes.clear();
        child.children.clear();
        child.text.clear();
    }
    model.attributes.retain(|(key, _)| key != "requiredextensions");
    Ok(crate::xml::document(&model))
}

/// The model settings without objects, assemblies or plate instances.
fn print_only_settings(data: &[u8]) -> Result<Vec<u8>> {
    let mut config = crate::xml::parse(std::str::from_utf8(data)?)?;
    config.children.retain(|e| !matches!(e.local(), "object" | "assemble"));
    for plate in config.children.iter_mut().filter(|e| e.local() == "plate") {
        plate.children.retain(|e| e.local() != "model_instance");
    }
    Ok(crate::xml::document(&config))
}

fn editable(name: &str) -> bool {
    name.starts_with("3D/Objects/") || name.starts_with("3D/_rels/")
        || matches!(name, "Metadata/layer_config_ranges.xml" | "Metadata/cut_information.xml")
}

/// Writes the print-only archive for `sequenced` to the new file `output`, from the native
/// slice's archive `template`, the sequencer's report beside `sequenced`, the playback motion
/// time and the first bed course's deposition span. The summary is returned.
pub fn package(template: &Path, sequenced: &Path, output: &Path, motion_seconds: f64, first_course_seconds: f64) -> Result<Json> {
    ensure!(!output.exists() && output != template, "Use a new destination; preserve the reviewed source archive");
    let raw = fs::read(sequenced)?;
    let report = Json::loads(&fs::read_to_string(sequenced.with_extension("json"))?)?;
    ensure!(report.get("sequenced_gcode_sha256") == Some(&Json::Str(crate::sha256_hex(&raw))), "Sequencer report and G-code differ");
    let groups = count(&raw, b"\n; CHANGE_LAYER\n");
    let Some(Json::List(rows)) = report.get("groups") else { bail!("The report has no groups") };
    ensure!(groups == rows.len(), "Missing course group delimiters");
    let Some(Json::Dict(deposition)) = report.get("deposition_mm_filament") else { bail!("The report has no filament") };
    let deposition: Vec<f64> = deposition.iter().map(|(_, v)| v.as_f64().context("A filament length is not a number")).collect::<Result<_>>()?;
    let filament_mm = sum(&deposition);
    let diameter = header_number(&raw, "; filament_diameter: ")?;
    let density = header_number(&raw, "; filament_density: ")?;
    let volume_mm3 = PI * (diameter / 2.0).powf(2.0) * filament_mm;
    let grams = density * volume_mm3 / 1000.0;
    let time = duration(motion_seconds);
    let mut gcode = raw;
    for (key, line) in [
        ("; model printing time: ", format!("; model printing time: {time}; total estimated time: {time}")),
        ("; total layer number: ", format!("; total layer number: {groups}")),
        ("; total filament length [mm] : ", format!("; total filament length [mm] : {filament_mm:.2}")),
        // Native Bambu header stores the value in cubic millimeters under this key.
        ("; total filament volume [cm^3] : ", format!("; total filament volume [cm^3] : {volume_mm3:.2}")),
        ("; total filament weight [g] : ", format!("; total filament weight [g] : {grams:.2}")),
    ] {
        gcode = replace_line(&gcode, key, &line)?;
    }
    // Retain stock UI progress events at startup with the sequenced motion estimate.
    let gcode = startup_progress(&gcode, (motion_seconds / 60.0).ceil() as i64)?;

    let mut archive = zip::ZipArchive::new(fs::File::open(template).with_context(|| format!("opening {}", template.display()))?)?;
    let mut writer = zip::ZipWriter::new(fs::OpenOptions::new().write(true).create_new(true).open(output)?);
    let options = zip::write::SimpleFileOptions::default().compression_method(zip::CompressionMethod::Deflated).compression_level(Some(6));
    for i in 0..archive.len() {
        let mut entry = archive.by_index(i)?;
        let name = entry.name()?.to_string();
        if name.starts_with("Metadata/hsm_") || editable(&name) {
            continue;
        }
        let mut data = Vec::new();
        entry.read_to_end(&mut data)?;
        let data = match name.as_str() {
            GCODE => gcode.clone(),
            n if n == format!("{GCODE}.md5") => crate::ids::md5_hex(&gcode).into_bytes(),
            SLICE => slice_info(&data, motion_seconds.ceil() as i64, grams, first_course_seconds, filament_mm, groups)?,
            LAYOUT => {
                let mut layout = Json::loads(std::str::from_utf8(&data)?)?;
                layout.set("first_layer_time", Json::Float(first_course_seconds));
                layout.dumps_compact().into_bytes()
            }
            MODEL => print_only_model(&data)?,
            SETTINGS => print_only_settings(&data)?,
            _ => data,
        };
        writer.start_file(name, options)?;
        writer.write_all(&data)?;
    }
    writer.finish()?;
    Ok(Json::Dict(vec![
        ("gcode_sha256".into(), Json::Str(crate::sha256_hex(&gcode))),
        ("gcode_md5".into(), Json::Str(crate::ids::md5_hex(&gcode))),
        ("course_groups".into(), Json::Int(groups as i64)),
        ("deposition_filament_mm".into(), Json::Float(filament_mm)),
        ("deposition_weight_g".into(), Json::Float(grams)),
        ("estimated_motion_seconds".into(), Json::Float(motion_seconds)),
        ("first_bed_course_deposition_span_seconds".into(), Json::Float(first_course_seconds)),
    ]))
}
