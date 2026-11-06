//! The four printed quadrants the shell splits into at its Y joint and Z seam.
use crate::Bounds;
use crate::spec::Box;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Y {
    Front,
    Back,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Z {
    Bottom,
    Top,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Quadrant {
    pub y: Y,
    pub z: Z,
}

impl Quadrant {
    pub const FRONT_BOTTOM: Self = Self { y: Y::Front, z: Z::Bottom };
    pub const FRONT_TOP: Self = Self { y: Y::Front, z: Z::Top };
    pub const BACK_BOTTOM: Self = Self { y: Y::Back, z: Z::Bottom };
    pub const BACK_TOP: Self = Self { y: Y::Back, z: Z::Top };

    pub fn name(self) -> &'static str {
        match (self.y, self.z) {
            (Y::Front, Z::Bottom) => "front-bottom",
            (Y::Front, Z::Top) => "front-top",
            (Y::Back, Z::Bottom) => "back-bottom",
            (Y::Back, Z::Top) => "back-top",
        }
    }

    /// The direction each quadrant builds in: back-top prints roof down.
    pub fn up(self) -> f64 {
        if self == Self::BACK_TOP { -1.0 } else { 1.0 }
    }

    /// The Z split this quadrant's column parts at.
    pub fn zj(self, b: &Box) -> f64 {
        if self.y == Y::Front { b.splits[0] } else { b.splits[1] }
    }

    /// The Y and Z bands the quadrant owns: `[y0, y1, z0, z1]`.
    pub fn bands(self, b: &Box) -> [f64; 4] {
        let zj = self.zj(b);
        let (y0, y1) = match self.y {
            Y::Front => (b.outer[2] - 1.0, b.y_joint),
            Y::Back => (b.y_joint, b.outer[3] + 1.0),
        };
        let (z0, z1) = match self.z {
            Z::Bottom => (b.outer[4] - 1.0, zj),
            Z::Top => (zj, b.outer[5] + 1.0),
        };
        [y0, y1, z0, z1]
    }
}

pub fn sorted(a: f64, b: f64) -> (f64, f64) {
    if a <= b { (a, b) } else { (b, a) }
}

/// The interior faces a quadrant's features root on: its flank faces in X and its walls in Y.
pub fn root_faces(inner: &Bounds, q: Quadrant) -> Bounds {
    use crate::faces::*;
    let [_, _, y0, y1, z0, z1] = *inner;
    let ([x0, x1], y1) = match (q.y, q.z) {
        (Y::Front, Z::Top) => (front_top_flank_face(), y1),
        (Y::Back, Z::Top) => (back_top_flank_face(), crate::shell::back_top_wall_face()),
        (Y::Back, Z::Bottom) => (back_bottom_flank_face(), crate::shell::REAR_PLANE_Y - crate::shell::WALL),
        (Y::Front, Z::Bottom) => (front_bottom_flank_face(), y1),
    };
    [x0, x1, y0, y1, z0, z1]
}
