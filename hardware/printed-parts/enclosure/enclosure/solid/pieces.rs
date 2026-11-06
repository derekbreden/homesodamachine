//! What every printed piece's files share, written from its plan in its own process: its solids,
//! the STEP and fine model of a shown body, and the payload the page draws, cut from the STL the
//! slicer reads.
use crate::eval::evaluate;
use crate::plan::{Graph, Shape};
use crate::presentation::{self, Request};
use crate::sources::Sources;
use crate::structure::Silhouette;
use anyhow::{Context, Result, anyhow};
use hsm_enclosure_numbers::Color;
use hsm_kernel::{Body, Solid, model_bytes, step_bytes};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::path::Path;

/// The viewer's crease angle, in degrees, as `hardware/scripts/_payload_rules.py` states it:
/// wider dihedral angles shade as separate regions.
const CREASE_DEG: f64 = 30.0;
/// The payload's distance budget per millimetre of the print's mean extent, as the same rules
/// state it.
const LINEAR_DEFLECTION_RATIO: f64 = 0.001;

/// `bytes` at `path`, unless the file holds them already; any other lands whole, by a rename.
pub fn keep(path: &Path, bytes: &[u8]) -> Result<()> {
    if std::fs::read(path).is_ok_and(|held| held == bytes) {
        return Ok(());
    }
    let file = path.file_name().and_then(|f| f.to_str()).ok_or_else(|| anyhow!("no file name in {}", path.display()))?;
    let tmp = path.with_file_name(format!(".{file}.{}.{file}", std::process::id()));
    std::fs::write(&tmp, bytes).with_context(|| format!("writing {}", tmp.display()))?;
    std::fs::rename(&tmp, path).with_context(|| format!("renaming onto {}", path.display()))
}

pub fn digest(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

pub fn solids<const N: usize>(g: &Graph, outputs: [Shape; N], silhouette: Option<&Silhouette>) -> Result<[Solid; N]> {
    evaluate(g, &outputs, silhouette)?.try_into().map_err(|_| anyhow!("one solid per plan output"))
}

/// The STEP and the fine model of a shown body; the model's bytes, which a fine-bound payload
/// names.
pub fn shown(dir: &Path, name: &str, solid: &Solid, color: Color) -> Result<(Vec<u8>, Vec<u8>)> {
    let bodies = [Body { name, color: Some(color), solid }];
    let step = step_bytes(&bodies, name)?;
    let model = model_bytes(&bodies);
    keep(&dir.join(format!("{name}.step")), &step)?;
    keep(&dir.join(format!("{name}.step.npz")), &model)?;
    Ok((step, model))
}

/// The payload cut from a printed STL, naming the file `source` holds the bytes of.
pub fn payload(dir: &Path, name: &str, color: Color, stl: &[u8], source: &[u8], sources: Option<&Sources>) -> Result<()> {
    let (mesh, exact) = presentation::weld(stl)?;
    let lineage = sources.and_then(|s| {
        let triangles: Vec<usize> = s.faces.iter().map(|&f| f as usize).collect();
        presentation::lineage(&s.records, &triangles, mesh.faces.len(), exact)
    });
    let cut = presentation::cut(&mesh, lineage, Request {
        name: Value::from(name),
        color: json!(color),
        src: &digest(source),
        crease_deg: CREASE_DEG,
        deflection_ratio: LINEAR_DEFLECTION_RATIO,
        preserve: false,
        unknown: sources.is_some(),
        check: false,
    })?;
    keep(&dir.join(format!("{name}.step.mesh")), &cut.payload)
}
