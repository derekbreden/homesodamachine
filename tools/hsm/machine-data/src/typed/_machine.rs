//! The machine scene: its scalar document, the fine-model export that writes it and the reader
//! that loads a current scene back into a `Machine`.
//!
//! The scene's bodies, frames and runs are library objects (meshcad shapes, `_routing` frames and
//! runs), so they stay values at the boundary. `sources` and `stamps` are installed natively after
//! the top level runs, so every use reads them from the namespace.
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::Result;
use hsm_documents::interop::{self, Val};
use py::s;
use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

/// Not yet compared with the generated build: the hybrid development build runs the generated namespace.
pub const TYPED: bool = false;

const MODULE: &str = "_machine";
const SCHEMA: i64 = 1;

struct State {
    ns: Ns,
    root: PathBuf,
    ml: PathBuf,
    /// `PATH`: the scene the default arguments name.
    path: PathBuf,
    time: Val,
    sys: Val,
    types: Val,
    machine_type: Val,
}

fn state(rt: &Rt) -> Result<std::rc::Rc<State>> {
    rt.state::<State>(MODULE)
}

/// `stamps()`, read from the namespace where the native reader is installed.
fn stamps(st: &State) -> Result<Val> {
    py::call(&st.ns.get("stamps")?, vec![])
}

/// `isinstance(value, kind)` as the runtime answers it for the builtin `list` and `dict`.
fn isinstance(value: &Val, kind: &str) -> Result<bool> {
    if matches!(value, Val::Ref(_)) {
        let builtin = interop::builtin("isinstance").expect("isinstance");
        return builtin.call(vec![value.clone(), Val::Type(kind.into())], vec![])?.truthy();
    }
    Ok(match kind {
        "list" => matches!(value, Val::List(_)),
        "dict" => matches!(value, Val::Dict(_)),
        _ => false,
    })
}

/// A builtin type applied to one value: `tuple(v)`, `dict(v)`, `int(v)`.
fn construct(kind: &str, value: Val) -> Result<Val> {
    Val::Type(kind.into()).call(vec![value], vec![])
}

/// `Machine.moved`: the sources whose stamp differs between the tree and the scene.
fn moved(st: &State, this: &Val) -> Result<Val> {
    let now = stamps(st)?;
    let was = py::snapshot(&this.attr("sources")?)?;
    let mut rels = BTreeSet::new();
    for key in now.iter()?.iter().chain(was.iter()?.iter()) {
        rels.insert(key.str()?);
    }
    let mut out = vec![];
    for rel in rels {
        let a = py::method(&now, "get", vec![s(&rel)])?;
        let b = py::method(&was, "get", vec![s(&rel)])?;
        if !interop::eq(&a, &b)? {
            out.push(s(rel));
        }
    }
    Ok(Val::Tuple(out))
}

/// `Machine.measured`: one line on the scene, and the sources that moved since it was built.
fn measured(st: &State, this: &Val) -> Result<Val> {
    let bodies = this.attr("solids")?.len()?;
    let runs = this.attr("runs")?.len()?;
    let strftime = st.time.attr("strftime")?;
    let localtime = st.time.attr("localtime")?;
    let when = localtime.call(vec![this.attr("taken")?], vec![])?;
    let built = strftime.call(vec![s("%Y-%m-%d %H:%M"), when], vec![])?;
    let head = format!("{bodies} bodies, {runs} runs, built {}", interop::format(&built, "")?);
    let gone = moved(st, this)?.iter()?;
    if gone.is_empty() {
        return Ok(s(format!("{head}, off this tree")));
    }
    let mut names = vec![];
    for g in gone.iter().take(4) {
        names.push(Path::new(&g.str()?).file_name().map(|v| v.to_string_lossy().into_owned()).unwrap_or_default());
    }
    let mut named = names.join(", ");
    if gone.len() > 4 {
        named += &format!(" and {} more", gone.len() - 4);
    }
    Ok(s(format!("{head}, BEFORE {named} MOVED: this is the machine in that scene, not the tree's")))
}

