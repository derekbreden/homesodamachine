//! Case-derived locating profiles for the integral pump inverse and lower retainer.
//!
//! The lower retainer has flat lands around the rigid eight-millimetre molded skirt.
//! Front-top's integral upper inverse locates the rear boss and clears the motor can.
//! The production geometry consumes these profiles in enclosure._fixed_pump_mount.
//!
//! The accepted earlier cradle/cap assembly held both physical pumps firmly without observed
//! vertical play; hardware/reference/kamoer-kphm400/physical-fit.json binds that identified
//! article. It does not qualify the integral upper/lower skirt capture. This module's collar
//! builder is a source solid, not a separate printed part. The physical reference is
//! hardware/reference/kamoer-kphm400/scan-review.md; case-derived geometry alone does not
//! independently establish physical contact.
//!
//! Run:
//!     tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-tray/pump_tray.py selftest
//!
//! Typed API: [`state`] holds the collar stock as a [`Stock`] (`pump-tray-defaults`, the names
//! the module's `globals().update(_stock)` binds) and that reply as JSON. [`depth`],
//! [`half_width`], [`far_reach`], [`outlet_fore_miter`], [`outlet_under_tangent`],
//! [`outlet_passage_start_y`] and [`numbers`] are the recipe figures; the CadQuery builders take
//! and return CadQuery objects as `Val`. Front-top replaces `boss_room` in this namespace while it
//! records (`_replace(shell._tray, {'boss_room': ...})`): a typed caller reaches it through
//! [`installed_boss_room`], which reads the name each call.
use super::num::{self, Num};
use super::pump_case;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result, anyhow, ensure};
use serde_json::{Map, Value, json};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "pump_tray";

/// The reference pump's dimensions `_pump_source()` reads off `kamoer_kphm400`, in its order.
const PUMP: [&str; 25] = [
    "barb_pitch",
    "base_plane_z",
    "bracket_t",
    "bracket_w",
    "head_depth",
    "head_front_below_skirt",
    "head_front_z",
    "head_w",
    "motor_dia",
    "motor_end_z",
    "outlet_relief",
    "outlet_relief_run",
    "outlet_span_x",
    "rear_axis_y_shift",
    "skirt_body_y",
    "skirt_body_y_max",
    "skirt_body_y_min",
    "skirt_depth",
    "skirt_support_xy_air",
    "skirt_support_y_minus",
    "skirt_upper_band",
    "skirt_y",
    "skirt_y_max",
    "skirt_y_plus_air",
    "tube_casing_w",
];

macro_rules! stock {
    ($($name:ident),* $(,)?) => {
        /// The collar stock, as `pump-tray-defaults` states it: every name the module's
        /// `globals().update(_stock)` binds.
        #[allow(non_snake_case)]
        #[derive(Clone, Debug)]
        pub struct Stock {
            $(pub $name: f64,)*
            pub skirt_body_open_y_bounds: [f64; 2],
        }
        impl Stock {
            fn of(v: &Value) -> Result<Stock> {
                let number = |key: &str| v[key].as_f64().with_context(|| format!("{key} is numeric"));
                let bounds = v["skirt_body_open_y_bounds"].as_array().context("skirt_body_open_y_bounds")?;
                ensure!(bounds.len() == 2, "skirt_body_open_y_bounds has two ends");
                Ok(Stock {
                    $($name: number(stringify!($name))?,)*
                    skirt_body_open_y_bounds: [
                        bounds[0].as_f64().context("a skirt body bound")?,
                        bounds[1].as_f64().context("a skirt body bound")?,
                    ],
                })
            }
        }
    };
}
stock!(
    PLATE,
    SHOULDER,
    boss_depth,
    boss_half,
    bracket_half,
    bracket_t,
    can_half,
    case_half,
    fitting_w,
    head_depth,
    head_front_below_skirt,
    head_front_z,
    head_half,
    motor_crown,
    outlet_axis_z,
    outlet_half,
    outlet_open_half,
    outlet_pitch,
    outlet_relief,
    outlet_relief_run,
    rear_axis_y_shift,
    shaft_w,
    skirt_body_open_y,
    skirt_body_y,
    skirt_depth,
    skirt_open_y_max,
    skirt_support_air,
    skirt_support_band,
    skirt_support_xy_air,
    skirt_support_y_minus,
    skirt_support_y_plus,
    skirt_upper_band,
    skirt_y,
    skirt_y_plus_air,
);

/// The module's typed state.
pub struct State {
    pub stock: Stock,
    /// `_stock`: the defaults reply, as `_data` sends it back as `stock`.
    pub json: Value,
    /// `_pump_source()` as a recipe receives it.
    pump: Value,
    /// `_here`: this module's file.
    here: PathBuf,
    cq: Val,
    kp: Val,
}

