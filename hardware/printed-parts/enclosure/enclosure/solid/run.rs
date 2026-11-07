//! A piece program's command line: the declared Box it cuts from and the directory its files go
//! into. A program runs at the repository root, or a copy of the files it reads at their
//! repository paths.
use anyhow::{Context, Result, bail};
use hsm_enclosure_numbers::spec::Box;
use std::path::{Path, PathBuf};

pub const BOX: &str = "hardware/manifold-layout/enclosure-box.json";
pub const OUTPUT: &str = "hardware/printed-parts/enclosure/enclosure";
pub const EXTERIOR: &str = "hardware/printed-parts/enclosure/enclosure/exterior.json";

/// The Box and the output directory `<program> [--box <declared Box>] [<output directory>]`
/// names, with the Box read as the run's first input.
pub fn arguments(program: &str) -> Result<(Box, PathBuf)> {
    let quadrant = matches!(
        program,
        "enclosure-front-top"
            | "enclosure-front-bottom"
            | "enclosure-back-top"
            | "enclosure-back-bottom"
    );
    let usage = format!(
        "usage: {program} [--box <declared Box>] [--exterior <exterior>] [<output directory>]"
    );
    let (mut declared, mut exterior, mut out) = (PathBuf::from(BOX), PathBuf::from(EXTERIOR), None);
    let mut args = std::env::args_os().skip(1);
    while let Some(arg) = args.next() {
        match arg.to_str() {
            Some("--box") => declared = args.next().with_context(|| usage.clone())?.into(),
            Some("--exterior") => exterior = args.next().with_context(|| usage.clone())?.into(),
            _ if out.is_none() => out = Some(PathBuf::from(arg)),
            _ => bail!(usage),
        }
    }
    let out = out.unwrap_or_else(|| PathBuf::from(OUTPUT));
    hsm_kernel::reads::begin();
    let document = read(&declared)?;
    let mut b = Box::from_document(serde_json::from_slice(&document)?)
        .with_context(|| declared.display().to_string())?;
    if quadrant {
        let design =
            serde_json::from_slice::<hsm_enclosure_numbers::exterior::Exterior>(&read(&exterior)?)
                .with_context(|| exterior.display().to_string())?;
        anyhow::ensure!(
            design.valid(),
            "the exterior dimensions describe a finite circular band and columns"
        );
        b.exterior = Some(design);
    }
    std::fs::create_dir_all(&out)?;
    Ok((b, out))
}

/// A file's bytes, listed among the run's reads.
pub fn read(path: &Path) -> Result<Vec<u8>> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(path, &bytes);
    Ok(bytes)
}
