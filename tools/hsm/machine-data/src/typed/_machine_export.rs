//! File-reference model and presentation export through the machine program.
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::Result;
use hsm_documents::interop::{self, Val};
use py::s;
use std::path::{Path, PathBuf};

/// Converted: the hybrid development build runs this module, not its generated namespace.
pub const TYPED: bool = true;

fn run(rt: &Rt, spec: Val, output: &Path) -> Result<Val> {
    let rust_part = rt.import("_rust_part")?;
    let output: PathBuf = py::resolve(output)?;
    py::mkdirs(&output)?;
    let op = py::method(&spec, "get", vec![s("op"), s("physical")])?;
    let numbers_name = interop::binary("add", s("machine-export-"), op)?;
    let result = py::call_kw(
        &rust_part.attr("cut")?,
        vec![s("machine"), s("machine-export"), py::dict([("spec", spec)]), Val::Path(output)],
        vec![("numbers_name", numbers_name)],
    )?;
    let rows = py::method(&result, "get", vec![s("results"), Val::Tuple(vec![])])?;
    if rows.truthy()? { rows.get(Val::Int(-1)) } else { Ok(result) }
}

fn resolved_str(value: &Val) -> Result<Val> {
    Ok(s(py::path_str(&py::resolve(&py::path(value)?)?)))
}

/// Physical STEP, exact fine archive and its paired drawing payload.
pub fn export(rt: &Rt, spec: &Val, output: &Val) -> Result<Val> {
    run(rt, py::merged(spec, [("op", s("physical"))])?, &py::path(output)?)
}

/// The named machine scene from physical and foam model references.
pub fn scene(rt: &Rt, model: &Val, target: &Val, aliases: Val, envelope: &Val, document: Val) -> Result<Val> {
    let target = py::resolve(&py::path(target)?)?;
    let envelope = py::dict_of(envelope)?;
    if !envelope.contains(&s("path"))? && envelope.contains(&s("model"))? {
        envelope.set(s("path"), py::at(&envelope, "model")?)?;
    }
    let spec = py::dict([
        ("op", s("scene")),
        ("model", resolved_str(model)?),
        ("file", s(py::path_str(&target))),
        ("aliases", aliases),
        ("envelope", envelope),
        ("document", document),
    ]);
    run(rt, spec, target.parent().unwrap_or(&target))
}

/// Replace explicit named drawing surfaces, retaining the target physical geometry.
pub fn graft(rt: &Rt, target_payload: &Val, skins: &Val, model: &Val) -> Result<Val> {
    let target = py::resolve(&py::path(target_payload)?)?;
    let spec = py::dict([
        ("op", s("graft")),
        ("target_payload", s(py::path_str(&target))),
        ("skins", Val::list(skins.iter()?)),
    ]);
    if !matches!(model, Val::None) {
        spec.set(s("model"), resolved_str(model)?)?;
    }
    run(rt, spec, target.parent().unwrap_or(&target))
}

/// Scene GLBs from existing mesh buffers and explicit body membership.
pub fn views(rt: &Rt, spec: &Val, output: &Val) -> Result<Val> {
    run(rt, py::merged(spec, [("op", s("views"))])?, &py::path(output)?)
}

/// Append generated wiring while retaining all physical STEP and payload records.
pub fn append_wiring(rt: &Rt, host_step: &Val, wire_step: &Val, wire_model: &Val) -> Result<Val> {
    let host = py::resolve(&py::path(host_step)?)?;
    let spec = py::dict([("op", s("append")), ("host_step", s(py::path_str(&host))), ("wire_step", resolved_str(wire_step)?)]);
    if !matches!(wire_model, Val::None) {
        spec.set(s("wire_model"), resolved_str(wire_model)?)?;
    }
    run(rt, spec, host.parent().unwrap_or(&host))
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::MACHINE_EXPORT))?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.def(rt, "_run", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["spec", "output"], &[])?;
        let spec = a.req("spec")?;
        run(rt, spec, &py::path(&a.req("output")?)?)
    })?;
    ns.def(rt, "export", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["spec", "output"], &[])?;
        export(rt, &a.req("spec")?, &a.req("output")?)
    })?;
    ns.def(rt, "scene", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["model", "target"], &["aliases", "envelope", "document"])?;
        let (model, target) = (a.req("model")?, a.req("target")?);
        let (aliases, envelope, document) = (a.req("aliases")?, a.req("envelope")?, a.req("document")?);
        scene(rt, &model, &target, aliases, &envelope, document)
    })?;
    ns.def(rt, "graft", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["target_payload", "skins"], &["model"])?;
        let (target, skins) = (a.req("target_payload")?, a.req("skins")?);
        graft(rt, &target, &skins, &a.opt("model").unwrap_or(Val::None))
    })?;
    ns.def(rt, "views", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["spec", "output"], &[])?;
        views(rt, &a.req("spec")?, &a.req("output")?)
    })?;
    ns.def(rt, "append_wiring", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["host_step", "wire_step"], &["wire_model"])?;
        let (host, wire) = (a.req("host_step")?, a.req("wire_step")?);
        append_wiring(rt, &host, &wire, &a.opt("wire_model").unwrap_or(Val::None))
    })?;
    Ok(())
}
