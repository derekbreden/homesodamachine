//! `_above_core_mounts`: cold-core equipment mounts carried by the production above-core
//! datums. Coordinates belong to the top cap and lid before their installed half turn.

use super::above_core::AboveCore;
use super::cad::{self, Cq};
use super::cold_core_interface as core;
use super::*;

pub const NAME: &str = "_above_core_mounts";

/// A deck mount: its explicit boss stations, how far its columns stand proud of the lid, what
/// a screw head bears on, the screw and the least seat.
#[derive(Clone)]
pub struct DeckMount {
    pub points: Vec<[f64; 2]>,
    pub standoff: f64,
    pub seat: f64,
    pub screw: f64,
    pub seat_min: f64,
    /// The five fields as Python holds them.
    pub fields: Vec<Val>,
}

/// One rail room under the pump: its side, its outer face and the two floor planes.
#[derive(Clone)]
pub struct Rail {
    pub side: Num,
    pub outer_y: f64,
    pub planes: [[f64; 3]; 2],
    pub val: Val,
}

/// One removable pump cap over the cradle.
#[derive(Clone)]
pub struct PumpCap {
    pub bore_radius: f64,
    pub station: Val,
    pub stock_half_width: f64,
    pub val: Val,
}

/// `pump_cradle_datums()`.
pub struct PumpCradle {
    pub centre: [f64; 3],
    pub can: Val,
    pub frame: Val,
    pub selected: Val,
    pub seat_bore_radius: f64,
    pub band: (f64, f64),
    pub rails: Vec<Rail>,
    pub caps: Vec<PumpCap>,
    pub val: Val,
}

/// `check_support_datums()`.
pub struct CheckSupport {
    pub centre: [f64; 3],
    pub fixed_band_radius: f64,
    pub root_fore_y: f64,
    pub root_aft_y: f64,
    pub bearing_fore_y: f64,
    pub seat_radius: f64,
    pub half_width: f64,
    pub stock_x_limits: (f64, f64),
    pub tie_window_y: (f64, f64),
    pub tie_window_z: (f64, f64),
    pub tie_roof_rise: f64,
    pub tie_route_z: f64,
    pub val: Val,
}

/// `union_support_datums()['vb-outlet-return']`.
pub struct UnionSupport {
    pub stock_min: [f64; 3],
    pub stock_max: [f64; 3],
    pub bore_origin: [f64; 3],
    pub bore_axis: [f64; 3],
    pub bore_length: f64,
    pub seat_radius: f64,
    pub tie_profile_origin: [f64; 3],
    pub tie_profile_x: [f64; 3],
    pub tie_profile_normal: [f64; 3],
    pub profile: [[f64; 2]; 5],
    pub tie_route_native_down: f64,
    pub centre: [f64; 3],
    pub parent: &'static str,
    pub implemented: bool,
    pub val: Val,
}

/// One segment of a nominal tie route.
#[derive(Clone)]
pub enum TieSegment {
    Line {
        points: [[f64; 3]; 2],
        wide_axis: [f64; 3],
    },
    Arc {
        points: [[f64; 3]; 3],
        radius: f64,
        sweep: f64,
        wide_axis: [f64; 3],
    },
}

impl TieSegment {
    fn to_val(&self) -> Val {
        match self {
            TieSegment::Line { points, wide_axis } => dict! {
                "kind" => "line",
                "points_mm" => list(points),
                "wide_axis" => *wide_axis,
            },
            TieSegment::Arc {
                points,
                radius,
                sweep,
                wide_axis,
            } => dict! {
                "kind" => "arc",
                "points_mm" => list(points),
                "radius_mm" => *radius,
                "sweep_degrees" => *sweep,
                "wide_axis" => *wide_axis,
            },
        }
    }
}

/// A tie route: its segments and the strip it is cut from.
pub struct TieRoute {
    pub segments: Vec<TieSegment>,
    pub length: f64,
    pub val: Val,
}

/// `valve_support_datums(name, face_z)`.
pub struct ValveSupport {
    pub bearing_min: [Num; 3],
    pub bearing_max: [Num; 3],
    pub root_min: [Num; 3],
    pub root_max: [Num; 3],
    pub val: Val,
}

