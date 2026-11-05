//! Rust machine assembly entry point and scalar construction questions.
//!
//! The pack's placement ledger (seats and bounds), the tray decks and pump stations read off
//! the placed bodies, the wall stations and port pitches, the tube and body anchors, and the
//! ceiling reliefs the top wall is cut with. Provider modules (CadQuery, `enclosure`,
//! `above_core`, the reference parts) stay Python objects; the arithmetic on what they hand
//! back is Rust.
use super::num::{self, Num};
use super::rt::{Ns, Rt};
use super::{_gas_chain, _stated_bounds, docs, py};
use anyhow::{Context, Result, anyhow, bail};
use hsm_documents::interop::{self, Val};
use py::s;
use std::cell::{OnceCell, RefCell};
use std::path::{Path, PathBuf};
use std::rc::Rc;

/// Converted: the hybrid development build runs this module, not its generated namespace.
pub const TYPED: bool = true;

const MODULE: &str = "enclosure_assembly";

// ---------------------------------------------------------------------------------------------
// Runtime helpers private to this module.

/// `raise Kind(message)` as the runtime spells it.
fn err(kind: &str, msg: impl std::fmt::Display) -> anyhow::Error {
    anyhow!("{kind}: {msg}")
}
fn g(x: f64) -> String {
    num::fmt(x, "g")
}
fn gv(v: &Val) -> Result<String> {
    num::fmtv(v, "g")
}
fn fv(v: &Val, spec: &str) -> Result<String> {
    num::fmtv(v, spec)
}
/// `str(value)` / an f-string field with no spec.
fn sv(v: &Val) -> Result<String> {
    num::fmtv(v, "")
}
fn an(v: &Val, name: &str) -> Result<f64> {
    v.attr(name)?.num()
}
fn anum(v: &Val, name: &str) -> Result<Num> {
    Num::of(&v.attr(name)?)
}
fn ix(v: &Val, i: i64) -> Result<Val> {
    v.get(Val::Int(i))
}
fn ixf(v: &Val, i: i64) -> Result<f64> {
    v.get(Val::Int(i))?.num()
}
fn ixn(v: &Val, i: i64) -> Result<Num> {
    Num::of(&v.get(Val::Int(i))?)
}
fn key(v: &Val, k: &str) -> Result<Val> {
    v.get(s(k))
}
fn keyf(v: &Val, k: &str) -> Result<f64> {
    v.get(s(k))?.num()
}
fn call0(m: &Val, name: &str) -> Result<Val> {
    py::method(m, name, vec![])
}
fn call1(m: &Val, name: &str, a: Val) -> Result<Val> {
    py::method(m, name, vec![a])
}
fn f3(a: [f64; 3]) -> Val {
    py::ftuple(&a)
}
fn tuple_of(v: &Val) -> Result<Val> {
    Ok(Val::Tuple(v.iter()?))
}
fn flt(x: f64) -> Val {
    Val::Float(x)
}
fn nabs(n: Num) -> Num {
    match n {
        Num::I(i) => Num::I(i.abs()),
        Num::F(x) => Num::F(x.abs()),
    }
}
/// The first three numbers of a sequence, as `v[0], v[1], v[2]` reads them.
fn three(v: &Val) -> Result<[f64; 3]> {
    let r = v.iter()?;
    anyhow::ensure!(r.len() >= 3, "index out of range");
    Ok([r[0].num()?, r[1].num()?, r[2].num()?])
}
fn three_n(v: &Val) -> Result<[Num; 3]> {
    let r = v.iter()?;
    anyhow::ensure!(r.len() >= 3, "index out of range");
    Ok([Num::of(&r[0])?, Num::of(&r[1])?, Num::of(&r[2])?])
}
/// `isinstance(value, tuple)` as the runtime answers it.
fn is_tuple(v: &Val) -> Result<bool> {
    match v {
        Val::Tuple(_) => Ok(true),
        Val::Ref(_) => interop::builtin("isinstance")
            .context("isinstance")?
            .call(vec![v.clone(), Val::Type("tuple".into())], vec![])?
            .truthy(),
        _ => Ok(false),
    }
}
/// `max(range(n), key=lambda i: abs(d[i]))`: the first of equal magnitudes wins.
fn argmax_abs(d: &[f64]) -> i64 {
    let mut best = 0usize;
    for i in 1..d.len() {
        if d[i].abs() > d[best].abs() {
            best = i;
        }
    }
    best as i64
}
fn sign_of(x: f64) -> f64 {
    if x > 0.0 { 1.0 } else { -1.0 }
}
/// A string-keyed dict built in order.
fn sdict(rows: Vec<(&str, Val)>) -> Val {
    py::dict(rows.into_iter().map(|(k, v)| (k.to_owned(), v)))
}
fn strs(names: &[&str]) -> Val {
    py::tuple(names.iter().map(|n| s(*n)))
}
fn fpair(a: f64, b: f64) -> Val {
    py::ftuple(&[a, b])
}

/// A placed body's bounding box as `_boxes.boxed` reads it.
#[derive(Clone, Copy, Debug)]
struct BBox {
    xmin: f64,
    ymin: f64,
    zmin: f64,
    xmax: f64,
    ymax: f64,
    zmax: f64,
}
impl BBox {
    fn of(b: &Val) -> Result<BBox> {
        Ok(BBox {
            xmin: an(b, "xmin")?,
            ymin: an(b, "ymin")?,
            zmin: an(b, "zmin")?,
            xmax: an(b, "xmax")?,
            ymax: an(b, "ymax")?,
            zmax: an(b, "zmax")?,
        })
    }
    fn xlen(&self) -> f64 {
        self.xmax - self.xmin
    }
    fn ylen(&self) -> f64 {
        self.ymax - self.ymin
    }
    fn lower(&self) -> [f64; 3] {
        [self.xmin, self.ymin, self.zmin]
    }
    fn upper(&self) -> [f64; 3] {
        [self.xmax, self.ymax, self.zmax]
    }
    fn lo(&self, axis: usize) -> f64 {
        self.lower()[axis]
    }
    fn hi(&self, axis: usize) -> f64 {
        self.upper()[axis]
    }
}

/// A value read once, after the statement that defines it has run.
macro_rules! late {
    ($cell:expr) => {
        $cell.get().with_context(|| format!("{} read before its definition", stringify!($cell)))?
    };
}

// ---------------------------------------------------------------------------------------------
// The module's typed state.

pub struct State {
    ns: Ns,
    hw: PathBuf,
    cq: Val,
    collections: Val,
    fits: Val,
    boxes: Val,
    above: Val,
    comp: Val,
    enc: Val,
    anchor_cap: Val,
    funnel_frame: Val,
    ml: Val,
    asse: Val,
    oad: Val,
    mq6: Val,
    foam: Val,
    cci: Val,
    keystone: Val,
    jg: Val,
    ring: Val,
    np: Val,
    tray: Val,
    dock: Val,
    split: Val,
    drain_bulkhead: Val,
    drain: Val,
    neofit: Val,
    wr1110: Val,
    digiten: Val,
    card: Val,
    vector: OnceCell<Val>,
    wago_steps: OnceCell<Val>,
    seat_type: OnceCell<Val>,
    seats: OnceCell<Val>,
    bound_type: OnceCell<Val>,
    bounds: OnceCell<Val>,
    /// The ids of `BOUNDS`, row for row, while nothing else has changed its length.
    bound_ids: RefCell<Vec<Val>>,
    late: Late,
}

/// Module constants a provider defines, read when their statement runs.
#[derive(Default)]
struct Late {
    core_hold_east_edge: OnceCell<Num>,
    refrigerant_ids: OnceCell<Vec<Val>>,
    chain_seat_slip: OnceCell<Num>,
    port_hole_slip: OnceCell<Num>,
    bulkhead_ring_slip: OnceCell<Num>,
    port_boss_proud: OnceCell<Num>,
    port_hardware_pitch: OnceCell<Num>,
    port_field_pitch: OnceCell<Num>,
    port_pitch: OnceCell<Num>,
    port_west_column: OnceCell<Num>,
    panel_x: OnceCell<Val>,
    digiten_step: OnceCell<PathBuf>,
    digiten_seat_slip: OnceCell<Num>,
    tube_anchor_slip: OnceCell<Num>,
    body_anchor_slip: OnceCell<Num>,
    c14_step: OnceCell<PathBuf>,
    c14_station: OnceCell<Val>,
    asse_seat_slip: OnceCell<Num>,
    misc: RefCell<Vec<(&'static str, Val)>>,
}

fn st(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

impl State {
    fn vector(&self) -> Result<&Val> {
        if self.vector.get().is_none() {
            let v = self.cq.attr("Vector")?;
            let _ = self.vector.set(v);
        }
        Ok(self.vector.get().unwrap())
    }
    /// `cq.Vector(x, y, z)`.
    fn vec3(&self, x: f64, y: f64, z: f64) -> Result<Val> {
        py::call(self.vector()?, vec![flt(x), flt(y), flt(z)])
    }
    /// `cq.Vector(*values)`.
    fn vec_of(&self, values: &Val) -> Result<Val> {
        py::splat(self.vector()?, values)
    }
    /// `box(shape)`: the shape's box through `_boxes`.
    fn boxv(&self, shape: &Val) -> Result<Val> {
        call1(&self.boxes, "boxed", shape.clone())
    }
    fn bbox(&self, shape: &Val) -> Result<BBox> {
        BBox::of(&self.boxv(shape)?)
    }
    fn seats(&self) -> Result<&Val> {
        Ok(late!(self.seats))
    }
    /// A module constant set by a statement this file holds, read back off the namespace.
    fn misc(&self, name: &str) -> Result<Val> {
        let rows = self.late.misc.borrow();
        rows.iter().find(|(n, _)| *n == name).map(|(_, v)| v.clone()).with_context(|| format!("{name} before its definition"))
    }
    fn keep_misc(&self, name: &'static str, value: Val) {
        self.late.misc.borrow_mut().push((name, value));
    }
}

// ---------------------------------------------------------------------------------------------
// The script's own entry point.

/// `if __name__ == "__main__": main(); raise SystemExit(0)`.
pub fn main_block(rt: &Rt) -> Result<()> {
    let ns = rt.namespace(MODULE)?;
    py::call(&ns.get("main")?, vec![])?;
    Ok(())
}

fn main_fn(rt: &Rt) -> Result<Val> {
    let layout = rt.import("_machine_layout")?;
    py::call(&layout.attr("main")?, vec![])
}

// ---------------------------------------------------------------------------------------------
// Boxes, shifts and turns (Python lines 125-182).

fn wago_step(rt: &Rt, size: &Val) -> Result<Val> {
    let st = st(rt)?;
    late!(st.wago_steps).get(size.clone())
}

/// `_shift(b, *, cx, x0, x1, cy, y0, y1, z0, dz)`: the vector that stands `b` on the planes.
fn shift(rt: &Rt, b: &Val, p: &[Option<Val>; 8]) -> Result<Val> {
    let st = st(rt)?;
    let some = |i: usize| -> Result<Option<f64>> {
        match &p[i] {
            None | Some(Val::None) => Ok(None),
            Some(v) => Ok(Some(v.num()?)),
        }
    };
    let (cx, x0, x1, cy, y0, y1, z0) = (some(0)?, some(1)?, some(2)?, some(3)?, some(4)?, some(5)?, some(6)?);
    let x = cx.map_or(Ok(0.0), |c| Ok::<f64, anyhow::Error>(c - (an(b, "xmin")? + an(b, "xmax")?) / 2.0))?
        + x0.map_or(Ok(0.0), |v| Ok::<f64, anyhow::Error>(v - an(b, "xmin")?))?
        + x1.map_or(Ok(0.0), |v| Ok::<f64, anyhow::Error>(v - an(b, "xmax")?))?;
    let y = cy.map_or(Ok(0.0), |c| Ok::<f64, anyhow::Error>(c - (an(b, "ymin")? + an(b, "ymax")?) / 2.0))?
        + y0.map_or(Ok(0.0), |v| Ok::<f64, anyhow::Error>(v - an(b, "ymin")?))?
        + y1.map_or(Ok(0.0), |v| Ok::<f64, anyhow::Error>(v - an(b, "ymax")?))?;
    let dz = match &p[7] {
        Some(v) if v.truthy()? => v.num()?,
        _ => 0.0,
    };
    let z = z0.map_or(Ok(0.0), |v| Ok::<f64, anyhow::Error>(v - an(b, "zmin")?))? + dz;
    st.vec3(x, y, z)
}

/// Rodrigues: `v` turned `deg` about the unit `axis` through the origin.
fn turned(rt: &Rt, v: &Val, axis: &Val, deg: &Val) -> Result<Val> {
    let st = st(rt)?;
    let a = call0(&st.vec_of(axis)?, "normalized")?;
    let th = num::radians(deg.num()?);
    let (c, s_) = (num::cos(th), num::sin(th));
    let first = interop::binary("mul", st.vec_of(v)?, flt(c))?;
    let second = interop::binary("mul", call1(&a, "cross", st.vec_of(v)?)?, flt(s_))?;
    let sum = interop::binary("add", first, second)?;
    let dot = call1(&a, "dot", st.vec_of(v)?)?;
    let scale = interop::binary("mul", dot, flt(1.0 - c))?;
    interop::binary("add", sum, interop::binary("mul", a, scale)?)
}

// ---------------------------------------------------------------------------------------------
// The placement ledger (Python lines 184-244).

const FACES: [&str; 7] = ["cx", "x0", "x1", "cy", "y0", "y1", "z0"];

/// `_FACE[k](b)`.
fn face_read(k: &str, b: &Val) -> Result<Val> {
    Ok(match k {
        "cx" => flt((an(b, "xmin")? + an(b, "xmax")?) / 2.0),
        "x0" => b.attr("xmin")?,
        "x1" => b.attr("xmax")?,
        "cy" => flt((an(b, "ymin")? + an(b, "ymax")?) / 2.0),
        "y0" => b.attr("ymin")?,
        "y1" => b.attr("ymax")?,
        "z0" => b.attr("zmin")?,
        _ => bail!("missing key {}", s(k).repr()?),
    })
}

/// `record_seat(name, *, turns=(), planes=None, station=None, got=None, members=())`.
fn record_seat(rt: &Rt, name: &Val, turns: &Val, planes: &Val, station: &Val, got: &Val, members: &Val) -> Result<Val> {
    let st = st(rt)?;
    let (rule, read) = if matches!(station, Val::None) {
        let rule = Val::dict(vec![]);
        let source = if planes.truthy()? { planes.clone() } else { Val::dict(vec![]) };
        for item in call0(&source, "items")?.iter()? {
            let kv = py::unpack(&item, 2)?;
            if !matches!(kv[1], Val::None) {
                rule.set(kv[0].clone(), kv[1].clone())?;
            }
        }
        let read = Val::dict(vec![]);
        for k in rule.iter()? {
            if let Val::Str(name) = &k {
                if FACES.contains(&name.as_str()) {
                    read.set(k.clone(), face_read(name, got)?)?;
                }
            }
        }
        (rule, read)
    } else {
        (sdict(vec![("station", tuple_of(station)?)]), sdict(vec![("station", tuple_of(got)?)]))
    };
    let members = {
        let m = tuple_of(members)?;
        if m.truthy()? { m } else { Val::Tuple(vec![name.clone()]) }
    };
    let seat = py::call(late!(st.seat_type), vec![tuple_of(turns)?, rule, read, Val::list(vec![]), members])?;
    let seats = st.seats()?;
    seats.set(name.clone(), seat)?;
    seats.get(name.clone())
}

/// A plane-rule seat from this module's own constructions.
fn seat_planes(rt: &Rt, name: &str, planes: Vec<(&str, Val)>, got: &Val) -> Result<Val> {
    let empty = Val::Tuple(vec![]);
    record_seat(rt, &s(name), &empty, &sdict(planes), &Val::None, got, &empty)
}

fn record_pump_dock_seats(rt: &Rt, box_spec: &Val, dock_parts: &Val) -> Result<()> {
    let st = st(rt)?;
    let plate = box_spec.attr("pack")?.attr("collet_plate")?;
    let plumbing = st.dock.attr("plumbing")?;
    let fore_y = key(&plate, "fore_y")?;
    let fore = Num::of(&call1(&plumbing, "tee_axis_y", fore_y.clone())?)?.sub(anum(&st.dock.attr("tee")?, "BRANCH_REACH")?);
    for item in call1(&st.dock, "stations", plate.clone())?.iter()? {
        let row = py::unpack(&item, 4)?;
        let (tee_name, x, z) = (row[1].str()?, row[2].clone(), row[3].clone());
        let name = format!("tee-{}", tee_name.to_lowercase());
        let z0 = Num::of(&z)?.sub(anum(&plumbing, "RUN_FACE")?);
        let got = st.boxv(&dock_parts.get(s(&name))?)?;
        seat_planes(rt, &name, vec![("y0", fore.val()), ("cx", x.clone()), ("z0", z0.val())], &got)?;
        let target = key(&plate, "return_ports")?.get(s(x.str()?))?;
        let lower = key(&key(&py::call(&plumbing.attr("tee_ports")?, vec![fore_y.clone(), x.clone(), z.clone()])?, "lower")?, "point")?;
        let line = py::call(&plumbing.attr("elbow_return")?, vec![lower.clone(), tuple_of(&key(&target, "point")?)?])?;
        let elbows = key(&line, "elbows")?;
        let legs = [
            (row[1].clone(), ix(&lower, 2)?, ix(&elbows, 0)?, plumbing.attr("RUN_INSERTION")?),
            (key(&target, "valve")?, ix(&key(&target, "point")?, 2)?, ix(&elbows, 1)?, plumbing.attr("VALVE_INSERTION_NOMINAL")?),
        ];
        for (host, port_z, _row, inserted) in legs {
            let name = format!("stem-elbow-{}", host.str()?.to_lowercase());
            let z1 = Num::of(&port_z)?.add(Num::of(&inserted)?);
            let got = st.boxv(&dock_parts.get(s(&name))?)?;
            seat_planes(rt, &name, vec![("z0", key(&line, "floor_z")?), ("z1", z1.val())], &got)?;
        }
    }
    Ok(())
}

fn note_room(rt: &Rt, name: &Val, what: Val, want: Val, got: Val) -> Result<()> {
    let st = st(rt)?;
    let seats = st.seats()?;
    if seats.contains(name)? {
        call1(&seats.get(name.clone())?.attr("room")?, "append", Val::Tuple(vec![what, want, got]))?;
    }
    Ok(())
}

// ---------------------------------------------------------------------------------------------
// The base, the condenser lane and the power face (Python lines 246-345).

const BASE_YAW: f64 = -90.0;
const COMPRESSOR_FRONT: f64 = 11.0;
const PACK_CROWN: f64 = 151.0;

fn east_lane_free(rt: &Rt, cond: &Val) -> Result<Num> {
    let st = st(rt)?;
    let b = st.boxv(cond)?;
    let storey_z = Num::of(&st.enc.attr("z_seam")?)?;
    let band_aft = ixn(&call1(&st.enc, "front_band_free_y", b.attr("ymin")?)?, 1)?;
    let (zmax, ymax) = (an(&b, "zmax")?, an(&b, "ymax")?);
    if zmax > storey_z.add(Num::F(1e-9)).f() || ymax > band_aft.add(Num::F(1e-9)).f() {
        return Err(err(
            "ValueError",
            format!(
                "the condenser reaches y {} and z {}, out of the corner of the ±X band the front column leaves empty — under z {}, forward of y {}. A block that stands up into the slide's storey answers to the rail's whole reach and not to its own fin, so it stands off `enclosure.side_band_inset` instead.",
                g(ymax),
                g(zmax),
                storey_z.fmt("g"),
                band_aft.fmt("g")
            ),
        ));
    }
    let face = ixn(&call0(&st.enc, "front_bottom_flank_face")?, 1)?;
    Ok(face.sub(anum(&st.enc, "cond_mount_clear")?).sub(Num::F(an(&b, "xmax")?)))
}

const FUSE_FACE_NORMAL: [f64; 3] = [1.0, 0.0, 0.0];

fn fuse_turn() -> Val {
    Val::Tuple(vec![
        Val::Tuple(vec![f3([1.0, 0.0, 0.0]), flt(90.0)]),
        Val::Tuple(vec![f3([0.0, 0.0, 1.0]), flt(90.0)]),
    ])
}

fn power_face_station(rt: &Rt, comp_carry: &Val) -> Result<Val> {
    let st = st(rt)?;
    let placed = py::call(comp_carry, vec![call0(&st.comp, "power_face")?])?;
    let pn = py::unpack(&placed, 2)?;
    let got: Vec<f64> = pn[1].iter()?.iter().map(|v| Ok(num::round_to(v.num()?, 9))).collect::<Result<_>>()?;
    if got.len() != 3 || got.iter().zip(FUSE_FACE_NORMAL).any(|(a, b)| *a != b) {
        return Err(err(
            "ValueError",
            format!(
                "the compressor's power face looks {} in the machine and the cutoff's quarters lay its contact line on {} — the base has been turned out from under this pose, and the case is now bedded in the cover rather than on it.",
                sv(&py::ftuple(&got))?,
                sv(&f3(FUSE_FACE_NORMAL))?
            ),
        ));
    }
    Ok(pn[0].clone())
}

const CORE: &str = "cold-core";

/// The Z the core presents to the machine: its top lid's outer face.
fn cap_face(rt: &Rt, foam: &Val) -> Result<Num> {
    let st = st(rt)?;
    Ok(Num::F(an(&st.boxv(foam)?, "zmin")?).add(anum(&st.foam, "cap_face_over_floor")?))
}

const MQ6_Y0: f64 = 38.3;

fn mq6_cradle(rt: &Rt, carry: &Val) -> Result<Val> {
    let st = st(rt)?;
    let pos = ix(&py::call(carry, vec![call0(&st.mq6, "card_plane")?])?, 0)?;
    Ok(Val::Tuple(vec![Val::Tuple(vec![ix(&pos, 0)?, ix(&pos, 1)?, ix(&pos, 2)?])]))
}

// ---------------------------------------------------------------------------------------------
// The bound ledger (Python lines 349-386).

fn record_bound(rt: &Rt, bound: Val) -> Result<Val> {
    let st = st(rt)?;
    let list = late!(st.bounds);
    let Val::List(rows) = list else { bail!("BOUNDS is not a list") };
    let id = bound.attr("id")?;
    let mut ids = st.bound_ids.borrow_mut();
    if ids.len() != rows.borrow().len() {
        *ids = rows.borrow().iter().map(|b| b.attr("id")).collect::<Result<_>>()?;
    }
    let mut kept_ids = Vec::with_capacity(ids.len() + 1);
    let mut kept = Vec::with_capacity(ids.len() + 1);
    for (x, row) in ids.iter().zip(rows.borrow().iter()) {
        if !interop::eq(x, &id)? {
            kept_ids.push(x.clone());
            kept.push(row.clone());
        }
    }
    kept_ids.push(id);
    kept.push(bound.clone());
    *rows.borrow_mut() = kept;
    *ids = kept_ids;
    Ok(bound)
}

fn carry_enclosure_bounds(rt: &Rt) -> Result<()> {
    let st = st(rt)?;
    for b in st.enc.attr("BOUNDS")?.iter()? {
        let bound = py::call(late!(st.bound_type), b.iter()?)?;
        record_bound(rt, bound)?;
    }
    Ok(())
}

fn carry_stated_bounds(rt: &Rt) -> Result<()> {
    let st = st(rt)?;
    for b in _stated_bounds::records(rt)? {
        let bound = py::call(late!(st.bound_type), b.iter()?)?;
        record_bound(rt, bound)?;
    }
    Ok(())
}

// ---------------------------------------------------------------------------------------------
// The core's frame and the cap's cradles (Python lines 389-449).

const CRADLE_TOL: f64 = 0.01;

/// `(origin, +X, +Y)` of the cold core in world, as CadQuery vectors.
fn core_frame(rt: &Rt, foam_carry: &Val) -> Result<(Val, Val, Val)> {
    let st = st(rt)?;
    let at = |p: [f64; 3]| -> Result<Val> {
        let placed = py::call(foam_carry, vec![Val::Tuple(vec![f3(p), f3([0.0, 0.0, 1.0])])])?;
        st.vec_of(&ix(&placed, 0)?)
    };
    let o = at([0.0, 0.0, 0.0])?;
    let ex = interop::binary("sub", at([1.0, 0.0, 0.0])?, o.clone())?;
    let ey = interop::binary("sub", at([0.0, 1.0, 0.0])?, o.clone())?;
    Ok((o, ex, ey))
}

fn cap_xy(rt: &Rt, foam_carry: &Val, world_xy: &Val) -> Result<Val> {
    let st = st(rt)?;
    let (o, ex, ey) = core_frame(rt, foam_carry)?;
    let dx = ixn(world_xy, 0)?.sub(anum(&o, "x")?);
    let dy = ixn(world_xy, 1)?.sub(anum(&o, "y")?);
    let d = py::call(st.vector()?, vec![dx.val(), dy.val(), flt(0.0)])?;
    let uv = Val::Tuple(vec![call1(&d, "dot", ex)?, call1(&d, "dot", ey)?]);
    call1(&st.foam, "spin_xy", uv)
}

fn cradle_rows(rt: &Rt, foam: &Val, foam_carry: &Val, placed: &Val) -> Result<Val> {
    let st = st(rt)?;
    let (_o, ex, ey) = core_frame(rt, foam_carry)?;
    let face = cap_face(rt, foam)?;
    let rows = Val::list(vec![]);
    for item in call0(&st.cci.attr("cap_cradles")?, "items")?.iter()? {
        let ns = py::unpack(&item, 2)?;
        let (name, station) = (ns[0].clone(), ns[1].clone());
        let b = BBox::of(&st.boxv(&placed.get(name.clone())?)?)?;
        let along: Vec<f64> = [&ex, &ey]
            .iter()
            .map(|v| Ok(an(v, "x")?.abs() * b.xlen() + an(v, "y")?.abs() * b.ylen()))
            .collect::<Result<_>>()?;
        let yaw = if along[0] >= along[1] { 0.0 } else { 90.0 };
        let xy = cap_xy(rt, foam_carry, &fpair((b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0))?;
        let xy = py::unpack(&xy, 2)?;
        let long = if along[1] > along[0] { along[1] } else { along[0] };
        let short = if along[1] < along[0] { along[1] } else { along[0] };
        let wants = Val::Tuple(vec![xy[0].clone(), xy[1].clone(), flt(yaw), Num::F(b.zmin).sub(face).val()]);
        rows.attr("append")?.call(vec![Val::Tuple(vec![name, station, wants, flt(long), flt(short)])], vec![])?;
    }
    Ok(rows)
}

fn cradles_land(rows: &Val) -> Result<Val> {
    let out = Val::list(vec![]);
    for row in rows.iter()? {
        let r = py::unpack(&row, 5)?;
        let (name, station, wants) = (r[0].clone(), r[1].clone(), r[2].clone());
        let centre = station.attr("centre")?;
        let has = Val::Tuple(vec![ix(&centre, 0)?, ix(&centre, 1)?, station.attr("yaw")?, station.attr("seat")?]);
        let mut off = false;
        for (h, w) in has.iter()?.iter().zip(wants.iter()?.iter()) {
            if nabs(Num::of(h)?.sub(Num::of(w)?)).f() > CRADLE_TOL {
                off = true;
            }
        }
        if off {
            out.attr("append")?.call(vec![Val::Tuple(vec![name, has, wants])], vec![])?;
        }
    }
    Ok(out)
}

const TRAY_SEAT_SLIP: f64 = 0.2;

// ---------------------------------------------------------------------------------------------
// Install, Python lines 1-452.

fn install_1(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::ENCLOSURE_ASSEMBLY))?;
    let path_type = rt.member("pathlib", "Path")?;
    ns.set("Path", path_type.clone())?;
    let sys = rt.import("sys")?;
    ns.set("sys", sys.clone())?;
    let file = py::path(&ns.get("__file__")?)?;
    let here = py::resolve(&file)?;
    ns.set("_here", Val::Path(here.clone()))?;
    let hw = here.ancestors().nth(2).map(Path::to_path_buf).context("parents[1]")?;
    ns.set("_hw", Val::Path(hw.clone()))?;
    py::sys_path_insert(rt, &py::path_str(&hw.join("scripts")))?;
    ns.def(rt, "main", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        main_fn(rt)
    })?;
    let parent = here.parent().map(Path::to_path_buf).unwrap_or_default();
    let folders: Vec<PathBuf> = [
        "scripts",
        "",
        "reference/compressor",
        "reference/condenser-block",
        "printed-parts/cadlib",
        "printed-parts/valve-seat",
        "printed-parts/zone-c/funnel",
        "printed-parts/zone-c/funnel-cover",
        "reference/jg-pp0408w",
        "reference/neofit-stem-elbow",
        "printed-parts/diaphragm-pump-sleeve",
        "reference/waveshare-43b-display",
        "reference/meanwell-irm90",
        "reference/teyleten-relay",
        "printed-parts/electronics",
        "printed-parts/electronics/pcba-tray",
        "reference/asse1022-assembly",
        "reference/flare38-14ptc",
        "reference/mq6-gas-sensor",
        "reference/sf76e-thermal-fuse",
        "printed-parts/refrigeration/fuse-clamp",
        "reference/water-split",
        "reference/shok-blok-regulator",
        "reference/beduan-solenoid",
        "reference/jg-bulkhead-union",
        "reference/iec-c14-inlet",
        "reference/riteav-keystone",
        "reference/neofit-bulkhead",
        "reference/neofit-drain-bulkhead",
        "reference/gasher-check-valve",
        "reference/wr1110-regulator",
        "reference/digiten-flow-sensor",
        "cold-core-layout",
        "printed-parts/cold-core",
        "printed-parts/cold-core/foam-assembly",
        "printed-parts/enclosure/bulkhead-ring",
        "printed-parts/faucet/tube-collar",
        "printed-parts/enclosure/nameplate",
        "printed-parts/enclosure/valve-tray",
        "printed-parts/enclosure/pump-tray",
        "printed-parts/enclosure/y-wall-of-back-top",
        "printed-parts/enclosure/display-cover",
        "printed-parts/enclosure/display-gasket",
        "printed-parts/enclosure/enclosure",
    ]
    .iter()
    .map(|rel| if rel.is_empty() { parent.clone() } else { rel.split('/').fold(hw.clone(), |p, part| p.join(part)) })
    .collect();
    for folder in &folders {
        ns.set("_p", Val::Path(folder.clone()))?;
        py::sys_path_insert(rt, &py::path_str(folder))?;
    }
    let cq = rt.import("_enclosure_datums")?;
    ns.set("cq", cq.clone())?;
    call0(&cq, "install")?;
    let collections = rt.import("collections")?;
    ns.set("collections", collections.clone())?;
    ns.set("math", rt.import("math")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let mut handles: Vec<Val> = vec![];
    for (alias, module) in [
        ("fits", "fits"),
        ("_boxes", "_boxes"),
        ("_above", "above_core"),
        ("_stated", "_stated_bounds"),
        ("_comp", "compressor"),
        ("_enc", "enclosure"),
        ("_anchor_cap", "_anchor_cap_interface"),
        ("_funnel_frame", "funnel_frame"),
        ("ml", "manifold_layout"),
        ("_asse", "asse1022_assembly"),
        ("_oad", "flare38_14ptc"),
        ("_mq6", "mq6_gas_sensor"),
        ("_foam", "foam_assembly"),
        ("_cci", "_cold_core_interface"),
        ("_keystone", "riteav_keystone"),
        ("_jg", "jg_bulkhead_union"),
        ("_ring", "bulkhead_ring"),
        ("_np", "nameplate"),
        ("_tray", "pump_tray"),
        ("_dock", "dock_structure"),
        ("_split", "water_split"),
        ("_drain_bulkhead", "neofit_drain_bulkhead"),
        ("_drain", "_drain"),
        ("_neofit", "neofit_bulkhead"),
        ("_wr1110", "wr1110_regulator"),
        ("_gas_chain", "_gas_chain"),
        ("_digiten", "digiten_flow_sensor"),
        ("_card", "_scorecard"),
    ] {
        let module = rt.import(module)?;
        ns.set(alias, module.clone())?;
        handles.push(module);
    }
    let mut h = handles.into_iter();
    let mut next = || h.next().expect("provider handle");
    let state = State {
        ns: ns.clone(),
        hw: hw.clone(),
        cq,
        collections: collections.clone(),
        fits: next(),
        boxes: next(),
        above: {
            let above = next();
            let _stated = next();
            above
        },
        comp: next(),
        enc: next(),
        anchor_cap: next(),
        funnel_frame: next(),
        ml: next(),
        asse: next(),
        oad: next(),
        mq6: next(),
        foam: next(),
        cci: next(),
        keystone: next(),
        jg: next(),
        ring: next(),
        np: next(),
        tray: next(),
        dock: next(),
        split: next(),
        drain_bulkhead: next(),
        drain: next(),
        neofit: next(),
        wr1110: {
            let wr = next();
            let _gas = next();
            wr
        },
        digiten: next(),
        card: next(),
        vector: OnceCell::new(),
        wago_steps: OnceCell::new(),
        seat_type: OnceCell::new(),
        seats: OnceCell::new(),
        bound_type: OnceCell::new(),
        bounds: OnceCell::new(),
        bound_ids: RefCell::new(vec![]),
        late: Late::default(),
    };
    let kept = rt.keep(MODULE, state);

    ns.set("_here", Val::Path(py::resolve(&file)?))?;
    let hw2 = here.ancestors().skip(1).find(|p| p.file_name().is_some_and(|n| n == "hardware")).map(Path::to_path_buf).context("StopIteration")?;
    ns.set("_hw", Val::Path(hw2.clone()))?;
    let hwp = |rel: &str| Val::Path(rel.split('/').fold(hw2.clone(), |p, part| p.join(part)));
    ns.set("PSU_STEP", hwp("reference/meanwell-irm90/meanwell-irm90.step"))?;
    ns.set("PCBA_STEP", hwp("printed-parts/electronics/pcba-tray/pcba-board.step"))?;
    ns.set("RELAY_STEP", hwp("reference/teyleten-relay/teyleten-relay.step"))?;
    let wago_steps = sdict(vec![
        ("413", hwp("reference/wago-221/wago-221-413.step")),
        ("415", hwp("reference/wago-221/wago-221-415.step")),
        ("420", hwp("reference/wago-221/wago-221-420.step")),
    ]);
    ns.set("WAGO_STEPS", wago_steps.clone())?;
    let _ = kept.wago_steps.set(wago_steps);
    ns.def(rt, "wago_step", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["size"], &[])?;
        wago_step(rt, &a.req("size")?)
    })?;
    ns.set("WAGO_POLES", strs(&["wago-v12", "wago-gnd", "wago-g", "wago-h", "wago-n"]))?;
    let pitch = anum(&kept.enc, "wago_pitch")?;
    let cluster = sdict(vec![
        ("wago-mana", Val::Tuple(vec![Val::Int(1), flt(169.0), flt(280.0), s("420")])),
        ("wago-manb", Val::Tuple(vec![Val::Int(1), flt(169.0), flt(246.0), s("415")])),
        ("wago-reeds-b", Val::Tuple(vec![Val::Int(-1), Num::F(335.0).sub(Num::F(2.0).mul(pitch)).val(), flt(270.0), s("413")])),
        ("wago-sensors", Val::Tuple(vec![Val::Int(-1), flt(335.0), flt(270.0), s("413")])),
    ]);
    ns.set("CLUSTER_WAGOS", cluster.clone())?;
    kept.keep_misc("CLUSTER_WAGOS", cluster);
    ns.set("FOAM_STEP", hwp("printed-parts/cold-core/foam-assembly/foam-assembly.step"))?;
    ns.set("FUNNEL_STEP", hwp("printed-parts/zone-c/funnel/funnel.step"))?;
    ns.set("FUNNEL_COVER_STEP", hwp("printed-parts/zone-c/funnel-cover/funnel-cover.step"))?;
    ns.set("FOAM_YAW", flt(90.0))?;
    ns.set("COMPRESSOR_YAW", flt(90.0))?;
    ns.set("FUNNEL_ROT", flt(0.0))?;
    ns.def(rt, "box", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["shape"], &[])?;
        st(rt)?.boxv(&a.req("shape")?)
    })?;
    ns.def(rt, "_shift", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["b"], &["cx", "x0", "x1", "cy", "y0", "y1", "z0", "dz"])?;
        let b = a.req("b")?;
        let p = [a.opt("cx"), a.opt("x0"), a.opt("x1"), a.opt("cy"), a.opt("y0"), a.opt("y1"), a.opt("z0"), a.opt("dz")];
        shift(rt, &b, &p)
    })?;
    ns.def(rt, "_turned", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["v", "axis", "deg"], &[])?;
        turned(rt, &a.req("v")?, &a.req("axis")?, &a.req("deg")?)
    })?;
    let seat_type = py::call_kw(&collections.attr("namedtuple")?, vec![s("Seat"), s("turns rule got room members")], vec![("module", s(MODULE))])?;
    ns.set("Seat", seat_type.clone())?;
    let _ = kept.seat_type.set(seat_type);
    let seats = Val::dict(vec![]);
    ns.set("SEATS", seats.clone())?;
    let _ = kept.seats.set(seats);
    let face = Val::dict(vec![]);
    for k in FACES {
        let runtime = rt.clone();
        face.set(
            s(k),
            Val::function(move |args, kw| {
                let _frame = runtime.frame(MODULE);
                let mut a = py::bind(args, kw, &["b"], &[])?;
                face_read(k, &a.req("b")?)
            }),
        )?;
    }
    ns.set("_FACE", face)?;
    ns.def(rt, "record_seat", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &["turns", "planes", "station", "got", "members"])?;
        let name = a.req("name")?;
        let turns = a.opt("turns").unwrap_or(Val::Tuple(vec![]));
        let planes = a.opt("planes").unwrap_or(Val::None);
        let station = a.opt("station").unwrap_or(Val::None);
        let got = a.opt("got").unwrap_or(Val::None);
        let members = a.opt("members").unwrap_or(Val::Tuple(vec![]));
        record_seat(rt, &name, &turns, &planes, &station, &got, &members)
    })?;
    ns.def(rt, "record_pump_dock_seats", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["box_spec", "dock_parts"], &[])?;
        record_pump_dock_seats(rt, &a.req("box_spec")?, &a.req("dock_parts")?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "note_room", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name", "what", "want", "got"], &[])?;
        let (name, what, want, got) = (a.req("name")?, a.req("what")?, a.req("want")?, a.req("got")?);
        note_room(rt, &name, what, want, got)?;
        Ok(Val::None)
    })?;
    ns.set("BASE_YAW", flt(BASE_YAW))?;
    ns.set("COMPRESSOR_FRONT", flt(COMPRESSOR_FRONT))?;
    ns.set("PACK_CROWN", flt(PACK_CROWN))?;
    ns.def(rt, "east_lane_free", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["cond"], &[])?;
        Ok(east_lane_free(rt, &a.req("cond")?)?.val())
    })?;
    ns.set("FUSE_TURN", fuse_turn())?;
    ns.set("FUSE_FACE_NORMAL", f3(FUSE_FACE_NORMAL))?;
    ns.def(rt, "power_face_station", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["comp_carry"], &[])?;
        power_face_station(rt, &a.req("comp_carry")?)
    })?;
    ns.set("CORE", s(CORE))?;
    ns.def(rt, "cap_face", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["foam"], &[])?;
        Ok(cap_face(rt, &a.req("foam")?)?.val())
    })?;
    ns.set("MQ6_Y0", flt(MQ6_Y0))?;
    ns.def(rt, "mq6_cradle", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["carry"], &[])?;
        mq6_cradle(rt, &a.req("carry")?)
    })?;
    let bound_type = py::call_kw(
        &collections.attr("namedtuple")?,
        vec![s("Bound"), s("id label ok value target detail kind")],
        vec![("defaults", Val::Tuple(vec![s("gate")])), ("module", s(MODULE))],
    )?;
    ns.set("Bound", bound_type.clone())?;
    let _ = kept.bound_type.set(bound_type);
    let bounds = Val::list(vec![]);
    ns.set("BOUNDS", bounds.clone())?;
    let _ = kept.bounds.set(bounds);
    ns.def(rt, "record_bound", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["bound"], &[])?;
        record_bound(rt, a.req("bound")?)
    })?;
    ns.def(rt, "carry_enclosure_bounds", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        carry_enclosure_bounds(rt)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "carry_stated_bounds", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        carry_stated_bounds(rt)?;
        Ok(Val::None)
    })?;
    ns.set("CRADLE_TOL", flt(0.001))?;
    ns.def(rt, "_core_frame", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["foam_carry"], &[])?;
        let (o, ex, ey) = core_frame(rt, &a.req("foam_carry")?)?;
        Ok(Val::Tuple(vec![o, ex, ey]))
    })?;
    ns.def(rt, "cap_xy", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["foam_carry", "world_xy"], &[])?;
        cap_xy(rt, &a.req("foam_carry")?, &a.req("world_xy")?)
    })?;
    ns.def(rt, "cradle_rows", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["foam", "foam_carry", "placed"], &[])?;
        cradle_rows(rt, &a.req("foam")?, &a.req("foam_carry")?, &a.req("placed")?)
    })?;
    ns.set("CRADLE_TOL", flt(CRADLE_TOL))?;
    ns.def(rt, "cradles_land", |_, args, kw| {
        let mut a = py::bind(args, kw, &["rows"], &[])?;
        cradles_land(&a.req("rows")?)
    })?;
    ns.set("TRAY_SEAT_SLIP", flt(TRAY_SEAT_SLIP))?;
    let _ = (&kept.collections, &kept.hw, &kept.ns);
    Ok(())
}

