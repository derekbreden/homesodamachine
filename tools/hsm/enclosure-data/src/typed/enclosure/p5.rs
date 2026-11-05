//! Part 5 of `enclosure`: the functions whose first Python line is in 6596–8543 — the tube
//! anchors and their capped ribs, the C14 tunnel and the keystone receptacle, the piece builder,
//! the build's reports and the bounds it reads off the built pieces, the stated box, its pages,
//! and the tools the box questions measure.
//!
//! Every function is the Python function of the same name, typed. Solids are [`Solid`] (the
//! construction-graph API of `_enclosure_panel`). The geometry leaves and the 29 slots, `cq`,
//! `record_bound`, `_teardrop_y` and `_flank_vents` are read from the namespace at every use, and
//! so are the functions of the provider modules (`_anchor_cap`, `_keystone`, `_data_fit`, `_dock`,
//! `_swept_top`, `_route_snaps`, `_fixed_pump_mount`, `_funnel_frame_part`, ...), which the
//! recorders replace while they run. A station a pack hands in is read once into a [`Station`];
//! the slots receive its vectors as they were handed in.
#![allow(non_snake_case, non_upper_case_globals, dead_code, unused_imports, unused_variables)]
use super::{Cx, State};
use crate::typed::_enclosure_panel::{self as panel, Solid};
use crate::typed::num::{self, Num};
use crate::typed::py::{self, Args, Kwargs, Py, Tup, Val};
use anyhow::{Context, Result, bail, ensure};
use hsm_documents::interop;
use std::rc::Rc;

/// The functions of this part that run typed: the hybrid build replaces exactly these.
pub const CONVERTED: &[&str] = &[
    "tube_anchor_tie_loop",
    "_anchor_plane",
    "tube_anchor_end_columns",
    "tube_anchor_corbel_depth",
    "tube_anchor_end_corbel_bounds",
    "back_top_frames",
    "back_top_owns",
    "_tube_anchors",
    "anchor_capped",
    "_capped_anchor",
    "_c14_aperture",
    "_c14_tunnel_geometry",
    "keystone_pocket_width",
    "_keystone_pocket_cut",
    "_keystone_catches",
    "_keystone_receptacle_geometry",
    "_keystone_receptacle",
    "_c14_tunnel",
    "y_stack_figures",
    "_report_bounds",
    "_box_question_frame",
    "_lip_lane_boxes",
    "_lip_lane_tool",
    "_under_lip_tool",
    "main",
];

// --- the Python boundary ------------------------------------------------------------------------

/// A typed function of this part as the namespace holds it: Python arguments in, Python values out.
fn wrap(cx: &Rc<Cx>, f: impl Fn(&Cx, Args, Kwargs) -> Result<Val> + 'static) -> Result<Val> {
    let held = cx.clone();
    Ok(cx.ns.function(&cx.rt, move |_rt, args, kwargs| f(&held, args, kwargs)))
}
/// A required parameter, converted.
fn req<T: Py>(b: &mut py::Bound, name: &str) -> Result<T> {
    let value = b.req(name)?;
    T::from_py(&value).with_context(|| format!("argument {name}"))
}
/// A parameter with a default, converted when given.
fn opt<T: Py>(b: &mut py::Bound, name: &str, default: T) -> Result<T> {
    match b.opt(name) {
        Some(value) => T::from_py(&value).with_context(|| format!("argument {name}")),
        None => Ok(default),
    }
}

/// A function of this part as a Python-callable value: its wrapper binds the Python signature
/// (positional names, defaults, keyword-only parameters), converts the arguments, calls the typed
/// function and converts its result.
pub fn function(cx: &Rc<Cx>, name: &str) -> Option<Result<Val>> {
    let f = match name {
        "tube_anchor_tie_loop" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["seat_r"], &[])?;
            tube_anchor_tie_loop(cx, req(&mut b, "seat_r")?)?.to_py()
        }),
        "_anchor_plane" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["origin", "u", "n"], &[])?;
            let (origin, u, n) = (b.req("origin")?, b.req("u")?, b.req("n")?);
            _anchor_plane(cx, &origin, &u, &n)
        }),
        "tube_anchor_end_columns" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["station", "roots", "lane", "up", "face_z", "depth"], &[])?;
            let station = b.req("station")?;
            let roots: [Num; 6] = req(&mut b, "roots")?;
            let lane: [Num; 6] = req(&mut b, "lane")?;
            let up = req(&mut b, "up")?;
            let face_z = req(&mut b, "face_z")?;
            let depth = opt(&mut b, "depth", None)?;
            tube_anchor_end_columns(cx, &station, &roots, &lane, up, face_z, depth)?.to_py()
        }),
        "tube_anchor_corbel_depth" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["station", "roots", "lane"], &[])?;
            let station = b.req("station")?;
            let roots: [Num; 6] = req(&mut b, "roots")?;
            let lane: [Num; 6] = req(&mut b, "lane")?;
            tube_anchor_corbel_depth(cx, &station, &roots, &lane)?.to_py()
        }),
        "tube_anchor_end_corbel_bounds" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["station", "roots", "lane", "up"], &[])?;
            let station = b.req("station")?;
            let roots: [Num; 6] = req(&mut b, "roots")?;
            let lane: [Num; 6] = req(&mut b, "lane")?;
            let up = req(&mut b, "up")?;
            tube_anchor_end_corbel_bounds(cx, &station, &roots, &lane, up)?.to_py()
        }),
        "back_top_frames" => wrap(cx, |cx, args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            back_top_frames(cx)?.to_py()
        }),
        "back_top_owns" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["point"], &[])?;
            let point = b.req("point")?;
            back_top_owns(cx, &py::f64s(&point)?)?.to_py()
        }),
        "_tube_anchors" => wrap(cx, |cx, args, kwargs| {
            let names = ["solid", "roots", "lane", "stations", "y0", "y1", "z0", "z1", "up"];
            let mut b = py::bind(args, kwargs, &names, &[])?;
            let solid = req(&mut b, "solid")?;
            let roots: [Num; 6] = req(&mut b, "roots")?;
            let lane: [Num; 6] = req(&mut b, "lane")?;
            let stations = b.req("stations")?;
            let (y0, y1, z0, z1) = (req(&mut b, "y0")?, req(&mut b, "y1")?, req(&mut b, "z0")?, req(&mut b, "z1")?);
            let up = opt(&mut b, "up", Num::F(1.0))?;
            _tube_anchors(cx, solid, &roots, &lane, &stations, y0, y1, z0, z1, up)?.to_py()
        }),
        "anchor_capped" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["station"], &[])?;
            anchor_capped(cx, &b.req("station")?)?.to_py()
        }),
        "_capped_anchor" => wrap(cx, |cx, args, kwargs| {
            let names = ["solid", "station", "b_face", "roots", "lane", "y0", "y1", "z0", "z1", "up"];
            let mut b = py::bind(args, kwargs, &names, &[])?;
            let solid = req(&mut b, "solid")?;
            let station = b.req("station")?;
            let b_face = req(&mut b, "b_face")?;
            let roots: [Num; 6] = req(&mut b, "roots")?;
            let lane: [Num; 6] = req(&mut b, "lane")?;
            let (y0, y1, z0, z1) = (req(&mut b, "y0")?, req(&mut b, "y1")?, req(&mut b, "z0")?, req(&mut b, "z1")?);
            let up = req(&mut b, "up")?;
            _capped_anchor(cx, solid, &station, b_face, &roots, &lane, y0, y1, z0, z1, up)?.to_py()
        }),
        "_c14_aperture" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["stations", "ports"], &[])?;
            let (stations, ports) = (b.req("stations")?, b.req("ports")?);
            _c14_aperture(cx, &stations, &ports)?.to_py()
        }),
        "_c14_tunnel_geometry" => wrap(cx, |cx, args, kwargs| {
            let names = ["inner", "outer", "stations", "ports", "z0", "z1", "up"];
            let mut b = py::bind(args, kwargs, &names, &[])?;
            let inner: [f64; 6] = req(&mut b, "inner")?;
            let outer: [f64; 6] = req(&mut b, "outer")?;
            let (stations, ports) = (b.req("stations")?, b.req("ports")?);
            let (z0, z1) = (req(&mut b, "z0")?, req(&mut b, "z1")?);
            let up = opt(&mut b, "up", Num::F(1.0))?;
            _c14_tunnel_geometry(cx, &inner, &outer, &stations, &ports, z0, z1, up)?.to_py()
        }),
        "keystone_pocket_width" => wrap(cx, |cx, args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            keystone_pocket_width(cx)?.to_py()
        }),
        "_keystone_pocket_cut" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["x", "z", "y_face", "back"], &[])?;
            let (x, z, y_face) = (req(&mut b, "x")?, req(&mut b, "z")?, req(&mut b, "y_face")?);
            let back = opt(&mut b, "back", None)?;
            _keystone_pocket_cut(cx, x, z, y_face, back)?.to_py()
        }),
        "_keystone_catches" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["catches", "up"], &[])?;
            let catches = req(&mut b, "catches")?;
            _keystone_catches(cx, catches, req(&mut b, "up")?)?.to_py()
        }),
        "_keystone_receptacle_geometry" => wrap(cx, |cx, args, kwargs| {
            let names = ["inner", "outer", "station", "z0", "z1", "up"];
            let mut b = py::bind(args, kwargs, &names, &[])?;
            let inner: [f64; 6] = req(&mut b, "inner")?;
            let outer: [f64; 6] = req(&mut b, "outer")?;
            let station = b.req("station")?;
            let (z0, z1) = (req(&mut b, "z0")?, req(&mut b, "z1")?);
            let up = opt(&mut b, "up", Num::F(1.0))?;
            _keystone_receptacle_geometry(cx, &inner, &outer, &station, z0, z1, up)?.to_py()
        }),
        "_keystone_receptacle" => wrap(cx, |cx, args, kwargs| {
            let names = ["solid", "inner", "outer", "station", "z0", "z1", "up"];
            let mut b = py::bind(args, kwargs, &names, &[])?;
            let solid = req(&mut b, "solid")?;
            let inner: [f64; 6] = req(&mut b, "inner")?;
            let outer: [f64; 6] = req(&mut b, "outer")?;
            let station = b.req("station")?;
            let (z0, z1) = (req(&mut b, "z0")?, req(&mut b, "z1")?);
            let up = opt(&mut b, "up", Num::F(1.0))?;
            _keystone_receptacle(cx, solid, &inner, &outer, &station, z0, z1, up)?.to_py()
        }),
        "_c14_tunnel" => wrap(cx, |cx, args, kwargs| {
            let names = ["solid", "inner", "outer", "stations", "ports", "z0", "z1", "up"];
            let mut b = py::bind(args, kwargs, &names, &[])?;
            let solid = req(&mut b, "solid")?;
            let inner: [f64; 6] = req(&mut b, "inner")?;
            let outer: [f64; 6] = req(&mut b, "outer")?;
            let (stations, ports) = (b.req("stations")?, b.req("ports")?);
            let (z0, z1) = (req(&mut b, "z0")?, req(&mut b, "z1")?);
            let up = opt(&mut b, "up", Num::F(1.0))?;
            _c14_tunnel(cx, solid, &inner, &outer, &stations, &ports, z0, z1, up)?.to_py()
        }),
        "y_stack_figures" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["inner"], &[])?;
            y_stack_figures(cx, &req(&mut b, "inner")?)?.to_py()
        }),
        "_report_bounds" => wrap(cx, |cx, args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            _report_bounds(cx)?.to_py()
        }),
        "_box_question_frame" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["bounds"], &[])?;
            _box_question_frame(cx, &b.req("bounds")?)?.to_py()
        }),
        "_lip_lane_boxes" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["inner", "y_span", "plate", "y_joint"], &[])?;
            let inner: [f64; 6] = req(&mut b, "inner")?;
            let y_span = req(&mut b, "y_span")?;
            let plate = b.req("plate")?;
            _lip_lane_boxes(cx, &inner, y_span, &plate, req(&mut b, "y_joint")?)?.to_py()
        }),
        "_lip_lane_tool" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["inner", "y_span", "plate", "y_joint"], &[])?;
            let inner: [f64; 6] = req(&mut b, "inner")?;
            let y_span = req(&mut b, "y_span")?;
            let plate = b.req("plate")?;
            _lip_lane_tool(cx, &inner, y_span, &plate, req(&mut b, "y_joint")?)?.to_py()
        }),
        "_under_lip_tool" => wrap(cx, |cx, args, kwargs| {
            let names = ["inner", "y_joint", "splits", "pump_trays", "column"];
            let mut b = py::bind(args, kwargs, &names, &[])?;
            let inner: [f64; 6] = req(&mut b, "inner")?;
            let y_joint = req(&mut b, "y_joint")?;
            let splits: [f64; 2] = req(&mut b, "splits")?;
            let pump_trays = b.req("pump_trays")?;
            let column = req(&mut b, "column")?;
            _under_lip_tool(cx, &inner, y_joint, splits, &pump_trays, column)?.to_py()
        }),
        "main" => wrap(cx, |cx, args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            main(cx)
        }),
        _ => return None,
    };
    Some(f)
}