/// The module's state, initializing the module on first use.
pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// `_read(op, **values)`: this crate's own recipe, answered in this process. A recipe's error
/// reads as the worker round trip raises it.
fn read(rt: &Rt, request: Value) -> Result<Value> {
    rt.enclosure_data(request).map_err(|error| anyhow!("ValueError: enclosure-data: {error:#}"))
}

/// `_data(op, **values)`: a `pump-tray-` recipe on the pump, the case and this module's stock.
fn data(rt: &Rt, op: &str, values: Map<String, Value>) -> Result<Value> {
    let st = state(rt)?;
    let mut request = Map::new();
    request.insert("op".into(), json!(format!("pump-tray-{op}")));
    request.insert("pump".into(), st.pump.clone());
    request.insert("case".into(), pump_case::state(rt)?.json.clone());
    request.insert("stock".into(), st.json.clone());
    for (key, value) in values {
        ensure!(
            !matches!(key.as_str(), "pump" | "case" | "stock"),
            "read() got multiple values for keyword argument '{key}'"
        );
        request.insert(key, value);
    }
    read(rt, Value::Object(request))
}
fn air(value: Value) -> Map<String, Value> {
    Map::from_iter([("air".to_owned(), value)])
}
fn four(v: &Value) -> Result<[f64; 4]> {
    let rows = v.as_array().context("four figures")?;
    ensure!(rows.len() == 4, "expected four figures, got {}", rows.len());
    let mut out = [0.; 4];
    for (slot, x) in out.iter_mut().zip(rows) {
        *slot = x.as_f64().context("a figure")?;
    }
    Ok(out)
}
/// `tuple(values)` of a recipe's list, each number as the JSON holds it.
fn tuple_of(v: Value) -> Result<Val> {
    match v {
        Value::Array(rows) => Ok(Val::Tuple(rows.into_iter().map(py::from_json).collect::<Result<_>>()?)),
        other => py::from_json(other)?.iter().map(Val::Tuple),
    }
}

