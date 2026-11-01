//! Closed triangle contacts, including coincident faces and touches at vertices or edges.
use super::{Integer, Plane, Point, Result, Sign, side_of_plane};
use std::cmp::Ordering;

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) enum Contact {
    Empty,
    Point(Point),
    Segment([Point; 2]),
    /// Convex closed intersection in the first triangle's winding. Collinear vertices remain
    /// available to register contacts across adjacent triangles.
    Coplanar(Vec<Point>),
}

fn strictly_one_side(signs: [Sign; 3]) -> bool {
    signs.iter().all(|&s| s == Sign::Positive) || signs.iter().all(|&s| s == Sign::Negative)
}

fn push_distinct(points: &mut Vec<Point>, point: Point) {
    if !points.contains(&point) {
        points.push(point);
    }
}

fn slice(triangle: [&Point; 3], plane: &Plane, signs: [Sign; 3]) -> Result<Vec<Point>> {
    let mut points = vec![];
    for i in 0..3 {
        let j = (i + 1) % 3;
        if signs[i] == Sign::Zero {
            push_distinct(&mut points, triangle[i].clone());
        }
        if signs[i] != Sign::Zero && signs[j] != Sign::Zero && signs[i] != signs[j] {
            push_distinct(
                &mut points,
                Point::line_plane(triangle[i], triangle[j], plane)?,
            );
        }
    }
    Ok(points)
}

/// Plane through `a` and `b`, extruded along the projection's dropped axis.
pub(crate) fn edge_plane(a: &Point, b: &Point, axis: usize) -> Result<Plane> {
    let (x, y) = ((axis + 1) % 3, (axis + 2) % 3);
    let mut coefficients = std::array::from_fn(|_| Integer::ZERO);
    coefficients[x] = a.h[y].mul(&b.h[3]).sub(&b.h[y].mul(&a.h[3]));
    coefficients[y] = b.h[x].mul(&a.h[3]).sub(&a.h[x].mul(&b.h[3]));
    coefficients[3] = a.h[x].mul(&b.h[y]).sub(&a.h[y].mul(&b.h[x]));
    Plane::new(coefficients)
}

fn clip(polygon: &[Point], plane: &Plane) -> Result<Vec<Point>> {
    let mut out = vec![];
    if polygon.is_empty() {
        return Ok(out);
    }
    for i in 0..polygon.len() {
        let (a, b) = (&polygon[i], &polygon[(i + 1) % polygon.len()]);
        let (sa, sb) = (side_of_plane(a, plane), side_of_plane(b, plane));
        if sa != Sign::Negative && out.last() != Some(a) {
            out.push(a.clone());
        }
        if sa != Sign::Zero && sb != Sign::Zero && sa != sb {
            let intersection = Point::line_plane(a, b, plane)?;
            if out.last() != Some(&intersection) {
                out.push(intersection);
            }
        }
    }
    if out.len() > 1 && out.first() == out.last() {
        out.pop();
    }
    Ok(out)
}

fn coplanar(a: [&Point; 3], b: [&Point; 3], support: &Plane) -> Result<Contact> {
    let axis = support.projection_axis();
    let mut polygon = a.map(Clone::clone).to_vec();
    for i in 0..3 {
        let mut edge = edge_plane(b[i], b[(i + 1) % 3], axis)?;
        if side_of_plane(b[(i + 2) % 3], &edge) == Sign::Negative {
            edge = edge.reversed();
        }
        polygon = clip(&polygon, &edge)?;
        if polygon.is_empty() {
            return Ok(Contact::Empty);
        }
    }
    if let Some(first) = (0..polygon.len()).min_by_key(|&i| &polygon[i]) {
        polygon.rotate_left(first);
    }
    match polygon.len() {
        0 => Ok(Contact::Empty),
        1 => Ok(Contact::Point(polygon.remove(0))),
        2 => Ok(Contact::Segment([polygon.remove(0), polygon.remove(0)])),
        _ => Ok(Contact::Coplanar(polygon)),
    }
}

