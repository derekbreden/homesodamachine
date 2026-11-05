//! Rear inlet header, pump joints and integral snap seats in appliance coordinates.
//!
//! Purchased profiles keep their own reference frames: each fitting is a reference module the
//! above-core parts load, and the tube recipes are the layout data recipes answered in process.
use super::num::Num;
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::{Context, Result, anyhow, bail, ensure};
use hsm_documents::interop::{self, Val};
use py::s;
use serde_json::{Value, json};
use std::rc::Rc;

/// Not yet compiled as it stands: the hybrid development build runs the generated namespace.
pub const TYPED: bool = false;

const MODULE: &str = "rear_plumbing";
/// Every rear tube's outside diameter.
const TUBE: f64 = 6.35;

pub struct State {
    /// `layout`: the above-core placements.
    layout: Val,
}
fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// `layout.specification()`: the shared production specification.
fn specification(rt: &Rt) -> Result<Val> {
    py::method(&state(rt)?.layout, "specification", vec![])
}

/// A value as the JSON a layout data request carries; provider containers are copied in one
/// snapshot each, and anything else that is not plain data is refused as Python's encoder does.
pub fn plain(value: &Val) -> Result<Value> {
    Ok(match value {
        Val::None => Value::Null,
        Val::Bool(b) => json!(b),
        Val::Int(i) => json!(i),
        Val::Float(f) => {
            ensure!(f.is_finite(), "Out of range float values are not JSON compliant: {}", Val::Float(*f).repr()?);
            json!(f)
        }
        Val::Str(text) => json!(text),
        Val::Tuple(rows) | Val::FrozenSet(rows) => Value::Array(rows.iter().map(plain).collect::<Result<_>>()?),
        Val::List(rows) | Val::Set(rows) => Value::Array(rows.borrow().iter().map(plain).collect::<Result<_>>()?),
        Val::Dict(rows) | Val::Namespace(rows) => Value::Object(
            rows.borrow().iter().map(|(k, v)| Ok((k.str()?, plain(v)?))).collect::<Result<_>>()?,
        ),
        Val::Ref(_) => {
            let copied = py::snapshot(value)?;
            ensure!(!matches!(copied, Val::Ref(_)), "Object of type {} is not JSON serializable", value.repr()?);
            plain(&copied)?
        }
        other => bail!("Object of type {} is not JSON serializable", other.repr()?),
    })
}

/// `_data(op, **values)`, answered by the layout data recipes in this process. A refused recipe
/// reads as the transport raises it: `ValueError: layout-data: <the recipe's error chain>`.
fn data(rt: &Rt, op: &str, values: Vec<(&str, Value)>) -> Result<Value> {
    let mut payload = serde_json::Map::new();
    payload.insert("op".into(), json!(op));
    for (key, value) in values {
        payload.insert(key.into(), value);
    }
    rt.layout_data(Value::Object(payload)).map_err(|error| anyhow!("ValueError: layout-data: {error:#}"))
}

/// `plan()`: the rear plumbing section of the production specification.
pub fn plan(rt: &Rt) -> Result<Val> {
    specification(rt)?.get(s("rear_plumbing"))
}

/// `reference(name, path)`: a purchased fitting's reference module, loaded afresh as
/// `rear_<name>`.
pub fn reference(rt: &Rt, name: &Val, path: &Val) -> Result<Val> {
    let parts = rt.import("above_core_parts")?;
    let qualified = match name {
        Val::Str(name) => s(format!("rear_{name}")),
        other => interop::binary("add", s("rear_"), other.clone())?,
    };
    py::call(&parts.attr("_module")?, vec![qualified, path.clone()])
}
fn reference_named(rt: &Rt, name: &str, path: &str) -> Result<Val> {
    reference(rt, &s(name), &s(path))
}
pub fn chain(rt: &Rt) -> Result<Val> {
    reference_named(rt, "threaded_chain", "reference/asse1022-threaded-chain/asse1022_threaded_chain.py")
}
pub fn union_tee(rt: &Rt) -> Result<Val> {
    reference_named(rt, "union_tee", "reference/jg-pp0208e-tee/jg_pp0208e_tee.py")
}
pub fn check(rt: &Rt) -> Result<Val> {
    reference_named(rt, "acvus", "reference/neofit-acvus44-check/neofit_acvus44_check.py")
}
pub fn joint(rt: &Rt) -> Result<Val> {
    reference_named(rt, "pump_joint", "reference/pump-barb-joint/pump_barb_joint.py")
}

/// `_arc_three(points)`.
pub fn arc_three(rt: &Rt, points: &Val) -> Result<Val> {
    py::from_json(data(rt, "arc-three", vec![("points", plain(points)?)])?)
}

