//! Native scene descriptors carry authored geometry, surfaces and absolute frame poses to Blender.
use crate::{root, write};
use anyhow::{Context, Result};
use serde::Serialize;
use serde_json::{Value, json};
use std::{collections::BTreeMap, fs, path::Path};

pub type V3 = [f64; 3];
pub fn add(a: V3, b: V3) -> V3 {
    std::array::from_fn(|i| a[i] + b[i])
}
pub fn sub(a: V3, b: V3) -> V3 {
    std::array::from_fn(|i| a[i] - b[i])
}
pub fn mul(a: V3, s: f64) -> V3 {
    a.map(|x| x * s)
}
pub fn dot(a: V3, b: V3) -> f64 {
    a.into_iter().zip(b).map(|(x, y)| x * y).sum()
}
pub fn cross(a: V3, b: V3) -> V3 {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
pub fn length(a: V3) -> f64 {
    dot(a, a).sqrt()
}
pub fn unit(a: V3) -> V3 {
    mul(a, 1. / length(a).max(1e-20))
}
pub fn blend(a: V3, b: V3, t: f64) -> V3 {
    add(a, mul(sub(b, a), t))
}
pub fn ease(t: f64) -> f64 {
    let t = t.clamp(0., 1.);
    t * t * (3. - 2. * t)
}
pub fn linear(hex: &str) -> V3 {
    let c = crate::draw::rgba(hex);
    [c.red(), c.green(), c.blue()].map(|x| {
        let x = x as f64;
        if x <= 0.04045 {
            x / 12.92
        } else {
            ((x + 0.055) / 1.055).powf(2.4)
        }
    })
}

pub fn payload_bytes(path: &str, select: &impl Fn(&str) -> bool) -> Result<Vec<u8>> {
    let bytes = fs::read(root().join(path))?;
    let (header, _) = hsm_kernel::scene::header(&bytes)?;
    let mut selected = Vec::new();
    let mut index = 0;
    for node in header["meshes"].as_array().context("payload entries")? {
        if header["v"] == 4 {
            for entry in node["entries"].as_array().context("scene entries")? {
                if select(entry["name"].as_str().context("scene entry name")?) {
                    selected.push(index);
                }
                index += 1;
            }
        } else {
            if select(node["name"].as_str().context("payload entry name")?) {
                selected.push(index);
            }
            index += 1;
        }
    }
    hsm_kernel::scene::flatten_selected_with(&bytes, &selected, hsm_kernel::scene::load_asset)
}
pub fn read_payload(
    path: &str,
    select: &impl Fn(&str) -> bool,
) -> Result<Vec<hsm_render::payload::RawMesh>> {
    hsm_render::payload::decode(&payload_bytes(path, select)?)
}

#[derive(Serialize, Clone, Copy)]
pub struct Array {
    offset: usize,
    count: usize,
}
#[derive(Serialize, Clone)]
pub struct Mesh {
    pub vertices: Array,
    pub triangles: Array,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub normals: Option<Array>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub uv: Option<Array>,
    pub smooth: bool,
}
#[derive(Serialize, Clone)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum Geometry {
    Mesh(Mesh),
    Instance {
        source: String,
    },
    Curve {
        points: Vec<V3>,
        radius: f64,
        bezier: bool,
        closed: bool,
    },
    Text {
        body: String,
        font: String,
        size: f64,
        align: String,
    },
    Empty,
    Area {
        energy: f64,
        size: f64,
        size_y: Option<f64>,
        color: V3,
    },
}
#[derive(Serialize, Clone)]
pub struct Object {
    pub name: String,
    pub geometry: Geometry,
    pub location: V3,
    pub rotation: V3,
    pub scale: V3,
    pub material: Option<String>,
    pub parent: Option<String>,
    pub hidden: bool,
    pub transmission: bool,
    pub glossy: bool,
    pub camera: bool,
    pub diffuse: bool,
    pub shadow: bool,
    pub receivers: Vec<String>,
    pub bevel: f64,
    pub bevel_segments: usize,
    pub normals: bool,
    pub difference: Vec<String>,
}
#[derive(Serialize, Clone)]
pub struct Node {
    pub id: String,
    pub kind: String,
    pub inputs: BTreeMap<String, Value>,
    pub properties: BTreeMap<String, Value>,
    pub ramp: Option<Vec<(f64, [f64; 4])>>,
}
#[derive(Serialize, Clone)]
pub struct Link {
    pub from: String,
    pub output: String,
    pub to: String,
    pub input: String,
}
#[derive(Serialize, Clone)]
pub struct Material {
    pub name: String,
    pub base: V3,
    pub roughness: f64,
    pub metal: f64,
    pub transmission: f64,
    pub ior: f64,
    pub emission: f64,
    pub specular: Option<f64>,
    pub anisotropy: Option<f64>,
    pub texture: Option<String>,
    pub nodes: Vec<Node>,
    pub links: Vec<Link>,
}
impl Material {
    pub fn new(name: &str, color: V3, roughness: f64) -> Self {
        Self {
            name: name.into(),
            base: color,
            roughness,
            metal: 0.,
            transmission: 0.,
            ior: 1.45,
            emission: 0.,
            specular: None,
            anisotropy: None,
            texture: None,
            nodes: Vec::new(),
            links: Vec::new(),
        }
    }
    pub fn node(
        &mut self,
        id: &str,
        kind: &str,
        inputs: &[(&str, Value)],
        properties: &[(&str, Value)],
    ) {
        self.nodes.push(Node {
            id: id.into(),
            kind: kind.into(),
            inputs: inputs
                .iter()
                .map(|(k, v)| (k.to_string(), v.clone()))
                .collect(),
            properties: properties
                .iter()
                .map(|(k, v)| (k.to_string(), v.clone()))
                .collect(),
            ramp: None,
        });
    }
    pub fn link(&mut self, from: &str, output: &str, to: &str, input: &str) {
        self.links.push(Link {
            from: from.into(),
            output: output.into(),
            to: to.into(),
            input: input.into(),
        });
    }
    pub fn grain(&mut self, scale: f64, strength: f64, distance: f64) {
        self.node(
            "grain",
            "ShaderNodeTexNoise",
            &[("Scale", json!(scale)), ("Detail", json!(2))],
            &[],
        );
        self.node(
            "bump",
            "ShaderNodeBump",
            &[("Strength", json!(strength)), ("Distance", json!(distance))],
            &[],
        );
        self.link("grain", "Fac", "bump", "Height");
        self.link("bump", "Normal", "Principled BSDF", "Normal");
    }
    pub fn clear(&mut self, tint: V3, roughness: f64, reflection: f64, fresnel: bool) {
        self.node(
            "clear",
            "ShaderNodeBsdfTransparent",
            &[("Color", json!([tint[0], tint[1], tint[2], 1.]))],
            &[],
        );
        self.node(
            "gloss",
            "ShaderNodeBsdfAnisotropic",
            &[
                ("Color", json!([1., 1., 1., 1.])),
                ("Roughness", json!(roughness)),
            ],
            &[],
        );
        self.node(
            "mix",
            "ShaderNodeMixShader",
            &[("0", json!(reflection))],
            &[],
        );
        if fresnel {
            self.node(
                "fresnel",
                "ShaderNodeFresnel",
                &[("IOR", json!(1.333))],
                &[],
            );
            self.node(
                "amount",
                "ShaderNodeMath",
                &[("1", json!(reflection))],
                &[("operation", json!("MULTIPLY"))],
            );
            self.link("fresnel", "Fac", "amount", "0");
            self.link("amount", "0", "mix", "0");
        }
        self.link("clear", "BSDF", "mix", "1");
        self.link("gloss", "BSDF", "mix", "2");
        self.link("mix", "Shader", "Material Output", "Surface");
    }
}
#[derive(Serialize, Clone)]
pub struct Camera {
    pub position: V3,
    pub target: V3,
    pub ortho: Option<f64>,
    pub lens: f64,
    pub focus: Option<V3>,
    pub aperture: f64,
}
#[derive(Serialize, Default, Clone)]
pub struct Update {
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub location: Option<V3>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rotation: Option<V3>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scale: Option<V3>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub hidden: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub vertices: Option<Array>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub energy: Option<f64>,
}
#[derive(Serialize)]
pub struct Frame {
    pub number: usize,
    pub file: String,
    pub width: u32,
    pub height: u32,
    pub camera: Camera,
    pub updates: Vec<Update>,
    pub node_inputs: Vec<(String, String, String, Value)>,
}
#[derive(Serialize)]
pub struct Settings {
    pub samples: usize,
    pub threshold: f64,
    pub max_bounces: usize,
    pub transmission_bounces: usize,
    pub transparent_bounces: usize,
    pub seed: usize,
    pub transparent: bool,
    pub look: String,
    pub world: V3,
    pub world_strength: f64,
}
impl Default for Settings {
    fn default() -> Self {
        Self {
            samples: 32,
            threshold: 0.035,
            max_bounces: 10,
            transmission_bounces: 8,
            transparent_bounces: 8,
            seed: 78,
            transparent: false,
            look: "AgX - Medium High Contrast".into(),
            world: linear("#E7EEF8"),
            world_strength: 0.24,
        }
    }
}
#[derive(Serialize)]
pub struct Scene {
    pub buffer: String,
    pub settings: Settings,
    pub materials: Vec<Material>,
    pub objects: Vec<Object>,
    pub frames: Vec<Frame>,
    pub save: Option<String>,
    #[serde(skip)]
    pub binary: Vec<u8>,
}
impl Scene {
    pub fn new() -> Self {
        Self {
            buffer: String::new(),
            settings: Settings::default(),
            materials: Vec::new(),
            objects: Vec::new(),
            frames: Vec::new(),
            save: None,
            binary: Vec::new(),
        }
    }
    pub fn floats(&mut self, values: impl IntoIterator<Item = f64>) -> Array {
        let offset = self.binary.len();
        for value in values {
            self.binary.extend_from_slice(&(value as f32).to_le_bytes());
        }
        Array {
            offset,
            count: (self.binary.len() - offset) / 4,
        }
    }
    fn indices(&mut self, values: impl IntoIterator<Item = u32>) -> Array {
        let offset = self.binary.len();
        for value in values {
            self.binary.extend_from_slice(&value.to_le_bytes());
        }
        Array {
            offset,
            count: (self.binary.len() - offset) / 4,
        }
    }
    pub fn mesh(
        &mut self,
        vertices: Vec<V3>,
        faces: Vec<Vec<usize>>,
        normals: Option<Vec<V3>>,
        uv: Option<Vec<[f64; 2]>>,
        smooth: bool,
    ) -> Geometry {
        let triangles = faces
            .into_iter()
            .flat_map(|face| {
                (1..face.len().saturating_sub(1))
                    .map(move |i| [face[0] as u32, face[i] as u32, face[i + 1] as u32])
                    .collect::<Vec<_>>()
            })
            .flatten();
        let vertices = self.floats(vertices.into_iter().flatten());
        let triangles = self.indices(triangles);
        let normals = normals.map(|data| self.floats(data.into_iter().flatten()));
        let uv = uv.map(|data| self.floats(data.into_iter().flatten()));
        Geometry::Mesh(Mesh {
            vertices,
            triangles,
            normals,
            uv,
            smooth,
        })
    }
    pub fn object(
        &mut self,
        name: &str,
        geometry: Geometry,
        material: Option<&str>,
        location: V3,
    ) -> usize {
        let i = self.objects.len();
        self.objects.push(Object {
            name: name.into(),
            geometry,
            location,
            rotation: [0.; 3],
            scale: [1.; 3],
            material: material.map(str::to_owned),
            parent: None,
            hidden: false,
            transmission: true,
            glossy: true,
            camera: true,
            diffuse: true,
            shadow: true,
            receivers: Vec::new(),
            bevel: 0.,
            bevel_segments: 3,
            normals: false,
            difference: Vec::new(),
        });
        i
    }
    pub fn material(&mut self, name: &str, hex: &str, roughness: f64) -> usize {
        let i = self.materials.len();
        self.materials
            .push(Material::new(name, linear(hex), roughness));
        i
    }
    pub fn box_(&mut self, name: &str, size: V3, at: V3, material: &str, bevel: f64) -> usize {
        let v = [
            [-1., -1., -1.],
            [1., -1., -1.],
            [1., 1., -1.],
            [-1., 1., -1.],
            [-1., -1., 1.],
            [1., -1., 1.],
            [1., 1., 1.],
            [-1., 1., 1.],
        ]
        .map(|p| std::array::from_fn(|k| p[k] * size[k] / 2.))
        .to_vec();
        let faces = [
            [0, 3, 2, 1],
            [4, 5, 6, 7],
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
        ]
        .map(|f| f.to_vec())
        .to_vec();
        let mesh = self.mesh(v, faces, None, None, false);
        let i = self.object(name, mesh, Some(material), at);
        self.objects[i].bevel = bevel;
        self.objects[i].normals = bevel > 0.;
        i
    }
    pub fn lathe(
        &mut self,
        name: &str,
        profile: &[[f64; 2]],
        material: &str,
        at: V3,
        sides: usize,
        split: bool,
    ) -> usize {
        let mut vertices = Vec::new();
        let mut normals = Vec::new();
        let mut faces = Vec::new();
        if split {
            for (j, pair) in profile.windows(2).enumerate() {
                let [r0, z0] = pair[0];
                let [r1, z1] = pair[1];
                let length = (r1 - r0).hypot(z1 - z0);
                let nr = (z1 - z0) / length;
                let nz = -(r1 - r0) / length;
                for [r, z] in [pair[0], pair[1]] {
                    for i in 0..sides {
                        let a = i as f64 * std::f64::consts::TAU / sides as f64;
                        vertices.push([r * a.cos(), r * a.sin(), z]);
                        normals.push([nr * a.cos(), nr * a.sin(), nz]);
                    }
                }
                let start = j * sides * 2;
                for i in 0..sides {
                    faces.push(vec![
                        start + i,
                        start + (i + 1) % sides,
                        start + sides + (i + 1) % sides,
                        start + sides + i,
                    ]);
                }
            }
        } else {
            for [r, z] in profile {
                for i in 0..sides {
                    let a = i as f64 * std::f64::consts::TAU / sides as f64;
                    vertices.push([r * a.cos(), r * a.sin(), *z]);
                }
            }
            for j in 0..profile.len() - 1 {
                for i in 0..sides {
                    faces.push(vec![
                        j * sides + i,
                        j * sides + (i + 1) % sides,
                        (j + 1) * sides + (i + 1) % sides,
                        (j + 1) * sides + i,
                    ]);
                }
            }
        }
        let mesh = self.mesh(
            vertices,
            faces,
            if split { Some(normals) } else { None },
            None,
            true,
        );
        self.object(name, mesh, Some(material), at)
    }
    pub fn cylinder(&mut self, name: &str, r: f64, h: f64, at: V3, material: &str) -> usize {
        let i = self.lathe(
            name,
            &[[0., -h / 2.], [r, -h / 2.], [r, h / 2.], [0., h / 2.]],
            material,
            at,
            96,
            true,
        );
        self.objects[i].bevel = 0.0012_f64.min(h / 6.);
        i
    }
    pub fn sphere(
        &mut self,
        name: &str,
        radius: f64,
        at: V3,
        material: &str,
        sides: usize,
        rings: usize,
    ) -> usize {
        let mut vertices = Vec::new();
        let mut normals = Vec::new();
        let mut faces = Vec::new();
        for j in 0..=rings {
            let a = j as f64 * std::f64::consts::PI / rings as f64;
            for i in 0..sides {
                let b = i as f64 * std::f64::consts::TAU / sides as f64;
                let p = [a.sin() * b.cos(), a.sin() * b.sin(), a.cos()];
                vertices.push(mul(p, radius));
                normals.push(p);
            }
        }
        for j in 0..rings {
            for i in 0..sides {
                faces.push(vec![
                    j * sides + i,
                    j * sides + (i + 1) % sides,
                    (j + 1) * sides + (i + 1) % sides,
                    (j + 1) * sides + i,
                ]);
            }
        }
        let mesh = self.mesh(vertices, faces, Some(normals), None, true);
        self.object(name, mesh, Some(material), at)
    }
    pub fn tube(&mut self, name: &str, points: &[V3], radius: f64, material: &str) -> usize {
        self.object(
            name,
            Geometry::Curve {
                points: points.to_vec(),
                radius,
                bezier: true,
                closed: false,
            },
            Some(material),
            [0.; 3],
        )
    }
    pub fn light(
        &mut self,
        name: &str,
        at: V3,
        target: V3,
        energy: f64,
        size: f64,
        color: &str,
    ) -> usize {
        let i = self.object(
            name,
            Geometry::Area {
                energy,
                size,
                size_y: None,
                color: linear(color),
            },
            None,
            at,
        );
        self.objects[i].rotation = track(sub(target, at));
        i
    }
    pub fn load(
        &mut self,
        path: &str,
        select: impl Fn(&str) -> bool,
        material: impl Fn(&hsm_render::payload::RawMesh) -> String,
        at: V3,
        rotation: f64,
        floor: Option<f64>,
    ) -> Result<Vec<usize>> {
        let mut objects = Vec::new();
        for raw in read_payload(path, &select)? {
            if !select(&raw.name) {
                continue;
            }
            let faces = raw
                .indices
                .chunks_exact(3)
                .filter(|face| {
                    floor.is_none_or(|floor| {
                        face.iter()
                            .all(|&i| raw.positions[i as usize][2] as f64 >= floor)
                    })
                })
                .map(|face| face.iter().map(|&i| i as usize).collect())
                .collect();
            let mesh = self.mesh(
                raw.positions
                    .iter()
                    .map(|p| p.map(|x| x as f64 * 0.001))
                    .collect(),
                faces,
                Some(raw.normals.iter().map(|p| p.map(|x| x as f64)).collect()),
                raw.uv
                    .as_ref()
                    .map(|p| p.iter().map(|p| p.map(|x| x as f64)).collect()),
                true,
            );
            let i = self.object(&raw.name, mesh, Some(&material(&raw)), at);
            self.objects[i].rotation[2] = rotation;
            objects.push(i);
        }
        Ok(objects)
    }
    pub fn write(&mut self, path: &Path) -> Result<()> {
        let buffer = path.with_extension("bin");
        self.buffer = buffer.to_string_lossy().into();
        write(buffer, &self.binary)?;
        write(path, serde_json::to_vec(self)?)
    }
    pub fn mesh_vertices(&self, index: usize) -> Result<Vec<V3>> {
        let Geometry::Mesh(mesh) = &self.objects[index].geometry else {
            anyhow::bail!("object is not a mesh");
        };
        Ok(
            self.binary[mesh.vertices.offset..mesh.vertices.offset + mesh.vertices.count * 4]
                .chunks_exact(12)
                .map(|p| {
                    std::array::from_fn(|i| {
                        f32::from_le_bytes(p[i * 4..i * 4 + 4].try_into().unwrap()) as f64
                    })
                })
                .collect(),
        )
    }
    pub fn uv(&mut self, index: usize, uv: Vec<[f64; 2]>) {
        let span = self.floats(uv.into_iter().flatten());
        if let Geometry::Mesh(mesh) = &mut self.objects[index].geometry {
            mesh.uv = Some(span);
        }
    }
}
/// XYZ Euler orientation of a local camera/light looking down its negative Z axis.
pub fn track(direction: V3) -> V3 {
    let d = unit(direction);
    [(-d[2]).acos(), 0., (-d[0]).atan2(d[1])]
}

pub struct Random(u64);
impl Random {
    pub fn new(seed: u64) -> Self {
        Self(seed)
    }
    pub fn uniform(&mut self, lo: f64, hi: f64) -> f64 {
        self.0 ^= self.0 >> 12;
        self.0 ^= self.0 << 25;
        self.0 ^= self.0 >> 27;
        let value = self.0.wrapping_mul(2685821657736338717);
        lo + (hi - lo) * ((value >> 11) as f64 / (1_u64 << 53) as f64)
    }
}
