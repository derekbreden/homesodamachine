//! The enclosure's small parts' programs: the folder each writes into, and its coloured prints'
//! separate filament bodies and one fused exterior STL.
use anyhow::{Result, ensure};
use hsm_kernel::part::write_shown;
use hsm_kernel::{Body, Solid, stl_bytes};
use serde_json::{Value, json};
use std::path::{Path, PathBuf};

/// A port's identification colours, as the payload carries them: the filament its chip prints in
/// and the colour of the word on it, under the port's filament key.
pub fn port_colors(fluid: &str) -> Result<([f64; 3], [f64; 3])> {
    use hsm_shared_data::color::{chips, rgb8_linear};
    let chips = chips()?;
    Ok((rgb8_linear(&chips["chip_filaments"][fluid][1], true)?, rgb8_linear(&chips["chip_word_colors"][fluid], true)?))
}

/// The folder a part's program writes into: the one it is given, or the part's own; the run's
/// reads begin here.
pub fn output(program: &str, folder: &str) -> Result<PathBuf> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(folder));
    ensure!(args.next().is_none(), "usage: {program} [<output directory>]");
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    Ok(out)
}

/// Keep the filament volumes in the STEP and model, and the explicit fused solid in the
/// single-material print. Identical bytes keep their timestamp; replacements land whole.
pub fn write_colored_part(out: &Path, name: &str, bodies: &[Body], exterior: &Solid) -> Result<Value> {
    let mut said = write_shown(out, name, bodies)?;
    let file = format!("{name}.stl");
    let path = out.join(&file);
    let bytes = stl_bytes(&[exterior])?;
    if !std::fs::read(&path).is_ok_and(|held| held == bytes) {
        let tmp = out.join(format!(".{name}.{}.stl", std::process::id()));
        std::fs::write(&tmp, bytes)?;
        std::fs::rename(&tmp, path)?;
    }
    said["files"].as_array_mut().unwrap().push(json!(file));
    Ok(said)
}