/// A provider port `(position, axis)` with the tube diameter appended.
fn with_tube(port: &Val) -> Result<Val> {
    let mut row = port.iter()?;
    row.push(Val::Float(TUBE));
    Ok(Val::Tuple(row))
}
fn station_row(position: Val, axis: Val) -> Val {
    Val::Tuple(vec![position, axis, Val::Float(TUBE)])
}

/// `ports(name)`: a rear fitting's native `port -> (position, axis, diameter)`, or `None` for a
/// fitting the rear plumbing does not own.
pub fn ports(rt: &Rt, name: &Val) -> Result<Val> {
    let _ = plan(rt)?;
    let name = match name {
        Val::Str(text) => text.as_str(),
        _ => return Ok(Val::None),
    };
    Ok(match name {
        "bulkhead-water" => {
            let inlet = py::method(&chain(rt)?, "ports", vec![])?.get(s("inlet"))?;
            let pu = py::unpack(&inlet, 2)?;
            let (p, u) = (pu[0].clone(), pu[1].clone());
            let back = Val::Tuple(u.iter()?.into_iter().map(|c| interop::unary("neg", c)).collect::<Result<_>>()?);
            py::dict([("outboard", station_row(p.clone(), u)), ("inboard", station_row(p, back))])
        }
        "gas-regulator" | "co2-inlet" => {
            let down = || Val::Tuple(vec![Val::Float(0.), Val::Float(0.), Val::Float(-1.)]);
            let up = || py::ftuple(&[0., 0., 1.]);
            let base = || py::ftuple(&[0., 0., 0.]);
            let top = || py::ftuple(&[0., 0., 62.814]);
            py::dict([
                ("inlet", station_row(base(), down())),
                ("outlet", station_row(top(), up())),
                ("outboard", station_row(base(), down())),
                ("inboard", station_row(top(), up())),
            ])
        }
        "gas-check" | "discharge-chain" => {
            let inlet = with_tube(&py::method(&check(rt)?, "stem_tip", vec![])?)?;
            let outlet = with_tube(&py::method(&check(rt)?, "tube_port", vec![])?)?;
            let tube_port = with_tube(&py::method(&check(rt)?, "tube_port", vec![])?)?;
            py::dict([("inlet", inlet), ("outlet", outlet), ("tube-port", tube_port)])
        }
        "water-split" => {
            let supply = with_tube(&py::method(&union_tee(rt)?, "branch", vec![])?)?;
            let to_vk = with_tube(&py::method(&union_tee(rt)?, "run", vec![Val::Int(1)])?)?;
            let to_flavor = with_tube(&py::method(&union_tee(rt)?, "run", vec![Val::Int(-1)])?)?;
            py::dict([("supply", supply), ("to-vk", to_vk), ("to-flavor", to_flavor)])
        }
        "suction-reducer" | "discharge-reducer" => {
            let length = Num::of(&joint(rt)?.attr("reducer")?.attr("LENGTH")?)?;
            let mouth = length.sub(Num::of(&joint(rt)?.attr("CUT_X")?)?);
            let at = Val::Tuple(vec![mouth.val(), Val::Float(0.), Val::Float(0.)]);
            py::dict([("tube", station_row(at, py::ftuple(&[1., 0., 0.])))])
        }
        "jg-pp061208w" => {
            let red = py::method(&chain(rt)?, "parameters", vec![])?.get(s("pp061208w"))?;
            let x = Num::of(&py::at(&red, "visible_axial_range_mm")?.get(Val::Int(1))?)?;
            let r = py::at(&red, "rotation")?;
            let mut p = Vec::with_capacity(3);
            for i in 0..3 {
                let origin = Num::of(&py::at(&red, "origin_mm")?.get(Val::Int(i))?)?;
                let along = Num::of(&r.get(Val::Int(i))?.get(Val::Int(0))?)?.mul(x);
                p.push(origin.add(along).val());
            }
            let axis = r.iter()?.iter().map(|row| row.get(Val::Int(0))).collect::<Result<Vec<_>>>()?;
            py::dict([("tube", station_row(Val::Tuple(p), Val::Tuple(axis)))])
        }
        _ => Val::None,
    })
}

