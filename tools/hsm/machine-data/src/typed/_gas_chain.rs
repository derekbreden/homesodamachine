//! External adapter envelopes and tube mouths on the warm CO2 chain.
use super::num::Num;
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::Result;
use hsm_documents::interop::{self, Val};
use py::s;
use std::rc::Rc;

/// Converted: the hybrid development build runs this module, not its generated namespace.
pub const TYPED: bool = true;

const MODULE: &str = "_gas_chain";
pub const REG_IN_ADAPTER: &str = "co2-adapter-regulator-in";
pub const REG_OUT_ADAPTER: &str = "co2-adapter-regulator-out";
pub const CHECK_IN_ADAPTER: &str = "co2-adapter-check-in";
pub const CHECK_OUT_ADAPTER: &str = "co2-adapter-check-out";
pub const ADAPTER_NAMES: [&str; 4] = [REG_IN_ADAPTER, REG_OUT_ADAPTER, CHECK_IN_ADAPTER, CHECK_OUT_ADAPTER];
pub const PORT_ADAPTERS: [(&str, &str); 4] = [
    ("wr1110.inlet", REG_IN_ADAPTER),
    ("wr1110.outlet", REG_OUT_ADAPTER),
    ("gasher-co2.inlet", CHECK_IN_ADAPTER),
    ("gasher-co2.outlet", CHECK_OUT_ADAPTER),
];

pub struct State {
    cq: Val,
    ptc: Val,
    check: Val,
    reg: Val,
    female: Val,
    /// Past the mate's face: the male connector's hex and collet.
    pub male_reach: Num,
    /// The female adapter's socket, hex and collet less the stub it swallows.
    pub female_reach: Num,
    pub regulator_engagement: Num,
    pub regulator_female_reach: Num,
    npt_engage: Val,
}
fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// A port: position and outward axis, the axis as the provider holds it.
#[derive(Clone)]
pub struct Port {
    pub pos: [Num; 3],
    pub axis: [Num; 3],
    pub axis_val: Val,
}
impl Port {
    pub fn of(value: &Val) -> Result<Port> {
        let value = py::snapshot(value)?;
        let rows = py::unpack(&value, 2)?;
        Ok(Port { pos: Num::three(&rows[0])?, axis: Num::three(&rows[1])?, axis_val: rows[1].clone() })
    }
    pub fn val(&self) -> Val {
        Val::Tuple(vec![Num::vals(&self.pos), self.axis_val.clone()])
    }
}

pub fn advance(port: &Port, reach: Num) -> Port {
    let pos = [0, 1, 2].map(|i| port.pos[i].add(reach.mul(port.axis[i])));
    Port { pos, ..port.clone() }
}
fn provider_port(module: &Val, name: &str) -> Result<Port> {
    Port::of(&py::method(module, name, vec![])?)
}
pub fn regulator_inlet(rt: &Rt) -> Result<Port> {
    let st = state(rt)?;
    Ok(advance(&provider_port(&st.reg, "inlet")?, st.male_reach))
}
pub fn regulator_outlet(rt: &Rt) -> Result<Port> {
    let st = state(rt)?;
    Ok(advance(&provider_port(&st.reg, "outlet")?, st.regulator_female_reach))
}
pub fn check_inlet(rt: &Rt) -> Result<Port> {
    let st = state(rt)?;
    Ok(advance(&provider_port(&st.check, "inlet")?, st.male_reach))
}
pub fn check_outlet(rt: &Rt) -> Result<Port> {
    let st = state(rt)?;
    Ok(advance(&provider_port(&st.check, "outlet")?, st.female_reach))
}

/// The existing nominal round inlet boss, used for a local tied ceiling cradle:
/// `((point, axis), radius, length)`.
pub fn check_socket(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let total = st.check.attr("TOTAL_LENGTH")?;
    let length = st.check.attr("SOCKET_LENGTH")?;
    let mid = interop::binary(
        "add",
        interop::binary("truediv", interop::unary("neg", total)?, Val::Float(2.))?,
        interop::binary("truediv", length.clone(), Val::Float(2.))?,
    )?;
    let frame = Val::Tuple(vec![
        Val::Tuple(vec![Val::Float(0.), mid, Val::Float(0.)]),
        py::ftuple(&[0., 1., 0.]),
    ]);
    let radius = interop::binary("truediv", st.check.attr("SOCKET_D")?, Val::Float(2.))?;
    Ok(Val::Tuple(vec![frame, radius, length]))
}

fn vector(st: &State, values: &Val) -> Result<Val> {
    py::splat(&st.cq.attr("Vector")?, values)
}

