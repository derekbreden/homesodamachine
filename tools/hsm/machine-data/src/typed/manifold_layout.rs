//! Two-channel flavor manifold with a purchased tee on each pump port.
//!
//! The study lays each limb's valves and tees out butted along its axis, folds the bodies ahead
//! of each anchor over the hinge, turns the two source valves round their quarters, and takes the
//! four pump tees, their upper tubes and their lower returns from `fixed_returns`. `numbers` is the
//! payload the Rust part cutter builds the study from; `report` prints the routing figures and
//! `_write_readme` fills the study's README.
use super::num::{self, Num};
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::{Context, Result, anyhow, bail, ensure};
use hsm_documents::interop::{self, Val};
use py::s;
use std::cell::{OnceCell, RefCell};
use std::f64::consts::PI;
use std::ops::{Add, Mul, Neg, Sub};
use std::path::PathBuf;
use std::rc::Rc;

/// Not yet compared with the generated build: the hybrid development build runs the generated namespace.
pub const TYPED: bool = false;

const MODULE: &str = "manifold_layout";

// ---------------------------------------------------------------------------------------------
// Numbers as the runtime holds them.

/// An int or a float, combining as the runtime combines them.
#[derive(Clone, Copy, Debug)]
struct N(Num);
impl N {
    const fn fl(x: f64) -> N {
        N(Num::F(x))
    }
    const fn int(i: i64) -> N {
        N(Num::I(i))
    }
    fn of(v: &Val) -> Result<N> {
        Ok(N(Num::of(v)?))
    }
    fn f(self) -> f64 {
        self.0.f()
    }
    fn val(self) -> Val {
        self.0.val()
    }
    fn fmt(self, spec: &str) -> String {
        self.0.fmt(spec)
    }
    fn is_int(self) -> bool {
        matches!(self.0, Num::I(_))
    }
    /// `abs(x)`: an int stays an int.
    fn abs(self) -> N {
        match self.0 {
            Num::I(i) => N::int(i.abs()),
            Num::F(x) => N::fl(x.abs()),
        }
    }
}
impl Add for N {
    type Output = N;
    fn add(self, o: N) -> N {
        N(self.0.add(o.0))
    }
}
impl Sub for N {
    type Output = N;
    fn sub(self, o: N) -> N {
        N(self.0.sub(o.0))
    }
}
impl Mul for N {
    type Output = N;
    fn mul(self, o: N) -> N {
        N(self.0.mul(o.0))
    }
}
impl Neg for N {
    type Output = N;
    fn neg(self) -> N {
        N(self.0.neg())
    }
}
/// `a / b`: always a float.
fn div(a: N, b: N) -> Result<N> {
    Ok(N::fl(fdiv(a.f(), b.f())?))
}
fn fdiv(a: f64, b: f64) -> Result<f64> {
    ensure!(b != 0., "division by zero");
    Ok(a / b)
}
/// `x ** y` as the runtime computes it: one libm `pow` whose exponent the optimizer never sees,
/// so a constant `2` or `0.5` is not folded into a multiply or a square root.
fn fpow(x: f64, y: f64) -> f64 {
    x.powf(std::hint::black_box(y))
}
/// `a ** b`.
fn pow(a: N, b: N) -> N {
    let v = fpow(a.f(), b.f());
    if a.is_int() && b.is_int() && v.is_finite() && v.fract() == 0. { N::int(v as i64) } else { N::fl(v) }
}
/// `max(a, b)` and `min(a, b)`: the first wins a tie.
fn nmax(a: N, b: N) -> N {
    if b.f() > a.f() { b } else { a }
}
fn nmin(a: N, b: N) -> N {
    if b.f() < a.f() { b } else { a }
}
fn sqrt(x: f64) -> Result<f64> {
    ensure!(x >= 0., "math domain error");
    Ok(x.sqrt())
}
fn acos(x: f64) -> Result<f64> {
    let v = x.acos();
    ensure!(v.is_finite(), "math domain error");
    Ok(v)
}
/// `max(0.0, x)`.
fn floor0(x: f64) -> f64 {
    if x > 0. { x } else { 0. }
}

type V3 = [N; 3];
fn fv3(v: [f64; 3]) -> V3 {
    v.map(N::fl)
}
fn tup(v: V3) -> Val {
    Val::Tuple(v.iter().map(|n| n.val()).collect())
}
fn ftup2(a: f64, b: f64) -> Val {
    Val::Tuple(vec![Val::Float(a), Val::Float(b)])
}
fn add3(a: V3, b: V3) -> V3 {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}
fn sub3(a: V3, b: V3) -> V3 {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}
fn cross(a: V3, b: V3) -> V3 {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}
/// Authoring coordinates carried to the enclosure's fitted pump datum, and back.
fn enc_pt(p: V3) -> V3 {
    [-p[0], p[2] + N::fl(PACK_ORIGIN_Y), p[1] + N::fl(WORLD_LIFT)]
}
fn auth_pt(p: V3) -> V3 {
    [-p[0], p[2] - N::fl(WORLD_LIFT), p[1] - N::fl(PACK_ORIGIN_Y)]
}
/// `enclosure_axis` and `authoring_axis` are the same swap.
fn swap_axis(a: V3) -> V3 {
    [-a[0], a[2], a[1]]
}
fn fold_dir(d: V3) -> V3 {
    [d[0], -d[1], -d[2]]
}
fn bend_dir(d: V3) -> V3 {
    [d[0], -d[2], d[1]]
}
/// The module's own `dist`: the square root as a power.
fn dist(a: V3, b: V3) -> N {
    let mut total = N::int(0);
    for i in 0..3 {
        total = total + pow(a[i] - b[i], N::int(2));
    }
    pow(total, N::fl(0.5))
}

// Values a caller hands in.
fn neg(v: &Val) -> Result<Val> {
    interop::unary("neg", v.clone())
}
/// `p[0], p[1], p[2]`.
fn items3(v: &Val) -> Result<Vec<Val>> {
    (0..3).map(|i| v.get(Val::Int(i))).collect()
}
fn index3(v: &Val) -> Result<V3> {
    let r = items3(v)?;
    Ok([N::of(&r[0])?, N::of(&r[1])?, N::of(&r[2])?])
}
/// `x, y, z = v`.
fn unpack3(v: &Val) -> Result<V3> {
    let r = py::unpack(v, 3)?;
    Ok([N::of(&r[0])?, N::of(&r[1])?, N::of(&r[2])?])
}
fn missing(key: &str) -> anyhow::Error {
    anyhow!("missing key {}", s(key).repr().unwrap_or_default())
}
/// A body or junction name: anything but a string is a key no table holds.
fn name_of(v: &Val) -> Result<String> {
    match v {
        Val::Str(t) => Ok(t.clone()),
        other => Err(anyhow!("missing key {}", other.repr()?)),
    }
}
fn fmtv(v: &Val, spec: &str) -> Result<String> {
    interop::format(v, spec)
}
fn names(list: &[&str]) -> Val {
    Val::list(list.iter().map(|n| s(*n)).collect())
}
fn same(a: &Val, b: &Val) -> Result<bool> {
    interop::compare("is", a.clone(), b.clone())?.truthy()
}

// ---------------------------------------------------------------------------------------------
// The study's own figures and tables.

const FLAVOR_SKEW: f64 = 22.0;
const LINE_HUG: f64 = 1.0;
const BUTT: f64 = 0.0;
const FORE_VALVE_RISE: f64 = 0.0;
const OUTER_AFT_X: f64 = 73.82;
const CARRIER_DATUM_SHIFT: f64 = -1.75;
const FIXED_TEE_AFT_SHIFT: f64 = 0.0;
const AFT_DECK_AFT_SHIFT: f64 = 0.0;
const AFT_PACK_RISE: f64 = 0.5;
const WORLD_LIFT: f64 = 201.425;
const PACK_ORIGIN_Y: f64 = 14.48;
const BARB_TO_PLATE: f64 = 5.351;
const PUMP_TUBE_HELD: f64 = 13.149;
const PUMP_BARBS_TO_BORE_FACE: f64 = 5.526;
const CROSSBAR: f64 = 0.0;
const ELBOW_LEG: f64 = 19.56;
const SOURCE_TRAVEL: f64 = 46.72;
const SOURCE_JOG: f64 = 13.625;
const SOURCE_SLACK: f64 = 0.5;
const HAIRPIN_OUT: f64 = 15.0;
const HAIRPIN_TILT: f64 = 49.0;

/// The pump tees, in `BARB_OF` order, which is also their sorted order.
const JUNCTIONS: [&str; 4] = ["Y-C", "Y-D", "Y-F", "Y-G"];
const FORE_VALVES: [&str; 4] = ["V-E", "V-F", "V-H", "V-I"];
/// `BARB_OF`: each pump tee's pump (the sign of its centre) and the barb side it takes.
const BARB_OF: [(&str, f64, i64); 4] = [("Y-C", -1., 1), ("Y-D", -1., -1), ("Y-F", 1., -1), ("Y-G", 1., 1)];
/// `PUMP_VALVES`: each pump tee's upper (fore) valve and its return (rear) valve.
const PUMP_VALVES: [(&str, &str, &str); 4] =
    [("Y-C", "V-E", "V-C"), ("Y-D", "V-F", "V-G"), ("Y-F", "V-H", "V-D"), ("Y-G", "V-I", "V-J")];
const PUMP_PART_SUFFIX: [(&str, &str); 4] =
    [("Y-C", "east-inner"), ("Y-D", "east-outer"), ("Y-F", "west-inner"), ("Y-G", "west-outer")];
const SOURCE_SPREAD: [(&str, f64); 2] = [("V-A", 1.92), ("V-B", 0.0)];
/// The two source valves turned round a quarter onto the folded deck (`BENT`).
const BENT: [&str; 2] = ["V-A", "V-B"];
const SBENDS: [(i64, &str); 2] = [(3, "V-A"), (5, "V-B")];
const LOWER_CONNECTIONS: [(i64, &str); 4] = [(9, "Y-C"), (17, "Y-D"), (19, "Y-F"), (27, "Y-G")];
const FORE_STUB_ROWS: [(&str, &str, &str); 4] =
    [("fore-y-c", "Y-C", "V-E"), ("fore-y-d", "Y-D", "V-F"), ("fore-y-f", "Y-F", "V-H"), ("fore-y-g", "Y-G", "V-I")];
const SEGMENTS: [(i64, &str, &str, &str); 17] = [
    (3, "V-A-O", "Y-A-1", "turn"),
    (5, "V-B-O", "Y-B-1", "turn"),
    (6, "Y-A-3", "Y-B-3", "crossbar"),
    (7, "Y-A-2", "V-C-I", "butt"),
    (8, "Y-B-2", "V-D-I", "butt"),
    (9, "V-C-O", "Y-C-1", "spine"),
    (10, "V-E-O", "Y-C-2", "fore-y-c"),
    (11, "Y-C-3", "P-A-I", "Y-C"),
    (12, "P-A-O", "Y-D-1", "Y-D"),
    (13, "Y-D-2", "V-F-I", "fore-y-d"),
    (17, "Y-D-3", "V-G-I", "spine"),
    (19, "V-D-O", "Y-F-1", "spine"),
    (20, "V-H-O", "Y-F-2", "fore-y-f"),
    (21, "Y-F-3", "P-B-I", "Y-F"),
    (22, "P-B-O", "Y-G-1", "Y-G"),
    (23, "Y-G-3", "V-I-I", "fore-y-g"),
    (27, "Y-G-2", "V-J-I", "spine"),
];
/// `MOUTHS` before their ports: `(cid, port label, what, body, end)`.
const MOUTH_ROWS: [(&str, &str, &str, &str, &str); 8] = [
    ("fluid-2", "V-A-I", "tap water in", "V-A", "front"),
    ("fluid-4", "V-B-I", "funnel in", "V-B", "front"),
    ("fluid-18", "V-G-O", "flavor A", "V-G", "front"),
    ("fluid-28", "V-J-O", "flavor B", "V-J", "front"),
    ("fluid-14", "V-F-O", "reservoir A fill", "V-F", "back"),
    ("fluid-16", "V-E-I", "reservoir A draw", "V-E", "back"),
    ("fluid-24", "V-I-O", "reservoir B fill", "V-I", "back"),
    ("fluid-26", "V-H-I", "reservoir B draw", "V-H", "back"),
];
const TWINS: [(&str, &str); 8] = [
    ("V-A", "V-B"),
    ("V-C", "V-D"),
    ("V-E", "V-H"),
    ("V-F", "V-I"),
    ("V-G", "V-J"),
    ("Y-A", "Y-B"),
    ("Y-C", "Y-F"),
    ("Y-D", "Y-G"),
];
const FOLD_BINDS: (&str, &str) = ("a folded valve's underside", "the spades of the one beneath it");

fn is_junction(name: &str) -> bool {
    JUNCTIONS.contains(&name)
}
fn is_bent(name: &str) -> bool {
    BENT.contains(&name)
}
fn junction_index(name: &str) -> Result<usize> {
    JUNCTIONS.iter().position(|n| *n == name).ok_or_else(|| missing(name))
}
/// A chain entry's materialized name: its body kind and lower-case chain name.
fn body_name(chain: &str) -> String {
    format!("{}-{}", if chain.starts_with("V-") { "valve" } else { "tee" }, chain.to_lowercase())
}
fn valve_dirs(flow: i64) -> (V3, V3) {
    (fv3([flow as f64, 0., 0.]), fv3([0., 0., 1.]))
}
fn tee_dirs(branch: [f64; 3]) -> (V3, V3) {
    let (bx, bz) = (branch[0], branch[2]);
    if bz != 0. {
        return (fv3([1., 0., 0.]), fv3(if bz < 0. { [0., 1., 0.] } else { [0., -1., 0.] }));
    }
    (fv3([0., 0., bx]), fv3([0., 1., 0.]))
}

/// What a chain entry carries: a valve's flow sign or a tee's branch direction.
#[derive(Clone, Copy)]
enum Arg {
    Flow(i64),
    Branch([f64; 3]),
}
impl Arg {
    fn val(self) -> Val {
        match self {
            Arg::Flow(f) => Val::Int(f),
            Arg::Branch(b) => py::ftuple(&b),
        }
    }
}
struct Limb {
    limb: &'static str,
    outer: bool,
    east: bool,
    anchor: usize,
    chain: &'static [(&'static str, Arg)],
}
const LIMBS: [Limb; 4] = [
    Limb {
        limb: "A1",
        outer: false,
        east: false,
        anchor: 3,
        chain: &[
            ("V-A", Arg::Flow(1)),
            ("Y-A", Arg::Branch([1., 0., 0.])),
            ("V-C", Arg::Flow(1)),
            ("Y-C", Arg::Branch([0., 0., -1.])),
            ("V-E", Arg::Flow(-1)),
        ],
    },
    Limb {
        limb: "A2",
        outer: true,
        east: false,
        anchor: 1,
        chain: &[("V-G", Arg::Flow(-1)), ("Y-D", Arg::Branch([0., 0., -1.])), ("V-F", Arg::Flow(1))],
    },
    Limb {
        limb: "B1",
        outer: false,
        east: true,
        anchor: 3,
        chain: &[
            ("V-B", Arg::Flow(1)),
            ("Y-B", Arg::Branch([-1., 0., 0.])),
            ("V-D", Arg::Flow(1)),
            ("Y-F", Arg::Branch([0., 0., -1.])),
            ("V-H", Arg::Flow(-1)),
        ],
    },
    Limb {
        limb: "B2",
        outer: true,
        east: true,
        anchor: 1,
        chain: &[("V-J", Arg::Flow(-1)), ("Y-G", Arg::Branch([0., 0., -1.])), ("V-I", Arg::Flow(1))],
    },
];

/// What `lay_out` reads.
#[derive(Clone, Copy)]
struct Lay {
    valve_len: N,
    tee_run: N,
    inner_x: N,
    outer_x: N,
}
impl Lay {
    fn limb_x(&self, l: &Limb) -> N {
        let x = if l.outer { self.outer_x } else { self.inner_x };
        if l.east { x } else { -x }
    }
    /// Half a body's own length along the limb, collet face to centre.
    fn half(&self, name: &str) -> N {
        if name.starts_with("V-") { N::fl(self.valve_len.f() / 2.) } else { self.tee_run }
    }
}

/// One body of `P`: its limb, centre and both collet faces along the limb.
struct Body {
    name: &'static str,
    limb: &'static str,
    x: N,
    y: N,
    arg: Arg,
    fold: bool,
    front: N,
    back: N,
}
impl Body {
    fn val(&self) -> Val {
        py::dict([
            ("limb", s(self.limb)),
            ("x", self.x.val()),
            ("y", self.y.val()),
            ("arg", self.arg.val()),
            ("fold", Val::Bool(self.fold)),
            ("front", self.front.val()),
            ("back", self.back.val()),
        ])
    }
    /// `P[name][key]`.
    fn field(&self, key: &Val) -> Result<Val> {
        let Val::Str(k) = key else { bail!("missing key {}", key.repr()?) };
        Ok(match k.as_str() {
            "limb" => s(self.limb),
            "x" => self.x.val(),
            "y" => self.y.val(),
            "arg" => self.arg.val(),
            "fold" => Val::Bool(self.fold),
            "front" => self.front.val(),
            "back" => self.back.val(),
            _ => bail!("missing key {}", key.repr()?),
        })
    }
}