// ---------------------------------------------------------------------------------------------
// Valve decks and pump stations (Python lines 454-655).

/// Placed bodies as `(name, solid)`, whichever of the two shapes `placed` arrived in.
fn bodies(placed: &Val) -> Result<Vec<(Val, Val)>> {
    let mut out: Vec<(Val, Val)> = vec![];
    for item in call0(placed, "items")?.iter()? {
        let nb = py::unpack(&item, 2)?;
        let body = if is_tuple(&nb[1])? { ix(&nb[1], 0)? } else { nb[1].clone() };
        match out.iter_mut().find(|(n, _)| interop::eq(n, &nb[0]).unwrap_or(false)) {
            Some(row) => row.1 = body,
            None => out.push((nb[0].clone(), body)),
        }
    }
    Ok(out)
}

fn coil_missing(name: &str, coil: &str) -> anyhow::Error {
    err(
        "KeyError",
        format!(
            "{name} is placed and {coil} is not, so nothing says which way it faces — a Beduan's coil stands on its crown and that is what tells a tray which of the body's six faces its four posts stand on."
        ),
    )
}

/// One valve's own +Z in world, as `(axis, sign)`.
fn valve_up(rt: &Rt, placed: &Val, name: &str) -> Result<(i64, f64)> {
    let st = st(rt)?;
    let coil = name.replace("valve-", "coil-");
    if !placed.contains(&s(&coil))? {
        return Err(coil_missing(name, &coil));
    }
    let vb = st.bbox(&placed.get(s(name))?)?;
    let cb = st.bbox(&placed.get(s(&coil))?)?;
    let d = [0, 1, 2].map(|i| (cb.lo(i) + cb.hi(i) - vb.lo(i) - vb.hi(i)) / 2.0);
    let axis = argmax_abs(&d);
    Ok((axis, sign_of(d[axis as usize])))
}

fn tray_valve(rt: &Rt, name: &str) -> Result<bool> {
    if !name.starts_with("valve-v-") {
        return Ok(false);
    }
    let st = st(rt)?;
    let key = s(name);
    if call0(&st.above, "valve_names")?.contains(&key)? {
        return Ok(false);
    }
    if st.cci.attr("cap_cradles")?.contains(&key)? {
        return Ok(false);
    }
    Ok(!call0(&st.above, "core_equipment_names")?.contains(&key)?)
}

/// `name -> (lower, upper)` readings, from this module's boxes or from a caller's mapping.
enum Readings<'a> {
    Typed(&'a [(String, [f64; 3], [f64; 3])]),
    Val(&'a Val),
}
impl Readings<'_> {
    fn names(&self) -> Result<Vec<String>> {
        match self {
            Readings::Typed(rows) => Ok(rows.iter().map(|r| r.0.clone()).collect()),
            Readings::Val(v) => v.iter()?.iter().map(Val::str).collect(),
        }
    }
    fn has(&self, name: &str) -> Result<bool> {
        match self {
            Readings::Typed(rows) => Ok(rows.iter().any(|r| r.0 == name)),
            Readings::Val(v) => v.contains(&s(name)),
        }
    }
    fn get(&self, name: &str) -> Result<([f64; 3], [f64; 3])> {
        match self {
            Readings::Typed(rows) => rows
                .iter()
                .find(|r| r.0 == name)
                .map(|r| (r.1, r.2))
                .with_context(|| format!("missing key {}", s(name).repr().unwrap_or_default())),
            Readings::Val(v) => {
                let lu = py::unpack(&v.get(s(name))?, 2)?;
                Ok((three(&lu[0])?, three(&lu[1])?))
            }
        }
    }
}

/// One valve deck: the world axis its valves' +Z runs on, which way, its plane and its seats.
struct Deck {
    name: String,
    axis: i64,
    sign: Num,
    plane: Num,
    seats: Vec<(Val, f64, f64)>,
}
impl Deck {
    fn val(&self) -> Val {
        let seats = self.seats.iter().map(|(n, u, v)| Val::Tuple(vec![n.clone(), flt(*u), flt(*v)])).collect();
        Val::Tuple(vec![Val::Int(self.axis), self.sign.val(), self.plane.val(), Val::Tuple(seats)])
    }
}
fn decks_val(decks: &[Deck]) -> Val {
    Val::dict(decks.iter().map(|d| (s(&d.name), d.val())).collect())
}

fn tray_where(axis: f64, sign: f64) -> Option<&'static str> {
    [(0.0, 1.0, "west"), (0.0, -1.0, "east"), (1.0, 1.0, "fore"), (1.0, -1.0, "aft"), (2.0, 1.0, "bottom"), (2.0, -1.0, "top")]
        .iter()
        .find(|(a, s_, _)| *a == axis && *s_ == sign)
        .map(|(_, _, w)| *w)
}

/// `tray_name(axis, sign, plane, taken)`; `key` is the `(axis, sign)` lookup as the caller holds it.
fn tray_name(axis: f64, sign: f64, plane: &Num, taken: impl Fn(&str) -> Result<bool>, key: impl Fn() -> Val) -> Result<String> {
    let place = tray_where(axis, sign).with_context(|| format!("missing key {}", key().repr().unwrap_or_default()))?;
    let name = format!("valve-tray-{place}");
    if !taken(&name)? { Ok(name) } else { Ok(format!("{name}-{}", plane.fmt(".0f"))) }
}

fn decks_from(rt: &Rt, bounds: &Readings) -> Result<Vec<Deck>> {
    let mut groups: Vec<((i64, f64, f64), Vec<(String, [f64; 3])>)> = vec![];
    for name in bounds.names()? {
        if !tray_valve(rt, &name)? {
            continue;
        }
        let coil = name.replace("valve-", "coil-");
        if !bounds.has(&coil)? {
            return Err(coil_missing(&name, &coil));
        }
        let (lower, upper) = bounds.get(&name)?;
        let (coil_lower, coil_upper) = bounds.get(&coil)?;
        let delta = [0, 1, 2].map(|i| (coil_lower[i] + coil_upper[i] - lower[i] - upper[i]) / 2.0);
        let axis = argmax_abs(&delta);
        let sign = sign_of(delta[axis as usize]);
        let centre = [0, 1, 2].map(|i| (lower[i] + upper[i]) / 2.0);
        let plane = if sign > 0.0 { lower } else { upper }[axis as usize];
        let k = (axis, sign, num::round_to(plane, 6));
        match groups.iter_mut().find(|(g, _)| g.0 == k.0 && g.1 == k.1 && g.2 == k.2) {
            Some(group) => group.1.push((name, centre)),
            None => groups.push((k, vec![(name, centre)])),
        }
    }
    groups.sort_by(|a, b| {
        (a.0.0.cmp(&b.0.0)).then(num::order(a.0.1, b.0.1)).then(num::order(a.0.2, b.0.2))
    });
    let mut out: Vec<Deck> = vec![];
    for ((axis, sign, plane), mut members) in groups {
        let across: i64 = if axis != 0 { 0 } else { 1 };
        let along = (0..3).find(|i| *i != axis && *i != across).context("StopIteration")?;
        members.sort_by(|a, b| a.0.cmp(&b.0));
        let seats = members.iter().map(|(n, c)| (s(n), c[across as usize], c[along as usize])).collect();
        let name = tray_name(axis as f64, sign, &Num::F(plane), |n| Ok(out.iter().any(|d| d.name == n)), || {
            Val::Tuple(vec![Val::Int(axis), flt(sign)])
        })?;
        let deck = Deck { name: name.clone(), axis, sign: Num::F(sign), plane: Num::F(plane), seats };
        match out.iter_mut().find(|d| d.name == name) {
            Some(old) => *old = deck,
            None => out.push(deck),
        }
    }
    Ok(out)
}

