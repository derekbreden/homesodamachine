//! Equipment dimensions, placements and tube recipes the machine program answers.
//!
//! Every recipe is one request to the machine program (`_rust_data.request`): the layout
//! specification, the reference parameters of the parts it places and the scalar inputs the
//! caller resolves. The frame and tube helpers answer from the layout data recipes in process.
use super::_machine_reporting::bind_rest;
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::Result;
use hsm_documents::interop::{self, Val};
use py::s;
use serde_json::{Map, Value};
use std::path::{Path, PathBuf};

/// Not yet compared with the generated build: the hybrid development build runs the generated namespace.
pub const TYPED: bool = false;

const MODULE: &str = "_machine_equipment";

struct State {
    /// The module namespace: the route recipes call `continuations` and `flavor_routes` on it.
    ns: Val,
    hw: PathBuf,
    /// `layout`: the above-core specification provider.
    layout: Val,
    /// `IDENTITY`, the namespace's own dict.
    identity: Val,
}

fn state(rt: &Rt) -> Result<std::rc::Rc<State>> {
    rt.state::<State>(MODULE)
}

/// The palette keys the equipment colors are taken from, in order.
const PALETTE: [&str; 18] = [
    "C_PCBA",
    "C_PSU",
    "C_RELAY",
    "C_C14",
    "M_BRASS",
    "C_DIGITEN",
    "C_VALVE",
    "M_DONOR_BLACK",
    "M_PETGF_BLACK",
    "M_TPU_BLACK",
    "M_JG_BLACK_PP",
    "M_NEOFIT_WHITE_ACETAL",
    "M_NEOFIT_ACETAL",
    "M_JG_WHITE_PP",
    "M_STAINLESS",
    "M_POM_ORANGE",
    "M_PVC_CLEAR",
    "M_NITRILE_BLACK",
];

/// `_request(op, **values)`: one answer from the machine program.
fn request_dict(rt: &Rt, op: Val, values: Val) -> Result<Val> {
    let call = rt.member("_rust_data", "request")?;
    let payload = Val::dict(vec![(s("op"), op)]);
    if let Val::Dict(rows) = &values {
        for (key, value) in rows.borrow().iter() {
            payload.set(key.clone(), value.clone())?;
        }
    }
    py::call(&call, vec![s("machine-data"), s("machine-data"), payload])
}

fn request(rt: &Rt, op: &str, values: Vec<(&str, Val)>) -> Result<Val> {
    request_dict(rt, s(op), Val::dict(values.into_iter().map(|(k, v)| (s(k), v)).collect()))
}

/// `_layout_data.data(op, **values)`, answered in process.
fn data(rt: &Rt, op: &str, values: Vec<(&str, Val)>) -> Result<Val> {
    let mut payload = Map::new();
    payload.insert("op".into(), Value::String(op.into()));
    for (key, value) in values {
        payload.insert(key.into(), py::plain(&value)?);
    }
    py::from_json(rt.layout_data(Value::Object(payload))?)
}

/// `dict(value)`: a mapping or a sequence of pairs, copied into a dict.
fn dict(value: &Val) -> Result<Val> {
    let value = py::snapshot(value)?;
    if matches!(value, Val::Dict(_)) {
        return Ok(value);
    }
    let out = Val::dict(vec![]);
    for item in value.iter()? {
        let pair = py::unpack(&item, 2)?;
        out.set(pair[0].clone(), pair[1].clone())?;
    }
    Ok(out)
}

/// `{name: source[name] for name in order}`.
fn pick(source: &Val, order: Vec<Val>) -> Result<Val> {
    let out = Val::dict(vec![]);
    for name in order {
        out.set(name.clone(), source.get(name)?)?;
    }
    Ok(out)
}

/// `_read(relative)`: a reference-parameter document, its read recorded.
fn read(rt: &Rt, st: &State, relative: &str) -> Result<Val> {
    let path = st.hw.join(relative);
    rt.note_read(&path)?;
    request(rt, "read_json", vec![("path", s(py::path_str(&path)))])
}

