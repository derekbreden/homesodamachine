//! `reservoir`: the open-top `[`-shaped PETG cups standing on the bag-pocket floors of the
//! foam shell, their cap clamps, gaskets and tube grips, in shell millimetres. Mirrored ±X.

use super::cold_core_interface as core;
use super::reed_channels::{self, REEDS_PER_RESERVOIR};
use super::reservoir_ports as tube_ports;
use super::*;

pub const NAME: &str = "reservoir";

pub const OUTER_CORNER_FILLET_RADIUS: f64 = 6.0;
pub const INNER_CORNER_FILLET_RADIUS: f64 = 6.0;
pub const CAP_WALL_HEIGHT: f64 = 5.0;
pub const CAP_WALL_WIDTH: f64 = 6.0;
pub const GASKET_THICKNESS: f64 = 2.0;
pub const GASKET_STRIP_WIDTH: f64 = 5.0;
pub const ROD_REGISTER_BOSS_HEIGHT: f64 = 2.0;
pub const ROD_ANCHOR_BOSS_HEIGHT: f64 = 6.0;
pub const ROD_ANCHOR_BOSS_FLOOR: f64 = 0.0;
pub const INSERT_POCKET_RADIUS: f64 = 2.0;
pub const INSERT_POCKET_DEPTH: f64 = 7.0;
pub const BOSS_ANNULUS: f64 = 3.0;
pub const BOSS_HEIGHT: f64 = 15.0;
pub const CYL_EXTRA_BELOW_BOTTOM: f64 = 5.0;
pub const CORNER_CURVE_PIVOT_DISTANCE: f64 = 2.0;

/// The documents beside this file that `document` fills.
const DOCUMENTS: [&str; 3] = ["vent.md", "level-sensing.md", "floor-and-dip-tube.md"];
/// The printed pieces `main` writes payloads for.
const PRINTED: [&str; 4] = [
    "reservoir-cap-right",
    "reservoir-cap-left",
    "reservoir-tube-grip",
    "reservoir-air-grip",
];
/// The reed-cable conduits the level-sensing document locates.
const REED_CONDUITS: [&str; 1] = ["reed-cable-a"];

pub struct State {
    pub here: PathBuf,
    mat: Val,
    fits: Val,
    float: Val,
    /// `_float_interface` figures as the provider states them.
    float_guide_diameter: Val,
    float_diameter: Val,
    float_bore_diameter: Val,
    float_rod_axis_from_inner_wall: Val,
    float_height: Val,
    pub bag_pocket_far_inner_x: f64,
    pub bag_pocket_y_inner_max: f64,
    pub bag_pocket_floor_top_z: f64,
    pub bag_pocket_walls_top_z: f64,
    pub pocket_centerward_arc_outer_radius: f64,
    pub port_hole_radius: f64,
    pub reservoir_clearance: f64,
    pub reservoir_floor_thickness: f64,
    pub reservoir_draw_port: core::Ports,
    pub reservoir_fill_port: core::Ports,
    pub reservoir_fill_sides: [i64; 2],
    pub level_rod_y: f64,
    pub lldpe_tube_od: f64,
    pub reservoir_wall_thickness: f64,
    pub cap_base_thickness: f64,
    pub cap_counterbore_diameter: f64,
    pub cap_counterbore_depth: f64,
    pub cap_clearance_hole_diameter: f64,
    pub cap_perimeter_z_range: (i64, f64),
    pub cap_base_z_range: [f64; 2],
    pub cap_total_height: f64,
    pub fill_bore_diameter: f64,
    pub reservoir_count: i64,
    pub rod_position_y: f64,
    pub rod_diameter: f64,
    pub rod_bore: f64,
    pub rod_boss_od: f64,
    pub body_boss_radius: f64,
    pub cap_boss_radius: f64,
    pub gasket_pad_radius: f64,
    pub outer_far_x_abs: f64,
    pub outer_y_max: f64,
    pub outer_centerward_radius: f64,
    pub inner_far_x_abs: f64,
    pub inner_y_max: f64,
    pub inner_centerward_radius: f64,
    pub rod_position_x: f64,
    pub outer_tab_interior_angle: f64,
    pub inner_corner_interior_angle: f64,
    pub cap_stack_above_body: f64,
    pub outer_z_range: [f64; 2],
    pub inner_z_range: [f64; 2],
    pub cap_assembly_lift: f64,
    pub cap_top_z: f64,
    pub rod_floor_z: f64,
    pub reservoir_rod_clearance: f64,
    pub reservoir_rod_len: f64,
    pub float_magnet_travel_z: [f64; 2],
    pub float_travel: f64,
    pub reservoir_reed_pitch: f64,
    pub reed_span: f64,
    pub reed_mid: f64,
    pub reservoir_reed_centres_z: [f64; REEDS_PER_RESERVOIR as usize],
    pub dip_tube_mouth_z: f64,
    pub outer_corner_x: f64,
    pub inner_corner_x: f64,
    screw_setback: f64,
    corner_xy_x: f64,
    corner_xy_y: f64,
    far_mid_x: f64,
    curve_apex_x: f64,
    corner_curve_y: f64,
    corner_curve_r: f64,
    corner_curve_x: f64,
    pub insert_positions_for_side_plus_1: [[f64; 2]; 6],
    far_wall_inner_x: f64,
    plus_y_wall_inner_y: f64,
    curve_inner_x_at_y0: f64,
    inv_sqrt2: f64,
    inner_corner_curve_x: f64,
    corner_curve_to_inner_corner_dx: f64,
    corner_curve_to_inner_corner_dy: f64,
    corner_curve_to_inner_corner_dist: f64,
    corner_curve_wall_dir_x: f64,
    corner_curve_wall_dir_y: f64,
    corner_curve_virtual_pivot_x: f64,
    corner_curve_virtual_pivot_y: f64,
    /// `body_boss_cut_info_for_side_plus_1`, in the dict's insertion order.
    pub body_boss_cut_info_for_side_plus_1: Vec<([f64; 2], [f64; 4])>,
}

