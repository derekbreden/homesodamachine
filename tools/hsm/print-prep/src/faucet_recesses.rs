//! Keeps slicer support out of faucet fastener recesses so their shoulders can bridge.

use anyhow::Result;
use hsm_faucet_numbers::shell::{
    BASE_PEDESTAL_HEIGHT, BASE_POD_CENTERS, BASE_POD_COUNTERBORE_DIA, BASE_POD_SHANK_DIA,
    BASE_SCREW_SEAT_Z,
};
use hsm_faucet_numbers::stack::PLATE_Z;
use serde_json::{Value, json};

use crate::mesh::Mesh;
use crate::project::Plate;
use crate::refresh::Refreshed;

const BLOCKER_SIDES: usize = 64;

pub fn add_blocker(
    plate: &mut Plate,
    index: usize,
    name: &str,
    center: [f64; 2],
    radius: f64,
    depth: [f64; 2],
) -> Result<usize> {
    let origin = plate.objects[index].source_center;
    let mut vertices = Vec::new();
    let mut faces = Vec::new();
    for z in depth {
        vertices.extend((0..BLOCKER_SIDES).map(|i| {
            let theta = std::f64::consts::TAU * i as f64 / BLOCKER_SIDES as f64;
            [
                center[0] + radius * theta.cos() - origin[0],
                center[1] + radius * theta.sin() - origin[1],
                z - origin[2],
            ]
        }));
        vertices.push([center[0] - origin[0], center[1] - origin[1], z - origin[2]]);
    }
    let top = BLOCKER_SIDES + 1;
    for i in 0..BLOCKER_SIDES {
        let j = (i + 1) % BLOCKER_SIDES;
        faces.extend([
            [i, j, j + top],
            [i, j + top, i + top],
            [BLOCKER_SIDES, j, i],
            [top + BLOCKER_SIDES, i + top, j + top],
        ]);
    }
    let mesh = Mesh { vertices, faces };
    mesh.check_closed_single_body(name)?;
    Ok(plate.add_part(
        index,
        name,
        mesh.vertices,
        mesh.faces,
        "support_blocker",
        Vec::new(),
        None,
    ))
}

/// The Sculpted and Industrial mounting plates share the same screw seat and pedestal geometry.
pub fn block_plate_counterbores(
    project: &mut Refreshed,
    part: &str,
    radial_clearance: f64,
    depth_allowance: [f64; 2],
) -> Result<Value> {
    let index = project.row(part)?.index;
    let radius = BASE_POD_COUNTERBORE_DIA / 2.0 + radial_clearance;
    let depth = [
        PLATE_Z[0] - depth_allowance[0],
        BASE_PEDESTAL_HEIGHT + depth_allowance[1],
    ];
    let mut blockers = Vec::new();
    for (i, center) in BASE_POD_CENTERS.into_iter().enumerate() {
        let name = format!("Keep tree support clear of screw counterbore {}", i + 1);
        let id = add_blocker(&mut project.plate, index, &name, center, radius, depth)?;
        blockers.push(json!({"part_id": id, "cad_center_mm": center}));
    }
    Ok(json!({
        "part": part,
        "blockers": blockers,
        "blocker_radius_mm": radius,
        "blocker_cad_z_mm": depth,
        "counterbore_radius_mm": BASE_POD_COUNTERBORE_DIA / 2.0,
        "shank_radius_mm": BASE_POD_SHANK_DIA / 2.0,
        "shoulder_cad_z_mm": BASE_SCREW_SEAT_Z,
    }))
}
