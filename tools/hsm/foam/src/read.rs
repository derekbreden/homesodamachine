//! What a finished run says: how high, how deep and how full the foam stands in a box of the
//! cavity over time, and the run packed for the page that draws it.
use crate::voxel::Grid;
use anyhow::Result;
use flate2::{Compression, write::GzEncoder};
use std::io::Write;

/// The open cells of a box, layer by layer along `up`, lowest first: each cell's arrival time.
fn layers(grid: &Grid, arrival: &[f32], up: usize, region: [[f64; 3]; 2]) -> Vec<Vec<f32>> {
    let lo = grid.cell(region[0]);
    let hi = grid.cell([region[1][0] - 1e-6, region[1][1] - 1e-6, region[1][2] - 1e-6]);
    let (a, b) = ((up + 1) % 3, (up + 2) % 3);
    let mut out = vec![];
    for layer in lo[up]..=hi[up] {
        let mut cells = vec![];
        for p in lo[a]..=hi[a] {
            for q in lo[b]..=hi[b] {
                let mut c = [0; 3];
                c[up] = layer;
                c[a] = p;
                c[b] = q;
                let t = arrival[grid.index(c[0], c[1], c[2])];
                if !t.is_nan() {
                    cells.push(t);
                }
            }
        }
        out.push(cells);
    }
    out
}

fn share(cells: &[f32], t: f32) -> f64 {
    if cells.is_empty() {
        return 0.;
    }
    cells.iter().filter(|&&a| a <= t).count() as f64 / cells.len() as f64
}

/// How high the foam stands in the box at each time, from the box's floor: the top of the
/// highest layer that is at least half foam with every layer under it.
pub fn height(grid: &Grid, arrival: &[f32], up: usize, region: [[f64; 3]; 2], times: &[f64]) -> Vec<f64> {
    let layers = layers(grid, arrival, up, region);
    times
        .iter()
        .map(|&t| {
            let reached = layers.iter().take_while(|cells| share(cells, t as f32) >= 0.5).count();
            reached as f64 * grid.h
        })
        .collect()
}

/// How far down from the box's top the foam reaches at each time.
pub fn reach(grid: &Grid, arrival: &[f32], up: usize, region: [[f64; 3]; 2], times: &[f64]) -> Vec<f64> {
    let layers = layers(grid, arrival, up, region);
    times
        .iter()
        .map(|&t| {
            let reached = layers.iter().rev().take_while(|cells| share(cells, t as f32) >= 0.5).count();
            reached as f64 * grid.h
        })
        .collect()
}

/// The share of the box's open cells that are foam at each time.
pub fn fill(grid: &Grid, arrival: &[f32], up: usize, region: [[f64; 3]; 2], times: &[f64]) -> Vec<f64> {
    let cells: Vec<f32> = layers(grid, arrival, up, region).concat();
    times.iter().map(|&t| share(&cells, t as f32)).collect()
}

/// The box's open volume, mm³.
pub fn open_volume(grid: &Grid, arrival: &[f32], up: usize, region: [[f64; 3]; 2]) -> f64 {
    layers(grid, arrival, up, region).iter().map(Vec::len).sum::<usize>() as f64 * grid.h.powi(3)
}

/// The time the field's bytes count from, and the seconds each count is worth.
pub struct Clock {
    pub start: f64,
    pub step: f64,
}

pub const NEVER: u8 = 255;

/// Arrival times as one byte a cell for the page: counts of `clock.step` from `clock.start`,
/// `NEVER` where no foam comes. Walls take the earliest time of the open cells they touch, so
/// the drawn foam meets them.
pub fn pack(grid: &Grid, arrival: &[f32], clock: &Clock) -> Vec<u8> {
    let byte = |t: f32| {
        if !t.is_finite() {
            NEVER
        } else {
            (((t as f64 - clock.start) / clock.step).ceil().clamp(0., 254.)) as u8
        }
    };
    let mut field: Vec<u8> = arrival.iter().map(|&t| if t.is_nan() { NEVER } else { byte(t) }).collect();
    let [nx, ny, nz] = grid.n;
    let stride = [1, nx, nx * ny];
    for _ in 0..2 {
        let before = field.clone();
        for k in 0..nz {
            for j in 0..ny {
                for i in 0..nx {
                    let g = grid.index(i, j, k);
                    if !arrival[g].is_nan() {
                        continue;
                    }
                    let ijk = [i, j, k];
                    let dims = [nx, ny, nz];
                    let mut earliest = before[g];
                    for a in 0..3 {
                        if ijk[a] > 0 {
                            earliest = earliest.min(before[g - stride[a]]);
                        }
                        if ijk[a] + 1 < dims[a] {
                            earliest = earliest.min(before[g + stride[a]]);
                        }
                    }
                    field[g] = earliest;
                }
            }
        }
    }
    field
}

pub fn gzip(bytes: &[u8]) -> Result<Vec<u8>> {
    let mut encoder = GzEncoder::new(Vec::new(), Compression::best());
    encoder.write_all(bytes)?;
    Ok(encoder.finish()?)
}
