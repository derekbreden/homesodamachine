//! Each printed piece's files, written from its plan in this process: the STEP, the fine
//! model, the payload the page draws and, for a printed piece, the STL the slicer reads.
use crate::corner;
use crate::eval::{evaluate, find};
use crate::numbers::{BackBottomPrint, BackTopPrint, Color, Field, FrontCorners, Rail};
use crate::ops;
use crate::plan::{Graph, Op, Shape};
use crate::presentation::{self, Request};
use crate::skin;
use crate::sources::Sources;
use crate::structure::Silhouette;
use anyhow::{Context, Result, anyhow};
use hsm_kernel::part::{write_printed, write_shown};
use hsm_kernel::{Body, Solid, model_bytes, step_bytes, v3};
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
fn keep(path: &Path, bytes: &[u8]) -> Result<()> {
    if std::fs::read(path).is_ok_and(|held| held == bytes) {
        return Ok(());
    }
    let file = path.file_name().and_then(|f| f.to_str()).ok_or_else(|| anyhow!("no file name in {}", path.display()))?;
    let tmp = path.with_file_name(format!(".{file}.{}.{file}", std::process::id()));
    std::fs::write(&tmp, bytes).with_context(|| format!("writing {}", tmp.display()))?;
    std::fs::rename(&tmp, path).with_context(|| format!("renaming onto {}", path.display()))
}