fn valve_tray_decks(rt: &Rt, placed: &Val) -> Result<Vec<Deck>> {
    let st = st(rt)?;
    let placed = bodies(placed)?;
    let mut requested: Vec<String> = vec![];
    for (name, _) in &placed {
        let name = name.str()?;
        if tray_valve(rt, &name)? && !requested.contains(&name) {
            requested.push(name);
        }
    }
    let coils: Vec<String> = requested.iter().map(|n| n.replace("valve-", "coil-")).collect();
    for coil in coils {
        if !requested.contains(&coil) {
            requested.push(coil);
        }
    }
    let mut rows: Vec<(String, [f64; 3], [f64; 3])> = vec![];
    for (name, shape) in &placed {
        let name = name.str()?;
        if requested.contains(&name) {
            let b = st.bbox(shape)?;
            match rows.iter_mut().find(|r| r.0 == name) {
                Some(row) => *row = (name, b.lower(), b.upper()),
                None => rows.push((name, b.lower(), b.upper())),
            }
        }
    }
    decks_from(rt, &Readings::Typed(&rows))
}

/// `_valve_tray_stations`: each deck as `(plane, sign, ((x, z), ...))`, in deck-name order.
fn valve_tray_rows(decks: &[&Deck]) -> Result<Val> {
    let mut sorted: Vec<&&Deck> = decks.iter().collect();
    sorted.sort_by(|a, b| a.name.cmp(&b.name));
    let mut out = vec![];
    for d in sorted {
        if d.axis != 1 {
            let letter = "xyz".chars().nth(d.axis.rem_euclid(3) as usize).unwrap_or('?');
            return Err(err(
                "ValueError",
                format!(
                    "a valve deck stands its valves' own +Z on {letter} and `enclosure._valve_trays` fuses a plate across the box's width on a Y plane — a deck on another axis needs the builder to learn it, not this table."
                ),
            ));
        }
        let seats = d.seats.iter().map(|(_, u, v)| fpair(num::round_to(*u, 6), num::round_to(*v, 6))).collect();
        out.push(Val::Tuple(vec![d.plane.val(), d.sign.val(), Val::Tuple(seats)]));
    }
    Ok(Val::Tuple(out))
}

/// A caller's decks mapping read back into decks.
fn decks_of(decks: &Val) -> Result<Vec<Deck>> {
    let mut out = vec![];
    for item in call0(decks, "items")?.iter()? {
        let nv = py::unpack(&item, 2)?;
        let row = py::unpack(&nv[1], 4)?;
        let seats = row[3]
            .iter()?
            .iter()
            .map(|seat| {
                let r = py::unpack(seat, 3)?;
                Ok((r[0].clone(), r[1].num()?, r[2].num()?))
            })
            .collect::<Result<_>>()?;
        out.push(Deck { name: nv[0].str()?, axis: row[0].integer()?, sign: Num::of(&row[1])?, plane: Num::of(&row[2])?, seats });
    }
    Ok(out)
}

const PUMP_TRAY_SLIP: f64 = 0.2;

fn pump_up(rt: &Rt, placed: &Val, head: &str) -> Result<(i64, f64)> {
    let st = st(rt)?;
    let can = head.replace("-head", "-motor");
    if !placed.contains(&s(&can))? {
        return Err(err(
            "KeyError",
            format!(
                "{head} is placed and {can} is not, so nothing says which way it faces — a Kamoer's can stands on the boss behind its head, and that is what tells a tray which of the head's six faces it lies on."
            ),
        ));
    }
    let hb = st.bbox(&placed.get(s(head))?)?;
    let cb = st.bbox(&placed.get(s(&can))?)?;
    let d = [0, 1, 2].map(|i| (cb.lo(i) + cb.hi(i) - hb.lo(i) - hb.hi(i)) / 2.0);
    let axis = argmax_abs(&d);
    Ok((axis, sign_of(d[axis as usize])))
}

struct PumpSeat {
    head: String,
    axis: i64,
    sign: f64,
    centre: [f64; 3],
}
impl PumpSeat {
    fn val(&self) -> Val {
        Val::Tuple(vec![Val::Int(self.axis), flt(self.sign), f3(self.centre)])
    }
}

fn pump_seats_from(rt: &Rt, bounds: &Readings) -> Result<Vec<PumpSeat>> {
    let st = st(rt)?;
    let mut heads = bounds.names()?;
    heads.sort();
    let mut out: Vec<PumpSeat> = vec![];
    for head in heads {
        if !(head.starts_with("pump-") && head.ends_with("-head")) {
            continue;
        }
        let can = head.replace("-head", "-motor");
        if !bounds.has(&can)? {
            return Err(err("KeyError", format!("{head} is placed and {can} is not")));
        }
        let (lower, upper) = bounds.get(&head)?;
        let (can_lower, can_upper) = bounds.get(&can)?;
        let d = [0, 1, 2].map(|i| (can_lower[i] + can_upper[i] - lower[i] - upper[i]) / 2.0);
        let axis = argmax_abs(&d);
        let sign = sign_of(d[axis as usize]);
        let mut centre = [0, 1, 2].map(|i| (can_lower[i] + can_upper[i]) / 2.0);
        centre[axis as usize] = if sign > 0.0 { upper } else { lower }[axis as usize];
        if axis == 2 && sign == 1.0 {
            centre[1] -= an(&st.tray, "rear_axis_y_shift")?;
            centre[2] += an(&st.enc.attr("_interface")?, "pump_seated_drop")?;
        }
        let seat = PumpSeat { head: head.clone(), axis, sign, centre: centre.map(|c| num::round_to(c, 6)) };
        match out.iter_mut().find(|p| p.head == head) {
            Some(old) => *old = seat,
            None => out.push(seat),
        }
    }
    Ok(out)
}

fn pump_tray_seats(rt: &Rt, placed: &Val) -> Result<Vec<PumpSeat>> {
    let st = st(rt)?;
    let mut rows: Vec<(String, [f64; 3], [f64; 3])> = vec![];
    for item in call0(placed, "items")?.iter()? {
        let ns = py::unpack(&item, 2)?;
        let name = ns[0].str()?;
        if name.starts_with("pump-") && (name.ends_with("-head") || name.ends_with("-motor")) {
            let b = st.bbox(&ns[1])?;
            match rows.iter_mut().find(|r| r.0 == name) {
                Some(row) => *row = (name, b.lower(), b.upper()),
                None => rows.push((name, b.lower(), b.upper())),
            }
        }
    }
    pump_seats_from(rt, &Readings::Typed(&rows))
}

fn pump_seats_val(seats: &[PumpSeat]) -> Val {
    Val::dict(seats.iter().map(|p| (s(&p.head), p.val())).collect())
}

fn pump_tray_stations(rt: &Rt, placed: &Val) -> Result<Val> {
    let mut seats = pump_tray_seats(rt, placed)?;
    seats.sort_by(|a, b| a.head.cmp(&b.head));
    let mut out = vec![];
    for p in &seats {
        if !(p.axis == 2 && p.sign == 1.0) {
            let letter = "xyz".chars().nth(p.axis.rem_euclid(3) as usize).unwrap_or('?');
            return Err(err(
                "ValueError",
                format!(
                    "{} stands its can on {}{letter} and `enclosure.build_pump_cartridge` lays a plate on a Z face — a pump on another axis needs the builder to learn it, not this table.",
                    p.head,
                    if p.sign > 0.0 { "+" } else { "-" }
                ),
            ));
        }
        out.push(f3(p.centre));
    }
    Ok(Val::Tuple(out))
}

// ---------------------------------------------------------------------------------------------
// The bay bulkhead's collet plate (Python lines 658-687).

fn collet_plate_spec(rt: &Rt, mcarry: &Val, tray_stations: &Val, valve_trays: &Val) -> Result<Val> {
    let st = st(rt)?;
    let ml = &st.ml;
    let mut holes: Vec<(f64, f64)> = vec![];
    let (upper_ports, return_ports) = (Val::dict(vec![]), Val::dict(vec![]));
    let mut names = py::strings(&ml.attr("BARB_OF")?)?;
    names.sort();
    for name in names {
        let station = py::call(&ml.attr("barb_station")?, vec![s(&name)])?;
        let placed = py::call(mcarry, vec![Val::Tuple(vec![station, f3([0.0, 0.0, 1.0])])])?;
        let pa = py::unpack(&placed, 2)?;
        let p = py::unpack(&pa[0], 3)?;
        let x = num::round_to(p[0].num()?, 6);
        holes.push((x, num::round_to(p[2].num()?, 6)));
        let valves = py::unpack(&ml.attr("PUMP_VALVES")?.get(s(&name))?, 2)?;
        for (ports, valve, end) in [(&upper_ports, &valves[0], "front"), (&return_ports, &valves[1], "back")] {
            let port = py::call(&ml.attr("port")?, vec![valve.clone(), s(end)])?;
            let axis = py::call(&ml.attr("port_axis")?, vec![valve.clone(), s(end)])?;
            let r = py::unpack(&py::call(mcarry, vec![Val::Tuple(vec![port, axis])])?, 2)?;
            ports.set(s(num::fstr(x)), sdict(vec![("point", tuple_of(&r[0])?), ("axis", tuple_of(&r[1])?), ("valve", valve.clone())]))?;
        }
    }
    holes.sort_by(|a, b| num::order(a.0, b.0).then(num::order(a.1, b.1)));
    let fore = num::round_to(call0(ml, "pump_wall_fore_y")?.num()?, 6);
    let plumbing = st.dock.attr("plumbing")?;
    let r6 = |v: Val| -> Result<Val> { Ok(flt(num::round_to(v.num()?, 6))) };
    let holes = Val::Tuple(holes.iter().map(|(x, z)| fpair(*x, *z)).collect());
    let aft_y = r6(call1(&plumbing, "plate_aft_y", flt(fore))?)?;
    let wall_aft_y = r6(call1(&st.dock, "wall_aft_y", flt(fore))?)?;
    let x0 = ix(&call0(&st.enc, "interior_x")?, 0)?;
    let x1 = ix(&call0(&st.enc, "interior_x")?, 1)?;
    let z0 = st.enc.attr("z_seam")?;
    let hole_d = Num::F(2.0).mul(anum(&st.dock, "HOLE_R")?).val();
    let seat_z = r6(ix(&call1(&st.enc, "bay_floor_z", tray_stations.clone())?, 1)?)?;
    let valve_trays = tuple_of(valve_trays)?;
    let bed = anum(&st.enc, "z_seam")?.add(anum(&st.enc, "slide_slip")?).val();
    let tee_axis_y = r6(call1(&plumbing, "tee_axis_y", flt(fore))?)?;
    let seated = r6(call1(&plumbing, "tip_y", flt(fore))?)?;
    let cut = r6(ml.attr("PUMP_TUBE_CUT")?)?;
    let tube_bottom = r6(call1(&plumbing, "tip_y", flt(fore))?)?;
    Ok(sdict(vec![
        ("holes", holes),
        ("fore_y", flt(fore)),
        ("aft_y", aft_y),
        ("wall_aft_y", wall_aft_y),
        ("x0", x0),
        ("x1", x1),
        ("z0", z0),
        ("z1", flt(218.85)),
        ("hole_d", hole_d),
        ("seat_z", seat_z),
        ("upper_ports", upper_ports),
        ("return_ports", return_ports),
        ("valve_trays", valve_trays),
        ("fixture_print_bed_z", bed),
        ("tee_axis_y", tee_axis_y),
        ("seated_tube_bottom_y", seated),
        ("pump_tube_cut", cut),
        ("tube_bottom_y", tube_bottom),
        ("assembly_state", s("seated")),
    ]))
}

// ---------------------------------------------------------------------------------------------
// The core's chase and holds, its riders and its anchors (Python lines 690-851).

const COND_PROBE_INSET: f64 = 0.5;
const COND_AIR_INSET: f64 = 0.05;
const COND_UNPRINTED: &str = "NOT PRINTED — no piece owns this station";

fn core_hold_lanes(st: &State) -> Result<[(Num, Num); 2]> {
    let edge = *late!(st.late.core_hold_east_edge);
    Ok([(Num::F(-43.6), Num::F(-37.5)), (edge.sub(Num::F(9.0)), edge)])
}

fn vent_chase(rt: &Rt, foam: &Val, foam_carry: &Val) -> Result<Val> {
    let st = st(rt)?;
    let tip = st.foam.attr("routes")?.attr("routes")?.get(s("prv-vent"))?.get(Val::Int(-1))?;
    let placed = py::unpack(&py::call(foam_carry, vec![Val::Tuple(vec![tip, f3([0.0, 1.0, 0.0])])])?, 2)?;
    let at = &placed[0];
    let x = Num::F(an(&st.boxv(foam)?, "xmin")?).sub(anum(&st.cci, "casing_foil_allowance")?);
    Ok(Val::Tuple(vec![Val::Tuple(vec![x.val(), ix(at, 1)?, ix(at, 2)?])]))
}

fn core_holds(rt: &Rt, foam: &Val) -> Result<Val> {
    let st = st(rt)?;
    let b = st.boxv(foam)?;
    let crown = cap_face(rt, foam)?;
    let mut out = vec![];
    for (x0, x1) in core_hold_lanes(&st)? {
        let aft = Num::F(an(&b, "ymax")?).add(anum(&st.cci, "casing_foil_allowance")?);
        out.push(Val::Tuple(vec![x0.val(), x1.val(), aft.val(), crown.val()]));
    }
    Ok(Val::Tuple(out))
}

const FRONT_RIDERS: [&str; 9] = [
    "valve-v-",
    "coil-v-",
    "tee-y-",
    "stem-elbow-",
    "turn-",
    "step-",
    "reservoir-a-fill-turn",
    "reservoir-a-draw-turn",
    "reservoir-b-fill-turn",
];
const CORE_RIDERS: [&str; 11] = [
    "g-ganen-pump",
    "valve-v-a",
    "valve-v-b",
    "vk-solenoid",
    "coil-v-a",
    "coil-v-b",
    "stub-fluid-2",
    "stub-fluid-4",
    "discharge-chain",
    "pump-elbow-suction",
    "pump-elbow-discharge",
];
const CORE_RIDE_LATER: [&str; 3] = ["foam-assembly", "funnel", "nameplate"];
const CORE_RIDE_RUNS: [&str; 3] = ["tube-", "turn-", "step-"];
const BEDDED_TOL: f64 = 0.01;
const JOINT_STATIONS: [(&str, &str, &str); 3] = [
    ("refrig-1", "compressor.refrig-discharge", "condenser+fan.refrig-inlet"),
    ("refrig-2", "condenser+fan.refrig-outlet", "foam-assembly.evap-inlet"),
    ("refrig-3", "foam-assembly.evap-outlet", "compressor.refrig-suction"),
];
const MADE_BY_MATE: &str = "mate";
const MADE_BY_TUBE: &str = "drawn";
const JOINT_TOL: f64 = 0.05;

fn refrigerant_mates(joints: &Val) -> Result<Val> {
    let out = Val::list(vec![]);
    for j in joints.iter()? {
        if !interop::eq(&j.attr("made")?, &s(MADE_BY_MATE))? {
            continue;
        }
        let mm = j.attr("mm")?;
        if matches!(mm, Val::None) || mm.num()? > JOINT_TOL {
            continue;
        }
        out.attr("append")?.call(vec![Val::Tuple(vec![j.attr("id")?, j.attr("frm")?, j.attr("to")?, j.attr("mm")?])], vec![])?;
    }
    Ok(out)
}

const MOUNT_TOL: f64 = 0.001;

fn cap_anchor(rt: &Rt, name: &Val) -> Result<Val> {
    let st = st(rt)?;
    let xy = py::unpack(&call1(&st.foam, "cap_anchor_station", name.clone())?, 2)?;
    let z = anum(&st.foam, "cap_face_z")?.add(Num::of(&call1(&st.cci, "cap_anchor_axis_over_face", name.clone())?)?);
    let axis = call0(&st.foam, "cap_conduit_axis_out")?;
    Ok(Val::Tuple(vec![Val::Tuple(vec![xy[0].clone(), xy[1].clone(), z.val()]), axis]))
}

fn cap_side_anchor(rt: &Rt, name: &Val) -> Result<Val> {
    let st = st(rt)?;
    let xy = py::unpack(&call1(&st.foam, "cap_side_anchor_station", name.clone())?, 2)?;
    let face = anum(&st.foam, "cap_face_z")?;
    let z = face.add(anum(&st.cci.attr("cap_side_anchors")?.get(name.clone())?, "over_face")?);
    Ok(Val::Tuple(vec![Val::Tuple(vec![xy[0].clone(), xy[1].clone(), z.val()]), f3([0.0, -1.0, 0.0])]))
}

fn cap_conduit(rt: &Rt, name: &Val) -> Result<Val> {
    call1(&st(rt)?.foam, "cap_conduit_mouth", name.clone())
}

const WATER_PUMP_WEST_LIMIT: f64 = -50.2;

fn water_pump_port_lane_limit(rt: &Rt) -> Result<Num> {
    let st = st(rt)?;
    let east = Num::of(&late!(st.late.panel_x).get(s("bulkhead-flavor-a"))?)?;
    Ok(east.add(anum(&st.jg, "BODY_D")?.div(Num::F(2.0))).add(Num::F(PORT_LANE_CLEAR)))
}

const DISCHARGE_ELBOW_DIP: f64 = 25.0;

fn pump_elbows() -> Val {
    let dip = num::radians(DISCHARGE_ELBOW_DIP);
    sdict(vec![
        ("suction", Val::Tuple(vec![s("pump-elbow-suction"), f3([0.0, -1.0, 0.0])])),
        ("discharge", Val::Tuple(vec![s("pump-elbow-discharge"), f3([0.0, -num::cos(dip), -num::sin(dip)])])),
    ])
}

// ---------------------------------------------------------------------------------------------
// The +Y wall's fittings, rings and pockets (Python lines 853-1062).

fn bulkhead_seat_y(rt: &Rt) -> Result<Num> {
    let st = st(rt)?;
    Ok(anum(&st.enc, "rear_plane_y")?.add(anum(&st.enc, "wall")?))
}

fn bulkhead_mouth_y(rt: &Rt) -> Result<Num> {
    let st = st(rt)?;
    Ok(bulkhead_seat_y(rt)?.add(anum(&st.jg, "far_ring_face_y")?))
}

/// Which provider module a `Y_WALL_FITTINGS` row names.
#[derive(Clone, Copy)]
enum Fit {
    Jg,
    DrainBulkhead,
    Neofit,
}
const Y_WALL_FITTINGS: [(&str, Fit, &str, &str, &str); 6] = [
    ("bulkhead-water", Fit::Jg, "union", "water", "water"),
    ("bulkhead-carb", Fit::Jg, "union", "carb", "carb"),
    ("bulkhead-flavor-a", Fit::DrainBulkhead, "drain", "flavor-a", "flavor"),
    ("bulkhead-flavor-b", Fit::DrainBulkhead, "drain", "flavor-b", "flavor"),
    ("co2-inlet", Fit::Neofit, "neofit", "co2", "co2"),
    ("bulkhead-drain", Fit::DrainBulkhead, "drain", "drain", "drain"),
];
impl State {
    fn fit(&self, f: Fit) -> &Val {
        match f {
            Fit::Jg => &self.jg,
            Fit::DrainBulkhead => &self.drain_bulkhead,
            Fit::Neofit => &self.neofit,
        }
    }
    fn y_wall_fitting(&self, name: &Val) -> Result<&Val> {
        let found = match name {
            Val::Str(text) => Y_WALL_FITTINGS.iter().find(|r| r.0 == text.as_str()),
            _ => None,
        };
        found.map(|r| self.fit(r.1)).with_context(|| format!("missing key {}", name.repr().unwrap_or_default()))
    }
}
fn y_wall_fittings_val(st: &State) -> Val {
    sdict(Y_WALL_FITTINGS.iter().map(|(n, f, r, w, fl)| (*n, Val::Tuple(vec![st.fit(*f).clone(), s(*r), s(*w), s(*fl)]))).collect())
}

/// `{first: value, **rest}` with more keys after.
fn carries_of(first: Vec<(&str, Val)>, rest: &Val, after: Vec<(&str, Val)>) -> Result<Val> {
    let d = sdict(first);
    for item in call0(rest, "items")?.iter()? {
        let kv = py::unpack(&item, 2)?;
        d.set(kv[0].clone(), kv[1].clone())?;
    }
    for (k, v) in after {
        d.set(s(k), v)?;
    }
    Ok(d)
}

fn y_wall_ports(rt: &Rt, bulkhead_carry: &Val, panel_carries: &Val) -> Result<Val> {
    let st = st(rt)?;
    let carries = carries_of(vec![("bulkhead-water", bulkhead_carry.clone())], panel_carries, vec![])?;
    let slip = late!(st.late.port_hole_slip).val();
    let out = Val::list(vec![]);
    for item in call0(&carries, "items")?.iter()? {
        let nc = py::unpack(&item, 2)?;
        let fitting = st.y_wall_fitting(&nc[0])?;
        let x = ix(&ix(&py::call(&nc[1], vec![call1(fitting, "port", flt(-1.0))?])?, 0)?, 0)?;
        let z = ix(&ix(&py::call(&nc[1], vec![call1(fitting, "port", flt(-1.0))?])?, 0)?, 2)?;
        let d = call1(fitting, "panel_hole_d", slip.clone())?;
        out.attr("append")?.call(vec![Val::Tuple(vec![s("round"), x, z, d])], vec![])?;
    }
    Ok(out)
}

const BULKHEAD_RING_RIM: f64 = 3.0;

fn port_clamp_stack(rt: &Rt, t: Num) -> Result<Num> {
    let st = st(rt)?;
    let stack = anum(&st.enc, "wall")?.add(*late!(st.late.port_boss_proud)).add(anum(&st.fits, "slip")?);
    Ok(t.max(stack))
}

fn port_pocket_d(rt: &Rt, ring: &Val) -> Result<Num> {
    let st = st(rt)?;
    Ok(Num::of(&call1(&st.ring, "od", ring.clone())?)?.add(Num::F(2.0).mul(*late!(st.late.bulkhead_ring_slip))))
}

fn port_pocket_rise(rt: &Rt, which: &Val) -> Result<Num> {
    let st = st(rt)?;
    let rise = if matches!(which, Val::None) { anum(&st.ring, "RISE")? } else { Num::of(&call1(&st.ring, "rise", which.clone())?)? };
    Ok(rise.add(*late!(st.late.bulkhead_ring_slip)))
}

fn wall_stations(rt: &Rt, bulkhead_carry: &Val, panel_carries: &Val, co2_carry: &Val, drain_carry: &Val) -> Result<Val> {
    let st = st(rt)?;
    let carries = carries_of(
        vec![("bulkhead-water", bulkhead_carry.clone())],
        panel_carries,
        vec![("co2-inlet", co2_carry.clone()), ("bulkhead-drain", drain_carry.clone())],
    )?;
    let out = Val::dict(vec![]);
    for (name, f, ring, which, fluid) in Y_WALL_FITTINGS {
        let fitting = st.fit(f);
        let carry = carries.get(s(name))?;
        let at = py::unpack(&ix(&py::call(&carry, vec![call1(fitting, "port", flt(-1.0))?])?, 0)?, 3)?;
        out.set(s(name), Val::Tuple(vec![at[0].clone(), at[2].clone(), fitting.clone(), s(ring), s(which), s(fluid)]))?;
    }
    Ok(out)
}

fn y_wall_field(rt: &Rt, stations: &Val) -> Result<Val> {
    let st = st(rt)?;
    let slip = *late!(st.late.bulkhead_ring_slip);
    let mut rows = vec![];
    for row in call0(stations, "values")?.iter()? {
        let r = py::unpack(&row, 6)?;
        let (ring, which) = (&r[3], &r[4]);
        let d = port_pocket_d(rt, ring)?;
        let rise = port_pocket_rise(rt, which)?;
        let bottom = Num::of(&call1(&st.ring, "bottom", ring.clone())?)?.add(slip);
        rows.push(Val::Tuple(vec![r[0].clone(), r[1].clone(), d.val(), rise.val(), bottom.val()]));
    }
    py::call(&st.enc.attr("PortField")?, vec![late!(st.late.port_boss_proud).val(), flt(BULKHEAD_RING_RIM), Val::Tuple(rows)])
}

const CUSTOMER_TUBE_STATIONS: [&str; 2] = ["bulkhead-water", "co2-inlet"];
const COLLAR_OFF_COLLET: f64 = 8.0;
const COLLAR_TUBE_TAIL: f64 = 10.0;
const NAMEPLATE_MARGIN: f64 = 5.0;
const NAMEPLATE: &str = "nameplate";
const NAMEPLATE_INK: &str = "nameplate-ink";
const NAMEPLATE_PSU_CLEAR: f64 = 1.0;
const NAMEPLATE_CAP_CLEAR: f64 = 1.0;