// --- what this part reads from elsewhere ------------------------------------------------------------

fn f(x: f64) -> Val {
    Val::Float(x)
}
fn floats<const N: usize>(values: [f64; N]) -> Val {
    py::ftuple(&values)
}
/// `obj.<name>` of a provider module or object, read now.
fn attr(object: &Val, name: &str) -> Result<Val> {
    object.attr(name)
}
/// `obj.<name>(*args)`, the attribute read at the call (the recorders replace provider functions).
fn call(object: &Val, name: &str, args: Args) -> Result<Val> {
    object.attr(name)?.call(args, vec![])
}
fn call_kw(object: &Val, name: &str, args: Args, kwargs: Vec<(&str, Val)>) -> Result<Val> {
    py::call_kw(&object.attr(name)?, args, kwargs)
}
/// A provider constant that may be an int or a float.
fn number(object: &Val, name: &str) -> Result<Num> {
    Num::of(&object.attr(name)?).with_context(|| format!("provider constant {name}"))
}
/// `fits.<name>`.
fn fits(cx: &Cx, name: &str) -> Result<f64> {
    cx.s.fits.attr(name)?.num().with_context(|| format!("fits.{name}"))
}
/// `math.sqrt(x)`, with the runtime's domain error.
fn sqrt(x: f64) -> Result<f64> {
    ensure!(x >= 0., "math domain error");
    Ok(x.sqrt())
}
/// `math.acos(x)`, with the runtime's domain error.
fn acos(x: f64) -> Result<f64> {
    let y = x.acos();
    ensure!(y.is_finite(), "math domain error");
    Ok(y)
}
/// `format(value, spec)` of a value as Python holds it.
fn fmtv(value: &Val, spec: &str) -> Result<String> {
    num::fmtv(value, spec)
}

/// `shell.<name>(*args)`: a geometry leaf or slot, read from the namespace at the call.
fn leaf(cx: &Cx, name: &str, args: Args) -> Result<Solid> {
    panel::call_leaf(&cx.ns.0, name, args, vec![])
}
fn leaf_kw(cx: &Cx, name: &str, args: Args, kwargs: Vec<(&str, Val)>) -> Result<Solid> {
    panel::call_leaf(&cx.ns.0, name, args, kwargs.into_iter().map(|(k, v)| (k.to_owned(), v)).collect())
}
/// `_ybox(x0, x1, y0, y1, z0, z1)` of six numbers as given.
fn ybox(cx: &Cx, bounds: [Val; 6]) -> Result<Solid> {
    leaf(cx, "_ybox", bounds.into())
}
/// `record_bound(bound)` through the namespace: the recorders and machine-data replace it.
fn record_bound(cx: &Cx, bound: Val) -> Result<Val> {
    py::call(&cx.ns.get("record_bound")?, vec![bound])
}
/// A solid as Python reads it off a provider: `None` stays `None`.
fn solid(value: &Val) -> Solid {
    Solid::from_val(value)
}
/// `hasattr(shape, name)`.
fn has_attr(shape: &Solid, name: &str) -> bool {
    match shape {
        Solid::Native(_) => matches!(name, "clean" | "val" | "fuse" | "cut" | "intersect" | "translate"),
        Solid::Py(value) => value.attr(name).is_ok(),
    }
}

// Other parts' functions this part calls (through the namespace until their parts publish).

fn interior_x(cx: &Cx) -> Result<(f64, f64)> {
    cx.generated("interior_x", vec![], vec![])
}
fn piece_root_faces(cx: &Cx, inner: &[f64; 6], y_side: &str, z_side: &str) -> Result<[f64; 6]> {
    cx.generated("piece_root_faces", crate::py_args![*inner, y_side.to_owned(), z_side.to_owned()], vec![])
}
fn back_wall_t_at(cx: &Cx, x: Num, z: Num) -> Result<f64> {
    cx.generated("back_wall_t_at", crate::py_args![x, z], vec![])
}
fn c14_mount_half(cx: &Cx, bore_w: Num, bore_h: Num, screw_reach: f64) -> Result<(f64, f64)> {
    cx.generated("c14_mount_half", crate::py_args![bore_w, bore_h, screw_reach], vec![])
}
fn back_top_ceiling_face(cx: &Cx) -> Result<f64> {
    cx.generated("back_top_ceiling_face", vec![], vec![])
}
fn supported_cut(cx: &Cx, cutter: Solid, up: Num) -> Result<Solid> {
    cx.generated("_supported_cut", crate::py_args![cutter, up], vec![])
}
fn z_rail_runs(cx: &Cx, inner: &[f64; 6], y_joint: f64, col: &str, plate: &Val) -> Result<Vec<[f64; 5]>> {
    cx.generated("_z_rail_runs", crate::py_args![*inner, y_joint, col.to_owned(), plate.clone()], vec![])
}
fn rail_x(cx: &Cx, x_in: f64, sx: f64, col: &str) -> Result<[f64; 4]> {
    cx.generated("_rail_x", crate::py_args![x_in, sx, col.to_owned()], vec![])
}
fn lip_underwall(cx: &Cx, inner: &[f64; 6], y_joint: f64, zj: f64) -> Result<Solid> {
    cx.generated("_lip_underwall", crate::py_args![*inner, y_joint, zj], vec![])
}
fn front_flat_lip_drop(cx: &Cx, inner: &[f64; 6], zj: f64) -> Result<Solid> {
    cx.generated("_front_flat_lip_drop", crate::py_args![*inner, zj], vec![])
}
fn column_pillar(cx: &Cx, inner: &[f64; 6], sx: i64, sy: i64, zj: f64) -> Result<Solid> {
    cx.generated("_column_pillar", crate::py_args![*inner, sx, sy, zj], vec![])
}

// --- tube anchors -----------------------------------------------------------------------------------

/// A tube station as the anchors read it: `station[:4]` is `(mid, u, n, seat_r)`; a fifth
/// entry names each end web's stand, a sixth `"cap"` marks a station an anchor cap closes.
struct Station {
    /// The station's entries as handed in.
    items: Vec<Val>,
    mid: Val,
    u: Val,
    n: Val,
    seat: Val,
    m: [Num; 3],
    uu: [Num; 3],
    nn: [Num; 3],
    seat_r: Num,
    /// `tuple(int(round(c)) for c in n)`.
    key: Vec<i64>,
}

/// The first three numbers of a vector, as `v[0]`, `v[1]`, `v[2]` read them.
fn three(v: &Val) -> Result<[Num; 3]> {
    let items = v.iter()?;
    ensure!(items.len() >= 3, "tuple index out of range");
    Ok([Num::of(&items[0])?, Num::of(&items[1])?, Num::of(&items[2])?])
}

impl Station {
    fn read(station: &Val) -> Result<Station> {
        let items = station.iter()?;
        // `mid, u, n, seat_r = station[:4]`
        let head = py::unpack(&Val::tuple(items.iter().take(4).cloned().collect()), 4)?;
        let key = head[2]
            .iter()?
            .iter()
            .map(|c| {
                Ok(match Num::of(c)? {
                    Num::I(i) => i,
                    Num::F(x) => num::round_int(x),
                })
            })
            .collect::<Result<Vec<i64>>>()?;
        Ok(Station {
            m: three(&head[0])?,
            uu: three(&head[1])?,
            nn: three(&head[2])?,
            seat_r: Num::of(&head[3])?,
            mid: head[0].clone(),
            u: head[1].clone(),
            n: head[2].clone(),
            seat: head[3].clone(),
            key,
            items,
        })
    }
    /// `anchor_capped(station)`.
    fn capped(&self) -> bool {
        capped(&self.items)
    }
}

/// `len(station) > 5 and station[5] == "cap"`.
fn capped(items: &[Val]) -> bool {
    items.len() > 5 && matches!(&items[5], Val::Str(s) if s == "cap")
}

/// `_ROOT_FACE.get(key)`: which interior face each root direction names. The anchor states no
/// height of its own: it is handed the tube, and the wall it stands on is where its rib stops.
fn root_face(key: &[i64]) -> Option<usize> {
    match key {
        [-1, 0, 0] => Some(0),
        [1, 0, 0] => Some(1),
        [0, -1, 0] => Some(2),
        [0, 1, 0] => Some(3),
        [0, 0, -1] => Some(4),
        [0, 0, 1] => Some(5),
        _ => None,
    }
}

/// `t = n × u`: the profile's `a` axis.
fn cross_t(n: &[Num; 3], u: &[Num; 3]) -> [Num; 3] {
    [
        n[1].mul(u[2]).sub(n[2].mul(u[1])),
        n[2].mul(u[0]).sub(n[0].mul(u[2])),
        n[0].mul(u[1]).sub(n[1].mul(u[0])),
    ]
}

/// `(b_face, b_lane)`: how far the piece's own root face and the box's lane stand off the
/// station's axis, along the root direction.
fn face_depths(st: &Station, face: usize, roots: &[Num; 6], lane: &[Num; 6]) -> (f64, f64) {
    let sign = if face % 2 == 1 { 1.0 } else { -1.0 };
    let along = st.m[face / 2];
    (roots[face].sub(along).f() * sign, lane[face].sub(along).f() * sign)
}

/// The plane a rib roots on: the piece's own face, or the box's lane where that face leaves the
/// zip tie no channel.
fn tied_root(cx: &Cx, st: &Station, b_face: f64, b_lane: f64, b_crown: f64) -> f64 {
    if b_face < b_lane - 1e-9 && b_face - b_crown < cx.s.tie_t && !st.capped() { b_lane } else { b_face }
}