/// `document(a, taken=None, card=None, drain=None, *, solids=None, core=None)`: the scene's
/// scalar document.
fn document(st: &State, a: &Val, taken: Val, card: Val, drain: Val, solids: Val, core: Val) -> Result<Val> {
    let metadata = py::method(a, "get", vec![s("metadata"), a.clone()])?;
    let taken = if matches!(taken, Val::None) { py::call(&st.time.attr("time")?, vec![])? } else { taken };
    let sources = stamps(st)?;
    let solids = if solids.truthy()? { solids } else { py::dget(&metadata, "solids", Val::Tuple(vec![]))? };
    let solids = Val::list(solids.iter()?);
    let core = if core.truthy()? { core } else { py::dget(&metadata, "core_body_names", Val::Tuple(vec![]))? };
    let core = Val::list(core.iter()?);
    let runs = py::dget(&metadata, "runs", Val::list(vec![]))?;
    let frames = py::dget(&metadata, "frames", Val::dict(vec![]))?;
    let boxed = py::method(&metadata, "get", vec![s("box")])?;
    let anchors = py::dget(&metadata, "anchors", Val::dict(vec![]))?;
    Ok(py::dict([
        ("schema", Val::Int(SCHEMA)),
        ("taken", taken),
        ("sources", sources),
        ("solids", solids),
        ("core", core),
        ("runs", runs),
        ("frames", frames),
        ("box", boxed),
        ("anchors", anchors),
        ("card", card),
        ("drain", drain),
    ]))
}

/// `write_from_fine(model, path=PATH, *, aliases, envelope, document)`: the scene written from
/// the fine model by the Rust export.
fn write_from_fine(rt: &Rt, model: &Val, path: &Val, aliases: Val, envelope: &Val, document: Val) -> Result<Val> {
    rt.import("_machine_export")?;
    let path = Val::Path(py::resolve(&py::path(path)?)?);
    super::_machine_export::scene(rt, model, &path, aliases, envelope, document)?;
    Ok(path)
}

/// `_tupled(value)`: JSON lists as tuples, all the way down.
fn tupled(value: &Val) -> Result<Val> {
    let value = py::snapshot(value)?;
    tupled_local(&value)
}
fn tupled_local(value: &Val) -> Result<Val> {
    Ok(match value {
        Val::List(rows) => Val::Tuple(rows.borrow().iter().map(tupled_local).collect::<Result<_>>()?),
        Val::Dict(rows) => {
            let out = Val::dict(vec![]);
            for (k, v) in rows.borrow().iter() {
                out.set(k.clone(), tupled_local(v)?)?;
            }
            out
        }
        other => other.clone(),
    })
}

/// `_run(row)`: a scene run row as a `_routing.Run`.
fn run(rt: &Rt, row: &Val) -> Result<Val> {
    let routing = rt.import("_routing")?;
    let row = construct("dict", row.clone())?;
    let pts = py::at(&row, "pts")?.iter()?.into_iter().map(|p| construct("tuple", p)).collect::<Result<Vec<_>>>()?;
    row.set(s("pts"), Val::list(pts))?;
    let bends = py::dget(&row, "bends", Val::Tuple(vec![]))?;
    let bends = bends.iter()?.into_iter().map(|b| construct("tuple", b)).collect::<Result<Vec<_>>>()?;
    row.set(s("bends"), Val::list(bends))?;
    for k in ["radii", "caps"] {
        let out = Val::dict(vec![]);
        for item in py::method(&py::dget(&row, k, Val::dict(vec![]))?, "items", vec![])?.iter()? {
            let pair = py::unpack(&item, 2)?;
            out.set(construct("int", pair[0].clone())?, pair[1].clone())?;
        }
        row.set(s(k), out)?;
    }
    routing.attr("Run")?.call(vec![], super::rt::keyword_items(row)?)
}

