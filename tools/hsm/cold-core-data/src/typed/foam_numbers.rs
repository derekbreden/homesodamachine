//! `foam_numbers`: the casing's source-frame placements and the internal routes' probes, as
//! the Rust assembly recipe reads them.

use super::above_core_mounts as mounts;
use super::cold_core_interface as core;
use super::foam_assembly;
use super::foam_cap_parts;
use super::internal_routes;
use super::*;

pub const NAME: &str = "foam_numbers";

pub struct State {
    sys: Val,
    root: PathBuf,
    cold: PathBuf,
    path: PathBuf,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let sys = rt.py("sys")?;
        let root = ancestor_where(&resolve(&rt.file(NAME)), |p| {
            p.join("hardware/scripts/_rust_part.py").is_file()
        })?;
        let cold = root.join("hardware/printed-parts/cold-core");
        let paths = [
            root.join("hardware/scripts"),
            cold.clone(),
            root.join("hardware/printed-parts/cadlib"),
        ];
        for path in &paths {
            rt.sys_path_insert(0, path)?;
        }
        let [_, _, path] = paths;
        Ok(Self {
            sys,
            root,
            cold,
            path,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// One placed casing piece in `stack_numbers()`.
fn piece(rt: &Runtime, linear: &Val, name: &str, folder: &str, color: &Val, rotation: f64, z: f64) -> Result<Val> {
    let s = state(rt)?;
    let model = format!("hardware/printed-parts/cold-core/{folder}/{name}.step.npz");
    rt.note_read(&s.root.join(&model))?;
    Ok(dict! {
        "name" => name,
        "model" => model,
        "color" => Val::list(linear.c(args![color])?.iter()?),
        "rotation_z_degrees" => rotation,
        "translation" => vec![0.0, 0.0, z],
    })
}

/// `stack_numbers()`: the three casing pieces in the assembly's source frame.
pub fn stack_numbers(rt: &Runtime) -> Result<Dict> {
    let fc = foam_cap_parts::state(rt)?;
    let mat = rt.py("_materials")?;
    let linear = mat.a("linear")?;
    let shell = mat.a("C_FOAM_SHELL")?;
    let lid_top = mat.a("C_CAP_LID_TOP")?;
    let bottom = mat.a("C_CAP_BOTTOM")?;
    let models = vec![
        piece(rt, &linear, "foam-shell", "foam-shell", &shell, 0.0, 0.0)?,
        piece(
            rt,
            &linear,
            "foam-cap-lid-top",
            "foam-cap",
            &lid_top,
            180.0,
            fc.cap_face_z - fc.lid_total_height,
        )?,
        piece(rt, &linear, "foam-cap-bottom", "foam-cap", &bottom, 0.0, fc.stack_floor_z)?,
    ];
    Ok(Dict::new().with("models", models).with(
        "document",
        dict! {"frame" => "foam assembly source", "schema" => "hsm-foam-assembly-1"},
    ))
}

fn points_val(points: &[[f64; 3]]) -> Val {
    Val::list(points.iter().map(ToVal::to_val).collect())
}

/// `numbers()`: the stack, the reservoirs as obstacles, the carbonator envelope, every
/// internal route and the report's probes.
pub fn numbers(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let source = foam_assembly::state(rt)?;
    let linear = rt.pya("_materials", "linear")?;
    let deflection_ratio = rt.pya("_payload_rules", "LINEAR_DEFLECTION_RATIO")?;
    let route = internal_routes::state(rt)?;
    let core = core::state(rt)?;
    let b = &core.base;
    let fc = foam_cap_parts::state(rt)?;
    let mut probes = vec![];
    for name in core.cap_conduits.keys() {
        let radius = if name == "reservoir-b-fill" {
            route.line_radius
        } else {
            core.cap_conduit_bore_radius - 0.3
        };
        let mut probe = Dict::new();
        probe.set("name", name);
        probe.set("radius", radius);
        if core.cap_cable_guides.iter().any(|g| g == name) {
            let (points, bend) = mounts::cable_guide_points(rt, name)?;
            let mut shell = vec![];
            for p in &points {
                shell.push(internal_routes::world_point_in_shell(rt, &p.to_val())?);
            }
            probe.set("kind", "route");
            probe.set("points", shell);
            probe.set("bend", bend);
        } else if core.cap_passive_guides.iter().any(|g| g == name)
            || ["water-in", "carb-water-out", "reservoir-b-fill"].contains(&name)
        {
            probe.set("kind", "route");
            probe.set("points", points_val(route.routes.at(name)?));
            probe.set("bend", route.route_bend_radius_val.clone());
        } else {
            let [x, y] = foam_assembly::cap_conduit_station(rt, name)?;
            probe.set("kind", "cylinder");
            probe.set("at", (x, y, b.foam_shell_outer_height - 1.0));
            probe.set("height", fc.cap_face_z - b.foam_shell_outer_height + 2.0);
        }
        probe.set(
            "lower_xy",
            foam_assembly::spin_xy(*core.cap_conduit_floor_xy.at(name)?),
        );
        probe.set("mouth", foam_assembly::cap_conduit_mouth(rt, name)?.0);
        probes.push(probe.val());
    }
    let mut obstacles = vec![];
    for (name, stem) in foam_assembly::RESERVOIRS {
        let cap = stem.replace("reservoir", "reservoir-cap");
        for (label, item, z) in [
            (name.to_string(), stem.to_string(), Num::F(0.0)),
            (format!("{name}'s cap"), cap, source.reservoir_cap_z),
        ] {
            let model = format!("hardware/printed-parts/cold-core/reservoir/{item}.step.npz");
            rt.note_read(&s.root.join(&model))?;
            obstacles.push(dict! {
                "name" => label,
                "model" => model,
                "translation" => (0.0, 0.0, z),
            });
        }
    }
    let mut d = stack_numbers(rt)?;
    d.set("obstacles", obstacles);
    d.set(
        "envelope",
        dict! {
            "tank_radius" => route.carbonator_outer_radius.clone(),
            "tank_z" => route.carbonator_envelope_z_range,
            "coil_radius" => b.carbonator_coil_envelope_radius,
            "coil_z" => (
                b.evap_tail_low_z - route.lldpe_tube_od / 2.0,
                b.evap_tail_high_z + route.lldpe_tube_od / 2.0,
            ),
        },
    );
    let mut names: Vec<&str> = route.routes.keys().collect();
    names.sort();
    let mut routes = vec![];
    for name in names {
        routes.push(dict! {
            "name" => name,
            "points" => points_val(route.routes.at(name)?),
            "color" => linear.c(args![source.route_colors.at(name)?])?,
        });
    }
    d.set("routes", routes);
    let vars = hsm_documents::interop::builtin("vars").context("vars")?;
    d.set(
        "routing",
        dict! {
            "stock_bend" => route.route_bend_radius_val.clone(),
            "radius" => route.line_radius,
            "floor" => route.bend_floor,
            "ladder" => Tuple(route.bend_ladder.clone()),
            "touch_volume" => route.touch_volume,
            "stock" => vars.c(args![route.route_stock])?,
            "prv_flank_y" => route.prv_vent_flank_y,
        },
    );
    d.set(
        "report",
        dict! {
            "floor" => fc.stack_floor_z,
            "face" => fc.cap_face_z,
            "lid_height" => fc.lid_total_height,
            "probes" => probes,
            "co2_points" => points_val(route.routes.at("co2-in")?),
            "co2_radius" => b.co2_inlet_tube_radius - 0.3,
            "co2_height" => source.co2_inlet_xyz.i(2)?,
            "lower_probe_radius" => core.cap_conduit_bore_radius - 0.3,
            "screw_xy" => b.attachment_xy_positions.clone(),
            "screw_probe_radius" => b.screw_clearance_radius - 0.3,
        },
    );
    d.set(
        "presentation",
        dict! {"deflection_ratio" => deflection_ratio, "simplification_fraction" => 0.5},
    );
    Ok(d.val())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("sys", s.sys.clone());
    ns.value("ROOT", Val::Path(s.root.clone()));
    ns.value("COLD", Val::Path(s.cold.clone()));
    ns.value("path", Val::Path(s.path.clone()));
    ns.func(rt, "stack_numbers", |rt, _| Ok(stack_numbers(rt)?.val()));
    ns.func(rt, "numbers", |rt, _| numbers(rt));
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
