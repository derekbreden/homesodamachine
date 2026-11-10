//! The detailed board model instances the vendor's colored geometry at the circuit's authored poses.
use crate::{
    circuit::{Cad, Circuit, Element},
    geometry,
};
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::{Plane, Profile, Solid, V3, v2, v3};
use serde_json::{Value, json};
use std::{
    collections::BTreeMap,
    fmt::Write as _,
    fs,
    path::{Path, PathBuf},
    process::Command,
    time::Instant,
};

#[derive(Clone)]
struct Mesh {
    positions: Vec<[f64; 3]>,
    triangles: Vec<[u32; 3]>,
    color: [f64; 3],
    normals: Option<Vec<[f32; 3]>>,
    color_is_linear: bool,
}

struct PinnedModels {
    manifest: Value,
    document: Value,
    binary: Vec<u8>,
}
impl PinnedModels {
    fn load(root: &Path) -> Result<Self> {
        use sha2::{Digest, Sha256};
        let directory = root.join("hardware/pcb/pcba");
        let manifest: Value =
            serde_json::from_slice(&fs::read(directory.join("vendor-models.json"))?)?;
        let bytes = fs::read(
            directory.join(
                manifest["mesh_source"]
                    .as_str()
                    .context("vendor source has no mesh path")?,
            ),
        )?;
        ensure!(
            format!("{:x}", Sha256::digest(&bytes))
                == manifest["mesh_sha256"].as_str().unwrap_or(""),
            "supplier mesh source differs from its provenance"
        );
        ensure!(
            bytes.len() >= 28 && &bytes[..4] == b"glTF",
            "supplier source is not GLB"
        );
        let json_length = u32::from_le_bytes(bytes[12..16].try_into()?) as usize;
        let document = serde_json::from_slice(
            bytes
                .get(20..20 + json_length)
                .context("truncated supplier JSON")?,
        )?;
        let binary = bytes
            .get(28 + json_length..)
            .context("truncated supplier mesh buffer")?
            .to_vec();
        Ok(Self {
            manifest,
            document,
            binary,
        })
    }
    fn parts(&self, url: &str) -> Result<Option<Vec<Mesh>>> {
        let Some(model) = self.manifest["models"].get(url) else {
            return Ok(None);
        };
        let node = model["node"]
            .as_u64()
            .context("supplier source has no node")? as usize;
        let mesh = self.document["nodes"][node]["mesh"]
            .as_u64()
            .context("supplier node has no mesh")? as usize;
        let mut parts = Vec::new();
        for primitive in self.document["meshes"][mesh]["primitives"]
            .as_array()
            .context("supplier mesh has no primitives")?
        {
            let vectors = |attribute: &str| -> Result<Vec<[f64; 3]>> {
                let index = primitive["attributes"][attribute]
                    .as_u64()
                    .context("missing supplier vector attribute")?
                    as usize;
                let accessor = &self.document["accessors"][index];
                let view = &self.document["bufferViews"][accessor["bufferView"]
                    .as_u64()
                    .context("attribute has no view")?
                    as usize];
                ensure!(
                    accessor["componentType"] == 5126 && accessor["type"] == "VEC3",
                    "invalid supplier vector type"
                );
                let start = view["byteOffset"].as_u64().unwrap_or(0) as usize
                    + accessor["byteOffset"].as_u64().unwrap_or(0) as usize;
                let stride = view["byteStride"].as_u64().unwrap_or(12) as usize;
                let count = accessor["count"]
                    .as_u64()
                    .context("attribute has no count")? as usize;
                (0..count)
                    .map(|i| {
                        let mut vector = [0.; 3];
                        for (k, value) in vector.iter_mut().enumerate() {
                            *value = f32::from_le_bytes(
                                self.binary
                                    .get(start + i * stride + k * 4..start + i * stride + k * 4 + 4)
                                    .context("truncated supplier vector")?
                                    .try_into()?,
                            ) as f64;
                        }
                        Ok(vector)
                    })
                    .collect()
            };
            let positions = vectors("POSITION")?
                .into_iter()
                .map(|p| p.map(|v| v * 1000.))
                .collect::<Vec<_>>();
            let normals = vectors("NORMAL")?
                .into_iter()
                .map(|p| p.map(|v| v as f32))
                .collect::<Vec<_>>();
            let index = primitive["indices"]
                .as_u64()
                .context("supplier primitive has no indices")? as usize;
            let accessor = &self.document["accessors"][index];
            let view = &self.document["bufferViews"][accessor["bufferView"]
                .as_u64()
                .context("indices have no view")?
                as usize];
            ensure!(
                accessor["componentType"] == 5125,
                "invalid supplier index type"
            );
            let start = view["byteOffset"].as_u64().unwrap_or(0) as usize
                + accessor["byteOffset"].as_u64().unwrap_or(0) as usize;
            let count = accessor["count"]
                .as_u64()
                .context("indices have no count")? as usize;
            ensure!(count % 3 == 0, "supplier primitive is not triangular");
            let mut triangles = Vec::new();
            for i in (0..count).step_by(3) {
                let mut triangle = [0; 3];
                for (k, value) in triangle.iter_mut().enumerate() {
                    *value = u32::from_le_bytes(
                        self.binary
                            .get(start + (i + k) * 4..start + (i + k) * 4 + 4)
                            .context("truncated supplier index")?
                            .try_into()?,
                    );
                }
                ensure!(
                    triangle.iter().all(|i| (*i as usize) < positions.len()),
                    "supplier index outside vertices"
                );
                triangles.push(triangle);
            }
            ensure!(
                normals.len() == positions.len(),
                "supplier normals differ from positions"
            );
            let material = primitive["material"]
                .as_u64()
                .context("supplier primitive has no material")? as usize;
            let color =
                &self.document["materials"][material]["pbrMetallicRoughness"]["baseColorFactor"];
            parts.push(Mesh {
                positions,
                triangles,
                color: [
                    color[0].as_f64().unwrap_or(0.7),
                    color[1].as_f64().unwrap_or(0.7),
                    color[2].as_f64().unwrap_or(0.7),
                ],
                normals: Some(normals),
                color_is_linear: true,
            });
        }
        Ok(Some(parts))
    }
    fn verify_step(&self, url: &str, source: &Path) -> Result<()> {
        use sha2::{Digest, Sha256};
        if let Some(model) = self.manifest["models"].get(url) {
            ensure!(
                format!("{:x}", Sha256::digest(fs::read(source)?))
                    == model["supplier_step_sha256"].as_str().unwrap_or(""),
                "supplier STEP differs from the pinned detailed model: {url}"
            );
        }
        Ok(())
    }
}
fn asset_name(url: &str) -> Result<String> {
    let file = url
        .split('?')
        .next()
        .unwrap_or(url)
        .rsplit('/')
        .next()
        .context("model URL has no filename")?;
    ensure!(
        !file.is_empty() && !file.contains(['\\', '\0']),
        "invalid model filename"
    );
    Ok(file.to_owned())
}
fn cached(url: &str, cache: &Path) -> Result<PathBuf> {
    let path = cache.join(asset_name(url)?);
    if fs::metadata(&path).is_ok_and(|m| m.len() > 0) {
        return Ok(path);
    }
    fs::create_dir_all(cache)?;
    let temp = path.with_extension(format!("download-{}", std::process::id()));
    let output = Command::new("curl")
        .args([
            "--fail",
            "--location",
            "--silent",
            "--show-error",
            "--max-time",
            "60",
            "--user-agent",
            "homesodamachine-board-3d/native",
            "--output",
        ])
        .arg(&temp)
        .arg(url)
        .output()?;
    if !output.status.success() {
        let _ = fs::remove_file(temp);
        bail!(
            "model download failed: {}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
    fs::rename(temp, &path)?;
    Ok(path)
}
fn parse_obj(path: &Path) -> Result<Vec<Mesh>> {
    let text = fs::read_to_string(path)?;
    let mut positions = vec![];
    let mut colors = BTreeMap::new();
    let mut material = String::new();
    let mut active = String::new();
    let mut faces = BTreeMap::<String, Vec<[u32; 3]>>::new();
    for line in text.lines() {
        let mut parts = line.split_whitespace();
        match parts.next() {
            Some("v") => {
                let values = parts
                    .take(3)
                    .map(str::parse::<f64>)
                    .collect::<std::result::Result<Vec<_>, _>>()?;
                ensure!(values.len() == 3, "OBJ vertex is incomplete");
                positions.push([values[0], values[1], values[2]]);
            }
            Some("newmtl") => material = parts.next().unwrap_or("").to_owned(),
            Some("Kd") => {
                let values = parts
                    .take(3)
                    .map(str::parse::<f64>)
                    .collect::<std::result::Result<Vec<_>, _>>()?;
                if values.len() == 3 {
                    colors.insert(material.clone(), [values[0], values[1], values[2]]);
                }
            }
            Some("usemtl") => active = parts.next().unwrap_or("").to_owned(),
            Some("f") => {
                let indices = parts
                    .map(|v| -> Result<u32> {
                        let index = v
                            .split('/')
                            .next()
                            .context("empty OBJ face index")?
                            .parse::<isize>()?;
                        let at = if index < 0 {
                            positions.len() as isize + index
                        } else {
                            index - 1
                        };
                        ensure!(
                            at >= 0 && (at as usize) < positions.len(),
                            "OBJ face index is outside vertices"
                        );
                        Ok(at as u32)
                    })
                    .collect::<Result<Vec<_>>>()?;
                ensure!(indices.len() >= 3, "OBJ face has too few vertices");
                let out = faces.entry(active.clone()).or_default();
                for i in 1..indices.len() - 1 {
                    out.push([indices[0], indices[i], indices[i + 1]]);
                }
            }
            _ => {}
        }
    }
    ensure!(
        !positions.is_empty() && !faces.is_empty(),
        "vendor OBJ contains no triangles"
    );
    Ok(faces
        .into_iter()
        .map(|(material, triangles)| {
            let mut used = BTreeMap::new();
            let mut vertices = vec![];
            let triangles = triangles
                .into_iter()
                .map(|triangle| {
                    triangle.map(|index| {
                        *used.entry(index).or_insert_with(|| {
                            let out = vertices.len() as u32;
                            vertices.push(positions[index as usize]);
                            out
                        })
                    })
                })
                .collect();
            Mesh {
                positions: vertices,
                triangles,
                color: colors.get(&material).copied().unwrap_or([0.7; 3]),
                normals: None,
                color_is_linear: false,
            }
        })
        .collect())
}
fn board(circuit: &Circuit, vias: bool) -> Result<Solid> {
    let board = circuit.board()?;
    let profile = if board.outline.len() >= 3 {
        Profile::polygon(
            &board
                .outline
                .iter()
                .map(|p| v2(p.x, p.y))
                .collect::<Vec<_>>(),
        )
    } else {
        Profile::polygon(&[
            v2(
                board.center.x - board.width / 2.0,
                board.center.y - board.height / 2.0,
            ),
            v2(
                board.center.x + board.width / 2.0,
                board.center.y - board.height / 2.0,
            ),
            v2(
                board.center.x + board.width / 2.0,
                board.center.y + board.height / 2.0,
            ),
            v2(
                board.center.x - board.width / 2.0,
                board.center.y + board.height / 2.0,
            ),
        ])
    };
    let slab = Plane::XY
        .offset(-board.thickness / 2.0)
        .extrude(&profile, board.thickness)?;
    let cut_height = board.thickness + 2.0;
    let mut cutters = vec![];
    for e in &circuit.elements {
        let hole = match e {
            Element::Hole(p) | Element::PlatedHole(p) => Some(p),
            Element::Via(p) if vias => Some(p),
            _ => None,
        };
        if let Some(p) = hole {
            if p.shape == "pill" || p.hole_shape == "pill" {
                let (w, h) = (
                    p.hole_width.context("slot has no hole width")?,
                    p.hole_height.context("slot has no hole height")?,
                );
                let width = w.min(h);
                let length = w.max(h);
                let half = (length - width) / 2.0;
                let mut shapes = vec![
                    Solid::cylinder(
                        v3(-half, 0.0, -cut_height / 2.0),
                        V3::Z,
                        width / 2.0,
                        cut_height,
                    )?,
                    Solid::cylinder(
                        v3(half, 0.0, -cut_height / 2.0),
                        V3::Z,
                        width / 2.0,
                        cut_height,
                    )?,
                ];
                if half > 0.0 {
                    shapes.push(Solid::cuboid(
                        v3(-half, -width / 2.0, -cut_height / 2.0),
                        v3(half, width / 2.0, cut_height / 2.0),
                    ));
                }
                let angle = if h >= w { 0.0 } else { 90.0 };
                cutters.push(
                    Solid::union_all(&shapes)?
                        .rotate(V3::ZERO, V3::Z, angle + p.ccw_rotation.unwrap_or(0.0))
                        .translate(v3(p.x, p.y, 0.0)),
                );
            } else {
                let diameter = p.hole_diameter.or(p.hole_width).unwrap_or(0.0);
                if diameter > 0.0 {
                    cutters.push(Solid::cylinder(
                        v3(p.x, p.y, -cut_height / 2.0),
                        V3::Z,
                        diameter / 2.0,
                        cut_height,
                    )?);
                }
            }
        }
    }
    slab.cut_all(&cutters)
}
fn board_mesh(board: &Solid) -> Mesh {
    Mesh {
        positions: board.verts().iter().map(|p| [p.x, p.y, p.z]).collect(),
        triangles: board.tris().to_vec(),
        color: [0.1, 0.48, 0.2],
        normals: None,
        color_is_linear: false,
    }
}

struct Placement {
    cad: Cad,
    bottom: bool,
    url: String,
    name: String,
}
fn placements(circuit: &Circuit) -> Result<Vec<Placement>> {
    let layers = circuit
        .elements
        .iter()
        .filter_map(|e| {
            if let Element::Component(c) = e {
                Some((c.pcb_component_id.as_str(), c.layer.as_str()))
            } else {
                None
            }
        })
        .collect::<BTreeMap<_, _>>();
    let names = circuit.names();
    circuit
        .elements
        .iter()
        .filter_map(|e| {
            if let Element::Cad(c) = e {
                if c.model_step_url.is_none() {
                    return None;
                }
                Some(
                    c.model_obj_url
                        .as_ref()
                        .context("vendor component has no OBJ model")
                        .map(|url| Placement {
                            cad: c.clone(),
                            bottom: layers
                                .get(c.pcb_component_id.as_str())
                                .is_some_and(|v| v.eq_ignore_ascii_case("bottom")),
                            url: url.clone(),
                            name: names
                                .get(&c.pcb_component_id)
                                .cloned()
                                .or_else(|| {
                                    circuit.elements.iter().find_map(|element| match element {
                                        Element::SourceComponent(source)
                                            if source.source_component_id
                                                == c.source_component_id =>
                                        {
                                            Some(source.name.clone())
                                        }
                                        _ => None,
                                    })
                                })
                                .unwrap_or_else(|| c.cad_component_id.clone()),
                        }),
                )
            } else {
                None
            }
        })
        .collect()
}

fn target(root: &Path, args: &[String]) -> Result<(String, PathBuf, PathBuf, bool, bool)> {
    let here = root.join("hardware/pcb/pcba");
    let mut target = None;
    let mut cache = here.join(".cad-cache");
    let mut step = false;
    let mut vias = false;
    let mut index = 0;
    while index < args.len() {
        match args[index].as_str() {
            "--step" => {
                step = true;
                index += 1;
            }
            "--vias" => {
                vias = true;
                index += 1;
            }
            "--cache-dir" => {
                cache = PathBuf::from(args.get(index + 1).context("--cache-dir requires a path")?);
                index += 2;
            }
            "--out-dir" => {
                ensure!(args.get(index + 1).is_some(), "--out-dir requires a path");
                index += 2;
            }
            s if !s.starts_with('-') && target.is_none() => {
                target = Some(s.to_owned());
                index += 1;
            }
            other => bail!("unknown model option {other}"),
        }
    }
    if let Some(target) = target.as_ref().filter(|v| v.ends_with(".circuit.json")) {
        let path = PathBuf::from(target);
        let name = path
            .file_name()
            .context("circuit has no filename")?
            .to_string_lossy()
            .trim_end_matches(".circuit.json")
            .to_owned();
        return Ok((name, path, cache, step, vias));
    }
    let name = target
        .as_deref()
        .map(|s| {
            Path::new(s)
                .file_stem()
                .unwrap()
                .to_string_lossy()
                .into_owned()
        })
        .unwrap_or_else(|| "pcba".into());
    let circuit = here.join("out").join(format!("{name}.circuit.json"));
    let source = here.join(format!("{name}.tsx"));
    let fresh = circuit.is_file()
        && (!source.is_file()
            || fs::metadata(&circuit)?.modified()? >= fs::metadata(&source)?.modified()?);
    if !fresh {
        ensure!(
            source.is_file(),
            "no {} and no {}",
            source.display(),
            circuit.display()
        );
        let status = Command::new(here.join("node_modules/.bin/tsci"))
            .current_dir(&here)
            .args(["export", "-f", "circuit-json"])
            .arg("-o")
            .arg(&circuit)
            .arg(&source)
            .status()?;
        ensure!(status.success(), "circuit export failed");
    }
    Ok((name, circuit, cache, step, vias))
}
pub fn run(root: &Path, args: &[String]) -> Result<()> {
    hsm_run_slots::process_enter("pcb-model")?;
    let started = Instant::now();
    let (name, path, cache, step, vias) = target(root, args)?;
    let circuit = Circuit::load(&path)?;
    let placements = placements(&circuit)?;
    let pinned = PinnedModels::load(root)?;
    let mut models = BTreeMap::new();
    for p in &placements {
        if !models.contains_key(&p.url) {
            let parts =
                if let Some(parts) = pinned.parts(p.cad.model_step_url.as_deref().unwrap_or(""))? {
                    parts
                } else {
                    parse_obj(&cached(&p.url, &cache)?)?
                };
            models.insert(p.url.clone(), parts);
        }
    }
    let slab = board(&circuit, vias)?;
    let mut meshes = vec![board_mesh(&slab)];
    let mut nodes = vec![json!({"name":"board","mesh":0})];
    let mut ranges = BTreeMap::new();
    for (url, parts) in &models {
        let start = meshes.len();
        meshes.extend(parts.clone());
        ranges.insert(url.clone(), (start, parts.len()));
    }
    for p in &placements {
        let (start, count) = ranges[&p.url];
        let columns = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
            .map(|v| geometry::rotate(v, p.cad.rotation, p.bottom));
        let t = geometry::place([0.; 3], &p.cad, p.bottom);
        let matrix = vec![
            columns[0][0],
            columns[0][1],
            columns[0][2],
            0.,
            columns[1][0],
            columns[1][1],
            columns[1][2],
            0.,
            columns[2][0],
            columns[2][1],
            columns[2][2],
            0.,
            t[0] / 1000.,
            t[1] / 1000.,
            t[2] / 1000.,
            1.,
        ];
        let children = (0..count)
            .map(|i| {
                let index = nodes.len();
                nodes.push(json!({"name":format!("{}/{}",p.name,i+1),"mesh":start+i}));
                index
            })
            .collect::<Vec<_>>();
        nodes.push(json!({"name":p.name,"matrix":matrix,"children":children}));
    }
    let out = args
        .windows(2)
        .find(|p| p[0] == "--out-dir")
        .map(|p| PathBuf::from(&p[1]))
        .unwrap_or_else(|| root.join("hardware/pcb/pcba/out"));
    fs::create_dir_all(&out)?;
    let glb = out.join(format!("{name}.glb"));
    let bytes = glb_bytes(&meshes, nodes, &pinned.manifest["material_names"])?;
    if !fs::read(&glb).is_ok_and(|prior| prior == bytes) {
        crate::write(&glb, &bytes)?;
    }
    println!(
        "[{name}] wrote {} — {} vendor components, {} bytes",
        glb.display(),
        placements.len(),
        bytes.len()
    );
    if !args.iter().any(|arg| arg == "--out-dir") {
        let textures = Command::new("bun")
            .current_dir(root.join("hardware/pcb/pcba"))
            .args(["board-texture.ts", &name])
            .status();
        if !textures.is_ok_and(|status| status.success()) {
            eprintln!("[{name}] board-texture skipped; run bun board-texture.ts {name}");
        }
    }
    if step {
        let path = out.join(format!("{name}.step"));
        write_step(&path, &name, &slab, &placements, &cache, &pinned)?;
        println!("[{name}] wrote {}", path.display());
    }
    println!("[{name}] {:.1}s", started.elapsed().as_secs_f64());
    Ok(())
}

fn glb_bytes(meshes: &[Mesh], nodes: Vec<Value>, material_names: &Value) -> Result<Vec<u8>> {
    let mut binary = vec![];
    let mut views = vec![];
    let mut accessors = vec![];
    let mut gltf_meshes = vec![];
    let mut materials = vec![];
    for mesh in meshes {
        let vertex_count = mesh.triangles.len() * 3;
        let mut positions = Vec::with_capacity(vertex_count * 12);
        let mut normals = Vec::with_capacity(vertex_count * 12);
        let (mut low, mut high) = ([f64::INFINITY; 3], [f64::NEG_INFINITY; 3]);
        for triangle in &mesh.triangles {
            let points = triangle.map(|i| mesh.positions[i as usize]);
            let a = v3(points[0][0], points[0][1], points[0][2]);
            let b = v3(points[1][0], points[1][1], points[1][2]);
            let c = v3(points[2][0], points[2][1], points[2][2]);
            let normal = (b - a).cross(c - a).unit();
            for (source_index, point) in triangle.iter().zip(points) {
                for axis in 0..3 {
                    let coordinate = (point[axis] / 1000.0) as f32;
                    positions.extend_from_slice(&coordinate.to_le_bytes());
                    low[axis] = low[axis].min(coordinate as f64);
                    high[axis] = high[axis].max(coordinate as f64);
                }
                let normal = mesh
                    .normals
                    .as_ref()
                    .map(|normals| normals[*source_index as usize].map(f64::from))
                    .unwrap_or([normal.x, normal.y, normal.z]);
                for value in normal {
                    normals.extend_from_slice(
                        &(if value.is_finite() { value } else { 0.0 } as f32).to_le_bytes(),
                    );
                }
            }
        }
        let material = materials.len();
        let linear = mesh.color.map(|s| {
            if mesh.color_is_linear {
                return s;
            }
            if s <= 0.04045 {
                s / 12.92
            } else {
                ((s + 0.055) / 1.055).powf(2.4)
            }
        });
        let name = material_names
            .as_array()
            .into_iter()
            .flatten()
            .find(|record| {
                (0..3).all(|axis| {
                    record["color"][axis]
                        .as_f64()
                        .is_some_and(|v| (v - linear[axis]).abs() < 1e-6)
                })
            })
            .and_then(|record| record["name"].as_str())
            .map(str::to_owned)
            .unwrap_or_else(|| format!("vendor_material_{material}"));
        materials.push(json!({"name":name,"pbrMetallicRoughness":{"baseColorFactor":[linear[0],linear[1],linear[2],1.]},"doubleSided":true}));
        let mut attributes = serde_json::Map::new();
        for (name, bytes, bounds) in [
            ("POSITION", positions, Some((low, high))),
            ("NORMAL", normals, None),
        ] {
            let view = views.len();
            views.push(json!({"buffer":0,"byteOffset":binary.len(),"byteLength":bytes.len(),"target":34962}));
            binary.extend(bytes);
            let index = accessors.len();
            let mut accessor =
                json!({"bufferView":view,"componentType":5126,"count":vertex_count,"type":"VEC3"});
            if let Some((low, high)) = bounds {
                accessor["min"] = json!(low);
                accessor["max"] = json!(high);
            }
            accessors.push(accessor);
            attributes.insert(name.into(), json!(index));
        }
        gltf_meshes
            .push(json!({"primitives":[{"attributes":attributes,"material":material,"mode":4}]}));
    }
    let children = nodes
        .iter()
        .flat_map(|n| n["children"].as_array().into_iter().flatten())
        .filter_map(Value::as_u64)
        .map(|i| i as usize)
        .collect::<std::collections::BTreeSet<_>>();
    let roots = (0..nodes.len())
        .filter(|i| !children.contains(i))
        .collect::<Vec<_>>();
    let document = json!({"asset":{"version":"2.0","generator":"hsm-pcb"},"scene":0,"scenes":[{"nodes":roots}],"nodes":nodes,"meshes":gltf_meshes,"materials":materials,"buffers":[{"byteLength":binary.len()}],"bufferViews":views,"accessors":accessors});
    let mut json = serde_json::to_vec(&document)?;
    while json.len() % 4 != 0 {
        json.push(b' ');
    }
    while binary.len() % 4 != 0 {
        binary.push(0);
    }
    let mut bytes = Vec::with_capacity(28 + json.len() + binary.len());
    bytes.extend_from_slice(b"glTF");
    for word in [
        2,
        28 + json.len() as u32 + binary.len() as u32,
        json.len() as u32,
        0x4e4f534a,
    ] {
        bytes.extend_from_slice(&word.to_le_bytes());
    }
    bytes.extend(json);
    bytes.extend_from_slice(&(binary.len() as u32).to_le_bytes());
    bytes.extend_from_slice(&0x004e4942u32.to_le_bytes());
    bytes.extend(binary);
    Ok(bytes)
}

struct Step {
    next: usize,
    text: String,
    styled: Vec<usize>,
}
fn step_references(record: &str) -> Vec<usize> {
    let mut refs = Vec::new();
    let mut quoted = false;
    let mut chars = record.chars().peekable();
    while let Some(ch) = chars.next() {
        if ch == '\'' {
            quoted = !quoted;
        }
        if ch == '#' && !quoted {
            let mut digits = String::new();
            while chars.peek().is_some_and(char::is_ascii_digit) {
                digits.push(chars.next().unwrap());
            }
            if let Ok(id) = digits.parse() {
                refs.push(id);
            }
        }
    }
    refs
}
impl Step {
    fn add(&mut self, entity: impl AsRef<str>) -> usize {
        let index = self.next;
        self.next += 1;
        writeln!(self.text, "#{index}={};", entity.as_ref()).unwrap();
        index
    }
    fn import(&mut self, bytes: &str, placement: &Placement) -> Result<Vec<usize>> {
        let data = bytes
            .split_once("DATA;")
            .context("STEP has no data section")?
            .1
            .split_once("ENDSEC;")
            .context("STEP has no data terminator")?
            .0;
        let mut records = vec![];
        let mut statement = String::new();
        let mut quoted = false;
        for ch in data.chars() {
            if ch == '\'' {
                quoted = !quoted;
            }
            statement.push(ch);
            if ch == ';' && !quoted {
                if let Some((left, right)) = statement.trim().trim_end_matches(';').split_once('=')
                {
                    if let Some(id) = left.trim().strip_prefix('#') {
                        records.push((id.trim().parse::<usize>()?, right.trim().to_owned()));
                    }
                }
                statement.clear();
            }
        }
        let offset = self.next;
        let max = records
            .iter()
            .map(|(id, _)| *id)
            .max()
            .context("STEP contains no entities")?;
        self.next += max + 1;
        let indexed = records
            .iter()
            .map(|(id, record)| (*id, record))
            .collect::<BTreeMap<_, _>>();
        let mut keep = std::collections::BTreeSet::new();
        let mut pending = records
            .iter()
            .filter(|(_, record)| {
                let compact = record
                    .chars()
                    .filter(|c| !c.is_whitespace())
                    .collect::<String>();
                ["MANIFOLD_SOLID_BREP(", "BREP_WITH_VOIDS(", "FACETED_BREP("]
                    .iter()
                    .any(|prefix| compact.starts_with(prefix))
            })
            .map(|(id, _)| *id)
            .collect::<Vec<_>>();
        let visit = |keep: &mut std::collections::BTreeSet<usize>, pending: &mut Vec<usize>| {
            while let Some(id) = pending.pop() {
                if keep.insert(id) {
                    if let Some(record) = indexed.get(&id) {
                        pending.extend(step_references(record));
                    }
                }
            }
        };
        visit(&mut keep, &mut pending);
        for (id, record) in &records {
            if record.trim_start().starts_with("STYLED_ITEM")
                && step_references(record)
                    .last()
                    .is_some_and(|target| keep.contains(target))
            {
                pending.push(*id);
            }
        }
        visit(&mut keep, &mut pending);
        let mut representations = vec![];
        for (id, mut record) in records {
            if !keep.contains(&id) {
                continue;
            }
            let compact = record
                .chars()
                .filter(|c| !c.is_whitespace())
                .collect::<String>();
            if compact.starts_with("STYLED_ITEM(") {
                self.styled.push(id + offset);
            }
            if compact.starts_with("MANIFOLD_SOLID_BREP(")
                || compact.starts_with("BREP_WITH_VOIDS(")
                || compact.starts_with("FACETED_BREP(")
            {
                representations.push(id + offset);
            }
            if compact.starts_with("CARTESIAN_POINT(") || compact.starts_with("DIRECTION(") {
                let open = record
                    .rfind('(')
                    .context("STEP vector has no coordinates")?;
                let close = record[open + 1..]
                    .find(')')
                    .context("STEP vector has no terminator")?
                    + open
                    + 1;
                let values = record[open + 1..close]
                    .split(',')
                    .map(|s| s.trim().replace('D', "E").parse::<f64>())
                    .collect::<std::result::Result<Vec<_>, _>>()?;
                if values.len() == 3 {
                    let point = [values[0], values[1], values[2]];
                    let point = if compact.starts_with("CARTESIAN_POINT(") {
                        geometry::place(point, &placement.cad, placement.bottom)
                    } else {
                        geometry::rotate(point, placement.cad.rotation, placement.bottom)
                    };
                    record.replace_range(
                        open + 1..close,
                        &format!("{:.17E},{:.17E},{:.17E}", point[0], point[1], point[2]),
                    );
                }
            }
            let mut remapped = String::new();
            let mut chars = record.chars().peekable();
            let mut quoted = false;
            while let Some(ch) = chars.next() {
                if ch == '\'' {
                    quoted = !quoted;
                }
                if ch == '#' && !quoted {
                    let mut number = String::new();
                    while chars.peek().is_some_and(char::is_ascii_digit) {
                        number.push(chars.next().unwrap());
                    }
                    write!(remapped, "#{}", number.parse::<usize>()? + offset)?;
                } else {
                    remapped.push(ch);
                }
            }
            writeln!(self.text, "#{}={remapped};", id + offset)?;
        }
        ensure!(
            !representations.is_empty(),
            "STEP contains no body representation"
        );
        Ok(representations)
    }
    fn point(&mut self, p: [f64; 3]) -> usize {
        self.add(format!(
            "CARTESIAN_POINT('',({:.17E},{:.17E},{:.17E}))",
            p[0], p[1], p[2]
        ))
    }
    fn direction(&mut self, p: [f64; 3]) -> usize {
        self.add(format!(
            "DIRECTION('',({:.17E},{:.17E},{:.17E}))",
            p[0], p[1], p[2]
        ))
    }
    fn axis(&mut self) -> usize {
        let origin = self.point([0.; 3]);
        let z = self.direction([0., 0., 1.]);
        let x = self.direction([1., 0., 0.]);
        self.add(format!("AXIS2_PLACEMENT_3D('',#{origin},#{z},#{x})"))
    }
    fn product(&mut self, name: &str, representation: usize, app: usize) -> usize {
        let name = name.replace('\'', "''");
        let context = self.add(format!("PRODUCT_CONTEXT('',#{app},'mechanical')"));
        let product = self.add(format!("PRODUCT('{name}','{name}','',(#{context}))"));
        let formation = self.add(format!("PRODUCT_DEFINITION_FORMATION('','',#{product})"));
        let context = self.add(format!(
            "PRODUCT_DEFINITION_CONTEXT('part definition',#{app},'design')"
        ));
        let definition = self.add(format!(
            "PRODUCT_DEFINITION('design','',#{formation},#{context})"
        ));
        let shape = self.add(format!("PRODUCT_DEFINITION_SHAPE('','',#{definition})"));
        self.add(format!(
            "SHAPE_DEFINITION_REPRESENTATION(#{shape},#{representation})"
        ));
        self.add(format!(
            "PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,(#{product}))"
        ));
        definition
    }
}
fn write_step(
    path: &Path,
    name: &str,
    board: &Solid,
    placements: &[Placement],
    cache: &Path,
    pinned: &PinnedModels,
) -> Result<()> {
    let mut step = Step {
        next: 1,
        text: String::new(),
        styled: Vec::new(),
    };
    let app = step.add("APPLICATION_CONTEXT('automotive design')");
    step.add(format!(
        "APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#{app})"
    ));
    let length = step.add("(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.))");
    let angle = step.add("(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.))");
    let solid = step.add("(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT())");
    let context = step.add(format!("(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNIT_ASSIGNED_CONTEXT((#{length},#{angle},#{solid})) REPRESENTATION_CONTEXT('',''))"));
    let origin = step.axis();
    let points = board
        .verts()
        .iter()
        .map(|p| step.point([p.x, p.y, p.z]))
        .collect::<Vec<_>>();
    let vertices = points
        .iter()
        .map(|point| step.add(format!("VERTEX_POINT('',#{point})")))
        .collect::<Vec<_>>();
    let mut edges = BTreeMap::new();
    let mut faces = Vec::new();
    for triangle in board.tris() {
        let mut boundary = Vec::new();
        for k in 0..3 {
            let (a, b) = (triangle[k] as usize, triangle[(k + 1) % 3] as usize);
            let key = (a.min(b), a.max(b));
            let edge = if let Some(edge) = edges.get(&key) {
                *edge
            } else {
                let direction = (board.verts()[key.1] - board.verts()[key.0]).unit();
                let d = step.direction([direction.x, direction.y, direction.z]);
                let vector = step.add(format!("VECTOR('',#{d},1.)"));
                let line = step.add(format!("LINE('',#{},#{vector})", points[key.0]));
                let edge = step.add(format!(
                    "EDGE_CURVE('',#{},#{},#{line},.T.)",
                    vertices[key.0], vertices[key.1]
                ));
                edges.insert(key, edge);
                edge
            };
            boundary.push(step.add(format!(
                "ORIENTED_EDGE('',*,*,#{edge},.{prefix}.)",
                prefix = if a < b { "T" } else { "F" }
            )));
        }
        let boundary = step.add(format!(
            "EDGE_LOOP('',({}))",
            boundary
                .iter()
                .map(|id| format!("#{id}"))
                .collect::<Vec<_>>()
                .join(",")
        ));
        let bound = step.add(format!("FACE_OUTER_BOUND('',#{boundary},.T.)"));
        let [a, b, c] = triangle.map(|i| board.verts()[i as usize]);
        let normal = (b - a).cross(c - a).unit();
        let x = (b - a).unit();
        let z = step.direction([normal.x, normal.y, normal.z]);
        let x = step.direction([x.x, x.y, x.z]);
        let axis = step.add(format!(
            "AXIS2_PLACEMENT_3D('',#{},#{z},#{x})",
            points[triangle[0] as usize]
        ));
        let plane = step.add(format!("PLANE('',#{axis})"));
        faces.push(step.add(format!("ADVANCED_FACE('',(#{bound}),#{plane},.T.)")));
    }
    let shell = step.add(format!(
        "CLOSED_SHELL('',({}))",
        faces
            .iter()
            .map(|face| format!("#{face}"))
            .collect::<Vec<_>>()
            .join(",")
    ));
    let slab = step.add(format!("MANIFOLD_SOLID_BREP('board',#{shell})"));
    let mut bodies = vec![slab];
    for placement in placements {
        let url = placement
            .cad
            .model_step_url
            .as_ref()
            .context("component has no STEP source")?;
        let source = cached(url, cache)?;
        pinned.verify_step(url, &source)?;
        bodies.extend(step.import(&fs::read_to_string(source)?, placement)?);
    }
    let mut items = vec![origin];
    items.extend(bodies);
    let shape = step.add(format!(
        "ADVANCED_BREP_SHAPE_REPRESENTATION('{}',({}),#{context})",
        name.replace('\'', "''"),
        items
            .iter()
            .map(|i| format!("#{i}"))
            .collect::<Vec<_>>()
            .join(",")
    ));
    step.product(name, shape, app);
    if !step.styled.is_empty() {
        step.add(format!(
            "MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',({}),#{context})",
            step.styled
                .iter()
                .map(|id| format!("#{id}"))
                .collect::<Vec<_>>()
                .join(",")
        ));
    }
    crate::write(path,format!("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('PCB vendor assembly'),'2;1');\nFILE_NAME('','1970-01-01T00:00:00',(''),(''),'hsm-pcb','hsm-pcb','');\nFILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\nENDSEC;\nDATA;\n{}ENDSEC;\nEND-ISO-10303-21;\n",step.text).as_bytes())
}

pub fn orientation(root: &Path, args: &[String]) -> Result<()> {
    let (name, path, cache, _, _) = target(root, args)?;
    let circuit = Circuit::load(&path)?;
    let pinned = PinnedModels::load(root)?;
    let mut boxes = BTreeMap::new();
    for e in &circuit.elements {
        if let Element::Courtyard(c) = e {
            if !c.outline.is_empty() {
                let mut b = [
                    f64::INFINITY,
                    f64::INFINITY,
                    f64::NEG_INFINITY,
                    f64::NEG_INFINITY,
                ];
                for p in &c.outline {
                    b[0] = b[0].min(p.x);
                    b[1] = b[1].min(p.y);
                    b[2] = b[2].max(p.x);
                    b[3] = b[3].max(p.y);
                }
                boxes.insert(c.pcb_component_id.clone(), b);
            }
        }
    }
    for e in &circuit.elements {
        if let Element::SmtPad(p) | Element::PlatedHole(p) = e {
            boxes.entry(p.pcb_component_id.clone()).or_insert_with(|| {
                let mut b = [p.x, p.y, p.x, p.y];
                for element in &circuit.elements {
                    if let Element::SmtPad(other) | Element::PlatedHole(other) = element {
                        if other.pcb_component_id == p.pcb_component_id {
                            b[0] = b[0].min(other.x);
                            b[1] = b[1].min(other.y);
                            b[2] = b[2].max(other.x);
                            b[3] = b[3].max(other.y);
                        }
                    }
                }
                b
            });
        }
    }
    let mut flagged = 0;
    let mut checked = 0;
    for p in placements(&circuit)? {
        let Some(foot) = boxes.get(&p.cad.pcb_component_id) else {
            continue;
        };
        let mesh =
            if let Some(parts) = pinned.parts(p.cad.model_step_url.as_deref().unwrap_or(""))? {
                parts
            } else {
                parse_obj(&cached(&p.url, &cache)?)?
            };
        let (mut low, mut high) = ([f64::INFINITY; 3], [f64::NEG_INFINITY; 3]);
        for model in mesh {
            for point in model.positions {
                let point = geometry::place(point, &p.cad, p.bottom);
                for i in 0..3 {
                    low[i] = low[i].min(point[i]);
                    high[i] = high[i].max(point[i]);
                }
            }
        }
        let center = ((low[0] + high[0] - foot[0] - foot[2]) / 2.0)
            .hypot((low[1] + high[1] - foot[1] - foot[3]) / 2.0);
        let (mw, mh, fw, fh) = (
            high[0] - low[0],
            high[1] - low[1],
            foot[2] - foot[0],
            foot[3] - foot[1],
        );
        let swapped = mw.max(mh) / mw.min(mh).max(1e-6) > 1.25
            && fw.max(fh) / fw.min(fh).max(1e-6) > 1.25
            && (mw >= mh) != (fw >= fh);
        checked += 1;
        if swapped || center > 1.0 {
            flagged += 1;
            println!(
                "{}: center offset {center:.2} mm; model {mw:.1}×{mh:.1}, footprint {fw:.1}×{fh:.1}{}",
                p.name,
                if swapped { "; LONG-AXIS SWAP" } else { "" }
            );
        }
    }
    println!("PART ORIENTATION AUDIT — {name}: {checked} placed parts, {flagged} flagged");
    ensure!(flagged == 0, "component orientation outliers");
    Ok(())
}
