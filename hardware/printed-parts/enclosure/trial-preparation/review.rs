//! enclosure-print-review — reads a preparation back against its record.
//!
//!     enclosure-print-review <preparation directory> [--project-only] [--no-audit] [--unbacked]
//!
//! `--project-only` reads the written project back: embedded meshes against their STLs, part
//! and modifier counts, painted facets and layer ranges. Without it the sliced archive is read
//! too, as `hsm_print_prep::review` describes, and `review.json` is written beside the record.
//! `--no-audit` skips the support topology; `--unbacked` reads adjacent-layer road shadows
//! through every fine band. It exits non-zero when a check fails.

use anyhow::{bail, Result};
use std::path::PathBuf;

fn main() -> Result<()> {
    let root = hsm_print_prep::root();
    let (mut directory, mut project_only, mut audit, mut unbacked) = (None, false, true, false);
    for arg in std::env::args().skip(1) {
        match arg.as_str() {
            "--project-only" => project_only = true,
            "--no-audit" => audit = false,
            "--unbacked" => unbacked = true,
            _ if directory.is_none() && !arg.starts_with("--") => directory = Some(PathBuf::from(arg)),
            _ => bail!("usage: enclosure-print-review <preparation directory> [--project-only] [--no-audit] [--unbacked]"),
        }
    }
    let Some(directory) = directory else { bail!("usage: enclosure-print-review <preparation directory> [--project-only] [--no-audit] [--unbacked]") };
    let result = if project_only {
        let result = hsm_print_prep::review::check_project(&root, &directory)?;
        println!("{}", serde_json::to_string_pretty(&result)?);
        result
    } else {
        // Reading a sliced archive is one of the Mac's heavy runs.
        hsm_run_slots::process_enter(&hsm_run_slots::native_key())?;
        hsm_print_prep::review::review(&root, &directory, audit, unbacked)?
    };
    if result["pass"] != serde_json::json!(true) {
        std::process::exit(1);
    }
    Ok(())
}
