//! Four removable snap caps for the rear inlet equipment.
//!
//! Typed API: [`world_bounds`] (the world box a pose carries a local box to) and [`numbers`]
//! (the four caps' recipe for the `rear-equipment-caps` part program, in [`NAMES`] order). The
//! rear plumbing, the above-core layout, the snaps and the fits are Python modules: their objects
//! stay `Val` and go back to them as they came; the figures computed on here are [`Num`]s, an int
//! staying an int as the recipe document writes it.
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result, bail, ensure};
use hsm_documents::interop;
use std::cmp::Ordering;
use std::path::{Path, PathBuf};
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "rear_equipment_caps";

/// The four caps, in the order [`numbers`] states them.
pub const NAMES: [&str; 4] = ["asse-snap-cap", "pisco-snap-cap", "meter-snap-cap", "regulator-snap-cap"];

/// The module's typed state.
pub struct State {
    /// `HERE`: this part's directory.
    here: PathBuf,
    /// `HW`: the repository's `hardware`.
    hw: PathBuf,
    rear_plumbing: Val,
    petgf_black: Val,
    linear: Val,
}

/// The module's state, initializing the module on first use.
pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

// The runtime's arithmetic on the module's numbers.

fn order(a: Num, b: Num) -> Result<Ordering> {
    a.f().partial_cmp(&b.f()).context("unordered numeric comparison")
}
fn lt(a: Num, b: Num) -> Result<bool> {
    Ok(order(a, b)?.is_lt())
}
fn gt(a: Num, b: Num) -> Result<bool> {
    Ok(order(a, b)?.is_gt())
}
fn le(a: Num, b: Num) -> Result<bool> {
    Ok(!order(a, b)?.is_gt())
}
fn ge(a: Num, b: Num) -> Result<bool> {
    Ok(!order(a, b)?.is_lt())
}
/// `min(a, b)`: the first of equal values wins.
fn min2(a: Num, b: Num) -> Result<Num> {
    Ok(if lt(b, a)? { b } else { a })
}
/// `max(a, b)`: the first of equal values wins.
fn max2(a: Num, b: Num) -> Result<Num> {
    Ok(if gt(b, a)? { b } else { a })
}
/// `min(values)`: the first of equal values wins.
fn min_of(values: impl IntoIterator<Item = Num>) -> Result<Num> {
    let mut best: Option<Num> = None;
    for v in values {
        if best.map(|b| order(v, b)).transpose()?.is_none_or(Ordering::is_lt) {
            best = Some(v);
        }
    }
    best.context("empty min/max")
}
/// `max(values)`: the first of equal values wins.
fn max_of(values: impl IntoIterator<Item = Num>) -> Result<Num> {
    let mut best: Option<Num> = None;
    for v in values {
        if best.map(|b| order(v, b)).transpose()?.is_none_or(Ordering::is_gt) {
            best = Some(v);
        }
    }
    best.context("empty min/max")
}
/// `max(*values)`: two or more arguments, compared among themselves.
fn max_args(values: Vec<Num>) -> Result<Num> {
    ensure!(values.len() > 1, "max() of {} arguments iterates its argument", values.len());
    max_of(values)
}
/// `x ** 2`: an int squared stays an int.
fn pow2(n: Num) -> Num {
    n.pow(Num::I(2))
}
/// `math.sqrt(x)`.
fn sqrt(x: f64) -> Result<f64> {
    if !(x >= 0.) {
        bail!("math domain error");
    }
    Ok(x.sqrt())
}

// Values as the providers and the profile files hold them.

