//! Scalar route stations, ports, anchors and materials for the assembly handoff.
//!
//! The assembly, its runs and the routing frames are provider objects; the unit tangents and
//! the nearest-port choice are computed here.
use super::num::Num;
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::{Context, Result, ensure};
use hsm_documents::interop::Val;
use py::s;

/// Converted: the hybrid development build runs this module, not its generated namespace.
pub const TYPED: bool = true;

/// `unit(a, b)`: the unit vector from `a` toward `b`.
pub fn unit(a: &Val, b: &Val) -> Result<[f64; 3]> {
    let mut d = [Num::I(0); 3];
    for (k, c) in d.iter_mut().enumerate() {
        let k = Val::Int(k as i64);
        let to = Num::of(&b.get(k.clone())?)?;
        *c = to.sub(Num::of(&a.get(k)?)?);
    }
    let squares = d.iter().fold(Num::I(0), |sum, c| sum.add(c.mul(*c))).f();
    ensure!(squares >= 0., "math domain error");
    let n = squares.sqrt();
    ensure!(n != 0., "division by zero");
    Ok(d.map(|c| c.f() / n))
}

/// `math.dist(a, b)`.
fn dist(a: &Val, b: &Val) -> Result<f64> {
    let (a, b) = (a.iter()?, b.iter()?);
    ensure!(a.len() == b.len(), "distance dimensions");
    let mut n = 0f64;
    for (a, b) in a.iter().zip(&b) {
        n = n.hypot(a.num()? - b.num()?);
    }
    Ok(n)
}

/// `name.partition(".")`: the component and the port.
fn partition(name: &Val) -> Result<(Val, Val)> {
    if let Val::Str(text) = name {
        return Ok(match text.split_once('.') {
            Some((comp, port)) => (s(comp), s(port)),
            None => (s(text.clone()), s("")),
        });
    }
    let parts = py::unpack(&py::method(name, "partition", vec![s(".")])?, 3)?;
    Ok((parts[0].clone(), parts[2].clone()))
}

/// A routing frame's port, or the native component's carried socket: `(frame, port)`.
pub fn resolve_end(rt: &Rt, a: &Val, name: &Val, at_pt: &Val, tangent: &Val, diam: &Val) -> Result<Val> {
    let routing = rt.import("_routing")?;
    let (comp, port) = partition(name)?;
    if routing.attr("_frames")?.contains(&comp)? && port.truthy()? {
        return py::call(&routing.attr("_anchor")?, vec![name.clone()]);
    }
    if routing.attr("_frames")?.contains(&comp)? {
        let frame = routing.attr("_frames")?.get(comp)?;
        let mut nearest: Option<(Val, f64)> = None;
        for p in frame.attr("ports")?.iter()? {
            let key = dist(&py::method(&frame, "at", vec![p.clone()])?, at_pt)?;
            let closer = match &nearest {
                Some((_, best)) => key.partial_cmp(best).context("unordered numeric comparison")?.is_lt(),
                None => true,
            };
            if closer {
                nearest = Some((p, key));
            }
        }
        let (port, _) = nearest.context("empty min/max")?;
        return Ok(Val::Tuple(vec![frame, port]));
    }
    let carried = |point: &Val, outward: &Val, d: Val| -> Result<Val> {
        Ok(Val::Tuple(vec![Val::Tuple(point.iter()?), Val::Tuple(outward.iter()?), d]))
    };
    if port.truthy()? {
        let routes = rt.import("above_core_routes")?;
        let station = py::call(&routes.attr("_station")?, vec![a.attr("carries")?, comp.clone(), port.clone()])?;
        let station = py::unpack(&station, 3)?;
        let ports = Val::dict(vec![(port.clone(), carried(&station[0], &station[1], station[2].clone())?)]);
        let frame = py::call(&routing.attr("Frame")?, vec![comp, ports, Val::None])?;
        return Ok(Val::Tuple(vec![frame, port]));
    }
    let ports = Val::dict(vec![(s("socket"), carried(at_pt, tangent, diam.clone())?)]);
    let frame = py::call(&routing.attr("Frame")?, vec![comp, ports, Val::None])?;
    Ok(Val::Tuple(vec![frame, s("socket")]))
}

/// `getattr(value, name, default)`.
fn attr_or(value: &Val, name: &str, default: Val) -> Val {
    value.attr(name).unwrap_or(default)
}