/// The shortest zip tie that closes round a seated body and its rib together.
///
/// A zip tie turns INSIDE the channel, so what it reaches round is the body with the rib's own
/// back behind it — the convex perimeter of that pair, and not of the wall the rib stands on.
/// Read on the bore, which is the section this box knows.
///
/// The hull is the rib's rectangle with a cap of the bore over it: the channel's floor, the
/// rib's two flanks down to the axis plane, a tangent from each corner onto the bore, and the
/// arc between the two tangent points. Floor and flank are both `seat_r + wall`, so the
/// rectangle is square and the whole figure is a function of the seat.
pub fn tube_anchor_tie_loop(cx: &Cx, seat_r: f64) -> Result<f64> {
    let w = seat_r + cx.s.wall;
    Ok((4.0 * w + 2.0 * sqrt(w * w - seat_r * seat_r)?)
        + seat_r * (std::f64::consts::PI - 2.0 * acos(seat_r / w)?))
}

/// The anchor's own workplane — profile drawn in (`t`, `n`), extruded along the tube.
///
/// `t = n × u` rather than `u × n`, so the workplane's second axis comes out as `n` itself and a
/// profile point's second coordinate is its own distance toward the root face.
pub fn _anchor_plane(cx: &Cx, origin: &Val, u: &Val, n: &Val) -> Result<Val> {
    let t = cross_t(&three(n)?, &three(u)?);
    let plane = cx.ns.get("cq")?.attr("Plane")?;
    let vector = |values: Args| -> Result<Val> { cx.ns.get("cq")?.attr("Vector")?.call(values, vec![]) };
    let origin = vector(origin.iter()?)?;
    let x_dir = vector(t.iter().map(|c| c.val()).collect())?;
    let normal = vector(u.iter()?)?;
    py::call_kw(&plane, vec![], vec![("origin", origin), ("xDir", x_dir), ("normal", normal)])
}

/// The two world-aligned boxes a rib's end webs would stand in as columns — from the flank
/// that looks print-down to the plane `face_z`, the piece's own print-bed face — or None for an
/// end that has no such column: a rib whose flanks are level, whose tube runs along the build
/// axis, or whose print-down flank does not look toward `face_z`. `depth` is how far off the
/// root face the column stands, None for the flank's whole section to the axis plane and
/// `tube_anchor_corbel_depth(station, roots, lane)` for the footprint the corbel would have
/// had. `station` is `(mid, u, n, seat_r)` as `_tube_anchors` reads it, `roots` and `lane` the
/// piece's root faces and the box's own, and the boxes are struck the way that builder strikes
/// the rib — a capped station's on its own longer rib and end webs (`_capped_anchor`); the
/// assembly reads each against the pack to say which end stands (`stand`).
pub fn tube_anchor_end_columns(
    cx: &Cx,
    station: &Val,
    roots: &[Num; 6],
    lane: &[Num; 6],
    up: Num,
    face_z: Num,
    depth: Option<Num>,
) -> Result<[Option<[f64; 6]>; 2]> {
    end_columns(cx, &Station::read(station)?, roots, lane, up, face_z, depth)
}

fn end_columns(
    cx: &Cx,
    st: &Station,
    roots: &[Num; 6],
    lane: &[Num; 6],
    up: Num,
    face_z: Num,
    depth: Option<Num>,
) -> Result<[Option<[f64; 6]>; 2]> {
    let s = &cx.s;
    let Some(face) = root_face(&st.key) else { return Ok([None, None]) };
    let (b_face, b_lane) = face_depths(st, face, roots, lane);
    let reach = st.seat_r.f() + s.wall;
    let b_crown = st.seat_r.f() + s.wall;
    let b_root = tied_root(cx, st, b_face, b_lane, b_crown);
    let t = cross_t(&st.nn, &st.uu);
    if (t[2].f().abs() - 1.0).abs() > 1e-6 {
        return Ok([None, None]);
    }
    let a_hang = reach.copysign(up.neg().mul(t[2]).f());
    let a_face = face_z.sub(st.m[2]).f() / t[2].f();
    if a_face.abs() <= a_hang.abs() + 1e-6 || (a_face > 0.0) != (a_hang > 0.0) {
        return Ok([None, None]);
    }
    let (length, web) = if st.capped() {
        (number(&s._anchor_cap, "RIB_LEN")?, number(&s._anchor_cap, "END_WEB")?)
    } else {
        (Num::F(s.tube_anchor_len), Num::F(s.tie_cav_wall))
    };
    let origin: [f64; 3] = std::array::from_fn(|k| st.m[k].f() - st.uu[k].mul(length).f() / 2.0);
    let b_lo = match depth {
        None => 0.0,
        Some(d) => num::max2(0.0, b_root - d.f()),
    };
    let mut out = [None, None];
    for (w, (s0, s1)) in [(Num::F(0.0), web), (length.sub(web), length)].into_iter().enumerate() {
        let mut pts: Vec<[f64; 3]> = Vec::with_capacity(8);
        for sv in [s0, s1] {
            for b in [b_lo, b_root] {
                for a in [a_hang, a_face] {
                    pts.push(std::array::from_fn(|k| {
                        ((origin[k] + st.uu[k].mul(sv).f()) + st.nn[k].f() * b) + t[k].f() * a
                    }));
                }
            }
        }
        let lo: [f64; 3] = std::array::from_fn(|k| num::min_of(pts.iter().map(|p| p[k])).expect("eight points"));
        let hi: [f64; 3] = std::array::from_fn(|k| num::max_of(pts.iter().map(|p| p[k])).expect("eight points"));
        out[w] = Some([lo[0], lo[1], lo[2], hi[0], hi[1], hi[2]]);
    }
    Ok(out)
}

/// How far off the root face a rib's corbel would stand — `tube_anchor_corbel_reach` past
/// the box's own lane, capped at the rib's depth — which is also the footprint a column may
/// take where the flank's whole section cannot.
pub fn tube_anchor_corbel_depth(cx: &Cx, station: &Val, roots: &[Num; 6], lane: &[Num; 6]) -> Result<Option<f64>> {
    corbel_depth(cx, &Station::read(station)?, roots, lane)
}

fn corbel_depth(cx: &Cx, st: &Station, roots: &[Num; 6], lane: &[Num; 6]) -> Result<Option<f64>> {
    let Some(face) = root_face(&st.key) else { return Ok(None) };
    let (b_face, b_lane) = face_depths(st, face, roots, lane);
    let b_crown = st.seat_r.f() + cx.s.wall;
    let b_root = tied_root(cx, st, b_face, b_lane, b_crown);
    Ok(Some(num::min2(b_root, (b_root - b_lane) + cx.s.tube_anchor_corbel_reach)))
}

/// The two world boxes enclosing the ordinary end-web corbels for `station`.
///
/// Each box is the corbel's complete triangular prism: one `tie_cav_wall` end, its full
/// `tube_anchor_corbel_depth` off the root face, and the same distance along the print-down
/// flank. A rib with no print-down flank has no end-web corbels.
pub fn tube_anchor_end_corbel_bounds(
    cx: &Cx,
    station: &Val,
    roots: &[Num; 6],
    lane: &[Num; 6],
    up: Num,
) -> Result<[Option<[f64; 6]>; 2]> {
    let st = Station::read(station)?;
    let depth = corbel_depth(cx, &st, roots, lane)?;
    let t = cross_t(&st.nn, &st.uu);
    let depth = match depth {
        Some(d) if !(d <= 1e-9) && !((t[2].f().abs() - 1.0).abs() > 1e-6) => d,
        _ => return Ok([None, None]),
    };
    let a_hang = (st.seat_r.f() + cx.s.wall).copysign(up.neg().mul(t[2]).f());
    let a_tip = a_hang + depth.copysign(a_hang);
    let tip_z = st.m[2].f() + t[2].f() * a_tip;
    end_columns(cx, &st, roots, lane, up, Num::F(tip_z), Some(Num::F(depth)))
}

/// Back-top's `(roots, lane)` off stated figures alone — the box's interior the pack is struck
/// against, and the faces this piece presents (`piece_root_faces`) — for a reader with no built
/// Box, struck the way `back_top_ceiling_stock` is.
pub fn back_top_frames(cx: &Cx) -> Result<([f64; 6], [f64; 6])> {
    let s = &cx.s;
    let (ix0, ix1) = interior_x(cx)?;
    let lane = [ix0, ix1, s.y_seam, s.rear_plane_y, s.z_seam, (s.appliance_height - s.floor_t) - s.wall];
    Ok((piece_root_faces(cx, &lane, "back", "top")?, lane))
}

/// Whether a station at `point` stands in back-top's band — aft of the Y seam, above the Z.
pub fn back_top_owns(cx: &Cx, point: &[f64]) -> Result<bool> {
    let at = |k: usize| point.get(k).copied().context("tuple index out of range");
    Ok(at(1)? > cx.s.y_seam && at(2)? > cx.s.z_seam)
}

