//! A solid carried by an affine map that need not keep its shape — a shear, a stretch along one
//! axis — as CadQuery's `transformGeometry` carries one (OCCT's `BRepBuilderAPI_GTransform`).
//!
//! The mesh goes point for point. A plane stays a plane, its normal carried by the inverse
//! transpose. A cylinder, cone, sphere or torus keeps its kind under a similarity only; under
//! any other map its face becomes a free surface, a B-spline, as OCCT makes every face it
//! carries.
use crate::face::{Face, Surface};
use crate::math::Affine;
use crate::solid::Solid;
use anyhow::{Result, ensure};

impl Solid {
    /// Carried by `t`, any affine map that does not flatten space.
    pub fn mapped(&self, t: &Affine) -> Result<Solid> {
        ensure!(t.det().abs() > 1e-12, "an affine map that flattens space");
        if similarity(t) {
            return Ok(self.transformed(t));
        }
        let verts = self.verts.iter().map(|&p| t.point(p)).collect();
        let tris = if t.det() < 0.0 {
            self.tris.iter().map(|&[a, b, c]| [a, c, b]).collect()
        } else {
            self.tris.clone()
        };
        let faces = self
            .faces
            .iter()
            .map(|f| Face {
                surface: match f.surface {
                    Surface::Plane { p, n } => Surface::Plane { p: t.point(p), n: t.normal(n) },
                    _ => Surface::Free { kind: "BSPLINE" },
                },
                ..*f
            })
            .collect();
        Ok(Solid::raw(verts, tris, self.face_of.clone(), faces))
    }
}

/// Whether `t` scales every length alike: its linear part's columns are square to each other and
/// of one length.
fn similarity(t: &Affine) -> bool {
    let c = |j: usize| [t.m[0][j], t.m[1][j], t.m[2][j]];
    let dot = |a: [f64; 3], b: [f64; 3]| a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    let (x, y, z) = (c(0), c(1), c(2));
    let s = dot(x, x);
    let tol = 1e-12 * s.max(1.0);
    (dot(y, y) - s).abs() <= tol
        && (dot(z, z) - s).abs() <= tol
        && dot(x, y).abs() <= tol
        && dot(y, z).abs() <= tol
        && dot(z, x).abs() <= tol
}
