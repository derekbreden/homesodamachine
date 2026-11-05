//! Doc-sync driver for hardware/printed-parts/enclosure/y-wall-of-back-top/README.md.
//!
//! Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/y-wall-of-back-top/_y_wall_dimensions.py
//!
//! Typed state: the rear palette (`_read("rear", ...)`) and the three colour mappings built from
//! it; the namespace and the state hold the same dicts.
use super::_nameplate_dimensions::variables;
use super::_nameplate_interface::read;
use super::_nameplate_wing_interface::parent;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result, bail};
use serde_json::json;
use std::path::PathBuf;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_y_wall_dimensions";

pub struct State {
    here: PathBuf,
    palette: Val,
    /// The namespace's `chip_filaments` dict itself.
    pub(crate) chip_filaments: Val,
    chip_word_colors: Val,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = parent(&py::resolve(&py::path(&ns.get("__file__")?)?)?);
    ns.set("_here", Val::Path(here.clone()))?;
    let hw = here.ancestors().skip(1).find(|p| p.file_name().is_some_and(|n| n == "hardware"))
        .context("StopIteration")?.to_owned();
    ns.set("_hw", Val::Path(hw.clone()))?;
    let root = here.ancestors().skip(1).find(|p| p.join("tools").join("docgen").is_dir())
        .context("StopIteration")?;
    py::sys_path_insert(rt, &py::path_str(&root.join("tools")))?;
    py::sys_path_insert(rt, &py::path_str(&hw.join("manifold-layout")))?;
    py::sys_path_insert(rt, &py::path_str(&hw.join("scripts")))?;
    ns.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    let stock_srgb = rt.member("_material_base", "stock_srgb")?;
    ns.set("stock_srgb", stock_srgb.clone())?;
    py::sys_path_insert(rt, &py::path_str(&hw.join("printed-parts/enclosure/enclosure")))?;
    ns.set("_read", rt.member("_enclosure_data", "read")?)?;
    let black = py::call(&stock_srgb, vec![py::s("M_PETGF_BLACK")])?;
    let palette = py::from_json(read(rt, "rear", json!({"black_srgb": py::plain(&black)?}))?)?;
    ns.set("_palette", palette.clone())?;
    ns.def(rt, "__getattr__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["name"], &[])?;
        let name = b.req("name")?;
        module_getattr(rt, &name)
    })?;
    ns.def(rt, "__dir__", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(py::list(module_dir(rt)?.into_iter().map(Val::Str)))
    })?;
    ns.def(rt, "c14_rim_inset", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        c14_rim_inset(rt)
    })?;
    // port_colors = {name: tuple(_palette['port_colors'][name]) for name in _palette['port_order']}
    let port_colors = Val::dict(vec![]);
    for name in py::at(&palette, "port_order")?.iter()? {
        let rgb = py::at(&palette, "port_colors")?.get(name.clone())?;
        port_colors.set(name, Val::Tuple(rgb.iter()?))?;
    }
    ns.set("port_colors", port_colors)?;
    let chip_filaments = Val::dict(vec![]);
    for name in py::at(&palette, "filament_order")?.iter()? {
        let row = py::at(&palette, "chip_filaments")?.get(name.clone())?;
        let rgb = Val::Tuple(row.get(Val::Int(1))?.iter()?);
        chip_filaments.set(name, Val::Tuple(vec![row.get(Val::Int(0))?, rgb]))?;
    }
    ns.set("chip_filaments", chip_filaments.clone())?;
    let chip_word_colors = Val::dict(vec![]);
    for name in py::at(&palette, "filament_order")?.iter()? {
        let rgb = py::at(&palette, "chip_word_colors")?.get(name.clone())?;
        chip_word_colors.set(name, Val::Tuple(rgb.iter()?))?;
    }
    ns.set("chip_word_colors", chip_word_colors.clone())?;
    rt.keep(MODULE, State { here, palette, chip_filaments, chip_word_colors });

    for (name, f) in [
        ("chip_color", chip_color as fn(&Rt, &Val) -> Result<Val>),
        ("word_color", word_color),
        ("port_color_hex", port_color_hex),
        ("port_color_svg", port_color_svg),
    ] {
        ns.def(rt, name, move |rt, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["fluid"], &[])?;
            f(rt, &b.req("fluid")?)
        })?;
    }
    ns.def(rt, "carb_union_end", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["panel_x"], &[])?;
        carb_union_end(rt, &b.req("panel_x")?)
    })?;
    ns.def(rt, "dropped_union_end", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["panel_on_gate_lane", "panel_x"], &[])?;
        let lanes = b.req("panel_on_gate_lane")?;
        dropped_union_end(rt, &lanes, &b.req("panel_x")?)
    })?;
    ns.def(rt, "panel_hole_diameters", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["ports"], &[])?;
        panel_hole_diameters(rt, &b.req("ports")?)
    })?;
    ns.def(rt, "main", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        main(rt)?;
        Ok(Val::None)
    })?;
    Ok(())
}

