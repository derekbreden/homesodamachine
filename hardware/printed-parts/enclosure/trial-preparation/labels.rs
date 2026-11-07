//! enclosure-labels — the identification plates: rear chips, tube collars and the nameplate.
//!
//!     enclosure-labels [--colour white|blue|red|black]... [--slice] [--output DIR]
//!
//! Two-colour PET-GF plates on Mark2, one per chip colour. They carry the compact rear chips
//! (`enclosure/rear-identification/`), the tube collars (`faucet/tube-collar/`) and the serial
//! nameplate (`enclosure/nameplate/`). Each part's body and lettering are the two solids its
//! generator writes into `<part>.step.npz`, posed face up: the chips and the nameplate lie on
//! their flat backs, the collars on their flat faces.
//!
//! The recipe is `petgf.3mf` on both nozzles with Mark2's Z trim. White PET-GF is on the left
//! nozzle and the plate's colour on the right, which takes its measured registration offset
//! (`calibration/dual-nozzle-registration/mark2-registration.json`). There are no supports and no
//! brim. One closing layer schedule puts a layer top on every face-up face and lettering top,
//! because the prime tower needs one schedule.
//!
//! A run writes `<output>/<date>-labels-<colour>-mark2-<digest>/`: the project, the body and
//! lettering meshes, `preparation.json`, and with `--slice` the archive and `review.json`. No
//! printer is contacted.

use anyhow::{bail, Context, Result};
use hsm_print_prep::json::Json;
use hsm_print_prep::mesh::{bounds, write_stl};
use hsm_print_prep::profile::{self, relative};
use hsm_print_prep::project::{Plate, Range};
use hsm_print_prep::{cooling, derive, gcode, npz, sha256_hex, slice};
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

const PROFILE: &str = "hardware/printed-parts/petgf.3mf";
const REGISTRATION: &str = "hardware/printed-parts/calibration/dual-nozzle-registration/mark2-registration.json";
/// Mark2's Z trim, as `pieces.json` gives it for every Mark2 plate.
const Z_TRIM: f64 = 0.04;
/// The unseasoned outer bed every bead keeps clear of.
const BORDER: f64 = 20.0;
/// Between parts, and between rows.
const GAP: f64 = 8.0;
/// The widest row of parts.
const ROW: f64 = 130.0;
/// The plate both nozzles reach.
const USABLE: ([f64; 2], [f64; 2]) = ([25.0, 0.0], [325.0, 320.0]);
/// The closing schedule's finest layer and its coarsest fine layer.
const FINEST: f64 = 0.08;
const COARSEST_FINE: f64 = 0.16;

struct Group {
    colour: &'static str,
    colours: [&'static str; 2],
    body: usize,
    word: usize,
    parts: &'static [&'static str],
}

/// One plate per chip colour. Filament 1 is the left nozzle's white; filament 2 the right's colour.
const GROUPS: [Group; 4] = [
    Group { colour: "white", colours: ["#FFFFFF", "#000000"], body: 1, word: 2, parts: &["chip:water", "chip:drain", "collar:water", "collar:drain"] },
    Group { colour: "blue", colours: ["#FFFFFF", "#46A8F9"], body: 2, word: 1, parts: &["chip:carb", "collar:carb"] },
    Group { colour: "red", colours: ["#FFFFFF", "#F54749"], body: 2, word: 1, parts: &["chip:co2", "collar:co2"] },
    Group { colour: "black", colours: ["#FFFFFF", "#000000"], body: 2, word: 1,
            parts: &["chip:flavor-a", "chip:flavor-b", "collar:flavor-a", "collar:flavor-b", "nameplate"] },
];

fn file_sha(path: &Path) -> Result<String> {
    Ok(sha256_hex(&std::fs::read(path).with_context(|| format!("reading {}", path.display()))?))
}

#[derive(Clone, Copy, PartialEq)]
enum Bed {
    /// The flat back on the bed, as the nameplate's print pose lays it.
    Back,
    /// The collar's flat face on the bed.
    Face,
}

