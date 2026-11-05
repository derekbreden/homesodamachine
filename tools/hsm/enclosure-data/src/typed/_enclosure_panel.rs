//! Enclosure-private numeric construction for the structural back-bottom panel.
//!
//! The native seam helpers keep ownership of their stations. This module records their
//! simple solid operations; Rust builds the solids and releases each intermediate after
//! its last use. Native builders and their cached geometry remain available to callers.
//!
//! # Construction graphs for typed modules
//!
//! A construction graph records each solid operation as a node
//! `dict(op=.., inputs=[..], source=dict(path=.., line=..), **numbers)`; a Rust part program builds
//! the solids from [`Graph::document`]. These types are the typed form of `_Graph`, `_Shape`,
//! `_rust_enclosure_checks._Questions` and `_ReadingShape`.
//!
//! - [`Graph`]: a native graph. [`Graph::new`] is `_Graph()`, [`Graph::questions`] is
//!   `_Questions(answers)` (its `add` gives reading shapes and records `empty` with zero bounds).
//!   [`Graph::add`] records a node (`#[track_caller]`: `source` is the calling line);
//!   [`Graph::box_`], [`Graph::cylinder`], [`Graph::prism`], [`Graph::rounded`] are the recipe
//!   helpers; [`Graph::document`] the part document. [`Graph::node`] is `graph.nodes[i]` (the
//!   node dict itself: mutate it in place as `graph.nodes[i].update(..)` does), [`Graph::attr`] /
//!   [`Graph::set_attr`] the graph's other attributes (`extras`, `answers`, `queries`).
//!   Questions graphs add [`Graph::model`], [`Graph::identity`], [`Graph::reading`] and
//!   [`Graph::questions_document`].
//! - [`AnyGraph`]: a graph argument that may be a Python object (machine-data's `_Questions()`, a
//!   generated module's `_Graph()`): `AnyGraph::from_val(&v)`, then the same recipe helpers; a
//!   Python graph is called through its methods.
//! - [`Shape`]: a native node and its bounds. [`Solid`]: what a typed caller holds,
//!   `Native(Shape)` or `Py(Val)` (any other value: a Python shape, or `None`), with the methods
//!   the recipes call (`cut`, `fuse`, `intersect`, `translate`, `rotate`, `mirror`, `clean`,
//!   `val`, `solids`, `bounding_box`, `bounds`, `index`, `volume`, `faces`, `is_valid`), the same
//!   whichever it holds. Operands may mix kinds, as Python's `_boolean` reads `other.index` and
//!   `other.bounds` from any operand.
//! - [`Bounds`]: `(xmin, xmax, ymin, ymax, zmin, zmax)` as Python holds them, ints and floats in a
//!   tuple or a list.
//!
//! Crossing into generated code: [`Solid::to_val`], [`Shape::to_val`] and [`Graph::to_val`] give
//! the value generated code receives, a `Val::Namespace` whose fields are the Python attributes
//! (`graph`, `index`, `bounds`; a graph's `nodes` is its one shared list) and whose methods act
//! on the native value; [`Solid::from_val`] / [`Graph::from_val`] recover the native value from
//! that namespace. A shape's namespace is made once, when it first crosses; a shape that never
//! crosses has none. `py::Py` converts the same way.
//!
//! Recorders: [`Recording::enter`] / [`Recording::exit`] is `_record(shell, graph, structure)`
//! for typed callers ([`record`] is the context manager generated callers `with`), installing
//! the same leaves under the same names and restoring them in the same order. [`leaf`] makes a
//! typed leaf value a recorder installs, and [`call_leaf`] calls `shell.<name>(..)` as the
//! enclosure does: a leaf made by [`leaf`] runs typed and returns its native shape unwrapped;
//! any other value is called and its result wrapped in a [`Solid`].
use super::num::Num;
use super::py::{self, Args, Kwargs, Val};
use super::rt::{self, Ns, Rt};
use anyhow::{Context, Result, anyhow, bail, ensure};
use hsm_documents::interop::{self, Entries};
use std::cell::{Cell, RefCell};
use std::collections::VecDeque;
use std::path::PathBuf;
use std::rc::{Rc, Weak};

pub const TYPED: bool = true;
const MODULE: &str = "_enclosure_panel";
/// The field of a native value's namespace that hands the native value back.
const MARK: &str = "__hsm_native__";

pub struct State {
    /// The module's Python classes, which Python-object graphs construct.
    shape_class: Val,
    simple_namespace: RefCell<Option<Val>>,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// `types.SimpleNamespace`.
pub fn simple_namespace(rt: &Rt) -> Result<Val> {
    let state = state(rt)?;
    if let Some(class) = state.simple_namespace.borrow().as_ref() {
        return Ok(class.clone());
    }
    let class = rt.member("types", "SimpleNamespace")?;
    *state.simple_namespace.borrow_mut() = Some(class.clone());
    Ok(class)
}

// ------------------------------------------------------------------------------------------
// Bounds

/// A shape's conservative bounds `(xmin, xmax, ymin, ymax, zmin, zmax)`: each number an int or
/// a float as Python holds it, in a tuple or (`list`) a list.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Bounds {
    pub v: [Num; 6],
    pub list: bool,
}

impl Bounds {
    pub fn tuple(v: [Num; 6]) -> Self {
        Self { v, list: false }
    }
    pub fn list(v: [Num; 6]) -> Self {
        Self { v, list: true }
    }
    /// A tuple of floats.
    pub fn floats(v: [f64; 6]) -> Self {
        Self::tuple(v.map(Num::F))
    }
    pub fn f(&self) -> [f64; 6] {
        self.v.map(Num::f)
    }
    pub fn lo(&self, axis: usize) -> Num {
        self.v[2 * axis]
    }
    pub fn hi(&self, axis: usize) -> Num {
        self.v[2 * axis + 1]
    }
    pub fn to_val(&self) -> Val {
        let values = self.v.iter().map(|n| n.val()).collect();
        if self.list { Val::list(values) } else { Val::Tuple(values) }
    }
    /// The bounds a Python value holds: `None` for `None`; a provider sequence is read in one
    /// callback.
    pub fn from_val(value: &Val) -> Result<Option<Bounds>> {
        let local;
        let value = match value {
            Val::None => return Ok(None),
            Val::Ref(_) => {
                local = py::snapshot(value)?;
                &local
            }
            other => other,
        };
        let (items, list) = match value {
            Val::List(items) => (items.borrow().clone(), true),
            Val::Tuple(items) => (items.clone(), false),
            other => bail!("shape bounds are a tuple or a list, not {}", other.repr()?),
        };
        ensure!(items.len() == 6, "shape bounds hold six numbers, not {}", items.len());
        let mut v = [Num::F(0.); 6];
        for (slot, item) in v.iter_mut().zip(&items) {
            *slot = Num::of(item)?;
        }
        Ok(Some(Bounds { v, list }))
    }
    /// `all(a[2k] < b[2k+1] and b[2k] < a[2k+1] for k in range(3))`.
    pub fn overlaps(&self, other: &Bounds) -> bool {
        (0..3).all(|k| self.lo(k).f() < other.hi(k).f() && other.lo(k).f() < self.hi(k).f())
    }
}

impl py::Py for Bounds {
    fn to_py(&self) -> Result<Val> {
        Ok(self.to_val())
    }
    fn from_py(value: &Val) -> Result<Self> {
        Bounds::from_val(value)?.context("shape bounds are None")
    }
}

/// `sorted((a, b))`.
fn sorted2(a: Num, b: Num) -> [Num; 2] {
    if b.f() < a.f() { [b, a] } else { [a, b] }
}

/// `min(values)`: the first of equal values.
fn least(values: impl IntoIterator<Item = Num>) -> Result<Num> {
    values.into_iter().reduce(Num::min).context("min() arg is an empty sequence")
}

/// `max(values)`: the first of equal values.
fn most(values: impl IntoIterator<Item = Num>) -> Result<Num> {
    values.into_iter().reduce(Num::max).context("max() arg is an empty sequence")
}

/// Three numbers of a coordinate sequence; a provider sequence is read in one callback.
fn three(value: &Val) -> Result<[Num; 3]> {
    let local = py::snapshot(value)?;
    let items = local.iter()?;
    ensure!(items.len() >= 3, "tuple index out of range");
    Ok([Num::of(&items[0])?, Num::of(&items[1])?, Num::of(&items[2])?])
}

fn numbers_of(value: &Val) -> Result<Vec<Num>> {
    py::snapshot(value)?.iter()?.iter().map(Num::of).collect()
}

// ------------------------------------------------------------------------------------------
// Native values crossing to generated code and back

enum Handoff {
    Graph(Rc<GraphCore>),
    Shape(Rc<ShapeCore>),
}

thread_local! {
    static HANDOFF: RefCell<Option<Handoff>> = const { RefCell::new(None) };
    static LEAVES: RefCell<Vec<(usize, LeafFn)>> = const { RefCell::new(Vec::new()) };
}

/// The native value a namespace made by this module stands for.
fn handoff(value: &Val) -> Option<Handoff> {
    let Val::Namespace(entries) = value else { return None };
    let mark = entries.borrow().iter().find_map(|(key, value)| match key {
        Val::Str(name) if name == MARK => Some(value.clone()),
        _ => None,
    })?;
    mark.call(vec![], vec![]).ok()?;
    HANDOFF.with(|held| held.borrow_mut().take())
}

fn attribute_error(kind: &str, name: &str) -> anyhow::Error {
    anyhow!("'{kind}' object has no attribute '{name}'")
}

// ------------------------------------------------------------------------------------------
// Graphs

struct GraphCore {
    /// `graph.nodes`: one list for the graph's life, shared with generated code.
    nodes: Val,
    questions: bool,
    /// The namespace generated code sees: the graph's other attributes and its methods.
    face: Entries,
    /// Bumped whenever a caller took the nodes list or a node dict, which it may have changed.
    epoch: Cell<u64>,
    /// `identity` keys of the first nodes, valid for one `epoch`.
    keys: RefCell<(u64, Vec<String>)>,
    /// The measured answers as local values, with the value they were read from.
    answers: RefCell<Option<(Val, Val)>>,
}

/// A native construction graph: `_enclosure_panel._Graph` or `_rust_enclosure_checks._Questions`.
#[derive(Clone)]
pub struct Graph(Rc<GraphCore>);

impl Default for Graph {
    fn default() -> Self {
        Self::new()
    }
}

