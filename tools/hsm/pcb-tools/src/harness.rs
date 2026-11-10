//! Harness crops retain the published connector geometry and original fabrication pixels at their bench poses.
use crate::circuit::{Circuit, Element};
use anyhow::{Context, Result, bail, ensure};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{collections::BTreeMap, f64::consts::FRAC_PI_2, fs, io::Cursor, path::Path};

struct Header {
    name: &'static str,
    bounds: [f64; 4],
    rotation: [f64; 3],
    position: [f64; 3],
    pin_material: &'static str,
}
const HEADERS: [Header; 2] = [
    Header {
        name: "J2",
        bounds: [5., 17., -16., 5.],
        rotation: [-FRAC_PI_2, 0., 0.],
        position: [-110.55, 0.4, -5.77],
        pin_material: "mat_6",
    },
    Header {
        name: "J13",
        bounds: [-19.75, -4.75, 27.8, 36.5],
        rotation: [-FRAC_PI_2, 0., FRAC_PI_2],
        position: [-68.55, 0.4, -12.25],
        pin_material: "mat_2",
    },
];
fn sha(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

pub fn run(root: &Path, args: &[String]) -> Result<()> {
    let mut source = root.join("hardware/pcb/pcba/out");
    let mut destination = root.join("web/public/harness");
    let mut release = root.join("hardware/cad-artifacts.json");
    let mut names = Vec::new();
    let mut arguments = args.iter();
    while let Some(arg) = arguments.next() {
        match arg.as_str() {
            "--source-dir" | "--out-dir" | "--release" => {
                let path = arguments
                    .next()
                    .with_context(|| format!("{arg} requires a path"))?;
                match arg.as_str() {
                    "--source-dir" => source = path.into(),
                    "--out-dir" => destination = path.into(),
                    _ => release = path.into(),
                }
            }
            "J2" | "J13" => names.push(arg.as_str()),
            _ => bail!(
                "harness-crops [J2 J13] [--source-dir DIRECTORY] [--out-dir DIRECTORY] [--release CATALOG]"
            ),
        }
    }
    if names.is_empty() {
        names.extend(HEADERS.iter().map(|h| h.name));
    }
    let catalog: Value = serde_json::from_slice(&fs::read(&release)?)?;
    let mut hashes = BTreeMap::new();
    for filename in ["pcba.glb", "pcba.top3d.png", "pcba.bottom3d.png"] {
        let hash = sha(&fs::read(source.join(filename))?);
        ensure!(
            catalog["solids"][format!("hardware/pcb/pcba/out/{filename}")] == hash,
            "{filename} differs from the published source catalog {}",
            release.display()
        );
        hashes.insert(filename.to_owned(), hash);
    }
    let glb = Glb::load(&source.join("pcba.glb"))?;
    let circuit = Circuit::load(&source.join("pcba.circuit.json"))?;
    for name in names {
        let header = HEADERS.iter().find(|h| h.name == name).unwrap();
        extract(&glb, &circuit, header, &hashes, &source, &destination)?;
    }
    Ok(())
}

struct Glb {
    document: Value,
    binary: Vec<u8>,
}
impl Glb {
    fn load(path: &Path) -> Result<Self> {
        let raw = fs::read(path)?;
        ensure!(raw.len() >= 28 && &raw[..4] == b"glTF", "invalid PCB GLB");
        let word = |i| u32::from_le_bytes(raw[i..i + 4].try_into().unwrap());
        ensure!(
            word(4) == 2 && word(8) as usize == raw.len() && word(16) == 0x4e4f534a,
            "invalid GLB chunks"
        );
        let end = 20usize
            .checked_add(word(12) as usize)
            .context("GLB JSON size overflow")?;
        ensure!(end + 8 <= raw.len(), "truncated GLB JSON");
        ensure!(
            word(end + 4) == 0x004e4942 && end + 8 + word(end) as usize == raw.len(),
            "invalid GLB buffer"
        );
        Ok(Self {
            document: serde_json::from_slice(&raw[20..end])?,
            binary: raw[end + 8..].to_vec(),
        })
    }
    fn view(&self, index: usize) -> Result<&[u8]> {
        let view = &self.document["bufferViews"][index];
        ensure!(
            view["buffer"].as_u64().unwrap_or(0) == 0,
            "external GLB buffer"
        );
        let start = view["byteOffset"].as_u64().unwrap_or(0) as usize;
        let size = view["byteLength"]
            .as_u64()
            .context("buffer view has no size")? as usize;
        self.binary
            .get(start..start.checked_add(size).context("view size overflow")?)
            .context("truncated buffer view")
    }
    fn rows(&self, index: usize) -> Result<Vec<Vec<f64>>> {
        let accessor = &self.document["accessors"][index];
        ensure!(accessor.get("sparse").is_none(), "sparse PCB attribute");
        let view_index = accessor["bufferView"]
            .as_u64()
            .context("accessor has no buffer view")? as usize;
        let view = &self.document["bufferViews"][view_index];
        let bytes = self.view(view_index)?;
        let width = match accessor["type"].as_str() {
            Some("SCALAR") => 1,
            Some("VEC2") => 2,
            Some("VEC3") => 3,
            Some("VEC4") => 4,
            _ => bail!("unsupported PCB attribute shape"),
        };
        let component = accessor["componentType"]
            .as_u64()
            .context("attribute has no component type")?;
        let size = match component {
            5126 | 5125 => 4,
            5123 => 2,
            5121 => 1,
            _ => bail!("unsupported PCB component"),
        };
        let count = accessor["count"]
            .as_u64()
            .context("attribute has no count")? as usize;
        let start = accessor["byteOffset"].as_u64().unwrap_or(0) as usize;
        let stride = view["byteStride"]
            .as_u64()
            .map(|v| v as usize)
            .unwrap_or(width * size);
        ensure!(stride >= width * size, "invalid PCB attribute stride");
        (0..count)
            .map(|row| {
                (0..width)
                    .map(|axis| {
                        let offset = row
                            .checked_mul(stride)
                            .and_then(|v| v.checked_add(start + axis * size))
                            .context("attribute offset overflow")?;
                        let value = bytes
                            .get(offset..offset + size)
                            .context("truncated PCB attribute")?;
                        Ok(match component {
                            5126 => f32::from_le_bytes(value.try_into()?) as f64,
                            5125 => u32::from_le_bytes(value.try_into()?) as f64,
                            5123 => u16::from_le_bytes(value.try_into()?) as f64,
                            _ => value[0] as f64,
                        })
                    })
                    .collect()
            })
            .collect()
    }
    fn attribute(&self, primitive: &Value, name: &str) -> Result<Vec<Vec<f64>>> {
        self.rows(
            primitive["attributes"][name]
                .as_u64()
                .with_context(|| format!("missing PCB {name}"))? as usize,
        )
    }
    fn indices(&self, primitive: &Value, count: usize) -> Result<Vec<usize>> {
        let ids = if let Some(index) = primitive["indices"].as_u64() {
            self.rows(index as usize)?
                .iter()
                .map(|v| v[0] as usize)
                .collect()
        } else {
            (0..count).collect::<Vec<_>>()
        };
        ensure!(
            primitive["mode"].as_u64().unwrap_or(4) == 4
                && ids.len() % 3 == 0
                && ids.iter().all(|i| *i < count),
            "invalid PCB triangles"
        );
        Ok(ids)
    }
    fn find(&self, name: &str) -> Result<usize> {
        let nodes = self.document["nodes"]
            .as_array()
            .context("GLB has no nodes")?;
        let matching = nodes
            .iter()
            .enumerate()
            .filter(|(_, n)| n["name"] == name)
            .map(|(i, _)| i)
            .collect::<Vec<_>>();
        ensure!(
            matching.len() == 1,
            "PCB node identity {name} is absent or ambiguous"
        );
        Ok(matching[0])
    }
    fn walk(
        &self,
        node: usize,
        parent: Matrix,
        visited: &mut Vec<usize>,
        out: &mut Vec<(usize, Matrix)>,
    ) -> Result<()> {
        ensure!(!visited.contains(&node), "cyclic PCB scene");
        visited.push(node);
        let record = self.document["nodes"]
            .get(node)
            .context("missing PCB node")?;
        let matrix = parent.times(Matrix::node(record)?);
        if record.get("mesh").is_some() {
            out.push((node, matrix));
        }
        if let Some(children) = record["children"].as_array() {
            for child in children {
                self.walk(
                    child.as_u64().context("invalid child")? as usize,
                    matrix,
                    visited,
                    out,
                )?;
            }
        }
        visited.pop();
        Ok(())
    }
    fn meshes(&self, node: usize) -> Result<Vec<(usize, Matrix)>> {
        let mut found = Vec::new();
        self.walk(node, Matrix::identity(), &mut Vec::new(), &mut found)?;
        Ok(found)
    }
}

#[derive(Clone, Copy)]
struct Matrix([f64; 16]);
impl Matrix {
    fn identity() -> Self {
        Self([
            1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1.,
        ])
    }
    fn node(node: &Value) -> Result<Self> {
        if let Some(matrix) = node["matrix"].as_array() {
            ensure!(matrix.len() == 16, "invalid PCB matrix");
            let mut values = [0.; 16];
            for (out, input) in values.iter_mut().zip(matrix) {
                *out = input.as_f64().context("invalid matrix value")?;
            }
            return Ok(Self(values));
        }
        let vector = |key: &str, default: &[f64]| -> Result<Vec<f64>> {
            if let Some(values) = node[key].as_array() {
                ensure!(values.len() == default.len(), "invalid node {key}");
                values
                    .iter()
                    .map(|v| v.as_f64().context("invalid transform value"))
                    .collect()
            } else {
                Ok(default.to_vec())
            }
        };
        let t = vector("translation", &[0.; 3])?;
        let s = vector("scale", &[1.; 3])?;
        let q = vector("rotation", &[0., 0., 0., 1.])?;
        let (x, y, z, w) = (q[0], q[1], q[2], q[3]);
        Ok(Self([
            (1. - 2. * (y * y + z * z)) * s[0],
            2. * (x * y + z * w) * s[0],
            2. * (x * z - y * w) * s[0],
            0.,
            2. * (x * y - z * w) * s[1],
            (1. - 2. * (x * x + z * z)) * s[1],
            2. * (y * z + x * w) * s[1],
            0.,
            2. * (x * z + y * w) * s[2],
            2. * (y * z - x * w) * s[2],
            (1. - 2. * (x * x + y * y)) * s[2],
            0.,
            t[0],
            t[1],
            t[2],
            1.,
        ]))
    }
    fn times(self, rhs: Self) -> Self {
        let mut out = [0.; 16];
        for col in 0..4 {
            for row in 0..4 {
                out[col * 4 + row] = (0..4)
                    .map(|k| self.0[k * 4 + row] * rhs.0[col * 4 + k])
                    .sum();
            }
        }
        Self(out)
    }
    fn point(self, p: &[f64]) -> [f64; 3] {
        std::array::from_fn(|row| {
            self.0[row] * p[0] + self.0[4 + row] * p[1] + self.0[8 + row] * p[2] + self.0[12 + row]
        })
    }
    fn normal(self, p: &[f64]) -> [f64; 3] {
        // Board crops use rigid transforms; the untouched connector keeps its original hierarchy.
        std::array::from_fn(|row| {
            self.0[row] * p[0] + self.0[4 + row] * p[1] + self.0[8 + row] * p[2]
        })
    }
}

struct Writer {
    document: Value,
    binary: Vec<u8>,
}
impl Writer {
    fn new(src: &Glb, name: &str) -> Result<Self> {
        let mut writer = Self {
            document: json!({"asset":{"version":"2.0","generator":format!("hsm-pcb {name} crop of the published PCBA")},"scene":0,"scenes":[{"nodes":[]}],"nodes":[],"meshes":[],"materials":src.document["materials"].clone(),"accessors":[],"bufferViews":[],"images":[],"textures":[],"samplers":[]}),
            binary: Vec::new(),
        };
        for key in ["textures", "samplers"] {
            if let Some(values) = src.document[key].as_array() {
                writer.document[key] = json!(values);
            }
        }
        if let Some(images) = src.document["images"].as_array() {
            for original in images {
                let mut image = original.clone();
                let index = image["bufferView"]
                    .as_u64()
                    .context("PCB texture is not embedded")? as usize;
                image["bufferView"] = json!(writer.blob(src.view(index)?, None));
                writer.push("images", image);
            }
        }
        Ok(writer)
    }
    fn push(&mut self, key: &str, value: Value) -> usize {
        let array = self.document[key].as_array_mut().unwrap();
        let index = array.len();
        array.push(value);
        index
    }
    fn blob(&mut self, bytes: &[u8], target: Option<u32>) -> usize {
        while self.binary.len() % 4 != 0 {
            self.binary.push(0);
        }
        let mut view = json!({"buffer":0,"byteOffset":self.binary.len(),"byteLength":bytes.len()});
        if let Some(target) = target {
            view["target"] = json!(target);
        }
        let index = self.push("bufferViews", view);
        self.binary.extend_from_slice(bytes);
        index
    }
    fn accessor(&mut self, rows: &[Vec<f64>], kind: &str, component: u64) -> Result<usize> {
        ensure!(!rows.is_empty(), "empty PCB attribute");
        let mut bytes = Vec::new();
        for row in rows {
            for &value in row {
                match component {
                    5126 => bytes.extend_from_slice(&(value as f32).to_le_bytes()),
                    5125 => bytes.extend_from_slice(&(value as u32).to_le_bytes()),
                    5123 => bytes.extend_from_slice(&(value as u16).to_le_bytes()),
                    5121 => bytes.push(value as u8),
                    _ => bail!("unsupported output component"),
                }
            }
        }
        let view = self.blob(&bytes, Some(if kind == "SCALAR" { 34963 } else { 34962 }));
        let mut accessor =
            json!({"bufferView":view,"componentType":component,"count":rows.len(),"type":kind});
        if kind == "VEC3" {
            accessor["min"] = json!(
                (0..3)
                    .map(|k| rows.iter().map(|r| r[k]).fold(f64::INFINITY, f64::min))
                    .collect::<Vec<_>>()
            );
            accessor["max"] = json!(
                (0..3)
                    .map(|k| rows.iter().map(|r| r[k]).fold(f64::NEG_INFINITY, f64::max))
                    .collect::<Vec<_>>()
            );
        }
        Ok(self.push("accessors", accessor))
    }
    fn copy_accessor(&mut self, src: &Glb, index: usize) -> Result<usize> {
        let source = &src.document["accessors"][index];
        let index = self.accessor(
            &src.rows(index)?,
            source["type"].as_str().context("accessor has no type")?,
            source["componentType"]
                .as_u64()
                .context("accessor has no component type")?,
        )?;
        if let Some(normalized) = source.get("normalized") {
            self.document["accessors"][index]["normalized"] = normalized.clone();
        }
        Ok(index)
    }
    fn copy_node(&mut self, src: &Glb, index: usize, depth: usize) -> Result<usize> {
        ensure!(
            depth
                <= src.document["nodes"]
                    .as_array()
                    .context("no PCB nodes")?
                    .len(),
            "cyclic PCB scene"
        );
        let mut node = src.document["nodes"]
            .get(index)
            .context("missing PCB node")?
            .clone();
        let output = self.push("nodes", Value::Null);
        if let Some(mesh) = node["mesh"].as_u64() {
            let mut mesh = src.document["meshes"][mesh as usize].clone();
            for primitive in mesh["primitives"]
                .as_array_mut()
                .context("missing PCB primitives")?
            {
                for (_, attribute) in primitive["attributes"]
                    .as_object_mut()
                    .context("missing PCB attributes")?
                {
                    *attribute = json!(self.copy_accessor(
                        src,
                        attribute.as_u64().context("invalid attribute index")? as usize
                    )?);
                }
                if let Some(index) = primitive["indices"].as_u64() {
                    primitive["indices"] = json!(self.copy_accessor(src, index as usize)?);
                }
            }
            node["mesh"] = json!(self.push("meshes", mesh));
        }
        if let Some(children) = node["children"].as_array() {
            let copies = children
                .iter()
                .map(|child| {
                    self.copy_node(
                        src,
                        child.as_u64().context("invalid PCB child")? as usize,
                        depth + 1,
                    )
                })
                .collect::<Result<Vec<_>>>()?;
            node["children"] = json!(copies);
        }
        self.document["nodes"][output] = node;
        Ok(output)
    }
    fn bytes(mut self) -> Result<Vec<u8>> {
        while self.binary.len() % 4 != 0 {
            self.binary.push(0);
        }
        self.document["buffers"] = json!([{"byteLength":self.binary.len()}]);
        let mut document = serde_json::to_vec(&self.document)?;
        while document.len() % 4 != 0 {
            document.push(b' ');
        }
        let size = u32::try_from(28 + document.len() + self.binary.len())?;
        let mut bytes = b"glTF".to_vec();
        for word in [2, size, document.len() as u32, 0x4e4f534a] {
            bytes.extend_from_slice(&word.to_le_bytes());
        }
        bytes.extend(document);
        bytes.extend_from_slice(&(self.binary.len() as u32).to_le_bytes());
        bytes.extend_from_slice(&0x004e4942u32.to_le_bytes());
        bytes.extend(self.binary);
        Ok(bytes)
    }
}

fn clip(poly: Vec<Vec<f64>>, axis: usize, bound: f64, greater: bool) -> Vec<Vec<f64>> {
    let mut out = Vec::new();
    for i in 0..poly.len() {
        let (a, b) = (&poly[i], &poly[(i + 1) % poly.len()]);
        let inside = |v: f64| if greater { v >= bound } else { v <= bound };
        let (ai, bi) = (inside(a[axis]), inside(b[axis]));
        if ai {
            out.push(a.clone());
        }
        if ai != bi {
            let t = (bound - a[axis]) / (b[axis] - a[axis]);
            out.push(a.iter().zip(b).map(|(a, b)| a + t * (b - a)).collect());
        }
    }
    out
}

fn crop_png(path: &Path, bounds: [i64; 4]) -> Result<(Vec<u8>, [u32; 2])> {
    let mut decoder = png::Decoder::new(Cursor::new(fs::read(path)?));
    decoder.set_transformations(png::Transformations::EXPAND | png::Transformations::STRIP_16);
    let mut reader = decoder.read_info()?;
    let mut bytes = vec![
        0;
        reader
            .output_buffer_size()
            .context("fabrication PNG too large")?
    ];
    let info = reader.next_frame(&mut bytes)?;
    ensure!(
        info.bit_depth == png::BitDepth::Eight,
        "unsupported fabrication PNG depth"
    );
    let channels = info.color_type.samples();
    let [left, top, right, bottom] = bounds;
    ensure!(right > left && bottom > top, "empty fabrication crop");
    let (width, height) = (u32::try_from(right - left)?, u32::try_from(bottom - top)?);
    let mut pixels = vec![0; width as usize * height as usize * channels];
    for y in top.max(0)..bottom.min(info.height as i64) {
        for x in left.max(0)..right.min(info.width as i64) {
            let input = (y as usize * info.width as usize + x as usize) * channels;
            let output = ((y - top) as usize * width as usize + (x - left) as usize) * channels;
            pixels[output..output + channels].copy_from_slice(&bytes[input..input + channels]);
        }
    }
    let mut png = Vec::new();
    {
        let mut encoder = png::Encoder::new(&mut png, width, height);
        encoder.set_color(info.color_type);
        encoder.set_depth(png::BitDepth::Eight);
        encoder.write_header()?.write_image_data(&pixels)?;
    }
    Ok((png, [info.width, info.height]))
}

fn extract(
    src: &Glb,
    circuit: &Circuit,
    config: &Header,
    hashes: &BTreeMap<String, String>,
    source: &Path,
    destination: &Path,
) -> Result<()> {
    let name = config.name;
    let component = circuit
        .elements
        .iter()
        .find_map(|e| match e {
            Element::SourceComponent(c) if c.name == name => Some(c),
            _ => None,
        })
        .context("connector absent from circuit")?;
    let pcb = circuit
        .elements
        .iter()
        .find_map(|e| match e {
            Element::Component(c) if c.source_component_id == component.source_component_id => {
                Some(c)
            }
            _ => None,
        })
        .context("connector has no PCB placement")?;
    let cad = circuit
        .elements
        .iter()
        .find_map(|e| match e {
            Element::Cad(c)
                if c.source_component_id == component.source_component_id
                    && c.model_step_url.is_some() =>
            {
                Some(c)
            }
            _ => None,
        })
        .context("connector has no detailed CAD source")?;
    let board = circuit.board()?;
    let xmin = board
        .outline
        .iter()
        .map(|p| p.x)
        .reduce(f64::min)
        .context("board has no outline")?;
    let ymax = board
        .outline
        .iter()
        .map(|p| p.y)
        .reduce(f64::max)
        .context("board has no outline")?;
    ensure!(
        board.width > 0. && board.height > 0.,
        "invalid board dimensions"
    );
    let header_node = src.find(name)?;
    let board_node = src.find("board").or_else(|_| src.find("PCB"))?;
    let mut pin_tip = f64::NEG_INFINITY;
    for (node, matrix) in src.meshes(header_node)? {
        let mesh = src.document["nodes"][node]["mesh"]
            .as_u64()
            .context("missing connector mesh")? as usize;
        for primitive in src.document["meshes"][mesh]["primitives"]
            .as_array()
            .context("missing connector primitives")?
        {
            let material = primitive["material"]
                .as_u64()
                .context("connector has no material")? as usize;
            if src.document["materials"][material]["name"] == config.pin_material {
                for position in src.attribute(primitive, "POSITION")? {
                    pin_tip = pin_tip.max(matrix.point(&position)[2]);
                }
            }
        }
    }
    ensure!(
        pin_tip.is_finite(),
        "{name} pin material {} absent from the detailed source",
        config.pin_material
    );
    let mut writer = Writer::new(src, name)?;
    let header_output = writer.copy_node(src, header_node, 0)?;
    writer.document["nodes"][header_output]["name"] = json!(name);
    let mut batches: BTreeMap<usize, (Vec<Vec<f64>>, Vec<Vec<f64>>, Vec<Vec<f64>>)> =
        BTreeMap::new();
    for (node, matrix) in src.meshes(board_node)? {
        let mesh = src.document["nodes"][node]["mesh"]
            .as_u64()
            .context("missing board mesh")? as usize;
        for primitive in src.document["meshes"][mesh]["primitives"]
            .as_array()
            .context("missing board primitives")?
        {
            let positions = src.attribute(primitive, "POSITION")?;
            let normals = src.attribute(primitive, "NORMAL")?;
            ensure!(
                normals.len() == positions.len(),
                "board normals differ from positions"
            );
            let material = primitive["material"]
                .as_u64()
                .context("board has no material")? as usize;
            let batch = batches.entry(material).or_default();
            for ids in src.indices(primitive, positions.len())?.chunks_exact(3) {
                let mut poly = ids
                    .iter()
                    .map(|i| {
                        matrix
                            .point(&positions[*i])
                            .into_iter()
                            .chain(matrix.normal(&normals[*i]))
                            .collect::<Vec<_>>()
                    })
                    .collect::<Vec<_>>();
                for (axis, bound, greater) in [
                    (0, config.bounds[0], true),
                    (0, config.bounds[1], false),
                    (1, config.bounds[2], true),
                    (1, config.bounds[3], false),
                ] {
                    poly = clip(poly, axis, bound / 1000., greater);
                }
                if poly.len() < 3 {
                    continue;
                }
                let start = batch.0.len();
                for p in &poly {
                    batch.0.push(p[..3].to_vec());
                    batch.1.push(p[3..].to_vec());
                }
                for k in 1..poly.len() - 1 {
                    for i in [start, start + k, start + k + 1] {
                        batch.2.push(vec![i as f64]);
                    }
                }
            }
        }
    }
    let mut primitives = Vec::new();
    for (material, (positions, normals, indices)) in batches {
        if indices.is_empty() {
            continue;
        }
        primitives.push(json!({"attributes":{"POSITION":writer.accessor(&positions,"VEC3",5126)?,"NORMAL":writer.accessor(&normals,"VEC3",5126)?},"indices":writer.accessor(&indices,"SCALAR",5125)?,"material":material}));
    }
    ensure!(!primitives.is_empty(), "empty board crop");
    let mesh = writer.push(
        "meshes",
        json!({"name":"Native board crop","primitives":primitives}),
    );
    let board_output = writer.push("nodes", json!({"name":"PCB","mesh":mesh}));
    let mut faces = Vec::new();
    let mut texture_crops = serde_json::Map::new();
    let sampler = writer.push(
        "samplers",
        json!({"magFilter":9729,"minFilter":9987,"wrapS":33071,"wrapT":33071}),
    );
    for (side, z) in [("top", 0.000705), ("bottom", -0.000705)] {
        let path = source.join(format!("pcba.{side}3d.png"));
        let decoder = png::Decoder::new(Cursor::new(fs::read(&path)?));
        let reader = decoder.read_info()?;
        let (w, h) = (reader.info().width as f64, reader.info().height as f64);
        let left = ((config.bounds[0] - xmin) / board.width * w).floor() as i64;
        let right = ((config.bounds[1] - xmin) / board.width * w).ceil() as i64;
        let top = ((ymax - config.bounds[3]) / board.height * h).floor() as i64;
        let bottom = ((ymax - config.bounds[2]) / board.height * h).ceil() as i64;
        let bounds = [left, top, right, bottom];
        let (png, size) = crop_png(&path, bounds)?;
        texture_crops.insert(side.into(), json!({"sourceSize":size,"pixelBounds":bounds}));
        let view = writer.blob(&png, None);
        let image = writer.push("images", json!({"bufferView":view,"mimeType":"image/png"}));
        let texture = writer.push("textures", json!({"sampler":sampler,"source":image}));
        let material=writer.push("materials",json!({"name":format!("Actual fabrication {side} face"),"pbrMetallicRoughness":{"baseColorTexture":{"index":texture},"metallicFactor":0,"roughnessFactor":0.85}}));
        let [x0, x1, y0, y1] = config.bounds.map(|x| x / 1000.);
        let positions = vec![
            vec![x0, y0, z],
            vec![x1, y0, z],
            vec![x1, y1, z],
            vec![x0, y1, z],
        ];
        let uv = positions
            .iter()
            .map(|p| {
                vec![
                    ((p[0] * 1000. - xmin) / board.width * w - left as f64) / (right - left) as f64,
                    ((ymax - p[1] * 1000.) / board.height * h - top as f64) / (bottom - top) as f64,
                ]
            })
            .collect::<Vec<_>>();
        let indices = if side == "top" {
            [0, 1, 2, 0, 2, 3]
        } else {
            [2, 1, 0, 3, 2, 0]
        };
        faces.push(json!({"attributes":{"POSITION":writer.accessor(&positions,"VEC3",5126)?,"NORMAL":writer.accessor(&vec![vec![0.,0.,if side=="top" {1.}else{-1.}];4],"VEC3",5126)?,"TEXCOORD_0":writer.accessor(&uv,"VEC2",5126)?},"indices":writer.accessor(&indices.map(|i|vec![i as f64]),"SCALAR",5125)?,"material":material}));
    }
    let mesh = writer.push(
        "meshes",
        json!({"name":"Unmodified fabrication textures","primitives":faces}),
    );
    let faces_output = writer.push("nodes", json!({"name":"Fabrication faces","mesh":mesh}));
    writer.document["scenes"][0]["nodes"] = json!([header_output, board_output, faces_output]);
    let mut ports = circuit
        .elements
        .iter()
        .filter_map(|e| match e {
            Element::SourcePort(p) if p.source_component_id == component.source_component_id => {
                Some(p)
            }
            _ => None,
        })
        .collect::<Vec<_>>();
    ensure!(
        ports.iter().all(|p| p.pin_number.is_some()),
        "connector port has no pin number"
    );
    ports.sort_by_key(|p| p.pin_number);
    let pins = ports
        .into_iter()
        .map(|port| {
            let pad = circuit
                .elements
                .iter()
                .find_map(|e| match e {
                    Element::Port(p) if p.source_port_id == port.source_port_id => Some(p),
                    _ => None,
                })
                .context("connector pin has no PCB port")?;
            Ok(json!({"pin":port.pin_number,"label":port.name,"boardMm":[pad.x,pad.y]}))
        })
        .collect::<Result<Vec<_>>>()?;
    let evidence = json!({"source":"hardware/pcb/pcba/out/pcba.glb","sha256":hashes["pcba.glb"],"textures":{"top":hashes["pcba.top3d.png"],"bottom":hashes["pcba.bottom3d.png"]},"header":name,"headerNode":header_node,"headerCad":cad.cad_component_id,"headerPcb":pcb.pcb_component_id,"cropMm":config.bounds,"textureCrops":texture_crops,"pins":pins,"pinTipZMm":pin_tip*1000.,"padSurfaceZMm":board.thickness/2.,"pinMaterialName":config.pin_material,"benchPose":{"scale":1000,"rotationXYZ":config.rotation,"positionMm":config.position},"matingAxis":{"native":[0,0,1],"bench":[0,1,0],"type":"vertical top-entry"},"method":format!("Native {name} connector hierarchy and board triangles clipped in board XY. Source vertex positions, normals, material names and winding are retained. Original fabrication PNG pixels are embedded with matching UV coordinates.")});
    let bytes = writer.bytes()?;
    crate::write(
        &destination.join(format!("{}-board.glb", name.to_lowercase())),
        &bytes,
    )?;
    let mut json = serde_json::to_vec_pretty(&evidence)?;
    json.push(b'\n');
    crate::write(
        &destination.join(format!("{}-board.json", name.to_lowercase())),
        &json,
    )?;
    println!("{name} native PCB crop: {} bytes", bytes.len());
    Ok(())
}