fn n(v: &Val) -> Result<Num> {
    Num::of(v)
}
fn at(v: &Val, key: &str) -> Result<Val> {
    py::at(v, key)
}
fn item(v: &Val, index: i64) -> Result<Val> {
    v.get(Val::Int(index))
}
/// `(v[0], v[1], v[2])`.
fn first3(v: &Val) -> Result<[Num; 3]> {
    Ok([n(&item(v, 0)?)?, n(&item(v, 1)?)?, n(&item(v, 2)?)?])
}
/// A point a provider returns.
fn point3(v: &Val) -> Result<[Num; 3]> {
    first3(&py::snapshot(v)?)
}
/// Rows of exactly `N` numbers, each unpacked as Python's `for a, b, ... in rows` does.
fn rows<const N: usize>(v: &Val) -> Result<Vec<[Num; N]>> {
    v.iter()?
        .iter()
        .map(|row| {
            let values = py::unpack(row, N)?;
            let mut out = [Num::I(0); N];
            for (slot, value) in out.iter_mut().zip(&values) {
                *slot = n(value)?;
            }
            Ok(out)
        })
        .collect()
}
/// `json.loads(path.read_text())`.
fn json_file(path: &Path) -> Result<Val> {
    py::json_loads(&py::read_text(path)?)
}

// The recipe's own records.

/// `box(x0, x1, y0, y1, z0, z1)`: `{'op': 'box', 'bounds': (...)}`.
fn boxed(bounds: Vec<Val>) -> Result<Val> {
    ensure!(bounds.len() == 6, "box() takes 6 positional arguments but {} were given", bounds.len());
    Ok(py::dict([("op", py::s("box")), ("bounds", Val::Tuple(bounds))]))
}
fn boxed_nums(bounds: [Num; 6]) -> Val {
    py::dict([("op", py::s("box")), ("bounds", Num::vals(&bounds))])
}
/// `{'op': 'section', **room}`.
fn section(room: &Val) -> Result<Val> {
    let out = py::dict([("op", py::s("section"))]);
    for (key, value) in interop::entries_of(room)? {
        out.set(key, value)?;
    }
    Ok(out)
}
/// `runs(rows, frame, air)`: a seat's measured runs `(lo, hi, r)` along the reference's own axis,
/// in reverse, as world Y spans under the frame's translation with `air` on each radius.
fn runs(rows: &[[Num; 3]], frame: &Val, air: Num) -> Result<Vec<[Num; 3]>> {
    let t = n(&item(&at(frame, "translation_mm")?, 1)?)?;
    Ok(rows.iter().rev().map(|&[lo, hi, r]| [t.sub(hi), t.sub(lo), r.add(air)]).collect())
}
/// The seat runs a cap spanning `cap_y` (with a quarter millimetre either end) reaches.
fn reached(seat: &[[Num; 3]], cap_y: [Num; 2]) -> Result<Vec<Num>> {
    let mut out = vec![];
    for &[y0, y1, r] in seat {
        if ge(y1, cap_y[0].sub(Num::F(0.25)))? && le(y0, cap_y[1].add(Num::F(0.25)))? {
            out.push(r);
        }
    }
    Ok(out)
}

/// A wrench flat on the ASSE body or cap: its world Y span, half its across-flats, its clock and
/// its widest radius.
struct Wrench {
    y: [Num; 2],
    half: Num,
    clock: Num,
    corner: Num,
}
impl Wrench {
    fn val(&self) -> Val {
        py::tuple([py::list(self.y.map(Num::val)), self.half.val(), self.clock.val(), self.corner.val()])
    }
}

/// The world box `frame` carries the local box `lo`..`hi` to: the bounds of its eight corners.
pub fn world_bounds(rt: &Rt, frame: &Val, lo: [Num; 3], hi: [Num; 3]) -> Result<[[Num; 3]; 2]> {
    let layout = rt.import("above_core")?;
    let point = layout.attr("point")?;
    let mut points: Vec<[Num; 3]> = Vec::with_capacity(8);
    for x in [lo[0], hi[0]] {
        for y in [lo[1], hi[1]] {
            for z in [lo[2], hi[2]] {
                points.push(point3(&point.call(vec![frame.clone(), Num::vals(&[x, y, z])], vec![])?)?);
            }
        }
    }
    let low = [0, 1, 2].map(|k| min_of(points.iter().map(|p| p[k])));
    let high = [0, 1, 2].map(|k| max_of(points.iter().map(|p| p[k])));
    let [l0, l1, l2] = low;
    let [h0, h1, h2] = high;
    Ok([[l0?, l1?, l2?], [h0?, h1?, h2?]])
}