impl Graph {
    /// `_Graph()`.
    pub fn new() -> Self {
        Self::make(None)
    }
    /// `_Questions(answers)`.
    pub fn questions(answers: Val) -> Self {
        Self::make(Some(answers))
    }
    fn make(answers: Option<Val>) -> Self {
        let questions = answers.is_some();
        Graph(Rc::new_cyclic(|weak: &Weak<GraphCore>| {
            let mut entries = vec![];
            if let Some(answers) = answers {
                entries.push((py::s("answers"), answers));
                entries.push((py::s("queries"), Val::dict(vec![])));
                entries.push((py::s("extras"), Val::dict(vec![])));
            }
            let held = weak.clone();
            entries.push((py::s(MARK), Val::function(move |_, _| {
                let core = held.upgrade().context("a construction graph outlived its recipe")?;
                HANDOFF.with(|slot| *slot.borrow_mut() = Some(Handoff::Graph(core)));
                Ok(Val::None)
            })));
            let held = weak.clone();
            entries.push((py::s("__getattr__"), Val::function(move |args, _| {
                let core = held.upgrade().context("a construction graph outlived its recipe")?;
                graph_method(&Graph(core), &args.first().context("attribute name")?.str()?)
            })));
            GraphCore {
                nodes: Val::list(vec![]),
                questions,
                face: Rc::new(RefCell::new(entries)),
                epoch: Cell::new(0),
                keys: RefCell::new((0, vec![])),
                answers: RefCell::new(None),
            }
        }))
    }
    /// The graph a value generated code holds stands for.
    pub fn from_val(value: &Val) -> Option<Graph> {
        match handoff(value)? {
            Handoff::Graph(core) => Some(Graph(core)),
            Handoff::Shape(_) => None,
        }
    }
    /// The value generated code receives: the same namespace every time.
    pub fn to_val(&self) -> Val {
        Val::Namespace(self.0.face.clone())
    }
    pub fn same(&self, other: &Graph) -> bool {
        Rc::ptr_eq(&self.0, &other.0)
    }
    /// Whether this is a `_Questions` graph, whose shapes are `_ReadingShape`s.
    pub fn is_questions(&self) -> bool {
        self.0.questions
    }
    fn kind(&self) -> &'static str {
        if self.0.questions { "_Questions" } else { "_Graph" }
    }
    fn touched(&self) {
        self.0.epoch.set(self.0.epoch.get() + 1);
    }
    /// `graph.<name>` for an attribute other than a method (`extras`, `answers`, `queries`, or
    /// one generated code set).
    pub fn attr(&self, name: &str) -> Result<Val> {
        if name == "nodes" {
            return Ok(self.nodes());
        }
        let entries = self.0.face.borrow();
        entries.iter().find_map(|(key, value)| match key {
            Val::Str(key) if key == name => Some(value.clone()),
            _ => None,
        }).ok_or_else(|| attribute_error(self.kind(), name))
    }
    /// `graph.<name> = value`.
    pub fn set_attr(&self, name: &str, value: Val) -> Result<()> {
        Val::Namespace(self.0.face.clone()).set(py::s(name), value)
    }
    /// `graph.nodes`: the one shared list (a caller holding it may change its nodes).
    pub fn nodes(&self) -> Val {
        self.touched();
        self.0.nodes.clone()
    }
    fn rows(&self) -> Rc<RefCell<Vec<Val>>> {
        match &self.0.nodes {
            Val::List(rows) => rows.clone(),
            _ => unreachable!("a graph's nodes are a list"),
        }
    }
    pub fn len(&self) -> usize {
        self.rows().borrow().len()
    }
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
    /// `graph.nodes[index]`: the node dict itself.
    pub fn node(&self, index: usize) -> Result<Val> {
        self.touched();
        self.rows().borrow().get(index).cloned().context("list index out of range")
    }
    /// `graph.nodes[index]['op']`.
    pub fn op(&self, index: usize) -> Result<Val> {
        let node = self.rows().borrow().get(index).cloned().context("list index out of range")?;
        node.get(py::s("op"))
    }

    /// `graph.add(op, inputs, bounds=bounds, **numbers)`: the node's `source` is the caller's line.
    #[track_caller]
    pub fn add(&self, op: &str, inputs: &[usize], bounds: Option<Bounds>, numbers: Vec<(&str, Val)>) -> Shape {
        let inputs = inputs.iter().map(|&i| Val::Int(i as i64)).collect();
        let numbers = numbers.into_iter().map(|(k, v)| (k.to_owned(), v)).collect();
        self.record(py::s(op), inputs, bounds, numbers, rt::site())
    }
    /// `graph.add` with the Python values a caller gave.
    #[track_caller]
    pub fn add_val(&self, op: Val, inputs: &Val, bounds: &Val, numbers: Kwargs) -> Result<Shape> {
        let inputs = inputs.iter()?;
        let empty = self.0.questions && interop::eq(&op, &py::s("empty"))?;
        let bounds = if empty { None } else { Bounds::from_val(bounds)? };
        Ok(self.record(op, inputs, bounds, numbers, rt::site()))
    }
    fn record(&self, op: Val, inputs: Vec<Val>, bounds: Option<Bounds>, numbers: Kwargs, source: Val) -> Shape {
        let empty = self.0.questions && matches!(&op, Val::Str(name) if name == "empty");
        let bounds = if empty { Some(Bounds::floats([0.; 6])) } else { bounds };
        let node = Val::dict(vec![(py::s("op"), op), (py::s("inputs"), Val::list(inputs)), (py::s("source"), source)]);
        for (key, value) in numbers {
            let _ = node.set(Val::Str(key), value);
        }
        let rows = self.rows();
        let index = {
            let mut rows = rows.borrow_mut();
            rows.push(node);
            rows.len() - 1
        };
        Shape::new(self.clone(), index, bounds)
    }

    /// `graph.box(*bounds)`.
    #[track_caller]
    pub fn box_(&self, bounds: Vec<Val>) -> Result<Shape> {
        let values = Val::Tuple(bounds);
        let typed = Bounds::from_val(&values)?;
        Ok(self.record(py::s("box"), vec![], typed, vec![("box".into(), values)], rt::site()))
    }
    /// `graph.box(x0, x1, y0, y1, z0, z1)` of numbers.
    #[track_caller]
    pub fn box6(&self, b: [Num; 6]) -> Shape {
        let values = Val::Tuple(b.iter().map(|n| n.val()).collect());
        self.record(py::s("box"), vec![], Some(Bounds::tuple(b)), vec![("box".into(), values)], rt::site())
    }
    /// `graph.cylinder(axis, radius, a, b, lo, hi)`: a circle in the other two axes, centred at
    /// `(a, b)`, swept from `lo` to `hi` along `axis`.
    #[track_caller]
    pub fn cylinder(&self, axis: i64, radius: Num, a: Num, b: Num, lo: Num, hi: Num) -> Result<Shape> {
        let (bounds, span) = cylinder_bounds(axis, radius, a, b, lo, hi)?;
        Ok(self.record(py::s("cylinder"), vec![], Some(bounds), vec![
            ("axis".into(), Val::Int(axis)),
            ("radius".into(), radius.val()),
            ("centre".into(), Val::Tuple(vec![a.val(), b.val()])),
            ("span".into(), Val::list(vec![span[0].val(), span[1].val()])),
        ], rt::site()))
    }
    /// `graph.prism(axis, lo, hi, section)`: the polygon `section` in the other two axes, swept
    /// from `lo` to `hi` along `axis`; `section` is recorded as `tuple(section)`.
    #[track_caller]
    pub fn prism(&self, axis: i64, lo: Num, hi: Num, section: &Val) -> Result<Shape> {
        let section = Val::Tuple(section.iter()?);
        let bounds = prism_bounds(axis, lo, hi, &section)?;
        let span = sorted2(lo, hi);
        Ok(self.record(py::s("prism"), vec![], Some(bounds), vec![
            ("axis".into(), Val::Int(axis)),
            ("span".into(), Val::list(vec![span[0].val(), span[1].val()])),
            ("section".into(), section),
        ], rt::site()))
    }
    /// `graph.rounded(shape, radius)`: rectangular stock with its standing edges rounded.
    #[track_caller]
    pub fn rounded(&self, shape: &Solid, radius: Num) -> Result<Solid> {
        if radius.f() <= 0. {
            return Ok(shape.clone());
        }
        let index = shape.index()?;
        if !interop::eq(&self.op(index)?, &py::s("box"))? {
            bail!("the enclosure standing round belongs to rectangular stock");
        }
        let bounds = shape.bounds_val()?;
        let typed = Bounds::from_val(&bounds)?;
        Ok(Solid::Native(self.record(py::s("rounded-box"), vec![], typed, vec![
            ("box".into(), bounds),
            ("radius".into(), radius.val()),
        ], rt::site())))
    }
    /// `graph.document(result, extras)`: the nodes `result` and the `extras` reach, renumbered in
    /// recording order.
    pub fn document(&self, result: &Solid, extras: &[(Val, Solid)]) -> Result<Val> {
        let roots = extras.iter().map(|(key, shape)| Ok((key.clone(), shape.index()?))).collect::<Result<Vec<_>>>()?;
        let rows = self.rows().borrow().clone();
        document_rows(&rows, result.index()?, &roots)
    }
}

impl py::Py for Graph {
    fn to_py(&self) -> Result<Val> {
        Ok(self.to_val())
    }
    fn from_py(value: &Val) -> Result<Self> {
        Graph::from_val(value).context("not a native construction graph")
    }
}

fn cylinder_bounds(axis: i64, radius: Num, a: Num, b: Num, lo: Num, hi: Num) -> Result<(Bounds, [Num; 2])> {
    ensure!((0..3).contains(&axis), "a cylinder axis is 0, 1 or 2, not {axis}");
    let span = sorted2(lo, hi);
    let mut v = [Num::F(0.); 6];
    let axis = axis as usize;
    v[2 * axis] = span[0];
    v[2 * axis + 1] = span[1];
    let other = (0..3).filter(|&k| k != axis);
    for (k, centre) in other.zip([a, b]) {
        v[2 * k] = centre.sub(radius);
        v[2 * k + 1] = centre.add(radius);
    }
    Ok((Bounds::list(v), span))
}

fn prism_bounds(axis: i64, lo: Num, hi: Num, section: &Val) -> Result<Bounds> {
    ensure!((0..3).contains(&axis), "a prism axis is 0, 1 or 2, not {axis}");
    let span = sorted2(lo, hi);
    let mut v = [Num::F(0.); 6];
    let axis = axis as usize;
    v[2 * axis] = span[0];
    v[2 * axis + 1] = span[1];
    let points = section.iter()?.iter().map(|p| {
        let p = py::snapshot(p)?;
        Ok([Num::of(&p.get(Val::Int(0))?)?, Num::of(&p.get(Val::Int(1))?)?])
    }).collect::<Result<Vec<_>>>()?;
    for (i, k) in (0..3).filter(|&k| k != axis).enumerate() {
        v[2 * k] = least(points.iter().map(|p| p[i]))?;
        v[2 * k + 1] = most(points.iter().map(|p| p[i]))?;
    }
    Ok(Bounds::list(v))
}

/// The document of the nodes reachable from `result` and from each extra, renumbered in
/// recording order: `_Graph.document`.
fn document_rows(rows: &[Val], result: usize, extras: &[(Val, usize)]) -> Result<Val> {
    let mut reachable = vec![false; rows.len()];
    let inputs = |row: &Val| -> Result<Vec<usize>> {
        row.get(py::s("inputs"))?.iter()?.iter().map(|i| Ok(i.integer()? as usize)).collect()
    };
    let mut visit = |start: usize, reachable: &mut Vec<bool>| -> Result<()> {
        let mut stack = vec![start];
        while let Some(index) = stack.pop() {
            ensure!(index < rows.len(), "list index out of range");
            if reachable[index] {
                continue;
            }
            reachable[index] = true;
            stack.extend(inputs(&rows[index])?);
        }
        Ok(())
    };
    visit(result, &mut reachable)?;
    for (_, index) in extras {
        visit(*index, &mut reachable)?;
    }
    let mut remap = vec![usize::MAX; rows.len()];
    let mut order = vec![];
    for (old, kept) in reachable.iter().enumerate() {
        if *kept {
            remap[old] = order.len();
            order.push(old);
        }
    }
    let renumber = |index: usize| -> Result<Val> {
        let new = *remap.get(index).context("missing key")?;
        ensure!(new != usize::MAX, "missing key {index}");
        Ok(Val::Int(new as i64))
    };
    let mut nodes = Vec::with_capacity(order.len());
    for &old in &order {
        let node = Val::dict(interop::entries_of(&rows[old])?);
        let renumbered = inputs(&rows[old])?.into_iter().map(renumber).collect::<Result<Vec<_>>>()?;
        node.set(py::s("inputs"), Val::list(renumbered))?;
        nodes.push(node);
    }
    let out = py::dict([("nodes", Val::list(nodes)), ("result", renumber(result)?)]);
    if !extras.is_empty() {
        let rows = extras.iter().map(|(key, index)| Ok((key.clone(), renumber(*index)?))).collect::<Result<Vec<_>>>()?;
        out.set(py::s("extras"), Val::dict(rows))?;
    }
    Ok(out)
}

/// A graph method or attribute as generated code reads it from the graph's namespace.
fn graph_method(graph: &Graph, name: &str) -> Result<Val> {
    let g = graph.clone();
    Ok(match name {
        "nodes" => graph.nodes(),
        "add" => Val::function(move |args, kwargs| {
            let (_, op, inputs, bounds, numbers) = bind_add(args, kwargs, false)?;
            Ok(g.add_val(op, &inputs, &bounds, numbers)?.to_val())
        }),
        "box" => Val::function(move |args, _| Ok(g.box_(args)?.to_val())),
        "cylinder" => Val::function(move |args, kwargs| {
            let mut b = py::bind(args, kwargs, &["axis", "radius", "a", "b", "lo", "hi"], &[])?;
            let axis = b.req("axis")?.integer()?;
            let [radius, a, c, lo, hi] = ["radius", "a", "b", "lo", "hi"].map(|n| b.req(n).and_then(|v| Num::of(&v)));
            Ok(g.cylinder(axis, radius?, a?, c?, lo?, hi?)?.to_val())
        }),
        "prism" => Val::function(move |args, kwargs| {
            let mut b = py::bind(args, kwargs, &["axis", "lo", "hi", "section"], &[])?;
            let axis = b.req("axis")?.integer()?;
            let lo = Num::of(&b.req("lo")?)?;
            let hi = Num::of(&b.req("hi")?)?;
            Ok(g.prism(axis, lo, hi, &b.req("section")?)?.to_val())
        }),
        "rounded" => Val::function(move |args, kwargs| {
            let mut b = py::bind(args, kwargs, &["shape", "radius"], &[])?;
            let shape = Solid::from_val(&b.req("shape")?);
            let radius = Num::of(&b.req("radius")?)?;
            Ok(g.rounded(&shape, radius)?.to_val())
        }),
        "document" if !graph.is_questions() => Val::function(move |args, kwargs| {
            let mut b = py::bind(args, kwargs, &["result", "extras"], &[])?;
            let result = Solid::from_val(&b.req("result")?);
            let extras = extras_of(&b.opt("extras").unwrap_or(Val::None))?;
            g.document(&result, &extras)
        }),
        "document" => Val::function(move |args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            g.questions_document()
        }),
        "model" if graph.is_questions() => Val::function(move |args, kwargs| {
            let mut b = py::bind(args, kwargs, &["value"], &[])?;
            Ok(g.model(&b.req("value")?)?.to_val())
        }),
        "identity" if graph.is_questions() => Val::function(move |args, kwargs| {
            let mut b = py::bind(args, kwargs, &["index"], &[])?;
            Ok(Val::Str(g.identity(b.req("index")?.integer()? as usize)?))
        }),
        "reading" if graph.is_questions() => Val::function(move |args, kwargs| {
            let mut b = py::bind(args, kwargs, &["shape"], &["kind", "components", "valid"])?;
            let shape = Solid::from_val(&b.req("shape")?);
            let kind = b.string_or("kind", "stats")?;
            let components = b.bool_or("components", false)?;
            let valid = b.bool_or("valid", false)?;
            g.reading(&shape, &kind, components, valid)
        }),
        _ => return Err(attribute_error(graph.kind(), name)),
    })
}

