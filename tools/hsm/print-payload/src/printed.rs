//! A printed piece's files from its program: the STEP, the model file and the STL the kernel cuts,
//! and the payload the page draws, cut from the STL with every printed triangle kept, so a pick on
//! the page lands on the surface the slicer prints.
use anyhow::{Context, Result, anyhow};
use hsm_kernel::Body;
use hsm_kernel::part::write_printed;
use crate as presentation;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::path::Path;

/// Writes `body`'s files as `name` into `dir`, the payload among them, and says what they hold.
pub fn write(dir: &Path, name: &str, body: Body) -> Result<Value> {
    let mut said = write_printed(dir, name, &[body])?;
    let read = |file: String| std::fs::read(dir.join(&file)).with_context(|| format!("reading {file}"));
    let step = read(format!("{name}.step"))?;
    let stl = read(format!("{name}.stl"))?;
    let payload = payload(body, &step, &stl)?;
    let file = format!("{name}.step.mesh");
    keep(&dir.join(&file), &payload)?;
    said["files"].as_array_mut().context("the files written")?.push(Value::from(file));
    Ok(said)
}

/// The payload of the printed triangles in `stl`, named and coloured as `body` and bound to the
/// STEP whose bytes are `step`.
pub fn payload(body: Body, step: &[u8], stl: &[u8]) -> Result<Vec<u8>> {
    let src: String = Sha256::digest(step).iter().map(|b| format!("{b:02x}")).collect();
    let (mesh, _) = presentation::weld(stl)?;
    let cut = presentation::cut(
        &mesh,
        None,
        presentation::Request {
            name: json!(body.name),
            color: json!(body.color),
            src: &src,
            crease_deg: presentation::CREASE_DEG,
            deflection_ratio: presentation::LINEAR_DEFLECTION_RATIO,
            preserve: true,
            unknown: false,
            check: false,
        },
    )?;
    Ok(cut.payload)
}

/// `bytes` at `path`, unless the file holds them already, landed whole by a rename.
pub fn keep(path: &Path, bytes: &[u8]) -> Result<()> {
    if std::fs::read(path).is_ok_and(|held| held == bytes) {
        return Ok(());
    }
    let file = path.file_name().and_then(|f| f.to_str()).ok_or_else(|| anyhow!("no file name in {}", path.display()))?;
    let tmp = path.with_file_name(format!(".{file}.{}.{file}", std::process::id()));
    std::fs::write(&tmp, bytes).with_context(|| format!("writing {}", tmp.display()))?;
    std::fs::rename(&tmp, path).with_context(|| format!("renaming onto {}", path.display()))
}

/// The directory a step's files go to: the one it is given on its command line, or its own in the
/// tree. A step names what it reads from here on.
pub fn out_dir(own: &str) -> Result<std::path::PathBuf> {
    hsm_kernel::reads::begin();
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(std::path::PathBuf::from).unwrap_or_else(|| own.into());
    if args.next().is_some() {
        anyhow::bail!("usage: {} [<output directory>]", std::env::args().next().unwrap_or_default());
    }
    std::fs::create_dir_all(&out)?;
    Ok(out)
}
