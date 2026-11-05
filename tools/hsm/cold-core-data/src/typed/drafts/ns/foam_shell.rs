//! `foam_shell`: the PET-GF enclosure around the cold core's carbonator, evaporator coil and
//! flavor reservoir pockets, cut by the Rust part recipe from the numbers this module states.

use super::above_core::AboveCore;
use super::above_core_mounts as mounts;
use super::cold_core_interface as core;
use super::copper_ports;
use super::foam_cap_parts;
use super::internal_routes;
use super::port_cuts;
use super::reed_b_outlet;
use super::reed_channels;
use super::reservoir_b_fill::{self, BEND_RADIUS, CHANNEL_CENTRE, CHANNEL_RADIUS, MOUTH};
use super::reservoir_pocket_walls as pocket_walls;
use super::support_ring;
use super::*;

pub const NAME: &str = "foam_shell";

/// The names the first `from _cold_core_interface import ...` binds, in its order.
const INTERFACE_NAMES: &[&str] = &[
    "above_carbonator_elbows_height",
    "attachment_xy_positions",
    "casing_foil_land",
    "seam_channel_depth",
    "seam_channel_land",
    "seam_channel_width",
    "bag_pocket_corner_inner_radius",
    "bag_pocket_far_inner_x",
    "bag_pocket_outermost_x",
    "bag_pocket_width",
    "bag_pocket_y_inner_max",
    "coil_radial_clearance",
    "carbonator_coil_envelope_radius",
    "corner_round_radius",
    "forward_band_width",
    "outer_shell_wall",
    "pour_band_pocket_side_y",
    "pour_band_shell_side_y",
    "foam_cap_interior_height",
    "cap_shell_clearance",
    "cap_lid_clearance",
    "foam_cap_lid_pour_radius",
    "foam_cap_lid_vent_radius",
    "foam_shell_outer_height",
    "foam_shell_rim_z",
    "insert_pocket_depth",
    "front_wall_x",
    "mid_screw_x_offset",
    "outer_shell_foam_gap",
    "port_lane_inner_y",
    "port_lane_mid_y",
    "port_lane_outer_y",
    "outer_shell_x_length",
    "outer_shell_y_length",
    "pocket_centerward_arc_outer_radius",
    "port_hole_radius",
    "reservoir_clearance",
    "screw_boss_size",
    "support_ring_radial_width",
    "carbonator_height",
    "carbonator_outer_radius",
    "carbonator_support_ring_height",
    "wall_and_floor_thickness",
    "wall_thickness",
];

/// The names the second `from _cold_core_interface import ...` binds.
const SCREW_NAMES: &[&str] = &[
    "cap_screw_beyond_face",
    "cap_screw_length",
    "head_cbore_radius",
    "head_pad_height",
    "insert_length",
    "screw_head_height",
];

