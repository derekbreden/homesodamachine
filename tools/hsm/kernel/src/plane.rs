//! Workplanes: an origin and a right-handed frame, the named ones as CadQuery names them.
use crate::math::{Affine, V2, V3, v2, v3};
use anyhow::{Result, ensure};

/// `x` and `y` span the plane and `z` is its normal; `y = z × x`.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Plane {
    pub origin: V3,
    pub x: V3,
    pub y: V3,
    pub z: V3,
}

impl Plane {
    /// The plane through `origin` with normal `z`, its x axis `x_dir` made square to `z`.
    pub fn new(origin: V3, x_dir: V3, z: V3) -> Result<Plane> {
        let z = z.unit();
        let x = x_dir - z * x_dir.dot(z);
        ensure!(z.is_finite() && x.norm() > 1e-12, "a plane needs a normal and an x axis across it");
        let x = x.unit();
        Ok(Plane { origin, x, y: z.cross(x), z })
    }

    const fn named(x: V3, z: V3) -> Plane {
        // y = z × x, written out for the axis-aligned frames below.
        let y = v3(z.y * x.z - z.z * x.y, z.z * x.x - z.x * x.z, z.x * x.y - z.y * x.x);
        Plane { origin: V3::ZERO, x, y, z }
    }

    pub const XY: Plane = Plane::named(v3(1.0, 0.0, 0.0), v3(0.0, 0.0, 1.0));
    pub const YZ: Plane = Plane::named(v3(0.0, 1.0, 0.0), v3(1.0, 0.0, 0.0));
    pub const ZX: Plane = Plane::named(v3(0.0, 0.0, 1.0), v3(0.0, 1.0, 0.0));
    pub const XZ: Plane = Plane::named(v3(1.0, 0.0, 0.0), v3(0.0, -1.0, 0.0));
    pub const YX: Plane = Plane::named(v3(0.0, 1.0, 0.0), v3(0.0, 0.0, -1.0));
    pub const ZY: Plane = Plane::named(v3(0.0, 0.0, 1.0), v3(-1.0, 0.0, 0.0));
    pub const FRONT: Plane = Plane::named(v3(1.0, 0.0, 0.0), v3(0.0, 0.0, 1.0));
    pub const BACK: Plane = Plane::named(v3(-1.0, 0.0, 0.0), v3(0.0, 0.0, -1.0));
    pub const LEFT: Plane = Plane::named(v3(0.0, 0.0, 1.0), v3(-1.0, 0.0, 0.0));
    pub const RIGHT: Plane = Plane::named(v3(0.0, 0.0, -1.0), v3(1.0, 0.0, 0.0));
    pub const TOP: Plane = Plane::named(v3(1.0, 0.0, 0.0), v3(0.0, 1.0, 0.0));
    pub const BOTTOM: Plane = Plane::named(v3(1.0, 0.0, 0.0), v3(0.0, -1.0, 0.0));

    /// A named plane — "XY", "YZ", "ZX", "XZ", "YX", "ZY", "front", "back", "left", "right",
    /// "top", "bottom" — through `origin`.
    pub fn by_name(name: &str, origin: V3) -> Result<Plane> {
        let p = match name {
            "XY" => Plane::XY,
            "YZ" => Plane::YZ,
            "ZX" => Plane::ZX,
            "XZ" => Plane::XZ,
            "YX" => Plane::YX,
            "ZY" => Plane::ZY,
            "front" => Plane::FRONT,
            "back" => Plane::BACK,
            "left" => Plane::LEFT,
            "right" => Plane::RIGHT,
            "top" => Plane::TOP,
            "bottom" => Plane::BOTTOM,
            _ => anyhow::bail!("no plane named {name:?}"),
        };
        Ok(p.at(origin))
    }

    /// The same frame through `origin`.
    pub fn at(&self, origin: V3) -> Plane {
        Plane { origin, ..*self }
    }

    /// Moved `d` along its normal.
    pub fn offset(&self, d: f64) -> Plane {
        self.at(self.origin + self.z * d)
    }

    /// Its origin moved to the point at `p` in its own coordinates.
    pub fn shifted(&self, p: V2) -> Plane {
        self.at(self.point(p))
    }

    /// Turned `degrees` about its own normal.
    pub fn spun(&self, degrees: f64) -> Plane {
        let r = Affine::rotation(V3::ZERO, self.z, degrees);
        Plane { origin: self.origin, x: r.vector(self.x), y: r.vector(self.y), z: self.z }
    }

    /// The point at `p` in the plane's own coordinates.
    pub fn point(&self, p: V2) -> V3 {
        self.origin + self.x * p.x + self.y * p.y
    }

    /// The point `p` in the plane's own coordinates and its height above it.
    pub fn local(&self, p: V3) -> (V2, f64) {
        let r = p - self.origin;
        (v2(r.dot(self.x), r.dot(self.y)), r.dot(self.z))
    }

    /// The map from the plane's own coordinates to the world's.
    pub fn to_world(&self) -> Affine {
        Affine::from_columns(self.x, self.y, self.z, self.origin)
    }

    /// The plane moved by `t`.
    pub fn transformed(&self, t: &Affine) -> Plane {
        let x = t.vector(self.x).unit();
        let z = t.normal(self.z);
        Plane { origin: t.point(self.origin), x, y: z.cross(x), z }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn named_planes_are_right_handed() {
        for p in [
            Plane::XY,
            Plane::YZ,
            Plane::ZX,
            Plane::XZ,
            Plane::YX,
            Plane::ZY,
            Plane::FRONT,
            Plane::BACK,
            Plane::LEFT,
            Plane::RIGHT,
            Plane::TOP,
            Plane::BOTTOM,
        ] {
            assert_eq!(p.x.cross(p.y), p.z);
        }
        assert_eq!(Plane::YZ.point(v2(2.0, 3.0)), v3(0.0, 2.0, 3.0));
        assert_eq!(Plane::XZ.y, v3(0.0, 0.0, 1.0));
    }
}
