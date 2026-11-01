//! Deterministic closed-bounds sweep. Every cross-operand candidate appears once.
use super::{Mesh, Point, Result};
use std::cmp::Ordering;

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub(crate) struct Pair {
    pub(crate) a: (usize, usize),
    pub(crate) b: (usize, usize),
}

#[derive(Clone, Copy)]
struct Bound<'a> {
    operand: usize,
    triangle: usize,
    low: [&'a Point; 3],
    high: [&'a Point; 3],
}

pub(crate) fn pairs(meshes: &[&Mesh]) -> Result<Vec<Pair>> {
    let mut bounds = vec![];
    for (operand, mesh) in meshes.iter().enumerate() {
        for (triangle, tri) in mesh.triangles.iter().enumerate() {
            let points = tri.corners.map(|i| &mesh.points[i as usize]);
            let (mut low, mut high) = ([points[0]; 3], [points[0]; 3]);
            for point in points.iter().skip(1) {
                for axis in 0..3 {
                    if point.cmp_axis(low[axis], axis)? == Ordering::Less {
                        low[axis] = point;
                    }
                    if point.cmp_axis(high[axis], axis)? == Ordering::Greater {
                        high[axis] = point;
                    }
                }
            }
            bounds.push(Bound {
                operand,
                triangle,
                low,
                high,
            });
        }
    }
    // Axis zero is a fixed valid projection, so this comparator cannot fail.
    bounds.sort_by(|a, b| {
        a.low[0]
            .cmp_axis(b.low[0], 0)
            .unwrap()
            .then_with(|| (a.operand, a.triangle).cmp(&(b.operand, b.triangle)))
    });
    let mut active: Vec<Vec<Bound<'_>>> = vec![vec![]; meshes.len()];
    let mut out = vec![];
    for bound in bounds {
        for (operand, bucket) in active.iter_mut().enumerate() {
            bucket.retain(|old| old.high[0].cmp_axis(bound.low[0], 0).unwrap() != Ordering::Less);
            if operand == bound.operand {
                continue;
            }
            for old in bucket.iter() {
                let mut overlap = true;
                for axis in 1..3 {
                    if old.high[axis].cmp_axis(bound.low[axis], axis)? == Ordering::Less
                        || bound.high[axis].cmp_axis(old.low[axis], axis)? == Ordering::Less
                    {
                        overlap = false;
                        break;
                    }
                }
                if overlap {
                    let (a, b) = ((old.operand, old.triangle), (bound.operand, bound.triangle));
                    out.push(if a < b {
                        Pair { a, b }
                    } else {
                        Pair { a: b, b: a }
                    });
                }
            }
        }
        active[bound.operand].push(bound);
    }
    out.sort_unstable();
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::super::Origin;
    use super::*;

    fn mesh(offset: f64) -> Mesh {
        Mesh::from_binary64(
            &[
                [offset, 0.0, 0.0],
                [offset + 1.0, 0.0, 0.0],
                [offset, 1.0, 0.0],
            ],
            &[[0, 1, 2]],
            &[Origin {
                operand: 0,
                face: 0,
            }],
        )
        .unwrap()
    }

    #[test]
    fn closed_bounds_include_touches_once_and_exclude_distant_operands() {
        let (a, b, c) = (mesh(0.0), mesh(1.0), mesh(3.0));
        assert_eq!(
            pairs(&[&a, &b, &c]).unwrap(),
            [Pair {
                a: (0, 0),
                b: (1, 0)
            }]
        );
        assert_eq!(
            pairs(&[&a, &a, &a]).unwrap(),
            [
                Pair {
                    a: (0, 0),
                    b: (1, 0)
                },
                Pair {
                    a: (0, 0),
                    b: (2, 0)
                },
                Pair {
                    a: (1, 0),
                    b: (2, 0)
                }
            ]
        );
    }
}