fn frame(st: &State, rotation: Val, translation: Val) -> Result<Val> {
    let rotation = if rotation.truthy()? { rotation } else { py::at(&st.identity, "rotation")? };
    let translation = if translation.truthy()? { translation } else { py::at(&st.identity, "translation_mm")? };
    Ok(py::dict([("rotation", rotation), ("translation_mm", translation)]))
}

fn specification(st: &State) -> Result<Val> {
    py::method(&st.layout, "specification", vec![])
}

/// `str(Path(input_root).resolve() / 'hardware' if input_root else HW)`.
fn inputs_hw(st: &State, input_root: &Val) -> Result<PathBuf> {
    Ok(if input_root.truthy()? { py::resolve(&py::path(input_root)?)?.join("hardware") } else { st.hw.clone() })
}

/// `_source(relative, input_root=None)`: where a placed part's model is read from.
fn source(rt: &Rt, st: &State, relative: &Val, input_root: &Val) -> Result<Val> {
    let placed = st.hw.join(relative.str()?);
    let manifest = placed.parent().unwrap_or(&placed).join("frozen-asset.json");
    if manifest.is_file() {
        rt.note_read(&manifest)?;
    }
    request(rt, "model_source", vec![
        ("mode", s("equipment")),
        ("relative", relative.clone()),
        ("authored_root", s(py::path_str(&st.hw))),
        ("input_root", s(py::path_str(&inputs_hw(st, input_root)?))),
    ])
}

fn stem(rt: &Rt, st: &State) -> Result<Val> {
    read(rt, st, "reference/neofit-stem-elbow/reference-parameters.json")
}
fn reducer(rt: &Rt, st: &State) -> Result<Val> {
    read(rt, st, "reference/jg-pp061208w/reference-parameters.json")
}
fn check(rt: &Rt, st: &State) -> Result<Val> {
    read(rt, st, "reference/neofit-acvus44-check/reference-parameters.json")
}

/// `_bfp_port(name)`: one port of the backflow preventer's reference.
fn bfp_port(rt: &Rt, st: &State, name: &str) -> Result<Val> {
    py::sys_path_insert(rt, &py::path_str(&st.hw.join("reference/multiplex-asse1022")))?;
    let reference = rt.import("multiplex_asse1022")?;
    py::method(&reference, name, vec![])
}

const CHAIN: &str = "reference/asse1022-threaded-chain/reference-parameters.json";

/// `_inputs()`: the reference parameters every placement request carries.
fn inputs(rt: &Rt, st: &State) -> Result<Val> {
    let stem = stem(rt, st)?;
    let reducer = reducer(rt, st)?;
    let check = check(rt, st)?;
    let chain = read(rt, st, CHAIN)?;
    let pump = read(rt, st, "reference/g-ganen-pump/reference-parameters.json")?;
    let jg = read(rt, st, "reference/jg-bulkhead-union/reference-parameters.json")?;
    let drain = read(rt, st, "reference/neofit-drain-bulkhead/reference-parameters.json")?;
    let ports = Val::dict(vec![]);
    for name in ["inlet", "outlet", "vent"] {
        ports.set(s(name), bfp_port(rt, st, name)?)?;
    }
    Ok(py::dict([
        ("stem", stem),
        ("reducer", reducer),
        ("check", check),
        ("chain", chain),
        ("pump", pump),
        ("jg", jg),
        ("drain", drain),
        ("multiplex_ports", ports),
    ]))
}

/// `_context(op, **values)`: a request carrying the specification and reference parameters.
fn context_dict(rt: &Rt, st: &State, op: Val, values: Val) -> Result<Val> {
    let spec = specification(st)?;
    let inputs = inputs(rt, st)?;
    let order = Val::list(py::at(&py::at(&spec, "fore_routes")?, "tubes")?.iter()?);
    let all = py::dict([("spec", spec), ("data", inputs), ("fore_tube_order", order)]);
    if let Val::Dict(rows) = &values {
        for (key, value) in rows.borrow().iter() {
            all.set(key.clone(), value.clone())?;
        }
    }
    request_dict(rt, op, all)
}

