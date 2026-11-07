//! funnel-mold-print-project — the silicone funnel mold's cavity and core, each on its own plate
//! of a Bambu Studio project composed from the installed system presets and the mold's recipe,
//! and optionally its offline slice. Never contacts a printer.
//!
//!     funnel-mold-print-project --models DIR --output PROJECT.3mf [--z-trim MM] [--label TEXT]
//!         [--nozzle 0.4|0.8] [--only cavity|core] [--settings-from SAVED.3mf] [--slice]
//!
//! `recipes.json` holds each nozzle's recipe, every setting it changes with its reason. Beside
//! the project go its provenance, naming where each setting came from, and the recipe as a
//! preset bundle Bambu Studio imports. `--settings-from` keeps a saved project's settings once
//! they agree with the recipe. `--slice` slices every plate into `native/` beside the project.

use anyhow::{bail, Context, Result};
use hsm_print_prep::json::{python_number, Json};
use hsm_print_prep::mesh::Mesh;
use hsm_print_prep::preset::system_preset;
use hsm_print_prep::profile::{trimmed_start_gcode, PRESETS, SETTINGS_MEMBER};
use hsm_print_prep::project::{self, MeshStyle, Plate, Range};
use hsm_print_prep::{faucet, root, sha256_hex, slice};
use std::collections::BTreeMap;
use std::io::Write;
use std::path::{Path, PathBuf};

const RECIPES: &str = "tools/funnel-mold-print/recipes.json";
/// Bambu Studio's offset between neighbouring plates on the H2C's bed.
const PLATE_STRIDE: f64 = 396.0;
const BED: &str = "Textured PEI Plate";
const PIECES: [&str; 2] = ["cavity", "core"];

fn text(value: &str) -> Json {
    Json::Text(value.into())
}

fn texts<S: AsRef<str>>(values: &[S]) -> Json {
    Json::List(values.iter().map(|v| text(v.as_ref())).collect())
}

fn number(value: f64) -> Json {
    Json::Number(python_number(value), value)
}

fn map(entries: Vec<(&str, Json)>) -> Json {
    Json::Map(entries.into_iter().map(|(k, v)| (k.to_string(), v)).collect())
}

fn entries(value: Option<&Json>) -> &[(String, Json)] {
    match value {
        Some(Json::Map(entries)) => entries,
        _ => &[],
    }
}

fn field<'a>(value: &'a Json, key: &str) -> Result<&'a str> {
    value.get(key).and_then(Json::text).with_context(|| format!("no {key}"))
}

fn float(value: Option<&Json>) -> Option<f64> {
    match value? {
        Json::Number(_, v) => Some(*v),
        Json::Text(s) => s.trim().parse().ok(),
        _ => None,
    }
}

/// A nozzle size as Python's `{:g}` writes it.
fn g(value: f64) -> String {
    python_number(value).trim_end_matches(".0").to_string()
}

fn side(recipe: &Json) -> Result<usize> {
    match field(recipe, "side")? {
        "left" => Ok(0),
        "right" => Ok(1),
        other => bail!("no hotend side {other}"),
    }
}

/// Each hotend's flow type, left first: the recipe's nozzle on its side, Standard opposite.
fn volume_types(recipe: &Json) -> Result<Vec<String>> {
    let mut volumes = vec!["Standard".to_string(); 2];
    volumes[side(recipe)?] = field(recipe, "nozzle_type")?.to_string();
    Ok(volumes)
}

fn nozzle(recipe: &Json) -> Result<f64> {
    float(recipe.get("nozzle_mm")).context("the recipe names no nozzle size")
}

fn printer_name(recipe: &Json, trim: f64) -> Result<String> {
    Ok(format!("Bambu Lab H2C {} {} +{trim:.2} Z trim", g(nozzle(recipe)?), field(recipe, "nozzle_type")?))
}

fn trims(recipe: &Json) -> Vec<f64> {
    recipe.get("z_trim").and_then(|z| z.get("available_mm")).map(Json::list).unwrap_or(&[]).iter().filter_map(|v| float(Some(v))).collect()
}

fn presets(recipe: &Json) -> Result<&Json> {
    recipe.get("system_presets").context("the recipe names no system presets")
}

/// The machine preset itself, then one printer per available Z trim.
fn printer_names(recipe: &Json) -> Result<Vec<String>> {
    let mut names = vec![field(presets(recipe)?, "machine")?.to_string()];
    for trim in trims(recipe) {
        names.push(printer_name(recipe, trim)?);
    }
    Ok(names)
}

