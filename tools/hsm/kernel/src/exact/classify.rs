//! Exact winding traces at a patch sample, with symbolic side and ray perturbations.
use super::meet::edge_plane;
use super::{Integer, Mesh, Plane, Point, Result, Sign};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Kind {
    Union,
    Cut,
    Intersect,
}

impl Kind {
    fn truth(self, winding: &[i32]) -> bool {
        match self {
            Self::Union => winding.iter().any(|&w| w > 0),
            Self::Cut => {
                winding.first().is_some_and(|&w| w > 0) && winding[1..].iter().all(|&w| w <= 0)
            }
            Self::Intersect => winding.iter().all(|&w| w > 0),
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct Decision {
    pub(crate) emit: bool,
    pub(crate) flip: bool,
}

struct RayTriangle {
    support: usize,
    edges: [Plane; 3],
    orientation: Sign,
}

pub(crate) struct RayMesh<'a> {
    mesh: &'a Mesh,
    triangles: Vec<RayTriangle>,
}

/// Evaluate at `p + side * delta * normal + epsilon * Y + epsilon^2 * Z`, where
/// `delta` dominates `epsilon` and both are positive infinitesimals. Each expression is linear
/// in the ray origin, so its sign is the first nonzero coefficient. Positive homogeneous
/// weights do not affect the individual coefficient signs.
fn symbolic(plane: &Plane, point: &Point, normal: &[Integer; 3], side: Sign) -> Sign {
    let base = plane.evaluate(point).sign();
    if base != Sign::Zero {
        return base;
    }
    let delta = (0..3)
        .fold(Integer::ZERO, |sum, i| {
            sum.add(&plane.coefficients[i].mul(&normal[i]))
        })
        .sign();
    if delta != Sign::Zero {
        return if side == Sign::Negative {
            delta.reversed()
        } else {
            delta
        };
    }
    for axis in [1, 2] {
        let sign = plane.coefficients[axis].sign();
        if sign != Sign::Zero {
            return sign;
        }
    }
    Sign::Zero
}

impl<'a> RayMesh<'a> {
    pub(crate) fn new(mesh: &'a Mesh) -> Result<Self> {
        let mut triangles = vec![];
        for triangle in &mesh.triangles {
            let orientation = mesh.planes[triangle.support].coefficients[0].sign();
            if orientation == Sign::Zero {
                continue;
            }
            let [a, b, c] = triangle.corners.map(|i| &mesh.points[i as usize]);
            triangles.push(RayTriangle {
                support: triangle.support,
                edges: [
                    edge_plane(a, b, 0)?,
                    edge_plane(b, c, 0)?,
                    edge_plane(c, a, 0)?,
                ],
                orientation,
            });
        }
        Ok(Self { mesh, triangles })
    }

    pub(crate) fn winding(&self, point: &Point, normal: &[Integer; 3], side: Sign) -> Result<i32> {
        let mut winding = 0_i32;
        for triangle in &self.triangles {
            if triangle
                .edges
                .iter()
                .any(|edge| symbolic(edge, point, normal, side) != triangle.orientation)
            {
                continue;
            }
            let ahead = symbolic(&self.mesh.planes[triangle.support], point, normal, side);
            if ahead == triangle.orientation.reversed() {
                let increment = if triangle.orientation == Sign::Positive {
                    1
                } else {
                    -1
                };
                winding = winding
                    .checked_add(increment)
                    .ok_or(super::Error::Overflow)?;
            }
        }
        Ok(winding)
    }
}

/// Classification assumes each input is the oriented boundary of a regular closed solid.
/// A patch's own operand is outside in front and inside behind. All other windings are traced
/// against input triangles, and the first operand at a coincident boundary emits that patch.
pub(crate) fn classify(
    kind: Kind,
    own: usize,
    point: &Point,
    support: &Plane,
    meshes: &[RayMesh<'_>],
) -> Result<Decision> {
    let normal = std::array::from_fn(|i| support.coefficients[i].clone());
    let (mut plus, mut minus) = (vec![0; meshes.len()], vec![0; meshes.len()]);
    for (operand, mesh) in meshes.iter().enumerate() {
        if operand == own {
            minus[operand] = 1;
        } else {
            plus[operand] = mesh.winding(point, &normal, Sign::Positive)?;
            minus[operand] = mesh.winding(point, &normal, Sign::Negative)?;
        }
    }
    let (front, back) = (kind.truth(&plus), kind.truth(&minus));
    let emit = front != back && (0..own).all(|i| plus[i] == minus[i]);
    Ok(Decision {
        emit,
        flip: emit && !back,
    })
}

#[cfg(test)]
mod tests {
    use super::super::Origin;
    use super::*;

    pub(super) fn cube(x: f64) -> Mesh {
        let points = [
            [x, 0.0, 0.0],
            [x + 1.0, 0.0, 0.0],
            [x + 1.0, 1.0, 0.0],
            [x, 1.0, 0.0],
            [x, 0.0, 1.0],
            [x + 1.0, 0.0, 1.0],
            [x + 1.0, 1.0, 1.0],
            [x, 1.0, 1.0],
        ];
        let triangles = [
            [0, 2, 1],
            [0, 3, 2],
            [4, 5, 6],
            [4, 6, 7],
            [0, 1, 5],
            [0, 5, 4],
            [3, 7, 6],
            [3, 6, 2],
            [0, 4, 7],
            [0, 7, 3],
            [1, 2, 6],
            [1, 6, 5],
        ];
        Mesh::from_binary64(
            &points,
            &triangles,
            &vec![
                Origin {
                    operand: 0,
                    face: 0
                };
                triangles.len()
            ],
        )
        .unwrap()
    }

    #[test]
    fn winding_resolves_face_diagonals_vertices_and_both_surface_sides() {
        let cube = cube(0.0);
        let rays = RayMesh::new(&cube).unwrap();
        let normal = [
            Integer::from_i128(1),
            Integer::from_i128(1),
            Integer::from_i128(1),
        ];
        for (coords, expected) in [
            ([0.5, 0.5, 0.5], 1),
            ([-1.0, 0.5, 0.5], 0),
            ([2.0, 0.5, 0.5], 0),
        ] {
            let point = Point::from_binary64(coords).unwrap();
            assert_eq!(
                rays.winding(&point, &normal, Sign::Positive).unwrap(),
                expected
            );
            assert_eq!(
                rays.winding(&point, &normal, Sign::Negative).unwrap(),
                expected
            );
        }
        let point = Point::from_binary64([0.0; 3]).unwrap();
        assert_eq!(rays.winding(&point, &normal, Sign::Positive).unwrap(), 1);
        assert_eq!(rays.winding(&point, &normal, Sign::Negative).unwrap(), 0);
    }

    #[test]
    fn coincident_operands_emit_one_boundary() {
        let cube = cube(0.0);
        let rays = [RayMesh::new(&cube).unwrap(), RayMesh::new(&cube).unwrap()];
        let point = Point::from_binary64([1.0, 0.5, 0.5]).unwrap();
        let support = Plane::new([1, 0, 0, -1].map(Integer::from_i128)).unwrap();
        for kind in [Kind::Union, Kind::Intersect] {
            assert_eq!(
                classify(kind, 0, &point, &support, &rays).unwrap(),
                Decision {
                    emit: true,
                    flip: false
                }
            );
            assert_eq!(
                classify(kind, 1, &point, &support, &rays).unwrap(),
                Decision {
                    emit: false,
                    flip: false
                }
            );
        }
        assert!(
            !classify(Kind::Cut, 0, &point, &support, &rays)
                .unwrap()
                .emit
        );
    }

    #[test]
    fn a_stacked_union_drops_the_interface_and_a_resting_cut_keeps_it() {
        let (a, b) = (cube(0.0), cube(1.0));
        let rays = [RayMesh::new(&a).unwrap(), RayMesh::new(&b).unwrap()];
        let point = Point::from_binary64([1.0, 0.5, 0.5]).unwrap();
        let support = Plane::new([1, 0, 0, -1].map(Integer::from_i128)).unwrap();
        assert!(
            !classify(Kind::Union, 0, &point, &support, &rays)
                .unwrap()
                .emit
        );
        assert_eq!(
            classify(Kind::Cut, 0, &point, &support, &rays).unwrap(),
            Decision {
                emit: true,
                flip: false
            }
        );
        assert!(
            !classify(Kind::Intersect, 0, &point, &support, &rays)
                .unwrap()
                .emit
        );
    }
}