/// `snap_datums()`: the integral rear seats' axes and supporting wall planes.
pub fn snap_datums(rt: &Rt) -> Result<Val> {
    let layout = state(rt)?.layout.clone();
    let data = plan(rt)?;
    let c = {
        let point = layout.attr("point")?;
        let frame = data.get(s("chain_frame"))?;
        let z = chain(rt)?.attr("bfp")?.attr("BODY_CENTER_Z")?;
        py::call(&point, vec![frame, Val::Tuple(vec![Val::Float(0.), Val::Float(0.), z])])?
    };
    let p = {
        let point = layout.attr("point")?;
        let frame = data.get(s("gas_frame"))?;
        py::call(&point, vec![frame, py::ftuple(&[0., 0., 0.])])?
    };
    let at = |v: &Val, i: i64| v.get(Val::Int(i));
    Ok(py::dict([
        ("asse_axis", Val::Tuple(vec![at(&c, 0)?, at(&c, 2)?])),
        ("asse_turn", Val::Float(90.)),
        ("pisco_axis", Val::Tuple(vec![at(&p, 0)?, at(&p, 2)?])),
        ("mouth_y", at(&p, 1)?),
        ("ceiling", data.get(s("snap_ceiling_z_mm"))?),
        ("rear", Val::Float(465.3)),
        ("side", Val::Float(98.5)),
    ]))
}

/// `meter_spans()`: receiver and removable-cap extents on the meter's own axial frame.
pub fn meter_spans(rt: &Rt) -> Result<Val> {
    let pose = py::call(&state(rt)?.layout.attr("pose")?, vec![s("digiten-flow")])?;
    let y = Num::of(&pose.get(s("translation_mm"))?.get(Val::Int(1))?)?;
    let span = |below: f64, above: f64| Val::Tuple(vec![y.sub(Num::F(below)).val(), y.add(Num::F(above)).val()]);
    Ok(Val::Tuple(vec![span(30.01, 29.99), span(19.01, 18.99)]))
}

/// `_route_stations(operation, resolver)`: each station a recipe names, keyed `name.port`.
pub fn route_stations(rt: &Rt, operation: &Val, resolver: &dyn Fn(&Val, &Val) -> Result<Val>) -> Result<Val> {
    let spec = specification(rt)?;
    let wanted = data(rt, "route-stations", vec![("operation", plain(operation)?), ("spec", plain(&spec)?)])?;
    let out = Val::dict(vec![]);
    for pair in py::from_json(wanted)?.iter()? {
        let pair = py::unpack(&pair, 2)?;
        let key = format!("{}.{}", interop::format(&pair[0], "")?, interop::format(&pair[1], "")?);
        out.set(s(key), resolver(&pair[0], &pair[1])?)?;
    }
    Ok(out)
}

/// `dict(rows)` of a layout recipe's `(name, value)` rows, as the runtime builds it.
fn rows_dict(rows: Value) -> Result<Val> {
    let rows = rows.as_array().context("route rows")?;
    let mut entries = Vec::with_capacity(rows.len());
    for row in rows {
        let pair = row.as_array().filter(|pair| pair.len() == 2).context("dictionary entry needs two values")?;
        entries.push((py::from_json(pair[0].clone())?, py::from_json(pair[1].clone())?));
    }
    Ok(Val::dict(entries))
}

/// `route_specs()`: the short rear tube recipes, provider ports carried to world stations.
pub fn route_specs(rt: &Rt) -> Result<Val> {
    let parts = rt.import("above_core_parts")?;
    let layout = state(rt)?.layout.clone();
    let station = |name: &Val, port: &Val| -> Result<Val> {
        let row = py::call(&parts.attr("port_stations")?, vec![name.clone()])?.get(port.clone())?;
        let row = py::unpack(&row, 3)?;
        let frame = py::call(&parts.attr("route_port_frame")?, vec![name.clone()])?;
        let point = py::call(&layout.attr("point")?, vec![frame.clone(), row[0].clone()])?;
        let vector = py::call(&layout.attr("vector")?, vec![frame.get(s("rotation"))?, row[1].clone()])?;
        Ok(Val::Tuple(vec![point, vector, row[2].clone()]))
    };
    let params = py::dict([
        ("reducer_insertion", joint(rt)?.attr("reducer")?.attr("TUBE_INSERTION_DEPTH")?),
        ("tee_insertion", union_tee(rt)?.attr("INSERTION")?),
        ("stem_insertion", py::method(&parts, "stem_elbow_reference", vec![])?.attr("SOCKET_INSERTION")?),
    ]);
    let spec = specification(rt)?;
    let stations = route_stations(rt, &s("rear-route-specs"), &station)?;
    rows_dict(data(rt, "rear-route-specs", vec![("spec", plain(&spec)?), ("stations", plain(&stations)?), ("params", plain(&params)?)])?)
}

