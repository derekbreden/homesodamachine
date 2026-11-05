//! Above-core shell datums and composition of numeric panel recipes.
//!
//! # Typed API
//!
//! Typed callers use these instead of the namespace:
//!
//! - [`rear_identification`]: the `rear_identification` module's namespace, imported on the first
//!   call (`functools.cache`).
//! - [`psu_fastener_plan`] and [`relay_fastener_plan`] give a [`FastenerPlan`];
//!   [`FastenerPlan::to_val`] is the dict the namespace function returns.
//! - [`wall_mount_datums`]: a [`WallMount`] per mounted part (`psu`, `relay-1`, `relay-2`), each
//!   with its plan and [`WallStation`]s; [`wall_mount_datums_val`] is the namespace's dict.
//! - [`wall_fastener_bounds`]: those mounts and a [`FastenerLane`] for each threaded station's screw
//!   and insert ([`FastenerLane::key`] is the dict key, `psu-screw-1`);
//!   [`wall_fastener_bounds_val`] is the namespace's dict. [`in_wall_fastener_lane`] answers for
//!   six floats.
//! - [`c14_fastener_plan`] ([`C14Fasteners`]), [`keystone_land`] (six floats),
//!   [`valve_seat_datums`] ([`ValveSeatDatum`]; [`valve_seat_datums_val`]) and
//!   [`gas_check_support_datums`] (the dict).
//! - [`rear_geometry`] and [`apply`] compose the solids they are handed (Python objects) with the
//!   panel recorder's factories, read from the namespace at each call.
//!
//! The layout's poses, and the points and directions the layout derives from them, are read once
//! per registry: `above_core.specification()` is cached and `point`/`vector` are pure. Every call
//! still makes its `sys.path` insertions. Errors carry the runtime's texts (`index out of range`,
//! `unpack: expected 3, got 2`).
use super::_enclosure_datums;
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use hsm_documents::interop;
use std::cell::RefCell;
use std::path::PathBuf;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_above_core_shell";

/// The graph factories, `None` until a panel recorder supplies them; the back-top and front-top
/// recorders replace them while they record, so each is read from the namespace where it is used.
const FACTORIES: [&str; 11] = [
    "box",
    "rectangle",
    "ycylinder",
    "zcylinder",
    "rear_well_tower",
    "wall_bosses",
    "valve_seats",
    "c14_rear_cutters",
    "keystone_rear_geometry",
    "fluid_supports",
    "stacked_well_towers",
];

