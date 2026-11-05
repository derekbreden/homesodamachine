//! The seats on back-top that the ASSE chain, the Pisco and the flow meter slide into, and the
//! snap caps that hold each in its seat.
//!
//! Stations, pockets and cap sections are computed here; CadQuery and numpy stay provider
//! objects. `box`, `prism_x` and `section_solid` are read from the namespace at each use (the
//! back-top recipe swaps them while it calls these functions), and so are the native profiles
//! installed after the top level (`clearance_profile`, `asse_cap_room`, `asse_adapter_capture`,
//! `pisco_cap_fit`).
use super::num::{self, Num};
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::{Context, Result, ensure};
use hsm_documents::interop::{self, Val};
use py::s;
use std::cell::RefCell;
use std::cmp::Ordering;
use std::f64::consts::PI;
use std::rc::Rc;

/// Not yet compiled as it stands: the hybrid development build runs the generated namespace.
pub const TYPED: bool = false;

const MODULE: &str = "rear_snaps";

pub const SLIDE: f64 = 16.0;
pub const THREAD: f64 = 1.5;
pub const WALL: f64 = 3.0;
pub const SPLIT: f64 = 335.0;
pub const INTO: f64 = 0.5;
pub const WING: f64 = 2.0;
pub const REACH: f64 = 2.6;
pub const SIDE: f64 = 0.5;
pub const FREE_LENGTH: f64 = 22.25;
pub const ROOT_RADIUS: f64 = 1.5;
pub const REAR_ROOT_DROP: f64 = 10.0;
pub const ASSE_HEX_SEATING_DEPTH: f64 = 0.25;
pub const ASSE_BODY_SEATING_DEPTH: f64 = 0.25;
pub const PISCO_RADIAL_RELIEF: f64 = 0.25;
pub const PISCO_CAP_AIR: f64 = 0.4;
pub const PISCO_CAP_FIT: f64 = 0.15;
pub const PISCO_BEARING_LENGTH: f64 = 3.0;
pub const METER_AIR: f64 = 0.75;
pub const METER_BACK: f64 = 9.0;
pub const METER_CAP_AIR: f64 = 0.25;
pub const METER_HOUSING_FIT: f64 = 0.15;
pub const METER_BEARING_DEPTH: f64 = 4.0;
pub const LEDGE: f64 = 3.0;
pub const NOSE_LAND: f64 = 1.6;
pub const TIP_RISE: f64 = 3.0;
pub const TOOL_SLOT_WIDTH: f64 = 3.5;
pub const TOOL_SLOT_HEIGHT: f64 = 3.0;
pub const TOOL_APPROACH_DEGREES: f64 = 50.0;
pub const HOOK: f64 = NOSE_LAND + TIP_RISE;
pub const VAR: f64 = 0.5;

/// The module's float constants in definition order.
const CONSTANTS: [(&str, f64); 28] = [
    ("SLIDE", SLIDE),
    ("THREAD", THREAD),
    ("WALL", WALL),
    ("SPLIT", SPLIT),
    ("INTO", INTO),
    ("WING", WING),
    ("REACH", REACH),
    ("SIDE", SIDE),
    ("FREE_LENGTH", FREE_LENGTH),
    ("ROOT_RADIUS", ROOT_RADIUS),
    ("REAR_ROOT_DROP", REAR_ROOT_DROP),
    ("ASSE_HEX_SEATING_DEPTH", ASSE_HEX_SEATING_DEPTH),
    ("ASSE_BODY_SEATING_DEPTH", ASSE_BODY_SEATING_DEPTH),
    ("PISCO_RADIAL_RELIEF", PISCO_RADIAL_RELIEF),
    ("PISCO_CAP_AIR", PISCO_CAP_AIR),
    ("PISCO_CAP_FIT", PISCO_CAP_FIT),
    ("PISCO_BEARING_LENGTH", PISCO_BEARING_LENGTH),
    ("METER_AIR", METER_AIR),
    ("METER_BACK", METER_BACK),
    ("METER_CAP_AIR", METER_CAP_AIR),
    ("METER_HOUSING_FIT", METER_HOUSING_FIT),
    ("METER_BEARING_DEPTH", METER_BEARING_DEPTH),
    ("LEDGE", LEDGE),
    ("NOSE_LAND", NOSE_LAND),
    ("TIP_RISE", TIP_RISE),
    ("TOOL_SLOT_WIDTH", TOOL_SLOT_WIDTH),
    ("TOOL_SLOT_HEIGHT", TOOL_SLOT_HEIGHT),
    ("TOOL_APPROACH_DEGREES", TOOL_APPROACH_DEGREES),
];
pub const CHAIN: [&str; 5] = ["jg-pp010822e", "gagira-coupling", "multiplex-asse1022", "jg-pi4512f6s", "jg-pp061208w"];
pub const SOLIDS: [&str; 6] = ["asse-seat", "asse-snap-cap", "pisco-seat", "pisco-snap-cap", "meter-seat", "meter-snap-cap"];

