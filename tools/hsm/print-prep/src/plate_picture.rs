//! A plate as the Parts page pictures it: the plate's printable volumes, posed on the bed as its
//! Bambu project places them and tinted by their filaments, standing on a gridded bed, written as
//! the payload `hsm render` draws.

use crate::{faucet::members, xml};
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use std::collections::{BTreeMap, HashMap, HashSet};
use std::path::Path;

const MODEL: &str = "3D/3dmodel.model";
const LAYOUT: &str = "Metadata/model_settings.config";
const SETTINGS: &str = "Metadata/project_settings.config";
/// The 3MF production extension, whose `path` puts a component's object in another model part.
const PRODUCTION: &str = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06";
const MESH_PAYLOAD_VERSION: u32 = 3;

/// The bed: a slab under the build surface, ruled at an even pitch with raised lines.
const BED_COLOR: &str = "#8195ac";
const BED_DEPTH: f64 = 5.0;
const GRID_COLOR: &str = "#9eaec0";
const GRID_PITCH: f64 = 20.0;
const GRID_HALF_WIDTH: f64 = 0.22;
const GRID_RISE: f64 = 0.05;
/// Bambu Studio lays a project's plates out a bed and its gutter apart, in units of the bed.
const PLATE_PITCH: f64 = 1.2;
/// A clear filament draws in a pale tint, and a black one in a slate that still shows its form.
const CLEAR: &str = "#a9c3cf";
const SLATE: &str = "#344051";
const BLACKS: [&str; 3] = ["#000000", "#161616", "#111111"];

/// The picture `hsm render` draws of the payload: an orthographic three-quarter view from the
/// front right, on a transparent ground the Parts tile shows through.
pub fn job(payload: &Path, out: &Path) -> Value {
    json!({
        "payload": payload, "out": out, "size": "640x560",
        "cam": [0.65, -1, 1.25], "transparent": true, "ortho": true,
        "margin": 1.54, "ground": false, "fog": false,
        "materials": [
            {"names": ["bed", "bed-grid-*"], "roughness": 0.87, "metalness": 0.10},
            {"names": ["part-*"], "roughness": 0.55, "metalness": 0.02},
        ],
    })
}

/// A 3MF transform: three rows of the linear part, then the translation, for row vectors.
type Pose = [[f64; 3]; 4];
const IDENTITY: Pose = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, 0.0]];

fn transform(node: &xml::Element) -> Result<Pose> {
    let Some(text) = node.attribute("transform") else { return Ok(IDENTITY) };
    let values = text.split_whitespace().map(str::parse).collect::<Result<Vec<f64>, _>>()
        .with_context(|| format!("transform {text}"))?;
    ensure!(values.len() == 12, "transform {text} is not a 3MF transform");
    Ok(std::array::from_fn(|row| std::array::from_fn(|col| values[row * 3 + col])))
}

/// `inner` placed by `outer`, as a component's transform sits inside its object's.
fn compose(inner: &Pose, outer: &Pose) -> Pose {
    std::array::from_fn(|row| std::array::from_fn(|col| {
        (0..3).map(|k| inner[row][k] * outer[k][col]).sum::<f64>() + if row == 3 { outer[3][col] } else { 0.0 }
    }))
}

fn place(pose: &Pose, p: [f64; 3]) -> [f64; 3] {
    std::array::from_fn(|col| (0..3).map(|k| p[k] * pose[k][col]).sum::<f64>() + pose[3][col])
}

fn mirrors(m: &Pose) -> bool {
    m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]) < 0.0
}

fn metadata(node: &xml::Element) -> HashMap<&str, &str> {
    node.children_named("metadata").filter_map(|row| Some((row.attribute("key")?, row.attribute("value")?))).collect()
}

fn object<'a>(model: &'a xml::Element, id: &str) -> Result<&'a xml::Element> {
    model.child("resources").into_iter().flat_map(|r| r.children_named("object"))
        .find(|o| o.attribute("id") == Some(id)).with_context(|| format!("no object {id}"))
}

/// One printable volume in the bed's frame, with its filament's index, counted from one.
struct Solid {
    points: Vec<[f64; 3]>,
    triangles: Vec<[u32; 3]>,
    filament: usize,
}

/// The model parts a plate's objects are drawn from: the project's model and each model part a
/// component names by its production path.
struct Models {
    main: xml::Element,
    parts: BTreeMap<String, xml::Element>,
    path: Option<String>,
}

