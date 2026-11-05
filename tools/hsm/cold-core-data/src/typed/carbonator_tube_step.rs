//! `carbonator_tube_step`: the carbonator tube, the 3D solid of the cut stock, for the welding
//! fixture and for quotes. Its figures are `_carbonator_stock`'s.

use super::*;

pub const NAME: &str = "carbonator_tube_step";

pub const OUT_NAME: &str = "carbonator-tube";

pub struct State {
    pub sys: Val,
    pub here: PathBuf,
    pub hw: PathBuf,
    /// `_p`, the last directory the module put on `sys.path`.
    pub p: PathBuf,
    pub carb: Val,
    pub tube_od: Val,
    pub tube_id: Val,
    pub tube_wall: Val,
    pub tube_length: Val,
    pub out_dir: PathBuf,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let sys = rt.py("sys")?;
        let here = resolve(&rt.file(NAME));
        let hw = ancestor(&here, "hardware")?;
        let mut p = PathBuf::new();
        for directory in [hw.join("scripts"), hw.join("cold-core-layout")] {
            if !sys.a("path")?.contains(&Val::Str(ps(&directory)))? {
                rt.sys_path_insert(0, &directory)?;
            }
            p = directory;
        }
        let carb = rt.py("_carbonator_stock")?;
        let tube_od = carb.a("TUBE_OD")?;
        let tube_id = carb.a("TUBE_ID")?;
        let tube_wall = carb.a("TUBE_WALL")?;
        let tube_length = carb.a("carbonator_height")?;
        let out_dir = here.parent().map(PathBuf::from).unwrap_or_default();
        Ok(Self {
            sys,
            here,
            hw,
            p,
            carb,
            tube_od,
            tube_id,
            tube_wall,
            tube_length,
            out_dir,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `build_tube()`: the barrel, bored through, as a CadQuery workplane.
pub fn build_tube(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let cq = rt.py("cadquery")?;
    let outer = cq
        .a("Workplane")?
        .c(args!["XY"])?
        .m("circle", args![s.tube_od.f()? / 2.0])?
        .m("extrude", vec![s.tube_length.clone()])?;
    let bore = cq
        .a("Workplane")?
        .c(args!["XY"])?
        .mk("workplane", vec![], kw!["offset" => -0.5])?
        .m("circle", args![s.tube_id.f()? / 2.0])?
        .m("extrude", args![s.tube_length.f()? + 1.0])?;
    outer.m("cut", vec![bore])
}

/// `numbers()`: the figures the Rust part cuts the tube from.
pub fn numbers(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let stainless = rt.pya("_material_base", "M_STAINLESS")?;
    let linear = rt.pya("_materials", "linear")?;
    Ok(dict![
        "name" => OUT_NAME,
        "radius" => s.tube_od.f()? / 2.0,
        "height" => s.tube_length.clone(),
        "bores" => vec![dict![
            "center" => vec![0.0, 0.0],
            "radius" => s.tube_id.f()? / 2.0,
            "floor" => 0.0,
        ]],
        "color" => Val::list(linear.c(vec![stainless])?.list()?),
    ])
}

/// The module's `main()`: the tube's STEP beside this file, and its figures on the terminal.
pub fn export(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    let rust_part = rt.py("_rust_part")?;
    rust_part.m(
        "cut",
        args!["cold-core", "carbonator-tube", numbers(rt)?, s.out_dir.clone()],
    )?;
    let path = s.out_dir.join(format!("{OUT_NAME}.step"));
    rt.print(format!("Exported: {}", ps(&path)))?;
    rt.print(format!(
        "  Tube:   Ø{} OD × {} wall × {} long, 316 SS",
        fv(&s.tube_od, ".3f")?,
        fv(&s.tube_wall, ".3f")?,
        fv(&s.tube_length, ".1f")?
    ))?;
    rt.print(format!("  Bore:   Ø{}", fv(&s.tube_id, ".3f")?))
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("sys", s.sys.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", Val::Path(s.here.clone()));
    ns.value("_hw", Val::Path(s.hw.clone()));
    ns.value("_p", Val::Path(s.p.clone()));
    ns.value("_carb", s.carb.clone());
    ns.value("tube_od", s.tube_od.clone());
    ns.value("tube_id", s.tube_id.clone());
    ns.value("tube_wall", s.tube_wall.clone());
    ns.value("tube_length", s.tube_length.clone());
    ns.value("out_dir", Val::Path(s.out_dir.clone()));
    ns.value("out_name", OUT_NAME);
    ns.func(rt, "build_tube", |rt, _| build_tube(rt));
    ns.func(rt, "numbers", |rt, _| numbers(rt));
    ns.func(rt, "main", |rt, _| {
        export(rt)?;
        Ok(Val::None)
    });
    Ok(())
}

pub fn main(rt: &Runtime) -> Result<()> {
    rt.pya("_rust_part", "start")?.c(vec![])?;
    export(rt)
}
