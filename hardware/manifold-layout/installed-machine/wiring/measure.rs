//! The extents of a fine model's bodies, read in this process from the model file itself.
//!
//! A body is bounded over its stored vertices and triangles, the coordinates the kernel keeps
//! for it. The bodies whose volume and separate solids are wanted, and every body of a model
//! that is moved first, go through the kernel's own import.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Affine, Imported};
use serde_json::{Value, json};
use std::collections::BTreeSet;
use std::io::{Read, Seek};
use std::path::Path;

/// Each body of the model at `path`, moved by `transform`, as its name, colour and bounds, with
/// its volume and separate solids for the names in `solids`.
pub fn summaries(path: &Path, transform: Option<&Affine>, solids: &BTreeSet<String>) -> Result<Vec<Value>> {
    crate::design::record(path);
    let file = std::fs::File::open(path).with_context(|| format!("reading {}", path.display()))?;
    let mut archive = zip::ZipArchive::new(std::io::BufReader::new(file))
        .with_context(|| format!("reading model {}", path.display()))?;
    let names: Vec<String> = serde_json::from_slice(Stored::read(&mut archive, "names")?.data())?;
    let colors: Vec<Option<[f64; 3]>> = serde_json::from_slice(Stored::read(&mut archive, "colors")?.data())?;
    ensure!(names.len() == colors.len(), "{} has {} names and {} colours", path.display(), names.len(), colors.len());
    let imported: BTreeSet<usize> = (0..names.len())
        .filter(|&i| transform.is_some() || solids.contains(&names[i]))
        .collect();
    let mut rows: Vec<Value> = vec![Value::Null; names.len()];
    hsm_kernel::import::visit_model_indices(path, &imported, |index, part: Imported| {
        let solid = match transform {
            Some(frame) => part.solid.transformed(frame),
            None => part.solid,
        };
        let bounds = solid.bounds();
        let mut row = json!({"name": part.name, "color": part.color, "volume": solid.volume(),
                             "min": bounds.min.to_array(), "max": bounds.max.to_array()});
        if solids.contains(&part.name) {
            row["components"] = json!(solid.components().iter().map(|piece| {
                let bounds = piece.bounds();
                json!({"volume": piece.volume(), "min": bounds.min.to_array(), "max": bounds.max.to_array()})
            }).collect::<Vec<_>>());
        }
        rows[index] = row;
        Ok(())
    })
    .with_context(|| format!("measuring {}", path.display()))?;
    for (i, (name, color)) in names.iter().zip(&colors).enumerate() {
        if !imported.contains(&i) {
            let (lo, hi) = stored_bounds(&mut archive, i).with_context(|| format!("measuring {name} in {}", path.display()))?;
            rows[i] = json!({"name": name, "color": color, "volume": null, "min": lo, "max": hi});
        }
    }
    Ok(rows)
}

/// The bounds of body `i` over the stored vertices its triangles use, as the kernel bounds it.
fn stored_bounds<R: Read + Seek>(archive: &mut zip::ZipArchive<R>, i: usize) -> Result<([f64; 3], [f64; 3])> {
    let vertices = Stored::read(archive, &format!("V{i}"))?;
    ensure!(vertices.descr == "<f8" && vertices.columns == 3, "body {i}'s vertices are not rows of three doubles");
    let vertices: Vec<f64> = vertices.data().chunks_exact(8).map(|b| f64::from_le_bytes(b.try_into().unwrap())).collect();
    let triangles = Stored::read(archive, &format!("T{i}"))?;
    ensure!(triangles.descr == "<u4" && triangles.columns == 3, "body {i}'s triangles are not rows of three indices");
    let mut lo = [f64::INFINITY; 3];
    let mut hi = [f64::NEG_INFINITY; 3];
    for b in triangles.data().chunks_exact(4) {
        let at = 3 * u32::from_le_bytes(b.try_into().unwrap()) as usize;
        ensure!(at + 2 < vertices.len(), "body {i} has a vertex index outside its array");
        for k in 0..3 {
            lo[k] = lo[k].min(vertices[at + k]);
            hi[k] = hi[k].max(vertices[at + k]);
        }
    }
    Ok((lo, hi))
}

/// One stored array of a model file: its element type, its row width and its bytes.
struct Stored {
    descr: String,
    columns: usize,
    bytes: Vec<u8>,
    start: usize,
}

impl Stored {
    /// The array `name` of the model `archive`.
    fn read<R: Read + Seek>(archive: &mut zip::ZipArchive<R>, name: &str) -> Result<Self> {
        let mut bytes = Vec::new();
        archive.by_name(&format!("{name}.npy"))?.read_to_end(&mut bytes)?;
        ensure!(bytes.len() >= 10 && bytes.starts_with(b"\x93NUMPY"), "{name} is not an array");
        let (offset, size) = if bytes[6] == 1 {
            (10, u16::from_le_bytes([bytes[8], bytes[9]]) as usize)
        } else {
            (12, u32::from_le_bytes([bytes[8], bytes[9], bytes[10], bytes[11]]) as usize)
        };
        let header = std::str::from_utf8(bytes.get(offset..offset + size).context("a truncated array header")?)?;
        ensure!(header.contains("'fortran_order': False"), "{name} is not in C order");
        let descr = header.split("'descr': '").nth(1).and_then(|s| s.split('\'').next()).unwrap_or_default().to_owned();
        let shape: Vec<usize> = header.split("'shape': (").nth(1).and_then(|s| s.split(')').next()).unwrap_or_default()
            .split(',').filter_map(|s| s.trim().parse().ok()).collect();
        Ok(Self { descr, columns: shape.get(1).copied().unwrap_or(1), bytes, start: offset + size })
    }

    /// The array's elements as stored.
    fn data(&self) -> &[u8] {
        &self.bytes[self.start..]
    }
}

/// A placement written as three rows of four numbers, or none where `value` is absent.
pub fn frame(value: Option<&Value>) -> Result<Option<Affine>> {
    let Some(value) = value.filter(|v| !v.is_null()) else { return Ok(None) };
    let rows = value.as_array().context("a placement is three rows of four numbers")?;
    ensure!(rows.len() == 3, "a placement has {} rows", rows.len());
    let mut m = [[0.0; 4]; 3];
    for (r, row) in rows.iter().enumerate() {
        let row = row.as_array().context("a placement row is a list")?;
        ensure!(row.len() == 4, "a placement row has {} numbers", row.len());
        for (c, value) in row.iter().enumerate() {
            m[r][c] = value.as_f64().filter(|v| v.is_finite()).context("a placement holds a non-finite number")?;
        }
    }
    Ok(Some(Affine { m }))
}