/// Exact route stations from the assembly already in the producer's memory.
///
/// The scene carries the runs and anchor stations. These are the runtime values its reader also
/// needs, including native socket frames and spool selections. No body is built or tessellated.
pub fn route_metadata(rt: &Rt, a: &Val) -> Result<Val> {
    let ea = rt.import("enclosure_assembly")?;
    let routing = rt.import("_routing")?;
    let cci = ea.attr("_cci")?;
    let ends = Val::dict(vec![]);
    for run in a.attr("runs")?.iter()? {
        ends.set(run.attr("id")?, Val::dict(vec![]))?;
        let first = run.attr("pts")?.get(Val::Int(0))?;
        let frm = (s("frm"), run.attr("frm")?, first.clone(), unit(&first, &run.attr("pts")?.get(Val::Int(1))?)?);
        let last = run.attr("pts")?.get(Val::Int(-1))?;
        let to = (s("to"), run.attr("to")?, last.clone(), unit(&last, &run.attr("pts")?.get(Val::Int(-2))?)?);
        for (which, name, point, tangent) in [frm, to] {
            let end = resolve_end(rt, a, &name, &point, &py::ftuple(&tangent), &run.attr("diam")?)?;
            let end = py::unpack(&end, 2)?;
            let (frame, port) = (&end[0], &end[1]);
            let row = py::dict([
                ("frame", frame.attr("name")?),
                ("port", port.clone()),
                ("at", py::method(frame, "at", vec![port.clone()])?),
                ("normal", py::method(frame, "normal", vec![port.clone()])?),
                ("diam", py::method(frame, "diam", vec![port.clone()])?),
            ]);
            ends.get(run.attr("id")?)?.set(which, row)?;
        }
    }
    let foam_carry = a.attr("carries")?.get(s("foam-assembly"))?;
    let ids = Val::set_values(a.attr("runs")?.iter()?.iter().map(|run| run.attr("id")).collect::<Result<_>>()?);
    let stations = Val::Tuple([a.attr("tube_anchors")?.iter()?, a.attr("cap_tube_anchors")?.iter()?].concat());
    let out = Val::dict(vec![]);
    out.set(s("schema"), Val::Int(1))?;
    out.set(s("native_route_specs"), attr_or(a, "native_route_specs", Val::dict(vec![])))?;
    out.set(s("anchor_sites"), ea.attr("TUBE_ANCHOR_SITES")?)?;
    out.set(s("tube_anchor_sites"), attr_or(a, "tube_anchor_sites", Val::None))?;
    out.set(s("ends"), ends)?;
    for (key, names, anchor) in [
        ("cap_anchor_points", "cap_anchors", "cap_anchor"),
        ("cap_side_anchor_points", "cap_side_anchors", "cap_side_anchor"),
    ] {
        let points = Val::dict(vec![]);
        for name in cci.attr(names)?.iter()? {
            if ids.contains(&name)? {
                let station = py::call(&ea.attr(anchor)?, vec![name.clone()])?;
                points.set(name, py::call(&foam_carry, vec![station])?.get(Val::Int(0))?)?;
            }
        }
        out.set(s(key), points)?;
    }
    let spools = Val::dict(vec![]);
    for run in a.attr("runs")?.iter()? {
        let spool = py::call(&routing.attr("spool_of")?, vec![run.attr("id")?])?;
        spools.set(run.attr("id")?, py::dict([
            ("name", spool.attr("name")?),
            ("rgb", Val::list(spool.attr("rgb")?.iter()?)),
            ("alpha", spool.attr("alpha")?),
            ("roughness", spool.attr("roughness")?),
            ("metalness", spool.attr("metalness")?),
            ("names", spool.attr("names")?),
        ]))?;
    }
    out.set(s("spools"), spools)?;
    out.set(s("unsupported_spans"), py::call(&ea.attr("unsupported_spans")?, vec![a.attr("runs")?, stations])?)?;
    Ok(out)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::TUBE_EXPORT))?;
    ns.set("math", rt.import("math")?)?;
    ns.set("sys", rt.import("sys")?)?;
    let path_type = rt.member("pathlib", "Path")?;
    ns.set("Path", path_type.clone())?;
    let file = py::call(&path_type, vec![ns.get("__file__")?])?;
    let root = py::method(&file, "resolve", vec![])?.attr("parents")?.get(Val::Int(2))?;
    ns.set("ROOT", root.clone())?;
    let root = py::path(&root)?;
    let hw = root.join("hardware");
    ns.set("HW", Val::Path(hw.clone()))?;
    for folder in [
        hw.join("scripts"),
        hw.join("manifold-layout"),
        hw.join("cold-core-layout"),
        hw.join("printed-parts").join("cold-core"),
        root.join("tools"),
    ] {
        ns.set("_p", Val::Path(folder.clone()))?;
        let text = py::path_str(&folder);
        if !py::sys_path_has(rt, &text)? {
            py::sys_path_insert(rt, &text)?;
        }
    }
    ns.def(rt, "unit", |_, args, kw| {
        let mut a = py::bind(args, kw, &["a", "b"], &[])?;
        let (from, to) = (a.req("a")?, a.req("b")?);
        Ok(py::ftuple(&unit(&from, &to)?))
    })?;
    ns.def(rt, "_resolve_end", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["a", "name", "at_pt", "tangent", "diam"], &[])?;
        let (assembly, name, at_pt) = (a.req("a")?, a.req("name")?, a.req("at_pt")?);
        let (tangent, diam) = (a.req("tangent")?, a.req("diam")?);
        resolve_end(rt, &assembly, &name, &at_pt, &tangent, &diam)
    })?;
    ns.def(rt, "route_metadata", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["a"], &[])?;
        route_metadata(rt, &a.req("a")?)
    })?;
    Ok(())
}
