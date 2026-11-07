//! aero-float-print-project — the installed all-ASA Aero float's next Mark2 print: the accepted
//! recipe with the current float and its RC62 insertion pause, sliced offline and reviewed. Never
//! contacts a printer.
//!
//!     aero-float-print-project
//!
//! The recipe is the identified v1 project's, as its preflight record binds it. The current float
//! mesh replaces the v1 body and the pause sits before the first layer over the magnet pocket.
//! The slice must pause once, after the last layer with the pocket open and before the first
//! layer over the magnet, keep the guide bore open on that layer, and lay beads over the float's
//! sections. The project, its previews and its preflight record go into `mark2-print/v2`, the
//! archive into the job's `ready/`; a job that started and did not finish is left to inspect.

#![recursion_limit = "256"]

use anyhow::{bail, Context, Result};
use hsm_aero_float_numbers as float;
use hsm_print_prep::gcode::Road;
use hsm_print_prep::ids::md5_hex;
use hsm_print_prep::json::{python_number, Json};
use hsm_print_prep::mesh::Mesh;
use hsm_print_prep::profile::{relative, SETTINGS_MEMBER};
use hsm_print_prep::review::{bead_cover, ring_spans, section_spans};
use hsm_print_prep::{faucet, project, root, sha256_hex, slice};
use serde_json::{json, Map, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::io::Write;
use std::rc::Rc;

const HERE: &str = "hardware/printed-parts/cold-core/magnetic-float/all-aero";
const RECIPE: &str = "all-aero-float.3mf";
const RECIPE_RECORD: &str = "mark2-print/v1/float-preflight.json";
const RECORDS: &str = "mark2-print/v2";
const JOB: &str = ".cache/prints/magnetic-float-all-aero-mark2-v2";
const NAME: &str = "magnetic-float-all-aero-mark2-v2.gcode.3mf";
const GCODE: &str = "Metadata/plate_1.gcode";
const TITLE: &str = "All-ASA Aero float with RC62 insertion pause";
/// The adaptive-leveling bounds the recipe selects in its start G-code.
const LEVELING: &str = "X110 Y14 I181 J154";
const CENTRE: [f64; 2] = [150.0, 145.0];
const MESSAGE: &str = "Insert one RC62 ring into the open annular pocket, fully down onto its floor. The magnet must sit below both pocket rims. Keep the guide bore open and clear loose strings without moving the float. Resume only with the magnet fully seated.";
const FEATURES: [&str; 4] = ["Inner wall", "Outer wall", "Overhang wall", "Gap infill"];
/// The filament the feed is measured in, and its density.
const FILAMENT_DIAMETER: f64 = 1.75;
const FILAMENT_DENSITY: f64 = 0.99;
/// The recipe's contour compensation, by which the printed section grows past the STL's.
const CONTOUR_GROWTH: f64 = 0.05;
/// A ring layer is open below this share of bead cover and closed above the other.
const OPEN: f64 = 0.05;
const CLOSED: f64 = 0.95;
/// Each sampled section's beads must cover more than this share of it.
const COVERED: f64 = 0.97;
/// The seated magnet stays this far under the last open layer, and the first cover this far
/// over the magnet.
const RIM_CLEARANCE: f64 = 0.1;
const COVER_CLEARANCE: f64 = 0.3;
/// The guide bore stays open on the closing layer to within this margin of its radius, with
/// at most this much bead over it.
const BORE_MARGIN: f64 = 0.1;
const BORE_BEADS: f64 = 0.01;

/// One extruding move in an object, as the slice commands it.
struct Move {
    line: usize,
    layer: f64,
    z: f64,
    road: Road,
    extrusion: f64,
}

struct Travel {
    layer: f64,
    distance: f64,
    before_first: bool,
}

/// The letter words `X Y Z E F` of a command, later ones replacing earlier.
fn values(code: &str) -> BTreeMap<char, f64> {
    let mut out = BTreeMap::new();
    let chars: Vec<char> = code.chars().collect();
    let mut i = 0;
    while i < chars.len() {
        if "XYZEF".contains(chars[i]) {
            let start = i + 1;
            let mut j = start;
            while j < chars.len() && (chars[j].is_ascii_digit() || "+-.".contains(chars[j])) {
                j += 1;
            }
            if j > start {
                if let Ok(v) = chars[start..j].iter().collect::<String>().parse() {
                    out.insert(chars[i], v);
                }
                i = j;
                continue;
            }
        }
        i += 1;
    }
    out
}

/// The slice's object moves: the extruding ones, the travels and the count of retractions.
fn moves(program: &str) -> Result<(Vec<Move>, Vec<Travel>, usize)> {
    let (mut xyz, mut e, mut width) = ([0.0f64; 3], 0.0f64, 0.0f64);
    let (mut absolute, mut relative_e) = (true, true);
    let (mut object, mut layer, mut feature) = (None::<i64>, None::<f64>, Rc::<str>::from(""));
    let (mut out, mut travels, mut retracts) = (Vec::new(), Vec::new(), 0);
    let mut deposited = BTreeSet::new();
    for (index, raw) in program.lines().enumerate() {
        let after = |prefix: &str| raw.strip_prefix(prefix).map(str::trim);
        if let Some(v) = after("; OBJECT_ID:") {
            object = v.parse().ok();
        } else if let Some(v) = after("; Z_HEIGHT:") {
            layer = v.parse().ok();
            object = None;
        } else if raw.starts_with("; start printing object, unique label id:") {
            object = raw.rsplit(':').next().and_then(|v| v.trim().parse().ok());
        } else if raw.starts_with("; stop printing object") {
            object = None;
        } else if let Some(v) = after("; FEATURE:") {
            feature = Rc::from(v);
        } else if let Some(v) = after("; LINE_WIDTH:") {
            width = v.parse().unwrap_or(width);
        }
        let code = raw.split(';').next().unwrap_or("").trim();
        let Some(command) = code.split_whitespace().next() else { continue };
        let v = values(code);
        match command {
            "G90" | "G91" => absolute = command == "G90",
            "M82" | "M83" => relative_e = command == "M83",
            "G92" => {
                for (k, c) in ['X', 'Y', 'Z'].into_iter().enumerate() {
                    xyz[k] = v.get(&c).copied().unwrap_or(xyz[k]);
                }
                e = v.get(&'E').copied().unwrap_or(e);
            }
            "G0" | "G1" | "G2" | "G3" => {
                let target: [f64; 3] = std::array::from_fn(|k| {
                    let c = ['X', 'Y', 'Z'][k];
                    if absolute { v.get(&c).copied().unwrap_or(xyz[k]) } else { xyz[k] + v.get(&c).copied().unwrap_or(0.0) }
                });
                let delta = if relative_e { v.get(&'E').copied().unwrap_or(0.0) } else { v.get(&'E').copied().unwrap_or(e) - e };
                let distance = (target[0] - xyz[0]).hypot(target[1] - xyz[1]);
                if let (Some(obj), Some(z)) = (object, layer) {
                    if delta > 1e-9 && distance > 1e-6 {
                        if command != "G0" && command != "G1" {
                            bail!("arc fitting must stay off: line {}", index + 1);
                        }
                        out.push(Move { line: index, layer: z, z: target[2], extrusion: delta,
                            road: Road { x0: xyz[0], y0: xyz[1], x1: target[0], y1: target[1], width, feature: feature.clone(), object: Some(obj), tool: 0 } });
                        deposited.insert(z.to_bits());
                    } else if distance > 1e-6 {
                        travels.push(Travel { layer: z, distance, before_first: !deposited.contains(&z.to_bits()) });
                    }
                    if delta < -1e-9 {
                        retracts += 1;
                    }
                }
                xyz = target;
                if let Some(de) = v.get(&'E') {
                    e = if relative_e { e + de } else { *de };
                }
            }
            _ => {}
        }
    }
    Ok((out, travels, retracts))
}

fn layers(moves: &[Move]) -> Vec<f64> {
    let mut heights: Vec<f64> = moves.iter().map(|m| m.layer).collect();
    heights.sort_by(f64::total_cmp);
    heights.dedup();
    heights
}

fn roads_at(moves: &[Move], z: f64) -> Vec<Road> {
    moves.iter().filter(|m| m.layer == z).map(|m| m.road.clone()).collect()
}

/// The share of the magnet's ring the layer's beads cover.
fn ring_cover(roads: &[Road]) -> f64 {
    let (ro, ri) = (float::MAGNET_OD / 2.0, float::MAGNET_ID / 2.0);
    let (covered, area) = bead_cover(roads, [CENTRE[0] - ro, CENTRE[1] - ro], [CENTRE[0] + ro, CENTRE[1] + ro],
                                     |y| ring_spans(CENTRE, ri, ro, y));
    if area > 0.0 { covered / area } else { 0.0 }
}

/// The pause, the layers either side of it and the guide bore, read off the slice.
fn magnet_pause_review(program: &str, moves: &[Move]) -> Result<Value> {
    let pauses: Vec<usize> = program.lines().enumerate().filter(|(_, l)| l.split(';').next().unwrap_or("").trim() == "M400 U1").map(|(i, _)| i).collect();
    let [pause] = pauses.as_slice() else { bail!("the slice pauses {} times", pauses.len()) };
    let heights = layers(moves);
    let mut coverage = Vec::new();
    for &z in &heights {
        if float::magnet_seat() - 0.4 <= z && z <= float::pocket_roof() + 0.4 {
            coverage.push((z, ring_cover(&roads_at(moves, z))));
        }
    }
    let open: Vec<f64> = coverage.iter().filter(|(_, f)| *f < OPEN).map(|(z, _)| *z).collect();
    let (Some(&lowest_open), Some(&rim)) = (open.first(), open.last()) else { bail!("no layer leaves the magnet pocket open") };
    let seat = heights.iter().copied().filter(|&z| z < lowest_open).fold(f64::NEG_INFINITY, f64::max);
    let first_cover = coverage.iter().filter(|(z, f)| *z > rim && *f > CLOSED).map(|(z, _)| *z).fold(f64::INFINITY, f64::min);
    if first_cover != (float::pause_before_z() * 1e6).round() / 1e6 {
        bail!("the first layer over the magnet is at {first_cover}, not the pause at {}", float::pause_before_z());
    }
    let before_top = moves.iter().filter(|m| m.line < *pause).map(|m| m.layer).fold(f64::NEG_INFINITY, f64::max);
    let after_bottom = moves.iter().filter(|m| m.line > *pause).map(|m| m.layer).fold(f64::INFINITY, f64::min);
    if before_top != rim || after_bottom != first_cover {
        bail!("the pause falls between layers {before_top} and {after_bottom}, not {rim} and {first_cover}");
    }
    if moves.iter().any(|m| m.line < *pause && m.layer == first_cover) {
        bail!("the slice covers the magnet before the pause");
    }
    let cover: Vec<&Move> = moves.iter().filter(|m| m.line > *pause && m.layer == first_cover).collect();
    let cover_z = cover.iter().map(|m| m.z).fold(f64::INFINITY, f64::min);
    if cover_z != first_cover {
        bail!("the first covering roads run at Z{cover_z}, not Z{first_cover}");
    }
    let top = seat + float::MAGNET_THICKNESS + float::MAGNET_TOLERANCE;
    if rim - top < RIM_CLEARANCE || cover_z - top < COVER_CLEARANCE {
        bail!("the seated magnet stands too close to the rim or the cover");
    }
    let cover_roads: Vec<Road> = cover.iter().map(|m| m.road.clone()).collect();
    let r = float::BORE_DIAMETER / 2.0 - BORE_MARGIN;
    let (over_bore, _) = bead_cover(&cover_roads, [CENTRE[0] - r, CENTRE[1] - r], [CENTRE[0] + r, CENTRE[1] + r], |y| {
        let dy = y - CENTRE[1];
        if dy.abs() < r { let x = (r * r - dy * dy).sqrt(); vec![(CENTRE[0] - x, CENTRE[0] + x)] } else { Vec::new() }
    });
    if over_bore >= BORE_BEADS {
        bail!("the closing layer lays {over_bore} mm² over the guide bore");
    }
    let by_layer: Map<String, Value> = coverage.iter().map(|(z, f)| (python_number(*z), json!(f))).collect();
    Ok(json!({"pause_command": "M400 U1", "pause_count": 1,
        "completed_layers_before_pause": heights.iter().position(|&z| z == rim).map_or(0, |i| i + 1),
        "last_open_pocket_layer_z_mm": rim, "printed_seat_top_z_mm": seat, "first_covering_layer_z_mm": cover_z,
        "nominal_printed_magnet_center_z_mm": seat + float::MAGNET_THICKNESS / 2.0,
        "nominal_cad_magnet_center_z_mm": float::magnet_midplane(),
        "physical_center_scope": "Layer quantization, magnet thickness tolerance and actual printed fit limit physical centering.",
        "nominal_seated_magnet_top_z_mm": seat + float::MAGNET_THICKNESS, "maximum_seated_magnet_top_z_mm": top,
        "minimum_magnet_recess_below_printed_rim_mm": rim - top, "minimum_first_cover_nozzle_clearance_mm": cover_z - top,
        "ring_footprint_coverage_by_layer": by_layer, "covering_roads_emitted_after_pause_only": true,
        "guide_bore_remains_open": true, "guide_bore_bead_area_mm2": over_bore, "pause_message": MESSAGE,
        "scope": "Explicit commands and exact bead footprints; firmware parking/resume motion, actual foam, magnet movement and hot metal adhesion remain physical-trial observations."}))
}

/// The beads against the float's grown section at the first two, the middle and the last layer.
fn coverage_review(moves: &[Move], mesh: &Mesh) -> Result<Value> {
    let heights = layers(moves);
    let mut picked: Vec<f64> = vec![heights[0], heights[1], heights[heights.len() / 2], heights[heights.len() - 1]];
    picked.sort_by(f64::total_cmp);
    picked.dedup();
    let triangles: Vec<[[f64; 3]; 3]> = mesh.faces.iter().map(|f| f.map(|i| mesh.vertices[i])).collect();
    let mut out = Vec::new();
    for z in picked {
        let ((lo, hi), spans) = section_spans(&triangles, z - 0.0001, CENTRE, CONTOUR_GROWTH).context("the plane misses the float")?;
        let (covered, area) = bead_cover(&roads_at(moves, z), lo, hi, spans);
        let fraction = covered / area;
        if fraction <= COVERED {
            bail!("the beads cover only {fraction} of the float's section at Z{z}");
        }
        out.push(json!({"layer_z_mm": z, "nominal_solid_area_mm2": area, "bead_footprint_coverage_fraction": fraction,
            "scope": "Exact native bead footprints against the compensated frozen STL section; this does not model actual foaming or establish physical density."}));
    }
    Ok(json!(out))
}

fn travel_review(moves: &[Move], travels: &[Travel], retracts: usize) -> Value {
    let within: Vec<&Travel> = travels.iter().filter(|t| !t.before_first).collect();
    let longest = |ts: &mut dyn Iterator<Item = f64>| ts.fold(0.0, f64::max);
    let mut samples = Map::new();
    let mut sampled: Vec<f64> = vec![moves[0].layer, moves[moves.len() / 2].layer, moves[moves.len() - 1].layer];
    sampled.sort_by(f64::total_cmp);
    sampled.dedup();
    for z in sampled {
        let at: Vec<f64> = travels.iter().filter(|t| t.layer == z).map(|t| t.distance).collect();
        samples.insert(python_number(z), json!({"xy_move_count": at.len(), "xy_distance_mm": at.iter().sum::<f64>(),
                                                 "longest_xy_move_mm": longest(&mut at.iter().copied())}));
    }
    json!({"explicit_object_xy_travel_move_count": travels.len(),
        "explicit_object_xy_travel_distance_mm": travels.iter().map(|t| t.distance).sum::<f64>(),
        "longest_explicit_object_xy_travel_mm": longest(&mut travels.iter().map(|t| t.distance)),
        "moves_longer_than_5_mm": travels.iter().filter(|t| t.distance > 5.0).count(),
        "within_layer_xy_move_count": within.len(), "within_layer_xy_distance_mm": within.iter().map(|t| t.distance).sum::<f64>(),
        "longest_within_layer_xy_move_mm": longest(&mut within.iter().map(|t| t.distance)),
        "object_retraction_count": retracts, "sample_layers": samples, "zero_travel": travels.is_empty(),
        "scope": "Explicit object G0/G1 moves with no positive extrusion, including retraction wipes and initial positioning. The first transfer from the startup strip is included in total travel, and excluded from within-layer travel. Firmware motion, timelapse internals and moves outside object labels are excluded."})
}

/// The pause preview: the float's section with its pocket and magnet, and the roads of the last
/// open layer and of the first layer over the magnet.
fn preview(moves: &[Move], pause: &Value) -> String {
    const PX: f64 = 7.5;
    let mut svg = String::from(r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 360" font-family="Helvetica, Arial, sans-serif" font-size="12"><rect width="960" height="360" fill="white"/>"#);
    let (h, rim, cover) = (float::height(), pause["last_open_pocket_layer_z_mm"].as_f64().unwrap_or(0.0), pause["first_covering_layer_z_mm"].as_f64().unwrap_or(0.0));
    // Section: X across, Z up; one millimetre is PX pixels, the panel 40 mm wide from X-20.
    let sx = |x: f64| 10.0 + (x + 20.0) * PX;
    let sz = |z: f64| 330.0 - (z + 1.0) * 300.0 / 31.0;
    let rect = |svg: &mut String, x0: f64, x1: f64, z0: f64, z1: f64, fill: &str, stroke: &str| {
        svg.push_str(&format!(r#"<rect x="{:.2}" y="{:.2}" width="{:.2}" height="{:.2}" fill="{fill}" stroke="{stroke}" stroke-width="0.8"/>"#,
                              sx(x0), sz(z1), sx(x1) - sx(x0), sz(z0) - sz(z1)));
    };
    for (a, b) in [(-float::DIAMETER / 2.0, -float::BORE_DIAMETER / 2.0), (float::BORE_DIAMETER / 2.0, float::DIAMETER / 2.0)] {
        rect(&mut svg, a, b, 0.0, h, "#e4d5a8", "#665b42");
    }
    for (a, b) in [(-float::POCKET_OD / 2.0, -float::POCKET_ID / 2.0), (float::POCKET_ID / 2.0, float::POCKET_OD / 2.0)] {
        rect(&mut svg, a, b, float::magnet_seat(), float::magnet_seat() + float::POCKET_DEPTH, "white", "#665b42");
    }
    for (a, b) in [(-float::MAGNET_OD / 2.0, -float::MAGNET_ID / 2.0), (float::MAGNET_ID / 2.0, float::MAGNET_OD / 2.0)] {
        rect(&mut svg, a, b, float::magnet_seat(), float::magnet_seat() + float::MAGNET_THICKNESS, "#75828f", "#35424e");
    }
    for (z, colour, dash) in [(float::magnet_midplane(), "#75828f", "6 4"), (cover, "#af523c", "2 3")] {
        svg.push_str(&format!(r#"<line x1="{:.2}" x2="{:.2}" y1="{:.2}" y2="{:.2}" stroke="{colour}" stroke-dasharray="{dash}"/>"#, sx(-20.0), sx(20.0), sz(z), sz(z)));
    }
    svg.push_str(&format!(r#"<text x="160" y="18" text-anchor="middle">{} mm body; magnet center at {} mm</text>"#, python_number(h), python_number(float::magnet_midplane())));
    // Each layer: X and Y about the float's centre, the panel 38 mm square.
    for (n, (z, title)) in [(rim, "Pocket open at pause"), (cover, "First layer over the inserted magnet")].into_iter().enumerate() {
        let x0 = 330.0 + n as f64 * 320.0;
        let px = |x: f64| x0 + (x + 19.0) * 300.0 / 38.0;
        let py = |y: f64| 330.0 - (y + 19.0) * 300.0 / 38.0;
        svg.push_str(&format!(r##"<rect x="{x0}" y="30" width="300" height="300" fill="none" stroke="#bbbbbb"/>"##));
        for m in moves.iter().filter(|m| m.layer == z) {
            svg.push_str(&format!(r##"<line x1="{:.2}" y1="{:.2}" x2="{:.2}" y2="{:.2}" stroke="#244867" stroke-width="0.65"/>"##,
                                  px(m.road.x0 - CENTRE[0]), py(m.road.y0 - CENTRE[1]), px(m.road.x1 - CENTRE[0]), py(m.road.y1 - CENTRE[1])));
        }
        svg.push_str(&format!(r#"<text x="{}" y="18" text-anchor="middle">{title}, Z = {} mm</text>"#, x0 + 150.0, python_number(z)));
    }
    svg.push_str("</svg>\n");
    svg
}

/// `xml` with the first value after `anchor` up to its closing quote replaced by `value`.
fn set_after(xml: &str, anchor: &str, value: &str) -> Result<String> {
    let at = xml.find(anchor).with_context(|| format!("no {anchor}"))? + anchor.len();
    let end = at + xml[at..].find('"').context("an unclosed attribute")?;
    Ok(format!("{}{}{}", &xml[..at], project::attr(value), &xml[end..]))
}

fn utc_now() -> String {
    let secs = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map(|d| d.as_secs() as i64).unwrap_or(0);
    let (days, rest) = (secs.div_euclid(86400), secs.rem_euclid(86400));
    // Civil date from days since 1970-01-01.
    let z = days + 719468;
    let era = z.div_euclid(146097);
    let doe = z - era * 146097;
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let (d, m) = (doy - (153 * mp + 2) / 5 + 1, if mp < 10 { mp + 3 } else { mp - 9 });
    let y = yoe + era * 400 + i64::from(m <= 2);
    format!("{y:04}-{m:02}-{d:02}T{:02}:{:02}:{:02}+00:00", rest / 3600, rest % 3600 / 60, rest % 60)
}

fn main() -> Result<()> {
    let root = root();
    if let Some(arg) = std::env::args().nth(1) {
        bail!("unknown argument {arg}");
    }
    let here = root.join(HERE);
    let (records, job) = (here.join(RECORDS), root.join(JOB));
    let recipe_path = here.join(RECIPE);
    let identified = faucet::read_json(&here.join(RECIPE_RECORD))?;
    if identified["project_sha256"].as_str() != Some(faucet::file_sha(&recipe_path)?.as_str()) {
        bail!("{RECIPE} differs from the v1 project its record identifies");
    }
    let mut members = faucet::members(&recipe_path)?;
    let text = String::from_utf8(members.get(SETTINGS_MEMBER).context("the recipe has no settings")?.clone())?;
    let settings = Json::parse(&text)?;
    let selected: Value = serde_json::from_str(&text)?;
    if settings.first_text("wall_loops") != Some("300") || settings.first_text("machine_pause_gcode").map(str::trim) != Some("M400 U1")
        || settings.first_text("machine_start_gcode").map(|s| s.matches(LEVELING).count()) != Some(3)
        || settings.first_text("print_settings_id") != Some(TITLE) || settings.get("post_process").is_some_and(|p| !p.list().is_empty()) {
        bail!("{RECIPE} no longer holds the float's recipe");
    }
    let stl = here.join("float-aero.stl");
    let mesh = Mesh::read_stl(&stl)?;
    // Closed and consistently wound; the sealed magnet pocket is a shell of its own.
    let closure = hsm_print_prep::mesh::closed_check(&mesh.faces);
    if closure["boundary_edges"] != 0 || closure["nonmanifold_edges"] != 0 || closure["inconsistent_edges"] != 0 {
        bail!("float-aero.stl is not closed and consistently wound: {closure}");
    }
    let (lo, hi) = mesh.bounds();
    let h = float::height();
    if lo[2].abs() > 1e-6 || (hi[2] - h).abs() > 1e-6 {
        bail!("float-aero.stl spans Z{} to Z{}, not the float's height", lo[2], hi[2]);
    }
    let half = python_number(h / 2.0);
    let config = String::from_utf8(members["Metadata/model_settings.config"].clone())?;
    let config = set_after(&config, r#"<metadata key="source_offset_z" value=""#, &half)?;
    let config = set_after(&config, r#"<mesh_stat face_count=""#, &mesh.faces.len().to_string())?;
    members.insert("Metadata/model_settings.config".into(), config.into_bytes());
    let model = String::from_utf8(members["3D/3dmodel.model"].clone())?;
    let at = model.find("<build").context("the model has no build")?;
    let model = format!("{}{}", &model[..at], set_after(&model[at..], r#"transform=""#, &format!("1 0 0 0 1 0 0 0 1 150 145 {half}"))?);
    let member = {
        let at = model.find(r#"p:path="/"#).context("the model names no mesh member")? + r#"p:path="/"#.len();
        model[at..at + model[at..].find('"').unwrap_or(0)].to_string()
    };
    members.insert("3D/3dmodel.model".into(), model.into_bytes());
    let object = String::from_utf8(members.get(&member).with_context(|| format!("no {member}"))?.clone())?;
    let (a, b) = (object.find("<mesh>").context("the object has no mesh")?, object.find("</mesh>").context("an unclosed mesh")? + "</mesh>".len());
    let mut xml = String::from("<mesh><vertices>");
    let vertices: Vec<[f64; 3]> = mesh.vertices.iter().map(|v| [v[0], v[1], v[2] - h / 2.0]).collect();
    for v in &vertices {
        xml.push_str(&format!(r#"<vertex x="{:.8}" y="{:.8}" z="{:.8}" />"#, v[0], v[1], v[2]));
    }
    xml.push_str("</vertices><triangles>");
    for f in &mesh.faces {
        xml.push_str(&format!(r#"<triangle v1="{}" v2="{}" v3="{}" />"#, f[0], f[1], f[2]));
    }
    xml.push_str("</triangles></mesh>");
    members.insert(member.clone(), format!("{}{xml}{}", &object[..a], &object[b..]).into_bytes());
    members.insert("Metadata/custom_gcode_per_layer.xml".into(), format!(
        "<?xml version='1.0' encoding='UTF-8'?>\n<custom_gcodes_per_layer><plate><plate_info id=\"1\" /><layer top_z=\"{:.6}\" type=\"1\" extruder=\"1\" color=\"\" extra=\"{}\" gcode=\"M400 U1\" /><mode value=\"SingleExtruder\" /></plate></custom_gcodes_per_layer>",
        float::pause_before_z(), project::attr(MESSAGE)).into_bytes());
    members.retain(|name, _| !name.starts_with("Metadata/plate_"));

    std::fs::create_dir_all(&records)?;
    let project_path = records.join(RECIPE);
    let native_dir = job.join("native");
    let native = native_dir.join(NAME);
    if !native.exists() {
        if job.exists() {
            bail!("{} holds an unfinished preparation; inspect it before making another export", job.display());
        }
        std::fs::create_dir_all(&native_dir)?;
        let mut archive = zip::ZipWriter::new(std::fs::File::create(&project_path)?);
        for (name, data) in &members {
            archive.start_file(name.as_str(), project::options())?;
            archive.write_all(data)?;
        }
        archive.finish()?;
        // Bambu Studio's slice is one of the Mac's heavy runs.
        hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
        let log = std::fs::File::create(job.join("slice.log"))?;
        let status = std::process::Command::new(slice::SLICER)
            .args(["--arrange", "0", "--orient", "0", "--slice", "0", "--export-3mf", NAME, "--outputdir"]).arg(&native_dir).arg(&project_path)
            .current_dir(&native_dir).stdout(log.try_clone()?).stderr(log).status()?;
        if !status.success() {
            bail!("the offline slice exited {}; {}", status.code().unwrap_or(-1), job.join("slice.log").display());
        }
    }
    if faucet::members(&project_path)? != members {
        bail!("{} is not the project this recipe writes", relative(&project_path, &root));
    }
    let output = faucet::members(&native)?;
    let gcode = output.get(GCODE).context("the archive has no G-code")?;
    if md5_hex(gcode) != String::from_utf8_lossy(&output[&format!("{GCODE}.md5")]).trim().to_lowercase() {
        bail!("the sliced G-code does not match its MD5");
    }
    let program = std::str::from_utf8(gcode)?;
    let effective: Value = serde_json::from_slice(&output[SETTINGS_MEMBER])?;
    for field in ["wall_loops", "top_one_wall_type", "only_one_wall_first_layer", "top_shell_layers", "bottom_shell_layers",
                  "sparse_infill_density", "filament_nozzle_map", "filament_flow_ratio", "curr_bed_type", "nozzle_temperature",
                  "eng_plate_temp", "chamber_temperatures", "enable_support", "skirt_loops", "brim_type", "machine_start_gcode"] {
        if effective[field] != selected[field] {
            bail!("the slice changed {field}");
        }
    }
    let native_model = String::from_utf8_lossy(&output["3D/3dmodel.model"]).to_string();
    let at = native_model.find(r#"p:path="/"#).context("the sliced model names no mesh")? + r#"p:path="/"#.len();
    let native_member = &native_model[at..at + native_model[at..].find('"').unwrap_or(0)];
    let native_mesh = String::from_utf8_lossy(&output[native_member]).to_string();
    let numbers = |tag: &str, keys: &[&str]| -> Vec<Vec<f64>> {
        native_mesh.split(&format!("<{tag} ")).skip(1).map(|chunk| keys.iter().map(|k| {
            chunk.split_once(&format!("{k}=\"")).and_then(|(_, r)| r.split_once('"')).and_then(|(v, _)| v.parse().ok()).unwrap_or(f64::NAN)
        }).collect()).collect()
    };
    let native_vertices = numbers("vertex", &["x", "y", "z"]);
    let native_faces = numbers("triangle", &["v1", "v2", "v3"]);
    if native_vertices.len() != vertices.len() || native_faces.len() != mesh.faces.len()
        || native_faces.iter().zip(&mesh.faces).any(|(n, f)| (0..3).any(|k| n[k] != f[k] as f64)) {
        bail!("the slice's mesh is not the float's");
    }
    let delta = native_vertices.iter().zip(&vertices).map(|(n, v)| (0..3).map(|k| (n[k] - v[k]).abs()).fold(0.0, f64::max)).fold(0.0, f64::max);
    if !(delta < 1e-6) {
        bail!("the slice moved the float's vertices by {delta} mm");
    }
    let startup = program.split("; MACHINE_START_GCODE_END").next().unwrap_or("");
    if !startup.contains(LEVELING) || !startup.contains(";===== ASA Aero bed priming strip =====") {
        bail!("the slice's startup lost the recipe's leveling bounds or bed priming strip");
    }
    let trims: Vec<f64> = program.lines().filter_map(|l| l.trim_start().strip_prefix("G29.1 Z"))
        .filter_map(|v| v.chars().take_while(|c| c.is_ascii_digit() || "+-.".contains(*c)).collect::<String>().parse().ok()).collect();
    if trims != [0.0, 0.04] {
        bail!("the slice emits Z trims {trims:?}");
    }
    let result = faucet::read_json(&native_dir.join("result.json"))?;
    let summary = &result["sliced_plates"][0];
    if summary["warning_message"].as_str().is_some_and(|w| !w.is_empty()) || summary["objects"].as_array().map_or(0, Vec::len) != 1 {
        bail!("the slice warns or holds other objects");
    }
    let (moves, travels, retracts) = moves(program)?;
    if moves.is_empty() || moves.iter().map(|m| m.road.object).collect::<BTreeSet<_>>().len() != 1 {
        bail!("the slice lays no roads, or roads for more than the float");
    }
    let mut features: BTreeMap<String, usize> = BTreeMap::new();
    for m in &moves {
        *features.entry(m.road.feature.to_string()).or_default() += 1;
    }
    if let Some(other) = features.keys().find(|f| !FEATURES.contains(&f.as_str())) {
        bail!("the slice lays {other}");
    }
    let coverage = coverage_review(&moves, &mesh)?;
    let pause = magnet_pause_review(program, &moves)?;

    let ready = job.join("ready");
    std::fs::create_dir_all(&ready)?;
    let archive = ready.join(NAME);
    if archive.exists() {
        if std::fs::read(&archive)? != std::fs::read(&native)? {
            bail!("{} differs from the slice", archive.display());
        }
    } else {
        std::fs::copy(&native, &archive)?;
    }
    let mut permissions = std::fs::metadata(&archive)?.permissions();
    permissions.set_readonly(true);
    std::fs::set_permissions(&archive, permissions)?;
    std::fs::write(ready.join("plate_1.gcode"), gcode)?;
    if let Some(png) = output.get("Metadata/plate_1.png") {
        std::fs::write(records.join("native-preview.png"), png)?;
    }
    std::fs::write(records.join("pause-preview.svg"), preview(&moves, &pause))?;
    let mass = moves.iter().map(|m| m.extrusion).sum::<f64>() * std::f64::consts::PI * (FILAMENT_DIAMETER / 2.0).powi(2) * FILAMENT_DENSITY / 1000.0;
    let mut snapshot = Map::new();
    for name in ["all_aero_float.rs", "numbers.rs", "design.json", "prepare_print.rs"] {
        snapshot.insert(relative(&here.join(name), &root), json!(faucet::file_sha(&here.join(name))?));
    }
    let layer_count = layers(&moves).len();
    let record = json!({"article": "All-ASA Aero magnetic float with RC62 insertion pause", "printer": "Mark2",
        "status": "prepared_not_submitted", "send_attempts": 0, "preview_inspected": false, "source_snapshot": snapshot,
        "source_stl_sha256": {"float-aero": faucet::file_sha(&stl)?}, "source_step_sha256": faucet::file_sha(&here.join("float-aero.step"))?,
        "recipe_project": relative(&recipe_path, &root), "recipe_project_sha256": faucet::file_sha(&recipe_path)?,
        "recipe_record": relative(&here.join(RECIPE_RECORD), &root), "recipe_settings_retained": true,
        "project": relative(&project_path, &root), "project_sha256": faucet::file_sha(&project_path)?,
        "archive": relative(&archive, &root), "archive_sha256": faucet::file_sha(&archive)?, "gcode_sha256": sha256_hex(gcode),
        "slicer_version": program.lines().find_map(|l| l.strip_prefix("; BambuStudio ")).unwrap_or(""),
        "native_mesh_vertex_max_delta_mm": delta, "native_triangle_connectivity_retained": true,
        "native_geometry_matches_frozen_stl": true, "center_xy_mm": CENTRE, "bed_z_mm": 0, "bed": "Engineering Plate, with glue",
        "requested_z_trim_mm": 0.04, "emitted_z_trim_commands_mm": trims, "native_recipe_retained": true,
        "adaptive_leveling_bounds_mm": {"x_min": 110, "x_max": 291, "y_min": 14, "y_max": 168},
        "recipe": {"wall_loops": 300, "top_shell_layers": 0, "bottom_shell_layers": 0, "sparse_infill_density_percent": 0,
                   "layer_height_mm": 0.2, "line_width_mm": 0.48, "flow_ratio": 0.52, "nozzle_c": 270, "bed_c": 90, "chamber_c": 60},
        "material_mapping": {"material": "Bambu ASA Aero White 46100", "filament_id": "GFB02", "source": "Polymaker drybox",
                             "external_slot": 255, "nozzle": "right fixed hardened standard-flow 0.4 mm",
                             "send_dialog_tile_required": "Ext ASA-AERO R", "send_dialog_verified": false},
        "native_slice_summary": {"estimated_time_s": summary["total_predication"], "filament_mass_g": summary["filaments"][0]["total_used_g"],
            "object_feed_mass_g": mass, "feed_mass_per_cad_foam_volume_g_cc": mass / float::foam_cc(),
            "scope": "Slicer/feed accounting excludes magnet, startup waste and firmware extrusion; it is not measured foam density.",
            "object_count": 1, "warnings": []},
        "path_features": features, "layers": layer_count, "coverage_review": coverage,
        "travel_review": travel_review(&moves, &travels, retracts), "magnet_pause_review": pause,
        "skirt_paths": 0, "brim_paths": 0, "support_paths": 0, "prepared_utc": utc_now(),
        "physical_print_completed": false, "density_verified": false, "buoyancy_verified": false});
    std::fs::write(records.join("float-preflight.json"), serde_json::to_string_pretty(&record)? + "\n")?;
    println!("{}", serde_json::to_string_pretty(&json!({"archive": record["archive"], "minutes": summary["total_predication"].as_f64().unwrap_or(0.0) / 60.0,
        "pause": record["magnet_pause_review"]["first_covering_layer_z_mm"], "layers": layer_count}))?);
    Ok(())
}
