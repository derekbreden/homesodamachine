//! The cap's conduits: where each line and cable passes up through the cap, in the cap's own
//! frame. Each stands over the casing's port for it unless the above-core design places its guide
//! on the lid's face, and the lid bores, countersinks or guides it by what the line does there.
use crate::P3;
use crate::design::above_core;
use hsm_cold_core_interface as core;
use hsm_cold_core_layout::cap::{cap_lid_pose, world_to_cap};

/// One conduit: its name and its centre in the cap's own frame.
#[derive(Clone, Copy, Debug)]
pub struct Conduit {
    pub name: &'static str,
    pub xy: [f64; 2],
}

/// The above-core design's guide `name` on the lid's face, in the cap's frame, or `fallback`
/// where the design places none.
fn guide(name: &str, fallback: [f64; 2]) -> [f64; 2] {
    match above_core().cap_guides_world_mm.get(name) {
        Some(&point) => {
            let [x, y, _] = world_to_cap(point);
            [x, y]
        }
        None => fallback,
    }
}

/// A reservoir's port from one of the interface's tables, in the cap's frame: the cap installs
/// spun a half turn on the shell.
fn over_port(table: &[(i64, [f64; 2])], side: i64) -> [f64; 2] {
    let [x, y] = core::reservoir_port(table, side).expect("the interface tables a port on each side");
    [-x, -y]
}

/// Reservoir A's reed ribbon over its reed column, in the cap's frame.
fn reed_cable() -> [f64; 2] {
    [-core::REED_CABLE_CONDUIT_X, -core::REED_CABLE_CONDUIT_Y]
}

/// Every conduit: the carbonator's water in, the reservoirs' draws and fills, the soda out, the
/// CO2 in, reservoir A's reed ribbon and the shared sensor loom.
pub fn conduits() -> Vec<Conduit> {
    let [gas_x, gas_y, _] = world_to_cap(above_core().gas_guide_world_mm);
    vec![
        Conduit { name: "water-in", xy: guide("water-in", core::WATER_IN_CONDUIT_XY) },
        Conduit { name: "reservoir-a", xy: over_port(&core::RESERVOIR_DRAW_PORT, 1) },
        Conduit { name: "reservoir-b", xy: guide("B-draw", over_port(&core::RESERVOIR_DRAW_PORT, -1)) },
        Conduit { name: "reservoir-a-fill", xy: guide("A-fill", over_port(&core::RESERVOIR_FILL_PORT, 1)) },
        Conduit { name: "reservoir-b-fill", xy: over_port(&core::RESERVOIR_FILL_PORT, -1) },
        Conduit { name: "carb-water-out", xy: guide("carb-water-out", core::CARB_WATER_OUT_CONDUIT_XY) },
        Conduit { name: "co2-in", xy: [gas_x, gas_y] },
        Conduit { name: "reed-cable-a", xy: guide("reed-cable-a", reed_cable()) },
        Conduit { name: "sensor-cable", xy: guide("sensor-cable", core::SENSOR_CABLE_CONDUIT_XY) },
    ]
}

/// The bore the lid opens for conduit `name`: the interface's own for the reservoir A fill's wider
/// straight bore, the shared conduit bore for every other.
pub fn bore_radius(name: &str) -> f64 {
    core::CAP_CONDUIT_BORE_RADII
        .iter()
        .find(|(wide, _)| *wide == name)
        .map_or(core::CAP_CONDUIT_BORE_RADIUS, |(_, radius)| *radius)
}

/// The conduits the lid bores straight through, by name: every one but the B fill's, which
/// turns in its holder, and the two that rise in straight guides of their own.
pub fn lid_bores() -> Vec<Conduit> {
    by_name(|name| !matches!(name, "reservoir-b-fill" | "water-in" | "carb-water-out"))
}

/// The conduits whose mouth on the lid's face is countersunk for a line leaving at a lean, by
/// name: every one but the B fill's, the water in's, the sensor loom's, which stays upright until
/// clear of the lid, and those with a wider bore of their own.
pub fn reliefs() -> Vec<Conduit> {
    by_name(|name| {
        !matches!(name, "reservoir-b-fill" | "water-in" | "sensor-cable")
            && !core::CAP_CONDUIT_BORE_RADII.iter().any(|(wide, _)| *wide == name)
    })
}

fn by_name(keep: impl Fn(&str) -> bool) -> Vec<Conduit> {
    let mut kept: Vec<Conduit> = conduits().into_iter().filter(|c| keep(c.name)).collect();
    kept.sort_by_key(|c| c.name);
    kept
}

/// The radial stock round a straight guide's bore.
pub const GUIDE_WALL: f64 = 3.;

/// A line that rises straight through the cup and the lid in a guide of its own: its guide point
/// on the lid's face, from the above-core design, and the cup's floor its bore starts under.
#[derive(Clone, Copy, Debug)]
pub struct StraightGuide {
    pub name: &'static str,
    pub point: P3,
    pub floor: f64,
}

/// The carbonator's water in and soda out, each in its straight guide.
pub fn straight_guides() -> [StraightGuide; 2] {
    let floor = cap_lid_pose().translation[2] - core::top_cap_height(&crate::fits());
    ["water-in", "carb-water-out"].map(|name| StraightGuide {
        name,
        point: above_core().cap_guides_world_mm[name],
        floor,
    })
}
