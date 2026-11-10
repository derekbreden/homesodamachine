//! Full-size cans, cartons and handling contexts supply the film's absolute-time routine shots.
use super::clock::{Shot, routine};
use crate::{draw, scene::*, write};
use anyhow::Result;
use std::{
    collections::BTreeMap,
    f64::consts::{PI, TAU},
    path::Path,
};

struct Group {
    root: String,
    members: Vec<String>,
}
pub struct Routine {
    pub scene: Scene,
    packs: Vec<(Group, Vec<Group>)>,
    contexts: BTreeMap<String, Group>,
    floor: String,
}
const PACK: V3 = [0.145, 0., 0.];
fn grid(i: usize) -> V3 {
    [
        (i % 4) as f64 * 0.0674 - 1.5 * 0.0674,
        (i / 4) as f64 * 0.0674 - 0.0674,
        0.0028,
    ]
}
fn parent(scene: &mut Scene, index: usize, root: &str) {
    scene.objects[index].parent = Some(root.into());
}
fn bx(scene: &mut Scene, name: &str, size: V3, at: V3, finish: &str, root: &str, bevel: f64) {
    let name = format!("{name}/{}", scene.objects.len());
    let i = scene.box_(&name, size, at, finish, bevel);
    parent(scene, i, root);
}
fn pipe(
    scene: &mut Scene,
    name: &str,
    points: &[V3],
    radius: f64,
    finish: &str,
    root: &str,
    closed: bool,
) {
    let name = format!("{name}/{}", scene.objects.len());
    let i = scene.object(
        &name,
        Geometry::Curve {
            points: points.to_vec(),
            radius,
            bezier: false,
            closed,
        },
        Some(finish),
        [0.; 3],
    );
    parent(scene, i, root);
}
fn torus(scene: &mut Scene, name: &str, r: f64, t: f64, at: V3, finish: &str, root: &str) {
    let sides = 10;
    let n = 96;
    let mut vertices = Vec::new();
    let mut faces = Vec::new();
    for i in 0..n {
        let a = TAU * i as f64 / n as f64;
        for j in 0..sides {
            let b = TAU * j as f64 / sides as f64;
            let radial = r + t * b.cos();
            vertices.push([radial * a.cos(), radial * a.sin(), t * b.sin()]);
        }
    }
    for i in 0..n {
        for j in 0..sides {
            faces.push(vec![
                i * sides + j,
                ((i + 1) % n) * sides + j,
                ((i + 1) % n) * sides + (j + 1) % sides,
                i * sides + (j + 1) % sides,
            ]);
        }
    }
    let mesh = scene.mesh(vertices, faces, None, None, true);
    let i = scene.object(name, mesh, Some(finish), at);
    parent(scene, i, root);
}
fn group(scene: &Scene, start: usize) -> Group {
    Group {
        root: scene.objects[start].name.clone(),
        members: scene.objects[start..]
            .iter()
            .map(|o| o.name.clone())
            .collect(),
    }
}
fn clone_group(scene: &mut Scene, source: &Group, name: &str, parent_name: &str) -> Group {
    let mut aliases = BTreeMap::new();
    let start = scene.objects.len();
    for (i, original) in source.members.iter().enumerate() {
        let object = scene
            .objects
            .iter()
            .find(|o| o.name == *original)
            .unwrap()
            .clone();
        let name = if i == 0 {
            name.to_string()
        } else {
            format!("{name}/{i}")
        };
        let source = object.name.clone();
        let parent = if i == 0 {
            Some(parent_name.into())
        } else {
            object.parent.and_then(|p| aliases.get(&p).cloned())
        };
        let index = scene.object(&name, Geometry::Instance { source }, None, object.location);
        scene.objects[index].rotation = object.rotation;
        scene.objects[index].scale = object.scale;
        scene.objects[index].parent = parent;
        scene.objects[index].bevel = object.bevel;
        scene.objects[index].bevel_segments = object.bevel_segments;
        scene.objects[index].normals = object.normals;
        aliases.insert(original.clone(), name);
    }
    group(scene, start)
}
fn label(out: &Path) -> Result<String> {
    let mut pixels = tiny_skia::Pixmap::new(2048, 2048).unwrap();
    pixels.fill(draw::rgba("#F3F0E8"));
    let t = tiny_skia::Transform::identity();
    for u in [0.25, 0.75] {
        let circle = tiny_skia::PathBuilder::from_circle(0., 0., 1.).unwrap();
        draw::path(
            &mut pixels,
            &circle,
            draw::rgba("#F58F45"),
            t.pre_translate((u * 2048.) as f32, ((1. - 0.465) * 2048.) as f32)
                .pre_scale((0.15 * 2048.) as f32, (0.145 * 2048.) as f32),
        );
    }
    for offset in [0., 0.5] {
        for (u, v, r) in [
            (0.19, 0.72, 0.022),
            (0.31, 0.775, 0.033),
            (0.365, 0.69, 0.014),
        ] {
            draw::circle(
                &mut pixels,
                [(u + offset) * 2048., (1. - v) * 2048.],
                r * 2048.,
                draw::rgba("#DCE6F5"),
                None,
                t,
            );
        }
    }
    let file = out.join("can-label.png");
    write(&file, pixels.encode_png()?)?;
    Ok(file.to_string_lossy().into())
}
impl Routine {
    pub fn new(out: &Path, samples: usize) -> Result<Self> {
        let mut scene = Scene::new();
        scene.settings.samples = samples;
        scene.settings.max_bounces = 7;
        scene.settings.transmission_bounces = 5;
        scene.settings.world = linear("#E7EEF6");
        scene.settings.world_strength = 0.26;
        for (name, hex, rough, metal, grain, distance) in [
            ("aluminum", "#D4DCE3", 0.27, 1., 0., 0.),
            ("brushed", "#BAC5D0", 0.38, 1., 0., 0.),
            ("score", "#84909B", 0.42, 0.82, 0., 0.),
            ("paint", "#F3F0E8", 0.46, 0.12, 420., 0.000003),
            ("carton", "#D9CEC0", 0.83, 0., 1450., 0.00007),
            ("fold", "#BFB19F", 0.87, 0., 0., 0.),
            ("silver", "#C2CCD7", 0.32, 0.86, 0., 0.),
            ("orange", "#FF9152", 0.58, 0., 0., 0.),
            ("rubber", "#17222D", 0.87, 0., 480., 0.00006),
            ("felt", "#3B4656", 0.96, 0., 1100., 0.00028),
            ("car-paint", "#B6C4D3", 0.25, 0.55, 0., 0.),
            ("tail", "#B54138", 0.25, 0.22, 0., 0.),
            ("white", "#E7E6DF", 0.57, 0., 0., 0.),
            ("counter", "#F1F0E9", 0.45, 0., 380., 0.000025),
            ("fridge", "#DDE8EF", 0.47, 0., 0., 0.),
            ("shelf", "#D8EDF6", 0.08, 0., 0., 0.),
            ("light-strip", "#ECF6FF", 0.4, 0., 0., 0.),
            ("floor", "#1749D1", 0.65, 0., 0., 0.),
            ("card", "#F4F7FB", 0.8, 0., 0., 0.),
        ] {
            let i = scene.material(name, hex, rough);
            scene.materials[i].metal = metal;
            if grain > 0. {
                scene.materials[i].grain(grain, 0.16, distance);
            }
            if name == "paint" {
                scene.materials[i].texture = Some(label(out)?);
            }
            if name == "brushed" {
                scene.materials[i].anisotropy = Some(0.45);
            }
            if name == "shelf" {
                scene.materials[i].transmission = 1.;
                scene.materials[i].ior = 1.46;
            }
            if name == "light-strip" {
                scene.materials[i].emission = 1.2;
            }
            if name == "floor" {
                scene.materials[i].emission = 0.16;
            }
            if name == "card" {
                scene.materials[i].emission = 0.8;
            }
        }
        let start = scene.objects.len();
        scene.object("Can template", Geometry::Empty, None, [0.; 3]);
        let s = 0.122 / 2.6;
        let profile: [[f64; 2]; 10] = [
            [0.53, 0.],
            [0.59, 0.02],
            [0.62, 0.08],
            [0.65, 0.17],
            [0.70, 0.30],
            [0.705, 2.22],
            [0.69, 2.36],
            [0.65, 2.46],
            [0.60, 2.55],
            [0.59, 2.60],
        ];
        let mut vertices = Vec::new();
        let mut normals = Vec::new();
        let mut uv = Vec::new();
        let mut faces = Vec::new();
        for (j, [r, z]) in profile.into_iter().enumerate() {
            let lo = profile[j.saturating_sub(1)];
            let hi = profile[(j + 1).min(profile.len() - 1)];
            let dr = hi[0] - lo[0];
            let dz = hi[1] - lo[1];
            let n = dr.hypot(dz);
            for i in 0..=96 {
                let a = TAU * i as f64 / 96.;
                vertices.push([r * s * a.cos(), r * s * a.sin(), z * s]);
                normals.push([dz * a.cos() / n, dz * a.sin() / n, -dr / n]);
                uv.push([i as f64 / 96., z / 2.6]);
            }
        }
        for j in 0..9 {
            for i in 0..96 {
                faces.push(vec![
                    j * 97 + i,
                    j * 97 + i + 1,
                    (j + 1) * 97 + i + 1,
                    (j + 1) * 97 + i,
                ]);
            }
        }
        let mesh = scene.mesh(vertices, faces, Some(normals), Some(uv), true);
        let i = scene.object("Shouldered printed can body", mesh, Some("paint"), [0.; 3]);
        parent(&mut scene, i, "Can template");
        torus(
            &mut scene,
            "Rolled top seam",
            0.589 * s,
            0.034 * s,
            [0., 0., 2.61 * s],
            "aluminum",
            "Can template",
        );
        torus(
            &mut scene,
            "Bottom standing seam",
            0.578 * s,
            0.030 * s,
            [0., 0., 0.05 * s],
            "aluminum",
            "Can template",
        );
        let i = scene.cylinder(
            "Recessed brushed lid",
            0.572 * s,
            0.034 * s,
            [0., 0., 2.604 * s],
            "brushed",
        );
        parent(&mut scene, i, "Can template");
        torus(
            &mut scene,
            "Pressed lid groove",
            0.477 * s,
            0.009 * s,
            [0., 0., 2.626 * s],
            "score",
            "Can template",
        );
        let opening: Vec<_> = (0..64)
            .map(|i| {
                let a = TAU * i as f64 / 64.;
                [a.cos() * 0.0075, -0.011 + a.sin() * 0.0083, 0.12305]
            })
            .collect();
        pipe(
            &mut scene,
            "Scored drinking opening",
            &opening,
            0.00017,
            "score",
            "Can template",
            true,
        );
        let n = 64;
        let mut vertices = Vec::new();
        let mut faces = Vec::new();
        for z in [0., 0.00065] {
            for (rx, ry, cy) in [(0.0058, 0.0103, 0.), (0.0031, 0.0046, 0.0022)] {
                for i in 0..n {
                    let a = TAU * i as f64 / n as f64;
                    vertices.push([rx * a.cos(), cy + ry * a.sin(), z]);
                }
            }
        }
        for i in 0..n {
            let j = (i + 1) % n;
            faces.extend([
                vec![i, j, n + j, n + i],
                vec![2 * n + i, 3 * n + i, 3 * n + j, 2 * n + j],
                vec![i, 2 * n + i, 2 * n + j, j],
                vec![n + i, n + j, 3 * n + j, 3 * n + i],
            ]);
        }
        let mesh = scene.mesh(vertices, faces, None, None, true);
        let i = scene.object(
            "Stamped aluminum pull tab",
            mesh,
            Some("aluminum"),
            [0., -0.001, 0.1232],
        );
        scene.objects[i].rotation[2] = -0.12;
        scene.objects[i].bevel = 0.00015;
        scene.objects[i].bevel_segments = 2;
        parent(&mut scene, i, "Can template");
        let i = scene.cylinder(
            "Pull tab rivet",
            0.00155,
            0.00065,
            [0., 0.0064, 0.12405],
            "aluminum",
        );
        parent(&mut scene, i, "Can template");
        let template = group(&scene, start);
        for object in &mut scene.objects[start..] {
            object.hidden = true;
        }
        let mut packs = Vec::new();
        for index in 0..5 {
            let start = scene.objects.len();
            let name = format!("Carton {index}");
            scene.object(&name, Geometry::Empty, None, PACK);
            let mut cans = Vec::new();
            for number in 0..12 {
                let can = clone_group(
                    &mut scene,
                    &template,
                    &format!("Carton {index} can {number}"),
                    &name,
                );
                let i = scene
                    .objects
                    .iter()
                    .position(|o| o.name == can.root)
                    .unwrap();
                scene.objects[i].location = grid(number);
                scene.objects[i].rotation[2] =
                    0.11 * ((number % 4) % 2) as f64 - 0.08 * (number / 4) as f64;
                cans.push(can);
            }
            for (label, size, at, bevel) in [
                (
                    "Carton base",
                    [0.277, 0.211, 0.0028],
                    [0., 0., 0.0014],
                    0.0006,
                ),
                (
                    "Carton front fold",
                    [0.277, 0.0015, 0.023],
                    [0., -0.211 / 2., 0.023 / 2.],
                    0.0004,
                ),
                (
                    "Carton back fold",
                    [0.277, 0.0015, 0.023],
                    [0., 0.211 / 2., 0.023 / 2.],
                    0.0004,
                ),
                (
                    "Carton left fold",
                    [0.0015, 0.211, 0.023],
                    [-0.277 / 2., 0., 0.023 / 2.],
                    0.0004,
                ),
                (
                    "Carton right fold",
                    [0.0015, 0.211, 0.023],
                    [0.277 / 2., 0., 0.023 / 2.],
                    0.0004,
                ),
            ] {
                bx(&mut scene, label, size, at, "carton", &name, bevel);
            }
            for x in [-0.277 * 0.5 + 0.011, 0.277 * 0.5 - 0.011] {
                pipe(
                    &mut scene,
                    "Carton corner crease",
                    &[
                        [x, -0.211 * 0.5 - 0.0008, 0.001],
                        [x, -0.211 * 0.5 - 0.0008, 0.022],
                    ],
                    0.00022,
                    "fold",
                    &name,
                    false,
                );
            }
            pipe(
                &mut scene,
                "Fine front carton fold",
                &[
                    [-0.277 / 2., -0.211 * 0.5 - 0.0009, 0.005],
                    [0.277 / 2., -0.211 * 0.5 - 0.0009, 0.005],
                ],
                0.0002,
                "fold",
                &name,
                false,
            );
            packs.push((group(&scene, start), cans));
        }
        let mut contexts = BTreeMap::new();
        for name in ["case", "car", "kitchen", "shelf"] {
            let start = scene.objects.len();
            let context = format!("{name} context");
            scene.object(&context, Geometry::Empty, None, PACK);
            match name {
                "case" => {
                    for i in 0..11 {
                        let x = -0.15 + 0.30 * i as f64 / 10.;
                        pipe(
                            &mut scene,
                            "Basket continuous steel wire",
                            &[
                                [x, -0.142, 0.147],
                                [x * 0.87, -0.113, -0.003],
                                [x * 0.87, 0.113, -0.003],
                                [x, 0.142, 0.147],
                            ],
                            0.00125,
                            "silver",
                            &context,
                            false,
                        );
                    }
                    for i in 0..7 {
                        let y = -0.11 + 0.22 * i as f64 / 6.;
                        pipe(
                            &mut scene,
                            "Basket cross wire",
                            &[
                                [-0.171, y * 1.24, 0.147],
                                [-0.139, y, -0.003],
                                [0.139, y, -0.003],
                                [0.171, y * 1.24, 0.147],
                            ],
                            0.00125,
                            "silver",
                            &context,
                            false,
                        );
                    }
                    for z in [0.028, 0.084, 0.147] {
                        let u = (z + 0.003) / 0.15;
                        let x = 0.139 + u * 0.032;
                        let y = 0.113 + u * 0.029;
                        pipe(
                            &mut scene,
                            "Basket horizontal rail",
                            &[[-x, -y, z], [x, -y, z], [x, y, z], [-x, y, z]],
                            0.0017,
                            "silver",
                            &context,
                            true,
                        );
                    }
                    for x in [-0.165, 0.165] {
                        pipe(
                            &mut scene,
                            "Cart handle upright",
                            &[[x, 0.142, 0.147], [x, 0.202, 0.238]],
                            0.0031,
                            "silver",
                            &context,
                            false,
                        );
                    }
                    pipe(
                        &mut scene,
                        "Orange shopping cart handle",
                        &[[-0.166, 0.202, 0.238], [0.166, 0.202, 0.238]],
                        0.009,
                        "orange",
                        &context,
                        false,
                    );
                    for x in [-0.130, 0.130] {
                        pipe(
                            &mut scene,
                            "Cart front structural support",
                            &[
                                [x, -0.106, -0.004],
                                [x, -0.090, -0.085],
                                [x * 1.24, 0.012, -0.48],
                            ],
                            0.0052,
                            "silver",
                            &context,
                            false,
                        );
                        pipe(
                            &mut scene,
                            "Cart rear structural support",
                            &[
                                [x, 0.106, -0.004],
                                [x, 0.130, -0.095],
                                [x * 1.24, 0.205, -0.48],
                            ],
                            0.0052,
                            "silver",
                            &context,
                            false,
                        );
                        pipe(
                            &mut scene,
                            "Cart basket lower frame",
                            &[[x, -0.107, -0.009], [x, 0.110, -0.009]],
                            0.0044,
                            "silver",
                            &context,
                            false,
                        );
                    }
                }
                "car" => {
                    for (label, size, at, finish, bevel) in [
                        (
                            "Cropped carpeted cargo floor",
                            [0.56, 0.40, 0.018],
                            [0., 0.015, -0.011],
                            "felt",
                            0.004,
                        ),
                        (
                            "Cargo bay rear lining",
                            [0.56, 0.018, 0.17],
                            [0., 0.205, 0.067],
                            "felt",
                            0.008,
                        ),
                        (
                            "Trunk sill",
                            [0.61, 0.048, 0.045],
                            [0., -0.201, -0.023],
                            "car-paint",
                            0.006,
                        ),
                        (
                            "Trunk threshold rubber",
                            [0.53, 0.042, 0.009],
                            [0., -0.197, 0.003],
                            "rubber",
                            0.003,
                        ),
                        (
                            "Cropped rear body panel",
                            [0.65, 0.018, 0.11],
                            [0., -0.226, -0.075],
                            "car-paint",
                            0.005,
                        ),
                        (
                            "Partial right rear lamp",
                            [0.039, 0.021, 0.095],
                            [0.277, -0.237, -0.065],
                            "tail",
                            0.006,
                        ),
                        (
                            "Partial left rear lamp",
                            [0.030, 0.021, 0.073],
                            [-0.277, -0.237, -0.042],
                            "tail",
                            0.005,
                        ),
                    ] {
                        bx(&mut scene, label, size, at, finish, &context, bevel);
                    }
                    for x in [-0.283, 0.283] {
                        bx(
                            &mut scene,
                            "Cropped cargo side lining",
                            [0.025, 0.27, 0.15],
                            [x, 0.070, 0.060],
                            "felt",
                            &context,
                            0.009,
                        );
                        pipe(
                            &mut scene,
                            "Trunk rubber side gasket",
                            &[[x, -0.10, -0.01], [x, 0.21, 0.02], [x, 0.215, 0.14]],
                            0.006,
                            "rubber",
                            &context,
                            false,
                        );
                    }
                    for i in 0..13 {
                        let x = -0.23 + 0.46 * i as f64 / 12.;
                        bx(
                            &mut scene,
                            "Threshold grip rib",
                            [0.0022, 0.034, 0.002],
                            [x, -0.198, 0.008],
                            "score",
                            &context,
                            0.0005,
                        );
                    }
                }
                "kitchen" => {
                    for (label, size, at, finish, bevel) in [
                        (
                            "Full-size counter crop",
                            [1.35, 0.57, 0.034],
                            [-0.13, 0.08, -0.020],
                            "counter",
                            0.003,
                        ),
                        (
                            "Cabinet front crop",
                            [1.27, 0.018, 0.45],
                            [-0.13, -0.189, -0.265],
                            "white",
                            0.001,
                        ),
                        (
                            "Quiet cabinet seam",
                            [0.0012, 0.001, 0.37],
                            [-0.13, -0.199, -0.25],
                            "score",
                            0.,
                        ),
                    ] {
                        bx(&mut scene, label, size, at, finish, &context, bevel);
                    }
                    for x in [-0.35, 0.09] {
                        for dx in [-0.045, 0.045] {
                            pipe(
                                &mut scene,
                                "Cabinet handle standoff",
                                &[[x + dx, -0.201, -0.10], [x + dx, -0.217, -0.10]],
                                0.0021,
                                "silver",
                                &context,
                                false,
                            );
                        }
                        pipe(
                            &mut scene,
                            "Counter cabinet handle",
                            &[[x - 0.058, -0.217, -0.10], [x + 0.058, -0.217, -0.10]],
                            0.0032,
                            "silver",
                            &context,
                            false,
                        );
                    }
                }
                _ => {
                    for (label, size, at, finish, bevel) in [
                        (
                            "Refrigerator glass shelf",
                            [0.50, 0.325, 0.004],
                            [0., 0.027, -0.004],
                            "shelf",
                            0.0006,
                        ),
                        (
                            "Refrigerator shelf front trim",
                            [0.505, 0.014, 0.012],
                            [0., -0.135, -0.003],
                            "aluminum",
                            0.002,
                        ),
                        (
                            "Refrigerator rear interior crop",
                            [0.535, 0.018, 0.51],
                            [0., 0.202, 0.205],
                            "fridge",
                            0.012,
                        ),
                        (
                            "Lower refrigerator shelf lip",
                            [0.50, 0.015, 0.012],
                            [0., -0.135, -0.151],
                            "aluminum",
                            0.002,
                        ),
                        (
                            "Lower refrigerator shelf crop",
                            [0.50, 0.32, 0.003],
                            [0., 0.028, -0.155],
                            "shelf",
                            0.0004,
                        ),
                    ] {
                        bx(&mut scene, label, size, at, finish, &context, bevel);
                    }
                    for x in [-0.259, 0.259] {
                        bx(
                            &mut scene,
                            "Cropped refrigerator side return",
                            [0.017, 0.145, 0.51],
                            [x, 0.126, 0.205],
                            "fridge",
                            &context,
                            0.008,
                        );
                        bx(
                            &mut scene,
                            "Vertical refrigerator light",
                            [0.006, 0.003, 0.29],
                            [x * 0.95, 0.187, 0.20],
                            "light-strip",
                            &context,
                            0.001,
                        );
                    }
                }
            }
            contexts.insert(name.into(), group(&scene, start));
        }
        let mut section = vec![[-3., -0.065], [0.36, -0.065]];
        for i in 1..=32 {
            let a = PI * 0.5 * i as f64 / 32.;
            section.push([0.36 + 0.38 * a.sin(), -0.065 + 0.38 * (1. - a.cos())]);
        }
        section.push([0.74, 3.]);
        let vertices = [-4., 4.]
            .into_iter()
            .flat_map(|x| section.iter().map(move |p| [x, p[0], p[1]]))
            .collect();
        let n = section.len();
        let mesh = scene.mesh(
            vertices,
            (0..n - 1)
                .map(|i| vec![i, n + i, n + i + 1, i + 1])
                .collect(),
            None,
            None,
            true,
        );
        scene.object(
            "Seamless cobalt handling stage",
            mesh,
            Some("floor"),
            [0.; 3],
        );
        for (name, at, target, energy, w, h, color) in [
            (
                "Long soft can key",
                [-0.22, -0.38, 0.55],
                [0.145, 0., 0.07],
                8.,
                0.26,
                0.55,
                "#FAFCFF",
            ),
            (
                "Controlled aluminum edge",
                [0.47, 0.14, 0.36],
                [0.145, 0., 0.09],
                3.5,
                0.10,
                0.42,
                "#E7F1FF",
            ),
            (
                "Gentle front label fill",
                [0.36, -0.55, 0.22],
                [0.145, 0., 0.07],
                0.9,
                0.31,
                0.25,
                "#FFFFFF",
            ),
            (
                "Broad top carton light",
                [0.10, 0.03, 0.71],
                [0.145, 0., 0.],
                2.5,
                0.50,
                0.34,
                "#F8FAFF",
            ),
        ] {
            let i = scene.light(name, at, target, energy, w, color);
            if let Geometry::Area { size_y, .. } = &mut scene.objects[i].geometry {
                *size_y = Some(h);
            }
        }
        let mesh = scene.mesh(
            vec![
                [-0.34, -0.29, 0.],
                [0.34, -0.29, 0.],
                [0.34, 0.29, 0.],
                [-0.34, 0.29, 0.],
            ],
            vec![vec![0, 1, 2, 3]],
            None,
            None,
            false,
        );
        let i = scene.object(
            "Broad neutral lid reflection",
            mesh,
            Some("card"),
            [0.13, -0.42, 0.47],
        );
        scene.objects[i].rotation = track(sub([0.13, -0.42, 0.47], [0.145, 0., 0.09]));
        scene.objects[i].camera = false;
        scene.objects[i].diffuse = false;
        scene.objects[i].shadow = false;
        scene.objects[i].transmission = false;
        Ok(Self {
            scene,
            packs,
            contexts,
            floor: "Seamless cobalt handling stage".into(),
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
        let pose = routine(shot, time)?;
        let mut updates = Vec::new();
        for (name, group) in &self.contexts {
            for member in &group.members {
                updates.push(Update {
                    name: member.clone(),
                    hidden: Some(*name != pose.context),
                    ..Default::default()
                });
            }
            updates.push(Update {
                name: group.root.clone(),
                location: Some(add(PACK, pose.offset)),
                ..Default::default()
            });
        }
        updates.push(Update {
            name: self.floor.clone(),
            location: Some([
                0.,
                0.,
                if shot.id == "case" {
                    -0.35 * (1. - pose.offset[0] / 0.66)
                } else {
                    0.
                },
            ]),
            ..Default::default()
        });
        for (index, (pack, cans)) in self.packs.iter().enumerate() {
            let selected = pose.packs.iter().find(|p| p.index == index);
            for member in &pack.members {
                updates.push(Update {
                    name: member.clone(),
                    hidden: Some(selected.is_none()),
                    ..Default::default()
                });
            }
            updates.push(Update {
                name: pack.root.clone(),
                location: Some(add(PACK, selected.map_or([0.; 3], |p| p.offset))),
                ..Default::default()
            });
            for (i, can) in cans.iter().enumerate() {
                let (hidden, offset) = selected.map_or((true, [0.; 3]), |p| p.cans[i]);
                for member in &can.members {
                    updates.push(Update {
                        name: member.clone(),
                        hidden: Some(hidden || selected.is_none()),
                        ..Default::default()
                    });
                }
                let mut at = add(grid(i), offset);
                if shot.id == "case" && i > 0 {
                    at[0] += 0.75 * (1. - pose.expand);
                }
                updates.push(Update {
                    name: can.root.clone(),
                    location: Some(at),
                    ..Default::default()
                });
            }
        }
        let wide = [0.485, -0.785, 0.415];
        let target = [0.015, 0., 0.042];
        let camera = if shot.id == "case" {
            let p = pose.expand;
            let z = pose.packs[0].offset[2];
            Camera {
                position: blend([-0.005, -0.590, 0.088], add(wide, [0., 0., z]), p),
                target: blend([-0.005, 0., -0.001], add(target, [0., 0., z]), p),
                ortho: None,
                lens: 70. + (45. - 70.) * p,
                focus: Some(blend([0.044, -0.098, 0.], [0.145, 0., 0.068 + z], p)),
                aperture: 12. - p,
            }
        } else {
            Camera {
                position: wide,
                target,
                ortho: None,
                lens: 45.,
                focus: Some([0.145, 0., 0.070]),
                aperture: 11.,
            }
        };
        self.scene.frames.push(Frame {
            number,
            file: file.to_string_lossy().into(),
            width,
            height: (width as f64 * 9. / 16.).round() as u32,
            camera,
            updates,
            node_inputs: Vec::new(),
        });
        Ok(())
    }
}