/// Live snap stock, fits and poses around reference-local measured cap clearances.
pub fn numbers(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let layout = rt.import("above_core")?;
    let parts = rt.import("above_core_parts")?;
    let snaps = rt.import("rear_snaps")?;
    let fits = rt.import("fits")?;
    let profiles = json_file(&st.hw.join("printed-parts/enclosure/enclosure/rear-seat-profiles.json"))?;
    let cap_profiles = json_file(&st.here.join("rear-cap-profiles.json"))?;
    let plumbing = &st.rear_plumbing;
    let datums = py::snapshot(&plumbing.attr("snap_datums")?.call(vec![], vec![])?)?;
    let plan = plumbing.attr("plan")?.call(vec![], vec![])?;
    let bfp = plumbing.attr("chain")?.call(vec![], vec![])?.attr("bfp")?;
    let (c, s) = (n(&fits.attr("running")?)?, n(&fits.attr("slip")?)?);
    let point = layout.attr("point")?;
    let pose = layout.attr("pose")?;
    let at_frame =
        |frame: &Val, p: [Num; 3]| -> Result<[Num; 3]> { point3(&point.call(vec![frame.clone(), Num::vals(&p)], vec![])?) };
    let station = snaps.attr("station")?;
    let cap_section = snaps.attr("cap_section")?;
    let zero = Num::F(0.0);

    // The ASSE 1022's cap.
    let axis = at(&datums, "asse_axis")?;
    let frame = at(&plan, "chain_frame")?;
    let ax = [n(&item(&axis, 0)?)?, n(&item(&axis, 1)?)?];
    let seat = runs(&rows::<3>(&at(&at(&profiles, "asse")?, "seat_runs")?)?, &frame, c)?;
    let cap_profile = rows::<2>(&py::snapshot(&bfp.attr("CAP_PROFILE")?)?)?;
    let crown = max_of(cap_profile.iter().map(|p| p[1]))?;
    let bonnet = max_of(cap_profile.iter().filter(|p| p[1].f() == crown.f()).map(|p| p[0]))?;
    let body_z = n(&bfp.attr("BODY_CENTER_Z")?)?;
    let gagira = n(&at(&at(&cap_profiles, "asse")?, "gagira_fore_x")?)?;
    let cap_y = [at_frame(&frame, [bonnet, zero, body_z])?[1].sub(s), at_frame(&frame, [gagira, zero, body_z])?[1].sub(s)];
    let body_profile = rows::<2>(&py::snapshot(&bfp.attr("BODY_PROFILE")?)?)?;
    let hex = n(&bfp.attr("HEX_ACROSS_FLATS")?)?;
    let cap_flats = n(&bfp.attr("CAP_ACROSS_FLATS")?)?;
    let turn = n(&at(&datums, "asse_turn")?)?;
    let mut wrenches: Vec<Wrench> = vec![];
    for (profile, across, clock) in [(&body_profile, hex, 0.3), (&cap_profile, cap_flats, 0.9)] {
        let first = profile.first().context("list index out of range")?[0];
        let last = profile.last().context("list index out of range")?[0];
        let ends = [at_frame(&frame, [first, zero, body_z])?[1], at_frame(&frame, [last, zero, body_z])?[1]];
        let y = if lt(ends[1], ends[0])? { [ends[1], ends[0]] } else { ends };
        wrenches.push(Wrench {
            y,
            half: across.div(Num::F(2.0)),
            clock: Num::F(clock).add(turn),
            corner: max_of(profile.iter().map(|p| p[1]))?,
        });
    }
    let mut widths = reached(&seat, cap_y)?;
    widths.extend(wrenches.iter().map(|w| w.corner.add(c)));
    let widest = max_args(widths)?;
    let split = ax[1].add(c);
    let half_width = snaps.attr("half_width")?.call(vec![widest.val(), split.val(), ax[1].val()], vec![])?;
    let wall = n(&snaps.attr("WALL")?)?;
    let st_asse = station.call(
        vec![ax[0].val(), n(&half_width)?.add(wall).val(), cap_y[0].val(), cap_y[1].val()],
        vec![
            ("split".into(), split.val()),
            ("wing_root".into(), ax[1].sub(n(&snaps.attr("REAR_ROOT_DROP")?)?).val()),
        ],
    )?;
    let wrench_rows = py::list(wrenches.iter().map(Wrench::val));
    let profile = snaps.attr("asse_cap_profile")?.call(vec![wrench_rows, s.val()], vec![])?;
    let capture = py::unpack(
        &snaps.attr("asse_adapter_capture")?.call(vec![frame.clone(), st_asse.clone(), axis.clone()], vec![])?,
        2,
    )?;
    let room = snaps
        .attr("asse_cap_room")?
        .call(vec![axis.clone(), profile, py::tuple([cap_y[0].val(), cap_y[1].add(Num::F(0.5)).val()])], vec![])?;
    let mut cuts = vec![section(&room)?, capture[1].clone()];
    let asse_pose = pose.call(vec![py::s("asse1022-assembly")], vec![])?;
    let vent = at(&at(&cap_profiles, "asse")?, "vent_bounds")?.iter()?;
    ensure!(vent.len() == 2, "_world_bounds() takes 3 positional arguments but {} were given", vent.len() + 1);
    let [lo, hi] = world_bounds(rt, &asse_pose, first3(&vent[0])?, first3(&vent[1])?)?;
    let thread = n(&snaps.attr("THREAD")?)?;
    cuts.push(boxed_nums([
        lo[0].sub(c),
        hi[0].add(c),
        lo[1].sub(thread).sub(c),
        hi[1].add(thread).add(c),
        lo[2].sub(Num::F(1.0)),
        ax[1],
    ]));
    let adapter = parts.attr("_module")?.call(
        vec![py::s("rear_cap_vent_adapter"), py::s("printed-parts/asse-drain-adapter/asse_drain_adapter.py")],
        vec![],
    )?;
    let barb = pow2(n(&adapter.attr("BARB_OD")?)?).add(pow2(n(&bfp.attr("VENT_D")?)?)).sub(pow2(n(&adapter.attr("BARB_BORE")?)?));
    let rb = Num::F(sqrt(barb.f())?).div(Num::F(2.0));
    let tube = pow2(n(&adapter.attr("TUBE_OD")?)?).add(pow2(Num::F(4.0))).sub(pow2(n(&adapter.attr("TUBE_BORE")?)?));
    let rt_tube = Num::F(sqrt(tube.f())?).div(Num::F(2.0));
    let tip = first3(&item(&bfp.attr("vent")?.call(vec![], vec![])?, 0)?)?;
    let sleeve_lo = [
        tip[0].sub(n(&adapter.attr("ELBOW_REACH")?)?),
        tip[1].sub(rb),
        tip[2].sub(n(&adapter.attr("SOCKET_DROP")?)?).sub(rt_tube),
    ];
    let sleeve_hi = [tip[0].add(rb), tip[1].add(rb), tip[2].add(n(&adapter.attr("INSTALLED_REACH")?)?)];
    let asse_pose = pose.call(vec![py::s("asse1022-assembly")], vec![])?;
    let [lower, upper] = world_bounds(rt, &asse_pose, sleeve_lo, sleeve_hi)?;
    cuts.push(boxed_nums([
        min2(lower[0], lo[0])?.sub(c),
        max2(upper[0], hi[0])?.add(c),
        min2(lower[1], lo[1])?.sub(thread).sub(c),
        max2(upper[1], hi[1])?.add(thread).add(c),
        lower[2].sub(Num::F(1.0)),
        upper[2].add(c),
    ]));
    let mut caps = vec![py::dict([
        ("name", py::s(NAMES[0])),
        ("section", cap_section.call(vec![st_asse, ax[1].val(), Val::None, ax[1].val(), Val::Bool(true)], vec![])?),
        ("stock", py::list([capture[0].clone()])),
        ("cuts", Val::list(cuts)),
        ("print_rotate_x", Val::Float(90.0)),
    ])];

    // The Pisco fitting's cap.
    let axis = at(&datums, "pisco_axis")?;
    let frame = at(&plan, "gas_frame")?;
    let ax = [n(&item(&axis, 0)?)?, n(&item(&axis, 1)?)?];
    let relief = n(&snaps.attr("PISCO_RADIAL_RELIEF")?)?;
    let seat = runs(&rows::<3>(&at(&at(&profiles, "pisco")?, "seat_runs")?)?, &frame, c.add(relief))?;
    let dims = at(&json_file(&st.hw.join("reference/compact-inline-candidates/dimensions.json"))?, "pisco_rvfup_quarter")?;
    let exterior = at(&dims, "fitted_exterior")?;
    let ranges = at(&exterior, "component_ranges_mm")?;
    let profile = at(&exterior, "profile_z_radius_mm")?;
    let (fitting, collet) = (at(&ranges, "outlet_fitting")?, at(&ranges, "outlet_collet")?);
    let radii = rows::<2>(&profile)?;
    let fitting_lo = n(&item(&fitting, 0)?)?;
    let mut neck = None;
    for &[z, r] in &radii {
        if gt(z, fitting_lo)? && lt(r, Num::F(6.5))? {
            neck = Some(z);
            break;
        }
    }
    let neck_z = neck.context("StopIteration")?;
    let mouth = at(&datums, "mouth_y")?;
    let collet_lo = item(&collet, 0)?;
    let cap_y = snaps.attr("pisco_cap_span")?.call(vec![mouth.clone(), collet_lo.clone(), at(&datums, "rear")?], vec![])?;
    let span = [n(&item(&cap_y, 0)?)?, n(&item(&cap_y, 1)?)?];
    let widest = max_of(reached(&seat, span)?)?;
    let mut args = vec![ax[0].val(), widest.val(), ax[1].val()];
    args.extend(cap_y.iter()?);
    let st_pisco = snaps.attr("pisco_station")?.call(args, vec![])?;
    let cap_air = n(&snaps.attr("PISCO_CAP_AIR")?)?;
    let mouth_y = n(&mouth)?;
    let body_low = mouth_y.sub(span[1]).sub(Num::F(1.0));
    let collet_z = n(&collet_lo)?;
    let mut body = vec![];
    let mut neck_rows = vec![];
    for &[z, r] in &radii {
        if le(body_low, z)? && le(z, neck_z)? {
            body.push(r);
        }
    }
    for &[z, r] in &radii {
        if le(neck_z, z)? && le(z, collet_z)? {
            neck_rows.push(r);
        }
    }
    let body_r = max_of(body)?.add(cap_air);
    let neck_r = max_of(neck_rows)?.add(cap_air);
    let lip = mouth_y.sub(neck_z).sub(s);
    let fit = snaps.attr("pisco_cap_fit")?.call(vec![profile, mouth, cap_y, axis, neck_z.val()], vec![])?;
    let mut cuts = vec![];
    for name in ["body", "neck"] {
        cuts.push(py::dict([
            ("op", py::s("radial-profile")),
            ("points", fit.get(py::s(name))?),
            ("frame", fit.get(py::s("frame"))?),
        ]));
    }
    let section_pisco =
        cap_section.call(vec![st_pisco.clone(), st_pisco.get(py::s("root"))?, ax[1].sub(body_r).sub(wall).val()], vec![])?;
    let grip = snaps.attr("pisco_grip_stock")?.call(vec![st_pisco, ax[1].val(), body_r.val(), neck_r.val(), lip.val()], vec![])?;
    let stock = grip.iter()?.iter().map(|b| boxed(b.iter()?)).collect::<Result<Vec<_>>>()?;
    caps.push(py::dict([
        ("name", py::s(NAMES[1])),
        ("section", section_pisco),
        ("stock", Val::list(stock)),
        ("cuts", Val::list(cuts)),
        ("print_rotate_x", Val::Float(90.0)),
    ]));

    // The Digiten flow meter's cap.
    let meter = plumbing
        .attr("reference")?
        .call(vec![py::s("cap_digiten"), py::s("reference/digiten-flow-sensor/digiten_flow_sensor.py")], vec![])?;
    let frame = pose.call(vec![py::s("digiten-flow")], vec![])?;
    let (centre_x, centre_z) = (n(&meter.attr("body_center_x")?)?, n(&meter.attr("body_center_z")?)?);
    let centre = at_frame(&frame, [centre_x, zero, centre_z])?;
    let port = at_frame(&frame, [zero, zero, zero])?;
    let (my, mz) = (centre[1], centre[2]);
    let soda = [port[0], port[2]];
    let wx = |y: Num| -> Result<Num> { Ok(at_frame(&frame, [centre_x, y, centre_z])?[0]) };
    let air = n(&snaps.attr("METER_AIR")?)?;
    let mx = wx(Num::F(7.3))?.sub(air);
    let spans = py::unpack(&plumbing.attr("meter_spans")?.call(vec![], vec![])?, 2)?;
    let (seat_y, cap_y) = (spans[0].clone(), spans[1].clone());
    let collar = max_of(meter.attr("port_collar_radii")?.iter()?.iter().map(n).collect::<Result<Vec<_>>>()?)?;
    let _core = wx(n(&item(&meter.attr("boss_y_range")?, 0)?)?)?.sub(air);
    let west = wx(n(&meter.attr("underside_y")?)?)?;
    let mut args = vec![Val::Float(0.0), soda[1].add(collar).add(air).sub(mz).add(wall).val()];
    args.extend(cap_y.iter()?);
    let st_meter = station.call(
        args,
        vec![("split".into(), Val::Float(0.0)), ("wing_root".into(), west.sub(air).sub(mx).val())],
    )?;
    let housing_fit = snaps.attr("METER_HOUSING_FIT")?;
    let clearance = snaps
        .attr("clearance_profile")?
        .call(vec![meter.attr("housing_profile")?, housing_fit.clone(), housing_fit.clone()], vec![])?;
    let mut housing = vec![];
    for row in clearance.iter()? {
        let pair = py::unpack(&row, 2)?;
        housing.push(py::tuple([wx(n(&pair[0])?)?.val(), pair[1].clone()]));
    }
    let rotation = py::tuple([py::ftuple(&[1., 0., 0.]), py::ftuple(&[0., 1., 0.]), py::ftuple(&[0., 0., 1.])]);
    let mut cuts = vec![
        py::dict([
            ("op", py::s("radial-profile")),
            ("points", Val::list(housing)),
            (
                "frame",
                py::dict([("rotation", rotation), ("translation_mm", py::tuple([Val::Float(0.0), my.val(), mz.val()]))]),
            ),
        ]),
        py::dict([
            ("op", py::s("cylinder-y")),
            ("centre", py::tuple([soda[0].val(), soda[1].val()])),
            ("radius", n(&meter.attr("port_neck_radius")?)?.add(n(&housing_fit)?).val()),
            ("span", seat_y),
        ]),
    ];
    let bottom = west.sub(air).sub(n(&snaps.attr("METER_BACK")?)?).sub(mx);
    let half = n(&st_meter.get(py::s("inner"))?)?.sub(n(&snaps.attr("ROOT_RADIUS")?)?).sub(Num::F(0.5));
    let corner = snaps.attr("meter_cap_corner_room")?.call(vec![mx.add(bottom).val(), mz.val(), cap_y.clone()], vec![])?;
    cuts.push(section(&corner)?);
    let section_meter = cap_section.call(vec![st_meter.clone(), st_meter.get(py::s("root"))?, bottom.val()], vec![])?;
    let mut bounds = vec![half.neg().val(), half.val()];
    bounds.extend(cap_y.iter()?);
    bounds.push(bottom.val());
    bounds.push(n(&st_meter.get(py::s("root"))?)?.add(n(&snaps.attr("METER_BEARING_DEPTH")?)?).val());
    caps.push(py::dict([
        ("name", py::s(NAMES[2])),
        ("section", section_meter),
        ("stock", py::list([boxed(bounds)?])),
        (
            "placement",
            py::dict([("rotate_y", Val::Float(90.0)), ("translation", py::tuple([mx.val(), Val::Float(0.0), mz.val()]))]),
        ),
        ("cuts", Val::list(cuts)),
        ("print_rotate_x", Val::Float(90.0)),
    ]));

    // The CO2 regulator's cap.
    let mount = plumbing.attr("regulator_datums")?.call(vec![], vec![])?;
    let st_regulator = mount.get(py::s("station"))?;
    mount.get(py::s("axis"))?;
    let section_regulator = cap_section.call(
        vec![st_regulator.clone(), st_regulator.get(py::s("root"))?, mount.get(py::s("cap_bottom"))?],
        vec![],
    )?;
    let stock = mount.get(py::s("cap_stock"))?.iter()?.iter().map(|b| boxed(b.iter()?)).collect::<Result<Vec<_>>>()?;
    let cuts = vec![py::dict([
        ("op", py::s("radial-profile")),
        ("points", mount.get(py::s("cap_profile"))?),
        ("frame", mount.get(py::s("profile_frame"))?),
    ])];
    caps.push(py::dict([
        ("name", py::s(NAMES[3])),
        ("section", section_regulator),
        ("stock", Val::list(stock)),
        ("cuts", Val::list(cuts)),
        ("rotate_z", Val::Float(90.0)),
        ("print_rotate_y", Val::Float(90.0)),
    ]));
    Ok(py::dict([("caps", Val::list(caps)), ("color", st.linear.call(vec![st.petgf_black.clone()], vec![])?)]))
}

