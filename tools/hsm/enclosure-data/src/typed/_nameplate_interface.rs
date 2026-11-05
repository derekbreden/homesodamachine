//! Nameplate face and its two plate-owned PET-GF snap tabs, in millimetres.
//!
//! The plate's back is Y=0; its face is +Y. Tabs run into -Y. One bar behind
//! the pocket receives both: its shoulders are rigid, and each tab's slot and
//! catch pocket stand in it with the bar's full frame above and below.
//!
//! Typed state: the face constants (`_dimensions()['face']`) and the plate's own
//! (`_dimensions()['nameplate']`) are read once at install; the `face-values` reading is pure and
//! kept after its first use. CadQuery stays a provider (`cq`), reached by callback. The helpers
//! at the end of this file (`m`, `mk`, `read`, `n`, ...) serve the other nameplate-family
//! modules too.
use super::num::Num;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::cell::OnceCell;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_nameplate_interface";

/// The face constants this module computes with (`_dimensions()['face']`); every one is a float.
#[derive(Clone, Copy, Debug)]
pub struct Face {
    pub bar_frame: f64,
    pub bearing_slip: f64,
    pub bevel: f64,
    pub corner_r: f64,
    pub lip: f64,
    pub lip_land: f64,
    pub lip_start: f64,
    pub shoulder_stock: f64,
    pub shoulder_w: f64,
    pub slip: f64,
    pub tab_length: f64,
    pub tab_thick: f64,
    pub tab_width: f64,
    pub tab_x: f64,
    pub tab_z: f64,
    pub thick: f64,
    pub wall: f64,
}

/// The slot sides `face-values` gives.
#[derive(Clone, Copy, Debug)]
struct FaceValues {
    neck: f64,
    inward: f64,
    bar_end: f64,
}

pub struct State {
    pub cq: Val,
    pub face: Face,
    /// `_dimensions()['face']` as the JSON `_read` sends.
    face_json: Value,
    /// `_dimensions()['nameplate']`: WIDTH, HEIGHT, CORNER_R, THICK as `station` reads them.
    plate: [Val; 4],
    /// The `Nameplate` namedtuple class.
    pub nameplate: Val,
    values: OnceCell<FaceValues>,
}

/// A `Nameplate` station: `namedtuple("Nameplate", "x z width height corner bevel slip thick wall")`.
#[derive(Clone, Copy, Debug)]
pub struct Nameplate {
    pub x: Num,
    pub z: Num,
    pub width: Num,
    pub height: Num,
    pub corner: Num,
    pub bevel: Num,
    pub slip: Num,
    pub thick: Num,
    pub wall: Num,
}
impl Nameplate {
    /// The Python `Nameplate` instance with these fields.
    pub fn py(&self, rt: &Rt) -> Result<Val> {
        let state = state(rt)?;
        py::call(&state.nameplate, [self.x, self.z, self.width, self.height, self.corner, self.bevel,
            self.slip, self.thick, self.wall].iter().map(|v| v.val()).collect())
    }
    /// The fields of a station object (a `Nameplate` or anything with its attributes), read in
    /// field order.
    pub fn of(station: &Val) -> Result<Nameplate> {
        let f = |name: &str| -> Result<Num> { Num::of(&station.attr(name)?) };
        Ok(Nameplate {
            x: f("x")?,
            z: f("z")?,
            width: f("width")?,
            height: f("height")?,
            corner: f("corner")?,
            bevel: f("bevel")?,
            slip: f("slip")?,
            thick: f("thick")?,
            wall: f("wall")?,
        })
    }
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    let namedtuple = rt.member("collections", "namedtuple")?;
    ns.set("namedtuple", namedtuple.clone())?;
    ns.set("math", rt.import("math")?)?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let dimensions = rt.member("_enclosure_data", "dimensions")?;
    ns.set("_dimensions", dimensions.clone())?;
    ns.set("_read", rt.member("_enclosure_data", "read")?)?;
    // globals().update(_dimensions()['face'])
    let values = py::snapshot(&py::call(&dimensions, vec![])?)?;
    let face = py::at(&values, "face")?;
    update(ns, &face)?;
    let nameplate = py::call(&namedtuple,
        vec![py::s("Nameplate"), py::s("x z width height corner bevel slip thick wall")])?;
    ns.set("Nameplate", nameplate.clone())?;
    let plate = py::at(&values, "nameplate")?;
    let f = |key: &str| -> Result<f64> { py::at(&face, key)?.num() };
    rt.keep(MODULE, State {
        cq,
        face: Face {
            bar_frame: f("BAR_FRAME")?,
            bearing_slip: f("BEARING_SLIP")?,
            bevel: f("BEVEL")?,
            corner_r: f("CORNER_R")?,
            lip: f("LIP")?,
            lip_land: f("LIP_LAND")?,
            lip_start: f("LIP_START")?,
            shoulder_stock: f("SHOULDER_STOCK")?,
            shoulder_w: f("SHOULDER_W")?,
            slip: f("SLIP")?,
            tab_length: f("TAB_LENGTH")?,
            tab_thick: f("TAB_THICK")?,
            tab_width: f("TAB_WIDTH")?,
            tab_x: f("TAB_X")?,
            tab_z: f("TAB_Z")?,
            thick: f("THICK")?,
            wall: f("WALL")?,
        },
        face_json: py::plain(&face)?,
        plate: [py::at(&plate, "WIDTH")?, py::at(&plate, "HEIGHT")?, py::at(&plate, "CORNER_R")?,
            py::at(&plate, "THICK")?],
        nameplate,
        values: OnceCell::new(),
    });

