//! Reference frames, port stations and tube routes in the above-core arrangement.
//!
//! Purchased references remain exterior layout geometry. The frame and tube recipes are the layout
//! data recipes, answered in process; the reference modules and the rear plumbing are providers.
use super::rt::{Ns, Rt};
use super::{above_core_bom, docs, py};
use anyhow::{Context, Result, anyhow, bail};
use hsm_documents::interop::{self, Val};
use py::s;
use serde_json::{Map, Value};
use std::path::PathBuf;
use std::rc::Rc;

/// Converted: the hybrid development build runs this module, not its generated namespace.
pub const TYPED: bool = true;

const MODULE: &str = "above_core_parts";

/// Reference models declared alongside the production arrangement data.
const REFERENCES: [(&str, &str); 16] = [
    ("pcba", "printed-parts/electronics/pcba-tray/pcba-board.step"),
    ("psu", "reference/meanwell-irm90/meanwell-irm90.step"),
    ("relay-1", "reference/teyleten-relay/teyleten-relay.step"),
    ("relay-2", "reference/teyleten-relay/teyleten-relay.step"),
    ("c14-inlet", "reference/iec-c14-inlet/iec-c14-inlet.step"),
    ("keystone-jack", "reference/riteav-keystone/riteav-keystone.step"),
    ("asse1022-assembly", "reference/multiplex-asse1022/multiplex-asse1022.step"),
    ("discharge-chain", "reference/neofit-acvus44-check/neofit-acvus44-check.step"),
    ("valve", "reference/beduan-solenoid/beduan-solenoid.step"),
    ("water-split", "reference/branch-stem-tees/neofit-atbu444-e-estimate.step"),
    ("stem-elbow", "reference/neofit-stem-elbow/neofit-stem-elbow.step"),
    ("jg-turn-elbow", "reference/jg-pp0308e-elbow/jg-pp0308e-elbow.step"),
    ("flow-regulator", "reference/yzmsz-water-regulator/geometry/yzmsz-water-regulator.step"),
    ("gas-regulator", "reference/compact-inline-candidates/geometry/candidate-regulator.step"),
    ("gas-check", "reference/neofit-acvus44-check/neofit-acvus44-check.step"),
    ("digiten-flow", "reference/digiten-flow-sensor/digiten-flow-sensor.step"),
];
/// The reference modules loaded by file: `(module name, path under hardware/)`.
const CHECK_REFERENCE: (&str, &str) = ("above_core_achv44", "reference/neofit-achv44-check/neofit_achv44_check.py");
const TEE_REFERENCE: (&str, &str) = ("above_core_pp0208e", "reference/tee-connector/tee_connector.py");
const STEM_ELBOW_REFERENCE: (&str, &str) = ("above_core_ateu44w", "reference/neofit-stem-elbow/neofit_stem_elbow.py");
const GAS_BULKHEAD: (&str, &str) = ("above_core_co2_bulkhead", "reference/neofit-bulkhead/neofit_bulkhead.py");
const WATER_BULKHEAD: (&str, &str) = ("above_core_water_bulkhead", "reference/jg-bulkhead-union/jg_bulkhead_union.py");
const FOUR_BULKHEAD: (&str, &str) = ("above_core_four_bulkhead", "reference/neofit-drain-bulkhead/neofit_drain_bulkhead.py");
const VENT_ADAPTER: (&str, &str) = ("above_core_vent_adapter", "printed-parts/asse-drain-adapter/asse_drain_adapter.py");

/// A native port: position, outward axis and tube diameter.
type Station = ([f64; 3], [f64; 3], f64);
const VALVE_PORTS: [(&str, Station); 2] = [
    ("inlet", ([0., -29.75, 11.05], [0., -1., 0.], 6.35)),
    ("outlet", ([0., 29.75, 11.05], [0., 1., 0.], 6.35)),
];
const WATER_SPLIT_PORTS: [(&str, Station); 4] = [
    ("supply", ([0., 6.0452, 0.], [0., 1., 0.], 6.35)),
    ("stem-tip", ([0., 21.0452, 0.], [0., 1., 0.], 6.35)),
    ("to-vk", ([20.1041, 0., 0.], [1., 0., 0.], 6.35)),
    ("to-flavor", ([-20.1041, 0., 0.], [-1., 0., 0.], 6.35)),
];
/// The stem elbow socket's tube diameter.
const SOCKET_TUBE: f64 = 6.35;

