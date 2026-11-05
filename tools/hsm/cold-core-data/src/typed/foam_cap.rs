//! `foam_cap`: the top equipment lid, the open-topped bottom cap and the internal B-fill bend
//! holder, cut by the Rust part recipe from the numbers this module states.

use super::above_core::AboveCore;
use super::above_core_mounts as mounts;
use super::cold_core_interface as core;
use super::foam_cap_parts;
use super::reservoir_b_fill::{self, BEND_RADIUS, CHANNEL_CENTRE, CHANNEL_RADIUS, MOUTH, WALL};
use super::*;

pub const NAME: &str = "foam_cap";

/// The names the two `from _cold_core_interface import ...` statements bind, in their order.
const INTERFACE_NAMES: &[&str] = &[
    "cap_conduit_links",
    "cap_conduit_link_width",
    "attachment_xy_positions",
    "cap_shell_clearance",
    "cap_lid_clearance",
    "wall_and_floor_thickness",
    "corner_round_radius",
    "foam_cap_lid_pour_radius",
    "foam_cap_lid_pour_xy",
    "foam_cap_lid_vent_radius",
    "foam_cap_lid_vent_xy",
    "head_pad_height",
    "screw_clearance_radius",
    "head_cbore_radius",
    "head_cbore_depth",
    "deck_mounts",
    "deck_mount_cap_gap",
    "deck_mount_xy",
    "deck_mount_boss_radius",
    "deck_mount_bore_radius",
    "deck_mount_bore_depth",
    "deck_mount_standoff",
    "deck_lid_hole_radius",
    "cap_conduits",
    "cap_conduit_bore_radius",
    "cap_conduit_boss_radius",
    "cap_conduit_entry_relief_radius",
    "cap_cradles",
    "cap_cradle_boss_radius",
    "cap_cradle_socket_radius",
    "cap_cradle_wall",
    "cap_cradle_room_gap",
    "cap_cradle_half_x",
    "cap_cradle_half_y",
    "cap_anchors",
    "cap_anchor_axis_over_face",
    "cap_side_anchors",
    "cap_side_anchor_height",
    "cap_side_anchor_holds",
    "cap_side_axis_y",
    "cap_side_tunnel_h",
    "cap_side_tunnel_roof",
    "cap_side_back_relief",
    "cap_side_cav_w",
    "cap_side_flank",
    "cap_side_len",
    "cap_side_wall",
    "cap_anchor_cav_w",
    "cap_anchor_cav_wall",
    "cap_anchor_len",
    "cap_anchor_wall",
    "cap_anchor_channel_height",
    "outer_shell_wall",
    "outer_shell_x_length",
    "outer_shell_y_length",
];

/// The clip tip angle every tube clip shares.
const TIP_DEGREES: f64 = 125.42102606277044;

