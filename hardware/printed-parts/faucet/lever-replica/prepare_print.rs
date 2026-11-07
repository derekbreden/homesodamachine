//! lever-print-project — one comparison lever from the shared PET-GF settings, and optionally
//! its offline slice. Never contacts a printer.
//!
//!     lever-print-project [--variant black-h2c|white-mark2] [--slice-output DIR]
//!
//! One comparison lever per machine: the filament colour is physical, and the Z trim is the
//! printer's. The lever lies on its local CAD +X side, its broad show face vertical. Derek's
//! physical acceptance travels with the record only while the printed mesh is the one accepted.

use anyhow::{bail, Context, Result};
use hsm_print_prep::profile::relative;
use hsm_print_prep::refresh::{self, Part};
use hsm_print_prep::{audit, root, sha256_hex, slice};
use serde_json::{json, Value};
use std::path::{Path, PathBuf};

const HERE: &str = "hardware/printed-parts/faucet/lever-replica";
const PROFILE: &str = "hardware/printed-parts/petgf.3mf";

struct Variant {
    name: &'static str,
    project: &'static str,
    archive: &'static str,
    z_trim: f64,
    title: &'static str,
}

const VARIANTS: [Variant; 2] = [
    Variant { name: "black-h2c", project: "lever-replica-petgf.3mf", archive: "lever-black-petgf-z018-h2c.gcode.3mf", z_trim: 0.18,
              title: "Lever comparison black PET-GF H2C" },
    Variant { name: "white-mark2", project: "lever-replica-petgf-white.3mf", archive: "lever-white-petgf-z004-mark2.gcode.3mf", z_trim: 0.04,
              title: "Lever comparison white PET-GF Mark2" },
];

fn file_sha(path: &Path) -> Result<String> {
    Ok(sha256_hex(&std::fs::read(path).with_context(|| format!("reading {}", path.display()))?))
}

/// Derek's physical observation of the printed lever, while the mesh is the one he accepted.
fn for_printed_model(here: &Path, stl_sha256: &str) -> Result<Value> {
    let record: Value = serde_json::from_slice(&std::fs::read(here.join("physical-acceptance.json"))?)?;
    let matches = record["printed_stl_sha256"].as_str() == Some(stl_sha256);
    let unconfirmed = json!("unconfirmed for this mesh");
    Ok(json!({"record": "physical-acceptance.json", "accepted_job_id": record["job_id"], "observed_date": record["observed_date"],
              "authority": record["authority"], "scope": record["scope"], "accepted_stl_sha256": record["printed_stl_sha256"],
              "current_stl_sha256": stl_sha256, "matches_accepted_geometry": matches,
              "physical_fit": if matches { record["physical_fit"].clone() } else { unconfirmed.clone() },
              "functional_operation": if matches { record["functional_operation"].clone() } else { unconfirmed },
              "quantified_strength": record["quantified_strength"], "quantified_endurance": record["quantified_endurance"]}))
}

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
    let spec = VARIANTS.iter().find(|v| v.name == variant).with_context(|| format!("no variant {variant}; black-h2c or white-mark2"))?;
    let project = here.join(spec.project);
    let stl = here.join("lever-replica-side-down.stl");
    let mut r = refresh::refresh(&root, &root.join(PROFILE), &[Part::new("lever-replica", stl.clone(), 0.0)], &[[0.0, 0.0]], spec.title, Some(spec.z_trim), 20.0)?;
    let acceptance = for_printed_model(&here, &r.rows[0].stl_sha256)?;
    for (k, v) in [("status", json!("offline project preparation; submissions are recorded in print-jobs.json")),
                   ("physical_acceptance", acceptance.clone()), ("pose", json!("local CAD +X side on bed; broad show face vertical")),
                   ("variant", json!(variant))] {
        r.extra.insert(k.into(), v);
    }
    let report = r.write(&root, &project)?;
    println!("{}", project.display());
    let Some(directory) = slice_output else { return Ok(()) };
    if directory.exists() && std::fs::read_dir(&directory)?.next().is_some() {
        bail!("use an empty slice directory");
    }
    // Bambu Studio's slice is one of the Mac's heavy runs.
    hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
    std::fs::create_dir_all(&directory)?;
    let directory = directory.canonicalize()?;
    let cli = slice::cli_project(&project, &directory)?;
    let log = std::fs::File::create(directory.join("bambu-cli.log"))?;
    let status = std::process::Command::new(slice::SLICER).args(["--slice", "0", "--arrange", "0", "--orient", "0", "--export-3mf", spec.archive, "--outputdir"])
        .arg(&directory).arg(&cli).stdout(log.try_clone()?).stderr(log).status()?;
    if !status.success() {
        bail!("offline slice failed; {}", directory.join("bambu-cli.log").display());
    }
    slice::apply_directory(&directory, &project)?;
    let result: Value = serde_json::from_slice(&std::fs::read(directory.join("result.json"))?)?;
    if result["return_code"].as_i64() != Some(0) {
        bail!("{}", result["error_string"]);
    }
    let gcode = std::fs::read(directory.join("plate_1.gcode"))?;
    let row = &report["parts"][0];
    let build: Vec<f64> = row["build_transform"].as_array().into_iter().flatten().filter_map(Value::as_f64).collect();
    let mut cad = audit::inverse(&build.clone().try_into().map_err(|_| anyhow::anyhow!("build transform"))?).context("the lever's transform is singular")?;
    for k in 0..3 {
        cad[9 + k] += row["source_center_mm"][k].as_f64().unwrap_or(0.0);
    }
    let options = audit::Options { piece: "lever-replica".into(), object: None, include_unlabelled: true, cad_transform: Some(cad), bed_reseat: None,
        inputs: json!({"gcode": "plate_1.gcode", "gcode_sha256": sha256_hex(&gcode), "model": relative(&stl, &root), "model_sha256": file_sha(&stl)?,
                       "profile": relative(&project, &root), "profile_sha256": file_sha(&project)?}) };
    let mut support = audit::audit(&gcode, &options);
    support["source_frame_note"] = json!("CAD coordinates in this audit are the side-down STL print frame.");
    let support_path = project.with_extension("support-audit.json");
    std::fs::write(&support_path, serde_json::to_string_pretty(&support)? + "\n")?;
    let archive = here.join(spec.archive);
    std::fs::copy(directory.join(spec.archive), &archive)?;
    let mut gcodes = serde_json::Map::new();
    for entry in std::fs::read_dir(&directory)? {
        let path = entry?.path();
        if path.extension().and_then(|e| e.to_str()) == Some("gcode") {
            gcodes.insert(path.file_name().unwrap().to_string_lossy().to_string(), json!(file_sha(&path)?));
        }
    }
    let readiness = json!({"status": "offline slice complete; physical observations are recorded separately",
        "physical_acceptance": acceptance, "project_sha256": report["project_sha256"], "printer_submission": false,
        "support_summary": support["summary"], "support_audit_sha256": file_sha(&support_path)?, "slice_result": result,
        "archive": spec.archive, "archive_sha256": file_sha(&archive)?, "gcode": gcodes});
    std::fs::write(project.with_extension("readiness.json"), serde_json::to_string_pretty(&readiness)? + "\n")?;
    println!("{}", serde_json::to_string_pretty(&json!({"slice": directory.display().to_string(), "plates": result["sliced_plates"]}))?);
    Ok(())
}
