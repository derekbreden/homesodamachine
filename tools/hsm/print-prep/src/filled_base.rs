//! Gives the slicer a faucet base with closed stock below its mounting face, down to the bed, so
//! it lays no support under the face and prints the courses above it as ordinary inside courses.
//!
//! The base is turned into its print pose, where the mounting face slopes down to the bed. A
//! prism stands on the bed under the face's rim, with the insert recesses' mouths left open so
//! the fill seals no pocket; it is cut a little inside the face's plane and joined to the base.
//! The result goes back to the base's own frame, corners the cut left a hair apart made one.

use crate::mesh::Mesh;
use anyhow::{Context, Result, ensure};
use hsm_manifold::Manifold;
use std::collections::BTreeMap;

/// How far the fill reaches past the mounting face's plane into the base.
const EMBED: f64 = 0.05;
/// How much wider than the base's own mouths the fill leaves the insert recesses open.
const MOUTH_CLEARANCE: f64 = 0.02;
/// The fill's height above the bed, more than the face rises.
const PRISM_HEIGHT: f64 = 40.0;
/// Rim points around the fill's footprint.
const RIM_POINTS: usize = 360;
/// Openings in the mounting face smaller than this are insert recess mouths.
const MOUTH_AREA: f64 = 200.0;
/// Decimal places the result's coordinates are kept to.
const DECIMALS: i32 = 5;

/// The base, in its own frame, with the space under its mounting face filled down to the bed.
/// `tilt_degrees` is the print pose's tilt of the face; `semi` the rim's half-width and half-depth.
pub fn fill(base: &Mesh, tilt_degrees: f64, semi: [f64; 2]) -> Result<Mesh> {
    base.check_closed_single_body("faucet base")?;
    let (s, c) = tilt_degrees.to_radians().sin_cos();
    let turn = |p: [f64; 3]| [p[0], c * p[1] + s * p[2], -s * p[1] + c * p[2]];
    let back = |p: [f64; 3]| [p[0], c * p[1] - s * p[2], s * p[1] + c * p[2]];
    let plate: Vec<[f64; 3]> = base.vertices.iter().map(|p| turn(*p)).collect();
    let bed = plate.iter().map(|p| p[2]).fold(f64::INFINITY, f64::min);

    let ring: Vec<[f64; 2]> = (0..RIM_POINTS)
        .map(|i| {
            let a = std::f64::consts::TAU * i as f64 / RIM_POINTS as f64;
            [semi[0] * a.cos(), semi[1] * a.sin() * c]
        })
        .collect();
    let mut prism = prism_of(&ring, bed, PRISM_HEIGHT)?;
    let mouths = mouths(base)?;
    ensure!(mouths.len() == 3, "expected three insert recess mouths, found {}", mouths.len());
    for (centre, radius) in mouths {
        let hole: Vec<[f64; 2]> = (0..96)
            .map(|i| {
                let a = std::f64::consts::TAU * i as f64 / 96.0;
                [centre[0] + (radius + MOUTH_CLEARANCE) * a.cos(), centre[1] * c + (radius * c + MOUTH_CLEARANCE) * a.sin()]
            })
            .collect();
        prism = prism.difference(&prism_of(&hole, bed - 1.0, PRISM_HEIGHT + 2.0)?);
    }
    // Keep what lies under the face's plane, a little inside the base: CAD z = s y + c z there.
    let (under, _) = prism.split_by_plane([0.0, -s, -c], -EMBED);
    let turned = manifold_of(&plate, &base.faces)?;
    let union = turned.union(&under);
    union.status()?;
    ensure!(union.decompose().len() == 1, "the filled base is not one closed body");
    let (vertices, stride, indices) = union.to_mesh_f64();
    let points: Vec<[f64; 3]> = vertices.chunks(stride).map(|v| [v[0], v[1], v[2]]).collect();
    let (lo, hi) = bounds(&points);
    let (plo, phi) = bounds(&plate);
    for k in 0..3 {
        ensure!((lo[k] - plo[k]).abs() < 1e-5 && (hi[k] - phi[k]).abs() < 1e-5, "the fill moved the base's bounds on axis {k}");
    }
    let scale = 10f64.powi(DECIMALS);
    let mut index: BTreeMap<[i64; 3], usize> = BTreeMap::new();
    let mut out = Vec::new();
    let keys: Vec<[i64; 3]> = points.iter().map(|p| back(*p).map(|v| (v * scale).round() as i64)).collect();
    for key in &keys {
        if !index.contains_key(key) {
            index.insert(*key, 0);
        }
    }
    for (n, (key, slot)) in index.iter_mut().enumerate() {
        *slot = n;
        out.push(key.map(|v| v as f64 / scale));
    }
    let faces: Vec<[usize; 3]> = indices
        .chunks(3)
        .map(|t| [0, 1, 2].map(|i| index[&keys[t[i] as usize]]))
        .filter(|f| f[0] != f[1] && f[1] != f[2] && f[0] != f[2])
        .collect();
    let result = Mesh { vertices: out, faces };
    result.check_closed_single_body("filled base")?;
    Ok(result)
}

