//! The dock's cuts in front-top's tee wall: each rear valve's port channel carried down to the
//! seam, and each tee's teardropped hole through the fore band and collar-clear bore behind it.
use crate::plan::{Graph, Shape};
use hsm_enclosure_dock_numbers::{RETURN_CHANNEL_R, RETURN_CHANNEL_RISE, TEARDROP_DEG, bore_r, hole_r, plumbing};
use hsm_enclosure_numbers::spec::ColletPlate;

/// Under each rear valve, its port channel carried down through front-top to the seam.
pub fn return_clearances(g: &mut Graph, plate: &ColletPlate) -> Vec<Shape> {
    plate
        .return_ports
        .values()
        .map(|port| {
            let [x, y, z] = port.point;
            g.zcyl(RETURN_CHANNEL_R, x, y, plate.z0 - 1.0, z + RETURN_CHANNEL_RISE)
        })
        .collect()
}

/// Everything the dock takes out of the tee wall: one teardropped hole through the fore band
/// per tee, then one teardropped collar-clear bore per tee from the bore face out through the
/// wall's aft face.
pub fn wall_cuts(g: &mut Graph, plate: &ColletPlate) -> Vec<Shape> {
    let face = plumbing::plate_aft_y(plate.fore_y);
    let mut cuts = Vec::new();
    for (radius, y0, y1) in [(hole_r(), plate.fore_y - 1.0, face + 1.0), (bore_r(), face, plate.wall_aft_y + 1.0)] {
        for &[x, z] in &plate.holes {
            cuts.push(g.teardrop_y(TEARDROP_DEG, radius, x, z, y0, y1, 1.0));
        }
    }
    cuts
}
