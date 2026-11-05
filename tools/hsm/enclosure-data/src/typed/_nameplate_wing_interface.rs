//! Accepted face-up nameplate wings and receiver, in the plate X/Y/Z frame.
//!
//! Typed state: the plate constants (`_dimensions()['nameplate']`, every one a float) are read
//! once at install. CadQuery stays a provider (`cq`); `box` is `_nameplate_interface.box`, the same
//! function object.
use super::_nameplate_interface::{self as interface, m, mk, rotate_x, sorted2, update};
use super::num::Num;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::Result;
use std::path::Path;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_nameplate_wing_interface";

/// `_dimensions()['nameplate']`.
#[derive(Clone, Copy, Debug)]
pub struct Plate {
    pub back_air: f64,
    pub corner_r: f64,
    pub east_backing: f64,
    pub east_relief_start: f64,
    pub end_air: f64,
    pub end_radius: f64,
    pub entry_bevel_depth: f64,
    pub entry_bevel_width: f64,
    pub face_slip: f64,
    pub face_x_air: f64,
    pub floor_stock: f64,
    pub height: f64,
    pub projection: f64,
    pub runout_lead: f64,
    pub supported_end_air: f64,
    pub thick: f64,
    pub thickness_air: f64,
    pub tip_air: f64,
    pub width: f64,
    pub wing_span: f64,
    pub wing_thick: f64,
}