/// Every tube anchor whose whole rib this piece owns.
///
/// A station carries the tube and only the tube — where its axis runs, which way it points, what
/// it seats on — and the box carries the face. So an anchor moves when its run moves and stops
/// where the wall stops. A piece that owns only part of a rib builds none of it, the way every
/// other station on these walls behaves.
///
/// AND THE FACE IS THE PIECE'S OWN (`piece_root_faces`), not the box's interior. A station is
/// struck in the box's frame because that is the frame the run is in; the plane its rib STOPS on
/// is whatever the piece carrying it presents, and on the two pieces with a grown flank those two
/// stand three and six millimetres apart. Measured to the wrong one the channel below is drawn
/// inside the wall's own stock, which is a rib with no cavity in it at all.
///
/// AND WHERE THAT FACE LEAVES NO CHANNEL, THE WALL GIVES THE RIB ITS LANE BACK. `lane` is the
/// box's own interior — one `wall` inside the exterior, the plane every station was struck
/// against — and a piece carrying stock inboard of it carries stock the rib was drawn to use. So
/// that piece gives it up over the rib's footprint and the rib roots on `lane` instead. The wall
/// keeps its full section everywhere the rib does not need it, and one `wall` stands behind
/// the relief because `lane` is one `wall` in.
///
/// THE RELIEF IS WIDER THAN THE RIB OVER THE TIE BAND ALONE, and there by the zip tie. What the
/// loop runs down is the rib's two FLANKS, from the channel's floor to the tube's own axis plane
/// (`tube_anchor_tie_loop`), so a relief cut to the rib's own reach would hand the zip tie a
/// channel it could not leave. Over the cavity's own `tie_cav_w` it is carried
/// `tie_t + tie_cav_buffer` past each flank instead — the same room over the zip tie every cavity
/// on this box carries — and those two lobes are what the loop comes down. The rib's two
/// `tie_cav_wall` ends take the rib's own reach, which the rib fills back: the wall keeps its
/// full section everywhere the zip tie never arrives.
///
/// THE CAVITY IS A REMAINDER: the rib stands one `wall` over the bore's crown down its whole
/// length and its two `tie_cav_wall` ends carry on to the face it roots on. The `tie_cav_w`
/// between them is the tie band, the one band the relief takes wide, and there the zip tie keeps
/// at most `tube_anchor_cavity_depth` once there is enough excess reach to add substantial
/// backing; that excess is filled from the root face. The crown is therefore always its floor and
/// either the root face or that backing is its roof — neither is cut, so there is no cutter face
/// to graze the opening.
///
/// A FLANK THAT LOOKS PRINT-DOWN STANDS ON THE FACE THE PRINT GROWS FROM, AND ONLY WHERE IT
/// CANNOT CARRIES A CORBEL. A station's fifth entry, `stand`, names per end web `(plane, depth)`:
/// the plane that end stands on — the piece's own print-bed face, where the air from the flank
/// to that face is free of every placed body (`enclosure_assembly.stand_anchors` reads it
/// against the pack) — and how far off the root face the column stands, None for the flank's
/// whole section where that air is free and the corbel's own depth where only that much is; or
/// None for the end where a body stands even in that. An end that stands goes on as a COLUMN:
/// the flank's section over that depth, straight to that plane (`_anchor_column`), so nothing
/// of it looks print-down there. An end that cannot takes a 45 degree wedge rooted on the same face the
/// rib is, growing off that face into `tube_anchor_corbel_reach`: a rib whose axis stands
/// inside that band is a triangle, `b_root` deep at the root face and nothing at the tube's axis
/// plane; a deeper one is a truncated wedge, out to the band's edge and no further, and the deep
/// end of its flank keeps its flat. `up` is the piece's print up along the box's Z, ±1, and
/// which flank hangs comes off the profile's own `a` axis read against it — the flank whose
/// outward looks along −`up`. A rib rooted on the floor or the ceiling, or with its tube running
/// along the build axis, has neither flank down and takes neither; a rib rooted on the face the
/// piece beds on — a ceiling-rooted rib on a piece printed ceiling-down — stands on the slab
/// with its seat an upward-opening cradle in the print. Column and corbel alike stand over the
/// same two `tie_cav_wall` ends and stop at the tie band, because the tie comes down that flank
/// to the axis plane over `tie_cav_w` and material there is the one path it has closed. The
/// band of flank between the two ends bridges.
///
/// THE ZIP TIE CLOSES ROUND THE TUBE AND THE RIB'S OWN BACK TOGETHER: through the cavity, out one
/// flank, round the far side of the tube and back in the other. What it pulls is the tube into
/// the bore, and the bore is what says where the tube is.
///
/// A STATION AN ANCHOR CAP CLOSES TAKES NONE OF THE TIE'S ROOM (`anchor_capped`). Its rib is one
/// solid post with a catch window in each flank (`_capped_anchor`), and the cap is the other
/// half of the pipe.
#[allow(clippy::too_many_arguments)]
pub fn _tube_anchors(
    cx: &Cx,
    solid: Solid,
    roots: &[Num; 6],
    lane: &[Num; 6],
    stations: &Val,
    y0: f64,
    y1: f64,
    z0: f64,
    z1: f64,
    up: Num,
) -> Result<Solid> {
    let s = &cx.s;
    if !stations.truthy()? {
        return Ok(solid);
    }
    let mut solid = solid;
    for station in stations.iter()? {
        let st = Station::read(&station)?;
        let stand = if st.items.len() > 4 && st.items[4].truthy()? {
            st.items[4].iter()?
        } else {
            vec![Val::None, Val::None]
        };
        let Some(face) = root_face(&st.key) else {
            bail!(
                "_tube_anchors: root direction {} names no interior face. An anchor stands on one of the \
                 box's six faces, and that face is what its rib stops on.",
                fmtv(&st.n, "")?
            )
        };
        let sign = if face % 2 == 1 { 1.0 } else { -1.0 };
        let b_face = roots[face].sub(st.m[face / 2]).f() * sign; // the face this piece presents
        if st.capped() {
            solid = _capped_anchor(cx, solid, &station, b_face, roots, lane, y0, y1, z0, z1, up)?;
            continue;
        }
        let b_lane = lane[face].sub(st.m[face / 2]).f() * sign; // and the box's own, at or outboard of it
        let reach = st.seat_r.f() + s.wall; // the lip's outer edge
        let b_crown = st.seat_r.f() + s.wall; // one `wall` over the bore's own crown
        // Add the supported tie-passage allowance at the backing side of its gap.
        // The tube-bearing web keeps its complete wall section and the tube's axis.
        let cavity_depth = s.tube_anchor_cavity_depth + fits(cx, "supported_surface")?;
        let relief = b_face < b_lane - 1e-9 && b_face - b_crown < s.tie_t;
        let mut b_root = b_face;
        if relief {
            b_root = b_lane; // the wall gives this rib its lane back
        }
        if b_root - b_crown < s.tie_t {
            bail!(
                "_tube_anchors: a `wall` off the bore's crown leaves {} mm under the face this rib roots on, \
                 and the zip tie is {} thick. What gives way here is the run's own lane, not the wall: route \
                 it further off that face, or anchor it to another one.",
                num::fmt(b_root - b_crown, ".3f"),
                num::fmt(s.tie_t, ".3g")
            );
        }
        let origin: [f64; 3] = std::array::from_fn(|k| st.m[k].f() - st.uu[k].f() * s.tube_anchor_len / 2.0);
        // The rib's own extent, so a piece that owns part of it builds none of it.
        let t = cross_t(&st.nn, &st.uu);
        let mut span: Vec<[f64; 3]> = Vec::with_capacity(8);
        for sv in [0.0, s.tube_anchor_len] {
            for b in [0.0, b_root] {
                for aa in [-reach, reach] {
                    span.push(std::array::from_fn(|k| {
                        ((origin[k] + st.uu[k].f() * sv) + st.nn[k].f() * b) + t[k].f() * aa
                    }));
                }
            }
        }
        let low = |k: usize| num::min_of(span.iter().map(|p| p[k])).expect("eight points");
        let high = |k: usize| num::max_of(span.iter().map(|p| p[k])).expect("eight points");
        if !(y0 <= low(1) && high(1) <= y1 && z0 <= low(2) && high(2) <= z1) {
            continue;
        }
        // THE CAVITY IS WHAT IS NEVER FUSED, and nothing is cut for it. The rib is ONE box its
        // whole length up to `b_crown`, the two ends carried on up to the face it roots on, and
        // ONE bore through all of it. In the central zip tie band, material comes back from a remote
        // root until only `tube_anchor_cavity_depth` remains, provided that backing itself is at
        // least `tube_anchor_backing_min`. That boxes a small tube's long rib into the wall without
        // changing either threading mouth or putting a fragile skin against them.
        //
        // The lower box runs the rib's whole length so the seat's own lip is ONE edge, and the rib
        // is UNIFIED before it joins the piece. A fuse imprints the seam of every solid that went
        // into it, so a rib fused straight onto the wall carries its lip in as many pieces as it
        // was laid down in — three here — and its bore in as many again.
        let band: [f64; 3] = std::array::from_fn(|k| origin[k] + st.uu[k].f() * s.tie_cav_wall);
        // The flank that looks print-down — None where the profile's `a` axis is level — and how
        // far off the root face its corbel grows: to the band's edge or the axis plane, whichever
        // it arrives at first.
        let a_hang = if t[2].f().abs() < 1e-9 { None } else { Some(reach.copysign(up.neg().mul(t[2]).f())) };
        let corbel = num::min2(b_root, (b_root - b_lane) + s.tube_anchor_corbel_reach);
        let rib_at = |at: [f64; 3], length: f64, reach: f64, b0: f64, b1: f64| -> Result<Solid> {
            leaf(cx, "_anchor_rib", vec![floats(at), st.u.clone(), st.n.clone(), f(length), f(reach), f(b0), f(b1)])
        };
        if relief {
            // THE RELIEF, cut before the rib is fused so the rib is what fills it. Its floor is
            // `lane`, so what stands behind it is the one `wall` this box carries everywhere. The
            // rib's own reach runs the whole length; the two lobes the zip tie comes down are the
            // tie band's, reach no further into the wall than the channel's own roof, and the
            // wall keeps its full section at the rib's two ends.
            solid = solid.cut(&[rib_at(origin, s.tube_anchor_len, reach, b_face, b_lane)?])?;
            // This channel is only the air available before the declared root. A shallow
            // anchor must not gain clearance by cutting through its supporting wall.
            let roof = num::min2(b_root, b_crown + cavity_depth);
            if roof > b_face + 1e-9 {
                solid = solid.cut(&[rib_at(band, s.tie_cav_w, (reach + s.tie_t) + s.tie_cav_buffer, b_face, roof)?])?;
            }
        }
        let mut rib = rib_at(origin, s.tube_anchor_len, reach, 0.0, b_crown)?;
        let ends = [(0.0, s.tie_cav_wall), (s.tie_cav_wall + s.tie_cav_w, s.tube_anchor_len)];
        for (w, (s0, s1)) in ends.into_iter().enumerate() {
            let end: [f64; 3] = std::array::from_fn(|k| origin[k] + st.uu[k].f() * s0);
            rib = rib.fuse(&[rib_at(end, s1 - s0, reach, b_crown, b_root)?])?;
            let Some(a_hang) = a_hang else { continue };
            let stand_w = stand.get(w).cloned().context("tuple index out of range")?;
            if !matches!(stand_w, Val::None) && (t[2].f().abs() - 1.0).abs() < 1e-6 {
                // THIS END STANDS ON THE PRINT-BED FACE `stand` NAMES: the flank's section, over
                // the depth named, goes straight on to that plane in the direction the
                // print-down flank looks.
                let pd = py::unpack(&stand_w, 2)?;
                let plane = Num::of(&pd[0])?;
                let a_face = plane.sub(st.m[2]).f() / t[2].f();
                let b_lo = match &pd[1] {
                    Val::None => 0.0,
                    depth => num::max2(0.0, b_root - depth.num()?),
                };
                if a_face.abs() > a_hang.abs() + 1e-6 && (a_face > 0.0) == (a_hang > 0.0) {
                    let column = leaf(
                        cx,
                        "_anchor_column",
                        vec![floats(end), st.u.clone(), st.n.clone(), f(s1 - s0), f(a_hang), f(a_face), f(b_root), f(b_lo)],
                    )?;
                    rib = rib.fuse(&[column])?;
                }
                continue;
            }
            if corbel > 1e-9 {
                let wedge = leaf(
                    cx,
                    "_anchor_corbel",
                    vec![floats(end), st.u.clone(), st.n.clone(), f(s1 - s0), f(a_hang), f(b_root), f(corbel)],
                )?;
                rib = rib.fuse(&[wedge])?;
            }
        }
        // THE CROWN OVER THE TIE BAND IS ONE FLAT `tie_cav_w` STRIP between the two end webs,
        // whichever way the piece prints: where it looks print-down it is a bridge that span
        // long, web to web, laid over the channel's air.
        if b_root - b_crown >= cavity_depth + s.tube_anchor_backing_min {
            rib = rib.fuse(&[rib_at(band, s.tie_cav_w, reach, b_crown + cavity_depth, b_root)?])?;
        }
        let mut seat = leaf(cx, "_anchor_bore", vec![floats(origin), st.u.clone(), st.seat.clone(), f(s.tube_anchor_len)])?;
        let supported_seat = st.uu[2].f().abs() < 1.0 - 1e-6 && st.nn[2].mul(up).f() >= -1e-6;
        if supported_seat {
            // Side-rooted circular seats have a print-down arc. Extend the exterior stock
            // along with that arc so the complete nominal wall remains behind the added
            // room. Ceiling-bedded open cradles and vertical bores need no such allowance.
            rib = supported_cut(cx, rib, up)?;
            seat = supported_cut(cx, seat, up)?;
        }
        rib = rib.cut(&[seat])?;
        let joined = if has_attr(&rib, "clean") { rib.clean()? } else { rib };
        solid = solid.fuse(&[joined])?;
    }
    Ok(solid)
}

/// Whether an anchor station is closed by an anchor cap rather than a zip tie: its sixth
/// entry, carried from the site's stated closure by `enclosure_assembly.stand_anchors`.
pub fn anchor_capped(cx: &Cx, station: &Val) -> Result<bool> {
    let _ = cx;
    Ok(capped(&station.iter()?))
}

