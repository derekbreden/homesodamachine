//! The enclosure assembly's tube runs: every line between two placed bodies, authored port to port.
//!
//! `STATIONS` holds each body's tube mouths as callables a frame carries into place. Each run is one
//! `_routing.bent` from a source port through hand-placed waypoints to its destination port; `_routing`
//! seats the corners and records every shortfall in `BLOCKED`.
use super::num::{self, Num};
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::{Context, Result, bail, ensure};
use hsm_documents::interop::{self, Val};
use py::s;
use std::cell::OnceCell;
use std::cmp::Ordering;
use std::path::Path;
use std::rc::Rc;

/// Converted: the hybrid development build runs this module, not its generated namespace.
pub const TYPED: bool = true;

const MODULE: &str = "_lines";

/// The folders put on `sys.path` after `hardware/scripts` and this file's own, under `hardware/`.
const FOLDERS: [&str; 20] = [
    "printed-parts/cold-core",
    "printed-parts/zone-c/funnel",
    "printed-parts/enclosure/enclosure",
    "reference/compressor",
    "reference/condenser-block",
    "reference/g-ganen-pump/installation",
    "printed-parts/diaphragm-pump-sleeve",
    "reference/neofit-achv44-check",
    "reference/asse1022-assembly",
    "reference/water-split",
    "reference/shok-blok-regulator",
    "reference/beduan-solenoid",
    "reference/jg-bulkhead-union",
    "reference/neofit-stem-elbow",
    "reference/neofit-bulkhead",
    "reference/neofit-drain-bulkhead",
    "reference/neofit-flavor-reducer",
    "reference/gasher-check-valve",
    "reference/wr1110-regulator",
    "reference/digiten-flow-sensor",
];

/// The modules imported, in order, under their aliases (`_anchor_cap` twice, as the source does).
const IMPORTS: [(&str, &str); 26] = [
    ("R", "_routing"),
    ("_cc", "_cold_core_interface"),
    ("_anchor_cap", "_anchor_cap_interface"),
    ("_asse", "asse1022_assembly"),
    ("_funnel", "funnel"),
    ("_pump", "g_ganen_installation"),
    ("_pump_elbow", "diaphragm_pump_sleeve"),
    ("_dis", "neofit_achv44_check"),
    ("_beduan", "beduan_solenoid"),
    ("_jg", "jg_bulkhead_union"),
    ("_drain_elbow", "neofit_stem_elbow"),
    ("_drain_bulkhead", "neofit_drain_bulkhead"),
    ("_flavor_reducer", "neofit_flavor_reducer"),
    ("_neofit", "neofit_bulkhead"),
    ("_flowreg", "shok_blok_regulator"),
    ("_split", "water_split"),
    ("_ml", "manifold_layout"),
    ("_comp", "compressor"),
    ("_cond", "condenser_block"),
    ("_copper", "_copper_ports"),
    ("_gasher", "gasher_check_valve"),
    ("_wr1110", "wr1110_regulator"),
    ("_gas_chain", "_gas_chain"),
    ("_anchor_cap", "_anchor_cap_interface"),
    ("_digiten", "digiten_flow_sensor"),
    ("_card", "_scorecard"),
];

pub const VALVES: [&str; 10] = ["V-A", "V-B", "V-C", "V-D", "V-E", "V-F", "V-G", "V-H", "V-I", "V-J"];
/// The cap conduits the foam assembly's stations read off `enclosure_assembly.cap_conduit`.
const CAP_CONDUITS: [&str; 7] =
    ["water-in", "carb-water-out", "reservoir-a", "reservoir-b", "reservoir-a-fill", "reservoir-b-fill", "co2-in"];
/// The runs this module draws.
pub const AUTHORED: [&str; 22] = [
    "water-7", "water-6", "water-5", "water-2", "fluid-1", "water-3", "co2-0", "co2-1", "co2-2", "fluid-2", "fluid-4",
    "carb-1", "carb-2", "fluid-28", "fluid-18", "fluid-24", "fluid-26", "fluid-14", "fluid-16", "refrig-3", "refrig-2",
    "refrig-1",
];

pub const SUCTION_LEAD: [f64; 2] = [22.0, 15.0];
/// `DISCHARGE_LEAD` is this straight, then the tube's bend radius.
pub const DISCHARGE_LEAD_STRAIGHT: f64 = 10.5;
pub const CU_OD: f64 = 6.35;
pub const CU_LEAD: f64 = 20.0;
pub const CROSS_DODGE_SPAN: [f64; 2] = [-22.0, -5.5];
pub const CROSS_DODGE_RAMP: f64 = 8.0;
pub const CROSS_DROP: f64 = 7.1;
pub const CHANNEL_X: f64 = -94.0;
pub const CROSS_RISE: f64 = 4.5;
pub const CROSS_LIFT_X: f64 = 24.0;
pub const CROSS_APPROACH_Y: f64 = 164.0;
pub const FLUID_1_INBOARD: f64 = 29.85;
pub const FLUID_1_APPROACH: f64 = 8.0;
pub const FLUID_1_DIAGONAL: f64 = 20.0;
pub const WATER_2_LEAD: f64 = 12.0;
pub const WATER_2_RUN: f64 = 21.25;
pub const FLUID_2_RETURN_X: f64 = -54.0;
pub const FLUID_2_RETURN_FORE_Y: f64 = 357.0;
pub const FLUID_2_OVER_CAP: f64 = 66.1;
pub const FLUID_2_DESCENT_EAST: f64 = 0.5;
pub const FLUID_4_CROSS_Y: f64 = 282.0;
pub const CARB_1_FORWARD_LEAN: f64 = 1.0;
pub const GATE_STUB_CLEAR: f64 = 4.0;
pub const GATE_B_JOG_LEG: f64 = 32.0;
pub const GATE_B_DRAIN_RETURN_RISE: f64 = 3.5;
pub const GATE_B_RETURN_WEST: f64 = 16.5;
pub const GATE_B_RETURN_HOLD_Y: f64 = 412.0;
pub const GATE_B_UNION_APPROACH: f64 = 10.0;
pub const GATE_B_STEP_Y: f64 = 393.0;
pub const GATE_B_RISE_RUN: f64 = 20.0;
pub const GATE_A_FRONT_Y: f64 = 135.0;
pub const GATE_A_FRONT_Z: f64 = 283.0;
pub const GATE_A_FRONT_JOIN_X: f64 = 35.0;
pub const GATE_A_OUTER_X: f64 = -88.0;
pub const GATE_A_DESCENT_START_Y: f64 = 175.0;
pub const GATE_A_BEARING_JOIN_Y: f64 = 235.0;
pub const GATE_A_BEARING_EXIT_Y: f64 = 295.0;
pub const GATE_A_LOW_LANE_JOIN_Y: f64 = 325.0;
pub const GATE_A_FORE_HEIGHT: f64 = 4.9;
pub const GATE_A_WEST_X: f64 = -76.5;
pub const GATE_A_RETURN_START_Y: f64 = 345.0;
pub const GATE_A_UNION_JOIN_Y: f64 = 375.0;
pub const GATE_A_UNION_LEVEL_RUN: f64 = 16.0;
pub const GATE_A_RISE_RUN: f64 = 20.0;
pub const GATE_B_CLIMB: f64 = 29.5;
/// `RESERVOIR_B_CRUISE` is the tube's bend radius less this.
pub const RESERVOIR_B_CRUISE_SHORT: f64 = 0.6;
pub const RESERVOIR_B_GATE_LEAN_DEG: f64 = 2.9;
pub const FILL_B_LEAN_Y: f64 = 170.0;
pub const FILL_B_JOIN_Y: f64 = 192.0;
pub const LANE_CLEAR: f64 = 4.0;
pub const FILL_A_LANE_Z: f64 = 289.0;
pub const FILL_A_GATE_LEAD: f64 = 14.6;
pub const FILL_A_GATE_LEAN_DEG: f64 = 2.9;
pub const FILL_A_FALL_RUN: f64 = 6.0;
pub const FILL_A_HOSE_DROP: f64 = 1.25;
pub const FILL_A_HOSE_FALL_RUN: f64 = 12.0;
pub const FILL_A_VALVE_DROP: f64 = 1.5;
pub const FILL_A_VALVE_RETURN_RUN: f64 = 8.0;
/// `FILL_A_BEARING_STRAIGHT` is the anchor cap's rib length plus this.
pub const FILL_A_BEARING_PAST_RIB: f64 = 2.0;
pub const DRAW_A_CRUISE: f64 = 43.4;
pub const DRAW_A_NECK_IN: [f64; 2] = [56.5, 47.7];
pub const DRAW_A_NECK_OUT: [f64; 3] = [92.2, 42.9, 38.3];
pub const DRAW_A_APPROACH: [f64; 3] = [11.7, 90.1, -2.3];
pub const DRAW_A_GATE_LEAD: f64 = 16.4;
pub const DRAW_B_CRUISE: f64 = 34.6;
pub const DRAW_B_APPROACH: [f64; 3] = [-11.65, 90.7, 2.8];
pub const DRAW_B_GATE_LEAD: f64 = 15.3;
pub const DRAW_GATE_LEAN_DEG: f64 = 2.9;

const NOTE_CO2_0: &str = "CO2: rear-wall bulkhead → WR1110 inlet collet";
const NOTE_CO2_1: &str = "CO2: WR1110 outlet → downstream check inlet, U-turn above the pump";
const NOTE_WATER_3: &str = "tap water: split branch → V-K inlet, down into the west channel, across the window under the funnel's drain union — stepping aft onto the lid's side post — and up V-K's own column into the mouth";
const NOTE_FLUID_1: &str = "flavor clean water: split run -> internal pressure regulator, below the frame";
const NOTE_WATER_2: &str =
    "tap water: ASSE outlet → split supply, one lean off the deck onto the lane the funnel's bowl leaves";
const NOTE_WATER_7: &str = "carb water: V-K outlet → the G Ganen's suction elbow, one lean up and west";
const NOTE_WATER_6: &str = "carb water: the G Ganen's discharge elbow → the single check's inlet collet";
const NOTE_WATER_5: &str =
    "carb water: water check's outlet → the core's water-in cap conduit, one slant across the fall";