/// The part's run: the four caps cut by the part program into this directory.
pub fn main(rt: &Rt) -> Result<()> {
    let st = state(rt)?;
    let rust_part = rt.import("_rust_part")?;
    let cut = rust_part.attr("cut")?;
    let result = cut.call(
        vec![py::s("enclosure-components"), py::s("rear-equipment-caps"), numbers(rt)?, Val::Path(st.here.clone())],
        vec![],
    )?;
    let print = interop::builtin("print").context("print")?;
    for file in at(&result, "files")?.iter()? {
        print.call(vec![Val::Str(format!("-> {}", num::fmtv(&file, "")?))], vec![("flush".into(), Val::Bool(true))])?;
    }
    Ok(())
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("json", rt.import("json")?)?;
    ns.set("math", rt.import("math")?)?;
    rt.import("pathlib")?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let sys = rt.import("sys")?;
    ns.set("sys", sys.clone())?;
    let file = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let here = file.parent().unwrap_or(&file).to_path_buf();
    ns.set("HERE", Val::Path(here.clone()))?;
    let hw = here
        .ancestors()
        .skip(1)
        .find(|p| p.file_name().is_some_and(|name| name == "hardware"))
        .map(Path::to_path_buf)
        .context("StopIteration")?;
    ns.set("HW", Val::Path(hw.clone()))?;
    let front = ["manifold-layout", "scripts", "printed-parts/cadlib"].map(|p| py::s(py::path_str(&hw.join(p))));
    sys.attr("path")?.set(Val::Slice { start: None, stop: Some(0), step: 1 }, py::list(front))?;
    py::sys_path_insert(rt, &py::path_str(&hw.join("printed-parts/cold-core")))?;
    let rear_plumbing = rt.import("rear_plumbing")?;
    ns.set("rear_plumbing", rear_plumbing.clone())?;
    rt.import("_materials")?;
    let petgf_black = rt.member("_materials", "M_PETGF_BLACK")?;
    ns.set("M_PETGF_BLACK", petgf_black.clone())?;
    let linear = rt.member("_materials", "linear")?;
    ns.set("linear", linear.clone())?;
    ns.set("NAMES", py::tuple(NAMES.map(py::s)))?;
    rt.keep(MODULE, State { here, hw, rear_plumbing, petgf_black, linear });

    ns.def(rt, "_world_bounds", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["frame", "lo", "hi"], &[])?;
        let (frame, lo, hi) = (b.req("frame")?, b.req("lo")?, b.req("hi")?);
        let [lo, hi] = world_bounds(rt, &frame, first3(&lo)?, first3(&hi)?)?;
        Ok(py::tuple([Num::vals(&lo), Num::vals(&hi)]))
    })?;
    ns.def(rt, "numbers", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        numbers(rt)
    })?;
    ns.def(rt, "main", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        main(rt)?;
        Ok(Val::None)
    })?;
    Ok(())
}

/// `if __name__ == '__main__':` — the part's own run.
pub fn main_block(rt: &Rt) -> Result<()> {
    let ns = rt.namespace(MODULE)?;
    let rust_part = rt.import("_rust_part")?;
    ns.set("_rust_part", rust_part.clone())?;
    rust_part.attr("start")?.call(vec![], vec![])?;
    main(rt)
}
