//! Forms the removable supports and keeps support out of the mounting insert recesses.

use anyhow::{Context, Result, ensure};
use hsm_faucet_numbers::shell::{
    BASE_INSERT_BOTTOM_Z, BASE_POD_CENTERS, BASE_POD_INSERT_DEPTH, BASE_POD_Z_BOTTOM,
    FOOT_CENTER_Y, FOOT_DEPTH, FOOT_WIDTH, ZONE1_Z_BOTTOM, base_pod_hole_dia,
};
use hsm_print_prep::faucet_recesses::add_blocker;
use hsm_print_prep::mesh::Mesh;
use hsm_print_prep::refresh::Refreshed;
use hsm_print_prep::{apply, faucet::read_json};
use serde_json::{Value, json};
use std::path::Path;

const ANGULAR_STEP_DEGREES: f64 = 1.0;

fn pair(value: &Value) -> Result<[f64; 2]> {
    Ok([
        value[0].as_f64().context("interval start")?,
        value[1].as_f64().context("interval end")?,
    ])
}

fn closed_strip(sections: &[[[f64; 3]; 4]]) -> (Vec<[f64; 3]>, Vec<[usize; 3]>) {
    let vertices = sections.iter().flatten().copied().collect();
    let mut faces = vec![[0, 1, 2], [0, 2, 3]];
    for i in 0..sections.len() - 1 {
        for j in 0..4 {
            let start = 4 * i + j;
            let end = 4 * i + (j + 1) % 4;
            faces.extend([[start, start + 4, end + 4], [start, end + 4, end]]);
        }
    }
    let end = 4 * (sections.len() - 1);
    faces.extend([[end, end + 2, end + 1], [end, end + 3, end + 2]]);
    (vertices, faces)
}

pub fn add(root: &Path, r: &mut Refreshed, recipe: &Value) -> Result<Value> {
    let base = r.row("faucet-shell-base")?.index;
    let object = &r.plate.objects[base];
    let source_center = object.source_center;
    let rotation = object.rotation;
    let inverse = [0, 1, 2].map(|i| [0, 1, 2].map(|j| rotation[j][i]));
    let translation = object.translation;
    let local = |cad: [f64; 3]| [0, 1, 2].map(|i| cad[i] - source_center[i]);
    let world = |cad| {
        let offset = apply(&rotation, local(cad));
        [0, 1, 2].map(|i| offset[i] + translation[i])
    };
    let from_world = |p: [f64; 3]| apply(&inverse, [0, 1, 2].map(|i| p[i] - translation[i]));
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
    let source = recipe["source_preparation"]
        .as_str()
        .context("accepted fin footprint source")?;
    let prior = read_json(&root.join(source))?;
    let setback = recipe["fin_setback_from_model_mm"]
        .as_f64()
        .context("fin setback")?;
    let min_height = recipe["minimum_fin_height_mm"]
        .as_f64()
        .context("minimum fin height")?;
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

    let arcs: &[Value] = if recipe["removable_fins"].as_bool().context("rim fin selection")? {
        prior["rim_arcs"].as_array().context("accepted fin arcs")?
    } else {
        &[]
    };
    let mut fins = Vec::new();
    for (i, arc) in arcs.iter().enumerate() {
        let interval = pair(&arc["cad_angle_interval_degrees"])?;
        let radii = pair(&arc["cad_radius_interval_mm"])?;
        let points = |theta| radii.map(|radius| world(rim(theta, radius, rim_center[2])));
        let fits = |theta| points(theta).iter().all(|p| p[2] >= setback + min_height);
        let mut samples = Vec::new();
        let mut previous = None;
        for theta in angles(interval) {
            let valid = fits(theta);
            if let Some((mut left, was_valid)) = previous {
                if was_valid != valid {
                    let mut right = theta;
                    for _ in 0..36 {
                        let mid = (left + right) / 2.0;
                        if fits(mid) == was_valid {
                            left = mid;
                        } else {
                            right = mid;
                        }
                    }
                    samples.push(if was_valid { left } else { right });
                }
            }
            if valid {
                samples.push(theta);
            }
            previous = Some((theta, valid));
        }
        ensure!(samples.len() >= 2, "fin {} does not clear the bed", i + 1);
        ensure!(
            samples.windows(2).all(|p| fits((p[0] + p[1]) / 2.0)),
            "fin {} splits at the bed",
            i + 1
        );
        let sections: Vec<_> = samples
            .iter()
            .map(|&theta| {
                let [inner, outer] = points(theta);
                let lower = |p: [f64; 3]| from_world([p[0], p[1], 0.0]);
                let upper = |p: [f64; 3]| from_world([p[0], p[1], p[2] - setback]);
                [lower(inner), lower(outer), upper(outer), upper(inner)]
            })
            .collect();
        let (vertices, faces) = closed_strip(&sections);
        let name = format!("Removable base rim fin {}", i + 1);
        let id = add(r, &name, Mesh { vertices, faces }, "normal_part")?;
        fins.push(json!({"part_id": id, "cad_angle_interval_degrees": [samples[0], samples[samples.len() - 1]], "reference_radius_interval_mm": radii}));
    }

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
    let (vertices, faces) = closed_strip(&sections);
    let enforcer = add(
        r,
        "Continuous base rim roof enforcer",
        Mesh { vertices, faces },
        "support_enforcer",
    )?;

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
        "source_preparation": source,
        "cad_xy_scale": scale,
        "seat_print_world_center_mm": world(rim_center),
        "seat_print_world_outward_normal": apply(&rotation, [0.0, 0.0, -1.0]),
        "fin_setback_from_model_mm": setback,
        "fins": fins,
        "rim_enforcer_part_id": enforcer,
        "bridge_only_pockets": pockets,
        "object_settings": settings,
    }))
}
