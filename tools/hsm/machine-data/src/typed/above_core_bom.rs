//! Selected above-core fitting names, answered by the layout data recipes.
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::{Context, Result};
use hsm_documents::interop::Val;
use serde_json::json;

/// Converted: the hybrid development build runs this module, not its generated namespace.
pub const TYPED: bool = true;

/// The reservoir gate elbows and the valve port each one hosts.
pub fn reservoir_gate_elbow_hosts(rt: &Rt) -> Result<Vec<(String, Vec<String>)>> {
    let gates = rt.layout_data(json!({"op": "reservoir-gates"}))?;
    let gates = gates.as_object().context("reservoir gates")?;
    gates.iter().map(|(name, row)| Ok((name.clone(), py::json_strings(row)?))).collect()
}

fn names(rt: &Rt, op: &str) -> Result<Vec<String>> {
    let spec = py::plain(&rt.import("above_core")?.attr("specification")?.call(vec![], vec![])?)?;
    py::json_strings(&rt.layout_data(json!({"op": op, "spec": spec}))?)
}
pub fn stem_elbow_names(rt: &Rt) -> Result<Vec<String>> {
    names(rt, "stem-elbow-names")
}
pub fn union_elbow_names(rt: &Rt) -> Result<Vec<String>> {
    names(rt, "union-elbow-names")
}

fn strings(names: Vec<String>) -> Val {
    py::tuple(names.into_iter().map(Val::Str))
}
pub fn hosts_val(hosts: Vec<(String, Vec<String>)>) -> Val {
    py::dict(hosts.into_iter().map(|(name, row)| (name, strings(row))))
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::ABOVE_CORE_BOM))?;
    ns.set("layout", rt.import("above_core")?)?;
    ns.set("_data", rt.member("_layout_data", "data")?)?;
    ns.def(rt, "reservoir_gate_elbow_hosts", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(hosts_val(reservoir_gate_elbow_hosts(rt)?))
    })?;
    ns.def(rt, "stem_elbow_names", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(strings(stem_elbow_names(rt)?))
    })?;
    ns.def(rt, "core_stem_elbow_names", |_, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(Val::Tuple(vec![]))
    })?;
    ns.def(rt, "union_elbow_names", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(strings(union_elbow_names(rt)?))
    })?;
    ns.def(rt, "core_union_elbow_names", |_, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(Val::Tuple(vec![]))
    })?;
    Ok(())
}
