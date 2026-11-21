//! Closed, corbelled casing recesses clear the rear nameplate's insert hosts without opening the foam cavity.
use anyhow::Result;
use hsm_cold_core_interface as core;
use hsm_cold_core_layout::cap;
use hsm_enclosure_numbers::{catalog, layout::layout, nameplate_mount, rear_wall};
use hsm_kernel::{Affine, Plane, Profile, Solid, V3, v2, v3};

/// One insert host's clearance in a casing piece's own frame: the corbelled wall that closes its
/// recess off from the foam, and the recess.
pub struct Clearance {
    pub stock: Solid,
    pub pocket: Solid,
}

/// The clearances of the hosts whose recess reaches `envelope`.
pub fn clearances(envelope: &Solid, local: fn([f64; 3]) -> [f64; 3]) -> Result<Vec<Clearance>> {
    let origin = V3::from(local([0., 0., 0.]));
    let axes = [V3::X, V3::Y, V3::Z].map(|p| V3::from(local([p.x, p.y, p.z])) - origin);
    let frame = Affine::from_columns(axes[0], axes[1], axes[2], origin);
    let n = nameplate_mount::dimensions(rear_wall::PLATE_WIDTH, rear_wall::PLATE_HEIGHT,
        rear_wall::PLATE_THICK, catalog::slip(), catalog::supported(), rear_wall::FIELD_PROUD);
    let mount = &layout().rear_identification.nameplate;
    let seat = mount.face_y_mm - rear_wall::PLATE_THICK;
    let rear = [-1., 1.].into_iter().flat_map(|sx| [-1., 1.].map(move |sy| {
        cap::cap_to_world([sx * core::OUTER_SHELL_X_LENGTH / 2., sy * core::OUTER_SHELL_Y_LENGTH / 2., 0.])[1]
    })).fold(f64::NEG_INFINITY, f64::max);
    let floor = seat + n["insert_stock_rear"].as_f64().unwrap() - catalog::running();
    let radius = n["insert_stock_radius"].as_f64().unwrap() + catalog::running();
    let wall = core::OUTER_SHELL_WALL;
    let depth = rear - (floor - wall);
    let peak = std::f64::consts::SQRT_2;
    let mut found = vec![];
    for station in n["stations"].as_array().unwrap() {
        let x = mount.center_x_mm + station[0].as_f64().unwrap();
        let z = mount.center_z_mm + station[1].as_f64().unwrap();
        let stock = Plane::YZ.at(v3(x - radius - wall, 0., 0.)).extrude(&Profile::polygon(&[
            v2(rear + 0.1, z - radius - wall - depth),
            v2(floor - wall, z - radius - wall),
            v2(floor - wall, z + peak * (radius + wall)),
            v2(rear + 0.1, z + peak * (radius + wall)),
        ]), 2. * (radius + wall))?.transformed(&frame).intersect(envelope)?;
        let pocket = Plane::XZ.at(v3(0., rear + 1., 0.)).extrude(&Profile::polygon(&[
            v2(x - radius, z - radius), v2(x + radius, z - radius),
            v2(x + radius, z + radius * (peak - 1.)), v2(x, z + peak * radius),
            v2(x - radius, z + radius * (peak - 1.)),
        ]), rear + 1. - floor)?.transformed(&frame);
        let p = pocket.bounds();
        let e = envelope.bounds();
        if p.min.x >= e.max.x || p.max.x <= e.min.x
            || p.min.y >= e.max.y || p.max.y <= e.min.y
            || p.min.z >= e.max.z || p.max.z <= e.min.z { continue; }
        found.push(Clearance { stock, pocket });
    }
    Ok(found)
}
