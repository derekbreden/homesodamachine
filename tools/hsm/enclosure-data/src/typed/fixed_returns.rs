//! Station datums for the four pump tees, the tee wall's fore band and the fittings and tubes
//! that join them.
//!
//! Coordinates are enclosure millimetres: +Y points inward and +Z points up. Each pump port
//! feeds one purchased PP0208E tee, its branch toward the pump and its run upright. The fore
//! valve stands over the run on one short straight tube. The lower return reaches the rear valve's
//! bottom port: a trimmed NeoFit stem elbow in the tee's lower collet, one tube, and a
//! second stem elbow in the valve.
//!
//! THE FORE BAND'S AFT FACE IS THE BORE FACE. Each tee's branch bore opens on it, and the tee
//! stands with its fixed branch barrel just aft of it. The branch collet stands extended in its
//! recess ahead of that face and grips the pump tube like any push-fit; the tube is pushed home
//! once, at the factory, to the tee's stop.
//!
//! This module holds geometry data only; the dock's solids and the manifold read the same
//! figures.
//!
//! Typed API: [`plate_aft_y`], [`tee_axis_y`], [`fore_valve_axis_y`], [`tip_y`], [`tee_ports`],
//! [`elbow_return`], [`s_bend`], [`station`], [`layouts`], [`sweep`] and [`tube`]; each record's
//! `val()` is the value the namespace function returns. Coordinates are [`Num`]s, so an int a
//! caller passes in comes back out an int where the runtime keeps it one.
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result, bail};
use hsm_documents::interop;
use std::cell::OnceCell;
use std::cmp::Ordering;
use std::path::Path;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "fixed_returns";

/// A point or direction in enclosure millimetres.
pub type V3 = [Num; 3];

const TUBE_ID: f64 = 4.30;
/// Seat depths: the valve's layout estimate. Actual fully seated marks govern factory cuts.
const VALVE_INSERTION_NOMINAL: f64 = 12.0;
/// `s_bend`'s default `direction`.
const UP: V3 = [Num::F(0.0), Num::F(0.0), Num::F(1.0)];

/// The module's figures: the tee's and the stem elbow's, and the fore band's built on them.
struct State {
    elbow: Val,
    tube_od: Val,
    plate_t: Num,
    bore_face_to_axis: Num,
    run_face: Num,
    tip_from_fore: Num,
    run_insertion: Num,
    elbow_drop: Num,
    /// The stem elbow's figures `elbow_return` reads, read at its first call.
    fitting: OnceCell<Fitting>,
}

struct Fitting {
    stem_length: Num,
    socket_mouth_reach: Num,
    socket_insertion: Num,
    collar_od: Num,
}

impl State {
    fn fitting(&self) -> Result<&Fitting> {
        if self.fitting.get().is_none() {
            let read = |name: &str| -> Result<Num> { Num::of(&self.elbow.attr(name)?) };
            let fitting = Fitting {
                stem_length: read("STEM_LENGTH")?,
                socket_mouth_reach: read("SOCKET_MOUTH_REACH")?,
                socket_insertion: read("SOCKET_INSERTION")?,
                collar_od: read("COLLAR_OD")?,
            };
            let _ = self.fitting.set(fitting);
        }
        Ok(self.fitting.get().expect("the elbow's figures"))
    }
}

fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

// The runtime's arithmetic on the module's numbers.

fn order(a: Num, b: Num) -> Result<Ordering> {
    a.f().partial_cmp(&b.f()).context("unordered numeric comparison")
}
fn le(a: Num, b: Num) -> Result<bool> {
    Ok(!order(a, b)?.is_gt())
}
fn lt(a: Num, b: Num) -> Result<bool> {
    Ok(order(a, b)?.is_lt())
}
/// `max(a, b)`: the first of equal values wins.
fn max(a: Num, b: Num) -> Result<Num> {
    Ok(if order(b, a)?.is_gt() { b } else { a })
}
/// `min(a, b)`: the first of equal values wins.
fn min(a: Num, b: Num) -> Result<Num> {
    Ok(if order(b, a)?.is_lt() { b } else { a })
}
/// `a / b`.
fn div(a: Num, b: Num) -> Result<Num> {
    if b.f() == 0. {
        bail!("division by zero");
    }
    Ok(a.div(b))
}
/// `math.sqrt(x)`.
fn sqrt(x: Num) -> Result<f64> {
    let x = x.f();
    if !(x >= 0.) {
        bail!("math domain error");
    }
    Ok(x.sqrt())
}
/// `sum(values)`: added in order from the int 0.
fn sum(values: impl IntoIterator<Item = Num>) -> Num {
    values.into_iter().fold(Num::I(0), Num::add)
}

