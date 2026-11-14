//! A polygon's buffer edges as GEOS's buffer builds them: its input simplification, offset
//! segments, round joins and double-double predicates make the offset curves, which are noded
//! where they cross and kept where the buffer lies on a single side. Curves that overlap are
//! refused, since GEOS would merge their edges.

use anyhow::{Result, bail, ensure};

pub type Point = [f64; 2];

const PI_OVER_2: f64 = std::f64::consts::PI / 2.0;
const PI_TIMES_2: f64 = 2.0 * std::f64::consts::PI;
const CURVE_VERTEX_SNAP_DISTANCE_FACTOR: f64 = 1.0e-4;
const OFFSET_SEGMENT_SEPARATION_FACTOR: f64 = 1.0e-3;
const INSIDE_TURN_VERTEX_SNAP_DISTANCE_FACTOR: f64 = 1.0e-3;
const SIMPLIFY_FACTOR: f64 = 100.0;
const MAX_CLOSING_SEG_LEN_FACTOR: f64 = 80.0;
const MAX_INVERTED_RING_SIZE: usize = 9;
const NUM_PTS_TO_CHECK: usize = 10;
const SPLIT: f64 = 134217729.0;

/// GEOS's double-double number.
#[derive(Clone, Copy, Debug)]
struct DD {
    hi: f64,
    lo: f64,
}

impl DD {
    fn of(x: f64) -> DD {
        DD { hi: x, lo: 0.0 }
    }

    fn add(self, y: DD) -> DD {
        let (hi, lo, yhi, ylo) = (self.hi, self.lo, y.hi, y.lo);
        let s_ = hi + yhi;
        let t_ = lo + ylo;
        let mut e = s_ - hi;
        let f = t_ - lo;
        let mut s = s_ - e;
        let mut t = t_ - f;
        s = (yhi - e) + (hi - s);
        t = (ylo - f) + (lo - t);
        e = s + t_;
        let h_ = s_ + e;
        let h = e + (s_ - h_);
        e = t + h;
        let zhi = h_ + e;
        let zlo = e + (h_ - zhi);
        DD { hi: zhi, lo: zlo }
    }

    fn sub(self, y: DD) -> DD {
        self.add(DD { hi: -1.0 * y.hi, lo: -1.0 * y.lo })
    }

    fn mul(self, y: DD) -> DD {
        let (hi, lo, yhi, ylo) = (self.hi, self.lo, y.hi, y.lo);
        let mut c_ = SPLIT * hi;
        let mut hx = c_ - hi;
        let mut c = SPLIT * yhi;
        hx = c_ - hx;
        let tx = hi - hx;
        let mut hy = c - yhi;
        c_ = hi * yhi;
        hy = c - hy;
        let ty = yhi - hy;
        c = ((((hx * hy - c_) + hx * ty) + tx * hy) + tx * ty) + (hi * ylo + lo * yhi);
        let zhi = c_ + c;
        hx = c_ - zhi;
        let zlo = c + hx;
        DD { hi: zhi, lo: zlo }
    }

    fn div(self, y: DD) -> DD {
        let (hi, lo, yhi, ylo) = (self.hi, self.lo, y.hi, y.lo);
        let c_ = hi / yhi;
        let mut c = SPLIT * c_;
        let mut hc = c - c_;
        let mut u = SPLIT * yhi;
        hc = c - hc;
        let tc = c_ - hc;
        let mut hy = u - yhi;
        let u_ = c_ * yhi;
        hy = u - hy;
        let ty = yhi - hy;
        u = (((hc * hy - u_) + hc * ty) + tc * hy) + tc * ty;
        c = ((((hi - u_) - u) + lo) - c_ * ylo) / yhi;
        u = c_ + c;
        DD { hi: u, lo: (c_ - u) + c }
    }

    fn value(self) -> f64 {
        self.hi + self.lo
    }

    fn sign(self) -> i32 {
        if self.hi < 0.0 || (self.hi == 0.0 && self.lo < 0.0) {
            -1
        } else if self.hi > 0.0 || (self.hi == 0.0 && self.lo > 0.0) {
            1
        } else {
            0
        }
    }
}

