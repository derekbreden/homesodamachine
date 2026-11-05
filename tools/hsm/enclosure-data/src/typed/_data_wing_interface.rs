//! DATA is the accepted nameplate construction with a narrower, wing-thick face.
//!
//! The centred jack opening is cut through the continuous plate. Broad wings and
//! matching receiving slots use the nameplate geometry and its seating datum.
//! Y=0 is the flat print-bed back; +Y is the customer-facing direction.
//!
//! Typed state: the DATA constants (`_dimensions()['data']`, every one a float), read once at
//! install, with the `data` and `nameplate` mappings as the JSON `_read` sends. `port_chip` and
//! CadQuery stay providers. `Station` is the namedtuple class the generated code makes.
use super::_nameplate_interface::{m, read, rotate_x, update};
use super::_nameplate_wing_interface::{self as wing, ApplyOpts};
use super::num::Num;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::Result;
use serde_json::{Value, json};
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_data_wing_interface";

/// `_dimensions()['data']`: the constants this module computes with.
#[derive(Clone, Copy, Debug)]
pub struct Data {
    pub back_air: f64,
    pub bottom: f64,
    pub center_z: f64,
    pub corner_r: f64,
    pub face_air: f64,
    pub height: f64,
    pub ink_depth: f64,
    pub opening_h: f64,
    pub opening_r: f64,
    pub opening_w: f64,
    pub pocket_depth: f64,
    pub supported_air: f64,
    pub thick: f64,
    pub top: f64,
    pub width: f64,
    pub wing_span: f64,
}

pub struct State {
    pub cq: Val,
    pub port_chip: Val,
    pub data: Data,
    data_json: Value,
    nameplate_json: Value,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("namedtuple", rt.member("collections", "namedtuple")?)?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let nameplate = rt.import("_nameplate_wing_interface")?;
    ns.set("nameplate", nameplate.clone())?;
    let port_chip = rt.import("port_chip")?;
    ns.set("port_chip", port_chip.clone())?;
    let dimensions = rt.member("_enclosure_data", "dimensions")?;
    ns.set("_dimensions", dimensions.clone())?;
    ns.set("_read", rt.member("_enclosure_data", "read")?)?;
    // globals().update(_dimensions()['data'])
    let values = py::snapshot(&py::call(&dimensions, vec![])?)?;
    let data = py::at(&values, "data")?;
    update(ns, &data)?;
    ns.set("box", nameplate.attr("box")?)?;
    let namedtuple = ns.get("namedtuple")?;
    let station = py::call_kw(&namedtuple, vec![py::s("Station"), py::s("x z")],
        vec![("module", py::s(MODULE))])?;
    ns.set("Station", station)?;
    let f = |key: &str| -> Result<f64> { py::at(&data, key)?.num() };
    let constants = Data {
        back_air: f("BACK_AIR")?,
        bottom: f("BOTTOM")?,
        center_z: f("CENTER_Z")?,
        corner_r: f("CORNER_R")?,
        face_air: f("FACE_AIR")?,
        height: f("HEIGHT")?,
        ink_depth: f("INK_DEPTH")?,
        opening_h: f("OPENING_H")?,
        opening_r: f("OPENING_R")?,
        opening_w: f("OPENING_W")?,
        pocket_depth: f("POCKET_DEPTH")?,
        supported_air: f("SUPPORTED_AIR")?,
        thick: f("THICK")?,
        top: f("TOP")?,
        width: f("WIDTH")?,
        wing_span: f("WING_SPAN")?,
    };
    rt.keep(MODULE, State {
        cq,
        port_chip,
        data: constants,
        data_json: py::plain(&data)?,
        nameplate_json: py::plain(&py::at(&values, "nameplate")?)?,
    });

    ns.def(rt, "jack_face_y", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["y_outer"], &[])?;
        let y_outer = Num::of(&b.req("y_outer")?)?;
        Ok(Val::Float(jack_face_y(rt, y_outer)?))
    })?;
    ns.def(rt, "pad_runout", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["station", "y_outer"], &["up"])?;
        let station = b.req("station")?;
        let y_outer = Num::of(&b.req("y_outer")?)?;
        let up = b.opt("up").map(|v| Num::of(&v)).transpose()?.unwrap_or(Num::I(-1));
        let z = Num::of(&station.get(Val::Int(1))?)?;
        let (y, z) = pad_runout(rt, z, y_outer, up)?;
        Ok(py::ftuple(&[y, z]))
    })?;
    ns.def(rt, "aperture", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["y0", "y1"], &[])?;
        let y0 = Num::of(&b.req("y0")?)?;
        let y1 = Num::of(&b.req("y1")?)?;
        aperture(rt, y0, y1)
    })?;
    ns.def(rt, "blank", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        blank(rt)
    })?;
    let supported = Num::F(constants.supported_air);
    ns.def(rt, "apply", move |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["solid", "station", "y_outer"], &["up", "supported"])?;
        let solid = b.req("solid")?;
        let station = b.req("station")?;
        let y_outer = Num::of(&b.req("y_outer")?)?;
        let up = b.opt("up").map(|v| Num::of(&v)).transpose()?.unwrap_or(Num::I(-1));
        let supported = b.opt("supported").map(|v| Num::of(&v)).transpose()?.unwrap_or(supported);
        apply(rt, solid, &station, y_outer, up, supported)
    })?;
    ns.def(rt, "plain_lips", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["station", "y_outer"], &[])?;
        let station = b.req("station")?;
        let y_outer = Num::of(&b.req("y_outer")?)?;
        Ok(wing::lips_val(&plain_lips(rt, &station, y_outer)?))
    })?;
    Ok(())
}

