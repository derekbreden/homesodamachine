//! The faucet and its umbilical as the bench bags them, from the display on the tip down to the
//! four square-cut tails and their collars, on the kernel: the Sculpted faucet's assembly and the
//! Industrial one's, with its shell base, plate and gasket under the head both styles share.
pub mod bodies;
pub mod cuts;
pub mod legs;
pub mod metrics;
pub mod ribbon;

use anyhow::{Context, Result};
use hsm_build_data::{payload, surfaces};
use hsm_kernel::Body;
use hsm_kernel::part::write_shown;
use hsm_kernel::reads;
use std::collections::BTreeMap;
use std::path::Path;

/// Which faucet the assembly stands.
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Variant {
    Sculpted,
    Industrial,
}

impl Variant {
    /// The assembly's name, which names its files.
    pub fn name(self) -> &'static str {
        match self {
            Variant::Sculpted => "faucet-assembly",
            Variant::Industrial => "faucet-industrial-assembly",
        }
    }
}

/// The tip both faucets share, under `printed-parts/faucet/`.
const TIP_STEP: &str = "faucet-shell/faucet-shell-tip.step";

/// The printed pieces whose own surfaces the payload draws, each by the body that stands it in
/// place and its STEP under `printed-parts/faucet/`: a piece's surface keeps every triangle it
/// prints with, where the body the assembly writes is simplified.
fn printed_surfaces(variant: Variant) -> [(&'static str, &'static str); 6] {
    let (base, plate, gasket) = match variant {
        Variant::Sculpted => (
            "faucet-shell/faucet-shell-base.step",
            "above-counter-plate/above-counter-plate.step",
            "above-counter-gasket/above-counter-gasket.step",
        ),
        Variant::Industrial => (
            "industrial/industrial-shell-base.step",
            "industrial/industrial-above-counter-plate.step",
            "industrial/industrial-above-counter-gasket.step",
        ),
    };
    [
        ("lever", "lever-replica/lever-replica.step"),
        ("shell_base", base),
        ("shell_tip", TIP_STEP),
        ("above_counter_plate", plate),
        ("above_counter_gasket", gasket),
        ("umbilical-organizer", "umbilical-organizer/umbilical-organizer.step"),
    ]
}

/// The surface a printed piece's payload holds, read beside its STEP and cut from it.
fn surface(step: &str) -> Result<payload::Mesh> {
    let digest = payload::digest(step).with_context(|| format!("reading {step}"))?;
    reads::digest(Path::new(step), &digest);
    let beside = format!("{step}.mesh");
    let bytes = std::fs::read(&beside).with_context(|| format!("reading {beside}"))?;
    reads::read(Path::new(&beside), &bytes);
    let piece = payload::decode(&bytes)?;
    anyhow::ensure!(piece.src.as_deref() == Some(digest.as_str()), "{beside} was not cut from the {step} beside it");
    let mut meshes = piece.meshes.into_iter();
    match (meshes.next(), meshes.next()) {
        (Some(mesh), None) => Ok(mesh),
        _ => anyhow::bail!("{beside} holds other than the piece's one surface"),
    }
}

/// Carry each printed piece's own surface into the payload at `mesh`, standing it where the
/// assembly stands the piece.
fn graft(mesh: &Path, variant: Variant) -> Result<()> {
    let mut skins = BTreeMap::new();
    for (body, step) in printed_surfaces(variant) {
        skins.insert(body.to_owned(), surface(&format!("hardware/printed-parts/faucet/{step}"))?);
    }
    let names: Vec<String> = skins.keys().cloned().collect();
    let result = surfaces::graft(mesh, &skins, false, |name, _| Ok(names.iter().find(|n| *n == name).cloned()), None)?;
    for row in result["moved"].as_array().into_iter().flatten() {
        eprintln!("{}: {} keeps its own surface; no placement recovered across {} mm", variant.name(), row["name"], row["drift_mm"]);
    }
    Ok(())
}

/// Write the assembly's STEP, model file and payload, each printed piece drawn with its own
/// surface.
pub fn run(variant: Variant) -> Result<()> {
    let out = hsm_print_payload::printed::out_dir("hardware/faucet-layout")?;
    let shown = bodies::bodies(variant)?;
    let rows: Vec<Body> = shown.iter().map(|s| Body { name: &s.name, color: Some(s.color), solid: &s.solid }).collect();
    let name = variant.name();
    println!("{}", write_shown(&out, name, &rows)?);
    graft(&out.join(format!("{name}.step.mesh")), variant)
}
