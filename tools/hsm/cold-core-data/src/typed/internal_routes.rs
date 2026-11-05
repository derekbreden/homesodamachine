//! `_internal_routes`: the lines inside the cold core, each drawn from its fitting to the
//! mouth it leaves by as a swept tube on its own centreline, with the corner arcs the stock
//! bends to and the readings that show no line meets a solid or another line.

use super::above_core::AboveCore;
use super::above_core_mounts as mounts;
use super::cad::Cq;
use super::cold_core_interface as core;
use super::foam_cap_parts as foam_cap;
use super::*;

pub const NAME: &str = "_internal_routes";

/// The names `from _cold_core_interface import ...` binds, in the statement's order.
const INTERFACE_NAMES: &[&str] = &[
    "cap_conduit_shell_xy",
    "cap_conduit_floor_xy",
    "cap_passive_guides",
    "cap_shell_clearance",
    "co2_inlet_y",
    "foam_shell_outer_height",
    "hole_shift_from_edge",
    "lldpe_bend_radius",
    "lldpe_tube_od",
    "port_hole_radius",
    "outer_shell_y_length",
    "port_lane_mid_y",
    "carbonator_coil_envelope_radius",
    "carbonator_outer_radius",
    "evap_tail_high_z",
    "evap_tail_low_z",
    "carbonator_support_ring_height",
    "carbonator_top_plate_z",
    "carbonator_port_offset",
    "wall_and_floor_thickness",
    "pocket_centerward_arc_outer_radius",
    "water_outlet_upper_climb_x",
    "water_outlet_drift_z",
    "west_lane_mid_y",
];

/// A route's centreline points, as `routes` keeps them.
pub type Points = Vec<[f64; 3]>;

