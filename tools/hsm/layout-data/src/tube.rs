//! A tube as the layout routes it: the pieces of its centreline, its stock, and the ports and
//! bodies it joins.
use crate::V3;
use serde::{Deserialize, Serialize};

/// One piece of a tube's centreline: a straight run between two points, a circular bend from
/// its first point through its second to its third, or a Bezier curve on its control points.
/// A bend the layout lays out states its circle as well.
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum Segment {
    Line {
        points_mm: [V3; 2],
    },
    Arc {
        points_mm: [V3; 3],
        #[serde(default, skip_serializing_if = "Option::is_none")]
        radius_mm: Option<f64>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        center_mm: Option<V3>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        axis: Option<V3>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        angle_rad: Option<f64>,
    },
    Bezier {
        control_points_mm: Vec<V3>,
    },
}

impl Segment {
    /// The bend from `start` through `middle` to `end`.
    pub fn through(start: V3, middle: V3, end: V3) -> Segment {
        Segment::Arc {
            points_mm: [start, middle, end],
            radius_mm: None,
            center_mm: None,
            axis: None,
            angle_rad: None,
        }
    }

    /// The points the segment is given by: a line's ends, a bend's three points, a curve's
    /// controls.
    pub fn points(&self) -> &[V3] {
        match self {
            Segment::Line { points_mm } => points_mm,
            Segment::Arc { points_mm, .. } => points_mm,
            Segment::Bezier { control_points_mm } => control_points_mm,
        }
    }
}

/// A radius a tube's record states as a number or as none, where the record states it at all.
mod stated {
    use serde::{Deserialize, Deserializer, Serialize, Serializer};

    pub fn serialize<S: Serializer>(value: &Option<Option<f64>>, to: S) -> Result<S::Ok, S::Error> {
        value.flatten().serialize(to)
    }

    pub fn deserialize<'de, D: Deserializer<'de>>(from: D) -> Result<Option<Option<f64>>, D::Error> {
        Option::<f64>::deserialize(from).map(Some)
    }
}

/// A tube between two ports: its centreline's segments and points along it, its stock, the
/// ports and bodies it joins, and what the plan says of it.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Tube {
    pub segments: Vec<Segment>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub points_mm: Option<Vec<V3>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub centerline_mm: Option<Vec<V3>>,
    pub od_mm: f64,
    pub id_mm: f64,
    pub spool: String,
    #[serde(default, skip_serializing_if = "Option::is_none", with = "stated")]
    pub radius_mm: Option<Option<f64>>,
    #[serde(default, skip_serializing_if = "Option::is_none", with = "stated")]
    pub minimum_radius_mm: Option<Option<f64>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub radius_basis: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub from: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub frm: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub to: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub owners: Option<Vec<String>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub status: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub basis: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub note: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub color: Option<V3>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub length_mm: Option<f64>,
}

impl Tube {
    /// A tube of the given stock along `segments`, with nothing else stated of it.
    pub fn of(segments: Vec<Segment>, od_mm: f64, id_mm: f64, spool: &str) -> Tube {
        Tube {
            segments,
            points_mm: None,
            centerline_mm: None,
            od_mm,
            id_mm,
            spool: spool.to_owned(),
            radius_mm: None,
            minimum_radius_mm: None,
            radius_basis: None,
            from: None,
            frm: None,
            to: None,
            owners: None,
            status: None,
            basis: None,
            note: None,
            color: None,
            length_mm: None,
        }
    }

    /// The tube with `points` stated as both its points and its centreline.
    pub fn through(mut self, points: Vec<V3>) -> Tube {
        self.centerline_mm = Some(points.clone());
        self.points_mm = Some(points);
        self
    }
}