    ns.def(rt, "station", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["x", "z"], &[])?;
        let (x, z) = (Num::of(&b.req("x")?)?, Num::of(&b.req("z")?)?);
        station(rt, x, z)?.py(rt)
    })?;
    ns.def(rt, "box", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["x0", "x1", "y0", "y1", "z0", "z1"], &[])?;
        let v = ["x0", "x1", "y0", "y1", "z0", "z1"].map(|name| b.req(name));
        let [x0, x1, y0, y1, z0, z1] = v;
        make_box(rt, [x0?, x1?, y0?, y1?, z0?, z1?])
    })?;
    ns.def(rt, "neck", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Float(neck(rt)?))
    })?;
    ns.def(rt, "inward", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Float(inward(rt)?))
    })?;
    ns.def(rt, "bar_end", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Float(bar_end(rt)?))
    })?;
    ns.def(rt, "slot_z", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["supported", "up"], &[])?;
        let supported = b.opt("supported").unwrap_or(Val::Float(0.25));
        let up = b.opt("up").unwrap_or(Val::Float(-1.0));
        let (z0, z1) = slot_z(rt, &supported, &up)?;
        Ok(py::ftuple(&[z0, z1]))
    })?;
    ns.def(rt, "tabs", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::list(tabs(rt)?))
    })?;
    ns.def(rt, "receiver_additions", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["supported", "up"], &[])?;
        let supported = b.opt("supported").unwrap_or(Val::Float(0.25));
        let up = b.opt("up").unwrap_or(Val::Float(-1.0));
        Ok(Val::list(receiver_additions(rt, &supported, &up)?))
    })?;
    ns.def(rt, "receiver_cuts", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["supported", "up"], &[])?;
        let supported = b.opt("supported").unwrap_or(Val::Float(0.25));
        let up = b.opt("up").unwrap_or(Val::Float(-1.0));
        Ok(Val::list(receiver_cuts(rt, &supported, &up)?))
    })?;
    ns.def(rt, "apply", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["solid", "plate", "y_outer"], &["wall", "supported", "up"])?;
        let solid = b.req("solid")?;
        let plate = b.req("plate")?;
        let y_outer = b.req("y_outer")?;
        let wall = b.opt("wall").unwrap_or(Val::Float(3.0));
        let supported = b.opt("supported").unwrap_or(Val::Float(0.25));
        let up = b.opt("up").unwrap_or(Val::Float(-1.0));
        apply(rt, solid, &plate, &y_outer, &wall, &supported, &up)
    })?;
    Ok(())
}

/// `globals().update(values)` for a local dict.
pub(crate) fn update(ns: &Ns, values: &Val) -> Result<()> {
    for key in values.iter()? {
        let value = values.get(key.clone())?;
        ns.0.set(key, value)?;
    }
    Ok(())
}

pub fn station(rt: &Rt, x: Num, z: Num) -> Result<Nameplate> {
    let state = state(rt)?;
    let [width, height, corner, thick] = &state.plate;
    Ok(Nameplate {
        x,
        z,
        width: Num::of(width)?,
        height: Num::of(height)?,
        corner: Num::of(corner)?,
        bevel: Num::F(state.face.bevel),
        slip: Num::F(state.face.slip),
        thick: Num::of(thick)?,
        wall: Num::F(state.face.wall),
    })
}