fn add(a: &V3, b: &V3) -> V3 {
    [a[0].add(b[0]), a[1].add(b[1]), a[2].add(b[2])]
}
fn scale(a: &V3, k: Num) -> V3 {
    [a[0].mul(k), a[1].mul(k), a[2].mul(k)]
}
fn unit(v: &V3) -> Result<V3> {
    let n = sqrt(sum(v.iter().map(|c| c.mul(*c))))?;
    Ok(scale(v, div(Num::F(1.0), Num::F(n))?))
}

fn v3(v: &V3) -> Val {
    Num::vals(v)
}
/// A sequence's first three items, indexed as `v[i]` reads them.
fn indexed3(v: &Val) -> Result<V3> {
    Ok([
        Num::of(&v.get(Val::Int(0))?)?,
        Num::of(&v.get(Val::Int(1))?)?,
        Num::of(&v.get(Val::Int(2))?)?,
    ])
}
fn nums(v: &Val) -> Result<Vec<Num>> {
    v.iter()?.iter().map(Num::of).collect()
}

/// One centreline segment: a straight, or a three-point arc.
#[derive(Clone, Debug)]
pub enum Segment {
    Line { start: V3, end: V3, tangent: V3, length: f64 },
    Arc {
        start: V3,
        midpoint: V3,
        end: V3,
        radius: f64,
        sweep_degrees: f64,
        start_tangent: V3,
        end_tangent: V3,
        length: f64,
    },
}
impl Segment {
    pub fn length(&self) -> f64 {
        match self {
            Segment::Line { length, .. } | Segment::Arc { length, .. } => *length,
        }
    }
    pub fn start(&self) -> &V3 {
        match self {
            Segment::Line { start, .. } | Segment::Arc { start, .. } => start,
        }
    }
    pub fn end(&self) -> &V3 {
        match self {
            Segment::Line { end, .. } | Segment::Arc { end, .. } => end,
        }
    }
    pub fn val(&self) -> Val {
        match self {
            Segment::Line { start, end, tangent, length } => py::dict([
                ("kind", py::s("line")),
                ("start_mm", v3(start)),
                ("end_mm", v3(end)),
                ("start_tangent", v3(tangent)),
                ("end_tangent", v3(tangent)),
                ("length_mm", Val::Float(*length)),
            ]),
            Segment::Arc { start, midpoint, end, radius, sweep_degrees, start_tangent, end_tangent, length } => py::dict([
                ("kind", py::s("arc")),
                ("start_mm", v3(start)),
                ("midpoint_mm", v3(midpoint)),
                ("end_mm", v3(end)),
                ("radius_mm", Val::Float(*radius)),
                ("sweep_degrees", Val::Float(*sweep_degrees)),
                ("start_tangent", v3(start_tangent)),
                ("end_tangent", v3(end_tangent)),
                ("length_mm", Val::Float(*length)),
            ]),
        }
    }
}
fn segments_val(segments: &[Segment]) -> Val {
    py::tuple(segments.iter().map(Segment::val))
}
/// `sum(s["length_mm"] for s in segments)`.
fn developed(segments: &[Segment]) -> Num {
    sum(segments.iter().map(|s| Num::F(s.length())))
}

/// A collet face: its point and outward axis.
#[derive(Clone, Debug)]
pub struct Port {
    pub point: V3,
    pub axis: V3,
}
impl Port {
    pub fn val(&self) -> Val {
        py::dict([("point", v3(&self.point)), ("axis", v3(&self.axis))])
    }
}

/// The tee's centre and its three collet faces.
#[derive(Clone, Debug)]
pub struct TeePorts {
    pub centre: V3,
    pub branch: Port,
    pub upper: Port,
    pub lower: Port,
}
impl TeePorts {
    pub fn val(&self) -> Val {
        py::dict([
            ("centre", v3(&self.centre)),
            ("branch", self.branch.val()),
            ("upper", self.upper.val()),
            ("lower", self.lower.val()),
        ])
    }
}

