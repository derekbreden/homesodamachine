//! Reference curved grip receiver and flat-wing cover geometry.
//!
//! The recorded coupon and cover trials use these reliefs, slots and placement.
//! The production enclosure has integral exposed handholds.
//!
//! `GripInterface` is the class the Python stub declares: one pair of mirrored handholds in the
//! enclosure coordinate frame. Its methods (`"GripInterface.<method>"`) work on the Python
//! instance: `__init__` sets its figures as attributes, and every other method reads the ones it
//! uses back off the instance when it is called, and the shell's off `self.shell`. CadQuery and
//! `overhang_round.transition` stay providers, reached by callback.
use super::num::Num;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::Result;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_grip_interface";

pub struct State {
    pub cq: Val,
    transition: Val,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let transition = rt.member("overhang_round", "transition")?;
    ns.set("transition", transition.clone())?;
    rt.keep(MODULE, State { cq, transition });

    ns.def(rt, "GripInterface.__init__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "shell"], &["floor_z"])?;
        let this = b.req("self")?;
        let shell = b.req("shell")?;
        let floor_z = Num::of(&b.opt("floor_z").unwrap_or(Val::Float(0.0)))?;
        init(rt, &this, shell, floor_z)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "GripInterface.box", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "x0", "x1", "y0", "y1", "z0", "z1"], &[])?;
        b.req("self")?;
        let [x0, x1, y0, y1, z0, z1] = ["x0", "x1", "y0", "y1", "z0", "z1"].map(|name| b.req(name));
        make_box(rt, [x0?, x1?, y0?, y1?, z0?, z1?])
    })?;
    ns.def(rt, "GripInterface.rounded", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "width", "height", "z0", "z1", "radius"], &[])?;
        b.req("self")?;
        let (width, height) = (b.req("width")?, b.req("height")?);
        let (z0, z1, radius) = (b.req("z0")?, b.req("z1")?, b.req("radius")?);
        rounded(rt, width, height, z0, z1, radius)
    })?;
    ns.def(rt, "GripInterface.wing", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "end"], &[])?;
        let this = b.req("self")?;
        wing(rt, &this, Num::of(&b.req("end")?)?)
    })?;
    ns.def(rt, "GripInterface.cover", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self"], &[])?;
        cover(rt, &b.req("self")?)
    })?;
    ns.def(rt, "GripInterface.placed", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "shape", "side", "drop"], &[])?;
        let this = b.req("self")?;
        let shape = b.req("shape")?;
        let side = b.opt("side").unwrap_or(Val::Int(1));
        let drop = Num::of(&b.opt("drop").unwrap_or(Val::Int(0)))?;
        placed(rt, &this, &shape, &side, drop)
    })?;
    ns.def(rt, "GripInterface.receiver_reliefs", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self"], &[])?;
        Ok(Val::list(receiver_reliefs(rt, &b.req("self")?)?))
    })?;
    ns.def(rt, "GripInterface.receiver_slots", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self"], &[])?;
        Ok(Val::list(receiver_slots(rt, &b.req("self")?)?))
    })?;
    ns.def(rt, "GripInterface.apply_receiver", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "solid", "piece"], &[])?;
        let this = b.req("self")?;
        let (solid, piece) = (b.req("solid")?, b.req("piece")?);
        apply_receiver(rt, &this, solid, &piece)
    })?;
    ns.set("GripInterface", rt.python_type(MODULE, "GripInterface")?)?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// A number attribute of an instance or the shell.
fn n(object: &Val, name: &str) -> Result<Num> {
    Num::of(&object.attr(name)?)
}

