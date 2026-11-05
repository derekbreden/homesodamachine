//! Rear-port identification figures: the word each of the +Y wall of back-top's six stations
//! carries, the lettering those words are set in, and the label envelope the wall's port pockets
//! are read from.
//!
//! Nothing here builds a part. `rear_identification` cuts the six installed tiles and `tube_collar`
//! the collars that name the same lines, and both take each station's word, the key its two filaments
//! are read under and the lettering from here, so a word changed for a port is changed on the wall
//! and on the tube by one edit. `data_ring` letters in the same face.
//!
//! ```text
//!     STATIONS, FLUIDS    each station's word, and the key `_y_wall_dimensions` reads its chip and
//!                         word filaments under
//!     WORD_*              the face, em, recess depth, raise and measured widths of the lettering
//!     RING_W, THICK, RISE, od, bottom, rise
//!                         the label envelope `enclosure_assembly` reads for the wall's port
//!                         pockets, the bosses behind them and the clamp stack
//!     split               a two-colour label STEP back apart, as `(tile, word)`
//! ```
//!
//! Coordinate frame — THE FITTING'S:
//!   Y = the fitting's flow axis. +Y = outboard, toward the customer's tube.
//!   Origin = the label's INBOARD face, the one that lands on the wall. A label spans y = 0 to its
//!       own thickness, and its word fills a recess in the outboard face and stands proud of it.
//!   +Z = up. X completes the right-handed frame, so from outside the machine — looking down −Y —
//!       +X runs to the LEFT and a word reads along −X.
//!
//! Typed state: `_dimensions()['bulkhead']`, copied once at install (the namespace's `_values` is
//! that dict itself), and the three fitting families. `Chip` is a `collections.namedtuple`, a Python
//! class, and `STATIONS` holds its instances.
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use hsm_documents::interop;
use serde_json::{Value, json};
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "bulkhead_ring";

