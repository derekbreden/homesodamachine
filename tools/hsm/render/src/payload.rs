//! The `.step.mesh` payload as flat arrays: what the /3d viewer's `decodeMeshPayload` reads,
//! without the collision trees `hsm_geometry::payload::decode` builds for queries.

use anyhow::{Context, Result, ensure};
use serde::Deserialize;

/// Versions the viewer decodes (`MESH_PAYLOAD_VERSIONS` in web/public/js/viewer/step.js).
const VERSIONS: [u32; 2] = [2, 3];

#[derive(Deserialize)]
struct Header {
    v: u32,
    meshes: Vec<Entry>,
}

#[derive(Deserialize)]
struct Entry {
    name: String,
    color: Option<[f64; 3]>,
    pos: [usize; 2],
    nrm: [usize; 2],
    idx: [usize; 2],
    fac: [usize; 2],
    col: Option<[usize; 2]>,
    uv: Option<[usize; 2]>,
}

pub struct RawMesh {
    pub name: String,
    /// Linear RGB, as `_materials.linear` wrote it.
    pub color: Option<[f64; 3]>,
    pub positions: Vec<[f32; 3]>,
    pub normals: Vec<[f32; 3]>,
    pub colors: Option<Vec<[f32; 3]>>,
    pub uv: Option<Vec<[f32; 2]>>,
    pub indices: Vec<u32>,
    /// Inclusive triangle ranges, one per B-rep face.
    pub faces: Vec<[u32; 2]>,
}

fn words(blob: &[u8], [offset, count]: [usize; 2]) -> Result<&[u8]> {
    ensure!(offset % 4 == 0, "unaligned payload array");
    let end = count
        .checked_mul(4)
        .and_then(|n| offset.checked_add(n))
        .context("payload array overflow")?;
    blob.get(offset..end)
        .context("payload array extends beyond the file")
}

fn f32s(bytes: &[u8]) -> impl Iterator<Item = f32> + '_ {
    bytes
        .chunks_exact(4)
        .map(|b| f32::from_le_bytes([b[0], b[1], b[2], b[3]]))
}

fn u32s(bytes: &[u8]) -> impl Iterator<Item = u32> + '_ {
    bytes
        .chunks_exact(4)
        .map(|b| u32::from_le_bytes([b[0], b[1], b[2], b[3]]))
}

fn triples(bytes: &[u8]) -> Vec<[f32; 3]> {
    let flat: Vec<f32> = f32s(bytes).collect();
    flat.chunks_exact(3).map(|c| [c[0], c[1], c[2]]).collect()
}

pub fn decode(bytes: &[u8]) -> Result<Vec<RawMesh>> {
    ensure!(bytes.len() >= 4, "truncated payload header");
    let size = u32::from_le_bytes(bytes[..4].try_into()?) as usize;
    let end = size.checked_add(4).context("payload header overflow")?;
    let header: Header =
        serde_json::from_slice(bytes.get(4..end).context("truncated payload header")?)?;
    ensure!(
        VERSIONS.contains(&header.v),
        "unsupported payload version {}",
        header.v
    );
    ensure!(end % 4 == 0, "unaligned payload header");
    let blob = &bytes[end..];
    header
        .meshes
        .into_iter()
        .enumerate()
        .map(|(i, e)| {
            ensure!(
                e.pos[1] % 3 == 0 && e.idx[1] % 3 == 0 && e.fac[1] % 2 == 0 && e.nrm[1] == e.pos[1],
                "invalid array lengths in mesh {i} ({})",
                e.name
            );
            let positions = triples(words(blob, e.pos)?);
            ensure!(
                positions.iter().flatten().all(|v| v.is_finite()),
                "non-finite coordinate in mesh {i} ({})",
                e.name
            );
            let normals = triples(words(blob, e.nrm)?);
            let colors = e.col.map(|range| -> Result<_> {
                ensure!(range[1] == e.pos[1], "invalid vertex colours in mesh {i} ({})", e.name);
                Ok(triples(words(blob, range)?))
            }).transpose()?;
            let uv = e.uv.map(|range| -> Result<_> {
                ensure!(range[1] == positions.len() * 2, "invalid UVs in mesh {i} ({})", e.name);
                let flat: Vec<f32> = f32s(words(blob, range)?).collect();
                Ok(flat.chunks_exact(2).map(|p| [p[0], p[1]]).collect())
            }).transpose()?;
            let indices: Vec<u32> = u32s(words(blob, e.idx)?).collect();
            ensure!(
                indices.iter().all(|&n| (n as usize) < positions.len()),
                "vertex index outside mesh {i} ({})",
                e.name
            );
            let flat: Vec<u32> = u32s(words(blob, e.fac)?).collect();
            let faces = flat.chunks_exact(2).map(|c| [c[0], c[1]]).collect();
            Ok(RawMesh {
                name: e.name,
                color: e.color,
                positions,
                normals,
                colors,
                uv,
                indices,
                faces,
            })
        })
        .collect()
}