/// GEOS's orientation index: positive when `q` is left of `p1`→`p2`, negative when right, zero
/// when on it.
pub fn orientation(p1: Point, p2: Point, q: Point) -> i32 {
    let (pax, pay, pbx, pby, pcx, pcy) = (p1[0], p1[1], p2[0], p2[1], q[0], q[1]);
    let detleft = (pax - pcx) * (pby - pcy);
    let detright = (pay - pcy) * (pbx - pcx);
    let det = detleft - detright;
    let sign = |x: f64| if x > 0.0 { 1 } else if x < 0.0 { -1 } else { 0 };
    let detsum = if detleft > 0.0 {
        if detright <= 0.0 {
            return sign(det);
        }
        detleft + detright
    } else if detleft < 0.0 {
        if detright >= 0.0 {
            return sign(det);
        }
        -detleft - detright
    } else {
        return sign(det);
    };
    let errbound = 1e-15 * detsum;
    if det >= errbound || -det >= errbound {
        return sign(det);
    }
    let dx1 = DD::of(p2[0]).add(DD::of(-p1[0]));
    let dy1 = DD::of(p2[1]).add(DD::of(-p1[1]));
    let dx2 = DD::of(q[0]).add(DD::of(-p2[0]));
    let dy2 = DD::of(q[1]).add(DD::of(-p2[1]));
    dx1.mul(dy2).sub(dy1.mul(dx2)).sign()
}

/// GEOS's double-double intersection of the lines through the segments.
fn line_intersection(p1: Point, p2: Point, q1: Point, q2: Point) -> Option<Point> {
    let [p1x, p1y, p2x, p2y] = [p1[0], p1[1], p2[0], p2[1]].map(DD::of);
    let [q1x, q1y, q2x, q2y] = [q1[0], q1[1], q2[0], q2[1]].map(DD::of);
    let px = p1y.sub(p2y);
    let py = p2x.sub(p1x);
    let pw = p1x.mul(p2y).sub(p2x.mul(p1y));
    let qx = q1y.sub(q2y);
    let qy = q2x.sub(q1x);
    let qw = q1x.mul(q2y).sub(q2x.mul(q1y));
    let x = py.mul(qw).sub(qy.mul(pw));
    let y = qx.mul(pw).sub(px.mul(qw));
    let w = px.mul(qy).sub(qx.mul(py));
    let (xi, yi) = (x.div(w).value(), y.div(w).value());
    (xi.is_finite() && yi.is_finite()).then_some([xi, yi])
}

fn distance(a: Point, b: Point) -> f64 {
    let (dx, dy) = (a[0] - b[0], a[1] - b[1]);
    (dx * dx + dy * dy).sqrt()
}

/// GEOS's distance from `p` to the segment `a`–`b`.
pub fn point_to_segment(p: Point, a: Point, b: Point) -> f64 {
    if a == b {
        return distance(p, a);
    }
    let len2 = (b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1]);
    let r = ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / len2;
    if r <= 0.0 {
        return distance(p, a);
    }
    if r >= 1.0 {
        return distance(p, b);
    }
    let s = ((a[1] - p[1]) * (b[0] - a[0]) - (a[0] - p[0]) * (b[1] - a[1])) / len2;
    s.abs() * len2.sqrt()
}

fn envelopes_meet(p1: Point, p2: Point, q1: Point, q2: Point) -> bool {
    for i in 0..2 {
        let (minq, maxq) = (q1[i].min(q2[i]), q1[i].max(q2[i]));
        let (minp, maxp) = (p1[i].min(p2[i]), p1[i].max(p2[i]));
        if minp > maxq || maxp < minq {
            return false;
        }
    }
    true
}

fn in_envelope(p1: Point, p2: Point, q: Point) -> bool {
    (0..2).all(|i| q[i] >= p1[i].min(p2[i]) && q[i] <= p1[i].max(p2[i]))
}

fn nearest_endpoint(p1: Point, p2: Point, q1: Point, q2: Point) -> Point {
    let mut nearest = p1;
    let mut least = point_to_segment(p1, q1, q2);
    for (candidate, a, b) in [(p2, q1, q2), (q1, p1, p2), (q2, p1, p2)] {
        let d = point_to_segment(candidate, a, b);
        if d < least {
            least = d;
            nearest = candidate;
        }
    }
    nearest
}

