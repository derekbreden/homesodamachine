//! Enclosure fit/readings on fine model references, without Python CAD objects.
//!
//! The enclosure's scalar station functions supply numeric tool recipes. Rust owns
//! their geometry and all model, volume, face and connected-component readings. The
//! existing report functions consume those readings, keeping their labels, units,
//! limits and document variables in one place with the mechanical dimensions.
//!
//! # Questions for typed modules
//!
//! A questions graph is a [`Graph`] made by [`Graph::questions`]: `Graph::questions(Val::None)`
//! collects questions, `Graph::questions(measure(rt, &graph)?)` answers them. Its shapes are
//! reading shapes ([`Shape::is_reading`]); [`Solid::volume`], [`Solid::bounding_box`],
//! [`Solid::solids`], [`Solid::is_valid`] and [`Solid::faces`] ask the graph about them, as
//! `_ReadingShape` does, through [`reading_volume`], [`reading_bounding_box`], [`reading_solids`],
//! [`reading_is_valid`] and [`reading_faces`]. A face or component reading is a Python object
//! (`_ScalarFace`, `_ScalarComponent`), a bounding box a `SimpleNamespace` ([`bounds_namespace`]),
//! a vector a `_Vector` ([`vector`]), exactly as generated code receives them.
//!
//! - [`Numeric::enter`] / [`Numeric::exit`] (or [`with_numeric`]) is `_numeric(shell, graph, box)`:
//!   `shell.cq` becomes the numeric vector namespace and `_record` (with the back-top leaves when
//!   a box is given) records the enclosure's geometry leaves into the graph; [`numeric`] is the
//!   context manager generated callers `with`.
//! - [`measure`] is `_measure(graph)`: the answers of one `enclosure-checks` run.
//! - [`reading`] is `graph.reading(shape, **kwargs)` for a native or a Python graph, [`model`]
//!   `graph.model(value)`.
//! - [`check_pieces`], [`box_readings`], [`piece_reports`] and [`check_rows`] are the module's
//!   functions with Python values in and out.
//!
//! Machine-data makes `_Questions()` as a Python object: every `"Class.method"` entry here takes a
//! Python `self` as well as a native one, and [`AnyGraph`] carries either.
use super::_enclosure_panel::{self as panel, AnyGraph, Graph, Recording, Shape, Solid};
use super::py::{self, Args, Kwargs, Val};
use super::rt::{self, Ns, Rt};
use anyhow::{Context, Result, bail};
use hsm_documents::interop;
use std::cell::RefCell;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_rust_enclosure_checks";

