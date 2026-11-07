//! donor-hold-down-print-project — one face-down TPU donor hand pad, and optionally its offline
//! slice. Submits no printer job and is not part of the build.
//!
//!     donor-hold-down-print-project [--slice-output DIR]
//!
//! The recipe is the reviewed TPU liner job's, bound to Mark1's standard Z trim: the liner job's
//! untrimmed exception is local to that job. The pad lies broad hand face down, its conforming
//! upper-half donor cavity upward. A slice must keep the requested TPU material and process.

use anyhow::{bail, Context, Result};
use hsm_print_prep::json::Json;
use hsm_print_prep::profile::{relative, SETTINGS_MEMBER};
use hsm_print_prep::refresh::{self, Part};
use hsm_print_prep::{faucet, root};
use serde_json::{json, Value};
use std::io::Write;
use std::path::PathBuf;

const HERE: &str = "hardware/printed-parts/fixtures/tube-insertion/donor-hold-down";
const SETTINGS_SOURCE: &str = "hardware/printed-parts/fixtures/tube-insertion/prints/2026-10-12-tpu-liners-close-z000-mark1/2026-10-12-tube-insertion-liners-tpu85a-right06-z000-close-mark1.3mf";
const PROJECT: &str = "donor-hold-down-half-body-tpu85a-right06-z018-mark1.3mf";
const IDENTITY: &str = "Bambu Lab H2C 0.6 Standard +0.18 Z trim";
const Z_TRIM: f64 = 0.18;
/// The model and every emitted bead keep this far inside the plate's edge.
const PLATE_BORDER: f64 = 20.0;

fn main() -> Result<()> {
    let root = root();
    let here = root.join(HERE);
    let ready = here.join("ready");
    let mut slice_output = None::<PathBuf>;
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--slice-output" => slice_output = Some(PathBuf::from(args.next().context("--slice-output needs a directory")?)),
            _ => bail!("unknown argument {arg}"),
        }
    }
    let source = root.join(SETTINGS_SOURCE);
    let reviewed = faucet::read_json(&source.with_extension("readiness.json"))?;
    let source_sha = faucet::file_sha(&source)?;
    if reviewed["project_sha256"].as_str() != Some(source_sha.as_str()) {
        bail!("the TPU recipe source differs from its reviewed project");
    }
    let mut members = faucet::members(&source)?;
    let mut settings = Json::parse(std::str::from_utf8(&members[SETTINGS_MEMBER])?)?;
    settings.set("print_compatible_printers", Json::List(vec![Json::Text(IDENTITY.into())]));
    let requested = settings.to_value();
    members.insert(SETTINGS_MEMBER.into(), (settings.dumps() + "\n").into_bytes());
    let profile = root.join(".cache/donor-hold-down-settings.3mf");
    std::fs::create_dir_all(profile.parent().unwrap())?;
    {
        let mut archive = zip::ZipWriter::new(std::fs::File::create(&profile)?);
        for (name, data) in &members {
            archive.start_file(name.as_str(), hsm_print_prep::project::options())?;
            archive.write_all(data)?;
        }
        archive.finish()?;
    }
    let part = Part::new("TPU upper-half donor cover", here.join("donor-hold-down-print.stl"), 0.0);
    let mut r = refresh::refresh(&root, &profile, &[part], &[[0.0, 0.0]], "Touch-Flo TPU half-body hold-down cover", Some(Z_TRIM), PLATE_BORDER)?;
    let spec = json!({"printer": "Mark1 (H2C)", "nozzle_mapping": "Right fixed 0.6 mm; black TPU 85A external spool 255", "z_trim_mm": Z_TRIM});
    for (k, v) in [("status", json!("offline project preparation; no printer submission")), ("printer_submission", json!(false)),
                   ("intended_printer", spec["printer"].clone()), ("material", json!("Black TPU 85A")), ("nozzle_mapping", spec["nozzle_mapping"].clone()),
                   ("print_pose", json!("Broad flat hand face down; conforming upper-half donor cavity upward")),
                   ("z_trim_basis", json!("Mark1 standard trim; the liner job's untrimmed exception is local to that job")),
                   ("original_settings_source", json!(SETTINGS_SOURCE)), ("original_settings_source_sha256", json!(source_sha)),
                   ("process_compatibility_binding", json!(IDENTITY))] {
        r.extra.insert(k.into(), v);
    }
    let project = ready.join(PROJECT);
    let report = r.write(&root, &project)?;
    println!("{}", relative(&project, &root));
    let Some(directory) = slice_output else { return Ok(()) };
    // Bambu Studio's slice is one of the Mac's heavy runs.
    hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
    std::fs::create_dir_all(directory.parent().unwrap_or(&directory))?;
    let directory = std::path::absolute(&directory)?;
    let mut record = refresh::slice_bench_plate(&project, &report, &spec, &directory, Some(&ready), PLATE_BORDER)?;
    let archive = ready.join(record["archive"].as_str().unwrap_or(""));
    let native: Value = {
        let mut zip = zip::ZipArchive::new(std::fs::File::open(&archive)?)?;
        let mut text = String::new();
        std::io::Read::read_to_string(&mut zip.by_name(SETTINGS_MEMBER)?, &mut text)?;
        serde_json::from_str(&text)?
    };
    let keys = ["filament_type", "filament_settings_id", "curr_bed_type", "layer_height", "initial_layer_print_height", "wall_loops",
                "sparse_infill_density", "enable_support", "filament_nozzle_map"];
    let changed: Vec<&str> = keys.iter().copied().filter(|k| native.get(*k) != requested.get(*k)).collect();
    if !changed.is_empty() {
        bail!("the native slice changed the requested TPU recipe: {changed:?}");
    }
    record["native_material_process"] = json!(keys.iter().map(|k| (k.to_string(), native.get(*k).cloned().unwrap_or(Value::Null))).collect::<serde_json::Map<_, _>>());
    std::fs::write(project.with_extension("readiness.json"), serde_json::to_string_pretty(&record)? + "\n")?;
    println!("{}", json!({"archive": record["archive"], "layers": record["layers"], "estimated_seconds": record["estimated_seconds"],
        "estimated_filament_g": record["estimated_filament_g"], "support_generated": record["support_generated"], "bead_margin_mm": record["bead_margin_mm"]}));
    Ok(())
}
