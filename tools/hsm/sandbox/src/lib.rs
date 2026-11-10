//! What a throwaway concept needs besides the kernel: where it writes, the catalog's colours, the
//! models already in the tree, and the viewer's files. A concept is a file in `examples/`, and
//! README.md says how to run one.
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::import::Imported;
use hsm_kernel::{Body, Solid};
use std::path::{Path, PathBuf};

/// The output directory the concept was given, made if it is missing.
pub fn out() -> Result<PathBuf> {
    let Some(dir) = std::env::args_os().nth(1) else { bail!("usage: <concept> <output directory>") };
    let dir = PathBuf::from(dir);
    std::fs::create_dir_all(&dir)?;
    Ok(dir)
}

/// A colour of the materials catalog by its name, such as `M_PETGF_BLACK`, as the viewer's files
/// carry it: linear RGB at single precision, the way the parts in the tree are coloured.
pub fn material(name: &str) -> Result<[f64; 3]> {
    let catalog: serde_json::Value =
        serde_json::from_str(include_str!("../../shared-data/catalog/materials.json"))?;
    let color = catalog["colors"].get(name).with_context(|| format!("no colour {name} in the materials catalog"))?;
    let (channels, srgb): (Vec<f64>, bool) = match color["bytes"].as_array() {
        Some(bytes) => (bytes.iter().filter_map(|b| b.as_f64()).map(|b| b / 255.).collect(), true),
        None => {
            let args = color["args"].as_array().context("a colour's channels")?;
            let srgb = args.len() < 5 || args[4].as_bool().unwrap_or_else(|| args[4].as_f64().is_some_and(|n| n != 0.));
            (args.iter().take(3).filter_map(|c| c.as_f64()).collect(), srgb)
        }
    };
    ensure!(channels.len() == 3, "{name} does not hold three channels");
    Ok([0, 1, 2].map(|i| {
        let c = channels[i];
        let linear = if !srgb { c } else if c <= 0.04045 { c / 12.92 } else { ((c + 0.055) / 1.055).powf(2.4) };
        linear as f32 as f64
    }))
}

/// The bodies of a model in the tree, named by its path under `hardware/` as /3d names it, such as
/// `printed-parts/enclosure/enclosure/enclosure-front-top.step`: their fine geometry, names and
/// colours, from the `.step.npz` beside the STEP. `hsm_kernel::import::body` picks one by name.
pub fn part(path: &str) -> Result<Vec<Imported>> {
    let model = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../hardware").join(format!("{path}.npz"));
    ensure!(model.is_file(), "hardware/{path}.npz is not on this disk");
    hsm_kernel::import::model(&model)
}

/// `bodies`, each a name, a colour and a solid, as the viewer's files in `dir`: `<name>.step`,
/// `<name>.step.npz` and `<name>.step.mesh`. Prints the STEP's path for native rendering. `hsm_kernel::part::write_part` writes the same with an STL, for a concept to print.
pub fn show(dir: &Path, name: &str, bodies: &[(&str, [f64; 3], &Solid)]) -> Result<()> {
    let bodies: Vec<Body> = bodies.iter().map(|&(name, color, solid)| Body { name, color: Some(color), solid }).collect();
    hsm_kernel::part::write_shown(dir, name, &bodies)?;
    println!("{}", dir.join(format!("{name}.step")).display());
    Ok(())
}
