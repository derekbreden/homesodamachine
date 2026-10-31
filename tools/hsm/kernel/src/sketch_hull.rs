//! The convex hull of circles and points, as CadQuery's `Sketch.hull` finds it: the march of Yue,
//! Murray, Corney and Clark for lines and circular arcs. From the lowest entity it goes
//! counterclockwise, each step to the entity whose tangent leaves at the least angle not below the
//! last step's, until it is back at the start.
//!
//! The outline keeps CadQuery's order, which is the order OCCT walks its face's outer wire in: the
//! segment leaving the start, then each arc and the segment after it, and the start's own arc
//! last. An arc runs counterclockwise from where the segment before it lands to where the next
//! leaves, at OCCT's parameters for it: the start angle in [0, 2π) and the end angle within one
//! turn above it.
use crate::math::{PI, TAU, V2, atan2, degrees, radians, v2};
use crate::plane::Plane;
use crate::profile::{Loop, Seg};
use crate::thru::{LoftEdge, LoftSection};
use anyhow::{Result, bail, ensure};

/// A circle or a point the hull wraps.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Wrapped {
    Circle { c: V2, r: f64 },
    Point(V2),
}

/// One edge of a hull outline.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum HullEdge {
    Line { a: V2, b: V2 },
    /// Counterclockwise about `c` from angle `t0` to `t1`, from `a` to `b`.
    Arc { c: V2, r: f64, t0: f64, t1: f64, a: V2, b: V2 },
}

#[derive(Clone, Copy, Debug)]
struct Segment {
    a: V2,
    b: V2,
}

#[derive(Clone, Copy, Debug)]
enum Step {
    Entity(usize),
    Segment(Segment),
}

/// `atan2(y, x)` turned into [0, 2π), CadQuery's `atan2p`.
fn atan2p(x: f64, y: f64) -> f64 {
    let rv = atan2(y, x);
    if rv < 0.0 { (TAU + rv) % TAU } else { rv }
}

/// The two points where the tangents from `p` touch the circle about `c` of radius `r`.
fn tangent_points(p: V2, c: V2, r: f64) -> (f64, f64, f64, f64) {
    let (dx, dy) = (p.x - c.x, p.y - c.y);
    let l = (dx * dx + dy * dy).sqrt();
    let l2 = l * l;
    let root = (l2 - r * r).sqrt();
    let x1 = r * r / l2 * dx - r / l2 * root * dy + c.x;
    let y1 = r * r / l2 * dy + r / l2 * root * dx + c.y;
    let x2 = r * r / l2 * dx + r / l2 * root * dy + c.x;
    let y2 = r * r / l2 * dy - r / l2 * root * dx + c.y;
    (x1, y1, x2, y2)
}

/// The first index of the least value, as numpy's `argmin`.
fn argmin(values: &[f64]) -> usize {
    let mut best = 0;
    for (i, v) in values.iter().enumerate() {
        if *v < values[best] {
            best = i;
        }
    }
    best
}

fn pt_pt(p1: V2, p2: V2) -> (f64, Segment) {
    let (dx, dy) = (p2.x - p1.x, p2.y - p1.y);
    let angle = if dx != 0.0 || dy != 0.0 { atan2p(dx, dy) } else { 0.0 };
    (angle, Segment { a: p1, b: p2 })
}

fn pt_arc(p: V2, c: V2, r: f64) -> (f64, Segment) {
    let (x1, y1, x2, y2) = tangent_points(p, c, r);
    let angles = [atan2p(x1 - p.x, y1 - p.y), atan2p(x2 - p.x, y2 - p.y)];
    let points = [v2(x1, y1), v2(x2, y2)];
    let ix = argmin(&angles);
    (angles[ix], Segment { a: p, b: points[ix] })
}

fn arc_pt(c: V2, r: f64, p: V2) -> (f64, Segment) {
    let (x1, y1, x2, y2) = tangent_points(p, c, r);
    let angles = [atan2p(p.x - x1, p.y - y1), atan2p(p.x - x2, p.y - y2)];
    let points = [v2(x1, y1), v2(x2, y2)];
    // numpy's argmax: the first index of the greatest value.
    let ix = if angles[1] > angles[0] { 1 } else { 0 };
    (angles[ix], Segment { a: points[ix], b: p })
}

