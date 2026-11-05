//! The anchor cap and the tube anchor it closes, in the anchor's own frame.
//!
//! `u` runs along the tube, `n` from the tube toward the face the rib roots on, and `t = n x u`; a
//! section point (a, b) stands at mid + a*t + b*n, with b = 0 on the tube's axis plane. That is the
//! frame `enclosure._tube_anchors` strikes every rib in, so one station places the rib, its catch
//! windows, the ceiling's wing room and the cap.
//!
//! THE RIB IS THE TIE RIB'S HALF PIPE WITHOUT THE TIE. A solid post, the seat bored into it and its
//! lips flat one `WALL` past the axis plane, with a catch window in each flank. Each window is a
//! closed pocket between the rib's two end webs, so on a piece printed root-down its bearing face
//! prints as a bridge web to web, the way the tie channel's crown did. On a rib rooted on a wall the
//! flank that looks print-down and its window's roof bridge web to web instead, and the two end
//! webs stand on the tied rib's own 45-degree corbels (`enclosure._capped_anchor`).
//!
//! THE CAP IS THE OTHER HALF OF THE PIPE, one section extruded `CAP_LEN` along the tube. Below the
//! axis plane it is solid from the bore out to its round back; two `WING`-thick wings rise up the
//! rib's flanks and each carries a lip that drops into its window. A `CAVITY` gap separates the
//! half pipe from each wing for `CAVITY_DEG` round the pipe, so a wing bends from the gap's round
//! end rather than from the axis plane. That length is what sets its strain going on
//! (`wing_strain`), and the cap's README holds it beside the accepted faucet display cover's.
//!
//! THE CAP IS CUT FOR THE 1/4" TUBE'S SEAT AND PRINTS STANDING ON ITS END. Every layer is the
//! whole section, so the wings bend along their extrusion lines, and no face overhangs.
//!
//! Typed state: the section constants, computed once at install from `dims.wall` and the three
//! fits. `Frame` is the class the Python stub declares; its methods (`"Frame.<method>"`) work on
//! the Python instance, whose `mid`, `u`, `n` and `t` they read once per call. CadQuery stays a
//! provider, reached by callback.
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_anchor_cap_interface";

/// The section constants, as the module computes them.
#[derive(Clone, Copy, Debug)]
pub struct Consts {
    pub wall: f64,
    pub tube_od: f64,
    /// The seat the rib bores for the tube.
    pub seat_r: f64,
    /// The rib's half-width, the tie rib's own.
    pub rib_r: f64,
    pub cap_len: f64,
    pub end_air: f64,
    pub window_len: f64,
    pub end_web: f64,
    pub rib_len: f64,
    /// The cap's half pipe, bore to the wing gap.
    pub saddle: f64,
    /// Each spring wing.
    pub wing: f64,
    /// Wing to rib flank.
    pub wing_air: f64,
    /// The lip's reach off its wing, the faucet cover's engagement.
    pub engage: f64,
    /// The straight face at the lip's tip.
    pub lip_tip: f64,
    /// The lip's ramp, degrees off the push.
    pub lead_in: f64,
    /// The wings' tops above the axis plane.
    pub wing_top: f64,
    /// How far round the half pipe the wing gap runs.
    pub cavity_deg: f64,
    /// The cap bore's eased edges...
    pub mouth: f64,
    /// ...run out this far round the bore.
    pub mouth_deg: f64,
    /// The rib's outer bottom edges, where the lips ride on.
    pub rib_chamfer: f64,
    /// Wing top to the face the rib roots on.
    pub headroom: f64,
    pub ramp_h: f64,
    pub lip_h: f64,
    /// The lip's flat retention face.
    pub lip_b: f64,
    pub wing_in: f64,
    pub wing_out: f64,
    pub saddle_r: f64,
    /// `WALL + WING_AIR - SADDLE`, whatever the seat.
    pub cavity: f64,
    pub window_depth: f64,
    pub window_b0: f64,
    pub window_b1: f64,
    pub slot_w: f64,
    pub slot_top: f64,
}

