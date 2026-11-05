//! Doc-sync driver for hardware/printed-parts/enclosure/nameplate/README.md.
//!
//! Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/_nameplate_dimensions.py
//!
//! Typed state: the checkout paths this module finds at import, and the printing plan
//! (`_dimensions()['plan']`) as the JSON `_read` sends.
use super::_nameplate_interface::{read, update};
use super::_nameplate_wing_interface::parent;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_nameplate_dimensions";

pub struct State {
    here: PathBuf,
    root: PathBuf,
    portal_host: String,
    plan: Value,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = parent(&py::resolve(&py::path(&ns.get("__file__")?)?)?);
    ns.set("_here", Val::Path(here.clone()))?;
    let root = here.ancestors().skip(1).find(|p| p.join("tools").join("docgen").is_dir())
        .context("StopIteration")?.to_owned();
    ns.set("_root", Val::Path(root.clone()))?;
    py::sys_path_insert(rt, &py::path_str(&root.join("tools")))?;
    ns.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    py::sys_path_insert(rt, &py::path_str(&root.join("hardware/printed-parts/enclosure/enclosure")))?;
    let dimensions = rt.member("_enclosure_data", "dimensions")?;
    ns.set("_dimensions", dimensions.clone())?;
    ns.set("_read", rt.member("_enclosure_data", "read")?)?;
    // globals().update(_dimensions()['plan'])
    let plan = py::at(&py::snapshot(&py::call(&dimensions, vec![])?)?, "plan")?;
    update(ns, &plan)?;
    let portal_host = py::at(&plan, "portal_host")?.str()?;
    rt.keep(MODULE, State { here, root, portal_host, plan: py::plain(&plan)? });

    for (name, field) in [("serial_of", "serial"), ("unit_url", "url"), ("unit_url_plain", "plain")] {
        ns.def(rt, name, move |rt, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["unit"], &[])?;
            let unit = b.req("unit")?;
            Ok(Val::Str(unit_field(rt, &unit, field)?))
        })?;
    }
    ns.def(rt, "main", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        main(rt)?;
        Ok(Val::None)
    })?;
    Ok(())
}

/// One field of `_read('nameplate-unit', unit=unit, portal_host=portal_host)`.
fn unit_field(rt: &Rt, unit: &Val, field: &str) -> Result<String> {
    let state = state(rt)?;
    let unit = read(rt, "nameplate-unit", json!({"unit": py::plain(unit)?, "portal_host": state.portal_host}))?;
    unit.get(field).and_then(Value::as_str).map(str::to_owned).with_context(|| format!("nameplate unit {field}"))
}

/// The four-digit identifier encoded in the QR and used by the unit log.
pub fn serial_of(rt: &Rt, unit: &Val) -> Result<String> {
    unit_field(rt, unit, "serial")
}

/// Uppercase scheme/host keep the complete URL in QR alphanumeric mode.
pub fn unit_url(rt: &Rt, unit: &Val) -> Result<String> {
    unit_field(rt, unit, "url")
}

/// The full-domain address for written instructions; the plate shows only a QR.
pub fn unit_url_plain(rt: &Rt, unit: &Val) -> Result<String> {
    unit_field(rt, unit, "plain")
}

/// A `_read` result mapping as docgen's `substitute_md` reads its `variables`.
pub(crate) fn variables(value: Value) -> Result<BTreeMap<String, String>> {
    let rows = py::from_json(value)?;
    let mut values = BTreeMap::new();
    for key in rows.iter()? {
        values.insert(key.str()?, rows.get(key)?.str()?);
    }
    Ok(values)
}

/// `docgen.substitute_md(path, variables=values)` as this module calls it.
fn substitute(rt: &Rt, path: &Path, values: &BTreeMap<String, String>) -> Result<()> {
    rt.substitute(hsm_documents::Kind::Markdown, path, values, Some(MODULE))?;
    Ok(())
}

pub fn main(rt: &Rt) -> Result<()> {
    let state = state(rt)?;
    let values = variables(read(rt, "plan-variables", json!({"plan": state.plan}))?)?;
    substitute(rt, &state.here.join("README.md"), &values)?;
    rt.print("-> README.md".into())?;
    substitute(rt, &state.root.join("future").join("unit-links.md"), &values)?;
    rt.print("-> future/unit-links.md".into())?;
    Ok(())
}

pub fn main_block(rt: &Rt) -> Result<()> {
    main(rt)
}