/// One `elbows` row: the elbow's crossing, the way its socket opens, its stem's length past the
/// shoulder and how much of that stands outside the collet.
#[derive(Clone, Debug)]
pub struct ElbowSeat {
    pub crossing: V3,
    pub socket: V3,
    pub stem: Num,
    pub showing: Num,
}
impl ElbowSeat {
    pub fn val(&self) -> Val {
        py::dict([
            ("crossing", v3(&self.crossing)),
            ("socket", v3(&self.socket)),
            ("stem", self.stem.val()),
            ("showing", self.showing.val()),
        ])
    }
}

/// The lower return: a stem elbow in each collet and one tube between them.
#[derive(Clone, Debug)]
pub struct Return {
    pub elbows: [ElbowSeat; 2],
    pub tube: Vec<Segment>,
    pub exposed_mm: Num,
    pub cut_mm: Num,
    pub floor_z: Num,
}
impl Return {
    pub fn val(&self) -> Val {
        py::dict([
            ("elbows", py::tuple(self.elbows.iter().map(ElbowSeat::val))),
            ("tube", segments_val(&self.tube)),
            ("exposed_mm", self.exposed_mm.val()),
            ("cut_mm", self.cut_mm.val()),
            ("floor_z", self.floor_z.val()),
        ])
    }
}

/// One pump port's tee, its fore valve's tube and its lower return to the rear valve.
#[derive(Clone, Debug)]
pub struct Station {
    pub tee: TeePorts,
    /// `dict(upper_port)`.
    pub upper_target: Val,
    /// `dict(return_port)`.
    pub return_target: Val,
    pub upper_tube: Vec<Segment>,
    pub lower: Return,
    pub upper_exposed_mm: Num,
}
impl Station {
    pub fn val(&self) -> Val {
        py::dict([
            ("tee", self.tee.val()),
            ("upper_target", self.upper_target.clone()),
            ("return_target", self.return_target.clone()),
            ("upper_tube", segments_val(&self.upper_tube)),
            ("return", self.lower.val()),
            ("upper_exposed_mm", self.upper_exposed_mm.val()),
        ])
    }
}

fn line(start: &V3, direction: &V3, length: Num) -> Segment {
    Segment::Line { start: *start, end: add(start, &scale(direction, length)), tangent: *direction, length: length.f() }
}

/// The bore face: the fore band's aft face.
pub fn plate_aft_y(rt: &Rt, fore_y: Num) -> Result<Num> {
    Ok(fore_y.add(state(rt)?.plate_t))
}

/// The tee's run axis in Y.
pub fn tee_axis_y(rt: &Rt, fore_y: Num) -> Result<Num> {
    Ok(plate_aft_y(rt, fore_y)?.add(state(rt)?.bore_face_to_axis))
}

/// The fore valve's port axis in Y: over its tee's run axis.
pub fn fore_valve_axis_y(rt: &Rt, fore_y: Num) -> Result<Num> {
    tee_axis_y(rt, fore_y)
}

/// The pump tube's seated tip: bottomed at the tee's stop.
pub fn tip_y(rt: &Rt, fore_y: Num) -> Result<Num> {
    Ok(fore_y.add(state(rt)?.tip_from_fore))
}

/// The tee's centre and its three collet faces, as point and outward axis.
pub fn tee_ports(rt: &Rt, fore_y: Num, x: Num, z: Num) -> Result<TeePorts> {
    let run_face = state(rt)?.run_face;
    let y = tee_axis_y(rt, fore_y)?;
    Ok(TeePorts {
        centre: [x, y, z],
        branch: Port { point: [x, plate_aft_y(rt, fore_y)?, z], axis: [Num::F(0.0), Num::F(-1.0), Num::F(0.0)] },
        upper: Port { point: [x, y, z.add(run_face)], axis: [Num::F(0.0), Num::F(0.0), Num::F(1.0)] },
        lower: Port { point: [x, y, z.sub(run_face)], axis: [Num::F(0.0), Num::F(0.0), Num::F(-1.0)] },
    })
}

