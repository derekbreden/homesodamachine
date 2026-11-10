//! Typed carbonator rod manufacturing datums and jet interfaces supply native tools.
use serde_json::{Value, json};
#[path="../../../../hardware/cold-core-layout/jet_cap_limits.rs"]
mod jet_cap_limits;
pub use jet_cap_limits::{JetCapLimits,JET_CAP_LIMITS};
pub use hsm_carbonator_numbers::jet;

/// Finished carbonator rod and its axial fit requirements, in inches and degrees.
#[derive(Clone, Copy, Debug)]
pub struct RodSpec {
    pub finished_length: f64,
    pub length_tolerance: f64,
    pub diameter_tolerance: f64,
    pub inside_face_span: f64,
    pub inside_face_span_tolerance: f64,
    pub edge_break_maximum: f64,
    pub end_squareness_degrees: f64,
    pub register_depth_tolerance: f64,
    pub register_point_degrees: f64,
    pub register_point_tolerance_degrees: f64,
}

pub const ROD_SPEC: RodSpec = RodSpec {
    finished_length: 5.110,
    length_tolerance: 0.005,
    diameter_tolerance: 0.002,
    inside_face_span: 5.000,
    inside_face_span_tolerance: 0.010,
    edge_break_maximum: 0.003,
    end_squareness_degrees: 0.5,
    register_depth_tolerance: 0.005,
    register_point_degrees: 135.0,
    register_point_tolerance_degrees: 0.5,
};

pub fn rod() -> Value {
    let s = ROD_SPEC;
    json!({"finished_length": s.finished_length, "length_tolerance": s.length_tolerance,
           "diameter_tolerance": s.diameter_tolerance, "inside_face_span": s.inside_face_span,
           "inside_face_span_tolerance": s.inside_face_span_tolerance, "edge_break_maximum": s.edge_break_maximum,
           "end_squareness_degrees": s.end_squareness_degrees, "register_depth_tolerance": s.register_depth_tolerance,
           "register_point_degrees": s.register_point_degrees, "register_point_tolerance_degrees": s.register_point_tolerance_degrees})
}
