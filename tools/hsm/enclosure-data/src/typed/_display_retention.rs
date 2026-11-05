//! The display cover's two skirts and the slots and catches the housing holds them with.
//!
//! Coordinates follow the machine display: X across, Y up the screen, Z out of the face.
//!
//! EACH SKIRT IS THE NAMEPLATE'S SNAP TAB RUN BROAD. Its thickness, reach, square lip, land and
//! bearing slip are `_nameplate_interface`'s, and it runs `LENGTH` along the display instead of
//! the tab's width. The housing's side of it is the nameplate receiver's too: a slot with a flex
//! lane to one side, and under the catch nothing at all. The catch is the ceiling of the storey
//! cavity beside the display (`enclosure.display_storey_cavities`), one a side from the flex lane
//! out to the side wall, open into the pump bay.
//!
//! Typed state: the skirt constants, read once at install from `_nameplate_interface`'s face and
//! `_enclosure_interface`. CadQuery stays a provider (`cq`), reached by callback.
use super::num::Num;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::Result;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_display_retention";

/// The skirt and pocket constants.
#[derive(Clone, Copy, Debug)]
pub struct Consts {
    pub wall: Num,
    pub length: Num,
    pub lip: Num,
    pub lip_start: Num,
    pub lip_land: Num,
    pub bearing_slip: Num,
    pub end_slip: Num,
    pub root: Num,
    pub depth: Num,
    pub outer_x: Num,
    /// The flat the lip catches under, one bearing slip above the lip's own shoulder.
    pub catch: Num,
    /// The slot runs the inset's own wall down to the catch; inboard it leaves the skirt room to
    /// bend in by the whole lip.
    pub neck_x: Num,
    pub flex_x: Num,
    pub run: Num,
}

pub struct State {
    pub cq: Val,
    pub c: Consts,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let tab = rt.import("_nameplate_interface")?;
    ns.set("_tab", tab.clone())?;
    let mut dims = vec![];
    for name in ["display_inset_x", "display_cover_slip", "display_cover_thickness"] {
        let value = rt.member("_enclosure_interface", name)?;
        ns.set(name, value.clone())?;
        dims.push(Num::of(&value)?);
    }
    let (inset_x, cover_slip, cover_thickness) = (dims[0], dims[1], dims[2]);
    let face = |name: &str| -> Result<Num> { Num::of(&tab.attr(name)?) };
    let wall = face("TAB_THICK")?;
    let length = Num::F(24.0);
    let lip = face("LIP")?;
    let lip_start = face("LIP_START")?;
    let lip_land = face("LIP_LAND")?;
    let bearing_slip = face("BEARING_SLIP")?;
    let end_slip = face("END_SLIP")?;
    let root = cover_thickness;
    let depth = root.add(face("TAB_LENGTH")?);
    let outer_x = inset_x.div(Num::F(2.0)).sub(cover_slip);
    let catch = root.add(lip_start).sub(bearing_slip);
    let neck_x = outer_x.add(cover_slip);
    let flex_x = outer_x.sub(wall).sub(lip);
    let run = length.add(Num::F(2.0).mul(end_slip));
    let c = Consts {
        wall, length, lip, lip_start, lip_land, bearing_slip, end_slip, root, depth, outer_x, catch,
        neck_x, flex_x, run,
    };
    for (name, value) in [
        ("WALL", wall), ("LENGTH", length), ("LIP", lip), ("LIP_START", lip_start), ("LIP_LAND", lip_land),
        ("BEARING_SLIP", bearing_slip), ("END_SLIP", end_slip), ("ROOT", root), ("DEPTH", depth),
        ("OUTER_X", outer_x), ("CATCH", catch), ("NECK_X", neck_x), ("FLEX_X", flex_x), ("RUN", run),
    ] {
        ns.set(name, value.val())?;
    }
    rt.keep(MODULE, State { cq, c });

    ns.def(rt, "_prism", move |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["profile", "length"], &[])?;
        let profile = b.req("profile")?;
        let length = Num::of(&b.opt("length").unwrap_or(Val::Float(24.0)))?;
        let mut points = vec![];
        for row in profile.iter()? {
            let pair = py::unpack(&row, 2)?;
            points.push((pair[0].clone(), pair[1].clone()));
        }
        prism(rt, &points, length)
    })?;
    ns.def(rt, "skirt", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["side"], &[])?;
        let side = Num::of(&b.opt("side").unwrap_or(Val::Int(1)))?;
        skirt(rt, side)
    })?;
    ns.def(rt, "pocket", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["side"], &[])?;
        let side = Num::of(&b.opt("side").unwrap_or(Val::Int(1)))?;
        pocket(rt, side)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// The closed polygon `profile` in XZ, extruded `length` along Y about Y = 0.
fn prism(rt: &Rt, profile: &[(Val, Val)], length: Num) -> Result<Val> {
    let cq = &state(rt)?.cq;
    let vector = cq.attr("Vector")?;
    let y = length.neg().div(Num::F(2.0)).val();
    let mut corners = vec![];
    for (x, z) in profile.iter().chain(profile.first()) {
        corners.push(py::call(&vector, vec![x.clone(), y.clone(), z.clone()])?);
    }
    if profile.is_empty() {
        anyhow::bail!("list index out of range");
    }
    let wire = py::call(&cq.attr("Wire")?.attr("makePolygon")?, vec![Val::list(corners)])?;
    let direction = py::call(&vector, vec![Val::Int(0), length.val(), Val::Int(0)])?;
    py::call(&cq.attr("Solid")?.attr("extrudeLinear")?, vec![wire, Val::list(vec![]), direction])
}

/// `[(side * px, z) for px, z in profile]`.
fn sided(side: Num, profile: &[(Num, Num)]) -> Vec<(Val, Val)> {
    profile.iter().map(|&(px, z)| (side.mul(px).val(), z.val())).collect()
}

/// One broad skirt: the nameplate tab's square catch and tapered nose.
pub fn skirt(rt: &Rt, side: Num) -> Result<Val> {
    let c = state(rt)?.c;
    let (x, r) = (c.outer_x, c.root);
    let profile = [
        (x.sub(c.wall), r.neg()),
        (x, r.neg()),
        (x, r.neg().sub(c.lip_start)),
        (x.add(c.lip), r.neg().sub(c.lip_start)),
        (x.add(c.lip), r.neg().sub(c.lip_start).sub(c.lip_land)),
        (x, c.depth.neg()),
        (x.sub(c.wall), c.depth.neg()),
    ];
    prism(rt, &sided(side, &profile), c.length)
}

/// The skirt's slot down to the catch, and the part of the storey cavity under the catch
/// that the skirt hangs into: one more lip past the lip's tip, to the skirt's own depth.
pub fn pocket(rt: &Rt, side: Num) -> Result<Val> {
    let c = state(rt)?.c;
    let one = Num::F(1.0);
    let slot = prism(rt, &sided(side, &[
        (c.flex_x, one), (c.neck_x, one), (c.neck_x, c.catch.neg()), (c.flex_x, c.catch.neg()),
    ]), c.run)?;
    let wide = c.outer_x.add(Num::F(2.0).mul(c.lip));
    let floor = c.depth.neg().sub(c.end_slip);
    let under = prism(rt, &sided(side, &[
        (c.flex_x, c.catch.neg()), (wide, c.catch.neg()), (wide, floor), (c.flex_x, floor),
    ]), c.run)?;
    py::method(&slot, "fuse", vec![under])
}