/// The lower return from the tee's downward lower collet at `start` to the rear valve's
/// downward bottom collet at `end`: a stem elbow in each, one tube between them.
///
/// The tee's elbow is cut to the run collet's seat depth, so its shoulder stands on the collet
/// face and its axes cross `ELBOW_DROP` under it. The valve's elbow stands shoulder-to-collet
/// when its port is lower, with a gentle S between the parallel sockets. A higher valve
/// retains enough stem below its collet to put both sockets level. Each `elbows` row is the elbow's crossing, the
/// way its socket opens, its stem's length past the shoulder and how much of that stands
/// outside the collet.
pub fn elbow_return(rt: &Rt, start: &V3, end: &V3) -> Result<Return> {
    let st = state(rt)?;
    let ([x0, y0, z0], [x1, y1, z1]) = (*start, *end);
    let z = z0.sub(st.elbow_drop);
    let showing = max(Num::F(0.0), z1.sub(z0))?;
    let fitting = st.fitting()?;
    let spare = fitting.stem_length.sub(Num::F(VALVE_INSERTION_NOMINAL));
    let high = spare.add(Num::F(1e-09));
    if !(le(Num::F(-1e-09), showing)? && le(showing, high)?) {
        bail!(
            "the valve's collet stands {} mm off the tee's, so its elbow would show {} mm of stem below it, outside the 0 to {} mm its stem has",
            z1.sub(z0).fmt("+g"),
            showing.fmt("g"),
            spare.fmt("g"),
        );
    }
    let span = num::hypot2(x1.sub(x0).f(), y1.sub(y0).f());
    let exposed = Num::F(span).sub(Num::F(2.0).mul(fitting.socket_mouth_reach));
    if le(exposed, Num::F(0.0))? {
        bail!("the ports stand {} mm apart, closer than two elbows' sockets", num::fmt(span, "g"));
    }
    let u = unit(&[x1.sub(x0), y1.sub(y0), Num::F(0.0)])?;
    let back = [u[0].neg(), u[1].neg(), Num::F(0.0)];
    let reach = fitting.socket_mouth_reach;
    let mouth = [x0.add(u[0].mul(reach)), y0.add(u[1].mul(reach)), z];
    let rear_z = z1.sub(st.elbow_drop).sub(showing);
    let rear_mouth = [x1.sub(u[0].mul(reach)), y1.sub(u[1].mul(reach)), rear_z];
    let segments = s_bend(&mouth, &rear_mouth, &u)?;
    let developed = developed(&segments);
    Ok(Return {
        elbows: [
            ElbowSeat { crossing: [x0, y0, z], socket: u, stem: st.run_insertion, showing: Num::F(0.0) },
            ElbowSeat {
                crossing: [x1, y1, rear_z],
                socket: back,
                stem: Num::F(VALVE_INSERTION_NOMINAL).add(showing),
                showing,
            },
        ],
        tube: segments,
        exposed_mm: developed,
        cut_mm: developed.add(Num::F(2.0).mul(fitting.socket_insertion)),
        floor_z: min(z, rear_z)?.sub(fitting.collar_od.div(Num::F(2.0))),
    })
}

/// Two equal tangent arcs between parallel sockets, or a straight if they align.
pub fn s_bend(start: &V3, end: &V3, direction: &V3) -> Result<Vec<Segment>> {
    let up = unit(direction)?;
    let delta: V3 = std::array::from_fn(|i| end[i].sub(start[i]));
    let length = sum((0..3).map(|i| delta[i].mul(up[i])));
    let lateral: V3 = std::array::from_fn(|i| delta[i].sub(length.mul(up[i])));
    let offset = sqrt(sum(lateral.iter().map(|v| v.mul(*v))))?;
    if lt(Num::F(offset), Num::F(1e-09))? {
        return Ok(vec![line(start, &up, length)]);
    }
    let side = unit(&lateral)?;
    let theta = 2.0 * offset.atan2(length.f());
    let r = div(length, Num::F(2.0 * num::sin(theta)))?.f();
    let centre = add(start, &scale(&side, Num::F(r)));

    let at = |phi: f64| -> V3 {
        add(&centre, &add(&scale(&side, Num::F(-r * num::cos(phi))), &scale(&up, Num::F(r * num::sin(phi)))))
    };

    let mid = at(theta);
    let turn = add(&scale(&side, Num::F(num::sin(theta))), &scale(&up, Num::F(num::cos(theta))));
    let first = Segment::Arc {
        start: *start,
        midpoint: at(theta / 2.0),
        end: mid,
        radius: r,
        sweep_degrees: num::degrees(theta),
        start_tangent: up,
        end_tangent: turn,
        length: r * theta,
    };
    let mirror = |p: &V3| -> V3 { std::array::from_fn(|i| Num::F(2.0).mul(mid[i]).sub(p[i])) };
    let second = Segment::Arc {
        start: mid,
        midpoint: mirror(&at(theta / 2.0)),
        end: *end,
        radius: r,
        sweep_degrees: num::degrees(theta),
        start_tangent: turn,
        end_tangent: up,
        length: r * theta,
    };
    Ok(vec![first, second])
}

