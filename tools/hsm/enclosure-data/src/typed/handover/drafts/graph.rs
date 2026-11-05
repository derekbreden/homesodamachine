//! Numeric construction graphs: the solids a piece is cut from, as a list of operations the
//! Rust kernel builds. A [`Shape`] is one node and the conservative bounds of what it makes;
//! a [`Graph`] holds the nodes and writes the reachable ones as the piece's recipe document.
//!
//! Each node keeps the operation's numbers exactly as the recipe gave them, integers and
//! floats, lists and tuples, and the source site that added it.
use crate::py::{self, IntoVal, Num};
use anyhow::{Result, bail, ensure};
use hsm_documents::interop::Val;
use std::cell::RefCell;
use std::panic::Location;
use std::rc::Rc;

/// Six bounds, `(xmin, xmax, ymin, ymax, zmin, zmax)`.
pub type Bounds = [Num; 6];

/// Bounds of floats.
pub fn bounds(values: [f64; 6]) -> Bounds {
    values.map(Num::Float)
}

/// One recorded operation.
#[derive(Clone, Debug)]
pub struct Node {
    pub op: String,
    pub inputs: Vec<usize>,
    pub path: String,
    pub line: u32,
    pub numbers: Vec<(String, Val)>,
}

#[derive(Default, Debug)]
struct Nodes(RefCell<Vec<Node>>);

/// The operations one piece is built from.
#[derive(Clone, Default, Debug)]
pub struct Graph(Rc<Nodes>);

/// One node of a [`Graph`] and the box that conservatively holds what it makes.
#[derive(Clone, Debug)]
pub struct Shape {
    pub graph: Graph,
    pub index: usize,
    pub bounds: Option<Bounds>,
}

/// A node's numbers, built in the order the recipe names them.
#[derive(Default)]
pub struct Numbers(Vec<(String, Val)>);

impl Numbers {
    pub fn new() -> Self {
        Self::default()
    }
    pub fn with(mut self, name: &str, value: impl IntoVal) -> Self {
        self.0.push((name.into(), value.into_val()));
        self
    }
    pub fn push(&mut self, name: &str, value: impl IntoVal) {
        self.0.push((name.into(), value.into_val()));
    }
}

fn site(location: &Location<'_>) -> (String, u32) {
    let file = location.file();
    let path = if file.starts_with("tools/") || file.starts_with("hardware/") {
        file.to_owned()
    } else {
        format!("tools/hsm/{file}")
    };
    (path, location.line())
}

fn bounds_val(b: &Bounds) -> Val {
    Val::tuple(b.iter().map(|n| n.val()).collect())
}

impl Graph {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn same(&self, other: &Graph) -> bool {
        Rc::ptr_eq(&self.0, &other.0)
    }

