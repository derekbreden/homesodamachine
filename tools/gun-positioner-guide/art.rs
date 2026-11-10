//! The PGFUN guide illustrates the retained assembly meshes with operation colours and labels.
use anyhow::{Context, Result, ensure};
use hsm_pages::{Font, Page, Path as DrawPath, Pen, Rgb, Run};
use hsm_pgfun_positioner::{Design, Mesh, load_meshes};
use serde::Deserialize;
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;
use std::sync::Arc;

#[derive(Clone, Copy)]
pub struct Scene {
    pub name: &'static str,
    pub labels: &'static [(&'static str, &'static str)],
    active: &'static [&'static str],
    select: fn(&str) -> bool,
}

pub const SCENES: &[Scene] = &[
    Scene {
        name: "assembly",
        select: |n| !starts(n, &["camera", "raynox", "controller", "fan", "umbilical"]),
        labels: &[
            ("yaw-reducer", "Swivel drive"),
            ("pitch-reducer", "Pivot drive"),
            ("lower-cradle", "Gun supported below"),
            ("rotator:recessed-cap", "Recessed tube joint"),
        ],
        active: &["yaw-reducer", "pitch-reducer", "lower-cradle"],
    },
    Scene {
        name: "bridge",
        select: |n| {
            starts(
                n,
                &["bridge", "bench-toe", "motor-pedestal", "rotator:base"],
            )
        },
        labels: &[
            ("bridge", "Printed bridge"),
            ("bench-toe-1", "Bench toes"),
            ("motor-pedestal", "Motor pedestal"),
            ("rotator:base", "Existing base"),
        ],
        active: &["bridge", "bench-toe-1", "bench-toe-2", "motor-pedestal"],
    },
    Scene {
        name: "motors",
        select: |n| matches!(n, "pitch-reducer" | "pitch-motor"),
        labels: &[
            ("pitch-motor", "NEMA 17 motor"),
            ("pitch-reducer", "PGFUN 50:1"),
        ],
        active: &["pitch-reducer"],
    },
    Scene {
        name: "yaw",
        select: |n| {
            starts(n, &["motor-pedestal", "yaw-"]) && !n.contains("holder") && !n.contains("stop")
        },
        labels: &[
            ("yaw-bearing-cartridge", "Bearing cartridge"),
            ("yaw-journal", "Supported journal"),
            ("yaw-reducer", "PGFUN 50:1"),
            ("yaw-motor", "Motor below the base"),
        ],
        active: &[
            "yaw-bearing-cartridge",
            "yaw-journal",
            "yaw-output-adapter",
            "yaw-bearing-cap",
        ],
    },
    Scene {
        name: "pivot",
        select: |n| {
            starts(
                n,
                &[
                    "fork",
                    "pitch-",
                    "left-cheek",
                    "right-cheek",
                    "bottom-frame",
                    "opposite-",
                    "axle-",
                ],
            ) && !n.contains("holder")
                && !n.contains("stop")
                && !n.contains("standoff")
        },
        labels: &[
            ("fork", "Fixed fork"),
            ("left-cheek", "Driven cheek"),
            ("right-cheek", "Opposite cheek"),
            ("opposite-bearing-cap", "6001 bearing pair"),
        ],
        active: &["left-cheek", "right-cheek", "bottom-frame-tie"],
    },
    Scene {
        name: "cradle",
        select: |n| {
            starts(
                n,
                &[
                    "gun:",
                    "gun-retainer",
                    "liner-",
                    "lower-cradle",
                    "left-cheek",
                    "right-cheek",
                    "bottom-frame",
                ],
            )
        },
        labels: &[
            ("lower-cradle", "Lower cradle"),
            ("gun-retainer-1", "Front housing band"),
            ("gun-retainer-2", "Rear housing band"),
        ],
        active: &["lower-cradle", "gun-retainer-1", "gun-retainer-2"],
    },
    Scene {
        name: "stops",
        select: |n| {
            matches!(
                n,
                "fork" | "left-cheek" | "yaw-bearing-cartridge" | "yaw-journal"
            ) || n.contains("stop-")
                || n.contains("limit-holder")
                || n.contains("standoff")
        },
        labels: &[
            ("yaw-stop-sector", "Yaw positive stop"),
            ("pitch-stop-sector", "Pitch positive stop"),
            ("pitch-switch-standoff-1", "Pitch switch standoffs"),
        ],
        active: &[
            "yaw-stop-sector",
            "pitch-stop-sector",
            "yaw-limit-holder-1",
            "yaw-limit-holder--1",
            "pitch-limit-holder-1",
            "pitch-limit-holder--1",
        ],
    },
    Scene {
        name: "camera",
        select: |n| {
            starts(
                n,
                &[
                    "camera",
                    "raynox",
                    "rotator:spool",
                    "rotator:recessed-cap",
                    "rotator:tube-nest",
                ],
            )
        },
        labels: &[
            ("camera-riser-base", "Level camera base"),
            ("camera-riser-top", "Camera tray"),
            ("camera-lens-upright", "Macro carrier"),
            ("camera-lens-cassette", "Raynox cassette"),
        ],
        active: &[
            "camera-lens-upright",
            "camera-lens-cassette",
            "camera-lens-retainer",
        ],
    },
    Scene {
        name: "controller",
        select: |n| starts(n, &["controller", "fan", "umbilical"]),
        labels: &[
            ("controller-case", "SKR Pico case"),
            ("fan-guard", "24 V fan guard"),
            ("umbilical-saddle", "Cable saddle"),
            ("umbilical-post-base", "Open service bore"),
        ],
        active: &["controller-case", "umbilical-saddle"],
    },
];

