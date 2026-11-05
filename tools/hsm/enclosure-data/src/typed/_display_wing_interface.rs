//! Accepted face-up display cover and its receiver in display-local coordinates.
//!
//! X is across the display, Y runs up it, and Z points out of the visible face.
//! The cover back and both wings share a bed plane. Pocket exits follow world
//! print-down so supports leave through the empty display storey.
//!
//! Typed state: the display constants (`_dimensions()['display']`, every one a float), read once
//! at install. `box`, `rounded_prism` and `support_exits` are names `_enclosure_front_top`'s
//! recorder replaces while it calls `cuts`, so every use reads them from the namespace. CadQuery
//! stays a provider (`cq`), reached by callback.
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::Result;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_display_wing_interface";

/// The display constants this module computes with.
#[derive(Clone, Copy, Debug)]
pub struct Display {
    pub angle: f64,
    pub back: f64,
    pub bearing_air: f64,
    pub body_x_air: f64,
    pub body_y_air: f64,
    pub corner_r: f64,
    pub cover_x: f64,
    pub cover_y: f64,
    pub end_air: f64,
    pub glass_seat: f64,
    pub tip_air: f64,
    pub window_r: f64,
    pub window_x: f64,
    pub window_y: f64,
    pub wing_end_r: f64,
    pub wing_reach: f64,
    pub wing_span: f64,
    pub wing_thick: f64,
}

pub struct State {
    pub cq: Val,
    pub d: Display,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("math", rt.import("math")?)?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    ns.set("rounded_prism", rt.member("_swept_top", "rounded_prism")?)?;
    let dimensions = rt.member("_enclosure_data", "dimensions")?;
    ns.set("_dimensions", dimensions.clone())?;
    // globals().update(_dimensions()['display'])
    let display = py::at(&py::snapshot(&py::call(&dimensions, vec![])?)?, "display")?;
    for key in display.iter()? {
        ns.0.set(key.clone(), display.get(key)?)?;
    }
    let f = |key: &str| -> Result<f64> { py::at(&display, key)?.num() };
    let d = Display {
        angle: f("ANGLE")?,
        back: f("BACK")?,
        bearing_air: f("BEARING_AIR")?,
        body_x_air: f("BODY_X_AIR")?,
        body_y_air: f("BODY_Y_AIR")?,
        corner_r: f("CORNER_R")?,
        cover_x: f("COVER_X")?,
        cover_y: f("COVER_Y")?,
        end_air: f("END_AIR")?,
        glass_seat: f("GLASS_SEAT")?,
        tip_air: f("TIP_AIR")?,
        window_r: f("WINDOW_R")?,
        window_x: f("WINDOW_X")?,
        window_y: f("WINDOW_Y")?,
        wing_end_r: f("WING_END_R")?,
        wing_reach: f("WING_REACH")?,
        wing_span: f("WING_SPAN")?,
        wing_thick: f("WING_THICK")?,
    };
    rt.keep(MODULE, State { cq, d });

    ns.def(rt, "box", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["x0", "x1", "y0", "y1", "z0", "z1"], &[])?;
        let [x0, x1, y0, y1, z0, z1] = ["x0", "x1", "y0", "y1", "z0", "z1"].map(|name| b.req(name));
        make_box(rt, [x0?, x1?, y0?, y1?, z0?, z1?])
    })?;
    ns.def(rt, "wing", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["side"], &[])?;
        wing(rt, Num::of(&b.req("side")?)?)
    })?;
    ns.def(rt, "cover", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        cover(rt)
    })?;
    ns.def(rt, "support_exits", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["depth", "inset", "roof_drop"], &[])?;
        let depth = Num::of(&b.req("depth")?)?;
        let inset = Num::of(&b.opt("inset").unwrap_or(Val::Float(0.0)))?;
        let roof_drop = Num::of(&b.opt("roof_drop").unwrap_or(Val::Float(0.0)))?;
        Ok(Val::list(support_exits(rt, depth, inset, roof_drop)?))
    })?;
    ns.def(rt, "cuts", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["pcb_depth", "exit_depth"], &[])?;
        let pcb_depth = Num::of(&b.req("pcb_depth")?)?;
        let exit_depth = b.req("exit_depth")?;
        cuts(rt, pcb_depth, exit_depth)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// `name(*args)` for a name the front-top recorder replaces: read from the namespace now.