pub struct State {
    hw: PathBuf,
    importlib: Val,
    sys: Val,
    layout: Val,
    origin: Val,
}
fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// `_layout_data.data(op, **values)`, answered in process. A refused recipe reads as the
/// transport raises it: `ValueError: layout-data: <the recipe's error chain>`.
fn layout_data(rt: &Rt, op: &str, values: &[(&str, &Val)]) -> Result<Value> {
    let mut payload = Map::new();
    payload.insert("op".into(), Value::String(op.into()));
    for (key, value) in values {
        payload.insert((*key).into(), py::plain(value)?);
    }
    rt.layout_data(Value::Object(payload)).map_err(|error| anyhow!("ValueError: layout-data: {error:#}"))
}
fn data(rt: &Rt, op: &str, values: &[(&str, &Val)]) -> Result<Val> {
    py::from_json(layout_data(rt, op, values)?)
}

/// A reference module executed from its file under `hardware/`, registered in `sys.modules`.
pub fn load_module(rt: &Rt, name: &Val, relative: &Val) -> Result<Val> {
    let st = state(rt)?;
    let location = Val::Path(st.hw.join(relative.str()?));
    let spec = py::call(&st.importlib.attr("util")?.attr("spec_from_file_location")?, vec![name.clone(), location])?;
    let result = py::call(&st.importlib.attr("util")?.attr("module_from_spec")?, vec![spec.clone()])?;
    st.sys.attr("modules")?.set(name.clone(), result.clone())?;
    py::call(&spec.attr("loader")?.attr("exec_module")?, vec![result.clone()])?;
    Ok(result)
}
fn reference(rt: &Rt, (name, relative): (&str, &str)) -> Result<Val> {
    load_module(rt, &s(name), &s(relative))
}
/// One ACHV44-E native frame and insertion estimate for water and CO2.
pub fn check_reference(rt: &Rt) -> Result<Val> {
    reference(rt, CHECK_REFERENCE)
}
/// The measured PP0208E: Y-A and Y-B take their stems to its tube stop.
pub fn tee_reference(rt: &Rt) -> Result<Val> {
    reference(rt, TEE_REFERENCE)
}
/// The scan-fitted ATEU44W: its socket release face and stem shoulder.
pub fn stem_elbow_reference(rt: &Rt) -> Result<Val> {
    reference(rt, STEM_ELBOW_REFERENCE)
}

pub fn frame(rotation: Val, translation: Val) -> Val {
    py::dict([("rotation", rotation), ("translation_mm", translation)])
}

/// The JSON items `tuple(value)` takes.
fn items(value: &Value) -> Result<Vec<Val>> {
    match value {
        Value::Array(rows) => rows.iter().cloned().map(py::from_json).collect(),
        Value::Object(rows) => Ok(rows.keys().map(|k| s(k.clone())).collect()),
        other => bail!("value is not iterable: {other}"),
    }
}
fn field<'a>(value: &'a Value, name: &str) -> Result<&'a Value> {
    value.get(name).with_context(|| format!("missing key '{name}'"))
}

/// `outer` composed with `inner`, as a frame of tuples.
pub fn compose(rt: &Rt, outer: &Val, inner: &Val) -> Result<Val> {
    let result = layout_data(rt, "compose", &[("outer", outer), ("inner", inner)])?;
    let rows = field(&result, "rotation")?.as_array().context("value is not iterable")?;
    let rotation = rows.iter().map(|row| Ok(Val::Tuple(items(row)?))).collect::<Result<Vec<_>>>()?;
    let translation = items(field(&result, "translation_mm")?)?;
    Ok(frame(Val::Tuple(rotation), Val::Tuple(translation)))
}

/// A snapshot pose, optionally composed with a local frame.
pub fn snapshot_pose(rt: &Rt, name: &Val, local: &Val) -> Result<Val> {
    let st = state(rt)?;
    let pose = py::call(&st.layout.attr("snapshot_pose")?, vec![name.clone()])?;
    if matches!(local, Val::None) { Ok(pose) } else { compose(rt, &pose, local) }
}

fn named(name: &Val, text: &str) -> bool {
    matches!(name, Val::Str(n) if n == text)
}