const NOTE_CO2_2: &str = "CO2: downstream check outlet → east lane → the core's CO2 cap conduit";
const NOTE_FLUID_2: &str =
    "clean water: internal regulator outlet, rear rising return west of the pump, then V-A's axial inlet quarter";
const NOTE_FLUID_4: &str = "funnel drain elbow → V-B inlet: aft through the V-A/V-B gap, west behind V-B's coil, aft down its west flank, and one U east and down into its aft-facing inlet";
const NOTE_CARB_1: &str = "carb water: the core's carb-water cap conduit → DIGITEN inlet, leaning forward up the port lane for main-board air, then west along the panel deck onto the meter's own column";
const NOTE_CARB_2: &str = "carb water: DIGITEN outlet → rear union, a shallow rise between two on-axis ends";
const NOTE_FLUID_28: &str =
    "flavor B: V-J-O → rear union, through the front support and a raised west return above the ASSE drain";
const NOTE_FLUID_18: &str =
    "flavor A: V-G-O → rear union, across the front coils, through the west cap bearing and over the pump's west-rear foot";
const NOTE_FLUID_14: &str = "reservoir A fill: V-F-O → the fill bore in its own cap, straight down onto the cap, then the whole way aft in the lane V-K and V-A leave to the bore's own column behind the suction elbow";
const NOTE_FLUID_16: &str = "reservoir A draw: the dip tube up out of A's cap → V-E-I, forward along the pump's east side and between V-A and V-K onto the gate's lead";
const NOTE_FLUID_24: &str =
    "reservoir B fill: V-I-O → the fill bore in its own cap, up the west outboard lane and one lean inboard onto the bore";
const NOTE_FLUID_26: &str =
    "reservoir B draw: the dip tube up out of B's cap → V-H-I, forward west of the funnel drain's elbow onto the gate's lead";
const NOTE_REFRIG_3: &str = "sealed loop: evaporator outlet → compressor suction, the one leg of the three that is drawn rather than made across a shared plane";
const NOTE_REFRIG_1: &str = "sealed loop: compressor discharge → condenser inlet, one straight across the lane";
const NOTE_REFRIG_2: &str = "sealed loop: condenser outlet → evaporator inlet, hand-formed across the lane";

pub struct State {
    r: Val,
    cc: Val,
    pump: Val,
    ml: Val,
    card: Val,
    flavor_reducer: Val,
    /// `_routing.BLOCKED`: the one dict `_routing` refills on every call.
    blocked: Val,
    /// The namespace's `STATIONS`: one dict, read where the source reads it.
    stations: Val,
    pub tube_bend: Num,
    pub elbow_cuff_d: Num,
    pub cu_bend: Num,
    pub split_tube_d: Num,
    cap_bore_skew: Val,
    pub cross_y: Num,
    pub cross_dodge_y: Num,
    pub channel_entry_y: Num,
    pub reservoir_b_cruise: Num,
    pub fill_a_bearing_straight: Num,
    collet_skew: OnceCell<Val>,
    butt_max: OnceCell<Num>,
    proud_length: OnceCell<Num>,
}
impl State {
    /// `R.COLLET_SKEW`, read where a run first needs it.
    fn collet_skew(&self) -> Result<Val> {
        if let Some(value) = self.collet_skew.get() {
            return Ok(value.clone());
        }
        let value = self.r.attr("COLLET_SKEW")?;
        Ok(self.collet_skew.get_or_init(|| value).clone())
    }
    /// `R.BUTT_MAX`.
    fn butt_max(&self) -> Result<Num> {
        if let Some(value) = self.butt_max.get() {
            return Ok(*value);
        }
        let value = Num::of(&self.r.attr("BUTT_MAX")?)?;
        Ok(*self.butt_max.get_or_init(|| value))
    }
    /// `_flavor_reducer.PROUD_LENGTH`.
    fn proud_length(&self) -> Result<Num> {
        if let Some(value) = self.proud_length.get() {
            return Ok(*value);
        }
        let value = Num::of(&self.flavor_reducer.attr("PROUD_LENGTH")?)?;
        Ok(*self.proud_length.get_or_init(|| value))
    }
    /// `(R.COLLET_SKEW, CAP_BORE_SKEW)`: a run that leaves a collet for a cap bore.
    fn collet_to_cap(&self) -> Result<Val> {
        Ok(Val::Tuple(vec![self.collet_skew()?, self.cap_bore_skew.clone()]))
    }
    /// `(CAP_BORE_SKEW, R.COLLET_SKEW)`: a run that leaves a cap bore for a collet.
    fn cap_to_collet(&self) -> Result<Val> {
        Ok(Val::Tuple(vec![self.cap_bore_skew.clone(), self.collet_skew()?]))
    }
}
fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

// ---------------------------------------------------------------------------------------------
// The Python boundary.

