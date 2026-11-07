//! The main board's files: the populated board as the machine carries it, an outline slab with
//! its mounting holes, one box per component above it and the through-hole tail envelope below,
//! from the board's written-down component stock; and the board figures the wiring takes.
//!
//!     pcba-assembly [<output directory>]
//!     pcba-assembly --read-fab-model
//!
//! The second form reads the component boxes off the fab model the PCB build exports and writes
//! them down in `board-stock.json`. It runs when the board's design changes.
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::part::write_shown;
use hsm_kernel::{Body, Solid, V3, v3};
use hsm_pcba_numbers as board;
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};

const NAME: &str = "pcba-board";
const OUTPUT: &str = "hardware/printed-parts/electronics/pcba-tray";
const STOCK: &str = "hardware/printed-parts/electronics/pcba-tray/board-stock.json";
const FAB_MODEL: &str = "hardware/pcb/pcba/out/pcba.glb";

/// A box by its low corner and its size, in the board's outline-centred frame.
type Box3 = [[f64; 3]; 2];

/// The populated board's component boxes: the bodies above its top face, and the through-hole
/// tails below its underside, capped at the tail envelope.
#[derive(Serialize, Deserialize)]
struct Stock {
    above: Vec<Box3>,
    below: Vec<Box3>,
}

/// The board figures the installed machine's wiring reads: the slab, and where its outline's
/// centre stands in its own PCB frame.
#[derive(Serialize)]
struct Figures {
    board: Slab,
    mounts: [Mount; 1],
}

#[derive(Serialize)]
struct Slab {
    slab: Box3,
}

#[derive(Serialize)]
struct Mount {
    name: &'static str,
    rotation: f64,
    translation: [f64; 3],
}

fn main() -> Result<()> {
    let args: Vec<_> = std::env::args_os().skip(1).collect();
    if args.len() == 1 && args[0] == "--read-fab-model" {
        let stock = read_fab_model(&std::fs::read(FAB_MODEL).context("the board's fab model")?)?;
        std::fs::write(STOCK, stock_text(&stock)?)?;
        println!("{STOCK}: {} boxes above, {} below", stock.above.len(), stock.below.len());
        return Ok(());
    }
    if args.len() > 1 {
        bail!("usage: pcba-assembly [<output directory>] | pcba-assembly --read-fab-model");
    }
    let out = args.first().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    hsm_kernel::reads::begin();
    let bytes = std::fs::read(STOCK).context("the board's written-down stock")?;
    hsm_kernel::reads::read(Path::new(STOCK), &bytes);
    let stock: Stock = serde_json::from_slice(&bytes).context("the board's stock")?;
    std::fs::create_dir_all(&out)?;
    let solid = build(&stock)?;
    let bodies = [Body { name: NAME, color: Some(hsm_catalog::pcba()), solid: &solid }];
    println!("{}", write_shown(&out, NAME, &bodies)?);

    let [w, d] = [board::width(), board::depth()];
    let [cx, cy] = board::centre();
    let figures = Figures {
        board: Slab { slab: [[-w / 2.0, -d / 2.0, 0.0], [w, d, board::THICKNESS]] },
        mounts: [Mount { name: "pcba0", rotation: 0.0, translation: [cx, cy, 0.0] }],
    };
    std::fs::write(out.join("pcba-assembly.numbers.json"), serde_json::to_string_pretty(&figures)? + "\n")?;
    Ok(())
}

/// The stock as its file holds it: a box to a line.
fn stock_text(stock: &Stock) -> Result<String> {
    let list = |boxes: &[Box3]| -> Result<String> {
        let lines = boxes.iter().map(|b| Ok(format!("    {}", serde_json::to_string(b)?))).collect::<Result<Vec<_>>>()?;
        Ok(lines.join(",\n"))
    };
    Ok(format!("{{\n  \"above\": [\n{}\n  ],\n  \"below\": [\n{}\n  ]\n}}\n", list(&stock.above)?, list(&stock.below)?))
}

fn cuboid([origin, size]: &Box3) -> Solid {
    let o = v3(origin[0], origin[1], origin[2]);
    Solid::cuboid(o, o + v3(size[0], size[1], size[2]))
}

/// A cylinder along Z from `(x, y, z)`.
fn cylinder(x: f64, y: f64, z: f64, radius: f64, height: f64) -> Result<Solid> {
    Solid::cylinder(v3(x, y, z), V3::Z, radius, height)
}

fn build(stock: &Stock) -> Result<Solid> {
    let [c0, c1] = board::centre();
    let (w, d, t) = (board::width(), board::depth(), board::THICKNESS);
    let bores = board::HOLES
        .iter()
        .map(|p| cylinder(p[0] - c0, p[1] - c1, -0.5, board::HOLE_DIAMETER / 2.0, t + 1.0))
        .collect::<Result<Vec<_>>>()?;
    let mut parts = vec![cuboid(&[[-w / 2.0, -d / 2.0, 0.0], [w, d, t]]).cut_all(&bores)?];
    parts.extend(stock.above.iter().map(cuboid));
    let slab = Solid::union_all(&parts)?;
    let solid = if stock.below.is_empty() {
        slab
    } else {
        let (reach, drop) = (board::HOLE_REACH, board::PIN_DROP);
        let keepouts: Vec<Solid> = board::HOLES
            .iter()
            .map(|p| cuboid(&[[p[0] - c0 - reach, p[1] - c1 - reach, -drop - 0.5], [2.0 * reach, 2.0 * reach, drop + 1.0]]))
            .collect();
        let tails: Vec<Solid> = stock.below.iter().map(cuboid).collect();
        let mut under = vec![Solid::union_all(&tails)?.cut_all(&keepouts)?];
        for joint in &board::JOINTS {
            under.push(cylinder(joint.at[0] - c0, joint.at[1] - c1, -drop, joint.diameter / 2.0, drop)?);
        }
        slab.union(&Solid::union_all(&under)?)?
    };
    ensure!(
        (solid.bounds().min.z + board::PIN_DROP).abs() <= 1e-9,
        "the populated board ends at its pin-tail clearance plane"
    );
    Ok(solid)
}

