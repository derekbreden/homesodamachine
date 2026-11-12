//! Native app reviews run Swift checks or collect the study app's own simulator renders.
use crate::{
    Temporary, execute, flag, option, output, read_json, text_output, validate_args, write_json,
};
use anyhow::{Context, Result, ensure};
use serde_json::Value;
use std::{
    fs,
    path::Path,
    process::Command,
    thread,
    time::{Duration, Instant},
};

pub fn checks(root: &Path, args: &[String]) -> Result<()> {
    ensure!(args.is_empty(), "ios-checks takes no arguments");
    hsm_run_slots::process_enter("ios-experience-checks")?;
    let checks = root.join("ios/SodaMachine/Checks");
    let core = root.join("ios/SodaMachine/SodaMachine/Core");
    let temporary = Temporary::new("soda-experience")?;
    let executable = temporary.0.join("experience-checks");
    let mut compiler = Command::new("swiftc");
    compiler.args(["-parse-as-library", "-default-isolation", "MainActor"]);
    for name in [
        "Navigation",
        "EditSessions",
        "SettingsSync",
        "MixChanges",
        "TrustState",
        "Management",
        "MachineModel",
        "Firmware",
        "MachineHistory",
    ] {
        compiler.arg(core.join(format!("{name}.swift")));
    }
    for name in [
        "Navigation",
        "Firmware",
        "SettingsSync",
        "Mix",
        "Trust",
        "History",
        "Experience",
    ] {
        compiler.arg(checks.join(format!("{name}Checks.swift")));
    }
    execute(compiler.arg("-o").arg(&executable))?;
    execute(&mut Command::new(executable))
}

pub fn capture(root: &Path, args: &[String]) -> Result<()> {
    ensure!(
        validate_args(args, &["--quick"], &["--routes"])?.is_empty(),
        "ios-capture accepts --quick and --routes ROUTES"
    );
    hsm_run_slots::process_enter("ios-study-capture")?;
    let here = root.join("ios/AdaptiveStudy");
    let bundle = "com.derekbreden.SodaMachineStudy";
    let name = "Soda layout study";
    let devices: Value = serde_json::from_slice(
        &output(Command::new("xcrun").args(["simctl", "list", "devices", "available", "-j"]))?
            .stdout,
    )?;
    let groups = devices["devices"]
        .as_object()
        .context("simctl returned no device groups")?;
    let device = groups
        .values()
        .filter_map(Value::as_array)
        .flatten()
        .find(|v| v["name"] == name);
    let identifier = match device {
        Some(device) => device["udid"]
            .as_str()
            .context("study simulator has no udid")?
            .to_owned(),
        None => text_output(Command::new("xcrun").args([
            "simctl",
            "create",
            name,
            "com.apple.CoreSimulator.SimDeviceType.iPhone-16-Pro",
            "com.apple.CoreSimulator.SimRuntime.iOS-18-5",
        ]))?,
    };
    execute(Command::new("xcrun").args(["simctl", "bootstatus", &identifier, "-b"]))?;
    execute(
        Command::new("xcodegen")
            .args(["generate", "--spec"])
            .arg(here.join("project.yml")),
    )?;
    let build = std::env::temp_dir().join("hsm-adaptive-study-build");
    execute(
        Command::new("xcodebuild")
            .arg("-project")
            .arg(here.join("SodaMachineStudy.xcodeproj"))
            .args([
                "-scheme",
                "SodaMachineStudy",
                "-destination",
                &format!("platform=iOS Simulator,id={identifier}"),
                "-configuration",
                "Debug",
                "-derivedDataPath",
            ])
            .arg(&build)
            .args(["build", "CODE_SIGNING_ALLOWED=NO", "-quiet"]),
    )?;
    let _ = Command::new("xcrun")
        .args(["simctl", "terminate", &identifier, bundle])
        .output();
    execute(
        Command::new("xcrun")
            .args(["simctl", "install", &identifier])
            .arg(build.join("Build/Products/Debug-iphonesimulator/SodaMachineStudy.app")),
    )?;
    let data = text_output(Command::new("xcrun").args([
        "simctl",
        "get_app_container",
        &identifier,
        bundle,
        "data",
    ]))?;
    let source = Path::new(&data).join("Documents/renders");
    if source.exists() {
        fs::remove_dir_all(&source)?;
    }
    let mut launch = Command::new("xcrun");
    launch.args(["simctl", "launch", &identifier, bundle, "--render"]);
    if flag(args, "--quick") {
        launch.arg("--quick");
    }
    if let Some(routes) = option(args, "--routes")? {
        launch.args(["--routes", &routes]);
    }
    execute(&mut launch)?;
    let deadline = Instant::now() + Duration::from_secs(180);
    while !source.join("COMPLETE.txt").is_file() {
        ensure!(Instant::now() <= deadline, "study rendering timed out");
        thread::sleep(Duration::from_millis(500));
    }
    let destination = here.join("renders");
    let manifest = destination.join("manifest.json");
    let mut merged = if manifest.exists() {
        read_json(&manifest)?
            .as_array()
            .context("stored manifest is not an array")?
            .clone()
    } else {
        Vec::new()
    };
    let captured = read_json(&source.join("manifest.json"))?
        .as_array()
        .context("captured manifest is not an array")?
        .clone();
    for item in &captured {
        let file = item["file"]
            .as_str()
            .context("captured manifest item has no file")?;
        if let Some(index) = merged.iter().position(|v| v["file"] == file) {
            merged[index] = item.clone();
        } else {
            merged.push(item.clone());
        }
    }
    copy_tree(&source, &destination)?;
    write_json(&manifest, &merged)?;
    println!(
        "Rendered {} native screens to {}; {} total captures",
        captured.len(),
        destination.display(),
        merged.len()
    );
    Ok(())
}

fn copy_tree(source: &Path, destination: &Path) -> Result<()> {
    fs::create_dir_all(destination)?;
    for entry in fs::read_dir(source)? {
        let entry = entry?;
        let target = destination.join(entry.file_name());
        if entry.file_type()?.is_dir() {
            copy_tree(&entry.path(), &target)?;
        } else {
            fs::copy(entry.path(), target)?;
        }
    }
    Ok(())
}
