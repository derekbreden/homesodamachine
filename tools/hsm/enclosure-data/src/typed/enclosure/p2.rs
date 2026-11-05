//! Part 2 of `enclosure`: the functions whose first Python line is in 2117–3500 — the box `_dims`
//! measures, the display facet, the outer plan the reeded skin walks, the wall through-holes, the
//! funnel opening, the Y seam's corner stacks and lip, and the handholds through the standing floor.
//!
//! Every function is the Python function of the same name, typed: numbers are `f64` (the module's
//! constants are floats; an int literal of the Python stays an int where it reaches a document),
//! fixed tuples are arrays and Rust tuples, the corner stacks' rows are [`Knuckle`] and [`Rod`].
//! The names the recorders and machine-data replace while they call the module (`record_bound`,
//! `cq`, `_teardrop_y`, the geometry slots) are read from the namespace at every use. Provider
//! modules (`fits`, `funnel`, `funnel_frame`, `reeding`, `port_chip`, `flute_skin`) stay Python
//! objects; their constants are read once per namespace ([`Provided`]), their functions called at
//! every use.
#![allow(non_snake_case, non_upper_case_globals, dead_code, unused_imports)]
use super::{Cx, State};
use crate::typed::_enclosure_datums::{Plane, Vector};
use crate::typed::num::{self, Num};
use crate::typed::py::{self, Args, Kwargs, Py, Tup, Val};
use crate::py_args;
use anyhow::{Context, Result, bail, ensure};
use std::cell::{OnceCell, RefCell};
use std::rc::Rc;

/// The functions of this part that run typed: the hybrid build replaces exactly these.
pub const CONVERTED: &[&str] = &[
    "_facet_geom",
    "housing_back_y",
    "pcb_ridge",
    "_ridge_join",
    "_seat_back",
    "display_centre_x",
    "flank_x_at",
    "_plan_segments",
    "seam_cap_z",
    "plate_outline",
    "plan_perimeter",
    "flute_pitch",
    "plan_at",
    "flute_centres",
    "_display_point",
    "display_plane",
    "_display_cut_exit_depth",
    "disposal_field",
    "disposal_figures",
    "_funnel_frame",
    "_funnel_hole",
    "_funnel_cut_plan",
    "funnel_seat_z",
    "_handhold_levels",
    "_band_x",
    "y_stack_y",
    "_y_stack_gap",
    "_y_knuckle_faces",
    "y_stack",
    "y_stack_axis",
    "y_stack_rods",
    "_y_face_z",
    "_y_top_cap",
    "_handhold_y",
    "grip_interface",
    "_handhold_backing_end",
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
        "_facet_geom" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer"], &[])?;
            _facet_geom(cx, &req(&mut b, "outer")?)?.to_py()
        }),
        "housing_back_y" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer"], &[])?;
            housing_back_y(cx, &req(&mut b, "outer")?)?.to_py()
        }),
        "pcb_ridge" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer"], &[])?;
            pcb_ridge(cx, &req(&mut b, "outer")?)?.to_py()
        }),
        "_ridge_join" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer", "fore"], &[])?;
            let outer = req(&mut b, "outer")?;
            _ridge_join(cx, &outer, req(&mut b, "fore")?)?.to_py()
        }),
        "_seat_back" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["depth", "half_slope"], &[])?;
            let depth = req(&mut b, "depth")?;
            _seat_back(cx, depth, req(&mut b, "half_slope")?)?.to_py()
        }),
        "display_centre_x" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer"], &[])?;
            display_centre_x(cx, &req(&mut b, "outer")?).to_py()
        }),
        "flank_x_at" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["y", "outer"], &[])?;
            let y = req(&mut b, "y")?;
            flank_x_at(cx, y, &req(&mut b, "outer")?)?.to_py()
        }),
        "_plan_segments" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer"], &[])?;
            _plan_segments(cx, &req(&mut b, "outer")?).to_py()
        }),
        "seam_cap_z" => wrap(cx, |cx, args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            seam_cap_z(cx).to_py()
        }),
        "plate_outline" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["plate"], &[])?;
            plate_outline(cx, &b.req("plate")?)?.to_py()
        }),
        "plan_perimeter" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer"], &[])?;
            plan_perimeter(cx, &req(&mut b, "outer")?).to_py()
        }),
        "flute_pitch" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer"], &[])?;
            flute_pitch(cx, &req(&mut b, "outer")?)?.to_py()
        }),
        "plan_at" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["s", "outer"], &[])?;
            let s = req(&mut b, "s")?;
            plan_at(cx, s, &req(&mut b, "outer")?)?.to_py()
        }),
        "flute_centres" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer"], &[])?;
            flute_centres(cx, &req(&mut b, "outer")?)?.to_py()
        }),
        "_display_point" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer", "point"], &[])?;
            let outer = req(&mut b, "outer")?;
            _display_point(cx, &outer, req(&mut b, "point")?)?.to_py()
        }),
        "display_plane" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer"], &[])?;
            display_plane(cx, &req(&mut b, "outer")?)?.to_val(&cx.rt)
        }),
        "_display_cut_exit_depth" => wrap(cx, |cx, args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            _display_cut_exit_depth(cx).to_py()
        }),
        "disposal_field" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer"], &[])?;
            disposal_field(cx, &req(&mut b, "outer")?)?.to_py()
        }),
        "disposal_figures" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer"], &[])?;
            disposal_figures(cx, &req(&mut b, "outer")?)?.to_py()
        }),
        "_funnel_frame" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["inner", "outer"], &[])?;
            let inner = req(&mut b, "inner")?;
            _funnel_frame(cx, &inner, &req(&mut b, "outer")?)?.to_py()
        }),
        "_funnel_hole" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["centre"], &[])?;
            _funnel_hole(cx, req(&mut b, "centre")?)?.to_py()
        }),
        "_funnel_cut_plan" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["centre"], &[])?;
            _funnel_cut_plan(cx, req(&mut b, "centre")?)?.to_py()
        }),
        "funnel_seat_z" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["outer"], &[])?;
            funnel_seat_z(cx, &req(&mut b, "outer")?)?.to_py()
        }),
        "_handhold_levels" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["inner"], &[])?;
            _handhold_levels(cx, &req(&mut b, "inner")?)?.to_py()
        }),
        "_band_x" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["x_ext", "sx"], &[])?;
            let x_ext = req(&mut b, "x_ext")?;
            _band_x(cx, x_ext, req(&mut b, "sx")?).to_py()
        }),
        "y_stack_y" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["y_joint"], &[])?;
            y_stack_y(cx, req(&mut b, "y_joint")?)?.to_py()
        }),
        "_y_stack_gap" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["down_supported", "up_supported"], &[])?;
            let down = int_of(&b.req("down_supported")?)?;
            let up = int_of(&b.req("up_supported")?)?;
            _y_stack_gap_ints(cx, down, up)?.to_py()
        }),
        "_y_knuckle_faces" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["piece", "gap_below", "gap_above"], &[])?;
            let piece: String = req(&mut b, "piece")?;
            let below = b.req("gap_below")?.truthy()?;
            let above = b.req("gap_above")?.truthy()?;
            let (bottom, top) = knuckle_faces(&piece, below, above);
            Ok(py::tuple([py::s(bottom), py::s(top)]))
        }),
        "y_stack" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["inner"], &[])?;
            y_stack(cx, &req(&mut b, "inner")?)?.to_py()
        }),
        "y_stack_axis" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["x_in", "sx", "y_joint", "rod"], &[])?;
            let (x_in, sx, y_joint) = (req(&mut b, "x_in")?, req(&mut b, "sx")?, req(&mut b, "y_joint")?);
            let rod = b.opt("rod").map(|v| v.str()).transpose()?.unwrap_or_else(|| "upper".into());
            y_stack_axis(cx, x_in, sx, y_joint, &rod).to_py()
        }),
        "y_stack_rods" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["inner"], &[])?;
            y_stack_rods(cx, &req(&mut b, "inner")?)?.to_py()
        }),
        "_y_face_z" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["kind", "level", "x_in", "sx", "y_joint", "x", "y"], &[])?;
            let kind: String = req(&mut b, "kind")?;
            let level = req(&mut b, "level")?;
            let (x_in, sx, y_joint) = (req(&mut b, "x_in")?, req(&mut b, "sx")?, req(&mut b, "y_joint")?);
            let (x, y) = (req(&mut b, "x")?, req(&mut b, "y")?);
            _y_face_z(cx, &kind, level, x_in, sx, y_joint, x, y).to_py()
        }),
        "_y_top_cap" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["top", "z1", "depth"], &[])?;
            let top: String = req(&mut b, "top")?;
            let z1 = req(&mut b, "z1")?;
            _y_top_cap(cx, &top, z1, req(&mut b, "depth")?).to_py()
        }),
        "_handhold_y" => wrap(cx, |cx, args, kwargs| {
            py::bind(args, kwargs, &[], &[])?;
            _handhold_y(cx).to_py()
        }),
        "grip_interface" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["inner"], &[])?;
            let inner = opt(&mut b, "inner", None)?;
            grip_interface(cx, inner.as_ref())
        }),
        "_handhold_backing_end" => wrap(cx, |cx, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["y_joint", "y_side"], &[])?;
            let y_joint = req(&mut b, "y_joint")?;
            let y_side = b.req("y_side")?;
            match &y_side {
                Val::Str(side) => _handhold_backing_end(cx, y_joint, side)?.to_py(),
                // `raise ValueError(y_side)`: the error's text is the value's own.
                other => bail!("{}", other.str()?),
            }
        }),
        _ => return None,
    };
    Some(f)
}