fn source(root: &Path, part: &str) -> Result<(PathBuf, Bed)> {
    let (kind, which) = part.split_once(':').unwrap_or((part, ""));
    let hp = root.join("hardware/printed-parts");
    Ok(match kind {
        "chip" => (hp.join(format!("enclosure/rear-identification/rear-label-{which}.step")), Bed::Back),
        "collar" => (hp.join(format!("faucet/tube-collar/tube-collar-{which}.step")), Bed::Face),
        "nameplate" => (hp.join("enclosure/nameplate/nameplate-001.step"), Bed::Back),
        _ => bail!("no label part {part}"),
    })
}

struct Shape {
    vertices: Vec<[f64; 3]>,
    faces: Vec<[usize; 3]>,
}

impl Shape {
    fn volume(&self) -> f64 {
        self.faces.iter().map(|f| {
            let [a, b, c] = f.map(|i| self.vertices[i]);
            a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])
        }).sum::<f64>() / 6.0
    }

    fn bounds(&self) -> ([f64; 3], [f64; 3]) {
        bounds(&self.vertices)
    }
}

/// The part's body and its lettering, the solids of its fine model, posed face up and centred on
/// the plate origin.
fn bodies(step: &Path, bed: Bed) -> Result<(Shape, Shape)> {
    let model = PathBuf::from(format!("{}.npz", step.display()));
    let arrays = npz::read_arrays(&model)?;
    let mut solids: Vec<Shape> = Vec::new();
    for i in 0.. {
        let (Some(v), Some(t)) = (arrays.get(&format!("V{i}")), arrays.get(&format!("T{i}"))) else { break };
        let flat = v.f64().context("vertex array")?;
        let index = t.indices().context("triangle array")?;
        solids.push(Shape {
            vertices: flat.chunks(3).map(|c| [c[0], c[1], c[2]]).collect(),
            faces: index.chunks(3).map(|c| [c[0], c[1], c[2]]).collect(),
        });
    }
    solids.sort_by(|a, b| b.volume().partial_cmp(&a.volume()).unwrap());
    if solids.len() < 2 {
        bail!("{} has no lettering body", model.display());
    }
    let body = solids.remove(0);
    // Lettering of several solids prints as one.
    let mut word = Shape { vertices: Vec::new(), faces: Vec::new() };
    for s in solids {
        let base = word.vertices.len();
        word.vertices.extend(s.vertices);
        word.faces.extend(s.faces.iter().map(|f| f.map(|i| i + base)));
    }
    let pose = |p: [f64; 3]| match bed {
        // A quarter turn about X, then half a turn about Z.
        Bed::Back => [-p[0], p[2], p[1]],
        // Half a turn about X.
        Bed::Face => [p[0], -p[1], -p[2]],
    };
    let (mut body, mut word) = (body, word);
    for v in body.vertices.iter_mut().chain(word.vertices.iter_mut()) {
        *v = pose(*v);
    }
    let (lo, hi) = body.bounds();
    let shift = [-(lo[0] + hi[0]) / 2.0, -(lo[1] + hi[1]) / 2.0, -lo[2]];
    for v in body.vertices.iter_mut().chain(word.vertices.iter_mut()) {
        *v = [v[0] + shift[0], v[1] + shift[1], v[2] + shift[2]];
    }
    Ok((body, word))
}

