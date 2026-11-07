//! The collet press's numbers, in millimetres: the one-piece hand tool whose forked head bears on
//! a John Guest PP0408W's release sleeve while its U-slot passes the 1/4" tube. The handle lies
//! flat on Z = 0 in the print frame and the head rises from it at the head angle. The head's own
//! frame has U along the slot, the slot's closed root at U = 0 and the jaw open toward +U.

/// The PP0408W's figures the press is shaped round, photo-measured off the part in hand
/// (`hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`):
/// the tube its ports take, and the release sleeve's outside and wall.
pub const PORT_DIAMETER: f64 = 6.35;
pub const COLLET_DIAMETER: f64 = 9.57;
pub const COLLET_WALL: f64 = 1.44;

/// The slot's width: past the tube, inside the sleeve's bore.
pub const JAW_GAP: f64 = 6.55;
/// The slot's closed root along U.
pub const JAW_ROOT: f64 = 0.;
/// The head's tilt off the bed.
pub const HEAD_ANGLE: f64 = 45.;
/// The head and the handle: one slab thickness and width.
pub const HEAD_THICKNESS: f64 = 6.;
pub const HEAD_WIDTH: f64 = 20.;
/// The nose's corner radius, also the handle's.
pub const TIP_RADIUS: f64 = 2.;
pub const HANDLE_LENGTH: f64 = 88.;
/// How far the handle runs past the head's top edge, into the head.
pub const HANDLE_REACH: f64 = 2.;
/// How far the handle's clip section overruns it: below and above, and behind its rear end.
pub const CLIP_Z_OVERRUN: f64 = 1.;
pub const CLIP_REAR_OVERRUN: f64 = 2.;

/// The release sleeve's bore, which the jaw has to stay inside.
pub fn collet_bore() -> f64 {
    COLLET_DIAMETER - 2. * COLLET_WALL
}

/// The head's rear edge along U: one arm's width of land behind the slot's root.
pub fn head_back() -> f64 {
    let arm = (HEAD_WIDTH - JAW_GAP) / 2.;
    JAW_ROOT - JAW_GAP / 2. - arm
}

/// The head's nose along U: past the sleeve's outside by the tip's round.
pub fn head_front() -> f64 {
    COLLET_DIAMETER / 2. + TIP_RADIUS
}

/// How far the tilted head is lifted so its rear lower edge buries into the handle.
pub fn head_z_shift() -> f64 {
    let angle = HEAD_ANGLE.to_radians();
    let lower = HEAD_THICKNESS - HEAD_THICKNESS * angle.cos();
    lower - head_back() * angle.sin()
}

/// Where the tilted head's underside stands at height `z`, along X.
pub fn head_underside_x(z: f64) -> f64 {
    (z - head_z_shift()) / HEAD_ANGLE.to_radians().tan()
}

/// The handle's rear and front ends along X: it reaches back from where the head's underside
/// meets the bed, and forward past the head's top edge.
pub fn handle_x() -> [f64; 2] {
    let rear = head_underside_x(0.) - HANDLE_LENGTH;
    [rear, head_underside_x(HEAD_THICKNESS) + HANDLE_REACH]
}

/// The section, in X and Z, the handle is clipped to: square at the rear, along the head's
/// underside at the front.
pub fn handle_clip() -> [[f64; 2]; 4] {
    let (z0, z1) = (-CLIP_Z_OVERRUN, HEAD_THICKNESS + CLIP_Z_OVERRUN);
    let rear = handle_x()[0] - CLIP_REAR_OVERRUN;
    [[rear, z0], [head_underside_x(z0), z0], [head_underside_x(z1), z1], [rear, z1]]
}