/// `continuations(station)`: the water, gas and vent continuations between named interfaces.
pub fn continuations(rt: &Rt, station: &Val) -> Result<Val> {
    let bulkhead = reference_named(rt, "pp1208e", "reference/jg-bulkhead-union/jg_bulkhead_union.py")?;
    let params = py::dict([
        ("check_insertion", check(rt)?.attr("INSERTION")?),
        ("bulkhead_tube_stop", bulkhead.attr("TUBE_STOP_DEPTH")?),
    ]);
    let spec = specification(rt)?;
    let resolve = |name: &Val, port: &Val| py::call(station, vec![name.clone(), port.clone()]);
    let stations = route_stations(rt, &s("rear-continuations"), &resolve)?;
    rows_dict(data(rt, "rear-continuations", vec![("spec", plain(&spec)?), ("stations", plain(&stations)?), ("params", plain(&params)?)])?)
}

/// `_flavor_s_bend(start, heading, offset, axis)`: `(segments, end)`.
pub fn flavor_s_bend(rt: &Rt, start: &Val, heading: &Val, offset: &Val, axis: &Val) -> Result<Val> {
    let result = data(rt, "flavor-s-bend", vec![
        ("start", plain(start)?),
        ("heading", plain(heading)?),
        ("offset", plain(offset)?),
        ("axis", plain(axis)?),
    ])?;
    let pair = py::unpack(&py::from_json(result)?, 2)?;
    Ok(Val::Tuple(vec![pair[0].clone(), Val::Tuple(pair[1].iter()?)]))
}

/// `_flavor_rear(flavor, destination)`.
pub fn flavor_rear(rt: &Rt, flavor: &Val, destination: &Val) -> Result<Val> {
    py::from_json(data(rt, "flavor-rear", vec![("flavor", plain(flavor)?), ("destination", plain(destination)?)])?)
}

/// `flavor_routes(station)`: the dispense-line recipes from the raw world-port stations.
pub fn flavor_routes(rt: &Rt, station: &Val) -> Result<Val> {
    let resolve = |name: &Val, port: &Val| py::call(station, vec![name.clone(), port.clone()]);
    let stations = route_stations(rt, &s("flavor-routes"), &resolve)?;
    rows_dict(data(rt, "flavor-routes", vec![("stations", plain(&stations)?)])?)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::REAR_PLUMBING))?;
    ns.set("json", rt.import("json")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("np", rt.import("numpy")?)?;
    let layout = rt.import("above_core")?;
    ns.set("layout", layout.clone())?;
    ns.set("_data", rt.member("_layout_data", "data")?)?;
    rt.keep(MODULE, State { layout });
    ns.def(rt, "plan", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        plan(rt)
    })?;
    ns.def(rt, "reference", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name", "path"], &[])?;
        reference(rt, &a.req("name")?, &a.req("path")?)
    })?;
    for (name, f) in [
        ("chain", chain as fn(&Rt) -> Result<Val>),
        ("union_tee", union_tee),
        ("check", check),
        ("joint", joint),
    ] {
        ns.def(rt, name, move |rt, args, kw| {
            py::bind(args, kw, &[], &[])?;
            f(rt)
        })?;
    }
    ns.def(rt, "_arc_three", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["points"], &[])?;
        arc_three(rt, &a.req("points")?)
    })?;
    ns.def(rt, "ports", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        ports(rt, &a.req("name")?)
    })?;
    ns.def(rt, "snap_datums", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        snap_datums(rt)
    })?;
    ns.def(rt, "meter_spans", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        meter_spans(rt)
    })?;
    ns.def(rt, "_route_stations", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["operation", "resolver"], &[])?;
        let (operation, resolver) = (a.req("operation")?, a.req("resolver")?);
        route_stations(rt, &operation, &|name, port| py::call(&resolver, vec![name.clone(), port.clone()]))
    })?;
    ns.def(rt, "route_specs", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        route_specs(rt)
    })?;
    ns.def(rt, "continuations", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["station"], &[])?;
        continuations(rt, &a.req("station")?)
    })?;
    ns.def(rt, "_flavor_s_bend", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["start", "heading", "offset", "axis"], &[])?;
        let (start, heading, offset, axis) = (a.req("start")?, a.req("heading")?, a.req("offset")?, a.req("axis")?);
        flavor_s_bend(rt, &start, &heading, &offset, &axis)
    })?;
    ns.def(rt, "_flavor_rear", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["flavor", "destination"], &[])?;
        flavor_rear(rt, &a.req("flavor")?, &a.req("destination")?)
    })?;
    ns.def(rt, "flavor_routes", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["station"], &[])?;
        flavor_routes(rt, &a.req("station")?)
    })?;
    Ok(())
}
