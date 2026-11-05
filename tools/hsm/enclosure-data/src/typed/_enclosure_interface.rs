//! Shared enclosure dimensions that do not require building the enclosure model.
//!
//! Parts that mate with the shell import this module. The enclosure module re-exports the same
//! names so its public geometry API stays intact without making a small mating part load the whole
//! machine.
//!
//! The constants are `core-interface`'s (`core_dimensions::interface`), answered in this process
//! from the three fits this module reads off `fits`, and set into the namespace in the reading's
//! key order (`globals().update(_values)`). Every one is a float. Their design notes:
//!
//! - `extrusion_w`: the outer-wall bead selected by the enclosure print profile.
//! - `funnel_collar_air`, `y_stack_high_depth`: the funnel pocket and upper Y seam stack share these
//!   shell interface dimensions.
//! - `rear_plane_y`: the rear inner face leaves the cold core 1.01 mm behind the full aft valve tray.
//! - `show_edge_r`, `show_corner_r`: the visible enclosure rounds. Broad body corners use twice the
//!   shoulder radius; hand openings keep an R6 inside corner and roll onto the wall with the same R6
//!   shoulder as the top, making their outside outline R12.
//! - `pump_station_lead`: signed pump-to-deck offset. The manifold subtracts it from the
//!   pump-outlet station and adds it to the placement span, leaving the fixed tee deck on its own
//!   plane. The pump skirt's slipped opening leaves 3 mm of cradle behind it at the common
//!   cartridge back.
//! - `pump_station_drop`: THE PUMPS' VERTICAL SERVICE DATUM. In `manifold_layout`'s authored frame
//!   the pump depth axis is Y; `enclosure_assembly` stands that axis on world Z. This shift
//!   therefore moves only the two pumps and the four barb ends downward in the installed machine.
//!   The manifold has its own independent rise, carried by its tees, valve seats and stationary
//!   tube endpoints.
//! - `pump_seated_drop`: the physical flange rests on the unchanged skirt lands below the holder's
//!   station datum. The extra micron is the upper-well Boolean overlap, also used by
//!   cap_drop_start_z.
//! - `inner_limb_drop`: the two source limbs, including their tees and aft valves, sit below the
//!   outer limbs. WHAT THE FIGURE IS FOR is the funnel: V-A and V-B stand coil-up directly under its
//!   sloping floor, and the drop clears the bowl's ramp above them. The current cavity volume is
//!   recorded in zone-c/funnel/integration-review/forward-expansion-check.json. The drop follows the
//!   measured Beduan's own height — the coil reaches 52.1 mm above the bearing face its posts are
//!   pressed to — and `clearance-floor` reads what is left between the two.
//! - `flute_depth`, `flute_rise`, `flute_full_depth_height`: THE FIELD THE BOX'S SHOW FACES CARRY,
//!   in the two figures a piece that does NOT carry it still has to know. The fade is driven by how
//!   far a station stands from the nearest edge of the show face (`cadlib/flute_skin._depth_field`),
//!   so a band's own two faces are both edges and the deepest station on a band of height h stands
//!   h / 2 from one — full depth only once that clears `flute_rise`. `flute_full_depth_height` is
//!   that threshold, and the pieces let into the box's faces read it to say which side of it they
//!   fall on: `display_cover.display-cover-reveal`. `enclosure.py` cuts the field with the same two.
//! - `heatset_len`, `heatset_long_len`: THE INSERT'S OWN BODY, both lengths ruthex sells in M3
//!   (RX-M3Sx4.0, where a station cannot give the long body its depth; RX-M3x5.7, everywhere a
//!   station can). They are the same insert otherwise — same ⌀4.6 knurl over the same ⌀4.0
//!   recommended hole — so a station picks between them on the depth of its own bore and nothing
//!   else, and `heatset_dia` serves either. A BORE IS NOT AN INSERT. `heatset_depth` is the POCKET:
//!   the body plus the relief a screw that outruns it needs. Anything asking how much thread a
//!   screw actually takes reads a length here and not that.
//! - `heatset_min_wall`: ruthex RX-M3Sx4.0 / RX-M3x5.7, measured from the Ø4 pilot.
//! - `mount_boss_dia`: 2 mm radial stock, including the supported-face bore allowance; a boss whose
//!   ligament is under `heatset_min_wall` raises "an M3 mounting boss needs ruthex's minimum
//!   surrounding wall".
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_enclosure_interface";

/// The module's typed state: the `core-interface` reading, by name, in its key order.
pub struct State {
    values: Vec<(String, f64)>,
    flute_rise: f64,
    flute_depth: f64,
}
impl State {
    /// One interface dimension (`dims.<name>`).
    pub fn get(&self, name: &str) -> Result<f64> {
        self.values.iter().find(|(key, _)| key == name).map(|(_, value)| *value)
            .with_context(|| format!("module '_enclosure_interface' has no attribute '{name}'"))
    }
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// One interface dimension, as `dims.<name>` reads it.
pub fn value(rt: &Rt, name: &str) -> Result<f64> {
    state(rt)?.get(name)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    // sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents
    //                             if p.name == "printed-parts") / "cadlib"))
    let file = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let printed = file.ancestors().skip(1)
        .find(|p| p.file_name().is_some_and(|name| name == "printed-parts"))
        .context("StopIteration")?;
    py::sys_path_insert(rt, &py::path_str(&printed.join("cadlib")))?;
    let fits = rt.import("fits")?;
    ns.set("fits", fits.clone())?;
    ns.set("_read", rt.member("_enclosure_data", "read")?)?;
    let mut chosen = serde_json::Map::new();
    for name in ["slip", "running", "supported_surface"] {
        chosen.insert(name.into(), py::plain(&fits.attr(name)?)?);
    }
    let reading = rt.enclosure_data(json!({"op": "core-interface", "fits": Value::Object(chosen)}))?;
    let values = py::from_json(reading.clone())?;
    ns.set("_values", values.clone())?;
    // globals().update(_values)
    let mut typed = vec![];
    for (name, value) in reading.as_object().context("core-interface values")? {
        ns.set(name, values.get(py::s(name.as_str()))?)?;
        typed.push((name.clone(), value.as_f64().with_context(|| format!("core-interface {name}"))?));
    }
    let find = |name: &str| typed.iter().find(|(key, _)| key == name).map(|(_, v)| *v)
        .with_context(|| format!("core-interface {name}"));
    let (flute_rise, flute_depth) = (find("flute_rise")?, find("flute_depth")?);
    rt.keep(MODULE, State { values: typed, flute_rise, flute_depth });

    ns.def(rt, "flute_reach", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["band_height"], &[])?;
        flute_reach(rt, &b.req("band_height")?)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// How deep a groove lands on a band `band_height` tall — the field's own expression.
///
/// `flute_skin._depth_field` ramps on `smoothstep(far / flute_rise)`, where `far` is the
/// distance to the nearest edge of the show face; on a band the deepest station stands half
/// the height from either face. So this is what a piece gets for being as tall as it is, and
/// it is the reading a reveal is stated against rather than a number typed beside one.
pub fn flute_reach(rt: &Rt, band_height: &Val) -> Result<Val> {
    let state = state(rt)?;
    let reach = rt.enclosure_data(json!({
        "op": "core-flute-reach",
        "band_height": py::plain(band_height)?,
        "values": {"flute_rise": state.flute_rise, "flute_depth": state.flute_depth},
    }))?;
    py::from_json(reach)
}
