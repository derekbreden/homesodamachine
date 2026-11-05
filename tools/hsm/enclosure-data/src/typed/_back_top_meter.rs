//! Plain roof piers for the meter's two fixed collars.
//!
//! Each pier has an open west-facing bearing and a straight strap passage.
//! Three millimetres of stock back the seats and passages. One broad fore
//! column carries both the meter and ASSE; their strap openings remain open.
//!
//! The piers stand on the `digiten-flow` pose `above_core` (`layout`) gives, and the meter's
//! collar profile comes from `digiten_flow_sensor`; both are read when a function is called.
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result, ensure};
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_back_top_meter";

pub struct State {
    /// The `importlib` the module imported, which `meter_support_datums` loads the meter through.
    importlib: Val,
    /// `above_core`, imported as `layout`.
    layout: Val,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    let importlib = rt.import("importlib")?;
    ns.set("importlib", importlib.clone())?;
    ns.set("math", rt.import("math")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let sys = rt.import("sys")?;
    ns.set("sys", sys.clone())?;
    let file = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let here = file.parent().context("HERE")?.to_path_buf();
    ns.set("HERE", Val::Path(here.clone()))?;
    let hw = here.ancestors().nth(3).context("IndexError")?.to_path_buf();
    ns.set("HW", Val::Path(hw.clone()))?;
    // sys.path[:0] = [...]
    let paths = ["manifold-layout", "scripts", "reference/digiten-flow-sensor", "printed-parts/cadlib"]
        .map(|p| py::s(py::path_str(&hw.join(p))));
    sys.attr("path")?.set(Val::Slice { start: None, stop: Some(0), step: 1 }, Val::list(paths.to_vec()))?;
    let layout = rt.import("above_core")?;
    ns.set("layout", layout.clone())?;
    rt.keep(MODULE, State { importlib, layout });

    ns.def(rt, "meter_support_datums", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::tuple(meter_support_datums(rt)?.iter().map(Datum::val).collect()))
    })?;
    ns.def(rt, "meter_tie_routes", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        meter_tie_routes(rt)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// One pier's datums: a row of `meter_support_datums()`.
#[derive(Clone, Debug)]
pub struct Datum {
    /// -1 for the fore pier, 1 for the aft.
    pub side: i64,
    pub station: Num,
    pub centre: [Num; 3],
    pub radius: Num,
    pub wall: Num,
    pub low: [Num; 3],
    pub high: [Num; 3],
    /// `layout.pose('asse1022-assembly')['translation_mm'][2]`, on the fore pier.
    pub asse_z: Option<Val>,
}

fn v3(values: &[Num; 3]) -> Val {
    Num::vals(values)
}

impl Datum {
    /// The row as `meter_support_datums()` gives it.
    pub fn val(&self) -> Val {
        let f = Num::F;
        let [_, y, _] = self.centre;
        let (low, high, radius, wall) = (self.low, self.high, self.radius, self.wall);
        let fore = self.side == -1;
        let band = if fore {
            [self.station.sub(f(3.)), self.station.add(f(3.))]
        } else {
            [self.station.sub(f(1.5)), self.station.add(f(4.5))]
        };
        let asse_bore = match &self.asse_z {
            Some(asse_z) if fore => py::dict([
                ("centre_xz_mm", py::tuple([Val::Float(37.25), asse_z.clone()])),
                ("radius_mm", Val::Float(16.75)),
            ]),
            _ => Val::None,
        };
        let body_setback = if self.side == 1 {
            py::dict([("fore_face_y_mm", y.sub(f(1.5)).val()), ("top_z_mm", Val::Float(315.))])
        } else {
            Val::None
        };
        py::dict([
            ("parent", py::s("enclosure-back-top")),
            ("centre_world_mm", v3(&self.centre)),
            ("width_mm", high[1].sub(low[1]).val()),
            ("seat_radius_mm", radius.val()),
            ("wall_mm", wall.val()),
            ("native_bearing_band_mm", Num::vals(&band)),
            ("stock_min_world_mm", v3(&low)),
            ("stock_max_world_mm", v3(&high)),
            ("seat_bottom_world_z_mm", low[2].val()),
            ("roof_root_world_z_mm", Val::Float(346.)),
            ("tie_plane_world_y_mm", y.val()),
            ("tie_slot_min_world_mm", v3(&self.tie_slot_min())),
            ("tie_slot_max_world_mm", v3(&self.tie_slot_max())),
            ("tie_backing_x_mm", Val::Float(52.5)),
            ("asse_bore", asse_bore),
            ("body_setback", body_setback),
        ])
    }
    /// `(low[0]-.1, y-1.5, z+radius+wall)`.
    pub fn tie_slot_min(&self) -> [Num; 3] {
        let [_, y, z] = self.centre;
        [self.low[0].sub(Num::F(0.1)), y.sub(Num::F(1.5)), z.add(self.radius).add(self.wall)]
    }
    /// `(high[0]+.1, y+1.5, z+radius+2.*wall)`.
    pub fn tie_slot_max(&self) -> [Num; 3] {
        let [_, y, z] = self.centre;
        [self.high[0].add(Num::F(0.1)), y.add(Num::F(1.5)), z.add(self.radius).add(Num::F(2.).mul(self.wall))]
    }
}

/// The fore and aft piers' datums.
pub fn meter_support_datums(rt: &Rt) -> Result<Vec<Datum>> {
    let state = state(rt)?;
    let fits = rt.import("fits")?;
    let meter = py::method(&state.importlib, "import_module", vec![py::s("digiten_flow_sensor")])?;
    let profile = py::call(&meter.attr("mounting_profile")?, vec![Val::Int(1)])?;
    let row = py::unpack(&py::item(&profile, Val::Int(-1))?, 4)?;
    let [first, last, r0, r1] = [&row[0], &row[1], &row[2], &row[3]].map(Num::of);
    let (first, last, r0, r1) = (first?, last?, r0?, r1?);
    let radius = r0.max(r1).add(Num::of(&fits.attr("slip")?)?);
    let wall = Num::F(3.);
    let f = Num::F;
    let mut result = vec![];
    for side in [-1i64, 1] {
        let station = if side == -1 { first.add(last).neg().div(f(2.)) } else { f(21.5) };
        let pose = py::call(&state.layout.attr("pose")?, vec![py::s("digiten-flow")])?;
        let at = py::call(&state.layout.attr("point")?, vec![pose, py::tuple([station.val(), Val::Float(0.), Val::Float(0.)])])?;
        let xyz = py::unpack(&at, 3)?;
        let (x, y, z) = (Num::of(&xyz[0])?, Num::of(&xyz[1])?, Num::of(&xyz[2])?);
        let low = if side == -1 {
            [f(44.5), f(361.), z.sub(radius).sub(wall)]
        } else {
            [x.add(f(2.5)), y.sub(f(4.5)), z.sub(radius).sub(wall)]
        };
        let high = [f(63.), y.add(f(4.5)), f(355.)];
        let asse_z = if side == -1 {
            let pose = py::call(&state.layout.attr("pose")?, vec![py::s("asse1022-assembly")])?;
            Some(py::item(&py::item(&pose, py::s("translation_mm"))?, Val::Int(2))?)
        } else {
            None
        };
        result.push(Datum { side, station, centre: [x, y, z], radius, wall, low, high, asse_z });
    }
    Ok(result)
}

/// `math.acos(x)`, refusing a value outside its domain as the runtime does.
fn acos(x: f64) -> Result<f64> {
    let angle = x.acos();
    ensure!(angle.is_finite(), "math domain error");
    Ok(angle)
}

/// A straight run of strap: `{'kind': 'line', 'points_mm': [a, b], 'wide_axis': (0., 1., 0.)}`.
fn line(a: &[Num; 3], b: &[Num; 3]) -> Val {
    py::dict([
        ("kind", py::s("line")),
        ("points_mm", Val::list(vec![v3(a), v3(b)])),
        ("wide_axis", py::ftuple(&[0., 1., 0.])),
    ])
}

/// Nominal 2.5 by 0.8 mm straps through the piers' straight passages.
///
/// The straps surround each collar and its seat. The head is accessible on
/// the west face. Purchased head dimensions, threading and holding force
/// require the physical assembly.
pub fn meter_tie_routes(rt: &Rt) -> Result<Val> {
    let result = Val::dict(vec![]);
    let f = Num::F;
    for (number, data) in meter_support_datums(rt)?.iter().enumerate() {
        let [x, y, z] = data.centre;
        let (low, high) = (data.low, data.high);
        let radius = data.radius.add(f(0.6));
        let (a, b) = (data.tie_slot_min(), data.tie_slot_max());
        let upper_z = a[2].add(b[2]).div(f(2.));
        let lower_z = low[2].sub(f(0.6));
        let (upper_west, lower_west) = ([low[0].sub(f(0.6)), y, upper_z], [low[0].sub(f(0.6)), y, lower_z]);
        let (upper_east, lower_east) = ([high[0].add(f(0.6)), y, upper_z], [high[0].add(f(0.6)), y, lower_z]);
        let tangent = |point: &[Num; 3], sign: i64| -> Result<f64> {
            let (dx, dz) = (point[0].sub(x).f(), point[2].sub(z).f());
            let turn = sign as f64 * acos(radius.f() / num::hypot2(dx, dz))?;
            Ok(num::modulo(num::degrees(dz.atan2(dx) + turn), 360.))
        };
        let (lower_angle, upper_angle) = (tangent(&lower_west, -1)?, tangent(&upper_west, 1)?);
        let point = |angle: f64| -> [Num; 3] {
            let theta = num::radians(angle);
            [x.add(radius.mul(f(num::cos(theta)))), y, z.add(radius.mul(f(num::sin(theta))))]
        };
        let (lower, upper) = (point(lower_angle), point(upper_angle));
        let sweep = upper_angle - lower_angle;
        let segments = vec![
            line(&upper_west, &upper_east),
            line(&upper_east, &lower_east),
            line(&lower_east, &lower_west),
            line(&lower_west, &lower),
            py::dict([
                ("kind", py::s("arc")),
                ("points_mm", Val::list(vec![v3(&lower), v3(&point((lower_angle + upper_angle) / 2.)), v3(&upper)])),
                ("radius_mm", radius.val()),
                ("sweep_degrees", Val::Float(sweep)),
                ("wide_axis", py::ftuple(&[0., 1., 0.])),
            ]),
            line(&upper, &upper_west),
        ];
        let fs = |p: &[Num; 3]| p.map(Num::f);
        let lengths = [
            num::dist(&fs(&upper_west), &fs(&upper_east)),
            num::dist(&fs(&upper_east), &fs(&lower_east)),
            num::dist(&fs(&lower_east), &fs(&lower_west)),
            num::dist(&fs(&lower_west), &fs(&lower)),
            radius.mul(f(num::radians(sweep).abs())).f(),
            num::dist(&fs(&upper), &fs(&upper_west)),
        ];
        let length = num::sum(lengths);
        let key = format!("meter-{}", if number == 0 { "fore" } else { "aft" });
        result.set(py::s(key), py::dict([
            ("parent", py::s("enclosure-back-top")),
            ("segments", Val::list(segments)),
            ("length_mm", Val::Float(length)),
            ("stock", py::s("6-inch narrow nylon tie")),
            ("stock_length_mm", Val::Float(152.4)),
            ("width_mm", Val::Float(2.5)),
            ("thickness_mm", Val::Float(0.8)),
            ("collar_plane_world_y_mm", y.val()),
            ("strip_basis", py::s("Nominal layout section; purchased strap/head dimensions unmeasured")),
        ]))?;
    }
    Ok(result)
}
