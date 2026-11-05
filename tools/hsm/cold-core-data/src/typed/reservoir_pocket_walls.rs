//! `_reservoir_pocket_walls`: the two reservoir pockets, one on each ±X side, as four-walled
//! enclosures whose centerward wall is curved to clear the carbonator and coil envelope.

use super::cold_core_interface as core;
use super::*;

pub const NAME: &str = "_reservoir_pocket_walls";

pub const POCKET_CENTERWARD_ARC_TRANSITION_Y: f64 = 60.0;
pub const TRANSITION_CENTER_X: f64 = 56.655020677894306;

pub struct State {
    cq: Val,
    world_workplane: Val,
    world_profile: Val,
    xy_plane_z_up: Val,
    pub wall_thickness: f64,
    pub pocket_centerward_arc_outer_radius: f64,
    pub foam_shell_outer_height: f64,
    pub bag_pocket_corner_inner_radius: f64,
    pub bag_pocket_y_inner_max: f64,
    pub bag_pocket_far_inner_x: f64,
    pub w: f64,
    pub arc_cavity_r: f64,
    pub arc_outer_r: f64,
    pub y_inner: f64,
    pub middle_outer_x: f64,
    pub middle_cavity_x: f64,
    pub chord_half_y: f64,
    pub transition_center_y: f64,
    pub transition_cavity_r: f64,
    pub transition_outer_r: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let cq = rt.py("cadquery")?;
        let world_workplane = rt.pya("world_workplane", "WorldWorkplane")?;
        let world_profile = rt.pya("world_workplane", "WorldProfile")?;
        let xy_plane_z_up = rt.pya("world_workplane", "xy_plane_z_up")?;
        let core = core::state(rt)?;
        let b = &core.base;
        let w = b.wall_thickness;
        let arc_cavity_r = b.pocket_centerward_arc_outer_radius;
        let arc_outer_r = arc_cavity_r - w;
        let y_inner = b.bag_pocket_y_inner_max;
        let arc_y = POCKET_CENTERWARD_ARC_TRANSITION_Y;
        let middle_outer_x = (arc_outer_r.powf(2.0) - arc_y.powf(2.0)).sqrt();
        let middle_cavity_x = (arc_cavity_r.powf(2.0) - arc_y.powf(2.0)).sqrt();
        let chord_half_y = (y_inner - arc_y) / 2.0;
        let transition_center_y = (y_inner + arc_y) / 2.0;
        let transition_cavity_r =
            ((TRANSITION_CENTER_X - middle_cavity_x).powf(2.0) + chord_half_y.powf(2.0)).sqrt();
        let transition_outer_r = transition_cavity_r + w;
        Ok(Self {
            cq,
            world_workplane,
            world_profile,
            xy_plane_z_up,
            wall_thickness: b.wall_thickness,
            pocket_centerward_arc_outer_radius: b.pocket_centerward_arc_outer_radius,
            foam_shell_outer_height: b.foam_shell_outer_height,
            bag_pocket_corner_inner_radius: b.bag_pocket_corner_inner_radius,
            bag_pocket_y_inner_max: b.bag_pocket_y_inner_max,
            bag_pocket_far_inner_x: b.bag_pocket_far_inner_x,
            w,
            arc_cavity_r,
            arc_outer_r,
            y_inner,
            middle_outer_x,
            middle_cavity_x,
            chord_half_y,
            transition_center_y,
            transition_cavity_r,
            transition_outer_r,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `build_plus_x_cavity(height=None)`: the +X pocket's cavity, as a wrapped workplane.
pub fn build_plus_x_cavity(rt: &Runtime, height: Option<f64>) -> Result<Val> {
    let s = state(rt)?;
    plus_x_cavity(rt, Val::Float(height.unwrap_or(s.foam_shell_outer_height)))
}

/// The cavity extruded `height` as the caller states it.
fn plus_x_cavity(rt: &Runtime, height: Val) -> Result<Val> {
    let s = state(rt)?;
    let far_x_inner = s.bag_pocket_far_inner_x;
    let corner_inner_r = s.bag_pocket_corner_inner_radius;
    let arc_y = POCKET_CENTERWARD_ARC_TRANSITION_Y;
    let (y_inner, middle_cavity_x) = (s.y_inner, s.middle_cavity_x);
    let transition_apex =
        |y_sign: i64| (TRANSITION_CENTER_X - s.transition_cavity_r, y_sign as f64 * s.transition_center_y);
    let cavity_profile = s
        .world_profile
        .c(vec![])?
        .m("moveTo", args![(middle_cavity_x, y_inner)])?
        .m("lineTo", args![(far_x_inner - corner_inner_r, y_inner)])?
        .m("radiusArc", args![(far_x_inner, y_inner - corner_inner_r), corner_inner_r])?
        .m("lineTo", args![(far_x_inner, -(y_inner - corner_inner_r))])?
        .m("radiusArc", args![(far_x_inner - corner_inner_r, -y_inner), corner_inner_r])?
        .m("lineTo", args![(middle_cavity_x, -y_inner)])?
        .m("threePointArc", args![transition_apex(-1), (middle_cavity_x, -arc_y)])?
        .m("threePointArc", args![(s.arc_cavity_r, 0i64), (middle_cavity_x, arc_y)])?
        .m("threePointArc", args![transition_apex(1), (middle_cavity_x, y_inner)])?;
    s.world_workplane
        .c(args![s.xy_plane_z_up])?
        .mk("workplane", vec![], kw!["offset" => 0i64])?
        .m("profile", args![cavity_profile])?
        .m("wire", vec![])?
        .m("extrude", args![height])
}

/// `build_reservoir_pocket_walls()`: both pockets' walls, the −X one mirrored from the +X.
pub fn build_reservoir_pocket_walls(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let height = s.foam_shell_outer_height;
    let cavity = build_plus_x_cavity(rt, Some(height))?.m("unwrap", vec![])?;
    let wire = cavity
        .m("faces", args!["<Z"])?
        .m("wires", vec![])?
        .m("val", vec![])?;
    let outer_wire = wire.mk("offset2D", args![s.w], kw!["kind" => "arc"])?.i(0)?;
    let outer = s
        .cq
        .a("Workplane")?
        .c(args!["XY"])?
        .m("add", args![outer_wire])?
        .m("toPending", vec![])?
        .m("extrude", args![height])?;
    let plus_x_pocket = outer.m("cut", args![cavity])?;
    plus_x_pocket.m("union", args![plus_x_pocket.m("mirror", args!["YZ"])?])
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "math", "math")?;
    ns.value("cq", s.cq.clone());
    ns.value("WorldWorkplane", s.world_workplane.clone());
    ns.value("WorldProfile", s.world_profile.clone());
    ns.value("xy_plane_z_up", s.xy_plane_z_up.clone());
    ns.value("wall_thickness", s.wall_thickness);
    ns.value("pocket_centerward_arc_outer_radius", s.pocket_centerward_arc_outer_radius);
    ns.value("foam_shell_outer_height", s.foam_shell_outer_height);
    ns.value("bag_pocket_corner_inner_radius", s.bag_pocket_corner_inner_radius);
    ns.value("bag_pocket_y_inner_max", s.bag_pocket_y_inner_max);
    ns.value("bag_pocket_far_inner_x", s.bag_pocket_far_inner_x);
    ns.value("w", s.w);
    ns.value("pocket_centerward_arc_transition_y", POCKET_CENTERWARD_ARC_TRANSITION_Y);
    ns.value("arc_cavity_r", s.arc_cavity_r);
    ns.value("arc_outer_r", s.arc_outer_r);
    ns.value("y_inner", s.y_inner);
    ns.value("middle_outer_x", s.middle_outer_x);
    ns.value("middle_cavity_x", s.middle_cavity_x);
    ns.value("_chord_half_y", s.chord_half_y);
    ns.value("transition_center_x", TRANSITION_CENTER_X);
    ns.value("transition_center_y", s.transition_center_y);
    ns.value("transition_cavity_r", s.transition_cavity_r);
    ns.value("transition_outer_r", s.transition_outer_r);
    ns.func(rt, "build_plus_x_cavity", |rt, c| {
        match c.opt::<Val>(0, "height", Val::None)? {
            Val::None => build_plus_x_cavity(rt, None),
            height => plus_x_cavity(rt, height),
        }
    });
    ns.func(rt, "build_reservoir_pocket_walls", |rt, _| {
        build_reservoir_pocket_walls(rt)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