/// The rib an anchor cap closes (`_anchor_cap_interface`): the tie rib's half pipe as one
/// solid post from the face it roots on to the axis plane, a catch window in each flank, and
/// no room for a tie anywhere.
///
/// THE CAP IS CUT FOR ONE SEAT. Its section is struck for the 1/4" tube, so a station seating
/// anything else raises.
///
/// AND THE RIB STANDS ON A FACE UNDER IT OR BESIDE IT IN THE PRINT. Rooted on the face the piece
/// prints on, it stands up off the bed: each window's bearing face prints as a bridge web to
/// web, and where the ceiling stands inside the wings' reach it has already given them their
/// room (`_ceiling_cap_reliefs`). Rooted on a wall, its tube level, it reaches out of that wall:
/// the flank that looks print-down and its window's roof bridge web to web, and the two end
/// webs stand on the tied rib's own 45-degree corbels (`tube_anchor_corbel_depth`), which grow
/// beyond the cap's ends and so never meet a wing; where that wall stands inside the wings'
/// reach it gives them their room here. A rib whose root looks print-up would hang, and raises.
///
/// The windows are cut once the rib is fused, each from its bearing face to where its flank
/// ends — the slab's interior face under the ceiling, the piece's own face elsewhere — so no
/// band of flank is left between window and root (`_anchor_cap_interface.window_top`).
///
/// A piece that owns only part of the rib builds none of it, like every other station here.
#[allow(clippy::too_many_arguments)]
pub fn _capped_anchor(
    cx: &Cx,
    solid: Solid,
    station: &Val,
    b_face: f64,
    roots: &[Num; 6],
    lane: &[Num; 6],
    y0: f64,
    y1: f64,
    z0: f64,
    z1: f64,
    up: Num,
) -> Result<Solid> {
    let st = Station::read(station)?;
    let cap = &cx.s._anchor_cap;
    let frame = call(cap, "Frame", vec![st.mid.clone(), st.u.clone(), st.n.clone()])?;
    let half = number(cap, "RIB_LEN")?.f() / 2.0;
    let mut span = Vec::with_capacity(8);
    for sv in [-half, half] {
        for b in [0.0, b_face] {
            let rib_r = number(cap, "RIB_R")?;
            for a in [rib_r.neg(), number(cap, "RIB_R")?] {
                span.push(call(&frame, "point", vec![a.val(), f(b), f(sv)])?);
            }
        }
    }
    let coords = |k: i64| -> Result<Vec<f64>> { span.iter().map(|p| p.get(Val::Int(k))?.num()).collect() };
    let (ys, zs) = (coords(1)?, coords(2)?);
    let lo = |v: &[f64]| num::min_of(v.iter().copied()).expect("eight points");
    let hi = |v: &[f64]| num::max_of(v.iter().copied()).expect("eight points");
    if !(y0 <= lo(&ys) && hi(&ys) <= y1 && z0 <= lo(&zs) && hi(&zs) <= z1) {
        return Ok(solid);
    }
    let mut solid = solid;
    let place = format!(
        "({}, {}, {})",
        fmtv(&st.m[0].val(), ".2f")?,
        fmtv(&st.m[1].val(), ".2f")?,
        fmtv(&st.m[2].val(), ".2f")?
    );
    if st.seat_r.f() > number(cap, "SEAT_R")?.f() + 1e-6 {
        bail!(
            "_capped_anchor: the anchor at {place} seats r {} and the anchor cap is cut for the 1/4\" tube's \
             {}. Close it with a zip tie, or cut a cap for its seat.",
            fmtv(&st.seat, ".3f")?,
            fmtv(&cap.attr("SEAT_R")?, ".3f")?
        );
    }
    let rise = st.nn[2].mul(up); // -1: root under the rib in the print; 0: a wall
    if rise.f() > 1e-6 {
        bail!(
            "_capped_anchor: the anchor at {place} roots on {}, which looks print-up; the rib would hang off \
             it. Close it with a zip tie.",
            fmtv(&Val::tuple(st.n.iter()?), "")?
        );
    }
    let walled = rise.f().abs() < 1e-6;
    if walled && st.uu[2].f().abs() > 1e-6 {
        bail!(
            "_capped_anchor: the anchor at {place} roots on a wall with its tube along {}; a wall rib stands \
             its tube level, so its webs' corbels carry the flank that looks print-down. Close it with a zip \
             tie.",
            fmtv(&Val::tuple(st.u.iter()?), "")?
        );
    }
    let ceiling = st.key == [0, 0, 1] && up.f() < 0.0;
    // Under the ceiling the rib is struck up to the lane (`b_face`), inside the slab, and its
    // flanks end on the face the slab presents (`back_top_ceiling_face`); anywhere else they end
    // on the root face itself.
    let b_top = if ceiling { (back_top_ceiling_face(cx)? - st.m[2].f()) * st.nn[2].f() } else { b_face };
    if !ceiling {
        for pocket in call(cap, "wing_room", vec![frame.clone(), f(b_face)])?.iter()? {
            solid = solid.cut(&[Solid::from_val(&pocket)])?;
        }
    }
    let mut rib = Solid::from_val(&call(cap, "rib", vec![frame.clone(), f(b_face), st.seat.clone()])?);
    if walled {
        let t2 = Num::of(&frame.attr("t")?.get(Val::Int(2))?)?;
        let a_hang = number(cap, "RIB_R")?.f().copysign(up.neg().mul(t2).f());
        let deep = corbel_depth(cx, &st, roots, lane)?
            .context("'>' not supported between instances of 'NoneType' and 'float'")?;
        if deep > 1e-9 {
            for s0 in [-half, half - number(cap, "END_WEB")?.f()] {
                let at = call(&frame, "point", vec![f(0.0), f(0.0), f(s0)])?;
                let wedge = leaf(
                    cx,
                    "_anchor_corbel",
                    vec![at, st.u.clone(), st.n.clone(), cap.attr("END_WEB")?, f(a_hang), f(b_face), f(deep)],
                )?;
                rib = rib.fuse(&[wedge])?;
            }
        }
    }
    solid = solid.fuse(&[rib.clean()?])?;
    for window in call(cap, "windows", vec![frame, f(b_top)])?.iter()? {
        solid = solid.cut(&[Solid::from_val(&window)])?;
    }
    Ok(solid)
}

// --- the C14 tunnel and the keystone receptacle ---------------------------------------------------

/// The rounded rectangle the C14's shroud reaches out through, picked out of a wall's own
/// port list by the two heat-set stations that straddle it — `(x, z, across_x, across_z, r)`.
///
/// THE HOLE AND THE STATIONS ARE ONE PLACEMENT: `enclosure_assembly.c14_cutout` and
/// `enclosure_assembly.c14_stations` are both struck on `C14_STATION`, and both screws sit ON
/// the mating axis, so the aperture is the rect port standing midway between them. A tunnel
/// built round a hole that is not cut is a plug, and this is where that reads.
pub fn _c14_aperture(cx: &Cx, stations: &Val, ports: &Val) -> Result<(f64, f64, Num, Num, Num)> {
    let _ = cx;
    let ends = py::unpack(&py::tuple([stations.get(Val::Int(0))?, stations.get(Val::Int(-1))?]), 2)?;
    let first = py::unpack(&ends[0], 2)?;
    let last = py::unpack(&ends[1], 2)?;
    let (x0, z0, x1, z1) = (Num::of(&first[0])?, Num::of(&first[1])?, Num::of(&last[0])?, Num::of(&last[1])?);
    let (ax, az) = (x0.add(x1).f() / 2.0, z0.add(z1).f() / 2.0);
    for port in ports.iter()? {
        let items = port.iter()?;
        ensure!(items.len() >= 3, "not enough values to unpack");
        let size = &items[3..];
        let rect = matches!(&items[0], Val::Str(kind) if kind == "rect");
        if rect && (Num::of(&items[1])?.f() - ax).abs() < 1e-6 && (Num::of(&items[2])?.f() - az).abs() < 1e-6 {
            ensure!(size.len() >= 2, "not enough values to unpack");
            let radius = &size[2..];
            let r = if radius.is_empty() { Num::F(0.0) } else { Num::of(&radius[0])? };
            return Ok((ax, az, Num::of(&size[0])?, Num::of(&size[1])?, r));
        }
    }
    bail!(
        "the C14's two stations straddle (x {}, z {}) and this wall's port list carries no rounded rectangle \
         there. A tunnel built round a hole that is not cut is a plug, so the pack states one or the other and \
         not both halves of a placement.",
        num::fmt(ax, ".4g"),
        num::fmt(az, ".4g")
    )
}

