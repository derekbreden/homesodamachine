//! The 1 mm TPU ring between the machine display glass and its snap-retained cover.
//!
//! The ring lies in the cover's local frame: X across, Y up the display plane and Z
//! out of the face. Its outer outline matches the glass and its inner outline the window.
//!
//! The ring's figures are the `gasket` reading (`main.rs`), answered in this process from the six
//! display dimensions `_enclosure_interface` gives and the ring's colour; its `scalars` are set
//! into the namespace in that reading's key order (`globals().update(_data()['scalars'])`).
//! CadQuery, `_rust_part` and `_materials` stay providers, reached by callback.
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use super::num;
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::path::PathBuf;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "display_gasket";

/// The ring's figures (`_data()['scalars']`).
#[derive(Clone, Copy, Debug)]
pub struct Scalars {
    pub corner_r: f64,
    pub glass_face_depth: f64,
    pub glass_thickness: f64,
    pub inner_slope: f64,
    pub inner_x: f64,
    pub outer_slope: f64,
    pub outer_x: f64,
    pub thickness: f64,
    pub z_bottom: f64,
    pub z_top: f64,
}

pub struct State {
    pub cq: Val,
    linear: Val,
    tpu_black: Val,
    /// The display dimensions `_data` sends, in its keyword order.
    display: Vec<(&'static str, Val)>,
    pub s: Scalars,
    here: PathBuf,
    file: PathBuf,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

const DISPLAY: [&str; 6] = [
    "display_bezel_depth", "display_bezel_slope", "display_bezel_x", "display_corner_r", "display_inset_depth",
    "display_inset_lap",
];

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let file = py::path(&ns.get("__file__")?)?;
    let here = py::resolve(&file)?;
    ns.set("_here", Val::Path(here.clone()))?;
    let hw = here.ancestors().skip(1).find(|p| p.file_name().is_some_and(|n| n == "hardware"))
        .context("StopIteration")?.to_path_buf();
    ns.set("_hw", Val::Path(hw.clone()))?;
    py::sys_path_insert(rt, &py::path_str(&hw.join("scripts")))?;
    let tools = here.ancestors().skip(1).find(|p| p.join("tools").join("docgen").is_dir())
        .context("StopIteration")?.join("tools");
    py::sys_path_insert(rt, &py::path_str(&tools))?;
    py::sys_path_insert(rt, &py::path_str(&hw.join("printed-parts").join("enclosure").join("enclosure")))?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    ns.set("export_assembly", rt.member("_cadq_export", "export_assembly")?)?;
    let tpu_black = rt.member("_materials", "M_TPU_BLACK")?;
    ns.set("M_TPU_BLACK", tpu_black.clone())?;
    let linear = rt.member("_materials", "linear")?;
    ns.set("linear", linear.clone())?;
    ns.set("one_body", rt.member("_materials", "one_body")?)?;
    ns.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    ns.set("substitute_py_comments", rt.member("docgen", "substitute_py_comments")?)?;
    let mut dims = BTreeMap::new();
    for name in DISPLAY {
        let value = rt.member("_enclosure_interface", name)?;
        ns.set(name, value.clone())?;
        dims.insert(name, value);
    }
    ns.set("_read", rt.member("_enclosure_data", "read")?)?;
    // _read('gasket', display_bezel_x=..., display_bezel_slope=..., display_corner_r=...,
    //       display_inset_lap=..., display_bezel_depth=..., display_inset_depth=..., color=...)
    let display = ["display_bezel_x", "display_bezel_slope", "display_corner_r", "display_inset_lap",
        "display_bezel_depth", "display_inset_depth"].map(|name| (name, dims[name].clone())).to_vec();
    let reading = read(rt, &display, &linear, &tpu_black)?;
    ns.def(rt, "_data", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        py::from_json(data(rt)?)
    })?;
    // globals().update(_data()['scalars'])
    let scalars = reading["scalars"].as_object().context("gasket scalars")?;
    for (name, value) in scalars {
        ns.set(name, py::from_json(value.clone())?)?;
    }
    let f = |key: &str| scalars.get(key).and_then(Value::as_f64).with_context(|| format!("gasket {key}"));
    let s = Scalars {
        corner_r: f("corner_r")?,
        glass_face_depth: f("glass_face_depth")?,
        glass_thickness: f("glass_thickness")?,
        inner_slope: f("inner_slope")?,
        inner_x: f("inner_x")?,
        outer_slope: f("outer_slope")?,
        outer_x: f("outer_x")?,
        thickness: f("thickness")?,
        z_bottom: f("z_bottom")?,
        z_top: f("z_top")?,
    };
    rt.keep(MODULE, State { cq, linear, tpu_black, display, s, here, file });