/// `GripInterface.__init__(shell, *, floor_z=0.0)`: the handholds' figures, set on the instance.
fn init(rt: &Rt, this: &Val, shell: Val, floor_z: Num) -> Result<()> {
    let transition = state(rt)?.transition.clone();
    let set = |name: &str, value: Num| this.setattr(name, value.val());
    this.setattr("shell", shell)?;
    let shell = this.attr("shell")?;
    let body_air = n(&shell.attr("fits")?, "slip")?;
    set("BODY_AIR", body_air)?;
    let length = n(&shell, "handhold_length")?.sub(Num::I(2).mul(body_air));
    set("LENGTH", length)?;
    let x_ext = n(&shell, "appliance_width")?.div(Num::I(2));
    set("X_EXT", x_ext)?;
    let band = py::unpack(&py::call(&shell.attr("_band_x")?, vec![x_ext.val(), Val::Int(-1)])?, 2)?;
    let cap = Num::of(&band[1])?;
    let inner_face = cap.add(n(&shell, "handhold_wall")?);
    set("INNER_FACE", inner_face)?;
    let edge = py::item(&py::call(&transition, vec![shell.attr("handhold_edge_r")?])?, Val::Int(1))?;
    let outer_flat = x_ext.sub(Num::of(&edge)?);
    set("OUTER_FLAT", outer_flat)?;
    let width = outer_flat.sub(inner_face).sub(body_air);
    set("WIDTH", width)?;
    let x_center = outer_flat.add(inner_face).add(body_air).div(Num::I(2));
    set("X_CENTER", x_center)?;
    let roof = floor_z.sub(n(&shell, "floor_t")?).add(n(&shell, "handhold_height")?)
        .add(n(&shell.attr("fits")?, "supported_surface")?);
    set("ROOF", roof)?;
    set("CROWN", roof.add(n(&shell, "handhold_roof")?))?;
    // Accepted flat-wing section; the cover and both wings share the bed.
    for (name, value) in [("THICK", 3.36), ("WING_THICK", 1.68), ("WING_REACH", 2.4), ("WING_SPAN", 5.0),
        ("WING_END_R", 0.6), ("CORNER_R", 0.6), ("TOUCH_R", 0.6)] {
        set(name, Num::F(value))?;
    }
    set("WING_END_AIR", n(&shell.attr("fits")?, "slip")?)?;
    set("BEARING_AIR", Num::F(0.45))?;
    let back_air = n(&shell.attr("fits")?, "supported_surface")?;
    set("BACK_AIR", back_air)?;
    set("ENTRY_WIDTH", Num::F(1.1))?;
    set("ENTRY_DEPTH", Num::F(0.4))?;
    set("BACK", roof.sub(back_air))
}

/// `cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))`.
pub fn make_box(rt: &Rt, bounds: [Val; 6]) -> Result<Val> {
    let cq = &state(rt)?.cq;
    let [x0, x1, y0, y1, z0, z1] = bounds;
    let size = |a: &Val, b: &Val| -> Result<Val> { Ok(Num::of(b)?.sub(Num::of(a)?).val()) };
    let (dx, dy, dz) = (size(&x0, &x1)?, size(&y0, &y1)?, size(&z0, &z1)?);
    let corner = py::call(&cq.attr("Vector")?, vec![x0, y0, z0])?;
    py::call(&cq.attr("Solid")?.attr("makeBox")?, vec![dx, dy, dz, corner])
}

/// A `width` by `height` plate from z0 to z1, its vertical edges rounded `radius`.
pub fn rounded(rt: &Rt, width: Val, height: Val, z0: Val, z1: Val, radius: Val) -> Result<Val> {
    let cq = &state(rt)?.cq;
    let rise = Num::of(&z1)?.sub(Num::of(&z0)?);
    let wp = py::call(&cq.attr("Workplane")?, vec![py::s("XY")])?;
    let wp = py::call_kw(&wp.attr("workplane")?, vec![], vec![("offset", z0)])?;
    let wp = py::method(&py::method(&wp, "rect", vec![width, height])?, "extrude", vec![rise.val()])?;
    let wp = py::method(&py::method(&wp, "edges", vec![py::s("|Z")])?, "fillet", vec![radius])?;
    py::method(&wp, "val", vec![])
}

