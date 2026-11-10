//! geometry-lint inspects saved printed meshes after publication without starting a build.
use anyhow::{Result, bail, ensure};
use clap::Parser;
use hsm_mesh_review::{CLASSES, Options};
use std::path::PathBuf;

#[derive(Parser)]
#[command(about = "Rank printed-mesh anomalies and emit /3d Find locations")]
struct Args {
    /// Saved STL files, or STEP paths with an STL beside them.
    pieces: Vec<PathBuf>,
    #[arg(long, default_value_t = 12)]
    top: usize,
    #[arg(long)]
    all: bool,
    #[arg(long, default_value = "step,bump,sliver,ceiling,slope,thin,ledge")]
    classes: String,
    /// Native fine archive whose recorded print binding names the exact STL.
    #[arg(long)]
    sources: Option<PathBuf>,
    /// Explicit build direction along the saved model's Z axis.
    #[arg(long, allow_hyphen_values = true)]
    print_up: Option<f64>,
    /// Explicit lean about the saved model's X axis after the build-direction flip.
    #[arg(long, allow_hyphen_values = true)]
    tilt_x: Option<f64>,
    /// Review a mold project's cavity and inverted core from their saved STL files.
    #[arg(long)]
    models: Option<PathBuf>,
    #[arg(long)]
    json: bool,
}
fn main() -> Result<()> {
    let args = Args::parse();
    let mut files = args.pieces;
    if let Some(models) = args.models {
        files.extend([models.join("cavity.stl"), models.join("core.stl")]);
    }
    ensure!(
        !files.is_empty(),
        "name at least one saved piece, or --models DIR"
    );
    let classes = args
        .classes
        .split(',')
        .filter(|s| !s.is_empty())
        .map(str::to_owned)
        .collect::<Vec<_>>();
    for class in &classes {
        if !CLASSES.contains(&class.as_str()) {
            bail!("unknown class {class}; choose {}", CLASSES.join(","));
        }
    }
    let options = Options {
        classes,
        up: args.print_up,
        tilt_x: args.tilt_x,
        sources: args.sources,
    };
    let mut reports = Vec::new();
    for file in files {
        let stl = if file.extension().is_some_and(|s| s == "stl") {
            file
        } else {
            file.with_extension("stl")
        };
        let report = hsm_mesh_review::review(&stl, &options)?;
        if !args.json {
            hsm_mesh_review::print_report(&report, args.top, args.all);
        }
        reports.push(report);
    }
    if args.json {
        println!("{}", serde_json::to_string_pretty(&reports)?);
    }
    Ok(())
}