/// `next(p for p in path.parents if test(p))`.
fn ancestor(path: &Path, test: impl Fn(&Path) -> bool) -> Result<PathBuf> {
    path.ancestors().skip(1).find(|p| test(p)).map(Path::to_owned).context("StopIteration")
}
fn name_of(path: &Path) -> String {
    path.file_name().map(|v| v.to_string_lossy().to_string()).unwrap_or_default()
}
/// `path.parent`.
fn parent(path: &Path) -> PathBuf {
    path.parent().unwrap_or(path).to_owned()
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    ns.set("_here", Val::Path(here.clone()))?;
    let hw = ancestor(&here, |p| name_of(p) == "hardware")?;
    ns.set("_hw", Val::Path(hw.clone()))?;
    for p in [hw.join("scripts"), hw.join("reference").join("kamoer-kphm400"), parent(&here)] {
        ns.set("_p", Val::Path(p.clone()))?;
        py::sys_path_insert(rt, &py::path_str(&p))?;
    }
    let tools = ancestor(&here, |p| p.join("tools").join("docgen").is_dir())?;
    py::sys_path_insert(rt, &py::path_str(&tools.join("tools")))?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let kp = rt.import("kamoer_kphm400")?;
    ns.set("_kp", kp.clone())?;
    ns.set("_pc", rt.import("pump_case")?)?;
    let fits = rt.import("fits")?;
    ns.set("fits", fits.clone())?;
    ns.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    py::sys_path_insert(rt, &py::path_str(&hw.join("printed-parts/enclosure/enclosure")))?;
    ns.set("_read", rt.member("_enclosure_data", "read")?)?;

    // `_pump_source()` reads module constants of the reference pump: read once, kept.
    let mut source = vec![];
    for name in PUMP {
        source.push((name, py::snapshot(&kp.attr(name)?)?));
    }
    let pump = Value::Object(source.iter().map(|(k, v)| Ok(((*k).to_owned(), py::plain(v)?))).collect::<Result<_>>()?);
    let source = Rc::new(source);
    ns.def(rt, "_pump_source", move |_rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(py::dict(source.iter().map(|(k, v)| (*k, v.clone()))))
    })?;
    let running = py::plain(&fits.attr("running")?)?;
    let case = pump_case::state(rt)?.json.clone();
    let reply = read(rt, json!({"op": "pump-tray-defaults", "pump": pump, "case": case, "fits": {"running": running}}))?;
    let stock_dict = py::from_json(reply.clone())?;
    ns.set("_stock", stock_dict.clone())?;
    // globals().update(_stock): the dict's own values.
    let rows = reply.as_object().context("the pump tray stock is a mapping")?;
    for key in rows.keys() {
        ns.set(key, py::item(&stock_dict, py::s(key.clone()))?)?;
    }
    ns.set("_stock_names", Val::Tuple(rows.keys().map(|k| py::s(k.clone())).collect()))?;
    let stock = Stock::of(&reply)?;
    rt.keep(MODULE, State { stock, json: reply, pump, here, cq, kp });

    ns.def(rt, "_data", |rt, args, mut kwargs| {
        ensure!(args.len() <= 1, "_data() takes 1 positional argument but {} were given", args.len());
        let op = match args.into_iter().next() {
            Some(op) => {
                ensure!(!kwargs.iter().any(|(k, _)| k == "op"), "_data() got multiple values for argument 'op'");
                op
            }
            None => {
                let at = kwargs.iter().position(|(k, _)| k == "op").context("_data() missing 1 required positional argument: 'op'")?;
                kwargs.remove(at).1
            }
        };
        let mut values = Map::new();
        for (key, value) in kwargs {
            values.insert(key, py::plain(&value)?);
        }
        py::from_json(data(rt, &op.str()?, values)?)
    })?;
    ns.def(rt, "depth", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        py::from_json(data(rt, "depth", Map::new())?)
    })?;
    ns.def(rt, "half_width", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Float(half_width(rt)?))
    })?;
    ns.def(rt, "far_reach", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Float(far_reach(rt)?))
    })?;
    ns.def(rt, "_in_pump_frame", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["solid"], &[])?;
        in_pump_frame(rt, &b.req("solid")?)
    })?;
    ns.def(rt, "head_room", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["air"], &[])?;
        head_room(rt, b.f64("air")?)
    })?;
    ns.def(rt, "outlet_fore_miter", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["air"], &[])?;
        tuple_of(data(rt, "miter", air(py::plain(&b.req("air")?)?))?)
    })?;
    ns.def(rt, "outlet_under_tangent", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["air"], &[])?;
        tuple_of(data(rt, "tangent", air(py::plain(&b.req("air")?)?))?)
    })?;
    ns.def(rt, "_outlet_span_extensions", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["air"], &[])?;
        Ok(outlet_span_extensions(rt, b.f64("air")?)?.unwrap_or(Val::None))
    })?;
    ns.def(rt, "outlet_passage_start_y", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["air"], &[])?;
        py::from_json(data(rt, "passage", air(py::plain(&b.req("air")?)?))?)
    })?;
    ns.def(rt, "drop_well", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["air", "support_top"], &[])?;
        let air = b.f64("air")?;
        let support_top = b.some("support_top").map(|v| Num::of(&v)).transpose()?;
        drop_well(rt, air, support_top)
    })?;
    ns.def(rt, "boss_room", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["air"], &[])?;
        boss_room(rt, b.f64("air")?)
    })?;
    ns.def(rt, "_case_base", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        case_base(rt)
    })?;
    ns.def(rt, "_slab", |rt, args, kwargs| {
        const NAMES: [&str; 6] = ["x0", "x1", "y0", "y1", "z0", "z1"];
        let mut b = py::bind(args, kwargs, &NAMES, &[])?;
        let mut bounds = [Num::I(0); 6];
        for (slot, name) in bounds.iter_mut().zip(NAMES) {
            *slot = Num::of(&b.req(name)?)?;
        }
        let st = state(rt)?;
        slab(&st, bounds)
    })?;
    ns.def(rt, "build_pump_tray", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["root"], &[])?;
        build_pump_tray(rt, b.f64("root")?)
    })?;
    ns.def(rt, "pump_bodies", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Tuple(pump_bodies(rt)?))
    })?;
    ns.def(rt, "fouled_volume", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["root"], &[])?;
        Ok(fouled_volume(rt, b.f64("root")?)?.val())
    })?;
    ns.def(rt, "storeys", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["root"], &[])?;
        Ok(py::ftuple(&storeys(rt, b.f64("root")?)?))
    })?;
    ns.def(rt, "trays_of_machine", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["facts"], &[])?;
        trays_of_machine(&b.req("facts")?)
    })?;
    ns.def(rt, "numbers", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["trays"], &[])?;
        py::from_json(numbers(rt, py::plain(&b.req("trays")?)?)?)
    })?;
    ns.def(rt, "selftest", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Int(selftest(rt)?))
    })?;
    ns.def(rt, "main", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        main(rt)?;
        Ok(Val::None)
    })?;
    Ok(())
}

pub fn main_block(rt: &Rt) -> Result<()> {
    let ns = rt.namespace(MODULE)?;
    let rust_part = rt.import("_rust_part")?;
    ns.set("_rust_part", rust_part.clone())?;
    py::method(&rust_part, "start", vec![])?;
    let sys = rt.import("sys")?;
    let argv = py::snapshot(&sys.attr("argv")?)?.iter()?;
    if argv.len() > 1 && matches!(&argv[1], Val::Str(arg) if arg == "selftest") {
        py::call(&sys.attr("exit")?, vec![Val::Int(selftest(rt)?)])?;
    }
    main(rt)
}