fn starts(name: &str, prefixes: &[&str]) -> bool {
    prefixes.iter().any(|prefix| name.starts_with(prefix))
}
fn sub(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    std::array::from_fn(|i| a[i] - b[i])
}
fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    (0..3).map(|i| a[i] * b[i]).sum()
}
fn cross(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
fn unit(a: [f64; 3]) -> [f64; 3] {
    let length = dot(a, a).sqrt().max(1e-9);
    a.map(|v| v / length)
}

#[derive(Deserialize)]
struct Printed {
    name: String,
}

struct Triangle {
    points: [[f64; 2]; 3],
    depth: f64,
    color: Rgb,
}

fn picture(
    meshes: &BTreeMap<String, Mesh>,
    printed: &BTreeSet<String>,
    scene: Scene,
    font: &Arc<Font>,
) -> Result<Page> {
    let view = unit([1.15, -1.8, 1.05]);
    let right = unit(cross([0., 0., 1.], view));
    let up = cross(view, right);
    let projected = |p: [f64; 3]| [dot(p, right), dot(p, up), dot(p, view)];
    let mut triangles = Vec::new();
    let mut centres = BTreeMap::new();
    let mut lo = [f64::INFINITY; 2];
    let mut hi = [f64::NEG_INFINITY; 2];
    for (name, mesh) in meshes.iter().filter(|(name, _)| (scene.select)(name)) {
        let points: Vec<_> = mesh.vertices.iter().copied().map(projected).collect();
        ensure!(!points.is_empty(), "empty guide mesh {name}");
        for p in &points {
            for i in 0..2 {
                lo[i] = lo[i].min(p[i]);
                hi[i] = hi[i].max(p[i]);
            }
        }
        centres.insert(
            name.as_str(),
            [
                points.iter().map(|p| p[0]).sum::<f64>() / points.len() as f64,
                points.iter().map(|p| p[1]).sum::<f64>() / points.len() as f64,
            ],
        );
        let mut base = if printed.contains(name) {
            [0.26, 0.28, 0.34]
        } else {
            [0.69, 0.73, 0.80]
        };
        if name.starts_with("gun:") {
            base = [0.20, 0.22, 0.28];
        }
        if name.starts_with("rotator:") {
            base = [0.73, 0.77, 0.84];
        }
        if name.starts_with("liner-") {
            base = [0.13, 0.14, 0.18];
        }
        if scene.active.contains(&name.as_str()) {
            base = [0.84, 0.25, 0.31];
        }
        for face in &mesh.faces {
            let [a, b, c] = face.map(|i| i as usize);
            let normal = unit(cross(
                sub(mesh.vertices[b], mesh.vertices[a]),
                sub(mesh.vertices[c], mesh.vertices[a]),
            ));
            let light = 0.66 + 0.34 * dot(normal, [0.3, -0.4, 0.85]).max(0.);
            let color = base.map(|v| (v * light).clamp(0., 1.));
            triangles.push(Triangle {
                points: [a, b, c].map(|i| [points[i][0], points[i][1]]),
                depth: (points[a][2] + points[b][2] + points[c][2]) / 3.,
                color: Rgb {
                    r: color[0],
                    g: color[1],
                    b: color[2],
                },
            });
        }
    }
    ensure!(
        lo.iter().all(|v| v.is_finite()),
        "guide scene has no selected meshes: {}",
        scene.name
    );
    let size = [hi[0] - lo[0], hi[1] - lo[1]];
    let viewport = [187.2, 25.056, 547.2, 400.896];
    let scale = ((viewport[2] - viewport[0]) / (size[0] * 1.14))
        .min((viewport[3] - viewport[1]) / (size[1] * 1.14));
    let centre = [(lo[0] + hi[0]) / 2., (lo[1] + hi[1]) / 2.];
    let place = |p: [f64; 2]| {
        [
            (viewport[0] + viewport[2]) / 2. + (p[0] - centre[0]) * scale,
            (viewport[1] + viewport[3]) / 2. + (p[1] - centre[1]) * scale,
        ]
    };
    triangles.sort_by(|a, b| a.depth.total_cmp(&b.depth));
    let mut page = Page::default();
    for triangle in triangles {
        page.fill(
            DrawPath::polyline(&triangle.points.map(place), true),
            triangle.color,
        );
    }
    for (i, (name, label)) in scene.labels.iter().enumerate() {
        let Some(centre) = centres.get(name) else {
            continue;
        };
        let left = i % 2 == 0;
        let target = place([
            if left {
                lo[0] - size[0] * 0.10
            } else {
                hi[0] + size[0] * 0.10
            },
            hi[1] - (i as f64 + 0.45) / (scene.labels.len() as f64 + 0.2) * size[1],
        ]);
        page.stroke(
            DrawPath::polyline(&[place(*centre), target], false),
            Pen::new(Rgb::hex("#606A78"), 0.8),
        );
        let width = font.width(label, 13.);
        page.text(Run {
            font: font.clone(),
            size: 13.,
            at: [target[0] - if left { width } else { 0. }, target[1] - 4.],
            color: Rgb::hex("#202337"),
            char_space: 0.,
            word_space: 0.,
            text: (*label).into(),
        });
    }
    Ok(page)
}

pub fn render(root: &Path, output: &Path, names: &[String], inputs: Option<&Path>) -> Result<()> {
    for name in names {
        ensure!(
            SCENES.iter().any(|scene| scene.name == name),
            "unknown PGFUN guide illustration {name}"
        );
    }
    let cad = inputs
        .map(Path::to_path_buf)
        .unwrap_or_else(|| root.join("hardware/printed-parts/fixtures/pgfun-positioner"));
    let design = Design::read(&cad.join("design.json"))?;
    let transform = design.gun_transform();
    let mut meshes = load_meshes(&cad.join("assembly-meshes.npz"))?;
    for (name, mut mesh) in load_meshes(&cad.join("reference-meshes.npz"))? {
        if name.starts_with("gun:") {
            for point in &mut mesh.vertices {
                let old = *point;
                *point = std::array::from_fn(|row| {
                    transform.m[row][3]
                        + (0..3)
                            .map(|col| transform.m[row][col] * old[col])
                            .sum::<f64>()
                });
            }
        }
        meshes.insert(name, mesh);
    }
    let printed: Vec<Printed> =
        serde_json::from_slice(&std::fs::read(cad.join("display-meshes.json"))?)?;
    let printed = printed.into_iter().map(|p| p.name).collect();
    let font = Arc::new(Font::new(
        "Plex",
        std::fs::read(root.join("hardware/install-guide/fonts/Plex-Regular.ttf"))?,
    )?);
    for scene in SCENES {
        if !names.is_empty() && !names.iter().any(|name| name == scene.name) {
            continue;
        }
        let page = picture(&meshes, &printed, *scene, &font)?;
        let mut pixmap =
            tiny_skia::Pixmap::new(2200, 1276).context("PGFUN guide illustration canvas")?;
        hsm_pages::raster::draw(
            &mut pixmap,
            &page,
            hsm_pages::raster::fit([720., 417.6], 2200, 0),
        );
        let target = output.join(format!("{}.png", scene.name));
        std::fs::create_dir_all(output)?;
        std::fs::write(&target, pixmap.encode_png()?)?;
        println!("{}", target.display());
    }
    Ok(())
}
