//! Finished jet-cap limits feed the manufacturing drawing and manual assembly guide.
#[derive(Clone, Copy, Debug)]
pub struct JetCapLimits {
    pub od_tolerance: f64,
    pub thickness_tolerance: f64,
    pub bore_plus: f64,
    pub bore_minus: f64,
    pub radial_offset_max: f64,
    pub axis_angle_max: f64,
    pub face_gap_max: f64,
    pub thickness_variation_max: f64,
    pub hole_edge_break_max: f64,
}

pub const JET_CAP_LIMITS: JetCapLimits = JetCapLimits {
    od_tolerance: 0.05,
    thickness_tolerance: 0.2,
    bore_plus: 0.05,
    bore_minus: 0.01,
    radial_offset_max: 0.1,
    axis_angle_max: 1.,
    face_gap_max: 0.05,
    thickness_variation_max: 0.05,
    hole_edge_break_max: 0.05,
};