impl State {
    /// `body_boss_cut_info_for_side_plus_1.get(xy)`.
    pub fn body_boss_cut_info(&self, xy: [f64; 2]) -> Option<[f64; 4]> {
        self.body_boss_cut_info_for_side_plus_1
            .iter()
            .find(|(key, _)| *key == xy)
            .map(|(_, info)| *info)
    }
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let here = parent_n(&resolve(&rt.file(NAME)), 0);
        rt.sys_path_insert(0, &ancestor(&here, "printed-parts")?.join("cadlib"))?;
        rt.sys_path_insert(0, &ancestor(&here, "hardware")?.join("scripts"))?;
        rt.sys_path_insert(0, &parent_n(&here, 0))?;
        let docgen = ancestor_where(&here, |p| p.join("tools").join("docgen").is_dir())?;
        rt.sys_path_insert(0, &docgen.join("tools"))?;
        let mat = rt.py("_materials")?;
        let fits = rt.py("fits")?;
        let core = core::state(rt)?;
        let base = &core.base;
        // `from _reed_channels import reeds_per_reservoir` runs that module's stated bounds.
        reed_channels::state(rt)?;
        let float = rt.py("_float_interface")?;
        let slip = fits.a("slip")?.f()?;
        let supported_surface = fits.a("supported_surface")?.f()?;