/// `petgf.3mf` with its filament arrays doubled onto both nozzles, as the nameplate's preparer does.
fn two_hotend_settings(root: &Path, colours: [&str; 2]) -> Result<(Plate, Value)> {
    let profile = profile::load(&root.join(PROFILE), Some(Z_TRIM), None, root)?;
    let mut plate = Plate::new("", &profile, "homesodamachine/labels/");
    let original = profile.settings.clone();
    let variants = original.get("filament_extruder_variant").map(Json::list).map_or(0, <[Json]>::len);
    let Json::Map(entries) = &mut plate.settings else { bail!("the recipe's settings are not a map") };
    for (_, value) in entries.iter_mut() {
        if let Json::List(items) = value {
            if items.len() == 1 || items.len() == variants {
                let again = items.clone();
                items.extend(again);
            }
        }
    }
    let registration: Value = serde_json::from_slice(&std::fs::read(root.join(REGISTRATION))?)?;
    if registration["status"] != "nameplate_appearance_accepted" {
        bail!("{REGISTRATION} status is {}", registration["status"]);
    }
    let texts = |items: &[&str]| Json::List(items.iter().map(|s| Json::Text(s.to_string())).collect());
    let repeat = |item: &str, n: usize| Json::List(vec![Json::Text(item.to_string()); n]);
    let indices: Vec<&str> = std::iter::repeat_n("1", variants).chain(std::iter::repeat_n("2", variants)).collect();
    let offset: Vec<&str> = registration["native_extruder_offset"].as_array().context("registration offset")?.iter().filter_map(Value::as_str).collect();
    let flush: Vec<&str> = ["0", "140", "140", "0"].repeat(2);
    for (key, value) in [
        ("filament_colour", texts(&colours)), ("filament_multi_colour", texts(&colours)), ("filament_map", texts(&["1", "2"])),
        ("filament_map_2", texts(&["1", "2"])), ("filament_nozzle_map", texts(&["0", "1"])), ("filament_map_mode", Json::Text("Manual".into())),
        ("filament_volume_map", texts(&["0", "0"])), ("filament_self_index", texts(&indices)),
        ("filament_printable", texts(&["3", "3"])), ("extruder_ams_count", texts(&["1#0|4#0", "1#0|4#0"])),
        ("filament_prime_volume", texts(&["45", "45"])), ("flush_volumes_vector", repeat("140", 4)),
        ("flush_volumes_matrix", texts(&flush)), ("extruder_offset", texts(&offset)), ("enable_support", Json::Text("0".into())),
        ("brim_type", Json::Text("no_brim".into())), ("brim_width", Json::Text("0".into())),
        ("initial_layer_print_height", Json::Text("0.2".into())), ("layer_height", Json::Text("0.24".into())),
        ("flush_into_support", Json::Text("0".into())), ("wipe_tower_x", texts(&["135", "135"])), ("wipe_tower_y", texts(&["90", "90"])),
    ] {
        plate.settings.set(key, value);
    }
    let mut filament = Json::parse(std::str::from_utf8(plate.members.get("Metadata/filament_settings_1.config").context("no filament settings")?)?)?;
    filament.set("filament_printable", texts(&["3"]));
    plate.members.retain(|name, _| name.starts_with("Metadata/filament_settings_"));
    for member in ["Metadata/filament_settings_1.config", "Metadata/filament_settings_2.config"] {
        plate.members.insert(member.into(), filament.dumps().into_bytes());
    }
    let mut changes = Map::new();
    if let Json::Map(entries) = &plate.settings {
        for (key, value) in entries {
            if original.get(key) != Some(value) {
                changes.insert(key.clone(), json!({"from": original.get(key).map(Json::to_value), "to": value.to_value()}));
            }
        }
    }
    let recipe = json!({"profile_changes": profile.changes, "two_hotend_changes": changes,
                        "registration": REGISTRATION, "registration_sha256": file_sha(&root.join(REGISTRATION))?});
    Ok((plate, recipe))
}

/// Rows of parts, widest first, centred on the shared printable area.
fn layout(footprints: &[[f64; 2]], centre: [f64; 2]) -> Vec<[f64; 2]> {
    let mut order: Vec<usize> = (0..footprints.len()).collect();
    order.sort_by(|&a, &b| footprints[b][0].partial_cmp(&footprints[a][0]).unwrap());
    let (mut rows, mut row, mut width): (Vec<Vec<usize>>, Vec<usize>, f64) = (Vec::new(), Vec::new(), 0.0);
    for i in order {
        let dx = footprints[i][0];
        if !row.is_empty() && width + GAP + dx > ROW {
            rows.push(std::mem::take(&mut row));
            width = 0.0;
        }
        width += if row.is_empty() { 0.0 } else { GAP } + dx;
        row.push(i);
    }
    rows.push(row);
    let depth_of = |r: &[usize]| r.iter().map(|&i| footprints[i][1]).fold(f64::NEG_INFINITY, f64::max);
    let depth: f64 = rows.iter().map(|r| depth_of(r)).sum::<f64>() + GAP * (rows.len() - 1) as f64;
    let mut placed = vec![[0.0; 2]; footprints.len()];
    let mut y = centre[1] + depth / 2.0;
    for r in &rows {
        let row_depth = depth_of(r);
        let row_width: f64 = r.iter().map(|&i| footprints[i][0]).sum::<f64>() + GAP * (r.len() - 1) as f64;
        let mut x = centre[0] - row_width / 2.0;
        for &i in r {
            placed[i] = [x + footprints[i][0] / 2.0, y - row_depth / 2.0];
            x += footprints[i][0] + GAP;
        }
        y -= row_depth + GAP;
    }
    placed
}