// --- what this part reads from elsewhere ------------------------------------------------------------

/// Provider constants this part reads, each group read once per module namespace on first use:
/// side-effect-free module constants nothing reassigns.
#[derive(Default)]
struct Provided {
    fits: OnceCell<Fits>,
    funnel: OnceCell<Funnel>,
}
/// `fits.running`, `fits.slip`, `fits.supported_surface`.
#[derive(Clone, Copy)]
struct Fits {
    running: f64,
    slip: f64,
    supported_surface: f64,
}
/// `funnel.collar_w`, `collar_d`, `brim_overhang`, `collar_corner_r`, `brim_thickness`.
#[derive(Clone, Copy)]
struct Funnel {
    collar_w: f64,
    collar_d: f64,
    brim_overhang: f64,
    collar_corner_r: f64,
    brim_thickness: f64,
}
thread_local! {
    static PROVIDED: RefCell<Vec<(Val, Rc<Provided>)>> = const { RefCell::new(Vec::new()) };
}
/// `a is b` for the containers and namespaces this part compares.
fn same_object(a: &Val, b: &Val) -> bool {
    match (a, b) {
        (Val::Namespace(a), Val::Namespace(b)) | (Val::Dict(a), Val::Dict(b)) => Rc::ptr_eq(a, b),
        (Val::List(a), Val::List(b)) => Rc::ptr_eq(a, b),
        _ => false,
    }
}
fn provided(cx: &Cx) -> Rc<Provided> {
    PROVIDED.with(|held| {
        let mut held = held.borrow_mut();
        if let Some((_, p)) = held.iter().find(|(ns, _)| same_object(ns, &cx.ns.0)) {
            return p.clone();
        }
        let p = Rc::new(Provided::default());
        held.push((cx.ns.0.clone(), p.clone()));
        p
    })
}
fn number(object: &Val, name: &str) -> Result<f64> {
    object.attr(name)?.num().with_context(|| format!("provider constant {name}"))
}
fn once<T: Copy>(cell: &OnceCell<T>, make: impl FnOnce() -> Result<T>) -> Result<T> {
    if let Some(value) = cell.get() {
        return Ok(*value);
    }
    let value = make()?;
    let _ = cell.set(value);
    Ok(value)
}
/// The `fits` constants.
fn fits(cx: &Cx) -> Result<Fits> {
    once(&provided(cx).fits, || {
        let fits = &cx.s.fits;
        Ok(Fits {
            running: number(fits, "running")?,
            slip: number(fits, "slip")?,
            supported_surface: number(fits, "supported_surface")?,
        })
    })
}
/// The `funnel` constants.
fn funnel(cx: &Cx) -> Result<Funnel> {
    once(&provided(cx).funnel, || {
        let f = &cx.s._funnel;
        Ok(Funnel {
            collar_w: number(f, "collar_w")?,
            collar_d: number(f, "collar_d")?,
            brim_overhang: number(f, "brim_overhang")?,
            collar_corner_r: number(f, "collar_corner_r")?,
            brim_thickness: number(f, "brim_thickness")?,
        })
    })
}