/// One wing, at the `end` of the strip.
pub fn wing(rt: &Rt, this: &Val, end: Num) -> Result<Val> {
    let reach = n(this, "WING_REACH")?;
    let blank = rounded(rt, reach.add(Num::I(1)).val(), this.attr("WING_SPAN")?, Val::Int(0), this.attr("WING_THICK")?,
        this.attr("WING_END_R")?)?;
    let x = end.mul(n(this, "LENGTH")?.div(Num::I(2)).add(n(this, "WING_REACH")?.sub(Num::I(1)).div(Num::I(2))));
    py::method(&blank, "translate", vec![py::tuple([x.val(), Val::Int(0), Val::Int(0)])])
}

/// One interchangeable strip; the finger face prints upward without supports.
pub fn cover(rt: &Rt, this: &Val) -> Result<Val> {
    let body = rounded(rt, this.attr("LENGTH")?, this.attr("WIDTH")?, Val::Int(0), this.attr("THICK")?,
        this.attr("CORNER_R")?)?;
    let mut edges = vec![];
    for e in py::method(&body, "Edges", vec![])?.iter()? {
        let zmin = n(&py::method(&e, "BoundingBox", vec![])?, "zmin")?;
        if zmin.sub(n(this, "THICK")?).f().abs() < 1e-06 {
            edges.push(e);
        }
    }
    let body = py::method(&body, "fillet", vec![this.attr("TOUCH_R")?, Val::list(edges)])?;
    let wings = vec![wing(rt, this, Num::I(-1))?, wing(rt, this, Num::I(1))?];
    py::method(&py::method(&body, "fuse", wings)?, "clean", vec![])
}

/// Local X→world Y and Z→world -Z; mirror the east placement for the west.
pub fn placed(_rt: &Rt, this: &Val, shape: &Val, side: &Val, drop: Num) -> Result<Val> {
    let ints = |xyz: [i64; 3]| Val::Tuple(xyz.iter().map(|&c| Val::Int(c)).collect());
    let turned = py::method(shape, "rotate", vec![ints([0, 0, 0]), ints([1, 1, 0]), Val::Int(180)])?;
    let at = py::tuple([this.attr("X_CENTER")?, this.attr("shell")?.attr("handhold_y")?,
        n(this, "BACK")?.sub(drop).val()]);
    let east = py::method(&turned, "translate", vec![at])?;
    let one = interop_eq(side, &Val::Int(1))?;
    if one { Ok(east) } else { py::method(&east, "mirror", vec![py::s("YZ")]) }
}

/// `a == b` as the runtime compares.
fn interop_eq(a: &Val, b: &Val) -> Result<bool> {
    hsm_documents::interop::compare("eq", a.clone(), b.clone())?.truthy()
}

/// `sorted((a, b))` of two numbers: the runtime's stable ascending sort.
fn sorted2(a: Num, b: Num) -> (Num, Num) {
    if b.f() < a.f() { (b, a) } else { (a, b) }
}

/// Clear the two inside R6 shoulders up to the original roof datum.
///
/// The mouth remains on the existing end-wall plane. Only stock below the
/// structural roof is removed. The relief continues through the exterior so
/// the outer corner cannot leave a tapered remnant beside the cover.
pub fn receiver_reliefs(rt: &Rt, this: &Val) -> Result<Vec<Val>> {
    let mut reliefs = vec![];
    let shell = this.attr("shell")?;
    let mouth = n(&shell, "handhold_length")?.div(Num::I(2));
    for end in [-1i64, 1] {
        let end = Num::I(end);
        let corner = n(&this.attr("shell")?, "handhold_corner_r")?;
        let (x0, x1) = sorted2(end.mul(mouth.sub(corner)), end.mul(mouth));
        let back_air = n(this, "BACK_AIR")?;
        let y0 = n(this, "WIDTH")?.neg().div(Num::I(2)).sub(n(this, "BODY_AIR")?);
        let y1 = n(this, "X_EXT")?.sub(n(this, "X_CENTER")?).add(Num::I(1));
        let z1 = n(&this.attr("shell")?, "handhold_corner_r")?.sub(back_air).add(Num::F(0.01));
        reliefs.push(make_box(rt, [x0.val(), x1.val(), y0.val(), y1.val(), back_air.neg().val(), z1.val()])?);
    }
    Ok(reliefs)
}