/// How segments meet, as GEOS's line intersector finds it.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Meeting {
    Apart,
    /// One point, and whether it lies inside both segments.
    Point(Point, bool),
    /// An overlap, with its first point.
    Overlap(Point),
}

/// GEOS's line intersector on the segments `p1`–`p2` and `q1`–`q2`.
pub fn meet(p1: Point, p2: Point, q1: Point, q2: Point) -> Meeting {
    if !envelopes_meet(p1, p2, q1, q2) {
        return Meeting::Apart;
    }
    let (pq1, pq2) = (orientation(p1, p2, q1), orientation(p1, p2, q2));
    if (pq1 > 0 && pq2 > 0) || (pq1 < 0 && pq2 < 0) {
        return Meeting::Apart;
    }
    let (qp1, qp2) = (orientation(q1, q2, p1), orientation(q1, q2, p2));
    if (qp1 > 0 && qp2 > 0) || (qp1 < 0 && qp2 < 0) {
        return Meeting::Apart;
    }
    if pq1 == 0 && pq2 == 0 && qp1 == 0 && qp2 == 0 {
        return collinear(p1, p2, q1, q2);
    }
    if pq1 == 0 || pq2 == 0 || qp1 == 0 || qp2 == 0 {
        let p = if p1 == q1 || p1 == q2 {
            p1
        } else if p2 == q1 || p2 == q2 {
            p2
        } else if pq1 == 0 {
            q1
        } else if pq2 == 0 {
            q2
        } else if qp1 == 0 {
            p1
        } else {
            p2
        };
        return Meeting::Point(p, false);
    }
    let mut p = line_intersection(p1, p2, q1, q2).unwrap_or_else(|| nearest_endpoint(p1, p2, q1, q2));
    if !(in_envelope(p1, p2, p) && in_envelope(q1, q2, p)) {
        p = nearest_endpoint(p1, p2, q1, q2);
    }
    Meeting::Point(p, true)
}

fn collinear(p1: Point, p2: Point, q1: Point, q2: Point) -> Meeting {
    let (q1in, q2in) = (in_envelope(p1, p2, q1), in_envelope(p1, p2, q2));
    let (p1in, p2in) = (in_envelope(q1, q2, p1), in_envelope(q1, q2, p2));
    if q1in && q2in {
        return Meeting::Overlap(q1);
    }
    if p1in && p2in {
        return Meeting::Overlap(p1);
    }
    let single = |first: Point, touch: bool| if touch { Meeting::Point(first, false) } else { Meeting::Overlap(first) };
    if q1in && p1in {
        return single(q1, q1 == p1 && !q2in && !p2in);
    }
    if q1in && p2in {
        return single(q1, q1 == p2 && !q2in && !p1in);
    }
    if q2in && p1in {
        return single(q2, q2 == p1 && !q1in && !p2in);
    }
    if q2in && p2in {
        return single(q2, q2 == p2 && !q1in && !p1in);
    }
    Meeting::Apart
}

/// GEOS's signed ring area, positive for a clockwise ring.
pub fn signed_area(ring: &[Point]) -> f64 {
    let n = ring.len();
    if n < 3 {
        return 0.0;
    }
    let x0 = ring[0][0];
    let (mut p1, mut p2) = (ring[0], ring[1]);
    p2[0] -= x0;
    let mut sum = 0.0;
    for i in 1..n - 1 {
        let p0y = p1[1];
        p1 = p2;
        p2 = ring[i + 1];
        p2[0] -= x0;
        sum += p1[0] * (p0y - p2[1]);
    }
    sum / 2.0
}