fn nameplate_cut(rt: &Rt, station: &Val) -> Result<Val> {
    let st = st(rt)?;
    let at = py::splat(&st.np.attr("interface")?.attr("station")?, station)?;
    py::call_kw(&at.attr("_replace")?, vec![], vec![("thick", st.np.attr("THICK")?)])
}

const DECK_CLEAR: f64 = 6.0;
const DECK_FALL_LIMIT: f64 = 60.0;
const PORT_NUT_GAP: f64 = 7.0;
const PORT_DECK_EXTRA: f64 = 7.5;

// ---------------------------------------------------------------------------------------------
// Install, Python lines 454-1062.

fn install_2(rt: &Rt, ns: &Ns) -> Result<()> {
    let kept = st(rt)?;
    ns.def(rt, "_valve_up", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["placed", "name"], &[])?;
        let (placed, name) = (a.req("placed")?, a.string("name")?);
        let (axis, sign) = valve_up(rt, &placed, &name)?;
        Ok(Val::Tuple(vec![Val::Int(axis), flt(sign)]))
    })?;
    ns.def(rt, "_bodies", |_, args, kw| {
        let mut a = py::bind(args, kw, &["placed"], &[])?;
        Ok(Val::dict(bodies(&a.req("placed")?)?))
    })?;
    ns.def(rt, "_tray_valve", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        Ok(Val::Bool(tray_valve(rt, &a.string("name")?)?))
    })?;
    ns.def(rt, "valve_tray_decks_from_bounds", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["bounds"], &[])?;
        Ok(decks_val(&decks_from(rt, &Readings::Val(&a.req("bounds")?))?))
    })?;
    ns.def(rt, "valve_tray_decks", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["placed"], &[])?;
        Ok(decks_val(&valve_tray_decks(rt, &a.req("placed")?)?))
    })?;
    ns.def(rt, "tray_name", |_, args, kw| {
        let mut a = py::bind(args, kw, &["axis", "sign", "plane", "taken"], &[])?;
        let (axis, sign, plane, taken) = (a.req("axis")?, a.req("sign")?, Num::of(&a.req("plane")?)?, a.req("taken")?);
        let key = || Val::Tuple(vec![axis.clone(), sign.clone()]);
        Ok(s(tray_name(axis.num()?, sign.num()?, &plane, |n| taken.contains(&s(n)), key)?))
    })?;
    ns.def(rt, "valve_tray_stations", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["placed"], &[])?;
        let decks = valve_tray_decks(rt, &a.req("placed")?)?;
        valve_tray_rows(&decks.iter().collect::<Vec<_>>())
    })?;
    ns.def(rt, "valve_tray_stations_from_bounds", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["bounds"], &[])?;
        let decks = decks_from(rt, &Readings::Val(&a.req("bounds")?))?;
        valve_tray_rows(&decks.iter().collect::<Vec<_>>())
    })?;
    ns.def(rt, "_valve_tray_stations", |_, args, kw| {
        let mut a = py::bind(args, kw, &["decks"], &[])?;
        let decks = decks_of(&a.req("decks")?)?;
        valve_tray_rows(&decks.iter().collect::<Vec<_>>())
    })?;
    ns.set("PUMP_TRAY_SLIP", flt(PUMP_TRAY_SLIP))?;
    ns.def(rt, "_pump_up", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["placed", "head"], &[])?;
        let (placed, head) = (a.req("placed")?, a.string("head")?);
        let (axis, sign) = pump_up(rt, &placed, &head)?;
        Ok(Val::Tuple(vec![Val::Int(axis), flt(sign)]))
    })?;
    ns.def(rt, "pump_tray_seats", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["placed"], &[])?;
        Ok(pump_seats_val(&pump_tray_seats(rt, &a.req("placed")?)?))
    })?;
    ns.def(rt, "pump_tray_seats_from_bounds", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["bounds"], &[])?;
        Ok(pump_seats_val(&pump_seats_from(rt, &Readings::Val(&a.req("bounds")?))?))
    })?;
    ns.def(rt, "pump_tray_stations", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["placed"], &[])?;
        pump_tray_stations(rt, &a.req("placed")?)
    })?;
    ns.def(rt, "collet_plate_spec", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["mcarry", "tray_stations", "valve_trays"], &[])?;
        let (mcarry, stations) = (a.req("mcarry")?, a.req("tray_stations")?);
        let trays = a.opt("valve_trays").unwrap_or(Val::Tuple(vec![]));
        collet_plate_spec(rt, &mcarry, &stations, &trays)
    })?;
    ns.set("COND_PROBE_INSET", flt(COND_PROBE_INSET))?;
    ns.set("COND_AIR_INSET", flt(COND_AIR_INSET))?;
    ns.set("_COND_UNPRINTED", s(COND_UNPRINTED))?;
    let spec = call0(&kept.above, "specification")?;
    let edge = key(&key(&key(&spec, "rear_wall")?, "interior_panel_relief")?, "xmin")?;
    ns.set("_CORE_HOLD_EAST_EDGE", edge.clone())?;
    let _ = kept.late.core_hold_east_edge.set(Num::of(&edge)?);
    let lanes = core_hold_lanes(&kept)?;
    ns.set("CORE_HOLD_LANES", Val::Tuple(lanes.iter().map(|(a, b)| Val::Tuple(vec![a.val(), b.val()])).collect()))?;
    ns.def(rt, "vent_chase", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["foam", "foam_carry"], &[])?;
        vent_chase(rt, &a.req("foam")?, &a.req("foam_carry")?)
    })?;
    ns.def(rt, "core_holds", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["foam"], &[])?;
        core_holds(rt, &a.req("foam")?)
    })?;
    ns.set("FRONT_RIDERS", strs(&FRONT_RIDERS))?;
    ns.set("CORE_RIDERS", strs(&CORE_RIDERS))?;
    ns.set("CORE_RIDE_LATER", strs(&CORE_RIDE_LATER))?;
    ns.set("CORE_RIDE_RUNS", strs(&CORE_RIDE_RUNS))?;
    ns.set("BEDDED_TOL", flt(BEDDED_TOL))?;
    ns.set("JOINT_STATIONS", sdict(JOINT_STATIONS.iter().map(|(id, a, b)| (*id, strs(&[a, b]))).collect()))?;
    let mut ids = vec![];
    for row in kept.card.attr("REFRIGERANT_SEGMENTS")?.iter()? {
        ids.push(py::unpack(&row, 3)?[0].clone());
    }
    ns.set("REFRIGERANT_IDS", Val::Tuple(ids.clone()))?;
    let _ = kept.late.refrigerant_ids.set(ids);
    ns.set("MADE_BY_MATE", s(MADE_BY_MATE))?;
    ns.set("MADE_BY_TUBE", s(MADE_BY_TUBE))?;
    ns.set("JOINT_TOL", flt(JOINT_TOL))?;
    ns.def(rt, "refrigerant_mates", |_, args, kw| {
        let mut a = py::bind(args, kw, &["joints"], &[])?;
        refrigerant_mates(&a.req("joints")?)
    })?;
    ns.set("MOUNT_TOL", flt(MOUNT_TOL))?;
    ns.def(rt, "pump_mount_rows", |_, args, kw| {
        py::bind(args, kw, &["foam_carry", "water_pump_carry"], &[])?;
        Ok(Val::list(vec![]))
    })?;
    ns.def(rt, "cap_anchor", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        cap_anchor(rt, &a.req("name")?)
    })?;
    ns.def(rt, "cap_side_anchor", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        cap_side_anchor(rt, &a.req("name")?)
    })?;
    ns.def(rt, "cap_conduit", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        cap_conduit(rt, &a.req("name")?)
    })?;
    ns.def(rt, "water_pump_west_limit", |_, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(flt(WATER_PUMP_WEST_LIMIT))
    })?;
    ns.def(rt, "water_pump_port_lane_limit", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(water_pump_port_lane_limit(rt)?.val())
    })?;
    ns.set("DISCHARGE_ELBOW_DIP", flt(DISCHARGE_ELBOW_DIP))?;
    ns.set("PUMP_ELBOWS", pump_elbows())?;
    let slip = kept.fits.attr("slip")?;
    ns.set("CHAIN_SEAT_SLIP", slip.clone())?;
    let _ = kept.late.chain_seat_slip.set(Num::of(&slip)?);
    let hole_slip = Num::F(2.0).mul(anum(&kept.fits, "slip")?);
    ns.set("PORT_HOLE_SLIP", hole_slip.val())?;
    let _ = kept.late.port_hole_slip.set(hole_slip);
    ns.def(rt, "bulkhead_seat_y", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(bulkhead_seat_y(rt)?.val())
    })?;
    ns.def(rt, "bulkhead_mouth_y", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(bulkhead_mouth_y(rt)?.val())
    })?;
    ns.def(rt, "y_wall_ports", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["bulkhead_carry", "panel_carries"], &[])?;
        y_wall_ports(rt, &a.req("bulkhead_carry")?, &a.req("panel_carries")?)
    })?;
    ns.set("Y_WALL_FITTINGS", y_wall_fittings_val(&kept))?;
    ns.def(rt, "ring_name", |_, args, kw| {
        let mut a = py::bind(args, kw, &["which"], &[])?;
        Ok(s(format!("bulkhead-ring-{}", sv(&a.req("which")?)?)))
    })?;
    ns.def(rt, "word_name", |_, args, kw| {
        let mut a = py::bind(args, kw, &["which"], &[])?;
        Ok(s(format!("bulkhead-ring-{}-word", sv(&a.req("which")?)?)))
    })?;
    let ring_slip = kept.fits.attr("slip")?;
    ns.set("BULKHEAD_RING_SLIP", ring_slip.clone())?;
    let _ = kept.late.bulkhead_ring_slip.set(Num::of(&ring_slip)?);
    ns.set("BULKHEAD_RING_RIM", flt(BULKHEAD_RING_RIM))?;
    let proud = kept.ring.attr("THICK")?;
    ns.set("PORT_BOSS_PROUD", proud.clone())?;
    let _ = kept.late.port_boss_proud.set(Num::of(&proud)?);
    ns.def(rt, "port_clamp_stack", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["t"], &[])?;
        Ok(port_clamp_stack(rt, Num::of(&a.req("t")?)?)?.val())
    })?;
    let union = s("union");
    ns.def(rt, "port_pocket_d", move |rt, args, kw| {
        let mut a = py::bind(args, kw, &["ring"], &[])?;
        let ring = a.opt("ring").unwrap_or_else(|| union.clone());
        Ok(port_pocket_d(rt, &ring)?.val())
    })?;
    ns.def(rt, "port_pocket_rise", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["which"], &[])?;
        Ok(port_pocket_rise(rt, &a.opt("which").unwrap_or(Val::None))?.val())
    })?;
    ns.def(rt, "wall_stations", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["bulkhead_carry", "panel_carries", "co2_carry", "drain_carry"], &[])?;
        let (b, p, c, d) = (a.req("bulkhead_carry")?, a.req("panel_carries")?, a.req("co2_carry")?, a.req("drain_carry")?);
        wall_stations(rt, &b, &p, &c, &d)
    })?;
    ns.def(rt, "y_wall_field", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["stations"], &[])?;
        y_wall_field(rt, &a.req("stations")?)
    })?;
    ns.set("CUSTOMER_TUBE_STATIONS", strs(&CUSTOMER_TUBE_STATIONS))?;
    ns.set("COLLAR_OFF_COLLET", flt(COLLAR_OFF_COLLET))?;
    ns.set("COLLAR_TUBE_TAIL", flt(COLLAR_TUBE_TAIL))?;
    ns.def(rt, "customer_tube_name", |_, args, kw| {
        let mut a = py::bind(args, kw, &["which"], &[])?;
        Ok(s(format!("tube-customer-{}", sv(&a.req("which")?)?)))
    })?;
    ns.def(rt, "collar_name", |_, args, kw| {
        let mut a = py::bind(args, kw, &["which"], &[])?;
        Ok(s(format!("tube-collar-{}", sv(&a.req("which")?)?)))
    })?;
    ns.def(rt, "collar_word_name", |_, args, kw| {
        let mut a = py::bind(args, kw, &["which"], &[])?;
        Ok(s(format!("tube-collar-{}-word", sv(&a.req("which")?)?)))
    })?;
    ns.set("NAMEPLATE_MARGIN", flt(NAMEPLATE_MARGIN))?;
    ns.set("NAMEPLATE", s(NAMEPLATE))?;
    ns.set("NAMEPLATE_INK", s(NAMEPLATE_INK))?;
    ns.set("NAMEPLATE_PSU_CLEAR", flt(NAMEPLATE_PSU_CLEAR))?;
    ns.set("NAMEPLATE_CAP_CLEAR", flt(NAMEPLATE_CAP_CLEAR))?;
    ns.def(rt, "nameplate_cut", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["station"], &[])?;
        nameplate_cut(rt, &a.req("station")?)
    })?;
    ns.set("DECK_CLEAR", flt(DECK_CLEAR))?;
    ns.set("DECK_FALL_LIMIT", flt(DECK_FALL_LIMIT))?;
    ns.set("PORT_NUT_GAP", flt(PORT_NUT_GAP))?;
    ns.set("PORT_DECK_EXTRA", flt(PORT_DECK_EXTRA))?;
    let hardware = ixn(&call0(&kept.jg, "panel_footprint")?, 0)?.add(Num::F(PORT_NUT_GAP)).add(Num::F(PORT_DECK_EXTRA));
    ns.set("PORT_HARDWARE_PITCH", hardware.val())?;
    let _ = kept.late.port_hardware_pitch.set(hardware);
    let field = port_pocket_d(rt, &s("union"))?.add(Num::F(BULKHEAD_RING_RIM));
    ns.set("PORT_FIELD_PITCH", field.val())?;
    let _ = kept.late.port_field_pitch.set(field);
    let pitch = hardware.max(field);
    ns.set("PORT_PITCH", pitch.val())?;
    let _ = kept.late.port_pitch.set(pitch);
    let wall = anum(&kept.enc, "wall")?;
    let thick = anum(&kept.ring, "THICK")?;
    _stated_bounds::state_bound(
        rt,
        s("port-pocket-floor"),
        s("Every pocket leaves wall under the chip it holds"),
        s(format!("a chip under `enclosure.wall` {} mm", wall.fmt("g"))),
        &Val::Bool(thick.f() < wall.sub(Num::F(1e-9)).f()),
        &s(format!(
            "the pocket is cut {} mm into a wall {} mm thick and leaves {} mm of floor under the chip.",
            thick.fmt("g"),
            wall.fmt("g"),
            wall.sub(thick).fmt(".2f")
        )),
    )?;
    let proud = *late!(kept.late.port_boss_proud);
    let port_stack = _stated_bounds::bound(
        rt,
        s("port-clamp-stack"),
        s("Every fitting's bare barrel takes the wall and the ring lying in it"),
        s(format!("a stack of the wall at its own station, floored on `enclosure.wall` and {} mm of boss", proud.fmt("g"))),
    )?;
    ns.set("_port_stack", port_stack.clone())?;
    for (name, f, ring, which, fluid) in Y_WALL_FITTINGS {
        let fit = kept.fit(f);
        ns.set("_n", s(name))?;
        ns.set("_fit", fit.clone())?;
        ns.set("_r", s(ring))?;
        ns.set("_w", s(which))?;
        ns.set("_f", s(fluid))?;
        let thread = interop::builtin("getattr").context("getattr")?.call(vec![fit.clone(), s("PANEL_THREAD"), Val::None], vec![])?;
        let bare = if thread.truthy()? { thread } else { fit.attr("THREAD_LEN")? };
        ns.set("_bare", bare.clone())?;
        let ports = key(&key(&call0(&kept.above, "specification")?, "rear_wall")?, "wet_ports")?;
        let mut found = None;
        for row in ports.iter()? {
            if interop::eq(&key(&row, "name")?, &s(name))? && found.is_none() {
                found = Some(row);
            }
        }
        let port = found.context("StopIteration")?;
        ns.set("_port", port.clone())?;
        let t = py::call(&kept.enc.attr("back_wall_t_at")?, vec![key(&port, "center_x_mm")?, key(&port, "center_z_mm")?])?;
        ns.set("_t", t.clone())?;
        let stack = port_clamp_stack(rt, Num::of(&t)?)?;
        ns.set("_stack", stack.val())?;
        let bare_n = Num::of(&bare)?;
        let ok = stack.f() <= bare_n.add(Num::F(1e-9)).f();
        let note = format!(
            "{name} offers {} mm of bare barrel and the joint it makes up through {} mm of wall stacks {} mm, leaving the nut none of it",
            fv(&bare, ".2f")?,
            gv(&t)?,
            stack.fmt("g")
        );
        _stated_bounds::take(&port_stack, &Val::Bool(ok), &s(note))?;
    }
    Ok(())
}

// ---------------------------------------------------------------------------------------------
// The west lane and the port columns (Python lines 1065-1120).

fn west_interior_face(rt: &Rt) -> Result<Val> {
    ix(&call0(&st(rt)?.enc, "interior_x")?, 0)
}
fn west_exterior_face(rt: &Rt) -> Result<Num> {
    let face = Num::of(&west_interior_face(rt)?)?;
    Ok(face.sub(anum(&st(rt)?.enc, "wall")?))
}
fn west_seam_crown(rt: &Rt) -> Result<Num> {
    let face = Num::of(&west_interior_face(rt)?)?;
    Ok(face.add(anum(&st(rt)?.enc, "side_band_inset")?))
}

const PORT_LANE_CLEAR: f64 = 1.0;
const PORT_FOOT_CLEAR: f64 = 1.0;
const FLAVOR_STOREY_DROP: f64 = 1.55;
const PANEL_ON_GATE_LANE: [&str; 2] = ["bulkhead-flavor-b", "bulkhead-flavor-a"];

fn panel_z(name: &Val, deck: Val, gate: Val) -> Result<Val> {
    for lane in PANEL_ON_GATE_LANE {
        if interop::eq(name, &s(lane))? {
            return Ok(gate);
        }
    }
    Ok(deck)
}

fn digiten_turn() -> Val {
    Val::Tuple(vec![
        Val::Tuple(vec![f3([0.0, 0.0, 1.0]), flt(90.0)]),
        Val::Tuple(vec![f3([0.0, 1.0, 0.0]), flt(90.0)]),
    ])
}
const CARB_2: f64 = 22.0;
const DIGITEN_CEILING_CLEAR: f64 = 1.0;
const DIGITEN_WEST_SET: f64 = 3.0;

/// `(axis_x, axis_z, seat_r, bands)` for the flow meter's anchors.
fn digiten_anchors(rt: &Rt, carry: &Val) -> Result<Val> {
    let st = st(rt)?;
    let axis = ix(&py::call(carry, vec![call0(&st.digiten, "inlet")?])?, 0)?;
    let mut bands = vec![];
    let mut radii: Vec<Num> = vec![];
    for sign in [-1i64, 1] {
        let profile = call1(&st.digiten, "mounting_profile", Val::Int(sign))?.get(Val::Int(-1))?;
        let r = py::unpack(&profile, 4)?;
        let mut ends: Vec<Num> = vec![];
        for x in [&r[0], &r[1]] {
            let along = Num::I(sign).mul(Num::of(x)?);
            let frame = Val::Tuple(vec![Val::Tuple(vec![along.val(), flt(0.0), flt(0.0)]), Val::Tuple(vec![Val::Int(sign), flt(0.0), flt(0.0)])]);
            ends.push(Num::of(&ix(&ix(&py::call(carry, vec![frame])?, 0)?, 1)?)?);
        }
        ends.sort_by(|a, b| num::order(a.f(), b.f()));
        bands.push(Num::vals(&ends));
        radii.push(Num::of(&r[2])?);
        radii.push(Num::of(&r[3])?);
    }
    let widest = radii.iter().skip(1).fold(radii[0], |m, r| m.max(*r));
    let seat = widest.add(*late!(st.late.digiten_seat_slip));
    Ok(Val::Tuple(vec![ix(&axis, 0)?, ix(&axis, 2)?, seat.val(), Val::Tuple(bands)]))
}

// ---------------------------------------------------------------------------------------------
// Tube anchors (Python lines 1157-1312).

const TUBE_ANCHOR_SPAN: f64 = 200.0;
const TUBE_ANCHOR_SITES: [(&str, usize, [f64; 3], &str); 3] = [
    ("carb-1", 1, [0.0, 0.0, 1.0], "enclosure-back-top"),
    ("co2-2", 1, [0.0, 0.0, 1.0], "enclosure-back-top"),
    ("fluid-28", 2, [-1.0, 0.0, 0.0], "enclosure-back-top"),
];
const TUBE_ANCHOR_END_FORMS: [(&str, [&str; 2]); 3] =
    [("carb-1", ["corbel", "corbel"]), ("co2-2", ["corbel", "corbel"]), ("fluid-28", ["corbel", "corbel"])];
const ANCHOR_END_FORMS: [&str; 2] = ["column", "corbel"];
const FLAVOR_B_ANCHOR_WELL_CLEAR: f64 = 1.0;
const TUBE_ANCHOR_CLOSURES: [(&str, &str); 3] = [("carb-1", "cap"), ("co2-2", "cap"), ("fluid-28", "tie")];
const ANCHOR_CLOSURES: [&str; 2] = ["tie", "cap"];

/// `math.dist(a, b)`.
fn dist(a: &[f64], b: &[f64]) -> Result<f64> {
    anyhow::ensure!(a.len() == b.len(), "distance dimensions");
    Ok(num::dist(a, b))
}
fn points(v: &Val) -> Result<Vec<Vec<f64>>> {
    py::snapshot(v)?.iter()?.iter().map(py::f64s).collect()
}
fn at3(p: &[f64]) -> Result<[f64; 3]> {
    anyhow::ensure!(p.len() >= 3, "index out of range");
    Ok([p[0], p[1], p[2]])
}

/// One run's route as the anchors read it.
struct RunData {
    run: Val,
    id: Val,
    pts: Vec<Vec<f64>>,
}
impl RunData {
    fn of(run: &Val) -> Result<RunData> {
        Ok(RunData { run: run.clone(), id: run.attr("id")?, pts: points(&run.attr("pts")?)? })
    }
    fn is(&self, id: &str) -> Result<bool> {
        interop::eq(&self.id, &s(id))
    }
    fn pt(&self, i: usize) -> Result<&Vec<f64>> {
        self.pts.get(i).context("IndexError: list index out of range")
    }
    /// `{i: radius_i * f(turn_i) for i, turn, _in, _out in run.bends}`.
    fn per_bend(&self, f: impl Fn(f64, f64) -> f64) -> Result<Vec<(Val, f64)>> {
        let radii = py::snapshot(&self.run.attr("radii")?)?;
        let mut out: Vec<(Val, f64)> = vec![];
        for bend in py::snapshot(&self.run.attr("bends")?)?.iter()? {
            let b = py::unpack(&bend, 4)?;
            let value = f(radii.get(b[0].clone())?.num()?, b[1].num()?);
            match out.iter_mut().find(|(k, _)| interop::eq(k, &b[0]).unwrap_or(false)) {
                Some(row) => row.1 = value,
                None => out.push((b[0].clone(), value)),
            }
        }
        Ok(out)
    }
    fn tangents(&self) -> Result<Vec<(Val, f64)>> {
        self.per_bend(|r, turn| r * (num::radians(turn) / 2.0).tan())
    }
}
fn lookup(map: &[(Val, f64)], i: usize) -> f64 {
    let key = Val::Int(i as i64);
    map.iter().find(|(k, _)| interop::eq(k, &key).unwrap_or(false)).map_or(0.0, |(_, v)| *v)
}
fn runs_by_id(runs: &Val) -> Result<Vec<(Val, Val)>> {
    let mut out: Vec<(Val, Val)> = vec![];
    for r in runs.iter()? {
        let id = r.attr("id")?;
        match out.iter_mut().find(|(k, _)| interop::eq(k, &id).unwrap_or(false)) {
            Some(row) => row.1 = r,
            None => out.push((id, r)),
        }
    }
    Ok(out)
}
fn find_run(by_id: &[(Val, Val)], id: &Val) -> Result<Option<Val>> {
    for (k, r) in by_id {
        if interop::eq(k, id)? {
            return Ok(Some(r.clone()));
        }
    }
    Ok(None)
}

/// `CLUSTER_WAGOS.values()` as `(side, y, z, size)`.
fn cluster_wagos(st: &State) -> Result<Vec<(i64, Num, Val, String)>> {
    let table = st.misc("CLUSTER_WAGOS")?;
    let mut out = vec![];
    for (_, row) in interop::entries_of(&table)? {
        let r = py::unpack(&row, 4)?;
        out.push((r[0].integer()?, Num::of(&r[1])?, r[2].clone(), r[3].str()?));
    }
    Ok(out)
}

