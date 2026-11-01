//! Homogeneous constructions. Finite binary64 inputs enter as their exact dyadic values.
use super::{Error, Integer, Result, Sign};
use std::cmp::Ordering;

pub(crate) const GRID: f64 = 1.0 / 1073741824.0;
pub(crate) const GRID_LIMIT: i64 = 1_i64 << 40;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct GridPoint(pub(crate) [i64; 3]);

impl GridPoint {
    pub(crate) fn new(coords: [i64; 3]) -> Result<Self> {
        if coords.iter().any(|x| x.unsigned_abs() > GRID_LIMIT as u64) {
            return Err(Error::CoordinateRange);
        }
        Ok(Self(coords))
    }
}

/// An optional, explicit grid conversion. The exact input path does not call it.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct GridFrame {
    pub(crate) origin: [i64; 3],
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct Quantized {
    pub(crate) point: GridPoint,
    pub(crate) moved: bool,
}

fn world_grid(x: f64) -> Result<i64> {
    if !x.is_finite() {
        return Err(Error::NonFiniteCoordinate);
    }
    let scaled = x / GRID;
    if scaled.abs() > (1_u64 << 52) as f64 {
        return Err(Error::CoordinateRange);
    }
    Ok(scaled.round_ties_even() as i64)
}

impl GridFrame {
    pub(crate) fn for_points(points: &[[f64; 3]]) -> Result<Self> {
        if points.is_empty() {
            return Ok(Self { origin: [0; 3] });
        }
        let (mut lo, mut hi) = ([i64::MAX; 3], [i64::MIN; 3]);
        for point in points {
            for axis in 0..3 {
                let q = world_grid(point[axis])?;
                lo[axis] = lo[axis].min(q);
                hi[axis] = hi[axis].max(q);
            }
        }
        let mut origin = [0; 3];
        for axis in 0..3 {
            let sum = i128::from(lo[axis]) + i128::from(hi[axis]);
            let lower = sum.div_euclid(2);
            origin[axis] =
                (lower + i128::from(sum.rem_euclid(2) != 0 && lower.rem_euclid(2) != 0)) as i64;
        }
        let frame = Self { origin };
        for &point in points {
            frame.quantize(point)?;
        }
        Ok(frame)
    }

    pub(crate) fn quantize(self, world: [f64; 3]) -> Result<Quantized> {
        let mut point = [0; 3];
        let mut moved = false;
        for axis in 0..3 {
            let q = world_grid(world[axis])?;
            point[axis] = q
                .checked_sub(self.origin[axis])
                .ok_or(Error::CoordinateRange)?;
            moved |= q as f64 * GRID != world[axis];
        }
        Ok(Quantized {
            point: GridPoint::new(point)?,
            moved,
        })
    }
}

/// `mantissa * 2^exponent`, with no remaining factor of two in a nonzero mantissa.
pub(super) fn binary64_parts(value: f64) -> Result<(i128, i32)> {
    if !value.is_finite() {
        return Err(Error::NonFiniteCoordinate);
    }
    let bits = value.to_bits();
    let raw_exponent = ((bits >> 52) & 0x7ff) as i32;
    let mut mantissa = bits & ((1_u64 << 52) - 1);
    let mut exponent = -1074;
    if raw_exponent != 0 {
        mantissa |= 1_u64 << 52;
        exponent = raw_exponent - 1023 - 52;
    }
    if mantissa == 0 {
        return Ok((0, 0));
    }
    let shift = mantissa.trailing_zeros();
    mantissa >>= shift;
    exponent += shift as i32;
    let sign = if bits >> 63 != 0 { -1 } else { 1 };
    Ok((i128::from(mantissa) * sign, exponent))
}

pub(super) fn determinant3(rows: [[&Integer; 3]; 3]) -> Integer {
    let [[a, b, c], [d, e, f], [g, h, i]] = rows;
    a.mul(&e.mul(i).sub(&f.mul(h)))
        .sub(&b.mul(&d.mul(i).sub(&f.mul(g))))
        .add(&c.mul(&d.mul(h).sub(&e.mul(g))))
}

fn reduce(values: &mut [Integer]) -> Result<()> {
    let mut factor = Integer::ZERO;
    for value in values.iter() {
        factor = factor.gcd(value);
        if factor == Integer::from_i128(1) {
            return Ok(());
        }
    }
    if !factor.is_zero() {
        for value in values {
            *value = value.divided_exactly(&factor)?;
        }
    }
    Ok(())
}

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub(crate) struct Plane {
    /// `n.x * X + n.y * Y + n.z * Z + d * W = 0`. Positive is the oriented front.
    pub(crate) coefficients: [Integer; 4],
}

impl Plane {
    pub(crate) fn new(mut coefficients: [Integer; 4]) -> Result<Self> {
        if coefficients[..3].iter().all(Integer::is_zero) {
            return Err(Error::DegenerateTriangle);
        }
        reduce(&mut coefficients)?;
        Ok(Self { coefficients })
    }