/// `(self, op, inputs=(), *, bounds=None, **numbers)` as `_Graph.add` binds them.
pub fn bind_add(args: Args, kwargs: Kwargs, with_self: bool) -> Result<(Option<Val>, Val, Val, Val, Kwargs)> {
    let mut args = args.into_iter();
    let mut me = if with_self { args.next() } else { None };
    let mut op = args.next();
    let mut inputs = args.next();
    ensure!(args.next().is_none(), "add() takes at most 3 positional arguments");
    let mut bounds = None;
    let mut numbers = vec![];
    for (key, value) in kwargs {
        match key.as_str() {
            "self" if with_self && me.is_none() => me = Some(value),
            "op" if op.is_none() => op = Some(value),
            "inputs" if inputs.is_none() => inputs = Some(value),
            "bounds" => bounds = Some(value),
            _ => numbers.push((key, value)),
        }
    }
    Ok((me, op.context("add() missing argument 'op'")?, inputs.unwrap_or(Val::Tuple(vec![])), bounds.unwrap_or(Val::None), numbers))
}

/// `(extras or {}).items()` with each shape.
fn extras_of(extras: &Val) -> Result<Vec<(Val, Solid)>> {
    if !extras.truthy()? {
        return Ok(vec![]);
    }
    py::method(extras, "items", vec![])?.iter()?.into_iter().map(|row| {
        let pair = py::unpack(&row, 2)?;
        Ok((pair[0].clone(), Solid::from_val(&pair[1])))
    }).collect()
}

// ------------------------------------------------------------------------------------------
// Questions graphs (the typed half of `_rust_enclosure_checks._Questions`)

impl Graph {
    fn questions_only(&self, method: &str) -> Result<()> {
        ensure!(self.0.questions, "'_Graph' object has no attribute '{method}'");
        Ok(())
    }
    /// `graph.answers`.
    pub fn answers(&self) -> Result<Val> {
        self.attr("answers")
    }
    /// `graph.queries`.
    pub fn queries(&self) -> Result<Val> {
        self.attr("queries")
    }
    /// `graph.extras`.
    pub fn extras(&self) -> Result<Val> {
        self.attr("extras")
    }
    /// `_Questions.model(value)`: a model reference (a path, a reference row, or a list of them,
    /// fused) as a reading shape.
    #[track_caller]
    pub fn model(&self, value: &Val) -> Result<Solid> {
        self.questions_only("model")?;
        let site = rt::site();
        self.model_at(value, &site)
    }
    fn model_at(&self, value: &Val, site: &Val) -> Result<Solid> {
        if is_instance(value, &["list", "tuple"])? {
            let parts = value.iter()?.iter().map(|row| self.model_at(row, site)).collect::<Result<Vec<_>>>()?;
            return match parts.split_first() {
                Some((first, rest)) => first.fuse(rest),
                None => Ok(Solid::Native(self.record(py::s("empty"), vec![], None, vec![], site.clone()))),
            };
        }
        let reference = if is_instance(value, &["str", "Path"])? {
            py::dict([("model", Val::Str(resolved(value)?))])
        } else {
            builtin("dict")?.call(vec![value.clone()], vec![])?
        };
        let model = reference.get(py::s("model"))?;
        reference.set(py::s("model"), Val::Str(resolved(&model)?))?;
        Ok(Solid::Native(self.record(py::s("model"), vec![], None, vec![("reference".into(), reference)], site.clone())))
    }
    /// `_Questions.identity(index)`: the content key of a node and everything it is built from.
    pub fn identity(&self, index: usize) -> Result<String> {
        self.questions_only("identity")?;
        let epoch = self.0.epoch.get();
        let rows = self.rows();
        let mut keys = self.0.keys.borrow_mut();
        if keys.0 != epoch {
            *keys = (epoch, vec![]);
        }
        let rows = rows.borrow();
        ensure!(index < rows.len(), "list index out of range");
        while keys.1.len() <= index {
            let key = node_key(&rows[keys.1.len()], &keys.1)?;
            keys.1.push(key);
        }
        Ok(keys.1[index].clone())
    }
    /// `_Questions.reading(shape, kind=.., components=.., valid=..)`: the measured row, or the
    /// placeholder while the questions are being collected.
    pub fn reading(&self, shape: &Solid, kind: &str, components: bool, valid: bool) -> Result<Val> {
        self.questions_only("reading")?;
        let index = shape.index()?;
        let key = format!("{}:{kind}", self.identity(index)?);
        let answers = self.answers()?;
        if !matches!(answers, Val::None) {
            let local = self.answer_rows(&answers)?;
            let row = match &local {
                Val::Dict(_) => local.get(py::s(&key)).ok(),
                _ => None,
            };
            let row = match row {
                Some(row) => row,
                None if matches!(local, Val::Dict(_)) => bail!("an enclosure report asked an unmeasured question: {key}"),
                None => {
                    if !answers.contains(&py::s(&key))? {
                        bail!("an enclosure report asked an unmeasured question: {key}");
                    }
                    answers.get(py::s(&key))?
                }
            };
            if components && !row.contains(&py::s("components"))? {
                bail!("an enclosure report asked unmeasured components: {key}");
            }
            return Ok(row);
        }
        let queries = self.queries()?;
        let fresh = py::dict([("key", py::s(&key)), ("node", Val::Int(index as i64)), ("kind", py::s(kind))]);
        let query = py::method(&queries, "setdefault", vec![py::s(&key), fresh])?;
        if components {
            query.set(py::s("components"), Val::Bool(true))?;
        }
        if valid {
            query.set(py::s("valid"), Val::Bool(true))?;
        }
        Ok(if kind == "faces" {
            Val::list(vec![])
        } else {
            py::dict([
                ("volume_mm3", Val::Float(0.)),
                ("min", Val::None),
                ("max", Val::None),
                ("components", Val::list(vec![])),
                ("valid", Val::Bool(true)),
            ])
        })
    }
    /// The answers as local values, read in one callback the first time.
    fn answer_rows(&self, answers: &Val) -> Result<Val> {
        if let Some((source, local)) = self.0.answers.borrow().as_ref() {
            if same_value(source, answers) {
                return Ok(local.clone());
            }
        }
        let local = py::snapshot(answers)?;
        *self.0.answers.borrow_mut() = Some((answers.clone(), local.clone()));
        Ok(local)
    }
    /// `_Questions.document()`: every question is a root.
    pub fn questions_document(&self) -> Result<Val> {
        self.questions_only("document")?;
        let rows = self.rows().borrow().clone();
        questions_rows(&rows, &py::method(&self.queries()?, "values", vec![])?.iter()?)
    }
}

/// `_Questions.document` of nodes and query rows held locally.
pub fn questions_rows(rows: &[Val], queries: &[Val]) -> Result<Val> {
    let mut needed = vec![false; rows.len()];
    for query in queries {
        let mut stack = vec![query.get(py::s("node"))?.integer()? as usize];
        while let Some(index) = stack.pop() {
            ensure!(index < rows.len(), "list index out of range");
            if needed[index] {
                continue;
            }
            needed[index] = true;
            for child in rows[index].get(py::s("inputs"))?.iter()? {
                stack.push(child.integer()? as usize);
            }
        }
    }
    let mut remap = vec![usize::MAX; rows.len()];
    let mut order = vec![];
    for (old, kept) in needed.iter().enumerate() {
        if *kept {
            remap[old] = order.len();
            order.push(old);
        }
    }
    let renumber = |index: &Val| -> Result<Val> {
        let index = index.integer()? as usize;
        let new = *remap.get(index).context("missing key")?;
        ensure!(new != usize::MAX, "missing key {index}");
        Ok(Val::Int(new as i64))
    };
    let mut nodes = Vec::with_capacity(order.len());
    for &old in &order {
        let node = Val::dict(interop::entries_of(&rows[old])?);
        let inputs = rows[old].get(py::s("inputs"))?.iter()?.iter().map(renumber).collect::<Result<Vec<_>>>()?;
        node.set(py::s("inputs"), Val::list(inputs))?;
        nodes.push(node);
    }
    let questions = queries.iter().map(|row| {
        let out = Val::dict(interop::entries_of(row)?);
        out.set(py::s("node"), renumber(&row.get(py::s("node"))?)?)?;
        Ok(out)
    }).collect::<Result<Vec<_>>>()?;
    Ok(py::dict([("nodes", Val::list(nodes)), ("queries", Val::list(questions))]))
}

/// One node's identity key: its numbers with its inputs' keys, hashed.
pub fn node_key(node: &Val, keys: &[String]) -> Result<String> {
    let row = Val::dict(vec![]);
    for (key, value) in interop::entries_of(node)? {
        if !matches!(&key, Val::Str(k) if k == "inputs" || k == "source") {
            row.set(key, value)?;
        }
    }
    let inputs = node.get(py::s("inputs"))?.iter()?.iter().map(|k| {
        keys.get(k.integer()? as usize).cloned().map(Val::Str).context("list index out of range")
    }).collect::<Result<Vec<_>>>()?;
    row.set(py::s("inputs"), Val::list(inputs))?;
    let (dumps, sha256) = HASHING.with(|held| held.clone());
    let text = dumps.call(vec![row], vec![
        ("sort_keys".into(), Val::Bool(true)),
        ("separators".into(), Val::Tuple(vec![py::s(","), py::s(":")])),
    ])?.str()?;
    let digest = sha256.call(vec![Val::Bytes(text.into_bytes())], vec![])?;
    py::method(&digest, "hexdigest", vec![])?.str()
}

thread_local! {
    /// `json.dumps` and `hashlib.sha256` of the runtime's own modules.
    static HASHING: (Val, Val) = (
        interop::builtin_module("json").and_then(|m| m.attr("dumps").ok()).expect("json.dumps"),
        interop::builtin_module("hashlib").and_then(|m| m.attr("sha256").ok()).expect("hashlib.sha256"),
    );
}

/// Whether two values are one object (`is`), for values held locally or by reference.
fn same_value(a: &Val, b: &Val) -> bool {
    match (a, b) {
        (Val::Ref(a), Val::Ref(b)) => a == b,
        (Val::Dict(a), Val::Dict(b)) => Rc::ptr_eq(a, b),
        (Val::None, Val::None) => true,
        _ => false,
    }
}

pub fn builtin(name: &str) -> Result<Val> {
    interop::builtin(name).with_context(|| format!("builtin {name}"))
}

/// `isinstance(value, (kind, ...))` with the runtime's builtin classes.
pub fn is_instance(value: &Val, kinds: &[&str]) -> Result<bool> {
    let kinds = kinds.iter().map(|k| if *k == "Path" { Ok(Val::Type("Path".into())) } else { builtin(k) }).collect::<Result<Vec<_>>>()?;
    builtin("isinstance")?.call(vec![value.clone(), Val::Tuple(kinds)], vec![])?.truthy()
}

/// `str(Path(value).resolve())`.
pub fn resolved(value: &Val) -> Result<String> {
    let path = Val::Type("Path".into()).call(vec![value.clone()], vec![])?;
    py::method(&path, "resolve", vec![])?.str()
}

// ------------------------------------------------------------------------------------------
// Shapes

struct ShapeCore {
    graph: Graph,
    index: usize,
}

struct ShapeCell {
    core: Rc<ShapeCore>,
    /// The bounds while the shape has no namespace; its namespace's `bounds` field after.
    bounds: RefCell<Option<Bounds>>,
    face: RefCell<Option<Entries>>,
}

/// A native node of a [`Graph`] and the box that conservatively holds what it makes.
#[derive(Clone)]
pub struct Shape(Rc<ShapeCell>);

