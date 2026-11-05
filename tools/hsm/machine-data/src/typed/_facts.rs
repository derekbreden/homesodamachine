//! What one build knows, written down so the readers do not each build it again.
//!
//! The build graph and the sources behind the assembly are answered by the machine program in
//! this process. The artifact and the scorecard are read through `_rust_data.request`, as the
//! Python surface sends it, because their documents are held by the reader's Python objects:
//! instances of the `Facts`, `_Row`, `_Frame` and `_BB` classes that surface declares.
use super::num::Num;
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::{Context, Result, bail, ensure};
use hsm_documents::interop::{self, Val};
use py::s;
use serde_json::{Value, json};
use std::path::{Path, PathBuf};
use std::rc::Rc;

/// Converted: the hybrid development build runs this module, not its generated namespace.
pub const TYPED: bool = true;

const MODULE: &str = "_facts";
const GENERATOR: &str = "hardware/manifold-layout/enclosure_assembly.py";
/// Placed port frames used by routing illustrations and bench inspection tools.
const CARD_PORT_BODIES: [&str; 15] = [
    "asse1022-assembly",
    "bulkhead-carb",
    "bulkhead-drain",
    "bulkhead-flavor-a",
    "bulkhead-flavor-b",
    "bulkhead-water",
    "digiten-flow",
    "foam-assembly",
    "vk-solenoid",
    "water-split",
    "gas-regulator",
    "gas-check",
    "jg-pp061208w",
    "suction-reducer",
    "discharge-reducer",
];
const BOX_FACT_ORDER: &str = "inner outer y_joint splits z_seam_passes front_ports back_ports east_ports \
west_ports funnel c14 east_bosses east_mount_fills side_wells floor_bosses west_cradle \
cond_cradle cond_mount cond_airway asse_cradle flow_meter_anchors tube_anchors \
ceiling_reliefs flank_reliefs front_flank_reliefs port_field nameplate valve_trays pump_trays core_stops core_holds \
vent_chase column_reliefs collet_plate pump_bay";
/// Box fields the artifact leaves out: the pack (copied field by field), the solids, and the
/// keystone (repeated as `KEYSTONE_STATION` in the constants).
const BOX_FACT_EXCLUDED: [&str; 3] = ["pack", "placed", "keystone"];

pub struct State {
    root: PathBuf,
    artifact: PathBuf,
    scorecard: PathBuf,
    step: PathBuf,
    graph: PathBuf,
    sys: Val,
    json: Val,
    realized: Val,
    /// `_BOX_FACT_ORDER` and `_BOX_FACT_EXCLUDED`: the namespace's own containers.
    order: Val,
    excluded: Val,
    /// The classes the Python surface declares.
    bb: Val,
    frame: Val,
    row: Val,
    facts: Val,
}
fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// `str(path.relative_to(base))`.
fn relative(path: &Path, base: &Path) -> Result<String> {
    Ok(py::path_str(path.strip_prefix(base)?))
}
/// `path.name`.
fn name(path: &Path) -> String {
    path.file_name().map(|v| v.to_string_lossy().into_owned()).unwrap_or_default()
}
fn text(value: &Val) -> Result<String> {
    interop::format(value, "")
}
/// `{**source}` into `target`: every key, then its value, as the runtime extends a dict.
fn extend(target: &Val, source: &Val) -> Result<()> {
    for key in source.iter()? {
        target.set(key.clone(), source.get(key)?)?;
    }
    Ok(())
}
/// The pairs of `mapping.items()`.
fn items(mapping: &Val) -> Result<Vec<(Val, Val)>> {
    py::method(mapping, "items", vec![])?
        .iter()?
        .into_iter()
        .map(|item| {
            let pair = py::unpack(&item, 2)?;
            Ok((pair[0].clone(), pair[1].clone()))
        })
        .collect()
}
fn builtin(name: &str) -> Result<Val> {
    interop::builtin(name).with_context(|| format!("{MODULE}: unknown name {name}"))
}
fn is_instance(value: &Val, kinds: &[&str]) -> Result<bool> {
    let kinds = Val::Tuple(kinds.iter().map(|kind| Val::Type((*kind).into())).collect());
    builtin("isinstance")?.call(vec![value.clone(), kinds], vec![])?.truthy()
}

// --- the sources behind the assembly ------------------------------------------------------

/// `_request(op, **values)`: one answer from the machine program, through `_rust_data.request`.
pub fn request(rt: &Rt, op: Val, values: Vec<(String, Val)>) -> Result<Val> {
    let call = rt.member("_rust_data", "request")?;
    let payload = Val::dict(vec![(s("op"), op)]);
    for (key, value) in values {
        payload.set(s(key), value)?;
    }
    py::call(&call, vec![s("machine-data"), s("machine-data"), payload])
}

/// `_read_graph()`: the build graph, noted as read; `{}` when it is not on this disk.
fn graph_document(rt: &Rt, st: &State) -> Result<Value> {
    rt.note_read(&st.graph)?;
    crate::answer(&json!({"op": "read_json", "path": py::path_str(&st.graph), "optional": true}))
}

