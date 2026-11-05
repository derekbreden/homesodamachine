//! `_cold_core_style`: the cold core's exact viewer colours, without building its geometry.

use super::*;

pub const NAME: &str = "_cold_core_style";

/// `ROUTE_SPOOLS`: the tubing spool each cold-core route is cut from.
pub const ROUTE_SPOOLS: [(&str, &str); 8] = [
    ("water-in", "white"),
    ("carb-water-out", "blue"),
    ("co2-in", "red"),
    ("prv-vent", "black"),
    ("reservoir-a", "black"),
    ("reservoir-a-fill", "black"),
    ("reservoir-b", "black"),
    ("reservoir-b-fill", "black"),
];

pub struct State {
    here: PathBuf,
    hw: PathBuf,
    mat: Val,
    routing: Val,
    /// `FOAM_COLORS`, in the dict's order.
    foam_colors: Vec<(&'static str, Val)>,
    /// `ROUTE_COLORS`: each route's spool colour, in `ROUTE_SPOOLS` order.
    route_colors: Vec<(&'static str, Val)>,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let here = resolve(&rt.file(NAME));
        let hw = ancestor(&here, "hardware")?;
        let scripts = hw.join("scripts");
        if !rt.pya("sys", "path")?.contains(&Val::Str(ps(&scripts)))? {
            rt.sys_path_insert(0, &scripts)?;
        }
        let mat = rt.py("_materials")?;
        let routing = rt.py("_routing")?;
        let foam_colors = vec![
            ("foam-shell", mat.a("C_FOAM_SHELL")?),
            ("foam-cap-lid-top", mat.a("C_CAP_LID_TOP")?),
            ("foam-cap-bottom", mat.a("C_CAP_BOTTOM")?),
        ];
        let mut route_colors = vec![];
        for (name, spool) in ROUTE_SPOOLS {
            route_colors.push((name, routing.m("color", args![spool])?));
        }
        Ok(Self {
            here,
            hw,
            mat,
            routing,
            foam_colors,
            route_colors,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `colour_for(name)`: the material colour a cold-core body draws in.
pub fn colour_for(rt: &Runtime, name: &str) -> Result<Val> {
    let s = state(rt)?;
    let material = |constant: &str| s.mat.a(constant);
    if name == "digiten-flow" {
        return material("C_DIGITEN");
    }
    if name == "reservoir-b-fill-guide" {
        return material("M_PETGF_BLACK");
    }
    if name.starts_with("cap-clamp-") {
        return material("M_DONOR_BLACK");
    }
    if name == "soda-bend-holder" {
        return material("M_PETGF_BLACK");
    }
    if name == "soda-continuous-insulation" {
        return material("M_NITRILE_BLACK");
    }
    if name.starts_with("tube-soda-core-") {
        return s.routing.m("color", args!["blue"]);
    }
    if let Some(route) = name.strip_prefix("line-") {
        return match s.route_colors.iter().find(|(key, _)| *key == route) {
            Some((_, colour)) => Ok(colour.clone()),
            None => bail!(
                "{}: no cold-core route colour",
                Val::Str(name.into()).repr()?
            ),
        };
    }
    if let Some((_, colour)) = s.foam_colors.iter().find(|(key, _)| *key == name) {
        return Ok(colour.clone());
    }
    if name == "reed-bridge" {
        return material("M_PETG_BLACK");
    }
    if name == "prv-shroud" {
        return material("C_SHROUD");
    }
    if name == "prv-sv125" {
        return material("M_BRASS");
    }
    if name.starts_with("endcap") {
        return material("M_STAINLESS");
    }
    if ["carbonator-elbow-co2-in", "carbonator-elbow-carb-water-out"].contains(&name) {
        return material("M_NEOFIT_ACETAL");
    }
    if name.starts_with("carbonator-elbow") {
        return material("M_STAINLESS");
    }
    if name.starts_with("collet-") {
        return material("M_JG_BLACK_PP");
    }
    if name.ends_with("-gasket") {
        return material("C_SILICONE");
    }
    if name.ends_with("-cap") {
        return material("C_RES_CAP");
    }
    if name.starts_with("reservoir-grip-") {
        return material("M_TPU_BLACK");
    }
    if name.starts_with("tube-reservoir-air-") {
        return s.routing.m("color", args!["drain-white"]);
    }
    if name.starts_with("reservoir") {
        return material("C_RESERVOIR");
    }
    if name.starts_with("evap-") {
        return material("M_COPPER");
    }
    if name.starts_with("float-rod") || name.starts_with("float-stop") {
        return material("M_STAINLESS");
    }
    if name.starts_with("float-") {
        return material("M_ASA_AERO_WHITE");
    }
    if name.starts_with("reed-") {
        return material("C_REED");
    }
    if name.starts_with("probe-") {
        return material("M_EPOXY_BLACK");
    }
    material("M_STAINLESS")
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", s.here.clone());
    ns.value("_hw", s.hw.clone());
    ns.value("_mat", s.mat.clone());
    ns.value("_routing", s.routing.clone());
    let mut foam_colors = Dict::new();
    for (name, colour) in &s.foam_colors {
        foam_colors.set(*name, colour.clone());
    }
    ns.value("FOAM_COLORS", foam_colors.val());
    let mut spools = Dict::new();
    for (name, spool) in ROUTE_SPOOLS {
        spools.set(name, spool);
    }
    ns.value("ROUTE_SPOOLS", spools.val());
    let mut route_colors = Dict::new();
    for (name, colour) in &s.route_colors {
        route_colors.set(*name, colour.clone());
    }
    ns.value("ROUTE_COLORS", route_colors.val());
    ns.func(rt, "colour_for", |rt, c| {
        colour_for(rt, &c.req::<String>(0, "name")?)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
