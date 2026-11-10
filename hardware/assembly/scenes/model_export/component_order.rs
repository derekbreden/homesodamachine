//! Preserve the existing colored-compound leaf order while retaining kernel fine geometry.
use anyhow::{Context, Result, ensure};
use hsm_kernel::Solid;

const ID: [[f64; 4]; 3] = [[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.]];
fn point(frame: &[[f64; 4]; 3], p: [f64; 3]) -> [f64; 3] {
    std::array::from_fn(|r| (0..3).map(|c| frame[r][c] * p[c]).sum::<f64>() + frame[r][3])
}
fn bounds(solid: &Solid, frame: &[[f64; 4]; 3]) -> ([f64; 3], [f64; 3]) {
    let mut lo = [f64::INFINITY; 3];
    let mut hi = [f64::NEG_INFINITY; 3];
    for p in solid.verts() {
        let p = point(frame, [p.x, p.y, p.z]);
        for c in 0..3 {
            lo[c] = lo[c].min(p[c]);
            hi[c] = hi[c].max(p[c]);
        }
    }
    (lo, hi)
}
/// Partition with the kernel and retain the old native reader's component numbering.
/// The native representation supplies order only: returned vertices/records are the
/// unchanged kernel components, in their original source frame.
pub fn in_frame(solid: &Solid, frame: &[[f64; 4]; 3]) -> Result<Vec<Solid>> {
    let parts = solid.components();
    if parts.len() < 2 {
        return Ok(parts);
    }
    let vertices = solid
        .verts()
        .iter()
        .map(|p| [p.x, p.y, p.z].map(hsm_kernel::rule::snap))
        .collect();
    let proxy = hsm_geometry::payload::Mesh::from_arrays(
        "component order",
        vertices,
        solid.tris().to_vec(),
    )?;
    let transform: [f64; 12] = std::array::from_fn(|i| frame[i % 3][i / 3]);
    let native = proxy.solid()?.transform(&transform);
    let native_parts: Vec<_> = native
        .decompose()
        .into_iter()
        .filter(|p| p.volume() > 0.)
        .collect();
    ensure!(
        native_parts.len() == parts.len(),
        "component partitions differ"
    );
    let boxes: Vec<_> = parts.iter().map(|p| bounds(p, frame)).collect();
    let mut remaining: Vec<Option<Solid>> = parts.into_iter().map(Some).collect();
    let mut result = Vec::new();
    for part in native_parts {
        let (lo, hi) = part.bounds().context("component bounds")?;
        let best = remaining
            .iter()
            .enumerate()
            .filter(|(_, p)| p.is_some())
            .min_by(|(a, _), (b, _)| {
                let error = |i: usize| {
                    (0..3)
                        .map(|c| {
                            (boxes[i].0[c] - lo[c])
                                .abs()
                                .max((boxes[i].1[c] - hi[c]).abs())
                        })
                        .fold(0., f64::max)
                };
                error(*a).total_cmp(&error(*b))
            })
            .map(|(i, _)| i)
            .context("component correspondence")?;
        result.push(remaining[best].take().unwrap());
    }
    Ok(result)
}
/// A source which is already in its installed frame.
pub fn ordered(solid: &Solid) -> Result<Vec<Solid>> {
    in_frame(solid, &ID)
}
