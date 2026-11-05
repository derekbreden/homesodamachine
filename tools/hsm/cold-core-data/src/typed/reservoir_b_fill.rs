//! `_reservoir_b_fill`: the B-fill tube passage and its independent R14 bend holder, in
//! appliance XYZ. The passage's numbers are read once; every caller gets its own dict.

use std::cell::RefCell;

use super::above_core::AboveCore;
use super::cad::*;
use super::cold_core_interface as core;
use super::*;

pub const NAME: &str = "_reservoir_b_fill";

pub const BEND_RADIUS: f64 = 14.0;
pub const CHANNEL_DIAMETER: f64 = 6.8;
pub const WALL: f64 = 2.0;
pub const MOUTH: f64 = 0.5;
pub const CHANNEL_RADIUS: f64 = CHANNEL_DIAMETER / 2.0;
pub const CHANNEL_CENTRE: f64 = WALL + CHANNEL_RADIUS;

fn dome_lift() -> f64 {
    (2f64.sqrt() - 1.0) * CHANNEL_RADIUS
}

/// `passage()`, as numbers.
pub struct Passage {
    pub entry: [f64; 3],
    pub x: f64,
    pub y: f64,
    pub front: f64,
    pub floor: f64,
    pub tip: [f64; 3],
    /// `pose['translation_mm'][2]`, as the provider states it.
    pub lid_bottom: Val,
    /// `specification()['cap_face_z_mm']`.
    pub face: Val,
    pub supported: Val,
    pub cup_top: f64,
}

impl Passage {
    pub fn bend_end(&self) -> [f64; 3] {
        [self.x, self.y, self.floor]
    }
    /// The dict `passage()` returns.
    pub fn val(&self) -> Result<Val> {
        let face = self.face.f()?;
        let supported = self.supported.f()?;
        let entry = self.entry;
        let (x, y, floor) = (self.x, self.y, self.floor);
        Ok(Dict::new()
            .with("entry_world_mm", entry)
            .with("outward_axis_world", (0.0, -1.0, 0.0))
            .with(
                "route_points_world_mm",
                (entry, [x, y, entry[2]], self.tip),
            )
            .with("bend_radius_mm", BEND_RADIUS)
            .with("channel_diameter_mm", CHANNEL_DIAMETER)
            .with("channel_section", "round")
            .with("wall_mm", WALL)
            .with("outlet_leg_mm", 0.0)
            .with("mouth_lead_in_mm", MOUTH)
            .with("cup_mouth_relief_mm", MOUTH)
            .with("supported_roof_allowance_mm", self.supported.clone())
            .with("print_up_world", (0.0, 0.0, 1.0))
            .with("bend_end_world_mm", [x, y, floor])
            .with("outlet_world_mm", [x, y, floor])
            .with("tip_world_mm", self.tip)
            .with("cup_floor_world_z_mm", floor)
            .with("cup_top_world_z_mm", self.cup_top)
            .with("lid_bottom_world_z_mm", self.lid_bottom.clone())
            .with("lid_face_world_z_mm", self.face.clone())
            .with("roof_top_world_z_mm", self.face.clone())
            .with(
                "throat_roof_stock_mm",
                face - (entry[2] + CHANNEL_RADIUS + supported),
            )
            .with(
                "entry_leadin_roof_stock_mm",
                face - (entry[2] + CHANNEL_RADIUS + MOUTH + supported),
            )
            .with("stock_min_world_mm", [x - 16.5, self.front, floor])
            .with(
                "stock_max_world_mm",
                (x + 16.5, y + 15.0, self.face.clone()),
            )
            .val())
    }
}

#[derive(Default)]
pub struct State {
    passage: RefCell<Option<Rc<Passage>>>,
    channel_air: RefCell<Option<Val>>,
    guide_native: RefCell<Option<Val>>,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(_rt: &Runtime) -> Result<Self> {
        Ok(Self::default())
    }
}

fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `passage()`: where the B-fill line enters the cap's front face and turns down to its seat.
pub fn passage(rt: &Runtime) -> Result<Rc<Passage>> {
    let s = state(rt)?;
    if let Some(held) = s.passage.borrow().as_ref() {
        return Ok(held.clone());
    }
    let core = core::state(rt)?;
    let b = &core.base;
    let layout = AboveCore::get(rt)?;
    let pose = layout.cap_lid_pose()?;
    let cup_height = b.foam_cap_height - b.head_pad_height;
    let lid_bottom = pose.k("translation_mm")?.i(2)?;
    let floor = lid_bottom.f()? - cup_height + b.cap_shell_clearance;
    let [fx, fy] = core.reservoir_fill_conduit_xy(-1)?;
    let at = layout.point(&pose, (fx, fy, 0.0))?;
    let (x, y) = (at[0], at[1]);
    let front = layout.point(&pose, (b.outer_shell_x_length / 2.0, 0.0, 0.0))?[1];
    let supported = rt.pya("fits", "supported_surface")?;
    let tangent_z = floor;
    let entry = [x, front, tangent_z + BEND_RADIUS];
    let tip = [x, y, floor - 5.4];
    let face = layout.spec().k("cap_face_z_mm")?;
    let cup_top = lid_bottom.f()? - b.cap_lid_clearance;
    let held = Rc::new(Passage {
        entry,
        x,
        y,
        front,
        floor,
        tip,
        lid_bottom,
        face,
        supported,
        cup_top,
    });
    *s.passage.borrow_mut() = Some(held.clone());
    Ok(held)
}

/// `passage()` as the dict Python reads.
pub fn passage_val(rt: &Runtime) -> Result<Val> {
    passage(rt)?.val()
}

fn workplane_xz(cq: &Cq) -> Result<Val> {
    cq.workplane(args!["XZ"], vec![])
}

/// `_body_section()`: the holder's domed section.
fn body_section(cq: &Cq) -> Result<Val> {
    let outer = CHANNEL_RADIUS + WALL;
    let (lo, hi) = (BEND_RADIUS - outer, BEND_RADIUS + outer);
    let z = CHANNEL_CENTRE + dome_lift();
    workplane_xz(cq)?
        .m("moveTo", args![lo, 0.0])?
        .m("lineTo", args![hi, 0.0])?
        .m("lineTo", args![hi, z])?
        .m("threePointArc", args![(BEND_RADIUS, z + outer), (lo, z)])?
        .m("close", vec![])
}

/// `_channel_section()`: the tube's round section.
fn channel_section(cq: &Cq) -> Result<Val> {
    workplane_xz(cq)?
        .m("moveTo", args![BEND_RADIUS, CHANNEL_CENTRE])?
        .m("circle", args![CHANNEL_RADIUS])
}

/// `_mouth()`: the lead-in cone at either end of the channel.
fn mouth(cq: &Cq) -> Result<Val> {
    let at = |y: f64, radius: f64| -> Result<Val> {
        let plane = cq.plane(kw![
            "origin" => (0.0, y, 0.0),
            "xDir" => (1.0, 0.0, 0.0),
            "normal" => (0.0, -1.0, 0.0)
        ])?;
        cq.workplane(args![plane], vec![])?
            .m("moveTo", args![BEND_RADIUS, CHANNEL_CENTRE])?
            .m("circle", args![radius])?
            .m("wires", vec![])?
            .m("val", vec![])
    };
    cq.ruled_loft(vec![
        at(-0.3, CHANNEL_RADIUS + MOUTH + 0.3)?,
        at(MOUTH + 0.05, CHANNEL_RADIUS - 0.05)?,
    ])
}

/// `holder_sections(inlet_leg, outlet_leg=0.0)`: `(body, channel)` of the bend holder.
pub fn holder_sections(rt: &Runtime, inlet_leg: f64, outlet_leg: f64) -> Result<(Val, Val)> {
    let cq = Cq::new(rt)?;
    let axis = [(0.0, 0.0, 0.0).to_val(), (0.0, 1.0, 0.0).to_val()];
    let half = 0.5f64.sqrt();
    let mirror = cq.vector([half, -half, 0.0])?;
    let origin = cq.m.a("Vector")?.c(vec![])?;
    let revolve = |section: Val| {
        section.m("revolve", vec![Val::Float(90.0), axis[0].clone(), axis[1].clone()])
    };
    let mut body = revolve(body_section(&cq)?)?
        .m("union", args![body_section(&cq)?.m("extrude", args![inlet_leg])?])?;
    let mut channel = revolve(channel_section(&cq)?)?
        .m("union", args![channel_section(&cq)?.m("extrude", args![inlet_leg])?])?;
    if outlet_leg > 0.0 {
        body = body.m(
            "union",
            args![body_section(&cq)?
                .m("extrude", args![outlet_leg])?
                .m("mirror", args![&mirror, &origin])?],
        )?;
        channel = channel.m(
            "union",
            args![channel_section(&cq)?
                .m("extrude", args![outlet_leg])?
                .m("mirror", args![&mirror, &origin])?],
        )?;
    }
    let start = translate(&mouth(&cq)?, [0.0, -inlet_leg, 0.0])?;
    let end = translate(&mouth(&cq)?, [0.0, -outlet_leg, 0.0])?.m("mirror", args![&mirror, &origin])?;
    let body = body.m("val", vec![])?;
    let channel = clean(&channel.m("val", vec![])?.m("fuse", vec![start, end])?)?;
    Ok((body, channel))
}

