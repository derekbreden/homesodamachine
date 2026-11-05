//! `_outer_shell`: the outer rectangular cup, its attachment bosses and their heat-set insert
//! pockets.

use super::cold_core_interface as core;
use super::*;

pub const NAME: &str = "_outer_shell";

pub struct State {
    cq: Val,
    world_workplane: Val,
    xy_plane_z_up: Val,
    fits: Val,
    supported_surface: f64,
    pub attachment_stations: Vec<([f64; 2], String)>,
    pub seam_channel_depth: f64,
    pub seam_channel_width: f64,
    pub outer_shell_wall: f64,
    pub wall_and_floor_thickness: f64,
    pub foam_shell_outer_height: f64,
    pub foam_shell_rim_z: f64,
    pub outer_shell_x_length: f64,
    pub outer_shell_y_length: f64,
    pub attachment_xy_positions: Vec<[f64; 2]>,
    pub screw_boss_size: f64,
    pub screw_guard_diameter: f64,
    pub screw_clearance_radius: f64,
    pub bottom_screw_bore_depth: f64,
    pub top_screw_bore_depth: f64,
    pub corner_round_radius: f64,
    pub insert_pocket_radius: f64,
    pub insert_pocket_depth: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let cq = rt.py("cadquery")?;
        let world_workplane = rt.pya("world_workplane", "WorldWorkplane")?;
        let xy_plane_z_up = rt.pya("world_workplane", "xy_plane_z_up")?;
        let fits = rt.py("fits")?;
        let core = core::state(rt)?;
        let b = &core.base;
        let supported_surface = fits.a("supported_surface")?.f()?;
        Ok(Self {
            cq,
            world_workplane,
            xy_plane_z_up,
            fits,
            supported_surface,
            attachment_stations: b.attachment_stations.clone(),
            seam_channel_depth: b.seam_channel_depth,
            seam_channel_width: b.seam_channel_width,
            outer_shell_wall: b.outer_shell_wall,
            wall_and_floor_thickness: b.wall_and_floor_thickness,
            foam_shell_outer_height: b.foam_shell_outer_height,
            foam_shell_rim_z: b.foam_shell_rim_z,
            outer_shell_x_length: b.outer_shell_x_length,
            outer_shell_y_length: b.outer_shell_y_length,
            attachment_xy_positions: b.attachment_xy_positions.clone(),
            screw_boss_size: b.screw_boss_size,
            screw_guard_diameter: b.screw_guard_diameter,
            screw_clearance_radius: b.screw_clearance_radius,
            bottom_screw_bore_depth: b.bottom_screw_bore_depth,
            top_screw_bore_depth: b.top_screw_bore_depth,
            corner_round_radius: b.corner_round_radius,
            insert_pocket_radius: b.insert_pocket_radius,
            insert_pocket_depth: b.insert_pocket_depth,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

impl State {
    /// `WorldWorkplane(xy_plane_z_up).workplane(offset=z)`.
    fn plan_at(&self, z: Num) -> Result<Val> {
        self.world_workplane
            .c(args![self.xy_plane_z_up])?
            .mk("workplane", vec![], kw!["offset" => z])
    }
    /// Circles of `radius` at every attachment station, extruded `depth` from `z`.
    fn station_circles(&self, z: Num, radius: f64, depth: f64) -> Result<Val> {
        self.plan_at(z)?
            .m("pushPoints", args![self.attachment_xy_positions])?
            .m("circle", args![radius])?
            .m("extrude", args![depth])
    }
}

/// `_rounded_footprint(height)`: the cup's outline with its corners rounded, `height` tall.
pub fn rounded_footprint(rt: &Runtime, height: f64) -> Result<Val> {
    let s = state(rt)?;
    s.plan_at(Num::I(0))?
        .m("rect", args![s.outer_shell_x_length, s.outer_shell_y_length])?
        .m("extrude", args![height])?
        .m("edges", args!["|Z"])?
        .m("fillet", args![s.corner_round_radius])
}

/// `cavity_plan(z0, z1, wall=None)`: the cup's cavity between `z0` and `z1`, inset `wall`.
pub fn cavity_plan(rt: &Runtime, z0: f64, z1: f64, wall: Option<f64>) -> Result<Val> {
    let s = state(rt)?;
    let w = wall.unwrap_or(s.outer_shell_wall);
    s.plan_at(Num::F(z0))?
        .m(
            "rect",
            args![s.outer_shell_x_length - 2.0 * w, s.outer_shell_y_length - 2.0 * w],
        )?
        .m("extrude", args![z1 - z0])?
        .m("edges", args!["|Z"])?
        .m("fillet", args![s.corner_round_radius - w])
}

/// `trim_cup_floor(cup, z0, z1, wall=None)`.
pub fn trim_cup_floor(rt: &Runtime, cup: &Val, z0: f64, z1: f64, wall: Option<f64>) -> Result<Val> {
    cup.m("cut", args![cavity_plan(rt, z0, z1, wall)?])
}

/// `build_attachment_bosses(height, oversize=0.0, diameter=None)`: a boss at every station,
/// webbed out to the wall it stands on, trimmed to the rounded footprint.
pub fn build_attachment_bosses(
    rt: &Runtime,
    height: f64,
    oversize: f64,
    diameter: Option<f64>,
) -> Result<Val> {
    let s = state(rt)?;
    let r = diameter.unwrap_or(s.screw_boss_size) / 2.0 + oversize;
    let corner_x = s.outer_shell_x_length / 2.0;
    let corner_y = s.outer_shell_y_length / 2.0;
    let mut bosses = s.station_circles(Num::I(0), r, height)?;
    for ([cx, cy], wall) in &s.attachment_stations {
        let (cx, cy) = (*cx, *cy);
        let mut boss_webs = Val::None;
        if wall == "corner" || wall == "y" {
            let y_sign = if cy > 0.0 { 1.0 } else { -1.0 };
            boss_webs = core::make_box(rt, &[cx - r, cx + r], &[cy, y_sign * corner_y], &[0.0, height])?;
        }
        if wall == "corner" || wall == "x" {
            let x_sign = if cx > 0.0 { 1.0 } else { -1.0 };
            let web = core::make_box(rt, &[cx, x_sign * corner_x], &[cy - r, cy + r], &[0.0, height])?;
            boss_webs = if matches!(boss_webs, Val::None) {
                web
            } else {
                boss_webs.m("union", args![web])?
            };
        }
        bosses = bosses.m("union", args![boss_webs])?;
    }
    bosses.m("intersect", args![rounded_footprint(rt, height)?.m("unwrap", vec![])?])
}

/// `fold_seam_channel(shell)`: the fore seam's folded land and the channel through it.
pub fn fold_seam_channel(rt: &Runtime, shell: &Val) -> Result<Val> {
    let s = state(rt)?;
    let face_y = s.outer_shell_y_length / 2.0;
    let floor_y = face_y - s.seam_channel_depth;
    let half = s.seam_channel_width / 2.0;
    let h = s.foam_shell_rim_z;
    let wall = s.outer_shell_wall;
    let fold = core::make_box(rt, &[-half - wall, half + wall], &[floor_y - wall, floor_y], &[0.0, h])?;
    let channel = core::make_box(rt, &[-half, half], &[floor_y, face_y + 1.0], &[-1.0, h + 1.0])?;
    shell.m("union", args![fold])?.m("cut", args![channel])
}

/// `build_outer_shell()`.
pub fn build_outer_shell(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let h = s.foam_shell_rim_z;
    let footprint = rounded_footprint(rt, h)?;
    let shell = footprint.m("cut", args![cavity_plan(rt, s.wall_and_floor_thickness, h, None)?])?;
    let hosts = build_attachment_bosses(rt, h, 0.0, Some(s.screw_guard_diameter))?;
    fold_seam_channel(rt, &shell.m("union", args![hosts])?)?.m("unwrap", vec![])
}

/// `cut_insert_pockets(foam_shell)`: heat-set insert pockets, screw tails and their tapers at
/// every station, from below and above.
pub fn cut_insert_pockets(rt: &Runtime, foam_shell: &Val) -> Result<Val> {
    let s = state(rt)?;
    let cq = super::cad::Cq::new(rt)?;
    let insert_pockets_at = |z_floor: Num, depth: f64| {
        s.station_circles(z_floor, s.insert_pocket_radius, depth)
    };
    let bottom_pockets = insert_pockets_at(Num::I(0), s.insert_pocket_depth + s.supported_surface)?
        .m("unwrap", vec![])?;
    let top_pockets = insert_pockets_at(
        Num::F(s.foam_shell_rim_z - s.insert_pocket_depth),
        s.insert_pocket_depth,
    )?
    .m("unwrap", vec![])?;
    let tails = |z0: f64, depth: f64| {
        s.station_circles(Num::F(z0), s.screw_clearance_radius, depth)?
            .m("unwrap", vec![])
    };
    let taper = |z0: f64, lower_radius: f64, upper_radius: f64| -> Result<Val> {
        let height = 2.0 * (lower_radius - upper_radius);
        let mut cones = vec![];
        for [x, y] in &s.attachment_xy_positions {
            cones.push(cq.solid(
                "makeCone",
                args![lower_radius, upper_radius, height, cq.vector([*x, *y, z0])?],
            )?);
        }
        cq.class("Compound", "makeCompound", vec![Val::list(cones)], vec![])
    };
    let pilot_end = s.insert_pocket_depth + s.supported_surface;
    let tail_end = s.bottom_screw_bore_depth + s.supported_surface;
    let shell = foam_shell
        .m("cut", args![bottom_pockets])?
        .m("cut", args![top_pockets])?;
    let shell = shell.m("cut", args![tails(0.0, tail_end)?])?;
    let shell = shell.m(
        "cut",
        args![taper(pilot_end, s.insert_pocket_radius, s.screw_clearance_radius)?],
    )?;
    let shell = shell.m("cut", args![taper(tail_end, s.screw_clearance_radius, 0.0)?])?;
    shell.m(
        "cut",
        args![tails(s.foam_shell_rim_z - s.top_screw_bore_depth, s.top_screw_bore_depth)?],
    )
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("cq", s.cq.clone());
    ns.value("WorldWorkplane", s.world_workplane.clone());
    ns.value("xy_plane_z_up", s.xy_plane_z_up.clone());
    ns.value("fits", s.fits.clone());
    ns.value("attachment_stations", tuple(&s.attachment_stations));
    ns.value("seam_channel_depth", s.seam_channel_depth);
    ns.value("seam_channel_width", s.seam_channel_width);
    ns.value("outer_shell_wall", s.outer_shell_wall);
    ns.value("wall_and_floor_thickness", s.wall_and_floor_thickness);
    ns.value("foam_shell_outer_height", s.foam_shell_outer_height);
    ns.value("foam_shell_rim_z", s.foam_shell_rim_z);
    ns.value("outer_shell_x_length", s.outer_shell_x_length);
    ns.value("outer_shell_y_length", s.outer_shell_y_length);
    ns.value("attachment_xy_positions", s.attachment_xy_positions.clone());
    ns.value("screw_boss_size", s.screw_boss_size);
    ns.value("screw_guard_diameter", s.screw_guard_diameter);
    ns.value("screw_clearance_radius", s.screw_clearance_radius);
    ns.value("bottom_screw_bore_depth", s.bottom_screw_bore_depth);
    ns.value("top_screw_bore_depth", s.top_screw_bore_depth);
    ns.value("corner_round_radius", s.corner_round_radius);
    ns.value("insert_pocket_radius", s.insert_pocket_radius);
    ns.value("insert_pocket_depth", s.insert_pocket_depth);
    ns.func(rt, "make_box", |rt, c| {
        let x: Vec<f64> = c.req(0, "x_range")?;
        let y: Vec<f64> = c.req(1, "y_range")?;
        let z: Vec<f64> = c.req(2, "z_range")?;
        core::make_box(rt, &x, &y, &z)
    });
    ns.func(rt, "_rounded_footprint", |rt, c| {
        rounded_footprint(rt, c.req(0, "height")?)
    });
    ns.func(rt, "cavity_plan", |rt, c| {
        let (z0, z1) = (c.req(0, "z0")?, c.req(1, "z1")?);
        cavity_plan(rt, z0, z1, c.opt(2, "wall", None)?)
    });
    ns.func(rt, "trim_cup_floor", |rt, c| {
        let cup = c.req::<Val>(0, "cup")?;
        let (z0, z1) = (c.req(1, "z0")?, c.req(2, "z1")?);
        trim_cup_floor(rt, &cup, z0, z1, c.opt(3, "wall", None)?)
    });
    ns.func(rt, "build_attachment_bosses", |rt, c| {
        let height = c.req(0, "height")?;
        let oversize = c.opt(1, "oversize", 0.0)?;
        build_attachment_bosses(rt, height, oversize, c.opt(2, "diameter", None)?)
    });
    ns.func(rt, "fold_seam_channel", |rt, c| {
        fold_seam_channel(rt, &c.req::<Val>(0, "shell")?)
    });
    ns.func(rt, "build_outer_shell", |rt, _| build_outer_shell(rt));
    ns.func(rt, "cut_insert_pockets", |rt, c| {
        cut_insert_pockets(rt, &c.req::<Val>(0, "foam_shell")?)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
