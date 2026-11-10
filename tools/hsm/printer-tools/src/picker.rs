//! Run the native visible-filament selector against synthetic images without application input.
use anyhow::{bail, Context, Result};
use std::{fs, path::Path, process::Command};
pub fn run(root: &Path) -> Result<()> {
    let directory = root.join(".cache/runs/python-retirement-20261110/printer-picker");
    fs::create_dir_all(&directory)?;
    let source = fs::read_to_string(root.join("tools/bambu-ui/main.swift"))?;
    let definitions = source
        .split_once("while let line = readLine()")
        .context("Native input process has no command loop")?
        .0;
    let harness = directory.join("main.swift");
    let binary = directory.join("picker-check");
    fs::write(
        &harness,
        format!("{definitions}\n{}", include_str!("picker-fixtures.swift")),
    )?;
    let status = Command::new(root.join("tools/run"))
        .arg("--")
        .args(["swiftc", "-O"])
        .arg(&harness)
        .arg("-o")
        .arg(&binary)
        .status()?;
    if !status.success() {
        bail!("Compile native OCR fixtures: {status}")
    }
    let output = Command::new(root.join("tools/run"))
        .arg("--")
        .arg(&binary)
        .output()?;
    if !output.status.success() {
        bail!(
            "Native OCR fixtures failed:\n{}\n{}",
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        )
    }
    let value: serde_json::Value = serde_json::from_slice(&output.stdout)?;
    let record = root.join(".cache/runs/python-retirement-20261110/printer-picker.json");
    fs::write(
        &record,
        format!("{}\n", serde_json::to_string_pretty(&value)?),
    )?;
    fs::remove_dir_all(directory)?;
    println!("{}", serde_json::to_string_pretty(&value)?);
    Ok(())
}
