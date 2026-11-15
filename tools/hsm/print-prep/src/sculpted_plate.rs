//! The Sculpted faucet plate's chain, which `sculpted-plate` runs from the checkout's meshes, the
//! standing finish selection and the plate's own selections to the print-only archive.
use crate::{faucet_contact, slice};
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::fs;
use std::path::{Path, PathBuf};

/// The plate's own selections.
pub const SELECTION: &str = "tools/hsm/print-prep/sculpted-plate.json";
/// The tip's pose about X on the plate, as the preparer's `--tip-rotation` takes it.
pub const TIP_ROTATION_DEGREES: f64 = -90.0;
/// The gap between the donor tip's support tops and the courses they carry.
pub const DONOR_SUPPORT_TOP_GAP_MM: f64 = 0.24;

pub fn selection(root: &Path) -> Result<Value> {
    let path = root.join(SELECTION);
    serde_json::from_slice(&fs::read(&path)?).with_context(|| format!("reading {}", path.display()))
}

/// Slices `project` into `directory` and runs the standing slice path's G-code stages over the
/// slice in their standing order, bridge-foundation cooling and then tip-end cooling. `report` is
/// the project's print report. The stages' receipts are returned.
pub fn slice_with_cooling(project: &Path, report: &Value, directory: &Path) -> Result<Value> {
    slice_raw(project, directory)?;
    let bridge = slice::apply_directory(directory, project)?;
    let stretch = faucet_contact::recorded_tip_end_stretch(report, &report["selected_finish"]["tip_end_cooling"])?;
    fs::create_dir_all(directory.join("mapped-slice"))?;
    let tip_end = faucet_contact::apply_stretch_cooling(project, directory, "tip-end-cooling", &stretch)?;
    Ok(json!({"bridge_foundation": bridge, "tip_end": tip_end}))
}

/// The slicer's own slice of `project` in `directory`, its archive named for the project and its
/// plate's G-code beside it.
fn slice_raw(project: &Path, directory: &Path) -> Result<PathBuf> {
    slice::run(Path::new(slice::SLICER), project, directory)?;
    let stem = project.file_stem().context("the project's name")?.to_string_lossy().to_string();
    let archive = directory.join(format!("{stem}.gcode.3mf"));
    fs::write(directory.join("plate_1.gcode"), crate::gcode::plate_gcode(&archive)?)?;
    Ok(archive)
}