impl Shape {
    fn new(graph: Graph, index: usize, bounds: Option<Bounds>) -> Shape {
        Shape(Rc::new(ShapeCell {
            core: Rc::new(ShapeCore { graph, index }),
            bounds: RefCell::new(bounds),
            face: RefCell::new(None),
        }))
    }
    fn with_face(core: Rc<ShapeCore>, face: Entries) -> Shape {
        Shape(Rc::new(ShapeCell { core, bounds: RefCell::new(None), face: RefCell::new(Some(face)) }))
    }
    pub fn graph(&self) -> &Graph {
        &self.0.core.graph
    }
    pub fn index(&self) -> usize {
        self.0.core.index
    }
    /// Whether this is a `_ReadingShape` (a shape of a questions graph).
    pub fn is_reading(&self) -> bool {
        self.0.core.graph.0.questions
    }
    fn kind(&self) -> &'static str {
        if self.is_reading() { "_ReadingShape" } else { "_Shape" }
    }
    /// The same node (`self is other` across the namespace boundary).
    pub fn same(&self, other: &Shape) -> bool {
        Rc::ptr_eq(&self.0.core, &other.0.core)
    }
    fn face_field(&self, name: &str) -> Option<Val> {
        let face = self.0.face.borrow();
        let face = face.as_ref()?;
        let entries = face.borrow();
        entries.iter().find_map(|(key, value)| match key {
            Val::Str(key) if key == name => Some(value.clone()),
            _ => None,
        })
    }
    /// `shape.bounds`.
    pub fn bounds(&self) -> Result<Option<Bounds>> {
        match self.face_field("bounds") {
            Some(value) => Bounds::from_val(&value),
            None if self.0.face.borrow().is_some() => Err(attribute_error(self.kind(), "bounds")),
            None => Ok(*self.0.bounds.borrow()),
        }
    }
    /// `shape.bounds` as Python holds it.
    pub fn bounds_val(&self) -> Result<Val> {
        match self.face_field("bounds") {
            Some(value) => Ok(value),
            None if self.0.face.borrow().is_some() => Err(attribute_error(self.kind(), "bounds")),
            None => Ok(self.0.bounds.borrow().map_or(Val::None, |b| b.to_val())),
        }
    }
    /// `shape.bounds = bounds`.
    pub fn set_bounds(&self, bounds: Option<Bounds>) -> Result<()> {
        let face = self.0.face.borrow().clone();
        match face {
            Some(face) => Val::Namespace(face).set(py::s("bounds"), bounds.map_or(Val::None, |b| b.to_val())),
            None => {
                *self.0.bounds.borrow_mut() = bounds;
                Ok(())
            }
        }
    }
    /// The value generated code receives: one namespace per shape, made when it first crosses.
    pub fn to_val(&self) -> Val {
        if let Some(face) = self.0.face.borrow().as_ref() {
            return Val::Namespace(face.clone());
        }
        let bounds = self.0.bounds.borrow().map_or(Val::None, |b| b.to_val());
        let entries: Entries = Rc::new(RefCell::new(vec![]));
        let core = self.0.core.clone();
        let mark = {
            let core = core.clone();
            Val::function(move |_, _| {
                HANDOFF.with(|slot| *slot.borrow_mut() = Some(Handoff::Shape(core.clone())));
                Ok(Val::None)
            })
        };
        let getattr = {
            let core = core.clone();
            let face = Rc::downgrade(&entries);
            Val::function(move |args, _| {
                let face = face.upgrade().context("a shape's namespace is gone")?;
                shape_method(&Shape::with_face(core.clone(), face), &args.first().context("attribute name")?.str()?)
            })
        };
        *entries.borrow_mut() = vec![
            (py::s("graph"), core.graph.to_val()),
            (py::s("index"), Val::Int(core.index as i64)),
            (py::s("bounds"), bounds),
            (py::s(MARK), mark),
            (py::s("__getattr__"), getattr),
        ];
        *self.0.face.borrow_mut() = Some(entries.clone());
        Val::Namespace(entries)
    }
    /// The shape a value generated code holds stands for.
    pub fn from_val(value: &Val) -> Option<Shape> {
        let Val::Namespace(entries) = value else { return None };
        match handoff(value)? {
            Handoff::Shape(core) => Some(Shape::with_face(core, entries.clone())),
            Handoff::Graph(_) => None,
        }
    }

    /// `_Shape._boolean(op, others)`: `cut` leaves out operands whose bounds miss this one's.
    #[track_caller]
    pub fn boolean(&self, op: &str, others: &[Solid]) -> Result<Shape> {
        let own = self.bounds()?;
        let mut nodes: Vec<(Val, Option<Bounds>)> = vec![(Val::Int(self.index() as i64), own)];
        for other in others {
            let bounds = other.bounds()?;
            if op == "cut" && own.is_some() && bounds.is_some_and(|b| !own.unwrap().overlaps(&b)) {
                continue;
            }
            nodes.push((other.index_val()?, bounds));
        }
        if nodes.len() == 1 {
            return Ok(self.clone());
        }
        let all = nodes.iter().all(|(_, b)| b.is_some());
        let bounds = match op {
            "union" if all => Some(combined(&nodes, false)?),
            "union" => None,
            "intersect" if all => Some(combined(&nodes, true)?),
            _ => own,
        };
        let inputs = nodes.into_iter().map(|(index, _)| index).collect();
        Ok(self.graph().record(py::s(op), inputs, bounds, vec![], rt::site()))
    }
    /// `shape.fuse(*others)`.
    #[track_caller]
    pub fn fuse(&self, others: &[Solid]) -> Result<Shape> {
        self.boolean("union", others)
    }
    /// `shape.cut(*others)`.
    #[track_caller]
    pub fn cut(&self, others: &[Solid]) -> Result<Shape> {
        self.boolean("cut", others)
    }
    /// `shape.intersect(*others)`.
    #[track_caller]
    pub fn intersect(&self, others: &[Solid]) -> Result<Shape> {
        self.boolean("intersect", others)
    }
    /// `shape.translate(delta)`: `delta` is recorded as given (a reading shape records
    /// `tuple(delta)`).
    #[track_caller]
    pub fn translate(&self, delta: &Val) -> Result<Shape> {
        let delta = if self.is_reading() { Val::Tuple(delta.iter()?) } else { delta.clone() };
        let bounds = match self.bounds()? {
            Some(b) => Some(translated(&b, &delta)?),
            None => None,
        };
        Ok(self.graph().record(py::s("translate"), vec![Val::Int(self.index() as i64)], bounds,
            vec![("delta".into(), delta)], rt::site()))
    }
    /// `shape.rotate(origin, end, angle)`: about the axis from `origin` to `end`, in degrees.
    #[track_caller]
    pub fn rotate(&self, origin: &Val, end: &Val, angle: &Val) -> Result<Shape> {
        let bounds = rotated(self.bounds()?, origin, end, angle)?;
        Ok(self.graph().record(py::s("rotate"), vec![Val::Int(self.index() as i64)], bounds, vec![
            ("origin".into(), origin.clone()),
            ("end".into(), end.clone()),
            ("angle".into(), angle.clone()),
        ], rt::site()))
    }
    /// `shape.mirror(plane)` for `'YZ'`, `'XZ'` or `'XY'`.
    #[track_caller]
    pub fn mirror(&self, plane: &Val) -> Result<Shape> {
        let axis = mirror_axis(plane)?;
        let bounds = self.bounds()?.map(|b| mirrored(&b, axis));
        Ok(self.graph().record(py::s("mirror"), vec![Val::Int(self.index() as i64)], bounds,
            vec![("axis".into(), Val::Int(axis as i64))], rt::site()))
    }
    /// `_Shape.BoundingBox()`: a namespace of the six bounds.
    pub fn bounding_box(&self) -> Result<Val> {
        if self.is_reading() {
            return super::_rust_enclosure_checks::reading_bounding_box(self);
        }
        let bounds = self.bounds_val()?;
        bounding_namespace(&rt::current()?, &bounds)
    }
}

impl py::Py for Shape {
    fn to_py(&self) -> Result<Val> {
        Ok(self.to_val())
    }
    fn from_py(value: &Val) -> Result<Self> {
        Shape::from_val(value).context("not a native construction shape")
    }
}

/// The union (`intersect` false) or intersection bounds of the operands.
fn combined(nodes: &[(Val, Option<Bounds>)], intersect: bool) -> Result<Bounds> {
    let mut v = [Num::F(0.); 6];
    for k in 0..3 {
        let lows = nodes.iter().map(|(_, b)| b.unwrap().lo(k));
        let highs = nodes.iter().map(|(_, b)| b.unwrap().hi(k));
        if intersect {
            v[2 * k] = most(lows)?;
            v[2 * k + 1] = least(highs)?;
        } else {
            v[2 * k] = least(lows)?;
            v[2 * k + 1] = most(highs)?;
        }
    }
    Ok(Bounds::tuple(v))
}

fn translated(b: &Bounds, delta: &Val) -> Result<Bounds> {
    let d = three(delta)?;
    let mut v = b.v;
    for k in 0..3 {
        v[2 * k] = b.v[2 * k].add(d[k]);
        v[2 * k + 1] = b.v[2 * k + 1].add(d[k]);
    }
    Ok(Bounds::tuple(v))
}

fn rotated(bounds: Option<Bounds>, origin: &Val, end: &Val, angle: &Val) -> Result<Option<Bounds>> {
    let origin = numbers_of(origin)?;
    let end = numbers_of(end)?;
    let axis: Vec<Num> = origin.iter().zip(&end).map(|(a, b)| b.sub(*a)).collect();
    let length = axis.iter().fold(Num::I(0), |sum, a| sum.add(a.mul(*a))).f().sqrt();
    ensure!(length != 0., "division by zero");
    let axis: Vec<f64> = axis.iter().map(|a| a.f() / length).collect();
    let angle = super::num::radians(angle.num()?);
    let (c, s) = (super::num::cos(angle), super::num::sin(angle));
    let Some(b) = bounds else { return Ok(None) };
    ensure!(axis.len() == 3 && origin.len() == 3, "rotation axis needs three coordinates");
    let point = |p: [Num; 3]| -> [f64; 3] {
        let q: Vec<f64> = p.iter().zip(&origin).map(|(a, b)| a.sub(*b).f()).collect();
        let cross = [axis[1] * q[2] - axis[2] * q[1], axis[2] * q[0] - axis[0] * q[2], axis[0] * q[1] - axis[1] * q[0]];
        let dot = axis.iter().zip(&q).fold(0f64, |sum, (a, b)| sum + a * b);
        [0, 1, 2].map(|k| origin[k].f() + c * q[k] + s * cross[k] + (1. - c) * dot * axis[k])
    };
    let mut corners = vec![];
    for x in [b.v[0], b.v[1]] {
        for y in [b.v[2], b.v[3]] {
            for z in [b.v[4], b.v[5]] {
                corners.push(point([x, y, z]));
            }
        }
    }
    let mut v = [Num::F(0.); 6];
    for k in 0..3 {
        v[2 * k] = least(corners.iter().map(|p| Num::F(p[k])))?;
        v[2 * k + 1] = most(corners.iter().map(|p| Num::F(p[k])))?;
    }
    Ok(Some(Bounds::tuple(v)))
}

fn mirror_axis(plane: &Val) -> Result<usize> {
    Ok(match plane {
        Val::Str(p) if p == "YZ" => 0,
        Val::Str(p) if p == "XZ" => 1,
        Val::Str(p) if p == "XY" => 2,
        other => bail!("missing key {}", other.repr()?),
    })
}

fn mirrored(b: &Bounds, axis: usize) -> Bounds {
    let mut v = b.v;
    v[2 * axis] = b.v[2 * axis + 1].neg();
    v[2 * axis + 1] = b.v[2 * axis].neg();
    Bounds::list(v)
}

/// `SimpleNamespace(xmin=.., xmax=.., ymin=.., ymax=.., zmin=.., zmax=..)` of a bounds value.
fn bounding_namespace(rt: &Rt, bounds: &Val) -> Result<Val> {
    if matches!(bounds, Val::None) {
        bail!("this private feature has no conservative numeric bounds");
    }
    let values = py::snapshot(bounds)?;
    let mut kwargs = vec![];
    for (k, axis) in ["x", "y", "z"].iter().enumerate() {
        for (i, suffix) in ["min", "max"].iter().enumerate() {
            kwargs.push((format!("{axis}{suffix}"), values.get(Val::Int((2 * k + i) as i64))?));
        }
    }
    simple_namespace(rt)?.call(vec![], kwargs)
}

/// A shape method as generated code reads it from the shape's namespace.
fn shape_method(me: &Shape, name: &str) -> Result<Val> {
    let me = me.clone();
    let reading = me.is_reading();
    Ok(match name {
        "_boolean" => Val::function(move |args, kwargs| {
            let mut b = py::bind(args, kwargs, &["op", "others"], &[])?;
            let op = b.string("op")?;
            let others = solids(&b.req("others")?)?;
            Ok(me.boolean(&op, &others)?.to_val())
        }),
        "fuse" | "cut" | "intersect" => {
            let op = if name == "fuse" { "union" } else if name == "cut" { "cut" } else { "intersect" };
            Val::function(move |args, _| {
                let others: Vec<Solid> = args.iter().map(Solid::from_val).collect();
                Ok(me.boolean(op, &others)?.to_val())
            })
        }
        "translate" => Val::function(move |args, kwargs| {
            let mut b = py::bind(args, kwargs, &["delta"], &[])?;
            Ok(me.translate(&b.req("delta")?)?.to_val())
        }),
        "rotate" => Val::function(move |args, kwargs| {
            let mut b = py::bind(args, kwargs, &["origin", "end", "angle"], &[])?;
            Ok(me.rotate(&b.req("origin")?, &b.req("end")?, &b.req("angle")?)?.to_val())
        }),
        "mirror" => Val::function(move |args, kwargs| {
            let mut b = py::bind(args, kwargs, &["plane"], &[])?;
            Ok(me.mirror(&b.req("plane")?)?.to_val())
        }),
        "clean" | "val" => Val::function(move |args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            Ok(me.to_val())
        }),
        "BoundingBox" => Val::function(move |args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            me.bounding_box()
        }),
        "Solids" if reading => Val::function(move |args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            super::_rust_enclosure_checks::reading_solids(&me)
        }),
        "Solids" => Val::function(move |args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            Ok(Val::list(vec![me.to_val()]))
        }),
        "Volume" if reading => Val::function(move |args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            super::_rust_enclosure_checks::reading_volume(&me)
        }),
        "isValid" if reading => Val::function(move |args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            super::_rust_enclosure_checks::reading_is_valid(&me)
        }),
        "Faces" if reading => Val::function(move |args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            super::_rust_enclosure_checks::reading_faces(&me)
        }),
        _ => return Err(attribute_error(me.kind(), name)),
    })
}

fn solids(values: &Val) -> Result<Vec<Solid>> {
    Ok(values.iter()?.iter().map(Solid::from_val).collect())
}

// ------------------------------------------------------------------------------------------
// Solids: native or Python

