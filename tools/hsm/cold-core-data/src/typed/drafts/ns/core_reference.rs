//! `core_reference`: the cold core's model references and its scalar source-frame
//! installation datums.

use super::cold_core_interface as core;
use super::foam_assembly;
use super::foam_cap_parts;
use super::internal_routes;
use super::*;

pub const NAME: &str = "core_reference";

pub struct State {
    sys: Val,
    root: PathBuf,
    cold: PathBuf,
    path: PathBuf,
    core_model: PathBuf,
    casing_model: PathBuf,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let sys = rt.py("sys")?;
        let root = ancestor_where(&resolve(&rt.file(NAME)), |p| {
            p.join("hardware/scripts/_assembly_model.py").is_file()
        })?;
        let cold = root.join("hardware/printed-parts/cold-core");
        let paths = [
            root.join("hardware/scripts"),
            cold.clone(),
            cold.join("foam-assembly"),
            root.join("hardware/cold-core-layout"),
        ];
        for path in &paths {
            let listed = hsm_documents::interop::compare(
                "not_in",
                Val::Str(ps(path)),
                sys.a("path")?,
            )?;
            if listed.truthy()? {
                rt.sys_path_insert(0, path)?;
            }
        }
        let [_, _, _, path] = paths;
        let core_model = root.join("hardware/cold-core-layout/cold-core-assembly.scene.npz");
        let casing_model = cold.join("foam-assembly/foam-assembly.step.npz");
        Ok(Self {
            sys,
            root,
            cold,
            path,
            core_model,
            casing_model,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `datums()`: where the casing seats and what it presents, in its source frame.
pub fn datums(rt: &Runtime) -> Result<Val> {
    rt.py("_rust_part")?.m("start", vec![])?;
    let core = core::state(rt)?;
    let b = &core.base;
    let copper = rt.import_module("_copper_ports")?; // via namespace: _copper_ports
    let casing = foam_assembly::state(rt)?;
    let fc = foam_cap_parts::state(rt)?;
    let routes = internal_routes::state(rt)?;
    let mut conduit_mouths = Dict::new();
    let mut lid_anchors = Dict::new();
    let mut side_anchors = Dict::new();
    let mut deck_mounts = Dict::new();
    let copper_mouths = copper.m("stations", vec![])?; // via namespace: _copper_ports
    let prv_vent_tip = *routes
        .routes
        .at("prv-vent")?
        .last()
        .context("IndexError: list index out of range")?;
    for name in core.cap_conduits.keys() {
        conduit_mouths.set(name, foam_assembly::cap_conduit_mouth(rt, name)?);
    }
    for name in core.cap_anchors.keys() {
        lid_anchors.set(name, foam_assembly::cap_anchor_station(rt, name)?);
    }
    for name in core.cap_side_anchors.keys() {
        side_anchors.set(name, foam_assembly::cap_side_anchor_station(rt, name)?);
    }
    for name in core.deck_mounts.keys() {
        deck_mounts.set(name, Tuple(foam_assembly::deck_mount_station(rt, name)?));
    }
    Ok(dict! {
        "front_wall_x" => b.front_wall_x,
        "stack_floor_z" => fc.stack_floor_z,
        "cap_face_z" => fc.cap_face_z,
        "cap_face_over_floor" => casing.cap_face_over_floor,
        "casing_foil_allowance" => b.casing_foil_allowance,
        "seat" => (b.front_wall_x, 0.0, fc.stack_floor_z),
        "copper_mouths" => copper_mouths,
        "prv_vent_tip" => prv_vent_tip,
        "conduit_mouths" => conduit_mouths,
        "lid_anchor_xy" => lid_anchors,
        "side_anchor_xy" => side_anchors,
        "deck_mount_xy" => deck_mounts,
    })
}

/// `range(n)`, as the runtime builds it.
fn range(n: usize) -> Result<Val> {
    hsm_documents::interop::builtin("range")
        .context("range")?
        .c(args![n])
}

/// `casing_bounds(model=CASING_MODEL)`: the measured casing's overall box and its bodies.
pub fn casing_bounds(rt: &Runtime, model: Val) -> Result<Val> {
    let assembly_model = rt.py("_assembly_model")?;
    let model = rt.import_module("pathlib")?.a("Path")?.c(args![model])?;
    let entries = assembly_model.m("identity", args![model])?;
    let reference = assembly_model.mk(
        "instance",
        args![model],
        kw!["indices" => range(entries.len()?)?],
    )?;
    let bodies = assembly_model
        .m("measure", args![Val::list(vec![reference]), Val::Tuple(vec![])])?
        .k("bodies")?;
    let rows = bodies.list()?;
    let min = hsm_documents::interop::builtin("min").context("min")?;
    let max = hsm_documents::interop::builtin("max").context("max")?;
    let mut low = vec![];
    for axis in 0..3 {
        let values = rows
            .iter()
            .map(|row| row.k("min")?.i(axis))
            .collect::<Result<Vec<_>>>()?;
        low.push(min.c(vec![Val::list(values)])?);
    }
    let mut high = vec![];
    for axis in 0..3 {
        let values = rows
            .iter()
            .map(|row| row.k("max")?.i(axis))
            .collect::<Result<Vec<_>>>()?;
        high.push(max.c(vec![Val::list(values)])?);
    }
    Ok(dict! {"min" => low, "max" => high, "bodies" => bodies})
}

/// `instance(transform, *, model=CORE_MODEL, prefix='cold-core/')`: the cold core placed by
/// `transform`, with its identities and transparency.
pub fn instance(rt: &Runtime, transform: Val, model: Val, prefix: Val) -> Result<Val> {
    let assembly_model = rt.py("_assembly_model")?;
    let model = rt.import_module("pathlib")?.a("Path")?.c(args![model])?;
    let identities = assembly_model.m("identity", args![model])?;
    let alpha = assembly_model
        .m("document", args![model])?
        .m("get", args!["alpha_by_name", Val::dict(vec![])])?;
    let reference = assembly_model.mk(
        "instance",
        args![model],
        kw![
            "indices" => range(identities.len()?)?,
            "transform" => transform,
            "prefix" => prefix,
        ],
    )?;
    Ok(dict! {"reference" => reference, "identities" => identities, "alpha_by_name" => alpha})
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("sys", s.sys.clone());
    ns.value("ROOT", Val::Path(s.root.clone()));
    ns.value("COLD", Val::Path(s.cold.clone()));
    ns.value("path", Val::Path(s.path.clone()));
    ns.value("CORE_MODEL", Val::Path(s.core_model.clone()));
    ns.value("CASING_MODEL", Val::Path(s.casing_model.clone()));
    ns.func(rt, "datums", |rt, _| datums(rt));
    let casing_model = s.casing_model.clone();
    ns.func(rt, "casing_bounds", move |rt, c| {
        let model = c.opt::<Val>(0, "model", Val::Path(casing_model.clone()))?;
        casing_bounds(rt, model)
    });
    let core_model = s.core_model.clone();
    ns.func(rt, "instance", move |rt, c| {
        let transform = c.req::<Val>(0, "transform")?;
        let model = c.kw::<Val>("model", Val::Path(core_model.clone()))?;
        let prefix = c.kw::<Val>("prefix", Val::Str("cold-core/".into()))?;
        instance(rt, transform, model, prefix)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
