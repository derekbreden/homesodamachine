//! Accepted face-up display bezel with coplanar horizontal retaining wings.
//!
//! The visible face is local Z=0. The back and both wings share one flat bed plane.
//! The TPU ring separates the bezel from the glass.
//!
//! The cover's recipe and README figures are `cover-recipe` and `cover-variables` (`main.rs`),
//! answered in this process from `_enclosure_data.dimensions()['display']`. The body is
//! `_display_wing_interface.cover()`. CadQuery, `_rust_part` and `_materials` stay providers.
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use serde_json::json;
use std::collections::BTreeMap;
use std::path::PathBuf;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "display_cover";

pub struct State {
    pub cq: Val,
    linear: Val,
    petgf_black: Val,
    here: PathBuf,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// `len(sys.argv) > 1 and sys.argv[1] == 'selftest'`.
fn selftest_asked(sys: &Val) -> Result<bool> {
    let argv = sys.attr("argv")?;
    Ok(argv.len()? > 1 && matches!(py::item(&argv, Val::Int(1))?, Val::Str(word) if word == "selftest"))
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    let sys = rt.import("sys")?;
    ns.set("sys", sys.clone())?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    ns.set("_here", Val::Path(here.clone()))?;
    let hw = here.ancestors().skip(1).find(|p| p.file_name().is_some_and(|n| n == "hardware"))
        .context("StopIteration")?.to_path_buf();
    ns.set("_hw", Val::Path(hw.clone()))?;
    let tools = hw.parent().context("_hw.parent")?.join("tools");
    for directory in [hw.join("scripts"), hw.join("printed-parts/enclosure/enclosure"), tools] {
        ns.set("directory", Val::Path(directory.clone()))?;
        py::sys_path_insert(rt, &py::path_str(&directory))?;
    }
    let is_main = matches!(ns.get("__name__")?, Val::Str(name) if name == "__main__");
    if is_main && !selftest_asked(&sys)? {
        let rust_part = rt.import("_rust_part")?;
        ns.set("_rust_part", rust_part.clone())?;
        py::method(&rust_part, "start", vec![])?;
    }
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    ns.set("export_assembly", rt.member("_cadq_export", "export_assembly")?)?;
    let petgf_black = rt.member("_materials", "M_PETGF_BLACK")?;
    ns.set("M_PETGF_BLACK", petgf_black.clone())?;
    let linear = rt.member("_materials", "linear")?;
    ns.set("linear", linear.clone())?;
    ns.set("one_body", rt.member("_materials", "one_body")?)?;
    ns.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    ns.set("dims", rt.import("_enclosure_interface")?)?;
    let wings = rt.import("_display_wing_interface")?;
    ns.set("wings", wings.clone())?;
    // Retained for the separately archived vertical-leaf trial generators.
    ns.set("retention", rt.import("_display_retention")?)?;
    ns.set("rounded_prism", rt.member("_swept_top", "rounded_prism")?)?;
    for (name, key) in [
        ("cover_x", "COVER_X"), ("cover_slope", "COVER_Y"), ("cover_corner_r", "CORNER_R"),
        ("cover_slip", "BODY_X_AIR"),
        ("window_x", "WINDOW_X"), ("window_slope", "WINDOW_Y"), ("window_corner_r", "WINDOW_R"),
    ] {
        ns.set(name, wings.attr(key)?)?;
    }
    rt.keep(MODULE, State { cq, linear, petgf_black, here });

    ns.def(rt, "build_display_cover", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        build_display_cover(rt)
    })?;
    ns.def(rt, "selftest", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Int(selftest(rt)?))
    })?;
    ns.def(rt, "numbers", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        numbers(rt)
    })?;
    ns.def(rt, "main", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        main(rt)?;
        Ok(Val::None)
    })?;
    Ok(())
}

/// `sys.exit(selftest() if len(sys.argv) > 1 and sys.argv[1] == 'selftest' else main())`.
pub fn main_block(rt: &Rt) -> Result<()> {
    let sys = rt.namespace(MODULE)?.get("sys")?;
    let code = if selftest_asked(&sys)? {
        Val::Int(selftest(rt)?)
    } else {
        main(rt)?;
        Val::None
    };
    py::method(&sys, "exit", vec![code])?;
    Ok(())
}

/// The cover as a workplane.
pub fn build_display_cover(rt: &Rt) -> Result<Val> {
    let body = super::_display_wing_interface::cover(rt)?;
    py::call_kw(&state(rt)?.cq.attr("Workplane")?, vec![], vec![("obj", body)])
}

/// The cover builds as one valid solid.
pub fn selftest(rt: &Rt) -> Result<i64> {
    let body = py::method(&build_display_cover(rt)?, "val", vec![])?;
    let valid = py::method(&body, "isValid", vec![])?.truthy()?
        && py::method(&body, "Solids", vec![])?.len()? == 1;
    anyhow::ensure!(valid, "assertion failed");
    rt.print("Display cover: one valid solid.".into())?;
    Ok(0)
}

/// `_enclosure_data.dimensions()['display']` as JSON.
fn display(rt: &Rt) -> Result<serde_json::Value> {
    let dimensions = rt.member("_enclosure_data", "dimensions")?;
    rt.member("_enclosure_data", "read")?;
    py::plain(&py::item(&py::call(&dimensions, vec![])?, py::s("display"))?)
}

/// The accepted bezel and coplanar wing stock, in display-local coordinates.
pub fn numbers(rt: &Rt) -> Result<Val> {
    let state = state(rt)?;
    let display = display(rt)?;
    let color = py::plain(&py::call(&state.linear, vec![state.petgf_black.clone()])?)?;
    py::from_json(rt.enclosure_data(json!({"op": "cover-recipe", "display": display, "color": color}))?)
}

/// Cut the cover and fill its figures into the README.
pub fn main(rt: &Rt) -> Result<()> {
    let state = state(rt)?;
    let rust_part = rt.import("_rust_part")?;
    let parent = state.here.parent().context("_here.parent")?.to_path_buf();
    let cut = rust_part.attr("cut")?;
    py::call(&cut, vec![py::s("enclosure-components"), py::s("display-cover"), numbers(rt)?,
        Val::Path(parent.clone())])?;
    let display = display(rt)?;
    let variables = py::from_json(rt.enclosure_data(json!({"op": "cover-variables", "display": display}))?)?;
    let mut values = BTreeMap::new();
    for key in variables.iter()? {
        values.insert(key.str()?, variables.get(key)?.str()?);
    }
    rt.substitute(hsm_documents::Kind::Markdown, &parent.join("README.md"), &values, Some(MODULE))?;
    rt.print("-> display-cover.step, display-cover.stl, README.md".into())?;
    Ok(())
}