fn context(rt: &Rt, st: &State, op: &str, values: Vec<(&str, Val)>) -> Result<Val> {
    context_dict(rt, st, s(op), Val::dict(values.into_iter().map(|(k, v)| (s(k), v)).collect()))
}

fn chain_inlet(rt: &Rt, st: &State) -> Result<Val> {
    let pair = py::unpack(&context(rt, st, "equipment_chain_inlet", vec![])?, 2)?;
    Ok(Val::Tuple(vec![Val::Tuple(pair[0].iter()?), Val::Tuple(pair[1].iter()?)]))
}

fn local_ports(rt: &Rt, st: &State, name: Val) -> Result<Val> {
    let result = py::snapshot(&context(rt, st, "equipment_ports", vec![("name", name)])?)?;
    let ports = py::at(&result, "ports")?;
    let out = Val::dict(vec![]);
    for port in py::at(&result, "order")?.iter()? {
        let row = ports.get(port.clone())?;
        let point = Val::Tuple(row.get(Val::Int(0))?.iter()?);
        let axis = Val::Tuple(row.get(Val::Int(1))?.iter()?);
        out.set(port, Val::Tuple(vec![point, axis, row.get(Val::Int(2))?]))?;
    }
    Ok(out)
}

fn grid(rt: &Rt, st: &State) -> Result<Val> {
    Ok(Val::list(request(rt, "equipment_grid", vec![("spec", specification(st)?)])?.iter()?))
}

/// `_joint_numbers(port)`: the reducer joint of one refrigerant port.
pub fn joint_numbers(rt: &Rt, port: Val) -> Result<Val> {
    let st = state(rt)?;
    context(rt, &st, "equipment_joint", vec![("port", port)])
}

fn palette(rt: &Rt) -> Result<Val> {
    let materials = rt.import("_materials")?;
    let linear = materials.attr("linear")?;
    let out = Val::dict(vec![]);
    for key in PALETTE {
        out.set(s(key), Val::list(py::call(&linear, vec![materials.attr(key)?])?.iter()?))?;
    }
    Ok(out)
}