    pub fn len(&self) -> usize {
        self.0.0.borrow().len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn op(&self, index: usize) -> String {
        self.0.0.borrow()[index].op.clone()
    }

    pub fn node(&self, index: usize) -> Node {
        self.0.0.borrow()[index].clone()
    }

    /// `graph.add(op, inputs, bounds=bounds, **numbers)`.
    #[track_caller]
    pub fn add(&self, op: &str, inputs: Vec<usize>, bounds: Option<Bounds>, numbers: Numbers) -> Shape {
        let (path, line) = site(Location::caller());
        self.add_at(op, inputs, bounds, numbers, path, line)
    }

    /// `graph.add` with its source site named.
    pub fn add_at(
        &self,
        op: &str,
        inputs: Vec<usize>,
        bounds: Option<Bounds>,
        numbers: Numbers,
        path: String,
        line: u32,
    ) -> Shape {
        let mut nodes = self.0.0.borrow_mut();
        let index = nodes.len();
        nodes.push(Node { op: op.into(), inputs, path, line, numbers: numbers.0 });
        Shape { graph: self.clone(), index, bounds }
    }

    /// `graph.box(x0, x1, y0, y1, z0, z1)`.
    #[track_caller]
    pub fn boxed(&self, b: Bounds) -> Shape {
        self.add("box", vec![], Some(b), Numbers::new().with("box", bounds_val(&b)))
    }

    /// `graph.box` of floats.
    #[track_caller]
    pub fn box6(&self, b: [f64; 6]) -> Shape {
        self.boxed(bounds(b))
    }

    /// `graph.cylinder(axis, radius, a, b, lo, hi)`: a circular prism along `axis`.
    #[track_caller]
    pub fn cylinder(&self, axis: usize, radius: Num, a: Num, b: Num, lo: Num, hi: Num) -> Shape {
        let span = sorted_nums(lo, hi);
        let mut out = [Num::Float(0.0); 6];
        out[2 * axis] = span[0];
        out[2 * axis + 1] = span[1];
        let other: Vec<usize> = (0..3).filter(|&k| k != axis).collect();
        for (k, centre) in other.into_iter().zip([a, b]) {
            out[2 * k] = centre.sub(radius);
            out[2 * k + 1] = centre.add(radius);
        }
        self.add(
            "cylinder",
            vec![],
            Some(out),
            Numbers::new()
                .with("axis", axis as i64)
                .with("radius", radius)
                .with("centre", (a, b))
                .with("span", vec![span[0], span[1]]),
        )
    }

    /// `graph.cylinder` of floats.
    #[track_caller]
    pub fn cylinder_f(&self, axis: usize, radius: f64, a: f64, b: f64, lo: f64, hi: f64) -> Shape {
        self.cylinder(axis, radius.into(), a.into(), b.into(), lo.into(), hi.into())
    }

    /// `graph.prism(axis, lo, hi, section)`: a polygon in the other two axes, swept along `axis`.
    #[track_caller]
    pub fn prism(&self, axis: usize, lo: Num, hi: Num, section: &[[Num; 2]]) -> Shape {
        let span = sorted_nums(lo, hi);
        let mut out = [Num::Float(0.0); 6];
        out[2 * axis] = span[0];
        out[2 * axis + 1] = span[1];
        let other: Vec<usize> = (0..3).filter(|&k| k != axis).collect();
        for (i, k) in other.into_iter().enumerate() {
            out[2 * k] = first_min(section.iter().map(|p| p[i]));
            out[2 * k + 1] = first_max(section.iter().map(|p| p[i]));
        }
        self.add(
            "prism",
            vec![],
            Some(out),
            Numbers::new()
                .with("axis", axis as i64)
                .with("span", vec![span[0], span[1]])
                .with("section", Val::tuple(section.iter().map(|p| (p[0], p[1]).into_val()).collect())),
        )
    }

    /// `graph.prism` of float points.
    #[track_caller]
    pub fn prism_f(&self, axis: usize, lo: f64, hi: f64, section: &[[f64; 2]]) -> Shape {
        let section: Vec<[Num; 2]> = section.iter().map(|p| [p[0].into(), p[1].into()]).collect();
        self.prism(axis, lo.into(), hi.into(), &section)
    }

    /// `graph.rounded(shape, radius)`: a box with its four Z edges rounded.
    #[track_caller]
    pub fn rounded(&self, shape: &Shape, radius: Num) -> Result<Shape> {
        if radius.f() <= 0.0 {
            return Ok(shape.clone());
        }
        if self.op(shape.index) != "box" {
            bail!("the enclosure standing round belongs to rectangular stock");
        }
        let b = shape.bounds.expect("a box has bounds");
        Ok(self.add(
            "rounded-box",
            vec![],
            Some(b),
            Numbers::new().with("box", bounds_val(&b)).with("radius", radius),
        ))
    }

    /// `graph.document(result, extras)`: the nodes `result` and `extras` reach, renumbered in
    /// the order they were added.
    pub fn document(&self, result: &Shape, extras: &[(String, Shape)]) -> Val {
        let nodes = self.0.0.borrow();
        let mut reachable = vec![false; nodes.len()];
        fn visit(nodes: &[Node], reachable: &mut [bool], index: usize) {
            if reachable[index] {
                return;
            }
            reachable[index] = true;
            for &child in &nodes[index].inputs {
                visit(nodes, reachable, child);
            }
        }
        visit(&nodes, &mut reachable, result.index);
        for (_, shape) in extras {
            visit(&nodes, &mut reachable, shape.index);
        }
        let mut remap = vec![usize::MAX; nodes.len()];
        let mut order = vec![];
        for (old, &kept) in reachable.iter().enumerate() {
            if kept {
                remap[old] = order.len();
                order.push(old);
            }
        }
        let rows = order
            .iter()
            .map(|&i| {
                let node = &nodes[i];
                let mut entries = vec![
                    (Val::Str("op".into()), Val::Str(node.op.clone())),
                    (
                        Val::Str("inputs".into()),
                        Val::list(node.inputs.iter().map(|&k| Val::Int(remap[k] as i64)).collect()),
                    ),
                    (
                        Val::Str("source".into()),
                        py::dict(vec![
                            ("path", Val::Str(node.path.clone())),
                            ("line", Val::Int(node.line as i64)),
                        ]),
                    ),
                ];
                entries.extend(node.numbers.iter().map(|(k, v)| (Val::Str(k.clone()), v.clone())));
                Val::dict(entries)
            })
            .collect();
        let mut out = vec![
            ("nodes", Val::list(rows)),
            ("result", Val::Int(remap[result.index] as i64)),
        ];
        if !extras.is_empty() {
            out.push((
                "extras",
                Val::dict(
                    extras
                        .iter()
                        .map(|(k, s)| (Val::Str(k.clone()), Val::Int(remap[s.index] as i64)))
                        .collect(),
                ),
            ));
        }
        py::dict(out)
    }
}

fn sorted_nums(a: Num, b: Num) -> [Num; 2] {
    if b < a { [b, a] } else { [a, b] }
}

fn first_min(values: impl Iterator<Item = Num>) -> Num {
    let mut best: Option<Num> = None;
    for v in values {
        if best.is_none_or(|b| v < b) {
            best = Some(v);
        }
    }
    best.expect("min of no values")
}

fn first_max(values: impl Iterator<Item = Num>) -> Num {
    let mut best: Option<Num> = None;
    for v in values {
        if best.is_none_or(|b| v > b) {
            best = Some(v);
        }
    }
    best.expect("max of no values")
}

/// Whether two boxes overlap with some volume in all three axes.
fn overlaps(a: &Bounds, b: &Bounds) -> bool {
    (0..3).all(|k| a[2 * k] < b[2 * k + 1] && b[2 * k] < a[2 * k + 1])
}

impl Shape {
    #[track_caller]
    fn boolean(&self, op: &str, others: &[&Shape]) -> Shape {
        let mut nodes: Vec<&Shape> = vec![self];
        if op == "cut" && self.bounds.is_some() {
            let own = self.bounds.as_ref().unwrap();
            nodes.extend(others.iter().copied().filter(|o| match &o.bounds {
                None => true,
                Some(b) => overlaps(own, b),
            }));
        } else {
            nodes.extend(others.iter().copied());
        }
        if nodes.len() == 1 {
            return self.clone();
        }
        let mut bounds = self.bounds;
        let all = nodes.iter().all(|n| n.bounds.is_some());
        if op == "union" {
            bounds = if all {
                let mut out = [Num::Float(0.0); 6];
                for k in 0..3 {
                    out[2 * k] = first_min(nodes.iter().map(|n| n.bounds.unwrap()[2 * k]));
                    out[2 * k + 1] = first_max(nodes.iter().map(|n| n.bounds.unwrap()[2 * k + 1]));
                }
                Some(out)
            } else {
                None
            };
        } else if op == "intersect" && all {
            let mut out = [Num::Float(0.0); 6];
            for k in 0..3 {
                out[2 * k] = first_max(nodes.iter().map(|n| n.bounds.unwrap()[2 * k]));
                out[2 * k + 1] = first_min(nodes.iter().map(|n| n.bounds.unwrap()[2 * k + 1]));
            }
            bounds = Some(out);
        }
        self.graph.add(op, nodes.iter().map(|n| n.index).collect(), bounds, Numbers::new())
    }