/// The fab model's scene, as far as the component boxes need it.
#[derive(Deserialize)]
struct Gltf {
    accessors: Vec<Accessor>,
    meshes: Vec<Mesh>,
    #[serde(default)]
    nodes: Vec<Node>,
}

#[derive(Deserialize)]
struct Accessor {
    min: Option<Vec<f64>>,
    max: Option<Vec<f64>>,
}

#[derive(Deserialize)]
struct Mesh {
    primitives: Vec<Primitive>,
}

#[derive(Deserialize)]
struct Primitive {
    attributes: Attributes,
}

#[derive(Deserialize)]
struct Attributes {
    #[serde(rename = "POSITION")]
    position: usize,
}

#[derive(Deserialize)]
struct Node {
    mesh: Option<usize>,
    translation: Option<[f64; 3]>,
    scale: Option<[f64; 3]>,
    rotation: Option<[f64; 4]>,
}

/// Each meshed node's box in the fab model, in millimetres: X, Y and Z low and high.
fn fab_boxes(glb: &[u8]) -> Result<Vec<[f64; 6]>> {
    ensure!(glb.len() >= 20 && &glb[..4] == b"glTF", "the fab model is a GLB");
    let n = u32::from_le_bytes(glb[12..16].try_into()?) as usize;
    let scene: Gltf = serde_json::from_slice(glb.get(20..20 + n).context("the GLB's JSON chunk")?)?;
    let mut boxes = vec![];
    for node in &scene.nodes {
        let Some(mesh) = node.mesh else { continue };
        let t = node.translation.unwrap_or([0.0; 3]);
        let s = node.scale.unwrap_or([1.0; 3]);
        let (mut lo, mut hi) = ([f64::INFINITY; 3], [f64::NEG_INFINITY; 3]);
        for primitive in &scene.meshes.get(mesh).context("a node's mesh")?.primitives {
            let a = scene.accessors.get(primitive.attributes.position).context("a position accessor")?;
            let (mn, mx) = (a.min.as_deref().context("its low bound")?, a.max.as_deref().context("its high bound")?);
            for corner in 0..8 {
                let mut p: [f64; 3] = std::array::from_fn(|i| if (corner >> i) & 1 != 0 { mn[i] * s[i] } else { mx[i] * s[i] });
                if let Some([qx, qy, qz, qw]) = node.rotation {
                    let [x, y, z] = p;
                    p = [
                        x * (1.0 - 2.0 * (qy * qy + qz * qz)) + y * 2.0 * (qx * qy - qz * qw) + z * 2.0 * (qx * qz + qy * qw),
                        x * 2.0 * (qx * qy + qz * qw) + y * (1.0 - 2.0 * (qx * qx + qz * qz)) + z * 2.0 * (qy * qz - qx * qw),
                        x * 2.0 * (qx * qz - qy * qw) + y * 2.0 * (qy * qz + qx * qw) + z * (1.0 - 2.0 * (qx * qx + qy * qy)),
                    ];
                }
                for i in 0..3 {
                    lo[i] = lo[i].min(p[i] + t[i]);
                    hi[i] = hi[i].max(p[i] + t[i]);
                }
            }
        }
        boxes.push([1000.0 * lo[0], 1000.0 * hi[0], 1000.0 * lo[1], 1000.0 * hi[1], 1000.0 * lo[2], 1000.0 * hi[2]]);
    }
    Ok(boxes)
}

/// The component stock read off the fab model: each component's box above the top face, and its
/// tails below the underside capped at the tail envelope, outline-centred.
fn read_fab_model(glb: &[u8]) -> Result<Stock> {
    let [c0, c1] = board::centre();
    let top = board::FAB_HALF_THICKNESS;
    let (mut above, mut below) = (vec![], vec![]);
    for [x0, x1, y0, y1, z0, z1] in fab_boxes(glb)? {
        let (w, d) = (x1 - x0, y1 - y0);
        if w < board::FAB_LEAST_BOX || d < board::FAB_LEAST_BOX || z1 - z0 < board::FAB_LEAST_BOX {
            continue;
        }
        if w > board::width() * board::FAB_BOARD_SHARE && d > board::depth() * board::FAB_BOARD_SHARE {
            continue;
        }
        if z1 > top + board::FAB_FACE_MARGIN {
            above.push([[x0 - c0, y0 - c1, board::THICKNESS], [w, d, z1 - top]]);
        }
        if z0 < -top - board::FAB_FACE_MARGIN {
            let zb = (-board::PIN_DROP).max(z0 + top);
            below.push([[x0 - c0, y0 - c1, zb], [w, d, -zb]]);
        }
    }
    Ok(Stock { above, below })
}
