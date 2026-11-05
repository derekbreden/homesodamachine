//! `_water_pressure_regulator`: the internal water regulator and its single tied cradle, in
//! the top lid's frame.

use std::cell::RefCell;

use super::cad::{self, Cq};
use super::*;

pub const NAME: &str = "_water_pressure_regulator";

pub const INLET_XY: [f64; 2] = [-5.2, -49.3];
pub const INLET_OVER_FACE: f64 = 48.6;
pub const BEARING_S: f64 = 96.0;
pub const SEAT_R: f64 = 9.45;
pub const HALF_WIDTH: f64 = SEAT_R + 3.25;
pub const LENGTH: f64 = 8.8;
pub const TIE_WIDTH: f64 = 2.8;
pub const TIE_HEIGHT: f64 = 3.25;
pub const UNDER_BORE: f64 = 4.5;

/// `cq.Vector(-0.985, -0.08, -0.152).normalized().toTuple()`.
pub fn axis() -> [f64; 3] {
    let v = [-0.985f64, -0.08, -0.152];
    let d = (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]).sqrt();
    [v[0] / d, v[1] / d, v[2] / d]
}

/// `@lru_cache(maxsize=8)` on `cradle`.
const CRADLES: usize = 8;

pub struct State {
    pub lru_cache: Val,
    pub sys: Val,
    pub cq: Cq,
    pub hw: PathBuf,
    pub regulator: Val,
    /// `cradle(face_z)` by argument, least recently used first.
    cradles: RefCell<Vec<(f64, Val)>>,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let lru_cache = rt.pya("functools", "lru_cache")?;
        let sys = rt.py("sys")?;
        let cq = Cq::new(rt)?;
        let hw = ancestor(&resolve(&rt.file(NAME)), "hardware")?;
        rt.sys_path_insert(0, &hw.join("reference/shok-blok-regulator"))?;
        let regulator = rt.py("shok_blok_regulator")?;
        Ok(Self {
            lru_cache,
            sys,
            cq,
            hw,
            regulator,
            cradles: RefCell::new(vec![]),
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `inlet(face_z)`: the regulator's inlet over the lid face.
pub fn inlet(face_z: f64) -> [f64; 3] {
    [INLET_XY[0], INLET_XY[1], face_z + INLET_OVER_FACE]
}

/// `bearing(face_z)`: the cradle's station along the regulator's axis.
pub fn bearing(face_z: f64) -> [f64; 3] {
    let start = inlet(face_z);
    let reach = scale3(axis(), BEARING_S);
    add3(start, reach)
}

/// `cradle(face_z)`: the tied post that carries the regulator body.
pub fn cradle(rt: &Runtime, face_z: f64) -> Result<Val> {
    let s = state(rt)?;
    {
        let mut held = s.cradles.borrow_mut();
        if let Some(at) = held.iter().position(|(z, _)| *z == face_z) {
            let row = held.remove(at);
            let solid = row.1.clone();
            held.push(row);
            return Ok(solid);
        }
    }
    let cq = &s.cq;
    let mid = bearing(face_z);
    let along = axis();
    let slope = along[2] / along[0];
    let (x0, x1) = (mid[0] - LENGTH / 2.0, mid[0] + LENGTH / 2.0);
    let y0 = mid[1] - HALF_WIDTH;
    let corners = [
        [x0, y0, face_z],
        [x1, y0, face_z],
        [x1, y0, mid[2] + slope * (x1 - mid[0])],
        [x0, y0, mid[2] + slope * (x0 - mid[0])],
        [x0, y0, face_z],
    ];
    let vectors = corners
        .iter()
        .map(|p| cq.vector(*p))
        .collect::<Result<Vec<_>>>()?;
    let wire = cq.class("Wire", "makePolygon", vec![Val::list(vectors)], vec![])?;
    let extent = cq.m.a("Vector")?.c(args![0i64, 2.0 * HALF_WIDTH, 0i64])?;
    let post = cq.solid("extrudeLinear", vec![wire, Val::list(vec![]), extent])?;
    let base = sub3(mid, scale3(along, 15.0));
    let bore = cq.solid(
        "makeCylinder",
        args![SEAT_R, 30i64, cq.vector(base)?, cq.vector(along)?],
    )?;
    let roof = mid[2] - SEAT_R - UNDER_BORE;
    let passage = cq.solid(
        "makeBox",
        args![
            TIE_WIDTH,
            2.0 * HALF_WIDTH + 2.0,
            TIE_HEIGHT,
            cq.vector([mid[0] - TIE_WIDTH / 2.0, y0 - 1.0, roof - TIE_HEIGHT])?
        ],
    )?;
    let solid = cad::clean(&cad::cut(&cad::cut(&post, vec![bore])?, vec![passage])?)?;
    let mut held = s.cradles.borrow_mut();
    held.push((face_z, solid.clone()));
    if held.len() > CRADLES {
        held.remove(0);
    }
    Ok(solid)
}

/// `proud()`: how far the cradle stands over the lid face.
pub fn proud(rt: &Runtime) -> Result<f64> {
    cradle(rt, 0.0)?.m("BoundingBox", vec![])?.a("zmax")?.f()
}

/// `tie_loop()`: the cable tie's length around the post and the regulator body.
pub fn tie_loop() -> f64 {
    let axis = axis();
    let horizontal = axis[0].abs() / hypot(&[axis[0], axis[1]]);
    let w = HALF_WIDTH / horizontal;
    let h = (SEAT_R + UNDER_BORE) / (1.0 - axis[2].powf(2.0)).sqrt();
    let r = SEAT_R;
    2.0 * w + 2.0 * h + 2.0 * (w * w - r * r).sqrt() + r * (std::f64::consts::PI - 2.0 * (r / w).acos())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("lru_cache", s.lru_cache.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.module(rt, "math", "math")?;
    ns.value("sys", s.sys.clone());
    ns.value("cq", s.cq.m.clone());
    ns.value("HW", Val::Path(s.hw.clone()));
    ns.value("regulator", s.regulator.clone());
    ns.value("INLET_XY", INLET_XY);
    ns.value("INLET_OVER_FACE", INLET_OVER_FACE);
    ns.value("AXIS", axis());
    ns.value("BEARING_S", BEARING_S);
    ns.value("SEAT_R", SEAT_R);
    ns.value("HALF_WIDTH", HALF_WIDTH);
    ns.value("LENGTH", LENGTH);
    ns.value("TIE_WIDTH", TIE_WIDTH);
    ns.value("TIE_HEIGHT", TIE_HEIGHT);
    ns.value("UNDER_BORE", UNDER_BORE);
    ns.func(rt, "inlet", |rt, c| {
        Cq::new(rt)?.vector(inlet(c.req(0, "face_z")?))
    });
    ns.func(rt, "bearing", |rt, c| {
        Cq::new(rt)?.vector(bearing(c.req(0, "face_z")?))
    });
    ns.func(rt, "cradle", |rt, c| cradle(rt, c.req(0, "face_z")?));
    ns.func(rt, "proud", |rt, _| Ok(Val::Float(proud(rt)?)));
    ns.func(rt, "tie_loop", |_, _| Ok(Val::Float(tie_loop())));
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
