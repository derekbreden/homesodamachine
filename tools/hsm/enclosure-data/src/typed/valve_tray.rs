//! A VALVE TRAY IS A PLATE OF VALVE SEATS, and it is a wall of the enclosure.
//!
//! One `valve_seat` per valve — four blind sockets a corner post presses into — SUNK into a flat
//! plate that runs from side wall to side wall of `enclosure-front-top`. The plate is one socket
//! and one wall thick, so it is the boss: nothing stands off it, the valve lands on its face, and
//! the only thing it opens for is each valve's own port, on a channel out both ends. It is
//! that piece's own material, fused in the way the ASSE anchor, the flow-meter anchors and every
//! tube rib are: `enclosure._valve_trays` stands one per deck, off the stations
//! `enclosure_assembly.valve_tray_stations` reads off the placed valves. NO TRAY SHIPS AS A PART,
//! nothing bolts a valve to one and nothing is bonded — the posts in their sockets are the whole of
//! the retention, the same bargain the cold core's cap lid strikes under its three valves
//! (`_cold_core_interface.cap_cradles`).
//!
//!     ACROSS  wall to wall. The plate is the piece, so it takes no slip and ends on the two
//!             interior faces
//!     ALONG   the seats' own reach off their valves' centres, and one `MARGIN` past that. The
//!             plate ends where the last boss does; the valves' collets and the tube butted into
//!             them hang past it
//!
//! This module states the tray's own figures and draws one in its own frame; `enclosure` turns it
//! onto a deck and fuses it. The frame is `valve_seat`'s carried onto a plate:
//!   Z = out of the valve-side face, the direction a valve's own +Z runs. `z = 0` IS THAT FACE, so
//!       the plate spans z = −`THICK` to 0 and every seat is sunk from zero. That face is the plane
//!       the valve's own round body boss lands on, so a valve stands ON the plate and not on four
//!       boss tops — `SEAT` is negative here, and that is the whole of the difference.
//!   X = across the plate. Y = along it. Origin is the plate's centre in both.
//!
//! The rectangular socket pattern follows the valve: X across the plate and the port axis on Y.
//!
//! In the piece's own print orientation the plate stands vertical, wall to wall, and NOTHING
//! stands off it: the port channel is a notch that runs up the plate's own section, while
//! `enclosure._valve_socket_cutters` carries each horizontal socket's complete round post room into
//! a tangent teardrop roof. There is no unsupported crown and no support in the thirty-two sockets
//! to pick out — which is what the thickness and roof buy, a boss on a standing plate being a
//! cylinder cantilevered into air.
//!
//! Run:
//!     tools/cad-venv/bin/python hardware/printed-parts/enclosure/valve-tray/valve_tray.py
//!     tools/cad-venv/bin/python hardware/printed-parts/enclosure/valve-tray/valve_tray.py selftest
//!
//! Typed API: [`state`] holds the seat and valve figures `_source()` reads (a [`Source`]) and the
//! plate's stock (`valve-tray-defaults`, the names `globals().update(...)` binds: a [`Stock`]).
//! [`reach`], [`height`], [`wall_root_floors`], [`port_drop`], [`port_channel_depth`], [`grip`],
//! [`segment_area`], [`tray_volume`], [`channel_floor`], [`socket_numbers`],
//! [`tray_stock_numbers`] and [`numbers`] are this crate's own `valve-tray-` recipes
//! (`src/valve_tray.rs`), answered in this process; [`depth`] is the stock's `THICK`. The
//! CadQuery builders take and return CadQuery objects as `Val`. Front-top replaces
//! `build_port_channel` and `build_body_clearance` in this namespace while it records
//! (`_leaves`), so [`web`] and [`build_valve_tray`] reach `build_port_channel` through the
//! namespace on every call.
use super::_enclosure_interface;
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result, anyhow, bail, ensure};
use hsm_documents::interop;
use serde_json::{Map, Value, json};
use std::cell::OnceCell;
use std::cmp::Ordering;
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "valve_tray";

/// The `valve_seat` figures `_source()` reads, in its order.
const SEAT_FIGURES: [&str; 8] = [
    "wall",
    "socket_floor_z",
    "socket_radius",
    "seat_half_y",
    "seat_top_z",
    "port_air",
    "corner_inset_x",
    "corner_inset_y",
];

