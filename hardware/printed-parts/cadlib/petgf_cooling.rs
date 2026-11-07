//! petgf-cooling — the localized PET-GF cooling stage. Bambu Studio runs `petgf-cooling <gcode>` on
//! each sliced plate's G-code from the project's post-processing hook, which rewrites the G-code in
//! place when the stage changes it and leaves its reading beside it; the preparers run
//! `petgf-cooling --directory <slice dir> --project <project>` over an offline slice.

use anyhow::{Context, Result};
use hsm_print_prep::{cooling, slice};
use std::path::PathBuf;

fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    // petgf-cooling --directory <slice dir> --project <project.3mf>: the stage over a whole
    // offline slice, as the preparers run it after the command-line slicer.
    if args.first().map(String::as_str) == Some("--directory") {
        let directory = PathBuf::from(args.get(1).context("--directory needs a folder")?);
        let project = PathBuf::from(args.get(3).filter(|_| args.get(2).map(String::as_str) == Some("--project")).context("--project needs a project")?);
        let reports = slice::apply_directory(&directory, &project)?;
        println!("{}", serde_json::to_string_pretty(&reports)?);
        return Ok(());
    }
    let source = PathBuf::from(args.first().context("usage: petgf-cooling <gcode>")?);
    let output = PathBuf::from(format!("{}.cooling", source.display()));
    let reading = cooling::foundation(&source, &output, &slice::environment_settings())?;
    if reading["changed"].as_bool() == Some(true) {
        std::fs::rename(&output, &source)?;
    } else if output.exists() {
        std::fs::remove_file(&output)?;
    }
    std::fs::write(format!("{}.cooling.json", source.display()), serde_json::to_string_pretty(&reading)? + "\n")?;
    Ok(())
}
