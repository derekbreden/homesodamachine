//! Where every triangle came from: the surface it lies on, the operation that made it, and the
//! generator line that asked for it.
use crate::math::{Affine, V3, atan};
use crate::rule::canonical_axis;
use std::fmt;
use std::panic::Location;

/// The generator line that asked for a face, as `#[track_caller]` reports it.
pub type Src = &'static Location<'static>;

/// The exact surface a face lies on. Normals point out of the solid.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Surface {
    Plane { p: V3, n: V3 },
    /// Axis through `p` along unit `d`.
    Cylinder { p: V3, d: V3, r: f64 },
    /// Radius `r` at `p`, growing by `slope` per unit along `d`.
    Cone { p: V3, d: V3, r: f64, slope: f64 },
    Sphere { c: V3, r: f64 },
    /// `major` from the axis to the tube's center, `minor` the tube's radius.
    Torus { c: V3, d: V3, major: f64, minor: f64 },
    /// A surface with no closed form here: an extrusion or revolution of a free curve, a ruled
    /// band, a blend.
    Free { kind: &'static str },
}

/// What two faces share to be one face: the surface, never where it came from. Components are
/// rounded integers, so equal keys hash alike.
#[derive(Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum SurfaceKey {
    Plane([i64; 4]),
    Cylinder([i64; 7]),
    Cone([i64; 7]),
    Sphere([i64; 4]),
    Torus([i64; 8]),
}

fn q(x: f64, decimals: i32) -> i64 {
    (x * 10f64.powi(decimals)).round_ties_even() as i64
}

impl Surface {
    pub fn kind(&self) -> &'static str {
        match self {
            Surface::Plane { .. } => "PLANE",
            Surface::Cylinder { .. } => "CYLINDER",
            Surface::Cone { .. } => "CONE",
            Surface::Sphere { .. } => "SPHERE",
            Surface::Torus { .. } => "TORUS",
            Surface::Free { kind } => kind,
        }
    }

    pub fn is_analytic(&self) -> bool {
        !matches!(self, Surface::Free { .. })
    }

    /// The surface moved by `t`, which may scale uniformly and mirror.
    pub fn transformed(&self, t: &Affine) -> Surface {
        let s = t.length_scale();
        let dir = |d: V3| t.vector(d).unit();
        match *self {
            Surface::Plane { p, n } => Surface::Plane { p: t.point(p), n: t.normal(n) },
            Surface::Cylinder { p, d, r } => Surface::Cylinder { p: t.point(p), d: dir(d), r: r * s },
            Surface::Cone { p, d, r, slope } => Surface::Cone { p: t.point(p), d: dir(d), r: r * s, slope },
            Surface::Sphere { c, r } => Surface::Sphere { c: t.point(c), r: r * s },
            Surface::Torus { c, d, major, minor } => Surface::Torus {
                c: t.point(c),
                d: dir(d),
                major: major * s,
                minor: minor * s,
            },
            Surface::Free { kind } => Surface::Free { kind },
        }
    }

    /// The key coincident surfaces share, or None for a free surface.
    pub fn key(&self) -> Option<SurfaceKey> {
        Some(match *self {
            Surface::Plane { p, n } => {
                let n = canonical_axis(n);
                SurfaceKey::Plane([q(n.x, 6), q(n.y, 6), q(n.z, 6), q(n.dot(p), 5)])
            }
            Surface::Cylinder { p, d, r } => {
                let d = canonical_axis(d);
                let foot = p - d * p.dot(d);
                SurfaceKey::Cylinder([
                    q(d.x, 6),
                    q(d.y, 6),
                    q(d.z, 6),
                    q(foot.x, 4),
                    q(foot.y, 4),
                    q(foot.z, 4),
                    q(r, 5),
                ])
            }
            Surface::Cone { p, d, r, slope } => {
                if slope == 0.0 {
                    return Surface::Cylinder { p, d, r }.key();
                }
                let apex = p - d * (r / slope);
                let dc = canonical_axis(d);
                SurfaceKey::Cone([
                    q(dc.x, 6),
                    q(dc.y, 6),
                    q(dc.z, 6),
                    q(apex.x, 4),
                    q(apex.y, 4),
                    q(apex.z, 4),
                    q(atan(slope).abs(), 6),
                ])
            }
            Surface::Sphere { c, r } => SurfaceKey::Sphere([q(c.x, 4), q(c.y, 4), q(c.z, 4), q(r, 5)]),
            Surface::Torus { c, d, major, minor } => {
                let d = canonical_axis(d);
                SurfaceKey::Torus([
                    q(d.x, 6),
                    q(d.y, 6),
                    q(d.z, 6),
                    q(c.x, 4),
                    q(c.y, 4),
                    q(c.z, 4),
                    q(major, 5),
                    q(minor, 5),
                ])
            }
            Surface::Free { .. } => return None,
        })
    }

    /// The surface's unit normal at (or nearest) `x`, in the record's own sense; None for a
    /// free surface.
    pub fn normal_at(&self, x: V3) -> Option<V3> {
        Some(match *self {
            Surface::Plane { n, .. } => n.unit(),
            Surface::Cylinder { p, d, .. } => (x - p).reject(d).unit(),
            Surface::Cone { p, d, slope, .. } => {
                let out = (x - p).reject(d).unit();
                (out - d * slope).unit()
            }
            Surface::Sphere { c, .. } => (x - c).unit(),
            Surface::Torus { c, d, major, .. } => {
                let v = x - c;
                let h = v.dot(d);
                let radial = v - d * h;
                let w = radial.unit() * (radial.norm() - major) + d * h;
                w.unit()
            }
            Surface::Free { .. } => return None,
        })
    }

    /// Signed distance from `x` to the surface, positive on the side the normal points; None
    /// for a free surface.
    pub fn distance(&self, x: V3) -> Option<f64> {
        Some(match *self {
            Surface::Plane { p, n } => (x - p).dot(n.unit()),
            Surface::Cylinder { p, d, r } => (x - p).reject(d).norm() - r,
            Surface::Cone { p, d, r, slope } => {
                let v = x - p;
                let h = v.dot(d);
                let rho = v.reject(d).norm();
                (rho - r - slope * h) / (1.0 + slope * slope).sqrt()
            }
            Surface::Sphere { c, r } => (x - c).norm() - r,
            Surface::Torus { c, d, major, minor } => {
                let v = x - c;
                let h = v.dot(d);
                let rho = v.reject(d).norm();
                ((rho - major).powi(2) + h * h).sqrt() - minor
            }
            Surface::Free { .. } => return None,
        })
    }
}

/// The boolean that brought a tool's face into a solid.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Via {
    pub op: &'static str,
    pub src: Src,
}

/// One face record: every triangle of a solid names one.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Face {
    pub surface: Surface,
    /// The builder that made the face: "box", "extrude", "revolve", "cylinder", "sweep", …
    pub op: &'static str,
    pub src: Src,
    pub via: Option<Via>,
}

impl Face {
    pub fn new(surface: Surface, op: &'static str, src: Src) -> Face {
        Face { surface, op, src, via: None }
    }

    pub fn transformed(&self, t: &Affine) -> Face {
        Face { surface: self.surface.transformed(t), ..*self }
    }
}

impl fmt::Display for Face {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} {} at {}:{}", self.surface.kind(), self.op, self.src.file(), self.src.line())?;
        if let Some(v) = self.via {
            write!(f, ", {} at {}:{}", v.op, v.src.file(), v.src.line())?;
        }
        Ok(())
    }
}
