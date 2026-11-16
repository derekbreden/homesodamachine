//! A printer recipe taken from a saved Bambu Studio project: its settings and filament presets,
//! with a user Z trim, another project's filament and the localized PET-GF cooling applied.

use anyhow::{bail, Context, Result};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::io::Read;
use std::path::{Path, PathBuf};

pub const SETTINGS_MEMBER: &str = "Metadata/project_settings.config";
pub const PRESETS: &str = "/Applications/BambuStudio.app/Contents/Resources/profiles/BBL";
pub const PETGF_SUPPORT_KEYS: [&str; 6] = [
    "support_top_z_distance", "support_interface_top_layers", "support_interface_spacing",
    "bridge_flow", "bridge_speed", "filament_bridge_speed",
];
const PETGF_PROFILE: &str = "hardware/printed-parts/petgf.3mf";
const PRESET_METADATA: [&str; 16] = [
    "type", "name", "inherits", "include", "from", "setting_id", "instantiation", "description",
    "alias", "filament_id", "version", "rename", "compatible_printers",
    "compatible_printers_condition", "compatible_prints", "compatible_prints_condition",
];

/// A settings document as a project's member carries it: indented JSON and a closing newline.
pub fn settings_bytes(settings: &Value) -> Result<Vec<u8>> {
    let mut bytes = serde_json::to_vec_pretty(settings)?;
    bytes.push(b'\n');
    Ok(bytes)
}

/// A setting's text, or its first entry's when it holds one per extruder or filament.
pub fn first_text<'a>(settings: &'a Value, key: &str) -> Option<&'a str> {
    settings[key].as_str().or_else(|| settings[key][0].as_str())
}