/// The module's `__getattr__`: `M_PETGF_BLACK` is read from `_material_base` on first use and kept
/// in the namespace.
fn module_getattr(rt: &Rt, name: &Val) -> Result<Val> {
    if name.str().ok().as_deref() == Some("M_PETGF_BLACK") {
        let value = rt.member("_material_base", "M_PETGF_BLACK")?;
        rt.namespace(MODULE)?.globals().set(name.clone(), value.clone())?;
        return Ok(value);
    }
    bail!("{}", name.str()?)
}

/// `sorted(set(globals()) | {"M_PETGF_BLACK"})`.
fn module_dir(rt: &Rt) -> Result<Vec<String>> {
    let mut names = rt.namespace(MODULE)?.names()?;
    names.push("M_PETGF_BLACK".into());
    names.sort();
    names.dedup();
    Ok(names)
}

// AC inlet recess: the bore the mating C13 cord housing enters, wall and inlet
// tunnel in one (`enclosure._c14_tunnel`), with the IEC 60320 C14 receptacle's
// flange seated at its floor and its shroud standing back up it. The depth range
// is how far the housing comes down that bore. Typed off the cordset, which this
// tree carries no body for — there is nothing to read it off.

/// How far the inlet's rim face, on the pocket floor, sits inside the wall's outer plane: the
/// bore the C13 nose crosses before it reaches the inlet.
pub fn c14_rim_inset(rt: &Rt) -> Result<Val> {
    let ea = rt.import("enclosure_assembly")?;
    let rear_plane_y = py::plain(&ea.attr("_enc")?.attr("rear_plane_y")?)?;
    let wall = py::plain(&ea.attr("_enc")?.attr("wall")?)?;
    let seat_y = py::plain(&py::call(&ea.attr("c14_seat_y")?, vec![])?)?;
    py::from_json(read(rt, "rim-inset", json!({"rear_plane_y": rear_plane_y, "wall": wall, "seat_y": seat_y}))?)
}

// The wall's identification colours, by the fluid each names — the one
// statement of what a colour MEANS on this machine.
//
// Blue is spent: `bom.md` §3 buys the carbonated-water umbilical riser in BLUE
// LLDPE and §8 buys the union that receives it wearing a blue accent ring, so
// blue names carbonated water and nothing else on this wall. That leaves the
// customer's teed-in tap-water station as the WHITE-marked one and the CO2
// inlet as the RED one, which is the scheme §"Umbilical port — tube
// identification" states and the quick start names its ports by.
//
// The iso line-art that paints these rings onto the wall
// (`../drawings/line-art/_appliance_model.py`) reads them from here, and the
// quick start (`/hardware/quickstart/`) reads the same four into its generated
// stylesheet from this file — so the face a customer looks at and the sheet in
// their hand cannot disagree about which colour is which line.
// FOUR TUBE COLOURS AND FOUR CHIP COLOURS, and they are the same four: a chip
// is the colour of the tube that goes into it. Black is not the absence of a
// marking on this wall — it is the FLAVOUR colour, the stock `_routing.SPOOLS`
// cuts both flavour lines off, and both flavour ports wear it. What black does
// not do is tell A from B: a customer pushes black into either one and the
// manifold sorts them.
//
// THE SPOOL EACH CHIP AND ITS TUBE COLLAR ARE CUT OFF, and it is not the tube's own colour.
// `port_colors` is the IDENTIFICATION scheme — neoFlo LLDPE, what the customer's tube is — and a
// chip printed to match one is Polymaker Fiberon PET-GF15, a different product that happens to
// answer to the same name. White, blue and red are the median of the wound filament in
// Polymaker's product photographs (FL02003, FL02006, FL02007). Black uses the shared
// PET-GF stock appearance. `ledger/purchases.md` §13 buys all four.

