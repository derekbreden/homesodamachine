//! Line drawings of solid models: the visible outlines of a closed triangle mesh seen
//! orthographically. Silhouette edges, sharp creases and open edges are drawn; each is cut
//! where a front-facing triangle lies in front of it, analytically, with no raster.
use std::collections::BTreeMap;

type P2 = [f64; 2];
type P3 = [f64; 3];

fn sub(a: P3, b: P3) -> P3 {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}
fn dot(a: P3, b: P3) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}
fn cross(a: P3, b: P3) -> P3 {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}
fn scale(a: P3, k: f64) -> P3 {
    a.map(|v| v * k)
}
fn norm(a: P3) -> f64 {
    dot(a, a).sqrt()
}
fn cross2(a: P3, b: P3) -> f64 {
    a[0] * b[1] - a[1] * b[0]
}

#[derive(Clone, Copy)]
struct Bounds {
    min: P2,
    max: P2,
}

impl Bounds {
    fn of(points: &[P3]) -> Bounds {
        let mut b = Bounds { min: [f64::INFINITY; 2], max: [f64::NEG_INFINITY; 2] };
        for p in points {
            for k in 0..2 {
                b.min[k] = b.min[k].min(p[k]);
                b.max[k] = b.max[k].max(p[k]);
            }
        }
        b
    }
    fn overlaps(self, o: Bounds) -> bool {
        (0..2).all(|k| self.min[k] <= o.max[k] && self.max[k] >= o.min[k])
    }
    fn union(self, o: Bounds) -> Bounds {
        Bounds { min: [0, 1].map(|k| self.min[k].min(o.min[k])), max: [0, 1].map(|k| self.max[k].max(o.max[k])) }
    }
}

/// The front triangles' boxes, split in halves along their longer side.
struct Tree {
    bounds: Bounds,
    node: Node,
}

enum Node {
    Leaf(Vec<usize>),
    Split(Box<Tree>, Box<Tree>),
}

impl Tree {
    fn new(mut indices: Vec<usize>, boxes: &[Bounds]) -> Tree {
        let bounds = indices.iter().map(|&i| boxes[i]).reduce(Bounds::union).expect("a tree over triangles");
        let node = if indices.len() <= 12 {
            Node::Leaf(indices)
        } else {
            let k = usize::from(bounds.max[1] - bounds.min[1] > bounds.max[0] - bounds.min[0]);
            indices.sort_unstable_by(|&a, &b| {
                (boxes[a].min[k] + boxes[a].max[k]).total_cmp(&(boxes[b].min[k] + boxes[b].max[k])).then(a.cmp(&b))
            });
            let right = indices.split_off(indices.len() / 2);
            Node::Split(Box::new(Tree::new(indices, boxes)), Box::new(Tree::new(right, boxes)))
        };
        Tree { bounds, node }
    }
    fn query(&self, area: Bounds, boxes: &[Bounds], out: &mut Vec<usize>) {
        if !self.bounds.overlaps(area) {
            return;
        }
        match &self.node {
            Node::Leaf(i) => out.extend(i.iter().copied().filter(|&i| boxes[i].overlaps(area))),
            Node::Split(a, b) => {
                a.query(area, boxes, out);
                b.query(area, boxes, out);
            }
        }
    }
}

