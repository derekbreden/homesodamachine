//! Guide recipe `startup`: the cylinder handwheel and the factory-set regulator with both gauges
//! pressurised.

use super::scenes;
use super::*;
use std::path::PathBuf;
use std::rc::Rc;

pub const NAME: &str = "startup";

pub const CAM: [Num; 3] = [Num::F(0.08), Num::I(1), Num::F(0.12)];
pub const TARGET: [Num; 3] = [Num::I(-35), Num::I(0), Num::F(-4.5)];
pub const SPAN: f64 = 103.5;
pub const SIZE: (i64, i64) = (1800, 1200);
pub const CYLINDER_PSI: i64 = 800;

pub struct State {
    pub cq: Val,
    /// The `scenes` namespace.
    pub scenes: Val,
    pub out: PathBuf,
    pub art: PathBuf,
    pub reg: Val,
    /// `reg.FACTORY_SET_PSI`.
    pub outlet_psi: Val,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let cq = rt.py("cadquery")?;
        let namespace = rt.import_module(scenes::NAME)?;
        let shared = scenes::state(rt)?;
        let out = shared.hardware.join("install-guide/out/startup");
        let art = shared.hardware.join("install-guide/art");
        let reg = shared.reg.clone();
        let outlet_psi = reg.a("FACTORY_SET_PSI")?;
        Ok(State {
            cq,
            scenes: namespace,
            out,
            art,
            reg,
            outlet_psi,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

fn num(reg: &Val, name: &str) -> Result<Num> {
    Num::from_val(&reg.a(name)?)
}

/// `dial_print(child, centre, pressure, full)`: the dial's scale and a needle at the illustrated
/// pressure.
pub fn dial_print(rt: &Runtime, child: &Val, centre: &Val, pressure: &Val, full: &Val) -> Result<Val> {
    let st = state(rt)?;
    let reg = &st.reg;
    let face_y = num(reg, "GAUGE_FACE_Y")?.add(num(reg, "PRINT_T")?);
    let below = face_y.f() - 1e-5;
    let mut marks = vec![];
    for solid in child.a("obj")?.m("Solids", vec![])?.iter()? {
        if solid.m("BoundingBox", vec![])?.a("ymin")?.f()? < below {
            marks.push(solid);
        }
    }
    let plane = st
        .cq
        .a("Workplane")?
        .c(vec![reg.a("_dial_plane")?])?
        .mk("workplane", vec![], kw!["offset" => face_y])?
        .m(
            "center",
            vec![Num::from_val(&centre.i(0)?)?.neg().to_val(), centre.i(2)?],
        )?;
    let angle = reg.m("_scale_deg", vec![pressure.clone(), full.clone()])?;
    marks.push(reg.m("_needle", vec![angle, plane])?);
    st.cq
        .a("Compound")?
        .a("makeCompound")?
        .c(vec![Val::list(marks)])
}

/// `assembly()`: the fitted regulator and top of the customer's cylinder.
pub fn assembly(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    let result = st
        .cq
        .a("Assembly")?
        .ck(vec![], kw!["name" => "startup-gas"])?;
    for child in scenes::cylinder(rt, Num::I(0))?.a("children")?.iter()? {
        let name = child.a("name")?;
        let dial = match &name {
            Val::Str(s) if s == "outlet-black-print" => Some((
                "outlet_dial",
                st.outlet_psi.clone(),
                "OUTLET_FULL_PSI",
            )),
            Val::Str(s) if s == "tank-black-print" => {
                Some(("tank_dial", Val::Int(CYLINDER_PSI), "TANK_FULL_PSI"))
            }
            _ => None,
        };
        match dial {
            Some((station, pressure, full)) => {
                let centre = st.reg.m(station, vec![])?.i(0)?;
                let obj = dial_print(rt, &child, &centre, &pressure, &st.reg.a(full)?)?;
                result.mk(
                    "add",
                    vec![obj],
                    kw!["name" => child.a("name")?, "color" => child.a("color")?],
                )?;
            }
            None => {
                result.m("add", vec![child])?;
            }
        }
    }
    Ok(result)
}

/// `points()`: the gauges, the needle's tip, the factory screw and the handwheel.
pub fn points(rt: &Runtime) -> Result<Val> {
    let st = state(rt)?;
    let reg = &st.reg;
    let scale = reg.m(
        "_scale_deg",
        vec![st.outlet_psi.clone(), reg.a("OUTLET_FULL_PSI")?],
    )?;
    let angle = radians(scale.f()?);
    let upper = reg.m("outlet_dial", vec![])?.i(0)?;
    let tip = (
        num(reg, "NEEDLE_R")?.neg().f() * angle.cos(),
        num(reg, "GAUGE_FACE_Y")?.add(num(reg, "PRINT_T")?).f() + 0.8,
        num(reg, "OUTLET_REACH")?.f() + num(reg, "NEEDLE_R")?.f() * angle.sin(),
    );
    Ok(dict![
        "upper-gauge" => upper,
        "upper-needle-tip" => tip,
        "cylinder-gauge" => reg.m("tank_dial", vec![])?.i(0)?,
        "factory-screw" => reg.m("adjustment", vec![])?.i(0)?,
        "cylinder-handwheel" => (-115, 0, 33),
    ])
}

/// `main()`: stage and render the pressurised regulator, and record its pose and points.
pub fn main(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    scenes::mkdir(&st.out, true, true)?;
    scenes::mkdir(&st.art, false, true)?;
    st.scenes.setattr("OUT", Val::Path(st.out.clone()))?;
    st.scenes.setattr("ART", Val::Path(st.art.clone()))?;
    st.scenes.setattr("jobs", Val::list(vec![]))?;
    let gas = assembly(rt)?;
    scenes::stage(
        rt,
        "startup-gas",
        &gas,
        CAM.to_val(),
        TARGET.to_val(),
        Val::Float(SPAN),
        Val::Str(format!("{}x{}", SIZE.0, SIZE.1)),
        false,
    )?;
    scenes::render(rt)?;
    let metadata = dict![
        "cam" => CAM,
        "target" => TARGET,
        "span" => SPAN,
        "size" => SIZE,
        "outlet_psi" => st.outlet_psi.clone(),
        "cylinder_psi" => CYLINDER_PSI,
        "points" => points(rt)?,
    ];
    write_text(
        &st.out.join("points.json"),
        &(json_dumps(&metadata, kw!["indent" => 2])? + "\n"),
    )?;
    rt.print(json_dumps(&metadata, kw!["indent" => 2])?)?;
    Ok(())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.module(rt, "json", "json")?;
    ns.module(rt, "math", "math")?;
    ns.value("cq", st.cq.clone());
    ns.value("scenes", st.scenes.clone());
    ns.value("OUT", st.out.clone());
    ns.value("ART", st.art.clone());
    ns.value("CAM", CAM);
    ns.value("TARGET", TARGET);
    ns.value("SPAN", SPAN);
    ns.value("SIZE", SIZE);
    ns.value("reg", st.reg.clone());
    ns.value("OUTLET_PSI", st.outlet_psi.clone());
    ns.value("CYLINDER_PSI", CYLINDER_PSI);
    ns.func(rt, "dial_print", |rt, c| {
        let child: Val = c.req(0, "child")?;
        let centre: Val = c.req(1, "centre")?;
        let pressure: Val = c.req(2, "pressure")?;
        let full: Val = c.req(3, "full")?;
        dial_print(rt, &child, &centre, &pressure, &full)
    });
    ns.func(rt, "assembly", |rt, _| assembly(rt));
    ns.func(rt, "points", |rt, _| points(rt));
    ns.func(rt, "main", |rt, _| {
        main(rt)?;
        Ok(Val::None)
    });
    Ok(())
}