/// `numbers(external_ports=None, extra_routes=(), *, input_root=None)`: the machine program's
/// equipment request, its routes, frames and ports in authored order.
pub fn numbers(rt: &Rt, external_ports: &Val, extra_routes: &Val, input_root: &Val) -> Result<Val> {
    let st = state(rt)?;
    let soda_inlet = rt.import("soda_inlet")?;
    let materials = rt.import("_materials")?;
    let routing = rt.import("_routing")?;
    let document = rt.member("_assembly_model", "document")?;
    let sources = Val::dict(vec![]);
    for relative in request(rt, "equipment_sources", vec![])?.iter()? {
        let path = source(rt, &st, &relative, input_root)?;
        let row = py::dict([("path", path.clone())]);
        sources.set(relative, row.clone())?;
        let text = path.str()?;
        if text.ends_with(".npz") {
            let mut shown = py::method(&py::call(&document, vec![path.clone()])?, "get", vec![s("presentation")])?;
            if !shown.truthy()? {
                shown = Val::Bool(Path::new(&format!("{}.mesh", &text[..text.len() - 4])).is_file());
            }
            row.set(s("presentation"), Val::Bool(shown.truthy()?))?;
        }
    }
    let colors = palette(rt)?;
    let grey = py::call(&materials.attr("linear")?, vec![materials.attr("M_JG_GREY_ACETAL")?])?;
    colors.set(s("M_JG_GREY_ACETAL"), Val::list(grey.iter()?))?;
    let pump_path = inputs_hw(&st, input_root)?.join("printed-parts/cold-core/foam-cap/foam-cap.numbers.json");
    rt.note_read(&pump_path)?;
    let pump_cap = py::at(&request(rt, "read_json", vec![("path", s(py::path_str(&pump_path)))])?, "pump")?;
    let insulation = py::method(&soda_inlet, "plan", vec![])?;
    let soft = Val::list(soda_inlet.attr("SOFT_NEIGHBORS")?.iter()?);
    let value = context(rt, &st, "equipment_numbers", vec![
        ("external_ports", external_ports.clone()),
        ("sources", sources),
        ("colors", colors.clone()),
        ("pump_cap", pump_cap),
        ("insulation_plan", insulation),
        ("soft_neighbors", soft),
    ])?;
    let routes = if matches!(external_ports, Val::None) {
        Val::dict(vec![])
    } else {
        let recipes = rt.import("above_core_routes")?;
        let placed = value.clone();
        let station = Val::function(move |args, kwargs| {
            let mut a = py::bind(args, kwargs, &["name", "port"], &[])?;
            let (name, port) = (a.req("name")?, a.req("port")?);
            py::at(&placed, "world_ports")?.get(name)?.get(port)
        });
        py::call_kw(&recipes.attr("route_specifications")?, vec![station], vec![("plumbing", st.ns.clone())])?
    };
    let integrated_order = Val::list(routes.iter()?);
    let extra = Val::list(extra_routes.iter()?);
    let color = routing.attr("color")?;
    let linear = materials.attr("linear")?;
    let spools = Val::dict(vec![]);
    for key in routing.attr("SPOOLS")?.iter()? {
        let rgb = py::call(&linear, vec![py::call(&color, vec![key.clone()])?])?;
        spools.set(key, Val::list(rgb.iter()?))?;
    }
    let result = py::snapshot(&request(rt, "equipment_finalize", vec![
        ("equipment", value),
        ("integrated_routes", routes),
        ("integrated_order", integrated_order),
        ("extra_routes", extra),
        ("spool_colors", spools),
    ])?)?;
    let reorder = |key: &str, order: &str| -> Result<()> {
        let picked = pick(&py::at(&result, key)?, py::at(&result, order)?.iter()?)?;
        result.set(s(key), picked)
    };
    reorder("routes", "route_order")?;
    reorder("native_route_specs", "native_route_order")?;
    let port_order = py::method(&result, "pop", vec![s("_frame_port_order")])?;
    reorder("frames", "component_order")?;
    for (name, row) in entries(&py::at(&result, "frames")?)? {
        let ports = pick(&py::at(&row, "ports")?, port_order.get(name)?.iter()?)?;
        row.set(s("ports"), ports)?;
    }
    let external = if external_ports.truthy()? { external_ports.clone() } else { Val::dict(vec![]) };
    let mut world_order: Vec<Val> = vec![];
    for name in external.iter()?.into_iter().chain(py::at(&result, "component_order")?.iter()?) {
        let mut seen = false;
        for kept in &world_order {
            if interop::eq(kept, &name)? {
                seen = true;
                break;
            }
        }
        if !seen {
            world_order.push(name);
        }
    }
    let world = pick(&py::at(&result, "world_ports")?, world_order)?;
    result.set(s("world_ports"), world.clone())?;
    for (name, ports) in entries(&world)? {
        let fallback = py::method(&external, "get", vec![name.clone(), Val::dict(vec![])])?;
        let order = py::method(&port_order, "get", vec![name.clone(), fallback])?;
        world.set(name, pick(&ports, order.iter()?)?)?;
    }
    let logical = py::method(&st.layout, "logical_connections", vec![])?.iter()?;
    let connections = pick(&py::at(&result, "native_connections")?, logical)?;
    result.set(s("native_connections"), connections)?;
    let named = pick(&py::at(&result, "colors")?, colors.iter()?)?;
    result.set(s("colors"), named)?;
    let mut spool_of = None;
    for (name, route) in entries(&py::at(&result, "routes")?)? {
        if route.contains(&s("spool"))? {
            if spool_of.is_none() {
                spool_of = Some(routing.attr("SPOOL_OF")?);
            }
            spool_of.as_ref().unwrap().set(name, py::at(&route, "spool")?)?;
        }
    }
    Ok(result)
}