/// The C14 tunnel's material and cutters — for the stations in `z0..z1`.
///
/// THE RECEPTACLE DOES NOT BEAR ON THIS WALL. It bears on the seating face, one
/// `c14_tunnel_len` inboard of the wall, and the customer's cord reaches it down a bore that is
/// the aperture itself and nothing else: the tunnel grows entirely OUTWARD of the hole, so
/// neither its section nor its two bores ever stand in the plug's way.
///
/// THE TUNNEL IS ONE BLOCK. From the pocket's mouth — `c14_pocket_depth` fore
/// of the seating face — to the wall, it is one rectangle of the half extents `c14_mount_half`
/// reads: the bore's section, the inserts' ligaments and the pocket's wall, whichever asks for
/// more on each axis. Its fore face is one plane, its flanks are two, and the flange's pocket
/// stands inside it everywhere. The block is clipped to the room, so above the aperture its
/// crown runs out into the top wall.
///
/// THIS STATION BELONGS TO CEILING-BEDDED BACK-TOP. `up` must therefore be `BACK_TOP_UP`: the
/// block's crown fuses into the ceiling slab, and its opposite horizontal face looks print-up.
/// What remains over air is the bore's own roof, a bridge the aperture's width between the two
/// block flanks.
///
/// THE FLANGE DROPS INTO ITS OWN PROFILE. The pocket is the purchased flange's exact
/// rounded/tapered outline at `c14_pocket_slip`, cut from the mouth to the seating face — the
/// plane the flange bears on, which does not move, and neither does either insert. Fore of the
/// mouth its exact slipped outline runs `c14_insertion_relief` further in Y- through the fixed
/// +X strip, so the two-ear moulding has a straight approach to its seat.
///
/// THE INSERTS ENTER THE SEATING FACE, from inside the machine like every other insert on this
/// box, and bottom on the wall's own inner face. The station is relieved back to `wall`
/// (`back_top_wall_reliefs`), so what stands over each blind end is `socket_cap` of wall and
/// the tunnel is the whole of what is left.
///
/// IT ROOTS ON `back_wall_t_at` AND NOT ON `inner`. The piece holding these stations carries
/// `back_top_wall_t` over most of this wall, so the plane the tunnel stands on is the section
/// read at the aperture — a tunnel rooted on the box's own rear plane would start a section
/// inside a wall that is thicker than that plane anywhere the relief does not reach. Beyond the
/// relief's ends the block's last millimetres stand inside that thicker wall, which is fused
/// stock and not a face.
#[allow(clippy::too_many_arguments)]
pub fn _c14_tunnel_geometry(
    cx: &Cx,
    inner: &[f64; 6],
    outer: &[f64; 6],
    stations: &Val,
    ports: &Val,
    z0: f64,
    z1: f64,
    up: Num,
) -> Result<Option<(Solid, Solid, Tup<Solid>)>> {
    let s = &cx.s;
    if !stations.truthy()? {
        return Ok(None);
    }
    let pairs = |stations: &Val| -> Result<Vec<(Num, Num)>> {
        stations
            .iter()?
            .iter()
            .map(|station| {
                let p = py::unpack(station, 2)?;
                Ok((Num::of(&p[0])?, Num::of(&p[1])?))
            })
            .collect()
    };
    if !pairs(stations)?.iter().all(|(_sx, sz)| z0 <= sz.f() && sz.f() <= z1) {
        return Ok(None);
    }
    if up.f() != s.BACK_TOP_UP {
        bail!(
            "the C14 station belongs to ceiling-bedded back-top ({} print-up), not a piece with print-up {}",
            num::fmt(s.BACK_TOP_UP, "g"),
            up.fmt("g")
        );
    }
    let (ax, az, wx, wz, r) = _c14_aperture(cx, stations, ports)?;
    let cap = back_wall_t_at(cx, Num::F(ax), Num::F(az))?;
    if (cap - s.socket_cap).abs() > s.stated_bound_tol {
        bail!(
            "the C14's aperture passes {} mm of wall and the cap over an insert's blind end is {}. The tunnel \
             runs one `heatset_depth` off that wall, so at any other section it holds either half an insert or a \
             cap and half a tunnel.",
            num::fmt(cap, ".2f"),
            num::fmt(s.socket_cap, "g")
        );
    }
    for (sx, sz) in pairs(stations)? {
        if (back_wall_t_at(cx, sx, sz)? - cap).abs() > s.stated_bound_tol {
            bail!(
                "the C14's station at (x {}, z {}) stands on {} mm of wall and the aperture it straddles on {} — \
                 one relief no longer covers this tunnel's fastening field, so an insert would bottom on a plane \
                 the tunnel does not root on.",
                sx.fmt(".4g"),
                sz.fmt(".4g"),
                num::fmt(back_wall_t_at(cx, sx, sz)?, ".2f"),
                num::fmt(cap, ".2f")
            );
        }
    }
    let aft = outer[3] - cap;
    let fore = aft - s.c14_tunnel_len;
    let mouth = fore - s.c14_pocket_depth;
    let screw_reach = num::max_of(pairs(stations)?.iter().map(|(sx, _sz)| (sx.f() - ax).abs()))
        .context("max() arg is an empty sequence")?;
    let (hx, hz) = c14_mount_half(cx, wx, wz, screw_reach)?;
    // The block keeps the one section `c14_mount_half` states. Its crown enters the grown
    // ceiling slab by more than one wall, joining the two as one continuous volume.
    let block = ybox(cx, [f(ax - hx), f(ax + hx), f(mouth), f(aft), f(az - hz), f(az + hz)])?;
    let feature = supported_cut(cx, block, up)?
        .intersect(&[ybox(cx, [f(inner[0]), f(inner[1]), f(mouth), f(aft), f(inner[4]), f(inner[5])])?])?;
    // The cord bore continues through the wall and tunnel. The exact flange pocket opens through
    // the block's fore face and continues inboard through the +X strip for assembly access; its
    // stopped +Y end is the face the flange bears on.
    let flange_pocket = leaf(
        cx,
        "c14_pocket_prism",
        vec![f(s.c14_pocket_slip), f((mouth - s.c14_pocket_overcut) - s.c14_insertion_relief), f(fore)],
    )?
    .translate(&floats([ax, 0.0, az]))?
    .val()?;
    let bore = leaf(cx, "_rect_cut_y", vec![f(ax), f(az), wx.val(), wz.val(), r.val(), f(fore), f(outer[3] + 1.0)])?
        .fuse(&[flange_pocket])?;
    let bore = supported_cut(cx, bore, up)?;
    let mut inserts = vec![];
    for (sx, sz) in pairs(stations)? {
        let insert =
            leaf(cx, "_ycyl", vec![f(s.heatset_dia / 2.0), sx.val(), sz.val(), f(fore), f(fore + s.heatset_depth)])?;
        inserts.push(supported_cut(cx, insert, up)?);
    }
    Ok(Some((feature, bore, Tup(inserts))))
}

/// The pocket the jack's body swings into: the module standard's, less the jack's own
/// slip in it, with the shared base fit at each wall.
pub fn keystone_pocket_width(cx: &Cx) -> Result<f64> {
    let k = &cx.s._keystone;
    Ok(number(k, "POCKET_W")?.sub(number(k, "FIT_SLIP")?).f() + 2.0 * fits(cx, "slip")?)
}

/// The unchanged jack's face and body with the enclosure's static mating clearance.
///
/// The purchased reference supplies the body envelope, lip depth, catch stations and swing
/// ease. Its illustrative receptacle dimensions do not set this printed part's fit. The pocket
/// runs from the lip to the jack's inner end, or on to `back` where the boss carrying it stands
/// deeper than the jack.
pub fn _keystone_pocket_cut(cx: &Cx, x: Num, z: Num, y_face: Num, back: Option<Num>) -> Result<(Solid, (Num, Num))> {
    let k = &cx.s._keystone;
    let aperture_w = number(k, "FACE_W")?.f() + 2.0 * fits(cx, "slip")?;
    let aperture_h = number(k, "FACE_H")?.f() + 2.0 * fits(cx, "slip")?;
    let pocket_w = keystone_pocket_width(cx)?;
    let pocket_h = number(k, "POCKET_H")?.sub(number(k, "FIT_SLIP")?).f() + 2.0 * fits(cx, "slip")?;
    let (y_lip, y_back) = (y_face.sub(number(k, "LIP_D")?), y_face.sub(number(k, "DEPTH")?));
    let aperture = leaf(
        cx,
        "_rect_cut_y",
        vec![x.val(), z.val(), f(aperture_w), f(aperture_h), f(0.0), y_lip.sub(Num::F(0.01)).val(), y_face.add(Num::F(0.01)).val()],
    )?;
    let pocket = leaf(
        cx,
        "_rect_cut_y",
        vec![
            x.val(),
            z.add(number(k, "POCKET_RISE")?).val(),
            f(pocket_w),
            f(pocket_h),
            f(0.0),
            back.unwrap_or(y_back).sub(Num::F(0.01)).val(),
            y_lip.add(Num::F(0.01)).val(),
        ],
    )?;
    let top = z.f() + aperture_h / 2.0;
    // The ease spans the lip as these two cut it, from the aperture's open end to the
    // pocket's front, and leaves the face `keystone_ease_shoulder` over the aperture's top edge.
    let rise = call(k, "ease_rise", vec![])?.num()?;
    let shoulder = cx.s.keystone_ease_shoulder;
    let face = y_face.add(Num::F(0.01));
    let lip = y_lip.add(Num::F(0.01));
    let section = py::list([
        py::tuple([face.val(), f(top)]),
        py::tuple([lip.val(), f(top)]),
        py::tuple([lip.val(), f(top + rise)]),
        py::tuple([f(face.f() - shoulder * number(k, "LIP_D")?.f() / rise), f(top + shoulder)]),
        py::tuple([face.val(), f(top + shoulder)]),
    ]);
    let ease = leaf(cx, "_yz_prism", vec![f(x.f() - aperture_w / 2.0), f(x.f() + aperture_w / 2.0), section])?;
    Ok((aperture.fuse(&[pocket])?.fuse(&[ease])?, (y_lip, y_back)))
}

/// Retain each catch's complete section at its pocket root and relieve its bridge face.
pub fn _keystone_catches(cx: &Cx, catches: Solid, up: Num) -> Result<Solid> {
    let loose = catches.solids()?;
    let keys = loose.iter().map(|s| s.bounding_box()?.attr("zmin")?.num()).collect::<Result<Vec<f64>>>()?;
    let lower = num::argmin(&keys, |k| *k).context("min() arg is an empty sequence")?;
    let lower = loose[lower].clone();
    let pocket_growth = num::max2(0.0, fits(cx, "slip")? - number(&cx.s._keystone, "FIT_SLIP")?.f() / 2.0);
    let mut out = Solid::Py(Val::None);
    for part in &loose {
        let sign = if part.method("isSame", vec![lower.to_val()], vec![])?.truthy()? { -1.0 } else { 1.0 };
        let mut rooted = part.fuse(&[part.translate(&py::tuple([Val::Int(0), Val::Int(0), f(sign * pocket_growth)]))?])?;
        // The fitted pocket grows by the same allowance across X: each catch runs on to both
        // side walls, which carry its bridge face.
        let east = rooted.translate(&py::tuple([f(pocket_growth), Val::Int(0), Val::Int(0)]))?;
        let west = rooted.translate(&py::tuple([f(-pocket_growth), Val::Int(0), Val::Int(0)]))?;
        rooted = rooted.fuse(&[east, west])?;
        // Lower catch's top faces print-down in a ceiling-bedded print, upper catch's
        // underside in a floor-bedded print. Moving its complete section preserves retention.
        if sign * up.f() > 0.0 {
            rooted = rooted.translate(&py::tuple([Val::Int(0), Val::Int(0), f(up.f() * fits(cx, "supported_surface")?)]))?;
        }
        out = if out.is_none() { rooted } else { out.fuse(&[rooted])? };
    }
    Ok(out)
}