/// The tray's whole run along the pump's axis — the bore on the boss, and one `SHOULDER` of
/// tower over its crown. What the piece has to own in height to build one.
pub fn depth(rt: &Rt) -> Result<f64> {
    data(rt, "depth", Map::new())?.as_f64().context("the tray depth is numeric")
}

/// Half the tray across — the case's own footprint.
pub fn half_width(rt: &Rt) -> Result<f64> {
    Ok(state(rt)?.stock.case_half)
}

/// How far the tray runs off the pump's axis away from the wall it roots on — the case's own
/// footprint, which already carries past the head.
pub fn far_reach(rt: &Rt) -> Result<f64> {
    Ok(state(rt)?.stock.case_half)
}

/// One of `pump_case`'s own solids carried into this module's frame — the case states its
/// footprint from a corner and this module states everything off the pump's axis.
fn in_pump_frame(rt: &Rt, solid: &Val) -> Result<Val> {
    let case = pump_case::state(rt)?;
    let c = &case.case;
    py::method(solid, "translate", vec![py::ftuple(&[-c.center_x, -c.center_y, 0.0])])
}

/// THE ROOM THE CASE LEAVES A HEAD, struck `air` off it — `pump_case.cavity` in this
/// module's frame.
///
/// IT IS ASYMMETRIC IN Y AND THE TWO HALVES ARE DIFFERENT WIDTHS ACROSS.
/// `pump_case.skirt_narrow_half_extent` on -Y, `skirt_base_half_extent` at the centre,
/// `skirt_wide_half_extent` on +Y, which is the OUTLET side: 56 mm across at the narrow end,
/// 64 at the centre, 70 at the outlet face. The complete pump stands widest at that same
/// face. The built-in tube casings stand outside that body room on their own 72.50 mm physical
/// span; the holder's 13.25 mm openings span 73 mm.
///
/// THE FITTED FACES COME WITH IT. The narrow-side skirt transition is one horizontal step
/// 8 mm below the bracket plane; `kamoer_kphm400.build_head` clips the pump to this same
/// figure. The lower extension keeps its case-derived sections below that step.
pub fn head_room(rt: &Rt, air: f64) -> Result<Val> {
    let st = state(rt)?;
    let s = &st.stock;
    let bounds = py::flist(&s.skirt_body_open_y_bounds);
    let room = pump_case::stepped_skirt_cavity(rt, air, Num::F(-s.skirt_depth), &bounds, Num::F(s.skirt_open_y_max))?;
    in_pump_frame(rt, &room)
}

/// The passages' fore-seam figures, one set for every construction that closes them.
///
/// ``(body_half, y0, outlet_open_half, y_open)``: the case-derived tube-side room edge, the
/// seam where each passage begins, the 73 mm envelope's half-span, and the y where the
/// flare's own 45 degree seam plane, carried past the room edge, reaches that envelope.
pub fn outlet_fore_miter(rt: &Rt, air_mm: f64) -> Result<[f64; 4]> {
    four(&data(rt, "miter", air(json!(air_mm)))?)
}

/// The passages' under-circle joint figures, one set for the construction that opens it.
///
/// ``(seam_z, u_wall, u_q, z_q)``: the case lower ramp's seam plane under the tube-side room,
/// how far that room's edge stands outboard of each tube axis, and where the plane rising
/// from the seam edge tangent to the r = ``shaft_w``/2 circular opening touches it — the
/// steep outer tangent, the one planar shelf-free joint between the room's seam and the
/// circle. ``u`` figures stand outboard of a tube axis; ``z`` figures are this frame's own.
pub fn outlet_under_tangent(rt: &Rt, air_mm: f64) -> Result<[f64; 4]> {
    four(&data(rt, "tangent", air(json!(air_mm)))?)
}

/// The two X strips which carry the tube-side room to its 73 mm opening envelope.
///
/// The matching circle-and-shaft cutters begin at ``outlet_passage_start_y`` and overlap these
/// strips over their whole run: one tangent opening. Keeping the middle closed preserves the
/// printed web between the two passages.
fn outlet_span_extensions(rt: &Rt, air_mm: f64) -> Result<Option<Val>> {
    let st = state(rt)?;
    let [body_half, y0, open_half, _y_open] = outlet_fore_miter(rt, air_mm)?;
    if open_half <= body_half + 1e-9 {
        return Ok(None);
    }
    let y1 = body_half;
    let (z0, z1) = (st.stock.outlet_axis_z, 0.0);

    let slab = |x0: f64, x1: f64| -> Result<Val> {
        let wp = py::call(&st.cq.attr("Workplane")?, vec![py::s("XY")])?;
        let size = vec![Val::Float(x1 - x0), Val::Float(y1 - y0), Val::Float(z1 - z0)];
        let block = py::call_kw(&wp.attr("box")?, size, vec![("centered", Val::Bool(false))])?;
        py::method(&block, "translate", vec![py::ftuple(&[x0, y0, z0])])
    };

    let fore = slab(-open_half, -body_half)?;
    Ok(Some(py::method(&fore, "union", vec![slab(body_half, open_half)?])?))
}