/// A solid a typed caller holds: a native shape, or any other value (a Python shape, `None`).
#[derive(Clone)]
pub enum Solid {
    Native(Shape),
    Py(Val),
}

impl Solid {
    /// The native shape a value stands for, else the value itself.
    pub fn from_val(value: &Val) -> Solid {
        match Shape::from_val(value) {
            Some(shape) => Solid::Native(shape),
            None => Solid::Py(value.clone()),
        }
    }
    /// The value generated code receives.
    pub fn to_val(&self) -> Val {
        match self {
            Solid::Native(shape) => shape.to_val(),
            Solid::Py(value) => value.clone(),
        }
    }
    pub fn native(&self) -> Option<&Shape> {
        match self {
            Solid::Native(shape) => Some(shape),
            Solid::Py(_) => None,
        }
    }
    pub fn is_none(&self) -> bool {
        matches!(self, Solid::Py(Val::None))
    }
    /// `self is other`.
    pub fn same(&self, other: &Solid) -> Result<bool> {
        Ok(match (self, other) {
            (Solid::Native(a), Solid::Native(b)) => a.same(b),
            (Solid::Native(_), _) | (_, Solid::Native(_)) => false,
            (Solid::Py(a), Solid::Py(b)) => interop::compare("is", a.clone(), b.clone())?.truthy()?,
        })
    }
    /// `shape.<name>(*args, **kwargs)` through the value generated code would hold.
    pub fn method(&self, name: &str, args: Args, kwargs: Kwargs) -> Result<Val> {
        self.to_val().attr(name)?.call(args, kwargs)
    }
    fn py_op(&self, name: &str, args: Args) -> Result<Solid> {
        Ok(Solid::from_val(&self.method(name, args, vec![])?))
    }
    /// `shape.index`.
    pub fn index_val(&self) -> Result<Val> {
        match self {
            Solid::Native(shape) => Ok(Val::Int(shape.index() as i64)),
            Solid::Py(value) => value.attr("index"),
        }
    }
    pub fn index(&self) -> Result<usize> {
        Ok(self.index_val()?.integer()? as usize)
    }
    /// `shape.bounds`.
    pub fn bounds(&self) -> Result<Option<Bounds>> {
        match self {
            Solid::Native(shape) => shape.bounds(),
            Solid::Py(value) => Bounds::from_val(&value.attr("bounds")?),
        }
    }
    /// `shape.bounds` as Python holds it.
    pub fn bounds_val(&self) -> Result<Val> {
        match self {
            Solid::Native(shape) => shape.bounds_val(),
            Solid::Py(value) => value.attr("bounds"),
        }
    }
    #[track_caller]
    pub fn cut(&self, others: &[Solid]) -> Result<Solid> {
        match self {
            Solid::Native(shape) => shape.cut(others).map(Solid::Native),
            Solid::Py(_) => self.py_op("cut", others.iter().map(Solid::to_val).collect()),
        }
    }
    #[track_caller]
    pub fn fuse(&self, others: &[Solid]) -> Result<Solid> {
        match self {
            Solid::Native(shape) => shape.fuse(others).map(Solid::Native),
            Solid::Py(_) => self.py_op("fuse", others.iter().map(Solid::to_val).collect()),
        }
    }
    #[track_caller]
    pub fn intersect(&self, others: &[Solid]) -> Result<Solid> {
        match self {
            Solid::Native(shape) => shape.intersect(others).map(Solid::Native),
            Solid::Py(_) => self.py_op("intersect", others.iter().map(Solid::to_val).collect()),
        }
    }
    #[track_caller]
    pub fn translate(&self, delta: &Val) -> Result<Solid> {
        match self {
            Solid::Native(shape) => shape.translate(delta).map(Solid::Native),
            Solid::Py(_) => self.py_op("translate", vec![delta.clone()]),
        }
    }
    #[track_caller]
    pub fn rotate(&self, origin: &Val, end: &Val, angle: &Val) -> Result<Solid> {
        match self {
            Solid::Native(shape) => shape.rotate(origin, end, angle).map(Solid::Native),
            Solid::Py(_) => self.py_op("rotate", vec![origin.clone(), end.clone(), angle.clone()]),
        }
    }
    #[track_caller]
    pub fn mirror(&self, plane: &Val) -> Result<Solid> {
        match self {
            Solid::Native(shape) => shape.mirror(plane).map(Solid::Native),
            Solid::Py(_) => self.py_op("mirror", vec![plane.clone()]),
        }
    }
    pub fn clean(&self) -> Result<Solid> {
        match self {
            Solid::Native(_) => Ok(self.clone()),
            Solid::Py(_) => self.py_op("clean", vec![]),
        }
    }
    pub fn val(&self) -> Result<Solid> {
        match self {
            Solid::Native(_) => Ok(self.clone()),
            Solid::Py(_) => self.py_op("val", vec![]),
        }
    }
    /// `shape.Solids()`: a construction shape is its own one solid; a reading shape's are the
    /// measured components.
    pub fn solids(&self) -> Result<Vec<Solid>> {
        match self {
            Solid::Native(shape) if shape.is_reading() => {
                Ok(super::_rust_enclosure_checks::reading_solids(shape)?.iter()?.iter().map(Solid::from_val).collect())
            }
            Solid::Native(_) => Ok(vec![self.clone()]),
            Solid::Py(_) => Ok(self.method("Solids", vec![], vec![])?.iter()?.iter().map(Solid::from_val).collect()),
        }
    }
    /// `shape.BoundingBox()`.
    pub fn bounding_box(&self) -> Result<Val> {
        match self {
            Solid::Native(shape) => shape.bounding_box(),
            Solid::Py(_) => self.method("BoundingBox", vec![], vec![]),
        }
    }
    /// `shape.Volume()` of a reading shape.
    pub fn volume(&self) -> Result<Val> {
        match self {
            Solid::Native(shape) if shape.is_reading() => super::_rust_enclosure_checks::reading_volume(shape),
            Solid::Native(shape) => Err(attribute_error(shape.kind(), "Volume")),
            Solid::Py(_) => self.method("Volume", vec![], vec![]),
        }
    }
    /// `shape.isValid()` of a reading shape.
    pub fn is_valid(&self) -> Result<Val> {
        match self {
            Solid::Native(shape) if shape.is_reading() => super::_rust_enclosure_checks::reading_is_valid(shape),
            Solid::Native(shape) => Err(attribute_error(shape.kind(), "isValid")),
            Solid::Py(_) => self.method("isValid", vec![], vec![]),
        }
    }
    /// `shape.Faces()` of a reading shape: the measured faces (`_ScalarFace` objects).
    pub fn faces(&self) -> Result<Vec<Val>> {
        match self {
            Solid::Native(shape) if shape.is_reading() => super::_rust_enclosure_checks::reading_faces(shape)?.iter(),
            Solid::Native(shape) => Err(attribute_error(shape.kind(), "Faces")),
            Solid::Py(_) => self.method("Faces", vec![], vec![])?.iter(),
        }
    }
}

impl py::Py for Solid {
    fn to_py(&self) -> Result<Val> {
        Ok(self.to_val())
    }
    fn from_py(value: &Val) -> Result<Self> {
        Ok(Solid::from_val(value))
    }
}

impl From<Shape> for Solid {
    fn from(shape: Shape) -> Solid {
        Solid::Native(shape)
    }
}

// ------------------------------------------------------------------------------------------
// Graphs that may be Python objects

/// A graph argument: a native [`Graph`] or a Python graph object (called through its methods).
#[derive(Clone)]
pub enum AnyGraph {
    Native(Graph),
    Py(Val),
}

impl AnyGraph {
    pub fn from_val(value: &Val) -> AnyGraph {
        match Graph::from_val(value) {
            Some(graph) => AnyGraph::Native(graph),
            None => AnyGraph::Py(value.clone()),
        }
    }
    pub fn to_val(&self) -> Val {
        match self {
            AnyGraph::Native(graph) => graph.to_val(),
            AnyGraph::Py(value) => value.clone(),
        }
    }
    pub fn native(&self) -> Option<&Graph> {
        match self {
            AnyGraph::Native(graph) => Some(graph),
            AnyGraph::Py(_) => None,
        }
    }
    /// `graph.<name>` (`nodes`, `extras`, `answers`, ...).
    pub fn attr(&self, name: &str) -> Result<Val> {
        match self {
            AnyGraph::Native(graph) => graph.attr(name),
            AnyGraph::Py(value) => value.attr(name),
        }
    }
    pub fn set_attr(&self, name: &str, value: Val) -> Result<()> {
        match self {
            AnyGraph::Native(graph) => graph.set_attr(name, value),
            AnyGraph::Py(graph) => graph.setattr(name, value),
        }
    }
    /// `graph.nodes[index]`.
    pub fn node(&self, index: usize) -> Result<Val> {
        match self {
            AnyGraph::Native(graph) => graph.node(index),
            AnyGraph::Py(value) => value.attr("nodes")?.get(Val::Int(index as i64)),
        }
    }
    /// `graph.add(op, inputs, bounds=bounds, **numbers)`.
    #[track_caller]
    pub fn add(&self, op: &str, inputs: Vec<Val>, bounds: Val, numbers: Vec<(&str, Val)>) -> Result<Solid> {
        match self {
            AnyGraph::Native(graph) => {
                let numbers = numbers.into_iter().map(|(k, v)| (k.to_owned(), v)).collect();
                Ok(Solid::Native(graph.add_val(py::s(op), &Val::list(inputs), &bounds, numbers)?))
            }
            AnyGraph::Py(value) => {
                let mut kwargs = vec![("bounds".to_owned(), bounds)];
                kwargs.extend(numbers.into_iter().map(|(k, v)| (k.to_owned(), v)));
                Ok(Solid::from_val(&value.attr("add")?.call(vec![py::s(op), Val::list(inputs)], kwargs)?))
            }
        }
    }
    /// `graph.box(*bounds)`.
    #[track_caller]
    pub fn box_(&self, bounds: Vec<Val>) -> Result<Solid> {
        match self {
            AnyGraph::Native(graph) => graph.box_(bounds).map(Solid::Native),
            AnyGraph::Py(value) => Ok(Solid::from_val(&value.attr("box")?.call(bounds, vec![])?)),
        }
    }
    /// `graph.cylinder(axis, radius, a, b, lo, hi)`.
    #[track_caller]
    pub fn cylinder(&self, axis: i64, radius: &Val, a: &Val, b: &Val, lo: &Val, hi: &Val) -> Result<Solid> {
        match self {
            AnyGraph::Native(graph) => Ok(Solid::Native(graph.cylinder(axis, Num::of(radius)?, Num::of(a)?, Num::of(b)?, Num::of(lo)?, Num::of(hi)?)?)),
            AnyGraph::Py(value) => Ok(Solid::from_val(&value.attr("cylinder")?.call(
                vec![Val::Int(axis), radius.clone(), a.clone(), b.clone(), lo.clone(), hi.clone()], vec![])?)),
        }
    }
    /// `graph.prism(axis, lo, hi, section)`.
    #[track_caller]
    pub fn prism(&self, axis: i64, lo: &Val, hi: &Val, section: &Val) -> Result<Solid> {
        match self {
            AnyGraph::Native(graph) => graph.prism(axis, Num::of(lo)?, Num::of(hi)?, section).map(Solid::Native),
            AnyGraph::Py(value) => Ok(Solid::from_val(&value.attr("prism")?.call(
                vec![Val::Int(axis), lo.clone(), hi.clone(), section.clone()], vec![])?)),
        }
    }
    /// `graph.rounded(shape, radius)`.
    #[track_caller]
    pub fn rounded(&self, shape: &Solid, radius: &Val) -> Result<Solid> {
        match self {
            AnyGraph::Native(graph) => graph.rounded(shape, Num::of(radius)?),
            AnyGraph::Py(value) => Ok(Solid::from_val(&value.attr("rounded")?.call(vec![shape.to_val(), radius.clone()], vec![])?)),
        }
    }
    /// `graph.document(result, extras)` (`extras` empty: `None`).
    pub fn document(&self, result: &Solid, extras: &[(Val, Solid)]) -> Result<Val> {
        match self {
            AnyGraph::Native(graph) => graph.document(result, extras),
            AnyGraph::Py(value) => {
                let extras = if extras.is_empty() {
                    Val::None
                } else {
                    Val::dict(extras.iter().map(|(k, s)| (k.clone(), s.to_val())).collect())
                };
                value.attr("document")?.call(vec![result.to_val(), extras], vec![])
            }
        }
    }
}

impl py::Py for AnyGraph {
    fn to_py(&self) -> Result<Val> {
        Ok(self.to_val())
    }
    fn from_py(value: &Val) -> Result<Self> {
        Ok(AnyGraph::from_val(value))
    }
}

// ------------------------------------------------------------------------------------------
// Leaves: the recipe functions recorders install into the enclosure namespace

type LeafFn = Rc<dyn Fn(Args, Kwargs) -> Result<Solid>>;

/// A typed leaf as the Python-callable value a recorder installs. Generated callers get the
/// solid's Python form; [`call_leaf`] runs it typed while the `Leaf` lives.
pub struct Leaf {
    pub value: Val,
    key: usize,
}

impl Drop for Leaf {
    fn drop(&mut self) {
        let key = self.key;
        LEAVES.with(|leaves| leaves.borrow_mut().retain(|(k, _)| *k != key));
    }
}