fn arc_arc(c1: V2, r1: f64, c2: V2, r2: f64) -> (f64, Segment) {
    let (dx1, dy1, dx2, dy2);
    if r1 > r2 {
        let delta_r = r1 - r2;
        let (xt1, yt1, xt2, yt2) = tangent_points(c2, c1, delta_r);
        dx1 = (xt1 - c1.x) / delta_r;
        dy1 = (yt1 - c1.y) / delta_r;
        dx2 = (xt2 - c1.x) / delta_r;
        dy2 = (yt2 - c1.y) / delta_r;
    } else if r1 < r2 {
        let delta_r = r2 - r1;
        let (xt1, yt1, xt2, yt2) = tangent_points(c1, c2, delta_r);
        dx1 = (xt1 - c2.x) / delta_r;
        dy1 = (yt1 - c2.y) / delta_r;
        dx2 = (xt2 - c2.x) / delta_r;
        dy2 = (yt2 - c2.y) / delta_r;
    } else {
        let (dx, dy) = (c2.x - c1.x, c2.y - c1.y);
        let l = (dx * dx + dy * dy).sqrt();
        let (dx, dy) = (dx / l, dy / l);
        dx1 = -dy;
        dy1 = dx;
        dx2 = dy;
        dy2 = -dx;
    }
    let (x11, y11) = (c1.x + dx1 * r1, c1.y + dy1 * r1);
    let (x12, y12) = (c1.x + dx2 * r1, c1.y + dy2 * r1);
    let (x21, y21) = (c2.x + dx1 * r2, c2.y + dy1 * r2);
    let (x22, y22) = (c2.x + dx2 * r2, c2.y + dy2 * r2);
    let a1_out = atan2p(x21 - x11, y21 - y11);
    let a2_out = atan2p(x22 - x12, y22 - y12);
    // The tangent that leaves the way the first circle turns counterclockwise.
    let a11 = (atan2p(x11 - c1.x, y11 - c1.y) + PI / 2.0) % TAU;
    let a21 = (atan2p(x12 - c1.x, y12 - c1.y) + PI / 2.0) % TAU;
    if (a21 - a2_out).abs() < (a11 - a1_out).abs() {
        (a2_out, Segment { a: v2(x12, y12), b: v2(x22, y22) })
    } else {
        (a1_out, Segment { a: v2(x11, y11), b: v2(x21, y21) })
    }
}

fn angle_to(current: &Wrapped, e: &Wrapped) -> (f64, Segment) {
    match (*current, *e) {
        (Wrapped::Point(p), Wrapped::Point(q)) => pt_pt(p, q),
        (Wrapped::Point(p), Wrapped::Circle { c, r }) => pt_arc(p, c, r),
        (Wrapped::Circle { c, r }, Wrapped::Point(p)) => arc_pt(c, r, p),
        (Wrapped::Circle { c: c1, r: r1 }, Wrapped::Circle { c: c2, r: r2 }) => arc_arc(c1, r1, c2, r2),
    }
}

/// The lowest of points by y, then x, the first of equals: numpy's `lexsort((x, y))[0]`.
fn lowest(points: &[V2]) -> usize {
    let mut best = 0;
    for (i, p) in points.iter().enumerate() {
        let q = points[best];
        if p.y < q.y || (p.y == q.y && p.x < q.x) {
            best = i;
        }
    }
    best
}

/// OCCT's arc of a circle from `a1` to `a2` degrees, counterclockwise: the parameters
/// `GC_MakeArcOfCircle` trims it to.
fn arc_params(a1: f64, a2: f64) -> (f64, f64) {
    let (u1, u2) = (radians(a1), radians(a2));
    let preci = ((u2 - u1).abs() / 2.0).min(1e-9);
    let mut u1 = u1 - ((u1 / TAU).floor()) * TAU;
    if TAU - u1 < preci {
        u1 -= TAU;
    }
    let mut u2 = u2 - ((u2 - u1) / TAU).floor() * TAU;
    if u2 - u1 < preci {
        u2 += TAU;
    }
    (u1, u2)
}