impl Models {
    fn read(files: &BTreeMap<String, Vec<u8>>) -> Result<Models> {
        let text = |name: &str| -> Result<String> {
            let bytes = files.get(name).with_context(|| format!("no {name}"))?;
            Ok(std::str::from_utf8(bytes).with_context(|| format!("{name} is not UTF-8"))?.to_string())
        };
        let main = xml::parse(&text(MODEL)?)?;
        let path = main.attributes.iter()
            .find(|(key, value)| key.starts_with("xmlns:") && value == PRODUCTION)
            .map(|(key, _)| format!("{}:path", &key["xmlns:".len()..]));
        let mut models = Models { main, parts: BTreeMap::new(), path };
        let mut pending = models.paths(&models.main);
        while let Some(name) = pending.pop() {
            if models.parts.contains_key(&name) {
                continue;
            }
            let part = xml::parse(&text(&name)?)?;
            pending.extend(models.paths(&part));
            models.parts.insert(name, part);
        }
        Ok(models)
    }

    /// The model part a component's object lives in, without its leading slash.
    fn path<'a>(&self, component: &'a xml::Element) -> Option<&'a str> {
        self.path.as_deref().and_then(|key| component.attribute(key)).map(|p| p.trim_start_matches('/'))
    }

    fn paths(&self, model: &xml::Element) -> Vec<String> {
        model.descendants().into_iter().filter(|e| e.local() == "component")
            .filter_map(|c| self.path(c).map(str::to_string)).collect()
    }

    /// Every printable mesh below `node`, posed by `pose`, as `parts` (the object's parts in the
    /// plate's settings) keep or drop it and assign its filament.
    fn walk(&self, node: &xml::Element, pose: &Pose, parts: &HashMap<&str, &xml::Element>, filament: &str,
            solids: &mut Vec<Solid>) -> Result<()> {
        if let Some(mesh) = node.child("mesh") {
            let points = mesh.child("vertices").context("a mesh without vertices")?.children.iter()
                .map(|vertex| -> Result<[f64; 3]> {
                    let mut p = [0.0; 3];
                    for (axis, value) in ["x", "y", "z"].iter().zip(&mut p) {
                        *value = vertex.attribute(axis).with_context(|| format!("a vertex without {axis}"))?.parse()?;
                    }
                    Ok(place(pose, p))
                })
                .collect::<Result<Vec<_>>>()?;
            let mut triangles = mesh.child("triangles").context("a mesh without triangles")?.children.iter()
                .map(|triangle| -> Result<[u32; 3]> {
                    let mut t = [0; 3];
                    for (key, index) in ["v1", "v2", "v3"].iter().zip(&mut t) {
                        *index = triangle.attribute(key).with_context(|| format!("a triangle without {key}"))?.parse()?;
                        ensure!((*index as usize) < points.len(), "a triangle names a missing vertex");
                    }
                    Ok(t)
                })
                .collect::<Result<Vec<_>>>()?;
            if mirrors(pose) {
                triangles.iter_mut().for_each(|t| t.reverse());
            }
            let filament = filament.parse().with_context(|| format!("filament {filament}"))?;
            ensure!(filament >= 1, "filament {filament} is not counted from one");
            solids.push(Solid { points, triangles, filament });
            return Ok(());
        }
        for component in node.child("components").into_iter().flat_map(|c| c.children_named("component")) {
            let volume = component.attribute("objectid").context("a component without an object")?;
            let part = parts.get(volume);
            // Modifiers, negative volumes and support blockers shape the slice, not the plate.
            if part.is_some_and(|part| part.attribute("subtype") != Some("normal_part")) {
                continue;
            }
            let source = match self.path(component) {
                Some(name) => self.parts.get(name).with_context(|| format!("no model part {name}"))?,
                None => &self.main,
            };
            let extruder = part.and_then(|part| metadata(part).get("extruder").copied()).unwrap_or(filament);
            self.walk(object(source, volume)?, &compose(&transform(component)?, pose), parts, extruder, solids)?;
        }
        Ok(())
    }
}

/// The bed's printable rectangle, its filaments' colours, and the plate's solids on that bed.
struct Plate {
    low: [f64; 2],
    high: [f64; 2],
    colors: Vec<String>,
    solids: Vec<Solid>,
}