fn function_key(value: &Val) -> Option<usize> {
    match value {
        Val::Func(f) => Some(Rc::as_ptr(f) as *const () as usize),
        _ => None,
    }
}

/// Make a leaf value from a typed function of Python arguments.
pub fn leaf(f: impl Fn(Args, Kwargs) -> Result<Solid> + 'static) -> Leaf {
    let typed: LeafFn = Rc::new(f);
    let call = typed.clone();
    let value = Val::function(move |args, kwargs| Ok(call(args, kwargs)?.to_val()));
    let key = function_key(&value).expect("a function value");
    LEAVES.with(|leaves| leaves.borrow_mut().push((key, typed)));
    Leaf { value, key }
}

/// `owner.<name>(*args, **kwargs)` read from the namespace at the call, as the enclosure calls
/// its geometry leaves: a typed leaf runs typed and gives its native shape unwrapped.
pub fn call_leaf(owner: &Val, name: &str, args: Args, kwargs: Kwargs) -> Result<Solid> {
    let value = owner.attr(name)?;
    if let Some(key) = function_key(&value) {
        let typed = LEAVES.with(|leaves| leaves.borrow().iter().find(|(k, _)| *k == key).map(|(_, f)| f.clone()));
        if let Some(typed) = typed {
            return typed(args, kwargs);
        }
    }
    Ok(Solid::from_val(&value.call(args, kwargs)?))
}

/// The cache `functools.cache` keeps for one function: results by the encoded arguments.
#[derive(Default)]
pub struct Memo(RefCell<VecDeque<(String, Solid)>>);

impl Memo {
    pub fn key(args: &Args, kwargs: &Kwargs) -> Result<String> {
        Ok(serde_json::to_string(&(
            Val::tuple(args.clone()).encode()?,
            Val::dict(kwargs.iter().map(|(k, v)| (Val::Str(k.clone()), v.clone())).collect()).encode()?,
        ))?)
    }
    pub fn get_or(&self, args: Args, kwargs: Kwargs, make: impl FnOnce(Args, Kwargs) -> Result<Solid>) -> Result<Solid> {
        let key = Self::key(&args, &kwargs)?;
        let hit = {
            let mut entries = self.0.borrow_mut();
            entries.iter().position(|(held, _)| *held == key).and_then(|i| entries.remove(i))
        };
        if let Some((key, value)) = hit {
            self.0.borrow_mut().push_back((key, value.clone()));
            return Ok(value);
        }
        let value = make(args, kwargs)?;
        self.0.borrow_mut().push_back((key, value.clone()));
        Ok(value)
    }
}

// ------------------------------------------------------------------------------------------
// The recorder

/// The geometry leaves `_record` replaces, in its order.
pub const RECORDED: [&str; 14] = [
    "_ybox", "_xcyl", "_ycyl", "_teardrop_y", "_zcyl", "_yz_prism", "_xz_prism", "_xy_prism",
    "_round_z", "_rounded_outer", "_handhold_cutter", "_handhold_finish_air", "disposal_letters",
    "_unified",
];

