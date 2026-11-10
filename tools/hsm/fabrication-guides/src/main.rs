//! The fabrication-guides command draws bench documents and prints their authored inputs without starting an appliance build.
use anyhow::{Context, Result};
use std::path::PathBuf;

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let guide=args.next().context("usage: fabrication-guides <assembly-letter|drill-and-cut-guide> [--root path] [--out path]")?;
    if guide == "data" {
        anyhow::ensure!(
            args.next().as_deref() == Some("weld-position") && args.next().is_none(),
            "usage: fabrication-guides data weld-position"
        );
        use hsm_endcap_circular_numbers as cap;
        use hsm_weld_rotator_numbers::{recipe, tube};
        println!(
            "{}",
            serde_json::json!({
                "tubeOd":tube::OD,"tubeWall":tube::WALL,"tubeHeight":tube::LENGTH,
                "capRecess":recipe::ENDCAP_RECESS,"capDiameter":cap::DIAMETER_IN*cap::INCH,
                "capThickness":cap::THICKNESS_IN*cap::INCH,"portDiameter":cap::HOLE_DIAMETER_IN*cap::INCH,
                "portOffset":cap::HOLE_SPACING_IN*cap::INCH/2.0
            })
        );
        return Ok(());
    }
    let mut root = std::env::current_dir()?;
    let mut out = None;
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--root" => root = PathBuf::from(args.next().context("--root needs a path")?),
            "--out" => out = Some(PathBuf::from(args.next().context("--out needs a path")?)),
            _ => anyhow::bail!("unknown argument {arg}"),
        }
    }
    let out = out.unwrap_or_else(|| root.clone());
    let manifest = hsm_fabrication_guides::build(&root, &out, &guide)?;
    println!(
        "{} / {} Letter pages",
        manifest["pdf"].as_str().unwrap_or(&guide),
        manifest["pages"]
    );
    Ok(())
}
