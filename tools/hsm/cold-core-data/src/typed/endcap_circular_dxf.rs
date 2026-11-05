//! `endcap_circular_dxf`: the circular carbonator end-cap disc's laser cut file, in inches,
//! and the blind rod-register datum, which the cut file leaves out.

use super::*;

pub const NAME: &str = "endcap_circular_dxf";

pub const DISC_DIAMETER: f64 = 4.860;
pub const DISC_RADIUS: f64 = DISC_DIAMETER / 2.0;
pub const DISC_THICKNESS: f64 = 0.250;
pub const HOLE_DIAMETER: f64 = 0.438;
pub const HOLE_RADIUS: f64 = HOLE_DIAMETER / 2.0;
pub const HOLE_SPACING: f64 = 1.500;
pub const HOLE_POSITIONS: [[f64; 2]; 2] = [[-HOLE_SPACING / 2.0, 0.0], [HOLE_SPACING / 2.0, 0.0]];
pub const TUBE_ID: f64 = 4.870;
pub const TUBE_ID_RADIUS: f64 = TUBE_ID / 2.0;
pub const REGISTER_DRILL_DIAMETER: f64 = 0.140625;
pub const REGISTER_DEPTH: f64 = 0.100;
pub const OUT_NAME: &str = "endcap-circular-2hole";