/// The keystone receptacle's fixed material and cutter.
///
/// The pocket needs the full module-standard height. Its printed surround is clipped to the
/// interior-ceiling plane if a station ever carries it that high; at a lower station the clip
/// is inert and the whole receptacle stands in this wall.
///
/// THE BOSS STANDS ON A 45° WEB ON ITS PRINT-DOWN SIDE, the same one a port chip's boss and a
/// +X mounting boss stand on. `up` is the piece's print-up in the machine's frame: for `up > 0`
/// the web is under the block, falling from the free face's bottom edge to the wall; for
/// `up < 0` (`BACK_TOP_UP`) it is over the block, rising from the free face's top edge to the
/// wall at `b.ymax`. ITS FIGURE IS THE BLOCK'S OWN BOX — the wall face it roots on, the free
/// face it ends at, and the reach between them — and it takes the same ceiling clip.
///
/// Returns ``(feature, cutter, catches)``. The cutter is kept separate because it has to pass
/// through both the additive boss and the wall already present in the piece; the catches are
/// kept separate because they are fused only after that cut.
pub fn _keystone_receptacle_geometry(
    cx: &Cx,
    inner: &[f64; 6],
    outer: &[f64; 6],
    station: &Val,
    z0: f64,
    z1: f64,
    up: Num,
) -> Result<Option<(Solid, Solid, Solid)>> {
    let s = &cx.s;
    let k = &s._keystone;
    if matches!(station, Val::None) {
        return Ok(None);
    }
    let xz = py::unpack(station, 2)?;
    let (x, z) = (Num::of(&xz[0])?, Num::of(&xz[1])?);
    if !(z0 <= z.f() && z.f() <= z1) {
        return Ok(None);
    }
    let y_face = Num::of(&call(&s._data_fit, "jack_face_y", vec![f(outer[3])])?)?;
    let boss = call(
        k,
        "receptacle_boss",
        vec![x.val(), z.val(), y_face.val(), y_face.sub(Num::F(back_wall_t_at(cx, x, z)?)).val()],
    )?;
    let pair = py::unpack(&boss, 2)?;
    let mut block = solid(&pair[0]);
    let mut catches = solid(&pair[1]);
    let bound = |b: &Val, name: &str| -> Result<Num> { Num::of(&b.attr(name)?) };
    let mut cheek_in = 0.0;
    if !block.is_none() {
        // Preserve the receptacle's three-millimetre surrounding section after applying
        // the shared base fit to the purchased body's nominal dimensions.
        let bb = block.bounding_box()?;
        let pw = keystone_pocket_width(cx)?;
        let ph = number(k, "POCKET_H")?.sub(number(k, "FIT_SLIP")?).f() + 2.0 * fits(cx, "slip")?;
        let hz = ph / 2.0 + number(k, "RECEPTACLE_WALL")?.f();
        // The cheeks carry the run-out up to the wall face, where the clamp nut over this column
        // comes nearest. In a ceiling-bedded print their inner faces stand where its envelope,
        // on `back_top_port_row_z`, keeps `keystone_nut_clear` off their tops.
        cheek_in = pw / 2.0;
        if up.f() < 0.0 {
            let crest = (((z.add(number(k, "POCKET_RISE")?).f() + hz) + (outer[3] - back_wall_t_at(cx, x, z)?))
                - bound(&bb, "ymin")?.f());
            let footprint = call(&s._jg, "panel_footprint", vec![])?.get(Val::Int(0))?.num()?;
            let reach = footprint / 2.0 + s.keystone_nut_clear;
            let over = s.back_top_port_row_z - crest;
            cheek_in = num::max2(cheek_in, sqrt(num::max2(0.0, reach * reach - over * over))?);
        }
        let hx = cheek_in + number(k, "RECEPTACLE_WALL")?.f();
        let rise = z.add(number(k, "POCKET_RISE")?);
        block = ybox(
            cx,
            [f(x.f() - hx), f(x.f() + hx), bb.attr("ymin")?, bb.attr("ymax")?, f(rise.f() - hz), f(z.add(number(k, "POCKET_RISE")?).f() + hz)],
        )?;
    }
    let mut feature = if !block.is_none() { supported_cut(cx, block.clone(), up)? } else { Solid::Py(Val::None) };
    let mut below_ceiling = Solid::Py(Val::None);
    if !block.is_none() {
        let b = block.bounding_box()?;
        let edge = if up.f() > 0.0 { bound(&b, "zmin")? } else { bound(&b, "zmax")? }; // the block's print-down edge
        let (ymin, ymax) = (bound(&b, "ymin")?, bound(&b, "ymax")?);
        let web = py::list([
            py::tuple([ymax.val(), edge.val()]),
            py::tuple([ymin.val(), edge.val()]),
            py::tuple([ymax.val(), edge.sub(up.mul(ymax.sub(ymin))).val()]),
        ]);
        feature = feature.fuse(&[leaf(cx, "_yz_prism", vec![b.attr("xmin")?, b.attr("xmax")?, web])?])?;
        below_ceiling = ybox(
            cx,
            [f(outer[0] - 1.0), f(outer[1] + 1.0), f(outer[2] - 1.0), f(outer[3] + 1.0), f(outer[4] - 1.0), f(inner[5])],
        )?;
        feature = feature.intersect(&[below_ceiling.clone()])?;
        if !catches.is_none() {
            catches = catches.intersect(&[below_ceiling.clone()])?;
        }
    }
    if !block.is_none() {
        // Full surrounding stock joins the recessed receptacle to the actual wall. Only its two
        // three-millimetre side cheeks carry the longer run-out to the wall; between them, under
        // the soda union and its nut, the corbel turns back at 45 degrees onto the DATA pad's
        // own run-out.
        let b = block.bounding_box()?;
        let root = outer[3] - back_wall_t_at(cx, x, z)?;
        let (xmin, xmax) = (bound(&b, "xmin")?, bound(&b, "xmax")?);
        let (ymin, ymax) = (bound(&b, "ymin")?, bound(&b, "ymax")?);
        if root > ymax.f() {
            let extension = ybox(
                cx,
                [xmin.val(), xmax.val(), ymax.sub(Num::F(0.01)).val(), f(root + 0.01), b.attr("zmin")?, b.attr("zmax")?],
            )?;
            feature = feature.fuse(&[supported_cut(cx, extension, up)?])?;
            let edge = if up.f() > 0.0 { bound(&b, "zmin")? } else { bound(&b, "zmax")? };
            for (xa, xb) in [(xmin.val(), f(x.f() - cheek_in)), (f(x.f() + cheek_in), xmax.val())] {
                let web = py::list([
                    py::tuple([f(root), edge.val()]),
                    py::tuple([ymin.val(), edge.val()]),
                    py::tuple([f(root), edge.sub(up.mul(Num::F(root).sub(ymin))).val()]),
                ]);
                let cheek = leaf(cx, "_yz_prism", vec![xa, xb, web])?;
                feature = feature.fuse(&[cheek])?;
            }
            let pad = call_kw(&s._data_fit, "pad_runout", vec![station.clone(), f(outer[3])], vec![("up", up.val())])?;
            let pad = py::unpack(&pad, 2)?;
            let (pad_y, pad_z) = (Num::of(&pad[0])?, Num::of(&pad[1])?);
            let ridge = ymin.add(pad_y).div(Num::I(2)).sub(up.mul(pad_z.sub(edge)).div(Num::I(2)));
            let corbel = py::list([
                py::tuple([ymin.val(), edge.val()]),
                py::tuple([ridge.val(), edge.sub(up.mul(ridge.sub(ymin))).val()]),
                py::tuple([pad_y.add(Num::F(0.01)).val(), pad_z.add(up.mul(Num::F(0.01))).val()]),
                py::tuple([pad_y.add(Num::F(0.01)).val(), edge.val()]),
            ]);
            feature = feature.fuse(&[leaf(cx, "_yz_prism", vec![f(x.f() - cheek_in), f(x.f() + cheek_in), corbel])?])?;
            feature = feature.intersect(&[below_ceiling.clone()])?;
        }
    }
    let (cutter, _bands) = _keystone_pocket_cut(cx, x, z, y_face, None)?;
    if !catches.is_none() {
        catches = _keystone_catches(cx, catches, up)?;
    }
    Ok(Some((feature, supported_cut(cx, cutter, up)?, catches)))
}

/// Fuse the keystone's receptacle to its back-wall piece and open it.
///
/// A KEYSTONE IS HELD BY A RECEPTACLE AND NOT BY A HOLE. `riteav_keystone` states the whole of
/// it — an aperture at the show face, a lip behind it, a pocket taller than the aperture, an
/// ease over the aperture's top edge the body swings through, and two catches at the pocket's
/// back the tang and the latch snap over. This wall gives the lip its depth out of its own
/// section, and a boss standing inboard gives the rest.
///
/// THE BOSS IS FUSED, THEN THE POCKET IS CUT, THEN THE CATCHES ARE FUSED BACK. The catches
/// stand inside the pocket, and a cut running after them would take them off again.
///
/// AND THE BOSS STANDS ON A 45° WEB ON ITS PRINT-DOWN SIDE. `up` is the piece's print-up in
/// the machine's frame; the block's face that looks print-down is its reach off the wall of
/// ceiling starting in air, and the web is that reach taken back to the wall at
/// `relief_chamfer` (`_keystone_receptacle_geometry`).
pub fn _keystone_receptacle(
    cx: &Cx,
    solid: Solid,
    inner: &[f64; 6],
    outer: &[f64; 6],
    station: &Val,
    z0: f64,
    z1: f64,
    up: Num,
) -> Result<Solid> {
    let Some((feature, cutter, catches)) = _keystone_receptacle_geometry(cx, inner, outer, station, z0, z1, up)? else {
        return Ok(solid);
    };
    let mut solid = solid;
    if !feature.is_none() {
        solid = solid.fuse(&[feature])?;
    }
    solid = solid.cut(&[cutter])?;
    if !catches.is_none() {
        solid = solid.fuse(&[catches])?;
    }
    Ok(solid)
}

/// Fuse the complete C14 surround to its back-wall piece and open its bores. `up` is the
/// piece's print-up in the machine's frame (`_c14_tunnel_geometry`).
#[allow(clippy::too_many_arguments)]
pub fn _c14_tunnel(
    cx: &Cx,
    solid: Solid,
    inner: &[f64; 6],
    outer: &[f64; 6],
    stations: &Val,
    ports: &Val,
    z0: f64,
    z1: f64,
    up: Num,
) -> Result<Solid> {
    let Some((feature, bore, inserts)) = _c14_tunnel_geometry(cx, inner, outer, stations, ports, z0, z1, up)? else {
        return Ok(solid);
    };
    // The tunnel block is one surround with the wall, clipped on the interior-ceiling plane
    // where its crown reaches it.
    let mut solid = solid.fuse(&[feature])?;
    // The bore, opened through everything standing round it. The wall's own cutters run to its
    // inner face and this one runs to the tunnel's, so the hole is one rectangle end to end.
    solid = solid.cut(&[bore])?;
    for cutter in inserts.0 {
        solid = solid.cut(&[cutter])?;
    }
    Ok(solid)
}

// --- the pieces ------------------------------------------------------------------------------------

/// The Y and Z bands one quadrant owns, as `(y0, y1, z0, z1)` — what every station is tested
/// against before the piece grows or cuts it. Each band runs a millimetre past the shell at its
/// outer end and stops on the seam at its inner one, so a station on a seam plane belongs to
/// exactly one piece.
pub fn _piece_bands(cx: &Cx, bx: &Val, name: &str) -> Result<[f64; 4]> {
    cx.generated("_piece_bands", crate::py_args![bx.clone(), name.to_owned()], vec![])
}

/// Fit room at Y closures, Z shoulders and every enclosing core surface.
pub fn _seam_fit_reliefs(cx: &Cx, piece: Solid, bx: &Val, y_side: &str, z_side: &str) -> Result<Solid> {
    cx.generated("_seam_fit_reliefs", crate::py_args![piece, bx.clone(), y_side.to_owned(), z_side.to_owned()], vec![])
}

/// One printable quadrant of the box.
pub fn build_piece(cx: &Cx, bx: &Val, y_side: &str, z_side: &str, halves_cache: &Val) -> Result<Solid> {
    cx.generated(
        "build_piece",
        crate::py_args![bx.clone(), y_side.to_owned(), z_side.to_owned(), halves_cache.clone()],
        vec![],
    )
}

// --- reporting ---------------------------------------------------------------------------------------

/// The display facet the front-top piece carries, measured on the built piece.
pub fn _report_facet(cx: &Cx, half: Solid, bx: &Val) -> Result<()> {
    cx.generated("_report_facet", crate::py_args![half, bx.clone()], vec![])
}

/// Each piece's size against the bed and every pair's shared volume.
pub fn _report_split(cx: &Cx, pieces: &Val, core: &Val, bx: &Val, installed_retainer: &Val) -> Result<()> {
    cx.generated(
        "_report_split",
        crate::py_args![pieces.clone(), core.clone(), bx.clone()],
        vec![("installed_retainer", installed_retainer.clone())],
    )
}

/// Each Z seam's height, whether it landed in a band its own column left open or
/// runs through that column on a clear lip, and the band the bed allowed it.
pub fn _report_seams(cx: &Cx, bx: &Val) -> Result<()> {
    cx.generated("_report_seams", crate::py_args![bx.clone()], vec![])
}

/// The corner stacks' figures for the pages and this file's own comments, in their order.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Figures(pub Vec<(&'static str, String)>);
impl Py for Figures {
    fn to_py(&self) -> Result<Val> {
        Ok(py::dict(self.0.iter().map(|(k, v)| (*k, Val::Str(v.clone())))))
    }
    fn from_py(value: &Val) -> Result<Self> {
        bail!("y_stack_figures are made here, not read: {}", value.repr()?)
    }
}

