//! Predicates on exact constructions. No approximate value selects a topological branch.
use super::point::determinant3;
use super::{Error, Plane, Point, Result, Sign};

/// Counterclockwise orientation after dropping `axis`; cyclic projected axes preserve signs.
pub(crate) fn orient2d(a: &Point, b: &Point, c: &Point, axis: usize) -> Result<Sign> {
    if axis >= 3 {
        return Err(Error::InvalidAxis);
    }
    let (x, y) = ((axis + 1) % 3, (axis + 2) % 3);
    let determinant = determinant3([&a.h, &b.h, &c.h].map(|h| [&h[x], &h[y], &h[3]]));
    Ok(determinant.sign())
}

pub(crate) fn side_of_plane(point: &Point, plane: &Plane) -> Sign {
    plane.evaluate(point).sign()
}

/// Positive on the side pointed to by `(b-a) cross (c-a)`.
pub(crate) fn orient3d(a: &Point, b: &Point, c: &Point, d: &Point) -> Result<Sign> {
    Ok(side_of_plane(d, &Plane::through(a, b, c)?))
}

#[cfg(test)]
mod tests {
    use super::super::Integer;
    use super::*;

    fn p(coords: [f64; 3]) -> Point {
        Point::from_binary64(coords).unwrap()
    }

    #[test]
    fn projections_have_consistent_orientation_and_exact_zeros() {
        let a = p([0.0; 3]);
        let b = p([1.0, 0.0, 0.0]);
        let c = p([0.0, 1.0, 0.0]);
        assert_eq!(orient2d(&a, &b, &c, 2).unwrap(), Sign::Positive);
        assert_eq!(orient2d(&a, &c, &b, 2).unwrap(), Sign::Negative);
        assert_eq!(
            orient3d(&a, &b, &c, &p([0.0, 0.0, 1.0])).unwrap(),
            Sign::Positive
        );
        assert_eq!(
            orient3d(&a, &b, &c, &p([0.25, 0.25, 0.0])).unwrap(),
            Sign::Zero
        );
        assert_eq!(orient2d(&a, &b, &c, 3), Err(Error::InvalidAxis));
    }

    #[test]
    fn predicates_distinguish_points_that_export_to_the_same_binary64() {
        let n = Integer::from_i128(1).shl(1200);
        let a = Point::new([n.clone(), n.clone(), Integer::ZERO, n.clone()]).unwrap();
        let b = Point::new([
            n.add(&Integer::from_i128(1)),
            n.clone(),
            Integer::ZERO,
            n.clone(),
        ])
        .unwrap();
        let c = Point::new([n.clone(), n.add(&Integer::from_i128(1)), Integer::ZERO, n]).unwrap();
        assert_eq!(a.binary64().unwrap(), b.binary64().unwrap());
        assert_eq!(a.binary64().unwrap(), c.binary64().unwrap());
        assert_eq!(orient2d(&a, &b, &c, 2).unwrap(), Sign::Positive);
    }
}
