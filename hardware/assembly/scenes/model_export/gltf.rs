//! Viewer scenes retain the existing presentation buffers and exact named frames.
use super::payload::{Entry, Payload};
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use std::{
    collections::BTreeMap,
    path::{Path, PathBuf},
};
type Matrix = [[f64; 4]; 4];
const ID: Matrix = [
    [1., 0., 0., 0.],
    [0., 1., 0., 0.],
    [0., 0., 1., 0.],
    [0., 0., 0., 1.],
];
const ZUP: Matrix = [
    [1., 0., 0., 0.],
    [0., 0., 1., 0.],
    [0., -1., 0., 0.],
    [0., 0., 0., 1.],
];
fn multiply(a: &Matrix, b: &Matrix) -> Matrix {
    std::array::from_fn(|r| std::array::from_fn(|c| (0..4).map(|k| a[r][k] * b[k][c]).sum()))
}
fn matrix(value: Option<&Value>) -> Result<Matrix> {
    let mut a = ID;
    if let Some(v) = value {
        let rows = v.as_array().context("view matrix")?;
        ensure!(rows.len() == 3 || rows.len() == 4, "view matrix rows");
        for r in 0..rows.len() {
            let row = rows[r].as_array().context("view matrix row")?;
            ensure!(row.len() == 4, "view matrix cols");
            for c in 0..4 {
                a[r][c] = row[c].as_f64().context("view matrix number")?;
            }
        }
    }
    Ok(a)
}
fn flip(value: Option<&Value>) -> Result<Matrix> {
    let Some(value) = value.filter(|v| !v.is_null()) else {
        return Ok(ID);
    };
    let rows = value.as_array().context("flip")?;
    ensure!(rows.len() == 2, "flip axis/degrees");
    let axis = rows[0].as_array().context("flip axis")?;
    let p = [
        axis[0].as_f64().context("axis")?,
        axis[1].as_f64().context("axis")?,
        axis[2].as_f64().context("axis")?,
    ];
    let n = p.iter().map(|v| v * v).sum::<f64>().sqrt();
    ensure!(n > 0., "zero axis");
    let [x, y, z] = p.map(|v| v / n);
    let a = rows[1].as_f64().context("angle")?.to_radians();
    let (c, s) = (a.cos(), a.sin());
    let t = 1. - c;
    Ok([
        [t * x * x + c, t * x * y - s * z, t * x * z + s * y, 0.],
        [t * x * y + s * z, t * y * y + c, t * y * z - s * x, 0.],
        [t * x * z - s * y, t * y * z + s * x, t * z * z + c, 0.],
        [0., 0., 0., 1.],
    ])
}
fn column_major(m: &Matrix) -> Vec<f64> {
    (0..4).flat_map(|c| (0..4).map(move |r| m[r][c])).collect()
}
struct Gltf {
    bin: Vec<u8>,
    views: Vec<Value>,
    accessors: Vec<Value>,
    meshes: Vec<Value>,
    nodes: Vec<Value>,
    materials: Vec<Value>,
    colours: Vec<[f64; 4]>,
}
impl Gltf {
    fn new() -> Self {
        Self {
            bin: Vec::new(),
            views: Vec::new(),
            accessors: Vec::new(),
            meshes: Vec::new(),
            nodes: vec![json!({"name":"world","children":[]})],
            materials: Vec::new(),
            colours: Vec::new(),
        }
    }
    fn buffer(&mut self, bytes: &[u8], target: u32) -> usize {
        while self.bin.len() % 4 != 0 {
            self.bin.push(0)
        }
        let index = self.views.len();
        self.views.push(json!({"buffer":0,"byteOffset":self.bin.len(),"byteLength":bytes.len(),"target":target}));
        self.bin.extend(bytes);
        index
    }
    fn accessor(
        &mut self,
        bytes: &[u8],
        component: u32,
        kind: &str,
        count: usize,
        bounds: Option<([f64; 3], [f64; 3])>,
    ) -> usize {
        let buffer = self.buffer(bytes, if kind == "SCALAR" { 34963 } else { 34962 });
        let mut row = json!({"bufferView":buffer,"byteOffset":0,"componentType":component,"count":count,"type":kind});
        if let Some((lo, hi)) = bounds {
            row["min"] = json!(lo);
            row["max"] = json!(hi);
        }
        let at = self.accessors.len();
        self.accessors.push(row);
        at
    }
    fn material(&mut self, rgba: [f64; 4], finishes: &Value) -> usize {
        if let Some(index) = self.colours.iter().position(|v| *v == rgba) {
            return index;
        }
        let mut rough = 0.6;
        let mut metal = 0.1;
        if let Some(rows) = finishes.as_array() {
            let mut best = 4e-4f64.powi(2);
            for row in rows {
                if let Some(c) = row["rgb"].as_array().filter(|c| c.len() == 3) {
                    let distance = (0..3)
                        .map(|i| (c[i].as_f64().unwrap_or(-9.) - rgba[i]).powi(2))
                        .sum::<f64>();
                    if distance <= best {
                        best = distance;
                        rough = row["roughness"].as_f64().unwrap_or(rough);
                        metal = row["metalness"].as_f64().unwrap_or(metal);
                    }
                }
            }
        }
        let index = self.materials.len();
        let mut row = json!({"name":format!("hsm-rgba-{index}"),"doubleSided":true,"pbrMetallicRoughness":{"baseColorFactor":rgba,"roughnessFactor":rough,"metallicFactor":if rgba[3]<1.{0.}else{metal}}});
        if rgba[3] < 1. {
            row["alphaMode"] = json!("BLEND");
        }
        self.materials.push(row);
        self.colours.push(rgba);
        index
    }
    fn leaf(
        &mut self,
        entry: &Entry,
        node_name: &str,
        transform: &Matrix,
        material: usize,
        parent: usize,
    ) -> Result<()> {
        let positions = entry.floats("pos");
        let mut lo = [f64::INFINITY; 3];
        let mut hi = [f64::NEG_INFINITY; 3];
        for p in positions.chunks_exact(3) {
            for c in 0..3 {
                lo[c] = lo[c].min(p[c] as f64);
                hi[c] = hi[c].max(p[c] as f64);
            }
        }
        let pos = self.accessor(
            &entry.arrays["pos"],
            5126,
            "VEC3",
            positions.len() / 3,
            Some((lo, hi)),
        );
        let nrm = self.accessor(
            &entry.arrays["nrm"],
            5126,
            "VEC3",
            positions.len() / 3,
            None,
        );
        let idx = self.accessor(
            &entry.arrays["idx"],
            5125,
            "SCALAR",
            entry.arrays["idx"].len() / 4,
            None,
        );
        let mesh = self.meshes.len();
        self.meshes.push(json!({"name":entry.name(),"primitives":[{"attributes":{"POSITION":pos,"NORMAL":nrm},"indices":idx,"material":material,"mode":4}]}));
        let node = self.nodes.len();
        self.nodes
            .push(json!({"name":node_name,"mesh":mesh,"matrix":column_major(transform)}));
        self.nodes[parent]["children"]
            .as_array_mut()
            .unwrap()
            .push(json!(node));
        Ok(())
    }
    fn body(
        &mut self,
        name: &str,
        entries: &[&Entry],
        transform: &Matrix,
        rgba: [f64; 4],
        finishes: &Value,
    ) -> Result<()> {
        let material = self.material(rgba, finishes);
        if entries.len() == 1 {
            return self.leaf(entries[0], name, transform, material, 0);
        }
        let parent = self.nodes.len();
        self.nodes
            .push(json!({"name":name,"matrix":column_major(transform),"children":[]}));
        self.nodes[0]["children"]
            .as_array_mut()
            .unwrap()
            .push(json!(parent));
        for entry in entries {
            self.leaf(entry, entry.name(), &ID, material, parent)?;
        }
        Ok(())
    }
    fn encode(mut self) -> Result<Vec<u8>> {
        while self.bin.len() % 4 != 0 {
            self.bin.push(0)
        }
        let roots = self.nodes.remove(0)["children"]
            .as_array()
            .unwrap()
            .iter()
            .map(|v| json!(v.as_u64().unwrap() - 1))
            .collect::<Vec<_>>();
        for node in &mut self.nodes {
            if let Some(children) = node.get_mut("children").and_then(Value::as_array_mut) {
                for child in children {
                    *child = json!(child.as_u64().unwrap() - 1);
                }
            }
        }
        let tree = json!({"asset":{"version":"2.0","generator":"hsm machine-export"},"scene":0,"scenes":[{"nodes":roots}],"nodes":self.nodes,"meshes":self.meshes,"materials":self.materials,"accessors":self.accessors,"bufferViews":self.views,"buffers":[{"byteLength":self.bin.len()}]});
        let mut head = serde_json::to_vec(&tree)?;
        while head.len() % 4 != 0 {
            head.push(b' ')
        }
        let size = 12 + 8 + head.len() + 8 + self.bin.len();
        let mut raw = Vec::with_capacity(size);
        for value in [0x46546c67u32, 2, size as u32, head.len() as u32, 0x4e4f534a] {
            raw.extend(value.to_le_bytes());
        }
        raw.extend(head);
        raw.extend((self.bin.len() as u32).to_le_bytes());
        raw.extend(0x004e4942u32.to_le_bytes());
        raw.extend(self.bin);
        Ok(raw)
    }
}
fn grouped(payload: &Payload) -> BTreeMap<String, Vec<&Entry>> {
    let mut out = BTreeMap::new();
    for entry in &payload.meshes {
        out.entry(entry.body().to_owned())
            .or_insert_with(Vec::new)
            .push(entry);
    }
    out
}
fn rgba(value: Option<&Value>, entries: &[&Entry]) -> Result<[f64; 4]> {
    let color = value
        .or_else(|| entries[0].meta.get("color"))
        .context("missing scene colour")?;
    let c = color.as_array().context("scene colour")?;
    ensure!(c.len() == 3 || c.len() == 4, "RGB or RGBA");
    Ok([
        c[0].as_f64().context("red")?,
        c[1].as_f64().context("green")?,
        c[2].as_f64().context("blue")?,
        c.get(3).and_then(Value::as_f64).unwrap_or(1.),
    ])
}
pub fn write_views(spec: &Value, output: &Path) -> Result<Value> {
    let outer = Payload::read(Path::new(super::text(spec, "outer_payload")?))?;
    let core = if let Some(path) = spec["core_payload"].as_str() {
        Some(Payload::read(Path::new(path))?)
    } else {
        None
    };
    let outer = grouped(&outer);
    let core = core.as_ref().map(grouped).unwrap_or_default();
    let carry = matrix(spec.get("core_transform"))?;
    let mut files = Vec::new();
    for view in spec["views"].as_array().context("views")? {
        let turn = if view.get("transform").is_some() {
            matrix(view.get("transform"))?
        } else {
            multiply(&ZUP, &flip(view.get("flip"))?)
        };
        let inner_turn = multiply(&turn, &carry);
        let mut gltf = Gltf::new();
        let names = view
            .get("bodies")
            .or_else(|| view.get("names"))
            .and_then(Value::as_array)
            .context("view bodies")?;
        for value in names {
            let name = value.as_str().context("body name")?;
            let qualified = if name.starts_with("cold-core/") {
                name.to_owned()
            } else {
                format!("cold-core/{name}")
            };
            let mut source = name;
            let mut inside = false;
            let entries = if let Some(rows) = outer.get(name) {
                rows
            } else if let Some(rows) = outer.get(&qualified) {
                source = &qualified;
                rows
            } else {
                inside = true;
                source = name.strip_prefix("cold-core/").unwrap_or(name);
                core.get(source)
                    .with_context(|| format!("scene missing {name}"))?
            };
            let mut color = view["overrides"].get(name).or_else(|| {
                if inside {
                    spec["core_colours"].get(source)
                } else {
                    spec["colours"].get(source)
                }
            });
            if color.is_none() {
                color = spec["colors"].get(source);
            }
            let col = rgba(color, entries)?;
            gltf.body(
                name,
                entries,
                if inside { &inner_turn } else { &turn },
                col,
                &spec["finishes"],
            )?;
        }
        let path = view["file"].as_str().map(PathBuf::from).unwrap_or_else(|| {
            output.join(format!("{}.glb", view["id"].as_str().unwrap_or("scene")))
        });
        super::put(&path, &gltf.encode()?)?;
        files.push(super::output_name(&path, output));
    }
    Ok(json!({"files":files,"bodies":[]}))
}