pub struct State {
    here: PathBuf,
    printed: PathBuf,
    argparse: Val,
    sys: Val,
    fits: Val,
    mat: Val,
    seat: Val,
    a_anchors: Val,
    above_core_wiring: Val,
    reservoir_ports: Val,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let argparse = rt.py("argparse")?;
        let sys = rt.py("sys")?;
        let here = parent(&resolve(&rt.file(NAME)));
        let printed = ancestor(&here, "printed-parts")?;
        rt.sys_path_insert(0, &printed.join("cadlib"))?;
        rt.sys_path_insert(0, &ancestor(&here, "hardware")?.join("scripts"))?;
        rt.sys_path_insert(0, &parent(&here))?;
        rt.sys_path_insert(0, &printed.join("valve-seat"))?;
        let docgen = ancestor_where(&here, |p| p.join("tools").join("docgen").is_dir())?;
        rt.sys_path_insert(0, &docgen.join("tools"))?;
        let fits = rt.py("fits")?;
        let mat = rt.py("_materials")?;
        let seat = rt.py("valve_seat")?;
        mounts::state(rt)?;
        let a_anchors = rt.import_module("_reservoir_a_anchors")?; // via namespace: _reservoir_a_anchors
        let above_core_wiring = rt.py("above_core_wiring")?;
        let reservoir_ports = rt.import_module("_reservoir_ports")?; // via namespace: _reservoir_ports
        foam_cap_parts::state(rt)?;
        core::state(rt)?;
        // `from docgen import substitute_py_comments`: the runtime's own substitution.
        Ok(Self {
            here,
            printed,
            argparse,
            sys,
            fits,
            mat,
            seat,
            a_anchors,
            above_core_wiring,
            reservoir_ports,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

fn parent(path: &Path) -> PathBuf {
    path.parent().unwrap_or(path).to_owned()
}

/// `(DOME_LIFT)`: `_reservoir_b_fill`'s dome rise over the channel's top.
fn dome_lift() -> f64 {
    (2f64.sqrt() - 1.0) * CHANNEL_RADIUS
}

/// `deck_boss_z_top(name)`: the top of a deck mount's column above the lid's underside.
pub fn deck_boss_z_top(rt: &Runtime, name: &str) -> Result<f64> {
    let lid_total_height = foam_cap_parts::state(rt)?.lid_total_height;
    Ok(lid_total_height + core::state(rt)?.deck_mount_standoff(name)?)
}

/// A tube clip's row in `tube_clips`.
fn clip(centre: Val, along: Val, radius: Val, wing: Val, span: Val, tip_degrees: Val) -> Val {
    dict! {
        "centre" => centre,
        "along" => along,
        "radius" => radius,
        "wing" => wing,
        "span" => span,
        "tip_degrees" => tip_degrees,
    }
}

/// `numbers()`: everything the Rust recipe needs to cut the lid, the bottom cap, the B-fill
/// guide and the pump snap cap.
pub fn numbers(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let fc = foam_cap_parts::state(rt)?;
    let core = core::state(rt)?;
    let b = &core.base;
    let a_snap = rt.import_module("_reservoir_a_c2")?; // via namespace: _reservoir_a_c2
    let above_core_routes = rt.py("above_core_routes")?;
    let rear_snaps = rt.py("rear_snaps")?;
    let linear = rt.pya("_materials", "linear")?;
    let root = ancestor_where(&s.here, |p| p.join("hardware").is_dir())?;
    rt.sys_path_insert(0, &root)?;
    let retainers = rt.py("hardware.wiring.installed.retainers")?;
    let manifold_bank_site = retainers.a("manifold_bank_site")?;
    let rear_level_hook_site = retainers.a("rear_level_hook_site")?;
    let layout = AboveCore::get(rt)?;
    let pose = layout.cap_lid_pose()?;
    let world_origin = layout.world_to_cap((0.0, 0.0, 0.0))?;
    let mut world_axes = vec![];
    for axis in [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)] {
        world_axes.push(sub3(layout.world_to_cap(axis)?, world_origin));
    }
    let pump = mounts::pump_cradle_datums(rt)?.val.clone();
    let b_fill = reservoir_b_fill::passage(rt)?;
    let r = CHANNEL_RADIUS;
    let centre = CHANNEL_CENTRE;
    let outer = r + WALL;
    let height = centre + dome_lift() + outer;
    let [x, y, z] = b_fill.bend_end();
    let bend = BEND_RADIUS;
    let guide_world_bounds = [
        [x + centre - height, x + centre],
        [y - bend, y + outer],
        [z + bend - outer, z + bend + outer],
    ];
    let mut corners = vec![];
    for px in guide_world_bounds[0] {
        for py in guide_world_bounds[1] {
            for pz in guide_world_bounds[2] {
                corners.push(layout.world_to_cap((px, py, pz))?);
            }
        }
    }
    let guide_bounds = [
        (0..3)
            .map(|i| fmin(corners.iter().map(|p| p[i])))
            .collect::<Vec<f64>>(),
        (0..3)
            .map(|i| fmax(corners.iter().map(|p| p[i])))
            .collect::<Vec<f64>>(),
    ];
    let spec = layout.spec();
    let va = spec.k("fore_routes")?.k("va_feed_snap")?;
    let mut clips = vec![clip(
        va.k("centre_world_mm")?,
        va.k("along_world")?,
        Val::Float(6.35 / 2.0),
        Val::Float(2.4),
        Val::Float(8.0),
        Val::Float(TIP_DEGREES),
    )];
    for (p, u) in [
        ((26.5, 266.0, 296.0), (1.0, 0.0, 0.0)),
        ((35.0, 414.0, 264.0), (0.0, 1.0, 0.0)),
    ] {
        clips.push(clip(
            p.to_val(),
            u.to_val(),
            Val::Float(4.1 / 2.0),
            Val::Float(1.52),
            Val::Float(8.0),
            Val::Float(TIP_DEGREES),
        ));
    }
    let a_spec = a_snap.m("specification", vec![])?; // via namespace: _reservoir_a_c2
    for p in a_spec.k("tube_centers_world_mm")?.iter()? {
        clips.push(clip(
            p,
            a_spec.k("tube_axis_world")?,
            a_spec.k("seat_radius_mm")?,
            a_spec.k("spring_thickness_mm")?,
            a_spec.k("station_length_mm")?,
            a_spec.k("tip_degrees")?,
        ));
    }
    let wiring = &s.above_core_wiring;
    let mut wells = vec![];
    for item in wiring
        .m("placements", vec![])?
        .m("items", vec![])?
        .iter()?
    {
        let pair = item.iter()?;
        ensure!(pair.len() == 2, "expected 2 values, got {}", pair.len());
        let (name, placement) = (pair[0].clone(), pair[1].clone());
        if hsm_documents::interop::compare("ne", placement.k("parent")?, Val::Str("cold-core".into()))?
            .truthy()?
        {
            continue;
        }
        let size = wiring.a("SIZES")?.get(placement.k("size")?)?;
        wells.push(dict! {"name" => name, "pose" => placement, "size" => size});
    }

    let stations = |rows: &[([f64; 2], String)]| -> Val {
        Val::list(
            rows.iter()
                .map(|(xy, wall)| dict! {"xy" => *xy, "wall" => wall.as_str()})
                .collect(),
        )
    };
    let mut bottom_holes = vec![];
    for xy in &b.bottom_pour_positions {
        bottom_holes.push(dict! {"xy" => *xy, "radius" => b.bottom_pour_radius});
    }
    for xy in core.foam_cap_lid_vent_xy(false) {
        bottom_holes.push(dict! {"xy" => xy, "radius" => b.foam_cap_lid_vent_radius});
    }
    let ports = &s.reservoir_ports;
    let mut air_holes = vec![];
    for xy in ports.a("air_position")?.m("values", vec![])?.iter()? {
        // via namespace: _reservoir_ports
        let mut negated = vec![];
        for v in xy.iter()? {
            negated.push(Num::from_val(&v)?.neg());
        }
        let diameter = ports.a("air_passage_diameter")?.f()?; // via namespace: _reservoir_ports
        air_holes.push(dict! {"xy" => negated, "radius" => diameter / 2.0});
    }
    let mut conduits = Dict::new();
    for (name, xy) in core.cap_conduits.iter() {
        if !["reservoir-b-fill", "water-in", "carb-water-out"].contains(&name) {
            conduits.set(name, *xy);
        }
    }
    let mut reliefs = Dict::new();
    for (name, xy) in core.cap_conduits.iter() {
        let excluded = ["reservoir-b-fill", "water-in", "sensor-cable"].contains(&name)
            || core.cap_conduit_bore_radii.keys().any(|k| k == name);
        if !excluded {
            reliefs.set(name, *xy);
        }
    }
    let mut deck_columns = vec![];
    for name in core.deck_mounts.keys() {
        for xy in core.deck_mount_xy(name)? {
            deck_columns.push(dict! {"xy" => xy, "top" => deck_boss_z_top(rt, name)?});
        }
    }
    let mut straight_guides = vec![];
    for name in ["water-in", "carb-water-out"] {
        straight_guides.push(dict! {
            "point" => spec.k("cap_guides_world_mm")?.k(name)?,
            "floor" => pose.k("translation_mm")?.i(2)?.f()? - fc.top_cap_height,
        });
    }
    let mut snap = Dict::new();
    for name in ["WING", "REACH", "LEDGE", "HOOK", "CATCH"] {
        snap.set(name, rear_snaps.a(name)?);
    }
    let valve_wall = mounts::valve_support_datums(rt, "valve-v-b", Some(fc.lid_total_height))?.val;
    let valve_pose = layout.pose("valve-v-b")?;
    let mut valve = Dict::new();
    for key in [
        "corner_inset_x",
        "corner_inset_y",
        "socket_radius",
        "socket_floor_z",
        "seat_top_z",
        "seat_half_y",
        "port_air",
    ] {
        valve.set(key, s.seat.a(key)?);
    }
    let valve_port_radius = s.seat.a("valve")?.a("port_radius")?;
    let valve_port_z = s.seat.a("valve")?.a("port_center_z")?;
    let mut union_supports = Dict::new();
    for (name, support) in mounts::union_support_datums(rt)? {
        union_supports.set(name, &support.val);
    }
    let well_wall = wiring.a("WALL")?;
    let well_fit = wiring.a("FIT")?;
    let a_seats = s.a_anchors.m("datums", vec![])?; // via namespace: _reservoir_a_anchors
    let a_seat_spec = s.a_anchors.m("specification", vec![])?; // via namespace: _reservoir_a_anchors
    let mut a_routes = Dict::new();
    for item in above_core_routes
        .m("reservoir_a_route_specs", vec![])?
        .m("items", vec![])?
        .iter()?
    {
        let pair = item.iter()?;
        ensure!(pair.len() == 2, "expected 2 values, got {}", pair.len());
        a_routes.set(&pair[0], pair[1].k("segments")?);
    }
    let flavor_wall = mounts::valve_support_datums(rt, "valve-v-b", None)?.val;
    let cable_bank = manifold_bank_site.c(vec![])?;
    let cable_hook = rear_level_hook_site.c(vec![])?;
    let b_fill_numbers = dict! {
        "bend" => bend,
        "radius" => r,
        "centre" => centre,
        "outer" => outer,
        "dome_lift" => dome_lift(),
        "inlet" => y - bend - b_fill.entry[1],
        "mouth" => MOUTH,
        "mouth_start" => -0.3,
        "mouth_end" => MOUTH + 0.05,
        "end_world" => vec![x, y, z],
        "guide_bounds_cap" => guide_bounds.to_vec(),
    };
    let colors = dict! {
        "foam-cap-lid-top" => linear.c(args![s.mat.a("C_CAP_LID_TOP")?])?,
        "foam-cap-bottom" => linear.c(args![s.mat.a("C_CAP_BOTTOM")?])?,
        "reservoir-b-fill-guide" => linear.c(args![s.mat.a("C_CAP_TOP")?])?,
        "pump-snap-cap" => linear.c(args![s.mat.a("M_PETGF_BLACK")?])?,
    };

    let mut d = Dict::new();
    d.set("width", b.outer_shell_x_length);
    d.set("depth", b.outer_shell_y_length);
    d.set("corner", b.corner_round_radius);
    d.set("wall", b.outer_shell_wall);
    d.set("floor", b.wall_and_floor_thickness);
    d.set("lid_height", fc.lid_total_height);
    d.set("bottom_height", b.bottom_cap_height);
    d.set("head_radius", b.head_cbore_radius);
    d.set("head_depth", b.head_cbore_depth);
    d.set("screw_radius", b.screw_clearance_radius);
    d.set("boss_radius", b.screw_boss_size / 2.0);
    d.set("head_pad_growth", fc.head_pad_growth);
    d.set("supported_surface", s.fits.a("supported_surface")?);
    d.set("running", s.fits.a("running")?);
    d.set("slip", s.fits.a("slip")?);
    d.set("bottom_stations", stations(b.attachment_stations.as_slice()));
    d.set("top_stations", stations(b.lid_attachment_stations.as_slice()));
    d.set("bottom_holes", Val::list(bottom_holes));
    d.set("air_holes", Val::list(air_holes));
    d.set("conduits", conduits);
    d.set("reliefs", reliefs);
    d.set("conduit_radius", core.cap_conduit_bore_radius);
    d.set("conduit_radii", core.cap_conduit_bore_radii.to_val());
    d.set("relief_radius", core.cap_conduit_entry_relief_radius);
    d.set("deck_columns", Val::list(deck_columns));
    d.set("deck_radius", b.deck_mount_boss_radius);
    d.set("deck_bore_radius", b.deck_mount_bore_radius);
    d.set("deck_bore_depth", core.deck_mount_bore_depth);
    d.set("straight_guides", Val::list(straight_guides));
    d.set("world_to_cap_origin", world_origin);
    d.set("world_to_cap_axes", world_axes);
    d.set("cap_face_world_z", spec.k("cap_face_z_mm")?);
    d.set("pump", pump);
    d.set("snap", snap);
    d.set("valve_wall", valve_wall);
    d.set("valve_pose", valve_pose);
    d.set("valve", valve);
    d.set("valve_port_radius", valve_port_radius);
    d.set("valve_port_z", valve_port_z);
    d.set("union_supports", union_supports);
    d.set("wells", Val::list(wells));
    d.set("well_wall", well_wall);
    d.set("well_fit", well_fit);
    d.set("a_seats", a_seats);
    d.set("a_seat_spec", a_seat_spec);
    d.set("a_snap", a_spec);
    d.set("a_routes", a_routes);
    d.set("tube_clips", Val::list(clips));
    d.set("flavor_wall", flavor_wall);
    d.set("cable_bank", cable_bank);
    d.set("cable_hook", cable_hook);
    d.set("b_fill", b_fill_numbers);
    d.set("colors", colors);
    Ok(d.val())
}

/// `main(output=_here)`: cut the cap's parts into `output`, flute their meshes and clear the
/// retired part files.
pub fn run(rt: &Runtime, output: Val) -> Result<()> {
    let rust_part = rt.py("_rust_part")?;
    let flute_payload = rt.py("flute_payload")?;
    let output = rt.import_module("pathlib")?.a("Path")?.c(args![output])?;
    output.mk("mkdir", vec![], kw!["parents" => true, "exist_ok" => true])?;
    rust_part.m("cut", args!["cold-core", "foam-cap", numbers(rt)?, output])?;
    let out = PathBuf::from_val(&output)?;
    for name in [
        "foam-cap-lid-top",
        "foam-cap-bottom",
        "reservoir-b-fill-guide",
        "pump-snap-cap",
    ] {
        flute_payload.mk(
            "cut",
            args![
                Val::Path(out.join(format!("{name}.step"))),
                Val::Path(out.join(format!("{name}.stl")))
            ],
            kw!["preserve_print_triangles" => name == "pump-snap-cap"],
        )?;
    }
    for name in ["foam-cap-top", "foam-cap-lid-bottom", "pump-snap-cap-rear"] {
        for suffix in [".step", ".step.mesh", ".stl"] {
            Val::Path(out.join(format!("{name}{suffix}"))).mk(
                "unlink",
                vec![],
                kw!["missing_ok" => true],
            )?;
        }
    }
    Ok(())
}

/// The native `substitute_py_comments(path, variables)` this module imported from docgen.
fn substitute_py_comments(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let path = PathBuf::from(c.req::<Val>(0, "path")?.str()?);
    let variables: Val = c.req(1, "variables")?;
    let mut values = vec![];
    for key in variables.iter()? {
        values.push((key.str()?, variables.get(key)?.str()?));
    }
    rt.substitute_py_comments(&path, &values, Some(NAME))?;
    Ok(Val::None)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    let fc = foam_cap_parts::state(rt)?;
    ns.value("argparse", s.argparse.clone());
    ns.module(rt, "math", "math")?;
    ns.value("sys", s.sys.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", Val::Path(s.here.clone()));
    ns.value("_printed", Val::Path(s.printed.clone()));
    ns.value("fits", s.fits.clone());
    ns.value("_mat", s.mat.clone());
    ns.value("seat", s.seat.clone());
    ns.module(rt, "_above_mounts", mounts::NAME)?;
    ns.value("_a_anchors", s.a_anchors.clone());
    ns.value("above_core_wiring", s.above_core_wiring.clone());
    ns.value("reservoir_ports", s.reservoir_ports.clone());
    ns.module(rt, "_reservoir_b_fill", reservoir_b_fill::NAME)?;
    ns.value("head_pad_growth", fc.head_pad_growth);
    ns.value("lid_cut_through_depth", fc.lid_cut_through_depth);
    ns.value("lid_total_height", fc.lid_total_height);
    ns.value("top_cap_height", fc.top_cap_height);
    let interface = rt.import_module(core::NAME)?;
    for name in INTERFACE_NAMES {
        ns.value(name, interface.a(name)?);
    }
    ns.func(rt, "substitute_py_comments", substitute_py_comments);
    ns.func(rt, "deck_boss_z_top", |rt, c| {
        Ok(deck_boss_z_top(rt, &c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "numbers", |rt, _| numbers(rt));
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