/// `_read_graph()`.
pub fn read_graph(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    py::from_json(graph_document(rt, &st)?)
}

/// `_source_names(graph)`: the generator's source projection of a graph.
pub fn source_names(graph: &Val) -> Result<Vec<String>> {
    Ok(crate::source_names(&py::plain(graph)?))
}

/// `sources()`: what the generator reads and no generator writes, as the graph names it.
pub fn sources(rt: &Rt) -> Result<Vec<String>> {
    let st = state(rt)?;
    Ok(crate::source_names(&graph_document(rt, &st)?))
}

/// `_realized.digest` over the named sources, or None when there are none.
fn digest(st: &State, names: &[String]) -> Result<Val> {
    if names.is_empty() {
        return Ok(Val::None);
    }
    let paths = names.iter().map(|name| Val::Path(st.root.join(name))).collect();
    py::call(&st.realized.attr("digest")?, vec![Val::list(paths)])
}

/// `_source_digest(graph)`.
pub fn source_digest_of(rt: &Rt, graph: &Val) -> Result<Val> {
    let st = state(rt)?;
    digest(&st, &source_names(graph)?)
}

/// `source_digest()`: one name for what the whole of `sources()` computes.
pub fn source_digest(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let names = crate::source_names(&graph_document(rt, &st)?);
    digest(&st, &names)
}

fn names(values: Vec<String>) -> Val {
    Val::list(values.into_iter().map(s).collect())
}

// --- the writer ---------------------------------------------------------------------------

/// `_plain(v)`: a value as JSON holds it; namedtuples keep their field names.
pub fn plain(v: &Val) -> Result<Val> {
    if matches!(v, Val::None) || is_instance(v, &["bool", "int", "float", "str"])? {
        return Ok(v.clone());
    }
    if v.attr("_asdict").is_ok() {
        let out = Val::dict(vec![]);
        for (key, x) in items(&py::method(v, "_asdict", vec![])?)? {
            out.set(key, plain(&x)?)?;
        }
        return Ok(out);
    }
    if is_instance(v, &["dict"])? {
        let out = Val::dict(vec![]);
        for (key, x) in items(v)? {
            out.set(s(key.str()?), plain(&x)?)?;
        }
        return Ok(out);
    }
    if is_instance(v, &["list", "tuple", "set", "frozenset"])? {
        return Ok(Val::list(v.iter()?.iter().map(plain).collect::<Result<_>>()?));
    }
    if v.attr("x").is_ok() && v.attr("y").is_ok() && v.attr("z").is_ok() {
        let float = Val::Type("float".into());
        let mut out = vec![];
        for axis in ["x", "y", "z"] {
            out.push(float.call(vec![v.attr(axis)?], vec![])?);
        }
        return Ok(Val::list(out));
    }
    let kind = builtin("type")?.call(vec![v.clone()], vec![])?.attr("__name__")?;
    bail!("TypeError: {} has no plain form — teach `_plain` about it", text(&kind)?)
}

/// `_box_plain(box)`: the shell's own figures and the pack's stations in one row.
pub fn box_plain(rt: &Rt, shell: &Val) -> Result<Val> {
    let st = state(rt)?;
    let src = Val::dict(vec![]);
    extend(&src, &py::method(&shell.attr("pack")?, "_asdict", vec![])?)?;
    extend(&src, &py::method(shell, "_asdict", vec![])?)?;
    let set = Val::Type("set".into());
    let keys = set.call(vec![src.clone()], vec![])?;
    let order = set.call(vec![st.order.clone()], vec![])?;
    let missing = interop::binary("sub", interop::binary("sub", keys.clone(), order.clone())?, st.excluded.clone())?;
    let extra = interop::binary("sub", order, keys)?;
    if missing.truthy()? || extra.truthy()? {
        let sorted = builtin("sorted")?;
        bail!(
            "KeyError: box fact projection is stale: missing {}, extra {}",
            text(&sorted.call(vec![missing], vec![])?)?,
            text(&sorted.call(vec![extra], vec![])?)?
        );
    }
    let out = Val::dict(vec![]);
    for key in st.order.iter()? {
        out.set(key.clone(), plain(&src.get(key)?)?)?;
    }
    Ok(out)
}

/// `_tube_handoff(whole)`: the route consumer's exact metadata, bound to the fine outputs.
pub fn tube_handoff(rt: &Rt, whole: &Val) -> Result<Val> {
    let st = state(rt)?;
    rt.import("_tube_export")?;
    let mesh = rt.import("_mesh_payload")?;
    let artifact = |path: PathBuf| -> Result<Val> {
        let shown = relative(&path, &st.root)?;
        let sha = py::call(&mesh.attr("source_digest")?, vec![Val::Path(path)])?;
        Ok(py::dict([("path", s(shown)), ("sha256", sha)]))
    };
    let step = artifact(st.step.clone())?;
    let fine = artifact(PathBuf::from(format!("{}.npz", py::path_str(&st.step))))?;
    let mut scene = st.step.clone();
    scene.set_extension("scene.npz");
    let scene = artifact(scene)?;
    let routing = plain(&super::_tube_export::route_metadata(rt, whole)?)?;
    Ok(py::dict([("schema", Val::Int(1)), ("step", step), ("fine_model", fine), ("scene", scene), ("routing", routing)]))
}