/// The tube-side seam where each complete circle-and-shaft passage begins.
pub fn outlet_passage_start_y(rt: &Rt, air_mm: f64) -> Result<f64> {
    data(rt, "passage", air(json!(air_mm)))?.as_f64().context("the passage start is numeric")
}

/// THE ROOM A PUMP IS LOWERED THROUGH, struck `air` off the case — `pump_case.drop_well`
/// in this module's frame.
///
/// ``air`` offsets the case profile laterally; the lower 45-degree flanks therefore
/// have ``air / sqrt(2)`` normal separation without moving their axial stations.
/// The 8 mm skirt lands over one flat horizontal support plane, with ``skirt_support_air``
/// below it. A continuous ``skirt_support_band`` land holds its X-, X+ and Y- flanks. The
/// measured 54 mm body passes through a 54.5 mm Y opening, leaving 4.9 mm of land on Y- and
/// 3.382 mm on Y+; there the two tube passages leave support only between their inside edges.
/// Those passages continue to the same 73 mm boundary as the upper well, with no flare or
/// fractional X step.
pub fn drop_well(rt: &Rt, air_mm: f64, support_top: Option<Num>) -> Result<Val> {
    let st = state(rt)?;
    let s = &st.stock;
    let support_top = support_top.unwrap_or(Num::F(-(s.skirt_depth + s.skirt_support_air)));
    let bounds = py::flist(&s.skirt_body_open_y_bounds);
    let well = pump_case::stepped_skirt_drop_well(rt, air_mm, support_top, &bounds, Num::F(s.skirt_open_y_max))?;
    let room = in_pump_frame(rt, &well)?;
    match outlet_span_extensions(rt, air_mm)? {
        None => Ok(room),
        Some(extensions) => py::method(&room, "union", vec![extensions]),
    }
}

/// The room the clamp's pressing plate leaves one boss, in this module's frame — the
/// case's own bore struck `air` off it over the boss's whole depth.
///
/// IT IS THE BORE'S FIGURE AND NOT A BOX ROUND IT. The boss is an octagon with a ledge on
/// four of its faces, and a block that took a square out for it left the square's four
/// corners standing outside everything that goes back in: the tray's ramp closes them
/// underneath, the tray's bore wall and tower wall them inboard, and the block's own fill
/// closes them where the can begins. The octagonal collar walls, rather than this cutter,
/// carry the fitted location.
fn boss_room(rt: &Rt, air_mm: f64) -> Result<Val> {
    let st = state(rt)?;
    let bore = pump_case::offset_polygon(rt, &pump_case::state(rt)?.case.bore_profile, air_mm)?;
    let ring = pump_case::profile_val(&pump_case::ring(rt, &bore)?);
    let wp = py::call(&st.cq.attr("Workplane")?, vec![py::s("XY")])?;
    let wire = py::method(&py::method(&wp, "polyline", vec![ring])?, "wire", vec![])?;
    py::method(&py::method(&wire, "extrude", vec![Val::Float(st.stock.boss_depth)])?, "val", vec![])
}
/// `boss_room(air)` as this namespace holds it now: front-top replaces the name while it
/// records, so a typed caller reads it each call.
pub fn installed_boss_room(rt: &Rt, air_mm: Val) -> Result<Val> {
    py::call(&rt.namespace(MODULE)?.get("boss_room")?, vec![air_mm])
}

/// `pump_case`'s BASE, in that module's own frame: the calls `build_pump_case` makes for
/// everything standing on the head's crown, and none of the skirt below it.
///
/// The bore is left for `build_pump_tray` to cut. The case bores its own one `overcut` past the
/// boss, which is what pierces a cut cleanly through to the skirt below; here there is no skirt
/// under it and that overcut is the shoulder standing off the crown it is meant to land on.
fn case_base(rt: &Rt) -> Result<Val> {
    let solid = pump_case::build_base_plate_with_ramp(rt)?;
    let solid = pump_case::add_bore_wall(rt, &solid)?;
    py::method(&solid, "union", vec![pump_case::build_tower(rt)?])
}

