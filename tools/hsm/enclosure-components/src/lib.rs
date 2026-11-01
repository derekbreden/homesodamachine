//! The enclosure's coloured prints: separate filament bodies and one fused exterior STL.
use anyhow::Result;
use hsm_kernel::part::write_shown;
use hsm_kernel::{Body, Solid, stl_bytes};
use serde_json::{Value, json};
use std::path::Path;

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