/// Every body butted along its limb, the anchor tee's centre at y = 0.
fn lay_out(lay: &Lay) -> Vec<Body> {
    let mut out = Vec::new();
    for l in &LIMBS {
        let x = lay.limb_x(l);
        let mut centres = Vec::new();
        let mut y = N::fl(0.);
        for (n, _) in l.chain {
            let c = y + lay.half(n);
            centres.push(c);
            y = c + lay.half(n) + N::fl(BUTT);
        }
        let shift = -centres[l.anchor];
        for (i, ((n, arg), c)) in l.chain.iter().zip(&centres).enumerate() {
            out.push(Body {
                name: n,
                limb: l.limb,
                x,
                y: *c + shift,
                arg: *arg,
                fold: i < l.anchor,
                front: *c + shift - lay.half(n),
                back: *c + shift + lay.half(n),
            });
        }
    }
    out
}
fn bodies_val(bodies: &[Body]) -> Val {
    Val::dict(bodies.iter().map(|b| (s(b.name), b.val())).collect())
}
fn limbs_val(lay: &Lay) -> Val {
    Val::dict(
        LIMBS
            .iter()
            .map(|l| {
                let chain = l.chain.iter().map(|(n, a)| Val::Tuple(vec![s(*n), a.val()])).collect();
                (s(l.limb), py::dict([("x", lay.limb_x(l).val()), ("anchor", Val::Int(l.anchor as i64)), ("chain", Val::list(chain))]))
            })
            .collect(),
    )
}

/// The two-arc family's least travel for a step of `jog` across at radius `r`.
fn two_arc_floor(r: f64, jog: f64) -> Result<f64> {
    sqrt(floor0(fpow(2. * r, 2.) - fpow(2. * r - jog, 2.)))
}
/// The arc angle and the straight between two arcs that step `jog` across in `travel` along.
fn sbend_solve(r: N, travel: N, jog: N) -> Result<(f64, f64)> {
    let a = 2. * r.f() - jog.f();
    let b = travel.f();
    let c = 2. * r.f();
    let m = num::hypot2(a, b);
    if c > m {
        bail!(
            "ValueError: a step of {} across in {} along cannot be made from two arcs of R{}: the pair reaches {} where it needs {}.",
            jog.fmt("g"),
            travel.fmt("g"),
            r.fmt("g"),
            num::fmt(m, ".2f"),
            num::fmt(c, "g")
        );
    }
    let th = b.atan2(a) - acos(fdiv(c, m)?)?;
    Ok((th, fdiv(b - 2. * r.f() * num::sin(th), num::cos(th))?))
}
fn hairpin_back(r: f64, travel: f64, jog: f64) -> Result<f64> {
    Ok(floor0(two_arc_floor(r, jog)? + SOURCE_SLACK - travel))
}

/// One flat segment of a step or hairpin: `("arc", a, mid, b)` or `("line", a, b)`.
struct Leg {
    kind: &'static str,
    points: Vec<[f64; 2]>,
}
impl Leg {
    fn val(&self) -> Val {
        let mut row = vec![s(self.kind)];
        row.extend(self.points.iter().map(|p| ftup2(p[0], p[1])));
        Val::Tuple(row)
    }
}
fn legs_val(legs: &[Leg]) -> Val {
    Val::list(legs.iter().map(Leg::val).collect())
}
/// The hairpin in its own plane's `(across, along)`.
fn hairpin_flat(r: f64, across: f64, back: N) -> Result<Vec<Leg>> {
    let aim = across.atan2((-back).f());
    let mut segs = Vec::new();
    let (mut p, mut h) = ([0f64, 0.], 0f64);
    for (turn, straight) in [(aim, num::hypot2(across, back.f())), (2. * PI - aim, 0.)] {
        let c = [p[0] + r * num::cos(h), p[1] - r * num::sin(h)];
        let at = |hh: f64| [c[0] - r * num::cos(hh), c[1] + r * num::sin(hh)];
        let n = (fdiv(turn, PI / 2.)? - 1e-9).ceil() as i64;
        let n = if n > 1 { n } else { 1 };
        for k in 0..n {
            let h0 = h + fdiv(turn * k as f64, n as f64)?;
            let h1 = h + fdiv(turn * (k + 1) as f64, n as f64)?;
            segs.push(Leg { kind: "arc", points: vec![at(h0), at((h0 + h1) / 2.), at(h1)] });
        }
        (p, h) = (at(h + turn), h + turn);
        if straight > 1e-9 {
            let q = [p[0] + straight * num::sin(h), p[1] + straight * num::cos(h)];
            segs.push(Leg { kind: "line", points: vec![p, q] });
            p = q;
        }
    }
    Ok(segs)
}
/// The two-arc step in its own plane's `(across, along)`.
fn sbend_flat(r: N, travel: N, jog: N) -> Result<Vec<Leg>> {
    let (th, s) = sbend_solve(r, travel, jog)?;
    let r = r.f();
    let c1 = [r, 0.];
    let e1 = [c1[0] - r * num::cos(th), c1[1] + r * num::sin(th)];
    let m1 = [c1[0] - r * num::cos(th / 2.), c1[1] + r * num::sin(th / 2.)];
    let e2 = [e1[0] + s * num::sin(th), e1[1] + s * num::cos(th)];
    let c2 = [e2[0] - r * num::cos(th), e2[1] + r * num::sin(th)];
    let e3 = [c2[0] + r, c2[1]];
    let ba = (e2[0] - c2[0]) + (e3[0] - c2[0]);
    let bz = (e2[1] - c2[1]) + (e3[1] - c2[1]);
    let bl = num::hypot2(ba, bz);
    let mut segs = vec![Leg { kind: "arc", points: vec![[0., 0.], m1, e1] }];
    if s > 1e-9 {
        segs.push(Leg { kind: "line", points: vec![e1, e2] });
    }
    segs.push(Leg { kind: "arc", points: vec![e2, [c2[0] + fdiv(r * ba, bl)?, c2[1] + fdiv(r * bz, bl)?], e3] });
    Ok(segs)
}

// ---------------------------------------------------------------------------------------------
// What `fixed_returns` answers.

/// A pump tee's ports, in the enclosure frame.
struct TeePorts {
    centre: V3,
    branch: (V3, V3),
    upper: (V3, V3),
    lower: (V3, V3),
}
fn port_pair(v: &Val) -> Result<(V3, V3)> {
    Ok((unpack3(&py::at(v, "point")?)?, unpack3(&py::at(v, "axis")?)?))
}
impl TeePorts {
    fn of(v: &Val) -> Result<TeePorts> {
        let v = py::snapshot(v)?;
        Ok(TeePorts {
            centre: unpack3(&py::at(&v, "centre")?)?,
            branch: port_pair(&py::at(&v, "branch")?)?,
            upper: port_pair(&py::at(&v, "upper")?)?,
            lower: port_pair(&py::at(&v, "lower")?)?,
        })
    }
}

/// One centreline segment carried into the authoring frame, its other entries as they were.
struct Seg(Vec<(Val, Val)>);
impl Seg {
    fn get(&self, key: &str) -> Result<&Val> {
        self.0.iter().find(|(k, _)| matches!(k, Val::Str(t) if t == key)).map(|(_, v)| v).ok_or_else(|| missing(key))
    }
    fn val(&self) -> Val {
        Val::dict(self.0.clone())
    }
}
/// `authoring_point` of a caller's point.
fn auth_pt_val(v: &Val) -> Result<Val> {
    let r = py::unpack(v, 3)?;
    Ok(Val::Tuple(vec![neg(&r[0])?, (N::of(&r[2])? - N::fl(WORLD_LIFT)).val(), (N::of(&r[1])? - N::fl(PACK_ORIGIN_Y)).val()]))
}
fn enc_pt_val(v: &Val) -> Result<Val> {
    let r = py::unpack(v, 3)?;
    Ok(Val::Tuple(vec![neg(&r[0])?, (N::of(&r[2])? + N::fl(PACK_ORIGIN_Y)).val(), (N::of(&r[1])? + N::fl(WORLD_LIFT)).val()]))
}
/// `authoring_axis` / `enclosure_axis` of a caller's axis.
fn swap_axis_val(v: &Val) -> Result<Val> {
    let r = py::unpack(v, 3)?;
    Ok(Val::Tuple(vec![neg(&r[0])?, r[2].clone(), r[1].clone()]))
}
/// `_authored(segment)`.
fn authored(segment: &Val) -> Result<Seg> {
    let mut rows = Vec::new();
    for key in segment.iter()? {
        let value = segment.get(key.clone())?;
        let name = if let Val::Str(t) = &key { t.as_str() } else { "" };
        let value = match name {
            "start_mm" | "end_mm" | "midpoint_mm" => auth_pt_val(&value)?,
            "start_tangent" | "end_tangent" => swap_axis_val(&value)?,
            _ => value,
        };
        rows.push((key, value));
    }
    Ok(Seg(rows))
}
/// `_segment_numbers(segment)`.
fn segment_numbers(seg: &Seg) -> Result<Val> {
    let kind = seg.get("kind")?.clone();
    let points = if interop::eq(&kind, &s("arc"))? {
        vec![seg.get("start_mm")?.clone(), seg.get("midpoint_mm")?.clone(), seg.get("end_mm")?.clone()]
    } else {
        vec![seg.get("start_mm")?.clone(), seg.get("end_mm")?.clone()]
    };
    Ok(py::dict([("kind", kind), ("points", Val::list(points))]))
}

/// One stem elbow of a lower return.
struct Elbow {
    crossing: V3,
    socket: V3,
    stem: N,
    showing: Val,
}
/// What `fixed_returns.station` gives one pump tee: its lower return.
struct Station {
    tube: Vec<Seg>,
    exposed: Val,
    cut: Val,
    elbows: Vec<Elbow>,
}
impl Station {
    fn of(v: &Val) -> Result<Station> {
        let v = py::snapshot(v)?;
        let ret = py::at(&v, "return")?;
        let tube = py::at(&ret, "tube")?.iter()?.iter().map(authored).collect::<Result<Vec<_>>>()?;
        let elbows = py::at(&ret, "elbows")?
            .iter()?
            .iter()
            .map(|e| {
                Ok(Elbow {
                    crossing: unpack3(&py::at(e, "crossing")?)?,
                    socket: unpack3(&py::at(e, "socket")?)?,
                    stem: N::of(&py::at(e, "stem")?)?,
                    showing: py::at(e, "showing")?,
                })
            })
            .collect::<Result<Vec<_>>>()?;
        Ok(Station { tube, exposed: py::at(&ret, "exposed_mm")?, cut: py::at(&ret, "cut_mm")?, elbows })
    }
}

/// The stem elbow's provider figures `numbers` places its stems by.
struct Kit {
    linear: Val,
    white: Val,
    ratio: Val,
    hub_back_reach: N,
    stem_od: N,
    profile: Vec<(N, N)>,
}

struct Mouth {
    cid: &'static str,
    p: &'static str,
    what: &'static str,
    at: V3,
    axis: V3,
}
impl Mouth {
    fn val(&self) -> Val {
        Val::Tuple(vec![s(self.cid), s(self.p), s(self.what), tup(self.at), tup(self.axis)])
    }
}

/// What `_write_readme` reads off `report`'s answer.
struct ReportData {
    bb: [N; 6],
    reach: [N; 6],
    bad: usize,
    made: Vec<(Val, N)>,
    mirror: Vec<(N, N)>,
}
fn lens(e: &[N; 6]) -> [N; 3] {
    [e[3] - e[0], e[4] - e[1], e[5] - e[2]]
}
/// `Extents.escape`: the shortest side and its axis.
fn escape(e: &[N; 6]) -> (&'static str, N) {
    let d = lens(e);
    let mut i = 0;
    for k in 1..3 {
        if d[k].f() < d[i].f() {
            i = k;
        }
    }
    (["x", "y", "z"][i], d[i])
}
/// `str(Extents)` of its six fields in field order.
fn extents_text(f: &[Val]) -> Result<String> {
    Ok(format!(
        "x[{},{}] y[{},{}] z[{},{}]",
        fmtv(&f[0], "8.2f")?,
        fmtv(&f[3], "8.2f")?,
        fmtv(&f[1], "8.2f")?,
        fmtv(&f[4], "8.2f")?,
        fmtv(&f[2], "8.2f")?,
        fmtv(&f[5], "8.2f")?
    ))
}
const EXTENT_FIELDS: [&str; 6] = ["xmin", "ymin", "zmin", "xmax", "ymax", "zmax"];
fn extents_fields(v: &Val) -> Result<Vec<Val>> {
    EXTENT_FIELDS.iter().map(|f| v.attr(f)).collect()
}
fn six(vals: &[Val]) -> Result<[N; 6]> {
    ensure!(vals.len() == 6, "an extent has six fields, got {}", vals.len());
    Ok([N::of(&vals[0])?, N::of(&vals[1])?, N::of(&vals[2])?, N::of(&vals[3])?, N::of(&vals[4])?, N::of(&vals[5])?])
}
/// A frozenset of the values, by equality.
fn set_of(values: Vec<Val>) -> Result<Vec<Val>> {
    let mut out: Vec<Val> = Vec::new();
    for v in values {
        let mut held = false;
        for u in &out {
            if interop::eq(u, &v)? {
                held = true;
                break;
            }
        }
        if !held {
            out.push(v);
        }
    }
    Ok(out)
}
fn set_eq(a: &[Val], b: &[Val]) -> Result<bool> {
    if a.len() != b.len() {
        return Ok(false);
    }
    for x in a {
        let mut held = false;
        for y in b {
            if interop::eq(x, y)? {
                held = true;
                break;
            }
        }
        if !held {
            return Ok(false);
        }
    }
    Ok(true)
}

// ---------------------------------------------------------------------------------------------
// The module's typed state.

/// The study's numbers: provider constants and what the module derives from them.
struct K {
    valve_len: N,
    valve_pitch: N,
    valve_port_z: N,
    tee_run: N,
    tee_branch: N,
    tube_d: N,
    min_bend: N,
    barb_pitch: N,
    barb_inset: N,
    inner_limb_drop: N,
    fore_stub_gap: N,
    tip_from_fore: N,
    pump_stub_projection: N,
    barb_plate_berth: N,
    pump_barb_z: N,
    pump_y: N,
    barb_standoff: N,
    limb_pitch: N,
    inner_x: N,
    pump_dx: N,
    outer_x: N,
    outer_aft_inset: N,
    limb_step: N,
    barb_lead: N,
    deck_z: N,
    hinge_y: N,
    deck_sep: N,
    hinge_z: N,
    upper_z: N,
    bend_y: N,
    carrier_connected: N,
    pump_station_lead: N,
    pump_station_drop: N,
    kp_cx: N,
    kp_head_front_z: N,
    kp_body_y_face: N,
    outlet_y: N,
    quarter_len: N,
}