/// Plate `number`, counted from one, of the project at `project`.
fn read(project: &Path, number: usize) -> Result<Plate> {
    let files = members(project)?;
    let layout = xml::parse(std::str::from_utf8(files.get(LAYOUT).with_context(|| format!("no {LAYOUT}"))?)?)?;
    let plates: Vec<_> = layout.children_named("plate").collect();
    ensure!(number >= 1 && number <= plates.len(), "{} has no plate {number}", project.display());
    let mut instances = HashSet::new();
    for instance in plates[number - 1].children_named("model_instance") {
        let row = metadata(instance);
        let id = row.get("object_id").context("a model instance without an object")?.to_string();
        instances.insert((id, row.get("instance_id").map_or(Ok(0), |n| n.parse::<usize>())?));
    }
    let objects: HashMap<&str, &xml::Element> =
        layout.children_named("object").filter_map(|o| Some((o.attribute("id")?, o))).collect();
    let settings: Value = serde_json::from_slice(files.get(SETTINGS).with_context(|| format!("no {SETTINGS}"))?)?;
    let (mut low, mut high) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
    for corner in settings["printable_area"].as_array().context("no printable area")? {
        let corner = corner.as_str().context("a printable area corner")?;
        let (x, y) = corner.split_once('x').with_context(|| format!("printable area corner {corner}"))?;
        for (axis, value) in [x, y].into_iter().enumerate() {
            let value: f64 = value.parse()?;
            low[axis] = low[axis].min(value);
            high[axis] = high[axis].max(value);
        }
    }
    let colors = settings["filament_colour"].as_array().context("no filament colours")?.iter()
        .map(|c| c.as_str().map(str::to_string).context("a filament colour"))
        .collect::<Result<Vec<_>>>()?;

    let models = Models::read(&files)?;
    let mut seen: HashMap<&str, usize> = HashMap::new();
    let mut solids = Vec::new();
    for item in models.main.child("build").into_iter().flat_map(|b| b.children_named("item")) {
        let id = item.attribute("objectid").context("a build item without an object")?;
        let serial = seen.entry(id).or_default();
        let instance = (id.to_string(), *serial);
        *serial += 1;
        if !instances.contains(&instance) || item.attribute("printable") == Some("0") {
            continue;
        }
        let config = objects.get(id).with_context(|| format!("no settings for object {id}"))?;
        let parts = config.children_named("part").filter_map(|p| Some((p.attribute("id")?, p))).collect();
        let filament = metadata(config).get("extruder").copied().unwrap_or("1");
        models.walk(object(&models.main, id)?, &transform(item)?, &parts, filament, &mut solids)?;
    }
    ensure!(!solids.is_empty(), "no printable geometry on plate {number}");

    // The other plates take whole beds and their gutters in Bambu Studio's layout. This plate's
    // frame is where its objects sit, whatever column of that grid it is in.
    if plates.len() > 1 {
        let (mut lo, mut hi) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
        for p in solids.iter().flat_map(|s| &s.points) {
            for axis in 0..2 {
                lo[axis] = lo[axis].min(p[axis]);
                hi[axis] = hi[axis].max(p[axis]);
            }
        }
        let origin: [f64; 2] = std::array::from_fn(|axis| {
            let pitch = (high[axis] - low[axis]) * PLATE_PITCH;
            (((lo[axis] + hi[axis]) / 2.0 - (high[axis] + low[axis]) / 2.0) / pitch).round_ties_even() * pitch
        });
        for p in solids.iter_mut().flat_map(|s| &mut s.points) {
            p[0] -= origin[0];
            p[1] -= origin[1];
        }
    }
    Ok(Plate { low, high, colors, solids })
}

fn slab(low: [f64; 3], high: [f64; 3]) -> (Vec<[f64; 3]>, Vec<[u32; 3]>) {
    let ([x, y, z], [w, d, h]) = (low, high);
    let corners = vec![[x, y, z], [w, y, z], [w, d, z], [x, d, z], [x, y, h], [w, y, h], [w, d, h], [x, d, h]];
    let sides = vec![[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4],
                     [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]];
    (corners, sides)
}

fn linear(color: &str) -> Result<[f64; 3]> {
    let mut rgb = [0.0; 3];
    for (i, channel) in rgb.iter_mut().enumerate() {
        let hex = color.get(1 + 2 * i..3 + 2 * i).with_context(|| format!("colour {color}"))?;
        let c = u8::from_str_radix(hex, 16).with_context(|| format!("colour {color}"))? as f64 / 255.0;
        *channel = if c <= 0.04045 { c / 12.92 } else { ((c + 0.055) / 1.055).powf(2.4) };
    }
    Ok(rgb)
}

fn surface(color: &str) -> &str {
    let rgb = color.get(..7).unwrap_or(color);
    if color.len() == 9 && color.ends_with("00") {
        CLEAR
    } else if BLACKS.contains(&rgb) {
        SLATE
    } else {
        rgb
    }
}

