//! Per-triangle exact constrained arrangements. Crossing points enter before constraints.
use super::meet::edge_plane;
use super::{Contact, Error, Plane, Point, Result, Sign, orient2d};
use std::cmp::Ordering;
use std::collections::{BTreeMap, BTreeSet};

fn key(a: usize, b: usize) -> [usize; 2] {
    if a < b { [a, b] } else { [b, a] }
}

#[derive(Clone, Debug)]
pub(crate) struct Patch {
    pub(crate) points: Vec<Point>,
    pub(crate) triangles: Vec<[usize; 3]>,
    /// Atomic edges that touch another operand. Original triangle boundaries alone are clean.
    pub(crate) dirty: BTreeSet<[usize; 2]>,
}

#[derive(Clone, Copy)]
struct Segment {
    ends: [usize; 2],
    dirty: bool,
}

fn intern(points: &mut Vec<Point>, index: &mut BTreeMap<Point, usize>, point: Point) -> usize {
    *index.entry(point.clone()).or_insert_with(|| {
        let id = points.len();
        points.push(point);
        id
    })
}

fn range(points: &[Point], ends: [usize; 2], axis: usize) -> [usize; 2] {
    if points[ends[0]].cmp_axis(&points[ends[1]], axis).unwrap() == Ordering::Greater {
        [ends[1], ends[0]]
    } else {
        ends
    }
}

fn opposite(a: Sign, b: Sign) -> bool {
    a != Sign::Zero && b != Sign::Zero && a != b
}

fn crosses(points: &[Point], a: [usize; 2], b: [usize; 2], axis: usize) -> Result<bool> {
    let [a, b, c, d] = [a[0], a[1], b[0], b[1]].map(|i| &points[i]);
    Ok(opposite(orient2d(a, b, c, axis)?, orient2d(a, b, d, axis)?)
        && opposite(orient2d(c, d, a, axis)?, orient2d(c, d, b, axis)?))
}

fn crossing_points(
    points: &mut Vec<Point>,
    index: &mut BTreeMap<Point, usize>,
    segments: &[Segment],
    axis: usize,
) -> Result<()> {
    let x = (axis + 1) % 3;
    let y = (axis + 2) % 3;
    let bounds: Vec<([usize; 2], [usize; 2])> = segments
        .iter()
        .map(|s| (range(points, s.ends, x), range(points, s.ends, y)))
        .collect();
    let mut order: Vec<usize> = (0..segments.len()).collect();
    order.sort_by(|&a, &b| {
        points[bounds[a].0[0]]
            .cmp_axis(&points[bounds[b].0[0]], x)
            .unwrap()
            .then(a.cmp(&b))
    });
    let mut active: Vec<usize> = vec![];
    for i in order {
        active.retain(|&j| {
            points[bounds[j].0[1]]
                .cmp_axis(&points[bounds[i].0[0]], x)
                .unwrap()
                != Ordering::Less
        });
        for &j in &active {
            if points[bounds[j].1[1]].cmp_axis(&points[bounds[i].1[0]], y)? == Ordering::Less
                || points[bounds[i].1[1]].cmp_axis(&points[bounds[j].1[0]], y)? == Ordering::Less
            {
                continue;
            }
            if crosses(points, segments[i].ends, segments[j].ends, axis)? {
                let [a, b] = segments[i].ends;
                let [c, d] = segments[j].ends;
                let line = edge_plane(&points[c], &points[d], axis)?;
                let point = Point::line_plane(&points[a], &points[b], &line)?;
                intern(points, index, point);
            }
        }
        active.push(i);
    }
    Ok(())
}