/// `math.sqrt(x)`, with the runtime's domain error.
fn sqrt(x: f64) -> Result<f64> {
    ensure!(x >= 0., "math domain error");
    Ok(x.sqrt())
}
/// `int(x)` of a value the runtime holds: a bool or number, truncated.
fn int_of(v: &Val) -> Result<i64> {
    v.integer()
}
/// A tuple of floats as Python sees it.
fn floats<const N: usize>(values: [f64; N]) -> Val {
    py::ftuple(&values)
}

/// A replaceable name of the module, read from the namespace now.
fn slot(cx: &Cx, name: &str) -> Result<Val> {
    cx.ns.get(name)
}
/// `record_bound(bound)` through the namespace: the recorders and machine-data replace it.
fn record_bound(cx: &Cx, bound: Val) -> Result<Val> {
    py::call(&slot(cx, "record_bound")?, vec![bound])
}

// Other parts' functions this part calls.

fn back_flank_start(cx: &Cx, y_joint: f64) -> Result<f64> {
    cx.generated("back_flank_start", py_args![y_joint], vec![])
}
fn interior_x(cx: &Cx) -> Result<(f64, f64)> {
    cx.generated("interior_x", vec![], vec![])
}
fn back_top_wall_face(cx: &Cx) -> Result<f64> {
    cx.generated("back_top_wall_face", vec![], vec![])
}

// --- display facet (solid surface) --------------------------------------------------------------

/// The facet's frame: its angle, the profile's display-plane normal and origin, and the slope's
/// Y and Z run.
pub fn _facet_geom(cx: &Cx, outer: &[f64; 6]) -> Result<(f64, [f64; 3], [f64; 3], f64, f64)> {
    let p = profile(cx, &floats(*outer))?;
    let a = num::radians(cx.s.display_facet_angle_deg);
    let dy = cx.s.display_facet_slope * num::cos(a);
    let dz = cx.s.display_facet_slope * num::sin(a);
    Ok((a, p.normal, p.origin, dy, dz))
}

/// The two stations of `_swept_top.profile(outer)` this part reads.
struct Profile {
    normal: [f64; 3],
    origin: [f64; 3],
}
/// `_swept_top.profile(outer)`: the typed module's reading, `outer` as the caller holds it.
fn profile(cx: &Cx, outer: &Val) -> Result<Profile> {
    let p = crate::typed::_swept_top::profile_json(&cx.rt, outer)?;
    let three = |key: &str| -> Result<[f64; 3]> {
        let rows = p[key].as_array().with_context(|| format!("missing key '{key}'"))?;
        ensure!(rows.len() == 3, "unpack: expected 3, got {}", rows.len());
        let n = |i: usize| rows[i].as_f64().with_context(|| format!("profile {key}"));
        Ok([n(0)?, n(1)?, n(2)?])
    };
    Ok(Profile { normal: three("normal")?, origin: three("origin")? })
}

/// The Y the display housing reaches back to — the display wall's flat face, cut the full
/// width, one running fit ahead of the funnel frame's flat front, which is the silicone
/// brim's front edge. The frontmost the Y seam may sit, since the whole facet belongs to the
/// front top piece. The display pockets keep their functional backing.
///
/// ONE PLANE, NOT A REACH OFF THE 45°. The slab behind the face is
/// `display_facet_thickness` thick measured perpendicular to it, which would put
/// its back plane at a Y that walks with the slope and with the thickness — and
/// at the top face that plane stands aft of everything the display needs, over
/// the funnel's own throat. This states where the slab stops instead. The funnel is
/// placed in machine Y, so `outer` does not move it.
pub fn housing_back_y(cx: &Cx, outer: &[f64; 6]) -> Result<f64> {
    let _ = outer;
    let datums = py::method(&cx.s._funnel_frame_part, "roof_datums", vec![])?;
    Ok(py::item(&datums, "front")?.num()? - cx.s.slide_slip)
}

/// Intersection of the display pocket's up-slope end and the housing back.
///
/// The station sets the supporting rib's crown. Its normal depth is the housing
/// thickness; its slope coordinate follows the actual PCB pocket.
pub fn pcb_ridge(cx: &Cx, outer: &[f64; 6]) -> Result<(f64, f64)> {
    let p = display_plane(cx, outer)?;
    let r = p
        .origin
        .add(&p.y_dir.mul(cx.s.display_body_offset_slope + cx.s.display_pcb_slope / 2.0))
        .sub(&p.z_dir.mul(cx.s.display_facet_thickness));
    Ok((r.y, r.z))
}

/// The bulkhead rises toward the PCB ridge on a 45-degree supporting face.
pub fn _ridge_join(cx: &Cx, outer: &[f64; 6], fore: f64) -> Result<(f64, (f64, f64))> {
    let (ry, rz) = pcb_ridge(cx, outer)?;
    let jog = rz - (ry - fore).abs();
    Ok((jog, (fore + cx.s.ridge_wall_t, jog - cx.s.ridge_wall_t * (sqrt(2.0)? - 1.0))))
}

/// A pocket's aft extent, measured from the enclosure's front plane.
pub fn _seat_back(cx: &Cx, depth: f64, half_slope: f64) -> Result<f64> {
    let a = num::radians(cx.s.display_facet_angle_deg);
    let p = profile(cx, &py::tuple([0i64; 6].map(Val::Int)))?;
    Ok(p.origin[1] + half_slope * num::cos(a) + depth * num::sin(a))
}

/// The X the display's glass is centred on — the box's own middle, since the
/// facet runs wall to wall. Read by the counterbore that receives it and by
/// `enclosure_assembly`'s placement of the reference body, so the housing and
/// the part in it cannot land on two different centres.
pub fn display_centre_x(cx: &Cx, outer: &[f64; 6]) -> f64 {
    let _ = cx;
    (outer[0] + outer[1]) / 2.0
}