/// `write(facts)`: a producer's plain facts table, written beside its scorecard.
pub fn write(rt: &Rt, facts: &Val) -> Result<Val> {
    let st = state(rt)?;
    let atomic = rt.member("_cadq_export", "_atomic_write")?;
    let dumped = py::call_kw(&st.json.attr("dumps")?, vec![facts.clone()], vec![("indent", Val::Int(1)), ("sort_keys", Val::Bool(true))])?;
    let body = interop::binary("add", dumped, s("\n"))?;
    let writer = {
        let rt = rt.clone();
        Val::function(move |args, kwargs| {
            let _frame = rt.frame(MODULE);
            let mut a = py::bind(args, kwargs, &["p"], &[])?;
            let path = Val::Type("Path".into()).call(vec![a.req("p")?], vec![])?;
            py::method(&path, "write_text", vec![body.clone()])
        })
    };
    py::call(&atomic, vec![Val::Path(st.artifact.clone()), writer])?;
    Ok(Val::Path(st.artifact.clone()))
}

// --- the reader ---------------------------------------------------------------------------

/// `min(a, b)` and `max(a, b)`: the first of equal values wins.
fn least(a: Val, b: Val) -> Result<Val> {
    Ok(if Num::of(&b)?.f() < Num::of(&a)?.f() { b } else { a })
}
fn most(a: Val, b: Val) -> Result<Val> {
    Ok(if Num::of(&b)?.f() > Num::of(&a)?.f() { b } else { a })
}

/// `_BB.add(self, other)`: the box holding both.
pub fn bb_add(rt: &Rt, me: &Val, other: &Val) -> Result<Val> {
    let st = state(rt)?;
    let mut fields = Vec::with_capacity(6);
    for (field, low) in [("xmin", true), ("ymin", true), ("zmin", true), ("xmax", false), ("ymax", false), ("zmax", false)] {
        let (a, b) = (me.attr(field)?, other.attr(field)?);
        fields.push(if low { least(a, b)? } else { most(a, b)? });
    }
    py::call(&st.bb, fields)
}

/// `self.<hi> - self.<lo>`.
fn span(me: &Val, hi: &str, lo: &str) -> Result<Val> {
    let hi = Num::of(&me.attr(hi)?)?;
    Ok(hi.sub(Num::of(&me.attr(lo)?)?).val())
}

fn bb_repr(me: &Val) -> Result<String> {
    let mut out = String::from("_BB(");
    for (axis, lead) in [("x", "x["), ("y", "] y["), ("z", "] z[")] {
        out.push_str(lead);
        out.push_str(&interop::format(&me.attr(&format!("{axis}min"))?, ".3f")?);
        out.push(',');
        out.push_str(&interop::format(&me.attr(&format!("{axis}max"))?, ".3f")?);
    }
    out.push_str("])");
    Ok(out)
}

/// `_Frame.__init__(self, d)`: one placed body's ports, `name -> (pos, axis, diam)`.
fn frame_init(me: &Val, d: &Val) -> Result<()> {
    let ports = Val::dict(vec![]);
    for (port, v) in items(d)? {
        let pos = Val::Tuple(v.get(s("pos"))?.iter()?);
        let axis = Val::Tuple(v.get(s("axis"))?.iter()?);
        ports.set(port, Val::Tuple(vec![pos, axis, v.get(s("diam"))?]))?;
    }
    me.setattr("ports", ports)
}

/// `_Row.__getattr__(self, k)`: a scorecard row's field by attribute.
pub fn row_attr(row: &Val, key: &Val) -> Result<Val> {
    match row.get(key.clone()) {
        Ok(value) => Ok(value),
        Err(_) => bail!("AttributeError: {}", key.str()?),
    }
}

/// `self._f[key]`.
fn field(me: &Val, key: &str) -> Result<Val> {
    me.attr("_f")?.get(s(key))
}
/// `_Row(self._f[key])`.
fn row_of(rt: &Rt, me: &Val, key: &str) -> Result<Val> {
    let st = state(rt)?;
    py::call(&st.row, vec![field(me, key)?])
}
/// `{k: kind(v) for k, v in self._f[key].items()}`.
fn rows_of(me: &Val, key: &str, kind: &Val) -> Result<Val> {
    let out = Val::dict(vec![]);
    for (k, v) in items(&field(me, key)?)? {
        out.set(k, py::call(kind, vec![v])?)?;
    }
    Ok(out)
}

/// `Facts.pieces`: every printed piece's row.
pub fn pieces(rt: &Rt, me: &Val) -> Result<Val> {
    let st = state(rt)?;
    rows_of(me, "pieces", &st.row)
}

/// `Facts.valve_trays`: `name -> (width, ((u, v), …))`.
fn valve_trays(me: &Val) -> Result<Val> {
    let out = Val::dict(vec![]);
    for (k, v) in items(&field(me, "valve_trays")?)? {
        let tray = py::unpack(&v, 2)?;
        let seats = tray[1].iter()?.iter().map(|seat| Ok(Val::Tuple(seat.iter()?))).collect::<Result<_>>()?;
        out.set(k, Val::Tuple(vec![tray[0].clone(), Val::Tuple(seats)]))?;
    }
    Ok(out)
}

