//! The Mark1 production identification plate refreshes the solids in the accepted multi-nozzle project.

use anyhow::{Context, Result, ensure};
use hsm_print_prep::faucet::members;
use hsm_print_prep::mesh::bounds;
use hsm_print_prep::profile::relative;
use hsm_print_prep::project::options;
use hsm_print_prep::xml::{self, Element};
use hsm_print_prep::{npz, sha256_hex};
use serde_json::{Map, Value, json};
use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::io::Write as _;
use std::ops::Range;
use std::path::{Path, PathBuf};

const RECIPE: &str = "hardware/printed-parts/enclosure/display-cover/prints/2026-11-08-identification-set-mark1-right-z005";
const MODEL: &str = "3D/3dmodel.model";
const SETTINGS: &str = "Metadata/model_settings.config";
const SOURCES: [(&str, &str); 8] = [
    ("Nameplate unit 0001", "enclosure/nameplate/nameplate-001"),
    ("Status plate", "enclosure/display-cover/status-plate"),
    ("TAP chip", "enclosure/rear-identification/rear-label-water"),
    ("CO2 chip", "enclosure/rear-identification/rear-label-co2"),
    ("SODA chip", "enclosure/rear-identification/rear-label-carb"),
    (
        "FLAVOR A chip",
        "enclosure/rear-identification/rear-label-flavor-a",
    ),
    (
        "DRAIN chip",
        "enclosure/rear-identification/rear-label-drain",
    ),
    (
        "FLAVOR B chip",
        "enclosure/rear-identification/rear-label-flavor-b",
    ),
];

fn metadata<'a>(node: &'a Element, key: &str) -> Result<&'a str> {
    node.children_named("metadata")
        .find(|child| child.attribute("key") == Some(key))
        .and_then(|child| child.attribute("value"))
        .with_context(|| format!("missing {key} on <{}>", node.name))
}

fn mesh_range(model: &str, id: &str) -> Result<Range<usize>> {
    let prefix = format!("<object id=\"{id}\" type=\"model\">");
    let start = model
        .find(&prefix)
        .with_context(|| format!("mesh resource {id}"))?
        + prefix.len();
    let rest = model[start..]
        .strip_prefix("<mesh>")
        .context("mesh opening tag")?;
    let end = rest.find("</mesh>").context("mesh closing tag")?;
    Ok(start..start + "<mesh>".len() + end + "</mesh>".len())
}

fn bed_center(mesh: &str) -> Result<[f64; 2]> {
    let vertices = mesh
        .split_once("</vertices>")
        .context("template vertices")?
        .0;
    let vertices = xml::parse(&format!("{vertices}</vertices></mesh>"))?;
    let vertices = vertices.child("vertices").context("template vertices")?;
    let mut points = Vec::with_capacity(vertices.children.len());
    for vertex in vertices.children_named("vertex") {
        points.push([
            vertex.attribute("x").context("template X")?.parse()?,
            vertex.attribute("y").context("template Y")?.parse()?,
            0.0,
        ]);
    }
    ensure!(!points.is_empty(), "template mesh has no vertices");
    let (low, high) = bounds(&points);
    Ok([(low[0] + high[0]) / 2.0, (low[1] + high[1]) / 2.0])
}

fn mesh_xml(vertices: &[[f64; 3]], faces: &[usize]) -> Result<String> {
    let mut out = String::from("<mesh><vertices>");
    for [x, y, z] in vertices {
        write!(out, "<vertex x=\"{x:.9}\" y=\"{y:.9}\" z=\"{z:.9}\" />")?;
    }
    out.push_str("</vertices><triangles>");
    for face in faces.chunks_exact(3) {
        write!(
            out,
            "<triangle v1=\"{}\" v2=\"{}\" v3=\"{}\" />",
            face[0], face[1], face[2]
        )?;
    }
    out.push_str("</triangles></mesh>");
    Ok(out)
}