/// The ±X exterior SURFACE's own distance from x = 0 at depth `y` — the wall's plane down
/// the flat, and `corner_round`'s arc wherever the turn has begun.
///
/// A BORE STRUCK ON A PLANE LEAVES LESS BEHIND A TURN. `interior_x` stands one `wall` in from
/// the flat, so anything run to it leaves exactly `wall` down the middle of a face and less
/// than that anywhere the round has carried the surface inboard. What has to leave a stated
/// section behind the surface — `flute_backing` above all, since a flute is cut into that
/// same surface — reads this and not the plane.
pub fn flank_x_at(cx: &Cx, y: f64, outer: &[f64; 6]) -> Result<f64> {
    let (ox1, oy0, oy1) = (outer[1], outer[2], outer[3]);
    let r = cx.s.corner_round;
    if oy0 + r <= y && y <= oy1 - r {
        return Ok(ox1);
    }
    let off = num::min2(num::min2((y - (oy0 + r)).abs(), (y - (oy1 - r)).abs()), r);
    Ok((ox1 - r) + sqrt(num::pow(r, 2.0) - num::pow(off, 2.0))?)
}

/// One run of the outer plan: `(kind, length, data)`.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Segment {
    /// `("line", length, (start, direction, outward normal))`.
    Line { length: f64, start: [f64; 2], direction: [f64; 2], normal: [f64; 2] },
    /// `("arc", length, (centre, start angle, radius))`.
    Arc { length: f64, centre: [f64; 2], start: f64, radius: f64 },
}
impl Segment {
    pub fn length(&self) -> f64 {
        match self {
            Segment::Line { length, .. } | Segment::Arc { length, .. } => *length,
        }
    }
}
impl Py for Segment {
    fn to_py(&self) -> Result<Val> {
        Ok(match self {
            Segment::Line { length, start, direction, normal } => py::tuple([
                py::s("line"),
                Val::Float(*length),
                py::tuple([floats(*start), floats(*direction), floats(*normal)]),
            ]),
            Segment::Arc { length, centre, start, radius } => py::tuple([
                py::s("arc"),
                Val::Float(*length),
                py::tuple([floats(*centre), Val::Float(*start), Val::Float(*radius)]),
            ]),
        })
    }
    fn from_py(value: &Val) -> Result<Self> {
        let row = py::unpack(value, 3)?;
        let length = row[1].num()?;
        let data = py::unpack(&row[2], 3)?;
        Ok(match row[0].str()?.as_str() {
            "line" => Segment::Line { length, start: py::v2(&data[0])?, direction: py::v2(&data[1])?, normal: py::v2(&data[2])? },
            "arc" => Segment::Arc { length, centre: py::v2(&data[0])?, start: data[1].num()?, radius: data[2].num()? },
            other => bail!("unknown plan segment {other}"),
        })
    }
}

/// The outer plan boundary as (kind, length, data), walked from the FRONT WALL'S
/// CENTRELINE heading +X — four straight runs and the four `corner_round` quarter turns
/// between them, in order, each carrying its own length so a walk is an arc-length walk.
///
/// THE DATUM IS x = 0 ON THE FRONT WALL, which is the plane the whole machine is struck
/// about. A field whose datum sits there is symmetric in x whatever its pitch, because the
/// half-perimeter either way round is the same walk mirrored.
///
/// There is no turn at the Y seam and none is wanted: that arris is a telescoping mating
/// face, square by construction (`_round_z`), and the two pieces that meet on it present one
/// continuous plan between them.
pub fn _plan_segments(cx: &Cx, outer: &[f64; 6]) -> [Segment; 9] {
    let (ox0, ox1, oy0, oy1) = (outer[0], outer[1], outer[2], outer[3]);
    let r = cx.s.corner_round;
    let run_x = (ox1 - ox0) - 2.0 * r;
    let run_y = (oy1 - oy0) - 2.0 * r;
    let pi = std::f64::consts::PI;
    let turn = pi * r / 2.0;
    let line = |length, start, direction, normal| Segment::Line { length, start, direction, normal };
    let arc = |length, centre, start, radius| Segment::Arc { length, centre, start, radius };
    [
        line(run_x / 2.0, [0.0, oy0], [1.0, 0.0], [0.0, -1.0]),
        arc(turn, [ox1 - r, oy0 + r], -pi / 2.0, r),
        line(run_y, [ox1, oy0 + r], [0.0, 1.0], [1.0, 0.0]),
        arc(turn, [ox1 - r, oy1 - r], 0.0, r),
        line(run_x, [ox1 - r, oy1], [-1.0, 0.0], [0.0, 1.0]),
        arc(turn, [ox0 + r, oy1 - r], pi / 2.0, r),
        line(run_y, [ox0, oy1 - r], [0.0, -1.0], [-1.0, 0.0]),
        arc(turn, [ox0 + r, oy0 + r], pi, r),
        line(run_x / 2.0, [ox0 + r, oy0], [1.0, 0.0], [0.0, -1.0]),
    ]
}

/// THE PLANE THE Z SEAM'S OWN FURNITURE TOPS OUT UNDER, one `wall` over the lip rim.
///
/// Under it stand the lip, the rail heads, the stop blocks and every lane the top piece
/// sweeps them in; over it front-bottom stands nothing at all. So it is the plane a body
/// riding in front-top has to be above before it may reach out to the side wall, and the
/// floor the bay's interior flute storey is struck on. Across the front band the cradle
/// replaces this closure; aft of the opening the ordinary seam furniture remains.
pub fn seam_cap_z(cx: &Cx) -> f64 {
    cx.s.z_seam + cx.s.z_rise + cx.s.wall
}

/// The release band's rectangular X/Z extent within the continuous bay bulkhead.
pub fn plate_outline(cx: &Cx, plate: &Val) -> Result<Vec<(Val, Val)>> {
    let _ = cx;
    let (x0, x1) = (py::at(plate, "x0")?, py::at(plate, "x1")?);
    let (z0, z1) = (py::at(plate, "z0")?, py::at(plate, "z1")?);
    Ok(vec![(x0.clone(), z0.clone()), (x1.clone(), z0), (x1, z1.clone()), (x0, z1)])
}

