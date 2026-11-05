//! `endcap_circular_step`: the complete machined carbonator end cap as a solid for CNC
//! machining quotes, in millimetres, from the inch source specs and the DXF module's blind
//! rod-register datum.

use super::*;

pub const NAME: &str = "endcap_circular_step";

/// mm per inch: the cap's source specs are in inches.
pub const INCH: f64 = 25.4;
pub const DISC_DIAMETER: f64 = 4.860 * INCH;
pub const DISC_RADIUS: f64 = DISC_DIAMETER / 2.0;
pub const DISC_THICKNESS: f64 = 0.250 * INCH;
pub const HOLE_DIAMETER: f64 = 0.438 * INCH;
pub const HOLE_RADIUS: f64 = HOLE_DIAMETER / 2.0;
pub const HOLE_OFFSET: f64 = 0.750 * INCH;
pub const HOLE_POSITIONS: [[f64; 2]; 2] = [[-HOLE_OFFSET, 0.0], [HOLE_OFFSET, 0.0]];
pub const REGISTER_DRILL_DIAMETER: f64 = 0.140625 * INCH;
pub const REGISTER_DEPTH: f64 = 0.100 * INCH;
pub const OUT_NAME: &str = "endcap-circular-2hole";

pub struct State {
    pub here: PathBuf,
    /// `endcap_circular_dxf.register_radius`, in inches.
    pub register_radius_in: f64,
    /// `endcap_circular_dxf.register_position`, in inches.
    pub register_position_in: [f64; 2],
    pub register_radius: f64,
    pub register_position: [f64; 2],
    pub out_dir: PathBuf,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let here = resolve(&rt.file(NAME));
        rt.sys_path_insert(0, &ancestor(&here, "hardware")?.join("scripts"))?;
        let docgen = ancestor_where(&here, |p| p.join("tools").join("docgen").is_dir())?;
        rt.sys_path_insert(0, &docgen.join("tools"))?;
        // `from docgen import substitute_py_comments`: the runtime's own substitution.
        let dxf = endcap_circular_dxf::state(rt)?;
        let (register_radius_in, register_position_in) = (dxf.register_radius, dxf.register_position);
        let register_radius = register_radius_in * INCH;
        let register_position = register_position_in.map(|v| v * INCH);
        let out_dir = parent_n(&resolve(&rt.file(NAME)), 0);
        Ok(Self {
            here,
            register_radius_in,
            register_position_in,
            register_radius,
            register_position,
            out_dir,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `build_endcap()`: the disc, its two through tap-drill holes and the blind rod register
/// entered from the +Z (inside) face.
pub fn build_endcap(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let cq = rt.py("cadquery")?;
    let disc = cq
        .a("Workplane")?
        .c(args!["XY"])?
        .m("circle", args![DISC_RADIUS])?
        .m("extrude", args![DISC_THICKNESS])?;
    // The tool over-runs both faces.
    let npt_holes = cq
        .a("Workplane")?
        .c(args!["XY"])?
        .mk("workplane", vec![], kw!["offset" => -0.5])?
        .m("pushPoints", args![HOLE_POSITIONS.to_vec()])?
        .m("circle", args![HOLE_RADIUS])?
        .m("extrude", args![DISC_THICKNESS + 1.0])?;
    // The register tool over-runs the +Z face only; the -Z pressure boundary stays whole.
    let register = cq
        .a("Workplane")?
        .c(args!["XY"])?
        .mk("workplane", vec![], kw!["offset" => DISC_THICKNESS + 0.5])?
        .m("moveTo", args![s.register_position[0], s.register_position[1]])?
        .m("circle", args![REGISTER_DRILL_DIAMETER / 2.0])?
        .m("extrude", args![-(REGISTER_DEPTH + 0.5)])?;
    disc.m("cut", vec![npt_holes])?.m("cut", vec![register])
}

/// `numbers()`: the machined cap dimensions and appearance read by `endcap_circular_step.rs`.
pub fn numbers(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let m_stainless = rt.pya("_material_base", "M_STAINLESS")?;
    let linear = rt.pya("_materials", "linear")?;
    let mut bores: Vec<Val> = HOLE_POSITIONS
        .iter()
        .map(|p| dict!["center" => p.to_vec(), "radius" => HOLE_RADIUS, "floor" => 0.0])
        .collect();
    bores.push(dict![
        "center" => s.register_position.to_vec(),
        "radius" => REGISTER_DRILL_DIAMETER / 2.0,
        "floor" => DISC_THICKNESS - REGISTER_DEPTH,
    ]);
    let color = Val::list(linear.c(vec![m_stainless])?.list()?);
    Ok(dict![
        "name" => OUT_NAME,
        "radius" => DISC_RADIUS,
        "height" => DISC_THICKNESS,
        "bores" => bores,
        "color" => color,
    ])
}

/// `main()`: the cut through the Rust part builder, its summary and the doc comments.
pub fn run(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    let numbers = numbers(rt)?;
    rt.pya("_rust_part", "cut")?.c(args![
        "cold-core",
        "endcap-circular-step",
        numbers,
        Val::Path(s.out_dir.clone())
    ])?;
    let path = s.out_dir.join(format!("{OUT_NAME}.step"));
    rt.print(format!("Exported: {}", ps(&path)))?;
    rt.print(format!(
        "  Disc:      Ø{} × {} mm, 316 SS",
        ff(DISC_DIAMETER, ".3f"),
        ff(DISC_THICKNESS, ".3f")
    ))?;
    rt.print(format!(
        "  NPT holes: 2× Ø{} mm THRU at X = ±{} mm",
        ff(HOLE_DIAMETER, ".3f"),
        ff(HOLE_OFFSET, ".3f")
    ))?;
    rt.print(format!(
        "  Register:  Ø{} × {} mm blind at {}, +Z (inside) face",
        ff(REGISTER_DRILL_DIAMETER, ".4g"),
        ff(REGISTER_DEPTH, ".3g"),
        s.register_position.to_val().str()?
    ))?;
    let g = |x: f64| ff(x, ".4g");
    let variables: Vec<(String, String)> = [
        ("DISC_D_MM", format!("{} mm", g(DISC_DIAMETER))),
        ("DISC_D_IN", format!("{} in", g(DISC_DIAMETER / INCH))),
        ("DISC_R_MM", format!("{} mm", g(DISC_RADIUS))),
        ("DISC_THK_MM", format!("{} mm", g(DISC_THICKNESS))),
        ("HOLE_D_MM", format!("{} mm", g(HOLE_DIAMETER))),
        ("HOLE_R_MM", format!("{} mm", g(HOLE_RADIUS))),
        ("HOLE_OFFSET_MM", format!("{} mm", g(HOLE_OFFSET))),
        ("REG_X", format!("{} mm", g(s.register_radius))),
        ("REG_D", format!("{} mm", g(REGISTER_DRILL_DIAMETER))),
        ("REG_DEPTH", format!("{} mm", g(REGISTER_DEPTH))),
        (
            "REG_PLATE_REMAINING",
            format!("{} mm", g(DISC_THICKNESS - REGISTER_DEPTH)),
        ),
    ]
    .into_iter()
    .map(|(k, v)| (k.to_owned(), v))
    .collect();
    rt.substitute_py_comments(&rt.file(NAME), &variables, Some(NAME))
}

/// The `__main__` block: the Rust part builder starts, then `main()`.
pub fn main(rt: &Runtime) -> Result<()> {
    rt.py("_rust_part")?.m("start", vec![])?;
    run(rt)
}

/// The native `substitute_py_comments(path, variables)` this module imported from docgen.
fn substitute_py_comments(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let path = PathBuf::from(c.req::<Val>(0, "path")?.str()?);
    let variables: Val = c.req(1, "variables")?;
    let mut values = vec![];
    for key in variables.iter()? {
        values.push((key.str()?, variables.get(key)?.str()?));
    }
    rt.substitute_py_comments(&path, &values, Some(NAME))?;
    Ok(Val::None)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", Val::Path(s.here.clone()));
    ns.func(rt, "substitute_py_comments", substitute_py_comments);
    ns.value("_register_radius_in", s.register_radius_in);
    ns.value("_register_position_in", s.register_position_in);
    ns.value("inch", INCH);
    ns.value("disc_diameter", DISC_DIAMETER);
    ns.value("disc_radius", DISC_RADIUS);
    ns.value("disc_thickness", DISC_THICKNESS);
    ns.value("hole_diameter", HOLE_DIAMETER);
    ns.value("hole_radius", HOLE_RADIUS);
    ns.value("hole_offset", HOLE_OFFSET);
    ns.value("hole_positions", HOLE_POSITIONS.to_vec());
    ns.value("register_radius", s.register_radius);
    ns.value("register_position", s.register_position);
    ns.value("register_drill_diameter", REGISTER_DRILL_DIAMETER);
    ns.value("register_depth", REGISTER_DEPTH);
    ns.value("out_dir", Val::Path(s.out_dir.clone()));
    ns.value("out_name", OUT_NAME);
    ns.func(rt, "build_endcap", |rt, _| build_endcap(rt));
    ns.func(rt, "numbers", |rt, _| numbers(rt));
    ns.func(rt, "main", |rt, _| {
        run(rt)?;
        Ok(Val::None)
    });
    Ok(())
}