/// The recipe over its system presets, with the Z trim in the start G-code, and the provenance
/// of every value.
fn fresh_settings(recipe: &Json, trim: f64) -> Result<(Json, Json)> {
    let (mut values, mut sources, mut files) = (Json::Map(Vec::new()), Json::Map(Vec::new()), Json::Map(Vec::new()));
    let named = presets(recipe)?;
    let mut filament_id = None;
    for (kind, name) in entries(Some(named)) {
        let resolved = system_preset(kind, name.text().context("a preset without a name")?, &mut files)?;
        for (key, value) in entries(Some(&resolved.values)) {
            values.set(key, value.clone());
        }
        for (key, value) in entries(Some(&resolved.sources)) {
            sources.set(key, value.clone());
        }
        if kind == "filament" {
            filament_id = resolved.ids.get("filament_id").cloned();
        }
    }
    for group in ["process_settings", "filament_settings"] {
        for (key, choice) in entries(recipe.get(group)) {
            let reason = choice.get("reason").and_then(Json::text).filter(|r| !r.is_empty()).with_context(|| format!("{key} has no reason"))?;
            values.set(key, choice.get("value").cloned().with_context(|| format!("{key} has no value"))?);
            sources.set(key, map(vec![("recipe", text(group)), ("reason", text(reason))]));
        }
    }
    let lane = side(recipe)?;
    let volumes = volume_types(recipe)?;
    let keys = |group: &str| entries(recipe.get(group)).iter().map(|(k, _)| k.as_str()).collect::<Vec<_>>().join(";");
    let lanes = values.get("filament_extruder_variant").map(|v| v.list().len()).unwrap_or(0);
    let stats: Vec<String> = volumes.iter().map(|v| format!("{v}#1")).collect();
    let assignment = vec![
        ("printer_settings_id", text(&printer_name(recipe, trim)?)),
        ("print_settings_id", text(field(recipe, "process_name")?)),
        ("filament_settings_id", texts(&[field(recipe, "filament_name")?])),
        ("inherits_group", texts(&[field(named, "process")?, field(named, "filament")?, field(named, "machine")?])),
        ("different_settings_to_system", texts(&[keys("process_settings"), keys("filament_settings"),
                                                 "machine_start_gcode;default_nozzle_volume_type;nozzle_volume_type".into()])),
        ("filament_ids", Json::List(vec![filament_id.context("the filament preset has no filament ID")?])),
        ("filament_colour", texts(&["#DDEBF0"])),
        ("filament_map_mode", text("Manual")),
        ("filament_map", texts(&[(lane + 1).to_string()])),
        ("filament_map_2", texts(&[(lane + 1).to_string()])),
        ("filament_nozzle_map", texts(&[lane.to_string()])),
        ("filament_self_index", texts(&vec!["1"; lanes])),
        ("filament_volume_map", texts(&[if field(recipe, "nozzle_type")? == "High Flow" { "1" } else { "0" }])),
        ("nozzle_volume_type", texts(&volumes)),
        ("default_nozzle_volume_type", texts(&volumes)),
        ("extruder_nozzle_stats", texts(&stats)),
        ("extruder_nozzle_stats_new", texts(&stats)),
        ("curr_bed_type", text(BED)),
        ("print_compatible_printers", texts(&printer_names(recipe)?)),
    ];
    let reason = format!("One PETG filament on the {} hotend, textured PEI; named source presets.", field(recipe, "side")?);
    for (key, value) in assignment {
        values.set(key, value);
        sources.set(key, map(vec![("generator", text("fresh_settings")), ("reason", text(&reason))]));
    }
    let start = field(&values, "machine_start_gcode").context("the machine preset has no start G-code")?.to_string();
    values.set("machine_start_gcode", text(&trimmed_start_gcode(&start, trim)?));
    let preset = sources.get("machine_start_gcode").and_then(|s| s.get("preset")).cloned().unwrap_or(Json::Null);
    let trim_reason = recipe.get("z_trim").and_then(|z| z.get("reason")).cloned().unwrap_or(Json::Null);
    sources.set("machine_start_gcode", map(vec![("preset", preset), ("generator", text("trimmed_start_gcode")), ("z_trim_mm", number(trim)),
                                               ("reason", trim_reason)]));
    let mut supplied = Json::Map(Vec::new());
    for (key, value) in entries(Some(&values)) {
        let mut row = vec![("value".to_string(), value.clone())];
        row.extend(entries(sources.get(key)).iter().cloned());
        supplied.set(key, Json::Map(row));
    }
    Ok((values, map(vec![("system_preset_sha256", files), ("supplied_settings", supplied)])))
}