/// The replacements `_record` installs, in order, and the typed leaves among them.
struct Replacements {
    rows: Vec<(&'static str, Val)>,
    leaves: Vec<Leaf>,
}

impl Replacements {
    fn typed(&mut self, name: &'static str, made: Leaf) {
        self.rows.push((name, made.value.clone()));
        self.leaves.push(made);
    }
    fn value(&mut self, name: &'static str, value: Val) {
        self.rows.push((name, value));
    }
}

/// `_record(shell, graph, structure)` while it is entered: the enclosure's private geometry
/// leaves record into the graph until [`Recording::exit`] restores them.
pub struct Recording {
    shell: Val,
    originals: Vec<(&'static str, Val)>,
    leaves: RefCell<Vec<Leaf>>,
}

impl Recording {
    /// Substitute only the enclosure's private geometry leaves (`__enter__`).
    pub fn enter(rt: &Rt, shell: &Val, graph: &AnyGraph, structure: Solid) -> Result<Recording> {
        let artwork = {
            rt.import("_disposal_artwork")?;
            rt.member("_disposal_artwork", "numbers")?
        };
        let mut put = Replacements { rows: vec![], leaves: vec![] };
        match graph {
            AnyGraph::Native(g) => {
                let g = g.clone();
                put.typed("_ybox", leaf(move |args, _| Ok(Solid::Native(g.box_(args)?))));
            }
            AnyGraph::Py(value) => put.value("_ybox", value.attr("box")?),
        }
        for (name, axis) in [("_xcyl", 0), ("_ycyl", 1)] {
            let g = graph.clone();
            put.typed(name, leaf(move |args, kwargs| {
                let names: [&'static str; 5] = if axis == 0 { ["r", "y", "z", "x0", "x1"] } else { ["r", "x", "z", "y0", "y1"] };
                let v = bound_values(args, kwargs, &names)?;
                g.cylinder(axis, &v[0], &v[1], &v[2], &v[3], &v[4])
            }));
        }
        {
            let (g, shell) = (graph.clone(), shell.clone());
            put.typed("_teardrop_y", leaf(move |args, kwargs| {
                let mut b = py::bind(args, kwargs, &["radius", "x", "z", "y0", "y1", "up"], &[])?;
                let [radius, x, z, y0, y1] = ["radius", "x", "z", "y0", "y1"].map(|n| b.req(n));
                let up = b.opt("up").unwrap_or(Val::Float(1.));
                teardrop_y(&shell, &g, &radius?, &x?, &z?, &y0?, &y1?, &up)
            }));
        }
        {
            let g = graph.clone();
            put.typed("_zcyl", leaf(move |args, kwargs| {
                let v = bound_values(args, kwargs, &["r", "x", "y", "z0", "z1"])?;
                g.cylinder(2, &v[0], &v[1], &v[2], &v[3], &v[4])
            }));
        }
        for (name, axis, names) in [("_yz_prism", 0, ["x0", "x1", "section"]), ("_xz_prism", 1, ["y0", "y1", "section"]),
                                    ("_xy_prism", 2, ["z0", "z1", "section"])] {
            let g = graph.clone();
            put.typed(name, leaf(move |args, kwargs| {
                let v = bound_values(args, kwargs, &names)?;
                g.prism(axis, &v[0], &v[1], &v[2])
            }));
        }
        match graph {
            AnyGraph::Native(g) => {
                let g = g.clone();
                put.typed("_round_z", leaf(move |args, kwargs| {
                    let mut b = py::bind(args, kwargs, &["shape", "radius"], &[])?;
                    let shape = Solid::from_val(&b.req("shape")?);
                    g.rounded(&shape, Num::of(&b.req("radius")?)?)
                }));
            }
            AnyGraph::Py(value) => put.value("_round_z", value.attr("rounded")?),
        }
        put.typed("_rounded_outer", leaf(move |args, kwargs| {
            py::bind(args, kwargs, &["outer"], &[])?;
            Ok(structure.clone())
        }));
        {
            let (g, shell) = (graph.clone(), shell.clone());
            put.typed("_handhold_cutter", leaf(move |args, kwargs| {
                let v = bound_values(args, kwargs, &["inner", "x_ext", "sx"])?;
                handhold_cutter(&shell, &g, &v[0], &v[1], &v[2])
            }));
        }
        {
            let (g, shell) = (graph.clone(), shell.clone());
            let memo = Memo::default();
            let rt = rt.clone();
            put.typed("_handhold_finish_air", leaf(move |args, kwargs| {
                memo.get_or(args, kwargs, |args, kwargs| {
                    let v = bound_values(args, kwargs, &["inner"])?;
                    handhold_finish(&rt, &shell, &g, &v[0])
                })
            }));
        }
        {
            let (g, shell) = (graph.clone(), shell.clone());
            put.typed("disposal_letters", leaf(move |args, kwargs| {
                let v = bound_values(args, kwargs, &["outer"])?;
                disposal_letters(&shell, &g, &artwork, &v[0])
            }));
        }
        put.typed("_unified", leaf(|args, kwargs| {
            let v = bound_values(args, kwargs, &["shape"])?;
            Ok(Solid::from_val(&v[0]))
        }));
        let originals = RECORDED.iter().map(|name| Ok((*name, shell.attr(name)?))).collect::<Result<Vec<_>>>()?;
        let Replacements { rows, leaves } = put;
        let recording = Recording { shell: shell.clone(), originals, leaves: RefCell::new(leaves) };
        for (name, replacement) in rows {
            if let Err(error) = shell.setattr(name, replacement) {
                let _ = recording.exit();
                return Err(error);
            }
        }
        Ok(recording)
    }
    /// Restore the leaves in the order they were replaced (`__exit__`).
    pub fn exit(&self) -> Result<()> {
        for (name, original) in &self.originals {
            self.shell.setattr(name, original.clone())?;
        }
        self.leaves.borrow_mut().clear();
        Ok(())
    }
}

/// Run `body` with `_record(shell, graph, structure)` entered, as a `with` block: the leaves are
/// restored whatever `body` returns, and a failure to restore wins.
pub fn with_recording<T>(rt: &Rt, shell: &Val, graph: &AnyGraph, structure: Solid, body: impl FnOnce() -> Result<T>) -> Result<T> {
    let recording = Recording::enter(rt, shell, graph, structure)?;
    let result = body();
    recording.exit()?;
    result
}

/// `_record(shell, graph, structure)`: the context manager generated callers enter.
pub fn record(rt: &Rt, shell: &Val, graph: &Val, structure: &Val) -> Val {
    let held: Rc<RefCell<Option<Recording>>> = Rc::new(RefCell::new(None));
    let enter = {
        let (rt, shell, graph, structure, held) = (rt.clone(), shell.clone(), graph.clone(), structure.clone(), held.clone());
        Val::function(move |_, _| {
            let _frame = rt.frame(MODULE);
            let recording = Recording::enter(&rt, &shell, &AnyGraph::from_val(&graph), Solid::from_val(&structure))?;
            *held.borrow_mut() = Some(recording);
            Ok(Val::None)
        })
    };
    let exit = Val::function(move |_, _| {
        match held.borrow().as_ref() {
            Some(recording) => recording.exit()?,
            None => bail!("_enclosure_panel: unknown name originals"),
        }
        Ok(Val::None)
    });
    rt::context(enter, exit)
}

/// Positional-or-keyword arguments by name, all required.
fn bound_values(args: Args, kwargs: Kwargs, names: &[&'static str]) -> Result<Vec<Val>> {
    let mut b = py::bind(args, kwargs, names, &[])?;
    names.iter().map(|name| b.req(name)).collect()
}

fn n(value: &Val) -> Result<Num> {
    Num::of(value)
}

#[allow(clippy::too_many_arguments)]
fn teardrop_y(shell: &Val, graph: &AnyGraph, radius: &Val, x: &Val, z: &Val, y0: &Val, y1: &Val, up: &Val) -> Result<Solid> {
    let angle = super::num::radians(shell.attr("teardrop_roof_angle")?.num()?);
    let (r, xn, zn, upn) = (n(radius)?, n(x)?, n(z)?, n(up)?);
    let half = r.f() * super::num::sin(angle);
    let tangent = zn.f() + upn.mul(r).f() * super::num::cos(angle);
    let apex = zn.f() + upn.mul(r).f() / super::num::cos(angle);
    let quarter = upn.f() * std::f64::consts::PI / 2.;
    let bounds = Val::Tuple(vec![xn.sub(r).val(), xn.add(r).val(), y0.clone(), y1.clone(), zn.sub(r).val(), zn.add(r).val()]);
    let circle = graph.add("cylinder", vec![], bounds, vec![
        ("axis", Val::Int(1)),
        ("radius", radius.clone()),
        ("centre", Val::Tuple(vec![x.clone(), z.clone()])),
        ("span", Val::Tuple(vec![y0.clone(), y1.clone()])),
        ("stations", Val::Tuple(vec![Val::Float(quarter - angle), Val::Float(quarter + angle)])),
    ])?;
    let section = Val::Tuple(vec![
        Val::Tuple(vec![Val::Float(xn.f() - half), Val::Float(tangent)]),
        Val::Tuple(vec![Val::Float(xn.f() + half), Val::Float(tangent)]),
        Val::Tuple(vec![x.clone(), Val::Float(apex)]),
    ]);
    let roof = graph.prism(1, y0, y1, &section)?;
    circle.fuse(&[roof])
}

fn handhold_cutter(shell: &Val, graph: &AnyGraph, inner: &Val, x_ext: &Val, sx: &Val) -> Result<Solid> {
    let levels = py::unpack(&py::call(&shell.attr("_handhold_levels")?, vec![inner.clone()])?, 3)?;
    let y = py::unpack(&py::call(&shell.attr("_handhold_y")?, vec![])?, 2)?;
    let band = py::unpack(&py::call(&shell.attr("_band_x")?, vec![x_ext.clone(), sx.clone()])?, 2)?;
    let sx = n(sx)?;
    let inside = n(&band[1])?.sub(sx.mul(n(&shell.attr("handhold_wall")?)?));
    let [xa, xb] = sorted2(inside, n(x_ext)?.sub(sx));
    let bed = n(&levels[0])?.sub(Num::F(1.));
    let bounds = Val::Tuple(vec![xa.val(), xb.val(), y[0].clone(), y[1].clone(), bed.val(), levels[1].clone()]);
    graph.add("handhold-cutter", vec![], bounds.clone(), vec![
        ("box", bounds),
        ("radius", shell.attr("handhold_corner_r")?),
    ])
}

fn handhold_finish(rt: &Rt, shell: &Val, graph: &AnyGraph, inner: &Val) -> Result<Solid> {
    let levels = py::unpack(&py::call(&shell.attr("_handhold_levels")?, vec![inner.clone()])?, 3)?;
    let y = py::unpack(&py::call(&shell.attr("_handhold_y")?, vec![])?, 2)?;
    let depth = n(&shell.attr("wall")?)?.add(n(&shell.attr("y_stack_low_depth")?)?);
    let corner = shell.attr("handhold_corner_r")?;
    let edge = shell.attr("handhold_edge_r")?;
    let end = n(&corner)?.add(n(&edge)?).add(n(&shell.attr("handhold_wall")?)?);
    let cutter_depth = depth.sub(n(&shell.attr("handhold_wall")?)?);
    let slope = rt.import("_enclosure_structure")?.attr("OUTWARD_PER_HEIGHT")?;
    let bounds = Val::Tuple(vec![Val::Float(0.), depth.val(), n(&y[0])?.sub(end).val(), n(&y[1])?.add(end).val(),
        levels[0].clone(), levels[2].clone()]);
    graph.add("handhold-finish-air", vec![], bounds, vec![
        ("bed", levels[0].clone()),
        ("roof", levels[1].clone()),
        ("crown", levels[2].clone()),
        ("y", Val::list(vec![y[0].clone(), y[1].clone()])),
        ("depth", depth.val()),
        ("corner", corner),
        ("radius", edge),
        ("end_stock", end.val()),
        ("cutter_depth", cutter_depth.val()),
        ("slope", slope),
    ])
}

fn disposal_letters(shell: &Val, graph: &AnyGraph, artwork: &Val, outer: &Val) -> Result<Solid> {
    let lines = shell.attr("disposal_lines")?;
    let family = shell.attr("disposal_font")?;
    let drawn = py::call(artwork, vec![shell.attr("disposal_font")?, shell.attr("disposal_kind")?])?;
    let cap_height = shell.attr("disposal_cap_height")?;
    let embed = shell.attr("disposal_embed")?;
    let depth = n(&shell.attr("disposal_raise")?)?.add(n(&embed)?);
    graph.add("disposal-letters", vec![], Val::None, vec![
        ("outer", outer.clone()),
        ("lines", lines),
        ("family", family),
        ("artwork", drawn),
        ("cap_height", cap_height),
        ("depth", depth.val()),
        ("embed", shell.attr("disposal_embed")?),
        ("line_gap", shell.attr("disposal_line_gap")?),
        ("bottom", shell.attr("disposal_bottom")?),
    ])
}

// ------------------------------------------------------------------------------------------
// Python-object graphs and shapes (the stub classes' methods with `self` a Python instance)

fn py_boolean(me: &Val, op: &Val, others: &Val) -> Result<Val> {
    if let Some(shape) = Shape::from_val(me) {
        return Ok(shape.boolean(&op.str()?, &solids(others)?)?.to_val());
    }
    let op_name = op.str()?;
    let others = others.iter()?;
    let own_val = me.attr("bounds")?;
    let own = Bounds::from_val(&own_val)?;
    let mut nodes: Vec<(Val, Option<Option<Bounds>>)> = vec![(me.clone(), Some(own))];
    for other in others {
        if op_name == "cut" && own.is_some() {
            let bounds = Bounds::from_val(&other.attr("bounds")?)?;
            if bounds.is_some_and(|b| !own.unwrap().overlaps(&b)) {
                continue;
            }
            nodes.push((other, Some(bounds)));
        } else {
            nodes.push((other, None));
        }
    }
    if nodes.len() == 1 {
        return Ok(me.clone());
    }
    let combine = op_name == "union" || op_name == "intersect";
    let mut known = vec![];
    if combine {
        for (node, bounds) in &nodes {
            known.push((Val::None, match bounds {
                Some(b) => *b,
                None => Bounds::from_val(&node.attr("bounds")?)?,
            }));
        }
    }
    let all = known.iter().all(|(_, b)| b.is_some());
    let bounds = match op_name.as_str() {
        "union" if all => combined(&known, false)?.to_val(),
        "union" => Val::None,
        "intersect" if all => combined(&known, true)?.to_val(),
        _ => own_val,
    };
    let indices = nodes.iter().map(|(node, _)| node.attr("index")).collect::<Result<Vec<_>>>()?;
    me.attr("graph")?.attr("add")?.call(vec![op.clone(), Val::list(indices)], vec![("bounds".into(), bounds)])
}

/// `self.graph.add(op, [self.index], bounds=bounds, **numbers)` of a Python shape.
fn py_graph_add(me: &Val, op: &str, bounds: Val, numbers: Vec<(&str, Val)>) -> Result<Val> {
    let index = me.attr("index")?;
    let mut kwargs: Kwargs = numbers.into_iter().map(|(k, v)| (k.to_owned(), v)).collect();
    kwargs.push(("bounds".into(), bounds));
    me.attr("graph")?.attr("add")?.call(vec![py::s(op), Val::list(vec![index])], kwargs)
}

/// `_Shape.translate(self, delta)` for a Python shape.
pub fn py_translate(me: &Val, delta: &Val) -> Result<Val> {
    if let Some(shape) = Shape::from_val(me) {
        return Ok(shape.translate(delta)?.to_val());
    }
    let bounds = match Bounds::from_val(&me.attr("bounds")?)? {
        Some(b) => translated(&b, delta)?.to_val(),
        None => Val::None,
    };
    py_graph_add(me, "translate", bounds, vec![("delta", delta.clone())])
}

fn py_rotate(me: &Val, origin: &Val, end: &Val, angle: &Val) -> Result<Val> {
    if let Some(shape) = Shape::from_val(me) {
        return Ok(shape.rotate(origin, end, angle)?.to_val());
    }
    let bounds = rotated(Bounds::from_val(&me.attr("bounds")?)?, origin, end, angle)?;
    py_graph_add(me, "rotate", bounds.map_or(Val::None, |b| b.to_val()),
        vec![("origin", origin.clone()), ("end", end.clone()), ("angle", angle.clone())])
}

fn py_mirror(me: &Val, plane: &Val) -> Result<Val> {
    if let Some(shape) = Shape::from_val(me) {
        return Ok(shape.mirror(plane)?.to_val());
    }
    let axis = mirror_axis(plane)?;
    let bounds = Bounds::from_val(&me.attr("bounds")?)?.map(|b| mirrored(&b, axis));
    py_graph_add(me, "mirror", bounds.map_or(Val::None, |b| b.to_val()), vec![("axis", Val::Int(axis as i64))])
}

/// `_Graph.add(self, op, inputs, bounds=bounds, **numbers)` for a Python graph: the node is
/// appended to the object's list and its shape is a `shape_class` instance.
pub fn py_add(rt: &Rt, me: &Val, op: Val, inputs: &Val, bounds: Val, numbers: Kwargs, shape_class: Option<&Val>) -> Result<Val> {
    let nodes = me.attr("nodes")?;
    let index = Val::Int(nodes.len()? as i64);
    let node = Val::dict(vec![(py::s("op"), op), (py::s("inputs"), Val::list(inputs.iter()?)), (py::s("source"), rt::site())]);
    for (key, value) in numbers {
        node.set(Val::Str(key), value)?;
    }
    py::method(&nodes, "append", vec![node])?;
    let class = match shape_class {
        Some(class) => class.clone(),
        None => state(rt)?.shape_class.clone(),
    };
    class.call(vec![me.clone(), index, bounds], vec![])
}

fn py_box(me: &Val, bounds: Vec<Val>) -> Result<Val> {
    let values = Val::Tuple(bounds);
    me.attr("add")?.call(vec![py::s("box")], vec![("bounds".into(), values.clone()), ("box".into(), values)])
}

fn py_cylinder(me: &Val, v: &[Val]) -> Result<Val> {
    let (bounds, span) = cylinder_bounds(v[0].integer()?, n(&v[1])?, n(&v[2])?, n(&v[3])?, n(&v[4])?, n(&v[5])?)?;
    me.attr("add")?.call(vec![py::s("cylinder")], vec![
        ("axis".into(), v[0].clone()),
        ("radius".into(), v[1].clone()),
        ("centre".into(), Val::Tuple(vec![v[2].clone(), v[3].clone()])),
        ("span".into(), Val::list(vec![span[0].val(), span[1].val()])),
        ("bounds".into(), bounds.to_val()),
    ])
}

fn py_prism(me: &Val, v: &[Val]) -> Result<Val> {
    let section = Val::Tuple(v[3].iter()?);
    let (lo, hi) = (n(&v[1])?, n(&v[2])?);
    let bounds = prism_bounds(v[0].integer()?, lo, hi, &section)?;
    let span = sorted2(lo, hi);
    me.attr("add")?.call(vec![py::s("prism")], vec![
        ("axis".into(), v[0].clone()),
        ("span".into(), Val::list(vec![span[0].val(), span[1].val()])),
        ("section".into(), section),
        ("bounds".into(), bounds.to_val()),
    ])
}

fn py_rounded(me: &Val, shape: &Val, radius: &Val) -> Result<Val> {
    if interop::compare("le", radius.clone(), Val::Int(0))?.truthy()? {
        return Ok(shape.clone());
    }
    let op = me.attr("nodes")?.get(shape.attr("index")?)?.get(py::s("op"))?;
    if interop::compare("ne", op, py::s("box"))?.truthy()? {
        bail!("the enclosure standing round belongs to rectangular stock");
    }
    let bounds = shape.attr("bounds")?;
    me.attr("add")?.call(vec![py::s("rounded-box")], vec![
        ("box".into(), bounds.clone()),
        ("radius".into(), radius.clone()),
        ("bounds".into(), bounds),
    ])
}

fn py_document(me: &Val, result: &Val, extras: &Val) -> Result<Val> {
    let rows = py::snapshot(&me.attr("nodes")?)?.iter()?;
    let result = result.attr("index")?.integer()? as usize;
    let extras = extras_of(extras)?.into_iter().map(|(key, shape)| Ok((key, shape.index()?))).collect::<Result<Vec<_>>>()?;
    document_rows(&rows, result, &extras)
}

// ------------------------------------------------------------------------------------------
// The module

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("contextmanager", rt.member("contextlib", "contextmanager")?)?;
    ns.set("cache", rt.member("functools", "cache")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("sys", rt.import("sys")?)?;
    ns.set("_enclosure_structure", rt.import("_enclosure_structure")?)?;

    ns.def(rt, "_Shape.__init__", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "graph", "index", "bounds"], &[])?;
        let me = b.req("self")?;
        let (graph, index) = (b.req("graph")?, b.req("index")?);
        let bounds = b.opt("bounds").unwrap_or(Val::None);
        me.setattr("graph", graph)?;
        me.setattr("index", index)?;
        me.setattr("bounds", bounds)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_Shape._boolean", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "op", "others"], &[])?;
        py_boolean(&b.req("self")?, &b.req("op")?, &b.req("others")?)
    })?;
    for (name, op) in [("_Shape.fuse", "union"), ("_Shape.cut", "cut"), ("_Shape.intersect", "intersect")] {
        ns.def(rt, name, move |_rt, args, _kwargs| {
            let (me, others) = args.split_first().context("missing argument self")?;
            py_boolean(me, &py::s(op), &Val::Tuple(others.to_vec()))
        })?;
    }
    ns.def(rt, "_Shape.translate", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "delta"], &[])?;
        py_translate(&b.req("self")?, &b.req("delta")?)
    })?;
    ns.def(rt, "_Shape.rotate", |_rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "origin", "end", "angle"])?;
        py_rotate(&v[0], &v[1], &v[2], &v[3])
    })?;
    ns.def(rt, "_Shape.mirror", |_rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "plane"])?;
        py_mirror(&v[0], &v[1])
    })?;
    for name in ["_Shape.clean", "_Shape.val"] {
        ns.def(rt, name, |_rt, args, kwargs| Ok(bound_values(args, kwargs, &["self"])?.remove(0)))?;
    }
    ns.def(rt, "_Shape.BoundingBox", |rt, args, kwargs| {
        let me = bound_values(args, kwargs, &["self"])?.remove(0);
        if let Some(shape) = Shape::from_val(&me) {
            return shape.bounding_box();
        }
        bounding_namespace(rt, &me.attr("bounds")?)
    })?;
    ns.def(rt, "_Shape.Solids", |_rt, args, kwargs| {
        let me = bound_values(args, kwargs, &["self"])?.remove(0);
        Ok(Val::list(vec![me]))
    })?;
    let shape_class = rt.python_type(MODULE, "_Shape")?;
    ns.set("_Shape", shape_class.clone())?;
    rt.keep(MODULE, State { shape_class, simple_namespace: RefCell::new(None) });

    ns.def(rt, "_Graph.__init__", |_rt, args, kwargs| {
        let me = bound_values(args, kwargs, &["self"])?.remove(0);
        if Graph::from_val(&me).is_none() {
            me.setattr("nodes", Val::list(vec![]))?;
        }
        Ok(Val::None)
    })?;
    ns.def(rt, "_Graph.add", |rt, args, kwargs| {
        let (me, op, inputs, bounds, numbers) = bind_add(args, kwargs, true)?;
        let me = me.context("missing argument self")?;
        if let Some(graph) = Graph::from_val(&me) {
            return Ok(graph.add_val(op, &inputs, &bounds, numbers)?.to_val());
        }
        py_add(rt, &me, op, &inputs, bounds, numbers, None)
    })?;
    ns.def(rt, "_Graph.box", |_rt, args, _kwargs| {
        let (me, bounds) = args.split_first().context("missing argument self")?;
        if let Some(graph) = Graph::from_val(me) {
            return Ok(graph.box_(bounds.to_vec())?.to_val());
        }
        py_box(me, bounds.to_vec())
    })?;
    ns.def(rt, "_Graph.cylinder", |_rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "axis", "radius", "a", "b", "lo", "hi"])?;
        if let Some(graph) = Graph::from_val(&v[0]) {
            return Ok(AnyGraph::Native(graph).cylinder(v[1].integer()?, &v[2], &v[3], &v[4], &v[5], &v[6])?.to_val());
        }
        py_cylinder(&v[0], &v[1..])
    })?;
    ns.def(rt, "_Graph.prism", |_rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "axis", "lo", "hi", "section"])?;
        if let Some(graph) = Graph::from_val(&v[0]) {
            return Ok(AnyGraph::Native(graph).prism(v[1].integer()?, &v[2], &v[3], &v[4])?.to_val());
        }
        py_prism(&v[0], &v[1..])
    })?;
    ns.def(rt, "_Graph.rounded", |_rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "shape", "radius"])?;
        if let Some(graph) = Graph::from_val(&v[0]) {
            return Ok(graph.rounded(&Solid::from_val(&v[1]), n(&v[2])?)?.to_val());
        }
        py_rounded(&v[0], &v[1], &v[2])
    })?;
    ns.def(rt, "_Graph.document", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "result", "extras"], &[])?;
        let me = b.req("self")?;
        let result = b.req("result")?;
        let extras = b.opt("extras").unwrap_or(Val::None);
        if let Some(graph) = Graph::from_val(&me) {
            return graph.document(&Solid::from_val(&result), &extras_of(&extras)?);
        }
        py_document(&me, &result, &extras)
    })?;
    ns.set("_Graph", rt.python_type(MODULE, "_Graph")?)?;

    ns.def(rt, "_record", |rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["shell", "graph", "structure"])?;
        Ok(record(rt, &v[0], &v[1], &v[2]))
    })?;
    ns.def(rt, "numbers", |rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["shell", "box"])?;
        numbers(rt, &v[0], &v[1])
    })?;
    ns.def(rt, "print_numbers", |rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["shell", "box"])?;
        print_numbers(rt, &v[0], &v[1])
    })?;
    ns.def(rt, "cut", |rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["shell", "box", "directory"])?;
        cut(rt, &v[0], &v[1], &v[2])
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

