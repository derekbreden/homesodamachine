//! `_fittings`: the purchased hardware inside the cold core, as parametric stand-ins built to
//! their catalog envelopes. Directions are normalized, dotted and crossed by OCCT's own vector
//! (`cq.Vector`), as the source does; offsets along them are computed here.

use super::cad::Cq;
use super::*;

pub const NAME: &str = "_fittings";

pub const IN: f64 = 25.4;

pub const ELBOW_HEX_AF: f64 = 0.625 * IN;
pub const ELBOW_LEG: f64 = 0.81 * IN;
pub const ELBOW_BORE: f64 = 0.25 * IN;
pub const ELBOW_MALE_R: f64 = 0.5 * 0.4375 * IN;
pub const ELBOW_MALE_LEN: f64 = 0.26 * IN;
pub const SOCKET_R: f64 = 0.5 * 0.54 * IN;
pub const SOCKET_DEPTH: f64 = 0.5 * IN;

pub const MALE_ELBOW_THREAD: f64 = 0.52 * IN;
pub const MALE_ELBOW_HEIGHT: f64 = 1.256 * IN;
pub const MALE_ELBOW_BODY_D: f64 = 0.61 * IN;
pub const MALE_ELBOW_LENGTH: f64 = 1.063 * IN;
pub const MALE_ELBOW_POST_W: f64 = 0.4375 * IN;
pub const MALE_ELBOW_INSERTION: f64 = 0.665 * IN;
pub const MALE_ELBOW_FLOW_BORE: f64 = 4.3;
pub const MALE_ELBOW_TUBE_OD: f64 = 0.25 * IN;
pub const MALE_ELBOW_AXIS_REACH: f64 =
    MALE_ELBOW_HEIGHT - MALE_ELBOW_THREAD - MALE_ELBOW_BODY_D / 2.0;
pub const MALE_ELBOW_MOUTH_REACH: f64 = MALE_ELBOW_LENGTH - MALE_ELBOW_POST_W / 2.0;

pub const PRV_HEX_AF: f64 = 0.5625 * IN;
pub const PRV_HEX_H: f64 = 0.44 * IN;
pub const PRV_CAP_R: f64 = 0.5 * 0.62 * IN;
pub const PRV_CAP_H: f64 = 1.06 * IN;
pub const PRV_MALE_LEN: f64 = 0.5 * IN;

pub const REED_GLASS_LEN: f64 = 14.0;
pub const REED_GLASS_R: f64 = 1.25;

pub const TO92_W: f64 = 4.3;
pub const TO92_H: f64 = 5.2;
pub const TO92_CORNER_R: f64 = 1.2;

/// `+Z`, the default axis of the capsule, reed and TO-92 stand-ins.
pub const UP: [f64; 3] = [0.0, 0.0, 1.0];

/// Where a fitting's lateral socket hands its line on: `Mouth(pos, axis, diam)`.
#[derive(Clone, Copy, Debug)]
pub struct Mouth {
    pub pos: [f64; 3],
    pub axis: [f64; 3],
    pub diam: f64,
}

impl Mouth {
    /// The `Mouth` namedtuple Python sees.
    pub fn val(&self, rt: &Runtime) -> Result<Val> {
        state(rt)?.mouth.c(args![self.pos, self.axis, self.diam])
    }
}