/// `_source()`: the seat's figures, its socket depth and the valve's port, as every
/// `valve-tray-` recipe reads them. Module constants of `valve_seat` and `beduan_solenoid`, read
/// once.
pub struct Source {
    /// The dict `_source()` returns, in its order.
    rows: Vec<(&'static str, Val)>,
    /// The same, as a recipe receives it.
    json: Value,
    pub wall: Num,
    pub socket_floor_z: Num,
    pub socket_radius: Num,
    pub seat_half_y: Num,
    pub seat_top_z: Num,
    pub port_air: Num,
    pub corner_inset_x: Num,
    pub corner_inset_y: Num,
    pub socket_depth: Num,
    pub port_center_z: Num,
    pub port_radius: Num,
}
impl Source {
    fn read(seat: &Val, valve: &Val) -> Result<Source> {
        let mut rows: Vec<(&'static str, Val)> = vec![];
        for name in SEAT_FIGURES {
            rows.push((name, seat.attr(name)?));
        }
        rows.push(("socket_depth", seat.attr("socket_depth")?.call(vec![], vec![])?));
        rows.push(("port_center_z", valve.attr("port_center_z")?));
        rows.push(("port_radius", valve.attr("port_radius")?));
        let mut json = Map::new();
        for (name, value) in &rows {
            json.insert((*name).to_owned(), py::plain(value)?);
        }
        let n = |name: &str| -> Result<Num> {
            Num::of(&rows.iter().find(|(key, _)| *key == name).context("a source figure")?.1)
        };
        Ok(Source {
            wall: n("wall")?,
            socket_floor_z: n("socket_floor_z")?,
            socket_radius: n("socket_radius")?,
            seat_half_y: n("seat_half_y")?,
            seat_top_z: n("seat_top_z")?,
            port_air: n("port_air")?,
            corner_inset_x: n("corner_inset_x")?,
            corner_inset_y: n("corner_inset_y")?,
            socket_depth: n("socket_depth")?,
            port_center_z: n("port_center_z")?,
            port_radius: n("port_radius")?,
            json: Value::Object(json),
            rows,
        })
    }
    /// A fresh `_source()` dict.
    fn val(&self) -> Val {
        py::dict(self.rows.iter().map(|(name, value)| (*name, value.clone())))
    }
}

/// The plate's stock, as `valve-tray-defaults` states it: the names the module's
/// `globals().update(...)` binds.
pub struct Stock {
    /// `THICK`: one socket and one wall.
    pub thick: Num,
    /// `MARGIN`: the plate past the last seat's reach.
    pub margin: Num,
    /// `SEAT`: where a valve's own frame lands, under the face.
    pub seat: Num,
    /// `PORT_SLIP`: the port channel's slip, the seat's `port_air`.
    pub port_slip: Num,
}

/// The valve body `build_body_clearance` clears, read off `beduan_solenoid` on first use.
struct Body {
    bearing_radius: Num,
    bearing_top: Num,
    body_radius: Num,
    body_main: [Num; 2],
    corner_boss_radius: Num,
    post_shoulder_z: Num,
    upper_corner_radius: Num,
    body_top_z: Num,
    top_box_bottom: Num,
    cap_width_x: Num,
    cap_depth_y: Num,
    top_box_height: Num,
    cap_corner_radius: Num,
}

/// The module's typed state.
pub struct State {
    pub source: Source,
    pub stock: Stock,
    /// The defaults reply: the stock `_data` sends as `stock`.
    stock_json: Value,
    /// `_here`: this module's file.
    here: PathBuf,
    valve: Val,
    seat: Val,
    body: OnceCell<Body>,
}
impl State {
    fn body(&self) -> Result<&Body> {
        if let Some(body) = self.body.get() {
            return Ok(body);
        }
        let v = &self.valve;
        let n = |name: &str| -> Result<Num> { Num::of(&v.attr(name)?) };
        let at = |name: &str, i: i64| -> Result<Num> { Num::of(&v.attr(name)?.get(Val::Int(i))?) };
        let body = Body {
            bearing_radius: n("bearing_radius")?,
            bearing_top: at("bearing_z_range", 1)?,
            body_radius: n("body_radius")?,
            body_main: [at("body_main_z_range", 0)?, at("body_main_z_range", 1)?],
            corner_boss_radius: n("corner_boss_radius")?,
            post_shoulder_z: n("post_shoulder_z")?,
            upper_corner_radius: n("upper_corner_radius")?,
            body_top_z: n("body_top_z")?,
            top_box_bottom: at("top_box_z_range", 0)?,
            cap_width_x: n("cap_width_x")?,
            cap_depth_y: n("cap_depth_y")?,
            top_box_height: n("top_box_height")?,
            cap_corner_radius: n("cap_corner_radius")?,
        };
        Ok(self.body.get_or_init(|| body))
    }
}

/// The module's state, initializing the module on first use.
pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// A name another module may replace in this namespace, as it stands now.
fn replaced(rt: &Rt, name: &str) -> Result<Val> {
    rt.namespace(MODULE)?.get(name)
}

// The runtime's arithmetic on the module's numbers.

fn order(a: Num, b: Num) -> Result<Ordering> {
    a.f().partial_cmp(&b.f()).context("unordered numeric comparison")
}
fn lt(a: Num, b: Num) -> Result<bool> {
    Ok(order(a, b)?.is_lt())
}
fn gt(a: Num, b: Num) -> Result<bool> {
    Ok(order(a, b)?.is_gt())
}
fn ge(a: Num, b: Num) -> Result<bool> {
    Ok(!order(a, b)?.is_lt())
}
fn le(a: Num, b: Num) -> Result<bool> {
    Ok(!order(a, b)?.is_gt())
}
fn abs(n: Num) -> Num {
    match n {
        Num::I(i) => Num::I(i.abs()),
        Num::F(x) => Num::F(x.abs()),
    }
}
/// `max(a, b)`: the first of equal values wins.
fn max2(a: Num, b: Num) -> Result<Num> {
    Ok(if gt(b, a)? { b } else { a })
}
/// `min(values)`: the first of equal values wins.
fn min_of(values: &[Num]) -> Result<Num> {
    let mut best: Option<Num> = None;
    for &v in values {
        if best.map(|b| order(v, b)).transpose()?.is_none_or(Ordering::is_lt) {
            best = Some(v);
        }
    }
    best.context("empty min/max")
}
/// `max(values)`: the first of equal values wins.
fn max_of(values: &[Num]) -> Result<Num> {
    let mut best: Option<Num> = None;
    for &v in values {
        if best.map(|b| order(v, b)).transpose()?.is_none_or(Ordering::is_gt) {
            best = Some(v);
        }
    }
    best.context("empty min/max")
}
/// `math.sqrt(x)`.
fn sqrt(x: f64) -> Result<f64> {
    if !(x >= 0.) {
        bail!("math domain error");
    }
    Ok(x.sqrt())
}

// The recipes' JSON.

fn num_json(n: Num) -> Value {
    match n {
        Num::I(i) => json!(i),
        Num::F(x) => json!(x),
    }
}
/// A seat row as a recipe receives it: `[[x, y], ...]`.
fn seats_json(seats: &[[Num; 2]]) -> Value {
    Value::Array(seats.iter().map(|[x, y]| Value::Array(vec![num_json(*x), num_json(*y)])).collect())
}
/// Seats `(x, y)` as Python hands them in.
fn seats_of(seats: &Val) -> Result<Vec<[Num; 2]>> {
    py::snapshot(seats)?
        .iter()?
        .iter()
        .map(|row| {
            let p = py::unpack(row, 2)?;
            Ok([Num::of(&p[0])?, Num::of(&p[1])?])
        })
        .collect()
}
fn number(reply: Value, op: &str) -> Result<f64> {
    reply.as_f64().with_context(|| format!("valve-tray-{op} is numeric"))
}
fn figures(reply: Value, op: &str) -> Result<Vec<f64>> {
    reply
        .as_array()
        .with_context(|| format!("valve-tray-{op} is a list"))?
        .iter()
        .map(|x| x.as_f64().with_context(|| format!("valve-tray-{op} figures are numeric")))
        .collect()
}
/// `tuple(values)` of a recipe's reply, each value as the JSON holds it.
fn tuple_of(v: Value) -> Result<Val> {
    match v {
        Value::Array(rows) => Ok(Val::Tuple(rows.into_iter().map(py::from_json).collect::<Result<_>>()?)),
        other => py::from_json(other)?.iter().map(Val::Tuple),
    }
}

/// `_read(op, **values)`: this crate's own recipe, answered in this process. A recipe's error
/// reads as the worker round trip raises it.
fn read(rt: &Rt, request: Value) -> Result<Value> {
    rt.enclosure_data(request).map_err(|error| anyhow!("ValueError: enclosure-data: {error:#}"))
}

/// `_data(op, **values)`: a `valve-tray-` recipe on the seat, the valve and this plate's stock.
fn data(rt: &Rt, op: &str, values: Vec<(String, Value)>) -> Result<Value> {
    let st = state(rt)?;
    let mut request = Map::new();
    request.insert("op".into(), json!(format!("valve-tray-{op}")));
    request.insert("source".into(), st.source.json.clone());
    request.insert("stock".into(), st.stock_json.clone());
    for (key, value) in values {
        ensure!(
            !matches!(key.as_str(), "source" | "stock"),
            "read() got multiple values for keyword argument '{key}'"
        );
        request.insert(key, value);
    }
    read(rt, Value::Object(request))
}
/// `_data(op, **values)` with Python values, its reply as Python reads the worker's.
fn data_val(rt: &Rt, op: &str, values: Vec<(&str, Val)>) -> Result<Val> {
    let values = values
        .into_iter()
        .map(|(key, value)| Ok((key.to_owned(), py::plain(&value)?)))
        .collect::<Result<Vec<_>>>()?;
    py::from_json(data(rt, op, values)?)
}

/// The seat's reach along its port axis, which sets the plate's height.
pub fn reach(rt: &Rt) -> Result<f64> {
    number(data(rt, "reach", vec![])?, "reach")
}

/// The seats' complete row span, their reach, and one `MARGIN` past each end.
pub fn height(rt: &Rt, seats: &[[Num; 2]]) -> Result<f64> {
    number(data(rt, "height", vec![("seats".into(), seats_json(seats))])?, "height")
}

/// The lower edge at each wall, following that side's outermost valve row.
///
/// The lower band between staggered rows stays inside the enclosure lip faces;
/// each full-width wall root carries its outer valve's complete reach and margin.
/// Coordinates are the seats' along-plate axis, world Z in the enclosure.
pub fn wall_root_floors(rt: &Rt, seats: &[[Num; 2]]) -> Result<Vec<f64>> {
    figures(data(rt, "wall-root-floors", vec![("seats".into(), seats_json(seats))])?, "wall-root-floors")
}

/// How far the valve's PORT hangs under the face the valve lands on.
///
/// The face is that landing plane (`valve_seat.seat_top_z`), and the port's barrel hangs
/// `beduan_solenoid.port_center_z` over the mounting plane with `port_radius` of itself under
/// that — so the barrel reaches this far inside a plate whose face is the landing plane. It is
/// why the plate opens a channel and not why the plate is thick: the sockets set the thickness
/// and the channel is cut back out of it.
pub fn port_drop(rt: &Rt) -> Result<f64> {
    number(data(rt, "port-drop", vec![])?, "port-drop")
}

/// How deep that channel cuts below the face — the port's drop and its slip.
pub fn port_channel_depth(rt: &Rt) -> Result<f64> {
    number(data(rt, "channel-depth", vec![])?, "channel-depth")
}

/// The width of one bead of this plate, which is what a web is read against.
///
/// A WEB IS WIDE OR IT IS NOTHING, and the figure that decides which is the nozzle, not zero.
/// The doc-only `main` hands in `enclosure_assembly.EXTRUSION_W` — the same constant
/// `tray-web` holds `web()` against — so the doc and the bound cannot come to differ about
/// what one bead is.
pub fn extrusion(width: Val) -> Val {
    width
}

/// The plate left between a corner socket and the port channel, MEASURED.
///
/// The two features run at right angles — the sockets down the valve's own axis, the channel
/// across the plate on its Y. A socket's inner edge stands `corner_inset_x - socket_radius` off
/// the centreline and the channel `port_radius + PORT_SLIP`, a tenth of a millimetre apart if
/// they ever met at one height; the channel's widest station is above the sockets' mouths and
/// never does. Anything that brings the two to one height spends that tenth at once, and
/// nothing about a solid says it has been spent.
///
/// NOT ARITHMETIC. The closest approach of the two axes lies above the socket's own top, so a
/// figure struck off the radii answers for a cylinder that is not there. This reads the solids.
///
/// Compare what comes back against the nozzle that lays it, not against zero: these plates are
/// `enclosure-front-top`'s material, so the bead they come off is the enclosure exterior's own
/// and `extrusion()` is where it is read. A web under one extrusion wide is a web the slicer
/// does not lay, and the socket opens into the channel over the stretch it does not.
pub fn web(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let sockets = st.seat.attr("build_sockets")?.call(vec![], vec![])?.attr("val")?.call(vec![], vec![])?;
    let channel_of = replaced(rt, "build_port_channel")?;
    let length = Val::Float(height(rt, &[])? + 2.0);
    let channel = channel_of.call(vec![length], vec![])?.attr("val")?.call(vec![], vec![])?;
    sockets.attr("distance")?.call(vec![channel], vec![])
}

/// How much of a corner post stands INSIDE the plate, with the valve at rest.
///
/// THE POSTS IN THEIR SOCKETS ARE THE WHOLE OF THE RETENTION (`valve_seat`), so this is the
/// whole of what holds a valve down. A still deck's face is the valve's own landing plane and
/// the post is in the plate over its whole length, on every deck — the release moves the tee
/// it butts and not the valve itself, so no plate on this machine is set off its valves.
pub fn grip(rt: &Rt) -> Result<f64> {
    number(data(rt, "grip", vec![])?, "grip")
}

/// One valve's port channel, in the valve's own frame: the barrel and its slip, run `length`
/// along the plate's own Y and open at both ends.
///
/// A CYLINDER AND NOT A SLOT. The port is round and the channel closes on it all the way round
/// at one slip, the way the flow-meter anchors take a barrel — a square slot to the same width
/// would take the plate's whole depth at the corners for air the port is nowhere near.
pub fn build_port_channel(rt: &Rt, length: Num) -> Result<Val> {
    let st = state(rt)?;
    let cq = rt.import("cadquery")?;
    let plane = cq.attr("Workplane")?.call(vec![py::s("XZ")], vec![])?;
    let centred = plane.attr("center")?.call(vec![Val::Float(0.0), st.source.port_center_z.val()], vec![])?;
    let circle = centred.attr("circle")?.call(vec![st.source.port_radius.add(st.stock.port_slip).val()], vec![])?;
    circle.attr("extrude")?.call(vec![length.div(Num::F(2.0)).val()], vec![("both".into(), Val::Bool(true))])
}

/// The stepped valve body with one millimetre of air above its bearing plane.
///
/// The lower post sockets retain their own radial fit below the bearing plane.
/// The physical cap dimensions are independent of the manifold's packing pitch.
pub fn build_body_clearance(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let cq = rt.import("cadquery")?;
    let slip = st.stock.port_slip;
    let workplane = |offset: Num| -> Result<Val> {
        cq.attr("Workplane")?
            .call(vec![py::s("XY")], vec![])?
            .attr("workplane")?
            .call(vec![], vec![("offset".into(), offset.val())])
    };
    let cylinder = |radius: Num, z0: Num, z1: Num, x: Num, y: Num| -> Result<Val> {
        workplane(z0)?
            .attr("center")?
            .call(vec![x.val(), y.val()], vec![])?
            .attr("circle")?
            .call(vec![radius.val()], vec![])?
            .attr("extrude")?
            .call(vec![z1.sub(z0).val()], vec![])
    };
    let union = |body: &Val, other: Val| -> Result<Val> { body.attr("union")?.call(vec![other], vec![]) };
    let b = st.body()?;
    let s = &st.source;
    let origin = Num::F(0.0);
    let mut body = cylinder(b.bearing_radius.add(slip), s.seat_top_z, b.bearing_top.add(slip), origin, origin)?;
    body = union(
        &body,
        cylinder(b.body_radius.add(slip), b.body_main[0].sub(slip), b.body_main[1].add(slip), origin, origin)?,
    )?;
    for sx in [-1.0, 1.0] {
        for sy in [-1.0, 1.0] {
            let (x, y) = (Num::F(sx).mul(s.corner_inset_x), Num::F(sy).mul(s.corner_inset_y));
            body = union(&body, cylinder(b.corner_boss_radius.add(slip), s.seat_top_z, b.post_shoulder_z.add(slip), x, y)?)?;
            body = union(
                &body,
                cylinder(b.upper_corner_radius.add(slip), b.post_shoulder_z.sub(slip), b.body_top_z.add(slip), x, y)?,
            )?;
        }
    }
    let two_slip = |figure: Num| figure.add(Num::F(2.0).mul(slip));
    let cap = workplane(b.top_box_bottom.sub(slip))?
        .attr("rect")?
        .call(vec![two_slip(b.cap_width_x).val(), two_slip(b.cap_depth_y).val()], vec![])?
        .attr("extrude")?
        .call(vec![two_slip(b.top_box_height).val()], vec![])?
        .attr("edges")?
        .call(vec![py::s("|Z")], vec![])?
        .attr("fillet")?
        .call(vec![b.cap_corner_radius.add(slip).val()], vec![])?;
    union(&body, cap)
}

/// One tray: the plate, with one `valve_seat`'s sockets and one port channel sunk into it
/// per station in `seats`.
///
/// `seats` is `(x, y)` per valve in the plate's own frame — where that valve's footprint centre
/// lands. Every valve on one tray has its port axis on Y and stands on the same plane;
/// adjacent columns may have different Y positions.
pub fn build_valve_tray(rt: &Rt, width: Num, seats: &[[Num; 2]]) -> Result<Val> {
    let cq = rt.import("cadquery")?;
    if seats.is_empty() {
        bail!("a valve tray with no seats is a plate, and this machine prints none");
    }
    let st = state(rt)?;
    let ys: Vec<Num> = seats.iter().map(|p| p[1]).collect();
    let mid_y = min_of(&ys)?.add(max_of(&ys)?).div(Num::F(2.0));
    let tray_height = height(rt, seats)?;
    let thick = st.stock.thick;
    let mut tray = cq
        .attr("Workplane")?
        .call(vec![py::s("XY")], vec![])?
        .attr("workplane")?
        .call(vec![], vec![("offset".into(), thick.neg().val())])?
        .attr("box")?
        .call(
            vec![width.val(), Val::Float(tray_height), thick.val()],
            vec![("centered".into(), py::tuple([Val::Bool(true), Val::Bool(true), Val::Bool(false)]))],
        )?
        .attr("translate")?
        .call(vec![py::tuple([Val::Float(0.0), mid_y.val(), Val::Float(0.0)])], vec![])?;
    // A station is where the valve's own frame lands: `SEAT` under the face, which is where the
    // sockets and the channel are both struck from. Cut, not fused — the plate is the boss.
    for &[x, y] in seats {
        let station = || py::tuple([x.val(), y.val(), st.stock.seat.val()]);
        let sockets = st.seat.attr("build_sockets")?.call(vec![], vec![])?.attr("translate")?.call(vec![station()], vec![])?;
        tray = tray.attr("cut")?.call(vec![sockets], vec![])?;
        let channel_length = Num::F(tray_height).add(Num::F(2.0).mul(abs(y.sub(mid_y)))).add(Num::F(2.0));
        let channel = replaced(rt, "build_port_channel")?
            .call(vec![channel_length.val()], vec![])?
            .attr("translate")?
            .call(vec![station()], vec![])?;
        tray = tray.attr("cut")?.call(vec![channel], vec![])?;
    }
    Ok(tray)
}

/// The area a circle of `radius` whose centre stands `over` a plane leaves BELOW it.
pub fn segment_area(rt: &Rt, radius: Num, over: Num) -> Result<f64> {
    number(data(rt, "segment", vec![("radius".into(), num_json(radius)), ("over".into(), num_json(over))])?, "segment")
}

/// One tray's material, in closed form — the plate, less one seat's four sockets and one
/// port channel apiece.
///
/// Exact, and that is a reading and not a convenience: the four sockets stand clear of one
/// another and clear of the channel between them (`selftest` measures both), the channel runs
/// straight out of both ends of the plate, and neither reaches the plate's back. So every cut
/// is a whole prism of known section, and a tray that measures anything else has a socket in
/// its channel or a channel out of its back.
pub fn tray_volume(rt: &Rt, width: Num, seats: &[[Num; 2]]) -> Result<f64> {
    number(data(rt, "volume", vec![("width".into(), num_json(width)), ("seats".into(), seats_json(seats))])?, "volume")
}

/// What the plate keeps under a port channel at its deepest. The channel's own floor is the
/// thinnest section on the plate — thinner than the socket floors, or the channel would be the
/// thing that sets `THICK`.
pub fn channel_floor(rt: &Rt) -> Result<f64> {
    number(data(rt, "channel-floor", vec![])?, "channel-floor")
}

/// The plate's whole run along its own Z — what the enclosure has to leave clear on a
/// deck's plane. Nothing stands over the face, so it is the plate and only the plate.
pub fn depth(rt: &Rt) -> Result<Num> {
    Ok(state(rt)?.stock.thick)
}

/// The tray against the valve it holds and the seat it carries.
pub fn selftest(rt: &Rt) -> Result<i64> {
    let st = state(rt)?;
    let s = &st.source;
    let stock = &st.stock;
    let g = |n: Num| n.fmt("g");
    let mut fails: Vec<String> = vec![];
    let socket_depth = || -> Result<Num> { Num::of(&st.seat.attr("socket_depth")?.call(vec![], vec![])?) };
    if lt(stock.thick.sub(socket_depth()?), s.wall.sub(Num::F(1e-9)))? {
        fails.push(format!(
            "a plate {} mm thick keeps {} mm behind a socket {} deep, under the {} mm wall every \
             socket in this machine is floored on",
            g(stock.thick),
            stock.thick.sub(socket_depth()?).fmt(".3f"),
            g(socket_depth()?),
            g(s.wall)
        ));
    }
    if le(Num::F(channel_floor(rt)?), s.wall.sub(Num::F(1e-9)))? {
        fails.push(format!(
            "a port channel {} mm deep leaves {} mm of plate under it, under one {} mm wall — the \
             channel is what sets the plate's thinnest section and it has outrun the sockets",
            num::fmt(port_channel_depth(rt)?, ".3f"),
            num::fmt(channel_floor(rt)?, ".3f"),
            g(s.wall)
        ));
    }
    if le(Num::F(port_drop(rt)?), Num::F(0.0))? {
        fails.push(format!(
            "the valve's port stands {} mm CLEAR of the face it lands on, so the plate needs no \
             channel and this one cuts a groove for air",
            num::fmt(-port_drop(rt)?, ".3f")
        ));
    }
    // The channel's own half-width where it opens on the face, against the nearest socket's.
    let open = num::pow(s.port_radius.add(stock.port_slip).f(), 2.0) - num::pow(s.port_center_z.sub(s.seat_top_z).f(), 2.0);
    let open_half = sqrt(max2(Num::F(open), Num::F(0.0))?.f())?;
    let socket_wall = s.corner_inset_x.sub(s.socket_radius);
    if ge(Num::F(open_half), socket_wall.sub(Num::F(1e-9)))? {
        fails.push(format!(
            "the port channel opens {} mm either side of the valve's centre and the nearest socket \
             wall stands at {} — the channel is in the socket, and a socket open down its side holds \
             no post",
            num::fmt(open_half, ".3f"),
            socket_wall.fmt(".3f")
        ));
    }
    // A synthetic row of four, one seat's width and a millimetre apart, so the construction is
    // measured here as well as where the machine stands its valves.
    let pitch = Num::F(2.0).mul(Num::of(&st.seat.attr("seat_half_x")?)?).add(Num::F(1.0));
    let seats: Vec<[Num; 2]> =
        [(-1.5, -3.0), (-0.5, 3.0), (0.5, -3.0), (1.5, 3.0)].map(|(i, y)| [Num::F(i).mul(pitch), Num::F(y)]).to_vec();
    let width = pitch.mul(Num::F(4.0));
    let mut attempt = || -> Result<()> {
        let built = build_valve_tray(rt, width, &seats)?.attr("val")?.call(vec![], vec![])?;
        let volume = || -> Result<Num> { Num::of(&built.attr("Volume")?.call(vec![], vec![])?) };
        let closed = Num::F(tray_volume(rt, width, &seats)?);
        if gt(abs(volume()?.sub(closed)), Num::F(1e-6).mul(closed))? {
            fails.push(format!(
                "a four-seat tray measures {} mm^3 against the {} its closed form says — a boss has \
                 met its neighbour or run off the plate",
                volume()?.fmt(".3f"),
                closed.fmt(".3f")
            ));
        }
        let bb = built.attr("BoundingBox")?.call(vec![], vec![])?;
        if gt(abs(Num::of(&bb.attr("ylen")?)?.sub(Num::F(height(rt, &seats)?))), Num::F(1e-6))? {
            fails.push(format!(
                "a tray stands {} mm high against the {} `height` declares",
                num::fmtv(&bb.attr("ylen")?, ".4f")?,
                num::fmt(height(rt, &seats)?, ".4f")
            ));
        }
        Ok(())
    };
    if let Err(error) = attempt() {
        fails.push(error.to_string());
    }
    for line in &fails {
        rt.print(format!("FAIL {line}"))?;
    }
    if fails.is_empty() {
        rt.print(format!(
            "ok  valve-tray  {} mm high x {} thick, seat {} (sunk), reach {}, port channel {} deep on {} of floor",
            num::fmt(height(rt, &seats)?, "g"),
            g(stock.thick),
            g(stock.seat),
            num::fmt(reach(rt)?, "g"),
            num::fmt(port_channel_depth(rt)?, ".3f"),
            num::fmt(channel_floor(rt)?, ".3f")
        ))?;
    }
    Ok(if fails.is_empty() { 0 } else { 1 })
}

/// The trays the enclosure stands, as `{name: (width, seats)}` in each plate's own frame.
///
/// `enclosure_assembly` groups the valves no cap cradle holds by the plane each stands on and
/// hands back one tray per plane, and the artifact carries what that grouping came to — so a
/// plate is drawn off a machine the assembly's own run already stood.
///
/// The doc-only `main` hands in the artifact. Keeping that run dependency in `main` leaves
/// the shape functions' source closure at this part.
pub fn trays_of_machine(facts: &Val) -> Result<Val> {
    facts.attr("valve_trays")
}

/// `_socket_numbers(x, y, shift)`: one seat's four sockets, as the recipe states them.
pub fn socket_numbers(rt: &Rt, x: Num, y: Num, shift: Num) -> Result<Value> {
    data(rt, "sockets", vec![("x".into(), num_json(x)), ("y".into(), num_json(y)), ("shift".into(), num_json(shift))])
}

/// The stock and cylindrical cuts of ``build_valve_tray``, in its own frame.
pub fn tray_stock_numbers(rt: &Rt, width: Num, seats: &[[Num; 2]]) -> Result<Value> {
    data(rt, "stock", vec![("width".into(), num_json(width)), ("seats".into(), seats_json(seats))])
}

/// The original tray stock, socket/channel cylinders and finite web-reading solids.
pub fn numbers(rt: &Rt, trays: &Val) -> Result<Value> {
    let extrusion_w = _enclosure_interface::value(rt, "extrusion_w")?;
    data(rt, "recipe", vec![("trays".into(), py::plain(trays)?), ("extrusion_w".into(), json!(extrusion_w))])
}

/// The doc-only run: the machine's trays checked by the part program, the report printed and
/// the README's figures substituted.
pub fn main(rt: &Rt) -> Result<()> {
    let st = state(rt)?;
    let rust_part = rt.import("_rust_part")?;
    let facts = rt.import("_facts")?.attr("read")?.call(vec![], vec![])?;
    let trays = trays_of_machine(&facts)?;
    let check = rust_part.attr("check")?;
    let recipe = py::from_json(numbers(rt, &trays)?)?;
    let measured = check.call(vec![py::s("enclosure-components"), py::s("valve-tray"), recipe], vec![])?;
    let report = data(
        rt,
        "report",
        vec![("trays".into(), py::plain(&trays)?), ("measured".into(), py::plain(&measured)?)],
    )?;
    let lines = py::from_json(report["lines"].clone())?.iter()?.iter().map(Val::str).collect::<Result<Vec<_>>>()?;
    rt.print(lines.join("\n"))?;
    let variables = py::from_json(report["variables"].clone())?;
    let mut values = BTreeMap::new();
    for key in variables.iter()? {
        values.insert(key.str()?, variables.get(key)?.str()?);
    }
    let readme = st.here.parent().unwrap_or(&st.here).join("README.md");
    rt.substitute(hsm_documents::Kind::Markdown, &readme, &values, Some(MODULE))?;
    rt.print("-> README.md".into())?;
    Ok(())
}

/// `_data(op, **values)` as Python calls it.
fn data_call(rt: &Rt, args: py::Args, mut kwargs: py::Kwargs) -> Result<Val> {
    ensure!(args.len() <= 1, "_data() takes 1 positional argument but {} were given", args.len());
    let named = kwargs.iter().position(|(key, _)| key == "op").map(|i| kwargs.remove(i).1);
    let op = match (args.into_iter().next(), named) {
        (Some(_), Some(_)) => bail!("_data() got multiple values for argument 'op'"),
        (Some(op), None) | (None, Some(op)) => op,
        (None, None) => bail!("_data() missing 1 required positional argument: 'op'"),
    };
    let op = op.str()?;
    let values = kwargs.into_iter().map(|(key, value)| Ok((key, py::plain(&value)?))).collect::<Result<Vec<_>>>()?;
    py::from_json(data(rt, &op, values)?)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("math", rt.import("math")?)?;
    ns.set("sys", rt.import("sys")?)?;
    rt.import("pathlib")?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    ns.set("_here", Val::Path(here.clone()))?;
    let hw = here
        .ancestors()
        .skip(1)
        .find(|p| p.file_name().is_some_and(|name| name == "hardware"))
        .map(Path::to_path_buf)
        .context("StopIteration")?;
    ns.set("_hw", Val::Path(hw.clone()))?;
    for p in [hw.join("scripts"), hw.join("printed-parts").join("valve-seat"), hw.join("reference").join("beduan-solenoid")] {
        ns.set("_p", Val::Path(p.clone()))?;
        py::sys_path_insert(rt, &py::path_str(&p))?;
    }
    let root = here
        .ancestors()
        .skip(1)
        .find(|p| p.join("tools").join("docgen").is_dir())
        .context("StopIteration")?;
    py::sys_path_insert(rt, &py::path_str(&root.join("tools")))?;
    let valve = rt.import("beduan_solenoid")?;
    ns.set("_valve", valve.clone())?;
    let seat = rt.import("valve_seat")?;
    ns.set("_seat", seat.clone())?;
    rt.import("docgen")?;
    ns.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    ns.def(rt, "__getattr__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["name"], &[])?;
        let name = b.req("name")?;
        if interop::eq(&name, &py::s("cq"))? {
            return rt.import("cadquery");
        }
        let module = rt.namespace(MODULE)?.get("__name__")?;
        bail!("module {} has no attribute {}", module.repr()?, name.repr()?)
    })?;
    py::sys_path_insert(rt, &py::path_str(&hw.join("printed-parts/enclosure/enclosure")))?;
    rt.import("_enclosure_data")?;
    ns.set("_read", rt.member("_enclosure_data", "read")?)?;
    ns.def(rt, "_source", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(state(rt)?.source.val())
    })?;