fn atomic_segments(
    points: &[Point],
    segments: &[Segment],
    axis: usize,
) -> Result<BTreeMap<[usize; 2], bool>> {
    let (x, y) = ((axis + 1) % 3, (axis + 2) % 3);
    let mut order: Vec<usize> = (0..points.len()).collect();
    order.sort_by(|&a, &b| points[a].cmp_axis(&points[b], x).unwrap().then(a.cmp(&b)));
    let mut out = BTreeMap::new();
    for segment in segments {
        let xr = range(points, segment.ends, x);
        let yr = range(points, segment.ends, y);
        let lo = order
            .partition_point(|&i| points[i].cmp_axis(&points[xr[0]], x).unwrap() == Ordering::Less);
        let hi = order.partition_point(|&i| {
            points[i].cmp_axis(&points[xr[1]], x).unwrap() != Ordering::Greater
        });
        let line = edge_plane(&points[segment.ends[0]], &points[segment.ends[1]], axis)?;
        let mut on = vec![];
        for &i in &order[lo..hi] {
            if points[i].cmp_axis(&points[yr[0]], y)? != Ordering::Less
                && points[i].cmp_axis(&points[yr[1]], y)? != Ordering::Greater
                && line.evaluate(&points[i]).is_zero()
            {
                on.push(i);
            }
        }
        // Use the nonconstant coordinate. With a nonzero segment at least one is nonconstant.
        let along = if points[xr[0]].cmp_axis(&points[xr[1]], x)? == Ordering::Equal {
            y
        } else {
            x
        };
        on.sort_by(|&a, &b| {
            points[a]
                .cmp_axis(&points[b], along)
                .unwrap()
                .then(a.cmp(&b))
        });
        for edge in on.windows(2) {
            out.entry(key(edge[0], edge[1]))
                .and_modify(|dirty| *dirty |= segment.dirty)
                .or_insert(segment.dirty);
        }
    }
    Ok(out)
}

struct Corridor {
    triangles: Vec<usize>,
    crossed: Vec<[usize; 2]>,
}

struct Triangulation {
    points: Vec<Point>,
    triangles: Vec<Option<[usize; 3]>>,
    edges: BTreeMap<[usize; 2], Vec<usize>>,
    incident: Vec<BTreeSet<usize>>,
    constrained: BTreeSet<[usize; 2]>,
    axis: usize,
    hint: usize,
}

impl Triangulation {
    fn new(points: Vec<Point>, axis: usize) -> Result<Self> {
        let incident = vec![BTreeSet::new(); points.len()];
        let mut out = Self {
            points,
            triangles: vec![],
            edges: BTreeMap::new(),
            incident,
            constrained: BTreeSet::new(),
            axis,
            hint: 0,
        };
        out.add([0, 1, 2])?;
        Ok(out)
    }

    fn add(&mut self, mut triangle: [usize; 3]) -> Result<usize> {
        let [a, b, c] = triangle.map(|i| &self.points[i]);
        match orient2d(a, b, c, self.axis)? {
            Sign::Zero => return Err(Error::InvalidArrangement),
            Sign::Negative => triangle.swap(1, 2),
            Sign::Positive => {}
        }
        let id = self.triangles.len();
        self.triangles.push(Some(triangle));
        for i in 0..3 {
            self.incident[triangle[i]].insert(id);
            self.edges
                .entry(key(triangle[i], triangle[(i + 1) % 3]))
                .or_default()
                .push(id);
        }
        Ok(id)
    }

    fn remove(&mut self, id: usize) -> Result<[usize; 3]> {
        let triangle = self
            .triangles
            .get_mut(id)
            .and_then(Option::take)
            .ok_or(Error::InvalidArrangement)?;
        for i in 0..3 {
            self.incident[triangle[i]].remove(&id);
            let edge = key(triangle[i], triangle[(i + 1) % 3]);
            let neighbors = self.edges.get_mut(&edge).ok_or(Error::InvalidArrangement)?;
            neighbors.retain(|&n| n != id);
            if neighbors.is_empty() {
                self.edges.remove(&edge);
            }
        }
        Ok(triangle)
    }

    fn neighbor(&self, edge: [usize; 2], current: usize) -> Result<usize> {
        self.edges
            .get(&edge)
            .and_then(|ids| ids.iter().copied().find(|&i| i != current))
            .ok_or(Error::InvalidArrangement)
    }

    fn signs(&self, triangle: [usize; 3], point: usize) -> Result<[Sign; 3]> {
        let mut signs = [Sign::Zero; 3];
        for i in 0..3 {
            signs[i] = orient2d(
                &self.points[triangle[i]],
                &self.points[triangle[(i + 1) % 3]],
                &self.points[point],
                self.axis,
            )?;
        }
        Ok(signs)
    }

    fn locate(&self, point: usize) -> Result<(usize, [Sign; 3])> {
        let mut current = self.hint;
        let mut visited = BTreeSet::new();
        while visited.insert(current) {
            let triangle = self.triangles[current].ok_or(Error::InvalidArrangement)?;
            let signs = self.signs(triangle, point)?;
            if let Some(edge) = signs.iter().position(|&s| s == Sign::Negative) {
                if let Ok(next) =
                    self.neighbor(key(triangle[edge], triangle[(edge + 1) % 3]), current)
                {
                    current = next;
                    continue;
                }
                break;
            } else {
                return Ok((current, signs));
            }
        }
        // Visibility walking can cycle in a non-Delaunay triangulation. The exact fallback
        // establishes containment without assuming a particular sequence of prior insertions.
        for (id, triangle) in self.triangles.iter().enumerate() {
            if let Some(triangle) = triangle {
                let signs = self.signs(*triangle, point)?;
                if signs.iter().all(|&s| s != Sign::Negative) {
                    return Ok((id, signs));
                }
            }
        }
        Err(Error::InvalidArrangement)
    }