pub struct State {
    pub cq: Val,
    pub plate: Plate,
    /// `dimensions.CORNER_R` at definition: `apply`'s default `corner_radius`.
    face_corner: Num,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// `apply`'s keyword arguments.
#[derive(Clone, Copy, Debug)]
pub struct ApplyOpts {
    pub supported: Num,
    pub up: Num,
    pub width: Num,
    pub height: Num,
    pub wing_span: Num,
    pub wall_face: Option<Num>,
    pub access: bool,
    pub runout_lead: Num,
    pub end_margin: Num,
    pub crown_face: Option<Num>,
    pub corner_radius: Num,
}
impl ApplyOpts {
    /// The defaults `apply` binds.
    pub fn defaults(rt: &Rt) -> Result<ApplyOpts> {
        let state = state(rt)?;
        let p = state.plate;
        Ok(ApplyOpts {
            supported: Num::F(p.supported_end_air),
            up: Num::I(-1),
            width: Num::F(p.width),
            height: Num::F(p.height),
            wing_span: Num::F(p.wing_span),
            wall_face: None,
            access: true,
            runout_lead: Num::F(0.0),
            end_margin: Num::F(2.0),
            crown_face: None,
            corner_radius: state.face_corner,
        })
    }
}

/// A station's `x` and `z`, as `apply`, `production_backing` and `plain_lips` read them.
pub fn station_xz(station: &Val) -> Result<(Num, Num)> {
    Ok((Num::of(&station.attr("x")?)?, Num::of(&station.attr("z")?)?))
}
/// An optional number: `None` where Python passes `None`.
fn optional(value: Option<Val>) -> Result<Option<Num>> {
    match value {
        None | Some(Val::None) => Ok(None),
        Some(v) => Ok(Some(Num::of(&v)?)),
    }
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("math", rt.import("math")?)?;
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    // HERE = Path(__file__).resolve().parent
    let here = parent(&py::resolve(&py::path(&ns.get("__file__")?)?)?);
    ns.set("HERE", Val::Path(here.clone()))?;
    py::sys_path_insert(rt, &py::path_str(&here))?;
    let cadlib = here.ancestors().nth(2).unwrap_or(here.as_path()).join("cadlib");
    py::sys_path_insert(rt, &py::path_str(&cadlib))?;
    let dimensions = rt.import("_nameplate_interface")?;
    ns.set("dimensions", dimensions.clone())?;
    ns.set("fits", rt.import("fits")?)?;
    let values = rt.member("_enclosure_data", "dimensions")?;
    ns.set("_dimensions", values.clone())?;
    // globals().update(_dimensions()['nameplate'])
    let values = py::snapshot(&py::call(&values, vec![])?)?;
    let plate = py::at(&values, "nameplate")?;
    update(ns, &plate)?;
    ns.set("box", dimensions.attr("box")?)?;
    let f = |key: &str| -> Result<f64> { py::at(&plate, key)?.num() };
    let plate = Plate {
        back_air: f("BACK_AIR")?,
        corner_r: f("CORNER_R")?,
        east_backing: f("EAST_BACKING")?,
        east_relief_start: f("EAST_RELIEF_START")?,
        end_air: f("END_AIR")?,
        end_radius: f("END_RADIUS")?,
        entry_bevel_depth: f("ENTRY_BEVEL_DEPTH")?,
        entry_bevel_width: f("ENTRY_BEVEL_WIDTH")?,
        face_slip: f("FACE_SLIP")?,
        face_x_air: f("FACE_X_AIR")?,
        floor_stock: f("FLOOR_STOCK")?,
        height: f("HEIGHT")?,
        projection: f("PROJECTION")?,
        runout_lead: f("RUNOUT_LEAD")?,
        supported_end_air: f("SUPPORTED_END_AIR")?,
        thick: f("THICK")?,
        thickness_air: f("THICKNESS_AIR")?,
        tip_air: f("TIP_AIR")?,
        width: f("WIDTH")?,
        wing_span: f("WING_SPAN")?,
        wing_thick: f("WING_THICK")?,
    };
    let face_corner = Num::of(&dimensions.attr("CORNER_R")?)?;
    rt.keep(MODULE, State { cq, plate, face_corner });

    let (width, span) = (Num::F(plate.width), Num::F(plate.wing_span));
    ns.def(rt, "wings", move |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &[], &["width", "span"])?;
        let width = b.opt("width").map(|v| Num::of(&v)).transpose()?.unwrap_or(width);
        let span = b.opt("span").map(|v| Num::of(&v)).transpose()?.unwrap_or(span);
        Ok(Val::list(wings(rt, width, span)?))
    })?;
    let (height, thick) = (Num::F(plate.height), Num::F(plate.thick));
    ns.def(rt, "blank", move |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &[], &["width", "height", "thick"])?;
        let width = b.opt("width").map(|v| Num::of(&v)).transpose()?.unwrap_or(width);
        let height = b.opt("height").map(|v| Num::of(&v)).transpose()?.unwrap_or(height);
        let thick = b.opt("thick").map(|v| Num::of(&v)).transpose()?.unwrap_or(thick);
        blank(rt, width, height, thick)
    })?;
    ns.def(rt, "apply", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["solid", "station", "y_outer"], &["supported", "up", "width",
            "height", "wing_span", "wall_face", "access", "runout_lead", "end_margin", "crown_face",
            "corner_radius"])?;
        let solid = b.req("solid")?;
        let station = b.req("station")?;
        let y_outer = Num::of(&b.req("y_outer")?)?;
        let mut o = ApplyOpts::defaults(rt)?;
        let num = |v: Option<Val>, default: Num| -> Result<Num> {
            v.map(|v| Num::of(&v)).transpose().map(|v| v.unwrap_or(default))
        };
        o.supported = num(b.opt("supported"), o.supported)?;
        o.up = num(b.opt("up"), o.up)?;
        o.width = num(b.opt("width"), o.width)?;
        o.height = num(b.opt("height"), o.height)?;
        o.wing_span = num(b.opt("wing_span"), o.wing_span)?;
        o.wall_face = optional(b.opt("wall_face"))?;
        o.access = b.bool_or("access", true)?;
        o.runout_lead = num(b.opt("runout_lead"), o.runout_lead)?;
        o.end_margin = num(b.opt("end_margin"), o.end_margin)?;
        o.crown_face = optional(b.opt("crown_face"))?;
        o.corner_radius = num(b.opt("corner_radius"), o.corner_radius)?;
        apply(rt, solid, station_xz(&station)?, y_outer, &o)
    })?;
    ns.def(rt, "receiver", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        receiver(rt)
    })?;
    ns.def(rt, "production_backing", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["solid", "station", "y_outer"], &["wall_face", "column"])?;
        let solid = b.req("solid")?;
        let station = b.req("station")?;
        let y_outer = Num::of(&b.req("y_outer")?)?;
        let wall_face = optional(b.opt("wall_face"))?;
        let column = match b.opt("column") {
            None | Some(Val::None) => None,
            Some(column) => Some(column),
        };
        production_backing(rt, solid, &station, y_outer, wall_face, column.as_ref())
    })?;
    ns.def(rt, "plain_lips", move |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["station", "y_outer"], &["width", "wing_span"])?;
        let station = station_xz(&b.req("station")?)?;
        let y_outer = Num::of(&b.req("y_outer")?)?;
        let width = b.opt("width").map(|v| Num::of(&v)).transpose()?.unwrap_or(width);
        let wing_span = b.opt("wing_span").map(|v| Num::of(&v)).transpose()?.unwrap_or(span);
        Ok(lips_val(&plain_lips(rt, station, y_outer, width, wing_span)?))
    })?;
    Ok(())
}