/// How far it is round the box's outer plan once — what `flute_count` divides.
pub fn plan_perimeter(cx: &Cx, outer: &[f64; 6]) -> f64 {
    num::sum(_plan_segments(cx, outer).iter().map(Segment::length))
}

/// The spacing the field actually lands on. It is a CONSEQUENCE of `flute_count`, not a
/// figure of its own, because a stated pitch would leave the perimeter with a remainder and
/// the remainder has to go somewhere — one wrong land, at whichever station the array
/// happened to close on. `flute-closes` is what holds it near the coupon's.
pub fn flute_pitch(cx: &Cx, outer: &[f64; 6]) -> Result<f64> {
    ensure!(cx.s.flute_count != 0, "division by zero");
    Ok(plan_perimeter(cx, outer) / cx.s.flute_count as f64)
}

/// The outer plan boundary's point and OUTWARD normal at arc length `s` from the datum.
///
/// THE PLAN CLOSES, so any `s` is on it: the walk is taken modulo the perimeter and the box
/// has no station where the field restarts.
pub fn plan_at(cx: &Cx, s: f64, outer: &[f64; 6]) -> Result<([f64; 2], [f64; 2])> {
    let segments = _plan_segments(cx, outer);
    let total = num::sum(segments.iter().map(Segment::length));
    ensure!(total != 0., "modulo by zero");
    let walk = cx.ns.get("_walk")?;
    let at = py::call(&walk, vec![segments.to_py()?, Val::Float(num::modulo(s, total))])?;
    let at = py::unpack(&at, 2)?;
    Ok((py::v2(&at[0])?, py::v2(&at[1])?))
}

/// Every groove's arc length, the datum's first. `flute_count` of them, closing on the
/// perimeter exactly.
pub fn flute_centres(cx: &Cx, outer: &[f64; 6]) -> Result<Tup<f64>> {
    let pitch = flute_pitch(cx, outer)?;
    Ok(Tup((0..cx.s.flute_count).map(|k| k as f64 * pitch).collect()))
}

/// A point given in the display's own frame — `x` across, `y` up the slope, `z` out along the
/// normal — in machine coordinates.
pub fn _display_point(cx: &Cx, outer: &[f64; 6], point: [f64; 3]) -> Result<[f64; 3]> {
    let (_angle, normal, origin, _dy, _dz) = _facet_geom(cx, outer)?;
    let [x, y, z] = point;
    Ok([
        display_centre_x(cx, outer) + x,
        origin[1] + normal[2] * y + normal[1] * z,
        origin[2] - normal[1] * y + normal[2] * z,
    ])
}

/// The display face as a workplane centred on the glass — the frame everything let into the
/// facet is struck in, and the frame `enclosure_assembly` poses the cover plate onto. Its
/// +X is the box's, its +Y runs UP the slope, and its normal points out at the user, so a
/// feature cut to depth `d` is extruded `-d`.
///
/// `cq.Plane(origin=cq.Vector(*center), xDir=cq.Vector(1, 0, 0), normal=cq.Vector(*normal))`, with
/// `cq` as the namespace holds it now: the plane is the instance that call makes.
pub fn display_plane(cx: &Cx, outer: &[f64; 6]) -> Result<Plane> {
    let (_a, normal, origin, _dy, _dz) = _facet_geom(cx, outer)?;
    let center = [display_centre_x(cx, outer), origin[1], origin[2]];
    let cq = slot(cx, "cq")?;
    if same_object(&cq, &cx.rt.import("_enclosure_datums")?) {
        return Plane::new(
            Vector::new(center[0], center[1], center[2]),
            Vector::new(1.0, 0.0, 0.0),
            Vector::new(normal[0], normal[1], normal[2]),
        );
    }
    let vector = cq.attr("Vector")?;
    let at = py::call(&vector, center.iter().map(|&v| Val::Float(v)).collect())?;
    let x_dir = py::call(&vector, vec![Val::Int(1), Val::Int(0), Val::Int(0)])?;
    let n = py::call(&vector, normal.iter().map(|&v| Val::Float(v)).collect())?;
    let plane = py::call_kw(&cq.attr("Plane")?, vec![], vec![("origin", at), ("xDir", x_dir), ("normal", n)])?;
    Plane::read(&cx.rt, &plane)
}

pub fn _display_cut_exit_depth(cx: &Cx) -> f64 {
    let _ = cx;
    12.0
}

// --- wall through-holes -------------------------------------------------------------------------

/// The flat wall under the warning, including a quiet margin on all four sides.
pub fn disposal_field(cx: &Cx, outer: &[f64; 6]) -> Result<[f64; 6]> {
    let s = &cx.s;
    // `from _disposal_artwork import flat_bounds`
    cx.rt.import("_disposal_artwork")?;
    let [x0, x1, z0, z1] = crate::typed::_disposal_artwork::flat_bounds(
        &cx.rt,
        &s.disposal_lines,
        s.disposal_cap_height,
        s.disposal_raise + s.disposal_embed,
        s.disposal_line_gap,
        &s.disposal_font,
        &s.disposal_kind,
    )?;
    let (centre, bottom) = ((outer[0] + outer[1]) / 2.0, outer[4] + s.disposal_bottom);
    Ok([
        centre + x0 - s.disposal_margin,
        centre + x1 + s.disposal_margin,
        outer[3] - s.wall,
        outer[3] + s.disposal_raise,
        bottom + z0 - s.disposal_margin,
        bottom + z1 + s.disposal_margin,
    ])
}

