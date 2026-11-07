//! tube-miter-box-print-project — the tube miter box from the shared PET-GF settings, offline.
//!
//!     tube-miter-box-print-project [--variant black-h2c|black-mark2] [--slice-output DIR]
//!
//! One project per machine: the shared settings and the Z trim are what differ. With
//! `--slice-output`, Bambu Studio slices the project into that empty directory and the
//! submittable archive lands beside the project. The box prints on its bottom face, troughs open
//! upward, with no support.

use anyhow::{bail, Context, Result};
use hsm_print_prep::refresh::{self, Part};
use hsm_print_prep::{root, sha256_hex};
use serde_json::json;
use std::path::PathBuf;

const HERE: &str = "hardware/printed-parts/fixtures/tube-miter-box";
const PROFILE: &str = "hardware/printed-parts/petgf.3mf";

/// Name, project, archive, Z trim and title per machine.
const VARIANTS: [(&str, &str, &str, f64, &str); 2] = [
    ("black-h2c", "tube-miter-box-petgf.3mf", "tube-miter-box-petgf-z018-h2c.gcode.3mf", 0.18, "Tube miter box black PET-GF H2C"),
    ("black-mark2", "tube-miter-box-petgf-mark2.3mf", "tube-miter-box-petgf-z004-mark2.gcode.3mf", 0.04, "Tube miter box black PET-GF Mark2"),
];

fn main() -> Result<()> {
    let root = root();
    let here = root.join(HERE);
    let (mut variant, mut slice_output) = ("black-h2c".to_string(), None::<PathBuf>);
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        let mut value = || args.next().with_context(|| format!("{arg} needs a value"));
        match arg.as_str() {
            "--variant" => variant = value()?,
            "--slice-output" => slice_output = Some(PathBuf::from(value()?)),
            _ => bail!("unknown argument {arg}"),
        }
    }
    let &(_, project, archive, z_trim, title) = VARIANTS.iter().find(|v| v.0 == variant).with_context(|| format!("no variant {variant}"))?;
    let (project, archive, stl) = (here.join(project), here.join(archive), here.join("tube-miter-box.stl"));
    let mut r = refresh::refresh(&root, &root.join(PROFILE), &[Part::new("tube-miter-box", stl.clone(), 0.0)], &[[0.0, 0.0]], title,
                                 Some(z_trim), 20.0)?;
    for (k, v) in [("status", json!("offline project preparation; a submission is recorded in print-jobs.json")),
                   ("pose", json!("bottom face on the bed, troughs open upward; no support")), ("variant", json!(variant))] {
        r.extra.insert(k.into(), v);
    }
    let report = r.write(&root, &project)?;
    println!("{}", project.display());
    let Some(directory) = slice_output else { return Ok(()) };
    // Bambu Studio's slice is one of the Mac's heavy runs.
    hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
    let name = archive.file_name().unwrap().to_string_lossy().to_string();
    let (result, gcode, sliced) = refresh::slice_cli(&project, &directory, &name)?;
    let trims = refresh::trim_commands(&gcode);
    if trims != refresh::expected_trims(z_trim) {
        bail!("plate trim commands {trims:?} are not the requested +{z_trim:.2}");
    }
    let features = refresh::features(&gcode);
    if features.iter().any(|f| f.contains("Support")) {
        bail!("the slice carries support: {features:?}");
    }
    std::fs::copy(&sliced, &archive)?;
    let plate = &result["sliced_plates"][0];
    let readiness = json!({
        "status": "offline slice complete; a submission is recorded in print-jobs.json", "printer_submission": false,
        "slice_result": result, "features": features, "layers": refresh::total_layers(&gcode),
        "estimated_seconds": plate["total_predication"],
        "estimated_filament_g": plate["filaments"].as_array().into_iter().flatten().filter_map(|f| f["total_used_g"].as_f64()).sum::<f64>(),
        "plate_trim_commands_mm": trims, "archive": name, "archive_sha256": sha256_hex(&std::fs::read(&archive)?),
        "gcode_sha256": sha256_hex(&gcode), "project_sha256": report["project_sha256"],
        "source_stl_sha256": sha256_hex(&std::fs::read(&stl)?), "source_profile_sha256": sha256_hex(&std::fs::read(root.join(PROFILE))?),
    });
    std::fs::write(project.with_extension("readiness.json"), serde_json::to_string_pretty(&readiness)? + "\n")?;
    println!("{}", serde_json::to_string_pretty(&json!({"archive": name, "layers": readiness["layers"], "estimated_seconds": readiness["estimated_seconds"],
        "estimated_filament_g": readiness["estimated_filament_g"], "features": readiness["features"], "plate_trim_commands_mm": readiness["plate_trim_commands_mm"]}))?);
    Ok(())
}
