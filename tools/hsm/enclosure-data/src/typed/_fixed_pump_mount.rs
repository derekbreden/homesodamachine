//! Integral pump inverse, roof stock and underside-installed lower retainer.
//!
//! The enclosure module supplies the machine frame and the fitted pump profiles.
//! This module reads its declared Box without realizing another enclosure piece.
//!
//! Typed API: [`datums`], [`snap_datums`], [`wiring_passages`] and [`wing_profile`] compute the
//! retainer's numbers; the solid builders call the enclosure's geometry leaves (`e._ybox`,
//! `e._xz_prism`, ...) and the solids' own methods as Python objects, in Python's order. `e` is
//! the enclosure module and `box` its `Box`, both reached as values.
//!
//! The front-top recipe replaces `inverse_cuts`, `wire_cuts`, `upper_wire_room` and
//! `display_cleanouts`, and the pump-retainer recipe replaces `_wing`, while they record
//! (`_enclosure_front_top._leaves`, `_enclosure_pump_retainer._leaves`): [`fixed_cuts`],
//! [`upper_wire_room`] and [`retainer`] call those five through this module's namespace.
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result, ensure};

pub const TYPED: bool = true;
const MODULE: &str = "_fixed_pump_mount";

const WING_THICK: Num = Num::F(2.0);
const WING_LENGTH: Num = Num::F(22.25);
const ROOT_RADIUS: Num = Num::F(1.5);
const CATCH_OVERLAP: Num = Num::F(2.6);
const CATCH_AIR: Num = Num::F(0.4);
const LEAD_RISE: Num = Num::F(4.6);
const PRY_WIDTH: Num = Num::F(5.0);
const RELAXED_SPREAD: Num = Num::F(0.35);
const SEATED_SPREAD: Num = Num::F(0.10);
const SHARED_HALF_SPAN: Num = Num::F(11.0);
const INTERNAL_WIRE_HALF_SPAN: Num = Num::F(6.0);
const DISPLAY_LINK_HALF_SPAN: Num = Num::F(9.0);
const TUBE_GATE_WIDTH: Num = Num::F(6.35 + 2.0 * 0.25);

