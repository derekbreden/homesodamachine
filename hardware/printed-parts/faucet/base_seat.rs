//! Keeps tree support out of a faucet base's mounting insert recesses, gives the base its support
//! settings, and records where its mounting face's seat lies on the plate.

use anyhow::{Context, Result};
use hsm_faucet_numbers::shell::{
    BASE_INSERT_BOTTOM_Z, BASE_POD_CENTERS, BASE_POD_INSERT_DEPTH, BASE_POD_Z_BOTTOM,
    FOOT_CENTER_Y, ZONE1_Z_BOTTOM, base_pod_hole_dia,
};
use hsm_print_prep::faucet_recesses::add_blocker;
use hsm_print_prep::refresh::Refreshed;
use hsm_print_prep::apply;
use serde_json::{Value, json};

fn pair(value: &Value) -> Result<[f64; 2]> {
    Ok([
        value[0].as_f64().context("interval start")?,
        value[1].as_f64().context("interval end")?,
    ])
}

/// The base `name` with its recesses' blockers and `recipe`'s support settings, and the record of
/// its seat.
pub fn add(r: &mut Refreshed, name: &str, recipe: &Value) -> Result<Value> {
    let base = r.row(name)?.index;
    let object = &r.plate.objects[base];
    let source_center = object.source_center;
    let rotation = object.rotation;
    let translation = object.translation;
    let world = |cad: [f64; 3]| {
        let offset = apply(&rotation, [0, 1, 2].map(|i| cad[i] - source_center[i]));
        [0, 1, 2].map(|i| offset[i] + translation[i])
    };
    let seat = [0.0, FOOT_CENTER_Y, ZONE1_Z_BOTTOM];

    let clearance = recipe["insert_blocker_radial_clearance_mm"]
        .as_f64()
        .context("insert blocker clearance")?;
    let [under, over] = pair(&recipe["insert_blocker_depth_allowance_mm"])?;
    let radius = base_pod_hole_dia() / 2.0 + clearance;
    let depth = [
        BASE_POD_Z_BOTTOM - under,
        BASE_INSERT_BOTTOM_Z + BASE_POD_INSERT_DEPTH + over,
    ];
    let mut pockets = Vec::new();
    for (i, center) in BASE_POD_CENTERS.into_iter().enumerate() {
        let name = format!("Keep tree support clear of mounting insert {}", i + 1);
        let id = add_blocker(&mut r.plate, base, &name, center, radius, depth)?;
        pockets.push(json!({"part_id": id, "cad_center_mm": center, "blocker_radius_mm": radius, "blocker_cad_z_mm": depth}));
    }
    let settings = recipe["object_settings"]
        .as_object()
        .context("base support settings")?;
    for (key, value) in settings {
        let value = value
            .as_str()
            .with_context(|| format!("base support setting {key}"))?;
        let settings = &mut r.plate.objects[base].settings;
        settings.retain(|(existing, _)| existing != key);
        settings.push((key.to_owned(), value.to_owned()));
    }
    Ok(json!({
        "part": name,
        "source_preparation": recipe["source_preparation"],
        "seat_print_world_center_mm": world(seat),
        "seat_print_world_outward_normal": apply(&rotation, [0.0, 0.0, -1.0]),
        "bridge_only_pockets": pockets,
        "object_settings": settings,
    }))
}