pub struct State {
    ns: Ns,
    routing: Val,
    returns: Val,
    enc_if: Val,
    stock: Val,
    here: PathBuf,
    hw: PathBuf,
    tee_step: PathBuf,
    elbow_step: PathBuf,
    kamoer_step: PathBuf,
    c_coil: Val,
    c_valve: Val,
    c_tee: Val,
    c_head: Val,
    c_boss: Val,
    c_motor: Val,
    k: K,
    bodies: Vec<Body>,
    shift: Vec<(&'static str, V3)>,
    types: OnceCell<(Val, Val)>,
    fore_deck: OnceCell<N>,
    tee_axis_y: OnceCell<N>,
    tube_id: OnceCell<Val>,
    kit: OnceCell<Kit>,
    tee_ports: RefCell<Vec<(&'static str, Rc<TeePorts>)>>,
    plumbing: RefCell<Option<(Val, Rc<Vec<Station>>)>>,
    s_bends: RefCell<Vec<([(bool, u64); 6], Rc<Vec<Seg>>)>>,
    runs: OnceCell<Vec<(&'static str, V3, V3)>>,
    fore_stubs: OnceCell<Vec<(&'static str, V3, V3)>>,
    fore_stub_exposed: OnceCell<N>,
    mouths: OnceCell<Vec<Mouth>>,
}

fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

impl State {
    fn body(&self, name: &str) -> Result<&Body> {
        self.bodies.iter().find(|b| b.name == name).ok_or_else(|| missing(name))
    }
    fn shift_of(&self, name: &str) -> Option<V3> {
        self.shift.iter().find(|r| r.0 == name).map(|r| r.1)
    }
    fn static_junction(&self, name: &str) -> Result<&'static str> {
        Ok(JUNCTIONS[junction_index(name)?])
    }
    fn quarters(&self) -> [(i64, N, N); 2] {
        [(3, -self.k.inner_x, self.k.upper_z), (5, self.k.inner_x, self.k.upper_z)]
    }
    fn types(&self, rt: &Rt) -> Result<&(Val, Val)> {
        if self.types.get().is_none() {
            let types = (rt.python_type(MODULE, "Extents")?, rt.python_type(MODULE, "Clash")?);
            let _ = self.types.set(types);
        }
        Ok(self.types.get().unwrap())
    }

    // Moves.
    fn fold_pt(&self, p: V3) -> V3 {
        [p[0], N::fl(2.) * self.k.hinge_y - p[1], N::fl(2.) * self.k.hinge_z - p[2]]
    }
    fn bend_pt(&self, p: V3, z0: N) -> V3 {
        let k = &self.k;
        let dy = p[1] - k.bend_y;
        let dz = p[2] - (z0 + k.min_bend);
        [p[0], k.bend_y - dz, z0 + k.min_bend + dy]
    }
    fn fold_pt_val(&self, p: &Val) -> Result<Val> {
        let r = items3(p)?;
        let k = &self.k;
        Ok(Val::Tuple(vec![
            r[0].clone(),
            (N::fl(2.) * k.hinge_y - N::of(&r[1])?).val(),
            (N::fl(2.) * k.hinge_z - N::of(&r[2])?).val(),
        ]))
    }
    fn bend_pt_val(&self, p: &Val, z0: N) -> Result<Val> {
        let r = items3(p)?;
        let k = &self.k;
        let dy = N::of(&r[1])? - k.bend_y;
        let dz = N::of(&r[2])? - (z0 + k.min_bend);
        Ok(Val::Tuple(vec![r[0].clone(), (k.bend_y - dz).val(), (z0 + k.min_bend + dy).val()]))
    }

    // Stations.
    fn barb_station(&self, tee: &str) -> Result<V3> {
        let (_, sign, side) = BARB_OF.iter().find(|r| r.0 == tee).ok_or_else(|| missing(tee))?;
        let px = if *sign < 0. { -self.k.pump_dx } else { self.k.pump_dx };
        Ok([px + div(N::int(*side) * self.k.barb_pitch, N::fl(2.))?, self.k.pump_y, self.k.pump_barb_z])
    }
    fn stub_tip(&self, name: &str) -> Result<V3> {
        let start = self.barb_station(name)?;
        Ok([start[0], start[1], start[2] + self.k.pump_stub_projection])
    }
    /// The collet plate's fore face, from the prepared pump tube's seated tip.
    fn pump_wall_fore_y(&self) -> Result<N> {
        Ok(enc_pt(self.stub_tip(JUNCTIONS[0])?)[1] - self.k.tip_from_fore)
    }
    fn fore_deck_aft_shift(&self) -> Result<N> {
        if let Some(v) = self.fore_deck.get() {
            return Ok(*v);
        }
        let axis = py::call(&self.returns.attr("fore_valve_axis_y")?, vec![self.pump_wall_fore_y()?.val()])?;
        let v = N::of(&axis)? - (self.k.deck_z + N::fl(PACK_ORIGIN_Y));
        let _ = self.fore_deck.set(v);
        Ok(v)
    }
    fn fixed_aft_shift(&self, name: &str) -> Result<N> {
        if is_junction(name) {
            return Ok(N::fl(FIXED_TEE_AFT_SHIFT));
        }
        if FORE_VALVES.contains(&name) { self.fore_deck_aft_shift() } else { Ok(N::fl(AFT_DECK_AFT_SHIFT)) }
    }
    fn tee_axis_y(&self) -> Result<N> {
        if let Some(v) = self.tee_axis_y.get() {
            return Ok(*v);
        }
        let v = N::of(&py::call(&self.returns.attr("tee_axis_y")?, vec![self.pump_wall_fore_y()?.val()])?)?;
        let _ = self.tee_axis_y.set(v);
        Ok(v)
    }
    fn tube_id(&self) -> Result<Val> {
        if let Some(v) = self.tube_id.get() {
            return Ok(v.clone());
        }
        let v = self.returns.attr("TUBE_ID")?;
        let _ = self.tube_id.set(v.clone());
        Ok(v)
    }

    // Ports.
    /// `_returns.tee_ports` for one pump tee, as the provider answers it.
    fn tee_ports_val(&self, name: &str) -> Result<Val> {
        let e = enc_pt(self.barb_station(name)?);
        py::call(&self.returns.attr("tee_ports")?, vec![self.pump_wall_fore_y()?.val(), e[0].val(), e[2].val()])
    }
    fn tee_ports(&self, name: &str) -> Result<Rc<TeePorts>> {
        let name = self.static_junction(name)?;
        if let Some((_, held)) = self.tee_ports.borrow().iter().find(|r| r.0 == name) {
            return Ok(held.clone());
        }
        let ports = Rc::new(TeePorts::of(&self.tee_ports_val(name)?)?);
        self.tee_ports.borrow_mut().push((name, ports.clone()));
        Ok(ports)
    }
    /// A point and a direction through the moves this body rides: the fold, the quarter turn,
    /// its pack shift, the carrier datum and the fixed aft shift.
    fn posed(&self, name: &str, p: V3, d: V3) -> Result<(V3, V3)> {
        let b = self.body(name)?;
        let (mut p, mut d) = (p, d);
        if b.fold {
            (p, d) = (self.fold_pt(p), fold_dir(d));
        }
        if is_bent(name) {
            (p, d) = (self.bend_pt(p, self.k.upper_z), bend_dir(d));
        }
        if let Some(sh) = self.shift_of(name) {
            p = add3(p, sh);
        }
        if is_junction(name) {
            p = [p[0], p[1], p[2] + N::fl(CARRIER_DATUM_SHIFT) + self.k.carrier_connected];
        }
        p = [p[0], p[1], p[2] + self.fixed_aft_shift(name)?];
        Ok((p, d))
    }
    fn end_pose(&self, name: &str, front: bool) -> Result<(V3, V3)> {
        let b = self.body(name)?;
        let y = if front { b.front } else { b.back };
        let d = if front { [0., -1., 0.] } else { [0., 1., 0.] };
        self.posed(name, [b.x, y, self.k.deck_z], fv3(d))
    }
    fn port(&self, name: &str, front: bool) -> Result<V3> {
        if is_junction(name) {
            let tp = self.tee_ports(name)?;
            return Ok(auth_pt(if front { tp.lower.0 } else { tp.upper.0 }));
        }
        Ok(self.end_pose(name, front)?.0)
    }
    fn port_axis(&self, name: &str, front: bool) -> Result<V3> {
        if is_junction(name) {
            let tp = self.tee_ports(name)?;
            return Ok(swap_axis(if front { tp.lower.1 } else { tp.upper.1 }));
        }
        Ok(self.end_pose(name, front)?.1)
    }
    fn branch_port(&self, name: &str) -> Result<(V3, V3)> {
        if is_junction(name) {
            let tp = self.tee_ports(name)?;
            return Ok((auth_pt(tp.branch.0), swap_axis(tp.branch.1)));
        }
        let b = self.body(name)?;
        let Arg::Branch(d) = b.arg else { bail!("value is not subscriptable") };
        let d = fv3(d);
        let k = &self.k;
        self.posed(name, [b.x + d[0] * k.tee_branch, b.y, k.deck_z + d[2] * k.tee_branch], d)
    }

    // The pump tees' plumbing.
    fn stations_of(&self, cache: &Val) -> Result<Vec<Station>> {
        JUNCTIONS.iter().map(|name| Station::of(&cache.get(s(*name))?)).collect()
    }
    /// `pump_plumbing()`: the stations `_plumbing_cache` holds, made once.
    fn plumbing(&self) -> Result<Rc<Vec<Station>>> {
        let cached = self.ns.get("_plumbing_cache")?;
        if !matches!(cached, Val::None) {
            if let Some((held, stations)) = &*self.plumbing.borrow() {
                if same(held, &cached)? {
                    return Ok(stations.clone());
                }
            }
            let stations = Rc::new(self.stations_of(&cached)?);
            *self.plumbing.borrow_mut() = Some((cached, stations.clone()));
            return Ok(stations);
        }
        let out = Val::dict(vec![]);
        let fore = self.pump_wall_fore_y()?;
        for (name, upper_valve, return_valve) in PUMP_VALVES {
            let e = enc_pt(self.barb_station(name)?);
            let upper = py::dict([
                ("point", tup(enc_pt(self.port(upper_valve, true)?))),
                ("axis", tup(swap_axis(self.port_axis(upper_valve, true)?))),
            ]);
            let lower = py::dict([
                ("point", tup(enc_pt(self.port(return_valve, false)?))),
                ("axis", tup(swap_axis(self.port_axis(return_valve, false)?))),
            ]);
            let station = py::call(&self.returns.attr("station")?, vec![fore.val(), e[0].val(), e[2].val(), upper, lower])?;
            out.set(s(name), station)?;
        }
        self.ns.set("_plumbing_cache", out.clone())?;
        let stations = Rc::new(self.stations_of(&out)?);
        *self.plumbing.borrow_mut() = Some((out, stations.clone()));
        Ok(stations)
    }
    fn junction_at_author_x(&self, x: N) -> Result<&'static str> {
        let mut best: Option<(&'static str, f64)> = None;
        for name in JUNCTIONS {
            let key = (self.body(name)?.x - x).abs().f();
            if best.is_none_or(|(_, b)| key < b) {
                best = Some((name, key));
            }
        }
        Ok(best.map(|b| b.0).unwrap())
    }
    fn return_exposed(&self, x: N) -> Result<Val> {
        let stations = self.plumbing()?;
        Ok(stations[junction_index(self.junction_at_author_x(x)?)?].exposed.clone())
    }
    fn return_cut(&self, x: N) -> Result<Val> {
        let name = self.junction_at_author_x(x)?;
        let (_, junction) = LOWER_CONNECTIONS.iter().find(|(_, j)| *j == name).context("StopIteration")?;
        Ok(self.plumbing()?[junction_index(junction)?].cut.clone())
    }
    /// The upper tube from a tee's run collet at `a` into its fore valve at `b`, bent by
    /// `fixed_returns.s_bend` in the enclosure frame and carried back.
    fn fore_segments(&self, a: V3, b: V3) -> Result<Rc<Vec<Seg>>> {
        let (ea, eb) = (enc_pt(a), enc_pt(b));
        let key = [ea[0], ea[1], ea[2], eb[0], eb[1], eb[2]].map(|n| (n.is_int(), n.f().to_bits()));
        if let Some((_, held)) = self.s_bends.borrow().iter().find(|r| r.0 == key) {
            return Ok(held.clone());
        }
        let bent = py::snapshot(&py::call(&self.returns.attr("s_bend")?, vec![tup(ea), tup(eb)])?)?;
        let segs = Rc::new(bent.iter()?.iter().map(authored).collect::<Result<Vec<_>>>()?);
        self.s_bends.borrow_mut().push((key, segs.clone()));
        Ok(segs)
    }
    fn fore_stub_length(&self, a: V3, b: V3) -> Result<N> {
        let mut total = N::int(0);
        for seg in self.fore_segments(a, b)?.iter() {
            total = total + N::of(seg.get("length_mm")?)?;
        }
        Ok(total)
    }

    // Runs and stubs.
    fn make_runs(&self) -> Result<Vec<(&'static str, V3, V3)>> {
        let mut out = vec![("crossbar", self.branch_port("Y-A")?.0, self.branch_port("Y-B")?.0)];
        for (name, _, _) in BARB_OF {
            out.push((name, self.barb_station(name)?, self.stub_tip(name)?));
        }
        Ok(out)
    }
    fn runs(&self) -> Result<&Vec<(&'static str, V3, V3)>> {
        if self.runs.get().is_none() {
            let runs = self.make_runs()?;
            let _ = self.runs.set(runs);
        }
        Ok(self.runs.get().unwrap())
    }
    fn make_fore_stubs(&self) -> Result<Vec<(&'static str, V3, V3)>> {
        FORE_STUB_ROWS.iter().map(|(key, tee, valve)| Ok((*key, self.port(tee, false)?, self.port(valve, true)?))).collect()
    }
    fn fore_stubs(&self) -> Result<&Vec<(&'static str, V3, V3)>> {
        if self.fore_stubs.get().is_none() {
            let stubs = self.make_fore_stubs()?;
            let _ = self.fore_stubs.set(stubs);
        }
        Ok(self.fore_stubs.get().unwrap())
    }
    fn fore_stub_exposed(&self) -> Result<N> {
        if let Some(v) = self.fore_stub_exposed.get() {
            return Ok(*v);
        }
        let (_, a, b) = self.fore_stubs()?[0];
        let v = self.fore_stub_length(a, b)?;
        let _ = self.fore_stub_exposed.set(v);
        Ok(v)
    }
    fn mouths(&self) -> Result<&Vec<Mouth>> {
        if self.mouths.get().is_none() {
            let rows = MOUTH_ROWS
                .iter()
                .map(|(cid, p, what, body, end)| {
                    let front = *end == "front";
                    Ok(Mouth { cid, p, what, at: self.port(body, front)?, axis: self.port_axis(body, front)? })
                })
                .collect::<Result<Vec<_>>>()?;
            let _ = self.mouths.set(rows);
        }
        Ok(self.mouths.get().unwrap())
    }

    // The source steps.
    fn source_valve_shift(&self, name: &str) -> Result<(f64, f64)> {
        let spread = SOURCE_SPREAD.iter().find(|r| r.0 == name).map(|r| r.1).ok_or_else(|| missing(name))?;
        Ok((spread.copysign(self.body(name)?.x.f()), -SOURCE_JOG))
    }
    fn source_cross(&self, name: &str) -> Result<(f64, f64)> {
        let (x, y) = self.source_valve_shift(name)?;
        Ok((x, y - AFT_PACK_RISE))
    }
    fn source_offset(&self, name: &str) -> Result<(f64, f64)> {
        let c = self.source_cross(name)?;
        if hairpin_back(self.k.min_bend.f(), SOURCE_TRAVEL, num::hypot2(c.0, c.1))? <= 1e-9 {
            return Ok((0., 0.));
        }
        let t = num::radians(HAIRPIN_TILT);
        Ok(((HAIRPIN_OUT * num::cos(t)).copysign(self.body(name)?.x.f()), HAIRPIN_OUT * num::sin(t)))
    }
    fn step_cross(&self, name: &str) -> Result<(f64, f64)> {
        let (cross, off) = (self.source_cross(name)?, self.source_offset(name)?);
        Ok((cross.0 - off.0, cross.1 - off.1))
    }
    fn source_step(&self, name: &str) -> Result<(f64, f64, f64)> {
        let c = self.step_cross(name)?;
        let jog = num::hypot2(c.0, c.1);
        let r = self.k.min_bend;
        let back = hairpin_back(r.f(), SOURCE_TRAVEL, jog)?;
        let (th, s) = sbend_solve(r, N::fl(SOURCE_TRAVEL + back), N::fl(jog))?;
        let mut length = 2. * r.f() * th + s;
        if back > 1e-9 {
            let off = self.source_offset(name)?;
            length += 2. * PI * r.f() + num::hypot(&[off.0, off.1, back]);
        }
        Ok((th, s, length))
    }
    fn hairpins_drawn(&self) -> Result<i64> {
        let mut n = 0;
        for (_, v) in SBENDS {
            let c = self.step_cross(v)?;
            if hairpin_back(self.k.min_bend.f(), SOURCE_TRAVEL, num::hypot2(c.0, c.1))? > 1e-9 {
                n += 1;
            }
        }
        Ok(n)
    }
    /// The source run's authored arcs and lines, laid from `start` along its lanes.
    fn source_segments(&self, name: &str, start: V3, travel: N) -> Result<Val> {
        let off = self.source_offset(name)?;
        let cross = self.step_cross(name)?;
        let jog = num::hypot2(cross.0, cross.1);
        let r = self.k.min_bend;
        let back = hairpin_back(r.f(), travel.f(), jog)?;
        let mut lanes = Vec::new();
        if back > 1e-9 {
            lanes.push((off, hairpin_flat(r.f(), num::hypot2(off.0, off.1), N::fl(back))?));
        }
        lanes.push((cross, sbend_flat(r, travel + N::fl(back), N::fl(jog))?));
        let mut origin = start;
        let mut out: Vec<(&'static str, Vec<V3>)> = Vec::new();
        for (axis, legs) in lanes {
            let length = num::hypot2(axis.0, axis.1);
            let direction = [fdiv(axis.0, length)?, fdiv(axis.1, length)?, 0.];
            for leg in legs {
                let points = leg
                    .points
                    .iter()
                    .map(|p| add3(add3(origin, direction.map(|v| N::fl(v * p[0]))), fv3([0., 0., p[1]])))
                    .collect();
                out.push((leg.kind, points));
            }
            origin = *out.last().and_then(|(_, points)| points.last()).context("IndexError")?;
        }
        Ok(Val::list(
            out.into_iter()
                .map(|(kind, points)| py::dict([("kind", s(kind)), ("points", Val::list(points.into_iter().map(tup).collect()))]))
                .collect(),
        ))
    }
    fn turns_meet(&self) -> Result<Vec<(i64, N)>> {
        let lands = [(3, self.port("V-A", false)?), (5, self.port("V-B", false)?)];
        let k = &self.k;
        let mut out = Vec::new();
        for (cid, x, z0) in self.quarters() {
            let mut end = [x, k.bend_y + k.min_bend - k.inner_limb_drop + N::fl(AFT_PACK_RISE), z0 + k.min_bend + N::fl(AFT_DECK_AFT_SHIFT)];
            if let Some((_, v)) = SBENDS.iter().find(|r| r.0 == cid) {
                let (dx, dy) = self.source_cross(v)?;
                end = [end[0] + N::fl(dx), end[1] + N::fl(dy), end[2] + N::fl(SOURCE_TRAVEL)];
            }
            let land = lands.iter().find(|l| l.0 == cid).map(|l| l.1).context("missing land")?;
            out.push((cid, dist(end, land)));
        }
        Ok(out)
    }
    fn mirror_off(&self) -> Result<Vec<(&'static str, &'static str, N, N)>> {
        let mut out = Vec::new();
        for (a, b) in TWINS {
            let (pa, pb) = (self.body(a)?, self.body(b)?);
            out.push((a, b, (pa.x + pb.x).abs(), (pa.y - pb.y).abs()));
        }
        out.push(("pump-a", "pump-b", (-self.k.pump_dx + self.k.pump_dx).abs(), N::fl(0.)));
        Ok(out)
    }

    // The payload.
    fn kit(&self, rt: &Rt) -> Result<&Kit> {
        if self.kit.get().is_none() {
            let linear = rt.member("_materials", "linear")?;
            let white = rt.member("_materials", "M_NEOFIT_WHITE_ACETAL")?;
            let stem = rt.import("neofit_stem_elbow")?;
            let ratio = rt.member("_payload_rules", "LINEAR_DEFLECTION_RATIO")?;
            let hub_back_reach = N::of(&stem.attr("HUB_BACK_REACH")?)?;
            let stem_od = N::of(&stem.attr("STEM_OD")?)?;
            let profile = py::snapshot(&stem.attr("PARAMETERS")?.get(s("profiles"))?.get(s("stem_x"))?)?;
            let profile = profile
                .iter()?
                .iter()
                .map(|row| {
                    let pr = py::unpack(row, 2)?;
                    Ok((N::of(&pr[0])?, N::of(&pr[1])?))
                })
                .collect::<Result<Vec<_>>>()?;
            let _ = self.kit.set(Kit { linear, white, ratio, hub_back_reach, stem_od, profile });
        }
        Ok(self.kit.get().unwrap())
    }
    fn reference(&self, kit: &Kit, name: String, source: &str, groups: Val, matrix: Val, color: &Val) -> Result<Val> {
        Ok(py::dict([
            ("name", s(name)),
            ("kind", s("reference")),
            ("source", s(source)),
            ("groups", groups),
            ("transform", matrix),
            ("color", py::call(&kit.linear, vec![color.clone()])?),
        ]))
    }
    fn tube(&self, kit: &Kit, name: String, segments: Val, normal: Val, color: &Val, inside: Val) -> Result<Val> {
        Ok(py::dict([
            ("name", s(name)),
            ("kind", s("tube")),
            ("segments", segments),
            ("normal", normal),
            ("od", self.k.tube_d.val()),
            ("id", inside),
            ("color", py::call(&kit.linear, vec![color.clone()])?),
        ]))
    }
    fn tube_color(&self, cid: &str) -> Result<Val> {
        py::call(&self.routing.attr("tube_color")?, vec![s(cid)])
    }
    /// The stem elbow's stem and root envelopes along its own axis for a stem `keep` long.
    fn stem_rows(kit: &Kit, keep: N) -> Result<(Val, Val)> {
        let profile = &kit.profile;
        let radius = div(kit.stem_od, N::fl(2.))?;
        let empty = || anyhow!("empty min/max");
        let straight: Vec<N> = profile.iter().filter(|(_, r)| (*r - radius).abs().f() < 1e-6).map(|(p, _)| *p).collect();
        let first = profile.first().context("an empty stem profile")?;
        let least = straight.iter().copied().reduce(nmin).ok_or_else(empty)?;
        let most = straight.iter().copied().reduce(nmax).ok_or_else(empty)?;
        let tip = least - first.0;
        let root_end =
            profile.iter().filter(|(p, r)| p.f() < 0. && r.f() > radius.f()).map(|(p, _)| *p).reduce(nmax).ok_or_else(empty)?;
        let root_allowance = root_end - most;
        let root_radius = profile.iter().filter(|(p, _)| p.f() <= root_end.f()).map(|(_, r)| *r).reduce(nmax).ok_or_else(empty)?;
        let (lo, hi) = (nmax(-keep, least), most);
        let c = N::fl(0.01);
        let stem = Val::list(vec![(lo - tip - c).val(), (hi + tip + c).val(), (radius + c).val()]);
        let root = Val::list(vec![(hi - c).val(), (hi + root_allowance + c).val(), (root_radius + c).val()]);
        Ok((stem, root))
    }
    /// Fine reference parts, installed frames and authored tube centrelines for Rust.
    fn numbers(&self, rt: &Rt, prepare_sources: bool) -> Result<Val> {
        let rust_part = rt.import("_rust_part")?;
        let kit = self.kit(rt)?;
        let k = &self.k;
        let sources = Val::dict(vec![]);
        if prepare_sources {
            let rows = [
                ("valve", self.hw.join("reference/beduan-solenoid/beduan-solenoid.step")),
                ("tee", self.tee_step.clone()),
                ("elbow", self.elbow_step.clone()),
                ("pump", self.kamoer_step.clone()),
                ("stem", self.hw.join("reference/neofit-stem-elbow/neofit-stem-elbow.step")),
            ];
            for (key, path) in rows {
                sources.set(s(key), py::call(&rust_part.attr("step")?, vec![Val::Path(path)])?)?;
            }
        }
        let mut bodies = Vec::new();
        let mut stems = Vec::new();
        for b in &self.bodies {
            if is_junction(b.name) {
                continue;
            }
            let carry = |p: V3| -> Result<V3> {
                let mut p = p;
                if b.fold {
                    p = self.fold_pt(p);
                }
                if is_bent(b.name) {
                    p = self.bend_pt(p, k.upper_z);
                }
                if let Some(sh) = self.shift_of(b.name) {
                    p = add3(p, sh);
                }
                Ok(add3(p, [N::fl(0.), N::fl(0.), self.fixed_aft_shift(b.name)?]))
            };
            let lower = b.name.to_lowercase();
            match b.arg {
                Arg::Flow(flow) => {
                    let (x_dir, z_dir) = valve_dirs(flow);
                    let frame = matrix([b.x, b.y, k.deck_z - k.valve_port_z], x_dir, z_dir, &carry)?;
                    let body = Val::list(vec![py::dict([("names", names(&["body", "collets"])), ("union", Val::Bool(true))])]);
                    bodies.push(self.reference(kit, format!("valve-{lower}"), "valve", body, frame.clone(), &self.c_valve)?);
                    let coil = Val::list(vec![
                        py::dict([("names", names(&["winding", "yoke", "screw-heads"])), ("union", Val::Bool(true))]),
                        py::dict([("names", names(&["terminals"]))]),
                    ]);
                    bodies.push(self.reference(kit, format!("coil-{lower}"), "valve", coil, frame, &self.c_coil)?);
                }
                Arg::Branch(branch) => {
                    let (x_dir, z_dir) = tee_dirs(branch);
                    let frame = matrix([b.x, b.y, k.deck_z], x_dir, z_dir, &carry)?;
                    bodies.push(self.reference(kit, format!("tee-{lower}"), "tee", Val::list(vec![Val::dict(vec![])]), frame, &self.c_tee)?);
                }
            }
        }
        for (pname, px) in [("pump-a", -k.pump_dx), ("pump-b", k.pump_dx)] {
            let at = [px + k.kp_cx, -k.barb_inset + k.pump_y - k.kp_head_front_z, k.pump_barb_z - k.kp_body_y_face];
            let row = |a: f64, b: f64, c: f64, d: N| Val::list(vec![Val::Float(a), Val::Float(b), Val::Float(c), d.val()]);
            let frame = Val::list(vec![row(-1., 0., 0., at[0]), row(0., 0., 1., at[1]), row(0., 1., 0., at[2])]);
            for (suffix, part, color) in [("head", "head", &self.c_head), ("boss", "rotor_housing", &self.c_boss), ("motor", "motor_body", &self.c_motor)] {
                let groups = Val::list(vec![py::dict([("names", names(&[part]))])]);
                bodies.push(self.reference(kit, format!("{pname}-{suffix}"), "pump", groups, frame.clone(), color)?);
            }
        }
        let (runs, stubs) = (self.runs()?, self.fore_stubs()?);
        for (cid, _, _, how) in SEGMENTS {
            let color = self.tube_color(&format!("fluid-{cid}"))?;
            if let Some((_, a, b)) = runs.iter().find(|r| r.0 == how).filter(|(_, a, b)| dist(*a, *b).f() > 1e-9) {
                let segments = Val::list(vec![py::dict([("kind", s("line")), ("points", Val::list(vec![tup(*a), tup(*b)]))])]);
                bodies.push(self.tube(kit, format!("tube-fluid-{cid}"), segments, tup(sub3(*b, *a)), &color, Val::None)?);
            } else if let Some((_, a, b)) = stubs.iter().find(|r| r.0 == how) {
                let segs = self.fore_segments(*a, *b)?;
                let numbers = Val::list(segs.iter().map(segment_numbers).collect::<Result<_>>()?);
                let normal = segs.first().context("IndexError")?.get("start_tangent")?.clone();
                bodies.push(self.tube(kit, format!("tube-fluid-{cid}"), numbers, normal, &color, self.tube_id()?)?);
            }
        }
        let stations = self.plumbing()?;
        for (cid, name) in LOWER_CONNECTIONS {
            let segs = &stations[junction_index(name)?].tube;
            let numbers = Val::list(segs.iter().map(segment_numbers).collect::<Result<_>>()?);
            let normal = segs.first().context("IndexError")?.get("start_tangent")?.clone();
            let color = self.tube_color(&format!("fluid-{cid}"))?;
            bodies.push(self.tube(kit, format!("tube-fluid-{cid}"), numbers, normal, &color, self.tube_id()?)?);
        }
        let authoring = |p: V3| -> Result<V3> { Ok(auth_pt(p)) };
        for (i, name) in JUNCTIONS.iter().enumerate() {
            let e = enc_pt(self.barb_station(name)?);
            let frame = matrix([e[0], self.tee_axis_y()?, e[2]], fv3([-1., 0., 0.]), fv3([0., 0., 1.]), &authoring)?;
            bodies.push(self.reference(kit, body_name(name), "tee", Val::list(vec![Val::dict(vec![])]), frame, &self.c_tee)?);
            let station = &stations[i];
            let return_valve = PUMP_VALVES[i].2;
            for (host, row) in [(*name, &station.elbows[0]), (return_valve, &station.elbows[1])] {
                let [ux, uy, _] = row.socket;
                let frame = matrix(row.crossing, fv3([0., 0., -1.]), [uy, -ux, N::fl(0.)], &authoring)?;
                let keep = kit.hub_back_reach + row.stem;
                let cut = py::dict([
                    ("origin", Val::list(vec![(-keep - N::fl(40.)).val(), Val::Float(-20.), Val::Float(-20.)])),
                    ("size", py::flist(&[40., 40., 40.])),
                ]);
                let label = format!("stem-elbow-{}", host.to_lowercase());
                let groups = Val::list(vec![
                    py::dict([("names", names(&["body_and_stem"])), ("cut_box", cut)]),
                    py::dict([("names", names(&["release_collet"]))]),
                ]);
                bodies.push(self.reference(kit, label.clone(), "stem", groups, frame.clone(), &kit.white)?);
                let (stem, root) = State::stem_rows(kit, keep)?;
                stems.push(py::dict([
                    ("elbow", s(label)),
                    ("host", s(body_name(host))),
                    ("transform", frame),
                    ("stem", stem),
                    ("root", root),
                ]));
            }
        }
        for (cid, x, z0) in self.quarters() {
            let shift = [N::fl(0.), -k.inner_limb_drop + N::fl(AFT_PACK_RISE), N::fl(AFT_DECK_AFT_SHIFT)];
            let r = k.min_bend;
            let kk = k.min_bend * N::fl(sqrt(0.5)?);
            let points = [[x, k.bend_y, z0], [x, k.bend_y + kk, z0 + r - kk], [x, k.bend_y + r, z0 + r]]
                .into_iter()
                .map(|p| tup(add3(p, shift)))
                .collect();
            let segments = Val::list(vec![py::dict([("kind", s("arc")), ("points", Val::list(points))])]);
            let color = self.tube_color(&format!("fluid-{cid}"))?;
            bodies.push(self.tube(kit, format!("turn-fluid-{cid}"), segments, py::ftuple(&[0., 1., 0.]), &color, Val::None)?);
        }
        for (cid, name) in SBENDS {
            let (_, x, z0) = self.quarters().into_iter().find(|q| q.0 == cid).context("missing quarter")?;
            let start = [x, k.bend_y + k.min_bend - k.inner_limb_drop + N::fl(AFT_PACK_RISE), z0 + k.min_bend + N::fl(AFT_DECK_AFT_SHIFT)];
            let segments = self.source_segments(name, start, N::fl(SOURCE_TRAVEL))?;
            let color = self.tube_color(&format!("fluid-{cid}"))?;
            bodies.push(self.tube(kit, format!("step-fluid-{cid}"), segments, py::ftuple(&[0., 0., 1.]), &color, Val::None)?);
        }
        for m in self.mouths()? {
            let tip = add3(m.at, m.axis.map(|v| v * k.min_bend));
            let segments = Val::list(vec![py::dict([("kind", s("line")), ("points", Val::list(vec![tup(m.at), tup(tip)]))])]);
            let color = self.tube_color(m.cid)?;
            bodies.push(self.tube(kit, format!("stub-{}", m.cid), segments, tup(m.axis), &color, Val::None)?);
        }
        Ok(py::dict([
            ("name", s("manifold-layout")),
            ("sources", sources),
            ("bodies", Val::list(bodies)),
            ("stems", Val::list(stems)),
            ("clash_floor", Val::Float(1.0)),
            ("presentation_ratio", kit.ratio.clone()),
        ]))
    }

    // The report.
    fn report(&self, rt: &Rt, measurements: &Val) -> Result<(Val, ReportData)> {
        let k = &self.k;
        let (extents, clash) = self.types(rt)?.clone();
        let m = py::snapshot(measurements)?;
        let (bb_vals, reach_vals) = (py::at(&m, "bb")?.iter()?, py::at(&m, "reach")?.iter()?);
        let bb = py::call(&extents, bb_vals.clone())?;
        let reach = py::call(&extents, reach_vals.clone())?;
        let (bbn, reachn) = (six(&bb_vals)?, six(&reach_vals)?);
        rt.print("\nlimbs (front → back, y at each body's centre)".into())?;
        for l in &LIMBS {
            let row = l
                .chain
                .iter()
                .map(|(n, _)| Ok(format!("{n}@{}", self.body(n)?.y.fmt("+.1f"))))
                .collect::<Result<Vec<_>>>()?
                .join("  ");
            let x = self.body(l.chain[0].0)?.x;
            rt.print(format!("  {}  x{}   {row}", l.limb, x.fmt("+7.2f")))?;
        }
        let mut made: Vec<(&'static str, N)> = self.runs()?.iter().map(|(name, a, b)| (*name, dist(*a, *b))).collect();
        let exposed = self.fore_stub_exposed()?;
        for (key, _, _) in FORE_STUB_ROWS {
            if let Some(row) = made.iter_mut().find(|r| r.0 == key) {
                row.1 = exposed;
            } else {
                made.push((key, exposed));
            }
        }
        rt.print(format!("\n{} connections", SEGMENTS.len()))?;
        let quarter = || format!("{} mm — one 90° turn at R{}", k.quarter_len.fmt(".2f"), k.min_bend.fmt("g"));
        for (cid, frm, to, how) in SEGMENTS {
            let note = if how == "spine" {
                let (_, name) = LOWER_CONNECTIONS.iter().find(|r| r.0 == cid).ok_or_else(|| anyhow!("missing key {cid}"))?;
                let line = &self.plumbing()?[junction_index(name)?];
                format!(
                    "{} mm free tube between two stem elbows, {} mm of stem below the valve",
                    fmtv(&line.exposed, ".3f")?,
                    fmtv(&line.elbows.get(1).context("IndexError")?.showing, ".3f")?
                )
            } else if how == "turn" {
                let mut note = quarter();
                if let Some((_, v)) = SBENDS.iter().find(|r| r.0 == cid) {
                    let (th, s, length) = self.source_step(v)?;
                    let c = self.step_cross(v)?;
                    let back = hairpin_back(k.min_bend.f(), SOURCE_TRAVEL, num::hypot2(c.0, c.1))?;
                    let lead = if back > 1e-9 {
                        let off = self.source_offset(v)?;
                        format!("a hairpin {} back and {} out, then ", num::fmt(back, ".2f"), num::fmt(num::hypot2(off.0, off.1), ".2f"))
                    } else {
                        String::new()
                    };
                    let cross = self.source_cross(v)?;
                    note = format!(
                        "{} mm — one 90° turn at R{}, then {lead}two of {}° with {} mm between: {} along and {} across",
                        num::fmt(k.quarter_len.f() + length, ".2f"),
                        k.min_bend.fmt("g"),
                        num::fmt(num::degrees(th), ".3f"),
                        num::fmt(s, ".2f"),
                        num::fmt(SOURCE_TRAVEL, "g"),
                        num::fmt(num::hypot2(cross.0, cross.1), ".2f")
                    );
                }
                note
            } else if FORE_STUB_ROWS.iter().any(|r| r.0 == how) {
                format!("{} mm upper tube, straight", exposed.fmt(".3f"))
            } else {
                let length = made.iter().find(|r| r.0 == how).map(|r| r.1).unwrap_or(N::fl(0.));
                let mut note = if length.f() < 1e-9 { "butt — 0 mm outside the collets".to_owned() } else { format!("{} mm straight", length.fmt(".2f")) };
                if self.quarters().iter().any(|q| q.0 == cid) {
                    note += &format!(" + one 90° turn at R{} ({} mm)", k.min_bend.fmt("g"), k.quarter_len.fmt(".2f"));
                }
                note
            };
            rt.print(format!("  fluid-{} {} → {}  {note}", num::fmti(cid, "<3"), fmtv(&s(frm), ">7")?, fmtv(&s(to), "<7")?))?;
        }
        let mouths = self.mouths()?;
        rt.print(format!("\n{} mouths leave the study", mouths.len()))?;
        for m in mouths {
            let rounded = m.axis.map(|c| num::round_to(c.f(), 6) + 0.);
            let way = match rounded {
                [x, y, z] if x == 0. && y == -1. && z == 0. => "front".to_owned(),
                [x, y, z] if x == 0. && y == 1. && z == 0. => "back".to_owned(),
                [x, y, z] if x == 0. && y == 0. && z == 1. => "up".to_owned(),
                [x, y, z] if x == 0. && y == 0. && z == -1. => "down".to_owned(),
                _ => tup(m.axis).str()?,
            };
            rt.print(format!(
                "  {} {}  ({}, {}, {})  {}  {}",
                fmtv(&s(m.cid), "<9")?,
                fmtv(&s(m.p), ">7")?,
                m.at[0].fmt("7.2f"),
                m.at[1].fmt("7.2f"),
                m.at[2].fmt("6.2f"),
                fmtv(&s(way), ">5")?,
                m.what
            ))?;
        }
        let [bx, by, bz] = lens(&bbn);
        let [rx, ry, rz] = lens(&reachn);
        let litres = |x: N, y: N, z: N| -> Result<String> { Ok(div(x * y * z, N::fl(1e6))?.fmt(".2f")) };
        rt.print(format!(
            "\nenvelope  X {}   Y {}   Z {}    ({} L)   bodies and the tube between them",
            bx.fmt("7.2f"),
            by.fmt("7.2f"),
            bz.fmt("7.2f"),
            litres(bx, by, bz)?
        ))?;
        rt.print(format!(
            "          x[{}, {}]  y[{}, {}]  z[{}, {}]",
            bbn[0].fmt("7.2f"),
            bbn[3].fmt("7.2f"),
            bbn[1].fmt("7.2f"),
            bbn[4].fmt("7.2f"),
            bbn[2].fmt("7.2f"),
            bbn[5].fmt("7.2f")
        ))?;
        rt.print(format!(
            "          X {}   Y {}   Z {}    ({} L)   with one {} mm mouth stub on each of the {}",
            rx.fmt("7.2f"),
            ry.fmt("7.2f"),
            rz.fmt("7.2f"),
            litres(rx, ry, rz)?,
            k.min_bend.fmt("g"),
            mouths.len()
        ))?;
        rt.print(format!(
            "deck at z {}, {} mm over the pump heads; each mm of BARB_LEAD lifts it one",
            k.deck_z.fmt(".2f"),
            (k.deck_z - k.valve_port_z - k.pump_barb_z).fmt(".2f")
        ))?;
        rt.print(format!(
            "LIMB_PITCH {} of a {} barb pitch — each tee stands {} mm off its barb's column on a {} mm lead, which is the climb {}° of skew asks for. HSM_LIMB_PITCH= builds another.",
            k.limb_pitch.fmt("g"),
            k.barb_pitch.fmt("g"),
            k.limb_step.fmt(".2f"),
            k.barb_lead.fmt(".2f"),
            num::fmt(FLAVOR_SKEW, "g")
        ))?;
        rt.print(format!("crossbar {} mm exposed; the two reservoir crossings enter their collets  off axis", num::fmt(CROSSBAR, ".2f")))?;
        rt.print(format!("upper tubes: {}, {} mm exposed, each straight", FORE_STUB_ROWS.len(), exposed.fmt("g")))?;
        rt.print(format!(
            "fold: hinge at y {} z {}, decks at z {} and {} — {} apart, which {} standing over {} sets",
            k.hinge_y.fmt(".2f"),
            k.hinge_z.fmt(".2f"),
            k.deck_z.fmt(".2f"),
            k.upper_z.fmt(".2f"),
            k.deck_sep.fmt("g"),
            FOLD_BINDS.0,
            FOLD_BINDS.1
        ))?;
        rt.print(format!(
            "lower links: {} lower returns, each a stem elbow in its pump tee's lower port, one continuous tube and a stem elbow in its rear valve; {} mm inner and {} mm outer nominal tube stock including insertion",
            SEGMENTS.iter().filter(|r| r.3 == "spine").count(),
            fmtv(&self.return_cut(k.inner_x)?, ".3f")?,
            fmtv(&self.return_cut(k.outer_x)?, ".3f")?
        ))?;
        let steps = SBENDS.iter().map(|(_, v)| Ok((*v, self.source_step(v)?))).collect::<Result<Vec<_>>>()?;
        let hairpins = self.hairpins_drawn()?;
        let mut parts = Vec::new();
        for (v, (th, s, ln)) in &steps {
            let spread = SOURCE_SPREAD.iter().find(|r| r.0 == *v).map(|r| r.1).ok_or_else(|| missing(v))?;
            let tail = if spread != 0. { format!(", spread {} outboard", num::fmt(spread, "g")) } else { String::new() };
            parts.push(format!(
                "{v} {}° each side of {} mm, {} mm of tube{tail}",
                num::fmt(num::degrees(*th), ".3f"),
                num::fmt(*s, ".2f"),
                num::fmt(*ln, ".2f")
            ));
        }
        rt.print(format!(
            "step: {} two-arc steps at R{}, each {} along the run and {} across it toward the crown, {} behind a hairpin — {}",
            SBENDS.len(),
            k.min_bend.fmt("g"),
            num::fmt(SOURCE_TRAVEL, "g"),
            num::fmt(self.source_cross("V-B")?.1.abs(), "g"),
            hairpins,
            parts.join("; ")
        ))?;
        let quarters = self.quarters();
        rt.print(format!(
            "turns: {} quarters at R{}, {} mm each — all on the plane y {}, {} on the lower deck and {} on the folded one",
            quarters.len(),
            k.min_bend.fmt("g"),
            k.quarter_len.fmt(".2f"),
            (k.bend_y - k.inner_limb_drop + N::fl(AFT_PACK_RISE)).fmt(".2f"),
            quarters.iter().filter(|q| q.2.f() == k.deck_z.f()).count(),
            quarters.iter().filter(|q| q.2.f() != k.deck_z.f()).count()
        ))?;
        rt.print(format!(
            "source tube corners: {}, at R{}; the recorded stock basis is {}. Pump-junction links use their documented straight or formed paths.",
            quarters.len() as i64 + 2 * SBENDS.len() as i64 + 2 * hairpins,
            k.min_bend.fmt("g"),
            fmtv(&self.stock.attr("source")?, "")?
        ))?;
        let meets = self.turns_meet()?;
        let worst_turn = meets.iter().map(|m| m.1).reduce(nmax).context("empty min/max")?;
        rt.print(format!("\nturns meet their collets: {} checked, worst {} mm apart", meets.len(), worst_turn.fmt(".4f")))?;
        for (cid, d) in &meets {
            if d.f() > 1e-6 {
                rt.print(format!("  fluid-{cid} lands {} mm off the collet it turns onto", d.fmt(".3f")))?;
            }
        }
        let off = self.mirror_off()?;
        let worst = off.iter().map(|(_, _, dx, dy)| nmax(*dx, *dy)).reduce(nmax).context("empty min/max")?;
        rt.print(format!("\nmirror about x=0: {} twinned pairs, worst off by {} mm", off.len(), worst.fmt(".4f")))?;
        for (a, b, dx, dy) in &off {
            if nmax(*dx, *dy).f() > 1e-6 {
                rt.print(format!("  {a} / {b}   x sums to {}, y differs by {}", dx.fmt(".4f"), dy.fmt(".4f")))?;
            }
        }
        struct Hit {
            obj: Val,
            a: Val,
            b: Val,
            volume: Val,
            fields: Vec<Val>,
        }
        let mut hits = Vec::new();
        for c in py::at(&m, "hits")?.iter()? {
            let (a, b, volume) = (py::at(&c, "a")?, py::at(&c, "b")?, py::at(&c, "volume")?);
            let fields = py::at(&c, "where")?.iter()?;
            let place = py::call(&extents, fields.clone())?;
            let obj = py::call(&clash, vec![a.clone(), b.clone(), volume.clone(), place])?;
            hits.push(Hit { obj, a, b, volume, fields });
        }
        let unanswered = py::at(&m, "unanswered")?;
        let mut stems: Vec<(Vec<Val>, Val)> = Vec::new();
        for r in py::at(&m, "stems")?.iter()? {
            let key = set_of(vec![py::at(&r, "a")?, py::at(&r, "b")?])?;
            let (_inside, outside) = (py::at(&r, "inside")?, py::at(&r, "outside")?);
            let mut held = false;
            for row in stems.iter_mut() {
                if set_eq(&row.0, &key)? {
                    row.1 = outside.clone();
                    held = true;
                    break;
                }
            }
            if !held {
                stems.push((key, outside));
            }
        }
        let mut bad = Vec::new();
        for hit in hits {
            let key = set_of(vec![hit.a.clone(), hit.b.clone()])?;
            let mut outside = N::fl(1.0);
            for row in &stems {
                if set_eq(&row.0, &key)? {
                    outside = N::of(&row.1)?;
                    break;
                }
            }
            if outside.f() > 1.0 {
                bad.push(hit);
            }
        }
        if !stems.is_empty() {
            let worst = stems.iter().map(|r| N::of(&r.1)).collect::<Result<Vec<_>>>()?.into_iter().reduce(nmax).context("empty min/max")?;
            rt.print(format!("\nstem elbows in their collets: {}, worst {} mm³ outside the stem", stems.len(), worst.fmt(".6f")))?;
        }
        rt.print(format!(
            "\nclash check: {} pair(s) sharing volume, {} the boolean would not answer for",
            bad.len(),
            unanswered.len()?
        ))?;
        for hit in &bad {
            let (axis, d) = escape(&six(&hit.fields)?);
            rt.print(format!(
                "  {} ∩ {}\n      {}   {} mm³, {} on {axis} clears it",
                fmtv(&hit.a, "")?,
                fmtv(&hit.b, "")?,
                extents_text(&hit.fields)?,
                fmtv(&hit.volume, ".1f")?,
                d.fmt(".2f")
            ))?;
        }
        let unanswered = unanswered.iter()?;
        for row in &unanswered {
            let v = py::unpack(row, 3)?;
            rt.print(format!("  {} ? {}   {}", fmtv(&v[0], "")?, fmtv(&v[1], "")?, fmtv(&v[2], "")?))?;
        }
        let data = ReportData {
            bb: bbn,
            reach: reachn,
            bad: bad.len() + unanswered.len(),
            made: made.iter().map(|(key, v)| (s(*key), *v)).collect(),
            mirror: off.iter().map(|(_, _, dx, dy)| (*dx, *dy)).collect(),
        };
        let bad_all = Val::list(bad.into_iter().map(|h| h.obj).chain(unanswered).collect());
        let made_val = py::dict(made.iter().map(|(key, v)| (*key, v.val())));
        let mirror_val = Val::list(off.iter().map(|(a, b, dx, dy)| Val::Tuple(vec![s(*a), s(*b), dx.val(), dy.val()])).collect());
        let out = py::dict([("bb", bb), ("reach", reach), ("bad", bad_all), ("made", made_val), ("mirror", mirror_val)]);
        Ok((out, data))
    }
    fn write_readme(&self, r: &ReportData) -> Result<()> {
        let k = &self.k;
        let [bx, by, bz] = lens(&r.bb);
        let [rx, ry, rz] = lens(&r.reach);
        let runs = self.runs()?;
        let pump_tee_tube_count = FORE_STUB_ROWS.len() + LOWER_CONNECTIONS.len();
        let crossbar = runs.iter().find(|r| r.0 == "crossbar").context("missing key 'crossbar'")?;
        let swallowed = SEGMENTS.iter().filter(|s| s.3 == "butt" || (s.3 == "crossbar" && dist(crossbar.1, crossbar.2).f() < 1e-9)).count();
        let lldpe_cut_count = pump_tee_tube_count + 2 + 0 + swallowed + BARB_OF.len();
        let made = |how: &str| -> Result<N> {
            for (key, v) in &r.made {
                if interop::eq(key, &s(how))? {
                    return Ok(*v);
                }
            }
            Ok(N::fl(0.))
        };
        let plumbing = self.plumbing()?;
        let showing = &plumbing[junction_index(self.junction_at_author_x(k.inner_x)?)?].elbows.get(1).context("IndexError")?.showing;
        let (b_th, b_s, b_len) = self.source_step("V-B")?;
        let (a_th, a_s, a_len) = self.source_step("V-A")?;
        let jog = self.source_cross("V-B")?.1.abs();
        let cross_a = self.source_cross("V-A")?;
        let hairpins = self.hairpins_drawn()?;
        let mirror_off = r.mirror.iter().map(|(dx, dy)| nmax(*dx, *dy)).reduce(nmax).context("empty min/max")?;
        let mut butts = 0;
        let mut straights = 0;
        for (_, _, _, how) in SEGMENTS {
            if how != "spine" && how != "turn" && made(how)?.f() < 1e-9 {
                butts += 1;
            }
            if runs.iter().any(|r| r.0 == how) && made(how)?.f() >= 1e-9 {
                straights += 1;
            }
        }
        let g = |n: N| n.fmt("g");
        let f2 = |n: N| n.fmt(".2f");
        let variables: Vec<(&str, String)> = vec![
            ("ENV_X", bx.fmt(".0f")),
            ("ENV_Y", by.fmt(".0f")),
            ("ENV_Z", bz.fmt(".0f")),
            ("ENV_L", div(bx * by * bz, N::fl(1e6))?.fmt(".2f")),
            ("REACH_X", rx.fmt(".0f")),
            ("REACH_Y", ry.fmt(".0f")),
            ("REACH_Z", rz.fmt(".0f")),
            ("STUB_LEN", g(k.min_bend)),
            ("DECK_Z", f2(k.deck_z)),
            ("DECK_Z2", f2(k.deck_z)),
            ("UPPER_Z", f2(k.upper_z)),
            ("UPPER_Z2", f2(k.upper_z)),
            ("RETURN_ELBOW_COUNT", (2 * LOWER_CONNECTIONS.len()).to_string()),
            ("RETURN_EXPOSED", fmtv(&self.return_exposed(k.inner_x)?, ".2f")?),
            ("RETURN_CUT", fmtv(&self.return_cut(k.inner_x)?, ".2f")?),
            ("OUTER_AFT_INSET", g(k.outer_aft_inset)),
            ("OUTER_RETURN_EXPOSED", fmtv(&self.return_exposed(k.outer_x)?, ".2f")?),
            ("OUTER_RETURN_CUT", fmtv(&self.return_cut(k.outer_x)?, ".2f")?),
            ("RETURN_DROP", fmtv(&self.returns.attr("ELBOW_DROP")?, ".3g")?),
            ("RETURN_SHOWING", fmtv(showing, ".3g")?),
            ("DECK_SEP", g(k.deck_sep)),
            ("SPINE_COUNT", SEGMENTS.iter().filter(|r| r.3 == "spine").count().to_string()),
            ("MIN_BEND2", g(k.min_bend)),
            ("QUARTER_R", g(k.min_bend)),
            ("QUARTER_LEN", f2(k.quarter_len)),
            ("QUARTER_COUNT", "2".into()),
            ("QUARTER_COUNT2", "2".into()),
            ("QUARTER_COUNT4", "2".into()),
            ("MOUTH_COUNT2", MOUTH_ROWS.len().to_string()),
            ("BEND_Y", f2(k.bend_y - k.inner_limb_drop + N::fl(AFT_PACK_RISE))),
            ("CORNER_COUNT", (2 + 2 * SBENDS.len() as i64 + 2 * hairpins).to_string()),
            ("STEP_ANGLE", num::fmt(num::degrees(b_th), ".3f")),
            ("STEP_STRAIGHT", num::fmt(b_s, ".2f")),
            ("STEP_LEN", num::fmt(b_len, ".2f")),
            ("STEP_TRAVEL", num::fmt(SOURCE_TRAVEL, "g")),
            ("STEP_JOG", num::fmt(jog, "g")),
            ("STEP_TRAVEL2", num::fmt(SOURCE_TRAVEL, "g")),
            ("STEP_TRAVEL3", num::fmt(SOURCE_TRAVEL, "g")),
            ("STEP_JOG2", num::fmt(jog, "g")),
            ("STEP_FLOOR", num::fmt(two_arc_floor(k.min_bend.f(), jog)?, ".2f")),
            ("HAIRPIN_COUNT", hairpins.to_string()),
            ("BARB_STANDOFF", g(k.barb_standoff)),
            ("BARB_TUBE_LEN", f2(k.pump_stub_projection)),
            ("BARB_PLATE_BERTH", g(k.barb_plate_berth)),
            ("FORE_STUB_GAP", g(k.fore_stub_gap)),
            ("FORE_STUB_EXPOSED", g(self.fore_stub_exposed()?)),
            ("FORE_STUB_COUNT", FORE_STUB_ROWS.len().to_string()),
            ("PUMP_STATION_LEAD", g(k.pump_station_lead)),
            ("PUMP_DROP", g(k.pump_station_drop)),
            ("STEP_SPREAD", num::fmt(SOURCE_SPREAD[0].1, "g")),
            ("STEP_CROSS_A", num::fmt(num::hypot2(cross_a.0, cross_a.1), ".2f")),
            ("STEP_ANGLE_A", num::fmt(num::degrees(a_th), ".3f")),
            ("STEP_STRAIGHT_A", num::fmt(a_s, ".2f")),
            ("STEP_LEN_A", num::fmt(a_len, ".2f")),
            ("DECK_GAP", f2(k.deck_z - k.valve_port_z - k.pump_barb_z)),
            ("CROSSBAR", num::fmt(CROSSBAR, ".2f")),
            ("TEE_COUNT", self.bodies.iter().filter(|b| b.name.starts_with("Y-")).count().to_string()),
            ("TEE_COUNT2", self.bodies.iter().filter(|b| b.name.starts_with("Y-")).count().to_string()),
            ("TUBE_COUNT2", lldpe_cut_count.to_string()),
            ("TWIN_COUNT", r.mirror.len().to_string()),
            ("MIRROR_OFF", mirror_off.fmt(".4f")),
            ("SEGMENT_COUNT", SEGMENTS.len().to_string()),
            ("BUTT_COUNT", butts.to_string()),
            ("TUBE_COUNT", lldpe_cut_count.to_string()),
            ("PUMP_TEE_TUBE_COUNT", pump_tee_tube_count.to_string()),
            ("STRAIGHT_COUNT", straights.to_string()),
            ("MOUTH_COUNT", MOUTH_ROWS.len().to_string()),
            ("MIN_BEND", g(k.min_bend)),
            ("BARB_PITCH", g(k.barb_pitch)),
            ("BARB_PITCH2", g(k.barb_pitch)),
            ("BARB_INSET", g(k.barb_inset)),
            ("VALVE_PITCH", g(k.valve_pitch)),
            ("VALVE_PORT_Z", g(k.valve_port_z)),
            ("VALVE_LEN", g(k.valve_len)),
            ("TEE_RUN", g(k.tee_run)),
            ("TEE_SPAN", g(N::int(2) * k.tee_run)),
            ("DIVIDER_PITCH", g(N::int(2) * k.outlet_y)),
            ("LIMB_OUT_XW", f2(-k.outer_x)),
            ("LIMB_IN_XW", f2(-k.inner_x)),
            ("LIMB_IN_XE", k.inner_x.fmt("+.2f")),
            ("LIMB_OUT_XE", k.outer_x.fmt("+.2f")),
            ("INNER_GAP", f2(N::int(2) * k.inner_x - k.valve_pitch)),
            ("CLASHES", r.bad.to_string()),
        ];
        let substitute = self.ns.get("substitute_md")?;
        let readme = self.here.parent().unwrap_or(&self.here).join("README.md");
        let variables = py::dict(variables.into_iter().map(|(key, v)| (key, s(v))));
        py::call_kw(&substitute, vec![Val::Path(readme)], vec![("variables", variables)])?;
        Ok(())
    }
}

/// `_matrix(origin, x_dir, z_dir, carry)`: the orthogonal frame, carried to another frame.
fn matrix(origin: V3, x_dir: V3, z_dir: V3, carry: &dyn Fn(V3) -> Result<V3>) -> Result<Val> {
    let y_dir = cross(z_dir, x_dir);
    let p = carry(origin)?;
    let x_dir = sub3(carry(add3(origin, x_dir))?, p);
    let y_dir = sub3(carry(add3(origin, y_dir))?, p);
    let z_dir = sub3(carry(add3(origin, z_dir))?, p);
    Ok(Val::list((0..3).map(|k| Val::list(vec![x_dir[k].val(), y_dir[k].val(), z_dir[k].val(), p[k].val()])).collect()))
}

/// `report`'s answer as `_write_readme` reads it from a caller.
fn report_data(r: &Val) -> Result<ReportData> {
    let bb = six(&extents_fields(&r.get(s("bb"))?)?)?;
    let reach = six(&extents_fields(&r.get(s("reach"))?)?)?;
    let made = py::snapshot(&r.get(s("made"))?)?;
    let made = made.iter()?.into_iter().map(|key| Ok((key.clone(), N::of(&made.get(key)?)?))).collect::<Result<Vec<_>>>()?;
    let mirror = py::snapshot(&r.get(s("mirror"))?)?
        .iter()?
        .iter()
        .map(|row| {
            let v = py::unpack(row, 4)?;
            Ok((N::of(&v[2])?, N::of(&v[3])?))
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(ReportData { bb, reach, bad: r.get(s("bad"))?.len()?, made, mirror })
}

fn main(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let rust_part = rt.import("_rust_part")?;
    let cut = rust_part.attr("cut")?;
    let payload = st.numbers(rt, true)?;
    let folder = Val::Path(st.here.parent().unwrap_or(&st.here).to_owned());
    let said = py::call(&cut, vec![s("machine"), s("manifold-layout"), payload, folder])?;
    rt.print("-> manifold-layout.step".into())?;
    let measurements = said.get(s("results"))?.get(Val::Int(0))?.get(s("measurements"))?;
    let (_, data) = st.report(rt, &measurements)?;
    st.write_readme(&data)?;
    rt.print("-> README.md".into())?;
    Ok(Val::None)
}

/// The script's `if __name__ == "__main__":` block.
pub fn main_block(rt: &Rt) -> Result<()> {
    let ns = rt.namespace(MODULE)?;
    let rust_part = rt.import("_rust_part")?;
    ns.set("_rust_part", rust_part.clone())?;
    py::method(&ns.get("_rust_part")?, "start", vec![])?;
    let sys = ns.get("sys")?;
    if sys.attr("argv")?.get(Val::Slice { start: Some(1), stop: None, step: 1 })?.truthy()? {
        py::call(&sys.attr("exit")?, vec![s("usage: manifold_layout.py")])?;
    }
    let result = main(rt)?;
    py::call(&ns.get("sys")?.attr("exit")?, vec![result])?;
    Ok(())
}

// ---------------------------------------------------------------------------------------------
// The namespace.

/// A provider constant as the namespace holds it, and as a number.
fn constant(module: &Val, name: &str) -> Result<(Val, N)> {
    let v = module.attr(name)?;
    let n = N::of(&v)?;
    Ok((v, n))
}
/// `float(os.environ.get(name, default))`.
fn env_float(os: &Val, name: &str, default: Val) -> Result<N> {
    let got = py::call(&os.attr("environ")?.attr("get")?, vec![s(name), default])?;
    N::of(&py::call(&interop::builtin("float").context("float")?, vec![got])?)
}
fn fl(x: f64) -> Val {
    Val::Float(x)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::MANIFOLD_LAYOUT))?;
    ns.set("math", rt.import("math")?)?;
    let os = rt.import("os")?;
    ns.set("os", os.clone())?;
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("NamedTuple", rt.member("typing", "NamedTuple")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    ns.set("_here", Val::Path(here.clone()))?;
    let parents = || here.ancestors().skip(1);
    let hw = parents().find(|p| p.file_name().is_some_and(|n| n == "hardware")).context("StopIteration")?.to_owned();
    ns.set("_hw", Val::Path(hw.clone()))?;
    let repo = parents().find(|p| p.join("hardware").join("scripts").join("_cadq_export.py").is_file()).context("StopIteration")?;
    ns.set("_repo", Val::Path(repo.to_owned()))?;
    let tools = parents().find(|p| p.join("tools").join("docgen").is_dir()).context("StopIteration")?.join("tools");
    ns.set("_tools", Val::Path(tools.clone()))?;
    let enclosure = hw.join("printed-parts").join("enclosure");
    for p in [
        hw.join("scripts"),
        hw.join("reference").join("beduan-solenoid"),
        hw.join("reference").join("tee-connector"),
        hw.join("reference").join("y-divider"),
        hw.join("reference").join("kamoer-kphm400"),
        hw.join("printed-parts").join("cadlib"),
        enclosure.join("enclosure"),
        enclosure.join("pump-dock"),
        enclosure.join("pump-tray"),
    ] {
        ns.set("_p", Val::Path(p.clone()))?;
        py::sys_path_insert(rt, &py::path_str(&p))?;
    }
    py::sys_path_insert(rt, &py::path_str(&tools))?;
    // The document shim records the importing module, so it is imported here, at module level.
    ns.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    let vlv = rt.import("beduan_solenoid")?;
    ns.set("vlv", vlv.clone())?;
    let kp = rt.import("kamoer_kphm400")?;
    ns.set("kp", kp.clone())?;
    let tee = rt.import("tee_connector")?;
    ns.set("tee", tee.clone())?;
    let ydiv = rt.import("y_divider")?;
    ns.set("ydiv", ydiv.clone())?;
    let routing = rt.import("_routing")?;
    ns.set("_routing", routing.clone())?;
    ns.set("_bounds", rt.import("_stated_bounds")?)?;
    let enc_if = rt.import("_enclosure_interface")?;
    ns.set("_enc_if", enc_if.clone())?;
    let returns = rt.import("fixed_returns")?;
    ns.set("_returns", returns.clone())?;
    let step = |name: &str| hw.join("reference").join(name).join(format!("{name}.step"));
    let (elbow_step, tee_step, kamoer_step) = (step("elbow-connector"), step("tee-connector"), step("kamoer-kphm400"));
    ns.set("ELBOW_STEP", Val::Path(elbow_step.clone()))?;
    ns.set("TEE_STEP", Val::Path(tee_step.clone()))?;
    ns.set("KAMOER_STEP", Val::Path(kamoer_step.clone()))?;
    ns.set(
        "PUMP_TURNS",
        Val::Tuple(vec![
            Val::Tuple(vec![py::ftuple(&[1., 0., 0.]), fl(-90.)]),
            Val::Tuple(vec![py::ftuple(&[0., 1., 0.]), fl(180.)]),
        ]),
    )?;
    let (v, valve_len) = constant(&vlv, "port_length")?;
    ns.set("VALVE_LEN", v)?;
    let (v, valve_pitch) = constant(&vlv, "body_width_x")?;
    ns.set("VALVE_PITCH", v)?;
    let (v, valve_port_z) = constant(&vlv, "port_center_z")?;
    ns.set("VALVE_PORT_Z", v)?;
    ns.set("VALVE_TOP_Z", vlv.attr("coil_z_range")?.get(Val::Int(1))?)?;
    let (v, tee_run) = constant(&tee, "RUN_HALF")?;
    ns.set("TEE_RUN", v)?;
    let (v, tee_branch) = constant(&tee, "BRANCH_REACH")?;
    ns.set("TEE_BRANCH", v)?;
    let (tube_d_val, tube_d) = constant(&tee, "TUBE_D")?;
    ns.set("TUBE_D", tube_d_val.clone())?;
    let stock = py::call(&routing.attr("stock_of")?, vec![s("fluid"), tube_d_val])?;
    ns.set("STOCK", stock.clone())?;
    let (min_bend_val, min_bend) = constant(&stock, "min_bend")?;
    ns.set("MIN_BEND", min_bend_val.clone())?;
    ns.set("FLAVOR_SKEW", fl(FLAVOR_SKEW))?;
    ns.set("LINE_HUG", fl(LINE_HUG))?;
    let (v, head_w) = constant(&kp, "head_w")?;
    ns.set("HEAD_W", v)?;
    ns.set("MOTOR_D", kp.attr("motor_dia")?)?;
    let arch = kp.attr("arch_xs")?;
    let barb_pitch = N::of(&arch.get(Val::Int(1))?)? - N::of(&arch.get(Val::Int(0))?)?;
    ns.set("BARB_PITCH", barb_pitch.val())?;
    let barb_inset = constant(&kp, "arch_plane_z")?.1 - constant(&kp, "head_front_z")?.1;
    ns.set("BARB_INSET", barb_inset.val())?;
    ns.set("BUTT", fl(BUTT))?;
    let pump_station_drop = constant(&enc_if, "pump_station_drop")?.1;
    let manifold_rise = constant(&enc_if, "manifold_rise")?.1;
    let pump_seated_drop = constant(&enc_if, "pump_seated_drop")?.1;
    let outlet = constant(&kp, "outlet_above_skirt_bottom")?.1;
    let carrier_drop = pump_station_drop + manifold_rise + pump_seated_drop - outlet;
    ns.set("CARRIER_DROP", carrier_drop.val())?;
    let (inner_limb_drop_val, inner_limb_drop) = constant(&enc_if, "inner_limb_drop")?;
    ns.set("INNER_LIMB_DROP", inner_limb_drop_val.clone())?;
    ns.set("FORE_VALVE_RISE", fl(FORE_VALVE_RISE))?;
    let fore_stub_gap = N::fl(FORE_VALVE_RISE) + carrier_drop;
    ns.set("FORE_STUB_GAP", fore_stub_gap.val())?;
    ns.set("FORE_VALVES", Val::frozen_set(FORE_VALVES.iter().map(|n| s(*n)).collect()))?;
    ns.set("OUTER_AFT_X", fl(OUTER_AFT_X))?;
    ns.set("CARRIER_DATUM_SHIFT", fl(CARRIER_DATUM_SHIFT))?;
    ns.set("FIXED_TEE_AFT_SHIFT", fl(FIXED_TEE_AFT_SHIFT))?;
    ns.set("AFT_DECK_AFT_SHIFT", fl(AFT_DECK_AFT_SHIFT))?;
    ns.set("AFT_PACK_RISE", fl(AFT_PACK_RISE))?;
    ns.set("OUTER_AFT_DROP", inner_limb_drop_val)?;
    ns.set("WORLD_LIFT", fl(WORLD_LIFT))?;
    ns.set("PACK_ORIGIN_Y", fl(PACK_ORIGIN_Y))?;
    ns.set("BARB_TO_PLATE", fl(BARB_TO_PLATE))?;
    let tip_from_fore = constant(&returns, "TIP_FROM_FORE")?.1;
    let pump_stub_projection = N::fl(BARB_TO_PLATE) + tip_from_fore;
    ns.set("PUMP_STUB_PROJECTION", pump_stub_projection.val())?;
    ns.set("PUMP_TUBE_HELD", fl(PUMP_TUBE_HELD))?;
    ns.set("PUMP_TUBE_CUT", (N::fl(PUMP_TUBE_HELD) + pump_stub_projection).val())?;
    ns.set("PUMP_BARBS_TO_BORE_FACE", fl(PUMP_BARBS_TO_BORE_FACE))?;
    let pump_station_lead = constant(&enc_if, "pump_station_lead")?.1;
    let collet_travel = constant(&tee, "BRANCH_COLLET_TRAVEL")?.1;
    let barb_plate_berth = N::fl(PUMP_BARBS_TO_BORE_FACE) - pump_station_lead - N::fl(CARRIER_DATUM_SHIFT) - collet_travel;
    ns.set("BARB_PLATE_BERTH", barb_plate_berth.val())?;
    let pump_barb_z = head_w - pump_station_lead;
    ns.set("PUMP_BARB_Z", pump_barb_z.val())?;
    let pump_y = outlet - pump_station_drop - pump_seated_drop - manifold_rise;
    ns.set("PUMP_Y", pump_y.val())?;
    let barb_standoff = barb_plate_berth + pump_station_lead;
    ns.set("BARB_STANDOFF", barb_standoff.val())?;
    ns.set("CROSSBAR", fl(CROSSBAR))?;
    let limb_pitch = env_float(&os, "HSM_LIMB_PITCH", barb_pitch.val())?;
    ns.set("LIMB_PITCH", limb_pitch.val())?;
    let inner_x = tee_branch + N::fl(CROSSBAR / 2.);
    ns.set("INNER_X", inner_x.val())?;
    let half_pitch = div(limb_pitch, N::fl(2.))?;
    let pump_dx = inner_x + half_pitch;
    ns.set("PUMP_DX", pump_dx.val())?;
    let outer_x = pump_dx + half_pitch;
    ns.set("OUTER_X", outer_x.val())?;
    let outer_aft_inset = outer_x - N::fl(OUTER_AFT_X);
    ns.set("OUTER_AFT_INSET", outer_aft_inset.val())?;
    let limb_step = div(barb_pitch - limb_pitch, N::fl(2.))?;
    ns.set("LIMB_STEP", limb_step.val())?;
    let barb_lead_floor = div(limb_step, N::fl(num::radians(FLAVOR_SKEW).tan()))?;
    ns.set("BARB_LEAD_FLOOR", barb_lead_floor.val())?;
    let barb_lead = barb_lead_floor + barb_standoff;
    ns.set("BARB_LEAD", barb_lead.val())?;
    let deck_z = pump_barb_z + barb_lead + tee_branch;
    ns.set("DECK_Z", deck_z.val())?;
    ns.set("STUB", min_bend_val.clone())?;
    let hinge_y = -tee_run;
    ns.set("HINGE_Y", hinge_y.val())?;
    ns.set("FOLD_CLEAR", fl(LINE_HUG))?;
    ns.set("ELBOW_LEG", fl(ELBOW_LEG))?;
    let mut colors = Vec::new();
    for name in ["C_COIL", "C_PUMP_BOSS", "C_PUMP_HEAD", "C_PUMP_MOTOR", "C_VALVE", "M_JG_BLACK_PP"] {
        let color = rt.member("_materials", name)?;
        ns.set(name, color.clone())?;
        colors.push(color);
    }
    let [c_coil, c_boss, c_head, c_motor, c_valve, c_tee]: [Val; 6] = colors.try_into().map_err(|_| anyhow!("six colors"))?;
    ns.set("C_TEE", c_tee.clone())?;
    ns.set("C_HEAD", c_head.clone())?;
    ns.set("C_BOSS", c_boss.clone())?;
    ns.set("C_MOTOR", c_motor.clone())?;

    ns.def(rt, "valve_dirs", |_, args, kw| {
        let mut a = py::bind(args, kw, &["flow"], &[])?;
        let flow = py::call(&interop::builtin("float").context("float")?, vec![a.req("flow")?])?;
        Ok(Val::Tuple(vec![Val::Tuple(vec![flow, fl(0.), fl(0.)]), py::ftuple(&[0., 0., 1.])]))
    })?;
    ns.def(rt, "tee_dirs", |_, args, kw| {
        let mut a = py::bind(args, kw, &["branch"], &[])?;
        let r = py::unpack(&a.req("branch")?, 3)?;
        let (bx, bz) = (&r[0], &r[2]);
        if bz.truthy()? {
            let below = interop::compare("lt", bz.clone(), Val::Int(0))?.truthy()?;
            return Ok(Val::Tuple(vec![py::ftuple(&[1., 0., 0.]), py::ftuple(if below { &[0., 1., 0.] } else { &[0., -1., 0.] })]));
        }
        Ok(Val::Tuple(vec![Val::Tuple(vec![fl(0.), fl(0.), bx.clone()]), py::ftuple(&[0., 1., 0.])]))
    })?;
    let lay = Lay { valve_len, tee_run, inner_x, outer_x };
    ns.set("LIMBS", limbs_val(&lay))?;
    ns.set("PUMPS", py::dict([("pump-a", (-pump_dx).val()), ("pump-b", pump_dx.val())]))?;
    let barb_of = BARB_OF
        .iter()
        .map(|(n, sign, side)| (s(*n), Val::Tuple(vec![(if *sign < 0. { -pump_dx } else { pump_dx }).val(), Val::Int(*side)])))
        .collect();
    ns.set("BARB_OF", Val::dict(barb_of))?;
    let junctions = Val::frozen_set(JUNCTIONS.iter().map(|n| s(*n)).collect());
    ns.set("PUMP_JUNCTIONS", junctions.clone())?;
    ns.set("FIXED_TEES", junctions.clone())?;
    ns.set("PUMP_VALVES", Val::dict(PUMP_VALVES.iter().map(|(t, u, r)| (s(*t), Val::Tuple(vec![s(*u), s(*r)]))).collect()))?;
    ns.set("PUMP_PART_SUFFIX", py::dict(PUMP_PART_SUFFIX.iter().map(|(t, x)| (*t, s(*x)))))?;
    ns.set("CARRIER_TEES", junctions)?;
    ns.set("CARRIER_RELEASE", tee.attr("CARRIER_RELEASE_OFFSET")?)?;
    ns.set("CARRIER_SQUEEZE", tee.attr("CARRIER_SQUEEZE_OFFSET")?)?;
    let (v, carrier_connected) = constant(&tee, "CARRIER_CONNECTED_OFFSET")?;
    ns.set("CARRIER_CONNECTED", v)?;
    ns.set("CARRIER_PARK", tee.attr("CARRIER_PARK_OFFSET")?)?;
    let carrier_states = py::snapshot(&tee.attr("CARRIER_STATES")?)?;
    let states = Val::dict(vec![]);
    for name in carrier_states.iter()? {
        let row = py::unpack(&carrier_states.get(name.clone())?, 2)?;
        states.set(name, row[0].clone())?;
    }
    ns.set("CARRIER_STATES", states)?;

    ns.def(rt, "barb_station", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["tee"], &[])?;
        Ok(tup(state(rt)?.barb_station(&name_of(&a.req("tee")?)?)?))
    })?;
    ns.def(rt, "body_name", |_, args, kw| {
        let mut a = py::bind(args, kw, &["chain"], &[])?;
        Ok(s(body_name(&a.string("chain")?)))
    })?;
    ns.def(rt, "_half", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        let st = state(rt)?;
        let lay = Lay { valve_len: st.k.valve_len, tee_run: st.k.tee_run, inner_x: st.k.inner_x, outer_x: st.k.outer_x };
        Ok(lay.half(&a.string("name")?).val())
    })?;
    ns.def(rt, "lay_out", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(bodies_val(&state(rt)?.bodies))
    })?;
    let bodies = lay_out(&lay);
    let flat = bodies_val(&bodies);
    ns.set("FLAT", flat.clone())?;
    ns.set("P", flat)?;
    ns.set("PURCHASED_TEES", Val::frozen_set(bodies.iter().filter(|b| b.name.starts_with("Y-")).map(|b| s(b.name)).collect()))?;
    let deck_sep = env_float(&os, "HSM_DECK_SEP", fl(60.95))?;
    ns.set("DECK_SEP", deck_sep.val())?;
    ns.set("FOLD_BINDS", Val::Tuple(vec![s(FOLD_BINDS.0), s(FOLD_BINDS.1)]))?;
    let hinge_z = deck_z + div(deck_sep, N::fl(2.))?;
    ns.set("HINGE_Z", hinge_z.val())?;
    let upper_z = deck_z + deck_sep;
    ns.set("UPPER_Z", upper_z.val())?;
    ns.set("FOLD_AXIS", Val::Tuple(vec![tup([N::fl(0.), hinge_y, hinge_z]), tup([N::fl(1.), hinge_y, hinge_z])]))?;
    ns.def(rt, "fold_pt", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["p"], &[])?;
        state(rt)?.fold_pt_val(&a.req("p")?)
    })?;
    ns.def(rt, "fold_dir", |_, args, kw| {
        let mut a = py::bind(args, kw, &["d"], &[])?;
        fold_dir_val(&a.req("d")?)
    })?;
    ns.set("BEND_R", min_bend_val.clone())?;
    let bend_y = tee_run + valve_len;
    ns.set("BEND_Y", bend_y.val())?;
    ns.set("BENT", py::dict(BENT.iter().map(|n| (*n, upper_z.val()))))?;
    ns.set("SOURCE_TRAVEL", fl(SOURCE_TRAVEL))?;
    ns.set("SOURCE_JOG", fl(SOURCE_JOG))?;
    ns.set("SOURCE_SPREAD", py::dict(SOURCE_SPREAD.iter().map(|(n, v)| (*n, fl(*v)))))?;
    ns.set("SOURCE_SLACK", fl(SOURCE_SLACK))?;
    ns.set("HAIRPIN_OUT", fl(HAIRPIN_OUT))?;
    ns.set("HAIRPIN_TILT", fl(HAIRPIN_TILT))?;
    ns.def(rt, "two_arc_floor", |_, args, kw| {
        let mut a = py::bind(args, kw, &["r", "jog"], &[])?;
        Ok(fl(two_arc_floor(a.f64("r")?, a.f64("jog")?)?))
    })?;
    ns.def(rt, "sbend_solve", |_, args, kw| {
        let mut a = py::bind(args, kw, &["r", "travel", "jog"], &[])?;
        let (r, travel, jog) = (N::of(&a.req("r")?)?, N::of(&a.req("travel")?)?, N::of(&a.req("jog")?)?);
        let (th, s) = sbend_solve(r, travel, jog)?;
        Ok(ftup2(th, s))
    })?;
    ns.def(rt, "source_offset", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        let (x, y) = state(rt)?.source_offset(&name_of(&a.req("name")?)?)?;
        Ok(ftup2(x, y))
    })?;
    ns.def(rt, "step_cross", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        let (x, y) = state(rt)?.step_cross(&name_of(&a.req("name")?)?)?;
        Ok(ftup2(x, y))
    })?;
    ns.def(rt, "hairpin_back", |_, args, kw| {
        let mut a = py::bind(args, kw, &["r", "travel", "jog"], &[])?;
        Ok(fl(hairpin_back(a.f64("r")?, a.f64("travel")?, a.f64("jog")?)?))
    })?;
    ns.def(rt, "source_valve_shift", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        let (x, y) = state(rt)?.source_valve_shift(&name_of(&a.req("name")?)?)?;
        Ok(ftup2(x, y))
    })?;
    ns.def(rt, "source_cross", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        let (x, y) = state(rt)?.source_cross(&name_of(&a.req("name")?)?)?;
        Ok(ftup2(x, y))
    })?;
    ns.def(rt, "source_step", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        let (th, s, length) = state(rt)?.source_step(&name_of(&a.req("name")?)?)?;
        Ok(py::ftuple(&[th, s, length]))
    })?;

    // SHIFT: each body's pack translation, in the order its updates first name it.
    let body_x = |name: &str| bodies.iter().find(|b| b.name == name).map(|b| b.x).ok_or_else(|| missing(name));
    let mut shift: Vec<(&'static str, V3)> = Vec::new();
    let put = |shift: &mut Vec<(&'static str, V3)>, name: &'static str, v: V3| {
        if let Some(row) = shift.iter_mut().find(|r| r.0 == name) {
            row.1 = v;
        } else {
            shift.push((name, v));
        }
    };
    let get = |shift: &Vec<(&'static str, V3)>, name: &str| shift.iter().find(|r| r.0 == name).map(|r| r.1);
    for (name, spread) in SOURCE_SPREAD {
        shift.push((name, fv3([spread.copysign(body_x(name)?.f()), -SOURCE_JOG, SOURCE_TRAVEL])));
    }
    for name in FORE_VALVES {
        put(&mut shift, name, fv3([0., FORE_VALVE_RISE, 0.]));
    }
    for name in JUNCTIONS {
        put(&mut shift, name, [N::fl(0.), -carrier_drop, N::fl(0.)]);
    }
    for name in ["V-G", "V-J"] {
        put(&mut shift, name, fv3([-outer_aft_inset.f().copysign(body_x(name)?.f()), 0., 0.]));
    }
    let mut last = ("", fv3([0., 0., 0.]));
    for name in ["V-C", "V-D", "V-G", "V-J", "Y-A", "Y-B"] {
        let d = get(&shift, name).unwrap_or(fv3([0., 0., 0.]));
        last = (name, d);
        put(&mut shift, name, [d[0], d[1] + N::fl(AFT_PACK_RISE), d[2]]);
    }
    for name in ["V-A", "V-B", "Y-A", "Y-B", "V-C", "V-D"] {
        let d = get(&shift, name).unwrap_or(fv3([0., 0., 0.]));
        last = (name, d);
        put(&mut shift, name, [d[0], d[1] - inner_limb_drop, d[2]]);
    }
    for name in ["V-G", "V-J"] {
        let d = get(&shift, name).ok_or_else(|| missing(name))?;
        last = (name, d);
        put(&mut shift, name, [d[0], d[1] - inner_limb_drop, d[2]]);
    }
    ns.set("SHIFT", Val::dict(shift.iter().map(|(n, v)| (s(*n), tup(*v))).collect()))?;
    ns.set("_name", s(last.0))?;
    ns.set("_dx", last.1[0].val())?;
    ns.set("_dy", last.1[1].val())?;
    ns.set("_dz", last.1[2].val())?;

    let k = K {
        valve_len,
        valve_pitch,
        valve_port_z,
        tee_run,
        tee_branch,
        tube_d,
        min_bend,
        barb_pitch,
        barb_inset,
        inner_limb_drop,
        fore_stub_gap,
        tip_from_fore,
        pump_stub_projection,
        barb_plate_berth,
        pump_barb_z,
        pump_y,
        barb_standoff,
        limb_pitch,
        inner_x,
        pump_dx,
        outer_x,
        outer_aft_inset,
        limb_step,
        barb_lead,
        deck_z,
        hinge_y,
        deck_sep,
        hinge_z,
        upper_z,
        bend_y,
        carrier_connected,
        pump_station_lead,
        pump_station_drop,
        kp_cx: constant(&kp, "cx")?.1,
        kp_head_front_z: constant(&kp, "head_front_z")?.1,
        kp_body_y_face: constant(&kp, "body_y_face")?.1,
        outlet_y: constant(&ydiv, "OUTLET_Y")?.1,
        quarter_len: div(N::fl(PI) * min_bend, N::fl(2.))?,
    };
    let st = rt.keep(
        MODULE,
        State {
            ns: ns.clone(),
            routing,
            returns,
            enc_if,
            stock,
            here,
            hw,
            tee_step,
            elbow_step,
            kamoer_step,
            c_coil,
            c_valve,
            c_tee,
            c_head,
            c_boss,
            c_motor,
            k,
            bodies,
            shift,
            types: OnceCell::new(),
            fore_deck: OnceCell::new(),
            tee_axis_y: OnceCell::new(),
            tube_id: OnceCell::new(),
            kit: OnceCell::new(),
            tee_ports: RefCell::new(Vec::new()),
            plumbing: RefCell::new(None),
            s_bends: RefCell::new(Vec::new()),
            runs: OnceCell::new(),
            fore_stubs: OnceCell::new(),
            fore_stub_exposed: OnceCell::new(),
            mouths: OnceCell::new(),
        },
    );

    ns.def(rt, "bend_pt", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["p", "z0"], &[])?;
        let p = a.req("p")?;
        state(rt)?.bend_pt_val(&p, N::of(&a.req("z0")?)?)
    })?;
    ns.def(rt, "bend_dir", |_, args, kw| {
        let mut a = py::bind(args, kw, &["d"], &[])?;
        bend_dir_val(&a.req("d")?)
    })?;
    ns.def(rt, "hairpin_flat", |_, args, kw| {
        let mut a = py::bind(args, kw, &["r", "across", "back"], &[])?;
        let (r, across, back) = (a.f64("r")?, a.f64("across")?, N::of(&a.req("back")?)?);
        Ok(legs_val(&hairpin_flat(r, across, back)?))
    })?;
    ns.def(rt, "hairpins_drawn", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(Val::Int(state(rt)?.hairpins_drawn()?))
    })?;
    ns.def(rt, "sbend_flat", |_, args, kw| {
        let mut a = py::bind(args, kw, &["r", "travel", "jog"], &[])?;
        let (r, travel, jog) = (N::of(&a.req("r")?)?, N::of(&a.req("travel")?)?, N::of(&a.req("jog")?)?);
        Ok(legs_val(&sbend_flat(r, travel, jog)?))
    })?;
    ns.def(rt, "fore_deck_aft_shift", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(state(rt)?.fore_deck_aft_shift()?.val())
    })?;
    ns.def(rt, "fixed_aft_shift", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        match a.req("name")? {
            Val::Str(name) => Ok(state(rt)?.fixed_aft_shift(&name)?.val()),
            _ => Ok(fl(AFT_DECK_AFT_SHIFT)),
        }
    })?;
    ns.def(rt, "enclosure_point", |_, args, kw| {
        let mut a = py::bind(args, kw, &["point"], &[])?;
        enc_pt_val(&a.req("point")?)
    })?;
    ns.def(rt, "authoring_point", |_, args, kw| {
        let mut a = py::bind(args, kw, &["point"], &[])?;
        auth_pt_val(&a.req("point")?)
    })?;
    ns.def(rt, "enclosure_axis", |_, args, kw| {
        let mut a = py::bind(args, kw, &["axis"], &[])?;
        swap_axis_val(&a.req("axis")?)
    })?;
    ns.def(rt, "authoring_axis", |_, args, kw| {
        let mut a = py::bind(args, kw, &["axis"], &[])?;
        swap_axis_val(&a.req("axis")?)
    })?;
    ns.def(rt, "pump_wall_fore_y", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(state(rt)?.pump_wall_fore_y()?.val())
    })?;
    ns.set("_plumbing_cache", Val::None)?;
    ns.def(rt, "pump_plumbing", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        let st = state(rt)?;
        let cached = st.ns.get("_plumbing_cache")?;
        if !matches!(cached, Val::None) {
            return Ok(cached);
        }
        st.plumbing()?;
        st.ns.get("_plumbing_cache")
    })?;
    ns.def(rt, "_tee_ports", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        state(rt)?.tee_ports_val(&name_of(&a.req("name")?)?)
    })?;
    ns.def(rt, "fixed_tee_centers", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["carry"], &[])?;
        let carry = a.some("carry");
        let st = state(rt)?;
        let out = Val::dict(vec![]);
        for name in JUNCTIONS {
            let centre = tup(auth_pt(st.tee_ports(name)?.centre));
            let value = match &carry {
                Some(carry) => py::call(carry, vec![Val::Tuple(vec![centre, py::ftuple(&[0., 0., 1.])])])?.get(Val::Int(0))?,
                None => centre,
            };
            out.set(s(name), value)?;
        }
        Ok(out)
    })?;
    ns.def(rt, "_posed", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name", "p", "d", "carrier_offset"], &[])?;
        let name = name_of(&a.req("name")?)?;
        let (mut p, mut d) = (a.req("p")?, a.req("d")?);
        let st = state(rt)?;
        let b = st.body(&name)?;
        if b.fold {
            (p, d) = (st.fold_pt_val(&p)?, fold_dir_val(&d)?);
        }
        if is_bent(&name) {
            (p, d) = (st.bend_pt_val(&p, st.k.upper_z)?, bend_dir_val(&d)?);
        }
        let mut p = index3(&p)?;
        if let Some(sh) = st.shift_of(&name) {
            p = add3(p, sh);
        }
        if is_junction(&name) {
            p = [p[0], p[1], p[2] + N::fl(CARRIER_DATUM_SHIFT) + st.k.carrier_connected];
        }
        p = [p[0], p[1], p[2] + st.fixed_aft_shift(&name)?];
        Ok(Val::Tuple(vec![tup(p), d]))
    })?;
    ns.def(rt, "port", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name", "end", "carrier_offset"], &[])?;
        let (name, end) = (name_of(&a.req("name")?)?, a.req("end")?);
        let st = state(rt)?;
        Ok(tup(port_of(&st, &name, &end)?.0))
    })?;
    ns.def(rt, "port_axis", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name", "end", "carrier_offset"], &[])?;
        let (name, end) = (name_of(&a.req("name")?)?, a.req("end")?);
        let st = state(rt)?;
        Ok(tup(port_of(&st, &name, &end)?.1))
    })?;
    ns.def(rt, "branch_port", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name", "carrier_offset"], &[])?;
        let (p, d) = state(rt)?.branch_port(&name_of(&a.req("name")?)?)?;
        Ok(Val::Tuple(vec![tup(p), tup(d)]))
    })?;
    ns.set("JOINS", Val::dict(vec![]))?;
    ns.def(rt, "_cross", |_, args, kw| {
        let mut a = py::bind(args, kw, &["a", "b"], &[])?;
        Ok(tup(cross(index3(&a.req("a")?)?, index3(&a.req("b")?)?)))
    })?;
    ns.def(rt, "elbow_pose", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["gate", "side"], &[])?;
        let (gate, side) = (name_of(&a.req("gate")?)?, N::of(&a.req("side")?)?);
        let st = state(rt)?;
        let b = st.body(&gate)?;
        let at = [b.x, b.back + N::fl(ELBOW_LEG), st.k.deck_z];
        let bend = st.ns.get("ELBOW_BEND").map_err(|_| anyhow!("manifold_layout: unknown name ELBOW_BEND"))?;
        let corner = st.bend_pt(at, N::of(&bend)?);
        let mouth = [corner[0] + side * N::fl(ELBOW_LEG), corner[1], corner[2]];
        let (x_dir, z_dir) = (bend_dir([N::fl(0.), N::fl(0.), side]), bend_dir([side, N::fl(0.), N::fl(0.)]));
        let leg1 = cross(z_dir, x_dir);
        let seat = [0, 1, 2].map(|i| corner[i] + leg1[i] * N::fl(ELBOW_LEG));
        Ok(Val::Tuple(vec![tup(corner), tup(mouth), tup(x_dir), tup(z_dir), tup(seat)]))
    })?;
    ns.def(rt, "_authored", |_, args, kw| {
        let mut a = py::bind(args, kw, &["segment"], &[])?;
        Ok(authored(&a.req("segment")?)?.val())
    })?;
    ns.def(rt, "lower_links", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        let stations = state(rt)?.plumbing()?;
        let out = Val::dict(vec![]);
        for (cid, name) in LOWER_CONNECTIONS {
            out.set(Val::Int(cid), Val::Tuple(stations[junction_index(name)?].tube.iter().map(Seg::val).collect()))?;
        }
        Ok(out)
    })?;
    ns.def(rt, "lower_link_length", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["cid"], &[])?;
        let cid = a.req("cid")?;
        let stations = state(rt)?.plumbing()?;
        for (key, name) in LOWER_CONNECTIONS {
            if interop::eq(&Val::Int(key), &cid)? {
                return Ok(stations[junction_index(name)?].cut.clone());
            }
        }
        bail!("missing key {}", cid.repr()?)
    })?;
    ns.def(rt, "_junction_at_author_x", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["x"], &[])?;
        Ok(s(state(rt)?.junction_at_author_x(N::of(&a.req("x")?)?)?))
    })?;
    ns.def(rt, "return_exposed", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["x"], &[])?;
        state(rt)?.return_exposed(N::of(&a.req("x")?)?)
    })?;
    ns.def(rt, "return_cut", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["x"], &[])?;
        state(rt)?.return_cut(N::of(&a.req("x")?)?)
    })?;
    ns.def(rt, "_fore_segments", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["a", "b"], &[])?;
        let (from, to) = (unpack3(&a.req("a")?)?, unpack3(&a.req("b")?)?);
        Ok(Val::Tuple(state(rt)?.fore_segments(from, to)?.iter().map(Seg::val).collect()))
    })?;
    ns.def(rt, "fore_stub_length", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["a", "b", "radius"], &[])?;
        let (from, to) = (unpack3(&a.req("a")?)?, unpack3(&a.req("b")?)?);
        Ok(state(rt)?.fore_stub_length(from, to)?.val())
    })?;
    ns.def(rt, "stub_tip", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        Ok(tup(state(rt)?.stub_tip(&name_of(&a.req("name")?)?)?))
    })?;
    ns.def(rt, "factory_tail_runs", |_, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(Val::dict(vec![]))
    })?;
    ns.def(rt, "factory_tail_length", |_, args, kw| {
        py::bind(args, kw, &["name"], &[])?;
        Ok(fl(0.))
    })?;
    ns.def(rt, "runs", |rt, args, kw| {
        py::bind(args, kw, &["carrier_offset"], &[])?;
        Ok(pairs_val(state(rt)?.runs()?))
    })?;
    let runs = st.runs()?;
    ns.set("RUNS", pairs_val(runs))?;
    ns.set("BARB_TUBE_LEN", pump_stub_projection.val())?;
    ns.set("PUMP_TUBE_PROJECTION", pump_stub_projection.val())?;
    ns.def(rt, "fore_stubs", |rt, args, kw| {
        py::bind(args, kw, &["carrier_offset"], &[])?;
        Ok(pairs_val(state(rt)?.fore_stubs()?))
    })?;
    ns.set("FORE_STUBS", pairs_val(st.fore_stubs()?))?;
    ns.set("FORE_STUB_EXPOSED", st.fore_stub_exposed()?.val())?;
    ns.def(rt, "turns_meet", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        let meets = state(rt)?.turns_meet()?;
        Ok(Val::list(meets.into_iter().map(|(cid, d)| Val::Tuple(vec![Val::Int(cid), d.val()])).collect()))
    })?;
    ns.set(
        "SEGMENTS",
        Val::list(SEGMENTS.iter().map(|(cid, a, b, how)| Val::Tuple(vec![Val::Int(*cid), s(*a), s(*b), s(*how)])).collect()),
    )?;
    ns.set("QUARTERS", Val::dict(st.quarters().iter().map(|(cid, x, z)| (Val::Int(*cid), Val::Tuple(vec![x.val(), z.val()]))).collect()))?;
    ns.set("QUARTER_LEN", st.k.quarter_len.val())?;
    ns.set("SBENDS", Val::dict(SBENDS.iter().map(|(cid, v)| (Val::Int(*cid), s(*v))).collect()))?;
    let mut steps = Vec::new();
    for (_, v) in SBENDS {
        let c = st.source_cross(v)?;
        let across = num::hypot2(c.0, c.1);
        let floor = two_arc_floor(min_bend.f(), across)?;
        steps.push(format!(
            "{v} steps {} across, whose floor is {} — {} mm of travel against the {} the step holds",
            num::fmt(across, ".2f"),
            num::fmt(floor, ".2f"),
            num::fmt(SOURCE_TRAVEL - floor, "+.2f"),
            num::fmt(SOURCE_SLACK, "g")
        ));
    }
    let note = steps.join("; ")
        + ". `SOURCE_JOG` is the lever: the floor climbs with the cross, and the travel is the pack's to give, not this run's.";
    super::_stated_bounds::state_bound(
        rt,
        s("source-step-room"),
        s("Both source runs step on two arcs alone"),
        s(format!("the travel over the two-arc floor by {} mm on each channel", num::fmt(SOURCE_SLACK, "g"))),
        &Val::Bool(st.hairpins_drawn()? == 0),
        &s(note),
    )?;
    ns.set("LOWER_CONNECTIONS", Val::dict(LOWER_CONNECTIONS.iter().map(|(cid, n)| (Val::Int(*cid), s(*n))).collect()))?;
    let mut spine = Vec::new();
    for (cid, frm, _, how) in SEGMENTS {
        if how == "spine" {
            let body = frm.rsplit_once('-').map_or(frm, |(head, _)| head);
            let limb = st.body(body)?.limb;
            let l = LIMBS.iter().find(|l| l.limb == limb).ok_or_else(|| missing(limb))?;
            spine.push((Val::Int(cid), lay.limb_x(l).val()));
        }
    }
    ns.set("SPINE", Val::dict(spine))?;
    ns.set("MOUTHS", Val::list(st.mouths()?.iter().map(Mouth::val).collect()))?;
    ns.def(rt, "_sum", |_, args, kw| {
        let mut a = py::bind(args, kw, &["a", "b"], &[])?;
        zip_op("add", &a.req("a")?, &a.req("b")?)
    })?;
    ns.def(rt, "_matrix", |_, args, kw| {
        let mut a = py::bind(args, kw, &["origin", "x_dir", "z_dir", "carry"], &[])?;
        let origin = a.req("origin")?;
        let x_dir = a.opt("x_dir").unwrap_or_else(|| py::ftuple(&[1., 0., 0.]));
        let z_dir = a.opt("z_dir").unwrap_or_else(|| py::ftuple(&[0., 0., 1.]));
        matrix_val(origin, x_dir, z_dir, a.some("carry"))
    })?;
    ns.def(rt, "_source_segments", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name", "start", "travel"], &[])?;
        let name = name_of(&a.req("name")?)?;
        let (start, travel) = (index3(&a.req("start")?)?, N::of(&a.req("travel")?)?);
        state(rt)?.source_segments(&name, start, travel)
    })?;
    ns.def(rt, "numbers", |rt, args, kw| {
        let mut a = py::bind(args, kw, &[], &["prepare_sources"])?;
        let prepare = a.bool_or("prepare_sources", true)?;
        state(rt)?.numbers(rt, prepare)
    })?;
    ns.def(rt, "_segment_numbers", |_, args, kw| {
        let mut a = py::bind(args, kw, &["segment"], &[])?;
        let segment = a.req("segment")?;
        let kind = segment.get(s("kind"))?;
        let arc = interop::eq(&segment.get(s("kind"))?, &s("arc"))?;
        let keys: &[&str] = if arc { &["start_mm", "midpoint_mm", "end_mm"] } else { &["start_mm", "end_mm"] };
        let points = keys.iter().map(|key| segment.get(s(*key))).collect::<Result<Vec<_>>>()?;
        Ok(py::dict([("kind", kind), ("points", Val::list(points))]))
    })?;
    for (field, lo, hi) in [("Extents.xlen", "xmin", "xmax"), ("Extents.ylen", "ymin", "ymax"), ("Extents.zlen", "zmin", "zmax")] {
        ns.def(rt, field, move |_, args, kw| {
            let mut a = py::bind(args, kw, &["self"], &[])?;
            let me = a.req("self")?;
            Ok((N::of(&me.attr(hi)?)? - N::of(&me.attr(lo)?)?).val())
        })?;
    }
    ns.def(rt, "Extents.escape", |_, args, kw| {
        let mut a = py::bind(args, kw, &["self"], &[])?;
        let (axis, d) = escape(&six(&extents_fields(&a.req("self")?)?)?);
        Ok(Val::Tuple(vec![s(axis), d.val()]))
    })?;
    ns.def(rt, "Extents.__str__", |_, args, kw| {
        let mut a = py::bind(args, kw, &["self"], &[])?;
        Ok(s(extents_text(&extents_fields(&a.req("self")?)?)?))
    })?;
    let (extents, clash) = st.types(rt)?;
    ns.set("Extents", extents.clone())?;
    ns.set("Clash", clash.clone())?;
    ns.set("TWINS", Val::list(TWINS.iter().map(|(a, b)| Val::Tuple(vec![s(*a), s(*b)])).collect()))?;
    ns.def(rt, "mirror_off", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        let off = state(rt)?.mirror_off()?;
        Ok(Val::list(off.into_iter().map(|(a, b, dx, dy)| Val::Tuple(vec![s(a), s(b), dx.val(), dy.val()])).collect()))
    })?;
    ns.def(rt, "dist", |_, args, kw| {
        let mut a = py::bind(args, kw, &["a", "b"], &[])?;
        Ok(dist(index3(&a.req("a")?)?, index3(&a.req("b")?)?).val())
    })?;
    ns.def(rt, "skew_deg", |_, args, kw| {
        let mut a = py::bind(args, kw, &["a", "b", "axis"], &[])?;
        let (from, to, axis) = (index3(&a.req("a")?)?, index3(&a.req("b")?)?, index3(&a.req("axis")?)?);
        let v = sub3(to, from);
        let m = pow(v.iter().fold(N::int(0), |t, c| t + *c * *c), N::fl(0.5));
        let dot = div((0..3).fold(N::int(0), |t, i| t + v[i] * axis[i]), m)?;
        Ok(fl(num::degrees(acos(nmax(N::fl(-1.), nmin(N::fl(1.), dot)).f())?)))
    })?;
    ns.def(rt, "report", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["assy", "measurements"], &[])?;
        let measurements = a.req("measurements")?;
        Ok(state(rt)?.report(rt, &measurements)?.0)
    })?;
    ns.def(rt, "_write_readme", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["r"], &[])?;
        let data = report_data(&a.req("r")?)?;
        state(rt)?.write_readme(&data)?;
        rt.print("-> README.md".into())?;
        Ok(Val::None)
    })?;
    ns.def(rt, "main", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        main(rt)
    })?;
    Ok(())
}

