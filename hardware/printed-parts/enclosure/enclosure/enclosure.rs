//! The enclosure model the site draws: its five shown pieces in place, read from their fine
//! models, with the pump dock's purchased tees and stem elbows at the stations the declared Box
//! sets.
//!
//!     enclosure [--box <declared Box>] [<output directory>]
//!
//! It runs at the repository root, or a copy of the files it reads at their repository paths:
//! the pieces' fine models in `hardware/printed-parts/enclosure/enclosure`, the tee's drawing and
//! the stem elbow's fine model. It writes the model beside the pieces unless told otherwise.
use anyhow::{Context, Result, bail};
use hsm_enclosure_dock_numbers as dock;
use hsm_enclosure_numbers::catalog::{digits, elbow_color, tee_color, wall_color};
use hsm_enclosure_numbers::spec::{Box, ColletPlate};
use hsm_kernel::write::Body;
use hsm_kernel::{Affine, Solid, V3, v3};
use hsm_model_export::model::{Ref, physical_rows};
use std::path::{Path, PathBuf};

const BOX: &str = "hardware/manifold-layout/enclosure-box.json";
const PIECES: &str = "hardware/printed-parts/enclosure/enclosure";
/// The tee's drawing: its manifest names no fine model, so the dock places the drawing.
const TEE: &str = "hardware/reference/tee-connector/tee-connector.step.mesh";
/// The stem elbow's fine model, as its manifest names it.
const ELBOW: &str = "hardware/reference/neofit-stem-elbow/neofit-stem-elbow.fine.step.npz";

/// The pieces the enclosure model shows, in its order: each one's files, and its body's name.
const SHOWN: [(&str, &str); 5] = [
    ("enclosure-front-bottom", "enclosure_front_bottom"),
    ("enclosure-front-top", "enclosure_front_top"),
    ("enclosure-back-bottom", "enclosure_back_bottom"),
    ("enclosure-back-top", "enclosure_back_top"),
    ("enclosure-pump-retainer-seated", "enclosure_pump_retainer"),
];

const USAGE: &str = "usage: enclosure [--box <declared Box>] [<output directory>]";

fn main() -> Result<()> {
    let (mut declared, mut out) = (PathBuf::from(BOX), None);
    let mut args = std::env::args_os().skip(1);
    while let Some(arg) = args.next() {
        match arg.to_str() {
            Some("--box") => declared = args.next().context(USAGE)?.into(),
            _ if out.is_none() => out = Some(PathBuf::from(arg)),
            _ => bail!(USAGE),
        }
    }
    let out = out.unwrap_or_else(|| PathBuf::from(PIECES));
    hsm_kernel::reads::begin();
    let document = read(&declared)?;
    let b = Box::from_document(serde_json::from_slice(&document)?).with_context(|| declared.display().to_string())?;
    std::fs::create_dir_all(&out)?;
    let mut rows: Vec<Ref> = SHOWN
        .iter()
        .map(|(file, name)| Ref::stored(&Path::new(PIECES).join(format!("{file}.step.npz")), 0, name, Some(digits(wall_color()))))
        .collect();
    let parts = dock_parts(&b.pack.collet_plate)?;
    let bodies: Vec<Body> = parts.iter().map(|(name, color, solid)| Body { name, color: Some(*color), solid }).collect();
    rows.extend(Ref::made(&bodies)?);
    drop(bodies);
    drop(parts);
    physical_rows("enclosure", rows, &out)
}

/// The dock's purchased parts as installed: each station's tee on its run axis, and the two
/// stem elbows of its return, their stems cut back to the depth each plugs in to.
fn dock_parts(plate: &ColletPlate) -> Result<Vec<(String, [f64; 3], Solid)>> {
    let tee = hsm_kernel::import::bodies(&read(Path::new(TEE))?, TEE)?;
    let elbow = hsm_kernel::import::model(ELBOW)?;
    let mut parts = Vec::new();
    for station in dock::stations(plate) {
        let pose = Affine::from_columns(-V3::X, -V3::Y, V3::Z, at(station.centre));
        for (i, body) in tee.iter().enumerate() {
            parts.push((numbered(&station.tee, i, tee.len()), tee_color(), body.solid.transformed(&pose)));
        }
        for e in &station.elbows {
            let x = -V3::Z;
            let z = v3(e.socket[1], -e.socket[0], 0.);
            let pose = Affine::from_columns(x, z.cross(x), z, at(e.crossing));
            let keep = dock::stem_elbow::hub_back_reach() + e.stem;
            let cutter = Solid::cuboid(v3(-keep - 40., -20., -20.), v3(-keep, 20., 20.));
            for (i, body) in elbow.iter().enumerate() {
                // The collet clears the cutter, so only the stem's body is cut back.
                let solid = if body.solid.bounds().min.x < -keep { body.solid.cut(&cutter)? } else { body.solid.clone() };
                parts.push((numbered(&e.name, i, elbow.len()), elbow_color(), solid.transformed(&pose)));
            }
        }
    }
    Ok(parts)
}

fn read(path: &Path) -> Result<Vec<u8>> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(path, &bytes);
    Ok(bytes)
}

fn at(p: [f64; 3]) -> V3 {
    v3(p[0], p[1], p[2])
}

/// `name`, numbered from one among `count` bodies of the same part.
fn numbered(name: &str, i: usize, count: usize) -> String {
    if count > 1 { format!("{name}/{}", i + 1) } else { name.to_owned() }
}