pub struct State {
    here: PathBuf,
    argparse: Val,
    sys: Val,
    c_foam_shell: Val,
    carbonator_height: Val,
    carbonator_outer_radius: Val,
    pocket_centerward_arc_transition_y: f64,
    transition_outer_r: f64,
    co2_inlet_xyz: [f64; 3],
    evap_cross_z: f64,
    copper_hole_radius: f64,
    /// `_copper_ports.stations`, the function itself.
    stations: Val,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let argparse = rt.py("argparse")?;
        let sys = rt.py("sys")?;
        let here = parent(&resolve(&rt.file(NAME)));
        rt.sys_path_insert(0, &ancestor(&here, "printed-parts")?.join("cadlib"))?;
        rt.sys_path_insert(0, &ancestor(&here, "hardware")?.join("scripts"))?;
        rt.sys_path_insert(0, &parent(&here))?;
        let docgen = ancestor_where(&here, |p| p.join("tools").join("docgen").is_dir())?;
        rt.sys_path_insert(0, &docgen.join("tools"))?;
        let c_foam_shell = rt.pya("_materials", "C_FOAM_SHELL")?;
        core::state(rt)?;
        // The interface states the carbonator stock's own height and radius.
        let carbonator_height = rt.pya("_carbonator_stock", "carbonator_height")?;
        let carbonator_outer_radius = rt.pya("_carbonator_stock", "carbonator_outer_radius")?;
        let pockets = pocket_walls::state(rt)?;
        let pocket_centerward_arc_transition_y = pocket_walls::POCKET_CENTERWARD_ARC_TRANSITION_Y;
        let transition_outer_r = pockets.transition_outer_r;
        let co2_inlet_xyz = port_cuts::state(rt)?.co2_inlet_xyz;
        // `from docgen import substitute_md`: the runtime's own substitution.
        // the function object is a member Python sees
        let stations = rt.import_module(copper_ports::NAME)?.a("stations")?;
        let evap_cross_z = copper_ports::EVAP_CROSS_Z;
        let copper_hole_radius = copper_ports::HOLE_RADIUS;
        Ok(Self {
            here,
            argparse,
            sys,
            c_foam_shell,
            carbonator_height,
            carbonator_outer_radius,
            pocket_centerward_arc_transition_y,
            transition_outer_r,
            co2_inlet_xyz,
            evap_cross_z,
            copper_hole_radius,
            stations,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

fn parent(path: &Path) -> PathBuf {
    path.parent().unwrap_or(path).to_owned()
}

/// `list(value)`.
fn listed(value: &Val) -> Result<Val> {
    Ok(Val::list(value.iter()?))
}

/// `box(x, y, z)`: three axis ranges as lists.
fn range_box(x: [f64; 2], y: &Val, z: &Val) -> Result<Val> {
    Ok(Val::list(vec![listed(&x.to_val())?, listed(y)?, listed(z)?]))
}

/// `numbers()`: everything the Rust recipe needs to cut the foam shell.
pub fn numbers(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let fits = rt.py("fits")?;
    let core = core::state(rt)?;
    let b = &core.base;
    let pockets = pocket_walls::state(rt)?;
    support_ring::state(rt)?;
    let reeds = reed_channels::state(rt)?;
    let routes = internal_routes::state(rt)?;
    mounts::state(rt)?;
    let top_cap_height = foam_cap_parts::state(rt)?.top_cap_height;
    let linear = rt.pya("_materials", "linear")?;

    let (mut envelopes, mut cavities, mut openings, mut upper_backs, mut roofs) =
        (vec![], vec![], vec![], vec![], vec![]);
    for side in [1.0f64, -1.0] {
        let x = side * b.reed_channel_inner_x;
        let envelope_y = reeds.reed_envelope_y_range.to_val();
        let envelope_z = reeds.reed_envelope_z_range.to_val();
        let cavity_y = reeds.reed_cavity_y_range.to_val();
        let cavity_z = reeds.reed_cavity_z_range.to_val();
        envelopes.push(range_box(
            [x, x + side * (b.reed_x_depth + b.wall_thickness)],
            &envelope_y,
            &envelope_z,
        )?);
        cavities.push(range_box([x, x + side * b.reed_x_depth], &cavity_y, &cavity_z)?);
        openings.push(range_box(
            [side * b.bag_pocket_far_inner_x, side * b.bag_pocket_outermost_x],
            &cavity_y,
            &(b.wall_and_floor_thickness, b.foam_shell_outer_height).to_val(),
        )?);
        upper_backs.push(range_box(
            [side * b.bag_pocket_far_inner_x, side * b.reed_channel_inner_x],
            &envelope_y,
            &(b.foam_shell_outer_height, b.foam_shell_rim_z).to_val(),
        )?);
        let (a, c) = (side * b.bag_pocket_far_inner_x, side * b.bag_pocket_outermost_x);
        let (x0, x1) = if c < a { (c, a) } else { (a, c) };
        let [y0, y1] = reeds.reed_cavity_y_range;
        let z = b.foam_shell_outer_height;
        roofs.push(dict! {
            "section" => Val::list(vec![
                (y0, z).to_val(),
                (y1, z).to_val(),
                (reeds.reed_y_center, z + 2.0 * b.reed_y_half_w).to_val(),
            ]),
            "start_x" => x0,
            "depth" => x1 - x0,
        });
    }

    let layout = AboveCore::get(rt)?;
    let world_to_shell = |point: [f64; 3]| -> Result<[f64; 3]> {
        let [x, y, z] = layout.world_to_cap(point)?;
        Ok([-x, -y, z + b.foam_shell_outer_height + top_cap_height])
    };
    let origin = world_to_shell([0.0, 0.0, 0.0])?;
    let mut axes = vec![];
    for axis in [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]] {
        axes.push(sub3(world_to_shell(axis)?, origin));
    }
    let passage = reservoir_b_fill::passage(rt)?;
    let b_end = passage.bend_end();

    let mut d = Dict::new();
    d.set("height", b.foam_shell_rim_z);
    d.set("pocket_height", b.foam_shell_outer_height);
    d.set("floor", b.wall_and_floor_thickness);
    d.set("wall", b.wall_thickness);
    d.set("outer_wall", b.outer_shell_wall);
    d.set("width", b.outer_shell_x_length);
    d.set("depth", b.outer_shell_y_length);
    d.set("corner_radius", b.corner_round_radius);
    let transition_x = pocket_walls::TRANSITION_CENTER_X - pockets.transition_cavity_r;
    d.set(
        "pocket",
        dict! {
            "middle_x" => pockets.middle_cavity_x,
            "inner_y" => pockets.y_inner,
            "far_x" => b.bag_pocket_far_inner_x,
            "corner_radius" => b.bag_pocket_corner_inner_radius,
            "transition_y" => pocket_walls::POCKET_CENTERWARD_ARC_TRANSITION_Y,
            "transition_x" => transition_x,
            "transition_mid_y" => pockets.transition_center_y,
            "arc_radius" => pockets.arc_cavity_r,
        },
    );
    d.set(
        "support",
        dict! {
            "outer_radius" => b.carbonator_coil_envelope_radius,
            "inner_radius" => b.carbonator_coil_envelope_radius - b.support_ring_radial_width,
            "bottom" => b.wall_and_floor_thickness,
            "top" => b.wall_and_floor_thickness + b.carbonator_support_ring_height,
            "slots" => support_ring::SLOT_COUNT,
            "slot_angle" => support_ring::SLOT_ANGULAR_WIDTH,
            "slot_clock" => support_ring::SLOT_CLOCK,
            "slot_margin" => support_ring::SLOT_RADIAL_MARGIN,
        },
    );
    d.set("host_radius", b.screw_guard_diameter / 2.0);
    d.set(
        "attachment_stations",
        Val::list(
            b.attachment_stations
                .iter()
                .map(|(xy, wall)| dict! {"xy" => *xy, "wall" => wall.as_str()})
                .collect(),
        ),
    );
    d.set("insert_radius", b.insert_pocket_radius);
    d.set("insert_depth", b.insert_pocket_depth);
    d.set("tail_radius", b.screw_clearance_radius);
    d.set("bottom_tail_depth", b.bottom_screw_bore_depth);
    d.set("top_tail_depth", b.top_screw_bore_depth);
    let supported = fits.a("supported_surface")?;
    let supported_f = supported.f()?;
    d.set(
        "bottom_tapers",
        Val::list(vec![
            dict! {
                "bottom" => b.insert_pocket_depth + supported_f,
                "lower_radius" => b.insert_pocket_radius,
                "upper_radius" => b.screw_clearance_radius,
                "height" => 2.0 * (b.insert_pocket_radius - b.screw_clearance_radius),
            },
            dict! {
                "bottom" => b.bottom_screw_bore_depth + supported_f,
                "lower_radius" => b.screw_clearance_radius,
                "upper_radius" => 0.0,
                "height" => 2.0 * b.screw_clearance_radius,
            },
        ]),
    );
    d.set("supported_surface", supported);
    d.set("seam_depth", b.seam_channel_depth);
    d.set("seam_width", b.seam_channel_width);
    d.set("reed_envelopes", Val::list(envelopes));
    d.set("reed_cavities", Val::list(cavities));
    d.set("reed_openings", Val::list(openings));
    d.set("reed_upper_backs", Val::list(upper_backs));
    d.set("reed_roofs", Val::list(roofs));
    d.set("reed_b_outlet", reed_b_outlet::datums(rt)?.val());
    d.set("vent_route", routes.routes.at("prv-vent")?.clone());
    d.set("vent_bend", routes.route_bend_radius_val.clone());
    d.set("vent_radius", b.port_hole_radius);
    d.set("copper_radius", s.copper_hole_radius);
    let origins = copper_ports::stations(rt)?
        .values()
        .map(|(point, _axis)| point.to_val())
        .collect();
    d.set("copper_origins", Val::list(origins));
    let names = copper_ports::stations(rt)?
        .keys()
        .map(|name| Val::Str(name.to_owned()))
        .collect();
    d.set("copper_names", Val::list(names));
    d.set(
        "b_fill",
        dict! {
            "bend_radius" => BEND_RADIUS,
            "channel_centre" => CHANNEL_CENTRE,
            "channel_radius" => CHANNEL_RADIUS,
            "mouth" => MOUTH,
            "mouth_start_y" => -0.3,
            "mouth_end_y" => MOUTH + 0.05,
            "mouth_start_radius" => CHANNEL_RADIUS + MOUTH + 0.3,
            "mouth_end_radius" => CHANNEL_RADIUS - 0.05,
            "inlet_leg" => b_end[1] - BEND_RADIUS - passage.entry[1],
            "bend_end_world" => b_end,
            "roof_allowance" => passage.supported.clone(),
            "world_to_shell_origin" => origin,
            "world_to_shell_axes" => axes,
        },
    );
    d.set("color", listed(&linear.c(args![s.c_foam_shell])?)?);
    Ok(d.val())
}

/// `update_readme(output, volume, bbox, centroid)`: the README's stated dimensions.
pub fn update_readme(
    rt: &Runtime,
    output: &Val,
    volume: &Val,
    bbox: &Val,
    centroid: &Val,
) -> Result<()> {
    let s = state(rt)?;
    let core = core::state(rt)?;
    let b = &core.base;
    let g = |x: f64| ff(x, ".4g");
    let mm = |x: f64| format!("{} mm", ff(x, ".4g"));
    let vmm = |x: &Val| -> Result<String> { Ok(format!("{} mm", fv(x, ".4g")?)) };
    let f3 = |x: Val| fv(&x, ".3f");
    let f6 = |x: Val| fv(&x, ".6f");
    let screws = b.attachment_xy_positions.len() as i64;
    let variables: Vec<(&str, String)> = vec![
        ("OUTER_H", mm(b.foam_shell_rim_z)),
        ("SHELL_OUTER_X", mm(b.outer_shell_x_length)),
        ("FSHELL_OUTER_Y", g(b.outer_shell_y_length)),
        ("OUTER_GAP", mm(b.outer_shell_foam_gap)),
        ("FSHELL_WALL_T", mm(b.wall_thickness)),
        ("FSHELL_FLOOR_T", mm(b.wall_and_floor_thickness)),
        ("TANK_H", vmm(&s.carbonator_height)?),
        ("TANK_R", vmm(&s.carbonator_outer_radius)?),
        ("POCKET_ARC_R", mm(b.pocket_centerward_arc_outer_radius)),
        (
            "POCKET_ARC_INNER_R",
            mm(b.pocket_centerward_arc_outer_radius - b.wall_thickness),
        ),
        ("POCKET_Y_OUTER", mm(b.bag_pocket_width / 2.0)),
        ("POCKET_Y_INNER", mm(b.bag_pocket_y_inner_max)),
        (
            "POCKET_ARC_TRANSITION_Y",
            mm(s.pocket_centerward_arc_transition_y),
        ),
        ("TRANSITION_ARC_R", mm(s.transition_outer_r)),
        ("COIL_GAP", mm(b.coil_radial_clearance)),
        ("ELBOW_ENV", mm(b.above_carbonator_elbows_height)),
        ("RESERVOIR_GAP", mm(b.reservoir_clearance)),
        ("POCKET_CORNER_R", mm(b.bag_pocket_corner_inner_radius)),
        ("POCKET_X_OUTER", mm(b.bag_pocket_outermost_x)),
        ("POCKET_X_INNER", mm(b.bag_pocket_far_inner_x)),
        ("SUPPORT_RING_H", mm(b.carbonator_support_ring_height)),
        ("SUPPORT_RING_W", mm(b.support_ring_radial_width)),
        (
            "SUPPORT_RING_INNER_R",
            mm(b.carbonator_coil_envelope_radius - b.support_ring_radial_width),
        ),
        ("TUBE_HOLE_D", mm(b.port_hole_radius * 2.0)),
        ("COPPER_HOLE_D", mm(2.0 * s.copper_hole_radius)),
        ("CORNER_ROUND_R", mm(b.corner_round_radius)),
        ("FOIL_LAND", mm(b.casing_foil_land)),
        ("SEAM_CHANNEL_W", mm(b.seam_channel_width)),
        ("SEAM_CHANNEL_D", mm(b.seam_channel_depth)),
        ("SEAM_CHANNEL_LAND", mm(b.seam_channel_land)),
        ("FSHELL_OUTER_WALL", mm(b.outer_shell_wall)),
        (
            "FSHELL_POUR_BAND",
            mm((b.pour_band_shell_side_y - b.pour_band_pocket_side_y).abs()),
        ),
        ("FSHELL_FORWARD_BAND", mm(b.forward_band_width)),
        ("BOSS_D", mm(b.screw_boss_size)),
        (
            "CAP_H",
            mm(b.foam_cap_interior_height - b.cap_shell_clearance - b.cap_lid_clearance),
        ),
        (
            "CAP_H_TOP",
            mm(b.foam_cap_interior_height
                - b.head_pad_height
                - b.cap_shell_clearance
                - b.cap_lid_clearance),
        ),
        ("POUR_D", mm(b.foam_cap_lid_pour_radius * 2.0)),
        ("LID_VENT_D", mm(b.foam_cap_lid_vent_radius * 2.0)),
        ("MID_BOSS_OFFSET", mm(b.mid_screw_x_offset)),
        ("BOSS_COUNT", fi(screws, "g")),
        ("FACE_SCREWS", fi(screws, "g")),
        ("STACK_INSERTS", fi(2 * screws, "g")),
        ("INSERT_DEPTH", mm(b.insert_pocket_depth)),
        ("CAP_SCREW_LEN", g(b.cap_screw_length)),
        ("SCREW_HEAD_H", mm(b.screw_head_height)),
        ("HEAD_CBORE_D", mm(b.head_cbore_radius * 2.0)),
        ("HEAD_PAD_H", mm(b.head_pad_height)),
        ("CAP_SCREW_REACH", mm(b.cap_screw_beyond_face)),
        ("INSERT_LEN", mm(b.insert_length)),
        (
            "TIP_CLEAR",
            mm(b.insert_pocket_depth - b.cap_screw_beyond_face),
        ),
        ("CO2_BORE_Y", g(s.co2_inlet_xyz[1])),
        ("CO2_BORE_Z", g(s.co2_inlet_xyz[2])),
        (
            "LANE_Y",
            format!("{} to {}", g(b.port_lane_outer_y), g(b.port_lane_inner_y)),
        ),
        ("LANE_W", mm(b.port_lane_inner_y - b.port_lane_outer_y)),
        ("LANE_MID_Y", g(b.port_lane_mid_y)),
        ("COPPER_Z", mm(s.evap_cross_z)),
        ("FSHELL_VOLUME", format!("{} mm³", fv(volume, ".3f")?)),
        (
            "FSHELL_BBOX_X",
            format!("{} to {} mm", f3(bbox.a("xmin")?)?, f3(bbox.a("xmax")?)?),
        ),
        (
            "FSHELL_BBOX_Y",
            format!("{} to {} mm", f3(bbox.a("ymin")?)?, f3(bbox.a("ymax")?)?),
        ),
        (
            "FSHELL_BBOX_Z",
            format!("{} to {} mm", f3(bbox.a("zmin")?)?, f3(bbox.a("zmax")?)?),
        ),
        (
            "CENTROID",
            format!(
                "({}, {}, {}) mm",
                f6(centroid.a("x")?)?,
                f6(centroid.a("y")?)?,
                f6(centroid.a("z")?)?
            ),
        ),
    ];
    let variables: Vec<(String, String)> = variables
        .into_iter()
        .map(|(k, v)| (k.to_owned(), v))
        .collect();
    let target = hsm_documents::interop::binary("truediv", output.clone(), "README.md".into())?;
    rt.substitute_md(&PathBuf::from(target.str()?), &variables, Some(NAME))?;
    rt.print("-> README.md")
}

/// `main(output=_here)`: cut the shell into `output` and report its front-face stations.
pub fn run(rt: &Runtime, output: Val) -> Result<()> {
    let core = core::state(rt)?;
    let rust_part = rt.py("_rust_part")?;
    let output = rt.import_module("pathlib")?.a("Path")?.c(args![output])?;
    output.mk("mkdir", vec![], kw!["parents" => true, "exist_ok" => true])?;
    let readings = rust_part
        .m("cut", args!["cold-core", "foam-shell", numbers(rt)?, output])?
        .k("bodies")?
        .i(0)?;
    let ports = readings.k("front_ports")?.list()?;
    let mut stations = vec![];
    for p in &ports {
        let origin = p.k("origin")?;
        stations.push(format!(
            "{} y {} z {}",
            fv(&p.k("name")?, "")?,
            fv(&origin.i(1)?, ".4g")?,
            fv(&origin.i(2)?, ".4g")?
        ));
    }
    rt.print(format!(
        "  front face:       {} stations on x {}, all open — {}",
        ports.len(),
        ff(core.base.front_wall_x, ".4g"),
        stations.join(", ")
    ))
}

/// The native `substitute_md(path, variables)` this module imported from docgen.
fn substitute_md(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let path = PathBuf::from(c.req::<Val>(0, "path")?.str()?);
    let variables: Val = c.req(1, "variables")?;
    let mut values = vec![];
    for key in variables.iter()? {
        values.push((key.str()?, variables.get(key)?.str()?));
    }
    rt.substitute_md(&path, &values, Some(NAME))?;
    Ok(Val::None)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("argparse", s.argparse.clone());
    ns.value("sys", s.sys.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", Val::Path(s.here.clone()));
    ns.value("C_FOAM_SHELL", s.c_foam_shell.clone());
    let interface = rt.import_module(core::NAME)?;
    for name in INTERFACE_NAMES {
        ns.value(name, interface.a(name)?);
    }
    ns.value(
        "pocket_centerward_arc_transition_y",
        s.pocket_centerward_arc_transition_y,
    );
    ns.value("transition_outer_r", s.transition_outer_r);
    ns.value("co2_inlet_xyz", s.co2_inlet_xyz);
    for name in SCREW_NAMES {
        ns.value(name, interface.a(name)?);
    }
    ns.func(rt, "substitute_md", substitute_md);
    ns.value("evap_cross_z", s.evap_cross_z);
    ns.value("copper_hole_radius", s.copper_hole_radius);
    ns.value("stations", s.stations.clone());
    ns.func(rt, "numbers", |rt, _| numbers(rt));
    ns.func(rt, "update_readme", |rt, c| {
        let output = c.req::<Val>(0, "output")?;
        let volume = c.req::<Val>(1, "volume")?;
        let bbox = c.req::<Val>(2, "bbox")?;
        let centroid = c.req::<Val>(3, "centroid")?;
        update_readme(rt, &output, &volume, &bbox, &centroid)?;
        Ok(Val::None)
    });
    let here = s.here.clone();
    ns.func(rt, "main", move |rt, c| {
        let output = c.opt::<Val>(0, "output", Val::Path(here.clone()))?;
        run(rt, output)?;
        Ok(Val::None)
    });
    Ok(())
}

/// The `__main__` block: start the part runner, read `--output` and cut.
pub fn main(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    rt.py("_rust_part")?.m("start", vec![])?;
    let description = super::table::documentation(NAME).map_or(Val::None, Val::from);
    let parser = s
        .argparse
        .mk("ArgumentParser", vec![], kw!["description" => description])?;
    parser.mk(
        "add_argument",
        args!["--output"],
        kw![
            "type" => rt.import_module("pathlib")?.a("Path")?,
            "default" => Val::Path(s.here.clone()),
        ],
    )?;
    let parsed = parser.m("parse_args", vec![])?;
    run(rt, parsed.a("output")?)
}
