//! The manual refresh renders current scenes and registers their artwork, cameras and source hashes.
use crate::{Options, pixels};
use anyhow::{Context, Result, ensure};
use hsm_pages::RgbaImage;
use hsm_run_slots::{Lease, ipc};
use serde::Deserialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
    process::Command,
    time::{SystemTime, UNIX_EPOCH},
};

#[derive(Deserialize)]
struct Screen {
    centre: [f64; 3],
    normal: [f64; 3],
    up: [f64; 3],
    width: f64,
    height: f64,
}

#[derive(Deserialize)]
struct View {
    name: String,
    path: PathBuf,
    cam: [f64; 3],
    target: [f64; 3],
    #[serde(default = "camera_up")]
    up: [f64; 3],
    span: f64,
    reference_size: [u32; 2],
    scale: f64,
    anchors: BTreeMap<String, [f64; 3]>,
}

fn camera_up() -> [f64; 3] {
    [0., 0., 1.]
}

#[derive(Deserialize)]
struct Scenes {
    source: PathBuf,
    source_sha256: String,
    screen: Screen,
    bottle_mouth: [f64; 3],
    views: Vec<View>,
}

#[derive(Deserialize)]
struct Camera {
    view_proj: [f64; 16],
}

#[derive(Deserialize)]
struct RenderReport {
    camera: Camera,
}

fn read(path: &Path) -> Result<Value> {
    serde_json::from_slice(&fs::read(path).with_context(|| format!("read {}", path.display()))?)
        .with_context(|| format!("JSON in {}", path.display()))
}

fn write(path: &Path, bytes: &[u8]) -> Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    fs::write(path, bytes).with_context(|| format!("write {}", path.display()))
}

fn write_json(path: &Path, value: &Value) -> Result<()> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    write(path, &bytes)
}

fn digest(path: &Path) -> Result<String> {
    Ok(format!(
        "{:x}",
        Sha256::digest(fs::read(path).with_context(|| format!("hash {}", path.display()))?)
    ))
}

fn named(path: &Path, root: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .to_string_lossy()
        .into_owned()
}

fn command(command: &mut Command, root: &Path, lease: &Lease) -> Result<Vec<u8>> {
    command.current_dir(root);
    lease.apply(command)?;
    let result = ipc::output(command).with_context(|| format!("start {command:?}"))?;
    ensure!(
        result.status.success(),
        "command failed: {command:?}\n{}\n{}",
        String::from_utf8_lossy(&result.stderr),
        String::from_utf8_lossy(&result.stdout)
    );
    Ok(result.stdout)
}

fn csv(point: [f64; 3]) -> String {
    point.map(|v| v.to_string()).join(",")
}

fn screen_corners(screen: &Screen, matrix: &[f64; 16], size: [u32; 2]) -> Result<[[f64; 2]; 4]> {
    let center: [f64; 3] = std::array::from_fn(|i| screen.centre[i] + screen.normal[i] * 0.15);
    let x = [screen.width / 2., 0., 0.];
    let y = screen.up.map(|v| v * screen.height / 2.);
    let mut corners = [[0.; 2]; 4];
    for (i, [sx, sy]) in [[-1., 1.], [1., 1.], [1., -1.], [-1., -1.]]
        .into_iter()
        .enumerate()
    {
        corners[i] = pixels::project(
            std::array::from_fn(|j| center[j] + sx * x[j] + sy * y[j]),
            matrix,
            size,
        )?;
    }
    Ok(corners)
}