/// One box, in `pump_case`'s frame.
fn slab(st: &State, [x0, x1, y0, y1, z0, z1]: [Num; 6]) -> Result<Val> {
    let wp = py::call(&st.cq.attr("Workplane")?, vec![py::s("XY")])?;
    let size = vec![x1.sub(x0).val(), y1.sub(y0).val(), z1.sub(z0).val()];
    let block = py::call_kw(&wp.attr("box")?, size, vec![("centered", Val::Bool(false))])?;
    py::method(&block, "translate", vec![Num::vals(&[x0, y0, z0])])
}

/// One tray, in the pump's own frame.
///
/// `root` is how far the plate runs from the pump's axis toward the wall it stands on — the
/// piece's figure, since where that wall is is not the pump's business.
pub fn build_pump_tray(rt: &Rt, root: f64) -> Result<Val> {
    let st = state(rt)?;
    let s = &st.stock;
    let case = pump_case::state(rt)?;
    let c = &case.case;
    let (cx, cy, hw, fr, d) = (c.center_x, c.center_y, half_width(rt)?, far_reach(rt)?, depth(rt)?);
    let big = num::max_of([hw, fr, root]).context("max of nothing")? + s.case_half + 10.0;
    let f = Num::F;
    // The case-derived collar follows the physical boss and can, while the broad pressing plate
    // and its root remain struck from the head datum. This is the same split datum the pump
    // reference exposes: lower/head geometry at the origin, rear stack at `rear_axis_y_shift`.
    let tray = py::method(&case_base(rt)?, "translate", vec![py::ftuple(&[0.0, s.rear_axis_y_shift, 0.0])])?;
    // CUT OFF THE CYLINDER, and then more: the tower down to one `SHOULDER` over the boss's crown.
    let cylinder = slab(&st, [f(cx - big), f(cx + big), f(cy - big), f(cy + big), f(d), f(d + big)])?;
    let tray = py::method(&tray, "cut", vec![cylinder])?;
    // AND CARRY THE PLATE OUT to the case's own footprint, then re-cut the bore the plate just
    // filled back in.
    let plate = slab(&st, [f(cx - hw), f(cx + hw), f(cy - root), f(cy + fr), f(0.0), f(c.base_thickness)])?;
    let tray = py::method(&tray, "union", vec![plate])?;
    // THE BORE, on the boss's own depth exactly, so the shoulder over it lands ON the crown. Its
    // top face stands inside the tower's material, which is what a cut needs instead of the
    // overcut that would pierce free air here.
    let bore = py::call(&st.cq.attr("Workplane")?, vec![py::s("XY")])?;
    let bore = py::call_kw(&bore.attr("workplane")?, vec![], vec![("offset", Val::Float(-1.0))])?;
    let bore = py::method(&bore, "center", vec![Val::Float(cx), Val::Float(cy + s.rear_axis_y_shift)])?;
    let ring = pump_case::profile_val(&pump_case::ring(rt, &c.bore_profile)?);
    let bore = py::method(&py::method(&bore, "polyline", vec![ring])?, "wire", vec![])?;
    let bore = py::method(&bore, "extrude", vec![Val::Float(s.boss_depth + 1.0)])?;
    let tray = py::method(&tray, "cut", vec![bore])?;
    // AND THE TRAY STOPS ON THE FACE IT ROOTS ON, so it meets the wall plane to plane.
    let wall = slab(&st, [f(cx - big), f(cx + big), f(cy - root - big), f(cy - root), f(-1.0), f(d + 1.0)])?;
    let tray = py::method(&tray, "cut", vec![wall])?;
    py::method(&tray, "translate", vec![py::ftuple(&[-cx, -cy, 0.0])])
}

/// The reference pump's three solids, moved onto the tray's own origin — `kamoer_kphm400`
/// draws them on the case's footprint centre, and this frame stands on the pump's axis.
pub fn pump_bodies(rt: &Rt) -> Result<Vec<Val>> {
    let st = state(rt)?;
    let mut out = vec![];
    for row in st.kp.attr("BODY_PARTS")?.iter()? {
        let row = py::unpack(&row, 3)?;
        let body = py::method(&py::call(&row[1], vec![])?, "val", vec![])?;
        let (x, y) = (Num::of(&st.kp.attr("cx")?)?, Num::of(&st.kp.attr("cy")?)?);
        out.push(py::method(&body, "translate", vec![Val::Tuple(vec![x.neg().val(), y.neg().val(), Val::Float(0.0)])])?);
    }
    Ok(out)
}

/// How much of the pump a tray stands inside — 0 mm³, or the tray is in the pump's way.
///
/// The bore is the section the boss is extruded on, so the two share their eight walls; the
/// plate's face lands on the head's crown and the shoulder's on the boss's, which are planes;
/// and the can turns in a bore the case cuts wider than it.
pub fn fouled_volume(rt: &Rt, root: f64) -> Result<Num> {
    let tray = py::method(&build_pump_tray(rt, root)?, "val", vec![])?;
    let mut volumes = vec![];
    for body in pump_bodies(rt)? {
        volumes.push(Num::of(&py::method(&py::method(&tray, "intersect", vec![body])?, "Volume", vec![])?)?);
    }
    Ok(volumes.into_iter().fold(Num::I(0), Num::add))
}