fn round(v: f64, digits: i32) -> f64 {
    let scale = 10f64.powi(digits);
    (v * scale).round() / scale
}

fn today() -> Result<String> {
    Ok(String::from_utf8(std::process::Command::new("date").arg("+%Y-%m-%d").output()?.stdout)?.trim().to_string())
}

fn now_utc() -> Result<String> {
    Ok(String::from_utf8(std::process::Command::new("date").args(["-u", "+%Y-%m-%dT%H:%M:%S+00:00"]).output()?.stdout)?.trim().to_string())
}

fn prepare(root: &Path, group: &Group, output: &Path) -> Result<PathBuf> {
    let (mut plate, recipe) = two_hotend_settings(root, group.colours)?;
    plate.title = format!("{} identification; Mark2", group.colour);
    plate.filament_maps = Some("1 2".into());
    plate.filament_map_mode = "Manual".into();
    plate.filament_volume_maps = "0 0".into();
    let centre = [(USABLE.0[0] + USABLE.1[0]) / 2.0, (USABLE.0[1] + USABLE.1[1]) / 2.0];
    struct Part { part: &'static str, step: PathBuf, bed: Bed, body: Shape, word: Shape, footprint: [f64; 2] }
    let mut parts: Vec<Part> = Vec::new();
    let mut sources: BTreeMap<String, String> = BTreeMap::new();
    for &part in group.parts {
        let (step, bed) = source(root, part)?;
        let (body, word) = bodies(&step, bed)?;
        let (bl, bh) = body.bounds();
        let (wl, wh) = word.bounds();
        let footprint = [bh[0].max(wh[0]) - bl[0].min(wl[0]), bh[1].max(wh[1]) - bl[1].min(wl[1])];
        sources.insert(relative(&step, root), file_sha(&step)?);
        parts.push(Part { part, step, bed, body, word, footprint });
    }
    let positions = layout(&parts.iter().map(|p| p.footprint).collect::<Vec<_>>(), centre);
    // The prime tower stands centred behind the parts, clear of every footprint.
    let back = parts.iter().zip(&positions).map(|(p, at)| at[1] + p.footprint[1] / 2.0).fold(f64::NEG_INFINITY, f64::max);
    let width: f64 = plate.settings.first_text("prime_tower_width").context("prime tower width")?.parse()?;
    let tower = |v: f64| Json::List(vec![Json::Text(format!("{v:.1}")); 2]);
    plate.settings.set("wipe_tower_x", tower(centre[0] - width / 2.0));
    plate.settings.set("wipe_tower_y", tower(back + GAP * 2.0));
    let tops: Vec<f64> = parts.iter().filter(|p| p.bed == Bed::Back)
        .flat_map(|p| [round(p.body.bounds().1[2], 4), round(p.word.bounds().1[2], 4)]).collect();
    let bands = derive::closing_schedule(&tops, FINEST, COARSEST_FINE)?;

    let mut digests: Vec<&String> = sources.values().collect();
    digests.sort();
    let digest = &sha256_hex(digests.into_iter().cloned().collect::<Vec<_>>().join("").as_bytes())[..8];
    let stem = format!("{}-labels-{}-mark2-{digest}", today()?, group.colour);
    std::fs::create_dir_all(output)?;
    let directory = output.canonicalize()?.join(&stem);
    if directory.exists() {
        bail!("{} exists; a preparation directory is written once", relative(&directory, root));
    }
    std::fs::create_dir_all(directory.join("geometry"))?;
    let mut records = Vec::new();
    for (p, at) in parts.iter().zip(&positions) {
        let name = p.part.replace(':', "-");
        let mut meshes = Map::new();
        for (label, shape, tool) in [("body", &p.body, group.body), ("word", &p.word, group.word)] {
            let stl = directory.join("geometry").join(format!("{name}-{label}.stl"));
            write_stl(&stl, &shape.vertices, &shape.faces)?;
            meshes.insert(label.into(), json!({"stl": relative(&stl, root), "stl_sha256": file_sha(&stl)?, "filament": tool,
                "facets": shape.faces.len(), "volume_mm3": round(shape.volume(), 3), "top_mm": round(shape.bounds().1[2], 4)}));
        }
        let identity = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]];
        let model = format!("{}.npz", p.step.file_name().unwrap().to_string_lossy());
        let index = plate.add_object(&name, p.body.vertices.clone(), p.body.faces.clone(), &model, [0.0; 3], identity,
                                     [at[0], at[1], 0.0], None, vec![("extruder".into(), group.body.to_string())]);
        plate.add_part(index, "word", p.word.vertices.clone(), p.word.faces.clone(), "normal_part",
                       vec![("extruder".into(), group.word.to_string())], None);
        plate.objects[index].ranges = bands.iter().map(|&[low, high, height]| Range {
            min_z: low, max_z: high, options: vec![("layer_height".into(), derive::g(height))],
        }).collect();
        records.push(json!({"part": p.part, "step": relative(&p.step, root), "step_sha256": file_sha(&p.step)?,
            "model": relative(&PathBuf::from(format!("{}.npz", p.step.display())), root),
            "model_sha256": file_sha(&PathBuf::from(format!("{}.npz", p.step.display())))?,
            "bed": if p.bed == Bed::Back { "flat back" } else { "flat face" }, "identify_id": plate.objects[index].identify_id,
            "plate_center_xy_mm": [round(at[0], 3), round(at[1], 3)], "footprint_xy_mm": p.footprint.map(|v| round(v, 3)),
            "meshes": meshes}));
    }
    // The cooling stage, over the doubled filament arrays.
    let mut members = plate.members.clone();
    members.insert(profile::SETTINGS_MEMBER.into(), (plate.settings.dumps() + "\n").into_bytes());
    let cooling_changes = cooling::apply_members(&mut members, &profile::cooling_hook(root))?;
    plate.settings = Json::parse(std::str::from_utf8(&members.remove(profile::SETTINGS_MEMBER).unwrap())?)?;
    plate.members = members;
    let project = directory.join(format!("{stem}.3mf"));
    plate.write(&project)?;
    let unique_tops: BTreeSet<u64> = tops.iter().map(|t| t.to_bits()).collect();
    let mut face_up: Vec<f64> = unique_tops.into_iter().map(f64::from_bits).collect();
    face_up.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let right = if group.colour == "white" { "black".to_string() } else { group.colour.to_string() };
    let preparation = json!({
        "piece": format!("labels-{}", group.colour), "printer": "Mark2",
        "nozzle": {"left": "0.4 mm hardened, white PET-GF (filament 1)", "right": format!("0.4 mm hardened, {right} PET-GF (filament 2)")},
        "material": "Polymaker Fiberon PET-GF15, two colours", "filament_colours": group.colours,
        "body_filament": group.body, "word_filament": group.word,
        "project": relative(&project, root), "project_sha256": file_sha(&project)?,
        "profile": PROFILE, "profile_sha256": file_sha(&root.join(PROFILE))?, "requested_z_trim_mm": Z_TRIM,
        // Bambu's Textured PEI compensation emits less than the request, by the amount here.
        "emitted_textured_trim_mm": round(Z_TRIM - 0.02, 3), "recipe": recipe, "cooling_changes": cooling_changes,
        "closing_layer_ranges_mm": bands, "face_up_tops_mm": face_up,
        "usable_plate_mm": [USABLE.0, USABLE.1], "plate_border_mm": BORDER,
        "parts": records, "sources_sha256": sources,
        "tool_sha256": {"hardware/printed-parts/enclosure/trial-preparation/labels.rs": file_sha(&root.join("hardware/printed-parts/enclosure/trial-preparation/labels.rs"))?},
        "prepared_utc": now_utc()?, "sliced": false, "submitted": false,
    });
    std::fs::write(directory.join("preparation.json"), serde_json::to_string_pretty(&preparation)? + "\n")?;
    println!("{}", relative(&project, root));
    Ok(directory)
}