/// `_box(doc)`: the scene's Box record, rebuilt from its namedtuple description.
fn boxed(rt: &Rt, doc: &Val) -> Result<Val> {
    let collections = rt.import("collections")?;
    let spec = rt.import("_box_spec")?;
    if matches!(doc, Val::None) {
        return Ok(Val::None);
    }
    let namedtuple = collections.attr("namedtuple")?;
    let record = spec.attr("_RECORD")?;
    let records = Val::dict(vec![]);
    fn collect(value: &Val, record: &Val, records: &Val, namedtuple: &Val) -> Result<()> {
        match value {
            Val::List(rows) => {
                for v in rows.borrow().iter() {
                    collect(v, record, records, namedtuple)?;
                }
            }
            Val::Dict(rows) => {
                if value.contains(record)? {
                    let name = value.get(record.clone())?;
                    let made = py::call_kw(namedtuple, vec![name.clone(), py::at(value, "fields")?], vec![("module", s(MODULE))])?;
                    if !records.contains(&name)? {
                        records.set(name, made)?;
                    }
                }
                for (_, v) in rows.borrow().iter() {
                    collect(v, record, records, namedtuple)?;
                }
            }
            _ => {}
        }
        Ok(())
    }
    let body = py::at(doc, "box")?;
    collect(&py::snapshot(&body)?, &record, &records, &namedtuple)?;
    let fields = py::at(doc, "box_fields")?;
    let box_type = py::call_kw(&namedtuple, vec![s("Box"), fields.clone()], vec![("module", s(MODULE))])?;
    let tupled = spec.attr("_tupled")?;
    let mut values = vec![];
    for f in fields.iter()? {
        values.push(py::call(&tupled, vec![py::at(doc, "box")?.get(f)?, records.clone()])?);
    }
    py::call(&box_type, values)
}

/// `load(path=PATH)`: the scene at `path` as a `Machine`, or None when it is missing or of
/// another schema.
fn load(rt: &Rt, st: &State, path: &Val) -> Result<Val> {
    let path = py::path(path)?;
    if !path.is_file() {
        return Ok(Val::None);
    }
    let scene = rt.member("meshcad", "scene")?;
    let routing = rt.import("_routing")?;
    let doc = py::method(&scene, "document", vec![Val::Path(path.clone())])?;
    if matches!(doc, Val::None) || !interop::eq(&py::method(&doc, "get", vec![s("schema")])?, &Val::Int(SCHEMA))? {
        return Ok(Val::None);
    }
    let held = py::method(&scene, "load", vec![Val::Path(path.clone())])?;
    let bodies = Val::dict(vec![]);
    for item in py::method(&held, "items", vec![])?.iter()? {
        let pair = py::unpack(&item, 2)?;
        let body = py::unpack(&pair[1], 2)?;
        bodies.set(pair[0].clone(), body[0].clone())?;
    }
    let frames = Val::dict(vec![]);
    let sides = Val::Tuple(["xmin", "xmax", "ymin", "ymax", "zmin", "zmax"].into_iter().map(s).collect());
    for item in py::method(&py::at(&doc, "frames")?, "items", vec![])?.iter()? {
        let pair = py::unpack(&item, 2)?;
        let (name, f) = (pair[0].clone(), pair[1].clone());
        let table = Val::dict(vec![]);
        for port in py::method(&py::at(&f, "ports")?, "items", vec![])?.iter()? {
            let port = py::unpack(&port, 2)?;
            let fields = py::unpack(&port[1], 3)?;
            let axis = if isinstance(&fields[1], "list")? { construct("tuple", fields[1].clone())? } else { fields[1].clone() };
            table.set(port[0].clone(), Val::Tuple(vec![construct("tuple", fields[0].clone())?, axis, fields[2].clone()]))?;
        }
        let zipped = interop::builtin("zip").expect("zip").call(vec![sides.clone(), py::at(&f, "bb")?], vec![])?;
        let bb = st.types.attr("SimpleNamespace")?.call(vec![], super::rt::keyword_items(construct("dict", zipped)?)?)?;
        let frame = py::call_kw(&routing.attr("frame")?, vec![name.clone(), Val::None, table], vec![("bb", bb)])?;
        frames.set(name, frame)?;
    }
    let colors = Val::dict(vec![]);
    for item in py::method(&held, "items", vec![])?.iter()? {
        let pair = py::unpack(&item, 2)?;
        let body = py::unpack(&pair[1], 2)?;
        colors.set(pair[0].clone(), body[1].clone())?;
    }
    let solids = construct("tuple", py::at(&doc, "solids")?)?;
    let core = construct("tuple", py::at(&doc, "core")?)?;
    let runs = Val::dict(vec![]);
    for row in py::at(&doc, "runs")?.iter()? {
        runs.set(py::at(&row, "id")?, run(rt, &row)?)?;
    }
    let boxed = boxed(rt, &py::at(&doc, "box")?)?;
    let anchors = tupled(&py::at(&doc, "anchors")?)?;
    let sources = py::at(&doc, "sources")?;
    let taken = py::at(&doc, "taken")?;
    let card = py::method(&doc, "get", vec![s("card")])?;
    let drain = py::method(&doc, "get", vec![s("drain")])?;
    py::call_kw(&st.machine_type, vec![], vec![
        ("bodies", bodies),
        ("colors", colors),
        ("solids", solids),
        ("core", core),
        ("runs", runs),
        ("frames", frames),
        ("box", boxed),
        ("anchors", anchors),
        ("sources", sources),
        ("taken", taken),
        ("path", Val::Path(path)),
        ("card", card),
        ("drain", drain),
    ])
}