/// Reference port frame of a fitting in the short above-core tube routes.
pub fn route_port_frame(rt: &Rt, name: &Val) -> Result<Val> {
    if named(name, "suction-reducer") {
        let plan = py::call(&rt.import("rear_plumbing")?.attr("plan")?, vec![])?;
        let joint = plan.get(s("suction-joint"))?;
        let end = plan.get(s("joint"))?.get(s("suction_bend"))?.get(s("end_frame"))?;
        return compose(rt, &joint, &end);
    }
    let snapshot = if named(name, "flow-regulator") { s("reg") } else { name.clone() };
    snapshot_pose(rt, &snapshot, &Val::None)
}

pub fn grid(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let spec = py::call(&st.layout.attr("specification")?, vec![])?;
    data(rt, "grid", &[("spec", &spec)])
}

/// The bulkhead reference a grid row's native kind names.
pub fn grid_module(rt: &Rt, row: &Val) -> Result<Val> {
    let kind = row.get(s("native_kind"))?;
    if named(&kind, "gas") {
        return reference(rt, GAS_BULKHEAD);
    }
    if named(&kind, "quarter") {
        return reference(rt, WATER_BULKHEAD);
    }
    reference(rt, FOUR_BULKHEAD)
}

fn station(at: Val, axis: [f64; 3], diameter: f64) -> Val {
    Val::Tuple(vec![at, py::ftuple(&axis), Val::Float(diameter)])
}
fn stations(rows: &[(&str, Station)]) -> Val {
    py::dict(rows.iter().map(|(port, (at, axis, d))| (*port, station(py::ftuple(at), *axis, *d))))
}
/// `(*point_and_axis, diameter)`.
fn extended(point_and_axis: &Val, diameter: f64) -> Result<Val> {
    let mut row = point_and_axis.iter()?;
    row.push(Val::Float(diameter));
    Ok(Val::Tuple(row))
}

/// Selected reference's native `port -> (position, axis, diameter)`.
///
/// The ASSE aliases describe its metal connections. The threaded adapters, union tee and stem
/// checks expose their own native interfaces separately.
pub fn port_stations(rt: &Rt, name: &Val) -> Result<Val> {
    let st = state(rt)?;
    let rear_plumbing = rt.import("rear_plumbing")?;
    let rear = py::call(&rear_plumbing.attr("ports")?, vec![name.clone()])?;
    if !matches!(rear, Val::None) {
        return Ok(rear);
    }
    let text = match name {
        Val::Str(n) => Some(n.as_str()),
        _ => None,
    };
    let socket = || -> Result<Val> {
        let socket = py::method(&stem_elbow_reference(rt)?, "socket", vec![])?;
        Ok(py::dict([("socket", extended(&socket, SOCKET_TUBE)?)]))
    };
    let elbows = above_core_bom::stem_elbow_names(rt)?;
    if text.is_some_and(|n| elbows.iter().any(|elbow| elbow == n)) {
        return socket();
    }
    let hosts = above_core_bom::reservoir_gate_elbow_hosts(rt)?;
    if text.is_some_and(|n| hosts.iter().any(|(host, _)| host == n)) {
        return socket();
    }
    let bfp = |port: &str| -> Result<Val> {
        let chain = py::call(&rear_plumbing.attr("chain")?, vec![])?;
        py::method(&chain.attr("bfp")?, port, vec![])
    };
    match text {
        Some("valve-v-a" | "valve-v-b" | "vk-solenoid") => return Ok(stations(&VALVE_PORTS)),
        Some("asse1022-assembly") => {
            let tube_in = extended(&bfp("inlet")?, 17.15)?;
            let tube_out = extended(&bfp("outlet")?, 15.88)?;
            let vent = extended(&bfp("vent")?, 7.7)?;
            return Ok(py::dict([("tube-in", tube_in), ("tube-out", tube_out), ("vent-tip", vent)]));
        }
        Some("water-split") => return Ok(stations(&WATER_SPLIT_PORTS)),
        Some("flow-regulator") => {
            return Ok(py::dict([
                ("inlet", station(st.origin.clone(), [-1., 0., 0.], 6.35)),
                ("outlet", station(py::ftuple(&[68.117, 0., 0.]), [1., 0., 0.], 6.35)),
            ]));
        }
        Some("gas-regulator") => {
            return Ok(py::dict([
                ("inlet", station(st.origin.clone(), [0., 0., -1.], 6.35)),
                ("outlet", station(py::ftuple(&[0., 0., 62.4]), [0., 0., 1.], 6.35)),
            ]));
        }
        Some(n @ ("gas-check" | "discharge-chain")) => {
            let native = py::snapshot(&py::method(&check_reference(rt)?, "ports", vec![])?)?;
            let ports = Val::dict(vec![]);
            for key in native.iter()? {
                let row = native.get(key.clone())?;
                ports.set(key, Val::Tuple(vec![row.get(s("position"))?, row.get(s("outward"))?, row.get(s("tube_od_mm"))?]))?;
            }
            if n == "discharge-chain" {
                ports.set(s("tube-port"), ports.get(s("outlet"))?)?;
            }
            return Ok(ports);
        }
        _ => {}
    }
    let Some(n) = text else {
        // `name.startswith(...)` on a value that is not text.
        return py::method(name, "startswith", vec![s("asse-")]).map(|_| Val::None);
    };
    if n.starts_with("asse-") && n.ends_with("-tpu") {
        let inlet = n == "asse-inlet-tpu";
        let at = py::ftuple(&[if inlet { -20. } else { 85. }, 0., 0.]);
        return Ok(py::dict([("tube", station(at, [if inlet { -1. } else { 1. }, 0., 0.], 6.35))]));
    }
    if n == "asse-drain-adapter" {
        let adapter = reference(rt, VENT_ADAPTER)?;
        let mouth = py::method(&adapter, "tube_mouth", vec![bfp("vent")?.get(Val::Int(0))?])?;
        return Ok(py::dict([("tube", station(mouth, [-1., 0., 0.], 4.))]));
    }
    Ok(Val::None)
}

