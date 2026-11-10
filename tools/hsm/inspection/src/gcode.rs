//! On-demand slice readings retain continuous walls, commanded speeds and seam positions.
pub(crate) use crate::math::{add, dot, scale, sub};
use anyhow::{Context, Result, ensure};
use clap::{Args, Parser, Subcommand};
use hsm_print_prep::{gcode as beads, review, xml};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    io::{Read, Write},
    ops::RangeInclusive,
    path::{Path, PathBuf},
};

#[path = "gcode_view.rs"]
pub mod view;

pub const OUTER_WALLS: [&str; 2] = ["Outer wall", "Overhang wall"];

/// A continuous commanded path keeps move metadata separate from deposited-bead reviews.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Run {
    pub layer: i64,
    pub z: f64,
    pub h: Option<f64>,
    pub object: Option<i64>,
    pub line: usize,
    pub end_line: usize,
    pub pts: Vec<[f64; 3]>,
    pub feed: Vec<f64>,
    pub overhang: Vec<bool>,
    pub lines: Vec<usize>,
}

pub fn slice_text(path: &Path, plate: usize) -> Result<String> {
    let bytes = if path.extension().is_some_and(|v| v == "gcode") {
        fs::read(path).with_context(|| format!("reading {}", path.display()))?
    } else if plate == 1 {
        beads::plate_gcode(path)?
    } else {
        ensure!(plate > 0, "plate numbers start at one");
        let mut archive = zip::ZipArchive::new(fs::File::open(path)?)?;
        let mut bytes = Vec::new();
        archive
            .by_name(&format!("Metadata/plate_{plate}.gcode"))?
            .read_to_end(&mut bytes)?;
        bytes
    };
    Ok(String::from_utf8(bytes).context("slice G-code is not UTF-8")?)
}

fn word(words: &[(u8, f64)], key: u8) -> Option<f64> {
    words.iter().find(|(k, _)| *k == key).map(|(_, v)| *v)
}
fn distance_xy(a: [f64; 3], b: [f64; 3]) -> f64 {
    (a[0] - b[0]).hypot(a[1] - b[1])
}
pub(crate) fn rounded(value: f64, places: i32) -> f64 {
    let factor = 10f64.powi(places);
    (value * factor).round_ties_even() / factor
}
fn arc(start: [f64; 3], end: [f64; 3], words: &[(u8, f64)], clockwise: bool) -> Vec<[f64; 3]> {
    let centre = [
        start[0] + word(words, b'I').unwrap_or(0.),
        start[1] + word(words, b'J').unwrap_or(0.),
    ];
    let radius = (start[0] - centre[0]).hypot(start[1] - centre[1]);
    let first = (start[1] - centre[1]).atan2(start[0] - centre[0]);
    let mut sweep = (end[1] - centre[1]).atan2(end[0] - centre[0]) - first;
    if clockwise {
        if sweep >= -1e-9 {
            sweep -= std::f64::consts::TAU;
        }
    } else if sweep <= 1e-9 {
        sweep += std::f64::consts::TAU;
    }
    let count = ((sweep.abs() * radius / 0.25).ceil() as usize).max(1);
    let mut points = (1..=count)
        .map(|i| {
            let t = i as f64 / count as f64;
            let angle = first + sweep * t;
            [
                centre[0] + radius * angle.cos(),
                centre[1] + radius * angle.sin(),
                start[2] + (end[2] - start[2]) * t,
            ]
        })
        .collect::<Vec<_>>();
    points[count - 1] = end;
    points
}