/// GEOS's buffer input simplification: removes shallow concavities on the side being offset.
fn simplify(line: &[Point], tolerance: f64) -> Vec<Point> {
    let tol = tolerance.abs();
    let wanted = if tolerance < 0.0 { -1 } else { 1 };
    let mut deleted = vec![false; line.len()];
    let next = |deleted: &[bool], index: usize| {
        let mut n = index + 1;
        while n < line.len() && deleted[n] {
            n += 1;
        }
        n
    };
    let shallow = |p0: Point, p1: Point, p2: Point| point_to_segment(p1, p0, p2) < tol;
    loop {
        let mut changed = false;
        let mut index = 1;
        let mut mid = next(&deleted, index);
        let mut last = next(&deleted, mid);
        while last < line.len() {
            let (p0, p1, p2) = (line[index], line[mid], line[last]);
            let mut deletable = orientation(p0, p1, p2) == wanted && shallow(p0, p1, p2);
            if deletable {
                let step = ((last - index) / NUM_PTS_TO_CHECK).max(1);
                deletable = (index..last).step_by(step).all(|i| shallow(p0, p1, line[i]));
            }
            if deletable {
                deleted[mid] = true;
                changed = true;
                index = last;
            } else {
                index = mid;
            }
            mid = next(&deleted, index);
            last = next(&deleted, mid);
        }
        if !changed {
            break;
        }
    }
    let mut out: Vec<Point> = Vec::with_capacity(line.len());
    for (p, gone) in line.iter().zip(&deleted) {
        if !gone && out.last() != Some(p) {
            out.push(*p);
        }
    }
    out
}

/// The side of a ring's travel an offset lies on.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Side {
    Left,
    Right,
}

impl Side {
    fn opposite(self) -> Side {
        match self {
            Side::Left => Side::Right,
            Side::Right => Side::Left,
        }
    }
}

/// GEOS's offset segment generator with round joins.
struct Generator {
    distance: f64,
    side: Side,
    quantum: f64,
    closing: f64,
    min_vertex: f64,
    pts: Vec<Point>,
    s0: Point,
    s1: Point,
    s2: Point,
    offset0: [Point; 2],
    offset1: [Point; 2],
    closing_segments: bool,
}

impl Generator {
    fn new(distance: f64, quadrant_segments: u32) -> Self {
        let quadrant_segments = quadrant_segments.max(1);
        Self {
            distance, side: Side::Left, quantum: PI_OVER_2 / quadrant_segments as f64,
            closing: if quadrant_segments >= 8 { MAX_CLOSING_SEG_LEN_FACTOR } else { 1.0 },
            min_vertex: distance * CURVE_VERTEX_SNAP_DISTANCE_FACTOR, pts: Vec::new(),
            s0: [0.0; 2], s1: [0.0; 2], s2: [0.0; 2], offset0: [[0.0; 2]; 2], offset1: [[0.0; 2]; 2],
            closing_segments: false,
        }
    }

    fn add(&mut self, p: Point) {
        if let Some(last) = self.pts.last() {
            if distance(p, *last) < self.min_vertex {
                return;
            }
        }
        self.pts.push(p);
    }

    fn close(&mut self) {
        if let (Some(first), Some(last)) = (self.pts.first().copied(), self.pts.last().copied()) {
            if first != last {
                self.pts.push(first);
            }
        }
    }

    fn offset(&self, p0: Point, p1: Point) -> [Point; 2] {
        let sign = if self.side == Side::Left { 1.0 } else { -1.0 };
        let (dx, dy) = (p1[0] - p0[0], p1[1] - p0[1]);
        let len = (dx * dx + dy * dy).sqrt();
        let ux = sign * self.distance * dx / len;
        let uy = sign * self.distance * dy / len;
        [[p0[0] - uy, p0[1] + ux], [p1[0] - uy, p1[1] + ux]]
    }

    fn init(&mut self, s1: Point, s2: Point, side: Side) {
        self.s1 = s1;
        self.s2 = s2;
        self.side = side;
        self.offset1 = self.offset(s1, s2);
    }