/// A parameter: name, default, keyword-only.
type Param = (&'static str, Option<Val>, bool);

/// Positional parameters without defaults.
fn req(names: &[&'static str]) -> Vec<Param> {
    names.iter().map(|&name| (name, None, false)).collect()
}

/// Arguments bound to parameters as the module's functions bind them: each parameter in turn takes
/// the next positional argument (unless keyword-only), else its keyword, else its default.
fn bind(args: py::Args, mut kwargs: py::Kwargs, params: &[Param]) -> Result<Vec<Val>> {
    let mut positional = args.into_iter();
    let mut values = Vec::with_capacity(params.len());
    for (name, default, keyword_only) in params {
        let keyword = kwargs.iter().position(|(key, _)| key.as_str() == *name);
        let given = if *keyword_only { None } else { positional.next() };
        values.push(match (given, keyword) {
            (Some(_), Some(_)) => bail!("multiple arguments for {name}"),
            (Some(value), None) => value,
            (None, Some(index)) => kwargs.remove(index).1,
            (None, None) => default.clone().with_context(|| format!("missing argument {name}"))?,
        });
    }
    ensure!(positional.next().is_none(), "too many positional arguments");
    ensure!(kwargs.is_empty(), "unexpected keyword arguments");
    Ok(values)
}

/// A module function, bound in the namespace.
fn define(
    ns: &Ns,
    rt: &Rt,
    name: &str,
    params: Vec<Param>,
    f: impl Fn(&Rt, Vec<Val>) -> Result<Val> + 'static,
) -> Result<()> {
    ns.def(rt, name, move |rt, args, kwargs| f(rt, bind(args, kwargs, &params)?))
}

/// A lambda a station entry holds.
fn lambda(rt: &Rt, params: Vec<Param>, f: impl Fn(&Rt, Vec<Val>) -> Result<Val> + 'static) -> Val {
    let rt = rt.clone();
    Val::function(move |args, kwargs| {
        let values = bind(args, kwargs, &params)?;
        let _frame = rt.frame(MODULE);
        f(&rt, values)
    })
}

/// A station that calls `module.method(*args)`.
fn call_station(rt: &Rt, module: &Val, method: &'static str, args: Vec<Val>) -> Val {
    let module = module.clone();
    lambda(rt, vec![], move |_, _| py::method(&module, method, args.clone()))
}

// ---------------------------------------------------------------------------------------------
// Numbers as the runtime combines them.

fn f(x: f64) -> Num {
    Num::F(x)
}
/// `v[i]` as a number.
fn idx(v: &Val, i: i64) -> Result<Num> {
    Num::of(&v.get(Val::Int(i))?)
}
/// The first three numbers of a sequence, copied in one callback when it is a provider's.
fn three(v: &Val) -> Result<[Num; 3]> {
    let v = py::snapshot(v)?;
    Ok([idx(&v, 0)?, idx(&v, 1)?, idx(&v, 2)?])
}
fn point(x: Num, y: Num, z: Num) -> Val {
    Num::vals(&[x, y, z])
}
fn order(a: Num, b: Num) -> Result<Ordering> {
    a.f().partial_cmp(&b.f()).context("unordered numeric comparison")
}
/// `max(a, b)`: the first wins a tie.
fn max(a: Num, b: Num) -> Result<Num> {
    Ok(if order(b, a)?.is_gt() { b } else { a })
}
/// `min(a, b)`: the first wins a tie.
fn min(a: Num, b: Num) -> Result<Num> {
    Ok(if order(b, a)?.is_lt() { b } else { a })
}
fn div(a: Num, b: Num) -> Result<Num> {
    ensure!(b.f() != 0., "division by zero");
    Ok(a.div(b))
}
fn pow(a: Num, b: Num) -> Num {
    let value = a.f().powf(b.f());
    match (a, b) {
        (Num::I(_), Num::I(_)) if value.is_finite() && value.fract() == 0. => Num::I(value as i64),
        _ => Num::F(value),
    }
}
fn sqrt(x: Num) -> Result<Num> {
    let x = x.f();
    ensure!(x >= 0., "math domain error");
    Ok(Num::F(x.sqrt()))
}
/// `math.tan(math.radians(deg))`.
fn tan_deg(deg: f64) -> f64 {
    num::radians(deg).tan()
}

// ---------------------------------------------------------------------------------------------
// Frames and runs.

/// `F[body].at(port)`.
fn at(frames: &Val, body: &str, port: &str) -> Result<[Num; 3]> {
    three(&py::method(&frames.get(s(body))?, "at", vec![s(port)])?)
}
/// `R.bent(*args, **kwargs)`.
fn bent(st: &State, args: Vec<Val>, kwargs: Vec<(&str, Val)>) -> Result<Val> {
    py::call_kw(&st.r.attr("bent")?, args, kwargs)
}
/// `{names} <= set(of)` as the runtime compares two sets.
fn subset(names: &[&str], of: &Val) -> Result<bool> {
    let wanted = Val::set_values(names.iter().map(|&name| s(name)).collect());
    let have = Val::set_values(of.iter()?);
    interop::compare("le", wanted, have)?.truthy()
}

/// A foam-assembly cap conduit's station, from the enclosure assembly.
pub fn ea_cap(rt: &Rt, name: &Val) -> Result<Val> {
    py::method(&rt.import("enclosure_assembly")?, "cap_conduit", vec![name.clone()])
}

fn ends(ml: &Val, v: &Val) -> Result<[&'static str; 2]> {
    let arg = ml.attr("P")?.get(v.clone())?.get(s("arg"))?;
    Ok(if order(Num::of(&arg)?, Num::I(0))?.is_gt() { ["front", "back"] } else { ["back", "front"] })
}
/// A valve's (inlet, outlet) ends.
pub fn valve_ends(rt: &Rt, v: &Val) -> Result<[&'static str; 2]> {
    ends(&state(rt)?.ml, v)
}

/// A flavor valve's outlet carried out past its reducer: `(point, axis)`.
pub fn flavor_outlet(rt: &Rt, v: &Val) -> Result<Val> {
    let st = state(rt)?;
    let end = s(ends(&st.ml, v)?[1]);
    let mouth = py::call(&st.ml.attr("port")?, vec![v.clone(), end.clone()])?;
    let axis = py::call(&st.ml.attr("port_axis")?, vec![v.clone(), end])?;
    let (mouth, along, proud) = (three(&mouth)?, three(&axis)?, st.proud_length()?);
    Ok(Val::Tuple(vec![Num::vals(&[0, 1, 2].map(|i| mouth[i].add(along[i].mul(proud)))), axis]))
}

/// Every placed (or bounded) body's frame, its ports carried into place.
pub fn frames(rt: &Rt, placed: &Val, carries: &Val, bounds: &Val) -> Result<Val> {
    let st = state(rt)?;
    let out = Val::dict(vec![]);
    let bounds = if bounds.truthy()? { bounds.clone() } else { Val::dict(vec![]) };
    let parts = rt.import("above_core_parts")?;
    // The runtime's `dict.fromkeys` keeps every key it is given, repeats included.
    let mut names = st.stations.iter()?;
    names.extend(placed.iter()?);
    names.extend(bounds.iter()?);
    for name in names {
        let unplaced = !placed.contains(&name)? && !bounds.contains(&name)?;
        if unplaced || !carries.contains(&name)? {
            continue;
        }
        let carry = carries.get(name.clone())?;
        let native = py::method(&parts, "port_stations", vec![name.clone()])?;
        let table = Val::dict(vec![]);
        if !matches!(native, Val::None) {
            for item in py::method(&native, "items", vec![])?.iter()? {
                let row = py::unpack(&item, 2)?;
                let station = py::unpack(&row[1], 3)?;
                let mut carried = py::call(&carry, vec![Val::Tuple(vec![station[0].clone(), station[1].clone()])])?.iter()?;
                carried.push(station[2].clone());
                table.set(row[0].clone(), Val::Tuple(carried))?;
            }
            out.set(name.clone(), frame(rt, &st, &name, placed, &table, &bounds)?)?;
            continue;
        }
        let ports = py::method(&st.stations, "get", vec![name.clone()])?;
        if matches!(ports, Val::None) {
            continue;
        }
        for item in py::method(&ports, "items", vec![])?.iter()? {
            let row = py::unpack(&item, 2)?;
            let entry = py::unpack(&row[1], 2)?;
            let carried = py::call(&carry, vec![py::call(&entry[0], vec![])?])?;
            let carried = py::unpack(&carried, 2)?;
            let axis = Val::Tuple(carried[1].iter()?);
            table.set(row[0].clone(), Val::Tuple(vec![carried[0].clone(), axis, entry[1].clone()]))?;
        }
        out.set(name.clone(), frame(rt, &st, &name, placed, &table, &bounds)?)?;
    }
    Ok(out)
}

/// One body's routing frame: boxed from its placed solid, or from its stated bounds.
fn frame(rt: &Rt, st: &State, name: &Val, placed: &Val, ports: &Val, bounds: &Val) -> Result<Val> {
    if !bounds.contains(name)? {
        let solid = placed.get(name.clone())?;
        return py::call(&st.r.attr("frame")?, vec![name.clone(), solid, ports.clone()]);
    }
    let namespace = rt.member("types", "SimpleNamespace")?;
    let limits = py::unpack(&bounds.get(name.clone())?, 2)?;
    let values = Val::dict(vec![]);
    for (key, value) in ["xmin", "ymin", "zmin"].into_iter().zip(limits[0].iter()?) {
        values.set(s(key), value)?;
    }
    for (key, value) in ["xmax", "ymax", "zmax"].into_iter().zip(limits[1].iter()?) {
        values.set(s(key), value)?;
    }
    let bb = namespace.call(vec![], super::rt::keyword_items(values)?)?;
    py::call_kw(&st.r.attr("frame")?, vec![name.clone(), Val::None, ports.clone()], vec![("bb", bb)])
}

/// The runs between the placed bodies. The runtime orders the two sets of each `<=` as numbers,
/// so the first test raises once the frames are made.
pub fn build_runs(rt: &Rt, placed: &Val, carries: &Val) -> Result<Val> {
    let frames = frames(rt, placed, carries, &Val::None)?;
    let has = |names: &[&str]| subset(names, &frames);
    let f = &frames;
    let mut runs = vec![];
    if has(&["compressor", "foam-assembly"])? {
        runs.push(refrig_3(rt, f)?);
    }
    if has(&["compressor", "condenser+fan"])? {
        runs.push(refrig_1(rt, f)?);
    }
    if has(&["condenser+fan", "foam-assembly"])? {
        runs.push(refrig_2(rt, f)?);
    }
    if has(&["vk-solenoid", "pump-elbow-suction"])? {
        runs.push(water_7(rt, f)?);
    }
    if has(&["pump-elbow-discharge", "discharge-chain"])? {
        runs.push(water_6(rt, f)?);
    }
    if has(&["discharge-chain", "foam-assembly"])? {
        runs.push(water_5(rt, f)?);
    }
    if has(&["asse1022-assembly", "water-split"])? {
        runs.push(water_2(rt, f)?);
    }
    if has(&["water-split", "flow-regulator"])? {
        runs.push(fluid_1(rt, f)?);
    }
    if has(&["water-split", "vk-solenoid"])? {
        runs.push(water_3(rt, f)?);
    }
    if has(&["co2-inlet", "wr1110"])? {
        runs.push(co2_0(rt, f)?);
    }
    if has(&["gasher-co2", "wr1110", "foam-assembly"])? {
        runs.push(co2_1(rt, f)?);
    }
    if has(&["gasher-co2", "foam-assembly"])? {
        runs.push(co2_2(rt, f)?);
    }
    if has(&["flow-regulator", "valve-v-a", "water-split"])? && subset(&["coil-v-a", "g-ganen-pump"], placed)? {
        runs.push(fluid_2(rt, f)?);
    }
    if has(&["foam-assembly", "digiten-flow"])? {
        runs.push(carb_1(rt, f)?);
    }
    if has(&["digiten-flow", "bulkhead-carb"])? {
        runs.push(carb_2(rt, f)?);
    }
    if has(&["valve-v-j", "bulkhead-flavor-b"])? && f.contains(&s("valve-v-i"))? {
        runs.push(fluid_28(rt, f, placed)?);
    }
    if has(&["valve-v-g", "bulkhead-flavor-a"])? && f.contains(&s("valve-v-f"))? {
        runs.push(fluid_18(rt, f, placed)?);
    }
    if has(&["valve-v-i", "foam-assembly"])? {
        runs.push(fluid_24(rt, f)?);
    }
    if has(&["valve-v-h", "foam-assembly"])? {
        runs.push(fluid_26(rt, f)?);
    }
    if has(&["valve-v-f", "foam-assembly"])? {
        runs.push(fluid_14(rt, f, placed)?);
    }
    if has(&["valve-v-e", "foam-assembly"])? {
        runs.push(fluid_16(rt, f)?);
    }
    Ok(Val::list(runs))
}

/// The runs drawn once the funnel's drain union is seated; the same `<=` raises as in `build_runs`.
pub fn build_seated_runs(rt: &Rt, placed: &Val, carries: &Val) -> Result<Val> {
    let frames = frames(rt, placed, carries, &Val::None)?;
    let mut runs = vec![];
    if subset(&["funnel-drain-union", "valve-v-b"], &frames)? {
        runs.push(fluid_4(rt, &frames)?);
    }
    Ok(Val::list(runs))
}

pub fn co2_0(rt: &Rt, _frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    bent(&st, vec![s("co2-0"), s("co2-inlet.inboard"), s("wr1110.inlet")], vec![("kind", s("co2")), ("note", s(NOTE_CO2_0))])
}

pub fn co2_1(rt: &Rt, frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    let enc = rt.import("enclosure")?;
    let src = at(frames, "wr1110", "outlet")?;
    let dst = at(frames, "gasher-co2", "inlet")?;
    let water_y = at(frames, "foam-assembly", "carb-water-out")?[1].sub(f(CARB_1_FORWARD_LEAN));
    let slip = Num::of(&enc.attr("fits")?.attr("slip")?)?;
    let wall = Num::of(&enc.attr("wall")?)?;
    let cradle_aft = water_y.add(div(st.split_tube_d, Num::I(2))?).add(slip).add(wall);
    let under = min(src[1], dst[1])?.sub(f(2.0).mul(st.tube_bend)).add(f(1.0));
    let outlet_d = Num::of(&py::method(&frames.get(s("wr1110"))?, "diam", vec![s("outlet")])?)?;
    let floor = Num::of(&st.card.attr("CLEARANCE_FLOOR")?)?;
    let turn_y = max(under, cradle_aft.add(div(outlet_d, Num::I(2))?).add(floor).add(f(0.1)))?;
    bent(
        &st,
        vec![
            s("co2-1"),
            s("wr1110.outlet"),
            point(src[0], turn_y, src[2]),
            point(dst[0], turn_y, dst[2]),
            s("gasher-co2.inlet"),
        ],
        vec![("kind", s("co2")), ("note", s(NOTE_CO2_1))],
    )
}

pub fn water_3(rt: &Rt, frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    let (split, vk) = (frames.get(s("water-split"))?, frames.get(s("vk-solenoid"))?);
    let src = three(&py::method(&split, "at", vec![s("to-vk")])?)?;
    let dst = three(&py::method(&vk, "at", vec![s("inlet")])?)?;
    let z = dst[2].sub(f(CROSS_DROP));
    let [dx0, dx1] = CROSS_DODGE_SPAN.map(f);
    let args = vec![
        s("water-3"),
        s("water-split.to-vk"),
        point(src[0], src[1], z.sub(f(CROSS_RISE))),
        point(f(CHANNEL_X), st.channel_entry_y, z.sub(f(CROSS_RISE))),
        point(f(CHANNEL_X), st.cross_y, z),
        point(dx0.sub(f(CROSS_DODGE_RAMP)), st.cross_y, z),
        point(dx0, st.cross_dodge_y, z),
        point(dx1, st.cross_dodge_y, z),
        point(f(CROSS_LIFT_X), st.cross_y, z),
        point(dst[0], f(CROSS_APPROACH_Y), dst[2]),
        s("vk-solenoid.inlet"),
    ];
    let lead = Val::Tuple(vec![Val::None, st.ml.attr("STUB")?]);
    bent(&st, args, vec![("kind", s("water")), ("lead", lead), ("note", s(NOTE_WATER_3))])
}

pub fn fluid_1(rt: &Rt, frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    let (split, reg) = (frames.get(s("water-split"))?, frames.get(s("flow-regulator"))?);
    let src = three(&py::method(&split, "at", vec![s("to-flavor")])?)?;
    let dst = three(&py::method(&reg, "at", vec![s("inlet")])?)?;
    let fore = src[1].sub(st.tube_bend);
    let lane_x = src[0].add(f(FLUID_1_INBOARD));
    let approach = three(&py::method(&reg, "normal", vec![s("inlet")])?)?;
    let join = [0, 1, 2].map(|k| dst[k].add(f(22.0).mul(approach[k])));
    bent(
        &st,
        vec![
            s("fluid-1"),
            s("water-split.to-flavor"),
            point(src[0], fore, src[2]),
            point(lane_x, fore, src[2]),
            point(lane_x, join[1].sub(f(FLUID_1_DIAGONAL)), src[2]),
            Num::vals(&join),
            s("flow-regulator.inlet"),
        ],
        vec![
            ("kind", s("fluid")),
            ("bend", st.tube_bend.val()),
            ("lead", py::ftuple(&[0.0, FLUID_1_APPROACH])),
            ("note", s(NOTE_FLUID_1)),
        ],
    )
}

pub fn water_2(rt: &Rt, frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    let supply = at(frames, "water-split", "supply")?;
    bent(
        &st,
        vec![
            s("water-2"),
            s("asse1022-assembly.tube-out"),
            point(supply[0], supply[1].add(f(WATER_2_RUN)), supply[2]),
            s("water-split.supply"),
        ],
        vec![
            ("kind", s("water")),
            ("bend", st.tube_bend.val()),
            ("lead", py::ftuple(&[WATER_2_LEAD, 0.0])),
            ("note", s(NOTE_WATER_2)),
        ],
    )
}

pub fn water_7(rt: &Rt, _frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    bent(
        &st,
        vec![s("water-7"), s("vk-solenoid.outlet"), s("pump-elbow-suction.tube")],
        vec![
            ("kind", s("water")),
            ("bend", st.tube_bend.val()),
            ("lead", py::ftuple(&SUCTION_LEAD)),
            ("note", s(NOTE_WATER_7)),
        ],
    )
}

pub fn water_6(rt: &Rt, _frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    bent(
        &st,
        vec![s("water-6"), s("pump-elbow-discharge.tube"), s("discharge-chain.inlet")],
        vec![
            ("kind", s("water")),
            ("bend", st.tube_bend.val()),
            ("lead", Val::Tuple(vec![Val::Float(DISCHARGE_LEAD_STRAIGHT), st.tube_bend.val()])),
            ("note", s(NOTE_WATER_6)),
        ],
    )
}

pub fn water_5(rt: &Rt, _frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    bent(
        &st,
        vec![s("water-5"), s("discharge-chain.tube-port"), s("foam-assembly.water-in")],
        vec![
            ("kind", s("water")),
            ("lead", st.tube_bend.val()),
            ("skew", st.collet_to_cap()?),
            ("note", s(NOTE_WATER_5)),
        ],
    )
}

pub fn co2_2(rt: &Rt, frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    let out = at(frames, "gasher-co2", "outlet")?;
    let bore = at(frames, "foam-assembly", "co2-in")?;
    let turn_y = out[1].add(f(2.0).mul(st.tube_bend));
    bent(
        &st,
        vec![
            s("co2-2"),
            s("gasher-co2.outlet"),
            point(out[0], turn_y, out[2]),
            point(bore[0], turn_y, out[2]),
            point(bore[0], bore[1], out[2]),
            s("foam-assembly.co2-in"),
        ],
        vec![
            ("kind", s("co2")),
            ("lead", Val::Tuple(vec![st.tube_bend.val(), st.tube_bend.val()])),
            ("skew", st.collet_to_cap()?),
            ("note", s(NOTE_CO2_2)),
        ],
    )
}

pub fn fluid_2(rt: &Rt, frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    let (reg, vk_a) = (frames.get(s("flow-regulator"))?, frames.get(s("valve-v-a"))?);
    let out = three(&py::method(&reg, "at", vec![s("outlet")])?)?;
    let inlet = three(&py::method(&vk_a, "at", vec![s("inlet")])?)?;
    let heading = three(&py::method(&reg, "normal", vec![s("outlet")])?)?;
    let turn = [0, 1, 2].map(|k| out[k].add(f(25.0).mul(heading[k])));
    let cross_z = at(frames, "foam-assembly", "carb-water-out")?[2].add(f(FLUID_2_OVER_CAP));
    let inlet_turn = inlet[1].add(st.tube_bend);
    bent(
        &st,
        vec![
            s("fluid-2"),
            s("flow-regulator.outlet"),
            Num::vals(&turn),
            point(f(FLUID_2_RETURN_X), turn[1], cross_z),
            point(f(FLUID_2_RETURN_X), f(FLUID_2_RETURN_FORE_Y), cross_z),
            point(inlet[0].add(f(FLUID_2_DESCENT_EAST)), inlet_turn, cross_z),
            point(inlet[0], inlet_turn, inlet[2]),
            s("valve-v-a.inlet"),
        ],
        vec![
            ("kind", s("fluid")),
            ("bend", st.tube_bend.val()),
            ("lead", Val::Tuple(vec![Val::Float(8.0), st.tube_bend.val()])),
            ("note", s(NOTE_FLUID_2)),
        ],
    )
}

pub fn fluid_4(rt: &Rt, frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    let drain = at(frames, "funnel-drain-union", "outlet")?;
    let inlet = at(frames, "valve-v-b", "inlet")?;
    let fall = drain[2].sub(inlet[2]);
    let reach = pow(Num::I(2).mul(st.tube_bend), Num::I(2)).sub(pow(fall, Num::I(2)));
    let flank_x = inlet[0].sub(sqrt(reach)?).sub(f(0.25));
    let turn_y = f(FLUID_4_CROSS_Y).add(Num::I(2).mul(st.tube_bend));
    bent(
        &st,
        vec![
            s("fluid-4"),
            s("funnel-drain-union.outlet"),
            point(drain[0], f(FLUID_4_CROSS_Y), drain[2]),
            point(flank_x, f(FLUID_4_CROSS_Y), drain[2]),
            point(flank_x, turn_y, drain[2]),
            point(inlet[0], turn_y, inlet[2]),
            s("valve-v-b.inlet"),
        ],
        vec![("kind", s("fluid")), ("bend", st.tube_bend.val()), ("note", s(NOTE_FLUID_4))],
    )
}

pub fn carb_1(rt: &Rt, frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    let bore = at(frames, "foam-assembly", "carb-water-out")?;
    let inlet = at(frames, "digiten-flow", "inlet")?;
    let deck_y = bore[1].sub(f(CARB_1_FORWARD_LEAN));
    bent(
        &st,
        vec![
            s("carb-1"),
            s("foam-assembly.carb-water-out"),
            point(bore[0], deck_y, inlet[2]),
            point(inlet[0], deck_y, inlet[2]),
            s("digiten-flow.inlet"),
        ],
        vec![
            ("kind", s("water")),
            ("lead", Val::Tuple(vec![st.tube_bend.val(), st.tube_bend.val()])),
            ("skew", st.cap_to_collet()?),
            ("note", s(NOTE_CARB_1)),
        ],
    )
}

pub fn carb_2(rt: &Rt, _frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    bent(
        &st,
        vec![s("carb-2"), s("digiten-flow.outlet"), s("bulkhead-carb.tube-in")],
        vec![
            ("kind", s("water")),
            ("lead", Val::Float(4.0)),
            ("bend", st.tube_bend.val()),
            ("note", s(NOTE_CARB_2)),
        ],
    )
}

/// Where fluid-18 bears through the reservoir-A cap, carried off the core's draw port.
fn gate_a_anchor(st: &State, frames: &Val) -> Result<[Num; 3]> {
    let draw = at(frames, "foam-assembly", "reservoir-a")?;
    let anchor = py::item(&st.cc.attr("cap_anchors")?, "fluid-18")?;
    let local = py::snapshot(&py::item(&st.cc.attr("cap_conduits")?, "reservoir-a")?)?;
    let centre = py::snapshot(&anchor.attr("centre")?)?;
    Ok([
        draw[0].add(idx(&centre, 1)?).sub(idx(&local, 1)?),
        draw[1].add(idx(&local, 0)?).sub(idx(&centre, 0)?),
        draw[2].add(Num::of(&anchor.attr("over_face")?)?),
    ])
}

/// The flavor gates' cruise height under V-I's outlet.
pub fn gate_cruise(rt: &Rt, v_i_outlet_z: Num) -> Result<Num> {
    let st = state(rt)?;
    let gap = Num::of(&st.ml.attr("FORE_STUB_GAP")?)?;
    Ok(v_i_outlet_z.sub(gap).add(st.tube_bend).sub(st.split_tube_d).sub(f(GATE_STUB_CLEAR)))
}

/// `STATIONS[body][port][0]()`.
pub fn station(rt: &Rt, body: &Val, port: &Val) -> Result<Val> {
    let st = state(rt)?;
    py::call(&st.stations.get(body.clone())?.get(port.clone())?.get(Val::Int(0))?, vec![])
}

fn gate_climb_under_cruise(rt: &Rt, st: &State, frames: &Val) -> Result<Num> {
    let cruise = gate_cruise(rt, at(frames, "valve-v-i", "outlet")?[2])?;
    let outlet = at(frames, "valve-v-j", "outlet")?;
    let drop = Num::of(&st.ml.attr("OUTER_AFT_DROP")?)?;
    max(cruise, outlet[2].add(drop).add(f(GATE_B_CLIMB)))
}

pub fn fluid_28(rt: &Rt, frames: &Val, _solids: &Val) -> Result<Val> {
    let st = state(rt)?;
    let gate = at(frames, "valve-v-j", "outlet")?;
    let tin = at(frames, "bulkhead-flavor-b", "tube-in")?;
    let climb = gate_climb_under_cruise(rt, &st, frames)?;
    let raised = climb.add(f(GATE_B_DRAIN_RETURN_RISE));
    let west = tin[0].sub(f(GATE_B_RETURN_WEST));
    let bends = Val::dict((1..=7).map(|corner| (Val::Int(corner), Val::Float(if corner <= 2 { 25.0 } else { 25.4 }))).collect());
    bent(
        &st,
        vec![
            s("fluid-28"),
            s("valve-v-j.outlet"),
            point(gate[0], gate[1], climb),
            point(tin[0], gate[1].add(f(GATE_B_JOG_LEG)), climb),
            point(tin[0], f(302.0), climb),
            point(tin[0], f(340.0), raised),
            point(west, f(365.0), raised),
            point(west, f(GATE_B_RETURN_HOLD_Y), raised),
            s("bulkhead-flavor-b.tube-in"),
        ],
        vec![
            ("kind", s("fluid")),
            ("lead", py::ftuple(&[0.0, GATE_B_UNION_APPROACH])),
            ("bend", bends),
            ("note", s(NOTE_FLUID_28)),
        ],
    )
}

pub fn fluid_18(rt: &Rt, frames: &Val, _solids: &Val) -> Result<Val> {
    let st = state(rt)?;
    let gate = at(frames, "valve-v-g", "outlet")?;
    let tin = at(frames, "bulkhead-flavor-a", "tube-in")?;
    let [anchor_x, _anchor_y, bearing_z] = gate_a_anchor(&st, frames)?;
    let fore_z = at(frames, "foam-assembly", "reservoir-a")?[2].add(f(GATE_A_FORE_HEIGHT));
    let draw_z = at(frames, "foam-assembly", "reservoir-a")?[2];
    let pad = Num::of(&py::method(&st.pump, "observed_pad_upper_z", vec![])?)?;
    let low_z = draw_z.add(pad).add(div(st.split_tube_d, f(2.0))?).add(f(LANE_CLEAR));
    let rise_y = f(GATE_A_UNION_JOIN_Y).add(f(GATE_A_UNION_LEVEL_RUN));
    bent(
        &st,
        vec![
            s("fluid-18"),
            s("valve-v-g.outlet"),
            point(gate[0], gate[1], f(GATE_A_FRONT_Z)),
            point(f(GATE_A_FRONT_JOIN_X), f(GATE_A_FRONT_Y), f(GATE_A_FRONT_Z)),
            point(f(GATE_A_OUTER_X), f(GATE_A_FRONT_Y), f(GATE_A_FRONT_Z)),
            point(f(GATE_A_OUTER_X), f(GATE_A_DESCENT_START_Y), f(GATE_A_FRONT_Z)),
            point(anchor_x, f(GATE_A_BEARING_JOIN_Y), bearing_z),
            point(anchor_x, f(GATE_A_BEARING_EXIT_Y), bearing_z),
            point(f(GATE_A_WEST_X), f(GATE_A_LOW_LANE_JOIN_Y), fore_z),
            point(f(GATE_A_WEST_X), f(GATE_A_RETURN_START_Y), fore_z),
            point(tin[0], f(GATE_A_UNION_JOIN_Y), low_z),
            point(tin[0], rise_y, low_z),
            point(tin[0], rise_y.add(f(GATE_A_RISE_RUN)), tin[2]),
            s("bulkhead-flavor-a.tube-in"),
        ],
        vec![("kind", s("fluid")), ("bend", Val::Float(25.0)), ("note", s(NOTE_FLUID_18))],
    )
}

/// The fill-A lane, clear forward of V-K's body.
fn fill_a_lane_y(st: &State, solids: &Val) -> Result<Num> {
    let bb = py::method(&solids.get(s("vk-solenoid"))?, "BoundingBox", vec![])?;
    Ok(Num::of(&bb.attr("ymin")?)?.sub(st.split_tube_d).sub(f(LANE_CLEAR)))
}
/// The reservoir-A cap's face height at fluid-14's anchor.
fn fill_a_cap_z(st: &State, frames: &Val) -> Result<Num> {
    let bore = at(frames, "foam-assembly", "reservoir-a-fill")?;
    let over = Num::of(&py::method(&st.cc, "cap_anchor_axis_over_face", vec![s("fluid-14")])?)?;
    Ok(bore[2].add(over))
}
/// Where fill-A turns behind the pump's suction elbow.
fn fill_a_turn_y(st: &State, frames: &Val) -> Result<Num> {
    let suction = at(frames, "g-ganen-pump", "suction")?;
    Ok(suction[1].add(div(st.elbow_cuff_d.add(st.split_tube_d), f(2.0))?).add(f(LANE_CLEAR)))
}

pub fn fluid_14(rt: &Rt, frames: &Val, solids: &Val) -> Result<Val> {
    let st = state(rt)?;
    let gate = at(frames, "valve-v-f", "outlet")?;
    let bore = at(frames, "foam-assembly", "reservoir-a-fill")?;
    let draw = at(frames, "foam-assembly", "reservoir-a")?;
    let centre = py::snapshot(&py::item(&st.cc.attr("cap_anchors")?, "fluid-14")?.attr("centre")?)?;
    let local = py::snapshot(&py::item(&st.cc.attr("cap_conduits")?, "reservoir-a")?)?;
    let lane_x = draw[0].add(idx(&centre, 1)?).sub(idx(&local, 1)?);
    let fall = fill_a_lane_y(&st, solids)?.add(st.tube_bend);
    let cap = fill_a_cap_z(&st, frames)?;
    let draw = at(frames, "foam-assembly", "reservoir-a")?;
    let bearing_y = draw[1].add(idx(&local, 0)?).sub(idx(&centre, 0)?);
    let kink = st.tube_bend.mul(f((FILL_A_VALVE_DROP.atan2(FILL_A_VALVE_RETURN_RUN) / 2.0).tan()));
    let valve_return = bearing_y.sub(div(st.fill_a_bearing_straight, f(2.0))?).sub(kink);
    let valve_under = cap.sub(f(FILL_A_VALVE_DROP));
    let hose_fall_end = at(frames, "pump-elbow-suction", "tube")?[1].sub(st.tube_bend);
    let hose_fall_start = hose_fall_end.sub(f(FILL_A_HOSE_FALL_RUN));
    let hose_under = cap.sub(f(FILL_A_HOSE_DROP));
    let mut args = vec![
        s("fluid-14"),
        s("valve-v-f.outlet"),
        point(
            gate[0],
            gate[1].add(f(FILL_A_GATE_LEAD).mul(f(tan_deg(FILL_A_GATE_LEAN_DEG)))),
            gate[2].add(f(FILL_A_GATE_LEAD)),
        ),
    ];
    args.push(point(lane_x, fill_a_lane_y(&st, solids)?, f(FILL_A_LANE_Z)));
    args.extend([
        point(lane_x, fall, f(FILL_A_LANE_Z)),
        point(lane_x, fall.add(f(FILL_A_FALL_RUN)), valve_under),
        point(lane_x, valve_return.sub(f(FILL_A_VALVE_RETURN_RUN)), valve_under),
        point(lane_x, valve_return, cap),
        point(lane_x, hose_fall_start, cap),
        point(lane_x, hose_fall_end, hose_under),
    ]);
    args.push(point(lane_x, fill_a_turn_y(&st, frames)?, hose_under));
    args.extend([point(bore[0], bore[1], cap), s("foam-assembly.reservoir-a-fill")]);
    bent(
        &st,
        args,
        vec![
            ("kind", s("fluid")),
            ("bend", st.tube_bend.val()),
            ("skew", st.collet_to_cap()?),
            ("note", s(NOTE_FLUID_14)),
        ],
    )
}

/// A point on the reservoir-A cap, `cap_xy` in the cap's own frame, `over_face` above its face.
/// The arguments are read where the source reads them, so a bad one fails at the same step.
fn on_cap(st: &State, frames: &Val, cap_xy: &Val, over_face: &Val) -> Result<[Num; 3]> {
    let reference = at(frames, "foam-assembly", "reservoir-a")?;
    let local = py::snapshot(&py::item(&st.cc.attr("cap_conduits")?, "reservoir-a")?)?;
    Ok([
        reference[0].add(idx(cap_xy, 1)?).sub(idx(&local, 1)?),
        reference[1].add(idx(&local, 0)?).sub(idx(cap_xy, 0)?),
        reference[2].add(Num::of(over_face)?),
    ])
}

/// A gate's lead: `lead` up off the gate, leaning toward `toward` at the draw gates' lean.
fn gate_lead(gate: &Val, toward: &Val, lead: &Val) -> Result<[Num; 3]> {
    let dx = idx(toward, 0)?.sub(idx(gate, 0)?);
    let dy = idx(toward, 1)?.sub(idx(gate, 1)?);
    let reach = f(num::hypot2(dx.f(), dy.f()));
    let lead = Num::of(lead)?;
    let lean = lead.mul(f(tan_deg(DRAW_GATE_LEAN_DEG)));
    Ok([
        idx(gate, 0)?.add(div(lean.mul(dx), reach)?),
        idx(gate, 1)?.add(div(lean.mul(dy), reach)?),
        idx(gate, 2)?.add(lead),
    ])
}

pub fn fluid_16(rt: &Rt, frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    let bore = at(frames, "foam-assembly", "reservoir-a")?;
    let gate = at(frames, "valve-v-e", "inlet")?;
    let cruise = bore[2].add(f(DRAW_A_CRUISE));
    let neck_in = on_cap(&st, frames, &py::ftuple(&DRAW_A_NECK_IN), &Val::Float(0.0))?;
    let neck_out = on_cap(&st, frames, &py::ftuple(&DRAW_A_NECK_OUT[..2]), &Val::Float(DRAW_A_NECK_OUT[2]))?;
    let approach = [0, 1, 2].map(|i| gate[i].add(f(DRAW_A_APPROACH[i])));
    let lead = gate_lead(&Num::vals(&gate), &Num::vals(&approach), &Val::Float(DRAW_A_GATE_LEAD))?;
    bent(
        &st,
        vec![
            s("fluid-16"),
            s("foam-assembly.reservoir-a"),
            point(bore[0], bore[1], cruise),
            point(neck_in[0], neck_in[1], cruise),
            Num::vals(&neck_out),
            Num::vals(&approach),
            Num::vals(&lead),
            s("valve-v-e.inlet"),
        ],
        vec![
            ("kind", s("fluid")),
            ("bend", st.tube_bend.val()),
            ("skew", st.cap_to_collet()?),
            ("note", s(NOTE_FLUID_16)),
        ],
    )
}

pub fn fluid_24(rt: &Rt, frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    let mouth = at(frames, "valve-v-i", "outlet")?;
    let bore = at(frames, "foam-assembly", "reservoir-b-fill")?;
    let cruise = mouth[2].add(st.reservoir_b_cruise);
    let lane_x = mouth[0];
    let lead_aft = st.reservoir_b_cruise.mul(f(tan_deg(RESERVOIR_B_GATE_LEAN_DEG)));
    bent(
        &st,
        vec![
            s("fluid-24"),
            s("valve-v-i.outlet"),
            point(lane_x, mouth[1].add(lead_aft), cruise),
            point(lane_x, f(FILL_B_LEAN_Y), cruise),
            point(bore[0], f(FILL_B_JOIN_Y), cruise),
            point(bore[0], bore[1], cruise),
            s("foam-assembly.reservoir-b-fill"),
        ],
        vec![
            ("kind", s("fluid")),
            ("bend", st.tube_bend.val()),
            ("skew", st.collet_to_cap()?),
            ("note", s(NOTE_FLUID_24)),
        ],
    )
}

pub fn fluid_26(rt: &Rt, frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    let bore = at(frames, "foam-assembly", "reservoir-b")?;
    let gate = at(frames, "valve-v-h", "inlet")?;
    let approach = [0, 1, 2].map(|i| gate[i].add(f(DRAW_B_APPROACH[i])));
    let lead = gate_lead(&Num::vals(&gate), &Num::vals(&approach), &Val::Float(DRAW_B_GATE_LEAD))?;
    bent(
        &st,
        vec![
            s("fluid-26"),
            s("foam-assembly.reservoir-b"),
            point(bore[0], bore[1], bore[2].add(f(DRAW_B_CRUISE))),
            Num::vals(&approach),
            Num::vals(&lead),
            s("valve-v-h.inlet"),
        ],
        vec![
            ("kind", s("fluid")),
            ("bend", st.tube_bend.val()),
            ("skew", st.cap_to_collet()?),
            ("note", s(NOTE_FLUID_26)),
        ],
    )
}

pub fn refrig_3(rt: &Rt, _frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    bent(
        &st,
        vec![s("refrig-3"), s("compressor.refrig-suction"), s("foam-assembly.evap-outlet")],
        vec![
            ("kind", s("refrigerant")),
            ("bend", st.cu_bend.val()),
            ("lead", Val::Float(CU_LEAD)),
            ("note", s(NOTE_REFRIG_3)),
        ],
    )
}

pub fn refrig_1(rt: &Rt, _frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    bent(
        &st,
        vec![s("refrig-1"), s("compressor.refrig-discharge"), s("condenser+fan.refrig-inlet")],
        vec![("kind", s("refrigerant")), ("note", s(NOTE_REFRIG_1))],
    )
}

pub fn refrig_2(rt: &Rt, _frames: &Val) -> Result<Val> {
    let st = state(rt)?;
    bent(
        &st,
        vec![s("refrig-2"), s("condenser+fan.refrig-outlet"), s("foam-assembly.evap-inlet")],
        vec![
            ("kind", s("refrigerant")),
            ("lead", Val::Float(2.0)),
            ("min_bend", Val::Float(8.0)),
            ("note", s(NOTE_REFRIG_2)),
        ],
    )
}

/// The tube solids of the runs longer than a butt joint.
pub fn tubes(rt: &Rt, runs: &Val) -> Result<Val> {
    let st = state(rt)?;
    let mut out = vec![];
    for run in runs.iter()? {
        let length = Num::of(&run.attr("length")?)?;
        if order(length, st.butt_max()?)?.is_gt() {
            let name = format!("tube-{}", num::fmtv(&run.attr("id")?, "")?);
            out.push(Val::Tuple(vec![s(name), py::call(&st.r.attr("tube")?, vec![run.clone()])?]));
        }
    }
    Ok(Val::list(out))
}

/// Prints each run and every shortfall `_routing` recorded.
pub fn report(rt: &Rt, runs: &Val) -> Result<Val> {
    if !runs.truthy()? {
        return Ok(Val::None);
    }
    let st = state(rt)?;
    rt.print("\nruns".into())?;
    for run in runs.iter()? {
        let id = num::fmtv(&run.attr("id")?, "12")?;
        let frm = num::fmtv(&run.attr("frm")?, "28")?;
        let to = num::fmtv(&run.attr("to")?, "28")?;
        let length = num::fmtv(&run.attr("length")?, "7.1f")?;
        let corners = num::fmti(run.attr("bends")?.len()? as i64, "");
        let tightest = num::fmtv(&run.attr("tightest")?, ".1f")?;
        let stock_min = st.r.attr("stock_min")?;
        let floor = num::fmtv(&py::call(&stock_min, vec![run.attr("kind")?, run.attr("diam")?])?, ".1f")?;
        rt.print(format!("  {id} {frm} → {to} {length} mm  {corners} corner(s) at R{tightest} (stock floor R{floor})"))?;
    }
    let blocked = py::snapshot(&st.blocked)?;
    let mut rows = vec![];
    for cid in blocked.iter()? {
        let why = blocked.get(cid.clone())?;
        rows.push((num::fmtv(&cid, "")?, num::fmtv(&why, "")?));
    }
    // The keys are run ids: strings, so their text orders them as `sorted` does.
    rows.sort();
    for (cid, why) in rows {
        rt.print(format!("  BLOCKED {cid}: {why}"))?;
    }
    Ok(Val::None)
}

// ---------------------------------------------------------------------------------------------
// The module's top level.

fn floats(ns: &Ns, rows: &[(&str, f64)]) -> Result<()> {
    for &(name, value) in rows {
        ns.set(name, Val::Float(value))?;
    }
    Ok(())
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::LINES))?;
    ns.set("math", rt.import("math")?)?;
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    ns.set("_here", Val::Path(here.clone()))?;
    let hw = here
        .ancestors()
        .skip(1)
        .find(|p| p.file_name().is_some_and(|name| name == "hardware"))
        .map(Path::to_path_buf)
        .context("no hardware folder above _lines.py")?;
    ns.set("_hw", Val::Path(hw.clone()))?;
    let mut folders = vec![hw.join("scripts"), here.parent().context("_lines.py folder")?.to_path_buf()];
    folders.extend(FOLDERS.iter().map(|folder| hw.join(folder)));
    for folder in folders {
        ns.set("_p", Val::Path(folder.clone()))?;
        py::sys_path_insert(rt, &py::path_str(&folder))?;
    }
    let mut modules: Vec<(&str, Val)> = vec![];
    for (alias, module) in IMPORTS {
        let value = rt.import(module)?;
        ns.set(alias, value.clone())?;
        modules.push((alias, value));
    }
    let module = |alias: &str| modules.iter().find(|(name, _)| *name == alias).map(|(_, value)| value.clone()).unwrap();
    let (r, cc, anchor_cap, asse, funnel, pump) =
        (module("R"), module("_cc"), module("_anchor_cap"), module("_asse"), module("_funnel"), module("_pump"));
    let (pump_elbow, dis, beduan, jg, drain_elbow, drain_bulkhead) = (
        module("_pump_elbow"),
        module("_dis"),
        module("_beduan"),
        module("_jg"),
        module("_drain_elbow"),
        module("_drain_bulkhead"),
    );
    let (flavor_reducer, neofit, flowreg, split, ml, comp) = (
        module("_flavor_reducer"),
        module("_neofit"),
        module("_flowreg"),
        module("_split"),
        module("_ml"),
        module("_comp"),
    );
    let (cond, copper, gas_chain, digiten, card) =
        (module("_cond"), module("_copper"), module("_gas_chain"), module("_digiten"), module("_card"));

    let blocked = r.attr("BLOCKED")?;
    ns.set("BLOCKED", blocked.clone())?;
    define(ns, rt, "_ea_cap", req(&["name"]), |rt, a| ea_cap(rt, &a[0]))?;
    let tube_d = split.attr("TUBE_D")?;
    let split_tube_d = Num::of(&tube_d)?;
    let tube_bend_val = py::call(&r.attr("stock_min")?, vec![s("water"), tube_d.clone()])?;
    let tube_bend = Num::of(&tube_bend_val)?;
    ns.set("TUBE_BEND", tube_bend_val.clone())?;
    let barb = Num::of(&pump_elbow.attr("BARB_OD_INSTALLED")?)?;
    let elbow_cuff_d = barb.add(f(2.0).mul(Num::of(&pump_elbow.attr("BAND_T")?)?));
    ns.set("ELBOW_CUFF_D", elbow_cuff_d.val())?;
    ns.set("SUCTION_LEAD", py::ftuple(&SUCTION_LEAD))?;
    ns.set("DISCHARGE_LEAD", Val::Tuple(vec![Val::Float(DISCHARGE_LEAD_STRAIGHT), tube_bend_val.clone()]))?;
    ns.set("CU_OD", Val::Float(CU_OD))?;
    let cu_bend_val = py::call(&r.attr("stock_min")?, vec![s("refrigerant"), Val::Float(CU_OD)])?;
    let cu_bend = Num::of(&cu_bend_val)?;
    ns.set("CU_BEND", cu_bend_val)?;
    ns.set("CU_LEAD", Val::Float(CU_LEAD))?;
    ns.set("CU_SUCTION_LANE", f(2.0).mul(cu_bend).val())?;
    let cap_bore_skew = cc.attr("cap_conduit_entry_skew")?;
    ns.set("CAP_BORE_SKEW", cap_bore_skew.clone())?;
    let adapters = py::merged(
        &gas_chain.attr("PORT_ADAPTERS")?,
        [("valve-v-g.outlet", s("flavor-reducer-v-g")), ("valve-v-j.outlet", s("flavor-reducer-v-j"))],
    )?;
    ns.set("PORT_ADAPTERS", adapters)?;

    // STATIONS: body -> port -> (station, bore), each station a callable giving (point, axis).
    let entry = |station: Val, diam: &Val| Val::Tuple(vec![station, diam.clone()]);
    let cu_od = Val::Float(CU_OD);
    let stations = Val::dict(vec![]);
    let mut foam: Vec<(&str, Val)> = CAP_CONDUITS
        .into_iter()
        .map(|name| (name, entry(lambda(rt, vec![], move |rt, _| ea_cap(rt, &s(name))), &tube_d)))
        .collect();
    for name in ["evap-outlet", "evap-inlet"] {
        foam.push((name, entry(call_station(rt, &copper, "station", vec![s(name)]), &cu_od)));
    }
    stations.set(s("foam-assembly"), py::dict(foam))?;
    let listed = |module: &Val, port: &'static str| {
        let module = module.clone();
        lambda(rt, vec![], move |_, _| py::method(&module, "stations", vec![])?.get(s(port)))
    };
    stations.set(
        s("compressor"),
        py::dict([
            ("refrig-suction", entry(listed(&comp, "refrig-suction"), &cu_od)),
            ("refrig-discharge", entry(listed(&comp, "refrig-discharge"), &cu_od)),
        ]),
    )?;
    stations.set(
        s("condenser+fan"),
        py::dict([
            ("refrig-outlet", entry(listed(&cond, "refrig-outlet"), &cu_od)),
            ("refrig-inlet", entry(listed(&cond, "refrig-inlet"), &cu_od)),
        ]),
    )?;
    let cuff = elbow_cuff_d.val();
    stations.set(
        s("g-ganen-pump"),
        py::dict([("suction", entry(pump.attr("suction")?, &cuff)), ("discharge", entry(pump.attr("discharge")?, &cuff))]),
    )?;
    let (elbow_port, elbow_d) = (pump_elbow.attr("tube_port")?, pump_elbow.attr("TUBE_D")?);
    stations.set(s("pump-elbow-suction"), py::dict([("tube", entry(elbow_port.clone(), &elbow_d))]))?;
    stations.set(s("pump-elbow-discharge"), py::dict([("tube", entry(elbow_port, &elbow_d))]))?;
    let (dis_outlet, dis_d) = (dis.attr("outlet")?, dis.attr("TUBE_OD")?);
    stations.set(
        s("discharge-chain"),
        py::dict([
            ("inlet", entry(dis.attr("inlet")?, &dis_d)),
            ("outlet", entry(dis_outlet.clone(), &dis_d)),
            ("tube-port", entry(dis_outlet, &dis_d)),
        ]),
    )?;
    stations.set(
        s("asse1022-assembly"),
        py::dict([
            ("tube-in", entry(call_station(rt, &asse, "port", vec![s("tube-in")]), &tube_d)),
            ("tube-out", entry(call_station(rt, &asse, "port", vec![s("tube-out")]), &tube_d)),
            ("vent-tip", entry(call_station(rt, &asse, "port", vec![s("vent-tip")]), &asse.attr("bfp")?.attr("VENT_D")?)),
        ]),
    )?;
    stations.set(
        s("vk-solenoid"),
        py::dict([("inlet", entry(beduan.attr("inlet")?, &tube_d)), ("outlet", entry(beduan.attr("outlet")?, &tube_d))]),
    )?;
    let flowreg_d = flowreg.attr("TUBE_D")?;
    stations.set(
        s("flow-regulator"),
        py::dict([("inlet", entry(flowreg.attr("inlet")?, &flowreg_d)), ("outlet", entry(flowreg.attr("outlet")?, &flowreg_d))]),
    )?;
    let sides = |module: &Val, names: [&'static str; 2], diam: &Val| {
        py::dict([
            (names[0], entry(call_station(rt, module, "port", vec![Val::Float(-1.0)]), diam)),
            (names[1], entry(call_station(rt, module, "port", vec![Val::Float(1.0)]), diam)),
        ])
    };
    let board = ["inboard", "outboard"];
    stations.set(s("bulkhead-drain"), sides(&drain_bulkhead, board, &drain_bulkhead.attr("TUBE_OD")?))?;
    stations.set(s("bulkhead-water"), sides(&jg, board, &jg.attr("PORT_D")?))?;
    stations.set(s("co2-inlet"), sides(&neofit, board, &neofit.attr("TUBE_OD")?))?;
    stations.set(
        s("gasher-co2"),
        py::dict([
            ("inlet", entry(gas_chain.attr("check_inlet")?, &tube_d)),
            ("outlet", entry(gas_chain.attr("check_outlet")?, &tube_d)),
        ]),
    )?;
    stations.set(
        s("wr1110"),
        py::dict([
            ("inlet", entry(gas_chain.attr("regulator_inlet")?, &tube_d)),
            ("outlet", entry(gas_chain.attr("regulator_outlet")?, &tube_d)),
        ]),
    )?;
    stations.set(
        s("water-split"),
        py::dict([
            ("supply", entry(split.attr("supply")?, &tube_d)),
            ("to-vk", entry(split.attr("to_vk")?, &tube_d)),
            ("to-flavor", entry(split.attr("to_flavor")?, &tube_d)),
        ]),
    )?;
    stations.set(
        s("digiten-flow"),
        py::dict([("inlet", entry(digiten.attr("inlet")?, &tube_d)), ("outlet", entry(digiten.attr("outlet")?, &tube_d))]),
    )?;
    let drain = {
        let funnel = funnel.clone();
        lambda(rt, vec![], move |_, _| Ok(Val::Tuple(vec![funnel.attr("drain_local")?, py::ftuple(&[0.0, 0.0, -1.0])])))
    };
    stations.set(s("funnel"), py::dict([("drain", entry(drain, &funnel.attr("spout_id")?))]))?;
    stations.set(
        s("funnel-drain-union"),
        py::dict([
            ("stub", entry(drain_elbow.attr("stem_tip")?, &drain_elbow.attr("STEM_OD")?)),
            ("outlet", entry(drain_elbow.attr("socket")?, &drain_elbow.attr("TUBE_OD")?)),
        ]),
    )?;
    ns.set("STATIONS", stations.clone())?;
    let tube = ["tube-in", "tube-out"];
    for body in ["bulkhead-flavor-a", "bulkhead-flavor-b"] {
        ns.set("_b", s(body))?;
        stations.set(s(body), sides(&drain_bulkhead, tube, &Val::Float(4.0)))?;
    }
    stations.set(s("bulkhead-carb"), sides(&jg, tube, &jg.attr("PORT_D")?))?;
    ns.set("VALVES", py::tuple(VALVES.map(s)))?;
    define(ns, rt, "valve_ends", req(&["v"]), |rt, a| Ok(py::tuple(valve_ends(rt, &a[0])?.map(s))))?;
    for valve in VALVES {
        ns.set("_v", s(valve))?;
        let [inlet, outlet] = ends(&ml, &s(valve))?;
        ns.set("_in", s(inlet))?;
        ns.set("_out", s(outlet))?;
        let mouth = |end: &'static str| {
            let ml = ml.clone();
            let params = vec![("v", Some(s(valve)), false), ("e", Some(s(end)), false)];
            lambda(rt, params, move |_, a| {
                let point = py::call(&ml.attr("port")?, vec![a[0].clone(), a[1].clone()])?;
                let axis = py::call(&ml.attr("port_axis")?, vec![a[0].clone(), a[1].clone()])?;
                Ok(Val::Tuple(vec![point, axis]))
            })
        };
        let ports = py::dict([("inlet", entry(mouth(inlet), &tube_d)), ("outlet", entry(mouth(outlet), &tube_d))]);
        stations.set(s(format!("valve-{}", valve.to_lowercase())), ports)?;
    }
    define(ns, rt, "flavor_outlet", req(&["v"]), |rt, a| flavor_outlet(rt, &a[0]))?;
    let reducer_d = flavor_reducer.attr("TUBE_OD")?;
    for valve in ["V-G", "V-J"] {
        ns.set("_v", s(valve))?;
        let outlet = lambda(rt, vec![("v", Some(s(valve)), false)], |rt, a| flavor_outlet(rt, &a[0]));
        stations.get(s(format!("valve-{}", valve.to_lowercase())))?.set(s("outlet"), entry(outlet, &reducer_d))?;
    }

    let placed_carries = || vec![("placed", None, false), ("carries", None, false)];
    let mut params = placed_carries();
    params.push(("bounds", Some(Val::None), true));
    define(ns, rt, "frames", params, |rt, a| frames(rt, &a[0], &a[1], &a[2]))?;
    define(ns, rt, "_frame", req(&["name", "placed", "ports", "bounds"]), |rt, a| {
        frame(rt, &*state(rt)?, &a[0], &a[1], &a[2], &a[3])
    })?;
    define(ns, rt, "build_runs", placed_carries(), |rt, a| build_runs(rt, &a[0], &a[1]))?;
    define(ns, rt, "build_seated_runs", placed_carries(), |rt, a| build_seated_runs(rt, &a[0], &a[1]))?;
    type Run = fn(&Rt, &Val) -> Result<Val>;
    let run = |name: &str, f: Run| define(ns, rt, name, req(&["F"]), move |rt, a| f(rt, &a[0]));
    run("_co2_0", co2_0)?;
    run("_co2_1", co2_1)?;
    let core_front_y = Num::of(&cc.attr("rear_plane_y")?)?
        .sub(Num::of(&cc.attr("rear_seam_clear")?)?)
        .sub(Num::of(&cc.attr("outer_shell_x_length")?)?);
    ns.set("_CORE_FRONT_Y", core_front_y.val())?;
    let cross_y = core_front_y.sub(f(1.5));
    ns.set("CROSS_Y", cross_y.val())?;
    let cross_dodge_y = core_front_y.add(f(2.0));
    ns.set("CROSS_DODGE_Y", cross_dodge_y.val())?;
    ns.set("CROSS_DODGE_SPAN", py::ftuple(&CROSS_DODGE_SPAN))?;
    floats(ns, &[("CROSS_DODGE_RAMP", CROSS_DODGE_RAMP), ("CROSS_DROP", CROSS_DROP), ("CHANNEL_X", CHANNEL_X), ("CROSS_RISE", CROSS_RISE)])?;
    let channel_entry_y = core_front_y.add(f(44.0));
    ns.set("CHANNEL_ENTRY_Y", channel_entry_y.val())?;
    floats(ns, &[("CROSS_LIFT_X", CROSS_LIFT_X), ("CROSS_APPROACH_Y", CROSS_APPROACH_Y)])?;
    run("_water_3", water_3)?;
    floats(ns, &[("FLUID_1_INBOARD", FLUID_1_INBOARD), ("FLUID_1_APPROACH", FLUID_1_APPROACH), ("FLUID_1_DIAGONAL", FLUID_1_DIAGONAL)])?;
    run("_fluid_1", fluid_1)?;
    floats(ns, &[("WATER_2_LEAD", WATER_2_LEAD), ("WATER_2_RUN", WATER_2_RUN)])?;
    run("_water_2", water_2)?;
    run("_water_7", water_7)?;
    run("_water_6", water_6)?;
    run("_water_5", water_5)?;
    run("_co2_2", co2_2)?;
    ns.set("FLUID_2_LEAD", tube_bend_val.clone())?;
    floats(
        ns,
        &[
            ("FLUID_2_RETURN_X", FLUID_2_RETURN_X),
            ("FLUID_2_RETURN_FORE_Y", FLUID_2_RETURN_FORE_Y),
            ("FLUID_2_OVER_CAP", FLUID_2_OVER_CAP),
            ("FLUID_2_DESCENT_EAST", FLUID_2_DESCENT_EAST),
        ],
    )?;
    run("_fluid_2", fluid_2)?;
    floats(ns, &[("FLUID_4_CROSS_Y", FLUID_4_CROSS_Y)])?;
    run("_fluid_4", fluid_4)?;
    floats(ns, &[("CARB_1_FORWARD_LEAN", CARB_1_FORWARD_LEAN)])?;
    run("_carb_1", carb_1)?;
    run("_carb_2", carb_2)?;
    floats(
        ns,
        &[
            ("GATE_STUB_CLEAR", GATE_STUB_CLEAR),
            ("GATE_B_JOG_LEG", GATE_B_JOG_LEG),
            ("GATE_B_DRAIN_RETURN_RISE", GATE_B_DRAIN_RETURN_RISE),
            ("GATE_B_RETURN_WEST", GATE_B_RETURN_WEST),
            ("GATE_B_RETURN_HOLD_Y", GATE_B_RETURN_HOLD_Y),
            ("GATE_B_UNION_APPROACH", GATE_B_UNION_APPROACH),
            ("GATE_B_STEP_Y", GATE_B_STEP_Y),
            ("GATE_B_RISE_RUN", GATE_B_RISE_RUN),
            ("GATE_A_FRONT_Y", GATE_A_FRONT_Y),
            ("GATE_A_FRONT_Z", GATE_A_FRONT_Z),
            ("GATE_A_FRONT_JOIN_X", GATE_A_FRONT_JOIN_X),
            ("GATE_A_OUTER_X", GATE_A_OUTER_X),
            ("GATE_A_DESCENT_START_Y", GATE_A_DESCENT_START_Y),
            ("GATE_A_BEARING_JOIN_Y", GATE_A_BEARING_JOIN_Y),
            ("GATE_A_BEARING_EXIT_Y", GATE_A_BEARING_EXIT_Y),
            ("GATE_A_LOW_LANE_JOIN_Y", GATE_A_LOW_LANE_JOIN_Y),
            ("GATE_A_FORE_HEIGHT", GATE_A_FORE_HEIGHT),
            ("GATE_A_WEST_X", GATE_A_WEST_X),
            ("GATE_A_RETURN_START_Y", GATE_A_RETURN_START_Y),
            ("GATE_A_UNION_JOIN_Y", GATE_A_UNION_JOIN_Y),
            ("GATE_A_UNION_LEVEL_RUN", GATE_A_UNION_LEVEL_RUN),
            ("GATE_A_RISE_RUN", GATE_A_RISE_RUN),
        ],
    )?;
    run("_gate_a_anchor", |rt, f| Ok(Num::vals(&gate_a_anchor(&*state(rt)?, f)?)))?;
    define(ns, rt, "gate_cruise", req(&["v_i_outlet_z"]), |rt, a| Ok(gate_cruise(rt, Num::of(&a[0])?)?.val()))?;
    define(ns, rt, "station", req(&["body", "port"]), |rt, a| station(rt, &a[0], &a[1]))?;
    floats(ns, &[("GATE_B_CLIMB", GATE_B_CLIMB)])?;
    run("_gate_climb_under_cruise", |rt, f| Ok(gate_climb_under_cruise(rt, &*state(rt)?, f)?.val()))?;
    type SolidRun = fn(&Rt, &Val, &Val) -> Result<Val>;
    let solid_run = |name: &str, g: SolidRun| define(ns, rt, name, req(&["F", "solids"]), move |rt, a| g(rt, &a[0], &a[1]));
    solid_run("_fluid_28", fluid_28)?;
    solid_run("_fluid_18", fluid_18)?;
    ns.set("RESERVOIR_CRUISE", tube_bend_val.clone())?;
    let reservoir_b_cruise = tube_bend.sub(f(RESERVOIR_B_CRUISE_SHORT));
    ns.set("RESERVOIR_B_CRUISE", reservoir_b_cruise.val())?;
    floats(
        ns,
        &[
            ("RESERVOIR_B_GATE_LEAN_DEG", RESERVOIR_B_GATE_LEAN_DEG),
            ("FILL_B_LEAN_Y", FILL_B_LEAN_Y),
            ("FILL_B_JOIN_Y", FILL_B_JOIN_Y),
            ("LANE_CLEAR", LANE_CLEAR),
            ("FILL_A_LANE_Z", FILL_A_LANE_Z),
            ("FILL_A_GATE_LEAD", FILL_A_GATE_LEAD),
            ("FILL_A_GATE_LEAN_DEG", FILL_A_GATE_LEAN_DEG),
        ],
    )?;
    ns.set("FILL_A_LANE_RUN", tube_bend_val.clone())?;
    floats(
        ns,
        &[
            ("FILL_A_FALL_RUN", FILL_A_FALL_RUN),
            ("FILL_A_HOSE_DROP", FILL_A_HOSE_DROP),
            ("FILL_A_HOSE_FALL_RUN", FILL_A_HOSE_FALL_RUN),
            ("FILL_A_VALVE_DROP", FILL_A_VALVE_DROP),
            ("FILL_A_VALVE_RETURN_RUN", FILL_A_VALVE_RETURN_RUN),
        ],
    )?;
    let fill_a_bearing_straight = Num::of(&anchor_cap.attr("RIB_LEN")?)?.add(f(FILL_A_BEARING_PAST_RIB));
    ns.set("FILL_A_BEARING_STRAIGHT", fill_a_bearing_straight.val())?;
    floats(ns, &[("DRAW_A_CRUISE", DRAW_A_CRUISE)])?;
    ns.set("DRAW_A_NECK_IN", py::ftuple(&DRAW_A_NECK_IN))?;
    ns.set("DRAW_A_NECK_OUT", py::ftuple(&DRAW_A_NECK_OUT))?;
    ns.set("DRAW_A_APPROACH", py::ftuple(&DRAW_A_APPROACH))?;
    floats(ns, &[("DRAW_A_GATE_LEAD", DRAW_A_GATE_LEAD), ("DRAW_B_CRUISE", DRAW_B_CRUISE)])?;
    ns.set("DRAW_B_APPROACH", py::ftuple(&DRAW_B_APPROACH))?;
    floats(ns, &[("DRAW_B_GATE_LEAD", DRAW_B_GATE_LEAD), ("DRAW_GATE_LEAN_DEG", DRAW_GATE_LEAN_DEG)])?;
    define(ns, rt, "_fill_a_lane_y", req(&["solids"]), |rt, a| Ok(fill_a_lane_y(&*state(rt)?, &a[0])?.val()))?;
    run("_fill_a_cap_z", |rt, f| Ok(fill_a_cap_z(&*state(rt)?, f)?.val()))?;
    run("_fill_a_turn_y", |rt, f| Ok(fill_a_turn_y(&*state(rt)?, f)?.val()))?;
    solid_run("_fluid_14", fluid_14)?;
    let cap_params = vec![("F", None, false), ("cap_xy", None, false), ("over_face", Some(Val::Float(0.0)), false)];
    define(ns, rt, "_on_cap", cap_params, |rt, a| Ok(Num::vals(&on_cap(&*state(rt)?, &a[0], &a[1], &a[2])?)))?;
    define(ns, rt, "_gate_lead", req(&["gate", "toward", "lead"]), |_, a| {
        Ok(Num::vals(&gate_lead(&a[0], &a[1], &a[2])?))
    })?;
    run("_fluid_16", fluid_16)?;
    run("_fluid_24", fluid_24)?;
    run("_fluid_26", fluid_26)?;
    run("_refrig_3", refrig_3)?;
    run("_refrig_1", refrig_1)?;
    run("_refrig_2", refrig_2)?;
    define(ns, rt, "authored", vec![], |_, _| Ok(Val::frozen_set(AUTHORED.iter().map(|&name| s(name)).collect())))?;
    ns.set("_AUTHORED", py::tuple(AUTHORED.map(s)))?;
    define(ns, rt, "tubes", req(&["runs"]), |rt, a| tubes(rt, &a[0]))?;
    define(ns, rt, "report", req(&["runs"]), |rt, a| report(rt, &a[0]))?;

    rt.keep(MODULE, State {
        r,
        cc,
        pump,
        ml,
        card,
        flavor_reducer,
        blocked,
        stations,
        tube_bend,
        elbow_cuff_d,
        cu_bend,
        split_tube_d,
        cap_bore_skew,
        cross_y,
        cross_dodge_y,
        channel_entry_y,
        reservoir_b_cruise,
        fill_a_bearing_straight,
        collet_skew: OnceCell::new(),
        butt_max: OnceCell::new(),
        proud_length: OnceCell::new(),
    });
    Ok(())
}