/// The base's insert recess mouths: each opening in its mounting face, by centre and radius in
/// the face's plane.
fn mouths(base: &Mesh) -> Result<Vec<([f64; 2], f64)>> {
    let bottom = base.vertices.iter().map(|p| p[2]).fold(f64::INFINITY, f64::min);
    let on: Vec<&[usize; 3]> = base.faces.iter().filter(|f| f.iter().all(|&i| (base.vertices[i][2] - bottom).abs() < 1e-6)).collect();
    let mut uses: BTreeMap<(usize, usize), i32> = BTreeMap::new();
    for f in &on {
        for k in 0..3 {
            let (a, b) = (f[k], f[(k + 1) % 3]);
            *uses.entry((a.min(b), a.max(b))).or_default() += 1;
        }
    }
    let mut next: BTreeMap<usize, Vec<usize>> = BTreeMap::new();
    for (&(a, b), &n) in &uses {
        if n == 1 {
            next.entry(a).or_default().push(b);
            next.entry(b).or_default().push(a);
        }
    }
    let mut seen = std::collections::BTreeSet::new();
    let mut out = Vec::new();
    for &start in next.keys() {
        if seen.contains(&start) {
            continue;
        }
        let mut loop_ = vec![start];
        seen.insert(start);
        let mut at = start;
        loop {
            let Some(&step) = next[&at].iter().find(|v| !seen.contains(*v)) else { break };
            seen.insert(step);
            loop_.push(step);
            at = step;
        }
        let xy: Vec<[f64; 2]> = loop_.iter().map(|&i| [base.vertices[i][0], base.vertices[i][1]]).collect();
        let area = xy.iter().zip(xy.iter().cycle().skip(1)).map(|(a, b)| a[0] * b[1] - b[0] * a[1]).sum::<f64>().abs() / 2.0;
        if area < MOUTH_AREA {
            let n = xy.len() as f64;
            let centre = [xy.iter().map(|p| p[0]).sum::<f64>() / n, xy.iter().map(|p| p[1]).sum::<f64>() / n];
            let radius = xy.iter().map(|p| (p[0] - centre[0]).hypot(p[1] - centre[1])).fold(0.0, f64::max);
            out.push((centre, radius));
        }
    }
    Ok(out)
}

/// A closed prism over a convex outline, standing `height` above `floor`.
fn prism_of(outline: &[[f64; 2]], floor: f64, height: f64) -> Result<Manifold> {
    let n = outline.len();
    let centre = [outline.iter().map(|p| p[0]).sum::<f64>() / n as f64, outline.iter().map(|p| p[1]).sum::<f64>() / n as f64];
    let mut vertices: Vec<[f64; 3]> = Vec::with_capacity(2 * n + 2);
    for z in [floor, floor + height] {
        vertices.extend(outline.iter().map(|p| [p[0], p[1], z]));
    }
    vertices.push([centre[0], centre[1], floor]);
    vertices.push([centre[0], centre[1], floor + height]);
    let (bottom, top) = (2 * n, 2 * n + 1);
    let mut faces = Vec::with_capacity(4 * n);
    for i in 0..n {
        let j = (i + 1) % n;
        faces.extend([[i, j, n + j], [i, n + j, n + i], [bottom, j, i], [top, n + i, n + j]]);
    }
    manifold_of(&vertices, &faces)
}

fn manifold_of(vertices: &[[f64; 3]], faces: &[[usize; 3]]) -> Result<Manifold> {
    let flat: Vec<f64> = vertices.iter().flatten().copied().collect();
    let indices: Vec<u64> = faces.iter().flatten().map(|&i| i as u64).collect();
    Manifold::from_mesh_f64(&flat, 3, &indices).context("a solid Manifold rejects")
}

fn bounds(points: &[[f64; 3]]) -> ([f64; 3], [f64; 3]) {
    let mut lo = [f64::INFINITY; 3];
    let mut hi = [f64::NEG_INFINITY; 3];
    for p in points {
        for k in 0..3 {
            lo[k] = lo[k].min(p[k]);
            hi[k] = hi[k].max(p[k]);
        }
    }
    (lo, hi)
}