/// Slice a plate with the installed Bambu Studio command line, then read the archive back:
/// integrity, the emitted trim, the bead envelope against the border, no support, every part
/// printed, and a layer top on every face-up top.
fn slice_and_review(root: &Path, directory: &Path) -> Result<bool> {
    let record = directory.join("preparation.json");
    let mut preparation: Value = serde_json::from_slice(&std::fs::read(&record)?)?;
    let project = root.join(preparation["project"].as_str().context("project")?);
    if Some(file_sha(&project)?.as_str()) != preparation["project_sha256"].as_str() {
        bail!("the project changed after preparation");
    }
    let native = directory.join("native");
    std::fs::create_dir(&native)?;
    let cli = slice::cli_project(&project, &native)?;
    let archive_name = project.file_name().unwrap().to_string_lossy().replace(".3mf", ".gcode.3mf");
    let log = std::fs::File::create(native.join("slice.log"))?;
    let status = std::process::Command::new(slice::SLICER)
        .args(["--slice", "0", "--arrange", "0", "--orient", "0", "--outputdir"]).arg(&native)
        .arg("--export-3mf").arg(&archive_name).arg(&cli).current_dir(&native)
        .stdout(log.try_clone()?).stderr(log).status()?;
    if !status.success() {
        bail!("Bambu Studio exited {}; see {}", status.code().unwrap_or(-1), relative(&native.join("slice.log"), root));
    }
    slice::apply_directory(&native, &project)?;
    let sliced: Value = serde_json::from_slice(&std::fs::read(native.join("result.json"))?)?;
    if sliced["return_code"].as_i64() != Some(0) {
        bail!("Bambu Studio reported {}", sliced["error_string"]);
    }
    let archive = directory.join(&archive_name);
    std::fs::copy(native.join(&archive_name), &archive)?;
    let gcode = gcode::plate_gcode(&archive)?;
    let md5 = {
        let mut zip = zip::ZipArchive::new(std::fs::File::open(&archive)?)?;
        let mut text = String::new();
        std::io::Read::read_to_string(&mut zip.by_name("Metadata/plate_1.gcode.md5")?, &mut text)?;
        text.trim().to_lowercase()
    };
    let integrity = hsm_print_prep::ids::md5_hex(&gcode) == md5;
    let head = String::from_utf8_lossy(&gcode[..gcode.len().min(400_000)]).to_string();
    let trims: Vec<f64> = head.lines().filter_map(|l| l.trim_start().strip_prefix("G29.1 Z"))
        .filter_map(|v| v.split(|c: char| !(c.is_ascii_digit() || c == '.' || c == '-' || c == '+')).next()?.parse().ok()).collect();
    let (mut low, mut high) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
    let (mut objects, mut supports, mut layer_count, mut tops) = (BTreeSet::new(), 0usize, 0usize, Vec::new());
    gcode::layers(&gcode, |layer| {
        layer_count += 1;
        tops.push(round(layer.z, 4));
        for road in &layer.roads {
            low = [low[0].min(road.x0.min(road.x1) - road.width / 2.0), low[1].min(road.y0.min(road.y1) - road.width / 2.0)];
            high = [high[0].max(road.x0.max(road.x1) + road.width / 2.0), high[1].max(road.y0.max(road.y1) + road.width / 2.0)];
            supports += road.is_support() as usize;
            if let Some(o) = road.object {
                objects.insert(o);
            }
        }
    });
    let area: Vec<Vec<f64>> = serde_json::from_value(preparation["usable_plate_mm"].clone())?;
    let margins = json!({"left": low[0] - area[0][0], "front": low[1] - area[0][1], "right": area[1][0] - high[0], "back": area[1][1] - high[1]});
    let minimum = margins.as_object().unwrap().values().filter_map(Value::as_f64).fold(f64::INFINITY, f64::min);
    let wanted: Vec<f64> = serde_json::from_value(preparation["face_up_tops_mm"].clone())?;
    let closed: Map<String, Value> = wanted.iter().map(|t| (derive::g(*t), json!(tops.iter().any(|z| (t - z).abs() < 1e-3)))).collect();
    let expected: BTreeSet<i64> = preparation["parts"].as_array().into_iter().flatten().filter_map(|p| p["identify_id"].as_i64()).collect();
    let plates = sliced["sliced_plates"].as_array().cloned().unwrap_or_default();
    let estimated: f64 = plates.iter().map(|p| p["total_predication"].as_f64().unwrap_or(0.0)).sum();
    let emitted = preparation["emitted_textured_trim_mm"].as_f64().unwrap_or(0.0);
    let checks = json!({
        "archive": integrity, "z_trim": trims.last().is_some_and(|t| (t - emitted).abs() < 0.005),
        "bed_border": minimum >= preparation["plate_border_mm"].as_f64().unwrap_or(BORDER),
        "no_support": supports == 0, "every_part_printed": expected.is_subset(&objects),
        "face_up_tops_closed": closed.values().all(|v| v == &json!(true)),
    });
    let passed = checks.as_object().unwrap().values().all(|v| v == &json!(true));
    let result = json!({
        "archive": relative(&archive, root), "archive_sha256": file_sha(&archive)?, "gcode_sha256": sha256_hex(&gcode),
        "gcode_md5_matches": integrity, "emitted_z_trim_mm": trims, "layers": layer_count,
        "bead_envelope_plate_mm": [low, high], "bed_margins_mm": margins, "minimum_bed_margin_mm": minimum,
        "support_roads": supports, "objects_printed": objects, "face_up_tops_closed": closed,
        "estimated_seconds": estimated,
        "slicer_warnings": plates.iter().filter_map(|p| p["warning_message"].as_str()).filter(|s| !s.is_empty()).collect::<Vec<_>>(),
        "checks": checks, "passed": passed,
        "scope": "Commanded paths and bead envelopes from this archive. Colour registration, lettering legibility, fit and finish are physical observations.",
    });
    std::fs::write(directory.join("review.json"), serde_json::to_string_pretty(&result)? + "\n")?;
    preparation["sliced"] = json!(true);
    preparation["archive"] = result["archive"].clone();
    preparation["archive_sha256"] = result["archive_sha256"].clone();
    preparation["gcode_sha256"] = result["gcode_sha256"].clone();
    preparation["estimated_seconds"] = json!(estimated);
    std::fs::write(&record, serde_json::to_string_pretty(&preparation)? + "\n")?;
    println!("{}", serde_json::to_string_pretty(&json!({"archive": result["archive"], "checks": result["checks"],
        "minimum_bed_margin_mm": minimum, "estimated_seconds": estimated}))?);
    Ok(passed)
}

fn main() -> Result<()> {
    let root = hsm_print_prep::root();
    let (mut colours, mut do_slice, mut output) = (Vec::new(), false, root.join(".cache/prints/trial"));
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--colour" => {
                let colour = args.next().context("--colour needs a colour")?;
                if !GROUPS.iter().any(|g| g.colour == colour) {
                    bail!("no {colour} plate; the plates are white, blue, red and black");
                }
                colours.push(colour);
            }
            "--slice" => do_slice = true,
            "--output" => output = PathBuf::from(args.next().context("--output needs a directory")?),
            _ => bail!("unknown argument {arg}"),
        }
    }
    // Preparing and slicing the plates is one of the Mac's heavy runs.
    hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
    let mut failed = Vec::new();
    for group in GROUPS.iter().filter(|g| colours.is_empty() || colours.iter().any(|c| c == g.colour)) {
        let directory = prepare(&root, group, &output)?;
        if do_slice && !slice_and_review(&root, &directory)? {
            failed.push(group.colour);
        }
    }
    if !failed.is_empty() {
        bail!("review did not pass: {}", failed.join(", "));
    }
    Ok(())
}