/// A PI010822S in a female socket: only the external hex and collet.
pub fn male_connector(rt: &Rt, port: &Val) -> Result<Val> {
    let st = state(rt)?;
    let rows = py::unpack(port, 2)?;
    let (pos, axis) = (&rows[0], &rows[1]);
    let plane = py::call_kw(&st.cq.attr("Plane")?, vec![], vec![("origin", pos.clone()), ("normal", axis.clone())])?;
    let workplane = py::call(&st.cq.attr("Workplane")?, vec![plane])?;
    let hex = py::method(&workplane, "polygon", vec![Val::Int(6), st.ptc.attr("HEX_ACROSS_CORNERS")?])?;
    let hex_body = py::method(&hex, "extrude", vec![st.ptc.attr("HEX_LENGTH")?])?;
    let along = py::method(&vector(&st, axis)?, "multiply", vec![st.ptc.attr("HEX_LENGTH")?])?;
    let collet_base = interop::binary("add", vector(&st, pos)?, along)?;
    let collet = py::call(
        &st.cq.attr("Solid")?.attr("makeCylinder")?,
        vec![
            interop::binary("truediv", st.ptc.attr("COLLET_D")?, Val::Int(2))?,
            st.ptc.attr("COLLET_LENGTH")?,
            collet_base,
            vector(&st, axis)?,
        ],
    )?;
    py::method(&py::method(&hex_body, "union", vec![collet])?, "val", vec![])
}

/// A PI450822S made up on a male stub whose far end is `port`.
pub fn female_adapter(rt: &Rt, port: &Val, stub_d: &Val, engagement: &Val) -> Result<Val> {
    let st = state(rt)?;
    let back = advance(&Port::of(port)?, Num::of(&interop::unary("neg", engagement.clone())?)?);
    let (pos, axis) = (Num::vals(&back.pos), back.axis_val.clone());
    let base = vector(&st, &pos)?;
    let direction = vector(&st, &axis)?;
    let cylinder = st.cq.attr("Solid")?.attr("makeCylinder")?;
    let f = &st.female;
    let socket = py::call(&cylinder, vec![
        interop::binary("truediv", f.attr("JG_SOCKET_D")?, Val::Int(2))?,
        f.attr("JG_SOCKET_L")?,
        base.clone(),
        direction.clone(),
    ])?;
    let hex_origin = interop::binary("add", base.clone(), py::method(&direction, "multiply", vec![f.attr("JG_SOCKET_L")?])?)?;
    let plane = py::call_kw(&st.cq.attr("Plane")?, vec![], vec![("origin", py::method(&hex_origin, "toTuple", vec![])?), ("normal", axis)])?;
    let hex = py::method(&py::call(&st.cq.attr("Workplane")?, vec![plane])?, "polygon", vec![Val::Int(6), f.attr("JG_HEX")?])?;
    let hex_body = py::method(&py::method(&hex, "extrude", vec![f.attr("JG_HEX_L")?])?, "val", vec![])?;
    let collet_at = interop::binary(
        "add",
        base.clone(),
        py::method(&direction, "multiply", vec![interop::binary("add", f.attr("JG_SOCKET_L")?, f.attr("JG_HEX_L")?)?])?,
    )?;
    let collet = py::call(&cylinder, vec![
        interop::binary("truediv", f.attr("JG_COLLET_D")?, Val::Int(2))?,
        f.attr("JG_COLLET_L")?,
        collet_at,
        direction.clone(),
    ])?;
    let bore = py::call(&cylinder, vec![interop::binary("truediv", stub_d.clone(), Val::Int(2))?, engagement.clone(), base, direction])?;
    let fused = py::method(&py::method(&socket, "fuse", vec![hex_body, collet])?, "clean", vec![])?;
    py::method(&fused, "cut", vec![bore])
}