/// `cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))`.
pub fn make_box(rt: &Rt, bounds: [Val; 6]) -> Result<Val> {
    let cq = &state(rt)?.cq;
    let [x0, x1, y0, y1, z0, z1] = bounds;
    let size = [sub(&x1, &x0)?, sub(&y1, &y0)?, sub(&z1, &z0)?];
    let corner = py::call(&cq.attr("Vector")?, vec![x0, y0, z0])?;
    let [dx, dy, dz] = size;
    py::call(&cq.attr("Solid")?.attr("makeBox")?, vec![dx.val(), dy.val(), dz.val(), corner])
}
/// `box` with typed bounds.
pub fn make_box_n(rt: &Rt, bounds: [Num; 6]) -> Result<Val> {
    make_box(rt, bounds.map(Num::val))
}

fn face_values(rt: &Rt) -> Result<FaceValues> {
    let state = state(rt)?;
    if let Some(values) = state.values.get() {
        return Ok(*values);
    }
    let reading = read(rt, "face-values", json!({"face": state.face_json}))?;
    let f = |key: &str| reading[key].as_f64().with_context(|| format!("face-values {key}"));
    let values = FaceValues { neck: f("neck")?, inward: f("inward")?, bar_end: f("bar_end")? };
    let _ = state.values.set(values);
    Ok(values)
}

/// The slot's outer side: the tab's outer face and its side slip.
pub fn neck(rt: &Rt) -> Result<f64> {
    Ok(face_values(rt)?.neck)
}

/// The slot's inner side, where the lip passes as the tab flexes.
pub fn inward(rt: &Rt) -> Result<f64> {
    Ok(face_values(rt)?.inward)
}

/// The bar's end, one shoulder beyond the slot.
pub fn bar_end(rt: &Rt) -> Result<f64> {
    Ok(face_values(rt)?.bar_end)
}

/// The slot's Z span. Only its print-down end takes the supported-surface allowance.
pub fn slot_z(rt: &Rt, supported: &Val, up: &Val) -> Result<(f64, f64)> {
    let state = state(rt)?;
    let reading = read(rt, "face-slots", json!({"face": state.face_json, "supported": py::plain(supported)?,
        "up": py::plain(up)?}))?;
    let rows = reading.as_array().context("face-slots rows")?;
    anyhow::ensure!(rows.len() == 2, "unpack: expected 2, got {}", rows.len());
    Ok((rows[0].as_f64().context("slot z0")?, rows[1].as_f64().context("slot z1")?))
}

/// Two straight cantilevers with square catches and tapered insertion noses.
pub fn tabs(rt: &Rt) -> Result<Vec<Val>> {
    let state = state(rt)?;
    let (cq, d) = (&state.cq, &state.face);
    let mut parts = vec![];
    for side in [-1i64, 1] {
        let (inner, outer) = (d.tab_x - d.tab_thick / 2., d.tab_x + d.tab_thick / 2.);
        let profile: [(f64, Num); 7] = [
            (inner, Num::I(0)),
            (outer, Num::I(0)),
            (outer, Num::F(-d.lip_start)),
            (outer + d.lip, Num::F(-d.lip_start)),
            (outer + d.lip, Num::F(-d.lip_start - d.lip_land)),
            (outer, Num::F(-d.tab_length)),
            (inner, Num::F(-d.tab_length)),
        ];
        let points = profile.iter().map(|(x, y)| py::tuple([Num::I(side).mul(Num::F(*x)), *y])).collect();
        let plane = mk(&py::call(&cq.attr("Workplane")?, vec![py::s("XY")])?, "workplane", vec![],
            vec![("offset", Val::Float(d.tab_z - d.tab_width / 2.))])?;
        let solid = m(&m(&m(&m(&plane, "polyline", vec![Val::list(points)])?, "close", vec![])?, "extrude",
            vec![Val::Float(d.tab_width)])?, "val", vec![])?;
        parts.push(solid);
    }
    Ok(parts)
}

