//! Exact state retained across booleans and affine maps. File conversion is a separate boundary.
use super::point::{binary64_parts, determinant3};
use super::{Error, Integer, Plane, Point, Result, Sign};
use std::collections::BTreeMap;

#[derive(Clone, Debug)]
pub(crate) struct Affine {
    matrix: [[Integer; 4]; 4],
}

fn cofactor(matrix: &[[Integer; 4]; 4], row: usize, col: usize) -> Integer {
    let rows: [usize; 3] = std::array::from_fn(|i| i + usize::from(i >= row));
    let cols: [usize; 3] = std::array::from_fn(|i| i + usize::from(i >= col));
    let minor = rows.map(|i| cols.map(|j| &matrix[i][j]));
    let value = determinant3(minor);
    if (row + col) % 2 == 0 {
        value
    } else {
        value.negated()
    }
}

impl Affine {
    /// Every finite coefficient enters with exactly its binary64 value.
    pub(crate) fn from_binary64(rows: [[f64; 4]; 3]) -> Result<Self> {
        let mut parts = [[(0_i128, 0_i32); 4]; 3];
        let mut base = 0;
        for i in 0..3 {
            for j in 0..4 {
                parts[i][j] = binary64_parts(rows[i][j])?;
                base = base.min(parts[i][j].1);
            }
        }
        let mut matrix = std::array::from_fn(|_| std::array::from_fn(|_| Integer::ZERO));
        for i in 0..3 {
            for j in 0..4 {
                let (mantissa, exponent) = parts[i][j];
                matrix[i][j] = Integer::from_i128(mantissa).shl((exponent - base) as usize);
            }
        }
        matrix[3][3] = Integer::from_i128(1).shl((-base) as usize);
        let out = Self { matrix };
        out.orientation()?;
        Ok(out)
    }

    pub(crate) fn orientation(&self) -> Result<Sign> {
        let m = &self.matrix;
        let determinant = determinant3([
            [&m[0][0], &m[0][1], &m[0][2]],
            [&m[1][0], &m[1][1], &m[1][2]],
            [&m[2][0], &m[2][1], &m[2][2]],
        ]);
        match determinant.sign() {
            Sign::Zero => Err(Error::SingularTransform),
            sign => Ok(sign),
        }
    }

    pub(crate) fn point(&self, point: &Point) -> Result<Point> {
        Point::new(self.matrix.each_ref().map(|row| {
            row.iter()
                .zip(&point.h)
                .fold(Integer::ZERO, |sum, (a, b)| sum.add(&a.mul(b)))
        }))
    }