pub struct State {
    pub c: Consts,
    /// `SEAT_R` as `cap` and `rib` took it for their default.
    seat_r: Val,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("math", rt.import("math")?)?;
    let sys = rt.import("sys")?;
    ns.set("sys", sys)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let file = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let here = file.parent().context("_HERE")?.to_path_buf();
    ns.set("_HERE", Val::Path(here.clone()))?;
    py::sys_path_insert(rt, &py::path_str(&here))?;
    let cadlib = here.ancestors().nth(2).context("_HERE.parents[1]")?.join("cadlib");
    py::sys_path_insert(rt, &py::path_str(&cadlib))?;
    ns.set("dims", rt.import("_enclosure_interface")?)?;
    let fits = rt.import("fits")?;
    ns.set("fits", fits.clone())?;
    let slip = Num::of(&fits.attr("slip")?)?;
    let supported = Num::of(&fits.attr("supported_surface")?)?;
    let (s, sup) = (slip.f(), supported.f());

    let wall = super::_enclosure_interface::value(rt, "wall")?;
    // The tube every capped anchor holds, and the seat the rib bores for it.
    let tube_od = 6.35;
    let seat_r = tube_od / 2.0 + s;
    let rib_r = seat_r + wall;
    // Along the tube: the cap, its end air to each window end, and the rib's end webs past those.
    // One cap closes every capped crossing, so its rib has to stand whole on the shortest straight
    // among them: `co2-2`'s 16.85 mm between its two R14 bends.
    let cap_len = 10.0;
    let end_air = s;
    let window_len = cap_len + 2.0 * end_air;
    let end_web = wall;
    let rib_len = window_len + 2.0 * end_web;
    // The section.
    let (saddle, wing, wing_air, engage, lip_tip, lead_in) = (2.5, 1.5, s, 1.2, 0.9, 30.0);
    let (wing_top, cavity_deg, mouth, mouth_deg, rib_chamfer, headroom) = (10.3, 36.0, 0.45, 10.0, 0.8, 0.6);
    let ramp_h = engage / num::radians(lead_in).tan();
    let lip_h = lip_tip + ramp_h;
    let lip_b = wing_top - lip_h;
    let wing_in = rib_r + wing_air;
    let wing_out = wing_in + wing;
    let saddle_r = seat_r + saddle;
    let cavity = wing_in - saddle_r;
    // The window: deep enough for the lip's whole engagement with a slip and the bridged roof's
    // finish allowance beyond it, from the bearing face a slip and that allowance under the seated
    // lip up to where the flank ends (`window_top`), which is past a slip over where the lip's ramp
    // crosses the flank (`WINDOW_B1`).
    let bearing_play = slip.add(supported);
    let window_depth = engage + s + sup;
    let window_b0 = lip_b - bearing_play.f();
    let window_b1 = lip_b + lip_tip + (engage - wing_air) / engage * ramp_h + s;
    // The wing room a root face standing inside the wings' reach gives up: the wing, the spread its
    // lip makes passing the flank, and a slip either side, to `HEADROOM` over the wing tops.
    let slot_w = wing_air + wing + engage + 2.0 * s;
    let slot_top = wing_top + headroom;
    let c = Consts {
        wall, tube_od, seat_r, rib_r, cap_len, end_air, window_len, end_web, rib_len, saddle, wing,
        wing_air, engage, lip_tip, lead_in, wing_top, cavity_deg, mouth, mouth_deg, rib_chamfer,
        headroom, ramp_h, lip_h, lip_b, wing_in, wing_out, saddle_r, cavity, window_depth, window_b0,
        window_b1, slot_w, slot_top,
    };
    let f = Val::Float;
    for (name, value) in [
        ("WALL", f(wall)), ("TUBE_OD", f(tube_od)), ("SEAT_R", f(seat_r)), ("RIB_R", f(rib_r)),
        ("CAP_LEN", f(cap_len)), ("END_AIR", slip.val()), ("WINDOW_LEN", f(window_len)),
        ("END_WEB", f(end_web)), ("RIB_LEN", f(rib_len)), ("SADDLE", f(saddle)), ("WING", f(wing)),
        ("WING_AIR", slip.val()), ("ENGAGE", f(engage)), ("LIP_TIP", f(lip_tip)), ("LEAD_IN", f(lead_in)),
        ("WING_TOP", f(wing_top)), ("CAVITY_DEG", f(cavity_deg)), ("MOUTH", f(mouth)),
        ("MOUTH_DEG", f(mouth_deg)), ("RIB_CHAMFER", f(rib_chamfer)), ("HEADROOM", f(headroom)),
        ("RAMP_H", f(ramp_h)), ("LIP_H", f(lip_h)), ("LIP_B", f(lip_b)), ("WING_IN", f(wing_in)),
        ("WING_OUT", f(wing_out)), ("SADDLE_R", f(saddle_r)), ("CAVITY", f(cavity)),
        ("BEARING_PLAY", bearing_play.val()), ("WINDOW_DEPTH", f(window_depth)),
        ("WINDOW_B0", f(window_b0)), ("WINDOW_B1", f(window_b1)), ("SLOT_W", f(slot_w)),
        ("SLOT_TOP", f(slot_top)),
    ] {
        ns.set(name, value)?;
    }
    let seat_default = Val::Float(seat_r);
    rt.keep(MODULE, State { c, seat_r: seat_default.clone() });