    pub(crate) fn through(a: &Point, b: &Point, c: &Point) -> Result<Self> {
        let mut coefficients = std::array::from_fn(|_| Integer::ZERO);
        for (excluded, coefficient) in coefficients.iter_mut().enumerate() {
            let cols: Vec<usize> = (0..4).filter(|&i| i != excluded).collect();
            let rows = [&a.h, &b.h, &c.h].map(|h| [&h[cols[0]], &h[cols[1]], &h[cols[2]]]);
            let determinant = determinant3(rows);
            *coefficient = if excluded % 2 == 0 {
                determinant
            } else {
                determinant.negated()
            };
        }
        Self::new(coefficients)
    }

    pub(crate) fn evaluate(&self, point: &Point) -> Integer {
        self.coefficients
            .iter()
            .zip(&point.h)
            .fold(Integer::ZERO, |sum, (a, b)| sum.add(&a.mul(b)))
    }

    pub(crate) fn reversed(&self) -> Self {
        Self {
            coefficients: self.coefficients.each_ref().map(Integer::negated),
        }
    }

    /// A plane key independent of its orientation, and the original orientation relative to it.
    pub(crate) fn support_key(&self) -> (Self, Sign) {
        if self.coefficients[..3]
            .iter()
            .find(|x| !x.is_zero())
            .unwrap()
            .sign()
            == Sign::Negative
        {
            (self.reversed(), Sign::Negative)
        } else {
            (self.clone(), Sign::Positive)
        }
    }

