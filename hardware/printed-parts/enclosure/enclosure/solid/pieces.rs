//! What every printed piece's files share, written from its plan in its own process: its solids,
//! the fine model of a shown body, and the payload the page draws, cut from the STL the
//! slicer reads.
use crate::eval::evaluate;
use crate::plan::{Graph, Shape};
use crate::presentation::{self, CREASE_DEG, LINEAR_DEFLECTION_RATIO, Request};
use crate::sources::Sources;
use crate::structure::Silhouette;
use anyhow::{Context, Result, anyhow};
use hsm_enclosure_numbers::Color;
use hsm_kernel::{Body, Solid, model_bytes};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::path::Path;

/// `bytes` at `path`, unless the file holds them already; any other lands whole, by a rename.
pub fn keep(path: &Path, bytes: &[u8]) -> Result<()> {
    if std::fs::read(path).is_ok_and(|held| held == bytes) {
        return Ok(());
    }
    let file = path
        .file_name()
        .and_then(|f| f.to_str())
        .ok_or_else(|| anyhow!("no file name in {}", path.display()))?;
    let tmp = path.with_file_name(format!(".{file}.{}.{file}", std::process::id()));
    std::fs::write(&tmp, bytes).with_context(|| format!("writing {}", tmp.display()))?;
    std::fs::rename(&tmp, path).with_context(|| format!("renaming onto {}", path.display()))
}

pub fn digest(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

pub fn solids<const N: usize>(
    g: &Graph,
    outputs: [Shape; N],
    silhouette: Option<&Silhouette>,
) -> Result<[Solid; N]> {
    evaluate(g, &outputs, silhouette)?
        .try_into()
        .map_err(|_| anyhow!("one solid per plan output"))
}

/// The finished body and its separately constrained authored addition share one evaluation.
pub fn separated(
    g: &Graph,
    result: Shape,
    silhouette: &Silhouette,
) -> Result<(Solid, Solid, Solid)> {
    if let Some((core, band)) = g.additive_parts(result) {
        let [solid, core, band] = solids(g, [result, core, band], Some(silhouette))?;
        Ok((solid, core, band))
    } else {
        let [solid] = solids(g, [result], Some(silhouette))?;
        Ok((solid.clone(), solid, Solid::empty()))
    }
}

/// The plain band joins the printed body after the wall's flute tool has finished.
pub fn join_band(core: &manifold_csg::Manifold, band: &Solid) -> Result<manifold_csg::Manifold> {
    let joined = if band.is_empty() {
        core.clone()
    } else {
        core.union(&crate::ops::manifold(band)?)
    };
    crate::ops::quantized(&joined)
}

/// The fine model binds a shown body to the printed surface derived from its construction.
pub fn shown(dir: &Path, name: &str, solid: &Solid, color: Color) -> Result<(Vec<u8>, Vec<u8>)> {
    let bodies = [Body {
        name,
        color: Some(color),
        solid,
    }];
    let model = crate::cache::phase("fine model", || Ok(model_bytes(&bodies)))?;
    keep(&dir.join(format!("{name}.step.npz")), &model)?;
    Ok((model.clone(), model))
}

/// The payload cut from a printed STL, naming the file `source` holds the bytes of.
pub fn payload(
    dir: &Path,
    name: &str,
    color: Color,
    stl: &[u8],
    source: &[u8],
    sources: Option<&Sources>,
) -> Result<()> {
    let (mesh, exact) = crate::cache::phase("print mesh welding", || presentation::weld(stl))?;
    let lineage = sources.and_then(|s| {
        let triangles: Vec<usize> = s.faces.iter().map(|&f| f as usize).collect();
        presentation::lineage(&s.records, &triangles, mesh.faces.len(), exact)
    });
    let cut = crate::cache::phase("viewer surface", || {
        presentation::cut(
            &mesh,
            lineage,
            Request {
                name: Value::from(name),
                color: json!(color),
                src: &digest(source),
                crease_deg: CREASE_DEG,
                deflection_ratio: LINEAR_DEFLECTION_RATIO,
                preserve: true,
                unknown: sources.is_some(),
                check: false,
            },
        )
    })?;
    let mut head=hsm_geometry::scene::pack(&cut.payload)?;
    head["step_export"]=json!(false);
    hsm_geometry::scene::persist(&dir.join(format!("{name}.step.mesh")),&head)
}