fn at(value: &Val, index: i64) -> Result<Val> {
    value.get(Val::Int(index))
}

fn le(a: &Val, b: &Val) -> Result<bool> {
    interop::compare("le", a.clone(), b.clone())?.truthy()
}

/// Record the complete current back-bottom construction, with its live seam numbers.
pub fn numbers(rt: &Rt, shell: &Val, boxv: &Val) -> Result<Val> {
    let graph = Graph::new();
    let outer = boxv.attr("outer")?;
    let structure_numbers = super::_enclosure_structure::numbers(rt, &outer)?;
    let structure = graph.add("silhouette", &[], Bounds::from_val(&outer)?, vec![]);
    let any = AnyGraph::Native(graph.clone());
    let result = with_recording(rt, shell, &any, Solid::Native(structure.clone()), || {
        // The lower half starts below the display/funnel storeys. Refuse a new
        // overlap until that additional feature has an explicit Rust construction.
        let top = at(&boxv.attr("splits")?, 1)?;
        let foot = at(&structure_numbers.get(py::s("profile"))?.get(py::s("foot"))?, 1)?;
        if le(&foot, &top)? {
            bail!("the display keepout reaches the structural back-bottom boundary");
        }
        let y_joint = boxv.attr("y_joint")?;
        let back = py::call(&shell.attr("housing_back_y")?, vec![outer.clone()])?;
        if interop::compare("ge", back, y_joint.clone())?.truthy()? {
            bail!("the display keepout reaches the back column");
        }
        let pack = boxv.attr("pack")?;
        if pack.attr("funnel")?.truthy()? {
            let seat = n(&py::call(&shell.attr("funnel_seat_z")?, vec![outer.clone()])?)?;
            let lower = seat.sub(n(&shell.attr("_funnel")?.attr("drop")?)?)
                .sub(n(&shell.attr("_funnel_frame_part")?.attr("web")?)?)
                .sub(n(&shell.attr("funnel_collar_air")?)?)
                .sub(Num::F(1.));
            if lower.f() <= n(&top)?.f() {
                bail!("the funnel clearance reaches the structural back-bottom boundary");
            }
        }
        let o = &outer;
        let inner = boxv.attr("inner")?;
        let cavity = Solid::from_val(&py::call(&shell.attr("_cavity")?, vec![inner.clone()])?);
        let stock = graph.box_(vec![at(o, 0)?, at(o, 1)?, y_joint.clone(), at(o, 3)?, at(o, 4)?, top.clone()])?;
        let mut half = structure.cut(&[cavity])?.intersect(&[Solid::Native(stock)])?;
        let tongue = at(&py::call(&shell.attr("_floor_tongue")?, vec![inner.clone(), y_joint.clone()])?, 1)?;
        half = half.cut(&[Solid::from_val(&tongue)])?;
        let pairs = [
            (pack.attr("back_ports")?, shell.attr("_port_cuts")?),
            (pack.attr("west_ports")?, shell.attr("_x_port_cuts")?),
        ];
        for (ports, cutter) in pairs {
            let mut selected = vec![];
            for p in ports.iter()? {
                if le(&at(&p, 2)?, &top)? {
                    selected.push(p);
                }
            }
            // The generated runtime's `is` never holds between two functions.
            let cuts = if interop::compare("is", cutter.clone(), shell.attr("_port_cuts")?)?.truthy()? {
                py::call(&cutter, vec![Val::list(selected), interop::binary("sub", at(&inner, 3)?, Val::Float(5.))?,
                    interop::binary("add", at(o, 3)?, Val::Float(5.))?])?
            } else {
                py::call(&cutter, vec![Val::list(selected), interop::binary("sub", at(o, 0)?, Val::Float(5.))?,
                    interop::binary("add", at(&inner, 0)?, Val::Float(5.))?])?
            };
            for air in cuts.iter()? {
                half = half.cut(&[Solid::from_val(&air)])?;
            }
        }
        let halves = py::dict([("back", half.to_val())]);
        let built = py::call_kw(&shell.attr("build_piece")?, vec![boxv.clone(), py::s("back"), py::s("bottom")],
            vec![("halves_cache", halves)])?;
        Ok(Solid::from_val(&built))
    })?;
    let linear = rt.member("_materials", "linear")?;
    let color = py::call(&linear, vec![shell.attr("PIECE_COLORS")?.get(py::s("back-bottom"))?])?;
    let panel = graph.document(&result, &[])?;
    let out = Val::dict(interop::entries_of(&structure_numbers)?);
    out.set(py::s("color"), color)?;
    out.set(py::s("panel"), panel)?;
    Ok(out)
}

/// The complete back-bottom print recipe, including the exterior field's live phase.
///
/// Other rear plain lands are above this panel. Read their exact pure bounds and
/// a conservative bound on the receiver pad before excluding them from its rail.
/// The warning land is calculated in Rust from the raked glyphs it actually built.
pub fn print_numbers(rt: &Rt, shell: &Val, boxv: &Val) -> Result<Val> {
    rt.import("_enclosure_skin")?;
    let above = shell.attr("_above_core_shell")?;
    let identification = py::method(&above, "rear_identification", vec![])?;
    let station = py::method(&identification, "nameplate_station", vec![])?;
    let wing = identification.attr("nameplate")?.attr("wing_interface")?;
    let plan = py::method(&identification, "nameplate_plan", vec![])?;
    // apply()'s pad extends ph/2 plus its end or run-out margin. Use the larger
    // margin for either print direction; cuts cannot enlarge this bound.
    let floor_stock = n(&wing.attr("FLOOR_STOCK")?)?;
    let runout = Num::F(2.).max(floor_stock.add(n(&wing.attr("RUNOUT_LEAD")?)?));
    let end_margin = n(&shell.attr("wall")?)?.add(n(&shell.attr("fits")?.attr("supported_surface")?)?);
    let pad_floor = n(&station.attr("z")?)?.sub(n(&wing.attr("HEIGHT")?)?.div(Num::I(2)))
        .sub(n(&wing.attr("FACE_SLIP")?)?).sub(runout.max(end_margin));
    let face_y = plan.get(py::s("face_y_mm"))?;
    let mut other = py::method(&identification, "rail_bounds", vec![])?.iter()?;
    other.extend(py::method(&wing, "plain_lips", vec![station.clone(), face_y.clone()])?.iter()?);
    other.push(py::method(&shell.attr("_above_core_shell")?, "keystone_land", vec![])?);
    let pack = boxv.attr("pack")?;
    let back_wall = at(&boxv.attr("outer")?, 3)?;
    let nameplate = pack.attr("nameplate")?;
    if nameplate.truthy()? {
        other.extend(py::method(&shell.attr("_nameplate_fit")?, "plain_lips", vec![nameplate, back_wall.clone()])?.iter()?);
    }
    let keystone = pack.attr("keystone")?;
    if keystone.truthy()? {
        other.extend(py::method(&shell.attr("_data_fit")?, "plain_lips", vec![keystone, back_wall])?.iter()?);
    }
    // The tall seam heads occupy the flank runs. Rear-wall features behind
    // their complete Y extent meet the wall's seam, rather than those heads.
    let inner = boxv.attr("inner")?;
    let runs = py::call(&shell.attr("_z_rail_runs")?, vec![inner.clone(), boxv.attr("y_joint")?, py::s("back"),
        pack.attr("collet_plate")?])?;
    let rail_end_y = most(runs.iter()?.iter().map(|run| Ok(n(&at(run, 2)?)?.max(n(&at(run, 3)?)?)))
        .collect::<Result<Vec<_>>>()?)?;
    let pad_y = n(&face_y)?.sub(n(&wing.attr("THICK")?)?).sub(n(&wing.attr("BACK_AIR")?)?).sub(floor_stock);
    let lands = |k: i64| -> Result<Vec<Num>> { other.iter().map(|land| n(&at(land, k)?)).collect() };
    let behind_rails = least(std::iter::once(pad_y).chain(lands(2)?))?.f() > rail_end_y.f();
    let rise = if behind_rails { Num::I(0) } else { n(&shell.attr("z_rise")?)? };
    let lowered = n(&at(&boxv.attr("splits")?, 1)?)?.add(rise);
    let crown = n(&at(&py::call(&shell.attr("_handhold_levels")?, vec![inner])?, 2)?)?;
    let panel_top = lowered.max(crown);
    if least(std::iter::once(pad_floor).chain(lands(4)?))?.f() <= panel_top.f() {
        bail!("a rear plain land reaches the back-bottom print boundary");
    }
    let outer = boxv.attr("outer")?;
    let at_station = {
        let (shell, outer) = (shell.clone(), outer.clone());
        Val::function(move |args, kwargs| {
            let s = bound_values(args, kwargs, &["s"])?.remove(0);
            py::call(&shell.attr("plan_at")?, vec![s, outer.clone()])
        })
    };
    let length = py::call(&shell.attr("plan_perimeter")?, vec![outer.clone()])?;
    let rail = py::call_kw(&shell.attr("_flute_skin")?.attr("Rail")?, vec![], vec![("at", at_station), ("length", length)])?;
    let out = numbers(rt, shell, boxv)?;
    let pitch = py::call(&shell.attr("flute_pitch")?, vec![outer])?;
    let field = super::_enclosure_skin::field_numbers(rt, &Val::list(vec![rail]), pitch, shell.attr("flute_depth")?,
        shell.attr("flute_rise")?)?;
    py::method(&out, "update", vec![field])?;
    out.set(py::s("print"), py::dict([
        ("warning_margin", shell.attr("disposal_margin")?),
        ("warning_raise", shell.attr("disposal_raise")?),
        ("wall", shell.attr("wall")?),
    ]))?;
    out.set(py::s("disjoint_lands"), py::dict([
        ("panel_top", panel_top.val()),
        ("receiver_pad_floor", pad_floor.val()),
        ("other_bounds", Val::list(other)),
    ]))?;
    Ok(out)
}

/// Write one native-free back-bottom part through the installed engine and print payload.
pub fn cut(rt: &Rt, shell: &Val, boxv: &Val, directory: &Val) -> Result<Val> {
    let rust_part = rt.import("_rust_part")?;
    rt.import("_enclosure_presentation")?;
    let cut = rust_part.attr("cut")?;
    let numbers = print_numbers(rt, shell, boxv)?;
    let said = py::call(&cut, vec![py::s("enclosure-shell"), py::s("enclosure-panel"), numbers, directory.clone()])?;
    let step = PathBuf::from(directory.str()?).join("enclosure-back-bottom.step");
    super::_enclosure_presentation::print_payload(rt, &step, Val::Bool(true))?;
    Ok(said)
}