/// `Facts.valve_tray_stations`: `(plane, sign, ((x, z), …))` per deck.
fn valve_tray_stations(me: &Val) -> Result<Val> {
    let decks = py::snapshot(&field(me, "valve_tray_stations")?)?;
    let mut out = vec![];
    for deck in decks.iter()? {
        let deck = py::unpack(&deck, 3)?;
        let seats = deck[2].iter()?.iter().map(|seat| Ok(Val::Tuple(seat.iter()?))).collect::<Result<_>>()?;
        out.push(Val::Tuple(vec![deck[0].clone(), deck[1].clone(), Val::Tuple(seats)]));
    }
    Ok(Val::Tuple(out))
}

/// `Facts.near(rid)`: what a run passes, nearest first, as `(body, gap)`.
fn near(me: &Val, rid: &Val) -> Result<Val> {
    let attempt = (|| -> Result<Val> {
        let rows = py::snapshot(&field(me, "run_near")?.get(rid.clone())?)?;
        let mut out = vec![];
        for row in rows.iter()? {
            let pair = py::unpack(&row, 2)?;
            out.push(Val::Tuple(vec![pair[0].clone(), pair[1].clone()]));
        }
        Ok(Val::list(out))
    })();
    attempt.or_else(|_| bail!("KeyError: {}'s neighbours are not recorded — add it to DECLARED_RUN_NEIGHBOURS", text(rid)?))
}

/// `Facts.bb(name)`: one placed body's optimal box.
pub fn bb(rt: &Rt, me: &Val, body: &Val) -> Result<Val> {
    let st = state(rt)?;
    let attempt = (|| -> Result<Val> {
        let bounds = field(me, "bodies")?.get(body.clone())?.iter()?;
        py::call(&st.bb, bounds)
    })();
    attempt.or_else(|_| {
        let bodies = field(me, "bodies")?;
        let count = bodies.len()?;
        let have = py::method(&s(", "), "join", vec![builtin("sorted")?.call(vec![bodies], vec![])?])?;
        bail!(
            "KeyError: {} is not among the {count} bodies the machine places — it has been renamed or dropped, and the figure reading it is stale. Have: {}",
            text(body)?,
            text(&have)?
        )
    })
}

/// `Facts.group(pick)`: the box holding every placed body `pick` accepts.
pub fn group(rt: &Rt, me: &Val, pick: &Val) -> Result<Val> {
    let mut out = Val::None;
    for body in field(me, "bodies")?.iter()? {
        if !py::call(pick, vec![body.clone()])?.truthy()? {
            continue;
        }
        let b = bb(rt, me, &body)?;
        out = if matches!(out, Val::None) { b } else { bb_add(rt, &out, &b)? };
    }
    ensure!(!matches!(out, Val::None), "ValueError: no placed body matched — this measurement has nothing in it");
    Ok(out)
}

/// `Facts.runs`: the drawn runs as the machine measured them.
pub fn runs(rt: &Rt, me: &Val) -> Result<Val> {
    let st = state(rt)?;
    let runs = py::method(&me.attr("_f")?, "get", vec![s("runs"), Val::Tuple(vec![])])?;
    Ok(Val::list(runs.iter()?.into_iter().map(|run| py::call(&st.row, vec![run])).collect::<Result<_>>()?))
}

/// `Facts.check(cid)`: the scorecard's row for one check.
pub fn check(rt: &Rt, me: &Val, cid: &Val) -> Result<Val> {
    let st = state(rt)?;
    let checks = || py::method(&me.attr("_c")?, "get", vec![s("checks"), Val::Tuple(vec![])]);
    for row in checks()?.iter()? {
        if interop::compare("eq", py::method(&row, "get", vec![s("id")])?, cid.clone())?.truthy()? {
            return py::call(&st.row, vec![row]);
        }
    }
    bail!("KeyError: {} is not among the {} checks", text(cid)?, checks()?.len()?)
}

/// `Facts.agrees_with_card()`: whether the card beside this artifact is the one it was taken beside.
pub fn agrees_with_card(rt: &Rt, me: &Val) -> Result<Val> {
    let st = state(rt)?;
    let held = py::method(&me.attr("_f")?, "get", vec![s("card")])?;
    let here = py::call(&st.realized.attr("code_digest")?, vec![Val::Path(st.scorecard.clone())])?;
    Ok(Val::Bool(interop::compare("eq", held, here)?.truthy()?))
}

/// `Facts.agrees_with_step()`: None when the STEP is not on this disk.
pub fn agrees_with_step(rt: &Rt, me: &Val) -> Result<Val> {
    let st = state(rt)?;
    let here = py::call(&st.realized.attr("code_digest")?, vec![Val::Path(st.step.clone())])?;
    if matches!(here, Val::None) {
        return Ok(Val::None);
    }
    let held = py::method(&me.attr("_f")?, "get", vec![s("step")])?;
    Ok(Val::Bool(interop::compare("eq", held, here)?.truthy()?))
}

