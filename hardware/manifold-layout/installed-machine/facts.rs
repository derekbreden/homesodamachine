//! The machine's facts: the written-down interior's fields, the placed bodies' bounds, the ports
//! the fittings present, the runs as drawn and the stations the BOM, the fluid diagrams and the
//! install guide read.
use crate::design;
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::path::Path;

/// The Box fields the facts carry, in the order they are read.
const BOX_FIELDS: [&str; 6] = ["inner", "outer", "funnel", "floor_bosses", "cond_mount", "collet_plate"];

/// The bodies whose ports the facts list.
const PORT_BODIES: [&str; 15] = [
    "asse1022-assembly", "bulkhead-carb", "bulkhead-drain", "bulkhead-flavor-a", "bulkhead-flavor-b",
    "bulkhead-water", "digiten-flow", "discharge-reducer", "foam-assembly", "gas-check", "gas-regulator",
    "jg-pp061208w", "suction-reducer", "vk-solenoid", "water-split",
];

/// The facts of the plan `spec`, with the stations taken from the written-down above-core layout,
/// and what the wiring is built without where there is anything.
pub fn facts(
    root: &Path,
    spec: &Value,
    floor_grommet_squeeze: f64,
    not_wired: &[crate::wiring::NotRouted],
) -> Result<Value> {
    let above = design::read(root.join("hardware/manifold-layout/above-core.json"))?;
    let c14 = &above["parts"]["c14-inlet"]["translation_mm"];
    let keystone = &above["rear_wall"]["dry_openings"]["keystone"]["face_center_mm"];
    let station = |at: &Value| -> Result<Value> {
        Ok(json!([at.get(0).context("a station's x")?, at.get(2).context("a station's z")?]))
    };
    let request = json!({
        "spec": spec,
        "box_fact_order": BOX_FIELDS,
        "card_port_bodies": PORT_BODIES,
        "constants": {
            "C14_STATION": station(c14)?,
            "FLOOR_GROMMET_SQUEEZE": floor_grommet_squeeze,
            "KEYSTONE_STATION": station(keystone)?,
        },
    });
    let mut facts = crate::reporting::facts(&request)?;
    if !not_wired.is_empty() {
        let rows: Vec<Value> = not_wired
            .iter()
            .map(|wire| json!({"id": wire.id, "frm": wire.from, "to": wire.to, "why": wire.reason}))
            .collect();
        facts["wiring_not_routed"] = json!(rows);
    }
    Ok(facts)
}