    ns.def(rt, "_rounded_prism", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["x", "slope", "r", "z0", "z1"], &[])?;
        let (x, slope, r) = (b.req("x")?, b.req("slope")?, b.req("r")?);
        let (z0, z1) = (b.req("z0")?, b.req("z1")?);
        rounded_prism(rt, x, slope, r, z0, z1)
    })?;
    ns.def(rt, "build_display_gasket", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        build_display_gasket(rt)
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

/// `if __name__ == "__main__": main()`, the module run as a script.
pub fn main_block(rt: &Rt) -> Result<()> {
    let rust_part = rt.import("_rust_part")?;
    rt.namespace(MODULE)?.set("_rust_part", rust_part.clone())?;
    py::method(&rust_part, "start", vec![])?;
    main(rt)
}

/// The `gasket` reading for these display dimensions and the ring's colour.
fn read(rt: &Rt, display: &[(&str, Val)], linear: &Val, tpu_black: &Val) -> Result<Value> {
    let mut payload = serde_json::Map::new();
    payload.insert("op".into(), json!("gasket"));
    for (name, value) in display {
        payload.insert((*name).into(), py::plain(value)?);
    }
    payload.insert("color".into(), py::plain(&py::call(linear, vec![tpu_black.clone()])?)?);
    rt.enclosure_data(Value::Object(payload))
}

/// `_data()`: the ring's variables, scalars and recipe.
pub fn data(rt: &Rt) -> Result<Value> {
    let state = state(rt)?;
    read(rt, &state.display, &state.linear, &state.tpu_black)
}

/// A `slope` by `x` plate between z0 and z1, its vertical edges rounded `r`.
pub fn rounded_prism(rt: &Rt, x: Val, slope: Val, r: Val, z0: Val, z1: Val) -> Result<Val> {
    let cq = &state(rt)?.cq;
    let height = num::Num::of(&z1)?.sub(num::Num::of(&z0)?);
    let wp = py::call(&cq.attr("Workplane")?, vec![py::s("XY")])?;
    let wp = py::call_kw(&wp.attr("workplane")?, vec![], vec![("offset", z0)])?;
    let wp = py::method(&py::method(&wp, "rect", vec![x, slope])?, "extrude", vec![height.val()])?;
    py::method(&py::method(&wp, "edges", vec![py::s("|Z")])?, "fillet", vec![r])
}

/// The ring, cut from the glass's outline by the plate's window.
pub fn build_display_gasket(rt: &Rt) -> Result<Val> {
    let s = state(rt)?.s;
    let proud = 1.0; // struck past both faces so the cut breaks clean
    let f = Val::Float;
    let ring = rounded_prism(rt, f(s.outer_x), f(s.outer_slope), f(s.corner_r), f(s.z_bottom), f(s.z_top))?;
    let window = rounded_prism(rt, f(s.inner_x), f(s.inner_slope), f(s.corner_r), f(s.z_bottom - proud),
        f(s.z_top + proud))?;
    py::method(&ring, "cut", vec![window])
}

/// The glass/window outlines and their shared compressed-gap thickness.
pub fn numbers(rt: &Rt) -> Result<Val> {
    py::from_json(data(rt)?["recipe"].take())
}

/// Cut the ring, report its figures and fill them into the README and this file's comments.
pub fn main(rt: &Rt) -> Result<()> {
    let state = state(rt)?;
    let rust_part = rt.import("_rust_part")?;
    let parent = state.here.parent().context("_here.parent")?.to_path_buf();
    let result = py::call(&rust_part.attr("cut")?, vec![py::s("enclosure-components"), py::s("display-gasket"),
        numbers(rt)?, Val::Path(parent.clone())])?;

    let out = parent.join("display-gasket.step");
    rt.print(format!("-> {}", out.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default()))?;

    let body = py::item(&py::item(&result, py::s("bodies"))?, Val::Int(0))?;
    let (lo, hi) = (py::item(&body, py::s("min"))?, py::item(&body, py::s("max"))?);
    let s = state.s;
    let (lap, inset) = (&state.display[3].1, &state.display[5].1);
    rt.print("Display gasket".into())?;
    rt.print(format!("  {} x {} outer, {} x {} inner — a {} ring, r{} corners", num::fmt(s.outer_x, "g"),
        num::fmt(s.outer_slope, "g"), num::fmt(s.inner_x, "g"), num::fmt(s.inner_slope, "g"), num::fmtv(lap, "g")?,
        num::fmt(s.corner_r, "g")))?;
    rt.print(format!("  {} thick, from the plate's underside at {} down to the glass at {}", num::fmt(s.thickness, "g"),
        num::fmtv(inset, "g")?, num::fmt(s.glass_face_depth, "g")))?;
    let at = |v: &Val, i: i64| -> Result<String> { num::fmtv(&py::item(v, Val::Int(i))?, ".2f") };
    rt.print(format!("  Bounding box: X [{}, {}]  Y [{}, {}]  Z [{}, {}]", at(&lo, 0)?, at(&hi, 0)?, at(&lo, 1)?,
        at(&hi, 1)?, at(&lo, 2)?, at(&hi, 2)?))?;

    let variables = py::from_json(data(rt)?["variables"].take())?;
    let mut values = BTreeMap::new();
    for key in variables.iter()? {
        values.insert(key.str()?, variables.get(key)?.str()?);
    }

    rt.substitute(hsm_documents::Kind::Markdown, &parent.join("README.md"), &values, Some(MODULE))?;
    rt.print("-> README.md".into())?;

    rt.substitute(hsm_documents::Kind::Python, &state.file, &values, Some(MODULE))?;
    rt.print(format!("-> {}", state.file.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default()))?;
    Ok(())
}