/// The colour one chip actually comes out — the filament it prints in, not the
/// identification colour it stands for.
///
/// `port_colors` is the SCHEME: what blue means on this wall, and the neoFlo
/// LLDPE the customer's tube is cut off. A chip printed to match one is Fiberon
/// PET-GF15, a different product answering to the same name.
/// `enclosure_assembly.build_bulkhead_rings` and the tube collars draw the chip
/// from here and the drawings paint the scheme from `port_colors`.
pub fn chip_color(rt: &Rt, fluid: &Val) -> Result<Val> {
    state(rt)?.chip_filaments.get(fluid.clone())?.get(Val::Int(1))
}

/// The colour a chip's WORD is lettered in — the one of the black and white spools that reads
/// against the filament that chip actually prints in. `bulkhead_ring` cuts the recess and this is
/// what fills it and stands out of it.
pub fn word_color(rt: &Rt, fluid: &Val) -> Result<Val> {
    state(rt)?.chip_word_colors.get(fluid.clone())
}

/// One identification colour as `#rrggbb`, for an SVG presentation
/// attribute.
pub fn port_color_hex(rt: &Rt, fluid: &Val) -> Result<Val> {
    py::at(&state(rt)?.palette, "hex")?.get(fluid.clone())
}

/// One identification colour in the `rgb(r, g, b)` spelling the iso
/// renderer writes into a marking's `fill` — which is the string a consumer
/// of that SVG finds the marking by.
pub fn port_color_svg(rt: &Rt, fluid: &Val) -> Result<Val> {
    py::at(&state(rt)?.palette, "svg")?.get(fluid.clone())
}

/// Which end of the umbilical row the blue-ringed carbonated-water union
/// stands at — READ off the `enclosure_assembly.PANEL_X` mapping `main` hands in, so the user
/// rule ("blue tube into the blue-ringed bulkhead, at
/// this end") cannot outlive the row it describes. +X is east.
pub fn carb_union_end(rt: &Rt, panel_x: &Val) -> Result<Val> {
    py::from_json(read(rt, "carb-union-end", json!({"panel_x": py::plain(panel_x)?}))?)
}

/// Which end of the umbilical row stands off the row's own storey — READ off
/// `enclosure_assembly.PANEL_ON_GATE_LANE` mapping `main` hands in against `PANEL_X`, so the user
/// rule ("the ones lower down are at this end") cannot outlive the arrangement it
/// describes. +X is east.
pub fn dropped_union_end(rt: &Rt, panel_on_gate_lane: &Val, panel_x: &Val) -> Result<Val> {
    let lanes = py::plain(&Val::list(panel_on_gate_lane.iter()?))?;
    py::from_json(read(rt, "dropped-union-end", json!({"lanes": lanes, "panel_x": py::plain(panel_x)?}))?)
}

/// The two bores this wall carries: `(bulkhead, co2)`.
///
/// Taken from the functions that STRIKE them, not from a second copy of their
/// arithmetic. `enclosure_assembly.y_wall_ports` and `enclosure_assembly.co2_wall_port` are the
/// calls `enclosure_assembly.pack` fills `back_ports` with, and `enclosure._port_cuts` bores
/// that list — so these are the holes that get cut, and a change to HOW either is
/// struck (a chamfer allowance, a different slip for gas than for water) arrives here
/// instead of leaving the README quoting the old rule.
///
/// Both strike against a placed fitting, so both wanted the pack. `_facts` carries what
/// those two calls returned when the machine was last stood, so the reading is the same
/// reading and no build is taken for it. `main` imports that doc-only reading and hands the
/// ports in; drivers importing this module for the AC recess or colours load neither the facts
/// nor the assembled machine.
///
/// All four PP1208E bulkheads on this wall — 1 water inlet + 3 umbilical-port unions —
/// use the largest union opening for the quarter-inch figure; metric flavor openings are listed separately.
pub fn panel_hole_diameters(rt: &Rt, ports: &Val) -> Result<Val> {
    let value = py::from_json(read(rt, "panel-hole-diameters", json!({"ports": py::plain(ports)?}))?)?;
    Ok(Val::Tuple(value.iter()?))
}

pub fn main(rt: &Rt) -> Result<()> {
    let state = state(rt)?;
    let above_core = rt.import("above_core")?;
    let spec = py::call(&above_core.attr("specification")?, vec![])?;
    let rows = py::at(&py::at(&py::at(&spec, "rear_wall")?, "grid")?, "rows_z_mm")?;
    let values = variables(read(rt, "grid-variables", json!({"rows": py::plain(&rows)?}))?)?;
    rt.substitute(hsm_documents::Kind::Markdown, &state.here.join("README.md"), &values, Some(MODULE))?;
    rt.print("-> README.md".into())?;
    Ok(())
}

pub fn main_block(rt: &Rt) -> Result<()> {
    main(rt)
}