/// The hull's edges in CadQuery's order. Circles are whole circles, CadQuery's
/// `Sketch.arc(c, r, 0, 360)`; at least one entity must be a circle or two must be points.
pub fn hull_edges(entities: &[Wrapped]) -> Result<Vec<HullEdge>> {
    ensure!(!entities.is_empty(), "a hull of nothing");
    // CadQuery's tangents need every circle and point clear of every circle's inside.
    for (i, a) in entities.iter().enumerate() {
        for b in &entities[i + 1..] {
            let inside = match (*a, *b) {
                (Wrapped::Circle { c, r }, Wrapped::Circle { c: d, r: s }) => (c - d).norm() <= (r - s).abs(),
                (Wrapped::Circle { c, r }, Wrapped::Point(p)) | (Wrapped::Point(p), Wrapped::Circle { c, r }) => {
                    (p - c).norm() <= r
                }
                _ => false,
            };
            ensure!(!inside, "a hull of {a:?} and {b:?}, one inside the other");
        }
    }
    // CadQuery lists the arcs before the points; the start is the lowest arc or point.
    let mut order: Vec<usize> = (0..entities.len()).filter(|&i| matches!(entities[i], Wrapped::Circle { .. })).collect();
    order.extend((0..entities.len()).filter(|&i| matches!(entities[i], Wrapped::Point(_))));
    let arcs: Vec<usize> = order.iter().copied().filter(|&i| matches!(entities[i], Wrapped::Circle { .. })).collect();
    let points: Vec<usize> = order.iter().copied().filter(|&i| matches!(entities[i], Wrapped::Point(_))).collect();
    let bottom = |i: usize| match entities[i] {
        Wrapped::Circle { c, r } => v2(c.x, c.y - r),
        Wrapped::Point(p) => p,
    };
    let start = match (points.is_empty(), arcs.is_empty()) {
        (true, false) => arcs[lowest(&arcs.iter().map(|&i| bottom(i)).collect::<Vec<_>>())],
        (false, true) => points[lowest(&points.iter().map(|&i| bottom(i)).collect::<Vec<_>>())],
        (false, false) => {
            let p = points[lowest(&points.iter().map(|&i| bottom(i)).collect::<Vec<_>>())];
            let a = arcs[lowest(&arcs.iter().map(|&i| bottom(i)).collect::<Vec<_>>())];
            if lowest(&[bottom(p), bottom(a)]) == 0 { p } else { a }
        }
        (true, true) => bail!("a hull of nothing"),
    };
    let mut hull = vec![Step::Entity(start)];
    let mut live = order;
    let (mut current, mut current_angle) = (start, 0.0);
    for _ in 0..=4 * entities.len() + 4 {
        let mut angles = vec![];
        let mut segments = vec![];
        for &e in &live {
            let (angle, segment) = if e == current {
                (f64::INFINITY, Segment { a: v2(f64::INFINITY, f64::INFINITY), b: v2(f64::INFINITY, f64::INFINITY) })
            } else {
                angle_to(&entities[current], &entities[e])
            };
            angles.push(if angle >= current_angle { angle } else { f64::INFINITY });
            segments.push(segment);
        }
        let ix = argmin(&angles);
        ensure!(angles[ix].is_finite(), "a hull march that found no next entity");
        let next = live[ix];
        if matches!(entities[next], Wrapped::Point(_)) {
            live.remove(ix);
        }
        hull.push(Step::Segment(segments[ix]));
        hull.push(Step::Entity(next));
        current = next;
        current_angle = angles[ix];
        if next == start {
            return finalize(entities, &hull);
        }
    }
    bail!("a hull march that never came back to its start")
}

fn finalize(entities: &[Wrapped], hull: &[Step]) -> Result<Vec<HullEdge>> {
    let arc = |i: usize, before: &Segment, after: &Segment| -> Result<HullEdge> {
        let Wrapped::Circle { c, r } = entities[i] else { bail!("an arc of a point") };
        let a1 = degrees(atan2p(before.b.x - c.x, before.b.y - c.y));
        let a2 = degrees(atan2p(after.a.x - c.x, after.a.y - c.y));
        ensure!(a1 != a2, "a hull arc of no length, which CadQuery makes a whole circle");
        let (t0, t1) = arc_params(a1, a2);
        Ok(HullEdge::Arc { c, r, t0, t1, a: before.b, b: after.a })
    };
    let mut out = vec![];
    for w in hull.windows(3) {
        match (w[0], w[1], w[2]) {
            (_, Step::Segment(s), _) => out.push(HullEdge::Line { a: s.a, b: s.b }),
            (Step::Segment(before), Step::Entity(i), Step::Segment(after))
                if matches!(entities[i], Wrapped::Circle { .. }) =>
            {
                out.push(arc(i, &before, &after)?)
            }
            _ => {}
        }
    }
    let n = hull.len();
    if let (Step::Segment(before), Step::Entity(i), Step::Segment(first)) = (hull[n - 2], hull[n - 1], hull[1]) {
        if matches!(entities[i], Wrapped::Circle { .. }) {
            out.push(arc(i, &before, &first)?);
        }
    }
    Ok(out)
}

/// The hull as a kernel loop, counterclockwise.
pub fn hull_loop(entities: &[Wrapped]) -> Result<Loop> {
    let segs = hull_edges(entities)?
        .into_iter()
        .map(|e| match e {
            HullEdge::Line { a, b } => Seg::Line { a, b },
            HullEdge::Arc { c, a, b, .. } => Seg::Arc { a, b, c, ccw: true },
        })
        .collect();
    Loop::new(segs)
}

/// The hull placed on `plane` as a loft section, each edge as OCCT has it.
pub fn hull_section(entities: &[Wrapped], plane: &Plane) -> Result<LoftSection> {
    let edges = hull_edges(entities)?
        .into_iter()
        .map(|e| match e {
            HullEdge::Line { a, b } => LoftEdge::Line { a: plane.point(a), b: plane.point(b) },
            HullEdge::Arc { c, r, t0, t1, .. } => {
                LoftEdge::Conic { c: plane.point(c), x: plane.x * r, y: plane.y * r, t0, t1 }
            }
        })
        .collect();
    Ok(LoftSection::new(edges))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn arcs_close_on_the_segments() {
        let e = [
            Wrapped::Circle { c: v2(0.0, 0.0), r: 5.0 },
            Wrapped::Circle { c: v2(3.0, 6.0), r: 1.25 },
            Wrapped::Circle { c: v2(-3.0, 6.0), r: 1.25 },
        ];
        let lp = hull_loop(&e).unwrap();
        assert_eq!(lp.segs.len(), 6);
        assert!(lp.area() > 0.0);
    }
}