    ns.def(rt, "Frame.__init__", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "mid", "u", "n"], &[])?;
        let this = b.req("self")?;
        let (mid, u, n) = (b.req("mid")?, b.req("u")?, b.req("n")?);
        frame_init(&this, &mid, &u, &n)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "Frame.point", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "a", "b", "s"], &[])?;
        let this = b.req("self")?;
        let (a, bb) = (b.f64("a")?, b.f64("b")?);
        let s = b.f64_or("s", 0.0)?;
        Ok(py::ftuple(&FrameView::of(&this)?.point(a, bb, s)))
    })?;
    ns.def(rt, "Frame.plane", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "s"], &[])?;
        let this = b.req("self")?;
        let s = b.f64("s")?;
        plane(rt, &this, s)
    })?;
    ns.def(rt, "Frame.prism", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "pts", "s0", "s1"], &[])?;
        let this = b.req("self")?;
        let pts = b.req("pts")?;
        let (s0, s1) = (Num::of(&b.req("s0")?)?, Num::of(&b.req("s1")?)?);
        prism(rt, &this, pts, s0, s1)
    })?;
    ns.def(rt, "Frame.section", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "start", "segments", "s0", "s1"], &[])?;
        let this = b.req("self")?;
        let start = b.req("start")?;
        let segments = Seg::all(&b.req("segments")?)?;
        let (s0, s1) = (Num::of(&b.req("s0")?)?, Num::of(&b.req("s1")?)?);
        section(rt, &this, &start, &segments, s0, s1)
    })?;
    ns.def(rt, "Frame.bore", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "r", "s0", "s1"], &[])?;
        let this = b.req("self")?;
        let r = b.req("r")?;
        let (s0, s1) = (Num::of(&b.req("s0")?)?, Num::of(&b.req("s1")?)?);
        bore(rt, &this, r, s0, s1)
    })?;
    ns.set("Frame", rt.python_type(MODULE, "Frame")?)?;
    ns.def(rt, "_lip", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["side"], &[])?;
        let side = Num::of(&b.req("side")?)?;
        Ok(lip(rt, side)?)
    })?;
    ns.def(rt, "_cavity", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["frame", "side", "s0", "s1"], &[])?;
        let frame = b.req("frame")?;
        let side = Num::of(&b.req("side")?)?;
        let (s0, s1) = (Num::of(&b.req("s0")?)?, Num::of(&b.req("s1")?)?);
        cavity_cut(rt, &frame, side, s0, s1)
    })?;
    let default = seat_default.clone();
    ns.def(rt, "cap", move |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["frame", "seat_r"], &[])?;
        let frame = b.req("frame")?;
        let seat_r = Num::of(&b.opt("seat_r").unwrap_or_else(|| default.clone()))?;
        cap(rt, &frame, seat_r)
    })?;
    let default = seat_default;
    ns.def(rt, "rib", move |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["frame", "b_root", "seat_r"], &[])?;
        let frame = b.req("frame")?;
        let b_root = b.req("b_root")?;
        let seat_r = b.opt("seat_r").unwrap_or_else(|| default.clone());
        rib(rt, &frame, b_root, seat_r)
    })?;
    ns.def(rt, "window_top", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["b_face"], &[])?;
        window_top(rt, b.req("b_face")?)
    })?;
    ns.def(rt, "windows", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["frame", "b_face"], &[])?;
        let frame = b.req("frame")?;
        Ok(Val::list(windows(rt, &frame, b.req("b_face")?)?))
    })?;
    ns.def(rt, "wing_room", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["frame", "b_face"], &[])?;
        let frame = b.req("frame")?;
        Ok(Val::list(wing_room(rt, &frame, &b.req("b_face")?)?))
    })?;
    ns.def(rt, "wing_strain", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Float(wing_strain(rt)?))
    })?;
    ns.def(rt, "wing_flex_len", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Float(wing_flex_len(rt)?))
    })?;
    ns.def(rt, "__getattr__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["name"], &[])?;
        let name = b.req("name")?;
        if matches!(&name, Val::Str(text) if text == "cq") {
            return rt.import("cadquery");
        }
        anyhow::bail!("module {} has no attribute {}", py::s(MODULE).repr()?, name.repr()?)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// The frame a `Frame` instance holds, read off it once.
#[derive(Clone, Copy, Debug)]
pub struct FrameView {
    pub mid: [f64; 3],
    pub u: [f64; 3],
    pub n: [f64; 3],
    pub t: [f64; 3],
}
impl FrameView {
    pub fn of(frame: &Val) -> Result<FrameView> {
        Ok(FrameView {
            mid: py::v3(&frame.attr("mid")?)?,
            u: py::v3(&frame.attr("u")?)?,
            n: py::v3(&frame.attr("n")?)?,
            t: py::v3(&frame.attr("t")?)?,
        })
    }
    /// `Frame.point(a, b, s)`: mid + a*t + b*n + s*u.
    pub fn point(&self, a: f64, b: f64, s: f64) -> [f64; 3] {
        std::array::from_fn(|k| self.mid[k] + a * self.t[k] + b * self.n[k] + s * self.u[k])
    }
}

/// `Frame.__init__`: an anchor's frame, `mid` on the tube's axis at the rib's centre, `u` along
/// the tube, `n` toward the root face; `t = n x u`.
fn frame_init(this: &Val, mid: &Val, u: &Val, n: &Val) -> Result<()> {
    this.setattr("mid", py::ftuple(&py::f64s(mid)?))?;
    let u = py::f64s(u)?;
    this.setattr("u", py::ftuple(&u))?;
    let n = py::f64s(n)?;
    this.setattr("n", py::ftuple(&n))?;
    let at = |v: &[f64], k: usize| v.get(k).copied().context("tuple index out of range");
    let t = [
        at(&n, 1)? * at(&u, 2)? - at(&n, 2)? * at(&u, 1)?,
        at(&n, 2)? * at(&u, 0)? - at(&n, 0)? * at(&u, 2)?,
        at(&n, 0)? * at(&u, 1)? - at(&n, 1)? * at(&u, 0)?,
    ];
    this.setattr("t", py::ftuple(&t))
}

/// `cq.Vector(*xyz)`.
fn vector(cq: &Val, xyz: &[f64; 3]) -> Result<Val> {
    py::call(&cq.attr("Vector")?, xyz.iter().map(|&v| Val::Float(v)).collect())
}

/// The section plane `s` along the tube; its x is `t` and its y comes out as `n`.
pub fn plane(rt: &Rt, frame: &Val, s: f64) -> Result<Val> {
    let cq = rt.import("cadquery")?;
    let f = FrameView::of(frame)?;
    let origin = vector(&cq, &f.point(0.0, 0.0, s))?;
    let (x_dir, normal) = (vector(&cq, &f.t)?, vector(&cq, &f.u)?);
    py::call_kw(&cq.attr("Plane")?, vec![], vec![("origin", origin), ("xDir", x_dir), ("normal", normal)])
}

/// `Frame.prism`: the polygon `pts` in the section plane at `s0`, extruded to `s1`.
pub fn prism(rt: &Rt, frame: &Val, pts: Val, s0: Num, s1: Num) -> Result<Val> {
    let cq = rt.import("cadquery")?;
    let wp = py::call(&cq.attr("Workplane")?, vec![plane(rt, frame, s0.f())?])?;
    let wp = py::method(&py::method(&wp, "polyline", vec![pts])?, "close", vec![])?;
    py::method(&py::method(&wp, "extrude", vec![s1.sub(s0).val()])?, "val", vec![])
}

/// One segment of a `Frame.section` outline: a line to a point, or a three-point arc.
#[derive(Clone, Debug)]
pub enum Seg {
    L(Val),
    A(Val, Val),
}
impl Seg {
    fn line(p: [Num; 2]) -> Seg {
        Seg::L(py::tuple(p))
    }
    fn arc(via: [Num; 2], end: [Num; 2]) -> Seg {
        Seg::A(py::tuple(via), py::tuple(end))
    }
    /// Python's segments: `("L", p)` lines, anything else `(kind, via, end)` arcs.
    fn all(segments: &Val) -> Result<Vec<Seg>> {
        segments.iter()?.iter().map(|seg| {
            let line = matches!(seg.get(Val::Int(0))?, Val::Str(kind) if kind == "L");
            Ok(if line { Seg::L(seg.get(Val::Int(1))?) } else { Seg::A(seg.get(Val::Int(1))?, seg.get(Val::Int(2))?) })
        }).collect()
    }
}

/// Lines ("L", p) and three-point arcs ("A", via, end) in (a, b), extruded s0..s1.
pub fn section(rt: &Rt, frame: &Val, start: &Val, segments: &[Seg], s0: Num, s1: Num) -> Result<Val> {
    let cq = rt.import("cadquery")?;
    let mut wp = py::call(&cq.attr("Workplane")?, vec![plane(rt, frame, s0.f())?])?;
    wp = py::method(&wp, "moveTo", start.iter()?)?;
    for seg in segments {
        wp = match seg {
            Seg::L(p) => py::method(&wp, "lineTo", p.iter()?)?,
            Seg::A(via, end) => py::method(&wp, "threePointArc", vec![via.clone(), end.clone()])?,
        };
    }
    let wp = py::method(&wp, "close", vec![])?;
    py::method(&py::method(&wp, "extrude", vec![s1.sub(s0).val()])?, "val", vec![])
}

/// `Frame.bore`: a cylinder of radius `r` on the tube's axis, s0..s1.
pub fn bore(rt: &Rt, frame: &Val, r: Val, s0: Num, s1: Num) -> Result<Val> {
    let cq = rt.import("cadquery")?;
    let f = FrameView::of(frame)?;
    let start = vector(&cq, &f.point(0.0, 0.0, s0.f()))?;
    let axis = vector(&cq, &f.u)?;
    py::call(&cq.attr("Solid")?.attr("makeCylinder")?, vec![r, s1.sub(s0).val(), start, axis])
}

/// A wing's lip: the flat retention face under it, the straight tip, and the ramp back out to
/// the wing's top inner corner, so no strip of the wing's inner face stands over the ramp.
pub fn lip(rt: &Rt, side: Num) -> Result<Val> {
    let c = state(rt)?.c;
    let pts = [
        (c.wing_in + 0.05, c.lip_b),
        (c.wing_in - c.engage, c.lip_b),
        (c.wing_in - c.engage, c.lip_b + c.lip_tip),
        (c.wing_in, c.lip_b + c.lip_h),
        (c.wing_in + 0.05, c.lip_b + c.lip_h),
    ];
    Ok(Val::list(pts.iter().map(|&(a, b)| py::tuple([side.mul(Num::F(a)), Num::F(b)])).collect()))
}

/// The gap between half pipe and wing, from above the axis plane `CAVITY_DEG` round the pipe
/// and round-ended there, so the wing's root is a full radius.
pub fn cavity_cut(rt: &Rt, frame: &Val, side: Num, s0: Num, s1: Num) -> Result<Val> {
    let c = state(rt)?.c;
    let t = num::radians(c.cavity_deg);
    let (r0, r1) = (c.saddle_r, c.wing_in);
    let (rm, rh) = ((r0 + r1) / 2.0, (r1 - r0) / 2.0);
    let end = [rm * num::cos(t) - rh * num::sin(t), -rm * num::sin(t) - rh * num::cos(t)];
    let pts: [(&str, Vec<[f64; 2]>); 5] = [
        ("L", vec![[r1, 0.5]]),
        ("L", vec![[r1, 0.0]]),
        ("A", vec![[r1 * num::cos(t / 2.0), -r1 * num::sin(t / 2.0)], [r1 * num::cos(t), -r1 * num::sin(t)]]),
        ("A", vec![end, [r0 * num::cos(t), -r0 * num::sin(t)]]),
        ("A", vec![[r0 * num::cos(t / 2.0), -r0 * num::sin(t / 2.0)], [r0, 0.0]]),
    ];
    let mirror = |p: [f64; 2]| [side.mul(Num::F(p[0])), Num::F(p[1])];
    let segments: Vec<Seg> = pts.iter().map(|(kind, rest)| {
        if *kind == "L" { Seg::line(mirror(rest[0])) } else { Seg::arc(mirror(rest[0]), mirror(rest[1])) }
    }).collect();
    let start = py::tuple([side.mul(Num::F(r0)), Num::F(0.5)]);
    section(rt, frame, &start, &segments, s0, s1)
}

/// The cap pushed home: its shoulders on the rib's lips at b = 0, centred on the station.
pub fn cap(rt: &Rt, frame: &Val, seat_r: Num) -> Result<Val> {
    let c = state(rt)?.c;
    let (s0, s1) = (-c.cap_len / 2.0, c.cap_len / 2.0);
    let (ca, sa) = (num::cos(num::radians(c.mouth_deg)), num::sin(num::radians(c.mouth_deg)));
    let f = Num::F;
    let neg = seat_r.neg();
    let segments = [
        Seg::line([f(c.wing_out), f(c.wing_top)]),
        Seg::line([f(c.wing_out), f(0.0)]),
        Seg::arc([f(0.0), f(-c.wing_out)], [f(-c.wing_out), f(0.0)]),
        Seg::line([f(-c.wing_out), f(c.wing_top)]),
        Seg::line([f(-c.wing_in), f(c.wing_top)]),
        Seg::line([f(-c.wing_in), f(0.0)]),
        Seg::line([neg.sub(f(c.mouth)), f(0.0)]),
        Seg::line([neg.mul(f(ca)), neg.mul(f(sa))]),
        Seg::arc([f(0.0), neg], [seat_r.mul(f(ca)), neg.mul(f(sa))]),
        Seg::line([seat_r.add(f(c.mouth)), f(0.0)]),
        Seg::line([f(c.wing_in), f(0.0)]),
    ];
    let start = py::ftuple(&[c.wing_in, c.wing_top]);
    let mut body = section(rt, frame, &start, &segments, f(s0), f(s1))?;
    for side in [1i64, -1] {
        let lip = prism(rt, frame, lip(rt, Num::I(side))?, f(s0), f(s1))?;
        body = py::method(&body, "fuse", vec![lip])?;
    }
    for side in [1i64, -1] {
        let gap = cavity_cut(rt, frame, Num::I(side), f(s0 - 1.0), f(s1 + 1.0))?;
        body = py::method(&body, "cut", vec![gap])?;
    }
    py::method(&body, "clean", vec![])
}

/// The rib, root face to the axis plane, its seat bored and its outer bottom edges chamfered.
/// The windows are cut from the piece once the rib is fused (`windows`).
pub fn rib(rt: &Rt, frame: &Val, b_root: Val, seat_r: Val) -> Result<Val> {
    let k = state(rt)?.c;
    let c = k.rib_chamfer;
    let f = Val::Float;
    let pts = Val::list(vec![
        py::tuple([f(-k.rib_r + c), f(0.0)]),
        py::tuple([f(k.rib_r - c), f(0.0)]),
        py::tuple([f(k.rib_r), f(c)]),
        py::tuple([f(k.rib_r), b_root.clone()]),
        py::tuple([f(-k.rib_r), b_root]),
        py::tuple([f(-k.rib_r), f(c)]),
    ]);
    let body = prism(rt, frame, pts, Num::F(-k.rib_len / 2.0), Num::F(k.rib_len / 2.0))?;
    let seat = bore(rt, frame, seat_r, Num::F(-k.rib_len / 2.0 - 1.0), Num::F(k.rib_len / 2.0 + 1.0))?;
    py::method(&body, "cut", vec![seat])
}

/// Where a window ends toward the root: where the flank it is cut in ends, so no band of
/// flank stands between the window and that face. That is the root face, or the top of the
/// wing room cut into it (`wing_room`), whose inner wall the flank runs on up.
pub fn window_top(rt: &Rt, b_face: Val) -> Result<Val> {
    let c = state(rt)?.c;
    Ok(if b_face.num()? < c.slot_top - c.headroom / 2.0 { Val::Float(c.slot_top) } else { b_face })
}

/// The two catch windows, each run out past its flank so the cut is clean, from its bearing
/// face to where the flank ends (`window_top`).
pub fn windows(rt: &Rt, frame: &Val, b_face: Val) -> Result<Vec<Val>> {
    let c = state(rt)?.c;
    let top = window_top(rt, b_face)?;
    let mut out = vec![];
    for side in [1i64, -1] {
        let side = Num::I(side);
        let (a_in, a_out) = (side.mul(Num::F(c.rib_r - c.window_depth)).val(), side.mul(Num::F(c.rib_r + 2.0)).val());
        let b0 = Val::Float(c.window_b0);
        let pts = Val::list(vec![
            py::tuple([a_in.clone(), b0.clone()]),
            py::tuple([a_out.clone(), b0]),
            py::tuple([a_out, top.clone()]),
            py::tuple([a_in, top.clone()]),
        ]);
        out.push(prism(rt, frame, pts, Num::F(-c.window_len / 2.0), Num::F(c.window_len / 2.0))?);
    }
    Ok(out)
}

/// Where the face the rib roots on stands inside the wings' reach, the slot each wing and
/// its spread take through that face, from a millimetre under it to `SLOT_TOP`. None where the
/// face leaves the wing tops at least half their `HEADROOM`, which no slot that shallow would
/// improve on.
pub fn wing_room(rt: &Rt, frame: &Val, b_face: &Val) -> Result<Vec<Val>> {
    let c = state(rt)?.c;
    let face = Num::of(b_face)?;
    if face.f() >= c.slot_top - c.headroom / 2.0 {
        return Ok(vec![]);
    }
    let mut out = vec![];
    for side in [1i64, -1] {
        let side = Num::I(side);
        let (a0, a1) = (side.mul(Num::F(c.rib_r)), side.mul(Num::F(c.rib_r + c.slot_w)));
        let low = face.sub(Num::F(1.0));
        let top = Num::F(c.slot_top);
        let pts = Val::list(vec![py::tuple([a0, low]), py::tuple([a1, low]), py::tuple([a1, top]), py::tuple([a0, top])]);
        out.push(prism(rt, frame, pts, Num::F(-c.window_len / 2.0), Num::F(c.window_len / 2.0))?);
    }
    Ok(out)
}

/// Peak strain in a wing as its lip passes the flank, on the beam estimate: the wing fixed
/// at the gap's round end, loaded across at the middle of the lip's flat tip, deflected by
/// `ENGAGE`. delta = F/EI * integral(lever^2 ds); strain = F * max lever * (WING / 2) / EI.
pub fn wing_strain(rt: &Rt) -> Result<f64> {
    let c = state(rt)?.c;
    let rm = (c.wing_in + c.wing_out) / 2.0;
    let load_b = c.lip_b + c.lip_tip / 2.0;
    let mut pts: Vec<[f64; 2]> = (0..41).map(|i| {
        let angle = -num::radians(c.cavity_deg) * (1.0 - i as f64 / 40.0);
        [rm * num::cos(angle), rm * num::sin(angle)]
    }).collect();
    pts.extend((1..21).map(|i| [rm, load_b * i as f64 / 20.0]));
    let integral = num::sum(pts.windows(2).map(|w| {
        let (p, q) = (w[0], w[1]);
        num::pow(load_b - (p[1] + q[1]) / 2.0, 2.0) * num::dist(&p, &q)
    }));
    let lever = num::max_of(pts.iter().map(|p| (load_b - p[1]).abs())).context("max() arg is an empty sequence")?;
    anyhow::ensure!(integral != 0.0, "division by zero");
    Ok(c.engage * lever * (c.wing / 2.0) / integral)
}

/// The wing's length from the gap's round end to the middle of the lip's tip.
pub fn wing_flex_len(rt: &Rt) -> Result<f64> {
    let c = state(rt)?.c;
    let rm = (c.wing_in + c.wing_out) / 2.0;
    Ok(rm * num::radians(c.cavity_deg) + c.lip_b + c.lip_tip / 2.0)
}