const fn f(x: f64) -> Num {
    Num::F(x)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("math", rt.import("math")?)?;
    ns.set("cq", rt.import("cadquery")?)?;
    for (name, value) in [
        ("WING_THICK", WING_THICK),
        ("WING_LENGTH", WING_LENGTH),
        ("ROOT_RADIUS", ROOT_RADIUS),
        ("CATCH_OVERLAP", CATCH_OVERLAP),
        ("CATCH_AIR", CATCH_AIR),
        ("LEAD_RISE", LEAD_RISE),
        ("PRY_WIDTH", PRY_WIDTH),
        ("RELAXED_SPREAD", RELAXED_SPREAD),
        ("SEATED_SPREAD", SEATED_SPREAD),
        ("SHARED_HALF_SPAN", SHARED_HALF_SPAN),
        ("INTERNAL_WIRE_HALF_SPAN", INTERNAL_WIRE_HALF_SPAN),
        ("DISPLAY_LINK_HALF_SPAN", DISPLAY_LINK_HALF_SPAN),
        ("TUBE_GATE_WIDTH", TUBE_GATE_WIDTH),
    ] {
        ns.set(name, value.val())?;
    }
    ns.def(rt, "datums", |_rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        Ok(datums(&e, &box_)?.val())
    })?;
    ns.def(rt, "fasteners", |_rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        fasteners(&e, &box_);
        Ok(py::tuple(Vec::<Val>::new()))
    })?;
    ns.def(rt, "hardware", |_rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        hardware(&e, &box_);
        Ok(py::tuple(Vec::<Val>::new()))
    })?;
    ns.def(rt, "snap_datums", |_rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        Ok(snap_datums(&e, &box_)?.val())
    })?;
    ns.def(rt, "snap_receivers", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["e", "box", "piece"], &[])?;
        let (e, box_, piece) = (b.req("e")?, b.req("box")?, b.req("piece")?);
        snap_receivers(&e, &box_, piece)
    })?;
    ns.def(rt, "stock", |_rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        stock(&e, &box_)
    })?;
    ns.def(rt, "loading_opening", |_rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        loading_opening(&e, &box_)
    })?;
    ns.def(rt, "wiring_passages", |_rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        Ok(wiring_passages(&e, &box_)?.val())
    })?;
    ns.def(rt, "_diamond_y", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["x", "y", "z", "r"], &[])?;
        let mut n = |name: &str| -> Result<Num> { Num::of(&b.req(name)?) };
        let (x, y, z, r) = (n("x")?, n("y")?, n("z")?, n("r")?);
        diamond_y(rt, x, y, z, r)
    })?;
    ns.def(rt, "_corridor_profile", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["vertices"], &[])?;
        let vertices = b.req("vertices")?.iter()?.iter().map(xyz).collect::<Result<Vec<_>>>()?;
        let ((low, high), outline) = corridor_profile(&vertices)?;
        Ok(py::tuple([py::tuple([low.val(), high.val()]), section(&outline)]))
    })?;
    ns.def(rt, "_convex_corridor", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["e", "shapes"], &[])?;
        let (e, shapes) = (b.req("e")?, b.req("shapes")?);
        convex_corridor(&e, &shapes.iter()?)
    })?;
    ns.def(rt, "wire_cuts", |rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        Ok(Val::list(wire_cuts(rt, &e, &box_)?))
    })?;
    ns.def(rt, "inverse_cuts", |rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        Ok(Val::list(inverse_cuts(rt, &e, &box_)?))
    })?;
    ns.def(rt, "upper_wire_room", |rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        upper_wire_room(rt, &e, &box_)
    })?;
    ns.def(rt, "display_cleanouts", |rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        Ok(Val::list(display_cleanouts(rt, &e, &box_)?))
    })?;
    ns.def(rt, "fixed_cuts", |rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        Ok(Val::list(fixed_cuts(rt, &e, &box_)?))
    })?;
    ns.def(rt, "lower_voids", |_rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        Ok(Val::list(lower_voids(&e, &box_)?))
    })?;
    ns.def(rt, "wing_profile", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["e", "box", "side", "spread"], &[])?;
        let (e, box_) = (b.req("e")?, b.req("box")?);
        let (side, spread) = (Num::of(&b.req("side")?)?, Num::of(&b.req("spread")?)?);
        Ok(wing_profile(&e, &box_, side, spread)?.val())
    })?;
    ns.def(rt, "_wing", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["e", "box", "side", "spread"], &[])?;
        let (e, box_) = (b.req("e")?, b.req("box")?);
        let (side, spread) = (Num::of(&b.req("side")?)?, Num::of(&b.req("spread")?)?);
        wing(rt, &e, &box_, side, spread)
    })?;
    ns.def(rt, "retainer", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["e", "box"], &["seated"])?;
        let (e, box_) = (b.req("e")?, b.req("box")?);
        let seated = b.bool_or("seated", false)?;
        retainer(rt, &e, &box_, seated)
    })?;
    ns.def(rt, "figures", |_rt, args, kwargs| {
        let (e, box_) = e_box(args, kwargs)?;
        figures(&e, &box_)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// `(e, box)`: the enclosure module and its Box, as every builder here takes them.
fn e_box(args: py::Args, kwargs: py::Kwargs) -> Result<(Val, Val)> {
    let mut b = py::bind(args, kwargs, &["e", "box"], &[])?;
    Ok((b.req("e")?, b.req("box")?))
}

/// `object.name` as a number.
fn num(object: &Val, name: &str) -> Result<Num> {
    Num::of(&object.attr(name)?)
}

/// `e.name(*args)`: one of the enclosure's functions, read where it is called (the recorders
/// replace its geometry leaves).
fn call(e: &Val, name: &str, args: Vec<Val>) -> Result<Val> {
    py::call(&e.attr(name)?, args)
}

/// A function this module's namespace holds now (another recipe may have replaced it).
fn current(rt: &Rt, name: &str) -> Result<Val> {
    rt.namespace(MODULE)?.get(name)
}

fn vals(values: &[Num]) -> Vec<Val> {
    values.iter().map(|v| v.val()).collect()
}
/// A point tuple.
fn point(values: &[Num]) -> Val {
    Val::Tuple(vals(values))
}
/// A list of `(a, b)` tuples: a prism section or a corridor outline.
fn section(points: &[(Num, Num)]) -> Val {
    Val::list(points.iter().map(|(a, b)| py::tuple([a.val(), b.val()])).collect())
}
/// `sorted((a, b))`.
fn sorted2(a: Num, b: Num) -> (Num, Num) {
    if b.f() < a.f() { (b, a) } else { (a, b) }
}
/// `min(values)`: the first of equal values wins.
fn min_of(values: impl IntoIterator<Item = Num>) -> Result<Num> {
    values.into_iter().reduce(Num::min).context("empty min/max")
}
/// `max(values)`: the first of equal values wins.
fn max_of(values: impl IntoIterator<Item = Num>) -> Result<Num> {
    values.into_iter().reduce(Num::max).context("empty min/max")
}
/// The numbers of a sequence.
fn nums(value: &Val) -> Result<Vec<Num>> {
    value.iter()?.iter().map(Num::of).collect()
}
/// `(p[0], p[1], p[2])` of a point.
fn xyz(value: &Val) -> Result<[Num; 3]> {
    let values = nums(value)?;
    ensure!(values.len() >= 3, "tuple index out of range");
    Ok([values[0], values[1], values[2]])
}
/// `box.pack.pump_trays` as `(cx, cy, cz)` stations.
fn stations(trays: &Val) -> Result<Vec<[Num; 3]>> {
    trays.iter()?.iter().map(Num::three).collect()
}
/// `math.tan(math.radians(degrees))`.
fn tan_degrees(degrees: Num) -> Num {
    f(num::radians(degrees.f()).tan())
}
/// `e.fits.clearance(supported=True)`.
fn supported_clearance(e: &Val) -> Result<Num> {
    let clearance = e.attr("fits")?.attr("clearance")?;
    Num::of(&py::call_kw(&clearance, vec![], vec![("supported", Val::Bool(true))])?)
}

/// The retainer's machine datums, read from the enclosure and its Box.
#[derive(Clone, Copy, Debug)]
pub struct Datums {
    pub flange_z: Num,
    pub bearing_z: Num,
    pub retainer_top_z: Num,
    pub bottom_z: Num,
    pub x0: Num,
    pub x1: Num,
    pub y0: Num,
    pub y1: Num,
    pub head_y: Num,
    pub motor_y: Num,
}
impl Datums {
    /// The dict `datums` returns.
    pub fn val(&self) -> Val {
        py::dict([
            ("flange_z", self.flange_z.val()),
            ("bearing_z", self.bearing_z.val()),
            ("retainer_top_z", self.retainer_top_z.val()),
            ("bottom_z", self.bottom_z.val()),
            ("x0", self.x0.val()),
            ("x1", self.x1.val()),
            ("y0", self.y0.val()),
            ("y1", self.y1.val()),
            ("head_y", self.head_y.val()),
            ("motor_y", self.motor_y.val()),
        ])
    }
}

pub fn datums(e: &Val, box_: &Val) -> Result<Datums> {
    let pack = box_.attr("pack")?;
    let trays = pack.attr("pump_trays")?;
    let stations = stations(&trays)?;
    let flange = min_of(stations.iter().map(|t| t[2]))?.sub(num(&e.attr("_interface")?, "pump_seated_drop")?);
    let grown = num(e, "front_top_flank_t")?.sub(num(e, "wall")?);
    let bearing_z = flange.add(supported_clearance(e)?);
    let running = num(&e.attr("fits")?, "running")?;
    let bottom_z = Num::of(&call(e, "bay_floor_z", vec![trays.clone()])?.get(Val::Int(1))?)?;
    let inner = box_.attr("inner")?;
    let x0 = Num::of(&inner.get(Val::Int(0))?)?.add(grown).add(running);
    let x1 = Num::of(&inner.get(Val::Int(1))?)?.sub(grown).sub(running);
    let y0 = num(e, "front_plane_y")?.add(running);
    let y1 = Num::of(&call(e, "pump_cartridge_aft_y", vec![trays, pack.attr("collet_plate")?])?)?;
    let total = stations.iter().fold(Num::I(0), |sum, t| sum.add(t[1]));
    let count = Num::I(stations.len() as i64);
    Ok(Datums {
        flange_z: flange,
        bearing_z,
        retainer_top_z: flange.sub(running),
        bottom_z,
        x0,
        x1,
        y0,
        y1,
        head_y: total.div(count),
        motor_y: total.div(count).add(num(&e.attr("_tray")?, "rear_axis_y_shift")?),
    })
}

/// The integral snap retainer uses no separate fasteners.
pub fn fasteners(_e: &Val, _box: &Val) {}

pub fn hardware(_e: &Val, _box: &Val) {}

/// The snap's end planes, spring section and receiver surfaces (`snap_datums`).
#[derive(Clone, Copy, Debug)]
pub struct SnapDatums {
    pub carrier_inner_x: Num,
    pub wing_inner_x: Num,
    pub wing_outer_x: Num,
    pub hook_outer_x: Num,
    pub hook_ramp_z: Num,
    pub root_z: Num,
    pub floor_z: Num,
    pub receiver_floor_z: Num,
    pub receiver_inner_x: Num,
    pub receiver_back_x: Num,
    pub receiver_outer_x: Num,
    pub receiver_y0: Num,
    pub receiver_y1: Num,
    pub receiver_z0: Num,
    pub receiver_z1: Num,
    pub receiver_roof_z: Num,
    pub port_inner_x: Num,
    pub port_outer_x: Num,
    pub port_y0: Num,
    pub port_y1: Num,
    pub port_z0: Num,
}
impl SnapDatums {
    /// The dict `snap_datums` returns.
    pub fn val(&self) -> Val {
        py::dict([
            ("carrier_inner_x", self.carrier_inner_x.val()),
            ("wing_inner_x", self.wing_inner_x.val()),
            ("wing_outer_x", self.wing_outer_x.val()),
            ("hook_outer_x", self.hook_outer_x.val()),
            ("hook_ramp_z", self.hook_ramp_z.val()),
            ("root_z", self.root_z.val()),
            ("floor_z", self.floor_z.val()),
            ("receiver_floor_z", self.receiver_floor_z.val()),
            ("receiver_inner_x", self.receiver_inner_x.val()),
            ("receiver_back_x", self.receiver_back_x.val()),
            ("receiver_outer_x", self.receiver_outer_x.val()),
            ("receiver_y0", self.receiver_y0.val()),
            ("receiver_y1", self.receiver_y1.val()),
            ("receiver_z0", self.receiver_z0.val()),
            ("receiver_z1", self.receiver_z1.val()),
            ("receiver_roof_z", self.receiver_roof_z.val()),
            ("port_inner_x", self.port_inner_x.val()),
            ("port_outer_x", self.port_outer_x.val()),
            ("port_y0", self.port_y0.val()),
            ("port_y1", self.port_y1.val()),
            ("port_z0", self.port_z0.val()),
        ])
    }
}

/// Common end planes, spring section and receiver bearing/access surfaces.
pub fn snap_datums(e: &Val, box_: &Val) -> Result<SnapDatums> {
    let d = datums(e, box_)?;
    let outer = d.x1;
    let floor = d.bottom_z;
    let cy = d.y0.add(d.y1).div(f(2.));
    let running = num(&e.attr("fits")?, "running")?;
    let edge = outer.add(running);
    let hook = edge.add(CATCH_OVERLAP).sub(SEATED_SPREAD);
    let inward = hook.add(RELAXED_SPREAD).sub(edge).add(f(0.5));
    let box_outer = Num::of(&box_.attr("outer")?.get(Val::Int(1))?)?;
    let wall = num(e, "wall")?;
    Ok(SnapDatums {
        carrier_inner_x: outer.sub(WING_THICK).sub(inward),
        wing_inner_x: outer.sub(WING_THICK),
        wing_outer_x: outer,
        hook_outer_x: hook,
        hook_ramp_z: floor.add(LEAD_RISE),
        root_z: floor.add(WING_LENGTH),
        floor_z: floor,
        receiver_floor_z: floor.sub(CATCH_AIR),
        receiver_inner_x: edge,
        receiver_back_x: hook.add(SEATED_SPREAD),
        receiver_outer_x: box_outer,
        receiver_y0: d.y0.sub(running),
        receiver_y1: d.y1.add(running),
        receiver_z0: num(e, "z_seam")?.add(running),
        receiver_z1: floor.add(WING_LENGTH).add(f(3.).mul(wall)),
        receiver_roof_z: floor.add(LEAD_RISE).add(f(2.).mul(running)),
        port_inner_x: outer.add(running),
        port_outer_x: box_outer.sub(wall),
        port_y0: cy.sub(PRY_WIDTH.div(f(2.))),
        port_y1: cy.add(PRY_WIDTH.div(f(2.))),
        port_z0: floor.sub(f(5.)),
    })
}

/// One plain full-span pocket per flank, with a central tool opening and 45° roof.
pub fn snap_receivers(e: &Val, box_: &Val, piece: Val) -> Result<Val> {
    let d = snap_datums(e, box_)?;
    let outer = box_.attr("outer")?;
    let mut piece = piece;
    for side in [f(-1.), f(1.)] {
        let (x0, x1) = sorted2(side.mul(d.receiver_inner_x), side.mul(d.receiver_outer_x.add(f(0.5))));
        let band = call(e, "_ybox", vals(&[x0, x1, d.receiver_y0, d.receiver_y1, d.receiver_z0, d.receiver_z1]))?;
        let rounded = call(e, "_rounded_outer", vec![outer.clone()])?;
        let stock = py::method(&band, "intersect", vec![rounded])?;
        let reach = d.receiver_back_x.sub(d.receiver_inner_x);
        let pocket = call(e, "_xz_prism", vec![d.receiver_y0.val(), d.receiver_y1.val(), section(&[
            (side.mul(d.receiver_inner_x), d.receiver_floor_z),
            (side.mul(d.receiver_back_x), d.receiver_floor_z),
            (side.mul(d.receiver_back_x), d.receiver_roof_z),
            (side.mul(d.receiver_inner_x), d.receiver_roof_z.add(reach)),
        ])])?;
        let (x0, x1) = sorted2(side.mul(d.port_inner_x), side.mul(d.port_outer_x));
        let port = call(e, "_ybox", vals(&[x0, x1, d.port_y0, d.port_y1, d.port_z0, d.receiver_roof_z]))?;
        let roof_drop = d.port_outer_x.sub(d.receiver_back_x);
        let corbel = call(e, "_xz_prism", vec![d.port_y0.val(), d.port_y1.val(), section(&[
            (side.mul(d.receiver_back_x), d.receiver_roof_z),
            (side.mul(d.port_outer_x), d.receiver_roof_z),
            (side.mul(d.port_outer_x), d.receiver_roof_z.sub(roof_drop)),
        ])])?;
        let receiver = py::method(&stock, "cut", vec![pocket])?;
        let receiver = py::method(&receiver, "cut", vec![port])?;
        let receiver = py::method(&receiver, "fuse", vec![corbel])?;
        let receiver = py::method(&receiver, "clean", vec![])?;
        piece = py::method(&py::method(&piece, "cut", vec![band])?, "fuse", vec![receiver])?;
    }
    py::method(&piece, "clean", vec![])
}

/// Broad stock continues to the existing outer roof and display housing.
pub fn stock(e: &Val, box_: &Val) -> Result<Val> {
    let d = datums(e, box_)?;
    let inner = box_.attr("inner")?;
    let outer = box_.attr("outer")?;
    let west = Num::of(&inner.get(Val::Int(0))?)?.sub(f(1.));
    let east = Num::of(&inner.get(Val::Int(1))?)?.add(f(1.));
    let fore = num(e, "front_plane_y")?.sub(f(1.));
    let back = call(e, "housing_back_y", vec![outer.clone()])?;
    let top = Num::of(&outer.get(Val::Int(5))?)?.add(f(1.));
    let slab = call(e, "_ybox", vec![west.val(), east.val(), fore.val(), back, d.bearing_z.val(), top.val()])?;
    let rounded = call(e, "_rounded_outer", vec![outer])?;
    py::method(&slab, "intersect", vec![rounded])
}

pub fn loading_opening(e: &Val, box_: &Val) -> Result<Val> {
    let d = datums(e, box_)?;
    let running = num(&e.attr("fits")?, "running")?;
    let back = call(e, "bay_back_y", vec![box_.attr("pack")?.attr("collet_plate")?])?;
    let floor = num(e, "z_seam")?.sub(f(20.));
    call(e, "_ybox", vec![
        d.x0.sub(running).val(),
        d.x1.add(running).val(),
        d.y0.sub(running).val(),
        back,
        floor.val(),
        d.bearing_z.val(),
    ])
}

/// The named nominal cable passages (`wiring_passages`).
#[derive(Clone, Debug)]
pub struct Passages {
    /// `front-top-electrical` points: rear, then fore.
    pub electrical: [[Num; 3]; 2],
    /// `front-top-pump-cross` points: the outermost pumps' X either side of the centre.
    pub cross: [[Num; 3]; 3],
    /// `front-top-pump-cross` floor.
    pub cross_floor_z: Num,
    /// `front-top-display-chimney` points and bounds.
    pub chimney: [[Num; 3]; 2],
    pub chimney_bounds: [Num; 6],
    /// `front-top-display-link` points: the link start, then the chimney head.
    pub link: Vec<Num>,
    pub link_end: [Num; 3],
    pub terminal_entry: Vec<Num>,
}
impl Passages {
    /// The dict `wiring_passages` returns.
    pub fn val(&self) -> Val {
        let points = |rows: &[[Num; 3]]| Val::list(rows.iter().map(|p| point(p)).collect());
        py::dict([
            ("front-top-electrical", py::dict([
                ("points_mm", points(&self.electrical)),
                ("diamond_half_span_mm", SHARED_HALF_SPAN.val()),
            ])),
            ("front-top-pump-cross", py::dict([
                ("points_mm", points(&self.cross)),
                ("roof_half_span_mm", INTERNAL_WIRE_HALF_SPAN.val()),
                ("floor_z_mm", self.cross_floor_z.val()),
            ])),
            ("front-top-display-chimney", py::dict([
                ("points_mm", points(&self.chimney)),
                ("bounds_mm", Val::list(vals(&self.chimney_bounds))),
            ])),
            ("front-top-display-link", py::dict([
                ("points_mm", Val::list(vec![point(&self.link), point(&self.link_end)])),
                ("terminal_entry_mm", point(&self.terminal_entry)),
                ("diamond_half_span_mm", DISPLAY_LINK_HALF_SPAN.val()),
            ])),
        ])
    }
}

/// Named nominal cable passages consumed by installed wiring and CAD.
pub fn wiring_passages(e: &Val, box_: &Val) -> Result<Passages> {
    let d = datums(e, box_)?;
    let cy = d.motor_y;
    // The exit and cross passage follow the seated motors rather than a lintel.
    let motor_end = d.flange_z.add(num(&e.attr("_tray")?, "motor_crown")?);
    let rear_z = motor_end.add(f(2.776));
    let cross_z = rear_z.add(f(4.));
    let pack = box_.attr("pack")?;
    let rear_y = Num::of(&py::at(&pack.attr("collet_plate")?, "wall_aft_y")?)?.add(f(0.664));
    let outer = box_.attr("outer")?;
    let reach = num(e, "display_facet_thickness")?.add(num(e, "display_pcb_cut_through")?).sub(f(1.)).neg();
    let back = nums(&call(e, "_display_point", vec![outer.clone(), point(&[f(0.5), f(-1.), reach])])?)?;
    let normal = nums(&call(e, "_facet_geom", vec![outer])?.get(Val::Int(1))?)?;
    let link = back.iter().zip(&normal).map(|(p, n)| p.sub(n.mul(f(6.)))).collect();
    let stations = stations(&pack.attr("pump_trays")?)?;
    let west = min_of(stations.iter().map(|t| t[0]))?;
    let east = max_of(stations.iter().map(|t| t[0]))?;
    let floor = motor_end.sub(num(e, "wall")?);
    let terminal_entry = back.iter().zip(&normal).map(|(p, n)| p.add(n.mul(f(2.)))).collect();
    Ok(Passages {
        electrical: [[f(0.), rear_y, rear_z], [f(0.), cy, rear_z]],
        cross: [[west, cy, cross_z], [f(0.), cy, cross_z], [east, cy, cross_z]],
        cross_floor_z: floor,
        chimney: [[f(0.), f(79.), cross_z], [f(0.), f(78.), f(321.)]],
        chimney_bounds: [f(-10.), f(10.), f(72.), f(84.), rear_z, f(334.)],
        link,
        link_end: [f(0.), f(78.), f(321.)],
        terminal_entry,
    })
}

/// A Y-normal diamond wire of half span `r` about `(x, y, z)`.
pub fn diamond_y(rt: &Rt, x: Num, y: Num, z: Num, r: Num) -> Result<Val> {
    let cq = rt.import("cadquery")?;
    let make_polygon = cq.attr("Wire")?.attr("makePolygon")?;
    let vector = cq.attr("Vector")?;
    let corners = vec![
        py::call(&vector, vals(&[x.sub(r), y, z]))?,
        py::call(&vector, vals(&[x, y, z.add(r)]))?,
        py::call(&vector, vals(&[x.add(r), y, z]))?,
        py::call(&vector, vals(&[x, y, z.sub(r)]))?,
    ];
    py::call_kw(&make_polygon, vec![Val::list(corners)], vec![("close", Val::Bool(true))])
}

/// `_diamond_y(*centre, r)`.
fn diamond_at(rt: &Rt, centre: &[Num], r: Num) -> Result<Val> {
    ensure!(centre.len() == 3, "_diamond_y takes a three-coordinate centre, not {}", centre.len());
    diamond_y(rt, centre[0], centre[1], centre[2], r)
}

/// `turn(a, b, c)`: the cross product's sign tells a left from a right turn.
fn turn(a: (Num, Num), b: (Num, Num), c: (Num, Num)) -> f64 {
    (b.0.f() - a.0.f()) * (c.1.f() - a.1.f()) - (b.1.f() - a.1.f()) * (c.0.f() - a.0.f())
}

/// `chain(sequence)`: one monotone hull chain.
fn chain(sequence: impl IntoIterator<Item = (Num, Num)>) -> Vec<(Num, Num)> {
    let mut result: Vec<(Num, Num)> = vec![];
    for point in sequence {
        while result.len() > 1 && turn(result[result.len() - 2], result[result.len() - 1], point) <= 1e-9 {
            result.pop();
        }
        result.push(point);
    }
    result
}

/// The straight-sided cable room's X span and convex Y/Z outline.
pub fn corridor_profile(vertices: &[[Num; 3]]) -> Result<((Num, Num), Vec<(Num, Num)>)> {
    // `sorted(set(...))`: the set keeps each value's first occurrence; the sort is stable.
    let mut points: Vec<(Num, Num)> = vec![];
    for p in vertices {
        let yz = (p[1], p[2]);
        if !points.iter().any(|q| q.0.f() == yz.0.f() && q.1.f() == yz.1.f()) {
            points.push(yz);
        }
    }
    points.sort_by(|a, b| match a.0.f().partial_cmp(&b.0.f()) {
        Some(std::cmp::Ordering::Equal) => a.1.f().partial_cmp(&b.1.f()).unwrap_or(std::cmp::Ordering::Equal),
        Some(order) => order,
        None => std::cmp::Ordering::Equal,
    });
    let mut outline = chain(points.iter().copied());
    outline.pop();
    let mut back = chain(points.iter().rev().copied());
    back.pop();
    outline.extend(back);
    let span = (min_of(vertices.iter().map(|p| p[0]))?, max_of(vertices.iter().map(|p| p[0]))?);
    Ok((span, outline))
}

/// One straight-sided display cable room containing its entry and chimney.
pub fn convex_corridor(e: &Val, shapes: &[Val]) -> Result<Val> {
    let mut vertices = vec![];
    for shape in shapes {
        for vertex in py::method(shape, "Vertices", vec![])?.iter()? {
            vertices.push(xyz(&py::method(&py::method(&vertex, "Center", vec![])?, "toTuple", vec![])?)?);
        }
    }
    let ((low, high), outline) = corridor_profile(&vertices)?;
    call(e, "_yz_prism", vec![low.val(), high.val(), section(&outline)])
}

pub fn wire_cuts(rt: &Rt, e: &Val, box_: &Val) -> Result<Vec<Val>> {
    let cq = rt.import("cadquery")?;
    let p = wiring_passages(e, box_)?;
    let [rear, fore] = p.electrical;
    let r = SHARED_HALF_SPAN;
    let make_loft = cq.attr("Solid")?.attr("makeLoft")?;
    let sections = Val::list(vec![
        diamond_y(rt, f(0.), fore[1], rear[2], r)?,
        diamond_y(rt, f(0.), rear[1], rear[2], r)?,
    ]);
    let mut out = vec![py::call(&make_loft, vec![sections, Val::Bool(true)])?];
    // The rear upper half opens through the bulkhead top; the forward roof
    // and the lower half retain the printable diamond section.
    let back = call(e, "housing_back_y", vec![box_.attr("outer")?])?;
    let bay_top = Num::of(&box_.attr("pump_bay")?.get(Val::Int(2))?)?.add(f(0.01));
    out.push(call(e, "_ybox", vec![r.neg().val(), r.val(), back, rear[1].val(), rear[2].val(), bay_top.val()])?);
    let [a, _mid, b] = p.cross;
    let r = INTERNAL_WIRE_HALF_SPAN;
    let floor = p.cross_floor_z;
    // A single level floor joins both motor rooms and the shared outlet. It
    // cannot leave a skin between two opposed diamond/cone faces.
    out.push(call(e, "_yz_prism", vec![a[0].val(), b[0].val(), section(&[
        (a[1].sub(r), floor),
        (a[1].add(r), floor),
        (a[1].add(r), a[2]),
        (a[1], a[2].add(r)),
        (a[1].sub(r), a[2]),
    ])])?);
    let chimney = call(e, "_ybox", vals(&p.chimney_bounds))?;
    let r = DISPLAY_LINK_HALF_SPAN;
    let plane = call(e, "display_plane", vec![box_.attr("outer")?])?;
    let first = diamond_at(rt, &p.terminal_entry, r)?;
    let inner = diamond_at(rt, &p.link, r)?;
    // A single rectangular pocket-normal connection contains the complete
    // entry envelope and joins the diamond run to the chimney.
    let mut points: Vec<Vec<Num>> = vec![];
    for section in [&first, &inner] {
        for vertex in py::method(section, "Vertices", vec![])?.iter()? {
            let local = py::method(&plane, "toLocalCoords", vec![py::method(&vertex, "Center", vec![])?])?;
            points.push(nums(&py::method(&local, "toTuple", vec![])?)?);
        }
    }
    let mut bounds = vec![];
    for axis in 0..3 {
        let along = |point: &Vec<Num>| point.get(axis).copied().context("tuple index out of range");
        bounds.push(min_of(points.iter().map(along).collect::<Result<Vec<_>>>()?)?.sub(f(1.)));
        bounds.push(max_of(points.iter().map(along).collect::<Result<Vec<_>>>()?)?.add(f(1.)));
    }
    let entry = call(e, "_ybox", vals(&bounds))?;
    let place = py::call(&cq.attr("Location")?, vec![plane])?;
    let entry = py::method(&entry, "moved", vec![place])?;
    // The entry, rising link and chimney share one convex room. Its plain
    // walls replace the thin banks between overlapping passage cuts.
    let head = diamond_at(rt, &p.link_end, r)?;
    out.push(convex_corridor(e, &[entry, inner, head, chimney])?);
    Ok(out)
}

/// The boss and motor inverse, with printable terminal-room roofs.
pub fn inverse_cuts(rt: &Rt, e: &Val, box_: &Val) -> Result<Vec<Val>> {
    let cq = rt.import("cadquery")?;
    let mut out = vec![];
    for [cx, cy, cz] in stations(&box_.attr("pack")?.attr("pump_trays")?)? {
        let tray = e.attr("_tray")?;
        let flange = cz.sub(num(&e.attr("_interface")?, "pump_seated_drop")?);
        let y = cy.add(num(&tray, "rear_axis_y_shift")?);
        let finish = supported_clearance(e)?;
        let room = py::call(&tray.attr("boss_room")?, vec![e.attr("cap_boss_air")?])?;
        // The supported boss shoulder has its own axial face allowance.
        let lifted = py::method(&room, "translate", vec![point(&[f(0.), f(0.), finish])])?;
        let room = py::method(&room, "fuse", vec![lifted])?;
        out.push(py::method(&room, "translate", vec![point(&[cx, y, flange])])?);
        let motor_end = flange.add(num(&tray, "motor_crown")?);
        let terminal_r = Num::of(&call(e, "cap_terminal_crown_r", vec![box_.clone()])?)?;
        let start = motor_end.sub(num(e, "wall")?);
        let can_half = num(&tray, "can_half")?;
        let can_floor = flange.add(num(&tray, "boss_depth")?).add(finish).sub(f(0.01));
        out.push(call(e, "_zcyl", vals(&[can_half, cx, y, can_floor, start.add(f(0.01))]))?);
        // The terminal room expands above the can and closes directly at the
        // saved printable roof angle, leaving full stock below the display seat.
        let rise = terminal_r.sub(can_half);
        let make_cone = cq.attr("Solid")?.attr("makeCone")?;
        let vector = cq.attr("Vector")?;
        let up = || py::call(&vector, vec![Val::Int(0), Val::Int(0), Val::Int(1)]);
        let base = py::call(&vector, vals(&[cx, y, start]))?;
        out.push(py::call(&make_cone, vec![can_half.val(), terminal_r.val(), rise.val(), base, up()?])?);
        let roof_rise = terminal_r.mul(tan_degrees(num(e, "teardrop_roof_angle")?));
        let base = py::call(&vector, vals(&[cx, y, start.add(rise)]))?;
        out.push(py::call(&make_cone, vec![terminal_r.val(), f(0.).val(), roof_rise.val(), base, up()?])?);
    }
    Ok(out)
}

/// One open motor/display room, with the fitted bearing and wing pockets retained.
pub fn upper_wire_room(rt: &Rt, e: &Val, box_: &Val) -> Result<Val> {
    let cq = rt.import("cadquery")?;
    let d = datums(e, box_)?;
    let radius = Num::of(&call(e, "cap_terminal_crown_r", vec![box_.clone()])?)?;
    let tray = e.attr("_tray")?;
    let base = d.flange_z.add(num(&tray, "motor_crown")?).sub(num(e, "wall")?).add(radius).sub(num(&tray, "can_half")?);
    let peak = base.add(radius.mul(tan_degrees(num(e, "teardrop_roof_angle")?)));
    let (offset_x, pcb_x) = (num(e, "display_body_offset_x")?, num(e, "display_pcb_x")?);
    let x0 = offset_x.sub(pcb_x.div(f(2.)));
    let x1 = offset_x.add(pcb_x.div(f(2.)));
    let motor = call(e, "_yz_prism", vec![x0.val(), x1.val(), section(&[
        (d.motor_y.sub(radius), base),
        (d.motor_y.add(radius), base),
        (d.motor_y, peak),
    ])])?;
    let depth = num(e, "display_facet_thickness")?.add(num(e, "display_pcb_cut_through")?);
    let (offset_slope, pcb_slope) = (num(e, "display_body_offset_slope")?, num(e, "display_pcb_slope")?);
    let pcb = call(e, "_ybox", vec![
        x0.val(),
        x1.val(),
        offset_slope.sub(pcb_slope.div(f(2.))).val(),
        offset_slope.add(pcb_slope.div(f(2.))).val(),
        depth.neg().val(),
        e.attr("_display_wings")?.attr("GLASS_SEAT")?,
    ])?;
    let plane = call(e, "display_plane", vec![box_.attr("outer")?])?;
    let pcb = py::method(&pcb, "moved", vec![py::call(&cq.attr("Location")?, vec![plane])?])?;
    let mut shapes = vec![motor, pcb];
    shapes.extend(py::call(&current(rt, "wire_cuts")?, vec![e.clone(), box_.clone()])?.iter()?.into_iter().skip(2));
    convex_corridor(e, &shapes)
}

/// Two plain wing-support access branches open into the empty PCB room.
pub fn display_cleanouts(rt: &Rt, e: &Val, box_: &Val) -> Result<Vec<Val>> {
    let cq = rt.import("cadquery")?;
    let wings = e.attr("_display_wings")?;
    let reach = num(&wings, "COVER_X")?.div(f(2.)).add(num(&wings, "WING_REACH")?).add(num(&wings, "TIP_AIR")?);
    let depth = Num::of(&call(e, "_display_cut_exit_depth", vec![])?)?;
    let roof = num(&wings, "GLASS_SEAT")?.sub(num(e, "wall")?);
    let floor = num(&wings, "BACK")?.add(num(&wings, "WING_THICK")?).add(num(&wings, "BEARING_AIR")?).sub(depth);
    let span = num(&wings, "WING_SPAN")?;
    let end_air = num(&wings, "END_AIR")?;
    let y0 = span.neg().div(f(2.)).sub(end_air).sub(depth.mul(tan_degrees(num(&wings, "ANGLE")?)));
    let y1 = span.div(f(2.)).add(end_air);
    let (offset_x, pcb_x) = (num(e, "display_body_offset_x")?, num(e, "display_pcb_x")?);
    let pcb0 = offset_x.sub(pcb_x.div(f(2.)));
    let pcb1 = offset_x.add(pcb_x.div(f(2.)));
    let place = py::call(&cq.attr("Location")?, vec![call(e, "display_plane", vec![box_.attr("outer")?])?])?;
    let mut out = vec![];
    for (x0, x1) in [(reach.neg(), pcb0.add(f(0.01))), (pcb1.sub(f(0.01)), reach)] {
        let branch = call(e, "_ybox", vals(&[x0, x1, y0, y1, floor, roof]))?;
        out.push(py::method(&branch, "moved", vec![place.clone()])?);
    }
    Ok(out)
}

pub fn fixed_cuts(rt: &Rt, e: &Val, box_: &Val) -> Result<Vec<Val>> {
    let args = || vec![e.clone(), box_.clone()];
    let mut out = vec![loading_opening(e, box_)?];
    out.extend(py::call(&current(rt, "inverse_cuts")?, args())?.iter()?);
    out.extend(py::call(&current(rt, "wire_cuts")?, args())?.iter()?);
    out.push(py::call(&current(rt, "upper_wire_room")?, args())?);
    out.extend(py::call(&current(rt, "display_cleanouts")?, args())?.iter()?);
    let plate = box_.attr("pack")?.attr("collet_plate")?;
    let half = TUBE_GATE_WIDTH.div(f(2.));
    for hole in py::at(&plate, "holes")?.iter()? {
        let hole = py::unpack(&hole, 2)?;
        let (x, z) = (Num::of(&hole[0])?, Num::of(&hole[1])?);
        let fore = Num::of(&py::at(&plate, "fore_y")?)?.sub(f(0.01));
        let aft = Num::of(&py::at(&plate, "wall_aft_y")?)?.add(f(0.01));
        let floor = num(e, "z_seam")?.sub(f(20.));
        out.push(call(e, "_ybox", vals(&[x.sub(half), x.add(half), fore, aft, floor, z.add(f(0.01))]))?);
    }
    Ok(out)
}

pub fn lower_voids(e: &Val, box_: &Val) -> Result<Vec<Val>> {
    let pack = box_.attr("pack")?;
    let (trays, _plate) = (pack.attr("pump_trays")?, pack.attr("collet_plate")?);
    let d = datums(e, box_)?;
    let source = call(e, "_pump_lower_well", vec![trays.clone()])?;
    let tray = e.attr("_tray")?;
    let pc = tray.attr("_pc")?;
    let pump_air = e.attr("cap_pump_air")?;
    let wall_offset = num(&pc, "skirt_wall")?.sub(Num::of(&pump_air)?);
    let upper_half = num(&pc, "skirt_base_half_extent")?.sub(wall_offset);
    let corner_r = num(&pc, "corner_r")?.sub(wall_offset);
    let support = call(e, "pump_skirt_support_z", vec![trays.clone()])?;
    let mut out = vec![];
    for [cx, cy, cz] in stations(&trays)? {
        let mut body = py::method(&source, "translate", vec![point(&[cx, cy, cz])])?;
        for sx in [f(-1.), f(1.)] {
            let x = cx.add(sx.mul(num(&tray, "outlet_pitch")?).div(f(2.)));
            let z = cz.add(num(&tray, "outlet_axis_z")?);
            let y0 = cy.add(Num::of(&py::call(&tray.attr("outlet_passage_start_y")?, vec![pump_air.clone()])?)?);
            let half = num(e, "cap_fitting_half")?;
            let tube = call(e, "_ycyl", vals(&[half, x, z, y0, d.y1.add(f(1.))]))?;
            let slot = call(e, "_ybox", vals(&[x.sub(half), x.add(half), y0, d.y1.add(f(1.)), z, d.retainer_top_z.add(f(1.))]))?;
            body = py::method(&body, "fuse", vec![tube, slot])?;
        }
        for wedge in call(e, "_outlet_under_tangent_wedges", vals(&[cx, cy, cz]))?.iter()? {
            body = py::method(&body, "fuse", vec![wedge])?;
        }
        for wedge in call(e, "_outlet_fore_miter_wedges", vals(&[cx, cy, cz]))?.iter()? {
            body = py::method(&body, "cut", vec![wedge])?;
        }
        // One square fore mouth per well reaches the corner tangency above
        // the fitted skirt land; the complete bearing section below stays solid.
        let mouth = call(e, "_ybox", vec![
            cx.sub(upper_half).val(),
            cx.add(upper_half).val(),
            d.y0.sub(f(1.)).val(),
            cy.sub(upper_half).add(corner_r).add(f(0.01)).val(),
            support.clone(),
            d.retainer_top_z.add(f(1.)).val(),
        ])?;
        body = py::method(&body, "fuse", vec![mouth])?;
        out.push(body);
    }
    Ok(out)
}

/// A profile point `(x, z)`.
type P = (Num, Num);

/// One edge of the wing profile.
#[derive(Clone, Copy, Debug)]
pub enum Segment {
    Line([P; 2]),
    Cubic([P; 4]),
}

/// The wing's profile (`wing_profile`): its Y extrusion interval and edges.
#[derive(Clone, Debug)]
pub struct WingProfile {
    pub span: (Num, Num),
    pub segments: Vec<Segment>,
}
impl WingProfile {
    /// The dict `wing_profile` returns.
    pub fn val(&self) -> Val {
        let pair = |p: &P| py::tuple([p.0.val(), p.1.val()]);
        let segments = self.segments.iter().map(|segment| match segment {
            Segment::Line(points) => py::dict([("line", Val::Tuple(points.iter().map(pair).collect()))]),
            Segment::Cubic(points) => py::dict([("cubic", Val::Tuple(points.iter().map(pair).collect()))]),
        });
        py::dict([
            ("span", py::tuple([self.span.0.val(), self.span.1.val()])),
            ("segments", Val::list(segments.collect())),
        ])
    }
}

/// The native wing's line/cubic controls and its extrusion interval.
pub fn wing_profile(e: &Val, box_: &Val, side: Num, spread: Num) -> Result<WingProfile> {
    let (d, s) = (datums(e, box_)?, snap_datums(e, box_)?);
    let points: [P; 5] = [
        (s.wing_inner_x, s.floor_z),
        (s.hook_outer_x, s.floor_z),
        (s.wing_outer_x, s.hook_ramp_z),
        (s.wing_outer_x, s.root_z),
        (s.wing_inner_x.sub(ROOT_RADIUS), s.root_z),
    ];
    let length = s.root_z.sub(s.floor_z);
    let deflection = |z: Num| -> Num {
        let t = s.root_z.sub(z).div(length);
        spread.mul(t).mul(t).mul(f(3.).sub(t)).div(f(2.))
    };
    let slope = |z: Num| -> Num {
        let t = s.root_z.sub(z).div(length);
        spread.neg().mul(f(3.).mul(t).sub(f(1.5).mul(t).mul(t))).div(length)
    };
    let mut segments = vec![];
    for (&(xa, za), &(xb, zb)) in points.iter().zip(&points[1..]) {
        let pa = (side.mul(xa.add(deflection(za))), za);
        let pb = (side.mul(xb.add(deflection(zb))), zb);
        if zb.sub(za).f().abs() < 1e-9 || xb.sub(xa).f().abs() > 1e-9 || spread.f() == 0. {
            segments.push(Segment::Line([pa, pb]));
        } else {
            let da = (side.mul(xb.sub(xa).add(slope(za).mul(zb.sub(za)))), zb.sub(za));
            let db = (side.mul(xb.sub(xa).add(slope(zb).mul(zb.sub(za)))), zb.sub(za));
            let third = f(1.0).div(f(3.0));
            segments.push(Segment::Cubic([
                pa,
                (pa.0.add(da.0.mul(third)), pa.1.add(da.1.mul(third))),
                (pb.0.sub(db.0.mul(third)), pb.1.sub(db.1.mul(third))),
                pb,
            ]));
        }
    }
    // The inside root is a tangent quarter round. The same cubic controls go
    // to the native and numerical builders, including their illustrated pose.
    let k = f(4.).div(f(3.)).mul(f((std::f64::consts::PI / 8.).tan())).mul(ROOT_RADIUS);
    let a = points[4];
    let b = (s.wing_inner_x, s.root_z.sub(ROOT_RADIUS));
    let controls = [a, (a.0.add(k), a.1), (b.0, b.1.add(k)), b];
    segments.push(Segment::Cubic(controls.map(|(x, z)| (side.mul(x.add(deflection(z))), z))));
    let (a, b) = (b, points[0]);
    let (pa, pb) = ((side.mul(a.0.add(deflection(a.1))), a.1), (side.mul(b.0.add(deflection(b.1))), b.1));
    let dz = b.1.sub(a.1);
    segments.push(Segment::Cubic([
        pa,
        (pa.0.add(side.mul(slope(a.1)).mul(dz).div(f(3.))), a.1.add(dz.div(f(3.)))),
        (pb.0.sub(side.mul(slope(b.1)).mul(dz).div(f(3.))), b.1.sub(dz.div(f(3.)))),
        pb,
    ]));
    Ok(WingProfile { span: (d.y0, d.y1), segments })
}

/// A single extruded profile; cubic sides have zero slope at the upper root.
///
/// The standalone part carries the relaxed section. Assemblies carry the seated
/// section. This is a geometric pose, not a computed elastic response.
pub fn wing(rt: &Rt, e: &Val, box_: &Val, side: Num, spread: Num) -> Result<Val> {
    let cq = rt.import("cadquery")?;
    let profile = wing_profile(e, box_, side, spread)?;
    let (y0, y1) = profile.span;
    let vector = |p: &P| -> Result<Val> { py::call(&cq.attr("Vector")?, vec![p.0.val(), y0.val(), p.1.val()]) };
    let mut edges = vec![];
    for segment in &profile.segments {
        edges.push(match segment {
            Segment::Line([a, b]) => {
                let make_line = cq.attr("Edge")?.attr("makeLine")?;
                py::call(&make_line, vec![vector(a)?, vector(b)?])?
            }
            Segment::Cubic(points) => {
                let make_bezier = cq.attr("Edge")?.attr("makeBezier")?;
                py::call(&make_bezier, vec![Val::list(points.iter().map(vector).collect::<Result<_>>()?)])?
            }
        });
    }
    let wire = py::call(&cq.attr("Wire")?.attr("assembleEdges")?, vec![Val::list(edges)])?;
    let extrude = cq.attr("Solid")?.attr("extrudeLinear")?;
    let direction = py::call(&cq.attr("Vector")?, vals(&[f(0.), y1.sub(y0), f(0.)]))?;
    py::call(&extrude, vec![wire, Val::list(vec![]), direction])
}

/// Full-span upper roots and lower hooks, with the fitted pump wells retained.
pub fn retainer(rt: &Rt, e: &Val, box_: &Val, seated: bool) -> Result<Val> {
    let (d, s) = (datums(e, box_)?, snap_datums(e, box_)?);
    let mut body = call(e, "_xz_prism", vec![d.y0.val(), d.y1.val(), section(&[
        (d.x0, d.retainer_top_z),
        (d.x1, d.retainer_top_z),
        (d.x1, s.root_z),
        (s.carrier_inner_x, s.root_z),
        (s.carrier_inner_x, d.bottom_z),
        (s.carrier_inner_x.neg(), d.bottom_z),
        (s.carrier_inner_x.neg(), s.root_z),
        (d.x0, s.root_z),
    ])])?;
    for cutter in lower_voids(e, box_)? {
        body = py::method(&body, "cut", vec![cutter])?;
    }
    let spread = if seated { SEATED_SPREAD } else { RELAXED_SPREAD };
    let mut wings = vec![];
    for side in [f(-1.), f(1.)] {
        wings.push(py::call(&current(rt, "_wing")?, vec![e.clone(), box_.clone(), side.val(), spread.val()])?);
    }
    let body = py::method(&body, "fuse", wings)?;
    call(e, "_unified", vec![body])
}

pub fn figures(e: &Val, box_: &Val) -> Result<Val> {
    let bay = box_.attr("pump_bay")?;
    let placed = if bay.truthy()? { box_.attr("pack")?.attr("pump_trays")?.truthy()? } else { false };
    if !placed {
        return Ok(Val::dict(vec![]));
    }
    let d = datums(e, box_)?;
    let s = snap_datums(e, box_)?;
    let mm6 = |value: Num| format!("{} mm", value.fmt(".6g"));
    let mm = |value: Num| format!("{} mm", value.fmt("g"));
    let tray = e.attr("_tray")?;
    let skirt_support = Num::of(&call(e, "pump_skirt_support_z", vec![box_.attr("pack")?.attr("pump_trays")?])?)?;
    let rows: Vec<(&str, String)> = vec![
        ("PUMP_RETAINER_W", mm6(d.x1.sub(d.x0))),
        ("PUMP_RETAINER_D", mm6(d.y1.sub(d.y0))),
        ("PUMP_RETAINER_H", mm6(d.retainer_top_z.sub(d.bottom_z))),
        ("PUMP_RETAINER_BOTTOM_Z", mm6(d.bottom_z)),
        ("PUMP_RETAINER_TOP_Z", mm6(d.retainer_top_z)),
        ("PUMP_FLANGE_Z", mm6(d.flange_z)),
        ("PUMP_FIXED_BEARING_Z", mm6(d.bearing_z)),
        ("PUMP_SKIRT_SUPPORT_Z", mm6(skirt_support)),
        ("PUMP_RETAINER_SCREW_COUNT", "0".to_owned()),
        ("PUMP_SNAP_ROOT_Z", mm6(s.root_z)),
        ("PUMP_SNAP_WING_THICK", mm(WING_THICK)),
        ("PUMP_SNAP_LENGTH", mm(WING_LENGTH)),
        ("PUMP_SNAP_RECEIVER_FLOOR_Z", mm6(s.receiver_floor_z)),
        ("PUMP_SNAP_PORT_WIDTH", mm(s.port_y1.sub(s.port_y0))),
        ("CAP_TUBE_OPEN", mm(Num::I(2).mul(num(e, "cap_fitting_half")?))),
        ("CAP_TUBE_PART", mm(num(&tray, "fitting_w")?)),
        ("CAP_TUBE_PITCH", mm(num(&tray, "outlet_pitch")?)),
        ("PUMP_SEATED_DROP", mm(num(&e.attr("_interface")?, "pump_seated_drop")?)),
        ("PUMP_SKIRT_DEPTH", mm(num(&tray, "skirt_depth")?)),
        ("PLATE_FOOT_X", mm(num(e, "plate_foot_reach")?)),
        ("PLATE_FOOT_Y", mm(num(e, "plate_foot_y")?)),
        ("PLATE_FOOT_T", mm(num(e, "plate_foot_t")?)),
        ("PLATE_FOOT_ANGLE", format!("{}°", num(e, "plate_foot_corbel_angle")?.fmt("g"))),
        ("PUMP_TUBE_GATE_WIDTH", mm(TUBE_GATE_WIDTH)),
        ("PUMP_SHARED_WIRE_SPAN", mm(Num::I(2).mul(SHARED_HALF_SPAN))),
    ];
    Ok(py::dict(rows.into_iter().map(|(key, value)| (key, py::s(value)))))
}