/// Straight through-slots in the existing 3 mm end walls.
///
/// Their mouths are at Y174/254, with no receiver stock projecting into the
/// handhold. The open rear exits avoid thin pocket backs and give support access.
pub fn receiver_slots(rt: &Rt, this: &Val) -> Result<Vec<Val>> {
    let cq = state(rt)?.cq.clone();
    let mut slots = vec![];
    for end in [-1i64, 1] {
        let end = Num::I(end);
        let shell = this.attr("shell")?;
        let mouth = n(&shell, "handhold_length")?.div(Num::I(2));
        let a = end.mul(n(this, "LENGTH")?.div(Num::I(2)).sub(Num::F(0.1)));
        let b = end.mul(mouth.add(n(&this.attr("shell")?, "handhold_wall")?).add(Num::F(0.1)));
        let (x0, x1) = sorted2(a, b);
        let (span, end_air) = (n(this, "WING_SPAN")?, n(this, "WING_END_AIR")?);
        let y0 = span.neg().div(Num::I(2)).sub(end_air);
        let y1 = span.div(Num::I(2)).add(n(this, "WING_END_AIR")?);
        let roof = n(this, "WING_THICK")?.add(n(this, "BEARING_AIR")?);
        let slot = make_box(rt, [x0.val(), x1.val(), y0.val(), y1.val(), n(this, "BACK_AIR")?.neg().val(), roof.val()])?;
        let plane = py::call_kw(&cq.attr("Workplane")?, vec![py::s("XZ")],
            vec![("origin", py::tuple([Val::Int(0), y1.val(), Val::Int(0)]))])?;
        let section = Val::list(vec![
            py::tuple([end.mul(mouth), roof]),
            py::tuple([end.mul(mouth.add(n(this, "ENTRY_WIDTH")?)), roof]),
            py::tuple([end.mul(mouth), roof.add(n(this, "ENTRY_DEPTH")?)]),
        ]);
        let lead = py::method(&py::method(&plane, "polyline", vec![section])?, "close", vec![])?;
        let lead = py::method(&py::method(&lead, "extrude", vec![y1.sub(y0).val()])?, "val", vec![])?;
        slots.push(py::method(&slot, "fuse", vec![lead])?);
    }
    Ok(slots)
}

/// Apply to either connected bottom half, retaining the existing Y joint.
///
/// Each slot belongs to the end wall in its own half. The reliefs and slots are
/// remote from the seam, its corner stack and the handhold's inner wall.
pub fn apply_receiver(rt: &Rt, this: &Val, solid: Val, piece: &Val) -> Result<Val> {
    let front = matches!(piece, Val::Str(p) if p == "front");
    if !front && !matches!(piece, Val::Str(p) if p == "back") {
        anyhow::bail!("{}", piece.str()?);
    }
    let end_index = if front { 0 } else { 1 };
    let relief = receiver_reliefs(rt, this)?.swap_remove(end_index);
    let slot = receiver_slots(rt, this)?.swap_remove(end_index);
    let mut solid = solid;
    for side in [-1i64, 1] {
        let side = Val::Int(side);
        let cut = py::method(&solid, "cut", vec![placed(rt, this, &relief, &side, Num::I(0))?])?;
        let cut = py::method(&cut, "cut", vec![placed(rt, this, &slot, &side, Num::I(0))?])?;
        solid = py::method(&cut, "clean", vec![])?;
    }
    Ok(solid)
}
