//! The faucet plate's chain, which `faucet-plate` runs for either style from the checkout's
//! meshes, the standing finish selection and the plate's own selections to the print-only archive.
//! Both styles lay the same tip, display cover and lever beside their own base and mounting plate.
use crate::{faucet_contact, slice, stretch_cooling, trial_archive};
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::fs;
use std::path::{Path, PathBuf};

/// The plate's own selections.
pub const SELECTION: &str = "tools/hsm/print-prep/faucet-plate.json";

/// A part of a plate: its name there and its mesh in the checkout.
#[derive(Clone, Copy)]
pub struct Part {
    pub name: &'static str,
    pub stl: &'static str,
}

pub const TIP: Part = Part { name: "faucet-shell-tip", stl: "hardware/printed-parts/faucet/faucet-shell/faucet-shell-tip.stl" };
pub const COVER: Part =
    Part { name: "faucet-display-cover", stl: "hardware/printed-parts/faucet/faucet-display-cover/faucet-display-cover.stl" };
pub const LEVER: Part = Part { name: "lever-replica", stl: "hardware/printed-parts/faucet/lever-replica/lever-replica-side-down.stl" };

/// The names the base, tip, cover, mounting plate and lever carry in the parent recipe whose
/// object settings and foot regions the preparer copies onto either style's parts.
pub const PARENT: [&str; 5] = ["industrial-shell-base", "faucet-shell-tip", "sculpted-display-cover", "industrial-above-counter-plate", "lever-replica"];

/// A faucet style's plate: its own base and mounting plate beside the shared parts.
pub struct Style {
    pub name: &'static str,
    /// The style as a plate's title names it.
    pub title: &'static str,
    pub base: Part,
    pub plate: Part,
}

pub const STYLES: [Style; 2] = [
    Style {
        name: "sculpted",
        title: "Sculpted",
        base: Part { name: "faucet-shell-base", stl: "hardware/printed-parts/faucet/faucet-shell/faucet-shell-base.stl" },
        plate: Part { name: "above-counter-plate", stl: "hardware/printed-parts/faucet/above-counter-plate/above-counter-plate.stl" },
    },
    Style {
        name: "industrial",
        title: "Industrial",
        base: Part { name: "industrial-shell-base", stl: "hardware/printed-parts/faucet/industrial/industrial-shell-base.stl" },
        plate: Part { name: "industrial-above-counter-plate", stl: "hardware/printed-parts/faucet/industrial/industrial-above-counter-plate.stl" },
    },
];

pub fn style(name: &str) -> Result<&'static Style> {
    STYLES.iter().find(|s| s.name == name).with_context(|| format!("no style {name}; sculpted or industrial"))
}

impl Style {
    /// The plate's parts in the order their object ids follow: base, tip, cover, plate, lever.
    pub fn parts(&self) -> [Part; 5] {
        [self.base, TIP, COVER, self.plate, LEVER]
    }

    /// `finish`, a selection written for the Sculpted plate, with every entry that names the
    /// Sculpted base or mounting plate naming this style's.
    pub fn finish(&self, finish: &Value) -> Value {
        let [base, plate] = [STYLES[0].base.name, STYLES[0].plate.name];
        match finish {
            Value::String(name) if name == base => json!(self.base.name),
            Value::String(name) if name == plate => json!(self.plate.name),
            Value::Array(items) => Value::Array(items.iter().map(|v| self.finish(v)).collect()),
            Value::Object(entries) => Value::Object(entries.iter().map(|(k, v)| (k.clone(), self.finish(v))).collect()),
            other => other.clone(),
        }
    }
}
/// The tip's pose about X on the plate, as the preparer's `--tip-rotation` takes it.
pub const TIP_ROTATION_DEGREES: f64 = -90.0;
/// The gap between the donor tip's support tops and the courses they carry.
pub const DONOR_SUPPORT_TOP_GAP_MM: f64 = 0.24;

/// The show laps' descent lift the plate's selections give, or none.
pub fn lift_share(plate: &Value) -> f64 {
    plate["descent_lift"]["share"].as_f64().unwrap_or(0.0)
}

pub fn selection(root: &Path) -> Result<Value> {
    let path = root.join(SELECTION);
    serde_json::from_slice(&fs::read(&path)?).with_context(|| format!("reading {}", path.display()))
}

/// Slices `project` into `directory` and runs the standing slice path's G-code stages over the
/// slice in their standing order, bridge-foundation cooling and then tip-end cooling. `report` is
/// the project's print report. Given `plain`, the same plate with other settings, the tip's layers
/// in the tip-end cooling zone come from its slice before the stages run. The stages' receipts
/// are returned.
pub fn slice_with_cooling(project: &Path, report: &Value, directory: &Path, plain: Option<&Path>) -> Result<Value> {
    let stretch = faucet_contact::recorded_tip_end_stretch(report, &report["selected_finish"]["tip_end_cooling"])?;
    let splice = match plain {
        None => {
            slice_raw(project, directory)?;
            Value::Null
        }
        Some(plain) => {
            let (level, other) = (directory.join("level"), directory.join("plain"));
            let level_archive = slice_raw(project, &level)?;
            let plain_archive = slice_raw(plain, &other)?;
            let probe = level.join("tip-end-zone.gcode");
            let from = stretch_cooling::apply(&level.join("plate_1.gcode"), &probe, &stretch)?.z_mm[0];
            fs::remove_file(&probe)?;
            let stem = project.file_stem().context("the project's name")?.to_string_lossy().to_string();
            trial_archive::splice_tip_layers(&level_archive, &plain_archive, from, directory, &stem, &json!({}))?
        }
    };
    let bridge = slice::apply_directory(directory, project)?;
    fs::create_dir_all(directory.join("mapped-slice"))?;
    let tip_end = faucet_contact::apply_stretch_cooling(project, directory, "tip-end-cooling", &stretch)?;
    Ok(json!({"tip_end_splice": splice, "bridge_foundation": bridge, "tip_end": tip_end}))
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