    fn insert_point(&mut self, point: usize) -> Result<()> {
        let (current, signs) = self.locate(point)?;
        let triangle = self.triangles[current].ok_or(Error::InvalidArrangement)?;
        if let Some(edge) = signs.iter().position(|&s| s == Sign::Zero) {
            let [a, b] = [triangle[edge], triangle[(edge + 1) % 3]];
            let neighbors = self
                .edges
                .get(&key(a, b))
                .ok_or(Error::InvalidArrangement)?
                .clone();
            for id in neighbors {
                let triangle = self.remove(id)?;
                let c = triangle
                    .into_iter()
                    .find(|&i| i != a && i != b)
                    .ok_or(Error::InvalidArrangement)?;
                self.hint = self.add([a, point, c])?;
                self.add([point, b, c])?;
            }
        } else {
            self.remove(current)?;
            for i in 0..3 {
                self.hint = self.add([triangle[i], triangle[(i + 1) % 3], point])?;
            }
        }
        Ok(())
    }

    fn trace(&self, a: usize, b: usize) -> Result<Corridor> {
        let mut current = None;
        for &id in &self.incident[a] {
            let triangle = self.triangles[id].ok_or(Error::InvalidArrangement)?;
            let i = triangle
                .iter()
                .position(|&v| v == a)
                .ok_or(Error::InvalidArrangement)?;
            let (u, v) = (triangle[(i + 1) % 3], triangle[(i + 2) % 3]);
            if orient2d(&self.points[a], &self.points[u], &self.points[b], self.axis)?
                == Sign::Positive
                && orient2d(&self.points[a], &self.points[b], &self.points[v], self.axis)?
                    == Sign::Positive
            {
                current = Some(id);
                break;
            }
        }
        let mut current = current.ok_or(Error::InvalidArrangement)?;
        let mut out = vec![];
        let mut crossed = vec![];
        let mut visited = BTreeSet::new();
        let mut entered = None;
        loop {
            if !visited.insert(current) {
                return Err(Error::InvalidArrangement);
            }
            out.push(current);
            let triangle = self.triangles[current].ok_or(Error::InvalidArrangement)?;
            if triangle.contains(&b) {
                return Ok(Corridor {
                    triangles: out,
                    crossed,
                });
            }
            let mut exit = None;
            for i in 0..3 {
                let edge = key(triangle[i], triangle[(i + 1) % 3]);
                if Some(edge) != entered && crosses(&self.points, [a, b], edge, self.axis)? {
                    if self.constrained.contains(&edge) {
                        return Err(Error::CrossingConstraints);
                    }
                    exit = Some(edge);
                    break;
                }
            }
            let edge = exit.ok_or(Error::InvalidArrangement)?;
            crossed.push(edge);
            current = self.neighbor(edge, current)?;
            entered = Some(edge);
        }
    }

    fn insert_constraint(&mut self, [a, b]: [usize; 2]) -> Result<()> {
        let edge = key(a, b);
        if self.edges.contains_key(&edge) {
            self.constrained.insert(edge);
            return Ok(());
        }
        let corridor = self.trace(a, b)?;
        let (mut left, mut right) = (vec![a], vec![a]);
        // Follow the triangle march, preserving separate occurrences at a shared position.
        // A pocket can trap uncut edges or untouched triangles; a geometric vertex-to-next
        // map loses its topology. See Livesu et al., arxiv.org/abs/2009.04294, section 5.1.
        for crossed in corridor.crossed {
            let (l, r) = match orient2d(
                &self.points[a],
                &self.points[b],
                &self.points[crossed[0]],
                self.axis,
            )? {
                Sign::Positive => (crossed[0], crossed[1]),
                Sign::Negative => (crossed[1], crossed[0]),
                Sign::Zero => return Err(Error::InvalidArrangement),
            };
            if left.last() != Some(&l) {
                left.push(l);
            }
            if right.last() != Some(&r) {
                right.push(r);
            }
        }
        left.push(b);
        right.push(b);
        left.reverse();
        let mut replacement = self.earcut(&right)?;
        replacement.extend(self.earcut(&left)?);
        for id in corridor.triangles {
            self.remove(id)?;
        }
        for triangle in replacement {
            self.add(triangle)?;
        }
        if !self.edges.contains_key(&edge) {
            return Err(Error::InvalidArrangement);
        }
        self.constrained.insert(edge);
        Ok(())
    }

