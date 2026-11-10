//! The manual homepage factory stages the current faucet, enclosure and regulator in a kitchen.
use crate::scene::*;
use crate::{Args, root, write};
use anyhow::{Context, Result, ensure};
use hsm_display_assets::{self as assets, Rendition};
use serde_json::{Value, json};
use std::{
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
    process::Command,
};

pub fn texture(index: usize, out: &Path) -> Result<String> {
    let data = assets::factory_rendition(&root(), index, Rendition::Anchor)?;
    let (width, height) = Rendition::Anchor.dimensions();
    let image = assets::decode_rgb565(width, height, &data)?;
    let path = out.join(format!("flavor-{index}.png"));
    write(&path, image.png()?)?;
    Ok(path.to_string_lossy().into())
}
pub fn prepare(out: &Path, preview: bool) -> Result<(Scene, BTreeMap<String, V3>)> {
    let mut scene = Scene::new();
    scene.settings.samples = if preview { 32 } else { 160 };
    scene.settings.threshold = if preview { 0.025 } else { 0.012 };
    scene.settings.transparent = true;
    scene.settings.look = "AgX - Very High Contrast".into();
    scene.materials.push(Material::new(
        "petgf",
        [0.0331047662, 0.0331047662, 0.0363064855],
        0.85,
    ));
    for (name, hex, rough, metal, trans, ior) in [
        ("rubber", "#22252A", 0.91, 0., 0., 1.45),
        ("display", "#15212B", 0.14, 0., 0., 1.45),
        ("steel", "#BCC4CD", 0.27, 0.92, 0., 1.45),
        ("aluminum", "#C3CCD7", 0.33, 0.88, 0., 1.45),
        ("brass", "#B5995A", 0.31, 0.77, 0., 1.45),
        ("stone", "#F4F5F7", 0.49, 0., 0., 1.45),
        ("paint", "#E8EDF2", 0.57, 0., 0., 1.45),
        ("oak", "#CFC4B0", 0.63, 0., 0., 1.45),
        ("floor", "#EAF0F6", 0.78, 0., 0., 1.45),
        ("co2-tube", "#66717E", 0.79, 0., 0., 1.45),
        ("glass", "#F7FCFF", 0.035, 0., 1., 1.46),
        ("soda", "#FFFFFF", 0.08, 0., 1., 1.33),
        ("water-stream", "#BDD6E8", 0.12, 0., 0.65, 1.33),
        ("flavor-stream", "#C7A169", 0.1, 0., 0.71, 1.33),
        ("bubble", "#FFFFFF", 0.02, 0., 1., 0.752),
    ] {
        let i = scene.material(name, hex, rough);
        scene.materials[i].metal = metal;
        scene.materials[i].transmission = trans;
        scene.materials[i].ior = ior;
    }
    let mat = |scene: &mut Scene, name: &str| {
        scene.materials.iter().position(|m| m.name == name).unwrap()
    };
    let i = mat(&mut scene, "soda");
    scene.materials[i].clear(linear("#FFF4B4"), 0.10, 0.035, false);
    let i = mat(&mut scene, "stone");
    scene.materials[i].grain(900., 0.11, 0.00009);
    let i = mat(&mut scene, "petgf");
    scene.materials[i].specular = Some(0.26);
    scene.materials[i].grain(2100., 0.10, 0.00005);
    let i = mat(&mut scene, "oak");
    let oak = &mut scene.materials[i];
    oak.node("coordinates", "ShaderNodeTexCoord", &[], &[]);
    oak.node(
        "mapping",
        "ShaderNodeVectorMath",
        &[("1", json!([90, 8, 4]))],
        &[("operation", json!("MULTIPLY"))],
    );
    oak.node(
        "wood",
        "ShaderNodeTexNoise",
        &[("Scale", json!(3)), ("Detail", json!(2))],
        &[],
    );
    oak.node("ramp", "ShaderNodeValToRGB", &[], &[]);
    let a = linear("#CDC0AC");
    let b = linear("#DDD3C2");
    oak.nodes.last_mut().unwrap().ramp = Some(vec![
        (0.2, [a[0], a[1], a[2], 1.]),
        (0.8, [b[0], b[1], b[2], 1.]),
    ]);
    oak.link("coordinates", "Generated", "mapping", "0");
    oak.link("mapping", "Vector", "wood", "Vector");
    oak.link("wood", "Fac", "ramp", "Fac");
    oak.link("ramp", "Color", "Principled BSDF", "Base Color");
    for (name, size, at, finish) in [
        (
            "Cabinet left side",
            [0.023, 0.63, 0.757],
            [-0.423, 0.015, 0.424],
            "oak",
        ),
        (
            "Cabinet pale outer left skin",
            [0.003, 0.63, 0.757],
            [-0.436, 0.015, 0.424],
            "paint",
        ),
        (
            "Cabinet rear panel",
            [0.846, 0.018, 0.757],
            [0., 0.321, 0.424],
            "oak",
        ),
        (
            "Cutaway right rear side",
            [0.023, 0.145, 0.757],
            [0.423, 0.257, 0.424],
            "oak",
        ),
        (
            "Cabinet base",
            [0.869, 0.63, 0.023],
            [0., 0.015, 0.055],
            "oak",
        ),
        (
            "Pale cabinet base edge",
            [0.869, 0.017, 0.025],
            [0., -0.308, 0.055],
            "paint",
        ),
        (
            "Recessed plinth",
            [0.811, 0.558, 0.028],
            [0., 0.039, 0.028],
            "paint",
        ),
    ] {
        scene.box_(name, size, at, finish, 0.002);
    }
    let countertop = 0.83;
    let counter = scene.box_(
        "Pale stone worktop",
        [0.97, 0.72, 0.032],
        [0., 0.015, countertop - 0.016],
        "stone",
        0.006,
    );
    scene.objects[counter].bevel_segments = 6;
    let hole = scene.box_(
        "Sink worktop cut",
        [0.346, 0.292, 0.26],
        [-0.232, 0.11, countertop],
        "stone",
        0.028,
    );
    scene.objects[hole].bevel_segments = 8;
    scene.objects[hole].hidden = true;
    scene.objects[counter]
        .difference
        .push("Sink worktop cut".into());
    let sink = scene.box_(
        "Undermount stainless sink",
        [0.362, 0.309, 0.124],
        [-0.232, 0.11, countertop - 0.066],
        "steel",
        0.029,
    );
    scene.objects[sink].bevel_segments = 8;
    let inner = scene.box_(
        "Sink hollow",
        [0.35, 0.297, 0.17],
        [-0.232, 0.11, countertop - 0.025],
        "steel",
        0.026,
    );
    scene.objects[inner].bevel_segments = 8;
    scene.objects[inner].hidden = true;
    scene.objects[sink].difference.push("Sink hollow".into());
    scene.cylinder(
        "Sink drain",
        0.016,
        0.0015,
        [-0.232, 0.11, countertop - 0.12],
        "aluminum",
    );
    scene.tube(
        "Quiet sink plumbing",
        &[
            [-0.232, 0.11, 0.709],
            [-0.232, 0.11, 0.59],
            [-0.232, 0.18, 0.54],
            [-0.232, 0.235, 0.55],
            [-0.232, 0.27, 0.61],
            [-0.232, 0.322, 0.61],
        ],
        0.014,
        "paint",
    );
    scene.cylinder(
        "Standard tap base",
        0.023,
        0.008,
        [-0.232, 0.296, countertop + 0.004],
        "steel",
    );
    scene.tube(
        "Standard kitchen water tap",
        &[
            [-0.232, 0.296, countertop + 0.008],
            [-0.232, 0.296, countertop + 0.1],
            [-0.232, 0.251, countertop + 0.158],
            [-0.232, 0.164, countertop + 0.153],
            [-0.232, 0.131, countertop + 0.112],
        ],
        0.0074,
        "steel",
    );
    scene.tube(
        "Standard tap control",
        &[
            [-0.222, 0.296, countertop + 0.025],
            [-0.193, 0.296, countertop + 0.027],
            [-0.191, 0.269, countertop + 0.049],
        ],
        0.004,
        "steel",
    );
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
    let faucet_at = [0.214, 0.037, countertop];
    let faucet = scene.load(
        "hardware/faucet-layout/faucet-assembly.step.mesh",
        |n| visible.contains(&n),
        |m| {
            if ["faucet_display", "faucet_display_screen"].contains(&m.name.as_str()) {
                "display".into()
            } else {
                "petgf".into()
            }
        },
        faucet_at,
        0.,
        Some(-6.),
    )?;
    let screen = *faucet
        .iter()
        .find(|&&i| scene.objects[i].name == "faucet_display_screen")
        .context("faucet physical display")?;
    let selected = texture(1, out)?;
    let texture0 = texture(0, out)?;
    let i = scene.material("selected-faucet", "#1749D1", 0.23);
    scene.materials[i].texture = Some(selected.clone());
    scene.materials[i].emission = 0.18;
    scene.objects[screen].material = Some("selected-faucet".into());
    let vertices = scene.mesh_vertices(screen)?;
    let minx = vertices.iter().map(|p| p[0]).fold(f64::INFINITY, f64::min);
    let maxx = vertices
        .iter()
        .map(|p| p[0])
        .fold(f64::NEG_INFINITY, f64::max);
    let minz = vertices.iter().map(|p| p[2]).fold(f64::INFINITY, f64::min);
    let maxz = vertices
        .iter()
        .map(|p| p[2])
        .fold(f64::NEG_INFINITY, f64::max);
    scene.uv(
        screen,
        vertices
            .iter()
            .map(|p| [(p[0] - minx) / (maxx - minx), (p[2] - minz) / (maxz - minz)])
            .collect(),
    );
    let unit_at = [0.144, -0.154, 0.071];
    let source = "hardware/manifold-layout/enclosure-assembly.step.mesh";
    let selected_unit = |n: &str| {
        [
            "enclosure-",
            "nameplate",
            "display",
            "status-plate",
            "funnel",
        ]
        .iter()
        .any(|p| n.starts_with(p))
            || n == "pump-jack"
    };
    let raw = read_payload(source, &selected_unit)?;
    for mesh in &raw {
        let name = &mesh.name;
        if name.starts_with("display/") {
            continue;
        }
        let mut material =
            Material::new(&format!("unit/{name}"), mesh.color.unwrap_or([0.4; 3]), 0.8);
        if name == "status-plate/3" {
            material.base = linear("#4189FF");
            material.roughness = 0.35;
            material.emission = 0.6;
        }
        scene.materials.push(material);
    }
    let unit = scene.load(
        source,
        selected_unit,
        |m| {
            if m.name.starts_with("display/") {
                "display".into()
            } else {
                format!("unit/{}", m.name)
            }
        },
        unit_at,
        0.,
        None,
    )?;
    for (name, color) in [
        ("ui-blue", "#1749D1"),
        ("ui-ice", "#DCE6FF"),
        ("ui-navy", "#10319C"),
        ("ui-white", "#FFFFFF"),
        ("ui-orange", "#FF9152"),
    ] {
        let i = scene.material(name, color, 0.31);
        scene.materials[i].emission = 0.16;
    }
    let bytes = fs::read(root().join(source))?;
    let size = u32::from_le_bytes(bytes[..4].try_into()?) as usize;
    let header: Value = serde_json::from_slice(&bytes[4..4 + size])?;
    let cover = header["meshes"]
        .as_array()
        .unwrap()
        .iter()
        .find(|n| n["name"] == "display-cover")
        .context("display cover frame")?;
    let matrix = cover
        .get("transform")
        .or_else(|| cover.get("_scene").and_then(|n| n.get("transform")))
        .context("display cover transform")?;
    let up: V3 = std::array::from_fn(|i| matrix[i][1].as_f64().unwrap());
    let normal: V3 = std::array::from_fn(|i| matrix[i][2].as_f64().unwrap());
    let mut glass_points = Vec::new();
    for i in unit {
        if scene.objects[i].name == "display/1" {
            glass_points.extend(scene.mesh_vertices(i)?);
        }
    }
    ensure!(!glass_points.is_empty(), "enclosure display glass");
    let range = |axis: V3| {
        let mut lo = f64::INFINITY;
        let mut hi = f64::NEG_INFINITY;
        for &p in &glass_points {
            let d = dot(p, axis);
            lo = lo.min(d);
            hi = hi.max(d);
        }
        [lo, hi]
    };
    let x = range([1., 0., 0.]);
    let y = range(up);
    let z = range(normal);
    let center = add(
        add(
            add(unit_at, [(x[0] + x[1]) / 2., 0., 0.]),
            mul(up, (y[0] + y[1]) / 2.),
        ),
        mul(normal, z[1]),
    );
    for (name, x, y, w, h, material, lift, texture) in [
        (
            "Physical enclosure UI",
            -0.0499,
            -0.030,
            0.0998,
            0.06,
            "ui-blue",
            0.0004,
            None,
        ),
        (
            "Flavor selection rail",
            -0.0499,
            -0.030,
            0.013,
            0.06,
            "ui-navy",
            0.00045,
            None,
        ),
        (
            "Selected flavor panel",
            -0.0369,
            -0.030,
            0.0292,
            0.06,
            "ui-ice",
            0.00045,
            None,
        ),
        (
            "Flavor 1 rail artwork",
            -0.0474,
            0.008,
            0.008,
            0.01488,
            "ui-white",
            0.0005,
            Some(texture0.as_str()),
        ),
        (
            "Flavor 2 rail artwork",
            -0.0474,
            -0.018,
            0.008,
            0.01488,
            "ui-white",
            0.0005,
            Some(selected.as_str()),
        ),
        (
            "Selected flavor artwork",
            -0.0331,
            -0.021,
            0.0215,
            0.040,
            "ui-white",
            0.0005,
            Some(selected.as_str()),
        ),
    ] {
        quad(
            &mut scene,
            name,
            center,
            up,
            normal,
            [x, y, w, h],
            material,
            lift,
            texture,
        );
    }
    for (body, x, y, size, material) in [
        ("Fill", -0.0025, 0.024, 0.0030, "ui-white"),
        ("Prime", 0.014, 0.024, 0.0030, "ui-white"),
        ("Clean", 0.031, 0.024, 0.0030, "ui-white"),
        ("Pouring.", -0.0045, 0.013, 0.0053, "ui-white"),
        ("Reservoir", -0.0045, -0.015, 0.0027, "ui-white"),
        ("Change image", -0.0045, -0.027, 0.0024, "ui-white"),
        ("Ratio", 0.037, -0.027, 0.0024, "ui-ice"),
    ] {
        let location = add(
            add(add(center, [x, 0., 0.]), mul(up, y)),
            mul(normal, 0.00062),
        );
        let object = scene.object(
            &format!("UI {body}"),
            Geometry::Text {
                body: body.into(),
                font: root()
                    .join("hardware/install-guide/fonts/Plex-Regular.ttf")
                    .to_string_lossy()
                    .into(),
                size,
                align: "LEFT".into(),
            },
            Some(material),
            location,
        );
        scene.objects[object].rotation[0] = up[2].atan2(up[1]);
    }
    for i in 0..4 {
        quad(
            &mut scene,
            &format!("Reservoir segment {i}"),
            center,
            up,
            normal,
            [0.030 + i as f64 * 0.0046, -0.015, 0.0038, 0.0022],
            "ui-orange",
            0.00058,
            None,
        );
    }
    quad(
        &mut scene,
        "UI divider",
        center,
        up,
        normal,
        [-0.0045, -0.020, 0.0512, 0.00012],
        "ui-ice",
        0.00054,
        None,
    );
    scene.tube(
        "Faucet umbilical",
        &[
            [0.214, 0.037, 0.809],
            [0.214, 0.07, 0.66],
            [0.207, 0.232, 0.579],
            [0.19, 0.297, 0.506],
            [0.178, 0.312, 0.387],
        ],
        0.009,
        "rubber",
    );
    scene.lathe(
        "Five-pound aluminum CO2 cylinder",
        &[
            [0., 0.],
            [0.050, 0.],
            [0.062, 0.008],
            [0.0665, 0.02],
            [0.0665, 0.367],
            [0.065, 0.390],
            [0.057, 0.41],
            [0.046, 0.428],
            [0.022, 0.442],
            [0.017, 0.446],
            [0.017, 0.457],
            [0., 0.457],
        ],
        "aluminum",
        [-0.253, -0.184, 0.067],
        128,
        false,
    );
    scene.cylinder(
        "Cylinder brass valve",
        0.013,
        0.033,
        [-0.253, -0.184, 0.539],
        "brass",
    );
    scene.cylinder(
        "Cylinder valve handwheel",
        0.020,
        0.010,
        [-0.253, -0.184, 0.557],
        "rubber",
    );
    let regulator = "hardware/reference/taprite-3741-regulator/taprite-3741-regulator.step.mesh";
    let reg = hsm_render::payload::decode(&fs::read(root().join(regulator))?)?;
    for mesh in &reg {
        let mut material = Material::new(
            &format!("reg/{}", mesh.name),
            mesh.color.unwrap_or([0.4; 3]),
            0.35,
        );
        material.metal = if ["print", "dial", "band"]
            .iter()
            .any(|s| mesh.name.contains(s))
        {
            0.
        } else {
            0.76
        };
        scene.materials.push(material);
    }
    scene.load(
        regulator,
        |_| true,
        |m| format!("reg/{}", m.name),
        [-0.328, -0.184, 0.537],
        std::f64::consts::PI,
        None,
    )?;
    scene.tube(
        "CO2 supply",
        &[
            [-0.328, -0.184, 0.494],
            [-0.324, -0.15, 0.432],
            [-0.29, 0.235, 0.411],
            [-0.09, 0.285, 0.408],
            [0.168, 0.319, 0.40],
        ],
        0.0032,
        "co2-tube",
    );
    let glass = [0.214, -0.143, countertop + 0.001];
    scene.lathe(
        "Cold soda glass",
        &[
            [0., 0.],
            [0.027, 0.],
            [0.03, 0.004],
            [0.0347, 0.116],
            [0.0345, 0.119],
            [0.0331, 0.12],
            [0.0327, 0.116],
            [0.028, 0.006],
            [0., 0.006],
        ],
        "glass",
        glass,
        128,
        true,
    );
    scene.lathe(
        "Soda in the glass",
        &[
            [0., 0.006],
            [0.0277, 0.006],
            [0.0315, 0.085],
            [0.0317, 0.087],
            [0., 0.087],
        ],
        "soda",
        glass,
        128,
        true,
    );
    scene.tube(
        "Clear soda pour",
        &[
            [0.214, -0.100, countertop + 0.185],
            [0.214, -0.12, countertop + 0.145],
            [0.214, -0.14, countertop + 0.091],
        ],
        0.0016,
        "water-stream",
    );
    scene.tube(
        "Separate flavor pour",
        &[
            [0.2108, -0.103, countertop + 0.185],
            [0.2108, -0.123, countertop + 0.145],
            [0.211, -0.145, countertop + 0.091],
        ],
        0.00040,
        "flavor-stream",
    );
    let mut rng = Random::new(12);
    for i in 0..52 {
        let radius = rng.uniform(0.00055, 0.001);
        let angle = rng.uniform(0., std::f64::consts::TAU);
        let distance = rng.uniform(0.006, 0.027);
        let z = rng.uniform(0.011, 0.086);
        scene.sphere(
            &format!("Tiny carbonation bubble {i}"),
            radius,
            add(glass, [angle.cos() * distance, angle.sin() * distance, z]),
            "bubble",
            10,
            6,
        );
    }
    scene.box_(
        "Studio floor",
        [200., 200., 0.01],
        [0., 0., -0.005],
        "floor",
        0.,
    );
    let i = scene.box_(
        "Faucet close-up stone surface",
        [3., 3., 0.032],
        [0., 0., countertop - 0.016],
        "stone",
        0.004,
    );
    scene.objects[i].hidden = true;
    for (name, at, target, energy, size, color) in [
        (
            "Large soft window",
            [-1.8, -2.1, 3.],
            [0., 0., 0.55],
            220.,
            2.3,
            "#FFF9F1",
        ),
        (
            "Pale front fill",
            [1.5, -1.9, 1.5],
            [0.1, 0., 0.4],
            55.,
            1.7,
            "#E2EDFF",
        ),
        (
            "Counter and faucet rim",
            [0.5, 1.5, 2.5],
            [0., 0., 0.55],
            165.,
            1.8,
            "#FFFFFF",
        ),
        (
            "Glass reflection strip",
            [0.70, -0.9, 1.45],
            [0.20, -0.10, 0.91],
            15.,
            0.42,
            "#FFFFFF",
        ),
    ] {
        scene.light(name, at, target, energy, size, color);
    }
    let focals = BTreeMap::from([
        ("faucet".into(), [0.214, -0.093, 1.045]),
        ("faucet_base".into(), [0.214, 0.037, 0.85]),
        ("glass".into(), [0.214, -0.143, 0.90]),
        ("machine".into(), [0.144, -0.147, 0.29]),
        ("machine_display".into(), center),
        ("cylinder".into(), [-0.253, -0.184, 0.31]),
        ("counter_front".into(), [0., -0.345, 0.813]),
        ("counter_rear".into(), [0., 0.375, 0.813]),
    ]);
    Ok((scene, focals))
}
fn quad(
    scene: &mut Scene,
    name: &str,
    center: V3,
    up: V3,
    normal: V3,
    rect: [f64; 4],
    material: &str,
    lift: f64,
    texture: Option<&str>,
) {
    let [x, y, w, h] = rect;
    let points = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
        .map(|[x, y]| add(add(add(center, [x, 0., 0.]), mul(up, y)), mul(normal, lift)))
        .to_vec();
    let finish = if let Some(texture) = texture {
        let i = scene.material(name, "#FFFFFF", 0.31);
        scene.materials[i].texture = Some(texture.into());
        scene.materials[i].emission = 0.16;
        name
    } else {
        material
    };
    let mesh = scene.mesh(
        points,
        vec![vec![0, 1, 2, 3]],
        None,
        Some(vec![[0., 0.], [1., 0.], [1., 1.], [0., 1.]]),
        false,
    );
    scene.object(name, mesh, Some(finish), [0.; 3]);
}
pub fn main(mut args: Args) -> Result<()> {
    let preview = args.flag("--preview");
    let only = args.flag("--scene-only");
    let describe = args.flag("--describe-only");
    let samples = args
        .take(&["--samples"])
        .map(|n| n.parse::<usize>())
        .transpose()?;
    let image_width = args
        .take(&["--width"])
        .map(|n| n.parse::<u32>())
        .transpose()?;
    let out = args
        .take(&["--out"])
        .map(PathBuf::from)
        .unwrap_or_else(|| root().join(format!(".cache/runs/homepage-art-{}", std::process::id())));
    fs::create_dir_all(&out)?;
    let out = fs::canonicalize(out)?;
    let blender = args
        .take(&["--blender"])
        .unwrap_or_else(|| "/Applications/Blender.app/Contents/MacOS/Blender".into());
    let selected = if args.flag("--shots") {
        args.0.clone()
    } else {
        vec!["kitchen".into(), "faucet".into(), "cabinet".into()]
    };
    let (mut scene, focals) = prepare(&out, preview)?;
    if let Some(samples) = samples {
        scene.settings.samples = samples;
    }
    if only {
        scene.save = Some(out.join("kitchen.blend").to_string_lossy().into());
    }
    for shot in if only { Vec::new() } else { selected } {
        let (position, target, span, width, height) = match shot.as_str() {
            "kitchen" => ([1.35, -2.5, 1.50], [0., 0.007, 0.508], 1.29, 1800, 1800),
            "faucet" => ([0.78, -1.30, 1.37], [0.197, -0.047, 0.96], 0.53, 1800, 1350),
            "cabinet" => ([0.89, -1.70, 0.95], [-0.045, 0.01, 0.325], 0.99, 1800, 1350),
            _ => anyhow::bail!("unknown kitchen shot {shot}"),
        };
        let mut updates = Vec::new();
        for object in &scene.objects {
            let hidden = if object.name == "Faucet close-up stone surface" {
                Some(shot != "faucet")
            } else if object.name.starts_with("Standard ")
                || [
                    "Pale stone worktop",
                    "Undermount stainless sink",
                    "Sink drain",
                ]
                .contains(&object.name.as_str())
            {
                Some(shot == "faucet")
            } else {
                None
            };
            if let Some(hidden) = hidden {
                updates.push(Update {
                    name: object.name.clone(),
                    hidden: Some(hidden),
                    ..Default::default()
                });
            }
        }
        let forward = unit(sub(target, position));
        let right = unit(cross(forward, [0., 0., 1.]));
        let up = cross(right, forward);
        let projected:BTreeMap<_,_>=focals.iter().map(|(name,&point)|{let v=sub(point,position);(name,json!({"x":0.5+dot(v,right)/span,"y":0.5-dot(v,up)/span*width as f64/height as f64}))}).collect();
        write(
            out.join(format!("{shot}.focals.json")),
            serde_json::to_vec_pretty(
                &json!({"dimensions":[width,height],"normalized":projected}),
            )?,
        )?;
        scene.frames.push(Frame {
            number: 0,
            file: out.join(format!("{shot}.png")).to_string_lossy().into(),
            width: image_width.unwrap_or(if preview { width / 2 } else { width }),
            height: image_width.map_or(if preview { height / 2 } else { height }, |w| {
                (w as f64 * height as f64 / width as f64).round() as u32
            }),
            camera: Camera {
                position,
                target,
                ortho: Some(span),
                lens: 70.,
                focus: None,
                aperture: 8.,
            },
            updates,
            node_inputs: Vec::new(),
        });
    }
    let descriptor = out.join("kitchen.scene.json");
    scene.write(&descriptor)?;
    if !describe {
        crate::run(
            Command::new(blender)
                .args([
                    "--background",
                    "--factory-startup",
                    "--python-exit-code",
                    "1",
                    "--python",
                ])
                .arg(root().join("tools/render/blender_adapter.py"))
                .arg("--")
                .arg(&descriptor),
        )?;
    }
    println!("{}", out.display());
    Ok(())
}