/// The warning's figures for its document, as `disposal_figures` writes them.
#[derive(Clone, Debug, PartialEq)]
pub struct DisposalFigures {
    pub cap_height: String,
    pub relief: String,
    pub bottom: String,
    pub field_width: String,
    pub field_height: String,
    pub margin: String,
}
impl Py for DisposalFigures {
    fn to_py(&self) -> Result<Val> {
        Ok(py::dict([
            ("DISPOSAL_CAP_HEIGHT", py::s(&self.cap_height)),
            ("DISPOSAL_RELIEF", py::s(&self.relief)),
            ("DISPOSAL_BOTTOM", py::s(&self.bottom)),
            ("DISPOSAL_FIELD_WIDTH", py::s(&self.field_width)),
            ("DISPOSAL_FIELD_HEIGHT", py::s(&self.field_height)),
            ("DISPOSAL_MARGIN", py::s(&self.margin)),
        ]))
    }
    fn from_py(value: &Val) -> Result<Self> {
        let text = |key: &str| -> Result<String> { py::at(value, key)?.str() };
        Ok(DisposalFigures {
            cap_height: text("DISPOSAL_CAP_HEIGHT")?,
            relief: text("DISPOSAL_RELIEF")?,
            bottom: text("DISPOSAL_BOTTOM")?,
            field_width: text("DISPOSAL_FIELD_WIDTH")?,
            field_height: text("DISPOSAL_FIELD_HEIGHT")?,
            margin: text("DISPOSAL_MARGIN")?,
        })
    }
}

pub fn disposal_figures(cx: &Cx, outer: &[f64; 6]) -> Result<DisposalFigures> {
    let s = &cx.s;
    let field = disposal_field(cx, outer)?;
    Ok(DisposalFigures {
        cap_height: format!("{} mm", num::fmt(s.disposal_cap_height, "g")),
        relief: format!("{} mm", num::fmt(s.disposal_raise, "g")),
        bottom: format!("{} mm", num::fmt(s.disposal_bottom, "g")),
        field_width: format!("{} mm", num::fmt(field[1] - field[0], ".1f")),
        field_height: format!("{} mm", num::fmt(field[5] - field[4], ".1f")),
        margin: format!("{} mm", num::fmt(s.disposal_margin, "g")),
    })
}

// --- funnel opening (Zone C) --------------------------------------------------------------------

/// What the top wall has left to give the collar, `(x_lo, x_hi, y_lo, y_hi)`: BEHIND the
/// display facet's own back plane, inboard of the ±X side bands, and ahead of the back
/// wall.
///
/// THE FRONT IS A DIFFERENT KIND OF EDGE FROM THE OTHER THREE. On those three the frame runs
/// out into a free edge, and the flange overhangs the collar by `brim_overhang` to catch the
/// wall and hold the funnel out of the box. Forward the brim's front edge stands one running
/// fit behind the display wall, `housing_back_y`, which carries the display's backing.
pub fn _funnel_frame(cx: &Cx, inner: &[f64; 6], outer: &[f64; 6]) -> Result<[f64; 4]> {
    let s = &cx.s;
    let [ix0, ix1, _iy0, iy1, _iz0, _iz1] = *inner;
    Ok([
        ix0 + s.side_band_inset + s.funnel_band_gap, // clear of the −X side band
        ix1 - s.side_band_inset - s.funnel_band_gap, // clear of the +X side band
        housing_back_y(cx, outer)?,                  // behind the display wall
        iy1 - s.wall,                                // ahead of the +Y wall
    ])
}

/// Rectangle (x0, x1, y0, y1) of the funnel opening in the top wall: the placed funnel's
/// collar — funnel.py's own dims at the box's own `funnel` centre.
///
/// The funnel is pushed as far FORWARD as `_funnel_frame` allows, and reaches aft for
/// whatever plan area its capacity needs — so the opening may cross the Y seam. Both halves
/// take their share of the cut and the collar bridges it; what the seam gives up there is its
/// top-wall lip over the hole's span, which the mouth shelf's own relief already accounts
/// for (`_funnel_cut`).
///
/// Plan arithmetic off one centre. `with_funnel` states what that collar owes its frame.
pub fn _funnel_hole(cx: &Cx, centre: (f64, f64)) -> Result<[f64; 4]> {
    let (cx_, cy) = centre;
    let f = funnel(cx)?;
    let (w, d) = (f.collar_w, f.collar_d);
    Ok([cx_ - w / 2.0, cx_ + w / 2.0, cy - d / 2.0, cy + d / 2.0])
}

/// The collar opening with one running clearance on all four plan faces.
pub fn _funnel_cut_plan(cx: &Cx, centre: (f64, f64)) -> Result<[f64; 4]> {
    let [x0, x1, y0, y1] = _funnel_hole(cx, centre)?;
    let air = cx.s.funnel_collar_air;
    Ok([x0 - air, x1 + air, y0 - air, y1 + air])
}

/// The inset brim's bearing plane, one brim thickness below the roof.
pub fn funnel_seat_z(cx: &Cx, outer: &[f64; 6]) -> Result<f64> {
    Ok(outer[5] - funnel(cx)?.brim_thickness)
}

// --- split joint: telescoping lip + two corner stacks ------------------------------------------
//
// The front half's lip telescopes into the back half on both side walls and the ceiling, and its
// floor runs on inside the slab as a square-ended tongue (`_floor_tongue`). What holds the halves
// together is a STACK of knuckles in each ±X corner of the overlap, alternating between the
// pieces, with two vertical M5 screws through them.
//
//   * THE LOWER STACK is a three-knuckle hinge inside the two bottom pieces: back-bottom's
//     knuckle over the handhold, front-bottom's, and back-bottom's under the Z seam. The screw
//     drives up from the handhold ceiling, its head in the lower back knuckle and its thread in
//     an insert set in the top of the upper one, so back-bottom holds it at both ends and
//     front-bottom's knuckle hangs on it between them.
//   * THE UPPER STACK is front-top's roof head block, back-top's middle knuckle, and front-top's
//     lower insert block. The M5 × 100 drives down through all three into the lower block's
//     blind pilot. Front-top holds both ends of the screw and captures back-top between them;
//     the middle knuckle retains its running fit. With the screws out, front-top draws forward.
//
// Every face between knuckles keeps a running fit. A knuckle face that prints facing down rises
// 45° off the stock its piece prints it on (`_y_knuckle_faces`), so no knuckle asks for
// support. The passages are printed clearance holes.

/// Standing floor, lifting ceiling and the full section above it.
pub fn _handhold_levels(cx: &Cx, inner: &[f64; 6]) -> Result<[f64; 3]> {
    let bed = inner[4] - cx.s.slab_t;
    let roof = bed + cx.s.handhold_height + fits(cx)?.supported_surface;
    Ok([bed, roof, roof + cx.s.handhold_roof])
}