/// The corner stacks' figures for the pages and this file's own comments.
pub fn y_stack_figures(cx: &Cx, inner: &[f64; 6]) -> Result<Figures> {
    let s = &cx.s;
    let (lower, upper) = super::p2::y_stack(cx, inner)?;
    let (lower_rod, upper_rod) = super::p2::y_stack_rods(cx, inner)?;
    let boss = s.floor_heatset_dia + 2.0 * s.floor_heatset_min_wall;
    let g = num::fmt;
    Ok(Figures(vec![
        ("SIDE_BAND", format!("{} mm", g(s.side_band_inset, ".4g"))),
        ("LIP_LEN", format!("{} mm", g(s.lip_len, ".4g"))),
        ("Y_STACK_FRONT_ROOT", format!("{} mm", g(s.y_stack_front_root, ".4g"))),
        ("Y_STACK_AXIS_OUT", format!("{} mm", g(s.wall + s.y_stack_axis_in, ".4g"))),
        ("Y_STACK_LOWER_AXIS_OUT", format!("{} mm", g(s.wall + s.y_stack_lower_axis_in, ".4g"))),
        ("Y_STACK_CEILING", g(lower[0].z0, ".4g")),
        ("Y_STACK_UPPER_FLOOR", g(upper[0].z0, ".4g")),
        ("Y_STACK_DATUM", g(upper[0].z1, ".5g")),
        ("Y_STACK_HEAD_INTERFACE", g(s.y_stack_upper_head_datum + s.lip_len / 2.0, ".5g")),
        ("Y_STACK_GAP", format!("{} mm", g(fits(cx, "running")?, ".3g"))),
        ("Y_STACK_CLEARANCE", format!("Ø{}", g(s.y_stack_clearance_dia, ".3g"))),
        ("Y_STACK_CBORE", format!("{} mm", g(s.y_stack_cbore_depth, ".3g"))),
        ("Y_STACK_LOWER_CBORE", format!("{} mm", g(lower_rod.seat_z - lower[0].z0, ".4g"))),
        ("Y_STACK_INSERT_BOSS", format!("Ø{}", g(boss, ".3g"))),
        ("Y_STACK_INSERT_LIGAMENT", format!("{} mm", g(s.lip_len / 2.0 - boss / 2.0, ".2g"))),
        ("LOWER_ROD", format!("M5 × {}", g(lower_rod.length, "g"))),
        ("UPPER_ROD", format!("M5 × {}", g(upper_rod.length, "g"))),
    ]))
}

/// The Y seam's corner stacks as they were struck: each knuckle's piece and heights, and
/// each rod's seat, tip and insert, the same at both corners.
pub fn _report_stacks(cx: &Cx, bx: &Val) -> Result<()> {
    cx.generated("_report_stacks", crate::py_args![bx.clone()], vec![])
}

/// Each column's slide, PROVED on the built pieces.
pub fn _report_slide(cx: &Cx, pieces: &Val, bx: &Val) -> Result<Val> {
    cx.generated("_report_slide", crate::py_args![pieces.clone(), bx.clone()], vec![])
}

/// The handholds' bound.
pub fn _handhold_bound(cx: &Cx, pieces: &Val, bx: &Val) -> Result<Val> {
    cx.generated("_handhold_bound", crate::py_args![pieces.clone(), bx.clone()], vec![])
}

/// The ceiling show cap's bound.
pub fn _ceiling_show_cap_bound(cx: &Cx, back_top: Solid, bx: &Val) -> Result<Val> {
    cx.generated("_ceiling_show_cap_bound", crate::py_args![back_top, bx.clone()], vec![])
}

/// The silhouette's bound.
pub fn _silhouette_bound(cx: &Cx, pieces: &Val, bx: &Val) -> Result<Val> {
    cx.generated("_silhouette_bound", crate::py_args![pieces.clone(), bx.clone()], vec![])
}

/// The box at `appliance_width` × `rear_plane_y` × `appliance_height`, with `pack` measured
/// against it — the description `build_pieces` turns into the four printable pieces.
pub fn stated_box(cx: &Cx, pack: &Val, readings: &Val) -> Result<Val> {
    cx.generated("stated_box", crate::py_args![pack.clone()], vec![("readings", readings.clone())])
}

/// Each standing corner's column, and what it gave up to the pack standing in it.
pub fn _report_columns(cx: &Cx, bx: &Val) -> Result<()> {
    cx.generated("_report_columns", crate::py_args![bx.clone()], vec![])
}

/// Every bound in the ledger that is open, and nothing when they all hold.
///
/// The card `enclosure_assembly` writes is the committed account of these; this is the same
/// reading for whoever ran this module on its own, where there is no card.
pub fn _report_bounds(cx: &Cx) -> Result<()> {
    let bounds = cx.s.BOUNDS.iter()?;
    let mut open = vec![];
    for b in &bounds {
        if !b.attr("ok")?.truthy()? {
            open.push(b.clone());
        }
    }
    if open.is_empty() {
        return Ok(());
    }
    cx.rt.print(format!(
        "\n{} of {} bounds open — the box is drawn at its stated size anyway, so the overrun is in the pieces:",
        open.len(),
        bounds.len()
    ))?;
    for b in &open {
        cx.rt.print(format!(
            "  {}: {}   (wants {})",
            fmtv(&b.attr("id")?, "")?,
            fmtv(&b.attr("value")?, "")?,
            fmtv(&b.attr("target")?, "")?
        ))?;
        for line in b.attr("detail")?.iter()? {
            cx.rt.print(format!("    {}", fmtv(&line, "")?))?;
        }
    }
    cx.rt.print(String::new())?;
    Ok(())
}

/// Fill the enclosure's pages from its current numeric plan and measured readings.
pub fn _write_docs(cx: &Cx, bx: &Val, vent_read: &Val) -> Result<()> {
    cx.generated("_write_docs", crate::py_args![bx.clone(), vent_read.clone()], vec![])
}

// --- the box questions ---------------------------------------------------------------------------------

/// Six scalar extrema supplied by the existing fine-model reader.
pub fn _reading_bounds(cx: &Cx, lower: &Val, upper: &Val) -> Result<Val> {
    cx.generated("_reading_bounds", crate::py_args![lower.clone(), upper.clone()], vec![])
}

/// The placed bodies' bounds, in the pack's order.
pub fn _box_bound_rows(cx: &Cx, placed: &Val, bounds: &Val) -> Result<Vec<Val>> {
    cx.generated("_box_bound_rows", crate::py_args![placed.clone(), bounds.clone()], vec![])
}

/// The stated shell and seam datums from the pack's explicit raw extrema.
pub fn _box_question_frame(cx: &Cx, bounds: &Val) -> Result<([f64; 6], f64, (f64, f64))> {
    let s = &cx.s;
    let mut lows = vec![];
    for row in bounds.attr("values")?.call(vec![], vec![])?.iter()? {
        let pair = py::unpack(&row, 2)?;
        lows.push(pair[0].get(Val::Int(2))?.num()?);
    }
    let czmin = num::min_of(lows).context("min() arg is an empty sequence")?;
    let (ix0, ix1) = interior_x(cx)?;
    let iz0 = num::min2(czmin, 0.0) - s.floor_drop;
    let iz1 = ((iz0 - s.slab_t) + s.appliance_height) - s.ceiling_skin;
    Ok(([ix0, ix1, s.front_plane_y, s.rear_plane_y, iz0, iz1], s.y_seam, (s.z_seam, s.z_seam)))
}

/// The authored rail-lane boxes, in their native fusion order.
pub fn _lip_lane_boxes(cx: &Cx, inner: &[f64; 6], y_span: (f64, f64), plate: &Val, y_joint: f64) -> Result<Vec<[f64; 6]>> {
    let [_ix0, _ix1, _iy0, _iy1, iz0, iz1] = *inner;
    let (cy0, cy1) = y_span;
    let col = if cy1 <= y_joint + 1.0 { "front" } else { "back" };
    let mut boxes = vec![];
    for [x_in, sx, ry0, ry1, _lane] in z_rail_runs(cx, inner, y_joint, col, plate)? {
        let (ya, yb) = (num::max2(ry0, cy0), num::min2(ry1, cy1));
        if yb <= ya + 1e-6 {
            continue;
        }
        let [x_hk, _x_f, _x_a, x_h1] = rail_x(cx, x_in, sx, col)?;
        let x_open = x_hk - sx * cx.s.slide_slip;
        boxes.push([num::min2(x_open, x_h1), num::max2(x_open, x_h1), ya, yb, iz0, iz1]);
    }
    Ok(boxes)
}

/// The lip lane's ring for one column: the rail-lane boxes fused in order, or None for a
/// column with none.
pub fn _lip_lane_tool(cx: &Cx, inner: &[f64; 6], y_span: (f64, f64), plate: &Val, y_joint: f64) -> Result<Solid> {
    let mut ring = Solid::Py(Val::None);
    for coordinates in _lip_lane_boxes(cx, inner, y_span, plate, y_joint)? {
        let lane = ybox(cx, coordinates.map(f))?;
        ring = if ring.is_none() { lane } else { ring.fuse(&[lane])? };
    }
    Ok(ring)
}

/// A floor section's tool: the boss's Y and Z band across the body's X extent.
pub fn _floor_section_tool(cx: &Cx, bounds: &Val, boss: [f64; 4]) -> Result<Solid> {
    cx.generated("_floor_section_tool", crate::py_args![bounds.clone(), boss], vec![])
}

/// The curved source skin with its actual Y clip, front-flat and pillar cuts.
pub fn _under_lip_tool(
    cx: &Cx,
    inner: &[f64; 6],
    y_joint: f64,
    splits: [f64; 2],
    pump_trays: &Val,
    column: i64,
) -> Result<Solid> {
    let [ix0, ix1, _iy0, iy1, iz0, iz1] = *inner;
    let options = [(splits[0], (iz0 - 1.0, y_joint)), (splits[1], (y_joint, iy1 + 1.0))];
    let index = if column < 0 { column + 2 } else { column };
    ensure!((0..2).contains(&index), "tuple index out of range");
    let (zj, (cy0, cy1)) = options[index as usize];
    let mut band = lip_underwall(cx, inner, y_joint, zj)?
        .intersect(&[ybox(cx, [f(ix0 - 1.0), f(ix1 + 1.0), f(cy0), f(cy1), f(iz0 - 1.0), f(iz1 + 1.0)])?])?;
    if zj == splits[0] && pump_trays.truthy()? {
        band = band.cut(&[front_flat_lip_drop(cx, inner, zj)?])?;
    }
    for [sx, sy] in cx.s.column_corners {
        band = band.cut(&[column_pillar(cx, inner, sx, sy, if sy < 0 { splits[0] } else { splits[1] })?])?;
    }
    Ok(band)
}

/// Small authored tools and ordered scalar questions for a referenced pack.
///
/// Bounds are ``name -> (lower, upper)`` raw f64 readings. Tool shapes are the
/// same source functions the direct geometry path calls; no body is loaded here.
pub fn box_question_tools(cx: &Cx, pack: &Val, bounds: &Val) -> Result<Val> {
    cx.generated("box_question_tools", crate::py_args![pack.clone(), bounds.clone()], vec![])
}

/// The enclosure step: `_enclosure_rust_driver.main`.
pub fn main(cx: &Cx) -> Result<Val> {
    let generate = cx.rt.member("_enclosure_rust_driver", "main")?;
    py::call(&generate, vec![])
}
