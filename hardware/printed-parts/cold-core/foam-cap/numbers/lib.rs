//! The foam cap's numbers, in millimetres: the equipment lid on the cold core's crown, the
//! open-topped closure under the core, the R14 holder reservoir B's fill tube turns in, and the
//! pump's snap cap; the lid's conduits and the mounts it carries for the parts above the core; and
//! reservoir A's two lid anchors. A point is in the enclosure's frame unless its doc says the cap's
//! own: the lid before the half turn it installs with. The cold core's assemblies take the cap's
//! heights and its mounts from here.
//!
//! The lid's and the cup's heights are the interface's (`foam_cap_lid_height`, `top_cap_height`),
//! as are the casing's footprint, the clamp stations and the deck mounts' stock.
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as core;
use hsm_reservoir_numbers as reservoir;

pub mod b_fill;
pub mod cables;
pub mod clips;
pub mod conduits;
pub mod deck;
mod design;
pub mod pump;
pub mod reservoir_a;
pub mod unions;
pub mod valve;
mod vector;
pub mod wells;

pub use design::{Can, Placed, PumpMount};
pub use hsm_cold_core_layout::cap::Pose;

/// A point or a direction.
pub type P3 = [f64; 3];

/// The fits the cap is cut to.
pub fn fits() -> core::Fits {
    catalog::fits()
}

/// Every piece prints in black glass-filled PETG.
pub fn colour() -> catalog::Colour {
    catalog::petgf_black()
}

/// How far the bottom closure's head pads grow past the clamp bosses, so its open head pockets
/// keep the casing's full inward wall round them.
pub fn head_pad_growth() -> f64 {
    (core::HEAD_CBORE_RADIUS + core::WALL_THICKNESS - core::SCREW_BOSS_SIZE / 2.).max(0.)
}

/// How deep a cut through the lid runs: the lid and one floor past it.
pub fn lid_cut_through_depth() -> f64 {
    core::foam_cap_lid_height(&fits()) + core::WALL_AND_FLOOR_THICKNESS
}

/// The stack's floor in the shell's frame: the bottom closure's outer face, which the appliance
/// stands the core on.
pub fn stack_floor_z() -> f64 {
    -(core::FOAM_CAP_HEIGHT + core::WALL_AND_FLOOR_THICKNESS)
}

/// The lid's top face in the shell's frame: the plane the crown's parts are placed off and the
/// conduits open on. The stack rises past it where V-B's wall and the pump cradle stand.
pub fn face_z() -> f64 {
    core::cap_face_z(&fits())
}

/// The bottom closure's two vent holes, in the −X corners mirrored across Y, clear of the pour
/// holes: air leaves by whichever stands uppermost.
pub fn vent_xy() -> [[f64; 2]; 2] {
    let x = -(core::OUTER_SHELL_X_LENGTH / 2. - core::FOAM_CAP_LID_HOLE_INSET);
    let y = core::OUTER_SHELL_Y_LENGTH / 2. - core::FOAM_CAP_LID_HOLE_INSET;
    [[x, y], [x, -y]]
}

/// A round hole through a piece: its centre in the piece's frame and its radius.
#[derive(Clone, Copy, Debug)]
pub struct Hole {
    pub xy: [f64; 2],
    pub radius: f64,
}

/// The bottom closure's holes: the interface's pour holes, then the vents.
pub fn bottom_holes() -> Vec<Hole> {
    let mut holes: Vec<Hole> = core::bottom_pour_positions()
        .into_iter()
        .map(|xy| Hole { xy, radius: core::BOTTOM_POUR_RADIUS })
        .collect();
    holes.extend(vent_xy().map(|xy| Hole { xy, radius: core::FOAM_CAP_LID_VENT_RADIUS }));
    holes
}

/// The passages the lid leaves the reservoirs' air tubes, over each one's port, the lid spun a
/// half turn on the shell.
pub fn air_holes() -> Vec<Hole> {
    reservoir::AIR_PORT
        .iter()
        .map(|(_, xy)| Hole { xy: [-xy[0], -xy[1]], radius: reservoir::AIR_PASSAGE_DIAMETER / 2. })
        .collect()
}

/// The world-to-cap frame: where the enclosure's origin lands in the cap's frame, and where each
/// of the enclosure's axes points in it.
pub fn world_to_cap() -> (P3, [P3; 3]) {
    use hsm_cold_core_layout::cap::world_to_cap as carry;
    let origin = carry([0., 0., 0.]);
    let axes = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]].map(|axis| vector::sub(carry(axis), origin));
    (origin, axes)
}