/// `Facts.agrees_with_sources()`: None when the artifact carries no digest or the graph names none.
pub fn agrees_with_sources(rt: &Rt, me: &Val) -> Result<Val> {
    let held = py::method(&me.attr("_f")?, "get", vec![s("sources")])?;
    if matches!(held, Val::None) {
        return Ok(Val::None);
    }
    let here = source_digest(rt)?;
    if matches!(here, Val::None) {
        return Ok(Val::None);
    }
    Ok(Val::Bool(interop::compare("eq", held, here)?.truthy()?))
}

fn is_false(value: Val) -> Result<bool> {
    interop::compare("is", value, Val::Bool(false))?.truthy()
}

/// `Facts.stale()`: what this artifact names that the tree no longer holds. Empty is current.
pub fn stale(rt: &Rt, me: &Val) -> Result<Val> {
    let st = state(rt)?;
    let code_digest = |path: &Path| -> Result<Val> { py::call(&st.realized.attr("code_digest")?, vec![Val::Path(path.to_owned())]) };
    let held = |key: &str| py::method(&me.attr("_f")?, "get", vec![s(key)]);
    let mut out = vec![];
    if !agrees_with_card(rt, me)?.truthy()? {
        let (other, verb) = (s(name(&st.scorecard)), s("taken beside"));
        out.push(s(disagrees(&st, &other, &verb, &held("card")?, &code_digest(&st.scorecard)?)?));
    }
    if is_false(agrees_with_step(rt, me)?)? {
        let (other, verb) = (s(name(&st.step)), s("measured off"));
        out.push(s(disagrees(&st, &other, &verb, &held("step")?, &code_digest(&st.step)?)?));
    }
    if is_false(agrees_with_sources(rt, me)?)? {
        let artifact = name(&st.artifact);
        let holds = text(&held("sources")?)?;
        let count = sources(rt)?.len();
        let here = text(&source_digest(rt)?)?;
        out.push(s(format!(
            "{artifact} was taken from a different tree — it holds {holds} for the {count} sources behind {GENERATOR}, which stand at {here} here. The three artifacts agree with each other and describe a machine that has since moved."
        )));
    }
    Ok(Val::list(out))
}

/// `_disagrees(other, verb, held, here)`: what the facts carry for another artifact against
/// what is beside them.
fn disagrees(st: &State, other: &Val, verb: &Val, held: &Val, here: &Val) -> Result<String> {
    let artifact = name(&st.artifact);
    let (other, here) = (text(other)?, text(here)?);
    if matches!(held, Val::None) {
        return Ok(format!("{artifact} carries no digest for {other}; {other} here is {here}"));
    }
    Ok(format!("{artifact} was {} a different {other} — it holds {}, {other} here is {here}", text(verb)?, text(held)?))
}

/// `read()`: the artifact and the scorecard behind one `Facts`.
pub fn read(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    if !st.artifact.is_file() {
        bail!(
            "FileNotFoundError: {} is not written — run tools/cad-venv/bin/python hardware/manifold-layout/enclosure_assembly.py",
            relative(&st.artifact, &st.root)?
        );
    }
    rt.note_read(&st.artifact)?;
    rt.note_read(&st.scorecard)?;
    let document = |path: &Path| request(rt, s("read_json"), vec![("path".into(), s(py::path_str(path)))]);
    let facts = document(&st.artifact)?;
    let card = document(&st.scorecard)?;
    py::call(&st.facts, vec![facts, card])
}

/// `Facts(facts, card)` over a copy of another's documents with `sources` set or left out.
fn facts_with(st: &State, f: &Val, sources: Option<Val>) -> Result<Val> {
    let document = Val::dict(vec![]);
    match &sources {
        None => {
            for (key, value) in items(&f.attr("_f")?)? {
                if interop::compare("ne", key.clone(), s("sources"))?.truthy()? {
                    document.set(key, value)?;
                }
            }
        }
        Some(here) => {
            extend(&document, &f.attr("_f")?)?;
            document.set(s("sources"), here.clone())?;
        }
    }
    py::call(&st.facts, vec![document, f.attr("_c")?])
}

fn mentions_tree(line: &Val) -> Result<bool> {
    interop::compare("in", s("different tree"), line.clone())?.truthy()
}

