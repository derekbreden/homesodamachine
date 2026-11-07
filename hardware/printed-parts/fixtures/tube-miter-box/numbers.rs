//! The tube miter box's numbers, in millimetres: a block with two open troughs, one for 1/4" and
//! one for 3/8" tube, crossed by a razor slot that guides a single-edge blade square through the
//! tube. Print frame: X along the troughs' pitch, Y along the troughs, +Z up from the bed.
use hsm_catalog::fits;

const INCH: f64 = 25.4;
/// The two tubes the troughs take.
pub const TUBE_OD_SMALL: f64 = INCH / 4.;
pub const TUBE_OD_LARGE: f64 = INCH * 3. / 8.;
/// The single-edge razor blade: its length, height and thickness, and the spine it is held by.
pub const RAZOR_BLADE_L: f64 = 1.5 * INCH;
pub const RAZOR_BLADE_H: f64 = 0.75 * INCH;
pub const RAZOR_BLADE_T: f64 = 0.009 * INCH;
pub const RAZOR_SPINE_H: f64 = 5.;
/// The razor slot: its width and length, its depth below the block's top and the floor under it.
pub const SLOT_W: f64 = 0.8;
pub const SLOT_L: f64 = 40.;
pub const SLOT_DEPTH: f64 = 15.;
pub const FLOOR_UNDER_SLOT: f64 = 3.;
/// The walls at each end of the slot.
pub const END_WALL: f64 = 5.;
/// The block either side of the slot: the off-cut's side and the side that is kept.
pub const OFFCUT_SIDE: f64 = 5.;
pub const KEEP_SIDE: f64 = 19.;
/// The troughs' spacing, and how far their floor stands above the slot's.
pub const TROUGH_PITCH: f64 = 20.;
pub const TROUGH_FLOOR_ABOVE_SLOT_FLOOR: f64 = 2.5;

/// The block's size along X, Y and Z.
pub fn block() -> [f64; 3] {
    [SLOT_L + 2. * END_WALL, OFFCUT_SIDE + SLOT_W + KEEP_SIDE, FLOOR_UNDER_SLOT + SLOT_DEPTH]
}

/// The slot's two faces along Y.
pub fn slot_y() -> [f64; 2] {
    [OFFCUT_SIDE, OFFCUT_SIDE + SLOT_W]
}

/// The troughs' floor above the bed.
pub fn trough_floor() -> f64 {
    FLOOR_UNDER_SLOT + TROUGH_FLOOR_ABOVE_SLOT_FLOOR
}

/// Each trough's centre along X and its radius: the tube's, on the running fit.
pub fn troughs() -> [[f64; 2]; 2] {
    let running = fits().running();
    [
        [-TROUGH_PITCH / 2., TUBE_OD_SMALL / 2. + running],
        [TROUGH_PITCH / 2., TUBE_OD_LARGE / 2. + running],
    ]
}

/// The razor at the end of its stroke, its box from X, Y and Z low to high: the spine down on the
/// block's top, the edge below the troughs' floor.
pub fn razor_bounds() -> [f64; 6] {
    let [y0, y1] = slot_y();
    let y = (y0 + y1) / 2.;
    let top = block()[2];
    let edge = top - (RAZOR_BLADE_H - RAZOR_SPINE_H);
    [-RAZOR_BLADE_L / 2., RAZOR_BLADE_L / 2., y - RAZOR_BLADE_T / 2., y + RAZOR_BLADE_T / 2., edge, top]
}