pub struct State {
    pub hw: PathBuf,
    path: PathBuf,
    deck_mount_type: Val,
    deck_mounts: RefCell<Option<Rc<Vec<(String, DeckMount)>>>>,
    pump: RefCell<Option<Rc<PumpCradle>>>,
    straight: RefCell<Vec<(String, Val)>>,
    fill_features: RefCell<Vec<(Val, Val)>>,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let hw = ancestor(&resolve(&rt.file(NAME)), "hardware")?;
        let paths = [
            hw.join("manifold-layout"),
            hw.join("printed-parts").join("valve-seat"),
            hw.join("printed-parts").join("electronics").join("pcba-tray"),
            hw.join("reference").join("meanwell-irm90"),
            hw.join("reference").join("g-ganen-pump").join("installation"),
            hw.join("reference").join("neofit-achv44-check"),
            hw.join("reference").join("digiten-flow-sensor"),
            hw.join("reference").join("neofit-stem-elbow"),
            hw.join("printed-parts").join("cold-core").join("reservoir"),
        ];
        for path in &paths {
            rt.sys_path_insert(0, path)?;
        }
        AboveCore::get(rt)?;
        let deck_mount_type =
            rt.namedtuple("DeckMount", "points standoff seat screw seat_min", NAME)?;
        Ok(Self {
            hw,
            path: paths[paths.len() - 1].clone(),
            deck_mount_type,
            deck_mounts: RefCell::new(None),
            pump: RefCell::new(None),
            straight: RefCell::new(vec![]),
            fill_features: RefCell::new(vec![]),
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}
fn ac(rt: &Runtime) -> Result<Rc<AboveCore>> {
    AboveCore::get(rt)
}

/// A 3×3 rotation as Python numbers: integer entries stay integers through `_multiply`.
pub type Rot = [[Num; 3]; 3];
pub fn rot_of(v: &Val) -> Result<Rot> {
    let rows = v.list()?;
    ensure!(rows.len() == 3, "rotation rows");
    let mut out = [[Num::I(0); 3]; 3];
    for (i, row) in rows.iter().enumerate() {
        out[i] = <[Num; 3]>::from_val(row)?;
    }
    Ok(out)
}
pub fn rot_val(r: &Rot) -> Val {
    Val::Tuple(r.iter().map(|row| row.to_val()).collect())
}

fn multiply(a: &Rot, b: &Rot) -> Rot {
    let mut out = [[Num::I(0); 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            let mut total = Num::I(0);
            for k in 0..3 {
                total = total.add(a[i][k].mul(b[k][j]));
            }
            out[i][j] = total;
        }
    }
    out
}

/// `component_in_cap(name)`: a native component frame carried into the uninstalled cap frame.
pub fn component_in_cap(rt: &Runtime, name: &str) -> Result<(Rot, [f64; 3])> {
    let a = ac(rt)?;
    let frame = a.pose(name)?;
    let cap = a.cap_lid_pose()?;
    let c = rot_of(&cap.k("rotation")?)?;
    let transposed: Rot = std::array::from_fn(|i| std::array::from_fn(|j| c[j][i]));
    let rotation = multiply(&transposed, &rot_of(&frame.k("rotation")?)?);
    let translation = a.world_to_cap(frame.k("translation_mm")?)?;
    Ok((rotation, translation))
}
fn frame_val(frame: &(Rot, [f64; 3])) -> Val {
    dict! {"rotation" => rot_val(&frame.0), "translation_mm" => frame.1}
}

/// `lid_face_z()`: the plain lid bearing face in the lid's native frame.
pub fn lid_face_z(rt: &Runtime) -> Result<f64> {
    let a = ac(rt)?;
    Ok(a.world_to_cap([0.0, 0.0, a.cap_face_z()?])?[2])
}

fn cadlib(rt: &Runtime) -> Result<()> {
    rt.sys_path_insert(0, &state(rt)?.hw.join("printed-parts").join("cadlib"))
}

/// `va_feed_snap()`: the full-root C2 seat for the V-A feed, in appliance coordinates.
pub fn va_feed_snap(rt: &Runtime) -> Result<Val> {
    cadlib(rt)?;
    let tube_clip = rt.pya("route_snap", "tube_clip")?;
    let a = ac(rt)?;
    let datum = a.spec().k("fore_routes")?.k("va_feed_snap")?;
    let centre = datum.k("centre_world_mm")?;
    tube_clip.ck(
        args![
            centre,
            datum.k("along_world")?,
            [0.0, 0.0, 1.0],
            centre.i(2)?.f()? - a.cap_face_z()?
        ],
        kw![
            "tube_od" => 6.35, "bore_diameter" => 6.35, "span" => 8.0, "wing" => 2.4,
            "print_up" => [0.0, 0.0, 1.0],
        ],
    )
}

/// `flavor_snaps()`: open flavor seats; the crossover's filled root joins V-B's wall.
pub fn flavor_snaps(rt: &Runtime) -> Result<Val> {
    let cq = Cq::new(rt)?;
    rt.sys_path_insert(0, &state(rt)?.hw.join("printed-parts/cadlib"))?;
    let tube_clip = rt.pya("route_snap", "tube_clip")?;
    let a = ac(rt)?;
    let result = Dict::new();
    let mut result = result;
    for (name, centre, axis) in [
        ("flavor-a", [26.5, 266.0, 296.0], [1.0, 0.0, 0.0]),
        ("flavor-b", [35.0, 414.0, 264.0], [0.0, 1.0, 0.0]),
    ] {
        let clip = tube_clip.ck(
            args![centre, axis, [0.0, 0.0, 1.0], centre[2] - a.cap_face_z()?],
            kw![
                "tube_od" => 4.0, "bore_diameter" => 4.1, "span" => 8.0, "wing" => 1.52,
                "print_up" => [0.0, 0.0, 1.0],
            ],
        )?;
        result.set(name, clip);
    }
    let wall = valve_support_datums(rt, "valve-v-b", None)?;
    let (x0, y0) = (wall.root_min[0].f(), wall.root_max[1].f() - 0.1);
    let z0 = a.cap_face_z()? - 0.1;
    let root_front = 266.0 - (4.1 / 2.0 + 1.52);
    let front = root_front + 0.1;
    let bridge = cq
        .workplane(args!["YZ"], vec![])?
        .mk("workplane", vec![], kw!["offset" => x0])?
        .m(
            "polyline",
            args![vec![
                [y0, z0],
                [front, z0],
                [front, 296.0 + front - root_front],
                [y0, 296.0 + y0 - root_front],
            ]],
        )?
        .m("close", vec![])?
        .m("extrude", args![30.5 - x0])?
        .m("val", vec![])?;
    let first = result.0[0].1.clone();
    result.set("flavor-a", cad::clean(&cad::fuse(&first, args![bridge])?)?);
    Ok(result.val())
}

fn wiring_paths(rt: &Runtime) -> Result<()> {
    let hw = &state(rt)?.hw;
    rt.sys_path_prepend(&[
        hw.parent().unwrap_or(hw).to_owned(),
        hw.join("printed-parts").join("cadlib"),
    ])
}

/// `manifold_cable_bank()`: one filled J1/J2 cable bank on the lid, in appliance coordinates.
pub fn manifold_cable_bank(rt: &Runtime) -> Result<Val> {
    wiring_paths(rt)?;
    let site_of = rt.pya("hardware.wiring.installed.retainers", "manifold_bank_site")?;
    let bank = rt.pya("route_snap", "cable_bank")?;
    let site = site_of.c(vec![])?;
    let keywords = ["seat_depth", "seat_heights", "span", "stock", "beak"]
        .iter()
        .map(|k| Ok((k.to_string(), site.k(k)?)))
        .collect::<Result<Vec<_>>>()?;
    bank.ck(args![site.k("origin")?], keywords)
}

/// `rear_level_cable_hook()`: one filled lid hook for the Reservoir A leads.
pub fn rear_level_cable_hook(rt: &Runtime) -> Result<Val> {
    wiring_paths(rt)?;
    let site_of = rt.pya("hardware.wiring.installed.retainers", "rear_level_hook_site")?;
    let hook = rt.pya("route_snap", "floor_cable_hook")?;
    let site = site_of.c(vec![])?;
    let keywords = ["seat_depth", "seat_height", "span", "stock", "beak"]
        .iter()
        .map(|k| Ok((k.to_string(), site.k(k)?)))
        .collect::<Result<Vec<_>>>()?;
    hook.ck(args![site.k("origin")?], keywords)
}

/// `mounting_points(name, holes)`: native mounting-hole points at their cap XY stations.
pub fn mounting_points(rt: &Runtime, name: &str, holes: &Val) -> Result<Vec<[f64; 2]>> {
    let a = ac(rt)?;
    let frame = a.pose(name)?;
    holes
        .list()?
        .iter()
        .map(|hole| {
            let (x, y): (Val, Val) = FromVal::from_val(hole)?;
            let world = a.point(&frame, (x, y, 0.0))?;
            Ok(xy(a.world_to_cap(world)?))
        })
        .collect()
}

fn standoff(rt: &Runtime, name: &str) -> Result<f64> {
    let rounded = round_to(component_in_cap(rt, name)?.1[2] - lid_face_z(rt)?, 4);
    Ok(if rounded == 0.0 { 0.0 } else { rounded })
}

/// `deck_mounts()`: PCB posts are integral to the lid and take full RX-M3x5.7 inserts.
pub fn deck_mounts(rt: &Runtime) -> Result<Rc<Vec<(String, DeckMount)>>> {
    let s = state(rt)?;
    if let Some(held) = s.deck_mounts.borrow().as_ref() {
        return Ok(held.clone());
    }
    let pcb = rt.py("pcba_tray")?;
    let points = mounting_points(rt, "pcba", &pcb.a("board")?.a("holes")?)?;
    let standoff = standoff(rt, "pcba")?;
    let thickness = pcb.a("_thickness")?;
    let seat_min = pcb.a("_thickness")?;
    let fields = vec![
        Val::Tuple(points.iter().map(ToVal::to_val).collect()),
        Val::Float(standoff),
        thickness.clone(),
        Val::Float(8.0),
        seat_min.clone(),
    ];
    let mount = DeckMount {
        points,
        standoff,
        seat: thickness.f()?,
        screw: 8.0,
        seat_min: seat_min.f()?,
        fields,
    };
    let held = Rc::new(vec![("pcba".to_owned(), mount)]);
    *s.deck_mounts.borrow_mut() = Some(held.clone());
    Ok(held)
}
fn deck_mounts_val(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let mut d = Dict::new();
    for (name, mount) in deck_mounts(rt)?.iter() {
        d.set(name.as_str(), s.deck_mount_type.c(mount.fields.clone())?);
    }
    Ok(d.val())
}

struct Section {
    x: f64,
    vertices: Vec<[f64; 3]>,
}
fn sections_of(pump: &Val) -> Result<Vec<Section>> {
    pump.k("casing_sections")?
        .list()?
        .iter()
        .map(|row| {
            Ok(Section {
                x: row.kf("x_mm")?,
                vertices: row
                    .k("vertices_mm")?
                    .list()?
                    .iter()
                    .map(|p| p.v3())
                    .collect::<Result<_>>()?,
            })
        })
        .collect()
}

/// `_pump_section_points(pump, first, last)`: observed barrel profiles with interpolated ends.
fn pump_section_points(sections: &[Section], first: f64, last: f64) -> Result<Vec<[f64; 3]>> {
    let mut points: Vec<[f64; 3]> = sections
        .iter()
        .filter(|row| first <= row.x && row.x <= last)
        .flat_map(|row| row.vertices.iter().copied())
        .collect();
    for end in [first, last] {
        let (a, b) = sections
            .iter()
            .zip(&sections[1..])
            .find(|(a, b)| a.x <= end && end <= b.x)
            .context("StopIteration: no casing section brackets the band end")?;
        let share = (end - a.x) / (b.x - a.x);
        for (p, q) in a.vertices.iter().zip(&b.vertices) {
            points.push(std::array::from_fn(|i| p[i] + (q[i] - p[i]) * share));
        }
    }
    Ok(points)
}

fn axis_z(origin: &[f64; 3], axis: &[f64; 3], x: f64) -> f64 {
    origin[2] + axis[2] * (x - origin[0]) / axis[0]
}
fn radial(p: &[f64; 3], origin: &[f64; 3], axis: &[f64; 3]) -> f64 {
    hypot(&[p[1] - origin[1], p[2] - axis_z(origin, axis, p[0])])
}
/// `max(first, *rest)`: the first of equals, and Python's error on a lone number.
fn max_of(first: f64, rest: Vec<f64>) -> Result<f64> {
    ensure!(!rest.is_empty(), "TypeError: 'float' object is not iterable");
    Ok(rest.into_iter().fold(first, pmax))
}

/// `pump_cradle_datums()`: the continuous motor clip, solid end lands and open rail rooms.
pub fn pump_cradle_datums(rt: &Runtime) -> Result<Rc<PumpCradle>> {
    let s = state(rt)?;
    if let Some(held) = s.pump.borrow().as_ref() {
        return Ok(held.clone());
    }
    let parts = rt.py("above_core_parts")?;
    let fits = rt.py("fits")?;
    let rear_snaps = rt.py("rear_snaps")?;
    let pump = own(
        &parts
            .m(
                "_module",
                args!["bearing_pump", "reference/g-ganen-pump/g_ganen_pump.py"],
            )?
            .m("parameters", vec![])?,
    )?;
    let a = ac(rt)?;
    let selected = a.spec().k("pump_mount")?;
    let band = selected.k("motor_band_native_x_mm")?;
    let (first, last): (Num, Num) = FromVal::from_val(&band)?;
    let (first_f, last_f) = (first.f(), last.f());
    let sections = sections_of(&pump)?;
    let points = pump_section_points(&sections, first_f, last_f)?;
    let can = pump.k("motor_can_envelope")?;
    let running = fits.a("running")?.f()?;
    let slip = fits.a("slip")?.f()?;
    let can_radius = can.kf("radius_mm")?;
    let origin = can.kv3("axis_point_mm")?;
    let axis = can.kv3("axis_direction")?;
    let underside = pump.k("rigid_underside")?;
    let mut cover_sides: Vec<Vec<f64>> = vec![];
    let lowest = fmin(points.iter().map(|p| p[2]));
    for side in underside.k("wire_cover_side_profiles")?.list()? {
        let [a, b, c] = side.k("side_plane")?.kv3("coefficients")?;
        let mut row = vec![];
        for x in [first_f, last_f] {
            for z in [lowest, origin[2] + can_radius] {
                row.push(a * x + b * z + c);
            }
        }
        cover_sides.push(row);
    }
    let all = || cover_sides.iter().flatten().copied();
    let cover_room = (fmin(all()) - 2.0 * running, fmax(all()) + 2.0 * running);
    let mut rails = vec![];
    for rail in underside.k("rail_face_planes")?.list()? {
        let planes = rail.k("planes")?;
        let plane = |name: &str| -> Result<Val> { planes.k(name)?.k("z_ax_plus_by_plus_c") };
        let (av, bv, cv) = (plane("outer_upper")?, plane("outer_lower")?, plane("inner_return")?);
        let (pa, pb, pc) = (av.v3()?, bv.v3()?, cv.v3()?);
        let corners: Vec<f64> = [first_f, last_f]
            .iter()
            .map(|x| ((pb[0] - pa[0]) * x + pb[2] - pa[2]) / (pa[1] - pb[1]))
            .collect();
        let side = Num::from_val(&rail.k("side")?)?;
        let outer = if side.f() > 0.0 {
            fmax(corners.iter().copied()) + running
        } else {
            fmin(corners.iter().copied()) - running
        };
        let val = dict! {
            "side" => side, "outer_y_mm" => outer,
            "floor_planes" => Val::Tuple(vec![bv.clone(), cv.clone()]),
        };
        rails.push(Rail {
            side,
            outer_y: outer,
            planes: [pb, pc],
            val,
        });
    }
    let above = |p: &[f64; 3]| p[2] >= axis_z(&origin, &axis, p[0]);
    let barrel_radius = max_of(
        can_radius,
        points
            .iter()
            .filter(|p| above(p))
            .map(|p| radial(p, &origin, &axis))
            .collect(),
    )?;
    let in_open_room = |p: &[f64; 3]| {
        if cover_room.0 <= p[1] && p[1] <= cover_room.1 {
            return true;
        }
        for rail in &rails {
            let side = rail.side.f();
            let along = p[1] * side;
            if !(0.0 <= along && along <= rail.outer_y * side) {
                continue;
            }
            if rail.planes.iter().all(|[a, b, c]| {
                p[2] >= a * p[0] + b * p[1] + c
                    - running * (1.0 + a * a + b * b).sqrt()
                    - 1.0e-8
            }) {
                return true;
            }
        }
        false
    };
    let seat_radius = max_of(
        barrel_radius,
        points
            .iter()
            .filter(|p| !in_open_room(p))
            .map(|p| radial(p, &origin, &axis))
            .collect(),
    )? + running;
    let middle = (first_f + last_f) / 2.0;
    let centre = [middle, origin[1], axis_z(&origin, &axis, middle)];
    let frame = a.pose("g-ganen-pump")?;
    let [cx, cy, cz] = a.point(&frame, centre)?;
    let snap_band = selected.k("snap_band_native_x_mm")?;
    let bands: Vec<(Num, Num)> = vec![FromVal::from_val(&snap_band)?];
    let mut radii = vec![];
    for (lo, hi) in &bands {
        let upper = pump_section_points(&sections, lo.f(), hi.f())?;
        radii.push(
            max_of(
                can_radius,
                upper
                    .iter()
                    .filter(|p| above(p))
                    .map(|p| radial(p, &origin, &axis))
                    .collect(),
            )? + slip,
        );
    }
    let wall = rear_snaps.a("WALL")?.f()?;
    let mut neck_terms = radii.clone();
    neck_terms.extend(rails.iter().map(|r| r.outer_y.abs()));
    let neck = fmax(neck_terms) + wall;
    let common = Dict::new()
        .with("centre_world_mm", [cx, cy, cz])
        .with("can", &can)
        .with("frame", &frame)
        .with("seat_bore_radius_mm", seat_radius)
        .with("band_native_x_mm", (first, last))
        .with("cover_room_native_y_mm", cover_room)
        .with(
            "rail_rooms",
            Val::list(rails.iter().map(|r| r.val.clone()).collect()),
        )
        .with("selected", &selected);
    let fy = Num::from_val(&frame.k("translation_mm")?.i(1)?)?;
    let mut caps = vec![];
    for ((lo, hi), radius) in bands.iter().zip(&radii) {
        let station = rear_snaps.a("station")?.ck(
            args![cx, neck, fy.add(*lo), fy.add(*hi)],
            kw!["split" => 0.0, "tool_angle_degrees" => -65.0, "tool_end_stock" => 10.0],
        )?;
        let outer = station.k("outer")?;
        station.set(
            "tool_outer_edges".into(),
            Val::Tuple(vec![Val::Float(cx - outer.f()?), Val::None]),
        )?;
        let ports = rear_snaps.a("receiver_tool_ports")?.c(args![station])?;
        station.set("tool_ports".into(), ports)?;
        let val = common
            .clone()
            .with("bore_radius_mm", *radius)
            .with("snap_station", &station)
            .with("cap_band_native_x_mm", (*lo, *hi))
            .with(
                "pocket_band_native_x_mm",
                (lo.f() - running, hi.f() + running),
            )
            .with("stock_half_width_mm", &outer)
            .val();
        caps.push(PumpCap {
            bore_radius: *radius,
            station,
            stock_half_width: outer.f()?,
            val,
        });
    }
    let mut whole = Dict(hsm_documents::interop::entries_of(&caps[0].val)?);
    whole.set(
        "caps",
        Val::list(caps.iter().map(|c| c.val.clone()).collect()),
    );
    whole.set(
        "end_stock_mm",
        (
            bands[0].0.f() - running - first_f,
            last_f - bands[bands.len() - 1].1.f() - running,
        ),
    );
    let held = Rc::new(PumpCradle {
        centre: [cx, cy, cz],
        can,
        frame,
        selected,
        seat_bore_radius: seat_radius,
        band: (first_f, last_f),
        rails,
        caps,
        val: whole.val(),
    });
    *s.pump.borrow_mut() = Some(held.clone());
    Ok(held)
}

fn pump_cap_to_world(shape: &Val, centre: [f64; 3]) -> Result<Val> {
    let [cx, _cy, cz] = centre;
    cad::translate(
        &cad::rotate(shape, [cx, 0.0, 0.0], [cx, 1.0, 0.0], 180.0)?,
        [0.0, 0.0, cz],
    )
}

fn pump_motor_room(rt: &Runtime, d: &PumpCradle, radius: f64) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let a = ac(rt)?;
    let axis = d.can.kv3("axis_direction")?;
    let origin = d.can.kv3("axis_point_mm")?;
    let (first, last) = d.band;
    let point = [
        first - 1.0,
        origin[1],
        origin[2] + axis[2] * (first - 1.0 - origin[0]) / axis[0],
    ];
    cq.cylinder(
        radius,
        (last - first + 2.0) / axis[0],
        a.point(&d.frame, point)?,
        a.vector(&d.frame.k("rotation")?, d.can.k("axis_direction")?)?,
    )
}

/// `pump_snap_cap(index)`: a filled box half-pipe with a thick crown and two spring leaves.
pub fn pump_snap_cap(rt: &Runtime, index: i64) -> Result<Val> {
    Cq::new(rt)?;
    let fits = rt.py("fits")?;
    let datums = pump_cradle_datums(rt)?;
    let d = datums
        .caps
        .get(index as usize)
        .context("pump cap index")?;
    let s = &d.station;
    let rear_snaps = rt.py("rear_snaps")?;
    let (c, wide) = (s.kf("axis_x")?, s.kf("outer")?);
    let roof = -(d.bore_radius + datums.selected.kf("cap_arch_wall_mm")?);
    let edge = datums.selected.kf("cap_east_roof_half_width_mm")?;
    let section = rear_snaps
        .a("cap_section")?
        .c(args![s, -fits.a("slip")?.f()?, roof])?;
    let segments = section.k("segments")?;
    segments.set(
        Val::Int(-2),
        dict! {"line" => ((c + wide, roof), (c - edge, roof))},
    )?;
    segments.set(
        Val::Int(-1),
        dict! {"line" => ((c - edge, roof), (c - wide, s.k("root")?))},
    )?;
    let blank = rear_snaps.a("section_solid")?.c(args![section])?;
    let room = pump_motor_room(rt, &datums, d.bore_radius)?;
    cad::clean(&cad::cut(&pump_cap_to_world(&blank, datums.centre)?, args![room])?)
}

/// `pump_snap_printable(index)`: axial end on the bed.
pub fn pump_snap_printable(rt: &Runtime, index: i64) -> Result<Val> {
    let shape = cad::rotate(
        &pump_snap_cap(rt, index)?,
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        90.0,
    )?;
    let b = shape.m("BoundingBox", vec![])?;
    let g = |k: &str| b.a(k)?.f();
    cad::translate(
        &shape,
        [
            -(g("xmin")? + g("xmax")?) / 2.0,
            -(g("ymin")? + g("ymax")?) / 2.0,
            -g("zmin")?,
        ],
    )
}

/// `pump_cradle()`: one broad lid-rooted block with a straight channel and rail stops.
pub fn pump_cradle(rt: &Runtime) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let rear_snaps = rt.py("rear_snaps")?;
    let d = pump_cradle_datums(rt)?;
    let a = ac(rt)?;
    let [cx, _cy, cz] = d.centre;
    let (first, _last) = d.band;
    let fy = d.frame.k("translation_mm")?.i(1)?.f()?;
    let face = a.cap_face_z()?;
    let selected = &d.selected;
    let stops = selected.k("rail_stop_native_x_mm")?.list()?;
    let (fore, rear) = (stops[0].v2()?, stops[1].v2()?);
    let stock_half_width = d.caps[0].stock_half_width;
    let wide = stock_half_width + 3.0;
    let half = 24.81;
    let mut body = cq.make_box(
        [2.0 * wide, rear[1] - fore[0], cz - face + 0.1],
        [cx - wide, fy + fore[0], face - 0.1],
    )?;
    body = cad::cut(
        &body,
        args![cq.make_box(
            [2.0 * half, rear[1] - fore[0] + 0.2, cz - face + 1.0],
            [cx - half, fy + fore[0] - 0.1, face],
        )?],
    )?;
    let running = rt.pya("fits", "running")?.f()?;
    for rail in &d.rails {
        let [a_, b_, c0] = rail.planes[0];
        let c_ = c0 - running * (1.0 + a_ * a_ + b_ * b_).sqrt();
        let mut profiles = vec![];
        for x in [fore[1], rear[0]] {
            let outer = rail.outer_y;
            let near = rail.side.f() * half;
            let yz = [
                (outer, a_ * x + b_ * outer + c_),
                (near, a_ * x + b_ * near + c_),
                (near, 100.0),
                (outer, 100.0),
            ];
            let corners: Vec<[f64; 3]> = yz.iter().map(|(y, z)| [x, *y, *z]).collect();
            profiles.push(cq.polygon(&corners)?);
        }
        let room = cad::moved(&cq.ruled_loft(profiles)?, &a.frame_location(&d.frame)?)?;
        body = cad::cut(&body, args![room])?;
    }
    let tz = d.frame.k("translation_mm")?.i(2)?.f()?;
    let head = selected.kf("rail_stop_native_z_mm")?;
    let slope = (cz - tz - head) / first;
    for (xa, xb) in [(fore[0] - 0.1, fore[1]), (fore[1], first)] {
        let mut profiles = vec![];
        for x in [xa, xb] {
            let (z, y) = (tz + head + slope * pmax(x, fore[1]), fy + x);
            profiles.push(cq.polygon(&[
                [cx - wide - 0.1, y, z],
                [cx + wide + 0.1, y, z],
                [cx + wide + 0.1, y, cz + 1.0],
                [cx - wide - 0.1, y, cz + 1.0],
            ])?);
        }
        body = cad::cut(&body, args![cq.ruled_loft(profiles)?])?;
    }
    for cap in &d.caps {
        let mut station = Dict(cap.station.items()?);
        station.set("outer", wide);
        for pocket in rear_snaps.a("pockets")?.c(args![station])?.list()? {
            body = cad::cut(&body, args![pump_cap_to_world(&pocket, d.centre)?])?;
        }
    }
    let (east, aft) = (cx + wide, fy + rear[1]);
    let cap_end = fmax(
        d.caps
            .iter()
            .map(|cap| cap.station.kf("y1"))
            .collect::<Result<Vec<_>>>()?,
    ) + running;
    let clearance = cq.make_box(
        [
            east - (cx + stock_half_width) + 0.1,
            aft - cap_end + 0.1,
            cz - face + 0.4,
        ],
        [cx + stock_half_width, cap_end, face - 0.2],
    )?;
    body = cad::cut(&body, args![clearance])?;
    cad::clean(&body)
}