    /// `shape.fuse(*others)`.
    #[track_caller]
    pub fn fuse(&self, others: &[&Shape]) -> Shape {
        self.boolean("union", others)
    }

    /// `shape.fuse(other)`.
    #[track_caller]
    pub fn fuse1(&self, other: &Shape) -> Shape {
        self.boolean("union", &[other])
    }

    /// `shape.cut(*others)`: others whose bounds miss this one's are left out.
    #[track_caller]
    pub fn cut(&self, others: &[&Shape]) -> Shape {
        self.boolean("cut", others)
    }

    /// `shape.cut(other)`.
    #[track_caller]
    pub fn cut1(&self, other: &Shape) -> Shape {
        self.boolean("cut", &[other])
    }

    /// `shape.intersect(*others)`.
    #[track_caller]
    pub fn intersect(&self, others: &[&Shape]) -> Shape {
        self.boolean("intersect", others)
    }

    /// `shape.intersect(other)`.
    #[track_caller]
    pub fn intersect1(&self, other: &Shape) -> Shape {
        self.boolean("intersect", &[other])
    }

    /// `shape.translate(delta)`; `delta` is written as the caller made it.
    #[track_caller]
    pub fn translate(&self, delta: [Num; 3], delta_val: Val) -> Shape {
        let bounds = self.bounds.map(|b| {
            let mut out = b;
            for k in 0..3 {
                out[2 * k] = b[2 * k].add(delta[k]);
                out[2 * k + 1] = b[2 * k + 1].add(delta[k]);
            }
            out
        });
        self.graph.add("translate", vec![self.index], bounds, Numbers::new().with("delta", delta_val))
    }