/// The module's typed state: its namespace, the paths and providers its top level reads, and the
/// layout values it has read.
struct State {
    ns: Ns,
    /// `HERE`: this module's directory.
    here: PathBuf,
    /// `HERE.parents[2]`: the `hardware` directory.
    hardware: PathBuf,
    /// `layout`: the `above_core` module.
    layout: Val,
    flute_depth: Num,
    /// `rear_identification()`'s module, once imported.
    identification: RefCell<Option<Val>>,
    /// `layout.<function>`.
    functions: RefCell<Vec<(&'static str, Val)>>,
    /// `layout.pose(name)`: one dict per part.
    poses: RefCell<Vec<(String, Val)>>,
    /// `layout.pose(name)['translation_mm']`, as the document holds it.
    translations: RefCell<Vec<(String, [Val; 3])>>,
    mounts: RefCell<Vec<(&'static str, Rc<Mount>)>>,
    seat: RefCell<Option<Rc<Seat>>>,
    seat_stock: RefCell<Vec<(&'static str, Rc<SeatStock>)>>,
}

fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// A value made once per key and kept.
fn cached<K: PartialEq + Clone, T: Clone>(cell: &RefCell<Vec<(K, T)>>, key: &K, make: impl FnOnce() -> Result<T>) -> Result<T> {
    let held = cell.borrow().iter().find(|(k, _)| k == key).map(|(_, v)| v.clone());
    if let Some(value) = held {
        return Ok(value);
    }
    let value = make()?;
    cell.borrow_mut().push((key.clone(), value.clone()));
    Ok(value)
}

/// A mounted part's axis and the world positions of its native holes.
struct Mount {
    /// `layout.vector(pose['rotation'], (0., 0., 1.))`.
    axis: [f64; 3],
    /// `layout.point(pose, (hx, hy, 0.))` for each of the source's `holes`.
    holes: Vec<[f64; 3]>,
}

/// The `valve_seat` numbers the seat datums use.
struct Seat {
    half_x: Num,
    half_y: Num,
    /// `socket_floor_z - wall`.
    floor: Num,
    top: Num,
    socket_diameter: Num,
    wall: Num,
}

/// A valve seat's stock extents, rooted in its sidewall.
struct SeatStock {
    low: [f64; 3],
    high: [f64; 3],
}

impl State {
    /// `layout.<name>`: nothing replaces the layout's functions.
    fn function(&self, name: &'static str) -> Result<Val> {
        cached(&self.functions, &name, || self.layout.attr(name))
    }
    /// `layout.pose(name)`.
    fn pose(&self, name: &str) -> Result<Val> {
        cached(&self.poses, &name.to_owned(), || py::call(&self.function("pose")?, vec![py::s(name)]))
    }
    /// `layout.pose(name)['translation_mm']`.
    fn translation(&self, name: &str) -> Result<[Val; 3]> {
        cached(&self.translations, &name.to_owned(), || {
            let t = py::unpack(&py::snapshot(&self.pose(name)?.get(py::s("translation_mm"))?)?, 3)?;
            Ok([t[0].clone(), t[1].clone(), t[2].clone()])
        })
    }
    /// `layout.point(frame, local)`.
    fn point(&self, frame: &Val, local: Val) -> Result<[f64; 3]> {
        py::v3(&py::call(&self.function("point")?, vec![frame.clone(), local])?)
    }
    /// `layout.vector(rotation, local)`.
    fn vector(&self, rotation: Val, local: [f64; 3]) -> Result<[f64; 3]> {
        py::v3(&py::call(&self.function("vector")?, vec![rotation, py::ftuple(&local)])?)
    }
    fn mount(&self, name: &'static str, source: &Val) -> Result<Rc<Mount>> {
        cached(&self.mounts, &name, || {
            let frame = self.pose(name)?;
            let axis = self.vector(frame.get(py::s("rotation"))?, [0., 0., 1.])?;
            let mut holes = vec![];
            for hole in py::snapshot(&source.attr("holes")?)?.iter()? {
                let xy = py::unpack(&hole, 2)?;
                holes.push(self.point(&frame, py::tuple([xy[0].clone(), xy[1].clone(), Val::Float(0.)]))?);
            }
            Ok(Rc::new(Mount { axis, holes }))
        })
    }
    /// The `valve_seat` module's numbers: module constants, read once.
    fn seat(&self, module: &Val) -> Result<Rc<Seat>> {
        if let Some(seat) = self.seat.borrow().clone() {
            return Ok(seat);
        }
        let read = |name: &str| Num::of(&module.attr(name)?);
        let wall = read("wall")?;
        let seat = Rc::new(Seat {
            half_x: read("seat_half_x")?,
            half_y: read("seat_half_y")?,
            floor: read("socket_floor_z")?.sub(wall),
            top: read("seat_top_z")?,
            socket_diameter: read("socket_diameter")?,
            wall,
        });
        *self.seat.borrow_mut() = Some(seat.clone());
        Ok(seat)
    }
    /// The world extents of the seat's corners in the part's frame, rooted at the sidewall on
    /// the part's side.
    fn seat_stock(&self, name: &'static str, seat: &Seat) -> Result<Rc<SeatStock>> {
        cached(&self.seat_stock, &name, || {
            let frame = self.pose(name)?;
            let mut corners = vec![];
            for x in [seat.half_x.neg(), seat.half_x] {
                for y in [seat.half_y.neg(), seat.half_y] {
                    for z in [seat.floor, seat.top] {
                        corners.push(self.point(&frame, Num::vals(&[x, y, z]))?);
                    }
                }
            }
            let (mut low, mut high) = (corners[0], corners[0]);
            for corner in &corners[1..] {
                for i in 0..3 {
                    low[i] = num::min2(low[i], corner[i]);
                    high[i] = num::max2(high[i], corner[i]);
                }
            }
            let side = self.translation(name)?[0].num()?;
            anyhow::ensure!(!side.is_nan(), "unordered numeric comparison");
            if side < 0. {
                low[0] = -98.51;
            } else {
                high[0] = 98.51;
            }
            Ok(Rc::new(SeatStock { low, high }))
        })
    }
}

/// `isinstance(value, (int, float))` as the runtime's arithmetic reads it.
fn is_number(value: &Val) -> bool {
    matches!(value, Val::Int(_) | Val::Bool(_) | Val::Float(_))
}

/// `value == text` or `value != text`.
fn text_is(op: &str, value: &Val, text: &str) -> Result<bool> {
    match value {
        Val::Str(held) => Ok((held == text) == (op == "eq")),
        _ => interop::compare(op, value.clone(), py::s(text))?.truthy(),
    }
}

/// `value is not None`.
fn is_not_none(value: &Val) -> Result<bool> {
    interop::compare("is_not", value.clone(), Val::None)?.truthy()
}

/// `rear_identification()`: the rear identification module, imported once.
pub fn rear_identification(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let held = st.identification.borrow().clone();
    if let Some(module) = held {
        return Ok(module);
    }
    let directory = st.here.parent().context("index out of range")?.join("rear-identification");
    py::sys_path_insert(rt, &py::path_str(&directory))?;
    let module = rt.import("rear_identification")?;
    *st.identification.borrow_mut() = Some(module.clone());
    Ok(module)
}

/// A fastener plan: the PSU's or a relay's. Fields only one of the two plans has are `Some` in
/// that plan.
#[derive(Clone, Debug)]
pub struct FastenerPlan {
    pub count: i64,
    /// Relay: the holes that take screws.
    pub active_hole_indices: Option<[i64; 2]>,
    pub screw: &'static str,
    pub screw_length_mm: f64,
    pub insert: &'static str,
    pub insert_length_mm: f64,
    /// PSU.
    pub ear_thickness_range_mm: Option<[f64; 2]>,
    /// Relay.
    pub pcb_thickness_mm: Option<f64>,
    pub receiving_range_mm: [f64; 2],
    pub pilot_depth_mm: f64,
    pub minimum_tip_air_mm: f64,
    pub minimum_blind_backing_mm: f64,
    pub minimum_fluted_backing_mm: f64,
    /// `flute_depth`.
    pub maximum_flute_depth_mm: Num,
    pub boss_radius_mm: f64,
    pub pilot_radius_mm: f64,
    /// Relay.
    pub insert_face_setback_mm: Option<f64>,
    /// Relay.
    pub screw_clearance_radius_mm: Option<f64>,
    /// Relay.
    pub pcb_support: Option<&'static str>,
    pub parent: &'static str,
    pub load_retention_qualified: bool,
}

impl FastenerPlan {
    /// The dict's rows, in the order each plan writes them.
    fn rows(&self) -> Vec<(&'static str, Val)> {
        let mut rows = vec![("count", Val::Int(self.count))];
        if let Some(active) = self.active_hole_indices {
            rows.push(("active_hole_indices", py::tuple(active.map(Val::Int))));
        }
        rows.push(("screw", py::s(self.screw)));
        rows.push(("screw_length_mm", Val::Float(self.screw_length_mm)));
        rows.push(("insert", py::s(self.insert)));
        rows.push(("insert_length_mm", Val::Float(self.insert_length_mm)));
        if let Some(range) = self.ear_thickness_range_mm {
            rows.push(("ear_thickness_range_mm", py::ftuple(&range)));
        }
        if let Some(thickness) = self.pcb_thickness_mm {
            rows.push(("pcb_thickness_mm", Val::Float(thickness)));
        }
        rows.push(("receiving_range_mm", py::ftuple(&self.receiving_range_mm)));
        rows.push(("pilot_depth_mm", Val::Float(self.pilot_depth_mm)));
        rows.push(("minimum_tip_air_mm", Val::Float(self.minimum_tip_air_mm)));
        rows.push(("minimum_blind_backing_mm", Val::Float(self.minimum_blind_backing_mm)));
        rows.push(("minimum_fluted_backing_mm", Val::Float(self.minimum_fluted_backing_mm)));
        rows.push(("maximum_flute_depth_mm", self.maximum_flute_depth_mm.val()));
        rows.push(("boss_radius_mm", Val::Float(self.boss_radius_mm)));
        rows.push(("pilot_radius_mm", Val::Float(self.pilot_radius_mm)));
        if let Some(setback) = self.insert_face_setback_mm {
            rows.push(("insert_face_setback_mm", Val::Float(setback)));
        }
        if let Some(radius) = self.screw_clearance_radius_mm {
            rows.push(("screw_clearance_radius_mm", Val::Float(radius)));
        }
        if let Some(text) = self.pcb_support {
            rows.push(("pcb_support", py::s(text)));
        }
        rows.push(("parent", py::s(self.parent)));
        rows.push(("load_retention_qualified", Val::Bool(self.load_retention_qualified)));
        rows
    }
    /// The plan's dict.
    pub fn to_val(&self) -> Val {
        py::dict(self.rows())
    }
    /// `plan.get('insert_face_setback_mm', 0.)`.
    pub fn setback(&self) -> f64 {
        self.insert_face_setback_mm.unwrap_or(0.)
    }
}

/// Four short inserts support the drawing's 6.7 ± 1 mm mounting ears.
pub fn psu_fastener_plan(rt: &Rt) -> Result<FastenerPlan> {
    let st = state(rt)?;
    let reach = [10. - 7.7, 10. - 5.7];
    let pilot = 5.;
    let lift = st.translation("psu")?[2].num()?;
    let backing = 355. - lift - pilot;
    Ok(FastenerPlan {
        count: 4,
        active_hole_indices: None,
        screw: "M3x10 SHCS",
        screw_length_mm: 10.,
        insert: "RX-M3Sx4",
        insert_length_mm: 4.,
        ear_thickness_range_mm: Some([5.7, 7.7]),
        pcb_thickness_mm: None,
        receiving_range_mm: reach,
        pilot_depth_mm: pilot,
        minimum_tip_air_mm: pilot - reach[1],
        minimum_blind_backing_mm: backing,
        minimum_fluted_backing_mm: backing,
        maximum_flute_depth_mm: st.flute_depth,
        boss_radius_mm: 5.,
        pilot_radius_mm: 2.,
        insert_face_setback_mm: None,
        screw_clearance_radius_mm: None,
        pcb_support: None,
        parent: "enclosure-back-top",
        load_retention_qualified: false,
    })
}

/// Two header-end screws and terminal-end edge rails hold each PCB.
pub fn relay_fastener_plan(rt: &Rt) -> Result<FastenerPlan> {
    let st = state(rt)?;
    let setback = 2.5;
    let reach = 8. - 1.5 - setback;
    let pilot = reach + 1.;
    let (first, second) = (st.translation("relay-1")?[0].num()?, st.translation("relay-2")?[0].num()?);
    anyhow::ensure!(first.partial_cmp(&second).is_some(), "unordered numeric comparison");
    let blind = num::min2(first, second) - setback - pilot + 107.5;
    Ok(FastenerPlan {
        count: 2,
        active_hole_indices: Some([0, 1]),
        screw: "M3x8 SHCS",
        screw_length_mm: 8.,
        insert: "RX-M3Sx4",
        insert_length_mm: 4.,
        ear_thickness_range_mm: None,
        pcb_thickness_mm: Some(1.5),
        receiving_range_mm: [reach, reach],
        pilot_depth_mm: pilot,
        minimum_tip_air_mm: 1.,
        minimum_blind_backing_mm: blind,
        minimum_fluted_backing_mm: blind - st.flute_depth.f(),
        maximum_flute_depth_mm: st.flute_depth,
        boss_radius_mm: 5.,
        pilot_radius_mm: 2.,
        insert_face_setback_mm: Some(setback),
        screw_clearance_radius_mm: Some(1.7),
        pcb_support: Some(
            "Four 3 mm edge ledges support the PCB; the terminal pair captures its top edges. The insert faces stand behind the pin envelope.",
        ),
        parent: "enclosure-back-top",
        load_retention_qualified: false,
    })
}

/// One native mounting hole of a wall-mounted part, in world millimetres.
#[derive(Clone, Debug)]
pub struct WallStation {
    pub native_hole_index: i64,
    pub position_world_mm: [f64; 3],
    pub insert_face_world_mm: [f64; 3],
    pub axis_world: [f64; 3],
    pub threaded: bool,
    /// `(x, y, 349.25)` under the PSU, `(-98.52, y, z)` on the west wall.
    pub stock_root_world_mm: [f64; 3],
    pub standoff_mm: f64,
}

impl WallStation {
    fn to_val(&self) -> Val {
        py::dict([
            ("native_hole_index", Val::Int(self.native_hole_index)),
            ("position_world_mm", py::ftuple(&self.position_world_mm)),
            ("insert_face_world_mm", py::ftuple(&self.insert_face_world_mm)),
            ("axis_world", py::ftuple(&self.axis_world)),
            ("threaded", Val::Bool(self.threaded)),
            ("stock_root_world_mm", py::ftuple(&self.stock_root_world_mm)),
            ("stock_root_world_x_mm", Val::Float(self.stock_root_world_mm[0])),
            ("standoff_mm", Val::Float(self.standoff_mm)),
        ])
    }
}

/// A wall-mounted part's plan and stations.
#[derive(Clone, Debug)]
pub struct WallMount {
    /// `psu`, `relay-1` or `relay-2`.
    pub name: &'static str,
    pub plan: FastenerPlan,
    pub stations: Vec<WallStation>,
}

impl WallMount {
    /// `{**plan, 'stations': tuple(stations)}`, and the station dicts it holds.
    fn to_val(&self) -> (Val, Vec<Val>) {
        let stations: Vec<Val> = self.stations.iter().map(WallStation::to_val).collect();
        let mut rows = self.plan.rows();
        rows.push(("stations", Val::Tuple(stations.clone())));
        (py::dict(rows), stations)
    }
}

/// Native mounting holes on ceiling PSU bosses and west-wall relay bars.
pub fn wall_mount_datums(rt: &Rt) -> Result<Vec<WallMount>> {
    let st = state(rt)?;
    let reference = st.hardware.join("reference");
    let paths = ["meanwell-irm90", "teyleten-relay"].map(|name| py::s(py::path_str(&reference.join(name))));
    let search = rt.import("sys")?.attr("path")?;
    search.set(Val::Slice { start: None, stop: Some(0), step: 1 }, Val::list(paths.to_vec()))?;
    let psu = rt.import("meanwell_irm90")?;
    let relay = rt.import("teyleten_relay")?;
    let parts = [
        ("psu", &psu, psu_fastener_plan(rt)?),
        ("relay-1", &relay, relay_fastener_plan(rt)?),
        ("relay-2", &relay, relay_fastener_plan(rt)?),
    ];
    let mut result = Vec::with_capacity(parts.len());
    for (name, source, plan) in parts {
        let mount = st.mount(name, source)?;
        let axis = mount.axis;
        let setback = plan.setback();
        let stations = mount
            .holes
            .iter()
            .enumerate()
            .map(|(index, &point)| {
                let root = if name == "psu" { [point[0], point[1], 349.25] } else { [-98.52, point[1], point[2]] };
                WallStation {
                    native_hole_index: index as i64,
                    position_world_mm: point,
                    insert_face_world_mm: [0, 1, 2].map(|i| point[i] - setback * axis[i]),
                    axis_world: axis,
                    threaded: name == "psu" || plan.active_hole_indices.is_some_and(|active| active.contains(&(index as i64))),
                    stock_root_world_mm: root,
                    standoff_mm: num::sum((0..3).map(|i| (point[i] - root[i]) * axis[i])),
                }
            })
            .collect();
        result.push(WallMount { name, plan, stations });
    }
    Ok(result)
}

/// `wall_mount_datums()` as the namespace function returns it.
pub fn wall_mount_datums_val(mounts: &[WallMount]) -> Val {
    py::dict(mounts.iter().map(|mount| (mount.name, mount.to_val().0)))
}

/// One threaded station's screw or insert envelope.
#[derive(Clone, Debug)]
pub struct FastenerLane {
    pub component: &'static str,
    /// `screw` or `insert`.
    pub kind: &'static str,
    /// The station's place among its part's holes, counted from one.
    pub number: i64,
    /// The station's mount and its index there, in what [`wall_fastener_bounds`] returns.
    pub mount: usize,
    pub station: usize,
    /// `(min, max)` corners.
    pub bounds_mm: [[f64; 3]; 2],
}

impl FastenerLane {
    /// `f'{component}-{kind}-{number}'`.
    pub fn key(&self) -> String {
        format!("{}-{}-{}", self.component, self.kind, num::fmti(self.number, ""))
    }
}

/// Named screw/insert envelopes on the drilled PSU and relay stations.
///
/// These are the finite mounting lanes through the flank, not clearance
/// exemptions for a complete device or for hardware elsewhere in the wall.
pub fn wall_fastener_bounds(rt: &Rt) -> Result<(Vec<WallMount>, Vec<FastenerLane>)> {
    let mounts = wall_mount_datums(rt)?;
    let lanes = fastener_lanes(&mounts);
    Ok((mounts, lanes))
}

fn fastener_lanes(mounts: &[WallMount]) -> Vec<FastenerLane> {
    let mut lanes = vec![];
    for (m, mount) in mounts.iter().enumerate() {
        for (k, station) in mount.stations.iter().enumerate() {
            if !station.threaded {
                continue;
            }
            let axis = station.axis_world;
            let (point, face) = (station.position_world_mm, station.insert_face_world_mm);
            let reach = if mount.name == "psu" { 6.7 } else { 1.5 };
            let head = [0, 1, 2].map(|i| point[i] + axis[i] * reach);
            for (kind, origin, lo, hi, radius) in [
                ("screw", head, -mount.plan.screw_length_mm, 3., 2.75),
                ("insert", face, -mount.plan.insert_length_mm, 0., 2.3),
            ] {
                let ends = [lo, hi].map(|t| [0, 1, 2].map(|i| origin[i] + axis[i] * t));
                let radial = axis.map(|u| radius * num::max2(0., 1. - u * u).sqrt());
                let low = [0, 1, 2].map(|i| num::min2(ends[0][i], ends[1][i]) - radial[i]);
                let high = [0, 1, 2].map(|i| num::max2(ends[0][i], ends[1][i]) + radial[i]);
                lanes.push(FastenerLane {
                    component: mount.name,
                    kind,
                    number: k as i64 + 1,
                    mount: m,
                    station: k,
                    bounds_mm: [low, high],
                });
            }
        }
    }
    lanes
}

/// `wall_fastener_bounds()` as the namespace function returns it: each row holds its station's
/// dict and its part's plan dict, shared between the part's rows.
pub fn wall_fastener_bounds_val(mounts: &[WallMount], lanes: &[FastenerLane]) -> Val {
    let built: Vec<(Val, Vec<Val>)> = mounts.iter().map(WallMount::to_val).collect();
    py::dict(lanes.iter().map(|lane| {
        let (plan, stations) = &built[lane.mount];
        let row = py::dict([
            ("component", py::s(lane.component)),
            ("parent", py::s(mounts[lane.mount].plan.parent)),
            ("kind", py::s(lane.kind)),
            ("station", stations[lane.station].clone()),
            ("plan", plan.clone()),
            ("bounds_mm", py::tuple([py::ftuple(&lane.bounds_mm[0]), py::ftuple(&lane.bounds_mm[1])])),
        ]);
        (lane.key(), row)
    }))
}

/// The bounds of the lane `name` names, after the lanes are made afresh.
fn lane_bounds(rt: &Rt, name: &Val) -> Result<Option<[[f64; 3]; 2]>> {
    let (_, lanes) = wall_fastener_bounds(rt)?;
    let Val::Str(name) = name else { return Ok(None) };
    Ok(lanes.into_iter().find(|lane| lane.key() == *name).map(|lane| lane.bounds_mm))
}

/// `a >= b` (`ge`) or `a <= b` (`le`) of two floats.
fn within(op: &str, a: f64, b: f64) -> Result<bool> {
    let order = a.partial_cmp(&b).context("unordered numeric comparison")?;
    Ok(if op == "ge" { order.is_ge() } else { order.is_le() })
}

/// Whether this named hardware stays inside its own drilled mounting lane.
///
/// `bounds` is `(xmin, ymin, zmin, xmax, ymax, zmax)`.
pub fn in_wall_fastener_lane(rt: &Rt, name: &str, bounds: &[f64; 6], tolerance: f64) -> Result<bool> {
    let Some([lo, hi]) = lane_bounds(rt, &py::s(name))? else { return Ok(false) };
    let mut inside = [false; 3];
    for i in 0..3 {
        inside[i] = within("ge", bounds[i], lo[i] - tolerance)? && within("le", bounds[i + 3], hi[i] + tolerance)?;
    }
    Ok(inside.iter().all(|&yes| yes))
}

/// `x - tolerance` or `x + tolerance` of the value the caller gave.
fn offset(op: &str, x: f64, tolerance: &Val) -> Result<Val> {
    if is_number(tolerance) {
        let t = tolerance.num()?;
        return Ok(Val::Float(if op == "sub" { x - t } else { x + t }));
    }
    interop::binary(op, Val::Float(x), tolerance.clone())
}

/// `in_wall_fastener_lane(name, bounds, tolerance)` for the values Python passes.
fn in_wall_fastener_lane_val(rt: &Rt, name: &Val, bounds: &Val, tolerance: &Val) -> Result<Val> {
    let Some([lo, hi]) = lane_bounds(rt, name)? else { return Ok(Val::Bool(false)) };
    let mut inside = Vec::with_capacity(3);
    for i in 0..3 {
        let value = bounds.get(Val::Int(i as i64))?;
        let above = interop::compare("ge", value, offset("sub", lo[i], tolerance)?)?.truthy()?;
        inside.push(above && {
            let value = bounds.get(Val::Int(i as i64 + 3))?;
            interop::compare("le", value, offset("add", hi[i], tolerance)?)?.truthy()?
        });
    }
    Ok(Val::Bool(inside.iter().all(|&yes| yes)))
}

/// `c14_fastener_plan()`.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct C14Fasteners {
    pub screw_length_mm: f64,
    pub washer_od_mm: f64,
    pub washer_thickness_mm: f64,
    pub flange_thickness_mm: f64,
    pub insert_length_mm: f64,
    pub screw_reach_mm: f64,
    pub pilot_depth_mm: f64,
    pub boss_depth_mm: f64,
    pub tip_air_mm: f64,
    pub backing_mm: f64,
}

impl C14Fasteners {
    pub fn to_val(&self) -> Val {
        py::dict([
            ("screw_length_mm", Val::Float(self.screw_length_mm)),
            ("washer_od_mm", Val::Float(self.washer_od_mm)),
            ("washer_thickness_mm", Val::Float(self.washer_thickness_mm)),
            ("flange_thickness_mm", Val::Float(self.flange_thickness_mm)),
            ("insert_length_mm", Val::Float(self.insert_length_mm)),
            ("screw_reach_mm", Val::Float(self.screw_reach_mm)),
            ("pilot_depth_mm", Val::Float(self.pilot_depth_mm)),
            ("boss_depth_mm", Val::Float(self.boss_depth_mm)),
            ("tip_air_mm", Val::Float(self.tip_air_mm)),
            ("backing_mm", Val::Float(self.backing_mm)),
        ])
    }
}

/// The washer bridges the inlet's native countersink under a socket head.
pub const fn c14_fastener_plan() -> C14Fasteners {
    C14Fasteners {
        screw_length_mm: 10.,
        washer_od_mm: 7.,
        washer_thickness_mm: 0.5,
        flange_thickness_mm: 3.25,
        insert_length_mm: 4.,
        screw_reach_mm: 6.25,
        pilot_depth_mm: 7.25,
        boss_depth_mm: 10.25,
        tip_air_mm: 1.,
        backing_mm: 3.,
    }
}

/// The flat land round the jack's aperture on the rear face: the flutes stay off its
/// three-millimetre lip and the ease over the aperture, one wall past each edge.
pub fn keystone_land(rt: &Rt) -> Result<[f64; 6]> {
    let st = state(rt)?;
    let enclosure = rt.import("enclosure")?;
    let jack = enclosure.attr("_keystone")?;
    let spec = py::call(&st.function("specification")?, vec![])?;
    let centre = spec.get(py::s("rear_wall"))?.get(py::s("dry_openings"))?.get(py::s("keystone"))?.get(py::s("face_center_mm"))?;
    let centre = py::unpack(&centre, 3)?;
    let (x, y, z) = (centre[0].num()?, centre[1].num()?, centre[2].num()?);
    let slip = enclosure.attr("fits")?.attr("slip")?.num()?;
    let wall = enclosure.attr("wall")?.num()?;
    let half_w = jack.attr("FACE_W")?.num()? / 2. + slip + wall;
    let half_h = jack.attr("FACE_H")?.num()? / 2. + slip + wall;
    let shoulder = enclosure.attr("keystone_ease_shoulder")?.num()?;
    Ok([x - half_w, x + half_w, y - 3., y + 1., z - half_h, z + half_h + shoulder])
}

/// The purchased check's fixed barrel band, carried into the east bay.
///
/// The body scale and socket depths retain the vendor-reference estimates.
/// The eight-millimetre bearing stays inside its fixed cylindrical band.
/// Both gas seats share Z293..301 and join as one plain rectangular carrier.
pub fn gas_check_support_datums(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    py::sys_path_insert(rt, &py::path_str(&st.hardware.join("reference/neofit-achv44-check")))?;
    let check = rt.import("neofit_achv44_check")?;
    let band = py::unpack(&py::method(&check, "bearing_band", vec![])?, 3)?;
    let (first, last, body_radius) = (band[0].clone(), band[1].clone(), band[2].clone());
    let inlet = py::unpack(&py::method(&check, "inlet", vec![])?, 2)?[0].clone();
    let along = Num::of(&inlet.get(Val::Int(1))?)?.add(Num::of(&first)?.add(Num::of(&last)?).div(Num::F(2.)));
    let native_centre = py::tuple([Val::Float(0.), along.val(), Val::Float(0.)]);
    let frame = py::call(&st.function("snapshot_pose")?, vec![py::s("gas-check")])?;
    let world = py::unpack(&py::call(&st.function("point")?, vec![frame.clone(), native_centre])?, 3)?;
    let centre = py::tuple([world[0].clone(), world[1].clone(), Val::Float(297.)]);
    let axis = py::call(&st.function("vector")?, vec![frame.get(py::s("rotation"))?, py::ftuple(&[0., 1., 0.])])?;
    let seat = Num::of(&body_radius)?.add(Num::F(0.25));
    let outer = seat.add(Num::F(3.)).f();
    anyhow::ensure!(outer.partial_cmp(&11.).is_some(), "unordered numeric comparison");
    Ok(py::dict([
        ("centre_world_mm", centre),
        ("axis_world", axis),
        ("fixed_band_from_inlet_mm", py::tuple([first, last])),
        ("body_radius_mm", body_radius),
        ("seat_radius_mm", seat.val()),
        ("bearing_width_mm", Val::Float(8.)),
        ("outer_half_y_mm", Val::Float(num::max2(11., outer))),
        ("wall_root_x_mm", Val::Float(98.51)),
        ("nominal_radial_air_mm", Val::Float(0.25)),
        ("ordinary_wall_mm", Val::Float(3.)),
    ]))
}

/// A valve's socket plate, rooted in its sidewall.
#[derive(Clone)]
pub struct ValveSeatDatum {
    /// `valve-v-a` or `vk-solenoid`.
    pub name: &'static str,
    pub stock_min_world_mm: [f64; 3],
    pub stock_max_world_mm: [f64; 3],
    pub socket_diameter_mm: Num,
    pub socket_floor_backing_mm: Num,
    /// The valve's pose dict, `layout.pose(name)`.
    pub frame: Val,
}

impl ValveSeatDatum {
    pub fn to_val(&self) -> Val {
        py::dict([
            ("parent", py::s("enclosure-back-top")),
            ("stock_min_world_mm", py::flist(&self.stock_min_world_mm)),
            ("stock_max_world_mm", py::flist(&self.stock_max_world_mm)),
            ("socket_diameter_mm", self.socket_diameter_mm.val()),
            ("socket_floor_backing_mm", self.socket_floor_backing_mm.val()),
            ("frame", self.frame.clone()),
            ("interface", py::s("Shared valve_seat V69 four blind sockets and open port channel")),
        ])
    }
}

/// Approved full socket plates rooted directly in the two sidewalls.
pub fn valve_seat_datums(rt: &Rt) -> Result<Vec<ValveSeatDatum>> {
    let st = state(rt)?;
    py::sys_path_insert(rt, &py::path_str(&st.hardware.join("printed-parts/valve-seat")))?;
    let seat = st.seat(&rt.import("valve_seat")?)?;
    let mut result = Vec::with_capacity(2);
    for name in ["valve-v-a", "vk-solenoid"] {
        let frame = st.pose(name)?;
        let stock = st.seat_stock(name, &seat)?;
        result.push(ValveSeatDatum {
            name,
            stock_min_world_mm: stock.low,
            stock_max_world_mm: stock.high,
            socket_diameter_mm: seat.socket_diameter,
            socket_floor_backing_mm: seat.wall,
            frame,
        });
    }
    Ok(result)
}

/// `valve_seat_datums()` as the namespace function returns it.
pub fn valve_seat_datums_val(datums: &[ValveSeatDatum]) -> Val {
    py::dict(datums.iter().map(|datum| (datum.name, datum.to_val())))
}

/// `piece.<name>(*args)`, the method read before its arguments are made.
fn then(piece: &Val, name: &str, args: impl FnOnce() -> Result<Vec<Val>>) -> Result<Val> {
    let method = piece.attr(name)?;
    method.call(args()?, vec![])
}

/// One of the recorder's factories, called as the namespace holds it now.
fn factory(st: &State, name: &str, args: Vec<Val>) -> Result<Val> {
    py::call(&st.ns.get(name)?, args)
}

/// The rear wall's relief, wet ports, C14 inlet mounts and keystone, on the back-top piece.
pub fn rear_geometry(rt: &Rt, piece: Val, holds: Val, keep_clear: Val) -> Result<Val> {
    let st = state(rt)?;
    let plan = py::call(&st.function("specification")?, vec![])?.get(py::s("rear_wall"))?;
    let relief = plan.get(py::s("interior_panel_relief"))?;
    let mut piece = then(&piece, "cut", || Ok(vec![factory(&st, "rectangle", vec![relief])?]))?;
    for port in py::snapshot(&plan.get(py::s("wet_ports"))?)?.iter()? {
        piece = then(&piece, "cut", || {
            let radius = Num::of(&port.get(py::s("bore_diameter_mm"))?)?.div(Num::I(2));
            let (x, z) = (port.get(py::s("center_x_mm"))?, port.get(py::s("center_z_mm"))?);
            Ok(vec![factory(&st, "ycylinder", vec![radius.val(), x, z, Val::Float(458.), Val::Float(472.3)])?])
        })?;
    }
    let c14 = plan.get(py::s("dry_openings"))?.get(py::s("c14"))?;
    let [x, y, z] = st.translation("c14-inlet")?;
    piece = then(&piece, "cut", || factory(&st, "c14_rear_cutters", vec![])?.iter())?;
    // Two washer-backed M3 x 10 screws carry the flange on short inserts.
    // Their blind pilots retain 3 mm stock behind the screw-tip relief.
    let seat_y = y.num()? - 3.25;
    let fasteners = c14_fastener_plan();
    let pitch = Num::of(&c14.get(py::s("mount_pitch_mm"))?)?;
    let x = Num::of(&x)?;
    for dx in [pitch.neg().div(Num::I(2)), pitch.div(Num::I(2))] {
        let column = x.add(dx).val();
        piece = then(&piece, "fuse", || {
            let boss = vec![Val::Float(5.), column.clone(), z.clone(), Val::Float(seat_y - fasteners.boss_depth_mm), Val::Float(seat_y)];
            Ok(vec![factory(&st, "ycylinder", boss)?])
        })?;
        piece = then(&piece, "cut", || {
            let pilot = vec![Val::Float(2.), column.clone(), z.clone(), Val::Float(seat_y - fasteners.pilot_depth_mm), Val::Float(seat_y + 0.01)];
            Ok(vec![factory(&st, "ycylinder", pilot)?])
        })?;
    }
    let made = py::unpack(&factory(&st, "keystone_rear_geometry", vec![holds, keep_clear])?, 3)?;
    let piece = py::method(&piece, "fuse", vec![made[0].clone()])?;
    let piece = py::method(&piece, "cut", vec![made[1].clone()])?;
    py::method(&piece, "fuse", vec![made[2].clone()])
}

/// The above-core features on one shell piece: the wiring stock and cuts on each top piece, and on
/// the back-top the rear wall, identification, wall bosses, valve seats and fluid supports.
pub fn apply(rt: &Rt, piece: Val, box_spec: &Val, y_side: &Val, z_side: &Val) -> Result<Val> {
    if text_is("ne", z_side, "top")? {
        return Ok(piece);
    }
    let st = state(rt)?;
    let wiring_module = rt.import("above_core_wiring")?;
    let features = wiring_module.attr("shell_features")?;
    let side = match y_side {
        Val::Str(text) => py::s(format!("{text}-top")),
        _ => interop::binary("add", y_side.clone(), py::s("-top"))?,
    };
    let wiring = py::call(&features, vec![side])?;
    let mut stock = wiring.get(py::s("add"))?;
    if is_not_none(&stock)? && text_is("eq", y_side, "front")? {
        let towers = st.ns.get("stacked_well_towers")?;
        stock = py::call(&towers, vec![stock, box_spec.attr("inner")?])?;
    }
    if is_not_none(&stock)? && text_is("eq", y_side, "back")? {
        let enclosure = rt.import("enclosure")?;
        let tower = st.ns.get("rear_well_tower")?;
        stock = py::call(&tower, vec![stock, py::method(&enclosure, "back_top_ceiling_face", vec![])?])?;
    }
    let mut piece = piece;
    if is_not_none(&stock)? {
        piece = py::method(&piece, "fuse", vec![stock])?;
    }
    if is_not_none(&wiring.get(py::s("cut"))?)? {
        piece = then(&piece, "cut", || Ok(vec![wiring.get(py::s("cut"))?]))?;
    }
    if text_is("ne", y_side, "back")? {
        return Ok(piece);
    }
    let held = box_spec.attr("pack")?.attr("core_holds")?;
    let holds = if held.truthy()? { held } else { Val::Tuple(vec![]) };
    piece = rear_geometry(rt, piece, holds, wiring.get(py::s("cut"))?)?;
    piece = py::method(&rear_identification(rt)?, "apply", vec![piece])?;
    let made = py::unpack(&factory(&st, "wall_bosses", vec![])?, 2)?;
    for feature in made[0].iter()? {
        piece = py::method(&piece, "fuse", vec![feature])?;
    }
    for hole in made[1].iter()? {
        piece = py::method(&piece, "cut", vec![hole])?;
    }
    for feature in py::method(&factory(&st, "valve_seats", vec![])?, "values", vec![])?.iter()? {
        piece = py::method(&piece, "fuse", vec![feature])?;
    }
    for feature in py::method(&factory(&st, "fluid_supports", vec![])?, "values", vec![])?.iter()? {
        piece = py::method(&piece, "fuse", vec![feature])?;
    }
    // Keep the measured inlet opening clear after all integral mounts join.
    then(&piece, "cut", || factory(&st, "c14_rear_cutters", vec![])?.iter())
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("functools", rt.import("functools")?)?;
    ns.set("math", rt.import("math")?)?;
    ns.set("sys", rt.import("sys")?)?;
    rt.import("pathlib")?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("_enclosure_datums", rt.import("_enclosure_datums")?)?;
    _enclosure_datums::install_standins(rt)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?.parent().context("parent")?.to_path_buf();
    ns.set("HERE", Val::Path(here.clone()))?;
    let hardware = here.ancestors().nth(3).context("index out of range")?.to_path_buf();
    py::sys_path_insert(rt, &py::path_str(&hardware.join("manifold-layout")))?;
    let layout = rt.import("above_core")?;
    ns.set("layout", layout.clone())?;
    rt.import("_enclosure_interface")?;
    let flute_depth = rt.member("_enclosure_interface", "flute_depth")?;
    ns.set("flute_depth", flute_depth.clone())?;
    rt.keep(MODULE, State {
        ns: ns.clone(),
        here,
        hardware,
        layout,
        flute_depth: Num::of(&flute_depth)?,
        identification: RefCell::new(None),
        functions: RefCell::new(vec![]),
        poses: RefCell::new(vec![]),
        translations: RefCell::new(vec![]),
        mounts: RefCell::new(vec![]),
        seat: RefCell::new(None),
        seat_stock: RefCell::new(vec![]),
    });

    ns.def(rt, "rear_identification", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        rear_identification(rt)
    })?;
    ns.def(rt, "psu_fastener_plan", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(psu_fastener_plan(rt)?.to_val())
    })?;
    ns.def(rt, "relay_fastener_plan", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(relay_fastener_plan(rt)?.to_val())
    })?;
    ns.def(rt, "wall_mount_datums", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(wall_mount_datums_val(&wall_mount_datums(rt)?))
    })?;
    ns.def(rt, "wall_fastener_bounds", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        let (mounts, lanes) = wall_fastener_bounds(rt)?;
        Ok(wall_fastener_bounds_val(&mounts, &lanes))
    })?;
    let tolerance = Val::Float(1e-05);
    ns.def(rt, "in_wall_fastener_lane", move |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["name", "bounds", "tolerance"], &[])?;
        let (name, bounds) = (b.req("name")?, b.req("bounds")?);
        let tolerance = b.opt("tolerance").unwrap_or_else(|| tolerance.clone());
        in_wall_fastener_lane_val(rt, &name, &bounds, &tolerance)
    })?;
    ns.def(rt, "c14_fastener_plan", |_rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(c14_fastener_plan().to_val())
    })?;
    ns.def(rt, "keystone_land", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(py::ftuple(&keystone_land(rt)?))
    })?;
    ns.def(rt, "gas_check_support_datums", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        gas_check_support_datums(rt)
    })?;
    ns.def(rt, "valve_seat_datums", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(valve_seat_datums_val(&valve_seat_datums(rt)?))
    })?;
    // The panel recorder supplies these graph factories while it records the recipe.
    for name in FACTORIES {
        ns.set(name, Val::None)?;
    }
    let no_holds = Val::Tuple(vec![]);
    ns.def(rt, "rear_geometry", move |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["piece", "holds", "keep_clear"], &[])?;
        let piece = b.req("piece")?;
        let holds = b.opt("holds").unwrap_or_else(|| no_holds.clone());
        let keep_clear = b.opt("keep_clear").unwrap_or(Val::None);
        rear_geometry(rt, piece, holds, keep_clear)
    })?;
    ns.def(rt, "apply", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["piece", "box_spec", "y_side", "z_side"], &[])?;
        let piece = b.req("piece")?;
        let (box_spec, y_side, z_side) = (b.req("box_spec")?, b.req("y_side")?, b.req("z_side")?);
        apply(rt, piece, &box_spec, &y_side, &z_side)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}