pub struct State {
    vector: Val,
    scalar_face: Val,
    scalar_component: Val,
    reading_shape: Val,
    redirect_stdout: Val,
    io: Val,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

fn s(text: &str) -> Val {
    py::s(text)
}

fn is_none(value: &Val) -> bool {
    matches!(value, Val::None)
}

/// Positional-or-keyword arguments by name, all required.
fn bound_values(args: Args, kwargs: Kwargs, names: &[&'static str]) -> Result<Vec<Val>> {
    let mut b = py::bind(args, kwargs, names, &[])?;
    names.iter().map(|name| b.req(name)).collect()
}

fn first_rest(args: &Args) -> Result<(&Val, &[Val])> {
    args.split_first().context("missing argument self")
}

// ------------------------------------------------------------------------------------------
// Vectors and scalar readings (Python objects; their methods take a Python `self`)

/// `_Vector(*coordinates)`.
pub fn vector(rt: &Rt, coordinates: Vec<Val>) -> Result<Val> {
    state(rt)?.vector.call(coordinates, vec![])
}

fn vector_combine(rt: &Rt, me: &Val, other: &Val, op: &str) -> Result<Val> {
    let values = me.iter()?.into_iter().zip(other.iter()?)
        .map(|(a, b)| interop::binary(op, a, b))
        .collect::<Result<Vec<_>>>()?;
    vector(rt, values)
}

/// `sum(a*b for a, b in zip(me, other))`.
fn vector_dot(me: &Val, other: &Val) -> Result<Val> {
    let mut total = Val::Int(0);
    for (a, b) in me.iter()?.into_iter().zip(other.iter()?) {
        total = interop::binary("add", total, interop::binary("mul", a, b)?)?;
    }
    Ok(total)
}

/// `_bounds(lower, upper)`: `SimpleNamespace(xmin=.., xmax=.., ..., zlen=.., center=_Vector(..))`
/// of two corners, either of which may be `None` (the origin).
pub fn bounds_namespace(rt: &Rt, lower: &Val, upper: &Val) -> Result<Val> {
    let origin = || Val::Tuple(vec![Val::Float(0.); 3]);
    let lower = if lower.truthy()? { lower.clone() } else { origin() };
    let upper = if upper.truthy()? { upper.clone() } else { origin() };
    let mut row: Kwargs = vec![];
    for (k, axis) in ["x", "y", "z"].iter().enumerate() {
        row.push((format!("{axis}min"), lower.get(Val::Int(k as i64))?));
        row.push((format!("{axis}max"), upper.get(Val::Int(k as i64))?));
    }
    for (k, axis) in ["x", "y", "z"].iter().enumerate() {
        let span = interop::binary("sub", upper.get(Val::Int(k as i64))?, lower.get(Val::Int(k as i64))?)?;
        row.push((format!("{axis}len"), span));
    }
    let centre = lower.iter()?.into_iter().zip(upper.iter()?)
        .map(|(a, b)| interop::binary("truediv", interop::binary("add", a, b)?, Val::Int(2)))
        .collect::<Result<Vec<_>>>()?;
    row.push(("center".into(), vector(rt, centre)?));
    panel::simple_namespace(rt)?.call(vec![], row)
}

// ------------------------------------------------------------------------------------------
// Reading shapes

/// `shape.graph.reading(shape, **kwargs)`.
fn shape_reading(me: &Solid, kwargs: Vec<(&str, Val)>) -> Result<Val> {
    match me {
        Solid::Native(shape) => reading(&AnyGraph::Native(shape.graph().clone()), me, kwargs),
        Solid::Py(value) => py::call_kw(&value.attr("graph")?.attr("reading")?, vec![value.clone()], kwargs),
    }
}

fn graph_of(me: &Solid) -> Result<AnyGraph> {
    Ok(match me {
        Solid::Native(shape) => AnyGraph::Native(shape.graph().clone()),
        Solid::Py(value) => AnyGraph::Py(value.attr("graph")?),
    })
}

fn every_other(bounds: &Val, start: Option<i64>) -> Result<Val> {
    bounds.get(Val::Slice { start, stop: None, step: 2 })
}

fn volume_of(me: &Solid) -> Result<Val> {
    shape_reading(me, vec![])?.get(s("volume_mm3"))
}

fn bounding_box_of(rt: &Rt, me: &Solid) -> Result<Val> {
    let graph = graph_of(me)?;
    let field = py::method(&graph.attr("extras")?, "get", vec![s("receiver_field")])?;
    if me.same(&Solid::from_val(&field))? && !is_none(&me.bounds_val()?) {
        // This box only sizes the exterior clip around the receiver tool. Its
        // conservative construction extents enclose that tool in either phase.
        let bounds = me.bounds_val()?;
        return bounds_namespace(rt, &every_other(&bounds, None)?, &every_other(&bounds, Some(1))?);
    }
    let row = shape_reading(me, vec![])?;
    if is_none(&graph.attr("answers")?) && !is_none(&me.bounds_val()?) {
        let bounds = me.bounds_val()?;
        return bounds_namespace(rt, &every_other(&bounds, None)?, &every_other(&bounds, Some(1))?);
    }
    bounds_namespace(rt, &row.get(s("min"))?, &row.get(s("max"))?)
}

fn solids_of(rt: &Rt, me: &Solid) -> Result<Val> {
    let row = shape_reading(me, vec![("components", Val::Bool(true)), ("valid", Val::Bool(true))])?;
    let class = state(rt)?.scalar_component.clone();
    let parts = py::method(&row, "get", vec![s("components"), Val::Tuple(vec![])])?.iter()?;
    Ok(Val::list(parts.into_iter().map(|part| class.call(vec![part], vec![])).collect::<Result<_>>()?))
}

fn is_valid_of(me: &Solid) -> Result<Val> {
    let row = shape_reading(me, vec![("valid", Val::Bool(true))])?;
    py::method(&row, "get", vec![s("valid"), Val::Bool(true)])
}

fn faces_of(rt: &Rt, me: &Solid) -> Result<Val> {
    let rows = shape_reading(me, vec![("kind", s("faces"))])?;
    let class = state(rt)?.scalar_face.clone();
    Ok(Val::list(rows.iter()?.into_iter().map(|row| class.call(vec![row], vec![])).collect::<Result<_>>()?))
}

/// `_ReadingShape.Volume()` of a native reading shape.
pub fn reading_volume(shape: &Shape) -> Result<Val> {
    volume_of(&Solid::Native(shape.clone()))
}
/// `_ReadingShape.BoundingBox()`: the receiver field's construction box, the construction box
/// while questions are collected, else the measured box.
pub fn reading_bounding_box(shape: &Shape) -> Result<Val> {
    bounding_box_of(&rt::current()?, &Solid::Native(shape.clone()))
}
/// `_ReadingShape.Solids()`: the measured components (`_ScalarComponent` objects).
pub fn reading_solids(shape: &Shape) -> Result<Val> {
    solids_of(&rt::current()?, &Solid::Native(shape.clone()))
}
/// `_ReadingShape.isValid()`.
pub fn reading_is_valid(shape: &Shape) -> Result<Val> {
    is_valid_of(&Solid::Native(shape.clone()))
}
/// `_ReadingShape.Faces()`: the measured faces (`_ScalarFace` objects).
pub fn reading_faces(shape: &Shape) -> Result<Val> {
    faces_of(&rt::current()?, &Solid::Native(shape.clone()))
}

// ------------------------------------------------------------------------------------------
// Questions graphs

/// `graph.reading(shape, **kwargs)` (`kind`, `components`, `valid`) for a native or a Python graph.
pub fn reading(graph: &AnyGraph, shape: &Solid, kwargs: Vec<(&str, Val)>) -> Result<Val> {
    match graph {
        AnyGraph::Native(g) => {
            let (mut kind, mut components, mut valid) = ("stats".to_owned(), false, false);
            for (key, value) in &kwargs {
                match *key {
                    "kind" => kind = value.str()?,
                    "components" => components = value.truthy()?,
                    "valid" => valid = value.truthy()?,
                    other => bail!("reading() got an unexpected keyword argument '{other}'"),
                }
            }
            g.reading(shape, &kind, components, valid)
        }
        AnyGraph::Py(value) => py::call_kw(&value.attr("reading")?, vec![shape.to_val()], kwargs),
    }
}

/// `graph.model(value)` for a native or a Python graph.
pub fn model(graph: &AnyGraph, value: &Val) -> Result<Solid> {
    match graph {
        AnyGraph::Native(g) => g.model(value),
        AnyGraph::Py(object) => Ok(Solid::from_val(&py::method(object, "model", vec![value.clone()])?)),
    }
}

/// `_Questions.add` with a Python `self`.
fn py_add(rt: &Rt, me: &Val, op: Val, inputs: &Val, bounds: Val, numbers: Kwargs) -> Result<Val> {
    let bounds = if interop::eq(&op, &s("empty"))? { Val::Tuple(vec![Val::Float(0.); 6]) } else { bounds };
    let class = state(rt)?.reading_shape.clone();
    panel::py_add(rt, me, op, inputs, bounds, numbers, Some(&class))
}

/// `_Questions.model` with a Python `self`.
fn py_model(rt: &Rt, me: &Val, value: &Val) -> Result<Val> {
    if panel::is_instance(value, &["list", "tuple"])? {
        let parts = value.iter()?.iter().map(|reference| py_model(rt, me, reference)).collect::<Result<Vec<_>>>()?;
        return match parts.split_first() {
            Some((first, rest)) => first.attr("fuse")?.call(rest.to_vec(), vec![]),
            None => py_add(rt, me, s("empty"), &Val::Tuple(vec![]), Val::None, vec![]),
        };
    }
    let reference = if panel::is_instance(value, &["str", "Path"])? {
        py::dict([("model", Val::Str(panel::resolved(value)?))])
    } else {
        panel::builtin("dict")?.call(vec![value.clone()], vec![])?
    };
    let model = reference.get(s("model"))?;
    reference.set(s("model"), Val::Str(panel::resolved(&model)?))?;
    py_add(rt, me, s("model"), &Val::Tuple(vec![]), Val::None, vec![("reference".into(), reference)])
}

/// `_Questions.identity` with a Python `self`.
fn py_identity(me: &Val, index: &Val) -> Result<String> {
    let index = index.integer()?;
    let rows = py::snapshot(&me.attr("nodes")?.get(Val::Slice { start: None, stop: Some(index + 1), step: 1 })?)?.iter()?;
    let mut keys = vec![];
    for node in &rows {
        let key = panel::node_key(node, &keys)?;
        keys.push(key);
    }
    let at = if index < 0 { keys.len() as i64 + index } else { index };
    keys.get(at as usize).cloned().context("list index out of range")
}

/// `_Questions.reading` with a Python `self`.
fn py_reading(me: &Val, shape: &Val, kind: &Val, components: &Val, valid: &Val) -> Result<Val> {
    let index = shape.attr("index")?;
    let identity = Val::Str(py_identity(me, &index)?);
    let key = interop::binary("add", interop::binary("add", identity, s(":"))?, kind.clone())?;
    let answers = me.attr("answers")?;
    if !is_none(&answers) {
        if !answers.contains(&key)? {
            bail!("an enclosure report asked an unmeasured question: {}", key.str()?);
        }
        let row = answers.get(key.clone())?;
        if components.truthy()? && !row.contains(&s("components"))? {
            bail!("an enclosure report asked unmeasured components: {}", key.str()?);
        }
        return Ok(row);
    }
    let fresh = py::dict([("key", key.clone()), ("node", shape.attr("index")?), ("kind", kind.clone())]);
    let query = py::method(&me.attr("queries")?, "setdefault", vec![key, fresh])?;
    if components.truthy()? {
        query.set(s("components"), Val::Bool(true))?;
    }
    if valid.truthy()? {
        query.set(s("valid"), Val::Bool(true))?;
    }
    Ok(if interop::eq(kind, &s("faces"))? {
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

/// `_Questions.document` with a Python `self`.
fn py_document(me: &Val) -> Result<Val> {
    let rows = py::snapshot(&me.attr("nodes")?)?.iter()?;
    let queries = py::snapshot(&me.attr("queries")?)?;
    panel::questions_rows(&rows, &py::method(&queries, "values", vec![])?.iter()?)
}

// ------------------------------------------------------------------------------------------
// Recording the enclosure's leaves

/// `_numeric(shell, graph, box)` while it is entered.
pub struct Numeric {
    shell: Val,
    original_cq: Val,
    recording: Recording,
    leaves: Option<Val>,
}

impl Numeric {
    /// Use the same mechanical station recipes, replacing their geometry leaves (`__enter__`).
    pub fn enter(rt: &Rt, shell: &Val, graph: &AnyGraph, boxv: Option<&Val>) -> Result<Numeric> {
        let original_cq = shell.attr("cq")?;
        let vectors = panel::simple_namespace(rt)?.call(vec![], vec![("Vector".into(), state(rt)?.vector.clone())])?;
        shell.setattr("cq", vectors)?;
        let restore = |error: anyhow::Error| -> Result<Numeric> {
            let _ = shell.setattr("cq", original_cq.clone());
            Err(error)
        };
        let recording = match Recording::enter(rt, shell, graph, Solid::Py(Val::None)) {
            Ok(recording) => recording,
            Err(error) => return restore(error),
        };
        let mut leaves = None;
        if let Some(boxv) = boxv {
            let entered = (|| -> Result<Val> {
                let back_top = rt.import("_enclosure_back_top")?;
                let context = back_top.attr("_leaves")?.call(vec![shell.clone(), graph.to_val(), boxv.clone()], vec![])?;
                context.attr("__enter__")?.call(vec![], vec![])?;
                Ok(context)
            })();
            match entered {
                Ok(context) => leaves = Some(context),
                Err(error) => {
                    let _ = recording.exit();
                    return restore(error);
                }
            }
        }
        Ok(Numeric { shell: shell.clone(), original_cq, recording, leaves })
    }
    /// Restore the leaves (last entered first) and `shell.cq` (`__exit__`); a restore that fails
    /// raises after the others ran.
    pub fn exit(&self) -> Result<()> {
        let mut outcome = Ok(());
        if let Some(leaves) = &self.leaves {
            if let Err(error) = leaves.attr("__exit__").and_then(|exit| exit.call(vec![Val::None, Val::None, Val::None], vec![])) {
                outcome = Err(error);
            }
        }
        if let Err(error) = self.recording.exit() {
            outcome = Err(error);
        }
        self.shell.setattr("cq", self.original_cq.clone())?;
        outcome
    }
}

/// Run `body` inside `_numeric(shell, graph, box)`, as a `with` block: the exit always runs and
/// its failure wins.
pub fn with_numeric<T>(rt: &Rt, shell: &Val, graph: &AnyGraph, boxv: Option<&Val>, body: impl FnOnce() -> Result<T>) -> Result<T> {
    let entered = Numeric::enter(rt, shell, graph, boxv)?;
    let result = body();
    entered.exit()?;
    result
}

/// `_numeric(shell, graph, box)`: the context manager generated callers enter.
pub fn numeric(rt: &Rt, shell: &Val, graph: &Val, boxv: &Val) -> Val {
    let held: Rc<RefCell<Option<Numeric>>> = Rc::new(RefCell::new(None));
    let enter = {
        let (rt, shell, graph, boxv, held) = (rt.clone(), shell.clone(), graph.clone(), boxv.clone(), held.clone());
        Val::function(move |_, _| {
            let _frame = rt.frame(MODULE);
            let boxv = (!is_none(&boxv)).then_some(&boxv);
            let entered = Numeric::enter(&rt, &shell, &AnyGraph::from_val(&graph), boxv)?;
            *held.borrow_mut() = Some(entered);
            Ok(Val::None)
        })
    };
    let exit = Val::function(move |_, _| {
        let entered = held.borrow_mut().take();
        match entered {
            Some(entered) => entered.exit()?,
            None => bail!("_rust_enclosure_checks: _numeric was not entered"),
        }
        Ok(Val::None)
    });
    rt::context(enter, exit)
}

/// `_measure(graph)`: the answers to every question the graph collected.
pub fn measure(rt: &Rt, graph: &AnyGraph) -> Result<Val> {
    let rust_part = rt.import("_rust_part")?;
    let check = rust_part.attr("check")?;
    let document = match graph {
        AnyGraph::Native(g) => g.questions_document()?,
        AnyGraph::Py(object) => py::method(object, "document", vec![])?,
    };
    check.call(vec![s("enclosure-shell"), s("enclosure-checks"), document], vec![])?.get(s("answers"))
}

/// The existing enclosure rows in the whole-machine scorecard's scalar form.
pub fn check_rows(bounds: &Val) -> Result<Val> {
    let mut rows = vec![];
    for row in bounds.iter()? {
        let id = row.attr("id")?;
        let label = row.attr("label")?;
        let status = if row.attr("ok")?.truthy()? { "pass" } else { "fail" };
        rows.push(py::dict([
            ("id", id),
            ("label", label),
            ("kind", s("gate")),
            ("status", s(status)),
            ("value", row.attr("value")?),
            ("target", row.attr("target")?),
            ("detail", row.attr("detail")?),
            ("active", Val::Bool(true)),
        ]));
    }
    Ok(Val::list(rows))
}

const SLIDE_PLANES: &str = "the back Z-slide catch is not two broad horizontal bearing planes:";

/// One pass of the enclosure's reports over `models` with `graph` (questions, then answers).
#[allow(clippy::too_many_arguments)]
pub fn piece_reports(rt: &Rt, shell: &Val, boxv: &Val, models: &Val, installed_retainer: &Val, core: &Val, graph: &AnyGraph) -> Result<Val> {
    let mut pieces: Vec<(Val, Solid)> = vec![];
    for item in py::method(models, "items", vec![])?.iter()? {
        let pair = py::unpack(&item, 2)?;
        let piece = model(graph, &pair[1])?;
        match pieces.iter_mut().find(|(name, _)| interop::eq(name, &pair[0]).unwrap_or(false)) {
            Some(slot) => slot.1 = piece,
            None => pieces.push((pair[0].clone(), piece)),
        }
    }
    let seated = if is_none(installed_retainer) { Solid::Py(Val::None) } else { model(graph, installed_retainer)? };
    let cold_core = if is_none(core) { Solid::Py(Val::None) } else { model(graph, core)? };
    let collected = Val::list(vec![]);
    let original_record = shell.attr("record_bound")?;
    let record = {
        let (collected, graph, original) = (collected.clone(), graph.clone(), original_record.clone());
        Val::function(move |args, kwargs| {
            let row = bound_values(args, kwargs, &["row"])?.remove(0);
            py::method(&collected, "append", vec![row.clone()])?;
            if !is_none(&graph.attr("answers")?) {
                return py::call(&original, vec![row]);
            }
            Ok(row)
        })
    };
    shell.setattr("record_bound", record.clone())?;
    let table = Val::dict(pieces.iter().map(|(name, piece)| (name.clone(), piece.to_val())).collect());
    let has = |name: &str| table.contains(&s(name));
    let body = || -> Result<(Val, Val)> {
        let boxed = (!is_none(boxv)).then_some(boxv);
        with_numeric(rt, shell, graph, boxed, || {
            let mut disconnected = vec![];
            for (name, piece) in &pieces {
                let count = piece.solids()?.len();
                let valid = piece.is_valid()?;
                if count != 1 || !valid.truthy()? {
                    disconnected.push(format!("{}: {count} solids", interop::format(name, "")?));
                }
            }
            let detail = if disconnected.is_empty() {
                format!("{} connected pieces", pieces.len())
            } else {
                disconnected.join("; ")
            };
            let listed = Val::list(disconnected.iter().map(|row| s(row)).collect());
            let bound = shell.attr("Bound")?.call(vec![
                s("connected-pieces"),
                s("Each printed enclosure piece is one valid connected solid"),
                Val::Bool(disconnected.is_empty()),
                s(&detail),
                s("one valid solid per printed piece"),
                listed,
            ], vec![])?;
            py::call(&record, vec![bound])?;
            if has("back-top")? {
                py::call(&shell.attr("_ceiling_show_cap_bound")?, vec![table.get(s("back-top"))?, boxv.clone()])?;
            }
            if has("front-bottom")? && has("back-bottom")? {
                py::call(&shell.attr("_handhold_bound")?, vec![table.clone(), boxv.clone()])?;
            }
            py::call(&shell.attr("_silhouette_bound")?, vec![table.clone(), boxv.clone()])?;
            let slides = match shell.attr("_report_slide").and_then(|f| py::call(&f, vec![table.clone(), boxv.clone()])) {
                Ok(slides) => slides,
                Err(error) => {
                    if !is_none(&graph.attr("answers")?) || !error.to_string().starts_with(SLIDE_PLANES) {
                        return Err(error);
                    }
                    // Both existing face questions are registered before the scalar
                    // bearing limit can be evaluated from the measured faces.
                    Val::dict(vec![])
                }
            };
            if has("front-top")? {
                py::call(&shell.attr("_report_facet")?, vec![table.get(s("front-top"))?, boxv.clone()])?;
            }
            py::call_kw(&shell.attr("_report_split")?, vec![table.clone(), cold_core.to_val(), boxv.clone()],
                vec![("installed_retainer", seated.to_val())])?;
            let vents = py::call(&shell.attr("vent_readings")?, vec![table.clone(), boxv.clone()])?;
            Ok((slides, vents))
        })
    };
    let result = body();
    shell.setattr("record_bound", original_record)?;
    let (slides, vents) = result?;
    let piece_bounds = Val::dict(vec![]);
    if !is_none(&graph.attr("answers")?) {
        for (name, piece) in &pieces {
            let row = reading(graph, piece, vec![])?;
            let mut corners = row.get(s("min"))?.iter()?;
            corners.extend(row.get(s("max"))?.iter()?);
            piece_bounds.set(name.clone(), Val::list(corners))?;
        }
    }
    Ok(py::dict([
        ("bounds", collected.clone()),
        ("checks", check_rows(&collected)?),
        ("slides", slides),
        ("vents", vents),
        ("piece_bounds", piece_bounds),
    ]))
}

/// All current inline enclosure questions in one Rust invocation.
///
/// ``models`` is ordered piece name -> fine NPZ path/instance specification. A
/// logical body can also name an ordered list of instance specifications. The
/// installed retainer is explicit; the relaxed print is not substituted for it.
/// Existing scalar decisions and report text run after the answers arrive.
pub fn check_pieces(rt: &Rt, shell: &Val, boxv: &Val, models: &Val, installed_retainer: &Val, core: &Val) -> Result<Val> {
    if models.contains(&s("pump-retainer"))? && is_none(installed_retainer) {
        bail!("enclosure checks need the explicit installed retainer model");
    }
    let questions = AnyGraph::Native(Graph::questions(Val::None));
    let state = state(rt)?;
    let quiet = state.redirect_stdout.call(vec![py::method(&state.io, "StringIO", vec![])?], vec![])?;
    quiet.attr("__enter__")?.call(vec![], vec![])?;
    let asked = piece_reports(rt, shell, boxv, models, installed_retainer, core, &questions);
    quiet.attr("__exit__")?.call(vec![Val::None, Val::None, Val::None], vec![])?;
    asked?;
    let answers = measure(rt, &questions)?;
    piece_reports(rt, shell, boxv, models, installed_retainer, core, &AnyGraph::Native(Graph::questions(answers)))
}

fn gt(a: &Val, b: &Val) -> Result<bool> {
    interop::compare("gt", a.clone(), b.clone())?.truthy()
}

fn ask(rt: &Rt, shell: &Val, pack: &Val, bounds: &Val, references: &Val, graph: &AnyGraph) -> Result<Val> {
    with_numeric(rt, shell, graph, None, || {
        let pair = py::unpack(&py::call(&shell.attr("box_question_tools")?, vec![pack.clone(), bounds.clone()])?, 2)?;
        let (tools, questions) = (&pair[0], &pair[1]);
        let mut bodies: Vec<(Val, Solid)> = vec![];
        for name in pack.attr("placed")?.iter()? {
            let body = model(graph, &references.get(name.clone())?)?;
            match bodies.iter_mut().find(|(held, _)| interop::eq(held, &name).unwrap_or(false)) {
                Some(slot) => slot.1 = body,
                None => bodies.push((name, body)),
            }
        }
        let tables = Val::dict(vec![]);
        for family in ["floor", "under", "pillars"] {
            tables.set(s(family), Val::dict(vec![]))?;
        }
        tables.set(s("lip"), py::dict([("front", Val::dict(vec![])), ("back", Val::dict(vec![]))]))?;
        for question in questions.iter()? {
            let tool = tools.get(question.get(s("tool"))?)?;
            let positive = question.get(s("positive_components"))?;
            let mut raw = py::dict([("volume_mm3", Val::Float(0.)), ("min", Val::None), ("max", Val::None)]);
            if positive.truthy()? {
                raw.set(s("components"), Val::list(vec![]))?;
            }
            let tool = Solid::from_val(&tool);
            let mut overlaps = !tool.is_none();
            if overlaps {
                let reach = tool.bounds_val()?;
                if !is_none(&reach) {
                    let corners = py::unpack(&bounds.get(question.get(s("body"))?)?, 2)?;
                    let (lower, upper) = (&corners[0], &corners[1]);
                    let mut all = true;
                    for k in 0..3i64 {
                        let near = gt(&upper.get(Val::Int(k))?, &reach.get(Val::Int(2 * k))?)?
                            && gt(&reach.get(Val::Int(2 * k + 1))?, &lower.get(Val::Int(k))?)?;
                        all &= near;
                    }
                    overlaps = all;
                }
            }
            if overlaps {
                let body_name = question.get(s("body"))?;
                let reference = references.get(body_name.clone())?;
                let instances = if panel::is_instance(&reference, &["list", "tuple"])? { reference.iter()? } else { vec![reference.clone()] };
                let dict = panel::builtin("dict")?;
                let mut sections = vec![];
                for instance in &instances {
                    for i in py::method(instance, "get", vec![s("indices"), Val::Tuple(vec![])])?.iter()? {
                        sections.push(dict.call(vec![instance.clone()], vec![("indices".into(), Val::list(vec![i]))])?);
                    }
                }
                let body_first = question.get(s("body_first"))?;
                let hit = if body_first.truthy()? && sections.len() > 1 {
                    // A native compound section is the ordered body sections, not a
                    // union that can remove a body's own internal overlap reading.
                    let mut hits = vec![];
                    for section in &sections {
                        hits.push(model(graph, section)?.intersect(std::slice::from_ref(&tool))?);
                    }
                    let indices = hits.iter().map(Solid::index_val).collect::<Result<Vec<_>>>()?;
                    graph.add("compose", indices, Val::None, vec![])?
                } else {
                    let body = bodies.iter().find(|(held, _)| interop::eq(held, &body_name).unwrap_or(false))
                        .map(|(_, body)| body.clone())
                        .with_context(|| format!("missing key {}", body_name.repr().unwrap_or_default()))?;
                    if body_first.truthy()? { body.intersect(std::slice::from_ref(&tool))? } else { tool.intersect(&[body])? }
                };
                let measured = reading(graph, &hit, vec![("components", positive.clone())])?;
                raw = Val::dict(interop::entries_of(&measured)?.into_iter()
                    .filter(|(key, _)| !matches!(key, Val::Str(k) if k == "valid"))
                    .collect());
            }
            let family = question.get(s("family"))?;
            let key = question.get(s("key"))?;
            if interop::eq(&family, &s("lip"))? {
                tables.get(family)?.get(key.get(Val::Int(0))?)?.set(key.get(Val::Int(1))?, raw)?;
            } else {
                tables.get(family)?.set(Val::Tuple(key.iter()?), raw)?;
            }
        }
        shell.attr("BoxReadings")?.call(vec![
            panel::builtin("dict")?.call(vec![bounds.clone()], vec![])?,
            tables.get(s("lip"))?,
            tables.get(s("floor"))?,
            tables.get(s("under"))?,
            tables.get(s("pillars"))?,
        ], vec![])
    })
}

/// The complete Box lip/floor/under-wall/pillar questions from fine selections.
pub fn box_readings(rt: &Rt, shell: &Val, pack: &Val, bounds: &Val, references: &Val) -> Result<Val> {
    let questions = AnyGraph::Native(Graph::questions(Val::None));
    ask(rt, shell, pack, bounds, references, &questions)?;
    let answers = measure(rt, &questions)?;
    ask(rt, shell, pack, bounds, references, &AnyGraph::Native(Graph::questions(answers)))
}

// ------------------------------------------------------------------------------------------
// The module

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("ExitStack", rt.member("contextlib", "ExitStack")?)?;
    ns.set("contextmanager", rt.member("contextlib", "contextmanager")?)?;
    let redirect_stdout = rt.member("contextlib", "redirect_stdout")?;
    ns.set("redirect_stdout", redirect_stdout.clone())?;
    ns.set("hashlib", rt.import("hashlib")?)?;
    let io = rt.import("io")?;
    ns.set("io", io.clone())?;
    ns.set("json", rt.import("json")?)?;
    ns.set("math", rt.import("math")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("SimpleNamespace", rt.member("types", "SimpleNamespace")?)?;
    rt.import("_enclosure_panel")?;
    ns.set("_Graph", rt.member("_enclosure_panel", "_Graph")?)?;
    ns.set("_Shape", rt.member("_enclosure_panel", "_Shape")?)?;
    ns.set("_record", rt.member("_enclosure_panel", "_record")?)?;

    ns.def(rt, "_Vector.__init__", |_rt, args, _kwargs| {
        let (me, coordinates) = first_rest(&args)?;
        let xyz = if coordinates.len() == 1 { Val::Tuple(coordinates[0].iter()?) } else { Val::Tuple(coordinates.to_vec()) };
        me.setattr("xyz", xyz.clone())?;
        let parts = py::unpack(&xyz, 3)?;
        me.setattr("x", parts[0].clone())?;
        me.setattr("y", parts[1].clone())?;
        me.setattr("z", parts[2].clone())?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_Vector.__iter__", |_rt, args, kwargs| {
        bound_values(args, kwargs, &["self"])?[0].attr("xyz")
    })?;
    ns.def(rt, "_Vector.__getitem__", |_rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "index"])?;
        v[0].attr("xyz")?.get(v[1].clone())
    })?;
    ns.def(rt, "_Vector.__add__", |rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "other"])?;
        vector_combine(rt, &v[0], &v[1], "add")
    })?;
    ns.def(rt, "_Vector.__sub__", |rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "other"])?;
        vector_combine(rt, &v[0], &v[1], "sub")
    })?;
    ns.def(rt, "_Vector.dot", |_rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "other"])?;
        vector_dot(&v[0], &v[1])
    })?;
    ns.def(rt, "_Vector.Length", |_rt, args, kwargs| {
        let me = bound_values(args, kwargs, &["self"])?.remove(0);
        Ok(Val::Float(vector_dot(&me, &me)?.num()?.sqrt()))
    })?;
    let vector_class = rt.python_type(MODULE, "_Vector")?;
    ns.set("_Vector", vector_class.clone())?;

    ns.def(rt, "_bounds", |rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["lower", "upper"])?;
        bounds_namespace(rt, &v[0], &v[1])
    })?;

    ns.def(rt, "_ScalarFace.__init__", |_rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "row"])?;
        v[0].setattr("row", v[1].clone())?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_ScalarFace.Area", |_rt, args, kwargs| {
        bound_values(args, kwargs, &["self"])?[0].attr("row")?.get(s("area"))
    })?;
    ns.def(rt, "_ScalarFace.Center", |rt, args, kwargs| {
        let me = bound_values(args, kwargs, &["self"])?.remove(0);
        vector(rt, me.attr("row")?.get(s("centre"))?.iter()?)
    })?;
    ns.def(rt, "_ScalarFace.normalAt", |rt, args, kwargs| {
        let me = bound_values(args, kwargs, &["self"])?.remove(0);
        vector(rt, me.attr("row")?.get(s("normal"))?.iter()?)
    })?;
    ns.def(rt, "_ScalarFace.BoundingBox", |rt, args, kwargs| {
        let row = bound_values(args, kwargs, &["self"])?[0].attr("row")?;
        bounds_namespace(rt, &row.get(s("min"))?, &row.get(s("max"))?)
    })?;
    ns.def(rt, "_ScalarFace.geomType", |_rt, args, kwargs| {
        bound_values(args, kwargs, &["self"])?[0].attr("row")?.get(s("kind"))
    })?;
    let scalar_face = rt.python_type(MODULE, "_ScalarFace")?;
    ns.set("_ScalarFace", scalar_face.clone())?;

    ns.def(rt, "_ScalarComponent.__init__", |_rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "row"])?;
        v[0].setattr("row", v[1].clone())?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_ScalarComponent.BoundingBox", |rt, args, kwargs| {
        let row = bound_values(args, kwargs, &["self"])?[0].attr("row")?;
        bounds_namespace(rt, &row.get(s("min"))?, &row.get(s("max"))?)
    })?;
    ns.def(rt, "_ScalarComponent.Volume", |_rt, args, kwargs| {
        bound_values(args, kwargs, &["self"])?[0].attr("row")?.get(s("volume_mm3"))
    })?;
    let scalar_component = rt.python_type(MODULE, "_ScalarComponent")?;
    ns.set("_ScalarComponent", scalar_component.clone())?;

    ns.def(rt, "_ReadingShape.translate", |_rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "delta"])?;
        match Solid::from_val(&v[0]) {
            Solid::Native(shape) => Ok(shape.translate(&v[1])?.to_val()),
            Solid::Py(me) => panel::py_translate(&me, &Val::Tuple(v[1].iter()?)),
        }
    })?;
    ns.def(rt, "_ReadingShape.Volume", |_rt, args, kwargs| {
        volume_of(&Solid::from_val(&bound_values(args, kwargs, &["self"])?[0]))
    })?;
    ns.def(rt, "_ReadingShape.BoundingBox", |rt, args, kwargs| {
        bounding_box_of(rt, &Solid::from_val(&bound_values(args, kwargs, &["self"])?[0]))
    })?;
    ns.def(rt, "_ReadingShape.Solids", |rt, args, kwargs| {
        solids_of(rt, &Solid::from_val(&bound_values(args, kwargs, &["self"])?[0]))
    })?;
    ns.def(rt, "_ReadingShape.isValid", |_rt, args, kwargs| {
        is_valid_of(&Solid::from_val(&bound_values(args, kwargs, &["self"])?[0]))
    })?;
    ns.def(rt, "_ReadingShape.Faces", |rt, args, kwargs| {
        faces_of(rt, &Solid::from_val(&bound_values(args, kwargs, &["self"])?[0]))
    })?;
    let reading_shape = rt.python_type(MODULE, "_ReadingShape")?;
    ns.set("_ReadingShape", reading_shape.clone())?;

    ns.def(rt, "_Questions.__init__", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "answers"], &[])?;
        let me = b.req("self")?;
        let answers = b.opt("answers").unwrap_or(Val::None);
        if Graph::from_val(&me).is_none() {
            me.setattr("nodes", Val::list(vec![]))?;
        }
        me.setattr("answers", answers)?;
        me.setattr("queries", Val::dict(vec![]))?;
        me.setattr("extras", Val::dict(vec![]))?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_Questions.add", |rt, args, kwargs| {
        let (me, op, inputs, bounds, numbers) = panel::bind_add(args, kwargs, true)?;
        let me = me.context("missing argument self")?;
        if let Some(graph) = Graph::from_val(&me) {
            return Ok(graph.add_val(op, &inputs, &bounds, numbers)?.to_val());
        }
        py_add(rt, &me, op, &inputs, bounds, numbers)
    })?;
    ns.def(rt, "_Questions.model", |rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "value"])?;
        if let Some(graph) = Graph::from_val(&v[0]) {
            return Ok(graph.model(&v[1])?.to_val());
        }
        py_model(rt, &v[0], &v[1])
    })?;
    ns.def(rt, "_Questions.identity", |_rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["self", "index"])?;
        if let Some(graph) = Graph::from_val(&v[0]) {
            return Ok(Val::Str(graph.identity(v[1].integer()? as usize)?));
        }
        Ok(Val::Str(py_identity(&v[0], &v[1])?))
    })?;
    ns.def(rt, "_Questions.reading", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "shape"], &["kind", "components", "valid"])?;
        let (me, shape) = (b.req("self")?, b.req("shape")?);
        let kind = b.opt("kind").unwrap_or(s("stats"));
        let components = b.opt("components").unwrap_or(Val::Bool(false));
        let valid = b.opt("valid").unwrap_or(Val::Bool(false));
        if let Some(graph) = Graph::from_val(&me) {
            return graph.reading(&Solid::from_val(&shape), &kind.str()?, components.truthy()?, valid.truthy()?);
        }
        py_reading(&me, &shape, &kind, &components, &valid)
    })?;
    ns.def(rt, "_Questions.document", |_rt, args, kwargs| {
        let me = bound_values(args, kwargs, &["self"])?.remove(0);
        if let Some(graph) = Graph::from_val(&me) {
            return graph.questions_document();
        }
        py_document(&me)
    })?;
    ns.set("_Questions", rt.python_type(MODULE, "_Questions")?)?;

    ns.def(rt, "_numeric", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shell", "graph", "box"], &[])?;
        let (shell, graph) = (b.req("shell")?, b.req("graph")?);
        let boxv = b.opt("box").unwrap_or(Val::None);
        Ok(numeric(rt, &shell, &graph, &boxv))
    })?;
    ns.def(rt, "_measure", |rt, args, kwargs| {
        let graph = bound_values(args, kwargs, &["graph"])?.remove(0);
        measure(rt, &AnyGraph::from_val(&graph))
    })?;
    ns.def(rt, "check_rows", |_rt, args, kwargs| {
        check_rows(&bound_values(args, kwargs, &["bounds"])?[0])
    })?;
    ns.def(rt, "_piece_reports", |rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["shell", "box", "models", "installed_retainer", "core", "graph"])?;
        piece_reports(rt, &v[0], &v[1], &v[2], &v[3], &v[4], &AnyGraph::from_val(&v[5]))
    })?;
    ns.def(rt, "check_pieces", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shell", "box", "models", "installed_retainer", "core"], &[])?;
        let (shell, boxv, models) = (b.req("shell")?, b.req("box")?, b.req("models")?);
        let installed_retainer = b.opt("installed_retainer").unwrap_or(Val::None);
        let core = b.opt("core").unwrap_or(Val::None);
        check_pieces(rt, &shell, &boxv, &models, &installed_retainer, &core)
    })?;
    ns.def(rt, "box_readings", |rt, args, kwargs| {
        let v = bound_values(args, kwargs, &["shell", "pack", "bounds", "references"])?;
        box_readings(rt, &v[0], &v[1], &v[2], &v[3])
    })?;
    rt.keep(MODULE, State { vector: vector_class, scalar_face, scalar_component, reading_shape, redirect_stdout, io });
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}