fn replaced(rt: &Rt, name: &str, args: Vec<Val>) -> Result<Val> {
    py::call(&rt.namespace(MODULE)?.get(name)?, args)
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

/// One wing, on the `side` of the cover.
pub fn wing(rt: &Rt, side: Num) -> Result<Val> {
    let d = state(rt)?.d;
    let f = Val::Float;
    let blank = replaced(rt, "rounded_prism", vec![f(d.wing_reach + 1.0), f(d.wing_span), f(d.wing_end_r), f(d.back),
        f(d.back + d.wing_thick)])?;
    let x = side.mul(Num::F(d.cover_x / 2.0 + (d.wing_reach - 1.0) / 2.0));
    py::method(&blank, "translate", vec![py::tuple([x.val(), Val::Int(0), Val::Int(0)])])
}

/// The cover: its bezel and both wings, the window cut through.
pub fn cover(rt: &Rt) -> Result<Val> {
    let d = state(rt)?.d;
    let f = Val::Float;
    let bezel = replaced(rt, "rounded_prism", vec![f(d.cover_x), f(d.cover_y), f(d.corner_r), f(d.back), Val::Int(0)])?;
    let window = replaced(rt, "rounded_prism", vec![f(d.window_x), f(d.window_y), f(d.window_r), f(d.back - 1.0),
        Val::Int(1)])?;
    let wings = vec![wing(rt, Num::I(-1))?, wing(rt, Num::I(1))?];
    let body = py::method(&py::method(&bezel, "fuse", wings)?, "cut", vec![window])?;
    py::method(&body, "clean", vec![])
}

/// The two wings' sides across X: `sorted((side*(COVER_X/2-.1), side*(COVER_X/2+WING_REACH+TIP_AIR)))`.
fn wing_span_x(d: &Display, side: f64) -> (f64, f64) {
    let (a, b) = (side * (d.cover_x / 2.0 - 0.1), side * (d.cover_x / 2.0 + d.wing_reach + d.tip_air));
    if b < a { (b, a) } else { (a, b) }
}

/// The wing pockets' support exits, each run `depth` down along world print-down.
pub fn support_exits(rt: &Rt, depth: Num, inset: Num, roof_drop: Num) -> Result<Vec<Val>> {
    let state = state(rt)?;
    let (cq, d) = (&state.cq, state.d);
    let roof = Num::F(d.back + d.wing_thick + d.bearing_air).sub(roof_drop).val();
    let shift_y = depth.neg().mul(Num::F(num::radians(d.angle).tan()));
    let mut exits = vec![];
    for side in [-1.0, 1.0] {
        let (xa, xb) = wing_span_x(&d, side);
        let (xa, xb) = (Num::F(xa).add(inset).val(), Num::F(xb).sub(inset).val());
        let y0 = Num::F(-d.wing_span / 2.0 - d.end_air).add(inset).val();
        let y1 = Num::F(d.wing_span / 2.0 + d.end_air).sub(inset).val();
        let vector = cq.attr("Vector")?;
        let mut corners = vec![];
        for (x, y) in [(&xa, &y0), (&xb, &y0), (&xb, &y1), (&xa, &y1), (&xa, &y0)] {
            corners.push(py::call(&vector, vec![x.clone(), y.clone(), roof.clone()])?);
        }
        let wire = py::call(&cq.attr("Wire")?.attr("makePolygon")?, vec![Val::list(corners)])?;
        let run = py::call(&vector, vec![Val::Int(0), shift_y.val(), depth.neg().val()])?;
        exits.push(py::call(&cq.attr("Solid")?.attr("extrudeLinear")?, vec![wire, Val::list(vec![]), run])?);
    }
    Ok(exits)
}

/// The receiver: the cover's inset, the glass seat, the PCB pocket, both wing pockets and their
/// support exits.
pub fn cuts(rt: &Rt, pcb_depth: Num, exit_depth: Val) -> Result<Val> {
    let d = state(rt)?.d;
    let f = Val::Float;
    let inset = replaced(rt, "rounded_prism", vec![f(d.cover_x + 2.0 * d.body_x_air), f(d.cover_y + 2.0 * d.body_y_air),
        f(d.corner_r + d.body_y_air), f(d.back), Val::Int(1)])?;
    let glass = replaced(rt, "rounded_prism", vec![f(113.8), f(77.3), f(2.65), f(d.glass_seat), Val::Int(1)])?;
    let pcb = replaced(rt, "box", vec![f(0.5 - 106.3 / 2.0), f(0.5 + 106.3 / 2.0), f(-1.0 - 69.3 / 2.0),
        f(-1.0 + 69.3 / 2.0), pcb_depth.neg().val(), Val::Int(1)])?;
    let mut result = py::method(&inset, "fuse", vec![glass, pcb])?;
    for side in [-1.0, 1.0] {
        let (xa, xb) = wing_span_x(&d, side);
        let pocket = replaced(rt, "box", vec![f(xa), f(xb), f(-d.wing_span / 2.0 - d.end_air),
            f(d.wing_span / 2.0 + d.end_air), f(d.back), f(d.back + d.wing_thick + d.bearing_air)])?;
        result = py::method(&result, "fuse", vec![pocket])?;
    }
    let exits = replaced(rt, "support_exits", vec![exit_depth])?.iter()?;
    py::method(&py::method(&result, "fuse", exits)?, "clean", vec![])
}
