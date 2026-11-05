//! `all_aero_float`: the one-piece ASA Aero bench float with an RC62 at its axial midplane.
//! Its figures come from `_float_interface`; its solids and measurements from the Rust part.

use super::*;

pub const NAME: &str = "all_aero_float";

/// The names `from _float_interface import ...` binds, in its order.
pub const FLOAT_NAMES: [&str; 30] = [
    "diameter",
    "bore_diameter",
    "guide_diameter",
    "magnet_od",
    "magnet_id",
    "magnet_thickness",
    "magnet_tolerance",
    "magnet_mass",
    "pocket_od",
    "pocket_id",
    "pocket_depth",
    "water_density",
    "design_foam_density",
    "minimum_reserve_lift_g",
    "height_increment",
    "layer_height",
    "xy_contour_compensation",
    "xy_hole_compensation",
    "annular_area",
    "pocket_volume",
    "minimum_height",
    "height",
    "magnet_midplane",
    "magnet_seat",
    "pocket_roof",
    "pause_before_z",
    "rod_axis_from_inner_wall",
    "minimum_wall_clearance",
    "maximum_wall_clearance",
    "magnet_above_waterline",
];

pub struct State {
    pub argparse: Val,
    pub sys: Val,
    pub root: PathBuf,
    pub here: PathBuf,
    /// The `_float_interface` figures, as the provider states them.
    pub float: OMap<Val>,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let argparse = rt.py("argparse")?;
        let sys = rt.py("sys")?;
        let file = resolve(&rt.file(NAME));
        let root = ancestor_where(&file, |p| p.join("hardware/scripts/_rust_part.py").is_file())?;
        let here = file.parent().map(PathBuf::from).unwrap_or_default();
        rt.sys_path_insert(0, &root.join("hardware/scripts"))?;
        rt.sys_path_insert(0, &parent_n(&here, 1))?;
        let interface = rt.py("_float_interface")?;
        let mut float = OMap::new();
        for name in FLOAT_NAMES {
            float.set(name, interface.a(name)?);
        }
        Ok(Self {
            argparse,
            sys,
            root,
            here,
            float,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `measurements()`: the Rust part's measurement of the float.
pub fn measurements(rt: &Runtime) -> Result<Val> {
    rt.pya("_cold_core_data", "read")?.c(args!["aero-measurements"])
}

/// `numbers()`: the figures the Rust part cuts the float from.
pub fn numbers(rt: &Runtime) -> Result<Val> {
    let read = rt.pya("_cold_core_data", "read")?;
    let linear = rt.pya("_materials", "linear")?;
    let aero = Val::list(linear.c(args!["#EEE4C4"])?.list()?);
    let magnet = Val::list(linear.c(args!["#737D88"])?.list()?);
    read.ck(
        args!["aero-numbers"],
        kw!["colors" => dict!["aero" => aero, "magnet" => magnet]],
    )
}

/// `write(output)`: the float's STEP, print payload and `design.json`.
pub fn write(rt: &Runtime, output: &Path) -> Result<()> {
    let s = state(rt)?;
    let rust_part = rt.py("_rust_part")?;
    let write_print_payload = rt.pya("flute_payload", "cut")?;
    let output = output.to_owned();
    std::fs::create_dir_all(&output)?;
    rust_part.m(
        "cut",
        args!["cold-core", "all-aero-float", numbers(rt)?, output.clone()],
    )?;
    write_print_payload.c(args![
        output.join("float-aero.step"),
        output.join("float-aero.stl")
    ])?;
    let info = measurements(rt)?;
    write_text(
        &output.join("design.json"),
        &(json_dumps(&info, kw!["indent" => 2i64])? + "\n"),
    )?;
    let summary = dict![
        "height_mm" => s.float.at("height")?,
        "minimum_height_mm" => s.float.at("minimum_height")?,
        "midplane_mm" => s.float.at("magnet_midplane")?,
        "buoyancy" => info.k("buoyancy")?,
    ];
    rt.print(json_dumps(&summary, kw!["indent" => 2i64])?)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("argparse", s.argparse.clone());
    ns.module(rt, "json", "json")?;
    ns.value("sys", s.sys.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("ROOT", Val::Path(s.root.clone()));
    ns.value("HERE", Val::Path(s.here.clone()));
    for (name, value) in s.float.iter() {
        ns.value(name, value.clone());
    }
    ns.func(rt, "measurements", |rt, _| measurements(rt));
    ns.func(rt, "numbers", |rt, _| numbers(rt));
    ns.func(rt, "write", |rt, c| {
        let output = c.opt::<PathBuf>(0, "output", state(rt)?.here.clone())?;
        write(rt, &output)?;
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
            "default" => Val::Path(s.here.clone())
        ],
    )?;
    let args = parser.m("parse_args", vec![])?;
    write(rt, &PathBuf::from_val(&args.a("output")?)?)
}