/// `path.parent`, as the runtime's `Path` gives it.
pub(crate) fn parent(path: &Path) -> std::path::PathBuf {
    path.parent().unwrap_or(path).to_owned()
}

/// The full-height roots overlap the plate; both wings begin at back Y=0.
pub fn wings(rt: &Rt, width: Num, span: Num) -> Result<Vec<Val>> {
    let state = state(rt)?;
    let (cq, p) = (&state.cq, &state.plate);
    let mut parts = vec![];
    for side in [-1i64, 1] {
        let sketch = m(&py::call(&cq.attr("Workplane")?, vec![py::s("XY")])?, "rect",
            vec![Val::Float(p.projection + 1.), span.val()])?;
        let wing = m(&m(&m(&sketch, "extrude", vec![Val::Float(p.wing_thick)])?, "edges", vec![py::s("|Z")])?,
            "fillet", vec![Val::Float(p.end_radius)])?;
        let wing = rotate_x(&m(&wing, "val", vec![])?, -90)?;
        let offset = Num::I(side).mul(width.div(Num::I(2)).add(Num::F((p.projection - 1.) / 2.)));
        parts.push(m(&wing, "translate", vec![py::tuple([offset, Num::I(0), Num::I(0)])])?);
    }
    Ok(parts)
}

pub fn blank(rt: &Rt, width: Num, height: Num, thick: Num) -> Result<Val> {
    let state = state(rt)?;
    let (cq, p) = (&state.cq, &state.plate);
    let sketch = m(&py::call(&cq.attr("Workplane")?, vec![py::s("XY")])?, "rect", vec![width.val(), height.val()])?;
    let plate = m(&m(&m(&m(&sketch, "extrude", vec![thick.val()])?, "edges", vec![py::s("|Z")])?, "fillet",
        vec![Val::Float(p.corner_r)])?, "val", vec![])?;
    let plate = rotate_x(&plate, -90)?;
    let parts = wings(rt, width, Num::F(p.wing_span))?;
    m(&m(&plate, "fuse", parts)?, "clean", vec![])
}

