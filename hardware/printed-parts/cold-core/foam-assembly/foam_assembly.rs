//! The foam assembly's files: the cold core's casing in the shell's frame, its printed pieces
//! placed from their own fine models, which the whole-machine program seats the core by
//! (`foam-assembly.step.npz`); and the stack's floor, the cap's face, the cap's conduits and the
//! lines potted in the casing, which the machine continues its own runs from
//! (`foam-assembly.numbers.json`).
//!
//!     foam-assembly [<output directory>]
use anyhow::{Context, Result, anyhow, bail};
use hsm_cold_core_layout::routes;
use hsm_foam_assembly_numbers::{self as numbers, Passage};
use hsm_kernel::write::Body;
use hsm_kernel::{Solid, V3, v3};
use serde_json::{Value, json};
use std::path::{Path, PathBuf};

const NAME: &str = "foam-assembly";
const OUTPUT: &str = "hardware/printed-parts/cold-core/foam-assembly";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: foam-assembly [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let casing = casing()?;
    let bodies: Vec<Body> =
        casing.iter().map(|(name, colour, solid)| Body { name, color: Some(*colour), solid }).collect();
    let document = json!({"frame": "foam assembly source", "schema": "hsm-foam-assembly-1"});
    let files = [
        (format!("{NAME}.step.npz"), hsm_kernel::step::model_bytes_with_document(&bodies, Some(&document))),
        (format!("{NAME}.numbers.json"), format!("{:#}\n", report()).into_bytes()),
    ];
    for (file, bytes) in &files {
        keep(&out.join(file), bytes)?;
    }
    let held: Vec<Value> = bodies
        .iter()
        .map(|b| {
            let s = b.solid.bounds();
            let (min, max) = (s.min.to_array(), s.max.to_array());
            json!({"name": b.name, "volume": b.solid.volume(), "min": min, "max": max})
        })
        .collect();
    println!(
        "{}",
        json!({"files": files.iter().map(|(f, _)| f.as_str()).collect::<Vec<_>>(), "bodies": held})
    );
    Ok(())
}

/// The casing's pieces, each fine body of each piece's model turned and lifted into place.
fn casing() -> Result<Vec<(&'static str, [f64; 3], Solid)>> {
    let mut placed = vec![];
    for piece in numbers::pieces() {
        for body in
            hsm_kernel::import::model(piece.model).with_context(|| format!("reading {}", piece.model))?
        {
            let mut fine = body.solid;
            if piece.turn != 0. {
                fine = fine.rotate(V3::ZERO, v3(0., 0., 1.), piece.turn);
            }
            if piece.lift != 0. {
                fine = fine.translate(v3(0., 0., piece.lift));
            }
            placed.push((piece.name, piece.colour.linear, fine));
        }
    }
    Ok(placed)
}

/// What the machine takes from the casing: the cap's face and the stack's floor, each conduit's
/// mouth and the bore or run below it, and each line potted in the casing.
fn report() -> Value {
    let probes: Vec<Value> = numbers::conduits()
        .into_iter()
        .map(|c| match c.passage {
            Passage::Bore { foot } => {
                json!({"name": c.name, "kind": "cylinder", "mouth": c.mouth, "at": foot})
            }
            Passage::Run { points, bend } => {
                json!({"name": c.name, "kind": "route", "mouth": c.mouth, "points": points, "bend": bend})
            }
        })
        .collect();
    let lines: Vec<Value> =
        routes::lines().into_iter().map(|l| json!({"name": l.name, "points": l.points})).collect();
    let (face, floor) = (hsm_foam_cap_numbers::face_z(), hsm_foam_cap_numbers::stack_floor_z());
    json!({"report": {"face": face, "floor": floor, "probes": probes}, "routes": lines})
}

/// `bytes` at `path`, unless the file holds them already; any other lands whole, by a rename.
fn keep(path: &Path, bytes: &[u8]) -> Result<()> {
    if std::fs::read(path).is_ok_and(|held| held == bytes) {
        return Ok(());
    }
    let file = path
        .file_name()
        .and_then(|f| f.to_str())
        .ok_or_else(|| anyhow!("no file name in {}", path.display()))?;
    let tmp = path.with_file_name(format!(".{file}.{}.{file}", std::process::id()));
    std::fs::write(&tmp, bytes).with_context(|| format!("writing {}", tmp.display()))?;
    std::fs::rename(&tmp, path).with_context(|| format!("renaming onto {}", path.display()))
}
