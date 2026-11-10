//! The faucet portrait evaluates gravity-driven jets, a continuous drink surface and fine carbonation.
use super::clock::Shot;
use crate::{kitchen, scene::*};
use anyhow::{Context, Result};
use serde_json::json;
use std::{
    f64::consts::{PI, TAU},
    path::Path,
};

const GLASS: V3 = [0.145, -0.151, 0.0004];
const FAUCET: V3 = [0.145, 0.045, 0.];
const SIDES: usize = 112;
const RINGS: usize = 40;
const STREAM_RINGS: usize = 52;
const STREAM_SIDES: usize = 12;
fn water_outlet() -> V3 {
    add(FAUCET, [0., -0.1339967220, 0.1803887434])
}
fn inner_radius(z: f64) -> f64 {
    0.0335 + (0.03675 - 0.0335) * ((z - 0.009) / (0.0834 - 0.009)).clamp(0., 1.)
}
fn trajectory(outlet: V3, speed: f64, level: f64, fraction: f64) -> (V3, V3) {
    let angle = 140_f64.to_radians();
    let velocity = mul([0., -angle.sin(), angle.cos()], speed);
    let drop = outlet[2] - (GLASS[2] + level);
    let flight = (velocity[2] + (velocity[2] * velocity[2] + 2. * 9.81 * drop).sqrt()) / 9.81;
    let dt = flight * fraction;
    (
        add(
            add(outlet, mul(velocity, dt)),
            [0., 0., -0.5 * 9.81 * dt * dt],
        ),
        add(velocity, [0., 0., -9.81 * dt]),
    )
}
struct Bubble {
    name: String,
    x: f64,
    y: f64,
    phase: f64,
    speed: f64,
    size: f64,
}
struct Impact {
    name: String,
    angle: f64,
    distance: f64,
    size: f64,
    phase: f64,
}
pub struct Beverage {
    pub scene: Scene,
    faucet: Vec<String>,
    liquid: String,
    vertices: Vec<V3>,
    surface_start: usize,
    outer_ring: usize,
    side_top: usize,
    surface: Vec<(f64, f64, f64)>,
    bubbles: Vec<Bubble>,
    wall: Vec<(String, f64)>,
    impact: Vec<Impact>,
    drops: Vec<Impact>,
}
fn instance(scene: &mut Scene, name: &str, source: &str, at: V3, scale: V3) -> usize {
    let i = scene.object(
        name,
        Geometry::Instance {
            source: source.into(),
        },
        None,
        at,
    );
    scene.objects[i].scale = scale;
    i
}
impl Beverage {
    pub fn new(out: &Path, samples: usize) -> Result<Self> {
        let mut scene = Scene::new();
        scene.settings.samples = samples;
        scene.settings.world = linear("#E9F1F5");
        scene.settings.world_strength = 0.18;
        for (name, hex, rough) in [
            ("shell", "#0E1216", 0.66),
            ("rubber", "#15191D", 0.88),
            ("hardware", "#202428", 0.56),
            ("display", "#101A20", 0.17),
        ] {
            scene.material(name, hex, rough);
        }
        scene.materials[0].grain(1450., 0.10, 0.000008);
        let visible = [
            "westbrass",
            "soda_faucet_tube",
            "flavor_tube_pos_x",
            "flavor_tube_neg_x",
            "lever",
            "above_counter_plate",
            "above_counter_gasket",
            "shell_base",
            "shell_tip",
            "faucet-display-cover-seated",
            "faucet_display",
            "faucet_display_screen",
        ];
        let indices = scene.load(
            "hardware/faucet-layout/faucet-assembly.step.mesh",
            |n| visible.contains(&n),
            |m| {
                if ["faucet_display", "faucet_display_screen"].contains(&m.name.as_str()) {
                    "display"
                } else if m.name == "above_counter_gasket" {
                    "rubber"
                } else if [
                    "westbrass",
                    "soda_faucet_tube",
                    "flavor_tube_pos_x",
                    "flavor_tube_neg_x",
                ]
                .contains(&m.name.as_str())
                {
                    "hardware"
                } else {
                    "shell"
                }
                .into()
            },
            FAUCET,
            0.,
            Some(-0.2),
        )?;
        let faucet: Vec<_> = indices
            .iter()
            .map(|&i| scene.objects[i].name.clone())
            .collect();
        for &i in &indices {
            scene.objects[i].transmission = false;
            scene.objects[i].glossy = false;
        }
        let screen = *indices
            .iter()
            .find(|&&i| scene.objects[i].name == "faucet_display_screen")
            .context("faucet screen")?;
        let i = scene.material("selected-display", "#FFFFFF", 0.24);
        scene.materials[i].texture = Some(kitchen::texture(1, out)?);
        scene.materials[i].emission = 0.32;
        scene.objects[screen].material = Some("selected-display".into());
        let vertices = scene.mesh_vertices(screen)?;
        scene.uv(
            screen,
            vertices
                .iter()
                .map(|v| {
                    [
                        (v[0] + 0.00888) / 0.01776,
                        (v[2] - 0.19962) / (0.22510 - 0.19962),
                    ]
                })
                .collect(),
        );
        let lever = *indices
            .iter()
            .find(|&&i| scene.objects[i].name == "lever")
            .context("faucet lever")?;
        let vertices = scene
            .mesh_vertices(lever)?
            .into_iter()
            .map(|v| sub(v, [0., 0., 0.046]))
            .flatten();
        let span = scene.floats(vertices);
        if let Geometry::Mesh(m) = &mut scene.objects[lever].geometry {
            m.vertices = span;
        }
        scene.objects[lever].location = add(scene.objects[lever].location, [0., 0., 0.046]);
        let i = scene.material("glass", "#FFFFFF", 0.040);
        scene.materials[i].transmission = 1.;
        scene.materials[i].ior = 1.46;
        scene.lathe(
            "Short everyday soda tumbler",
            &[
                [0., 0.],
                [0.0285, 0.],
                [0.0334, 0.0007],
                [0.0342, 0.0027],
                [0.0350, 0.0090],
                [0.0382, 0.0834],
                [0.03835, 0.0851],
                [0.03815, 0.0860],
                [0.03765, 0.08645],
                [0.03710, 0.08620],
                [0.03685, 0.0855],
                [0.03675, 0.0834],
                [0.0335, 0.0090],
                [0.0326, 0.0054],
                [0.0285, 0.0048],
                [0., 0.0048],
            ],
            "glass",
            GLASS,
            128,
            true,
        );
        let mut soda = Material::new("soda", [1.; 3], 0.5);
        soda.clear([0.98, 1., 0.70], 0.050, 0.85, true);
        soda.node(
            "absorption",
            "ShaderNodeVolumeAbsorption",
            &[
                ("Color", json!([0.92, 0.98, 0.06, 1.])),
                ("Density", json!(38)),
            ],
            &[],
        );
        soda.link("absorption", "Volume", "Material Output", "Volume");
        scene.materials.push(soda);
        let mut water = Material::new("water", [1.; 3], 0.5);
        water.clear([0.985, 0.995, 1.], 0.12, 0.92, true);
        water.node("position", "ShaderNodeNewGeometry", &[], &[]);
        water.node(
            "flow-noise",
            "ShaderNodeTexNoise",
            &[("Scale", json!(650)), ("Detail", json!(2))],
            &[("noise_dimensions", json!("4D"))],
        );
        water.node(
            "flow-bump",
            "ShaderNodeBump",
            &[("Strength", json!(0.28)), ("Distance", json!(0.000075))],
            &[],
        );
        water.link("position", "Position", "flow-noise", "Vector");
        water.link("flow-noise", "Fac", "flow-bump", "Height");
        water.link("flow-bump", "Normal", "gloss", "Normal");
        water.node(
            "aeration",
            "ShaderNodeBsdfDiffuse",
            &[
                ("Color", json!([0.92, 0.97, 1., 1.])),
                ("Roughness", json!(0.25)),
            ],
            &[],
        );
        water.node(
            "aeration-mix",
            "ShaderNodeMixShader",
            &[("0", json!(0.085))],
            &[],
        );
        water.link("mix", "Shader", "aeration-mix", "1");
        water.link("aeration", "BSDF", "aeration-mix", "2");
        water.link("aeration-mix", "Shader", "Material Output", "Surface");
        scene.materials.push(water);
        let mut flavor = Material::new("flavor", [1.; 3], 0.5);
        flavor.clear([0.87, 0.98, 0.47], 0.12, 0.75, true);
        scene.materials.push(flavor);
        let mut condensation = Material::new("condensation", [1.; 3], 0.035);
        condensation.transmission = 1.;
        condensation.ior = 1.333;
        scene.materials.push(condensation);
        let mut air = Material::new("air", [1.; 3], 0.5);
        air.clear([1.; 3], 0.045, 0.9, true);
        air.node(
            "glint-fresnel",
            "ShaderNodeFresnel",
            &[("IOR", json!(1.333))],
            &[],
        );
        air.node(
            "glint-strength",
            "ShaderNodeMath",
            &[("1", json!(0.85))],
            &[("operation", json!("MULTIPLY"))],
        );
        air.node(
            "glint",
            "ShaderNodeEmission",
            &[("Color", json!([0.80, 0.94, 1., 1.]))],
            &[],
        );
        air.node("glint-add", "ShaderNodeAddShader", &[], &[]);
        air.link("glint-fresnel", "Fac", "glint-strength", "0");
        air.link("glint-strength", "0", "glint", "Strength");
        air.link("mix", "Shader", "glint-add", "0");
        air.link("glint", "Emission", "glint-add", "1");
        air.link("glint-add", "Shader", "Material Output", "Surface");
        scene.materials.push(air);
        let mut vertices = vec![[0., 0., 0.0049]];
        for i in 0..SIDES {
            let a = TAU * i as f64 / SIDES as f64;
            vertices.push([0.0327 * a.cos(), 0.0327 * a.sin(), 0.0049]);
        }
        let surface_start = vertices.len();
        vertices.push([0., 0., 0.0715]);
        let mut surface = vec![(0., 0., 0.)];
        for ring in 1..=RINGS {
            let fraction = ring as f64 / RINGS as f64;
            for side in 0..SIDES {
                let a = TAU * side as f64 / SIDES as f64;
                vertices.push([
                    fraction * 0.0362 * a.cos(),
                    fraction * 0.0362 * a.sin(),
                    0.0715,
                ]);
                surface.push((fraction, a.cos(), a.sin()));
            }
        }
        let mut faces: Vec<_> = (0..SIDES)
            .map(|i| vec![0, 1 + (i + 1) % SIDES, 1 + i])
            .collect();
        let first = surface_start + 1;
        faces.extend((0..SIDES).map(|i| vec![surface_start, first + i, first + (i + 1) % SIDES]));
        for ring in 0..RINGS - 1 {
            let lower = first + ring * SIDES;
            let upper = first + (ring + 1) * SIDES;
            faces.extend((0..SIDES).map(|i| {
                vec![
                    lower + i,
                    upper + i,
                    upper + (i + 1) % SIDES,
                    lower + (i + 1) % SIDES,
                ]
            }));
        }
        let outer_ring = first + (RINGS - 1) * SIDES;
        let side_start = vertices.len();
        for i in 0..SIDES {
            let a = TAU * i as f64 / SIDES as f64;
            vertices.push([0.0327 * a.cos(), 0.0327 * a.sin(), 0.0049]);
        }
        let side_top = vertices.len();
        for i in 0..SIDES {
            vertices.push(vertices[outer_ring + i]);
        }
        faces.extend((0..SIDES).map(|i| {
            vec![
                side_start + i,
                side_start + (i + 1) % SIDES,
                side_top + (i + 1) % SIDES,
                side_top + i,
            ]
        }));
        let mesh = scene.mesh(vertices.clone(), faces, None, None, true);
        let liquid = "Soda volume with continuous meniscus".to_string();
        scene.object(&liquid, mesh, Some("soda"), GLASS);
        let i = scene.sphere(
            "Condensation template",
            1.,
            [0., 0., -10.],
            "condensation",
            12,
            8,
        );
        scene.objects[i].hidden = true;
        let i = scene.sphere("Carbonation template", 1., [0., 0., -10.], "air", 12, 8);
        scene.objects[i].hidden = true;
        let mut rng = Random::new(718);
        for i in 0..300 {
            let angle = rng.uniform(0., TAU);
            let z = rng.uniform(0.010, 0.080);
            let size = if i % 3 != 0 {
                rng.uniform(0.00015, 0.00048)
            } else {
                rng.uniform(0.00048, 0.00090)
            };
            let radius = 0.035 + 0.0032 * (z - 0.009) / 0.0744;
            let i = instance(
                &mut scene,
                &format!("Condensation bead {i}"),
                "Condensation template",
                add(
                    GLASS,
                    [
                        (radius + size * 0.13) * angle.cos(),
                        (radius + size * 0.13) * angle.sin(),
                        z,
                    ],
                ),
                [size * 0.44, size, size * rng.uniform(1.1, 1.75)],
            );
            scene.objects[i].rotation[2] = angle;
        }
        let mut bubbles = Vec::new();
        for lane in 0..30 {
            let angle = if lane < 18 {
                rng.uniform(-2.6, -0.2)
            } else {
                rng.uniform(0., TAU)
            };
            let radius = if lane < 18 {
                rng.uniform(0.024, 0.032)
            } else {
                rng.uniform(0.009, 0.030)
            };
            let speed = rng.uniform(0.012, 0.023);
            for bead in 0..25 {
                let name = format!("Fine carbonation lane {lane} bead {bead}");
                instance(
                    &mut scene,
                    &name,
                    "Carbonation template",
                    GLASS,
                    [0.0002; 3],
                );
                bubbles.push(Bubble {
                    name,
                    x: radius * angle.cos(),
                    y: radius * angle.sin(),
                    phase: (bead as f64 / 25. + rng.uniform(0., 0.012)) % 1.,
                    speed,
                    size: rng.uniform(0.00012, 0.00030),
                });
            }
        }
        let mut wall = Vec::new();
        for i in 0..220 {
            let z = rng.uniform(0.009, 0.068);
            let angle = rng.uniform(0., TAU);
            let radius = inner_radius(z) - 0.0002;
            let size = rng.uniform(0.00008, 0.00019);
            let name = format!("Tiny wall nucleation bead {i}");
            instance(
                &mut scene,
                &name,
                "Carbonation template",
                add(GLASS, [radius * angle.cos(), radius * angle.sin(), z]),
                [size; 3],
            );
            wall.push((name, z));
        }
        let mut impact = Vec::new();
        for i in 0..28 {
            let name = format!("Small impact air inclusion {i}");
            instance(
                &mut scene,
                &name,
                "Carbonation template",
                GLASS,
                [0.0002; 3],
            );
            impact.push(Impact {
                name,
                angle: rng.uniform(0., TAU),
                distance: rng.uniform(0.0013, 0.0055),
                size: rng.uniform(0.0001, 0.00028),
                phase: rng.uniform(0., 1.),
            });
        }
        let mut drops = Vec::new();
        for i in 0..7 {
            let name = format!("Tiny moving impact droplet {i}");
            instance(
                &mut scene,
                &name,
                "Condensation template",
                GLASS,
                [0.0002; 3],
            );
            drops.push(Impact {
                name,
                angle: rng.uniform(0., TAU),
                distance: 0.,
                phase: rng.uniform(0., 1.),
                size: rng.uniform(0.00018, 0.00038),
            });
        }
        for (name, finish) in [
            ("Curving clear water stream", "water"),
            ("Separate fine citrus stream", "flavor"),
        ] {
            let mut faces = Vec::new();
            for ring in 0..STREAM_RINGS - 1 {
                for side in 0..STREAM_SIDES {
                    faces.push(vec![
                        ring * STREAM_SIDES + side,
                        ring * STREAM_SIDES + (side + 1) % STREAM_SIDES,
                        (ring + 1) * STREAM_SIDES + (side + 1) % STREAM_SIDES,
                        (ring + 1) * STREAM_SIDES + side,
                    ]);
                }
            }
            faces.push((0..STREAM_SIDES).rev().collect());
            faces.push(
                (0..STREAM_SIDES)
                    .map(|i| (STREAM_RINGS - 1) * STREAM_SIDES + i)
                    .collect(),
            );
            let mesh = scene.mesh(
                vec![[0.; 3]; STREAM_RINGS * STREAM_SIDES],
                faces,
                None,
                None,
                true,
            );
            scene.object(name, mesh, Some(finish), [0.; 3]);
        }
        let receivers: Vec<_> = scene
            .objects
            .iter()
            .filter(|o| {
                !faucet.contains(&o.name)
                    && matches!(o.geometry, Geometry::Mesh(_) | Geometry::Instance { .. })
            })
            .map(|o| o.name.clone())
            .collect();
        let i = scene.material("studio-floor", "#EAF6FF", 0.50);
        let floor = &mut scene.materials[i];
        floor.emission = 0.12;
        floor.node("coordinates", "ShaderNodeTexCoord", &[], &[]);
        floor.node("separate", "ShaderNodeSeparateXYZ", &[], &[]);
        floor.node(
            "ramp",
            "ShaderNodeValToRGB",
            &[],
            &[("color_ramp.interpolation", json!("EASE"))],
        );
        floor.nodes.last_mut().unwrap().ramp = Some(
            [(0.46, "#EAF6FF"), (0.65, "#A7D5FB"), (0.98, "#1D51D3")]
                .map(|(p, c)| {
                    let c = linear(c);
                    (p, [c[0], c[1], c[2], 1.])
                })
                .to_vec(),
        );
        floor.link("coordinates", "Window", "separate", "Vector");
        floor.link("separate", "X", "ramp", "Fac");
        floor.link("ramp", "Color", "Principled BSDF", "Base Color");
        floor.link("ramp", "Color", "Principled BSDF", "Emission Color");
        let mut section = vec![[-4., 0.], [0.32, 0.]];
        for i in 1..=40 {
            let a = PI * 0.5 * i as f64 / 40.;
            section.push([0.32 + 0.38 * a.sin(), 0.38 * (1. - a.cos())]);
        }
        section.push([0.70, 3.]);
        let vertices2 = [-4., 4.]
            .into_iter()
            .flat_map(|x| section.iter().map(move |p| [x, p[0], p[1]]))
            .collect();
        let n = section.len();
        let mesh = scene.mesh(
            vertices2,
            (0..n - 1)
                .map(|i| vec![i, n + i, n + i + 1, i + 1])
                .collect(),
            None,
            None,
            true,
        );
        scene.object("Seamless pale studio", mesh, Some("studio-floor"), [0.; 3]);
        for (name, at, target, energy, w, h, color, linked) in [
            (
                "Broad neutral key",
                [-0.30, -0.32, 0.56],
                [0.13, -0.04, 0.11],
                5.,
                0.42,
                0.58,
                "#F7FBFF",
                false,
            ),
            (
                "Long product edge",
                [0.40, 0.21, 0.39],
                [0.145, 0.02, 0.13],
                1.2,
                0.10,
                0.40,
                "#E5F0FF",
                false,
            ),
            (
                "Glass broad backlight",
                [0.12, 0.15, 0.29],
                [0.145, -0.15, 0.052],
                5.,
                0.22,
                0.30,
                "#FFFFFF",
                true,
            ),
            (
                "Glass bright side",
                [0.36, -0.10, 0.22],
                [0.145, -0.151, 0.045],
                1.6,
                0.035,
                0.20,
                "#FFFFFF",
                true,
            ),
            (
                "Cold bead highlight",
                [-0.04, -0.29, 0.19],
                [0.145, -0.17, 0.05],
                1.8,
                0.035,
                0.19,
                "#FFFFFF",
                true,
            ),
            (
                "Quiet front fill",
                [0.35, -0.53, 0.28],
                [0.145, -0.04, 0.13],
                0.15,
                0.32,
                0.36,
                "#F5FAFF",
                false,
            ),
            (
                "Background gradient",
                [-0.55, -0.12, 0.85],
                [0.12, 0.60, 0.48],
                5.,
                0.85,
                0.85,
                "#E8F2FF",
                false,
            ),
        ] {
            let i = scene.light(name, at, target, energy, w, color);
            if let Geometry::Area { size_y, .. } = &mut scene.objects[i].geometry {
                *size_y = Some(h);
            }
            if linked {
                scene.objects[i].receivers = receivers.clone();
            }
        }
        Ok(Self {
            scene,
            faucet,
            liquid,
            vertices,
            surface_start,
            outer_ring,
            side_top,
            surface,
            bubbles,
            wall,
            impact,
            drops,
        })
    }
    pub fn frame(
        &mut self,
        shot: &Shot,
        number: usize,
        time: f64,
        width: u32,
        file: &Path,
    ) -> Result<()> {
        let duration = shot.end - shot.start;
        let offset = shot.motion_offset.unwrap_or(0.);
        let t = time + offset;
        let motion = shot.motion_duration.unwrap_or(duration);
        let p = ease(t / motion.max(0.001));
        let flowing = shot.id == "pour";
        let full = 0.0715;
        let volume = PI * (0.0018_f64.powi(2) * 0.90 + 0.00044_f64.powi(2) * 0.75);
        let area = PI * inner_radius(full).powi(2);
        let level = if flowing {
            full - volume * (duration + offset - t).max(0.) / area
        } else {
            full
        };
        let (hit, _) = trajectory(water_outlet(), 0.90, level, 1.);
        let local = sub(hit, GLASS);
        let radius = inner_radius(level) + 0.00006;
        let mut vertices = self.vertices.clone();
        for (index, &(fraction, c, s)) in self.surface.iter().enumerate() {
            let x = fraction * radius * c;
            let y = fraction * radius * s;
            let edge = (radius - x.hypot(y)).max(0.);
            let mut z = level + 0.00055 * (-edge / 0.0015).exp();
            if flowing {
                let dx = x - local[0];
                let dy = y - local[1];
                let distance = (dx * 1.06).hypot(dy * 0.94);
                let angle = dy.atan2(dx);
                let wave = distance + 0.00075 * (angle * 3. + t * 4.1).sin();
                let depression = -0.00060 * (-(distance / 0.0028).powi(2)).exp();
                let rings = 0.00028 * (-distance * 80.).exp() * (wave * 670. - t * 13.).cos();
                let crossing = 0.00010 * (x * 320. + y * 450. + t * 8.).sin();
                z += (edge / 0.003).min(1.) * (depression + rings + crossing);
            } else {
                z += 0.000022 * (x * 170. + y * 120. + t * 1.6).sin();
            }
            vertices[self.surface_start + index] = [x, y, z];
        }
        for i in 0..SIDES {
            vertices[self.side_top + i] = vertices[self.outer_ring + i];
        }
        let mut updates = vec![Update {
            name: self.liquid.clone(),
            vertices: Some(self.scene.floats(vertices.into_iter().flatten())),
            ..Default::default()
        }];
        for name in &self.faucet {
            updates.push(Update {
                name: name.clone(),
                hidden: Some(shot.id == "drink"),
                ..Default::default()
            });
        }
        updates.push(Update {
            name: "lever".into(),
            rotation: Some([if flowing { 0.23 } else { 0. }, 0., 0.]),
            ..Default::default()
        });
        for bubble in &self.bubbles {
            let z = 0.007
                + (bubble.phase * (level - 0.008) + t * bubble.speed).rem_euclid(level - 0.008);
            let size = bubble.size * (0.65 + 0.45 * z / level);
            updates.push(Update {
                name: bubble.name.clone(),
                location: Some(add(
                    GLASS,
                    [
                        bubble.x + 0.00025 * (t * 2. + bubble.phase * TAU).sin(),
                        bubble.y,
                        z,
                    ],
                )),
                scale: Some([size, size, size * 1.06]),
                ..Default::default()
            });
        }
        for (name, z) in &self.wall {
            updates.push(Update {
                name: name.clone(),
                hidden: Some(*z > level - 0.001),
                ..Default::default()
            });
        }
        for b in &self.impact {
            updates.push(Update {
                name: b.name.clone(),
                hidden: Some(!flowing),
                location: Some(add(
                    hit,
                    [
                        (b.angle + t * 0.6).cos() * b.distance,
                        (b.angle + t * 0.6).sin() * b.distance,
                        -0.00025 - 0.0025 * (b.phase + t * 0.8).rem_euclid(1.),
                    ],
                )),
                scale: Some([b.size; 3]),
                ..Default::default()
            });
        }
        for b in &self.drops {
            let age = ((t + b.phase) * 1.8).rem_euclid(0.075);
            let r = 0.0015 + age * 0.035;
            updates.push(Update {
                name: b.name.clone(),
                hidden: Some(!flowing),
                location: Some(add(
                    hit,
                    [
                        (b.angle + t * 0.7).cos() * r,
                        (b.angle + t * 0.7).sin() * r,
                        0.34 * age - 0.5 * 9.81 * age * age,
                    ],
                )),
                scale: Some([b.size, b.size, b.size * 1.25]),
                ..Default::default()
            });
        }
        for (name, outlet, speed, radius, phase) in [
            (
                "Curving clear water stream",
                water_outlet(),
                0.90,
                0.0018,
                0.,
            ),
            (
                "Separate fine citrus stream",
                add(water_outlet(), [-0.003175, -0.004641, 0.003897]),
                0.75,
                0.00044,
                1.3,
            ),
        ] {
            let mut vertices = Vec::new();
            if flowing {
                for ring in 0..STREAM_RINGS {
                    let f = ring as f64 / (STREAM_RINGS - 1) as f64;
                    let (mut point, velocity) = trajectory(outlet, speed, level, f);
                    point[0] += 0.00065 * (t * 28. - f * 22. + phase).sin() * f.powf(1.4);
                    point[1] += 0.00045 * (t * 21. - f * 29. + phase).sin() * f;
                    point[2] -= 0.00035 * f.powi(12);
                    let tangent = unit(velocity);
                    let side_y = unit(cross(tangent, [1., 0., 0.]));
                    let taper = (speed / length(velocity)).sqrt();
                    let travelling = 0.17 * (t * 31. - f * 32. + phase).sin()
                        + 0.075 * (t * 54. - f * 75.).sin();
                    let radius = radius * taper * (1. + travelling * f.powf(0.7));
                    for side in 0..STREAM_SIDES {
                        let angle = TAU * side as f64 / STREAM_SIDES as f64;
                        let organic = 1. + 0.035 * (angle * 3. + t * 18. - f * 15.).sin();
                        vertices.push(add(
                            point,
                            mul(
                                add([angle.cos(), 0., 0.], mul(side_y, angle.sin())),
                                radius * organic,
                            ),
                        ));
                    }
                }
            }
            let span = if flowing {
                Some(self.scene.floats(vertices.into_iter().flatten()))
            } else {
                None
            };
            updates.push(Update {
                name: name.into(),
                hidden: Some(!flowing),
                vertices: span,
                ..Default::default()
            });
        }
        let (at, target, lens, focus, aperture) = match shot.id.as_str() {
            "drink" => (
                blend([0.225, -0.385, 0.145], [0.221, -0.377, 0.142], p),
                [0.145, -0.151, 0.060],
                85.,
                [0.155, -0.181, 0.060],
                32.,
            ),
            "pour" => (
                blend([0.520, -0.480, 0.340], [0.514, -0.474, 0.337], p),
                [0.143, -0.118, 0.115],
                62.,
                [0.144, -0.139, 0.119],
                13.,
            ),
            "serve" => (
                blend([0.435, -0.790, 0.263], [0.432, -0.784, 0.261], p),
                [-0.025, -0.035, 0.084],
                52.,
                [0.145, -0.085, 0.112],
                12.,
            ),
            _ => (
                blend([0.470, -0.820, 0.270], [0.461, -0.805, 0.267], p),
                [-0.018, -0.045, 0.092],
                53.,
                [0.145, -0.085, 0.119],
                9.,
            ),
        };
        self.scene.frames.push(Frame {
            number,
            file: file.to_string_lossy().into(),
            width,
            height: (width as f64 * 9. / 16.).round() as u32,
            camera: Camera {
                position: at,
                target,
                ortho: None,
                lens,
                focus: Some(focus),
                aperture,
            },
            updates,
            node_inputs: vec![(
                "water".into(),
                "flow-noise".into(),
                "W".into(),
                json!(t * 1.7),
            )],
        });
        Ok(())
    }
}
