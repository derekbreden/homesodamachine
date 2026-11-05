//! Black DATA trim, white raised lettering, continuous nameplate wings.
//!
//! Typed state: the lettering figures read once from `bulkhead_ring` (`WORD_SIZE`, `WORD_RAISE`,
//! `WORD_FONT`, `WORD_KIND`), the STEP path, and the CadQuery and `_materials` handles, which stay
//! providers. The DATA face (`THICK`, `TOP`, `INK_DEPTH`) is `_data_wing_interface`'s typed state.
use super::_data_wing_interface as interface;
use super::_nameplate_interface::{ints, m, mk, read};
use super::_nameplate_wing_interface::parent;
use super::_y_wall_dimensions as rear;
use super::bulkhead_ring as ring;
use super::num::Num;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use serde_json::json;
use std::path::PathBuf;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "data_ring";

/// The lettering `bulkhead_ring` sets every rear word in.
struct Word {
    size: Num,
    raise: Num,
    font: String,
    kind: String,
}

pub struct State {
    cq: Val,
    linear: Val,
    step_safe: Val,
    /// `STEP`.
    step: PathBuf,
    word: Word,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("json", rt.import("json")?)?;
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let hw = here.ancestors().skip(1).find(|p| p.file_name().is_some_and(|n| n == "hardware"))
        .context("StopIteration")?.to_path_buf();
    ns.set("_hw", Val::Path(hw.clone()))?;
    let front = [
        parent(&here),
        hw.join("scripts"),
        hw.join("printed-parts/enclosure/enclosure"),
        hw.join("printed-parts/enclosure/bulkhead-ring"),
        hw.join("printed-parts/enclosure/y-wall-of-back-top"),
    ];
    rt.import("sys")?.attr("path")?.set(Val::Slice { start: None, stop: Some(0), step: 1 },
        py::list(front.iter().map(|p| py::s(py::path_str(p)))))?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    ns.set("interface", rt.import("_data_wing_interface")?)?;
    let bulkhead = rt.import("bulkhead_ring")?;
    ns.set("ring", bulkhead.clone())?;
    ns.set("rear", rt.import("_y_wall_dimensions")?)?;
    ns.set("export_assembly", rt.member("_cadq_export", "export_assembly")?)?;
    let linear = rt.member("_materials", "linear")?;
    ns.set("linear", linear.clone())?;
    let step_safe = rt.member("_materials", "step_safe")?;
    ns.set("step_safe", step_safe.clone())?;
    let step = hw.join("printed-parts/enclosure/data-ring/data-ring.step");
    ns.set("STEP", Val::Path(step.clone()))?;
    let word = Word {
        size: Num::of(&bulkhead.attr("WORD_SIZE")?)?,
        raise: Num::of(&bulkhead.attr("WORD_RAISE")?)?,
        font: bulkhead.attr("WORD_FONT")?.str()?,
        kind: bulkhead.attr("WORD_KIND")?.str()?,
    };
    rt.keep(MODULE, State { cq, linear, step_safe, step, word });