/// A named pair of points as the namespace holds `RUNS` and `FORE_STUBS`.
fn pairs_val(rows: &[(&'static str, V3, V3)]) -> Val {
    Val::dict(rows.iter().map(|(key, a, b)| (s(*key), Val::Tuple(vec![tup(*a), tup(*b)]))).collect())
}
/// `port`'s and `port_axis`'s pose for a caller's `end`: any key of the body's row.
fn port_of(st: &State, name: &str, end: &Val) -> Result<(V3, V3)> {
    let front = interop::eq(end, &s("front"))?;
    if is_junction(name) {
        return Ok((st.port(name, front)?, st.port_axis(name, front)?));
    }
    let b = st.body(name)?;
    let y = N::of(&b.field(end)?)?;
    let d = if front { [0., -1., 0.] } else { [0., 1., 0.] };
    st.posed(name, [b.x, y, st.k.deck_z], fv3(d))
}
fn fold_dir_val(d: &Val) -> Result<Val> {
    let r = items3(d)?;
    Ok(Val::Tuple(vec![r[0].clone(), neg(&r[1])?, neg(&r[2])?]))
}
fn bend_dir_val(d: &Val) -> Result<Val> {
    let r = items3(d)?;
    Ok(Val::Tuple(vec![r[0].clone(), neg(&r[2])?, r[1].clone()]))
}
/// `tuple(x <op> y for x, y in zip(a, b))` of a caller's values.
fn zip_op(op: &str, a: &Val, b: &Val) -> Result<Val> {
    let (a, b) = (a.iter()?, b.iter()?);
    Ok(Val::Tuple(a.into_iter().zip(b).map(|(x, y)| interop::binary(op, x, y)).collect::<Result<_>>()?))
}
/// `_matrix` of a caller's frame, carried by a caller's function.
fn matrix_val(origin: Val, x_dir: Val, z_dir: Val, carry: Option<Val>) -> Result<Val> {
    let y_dir = tup(cross(index3(&z_dir)?, index3(&x_dir)?));
    let (mut origin, mut x_dir, mut y_dir, mut z_dir) = (origin, x_dir, y_dir, z_dir);
    if let Some(carry) = carry {
        let p = py::call(&carry, vec![origin.clone()])?;
        x_dir = zip_op("sub", &py::call(&carry, vec![zip_op("add", &origin, &x_dir)?])?, &p)?;
        y_dir = zip_op("sub", &py::call(&carry, vec![zip_op("add", &origin, &y_dir)?])?, &p)?;
        z_dir = zip_op("sub", &py::call(&carry, vec![zip_op("add", &origin, &z_dir)?])?, &p)?;
        origin = p;
    }
    let rows = (0..3)
        .map(|k| {
            let k = Val::Int(k);
            Ok(Val::list(vec![x_dir.get(k.clone())?, y_dir.get(k.clone())?, z_dir.get(k.clone())?, origin.get(k)?]))
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(Val::list(rows))
}