#[derive(Default)]
struct Payload {
    meshes: Vec<Value>,
    blob: Vec<u8>,
}

impl Payload {
    /// One array at the blob's end, as the payload locates it: its byte offset and its length.
    fn put(&mut self, words: impl Iterator<Item = [u8; 4]>) -> [usize; 2] {
        let offset = self.blob.len();
        self.blob.extend(words.flatten());
        [offset, (self.blob.len() - offset) / 4]
    }

    /// A mesh named `name`, shaded smooth across shared vertices or `flat` per triangle.
    fn add(&mut self, name: &str, points: &[[f64; 3]], triangles: &[[u32; 3]], color: &str, flat: bool) -> Result<()> {
        let sub = |a: [f64; 3], b: [f64; 3]| [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
        let faces: Vec<[f64; 3]> = triangles.iter().map(|t| {
            let [p, q, r] = t.map(|i| points[i as usize]);
            let (u, v) = (sub(q, p), sub(r, p));
            [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        }).collect();
        let (positions, indices, mut normals): (Vec<[f64; 3]>, Vec<u32>, Vec<[f64; 3]>) = if flat {
            (triangles.iter().flat_map(|t| t.map(|i| points[i as usize])).collect(),
             (0..3 * triangles.len() as u32).collect(),
             faces.iter().flat_map(|f| [*f; 3]).collect())
        } else {
            let mut normals = vec![[0.0; 3]; points.len()];
            for corner in 0..3 {
                for (t, f) in triangles.iter().zip(&faces) {
                    let n = &mut normals[t[corner] as usize];
                    (0..3).for_each(|axis| n[axis] += f[axis]);
                }
            }
            (points.to_vec(), triangles.iter().flatten().copied().collect(), normals)
        };
        for n in &mut normals {
            let length = (n[0] * n[0] + n[1] * n[1] + n[2] * n[2]).sqrt();
            if length > 0.0 {
                n.iter_mut().for_each(|c| *c /= length);
            }
        }
        let color = linear(color)?;
        let floats = |rows: &[[f64; 3]]| rows.iter().flatten().map(|&c| (c as f32).to_le_bytes()).collect::<Vec<_>>();
        let pos = self.put(floats(&positions).into_iter());
        let nrm = self.put(floats(&normals).into_iter());
        let idx = self.put(indices.iter().map(|i| i.to_le_bytes()));
        self.meshes.push(json!({"name": name, "color": color, "pos": pos, "nrm": nrm, "idx": idx, "fac": [0, 0]}));
        Ok(())
    }

    fn bytes(self) -> Result<Vec<u8>> {
        let mut header = serde_json::to_vec(&json!({"v": MESH_PAYLOAD_VERSION, "meshes": self.meshes}))?;
        header.resize(header.len().next_multiple_of(4), b' ');
        let mut out = (header.len() as u32).to_le_bytes().to_vec();
        out.extend(header);
        out.extend(self.blob);
        Ok(out)
    }
}

/// The payload of plate `number` of the project at `project`: the bed, its grid, and each
/// printable volume as `part-N`.
pub fn payload(project: &Path, number: usize) -> Result<Vec<u8>> {
    let plate = read(project, number)?;
    let ([x, y], [w, d]) = (plate.low, plate.high);
    let mut out = Payload::default();
    let (corners, sides) = slab([x, y, -BED_DEPTH], [w, d, 0.0]);
    out.add("bed", &corners, &sides, BED_COLOR, true)?;
    for (axis, start, end) in [("x", x, w), ("y", y, d)] {
        let first = start + GRID_PITCH;
        let count = ((end - first) / GRID_PITCH).ceil().max(0.0) as usize;
        for i in 0..count {
            let at = first + i as f64 * GRID_PITCH;
            let (lo, hi) = if axis == "x" {
                ([at - GRID_HALF_WIDTH, y, 0.0], [at + GRID_HALF_WIDTH, d, GRID_RISE])
            } else {
                ([x, at - GRID_HALF_WIDTH, 0.0], [w, at + GRID_HALF_WIDTH, GRID_RISE])
            };
            let (corners, sides) = slab(lo, hi);
            out.add(&format!("bed-grid-{axis}-{i}"), &corners, &sides, GRID_COLOR, true)?;
        }
    }
    for (i, solid) in plate.solids.iter().enumerate() {
        let color = plate.colors.get(solid.filament - 1).with_context(|| format!("no colour for filament {}", solid.filament))?;
        out.add(&format!("part-{i}"), &solid.points, &solid.triangles, surface(color), false)?;
    }
    out.bytes()
}
