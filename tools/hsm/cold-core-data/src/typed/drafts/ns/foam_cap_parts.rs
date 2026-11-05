//! `_foam_cap`: the cold core's uniform equipment lid and its open-topped bottom closure, and
//! the stack heights (lid, top cup, floor, cap face) the core's other parts place by.

use super::above_core_mounts as mounts;
use super::cad::Cq;
use super::cold_core_interface as core;
use super::internal_routes as routes;
use super::reservoir_b_fill;
use super::*;

pub const NAME: &str = "_foam_cap";

/// The names `from _cold_core_interface import ...` binds, in the statement's order.
const INTERFACE_NAMES: &[&str] = &[
    "wall_and_floor_thickness",
    "wall_thickness",
    "outer_shell_wall",
    "outer_shell_x_length",
    "outer_shell_y_length",
    "corner_round_radius",
    "screw_boss_size",
    "cap_conduits",
    "cap_conduit_floor_xy",
    "cap_passive_guides",
    "cap_cable_guides",
    "cap_conduit_bore_radius",
    "cap_conduit_bore_radii",
    "cap_conduit_boss_radius",
    "cap_conduit_links",
    "cap_conduit_link_width",
    "cap_conduit_entry_relief_radius",
    "foam_cap_height",
    "foam_shell_outer_height",
    "foam_cap_lid_pour_radius",
    "foam_cap_lid_vent_radius",
    "foam_cap_lid_pour_xy",
    "foam_cap_lid_vent_xy",
    "attachment_xy_positions",
    "attachment_stations",
    "lid_attachment_stations",
    "lid_attachment_xy_positions",
    "cap_shell_clearance",
    "cap_lid_clearance",
    "screw_clearance_radius",
    "head_cbore_radius",
    "head_cbore_depth",
    "head_pad_height",
    "head_pad_slip",
    "foam_cap_lid_height",
    "bottom_cap_height",
    "bottom_pour_positions",
    "bottom_pour_radius",
];

