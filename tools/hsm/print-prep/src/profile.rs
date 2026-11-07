//! A printer recipe taken from a saved Bambu Studio project: its settings and filament presets,
//! with a user Z trim, another project's filament and the localized PET-GF cooling applied.

use crate::json::Json;
use anyhow::{bail, Context, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::io::Read;
use std::path::{Path, PathBuf};

pub const SETTINGS_MEMBER: &str = "Metadata/project_settings.config";
pub const PRESETS: &str = "/Applications/BambuStudio.app/Contents/Resources/profiles/BBL";
const PRESET_METADATA: [&str; 16] = [
    "type", "name", "inherits", "include", "from", "setting_id", "instantiation", "description",
    "alias", "filament_id", "version", "rename", "compatible_printers",
    "compatible_printers_condition", "compatible_prints", "compatible_prints_condition",
];

pub struct Profile {
    /// The settings member and the filament presets, as the project carries them.
    pub members: BTreeMap<String, Vec<u8>>,
    pub settings: Json,
    /// What moved from the saved project, for the preparation record.
    pub changes: serde_json::Map<String, Value>,
    pub cooling_member_changes: Value,
    pub original_payload: Vec<u8>,
    pub usable_low: [f64; 2],
    pub usable_high: [f64; 2],
    pub printable_area_extruders: Vec<usize>,
    pub source: PathBuf,
}

/// The command Bambu Studio runs on a sliced plate's G-code: the cooling stage.
pub fn cooling_hook(root: &Path) -> String {
    root.join("tools/hsm/target/release/petgf-cooling").display().to_string()
}

fn read_members(path: &Path) -> Result<BTreeMap<String, Vec<u8>>> {
    let file = std::fs::File::open(path).with_context(|| format!("opening {}", path.display()))?;
    let mut archive = zip::ZipArchive::new(file)?;
    let mut members = BTreeMap::new();
    for i in 0..archive.len() {
        let mut entry = archive.by_index(i)?;
        let name = entry.name()?.to_string();
        let mut data = Vec::new();
        entry.read_to_end(&mut data).with_context(|| format!("{} has a damaged member", path.display()))?;
        members.insert(name, data);
    }
    Ok(members)
}

fn filament_member(name: &str) -> bool {
    name.starts_with("Metadata/filament_settings_") && name.ends_with(".config")
}

/// Every setting Bambu's filament presets define, through the named preset's parents.
pub fn filament_keys(name: &str) -> Result<BTreeSet<String>> {
    let path = Path::new(PRESETS).join("filament").join(format!("{name}.json"));
    let data: Value = serde_json::from_slice(&std::fs::read(&path).with_context(|| format!("reading {}", path.display()))?)?;
    let map = data.as_object().context("a filament preset that is not an object")?;
    let mut keys: BTreeSet<String> = map.keys().filter(|k| !PRESET_METADATA.contains(&k.as_str())).cloned().collect();
    let mut parents: Vec<String> = Vec::new();
    if let Some(p) = map.get("inherits").and_then(Value::as_str).filter(|p| !p.is_empty()) {
        parents.push(p.to_string());
    }
    if let Some(list) = map.get("include").and_then(Value::as_array) {
        parents.extend(list.iter().filter_map(Value::as_str).map(String::from));
    }
    for parent in parents {
        keys.extend(filament_keys(&parent)?);
    }
    Ok(keys)
}

/// Another saved project's filament block over this project's printer and process.
fn take_filament(settings: &mut Json, from: &Path, root: &Path) -> Result<(BTreeMap<String, Vec<u8>>, Value)> {
    let theirs_members = read_members(from)?;
    let theirs = Json::parse(std::str::from_utf8(theirs_members.get(SETTINGS_MEMBER).context("no project settings")?)?)?;
    let named = theirs.first_text("filament_settings_id").context("no filament named")?.to_string();
    let mut current = BTreeMap::new();
    let mut system = None;
    let mut preset_keys = BTreeSet::new();
    for (member, data) in &theirs_members {
        if !filament_member(member) {
            continue;
        }
        let preset = Json::parse(std::str::from_utf8(data)?)?;
        if preset.get("name").and_then(Json::text) == Some(named.as_str()) {
            if system.is_none() {
                system = preset.get("inherits").and_then(Json::text).filter(|s| !s.is_empty()).map(String::from);
            }
            if let Json::Map(entries) = &preset {
                preset_keys.extend(entries.iter().map(|(k, _)| k.clone()));
            }
            current.insert(member.clone(), data.clone());
        }
    }
    let system = system.unwrap_or_else(|| named.clone());
    let mut keys = filament_keys(&system)?;
    keys.extend(preset_keys.into_iter().filter(|k| !PRESET_METADATA.contains(&k.as_str())));
    keys.insert("filament_self_index".into());
    let mut moved = Vec::new();
    for key in &keys {
        if let Some(value) = theirs.get(key) {
            if settings.get(key) != Some(value) {
                moved.push(key.clone());
            }
        }
    }
    for key in &moved {
        settings.set(key, theirs.get(key).unwrap().clone());
    }
    for group in ["inherits_group", "different_settings_to_system"] {
        if let (Some(Json::List(t)), Some(Json::List(s))) = (theirs.get(group), settings.get(group)) {
            if t.len() == s.len() && !s.is_empty() {
                // Python's settings[:1] + theirs[1:-1] + settings[-1:], one-item lists included.
                let mut merged = vec![s[0].clone()];
                merged.extend(t.get(1..t.len().saturating_sub(1)).unwrap_or(&[]).iter().cloned());
                merged.push(s[s.len() - 1].clone());
                settings.set(group, Json::List(merged));
            }
        }
    }
    let bytes = std::fs::read(from)?;
    let record = json!({
        "project": relative(from, root),
        "sha256": crate::sha256_hex(&bytes),
        "filament": named, "system_preset": system, "keys": moved,
    });
    Ok((current, record))
}

pub fn relative(path: &Path, root: &Path) -> String {
    let path = path.canonicalize().unwrap_or_else(|_| path.to_path_buf());
    path.strip_prefix(root).map(|p| p.display().to_string()).unwrap_or_else(|_| path.display().to_string())
}

/// The plate-compensation block with the user's Z trim, as the Python preparers wrote it.
fn trim_block(z: f64) -> String {
    let z = format!("{z:.2}");
    [
        format!(";===== plate compensation plus user-calibrated +{z} mm Z trim ====="),
        "{if curr_bed_type==\"Textured PEI Plate\"}".to_string(),
        "    {if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}".to_string(),
        format!("        G29.1 Z{{{z} - 0.01}}"),
        "    {else}".to_string(),
        format!("        G29.1 Z{{{z} - 0.02}}"),
        "    {endif}".to_string(),
        "{else}".to_string(),
        "    {if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}".to_string(),
        format!("        G29.1 Z{{{z} + 0.01}}"),
        "    {else}".to_string(),
        format!("        G29.1 Z{{{z}}}"),
        "    {endif}".to_string(),
        "{endif}".to_string(),
    ]
    .join("\n")
}

fn points(text: &str) -> Result<Vec<[f64; 2]>> {
    text.split(',')
        .map(|p| {
            let (x, y) = p.split_once('x').context("an area point without an x")?;
            Ok([x.trim().parse()?, y.trim().parse()?])
        })
        .collect()
}

/// Load a saved project's recipe. `filament_from` takes another project's filament block;
/// `z_trim` replaces the start G-code's plate compensation; the cooling stage's hook is the
/// command Bambu Studio runs on each sliced plate.
pub fn load(settings_from: &Path, z_trim: Option<f64>, filament_from: Option<&Path>, root: &Path) -> Result<Profile> {
    let source_members = read_members(settings_from)?;
    let original = source_members.get(SETTINGS_MEMBER).context("the project has no settings member")?.clone();
    let mut settings = Json::parse(std::str::from_utf8(&original)?)?;
    let mut payload = original.clone();
    let mut changes = serde_json::Map::new();
    let mut filament_members = None;
    if let Some(from) = filament_from {
        let (members, record) = take_filament(&mut settings, from, root)?;
        filament_members = Some(members);
        changes.insert("filament_from".into(), record);
        payload = (settings.dumps() + "\n").into_bytes();
    }
    if let Some(z) = z_trim {
        if !z.is_finite() {
            bail!("Z trim must be a finite millimetre value");
        }
        let start = settings.get("machine_start_gcode").and_then(Json::text).context("no start G-code")?.to_string();
        let at = ["\n;===== for Textured PEI Plate", "\n;===== plate compensation plus user-calibrated"]
            .iter()
            .filter_map(|m| start.find(m).map(|i| i + 1))
            .min()
            .or_else(|| (start.starts_with(";===== for Textured PEI Plate") || start.starts_with(";===== plate compensation plus user-calibrated")).then_some(0))
            .context("The profile has no recognized plate-compensation block")?;
        let end = at + start[at..].find("\nG150.1").context("no G150.1 after the plate compensation")?;
        let trimmed = format!("{}{}{}", &start[..at], trim_block(z), &start[end..]);
        let nozzle: f64 = settings.first_text("nozzle_diameter").context("no nozzle diameter")?.parse()?;
        let identity = format!("Bambu Lab H2C {} Standard +{:.2} Z trim", crate::json::python_number(nozzle).trim_end_matches(".0"), z);
        changes.insert("machine_start_gcode".into(), json!({
            "from_sha256": crate::sha256_hex(start.as_bytes()),
            "to_sha256": crate::sha256_hex(trimmed.as_bytes()),
            "requested_z_trim_mm": z,
        }));
        let printer = settings.get("printer_settings_id").cloned().unwrap_or(Json::Null).to_value();
        changes.insert("printer_settings_id".into(), json!({"from": printer, "to": identity}));
        settings.set("machine_start_gcode", Json::Text(trimmed));
        settings.set("printer_settings_id", Json::Text(identity.clone()));
        // The slicer refuses a process whose compatible printers do not name the printer.
        if let Some(Json::List(compatible)) = settings.get("print_compatible_printers").cloned() {
            if !compatible.iter().any(|c| c.text() == Some(identity.as_str())) {
                let mut more = compatible.clone();
                more.push(Json::Text(identity.clone()));
                changes.insert("print_compatible_printers".into(), json!({
                    "from": Json::List(compatible).to_value(), "to": Json::List(more.clone()).to_value()}));
                settings.set("print_compatible_printers", Json::List(more));
            }
        }
        payload = (settings.dumps() + "\n").into_bytes();
    }
    let areas: Vec<Vec<[f64; 2]>> = settings.get("extruder_printable_area").map(Json::list).unwrap_or(&[])
        .iter().filter_map(Json::text).map(points).collect::<Result<_>>()?;
    let mut used: Vec<usize> = settings.get("filament_nozzle_map").map(Json::list).unwrap_or(&[])
        .iter()
        .filter_map(|v| match v { Json::Text(s) => s.parse().ok(), Json::Number(_, n) => Some(*n as usize), _ => None })
        .filter(|&n| n < areas.len())
        .collect::<BTreeSet<usize>>().into_iter().collect();
    let chosen: Vec<&Vec<[f64; 2]>> = if used.is_empty() { areas.iter().collect() } else { used.iter().map(|&i| &areas[i]).collect() };
    let bed = points(&settings.get("printable_area").map(Json::list).unwrap_or(&[]).iter().filter_map(Json::text).collect::<Vec<_>>().join(","))?;
    let (mut low, mut high) = ([f64::NEG_INFINITY; 2], [f64::INFINITY; 2]);
    if chosen.is_empty() {
        for p in &bed {
            for i in 0..2 {
                low[i] = if low[i] == f64::NEG_INFINITY { p[i] } else { low[i].min(p[i]) };
                high[i] = if high[i] == f64::INFINITY { p[i] } else { high[i].max(p[i]) };
            }
        }
    } else {
        for area in &chosen {
            for i in 0..2 {
                low[i] = low[i].max(area.iter().map(|p| p[i]).fold(f64::INFINITY, f64::min));
                high[i] = high[i].min(area.iter().map(|p| p[i]).fold(f64::NEG_INFINITY, f64::max));
            }
        }
    }
    if used.is_empty() {
        used = (0..areas.len()).collect();
    }
    let mut members = BTreeMap::new();
    members.insert(SETTINGS_MEMBER.to_string(), payload);
    match filament_members {
        Some(f) => members.extend(f),
        None => members.extend(source_members.iter().filter(|(n, _)| filament_member(n)).map(|(n, d)| (n.clone(), d.clone()))),
    }
    let hook = cooling_hook(root);
    let cooling = crate::cooling::apply_members(&mut members, &hook)?;
    if let Some(Value::Object(project)) = cooling.get(SETTINGS_MEMBER) {
        for (k, v) in project {
            changes.insert(k.clone(), v.clone());
        }
    }
    let settings = Json::parse(std::str::from_utf8(&members[SETTINGS_MEMBER])?)?;
    Ok(Profile {
        members, settings, changes, cooling_member_changes: cooling, original_payload: original,
        usable_low: low, usable_high: high, printable_area_extruders: used,
        source: settings_from.to_path_buf(),
    })
}