/// The tray's material on each of the two faces it covers, as `(on the head, on the crown)`
/// in mm² of section — the reading that says a tray wraps BOTH storeys of the pump and not one.
///
/// Read a hair above each face, so what is measured is the tray standing on it.
pub fn storeys(rt: &Rt, root: f64) -> Result<[f64; 2]> {
    let st = state(rt)?;
    let tray = py::method(&build_pump_tray(rt, root)?, "val", vec![])?;
    let mut out = [0.; 2];
    for (slot, z) in out.iter_mut().zip([0.0, st.stock.boss_depth]) {
        let wp = py::call(&st.cq.attr("Workplane")?, vec![py::s("XY")])?;
        let size = vec![Val::Float(1000.0), Val::Float(1000.0), Val::Float(0.02)];
        let sheet = py::call_kw(&wp.attr("box")?, size, vec![("centered", Val::Bool(true))])?;
        let sheet = py::method(&py::method(&sheet, "translate", vec![py::ftuple(&[0.0, 0.0, z + 0.05])])?, "val", vec![])?;
        let cut = py::method(&tray, "intersect", vec![sheet])?;
        *slot = py::method(&cut, "Volume", vec![])?.num()? / 0.02;
    }
    Ok(out)
}

/// The collar sources the enclosure places, as `{name: root}` — one off each pump, as the
/// artifact carries them from the run that stood the machine.
///
/// The doc-only `main` hands in the artifact. Keeping that run dependency in `main` leaves
/// the shape functions' source closure at this part.
pub fn trays_of_machine(facts: &Val) -> Result<Val> {
    facts.attr("pump_trays")
}

/// The case's original polygon stock, axial stations and the machine's collar roots.
pub fn numbers(rt: &Rt, trays: Value) -> Result<Value> {
    data(rt, "recipe", Map::from_iter([("trays".to_owned(), trays)]))
}

/// The first selftest block: the tray built at `root`, its storeys when it got that far.
fn tray_checks(rt: &Rt, root: f64, fails: &mut Vec<String>) -> Result<[f64; 2]> {
    let built = py::method(&build_pump_tray(rt, root)?, "val", vec![])?;
    if !py::method(&built, "isValid", vec![])?.truthy()? {
        fails.push("the tray is not a valid solid".into());
    }
    let solids = py::method(&built, "Solids", vec![])?.len()?;
    if solids != 1 {
        fails.push(format!(
            "the tray comes out {} solids, not one — the plate carried out has parted from the case's own",
            num::fmti(solids as i64, "")
        ));
    }
    let zlen = py::method(&built, "BoundingBox", vec![])?.attr("zlen")?.num()?;
    if (zlen - depth(rt)?).abs() > 1e-6 {
        fails.push(format!(
            "a tray runs {} mm along the pump's axis against the {} it declares",
            num::fmt(zlen, ".4f"),
            num::fmt(depth(rt)?, "g")
        ));
    }
    let foul = fouled_volume(rt, root)?;
    if foul.f() > 1e-6 {
        fails.push(format!("the tray stands {} mm^3 inside the pump it holds", foul.fmt(".6f")));
    }
    let [on_head, on_crown] = storeys(rt, root)?;
    if on_head <= 0.0 {
        fails.push("the tray carries no material on the head's own crown".into());
    }
    if on_crown <= 0.0 {
        fails.push("the tray carries no material on the boss's crown — the cut took the shoulder with the cylinder".into());
    }
    Ok([on_head, on_crown])
}