/// `current(path=PATH)`: the scene when its sources match the tree's, else None.
fn current(rt: &Rt, st: &State, path: &Val) -> Result<Val> {
    let path = py::path(path)?;
    if !path.is_file() {
        return Ok(Val::None);
    }
    let reader = rt.member("_assembly_model", "document")?;
    let doc = py::call(&reader, vec![Val::Path(path.clone())])?;
    if matches!(doc, Val::None)
        || !interop::eq(&py::method(&doc, "get", vec![s("schema")])?, &Val::Int(SCHEMA))?
        || !interop::eq(&py::at(&doc, "sources")?, &stamps(st)?)?
    {
        return Ok(Val::None);
    }
    load(rt, st, &Val::Path(path))
}

/// `machine()`: the current scene, running the Rust assembly driver first when it is stale.
fn machine(rt: &Rt, st: &State) -> Result<Val> {
    let m = current(rt, st, &Val::Path(st.path.clone()))?;
    if !matches!(m, Val::None) {
        return Ok(m);
    }
    let print = interop::builtin("print").expect("print");
    print.call(
        vec![s("_machine: the scene is stale; running the Rust assembly driver")],
        vec![("file".into(), st.sys.attr("stderr")?)],
    )?;
    let subprocess = rt.import("subprocess")?;
    let slots = rt.import("_run_slots")?;
    let command = Val::list(vec![st.sys.attr("executable")?, s(py::path_str(&st.ml.join("enclosure_assembly.py")))]);
    let mut kwargs: Vec<(String, Val)> = vec![
        ("cwd".into(), Val::Path(st.root.clone())),
        ("stdout".into(), Val::Int(2)),
        ("check".into(), Val::Bool(true)),
    ];
    kwargs.extend(super::rt::keyword_items(py::call(&slots.attr("subprocess_kwargs")?, vec![])?)?);
    subprocess.attr("run")?.call(vec![command], kwargs)?;
    load(rt, st, &Val::Path(st.path.clone()))
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::MACHINE))?;
    ns.set("dataclasses", rt.import("dataclasses")?)?;
    ns.set("json", rt.import("json")?)?;
    let sys = rt.import("sys")?;
    ns.set("sys", sys.clone())?;
    let time = rt.import("time")?;
    ns.set("time", time.clone())?;
    let types = rt.import("types")?;
    ns.set("types", types.clone())?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    ns.set("_HERE", Val::Path(here.clone()))?;
    let root = here.ancestors().nth(3).unwrap_or(&here).to_owned();
    ns.set("_ROOT", Val::Path(root.clone()))?;
    let ml = root.join("hardware").join("manifold-layout");
    ns.set("_ML", Val::Path(ml.clone()))?;
    let path = ml.join("enclosure-assembly.scene.npz");
    ns.set("PATH", Val::Path(path.clone()))?;
    ns.set("SCHEMA", Val::Int(SCHEMA))?;
    ns.set("_GRAPH", Val::Path(root.join("tools").join("bazel").join("graph.json")))?;
    ns.set("_WORLD", s("hardware/manifold-layout/enclosure_assembly.py"))?;
    ns.set("_FALLBACK_SOURCES", Val::Tuple(
        [
            "manifold-layout/enclosure_assembly.py",
            "manifold-layout/_lines.py",
            "manifold-layout/manifold_layout.py",
            "scripts/_routing.py",
            "printed-parts/enclosure/enclosure/enclosure.py",
        ]
        .into_iter()
        .map(s)
        .collect(),
    ))?;
    ns.def(rt, "Machine.moved", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["self"], &[])?;
        moved(&*state(rt)?, &a.req("self")?)
    })?;
    ns.def(rt, "Machine.measured", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["self"], &[])?;
        measured(&*state(rt)?, &a.req("self")?)
    })?;
    let machine_type = rt.python_type(MODULE, "Machine")?;
    ns.set("Machine", machine_type.clone())?;
    rt.keep(MODULE, State { ns: ns.clone(), root, ml, path: path.clone(), time, sys, types, machine_type });
    ns.def(rt, "document", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["a", "taken", "card", "drain"], &["solids", "core"])?;
        let doc = a.req("a")?;
        let taken = a.opt("taken").unwrap_or(Val::None);
        let card = a.opt("card").unwrap_or(Val::None);
        let drain = a.opt("drain").unwrap_or(Val::None);
        let solids = a.opt("solids").unwrap_or(Val::None);
        let core = a.opt("core").unwrap_or(Val::None);
        document(&*state(rt)?, &doc, taken, card, drain, solids, core)
    })?;
    let default = Val::Path(path);
    let path_default = default.clone();
    ns.def(rt, "write_from_fine", move |rt, args, kw| {
        let mut a = py::bind(args, kw, &["model", "path"], &["aliases", "envelope", "document"])?;
        let model = a.req("model")?;
        let path = a.opt("path").unwrap_or_else(|| path_default.clone());
        let (aliases, envelope, document) = (a.req("aliases")?, a.req("envelope")?, a.req("document")?);
        write_from_fine(rt, &model, &path, aliases, &envelope, document)
    })?;
    ns.def(rt, "_tupled", |_, args, kw| {
        let mut a = py::bind(args, kw, &["value"], &[])?;
        tupled(&a.req("value")?)
    })?;
    ns.def(rt, "_run", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["row"], &[])?;
        run(rt, &a.req("row")?)
    })?;
    ns.def(rt, "_box", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["doc"], &[])?;
        boxed(rt, &a.req("doc")?)
    })?;
    let path_default = default.clone();
    ns.def(rt, "load", move |rt, args, kw| {
        let mut a = py::bind(args, kw, &["path"], &[])?;
        let path = a.opt("path").unwrap_or_else(|| path_default.clone());
        load(rt, &*state(rt)?, &path)
    })?;
    let path_default = default;
    ns.def(rt, "current", move |rt, args, kw| {
        let mut a = py::bind(args, kw, &["path"], &[])?;
        let path = a.opt("path").unwrap_or_else(|| path_default.clone());
        current(rt, &*state(rt)?, &path)
    })?;
    ns.def(rt, "machine", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        machine(rt, &*state(rt)?)
    })?;
    Ok(())
}