/// Flush plate pocket and two sideways slots; no cantilevers behind the face.
///
/// Body X has 0.15 mm per side; Z uses the shared static allowance.
/// Nonlocating wing tips have 0.30 mm centered X clearance, retaining
/// 0.15 mm at maximum body travel. The plate back and wing
/// undersides have static clearance from their receiving floors. The Y slot has
/// 0.45 mm of local relief above the nominal wing. Its walls print vertically,
/// so only the print-down mouth and slot ends receive the extra
/// supported-surface allowance. This hand-inserted plate has no low-force fit.
///
/// `end_margin` is the pad's stock past the mouth's print-up end. Given the host's show face
/// `crown_face`, the pad's print-down end, where it stands proud of that face, runs out to it
/// at 45 degrees, so the pad's first layers grow off the wall rather than hang off it.
pub fn apply(rt: &Rt, solid: Val, station: (Num, Num), y_outer: Num, o: &ApplyOpts) -> Result<Val> {
    let state = state(rt)?;
    let (cq, p) = (&state.cq, &state.plate);
    let two = Num::I(2);
    let f = Num::F;
    let floor = y_outer.sub(f(p.thick));
    let shift = py::tuple([station.0, floor, station.1]);
    let (pw, ph) = (o.width.add(two.mul(f(p.face_slip))), o.height.add(two.mul(f(p.face_slip))));
    // Keep the full floor section behind the body, and `runout_lead` past its print-down
    // edge, before the run-out. The opposite end retains `end_margin`.
    let runout_margin = f(2.0).max(f(p.floor_stock).add(o.runout_lead));
    // On a base wall the east end runs square into its hidden relief
    // (`production_backing`); a corner round there leaves only a sliver.
    let rounds = if o.wall_face.is_none() { "|Z" } else { "|Z and <X" };
    let workplane = |plane: &str| py::call(&cq.attr("Workplane")?, vec![py::s(plane)]);
    let yz = || mk(&cq.attr("Workplane")?, "__call__", vec![py::s("YZ")],
        vec![("origin", py::tuple([pw.neg(), Num::I(0), Num::I(0)]))]);
    let sketch = m(&workplane("XY")?, "rect", vec![pw.add(two.mul(f(p.projection).add(two))).val(),
        ph.add(o.end_margin).add(runout_margin).val()])?;
    let pad = m(&m(&m(&m(&sketch, "extrude", vec![Val::Float(p.floor_stock + p.back_air + p.thick)])?, "edges",
        vec![py::s(rounds)])?, "fillet", vec![o.corner_radius.add(two).val()])?, "val", vec![])?;
    let pad = m(&rotate_x(&pad, -90)?, "translate", vec![py::tuple([Num::I(0), f(-p.floor_stock - p.back_air),
        o.up.neg().mul(runout_margin.sub(o.end_margin)).div(two)])])?;
    // A 45-degree inboard run-out carries the added pocket floor in the wall pose.
    let zedge = o.up.neg().mul(ph.div(two).add(runout_margin));
    let section = Val::list(vec![
        py::tuple([f(-p.floor_stock - p.back_air), zedge]),
        py::tuple([f(-p.floor_stock - p.back_air), zedge.add(o.up.mul(f(p.floor_stock)))]),
        py::tuple([f(-p.back_air), zedge]),
    ]);
    let ramp = m(&m(&m(&m(&yz()?, "polyline", vec![section])?, "close", vec![])?, "extrude",
        vec![two.mul(pw).val()])?, "val", vec![])?;
    let mut pad = m(&pad, "cut", vec![ramp])?;
    if let Some(wall_face) = o.wall_face {
        // The opposite pad end meets the base wall on a 45-degree plane.
        // Cut the pad alone so existing host feet keep their complete profiles.
        let (rear, wall_y) = (f(-p.floor_stock - p.back_air), wall_face.sub(floor));
        let run = wall_y.sub(rear);
        if run.f() > 0. {
            let end = o.up.mul(ph.div(two).add(o.end_margin));
            let section = Val::list(vec![
                py::tuple([rear, end]),
                py::tuple([wall_y, end]),
                py::tuple([rear, end.sub(o.up.mul(run))]),
            ]);
            let finish = m(&m(&m(&m(&yz()?, "polyline", vec![section])?, "close", vec![])?, "extrude",
                vec![two.mul(pw).val()])?, "val", vec![])?;
            pad = m(&pad, "cut", vec![finish])?;
        }
    }
    if let Some(crown_face) = o.crown_face.filter(|crown_face| y_outer.f() > crown_face.f()) {
        let proud = y_outer.sub(crown_face);
        let hundredth = f(0.01);
        let section = Val::list(vec![
            py::tuple([f(p.thick).sub(proud).sub(hundredth), zedge.sub(o.up.mul(hundredth))]),
            py::tuple([f(p.thick + 0.01), zedge.sub(o.up.mul(hundredth))]),
            py::tuple([f(p.thick + 0.01), zedge.add(o.up.mul(proud.add(hundredth)))]),
        ]);
        let crown = m(&m(&m(&m(&yz()?, "polyline", vec![section])?, "close", vec![])?, "extrude",
            vec![two.mul(pw).val()])?, "val", vec![])?;
        pad = m(&pad, "cut", vec![crown])?;
    }
    let mut solid = m(&solid, "fuse", vec![m(&pad, "translate", vec![shift.clone()])?])?;
    let sketch = m(&workplane("XY")?, "rect", vec![o.width.add(two.mul(f(p.face_x_air))).val(), ph.val()])?;
    let mouth = m(&m(&m(&m(&sketch, "extrude", vec![Val::Float(p.thick + 1. + p.back_air)])?, "edges",
        vec![py::s("|Z")])?, "fillet", vec![o.corner_radius.add(f(p.face_slip)).val()])?, "val", vec![])?;
    let mouth = m(&rotate_x(&mouth, -90)?, "translate", vec![py::tuple([Num::I(0), f(-p.back_air), Num::I(0)])])?;
    // The print-down mouth edge gets the same rough-surface allowance as the
    // slot end; otherwise that edge can bind before the wings are seated.
    let lifted = m(&mouth, "translate", vec![py::tuple([Num::I(0), Num::I(0), o.up.mul(o.supported)])])?;
    let mouth = m(&mouth, "fuse", vec![lifted])?;
    solid = m(&solid, "cut", vec![m(&mouth, "translate", vec![shift.clone()])?])?;
    let z0 = o.wing_span.neg().div(two).sub(f(p.end_air)).add(Num::I(0).min(o.up.mul(o.supported)));
    let z1 = o.wing_span.div(two).add(f(p.end_air)).add(Num::I(0).max(o.up.mul(o.supported)));
    for side in [-1i64, 1] {
        let s = Num::I(side);
        let (xa, xb) = sorted2(s.mul(o.width.div(two).sub(f(0.1))).f(),
            s.mul(o.width.div(two).add(f(p.projection)).add(f(p.tip_air))).f());
        let slot = interface::make_box_n(rt, [f(xa), f(xb), f(-p.back_air), f(p.wing_thick + p.thickness_air), z0, z1])?;
        solid = m(&solid, "cut", vec![m(&slot, "translate", vec![shift.clone()])?])?;
        // Entry bevel clears the rotating wing during hand-bent insertion.
        // The outer flat bearing retains the trial thickness gap.
        // The bevel follows the slot roof with its width and slope fixed.
        let mouth_x = o.width.div(two).add(f(p.face_slip));
        let roof_y = p.wing_thick + p.thickness_air;
        let plane = mk(&workplane("XY")?, "workplane", vec![], vec![("offset", z0.val())])?;
        let section = Val::list(vec![
            py::tuple([s.mul(mouth_x), f(roof_y)]),
            py::tuple([s.mul(mouth_x.add(f(p.entry_bevel_width))), f(roof_y)]),
            py::tuple([s.mul(mouth_x), f(roof_y + p.entry_bevel_depth)]),
        ]);
        let lead = m(&m(&m(&m(&plane, "polyline", vec![section])?, "close", vec![])?, "extrude",
            vec![z1.sub(z0).val()])?, "val", vec![])?;
        solid = m(&solid, "cut", vec![m(&lead, "translate", vec![shift.clone()])?])?;
    }
    // Back access permits pushing the centre outward to release the wings.
    // Its diamond ceiling is self-supporting in the enclosure wall orientation.
    // A plate with its own opening is released through it and takes no diamond.
    if o.access {
        let outline = Val::list(vec![
            py::tuple([Val::Int(-9), Val::Int(0)]),
            py::tuple([Val::Int(0), Val::Int(10)]),
            py::tuple([Val::Int(9), Val::Int(0)]),
            py::tuple([Val::Int(0), Val::Int(-10)]),
        ]);
        let diamond = m(&m(&m(&m(&workplane("XY")?, "polyline", vec![outline])?, "close", vec![])?, "extrude",
            vec![Val::Float(p.floor_stock + p.back_air + 1.)])?, "val", vec![])?;
        let diamond = m(&rotate_x(&diamond, -90)?, "translate",
            vec![py::tuple([Val::Int(0), Val::Float(-p.floor_stock - p.back_air - 0.5), Val::Int(0)])])?;
        solid = m(&solid, "cut", vec![m(&diamond, "translate", vec![shift])?])?;
    }
    m(&solid, "clean", vec![])
}