/// The second selftest block: the fitted drop well against the reference head's flank ramps.
fn flank_checks(rt: &Rt, fails: &mut Vec<String>) -> Result<()> {
    let st = state(rt)?;
    let head = py::method(&in_pump_frame(rt, &py::call(&st.kp.attr("build_head")?, vec![])?)?, "val", vec![])?;
    let fitted_air = 0.4;
    let well = py::method(&drop_well(rt, fitted_air, None)?, "val", vec![])?;
    if !py::method(&well, "isValid", vec![])?.truthy()? || py::method(&well, "Solids", vec![])?.len()? != 1 {
        fails.push("the fitted drop well is not one valid solid".into());
    }
    let mut ramps = vec![];
    for face in py::method(&head, "Faces", vec![])?.iter()? {
        if py::method(&face, "normalAt", vec![])?.attr("x")?.num()?.abs() > 0.6
            && py::method(&face, "normalAt", vec![])?.attr("z")?.num()?.abs() > 0.6
        {
            ramps.push(face);
        }
    }
    if ramps.is_empty() {
        fails.push("the pump reference has no lower flank ramps to verify".into());
    }
    for face in &ramps {
        let mut mates = vec![];
        for mate in py::method(&well, "Faces", vec![])?.iter()? {
            let normal = py::method(&mate, "normalAt", vec![])?;
            if py::method(&normal, "dot", vec![py::method(face, "normalAt", vec![])?])?.num()? > 1.0 - 1e-6 {
                mates.push(mate);
            }
        }
        let mut gaps = vec![];
        for mate in &mates {
            gaps.push(py::method(face, "distance", vec![mate.clone()])?.num()?);
        }
        let gap = num::min_of(gaps).unwrap_or(f64::INFINITY);
        let expected_gap = fitted_air / num::pow(2.0, 0.5);
        if (gap - expected_gap).abs() > 1e-6 {
            fails.push(format!(
                "the lower pump flank has {} mm normal air, expected the fitted profile's {}",
                num::fmt(gap, ".6f"),
                num::fmt(expected_gap, ".6f")
            ));
        }
    }
    Ok(())
}

/// The tray against the pump it takes and the case it is cut out of.
pub fn selftest(rt: &Rt) -> Result<i64> {
    let st = state(rt)?;
    let s = &st.stock;
    let mut fails: Vec<String> = vec![];
    // The collar footprint must cover the molded flange so the enclosure can restore a
    // complete pressing annulus on its upper face.
    if half_width(rt)? < s.bracket_half {
        fails.push(format!(
            "the collar runs {} mm off the axis and the bracket reaches {} — the pressing annulus cannot cover it",
            num::fmt(half_width(rt)?, ".3f"),
            num::fmt(s.bracket_half, ".3f")
        ));
    }
    if s.can_half >= s.boss_half {
        fails.push(format!(
            "the can's bore reaches {} mm and the boss's octagon {} — the shoulder lands on nothing",
            num::fmt(s.can_half, "g"),
            num::fmt(s.boss_half, "g")
        ));
    }
    // A tray rooted 3 mm past the head's own edge.
    let root = s.head_half + 3.0;
    let storeys = match tray_checks(rt, root, &mut fails) {
        Ok(storeys) => Some(storeys),
        Err(error) => {
            fails.push(error.to_string());
            None
        }
    };
    if let Err(error) = flank_checks(rt, &mut fails) {
        fails.push(format!("lower pump flank clearance: {error}"));
    }
    for line in &fails {
        rt.print(format!("FAIL {line}"))?;
    }
    if fails.is_empty() {
        let [on_head, on_crown] = storeys.context("the tray's storeys")?;
        rt.print(format!(
            "ok  pump-tray  {} across, {} of shoulder over {} of bore, octagon {} at the flats, can bore {}, clear of a {} bracket, {} mm² on the head and {} on the crown",
            num::fmt(2. * half_width(rt)?, "g"),
            num::fmt(s.SHOULDER, "g"),
            num::fmt(s.boss_depth, "g"),
            num::fmt(2. * s.boss_half, "g"),
            num::fmt(2. * s.can_half, "g"),
            num::fmt(2. * s.bracket_half, "g"),
            num::fmt(on_head, ".0f"),
            num::fmt(on_crown, ".0f")
        ))?;
    }
    Ok(if fails.is_empty() { 0 } else { 1 })
}

fn main(rt: &Rt) -> Result<()> {
    let st = state(rt)?;
    let rust_part = rt.import("_rust_part")?;
    let facts = rt.import("_facts")?;
    let trays = py::plain(&trays_of_machine(&py::call(&facts.attr("read")?, vec![])?)?)?;
    let recipe = py::from_json(numbers(rt, trays.clone())?)?;
    let measured = py::call(
        &rust_part.attr("check")?,
        vec![py::s("enclosure-components"), py::s("pump-tray"), recipe],
    )?;
    let values = Map::from_iter([("trays".to_owned(), trays), ("measured".to_owned(), py::plain(&measured)?)]);
    let report = data(rt, "report", values)?;
    let lines = report["lines"].as_array().context("report lines")?;
    let lines = lines.iter().map(|line| line.as_str().map(str::to_owned).context("a report line")).collect::<Result<Vec<_>>>()?;
    rt.print(lines.join("\n"))?;
    let mut variables = BTreeMap::new();
    for (key, value) in report["variables"].as_object().context("report variables")? {
        variables.insert(key.clone(), py::from_json(value.clone())?.str()?);
    }
    rt.substitute(hsm_documents::Kind::Markdown, &parent(&st.here).join("README.md"), &variables, Some(MODULE))?;
    rt.print("-> README.md".into())
}