/// `dict(port)`: the caller's port copied, its rows in order.
fn port_copy(port: &Val) -> Result<Val> {
    Ok(Val::dict(interop::entries_of(port)?))
}

/// One pump port's tee, its fore valve's tube and its lower return to the rear valve.
pub fn station(rt: &Rt, fore_y: Num, x: Num, z: Num, upper_port: &Val, return_port: &Val) -> Result<Station> {
    let ports = tee_ports(rt, fore_y, x, z)?;
    let upper = s_bend(&ports.upper.point, &Num::three(&py::at(upper_port, "point")?)?, &UP)?;
    let lower = elbow_return(rt, &ports.lower.point, &Num::three(&py::at(return_port, "point")?)?)?;
    let upper_exposed_mm = developed(&upper);
    Ok(Station {
        tee: ports,
        upper_target: port_copy(upper_port)?,
        return_target: port_copy(return_port)?,
        upper_tube: upper,
        lower,
        upper_exposed_mm,
    })
}

/// Each collet-plate hole's station, keyed by `str(x)`.
pub fn layouts(rt: &Rt, plate: &Val) -> Result<Vec<(String, Station)>> {
    // One copy of the caller's plate; its port dicts are copied again by `station`.
    let plate = py::snapshot(plate)?;
    let mut out: Vec<(String, Station)> = vec![];
    for hole in py::at(&plate, "holes")?.iter()? {
        let pair = py::unpack(&hole, 2)?;
        let key = pair[0].str()?;
        let fore_y = Num::of(&py::at(&plate, "fore_y")?)?;
        let upper_port = py::at(&plate, "upper_ports")?.get(py::s(key.clone()))?;
        let return_port = py::at(&plate, "return_ports")?.get(py::s(key.clone()))?;
        let station = station(rt, fore_y, Num::of(&pair[0])?, Num::of(&pair[1])?, &upper_port, &return_port)?;
        match out.iter_mut().find(|(held, _)| *held == key) {
            Some(row) => row.1 = station,
            None => out.push((key, station)),
        }
    }
    Ok(out)
}

/// A round tube of `diameter` swept along the centreline `segments`.
pub fn sweep(rt: &Rt, diameter: Num, segments: &Val) -> Result<Val> {
    let cq = rt.import("cadquery")?;
    let vector = |items: &Val| -> Result<Val> { py::splat(&cq.attr("Vector")?, items) };
    let mut edges = vec![];
    for s in segments.iter()? {
        let a = vector(&py::at(&s, "start_mm")?)?;
        let b = vector(&py::at(&s, "end_mm")?)?;
        edges.push(if interop::eq(&py::at(&s, "kind")?, &py::s("arc"))? {
            let midpoint = vector(&py::at(&s, "midpoint_mm")?)?;
            py::call(&cq.attr("Edge")?.attr("makeThreePointArc")?, vec![a, midpoint, b])?
        } else {
            py::call(&cq.attr("Edge")?.attr("makeLine")?, vec![a, b])?
        });
    }
    let first = segments.get(Val::Int(0))?;
    let profile = py::call(
        &cq.attr("Wire")?.attr("makeCircle")?,
        vec![
            diameter.div(Num::F(2.0)).val(),
            vector(&py::at(&first, "start_mm")?)?,
            vector(&py::at(&first, "start_tangent")?)?,
        ],
    )?;
    let path = py::call(&cq.attr("Wire")?.attr("assembleEdges")?, vec![Val::list(edges)])?;
    py::call_kw(
        &cq.attr("Solid")?.attr("sweep")?,
        vec![profile, Val::list(vec![]), path],
        vec![("makeSolid", Val::Bool(true)), ("isFrenet", Val::Bool(true))],
    )
}