pub struct State {
    pub cq: Cq,
    /// `Mouth = namedtuple('Mouth', ['pos', 'axis', 'diam'])`.
    pub mouth: Val,
    /// `_float_interface`.
    pub float: Val,
    /// `FLOAT_OD`, `FLOAT_H`, `FLOAT_BORE`, as the provider states them.
    pub float_od: Val,
    pub float_h: Val,
    pub float_bore: Val,
    pub pocket_od: f64,
    pub pocket_id: f64,
    pub pocket_depth: f64,
    pub magnet_od: f64,
    pub magnet_id: f64,
    pub magnet_thickness: f64,
    pub magnet_seat: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let cq = Cq::new(rt)?;
        let mouth = rt.namedtuple("Mouth", "pos axis diam", NAME)?;
        let float = rt.py("_float_interface")?;
        let float_od = float.a("diameter")?;
        let float_h = float.a("height")?;
        let float_bore = float.a("bore_diameter")?;
        let f = |name: &str| -> Result<f64> { float.a(name)?.f() };
        Ok(Self {
            pocket_od: f("pocket_od")?,
            pocket_id: f("pocket_id")?,
            pocket_depth: f("pocket_depth")?,
            magnet_od: f("magnet_od")?,
            magnet_id: f("magnet_id")?,
            magnet_thickness: f("magnet_thickness")?,
            magnet_seat: f("magnet_seat")?,
            cq,
            mouth,
            float_od,
            float_h,
            float_bore,
            float,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// The three coordinates of a `cq.Vector`, as `tuple(v)` reads them.
fn coords(v: &Val) -> Result<[f64; 3]> {
    <[f64; 3]>::from_val(&Val::Tuple(v.iter()?))
}

/// `cq.Vector(*v).normalized()`: the OCCT unit vector, and its coordinates.
fn unit(cq: &Cq, v: [f64; 3]) -> Result<[f64; 3]> {
    coords(&cq.vector(v)?.m("normalized", vec![])?)
}

/// `cq.Vector(x, y, z)` from int literals, as the source writes them.
fn ints(cq: &Cq, v: [i64; 3]) -> Result<Val> {
    cq.m.a("Vector")?.c(args![v[0], v[1], v[2]])
}

/// `_hex(across_flats, height)`: a hex prism standing on XY.
pub fn hex(rt: &Runtime, across_flats: f64, height: f64) -> Result<Val> {
    let cq = &state(rt)?.cq;
    let r = across_flats / 3f64.sqrt();
    let mut pts: Vec<Val> = (0..6i64)
        .map(|i| {
            let angle = radians((60 * i) as f64);
            (r * angle.cos(), r * angle.sin()).to_val()
        })
        .collect();
    pts.push(pts[0].clone());
    cq.workplane(args!["XY"], vec![])?
        .m("polyline", vec![Val::list(pts)])?
        .m("wire", vec![])?
        .m("extrude", args![height])?
        .m("val", vec![])
}

/// `_cyl(radius, height)`: a cylinder up +Z from the origin.
pub fn cyl(rt: &Runtime, radius: f64, height: f64) -> Result<Val> {
    let cq = &state(rt)?.cq;
    cq.solid(
        "makeCylinder",
        args![radius, height, ints(cq, [0, 0, 0])?, ints(cq, [0, 0, 1])?],
    )
}

/// `_orient(solid, axis)`: turn a solid built up +Z to stand along `axis`.
pub fn orient(rt: &Runtime, solid: Val, axis: [f64; 3]) -> Result<Val> {
    let cq = &state(rt)?.cq;
    let axis = cq.vector(axis)?.m("normalized", vec![])?;
    let z = ints(cq, [0, 0, 1])?;
    let dot = pmax(-1.0, pmin(1.0, z.m("dot", vec![axis.clone()])?.f()?));
    if dot > 1.0 - 1e-12 {
        return Ok(solid);
    }
    if dot < -1.0 + 1e-12 {
        return solid.m(
            "rotate",
            args![ints(cq, [0, 0, 0])?, ints(cq, [1, 0, 0])?, 180i64],
        );
    }
    let origin = ints(cq, [0, 0, 0])?;
    let normal = z.m("cross", vec![axis])?;
    solid.m("rotate", args![origin, normal, degrees(dot.acos())])
}

/// `solid.translate(cq.Vector(*v))`.
fn moved(cq: &Cq, solid: Val, v: [f64; 3]) -> Result<Val> {
    solid.m("translate", vec![cq.vector(v)?])
}

/// `street_elbow(corner=, up=, out=, up_leg=, out_leg=, male_len=)`: a barstock street elbow
/// whose two legs cross at `corner`, its male leg threading along `up`.
pub fn street_elbow(
    rt: &Runtime,
    corner: [f64; 3],
    up: [f64; 3],
    out: [f64; 3],
    up_leg: Option<f64>,
    out_leg: Option<f64>,
    male_len: Option<f64>,
) -> Result<(Val, Mouth)> {
    let s = state(rt)?;
    let cq = &s.cq;
    let up = unit(cq, up)?;
    let out = unit(cq, out)?;
    let c = corner;
    let up_leg = up_leg.unwrap_or(ELBOW_LEG);
    let out_leg = out_leg.unwrap_or(ELBOW_LEG);
    let male_len = male_len.unwrap_or(ELBOW_MALE_LEN);
    let leg_up = moved(cq, orient(rt, hex(rt, ELBOW_HEX_AF, up_leg)?, up)?, c)?;
    let leg_out = moved(cq, orient(rt, hex(rt, ELBOW_HEX_AF, out_leg)?, out)?, c)?;
    let stub = moved(
        cq,
        orient(rt, cyl(rt, ELBOW_MALE_R, male_len)?, up)?,
        add3(c, scale3(up, up_leg)),
    )?;
    let solid = leg_up.m("fuse", vec![leg_out])?.m("fuse", vec![stub])?;
    let bore_up = moved(
        cq,
        orient(rt, cyl(rt, ELBOW_BORE / 2.0, up_leg + male_len + 1.0)?, up)?,
        c,
    )?;
    let bore_out = moved(
        cq,
        orient(rt, cyl(rt, ELBOW_BORE / 2.0, out_leg + 1.0)?, out)?,
        c,
    )?;
    let socket = moved(
        cq,
        orient(rt, cyl(rt, SOCKET_R, pmin(SOCKET_DEPTH, out_leg))?, out)?,
        add3(c, scale3(out, out_leg - pmin(SOCKET_DEPTH, out_leg))),
    )?;
    let solid = solid
        .m("cut", vec![bore_up])?
        .m("cut", vec![bore_out])?
        .m("cut", vec![socket])?;
    let mouth = Mouth {
        pos: add3(c, scale3(out, out_leg)),
        axis: out,
        diam: ELBOW_BORE,
    };
    Ok((solid, mouth))
}

/// `male_elbow(corner=, up=, out=)`: the push-fit male elbow, one moulding, its thread along
/// `up` and its tube socket along `out`.
pub fn male_elbow(
    rt: &Runtime,
    corner: [f64; 3],
    up: [f64; 3],
    out: [f64; 3],
) -> Result<(Val, Mouth)> {
    let s = state(rt)?;
    let cq = &s.cq;
    let up = unit(cq, up)?;
    let out = unit(cq, out)?;
    let c = corner;
    let body_r = MALE_ELBOW_BODY_D / 2.0;
    let socket_body = moved(
        cq,
        orient(rt, cyl(rt, body_r, MALE_ELBOW_MOUTH_REACH)?, out)?,
        c,
    )?;
    let post = moved(
        cq,
        orient(
            rt,
            cyl(rt, MALE_ELBOW_POST_W / 2.0, body_r + MALE_ELBOW_AXIS_REACH)?,
            up,
        )?,
        sub3(c, scale3(up, body_r)),
    )?;
    let thread = moved(
        cq,
        orient(rt, cyl(rt, ELBOW_MALE_R, MALE_ELBOW_THREAD)?, up)?,
        add3(c, scale3(up, MALE_ELBOW_AXIS_REACH)),
    )?;
    let solid = socket_body.m("fuse", vec![post])?.m("fuse", vec![thread])?;
    let mouth = add3(c, scale3(out, MALE_ELBOW_MOUTH_REACH));
    let socket = moved(
        cq,
        orient(
            rt,
            cyl(rt, MALE_ELBOW_TUBE_OD / 2.0, MALE_ELBOW_INSERTION)?,
            out,
        )?,
        sub3(mouth, scale3(out, MALE_ELBOW_INSERTION)),
    )?;
    let bore_out = moved(
        cq,
        orient(
            rt,
            cyl(rt, MALE_ELBOW_FLOW_BORE / 2.0, MALE_ELBOW_MOUTH_REACH)?,
            out,
        )?,
        c,
    )?;
    let bore_up = moved(
        cq,
        orient(
            rt,
            cyl(
                rt,
                MALE_ELBOW_FLOW_BORE / 2.0,
                MALE_ELBOW_AXIS_REACH + MALE_ELBOW_THREAD + 1.0,
            )?,
            up,
        )?,
        c,
    )?;
    let solid = solid
        .m("cut", vec![socket])?
        .m("cut", vec![bore_out])?
        .m("cut", vec![bore_up])?;
    Ok((
        solid,
        Mouth {
            pos: mouth,
            axis: out,
            diam: MALE_ELBOW_TUBE_OD,
        },
    ))
}

/// `sv125(at=, axis=)`: the SV-125 relief valve, its male thread ending at `at`.
pub fn sv125(rt: &Runtime, at: [f64; 3], axis: [f64; 3]) -> Result<Val> {
    let s = state(rt)?;
    let cq = &s.cq;
    let axis = unit(cq, axis)?;
    let base = at;
    let stub = moved(
        cq,
        orient(rt, cyl(rt, ELBOW_MALE_R, PRV_MALE_LEN)?, axis)?,
        sub3(base, scale3(axis, PRV_MALE_LEN)),
    )?;
    let hexb = moved(cq, orient(rt, hex(rt, PRV_HEX_AF, PRV_HEX_H)?, axis)?, base)?;
    let cap = moved(
        cq,
        orient(rt, cyl(rt, PRV_CAP_R, PRV_CAP_H)?, axis)?,
        add3(base, scale3(axis, PRV_HEX_H)),
    )?;
    stub.m("fuse", vec![hexb])?.m("fuse", vec![cap])
}

/// `sv125_reach()`: how far the valve stands off its port.
pub fn sv125_reach() -> f64 {
    PRV_HEX_H + PRV_CAP_H
}

/// `float_capsule(centre=, axis=)`: an Aero float with its RC62, centred on `centre`.
pub fn float_capsule(rt: &Runtime, centre: [f64; 3], axis: [f64; 3]) -> Result<Val> {
    let s = state(rt)?;
    let cq = &s.cq;
    let axis = unit(cq, axis)?;
    let c = centre;
    let (od, h, bore) = (s.float_od.f()?, s.float_h.f()?, s.float_bore.f()?);
    let body = moved(
        cq,
        orient(rt, cyl(rt, od / 2.0, h)?, axis)?,
        sub3(c, scale3(axis, h / 2.0)),
    )?;
    let bore = moved(
        cq,
        orient(rt, cyl(rt, bore / 2.0, h + 2.0)?, axis)?,
        sub3(c, scale3(axis, h / 2.0 + 1.0)),
    )?;
    let pocket = cyl(rt, s.pocket_od / 2.0, s.pocket_depth)?
        .m("cut", vec![cyl(rt, s.pocket_id / 2.0, s.pocket_depth)?])?;
    let pocket = moved(
        cq,
        orient(rt, pocket, axis)?,
        add3(c, scale3(axis, s.magnet_seat - h / 2.0)),
    )?;
    let magnet = cyl(rt, s.magnet_od / 2.0, s.magnet_thickness)?
        .m("cut", vec![cyl(rt, s.magnet_id / 2.0, s.magnet_thickness)?])?;
    let magnet = moved(
        cq,
        orient(rt, magnet, axis)?,
        add3(c, scale3(axis, s.magnet_seat - h / 2.0)),
    )?;
    let float = body.m("cut", vec![bore])?.m("cut", vec![pocket])?;
    cq.class(
        "Compound",
        "makeCompound",
        vec![Val::list(vec![float, magnet])],
        vec![],
    )
}

/// `reed(centre=, axis=)`: a reed switch's glass, centred on `centre`.
pub fn reed(rt: &Runtime, centre: [f64; 3], axis: [f64; 3]) -> Result<Val> {
    let s = state(rt)?;
    let cq = &s.cq;
    let axis = unit(cq, axis)?;
    moved(
        cq,
        orient(rt, cyl(rt, REED_GLASS_R, REED_GLASS_LEN)?, axis)?,
        sub3(centre, scale3(axis, REED_GLASS_LEN / 2.0)),
    )
}

/// `to92(centre=, axis=)`: a TO-92 probe body, centred on `centre`.
pub fn to92(rt: &Runtime, centre: [f64; 3], axis: [f64; 3]) -> Result<Val> {
    let s = state(rt)?;
    let cq = &s.cq;
    let axis = unit(cq, axis)?;
    let body = cq
        .workplane(args!["XY"], vec![])?
        .m("rect", args![TO92_W, TO92_W])?
        .m("extrude", args![TO92_H])?
        .m("edges", args!["|Z"])?
        .m("fillet", args![TO92_CORNER_R])?
        .m("val", vec![])?;
    moved(
        cq,
        orient(rt, body, axis)?,
        sub3(centre, scale3(axis, TO92_H / 2.0)),
    )
}

/// `stand_x_along(solid, at=, axis=)`: turn a solid's +X onto `axis`, then move it to `at`.
pub fn stand_x_along(rt: &Runtime, solid: Val, at: [f64; 3], axis: [f64; 3]) -> Result<Val> {
    let cq = &state(rt)?.cq;
    let a = cq.vector(axis)?.m("normalized", vec![])?;
    let x = ints(cq, [1, 0, 0])?;
    let dot = pmax(-1.0, pmin(1.0, x.m("dot", vec![a.clone()])?.f()?));
    let turned = if dot > 1.0 - 1e-12 {
        solid
    } else if dot < -1.0 + 1e-12 {
        solid.m(
            "rotate",
            args![ints(cq, [0, 0, 0])?, ints(cq, [0, 0, 1])?, 180i64],
        )?
    } else {
        let origin = ints(cq, [0, 0, 0])?;
        let normal = x.m("cross", vec![a])?;
        solid.m("rotate", args![origin, normal, degrees(dot.acos())])?
    };
    moved(cq, turned, at)
}

/// A Python call's `(solid, mouth)` pair.
fn pair(rt: &Runtime, (solid, mouth): (Val, Mouth)) -> Result<Val> {
    Ok(Val::Tuple(vec![solid, mouth.val(rt)?]))
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "math", "math")?;
    ns.value("namedtuple", rt.import_module("collections")?.a("namedtuple")?);
    ns.value("cq", s.cq.m.clone());
    ns.value("IN", IN);
    ns.value("Mouth", s.mouth.clone());
    ns.func(rt, "_hex", |rt, c| {
        hex(rt, c.req(0, "across_flats")?, c.req(1, "height")?)
    });
    ns.func(rt, "_cyl", |rt, c| {
        let radius: f64 = c.req(0, "radius")?;
        let height: f64 = c.req(1, "height")?;
        let base = c.maybe::<Val>(2, "base")?;
        let axis = c.maybe::<Val>(3, "axis")?;
        if base.is_none() && axis.is_none() {
            return cyl(rt, radius, height);
        }
        let cq = &state(rt)?.cq;
        let base = match base {
            Some(v) => cq.vector_of(&v)?,
            None => ints(cq, [0, 0, 0])?,
        };
        let axis = match axis {
            Some(v) => cq.vector_of(&v)?,
            None => ints(cq, [0, 0, 1])?,
        };
        cq.solid("makeCylinder", args![radius, height, base, axis])
    });
    ns.func(rt, "_orient", |rt, c| {
        orient(rt, c.req(0, "solid")?, c.req(1, "axis")?)
    });
    ns.value("ELBOW_HEX_AF", ELBOW_HEX_AF);
    ns.value("ELBOW_LEG", ELBOW_LEG);
    ns.value("ELBOW_BORE", ELBOW_BORE);
    ns.value("ELBOW_MALE_R", ELBOW_MALE_R);
    ns.value("ELBOW_MALE_LEN", ELBOW_MALE_LEN);
    ns.value("SOCKET_R", SOCKET_R);
    ns.value("SOCKET_DEPTH", SOCKET_DEPTH);
    ns.func(rt, "street_elbow", |rt, c| {
        let corner = c.req(usize::MAX, "corner")?;
        let up = c.kw("up", UP)?;
        let out = c.req(usize::MAX, "out")?;
        let up_leg = c.kw::<Option<f64>>("up_leg", None)?;
        let out_leg = c.kw::<Option<f64>>("out_leg", None)?;
        let male_len = c.kw::<Option<f64>>("male_len", None)?;
        pair(rt, street_elbow(rt, corner, up, out, up_leg, out_leg, male_len)?)
    });
    ns.value("MALE_ELBOW_THREAD", MALE_ELBOW_THREAD);
    ns.value("MALE_ELBOW_HEIGHT", MALE_ELBOW_HEIGHT);
    ns.value("MALE_ELBOW_BODY_D", MALE_ELBOW_BODY_D);
    ns.value("MALE_ELBOW_LENGTH", MALE_ELBOW_LENGTH);
    ns.value("MALE_ELBOW_POST_W", MALE_ELBOW_POST_W);
    ns.value("MALE_ELBOW_INSERTION", MALE_ELBOW_INSERTION);
    ns.value("MALE_ELBOW_FLOW_BORE", MALE_ELBOW_FLOW_BORE);
    ns.value("MALE_ELBOW_TUBE_OD", MALE_ELBOW_TUBE_OD);
    ns.value("MALE_ELBOW_AXIS_REACH", MALE_ELBOW_AXIS_REACH);
    ns.value("MALE_ELBOW_MOUTH_REACH", MALE_ELBOW_MOUTH_REACH);
    ns.func(rt, "male_elbow", |rt, c| {
        let corner = c.req(usize::MAX, "corner")?;
        let up = c.req(usize::MAX, "up")?;
        let out = c.req(usize::MAX, "out")?;
        pair(rt, male_elbow(rt, corner, up, out)?)
    });
    ns.value("PRV_HEX_AF", PRV_HEX_AF);
    ns.value("PRV_HEX_H", PRV_HEX_H);
    ns.value("PRV_CAP_R", PRV_CAP_R);
    ns.value("PRV_CAP_H", PRV_CAP_H);
    ns.value("PRV_MALE_LEN", PRV_MALE_LEN);
    ns.func(rt, "sv125", |rt, c| {
        sv125(rt, c.req(usize::MAX, "at")?, c.req(usize::MAX, "axis")?)
    });
    ns.func(rt, "sv125_reach", |_, _| Ok(Val::Float(sv125_reach())));
    ns.value("_float", s.float.clone());
    ns.value("FLOAT_OD", s.float_od.clone());
    ns.value("FLOAT_H", s.float_h.clone());
    ns.value("FLOAT_BORE", s.float_bore.clone());
    ns.func(rt, "float_capsule", |rt, c| {
        float_capsule(rt, c.req(usize::MAX, "centre")?, c.kw("axis", UP)?)
    });
    ns.value("REED_GLASS_LEN", REED_GLASS_LEN);
    ns.value("REED_GLASS_R", REED_GLASS_R);
    ns.func(rt, "reed", |rt, c| {
        reed(rt, c.req(usize::MAX, "centre")?, c.kw("axis", UP)?)
    });
    ns.value("TO92_W", TO92_W);
    ns.value("TO92_H", TO92_H);
    ns.value("TO92_CORNER_R", TO92_CORNER_R);
    ns.func(rt, "to92", |rt, c| {
        to92(rt, c.req(usize::MAX, "centre")?, c.kw("axis", UP)?)
    });
    ns.func(rt, "stand_x_along", |rt, c| {
        let solid = c.req(0, "solid")?;
        stand_x_along(rt, solid, c.req(usize::MAX, "at")?, c.req(usize::MAX, "axis")?)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