    let source = Source::read(&seat, &valve)?;
    // globals().update(_read('valve-tray-defaults', source=_source())): the reply's key order.
    let defaults = read(rt, json!({"op": "valve-tray-defaults", "source": source.json.clone()}))?;
    for (name, value) in defaults.as_object().context("valve-tray-defaults is a mapping")? {
        ns.set(name, py::from_json(value.clone())?)?;
    }
    let stock_figure = |name: &str| -> Result<Num> { Num::of(&py::from_json(defaults[name].clone())?) };
    let stock = Stock {
        thick: stock_figure("THICK")?,
        margin: stock_figure("MARGIN")?,
        seat: stock_figure("SEAT")?,
        port_slip: stock_figure("PORT_SLIP")?,
    };
    rt.keep(MODULE, State { source, stock, stock_json: defaults, here, valve, seat, body: OnceCell::new() });

    ns.def(rt, "_data", data_call)?;
    ns.def(rt, "reach", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        data_val(rt, "reach", vec![])
    })?;
    ns.def(rt, "height", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["seats"], &[])?;
        let seats = b.opt("seats").unwrap_or_else(|| Val::Tuple(vec![]));
        data_val(rt, "height", vec![("seats", seats)])
    })?;
    ns.def(rt, "wall_root_floors", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["seats"], &[])?;
        let seats = py::plain(&b.req("seats")?)?;
        tuple_of(data(rt, "wall-root-floors", vec![("seats".into(), seats)])?)
    })?;
    ns.def(rt, "port_drop", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        data_val(rt, "port-drop", vec![])
    })?;
    ns.def(rt, "port_channel_depth", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        data_val(rt, "channel-depth", vec![])
    })?;
    ns.def(rt, "extrusion", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["width"], &[])?;
        Ok(extrusion(b.req("width")?))
    })?;
    ns.def(rt, "web", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        web(rt)
    })?;
    ns.def(rt, "grip", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        data_val(rt, "grip", vec![])
    })?;
    ns.def(rt, "build_port_channel", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["length"], &[])?;
        build_port_channel(rt, Num::of(&b.req("length")?)?)
    })?;
    ns.def(rt, "build_body_clearance", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        build_body_clearance(rt)
    })?;
    ns.def(rt, "build_valve_tray", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["width", "seats"], &[])?;
        let width = Num::of(&b.req("width")?)?;
        let seats = seats_of(&b.req("seats")?)?;
        build_valve_tray(rt, width, &seats)
    })?;
    ns.def(rt, "_segment_area", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["radius", "over"], &[])?;
        let (radius, over) = (b.req("radius")?, b.req("over")?);
        data_val(rt, "segment", vec![("radius", radius), ("over", over)])
    })?;
    ns.def(rt, "tray_volume", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["width", "seats"], &[])?;
        let (width, seats) = (b.req("width")?, b.req("seats")?);
        data_val(rt, "volume", vec![("width", width), ("seats", seats)])
    })?;
    ns.def(rt, "channel_floor", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        data_val(rt, "channel-floor", vec![])
    })?;
    ns.def(rt, "depth", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(depth(rt)?.val())
    })?;
    ns.def(rt, "selftest", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Int(selftest(rt)?))
    })?;
    ns.def(rt, "trays_of_machine", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["facts"], &[])?;
        trays_of_machine(&b.req("facts")?)
    })?;
    ns.def(rt, "_socket_numbers", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["x", "y", "shift"], &[])?;
        let (x, y, shift) = (b.req("x")?, b.req("y")?, b.req("shift")?);
        data_val(rt, "sockets", vec![("x", x), ("y", y), ("shift", shift)])
    })?;
    ns.def(rt, "tray_stock_numbers", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["width", "seats"], &[])?;
        let (width, seats) = (b.req("width")?, b.req("seats")?);
        data_val(rt, "stock", vec![("width", width), ("seats", seats)])
    })?;
    ns.def(rt, "numbers", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["trays"], &[])?;
        py::from_json(numbers(rt, &b.req("trays")?)?)
    })?;
    ns.def(rt, "main", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        main(rt)?;
        Ok(Val::None)
    })?;
    Ok(())
}

/// `if __name__ == "__main__":` — the part's own run (`selftest` as its first argument runs the
/// self-test instead).
pub fn main_block(rt: &Rt) -> Result<()> {
    let ns = rt.namespace(MODULE)?;
    let rust_part = rt.import("_rust_part")?;
    ns.set("_rust_part", rust_part.clone())?;
    rust_part.attr("start")?.call(vec![], vec![])?;
    let sys = ns.get("sys")?;
    let argv = py::snapshot(&sys.attr("argv")?)?.iter()?;
    if argv.len() > 1 && interop::eq(&argv[1], &py::s("selftest"))? {
        sys.attr("exit")?.call(vec![Val::Int(selftest(rt)?)], vec![])?;
    }
    main(rt)
}