    pub(crate) fn projection_axis(&self) -> usize {
        let mut axis = 0;
        for i in 1..3 {
            if self.coefficients[i].abs() > self.coefficients[axis].abs() {
                axis = i;
            }
        }
        axis
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub(crate) struct Point {
    /// Primitive integer homogeneous coordinates, with strictly positive weight.
    pub(crate) h: [Integer; 4],
}

impl Point {
    pub(crate) fn new(mut h: [Integer; 4]) -> Result<Self> {
        match h[3].sign() {
            Sign::Zero => return Err(Error::NonUniqueIntersection),
            Sign::Negative => h = h.each_ref().map(Integer::negated),
            Sign::Positive => {}
        }
        reduce(&mut h)?;
        Ok(Self { h })
    }

    pub(crate) fn from_grid(point: GridPoint) -> Self {
        let [x, y, z] = point.0;
        Self {
            h: [
                Integer::from_i128(x.into()),
                Integer::from_i128(y.into()),
                Integer::from_i128(z.into()),
                Integer::from_i128(1),
            ],
        }
    }

    pub(crate) fn from_binary64(coords: [f64; 3]) -> Result<Self> {
        let parts = coords.map(binary64_parts);
        let [(x, ex), (y, ey), (z, ez)] = [parts[0]?, parts[1]?, parts[2]?];
        let base = ex.min(ey).min(ez).min(0);
        Self::new([
            Integer::from_i128(x).shl((ex - base) as usize),
            Integer::from_i128(y).shl((ey - base) as usize),
            Integer::from_i128(z).shl((ez - base) as usize),
            Integer::from_i128(1).shl((-base) as usize),
        ])
    }

    pub(crate) fn line_plane(a: &Self, b: &Self, plane: &Plane) -> Result<Self> {
        let (sa, sb) = (plane.evaluate(a), plane.evaluate(b));
        if sa.is_zero() && sb.is_zero() {
            return Err(Error::NonUniqueIntersection);
        }
        if sa.is_zero() {
            return Ok(a.clone());
        }
        if sb.is_zero() {
            return Ok(b.clone());
        }
        Self::new(std::array::from_fn(|i| {
            sb.mul(&a.h[i]).sub(&sa.mul(&b.h[i]))
        }))
    }

    pub(crate) fn triple_plane(a: &Plane, b: &Plane, c: &Plane) -> Result<Self> {
        let normals =
            [&a.coefficients, &b.coefficients, &c.coefficients].map(|p| [&p[0], &p[1], &p[2]]);
        let weight = determinant3(normals);
        if weight.is_zero() {
            return Err(Error::NonUniqueIntersection);
        }
        let mut h = std::array::from_fn(|_| Integer::ZERO);
        for axis in 0..3 {
            let mut rows = normals;
            for (i, p) in [a, b, c].iter().enumerate() {
                rows[i][axis] = &p.coefficients[3];
            }
            h[axis] = determinant3(rows).negated();
        }
        h[3] = weight;
        Self::new(h)
    }

    pub(crate) fn centroid(a: &Self, b: &Self, c: &Self) -> Result<Self> {
        let ab = a.h[3].mul(&b.h[3]);
        let ac = a.h[3].mul(&c.h[3]);
        let bc = b.h[3].mul(&c.h[3]);
        let mut h = std::array::from_fn(|_| Integer::ZERO);
        for axis in 0..3 {
            h[axis] = a.h[axis]
                .mul(&bc)
                .add(&b.h[axis].mul(&ac))
                .add(&c.h[axis].mul(&ab));
        }
        h[3] = ab.mul(&c.h[3]).mul(&Integer::from_i128(3));
        Self::new(h)
    }

    pub(crate) fn cmp_axis(&self, other: &Self, axis: usize) -> Result<Ordering> {
        if axis >= 3 {
            return Err(Error::InvalidAxis);
        }
        Ok(self.h[axis]
            .mul(&other.h[3])
            .cmp(&other.h[axis].mul(&self.h[3])))
    }

    pub(crate) fn rounded_grid(&self) -> Result<[i64; 3]> {
        Ok([
            self.h[0].rounded_ratio_i64(&self.h[3])?,
            self.h[1].rounded_ratio_i64(&self.h[3])?,
            self.h[2].rounded_ratio_i64(&self.h[3])?,
        ])
    }

    /// Numerical export only. Mesh validity requires a separate conversion review.
    pub(crate) fn binary64(&self) -> Result<[f64; 3]> {
        Ok([
            self.h[0].ratio_binary64(&self.h[3])?,
            self.h[1].ratio_binary64(&self.h[3])?,
            self.h[2].ratio_binary64(&self.h[3])?,
        ])
    }
}

impl Ord for Point {
    fn cmp(&self, other: &Self) -> Ordering {
        for axis in 0..3 {
            let order = self.cmp_axis(other, axis).expect("valid coordinate axis");
            if order != Ordering::Equal {
                return order;
            }
        }
        Ordering::Equal
    }
}

impl PartialOrd for Point {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    pub(super) fn p(coords: [i64; 3]) -> Point {
        Point::from_grid(GridPoint::new(coords).unwrap())
    }

    fn plane(coefficients: [i128; 4]) -> Plane {
        Plane::new(coefficients.map(Integer::from_i128)).unwrap()
    }

    #[test]
    fn binary64_inputs_round_trip_without_a_grid_snap() {
        for x in [
            0.0,
            0.1,
            -0.1,
            f64::MIN_POSITIVE,
            f64::from_bits(1),
            f64::MAX,
            2.0_f64.sqrt(),
        ] {
            let point = Point::from_binary64([x, 1.0, -3.5]).unwrap();
            assert_eq!(point.binary64().unwrap()[0].to_bits(), x.to_bits());
        }
        assert_eq!(
            Point::from_binary64([f64::NAN, 0.0, 0.0]),
            Err(Error::NonFiniteCoordinate)
        );
    }

    #[test]
    fn grid_origin_is_an_integer_even_for_a_half_grid_bbox_center() {
        let frame = GridFrame::for_points(&[[0.0, 0.0, 0.0], [GRID, -3.0 * GRID, 0.0]]).unwrap();
        assert_eq!(frame.origin, [0, -2, 0]);
        assert!(!frame.quantize([GRID, -3.0 * GRID, 0.0]).unwrap().moved);
        assert!(frame.quantize([GRID * 0.25, 0.0, 0.0]).unwrap().moved);
    }

    #[test]
    fn constructions_are_primitive_oriented_and_path_independent() {
        let a = plane([2, 0, 0, -1]);
        let b = plane([0, 3, 0, -1]);
        let c = plane([0, 0, 5, -1]);
        let tpi = Point::triple_plane(&a, &b, &c).unwrap();
        assert_eq!(tpi.binary64().unwrap(), [0.5, 1.0 / 3.0, 0.2]);
        for support in [&a, &b, &c] {
            assert!(support.evaluate(&tpi).is_zero());
        }
        let zero = p([0, 0, 0]);
        let end = p([3, 2, 6]);
        let lpi = Point::line_plane(&zero, &end, &plane([0, 0, 5, -1])).unwrap();
        assert_eq!(
            lpi,
            Point::line_plane(&end, &zero, &plane([0, 0, -5, 1])).unwrap()
        );
        assert_eq!(lpi.binary64().unwrap(), [0.1, 1.0 / 15.0, 0.2]);
        assert_eq!(
            Plane::through(&zero, &p([1, 0, 0]), &p([0, 1, 0])).unwrap(),
            plane([0, 0, 1, 0])
        );
        assert_eq!(
            plane([-2, 0, 0, 4]).support_key(),
            (plane([1, 0, 0, -2]), Sign::Negative)
        );
        assert_eq!(
            Point::triple_plane(&a, &a, &c),
            Err(Error::NonUniqueIntersection)
        );
        assert_eq!(
            Point::line_plane(&zero, &p([1, 0, 0]), &plane([0, 0, 1, 0])),
            Err(Error::NonUniqueIntersection)
        );
    }
}
