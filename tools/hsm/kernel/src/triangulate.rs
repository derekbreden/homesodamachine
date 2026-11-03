//! Triangles over planar polygons with holes: a constrained Delaunay triangulation of the loops'
//! own points, its triangles kept where an odd number of loops enclose them. No point is added,
//! so a cap meets the walls beside it point for point, and the same loops always give the same
//! triangles.
use crate::math::V2;
use anyhow::{Result, bail, ensure};
use spade::handles::{FixedFaceHandle, FixedVertexHandle, PossiblyOuterTag};
use spade::{ConstrainedDelaunayTriangulation, Point2, Triangulation};
use std::collections::VecDeque;

/// Triangles counterclockwise in the loops' own coordinates, as indices into the loops'
/// points taken one loop after another.
pub fn triangulate(loops: &[Vec<V2>]) -> Result<Vec<[u32; 3]>> {
    let mut cdt = ConstrainedDelaunayTriangulation::<Point2<f64>>::new();
    let total: usize = loops.iter().map(Vec::len).sum();
    let mut handles: Vec<FixedVertexHandle> = Vec::with_capacity(total);
    let mut index_of: Vec<u32> = vec![];
    let mut next = 0u32;
    for lp in loops {
        for p in lp {
            let h = cdt
                // Plane projection can leave an analytically zero coordinate
                // below Spade's exact-predicate floor. Normalize only that
                // insertion coordinate; the source/world vertices stay intact.
                .insert(spade::mitigate_underflow(Point2::new(p.x, p.y)))
                .map_err(|e| anyhow::anyhow!("a profile point at ({}, {}): {e:?}", p.x, p.y))?;
            if index_of.len() <= h.index() {
                index_of.resize(h.index() + 1, u32::MAX);
            }
            if index_of[h.index()] == u32::MAX {
                index_of[h.index()] = next;
            }
            handles.push(h);
            next += 1;
        }
    }
    let mut start = 0;
    for lp in loops {
        let m = lp.len();
        ensure!(m >= 3, "a loop of {m} points bounds nothing");
        for k in 0..m {
            let (a, b) = (handles[start + k], handles[start + (k + 1) % m]);
            if a == b || cdt.exists_constraint(a, b) {
                continue;
            }
            if cdt.try_add_constraint(a, b).is_empty() {
                let (p, q) = (lp[k], lp[(k + 1) % m]);
                bail!(
                    "the profile crosses itself: its edge ({:.6}, {:.6})–({:.6}, {:.6}) cuts another",
                    p.x,
                    p.y,
                    q.x,
                    q.y
                );
            }
        }
        start += m;
    }
    // Inside is an odd count of constraint edges crossed from the outer face.
    let mut parity = vec![u8::MAX; cdt.num_all_faces()];
    let outer = cdt.outer_face().fix();
    parity[outer.index()] = 0;
    let mut queue: VecDeque<FixedFaceHandle<PossiblyOuterTag>> = VecDeque::from([outer]);
    while let Some(f) = queue.pop_front() {
        let p = parity[f.index()];
        let face = cdt.face(f);
        let Some(first) = face.adjacent_edge() else { continue };
        let mut e = first;
        loop {
            let g = e.rev().face().fix();
            if parity[g.index()] == u8::MAX {
                parity[g.index()] = p ^ cdt.is_constraint_edge(e.as_undirected().fix()) as u8;
                queue.push_back(g);
            }
            e = e.next();
            if e == first {
                break;
            }
        }
    }
    let mut out = vec![];
    for face in cdt.inner_faces() {
        if parity[face.fix().index()] == 1 {
            let [a, b, c] = face.vertices();
            out.push([index_of[a.fix().index()], index_of[b.fix().index()], index_of[c.fix().index()]]);
        }
    }
    ensure!(!out.is_empty(), "a profile that encloses nothing");
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::math::v2;

    fn area(loops: &[Vec<V2>], tris: &[[u32; 3]]) -> f64 {
        let pts: Vec<V2> = loops.concat();
        tris.iter()
            .map(|t| {
                let (a, b, c) = (pts[t[0] as usize], pts[t[1] as usize], pts[t[2] as usize]);
                0.5 * (b - a).cross(c - a)
            })
            .sum()
    }

    #[test]
    fn a_square_with_a_hole() {
        let outer = vec![v2(0.0, 0.0), v2(4.0, 0.0), v2(4.0, 4.0), v2(0.0, 4.0)];
        let hole = vec![v2(1.0, 1.0), v2(1.0, 3.0), v2(3.0, 3.0), v2(3.0, 1.0)];
        let loops = vec![outer, hole];
        let tris = triangulate(&loops).unwrap();
        assert!((area(&loops, &tris) - 12.0).abs() < 1e-12);
        assert_eq!(tris.len(), 8);
    }

    #[test]
    fn a_crossing_profile_is_refused() {
        let bow = vec![v2(0.0, 0.0), v2(2.0, 2.0), v2(2.0, 0.0), v2(0.0, 2.0)];
        assert!(triangulate(&[bow]).is_err());
    }
}