pub(crate) fn meet(a: [&Point; 3], pa: &Plane, b: [&Point; 3], pb: &Plane) -> Result<Contact> {
    let (sa, sb) = (
        a.map(|p| side_of_plane(p, pb)),
        b.map(|p| side_of_plane(p, pa)),
    );
    if strictly_one_side(sa) || strictly_one_side(sb) {
        return Ok(Contact::Empty);
    }
    if sa == [Sign::Zero; 3] {
        return coplanar(a, b, pa);
    }
    let mut aa = slice(a, pb, sa)?;
    let mut bb = slice(b, pa, sb)?;
    if aa.is_empty() || bb.is_empty() {
        return Ok(Contact::Empty);
    }
    let cross: [Integer; 3] = std::array::from_fn(|axis| {
        let (i, j) = ((axis + 1) % 3, (axis + 2) % 3);
        pa.coefficients[i]
            .mul(&pb.coefficients[j])
            .sub(&pa.coefficients[j].mul(&pb.coefficients[i]))
    });
    let mut axis = 0;
    for i in 1..3 {
        if cross[i].abs() > cross[axis].abs() {
            axis = i;
        }
    }
    // The non-coplanar supports are nonparallel: otherwise the strict-side test returned.
    debug_assert!(!cross[axis].is_zero());
    if aa.len() > 1 && aa[0].cmp_axis(&aa[1], axis)? == Ordering::Greater {
        aa.swap(0, 1);
    }
    if bb.len() > 1 && bb[0].cmp_axis(&bb[1], axis)? == Ordering::Greater {
        bb.swap(0, 1);
    }
    let lo = if aa[0].cmp_axis(&bb[0], axis)? == Ordering::Less {
        &bb[0]
    } else {
        &aa[0]
    };
    let (a_hi, b_hi) = (aa.last().unwrap(), bb.last().unwrap());
    let hi = if a_hi.cmp_axis(b_hi, axis)? == Ordering::Greater {
        b_hi
    } else {
        a_hi
    };
    match lo.cmp_axis(hi, axis)? {
        Ordering::Less => Ok(Contact::Segment([lo.clone(), hi.clone()])),
        Ordering::Equal => Ok(Contact::Point(lo.clone())),
        Ordering::Greater => Ok(Contact::Empty),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn points(a: [[f64; 3]; 3]) -> [Point; 3] {
        a.map(|p| Point::from_binary64(p).unwrap())
    }

    fn contact(a: &[[f64; 3]; 3], b: &[[f64; 3]; 3]) -> Contact {
        let (a, b) = (points(*a), points(*b));
        let (pa, pb) = (
            Plane::through(&a[0], &a[1], &a[2]).unwrap(),
            Plane::through(&b[0], &b[1], &b[2]).unwrap(),
        );
        meet(a.each_ref(), &pa, b.each_ref(), &pb).unwrap()
    }

    #[test]
    fn transverse_contacts_include_vertex_and_edge_touches() {
        let a = [[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 2.0, 0.0]];
        let b = [[0.5, 0.0, -1.0], [0.5, 0.0, 1.0], [0.5, 2.0, 0.0]];
        let Contact::Segment(segment) = contact(&a, &b) else {
            panic!("expected a segment")
        };
        assert_eq!(
            segment.map(|p| p.binary64().unwrap()),
            [[0.5, 0.0, 0.0], [0.5, 1.5, 0.0]]
        );
        let b = [[0.0, 0.0, 0.0], [-1.0, 0.0, 1.0], [0.0, -1.0, 1.0]];
        assert_eq!(
            contact(&a, &b),
            Contact::Point(Point::from_binary64([0.0; 3]).unwrap())
        );
        let b = [[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [1.0, 0.0, 1.0]];
        let Contact::Segment(segment) = contact(&a, &b) else {
            panic!("expected an edge")
        };
        assert_eq!(
            segment.map(|p| p.binary64().unwrap()),
            [[0.0; 3], [2.0, 0.0, 0.0]]
        );
    }

    #[test]
    fn coplanar_contacts_are_closed_and_orientation_independent() {
        let a = [[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 2.0, 0.0]];
        let b = [[0.5, 0.5, 0.0], [1.5, 0.5, 0.0], [0.5, 1.5, 0.0]];
        let Contact::Coplanar(poly) = contact(&a, &b) else {
            panic!("expected a polygon")
        };
        assert_eq!(poly.len(), 3);
        for vertex in b {
            assert!(poly.contains(&Point::from_binary64(vertex).unwrap()));
        }
        let mut reverse = b;
        reverse.swap(1, 2);
        assert_eq!(contact(&a, &b), contact(&a, &reverse));
        let b = [[2.0, 0.0, 0.0], [3.0, 0.0, 0.0], [2.0, 1.0, 0.0]];
        assert_eq!(
            contact(&a, &b),
            Contact::Point(Point::from_binary64([2.0, 0.0, 0.0]).unwrap())
        );
        let b = [[0.0; 3], [2.0, 0.0, 0.0], [1.0, -1.0, 0.0]];
        assert!(matches!(contact(&a, &b), Contact::Segment(_)));
    }

    #[test]
    fn disjoint_supports_and_disjoint_coplanar_triangles_have_no_contact() {
        let a = [[0.0; 3], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]];
        let b = a.map(|[x, y, z]| [x, y, z + 0.25]);
        assert_eq!(contact(&a, &b), Contact::Empty);
        let b = a.map(|[x, y, z]| [x + 2.0, y + 2.0, z]);
        assert_eq!(contact(&a, &b), Contact::Empty);
    }
}
