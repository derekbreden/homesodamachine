//! `hsm-manual-guides` builds the shop books only when a guide is requested.
use anyhow::{Context, Result, bail};
use std::path::PathBuf;

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let operation = args.next().unwrap_or_else(|| "help".into());
    if operation == "list" {
        for spec in hsm_manual_guides::html::SPECS {
            println!("{}\t{}", spec.id, spec.title);
        }
        for (name, title) in [
            ("faucet-assembly-guide", "Faucet assembly"),
            ("gun-positioner-guide", "PGFUN two-axis weld positioner"),
            ("mold-guide", "Silicone mold and insulation"),
            ("refrigeration-guide", "Refrigeration circuit"),
            ("water-inlet-jet-guide", "Water-inlet jet"),
        ] {
            println!("{name}\t{title}");
        }
        return Ok(());
    }
    if operation == "help" || operation == "--help" {
        println!(
            "hsm-manual-guides list\nhsm-manual-guides author magnetic-float-guide [--root DIR] [--output DIR]\nhsm-manual-guides bind GUIDE [--root DIR] [--output DIR] [--reuse-leaves] [--pages N ...]\nhsm-manual-guides build GUIDE [--root DIR] [--output DIR] [--reuse-art] [--inputs DIR]\nhsm-manual-guides art GUIDE [--root DIR] [--output DIR] [--scenes NAME ...] [--inputs DIR]\nhsm-manual-guides fixture tube-insertion|donor-hold-down [--root DIR] [--output DIR]\nhsm-manual-guides review tube-insertion [--root DIR] [--output FILE]\nhsm-manual-guides qa gun-positioner-guide [--root DIR]\nhsm-manual-guides markings refrigerant-warning [--root DIR] [--output DIR] [--inputs HELVETICA_TTC]"
        );
        return Ok(());
    }
    let name = args.next().context("guide name")?;
    let mut root = None;
    let mut output = None;
    let mut inputs = None;
    let mut reuse = false;
    let mut selected = Vec::new();
    let mut scenes = Vec::new();
    let mut reuse_art = false;
    let mut list_scenes = false;
    let mut rest = args.peekable();
    while let Some(arg) = rest.next() {
        match arg.as_str() {
            "--root" => root = Some(PathBuf::from(rest.next().context("--root DIR")?)),
            "--output" => output = Some(PathBuf::from(rest.next().context("--output DIR")?)),
            "--inputs" => inputs = Some(PathBuf::from(rest.next().context("--inputs DIR")?)),
            "--reuse-leaves" => reuse = true,
            "--reuse-art" => reuse_art = true,
            "--list" => list_scenes = true,
            "--scenes" => {
                while rest.peek().is_some_and(|v| !v.starts_with('-')) {
                    scenes.push(rest.next().unwrap());
                }
            }
            "--pages" => {
                while rest.peek().is_some_and(|v| !v.starts_with('-')) {
                    selected.push(
                        rest.next()
                            .unwrap()
                            .parse::<usize>()
                            .context("page number")?,
                    );
                }
            }
            _ => bail!("unknown argument {arg}"),
        }
    }
    let cwd = std::env::current_dir()?;
    let absolute = |path: PathBuf| {
        if path.is_absolute() {
            path
        } else {
            cwd.join(path)
        }
    };
    let root = absolute(root.map_or_else(hsm_manual_guides::root, Ok)?)
        .canonicalize()
        .context("guide checkout root")?;
    let output = output.map(absolute);
    let inputs = inputs.map(absolute);
    if operation == "art" && list_scenes {
        let names: Vec<&str> = match name.as_str() {
            "gun-positioner-guide" => hsm_manual_guides::pgfun_art::SCENES
                .iter()
                .map(|s| s.name)
                .collect(),
            "tube-insertion-guide" => hsm_manual_guides::tube_art::NAMES.to_vec(),
            "faucet-assembly-guide" => hsm_manual_guides::faucet_art::NAMES.to_vec(),
            _ => bail!("unknown artwork guide {name}"),
        };
        for name in names {
            println!("{name}");
        }
        return Ok(());
    }
    match operation.as_str() {
        "markings" if name == "refrigerant-warning" => {
            hsm_manual_guides::markings::build(&root, output.as_deref(), inputs.as_deref())
        }
        "bind" => hsm_manual_guides::html::bind(&root, &name, output.as_deref(), reuse, &selected),
        "author" if name == "magnetic-float-guide" => {
            hsm_manual_guides::float::author(&root, output.as_deref())
        }
        "build" if matches!(name.as_str(), "mold-guide" | "refrigeration-guide") => {
            hsm_manual_guides::paper::build(&root, &name, output.as_deref())
        }
        "build" if name == "faucet-assembly-guide" => {
            hsm_manual_guides::faucet_book::build(&root, output.as_deref())
        }
        "build" if name == "water-inlet-jet-guide" => {
            hsm_manual_guides::jet_book::build(&root, output.as_deref())
        }
        "build" if name == "gun-positioner-guide" => {
            if reuse_art {
                return hsm_manual_guides::pgfun_book::build(
                    &root,
                    output.as_deref(),
                    None,
                    inputs.as_deref(),
                );
            }
            let art = output
                .as_deref()
                .unwrap_or(&root)
                .join("hardware/gun-positioner-guide/art");
            hsm_manual_guides::pgfun_art::render(&root, &art, &[], inputs.as_deref())?;
            hsm_manual_guides::pgfun_book::build(
                &root,
                output.as_deref(),
                Some(&art),
                inputs.as_deref(),
            )
        }
        "art" if name == "gun-positioner-guide" => hsm_manual_guides::pgfun_art::render(
            &root,
            &output.unwrap_or_else(|| root.join("hardware/gun-positioner-guide/art")),
            &scenes,
            inputs.as_deref(),
        ),
        "art" if name == "tube-insertion-guide" => hsm_manual_guides::tube_art::render(
            &root,
            &output.unwrap_or_else(|| root.join("hardware/tube-insertion-guide/art")),
            &scenes,
        ),
        "art" if name == "faucet-assembly-guide" => hsm_manual_guides::faucet_art::render(
            &root,
            &output.unwrap_or_else(|| root.join("hardware/faucet-assembly-guide/art")),
            &scenes,
        ),
        "fixture" if name == "tube-insertion" => {
            hsm_manual_guides::tube_fixture::export(
                &root,
                &output.unwrap_or_else(|| root.join(hsm_manual_guides::tube_fixture::DIRECTORY)),
            )?;
            Ok(())
        }
        "fixture" if name == "donor-hold-down" => hsm_manual_guides::donor_pad::export(
            &root,
            &output.unwrap_or_else(|| root.join(hsm_manual_guides::donor_pad::DIRECTORY)),
        ),
        "qa" if name == "gun-positioner-guide" => hsm_manual_guides::pgfun_qa::review(&root),
        "review" if name == "tube-insertion" => hsm_manual_guides::tube_review::review(
            &root,
            &output.unwrap_or_else(|| {
                root.join(hsm_manual_guides::tube_fixture::DIRECTORY)
                    .join("geometry-review.json")
            }),
        ),
        _ => bail!("unknown operation {operation}"),
    }
}