        let reservoir_wall_thickness = base.reservoir_floor_thickness;
        let cap_base_thickness = tube_ports::PLATE_THICKNESS;
        let cap_counterbore_diameter = 5.5 + 2.0 * slip;
        let cap_counterbore_depth = cap_base_thickness + supported_surface;
        let cap_clearance_hole_diameter = 3.0 + 2.0 * slip;
        let cap_perimeter_z_range = (0, CAP_WALL_HEIGHT);
        let cap_base_z_range = [CAP_WALL_HEIGHT, CAP_WALL_HEIGHT + cap_base_thickness];
        let cap_total_height = cap_base_z_range[1];
        let fill_bore_diameter = tube_ports::LIQUID_GRIP.waist_d;
        // `len(fill_position)`: the fill-port dict holds both sides.
        let reservoir_count = 2;
        let rod_position_y = base.level_rod_y;
        let float_guide_diameter = float.a("guide_diameter")?;
        let rod_diameter = float_guide_diameter.f()?;
        let rod_bore = rod_diameter + 2.0 * slip;
        let rod_boss_od = rod_bore + 4.0;
        let body_boss_radius = INSERT_POCKET_RADIUS + BOSS_ANNULUS;
        let cap_boss_radius = body_boss_radius;
        let gasket_pad_radius = body_boss_radius;
        let outer_far_x_abs = base.bag_pocket_far_inner_x - base.reservoir_clearance;
        let outer_y_max = base.bag_pocket_y_inner_max - base.reservoir_clearance;
        let outer_centerward_radius =
            base.pocket_centerward_arc_outer_radius + base.reservoir_clearance;
        let inner_far_x_abs = outer_far_x_abs - reservoir_wall_thickness;
        let inner_y_max = outer_y_max - reservoir_wall_thickness;
        let inner_centerward_radius = outer_centerward_radius + reservoir_wall_thickness;
        let float_diameter = float.a("diameter")?;
        let float_bore_diameter = float.a("bore_diameter")?;
        let float_rod_axis_from_inner_wall = float.a("rod_axis_from_inner_wall")?;
        let rod_position_x = inner_far_x_abs - float_rod_axis_from_inner_wall.f()?;
        let outer_tab_interior_angle = degrees((outer_y_max / outer_centerward_radius).acos());
        let inner_corner_interior_angle = degrees((inner_y_max / inner_centerward_radius).acos());
        let cap_stack_above_body = GASKET_THICKNESS + CAP_WALL_HEIGHT + cap_base_thickness;
        let outer_z_range = [
            base.bag_pocket_floor_top_z + base.reservoir_clearance,
            base.bag_pocket_walls_top_z - base.reservoir_clearance - cap_stack_above_body,
        ];
        let inner_z_range = [outer_z_range[0] + reservoir_wall_thickness, outer_z_range[1]];
        let cap_assembly_lift = outer_z_range[1] + GASKET_THICKNESS;
        let cap_top_z = cap_assembly_lift + cap_total_height;
        let rod_floor_z = inner_z_range[0];
        let reservoir_rod_clearance = slip;
        let reservoir_rod_len = cap_assembly_lift + CAP_WALL_HEIGHT
            - (rod_floor_z + ROD_ANCHOR_BOSS_FLOOR)
            - reservoir_rod_clearance;
        let magnet_midplane = float.a("magnet_midplane")?.f()?;
        let float_height = float.a("height")?;
        let float_magnet_travel_z = [
            rod_floor_z + ROD_ANCHOR_BOSS_HEIGHT + magnet_midplane,
            cap_assembly_lift - ROD_REGISTER_BOSS_HEIGHT - (float_height.f()? - magnet_midplane),
        ];
        let float_travel = float_magnet_travel_z[1] - float_magnet_travel_z[0];
        let reservoir_reed_pitch = (float_travel / (REEDS_PER_RESERVOIR - 1) as f64).floor();
        let reed_span = (REEDS_PER_RESERVOIR - 1) as f64 * reservoir_reed_pitch;
        let reed_mid = fsum(float_magnet_travel_z) / 2.0;
        let reservoir_reed_centres_z =
            std::array::from_fn(|i| reed_mid - reed_span / 2.0 + i as f64 * reservoir_reed_pitch);
        ensure!(reed_span < float_travel, "assertion failed");
        let dip_tube_mouth_z = rod_floor_z + core.lldpe_tube_od / 2.0;
        let outer_corner_x = (outer_centerward_radius.powf(2.0) - outer_y_max.powf(2.0)).sqrt();
        let inner_corner_x = (inner_centerward_radius.powf(2.0) - inner_y_max.powf(2.0)).sqrt();
        let screw_setback = OUTER_CORNER_FILLET_RADIUS;
        let corner_xy_x = outer_far_x_abs - screw_setback;
        let corner_xy_y = outer_y_max - screw_setback;
        let far_mid_x = outer_far_x_abs - screw_setback;
        let curve_apex_x = outer_centerward_radius + screw_setback;
        let corner_curve_y = outer_y_max - OUTER_CORNER_FILLET_RADIUS;
        let corner_curve_r = outer_centerward_radius + OUTER_CORNER_FILLET_RADIUS;
        let corner_curve_x = (corner_curve_r.powf(2.0) - corner_curve_y.powf(2.0)).sqrt();
        let insert_positions_for_side_plus_1 = [
            [corner_xy_x, corner_xy_y],
            [corner_xy_x, -corner_xy_y],
            [far_mid_x, 0.0],
            [corner_curve_x, corner_curve_y],
            [corner_curve_x, -corner_curve_y],
            [curve_apex_x, 0.0],
        ];
        let far_wall_inner_x = outer_far_x_abs - reservoir_wall_thickness;
        let plus_y_wall_inner_y = outer_y_max - reservoir_wall_thickness;
        let curve_inner_x_at_y0 = outer_centerward_radius + reservoir_wall_thickness;
        let inv_sqrt2 = 1.0 / 2.0f64.sqrt();
        let inner_corner_curve_x =
            (curve_inner_x_at_y0.powf(2.0) - plus_y_wall_inner_y.powf(2.0)).sqrt();
        let dx = inner_corner_curve_x - corner_curve_x;
        let dy = plus_y_wall_inner_y - corner_curve_y;
        let dist = (dx.powf(2.0) + dy.powf(2.0)).sqrt();
        let dir_x = dx / dist;
        let dir_y = dy / dist;
        let pivot_x = corner_curve_x + CORNER_CURVE_PIVOT_DISTANCE * dir_x;
        let pivot_y = corner_curve_y + CORNER_CURVE_PIVOT_DISTANCE * dir_y;
        // A dict literal: a repeated key keeps its first place and takes the later value.
        let mut body_boss_cut_info_for_side_plus_1: Vec<([f64; 2], [f64; 4])> = vec![];
        for (key, info) in [
            (
                [corner_xy_x, corner_xy_y],
                [far_wall_inner_x, plus_y_wall_inner_y, inv_sqrt2, inv_sqrt2],
            ),
            (
                [corner_xy_x, -corner_xy_y],
                [far_wall_inner_x, -plus_y_wall_inner_y, inv_sqrt2, -inv_sqrt2],
            ),
            ([far_mid_x, 0.0], [far_wall_inner_x, 0.0, 1.0, 0.0]),
            ([corner_curve_x, corner_curve_y], [pivot_x, pivot_y, dir_x, dir_y]),
            ([corner_curve_x, -corner_curve_y], [pivot_x, -pivot_y, dir_x, -dir_y]),
            ([curve_apex_x, 0.0], [curve_inner_x_at_y0, 0.0, -1.0, 0.0]),
        ] {
            match body_boss_cut_info_for_side_plus_1
                .iter_mut()
                .find(|(k, _)| *k == key)
            {
                Some(entry) => entry.1 = info,
                None => body_boss_cut_info_for_side_plus_1.push((key, info)),
            }
        }
        Ok(Self {
            here,
            mat,
            fits,
            float,
            float_guide_diameter,
            float_diameter,
            float_bore_diameter,
            float_rod_axis_from_inner_wall,
            float_height,
            bag_pocket_far_inner_x: base.bag_pocket_far_inner_x,
            bag_pocket_y_inner_max: base.bag_pocket_y_inner_max,
            bag_pocket_floor_top_z: base.bag_pocket_floor_top_z,
            bag_pocket_walls_top_z: base.bag_pocket_walls_top_z,
            pocket_centerward_arc_outer_radius: base.pocket_centerward_arc_outer_radius,
            port_hole_radius: base.port_hole_radius,
            reservoir_clearance: base.reservoir_clearance,
            reservoir_floor_thickness: base.reservoir_floor_thickness,
            reservoir_draw_port: base.reservoir_draw_port,
            reservoir_fill_port: base.reservoir_fill_port,
            reservoir_fill_sides: base.reservoir_fill_sides,
            level_rod_y: base.level_rod_y,
            lldpe_tube_od: core.lldpe_tube_od,
            reservoir_wall_thickness,
            cap_base_thickness,
            cap_counterbore_diameter,
            cap_counterbore_depth,
            cap_clearance_hole_diameter,
            cap_perimeter_z_range,
            cap_base_z_range,
            cap_total_height,
            fill_bore_diameter,
            reservoir_count,
            rod_position_y,
            rod_diameter,
            rod_bore,
            rod_boss_od,
            body_boss_radius,
            cap_boss_radius,
            gasket_pad_radius,
            outer_far_x_abs,
            outer_y_max,
            outer_centerward_radius,
            inner_far_x_abs,
            inner_y_max,
            inner_centerward_radius,
            rod_position_x,
            outer_tab_interior_angle,
            inner_corner_interior_angle,
            cap_stack_above_body,
            outer_z_range,
            inner_z_range,
            cap_assembly_lift,
            cap_top_z,
            rod_floor_z,
            reservoir_rod_clearance,
            reservoir_rod_len,
            float_magnet_travel_z,
            float_travel,
            reservoir_reed_pitch,
            reed_span,
            reed_mid,
            reservoir_reed_centres_z,
            dip_tube_mouth_z,
            outer_corner_x,
            inner_corner_x,
            screw_setback,
            corner_xy_x,
            corner_xy_y,
            far_mid_x,
            curve_apex_x,
            corner_curve_y,
            corner_curve_r,
            corner_curve_x,
            insert_positions_for_side_plus_1,
            far_wall_inner_x,
            plus_y_wall_inner_y,
            curve_inner_x_at_y0,
            inv_sqrt2,
            inner_corner_curve_x,
            corner_curve_to_inner_corner_dx: dx,
            corner_curve_to_inner_corner_dy: dy,
            corner_curve_to_inner_corner_dist: dist,
            corner_curve_wall_dir_x: dir_x,
            corner_curve_wall_dir_y: dir_y,
            corner_curve_virtual_pivot_x: pivot_x,
            corner_curve_virtual_pivot_y: pivot_y,
            body_boss_cut_info_for_side_plus_1,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `numbers()`: the figures the kernel's reservoir recipe cuts from.
pub fn numbers(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let linear = rt.pya("_materials", "linear")?;
    let stations: Vec<Val> = s
        .insert_positions_for_side_plus_1
        .iter()
        .map(|xy| {
            Dict::new()
                .with("xy", *xy)
                .with("cut", s.body_boss_cut_info(*xy))
                .val()
        })
        .collect();
    let mut ports = vec![];
    for side in [1, -1] {
        let fill = if s.reservoir_fill_sides.contains(&side) {
            Some(s.reservoir_fill_port.side(side)?)
        } else {
            None
        };
        ports.push(
            Dict::new()
                .with("side", side)
                .with("vent", tube_ports::air_position(side)?)
                .with("fill", fill)
                .with("draw", s.reservoir_draw_port.side(side)?)
                .val(),
        );
    }
    let mut d = Dict::new()
        .with("outer_far_x", s.outer_far_x_abs)
        .with("outer_y", s.outer_y_max)
        .with("outer_radius", s.outer_centerward_radius)
        .with("outer_round", OUTER_CORNER_FILLET_RADIUS)
        .with("inner_round", INNER_CORNER_FILLET_RADIUS)
        .with("wall", s.reservoir_wall_thickness)
        .with("outer_z", s.outer_z_range)
        .with("inner_z", s.inner_z_range)
        .with("insert_stations", stations)
        .with("body_boss_radius", s.body_boss_radius)
        .with("boss_height", BOSS_HEIGHT)
        .with("boss_extra_below", CYL_EXTRA_BELOW_BOTTOM)
        .with("insert_radius", INSERT_POCKET_RADIUS)
        .with("insert_depth", INSERT_POCKET_DEPTH)
        .with("rod_xy", (s.rod_position_x, s.rod_position_y))
        .with("rod_floor", s.rod_floor_z)
        .with("rod_anchor_height", ROD_ANCHOR_BOSS_HEIGHT)
        .with("rod_anchor_floor", ROD_ANCHOR_BOSS_FLOOR)
        .with("rod_register_height", ROD_REGISTER_BOSS_HEIGHT)
        .with("rod_boss_radius", s.rod_boss_od / 2.0)
        .with("rod_bore_radius", s.rod_bore / 2.0)
        .with("cap_wall_height", CAP_WALL_HEIGHT)
        .with("cap_wall_width", CAP_WALL_WIDTH)
        .with("cap_base_thickness", s.cap_base_thickness)
        .with("cap_height", s.cap_total_height)
        .with("cap_boss_radius", s.cap_boss_radius)
        .with("clearance_radius", s.cap_clearance_hole_diameter / 2.0)
        .with("counterbore_radius", s.cap_counterbore_diameter / 2.0)
        .with("counterbore_depth", s.cap_counterbore_depth)
        .with("gasket_thickness", GASKET_THICKNESS)
        .with("gasket_strip_width", GASKET_STRIP_WIDTH)
        .with("gasket_pad_radius", s.gasket_pad_radius)
        .with("plate_thickness", tube_ports::PLATE_THICKNESS)
        .with("liquid_grip", tube_ports::LIQUID_GRIP.val())
        .with("air_grip", tube_ports::AIR_GRIP.val())
        .with("ports", ports)
        .with(
            "reed_window",
            (
                fmin(s.reservoir_reed_centres_z),
                fmax(s.reservoir_reed_centres_z),
            ),
        );
    let colors = [
        ("body", s.mat.a("C_RESERVOIR")?),
        ("cap", s.mat.a("C_RES_CAP")?),
        ("gasket", s.mat.a("C_SILICONE")?),
        ("grip", s.mat.a("M_TPU_BLACK")?),
    ];
    for (name, color) in colors {
        d.set(
            format!("color_{name}"),
            Val::list(linear.c(vec![color])?.list()?),
        );
    }
    Ok(d.val())
}

/// `document(capacity_l, window_l)`: fills the reservoir documents and this file's comments.
pub fn document(rt: &Runtime, capacity_l: &Val, window_l: &Val) -> Result<()> {
    let s = state(rt)?;
    let core = core::state(rt)?;
    let g = |x: f64| ff(x, ".4g");
    let mm = |x: f64| format!("{} mm", ff(x, ".4g"));
    let pair = |[x, y]: [f64; 2]| format!("({}, {})", ff(x, ".4g"), ff(y, ".4g"));
    let [travel_low, travel_high] = s.float_magnet_travel_z;
    let reed_centres: Vec<String> = s
        .reservoir_reed_centres_z
        .iter()
        .map(|z| ff(*z, ".2f"))
        .collect();
    let mut conduits = vec![];
    for name in REED_CONDUITS {
        let [x, y] = core.cap_conduit_shell_xy(name)?;
        conduits.push(format!("{name} ({}, {})", g(x), g(y)));
    }
    let variables: Vec<(String, String)> = [
        ("FILL_BORE_D", mm(s.fill_bore_diameter)),
        ("CONDUIT_BORE_D", mm(s.port_hole_radius * 2.0)),
        ("FILL_POSITION_A", pair(s.reservoir_fill_port.side(1)?)),
        ("FILL_POSITION_B", pair(s.reservoir_fill_port.side(-1)?)),
        ("ROD_DIAMETER", mm(s.rod_diameter)),
        ("ROD_POSITION_X", ff(s.rod_position_x, ".2f")),
        ("CAVITY_FAR_WALL_X", ff(s.inner_far_x_abs, ".2f")),
        (
            "ROD_WALL_DISTANCE",
            format!("{} mm", fv(&s.float_rod_axis_from_inner_wall, "g")?),
        ),
        ("FLOAT_DIAMETER", format!("{} mm", fv(&s.float_diameter, "g")?)),
        ("FLOAT_HEIGHT", format!("{} mm", fv(&s.float_height, "g")?)),
        (
            "FLOAT_TRAVEL",
            format!("{}–{} mm", ff(travel_low, ".2f"), ff(travel_high, ".2f")),
        ),
        ("REED_CENTRES", reed_centres.join(", ")),
        ("ROD_POSITION_Y", g(s.rod_position_y)),
        ("REEDS_PER_RES", fi(REEDS_PER_RESERVOIR, ".4g")),
        (
            "RESERVOIR_ROD_LEN",
            format!(
                "{} mm ({} in)",
                g(s.reservoir_rod_len),
                ff(s.reservoir_rod_len / 25.4, ".3g")
            ),
        ),
        (
            "RESERVOIR_SEAT_TO_SEAT",
            mm(s.reservoir_rod_len + s.reservoir_rod_clearance),
        ),
        (
            "ROD_END_CLEARANCE",
            format!("{} mm", ff(s.reservoir_rod_clearance, "g")),
        ),
        ("REED_PITCH", format!("{} mm", ff(s.reservoir_reed_pitch, "g"))),
        ("REED_CONDUIT_XY", conduits.join(", ")),
        ("DRAW_POSITION_A", pair(s.reservoir_draw_port.side(1)?)),
        ("DRAW_POSITION_B", pair(s.reservoir_draw_port.side(-1)?)),
        ("FLOOR_Z", mm(s.rod_floor_z)),
        ("RESERVOIR_CAPACITY", format!("{} L", fv(capacity_l, ".2f")?)),
        ("RESERVOIR_WINDOW", format!("{} L", fv(window_l, ".2f")?)),
        ("RESERVOIR_WALL_T", mm(s.reservoir_wall_thickness)),
        ("CAP_TOTAL_H", mm(s.cap_total_height)),
        ("ROD_BORE", mm(s.rod_bore)),
        ("ROD_BOSS_OD", mm(s.rod_boss_od)),
        ("BODY_BOSS_R", mm(s.body_boss_radius)),
        ("BODY_BOSS_D", mm(2.0 * s.body_boss_radius)),
        ("CAP_BOSS_R", mm(s.cap_boss_radius)),
        ("CAP_STACK_H", mm(s.cap_stack_above_body)),
        ("CAP_ASSEMBLY_LIFT", mm(s.cap_assembly_lift)),
        ("CAP_TOP_Z", mm(s.cap_top_z)),
        ("OUTER_Y_MAX", mm(s.outer_y_max)),
        ("OUTER_CENTERWARD_R", mm(s.outer_centerward_radius)),
        ("INNER_Y_MAX", mm(s.inner_y_max)),
        (
            "OUTER_TAB_ANGLE",
            format!("{}°", ff(s.outer_tab_interior_angle, ".0f")),
        ),
        (
            "INNER_CORNER_ANGLE",
            format!("{}°", ff(s.inner_corner_interior_angle, ".0f")),
        ),
        ("CAP_COUNTERBORE_D", mm(s.cap_counterbore_diameter)),
        ("CAP_CLEARANCE_HOLE_D", mm(s.cap_clearance_hole_diameter)),
        ("GASKET_STRIP_W", mm(GASKET_STRIP_WIDTH)),
        ("GASKET_THICKNESS", mm(GASKET_THICKNESS)),
        ("RESERVOIR_CLEARANCE", mm(s.reservoir_clearance)),
        ("INSERT_POCKET_DEPTH", mm(INSERT_POCKET_DEPTH)),
        ("OUTER_FILLET_R", mm(OUTER_CORNER_FILLET_RADIUS)),
        ("CORNER_XY_Y", g(s.corner_xy_y)),
        ("INNER_CORNER_CURVE_X", mm(s.inner_corner_curve_x)),
        ("CORNER_CURVE_DIST", mm(s.corner_curve_to_inner_corner_dist)),
        ("GASKET_PAD_D", format!("ø{}", g(2.0 * s.gasket_pad_radius))),
    ]
    .into_iter()
    .map(|(k, v)| (k.to_owned(), v))
    .collect();
    for name in DOCUMENTS {
        rt.substitute_md(&s.here.join(name), &variables, Some(NAME))?;
        rt.print(format!("-> {name}"))?;
    }
    let file = rt.file(NAME);
    rt.substitute_py_comments(&file, &variables, Some(NAME))?;
    let name = file.file_name().map(|n| n.to_string_lossy().into_owned());
    rt.print(format!("-> {} (self)", name.unwrap_or_default()))
}

/// The Python `main(output=_here)`: cuts the reservoir on the kernel, writes the printed
/// pieces' payloads and fills the documents.
pub fn write(rt: &Runtime, output: &Path) -> Result<()> {
    let rust_part = rt.py("_rust_part")?;
    let write_print_payload = rt.pya("flute_payload", "cut")?;
    std::fs::create_dir_all(output)?;
    let output = output.to_path_buf();
    let readings = rust_part
        .m(
            "cut",
            args!["cold-core", "reservoir", numbers(rt)?, output.clone()],
        )?
        .k("bodies")?
        .i(0)?;
    let capacity_l = readings.k("capacity_l")?;
    let window_l = readings.k("reed_window_l")?;
    for name in PRINTED {
        write_print_payload.ck(
            args![
                output.join(format!("{name}.step")),
                output.join(format!("{name}.stl"))
            ],
            kw!["preserve_print_triangles" => true],
        )?;
    }
    rt.print(format!(
        "   capacity {} L floor to rim; {} L between the end reeds",
        fv(&capacity_l, ".3f")?,
        fv(&window_l, ".3f")?
    ))?;
    document(rt, &capacity_l, &window_l)
}

/// The variables a docgen call passes, as `str()` of each value.
fn substitution(c: &mut Call) -> Result<(PathBuf, Vec<(String, String)>)> {
    let path = PathBuf::from(c.req::<Val>(0, "path")?.str()?);
    let variables: Val = c.req(1, "variables")?;
    let mut values = vec![];
    for key in variables.iter()? {
        values.push((key.str()?, variables.get(key)?.str()?));
    }
    Ok((path, values))
}

/// The native `substitute_md(path, variables)` this module imported from docgen.
fn substitute_md(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let (path, values) = substitution(c)?;
    rt.substitute_md(&path, &values, Some(NAME))?;
    Ok(Val::None)
}

/// The native `substitute_py_comments(path, variables)` this module imported from docgen.
fn substitute_py_comments(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let (path, values) = substitution(c)?;
    rt.substitute_py_comments(&path, &values, Some(NAME))?;
    Ok(Val::None)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "argparse", "argparse")?;
    ns.module(rt, "math", "math")?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", s.here.clone());
    ns.value("_mat", s.mat.clone());
    ns.value("fits", s.fits.clone());
    ns.module(rt, "tube_ports", tube_ports::NAME)?;
    ns.func(rt, "substitute_md", substitute_md);
    ns.func(rt, "substitute_py_comments", substitute_py_comments);
    ns.func(rt, "cap_conduit_shell_xy", |rt, c| {
        Ok(core::state(rt)?
            .cap_conduit_shell_xy(&c.req::<String>(0, "name")?)?
            .to_val())
    });
    ns.value("bag_pocket_far_inner_x", s.bag_pocket_far_inner_x);
    ns.value("bag_pocket_y_inner_max", s.bag_pocket_y_inner_max);
    ns.value("bag_pocket_floor_top_z", s.bag_pocket_floor_top_z);
    ns.value("bag_pocket_walls_top_z", s.bag_pocket_walls_top_z);
    ns.value(
        "pocket_centerward_arc_outer_radius",
        s.pocket_centerward_arc_outer_radius,
    );
    ns.value("port_hole_radius", s.port_hole_radius);
    ns.value("reservoir_clearance", s.reservoir_clearance);
    ns.value("reservoir_floor_thickness", s.reservoir_floor_thickness);
    ns.value("reservoir_draw_port", s.reservoir_draw_port);
    ns.value("reservoir_fill_port", s.reservoir_fill_port);
    ns.value("reservoir_fill_sides", s.reservoir_fill_sides);
    ns.value("level_rod_y", s.level_rod_y);
    ns.value("lldpe_tube_od", s.lldpe_tube_od);
    ns.value("reeds_per_reservoir", REEDS_PER_RESERVOIR);
    ns.value("_float", s.float.clone());
    ns.value("reservoir_wall_thickness", s.reservoir_wall_thickness);
    ns.value("outer_corner_fillet_radius", OUTER_CORNER_FILLET_RADIUS);
    ns.value("inner_corner_fillet_radius", INNER_CORNER_FILLET_RADIUS);
    ns.value("cap_base_thickness", s.cap_base_thickness);
    ns.value("cap_wall_height", CAP_WALL_HEIGHT);
    ns.value("cap_wall_width", CAP_WALL_WIDTH);
    ns.value("cap_counterbore_diameter", s.cap_counterbore_diameter);
    ns.value("cap_counterbore_depth", s.cap_counterbore_depth);
    ns.value("cap_clearance_hole_diameter", s.cap_clearance_hole_diameter);
    ns.value("gasket_thickness", GASKET_THICKNESS);
    ns.value("gasket_strip_width", GASKET_STRIP_WIDTH);
    ns.value("cap_perimeter_z_range", s.cap_perimeter_z_range);
    ns.value("cap_base_z_range", s.cap_base_z_range);
    ns.value("cap_total_height", s.cap_total_height);
    ns.value("fill_position", s.reservoir_fill_port);
    ns.value("draw_position", s.reservoir_draw_port);
    ns.value("vent_position", tube_ports::air_position_val());
    ns.value("fill_bore_diameter", s.fill_bore_diameter);
    ns.value("reservoir_count", s.reservoir_count);
    ns.value("rod_position_y", s.rod_position_y);
    ns.value("rod_diameter", s.float_guide_diameter.clone());
    ns.value("rod_bore", s.rod_bore);
    ns.value("rod_boss_od", s.rod_boss_od);
    ns.value("rod_register_boss_height", ROD_REGISTER_BOSS_HEIGHT);
    ns.value("rod_anchor_boss_height", ROD_ANCHOR_BOSS_HEIGHT);
    ns.value("rod_anchor_boss_floor", ROD_ANCHOR_BOSS_FLOOR);
    ns.value("insert_pocket_radius", INSERT_POCKET_RADIUS);
    ns.value("insert_pocket_depth", INSERT_POCKET_DEPTH);
    ns.value("boss_annulus", BOSS_ANNULUS);
    ns.value("body_boss_radius", s.body_boss_radius);
    ns.value("cap_boss_radius", s.cap_boss_radius);
    ns.value("gasket_pad_radius", s.gasket_pad_radius);
    ns.value("boss_height", BOSS_HEIGHT);
    ns.value("_cyl_extra_below_bottom", CYL_EXTRA_BELOW_BOTTOM);
    ns.value("outer_far_x_abs", s.outer_far_x_abs);
    ns.value("outer_y_max", s.outer_y_max);
    ns.value("outer_centerward_radius", s.outer_centerward_radius);
    ns.value("inner_far_x_abs", s.inner_far_x_abs);
    ns.value("inner_y_max", s.inner_y_max);
    ns.value("inner_centerward_radius", s.inner_centerward_radius);
    ns.value("float_capsule_od", s.float_diameter.clone());
    ns.value("float_capsule_bore", s.float_bore_diameter.clone());
    ns.value("rod_position_x", s.rod_position_x);
    ns.value("outer_tab_interior_angle", s.outer_tab_interior_angle);
    ns.value("inner_corner_interior_angle", s.inner_corner_interior_angle);
    ns.value("cap_stack_above_body", s.cap_stack_above_body);
    ns.value("outer_z_range", s.outer_z_range);
    ns.value("inner_z_range", s.inner_z_range);
    ns.value("cap_assembly_lift", s.cap_assembly_lift);
    ns.value("cap_top_z", s.cap_top_z);
    ns.value("rod_floor_z", s.rod_floor_z);
    ns.value("reservoir_rod_clearance", s.reservoir_rod_clearance);
    ns.value("reservoir_rod_len", s.reservoir_rod_len);
    ns.value("float_magnet_travel_z", s.float_magnet_travel_z);
    ns.value("_float_travel", s.float_travel);
    ns.value("reservoir_reed_pitch", s.reservoir_reed_pitch);
    ns.value("_reed_span", s.reed_span);
    ns.value("_reed_mid", s.reed_mid);
    ns.value("reservoir_reed_centres_z", s.reservoir_reed_centres_z);
    ns.value("dip_tube_mouth_z", s.dip_tube_mouth_z);
    ns.value("outer_corner_x", s.outer_corner_x);
    ns.value("inner_corner_x", s.inner_corner_x);
    ns.value("_screw_setback", s.screw_setback);
    ns.value("_corner_xy_x", s.corner_xy_x);
    ns.value("_corner_xy_y", s.corner_xy_y);
    ns.value("_far_mid_x", s.far_mid_x);
    ns.value("_curve_apex_x", s.curve_apex_x);
    ns.value("_corner_curve_y", s.corner_curve_y);
    ns.value("_corner_curve_r", s.corner_curve_r);
    ns.value("_corner_curve_x", s.corner_curve_x);
    ns.value(
        "insert_positions_for_side_plus_1",
        s.insert_positions_for_side_plus_1.to_vec(),
    );
    ns.value("_far_wall_inner_x", s.far_wall_inner_x);
    ns.value("_plus_y_wall_inner_y", s.plus_y_wall_inner_y);
    ns.value("_curve_inner_x_at_y0", s.curve_inner_x_at_y0);
    ns.value("_inv_sqrt2", s.inv_sqrt2);
    ns.value("_inner_corner_curve_x", s.inner_corner_curve_x);
    ns.value(
        "_corner_curve_to_inner_corner_dx",
        s.corner_curve_to_inner_corner_dx,
    );
    ns.value(
        "_corner_curve_to_inner_corner_dy",
        s.corner_curve_to_inner_corner_dy,
    );
    ns.value(
        "_corner_curve_to_inner_corner_dist",
        s.corner_curve_to_inner_corner_dist,
    );
    ns.value("_corner_curve_wall_dir_x", s.corner_curve_wall_dir_x);
    ns.value("_corner_curve_wall_dir_y", s.corner_curve_wall_dir_y);
    ns.value("_corner_curve_pivot_distance", CORNER_CURVE_PIVOT_DISTANCE);
    ns.value("_corner_curve_virtual_pivot_x", s.corner_curve_virtual_pivot_x);
    ns.value("_corner_curve_virtual_pivot_y", s.corner_curve_virtual_pivot_y);
    let mut cut_info = Dict::new();
    for (key, info) in &s.body_boss_cut_info_for_side_plus_1 {
        cut_info.set(*key, *info);
    }
    ns.value("body_boss_cut_info_for_side_plus_1", cut_info.val());
    ns.func(rt, "numbers", |rt, _| numbers(rt));
    ns.func(rt, "document", |rt, c| {
        let capacity_l: Val = c.req(0, "capacity_l")?;
        let window_l: Val = c.req(1, "window_l")?;
        document(rt, &capacity_l, &window_l)?;
        Ok(Val::None)
    });
    ns.func(rt, "main", |rt, c| {
        let output: PathBuf = c.opt(0, "output", state(rt)?.here.clone())?;
        write(rt, &output)?;
        Ok(Val::None)
    });
    Ok(())
}

/// The `__main__` block: `--output` names the directory the pieces go to.
pub fn main(rt: &Runtime) -> Result<()> {
    rt.py("_rust_part")?.m("start", vec![])?;
    let s = state(rt)?;
    let description = super::table::documentation(NAME).map_or(Val::None, Val::from);
    let parser = rt
        .py("argparse")?
        .mk("ArgumentParser", vec![], kw!["description" => description])?;
    let path = rt.import_module("pathlib")?.a("Path")?;
    parser.mk(
        "add_argument",
        args!["--output"],
        kw!["type" => path, "default" => s.here.clone()],
    )?;
    let args = parser.m("parse_args", vec![])?;
    write(rt, &PathBuf::from_val(&args.a("output")?)?)
}