/// The receiving bar and its corbel, relative to the plate back.
///
/// The bar spans both shoulders and runs from the wall to SHOULDER_STOCK
/// inboard of the bearing faces, BAR_FRAME above and below the slots. A 45°
/// corbel carries its print-down face to the wall.
pub fn receiver_additions(rt: &Rt, supported: &Val, up: &Val) -> Result<Vec<Val>> {
    let state = state(rt)?;
    let (cq, d) = (&state.cq, &state.face);
    let pad_y = d.thick - d.wall;
    let front = -d.lip_start + d.bearing_slip - d.shoulder_stock;
    let (z0, z1) = slot_z(rt, supported, up)?;
    let (lo, hi) = (z0 - d.bar_frame, z1 + d.bar_frame);
    let up = Num::of(up)?;
    let crown = if up.f() < 0. { hi } else { lo };
    let x = bar_end(rt)?;
    let origin = py::tuple([Val::Float(-x), Val::Int(0), Val::Int(0)]);
    let plane = mk(&cq.attr("Workplane")?, "__call__", vec![py::s("YZ")], vec![("origin", origin)])?;
    let corner = Num::F(crown).sub(up.mul(Num::F(pad_y - front)));
    let section = Val::list(vec![
        py::ftuple(&[front, crown]),
        py::ftuple(&[pad_y, crown]),
        py::tuple([Num::F(pad_y), corner]),
    ]);
    let corbel = m(&m(&m(&m(&plane, "polyline", vec![section])?, "close", vec![])?, "extrude",
        vec![Num::I(2).mul(Num::F(x)).val()])?, "val", vec![])?;
    Ok(vec![make_box_n(rt, [Num::F(-x), Num::F(x), Num::F(front), Num::F(pad_y), Num::F(lo), Num::F(hi)])?,
        corbel])
}

/// Each tab's slot and catch pocket, relative to the plate back.
///
/// The slot passes through the pocket floor and the bar. The catch pocket
/// runs from the slot's inner side out through the bar's end, ahead of the
/// shoulder's bearing face.
pub fn receiver_cuts(rt: &Rt, supported: &Val, up: &Val) -> Result<Vec<Val>> {
    let state = state(rt)?;
    let d = state.face;
    let (z0, z1) = slot_z(rt, supported, up)?;
    let far = -d.tab_length - 1.;
    let mut cuts = vec![];
    for side in [-1f64, 1.] {
        let (x0, x1) = sorted2(side * inward(rt)?, side * neck(rt)?);
        cuts.push(make_box_n(rt, [x0, x1, far, 0.8, z0, z1].map(Num::F))?);
        let (x0, x1) = sorted2(side * inward(rt)?, side * (bar_end(rt)? + 1.));
        cuts.push(make_box_n(rt, [x0, x1, far, -d.lip_start + d.bearing_slip, z0, z1].map(Num::F))?);
    }
    Ok(cuts)
}

/// `sorted((a, b))` of two floats: the runtime's stable ascending sort.
pub(crate) fn sorted2(a: f64, b: f64) -> (f64, f64) {
    if b < a { (b, a) } else { (a, b) }
}