/// A local dict's entries.
fn entries(value: &Val) -> Result<Vec<(Val, Val)>> {
    match value {
        Val::Dict(rows) => Ok(rows.borrow().clone()),
        _ => py::method(value, "items", vec![])?
            .iter()?
            .into_iter()
            .map(|item| {
                let pair = py::unpack(&item, 2)?;
                Ok((pair[0].clone(), pair[1].clone()))
            })
            .collect(),
    }
}

/// `build(output, *, external_ports=None, extra_routes=(), input_root=None)`: the equipment's
/// fine model and its model-reference plan.
pub fn build(rt: &Rt, output: &Val, external_ports: &Val, extra_routes: &Val, input_root: &Val) -> Result<Val> {
    let rust_part = rt.import("_rust_part")?;
    py::method(&rust_part, "start", vec![])?;
    let output = py::resolve(&py::path(output)?)?;
    py::mkdirs(&output)?;
    let cut = rust_part.attr("cut")?;
    let request_numbers = numbers(rt, external_ports, extra_routes, input_root)?;
    py::call(&cut, vec![s("machine"), s("machine-equipment"), request_numbers, Val::Path(output.clone())])?;
    let plan = output.join("machine-equipment.json");
    let result = py::snapshot(&request(rt, "read_json", vec![("path", s(py::path_str(&plan)))])?)?;
    let model = s(py::path_str(&output.join("machine-equipment.step.npz")));
    for instance in py::at(&result, "instances")?.iter()? {
        instance.set(s("model"), model.clone())?;
    }
    result.set(s("model"), model)?;
    Ok(result)
}

/// The five tube continuations and four flavor ends the route recipes station.
const CONTINUATIONS: [(&str, &str); 5] = [
    ("digiten-flow", "outlet"),
    ("bulkhead-carb", "tube-in"),
    ("gas-check", "outlet"),
    ("asse-drain-adapter", "tube"),
    ("bulkhead-drain", "inboard"),
];
const FLAVORS: [(&str, &str); 4] = [
    ("valve-v-g", "outlet"),
    ("valve-v-j", "outlet"),
    ("bulkhead-flavor-a", "tube-in"),
    ("bulkhead-flavor-b", "tube-in"),
];

