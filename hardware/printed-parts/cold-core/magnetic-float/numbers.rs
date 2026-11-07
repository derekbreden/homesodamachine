//! The PETG-shell bench float's numbers, in millimetres: an RC62 ring magnet sealed in a clear
//! PETG envelope round an ASA Aero core and insert, the bench and reed test article beside the
//! one-piece Aero float the machine installs. The guide bore is on Z, the finished bottom at Z = 0
//! and the roof above it. The magnet is the RC62 the Aero float's crate describes.
use hsm_aero_float_numbers as aero;
use hsm_cold_core_catalog as catalog;

/// The envelope's diameter, and the open guide bore through it.
pub const DIAMETER: f64 = 36.;
pub const BORE_DIAMETER: f64 = 4.8;
/// The PETG envelope's outer wall, the lining of its bore and its floor under the core.
pub const OUTER_WALL: f64 = 3.;
pub const BORE_WALL: f64 = 1.8;
pub const FLOOR: f64 = 3.;
/// The roof's underside, where the insert's top meets it, and the roof printed over the insert
/// once the pause is over.
pub const ROOF_BOTTOM: f64 = 57.;
pub const ROOF: f64 = 3.06;
/// The finished height.
pub const HEIGHT: f64 = ROOF_BOTTOM + ROOF;
/// The Aero insert, which fills the interior from the core's top to the roof.
pub const INSERT_HEIGHT: f64 = 10.;
/// The chamfer on each Aero piece's two lower edges, as deep as it is high, where its press fit
/// starts.
pub const INSERTION_LEAD: f64 = 0.5;

/// The RC62's faces, its dimensional tolerance and its mass, as the Aero float's crate gives them.
pub const MAGNET_OD: f64 = aero::MAGNET_OD;
pub const MAGNET_ID: f64 = aero::MAGNET_ID;
pub const MAGNET_THICKNESS: f64 = aero::MAGNET_THICKNESS;
pub const MAGNET_TOLERANCE: f64 = aero::MAGNET_TOLERANCE;
pub const MAGNET_MASS: f64 = aero::MAGNET_MASS;
/// The pocket in the core's top that seats the magnet: what it clears the magnet's diameters by,
/// and its depth below the insert.
pub const POCKET_CLEARANCE: f64 = 0.3;
pub const POCKET_DEPTH: f64 = 3.4;
/// The slicer's radial compensation of the core's and the insert's straight lands: each outer
/// contour grown and each bore shrunk by it.
pub const CORE_FIT_ALLOWANCE: f64 = 0.05;
pub const INSERT_FIT_ALLOWANCE: f64 = 0.05;
/// The PETG envelope's density, and the water the float's lift is worked in, in g/cc.
pub const PETG_DENSITY: f64 = 1.25;
pub const WATER_DENSITY: f64 = 1.;

pub const OUTER_RADIUS: f64 = DIAMETER / 2.;
pub const BORE_RADIUS: f64 = BORE_DIAMETER / 2.;
/// The interior the core and the insert fill, inside the envelope's walls.
pub const CORE_OUTER_RADIUS: f64 = OUTER_RADIUS - OUTER_WALL;
pub const CORE_INNER_RADIUS: f64 = BORE_RADIUS + BORE_WALL;
/// The insert's top, at the roof's underside, and its bottom, on the core's top.
pub const INSERT_TOP: f64 = ROOF_BOTTOM;
pub const INSERT_BOTTOM: f64 = INSERT_TOP - INSERT_HEIGHT;
/// The pocket's floor, where the magnet's lower face seats, and its diameters.
pub const MAGNET_SEAT: f64 = INSERT_BOTTOM - POCKET_DEPTH;
pub const POCKET_OD: f64 = MAGNET_OD + POCKET_CLEARANCE;
pub const POCKET_ID: f64 = MAGNET_ID - POCKET_CLEARANCE;

/// The Aero core's colour in the float's files.
pub fn aero_colour() -> catalog::Colour {
    catalog::hex("#EBC777")
}

/// The magnet's colour in the float's files.
pub fn magnet_colour() -> catalog::Colour {
    catalog::hex("#707985")
}