/// `selftest()`: the reader over this tree's artifact, and the source digest over made-up ones.
pub fn selftest(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let f = read(rt)?;
    let outer = || row_attr(&row_of(rt, &f, "box")?, &s("outer"));
    let placed = || row_attr(&row_of(rt, &f, "pack")?, &s("placed"));
    ensure!(outer()?.truthy()?, "the box states no outer bound");
    ensure!(placed()?.truthy()?, "no placed bodies");
    ensure!(row_attr(&check(rt, &f, &s("clearance-floor"))?, &s("status"))?.truthy()?, "the card carries no clearance-floor verdict");
    ensure!(pieces(rt, &f)?.truthy()?, "no printed pieces");
    rt.print(format!("  the box states an outer bound of {}", text(&outer()?)?))?;
    let (bodies, printed, drawn) = (placed()?.len()?, pieces(rt, &f)?.len()?, runs(rt, &f)?.len()?);
    rt.print(format!("  {bodies} placed bodies, {printed} printed pieces, {drawn} runs"))?;
    rt.print(format!("  declared gaps: {}", text(&field(&f, "gaps")?)?))?;
    rt.print(format!("  artifact and card agree on the tree: {}", text(&agrees_with_card(rt, &f)?)?))?;

    let silent = facts_with(&st, &f, None)?;
    ensure!(
        matches!(agrees_with_sources(rt, &silent)?, Val::None),
        "an artifact carrying no source digest reads as a fault instead of a silence"
    );
    let mut flagged = false;
    for line in stale(rt, &silent)?.iter()? {
        flagged |= mentions_tree(&line)?;
    }
    ensure!(!flagged, "an artifact silent about its sources is reported stale for it");
    let graph = read_graph(rt)?;
    let found = names(source_names(&graph)?);
    let index = relative(&st.graph, &st.root)?;
    ensure!(interop::compare("not_in", s(index), found)?.truthy()?, "the whole build graph is treated as an enclosure source");
    let foreign = Val::dict(vec![]);
    extend(&foreign, &graph)?;
    let fixture = py::dict([
        ("reads", Val::list(vec![s("selftest/unrelated-fixture-input.py")])),
        ("writes", Val::list(vec![s("selftest/unrelated-fixture.step")])),
    ]);
    foreign.set(s("selftest/unrelated-fixture.py"), fixture)?;
    ensure!(
        interop::compare("eq", source_digest_of(rt, &foreign)?, source_digest_of(rt, &graph)?)?.truthy()?,
        "an unrelated generator changes the enclosure source digest"
    );
    let here = source_digest_of(rt, &graph)?;
    if !matches!(here, Val::None) {
        let fresh = facts_with(&st, &f, Some(here.clone()))?;
        let moved = facts_with(&st, &f, Some(s("0".repeat(32))))?;
        ensure!(
            interop::compare("is", agrees_with_sources(rt, &fresh)?, Val::Bool(true))?.truthy()?,
            "a source digest naming this tree does not read current"
        );
        ensure!(is_false(agrees_with_sources(rt, &moved)?)?, "a source digest naming another tree reads current");
        let mut any = false;
        for line in stale(rt, &moved)?.iter()? {
            any |= mentions_tree(&line)?;
        }
        ensure!(any, "a tree that has moved writes no line a reader can act on");
        rt.print(format!("  {} sources behind {GENERATOR} name this tree {}", sources(rt)?.len(), text(&here)?))?;
    } else {
        rt.print(format!("  no source digest: {} names no {GENERATOR}", relative(&st.graph, &st.root)?))?;
    }
    rt.print("_facts selftest OK".into())?;
    Ok(Val::None)
}

/// `main(argv)`: exit 2 when the facts no longer describe this tree.
pub fn main(rt: &Rt, argv: &Val) -> Result<Val> {
    let st = state(rt)?;
    if interop::compare("in", s("selftest"), argv.clone())?.truthy()? {
        return selftest(rt);
    }
    if interop::compare("in", s("--write"), argv.clone())?.truthy()? {
        py::call(&st.sys.attr("exit")?, vec![s("Facts are written by hardware/manifold-layout/enclosure_assembly.py")])?;
    }
    let facts = read(rt)?;
    let lines = stale(rt, &facts)?;
    if lines.truthy()? {
        let joined = py::method(&s("\n"), "join", vec![lines])?;
        builtin("print")?.call(vec![joined], vec![("file".into(), st.sys.attr("stderr")?)])?;
        return Ok(Val::Int(2));
    }
    rt.print("the facts describe this tree's assembly outputs".into())?;
    Ok(Val::Int(0))
}

/// `sys.exit(main(sys.argv[1:]) or 0)`.
pub fn main_block(rt: &Rt) -> Result<()> {
    let st = state(rt)?;
    let argv = st.sys.attr("argv")?.get(Val::Slice { start: Some(1), stop: None, step: 1 })?;
    let code = main(rt, &argv)?;
    let code = if code.truthy()? { code } else { Val::Int(0) };
    py::call(&st.sys.attr("exit")?, vec![code])?;
    Ok(())
}