    fn next_segment(&mut self, p: Point, add_start: bool) {
        if self.s2 == p {
            return;
        }
        self.s0 = self.s1;
        self.s1 = self.s2;
        self.s2 = p;
        self.offset0 = self.offset(self.s0, self.s1);
        self.offset1 = self.offset(self.s1, self.s2);
        let turn = orientation(self.s0, self.s1, self.s2);
        let outside = (turn == -1 && self.side == Side::Left) || (turn == 1 && self.side == Side::Right);
        if turn == 0 {
            if matches!(meet(self.s0, self.s1, self.s1, self.s2), Meeting::Overlap(_)) {
                self.corner(self.s1, self.offset0[1], self.offset1[0], -1);
            }
        } else if outside {
            if distance(self.offset0[1], self.offset1[0]) < self.distance * OFFSET_SEGMENT_SEPARATION_FACTOR {
                self.add(self.offset0[1]);
                return;
            }
            if add_start {
                self.add(self.offset0[1]);
            }
            self.corner(self.s1, self.offset0[1], self.offset1[0], turn);
            self.add(self.offset1[0]);
        } else {
            let [a, b] = self.offset0;
            let [c, d] = self.offset1;
            match meet(a, b, c, d) {
                Meeting::Point(q, _) | Meeting::Overlap(q) => self.add(q),
                Meeting::Apart => {
                    if distance(b, c) < self.distance * INSIDE_TURN_VERTEX_SNAP_DISTANCE_FACTOR {
                        self.add(b);
                    } else {
                        self.closing_segments = true;
                        let k = self.closing;
                        let s1 = self.s1;
                        self.add(b);
                        self.add([(k * b[0] + s1[0]) / (k + 1.0), (k * b[1] + s1[1]) / (k + 1.0)]);
                        self.add([(k * c[0] + s1[0]) / (k + 1.0), (k * c[1] + s1[1]) / (k + 1.0)]);
                        self.add(c);
                    }
                }
            }
        }
    }

    /// A round join about `p` from `p0` to `p1`, turning as `direction` says.
    fn corner(&mut self, p: Point, p0: Point, p1: Point, direction: i32) {
        let mut start = (p0[1] - p[1]).atan2(p0[0] - p[0]);
        let end = (p1[1] - p[1]).atan2(p1[0] - p[0]);
        if direction == -1 {
            if start <= end {
                start += PI_TIMES_2;
            }
        } else if start >= end {
            start -= PI_TIMES_2;
        }
        self.add(p0);
        let factor = if direction == -1 { -1 } else { 1 };
        let total = (start - end).abs();
        let segments = (total / self.quantum + 0.5) as i32;
        if segments >= 1 {
            let increment = total / segments as f64;
            for i in 0..segments {
                let angle = start + (factor * i) as f64 * increment;
                let (mut s, mut c) = (angle.sin(), angle.cos());
                if s.abs() < 5e-16 {
                    s = 0.0;
                }
                if c.abs() < 5e-16 {
                    c = 0.0;
                }
                self.add([p[0] + self.distance * c, p[1] + self.distance * s]);
            }
        }
        self.add(p1);
    }
}

/// GEOS's offset curve of a closed ring, `distance` to its `side`.
fn ring_curve(ring: &[Point], side: Side, distance: f64, quadrant_segments: u32) -> Result<(Vec<Point>, bool)> {
    ensure!(ring.len() > 3 && ring.first() == ring.last(), "an offset needs a closed ring");
    let mut generator = Generator::new(distance, quadrant_segments);
    let mut tolerance = distance / SIMPLIFY_FACTOR;
    if side == Side::Right {
        tolerance = -tolerance;
    }
    let simplified = simplify(ring, tolerance);
    let n = simplified.len() - 1;
    generator.init(simplified[n - 1], simplified[0], side);
    for (i, p) in simplified.iter().enumerate().skip(1) {
        generator.next_segment(*p, i != 1);
    }
    generator.close();
    Ok((generator.pts, generator.closing_segments))
}

fn without_repeats(ring: &[Point]) -> Vec<Point> {
    let mut out: Vec<Point> = Vec::with_capacity(ring.len());
    for p in ring {
        if out.last() != Some(p) {
            out.push(*p);
        }
    }
    out
}

fn fully_eroded(ring: &[Point], hole: bool, distance: f64) -> Result<bool> {
    if ring.len() < 4 {
        return Ok(true);
    }
    ensure!(ring.len() > 4, "a triangle's erosion is not offset here");
    if (hole && distance > 0.0) || (!hole && distance < 0.0) {
        let (mut lo, mut hi) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
        for p in ring {
            for i in 0..2 {
                lo[i] = lo[i].min(p[i]);
                hi[i] = hi[i].max(p[i]);
            }
        }
        let least = (hi[1] - lo[1]).min(hi[0] - lo[0]);
        return Ok(2.0 * distance.abs() > least);
    }
    Ok(false)
}

