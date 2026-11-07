//! The ASA Aero float's numbers, in millimetres, grams and g/cc: the one-piece guided float with a
//! K&J RC62 ring magnet sealed into it during printing, which the carbonator and the reservoirs
//! guide on a rod. The float's own files, the reservoirs, the reed bridge, the carbonator's end
//! cap and the cold core's assembly take them by name, and the PETG-shell bench float takes the
//! RC62's.
use std::f64::consts::PI;

/// The float's diameter.
pub const DIAMETER: f64 = 36.;
/// What the float clears the tube's inner wall by.
pub const WALL_CLEARANCE: f64 = 2.;
/// Where the float's guide rod stands: its axis, measured in from the tube's inner wall.
pub const ROD_AXIS_FROM_INNER_WALL: f64 = DIAMETER / 2. + WALL_CLEARANCE;

/// The guide bore through the float, and the 1/8" 316 rod it rides.
pub const BORE_DIAMETER: f64 = 4.8;
pub const GUIDE_DIAMETER: f64 = 3.175;
/// How far the float can wander off the rod's axis.
pub const GUIDE_RADIAL_CLEARANCE: f64 = (BORE_DIAMETER - GUIDE_DIAMETER) / 2.;
/// The float's wall clearance at either extreme of that wander.
pub const MINIMUM_WALL_CLEARANCE: f64 = WALL_CLEARANCE - GUIDE_RADIAL_CLEARANCE;
pub const MAXIMUM_WALL_CLEARANCE: f64 = WALL_CLEARANCE + GUIDE_RADIAL_CLEARANCE;

/// The RC62 ring magnet: its faces, its dimensional tolerance and its mass.
pub const MAGNET_OD: f64 = 19.05;
pub const MAGNET_ID: f64 = 9.525;
pub const MAGNET_THICKNESS: f64 = 3.175;
pub const MAGNET_TOLERANCE: f64 = 0.1;
pub const MAGNET_MASS: f64 = 5.09;
/// How far the magnet's rim stands in from the float's.
pub const MAGNET_EDGE_INSET: f64 = (DIAMETER - MAGNET_OD) / 2.;
/// The magnet's colour in the float's files, as sRGB hex. The body takes the catalog's ASA Aero.
pub const MAGNET_COLOUR: &str = "#737D88";

/// The pocket the magnet is dropped into at the print's pause.
pub const POCKET_OD: f64 = 19.35;
pub const POCKET_ID: f64 = 9.225;
pub const POCKET_DEPTH: f64 = 3.6;

/// The sizing inputs: the liquid, the foamed ASA's design density, the lift kept in reserve, and
/// the step the height rounds up by.
pub const WATER_DENSITY: f64 = 0.9997;
pub const DESIGN_FOAM_DENSITY: f64 = 0.65;
pub const MINIMUM_RESERVE_LIFT_G: f64 = 5.;
pub const HEIGHT_INCREMENT: f64 = 1.;

/// The print: its layer, and the slicer's XY compensation of outer contours and of holes.
pub const LAYER_HEIGHT: f64 = 0.2;
pub const XY_CONTOUR_COMPENSATION: f64 = 0.05;
pub const XY_HOLE_COMPENSATION: f64 = -0.05;

/// The float's plan area round its open bore.
pub fn annular_area() -> f64 {
    PI * ((DIAMETER / 2.).powi(2) - (BORE_DIAMETER / 2.).powi(2))
}

/// The magnet pocket's volume.
pub fn pocket_volume() -> f64 {
    PI * ((POCKET_OD / 2.).powi(2) - (POCKET_ID / 2.).powi(2)) * POCKET_DEPTH
}

/// The least height that floats the magnet with the reserve lift to spare.
pub fn minimum_height() -> f64 {
    (MINIMUM_RESERVE_LIFT_G + MAGNET_MASS - DESIGN_FOAM_DENSITY * pocket_volume() / 1000.)
        / ((WATER_DENSITY - DESIGN_FOAM_DENSITY) * annular_area() / 1000.)
}

/// The float's height: the least height, rounded up to the step.
pub fn height() -> f64 {
    (minimum_height() / HEIGHT_INCREMENT).ceil() * HEIGHT_INCREMENT
}

/// The magnet sits on the float's mid-height.
pub fn magnet_midplane() -> f64 {
    height() / 2.
}

/// The pocket's floor, where the magnet's lower face seats.
pub fn magnet_seat() -> f64 {
    magnet_midplane() - MAGNET_THICKNESS / 2.
}

/// The pocket's roof, printed over the magnet once it is in.
pub fn pocket_roof() -> f64 {
    magnet_seat() + POCKET_DEPTH
}

/// The first layer the printer pauses before, to take the magnet: the layer at the pocket's roof.
pub fn pause_before_z() -> f64 {
    (pocket_roof() / LAYER_HEIGHT - 1e-9).ceil() * LAYER_HEIGHT
}

/// What the float displaces, its open bore excluded, in cc.
pub fn displacement_cc() -> f64 {
    annular_area() * height() / 1000.
}

/// The ASA Aero in the float, in cc.
pub fn foam_cc() -> f64 {
    displacement_cc() - pocket_volume() / 1000.
}

/// The finished float's mass at the design density.
pub fn design_mass_g() -> f64 {
    foam_cc() * DESIGN_FOAM_DENSITY + MAGNET_MASS
}

/// Where the magnet's centre stands above the surface, for the float guided upright and dry, of
/// `mass_g` in a liquid of `liquid_density`.
pub fn magnet_above_waterline(mass_g: f64, liquid_density: f64) -> f64 {
    magnet_midplane() - mass_g / (liquid_density * annular_area() / 1000.)
}

/// The conservative distance from a reed's centre to the nearest edge of the magnet (or, with
/// `float_edge`, of the float), the reed and the rod collinear, with the float's play on the rod.
pub fn edge_distance(rod_axis: f64, reed_axis: f64, float_edge: bool) -> f64 {
    let reach = if float_edge { DIAMETER } else { MAGNET_OD };
    (reed_axis - rod_axis).abs() + GUIDE_RADIAL_CLEARANCE - reach / 2.
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_float_comes_out_at_its_printed_height() {
        assert!(WALL_CLEARANCE - GUIDE_RADIAL_CLEARANCE > 1.);
        assert_eq!(height(), 28.);
        assert_eq!(magnet_midplane(), 14.);
    }
}
