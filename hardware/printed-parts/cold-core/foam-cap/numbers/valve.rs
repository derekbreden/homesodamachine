//! V-B's upright wall on the lid: one integral block whose face carries the valve's four blind
//! sockets and its port channel, as the valve seat cuts them, rooted on the lid's face within the
//! core's footprint. The above-core design places the valve and fixes the wall's west backing
//! plane and its top.
use crate::P3;
use crate::design::above_core;
use crate::vector::bounds;
use hsm_cold_core_interface as core;
use hsm_cold_core_layout::cap::{Pose, cap_lid_pose};
use hsm_valve_seat_numbers as seat;

/// V-B's pose in the enclosure: the valve's frame, its posts' ends at Z = 0 and its port on Y.
pub fn pose() -> Pose {
    above_core().parts.valve_v_b.pose()
}

/// The wall's two blocks, in the enclosure: the bearing block the sockets are cut in, and the root
/// under it down to the lid's face; how deep the root runs along Y, and the stock behind each
/// socket's floor.
#[derive(Clone, Copy, Debug)]
pub struct Wall {
    pub bearing: [P3; 2],
    pub root: [P3; 2],
    pub root_depth: f64,
    pub socket_backing: f64,
}

/// V-B's wall, rooted on the lid's face.
pub fn wall() -> Wall {
    let slip = crate::fits().slip;
    let pose = pose();
    let limits = [
        [-seat::half_x(slip), seat::half_x(slip)],
        [-seat::half_y(slip), seat::half_y(slip)],
        [seat::SOCKET_FLOOR_Z - seat::WALL, seat::SEAT_TOP_Z],
    ];
    let mut corners = vec![];
    for x in limits[0] {
        for y in limits[1] {
            for z in limits[2] {
                corners.push(pose.point([x, y, z]));
            }
        }
    }
    let [low, high] = bounds(&corners);
    let fixed = above_core().vb_mount.seat_wall_bounds_mm;
    let low = [fixed[0][0], low[1], low[2]];
    let high = [high[0], high[1], high[2].max(fixed[1][2])];
    let face = cap_lid_pose().point([0., 0., core::foam_cap_lid_height(&crate::fits())])[2];
    // The root keeps inside the core's footprint across the enclosure's X.
    let half = core::OUTER_SHELL_Y_LENGTH / 2.;
    let root_high = [half.min(high[0]), high[1], low[2]];
    Wall {
        bearing: [low, high],
        root: [[(-half).max(low[0]), low[1], face], root_high],
        root_depth: root_high[1] - low[1],
        socket_backing: seat::WALL,
    }
}