    fn earcut(&self, polygon: &[usize]) -> Result<Vec<[usize; 3]>> {
        if polygon.len() < 3 {
            return Err(Error::InvalidArrangement);
        }
        let mut ring = polygon.to_vec();
        let mut out = vec![];
        while ring.len() > 3 {
            let mut ear = None;
            // Each pocket's first and last occurrences are the constrained endpoints. Keep
            // those fixed while clipping the mesh-derived chain's internal ears.
            for i in 1..ring.len() - 1 {
                let [a, b, c] = [ring[i - 1], ring[i], ring[i + 1]];
                let [pa, pb, pc] = [a, b, c].map(|j| &self.points[j]);
                if orient2d(pa, pb, pc, self.axis)? != Sign::Positive {
                    continue;
                }
                let mut empty = true;
                for &v in &ring {
                    if v == a || v == b || v == c {
                        continue;
                    }
                    let p = &self.points[v];
                    if orient2d(pa, pb, p, self.axis)? != Sign::Negative
                        && orient2d(pb, pc, p, self.axis)? != Sign::Negative
                        && orient2d(pc, pa, p, self.axis)? != Sign::Negative
                    {
                        empty = false;
                        break;
                    }
                }
                if empty {
                    ear = Some((i, [a, b, c]));
                    break;
                }
            }
            let (i, triangle) = ear.ok_or(Error::InvalidArrangement)?;
            out.push(triangle);
            ring.remove(i);
        }
        let last = [ring[0], ring[1], ring[2]];
        if orient2d(
            &self.points[last[0]],
            &self.points[last[1]],
            &self.points[last[2]],
            self.axis,
        )? != Sign::Positive
        {
            return Err(Error::InvalidArrangement);
        }
        out.push(last);
        Ok(out)
    }
}