pub struct State {
    /// The namespace: the replaceable names and the native profiles are read from it per use.
    ns: Ns,
    np: Val,
    cq: Val,
    json: Val,
    /// `pathlib.Path`.
    path: Val,
    /// `fits.running`, `fits.slip`.
    running: Num,
    slip: Num,
    /// `CATCH`: `fits.clearance(supported=True)`.
    catch: Num,
    /// `METER_COLLAR_AXIAL_AIR`.
    collar_air: Num,
    /// CadQuery and numpy attributes (`cq.Solid.makeBox`, `np.linalg.norm`), read once.
    attrs: RefCell<Vec<(&'static str, Val)>>,
}
impl State {
    /// A CadQuery or numpy attribute path, read on first use.
    fn lib(&self, path: &'static str) -> Result<Val> {
        if let Some((_, value)) = self.attrs.borrow().iter().find(|(name, _)| *name == path) {
            return Ok(value.clone());
        }
        let mut names = path.split('.');
        let mut value = match names.next() {
            Some("cq") => self.cq.clone(),
            _ => self.np.clone(),
        };
        for name in names {
            value = value.attr(name)?;
        }
        self.attrs.borrow_mut().push((path, value.clone()));
        Ok(value)
    }
    /// `cq.Vector(x, y, z)`.
    fn vector(&self, x: Val, y: Val, z: Val) -> Result<Val> {
        py::call(&self.lib("cq.Vector")?, vec![x, y, z])
    }
    /// A replaceable or native name, as the namespace holds it now.
    fn named(&self, name: &str) -> Result<Val> {
        self.ns.get(name)
    }
}
fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

// ---- the runtime's arithmetic on numbers held typed ----

const fn f(x: f64) -> Num {
    Num::F(x)
}
/// The runtime's ordering of two numbers; an unordered pair is an error, as in comparisons and
/// `min`/`max`.
fn order(a: f64, b: f64) -> Result<Ordering> {
    a.partial_cmp(&b).context("unordered numeric comparison")
}
fn lt(a: f64, b: f64) -> Result<bool> {
    Ok(order(a, b)?.is_lt())
}
fn le(a: f64, b: f64) -> Result<bool> {
    Ok(!order(a, b)?.is_gt())
}
fn gt(a: f64, b: f64) -> Result<bool> {
    Ok(order(a, b)?.is_gt())
}
fn ge(a: f64, b: f64) -> Result<bool> {
    Ok(!order(a, b)?.is_lt())
}
/// `max(a, b)`: the first wins a tie.
fn max2(a: Num, b: Num) -> Result<Num> {
    Ok(if order(b.f(), a.f())?.is_gt() { b } else { a })
}
/// `min(a, b)`: the first wins a tie.
fn min2(a: Num, b: Num) -> Result<Num> {
    Ok(if order(b.f(), a.f())?.is_lt() { b } else { a })
}
fn fmax(a: f64, b: f64) -> Result<f64> {
    Ok(if order(b, a)?.is_gt() { b } else { a })
}
fn fmin(a: f64, b: f64) -> Result<f64> {
    Ok(if order(b, a)?.is_lt() { b } else { a })
}
/// `a / b`.
fn div(a: Num, b: Num) -> Result<Num> {
    ensure!(b.f() != 0., "division by zero");
    Ok(Num::F(a.f() / b.f()))
}
/// `x ** 2`: libm `pow`, as the runtime calls it. A constant exponent would let the optimizer
/// turn it into `x * x`, which differs from libm's `pow(x, 2.0)` in the last bit for about one
/// value in a thousand.
fn pow2(x: Num) -> Num {
    let v = x.f().powf(std::hint::black_box(2.));
    match x {
        Num::I(_) if v.is_finite() && v.fract() == 0. => Num::I(v as i64),
        _ => Num::F(v),
    }
}
/// `math.sqrt(x)`.
fn sqrt(x: Num) -> Result<f64> {
    let x = x.f();
    ensure!(x >= 0., "math domain error");
    Ok(x.sqrt())
}
/// `sorted((a, b))` of two numbers: stable, unordered pairs left as they are.
fn sorted2(a: Num, b: Num) -> (Num, Num) {
    if num::order(b.f(), a.f()) == Ordering::Less { (b, a) } else { (a, b) }
}
/// `max(values)` (`Greater`) or `min(values)` (`Less`): the first of equal values.
fn pick(values: Vec<Val>, want: Ordering) -> Result<Val> {
    let mut best: Option<(Val, f64)> = None;
    for value in values {
        let key = value.num()?;
        let wins = match &best {
            None => true,
            Some((_, b)) => order(key, *b)? == want,
        };
        if wins {
            best = Some((value, key));
        }
    }
    best.map(|(value, _)| value).context("empty min/max")
}
/// The index `min(range(len(xs)), key=xs.__getitem__)` (`Less`) or `max(..)` (`Greater`) picks.
fn pick_index(xs: &[f64], want: Ordering) -> Result<usize> {
    let mut best: Option<(usize, f64)> = None;
    for (i, &x) in xs.iter().enumerate() {
        let wins = match best {
            None => true,
            Some((_, b)) => order(x, b)? == want,
        };
        if wins {
            best = Some((i, x));
        }
    }
    best.map(|(i, _)| i).context("empty min/max")
}
/// `float(x)`.
fn float(v: &Val) -> f64 {
    v.num().unwrap_or(0.)
}

// ---- values handed to providers ----

fn t2(a: Val, b: Val) -> Val {
    Val::Tuple(vec![a, b])
}
fn ints(a: i64, b: i64, c: i64) -> Val {
    Val::Tuple(vec![Val::Int(a), Val::Int(b), Val::Int(c)])
}
/// `{'line': (a, b)}`.
fn line(a: &Val, b: &Val) -> Val {
    py::dict([("line", t2(a.clone(), b.clone()))])
}
/// `[{'line': (p, q)} for p, q in zip(points, points[1:])]`.
fn run(points: &[Val]) -> Vec<Val> {
    points.windows(2).map(|pair| line(&pair[0], &pair[1])).collect()
}
/// `[{'line': (a, b)} for a, b in zip(points, points[1:] + points[:1])]`.
fn closed(points: &[Val]) -> Vec<Val> {
    (0..points.len()).map(|i| line(&points[i], &points[(i + 1) % points.len()])).collect()
}
/// `{'arc': (a, mid, b, centre), 'ccw': True}`, or without `ccw`.
fn arc(a: Val, mid: Val, b: Val, centre: Val, ccw: bool) -> Val {
    let row = Val::Tuple(vec![a, mid, b, centre]);
    if ccw { py::dict([("arc", row), ("ccw", Val::Bool(true))]) } else { py::dict([("arc", row)]) }
}
/// `[:, k]`.
fn column(k: i64) -> Val {
    Val::Tuple(vec![Val::Slice { start: None, stop: None, step: 1 }, Val::Int(k)])
}
/// `bool(a <op> b)` of a provider comparison.
fn truth(op: &str, a: Val, b: Val) -> Result<bool> {
    interop::compare(op, a, b)?.truthy()
}
fn starts_with(name: &Val, prefix: &str) -> Result<bool> {
    match name {
        Val::Str(text) => Ok(text.starts_with(prefix)),
        other => py::method(other, "startswith", vec![s(prefix)])?.truthy(),
    }
}
/// `points.tolist()` of a numpy array, or the numbers of a sequence.
fn floats_of(value: &Val) -> Result<Vec<f64>> {
    let local = match value {
        Val::Ref(_) => {
            let copied = py::snapshot(value)?;
            if matches!(copied, Val::Ref(_)) { py::method(value, "tolist", vec![])? } else { copied }
        }
        other => other.clone(),
    };
    local.iter()?.iter().map(Val::num).collect()
}

/// A record a caller passes (a station), copied in one snapshot.
struct Rec(Val);
impl Rec {
    fn of(value: &Val) -> Result<Self> {
        Ok(Self(py::snapshot(value)?))
    }
    fn val(&self, key: &str) -> Result<Val> {
        self.0.get(s(key))
    }
    fn num(&self, key: &str) -> Result<Num> {
        Num::of(&self.val(key)?)
    }
    /// `record.get(key, default)`.
    fn get(&self, key: &str, default: Val) -> Result<Val> {
        py::dget(&self.0, key, default)
    }
}

// ---- the module's functions ----

/// `surface_points(shape, step=0.2)`: the tessellation's vertices and an area-weighted sample.
pub fn surface_points(rt: &Rt, shape: &Val, step: &Val) -> Result<Val> {
    let st = state(rt)?;
    let mesh = py::unpack(&py::method(shape, "tessellate", vec![Val::Float(0.02), Val::Float(0.1)])?, 2)?;
    let array = st.lib("np.array")?;
    let mut rows = vec![];
    for q in mesh[0].iter()? {
        rows.push(Val::Tuple(vec![q.attr("x")?, q.attr("y")?, q.attr("z")?]));
    }
    let vs = py::call(&array, vec![Val::list(rows)])?;
    let tri = vs.get(py::call(&array, vec![mesh[1].clone()])?)?;
    let (a, b, c) = (tri.get(column(0))?, tri.get(column(1))?, tri.get(column(2))?);
    let cross = py::call(&st.lib("np.cross")?, vec![
        interop::binary("sub", b.clone(), a.clone())?,
        interop::binary("sub", c.clone(), a.clone())?,
    ])?;
    let norm = py::call_kw(&st.lib("np.linalg.norm")?, vec![cross], vec![("axis", Val::Int(1))])?;
    let area = interop::binary("mul", Val::Float(0.5), norm)?;
    let count = interop::binary("truediv", area, pow2(Num::of(step)?).val())?;
    let n = py::method(&py::call(&st.lib("np.ceil")?, vec![count])?, "astype", vec![Val::Type("int".into())])?;
    let arange = py::call(&st.lib("np.arange")?, vec![Val::Int(tri.len()? as i64)])?;
    let i = py::call(&st.lib("np.repeat")?, vec![arange, n])?;
    let rng = py::call(&st.lib("np.random.default_rng")?, vec![Val::Int(1)])?;
    let wide = Val::Tuple(vec![Val::Slice { start: None, stop: None, step: 1 }, Val::None]);
    let draw = py::method(&rng, "random", vec![Val::Int(i.len()? as i64)])?;
    let r1 = py::call(&st.lib("np.sqrt")?, vec![draw])?.get(wide.clone())?;
    let r2 = py::method(&rng, "random", vec![Val::Int(i.len()? as i64)])?.get(wide)?;
    let first = interop::binary("mul", interop::binary("sub", Val::Int(1), r1.clone())?, a.get(i.clone())?)?;
    let second = interop::binary(
        "mul",
        interop::binary("mul", r1.clone(), interop::binary("sub", Val::Int(1), r2.clone())?)?,
        b.get(i.clone())?,
    )?;
    let partial = interop::binary("add", first, second)?;
    let third = interop::binary("mul", interop::binary("mul", r1, r2)?, c.get(i)?)?;
    let sample = interop::binary("add", partial, third)?;
    py::call(&st.lib("np.concatenate")?, vec![Val::list(vec![sample, vs])])
}

/// `envelope(points, axis, lo, hi, step=0.1)`: the radius about `axis` in each axial bin.
pub fn envelope(rt: &Rt, points: &Val, axis: &Val, lo: &Val, hi: &Val, step: &Val) -> Result<Val> {
    let st = state(rt)?;
    let ys = py::call(&st.lib("np.arange")?, vec![lo.clone(), hi.clone(), step.clone()])?;
    let r = py::call(&st.lib("np.zeros")?, vec![Val::Int(ys.len()? as i64)])?;
    let scaled = interop::binary("truediv", interop::binary("sub", points.get(column(1))?, lo.clone())?, step.clone())?;
    let k = py::method(&py::call(&st.lib("np.floor")?, vec![scaled])?, "astype", vec![Val::Type("int".into())])?;
    let above = truth("ge", k.clone(), Val::Int(0))?;
    let below = truth("lt", k.clone(), Val::Int(ys.len()? as i64))?;
    let ok = Val::Int(i64::from(above) & i64::from(below));
    let bins = k.get(ok.clone())?;
    let radial = py::call(&st.lib("np.hypot")?, vec![
        interop::binary("sub", points.get(Val::Tuple(vec![ok.clone(), Val::Int(0)]))?, axis.get(Val::Int(0))?)?,
        interop::binary("sub", points.get(Val::Tuple(vec![ok, Val::Int(2)]))?, axis.get(Val::Int(1))?)?,
    ])?;
    py::call(&st.lib("np.maximum.at")?, vec![r.clone(), bins, radial])?;
    Ok(t2(ys, r))
}

/// `swept(r, behind, ahead, step=0.1)`: each bin's largest radius over the slide window.
pub fn swept(rt: &Rt, r: &Val, behind: &Val, ahead: &Val, step: &Val) -> Result<Val> {
    let st = state(rt)?;
    let step = Num::of(step)?;
    let a = num::round_int(div(Num::of(behind)?, step)?.f());
    let b = num::round_int(div(Num::of(ahead)?, step)?.f());
    let n = r.len()? as i64;
    let mut rows = Vec::with_capacity(n.max(0) as usize);
    for i in 0..n {
        let start = if i - a > 0 { i - a } else { 0 };
        let stop = if i + b + 1 < n { i + b + 1 } else { n };
        let window = r.get(Val::Slice { start: Some(start), stop: Some(stop), step: 1 })?;
        rows.push(py::method(&window, "max", vec![])?);
    }
    py::call(&st.lib("np.array")?, vec![Val::list(rows)])
}

/// `steps(ys, r, tol=0.2, step=0.1, shortest=1.5)`: the radius profile as `(y0, y1, r)` runs.
pub fn steps(ys: &Val, r: &Val, tol: f64, step: f64, shortest: f64) -> Result<Val> {
    let r = floats_of(r)?;
    let ys = floats_of(ys)?;
    let at = |i: usize| ys.get(i).copied().context("index out of range");
    let mut out: Vec<[f64; 3]> = vec![];
    let mut i = 0;
    while i < r.len() {
        if le(r[i], 0.)? {
            i += 1;
            continue;
        }
        let (mut j, mut lo, mut hi) = (i, r[i], r[i]);
        while j + 1 < r.len() && gt(r[j + 1], 0.)? && le(fmax(hi, r[j + 1])? - fmin(lo, r[j + 1])?, tol)? {
            j += 1;
            (lo, hi) = (fmin(lo, r[j])?, fmax(hi, r[j])?);
        }
        out.push([at(i)?, at(j)? + step, hi]);
        i = j + 1;
    }
    let mut merged = vec![*out.first().context("index out of range")?];
    for &[y0, y1, rr] in &out[1..] {
        let last = merged.last_mut().expect("merged starts with a run");
        if lt((last[1] - y0).abs(), 1e-6)? && lt((last[2] - rr).abs(), 1e-6)? {
            last[1] = y1;
        } else {
            merged.push([y0, y1, rr]);
        }
    }
    while merged.len() > 1 {
        let lengths: Vec<f64> = merged.iter().map(|m| m[1] - m[0]).collect();
        let i = pick_index(&lengths, Ordering::Less)?;
        if ge(merged[i][1] - merged[i][0], shortest)? {
            break;
        }
        let j = if i == merged.len() - 1 || (i > 0 && ge(merged[i - 1][2], merged[i + 1][2])?) { i - 1 } else { i + 1 };
        let (lo, hi) = (i.min(j), i.max(j));
        let joined = [merged[lo][0], merged[hi][1], fmax(merged[lo][2], merged[hi][2])?];
        merged.splice(lo..=hi, [joined]);
        let mut k = 0;
        while k + 1 < merged.len() {
            if lt((merged[k][2] - merged[k + 1][2]).abs(), 1e-9)? {
                let joined = [merged[k][0], merged[k + 1][1], merged[k][2]];
                merged.splice(k..k + 2, [joined]);
            } else {
                k += 1;
            }
        }
    }
    Ok(Val::list(merged.iter().map(|m| py::ftuple(m)).collect()))
}

/// `turned(profile, axis)`: the `(y0, y1, r)` runs revolved about Y at `axis` (x, z).
pub fn turned(rt: &Rt, profile: &Val, axis: &Val) -> Result<Val> {
    let st = state(rt)?;
    let profile = py::snapshot(profile)?;
    let mut pts = vec![t2(profile.get(Val::Int(0))?.get(Val::Int(0))?, Val::Float(0.))];
    for row in profile.iter()? {
        let run = py::unpack(&row, 3)?;
        pts.push(t2(run[0].clone(), run[2].clone()));
        pts.push(t2(run[1].clone(), run[2].clone()));
    }
    pts.push(t2(profile.get(Val::Int(-1))?.get(Val::Int(1))?, Val::Float(0.)));
    let mut clean = vec![pts[0].clone()];
    for p in &pts[1..] {
        let last = clean.last().expect("clean starts with a point").clone();
        let apart = |k: i64| -> Result<bool> {
            let d = Num::of(&p.get(Val::Int(k))?)?.sub(Num::of(&last.get(Val::Int(k))?)?);
            gt(d.f().abs(), 1e-9)
        };
        if apart(0)? || apart(1)? {
            clean.push(p.clone());
        }
    }
    let wp = py::call(&st.lib("cq.Workplane")?, vec![s("XY")])?;
    let wp = py::method(&py::method(&wp, "polyline", vec![Val::list(clean)])?, "close", vec![])?;
    let solid = py::method(&py::method(&wp, "revolve", vec![Val::Int(360), ints(0, 0, 0), ints(1, 0, 0)])?, "val", vec![])?;
    let solid = py::method(&solid, "rotate", vec![ints(0, 0, 0), ints(0, 0, 1), Val::Int(90)])?;
    py::method(&solid, "translate", vec![Val::Tuple(vec![axis.get(Val::Int(0))?, Val::Float(0.), axis.get(Val::Int(1))?])])
}

/// `hex_prism(axis, apothem, clock_deg, y0, y1, corner)`: a hex prism along Y, its corners
/// rounded to `corner`.
pub fn hex_prism(rt: &Rt, axis: &Val, apothem: &Val, clock_deg: &Val, y0: &Val, y1: &Val, corner: &Val) -> Result<Val> {
    let st = state(rt)?;
    let rr = div(Num::of(apothem)?, f(num::cos(PI / 6.)))?;
    let (ax, az) = (axis.get(Val::Int(0))?, axis.get(Val::Int(1))?);
    let (x, z, clock) = (Num::of(&ax)?, Num::of(&az)?, Num::of(clock_deg)?);
    let mut pts = Vec::with_capacity(6);
    for i in 0..6 {
        let angle = num::radians(clock.add(Num::I(60).mul(Num::I(i))).f());
        let px = x.add(rr.mul(f(num::sin(angle))));
        let pz = z.sub(rr.mul(f(num::cos(angle))));
        pts.push(st.vector(px.val(), y0.clone(), pz.val())?);
    }
    let length = Num::of(y1)?.sub(Num::of(y0)?);
    let wire = py::call_kw(&st.lib("cq.Wire.makePolygon")?, vec![Val::list(pts)], vec![("close", Val::Bool(true))])?;
    let along = st.vector(Val::Int(0), length.val(), Val::Int(0))?;
    let prism = py::call(&st.lib("cq.Solid.extrudeLinear")?, vec![wire, Val::list(vec![]), along])?;
    let origin = st.vector(ax, y0.clone(), az)?;
    let cylinder = py::call(&st.lib("cq.Solid.makeCylinder")?, vec![
        corner.clone(),
        length.val(),
        origin,
        st.vector(Val::Int(0), Val::Int(1), Val::Int(0))?,
    ])?;
    py::method(&prism, "intersect", vec![cylinder])
}

/// `asse_cap_profile(wrenches, air)`: the hex pipe about both wrenches' side corners.
pub fn asse_cap_profile(wrenches: &Val, air: &Val) -> Result<Val> {
    let rows = py::snapshot(wrenches)?.iter()?;
    let mut total = Num::I(0);
    for row in &rows {
        total = total.add(Num::of(&py::unpack(row, 4)?[2])?);
    }
    let clock = div(total, Num::I(rows.len() as i64))?;
    let tan = (PI / 6.).tan();
    let mut apothem: Option<f64> = None;
    for row in &rows {
        let w = py::unpack(row, 4)?;
        let turn = num::radians(Num::of(&w[2])?.sub(clock).f());
        let reach = Num::of(&w[1])?.mul(f(num::cos(turn) + tan * num::sin(turn).abs())).f();
        apothem = Some(match apothem {
            Some(best) if !order(reach, best)?.is_gt() => best,
            _ => reach,
        });
    }
    let apothem = f(apothem.context("empty min/max")?);
    let tenths = apothem.add(Num::of(air)?).mul(f(10.)).f().ceil() as i64;
    Ok(py::dict([("apothem", Val::Float(tenths as f64 / 10.)), ("clock", clock.val())]))
}

/// `meter_cap_corner_room(west, centre_z, span)`: the meter cap's trimmed west corner.
pub fn meter_cap_corner_room(west: &Val, centre_z: &Val, span: &Val) -> Result<Val> {
    let (w, cz) = (Num::of(west)?, Num::of(centre_z)?);
    let top = cz.sub(f(8.));
    let trim = f(METER_BACK).sub(f(WALL));
    let points = [
        t2(w.sub(f(1.)).val(), cz.sub(f(40.)).val()),
        t2(w.add(trim).val(), cz.sub(f(40.)).val()),
        t2(w.add(trim).val(), top.sub(trim).val()),
        t2(west.clone(), top.val()),
        t2(w.sub(f(1.)).val(), top.val()),
    ];
    let segments = Val::list(closed(&points));
    let (a, b) = (Num::of(&span.get(Val::Int(0))?)?, Num::of(&span.get(Val::Int(1))?)?);
    Ok(py::dict([("segments", segments), ("span", t2(a.sub(f(0.1)).val(), b.add(f(0.1)).val()))]))
}

/// `box(x0, x1, y0, y1, z0, z1)`.
pub fn make_box(rt: &Rt, x0: &Val, x1: &Val, y0: &Val, y1: &Val, z0: &Val, z1: &Val) -> Result<Val> {
    let st = state(rt)?;
    let make = st.lib("cq.Solid.makeBox")?;
    let dx = Num::of(x1)?.sub(Num::of(x0)?);
    let dy = Num::of(y1)?.sub(Num::of(y0)?);
    let dz = Num::of(z1)?.sub(Num::of(z0)?);
    let corner = st.vector(x0.clone(), y0.clone(), z0.clone())?;
    py::call(&make, vec![dx.val(), dy.val(), dz.val(), corner])
}
/// The namespace's `box`, which a caller may have swapped.
fn named_box(st: &State, args: Vec<Val>) -> Result<Val> {
    py::call(&st.named("box")?, args)
}

/// `stadium_x(yc, zc, r, fore, aft, x0, x1)`: a stadium in YZ extruded along X.
pub fn stadium_x(rt: &Rt, yc: &Val, zc: &Val, r: &Val, fore: &Val, aft: &Val, x0: &Val, x1: &Val) -> Result<Val> {
    let st = state(rt)?;
    let (y, z, r) = (Num::of(yc)?, Num::of(zc)?, Num::of(r)?);
    let (a, b) = (y.sub(Num::of(fore)?), y.add(Num::of(aft)?));
    let wp = py::call_kw(&st.lib("cq.Workplane")?, vec![s("YZ")], vec![("origin", Val::Tuple(vec![x0.clone(), Val::Int(0), Val::Int(0)]))])?;
    let wp = py::method(&wp, "moveTo", vec![a.val(), z.sub(r).val()])?;
    let wp = py::method(&wp, "lineTo", vec![b.val(), z.sub(r).val()])?;
    let wp = py::method(&wp, "threePointArc", vec![t2(b.add(r).val(), zc.clone()), t2(b.val(), z.add(r).val())])?;
    let wp = py::method(&wp, "lineTo", vec![a.val(), z.add(r).val()])?;
    let wp = py::method(&wp, "threePointArc", vec![t2(a.sub(r).val(), zc.clone()), t2(a.val(), z.sub(r).val())])?;
    let w = py::method(&wp, "close", vec![])?;
    let length = Num::of(x1)?.sub(Num::of(x0)?);
    py::method(&py::method(&w, "extrude", vec![length.val()])?, "val", vec![])
}

/// `half_width(radius, z, axis_z)`: the half chord of a circle about `axis_z` at height `z`.
pub fn half_width(radius: Num, z: Num, axis_z: Num) -> Result<f64> {
    sqrt(max2(pow2(radius).sub(pow2(z.sub(axis_z))), f(0.))?)
}

/// `station(...)`'s arguments as Python passes them.
pub struct StationArgs {
    pub axis_x: Val,
    pub neck: Val,
    pub y0: Val,
    pub y1: Val,
    pub split: Val,
    pub wing_root: Val,
    pub free_length: Val,
    pub tool_angle_degrees: Val,
    pub tool_end_stock: Val,
}
impl StationArgs {
    /// The required arguments, the rest at their defaults.
    pub fn new(axis_x: Val, neck: Val, y0: Val, y1: Val) -> Self {
        Self {
            axis_x,
            neck,
            y0,
            y1,
            split: Val::Float(SPLIT),
            wing_root: Val::None,
            free_length: Val::Float(FREE_LENGTH),
            tool_angle_degrees: Val::Float(TOOL_APPROACH_DEGREES),
            tool_end_stock: Val::Float(WALL),
        }
    }
}

/// `station(axis_x, neck, y0, y1, split=SPLIT, *, wing_root=None, ...)`: the snap's planes.
pub fn station(rt: &Rt, a: StationArgs) -> Result<Val> {
    let st = state(rt)?;
    let ledge = Num::of(&a.neck)?.add(f(REACH)).add(st.running);
    let inner = ledge.add(f(SIDE));
    let root = if matches!(a.wing_root, Val::None) { a.split.clone() } else { a.wing_root.clone() };
    let catch = max2(
        Num::of(&root)?.add(Num::of(&a.free_length)?),
        Num::of(&a.split)?.add(f(LEDGE)).add(st.catch),
    )?;
    let bearing = catch.sub(st.catch);
    let tip = catch.add(f(HOOK));
    let result = py::dict([
        ("axis_x", a.axis_x),
        ("y0", a.y0),
        ("y1", a.y1),
        ("split", a.split),
        ("neck", a.neck),
        ("ledge", ledge.val()),
        ("inner", inner.val()),
        ("outer", inner.add(f(WING)).val()),
        ("hook", ledge.sub(f(REACH)).val()),
        ("bearing", bearing.val()),
        ("catch", catch.val()),
        ("tip", tip.val()),
        ("ceiling", tip.add(Num::I(2).mul(st.running)).val()),
        ("root", root),
        ("nose_land", Val::Float(NOSE_LAND)),
        ("root_radius", Val::Float(ROOT_RADIUS)),
        ("tool_angle_degrees", a.tool_angle_degrees),
        ("tool_end_stock", a.tool_end_stock),
    ]);
    result.set(s("tool_ports"), Val::list(receiver_tool_ports(&result)))?;
    Ok(result)
}

/// `receiver_tool_ports(s)`: the receivers have no tool ports.
pub fn receiver_tool_ports(_station: &Val) -> Vec<Val> {
    vec![]
}

/// `prism_x(x0, x1, points)`: a YZ polygon extruded along X.
pub fn prism_x(rt: &Rt, x0: &Val, x1: &Val, points: &Val) -> Result<Val> {
    let st = state(rt)?;
    let wp = py::call_kw(&st.lib("cq.Workplane")?, vec![s("YZ")], vec![("origin", Val::Tuple(vec![x0.clone(), Val::Float(0.), Val::Float(0.)]))])?;
    let wp = py::method(&py::method(&wp, "polyline", vec![points.clone()])?, "close", vec![])?;
    let length = Num::of(x1)?.sub(Num::of(x0)?);
    py::method(&py::method(&wp, "extrude", vec![length.val()])?, "val", vec![])
}

/// `radial_profile(points)`: an `(x, r)` profile revolved about X.
pub fn radial_profile(rt: &Rt, points: &Val) -> Result<Val> {
    let st = state(rt)?;
    let points = py::snapshot(points)?;
    let mut path = vec![t2(points.get(Val::Int(0))?.get(Val::Int(0))?, Val::Float(0.))];
    for row in points.iter()? {
        path.push(Val::Tuple(row.iter()?));
    }
    path.push(t2(points.get(Val::Int(-1))?.get(Val::Int(0))?, Val::Float(0.)));
    let wp = py::call(&st.lib("cq.Workplane")?, vec![s("XY")])?;
    let wp = py::method(&py::method(&wp, "polyline", vec![Val::list(path)])?, "close", vec![])?;
    py::method(&py::method(&wp, "revolve", vec![Val::Int(360), ints(0, 0, 0), ints(1, 0, 0)])?, "val", vec![])
}

/// `stadium_profile_x(points, centre, fore, aft)`: an `(x, r)` profile swept fore and aft.
pub fn stadium_profile_x(rt: &Rt, points: &Val, centre: &Val, fore: &Val, aft: &Val) -> Result<Val> {
    let st = state(rt)?;
    let yz = py::unpack(centre, 2)?;
    let (y, z_v) = (Num::of(&yz[0])?, yz[1].clone());
    let z = Num::of(&z_v)?;
    let (a, b) = (y.sub(Num::of(fore)?), y.add(Num::of(aft)?));
    let rows = py::snapshot(points)?.iter()?;
    let axis = || st.vector(Val::Int(1), Val::Int(0), Val::Int(0));
    let mut pieces = vec![];
    for pair in rows.windows(2) {
        let (p0, p1) = (py::unpack(&pair[0], 2)?, py::unpack(&pair[1], 2)?);
        let (x0_v, r0_v, x1_v, r1_v) = (p0[0].clone(), p0[1].clone(), p1[0].clone(), p1[1].clone());
        let (x0, r0, x1, r1) = (Num::of(&x0_v)?, Num::of(&r0_v)?, Num::of(&x1_v)?, Num::of(&r1_v)?);
        let length = x1.sub(x0);
        if lt(length.f(), 1e-8)? {
            continue;
        }
        for cy in [a, b] {
            let piece = if gt(r1.sub(r0).f().abs(), 1e-8)? {
                let make = st.lib("cq.Solid.makeCone")?;
                let base = st.vector(x0_v.clone(), cy.val(), z_v.clone())?;
                py::call(&make, vec![r0_v.clone(), r1_v.clone(), length.val(), base, axis()?])?
            } else {
                let make = st.lib("cq.Solid.makeCylinder")?;
                let base = st.vector(x0_v.clone(), cy.val(), z_v.clone())?;
                py::call(&make, vec![r0_v.clone(), length.val(), base, axis()?])?
            };
            pieces.push(piece);
        }
        if gt(b.sub(a).f(), 1e-8)? {
            let outline = vec![
                st.vector(x0_v.clone(), a.val(), z.sub(r0).val())?,
                st.vector(x1_v.clone(), a.val(), z.sub(r1).val())?,
                st.vector(x1_v.clone(), a.val(), z.add(r1).val())?,
                st.vector(x0_v.clone(), a.val(), z.add(r0).val())?,
            ];
            let wire = py::call_kw(&st.lib("cq.Wire.makePolygon")?, vec![Val::list(outline)], vec![("close", Val::Bool(true))])?;
            let along = st.vector(Val::Int(0), b.sub(a).val(), Val::Int(0))?;
            pieces.push(py::call(&st.lib("cq.Solid.extrudeLinear")?, vec![wire, Val::list(vec![]), along])?);
        }
    }
    let first = pieces.first().context("index out of range")?;
    py::method(&py::method(first, "fuse", pieces[1..].to_vec())?, "clean", vec![])
}

/// `radial_room(record)`: a revolved profile, clipped to its wrench hex and relief, placed at
/// its frame.
pub fn radial_room(rt: &Rt, record: &Val) -> Result<Val> {
    let st = state(rt)?;
    let above_core = rt.import("above_core")?;
    let record = py::snapshot(record)?;
    let points = record.get(s("points"))?;
    let mut shape = radial_profile(rt, &points)?;
    if record.contains(&s("wrench"))? {
        let wrench = record.get(s("wrench"))?;
        let lo = points.get(Val::Int(0))?.get(Val::Int(0))?;
        let hi = points.get(Val::Int(-1))?.get(Val::Int(0))?;
        let across = div(Num::I(2).mul(Num::of(&wrench.get(s("apothem"))?)?), f(num::cos(PI / 6.)))?;
        let wp = py::call_kw(&st.lib("cq.Workplane")?, vec![s("YZ")], vec![("origin", Val::Tuple(vec![lo.clone(), Val::Float(0.), Val::Float(0.)]))])?;
        let wp = py::method(&wp, "polygon", vec![Val::Int(6), across.val()])?;
        let length = Num::of(&hi)?.sub(Num::of(&lo)?);
        let prism = py::method(&py::method(&wp, "extrude", vec![length.val()])?, "val", vec![])?;
        let prism = py::method(&prism, "rotate", vec![ints(0, 0, 0), ints(1, 0, 0), wrench.get(s("clock"))?])?;
        shape = py::method(&shape, "intersect", vec![prism])?;
        if wrench.contains(&s("outline"))? {
            let span = py::unpack(&wrench.get(s("relief_span"))?, 2)?;
            let (a, b) = (span[0].clone(), span[1].clone());
            let width = Num::of(&b)?.sub(Num::of(&a)?);
            let wp = py::call_kw(&st.lib("cq.Workplane")?, vec![s("YZ")], vec![("origin", Val::Tuple(vec![a.clone(), Val::Float(0.), Val::Float(0.)]))])?;
            let wp = py::method(&py::method(&wp, "polyline", vec![wrench.get(s("outline"))?])?, "close", vec![])?;
            let relief = py::method(&py::method(&wp, "extrude", vec![width.val()])?, "val", vec![])?;
            let corners = py::call(&st.lib("cq.Solid.makeCylinder")?, vec![
                wrench.get(s("relief_corner"))?,
                width.val(),
                st.vector(a, Val::Float(0.), Val::Float(0.))?,
                st.vector(Val::Float(1.), Val::Float(0.), Val::Float(0.))?,
            ])?;
            let kept = py::method(&relief, "intersect", vec![corners])?;
            shape = py::method(&py::method(&shape, "fuse", vec![kept])?, "clean", vec![])?;
        }
    }
    let location = py::call(&above_core.attr("frame_location")?, vec![record.get(s("frame"))?])?;
    py::method(&shape, "moved", vec![location])
}

/// `pisco_grip_stock(s, axis_z, body_r, neck_r, lip)`: the Pisco cap's grip blocks as box
/// extents.
pub fn pisco_grip_stock(station: &Val, axis_z: &Val, body_r: &Val, lip: &Val) -> Result<Val> {
    let s = Rec::of(station)?;
    let half = s.num("inner")?.sub(f(ROOT_RADIUS)).sub(f(0.5));
    let (z, body) = (Num::of(axis_z)?, Num::of(body_r)?);
    let bottom = z.sub(body).sub(f(WALL));
    let top = z.sub(f(sqrt(max2(pow2(body).sub(pow2(half.sub(f(WALL)))), f(0.))?)?));
    let ax = s.num("axis_x")?;
    Ok(Val::list(vec![
        Val::Tuple(vec![ax.sub(half).val(), ax.add(half).val(), s.val("y0")?, s.val("y1")?, bottom.val(), top.val()]),
        Val::Tuple(vec![ax.sub(half).val(), ax.add(half).val(), s.val("y0")?, lip.clone(), bottom.val(), axis_z.clone()]),
    ]))
}

/// `pisco_bearing_profile(runs, profile, mouth_y)`: the seat runs, split where the Pisco's
/// bearing band starts and ends, the band at the bearing radius.
pub fn pisco_bearing_profile(runs: &Val, profile: &Val, mouth_y: &Val) -> Result<Val> {
    let profile = py::snapshot(profile)?;
    let mut widest: Option<(Val, f64)> = None;
    for p in profile.iter()? {
        let key = p.get(Val::Int(1))?.num()?;
        let wins = match &widest {
            None => true,
            Some((_, best)) => order(key, *best)?.is_gt(),
        };
        if wins {
            widest = Some((p, key));
        }
    }
    let zr = py::unpack(&widest.context("empty min/max")?.0, 2)?;
    let (z, r) = (Num::of(&zr[0])?, Num::of(&zr[1])?);
    let face = Num::of(mouth_y)?.sub(z);
    let (y0, y1) = (face.sub(f(PISCO_BEARING_LENGTH / 2.)), face.add(f(PISCO_BEARING_LENGTH / 2.)));
    let bearing = r.add(f(PISCO_CAP_FIT)).val();
    let mut result = vec![];
    for row in py::snapshot(runs)?.iter()? {
        let run = py::unpack(&row, 3)?;
        let (a, b) = (Num::of(&run[0])?, Num::of(&run[1])?);
        let mut cuts: Vec<(Val, f64)> = vec![(run[0].clone(), a.f()), (run[1].clone(), b.f())];
        for v in [y0, y1] {
            if lt(a.f(), v.f())? && lt(v.f(), b.f())? {
                cuts.push((v.val(), v.f()));
            }
        }
        let mut unique: Vec<(Val, f64)> = vec![];
        for cut in cuts {
            if !unique.iter().any(|kept| kept.1 == cut.1) {
                unique.push(cut);
            }
        }
        unique.sort_by(|p, q| num::order(p.1, q.1));
        for pair in unique.windows(2) {
            let mid = (pair[0].1 + pair[1].1) / 2.;
            let band = le(y0.f(), mid)? && le(mid, y1.f())?;
            result.push(Val::Tuple(vec![pair[0].0.clone(), pair[1].0.clone(), if band { bearing.clone() } else { run[2].clone() }]));
        }
    }
    Ok(Val::list(result))
}

/// `pockets(s)`: the ledge, spring and root pockets in each of the seat's flanks.
pub fn pockets(rt: &Rt, station: &Val) -> Result<Vec<Val>> {
    let st = state(rt)?;
    let s = Rec::of(station)?;
    let a = st.running;
    let mut out = vec![];
    for side in [-1., 1.] {
        let side = f(side);
        let ax = s.num("axis_x")?;
        let far = ax.add(side.mul(s.num("outer")?.add(f(1.))));
        let ledge = ax.add(side.mul(s.num("ledge")?));
        let neck = ax.add(side.mul(s.num("neck")?));
        let (y0, y1) = (s.num("y0")?.sub(a).val(), s.num("y1")?.add(a).val());
        let (lo, hi) = sorted2(ledge, far);
        out.push(named_box(&st, vec![lo.val(), hi.val(), y0.clone(), y1.clone(), s.num("split")?.sub(f(1.)).val(), s.val("bearing")?])?);
        let (lo, hi) = sorted2(neck, far);
        out.push(named_box(&st, vec![lo.val(), hi.val(), y0.clone(), y1.clone(), s.val("bearing")?, s.val("ceiling")?])?);
        let radius = Num::of(&s.get("root_radius", Val::Float(ROOT_RADIUS))?)?;
        let near = ax.add(side.mul(s.num("inner")?.sub(radius).sub(a)));
        let root = s.num("root")?;
        let (lo, hi) = sorted2(near, far);
        out.push(named_box(&st, vec![lo.val(), hi.val(), y0, y1, root.sub(a).val(), root.add(radius).add(a).val()])?);
    }
    let mut ports = vec![];
    for port in receiver_tool_ports(station) {
        let mut args = port.get(py::s("span"))?.iter()?;
        args.push(port.get(py::s("section"))?);
        ports.push(py::call(&st.named("prism_x")?, args)?);
    }
    out.extend(ports);
    if s.get("tool_inner_slope", Val::None)?.truthy()? {
        let low = s.num("split")?.sub(f(1.));
        for port in receiver_tool_ports(station) {
            out.push(tool_flare(&st, &s, &port, low)?);
        }
    }
    Ok(out)
}
/// One tool port's inner flare: the port section swept out to the neck's sloped inner face.
fn tool_flare(st: &State, s: &Rec, port: &Val, low: Num) -> Result<Val> {
    let a = st.running;
    let side = Num::of(&port.get(py::s("side"))?)?;
    let edge = s.num("axis_x")?.add(side.mul(s.num("neck")?));
    let near = edge.sub(side.mul(s.num("tool_inner_slope")?).mul(s.num("bearing")?.sub(low)));
    let points = [t2(edge.val(), low.val()), t2(edge.val(), s.val("bearing")?), t2(near.val(), low.val())];
    let section = port.get(py::s("section"))?;
    let ys: Vec<Val> = section.iter()?.iter().map(|p| p.get(Val::Int(0))).collect::<Result<_>>()?;
    let yn: Vec<f64> = ys.iter().map(Val::num).collect::<Result<_>>()?;
    let lowest = pick(ys.clone(), Ordering::Less)?;
    let highest = pick(ys.clone(), Ordering::Greater)?;
    let fore = s.num("y0")?.sub(a);
    let start = if gt(fore.f(), lowest.num()?)? { fore.val() } else { lowest.clone() };
    let aft = s.num("y1")?.add(a);
    let end = if lt(aft.f(), highest.num()?)? { aft.val() } else { highest.clone() };
    let flare = py::call(&st.named("section_solid")?, vec![py::dict([("span", t2(start, end)), ("segments", Val::list(closed(&points)))])])?;
    let first = pick_index(&yn, Ordering::Less)?;
    let last = pick_index(&yn, Ordering::Greater)?;
    let mut rows = vec![t2(pick(ys.clone(), Ordering::Less)?, low.val())];
    let mut i = first;
    loop {
        rows.push(section.get(Val::Int(i as i64))?);
        if i == last {
            break;
        }
        i = (i + 1) % ys.len();
    }
    rows.push(t2(pick(ys, Ordering::Greater)?, low.val()));
    let (lo, hi) = sorted2(near, edge);
    let prism = py::call(&st.named("prism_x")?, vec![lo.val(), hi.val(), Val::list(rows)])?;
    py::method(&flare, "intersect", vec![prism])
}

/// `pisco_cap_service_cuts(s)`: the opening the Pisco cap's leaves swing through fore.
pub fn pisco_cap_service_cuts(rt: &Rt, station: &Val) -> Result<Vec<Val>> {
    let st = state(rt)?;
    let s = Rec::of(station)?;
    let c = st.running;
    let half = s.num("outer")?.add(f(3.2)).add(c);
    let (ax, y0) = (s.num("axis_x")?, s.num("y0")?);
    Ok(vec![named_box(&st, vec![
        ax.sub(half).val(),
        ax.add(half).val(),
        y0.sub(c).sub(f(WALL)).sub(f(1.)).val(),
        y0.add(c).val(),
        s.num("split")?.sub(f(1.)).val(),
        s.val("bearing")?,
    ])?])
}

/// `asse_service_corner(s)`: the corner relief at the ASSE seat's fore east edge.
pub fn asse_service_corner(rt: &Rt, station: &Val) -> Result<Val> {
    let st = state(rt)?;
    let s = Rec::of(station)?;
    let c = st.running;
    let ax = s.num("axis_x")?;
    let x = ax.add(s.num("neck")?).add(f(WALL));
    let far = ax.add(s.num("outer")?).add(f(WALL)).add(f(1.));
    let z = s.num("split")?;
    let points = [
        t2(x.val(), z.sub(f(0.1)).val()),
        t2(far.val(), z.sub(f(0.1)).val()),
        t2(far.val(), z.add(f(WALL)).val()),
        t2(x.add(f(WALL)).val(), z.add(f(WALL)).val()),
    ];
    let solid = st.named("section_solid")?;
    let y0 = s.num("y0")?;
    let span = t2(y0.sub(c).sub(f(WALL)).sub(f(0.1)).val(), y0.add(c).val());
    py::call(&solid, vec![py::dict([("span", span), ("segments", Val::list(closed(&points)))])])
}

/// `pisco_station(axis_x, admitted_radius, axis_z, y0, y1)`: the Pisco's station, split 7 mm
/// above its axis.
pub fn pisco_station(rt: &Rt, axis_x: Val, admitted_radius: Num, axis_z: &Val, y0: Val, y1: Val) -> Result<Val> {
    let st = state(rt)?;
    let z = Num::of(axis_z)?;
    let web = f(WALL).sub(f(REACH)).sub(st.running);
    let split = z.add(f(7.));
    let neck = f(half_width(admitted_radius, split, z)?).add(web);
    let mut args = StationArgs::new(axis_x, neck.val(), y0, y1);
    args.split = split.val();
    args.wing_root = z.sub(f(REAR_ROOT_DROP)).val();
    args.tool_angle_degrees = Val::Float(75.);
    let result = station(rt, args)?;
    result.set(s("tool_inner_slope"), Val::Float(2.))?;
    Ok(result)
}

/// `pisco_cap_span(mouth_y, collet_start, rear)`: the Pisco cap's axial extent.
pub fn pisco_cap_span(rt: &Rt, mouth_y: &Val, collet_start: &Val, rear: &Val) -> Result<Val> {
    let st = state(rt)?;
    let fore = Num::of(mouth_y)?.sub(Num::of(collet_start)?).add(st.running).add(f(0.01));
    let aft = Num::of(rear)?.sub(f(WALL)).sub(st.running);
    Ok(t2(fore.val(), aft.val()))
}

/// `cap_section(s, base, bottom, axis_z=None, hexed=False)`: the snap cap's XZ section.
pub fn cap_section(station: &Val, base: &Val, bottom: &Val, axis_z: &Val, hexed: &Val) -> Result<Val> {
    let s = Rec::of(station)?;
    let (c_v, w, wi, h) = (s.val("axis_x")?, s.num("outer")?, s.num("inner")?, s.num("hook")?);
    let c = Num::of(&c_v)?;
    let (catch_v, tip_v) = (s.val("catch")?, s.val("tip")?);
    let catch = Num::of(&catch_v)?;
    let no_axis = matches!(axis_z, Val::None);
    let root_v = s.get("root", if no_axis { base.clone() } else { axis_z.clone() })?;
    let root = Num::of(&root_v)?;
    let given = Num::of(base)?;
    let (base_v, base) = if order(root.f(), given.f())?.is_lt() { (root_v.clone(), root) } else { (base.clone(), given) };
    let radius = Num::of(&s.get("root_radius", Val::Float(ROOT_RADIUS))?)?;
    let west = [
        t2(c.sub(w).val(), root_v.clone()),
        t2(c.sub(w).val(), tip_v),
        t2(c.sub(h).val(), catch.add(s.num("nose_land")?).val()),
        t2(c.sub(h).val(), catch_v.clone()),
        t2(c.sub(wi).val(), catch_v),
        t2(c.sub(wi).val(), base.add(radius).val()),
    ];
    let mut east = Vec::with_capacity(west.len());
    for p in west.iter().rev() {
        let xz = py::unpack(p, 2)?;
        east.push(t2(Num::I(2).mul(c).sub(Num::of(&xz[0])?).val(), xz[1].clone()));
    }
    let a = t2(c.sub(wi).add(radius).val(), base_v.clone());
    let b = t2(c.add(wi).sub(radius).val(), base_v);
    let k = div(radius, f(2f64.sqrt()))?;
    let mut edges = run(&west);
    edges.push(arc(
        west[west.len() - 1].clone(),
        t2(c.sub(wi).add(radius).sub(k).val(), base.add(radius).sub(k).val()),
        a.clone(),
        t2(c.sub(wi).add(radius).val(), base.add(radius).val()),
        true,
    ));
    edges.extend(run(&[a, b.clone()]));
    edges.push(arc(
        b,
        t2(c.add(wi).sub(radius).add(k).val(), base.add(radius).sub(k).val()),
        east[0].clone(),
        t2(c.add(wi).sub(radius).val(), base.add(radius).val()),
        true,
    ));
    edges.extend(run(&east));
    let east_end = east[east.len() - 1].clone();
    if no_axis {
        edges.extend(run(&[east_end, t2(c.add(w).val(), bottom.clone()), t2(c.sub(w).val(), bottom.clone()), west[0].clone()]));
    } else if hexed.truthy()? {
        let z = Num::of(axis_z)?;
        let low = z.sub(div(w.mul(f(3f64.sqrt())), f(2.))?).val();
        let half = div(w, f(2.))?;
        edges.extend(run(&[east_end, t2(c.add(half).val(), low.clone()), t2(c.sub(half).val(), low), west[0].clone()]));
    } else {
        let z0 = Num::of(axis_z)?;
        let r = z0.sub(Num::of(bottom)?);
        let z = root.sub(z0);
        let distance2 = w.mul(w).add(z.mul(z));
        let tangent = div(r.mul(f(sqrt(max2(distance2.sub(r.mul(r)), f(0.))?)?)), distance2)?;
        let tx = div(r.mul(r).mul(w), distance2)?.add(tangent.mul(z));
        let tz = div(r.mul(r).mul(z), distance2)?.sub(tangent.mul(w));
        let east_tangent = t2(c.add(tx).val(), z0.add(tz).val());
        let west_tangent = t2(c.sub(tx).val(), z0.add(tz).val());
        edges.extend(run(&[east_end, east_tangent.clone()]));
        edges.push(arc(east_tangent, t2(c_v.clone(), bottom.clone()), west_tangent.clone(), t2(c_v, axis_z.clone()), false));
        edges.extend(run(&[west_tangent, west[0].clone()]));
    }
    Ok(py::dict([("segments", Val::list(edges)), ("span", t2(s.val("y0")?, s.val("y1")?))]))
}

/// `section_solid(section)`: an XZ section of lines and arcs extruded along Y over its span.
pub fn section_solid(rt: &Rt, section: &Val) -> Result<Val> {
    let st = state(rt)?;
    let section = py::snapshot(section)?;
    let v = |p: &Val| -> Result<Val> {
        st.vector(p.get(Val::Int(0))?, section.get(s("span"))?.get(Val::Int(0))?, p.get(Val::Int(1))?)
    };
    let mut edges = vec![];
    for segment in section.get(s("segments"))?.iter()? {
        if segment.contains(&s("line"))? {
            let pq = py::unpack(&segment.get(s("line"))?, 2)?;
            let make = st.lib("cq.Edge.makeLine")?;
            let (p, q) = (v(&pq[0])?, v(&pq[1])?);
            edges.push(py::call(&make, vec![p, q])?);
        } else {
            let points = py::unpack(&segment.get(s("arc"))?, 4)?;
            let make = st.lib("cq.Edge.makeThreePointArc")?;
            let (a, mid, b) = (v(&points[0])?, v(&points[1])?, v(&points[2])?);
            edges.push(py::call(&make, vec![a, mid, b])?);
        }
    }
    let extrude = st.lib("cq.Solid.extrudeLinear")?;
    let wire = py::call(&st.lib("cq.Wire.assembleEdges")?, vec![Val::list(edges)])?;
    let span = section.get(s("span"))?;
    let length = Num::of(&span.get(Val::Int(1))?)?.sub(Num::of(&span.get(Val::Int(0))?)?);
    let along = st.vector(Val::Float(0.), length.val(), Val::Float(0.))?;
    py::call(&extrude, vec![wire, Val::list(vec![]), along])
}

/// `cap(s, base, bottom, axis_z=None, hexed=False)`: the snap cap as a solid.
pub fn cap(rt: &Rt, station: &Val, base: &Val, bottom: &Val, axis_z: &Val, hexed: &Val) -> Result<Val> {
    let st = state(rt)?;
    let solid = st.named("section_solid")?;
    py::call(&solid, vec![cap_section(station, base, bottom, axis_z, hexed)?])
}

/// `at_world(location, point)`: a local point carried to the world frame.
pub fn at_world(rt: &Rt, location: &Val, point: &Val) -> Result<Val> {
    let st = state(rt)?;
    let vertex = py::call(&st.lib("cq.Vertex.makeVertex")?, point.iter()?)?;
    let moved = py::method(&vertex, "moved", vec![location.clone()])?;
    let centre = py::method(&py::method(&moved, "Center", vec![])?, "toTuple", vec![])?;
    py::call(&st.lib("np.array")?, vec![centre])
}

/// `build(...)`'s arguments.
pub struct BuildArgs {
    pub parts: Val,
    pub asse_axis: Val,
    pub asse_at: Val,
    pub asse_turn: Val,
    pub pisco_axis: Val,
    pub mouth_y: Val,
    pub ceiling: Val,
    pub rear: Val,
    pub side: Val,
    pub meter: Val,
    pub meter_at: Val,
}

/// `build(parts, asse_axis, asse_at, asse_turn, pisco_axis, mouth_y, ceiling, rear, side, meter,
/// meter_at)`: every seat and cap from the parts' sampled surfaces, with their numbers.
pub fn build(rt: &Rt, a: &BuildArgs) -> Result<Val> {
    let st = state(rt)?;
    let bfp = rt.import("multiplex_asse1022")?;
    let hw = {
        let file = py::call(&st.path, vec![st.ns.get("__file__")?])?;
        py::method(&file, "resolve", vec![])?.attr("parent")?.attr("parent")?
    };
    let mut names: Vec<Val> = CHAIN.iter().map(|name| s(*name)).collect();
    for name in a.parts.iter()? {
        if starts_with(&name, "pisco-")? {
            names.push(name);
        }
    }
    names.push(s("co2-check"));
    let pts = Val::dict(vec![]);
    for name in names {
        let shape = a.parts.get(name.clone())?.get(Val::Int(0))?;
        let sampled = surface_points(rt, &shape, &Val::Float(0.2))?;
        pts.set(name, sampled)?;
    }
    let (lo, hi, bin) = (Val::Float(370.), Val::Float(482.), Val::Float(0.1));
    let (c, sl) = (st.running, st.slip);
    let out = Val::dict(vec![]);
    let numbers = Val::dict(vec![]);
    let concatenate = st.lib("np.concatenate")?;
    let maximum = st.lib("np.maximum")?;
    let choose = st.lib("np.where")?;
    let coupled = py::call(&concatenate, vec![Val::list(vec![pts.get(s("gagira-coupling"))?, pts.get(s("jg-pp010822e"))?])])?;
    let pair = py::unpack(&envelope(rt, &coupled, &a.asse_axis, &lo, &hi, &bin)?, 2)?;
    let (ys, r_g) = (pair[0].clone(), pair[1].clone());

    let wrench = |profile: &Val, across: &Val, clock: f64| -> Result<Val> {
        let ends = [profile.get(Val::Int(0))?.get(Val::Int(0))?, profile.get(Val::Int(-1))?.get(Val::Int(0))?];
        let mut y = Vec::with_capacity(2);
        for x in ends {
            let point = Val::Tuple(vec![x, Val::Float(0.), bfp.attr("BODY_CENTER_Z")?]);
            y.push(float(&at_world(rt, &a.asse_at, &point)?.get(Val::Int(1))?));
        }
        y.sort_by(|p, q| num::order(*p, *q));
        let mut radii = vec![];
        for row in profile.iter()? {
            radii.push(py::unpack(&row, 2)?[1].clone());
        }
        Ok(Val::Tuple(vec![
            py::flist(&y),
            div(Num::of(across)?, f(2.))?.val(),
            f(clock).add(Num::of(&a.asse_turn)?).val(),
            pick(radii, Ordering::Greater)?,
        ]))
    };
    let wrenches = vec![
        wrench(&bfp.attr("BODY_PROFILE")?, &bfp.attr("HEX_ACROSS_FLATS")?, 0.3)?,
        wrench(&bfp.attr("CAP_PROFILE")?, &bfp.attr("CAP_ACROSS_FLATS")?, 0.9)?,
    ];
    let mut wrench_rooms = vec![];
    for w in &wrenches {
        let w4 = py::unpack(w, 4)?;
        let y = py::unpack(&w4[0], 2)?;
        let fore = Num::of(&y[0])?.sub(f(THREAD)).mul(f(10.)).f().floor() as i64;
        let aft = Num::of(&y[1])?.add(f(THREAD)).mul(f(10.)).f().ceil() as i64;
        wrench_rooms.push([Val::Float(fore as f64 / 10.), Val::Float(aft as f64 / 10.), w4[1].clone(), w4[2].clone(), w4[3].clone()]);
    }
    let sampled = pts.get(s("multiplex-asse1022"))?;
    let axis_z = a.asse_axis.get(Val::Int(1))?;
    let under = Num::of(&axis_z)?.sub(div(Num::of(&bfp.attr("HEX_ACROSS_FLATS")?)?, f(2.))?).sub(f(0.5));
    let vent = sampled.get(Val::Bool(truth("lt", sampled.get(column(2))?, under.val())?))?;
    let asse = sampled.get(Val::Bool(truth("ge", sampled.get(column(2))?, under.val())?))?;
    let rr = py::call(&st.lib("np.hypot")?, vec![
        interop::binary("sub", asse.get(column(0))?, a.asse_axis.get(Val::Int(0))?)?,
        interop::binary("sub", asse.get(column(2))?, axis_z.clone())?,
    ])?;
    let mut keep = py::call(&st.lib("np.ones")?, vec![Val::Int(asse.len()? as i64), Val::Type("bool".into())])?;
    for w in &wrenches {
        let w4 = py::unpack(w, 4)?;
        let y = py::unpack(&w4[0], 2)?;
        let fore = truth("le", asse.get(column(1))?, y[0].clone())?;
        let aft = truth("ge", asse.get(column(1))?, y[1].clone())?;
        let inside = truth("le", rr.clone(), w4[1].clone())?;
        keep = interop::binary("and", keep, Val::Int(i64::from(fore) | i64::from(aft) | i64::from(inside)))?;
    }
    let body = py::call(&concatenate, vec![Val::list(vec![asse.get(keep)?, pts.get(s("jg-pi4512f6s"))?])])?;
    let r_b = py::unpack(&envelope(rt, &body, &a.asse_axis, &lo, &hi, &bin)?, 2)?[1].clone();
    let cav = py::call(&maximum, vec![
        swept(rt, &r_g, &Val::Float(0.), &Val::Float(SLIDE), &bin)?,
        swept(rt, &r_b, &Val::Float(THREAD), &f(SLIDE).add(f(THREAD)).val(), &bin)?,
    ])?;
    let cav = py::call(&choose, vec![
        Val::Bool(truth("gt", cav.clone(), Val::Int(0))?),
        interop::binary("add", cav.clone(), c.val())?,
        Val::Float(0.),
    ])?;
    let asse_steps = steps(&ys, &cav, 0.2, 0.1, 1.5)?;
    let cap_rows = bfp.attr("CAP_PROFILE")?.iter()?;
    let mut radii = vec![];
    for row in &cap_rows {
        radii.push(py::unpack(row, 2)?[1].clone());
    }
    let tallest = pick(radii, Ordering::Greater)?.num()?;
    let mut bonnets = vec![];
    for row in &cap_rows {
        let xr = py::unpack(row, 2)?;
        if xr[1].num()? == tallest {
            bonnets.push(xr[0].clone());
        }
    }
    let bonnet = pick(bonnets, Ordering::Greater)?;
    let gag_fore = py::method(&a.parts.get(s("gagira-coupling"))?.get(Val::Int(0))?, "BoundingBox", vec![])?.attr("ymin")?;
    let bonnet_world = at_world(rt, &a.asse_at, &Val::Tuple(vec![bonnet, Val::Float(0.), bfp.attr("BODY_CENTER_Z")?]))?;
    let cap_y = (f(float(&bonnet_world.get(Val::Int(1))?)).sub(sl), Num::of(&gag_fore)?.sub(sl));
    let split = Num::of(&axis_z)?.add(c);
    let m = Val::Int(
        i64::from(truth("ge", ys.clone(), cap_y.0.sub(f(0.25)).val())?)
            & i64::from(truth("le", ys.clone(), cap_y.1.add(f(0.25)).val())?),
    );
    let mut widths = vec![py::method(&cav.get(m)?, "max", vec![])?];
    for w in &wrenches {
        let row = w.iter()?;
        let corner = row.last().context("not enough values to unpack")?;
        widths.push(Num::of(corner)?.add(c).val());
    }
    let widest = pick(widths, Ordering::Greater)?;
    let neck = f(half_width(Num::of(&widest)?, split, Num::of(&axis_z)?)?).add(f(WALL));
    let mut args = StationArgs::new(a.asse_axis.get(Val::Int(0))?, neck.val(), cap_y.0.val(), cap_y.1.val());
    args.split = split.val();
    args.wing_root = Num::of(&axis_z)?.sub(f(REAR_ROOT_DROP)).val();
    let st_a = station(rt, args)?;
    let cap_profile = asse_cap_profile(&Val::Tuple(wrenches.clone()), &sl.val())?;
    let v_lo = py::call_kw(&vent.attr("min")?, vec![], vec![("axis", Val::Int(0))])?;
    let v_hi = py::call_kw(&vent.attr("max")?, vec![], vec![("axis", Val::Int(0))])?;
    let plumbing = rt.import("rear_plumbing")?;
    let capture = st.named("asse_adapter_capture")?;
    let chain_frame = py::call(&plumbing.attr("plan")?, vec![])?.get(s("chain_frame"))?;
    let adapter = py::unpack(&py::call(&capture, vec![chain_frame, st_a.clone(), a.asse_axis.clone()])?, 2)?;
    let hexed = cap(rt, &st_a, &axis_z, &Val::None, &axis_z, &Val::Bool(true))?;
    let stock = py::call(&st.named("section_solid")?, vec![adapter[0].clone()])?;
    let snap = py::method(&hexed, "fuse", vec![stock])?;
    let solid = st.named("section_solid")?;
    let room = py::call(&st.named("asse_cap_room")?, vec![a.asse_axis.clone(), cap_profile.clone(), t2(cap_y.0.val(), cap_y.1.add(f(0.5)).val())])?;
    let room = py::call(&solid, vec![room])?;
    let snap = py::method(&snap, "cut", vec![room, radial_room(rt, &adapter[1])?])?;
    let lo_at = |i: i64| Num::of(&v_lo.get(Val::Int(i))?);
    let hi_at = |i: i64| Num::of(&v_hi.get(Val::Int(i))?);
    let slot = named_box(&st, vec![
        lo_at(0)?.sub(c).val(),
        hi_at(0)?.add(c).val(),
        lo_at(1)?.sub(f(THREAD)).sub(c).val(),
        hi_at(1)?.add(f(THREAD)).add(c).val(),
        lo_at(2)?.sub(f(1.)).val(),
        axis_z.clone(),
    ])?;
    out.set(s("asse-snap-cap"), py::method(&py::method(&snap, "cut", vec![slot])?, "clean", vec![])?)?;
    let w = Num::of(&st_a.get(s("outer"))?)?;
    let ax = Num::of(&a.asse_axis.get(Val::Int(0))?)?;
    let (rear, ceiling) = (Num::of(&a.rear)?, Num::of(&a.ceiling)?);
    let seat = named_box(&st, vec![
        ax.sub(w).val(),
        ax.add(w).val(),
        cap_y.0.sub(c).sub(f(WALL)).val(),
        rear.add(f(INTO)).val(),
        split.val(),
        ceiling.add(f(INTO)).val(),
    ])?;
    let mut room = turned(rt, &asse_steps, &a.asse_axis)?;
    for [y0, y1, apothem, clock, corner] in &wrench_rooms {
        let prism = hex_prism(
            rt,
            &a.asse_axis,
            &Num::of(apothem)?.add(c).val(),
            clock,
            &Num::of(y0)?.sub(f(SLIDE)).val(),
            y1,
            &Num::of(corner)?.add(c).val(),
        )?;
        room = py::method(&room, "fuse", vec![prism])?;
    }
    let mut seat = py::method(&seat, "cut", vec![room])?;
    for p in pockets(rt, &st_a)? {
        seat = py::method(&seat, "cut", vec![p])?;
    }
    let corner = asse_service_corner(rt, &st_a)?;
    out.set(s("asse-seat"), py::method(&py::method(&seat, "cut", vec![corner])?, "clean", vec![])?)?;
    let mut rows = vec![];
    for w in &wrenches {
        let w4 = py::unpack(w, 4)?;
        rows.push(py::dict([("y", w4[0].clone()), ("apothem", w4[1].clone()), ("clock", w4[2].clone()), ("corner", w4[3].clone())]));
    }
    numbers.set(s("asse"), py::dict([
        ("station", st_a.clone()),
        ("seat_runs", asse_steps),
        ("cap_profile", cap_profile),
        ("wrenches", Val::list(rows)),
        ("gagira_fore_y", gag_fore),
        ("vent", Val::list(vec![py::method(&v_lo, "tolist", vec![])?, py::method(&v_hi, "tolist", vec![])?])),
    ]))?;

    let load = st.json.attr("load")?;
    let open = interop::builtin("open").context("open")?;
    let file = py::call(&open, vec![interop::binary("truediv", hw, s("reference/compact-inline-candidates/dimensions.json"))?])?;
    let dims = py::call(&load, vec![file])?.get(s("pisco_rvfup_quarter"))?;
    let ranges = dims.get(s("fitted_exterior"))?.get(s("component_ranges_mm"))?;
    let profile = py::call(&st.lib("np.array")?, vec![dims.get(s("fitted_exterior"))?.get(s("profile_z_radius_mm"))?])?;
    let mut pisco = vec![];
    for name in pts.iter()? {
        if starts_with(&name, "pisco-")? {
            pisco.push(pts.get(name)?);
        }
    }
    let joined = py::call(&concatenate, vec![Val::list(pisco)])?;
    let pair = py::unpack(&envelope(rt, &joined, &a.pisco_axis, &lo, &hi, &bin)?, 2)?;
    let (ys2, r_p) = (pair[0].clone(), pair[1].clone());
    let r_c = py::unpack(&envelope(rt, &pts.get(s("co2-check"))?, &a.pisco_axis, &lo, &hi, &bin)?, 2)?[1].clone();
    let cav2 = py::call(&maximum, vec![
        swept(rt, &r_p, &Val::Float(0.), &Val::Float(SLIDE), &bin)?,
        swept(rt, &r_c, &Val::Float(0.5), &f(SLIDE).add(f(0.5)).val(), &bin)?,
    ])?;
    let cav2 = py::call(&choose, vec![
        Val::Bool(truth("gt", cav2.clone(), Val::Int(0))?),
        interop::binary("add", interop::binary("add", cav2.clone(), c.val())?, Val::Float(PISCO_RADIAL_RELIEF))?,
        Val::Float(0.),
    ])?;
    let (fitting, collet) = (ranges.get(s("outlet_fitting"))?, ranges.get(s("outlet_collet"))?);
    let neck_rows = Val::Int(
        i64::from(truth("gt", profile.get(column(0))?, fitting.get(Val::Int(0))?)?)
            & i64::from(truth("lt", profile.get(column(1))?, Val::Float(6.5))?),
    );
    let neck_z = profile.get(neck_rows)?.get(Val::Tuple(vec![Val::Int(0), Val::Int(0)]))?;
    let step_face = Num::of(&a.mouth_y)?.sub(Num::of(&neck_z)?);
    let pcap = pisco_cap_span(rt, &a.mouth_y, &collet.get(Val::Int(0))?, &a.rear)?;
    let (p0, p1) = (Num::of(&pcap.get(Val::Int(0))?)?, Num::of(&pcap.get(Val::Int(1))?)?);
    let m = Val::Int(
        i64::from(truth("ge", ys2.clone(), p0.sub(f(0.25)).val())?) & i64::from(truth("le", ys2.clone(), p1.add(f(0.25)).val())?),
    );
    let admitted = Num::of(&py::method(&cav2.get(m)?, "max", vec![])?)?;
    let st_p = pisco_station(rt, a.pisco_axis.get(Val::Int(0))?, admitted, &a.pisco_axis.get(Val::Int(1))?, p0.val(), p1.val())?;
    let w = Num::of(&st_p.get(s("outer"))?)?;
    let px = Num::of(&a.pisco_axis.get(Val::Int(0))?)?;
    let front = p0.sub(c).sub(f(WALL));
    let seat = named_box(&st, vec![
        px.sub(w).val(),
        px.add(w).val(),
        front.val(),
        rear.add(f(INTO)).val(),
        st_p.get(s("split"))?,
        ceiling.add(f(INTO)).val(),
    ])?;
    let admitted_runs = py::call(&choose, vec![Val::Bool(truth("ge", ys2.clone(), front.sub(Num::I(1)).val())?), cav2.clone(), Val::Float(0.)])?;
    let seat_profile = pisco_bearing_profile(&steps(&ys2, &admitted_runs, 0.2, 0.1, 1.5)?, &profile, &a.mouth_y)?;
    let mut seat = py::method(&seat, "cut", vec![turned(rt, &seat_profile, &a.pisco_axis)?])?;
    for p in pockets(rt, &st_p)? {
        seat = py::method(&seat, "cut", vec![p])?;
    }
    for opening in pisco_cap_service_cuts(rt, &st_p)? {
        seat = py::method(&seat, "cut", vec![opening])?;
    }
    out.set(s("pisco-seat"), py::method(&seat, "clean", vec![])?)?;
    let held_rows = Val::Int(
        i64::from(truth("ge", profile.get(column(0))?, Num::of(&a.mouth_y)?.sub(p1).sub(f(1.)).val())?)
            & i64::from(truth("le", profile.get(column(0))?, neck_z.clone())?),
    );
    let held = profile.get(held_rows)?;
    let r_body = Num::of(&py::method(&held.get(column(1))?, "max", vec![])?)?.add(f(PISCO_CAP_AIR));
    let outlet_rows = Val::Int(
        i64::from(truth("ge", profile.get(column(0))?, neck_z.clone())?)
            & i64::from(truth("le", profile.get(column(0))?, collet.get(Val::Int(0))?)?),
    );
    let outlet = profile.get(outlet_rows)?;
    let r_neck = Num::of(&py::method(&outlet.get(column(1))?, "max", vec![])?)?.add(f(PISCO_CAP_AIR));
    let lip = step_face.sub(sl);
    let cap_fit = py::call(&st.named("pisco_cap_fit")?, vec![profile.clone(), a.mouth_y.clone(), pcap.clone(), a.pisco_axis.clone(), neck_z])?;
    let pz = a.pisco_axis.get(Val::Int(1))?;
    let snap = cap(rt, &st_p, &st_p.get(s("root"))?, &Num::of(&pz)?.sub(r_body).sub(f(WALL)).val(), &Val::None, &Val::Bool(false))?;
    let mut grips = vec![];
    for extent in pisco_grip_stock(&st_p, &pz, &r_body.val(), &lip.val())?.iter()? {
        grips.push(named_box(&st, extent.iter()?)?);
    }
    let snap = py::method(&snap, "fuse", grips)?;
    let mut rooms = vec![];
    for name in ["body", "neck"] {
        let record = py::dict([("points", cap_fit.get(s(name))?), ("frame", cap_fit.get(s("frame"))?)]);
        rooms.push(radial_room(rt, &record)?);
    }
    out.set(s("pisco-snap-cap"), py::method(&py::method(&snap, "cut", rooms)?, "clean", vec![])?)?;
    numbers.set(s("pisco"), py::dict([
        ("station", st_p),
        ("step_face_y", step_face.val()),
        ("body_r", r_body.val()),
        ("neck_r", r_neck.val()),
        ("cap_fit", cap_fit),
        ("seat_runs", seat_profile),
        ("cap_release_drop_mm", Val::Float(3.6)),
        ("cap_service_fore_slide_mm", Val::Float(45.)),
        (
            "cap_service_route",
            s("Remove ASSE and meter caps; hold PISCO leaves open, lower 3.6 mm, disconnect the outlet stem check, then slide 45 mm fore."),
        ),
    ]))?;

    let meter = &a.meter;
    let at = |point: Val| at_world(rt, &a.meter_at, &point);
    let centre = at(Val::Tuple(vec![meter.attr("body_center_x")?, Val::Float(0.), meter.attr("body_center_z")?]))?;
    let (my, mz) = (float(&centre.get(Val::Int(1))?), float(&centre.get(Val::Int(2))?));
    let port = at(py::ftuple(&[0., 0., 0.]))?;
    let soda = (float(&port.get(Val::Int(0))?), float(&port.get(Val::Int(2))?));
    let wx = |y: Val| -> Result<f64> {
        Ok(float(&at(Val::Tuple(vec![meter.attr("body_center_x")?, y, meter.attr("body_center_z")?]))?.get(Val::Int(0))?))
    };
    let wy = |x: Val| -> Result<f64> { Ok(float(&at(Val::Tuple(vec![x, Val::Float(0.), Val::Float(0.)]))?.get(Val::Int(1))?)) };
    let under = meter.attr("underside_y")?;
    let mx = f(wx(Val::Float(7.3))?).sub(f(METER_AIR));
    let (fore, aft) = (f(SLIDE).add(f(VAR)), f(METER_HOUSING_FIT));
    let x0 = mx.sub(f(1.));
    let fit = f(METER_HOUSING_FIT);
    let mut housing = vec![];
    let fitted = py::call(&st.named("clearance_profile")?, vec![meter.attr("housing_profile")?, fit.val(), fit.val()])?;
    for row in fitted.iter()? {
        let yr = py::unpack(&row, 2)?;
        housing.push(t2(Val::Float(wx(yr[0].clone())?), yr[1].clone()));
    }
    let housing = Val::list(housing);
    let mut cup = stadium_profile_x(rt, &housing, &py::ftuple(&[my, mz]), &fore.val(), &aft.val())?;
    let boss_x = Num::of(&meter.attr("boss_x")?)?;
    for dy in [boss_x.neg(), boss_x] {
        let boss_z = Num::of(&meter.attr("boss_z")?)?;
        for dz in [boss_z.neg(), boss_z] {
            let (yc, zc) = (f(my).add(dy).val(), f(mz).add(dz).val());
            let boss = stadium_x(
                rt,
                &yc,
                &zc,
                &Num::of(&meter.attr("boss_radius")?)?.add(fit).val(),
                &fore.val(),
                &aft.val(),
                &f(wx(meter.attr("boss_y_range")?.get(Val::Int(0))?)?).sub(fit).val(),
                &f(wx(meter.attr("boss_y_range")?.get(Val::Int(1))?)?).add(fit).val(),
            )?;
            let head = stadium_x(
                rt,
                &yc,
                &zc,
                &Num::of(&meter.attr("screw_head_radius")?)?.add(fit).val(),
                &fore.val(),
                &aft.val(),
                &f(wx(meter.attr("screw_head_y_range")?.get(Val::Int(0))?)?).sub(fit).val(),
                &f(wx(meter.attr("screw_head_y_range")?.get(Val::Int(1))?)?).add(fit).val(),
            )?;
            cup = py::method(&cup, "fuse", vec![boss, head])?;
        }
    }
    let r_collar = Num::of(&pick(meter.attr("port_collar_radii")?.iter()?, Ordering::Greater)?)?;
    for sign in [-1., 1.] {
        let sign = f(sign);
        let mut y = [
            wy(sign.mul(Num::of(&meter.attr("port_neck_end")?)?).val())?,
            wy(sign.mul(Num::of(&meter.attr("port_collar_end")?)?).val())?,
        ];
        y.sort_by(|p, q| num::order(*p, *q));
        let (ya, yb) = (f(y[0]), f(y[1]));
        let collar_end = yb.add(st.collar_air);
        let start = ya.sub(fore).sub(f(METER_AIR));
        let collar = py::call(&st.lib("cq.Solid.makeCylinder")?, vec![
            r_collar.add(f(METER_AIR)).val(),
            collar_end.sub(start).val(),
            st.vector(Val::Float(soda.0), start.val(), Val::Float(soda.1))?,
            st.vector(Val::Int(0), Val::Int(1), Val::Int(0))?,
        ])?;
        let clip = named_box(&st, vec![
            x0.val(),
            f(soda.0).add(r_collar).add(f(1.)).val(),
            ya.sub(fore).sub(f(2.)).val(),
            yb.add(aft).add(f(2.)).val(),
            f(soda.1).sub(r_collar).sub(f(1.)).val(),
            f(soda.1).add(r_collar).add(f(1.)).val(),
        ])?;
        cup = py::method(&cup, "fuse", vec![py::method(&collar, "intersect", vec![clip])?])?;
    }
    let root = at_world(rt, &a.meter_at, &meter.attr("wire_root")?)?;
    let half = div(Num::of(&meter.attr("wire_root_width")?)?, f(2.))?;
    let wire_y = Num::of(&meter.attr("wire_root")?.get(Val::Int(1))?)?.add(div(Num::of(&meter.attr("wire_root_depth")?)?, f(2.))?);
    let mut wire_room = vec![
        x0.val(),
        f(wx(wire_y.val())?).add(f(METER_AIR)).val(),
        f(wy(half.neg().val())?).sub(fore).sub(f(METER_AIR)).val(),
        f(wy(half.val())?).add(aft).add(f(METER_AIR)).val(),
    ];
    let (seat_y, cap_y) = ((Val::Float(386.), Val::Float(446.)), (Val::Float(397.), Val::Float(435.)));
    let _core = f(wx(meter.attr("boss_y_range")?.get(Val::Int(0))?)?).sub(f(METER_AIR));
    let west_end = f(wx(under)?);
    let neck = f(soda.1).add(r_collar).add(f(METER_AIR)).sub(f(mz)).add(f(WALL));
    let mut args = StationArgs::new(Val::Float(0.), neck.val(), cap_y.0.clone(), cap_y.1.clone());
    args.split = Val::Float(0.);
    args.wing_root = west_end.sub(f(METER_AIR)).sub(mx).val();
    let st_m = station(rt, args)?;
    let w = Num::of(&st_m.get(s("outer"))?)?;
    let root_z = float(&root.get(Val::Int(2))?);
    wire_room.push(min2(f(root_z).sub(f(3.)), f(mz).sub(Num::of(&st_m.get(s("neck"))?)?))?.val());
    let root_z = float(&root.get(Val::Int(2))?);
    wire_room.push(f(root_z).add(Num::of(&meter.attr("wire_boss_len")?)?).add(f(METER_AIR)).val());
    let wiring = named_box(&st, wire_room)?;
    cup = py::method(&py::method(&cup, "fuse", vec![wiring])?, "clean", vec![])?;
    let to_world = |shape: &Val| -> Result<Val> {
        let turned = py::method(shape, "rotate", vec![ints(0, 0, 0), ints(0, 1, 0), Val::Int(90)])?;
        py::method(&turned, "translate", vec![Val::Tuple(vec![mx.val(), Val::Float(0.), Val::Float(mz)])])
    };
    let side = Num::of(&a.side)?;
    let seat = named_box(&st, vec![
        mx.val(),
        side.add(f(INTO)).val(),
        seat_y.0.clone(),
        seat_y.1.clone(),
        f(mz).sub(w).val(),
        f(mz).add(w).val(),
    ])?;
    let mut seat = py::method(&seat, "cut", vec![cup])?;
    for p in pockets(rt, &st_m)? {
        seat = py::method(&seat, "cut", vec![to_world(&p)?])?;
    }
    out.set(s("meter-seat"), py::method(&seat, "clean", vec![])?)?;
    let hollow = py::method(&radial_profile(rt, &housing)?, "translate", vec![py::ftuple(&[0., my, mz])])?;
    let neck_bore = py::call(&st.lib("cq.Solid.makeCylinder")?, vec![
        Num::of(&meter.attr("port_neck_radius")?)?.add(fit).val(),
        f(446.).sub(f(386.)).val(),
        st.vector(Val::Float(soda.0), seat_y.0.clone(), Val::Float(soda.1))?,
        st.vector(Val::Int(0), Val::Int(1), Val::Int(0))?,
    ])?;
    let hollow = py::method(&hollow, "fuse", vec![neck_bore])?;
    let bottom = west_end.sub(f(METER_AIR)).sub(f(METER_BACK)).sub(mx);
    let half = Num::of(&st_m.get(s("inner"))?)?.sub(f(ROOT_RADIUS)).sub(f(0.5));
    let blank = cap(rt, &st_m, &st_m.get(s("root"))?, &bottom.val(), &Val::None, &Val::Bool(false))?;
    let bearing = named_box(&st, vec![
        half.neg().val(),
        half.val(),
        cap_y.0.clone(),
        cap_y.1.clone(),
        bottom.val(),
        Num::of(&st_m.get(s("root"))?)?.add(f(METER_BEARING_DEPTH)).val(),
    ])?;
    let blank = py::method(&blank, "fuse", vec![bearing])?;
    let body = py::method(&to_world(&blank)?, "cut", vec![hollow])?;
    let solid = st.named("section_solid")?;
    let corner = meter_cap_corner_room(&mx.add(bottom).val(), &Val::Float(mz), &t2(cap_y.0.clone(), cap_y.1.clone()))?;
    let body = py::method(&body, "cut", vec![py::call(&solid, vec![corner])?])?;
    out.set(s("meter-snap-cap"), py::method(&body, "clean", vec![])?)?;
    numbers.set(s("meter"), py::dict([
        ("station", st_m),
        ("split_x", mx.val()),
        ("axis", py::flist(&[my, mz])),
        ("housing_air_mm", Val::Float(METER_AIR)),
        ("lower_leaf_span_mm", f(435.).sub(f(397.)).val()),
    ]))?;
    let solids = Val::dict(vec![]);
    for name in SOLIDS {
        solids.set(s(name), out.get(s(name))?)?;
    }
    Ok(t2(solids, numbers))
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::REAR_SNAPS))?;
    let json = rt.import("json")?;
    ns.set("json", json.clone())?;
    ns.set("math", rt.import("math")?)?;
    let path = rt.member("pathlib", "Path")?;
    ns.set("Path", path.clone())?;
    let np = rt.import("numpy")?;
    ns.set("np", np.clone())?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let fits = rt.import("fits")?;
    ns.set("fits", fits.clone())?;
    for (name, value) in CONSTANTS {
        ns.set(name, Val::Float(value))?;
    }
    ns.set("HOOK", Val::Float(HOOK))?;
    let catch = py::call_kw(&fits.attr("clearance")?, vec![], vec![("supported", Val::Bool(true))])?;
    ns.set("CATCH", catch.clone())?;
    ns.set("VAR", Val::Float(VAR))?;
    let slip = Num::of(&fits.attr("slip")?)?;
    let collar_air = f(VAR).add(slip);
    ns.set("METER_COLLAR_AXIAL_AIR", collar_air.val())?;
    ns.set("CHAIN", Val::Tuple(CHAIN.iter().map(|name| s(*name)).collect()))?;
    ns.set("SOLIDS", Val::Tuple(SOLIDS.iter().map(|name| s(*name)).collect()))?;
    ns.set("SEATS", Val::Tuple(SOLIDS.iter().step_by(2).map(|name| s(*name)).collect()))?;
    ns.set("CAPS", Val::Tuple(SOLIDS.iter().skip(1).step_by(2).map(|name| s(*name)).collect()))?;
    ns.set("ON", py::dict([
        ("asse-snap-cap", py::ftuple(&[0., 0., 1.])),
        ("pisco-snap-cap", py::ftuple(&[0., 0., 1.])),
        ("meter-snap-cap", py::ftuple(&[1., 0., 0.])),
    ]))?;
    let running = Num::of(&fits.attr("running")?)?;
    rt.keep(MODULE, State {
        ns: ns.clone(),
        np,
        cq,
        json,
        path,
        running,
        slip,
        catch: Num::of(&catch)?,
        collar_air,
        attrs: RefCell::new(vec![]),
    });
    ns.def(rt, "surface_points", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["shape", "step"], &[])?;
        let shape = a.req("shape")?;
        surface_points(rt, &shape, &a.opt("step").unwrap_or(Val::Float(0.2)))
    })?;
    ns.def(rt, "envelope", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["points", "axis", "lo", "hi", "step"], &[])?;
        let (points, axis, lo, hi) = (a.req("points")?, a.req("axis")?, a.req("lo")?, a.req("hi")?);
        envelope(rt, &points, &axis, &lo, &hi, &a.opt("step").unwrap_or(Val::Float(0.1)))
    })?;
    ns.def(rt, "swept", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["r", "behind", "ahead", "step"], &[])?;
        let (r, behind, ahead) = (a.req("r")?, a.req("behind")?, a.req("ahead")?);
        swept(rt, &r, &behind, &ahead, &a.opt("step").unwrap_or(Val::Float(0.1)))
    })?;
    ns.def(rt, "steps", |_, args, kw| {
        let mut a = py::bind(args, kw, &["ys", "r", "tol", "step", "shortest"], &[])?;
        let (ys, r) = (a.req("ys")?, a.req("r")?);
        let (tol, step, shortest) = (a.f64_or("tol", 0.2)?, a.f64_or("step", 0.1)?, a.f64_or("shortest", 1.5)?);
        steps(&ys, &r, tol, step, shortest)
    })?;
    ns.def(rt, "turned", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["profile", "axis"], &[])?;
        turned(rt, &a.req("profile")?, &a.req("axis")?)
    })?;
    ns.def(rt, "hex_prism", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["axis", "apothem", "clock_deg", "y0", "y1", "corner"], &[])?;
        let (axis, apothem, clock) = (a.req("axis")?, a.req("apothem")?, a.req("clock_deg")?);
        let (y0, y1, corner) = (a.req("y0")?, a.req("y1")?, a.req("corner")?);
        hex_prism(rt, &axis, &apothem, &clock, &y0, &y1, &corner)
    })?;
    ns.def(rt, "asse_cap_profile", |_, args, kw| {
        let mut a = py::bind(args, kw, &["wrenches", "air"], &[])?;
        asse_cap_profile(&a.req("wrenches")?, &a.req("air")?)
    })?;
    ns.def(rt, "meter_cap_corner_room", |_, args, kw| {
        let mut a = py::bind(args, kw, &["west", "centre_z", "span"], &[])?;
        meter_cap_corner_room(&a.req("west")?, &a.req("centre_z")?, &a.req("span")?)
    })?;
    ns.def(rt, "box", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["x0", "x1", "y0", "y1", "z0", "z1"], &[])?;
        let (x0, x1, y0, y1, z0, z1) = (a.req("x0")?, a.req("x1")?, a.req("y0")?, a.req("y1")?, a.req("z0")?, a.req("z1")?);
        make_box(rt, &x0, &x1, &y0, &y1, &z0, &z1)
    })?;
    ns.def(rt, "stadium_x", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["yc", "zc", "r", "fore", "aft", "x0", "x1"], &[])?;
        let (yc, zc, r, fore) = (a.req("yc")?, a.req("zc")?, a.req("r")?, a.req("fore")?);
        let (aft, x0, x1) = (a.req("aft")?, a.req("x0")?, a.req("x1")?);
        stadium_x(rt, &yc, &zc, &r, &fore, &aft, &x0, &x1)
    })?;
    ns.def(rt, "half_width", |_, args, kw| {
        let mut a = py::bind(args, kw, &["radius", "z", "axis_z"], &[])?;
        let (radius, z, axis_z) = (Num::of(&a.req("radius")?)?, Num::of(&a.req("z")?)?, Num::of(&a.req("axis_z")?)?);
        Ok(Val::Float(half_width(radius, z, axis_z)?))
    })?;
    ns.def(rt, "station", |rt, args, kw| {
        let mut a = py::bind(
            args,
            kw,
            &["axis_x", "neck", "y0", "y1", "split"],
            &["wing_root", "free_length", "tool_angle_degrees", "tool_end_stock"],
        )?;
        let mut call = StationArgs::new(a.req("axis_x")?, a.req("neck")?, a.req("y0")?, a.req("y1")?);
        if let Some(split) = a.opt("split") {
            call.split = split;
        }
        if let Some(wing_root) = a.opt("wing_root") {
            call.wing_root = wing_root;
        }
        if let Some(free_length) = a.opt("free_length") {
            call.free_length = free_length;
        }
        if let Some(angle) = a.opt("tool_angle_degrees") {
            call.tool_angle_degrees = angle;
        }
        if let Some(stock) = a.opt("tool_end_stock") {
            call.tool_end_stock = stock;
        }
        station(rt, call)
    })?;
    ns.def(rt, "receiver_tool_ports", |_, args, kw| {
        let mut a = py::bind(args, kw, &["s"], &[])?;
        Ok(Val::list(receiver_tool_ports(&a.req("s")?)))
    })?;
    ns.def(rt, "prism_x", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["x0", "x1", "points"], &[])?;
        prism_x(rt, &a.req("x0")?, &a.req("x1")?, &a.req("points")?)
    })?;
    ns.def(rt, "radial_profile", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["points"], &[])?;
        radial_profile(rt, &a.req("points")?)
    })?;
    ns.def(rt, "stadium_profile_x", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["points", "centre", "fore", "aft"], &[])?;
        let (points, centre, fore, aft) = (a.req("points")?, a.req("centre")?, a.req("fore")?, a.req("aft")?);
        stadium_profile_x(rt, &points, &centre, &fore, &aft)
    })?;
    ns.def(rt, "radial_room", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["record"], &[])?;
        radial_room(rt, &a.req("record")?)
    })?;
    ns.def(rt, "pisco_grip_stock", |_, args, kw| {
        let mut a = py::bind(args, kw, &["s", "axis_z", "body_r", "neck_r", "lip"], &[])?;
        let (station, axis_z, body_r) = (a.req("s")?, a.req("axis_z")?, a.req("body_r")?);
        let _neck_r = a.req("neck_r")?;
        pisco_grip_stock(&station, &axis_z, &body_r, &a.req("lip")?)
    })?;
    ns.def(rt, "pisco_bearing_profile", |_, args, kw| {
        let mut a = py::bind(args, kw, &["runs", "profile", "mouth_y"], &[])?;
        pisco_bearing_profile(&a.req("runs")?, &a.req("profile")?, &a.req("mouth_y")?)
    })?;
    ns.def(rt, "pockets", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["s"], &[])?;
        Ok(Val::list(pockets(rt, &a.req("s")?)?))
    })?;
    ns.def(rt, "pisco_cap_service_cuts", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["s"], &[])?;
        Ok(Val::list(pisco_cap_service_cuts(rt, &a.req("s")?)?))
    })?;
    ns.def(rt, "asse_service_corner", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["s"], &[])?;
        asse_service_corner(rt, &a.req("s")?)
    })?;
    ns.def(rt, "pisco_station", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["axis_x", "admitted_radius", "axis_z", "y0", "y1"], &[])?;
        let (axis_x, admitted, axis_z) = (a.req("axis_x")?, Num::of(&a.req("admitted_radius")?)?, a.req("axis_z")?);
        pisco_station(rt, axis_x, admitted, &axis_z, a.req("y0")?, a.req("y1")?)
    })?;
    ns.def(rt, "pisco_cap_span", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["mouth_y", "collet_start", "rear"], &[])?;
        pisco_cap_span(rt, &a.req("mouth_y")?, &a.req("collet_start")?, &a.req("rear")?)
    })?;
    ns.def(rt, "cap_section", |_, args, kw| {
        let mut a = py::bind(args, kw, &["s", "base", "bottom", "axis_z", "hexed"], &[])?;
        let (station, base, bottom) = (a.req("s")?, a.req("base")?, a.req("bottom")?);
        let axis_z = a.opt("axis_z").unwrap_or(Val::None);
        cap_section(&station, &base, &bottom, &axis_z, &a.opt("hexed").unwrap_or(Val::Bool(false)))
    })?;
    ns.def(rt, "section_solid", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["section"], &[])?;
        section_solid(rt, &a.req("section")?)
    })?;
    ns.def(rt, "cap", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["s", "base", "bottom", "axis_z", "hexed"], &[])?;
        let (station, base, bottom) = (a.req("s")?, a.req("base")?, a.req("bottom")?);
        let axis_z = a.opt("axis_z").unwrap_or(Val::None);
        cap(rt, &station, &base, &bottom, &axis_z, &a.opt("hexed").unwrap_or(Val::Bool(false)))
    })?;
    ns.def(rt, "at_world", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["location", "point"], &[])?;
        at_world(rt, &a.req("location")?, &a.req("point")?)
    })?;
    ns.def(rt, "build", |rt, args, kw| {
        let mut a = py::bind(
            args,
            kw,
            &["parts", "asse_axis", "asse_at", "asse_turn", "pisco_axis", "mouth_y", "ceiling", "rear", "side", "meter", "meter_at"],
            &[],
        )?;
        let call = BuildArgs {
            parts: a.req("parts")?,
            asse_axis: a.req("asse_axis")?,
            asse_at: a.req("asse_at")?,
            asse_turn: a.req("asse_turn")?,
            pisco_axis: a.req("pisco_axis")?,
            mouth_y: a.req("mouth_y")?,
            ceiling: a.req("ceiling")?,
            rear: a.req("rear")?,
            side: a.req("side")?,
            meter: a.req("meter")?,
            meter_at: a.req("meter_at")?,
        };
        build(rt, &call)
    })?;
    Ok(())
}