/// The side band's two faces inboard of a ±X exterior face: the thickened flank's inner face
/// and the cold core's flank plane, where the band ends.
pub fn _band_x(cx: &Cx, x_ext: f64, sx: f64) -> (f64, f64) {
    let s = &cx.s;
    (x_ext + sx * s.back_bottom_flank_t, x_ext + sx * (s.wall + s.y_stack_low_depth))
}

/// The Y run a corner stack stands in: a front knuckle's root fore of the seam to the back
/// pieces' thickened flank, which the back knuckles grow into.
pub fn y_stack_y(cx: &Cx, y_joint: f64) -> Result<(f64, f64)> {
    Ok((y_joint - cx.s.y_stack_front_root, back_flank_start(cx, y_joint)?))
}

/// Running room at a knuckle interface, counting each supported opposing face once.
pub fn _y_stack_gap(cx: &Cx, down_supported: bool, up_supported: bool) -> Result<f64> {
    _y_stack_gap_ints(cx, i64::from(down_supported), i64::from(up_supported))
}
/// `_y_stack_gap` of the two `int(..)` the Python takes of its arguments.
fn _y_stack_gap_ints(cx: &Cx, down: i64, up: i64) -> Result<f64> {
    let fits = fits(cx)?;
    Ok(fits.running + fits.supported_surface * (down + up) as f64)
}

/// How a knuckle's bottom and top faces run: "level", "aft" (rising one for one aft of
/// the seam plane) or "in" (rising one for one inboard of the interior face).
///
/// A face that prints facing down rises off the stock its own piece prints it on. Front-bottom's
/// knuckle grows aft off its handhold roof, so its underside rises aft, and the back knuckle it
/// stands over takes that slope on its top. Back-bottom's upper knuckle grows off its own skin,
/// so its underside rises inboard, and front-bottom's takes that slope on its top. Back-bottom's
/// lower knuckle bottoms on the handhold ceiling. Front-top's insert block rises inboard
/// off its lip band. Its roof head block rises aft, with the matching top of back-top's
/// middle block rising aft so that block grows forward when printed roof-down.
pub fn _y_knuckle_faces(cx: &Cx, piece: &str, gap_below: f64, gap_above: f64) -> (&'static str, &'static str) {
    let _ = cx;
    knuckle_faces(piece, gap_below != 0.0, gap_above != 0.0)
}
fn knuckle_faces(piece: &str, gap_below: bool, gap_above: bool) -> (&'static str, &'static str) {
    if piece == "front-bottom" {
        return ("aft", "in");
    }
    if piece == "back-bottom" {
        return (if gap_below { "in" } else { "level" }, if gap_above { "aft" } else { "level" });
    }
    if piece == "front-top" {
        return (if gap_below { "aft" } else { "in" }, "level");
    }
    ("level", "aft")
}

/// One knuckle of a corner stack, `(piece, z0, z1, gap_below, gap_above)`.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Knuckle {
    pub piece: &'static str,
    pub z0: f64,
    pub z1: f64,
    pub gap_below: f64,
    pub gap_above: f64,
}
/// The four pieces a knuckle or insert belongs to, as the stack names them.
fn piece_name(name: &str) -> Result<&'static str> {
    Ok(match name {
        "front-bottom" => "front-bottom",
        "back-bottom" => "back-bottom",
        "front-top" => "front-top",
        "back-top" => "back-top",
        other => bail!("not a corner-stack piece: {other}"),
    })
}
impl Py for Knuckle {
    fn to_py(&self) -> Result<Val> {
        Ok(py::tuple([
            py::s(self.piece),
            Val::Float(self.z0),
            Val::Float(self.z1),
            Val::Float(self.gap_below),
            Val::Float(self.gap_above),
        ]))
    }
    fn from_py(value: &Val) -> Result<Self> {
        let row = py::unpack(value, 5)?;
        Ok(Knuckle {
            piece: piece_name(&row[0].str()?)?,
            z0: row[1].num()?,
            z1: row[2].num()?,
            gap_below: row[3].num()?,
            gap_above: row[4].num()?,
        })
    }
}

/// Each corner's knuckles, bottom to top, as `(lower, upper)`: rows of
/// `(piece, z0, z1, gap_below, gap_above)`. z0 and z1 are the knuckle's bottom and top where
/// `_y_knuckle_faces` strikes them: a level face at its height, a face rising aft at the seam
/// plane `y_joint`, a face rising inboard at the interior face. The gaps are vertical, one
/// running fit measured square to the face.
///
/// The bottom pieces and front-top print +Z up; back-top prints on its roof.
pub fn y_stack(cx: &Cx, inner: &[f64; 6]) -> Result<([Knuckle; 3], [Knuckle; 3])> {
    let s = &cx.s;
    let [_bed, ceiling, crown] = _handhold_levels(cx, inner)?;
    let Fits { running, slip, .. } = fits(cx)?;
    let sloped = running * sqrt(2.0)?;
    let seated = _y_stack_gap(cx, false, false)?;
    // The first interface follows the head seat, retaining the same bearing shoulder over
    // the deeper head pocket. It also stays above the complete lifting-ceiling section.
    let top = s.z_seam;
    let lower_seat = top + s.y_stack_screw_length_tolerance - s.lower_rod_len;
    let fb0 = num::max2(crown + sloped - slip, lower_seat + s.y_stack_lower_plane_over_seat + sloped);
    // Back-bottom's insert anchor ends on the Z seam, with its complete root under the
    // back rail. The fully threaded screw bears on both faces of front-bottom's knuckle.
    let bb0 = top - s.y_stack_lower_anchor_face_drop + sloped;
    let k = |piece, z0, z1, gap_below, gap_above| Knuckle { piece, z0, z1, gap_below, gap_above };
    let lower = [
        k("back-bottom", ceiling, fb0 - sloped, 0.0, sloped),
        k("front-bottom", fb0, bb0 - sloped, sloped, sloped),
        k("back-bottom", bb0, top, sloped, 0.0),
    ];
    let roof = inner[5] + s.wall;
    let datum = s.y_stack_upper_datum;
    let head_seat = roof - s.y_stack_head_recess - s.y_stack_head_h;
    let pilot_bottom = num::min2(
        datum - s.floor_heatset_depth - s.mount_bore_relief,
        head_seat - s.upper_rod_len - s.y_stack_tip_clearance,
    );
    // The 45-degree underside clears the source-valve coil while retaining
    // three millimetres around the complete blind pilot and beneath its tip.
    let front_floor = pilot_bottom - s.y_stack_axis_in - s.floor_heatset_dia / 2. - s.wall - slip;
    let upper = [
        k("front-top", front_floor, datum, 0.0, seated),
        k("back-top", datum + seated, s.y_stack_upper_head_datum - sloped, seated, sloped),
        k("front-top", s.y_stack_upper_head_datum, roof, sloped, 0.0),
    ];
    Ok((lower, upper))
}

