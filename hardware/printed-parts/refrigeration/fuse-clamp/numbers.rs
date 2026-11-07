//! The fuse clamp's numbers, in millimetres: the printed bracket that pinches the SF76E thermal
//! cutoff's case against the compressor's power box. A head on the box's flank carries the channel
//! the case lies in, a neck runs down the flank to the base plate's crown, and two leaves reach
//! inboard into the air the box hangs over its plate, one on each face of that gap. The cutoff's
//! own frame: X along its axis, Z = 0 on the flank the case seats on with +Z out of it, Y up from
//! the case's axis at the box's mid-height.
use hsm_catalog::fits;

/// The compressor's power box, its standing height, calipered off the donor compressor
/// (`hardware/reference/compressor/README.md`).
pub const POWER_BOX_HEIGHT: f64 = 45.;
/// The air the compressor's power box hangs over its base plate, from its underside to the
/// plate's crown, calipered off the donor compressor.
pub const POWER_BOX_GAP: f64 = 15.;

/// The SF76E's case diameter, from the SEFUSE SF/E series outline in its datasheet
/// (`hardware/reference/sf76e-thermal-fuse/README.md`).
pub const CASE_D: f64 = 4.2;
/// The SF76E's case length, from the same outline.
pub const CASE_L: f64 = 11.;
/// The straight the SF/E datasheet keeps unbent on each of the SF76E's leads, off its case.
pub const LEAD_STUB: f64 = 3.;

/// How far past each lead's unbent straight the channel lets it go.
pub const LEAD_RELEASE: f64 = 0.5;
/// The head's section over the case, past the channel's crown.
pub const CROWN: f64 = 2.5;
/// The band of head that bears on the cover above and below the channel.
pub const HEAD_PAD: f64 = 6.7;
/// The neck's section out of the flank.
pub const NECK_Z: f64 = 3.5;
/// Each leaf's section across the gap.
pub const LEAF_Y: f64 = 2.5;
/// How far each leaf reaches inboard, behind the flank.
pub const LEAF_REACH: f64 = 22.;
/// The chamfer on each leaf's tip that starts it into the gap.
pub const LEAF_LEAD_IN: f64 = 1.5;
/// How far proud of its own diameter the case meets the crown.
pub const CONTACT_TOL: f64 = 0.01;

/// The part's one width along X: the case, and each lead's unbent straight with its release.
pub fn part_x() -> f64 {
    CASE_L + 2. * (LEAD_STUB + LEAD_RELEASE)
}

/// The channel's height along Y: the case with a slip either side, so its walls fence the case
/// and never take the load.
pub fn channel_h() -> f64 {
    CASE_D + 2. * fits().slip
}

/// The channel's depth out of the flank: the case's own diameter, so the crown lands on it.
pub fn channel_z() -> f64 {
    CASE_D
}

/// The head's reach either side of the case's axis.
pub fn head_y() -> f64 {
    channel_h() / 2. + HEAD_PAD
}

/// The head's height out of the flank.
pub fn head_z() -> f64 {
    channel_z() + CROWN
}

/// The box's underside along Y, which the upper leaf bears on.
pub fn box_floor() -> f64 {
    -POWER_BOX_HEIGHT / 2.
}

/// The plate's crown along Y, which the lower leaf bears on.
pub fn plate_top() -> f64 {
    box_floor() - POWER_BOX_GAP
}
