//! Solids as voxels: which cells a closed triangle mesh fills, and how far each open cell stands
//! from the nearest wall.

/// A box of cubic cells, `h` on a side, its first cell's corner at `origin`.
#[derive(Clone)]
pub struct Grid {
    pub origin: [f64; 3],
    pub h: f64,
    pub n: [usize; 3],
}

impl Grid {
    /// The cells that cover `lo`..`hi`, which must lie on multiples of `h` from `lo`.
    pub fn covering(lo: [f64; 3], hi: [f64; 3], h: f64) -> Grid {
        let n = [0, 1, 2].map(|a| ((hi[a] - lo[a]) / h).round().max(1.) as usize);
        Grid { origin: lo, h, n }
    }

    pub fn len(&self) -> usize {
        self.n[0] * self.n[1] * self.n[2]
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn index(&self, i: usize, j: usize, k: usize) -> usize {
        (k * self.n[1] + j) * self.n[0] + i
    }

    pub fn centre(&self, i: usize, j: usize, k: usize) -> [f64; 3] {
        [
            self.origin[0] + (i as f64 + 0.5) * self.h,
            self.origin[1] + (j as f64 + 0.5) * self.h,
            self.origin[2] + (k as f64 + 0.5) * self.h,
        ]
    }

    /// The cell holding `p`, clamped into the grid.
    pub fn cell(&self, p: [f64; 3]) -> [usize; 3] {
        [0, 1, 2].map(|a| (((p[a] - self.origin[a]) / self.h).floor().max(0.) as usize).min(self.n[a] - 1))
    }
}

/// Which cells of `grid` have their centre inside the closed mesh: one ray along z through each
/// column of centres, filled between its crossings in pairs.
pub fn fill(grid: &Grid, verts: &[[f64; 3]], tris: &[[u32; 3]]) -> Vec<bool> {
    let [nx, ny, nz] = grid.n;
    let mut crossings: Vec<Vec<f32>> = vec![Vec::new(); nx * ny];
    // The rays stand a hair off the cell centres, so none runs along a triangle's edge.
    let (ox, oy) = (grid.origin[0] + 0.5 * grid.h + 1.3e-7, grid.origin[1] + 0.5 * grid.h + 0.7e-7);
    for tri in tris {
        let [a, b, c] = tri.map(|v| verts[v as usize]);
        let area = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]);
        if area.abs() < 1e-12 {
            continue;
        }
        let lo_x = a[0].min(b[0]).min(c[0]);
        let hi_x = a[0].max(b[0]).max(c[0]);
        let lo_y = a[1].min(b[1]).min(c[1]);
        let hi_y = a[1].max(b[1]).max(c[1]);
        let i0 = (((lo_x - ox) / grid.h).ceil().max(0.)) as usize;
        let j0 = (((lo_y - oy) / grid.h).ceil().max(0.)) as usize;
        let i1 = ((hi_x - ox) / grid.h).floor();
        let j1 = ((hi_y - oy) / grid.h).floor();
        if i1 < 0. || j1 < 0. {
            continue;
        }
        let (i1, j1) = ((i1 as usize).min(nx - 1), (j1 as usize).min(ny - 1));
        for j in j0..=j1 {
            let y = oy + j as f64 * grid.h;
            for i in i0..=i1 {
                let x = ox + i as f64 * grid.h;
                let w0 = ((b[0] - x) * (c[1] - y) - (c[0] - x) * (b[1] - y)) / area;
                let w1 = ((c[0] - x) * (a[1] - y) - (a[0] - x) * (c[1] - y)) / area;
                let w2 = 1. - w0 - w1;
                if w0 >= 0. && w1 >= 0. && w2 >= 0. {
                    crossings[j * nx + i].push((w0 * a[2] + w1 * b[2] + w2 * c[2]) as f32);
                }
            }
        }
    }
    let mut solid = vec![false; grid.len()];
    for j in 0..ny {
        for i in 0..nx {
            let column = &mut crossings[j * nx + i];
            column.sort_by(|p, q| p.total_cmp(q));
            for pair in column.chunks_exact(2) {
                let k0 = (((pair[0] as f64 - grid.origin[2]) / grid.h - 0.5).ceil().max(0.)) as usize;
                let k1 = ((pair[1] as f64 - grid.origin[2]) / grid.h - 0.5).floor();
                if k1 < 0. {
                    continue;
                }
                for k in k0..=(k1 as usize).min(nz - 1) {
                    solid[grid.index(i, j, k)] = true;
                }
            }
        }
    }
    solid
}

/// The distance from each open cell's centre to the nearest solid cell's face, in the grid's
/// units of length; zero in the solid cells. Exact for walls that lie on the grid.
pub fn wall_distance(grid: &Grid, solid: &[bool]) -> Vec<f32> {
    let [nx, ny, nz] = grid.n;
    let far = 1e12_f32;
    // Squared distance, in cells, to the nearest solid cell's centre, one axis at a time.
    let mut d: Vec<f32> = solid.iter().map(|&s| if s { 0. } else { far }).collect();
    let longest = nx.max(ny).max(nz);
    let mut line = vec![0f32; longest];
    let mut out = vec![0f32; longest];
    let mut v = vec![0usize; longest];
    let mut z = vec![0f64; longest + 1];
    let mut pass = |d: &mut [f32], count: usize, start: &dyn Fn(usize) -> usize, stride: usize, len: usize| {
        for row in 0..count {
            let base = start(row);
            for q in 0..len {
                line[q] = d[base + q * stride];
            }
            lower_envelope(&line[..len], &mut out[..len], &mut v, &mut z);
            for q in 0..len {
                d[base + q * stride] = out[q];
            }
        }
    };
    pass(&mut d, ny * nz, &|row| row * nx, 1, nx);
    pass(&mut d, nx * nz, &|row| (row / nx) * nx * ny + row % nx, nx, ny);
    pass(&mut d, nx * ny, &|row| row, nx * ny, nz);
    let h = grid.h as f32;
    d.iter().map(|&sq| if sq <= 0. { 0. } else { (sq.sqrt() - 0.5).max(0.5) * h }).collect()
}

/// Felzenszwalb and Huttenlocher's one-dimensional squared-distance transform.
fn lower_envelope(f: &[f32], out: &mut [f32], v: &mut [usize], z: &mut [f64]) {
    let n = f.len();
    let parabola = |q: usize| f[q] as f64 + (q * q) as f64;
    let mut k = 0;
    v[0] = 0;
    z[0] = f64::NEG_INFINITY;
    z[1] = f64::INFINITY;
    for q in 1..n {
        loop {
            let p = v[k];
            let s = (parabola(q) - parabola(p)) / (2. * (q as f64 - p as f64));
            if s <= z[k] && k > 0 {
                k -= 1;
            } else {
                k += 1;
                v[k] = q;
                z[k] = s;
                z[k + 1] = f64::INFINITY;
                break;
            }
        }
    }
    k = 0;
    for (q, slot) in out.iter_mut().enumerate().take(n) {
        while z[k + 1] < q as f64 {
            k += 1;
        }
        let p = v[k];
        let gap = q as f64 - p as f64;
        *slot = (gap * gap + f[p] as f64) as f32;
    }
}
