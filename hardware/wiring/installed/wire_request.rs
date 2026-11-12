//! The request the installed wires are cut from: each conductor's centreline and each
//! termination's and jacket's shape, in enclosure millimetres.
use serde::{Deserialize, Serialize};

pub type V = [f64; 3];

/// One piece of a centreline: a straight run, a circular bend through its midpoint, or a spline.
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum Segment {
    Line {
        start_mm: V,
        end_mm: V,
        length_mm: f64,
    },
    Arc {
        start_mm: V,
        midpoint_mm: V,
        end_mm: V,
        radius_mm: f64,
        angle_radians: f64,
        length_mm: f64,
    },
    Spline(Spline),
}

impl Segment {
    /// Where the segment begins.
    pub fn start(&self) -> V {
        match self {
            Segment::Line { start_mm, .. } | Segment::Arc { start_mm, .. } => *start_mm,
            Segment::Spline(spline) => spline.start_mm,
        }
    }

    /// Where the segment ends.
    pub fn end(&self) -> V {
        match self {
            Segment::Line { end_mm, .. } | Segment::Arc { end_mm, .. } => *end_mm,
            Segment::Spline(spline) => spline.end_mm,
        }
    }

    /// The segment's length along its curve.
    pub fn length(&self) -> f64 {
        match self {
            Segment::Line { length_mm, .. } | Segment::Arc { length_mm, .. } => *length_mm,
            Segment::Spline(spline) => spline.length_mm,
        }
    }
}

/// A clamped spline through its interpolation points, with what was measured along it: its
/// length, points at even steps of that length and its tightest bend.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Spline {
    pub start_mm: V,
    pub end_mm: V,
    pub interpolation_points_mm: Vec<V>,
    pub endpoint_tangents: [V; 2],
    pub endpoint_derivatives: [V; 2],
    pub parameters: Vec<f64>,
    pub length_mm: f64,
    pub sampled_points_mm: Vec<V>,
    pub maximum_sample_step_mm: f64,
    pub minimum_bend_mm: Option<f64>,
}

/// A cylinder from its base centre along its axis.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Cylinder {
    pub radius_mm: f64,
    pub height_mm: f64,
    pub base_mm: V,
    pub axis: V,
}

/// Where an imported reference stands: the rows of its rotation, then its translation.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Pose {
    pub rotation: [V; 3],
    pub translation_mm: V,
}

/// The shape of a termination or a jacket.
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum Shape {
    /// A reference STEP of the checkout, posed.
    Import { step: String, pose: Pose },
    /// A ring terminal: its eye less its bore, with its barrel, on the plane at `origin_mm`.
    Ring {
        eye: Cylinder,
        bore: Cylinder,
        barrel: Cylinder,
        origin_mm: V,
        x_dir: V,
        normal: V,
    },
    /// A connector housing: a block on the plane at `origin_mm`, less a bore for each pin.
    Housing {
        origin_mm: V,
        x_dir: V,
        normal: V,
        dimensions_mm: V,
        bores: Vec<Cylinder>,
    },
    /// A round lead swept along its segments.
    Sweep {
        connection_id: String,
        points_mm: Vec<V>,
        segments: Vec<Segment>,
        diameter_mm: f64,
    },
    /// A splice sleeve: its outer cylinder less its inner one.
    Sleeve { outer: Cylinder, inner: Cylinder },
    /// A cable jacket: an annulus swept along its segments.
    AnnularSweep {
        points_mm: Vec<V>,
        segments: Vec<Segment>,
        diameter_mm: f64,
        inner_diameter_mm: f64,
    },
}

/// A conductor: its insulated diameter, its colour and its centreline.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Wire {
    pub name: String,
    pub diameter_mm: f64,
    pub linear_rgb: V,
    pub segments: Vec<Segment>,
}

/// A termination or a jacket: its colour and its shape.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Part {
    pub name: String,
    pub linear_rgb: V,
    #[serde(flatten)]
    pub shape: Shape,
}

/// Everything the installed wires are cut from, and the names and tolerances they are written
/// under.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Request {
    pub name: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub file_stem: Option<String>,
    pub presentation_deflection_ratio: f64,
    pub presentation_angular_deflection_rad: f64,
    pub routes: Vec<Wire>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub components: Vec<Part>,
}