fn int3(v: [i64; 3]) -> Val {
    (v[0], v[1], v[2]).to_val()
}

/// `channel_air()`: the tube's own clear passage through the cap, roof allowance included.
pub fn channel_air(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    if let Some(held) = s.channel_air.borrow().as_ref() {
        return Ok(held.clone());
    }
    let data = passage(rt)?;
    let [x, y, tangent_z] = data.bend_end();
    let turn_y = y - BEND_RADIUS;
    let (_body, channel) = holder_sections(rt, turn_y - data.entry[1], 0.0)?;
    let channel = channel
        .m("rotate", vec![int3([0, 0, 0]), int3([0, 1, 0]), Val::Float(-90.0)])?
        .m("translate", args![(x + CHANNEL_CENTRE, turn_y, tangent_z)])?;
    let lifted = channel.m("translate", args![(0.0, 0.0, data.supported.clone())])?;
    let air = clean(&channel.m("fuse", vec![lifted])?)?;
    *s.channel_air.borrow_mut() = Some(air.clone());
    Ok(air)
}

/// `guide_native()`: the accepted R14 holder, from its exploration module.
pub fn guide_native(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    if let Some(held) = s.guide_native.borrow().as_ref() {
        return Ok(held.clone());
    }
    let util = rt.py("importlib.util")?;
    let root = ancestor_where(&resolve(&rt.file(NAME)), |p| p.join("future").is_dir())?;
    let spec = util.m(
        "spec_from_file_location",
        args![
            "_b_fill_r14",
            Val::Path(root.join("future/tube-bend-holder-exploration/tube_bend_holder.py"))
        ],
    )?;
    let module = util.m("module_from_spec", args![&spec])?;
    spec.a("loader")?.m("exec_module", args![&module])?;
    let holder = module.m("holder", args![WALL, 0.0])?.m("val", vec![])?;
    *s.guide_native.borrow_mut() = Some(holder.clone());
    Ok(holder)
}

/// `guide_world()`: the holder placed over the bend.
pub fn guide_world(rt: &Runtime) -> Result<Val> {
    let [x, y, z] = passage(rt)?.bend_end();
    guide_native(rt)?
        .m("rotate", vec![int3([0, 0, 0]), int3([0, 1, 0]), Val::Float(-90.0)])?
        .m("translate", args![(x + CHANNEL_CENTRE, y - BEND_RADIUS, z)])
}

/// `features(cup_height)`: what the cap cuts and carries for the B-fill line.
pub fn features(rt: &Runtime, _cup_height: f64) -> Result<Val> {
    Ok(Dict::new()
        .with("cut", channel_air(rt)?)
        .with("channel_air", channel_air(rt)?)
        .with("holder_outer", guide_world(rt)?)
        .val())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    ns.python(rt, "lru_cache", "functools", "lru_cache")?;
    ns.module(rt, "importlib", "importlib")?;
    ns.module(rt, "math", "math")?;
    ns.value("BEND_RADIUS", BEND_RADIUS);
    ns.value("CHANNEL_DIAMETER", CHANNEL_DIAMETER);
    ns.value("WALL", WALL);
    ns.value("MOUTH", MOUTH);
    ns.value("CHANNEL_RADIUS", CHANNEL_RADIUS);
    ns.value("CHANNEL_CENTRE", CHANNEL_CENTRE);
    ns.value("DOME_LIFT", dome_lift());
    ns.func(rt, "passage", |rt, _| passage_val(rt));
    ns.func(rt, "_body_section", |rt, _| body_section(&Cq::new(rt)?));
    ns.func(rt, "_channel_section", |rt, _| channel_section(&Cq::new(rt)?));
    ns.func(rt, "_mouth", |rt, _| mouth(&Cq::new(rt)?));
    ns.func(rt, "holder_sections", |rt, c| {
        let inlet_leg = c.req(0, "inlet_leg")?;
        let outlet_leg = c.opt(1, "outlet_leg", 0.0)?;
        Ok(holder_sections(rt, inlet_leg, outlet_leg)?.to_val())
    });
    ns.func(rt, "channel_air", |rt, _| channel_air(rt));
    ns.func(rt, "guide_native", |rt, _| guide_native(rt));
    ns.func(rt, "guide_world", |rt, _| guide_world(rt));
    ns.func(rt, "features", |rt, c| {
        let cup_height = c.req(0, "cup_height")?;
        features(rt, cup_height)
    });
    Ok(())
}