/// Cut the same pocket and receiving bar in an enclosure wall or a fit coupon.
pub fn apply(rt: &Rt, solid: Val, plate: &Val, y_outer: &Val, wall: &Val, supported: &Val, up: &Val)
    -> Result<Val> {
    let cq = state(rt)?.cq.clone();
    let (y_outer, wall) = (Num::of(y_outer)?, Num::of(wall)?);
    let attr = |name: &str| -> Result<Num> { Num::of(&plate.attr(name)?) };
    let (y_inner, y_pad) = (y_outer.sub(wall), y_outer.sub(attr("wall")?));
    let floor = y_outer.sub(attr("thick")?);
    let two = Num::I(2);
    let (pw, ph) = (attr("width")?.add(two.mul(attr("slip")?)), attr("height")?.add(two.mul(attr("slip")?)));
    let pr = attr("corner")?.add(attr("slip")?);
    let workplane = |plane: &str| py::call(&cq.attr("Workplane")?, vec![py::s(plane)]);
    let sketch = m(&workplane("XY")?, "rect", vec![pw.add(two.mul(wall)).val(), ph.add(two.mul(wall)).val()])?;
    let pad = m(&m(&m(&m(&sketch, "extrude", vec![y_inner.sub(y_pad).val()])?, "edges", vec![py::s("|Z")])?,
        "fillet", vec![pr.add(wall).val()])?, "val", vec![])?;
    let pad = m(&rotate_x(&pad, -90)?, "translate", vec![py::tuple([attr("x")?, y_pad, attr("z")?])])?;
    let rise = y_inner.sub(y_pad);
    let (up_v, supported_v) = (up, supported);
    let up = Num::of(up)?;
    let supported = Num::of(supported)?;
    let zedge = attr("z")?.sub(up.mul(ph.div(two).add(wall)));
    let xhalf = pw.div(two).add(wall);
    let origin = py::tuple([attr("x")?.sub(xhalf).sub(Num::I(1)), Num::I(0), Num::I(0)]);
    let plane = mk(&cq.attr("Workplane")?, "__call__", vec![py::s("YZ")], vec![("origin", origin)])?;
    let section = Val::list(vec![
        py::tuple([y_pad, zedge]),
        py::tuple([y_pad, zedge.add(up.mul(rise))]),
        py::tuple([y_inner, zedge]),
    ]);
    let ramp = m(&m(&m(&m(&plane, "polyline", vec![section])?, "close", vec![])?, "extrude",
        vec![two.mul(xhalf).add(two).val()])?, "val", vec![])?;
    let pad = m(&pad, "cut", vec![ramp])?;
    let lifted = m(&pad, "translate", vec![py::tuple([Num::I(0), Num::I(0), up.mul(supported)])])?;
    let mut solid = m(&solid, "fuse", vec![pad, lifted])?;
    let placement = py::tuple([attr("x")?, floor, attr("z")?]);
    for addition in receiver_additions(rt, supported_v, up_v)? {
        solid = m(&solid, "fuse", vec![m(&addition, "translate", vec![placement.clone()])?])?;
    }
    let bevel = attr("bevel")?.sub(Num::F(2f64.sqrt() - 1.).mul(attr("slip")?));
    let mouth = m(&workplane("XY")?, "rect", vec![pw.val(), ph.val()])?;
    let mouth = m(&m(&m(&m(&m(&m(&mouth, "extrude", vec![attr("thick")?.add(Num::I(1)).val()])?, "edges",
        vec![py::s("|Z")])?, "fillet", vec![pr.val()])?, "faces", vec![py::s("<Z")])?, "chamfer",
        vec![bevel.val()])?, "val", vec![])?;
    let mouth = m(&rotate_x(&mouth, -90)?, "translate", vec![placement.clone()])?;
    let lifted = m(&mouth, "translate", vec![py::tuple([Num::I(0), Num::I(0), up.mul(supported)])])?;
    solid = m(&solid, "cut", vec![m(&mouth, "fuse", vec![lifted])?])?;
    for cutter in receiver_cuts(rt, supported_v, up_v)? {
        solid = m(&solid, "cut", vec![m(&cutter, "translate", vec![placement.clone()])?])?;
    }
    Ok(solid)
}

// Helpers the nameplate-family modules share.

/// `obj.name(*args)`.
pub(crate) fn m(obj: &Val, name: &str, args: Vec<Val>) -> Result<Val> {
    py::method(obj, name, args)
}
/// `obj.name(*args, **kwargs)`; `"__call__"` calls `obj` itself.
pub(crate) fn mk(obj: &Val, name: &str, args: Vec<Val>, kwargs: Vec<(&str, Val)>) -> Result<Val> {
    let f = if name == "__call__" { obj.clone() } else { obj.attr(name)? };
    py::call_kw(&f, args, kwargs)
}
/// `shape.rotate((0,0,0),(1,0,0),angle)` with an integer angle.
pub(crate) fn rotate_x(shape: &Val, angle: i64) -> Result<Val> {
    m(shape, "rotate", vec![ints(&[0, 0, 0]), ints(&[1, 0, 0]), Val::Int(angle)])
}
/// A tuple of integers.
pub(crate) fn ints(values: &[i64]) -> Val {
    Val::Tuple(values.iter().map(|&v| Val::Int(v)).collect())
}
/// `_enclosure_data.read(op, **fields)`, answered in this process. A failure reads as the
/// worker round trip's does: the `ValueError` `_rust_data` raises, as a callback error.
pub(crate) fn read(rt: &Rt, op: &str, fields: Value) -> Result<Value> {
    let mut payload = serde_json::Map::new();
    payload.insert("op".into(), json!(op));
    if let Value::Object(rows) = fields {
        payload.extend(rows);
    }
    rt.enclosure_data(Value::Object(payload))
        .map_err(|e| anyhow::anyhow!("ValueError: enclosure-data: {e:#}"))
}
/// `a - b` for two Python numbers.
fn sub(a: &Val, b: &Val) -> Result<Num> {
    Ok(Num::of(a)?.sub(Num::of(b)?))
}
