//! Exact constructions and predicates on the kernel's binary grid.
//!
//! Positions remain homogeneous integers while topology is decided. Approximations may guide
//! searches, but do not decide incidence or orientation. Checked inline arithmetic grows into
//! heap limbs when exact constructions or transforms need more precision.
//!
//! This module has no production dispatch. Converting a constructed point to a grid coordinate
//! is a numeric operation; it does not by itself establish a valid rounded mesh.
#![allow(dead_code)]

mod arrange;
mod classify;
mod int;
mod integer;
mod meet;
mod pairs;
mod point;
mod predicate;
mod state;

pub(crate) use arrange::{Patch, arrange};
pub(crate) use classify::{Decision, Kind, RayMesh, classify};
pub(crate) use int::Int;
pub(crate) use integer::Integer;
pub(crate) use meet::{Contact, meet};
pub(crate) use pairs::{Pair, pairs};
pub(crate) use point::{GridFrame, GridPoint, Plane, Point, Quantized};
pub(crate) use predicate::{orient2d, orient3d, side_of_plane};
pub(crate) use state::{Affine, Mesh, Origin, Triangle};

/// The inline arithmetic has 1024 magnitude bits. Larger exact values use heap limbs.
pub(crate) type Wide = Int<16>;
pub(crate) type Result<T> = std::result::Result<T, Error>;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) enum Error {
    Overflow,
    ZeroDivisor,
    InexactDivision,
    NonFiniteCoordinate,
    CoordinateRange,
    DegenerateTriangle,
    NonUniqueIntersection,
    NonPositiveWeight,
    InvalidAxis,
    SingularTransform,
    InvalidMeshIndex,
    InvalidArrangement,
    CrossingConstraints,
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(match self {
            Error::Overflow => "the exact integer capacity was exceeded",
            Error::ZeroDivisor => "exact division by zero",
            Error::InexactDivision => "an exact integer division has a remainder",
            Error::NonFiniteCoordinate => "an exact operand has a non-finite coordinate",
            Error::CoordinateRange => "an exact operand is outside the supported grid range",
            Error::DegenerateTriangle => "an exact operand has a degenerate triangle",
            Error::NonUniqueIntersection => "the exact intersection is not a unique point",
            Error::NonPositiveWeight => "an exact point has a non-positive homogeneous weight",
            Error::InvalidAxis => "an exact predicate has an invalid projection axis",
            Error::SingularTransform => "an exact affine map is singular",
            Error::InvalidMeshIndex => "an exact triangle names a missing vertex",
            Error::InvalidArrangement => "an exact triangle arrangement is inconsistent",
            Error::CrossingConstraints => "exact constraints cross without a registered vertex",
        })
    }
}

impl std::error::Error for Error {}

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub(crate) enum Sign {
    Negative,
    Zero,
    Positive,
}

impl Sign {
    pub(crate) fn reversed(self) -> Self {
        match self {
            Self::Negative => Self::Positive,
            Self::Zero => Self::Zero,
            Self::Positive => Self::Negative,
        }
    }
}