/// `pump_lid_clearance()`: one straight shallow lid recess for the molded cover and head.
pub fn pump_lid_clearance(rt: &Runtime) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let d = pump_cradle_datums(rt)?;
    let a = ac(rt)?;
    let cx = d.centre[0];
    let fy = d.frame.k("translation_mm")?.i(1)?.f()?;
    let fore = d.selected.kf("cover_channel_fore_native_x_mm")?;
    let aft = d.selected.k("rail_stop_native_x_mm")?.i(1)?.i(1)?.f()?;
    let face = a.cap_face_z()?;
    let depth = d.selected.kf("cover_channel_recess_mm")?;
    cq.make_box(
        [49.62, aft - fore + 0.2, depth + 0.1],
        [cx - 24.81, fy + fore - 0.1, face - depth],
    )
}

/// `valve_support_datums(name, face_z)`.
pub fn valve_support_datums(rt: &Runtime, name: &str, face_z: Option<f64>) -> Result<ValveSupport> {
    let seat = rt.py("valve_seat")?;
    let core = core::base(rt)?;
    let a = ac(rt)?;
    let frame = a.pose(name)?;
    let f = |k: &str| seat.a(k)?.f();
    let limits = [
        [-f("seat_half_x")?, f("seat_half_x")?],
        [-f("seat_half_y")?, f("seat_half_y")?],
        [f("socket_floor_z")? - f("wall")?, f("seat_top_z")?],
    ];
    let mut corners = vec![];
    for x in limits[0] {
        for y in limits[1] {
            for z in limits[2] {
                corners.push(a.point(&frame, [x, y, z])?);
            }
        }
    }
    let low3: [f64; 3] = std::array::from_fn(|i| fmin(corners.iter().map(|p| p[i])));
    let high3: [f64; 3] = std::array::from_fn(|i| fmax(corners.iter().map(|p| p[i])));
    let mut low: [Num; 3] = low3.map(Num::F);
    let mut high: [Num; 3] = high3.map(Num::F);
    if name == "valve-v-b" {
        let bounds = a.spec().k("vb_mount")?.k("seat_wall_bounds_mm")?;
        low = [Num::from_val(&bounds.i(0)?.i(0)?)?, low[1], low[2]];
        high = [
            high[0],
            high[1],
            high[2].max(Num::from_val(&bounds.i(1)?.i(2)?)?),
        ];
    }
    let face = match face_z {
        None => Num::from_val(&a.spec().k("cap_face_z_mm")?)?,
        Some(z) => Num::F(a.point(&a.cap_lid_pose()?, [0.0, 0.0, z])?[2]),
    };
    let half = core.outer_shell_y_length / 2.0;
    let mut root_high = [Num::F(half).min(high[0]), high[1], low[2]];
    let root_min = [Num::F(-half).max(low[0]), low[1], face];
    let mut data = Dict::new()
        .with("bearing_min_world_mm", low)
        .with("bearing_max_world_mm", high)
        .with("root_min_world_mm", root_min)
        .with("socket_backing_mm", seat.a("wall")?);
    if name == "valve-v-a" || name == "vk-solenoid" {
        let elbow = rt.py("neofit_stem_elbow")?;
        let valve = seat.a("valve")?;
        let port_y = a.point(&frame, (0.0, 0.0, valve.a("port_center_z")?))?[1];
        let slip = seat.a("fits")?.a("slip")?;
        let aft = port_y
            - pmax(
                valve.a("port_radius")?.f()?,
                elbow.a("COLLAR_OD")?.f()? / 2.0,
            )
            - slip.f()?;
        root_high = [root_high[0], Num::F(aft), root_high[2]];
        data.set("port_throat_aft_world_y_mm", aft);
        data.set("port_throat_clearance_mm", slip);
    }
    data.set("root_max_world_mm", root_high);
    data.set("root_depth_mm", root_high[1].sub(low[1]));
    Ok(ValveSupport {
        bearing_min: low,
        bearing_max: high,
        root_min,
        root_max: root_high,
        val: data.val(),
    })
}

