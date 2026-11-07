//! Reservoir B's fill tube where the cap holds it (`hsm_cold_core_layout::b_fill`): the R14
//! holder that keeps the tube's turn is a piece of its own and stays with the tube, so the lid
//! leaves a plain window round it.
use crate::P3;
use hsm_cold_core_layout::b_fill::{BEND_RADIUS, CHANNEL_CENTRE, CHANNEL_RADIUS, DOME_LIFT, WALL, passage};
use hsm_cold_core_layout::cap::world_to_cap;

/// The holder's outer radius round the channel's centre.
pub fn outer() -> f64 {
    CHANNEL_RADIUS + WALL
}

/// The air the lid's window keeps round the holder, each side.
pub const WINDOW_CLEARANCE: f64 = 0.15;

/// The installed holder's bounds in the cap's own frame: its domed back's full height out from the
/// turn's end, from its turn to past its channel, and round the bend's height.
pub fn holder_bounds() -> [P3; 2] {
    let [x, y, z] = passage().bend_end;
    let outer = outer();
    let height = CHANNEL_CENTRE + DOME_LIFT + outer;
    let world = [
        [x + CHANNEL_CENTRE - height, x + CHANNEL_CENTRE],
        [y - BEND_RADIUS, y + outer],
        [z + BEND_RADIUS - outer, z + BEND_RADIUS + outer],
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