fn tube_anchor_midpoint(rt: &Rt, run: &RunData, leg: usize) -> Result<[f64; 3]> {
    let st = st(rt)?;
    let (p, q) = (run.pt(leg)?, run.pt(leg + 1)?);
    let (p3, q3) = (at3(p)?, at3(q)?);
    let mid = [0, 1, 2].map(|k| (p3[k] + q3[k]) / 2.0);
    if run.is("carb-1")? {
        let tangents = run.tangents()?;
        let at = lookup(&tangents, leg) + an(&st.enc, "wall")? + an(&st.anchor_cap, "RIB_LEN")? / 2.0;
        let length = dist(p, q)?;
        return Ok([0, 1, 2].map(|k| p3[k] + (q3[k] - p3[k]) * at / length));
    }
    if !run.is("fluid-28")? {
        return Ok(mid);
    }
    if (p3[0] - q3[0]).abs() > 1e-6 || (p3[2] - q3[2]).abs() > 1e-6 || q3[1] <= p3[1] {
        return Err(err("ValueError", "fluid-28's wall anchor requires its aft-running straight Y leg"));
    }
    let wagos = cluster_wagos(&st)?;
    let mut wells: Vec<(Num, String)> = vec![];
    for (side, y, z, size) in wagos {
        if side < 0 && call1(&st.enc, "back_top_owns", Val::Tuple(vec![flt(0.0), y.val(), z]))?.truthy()? {
            wells.push((y, size));
        }
    }
    if wells.is_empty() {
        return Err(err("ValueError", "fluid-28's anchor has no rear Wago row to locate its working gap"));
    }
    let mut well_fore: Option<Num> = None;
    for (y, size) in &wells {
        let half = ixn(&call1(&st.enc, "wago_half", s(size.clone()))?, 0)?;
        let swing = Num::of(&call1(&st.enc, "wago_swing", s(size.clone()))?)?.div(Num::F(2.0));
        let fore = y.sub(half.max(swing));
        well_fore = Some(match well_fore {
            Some(m) => m.min(fore),
            None => fore,
        });
    }
    let len = an(&st.enc, "tube_anchor_len")?;
    let y = well_fore.context("min")?.f() - FLAVOR_B_ANCHOR_WELL_CLEAR - len / 2.0;
    let tangents = run.tangents()?;
    let straight_lo = p3[1] + lookup(&tangents, leg);
    let straight_hi = q3[1] - lookup(&tangents, leg + 1);
    let half = len / 2.0;
    if y - half < straight_lo - 1e-6 || y + half > straight_hi + 1e-6 {
        return Err(err(
            "ValueError",
            format!(
                "fluid-28 anchor Y{}..{} leaves its actual straight Y{}..{}",
                num::fmt(y - half, ".3f"),
                num::fmt(y + half, ".3f"),
                num::fmt(straight_lo, ".3f"),
                num::fmt(straight_hi, ".3f")
            ),
        ));
    }
    Ok([mid[0], y, mid[2]])
}

fn tube_anchor_sites(rt: &Rt, runs: &Val) -> Result<Val> {
    let st = st(rt)?;
    let by_id = runs_by_id(runs)?;
    let site_ids: Vec<&str> = TUBE_ANCHOR_SITES.iter().map(|r| r.0).collect();
    let end_ids: Vec<&str> = TUBE_ANCHOR_END_FORMS.iter().map(|r| r.0).collect();
    let closure_ids: Vec<&str> = TUBE_ANCHOR_CLOSURES.iter().map(|r| r.0).collect();
    for (table, what) in [(&end_ids, "end forms"), (&closure_ids, "closures")] {
        let mut missing: Vec<&str> = site_ids.iter().filter(|id| !table.contains(id)).copied().collect();
        if !missing.is_empty() {
            missing.sort();
            return Err(err("ValueError", format!("tube_anchors: no {what} stated for {}", sv(&py::list(missing.iter().map(|m| s(*m))))?)));
        }
        let mut unknown: Vec<&str> = table.iter().filter(|id| !site_ids.contains(id)).copied().collect();
        if !unknown.is_empty() {
            unknown.sort();
            return Err(err("ValueError", format!("tube_anchors: {what} name no anchor site: {}", sv(&py::list(unknown.iter().map(|m| s(*m))))?)));
        }
    }
    let slip = *late!(st.late.tube_anchor_slip);
    let mut stations = vec![];
    for (rid, leg, root, _piece) in TUBE_ANCHOR_SITES {
        let end_forms = TUBE_ANCHOR_END_FORMS.iter().find(|r| r.0 == rid).map(|r| r.1).context("KeyError")?;
        if end_forms.iter().any(|f| !ANCHOR_END_FORMS.contains(f)) {
            return Err(err(
                "ValueError",
                format!(
                    "tube_anchors: {rid} end forms are {}; each of the two route ends must be one of {}.",
                    strs(&end_forms).repr()?,
                    sv(&strs(&ANCHOR_END_FORMS))?
                ),
            ));
        }
        let closure = TUBE_ANCHOR_CLOSURES.iter().find(|r| r.0 == rid).map(|r| r.1).context("KeyError")?;
        if !ANCHOR_CLOSURES.contains(&closure) {
            return Err(err(
                "ValueError",
                format!("tube_anchors: {rid} is closed by {}; a closure is one of {}.", s(closure).repr()?, sv(&strs(&ANCHOR_CLOSURES))?),
            ));
        }
        let Some(run) = find_run(&by_id, &s(rid))? else { continue };
        let r = RunData::of(&run)?;
        if leg + 1 >= r.pts.len() {
            return Err(err(
                "ValueError",
                format!(
                    "tube_anchors: {rid} has {} legs and this row names leg {leg}. `TUBE_ANCHOR_SITES` names a leg of the route as `_lines` draws it.",
                    r.pts.len() as i64 - 1
                ),
            ));
        }
        let (p, q) = (r.pt(leg)?, r.pt(leg + 1)?);
        let length = dist(p, q)?;
        let (p3, q3) = (at3(p)?, at3(q)?);
        let u = [0, 1, 2].map(|k| (q3[k] - p3[k]) / length);
        if num::sum((0..3).map(|k| u[k] * root[k])).abs() > 1e-9 {
            return Err(err(
                "ValueError",
                format!(
                    "tube_anchors: {rid} leg {leg} runs along {} and this row roots it on {}. An anchor stands ACROSS its tube, never off the face the tube points at.",
                    sv(&f3(u))?,
                    sv(&f3(root))?
                ),
            ));
        }
        let anchor_len = an(&st.enc, "tube_anchor_len")?;
        if length < anchor_len {
            return Err(err(
                "ValueError",
                format!(
                    "tube_anchors: {rid} leg {leg} is {} mm and a rib is {}. A seat longer than the straight it stands on would close on the corners either side of it.",
                    num::fmt(length, ".2f"),
                    num::fmt(anchor_len, ".2f")
                ),
            ));
        }
        let mid = tube_anchor_midpoint(rt, &r, leg)?;
        let seat = anum(&run, "diam")?.div(Num::F(2.0)).add(slip);
        let mut station = vec![f3(mid), f3(u), f3(root), seat.val(), strs(&end_forms)];
        if closure == "cap" {
            let tangents = r.tangents()?;
            let at = dist(p, &mid)?;
            let (lo, hi) = (lookup(&tangents, leg), length - lookup(&tangents, leg + 1));
            let half = an(&st.anchor_cap, "RIB_LEN")? / 2.0;
            if at - half < lo - 1e-6 || at + half > hi + 1e-6 {
                return Err(err(
                    "ValueError",
                    format!(
                        "tube_anchors: {rid}'s capped rib runs {}..{} mm along leg {leg}, whose straight is {}..{}. A rib off the straight closes on the bend either side of it.",
                        num::fmt(at - half, ".2f"),
                        num::fmt(at + half, ".2f"),
                        num::fmt(lo, ".2f"),
                        num::fmt(hi, ".2f")
                    ),
                ));
            }
            station.push(s("cap"));
        }
        stations.push(Val::Tuple(vec![s(rid), Val::Tuple(station)]));
    }
    Ok(Val::Tuple(stations))
}

// ---------------------------------------------------------------------------------------------
// Body anchors and the cap's anchors (Python lines 1314-1445).

#[derive(Clone, Copy)]
enum Section {
    Barrel,
    CheckSocket,
    SplitSeat,
}
const BODY_ANCHOR_SITES: [(&str, Section, [f64; 3], &str); 3] = [
    ("wr1110", Section::Barrel, [0.0, 0.0, 1.0], "enclosure-back-top"),
    ("gasher-co2", Section::CheckSocket, [0.0, 0.0, 1.0], "enclosure-back-top"),
    ("water-split", Section::SplitSeat, [-1.0, 0.0, 0.0], "enclosure-back-top"),
];
const BODY_ANCHOR_END_FORMS: [(&str, [&str; 2]); 3] =
    [("wr1110", ["corbel", "corbel"]), ("gasher-co2", ["corbel", "corbel"]), ("water-split", ["corbel", "corbel"])];

fn split_seat(rt: &Rt) -> Result<Val> {
    let st = st(rt)?;
    py::call(&st.split.attr("clearance_seat")?, vec![st.enc.attr("tube_anchor_len")?, st.enc.attr("tie_w")?])
}

fn body_anchors(rt: &Rt, carries: &Val) -> Result<Val> {
    let st = st(rt)?;
    let slip = *late!(st.late.body_anchor_slip);
    let mut stations = vec![];
    for (name, section, root, _piece) in BODY_ANCHOR_SITES {
        let carry = call1(carries, "get", s(name))?;
        if matches!(carry, Val::None) {
            continue;
        }
        let read = match section {
            Section::Barrel => call0(&st.wr1110, "barrel")?,
            Section::CheckSocket => _gas_chain::check_socket(rt)?,
            Section::SplitSeat => split_seat(rt)?,
        };
        let srl = py::unpack(&read, 3)?;
        let (station, r, length) = (&srl[0], &srl[1], &srl[2]);
        let mu = py::unpack(&py::call(&carry, vec![station.clone()])?, 2)?;
        let (mid, u) = (&mu[0], &mu[1]);
        let uf = py::f64s(u)?;
        anyhow::ensure!(uf.len() >= 3, "index out of range");
        if num::sum((0..3).map(|k| uf[k] * root[k])).abs() > 1e-9 {
            return Err(err(
                "ValueError",
                format!(
                    "body_anchors: {name}'s section runs along {} and this row roots it on {}. An anchor stands ACROSS the body, never off the face the body points at.",
                    sv(u)?,
                    sv(&f3(root))?
                ),
            ));
        }
        let anchor_len = an(&st.enc, "tube_anchor_len")?;
        if length.num()? < anchor_len {
            return Err(err(
                "ValueError",
                format!(
                    "body_anchors: {name}'s section is {} mm and a rib is {}. A seat longer than the section it bears on closes on whatever is either side of it.",
                    fv(length, ".2f")?,
                    num::fmt(anchor_len, ".2f")
                ),
            ));
        }
        let forms = BODY_ANCHOR_END_FORMS.iter().find(|r| r.0 == name).map(|r| r.1).context("KeyError")?;
        stations.push(Val::Tuple(vec![tuple_of(mid)?, tuple_of(u)?, f3(root), Num::of(r)?.add(slip).val(), strs(&forms)]));
    }
    Ok(Val::Tuple(stations))
}

/// `_on_leg`: whether `pt` lies on the segment `p..q`.
fn on_leg(pt: &[f64], p: &[f64], q: &[f64], tol: f64) -> Result<bool> {
    let d = dist(p, q)?;
    if d < tol {
        return Ok(false);
    }
    Ok((dist(p, pt)? + dist(pt, q)? - d).abs() < tol)
}

fn leg_dir(p: &[f64], q: &[f64]) -> Result<Val> {
    let d = dist(p, q)?;
    let (p3, q3) = (at3(p)?, at3(q)?);
    Ok(f3([0, 1, 2].map(|k| (q3[k] - p3[k]) / d)))
}

fn cap_tube_anchors(rt: &Rt, foam_carry: &Val, runs: &Val) -> Result<Val> {
    let st = st(rt)?;
    let by_id = runs_by_id(runs)?;
    let mut out = vec![];
    let anchors = st.cci.attr("cap_anchors")?;
    for name in anchors.iter()? {
        let Some(run) = find_run(&by_id, &name)? else { continue };
        let mid = ix(&py::call(foam_carry, vec![cap_anchor(rt, &name)?])?, 0)?;
        let m = py::f64s(&mid)?;
        let pts = points(&run.attr("pts")?)?;
        let mut held = false;
        for i in 0..pts.len().saturating_sub(1) {
            let (p, q) = (&pts[i], &pts[i + 1]);
            if !on_leg(&m, p, q, 1e-3)? {
                continue;
            }
            out.push(Val::Tuple(vec![mid.clone(), leg_dir(p, q)?, f3([0.0, 0.0, -1.0]), anchors.get(name.clone())?.attr("seat_r")?]));
            held = true;
            break;
        }
        if !held {
            return Err(err(
                "ValueError",
                format!(
                    "cap_tube_anchors: the rib for {} stands at {} and no leg of that run passes through it. `_cold_core_interface.cap_anchors[{}].centre` is in the cap's own frame, and the run is where its two ports put it.",
                    sv(&name)?,
                    sv(&mid)?,
                    name.repr()?
                ),
            ));
        }
    }
    let side = st.cci.attr("cap_side_anchors")?;
    for name in side.iter()? {
        let Some(run) = find_run(&by_id, &name)? else { continue };
        let mr = py::unpack(&py::call(foam_carry, vec![cap_side_anchor(rt, &name)?])?, 2)?;
        let (mid, root) = (&mr[0], &mr[1]);
        let m = py::f64s(mid)?;
        let pts = points(&run.attr("pts")?)?;
        let mut held = false;
        for i in 0..pts.len().saturating_sub(1) {
            let (p, q) = (&pts[i], &pts[i + 1]);
            if !on_leg(&m, p, q, 1e-3)? {
                continue;
            }
            out.push(Val::Tuple(vec![mid.clone(), leg_dir(p, q)?, tuple_of(root)?, side.get(name.clone())?.attr("seat_r")?]));
            held = true;
            break;
        }
        if !held {
            return Err(err(
                "ValueError",
                format!(
                    "cap_tube_anchors: the side post for {} stands its pipe at {} and no leg of that run passes through it. `_cold_core_interface.cap_side_anchors[{}]` is in the cap's own frame, and the run is where its two ports put it.",
                    sv(&name)?,
                    sv(mid)?,
                    name.repr()?
                ),
            ));
        }
    }
    Ok(Val::Tuple(out))
}

fn lid_cap_stations(rt: &Rt, foam_carry: &Val, runs: &Val) -> Result<Val> {
    let st = st(rt)?;
    let by_id = runs_by_id(runs)?;
    let mut out = vec![];
    for item in call0(&st.cci.attr("cap_anchors")?, "items")?.iter()? {
        let nr = py::unpack(&item, 2)?;
        let (name, row) = (&nr[0], &nr[1]);
        let run = find_run(&by_id, name)?;
        if !interop::eq(&row.attr("closure")?, &s("cap"))? {
            continue;
        }
        let Some(run) = run else { continue };
        let mid = ix(&py::call(foam_carry, vec![cap_anchor(rt, name)?])?, 0)?;
        let m = py::f64s(&mid)?;
        let pts = points(&run.attr("pts")?)?;
        let mut held = false;
        for pair in pts.windows(2) {
            if on_leg(&m, &pair[0], &pair[1], 1e-3)? {
                out.push(Val::Tuple(vec![name.clone(), mid.clone(), leg_dir(&pair[0], &pair[1])?]));
                held = true;
                break;
            }
        }
        if !held {
            return Err(err(
                "ValueError",
                format!(
                    "lid_cap_stations: the capped rib for {} stands at {} and no leg of that run passes through it.",
                    sv(name)?,
                    sv(&mid)?
                ),
            ));
        }
    }
    Ok(Val::Tuple(out))
}

// ---------------------------------------------------------------------------------------------
// Reservoir A's paired seats and the unsupported spans (Python lines 1447-1543).

fn reservoir_a_anchor_sites(rt: &Rt, runs: &Val) -> Result<Val> {
    let anchors = rt.import("_reservoir_a_anchors")?;
    let by_id = runs_by_id(runs)?;
    let spec = call0(&anchors, "specification")?;
    let datums = py::snapshot(&call0(&anchors, "datums")?)?;
    let mut out = vec![];
    for row in call0(&datums, "values")?.iter()? {
        let ids = key(&row, "routes_west_to_east")?.iter()?;
        let centres = key(&row, "tube_centers_world_mm")?.iter()?;
        let axes = key(&row, "tube_axes_world")?.iter()?;
        for ((identifier, point), axis) in ids.iter().zip(centres.iter()).zip(axes.iter()) {
            if find_run(&by_id, identifier)?.is_none() {
                continue;
            }
            let seat = py::call(&row.attr("get")?, vec![s("seat_radius_mm"), key(&spec, "seat_radius_mm")?])?;
            out.push(Val::Tuple(vec![identifier.clone(), Val::Tuple(vec![tuple_of(point)?, tuple_of(axis)?, f3([0.0, 0.0, -1.0]), seat])]));
        }
    }
    Ok(Val::Tuple(out))
}

fn dot(a: &[f64], b: &[f64]) -> f64 {
    num::sum(a.iter().zip(b).map(|(a, b)| a * b))
}

/// Exact native line/arc lengths at reservoir A's seats, for the current route only.
fn reservoir_a_developed_stations(rt: &Rt, run: &RunData, pts: &[Vec<f64>]) -> Result<Option<Vec<f64>>> {
    if !(run.is("fluid-14")? || run.is("fluid-16")?) {
        return Ok(None);
    }
    let routes = rt.import("above_core_routes")?;
    let spec = py::snapshot(&call0(&routes, "reservoir_a_route_specs")?.get(run.id.clone())?)?;
    let authored = points(&key(&spec, "points_mm")?)?;
    if run.pts.len() != authored.len() {
        return Ok(None);
    }
    for (a, b) in run.pts.iter().zip(&authored) {
        if dist(a, b)? > 1e-6 {
            return Ok(None);
        }
    }
    let mut cuts = vec![0.0];
    let mut distance = 0.0;
    for segment in key(&spec, "segments")?.iter()? {
        if interop::eq(&key(&segment, "kind")?, &s("line"))? {
            let pq = points(&key(&segment, "points_mm")?)?;
            anyhow::ensure!(pq.len() == 2, "unpack: expected 2, got {}", pq.len());
            let (p, q) = (&pq[0], &pq[1]);
            for point in pts {
                if on_leg(point, p, q, 1e-6)? {
                    cuts.push(distance + dist(p, point)?);
                }
            }
            distance += dist(p, q)?;
        } else {
            let center = py::f64s(&key(&segment, "center_mm")?)?;
            let axis = py::f64s(&key(&segment, "axis")?)?;
            let radius = keyf(&segment, "radius_mm")?;
            let angle = keyf(&segment, "angle_rad")?;
            let first = py::f64s(&ix(&key(&segment, "points_mm")?, 0)?)?;
            let start: Vec<f64> = first.iter().zip(&center).map(|(p, c)| p - c).collect();
            for point in pts {
                let radial: Vec<f64> = point.iter().zip(&center).map(|(p, c)| p - c).collect();
                if (dist(point, &center)? - radius).abs() > 1e-6 || dot(&radial, &axis).abs() > 1e-6 {
                    continue;
                }
                let (s3, r3) = (at3(&start)?, at3(&radial)?);
                let cross = [
                    s3[1] * r3[2] - s3[2] * r3[1],
                    s3[2] * r3[0] - s3[0] * r3[2],
                    s3[0] * r3[1] - s3[1] * r3[0],
                ];
                let mut turn = (1f64.copysign(angle) * dot(&axis, &cross)).atan2(dot(&start, &radial));
                if turn < -1e-6 / radius {
                    turn += 2.0 * std::f64::consts::PI;
                }
                if turn <= angle.abs() + 1e-6 / radius {
                    cuts.push(distance + radius * if turn > 0.0 { turn } else { 0.0 });
                }
            }
            distance += radius * angle.abs();
        }
    }
    cuts.push(distance);
    let mut unique: Vec<f64> = vec![];
    for c in cuts {
        if !unique.contains(&c) {
            unique.push(c);
        }
    }
    unique.sort_by(|a, b| num::order(*a, *b));
    Ok(Some(unique))
}

/// `max(b - a for a, b in zip(cuts, cuts[1:]))`.
fn widest_gap(cuts: &[f64]) -> Result<f64> {
    let mut best: Option<f64> = None;
    for pair in cuts.windows(2) {
        let gap = pair[1] - pair[0];
        best = Some(match best {
            Some(b) if !(gap > b) => b,
            _ => gap,
        });
    }
    best.context("ValueError: max() arg is an empty sequence")
}

fn unsupported_spans(rt: &Rt, runs: &Val, stations: &Val) -> Result<Val> {
    let rows = py::snapshot(stations)?.iter()?;
    let mut mids: Vec<Vec<f64>> = vec![];
    for row in &rows {
        let head = row.iter()?;
        anyhow::ensure!(head.len() >= 4, "unpack: expected 4, got {}", head.len());
        mids.push(py::f64s(&head[0])?);
    }
    let out = Val::dict(vec![]);
    for r in runs.iter()? {
        let run = RunData::of(&r)?;
        let firsts: Vec<Vec<f64>> = rows.iter().map(|row| py::f64s(&ix(row, 0)?)).collect::<Result<_>>()?;
        if let Some(native) = reservoir_a_developed_stations(rt, &run, &firsts)? {
            out.set(run.id.clone(), flt(widest_gap(&native)?))?;
            continue;
        }
        let short = run.per_bend(|r, turn| 2.0 * r * (num::radians(turn) / 2.0).tan() - r * num::radians(turn))?;
        let mut cuts = vec![0.0];
        let mut s_ = 0.0;
        for i in 0..run.pts.len().saturating_sub(1) {
            s_ -= lookup(&short, i);
            for mid in &mids {
                if on_leg(mid, &run.pts[i], &run.pts[i + 1], 1e-6)? {
                    cuts.push(s_ + dist(&run.pts[i], mid)?);
                }
            }
            s_ += dist(&run.pts[i], &run.pts[i + 1])?;
        }
        cuts.push(s_);
        cuts.sort_by(|a, b| num::order(*a, *b));
        out.set(run.id.clone(), flt(widest_gap(&cuts)?))?;
    }
    Ok(out)
}

const ASSE_TIE_T: f64 = 1.0;
const ASSE_TIE_CLEAR: f64 = 0.5;

fn interior_ceiling(rt: &Rt) -> Result<Num> {
    let st = st(rt)?;
    Ok(anum(&st.enc, "appliance_height")?.sub(anum(&st.enc, "floor_t")?).sub(anum(&st.enc, "ceiling_skin")?))
}

// ---------------------------------------------------------------------------------------------
// Install, Python lines 1065-1559.

