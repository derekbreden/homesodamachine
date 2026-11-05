//! Requests for the installed warm-tube and insulation geometry the machine program builds.
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::Result;
use hsm_documents::interop::{self, Val};
use py::s;
use std::path::PathBuf;

/// Converted: the hybrid development build runs this module, not its generated namespace.
pub const TYPED: bool = true;

/// The machine program's route request: authored route order and world-placed references.
pub fn numbers(rt: &Rt, routes: &Val, insulation: &Val, components: &Val, name: &Val) -> Result<Val> {
    let deepcopy = rt.member("copy", "deepcopy")?;
    let components = if components.truthy()? { components.clone() } else { Val::dict(vec![]) };
    Ok(py::dict([
        ("name", name.clone()),
        ("routes", py::call(&deepcopy, vec![routes.clone()])?),
        ("route_order", Val::list(routes.iter()?)),
        ("insulation", py::call(&deepcopy, vec![insulation.clone()])?),
        ("components", py::call(&deepcopy, vec![components])?),
    ]))
}

/// The holder and soft-neighbor groups selected from the equipment's fine model.
pub fn equipment_inputs(request: &Val, model: &Val, groups: &Val) -> Result<Val> {
    let mut insulation = py::method(request, "get", vec![s("insulation")])?;
    if matches!(insulation, Val::None) {
        insulation = Val::None;
        for row in py::dget(request, "items", Val::Tuple(vec![]))?.iter()? {
            if interop::eq(&py::method(&row, "get", vec![s("op")])?, &s("insulation"))? {
                insulation = row;
                break;
            }
        }
    }
    let components = Val::dict(vec![]);
    if !matches!(insulation, Val::None) {
        let mut names = vec![s("soda-bend-holder")];
        names.extend(py::at(&insulation, "neighbors")?.iter()?);
        let model = s(py::path_str(&py::path(model)?));
        for name in names {
            let indices = Val::list(groups.get(name.clone())?.iter()?);
            components.set(name, py::dict([("model", model.clone()), ("indices", indices)]))?;
        }
    }
    Ok(py::dict([("routes", py::at(request, "routes")?), ("insulation", insulation), ("components", components)]))
}

/// Write paired fine geometry and ordered named-body metadata through the machine program.
pub fn build(rt: &Rt, output: &Val, routes: &Val, insulation: &Val, components: &Val, name: &Val) -> Result<Val> {
    let rust_part = rt.import("_rust_part")?;
    let output: PathBuf = py::resolve(&py::path(output)?)?;
    py::mkdirs(&output)?;
    let request = numbers(rt, routes, insulation, components, name)?;
    py::call(&rust_part.attr("cut")?, vec![s("machine"), s("machine-routes"), request, Val::Path(output.clone())])?;
    let name = interop::format(name, "")?;
    let result = py::json_loads(&py::read_text(&output.join(format!("{name}.json")))?)?;
    let model = s(py::path_str(&output.join(format!("{name}.step.npz"))));
    for instance in py::at(&result, "instances")?.iter()? {
        instance.set(s("model"), model.clone())?;
    }
    result.set(s("model"), model)?;
    Ok(result)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::MACHINE_ROUTES))?;
    ns.set("deepcopy", rt.member("copy", "deepcopy")?)?;
    ns.set("json", rt.import("json")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.def(rt, "numbers", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["routes"], &["insulation", "components", "name"])?;
        let routes = a.req("routes")?;
        let insulation = a.opt("insulation").unwrap_or(Val::None);
        let components = a.opt("components").unwrap_or(Val::None);
        let name = a.opt("name").unwrap_or_else(|| s("machine-routes"));
        numbers(rt, &routes, &insulation, &components, &name)
    })?;
    ns.def(rt, "equipment_inputs", |_, args, kw| {
        let mut a = py::bind(args, kw, &["request", "model", "groups"], &[])?;
        equipment_inputs(&a.req("request")?, &a.req("model")?, &a.req("groups")?)
    })?;
    ns.def(rt, "build", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["output", "routes"], &["insulation", "components", "name"])?;
        let (output, routes) = (a.req("output")?, a.req("routes")?);
        let insulation = a.opt("insulation").unwrap_or(Val::None);
        let components = a.opt("components").unwrap_or(Val::None);
        let name = a.opt("name").unwrap_or_else(|| s("machine-routes"));
        build(rt, &output, &routes, &insulation, &components, &name)
    })?;
    Ok(())
}