    ns.def(rt, "build_word", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        build_word(rt)
    })?;
    ns.def(rt, "build_ring", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        build_ring(rt)
    })?;
    ns.def(rt, "build_part", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        build_part(rt)
    })?;
    ns.def(rt, "split", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shape"], &[])?;
        split(rt, b.req("shape")?)
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

/// The `__main__` block: start the part-program session, then `main()`.
pub fn main_block(rt: &Rt) -> Result<()> {
    let rust_part = rt.import("_rust_part")?;
    rt.namespace(MODULE)?.set("_rust_part", rust_part.clone())?;
    m(&rust_part, "start", vec![])?;
    main(rt)
}

pub fn build_word(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let d = interface::state(rt)?.data;
    let w = &st.word;
    let workplane = py::call(&st.cq.attr("Workplane")?, vec![py::s("XY")])?;
    let lettered = mk(&workplane, "text", vec![py::s("DATA"), w.size.val(),
        Num::F(d.ink_depth).add(w.raise).val()], vec![
        ("font", py::s(w.font.as_str())),
        ("kind", py::s(w.kind.as_str())),
        ("halign", py::s("center")),
        ("valign", py::s("center")),
    ])?;
    let text = m(&m(&m(&lettered, "val", vec![])?, "rotate",
        vec![ints(&[0, 0, 0]), ints(&[1, 0, 0]), Val::Int(90)])?, "rotate",
        vec![ints(&[0, 0, 0]), ints(&[0, 0, 1]), Val::Int(180)])?;
    let bb = m(&text, "BoundingBox", vec![])?;
    let at = |name: &str| -> Result<Num> { Num::of(&bb.attr(name)?) };
    let x = at("xmin")?.add(at("xmax")?).neg().div(Num::I(2));
    let y = Num::F(d.thick).sub(Num::F(d.ink_depth)).sub(at("ymin")?);
    let z = Num::F(11.0).add(Num::F(d.top)).div(Num::I(2)).sub(at("zmin")?.add(at("zmax")?).div(Num::I(2)));
    m(&text, "translate", vec![py::tuple([x.val(), y.val(), z.val()])])
}

pub fn build_ring(rt: &Rt) -> Result<Val> {
    let blank = interface::blank(rt)?;
    m(&blank, "cut", vec![build_word(rt)?])
}

pub fn build_part(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let assembly = py::call(&st.cq.attr("Assembly")?, vec![])?;
    let flavor = py::s("flavor");
    let rows = [
        ("data-ring", build_ring(rt)?, rear::chip_color(rt, &flavor)?),
        ("data-ring-word", build_word(rt)?, rear::word_color(rt, &flavor)?),
    ];
    for (name, solid, color) in rows {
        let channels = color.iter()?.iter().map(|c| Ok(Num::of(c)?.div(Num::I(255)).val()))
            .collect::<Result<Vec<_>>>()?;
        let color = py::call(&st.step_safe, vec![py::call(&st.cq.attr("Color")?, channels)?])?;
        mk(&assembly, "add", vec![solid], vec![("name", py::s(name)), ("color", color)])?;
    }
    Ok(assembly)
}

pub fn split(rt: &Rt, shape: Val) -> Result<Val> {
    ring::split(rt, shape)
}

/// The shared DATA trim datums, original glyph controls and filament colours.
pub fn numbers(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let artwork = parent(&st.step).join("data-word.json");
    rt.note_read(&artwork)?;
    let color = |rgb: Val| -> Result<Val> {
        let channels = rgb.iter()?.iter().map(|c| Ok(Num::of(c)?.div(Num::F(255.)).val()))
            .collect::<Result<Vec<_>>>()?;
        let srgb = py::call(&st.cq.attr("Color")?, channels)?;
        py::call(&st.linear, vec![py::call(&st.step_safe, vec![srgb])?])
    };
    let values = py::snapshot(&py::call(&rt.member("_enclosure_data", "dimensions")?, vec![])?)?;
    let flavor = py::s("flavor");
    let fields = json!({
        "data": py::plain(&py::at(&values, "data")?)?,
        "nameplate": py::plain(&py::at(&values, "nameplate")?)?,
        "bulkhead": py::plain(&py::at(&values, "bulkhead")?)?,
        "artwork_path": py::path_str(&artwork),
        "chip_color": py::plain(&color(rear::chip_color(rt, &flavor)?)?)?,
        "word_color": py::plain(&color(rear::word_color(rt, &flavor)?)?)?,
    });
    py::from_json(read(rt, "data-recipe", fields)?)
}

pub fn main(rt: &Rt) -> Result<()> {
    let st = state(rt)?;
    let rust_part = rt.import("_rust_part")?;
    let recipe = numbers(rt)?;
    m(&rust_part, "cut", vec![py::s("enclosure-components"), py::s("data-ring"), recipe,
        Val::Path(parent(&st.step))])?;
    Ok(())
}