fn install_3(rt: &Rt, ns: &Ns) -> Result<()> {
    let kept = st(rt)?;
    ns.def(rt, "west_interior_face", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        west_interior_face(rt)
    })?;
    ns.def(rt, "west_exterior_face", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(west_exterior_face(rt)?.val())
    })?;
    ns.def(rt, "west_seam_crown", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(west_seam_crown(rt)?.val())
    })?;
    ns.set("PORT_LANE_CLEAR", flt(PORT_LANE_CLEAR))?;
    let column = west_seam_crown(rt)?.add(Num::F(PORT_LANE_CLEAR)).add(anum(&kept.jg, "BODY_D")?.div(Num::F(2.0)));
    ns.set("PORT_WEST_COLUMN", column.val())?;
    let _ = kept.late.port_west_column.set(column);
    let pitch = *late!(kept.late.port_pitch);
    let panel_x = sdict(vec![
        ("bulkhead-flavor-b", column.val()),
        ("bulkhead-flavor-a", column.add(pitch).val()),
        ("bulkhead-carb", column.add(pitch).val()),
    ]);
    ns.set("PANEL_X", panel_x.clone())?;
    let _ = kept.late.panel_x.set(panel_x);
    ns.set("PORT_FOOT_CLEAR", flt(PORT_FOOT_CLEAR))?;
    ns.set("FLAVOR_STOREY_DROP", flt(FLAVOR_STOREY_DROP))?;
    ns.def(rt, "flavor_storey", |_, args, kw| {
        let mut a = py::bind(args, kw, &["gate", "pump_carry"], &[])?;
        let gate = Num::of(&a.req("gate")?)?;
        a.req("pump_carry")?;
        Ok(gate.sub(Num::F(FLAVOR_STOREY_DROP)).val())
    })?;
    ns.set("PANEL_ON_GATE_LANE", strs(&PANEL_ON_GATE_LANE))?;
    ns.def(rt, "panel_z", |_, args, kw| {
        let mut a = py::bind(args, kw, &["name", "deck", "gate"], &[])?;
        let (name, deck, gate) = (a.req("name")?, a.req("deck")?, a.req("gate")?);
        panel_z(&name, deck, gate)
    })?;
    let hw = py::path(&ns.get("_hw")?)?;
    let digiten_step = hw.join("reference").join("digiten-flow-sensor").join("digiten-flow-sensor.step");
    ns.set("DIGITEN_STEP", Val::Path(digiten_step.clone()))?;
    let _ = kept.late.digiten_step.set(digiten_step);
    ns.set("DIGITEN_TURN", digiten_turn())?;
    ns.set("CARB_2", flt(CARB_2))?;
    ns.set("DIGITEN_CEILING_CLEAR", flt(DIGITEN_CEILING_CLEAR))?;
    ns.set("DIGITEN_WEST_SET", flt(DIGITEN_WEST_SET))?;
    let slip = kept.fits.attr("slip")?;
    ns.set("DIGITEN_SEAT_SLIP", slip.clone())?;
    let _ = kept.late.digiten_seat_slip.set(Num::of(&slip)?);
    ns.def(rt, "digiten_anchors", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["carry"], &[])?;
        digiten_anchors(rt, &a.req("carry")?)
    })?;
    ns.set("TUBE_ANCHOR_SPAN", flt(TUBE_ANCHOR_SPAN))?;
    let slip = kept.fits.attr("slip")?;
    ns.set("TUBE_ANCHOR_SLIP", slip.clone())?;
    let _ = kept.late.tube_anchor_slip.set(Num::of(&slip)?);
    ns.set(
        "TUBE_ANCHOR_SITES",
        Val::Tuple(TUBE_ANCHOR_SITES.iter().map(|(id, leg, root, piece)| Val::Tuple(vec![s(*id), Val::Int(*leg as i64), f3(*root), s(*piece)])).collect()),
    )?;
    ns.set("TUBE_ANCHOR_END_FORMS", sdict(TUBE_ANCHOR_END_FORMS.iter().map(|(id, f)| (*id, strs(f))).collect()))?;
    ns.set("ANCHOR_END_FORMS", strs(&ANCHOR_END_FORMS))?;
    ns.set("FLAVOR_B_ANCHOR_WELL_CLEAR", flt(FLAVOR_B_ANCHOR_WELL_CLEAR))?;
    ns.set("TUBE_ANCHOR_CLOSURES", sdict(TUBE_ANCHOR_CLOSURES.iter().map(|(id, c)| (*id, s(*c))).collect()))?;
    ns.set("ANCHOR_CLOSURES", strs(&ANCHOR_CLOSURES))?;
    ns.def(rt, "tube_anchor_midpoint", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["run", "leg"], &[])?;
        let (run, leg) = (RunData::of(&a.req("run")?)?, a.req("leg")?.integer()?);
        anyhow::ensure!(leg >= 0, "negative leg");
        Ok(f3(tube_anchor_midpoint(rt, &run, leg as usize)?))
    })?;
    ns.def(rt, "tube_anchor_sites", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["runs"], &[])?;
        tube_anchor_sites(rt, &a.req("runs")?)
    })?;
    let slip = kept.fits.attr("slip")?;
    ns.set("BODY_ANCHOR_SLIP", slip.clone())?;
    let _ = kept.late.body_anchor_slip.set(Num::of(&slip)?);
    let runtime = rt.clone();
    let split = Val::function(move |args, kw| {
        let _frame = runtime.frame(MODULE);
        py::bind(args, kw, &[], &[])?;
        split_seat(&runtime)
    });
    let sections = [kept.wr1110.attr("barrel")?, kept.ns.get("_gas_chain")?.attr("check_socket")?, split];
    ns.set(
        "BODY_ANCHOR_SITES",
        Val::Tuple(
            BODY_ANCHOR_SITES
                .iter()
                .zip(sections)
                .map(|((name, _, root, piece), section)| Val::Tuple(vec![s(*name), section, f3(*root), s(*piece)]))
                .collect(),
        ),
    )?;
    ns.set("BODY_ANCHOR_END_FORMS", sdict(BODY_ANCHOR_END_FORMS.iter().map(|(id, f)| (*id, strs(f))).collect()))?;
    ns.def(rt, "body_anchors", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["carries"], &[])?;
        body_anchors(rt, &a.req("carries")?)
    })?;
    ns.def(rt, "cap_tube_anchors", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["foam_carry", "runs"], &[])?;
        cap_tube_anchors(rt, &a.req("foam_carry")?, &a.req("runs")?)
    })?;
    ns.def(rt, "lid_cap_stations", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["foam_carry", "runs"], &[])?;
        lid_cap_stations(rt, &a.req("foam_carry")?, &a.req("runs")?)
    })?;
    ns.def(rt, "reservoir_a_anchor_sites", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["runs"], &[])?;
        reservoir_a_anchor_sites(rt, &a.req("runs")?)
    })?;
    ns.def(rt, "reservoir_a_developed_stations", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["run", "points"], &[])?;
        let (run, pts) = (a.req("run")?, a.req("points")?);
        let run = RunData::of(&run)?;
        if !(run.is("fluid-14")? || run.is("fluid-16")?) {
            return Ok(Val::None);
        }
        let pts = points(&pts)?;
        Ok(match reservoir_a_developed_stations(rt, &run, &pts)? {
            Some(cuts) => py::ftuple(&cuts),
            None => Val::None,
        })
    })?;
    ns.def(rt, "unsupported_spans", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["runs", "stations"], &[])?;
        unsupported_spans(rt, &a.req("runs")?, &a.req("stations")?)
    })?;
    ns.def(rt, "_on_leg", |_, args, kw| {
        let mut a = py::bind(args, kw, &["pt", "p", "q", "tol"], &[])?;
        let (pt, p, q) = (py::f64s(&a.req("pt")?)?, py::f64s(&a.req("p")?)?, py::f64s(&a.req("q")?)?);
        let tol = a.f64_or("tol", 1e-6)?;
        Ok(Val::Bool(on_leg(&pt, &p, &q, tol)?))
    })?;
    ns.set("ASSE_TIE_T", flt(ASSE_TIE_T))?;
    ns.set("ASSE_TIE_CLEAR", flt(ASSE_TIE_CLEAR))?;
    ns.def(rt, "interior_ceiling", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(interior_ceiling(rt)?.val())
    })?;
    Ok(())
}

// ---------------------------------------------------------------------------------------------
// The C14 inlet, the keystone and the CO2 inlet on the +Y wall (Python lines 1561-1642).

fn c14_cutout(rt: &Rt) -> Result<Val> {
    let st = st(rt)?;
    let station = late!(st.late.c14_station);
    Ok(Val::Tuple(vec![
        s("rect"),
        ix(station, 0)?,
        ix(station, 1)?,
        st.enc.attr("c14_bore_w")?,
        st.enc.attr("c14_bore_h")?,
        st.enc.attr("c14_bore_r")?,
    ]))
}

fn c14_mount_half(rt: &Rt) -> Result<Val> {
    let cut = py::unpack(&c14_cutout(rt)?, 6)?;
    let st = st(rt)?;
    let half = anum(&st.enc, "c14_screw_pitch")?.div(Num::F(2.0));
    py::method(&st.enc, "c14_mount_half", vec![cut[3].clone(), cut[4].clone(), half.val()])
}

fn c14_seat_y(rt: &Rt) -> Result<Num> {
    let st = st(rt)?;
    let xz = py::unpack(late!(st.late.c14_station), 2)?;
    let outer = anum(&st.enc, "rear_plane_y")?.add(anum(&st.enc, "wall")?);
    let wall = Num::of(&py::method(&st.enc, "back_wall_t_at", vec![xz[0].clone(), xz[1].clone()])?)?;
    Ok(outer.sub(wall).sub(anum(&st.enc, "c14_tunnel_len")?))
}

fn c14_stations(rt: &Rt) -> Result<Val> {
    let st = st(rt)?;
    let station = late!(st.late.c14_station);
    let pitch = anum(&st.enc, "c14_screw_pitch")?;
    let mut out = vec![];
    for dx in [pitch.neg().div(Num::F(2.0)), pitch.div(Num::F(2.0))] {
        out.push(Val::Tuple(vec![ixn(station, 0)?.add(dx).val(), ix(station, 1)?]));
    }
    Ok(Val::Tuple(out))
}

fn co2_chain_turn() -> Val {
    Val::Tuple(vec![Val::Tuple(vec![f3([0.0, 0.0, 1.0]), flt(180.0)])])
}

fn keystone_cutout(rt: &Rt, station: &Val) -> Result<Val> {
    let st = st(rt)?;
    let slip = anum(&st.fits, "slip")?;
    let wx = anum(&st.keystone, "FACE_W")?.add(Num::F(2.0).mul(slip));
    let wz = anum(&st.keystone, "FACE_H")?.add(Num::F(2.0).mul(anum(&st.fits, "slip")?));
    let r = ix(&call0(&st.keystone, "panel_cutout")?, 2)?;
    let xz = py::unpack(station, 2)?;
    Ok(Val::Tuple(vec![s("rect"), xz[0].clone(), xz[1].clone(), wx.val(), wz.val(), r]))
}

const CO2_REGULATOR_SETBACK: f64 = 58.0;
const CO2_CHECK_SIDE_OFFSET: f64 = 36.0;
const CO2_CHECK_FORWARD_OFFSET: f64 = 20.0;

fn co2_inlet_mouth_y(rt: &Rt) -> Result<Num> {
    let seat = bulkhead_seat_y(rt)?;
    Ok(seat.add(anum(&st(rt)?.neofit, "far_ring_face_y")?))
}

fn co2_wall_port(rt: &Rt, inlet_carry: &Val) -> Result<Val> {
    let st = st(rt)?;
    let pos = ix(&py::call(inlet_carry, vec![call1(&st.neofit, "port", flt(-1.0))?])?, 0)?;
    let hole = call1(&st.neofit, "panel_hole_d", late!(st.late.port_hole_slip).val())?;
    Ok(Val::Tuple(vec![s("round"), ix(&pos, 0)?, ix(&pos, 2)?, hole]))
}

/// `STANDALONE`: every body the pack does not carry.
fn standalone(st: &State, ns: &Ns) -> Result<Val> {
    let mut out: Vec<Val> = ["compressor", "condenser+fan", "foam-assembly", "g-ganen-pump"].map(s).to_vec();
    for row in call0(&ns.get("PUMP_ELBOWS")?, "values")?.iter()? {
        let name = py::unpack(&row, 2)?[0].clone();
        for part in ["", "-clamp-barb", "-clamp-tube"] {
            out.push(s(format!("{}{part}", sv(&name)?)));
        }
    }
    for name in [
        "funnel",
        "discharge-chain",
        "display",
        "display-cover",
        "display-gasket",
        "psu",
        "pcba",
        "relay-1",
        "relay-2",
        "asse1022-assembly",
        "bulkhead-drain",
    ] {
        out.push(s(name));
    }
    out.extend(st.drain.attr("ADAPTER_NAMES")?.iter()?);
    out.extend(["mq6-sensor", "thermal-fuse", "fuse-clamp"].map(s));
    out.extend(ns.get("WAGO_POLES")?.iter()?);
    out.extend(ns.get("CLUSTER_WAGOS")?.iter()?);
    out.extend(
        ["water-split", "flow-regulator", "vk-solenoid", "bulkhead-water", "c14-inlet", "co2-inlet", "gasher-co2", "wr1110"].map(s),
    );
    out.extend(ns.get("_gas_chain")?.attr("ADAPTER_NAMES")?.iter()?);
    out.extend(
        ["nameplate", "nameplate-ink", "bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-carb", "digiten-flow"].map(s),
    );
    for (rid, closure) in TUBE_ANCHOR_CLOSURES {
        if closure == "cap" {
            out.push(s(format!("anchor-cap-{rid}")));
        }
    }
    for item in call0(&st.cci.attr("cap_anchors")?, "items")?.iter()? {
        let nr = py::unpack(&item, 2)?;
        if interop::eq(&nr[1].attr("closure")?, &s("cap"))? {
            out.push(s(format!("anchor-cap-{}", sv(&nr[0])?)));
        }
    }
    Ok(Val::Tuple(out))
}

fn manifold_body(st: &State, name: &Val) -> Result<bool> {
    if st.misc("STANDALONE")?.contains(name)? {
        return Ok(false);
    }
    let enclosure = match name {
        Val::Str(text) => text.starts_with("enclosure-"),
        _ => py::method(name, "startswith", vec![s("enclosure-")])?.truthy()?,
    };
    if enclosure {
        return Ok(false);
    }
    Ok(!st.misc("_ROUTED")?.contains(name)?)
}

fn east_wall_seat(rt: &Rt) -> Result<Num> {
    let st = st(rt)?;
    let east = ixn(&call0(&st.enc, "interior_x")?, 1)?;
    Ok(east.sub(anum(&st.enc, "mount_boss_out")?))
}

const FLOOR_BOSS_SLIP: f64 = 1.0;
const FLOOR_GROMMET_SQUEEZE: f64 = 0.4;

fn floor_mounts(mounted: &[Val]) -> Result<Val> {
    let mut out = vec![];
    for body in mounted {
        let row = py::unpack(body, 4)?;
        let (carry, holes, face_z, bore_d) = (&row[0], &row[1], &row[2], &row[3]);
        for hole in holes.iter()? {
            let h = py::unpack(&hole, 2)?;
            let station = Val::Tuple(vec![Val::Tuple(vec![h[0].clone(), h[1].clone(), face_z.clone()]), f3([0.0, 0.0, 1.0])]);
            let placed = py::unpack(&py::call(carry, vec![station])?, 2)?;
            let pos = &placed[0];
            out.push(Val::Tuple(vec![
                ix(pos, 0)?,
                ix(pos, 1)?,
                ixn(pos, 2)?.sub(Num::F(FLOOR_GROMMET_SQUEEZE)).val(),
                Num::of(bore_d)?.sub(Num::F(2.0).mul(Num::F(FLOOR_BOSS_SLIP))).val(),
            ]));
        }
    }
    Ok(Val::Tuple(out))
}

// ---------------------------------------------------------------------------------------------
// Install, Python lines 1561-1717.

fn install_4(rt: &Rt, ns: &Ns) -> Result<()> {
    let kept = st(rt)?;
    let hw = py::path(&ns.get("_hw")?)?;
    let c14_step = hw.join("reference").join("iec-c14-inlet").join("iec-c14-inlet.step");
    ns.set("C14_STEP", Val::Path(c14_step.clone()))?;
    let _ = kept.late.c14_step.set(c14_step);
    ns.def(rt, "c14_mount_half", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        c14_mount_half(rt)
    })?;
    let x = ix(&key(&call1(&kept.above, "pose", s("c14-inlet"))?, "translation_mm")?, 0)?;
    let z = ix(&key(&call1(&kept.above, "pose", s("c14-inlet"))?, "translation_mm")?, 2)?;
    let station = Val::Tuple(vec![x, z]);
    ns.set("C14_STATION", station.clone())?;
    let _ = kept.late.c14_station.set(station);
    ns.def(rt, "c14_seat_y", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(c14_seat_y(rt)?.val())
    })?;
    ns.def(rt, "c14_stations", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        c14_stations(rt)
    })?;
    ns.def(rt, "c14_cutout", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        c14_cutout(rt)
    })?;
    ns.set("CO2_CHAIN_TURN", co2_chain_turn())?;
    ns.def(rt, "keystone_cutout", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["station"], &[])?;
        keystone_cutout(rt, &a.req("station")?)
    })?;
    ns.set("CO2_REGULATOR_SETBACK", flt(CO2_REGULATOR_SETBACK))?;
    ns.set("CO2_CHECK_SIDE_OFFSET", flt(CO2_CHECK_SIDE_OFFSET))?;
    ns.set("CO2_CHECK_FORWARD_OFFSET", flt(CO2_CHECK_FORWARD_OFFSET))?;
    ns.def(rt, "co2_inlet_mouth_y", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(co2_inlet_mouth_y(rt)?.val())
    })?;
    ns.def(rt, "co2_wall_port", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["inlet_carry"], &[])?;
        co2_wall_port(rt, &a.req("inlet_carry")?)
    })?;
    let alone = standalone(&kept, ns)?;
    ns.set("STANDALONE", alone.clone())?;
    kept.keep_misc("STANDALONE", alone);
    ns.def(rt, "_manifold", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        let kept = st(rt)?;
        Ok(Val::Bool(manifold_body(&kept, &a.req("name")?)?))
    })?;
    let routed = Val::set_values(vec![]);
    ns.set("_ROUTED", routed.clone())?;
    kept.keep_misc("_ROUTED", routed);
    ns.def(rt, "east_wall_seat", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(east_wall_seat(rt)?.val())
    })?;
    ns.set("FLOOR_BOSS_SLIP", flt(FLOOR_BOSS_SLIP))?;
    ns.set("FLOOR_GROMMET_SQUEEZE", flt(FLOOR_GROMMET_SQUEEZE))?;
    ns.def(rt, "floor_mounts", |_, args, kw| {
        anyhow::ensure!(kw.is_empty(), "unexpected keyword arguments");
        floor_mounts(&args)
    })?;
    Ok(())
}

// ---------------------------------------------------------------------------------------------
// The power rows, the Wago wells and the ASSE chain's anchor (Python lines 1720-1962).

fn turns(rows: &[([f64; 3], f64)]) -> Val {
    Val::Tuple(rows.iter().map(|(axis, deg)| Val::Tuple(vec![f3(*axis), flt(*deg)])).collect())
}

const PSU_AFT_WIRE_ALLOWANCE: f64 = 5.0;
const PSU_RELAY_BODY_GAP: f64 = 4.0;
const RELAY_BOARD_BODY_GAP: f64 = 3.0;
const WIRED_CLEAR: f64 = 6.0;
const RELAY1_CORBEL_LIFT: f64 = 0.0;
const WAGO_CORBEL_FLOOR_CLEAR: f64 = 1.0;

fn wago_skirt(rt: &Rt, size: &Val) -> Result<Num> {
    let st = st(rt)?;
    let half = ixn(&call1(&st.enc, "wago_half", size.clone())?, 1)?;
    let stand = ixn(&call1(&st.enc, "wago_stand", size.clone())?, 1)?;
    Ok(half.sub(stand.div(Num::F(2.0))))
}

fn wago_row_reach(rt: &Rt) -> Result<Num> {
    let st = st(rt)?;
    let pitches = Num::F(4.0).mul(anum(&st.enc, "wago_pitch")?);
    let stand = ixn(&call1(&st.enc, "wago_stand", s("413"))?, 0)?;
    Ok(pitches.add(anum(&st.enc, "wago_well_wall")?).add(stand))
}

fn wago_wells(rt: &Rt, row: &Val, cluster: &Val, over: &Val) -> Result<Val> {
    let st = st(rt)?;
    let up = Num::of(&py::method(&st.enc, "print_up", vec![s("back"), s("top")])?)?;
    let row_clear = if up.f() > 0.0 { over.clone() } else { call0(&st.enc, "back_top_ceiling_face")? };
    let mut out = vec![];
    for item in row.iter()? {
        let r = py::unpack(&item, 3)?;
        let b = st.boxv(&r[1])?;
        let y = (an(&b, "ymin")? + an(&b, "ymax")?) / 2.0;
        let z = (an(&b, "zmin")? + an(&b, "zmax")?) / 2.0;
        out.push(Val::Tuple(vec![Val::Int(1), flt(y), flt(z), s("413"), row_clear.clone(), Val::Bool(true)]));
    }
    let wagos = st.misc("CLUSTER_WAGOS")?;
    for item in cluster.iter()? {
        let r = py::unpack(&item, 4)?;
        let (name, size) = (&r[0], &r[3]);
        let b = st.boxv(&r[1])?;
        let centre = [
            (an(&b, "xmin")? + an(&b, "xmax")?) / 2.0,
            (an(&b, "ymin")? + an(&b, "ymax")?) / 2.0,
            (an(&b, "zmin")? + an(&b, "zmax")?) / 2.0,
        ];
        let owned = up.f() < 0.0 && call1(&st.enc, "back_top_owns", f3(centre))?.truthy()?;
        let clear = if owned { call0(&st.enc, "back_top_ceiling_face")? } else { Val::None };
        out.push(Val::Tuple(vec![
            ix(&wagos.get(name.clone())?, 0)?,
            flt(centre[1]),
            flt(centre[2]),
            size.clone(),
            clear,
            Val::Bool(!interop::eq(name, &s("wago-manb"))?),
        ]));
    }
    Ok(Val::Tuple(out))
}

const ASSE1022_YAW: f64 = -90.0;
const ASSE_STEP_SLIP: f64 = 0.5;
const ASSE_TIE_VENT_CLEAR: f64 = 1.5;
const ASSE_TIE_NECK_ALLOWANCE_D: f64 = 9.53;

/// One section of the ASSE chain: `(y0, y1, west_x, seat_r, axis_x)`.
#[derive(Clone, Copy)]
struct AsseSection {
    y0: Num,
    y1: Num,
    west: Num,
    seat_r: Option<Num>,
    axis_x: Num,
}
impl AsseSection {
    fn val(&self) -> Val {
        Val::Tuple(vec![self.y0.val(), self.y1.val(), self.west.val(), self.seat_r.map_or(Val::None, Num::val), self.axis_x.val()])
    }
}

fn asse_axis(st: &State, carry: &Val) -> Result<Val> {
    ix(&py::call(carry, vec![call0(&st.asse, "flow_axis")?])?, 0)
}

fn asse_sections(rt: &Rt, carry: &Val) -> Result<[AsseSection; 3]> {
    let st = st(rt)?;
    let axis_x = ixn(&asse_axis(&st, carry)?, 0)?;
    let slip = *late!(st.late.asse_seat_slip);
    let bfp = st.asse.attr("bfp")?;
    let band = |x0: Num, x1: Num, across: Num, hexed: bool| -> Result<AsseSection> {
        let mut ends = vec![];
        for x in [x0, x1] {
            let station = Val::Tuple(vec![Val::Tuple(vec![x.val(), flt(0.0), bfp.attr("BODY_CENTER_Z")?]), f3([1.0, 0.0, 0.0])]);
            ends.push(ixn(&ix(&py::call(carry, vec![station])?, 0)?, 1)?);
        }
        ends.sort_by(|a, b| num::order(a.f(), b.f()));
        if hexed {
            let west = axis_x.sub(across.div(Num::F(2.0))).sub(slip.div(Num::F(num::sin(num::radians(60.0)))));
            return Ok(AsseSection { y0: ends[0], y1: ends[1], west, seat_r: None, axis_x });
        }
        let seat_r = across.div(Num::F(2.0)).add(slip);
        Ok(AsseSection { y0: ends[0], y1: ends[1], west: axis_x.sub(seat_r), seat_r: Some(seat_r), axis_x })
    };
    let oad = &st.oad;
    let coupling = st.asse.attr("coupling")?;
    let outlet = anum(&st.asse, "OUTLET_X")?;
    let fwd = band(outlet, outlet.add(anum(oad, "NUT_LENGTH")?), anum(oad, "NUT_ACROSS_CORNERS")?, false)?;
    let barrel = band(anum(&st.asse, "BARREL_UPSTREAM")?, anum(&st.asse, "BARREL_DOWNSTREAM")?, anum(&bfp, "HEX_ACROSS_CORNERS")?, true)?;
    let start = anum(&st.asse, "COUPLING_X")?;
    let aft = band(start, start.add(anum(&coupling, "LENGTH")?), anum(&coupling, "HEX_ACROSS_CORNERS")?, false)?;
    let reach = fwd.y1.sub(fwd.y0).min(aft.y1.sub(aft.y0));
    let mut out = [
        AsseSection { y0: fwd.y1.sub(reach), ..fwd },
        barrel,
        AsseSection { y1: aft.y0.add(reach), ..aft },
    ];
    for i in 0..2 {
        let deep = if out[i].west.f() < out[i + 1].west.f() { i } else { i + 1 };
        let step = if deep == i { Num::F(ASSE_STEP_SLIP) } else { Num::F(-ASSE_STEP_SLIP) };
        let edge = out[i].y1.add(step);
        out[i].y1 = edge;
        out[i + 1].y0 = edge;
    }
    Ok(out)
}
fn asse_sections_val(sections: &[AsseSection; 3]) -> Val {
    Val::Tuple(sections.iter().map(AsseSection::val).collect())
}