/// The tube itself: its outside swept, its bore swept out.
pub fn tube(rt: &Rt, segments: &Val) -> Result<Val> {
    let outside = sweep(rt, Num::of(&state(rt)?.tube_od)?, segments)?;
    let cut = outside.attr("cut")?;
    let bore = sweep(rt, Num::F(TUBE_ID), segments)?;
    py::method(&cut.call(vec![bore], vec![])?, "clean", vec![])
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("math", rt.import("math")?)?;
    ns.set("sys", rt.import("sys")?)?;
    rt.import("pathlib")?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let hw = here
        .ancestors()
        .skip(1)
        .find(|p| p.file_name().is_some_and(|name| name == "hardware"))
        .map(Path::to_path_buf)
        .context("StopIteration")?;
    ns.set("_hw", Val::Path(hw.clone()))?;
    for p in [hw.join("reference").join("tee-connector"), hw.join("reference").join("neofit-stem-elbow"), hw.join("scripts")] {
        ns.set("_p", Val::Path(p.clone()))?;
        let text = py::path_str(&p);
        if !py::sys_path_has(rt, &text)? {
            py::sys_path_insert(rt, &text)?;
        }
    }
    let tee = rt.import("tee_connector")?;
    ns.set("tee", tee.clone())?;
    let elbow = rt.import("neofit_stem_elbow")?;
    ns.set("elbow", elbow.clone())?;

    let tube_od = tee.attr("TUBE_D")?;
    ns.set("TUBE_OD", tube_od.clone())?;
    ns.set("TUBE_ID", Val::Float(TUBE_ID))?;
    // The tee wall's fore band, from the bay face to the bore face.
    let plate_t = Num::F(3.175).add(Num::of(&tee.attr("BRANCH_COLLET_TRAVEL")?)?);
    ns.set("PLATE_T", plate_t.val())?;
    // The tee's run axis aft of the bore face: its fixed branch barrel stands
    // `BORE_FACE_TO_AXIS - tee.BRANCH_FIXED_END` aft of that face, the stop it lands on pushed fore.
    let bore_face_to_axis = tee.attr("BRANCH_PRESSED_REACH")?;
    ns.set("BORE_FACE_TO_AXIS", bore_face_to_axis.clone())?;
    let run_face = tee.attr("RUN_HALF")?; // each run collet face from the tee's centre
    ns.set("RUN_FACE", run_face.clone())?;
    let tip_depth = tee.attr("INSERTION")?; // a bottomed tube's tip past the bore face
    ns.set("TIP_DEPTH", tip_depth.clone())?;
    // The pump tube's tip, aft of the fore band's bay face, with the cradle home.
    let tip_from_fore = plate_t.add(Num::of(&tip_depth)?);
    ns.set("TIP_FROM_FORE", tip_from_fore.val())?;
    // Seat depths: a stem or tube bottomed in a run collet standing extended, and the valve's
    // layout estimate. Actual fully seated marks govern factory cuts.
    let run_insertion = tee.attr("RUN_INSERTION_EXTENDED")?;
    ns.set("RUN_INSERTION", run_insertion.clone())?;
    ns.set("VALVE_INSERTION_NOMINAL", Val::Float(VALVE_INSERTION_NOMINAL))?;
    // A stem elbow's axes cross this far under the face its shoulder stands on.
    let elbow_drop = elbow.attr("HUB_BACK_REACH")?;
    ns.set("ELBOW_DROP", elbow_drop.clone())?;

    rt.keep(MODULE, State {
        elbow,
        tube_od,
        plate_t,
        bore_face_to_axis: Num::of(&bore_face_to_axis)?,
        run_face: Num::of(&run_face)?,
        tip_from_fore,
        run_insertion: Num::of(&run_insertion)?,
        elbow_drop: Num::of(&elbow_drop)?,
        fitting: OnceCell::new(),
    });

    ns.def(rt, "_add", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["a", "b"], &[])?;
        let (a, b) = (indexed3(&b.req("a")?)?, indexed3(&b.req("b")?)?);
        Ok(v3(&add(&a, &b)))
    })?;
    ns.def(rt, "_scale", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["a", "k"], &[])?;
        let (a, k) = (nums(&b.req("a")?)?, Num::of(&b.req("k")?)?);
        Ok(Num::vals(&a.iter().map(|v| v.mul(k)).collect::<Vec<_>>()))
    })?;
    ns.def(rt, "_unit", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["v"], &[])?;
        let v = nums(&b.req("v")?)?;
        let n = sqrt(sum(v.iter().map(|c| c.mul(*c))))?;
        let k = div(Num::F(1.0), Num::F(n))?;
        Ok(Num::vals(&v.iter().map(|c| c.mul(k)).collect::<Vec<_>>()))
    })?;
    ns.def(rt, "_line", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["start", "direction", "length"], &[])?;
        let (start, direction, length) = (b.req("start")?, b.req("direction")?, Num::of(&b.req("length")?)?);
        let scaled: Vec<Num> = nums(&direction)?.iter().map(|d| d.mul(length)).collect();
        let first = indexed3(&start)?;
        let end = (0..3)
            .map(|i| Ok(first[i].add(*scaled.get(i).context("tuple index out of range")?)))
            .collect::<Result<Vec<_>>>()?;
        Ok(py::dict([
            ("kind", py::s("line")),
            ("start_mm", Val::Tuple(start.iter()?)),
            ("end_mm", Num::vals(&end)),
            ("start_tangent", Val::Tuple(direction.iter()?)),
            ("end_tangent", Val::Tuple(direction.iter()?)),
            ("length_mm", Val::Float(length.f())),
        ]))
    })?;
    ns.def(rt, "plate_aft_y", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["fore_y"], &[])?;
        Ok(plate_aft_y(rt, Num::of(&b.req("fore_y")?)?)?.val())
    })?;
    ns.def(rt, "tee_axis_y", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["fore_y"], &[])?;
        Ok(tee_axis_y(rt, Num::of(&b.req("fore_y")?)?)?.val())
    })?;
    ns.def(rt, "fore_valve_axis_y", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["fore_y"], &[])?;
        Ok(fore_valve_axis_y(rt, Num::of(&b.req("fore_y")?)?)?.val())
    })?;
    ns.def(rt, "tip_y", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["fore_y"], &[])?;
        Ok(tip_y(rt, Num::of(&b.req("fore_y")?)?)?.val())
    })?;
    ns.def(rt, "tee_ports", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["fore_y", "x", "z"], &[])?;
        let (fore_y, x, z) = (Num::of(&b.req("fore_y")?)?, Num::of(&b.req("x")?)?, Num::of(&b.req("z")?)?);
        Ok(tee_ports(rt, fore_y, x, z)?.val())
    })?;
    ns.def(rt, "elbow_return", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["start", "end"], &[])?;
        let (start, end) = (Num::three(&b.req("start")?)?, Num::three(&b.req("end")?)?);
        Ok(elbow_return(rt, &start, &end)?.val())
    })?;
    ns.def(rt, "s_bend", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["start", "end", "direction"], &[])?;
        let (start, end) = (Num::three(&b.req("start")?)?, Num::three(&b.req("end")?)?);
        let direction = b.opt("direction").map(|d| Num::three(&d)).transpose()?.unwrap_or(UP);
        Ok(segments_val(&s_bend(&start, &end, &direction)?))
    })?;
    ns.def(rt, "station", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["fore_y", "x", "z", "upper_port", "return_port"], &[])?;
        let (fore_y, x, z) = (Num::of(&b.req("fore_y")?)?, Num::of(&b.req("x")?)?, Num::of(&b.req("z")?)?);
        // A caller's dict arrives by reference: one copy each, read and kept.
        let (upper_port, return_port) = (py::snapshot(&b.req("upper_port")?)?, py::snapshot(&b.req("return_port")?)?);
        Ok(station(rt, fore_y, x, z, &upper_port, &return_port)?.val())
    })?;
    ns.def(rt, "layouts", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["plate"], &[])?;
        let rows = layouts(rt, &b.req("plate")?)?;
        Ok(Val::dict(rows.iter().map(|(key, station)| (py::s(key.clone()), station.val())).collect()))
    })?;
    ns.def(rt, "sweep", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["diameter", "segments"], &[])?;
        let diameter = Num::of(&b.req("diameter")?)?;
        sweep(rt, diameter, &b.req("segments")?)
    })?;
    ns.def(rt, "tube", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["segments"], &[])?;
        tube(rt, &b.req("segments")?)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}