/// Whether a saved setting is the value supplied, as Bambu Studio rewrites a few on saving.
fn equivalent(key: &str, supplied: &Json, effective: &Json) -> bool {
    if supplied == effective {
        return true;
    }
    if key == "extruder_nozzle_stats" || key == "extruder_nozzle_stats_new" {
        let installed = |lanes: &Json| -> Vec<Vec<String>> {
            lanes.list().iter().map(|lane| {
                let mut kept: Vec<String> = lane.text().unwrap_or("").split('|')
                    .filter(|e| e.rsplit_once('#').and_then(|(_, n)| n.parse::<i64>().ok()).is_some_and(|n| n != 0))
                    .map(String::from).collect();
                kept.sort();
                kept
            }).collect()
        };
        return installed(supplied) == installed(effective);
    }
    if key == "best_object_pos" {
        return supplied.text().map(|s| s.replace('x', ",")).as_deref() == effective.text();
    }
    if key == "enable_long_retraction_when_cut" {
        return *supplied == Json::List(vec![effective.clone()]);
    }
    if matches!(key, "top_surface_density" | "bottom_surface_density" | "monotonic_travel_into_wall") {
        let percent = |v: &Json| v.text().and_then(|s| s.trim_end_matches('%').parse::<f64>().ok());
        return percent(supplied).is_some() && percent(supplied) == percent(effective);
    }
    if let (Json::List(a), Json::List(b)) = (supplied, effective) {
        return a.len() == b.len() && a.iter().zip(b).all(|(x, y)| equivalent(key, x, y));
    }
    match (float(Some(supplied)), float(Some(effective))) {
        (Some(a), Some(b)) => (a - b).abs() <= f64::max(1e-9 * f64::max(a.abs(), b.abs()), 1e-9),
        _ => false,
    }
}