pub struct State {
    cq: Val,
    world_workplane: Val,
    xy_plane_z_up: Val,
    fits: Val,
    supported_surface: f64,
    build_attachment_bosses: Val,
    trim_cup_floor: Val,
    pub lid_total_height: f64,
    pub lid_cut_through_depth: f64,
    pub head_pad_growth: f64,
    pub top_cap_height: f64,
    pub stack_floor_z: f64,
    pub cap_face_z: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let cq = rt.py("cadquery")?;
        let world_workplane = rt.pya("world_workplane", "WorldWorkplane")?;
        let xy_plane_z_up = rt.pya("world_workplane", "xy_plane_z_up")?;
        let fits = rt.py("fits")?;
        let core = core::state(rt)?;
        let outer_shell = rt.import_module("_outer_shell")?; // via namespace: _outer_shell
        let build_attachment_bosses = outer_shell.a("build_attachment_bosses")?; // via namespace: _outer_shell
        let trim_cup_floor = outer_shell.a("trim_cup_floor")?; // via namespace: _outer_shell
        mounts::state(rt)?;
        let b = &core.base;
        let lid_total_height = b.foam_cap_lid_height;
        let lid_cut_through_depth = lid_total_height + b.wall_and_floor_thickness;
        let head_pad_growth = pmax(
            0.0,
            b.head_cbore_radius + b.wall_thickness - b.screw_boss_size / 2.0,
        );
        let top_cap_height = b.foam_cap_height - b.head_pad_height;
        let stack_floor_z = -(b.foam_cap_height + b.wall_and_floor_thickness);
        let cap_face_z = b.foam_shell_outer_height + top_cap_height + lid_total_height;
        let supported_surface = fits.a("supported_surface")?.f()?;
        Ok(Self {
            cq,
            world_workplane,
            xy_plane_z_up,
            fits,
            supported_surface,
            build_attachment_bosses,
            trim_cup_floor,
            lid_total_height,
            lid_cut_through_depth,
            head_pad_growth,
            top_cap_height,
            stack_floor_z,
            cap_face_z,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `WorldWorkplane(xy_plane_z_up)`.
fn plane(s: &State) -> Result<Val> {
    s.world_workplane.c(args![s.xy_plane_z_up])
}

/// `attachment_clearances_extrude(height, top=False)`: the screw clearance bores.
pub fn attachment_clearances_extrude(rt: &Runtime, height: f64, top: bool) -> Result<Val> {
    let s = state(rt)?;
    let core = core::state(rt)?;
    let b = &core.base;
    let points = if top {
        &b.lid_attachment_xy_positions
    } else {
        &b.attachment_xy_positions
    };
    plane(&s)?
        .mk("workplane", vec![], kw!["offset" => 0i64])?
        .m("pushPoints", args![points])?
        .m("circle", args![b.screw_clearance_radius])?
        .m("extrude", args![height])
}

/// `build_conduit_bores(height, radius=cap_conduit_bore_radius, overshoot=0.0, frame='cup')`.
pub fn build_conduit_bores(
    rt: &Runtime,
    height: f64,
    radius: f64,
    overshoot: f64,
    frame: &str,
) -> Result<Val> {
    let s = state(rt)?;
    let core = core::state(rt)?;
    let b = &core.base;
    let cq = Cq::new(rt)?;
    let guides: Vec<&str> = core
        .cap_passive_guides
        .iter()
        .chain(&core.cap_cable_guides)
        .map(String::as_str)
        .collect();
    let ordinary: Vec<[f64; 2]> = core
        .cap_conduits
        .iter()
        .filter(|(name, _)| {
            !["reservoir-b-fill", "water-in", "carb-water-out"].contains(name)
                && !(frame == "lid" && core.cap_conduit_bore_radii.get(name).is_some())
                && (frame == "lid" || !guides.contains(name))
        })
        .map(|(_, xy)| *xy)
        .collect();
    let mut bores = plane(&s)?
        .mk("workplane", vec![], kw!["offset" => -overshoot])?
        .m("pushPoints", args![ordinary])?
        .m("circle", args![radius])?
        .m("extrude", args![height + overshoot])?;
    if frame == "lid" {
        for (name, bore_radius) in core.cap_conduit_bore_radii.iter() {
            let bore = plane(&s)?
                .mk("workplane", vec![], kw!["offset" => -overshoot])?
                .m("pushPoints", args![vec![core.cap_conduit(name)?]])?
                .m("circle", args![*bore_radius])?
                .m("extrude", args![height + overshoot])?;
            bores = bores.m("union", args![bore])?;
        }
    }
    let band = cq.make_box(
        [
            b.outer_shell_x_length + 40.0,
            b.outer_shell_y_length + 40.0,
            height + overshoot + 1.0,
        ],
        [
            -b.outer_shell_x_length / 2.0 - 20.0,
            -b.outer_shell_y_length / 2.0 - 20.0,
            -overshoot,
        ],
    )?;
    if frame == "cup" {
        let r = routes::state(rt)?;
        for name in &core.cap_passive_guides {
            let passage = routes::build_route(rt, r.routes.at(name)?, r.route_bend_radius, radius)?;
            let passage = passage
                .m("rotate", args![[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], 180.0])?
                .m("translate", args![[0.0, 0.0, -b.foam_shell_outer_height]])?;
            bores = bores.m("union", args![passage.m("intersect", args![band])?])?;
        }
        for name in &core.cap_cable_guides {
            let (points, bend) = mounts::cable_guide_points(rt, name)?;
            let passage = routes::build_route(rt, &points, bend, radius)?;
            let passage = mounts::world_shape_in_cap(rt, &passage)?
                .m("translate", args![[0.0, 0.0, s.top_cap_height]])?;
            bores = bores.m("union", args![passage.m("intersect", args![band])?])?;
        }
    }
    for features in [mounts::water_in_features, mounts::soda_out_features] {
        let mut air = mounts::world_shape_in_cap(rt, &features(rt)?.k("cut")?)?;
        if frame == "cup" {
            air = air.m("translate", args![[0.0, 0.0, s.top_cap_height]])?;
        }
        bores = bores.m("union", args![air.m("intersect", args![band])?])?;
    }
    let mut fitting_air = reservoir_b_fill::channel_air(rt)?;
    fitting_air = mounts::world_shape_in_cap(rt, &fitting_air)?;
    if frame == "cup" {
        fitting_air = fitting_air.m("translate", args![[0.0, 0.0, s.top_cap_height]])?;
    }
    bores.m("union", args![fitting_air.m("intersect", args![band])?])
}

/// `build_conduit_entry_reliefs(z_inner)`: the lofted cone at each ordinary bore's entry, or
/// `None` when no conduit takes one.
pub fn build_conduit_entry_reliefs(rt: &Runtime, z_inner: f64) -> Result<Option<Val>> {
    let s = state(rt)?;
    let core = core::state(rt)?;
    let b = &core.base;
    let mut cones: Option<Val> = None;
    for (name, centre) in core.cap_conduits.iter() {
        if ["reservoir-b-fill", "water-in", "sensor-cable"].contains(&name)
            || core.cap_conduit_bore_radii.get(name).is_some()
        {
            continue;
        }
        let cone = plane(&s)?
            .mk("workplane", vec![], kw!["offset" => z_inner])?
            .m("moveTo", args![*centre])?
            .m("circle", args![core.cap_conduit_bore_radius])?
            .mk("workplane", vec![], kw!["offset" => b.wall_and_floor_thickness])?
            .m("moveTo", args![*centre])?
            .m("circle", args![core.cap_conduit_entry_relief_radius])?
            .mk("loft", vec![], kw!["ruled" => true])?;
        cones = Some(match cones {
            None => cone,
            Some(cones) => cones.m("union", args![cone])?,
        });
    }
    Ok(cones)
}

/// `head_access_pockets(z0, depth, top=False)`: the counterbores and the slots that open each
/// one to the wall it sits against.
pub fn head_access_pockets(rt: &Runtime, z0: f64, depth: f64, top: bool) -> Result<Val> {
    let s = state(rt)?;
    let core = core::state(rt)?;
    let b = &core.base;
    let stations = if top {
        &b.lid_attachment_stations
    } else {
        &b.attachment_stations
    };
    let points: Vec<[f64; 2]> = stations.iter().map(|(xy, _)| *xy).collect();
    let mut pockets = plane(&s)?
        .mk("workplane", vec![], kw!["offset" => z0])?
        .m("pushPoints", args![points])?
        .m("circle", args![b.head_cbore_radius])?
        .m("extrude", args![depth])?;
    let r = b.head_cbore_radius;
    let sign = |v: f64| if v > 0.0 { 1.0 } else { -1.0 };
    for ([x, y], wall) in stations {
        let (x, y) = (*x, *y);
        let slot = if wall == "corner" {
            let ox = x - sign(x) * (b.outer_shell_x_length / 2.0 - b.corner_round_radius);
            let oy = y - sign(y) * (b.outer_shell_y_length / 2.0 - b.corner_round_radius);
            let angle = degrees(oy.atan2(ox)) - 90.0;
            s.cq.m("Workplane", args!["XY"])?
                .mk(
                    "box",
                    args![2.0 * r, 2.0 * b.corner_round_radius + 2.0, depth],
                    kw!["centered" => (true, false, false)],
                )?
                .m("rotate", args![(0i64, 0i64, 0i64), (0i64, 0i64, 1i64), angle])?
                .m("translate", args![[x, y, z0]])?
        } else if wall == "x" {
            let end = sign(x) * (b.outer_shell_x_length / 2.0 + 1.0);
            s.cq.m("Workplane", args!["XY"])?
                .mk(
                    "box",
                    args![(end - x).abs(), 2.0 * r, depth],
                    kw!["centered" => (true, true, false)],
                )?
                .m("translate", args![[(x + end) / 2.0, y, z0]])?
        } else {
            let end = sign(y) * (b.outer_shell_y_length / 2.0 + 1.0);
            s.cq.m("Workplane", args!["XY"])?
                .mk(
                    "box",
                    args![2.0 * r, (end - y).abs(), depth],
                    kw!["centered" => (true, true, false)],
                )?
                .m("translate", args![[x, (y + end) / 2.0, z0]])?
        };
        pockets = pockets.m("union", args![slot])?;
    }
    Ok(pockets)
}

/// `build_foam_cap_lid()`: the uniform equipment lid.
pub fn build_foam_cap_lid(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let core = core::state(rt)?;
    let b = &core.base;
    let cq = Cq::new(rt)?;
    let mut lid = plane(&s)?
        .m("rect", args![b.outer_shell_x_length, b.outer_shell_y_length])?
        .m("extrude", args![s.lid_total_height])?
        .m("edges", args!["|Z"])?
        .m("fillet", args![b.corner_round_radius])?;
    lid = lid.m(
        "cut",
        args![head_access_pockets(
            rt,
            s.lid_total_height - b.head_cbore_depth,
            b.head_cbore_depth,
            true
        )?],
    )?;
    lid = lid.m(
        "cut",
        args![attachment_clearances_extrude(rt, s.lid_cut_through_depth, true)?],
    )?;
    lid = lid.m(
        "cut",
        args![build_conduit_bores(
            rt,
            s.lid_cut_through_depth,
            core.cap_conduit_bore_radius,
            0.0,
            "lid"
        )?],
    )?;
    lid = lid
        .m(
            "cut",
            args![build_conduit_entry_reliefs(
                rt,
                s.lid_total_height - b.wall_and_floor_thickness
            )?],
        )?
        .m("unwrap", vec![])?;
    for features in [mounts::water_in_features, mounts::soda_out_features] {
        let features = features(rt)?;
        lid = lid.m(
            "union",
            args![mounts::world_shape_in_cap(rt, &features.k("lid_add")?)?],
        )?;
        lid = lid.m(
            "cut",
            args![mounts::world_shape_in_cap(rt, &features.k("cut")?)?],
        )?;
    }
    let guide = mounts::world_shape_in_cap(rt, &reservoir_b_fill::guide_world(rt)?)?;
    let bounds = guide.m("BoundingBox", vec![])?;
    let window = cq.make_box(
        [
            bounds.a("xlen")?.f()? + 0.3,
            bounds.a("ylen")?.f()? + 0.3,
            s.lid_total_height + 0.2,
        ],
        [
            bounds.a("xmin")?.f()? - 0.15,
            bounds.a("ymin")?.f()? - 0.15,
            -0.1,
        ],
    )?;
    lid.m("cut", args![window])
}

/// `build_bottom_cap()`: the open-topped bottom closure.
pub fn build_bottom_cap(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let core = core::state(rt)?;
    let b = &core.base;
    let cq = Cq::new(rt)?;
    let height = b.bottom_cap_height;
    let mut cap = plane(&s)?
        .m("rect", args![b.outer_shell_x_length, b.outer_shell_y_length])?
        .m("extrude", args![height])?
        .m("edges", args!["|Z"])?
        .m("fillet", args![b.corner_round_radius])?
        .m("faces", args![">Z"])?
        .m("shell", args![-b.outer_shell_wall])?;
    cap = s
        .trim_cup_floor
        .c(args![cap, b.wall_and_floor_thickness, b.outer_shell_wall])?; // via namespace: _outer_shell
    cap = cap.m("union", args![s.build_attachment_bosses.c(args![height])?])?; // via namespace: _outer_shell
    let oversized = s.build_attachment_bosses.ck(
        args![s.lid_total_height],
        kw!["oversize" => s.head_pad_growth],
    )?; // via namespace: _outer_shell
    cap = cap.m("union", args![oversized])?;
    cap = cap.m(
        "cut",
        args![head_access_pockets(
            rt,
            0.0,
            b.head_cbore_depth + s.supported_surface,
            false
        )?],
    )?;
    cap = cap.m(
        "cut",
        args![attachment_clearances_extrude(rt, height + 0.1, false)?],
    )?;
    let mut holes: Vec<([f64; 2], f64)> = b
        .bottom_pour_positions
        .iter()
        .map(|xy| (*xy, b.bottom_pour_radius))
        .collect();
    holes.extend(
        core.foam_cap_lid_vent_xy(false)
            .iter()
            .map(|xy| (*xy, b.foam_cap_lid_vent_radius)),
    );
    for (xy, radius) in holes {
        cap = cap.m(
            "cut",
            args![cq.cylinder_z(radius, height + 0.2, [xy[0], xy[1], -0.1])?],
        )?;
    }
    cap.m("clean", vec![])?.m("unwrap", vec![])
}

/// `import_cap_part(path)`: a cap part's solid from its STEP, or rebuilt when the STEP holds
/// meshcad's tessellation.
pub fn import_cap_part(rt: &Runtime, path: &Val) -> Result<Val> {
    let s = state(rt)?;
    let import_step = rt.pya("_cadq_export", "import_step")?;
    let path = PathBuf::from(path.str()?);
    let getattr = hsm_documents::interop::builtin("getattr").context("getattr")?;
    if !getattr.c(args![s.cq, "MESH", false])?.truthy()? {
        let context = rt
            .pya("builtins", "open")?
            .c(args![Val::Path(path.clone()), "rb"])?;
        let stream = context.m("__enter__", vec![])?;
        let read = (|| -> Result<bool> {
            let head = stream.m("read", args![200i64])?;
            hsm_documents::interop::compare(
                "in",
                Val::Bytes(b"meshcad tessellated".to_vec()),
                head,
            )?
            .truthy()
        })();
        context.m("__exit__", vec![Val::None, Val::None, Val::None])?;
        if read? {
            let stem = path
                .file_stem()
                .map(|v| v.to_string_lossy().to_string())
                .unwrap_or_default();
            if stem == "foam-cap-bottom" {
                return build_bottom_cap(rt)?.m("val", vec![]);
            }
            if stem == "foam-cap-lid-top" {
                rt.py("importlib.util")?;
                let importlib = rt.py("importlib")?;
                let source = rt
                    .file(NAME)
                    .parent()
                    .context("module directory")?
                    .join("foam-cap")
                    .join("foam_cap.py");
                let util = importlib.a("util")?;
                let spec = util.m(
                    "spec_from_file_location",
                    args!["_native_foam_cap", Val::Path(source)],
                )?;
                let module = util.m("module_from_spec", args![spec])?;
                spec.a("loader")?.m("exec_module", args![module])?;
                return module.m("build_top_lid", vec![])?.m("val", vec![]);
            }
            if stem == "reservoir-b-fill-guide" {
                return reservoir_b_fill::guide_native(rt);
            }
            if stem == "pump-snap-cap" {
                return mounts::pump_snap_printable(rt, 0);
            }
        }
    }
    import_step.c(args![ps(&path)])?.m("val", vec![])
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "math", "math")?;
    ns.value("cq", s.cq.clone());
    ns.value("WorldWorkplane", s.world_workplane.clone());
    ns.value("xy_plane_z_up", s.xy_plane_z_up.clone());
    ns.value("fits", s.fits.clone());
    let interface = rt.import_module(core::NAME)?;
    for name in INTERFACE_NAMES {
        ns.value(name, interface.a(name)?);
    }
    ns.value("build_attachment_bosses", s.build_attachment_bosses.clone());
    ns.value("trim_cup_floor", s.trim_cup_floor.clone());
    ns.module(rt, "_above_mounts", mounts::NAME)?;
    ns.value("lid_total_height", s.lid_total_height);
    ns.value("lid_cut_through_depth", s.lid_cut_through_depth);
    ns.value("head_pad_growth", s.head_pad_growth);
    ns.value("top_cap_height", s.top_cap_height);
    ns.value("stack_floor_z", s.stack_floor_z);
    ns.value("cap_face_z", s.cap_face_z);
    ns.func(rt, "attachment_clearances_extrude", |rt, c| {
        let height = c.req(0, "height")?;
        let top = c.opt(1, "top", false)?;
        attachment_clearances_extrude(rt, height, top)
    });
    ns.func(rt, "build_conduit_bores", |rt, c| {
        let core = core::state(rt)?;
        let height = c.req(0, "height")?;
        let radius = c.opt(1, "radius", core.cap_conduit_bore_radius)?;
        let overshoot = c.opt(2, "overshoot", 0.0)?;
        let frame = c.opt(3, "frame", "cup".to_string())?;
        build_conduit_bores(rt, height, radius, overshoot, &frame)
    });
    ns.func(rt, "build_conduit_entry_reliefs", |rt, c| {
        let z_inner = c.req(0, "z_inner")?;
        Ok(build_conduit_entry_reliefs(rt, z_inner)?.unwrap_or(Val::None))
    });
    ns.func(rt, "head_access_pockets", |rt, c| {
        let z0 = c.req(0, "z0")?;
        let depth = c.req(1, "depth")?;
        let top = c.opt(2, "top", false)?;
        head_access_pockets(rt, z0, depth, top)
    });
    ns.func(rt, "build_foam_cap_lid", |rt, _| build_foam_cap_lid(rt));
    ns.func(rt, "build_bottom_cap", |rt, _| build_bottom_cap(rt));
    ns.func(rt, "import_cap_part", |rt, c| {
        import_cap_part(rt, &c.req::<Val>(0, "path")?)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
