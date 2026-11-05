//! `foam_assembly`: the three-piece cold-core casing in its native assembly frame, the cap
//! conduits' stations and mouths, and the assembly's printed report.

use super::above_core_mounts as mounts;
use super::cold_core_interface as core;
use super::foam_cap_parts;
use super::foam_numbers;
use super::internal_routes;
use super::*;

pub const NAME: &str = "foam_assembly";

/// The names `from _cold_core_interface import ...` binds, in the statement's order.
const INTERFACE_NAMES: &[&str] = &[
    "cap_side_anchors",
    "attachment_xy_positions",
    "cap_shell_clearance",
    "foam_cap_height",
    "cap_anchors",
    "cap_conduits",
    "cap_conduit_floor_xy",
    "cap_passive_guides",
    "cap_cable_guides",
    "cap_conduit_axis",
    "cap_conduit_bore_radius",
    "co2_inlet_tube_radius",
    "screw_clearance_radius",
    "deck_mount_xy",
    "foam_shell_outer_height",
    "head_pad_height",
];

/// `cap_conduit_axis`, as the interface states it.
const CAP_CONDUIT_AXIS: [f64; 3] = [0.0, 0.0, 1.0];

/// `ROUTE_SPOOLS`: each internal line's tubing spool.
const ROUTE_SPOOLS: [(&str, &str); 8] = [
    ("water-in", "white"),
    ("carb-water-out", "blue"),
    ("co2-in", "red"),
    ("prv-vent", "black"),
    ("reservoir-a", "black"),
    ("reservoir-a-fill", "black"),
    ("reservoir-b", "black"),
    ("reservoir-b-fill", "black"),
];

/// `RESERVOIRS`: each reservoir's part stem.
pub const RESERVOIRS: [(&str, &str); 2] = [
    ("reservoir A", "reservoir-right"),
    ("reservoir B", "reservoir-left"),
];