/// Feed-only changes and scarf connectors stay inside a run; travel and retraction end it.
pub fn read_runs(text: &str, object_id: Option<i64>, features: &[&str]) -> Result<Vec<Run>> {
    let mut position = [0.; 3];
    let (mut relative_e, mut absolute_xyz) = (true, true);
    let (mut z, mut height) = (None, None);
    let mut layer = -1;
    let (mut feature, mut object, mut feed, mut e_absolute) = ("", None, 0., 0.);
    let mut run: Option<Run> = None;
    let mut runs = Vec::new();
    fn finish(run: &mut Option<Run>, runs: &mut Vec<Run>) {
        if let Some(run) = run.take().filter(|run| run.pts.len() > 2) {
            runs.push(run);
        }
    }
    for (index, raw) in text.lines().enumerate() {
        let line = index + 1;
        if let Some(comment) = raw.strip_prefix(';') {
            let comment = comment.trim();
            if let Some(value) = comment.strip_prefix("Z_HEIGHT:") {
                finish(&mut run, &mut runs);
                z = Some(
                    value
                        .trim()
                        .parse::<f64>()
                        .with_context(|| format!("layer Z at G-code line {line}"))?,
                );
                layer += 1;
            } else if let Some(value) = comment.strip_prefix("LAYER_HEIGHT:") {
                height = Some(
                    value
                        .trim()
                        .parse::<f64>()
                        .with_context(|| format!("layer height at G-code line {line}"))?,
                );
            } else if let Some(value) = comment.strip_prefix("FEATURE:") {
                feature = value.trim();
                if !features.contains(&feature) {
                    finish(&mut run, &mut runs);
                }
            } else if let Some(value) = comment.strip_prefix("OBJECT_ID:") {
                finish(&mut run, &mut runs);
                object = Some(
                    value
                        .trim()
                        .parse::<i64>()
                        .with_context(|| format!("object at G-code line {line}"))?,
                );
            } else if let Some(value) =
                comment.strip_prefix("start printing object, unique label id:")
            {
                finish(&mut run, &mut runs);
                object = Some(
                    value
                        .trim()
                        .parse::<i64>()
                        .with_context(|| format!("object at G-code line {line}"))?,
                );
            } else if comment.starts_with("stop printing object") {
                finish(&mut run, &mut runs);
                object = None;
            }
            continue;
        }
        let code = raw.split(';').next().unwrap_or("").trim();
        let Some(command) = code.split_whitespace().next() else {
            continue;
        };
        match command {
            "G90" | "G91" => {
                absolute_xyz = command == "G90";
                continue;
            }
            "M82" | "M83" => {
                relative_e = command == "M83";
                continue;
            }
            "G0" | "G1" | "G2" | "G3" | "G92" => {}
            _ => continue,
        }
        let words = beads::words(&code[command.len()..]);
        if command == "G92" {
            for (i, key) in b"XYZ".iter().enumerate() {
                position[i] = word(&words, *key).unwrap_or(position[i]);
            }
            e_absolute = word(&words, b'E').unwrap_or(e_absolute);
            continue;
        }
        if let Some(value) = word(&words, b'F') {
            feed = value / 60.;
        }
        let mut next = position;
        for (i, key) in b"XYZ".iter().enumerate() {
            if let Some(value) = word(&words, *key) {
                next[i] = if absolute_xyz {
                    value
                } else {
                    position[i] + value
                };
            }
        }
        let e = word(&words, b'E');
        let delta = e.map_or(0., |value| {
            if relative_e {
                value
            } else {
                value - e_absolute
            }
        });
        if let Some(value) = e {
            e_absolute = if relative_e {
                e_absolute + value
            } else {
                value
            };
        }
        let step = distance_xy(next, position);
        let moved = step > 1e-9;
        let wanted = features.contains(&feature)
            && z.is_some()
            && object_id.is_none_or(|id| object == Some(id));
        let extruding = e.is_some() && delta >= 0.;
        let hop =
            run.is_some() && e.is_none() && step <= 0.02 && (next[2] - position[2]).abs() <= 0.002;
        if wanted && moved && (extruding || hop) {
            let run = run.get_or_insert_with(|| Run {
                layer,
                z: z.unwrap(),
                h: height,
                object,
                line,
                end_line: line,
                pts: vec![position],
                feed: Vec::new(),
                overhang: Vec::new(),
                lines: Vec::new(),
            });
            let points = if command == "G2" || command == "G3" {
                arc(position, next, &words, command == "G2")
            } else {
                vec![next]
            };
            let count = points.len();
            run.pts.extend(points);
            run.feed.extend(std::iter::repeat_n(feed, count));
            run.overhang
                .extend(std::iter::repeat_n(feature == "Overhang wall", count));
            run.lines.extend(std::iter::repeat_n(line, count));
            run.end_line = line;
        } else if moved || delta < 0. {
            finish(&mut run, &mut runs);
        }
        position = next;
    }
    finish(&mut run, &mut runs);
    Ok(runs)
}

/// An absent identify label leaves the slice's actual object labels available for inspection.
pub fn object_in(text: &str, identify_id: Option<i64>) -> Option<i64> {
    let id = identify_id?;
    text.lines()
        .filter_map(|line| {
            let comment = line.strip_prefix(';')?.trim();
            let value = comment
                .strip_prefix("OBJECT_ID:")
                .or_else(|| comment.strip_prefix("start printing object, unique label id:"))?;
            value.trim().parse::<i64>().ok()
        })
        .any(|value| value == id)
        .then_some(id)
}
pub fn first_lap(points: &[[f64; 3]], tolerance: f64) -> Option<usize> {
    let start = *points.first()?;
    let away = points
        .iter()
        .position(|p| distance_xy(*p, start) > 2. * tolerance)?;
    points
        .iter()
        .enumerate()
        .skip(away + 1)
        .find(|(_, p)| distance_xy(**p, start) < tolerance)
        .map(|(i, _)| i)
}
pub fn polygon(points: &[[f64; 3]]) -> (f64, [f64; 2]) {
    if points.is_empty() {
        return (0., [0.; 2]);
    }
    let (mut twice_area, mut x, mut y) = (0., 0., 0.);
    for i in 0..points.len() {
        let (a, b) = (points[i], points[(i + 1) % points.len()]);
        let cross = a[0] * b[1] - b[0] * a[1];
        twice_area += cross;
        x += (a[0] + b[0]) * cross;
        y += (a[1] + b[1]) * cross;
    }
    let area = twice_area / 2.;
    if area.abs() < 1e-12 {
        return (
            0.,
            std::array::from_fn(|i| points.iter().map(|p| p[i]).sum::<f64>() / points.len() as f64),
        );
    }
    (area, [x / (6. * area), y / (6. * area)])
}
pub struct ExteriorLoop<'a> {
    pub run: &'a Run,
    pub lap: &'a [[f64; 3]],
    pub closed: bool,
    pub area: f64,
    pub centroid: [f64; 2],
}
pub fn exterior_loops(runs: &[Run]) -> Vec<ExteriorLoop<'_>> {
    let mut best = BTreeMap::<(String, i64), ExteriorLoop<'_>>::new();
    for run in runs {
        let cut = first_lap(&run.pts, 0.6);
        let lap = &run.pts[..cut.map_or(run.pts.len(), |i| i + 1)];
        let (area, centroid) = polygon(lap);
        let key = (
            run.object
                .map_or_else(|| "None".into(), |id| id.to_string()),
            run.layer,
        );
        if area > 0. && best.get(&key).is_none_or(|previous| area > previous.area) {
            best.insert(
                key,
                ExteriorLoop {
                    run,
                    lap,
                    closed: cut.is_some(),
                    area,
                    centroid,
                },
            );
        }
    }
    best.into_values().collect()
}
pub fn start_normal(points: &[[f64; 3]]) -> [f64; 3] {
    let Some(start) = points.first() else {
        return [0., -1., 0.];
    };
    let direction = points
        .iter()
        .find(|p| distance_xy(**p, *start) > 0.3)
        .map(|p| [p[0] - start[0], p[1] - start[1]])
        .unwrap_or([1., 0.]);
    let length = direction[0].hypot(direction[1]);
    [direction[1] / length, -direction[0] / length, 0.]
}