pub(super) fn run(options: Options) -> Result<()> {
    let root = options
        .root
        .unwrap_or(std::env::current_dir()?)
        .canonicalize()?;
    ensure!(
        root.join("hardware/install-guide").is_dir(),
        "--root must name the repository"
    );
    let run = options.out.unwrap_or_else(|| {
        root.join(".cache/runs").join(format!(
            "install-guide-{}-{}",
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs(),
            std::process::id()
        ))
    });
    fs::create_dir_all(&run)?;
    let run = run.canonicalize()?;
    let original_assets = root.join("hardware/install-guide/assets");
    let assets = options.assets.unwrap_or_else(|| original_assets.clone());
    fs::create_dir_all(&assets)?;
    let assets = assets.canonicalize()?;
    let registration_file = assets.join("print-resolution.json");
    let registration_source = if registration_file.is_file() {
        registration_file.clone()
    } else {
        original_assets.join("print-resolution.json")
    };
    let mut registrations = read(&registration_source)?;
    let lease = hsm_run_slots::acquire(
        "install-guide illustrations",
        hsm_run_slots::inherited()?,
        false,
    )?;
    let builder = root.join("tools/hsm/target/release/install-illustrations");
    ensure!(
        builder.is_file(),
        "build hsm-kit-art's install-illustrations before refreshing artwork"
    );
    command(Command::new(builder).arg(&run), &root, &lease)?;
    let manifest = read(&run.join("scenes.json"))?;
    let scenes: Scenes = serde_json::from_value(manifest.clone())?;
    for name in &options.views {
        ensure!(
            scenes.views.iter().any(|view| &view.name == name),
            "unknown illustration {name}"
        );
    }
    let screen_path = original_assets.join("fill-screen.png");
    let mut screen = None;
    let mut receipts = Vec::new();
    for view in &scenes.views {
        if !options.views.is_empty() && !options.views.contains(&view.name) {
            continue;
        }
        ensure!(
            view.scale.is_finite() && view.scale > 0.,
            "{} has invalid scale",
            view.name
        );
        let size = view.reference_size.map(|v| (v as f64 * view.scale) as u32);
        ensure!(
            size[0] > 0 && size[1] > 0,
            "{} has empty dimensions",
            view.name
        );
        let path = run.join(format!("{}.png", view.name));
        let stdout = command(
            Command::new("hsm")
                .arg("--root")
                .arg(&root)
                .args(["render", "manifold-layout/enclosure-assembly.step"])
                .arg(&path)
                .arg("--payload")
                .arg(&view.path)
                .arg("--cam")
                .arg(csv(view.cam))
                .arg("--target")
                .arg(csv(view.target))
                .arg("--up")
                .arg(csv(view.up))
                .arg("--span")
                .arg(view.span.to_string())
                .arg("--size")
                .arg(format!("{}x{}", size[0], size[1]))
                .args(["--transparent", "--no-ground", "--no-fog", "--json"]),
            &root,
            &lease,
        )?;
        let report: Value = serde_json::from_slice(&stdout).context("renderer report")?;
        let report: RenderReport = serde_json::from_value(if report.is_array() {
            report[0].clone()
        } else {
            report
        })?;
        let matrix = &report.camera.view_proj;
        let mut image = RgbaImage::read_png(&fs::read(&path)?)?;
        ensure!(
            [image.width, image.height] == size,
            "renderer dimensions differ for {}",
            view.name
        );
        if view.name.starts_with("fill-") {
            if screen.is_none() {
                screen = Some(RgbaImage::read_png(&fs::read(&screen_path)?)?);
            }
            pixels::overlay(
                &mut image,
                screen.as_ref().unwrap(),
                screen_corners(&scenes.screen, matrix, size)?,
            )?;
        }
        let framed = view.name == "fill-screen-framed";
        let relative = if framed {
            "fill-screen-framed.png".to_owned()
        } else {
            format!("steps/{}.png", view.name)
        };
        let target = assets.join(&relative);
        write(&target, &image.png()?)?;
        let reference_name = if framed || view.name.starts_with("fill-") {
            format!("{}.png", view.name)
        } else {
            format!("rear-layout-{}.png", view.name)
        };
        let reference_relative = format!("reference/{reference_name}");
        let reference = assets.join(&reference_relative);
        write(
            &reference,
            &pixels::resize(&image, view.reference_size)?.png()?,
        )?;
        let mut row = registrations["assets"][&relative]
            .as_object()
            .cloned()
            .unwrap_or_default();
        row.remove("fixed_native_crop");
        row.extend(
            json!({"reference_size":view.reference_size,"render_size":size,
            "scale":[view.scale,view.scale],"coordinate_reference_path":reference_relative,
            "coordinate_reference_sha256":digest(&reference)?,"render_sha256":digest(&target)?,
            "source_sha256":scenes.source_sha256})
            .as_object()
            .unwrap()
            .clone(),
        );
        if !framed {
            let anchors: BTreeMap<_, _> = view
                .anchors
                .iter()
                .map(|(key, point)| {
                    Ok((
                        key.clone(),
                        pixels::project(*point, matrix, view.reference_size)?,
                    ))
                })
                .collect::<Result<_>>()?;
            row.extend(
                json!({"scene_mesh_sha256":digest(&view.path)?,
                "registered_camera":{"cam":view.cam,"target":view.target,"span":view.span},
                "anchor_source_mm":view.anchors,"anchors_reference_pixels":anchors})
                .as_object()
                .unwrap()
                .clone(),
            );
        }
        registrations["assets"][&relative] = Value::Object(row);
        receipts
            .push(json!({"name":view.name,"sha256":digest(&target)?,"path":named(&target,&root)}));
        println!("{}: {}x{}", view.name, size[0], size[1]);
    }
    write_json(&registration_file, &registrations)?;
    let fills: Vec<_> = receipts
        .iter()
        .filter(|r| r["name"].as_str().is_some_and(|n| n.starts_with("fill-")))
        .collect();
    if !fills.is_empty() {
        let file = assets.join("fill-scene-inputs.json");
        let source = if file.is_file() {
            file.clone()
        } else {
            original_assets.join("fill-scene-inputs.json")
        };
        let mut fill = read(&source)?;
        fill["purpose"] =
            json!("The Fill pictures and their motion cue follow the current appliance geometry.");
        fill["sources"] = json!({});
        fill["sources"][named(&scenes.source, &root)] = json!(scenes.source_sha256);
        for name in [
            "tools/install-guide/art.rs",
            "tools/hsm/install-art/Cargo.toml",
            "tools/hsm/install-art/src/main.rs",
            "tools/hsm/install-art/src/refresh.rs",
            "tools/hsm/install-art/src/pixels.rs",
        ] {
            fill["sources"][name] = json!(digest(&root.join(name))?);
        }
        fill["sources"]["hardware/install-guide/assets/fill-screen.png"] =
            json!(digest(&screen_path)?);
        fill["screen"] = manifest["screen"].clone();
        if fills.iter().any(|r| r["name"] == "fill-ready") {
            fill["bottle_mouth"] = json!(scenes.bottle_mouth);
            fill["arrow"] = json!(
                (0..=10)
                    .map(|i| {
                        let a = (20. * i as f64 / 10.).to_radians();
                        [
                            scenes.bottle_mouth[0],
                            scenes.bottle_mouth[1] - 190. * a.cos(),
                            scenes.bottle_mouth[2] + 190. * a.sin(),
                        ]
                    })
                    .collect::<Vec<_>>()
            );
            let view = scenes
                .views
                .iter()
                .find(|v| v.name == "fill-ready")
                .unwrap();
            fill["pose"] = json!({"cam":view.cam,"target":view.target,"span":view.span,"size":view.reference_size});
        }
        for receipt in fills {
            fill["outputs_sha256"][receipt["path"].as_str().unwrap()] = receipt["sha256"].clone();
            fill["views"][receipt["name"].as_str().unwrap()] = json!({"source_payload_sha256":scenes.source_sha256,
                "render_sha256":receipt["sha256"]});
        }
        write_json(&file, &fill)?;
    }
    write_json(
        &run.join("result.json"),
        &json!({"purpose":"The install guide refresh records the current appliance artwork and its sources.",
        "source_sha256":scenes.source_sha256,"images":receipts}),
    )?;
    for view in &scenes.views {
        for temporary in [
            view.path.clone(),
            run.join(format!("{}-props.mesh", view.name)),
            run.join(format!("{}.png", view.name)),
        ] {
            if temporary.parent() == Some(run.as_path()) && temporary.is_file() {
                fs::remove_file(temporary)?;
            }
        }
    }
    Ok(())
}