fn asse_ties(rt: &Rt, carry: &Val) -> Result<Val> {
    let [_fwd, barrel, _aft] = asse_sections(rt, carry)?;
    let st = st(rt)?;
    let vent = ix(&py::call(carry, vec![call1(&st.asse, "port", s("vent-tip"))?])?, 0)?;
    let vy = ixn(&vent, 1)?;
    let edge = Num::F(ASSE_TIE_NECK_ALLOWANCE_D / 2.0 + ASSE_TIE_VENT_CLEAR);
    Ok(Val::Tuple(vec![
        barrel.y0.add(vy.sub(edge)).div(Num::F(2.0)).val(),
        vy.add(edge).add(barrel.y1).div(Num::F(2.0)).val(),
    ]))
}

fn asse_section_drops(rt: &Rt) -> Result<[Num; 3]> {
    let st = st(rt)?;
    let hexed = anum(&st.asse.attr("bfp")?, "HEX_ACROSS_CORNERS")?.div(Num::F(2.0)).mul(Num::F(num::cos(num::radians(30.0))));
    let nut = anum(&st.oad, "NUT_ACROSS_CORNERS")?.div(Num::F(2.0));
    let coupling = anum(&st.asse.attr("coupling")?, "HEX_ACROSS_CORNERS")?.div(Num::F(2.0));
    Ok([hexed, nut, coupling])
}

fn asse_reach_down(rt: &Rt) -> Result<Num> {
    let [a, b, c] = asse_section_drops(rt)?;
    Ok(a.max(b).max(c))
}

fn asse_cradle(rt: &Rt, carry: &Val) -> Result<Val> {
    let kept = st(rt)?;
    let axis = asse_axis(&kept, carry)?;
    let z = ix(&axis, 2)?;
    let sections = asse_sections_val(&asse_sections(rt, carry)?);
    let ties = asse_ties(rt, carry)?;
    Ok(Val::Tuple(vec![z, sections, ties, asse_reach_down(rt)?.val()]))
}

fn anchor_rows(rt: &Rt, foam_carry: &Val, bodies: &Val) -> Result<Val> {
    let st = st(rt)?;
    let slip = *late!(st.late.chain_seat_slip);
    let rows = Val::list(vec![]);
    for item in call0(&st.cci.attr("cap_anchors")?, "items")?.iter()? {
        let ns_ = py::unpack(&item, 2)?;
        let (name, station) = (&ns_[0], &ns_[1]);
        if !bodies.contains(name)? {
            continue;
        }
        let cm = py::unpack(&bodies.get(name.clone())?, 2)?;
        let (carry, module) = (&cm[0], &cm[1]);
        let axis = ix(&py::call(foam_carry, vec![cap_anchor(rt, name)?])?, 0)?;
        let tip = ix(&py::call(carry, vec![call0(module, "inlet")?])?, 0)?;
        let half = anum(&st.cci, "cap_anchor_len")?.div(Num::F(2.0));
        let outlet = ix(&py::call(carry, vec![call0(module, "outlet")?])?, 0)?;
        let direction = interop::binary("sub", st.vec_of(&outlet)?, st.vec_of(&tip)?)?;
        let offset = interop::binary("sub", st.vec_of(&axis)?, st.vec_of(&tip)?)?;
        let dot = offset.attr("dot")?;
        let distance = Num::of(&py::call(&dot, vec![call0(&direction, "normalized")?])?)?;
        let (s0, s1) = (distance.sub(half), distance.add(half));
        let mut under: Vec<(Val, Num)> = vec![];
        for section in call0(module, "sections")?.iter()? {
            let r = py::unpack(&section, 4)?;
            if Num::of(&r[2])?.f() < s1.f() - 1e-9 && s0.f() + 1e-9 < Num::of(&r[3])?.f() {
                under.push((r[0].clone(), Num::of(&r[1])?));
            }
        }
        let mut fills: Vec<(Val, Num)> = vec![];
        for (lab, r) in &under {
            let seat = anum(station, "seat_r")?;
            if nabs(r.add(slip).sub(seat)).f() <= 1e-3 {
                fills.push((lab.clone(), *r));
            }
        }
        let fouls = Val::list(vec![]);
        for (lab, r) in &under {
            let seat = anum(station, "seat_r")?;
            if r.add(slip).f() > seat.f() + 1e-3 {
                py::method(&fouls, "append", vec![lab.clone()])?;
            }
        }
        let (label, r) = if let Some(first) = fills.first() {
            first.clone()
        } else if let Some(first) = under.first() {
            let mut best = first.clone();
            for row in &under[1..] {
                if row.1.f() > best.1.f() {
                    best = row.clone();
                }
            }
            best
        } else {
            (s("nothing"), Num::F(0.0))
        };
        let held = if fouls.truthy()? || !fills.is_empty() { fouls } else { Val::list(vec![s("no section fills the bore")]) };
        py::method(
            &rows,
            "append",
            vec![Val::Tuple(vec![name.clone(), label, station.attr("seat_r")?, r.add(slip).val(), held])],
        )?;
    }
    Ok(rows)
}

// ---------------------------------------------------------------------------------------------
// Install, Python lines 1720-1962.

fn install_5(rt: &Rt, ns: &Ns) -> Result<()> {
    let kept = st(rt)?;
    ns.set("PSU_TURN", turns(&[([0.0, 1.0, 0.0], -90.0)]))?;
    ns.set("PSU_AFT_WIRE_ALLOWANCE", flt(PSU_AFT_WIRE_ALLOWANCE))?;
    ns.set("PSU_RELAY_BODY_GAP", flt(PSU_RELAY_BODY_GAP))?;
    ns.set("RELAY_BOARD_BODY_GAP", flt(RELAY_BOARD_BODY_GAP))?;
    ns.set("PCBA_TURN", turns(&[([0.0, 1.0, 0.0], -90.0), ([1.0, 0.0, 0.0], -90.0)]))?;
    ns.set("WIRED_CLEAR", flt(WIRED_CLEAR))?;
    ns.set("RELAY_TURN", turns(&[([0.0, 0.0, 1.0], 270.0), ([0.0, 1.0, 0.0], 270.0)]))?;
    ns.set("RELAY1_CORBEL_LIFT", flt(RELAY1_CORBEL_LIFT))?;
    ns.set("WAGO_TURN", turns(&[([1.0, 0.0, 0.0], 90.0), ([0.0, 1.0, 0.0], -90.0)]))?;
    ns.set("WAGO_TURN_WEST", turns(&[([1.0, 0.0, 0.0], 90.0), ([0.0, 1.0, 0.0], 90.0)]))?;
    ns.set("WAGO_CORBEL_FLOOR_CLEAR", flt(WAGO_CORBEL_FLOOR_CLEAR))?;
    ns.def(rt, "_wago_skirt", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["size"], &[])?;
        let size = a.opt("size").unwrap_or_else(|| s("413"));
        Ok(wago_skirt(rt, &size)?.val())
    })?;
    ns.def(rt, "wago_row_reach", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(wago_row_reach(rt)?.val())
    })?;
    ns.def(rt, "wago_wells", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["row", "cluster", "over"], &[])?;
        wago_wells(rt, &a.req("row")?, &a.req("cluster")?, &a.req("over")?)
    })?;
    ns.set("ASSE1022_YAW", flt(ASSE1022_YAW))?;
    let slip = kept.fits.attr("slip")?;
    ns.set("ASSE_SEAT_SLIP", slip.clone())?;
    let _ = kept.late.asse_seat_slip.set(Num::of(&slip)?);
    ns.set("ASSE_STEP_SLIP", flt(ASSE_STEP_SLIP))?;
    ns.def(rt, "asse_sections", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["asse_carry"], &[])?;
        Ok(asse_sections_val(&asse_sections(rt, &a.req("asse_carry")?)?))
    })?;
    ns.set("ASSE_TIE_VENT_CLEAR", flt(ASSE_TIE_VENT_CLEAR))?;
    ns.set("ASSE_TIE_NECK_ALLOWANCE_D", flt(ASSE_TIE_NECK_ALLOWANCE_D))?;
    ns.def(rt, "asse_ties", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["asse_carry"], &[])?;
        asse_ties(rt, &a.req("asse_carry")?)
    })?;
    ns.def(rt, "asse_reach_down", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["asse_carry"], &[])?;
        a.req("asse_carry")?;
        Ok(asse_reach_down(rt)?.val())
    })?;
    ns.def(rt, "_asse_section_drops", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["asse_carry"], &[])?;
        a.req("asse_carry")?;
        Ok(Val::list(asse_section_drops(rt)?.iter().map(|n| n.val()).collect()))
    })?;
    ns.def(rt, "asse_cradle", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["asse_carry"], &[])?;
        asse_cradle(rt, &a.req("asse_carry")?)
    })?;
    ns.def(rt, "anchor_rows", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["foam_carry", "bodies"], &[])?;
        anchor_rows(rt, &a.req("foam_carry")?, &a.req("bodies")?)
    })?;
    Ok(())
}

// ---------------------------------------------------------------------------------------------
// The water split, the pack's carry and its rows (Python lines 1965-2033).

const FLAVOR_STEP: f64 = 42.20;
const BOWL_CLEAR: f64 = 1.0;
const WATER_2: f64 = 42.0;
const SPLIT_FLANK_OFFSET: f64 = 8.65;
const PACK_Y: f64 = 14.48;

fn whole(rt: &Rt, bodies: &Val) -> Result<Val> {
    let st = st(rt)?;
    let mut out = Val::None;
    for body in bodies.iter()? {
        let b = st.boxv(&body)?;
        out = if matches!(out, Val::None) { b } else { call1(&out, "add", b)? };
    }
    Ok(out)
}

/// `manifold_carry(lift)`: the station carry `(x, y, z) → (−x, z + PACK_Y, y + lift)`.
fn manifold_carry(lift: Num) -> Val {
    Val::function(move |args, kw| {
        let mut a = py::bind(args, kw, &["station"], &[])?;
        let station = py::unpack(&a.req("station")?, 2)?;
        let p = py::unpack(&station[0], 3)?;
        let axis = py::unpack(&station[1], 3)?;
        Ok(Val::Tuple(vec![
            Val::Tuple(vec![Num::of(&p[0])?.neg().val(), Num::of(&p[2])?.add(Num::F(PACK_Y)).val(), Num::of(&p[1])?.add(lift).val()]),
            Val::Tuple(vec![Num::of(&axis[0])?.neg().val(), axis[2].clone(), axis[1].clone()]),
        ]))
    })
}

fn manifold_pump_trays(rt: &Rt, carry: &Val) -> Result<Val> {
    let st = st(rt)?;
    let ml = &st.ml;
    let kp = ml.attr("kp")?;
    let head_y = anum(ml, "BARB_INSET")?
        .neg()
        .add(anum(ml, "PUMP_Y")?)
        .sub(anum(&kp, "head_front_z")?)
        .add(anum(&kp, "base_plane_z")?);
    let head_z = anum(ml, "PUMP_BARB_Z")?.sub(anum(&kp, "body_y_face")?).add(anum(&kp, "cy")?);
    let pumps = interop::builtin("sorted").context("sorted")?.call(vec![call0(&ml.attr("PUMPS")?, "items")?], vec![])?;
    let mut stations = vec![];
    for item in pumps.iter()? {
        let px = py::unpack(&item, 2)?[1].clone();
        let station = Val::Tuple(vec![Val::Tuple(vec![px, head_y.val(), head_z.val()]), f3([0.0, 1.0, 0.0])]);
        let mut centre = ix(&py::call(carry, vec![station])?, 0)?.iter()?;
        anyhow::ensure!(centre.len() > 2, "IndexError: list index out of range");
        let drop = anum(&st.enc.attr("_interface")?, "pump_seated_drop")?;
        centre[2] = Num::of(&centre[2])?.add(drop).val();
        stations.push(Val::Tuple(centre.iter().map(|v| Ok(flt(num::round_to(v.num()?, 6)))).collect::<Result<_>>()?));
    }
    Ok(Val::Tuple(stations))
}

fn manifold_references(rt: &Rt, a: &Val) -> Result<Val> {
    let model = rt.import("_assembly_model")?;
    let getattr = interop::builtin("getattr").context("getattr")?;
    let reading = getattr.call(vec![a.clone(), s("manifold_reading"), Val::None], vec![])?;
    if matches!(reading, Val::None) {
        return Ok(Val::dict(vec![]));
    }
    let mut indices: Vec<(Val, Vec<Val>)> = vec![];
    for (index, row) in reading.attr("summaries")?.iter()?.into_iter().enumerate() {
        let name = key(&row, "name")?;
        let at = Val::Int(index as i64);
        match indices.iter_mut().find(|(k, _)| interop::eq(k, &name).unwrap_or(false)) {
            Some((_, rows)) => rows.push(at),
            None => indices.push((name, vec![at])),
        }
    }
    let out = Val::dict(vec![]);
    for (name, selection) in indices {
        let instance = py::call_kw(&model.attr("instance")?, vec![reading.attr("model")?], vec![("indices", Val::list(selection))])?;
        out.set(name, instance)?;
    }
    Ok(out)
}

fn with_manifold_rows(a: &Val, native: &Val, rows: &Val) -> Result<Val> {
    let mut before: Vec<Val> = vec![];
    for child in a.attr("children")?.iter()? {
        let name = child.attr("name")?;
        if interop::eq(&name, &s("manifold-layout"))? {
            break;
        }
        if !before.iter().any(|b| interop::eq(b, &name).unwrap_or(false)) {
            before.push(name);
        }
    }
    let out = Val::dict(vec![]);
    let mut inserted = false;
    for item in call0(native, "items")?.iter()? {
        let nv = py::unpack(&item, 2)?;
        if !inserted && !before.iter().any(|b| interop::eq(b, &nv[0]).unwrap_or(false)) {
            py::method(&out, "update", vec![rows.clone()])?;
            inserted = true;
        }
        out.set(nv[0].clone(), nv[1].clone())?;
    }
    if !inserted {
        py::method(&out, "update", vec![rows.clone()])?;
    }
    Ok(out)
}

// ---------------------------------------------------------------------------------------------
// The ceiling reliefs (Python lines 2036-2251).

const THROUGH_WALL: [&str; 8] = [
    "bulkhead-water",
    "c14-inlet",
    "keystone-jack",
    "co2-inlet",
    "bulkhead-flavor-a",
    "bulkhead-flavor-b",
    "bulkhead-carb",
    "bulkhead-drain",
];
const CEILING_RELIEF_PLAN_SLIP: f64 = 2.0;
const CEILING_RELIEF_Z_CLEAR: f64 = 1.0;
const CEILING_RELIEF_LANE_BODIES: [&str; 1] = ["asse1022-assembly"];
const CEILING_RELIEF_MIN_DEPTH_BODIES: [&str; 1] = ["gasher-co2"];
const CEILING_RELIEF_CONNECTOR_PAIRS: [(&str, &str); 2] = [("asse1022-assembly", "bulkhead-water"), ("digiten-flow", "wr1110")];
const CEILING_RELIEF_CONNECTOR_ENTRY: f64 = 0.5;
const CEILING_RELIEF_ENVELOPE_BODIES: [&str; 1] = ["digiten-flow"];

/// One relief row `(name, x0, x1, y0, y1, roof)`, kept beside the value it was read from.
#[derive(Clone)]
struct Relief {
    row: Val,
    items: Vec<Val>,
    v: [Num; 5],
}
impl Relief {
    fn of(row: &Val) -> Result<Relief> {
        let items = row.iter()?;
        anyhow::ensure!(items.len() >= 6, "IndexError: tuple index out of range");
        let v = [Num::of(&items[1])?, Num::of(&items[2])?, Num::of(&items[3])?, Num::of(&items[4])?, Num::of(&items[5])?];
        Ok(Relief { row: row.clone(), items, v })
    }
    fn new(name: Val, v: [Num; 5]) -> Relief {
        let items: Vec<Val> = std::iter::once(name).chain(v.iter().map(|n| n.val())).collect();
        Relief { row: Val::Tuple(items.clone()), items, v }
    }
    fn name(&self) -> &Val {
        &self.items[0]
    }
    /// `row[i]` for `i` in 1..=5.
    fn at(&self, i: usize) -> Num {
        self.v[i - 1]
    }
    fn f(&self, i: usize) -> f64 {
        self.v[i - 1].f()
    }
    fn is(&self, name: &Val) -> Result<bool> {
        interop::eq(self.name(), name)
    }
    fn is_in(&self, names: &[Val]) -> Result<bool> {
        for n in names {
            if self.is(n)? {
                return Ok(true);
            }
        }
        Ok(false)
    }
    /// `row[:5] + (roof,)`.
    fn with_roof(&self, roof: Num) -> Relief {
        let mut items = self.items[..5].to_vec();
        items.push(roof.val());
        let mut v = self.v;
        v[4] = roof;
        Relief { row: Val::Tuple(items.clone()), items, v }
    }
    /// `(row[0], *(round(value / tol) for value in row[1:]))`.
    fn key(&self, tol: f64) -> Result<(Val, Vec<i64>)> {
        let mut out = vec![];
        for value in &self.items[1..] {
            out.push((value.num()? / tol).round_ties_even() as i64);
        }
        Ok((self.items[0].clone(), out))
    }
}
fn reliefs_of(v: &Val) -> Result<Vec<Relief>> {
    v.iter()?.iter().map(Relief::of).collect()
}
fn reliefs_val(rows: &[Relief]) -> Val {
    Val::Tuple(rows.iter().map(|r| r.row.clone()).collect())
}
fn names(rows: &[&str]) -> Vec<Val> {
    rows.iter().map(|n| s(*n)).collect()
}
/// `min(values)`: the first of equal values wins.
fn nmin(values: impl IntoIterator<Item = Num>) -> Result<Num> {
    values.into_iter().reduce(|a, b| a.min(b)).context("ValueError: min() arg is an empty sequence")
}
fn nmax(values: impl IntoIterator<Item = Num>) -> Result<Num> {
    values.into_iter().reduce(|a, b| a.max(b)).context("ValueError: max() arg is an empty sequence")
}

fn contained_reliefs(rt: &Rt, reliefs: &Val) -> Result<Val> {
    let st = st(rt)?;
    let tol = an(&st.enc, "stated_bound_tol")?;
    let mut out: Vec<Relief> = vec![];
    for row in reliefs_of(reliefs)? {
        let mut contained = false;
        let mut remove = vec![];
        for (i, other) in out.iter().enumerate() {
            if !row.is(other.name())? || nabs(row.at(5).sub(other.at(5))).f() > tol {
                continue;
            }
            let other_contains = other.f(1) <= row.f(1) + tol
                && other.f(2) >= row.f(2) - tol
                && other.f(3) <= row.f(3) + tol
                && other.f(4) >= row.f(4) - tol;
            let row_contains = row.f(1) <= other.f(1) + tol
                && row.f(2) >= other.f(2) - tol
                && row.f(3) <= other.f(3) + tol
                && row.f(4) >= other.f(4) - tol;
            if other_contains {
                contained = true;
                break;
            }
            if row_contains {
                remove.push(i);
            }
        }
        if contained {
            continue;
        }
        for i in remove.into_iter().rev() {
            out.remove(i);
        }
        out.push(row);
    }
    Ok(reliefs_val(&out))
}

fn enveloped_reliefs(rt: &Rt, reliefs: &Val) -> Result<Val> {
    let st = st(rt)?;
    let mut out = reliefs_of(reliefs)?;
    for name in CEILING_RELIEF_ENVELOPE_BODIES {
        let name = s(name);
        let mut indices = vec![];
        for (i, row) in out.iter().enumerate() {
            if row.is(&name)? {
                indices.push(i);
            }
        }
        if indices.len() < 2 {
            continue;
        }
        let rows: Vec<&Relief> = indices.iter().map(|&i| &out[i]).collect();
        let tol = an(&st.enc, "stated_bound_tol")?;
        let x_overlap = nmin(rows.iter().map(|r| r.at(2)))?.sub(nmax(rows.iter().map(|r| r.at(1)))?);
        let y_overlap = nmin(rows.iter().map(|r| r.at(4)))?.sub(nmax(rows.iter().map(|r| r.at(3)))?);
        if x_overlap.f() <= tol || y_overlap.f() <= tol {
            continue;
        }
        let envelope = Relief::new(
            name.clone(),
            [
                nmin(rows.iter().map(|r| r.at(1)))?,
                nmax(rows.iter().map(|r| r.at(2)))?,
                nmin(rows.iter().map(|r| r.at(3)))?,
                nmax(rows.iter().map(|r| r.at(4)))?,
                nmax(rows.iter().map(|r| r.at(5)))?,
            ],
        );
        let first = indices[0];
        let mut kept = vec![];
        for row in out {
            if !row.is(&name)? {
                kept.push(row);
            }
        }
        out = kept;
        out.insert(first.min(out.len()), envelope);
    }
    Ok(reliefs_val(&out))
}

fn level_reliefs(rt: &Rt, reliefs: &Val) -> Result<Val> {
    let st = st(rt)?;
    let mut out = reliefs_of(reliefs)?;
    for group in st.misc("CEILING_RELIEF_LEVEL_GROUPS")?.iter()? {
        let group = group.iter()?;
        let mut roof: Option<Num> = None;
        for row in &out {
            if row.is_in(&group)? {
                roof = Some(match roof {
                    Some(r) => r.max(row.at(5)),
                    None => row.at(5),
                });
            }
        }
        if let Some(roof) = roof {
            let mut next = vec![];
            for row in &out {
                next.push(if row.is_in(&group)? { row.with_roof(roof) } else { row.clone() });
            }
            out = next;
        }
    }
    Ok(reliefs_val(&out))
}

fn full_depth_reliefs(rt: &Rt, reliefs: &Val) -> Result<Val> {
    let st = st(rt)?;
    let face = Num::of(&call0(&st.enc, "back_top_ceiling_face")?)?;
    let tol = an(&st.enc, "stated_bound_tol")?;
    let rows = reliefs.iter()?;
    for row in &rows {
        let depth = ixn(row, 5)?.sub(face);
        let wall = st.enc.attr("wall")?;
        if tol < depth.f() && depth.f() < wall.num()? - tol {
            return Err(err(
                "ValueError",
                format!(
                    "ceiling relief `{}` is only {} mm deep; level it with its purchased-part pocket, omit it, or make it at least one {} mm wall",
                    sv(&ix(row, 0)?)?,
                    depth.fmt(".3f"),
                    gv(&wall)?
                ),
            ));
        }
    }
    Ok(Val::Tuple(rows))
}

fn minimum_depth_reliefs(rt: &Rt, reliefs: &Val) -> Result<Val> {
    let st = st(rt)?;
    let face = Num::of(&call0(&st.enc, "back_top_ceiling_face")?)?;
    let roof = face.add(anum(&st.enc, "wall")?);
    let deep = names(&CEILING_RELIEF_MIN_DEPTH_BODIES);
    let mut out = vec![];
    for row in reliefs.iter()? {
        let name = ix(&row, 0)?;
        let mut listed = false;
        for n in &deep {
            if interop::eq(&name, n)? {
                listed = true;
                break;
            }
        }
        if listed {
            let relief = Relief::of(&row)?;
            out.push(relief.with_roof(relief.at(5).max(roof)).row);
        } else {
            out.push(row);
        }
    }
    Ok(Val::Tuple(out))
}

fn asse_end_reliefs(rt: &Rt, reliefs: &Val, cradle: &Val) -> Result<Val> {
    if !cradle.truthy()? {
        return Ok(reliefs.clone());
    }
    let st = st(rt)?;
    let sections = ix(cradle, 1)?;
    let fore = ix(&ix(&sections, 0)?, 0)?;
    let aft = ix(&ix(&sections, -1)?, 1)?;
    let (fore_n, aft_n) = (Num::of(&fore)?, Num::of(&aft)?);
    let keep = Num::F(ASSE_STEP_SLIP).add(*late!(st.late.asse_seat_slip));
    let mut out = vec![];
    for row in reliefs.iter()? {
        let mut r = py::unpack(&row, 6)?;
        if interop::eq(&r[0], &s("asse1022-assembly"))? {
            let wall = an(&st.enc, "wall")?;
            let y1 = Num::of(&r[4])?;
            let over = y1.sub(aft_n).f();
            if 0.0 < over && over < wall && y1.sub(Num::F(CEILING_RELIEF_PLAN_SLIP)).add(keep).f() <= aft_n.f() {
                r[4] = aft.clone();
            }
            let y0 = Num::of(&r[3])?;
            let short = fore_n.sub(y0).f();
            if 0.0 < short && short < an(&st.enc, "wall")? && y0.add(Num::F(CEILING_RELIEF_PLAN_SLIP)).sub(keep).f() >= fore_n.f() {
                r[3] = fore.clone();
            }
        }
        out.push(Val::Tuple(r));
    }
    Ok(Val::Tuple(out))
}

