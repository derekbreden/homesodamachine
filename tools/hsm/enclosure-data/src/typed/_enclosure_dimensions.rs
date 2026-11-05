//! Read the enclosure README's dimensions from canonical appliance facts.
//!
//! Typed API: [`main`] fills the enclosure README's dimensions. The appliance facts, the
//! condenser figures and the enclosure datums are read once by the module's top level, as
//! Python reads them, and kept: `facts`, `box`, `compressor` and `block` stay the provider's
//! objects; the appliance extents are computed here.
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use std::collections::BTreeMap;
use std::path::PathBuf;

pub const TYPED: bool = true;
const MODULE: &str = "_enclosure_dimensions";

/// The suffixes of the facts' sources that the build records as read.
const RECORDED: [&str; 7] = [".py", ".rs", ".json", ".toml", ".lock", ".yaml", ".yml"];

struct State {
    here: PathBuf,
    /// `_enclosure_datums.load()`.
    enclosure: Val,
    /// The namespace's `condenser`: `AIRFLOW`, `FACE_A` and `FACE_B` of `condenser_block`.
    condenser: Val,
    foam_shell_outer_height: Val,
    outer_shell_x_length: Val,
    outer_shell_y_length: Val,
    /// `_facts.read()`, its `box`, and its `bb('compressor')` and `bb('condenser+fan')`.
    facts: Val,
    box_: Val,
    compressor: Val,
    block: Val,
    /// `APPLIANCE_W`, `APPLIANCE_D` and `APPLIANCE_H`.
    appliance: [Num; 3],
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("sys", rt.import("sys")?)?;
    rt.import("pathlib")?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let file = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let here = file.parent().unwrap_or(&file).to_owned();
    ns.set("HERE", Val::Path(here.clone()))?;
    let root = here
        .ancestors()
        .skip(1)
        .find(|p| p.join("hardware").join("scripts").is_dir())
        .context("StopIteration")?
        .to_owned();
    ns.set("ROOT", Val::Path(root.clone()))?;
    let hw = root.join("hardware");
    ns.set("HW", Val::Path(hw.clone()))?;
    for path in [
        root.join("tools"),
        hw.join("scripts"),
        hw.join("manifold-layout"),
        hw.join("printed-parts").join("cadlib"),
        hw.join("printed-parts").join("cold-core"),
        here.join("enclosure"),
        hw.join("reference").join("condenser-block"),
    ] {
        ns.set("path", Val::Path(path.clone()))?;
        py::sys_path_insert(rt, &py::path_str(&path))?;
    }

    let facts_module = rt.import("_facts")?;
    ns.set("_facts", facts_module.clone())?;
    ns.set("_enclosure_numbers", rt.member("_enclosure_datums", "load")?)?;
    let enclosure = super::_enclosure_datums::load(rt)?;
    ns.set("enclosure", enclosure.clone())?;
    let note_read = rt.member("_cadq_export", "note_read")?;
    ns.set("note_read", note_read.clone())?;
    let condenser_source = hw.join("reference/condenser-block/condenser_block.py");
    ns.set("_condenser_source", Val::Path(condenser_source.clone()))?;
    py::call(&note_read, vec![Val::Path(condenser_source)])?;
    let condenser_module = rt.import("condenser_block")?;
    ns.set("_condenser", condenser_module.clone())?;
    let condenser = Val::dict(vec![]);
    for name in ["AIRFLOW", "FACE_A", "FACE_B"] {
        condenser.set(py::s(name), condenser_module.attr(name)?)?;
    }
    ns.set("condenser", condenser.clone())?;
    py::call(&note_read, vec![Val::Path(hw.join("manifold-layout/enclosure_assembly.py"))])?;
    for source in py::method(&facts_module, "sources", vec![])?.iter()? {
        ns.set("source", source.clone())?;
        let text = source.str()?;
        let suffix = PathBuf::from(&text)
            .extension()
            .map(|v| format!(".{}", v.to_string_lossy()))
            .unwrap_or_default();
        if RECORDED.contains(&suffix.as_str()) {
            py::call(&note_read, vec![Val::Path(root.join(&text))])?;
        }
    }
    let foam_shell_outer_height = rt.member("_cold_core_interface", "foam_shell_outer_height")?;
    ns.set("foam_shell_outer_height", foam_shell_outer_height.clone())?;
    let outer_shell_x_length = rt.member("_cold_core_interface", "outer_shell_x_length")?;
    ns.set("outer_shell_x_length", outer_shell_x_length.clone())?;
    let outer_shell_y_length = rt.member("_cold_core_interface", "outer_shell_y_length")?;
    ns.set("outer_shell_y_length", outer_shell_y_length.clone())?;
    ns.set("substitute_md", rt.member("docgen", "substitute_md")?)?;

    let facts = py::method(&facts_module, "read", vec![])?;
    ns.set("facts", facts.clone())?;
    let box_ = facts.attr("box")?;
    ns.set("box", box_.clone())?;
    let outer = py::at(&box_, "outer")?;
    ns.set("outer", outer.clone())?;
    let compressor = py::method(&facts, "bb", vec![py::s("compressor")])?;
    let block = py::method(&facts, "bb", vec![py::s("condenser+fan")])?;
    ns.set("compressor", compressor.clone())?;
    ns.set("block", block.clone())?;
    let extents = py::snapshot(&outer)?;
    let at = |k: i64| -> Result<Num> { Num::of(&extents.get(Val::Int(k))?) };
    let appliance = [at(1)?.sub(at(0)?), at(3)?.sub(at(2)?), at(5)?.sub(at(4)?)];
    ns.set("APPLIANCE_W", appliance[0].val())?;
    ns.set("APPLIANCE_D", appliance[1].val())?;
    ns.set("APPLIANCE_H", appliance[2].val())?;
    rt.keep(MODULE, State {
        here,
        enclosure,
        condenser,
        foam_shell_outer_height,
        outer_shell_x_length,
        outer_shell_y_length,
        facts,
        box_,
        compressor,
        block,
        appliance,
    });
    ns.def(rt, "main", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        main(rt)?;
        Ok(Val::None)
    })?;
    Ok(())
}

