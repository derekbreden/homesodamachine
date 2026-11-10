//! The retained Westbrass reference owns the donor datums used by the manual insertion fixture.
//! Its issued mesh and measurement-source provenance are recorded in frozen-asset.json.
pub const BODY_DIAMETER: f64 = 31.5;
pub const CYLINDER_HEIGHT: f64 = 13.;
pub const TRANSITION_RADIUS: f64 = 6.;
pub const BODY_FLAT_THICKNESS: f64 = 17.;
pub const SHANK_DIAMETER: f64 = 11.;
pub const SHANK_LENGTH: f64 = 50.;
pub const PLATEAU_Z: f64 = 39.;
pub const ARCH_PEAK_Z: f64 = 46.;
pub const PORT_DIAMETER: f64 = 10.;
pub const PORT_EDGE_GAP: f64 = 2.;
pub const PORT_X: f64 = BODY_DIAMETER / 2. - PORT_EDGE_GAP - PORT_DIAMETER / 2.;
pub const PORT_DEPTH: f64 = 20.;
