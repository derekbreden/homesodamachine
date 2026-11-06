//! The numbers each piece's evaluator reads beside its construction plan.
use crate::plan::{Bounds, P2};
use serde::{Deserialize, Serialize};

/// YZ stations of the front round, the display plane and the round onto the roof.
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Profile {
    pub foot: P2,
    pub front_mid: P2,
    pub start: P2,
    pub end: P2,
    pub top_mid: P2,
    pub roof: P2,
    pub origin: [f64; 3],
    pub normal: [f64; 3],
}

/// One section of the side-edge fill at the curved display top.
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct FillSection {
    pub x: f64,
    pub centre: P2,
    pub ellipse: [f64; 3],
    pub inner_radius: f64,
    pub start: P2,
    pub top_tangent: P2,
    pub inner_end: P2,
    pub inner_mid: P2,
    pub inner_start: P2,
    pub upper_roof: P2,
    pub lower_roof: P2,
    pub upper_aft: P2,
    pub lower_aft: P2,
}

/// The structure numbers every quadrant's evaluator reads beside its graph.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Structure {
    pub outer: Bounds,
    pub profile: Profile,
    pub standing_radius: f64,
    pub side_radius: f64,
    pub angle: f64,
    pub roof_fill_sections: [Vec<FillSection>; 2],
    pub roof_transition: RoofTransition,
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct RoofTransition {
    pub height: f64,
    pub foot: f64,
    pub outward_per_height: f64,
}

/// The print rail's frames round the closed plan perimeter.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Rail {
    pub s: Vec<f64>,
    pub point: Vec<P2>,
    pub normal: Vec<P2>,
    pub closed: bool,
    pub band: Option<P2>,
    /// The plain lands the flutes stop short of.
    pub plain: Vec<Bounds>,
}

/// The field's tolerances and the flutes' pitch, width, depth and rise.
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Field {
    pub across: f64,
    pub along: f64,
    pub margin: f64,
    pub overrun: f64,
    pub plan_tol: f64,
    pub face_tol: f64,
    pub pitch: f64,
    pub width: f64,
    pub depth: f64,
    pub rise: f64,
}

/// A body's colour, linear RGB, as its files carry it.
pub type Color = [f64; 3];

/// The back-bottom print's raised warning field: the wall it relieves and how far the letters
/// stand proud of its margin.
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct BackBottomPrint {
    pub wall: f64,
    pub warning_margin: f64,
    pub warning_raise: f64,
}

/// The back-top print's raised lands: how far each sinks into the wall, the rails' raised
/// bounds beside the nameplate field, and the sliding channels kept clear of their skin.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BackTopPrint {
    pub embed: f64,
    pub label_channels: Vec<Bounds>,
    pub raised_bounds: Vec<Bounds>,
}

/// One front corner's frame: its origin and the hand of its X axis.
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct CornerFrame {
    pub origin: [f64; 3],
    pub x_sign: f64,
}

/// One rational B-spline patch of the retained front corner, in its unit frame.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CornerSurface {
    pub degree: [usize; 2],
    pub knots: [Vec<f64>; 2],
    pub multiplicities: [Vec<usize>; 2],
    pub poles: Vec<Vec<[f64; 3]>>,
    pub weights: Vec<Vec<f64>>,
    pub source_step_entity: u64,
}

/// The analytic front corner drawn on front-top's rounded body, scaled into each frame.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FrontCorners {
    pub frames: Vec<CornerFrame>,
    pub scale_mm: f64,
    pub surfaces: Vec<CornerSurface>,
}
