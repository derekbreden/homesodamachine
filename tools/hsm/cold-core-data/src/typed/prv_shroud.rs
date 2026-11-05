//! `prv_shroud`: the printed PETG cup that surrounds the Control Devices SV-125
//! pressure-relief valve during the cold-core body foam pour.

use std::f64::consts::PI;

use super::*;

pub const NAME: &str = "prv_shroud";

pub const WALL_THICKNESS: f64 = 2.0;
pub const CAP_THICKNESS: f64 = 2.0;
pub const CAVITY_LENGTH: f64 = 44.0;
pub const VENT_STATION_Z: f64 = 37.88;
pub const TOTAL_LENGTH: f64 = CAVITY_LENGTH + CAP_THICKNESS;
pub const OVERCUT: f64 = 0.1;

pub struct State {
    pub argparse: Val,
    pub sys: Val,
    pub here: PathBuf,
    pub fits: Val,
    /// `fits.supported_surface`, as the provider states it.
    pub supported_surface: Val,
    pub inner_diameter: f64,
    pub vent_hole_diameter: f64,
    pub outer_diameter: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let argparse = rt.py("argparse")?;
        let sys = rt.py("sys")?;
        let here = resolve(&rt.file(NAME));
        rt.sys_path_insert(0, &ancestor(&here, "hardware")?.join("scripts"))?;
        rt.sys_path_insert(
            0,
            &ancestor_where(&here, |p| p.join("tools").join("docgen").is_dir())?.join("tools"),
        )?;
        rt.sys_path_insert(0, &parent_n(&here, 1))?;
        rt.sys_path_insert(0, &ancestor(&here, "printed-parts")?.join("cadlib"))?;
        let fits = rt.py("fits")?;
        // `from docgen import substitute_md, substitute_py_comments` imports Python's docgen;
        // the substitution itself is the runtime's.
        rt.py("docgen")?;
        let slip = fits.a("slip")?.f()?;
        let inner_diameter = 18.8 + 2.0 * slip;
        let vent_hole_diameter = 6.5 + 2.0 * slip;
        let outer_diameter = inner_diameter + 2.0 * WALL_THICKNESS;
        let supported_surface = fits.a("supported_surface")?;
        Ok(Self {
            argparse,
            sys,
            here,
            fits,
            supported_surface,
            inner_diameter,
            vent_hole_diameter,
            outer_diameter,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `numbers()`: the figures the Rust part cuts the shroud from.
pub fn numbers(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let shroud = rt.pya("_materials", "C_SHROUD")?;
    let linear = rt.pya("_materials", "linear")?;
    Ok(dict![
        "inner_radius" => s.inner_diameter / 2.0,
        "outer_radius" => s.outer_diameter / 2.0,
        "cavity_length" => CAVITY_LENGTH,
        "total_length" => TOTAL_LENGTH,
        "vent_radius" => s.vent_hole_diameter / 2.0,
        "vent_station_z" => VENT_STATION_Z,
        "overcut" => OVERCUT,
        "supported_surface" => s.supported_surface.clone(),
        "color" => Val::list(linear.c(vec![shroud])?.list()?),
    ])
}

/// `volume()`: the shroud's volume, mm³, the vent's two bores taken out by Simpson's rule.
pub fn volume(rt: &Runtime) -> Result<f64> {
    let s = state(rt)?;
    let (outer, inner, radius) = (
        s.outer_diameter / 2.0,
        s.inner_diameter / 2.0,
        s.vent_hole_diameter / 2.0,
    );
    let allowance = s.supported_surface.f()?;
    let split = (allowance / (2.0 * radius)).acos();
    let strip = |theta: f64, overlapping: bool| {
        let x = radius * theta.sin();
        let half = radius * theta.cos();
        let depth = (outer * outer - x * x).sqrt() - (inner * inner - x * x).sqrt();
        let height = if overlapping {
            2.0 * half + allowance
        } else {
            4.0 * half
        };
        depth * height * half
    };
    let integral = |start: f64, stop: f64, overlapping: bool| {
        let count = 128i64;
        let step = (stop - start) / count as f64;
        let mut total = strip(start, overlapping) + strip(stop, overlapping);
        total += fsum((1..count).map(|i| {
            let weight = if i % 2 != 0 { 4.0 } else { 2.0 };
            weight * strip(start + i as f64 * step, overlapping)
        }));
        total * step / 3.0
    };
    let removed = 2.0 * (integral(0.0, split, true) + integral(split, PI / 2.0, false));
    Ok(PI * (outer * outer * TOTAL_LENGTH - inner * inner * CAVITY_LENGTH) - removed)
}

/// The module's `main(output=None)`: the shroud's STEP, then its documents.
pub fn run(rt: &Runtime, output: Option<PathBuf>) -> Result<()> {
    let s = state(rt)?;
    let out_dir = match output {
        Some(path) => path,
        None => s.here.parent().map(PathBuf::from).unwrap_or_default(),
    };
    std::fs::create_dir_all(&out_dir)?;
    let rust_part = rt.py("_rust_part")?;
    rust_part.m(
        "cut",
        args!["cold-core", "prv-shroud", numbers(rt)?, out_dir.clone()],
    )?;
    let vol = volume(rt)?;
    let radius = s.outer_diameter / 2.0;
    rt.print(format!(
        "-> prv-shroud.step  bbox X[{}..{}] Y[{}..{}] Z[{}..{}]  vol {} mm^3",
        ff(-radius, "6.2f"),
        ff(radius, "6.2f"),
        ff(-radius, "6.2f"),
        ff(radius, "6.2f"),
        ff(0.0, "6.2f"),
        ff(TOTAL_LENGTH, "6.2f"),
        ff(vol, ".3f")
    ))?;
    document(rt, vol)
}

/// `document(vol)`: the README's and this source's figures.
pub fn document(rt: &Runtime, vol: f64) -> Result<()> {
    let s = state(rt)?;
    let out_dir = s.here.parent().map(PathBuf::from).unwrap_or_default();
    let radius = s.outer_diameter / 2.0;
    let g = |x: f64| format!("{} mm", ff(x, ".4g"));
    let span = |a: f64, b: f64| format!("{} to {} mm", ff(a, ".3f"), ff(b, ".3f"));
    let variables: Vec<(String, String)> = [
        ("PRV_INNER_D", g(s.inner_diameter)),
        ("PRV_WALL_T", g(WALL_THICKNESS)),
        ("PRV_CAP_T", g(CAP_THICKNESS)),
        ("CAVITY_L", g(CAVITY_LENGTH)),
        ("PRV_VENT_D", g(s.vent_hole_diameter)),
        ("VENT_STATION", g(VENT_STATION_Z)),
        ("PRV_OUTER_D", g(s.outer_diameter)),
        ("TOTAL_L", g(TOTAL_LENGTH)),
        ("OVERCUT", g(OVERCUT)),
        ("PRV_VOLUME", format!("{} mm³", ff(vol, ".3f"))),
        ("PRV_BBOX_X", span(-radius, radius)),
        ("PRV_BBOX_Y", span(-radius, radius)),
        ("PRV_BBOX_Z", span(0.0, TOTAL_LENGTH)),
    ]
    .into_iter()
    .map(|(k, v)| (k.to_owned(), v))
    .collect();
    rt.substitute_md(&out_dir.join("README.md"), &variables, Some(NAME))?;
    rt.print("-> README.md")?;
    let source = rt.file(NAME);
    rt.substitute_py_comments(&source, &variables, Some(NAME))?;
    let name = source
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    rt.print(format!("-> {name} (self)"))
}

/// The `variables` of a docgen call, positional or by keyword, as `str()` of each value.
fn substitution(c: &mut Call) -> Result<(PathBuf, Vec<(String, String)>)> {
    let path = PathBuf::from(c.req::<Val>(0, "path")?.str()?);
    let variables: Val = c.req(1, "variables")?;
    let mut values = vec![];
    for key in variables.iter()? {
        values.push((key.str()?, variables.get(key)?.str()?));
    }
    Ok((path, values))
}

/// The native `substitute_md(path, variables)` this module imported from docgen.
fn substitute_md(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let (path, values) = substitution(c)?;
    rt.substitute_md(&path, &values, Some(NAME))?;
    Ok(Val::None)
}

/// The native `substitute_py_comments(path, variables)` this module imported from docgen.
fn substitute_py_comments(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let (path, values) = substitution(c)?;
    rt.substitute_py_comments(&path, &values, Some(NAME))?;
    Ok(Val::None)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("argparse", s.argparse.clone());
    ns.module(rt, "math", "math")?;
    ns.value("sys", s.sys.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", Val::Path(s.here.clone()));
    ns.value("fits", s.fits.clone());
    ns.func(rt, "substitute_md", substitute_md);
    ns.func(rt, "substitute_py_comments", substitute_py_comments);
    ns.value("inner_diameter", s.inner_diameter);
    ns.value("wall_thickness", WALL_THICKNESS);
    ns.value("cap_thickness", CAP_THICKNESS);
    ns.value("cavity_length", CAVITY_LENGTH);
    ns.value("vent_hole_diameter", s.vent_hole_diameter);
    ns.value("vent_station_z", VENT_STATION_Z);
    ns.value("outer_diameter", s.outer_diameter);
    ns.value("total_length", TOTAL_LENGTH);
    ns.value("overcut", OVERCUT);
    ns.func(rt, "numbers", |rt, _| numbers(rt));
    ns.func(rt, "volume", |rt, _| Ok(Val::Float(volume(rt)?)));
    ns.func(rt, "main", |rt, c| {
        run(rt, c.opt::<Option<PathBuf>>(0, "output", None)?)?;
        Ok(Val::None)
    });
    ns.func(rt, "document", |rt, c| {
        document(rt, c.req(0, "vol")?)?;
        Ok(Val::None)
    });
    Ok(())
}

pub fn main(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    rt.pya("_rust_part", "start")?.c(vec![])?;
    let doc = super::table::documentation(NAME).map_or(Val::None, Val::from);
    let parser = s
        .argparse
        .a("ArgumentParser")?
        .ck(vec![], kw!["description" => doc])?;
    parser.mk(
        "add_argument",
        args!["--output"],
        kw![
            "type" => rt.import_module("pathlib")?.a("Path")?,
            "default" => Val::Path(s.here.parent().map(PathBuf::from).unwrap_or_default())
        ],
    )?;
    let args = parser.m("parse_args", vec![])?;
    run(rt, Option::<PathBuf>::from_val(&args.a("output")?)?)
}