fn stations(station: &Val, names: &[(&str, &str)]) -> Result<Val> {
    let out = Val::dict(vec![]);
    for (name, port) in names {
        out.set(s(format!("{name}.{port}")), py::call(station, vec![s(*name), s(*port)])?)?;
    }
    Ok(out)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::MACHINE_EQUIPMENT))?;
    ns.set("cache", rt.member("functools", "cache")?)?;
    ns.set("json", rt.import("json")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("sys", rt.import("sys")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let root = here.ancestors().nth(3).unwrap_or(&here).to_owned();
    ns.set("ROOT", Val::Path(root.clone()))?;
    let hw = root.join("hardware");
    ns.set("HW", Val::Path(hw.clone()))?;
    let layout_dir = hw.join("manifold-layout");
    ns.set("LAYOUT", Val::Path(layout_dir.clone()))?;
    let text = py::path_str(&layout_dir);
    if !py::sys_path_has(rt, &text)? {
        py::sys_path_insert(rt, &text)?;
    }
    let layout = rt.import("above_core")?;
    ns.set("layout", layout.clone())?;
    ns.set("stem_elbow_names", rt.member("above_core_bom", "stem_elbow_names")?)?;
    ns.set("union_elbow_names", rt.member("above_core_bom", "union_elbow_names")?)?;
    ns.set("reservoir_gate_elbow_hosts", rt.member("above_core_bom", "reservoir_gate_elbow_hosts")?)?;
    let identity = py::dict([
        ("rotation", Val::list(vec![py::flist(&[1.0, 0.0, 0.0]), py::flist(&[0.0, 1.0, 0.0]), py::flist(&[0.0, 0.0, 1.0])])),
        ("translation_mm", py::flist(&[0.0, 0.0, 0.0])),
    ]);
    ns.set("IDENTITY", identity.clone())?;
    rt.keep(MODULE, State { ns: ns.0.clone(), hw, layout, identity });

    ns.def(rt, "_request", |rt, args, kw| {
        let (bound, values) = bind_rest(args, kw, &["op"])?;
        request_dict(rt, bound[0].clone(), values)
    })?;
    ns.def(rt, "_read", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["relative"], &[])?;
        read(rt, &*state(rt)?, &a.string("relative")?)
    })?;
    ns.def(rt, "frame", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["rotation", "translation"], &[])?;
        let rotation = a.opt("rotation").unwrap_or(Val::None);
        let translation = a.opt("translation").unwrap_or(Val::None);
        frame(&*state(rt)?, rotation, translation)
    })?;
    ns.def(rt, "compose", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["a", "b"], &[])?;
        let (first, second) = (a.req("a")?, a.req("b")?);
        request(rt, "equipment_compose", vec![("a", first), ("b", second)])
    })?;
    ns.def(rt, "transform", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["pose"], &[])?;
        request(rt, "equipment_transform", vec![("pose", a.req("pose")?)])
    })?;
    ns.def(rt, "_along_y", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["point", "axis"], &[])?;
        let (point, axis) = (a.req("point")?, a.req("axis")?);
        request(rt, "equipment_along_y", vec![("point", point), ("axis", axis)])
    })?;
    ns.def(rt, "plan", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        py::at(&specification(&*state(rt)?)?, "rear_plumbing")
    })?;
    ns.def(rt, "_source", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["relative", "input_root"], &[])?;
        let relative = a.req("relative")?;
        let input_root = a.opt("input_root").unwrap_or(Val::None);
        source(rt, &*state(rt)?, &relative, &input_root)
    })?;
    ns.def(rt, "_stem", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        stem(rt, &*state(rt)?)
    })?;
    ns.def(rt, "_reducer", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        reducer(rt, &*state(rt)?)
    })?;
    ns.def(rt, "_check", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        check(rt, &*state(rt)?)
    })?;
    ns.def(rt, "_bfp_port", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        bfp_port(rt, &*state(rt)?, &a.string("name")?)
    })?;
    ns.def(rt, "_chain_parts", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        py::at(&read(rt, &*state(rt)?, CHAIN)?, "components")
    })?;
    ns.def(rt, "_inputs", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        inputs(rt, &*state(rt)?)
    })?;
    ns.def(rt, "_context", |rt, args, kw| {
        let (bound, values) = bind_rest(args, kw, &["op"])?;
        context_dict(rt, &*state(rt)?, bound[0].clone(), values)
    })?;
    ns.def(rt, "_chain_inlet", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        chain_inlet(rt, &*state(rt)?)
    })?;
    ns.def(rt, "local_ports", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        local_ports(rt, &*state(rt)?, a.req("name")?)
    })?;
    ns.def(rt, "_grid", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        grid(rt, &*state(rt)?)
    })?;
    ns.def(rt, "_joint_numbers", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["port"], &[])?;
        joint_numbers(rt, a.req("port")?)
    })?;
    ns.def(rt, "_palette", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        palette(rt)
    })?;
    ns.def(rt, "numbers", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["external_ports", "extra_routes"], &["input_root"])?;
        let external_ports = a.opt("external_ports").unwrap_or(Val::None);
        let extra_routes = a.opt("extra_routes").unwrap_or(Val::Tuple(vec![]));
        let input_root = a.opt("input_root").unwrap_or(Val::None);
        numbers(rt, &external_ports, &extra_routes, &input_root)
    })?;
    ns.def(rt, "build", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["output"], &["external_ports", "extra_routes", "input_root"])?;
        let output = a.req("output")?;
        let external_ports = a.opt("external_ports").unwrap_or(Val::None);
        let extra_routes = a.opt("extra_routes").unwrap_or(Val::Tuple(vec![]));
        let input_root = a.opt("input_root").unwrap_or(Val::None);
        build(rt, &output, &external_ports, &extra_routes, &input_root)
    })?;
    ns.def(rt, "_reducer_insertion", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        context(rt, &*state(rt)?, "equipment_reducer_insertion", vec![])
    })?;
    ns.def(rt, "route_port_frame", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        let name = a.req("name")?;
        let spec = specification(&*state(rt)?)?;
        request(rt, "equipment_route_frame", vec![("spec", spec), ("name", name)])
    })?;
    ns.def(rt, "_offset", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["point", "vector", "length"], &[])?;
        let (point, vector) = (a.req("point")?, a.req("vector")?);
        let length = a.opt("length").unwrap_or(Val::Float(1.0));
        data(rt, "offset", vec![("point", point), ("vector", vector), ("length", length)])
    })?;
    ns.def(rt, "_link", |rt, args, kw| {
        let names = ["a", "axis_a", "depth_a", "b", "axis_b", "depth_b"];
        let mut a = py::bind(args, kw, &names, &[])?;
        let mut values = vec![];
        for name in names {
            values.push((name, a.req(name)?));
        }
        data(rt, "link", values)
    })?;
    ns.def(rt, "_line", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["a", "b"], &[])?;
        let (first, second) = (a.req("a")?, a.req("b")?);
        data(rt, "line", vec![("a", first), ("b", second)])
    })?;
    ns.def(rt, "_bezier", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["control"], &[])?;
        data(rt, "bezier", vec![("control", a.req("control")?)])
    })?;
    ns.def(rt, "_crowned_beziers", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["control", "crown", "intervals"], &[])?;
        let (control, crown) = (a.req("control")?, a.req("crown")?);
        let intervals = a.opt("intervals").unwrap_or(Val::Int(16));
        data(rt, "crowned-beziers", vec![("control", control), ("crown", crown), ("intervals", intervals)])
    })?;
    ns.def(rt, "_sample_bezier", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["control", "samples"], &[])?;
        let control = a.req("control")?;
        let samples = a.opt("samples").unwrap_or(Val::Int(65));
        data(rt, "sample-bezier", vec![("control", control), ("samples", samples)])
    })?;
    ns.def(rt, "local_routes", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        let result = py::snapshot(&context(rt, &*state(rt)?, "equipment_local_routes", vec![])?)?;
        pick(&py::at(&result, "routes")?, py::at(&result, "order")?.iter()?)
    })?;
    ns.def(rt, "_arc_three", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["points"], &[])?;
        data(rt, "arc-three", vec![("points", a.req("points")?)])
    })?;
    ns.def(rt, "_rear_routes", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        dict(&context(rt, &*state(rt)?, "equipment_rear_routes", vec![])?)
    })?;
    ns.def(rt, "continuations", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["station"], &[])?;
        let stations = stations(&a.req("station")?, &CONTINUATIONS)?;
        dict(&context(rt, &*state(rt)?, "equipment_continuations", vec![("stations", stations)])?)
    })?;
    ns.def(rt, "_flavor_s_bend", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["start", "heading", "offset", "axis"], &[])?;
        let (start, heading, offset, axis) = (a.req("start")?, a.req("heading")?, a.req("offset")?, a.req("axis")?);
        let answer = data(rt, "flavor-s-bend", vec![("start", start), ("heading", heading), ("offset", offset), ("axis", axis)])?;
        let pair = py::unpack(&answer, 2)?;
        Ok(Val::Tuple(vec![pair[0].clone(), Val::Tuple(pair[1].iter()?)]))
    })?;
    ns.def(rt, "_flavor_rear", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["flavor", "destination"], &[])?;
        let (flavor, destination) = (a.req("flavor")?, a.req("destination")?);
        data(rt, "flavor-rear", vec![("flavor", flavor), ("destination", destination)])
    })?;
    ns.def(rt, "flavor_routes", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["station"], &[])?;
        let stations = stations(&a.req("station")?, &FLAVORS)?;
        dict(&request(rt, "equipment_flavor_routes", vec![("stations", stations)])?)
    })?;
    Ok(())
}
