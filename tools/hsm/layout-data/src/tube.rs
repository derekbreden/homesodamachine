//! The pieces of a tube's centreline, as the layout writes them and the routes stage sweeps them.
use crate::V3;
use serde::{Deserialize, Serialize};

/// One piece of a tube's centreline: a straight run between two points, a circular bend from
/// its first point through its second to its third, or a Bezier curve on its control points.
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum Segment {
    Line { points_mm: [V3; 2] },
    Arc { points_mm: [V3; 3] },
    Bezier { control_points_mm: Vec<V3> },
}