/// Rust native tube recipes, with the rear reference ports supplied by their provider.
pub fn route_specs(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let rear = py::call(&rt.import("rear_plumbing")?.attr("route_specs")?, vec![])?;
    let spec = py::snapshot(&py::call(&st.layout.attr("specification")?, vec![])?)?;
    let order = Val::list(spec.get(s("fore_routes"))?.get(s("tubes"))?.iter()?);
    let rear = py::snapshot(&rear)?;
    let rear_order = Val::list(rear.iter()?);
    let result = layout_data(rt, "fore-routes", &[("spec", &spec), ("rear", &rear), ("order", &order), ("rear_order", &rear_order)])?;
    dict_from(result)
}

/// `dict(answer)`: an object's items, or an array's `[key, value]` pairs, in order.
fn dict_from(answer: Value) -> Result<Val> {
    let out = Val::dict(vec![]);
    match answer {
        Value::Object(rows) => {
            for (key, value) in rows {
                out.set(s(key), py::from_json(value)?)?;
            }
        }
        Value::Array(rows) => {
            for (index, row) in rows.into_iter().enumerate() {
                let Value::Array(pair) = row else {
                    bail!("TypeError: cannot convert dictionary update sequence element #{index} to a sequence");
                };
                let [key, value]: [Value; 2] = pair.try_into().map_err(|pair: Vec<Value>| {
                    anyhow!("ValueError: dictionary update sequence element #{index} has length {}; 2 is required", pair.len())
                })?;
                out.set(py::from_json(key)?, py::from_json(value)?)?;
            }
        }
        other => bail!("TypeError: {other} is not iterable"),
    }
    Ok(out)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::ABOVE_CORE_PARTS))?;
    ns.set("cache", rt.member("functools", "cache")?)?;
    rt.import("importlib.util")?;
    let importlib = rt.import("importlib")?;
    ns.set("importlib", importlib.clone())?;
    let path_type = rt.member("pathlib", "Path")?;
    ns.set("Path", path_type.clone())?;
    let sys = rt.import("sys")?;
    ns.set("sys", sys.clone())?;
    let here = py::method(&py::call(&path_type, vec![ns.get("__file__")?])?, "resolve", vec![])?.attr("parent")?;
    ns.set("HERE", here.clone())?;
    let hw = here.attr("parent")?;
    ns.set("HW", hw.clone())?;
    ns.set("ROOT", hw.attr("parent")?)?;
    py::sys_path_insert(rt, &interop::binary("truediv", hw.clone(), s("scripts"))?.str()?)?;
    let layout = rt.import("above_core")?;
    ns.set("layout", layout.clone())?;
    ns.set("_data", rt.member("_layout_data", "data")?)?;
    for name in ["stem_elbow_names", "core_stem_elbow_names", "reservoir_gate_elbow_hosts", "union_elbow_names", "core_union_elbow_names"] {
        ns.set(name, rt.member("above_core_bom", name)?)?;
    }
    let identity = py::tuple([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]].iter().map(|row| py::ftuple(row)));
    ns.set("IDENTITY", identity.clone())?;
    let origin = py::ftuple(&[0., 0., 0.]);
    ns.set("ORIGIN", origin.clone())?;
    let hw = py::path(&hw)?;
    ns.set("REFERENCES", py::dict(REFERENCES.iter().map(|(name, path)| (*name, Val::Path(hw.join(path))))))?;
    rt.keep(MODULE, State { hw, importlib, sys, layout, origin: origin.clone() });

    ns.def(rt, "_module", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name", "relative"], &[])?;
        let (name, relative) = (a.req("name")?, a.req("relative")?);
        load_module(rt, &name, &relative)
    })?;
    ns.def(rt, "check_reference", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        check_reference(rt)
    })?;
    ns.def(rt, "tee_reference", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        tee_reference(rt)
    })?;
    ns.def(rt, "stem_elbow_reference", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        stem_elbow_reference(rt)
    })?;
    ns.def(rt, "_frame", move |_, args, kw| {
        let mut a = py::bind(args, kw, &["rotation", "translation"], &[])?;
        let rotation = a.opt("rotation").unwrap_or_else(|| identity.clone());
        let translation = a.opt("translation").unwrap_or_else(|| origin.clone());
        Ok(frame(rotation, translation))
    })?;
    ns.def(rt, "_compose", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["outer", "inner"], &[])?;
        let (outer, inner) = (a.req("outer")?, a.req("inner")?);
        compose(rt, &outer, &inner)
    })?;
    ns.def(rt, "_snapshot", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name", "local"], &[])?;
        let name = a.req("name")?;
        let local = a.opt("local").unwrap_or(Val::None);
        snapshot_pose(rt, &name, &local)
    })?;
    ns.def(rt, "route_port_frame", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        route_port_frame(rt, &a.req("name")?)
    })?;
    ns.def(rt, "_grid", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        grid(rt)
    })?;
    ns.def(rt, "_grid_module", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["row"], &[])?;
        grid_module(rt, &a.req("row")?)
    })?;
    ns.def(rt, "core_components", |_, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(Val::dict(vec![]))
    })?;
    ns.def(rt, "_offset", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["point", "vector", "length"], &[])?;
        let (point, vector) = (a.req("point")?, a.req("vector")?);
        let length = a.opt("length").unwrap_or(Val::Float(1.));
        data(rt, "offset", &[("point", &point), ("vector", &vector), ("length", &length)])
    })?;
    ns.def(rt, "_link", |rt, args, kw| {
        let names = ["a", "axis_a", "depth_a", "b", "axis_b", "depth_b"];
        let mut a = py::bind(args, kw, &names, &[])?;
        let values = names.iter().map(|n| a.req(n)).collect::<Result<Vec<_>>>()?;
        let rows: Vec<(&str, &Val)> = names.iter().copied().zip(values.iter()).collect();
        data(rt, "link", &rows)
    })?;
    ns.def(rt, "port_stations", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        port_stations(rt, &a.req("name")?)
    })?;
    ns.def(rt, "_line", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["a", "b"], &[])?;
        let (from, to) = (a.req("a")?, a.req("b")?);
        data(rt, "line", &[("a", &from), ("b", &to)])
    })?;
    ns.def(rt, "_bezier", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["control"], &[])?;
        data(rt, "bezier", &[("control", &a.req("control")?)])
    })?;
    ns.def(rt, "_crowned_beziers", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["control", "crown", "intervals"], &[])?;
        let (control, crown) = (a.req("control")?, a.req("crown")?);
        let intervals = a.opt("intervals").unwrap_or(Val::Int(16));
        data(rt, "crowned-beziers", &[("control", &control), ("crown", &crown), ("intervals", &intervals)])
    })?;
    ns.def(rt, "_sample_bezier", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["control", "samples"], &[])?;
        let control = a.req("control")?;
        let samples = a.opt("samples").unwrap_or(Val::Int(65));
        data(rt, "sample-bezier", &[("control", &control), ("samples", &samples)])
    })?;
    ns.def(rt, "route_specs", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        route_specs(rt)
    })?;
    Ok(())
}