/// A selected print part supplies its authored plate transform and source-model centre.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Placement {
    pub name: String,
    pub identify_id: Option<i64>,
    pub member: Option<String>,
    pub object_id: Option<i64>,
    pub m: [[f64; 3]; 3],
    pub t: [f64; 3],
    pub center: [f64; 3],
}
fn vector(value: &Value, what: &str) -> Result<[f64; 3]> {
    let values = value
        .as_array()
        .with_context(|| format!("{what} is an array"))?;
    ensure!(values.len() >= 3, "{what} has no complete coordinate");
    let mut out = [0.; 3];
    for i in 0..3 {
        out[i] = values[i]
            .as_f64()
            .filter(|v| v.is_finite())
            .with_context(|| format!("{what} coordinate"))?;
    }
    Ok(out)
}
impl Placement {
    pub fn read(path: &Path, part: &str) -> Result<Self> {
        Self::from_value(
            &serde_json::from_slice(
                &fs::read(path).with_context(|| format!("reading {}", path.display()))?,
            )?,
            part,
        )
    }
    pub fn from_value(report: &Value, part: &str) -> Result<Self> {
        let row = report["parts"]
            .as_array()
            .context("print report parts")?
            .iter()
            .find(|row| row["name"].as_str().is_some_and(|name| name.contains(part)))
            .with_context(|| format!("no print part matches {part:?}"))?;
        let transform = row["build_transform"]
            .as_array()
            .context("part build_transform")?;
        ensure!(
            transform.len() >= 9,
            "part build transform has no complete rotation"
        );
        let mut m = [[0.; 3]; 3];
        for i in 0..3 {
            for j in 0..3 {
                m[i][j] = transform[i * 3 + j]
                    .as_f64()
                    .filter(|v| v.is_finite())
                    .context("part rotation number")?;
            }
        }
        Ok(Self {
            name: row["name"].as_str().context("print part name")?.into(),
            identify_id: row["identify_id"].as_i64(),
            member: row["member"].as_str().map(str::to_owned),
            object_id: row["object_id"].as_i64(),
            m,
            t: vector(&row["plate_translation_mm"], "plate translation")?,
            center: vector(&row["source_center_mm"], "source centre")?,
        })
    }
    pub fn to_cad(&self, p: [f64; 3]) -> [f64; 3] {
        std::array::from_fn(|i| {
            self.center[i]
                + (0..3)
                    .map(|j| (p[j] - self.t[j]) * self.m[i][j])
                    .sum::<f64>()
        })
    }
    pub fn to_plate(&self, p: [f64; 3]) -> [f64; 3] {
        std::array::from_fn(|i| {
            self.t[i]
                + (0..3)
                    .map(|j| (p[j] - self.center[j]) * self.m[j][i])
                    .sum::<f64>()
        })
    }
    fn normalized_to_plate(&self, p: [f64; 3]) -> [f64; 3] {
        std::array::from_fn(|i| self.t[i] + (0..3).map(|j| p[j] * self.m[j][i]).sum::<f64>())
    }
}