/// A number as `json.dumps` writes it.
fn num_json(n: Num) -> Value {
    match n {
        Num::I(i) => json!(i),
        Num::F(x) => json!(x),
    }
}

/// Purchased jack and complete receptacle datum, independent of the DATA plate.
pub fn jack_face_y(rt: &Rt, y_outer: Num) -> Result<f64> {
    let state = state(rt)?;
    let value = read(rt, "data-jack-face", json!({"data": state.data_json, "y_outer": num_json(y_outer)}))?;
    Ok(py::from_json(value)?.num()?)
}

/// Where the pad's 45-degree print-down run-out leaves its inboard face, as (y, z).
pub fn pad_runout(rt: &Rt, z: Num, y_outer: Num, up: Num) -> Result<(f64, f64)> {
    let state = state(rt)?;
    let value = read(rt, "data-pad-runout", json!({
        "data": state.data_json,
        "nameplate": state.nameplate_json,
        "z": num_json(z),
        "y_outer": num_json(y_outer),
        "up": num_json(up),
    }))?;
    let [y, z] = py::v2(&py::from_json(value)?)?;
    Ok((y, z))
}

pub fn aperture(rt: &Rt, y0: Num, y1: Num) -> Result<Val> {
    let state = state(rt)?;
    let (cq, d) = (&state.cq, &state.data);
    let sketch = m(&py::call(&cq.attr("Workplane")?, vec![py::s("XY")])?, "rect",
        vec![Val::Float(d.opening_w), Val::Float(d.opening_h)])?;
    let opening = m(&m(&m(&m(&sketch, "extrude", vec![y1.sub(y0).val()])?, "edges", vec![py::s("|Z")])?,
        "fillet", vec![Val::Float(d.opening_r)])?, "val", vec![])?;
    m(&rotate_x(&opening, -90)?, "translate", vec![py::tuple([Num::I(0), y0, Num::I(0)])])
}

/// Continuous plate and two full-span wings share one flat bed face.
pub fn blank(rt: &Rt) -> Result<Val> {
    let state = state(rt)?;
    let d = &state.data;
    let plate = py::call(&state.port_chip.attr("outline")?, vec![Val::Float(d.width), Val::Float(d.top),
        Val::Float(d.bottom), Val::Float(d.thick)])?;
    let mut wings = vec![];
    for part in wing::wings(rt, Num::F(d.width), Num::F(d.wing_span))? {
        wings.push(m(&part, "translate", vec![py::tuple([Val::Int(0), Val::Int(0), Val::Float(d.center_z)])])?);
    }
    let opening = aperture(rt, Num::F(-0.01), Num::F(d.thick + 0.01))?;
    m(&m(&m(&plate, "fuse", wings)?, "cut", vec![opening])?, "clean", vec![])
}

pub fn apply(rt: &Rt, solid: Val, station: &Val, y_outer: Num, up: Num, supported: Num) -> Result<Val> {
    let state = state(rt)?;
    let d = &state.data;
    let parts = py::unpack(station, 2)?;
    let (x, z) = (parts[0].clone(), parts[1].clone());
    let mut o = ApplyOpts::defaults(rt)?;
    o.up = up;
    o.supported = supported;
    o.width = Num::F(d.width);
    o.height = Num::F(d.height);
    o.wing_span = Num::F(d.wing_span);
    o.access = false;
    o.runout_lead = Num::F(wing::state(rt)?.plate.runout_lead);
    let centre = (Num::of(&x)?, Num::of(&z)?.add(Num::F(d.center_z)));
    let solid = wing::apply(rt, solid, centre, y_outer, &o)?;
    let mouth = py::call_kw(&state.port_chip.attr("outline")?, vec![
        Val::Float(d.width + 2. * d.face_air),
        Val::Float(d.top + d.face_air),
        Val::Float(d.bottom + d.face_air),
        Val::Float(d.pocket_depth + 1. + d.back_air),
    ], vec![("radius", Val::Float(d.corner_r + d.face_air))])?;
    let lifted = m(&mouth, "translate", vec![py::tuple([Num::I(0), Num::I(0), up.mul(supported)])])?;
    let mouth = m(&mouth, "fuse", vec![lifted])?;
    let shift = Val::Tuple(vec![x, y_outer.sub(Num::F(d.pocket_depth)).sub(Num::F(d.back_air)).val(), z]);
    m(&m(&solid, "cut", vec![m(&mouth, "translate", vec![shift])?])?, "clean", vec![])
}

pub fn plain_lips(rt: &Rt, station: &Val, y_outer: Num) -> Result<[[Num; 6]; 2]> {
    let d = state(rt)?.data;
    let parts = py::unpack(station, 2)?;
    let centre = (Num::of(&parts[0])?, Num::of(&parts[1])?.add(Num::F(d.center_z)));
    wing::plain_lips(rt, centre, y_outer, Num::F(d.width), Num::F(d.wing_span))
}