pub struct State {
    pub cq: Val,
    /// `{"union": _jg, "neofit": _neo, "drain": _drain}`, the namespace's own dict.
    families: Val,
    /// `_values` copied: the bulkhead figures as `_enclosure_data.dimensions()` gives them.
    values: Val,
    /// The same, as the JSON `rise` sends.
    values_json: Value,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// Python's `str.isupper`, as the runtime implements it.
fn isupper(text: &str) -> bool {
    text.chars().any(char::is_uppercase) && !text.chars().any(char::is_lowercase)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    let collections = rt.import("collections")?;
    ns.set("collections", collections.clone())?;
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    ns.set("_here", Val::Path(here.clone()))?;
    let hw = here.ancestors().skip(1).find(|p| p.file_name().is_some_and(|n| n == "hardware"))
        .context("StopIteration")?.to_path_buf();
    ns.set("_hw", Val::Path(hw.clone()))?;
    for p in [
        hw.join("scripts"),
        hw.join("printed-parts").join("cadlib"),
        hw.join("printed-parts").join("enclosure").join("enclosure"),
        hw.join("printed-parts").join("enclosure").join("y-wall-of-back-top"),
        hw.join("reference").join("jg-bulkhead-union"),
        hw.join("reference").join("neofit-bulkhead"),
        hw.join("reference").join("neofit-drain-bulkhead"),
    ] {
        ns.set("_p", Val::Path(p.clone()))?;
        py::sys_path_insert(rt, &py::path_str(&p))?;
    }
    let tools = here.ancestors().skip(1).find(|p| p.join("tools").join("docgen").is_dir())
        .context("StopIteration")?.join("tools");
    py::sys_path_insert(rt, &py::path_str(&tools))?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let jg = rt.import("jg_bulkhead_union")?;
    ns.set("_jg", jg.clone())?;
    let drain = rt.import("neofit_drain_bulkhead")?;
    ns.set("_drain", drain.clone())?;
    let neo = rt.import("neofit_bulkhead")?;
    ns.set("_neo", neo.clone())?;
    ns.set("port_chip", rt.import("port_chip")?)?;
    ns.set("_enc_interface", rt.import("_enclosure_interface")?)?;
    // THREE FAMILIES OF FITTING CROSS THIS WALL, and a pocket's lower edge is struck on the flange of
    // the one it sits under — `union` for the PP1208E the water and umbilical ports use, `neofit` for
    // the ABU44, and the metric DRAIN fitting. All labels share one width.
    let families = py::dict([("union", jg), ("neofit", neo), ("drain", drain)]);
    ns.set("FAMILIES", families.clone())?;
    // The band a port's identification is lettered and painted in: `tube_collar` stands its word in
    // a band this tall above the tube's axis, and `drawings/line-art/_appliance_model` paints each
    // port's mark this far past the fitting.
    let dimensions = rt.member("_enclosure_data", "dimensions")?;
    ns.set("_dimensions", dimensions.clone())?;
    ns.set("_read", rt.member("_enclosure_data", "read")?)?;
    let shared = py::item(&py::call(&dimensions, vec![])?, py::s("bulkhead"))?;
    ns.set("_values", shared.clone())?;
    let values = py::snapshot(&shared)?;
    // globals().update({name: value for name, value in _values.items()
    //                   if name.isupper() and name != 'STATIONS'})
    for key in values.iter()? {
        let name = key.str()?;
        if isupper(&name) && name != "STATIONS" {
            ns.set(&name, values.get(key)?)?;
        }
    }
    let chip = py::call(&collections.attr("namedtuple")?, vec![py::s("Chip"), py::s("word")])?;
    ns.set("Chip", chip.clone())?;
    let order = py::at(&values, "station_order")?.iter()?;
    let (words, fluids) = (py::at(&values, "STATIONS")?, py::at(&values, "FLUIDS")?);
    let stations = Val::dict(vec![]);
    for name in &order {
        stations.set(name.clone(), py::call(&chip, vec![words.get(name.clone())?])?)?;
    }
    ns.set("STATIONS", stations)?;
    let by_station = Val::dict(vec![]);
    for name in &order {
        by_station.set(name.clone(), fluids.get(name.clone())?)?;
    }
    ns.set("FLUIDS", by_station)?;
    let values_json = py::plain(&values)?;
    rt.keep(MODULE, State { cq, families, values, values_json });

    ns.def(rt, "od", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["fam"], &[])?;
        b.req("fam")?;
        od(rt)
    })?;
    ns.def(rt, "bottom", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["fam"], &[])?;
        bottom(rt, &b.req("fam")?)
    })?;
    ns.def(rt, "rise", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["which"], &[])?;
        rise(rt, &b.req("which")?)
    })?;
    ns.def(rt, "split", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shape"], &[])?;
        split(rt, b.req("shape")?)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// The common width of all six labels, including the longest FLAVOR word.
pub fn od(rt: &Rt) -> Result<Val> {
    py::at(&state(rt)?.values, "width")
}

/// A pocket's bottom edge below its fitting's axis, at the flange envelope.
pub fn bottom(rt: &Rt, fam: &Val) -> Result<Val> {
    let family = state(rt)?.families.get(fam.clone())?;
    let footprint = py::method(&family, "flange_footprint", vec![])?;
    py::from_json(rt.enclosure_data(json!({"op": "bulkhead-bottom", "flange_footprint": py::plain(&footprint)?}))?)
}

/// A pocket's top above its own fitting's axis.
pub fn rise(rt: &Rt, which: &Val) -> Result<Val> {
    let state = state(rt)?;
    let drop = super::_enclosure_interface::value(rt, "co2_axis_drop")?;
    py::from_json(rt.enclosure_data(json!({"op": "bulkhead-rise", "bulkhead": state.values_json,
        "which": py::plain(which)?, "co2_axis_drop": drop}))?)
}

/// A two-colour label's STEP back apart, as `(tile, word)`.
///
/// The tile spans its whole thickness from the inboard face at y = 0; the lettering stands in the
/// recess and reaches nowhere near that face. So the ONE body touching it is the tile and every
/// other body is a letter. Counting letters would tie this to the word each station happens to
/// carry; reading the face does not.
pub fn split(rt: &Rt, shape: Val) -> Result<Val> {
    let solids = if shape.attr("Solids").is_ok() { py::method(&shape, "Solids", vec![])? } else { shape };
    let all = solids.iter()?;
    let mut floor = vec![];
    for s in &all {
        if py::method(s, "BoundingBox", vec![])?.attr("ymin")?.num()?.abs() < 1e-6 {
            floor.push(s.clone());
        }
    }
    if floor.len() != 1 || all.len() < 2 {
        anyhow::bail!(
            "a label's STEP is a tile and the letters lying in it, and this one carries {} {}, {} of them on \
             the inboard face",
            all.len(), if all.len() == 1 { "body" } else { "bodies" }, floor.len());
    }
    let tile = floor[0].clone();
    let mut letters = vec![];
    for s in all {
        if interop::compare("is_not", s.clone(), tile.clone())?.truthy()? {
            letters.push(s);
        }
    }
    let word = py::call(&state(rt)?.cq.attr("Compound")?.attr("makeCompound")?, vec![Val::list(letters)])?;
    Ok(py::tuple([tile, word]))
}