pub fn receiver(rt: &Rt) -> Result<Val> {
    let p = state(rt)?.plate;
    let shell = interface::make_box_n(rt, [
        Num::F(-p.width / 2. - p.projection - 3.),
        Num::F(p.width / 2. + p.projection + 3.),
        Num::F(p.thick - 3.),
        Num::F(p.thick),
        Num::F(-p.height / 2. - 4.),
        Num::F(p.height / 2. + 4.),
    ])?;
    let station = interface::station(rt, Num::I(0), Num::I(0))?;
    let mut o = ApplyOpts::defaults(rt)?;
    o.corner_radius = Num::F(p.corner_r);
    apply(rt, shell, (station.x, station.z), Num::F(p.thick), &o)
}

/// Relieve the hidden east backing, with run-outs beyond the complete pad.
///
/// Given the room's corner `column` as `(x, y, radius)`, the relief runs to it and ends
/// on the column's own round.
pub fn production_backing(rt: &Rt, solid: Val, station: &Val, y_outer: Num, wall_face: Option<Num>,
    column: Option<&Val>) -> Result<Val> {
    let state = state(rt)?;
    let (cq, p) = (&state.cq, &state.plate);
    let f = Num::F;
    let (xa, mut xb) = (f(p.east_relief_start), f(p.width / 2. + p.projection + 4.));
    if let Some(column) = column {
        xb = Num::of(&column.get(Val::Int(0))?)?.sub(Num::of(&station.attr("x")?)?);
    }
    let (ya, yb) = (f(-p.floor_stock - p.back_air - 1.), f(-p.east_backing - p.back_air));
    let (za, zb) = (f(-p.height / 2. - 5.), f(p.height / 2. + 5.));
    let mut keepout = interface::make_box_n(rt, [xa, xb, ya, yb, za, zb])?;
    if let Some(wall_face) = wall_face {
        let wall_y = wall_face.sub(y_outer.sub(f(p.thick)));
        let run = yb.sub(wall_y);
        if run.f() > 0. {
            // Only the shallow bite into the base wall runs out. Both triangles
            // lie beyond the existing full pad/body/wing relief footprint.
            for profile in [
                [(wall_y, za.sub(run)), (yb, za), (wall_y, za)],
                [(wall_y, zb), (yb, zb), (wall_y, zb.add(run))],
            ] {
                let profile = Val::Tuple(profile.iter().map(|&(y, z)| py::tuple([y, z])).collect());
                let plane = mk(&cq.attr("Workplane")?, "__call__", vec![py::s("YZ")],
                    vec![("origin", py::tuple([xa, Num::I(0), Num::I(0)]))])?;
                let end = m(&m(&m(&m(&plane, "polyline", vec![profile])?, "close", vec![])?, "extrude",
                    vec![xb.sub(xa).val()])?, "val", vec![])?;
                keepout = m(&keepout, "fuse", vec![end])?;
            }
        }
    }
    // The relief's west end is a 45-degree face from the pad's back at EAST_RELIEF_START to
    // its full depth, so the body's backing ends without a step as tall as the relief is deep.
    let rear = f(-p.floor_stock - p.back_air);
    let plane = mk(&py::call(&cq.attr("Workplane")?, vec![py::s("XY")])?, "workplane", vec![],
        vec![("offset", za.sub(f(p.height)).val())])?;
    let section = Val::list(vec![
        py::tuple([xa, rear]),
        py::tuple([xa.add(yb).sub(rear), yb]),
        py::tuple([xa, yb]),
    ]);
    let head = m(&m(&m(&m(&plane, "polyline", vec![section])?, "close", vec![])?, "extrude",
        vec![zb.sub(za).add(Num::I(2).mul(f(p.height))).val()])?, "val", vec![])?;
    keepout = m(&keepout, "cut", vec![head])?;
    let (x, z) = station_xz_at(station)?;
    keepout = m(&keepout, "translate", vec![Val::Tuple(vec![x, y_outer.sub(f(p.thick)).val(), z])])?;
    if let Some(column) = column {
        let parts = py::unpack(column, 3)?;
        let z = Num::of(&station.attr("z")?)?;
        let corner = py::call(&cq.attr("Vector")?, vec![parts[0].clone(), parts[1].clone(),
            z.sub(f(1.5).mul(f(p.height))).val()])?;
        let axis = py::call(&cq.attr("Vector")?, vec![Val::Int(0), Val::Int(0), Val::Int(1)])?;
        let cylinder = py::call(&cq.attr("Solid")?.attr("makeCylinder")?, vec![parts[2].clone(),
            Num::I(3).mul(f(p.height)).val(), corner, axis])?;
        keepout = m(&keepout, "cut", vec![cylinder])?;
    }
    m(&m(&solid, "cut", vec![keepout])?, "clean", vec![])
}