/// A screw axis in plan; the lower head passes the handhold's full-section inner wall.
pub fn y_stack_axis(cx: &Cx, x_in: f64, sx: f64, y_joint: f64, rod: &str) -> (f64, f64) {
    let s = &cx.s;
    let inset = if rod == "lower" { s.y_stack_lower_axis_in } else { s.y_stack_axis_in };
    (x_in + sx * inset, y_joint + s.lip_len / 2.0)
}

/// One corner screw, `(rod, seat_z, tip_z, length, insert_piece, insert_z0, insert_z1)`.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Rod {
    pub rod: &'static str,
    pub seat_z: f64,
    pub tip_z: f64,
    pub length: f64,
    pub insert_piece: &'static str,
    pub insert_z0: f64,
    pub insert_z1: f64,
}
impl Py for Rod {
    fn to_py(&self) -> Result<Val> {
        Ok(py::tuple([
            py::s(self.rod),
            Val::Float(self.seat_z),
            Val::Float(self.tip_z),
            Val::Float(self.length),
            py::s(self.insert_piece),
            Val::Float(self.insert_z0),
            Val::Float(self.insert_z1),
        ]))
    }
    fn from_py(value: &Val) -> Result<Self> {
        let row = py::unpack(value, 7)?;
        Ok(Rod {
            rod: match row[0].str()?.as_str() {
                "lower" => "lower",
                "upper" => "upper",
                other => bail!("not a corner-stack rod: {other}"),
            },
            seat_z: row[1].num()?,
            tip_z: row[2].num()?,
            length: row[3].num()?,
            insert_piece: piece_name(&row[4].str()?)?,
            insert_z0: row[5].num()?,
            insert_z1: row[6].num()?,
        })
    }
}

/// Each corner's two screws, the same both corners, as rows of
/// `(rod, seat_z, tip_z, length, insert_piece, insert_z0, insert_z1)`: where the head's
/// underside bears, where the tip ends, and the M5 insert its thread engages. Both inserts
/// are pressed in from the top of their knuckles. The lower screw enters its insert from the
/// deep end and its tip stands the length allowance past the insert's open top, so the
/// shortest screw still takes the whole insert; its head sits as deep in the handhold ceiling
/// as that leaves.
pub fn y_stack_rods(cx: &Cx, inner: &[f64; 6]) -> Result<(Rod, Rod)> {
    let s = &cx.s;
    let (lower, upper) = y_stack(cx, inner)?;
    let top = lower[2].z1;
    let seat = top + s.y_stack_screw_length_tolerance - s.lower_rod_len;
    let low = Rod {
        rod: "lower",
        seat_z: seat,
        tip_z: seat + s.lower_rod_len,
        length: s.lower_rod_len,
        insert_piece: lower[2].piece,
        insert_z0: top - s.floor_heatset_depth,
        insert_z1: top,
    };
    let (roof, datum) = (upper[2].z1, upper[0].z1);
    let seat = roof - s.y_stack_head_recess - s.y_stack_head_h;
    let high = Rod {
        rod: "upper",
        seat_z: seat,
        tip_z: seat - s.upper_rod_len,
        length: s.upper_rod_len,
        insert_piece: upper[0].piece,
        insert_z0: datum - s.floor_heatset_depth,
        insert_z1: datum,
    };
    Ok((low, high))
}

/// A knuckle face's height at one point in plan.
#[allow(clippy::too_many_arguments)]
pub fn _y_face_z(cx: &Cx, kind: &str, level: f64, x_in: f64, sx: f64, y_joint: f64, x: f64, y: f64) -> f64 {
    let _ = cx;
    if kind == "aft" {
        return level + (y - y_joint);
    }
    if kind == "in" {
        return level + sx * (x - x_in);
    }
    level
}

/// Where a knuckle's rising top levels off: one `wall` short of the free face it rises
/// toward, so the knuckle ends on a face rather than a 45° arris.
pub fn _y_top_cap(cx: &Cx, top: &str, z1: f64, depth: f64) -> Option<f64> {
    if top == "in" {
        return Some(z1 + depth - cx.s.wall);
    }
    if top == "aft" {
        return Some(z1 + cx.s.lip_len - cx.s.wall);
    }
    None
}

// --- handholds through the standing floor -------------------------------------------------------

pub fn _handhold_y(cx: &Cx) -> (f64, f64) {
    let s = &cx.s;
    (s.handhold_y - s.handhold_length / 2.0, s.handhold_y + s.handhold_length / 2.0)
}

/// Reference geometry for the recorded grip-cover trials.
pub fn grip_interface(cx: &Cx, inner: Option<&[f64; 6]>) -> Result<Val> {
    let floor_z = match inner {
        Some(inner) => inner[4],
        None => 0.0,
    };
    let class = cx.s._grip_interface.attr("GripInterface")?;
    py::call_kw(&class, vec![cx.ns.0.clone()], vec![("floor_z", Val::Float(floor_z))])
}

/// Square ends of the nominal-wall backing, separated by one running fit.
pub fn _handhold_backing_end(cx: &Cx, y_joint: f64, y_side: &str) -> Result<f64> {
    if !matches!(y_side, "front" | "back") {
        bail!("{y_side}");
    }
    let s = &cx.s;
    Ok(y_joint + s.lip_len - s.handhold_wall - (if y_side == "front" { fits(cx)?.running } else { 0.0 }))
}