/// The visible pieces of a mesh's outline edges, in the view's plane: `normal` points at the
/// viewer and `right` is the drawing's +x. Model units.
pub fn visible_edges(vertices: &[P3], triangles: &[[u32; 3]], normal: P3, right: P3, sharp_degrees: f64) -> Vec<[P2; 2]> {
    let normal = scale(normal, 1.0 / norm(normal));
    let right = sub(right, scale(normal, dot(normal, right)));
    let right = scale(right, 1.0 / norm(right));
    let up = cross(normal, right);
    let projected: Vec<P3> = vertices.iter().map(|&p| [dot(p, right), dot(p, up), dot(p, normal)]).collect();
    let corners: Vec<[P3; 3]> = triangles.iter().map(|t| t.map(|i| projected[i as usize])).collect();
    let normals: Vec<P3> = corners.iter().map(|c| cross(sub(c[1], c[0]), sub(c[2], c[0]))).collect();
    let front: Vec<bool> = normals.iter().map(|n| n[2] > 1e-12).collect();

    let mut owners: BTreeMap<[u32; 2], Vec<usize>> = BTreeMap::new();
    for (a, b) in [(0, 1), (1, 2), (2, 0)] {
        for (i, t) in triangles.iter().enumerate() {
            let mut edge = [t[a], t[b]];
            edge.sort();
            owners.entry(edge).or_default().push(i);
        }
    }
    let threshold = sharp_degrees.to_radians().cos();
    let mut candidates = Vec::new();
    for (&edge, incident) in &owners {
        if incident.len() == 2 {
            let (a, b) = (incident[0], incident[1]);
            let ua = scale(normals[a], 1.0 / norm(normals[a]).max(1e-30));
            let ub = scale(normals[b], 1.0 / norm(normals[b]).max(1e-30));
            if front[a] != front[b] || dot(ua, ub) < threshold {
                candidates.push(edge);
            }
        }
    }
    candidates.extend(owners.iter().filter(|(_, v)| v.len() == 1).map(|(&e, _)| e));

    let facing: Vec<usize> = (0..triangles.len()).filter(|&i| front[i]).collect();
    if facing.is_empty() {
        return Vec::new();
    }
    let boxes: Vec<Bounds> = facing.iter().map(|&i| Bounds::of(&corners[i])).collect();
    let tree = Tree::new((0..facing.len()).collect(), &boxes);
    // Each front triangle's depth as a plane over the drawing: z = plane − c·(x, y).
    let slopes: Vec<P3> = facing.iter().map(|&i| scale(normals[i], 1.0 / normals[i][2])).collect();
    let planes: Vec<f64> = facing.iter().zip(&slopes).map(|(&i, c)| dot(*c, corners[i][0])).collect();
    let at = |a: P3, d: P3, t: f64| [a[0] + d[0] * t, a[1] + d[1] * t];

    let mut out = Vec::new();
    let mut nearby = Vec::new();
    for edge in candidates {
        let (a, b) = (projected[edge[0] as usize], projected[edge[1] as usize]);
        let d = sub(b, a);
        if d[0].hypot(d[1]) < 1e-10 {
            continue;
        }
        nearby.clear();
        tree.query(Bounds::of(&[a, b]), &boxes, &mut nearby);
        let mut hidden = Vec::with_capacity(nearby.len());
        for &j in &nearby {
            let c = corners[facing[j]];
            let slope = slopes[j];
            let (mut low, mut high, mut valid) = (0.0f64, 1.0f64, true);
            // Inside the triangle's three edges, and behind its surface.
            for side in 0..4 {
                let (alpha, beta) = if side < 3 {
                    let v = sub(c[(side + 1) % 3], c[side]);
                    (cross2(v, sub(a, c[side])), cross2(v, d))
                } else {
                    (planes[j] - (slope[0] * a[0] + slope[1] * a[1]) - a[2] - 1e-7, -(slope[0] * d[0] + slope[1] * d[1]) - d[2])
                };
                if beta.abs() < 1e-15 {
                    if alpha < -1e-12 {
                        valid = false;
                        break;
                    }
                } else if beta > 0.0 {
                    low = low.max(-alpha / beta);
                } else {
                    high = high.min(-alpha / beta);
                }
            }
            if valid && high > low {
                hidden.push((low, high));
            }
        }
        hidden.sort_by(|p, q| p.0.total_cmp(&q.0).then(p.1.total_cmp(&q.1)));
        let mut begin = 0.0f64;
        for (low, high) in hidden {
            if low > begin + 1e-10 {
                out.push([at(a, d, begin), at(a, d, low)]);
            }
            begin = begin.max(high);
        }
        if begin < 1.0 - 1e-10 {
            out.push([at(a, d, begin), [b[0], b[1]]]);
        }
    }
    out
}

fn key(p: P2) -> [i64; 2] {
    p.map(|x| (x * 1e9).round() as i64)
}

fn distance2(p: P2, a: P2, b: P2) -> f64 {
    let (dx, dy) = (b[0] - a[0], b[1] - a[1]);
    let l = dx * dx + dy * dy;
    let t = if l == 0.0 { 0.0 } else { (((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l).clamp(0.0, 1.0) };
    (p[0] - a[0] - dx * t).powi(2) + (p[1] - a[1] - dy * t).powi(2)
}

/// Douglas–Peucker: the points a polyline keeps within `tolerance`.
fn simplify(points: &[P2], tolerance: f64) -> Vec<P2> {
    if points.len() <= 2 {
        return points.to_vec();
    }
    let mut kept = vec![false; points.len()];
    kept[0] = true;
    kept[points.len() - 1] = true;
    let mut spans = vec![(0, points.len() - 1)];
    while let Some((start, end)) = spans.pop() {
        let mut furthest = None;
        let mut most = tolerance * tolerance;
        for i in start + 1..end {
            let d = distance2(points[i], points[start], points[end]);
            if d > most {
                most = d;
                furthest = Some(i);
            }
        }
        if let Some(i) = furthest {
            kept[i] = true;
            spans.push((i, end));
            spans.push((start, i));
        }
    }
    points.iter().zip(kept).filter_map(|(&p, k)| k.then_some(p)).collect()
}

/// Edge pieces joined end to end where exactly two meet, each path simplified to `tolerance`.
pub fn paths(edges: &[[P2; 2]], tolerance: f64) -> Vec<Vec<P2>> {
    let mut ends: BTreeMap<[i64; 2], Vec<usize>> = BTreeMap::new();
    for (i, e) in edges.iter().enumerate() {
        for &p in e {
            ends.entry(key(p)).or_default().push(i);
        }
    }
    let mut used = vec![false; edges.len()];
    let mut out = Vec::new();
    for first in 0..edges.len() {
        if used[first] {
            continue;
        }
        used[first] = true;
        let mut points = edges[first].to_vec();
        for _ in 0..2 {
            loop {
                let at = key(*points.last().unwrap());
                let incident = &ends[&at];
                if incident.len() != 2 {
                    break;
                }
                let Some(next) = incident.iter().copied().find(|&i| !used[i]) else { break };
                used[next] = true;
                let e = edges[next];
                points.push(if key(e[0]) == at { e[1] } else { e[0] });
            }
            points.reverse();
        }
        out.push(if tolerance != 0.0 && points.len() > 2 { simplify(&points, tolerance) } else { points });
    }
    out
}
