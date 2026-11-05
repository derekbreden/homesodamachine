//! `magnetic_float`: the RC62 magnetic float, a PETG Translucent Clear envelope and a fitted
//! ASA Aero core. Every figure is this module's own; the solids come from the Rust part.

use std::f64::consts::PI;

use super::*;

pub const NAME: &str = "magnetic_float";

pub const DIAMETER: f64 = 36.0;
pub const HEIGHT: f64 = 60.06;
pub const BORE_DIAMETER: f64 = 4.8;
pub const OUTER_WALL: f64 = 3.0;
pub const BORE_WALL: f64 = 1.8;
pub const FLOOR: f64 = 3.0;
pub const ROOF: f64 = 3.06;
pub const PETG_LAYER: f64 = 0.18;
pub const PETG_FIRST_LAYER: f64 = 0.3;
pub const MAGNET_OD: f64 = 19.05;
pub const MAGNET_ID: f64 = 9.525;
pub const MAGNET_HEIGHT: f64 = 3.175;
pub const MAGNET_TOLERANCE: f64 = 0.1;
pub const MAGNET_MASS: f64 = 5.09;
pub const MAGNET_POCKET_OD: f64 = MAGNET_OD + 0.3;
pub const MAGNET_POCKET_ID: f64 = MAGNET_ID - 0.3;
pub const MAGNET_POCKET_DEPTH: f64 = 3.4;
pub const INSERT_HEIGHT: f64 = 10.0;
pub const CORE_FIT_ALLOWANCE: f64 = 0.05;
pub const INSERT_FIT_ALLOWANCE: f64 = 0.05;
pub const INSERTION_LEAD: f64 = 0.5;
pub const PETG_DENSITY: f64 = 1.25;
pub const PETG_MATERIAL: &str = "Bambu PETG Translucent Clear 32101";
pub const WATER_DENSITY: f64 = 1.0;
pub const COLORS: [(&str, &str); 3] = [
    ("petg", "#D9EBF2"),
    ("aero", "#EBC777"),
    ("magnet", "#707985"),
];
pub const INSERT_LIFT: f64 = 24.0;
pub const MAGNET_LIFT: f64 = 10.0;
pub const OUTER_RADIUS: f64 = DIAMETER / 2.0;
pub const BORE_RADIUS: f64 = BORE_DIAMETER / 2.0;
pub const CORE_OUTER_RADIUS: f64 = OUTER_RADIUS - OUTER_WALL;
pub const CORE_INNER_RADIUS: f64 = BORE_RADIUS + BORE_WALL;

/// The Aero densities the buoyancy table reads.
const DENSITIES: [f64; 6] = [0.46, 0.53, 0.55, 0.6, 0.65, 0.7];