pub fn bodies(rt: &Rt, regulator_carry: &Val, check_carry: &Val) -> Result<Val> {
    let st = state(rt)?;
    let moved = |body: Val, carry: &Val| py::method(&body, "moved", vec![carry.attr("where")?]);
    let reg_in = moved(male_connector(rt, &py::method(&st.reg, "inlet", vec![])?)?, regulator_carry)?;
    let reg_out = moved(
        female_adapter(rt, &py::method(&st.reg, "outlet", vec![])?, &st.reg.attr("STUB_D")?, &st.regulator_engagement.val())?,
        regulator_carry,
    )?;
    let check_in = moved(male_connector(rt, &py::method(&st.check, "inlet", vec![])?)?, check_carry)?;
    let check_out = moved(
        female_adapter(rt, &py::method(&st.check, "outlet", vec![])?, &st.check.attr("THREAD_D")?, &st.npt_engage)?,
        check_carry,
    )?;
    Ok(py::dict([(REG_IN_ADAPTER, reg_in), (REG_OUT_ADAPTER, reg_out), (CHECK_IN_ADAPTER, check_in), (CHECK_OUT_ADAPTER, check_out)]))
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::GAS_CHAIN))?;
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let file = py::path(&ns.get("__file__")?)?;
    let hw = py::resolve(&file)?.ancestors().nth(2).map(|p| p.to_owned()).unwrap_or_default();
    ns.set("_hw", Val::Path(hw.clone()))?;
    for folder in ["jg-pp010822e", "gasher-check-valve", "wr1110-regulator", "seaflo-discharge-chain"] {
        ns.set("_folder", s(folder))?;
        py::sys_path_insert(rt, &py::path_str(&hw.join("reference").join(folder)))?;
    }
    let ptc = rt.import("jg_pp010822e")?;
    ns.set("_ptc", ptc.clone())?;
    let check = rt.import("gasher_check_valve")?;
    ns.set("_check", check.clone())?;
    let reg = rt.import("wr1110_regulator")?;
    ns.set("_reg", reg.clone())?;
    let female = rt.import("seaflo_discharge_chain")?;
    ns.set("_female", female.clone())?;
    let n = |module: &Val, name: &str| -> Result<Num> { Num::of(&module.attr(name)?) };
    let male_reach = n(&ptc, "HEX_LENGTH")?.add(n(&ptc, "COLLET_LENGTH")?);
    ns.set("MALE_REACH", male_reach.val())?;
    let socket_hex_collet = n(&female, "JG_SOCKET_L")?.add(n(&female, "JG_HEX_L")?).add(n(&female, "JG_COLLET_L")?);
    let female_reach = socket_hex_collet.sub(n(&female, "NPT_ENGAGE")?);
    ns.set("FEMALE_REACH", female_reach.val())?;
    let regulator_engagement = n(&female, "NPT_ENGAGE")?.min(n(&reg, "STUB_LENGTH")?);
    ns.set("REGULATOR_ENGAGEMENT", regulator_engagement.val())?;
    let socket_hex_collet = n(&female, "JG_SOCKET_L")?.add(n(&female, "JG_HEX_L")?).add(n(&female, "JG_COLLET_L")?);
    let regulator_female_reach = socket_hex_collet.sub(regulator_engagement);
    ns.set("REGULATOR_FEMALE_REACH", regulator_female_reach.val())?;
    for name in ADAPTER_NAMES {
        let key = match name {
            REG_IN_ADAPTER => "REG_IN_ADAPTER",
            REG_OUT_ADAPTER => "REG_OUT_ADAPTER",
            CHECK_IN_ADAPTER => "CHECK_IN_ADAPTER",
            _ => "CHECK_OUT_ADAPTER",
        };
        ns.set(key, s(name))?;
    }
    ns.set("ADAPTER_NAMES", py::tuple(ADAPTER_NAMES.map(s)))?;
    ns.set("PORT_ADAPTERS", py::dict(PORT_ADAPTERS.map(|(port, name)| (port, s(name)))))?;
    let npt_engage = female.attr("NPT_ENGAGE")?;
    rt.keep(MODULE, State {
        cq, ptc, check, reg, female, male_reach, female_reach, regulator_engagement, regulator_female_reach,
        npt_engage: npt_engage.clone(),
    });
    ns.def(rt, "advance", |_, args, kw| {
        let mut a = py::bind(args, kw, &["port", "reach"], &[])?;
        let port = Port::of(&a.req("port")?)?;
        Ok(advance(&port, Num::of(&a.req("reach")?)?).val())
    })?;
    for (name, f) in [
        ("regulator_inlet", regulator_inlet as fn(&Rt) -> Result<Port>),
        ("regulator_outlet", regulator_outlet),
        ("check_inlet", check_inlet),
        ("check_outlet", check_outlet),
    ] {
        ns.def(rt, name, move |rt, args, kw| {
            py::bind(args, kw, &[], &[])?;
            Ok(f(rt)?.val())
        })?;
    }
    ns.def(rt, "check_socket", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        check_socket(rt)
    })?;
    ns.def(rt, "male_connector", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["port"], &[])?;
        male_connector(rt, &a.req("port")?)
    })?;
    ns.def(rt, "female_adapter", move |rt, args, kw| {
        let mut a = py::bind(args, kw, &["port", "stub_d", "engagement"], &[])?;
        let (port, stub_d) = (a.req("port")?, a.req("stub_d")?);
        let engagement = a.opt("engagement").unwrap_or_else(|| npt_engage.clone());
        female_adapter(rt, &port, &stub_d, &engagement)
    })?;
    ns.def(rt, "bodies", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["regulator_carry", "check_carry"], &[])?;
        bodies(rt, &a.req("regulator_carry")?, &a.req("check_carry")?)
    })?;
    Ok(())
}