fn connected_reliefs(rt: &Rt, reliefs: &Val) -> Result<Val> {
    let st = st(rt)?;
    let source = reliefs_of(reliefs)?;
    let mut out = source.clone();
    let tol = an(&st.enc, "stated_bound_tol")?;
    let wall = an(&st.enc, "wall")?;
    let same = |a: &(Val, Vec<i64>), b: &(Val, Vec<i64>)| a.1 == b.1 && interop::eq(&a.0, &b.0).unwrap_or(false);
    let mut keys: Vec<(Val, Vec<i64>)> = vec![];
    for p in &source {
        let k = p.key(tol)?;
        if !keys.iter().any(|x| same(x, &k)) {
            keys.push(k);
        }
    }
    let entry = Num::F(CEILING_RELIEF_CONNECTOR_ENTRY);
    for (left, right) in CEILING_RELIEF_CONNECTOR_PAIRS {
        let mut left_rows = vec![];
        let mut right_rows = vec![];
        for row in &source {
            if row.is(&s(left))? {
                left_rows.push(row);
            }
        }
        for row in &source {
            if row.is(&s(right))? {
                right_rows.push(row);
            }
        }
        if left_rows.is_empty() && right_rows.is_empty() {
            continue;
        }
        let mut candidates = vec![];
        for p in &left_rows {
            for q in &right_rows {
                let x_overlap = p.at(2).min(q.at(2)).sub(p.at(1).max(q.at(1)));
                let y_overlap = p.at(4).min(q.at(4)).sub(p.at(3).max(q.at(3)));
                let x_gap = q.at(1).sub(p.at(2)).max(p.at(1).sub(q.at(2)));
                let y_gap = q.at(3).sub(p.at(4)).max(p.at(3).sub(q.at(4)));
                let separated_x = x_gap.f() > tol;
                let separated_y = y_gap.f() > tol;
                if separated_x == separated_y {
                    continue;
                }
                let (x0, x1, y0, y1);
                if separated_x {
                    if x_gap.f() >= wall || y_overlap.f() <= tol {
                        continue;
                    }
                    x0 = p.at(2).min(q.at(2)).sub(entry);
                    x1 = p.at(1).max(q.at(1)).add(entry);
                    (y0, y1) = (p.at(3).max(q.at(3)), p.at(4).min(q.at(4)));
                } else {
                    if y_gap.f() >= wall || x_overlap.f() <= tol {
                        continue;
                    }
                    (x0, x1) = (p.at(1).max(q.at(1)), p.at(2).min(q.at(2)));
                    y0 = p.at(4).min(q.at(4)).sub(entry);
                    y1 = p.at(3).max(q.at(3)).add(entry);
                }
                candidates.push(Relief::new(s(format!("{left}/{right} connector")), [x0, x1, y0, y1, p.at(5).min(q.at(5))]));
            }
        }
        let mut unique: Vec<Relief> = vec![];
        let mut pair_keys: Vec<(Val, Vec<i64>)> = vec![];
        for connector in candidates {
            let k = connector.key(tol)?;
            if !pair_keys.iter().any(|x| same(x, &k)) {
                pair_keys.push(k);
                unique.push(connector);
            }
        }
        for connector in unique {
            let k = connector.key(tol)?;
            if !keys.iter().any(|x| same(x, &k)) {
                keys.push(k);
                out.push(connector);
            }
        }
    }
    Ok(reliefs_val(&out))
}

// ---------------------------------------------------------------------------------------------
// Anchor stands, well columns and the front flank (Python lines 2254-2423).

const WEDGE_CLEAR: f64 = 1.0;
const WELL_COLUMNS: [(i64, f64); 2] = [(1, 322.25), (-1, 270.0)];
const PLAN_INSET: f64 = 0.02;

fn well_columns() -> Val {
    Val::Tuple(WELL_COLUMNS.iter().map(|(side, z)| Val::Tuple(vec![Val::Int(*side), flt(*z)])).collect())
}

fn stand_anchors(rt: &Rt, stations: &Val) -> Result<Val> {
    let st = st(rt)?;
    let up = py::method(&st.enc, "print_up", vec![s("back"), s("top")])?;
    let frames = py::unpack(&call0(&st.enc, "back_top_frames")?, 2)?;
    let (roots, lane) = (&frames[0], &frames[1]);
    let face_z = call0(&st.enc, "back_top_ceiling_face")?;
    let forms_ok = strs(&ANCHOR_END_FORMS);
    let mut out = vec![];
    for station in stations.iter()? {
        let items = station.iter()?;
        let end_forms = if items.len() > 4 { items[4].iter()? } else { vec![s("corbel"), s("corbel")] };
        let mut bad = end_forms.len() != 2;
        if !bad {
            for form in &end_forms {
                if !forms_ok.contains(form)? {
                    bad = true;
                    break;
                }
            }
        }
        if bad {
            return Err(err(
                "ValueError",
                format!(
                    "stand_anchors: end forms are {}; each end must be one of {}.",
                    Val::Tuple(end_forms.clone()).repr()?,
                    sv(&forms_ok)?
                ),
            ));
        }
        let head = Val::Tuple(items.iter().take(4).cloned().collect());
        let capped = items.len() >= 6 && interop::eq(&items[5], &s("cap"))?;
        let mid = ix(&head, 0)?;
        let at = || -> Result<String> {
            Ok(format!("({}, {}, {})", fv(&ix(&mid, 0)?, ".2f")?, fv(&ix(&mid, 1)?, ".2f")?, fv(&ix(&mid, 2)?, ".2f")?))
        };
        if !call1(&st.enc, "back_top_owns", mid.clone())?.truthy()? {
            if capped {
                return Err(err(
                    "ValueError",
                    format!(
                        "stand_anchors: the anchor at {} is capped and stands outside back-top's band; the box's anchor caps close ribs back-top builds.",
                        at()?
                    ),
                ));
            }
            out.push(head);
            continue;
        }
        let columns = py::method(
            &st.enc,
            "tube_anchor_end_columns",
            vec![head.clone(), roots.clone(), lane.clone(), up.clone(), face_z.clone()],
        )?
        .iter()?;
        let mut stand = vec![];
        for (end, (form, column)) in end_forms.iter().zip(columns.iter()).enumerate() {
            if interop::eq(form, &s("corbel"))? {
                stand.push(Val::None);
                continue;
            }
            if matches!(column, Val::None) {
                return Err(err(
                    "ValueError",
                    format!(
                        "stand_anchors: the anchor at {} states `column` on end {}, and that rib has no column to the print-bed face — its site should say `corbel`.",
                        at()?,
                        end + 1
                    ),
                ));
            }
            stand.push(Val::Tuple(vec![face_z.clone(), Val::None]));
        }
        let mut row = head.iter()?;
        row.push(Val::Tuple(stand));
        if capped {
            row.push(s("cap"));
        }
        out.push(Val::Tuple(row));
    }
    Ok(Val::Tuple(out))
}

fn stand_wells(stations: &Val) -> Result<Val> {
    let rows = stations.iter()?;
    let mut by_row: Vec<(Val, Vec<Val>)> = vec![];
    for row in &rows {
        let items = row.iter()?;
        let six = py::unpack(&Val::Tuple(items.into_iter().take(6).collect()), 6)?;
        let k = Val::Tuple(vec![six[0].clone(), flt(num::round_to(six[2].num()?, 4))]);
        match by_row.iter_mut().find(|(r, _)| interop::eq(r, &k).unwrap_or(false)) {
            Some((_, clears)) => clears.push(six[4].clone()),
            None => by_row.push((k, vec![six[4].clone()])),
        }
    }
    let columns = well_columns();
    for k in columns.iter()? {
        let Some((_, clears)) = by_row.iter().find(|(r, _)| interop::eq(r, &k).unwrap_or(false)) else {
            return Err(err(
                "ValueError",
                format!("WELL_COLUMNS names the row {}, and no well stands there; the row it was written for has moved or gone.", sv(&k)?),
            ));
        };
        if clears.iter().any(|c| matches!(c, Val::None)) {
            return Err(err(
                "ValueError",
                format!(
                    "WELL_COLUMNS names the row {}, and its wells have no plane to stand a column on. A row off the ceiling-down piece cannot carry one.",
                    sv(&k)?
                ),
            ));
        }
    }
    let mut out = vec![];
    for row in &rows {
        let items = row.iter()?;
        let mut head: Vec<Val> = items.iter().take(6).cloned().collect();
        let k = Val::Tuple(vec![ix(row, 0)?, flt(num::round_to(ixf(row, 2)?, 4))]);
        if columns.contains(&k)? {
            head.push(Val::Bool(true));
        } else if !matches!(ix(row, 4)?, Val::None) {
            head.push(Val::Bool(false));
        }
        out.push(Val::Tuple(head));
    }
    Ok(Val::Tuple(out))
}

fn authored_anchor_corbels(rt: &Rt, stations: &Val) -> Result<Val> {
    let st = st(rt)?;
    let frames = py::unpack(&call0(&st.enc, "back_top_frames")?, 2)?;
    let up = py::method(&st.enc, "print_up", vec![s("back"), s("top")])?;
    let mut rooms = vec![];
    for station in stations.iter()? {
        if station.len()? < 5 {
            continue;
        }
        let forms = ix(&station, 4)?.iter()?;
        let bounds = py::method(
            &st.enc,
            "tube_anchor_end_corbel_bounds",
            vec![station.clone(), frames[0].clone(), frames[1].clone(), up.clone()],
        )?
        .iter()?;
        for (end, (form, bound)) in forms.iter().zip(bounds.iter()).enumerate() {
            if !interop::eq(form, &s("corbel"))? || matches!(bound, Val::None) {
                continue;
            }
            let mid = ix(&station, 0)?;
            rooms.push(Val::Tuple(vec![
                s(format!(
                    "tube anchor at ({}, {}, {}), end {}",
                    fv(&ix(&mid, 0)?, ".2f")?,
                    fv(&ix(&mid, 1)?, ".2f")?,
                    fv(&ix(&mid, 2)?, ".2f")?,
                    end + 1
                )),
                bound.clone(),
                s("the anchor site specifies its ordinary full-width 45-degree corbel"),
            ]));
        }
    }
    Ok(Val::Tuple(rooms))
}

/// The probe box `tool(lower, upper, lo, hi)` the front flank's readings take.
fn flank_tool(lower: &[Num; 3], upper: &[Num; 3], lo: Num, hi: Num) -> Val {
    let origin = [lo, lower[1].sub(Num::F(1.0)), lower[2].sub(Num::F(1.0))];
    let span = [hi.sub(lo), upper[1].sub(lower[1]).add(Num::F(2.0)), upper[2].sub(lower[2]).add(Num::F(2.0))];
    Val::list(vec![
        Val::list(origin.iter().map(|n| n.val()).collect()),
        Val::list(origin.iter().zip(span).map(|(p, d)| p.add(d).val()).collect()),
    ])
}

struct FlankPlan {
    name: &'static str,
    side: f64,
    face: Num,
    coil: Val,
    crossing: Option<Val>,
}

fn front_flank_reliefs_fine(rt: &Rt, reference: &Val, transform: &Val) -> Result<Val> {
    let model = rt.import("_assembly_model")?;
    let st = st(rt)?;
    let mut entries: Vec<(String, Vec<Val>)> = vec![];
    for (index, row) in reference.attr("summaries")?.iter()?.into_iter().enumerate() {
        let full = key(&row, "name")?.str()?;
        let (stem, tail) = match full.rfind('/') {
            Some(i) => (&full[..i], &full[i + 1..]),
            None => ("", full.as_str()),
        };
        let digits = !tail.is_empty() && tail.chars().all(|c| c.is_ascii_digit());
        let name = if digits { stem.to_owned() } else { full.clone() };
        let at = Val::Int(index as i64);
        match entries.iter_mut().find(|(k, _)| *k == name) {
            Some((_, rows)) => rows.push(at),
            None => entries.push((name, vec![at])),
        }
    }
    let entry_list = |name: &str| -> Result<Val> {
        let rows = entries.iter().find(|(k, _)| k == name).with_context(|| format!("missing key {}", s(name).repr().unwrap_or_default()))?;
        Ok(Val::list(rows.1.clone()))
    };
    let air = Num::of(&st.card.attr("CLEARANCE_FLOOR")?)?;
    let bounds_of = |name: &str| -> Result<([Num; 3], [Num; 3])> {
        let lu = py::unpack(&reference.attr("raw_bounds")?.get(s(name))?, 2)?;
        Ok((three_n(&lu[0])?, three_n(&lu[1])?))
    };
    let mut plans: Vec<(&'static str, &'static str, f64, Num)> = vec![];
    let mut requests = vec![];
    for (name, valve) in [("coil-v-f", "valve-v-f"), ("coil-v-i", "valve-v-i")] {
        let (lower, upper) = bounds_of(name)?;
        let side = if lower[0].add(upper[0]).div(Num::F(2.0)).f() > 0.0 { 1.0 } else { -1.0 };
        let face = ixn(&call0(&st.enc, "front_top_flank_face")?, if side > 0.0 { 1 } else { 0 })?;
        let (lo, hi) = if side > 0.0 { (face.sub(air), upper[0].add(Num::F(1.0))) } else { (lower[0].sub(Num::F(1.0)), face.add(air)) };
        if hi.f() <= lo.f() {
            continue;
        }
        plans.push((name, valve, side, face));
        requests.push(sdict(vec![("indices", entry_list(name)?), ("box", flank_tool(&lower, &upper, lo, hi))]));
    }
    let box_commons = |requests: Vec<Val>| -> Result<Vec<Val>> {
        py::call_kw(&model.attr("box_commons")?, vec![reference.attr("model")?, Val::list(requests)], vec![("transform", transform.clone())])?.iter()
    };
    let readings = box_commons(requests)?;
    let mut active: Vec<FlankPlan> = vec![];
    let mut valves: Vec<(usize, Val)> = vec![];
    for ((name, valve, side, face), reading) in plans.into_iter().zip(readings) {
        let raw = key(&reading, "raw")?;
        if matches!(key(&raw, "min")?, Val::None) {
            continue;
        }
        let (lower, upper) = bounds_of(valve)?;
        let (lo, hi) = if side > 0.0 { (face, upper[0].add(Num::F(1.0))) } else { (lower[0].sub(Num::F(1.0)), face) };
        if hi.f() > lo.f() {
            valves.push((active.len(), sdict(vec![("indices", entry_list(valve)?), ("box", flank_tool(&lower, &upper, lo, hi))])));
        }
        active.push(FlankPlan { name, side, face, coil: raw, crossing: None });
    }
    let readings = box_commons(valves.iter().map(|(_, request)| request.clone()).collect())?;
    for ((owner, _), reading) in valves.iter().zip(readings) {
        let raw = key(&reading, "raw")?;
        if !matches!(key(&raw, "min")?, Val::None) {
            active[*owner].crossing = Some(raw);
        }
    }
    let mut pockets = vec![];
    for plan in &active {
        let mut bounds = vec![plan.coil.clone()];
        if let Some(crossing) = &plan.crossing {
            bounds.push(crossing.clone());
        }
        let mut axes: [Vec<Num>; 3] = [vec![], vec![], vec![]];
        for (k, values) in axes.iter_mut().enumerate() {
            for row in &bounds {
                for end in ["min", "max"] {
                    values.push(ixn(&key(row, end)?, k as i64)?);
                }
            }
        }
        let [xs, ys, zs] = axes;
        let floor = if plan.side > 0.0 { nmax(xs)?.add(air) } else { nmin(xs)?.sub(air) };
        let interior: Vec<Num> = call0(&st.enc, "interior_x")?.iter()?.iter().map(Num::of).collect::<Result<_>>()?;
        let nearest = nmin(interior.iter().map(|x| nabs(*x)))?;
        if nabs(floor).f() > nearest.f() {
            return Err(err("ValueError", format!("{} clearance would enter the nominal enclosure wall", plan.name)));
        }
        pockets.push(Val::Tuple(vec![
            s(plan.name),
            plan.face.min(floor).val(),
            plan.face.max(floor).val(),
            nmin(ys.iter().copied())?.sub(air).val(),
            nmax(ys)?.add(air).val(),
            nmin(zs.iter().copied())?.sub(air).val(),
            nmax(zs)?.add(air).val(),
        ]));
    }
    Ok(Val::Tuple(pockets))
}

fn above_core_ceiling_reliefs(rt: &Rt) -> Result<Val> {
    let st = st(rt)?;
    let pockets = key(&key(&call0(&st.above, "specification")?, "ceiling_pockets")?, "pockets")?;
    let mut out = vec![];
    for p in pockets.iter()? {
        let mut row = vec![];
        for k in ["name", "xmin", "xmax", "ymin", "ymax", "zmax"] {
            row.push(key(&p, k)?);
        }
        out.push(Val::Tuple(row));
    }
    Ok(Val::Tuple(out))
}

fn funnel_centre(rt: &Rt, b: &Val) -> Result<Val> {
    let inner = b.attr("inner")?;
    let x = ixn(&inner, 0)?.add(ixn(&b.attr("inner")?, 1)?).div(Num::I(2));
    Ok(Val::Tuple(vec![x.val(), st(rt)?.funnel_frame.attr("center_y")?]))
}

const RIDGE_REACH: f64 = 60.0;
const SEAT_TOL: f64 = 1e-6;
const NOT_A_BODY: [&str; 5] = ["tube-", "turn-", "step-", "stub-", "enclosure-"];

fn seat_off(seat: &Val) -> Result<Val> {
    let rule = seat.attr("rule")?;
    if rule.contains(&s("station"))? {
        let got = key(&seat.attr("got")?, "station")?.iter()?;
        let want = key(&seat.attr("rule")?, "station")?.iter()?;
        let mut misses = vec![];
        for (g, w) in got.iter().zip(want.iter()) {
            misses.push(nabs(Num::of(g)?.sub(Num::of(w)?)));
        }
        return Ok(nmax(misses)?.val());
    }
    let mut misses = vec![];
    for item in call0(&seat.attr("rule")?, "items")?.iter()? {
        let kv = py::unpack(&item, 2)?;
        let got = seat.attr("got")?;
        if got.contains(&kv[0])? {
            misses.push(nabs(Num::of(&seat.attr("got")?.get(kv[0].clone())?)?.sub(Num::of(&kv[1])?)));
        }
    }
    Ok(match nmax(misses) {
        Ok(worst) => worst.val(),
        Err(_) => flt(0.0),
    })
}

// ---------------------------------------------------------------------------------------------
// Install, Python lines 1965-2458.

fn install_6(rt: &Rt, ns: &Ns) -> Result<()> {
    let kept = st(rt)?;
    ns.set("SPLIT_TURN", turns(&[([0.0, 1.0, 0.0], -90.0)]))?;
    ns.set("FLAVOR_STEP", flt(FLAVOR_STEP))?;
    ns.set("BOWL_CLEAR", flt(BOWL_CLEAR))?;
    ns.set("WATER_2", flt(WATER_2))?;
    ns.set("SPLIT_FLANK_OFFSET", flt(SPLIT_FLANK_OFFSET))?;
    ns.def(rt, "_whole", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["bodies"], &[])?;
        whole(rt, &a.req("bodies")?)
    })?;
    ns.set("PACK_Y", flt(PACK_Y))?;
    ns.def(rt, "manifold_carry", |_, args, kw| {
        let mut a = py::bind(args, kw, &["lift"], &[])?;
        Ok(manifold_carry(Num::of(&a.req("lift")?)?))
    })?;
    ns.def(rt, "manifold_pump_trays", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["carry"], &[])?;
        manifold_pump_trays(rt, &a.req("carry")?)
    })?;
    ns.def(rt, "manifold_references", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["a"], &[])?;
        manifold_references(rt, &a.req("a")?)
    })?;
    ns.def(rt, "_with_manifold_rows", |_, args, kw| {
        let mut a = py::bind(args, kw, &["a", "native", "rows"], &[])?;
        with_manifold_rows(&a.req("a")?, &a.req("native")?, &a.req("rows")?)
    })?;
    ns.set("THROUGH_WALL", strs(&THROUGH_WALL))?;
    ns.set("CEILING_RELIEF_PLAN_SLIP", flt(CEILING_RELIEF_PLAN_SLIP))?;
    ns.set("CEILING_RELIEF_Z_CLEAR", flt(CEILING_RELIEF_Z_CLEAR))?;
    let gas = ns.get("_gas_chain")?;
    let groups = Val::Tuple(vec![
        strs(&["asse1022-assembly"]),
        strs(&["digiten-flow"]),
        Val::Tuple(vec![s("wr1110"), gas.attr("REG_IN_ADAPTER")?, gas.attr("REG_OUT_ADAPTER")?]),
        Val::Tuple(vec![s("gasher-co2"), gas.attr("CHECK_IN_ADAPTER")?, gas.attr("CHECK_OUT_ADAPTER")?]),
    ]);
    ns.set("CEILING_RELIEF_LEVEL_GROUPS", groups.clone())?;
    kept.keep_misc("CEILING_RELIEF_LEVEL_GROUPS", groups);
    ns.set("CEILING_RELIEF_LANE_BODIES", strs(&CEILING_RELIEF_LANE_BODIES))?;
    ns.set("CEILING_RELIEF_MIN_DEPTH_BODIES", strs(&CEILING_RELIEF_MIN_DEPTH_BODIES))?;
    ns.set(
        "CEILING_RELIEF_CONNECTOR_PAIRS",
        Val::Tuple(CEILING_RELIEF_CONNECTOR_PAIRS.iter().map(|(a, b)| strs(&[a, b])).collect()),
    )?;
    ns.set("CEILING_RELIEF_CONNECTOR_ENTRY", flt(CEILING_RELIEF_CONNECTOR_ENTRY))?;
    ns.set("CEILING_RELIEF_ENVELOPE_BODIES", strs(&CEILING_RELIEF_ENVELOPE_BODIES))?;
    ns.def(rt, "_contained_reliefs", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["reliefs"], &[])?;
        contained_reliefs(rt, &a.req("reliefs")?)
    })?;
    ns.def(rt, "_enveloped_reliefs", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["reliefs"], &[])?;
        enveloped_reliefs(rt, &a.req("reliefs")?)
    })?;
    ns.def(rt, "_level_reliefs", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["reliefs"], &[])?;
        level_reliefs(rt, &a.req("reliefs")?)
    })?;
    ns.def(rt, "_full_depth_reliefs", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["reliefs"], &[])?;
        full_depth_reliefs(rt, &a.req("reliefs")?)
    })?;
    ns.def(rt, "_minimum_depth_reliefs", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["reliefs"], &[])?;
        minimum_depth_reliefs(rt, &a.req("reliefs")?)
    })?;
    ns.def(rt, "_asse_end_reliefs", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["reliefs", "cradle"], &[])?;
        asse_end_reliefs(rt, &a.req("reliefs")?, &a.req("cradle")?)
    })?;
    ns.def(rt, "_connected_reliefs", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["reliefs"], &[])?;
        connected_reliefs(rt, &a.req("reliefs")?)
    })?;
    ns.set("WEDGE_CLEAR", flt(WEDGE_CLEAR))?;
    ns.set("WELL_COLUMNS", well_columns())?;
    ns.set("KEPT_WEDGES", Val::Tuple(vec![]))?;
    ns.def(rt, "stand_anchors", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["stations"], &[])?;
        stand_anchors(rt, &a.req("stations")?)
    })?;
    ns.def(rt, "stand_wells", |_, args, kw| {
        let mut a = py::bind(args, kw, &["stations"], &[])?;
        stand_wells(&a.req("stations")?)
    })?;
    ns.set("_PLAN_INSET", flt(PLAN_INSET))?;
    ns.def(rt, "authored_anchor_corbels", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["stations"], &[])?;
        authored_anchor_corbels(rt, &a.req("stations")?)
    })?;
    ns.def(rt, "front_flank_reliefs_fine", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["reference"], &["transform"])?;
        let reference = a.req("reference")?;
        let transform = a.opt("transform").unwrap_or(Val::None);
        front_flank_reliefs_fine(rt, &reference, &transform)
    })?;
    ns.def(rt, "above_core_ceiling_reliefs", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        above_core_ceiling_reliefs(rt)
    })?;
    ns.def(rt, "funnel_centre", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["box"], &[])?;
        funnel_centre(rt, &a.req("box")?)
    })?;
    ns.set("COVER_ORIGIN", Val::Tuple(vec![f3([0.0, 0.0, 0.0]), f3([0.0, 0.0, 1.0])]))?;
    ns.set("RIDGE_REACH", flt(RIDGE_REACH))?;
    ns.set("SEAT_TOL", flt(SEAT_TOL))?;
    ns.set("NOT_A_BODY", strs(&NOT_A_BODY))?;
    ns.def(rt, "seat_off", |_, args, kw| {
        let mut a = py::bind(args, kw, &["seat"], &[])?;
        seat_off(&a.req("seat")?)
    })?;
    Ok(())
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    install_1(rt, ns)?;
    install_2(rt, ns)?;
    install_3(rt, ns)?;
    install_4(rt, ns)?;
    install_5(rt, ns)?;
    install_6(rt, ns)?;
    Ok(())
}