    /// `shape.translate((x, y, z))` with a tuple of floats.
    #[track_caller]
    pub fn translate_f(&self, delta: [f64; 3]) -> Shape {
        self.translate(delta.map(Num::Float), (delta[0], delta[1], delta[2]).into_val())
    }

    /// `shape.rotate(origin, end, angle)`: about the axis from `origin` to `end`, in degrees.
    #[track_caller]
    pub fn rotate(&self, origin: [f64; 3], end: [f64; 3], angle: f64, numbers: (Val, Val, Val)) -> Shape {
        let axis: Vec<f64> = origin.iter().zip(&end).map(|(a, b)| b - a).collect();
        let length = py::sum(axis.iter().map(|a| a * a)).sqrt();
        let axis: Vec<f64> = axis.iter().map(|a| a / length).collect();
        let (c, s) = (py::radians(angle).cos(), py::radians(angle).sin());
        let point = |p: [f64; 3]| -> [f64; 3] {
            let q: Vec<f64> = p.iter().zip(&origin).map(|(a, b)| a - b).collect();
            let cross = [
                axis[1] * q[2] - axis[2] * q[1],
                axis[2] * q[0] - axis[0] * q[2],
                axis[0] * q[1] - axis[1] * q[0],
            ];
            let dot = py::sum(axis.iter().zip(&q).map(|(a, b)| a * b));
            [0, 1, 2].map(|k| origin[k] + c * q[k] + s * cross[k] + (1. - c) * dot * axis[k])
        };
        let bounds = self.bounds.map(|b| {
            let f = b.map(Num::f);
            let mut corners = vec![];
            for x in [f[0], f[1]] {
                for y in [f[2], f[3]] {
                    for z in [f[4], f[5]] {
                        corners.push(point([x, y, z]));
                    }
                }
            }
            let mut out = [Num::Float(0.0); 6];
            for k in 0..3 {
                out[2 * k] = Num::Float(py::min(corners.iter().map(|p| p[k])));
                out[2 * k + 1] = Num::Float(py::max(corners.iter().map(|p| p[k])));
            }
            out
        });
        self.graph.add(
            "rotate",
            vec![self.index],
            bounds,
            Numbers::new().with("origin", numbers.0).with("end", numbers.1).with("angle", numbers.2),
        )
    }

    /// `shape.mirror(plane)` for `'YZ'`, `'XZ'` or `'XY'`.
    #[track_caller]
    pub fn mirror(&self, plane: &str) -> Result<Shape> {
        let axis = match plane {
            "YZ" => 0,
            "XZ" => 1,
            "XY" => 2,
            other => bail!("mirror plane {other}"),
        };
        let bounds = self.bounds.map(|b| {
            let mut out = b;
            out[2 * axis] = b[2 * axis + 1].neg();
            out[2 * axis + 1] = b[2 * axis].neg();
            out
        });
        Ok(self.graph.add("mirror", vec![self.index], bounds, Numbers::new().with("axis", axis as i64)))
    }

    /// `shape.BoundingBox()`.
    pub fn bounding_box(&self) -> Result<Bounds> {
        match self.bounds {
            Some(b) => Ok(b),
            None => bail!("this private feature has no conservative numeric bounds"),
        }
    }

    /// The bounds as floats.
    pub fn box_f(&self) -> Result<[f64; 6]> {
        Ok(self.bounding_box()?.map(Num::f))
    }
}

/// Check a graph-holding value is the graph a recipe expects.
pub fn same_graph(a: &Shape, b: &Shape) -> Result<()> {
    ensure!(a.graph.same(&b.graph), "shapes from different construction graphs");
    Ok(())
}