/// A polygon as rings: its shell, then its holes.
#[derive(Clone, Debug)]
pub struct Polygon {
    pub shell: Vec<Point>,
    pub holes: Vec<Vec<Point>>,
}

fn segments(ring: &[Point]) -> impl Iterator<Item = (Point, Point)> + '_ {
    ring.windows(2).map(|w| (w[0], w[1]))
}

/// The offset curves of the polygon's rings, as GEOS's buffer generates them before noding, each
/// with whether the buffer's area lies on its right.
fn curves(polygon: &Polygon, distance: f64, quadrant_segments: u32) -> Result<Vec<(Vec<Point>, bool, bool)>> {
    let (offset, side) = if distance < 0.0 { (-distance, Side::Right) } else { (distance, Side::Left) };
    if distance < 0.0 && fully_eroded(&polygon.shell, false, distance)? {
        return Ok(Vec::new());
    }
    let mut out = Vec::new();
    // The area lies right of a clockwise shell and of a counterclockwise hole, as GEOS labels them.
    let mut add = |ring: &[Point], side: Side, hole: bool| -> Result<()> {
        let ring = without_repeats(ring);
        let ccw = signed_area(&ring) < 0.0;
        let flipped = ring.len() >= 4 && ccw;
        let side = if flipped { side.opposite() } else { side };
        ensure!(ring.len() >= MAX_INVERTED_RING_SIZE, "a ring this small could invert; GEOS would rebuild it");
        let (curve, closing) = ring_curve(&ring, side, offset, quadrant_segments)?;
        out.push((curve, flipped == hole, closing));
        Ok(())
    };
    add(&polygon.shell, side, false)?;
    for hole in &polygon.holes {
        if distance > 0.0 && fully_eroded(hole, true, distance)? {
            continue;
        }
        add(hole, side.opposite(), true)?;
    }
    Ok(out)
}

/// A piece of an offset curve between nodes, with whether the buffer's area lies on its right.
#[derive(Clone, Copy, Debug)]
struct Piece {
    a: Point,
    b: Point,
    right: bool,
}

/// The pieces of the curves once GEOS's noder has split them where they cross.
fn noded(raw: &[(Vec<Point>, bool, bool)]) -> Result<Vec<Piece>> {
    let segs: Vec<(usize, usize, Point, Point, bool)> = raw.iter().enumerate()
        .flat_map(|(c, (ring, right, _))| segments(ring).enumerate().map(move |(i, (a, b))| (c, i, a, b, *right))).collect();
    let boxes: Vec<[f64; 4]> = segs.iter().map(|(_, _, a, b, _)| [a[0].min(b[0]), a[0].max(b[0]), a[1].min(b[1]), a[1].max(b[1])]).collect();
    let mut order: Vec<usize> = (0..segs.len()).collect();
    order.sort_by(|&i, &j| boxes[i][0].partial_cmp(&boxes[j][0]).unwrap());
    let mut nodes: Vec<Vec<Point>> = vec![Vec::new(); segs.len()];
    for (k, &i) in order.iter().enumerate() {
        for &j in &order[k + 1..] {
            if boxes[j][0] > boxes[i][1] {
                break;
            }
            if boxes[j][2] > boxes[i][3] || boxes[j][3] < boxes[i][2] {
                continue;
            }
            let (lo, hi) = (i.min(j), i.max(j));
            let ((ci, si, a, b, _), (cj, sj, c, d, _)) = (segs[lo], segs[hi]);
            match meet(a, b, c, d) {
                Meeting::Apart => {}
                Meeting::Overlap(_) => bail!("the offset curves overlap; GEOS would merge their edges"),
                Meeting::Point(q, _) => {
                    let count = raw[ci].0.len() - 1;
                    let neighbours = ci == cj && ((si + 1) % count == sj || (sj + 1) % count == si);
                    if neighbours {
                        continue;
                    }
                    for (n, (x, y)) in [(lo, (a, b)), (hi, (c, d))] {
                        if q != x && q != y {
                            nodes[n].push(q);
                        }
                    }
                }
            }
        }
    }
    let mut pieces = Vec::new();
    for (n, (_, _, a, b, right)) in segs.into_iter().enumerate() {
        let mut inner = std::mem::take(&mut nodes[n]);
        let along = |p: &Point| (p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1]);
        inner.sort_by(|p, q| along(p).partial_cmp(&along(q)).unwrap());
        inner.dedup();
        let mut from = a;
        for p in inner.into_iter().chain(std::iter::once(b)) {
            if p != from {
                pieces.push(Piece { a: from, b: p, right });
            }
            from = p;
        }
    }
    Ok(pieces)
}