pub(crate) fn arrange(triangle: [Point; 3], contacts: &[Contact]) -> Result<Patch> {
    let plane = Plane::through(&triangle[0], &triangle[1], &triangle[2])?;
    let axis = plane.projection_axis();
    let reversed = orient2d(&triangle[0], &triangle[1], &triangle[2], axis)? == Sign::Negative;
    let mut points = triangle.to_vec();
    let mut index: BTreeMap<Point, usize> = points
        .iter()
        .cloned()
        .enumerate()
        .map(|(i, p)| (p, i))
        .collect();
    let mut segments = vec![
        Segment {
            ends: [0, 1],
            dirty: false,
        },
        Segment {
            ends: [1, 2],
            dirty: false,
        },
        Segment {
            ends: [2, 0],
            dirty: false,
        },
    ];
    for contact in contacts {
        let polygon: Vec<&Point> = match contact {
            Contact::Empty => continue,
            Contact::Point(point) => vec![point],
            Contact::Segment(ends) => ends.iter().collect(),
            Contact::Coplanar(polygon) => polygon.iter().collect(),
        };
        let ids: Vec<usize> = polygon
            .into_iter()
            .map(|p| intern(&mut points, &mut index, p.clone()))
            .collect();
        if ids.len() == 2 && ids[0] != ids[1] {
            segments.push(Segment {
                ends: [ids[0], ids[1]],
                dirty: true,
            });
        } else if ids.len() > 2 {
            for i in 0..ids.len() {
                if ids[i] != ids[(i + 1) % ids.len()] {
                    segments.push(Segment {
                        ends: [ids[i], ids[(i + 1) % ids.len()]],
                        dirty: true,
                    });
                }
            }
        }
    }
    crossing_points(&mut points, &mut index, &segments, axis)?;
    let atomic = atomic_segments(&points, &segments, axis)?;
    let mut order: Vec<usize> = (3..points.len()).collect();
    order.sort_by(|&a, &b| points[a].cmp(&points[b]).then(a.cmp(&b)));
    let mut triangulation = Triangulation::new(points, axis)?;
    for i in order {
        triangulation.insert_point(i)?;
    }
    for &edge in atomic.keys() {
        triangulation.insert_constraint(edge)?;
    }
    let mut triangles: Vec<[usize; 3]> = triangulation.triangles.into_iter().flatten().collect();
    if reversed {
        for triangle in &mut triangles {
            triangle.swap(1, 2);
        }
    }
    let dirty = atomic
        .into_iter()
        .filter_map(|(edge, dirty)| dirty.then_some(edge))
        .collect();
    Ok(Patch {
        points: triangulation.points,
        triangles,
        dirty,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn p(x: f64, y: f64) -> Point {
        Point::from_binary64([x, y, 0.0]).unwrap()
    }

    fn triangle() -> [Point; 3] {
        [p(0.0, 0.0), p(8.0, 0.0), p(0.0, 8.0)]
    }

    fn area(patch: &Patch) -> f64 {
        patch
            .triangles
            .iter()
            .map(|t| {
                let [a, b, c] = t.map(|i| patch.points[i].binary64().unwrap());
                ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) / 2.0
            })
            .sum()
    }

    fn check_area(patch: &Patch, expected: f64) {
        let mut edges: BTreeMap<[usize; 2], usize> = BTreeMap::new();
        for triangle in &patch.triangles {
            assert_eq!(
                orient2d(
                    &patch.points[triangle[0]],
                    &patch.points[triangle[1]],
                    &patch.points[triangle[2]],
                    2
                )
                .unwrap(),
                Sign::Positive
            );
            for i in 0..3 {
                *edges
                    .entry(key(triangle[i], triangle[(i + 1) % 3]))
                    .or_default() += 1;
            }
        }
        assert!(edges.values().all(|&n| n <= 2));
        assert!(patch.dirty.iter().all(|edge| edges.contains_key(edge)));
        assert_eq!(area(patch), expected);
    }

    fn check(patch: &Patch) {
        check_area(patch, 32.0);
    }

    #[test]
    fn isolated_points_and_boundary_subdivisions_preserve_the_triangle() {
        let patch = arrange(
            triangle(),
            &[Contact::Point(p(2.0, 2.0)), Contact::Point(p(4.0, 0.0))],
        )
        .unwrap();
        check(&patch);
        assert_eq!(patch.points.len(), 5);
        assert!(patch.dirty.is_empty());
    }

    #[test]
    fn crossing_and_overlapping_constraints_split_at_exact_shared_points() {
        let contacts = [
            Contact::Segment([p(0.0, 2.0), p(6.0, 2.0)]),
            Contact::Segment([p(2.0, 0.0), p(2.0, 6.0)]),
            Contact::Segment([p(1.0, 2.0), p(4.0, 2.0)]),
        ];
        let patch = arrange(triangle(), &contacts).unwrap();
        check(&patch);
        assert!(patch.points.contains(&p(2.0, 2.0)));
        assert_eq!(patch.dirty.len(), 6);
    }

    #[test]
    fn a_closed_inner_loop_and_disjoint_contacts_leave_no_holes_in_the_arrangement() {
        let contacts = [
            Contact::Coplanar(vec![p(1.0, 1.0), p(2.0, 1.0), p(1.0, 2.0)]),
            Contact::Coplanar(vec![p(4.0, 1.0), p(5.0, 1.0), p(4.0, 2.0)]),
        ];
        let patch = arrange(triangle(), &contacts).unwrap();
        check(&patch);
        assert_eq!(patch.dirty.len(), 6);
    }

    #[test]
    fn a_corridor_retains_repeated_corner_occurrences_and_an_untouched_island() {
        let patch = arrange(
            [p(0.0, 0.0), p(50.0, 0.0), p(0.0, 50.0)],
            &[
                Contact::Point(p(18.0, 30.0)),
                Contact::Point(p(8.0, 21.0)),
                Contact::Point(p(24.0, 12.0)),
                Contact::Point(p(2.0, 8.0)),
                Contact::Point(p(23.0, 10.0)),
                Contact::Segment([p(0.0, 0.0), p(18.0, 30.0)]),
            ],
        )
        .unwrap();
        check_area(&patch, 1250.0);
        assert_eq!(patch.points.len(), 8);
        let used: BTreeSet<usize> = patch.triangles.iter().flatten().copied().collect();
        assert_eq!(used.len(), patch.points.len());
        assert_eq!(patch.dirty, BTreeSet::from([[0, 3]]));
        assert!(patch.triangles.iter().any(|triangle| {
            let mut corners = *triangle;
            corners.sort_unstable();
            corners == [1, 5, 7]
        }));
    }
}