pub struct State {
    pub here: PathBuf,
    /// `_float_interface.rod_axis_from_inner_wall`, as the provider states it.
    pub rod_axis_from_inner_wall: Val,
    pub register_radius: f64,
    pub register_position: [f64; 2],
    pub out_dir: PathBuf,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let here = resolve(&rt.file(NAME));
        let docgen = ancestor_where(&here, |p| p.join("tools").join("docgen").is_dir())?;
        rt.sys_path_insert(0, &docgen.join("tools"))?;
        rt.sys_path_insert(0, &ancestor(&here, "hardware")?.join("scripts"))?;
        // `from docgen import substitute_py_comments`, `from _document_export import export_dxf`:
        // the runtime's own substitution and export.
        rt.sys_path_insert(
            0,
            &ancestor(&here, "hardware")?.join("printed-parts").join("cold-core"),
        )?;
        let rod_axis_from_inner_wall = rt.pya("_float_interface", "rod_axis_from_inner_wall")?;
        let register_radius = TUBE_ID_RADIUS - rod_axis_from_inner_wall.f()? / 25.4;
        let register_position = [-register_radius, 0.0];
        let out_dir = parent_n(&resolve(&rt.file(NAME)), 0);
        Ok(Self {
            here,
            rod_axis_from_inner_wall,
            register_radius,
            register_position,
            out_dir,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `make_disc()`: the disc outline and the two tap-drill holes, exported as the DXF cut file.
pub fn make_disc(rt: &Runtime) -> Result<PathBuf> {
    let s = state(rt)?;
    let ezdxf = rt.py("ezdxf")?;
    let doc = ezdxf.mk("new", vec![], kw!["dxfversion" => "R2010"])?;
    doc.a("header")?.set(Val::Str("$INSUNITS".into()), Val::Int(1))?;
    let msp = doc.m("modelspace", vec![])?;
    msp.m("add_circle", args![(0i64, 0i64), DISC_RADIUS])?;
    for hole_center in HOLE_POSITIONS {
        msp.m("add_circle", args![hole_center, HOLE_RADIUS])?;
    }
    let path = s.out_dir.join(format!("{OUT_NAME}.dxf"));
    rt.export_dxf(&doc, Path::new(&ps(&path)))?;
    Ok(path)
}

/// `main()`: the cut file, its summary and the source's own doc comments.
pub fn main(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    let path = make_disc(rt)?;
    rt.print(format!(
        "Exported: {}  ({} holes)",
        ps(&path),
        HOLE_POSITIONS.len()
    ))?;
    rt.print(format!(
        "  Disc diameter:   {}\"  (fits 5.000\" OD x 0.065\" wall tube, ID 4.870\")",
        pystr(DISC_DIAMETER)
    ))?;
    rt.print(format!("  Disc thickness:  {}\"", pystr(DISC_THICKNESS)))?;
    rt.print(format!(
        "  Hole diameter:   {}\"  (7/16\" tap drill for 1/4\"-18 NPT)",
        pystr(HOLE_DIAMETER)
    ))?;
    rt.print(format!(
        "  Hole spacing:    {}\" center-to-center along one axis",
        ff(HOLE_SPACING, ".4g")
    ))?;
    rt.print("  Material:        316 SS, laser-cut")?;
    rt.print("  Per carbonator:  2 identical discs, each tapped 2x 1/4\"-18 NPT")?;
    rt.print(format!(
        "  Rod register:    blind drill (NOT cut) at {} in, Ø{}\" x {}\" deep, from inside face",
        s.register_position.to_val().str()?,
        ff(REGISTER_DRILL_DIAMETER, ".4g"),
        ff(REGISTER_DEPTH, ".3g")
    ))?;
    let g = |x: f64| ff(x, ".4g");
    let variables: Vec<(String, String)> = [
        ("DISC_D_IN", format!("{} in", g(DISC_DIAMETER))),
        ("DISC_R_IN", format!("{} in", g(DISC_RADIUS))),
        ("DISC_THK_IN", format!("{} in", g(DISC_THICKNESS))),
        ("HOLE_D_IN", format!("{} in", g(HOLE_DIAMETER))),
        ("HOLE_R_IN", format!("{} in", g(HOLE_RADIUS))),
        ("HOLE_SPACING", format!("{} in", g(HOLE_SPACING))),
        ("HOLE_OFFSET", g(HOLE_SPACING / 2.0)),
        ("REGISTER_X", g(s.register_position[0])),
        ("REGISTER_R", format!("{} in", g(s.register_radius))),
        ("TUBE_ID_R", format!("{} in", g(TUBE_ID_RADIUS))),
        (
            "ROD_WALL_DISTANCE",
            format!("{} mm", fv(&s.rod_axis_from_inner_wall, "g")?),
        ),
        (
            "REGISTER_DRILL_D",
            format!("{} in", ff(REGISTER_DRILL_DIAMETER, ".3f")),
        ),
        ("REGISTER_DEPTH", format!("{} in", ff(REGISTER_DEPTH, ".2f"))),
        (
            "REGISTER_REMAINING",
            format!("{} in", g(DISC_THICKNESS - REGISTER_DEPTH)),
        ),
    ]
    .into_iter()
    .map(|(k, v)| (k.to_owned(), v))
    .collect();
    rt.substitute_py_comments(&rt.file(NAME), &variables, Some(NAME))
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

/// The native `_document_export.export_dxf(source, target_path)`.
fn export_dxf(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let document: Val = c.req(0, "source")?;
    let target = PathBuf::from(c.req::<Val>(1, "target_path")?.str()?);
    rt.export_dxf(&document, &target)?;
    Ok(Val::None)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", Val::Path(s.here.clone()));
    ns.func(rt, "substitute_py_comments", substitute_py_comments);
    ns.func(rt, "export_dxf", export_dxf);
    ns.value("rod_axis_from_inner_wall", s.rod_axis_from_inner_wall.clone());
    ns.value("disc_diameter", DISC_DIAMETER);
    ns.value("disc_radius", DISC_RADIUS);
    ns.value("disc_thickness", DISC_THICKNESS);
    ns.value("hole_diameter", HOLE_DIAMETER);
    ns.value("hole_radius", HOLE_RADIUS);
    ns.value("hole_spacing", HOLE_SPACING);
    ns.value("hole_positions", HOLE_POSITIONS.to_vec());
    ns.value("tube_id", TUBE_ID);
    ns.value("tube_id_radius", TUBE_ID_RADIUS);
    ns.value("register_radius", s.register_radius);
    ns.value("register_position", s.register_position);
    ns.value("register_drill_diameter", REGISTER_DRILL_DIAMETER);
    ns.value("register_depth", REGISTER_DEPTH);
    ns.value("out_dir", Val::Path(s.out_dir.clone()));
    ns.value("out_name", OUT_NAME);
    ns.func(rt, "make_disc", |rt, _| Ok(Val::Path(make_disc(rt)?)));
    ns.func(rt, "main", |rt, _| {
        main(rt)?;
        Ok(Val::None)
    });
    Ok(())
}