pub fn enforcer_triangles(project: &Path, placement: &Placement) -> Result<Vec<[[f64; 3]; 3]>> {
    let mut archive = zip::ZipArchive::new(
        fs::File::open(project).with_context(|| format!("opening {}", project.display()))?,
    )?;
    let mut members = BTreeSet::new();
    if let Some(member) = placement
        .member
        .as_ref()
        .filter(|member| !member.is_empty())
    {
        members.insert(member.trim_start_matches('/').to_owned());
    }
    if members.is_empty() {
        if let Some(id) = placement.object_id {
            let mut model = String::new();
            archive
                .by_name("3D/3dmodel.model")?
                .read_to_string(&mut model)?;
            let model = xml::parse(&model)?;
            if let Some(object) = model.descendants().into_iter().find(|node| {
                node.local() == "object"
                    && node.attribute("id").and_then(|s| s.parse::<i64>().ok()) == Some(id)
            }) {
                for component in object
                    .descendants()
                    .into_iter()
                    .filter(|node| node.local() == "component")
                {
                    for (key, value) in &component.attributes {
                        if key.rsplit(':').next() == Some("path") {
                            members.insert(value.trim_start_matches('/').into());
                        }
                    }
                }
            }
        }
    }
    let mut triangles = Vec::new();
    for i in 0..archive.len() {
        let mut member = archive.by_index(i)?;
        let name = member.name()?;
        if !members.contains(name.as_ref()) {
            continue;
        }
        let mut text = String::new();
        member.read_to_string(&mut text)?;
        let model = xml::parse(&text)?;
        for mesh in std::iter::once(&model)
            .chain(model.descendants())
            .filter(|node| node.local() == "mesh")
        {
            let mut vertices = Vec::new();
            for vertex in mesh
                .descendants()
                .into_iter()
                .filter(|node| node.local() == "vertex")
            {
                let mut p = [0.; 3];
                for (i, key) in ["x", "y", "z"].iter().enumerate() {
                    p[i] = vertex
                        .attribute(key)
                        .with_context(|| format!("paint vertex {key}"))?
                        .parse::<f64>()?;
                }
                vertices.push(placement.normalized_to_plate(p));
            }
            for triangle in mesh.descendants().into_iter().filter(|node| {
                node.local() == "triangle" && node.attribute("paint_seam") == Some("4")
            }) {
                let mut points = [[0.; 3]; 3];
                for (i, key) in ["v1", "v2", "v3"].iter().enumerate() {
                    let index = triangle
                        .attribute(key)
                        .context("paint triangle index")?
                        .parse::<usize>()?;
                    points[i] = *vertices
                        .get(index)
                        .context("paint triangle references a missing vertex")?;
                }
                triangles.push(points);
            }
        }
    }
    Ok(triangles)
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Seam {
    pub layer: usize,
    pub print_z: f64,
    pub layer_h: Option<f64>,
    pub gcode_line: usize,
    pub closed: bool,
    pub perimeter_mm: f64,
    pub lateral_mm: f64,
    pub arc_from_target_mm: f64,
    pub start_plate: [f64; 3],
    pub end_plate: [f64; 3],
    pub target_plate: [f64; 3],
    pub start_normal: [f64; 3],
    pub start_cad: [f64; 3],
    pub target_cad: [f64; 3],
    pub centroid_plate: [f64; 2],
    #[serde(skip_serializing_if = "Option::is_none")]
    pub enforcer_mm: Option<f64>,
}
pub fn measure_runs(
    runs: &[Run],
    placement: &Placement,
    toward: [f64; 3],
    enforcers: &[[[f64; 3]; 3]],
) -> Vec<Seam> {
    exterior_loops(runs)
        .into_iter()
        .map(|lp| {
            let (run, lap) = (lp.run, lp.lap);
            let mut lengths = vec![0.];
            for points in lap.windows(2) {
                lengths.push(lengths.last().unwrap() + distance_xy(points[0], points[1]));
            }
            let perimeter = lengths.last().unwrap() + distance_xy(*lap.last().unwrap(), lap[0]);
            let mut crossings = Vec::new();
            for i in 0..lap.len() {
                let j = (i + 1) % lap.len();
                let (a, b) = (placement.to_cad(lap[i])[0], placement.to_cad(lap[j])[0]);
                if a * b <= 0. && a != b {
                    let fraction = a / (a - b);
                    let point = add(lap[i], scale(sub(lap[j], lap[i]), fraction));
                    let end = if j == 0 { perimeter } else { lengths[j] };
                    crossings.push((point, lengths[i] + fraction * (end - lengths[i])));
                }
            }
            let (target, target_arc) = crossings
                .into_iter()
                .reduce(|a, b| {
                    if dot(placement.to_cad(b.0), toward) > dot(placement.to_cad(a.0), toward) {
                        b
                    } else {
                        a
                    }
                })
                .unwrap_or_else(|| {
                    let i = (0..lap.len())
                        .reduce(|a, b| {
                            if dot(placement.to_cad(lap[b]), toward)
                                > dot(placement.to_cad(lap[a]), toward)
                            {
                                b
                            } else {
                                a
                            }
                        })
                        .unwrap();
                    (lap[i], lengths[i])
                });
            let mut offset = (-target_arc).rem_euclid(perimeter);
            if offset > perimeter / 2. {
                offset -= perimeter;
            }
            let start = run.pts[0];
            let enforcer_mm = if enforcers.is_empty() {
                None
            } else {
                let p = [
                    target[0],
                    target[1],
                    run.z - run.h.filter(|v| *v != 0.).unwrap_or(0.2) / 2.,
                ];
                Some(
                    enforcers
                        .iter()
                        .map(|triangle| {
                            review::point_triangle(p, triangle[0], triangle[1], triangle[2])
                        })
                        .fold(f64::INFINITY, f64::min),
                )
            };
            Seam {
                layer: (run.layer + 1) as usize,
                print_z: run.z,
                layer_h: run.h,
                gcode_line: run.line,
                closed: lp.closed,
                perimeter_mm: perimeter,
                lateral_mm: placement.to_cad(start)[0],
                arc_from_target_mm: offset,
                start_plate: start,
                end_plate: *run.pts.last().unwrap(),
                target_plate: target,
                start_normal: start_normal(&run.pts),
                start_cad: placement.to_cad(start),
                target_cad: placement.to_cad(target),
                centroid_plate: lp.centroid,
                enforcer_mm,
            }
        })
        .collect()
}
pub fn measure(
    slice: &Path,
    placement: &Placement,
    project: Option<&Path>,
    toward: [f64; 3],
) -> Result<Vec<Seam>> {
    let text = slice_text(slice, 1)?;
    let runs = read_runs(&text, object_in(&text, placement.identify_id), &OUTER_WALLS)?;
    let enforcers = project
        .map(|path| enforcer_triangles(path, placement))
        .transpose()?
        .unwrap_or_default();
    Ok(measure_runs(&runs, placement, toward, &enforcers))
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Speed {
    pub layer: usize,
    pub print_z: f64,
    pub point_plate: [f64; 3],
    pub arriving_mm_s: f64,
    pub leaving_mm_s: f64,
    pub arriving_line: usize,
    pub labelled_overhang: bool,
    pub loop_min_mm_s: f64,
    pub loop_max_mm_s: f64,
}
pub fn layer_range(text: &str) -> Result<RangeInclusive<usize>> {
    let (first, last) = text.split_once('-').unwrap_or((text, text));
    let first = first.parse::<usize>().context("first layer")?;
    let last = last.parse::<usize>().context("last layer")?;
    ensure!(
        first > 0 && last >= first,
        "layer range must run forward from a positive layer"
    );
    Ok(first..=last)
}
pub fn probe_runs(
    runs: &[Run],
    at: &str,
    layers: Option<&RangeInclusive<usize>>,
) -> Result<Vec<Speed>> {
    let direction = match at {
        "leftmost" => Some((0, -1.)),
        "rightmost" => Some((0, 1.)),
        "front" => Some((1, -1.)),
        "back" => Some((1, 1.)),
        _ => None,
    };
    let xy = if direction.is_none() {
        let values = parse_coordinates(at, 2)?;
        Some([values[0], values[1]])
    } else {
        None
    };
    let mut rows = Vec::new();
    for lp in exterior_loops(runs) {
        let run = lp.run;
        let layer = (run.layer + 1) as usize;
        if layers.is_some_and(|layers| !layers.contains(&layer)) {
            continue;
        }
        let index = (1..run.pts.len())
            .reduce(|a, b| {
                let score = |i: usize| {
                    if let Some((axis, sign)) = direction {
                        sign * run.pts[i][axis]
                    } else {
                        let xy = xy.unwrap();
                        -(run.pts[i][0] - xy[0]).hypot(run.pts[i][1] - xy[1])
                    }
                };
                if score(b) > score(a) { b } else { a }
            })
            .context("outer wall has no moves")?;
        let leaving = index.min(run.feed.len() - 1);
        rows.push(Speed {
            layer,
            print_z: run.z,
            point_plate: run.pts[index].map(|v| rounded(v, 3)),
            arriving_mm_s: rounded(run.feed[index - 1], 2),
            leaving_mm_s: rounded(run.feed[leaving], 2),
            arriving_line: run.lines[index - 1],
            labelled_overhang: run.overhang[index - 1],
            loop_min_mm_s: rounded(run.feed.iter().copied().fold(f64::INFINITY, f64::min), 2),
            loop_max_mm_s: rounded(
                run.feed.iter().copied().fold(f64::NEG_INFINITY, f64::max),
                2,
            ),
        });
    }
    Ok(rows)
}
pub fn probe(
    slice: &Path,
    at: &str,
    layers: Option<&RangeInclusive<usize>>,
    object_id: Option<i64>,
) -> Result<Vec<Speed>> {
    let runs = read_runs(&slice_text(slice, 1)?, object_id, &OUTER_WALLS)?;
    probe_runs(&runs, at, layers)
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Zone {
    pub layers: [usize; 2],
    pub print_z_mm: [f64; 2],
    pub cad_z_mm: [f64; 2],
    pub peak_lateral_mm: f64,
    pub peak_print_z_mm: f64,
    pub peak_gcode_line: usize,
}
pub fn zones(rows: &[Seam], tolerance: f64) -> Vec<Zone> {
    let mut out = Vec::new();
    let mut current = Vec::<&Seam>::new();
    for row in rows.iter().map(Some).chain([None]) {
        if let Some(row) = row.filter(|row| row.lateral_mm.abs() > tolerance) {
            current.push(row);
            continue;
        }
        if let (Some(first), Some(last)) = (current.first(), current.last()) {
            let peak = current
                .iter()
                .copied()
                .reduce(|a, b| {
                    if b.lateral_mm.abs() > a.lateral_mm.abs() {
                        b
                    } else {
                        a
                    }
                })
                .unwrap();
            out.push(Zone {
                layers: [first.layer, last.layer],
                print_z_mm: [first.print_z, last.print_z],
                cad_z_mm: [
                    rounded(first.target_cad[2], 2),
                    rounded(last.target_cad[2], 2),
                ],
                peak_lateral_mm: rounded(peak.lateral_mm, 3),
                peak_print_z_mm: peak.print_z,
                peak_gcode_line: peak.gcode_line,
            });
        }
        current.clear();
    }
    out
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Band {
    pub print_z_mm: [f64; 2],
    pub layers: usize,
    pub mean_lateral_mm: f64,
    pub max_abs_lateral_mm: f64,
}
pub fn profile(rows: &[Seam], band: f64) -> Vec<Band> {
    let mut groups = BTreeMap::<i64, Vec<&Seam>>::new();
    for row in rows {
        groups
            .entry((row.print_z / band).floor() as i64)
            .or_default()
            .push(row);
    }
    groups
        .into_iter()
        .map(|(key, rows)| Band {
            print_z_mm: [key as f64 * band, (key + 1) as f64 * band],
            layers: rows.len(),
            mean_lateral_mm: rounded(
                rows.iter().map(|row| row.lateral_mm).sum::<f64>() / rows.len() as f64,
                3,
            ),
            max_abs_lateral_mm: rounded(
                rows.iter()
                    .map(|row| row.lateral_mm.abs())
                    .fold(0., f64::max),
                3,
            ),
        })
        .collect()
}
pub(crate) fn parse_coordinates(text: &str, count: usize) -> Result<Vec<f64>> {
    let values = text
        .split(',')
        .map(|value| value.trim().parse::<f64>().context("coordinate"))
        .collect::<Result<Vec<_>>>()?;
    ensure!(
        values.len() == count && values.iter().all(|v| v.is_finite()),
        "expected {count} finite comma-separated coordinates"
    );
    Ok(values)
}

#[derive(Parser)]
#[command(
    name = "hsm-gcode",
    about = "Read commanded seams and speeds from an existing slice"
)]
struct Command {
    #[command(subcommand)]
    mode: Mode,
}
#[derive(Subcommand)]
enum Mode {
    Seams(Seams),
    #[command(alias = "speed")]
    Speeds(Speeds),
    View(view::Options),
}
#[derive(Args)]
struct Seams {
    slice: PathBuf,
    print_json: PathBuf,
    #[arg(long)]
    part: String,
    #[arg(long)]
    project: Option<PathBuf>,
    #[arg(long, default_value = "0,1,0", allow_hyphen_values = true)]
    toward: String,
    #[arg(long, default_value_t = 1.0)]
    tolerance: f64,
    #[arg(long)]
    csv: Option<PathBuf>,
    #[arg(long)]
    json: Option<PathBuf>,
}
#[derive(Args)]
struct Speeds {
    slice: PathBuf,
    #[arg(long, allow_hyphen_values = true)]
    at: String,
    #[arg(long)]
    layers: Option<String>,
    #[arg(long)]
    object: Option<i64>,
    #[arg(long)]
    json: Option<PathBuf>,
}
fn save_json(path: &Path, value: &impl Serialize) -> Result<()> {
    fs::write(path, serde_json::to_string_pretty(value)? + "\n")
        .with_context(|| format!("writing {}", path.display()))
}
fn seams_cli(args: Seams) -> Result<i32> {
    ensure!(
        args.tolerance.is_finite() && args.tolerance >= 0.,
        "seam tolerance must be finite and nonnegative"
    );
    let placement = Placement::read(&args.print_json, &args.part)?;
    let toward = parse_coordinates(&args.toward, 3)?.try_into().unwrap();
    let rows = measure(&args.slice, &placement, args.project.as_deref(), toward)?;
    ensure!(
        !rows.is_empty(),
        "no exterior loops for {} in {}",
        placement.name,
        args.slice.display()
    );
    let zones = zones(&rows, args.tolerance);
    let bands = profile(&rows, 10.);
    let maximum = rounded(
        rows.iter()
            .map(|row| row.lateral_mm.abs())
            .fold(0., f64::max),
        3,
    );
    let open = rows.iter().filter(|row| !row.closed).count();
    let summary = json!({"slice":args.slice,"part":placement.name,"layers":rows.len(),"open_loops":open,"tolerance_mm":args.tolerance,"max_abs_lateral_mm":maximum,"zones":zones,"profile":bands});
    println!(
        "{}: {} layers, {open} open, largest offset {maximum} mm",
        placement.name,
        rows.len()
    );
    println!(
        "{:>14} {:>6} {:>7} {:>9}",
        "print Z band", "layers", "mean", "max |off|"
    );
    for band in &bands {
        println!(
            "{:6.0}-{:<6.0} {:6} {:7.2} {:9.2}",
            band.print_z_mm[0],
            band.print_z_mm[1],
            band.layers,
            band.mean_lateral_mm,
            band.max_abs_lateral_mm
        );
    }
    for zone in &zones {
        println!(
            "over {} mm: layers {}-{}, print Z {}-{}, CAD Z {}-{}, peak {} mm at print Z {} (G-code line {})",
            args.tolerance,
            zone.layers[0],
            zone.layers[1],
            zone.print_z_mm[0],
            zone.print_z_mm[1],
            zone.cad_z_mm[0],
            zone.cad_z_mm[1],
            zone.peak_lateral_mm,
            zone.peak_print_z_mm,
            zone.peak_gcode_line
        );
    }
    if let Some(path) = args.json {
        save_json(&path, &summary)?;
    }
    if let Some(path) = args.csv {
        let mut out = fs::File::create(&path)?;
        writeln!(
            out,
            "layer,print_z,layer_h,gcode_line,closed,perimeter_mm,lateral_mm,arc_from_target_mm,start_cad_x,start_cad_y,start_cad_z,target_cad_y,target_cad_z,enforcer_mm"
        )?;
        for row in rows {
            let fields = vec![
                row.layer.to_string(),
                row.print_z.to_string(),
                row.layer_h.map(|v| v.to_string()).unwrap_or_default(),
                row.gcode_line.to_string(),
                usize::from(row.closed).to_string(),
                rounded(row.perimeter_mm, 3).to_string(),
                rounded(row.lateral_mm, 3).to_string(),
                rounded(row.arc_from_target_mm, 3).to_string(),
                rounded(row.start_cad[0], 3).to_string(),
                rounded(row.start_cad[1], 3).to_string(),
                rounded(row.start_cad[2], 3).to_string(),
                rounded(row.target_cad[1], 3).to_string(),
                rounded(row.target_cad[2], 3).to_string(),
                row.enforcer_mm
                    .map(|v| rounded(v, 3).to_string())
                    .unwrap_or_default(),
            ];
            writeln!(out, "{}", fields.join(","))?;
        }
    }
    Ok(0)
}
fn speeds_cli(args: Speeds) -> Result<i32> {
    let layers = args.layers.as_deref().map(layer_range).transpose()?;
    let rows = probe(&args.slice, &args.at, layers.as_ref(), args.object)?;
    println!(
        "{:>5} {:>8} {:>24} {:>7} {:>7} {:>8} {:>8} {:>12}",
        "layer", "print Z", "point (plate mm)", "arrive", "leave", "line", "overhang", "loop range"
    );
    for row in &rows {
        let [x, y, z] = row.point_plate;
        let point = format!("{x:.2}, {y:.2}, {z:.2}");
        println!(
            "{:5} {:8.2} {point:>24} {:7.2} {:7.2} {:8} {:>8} {:5.1}-{:<5.1}",
            row.layer,
            row.print_z,
            row.arriving_mm_s,
            row.leaving_mm_s,
            row.arriving_line,
            row.labelled_overhang,
            row.loop_min_mm_s,
            row.loop_max_mm_s
        );
    }
    if let Some(path) = args.json {
        save_json(&path, &rows)?;
    }
    Ok(0)
}
pub fn cli(args: &[String]) -> Result<i32> {
    let command = match Command::try_parse_from(
        std::iter::once("hsm-gcode".into()).chain(args.iter().cloned()),
    ) {
        Ok(command) => command,
        Err(error) => {
            let status = error.exit_code();
            error.print()?;
            return Ok(status);
        }
    };
    match command.mode {
        Mode::Seams(args) => seams_cli(args),
        Mode::Speeds(args) => speeds_cli(args),
        Mode::View(args) => view::run(args),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    struct Scratch(PathBuf);
    impl Scratch {
        fn new() -> Result<Self> {
            let parent = Path::new(env!("CARGO_MANIFEST_DIR"))
                .ancestors()
                .nth(3)
                .unwrap()
                .join(".cache/runs");
            fs::create_dir_all(&parent)?;
            let path = parent.join(format!(
                "gcode-fixture-{}-{}",
                std::process::id(),
                std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)?
                    .as_nanos()
            ));
            fs::create_dir(&path)?;
            Ok(Self(path))
        }
    }
    impl Drop for Scratch {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }
    fn placement() -> Placement {
        Placement {
            name: "part".into(),
            identify_id: Some(7),
            member: None,
            object_id: None,
            m: [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]],
            t: [0.; 3],
            center: [0.; 3],
        }
    }
    fn square() -> String {
        "M83\n; Z_HEIGHT: 0.2\n; LAYER_HEIGHT: 0.2\n; OBJECT_ID: 7\n; FEATURE: Outer wall\nG1 X-2 Y-2 Z0.1 F600\nG1 X2 Y-2 E1 Z0.15\nG1 F1200\nM204 S1000\n; FEATURE: Overhang wall\nG1 X2 Y2 E1 Z0.2\nG1 X-2 Y2 E0\nG1 X-2 Y-2 E1\nG1 X-1.999 Y-2\nG1 X-1.8 Y-2 E0\nG1 E-1\n".into()
    }
    #[test]
    fn scarf_runs_keep_zero_e_hops_modal_feed_and_source_lines() -> Result<()> {
        let text = square();
        let runs = read_runs(&text, Some(7), &OUTER_WALLS)?;
        assert_eq!(runs.len(), 1);
        let run = &runs[0];
        assert_eq!(run.pts.len(), 7);
        assert_eq!(run.feed, vec![10., 20., 20., 20., 20., 20.]);
        assert_eq!(run.lines[0], 7);
        assert_eq!(run.line, 7);
        assert_eq!(run.pts[1][2], 0.15);
        assert!(run.overhang[1]);
        assert_eq!(run.end_line, 15);
        assert_eq!(object_in(&text, Some(7)), Some(7));
        assert_eq!(object_in(&text, Some(70)), None);
        Ok(())
    }
    #[test]
    fn geometry_selected_speed_observes_feed_only_change() -> Result<()> {
        let runs = read_runs(&square(), Some(7), &OUTER_WALLS)?;
        let rows = probe_runs(&runs, "rightmost", None)?;
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0].arriving_mm_s, 10.);
        assert_eq!(rows[0].leaving_mm_s, 20.);
        assert_eq!(rows[0].loop_min_mm_s, 10.);
        assert_eq!(rows[0].loop_max_mm_s, 20.);
        assert_eq!(rows[0].arriving_line, 7);
        assert!(probe_runs(&runs, "missing", None).is_err());
        Ok(())
    }
    #[test]
    fn exterior_uses_area_and_seam_uses_current_contour_in_cad_frame() -> Result<()> {
        let mut runs = read_runs(&square(), Some(7), &OUTER_WALLS)?;
        let mut hole = runs[0].clone();
        for point in &mut hole.pts {
            point[0] /= 4.;
            point[1] /= 4.;
        }
        runs.push(hole);
        let loops = exterior_loops(&runs);
        assert_eq!(loops.len(), 1);
        assert_eq!(loops[0].area, 16.);
        let rows = measure_runs(&runs, &placement(), [0., 1., 0.], &[]);
        assert_eq!(rows[0].lateral_mm, -2.);
        assert!((rows[0].target_cad[0]).abs() < 1e-9);
        assert_eq!(rows[0].target_cad[1], 2.);
        assert_eq!(rows[0].arc_from_target_mm, 6.);
        assert!(rows[0].closed);
        assert_eq!(rows[0].perimeter_mm, 16.);
        assert_eq!(zones(&rows, 1.).len(), 1);
        Ok(())
    }
    #[test]
    fn absolute_relative_motion_and_arc_z_interpolation() -> Result<()> {
        let text = "G90\nM82\nG92 X1 Y0 Z0 E10\n; Z_HEIGHT: 0.2\n; OBJECT_ID: 7\n; FEATURE: Outer wall\nG3 X0 Y1 Z0.2 I-1 J0 E11 F600\nG91\nG1 X-1 Y-1 Z0.1 E12\nG90\nG1 X1 Y0 E13\nG1 E12\nG1 X2 Y0\n";
        let runs = read_runs(text, Some(7), &OUTER_WALLS)?;
        assert_eq!(runs.len(), 1);
        let run = &runs[0];
        assert!(run.pts.len() > 5);
        assert_eq!(run.pts[0], [1., 0., 0.]);
        assert!(run.pts.iter().any(|p| p[2] > 0. && p[2] < 0.2));
        assert!((run.pts[run.pts.len() - 2][2] - 0.3).abs() < 1e-9);
        assert_eq!(run.feed[0], 10.);
        Ok(())
    }
    #[test]
    fn placement_round_trip_and_paint_distance_keep_selected_part_frame() -> Result<()> {
        let report = json!({"parts":[{"name":"target","identify_id":7,"member":"/3D/selected.model","object_id":9,"build_transform":[1,0,0,0,0,-1,0,1,0,0,0,0],"plate_translation_mm":[100,90,2],"source_center_mm":[5,6,7]}]});
        let placement = Placement::from_value(&report, "target")?;
        let p = [8., 4., 3.];
        let roundtrip = placement.to_cad(placement.to_plate(p));
        for i in 0..3 {
            assert!((p[i] - roundtrip[i]).abs() < 1e-9);
        }
        assert_eq!(placement.normalized_to_plate([0., 0., 0.]), placement.t);
        let runs = read_runs(&square(), Some(7), &OUTER_WALLS)?;
        let rows = measure_runs(
            &runs,
            &super::tests::placement(),
            [0., 1., 0.],
            &[[[-2., 2., 0.1], [2., 2., 0.1], [0., 3., 0.1]]],
        );
        assert!(rows[0].enforcer_mm.unwrap() < 1e-9);
        Ok(())
    }
    #[test]
    fn selected_3mf_member_and_component_fallback_exclude_other_objects_paint() -> Result<()> {
        let scratch = Scratch::new()?;
        let path = scratch.0.join("project.3mf");
        let mut archive = zip::ZipWriter::new(fs::File::create(&path)?);
        let main = "<model xmlns:p='urn:production'><resources><object id='9'><components><component p:path='/3D/selected.model' objectid='1'/></components></object><object id='10'><components><component p:path='/3D/other.model' objectid='2'/></components></object></resources></model>";
        let selected = "<model><resources><object id='1'><mesh><vertices><vertex x='0' y='0' z='0'/><vertex x='1' y='0' z='0'/><vertex x='0' y='1' z='0'/></vertices><triangles><triangle v1='0' v2='1' v3='2' paint_seam='4'/><triangle v1='0' v2='2' v3='1' paint_seam='0'/></triangles></mesh></object></resources></model>";
        let other = selected.replace("x='0'", "x='100'");
        for (name, text) in [
            ("3D/3dmodel.model", main),
            ("3D/selected.model", selected),
            ("3D/other.model", other.as_str()),
        ] {
            archive.start_file(name, hsm_print_prep::project::options())?;
            archive.write_all(text.as_bytes())?;
        }
        archive.finish()?;
        let mut selected = placement();
        selected.member = Some("/3D/selected.model".into());
        selected.object_id = Some(9);
        selected.t = [100., 90., 2.];
        selected.center = [50., 60., 70.];
        let direct = enforcer_triangles(&path, &selected)?;
        assert_eq!(direct.len(), 1);
        assert_eq!(
            direct[0],
            [[100., 90., 2.], [101., 90., 2.], [100., 91., 2.]]
        );
        selected.member = None;
        assert_eq!(enforcer_triangles(&path, &selected)?, direct);
        selected.object_id = None;
        assert!(enforcer_triangles(&path, &selected)?.is_empty());
        Ok(())
    }
    #[test]
    fn plain_and_archived_slice_inputs_keep_plate_selection() -> Result<()> {
        let scratch = Scratch::new()?;
        let plain = scratch.0.join("part.gcode");
        let text = square();
        fs::write(&plain, &text)?;
        assert_eq!(slice_text(&plain, 1)?, text);
        let path = scratch.0.join("part.gcode.3mf");
        let mut archive = zip::ZipWriter::new(fs::File::create(&path)?);
        for (name, bytes) in [
            ("Metadata/plate_1.gcode", text.as_bytes()),
            ("Metadata/plate_2.gcode", b"; Z_HEIGHT: 0.4\n".as_slice()),
        ] {
            archive.start_file(name, hsm_print_prep::project::options())?;
            archive.write_all(bytes)?;
        }
        archive.finish()?;
        assert_eq!(slice_text(&path, 1)?, text);
        assert_eq!(slice_text(&path, 2)?, "; Z_HEIGHT: 0.4\n");
        Ok(())
    }
}