pub struct State {
    here: PathBuf,
    cq: Val,
    co2_inlet_lane_xyz: Val,
    co2_inlet_xyz: Val,
    front_face_port_z: Val,
    water_outlet_ring_crossing_x: Val,
    reservoir: Val,
    shroud: Val,
    stock_min: Val,
    stock_of: Val,
    pub carbonator_outer_radius: Val,
    coil_envelope_radius: f64,
    pocket_arc_outer_radius: f64,
    wall_and_floor: f64,
    foam_shell_outer_height: f64,
    top_cap_height: f64,
    cap_shell_clearance: f64,
    carbonator_port_offset: f64,
    water_outlet_upper_climb_x: f64,
    water_outlet_drift_z: (f64, f64),
    evap_tail_low_z: f64,
    evap_tail_high_z: f64,
    pub port_hole_radius: f64,
    pub lldpe_tube_od: f64,
    pub line_radius: f64,
    pub line_hug: f64,
    pub route_bend_radius_val: Val,
    pub route_bend_radius: f64,
    pub route_stock: Val,
    pub dip_tube_z: Num,
    pub plate_storey_z: f64,
    pub top_band_z: f64,
    pub shell_top_z: f64,
    pub conduit_mouth_z: f64,
    pub lane_step_top_z: f64,
    pub reservoir_cap_z: Num,
    pub reservoir_cap_top_z: Num,
    pub prv_vent_lane_y: f64,
    pub prv_vent_start: [f64; 3],
    pub prv_vent_flank_y: f64,
    pub prv_vent_fall_margin: f64,
    pub prv_vent_cross_z: f64,
    pub prv_vent_reach: f64,
    pub carbonator_envelope_z_range: (f64, f64),
    pub routes: OMap<Points>,
    pub bend_floor: f64,
    pub bend_ladder: Vec<f64>,
    pub touch_volume: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let cq = rt.py("cadquery")?;
        let here = resolve(&rt.file(NAME));
        let dir = here.parent().context("module directory")?.to_owned();
        rt.sys_path_insert(0, &dir)?;
        rt.sys_path_insert(0, &dir.join("reservoir"))?;
        rt.sys_path_insert(0, &dir.join("prv-shroud"))?;
        rt.sys_path_insert(0, &parent_n(&here, 2).join("scripts"))?;
        let core = core::state(rt)?;
        let cap = foam_cap::state(rt)?;
        mounts::state(rt)?;
        let port_cuts = rt.import_module("_port_cuts")?; // via namespace: _port_cuts
        let co2_inlet_lane_xyz = port_cuts.a("co2_inlet_lane_xyz")?; // via namespace: _port_cuts
        let co2_inlet_xyz = port_cuts.a("co2_inlet_xyz")?; // via namespace: _port_cuts
        let front_face_port_z = port_cuts.a("front_face_port_z")?; // via namespace: _port_cuts
        let water_outlet_ring_crossing_x = port_cuts.a("water_outlet_ring_crossing_x")?; // via namespace: _port_cuts
        let reservoir = rt.import_module("reservoir")?; // via namespace: reservoir
        let shroud = rt.import_module("prv_shroud")?; // via namespace: prv_shroud
        let stock_min = rt.pya("_routing", "stock_min")?;
        let stock_of = rt.pya("_routing", "stock_of")?;
        let carbonator_outer_radius = rt.pya("_carbonator_stock", "carbonator_outer_radius")?;
        let b = &core.base;
        let lldpe_tube_od = core.lldpe_tube_od;
        let line_radius = lldpe_tube_od / 2.0;
        let line_hug = 2.0;
        let route_bend_radius_val = stock_min.c(args!["fluid", lldpe_tube_od])?;
        let route_bend_radius = route_bend_radius_val.f()?;
        let route_stock = stock_of.c(args!["fluid", lldpe_tube_od])?;
        let dip_tube_z = Num::from_val(&reservoir.a("dip_tube_mouth_z")?)?; // via namespace: reservoir
        let plate_storey_z = front_face_port_z.f()?;
        let top_band_z = core.carbonator_top_plate_z + b.hole_shift_from_edge;
        let shell_top_z = b.foam_shell_outer_height;
        let conduit_mouth_z = cap.cap_face_z;
        let lane_step_top_z = shell_top_z - route_bend_radius;
        let reservoir_cap_z = Num::from_val(&reservoir.a("cap_assembly_lift")?)?; // via namespace: reservoir
        let reservoir_cap_top_z =
            reservoir_cap_z.add(Num::from_val(&reservoir.a("cap_total_height")?)?); // via namespace: reservoir
        let prv_vent_lane_y = b.west_lane_mid_y;
        let prv_vent_start = [
            0.0,
            prv_vent_lane_y,
            core.carbonator_top_plate_z + b.hole_shift_from_edge
                - shroud.a("outer_diameter")?.f()? / 2.0, // via namespace: prv_shroud
        ];
        let prv_vent_flank_y = b.outer_shell_y_length / 2.0;
        let prv_vent_fall_margin = 2.0;
        let prv_vent_cross_z = prv_vent_start[2] - (route_bend_radius + prv_vent_fall_margin);
        let prv_vent_reach = route_bend_radius - (prv_vent_flank_y - prv_vent_lane_y) + 1.0;
        let carbonator_envelope_z_range = (
            b.wall_and_floor_thickness + b.carbonator_support_ring_height,
            core.carbonator_top_plate_z,
        );
        let mut s = Self {
            here,
            cq,
            co2_inlet_lane_xyz,
            co2_inlet_xyz,
            front_face_port_z,
            water_outlet_ring_crossing_x,
            reservoir,
            shroud,
            stock_min,
            stock_of,
            carbonator_outer_radius,
            coil_envelope_radius: b.carbonator_coil_envelope_radius,
            pocket_arc_outer_radius: b.pocket_centerward_arc_outer_radius,
            wall_and_floor: b.wall_and_floor_thickness,
            foam_shell_outer_height: b.foam_shell_outer_height,
            top_cap_height: cap.top_cap_height,
            cap_shell_clearance: b.cap_shell_clearance,
            carbonator_port_offset: b.carbonator_port_offset,
            water_outlet_upper_climb_x: core.water_outlet_upper_climb_x,
            water_outlet_drift_z: core.water_outlet_drift_z,
            evap_tail_low_z: b.evap_tail_low_z,
            evap_tail_high_z: b.evap_tail_high_z,
            port_hole_radius: b.port_hole_radius,
            lldpe_tube_od,
            line_radius,
            line_hug,
            route_bend_radius_val,
            route_bend_radius,
            route_stock,
            dip_tube_z,
            plate_storey_z,
            top_band_z,
            shell_top_z,
            conduit_mouth_z,
            lane_step_top_z,
            reservoir_cap_z,
            reservoir_cap_top_z,
            prv_vent_lane_y,
            prv_vent_start,
            prv_vent_flank_y,
            prv_vent_fall_margin,
            prv_vent_cross_z,
            prv_vent_reach,
            carbonator_envelope_z_range,
            routes: OMap::new(),
            bend_floor: 0.0,
            bend_ladder: vec![],
            touch_volume: 0.0,
        };
        s.routes = routes_of(rt, &s)?;
        s.bend_floor = 0.5 * lldpe_tube_od;
        s.bend_ladder = (0..24).map(|k| 0.85f64.powf(k as f64)).collect();
        s.touch_volume = 0.1;
        Ok(s)
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `math.sqrt`, `math.acos` and `math.asin` as the runtime evaluates them: a domain error
/// raises.
fn sqrt(x: f64) -> Result<f64> {
    ensure!(x >= 0.0, "math domain error");
    Ok(x.sqrt())
}
fn acos(x: f64) -> Result<f64> {
    let y = x.acos();
    ensure!(y.is_finite(), "math domain error");
    Ok(y)
}
fn asin(x: f64) -> Result<f64> {
    let y = x.asin();
    ensure!(y.is_finite(), "math domain error");
    Ok(y)
}
/// `a / b`, raising on a zero divisor as the runtime does.
fn div(a: f64, b: f64) -> Result<f64> {
    ensure!(b != 0.0, "division by zero");
    Ok(a / b)
}
/// `max(-1.0, min(1.0, x))`.
fn clamp_unit(x: f64) -> f64 {
    pmax(-1.0, pmin(1.0, x))
}

fn coil_standoff_y_of(s: &State, x: f64) -> Result<f64> {
    let clear = s.coil_envelope_radius + s.line_radius + s.line_hug;
    let reach = clear.powf(2.0) - x.powf(2.0);
    Ok(if reach > 0.0 { -sqrt(reach)? } else { 0.0 })
}

fn annulus_y_of(s: &State, x: f64) -> Result<f64> {
    let mid = (s.coil_envelope_radius + s.pocket_arc_outer_radius - s.wall_and_floor) / 2.0;
    let reach = mid.powf(2.0) - x.powf(2.0);
    Ok(if reach > 0.0 { -sqrt(reach)? } else { 0.0 })
}

fn co2_run_y_of(s: &State, x: f64) -> Result<Option<f64>> {
    let [x0, y0, _z0] = s.co2_inlet_lane_xyz.v3()?;
    let [x1, y1, _z1] = s.co2_inlet_xyz.v3()?;
    if !(pmin(x0, x1) - 1e-09 <= x && x <= pmax(x0, x1) + 1e-09) {
        return Ok(None);
    }
    Ok(Some(y0 + div((y1 - y0) * (x - x0), x1 - x0)?))
}

fn world_point_in_shell_of(rt: &Runtime, s: &State, point: &Val) -> Result<[f64; 3]> {
    let [x, y, z] = AboveCore::get(rt)?.world_to_cap(point)?;
    Ok([-x, -y, z + s.foam_shell_outer_height + s.top_cap_height])
}

fn reservoir_guide_route_of(rt: &Runtime, s: &State, name: &str, start_z: f64) -> Result<Points> {
    let core = core::state(rt)?;
    let [fx, fy] = core.cap_conduit_floor_xy(name)?;
    Ok(mounts::passive_guide_points(
        [-fx, -fy],
        core.cap_conduit_shell_xy(name)?,
        start_z,
        s.conduit_mouth_z,
        s.foam_shell_outer_height + s.cap_shell_clearance + s.wall_and_floor + 0.25,
        s.route_bend_radius,
    ))
}

/// The first two members of a Python point with `z` after them: `(*point[:2], z)`.
fn lifted(point: &Val, z: f64) -> Result<Val> {
    let items = point.list()?;
    let mut row: Vec<Val> = items.into_iter().take(2).collect();
    row.push(Val::Float(z));
    Ok(Val::Tuple(row))
}

/// `_routes()`: every line's centreline, keyed by line.
fn routes_of(rt: &Runtime, s: &State) -> Result<OMap<Points>> {
    let core = core::state(rt)?;
    let spec = AboveCore::get(rt)?.spec().clone();
    let r = s.route_bend_radius;
    let carb_x = s.water_outlet_ring_crossing_x.f()?;
    let carb_riser_y = annulus_y_of(s, carb_x)?;
    let carb_upper_x = s.water_outlet_upper_climb_x;
    let carb_upper_y = coil_standoff_y_of(s, carb_upper_x)?;
    let carb_mid_x = (carb_x + carb_upper_x) / 2.0;
    let gas_guide = spec.k("gas_guide_world_mm")?;
    let gas_lower_xy = [75.0, 371.8];
    let gas_items = gas_guide.list()?;
    let gas_head: Vec<f64> = gas_items
        .iter()
        .take(2)
        .map(Val::num)
        .collect::<Result<_>>()?;
    ensure!(gas_head.len() == gas_lower_xy.len(), "distance dimensions");
    let gas_shift = dist(&gas_head, &gas_lower_xy);
    let gas_theta = acos(1.0 - gas_shift / (2.0 * r))?;
    let gas_setback = r * (gas_theta / 2.0).tan();
    let gas_drop = 2.0 * r * gas_theta.sin();
    let gas_turn_z = 230.4;
    let water_guide = spec.k("cap_guides_world_mm")?.k("water-in")?;
    let water_theta =
        std::f64::consts::PI / 4.0 + asin((14.9 / r - 1.0) / sqrt(2.0)?)?;
    let water_setback = r * (water_theta / 2.0).tan();
    let water_turn_start = -70.5 + r * (water_theta.sin() + water_theta.cos());
    let water_lane_x = -78.5;
    let water_return_y = 363.0;
    let water_return_theta = acos(1.0 - (water_lane_x + 70.5f64).abs() / (2.0 * r))?;
    let water_return_setback = r * (water_return_theta / 2.0).tan();
    let water_return_run = 2.0 * r * water_return_theta.sin();
    let co2_under_tank_y = co2_run_y_of(s, carb_x)?;
    let carb_co2_rise = match co2_under_tank_y {
        None => 0.0,
        Some(under) => {
            (s.lldpe_tube_od + s.line_hug)
                * div(
                    s.carbonator_port_offset - carb_riser_y,
                    s.carbonator_port_offset - under,
                )?
        }
    };
    let in_shell = |points: Vec<Val>| -> Result<Points> {
        points
            .iter()
            .map(|p| world_point_in_shell_of(rt, s, p))
            .collect()
    };
    let mut routes = OMap::new();
    let mut water_in = vec![[0.0, -s.carbonator_port_offset, s.top_band_z]];
    water_in.extend(in_shell(vec![
        [-20.0, 283.0, 219.4].to_val(),
        [water_turn_start - water_setback, 283.0, 219.4].to_val(),
        [-70.5, 283.0, 204.5].to_val(),
        [-70.5, water_return_y + water_return_setback, 204.5].to_val(),
        [
            water_lane_x,
            water_return_y + water_return_run - water_return_setback,
            204.5,
        ]
        .to_val(),
        [water_lane_x, 385.0, 204.5].to_val(),
        lifted(&water_guide, 204.5)?,
        water_guide.clone(),
    ])?);
    routes.set("water-in", water_in);
    let [ax, ay] = core.cap_conduit_shell_xy("reservoir-a")?;
    let [bx, by] = core.cap_conduit_shell_xy("reservoir-a")?;
    routes.set(
        "reservoir-a",
        vec![[ax, ay, s.dip_tube_z.f()], [bx, by, s.conduit_mouth_z]],
    );
    routes.set(
        "reservoir-b",
        reservoir_guide_route_of(rt, s, "reservoir-b", s.dip_tube_z.f())?,
    );
    let mut co2_in = in_shell(vec![
        gas_guide.clone(),
        lifted(&gas_guide, gas_turn_z - gas_setback)?,
        [
            gas_lower_xy[0],
            gas_lower_xy[1],
            gas_turn_z - gas_drop + gas_setback,
        ]
        .to_val(),
    ])?;
    co2_in.push(s.co2_inlet_lane_xyz.v3()?);
    co2_in.push(s.co2_inlet_xyz.v3()?);
    routes.set("co2-in", co2_in);
    let (drift_low, drift_high) = s.water_outlet_drift_z;
    let [ox, oy] = core.cap_conduit_shell_xy("carb-water-out")?;
    let [mx, my] = core.cap_conduit_shell_xy("carb-water-out")?;
    routes.set(
        "carb-water-out",
        vec![
            [0.0, s.carbonator_port_offset, s.plate_storey_z],
            [carb_x, s.carbonator_port_offset, s.plate_storey_z],
            [carb_x, carb_riser_y, s.plate_storey_z + carb_co2_rise],
            [carb_x, carb_riser_y, drift_low],
            [
                carb_mid_x,
                coil_standoff_y_of(s, carb_mid_x)?,
                fsum([drift_low, drift_high]) / 2.0,
            ],
            [carb_upper_x, carb_upper_y, drift_high],
            [carb_upper_x, carb_upper_y, s.top_band_z],
            [ox, oy, s.top_band_z],
            [mx, my, s.conduit_mouth_z],
        ],
    );
    routes.set(
        "prv-vent",
        vec![
            s.prv_vent_start,
            [s.prv_vent_start[0], s.prv_vent_lane_y, s.prv_vent_cross_z],
            [
                s.prv_vent_start[0],
                s.prv_vent_flank_y + s.prv_vent_reach,
                s.prv_vent_cross_z,
            ],
        ],
    );
    let cap_wall_height = s.reservoir.a("cap_wall_height")?.f()?; // via namespace: reservoir
    routes.set(
        "reservoir-a-fill",
        reservoir_guide_route_of(
            rt,
            s,
            "reservoir-a-fill",
            s.reservoir_cap_z.f() + cap_wall_height - 1.0,
        )?,
    );
    let passage = mounts::reservoir_b_fill_passage(rt)?;
    routes.set(
        "reservoir-b-fill",
        in_shell(passage.k("route_points_world_mm")?.list()?)?,
    );
    Ok(routes)
}

/// `coil_standoff_y(x)`: the y a line hugging the evaporator coil's envelope runs at.
pub fn coil_standoff_y(rt: &Runtime, x: f64) -> Result<f64> {
    coil_standoff_y_of(&*state(rt)?, x)
}

/// `annulus_y(x)`: the y midway across the annulus between the coil and the pocket arc.
pub fn annulus_y(rt: &Runtime, x: f64) -> Result<f64> {
    annulus_y_of(&*state(rt)?, x)
}

/// `co2_run_y(x)`: the CO2 inlet run's y at `x`, or `None` off the run.
pub fn co2_run_y(rt: &Runtime, x: f64) -> Result<Option<f64>> {
    co2_run_y_of(&*state(rt)?, x)
}

/// `world_point_in_shell(point)`: a world point in the shell's own frame.
pub fn world_point_in_shell(rt: &Runtime, point: &Val) -> Result<[f64; 3]> {
    world_point_in_shell_of(rt, &*state(rt)?, point)
}

/// `reservoir_guide_route(name, start_z)`.
pub fn reservoir_guide_route(rt: &Runtime, name: &str, start_z: f64) -> Result<Points> {
    reservoir_guide_route_of(rt, &*state(rt)?, name, start_z)
}

fn route_length(a: [f64; 3]) -> Result<f64> {
    sqrt(dot3(a, a))
}
fn route_unit(a: [f64; 3]) -> Result<[f64; 3]> {
    Ok(scale3(a, div(1.0, route_length(a)?)?))
}

/// `_route_points(points)`: the points with repeats and straight-through points dropped.
pub fn route_points(points: &[[f64; 3]]) -> Result<Points> {
    ensure!(!points.is_empty(), "list index out of range");
    let mut kept = vec![points[0]];
    for &v in &points[1..] {
        if route_length(sub3(v, kept[kept.len() - 1]))? < 1e-09 {
            continue;
        }
        if kept.len() >= 2 {
            let (a, b) = (kept[kept.len() - 2], kept[kept.len() - 1]);
            if route_length(cross3(route_unit(sub3(b, a))?, route_unit(sub3(v, b))?))? < 1e-09 {
                let last = kept.len() - 1;
                kept[last] = v;
                continue;
            }
        }
        kept.push(v);
    }
    Ok(kept)
}

/// `_corner_data(points, bend_radius)`: the kept points and each corner's arc radius, eased
/// below `bend_radius` where two corners' setbacks would overrun the leg between them.
pub fn corner_data(points: &[[f64; 3]], bend_radius: f64) -> Result<(Points, Vec<f64>)> {
    let v = route_points(points)?;
    let n = v.len();
    let inner = 1..n.saturating_sub(1);
    let mut half = vec![0.0; n];
    for i in inner.clone() {
        let u = route_unit(sub3(v[i - 1], v[i]))?;
        let w = route_unit(sub3(v[i + 1], v[i]))?;
        half[i] = acos(clamp_unit(dot3(u, w)))? / 2.0;
    }
    let mut radius = vec![0.0; n];
    for i in inner.clone() {
        radius[i] = bend_radius;
    }
    for _ in 0..64 {
        let setback: Vec<f64> = (0..n)
            .map(|i| {
                if half[i] > 1e-09 {
                    div(radius[i], half[i].tan())
                } else {
                    Ok(0.0)
                }
            })
            .collect::<Result<_>>()?;
        let mut worst = 1.0;
        for i in 0..n.saturating_sub(1) {
            let leg = route_length(sub3(v[i + 1], v[i]))?;
            let want = setback[i] + setback[i + 1];
            if want > leg {
                worst = pmin(worst, div(leg, want)?);
            }
        }
        if worst >= 1.0 - 1e-12 {
            break;
        }
        for i in inner.clone() {
            radius[i] *= worst * 0.999;
        }
    }
    Ok((v, radius))
}

/// `corner_radii(points, bend_radius)`: the kept points as `cq.Vector`s and the corner radii.
pub fn corner_radii(rt: &Runtime, points: &[[f64; 3]], bend_radius: f64) -> Result<(Vec<Val>, Vec<f64>)> {
    let (points, radii) = corner_data(points, bend_radius)?;
    let cq = Cq::new(rt)?;
    let vectors = points
        .iter()
        .map(|p| cq.vector(*p))
        .collect::<Result<Vec<_>>>()?;
    Ok((vectors, radii))
}

/// `_drop_collinear(points)`.
pub fn drop_collinear(rt: &Runtime, points: &[[f64; 3]]) -> Result<Vec<Val>> {
    let cq = Cq::new(rt)?;
    route_points(points)?
        .iter()
        .map(|p| cq.vector(*p))
        .collect()
}

fn vsub(a: &Val, b: &Val) -> Result<Val> {
    hsm_documents::interop::binary("sub", a.clone(), b.clone())
}
fn vadd(a: &Val, b: &Val) -> Result<Val> {
    hsm_documents::interop::binary("add", a.clone(), b.clone())
}
fn length(v: &Val) -> Result<f64> {
    v.a("Length")?.f()
}

/// One corner of a route as `cq.Vector`s: its unit legs, half-angle and setback.
struct Corner {
    u: Val,
    w: Val,
    half: f64,
    setback: f64,
}
fn corner(v: &[Val], radius: &[f64], i: usize) -> Result<Corner> {
    let u = vsub(&v[i - 1], &v[i])?.m("normalized", vec![])?;
    let w = vsub(&v[i + 1], &v[i])?.m("normalized", vec![])?;
    let half = acos(clamp_unit(u.m("dot", args![w])?.f()?))? / 2.0;
    let setback = div(radius[i], half.tan())?;
    Ok(Corner {
        u,
        w,
        half,
        setback,
    })
}

/// `route_legs(points, bend_radius=route_bend_radius)`: the straight legs between corner arcs.
pub fn route_legs(rt: &Runtime, points: &[[f64; 3]], bend_radius: f64) -> Result<Vec<(Val, Val)>> {
    let (v, radius) = corner_radii(rt, points, bend_radius)?;
    let mut legs = vec![];
    let mut tail = v[0].clone();
    for i in 1..v.len().saturating_sub(1) {
        let c = corner(&v, &radius, i)?;
        let head = vadd(&v[i], &c.u.m("multiply", args![c.setback])?)?;
        if length(&vsub(&head, &tail)?)? > 1e-07 {
            legs.push((tail.clone(), head));
        }
        tail = vadd(&v[i], &c.w.m("multiply", args![c.setback])?)?;
    }
    let last = &v[v.len() - 1];
    if length(&vsub(last, &tail)?)? > 1e-07 {
        legs.push((tail, last.clone()));
    }
    Ok(legs)
}

/// `route_wire(points, bend_radius=route_bend_radius)`: the centreline as lines and arcs.
pub fn route_wire(rt: &Runtime, points: &[[f64; 3]], bend_radius: f64) -> Result<Val> {
    let (v, radius) = corner_radii(rt, points, bend_radius)?;
    let edge = rt.py("cadquery")?.a("Edge")?;
    let mut edges = vec![];
    let mut tail = v[0].clone();
    for i in 1..v.len().saturating_sub(1) {
        let c = corner(&v, &radius, i)?;
        let p_in = vadd(&v[i], &c.u.m("multiply", args![c.setback])?)?;
        let p_out = vadd(&v[i], &c.w.m("multiply", args![c.setback])?)?;
        let bisector = vadd(&c.u.m("normalized", vec![])?, &c.w.m("normalized", vec![])?)?
            .m("normalized", vec![])?;
        let centre = vadd(
            &v[i],
            &bisector.m("multiply", args![div(radius[i], c.half.sin())?])?,
        )?;
        let mid = vadd(
            &centre,
            &vsub(&v[i], &centre)?
                .m("normalized", vec![])?
                .m("multiply", args![radius[i]])?,
        )?;
        if length(&vsub(&p_in, &tail)?)? > 1e-07 {
            edges.push(edge.m("makeLine", args![tail, p_in])?);
        }
        edges.push(edge.m("makeThreePointArc", args![p_in, mid, p_out])?);
        tail = p_out;
    }
    let last = &v[v.len() - 1];
    if length(&vsub(last, &tail)?)? > 1e-07 {
        edges.push(edge.m("makeLine", args![tail, last])?);
    }
    rt.py("cadquery")?
        .a("Wire")?
        .m("assembleEdges", vec![Val::list(edges)])
}

/// `build_route(points, bend_radius=route_bend_radius, radius=line_radius)`: the swept tube.
pub fn build_route(rt: &Runtime, points: &[[f64; 3]], bend_radius: f64, radius: f64) -> Result<Val> {
    let wire = route_wire(rt, points, bend_radius)?;
    let cq = rt.py("cadquery")?;
    let origin = wire.m("startPoint", vec![])?;
    let normal = wire.m("tangentAt", args![0i64])?;
    let plane = cq.a("Plane")?.ck(vec![], kw!["origin" => origin, "normal" => normal])?;
    let profile = cq.a("Workplane")?.c(args![plane])?;
    let circle = profile.m("circle", args![radius])?;
    let path = cq
        .a("Workplane")?
        .c(args!["XY"])?
        .m("newObject", vec![Val::list(vec![wire])])?;
    circle
        .mk("sweep", args![path], kw!["isFrenet" => true])?
        .m("val", vec![])
}

/// `route_corridor(name, radius=port_hole_radius)`: a line's tube at a bore's radius.
pub fn route_corridor(rt: &Runtime, name: &str, radius: f64) -> Result<Val> {
    let s = state(rt)?;
    build_route(rt, s.routes.at(name)?, s.route_bend_radius, radius)
}

/// `fit_route(points, obstacles)`: the widest rung of the bend ladder whose tube clears every
/// obstacle, or the floor bend.
pub fn fit_route(rt: &Runtime, points: &[[f64; 3]], obstacles: &OMap<Val>) -> Result<(f64, Val)> {
    let s = state(rt)?;
    let overlap = rt.py("_overlap")?;
    for &rung in &s.bend_ladder {
        let bend = s.route_bend_radius * rung;
        if bend < s.bend_floor {
            break;
        }
        let tube = build_route(rt, points, bend, s.line_radius)?;
        let mut clear = vec![];
        for obstacle in obstacles.values() {
            clear.push(overlap.m("volume", args![tube, obstacle])?.f()? <= s.touch_volume);
        }
        if clear.iter().all(|c| *c) {
            return Ok((bend, tube));
        }
    }
    Ok((
        s.bend_floor,
        build_route(rt, points, s.bend_floor, s.line_radius)?,
    ))
}

/// `build_routes(obstacles=None)`: every line's `(bend, tube)`, fitted when obstacles are given.
pub fn build_routes(rt: &Runtime, obstacles: Option<&OMap<Val>>) -> Result<OMap<(f64, Val)>> {
    let s = state(rt)?;
    let mut out = OMap::new();
    for (name, points) in s.routes.iter() {
        let fitted = match obstacles {
            None => (
                s.route_bend_radius,
                build_route(rt, points, s.route_bend_radius, s.line_radius)?,
            ),
            Some(obstacles) => fit_route(rt, points, obstacles)?,
        };
        out.set(name, fitted);
    }
    Ok(out)
}

/// `carbonator_envelope()`: the carbonator tank and its coil envelope as one solid.
pub fn carbonator_envelope(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let (z0, z1) = s.carbonator_envelope_z_range;
    let vector = s.cq.a("Vector")?;
    let solid = s.cq.a("Solid")?;
    let tank = solid.m(
        "makeCylinder",
        args![
            s.carbonator_outer_radius,
            z1 - z0,
            vector.c(args![0i64, 0i64, z0])?
        ],
    )?;
    let (coil_lo, coil_hi) = (
        s.evap_tail_low_z - s.lldpe_tube_od / 2.0,
        s.evap_tail_high_z + s.lldpe_tube_od / 2.0,
    );
    let coil = solid.m(
        "makeCylinder",
        args![
            s.coil_envelope_radius,
            coil_hi - coil_lo,
            vector.c(args![0i64, 0i64, coil_lo])?
        ],
    )?;
    tank.m("fuse", args![coil])?.m("clean", vec![])
}

/// Python's `pattern % values`.
fn percent(pattern: &str, values: Vec<Val>) -> Result<String> {
    hsm_documents::interop::binary("mod", Val::Str(pattern.into()), Val::Tuple(values))?.str()
}

/// `next(row[field] for row in rows if test(row))`.
fn first_row(rows: &Val, field: &str, test: impl Fn(&Val) -> Result<bool>) -> Result<Val> {
    for row in rows.list()? {
        if test(&row)? {
            return row.k(field);
        }
    }
    bail!("StopIteration")
}

fn is(value: Val, text: &str) -> Result<bool> {
    hsm_documents::interop::eq(&value, &Val::Str(text.into()))
}

/// `report_routes(fitted, obstacles, *, measurements=None)`: each line's reading, printed.
pub fn report_routes(
    rt: &Runtime,
    fitted: &OMap<(f64, Val)>,
    obstacles: &OMap<Val>,
    measurements: Option<&Val>,
) -> Result<()> {
    let s = state(rt)?;
    let mut overlap = None;
    let mut readings: OMap<Val> = OMap::new();
    match measurements {
        None => overlap = Some(rt.py("_overlap")?),
        Some(m) => {
            for row in m.k("routes")?.list()? {
                readings.set(&row.k("name")?.str()?, row);
            }
        }
    }
    rt.print(percent(
        "  internal routes: %d lines in %s, stock arc %.4g mm — %s",
        vec![
            Val::Int(fitted.len() as i64),
            s.route_stock.a("name")?,
            s.route_bend_radius_val.clone(),
            s.route_stock.a("source")?,
        ],
    )?)?;
    let mut short: Vec<String> = vec![];
    let mut names: Vec<&str> = fitted.keys().collect();
    names.sort();
    for &name in &names {
        let (bend, tube) = fitted.at(name)?.clone();
        let (radius, length) = match &overlap {
            Some(_) => {
                let points = s.routes.at(name)?;
                let (_v, radius) = corner_radii(rt, points, bend)?;
                let length = route_wire(rt, points, bend)?.m("Length", vec![])?.f()?;
                (radius, length)
            }
            None => {
                let row = readings.at(name)?;
                (row.k("radii")?.floats()?, row.k("length")?.f()?)
            }
        };
        let inner: &[f64] = if radius.len() >= 2 {
            &radius[1..radius.len() - 1]
        } else {
            &[]
        };
        let corners: Vec<f64> = inner.iter().copied().filter(|r| *r > 0.0).collect();
        let tightest = if corners.is_empty() {
            f64::INFINITY
        } else {
            fmin(corners.iter().copied())
        };
        let mut hits = vec![];
        for (other, solid) in obstacles.iter() {
            let volume = match &overlap {
                Some(overlap) => overlap.m("volume", args![tube, solid])?.f()?,
                None => first_row(&readings.at(name)?.k("blocked")?, "volume", |row| {
                    is(row.k("name")?, other)
                })?
                .f()?,
            };
            if volume > s.touch_volume {
                hits.push(percent("%s by %.2f mm³", vec![other.into(), volume.into()])?);
            }
        }
        let tight = if corners.is_empty() {
            " none  ".to_string()
        } else {
            percent("%5.2f mm", vec![tightest.into()])?
        };
        let verdict = if hits.is_empty() {
            "clear".to_string()
        } else {
            format!("** {}", hits.join("; "))
        };
        rt.print(percent(
            "    %-17s %6.1f mm, %d corners, arc %5.2f mm, tightest %s — %s",
            vec![
                name.into(),
                length.into(),
                Val::Int(corners.len() as i64),
                bend.into(),
                tight.into(),
                verdict.into(),
            ],
        )?)?;
        if !corners.is_empty() && tightest < s.route_bend_radius - 1e-09 {
            short.push(percent("%s at %.2f mm", vec![name.into(), tightest.into()])?);
        }
    }
    let mut crossed = false;
    for (i, &a) in names.iter().enumerate() {
        for &b in &names[i + 1..] {
            let volume = match (&overlap, measurements) {
                (Some(overlap), _) => overlap
                    .m("volume", args![fitted.at(a)?.1, fitted.at(b)?.1])?
                    .f()?,
                (None, Some(m)) => first_row(&m.k("crossings")?, "volume", |row| {
                    Ok(is(row.k("a")?, a)? && is(row.k("b")?, b)?)
                })?
                .f()?,
                (None, None) => bail!("route readings"),
            };
            if volume > s.touch_volume {
                crossed = true;
            }
        }
    }
    rt.print(if crossed {
        "    ** LINES CROSS **"
    } else {
        "    no line meets another"
    })?;
    rt.print(if short.is_empty() {
        "    every corner at the stock arc".to_string()
    } else {
        percent(
            "    under the %.4g mm stock arc: %s",
            vec![s.route_bend_radius_val.clone(), short.join("; ").into()],
        )?
    })?;
    Ok(())
}

/// `route_segments(points, bend_radius=route_bend_radius)`: the centreline as line and arc
/// rows, each with its length.
pub fn route_segments(points: &[[f64; 3]], bend_radius: f64) -> Result<Vec<Val>> {
    let (points, radii) = corner_data(points, bend_radius)?;
    let mut segments = vec![];
    let mut tail = points[0];
    let line = |segments: &mut Vec<Val>, tail: [f64; 3], end: [f64; 3]| -> Result<()> {
        segments.push(dict! {
            "kind" => "line",
            "start_mm" => tail,
            "end_mm" => end,
            "length_mm" => route_length(sub3(end, tail))?,
        });
        Ok(())
    };
    for i in 1..points.len().saturating_sub(1) {
        let u = route_unit(sub3(points[i - 1], points[i]))?;
        let w = route_unit(sub3(points[i + 1], points[i]))?;
        let half = acos(clamp_unit(dot3(u, w)))? / 2.0;
        let setback = div(radii[i], half.tan())?;
        let incoming = add3(points[i], scale3(u, setback));
        let outgoing = add3(points[i], scale3(w, setback));
        let centre = add3(
            points[i],
            scale3(route_unit(add3(u, w))?, div(radii[i], half.sin())?),
        );
        let mid = add3(
            centre,
            scale3(route_unit(sub3(points[i], centre))?, radii[i]),
        );
        if route_length(sub3(incoming, tail))? > 1e-07 {
            line(&mut segments, tail, incoming)?;
        }
        let angle = std::f64::consts::PI - 2.0 * half;
        segments.push(dict! {
            "kind" => "arc",
            "start_mm" => incoming,
            "end_mm" => outgoing,
            "midpoint_mm" => mid,
            "radius_mm" => radii[i],
            "angle_radians" => angle,
            "length_mm" => radii[i] * angle,
        });
        tail = outgoing;
    }
    let last = points[points.len() - 1];
    if route_length(sub3(last, tail))? > 1e-07 {
        line(&mut segments, tail, last)?;
    }
    Ok(segments)
}

/// A Python point or vector, as the runtime's generic tuple helpers read it.
fn nums(c: &mut Call, index: usize, name: &str) -> Result<Vec<Num>> {
    c.req::<Vec<Num>>(index, name)
}
fn num_tuple(values: Vec<Num>) -> Val {
    Tuple(values).to_val()
}
fn num_dot(a: &[Num], b: &[Num]) -> Num {
    let mut total = Num::I(0);
    for (x, y) in a.iter().zip(b) {
        total = total.add(x.mul(*y));
    }
    total
}
fn num_length(a: &[Num]) -> Result<f64> {
    sqrt(num_dot(a, a).f())
}
fn num_unit(a: &[Num]) -> Result<Vec<Num>> {
    let k = Num::F(div(1.0, num_length(a)?)?);
    Ok(a.iter().map(|x| x.mul(k)).collect())
}
fn num_cross(a: &[Num], b: &[Num]) -> Result<Vec<Num>> {
    ensure!(a.len() >= 3 && b.len() >= 3, "tuple index out of range");
    Ok(vec![
        a[1].mul(b[2]).sub(a[2].mul(b[1])),
        a[2].mul(b[0]).sub(a[0].mul(b[2])),
        a[0].mul(b[1]).sub(a[1].mul(b[0])),
    ])
}

fn points_val(points: &[[f64; 3]]) -> Val {
    Val::list(points.iter().map(ToVal::to_val).collect())
}

fn obstacles_of(value: &Val) -> Result<OMap<Val>> {
    let mut out = OMap::new();
    for (key, value) in value.items()? {
        out.set(&key.str()?, value);
    }
    Ok(out)
}

fn fitted_val(fitted: &OMap<(f64, Val)>) -> Val {
    fitted.to_val()
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    let cap = foam_cap::state(rt)?;
    ns.module(rt, "math", "math")?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("cq", s.cq.clone());
    ns.value("_here", Val::Path(s.here.clone()));
    let interface = rt.import_module(core::NAME)?;
    for name in INTERFACE_NAMES {
        ns.value(name, interface.a(name)?);
    }
    ns.value("cap_face_z", cap.cap_face_z);
    ns.value("top_cap_height", cap.top_cap_height);
    ns.module(rt, "_above_mounts", mounts::NAME)?;
    ns.value("co2_inlet_lane_xyz", s.co2_inlet_lane_xyz.clone());
    ns.value("co2_inlet_xyz", s.co2_inlet_xyz.clone());
    ns.value("front_face_port_z", s.front_face_port_z.clone());
    ns.value(
        "water_outlet_ring_crossing_x",
        s.water_outlet_ring_crossing_x.clone(),
    );
    ns.value("_reservoir", s.reservoir.clone());
    ns.value("_shroud", s.shroud.clone());
    ns.value("stock_min", s.stock_min.clone());
    ns.value("stock_of", s.stock_of.clone());
    ns.value("line_radius", s.line_radius);
    ns.value("line_hug", s.line_hug);
    ns.value("route_bend_radius", s.route_bend_radius_val.clone());
    ns.value("route_stock", s.route_stock.clone());
    ns.value("dip_tube_z", s.dip_tube_z);
    ns.value("plate_storey_z", s.front_face_port_z.clone());
    ns.value("top_band_z", s.top_band_z);
    ns.value("shell_top_z", s.shell_top_z);
    ns.value("conduit_mouth_z", s.conduit_mouth_z);
    ns.value("lane_step_top_z", s.lane_step_top_z);
    ns.value("reservoir_cap_z", s.reservoir_cap_z);
    ns.value("reservoir_cap_top_z", s.reservoir_cap_top_z);
    ns.value("prv_vent_lane_y", s.prv_vent_lane_y);
    ns.value("prv_vent_start", s.prv_vent_start);
    ns.value("prv_vent_flank_y", s.prv_vent_flank_y);
    ns.value("prv_vent_fall_margin", s.prv_vent_fall_margin);
    ns.value("prv_vent_cross_z", s.prv_vent_cross_z);
    ns.value("prv_vent_reach", s.prv_vent_reach);
    ns.value("carbonator_envelope_z_range", s.carbonator_envelope_z_range);
    ns.func(rt, "coil_standoff_y", |rt, c| {
        Ok(coil_standoff_y(rt, c.req(0, "x")?)?.to_val())
    });
    ns.func(rt, "annulus_y", |rt, c| Ok(annulus_y(rt, c.req(0, "x")?)?.to_val()));
    ns.func(rt, "co2_run_y", |rt, c| Ok(co2_run_y(rt, c.req(0, "x")?)?.to_val()));
    ns.func(rt, "_routes", |rt, _| Ok(routes_of(rt, &*state(rt)?)?.to_val()));
    ns.func(rt, "world_point_in_shell", |rt, c| {
        Ok(world_point_in_shell(rt, &c.req::<Val>(0, "point")?)?.to_val())
    });
    ns.func(rt, "reservoir_guide_route", |rt, c| {
        let name = c.req::<String>(0, "name")?;
        let start_z = c.req(1, "start_z")?;
        Ok(points_val(&reservoir_guide_route(rt, &name, start_z)?))
    });
    ns.value("routes", s.routes.to_val());
    ns.func(rt, "_route_points", |_, c| {
        Ok(points_val(&route_points(&c.req::<Points>(0, "points")?)?))
    });
    ns.func(rt, "_corner_data", |_, c| {
        let points = c.req::<Points>(0, "points")?;
        let bend_radius = c.req(1, "bend_radius")?;
        let (points, radii) = corner_data(&points, bend_radius)?;
        Ok((points_val(&points), radii).to_val())
    });
    ns.func(rt, "route_legs", |rt, c| {
        let points = c.req::<Points>(0, "points")?;
        let bend_radius = c.opt(1, "bend_radius", state(rt)?.route_bend_radius)?;
        let legs = route_legs(rt, &points, bend_radius)?;
        Ok(Val::list(legs.iter().map(ToVal::to_val).collect()))
    });
    ns.func(rt, "route_wire", |rt, c| {
        let points = c.req::<Points>(0, "points")?;
        let bend_radius = c.opt(1, "bend_radius", state(rt)?.route_bend_radius)?;
        route_wire(rt, &points, bend_radius)
    });
    ns.func(rt, "build_route", |rt, c| {
        let s = state(rt)?;
        let points = c.req::<Points>(0, "points")?;
        let bend_radius = c.opt(1, "bend_radius", s.route_bend_radius)?;
        let radius = c.opt(2, "radius", s.line_radius)?;
        build_route(rt, &points, bend_radius, radius)
    });
    ns.func(rt, "route_corridor", |rt, c| {
        let name = c.req::<String>(0, "name")?;
        let radius = c.opt(1, "radius", state(rt)?.port_hole_radius)?;
        route_corridor(rt, &name, radius)
    });
    ns.value("bend_floor", s.bend_floor);
    ns.value("bend_ladder", Tuple(s.bend_ladder.clone()));
    ns.value("touch_volume", s.touch_volume);
    ns.func(rt, "fit_route", |rt, c| {
        let points = c.req::<Points>(0, "points")?;
        let obstacles = obstacles_of(&c.req::<Val>(1, "obstacles")?)?;
        Ok(fit_route(rt, &points, &obstacles)?.to_val())
    });
    ns.func(rt, "build_routes", |rt, c| {
        let obstacles = match c.opt::<Val>(0, "obstacles", Val::None)? {
            Val::None => None,
            value => Some(obstacles_of(&value)?),
        };
        Ok(fitted_val(&build_routes(rt, obstacles.as_ref())?))
    });
    ns.func(rt, "carbonator_envelope", |rt, _| carbonator_envelope(rt));
    ns.func(rt, "report_routes", |rt, c| {
        let fitted_arg = c.req::<Val>(0, "fitted")?;
        let mut fitted = OMap::new();
        for (key, value) in fitted_arg.items()? {
            fitted.set(&key.str()?, <(f64, Val)>::from_val(&value)?);
        }
        let obstacles = obstacles_of(&c.req::<Val>(1, "obstacles")?)?;
        let measurements = match c.kw::<Val>("measurements", Val::None)? {
            Val::None => None,
            value => Some(value),
        };
        report_routes(rt, &fitted, &obstacles, measurements.as_ref())?;
        Ok(Val::None)
    });
    ns.func(rt, "_route_sub", |_, c| {
        let (a, b) = (nums(c, 0, "a")?, nums(c, 1, "b")?);
        Ok(num_tuple(a.iter().zip(&b).map(|(x, y)| x.sub(*y)).collect()))
    });
    ns.func(rt, "_route_add", |_, c| {
        let (a, b) = (nums(c, 0, "a")?, nums(c, 1, "b")?);
        Ok(num_tuple(a.iter().zip(&b).map(|(x, y)| x.add(*y)).collect()))
    });
    ns.func(rt, "_route_mul", |_, c| {
        let a = nums(c, 0, "a")?;
        let scale = c.req::<Num>(1, "scale")?;
        Ok(num_tuple(a.iter().map(|x| x.mul(scale)).collect()))
    });
    ns.func(rt, "_route_dot", |_, c| {
        let (a, b) = (nums(c, 0, "a")?, nums(c, 1, "b")?);
        Ok(num_dot(&a, &b).to_val())
    });
    ns.func(rt, "_route_length", |_, c| {
        Ok(num_length(&nums(c, 0, "a")?)?.to_val())
    });
    ns.func(rt, "_route_unit", |_, c| {
        Ok(num_tuple(num_unit(&nums(c, 0, "a")?)?))
    });
    ns.func(rt, "_route_cross", |_, c| {
        let (a, b) = (nums(c, 0, "a")?, nums(c, 1, "b")?);
        Ok(num_tuple(num_cross(&a, &b)?))
    });
    ns.func(rt, "route_segments", |rt, c| {
        let points = c.req::<Points>(0, "points")?;
        let bend_radius = c.opt(1, "bend_radius", state(rt)?.route_bend_radius)?;
        Ok(Val::list(route_segments(&points, bend_radius)?))
    });
    ns.func(rt, "_drop_collinear", |rt, c| {
        Ok(Val::list(drop_collinear(rt, &c.req::<Points>(0, "points")?)?))
    });
    ns.func(rt, "corner_radii", |rt, c| {
        let points = c.req::<Points>(0, "points")?;
        let bend_radius = c.req(1, "bend_radius")?;
        let (vectors, radii) = corner_radii(rt, &points, bend_radius)?;
        Ok((Val::list(vectors), radii).to_val())
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
