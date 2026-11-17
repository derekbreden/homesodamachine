//! Reservoir B's fill tube where the cap holds it (`hsm_cold_core_layout::b_fill`): the R14
//! holder stays with the tube and fills the lid's window flush with the equipment face.
use crate::P3;
use hsm_cold_core_layout::b_fill::{BEND_RADIUS, CHANNEL_CENTRE, CHANNEL_RADIUS, DOME_LIFT, WALL, passage};
use hsm_cold_core_layout::cap::world_to_cap;

/// The holder's outer radius round the channel's centre.
pub fn outer() -> f64 {
    CHANNEL_RADIUS + WALL
}

/// The full depth from the holder's print bed to the top of its dome.
fn holder_depth() -> f64 {
    CHANNEL_CENTRE + DOME_LIFT + outer()
}

/// The bed-rooted stock in the holder's print frame that fills the window through the lid plate.
pub fn lid_fill_stock() -> [P3; 2] {
    let p = passage();
    let bend_z = p.bend_end[2];
    [
        [p.lid_bottom_z - bend_z, 0., 0.],
        [p.lid_face_z - bend_z, BEND_RADIUS + outer(), holder_depth()],
    ]
}

/// The clearance the lid's window keeps on each side of the holder.
pub const WINDOW_CLEARANCE: f64 = 0.15;

/// The installed holder's bounds in the lid's frame, used to size its mating window.
pub fn holder_bounds() -> [P3; 2] {
    let p = passage();
    let [x, y, z] = p.bend_end;
    let world = [
        [x + CHANNEL_CENTRE - holder_depth(), x + CHANNEL_CENTRE],
        [y - BEND_RADIUS, y + outer()],
        [z, p.lid_face_z],
    ];
    let mut corners = vec![];
    for px in world[0] {
        for py in world[1] {
            for pz in world[2] {
                corners.push(world_to_cap([px, py, pz]));
            }
        }
    }
    crate::vector::bounds(&corners)
}