/// `(station.x, station.z)` as values.
fn station_xz_at(station: &Val) -> Result<(Val, Val)> {
    Ok((station.attr("x")?, station.attr("z")?))
}

/// Preserve the coupon's complete retaining thickness through the show flutes.
pub fn plain_lips(rt: &Rt, station: (Num, Num), y_outer: Num, width: Num, wing_span: Num) -> Result<[[Num; 6]; 2]> {
    let p = state(rt)?.plate;
    let (two, f) = (Num::I(2), Num::F);
    let mut fields = [[Num::I(0); 6]; 2];
    for (i, side) in [-1i64, 1].into_iter().enumerate() {
        let s = Num::I(side);
        let (x0, x1) = sorted2(s.mul(width.div(two).add(f(p.face_x_air))).f(),
            s.mul(width.div(two).add(f(p.projection)).add(f(p.tip_air))).f());
        let (x, z) = station;
        fields[i] = [
            x.add(f(x0)).sub(f(0.4)),
            x.add(f(x1)).add(f(0.4)),
            y_outer.sub(f(p.thick)).sub(f(p.back_air)),
            y_outer.add(Num::I(1)),
            z.sub(wing_span.div(two)).sub(f(p.end_air)).sub(f(p.supported_end_air)).sub(f(0.4)),
            z.add(wing_span.div(two)).add(f(p.end_air)).add(f(0.4)),
        ];
    }
    Ok(fields)
}

/// `plain_lips`' value: a tuple of two 6-tuples.
pub fn lips_val(fields: &[[Num; 6]]) -> Val {
    Val::Tuple(fields.iter().map(|row| Num::vals(row)).collect())
}
