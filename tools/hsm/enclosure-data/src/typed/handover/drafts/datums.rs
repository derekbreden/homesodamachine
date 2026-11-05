//! Vectors, planes and placements: the numeric frames the enclosure recipes are written in.
//! They construct no geometry; every solid is a construction recipe (`crate::graph`).
use crate::py;

/// A point or direction; every component is a float.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Vector {
    pub x: f64,
    pub y: f64,
    pub z: f64,
}

impl Vector {
    pub const fn new(x: f64, y: f64, z: f64) -> Self {
        Self { x, y, z }
    }

    pub fn from_tuple(t: [f64; 3]) -> Self {
        Self::new(t[0], t[1], t[2])
    }

    pub fn to_tuple(&self) -> [f64; 3] {
        [self.x, self.y, self.z]
    }

    pub fn add(&self, other: &Vector) -> Vector {
        Vector::new(self.x + other.x, self.y + other.y, self.z + other.z)
    }

    pub fn sub(&self, other: &Vector) -> Vector {
        Vector::new(self.x - other.x, self.y - other.y, self.z - other.z)
    }

    pub fn mul(&self, scale: f64) -> Vector {
        Vector::new(self.x * scale, self.y * scale, self.z * scale)
    }

    /// `v / scale` is `v * (1.0 / scale)`.
    pub fn div(&self, scale: f64) -> Vector {
        self.mul(1.0 / scale)
    }

    pub fn neg(&self) -> Vector {
        self.mul(-1.0)
    }

    /// The sum of products, from zero.
    pub fn dot(&self, other: &Vector) -> f64 {
        0.0 + self.x * other.x + self.y * other.y + self.z * other.z
    }

    pub fn length(&self) -> f64 {
        self.dot(self).sqrt()
    }

    pub fn normalized(&self) -> Vector {
        self.div(self.length())
    }

    pub fn cross(&self, other: &Vector) -> Vector {
        let (a, b, c) = (self.x, self.y, self.z);
        let (d, e, f) = (other.x, other.y, other.z);
        Vector::new(b * f - c * e, c * d - a * f, a * e - b * d)
    }

    pub fn get_angle(&self, other: &Vector) -> f64 {
        let cos = self.dot(other) / (self.length() * other.length());
        py::max2(-1.0, py::min2(1.0, cos)).acos()
    }

    /// `repr(v)`: `Vector(x, y, z)`.
    pub fn repr(&self) -> String {
        format!(
            "Vector({}, {}, {})",
            py::float_text(self.x),
            py::float_text(self.y),
            py::float_text(self.z)
        )
    }
}

/// A plane: an origin and three orthonormal directions.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Plane {
    pub origin: Vector,
    pub x_dir: Vector,
    pub y_dir: Vector,
    pub z_dir: Vector,
}

impl Plane {
    /// `Plane(origin, xDir, normal)`: the normal is normalized and `xDir` made square to it.
    pub fn new(origin: Vector, x_dir: Vector, normal: Vector) -> Plane {
        let z_dir = normal.normalized();
        let x_dir = x_dir.sub(&z_dir.mul(z_dir.dot(&x_dir))).normalized();
        let y_dir = z_dir.cross(&x_dir);
        Plane { origin, x_dir, y_dir, z_dir }
    }

    /// `Plane.named(name, origin)`.
    pub fn named(name: &str, origin: Vector) -> Option<Plane> {
        let (x, z) = match name {
            "XY" => ([1., 0., 0.], [0., 0., 1.]),
            "YZ" => ([0., 1., 0.], [1., 0., 0.]),
            "XZ" => ([1., 0., 0.], [0., -1., 0.]),
            "YX" => ([0., 1., 0.], [0., 0., -1.]),
            "ZY" => ([0., 0., 1.], [-1., 0., 0.]),
            "ZX" => ([0., 0., 1.], [0., 1., 0.]),
            _ => return None,
        };
        Some(Plane::new(origin, Vector::from_tuple(x), Vector::from_tuple(z)))
    }

    /// `plane.toWorldCoords(point)`; a two-value point lies in the plane.
    pub fn to_world(&self, point: &[f64]) -> Vector {
        let p = [point[0], point[1], if point.len() == 2 { 0.0 } else { point[2] }];
        self.origin
            .add(&self.x_dir.mul(p[0]))
            .add(&self.y_dir.mul(p[1]))
            .add(&self.z_dir.mul(p[2]))
    }

    /// `plane.toLocalCoords(point)`.
    pub fn to_local(&self, point: &Vector) -> Vector {
        let p = point.sub(&self.origin);
        Vector::new(p.dot(&self.x_dir), p.dot(&self.y_dir), p.dot(&self.z_dir))
    }

    pub fn location(&self) -> Location {
        Location::from_plane(self)
    }
}

/// A rigid placement: three rows of a rotation and a translation.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Location {
    pub rows: [[f64; 4]; 3],
}

impl Location {
    pub fn identity() -> Location {
        Location::at(&Vector::new(0., 0., 0.), None, 0.0)
    }

    /// `Location(point, axis, angle)`: a rotation of `angle` degrees about `axis`, then `point`.
    pub fn at(point: &Vector, axis: Option<&Vector>, angle: f64) -> Location {
        let rotation = match axis {
            None => [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]],
            Some(axis) => {
                let n = axis.normalized();
                let (x, y, z) = (n.x, n.y, n.z);
                let (c, s) = (py::radians(angle).cos(), py::radians(angle).sin());
                let d = 1.0 - c;
                [
                    [c + x * x * d, x * y * d - z * s, x * z * d + y * s],
                    [y * x * d + z * s, c + y * y * d, y * z * d - x * s],
                    [z * x * d - y * s, z * y * d + x * s, c + z * z * d],
                ]
            }
        };
        let p = point.to_tuple();
        let mut rows = [[0.; 4]; 3];
        for k in 0..3 {
            rows[k] = [rotation[k][0], rotation[k][1], rotation[k][2], p[k]];
        }
        Location { rows }
    }

    /// `Location(plane)`: the plane's directions as columns, its origin as the translation.
    pub fn from_plane(plane: &Plane) -> Location {
        let axes = [plane.x_dir.to_tuple(), plane.y_dir.to_tuple(), plane.z_dir.to_tuple()];
        let origin = plane.origin.to_tuple();
        let mut rows = [[0.; 4]; 3];
        for k in 0..3 {
            rows[k] = [axes[0][k], axes[1][k], axes[2][k], origin[k]];
        }
        Location { rows }
    }

    /// `a * b`: `b`'s placement carried by `a`.
    pub fn mul(&self, other: &Location) -> Location {
        let (a, b) = (&self.rows, &other.rows);
        let mut rows = [[0.; 4]; 3];
        for i in 0..3 {
            for j in 0..3 {
                rows[i][j] = py::sum((0..3).map(|k| a[i][k] * b[k][j]));
            }
            rows[i][3] = a[i][3] + py::sum((0..3).map(|k| a[i][k] * b[k][3]));
        }
        Location { rows }
    }

    /// `location.inverse`.
    pub fn inverse(&self) -> Location {
        let r = &self.rows;
        let mut rows = [[0.; 4]; 3];
        for i in 0..3 {
            for j in 0..3 {
                rows[i][j] = r[j][i];
            }
            rows[i][3] = -py::sum((0..3).map(|j| r[j][i] * r[j][3]));
        }
        Location { rows }
    }

    /// `location.wrapped.Transformation().Value(row, column)`, counted from one.
    pub fn value(&self, row: usize, column: usize) -> f64 {
        self.rows[row - 1][column - 1]
    }
}
