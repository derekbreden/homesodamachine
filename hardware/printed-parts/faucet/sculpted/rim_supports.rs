//! Forms the removable supports and keeps support out of the mounting insert recesses.

use anyhow::{Context, Result};
use hsm_faucet_numbers::shell::{
    BASE_INSERT_BOTTOM_Z, BASE_POD_CENTERS, BASE_POD_INSERT_DEPTH, BASE_POD_Z_BOTTOM,
    FOOT_CENTER_Y, FOOT_DEPTH, FOOT_WIDTH, ZONE1_Z_BOTTOM, base_pod_hole_dia,
};
use hsm_print_prep::faucet_contact::closed_rim_strip;
use hsm_print_prep::faucet_recesses::add_blocker;
use hsm_print_prep::mesh::Mesh;
use hsm_print_prep::refresh::Refreshed;
use hsm_print_prep::apply;
use serde_json::{Value, json};

const ANGULAR_STEP_DEGREES: f64 = 1.0;

fn pair(value: &Value) -> Result<[f64; 2]> {
    Ok([
        value[0].as_f64().context("interval start")?,
        value[1].as_f64().context("interval end")?,
    ])
}

/// `roof` adds the enforcer that asks for a support roof along the rim.
pub fn add(r: &mut Refreshed, recipe: &Value, roof: bool) -> Result<Value> {
    let base = r.row("faucet-shell-base")?.index;
    let object = &r.plate.objects[base];
    let source_center = object.source_center;
    let rotation = object.rotation;
    let translation = object.translation;
    let local = |cad: [f64; 3]| [0, 1, 2].map(|i| cad[i] - source_center[i]);
    let world = |cad| {
        let offset = apply(&rotation, local(cad));
        [0, 1, 2].map(|i| offset[i] + translation[i])
    };
    let rim_center = [0.0, FOOT_CENTER_Y, ZONE1_Z_BOTTOM];
    let stock = recipe["reference_rim_diameter_mm"]
        .as_f64()
        .context("reference rim diameter")?;
    let scale = [FOOT_WIDTH / stock, FOOT_DEPTH / stock];
    let rim = |theta: f64, radius: f64, z: f64| {
        let (sin, cos) = theta.to_radians().sin_cos();
        [
            rim_center[0] + scale[0] * radius * cos,
            rim_center[1] + scale[1] * radius * sin,
            z,
        ]
    };
    let angles = |[start, end]: [f64; 2]| {
        let steps = ((end - start) / ANGULAR_STEP_DEGREES).ceil() as usize;
        (0..=steps).map(move |i| start + (end - start) * i as f64 / steps as f64)
    };
    let add = |r: &mut Refreshed, name: &str, mesh: Mesh, subtype: &str| -> Result<usize> {
        mesh.check_closed_single_body(name)?;
        Ok(r.plate.add_part(
            base,
            name,
            mesh.vertices,
            mesh.faces,
            subtype,
            Vec::new(),
            None,
        ))
    };

    let enforcer_angles = pair(&recipe["rim_enforcer_angle_degrees"])?;
    let [inner, outer] = pair(&recipe["rim_enforcer_radius_mm"])?;
    let half = recipe["rim_enforcer_half_height_mm"]
        .as_f64()
        .context("rim enforcer depth")?;
    let low = rim_center[2] - half;
    let high = rim_center[2] + half;
    let sections: Vec<_> = angles(enforcer_angles)
        .map(|theta| {
            [[inner, low], [outer, low], [outer, high], [inner, high]]
                .map(|[radius, z]| local(rim(theta, radius, z)))
        })
        .collect();
    let enforcer = if roof {
        Some(add(
            r,
            "Continuous base rim roof enforcer",
            closed_rim_strip(&sections),
            "support_enforcer",
        )?)
    } else {
        None
    };

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
        "part": "faucet-shell-base",
        "source_preparation": recipe["source_preparation"],
        "cad_xy_scale": scale,
        "seat_print_world_center_mm": world(rim_center),
        "seat_print_world_outward_normal": apply(&rotation, [0.0, 0.0, -1.0]),
        "rim_enforcer_part_id": enforcer,
        "bridge_only_pockets": pockets,
        "object_settings": settings,
    }))
}