/// The buffer's depth on each side of a piece: how many offset curves have the buffer's area
/// on that side, counted along a line through the piece's middle.
fn depths(pieces: &[Piece], index: usize) -> (i32, i32) {
    let s = pieces[index];
    // A level piece is read turned square to itself, which keeps every orientation.
    let turn = s.a[1] == s.b[1];
    let t = |p: Point| if turn { [-p[1], p[0]] } else { p };
    let (a, b) = (t(s.a), t(s.b));
    let m = [(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0];
    let mut before = 0;
    for (k, other) in pieces.iter().enumerate() {
        if k == index {
            continue;
        }
        let (c, d) = (t(other.a), t(other.b));
        if (c[1] > m[1]) == (d[1] > m[1]) {
            continue;
        }
        let upward = d[1] > c[1];
        let turn_m = orientation(c, d, m);
        let left_of_m = if upward { turn_m < 0 } else { turn_m > 0 };
        if left_of_m {
            let step = if upward { 1 } else { -1 };
            before += if other.right { step } else { -step };
        }
    }
    let upward = b[1] > a[1];
    let step = if upward { 1 } else { -1 };
    let across = before + if s.right { step } else { -step };
    // Left of an upward piece is the side before it along the line.
    if upward { (before, across) } else { (across, before) }
}

/// The edges of the polygon's buffer by `distance`, as GEOS builds them from its offset curves:
/// the curves noded where they cross, and the pieces with the buffer on a single side.
pub fn buffer_edges(polygon: &Polygon, distance: f64, quadrant_segments: u32) -> Result<Vec<(Point, Point)>> {
    let raw = curves(polygon, distance, quadrant_segments)?;
    let pieces = noded(&raw)?;
    Ok((0..pieces.len()).filter_map(|i| {
        let (left, right) = depths(&pieces, i);
        let edge = (right >= 1 && left <= 0) || (left >= 1 && right <= 0);
        edge.then_some((pieces[i].a, pieces[i].b))
    }).collect())
}

/// Whether `p` lies inside the closed ring, by crossings.
pub fn inside(p: Point, ring: &[Point]) -> bool {
    let mut crossings = 0;
    for (a, b) in segments(ring) {
        if (a[1] > p[1]) != (b[1] > p[1]) {
            let x = a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1]);
            if x > p[0] {
                crossings += 1;
            }
        }
    }
    crossings % 2 == 1
}

/// The pieces of the segment `p1`–`p2` inside the area the edges bound, in order along it, each
/// with its ends where GEOS's intersector puts them. A segment through a vertex or along an edge
/// is refused.
pub fn clip_segment(p1: Point, p2: Point, edges: &[(Point, Point)]) -> Result<Vec<(Point, Point)>> {
    let mut crossings: Vec<Point> = Vec::new();
    for (a, b) in edges {
        match meet(p1, p2, *a, *b) {
            Meeting::Apart => {}
            Meeting::Point(q, true) => crossings.push(q),
            _ => bail!("a stitch road meets the inset section at a vertex or along an edge"),
        }
    }
    let along = |q: &Point| (q[0] - p1[0]) * (p2[0] - p1[0]) + (q[1] - p1[1]) * (p2[1] - p1[1]);
    crossings.sort_by(|a, b| along(a).partial_cmp(&along(b)).unwrap());
    ensure!(crossings.len() % 2 == 0, "a stitch road ends inside the inset section");
    Ok(crossings.chunks(2).map(|c| (c[0], c[1])).collect())
}