pub struct State {
    here: PathBuf,
    repo: PathBuf,
    hw: PathBuf,
    cold_core: PathBuf,
    sys: Val,
    pub co2_inlet_xyz: Val,
    routing: Val,
    mat: Val,
    pub cap_face_over_floor: f64,
    shell_step: PathBuf,
    cap_dir: PathBuf,
    reservoir_dir: PathBuf,
    pub reservoir_cap_z: Num,
    shell_color: Val,
    pub colors: OMap<Val>,
    pub route_colors: OMap<Val>,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let sys = rt.py("sys")?;
        let here = resolve(&rt.file(NAME));
        let repo = ancestor_where(&here, |p| {
            p.join("hardware")
                .join("scripts")
                .join("_cadq_export.py")
                .is_file()
        })?;
        let hw = repo.join("hardware");
        let cold_core = hw.join("printed-parts").join("cold-core");
        rt.sys_path_insert(0, &hw.join("scripts"))?;
        rt.sys_path_insert(0, &cold_core)?;
        rt.sys_path_insert(0, &hw.join("printed-parts").join("cadlib"))?;
        core::state(rt)?;
        let fc = foam_cap_parts::state(rt)?;
        let co2_inlet_xyz = rt.import_module("_port_cuts")?.a("co2_inlet_xyz")?; // via namespace: _port_cuts
        let routes = internal_routes::state(rt)?;
        let routing = rt.py("_routing")?;
        let mat = rt.py("_materials")?;
        mounts::state(rt)?;
        let cap_face_over_floor = fc.cap_face_z - fc.stack_floor_z;
        let shell_step = cold_core.join("foam-shell").join("foam-shell.step");
        let cap_dir = cold_core.join("foam-cap");
        let reservoir_dir = cold_core.join("reservoir");
        let reservoir_cap_z = routes.reservoir_cap_z;
        let shell_color = mat.a("C_FOAM_SHELL")?;
        let mut colors = OMap::new();
        colors.set("foam-cap-lid-top", mat.a("C_CAP_LID_TOP")?);
        colors.set("foam-cap-bottom", mat.a("C_CAP_BOTTOM")?);
        let mut route_colors = OMap::new();
        for (name, key) in ROUTE_SPOOLS {
            route_colors.set(name, routing.m("color", args![key])?);
        }
        Ok(Self {
            here,
            repo,
            hw,
            cold_core,
            sys,
            co2_inlet_xyz,
            routing,
            mat,
            cap_face_over_floor,
            shell_step,
            cap_dir,
            reservoir_dir,
            reservoir_cap_z,
            shell_color,
            colors,
            route_colors,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

fn parent(path: &Path) -> PathBuf {
    path.parent().unwrap_or(path).to_owned()
}

/// `spin_xy(p)`: a cap-frame plan point turned half a turn into the shell's frame.
pub fn spin_xy(p: [f64; 2]) -> [f64; 2] {
    [-p[0], -p[1]]
}

/// `cap_conduit_station(name)`: a conduit's centre in the shell's frame.
pub fn cap_conduit_station(rt: &Runtime, name: &str) -> Result<[f64; 2]> {
    Ok(spin_xy(*core::state(rt)?.cap_conduits.at(name)?))
}

/// `cap_conduit_axis_out()`.
pub fn cap_conduit_axis_out() -> [f64; 3] {
    CAP_CONDUIT_AXIS
}

/// `cap_conduit_mouth(name)`: where a conduit leaves the cap face, and its outward axis.
pub fn cap_conduit_mouth(rt: &Runtime, name: &str) -> Result<([f64; 3], [f64; 3])> {
    if name == "reservoir-b-fill" {
        let passage = mounts::reservoir_b_fill_passage(rt)?;
        let point = passage.k("entry_world_mm")?;
        let mouth = internal_routes::world_point_in_shell(rt, &point)?;
        let outward = passage.k("outward_axis_world")?.floats()?;
        let along: Vec<f64> = point
            .floats()?
            .iter()
            .zip(&outward)
            .map(|(p, a)| p + a)
            .collect();
        let outside = internal_routes::world_point_in_shell(rt, &Tuple(along).to_val())?;
        return Ok((mouth, sub3(outside, mouth)));
    }
    let [x, y] = cap_conduit_station(rt, name)?;
    let cap_face_z = foam_cap_parts::state(rt)?.cap_face_z;
    Ok(([x, y, cap_face_z], CAP_CONDUIT_AXIS))
}

/// `cap_anchor_station(name)`.
pub fn cap_anchor_station(rt: &Runtime, name: &str) -> Result<[f64; 2]> {
    Ok(spin_xy(core::state(rt)?.cap_anchors.at(name)?.centre))
}

/// `cap_side_anchor_station(name)`.
pub fn cap_side_anchor_station(rt: &Runtime, name: &str) -> Result<[f64; 2]> {
    let core = core::state(rt)?;
    let a = core.cap_side_anchors.at(name)?;
    Ok(spin_xy([a.centre[0] + a.axis_off, a.centre[1]]))
}

/// `deck_mount_station(name)`.
pub fn deck_mount_station(rt: &Runtime, name: &str) -> Result<Vec<[f64; 2]>> {
    Ok(core::state(rt)?
        .deck_mount_xy(name)?
        .into_iter()
        .map(spin_xy)
        .collect())
}

/// Python's `pattern % values`.
fn percent(pattern: &str, values: Vec<Val>) -> Result<String> {
    hsm_documents::interop::binary("mod", Val::Str(pattern.into()), Val::Tuple(values))?.str()
}

/// `next(project(row) for row in rows if test(row))`, every row tested and every match
/// projected, as the runtime evaluates it.
fn first(
    rows: &[Val],
    test: impl Fn(&Val) -> Result<bool>,
    project: impl Fn(&Val) -> Result<Val>,
) -> Result<Val> {
    let mut found = vec![];
    for row in rows {
        if test(row)? {
            found.push(project(row)?);
        }
    }
    found.into_iter().next().context("StopIteration")
}

fn is(value: Val, text: &str) -> Result<bool> {
    hsm_documents::interop::eq(&value, &Val::Str(text.into()))
}

/// `bounds(name)`: one placed part's measured box, as its low and high corners.
fn bounds(measurements: &Val, name: &str) -> Result<(Vec<Val>, Vec<Val>)> {
    let pair = measurements.k("bounds")?.k(name)?.list()?;
    ensure!(pair.len() == 2, "expected 2 values, got {}", pair.len());
    Ok((pair[0].list()?, pair[1].list()?))
}

/// `_report(placed, *, measurements)`: the casing's printed checks.
pub fn report(rt: &Runtime, placed: &OMap<Val>, measurements: &Val) -> Result<()> {
    let core = core::state(rt)?;
    let b = &core.base;
    let fc = foam_cap_parts::state(rt)?;
    let s = state(rt)?;
    let m = own(measurements)?;
    rt.print("  part                  X range            Y range            Z range")?;
    for (name, row) in placed.iter() {
        let parts = row.list()?;
        ensure!(parts.len() == 2, "expected 2 values, got {}", parts.len());
        let (low, high) = bounds(&m, name)?;
        rt.print(percent(
            "  %-19s [%7.1f,%7.1f]  [%7.1f,%7.1f]  [%7.1f,%7.1f]",
            vec![
                name.into(),
                low[0].clone(),
                high[0].clone(),
                low[1].clone(),
                high[1].clone(),
                low[2].clone(),
                high[2].clone(),
            ],
        )?)?;
    }
    let screws: Vec<[f64; 2]> = b
        .attachment_xy_positions
        .iter()
        .map(|[x, y]| [round_to(*x, 6), round_to(*y, 6)])
        .collect();
    let floor = bounds(&m, "foam-cap-bottom")?.0[2].f()?;
    let face = bounds(&m, "foam-cap-lid-top")?.0[2].f()? + fc.lid_total_height;
    ensure!(
        (floor - fc.stack_floor_z).abs() < 1e-06 && (face - fc.cap_face_z).abs() < 1e-06,
        "the stack stands on {} and presents its cap face at {}, against the {} / {} this module tells the machine to expect",
        ff(floor, ".4f"),
        ff(face, ".4f"),
        ff(fc.stack_floor_z, ".4f"),
        ff(fc.cap_face_z, ".4f")
    );
    rt.print(percent(
        "  cap face %.1f, %.1f mm over the stack's own floor — what stands on the core is placed off this, not off the box's top  OK",
        vec![face.into(), s.cap_face_over_floor.into()],
    )?)?;
    placed.at("foam-shell")?.i(0)?;
    let reading = m.k("co2")?;
    let mut values = vec![];
    for end in ["start", "end"] {
        let point = reading.k(end)?.list()?;
        values.extend(point.into_iter().take(2));
    }
    let reach_length = reading.k("length")?;
    let blocked = reading.k("blocked")?;
    let verdict = if blocked.f()? <= 1e-06 {
        "clear  OK".to_string()
    } else {
        percent("** BLOCKED by %.3f mm^3", vec![blocked.clone()])?
    };
    values.push(s.co2_inlet_xyz.i(2)?);
    values.push(reach_length);
    values.push(verdict.into());
    rt.print(percent(
        "  CO2 reach in: (%.2f, %.2f) .. (%.2f, %.2f) at z %.2f, %.1f mm straight — %s",
        values,
    )?)?;
    let passages = m.k("passages")?.list()?;
    for cname in core.cap_conduits.keys() {
        let reading = first(&passages, |row| is(row.k("name")?, cname), |row| Ok(row.clone()))?;
        let mut blocked: OMap<f64> = OMap::new();
        for row in reading.k("blocked")?.list()? {
            blocked.set(&row.k("name")?.str()?, row.k("volume")?.f()?);
        }
        if reading.k("bottom_open")?.truthy()? {
            rt.print(format!("  ** foam-cap-bottom is open on {cname}'s lower entry"))?;
        }
        for (name, volume) in blocked.iter() {
            if *volume > 1e-06 {
                rt.print(format!(
                    "  ** {name} blocks {cname}'s actual passage by {} mm^3",
                    ff(*volume, ".3f")
                ))?;
            }
        }
        let (mouth, _axis) = cap_conduit_mouth(rt, cname)?;
        ensure!(!blocked.is_empty(), "max() arg is an empty sequence");
        let verdict = if fmax(blocked.values().copied()) <= 1e-06 {
            "clear  OK"
        } else {
            "** BLOCKED"
        };
        rt.print(percent(
            "  cap conduit %-16s mouth (%+7.2f,%+7.2f,%+7.2f): %s",
            vec![
                cname.into(),
                mouth[0].into(),
                mouth[1].into(),
                mouth[2].into(),
                verdict.into(),
            ],
        )?)?;
    }
    let mut clear = true;
    let screw_paths = m.k("screw_paths")?.list()?;
    for name in ["foam-cap-lid-top", "foam-cap-bottom"] {
        placed.at(name)?.i(0)?;
        bounds(&m, name)?;
        for &[x, y] in &screws {
            let blocked = first(
                &screw_paths,
                |row| {
                    if !is(row.k("name")?, name)? {
                        return Ok(false);
                    }
                    let xy = row.k("xy")?.list()?;
                    Ok(xy.len() == 2 && xy[0].f()? == x && xy[1].f()? == y)
                },
                |row| row.k("blocked"),
            )?
            .f()?;
            if blocked > 1e-06 {
                clear = false;
                rt.print(percent(
                    "  ** screw path BLOCKED in %s at (%.1f, %.1f)",
                    vec![name.into(), x.into(), y.into()],
                )?)?;
            }
        }
    }
    rt.print(if clear {
        format!(
            "  screw paths: all {} clear through every cap + lid (top + bottom)  OK",
            b.attachment_xy_positions.len()
        )
    } else {
        "  ** SCREW PATHS BLOCKED **".to_string()
    })?;
    let names: Vec<&str> = placed.keys().collect();
    let clashes = m.k("clashes")?.list()?;
    let mut clash = false;
    for i in 0..names.len() {
        for j in i + 1..names.len() {
            placed.at(names[i])?.i(0)?;
            placed.at(names[j])?.i(0)?;
            let volume = first(
                &clashes,
                |row| Ok(is(row.k("a")?, names[i])? && is(row.k("b")?, names[j])?),
                |row| row.k("volume"),
            )?;
            if volume.f()? > 0.001 {
                clash = true;
                rt.print(percent(
                    "  ** SOLID clash %s / %s = %.2f mm^3",
                    vec![names[i].into(), names[j].into(), volume],
                )?)?;
            }
        }
    }
    rt.print(if !clash {
        "  no solid collisions"
    } else {
        "  ** CLASHES PRESENT **"
    })
}

/// `rust_main(output=None)`: cut the assembly, report it and its internal routes, and write
/// the presentation STEP.
pub fn rust_main(rt: &Runtime, output: Val) -> Result<Val> {
    let s = state(rt)?;
    let rust_part = rt.py("_rust_part")?;
    foam_numbers::state(rt)?;
    let output = if matches!(output, Val::None) {
        Val::Path(parent(&s.here))
    } else {
        rt.import_module("pathlib")?.a("Path")?.c(args![output])?
    };
    output.mk("mkdir", vec![], kw!["parents" => true, "exist_ok" => true])?;
    let numbers = foam_numbers::numbers(rt)?;
    let result = rust_part.m("cut", args!["cold-core", "foam-assembly", numbers, output])?;
    let mut casing = vec![];
    for row in result.k("bodies")?.iter()? {
        let name = row.k("name")?;
        let kept = matches!(&name, Val::Str(n) if s.colors.get(n).is_some() || n == "foam-shell");
        if kept {
            casing.push(row);
        }
    }
    let measurements = casing.first().context("IndexError: list index out of range")?.k("assembly_report")?;
    let mut extents = Dict::new();
    for row in &casing {
        extents.set(row.k("name")?, (row.k("min")?, row.k("max")?));
    }
    measurements.set(Val::Str("bounds".into()), extents.val())?;
    let mut placed = OMap::new();
    for row in &casing {
        placed.set(&row.k("name")?.str()?, (Val::None, Val::None).to_val());
    }
    report(rt, &placed, &measurements)?;
    let mut readings = vec![];
    for row in result.k("bodies")?.iter()? {
        if hsm_documents::interop::compare("in", Val::Str("route_report".into()), row.clone())?
            .truthy()?
        {
            readings.push(row.k("route_report")?);
        }
    }
    let routes_reading = readings.into_iter().next().context("StopIteration")?;
    let mut fitted = OMap::new();
    let route_rows = routes_reading.k("routes")?.list()?;
    for row in &route_rows {
        fitted.set(&row.k("name")?.str()?, (row.k("bend")?.f()?, Val::None));
    }
    let mut obstacles = OMap::new();
    let first_route = route_rows.first().context("IndexError: list index out of range")?;
    for row in first_route.k("blocked")?.list()? {
        obstacles.set(&row.k("name")?.str()?, Val::None);
    }
    internal_routes::report_routes(rt, &fitted, &obstacles, Some(&routes_reading))?;
    rt.sys_path_insert(0, &s.hw.join("cold-core-layout"))?;
    let finish = rt.import_module("_core_presentation")?.a("finish")?; // via namespace: _core_presentation
    let target = hsm_documents::interop::binary("truediv", output.clone(), "foam-assembly.step".into())?;
    finish.c(args![target, numbers.k("models")?])?; // via namespace: _core_presentation
    Ok(result)
}

/// `main(argv=None)`: read `--output` and run the assembly.
pub fn main_with(rt: &Runtime, argv: Val) -> Result<()> {
    let argparse = rt.py("argparse")?;
    let description = super::table::documentation(NAME).map_or(Val::None, Val::from);
    let parser = argparse.mk("ArgumentParser", vec![], kw!["description" => description])?;
    parser.mk(
        "add_argument",
        args!["--output"],
        kw![
            "type" => rt.import_module("pathlib")?.a("Path")?,
            "help" => "directory for generated assembly files",
        ],
    )?;
    let parsed = parser.m("parse_args", args![argv])?;
    rust_main(rt, parsed.a("output")?)?;
    Ok(())
}

fn station_val(p: [f64; 2]) -> Val {
    p.to_val()
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    let fc = foam_cap_parts::state(rt)?;
    ns.value("sys", s.sys.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", Val::Path(s.here.clone()));
    ns.value("_repo", Val::Path(s.repo.clone()));
    ns.value("_hw", Val::Path(s.hw.clone()));
    ns.value("_cold_core", Val::Path(s.cold_core.clone()));
    let interface = rt.import_module(core::NAME)?;
    for name in INTERFACE_NAMES {
        ns.value(name, interface.a(name)?);
    }
    ns.value("cap_face_z", fc.cap_face_z);
    ns.value("lid_total_height", fc.lid_total_height);
    ns.value("stack_floor_z", fc.stack_floor_z);
    ns.value("top_cap_height", fc.top_cap_height);
    ns.value("co2_inlet_xyz", s.co2_inlet_xyz.clone());
    ns.module(rt, "routes", internal_routes::NAME)?;
    ns.value("_routing", s.routing.clone());
    ns.value("_mat", s.mat.clone());
    ns.module(rt, "_above_mounts", mounts::NAME)?;
    ns.value("cap_face_over_floor", s.cap_face_over_floor);
    ns.value("SHELL_STEP", Val::Path(s.shell_step.clone()));
    ns.value("CAP_DIR", Val::Path(s.cap_dir.clone()));
    ns.value("RESERVOIR_DIR", Val::Path(s.reservoir_dir.clone()));
    let mut reservoirs = Dict::new();
    for (name, stem) in RESERVOIRS {
        reservoirs.set(name, stem);
    }
    ns.value("RESERVOIRS", reservoirs);
    ns.value("RESERVOIR_CAP_Z", s.reservoir_cap_z);
    ns.value("SHELL_COLOR", s.shell_color.clone());
    ns.value("COLORS", s.colors.to_val());
    let mut spools = Dict::new();
    for (name, key) in ROUTE_SPOOLS {
        spools.set(name, key);
    }
    ns.value("ROUTE_SPOOLS", spools);
    ns.value("ROUTE_COLORS", s.route_colors.to_val());
    ns.func(rt, "spin_xy", |_, c| {
        let p = c.req::<Val>(0, "p")?;
        Ok(Val::Tuple(vec![
            Num::from_val(&p.i(0)?)?.neg().to_val(),
            Num::from_val(&p.i(1)?)?.neg().to_val(),
        ]))
    });
    ns.func(rt, "cap_conduit_station", |rt, c| {
        Ok(station_val(cap_conduit_station(rt, &c.req::<String>(0, "name")?)?))
    });
    ns.func(rt, "cap_conduit_axis_out", |_, _| Ok(cap_conduit_axis_out().to_val()));
    ns.func(rt, "cap_conduit_mouth", |rt, c| {
        Ok(cap_conduit_mouth(rt, &c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "cap_anchor_station", |rt, c| {
        Ok(station_val(cap_anchor_station(rt, &c.req::<String>(0, "name")?)?))
    });
    ns.func(rt, "cap_side_anchor_station", |rt, c| {
        Ok(station_val(cap_side_anchor_station(rt, &c.req::<String>(0, "name")?)?))
    });
    ns.func(rt, "deck_mount_station", |rt, c| {
        Ok(Tuple(deck_mount_station(rt, &c.req::<String>(0, "name")?)?).to_val())
    });
    ns.func(rt, "_report", |rt, c| {
        let placed_val = c.req::<Val>(0, "placed")?;
        let measurements = c.req::<Val>(usize::MAX, "measurements")?;
        let mut placed = OMap::new();
        for (name, row) in placed_val.items()? {
            placed.set(&name.str()?, row);
        }
        report(rt, &placed, &measurements)?;
        Ok(Val::None)
    });
    ns.func(rt, "rust_main", |rt, c| {
        let output = c.opt::<Val>(0, "output", Val::None)?;
        rust_main(rt, output)
    });
    ns.func(rt, "main", |rt, c| {
        let argv = c.opt::<Val>(0, "argv", Val::None)?;
        main_with(rt, argv)?;
        Ok(Val::None)
    });
    Ok(())
}

/// The `__main__` blocks: start the part runner, then `main()`.
pub fn main(rt: &Runtime) -> Result<()> {
    state(rt)?;
    rt.py("_rust_part")?.m("start", vec![])?;
    main_with(rt, Val::None)
}
