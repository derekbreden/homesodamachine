//! The head map gives the head replay the whole modeled toolhead around the active nozzle: the
//! left-active head's height map, which holds the low parts of its bodies, with the rest of each
//! body folded in from the toolhead model's export.
//!
//! A map is two grids about the active tip, +X to the operator's right and +Y toward the back:
//! the lowest modeled point of the head over each cell, and the active nozzle's own bodies apart.
//! A cell nothing hangs over is infinite.

use crate::course_field::distance;
use crate::npz;
use anyhow::{ensure, Context, Result};
use std::path::Path;

/// The whole modeled head over the active tip, which the head replay reads.
pub const FULL_HEAD_MAP: &str = "tools/hsm/print-prep/faucet-underside/left-active-full-height.npz";
/// The toolhead model's bodies that are the active nozzle, which the map keeps apart.
const NOZZLE_BODIES: &str = "Left nozzle";
/// The height above the tip from which a body's triangles fold in; the left-active map holds
/// the triangles that reach below it.
const FOLD_FROM_Z: f64 = 30.0;

pub struct HeadMap {
    /// The head's lowest point over each cell, row by row from `y0`.
    pub head: Vec<f64>,
    /// The active nozzle's lowest point over each cell, on the same grid.
    pub nozzle: Vec<f64>,
    pub rows: usize,
    pub cols: usize,
    /// The first cell's centre and the grid's pitch, in millimetres from the tip.
    pub x0: f64,
    pub y0: f64,
    pub step: f64,
}

impl HeadMap {
    pub fn read(path: &Path) -> Result<HeadMap> {
        let arrays = npz::read_arrays(path)?;
        let get = |name: &str| arrays.get(name).with_context(|| format!("{} has no {name}", path.display()));
        let scalar = |name: &str| -> Result<f64> {
            get(name)?.f64().and_then(|v| v.first().copied()).with_context(|| format!("{name} in {} is a number", path.display()))
        };
        let (head, nozzle) = (get("H")?, get("N")?);
        ensure!(head.shape.len() == 2 && nozzle.shape == head.shape, "{}'s head and nozzle grids differ", path.display());
        Ok(HeadMap {
            head: head.f64().context("H holds numbers")?.to_vec(),
            nozzle: nozzle.f64().context("N holds numbers")?.to_vec(),
            rows: head.shape[0],
            cols: head.shape[1],
            x0: scalar("x0")?,
            y0: scalar("y0")?,
            step: scalar("step")?,
        })
    }

    pub fn write(&self, path: &Path) -> Result<()> {
        let shape = [self.rows, self.cols];
        npz::write_f64(path, &[
            ("H", &shape, &self.head),
            ("N", &shape, &self.nozzle),
            ("step", &[], &[self.step]),
            ("x0", &[], &[self.x0]),
            ("y0", &[], &[self.y0]),
        ])
    }

    /// Folds in the toolhead model's export at `toolhead`: every triangle of a body other than
    /// the nozzle's that lies wholly above the fold height, sampled finer than the grid and kept
    /// in the cell nearest each sample where it hangs lowest.
    pub fn fold(&mut self, toolhead: &Path) -> Result<()> {
        let arrays = npz::read_arrays(toolhead)?;
        let get = |name: &str| arrays.get(name).with_context(|| format!("{} has no {name}", toolhead.display()));
        let names: Vec<String> = serde_json::from_slice(get("names")?.bytes().context("the body names are text")?)?;
        for (index, name) in names.iter().enumerate() {
            if name.starts_with(NOZZLE_BODIES) {
                continue;
            }
            let vertices = get(&format!("V{index}"))?.f64().with_context(|| format!("{name}'s vertices are numbers"))?;
            let faces = get(&format!("T{index}"))?.indices().with_context(|| format!("{name}'s faces are indices"))?;
            let corner = |i: usize| -> Result<[f64; 3]> {
                vertices.get(3 * i..3 * i + 3).map(|v| [v[0], v[1], v[2]]).with_context(|| format!("{name} has no vertex {i}"))
            };
            for face in faces.chunks_exact(3) {
                let [a, b, c] = [corner(face[0])?, corner(face[1])?, corner(face[2])?];
                if a[2].min(b[2]).min(c[2]) < FOLD_FROM_Z {
                    continue;
                }
                let span = distance(b, a).max(distance(c, a)).max(distance(c, b));
                let size = ((span / (self.step / 2.0)).ceil() as usize).max(2);
                for row in 0..=size {
                    let v = row as f64 / size as f64;
                    for column in 0..=size {
                        let u = column as f64 / size as f64;
                        if u + v > 1.0 + 1e-9 {
                            continue;
                        }
                        let p: [f64; 3] = std::array::from_fn(|k| a[k] + u * (b[k] - a[k]) + v * (c[k] - a[k]));
                        let x = ((p[0] - self.x0) / self.step).round_ties_even();
                        let y = ((p[1] - self.y0) / self.step).round_ties_even();
                        if x < 0.0 || y < 0.0 || x >= self.cols as f64 || y >= self.rows as f64 {
                            continue;
                        }
                        let lowest = &mut self.head[y as usize * self.cols + x as usize];
                        *lowest = lowest.min(p[2]);
                    }
                }
            }
        }
        Ok(())
    }
}