pub(super) fn prepare(root: &Path, output: &Path) -> Result<PathBuf> {
    let recipe = root.join(RECIPE);
    let template = recipe.join("HSM-identification-set-Mark1-right-z005.3mf");
    let template_sha = super::file_sha(&template)?;
    let review = recipe.join("review.json");
    let trim = hsm_print_prep::faucet::read_json(&review)?;
    let right = trim["z_trim_mm"]["right_white_blue_red_clear"]
        .as_f64()
        .context("accepted right trim")?;
    let mut archive = members(&template)?;
    let mut model = String::from_utf8(archive.remove(MODEL).context(MODEL)?)?;
    let config = xml::parse(std::str::from_utf8(
        archive.get(SETTINGS).context(SETTINGS)?,
    )?)?;
    let settings: Value = serde_json::from_slice(
        archive
            .get("Metadata/project_settings.config")
            .context("accepted project settings")?,
    )?;
    let plate = config.child("plate").context("accepted project plate")?;
    let instances: BTreeMap<_, _> = plate
        .children_named("model_instance")
        .map(|instance| -> Result<_> {
            Ok((
                metadata(instance, "object_id")?,
                metadata(instance, "identify_id")?.parse::<i64>()?,
            ))
        })
        .collect::<Result<_>>()?;
    let mut updates = Vec::new();
    let mut parts = Vec::new();
    let mut top_heights = Vec::new();
    let mut fingerprint = template_sha.clone();
    for (name, source) in SOURCES {
        let object = config
            .children_named("object")
            .find(|object| metadata(object, "name").ok() == Some(name))
            .with_context(|| format!("template object {name}"))?;
        let instance = instances
            .get(object.attribute("id").context("template object ID")?)
            .context("template instance ID")?;
        let step = root
            .join("hardware/printed-parts")
            .join(format!("{source}.step"));
        let payload = PathBuf::from(format!("{}.npz", step.display()));
        let arrays = npz::read_arrays(&payload)?;
        let names: Vec<String> = serde_json::from_slice(
            arrays
                .get("names")
                .and_then(npz::Array::bytes)
                .context("solid names")?,
        )?;
        let model_sha = super::file_sha(&payload)?;
        fingerprint.push_str(&model_sha);
        let status = name == "Status plate";
        let mut at = None;
        let mut shift = [0.0; 3];
        let mut solids = Map::new();
        for (index, part) in object.children_named("part").enumerate() {
            let solid = metadata(part, "name")?;
            let array_index = names
                .iter()
                .position(|s| s == solid)
                .with_context(|| format!("{} lacks {solid}", payload.display()))?;
            let range = mesh_range(&model, part.attribute("id").context("template mesh ID")?)?;
            let flat = arrays
                .get(&format!("V{array_index}"))
                .and_then(npz::Array::f64)
                .context("vertices")?;
            let faces = arrays
                .get(&format!("T{array_index}"))
                .and_then(npz::Array::indices)
                .context("triangles")?;
            let mut vertices: Vec<[f64; 3]> = flat
                .chunks_exact(3)
                .map(|p| {
                    if status {
                        [p[0], p[1], p[2]]
                    } else {
                        [-p[0], p[2], p[1]]
                    }
                })
                .collect();
            ensure!(
                !vertices.is_empty() && !faces.is_empty(),
                "{solid} has no mesh"
            );
            if index == 0 {
                let center = bed_center(&model[range.clone()])?;
                let (low, high) = bounds(&vertices);
                shift = [
                    center[0] - (low[0] + high[0]) / 2.0,
                    center[1] - (low[1] + high[1]) / 2.0,
                    -low[2],
                ];
                at = Some(center);
            }
            for point in &mut vertices {
                for axis in 0..3 {
                    point[axis] += shift[axis];
                }
            }
            let (low, high) = bounds(&vertices);
            top_heights.push(super::round(high[2], 4));
            solids.insert(
                solid.into(),
                json!({
                    "filament": metadata(part, "extruder")?.parse::<usize>()?,
                    "bounds_mm": [low, high], "facets": faces.len() / 3,
                }),
            );
            updates.push((range, mesh_xml(&vertices, &faces)?));
        }
        ensure!(
            solids.len() == names.len(),
            "production solids changed for {name}"
        );
        parts.push(json!({
            "part": name, "step": relative(&step, root), "step_sha256": super::file_sha(&step)?,
            "model": relative(&payload, root), "model_sha256": model_sha, "identify_id": instance,
            "plate_center_xy_mm": at.context("body mesh")?, "meshes": solids,
        }));
    }
    updates.sort_by_key(|(range, _)| range.start);
    for (range, mesh) in updates.into_iter().rev() {
        model.replace_range(range, &mesh);
    }
    archive.insert(MODEL.into(), model.into_bytes());
    let digest = sha256_hex(fingerprint.as_bytes());
    let stem = format!("{}-identification-mark1-{}", super::today()?, &digest[..8]);
    std::fs::create_dir_all(output)?;
    let directory = output.canonicalize()?.join(&stem);
    std::fs::create_dir(&directory).with_context(|| format!("creating {}", directory.display()))?;
    let project = directory.join(format!("{stem}.3mf"));
    let mut writer = zip::ZipWriter::new(std::fs::File::create(&project)?);
    for (name, data) in archive {
        writer.start_file(name, options())?;
        writer.write_all(&data)?;
    }
    writer.finish()?;
    top_heights.sort_by(f64::total_cmp);
    top_heights.dedup();
    let record = json!({
        "piece": "identification", "printer": "Mark1",
        "material": "Bambu PETG Basic and clear Bambu PETG Translucent",
        "nozzle": {"left": "0.2 mm, black PETG Basic", "right": "0.2 mm, white, blue, red and clear PETG"},
        "filament_colours": settings["filament_colour"],
        "project": relative(&project, root), "project_sha256": super::file_sha(&project)?,
        "profile": relative(&template, root), "profile_sha256": template_sha, "recipe": relative(&review, root),
        "right_nozzle_trim_mm": right, "face_up_tops_mm": top_heights,
        "usable_plate_mm": [super::USABLE.0, super::USABLE.1], "plate_border_mm": super::BORDER,
        "parts": parts, "prepared_utc": super::now_utc()?, "sliced": false, "submitted": false,
    });
    std::fs::write(
        directory.join("preparation.json"),
        serde_json::to_string_pretty(&record)? + "\n",
    )?;
    println!("{}", relative(&project, root));
    Ok(directory)
}

/// Every filament start applies its side's trim, and every end resets the trim before a tool change.
pub(super) fn trim_matches(gcode: &[u8], right: f64) -> bool {
    let text = String::from_utf8_lossy(gcode);
    let mut lines = text.lines().map(str::trim);
    let mut tool = 0;
    let mut seen = BTreeSet::new();
    let mut active = false;
    while let Some(line) = lines.next() {
        let command = line.split_ascii_whitespace().next().unwrap_or("");
        if let Some(next) = command
            .strip_prefix('T')
            .and_then(|n| n.parse::<usize>().ok())
            .filter(|&n| n < 5)
        {
            if active {
                return false;
            }
            tool = next;
        }
        let start = line == "; filament start gcode";
        if start || line == "; filament end gcode" {
            if start == active || lines.next() != Some("M400") {
                return false;
            }
            let expected = if start && tool != 0 { right } else { 0.0 };
            let trim = lines
                .next()
                .and_then(|v| v.strip_prefix("G29.1 Z"))
                .and_then(|v| v.parse::<f64>().ok());
            if trim.is_none_or(|value| (value - expected).abs() >= 0.005) {
                return false;
            }
            active = start;
            if start {
                seen.insert(tool);
            }
        }
    }
    !active && seen.len() == 5
}