pub struct Profile {
    /// The settings member and the filament presets, as the project carries them.
    pub members: BTreeMap<String, Vec<u8>>,
    pub settings: Value,
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

/// The shared PET-GF pattern for ordinary sparse infill in an accepted print recipe.
pub fn petgf_infill_pattern(root: &Path) -> Result<String> {
    let members = read_members(&root.join(PETGF_PROFILE))?;
    let payload = members.get(SETTINGS_MEMBER).context("no shared PET-GF settings")?;
    let settings: Value = serde_json::from_slice(payload)?;
    Ok(first_text(&settings, "sparse_infill_pattern").context("no shared PET-GF infill pattern")?.to_string())
}

/// Current PET-GF contact and bridge defaults, including when a preparer takes its other
/// settings from an accepted print. Part-specific support geometry and later trial overrides
/// remain the preparer's responsibility.
pub fn apply_petgf_support(members: &mut BTreeMap<String, Vec<u8>>, root: &Path) -> Result<Value> {
    let is_petgf = |settings: &Value| {
        let identity = settings.get("filament_settings_id").or_else(|| settings.get("name"));
        let matches = |name: &str| {
            let name = name.to_lowercase();
            name.contains("pet-gf") || name.contains("petgf")
        };
        match identity {
            Some(Value::String(name)) => matches(name),
            Some(Value::Array(names)) => names.iter().filter_map(Value::as_str).any(matches),
            _ => false,
        }
    };
    let settings: Value = serde_json::from_slice(members.get(SETTINGS_MEMBER).context("no project settings")?)?;
    if !is_petgf(&settings) {
        return Ok(Value::Null);
    }
    let source = root.join(PETGF_PROFILE);
    let shared = read_members(&source)?;
    let recipe: Value = serde_json::from_slice(shared.get(SETTINGS_MEMBER).context("no shared PET-GF settings")?)?;
    let mut changed_members = serde_json::Map::new();
    for (name, bytes) in members.iter_mut() {
        if name != SETTINGS_MEMBER && !filament_member(name) {
            continue;
        }
        let mut settings: Value = serde_json::from_slice(bytes)?;
        if !is_petgf(&settings) {
            continue;
        }
        let mut changes = serde_json::Map::new();
        for key in PETGF_SUPPORT_KEYS {
            if name != SETTINGS_MEMBER && key != "filament_bridge_speed" {
                continue;
            }
            let value = recipe.get(key).with_context(|| format!("shared PET-GF profile has no {key}"))?;
            let value = match (settings.get(key), value) {
                (Some(Value::Array(current)), Value::Array(values)) if !values.is_empty() =>
                    Value::Array(vec![values[0].clone(); current.len()]),
                _ => value.clone(),
            };
            let old = settings[key].clone();
            if old != value {
                changes.insert(key.to_string(), json!({"from": old, "to": value}));
                settings[key] = value;
            }
        }
        if !changes.is_empty() {
            *bytes = settings_bytes(&settings)?;
            changed_members.insert(name.clone(), Value::Object(changes));
        }
    }
    Ok(json!({"profile": PETGF_PROFILE, "sha256": crate::sha256_hex(&std::fs::read(source)?), "members": changed_members}))
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
fn take_filament(settings: &mut Value, from: &Path, root: &Path) -> Result<(BTreeMap<String, Vec<u8>>, Value)> {
    let theirs_members = read_members(from)?;
    let theirs: Value = serde_json::from_slice(theirs_members.get(SETTINGS_MEMBER).context("no project settings")?)?;
    let named = first_text(&theirs, "filament_settings_id").context("no filament named")?.to_string();
    let mut current = BTreeMap::new();
    let mut system = None;
    let mut preset_keys = BTreeSet::new();
    for (member, data) in &theirs_members {
        if !filament_member(member) {
            continue;
        }
        let preset: Value = serde_json::from_slice(data)?;
        if preset["name"].as_str() == Some(named.as_str()) {
            if system.is_none() {
                system = preset["inherits"].as_str().filter(|s| !s.is_empty()).map(String::from);
            }
            if let Some(entries) = preset.as_object() {
                preset_keys.extend(entries.keys().cloned());
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
        settings[key.as_str()] = theirs[key.as_str()].clone();
    }
    // Each group lists the process first, the filaments, then the printer: their filaments
    // between this project's process and printer.
    for group in ["inherits_group", "different_settings_to_system"] {
        let (Some(Value::Array(t)), Some(Value::Array(mut merged))) = (theirs.get(group), settings.get(group).cloned()) else { continue };
        if t.len() == merged.len() && t.len() > 2 {
            let filaments = 1..t.len() - 1;
            merged[filaments.clone()].clone_from_slice(&t[filaments]);
            settings[group] = Value::Array(merged);
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

/// The print setup that owns each printer's PET-GF settings.
pub const PETGF_SETUP: &str = "hardware/printed-parts/enclosure/trial-preparation/pieces.json";

/// A printer's user Z trim for PET-GF on Textured PEI through its 0.4 mm nozzle, in millimetres,
/// as the print setup gives it.
pub fn petgf_z_trim(root: &Path, printer: &str) -> Result<f64> {
    let setup: Value = serde_json::from_slice(&std::fs::read(root.join(PETGF_SETUP)).with_context(|| format!("reading {PETGF_SETUP}"))?)?;
    setup["printers"][printer]["z_trim_mm"].as_f64().with_context(|| format!("{PETGF_SETUP} gives no Z trim for printer {printer}"))
}

/// The plate-compensation block with the user's Z trim. Its header line is how
/// `trimmed_start_gcode` finds the block in a start G-code it has already trimmed.
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

/// Where `start`'s plate-compensation block, stock or trimmed, begins and ends.
fn compensation_span(start: &str) -> Result<(usize, usize)> {
    let at = ["\n;===== for Textured PEI Plate", "\n;===== plate compensation plus user-calibrated"]
        .iter()
        .filter_map(|m| start.find(m).map(|i| i + 1))
        .min()
        .or_else(|| (start.starts_with(";===== for Textured PEI Plate") || start.starts_with(";===== plate compensation plus user-calibrated")).then_some(0))
        .context("The profile has no recognized plate-compensation block")?;
    let end = at + start[at..].find("\nG150.1").context("no G150.1 after the plate compensation")?;
    Ok((at, end))
}

/// `start` with its plate compensation, stock or already trimmed, replaced by the block that
/// adds the user's Z trim `z`.
pub fn trimmed_start_gcode(start: &str, z: f64) -> Result<String> {
    let (at, end) = compensation_span(start)?;
    Ok(format!("{}{}{}", &start[..at], trim_block(z), &start[end..]))
}

/// The plate the PET-GF Z trim belongs to.
pub const TEXTURED_PEI: &str = "Textured PEI Plate";

/// The glued plate PET-GF also prints on, with a Z trim of its own.
pub const ENGINEERING_PLATE: &str = "Engineering Plate";

/// A printer's user Z trim for PET-GF through its 0.4 mm nozzle on `bed`, in millimetres, as the
/// print setup gives it: the Textured PEI trim, or the Engineering Plate's.
pub fn petgf_bed_z_trim(root: &Path, printer: &str, bed: &str) -> Result<f64> {
    let key = match bed {
        TEXTURED_PEI => "z_trim_mm",
        ENGINEERING_PLATE => "engineering_plate_z_trim_mm",
        other => bail!("{PETGF_SETUP} gives no PET-GF Z trim for the {other}"),
    };
    let setup: Value = serde_json::from_slice(&std::fs::read(root.join(PETGF_SETUP)).with_context(|| format!("reading {PETGF_SETUP}"))?)?;
    setup["printers"][printer][key].as_f64().with_context(|| format!("{PETGF_SETUP} gives no {bed} Z trim for printer {printer}"))
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
    let mut settings: Value = serde_json::from_slice(&original)?;
    let mut payload = original.clone();
    let mut changes = serde_json::Map::new();
    let mut filament_members = None;
    if let Some(from) = filament_from {
        let (members, record) = take_filament(&mut settings, from, root)?;
        filament_members = Some(members);
        changes.insert("filament_from".into(), record);
        payload = settings_bytes(&settings)?;
    }
    if let Some(z) = z_trim {
        if !z.is_finite() {
            bail!("Z trim must be a finite millimetre value");
        }
        let start = settings["machine_start_gcode"].as_str().context("no start G-code")?.to_string();
        let trimmed = trimmed_start_gcode(&start, z)?;
        let nozzle: f64 = first_text(&settings, "nozzle_diameter").context("no nozzle diameter")?.parse()?;
        let identity = format!("Bambu Lab H2C {nozzle} Standard +{z:.2} Z trim");
        changes.insert("machine_start_gcode".into(), json!({
            "from_sha256": crate::sha256_hex(start.as_bytes()),
            "to_sha256": crate::sha256_hex(trimmed.as_bytes()),
            "requested_z_trim_mm": z,
        }));
        changes.insert("printer_settings_id".into(), json!({"from": settings["printer_settings_id"], "to": identity}));
        settings["machine_start_gcode"] = json!(trimmed);
        settings["printer_settings_id"] = json!(identity);
        // The slicer refuses a process whose compatible printers do not name the printer.
        if let Some(Value::Array(compatible)) = settings.get("print_compatible_printers").cloned() {
            if !compatible.iter().any(|c| c.as_str() == Some(identity.as_str())) {
                let mut more = compatible.clone();
                more.push(json!(identity));
                changes.insert("print_compatible_printers".into(), json!({"from": compatible, "to": more}));
                settings["print_compatible_printers"] = Value::Array(more);
            }
        }
        payload = settings_bytes(&settings)?;
    }
    let areas: Vec<Vec<[f64; 2]>> = settings["extruder_printable_area"].as_array().into_iter().flatten()
        .filter_map(Value::as_str).map(points).collect::<Result<_>>()?;
    let mut used: Vec<usize> = settings["filament_nozzle_map"].as_array().into_iter().flatten()
        .filter_map(|v| match v { Value::String(s) => s.parse().ok(), Value::Number(n) => n.as_f64().map(|n| n as usize), _ => None })
        .filter(|&n| n < areas.len())
        .collect::<BTreeSet<usize>>().into_iter().collect();
    let chosen: Vec<&Vec<[f64; 2]>> = if used.is_empty() { areas.iter().collect() } else { used.iter().map(|&i| &areas[i]).collect() };
    let bed = points(&settings["printable_area"].as_array().into_iter().flatten().filter_map(Value::as_str).collect::<Vec<_>>().join(","))?;
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
    let support = apply_petgf_support(&mut members, root)?;
    if !support.is_null() {
        changes.insert("petgf_support_recipe".into(), support);
    }
    let hook = cooling_hook(root);
    let cooling = crate::cooling::apply_members(&mut members, &hook)?;
    if let Some(Value::Object(project)) = cooling.get(SETTINGS_MEMBER) {
        for (k, v) in project {
            changes.insert(k.clone(), v.clone());
        }
    }
    let settings: Value = serde_json::from_slice(&members[SETTINGS_MEMBER])?;
    Ok(Profile {
        members, settings, changes, cooling_member_changes: cooling, original_payload: original,
        usable_low: low, usable_high: high, printable_area_extruders: used,
        source: settings_from.to_path_buf(),
    })
}