/// `valve_support(name, face_z)`.
pub fn valve_support(rt: &Runtime, name: &str, face_z: Option<f64>) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let seat = rt.py("valve_seat")?;
    let data = valve_support_datums(rt, name, face_z)?;
    let block = |low: &[Num; 3], high: &[Num; 3]| {
        let size: [f64; 3] = std::array::from_fn(|i| high[i].sub(low[i]).f());
        cq.make_box(size, low.map(Num::f))
    };
    let wall = cad::fuse(
        &block(&data.bearing_min, &data.bearing_max)?,
        args![block(&data.root_min, &data.root_max)?],
    )?;
    let location = ac(rt)?.location(name)?;
    let sockets = cad::moved(&seat.m("build_sockets", vec![])?.m("val", vec![])?, &location)?;
    let half_y = seat.a("seat_half_y")?.f()?;
    let channel = cad::moved(
        &seat
            .m("build_port_channel", args![2.0 * half_y + 2.0])?
            .m("val", vec![])?,
        &location,
    )?;
    world_shape_in_cap(rt, &cad::clean(&cad::cut(&wall, args![sockets, channel])?)?)
}

fn check_bearing_station(rt: &Runtime) -> Result<([f64; 3], Val, f64, f64)> {
    let check = rt.py("neofit_achv44_check")?;
    let (first, last, radius): (f64, f64, Val) =
        FromVal::from_val(&check.m("bearing_band", vec![])?)?;
    let (inlet, outward): ([f64; 3], [f64; 3]) = FromVal::from_val(&check.m("inlet", vec![])?)?;
    let distance = (first + last) / 2.0;
    let point = std::array::from_fn(|i| inlet[i] - distance * outward[i]);
    Ok((point, radius, first, last))
}

/// `check_anchor()`.
pub fn check_anchor(rt: &Runtime) -> Result<Val> {
    let (native, radius, _first, _last) = check_bearing_station(rt)?;
    let frame = frame_val(&component_in_cap(rt, "discharge-chain")?);
    let point = ac(rt)?.point(&frame, native)?;
    Ok(Val::Tuple(vec![
        xy(point).to_val(),
        radius,
        Val::Float(point[2] - lid_face_z(rt)?),
    ]))
}

/// `check_support_datums()`.
pub fn check_support_datums(rt: &Runtime) -> Result<CheckSupport> {
    let fits = rt.py("fits")?;
    let core = core::state(rt)?;
    rt.py("g_ganen_installation")?;
    let check = rt.py("neofit_achv44_check")?;
    let (first, last, band_radius): (f64, f64, f64) =
        FromVal::from_val(&check.m("bearing_band", vec![])?)?;
    let bearing_first = first + 0.5;
    let bearing_last = bearing_first + core.cap_anchor_len;
    let (inlet, outward): ([f64; 3], [f64; 3]) = FromVal::from_val(&check.m("inlet", vec![])?)?;
    let native: [f64; 3] =
        std::array::from_fn(|i| inlet[i] - (bearing_first + bearing_last) / 2.0 * outward[i]);
    let a = ac(rt)?;
    let centre = a.point(&a.pose("discharge-chain")?, native)?;
    let radius = band_radius + fits.a("slip")?.f()?;
    let fore = centre[1] - core.cap_anchor_len / 2.0;
    let aft = centre[1] + core.cap_anchor_len / 2.0;
    let slot_top = centre[2] - radius - 3.0;
    let out = CheckSupport {
        centre,
        fixed_band_radius: band_radius,
        root_fore_y: fore,
        root_aft_y: aft,
        bearing_fore_y: fore,
        seat_radius: radius,
        half_width: radius + 3.0,
        stock_x_limits: (centre[0], centre[0] + radius + 3.0),
        tie_window_y: (centre[1] - 1.4, centre[1] + 1.4),
        tie_window_z: (slot_top - 3.2, slot_top),
        tie_roof_rise: 1.4,
        tie_route_z: slot_top - 2.0,
        val: Val::None,
    };
    let val = dict! {
        "centre_world_mm" => centre,
        "fixed_band_from_inlet_mm" => (first, last),
        "bearing_from_inlet_mm" => (bearing_first, bearing_last),
        "fixed_band_radius_mm" => band_radius,
        "root_fore_y_mm" => fore,
        "root_aft_y_mm" => aft,
        "bearing_fore_y_mm" => fore,
        "seat_radius_mm" => radius,
        "half_width_mm" => out.half_width,
        "stock_x_limits_world_mm" => out.stock_x_limits,
        "tie_window_y_mm" => out.tie_window_y,
        "tie_window_z_mm" => out.tie_window_z,
        "tie_roof_rise_mm" => 1.4,
        "tie_route_z_mm" => out.tie_route_z,
        "open_direction" => "west-and-up",
        "wall_mm" => 3.0,
    };
    Ok(CheckSupport { val, ..out })
}