pub fn main_block(rt: &Rt) -> Result<()> {
    main(rt)
}

/// `abs(x)`.
fn abs(x: Num) -> Num {
    match x {
        Num::I(i) => Num::I(i.abs()),
        Num::F(v) => Num::F(v.abs()),
    }
}

/// Fill the README's dimensions and report it.
pub fn main(rt: &Rt) -> Result<()> {
    let state = rt.state::<State>(MODULE)?;
    // The front corner stations identify the floor footprint independently of
    // cap passages and equipment standing proud above it.
    let mut core_front: Option<Num> = None;
    for stop in py::snapshot(&py::at(&state.box_, "core_stops")?)?.iter()? {
        let stop = py::unpack(&stop, 3)?;
        let front = Num::of(&stop[1])?.sub(Num::of(&stop[2])?);
        core_front = Some(core_front.map_or(front, |best| best.min(front)));
    }
    let core_front = core_front.context("empty min/max")?;

    let (compressor, block) = (&state.compressor, &state.block);
    let reading = |object: &Val, name: &str| -> Result<(Val, Num)> {
        let value = object.attr(name)?;
        let number = Num::of(&value)?;
        Ok((value, number))
    };
    let (compressor_xmin, compressor_xmax) = (reading(compressor, "xmin")?, reading(compressor, "xmax")?);
    let (compressor_ymin, compressor_ymax) = (reading(compressor, "ymin")?, reading(compressor, "ymax")?);
    let compressor_zmax = reading(compressor, "zmax")?;
    let (block_xmin, block_xmax) = (reading(block, "xmin")?, reading(block, "xmax")?);
    let (block_ymin, block_ymax) = (reading(block, "ymin")?, reading(block, "ymax")?);
    let (block_zmin, block_zmax) = (reading(block, "zmin")?, reading(block, "zmax")?);
    let condenser = |name: &str| py::at(&state.condenser, name);
    let splits = py::snapshot(&py::at(&state.box_, "splits")?)?;
    let back_bottom = py::snapshot(&py::at(&py::at(&state.facts.attr("pieces")?, "back-bottom")?, "box")?)?;
    let back_bottom_h = Num::of(&back_bottom.get(Val::Int(5))?)?.sub(Num::of(&back_bottom.get(Val::Int(2))?)?);

    let g = |value: &Val| num::fmtv(value, ".4g");
    let n = |value: Num| value.fmt(".4g");
    let [width, depth, height] = state.appliance;
    let variables: [(&str, String); 22] = [
        ("FOAM_SHELL_X", g(&state.outer_shell_x_length)?),
        ("FOAM_SHELL_Y", g(&state.outer_shell_y_length)?),
        ("FOAM_SHELL_Z", g(&state.foam_shell_outer_height)?),
        ("APPLIANCE_WIDTH", format!("{} mm", n(width))),
        ("APPLIANCE_DEPTH", format!("{} mm", n(depth))),
        ("APPLIANCE_HEIGHT", format!("{} mm", n(height))),
        ("WALL_STANDOFF", g(&state.enclosure.attr("side_band_inset")?)?),
        ("COMP_BAY_W", n(compressor_xmax.1.max(block_xmax.1).sub(compressor_xmin.1.min(block_xmin.1)))),
        ("COMP_BAY_D", n(compressor_ymax.1.max(block_ymax.1).sub(compressor_ymin.1.min(block_ymin.1)))),
        ("COMP_BAY_TOP", n(compressor_zmax.1.max(block_zmax.1))),
        ("COMP_BAY_STEP", n(abs(compressor_zmax.1.sub(block_zmax.1)))),
        ("COMPRESSOR_ROOF", g(&compressor_zmax.0)?),
        ("MATE_X", g(&compressor_xmax.0)?),
        ("CONDENSER_ACROSS", g(&condenser("AIRFLOW")?)?),
        ("CONDENSER_LONG", g(&condenser("FACE_A")?)?),
        ("CONDENSER_STANDING", g(&condenser("FACE_B")?)?),
        ("CONDENSER_LIFT", g(&block_zmin.0)?),
        ("CORE_FRONT_Y", n(core_front)),
        ("CORE_CROWN", g(&py::at(&state.facts.attr("faces")?, "foam-assembly.cap")?)?),
        ("BACK_Z_SEAM", g(&splits.get(Val::Int(1))?)?),
        ("BACK_BOTTOM_H", n(back_bottom_h)),
        ("BED_Z", g(&state.enclosure.attr("H2C_Z")?)?),
    ];
    let values: BTreeMap<String, String> = variables.into_iter().map(|(k, v)| (k.to_owned(), v)).collect();
    rt.substitute(hsm_documents::Kind::Markdown, &state.here.join("README.md"), &values, Some(MODULE))?;
    rt.print("-> README.md".into())?;
    Ok(())
}
