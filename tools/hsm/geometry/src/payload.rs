use anyhow::{Context, Result, bail, ensure};
use manifold_csg::Manifold;
use parry3d_f64::{math::Point, shape::TriMesh};
use serde::Deserialize;
use sha2::{Digest, Sha256};
use std::sync::{Mutex, OnceLock};

pub const PAYLOAD_VERSION: u32 = 3;

#[derive(Deserialize)]
pub struct Header {
    pub v: u32,
    pub meshes: Vec<Entry>,
    pub src: Option<String>,
    pub cut: Option<serde_json::Value>,
}

#[derive(Deserialize)]
pub struct Entry {
    pub name: String,
    pub color: Option<[f64; 3]>,
    pub pos: [usize; 2],
    pub nrm: [usize; 2],
    pub idx: [usize; 2],
    pub fac: [usize; 2],
}

pub struct Mesh {
    pub name: String,
    pub color: Option<[f64; 3]>,
    pub shape: TriMesh,
    /// Inclusive triangle ranges, in the same order as the viewer's face IDs.
    pub faces: Vec<[u32; 2]>,
    pub(crate) solid: OnceLock<Result<Mutex<Manifold>, String>>,
}

pub struct Payload {
    pub digest: String,
    pub source: Option<String>,
    pub cut: Option<String>,
    pub meshes: Vec<Mesh>,
}

fn array(blob: &[u8], [offset, count]: [usize; 2]) -> Result<&[u8]> {
    ensure!(offset % 4 == 0, "unaligned payload array");
    let end = count
        .checked_mul(4)
        .and_then(|n| offset.checked_add(n))
        .context("payload array overflow")?;
    blob.get(offset..end)
        .context("payload array extends beyond the file")
}

pub fn decode(bytes: &[u8]) -> Result<Payload> {
    ensure!(bytes.len() >= 4, "truncated payload header");
    let size = u32::from_le_bytes(bytes[..4].try_into()?) as usize;
    let end = size.checked_add(4).context("payload header overflow")?;
    let header: Header =
        serde_json::from_slice(bytes.get(4..end).context("truncated payload header")?)?;
    ensure!(
        header.v == PAYLOAD_VERSION,
        "unsupported payload version {}; expected {}",
        header.v,
        PAYLOAD_VERSION
    );
    ensure!(end % 4 == 0, "unaligned payload header");
    let blob = &bytes[end..];
    let mut meshes = Vec::with_capacity(header.meshes.len());
    for (i, e) in header.meshes.into_iter().enumerate() {
        let floats = |range| -> Result<Vec<f64>> {
            array(blob, range)?
                .chunks_exact(4)
                .map(|b| {
                    let n = f32::from_le_bytes(b.try_into()?) as f64;
                    ensure!(n.is_finite(), "non-finite coordinate in mesh {i}");
                    Ok(n)
                })
                .collect()
        };
        let ints = |range| -> Result<Vec<u32>> {
            Ok(array(blob, range)?
                .chunks_exact(4)
                .map(|b| u32::from_le_bytes(b.try_into().unwrap()))
                .collect())
        };
        ensure!(
            e.pos[1] % 3 == 0 && e.idx[1] % 3 == 0 && e.fac[1] % 2 == 0,
            "invalid array lengths in mesh {i}"
        );
        ensure!(
            e.nrm[1] == e.pos[1],
            "normal count differs from vertex count in mesh {i}"
        );
        array(blob, e.nrm)?;
        let pos = floats(e.pos)?;
        let vertices: Vec<_> = pos
            .chunks_exact(3)
            .map(|p| Point::new(p[0], p[1], p[2]))
            .collect();
        let indices = ints(e.idx)?;
        ensure!(
            indices.iter().all(|&n| (n as usize) < vertices.len()),
            "vertex index outside mesh {i}"
        );
        let indices: Vec<_> = indices
            .chunks_exact(3)
            .map(|v| [v[0], v[1], v[2]])
            .collect();
        let faces: Vec<_> = ints(e.fac)?.chunks_exact(2).map(|v| [v[0], v[1]]).collect();
        ensure!(
            faces
                .iter()
                .all(|v| v[0] <= v[1] && (v[1] as usize) < indices.len()),
            "invalid face range in mesh {i}"
        );
        ensure!(
            faces.windows(2).all(|w| w[0][1] < w[1][0]),
            "overlapping or unordered face ranges in mesh {i}"
        );
        if vertices.is_empty() || indices.is_empty() {
            bail!("empty mesh {i} ({})", e.name);
        }
        let shape =
            TriMesh::new(vertices, indices).map_err(|err| anyhow::anyhow!("mesh {i}: {err}"))?;
        meshes.push(Mesh {
            name: e.name,
            color: e.color,
            shape,
            faces,
            solid: OnceLock::new(),
        });
    }
    Ok(Payload {
        digest: format!("{:x}", Sha256::digest(bytes)),
        source: header.src,
        cut: header.cut.map(|v| v.to_string()),
        meshes,
    })
}