/// `check_support()`.
pub fn check_support(rt: &Runtime) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let data = check_support_datums(rt)?;
    let a = ac(rt)?;
    let [x, _y, z] = data.centre;
    let (low_x, high_x) = data.stock_x_limits;
    let face = a.cap_face_z()?;
    let root = cq.make_box(
        [
            high_x - low_x,
            data.root_aft_y - data.root_fore_y,
            z - face + 0.15,
        ],
        [low_x, data.root_fore_y, face - 0.15],
    )?;
    let (y0, y1) = data.tie_window_y;
    let (z0, z1) = data.tie_window_z;
    let plane = cq.plane(kw![
        "origin" => (low_x - 0.1, 0.0, 0.0),
        "xDir" => (0.0, 1.0, 0.0),
        "normal" => (1.0, 0.0, 0.0),
    ])?;
    let shoulder = z1 - data.tie_roof_rise;
    let passage = cq
        .workplane(args![plane], vec![])?
        .m(
            "polyline",
            args![vec![
                (y0, z0),
                (y1, z0),
                (y1, shoulder),
                ((y0 + y1) / 2.0, z1),
                (y0, shoulder),
            ]],
        )?
        .m("close", vec![])?
        .m("extrude", args![high_x - low_x + 0.2])?
        .m("val", vec![])?;
    let bore = cq.cylinder(
        data.seat_radius,
        data.root_aft_y - data.bearing_fore_y + 0.2,
        [x, data.bearing_fore_y - 0.1, z],
        [0.0, 1.0, 0.0],
    )?;
    world_shape_in_cap(rt, &cad::clean(&cad::cut(&root, args![bore, passage])?)?)
}

fn back_top_meter(rt: &Runtime) -> Result<Val> {
    let directory = state(rt)?.hw.join("printed-parts/enclosure/enclosure");
    if !rt.pya("sys", "path")?.contains(&Val::Str(ps(&directory)))? {
        rt.sys_path_insert(0, &directory)?;
    }
    rt.py("_back_top_meter")
}

/// `meter_support_datums()`.
pub fn meter_support_datums(rt: &Runtime) -> Result<Val> {
    back_top_meter(rt)?.m("meter_support_datums", vec![])
}

fn jg_band_radius(rt: &Runtime, leg: &str, first: f64, last: f64) -> Result<f64> {
    let path = state(rt)?
        .hw
        .join("reference")
        .join("jg-pp0308e-elbow")
        .join("scan-measurements.json");
    let rows = json_loads(&read_text(&path)?)?
        .k("profiles")?
        .k(leg)?
        .k("fixed_body")?;
    let radii: Vec<f64> = rows
        .list()?
        .iter()
        .map(|row| -> Result<Option<f64>> {
            let (station, radius): (f64, f64) = FromVal::from_val(row)?;
            Ok((first <= station && station <= last).then_some(radius))
        })
        .collect::<Result<Vec<_>>>()?
        .into_iter()
        .flatten()
        .collect();
    ensure!(!radii.is_empty(), "ValueError: max() arg is an empty sequence");
    Ok(fmax(radii))
}

/// `union_support_datums()`.
pub fn union_support_datums(rt: &Runtime) -> Result<Vec<(&'static str, UnionSupport)>> {
    let fits = rt.py("fits")?;
    let a = ac(rt)?;
    let face = a.cap_face_z()? - 0.15;
    let frame = a.snapshot_pose("vb-outlet-return")?;
    let centre = a.point(&frame, [0.0, 0.0, 14.5])?;
    let radius = jg_band_radius(rt, "z", 13.0, 16.0)? + fits.a("slip")?.f()?;
    let rotation = frame.k("rotation")?;
    let down = a.vector(&rotation, [1.0, 0.0, 0.0])?;
    let through = a.vector(&rotation, [0.0, 1.0, 0.0])?;
    let wide = a.vector(&rotation, [0.0, 0.0, -1.0])?;
    let peak: [f64; 3] = std::array::from_fn(|i| centre[i] + (radius + 3.0) * down[i]);
    let low = [centre[0] - radius - 3.0, centre[1] - 5.75, face];
    let high = [centre[0], centre[1] + 5.75, centre[2]];
    let profile = [
        [-1.4, -4.4],
        [1.4, -4.4],
        [1.4, -2.6],
        [0.0, 0.0],
        [-1.4, -2.6],
    ];
    let mut corners = vec![];
    for x in [low[0] - 0.1, high[0] + 0.1] {
        for [u, v] in profile {
            let point: [f64; 3] = std::array::from_fn(|i| peak[i] + u * wide[i] - v * down[i]);
            let t = (x - point[0]) / through[0];
            corners.push(std::array::from_fn::<f64, 3, _>(|i| point[i] + t * through[i]));
        }
    }
    let bore_origin = a.point(&frame, [0.0, 0.0, -5.0])?;
    let bore_axis = a.vector(&rotation, [0.0, 0.0, 1.0])?;
    let window_min: [f64; 3] = std::array::from_fn(|i| fmin(corners.iter().map(|p| p[i])));
    let window_max: [f64; 3] = std::array::from_fn(|i| fmax(corners.iter().map(|p| p[i])));
    let val = dict! {
        "stock_min_world_mm" => low,
        "stock_max_world_mm" => high,
        "bore_origin_world_mm" => bore_origin,
        "bore_axis_world" => bore_axis,
        "bore_length_mm" => 50.0,
        "seat_radius_mm" => radius,
        "native_leg" => "z",
        "native_band_mm" => (13.0, 16.0),
        "tie_window_min_world_mm" => window_min,
        "tie_window_max_world_mm" => window_max,
        "tie_profile_origin_world_mm" => peak,
        "tie_profile_x_world" => wide,
        "tie_profile_normal_world" => through,
        "tie_profile_mm" => profile,
        "tie_route_native_down_mm" => radius + 6.3,
        "centre_world_mm" => centre,
        "wall_mm" => 3.0,
        "parent" => "foam-assembly",
        "support_implemented" => true,
    };
    Ok(vec![(
        "vb-outlet-return",
        UnionSupport {
            stock_min: low,
            stock_max: high,
            bore_origin,
            bore_axis,
            bore_length: 50.0,
            seat_radius: radius,
            tie_profile_origin: peak,
            tie_profile_x: wide,
            tie_profile_normal: through,
            profile,
            tie_route_native_down: radius + 6.3,
            centre,
            parent: "foam-assembly",
            implemented: true,
            val,
        },
    )])
}
fn union_support_datums_val(rt: &Runtime) -> Result<Val> {
    let mut d = Dict::new();
    for (name, support) in union_support_datums(rt)? {
        d.set(name, &support.val);
    }
    Ok(d.val())
}

/// `union_supports()`.
pub fn union_supports(rt: &Runtime) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let mut result = Dict::new();
    for (name, data) in union_support_datums(rt)? {
        if data.parent != "foam-assembly" {
            continue;
        }
        let (low, high) = (data.stock_min, data.stock_max);
        let stock = cq.make_box(std::array::from_fn(|i| high[i] - low[i]), low)?;
        let bore = cq.cylinder(
            data.seat_radius,
            data.bore_length,
            data.bore_origin,
            data.bore_axis,
        )?;
        result.set(
            name,
            world_shape_in_cap(rt, &cad::clean(&cad::cut(&stock, args![bore])?)?)?,
        );
    }
    Ok(result.val())
}

/// `union_support_cuts()`.
pub fn union_support_cuts(rt: &Runtime) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let mut result = Dict::new();
    for (name, data) in union_support_datums(rt)? {
        if data.parent != "foam-assembly" {
            continue;
        }
        let origin: [f64; 3] = std::array::from_fn(|i| {
            data.tie_profile_origin[i] - 40.0 * data.tie_profile_normal[i]
        });
        let plane = cq.plane(kw![
            "origin" => origin,
            "xDir" => data.tie_profile_x,
            "normal" => data.tie_profile_normal,
        ])?;
        let passage = cq
            .workplane(args![plane], vec![])?
            .m("polyline", args![data.profile])?
            .m("close", vec![])?
            .m("extrude", args![80.0])?
            .m("val", vec![])?;
        result.set(name, world_shape_in_cap(rt, &passage)?);
    }
    Ok(result.val())
}

fn tie_arc_point(centre: [f64; 3], u: [f64; 3], v: [f64; 3], radius: f64, angle: f64) -> [f64; 3] {
    let angle = radians(angle);
    std::array::from_fn(|i| centre[i] + radius * (u[i] * angle.cos() + v[i] * angle.sin()))
}
fn tie_line(first: [f64; 3], last: [f64; 3], wide_axis: [f64; 3]) -> TieSegment {
    TieSegment::Line {
        points: [first, last],
        wide_axis,
    }
}
fn tie_arc(centre: [f64; 3], u: [f64; 3], v: [f64; 3], radius: f64, first: f64, last: f64) -> TieSegment {
    let normal = [
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    ];
    TieSegment::Arc {
        points: [first, (first + last) / 2.0, last]
            .map(|angle| tie_arc_point(centre, u, v, radius, angle)),
        radius,
        sweep: last - first,
        wide_axis: normal,
    }
}
fn tie_length(segments: &[TieSegment]) -> f64 {
    fsum(segments.iter().map(|row| match row {
        TieSegment::Line { points, .. } => dist(&points[0], &points[1]),
        TieSegment::Arc { radius, sweep, .. } => radius * radians(*sweep).abs(),
    }))
}
fn segments_val(segments: &[TieSegment]) -> Val {
    Val::list(segments.iter().map(TieSegment::to_val).collect())
}