fn digest(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn solids<const N: usize>(g: &Graph, outputs: [Shape; N], silhouette: Option<&Silhouette>) -> Result<[Solid; N]> {
    evaluate(g, &outputs, silhouette)?.try_into().map_err(|_| anyhow!("one solid per plan output"))
}

/// The STEP and the fine model of a shown body; the model's bytes, which a fine-bound payload
/// names.
fn shown(dir: &Path, name: &str, solid: &Solid, color: Color) -> Result<(Vec<u8>, Vec<u8>)> {
    let bodies = [Body { name, color: Some(color), solid }];
    let step = step_bytes(&bodies, name)?;
    let model = model_bytes(&bodies);
    keep(&dir.join(format!("{name}.step")), &step)?;
    keep(&dir.join(format!("{name}.step.npz")), &model)?;
    Ok((step, model))
}

/// The payload cut from a printed STL, naming the file `source` holds the bytes of.
fn payload(dir: &Path, name: &str, color: Color, stl: &[u8], source: &[u8], sources: Option<&Sources>) -> Result<()> {
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

/// The back-bottom panel: its raised disposal warning stands on a smooth field in the fluted
/// print.
#[allow(clippy::too_many_arguments)]
pub fn write_back_bottom(dir: &Path, g: &Graph, result: Shape, silhouette: &Silhouette, field: &Field,
                         rails: &[Rail], print: &BackBottomPrint, color: Color) -> Result<()> {
    let name = "enclosure-back-bottom";
    let letters = find(g, result, |op| matches!(op, Op::DisposalLetters(_))).context("back-bottom warning relief")?;
    let [solid, relief] = solids(g, [result, letters], Some(silhouette))?;
    let (_, model) = shown(dir, name, &solid, color)?;
    let o = silhouette.structure.outer;
    let b = relief.bounds();
    let margin = print.warning_margin;
    let land = [
        b.min.x - margin,
        b.max.x + margin,
        o[3] - print.wall,
        o[3] + print.warning_raise,
        b.min.z - margin,
        b.max.z + margin,
    ];
    let smooth = solid.cut(&Solid::cuboid(
        v3(land[0], o[3], land[4]),
        v3(land[1], o[3] + print.warning_raise + 1.0, land[5]),
    ))?;
    let fluted = skin::flute_solid(&smooth.simplified()?, field, rails, &[land])?;
    let joined = fluted.union(&ops::manifold(&relief)?);
    let stl = ops::print_stl_bytes(&ops::quantized(&joined)?);
    keep(&dir.join(format!("{name}.stl")), &stl)?;
    payload(dir, name, color, &stl, &model, None)
}

/// The back-top panel: the nameplate field and the raised rails stand smooth in the fluted
/// print, clear of the sliding channels.
#[allow(clippy::too_many_arguments)]
pub fn write_back_top(dir: &Path, g: &Graph, result: Shape, receiver_field: Shape, silhouette: &Silhouette,
                      field: &Field, rails: &[Rail], print: &BackTopPrint, color: Color) -> Result<()> {
    let name = "enclosure-back-top";
    let [solid, receiver] = solids(g, [result, receiver_field], Some(silhouette))?;
    let (_, model) = shown(dir, name, &solid, color)?;
    let o = silhouette.structure.outer;
    let b = receiver.bounds();
    let land = [b.min.x, b.max.x, b.min.y, o[3] + 1., b.min.z, b.max.z];
    let mut lands = vec![land];
    lands.extend(print.raised_bounds.iter().copied());
    let mut smooth = solid.clone();
    let mut relief = vec![];
    for b in &lands {
        smooth = smooth.cut(&Solid::cuboid(v3(b[0], b[2], b[4]), v3(b[1], o[3] + 10., b[5])))?;
        relief.push(solid.intersect(&Solid::cuboid(v3(b[0], b[2] - print.embed, b[4]), v3(b[1], o[3] + 10., b[5])))?);
    }
    let relief = Solid::union_all(&relief)?;
    let fluted = skin::flute_solid(&smooth.simplified()?, field, rails, &[land])?;
    let mut joined = fluted.union(&ops::manifold(&relief)?);
    // Keep the raised rails' embedded print skin out of the sliding channels. Their fitted
    // lips start at the outer wall plane.
    let rear = o[3];
    for bounds in &print.label_channels {
        let (lo, hi) = ops::corners(bounds);
        joined = joined.difference(&ops::manifold(&Solid::cuboid(lo, v3(hi.x, hi.y.min(rear), hi.z)))?);
    }
    let stl = ops::print_stl_bytes(&ops::quantized(&joined)?);
    keep(&dir.join(format!("{name}.stl")), &stl)?;
    payload(dir, name, color, &stl, &model, None)
}

/// The front-bottom quadrant and its fluted print.
pub fn write_front_bottom(dir: &Path, g: &Graph, result: Shape, silhouette: &Silhouette, field: &Field,
                          rails: &[Rail], color: Color) -> Result<()> {
    let name = "enclosure-front-bottom";
    let [solid] = solids(g, [result], Some(silhouette))?;
    let (_, model) = shown(dir, name, &solid, color)?;
    let printed = skin::flute_solid(&solid.simplified()?, field, rails, &[])?;
    let stl = ops::print_stl_bytes(&printed);
    keep(&dir.join(format!("{name}.stl")), &stl)?;
    payload(dir, name, color, &stl, &model, None)
}

/// The front-top quadrant, its front corner drawn on the analytic controls, and its fluted
/// print with each triangle's lineage.
#[allow(clippy::too_many_arguments)]
pub fn write_front_top(dir: &Path, g: &Graph, result: Shape, silhouette: &Silhouette, corners: &FrontCorners,
                       field: &Field, rails: &[Rail], color: Color) -> Result<()> {
    let name = "enclosure-front-top";
    let structure = silhouette.structure;
    let [plan] = solids(g, [result], Some(silhouette))?;
    let solid = corner::replace(plan.simplified()?, corners, structure.side_radius, structure.angle)?;
    drop(plan);
    // The complete structural model carries the CAD file's sliver cleanup; the print starts
    // from the same model.
    let model = solid.simplified()?;
    drop(solid);
    let (step, _) = shown(dir, name, &model, color)?;
    let mut sources = Sources::new(&model);
    let shape = skin::flute_solid_observed(&model, field, rails, &[], &mut sources)?;
    let stl = ops::print_stl_bytes(&shape);
    keep(&dir.join(format!("{name}.stl")), &stl)?;
    let mut document = sources.document();
    document["sha256"] = digest(&stl).into();
    keep(&dir.join(format!("{name}.stl.sources.json")), &serde_json::to_vec(&document)?)?;
    payload(dir, name, color, &stl, &step, Some(&sources))
}

/// The lower pump retainer: relaxed wings print and draw from the STL; seated, it is drawn
/// from its solid and not printed.
pub fn write_retainer(dir: &Path, g: &Graph, result: Shape, name: &str, seated: bool, color: Color) -> Result<()> {
    let [solid] = solids(g, [result], None)?;
    let bodies = [Body { name, color: Some(color), solid: &solid }];
    if seated {
        write_shown(dir, name, &bodies)?;
        return Ok(());
    }
    write_printed(dir, name, &bodies)?;
    let step = std::fs::read(dir.join(format!("{name}.step")))?;
    let stl = std::fs::read(dir.join(format!("{name}.stl")))?;
    payload(dir, name, color, &stl, &step, None)
}

/// The four-channel factory tube-setting jig.
pub fn write_jig(dir: &Path, g: &Graph, result: Shape, color: Color) -> Result<()> {
    let name = "enclosure-pump-tube-setting-jig";
    let [solid] = solids(g, [result], None)?;
    write_printed(dir, name, &[Body { name, color: Some(color), solid: &solid }])?;
    let model = std::fs::read(dir.join(format!("{name}.step.npz")))?;
    let stl = std::fs::read(dir.join(format!("{name}.stl")))?;
    payload(dir, name, color, &stl, &model, None)
}