    pub(crate) fn plane(&self, plane: &Plane) -> Result<Plane> {
        let orientation = self.orientation()?;
        // The cofactor matrix is det(M) * inverse-transpose(M). Correct the determinant's
        // sign so a positive halfspace remains positive under a reflection too.
        let coefficients = std::array::from_fn(|i| {
            let value = (0..4).fold(Integer::ZERO, |sum, j| {
                sum.add(&cofactor(&self.matrix, i, j).mul(&plane.coefficients[j]))
            });
            if orientation == Sign::Negative {
                value.negated()
            } else {
                value
            }
        });
        Plane::new(coefficients)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub(crate) struct Origin {
    pub(crate) operand: u32,
    pub(crate) face: u32,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct Triangle {
    pub(crate) corners: [u32; 3],
    pub(crate) support: usize,
    pub(crate) origin: Origin,
}

#[derive(Clone, Debug)]
pub(crate) struct Mesh {
    pub(crate) points: Vec<Point>,
    pub(crate) planes: Vec<Plane>,
    pub(crate) triangles: Vec<Triangle>,
}

/// Local numerical conversion observations. These do not prove absence of self-intersections.
#[derive(Clone, Debug, Default, PartialEq)]
pub(crate) struct ConversionReport {
    pub(crate) moved_vertices: usize,
    pub(crate) coincident_vertices: usize,
    pub(crate) collapsed_triangles: usize,
    pub(crate) reversed_triangles: usize,
    pub(crate) max_axis_displacement: f64,
}

impl Mesh {
    pub(crate) fn from_binary64(
        positions: &[[f64; 3]],
        triangles: &[[u32; 3]],
        origins: &[Origin],
    ) -> Result<Self> {
        if origins.len() != triangles.len() {
            return Err(Error::InvalidMeshIndex);
        }
        let points: Vec<Point> = positions
            .iter()
            .copied()
            .map(Point::from_binary64)
            .collect::<Result<_>>()?;
        let mut planes = vec![];
        let mut plane_index = BTreeMap::new();
        let mut out = vec![];
        for (&corners, &origin) in triangles.iter().zip(origins) {
            let [a, b, c] = corners.map(|i| points.get(i as usize).ok_or(Error::InvalidMeshIndex));
            let plane = Plane::through(a?, b?, c?)?;
            let support = *plane_index.entry(plane.clone()).or_insert_with(|| {
                let index = planes.len();
                planes.push(plane);
                index
            });
            out.push(Triangle {
                corners,
                support,
                origin,
            });
        }
        Ok(Self {
            points,
            planes,
            triangles: out,
        })
    }

    pub(crate) fn transformed(&self, affine: &Affine) -> Result<Self> {
        let points = self
            .points
            .iter()
            .map(|p| affine.point(p))
            .collect::<Result<_>>()?;
        let planes = self
            .planes
            .iter()
            .map(|p| affine.plane(p))
            .collect::<Result<_>>()?;
        let mut triangles = self.triangles.clone();
        if affine.orientation()? == Sign::Negative {
            for triangle in &mut triangles {
                triangle.corners.swap(1, 2);
            }
        }
        Ok(Self {
            points,
            planes,
            triangles,
        })
    }

    pub(crate) fn max_integer_bits(&self) -> usize {
        self.points
            .iter()
            .flat_map(|p| p.h.iter())
            .chain(self.planes.iter().flat_map(|p| p.coefficients.iter()))
            .map(Integer::bit_len)
            .max()
            .unwrap_or(0)
    }

    pub(crate) fn binary64(&self) -> Result<Vec<[f64; 3]>> {
        self.points.iter().map(Point::binary64).collect()
    }

    pub(crate) fn conversion_report(&self) -> Result<ConversionReport> {
        let positions = self.binary64()?;
        let rounded: Vec<Point> = positions
            .iter()
            .copied()
            .map(Point::from_binary64)
            .collect::<Result<_>>()?;
        let mut report = ConversionReport::default();
        let mut seen: BTreeMap<[u64; 3], usize> = BTreeMap::new();
        for (i, ((exact, rounded), position)) in
            self.points.iter().zip(&rounded).zip(&positions).enumerate()
        {
            if exact != rounded {
                report.moved_vertices += 1;
            }
            let key = position.map(|x| if x == 0.0 { 0 } else { x.to_bits() });
            if let Some(&prior) = seen.get(&key) {
                if self.points[prior] != *exact {
                    report.coincident_vertices += 1;
                }
            } else {
                seen.insert(key, i);
            }
            for axis in 0..3 {
                let difference = exact.h[axis]
                    .mul(&rounded.h[3])
                    .sub(&rounded.h[axis].mul(&exact.h[3]));
                let denominator = exact.h[3].mul(&rounded.h[3]);
                report.max_axis_displacement = report
                    .max_axis_displacement
                    .max(difference.ratio_binary64(&denominator)?.abs());
            }
        }
        for triangle in &self.triangles {
            let [a, b, c] = triangle.corners.map(|i| &rounded[i as usize]);
            match Plane::through(a, b, c) {
                Err(Error::DegenerateTriangle) => report.collapsed_triangles += 1,
                Err(error) => return Err(error),
                Ok(plane) => {
                    let support = &self.planes[triangle.support];
                    let dot = (0..3).fold(Integer::ZERO, |sum, i| {
                        sum.add(&support.coefficients[i].mul(&plane.coefficients[i]))
                    });
                    if dot.sign() == Sign::Negative {
                        report.reversed_triangles += 1;
                    }
                }
            }
        }
        Ok(report)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn shear(value: f64) -> Affine {
        Affine::from_binary64([
            [1.0, value, 0.0, 0.1],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
        ])
        .unwrap()
    }

    #[test]
    fn constructed_points_survive_affine_round_trips_without_rounding() {
        let plane = |c: [i128; 4]| Plane::new(c.map(Integer::from_i128)).unwrap();
        let point = Point::triple_plane(
            &plane([3, 0, 0, -1]),
            &plane([0, 5, 0, -1]),
            &plane([0, 0, 7, -1]),
        )
        .unwrap();
        let forward = shear(0.1);
        let back = Affine::from_binary64([
            [1.0, -0.1, 0.0, -0.1],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
        ])
        .unwrap();
        let mut transformed = point.clone();
        for _ in 0..32 {
            transformed = forward.point(&transformed).unwrap();
        }
        for _ in 0..32 {
            transformed = back.point(&transformed).unwrap();
        }
        assert_eq!(transformed, point);
    }

    #[test]
    fn reflected_state_retains_oriented_supports_and_provenance() {
        let origin = Origin {
            operand: 2,
            face: 9,
        };
        let mesh = Mesh::from_binary64(
            &[[0.0; 3], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            &[[0, 1, 2]],
            &[origin],
        )
        .unwrap();
        let reflection = Affine::from_binary64([
            [-1.0, 0.0, 0.0, 0.1],
            [0.0, 1.0, 0.0, 0.2],
            [0.0, 0.0, 1.0, 0.3],
        ])
        .unwrap();
        let reflected = mesh.transformed(&reflection).unwrap();
        let triangle = &reflected.triangles[0];
        assert_eq!(triangle.origin, origin);
        assert_eq!(triangle.corners, [0, 2, 1]);
        let [a, b, c] = triangle.corners.map(|i| &reflected.points[i as usize]);
        assert_eq!(
            Plane::through(a, b, c).unwrap(),
            reflected.planes[triangle.support]
        );
        assert_eq!(
            reflected.conversion_report().unwrap().collapsed_triangles,
            0
        );
    }

    #[test]
    fn export_reports_coincidence_without_merging_exact_points() {
        let n = Integer::from_i128(1).shl(1200);
        let point = |x, y| Point::new([x, y, Integer::ZERO, n.clone()]).unwrap();
        let points = vec![
            point(n.clone(), n.clone()),
            point(n.add(&Integer::from_i128(1)), n.clone()),
            point(n.clone(), n.add(&Integer::from_i128(1))),
        ];
        let planes = vec![Plane::through(&points[0], &points[1], &points[2]).unwrap()];
        let mesh = Mesh {
            points,
            planes,
            triangles: vec![Triangle {
                corners: [0, 1, 2],
                support: 0,
                origin: Origin {
                    operand: 0,
                    face: 0,
                },
            }],
        };
        let report = mesh.conversion_report().unwrap();
        assert_eq!(report.coincident_vertices, 2);
        assert_eq!(report.collapsed_triangles, 1);
        assert_eq!(mesh.points.len(), 3);
    }
}