/// `check_tie_route()`.
pub fn check_tie_route(rt: &Runtime) -> Result<Val> {
    let data = check_support_datums(rt)?;
    let [x, y, z] = data.centre;
    let allowance = 0.55;
    let radius = data.fixed_band_radius + allowance;
    let w = data.stock_x_limits.1 - x + allowance;
    let h = z - data.tie_route_z;
    let left = (-allowance, -h);
    let left_angle = left.1.atan2(left.0) - (radius / hypot(&[left.0, left.1])).acos();
    let right_angle = (radius / w).acos();
    let (centre, u, v) = ([x, y, z], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]);
    let first = [x + left.0, y, z + left.1];
    let lower_east = [x + w, y, z - h];
    let upper_east = [x + w, y, z];
    let right = tie_arc_point(centre, u, v, radius, degrees(right_angle));
    let last = tie_arc_point(centre, u, v, radius, degrees(left_angle));
    let segments = vec![
        tie_line(first, lower_east, [0.0, 1.0, 0.0]),
        tie_line(lower_east, upper_east, [0.0, 1.0, 0.0]),
        tie_line(upper_east, right, [0.0, 1.0, 0.0]),
        tie_arc(
            centre,
            u,
            v,
            radius,
            degrees(right_angle),
            degrees(left_angle) + 360.0,
        ),
        tie_line(last, first, [0.0, 1.0, 0.0]),
    ];
    Ok(dict! {
        "segments" => segments_val(&segments),
        "length_mm" => tie_length(&segments),
        "stock" => "6-inch narrow nylon tie",
        "stock_length_mm" => 152.4,
        "width_mm" => 2.5,
        "thickness_mm" => 0.8,
        "fixed_band_plane_world_y_mm" => y,
        "threading_height_mm" => data.tie_window_z.1 - data.tie_window_z.0,
        "strip_basis" => "Nominal layout allowance; purchased strap/head dimensions unmeasured",
    })
}

fn vb_union_tie(rt: &Runtime, data: &UnionSupport) -> Result<Vec<TieSegment>> {
    let a = ac(rt)?;
    let frame = a.snapshot_pose("vb-outlet-return")?;
    let rotation = frame.k("rotation")?;
    let centre = data.centre;
    let u = a.vector(&rotation, [0.0, 1.0, 0.0])?;
    let v = a.vector(&rotation, [1.0, 0.0, 0.0])?.map(|value| -value);
    let radius = data.seat_radius + 0.55;
    let lower = tie_arc_point(centre, u, v, radius, -20.0);
    let upper = tie_arc_point(centre, u, v, radius, 170.0);
    let down = a.vector(&rotation, [1.0, 0.0, 0.0])?;
    let axis = a.vector(&rotation, [0.0, 0.0, 1.0])?;
    let line_origin: [f64; 3] =
        std::array::from_fn(|i| centre[i] + data.tie_route_native_down * down[i]);
    let (west_x, east_x) = (data.stock_min[0] - 0.8, data.stock_max[0] + 0.8);
    let at_x = |x: f64| -> [f64; 3] {
        let t = (x - line_origin[0]) / u[0];
        std::array::from_fn(|i| line_origin[i] + t * u[i])
    };
    let (west_lower, east_lower) = (at_x(west_x), at_x(east_x));
    let west_upper = [west_x, centre[1], pmax(centre[2] + 3.0, upper[2] + 1.0)];
    Ok(vec![
        tie_arc(centre, u, v, radius, -20.0, 170.0),
        tie_line(upper, west_upper, axis),
        tie_line(west_upper, west_lower, axis),
        tie_line(west_lower, east_lower, axis),
        tie_line(east_lower, lower, axis),
    ])
}