pub struct State {
    pub argparse: Val,
    pub sys: Val,
    pub root: PathBuf,
    pub linear: Val,
    pub roof_bottom: f64,
    pub insert_top: f64,
    pub insert_bottom: f64,
    pub magnet_seat: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let argparse = rt.py("argparse")?;
        let sys = rt.py("sys")?;
        let root = ancestor_where(&resolve(&rt.file(NAME)), |p| {
            p.join("hardware/scripts/_rust_part.py").is_file()
        })?;
        rt.sys_path_insert(0, &root.join("hardware/scripts"))?;
        rt.sys_path_insert(0, &root.join("tools"))?;
        let linear = rt.pya("_materials", "linear")?;
        // `from docgen import substitute_md` imports Python's docgen; the substitution itself
        // is the runtime's.
        rt.py("docgen")?;
        let roof_bottom = round_to(HEIGHT - ROOF, 6);
        let insert_top = roof_bottom;
        let insert_bottom = insert_top - INSERT_HEIGHT;
        let magnet_seat = insert_bottom - MAGNET_POCKET_DEPTH;
        Ok(Self {
            argparse,
            sys,
            root,
            linear,
            roof_bottom,
            insert_top,
            insert_bottom,
            magnet_seat,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `ring(outer, inner, bottom, top)`: an annulus's volume.
pub fn ring(outer: f64, inner: f64, bottom: f64, top: f64) -> f64 {
    PI * (outer.powf(2.0) - inner.powf(2.0)) * (top - bottom)
}

/// `led_ring(...)`: an annulus less its two lower lead-ins.
pub fn led_ring(outer: f64, inner: f64, bottom: f64, top: f64) -> f64 {
    ring(outer, inner, bottom, top) - PI * INSERTION_LEAD.powf(2.0) * (outer + inner)
}

/// `volumes()`: each piece's volume, mm³, in the source's order.
pub fn volumes(rt: &Runtime) -> Result<[(&'static str, f64); 4]> {
    let s = state(rt)?;
    let pocket = ring(
        MAGNET_POCKET_OD / 2.0,
        MAGNET_POCKET_ID / 2.0,
        s.magnet_seat,
        s.insert_bottom,
    );
    Ok([
        (
            "body-petg",
            ring(OUTER_RADIUS, BORE_RADIUS, 0.0, HEIGHT)
                - ring(CORE_OUTER_RADIUS, CORE_INNER_RADIUS, FLOOR, s.roof_bottom),
        ),
        (
            "body-aero",
            led_ring(CORE_OUTER_RADIUS, CORE_INNER_RADIUS, FLOOR, s.insert_bottom) - pocket,
        ),
        (
            "insert-aero",
            led_ring(CORE_OUTER_RADIUS, CORE_INNER_RADIUS, s.insert_bottom, s.insert_top),
        ),
        (
            "magnet",
            ring(
                MAGNET_OD / 2.0,
                MAGNET_ID / 2.0,
                s.magnet_seat,
                s.magnet_seat + MAGNET_HEIGHT,
            ),
        ),
    ])
}

/// One row of the buoyancy table.
pub struct Buoyancy {
    pub density: f64,
    pub mass: f64,
    pub reserve: f64,
    pub freeboard: f64,
}

/// `measurements()`, as numbers.
pub struct Measurements {
    pub volumes_cc: Vec<(&'static str, f64)>,
    pub displaced: f64,
    pub petg: f64,
    pub aero: f64,
    pub buoyancy: Vec<Buoyancy>,
    roof_bottom: f64,
    insert_top: f64,
    insert_bottom: f64,
    magnet_seat: f64,
}

impl Measurements {
    pub fn water_displacement(&self) -> f64 {
        self.displaced * WATER_DENSITY
    }
    pub fn nominal_unfilled_volume(&self) -> f64 {
        pmax(
            0.0,
            self.displaced - fsum(self.volumes_cc.iter().map(|(_, v)| *v)),
        )
    }
    pub fn magnet_roof_gap(&self) -> f64 {
        self.roof_bottom - self.magnet_seat - MAGNET_HEIGHT - MAGNET_TOLERANCE
    }
    /// The dict `measurements()` returns.
    pub fn val(&self) -> Val {
        let dimensions = Dict::new()
            .with("diameter", DIAMETER)
            .with("height", HEIGHT)
            .with("bore", BORE_DIAMETER)
            .with("petg_outer_wall", OUTER_WALL)
            .with("petg_bore_wall", BORE_WALL)
            .with("petg_floor", FLOOR)
            .with("petg_roof", ROOF)
            .with("insert_height", INSERT_HEIGHT)
            .with("insert_top", self.insert_top)
            .with("insert_bottom", self.insert_bottom)
            .with("magnet_seat", self.magnet_seat)
            .with("roof_bottom", self.roof_bottom)
            .with("magnet_pocket_od", MAGNET_POCKET_OD)
            .with("magnet_pocket_id", MAGNET_POCKET_ID)
            .with("magnet_pocket_height", MAGNET_POCKET_DEPTH)
            .with("aero_lower_lead_in", INSERTION_LEAD)
            .with("insert_od", 2.0 * CORE_OUTER_RADIUS)
            .with("insert_id", 2.0 * CORE_INNER_RADIUS);
        let magnet = Dict::new()
            .with("model", "K&J RC62")
            .with("mass_g", MAGNET_MASS)
            .with("od_mm", MAGNET_OD)
            .with("id_mm", MAGNET_ID)
            .with("height_mm", MAGNET_HEIGHT)
            .with("maximum_dimensional_tolerance_mm", MAGNET_TOLERANCE)
            .with("source", "https://www.kjmagnetics.com/rc62-neodymium-ring-magnet");
        let mut volume_cc = Dict::new();
        for (name, volume) in &self.volumes_cc {
            volume_cc.set(*name, *volume);
        }
        let table: Vec<Val> = self
            .buoyancy
            .iter()
            .map(|row| {
                Dict::new()
                    .with("aero_density_g_cc", row.density)
                    .with("assembled_mass_g", row.mass)
                    .with("reserve_lift_g", row.reserve)
                    .with("upright_freeboard_mm", row.freeboard)
                    .val()
            })
            .collect();
        let neutral = (self.displaced * WATER_DENSITY - self.petg * PETG_DENSITY - MAGNET_MASS)
            / self.aero;
        let radial = pmin(
            (MAGNET_POCKET_OD - MAGNET_OD - MAGNET_TOLERANCE) / 2.0 - CORE_FIT_ALLOWANCE,
            (MAGNET_ID - MAGNET_TOLERANCE - MAGNET_POCKET_ID) / 2.0 - CORE_FIT_ALLOWANCE,
        );
        Dict::new()
            .with("dimensions_mm", dimensions)
            .with("magnet", magnet)
            .with("volume_cc", volume_cc)
            .with("water_displacement_g", self.water_displacement())
            .with("petg_material", PETG_MATERIAL)
            .with("petg_density_g_cc", PETG_DENSITY)
            .with("buoyancy", Val::list(table))
            .with("neutral_aero_density_g_cc", neutral)
            .with("nominal_unfilled_volume_cc", self.nominal_unfilled_volume())
            .with("aero_material", "Bambu ASA Aero White 46100")
            .with("core_print_fit_allowance_radial_mm", CORE_FIT_ALLOWANCE)
            .with("insert_print_fit_allowance_radial_mm", INSERT_FIT_ALLOWANCE)
            .with(
                "minimum_seated_magnet_top_to_roof_bottom_mm",
                self.magnet_roof_gap(),
            )
            .with("magnet_pocket_minimum_compensated_radial_clearance_mm", radial)
            .with(
                "magnet_pocket_minimum_depth_clearance_mm",
                MAGNET_POCKET_DEPTH - MAGNET_HEIGHT - MAGNET_TOLERANCE,
            )
            .with(
                "fit",
                "The Aero pieces have 0.5 mm lower outer/bore lead-ins and 0.05 mm radial contour expansion and bore reduction on their straight lands. The RC62 seats in a clearance pocket below the insert. The insert top supports the full roof. Intentional unfilled volume comprises lower lead-ins and magnet-pocket clearance.",
            )
            .with(
                "pressure_rating",
                "Unqualified prototype; no hydrostatic test recorded.",
            )
            .val()
    }
}

/// `measurements()`: the float's design record.
pub fn measurements(rt: &Runtime) -> Result<Measurements> {
    let s = state(rt)?;
    let volumes_cc: Vec<(&'static str, f64)> = volumes(rt)?
        .iter()
        .map(|(name, volume)| (*name, volume / 1000.0))
        .collect();
    let displaced = PI * (OUTER_RADIUS.powf(2.0) - BORE_RADIUS.powf(2.0)) * HEIGHT / 1000.0;
    let cc = |name: &str| {
        volumes_cc
            .iter()
            .find(|(n, _)| *n == name)
            .map(|(_, v)| *v)
            .unwrap_or_default()
    };
    let petg = cc("body-petg");
    let aero = cc("body-aero") + cc("insert-aero");
    let buoyancy = DENSITIES
        .iter()
        .map(|&density| {
            let mass = petg * PETG_DENSITY + aero * density + MAGNET_MASS;
            let reserve = displaced * WATER_DENSITY - mass;
            Buoyancy {
                density,
                mass,
                reserve,
                freeboard: HEIGHT * reserve / displaced,
            }
        })
        .collect();
    Ok(Measurements {
        volumes_cc,
        displaced,
        petg,
        aero,
        buoyancy,
        roof_bottom: s.roof_bottom,
        insert_top: s.insert_top,
        insert_bottom: s.insert_bottom,
        magnet_seat: s.magnet_seat,
    })
}

/// `numbers()`, as the ordered dict it builds.
fn numbers_dict(rt: &Runtime) -> Result<Dict> {
    let s = state(rt)?;
    let mut d = Dict::new()
        .with("diameter", DIAMETER)
        .with("height", HEIGHT)
        .with("outer_radius", OUTER_RADIUS)
        .with("bore_radius", BORE_RADIUS)
        .with("core_outer_radius", CORE_OUTER_RADIUS)
        .with("core_inner_radius", CORE_INNER_RADIUS)
        .with("floor", FLOOR)
        .with("roof_bottom", s.roof_bottom)
        .with("insert_bottom", s.insert_bottom)
        .with("insert_top", s.insert_top)
        .with("magnet_seat", s.magnet_seat)
        .with("magnet_height", MAGNET_HEIGHT)
        .with("magnet_outer_radius", MAGNET_OD / 2.0)
        .with("magnet_inner_radius", MAGNET_ID / 2.0)
        .with("magnet_tolerance", MAGNET_TOLERANCE)
        .with("pocket_outer_radius", MAGNET_POCKET_OD / 2.0)
        .with("pocket_inner_radius", MAGNET_POCKET_ID / 2.0)
        .with("insertion_lead", INSERTION_LEAD)
        .with("insert_lift", INSERT_LIFT)
        .with("magnet_lift", MAGNET_LIFT);
    for (material, color) in COLORS {
        let linear = s.linear.c(args![color])?;
        d.set(format!("color_{material}"), Val::list(linear.list()?));
    }
    Ok(d)
}

/// `numbers()`: the figures the Rust part cuts the float from.
pub fn numbers(rt: &Runtime) -> Result<Val> {
    Ok(numbers_dict(rt)?.val())
}

/// `check(asked)`: the Rust part's check of the float's figures.
pub fn check(rt: &Runtime, asked: Val) -> Result<Val> {
    let rust_part = rt.py("_rust_part")?;
    let mut figures = numbers_dict(rt)?;
    figures.set("check", asked);
    rust_part.m("check", args!["cold-core", "magnetic-float", figures])
}

/// `write(output)`: the float's STEP, `design.json`, and the README's figures.
pub fn write(rt: &Runtime, output: &Path) -> Result<()> {
    let s = state(rt)?;
    let rust_part = rt.py("_rust_part")?;
    std::fs::create_dir_all(output)?;
    rust_part.m(
        "cut",
        args!["cold-core", "magnetic-float", numbers(rt)?, output.to_owned()],
    )?;
    let info = measurements(rt)?;
    let record = info.val();
    write_text(
        &output.join("design.json"),
        &(json_dumps(&record, kw!["indent" => 2i64])? + "\n"),
    )?;
    let readme = output.join("README.md");
    if readme.exists() {
        let g = |x: f64| ff(x, "g");
        let mut figures: OMap<String> = OMap::new();
        for (key, value) in [
            ("FLOAT_DIAMETER", format!("{} mm", g(DIAMETER))),
            ("FLOAT_HEIGHT", format!("{} mm", g(HEIGHT))),
            ("FLOAT_BORE", format!("{} mm", g(BORE_DIAMETER))),
            ("OUTER_WALL", format!("{} mm", g(OUTER_WALL))),
            ("BORE_WALL", format!("{} mm", g(BORE_WALL))),
            ("FLOOR", format!("{} mm", g(FLOOR))),
            ("ROOF", format!("{} mm", g(ROOF))),
            ("INSERT_HEIGHT", format!("{} mm", g(INSERT_HEIGHT))),
            (
                "INSERT_SIZE",
                format!(
                    "{} × {} × {} mm",
                    g(2.0 * CORE_OUTER_RADIUS),
                    g(2.0 * CORE_INNER_RADIUS),
                    g(INSERT_HEIGHT)
                ),
            ),
            (
                "MAGNET_SIZE",
                format!(
                    "{} × {} × {} mm",
                    g(MAGNET_OD),
                    g(MAGNET_ID),
                    g(MAGNET_HEIGHT)
                ),
            ),
            ("MAGNET_SEAT", format!("{} mm", g(s.magnet_seat))),
            (
                "INSERT_STATIONS",
                format!("{} / {} mm", g(s.insert_bottom), g(s.insert_top)),
            ),
            ("ROOF_BOTTOM", format!("{} mm", g(s.roof_bottom))),
            (
                "DISPLACEMENT",
                format!("{} g", ff(info.water_displacement(), ".2f")),
            ),
            (
                "UNFILLED_VOLUME",
                format!("{} cm³", ff(info.nominal_unfilled_volume(), ".3f")),
            ),
            ("FIT_ALLOWANCE", format!("{} mm", g(INSERT_FIT_ALLOWANCE))),
            ("PAUSE_LAYER", format!("{} mm", g(s.roof_bottom + PETG_LAYER))),
            ("ROOF_LAYERS", format!("{} layers", round_int(ROOF / PETG_LAYER))),
            ("MAGNET_ROOF_GAP", format!("{} mm", g(info.magnet_roof_gap()))),
        ] {
            figures.set(key, value);
        }
        for row in &info.buoyancy {
            let code = fi(round_int(row.density * 100.0), "03d");
            figures.set(&format!("MASS_{code}"), format!("{} g", ff(row.mass, ".2f")));
            figures.set(&format!("LIFT_{code}"), format!("{} g", ff(row.reserve, ".2f")));
        }
        rt.substitute_md(&readme, &figures.0, Some(NAME))?;
    }
    rt.pya("builtins", "print")?.ck(
        args![json_dumps(&record, kw!["indent" => 2i64])?],
        kw!["flush" => true],
    )?;
    Ok(())
}

/// The module's `main()`: the float written where `--output` says.
pub fn run(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    let doc = super::table::documentation(NAME).map_or(Val::None, Val::from);
    let parser = s
        .argparse
        .a("ArgumentParser")?
        .ck(vec![], kw!["description" => doc])?;
    let here = resolve(&rt.file(NAME));
    parser.mk(
        "add_argument",
        args!["--output"],
        kw![
            "type" => rt.import_module("pathlib")?.a("Path")?,
            "default" => Val::Path(here.parent().map(PathBuf::from).unwrap_or_default())
        ],
    )?;
    let args = parser.m("parse_args", vec![])?;
    write(rt, &PathBuf::from_val(&args.a("output")?)?)
}

/// The native `substitute_md(path, variables)` this module imported from docgen.
fn substitute_md(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let path = PathBuf::from(c.req::<Val>(0, "path")?.str()?);
    let variables: Val = c.req(1, "variables")?;
    let mut values = vec![];
    for key in variables.iter()? {
        values.push((key.str()?, variables.get(key)?.str()?));
    }
    rt.substitute_md(&path, &values, Some(NAME))?;
    Ok(Val::None)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("argparse", s.argparse.clone());
    ns.module(rt, "json", "json")?;
    ns.module(rt, "math", "math")?;
    ns.value("sys", s.sys.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("ROOT", Val::Path(s.root.clone()));
    ns.value("linear", s.linear.clone());
    ns.func(rt, "substitute_md", substitute_md);
    ns.value("diameter", DIAMETER);
    ns.value("height", HEIGHT);
    ns.value("bore_diameter", BORE_DIAMETER);
    ns.value("outer_wall", OUTER_WALL);
    ns.value("bore_wall", BORE_WALL);
    ns.value("floor", FLOOR);
    ns.value("roof", ROOF);
    ns.value("petg_layer", PETG_LAYER);
    ns.value("petg_first_layer", PETG_FIRST_LAYER);
    ns.value("magnet_od", MAGNET_OD);
    ns.value("magnet_id", MAGNET_ID);
    ns.value("magnet_height", MAGNET_HEIGHT);
    ns.value("magnet_tolerance", MAGNET_TOLERANCE);
    ns.value("magnet_mass", MAGNET_MASS);
    ns.value("magnet_pocket_od", MAGNET_POCKET_OD);
    ns.value("magnet_pocket_id", MAGNET_POCKET_ID);
    ns.value("magnet_pocket_depth", MAGNET_POCKET_DEPTH);
    ns.value("insert_height", INSERT_HEIGHT);
    ns.value("core_fit_allowance", CORE_FIT_ALLOWANCE);
    ns.value("insert_fit_allowance", INSERT_FIT_ALLOWANCE);
    ns.value("insertion_lead", INSERTION_LEAD);
    ns.value("petg_density", PETG_DENSITY);
    ns.value("petg_material", PETG_MATERIAL);
    ns.value("water_density", WATER_DENSITY);
    let mut colors = Dict::new();
    for (material, color) in COLORS {
        colors.set(material, color);
    }
    ns.value("colors", colors);
    ns.value("insert_lift", INSERT_LIFT);
    ns.value("magnet_lift", MAGNET_LIFT);
    ns.value("outer_radius", OUTER_RADIUS);
    ns.value("bore_radius", BORE_RADIUS);
    ns.value("core_outer_radius", CORE_OUTER_RADIUS);
    ns.value("core_inner_radius", CORE_INNER_RADIUS);
    ns.value("roof_bottom", s.roof_bottom);
    ns.value("insert_top", s.insert_top);
    ns.value("insert_bottom", s.insert_bottom);
    ns.value("magnet_seat", s.magnet_seat);
    ns.func(rt, "ring", |_, c| {
        Ok(Val::Float(ring(
            c.req(0, "outer")?,
            c.req(1, "inner")?,
            c.req(2, "bottom")?,
            c.req(3, "top")?,
        )))
    });
    ns.func(rt, "led_ring", |_, c| {
        Ok(Val::Float(led_ring(
            c.req(0, "outer")?,
            c.req(1, "inner")?,
            c.req(2, "bottom")?,
            c.req(3, "top")?,
        )))
    });
    ns.func(rt, "volumes", |rt, _| {
        let mut d = Dict::new();
        for (name, volume) in volumes(rt)? {
            d.set(name, volume);
        }
        Ok(d.val())
    });
    ns.func(rt, "measurements", |rt, _| Ok(measurements(rt)?.val()));
    ns.func(rt, "numbers", |rt, _| numbers(rt));
    ns.func(rt, "check", |rt, c| check(rt, c.req(0, "asked")?));
    ns.func(rt, "write", |rt, c| {
        write(rt, &c.req::<PathBuf>(0, "output")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "main", |rt, _| {
        run(rt)?;
        Ok(Val::None)
    });
    Ok(())
}

pub fn main(rt: &Runtime) -> Result<()> {
    rt.pya("_rust_part", "start")?.c(vec![])?;
    run(rt)
}
