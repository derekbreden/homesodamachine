//! repo-tools runs repository maintenance and explicit readings without joining the print build.
use anyhow::{Context, Result};
use std::path::PathBuf;
fn main() -> Result<()> {
    let mut args: Vec<String> = std::env::args().skip(1).collect();
    let mut root = None;
    if let Some(i) = args.iter().position(|a| a == "--root") {
        root = Some(PathBuf::from(
            args.get(i + 1).context("--root needs a path")?,
        ));
        args.drain(i..=i + 1);
    }
    let root = hsm_repo_tools::root(root)?;
    let Some(command) = args.first().map(String::as_str) else {
        println!(
            "repo-tools <cache-gc|time-to-site|missing-tools|model|checks|checks-now|check|paths|drawing-review> [options] [--root path]"
        );
        return Ok(());
    };
    let code = match command {
        "cache-gc" => hsm_repo_tools::cache::cli(&root, &args[1..])?,
        "time-to-site" => hsm_repo_tools::timing::cli(&root, &args[1..])?,
        "missing-tools" => hsm_repo_tools::discovery::cli(&root, &args[1..])?,
        "model" => hsm_repo_tools::model::cli(&root, &args[1..])?,
        "checks" => hsm_repo_tools::checks::cli(&root, &args[1..])?,
        "checks-now" => hsm_repo_tools::checks::now(&root, &args[1..])?,
        "check" => hsm_repo_tools::integrity::cli(&root, &args[1..])?,
        "paths" => hsm_repo_tools::paths::cli(&root, &args[1..])?,
        "drawing-review" => hsm_repo_tools::drawing_review::cli(&root, &args[1..])?,
        "--help" | "-h" => {
            println!(
                "repo-tools maintains repository scratch and reads requested timing, calibration and checks."
            );
            0
        }
        _ => anyhow::bail!("unknown repo-tools command {command}"),
    };
    std::process::exit(code)
}