/// `union_tie_routes()`.
pub fn union_tie_routes(rt: &Runtime) -> Result<Vec<(&'static str, TieRoute)>> {
    let data = union_support_datums(rt)?;
    let mut result = vec![];
    for (name, support) in &data {
        if *name != "vb-outlet-return" || !support.implemented {
            continue;
        }
        let segments = vb_union_tie(rt, support)?;
        let length = tie_length(&segments);
        let val = dict! {
            "segments" => segments_val(&segments),
            "length_mm" => length,
            "stock" => "6-inch narrow nylon tie",
            "stock_length_mm" => 152.4,
            "width_mm" => 2.5,
            "thickness_mm" => 0.8,
            "strip_basis" => "Nominal layout allowance; purchased strap dimensions unmeasured",
        };
        result.push((
            *name,
            TieRoute {
                segments,
                length,
                val,
            },
        ));
    }
    Ok(result)
}
fn routes_val(routes: &[(&'static str, TieRoute)]) -> Val {
    let mut d = Dict::new();
    for (name, route) in routes {
        d.set(*name, &route.val);
    }
    d.val()
}

/// `meter_tie_routes()`.
pub fn meter_tie_routes() -> Vec<(&'static str, TieRoute)> {
    vec![]
}

/// `nominal_tie_strips()`.
pub fn nominal_tie_strips(rt: &Runtime) -> Result<Val> {
    let cq = Cq::new(rt)?;
    let mut result = Dict::new();
    let mut routes = union_tie_routes(rt)?;
    routes.extend(meter_tie_routes());
    for (name, data) in &routes {
        let (width, thickness) = (2.5, 0.8);
        let mut pieces = vec![];
        for segment in &data.segments {
            let piece = match segment {
                TieSegment::Arc {
                    points, wide_axis, ..
                } => {
                    let vectors = points
                        .iter()
                        .map(|p| cq.vector(*p))
                        .collect::<Result<Vec<_>>>()?;
                    let edge = cq.class("Edge", "makeThreePointArc", vectors, vec![])?;
                    let wire = cq.class(
                        "Wire",
                        "assembleEdges",
                        vec![Val::list(vec![edge.clone()])],
                        vec![],
                    )?;
                    let plane = cq.plane(kw![
                        "origin" => edge.m("startPoint", vec![])?,
                        "normal" => edge.m("tangentAt", args![0i64])?,
                        "xDir" => cq.vector(*wide_axis)?,
                    ])?;
                    cq.workplane(args![plane], vec![])?
                        .m("rect", args![width, thickness])?
                        .mk(
                            "sweep",
                            args![wire],
                            kw!["isFrenet" => true, "transition" => "round"],
                        )?
                        .m("val", vec![])?
                }
                TieSegment::Line { points, wide_axis } => {
                    let first = cq.vector(points[0])?;
                    let last = cq.vector(points[1])?;
                    let tangent = hsm_documents::interop::binary("sub", last.clone(), first.clone())?
                        .m("normalized", vec![])?;
                    let wide0 = cq.vector(*wide_axis)?;
                    let along = hsm_documents::interop::binary(
                        "mul",
                        tangent.clone(),
                        wide0.m("dot", args![tangent])?,
                    )?;
                    let wide = hsm_documents::interop::binary("sub", wide0, along)?
                        .m("normalized", vec![])?;
                    let thin = tangent.m("cross", args![wide])?.m("normalized", vec![])?;
                    let rectangle = |at: &Val| -> Result<Val> {
                        let corners = [
                            (-width / 2.0, -thickness / 2.0),
                            (width / 2.0, -thickness / 2.0),
                            (width / 2.0, thickness / 2.0),
                            (-width / 2.0, thickness / 2.0),
                        ]
                        .iter()
                        .map(|(w, t)| {
                            let a = hsm_documents::interop::binary(
                                "add",
                                at.clone(),
                                hsm_documents::interop::binary(
                                    "mul",
                                    wide.clone(),
                                    Val::Float(*w),
                                )?,
                            )?;
                            hsm_documents::interop::binary(
                                "add",
                                a,
                                hsm_documents::interop::binary(
                                    "mul",
                                    thin.clone(),
                                    Val::Float(*t),
                                )?,
                            )
                        })
                        .collect::<Result<Vec<_>>>()?;
                        cq.class(
                            "Wire",
                            "makePolygon",
                            vec![Val::list(corners)],
                            kw!["close" => true],
                        )
                    };
                    cq.ruled_loft(vec![rectangle(&first)?, rectangle(&last)?])?
                }
            };
            pieces.push(piece);
        }
        result.set(
            *name,
            cq.class("Compound", "makeCompound", vec![Val::list(pieces)], vec![])?,
        );
    }
    Ok(result.val())
}

/// `gas_guide_xy()`.
pub fn gas_guide_xy(rt: &Runtime) -> Result<[f64; 2]> {
    let a = ac(rt)?;
    Ok(xy(a.world_to_cap(a.spec().k("gas_guide_world_mm")?)?))
}

/// `cap_guide_xy(name, fallback)`.
pub fn cap_guide_xy(rt: &Runtime, name: &str, fallback: [f64; 2]) -> Result<[f64; 2]> {
    let a = ac(rt)?;
    match a.spec().k("cap_guides_world_mm")?.get_opt(name)? {
        None | Some(Val::None) => Ok(fallback),
        Some(point) => Ok(xy(a.world_to_cap(point)?)),
    }
}

/// `world_shape_in_cap(shape)`.
pub fn world_shape_in_cap(rt: &Runtime, shape: &Val) -> Result<Val> {
    let a = ac(rt)?;
    let frame = a.cap_lid_pose()?;
    let r = rot_of(&frame.k("rotation")?)?;
    let rotation: Rot = std::array::from_fn(|i| std::array::from_fn(|j| r[j][i]));
    let translation: [Num; 3] = <[Num; 3]>::from_val(&frame.k("translation_mm")?)?;
    let rotation = rot_val(&rotation);
    let back = a.vector(&rotation, translation.map(Num::neg))?;
    cad::moved(
        shape,
        &a.frame_location(&dict! {"rotation" => &rotation, "translation_mm" => back})?,
    )
}

/// `passive_guide_points(lower_xy, upper_xy, start_z, end_z, bend_start_z, radius=14.0)`.
pub fn passive_guide_points(
    lower: [f64; 2],
    upper: [f64; 2],
    start_z: f64,
    end_z: f64,
    bend_start_z: f64,
    radius: f64,
) -> Vec<[f64; 3]> {
    let distance = dist(&lower, &upper);
    if distance < 1e-09 {
        return vec![xyz(lower, start_z), xyz(upper, end_z)];
    }
    let theta = (1.0 - distance / (2.0 * radius)).acos();
    let setback = radius * (theta / 2.0).tan();
    let rise = 2.0 * radius * theta.sin();
    vec![
        xyz(lower, start_z),
        xyz(lower, bend_start_z + setback),
        xyz(upper, bend_start_z + rise - setback),
        xyz(upper, end_z),
    ]
}

/// `cable_guide_points(name)`: `(points, bend radius)`.
pub fn cable_guide_points(rt: &Runtime, name: &str) -> Result<(Vec<[f64; 3]>, f64)> {
    let core = core::state(rt)?;
    let a = ac(rt)?;
    let pose = a.cap_lid_pose()?;
    let floor = core.cap_conduit_floor_xy(name)?;
    let top = core.cap_conduit(name)?;
    let lower = xy(a.point(&pose, xyz(floor, 0.0))?);
    let upper = xy(a.point(&pose, xyz(top, 0.0))?);
    let cup_height = core.base.foam_cap_height - core.base.head_pad_height;
    let lid_z = pose.k("translation_mm")?.i(2)?.f()?;
    let cup_bottom = lid_z - cup_height;
    let mid_z = lid_z - 6.6;
    let face = a.cap_face_z()?;
    if dist(&lower, &upper) < 1e-09 {
        return Ok((
            vec![xyz(lower, cup_bottom - 1.0), xyz(upper, face + 2.0)],
            5.5,
        ));
    }
    let plan: Vec<[f64; 2]> = if name == "sensor-cable" {
        vec![lower, [lower[0], upper[1]], upper]
    } else {
        vec![lower, upper]
    };
    let mut points = vec![xyz(lower, cup_bottom - 1.0)];
    points.extend(plan.iter().map(|p| xyz(*p, mid_z)));
    points.push(xyz(upper, face + 2.0));
    Ok((points, 5.5))
}

/// `water_in_guide_points()`.
pub fn water_in_guide_points(rt: &Runtime) -> Result<Vec<Val>> {
    let core = core::base(rt)?;
    let a = ac(rt)?;
    let parts = a.spec().k("cap_guides_world_mm")?.k("water-in")?.list()?;
    let guide = Val::Tuple(parts.clone());
    // `core.carbonator_height` is `_carbonator_stock`'s, which the interface re-exports.
    let carbonator_height = rt.pya("_carbonator_stock", "carbonator_height")?.f()?;
    let band = core.wall_and_floor_thickness
        + core.carbonator_support_ring_height
        + carbonator_height
        + core.hole_shift_from_edge;
    let cup_height = core.foam_cap_height - core.head_pad_height;
    let world_z =
        a.cap_lid_pose()?.k("translation_mm")?.i(2)?.f()? - cup_height - core.foam_shell_outer_height;
    ensure!(parts.len() >= 2, "water-in guide point");
    let lifted = Val::Tuple(vec![parts[0].clone(), parts[1].clone(), Val::Float(band + world_z)]);
    Ok(vec![lifted, guide])
}

/// `water_in_floor_xy()`.
pub fn water_in_floor_xy(rt: &Runtime) -> Result<[f64; 2]> {
    let points = water_in_guide_points(rt)?;
    Ok(xy(ac(rt)?.world_to_cap(&points[points.len() - 1])?))
}

/// `water_in_features()`.
pub fn water_in_features(rt: &Runtime) -> Result<Val> {
    straight_cap_features(rt, "water-in")
}

/// `soda_out_guide_points()`.
pub fn soda_out_guide_points(rt: &Runtime) -> Result<Vec<Val>> {
    let a = ac(rt)?;
    let guide = Val::Tuple(
        a.spec()
            .k("cap_guides_world_mm")?
            .k("carb-water-out")?
            .list()?,
    );
    let core = core::base(rt)?;
    let floor = a.cap_lid_pose()?.k("translation_mm")?.i(2)?.f()?
        - (core.foam_cap_height - core.head_pad_height);
    Ok(vec![xyz(xy(guide.v3()?), floor - 1.0).to_val(), guide])
}

/// `soda_out_features()`.
pub fn soda_out_features(rt: &Runtime) -> Result<Val> {
    straight_cap_features(rt, "carb-water-out")
}

/// `reservoir_b_fill_passage()`.
pub fn reservoir_b_fill_passage(rt: &Runtime) -> Result<Val> {
    super::reservoir_b_fill::passage_val(rt)
}

/// `reservoir_b_fill_features(cup_height)`.
pub fn reservoir_b_fill_features(rt: &Runtime, cup_height: Val) -> Result<Val> {
    let s = state(rt)?;
    for (key, value) in s.fill_features.borrow().iter() {
        if hsm_documents::interop::eq(key, &cup_height)? {
            return Ok(value.clone());
        }
    }
    let value = super::reservoir_b_fill::features(rt, cup_height.f()?)?;
    s.fill_features.borrow_mut().push((cup_height, value.clone()));
    Ok(value)
}

/// `schedule()`.
pub fn schedule(rt: &Runtime) -> Result<Val> {
    let core = core::state(rt)?;
    let b = &core.base;
    let mut modules = Dict::new();
    for (name, row) in deck_mounts(rt)?.iter() {
        let lid_stack = if row.standoff == 0.0 {
            b.foam_cap_lid_height + b.cap_lid_clearance
        } else {
            0.0
        };
        let maximum_reach = row.screw - row.seat_min - lid_stack;
        let mut entry = Dict::new();
        for (field, value) in ["points", "standoff", "seat", "screw", "seat_min"]
            .iter()
            .zip(&row.fields)
        {
            entry.set(*field, value);
        }
        entry.set("quantity", row.points.len());
        entry.set("nominal_threaded_reach_mm", core.deck_mount_reach(name)?);
        entry.set("maximum_threaded_reach_mm", maximum_reach);
        entry.set(
            "minimum_tip_clearance_mm",
            core.deck_mount_bore_depth - maximum_reach,
        );
        modules.set(name.as_str(), entry);
    }
    let mut supports = Dict::new();
    for name in ["valve-v-b"] {
        supports.set(
            name,
            dict! {
                "attachment" => "Integral upright socket wall on the top lid",
                "native_to_cap" => frame_val(&component_in_cap(rt, name)?),
                "socket_fit" => "Shared valve_seat V69",
            },
        );
    }
    let mut allocation = Dict::new();
    for (name, route) in union_tie_routes(rt)? {
        allocation.set(
            name,
            dict! {
                "length_mm" => route.length,
                "stock" => "6-inch narrow nylon tie",
                "stock_length_mm" => 152.4,
            },
        );
    }
    Ok(dict! {
        "frame" => "Top cap/lid native coordinates before installed half turn",
        "insert" => "ruthex RX-M3x5.7",
        "lid_face_z_mm" => lid_face_z(rt)?,
        "column_diameter_mm" => 2.0 * b.deck_mount_boss_radius,
        "pilot_diameter_mm" => 2.0 * b.deck_mount_bore_radius,
        "pilot_depth_mm" => core.deck_mount_bore_depth,
        "insert_length_mm" => b.deck_mount_insert_length,
        "modules" => modules,
        "valve_supports" => supports,
        "union_supports" => union_support_datums_val(rt)?,
        "union_tie_allocation" => allocation,
    })
}

/// `straight_cap_features(name)`.
pub fn straight_cap_features(rt: &Runtime, name: &str) -> Result<Val> {
    let s = state(rt)?;
    if let Some((_, held)) = s.straight.borrow().iter().find(|(n, _)| n == name) {
        return Ok(held.clone());
    }
    let cq = Cq::new(rt)?;
    let core = core::state(rt)?;
    let b = &core.base;
    let a = ac(rt)?;
    let guide = a.spec().k("cap_guides_world_mm")?.k(name)?.v3()?;
    let lid_bottom = a.cap_lid_pose()?.k("translation_mm")?.i(2)?.f()?;
    let floor = lid_bottom - (b.foam_cap_height - b.head_pad_height);
    let radius = core.cap_conduit_bore_radius;
    let cylinder = |r: f64, z0: f64, z1: f64| cq.cylinder_z(r, z1 - z0, xyz(xy(guide), z0));
    let value = dict! {
        "cup_add" => cylinder(radius + 3.0, floor + b.cap_shell_clearance, lid_bottom - b.cap_lid_clearance)?,
        "lid_add" => cylinder(radius + 3.0, lid_bottom, guide[2])?,
        "cut" => cylinder(radius, floor - 1.0, guide[2] + 1.0)?,
        "wall_mm" => 3.0,
        "horizontal_floor_backing_mm" => Val::None,
    };
    s.straight
        .borrow_mut()
        .push((name.to_owned(), value.clone()));
    Ok(value)
}

fn points_val(points: &[[f64; 3]]) -> Val {
    Val::Tuple(points.iter().map(ToVal::to_val).collect())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("lru_cache", rt.import_module("functools")?.a("lru_cache")?);
    ns.module(rt, "importlib", "importlib")?;
    ns.module(rt, "itertools", "itertools")?;
    ns.module(rt, "math", "math")?;
    ns.value("namedtuple", rt.import_module("collections")?.a("namedtuple")?);
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.module(rt, "sys", "sys")?;
    ns.value("HW", s.hw.clone());
    ns.value("path", s.path.clone());
    ns.value("above_core", rt.py("above_core")?);
    ns.value("DeckMount", s.deck_mount_type.clone());
    ns.func(rt, "_multiply", |_, c| {
        let a = rot_of(&c.req::<Val>(0, "a")?)?;
        let b = rot_of(&c.req::<Val>(1, "b")?)?;
        Ok(rot_val(&multiply(&a, &b)))
    });
    ns.func(rt, "component_in_cap", |rt, c| {
        Ok(frame_val(&component_in_cap(rt, &c.req::<String>(0, "name")?)?))
    });
    ns.func(rt, "lid_face_z", |rt, _| Ok(lid_face_z(rt)?.to_val()));
    ns.func(rt, "va_feed_snap", |rt, _| va_feed_snap(rt));
    ns.func(rt, "flavor_snaps", |rt, _| flavor_snaps(rt));
    ns.func(rt, "manifold_cable_bank", |rt, _| manifold_cable_bank(rt));
    ns.func(rt, "rear_level_cable_hook", |rt, _| rear_level_cable_hook(rt));
    ns.func(rt, "mounting_points", |rt, c| {
        let name = c.req::<String>(0, "name")?;
        let holes = c.req::<Val>(1, "holes")?;
        Ok(Val::Tuple(
            mounting_points(rt, &name, &holes)?
                .iter()
                .map(ToVal::to_val)
                .collect(),
        ))
    });
    ns.func(rt, "_standoff", |rt, c| {
        Ok(standoff(rt, &c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "deck_mounts", |rt, _| deck_mounts_val(rt));
    ns.func(rt, "_pump_section_points", |_, c| {
        let pump = own(&c.req::<Val>(0, "pump")?)?;
        let first = c.req::<f64>(1, "first")?;
        let last = c.req::<f64>(2, "last")?;
        let points = pump_section_points(&sections_of(&pump)?, first, last)?;
        Ok(Val::list(
            points
                .iter()
                .map(|p| Val::list(p.iter().map(|v| Val::Float(*v)).collect()))
                .collect(),
        ))
    });
    ns.func(rt, "pump_cradle_datums", |rt, _| {
        Ok(pump_cradle_datums(rt)?.val.clone())
    });
    ns.func(rt, "_pump_cap_to_world", |_, c| {
        let shape = c.req::<Val>(0, "shape")?;
        let datum = c.req::<Val>(1, "datum")?;
        pump_cap_to_world(&shape, datum.kv3("centre_world_mm")?)
    });
    ns.func(rt, "_pump_motor_room", |rt, c| {
        let datum = c.req::<Val>(0, "datum")?;
        let seat = c.kw::<bool>("seat", false)?;
        let d = pump_cradle_datums(rt)?;
        let key = if seat {
            "seat_bore_radius_mm"
        } else {
            "bore_radius_mm"
        };
        pump_motor_room(rt, &d, datum.kf(key)?)
    });
    ns.func(rt, "pump_snap_cap", |rt, c| {
        pump_snap_cap(rt, c.opt::<i64>(0, "index", 0)?)
    });
    ns.func(rt, "pump_snap_printable", |rt, c| {
        pump_snap_printable(rt, c.opt::<i64>(0, "index", 0)?)
    });
    ns.func(rt, "pump_cradle", |rt, _| pump_cradle(rt));
    ns.func(rt, "pump_lid_clearance", |rt, _| pump_lid_clearance(rt));
    ns.func(rt, "valve_support_datums", |rt, c| {
        let name = c.req::<String>(0, "name")?;
        let face_z = c.opt::<Option<f64>>(1, "face_z", None)?;
        Ok(valve_support_datums(rt, &name, face_z)?.val)
    });
    ns.func(rt, "valve_support", |rt, c| {
        let name = c.req::<String>(0, "name")?;
        let face_z = c.opt::<Option<f64>>(1, "face_z", None)?;
        valve_support(rt, &name, face_z)
    });
    ns.func(rt, "_check_bearing_station", |rt, _| {
        let (point, radius, first, last) = check_bearing_station(rt)?;
        Ok(Val::Tuple(vec![point.to_val(), radius, first.to_val(), last.to_val()]))
    });
    ns.func(rt, "check_anchor", |rt, _| check_anchor(rt));
    ns.func(rt, "check_support_datums", |rt, _| Ok(check_support_datums(rt)?.val));
    ns.func(rt, "check_support", |rt, _| check_support(rt));
    ns.func(rt, "_back_top_meter", |rt, _| back_top_meter(rt));
    ns.func(rt, "meter_support_datums", |rt, _| meter_support_datums(rt));
    ns.func(rt, "_jg_band_radius", |rt, c| {
        let leg = c.req::<String>(0, "leg")?;
        let first = c.req::<f64>(1, "first")?;
        let last = c.req::<f64>(2, "last")?;
        Ok(jg_band_radius(rt, &leg, first, last)?.to_val())
    });
    ns.func(rt, "union_support_datums", |rt, _| union_support_datums_val(rt));
    ns.func(rt, "union_supports", |rt, _| union_supports(rt));
    ns.func(rt, "union_support_cuts", |rt, _| union_support_cuts(rt));
    ns.func(rt, "_tie_arc_point", |_, c| {
        let centre = c.req::<[f64; 3]>(0, "centre")?;
        let u = c.req::<[f64; 3]>(1, "u")?;
        let v = c.req::<[f64; 3]>(2, "v")?;
        let radius = c.req::<f64>(3, "radius")?;
        let angle = c.req::<f64>(4, "angle")?;
        Ok(tie_arc_point(centre, u, v, radius, angle).to_val())
    });
    ns.func(rt, "_tie_line", |_, c| {
        let first = c.req::<Val>(0, "first")?;
        let last = c.req::<Val>(1, "last")?;
        let wide = c.opt::<Val>(2, "wide_axis", [0.0, 0.0, 1.0].to_val())?;
        Ok(dict! {"kind" => "line", "points_mm" => Val::list(vec![first, last]), "wide_axis" => wide})
    });
    ns.func(rt, "_tie_arc", |_, c| {
        let centre = c.req::<[f64; 3]>(0, "centre")?;
        let u = c.req::<[f64; 3]>(1, "u")?;
        let v = c.req::<[f64; 3]>(2, "v")?;
        let radius = c.req::<f64>(3, "radius")?;
        let first = c.req::<f64>(4, "first")?;
        let last = c.req::<f64>(5, "last")?;
        Ok(tie_arc(centre, u, v, radius, first, last).to_val())
    });
    ns.func(rt, "_tie_length", |_, c| {
        let segments = c.req::<Val>(0, "segments")?;
        let mut total = Num::I(0);
        for row in segments.list()? {
            let length = if row.ks("kind")? == "line" {
                let points = row.k("points_mm")?.list()?;
                let (a, b) = (points[0].floats()?, points[1].floats()?);
                dist(&a, &b)
            } else {
                row.kf("radius_mm")? * radians(row.kf("sweep_degrees")?).abs()
            };
            total = total.add(length);
        }
        Ok(total.to_val())
    });
    ns.func(rt, "check_tie_route", |rt, _| check_tie_route(rt));
    ns.func(rt, "_vb_union_tie", |rt, c| {
        c.req::<Val>(0, "data")?;
        let data = union_support_datums(rt)?;
        Ok(segments_val(&vb_union_tie(rt, &data[0].1)?))
    });
    ns.func(rt, "union_tie_routes", |rt, _| Ok(routes_val(&union_tie_routes(rt)?)));
    ns.func(rt, "meter_tie_routes", |_, _| Ok(routes_val(&meter_tie_routes())));
    ns.func(rt, "nominal_tie_strips", |rt, _| nominal_tie_strips(rt));
    ns.func(rt, "gas_guide_xy", |rt, _| Ok(gas_guide_xy(rt)?.to_val()));
    ns.func(rt, "cap_guide_xy", |rt, c| {
        let name = c.req::<String>(0, "name")?;
        let fallback = c.req::<Val>(1, "fallback")?;
        let a = ac(rt)?;
        match a.spec().k("cap_guides_world_mm")?.get_opt(&name)? {
            None | Some(Val::None) => Ok(fallback),
            Some(point) => Ok(xy(a.world_to_cap(point)?).to_val()),
        }
    });
    ns.func(rt, "world_shape_in_cap", |rt, c| {
        world_shape_in_cap(rt, &c.req::<Val>(0, "shape")?)
    });
    ns.func(rt, "passive_guide_points", |_, c| {
        let lower = c.req::<[f64; 2]>(0, "lower_xy")?;
        let upper = c.req::<[f64; 2]>(1, "upper_xy")?;
        let start_z = c.req::<f64>(2, "start_z")?;
        let end_z = c.req::<f64>(3, "end_z")?;
        let bend = c.req::<f64>(4, "bend_start_z")?;
        let radius = c.opt::<f64>(5, "radius", 14.0)?;
        Ok(Val::list(
            passive_guide_points(lower, upper, start_z, end_z, bend, radius)
                .iter()
                .map(ToVal::to_val)
                .collect(),
        ))
    });
    ns.func(rt, "cable_guide_points", |rt, c| {
        let (points, bend) = cable_guide_points(rt, &c.req::<String>(0, "name")?)?;
        Ok(dict! {"points_mm" => points_val(&points), "bend_radius_mm" => bend})
    });
    ns.func(rt, "water_in_guide_points", |rt, _| {
        Ok(Val::list(water_in_guide_points(rt)?))
    });
    ns.func(rt, "water_in_floor_xy", |rt, _| Ok(water_in_floor_xy(rt)?.to_val()));
    ns.func(rt, "water_in_features", |rt, _| water_in_features(rt));
    ns.func(rt, "soda_out_guide_points", |rt, _| {
        Ok(Val::list(soda_out_guide_points(rt)?))
    });
    ns.func(rt, "soda_out_features", |rt, _| soda_out_features(rt));
    ns.func(rt, "reservoir_b_fill_passage", |rt, _| reservoir_b_fill_passage(rt));
    ns.func(rt, "reservoir_b_fill_features", |rt, c| {
        let cup_height = c.req::<Val>(0, "cup_height")?;
        reservoir_b_fill_features(rt, cup_height)
    });
    ns.func(rt, "schedule", |rt, _| schedule(rt));
    ns.func(rt, "straight_cap_features", |rt, c| {
        straight_cap_features(rt, &c.req::<String>(0, "name")?)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