/// A method of one of the surface's classes that takes only `self`.
fn def_self(ns: &Ns, rt: &Rt, name: &str, f: impl Fn(&Rt, &Val) -> Result<Val> + 'static) -> Result<()> {
    ns.def(rt, name, move |rt, args, kw| {
        let mut a = py::bind(args, kw, &["self"], &[])?;
        f(rt, &a.req("self")?)
    })
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::FACTS))?;
    let json = rt.import("json")?;
    ns.set("json", json.clone())?;
    let sys = rt.import("sys")?;
    ns.set("sys", sys.clone())?;
    let path_type = rt.member("pathlib", "Path")?;
    ns.set("Path", path_type.clone())?;
    let here = py::method(&py::call(&path_type, vec![ns.get("__file__")?])?, "resolve", vec![])?;
    ns.set("_HERE", here.clone())?;
    let hw = here.attr("parent")?.attr("parent")?;
    ns.set("_HW", hw.clone())?;
    let root = hw.attr("parent")?;
    ns.set("_ROOT", root.clone())?;
    let (hw, root) = (py::path(&hw)?, py::path(&root)?);
    let reference = hw.join("reference");
    for folder in [
        hw.join("scripts"),
        hw.join("manifold-layout"),
        hw.join("printed-parts").join("enclosure").join("enclosure"),
        reference.join("digiten-flow-sensor"),
        reference.join("wr1110-regulator"),
        reference.join("jg-bulkhead-union"),
    ] {
        ns.set("_p", Val::Path(folder.clone()))?;
        let text = py::path_str(&folder);
        if !py::sys_path_has(rt, &text)? {
            py::sys_path_insert(rt, &text)?;
        }
    }
    let realized = rt.import("_realized")?;
    ns.set("_realized", realized.clone())?;
    let layout = hw.join("manifold-layout");
    let artifact = layout.join("enclosure-assembly.facts.json");
    ns.set("ARTIFACT", Val::Path(artifact.clone()))?;
    let scorecard = layout.join("enclosure-assembly.scorecard.json");
    ns.set("SCORECARD", Val::Path(scorecard.clone()))?;
    let step = layout.join("enclosure-assembly.step");
    ns.set("STEP", Val::Path(step.clone()))?;
    ns.set("SCHEMA", Val::Int(2))?;
    let graph = root.join("tools").join("bazel").join("graph.json");
    ns.set("GRAPH", Val::Path(graph.clone()))?;
    ns.set("GENERATOR", s(GENERATOR))?;

    ns.def(rt, "_request", |rt, args, mut kw| {
        let named = kw.iter().position(|(key, _)| key == "op");
        let mut positional = args.into_iter();
        let op = match (positional.next(), named) {
            (Some(_), Some(_)) => bail!("multiple arguments for op"),
            (Some(op), None) => op,
            (None, Some(index)) => kw.remove(index).1,
            (None, None) => bail!("missing argument op"),
        };
        ensure!(positional.next().is_none(), "too many positional arguments");
        request(rt, op, kw)
    })?;
    ns.def(rt, "_read_graph", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        read_graph(rt)
    })?;
    ns.def(rt, "_source_names", |_, args, kw| {
        let mut a = py::bind(args, kw, &["graph"], &[])?;
        Ok(names(source_names(&a.req("graph")?)?))
    })?;
    ns.def(rt, "sources", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(names(sources(rt)?))
    })?;
    ns.def(rt, "_source_digest", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["graph"], &[])?;
        source_digest_of(rt, &a.req("graph")?)
    })?;
    ns.def(rt, "source_digest", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        source_digest(rt)
    })?;
    ns.set("DECLARED_GAPS", Val::Tuple(vec![]))?;
    ns.set("DECLARED_RUN_NEIGHBOURS", Val::Tuple(vec![]))?;
    ns.set("CARD_PORT_BODIES", py::tuple(CARD_PORT_BODIES.map(s)))?;
    ns.def(rt, "_plain", |_, args, kw| {
        let mut a = py::bind(args, kw, &["v"], &[])?;
        plain(&a.req("v")?)
    })?;
    let order = Val::list(BOX_FACT_ORDER.split_whitespace().map(s).collect());
    ns.set("_BOX_FACT_ORDER", order.clone())?;
    let excluded = Val::set_values(BOX_FACT_EXCLUDED.map(s).to_vec());
    ns.set("_BOX_FACT_EXCLUDED", excluded.clone())?;
    ns.def(rt, "_box_plain", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["box"], &[])?;
        box_plain(rt, &a.req("box")?)
    })?;
    ns.def(rt, "_tube_handoff", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["whole"], &[])?;
        tube_handoff(rt, &a.req("whole")?)
    })?;
    ns.def(rt, "write", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["facts"], &[])?;
        write(rt, &a.req("facts")?)
    })?;

    ns.def(rt, "_BB.__init__", |_, args, kw| {
        let fields = ["xmin", "ymin", "zmin", "xmax", "ymax", "zmax"];
        let mut a = py::bind(args, kw, &["self", "xmin", "ymin", "zmin", "xmax", "ymax", "zmax"], &[])?;
        let me = a.req("self")?;
        let values = fields.iter().map(|field| a.req(field)).collect::<Result<Vec<_>>>()?;
        for (field, value) in fields.iter().zip(values) {
            me.setattr(field, value)?;
        }
        Ok(Val::None)
    })?;
    ns.def(rt, "_BB.add", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["self", "other"], &[])?;
        bb_add(rt, &a.req("self")?, &a.req("other")?)
    })?;
    def_self(ns, rt, "_BB.xlen", |_, me| span(me, "xmax", "xmin"))?;
    def_self(ns, rt, "_BB.ylen", |_, me| span(me, "ymax", "ymin"))?;
    def_self(ns, rt, "_BB.zlen", |_, me| span(me, "zmax", "zmin"))?;
    def_self(ns, rt, "_BB.__repr__", |_, me| Ok(s(bb_repr(me)?)))?;
    let bb_type = rt.python_type(MODULE, "_BB")?;
    ns.set("_BB", bb_type.clone())?;
    ns.def(rt, "_Frame.__init__", |_, args, kw| {
        let mut a = py::bind(args, kw, &["self", "d"], &[])?;
        frame_init(&a.req("self")?, &a.req("d")?)?;
        Ok(Val::None)
    })?;
    let frame_type = rt.python_type(MODULE, "_Frame")?;
    ns.set("_Frame", frame_type.clone())?;
    ns.def(rt, "_Row.__getattr__", |_, args, kw| {
        let mut a = py::bind(args, kw, &["self", "k"], &[])?;
        row_attr(&a.req("self")?, &a.req("k")?)
    })?;
    let row_type = rt.python_type(MODULE, "_Row")?;
    ns.set("_Row", row_type.clone())?;

    ns.def(rt, "Facts.__init__", |_, args, kw| {
        let mut a = py::bind(args, kw, &["self", "facts", "card"], &[])?;
        let (me, facts, card) = (a.req("self")?, a.req("facts")?, a.req("card")?);
        me.setattr("_f", facts)?;
        me.setattr("_c", card)?;
        Ok(Val::None)
    })?;
    def_self(ns, rt, "Facts.box", |rt, me| row_of(rt, me, "box"))?;
    def_self(ns, rt, "Facts.pack", |rt, me| row_of(rt, me, "pack"))?;
    def_self(ns, rt, "Facts.wall_ports", |rt, me| row_of(rt, me, "wall_ports"))?;
    def_self(ns, rt, "Facts.pieces", pieces)?;
    def_self(ns, rt, "Facts.valve_trays", |_, me| valve_trays(me))?;
    def_self(ns, rt, "Facts.valve_tray_stations", |_, me| valve_tray_stations(me))?;
    def_self(ns, rt, "Facts.pump_trays", |_, me| Val::Type("dict".into()).call(vec![field(me, "pump_trays")?], vec![]))?;
    def_self(ns, rt, "Facts.gaps", |_, me| field(me, "gaps"))?;
    def_self(ns, rt, "Facts.faces", |_, me| field(me, "faces"))?;
    def_self(ns, rt, "Facts.card_ports", |rt, me| rows_of(me, "card_ports", &state(rt)?.frame))?;
    def_self(ns, rt, "Facts.carried_points", |rt, me| rows_of(me, "carried_points", &state(rt)?.row))?;
    def_self(ns, rt, "Facts.card_digest", |_, me| field(me, "card"))?;
    def_self(ns, rt, "Facts.constants", |rt, me| row_of(rt, me, "constants"))?;
    def_self(ns, rt, "Facts.hopper_hole", |_, me| field(me, "hopper_hole"))?;
    def_self(ns, rt, "Facts.manifold_bodies", |_, me| field(me, "manifold_bodies"))?;
    def_self(ns, rt, "Facts.mouths", |_, me| field(me, "mouths"))?;
    ns.def(rt, "Facts.near", |_, args, kw| {
        let mut a = py::bind(args, kw, &["self", "rid"], &[])?;
        near(&a.req("self")?, &a.req("rid")?)
    })?;
    def_self(ns, rt, "Facts.bodies", |_, me| field(me, "bodies"))?;
    ns.def(rt, "Facts.bb", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["self", "name"], &[])?;
        bb(rt, &a.req("self")?, &a.req("name")?)
    })?;
    ns.def(rt, "Facts.group", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["self", "pick"], &[])?;
        group(rt, &a.req("self")?, &a.req("pick")?)
    })?;
    def_self(ns, rt, "Facts.runs", runs)?;
    ns.def(rt, "Facts.check", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["self", "cid"], &[])?;
        check(rt, &a.req("self")?, &a.req("cid")?)
    })?;
    def_self(ns, rt, "Facts.agrees_with_card", agrees_with_card)?;
    def_self(ns, rt, "Facts.agrees_with_step", agrees_with_step)?;
    def_self(ns, rt, "Facts.agrees_with_sources", agrees_with_sources)?;
    def_self(ns, rt, "Facts.stale", stale)?;
    let facts_type = rt.python_type(MODULE, "Facts")?;
    ns.set("Facts", facts_type.clone())?;

    ns.def(rt, "_disagrees", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["other", "verb", "held", "here"], &[])?;
        let (other, verb, held, here) = (a.req("other")?, a.req("verb")?, a.req("held")?, a.req("here")?);
        let st = state(rt)?;
        Ok(s(disagrees(&st, &other, &verb, &held, &here)?))
    })?;
    ns.def(rt, "read", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        read(rt)
    })?;
    ns.def(rt, "selftest", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        selftest(rt)
    })?;
    ns.def(rt, "main", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["argv"], &[])?;
        main(rt, &a.req("argv")?)
    })?;
    rt.keep(
        MODULE,
        State {
            root,
            artifact,
            scorecard,
            step,
            graph,
            sys,
            json,
            realized,
            order,
            excluded,
            bb: bb_type,
            frame: frame_type,
            row: row_type,
            facts: facts_type,
        },
    );
    Ok(())
}
