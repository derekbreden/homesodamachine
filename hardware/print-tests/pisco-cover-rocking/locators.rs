//! The trial stops limit cover roll against the rigid rear heels and the front outlet lip.
use anyhow::Result;
use hsm_enclosure_numbers::Bounds;
use hsm_enclosure_numbers::layout::{PISCO_WING_AFT_Y, Station, layout};
use hsm_kernel::{Solid, v3};
use serde_json::{Value, json};

const STOP_GAP: f64 = 0.18;
const JOIN: f64 = 0.4;

/// The west and east posts stand the same distance from the regulator axis.
fn flanks(x: f64, [inner, outer]: [f64; 2], [fore, aft]: [f64; 2], [low, high]: [f64; 2]) -> [Bounds; 2] {
    [[x - outer, x - inner, fore, aft, low, high], [x + inner, x + outer, fore, aft, low, high]]
}

/// The receiver posts stand aft of the free leaves. Each narrows near the heel so the rigid
/// saddle can tilt past the inside edge on entry. The wider shoulder grows from the receiver.
fn rear_bounds(st: &Station) -> ([Bounds; 2], [Bounds; 2]) {
    let fore = PISCO_WING_AFT_Y + 0.9;
    let shoulder_z = st.root + 1.3;
    let tips = flanks(st.axis_x, [11.9, 14.1], [fore, fore + 2.8], [st.root + STOP_GAP, shoulder_z + JOIN]);
    let shoulders = flanks(st.axis_x, [11.38, 14.38], [fore, fore + 3.0], [shoulder_z, st.split + 0.8]);
    (tips, shoulders)
}

/// The front posts grow from the rigid outlet lip and start on the cover's printed end face.
fn front_bounds(st: &Station) -> [Bounds; 2] {
    let lip_z = layout().rear_plumbing.gas_frame.point([0.0; 3])[2];
    flanks(st.axis_x, [8.1, 10.3], [st.y0, st.y0 + 2.1], [lip_z - JOIN, st.split - STOP_GAP])
}

fn join_posts(host: &Solid, bounds: impl IntoIterator<Item = Bounds>) -> Result<Solid> {
    let mut solids = vec![host.clone()];
    for [x0, x1, y0, y1, z0, z1] in bounds {
        solids.push(Solid::cuboid(v3(x0, y0, z0), v3(x1, y1, z1)));
    }
    Solid::union_all(&solids)
}

pub fn rear_stops(base: &Solid, st: &Station) -> Result<Solid> {
    let (tips, shoulders) = rear_bounds(st);
    join_posts(base, tips.into_iter().chain(shoulders))
}

pub fn front_stops(cap: &Solid, st: &Station) -> Result<Solid> {
    join_posts(cap, front_bounds(st))
}

/// The mesh comparison reads the same installed rectangles used to build the posts.
pub fn measurements(st: &Station) -> Value {
    let (tips, shoulders) = rear_bounds(st);
    json!({
        "nominal_gap_z_mm": STOP_GAP,
        "bounds_order": ["xmin", "xmax", "ymin", "ymax", "zmin", "zmax"],
        "rear_heel_top_z_mm": st.root,
        "rear_base_tip_bounds_mm": tips,
        "rear_base_shoulder_bounds_mm": shoulders,
        "front_receiver_flat_z_mm": st.split,
        "front_cover_post_bounds_mm": front_bounds(st)
    })
}