/// The centre of the selected hotend's printable area, each plate's model centre.
fn bed_centre(settings: &Json, lane: usize) -> Result<[f64; 2]> {
    let area = settings.get("extruder_printable_area").map(Json::list).and_then(|a| a.get(lane)).and_then(Json::text)
        .context("the printer has no printable area for the hotend")?;
    let (mut lo, mut hi) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
    for point in area.split(',') {
        let (x, y) = point.split_once('x').context("an area point without an x")?;
        for (k, v) in [x, y].into_iter().enumerate() {
            let v: f64 = v.trim().parse()?;
            lo[k] = lo[k].min(v);
            hi[k] = hi[k].max(v);
        }
    }
    Ok([(lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0])
}

/// The installed Bambu Studio's version.
fn slicer_version() -> Result<String> {
    let plist = Path::new(PRESETS).ancestors().nth(3).context("no application folder")?.join("Info.plist");
    let text = std::fs::read_to_string(&plist).with_context(|| format!("reading {}", plist.display()))?;
    let after = text.split_once("<key>CFBundleShortVersionString</key>").context("the application names no version")?.1;
    let value = after.split_once("<string>").and_then(|(_, rest)| rest.split_once("</string>")).context("the application's version is not a string")?.0;
    Ok(value.trim().to_string())
}

/// Every selector's preset, the stock parent named and the recipe's edits on it, as one bundle
/// Bambu Studio imports.
fn preset_bundle(recipe: &Json, version: &str, destination: &Path) -> Result<()> {
    let named = presets(recipe)?;
    let mut scratch = Json::Map(Vec::new());
    let machine = field(named, "machine")?;
    let stock = system_preset("machine", machine, &mut scratch)?;
    let start = field(&stock.values, "machine_start_gcode")?.to_string();
    let mut profiles = Vec::new();
    for offset in trims(recipe) {
        let name = printer_name(recipe, offset)?;
        profiles.push(map(vec![("from", text("User")), ("inherits", text(machine)), ("name", text(&name)), ("printer_settings_id", text(&name)),
                               ("version", text(version)), ("machine_start_gcode", text(&trimmed_start_gcode(&start, offset)?)),
                               ("default_nozzle_volume_type", texts(&volume_types(recipe)?))]));
    }
    for (kind, identity) in [("process", "print_settings_id"), ("filament", "filament_settings_id")] {
        let name = field(recipe, &format!("{kind}_name"))?;
        if name.contains('/') || name.contains('\\') {
            bail!("Preset names must also be valid filenames.");
        }
        let mut profile = map(vec![("from", text("User")), ("inherits", text(field(named, kind)?)), ("name", text(name)), ("version", text(version)),
                                   (identity, if kind == "filament" { texts(&[name]) } else { text(name) })]);
        for (key, choice) in entries(recipe.get(&format!("{kind}_settings"))) {
            profile.set(key, choice.get("value").cloned().unwrap_or(Json::Null));
        }
        if kind == "process" {
            profile.set("compatible_printers", texts(&printer_names(recipe)?));
        } else {
            let ids = system_preset(kind, field(named, kind)?, &mut scratch)?.ids;
            profile.set("filament_id", ids.get("filament_id").cloned().context("the filament preset has no filament ID")?);
        }
        profiles.push(profile);
    }
    let mut archive = zip::ZipWriter::new(std::fs::File::create(destination).with_context(|| format!("writing {}", destination.display()))?);
    for profile in &profiles {
        archive.start_file(format!("{}.json", field(profile, "name")?), project::options())?;
        archive.write_all((profile.dumps() + "\n").as_bytes())?;
    }
    archive.finish()?;
    Ok(())
}

/// Every plate sliced into `native/` beside the project, each plate's estimate printed.
fn slice_project(project: &Path) -> Result<()> {
    let native = project.parent().context("the project has no folder")?.join("native");
    std::fs::create_dir_all(&native)?;
    let name = project.file_name().context("the project has no name")?.to_string_lossy().replace(".3mf", ".gcode.3mf");
    let log = std::fs::File::create(native.join("slice.log"))?;
    let status = std::process::Command::new(slice::SLICER)
        .args(["--slice", "0", "--arrange", "0", "--orient", "0", "--outputdir"]).arg(&native)
        .args(["--export-3mf", &name]).arg(project)
        .current_dir(&native).stdout(log.try_clone()?).stderr(log).status()?;
    let result = if native.join("result.json").is_file() { faucet::read_json(&native.join("result.json"))? } else { serde_json::json!({}) };
    if !status.success() || result["return_code"].as_i64() != Some(0) {
        bail!("slice failed ({}): {}; see {}", status.code().unwrap_or(-1), result["error_string"], native.join("slice.log").display());
    }
    for plate in result["sliced_plates"].as_array().into_iter().flatten() {
        let grams: f64 = plate["filaments"].as_array().into_iter().flatten().filter_map(|f| f["total_used_g"].as_f64()).sum();
        println!("plate {}: {:.1} h, {grams:.0} g", plate["id"], plate["total_predication"].as_f64().unwrap_or(0.0) / 3600.0);
    }
    println!("{}", native.join(&name).display());
    Ok(())
}

fn main() -> Result<()> {
    let root = root();
    let (mut models, mut output, mut z_trim, mut label, mut nozzle_mm, mut only, mut settings_from, mut do_slice) =
        (None::<PathBuf>, None::<PathBuf>, None::<f64>, None::<String>, 0.4, None::<String>, None::<PathBuf>, false);
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        let mut value = || args.next().with_context(|| format!("{arg} needs a value"));
        match arg.as_str() {
            "--models" => models = Some(PathBuf::from(value()?)),
            "--output" => output = Some(PathBuf::from(value()?)),
            "--z-trim" => z_trim = Some(value()?.parse()?),
            "--label" => label = Some(value()?),
            "--nozzle" => nozzle_mm = value()?.parse()?,
            "--only" => only = Some(value()?),
            "--settings-from" => settings_from = Some(PathBuf::from(value()?)),
            "--slice" => do_slice = true,
            _ => bail!("unknown argument {arg}"),
        }
    }
    let models = models.context("--models names the folder holding cavity.stl and core.stl")?;
    let output = output.context("--output names the project to write")?;
    let recipes = Json::parse(&std::fs::read_to_string(root.join(RECIPES))?)?;
    let recipe = recipes.get(&g(nozzle_mm)).with_context(|| format!("no recipe for the {} mm nozzle", g(nozzle_mm)))?;
    let trim = match z_trim {
        Some(t) if trims(recipe).contains(&t) => t,
        Some(t) => bail!("no +{t} mm Z trim; the recipe offers {:?}", trims(recipe)),
        None => float(recipe.get("z_trim").and_then(|z| z.get("default_mm"))).context("the recipe has no default Z trim")?,
    };
    let names: Vec<&str> = match only.as_deref() {
        Some(piece) if PIECES.contains(&piece) => vec![piece],
        Some(piece) => bail!("no piece {piece}; cavity or core"),
        None => PIECES.to_vec(),
    };
    let (mut settings, mut provenance) = fresh_settings(recipe, trim)?;
    if let Some(saved) = &settings_from {
        let members = faucet::members(saved)?;
        let payload = members.get(SETTINGS_MEMBER).context("the saved project has no settings")?;
        let preserved = Json::parse(std::str::from_utf8(payload)?)?;
        for group in ["process_settings", "filament_settings"] {
            for (key, expected) in entries(recipe.get(group)) {
                let have = preserved.get(key).with_context(|| format!("the saved project has no {key}"))?;
                if !equivalent(key, expected.get("value").unwrap_or(&Json::Null), have) {
                    bail!("the saved project's {key} is {}", have.dumps());
                }
            }
        }
        for key in ["printer_settings_id", "print_settings_id", "filament_settings_id", "machine_start_gcode", "curr_bed_type",
                    "nozzle_diameter", "nozzle_volume_type", "filament_volume_map"] {
            let have = preserved.get(key).with_context(|| format!("the saved project has no {key}"))?;
            if !equivalent(key, settings.get(key).unwrap_or(&Json::Null), have) {
                bail!("the saved project's {key} is {}", have.dumps());
            }
        }
        let source = vec![("project", text(&saved.file_name().unwrap_or_default().to_string_lossy())),
                          ("project_sha256", text(&faucet::file_sha(saved)?))];
        let mut record = map(source.clone());
        record.set("settings_sha256", text(&sha256_hex(payload)));
        provenance.set("settings_source", record);
        let mut supplied = Json::Map(Vec::new());
        for (key, value) in entries(Some(&preserved)) {
            let mut row = vec![("value".to_string(), value.clone())];
            row.extend(source.iter().map(|(k, v)| (k.to_string(), v.clone())));
            supplied.set(key, Json::Map(row));
        }
        provenance.set("supplied_settings", supplied);
        settings = preserved;
    }
    let version = slicer_version()?;
    let lane = side(recipe)?;
    let centre = bed_centre(&settings, lane)?;
    let side_map = (lane + 1).to_string();
    if settings.get("filament_map") != Some(&texts(&[&side_map])) {
        bail!("the settings map the filament to {}, not the recipe's hotend", settings.get("filament_map").map(Json::dumps).unwrap_or_default());
    }
    let label = label.unwrap_or_else(|| "Funnel mold".into());
    let mut plate = Plate::with_settings(&label, settings, BTreeMap::new(), "homesodamachine/funnel-mold/");
    plate.mesh_style = MeshStyle::Element;
    plate.application = format!("BambuStudio-{version}");
    plate.filament_maps = Some(side_map);
    plate.filament_map_mode = "Manual".into();
    plate.filament_volume_maps = if field(recipe, "nozzle_type")? == "High Flow" { "1" } else { "0" }.into();
    let mut meshes = Json::Map(Vec::new());
    for (i, name) in names.iter().enumerate() {
        let index = i + 1;
        let path = models.join(format!("{name}.stl"));
        let mesh = Mesh::read_stl(&path)?;
        mesh.check_closed_single_body(&format!("{name}.stl"))?;
        let center = mesh.center();
        let (low, high) = mesh.bounds();
        let local: Vec<[f64; 3]> = mesh.vertices.iter().map(|v| [v[0] - center[0], v[1] - center[1], v[2] - center[2]]).collect();
        // The cavity prints upright; the core prints inverted on its dry back.
        let rotation = if *name == "core" { [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]] } else { [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]] };
        let translation = [centre[0] + i as f64 * PLATE_STRIDE, centre[1], (high[2] - low[2]) / 2.0];
        let at = plate.add_object(&format!("{label} {name}"), local, mesh.faces.clone(), &format!("{name}.stl"), center, rotation, translation,
                                  None, Vec::new());
        plate.objects[at].identify_id = 1800 + index;
        for band in recipe.get("layer_ranges_mm").and_then(|r| r.get(name)).map(Json::list).unwrap_or(&[]) {
            let (Some(bottom), Some(top)) = (float(band.list().first()), float(band.list().get(1))) else { bail!("a layer range needs a bottom and a top") };
            plate.objects[at].ranges.push(Range { min_z: bottom, max_z: top, options: vec![("layer_height".into(), "0.16".into())] });
        }
        meshes.set(name, text(&faucet::file_sha(&path)?));
    }
    plate.plates = names.iter().map(|name| format!("{label} {name}")).collect();
    plate.write(&output)?;
    provenance.set("mesh_sha256", meshes);
    provenance.set("parts", texts(&names));
    provenance.set("recipe", recipe.clone());
    provenance.set("slicer_version", text(&version));
    std::fs::write(output.with_extension("provenance.json"), provenance.dumps() + "\n")?;
    preset_bundle(recipe, &version, &output.parent().unwrap_or(Path::new(".")).join("funnel-mold-presets.bbscfg"))?;
    println!("{}", output.display());
    if do_slice {
        // Bambu Studio's slice is one of the Mac's heavy runs.
        hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
        slice_project(&std::path::absolute(&output)?)?;
    }
    Ok(())
}
