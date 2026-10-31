//! Vectors, transforms, and the float functions a native and a wasm32 build compute alike:
//! sines, cosines and their inverses are the `libm` crate's.
use std::ops::{Add, AddAssign, Div, Index, Mul, Neg, Sub, SubAssign};

pub const PI: f64 = std::f64::consts::PI;
pub const TAU: f64 = std::f64::consts::TAU;

pub fn sin(x: f64) -> f64 {
    libm::sin(x)
}
pub fn cos(x: f64) -> f64 {
    libm::cos(x)
}
pub fn tan(x: f64) -> f64 {
    libm::tan(x)
}
pub fn acos(x: f64) -> f64 {
    libm::acos(x)
}
pub fn asin(x: f64) -> f64 {
    libm::asin(x)
}
pub fn atan(x: f64) -> f64 {
    libm::atan(x)
}
pub fn atan2(y: f64, x: f64) -> f64 {
    libm::atan2(y, x)
}
pub fn hypot(x: f64, y: f64) -> f64 {
    libm::hypot(x, y)
}
pub fn radians(deg: f64) -> f64 {
    deg * (PI / 180.0)
}
pub fn degrees(rad: f64) -> f64 {
    rad * (180.0 / PI)
}

#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct V2 {
    pub x: f64,
    pub y: f64,
}

#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct V3 {
    pub x: f64,
    pub y: f64,
    pub z: f64,
}

pub const fn v2(x: f64, y: f64) -> V2 {
    V2 { x, y }
}

pub const fn v3(x: f64, y: f64, z: f64) -> V3 {
    V3 { x, y, z }
}

impl V2 {
    pub const ZERO: V2 = v2(0.0, 0.0);
    pub fn dot(self, o: V2) -> f64 {
        self.x * o.x + self.y * o.y
    }
    /// The z of the 3D cross product: positive when `o` turns counterclockwise from `self`.
    pub fn cross(self, o: V2) -> f64 {
        self.x * o.y - self.y * o.x
    }
    pub fn norm(self) -> f64 {
        hypot(self.x, self.y)
    }
    pub fn unit(self) -> V2 {
        self / self.norm()
    }
    /// A quarter turn counterclockwise.
    pub fn perp(self) -> V2 {
        v2(-self.y, self.x)
    }
    pub fn angle(self) -> f64 {
        atan2(self.y, self.x)
    }
    pub fn at_angle(a: f64) -> V2 {
        v2(cos(a), sin(a))
    }
    pub fn lerp(self, o: V2, t: f64) -> V2 {
        self + (o - self) * t
    }
}

impl V3 {
    pub const ZERO: V3 = v3(0.0, 0.0, 0.0);
    pub const X: V3 = v3(1.0, 0.0, 0.0);
    pub const Y: V3 = v3(0.0, 1.0, 0.0);
    pub const Z: V3 = v3(0.0, 0.0, 1.0);
    pub fn dot(self, o: V3) -> f64 {
        self.x * o.x + self.y * o.y + self.z * o.z
    }
    pub fn cross(self, o: V3) -> V3 {
        v3(
            self.y * o.z - self.z * o.y,
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x,
        )
    }
    pub fn norm(self) -> f64 {
        self.dot(self).sqrt()
    }
    pub fn norm2(self) -> f64 {
        self.dot(self)
    }
    pub fn unit(self) -> V3 {
        self / self.norm()
    }
    pub fn min(self, o: V3) -> V3 {
        v3(self.x.min(o.x), self.y.min(o.y), self.z.min(o.z))
    }
    pub fn max(self, o: V3) -> V3 {
        v3(self.x.max(o.x), self.y.max(o.y), self.z.max(o.z))
    }
    pub fn lerp(self, o: V3, t: f64) -> V3 {
        self + (o - self) * t
    }
    pub fn to_array(self) -> [f64; 3] {
        [self.x, self.y, self.z]
    }
    pub fn is_finite(self) -> bool {
        self.x.is_finite() && self.y.is_finite() && self.z.is_finite()
    }
    /// The component of `self` square to the unit vector `d`.
    pub fn reject(self, d: V3) -> V3 {
        self - d * self.dot(d)
    }
}

impl From<[f64; 3]> for V3 {
    fn from(a: [f64; 3]) -> V3 {
        v3(a[0], a[1], a[2])
    }
}
impl From<(f64, f64, f64)> for V3 {
    fn from(a: (f64, f64, f64)) -> V3 {
        v3(a.0, a.1, a.2)
    }
}
impl From<[f64; 2]> for V2 {
    fn from(a: [f64; 2]) -> V2 {
        v2(a[0], a[1])
    }
}
impl From<(f64, f64)> for V2 {
    fn from(a: (f64, f64)) -> V2 {
        v2(a.0, a.1)
    }
}

impl Index<usize> for V3 {
    type Output = f64;
    fn index(&self, i: usize) -> &f64 {
        match i {
            0 => &self.x,
            1 => &self.y,
            2 => &self.z,
            _ => panic!("V3 index {i}"),
        }
    }
}

macro_rules! vec_ops {
    ($t:ident, $($f:ident),+) => {
        impl Add for $t {
            type Output = $t;
            fn add(self, o: $t) -> $t { $t { $($f: self.$f + o.$f),+ } }
        }
        impl Sub for $t {
            type Output = $t;
            fn sub(self, o: $t) -> $t { $t { $($f: self.$f - o.$f),+ } }
        }
        impl Mul<f64> for $t {
            type Output = $t;
            fn mul(self, s: f64) -> $t { $t { $($f: self.$f * s),+ } }
        }
        impl Mul<$t> for f64 {
            type Output = $t;
            fn mul(self, v: $t) -> $t { $t { $($f: self * v.$f),+ } }
        }
        impl Div<f64> for $t {
            type Output = $t;
            fn div(self, s: f64) -> $t { $t { $($f: self.$f / s),+ } }
        }
        impl Neg for $t {
            type Output = $t;
            fn neg(self) -> $t { $t { $($f: -self.$f),+ } }
        }
        impl AddAssign for $t {
            fn add_assign(&mut self, o: $t) { $(self.$f += o.$f;)+ }
        }
        impl SubAssign for $t {
            fn sub_assign(&mut self, o: $t) { $(self.$f -= o.$f;)+ }
        }
    };
}
vec_ops!(V2, x, y);
vec_ops!(V3, x, y, z);

/// An affine map of space: `p' = M p + t`, rows of `m` are `[M | t]`.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Affine {
    pub m: [[f64; 4]; 3],
}

impl Default for Affine {
    fn default() -> Self {
        Affine::IDENTITY
    }
}

impl Affine {
    pub const IDENTITY: Affine = Affine {
        m: [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]],
    };

    pub fn translation(t: V3) -> Affine {
        let mut a = Affine::IDENTITY;
        a.m[0][3] = t.x;
        a.m[1][3] = t.y;
        a.m[2][3] = t.z;
        a
    }

    pub fn scale(s: f64) -> Affine {
        Affine {
            m: [[s, 0.0, 0.0, 0.0], [0.0, s, 0.0, 0.0], [0.0, 0.0, s, 0.0]],
        }
    }

    /// The columns are where the unit axes go, then the translation.
    pub fn from_columns(x: V3, y: V3, z: V3, t: V3) -> Affine {
        Affine {
            m: [[x.x, y.x, z.x, t.x], [x.y, y.y, z.y, t.y], [x.z, y.z, z.z, t.z]],
        }
    }

    /// A turn of `degrees` counterclockwise about the axis through `p` along `d`.
    pub fn rotation(p: V3, d: V3, degrees: f64) -> Affine {
        let k = d.unit();
        let a = radians(degrees);
        let (s, c) = (sin(a), cos(a));
        let t = 1.0 - c;
        let r = [
            [t * k.x * k.x + c, t * k.x * k.y - s * k.z, t * k.x * k.z + s * k.y],
            [t * k.x * k.y + s * k.z, t * k.y * k.y + c, t * k.y * k.z - s * k.x],
            [t * k.x * k.z - s * k.y, t * k.y * k.z + s * k.x, t * k.z * k.z + c],
        ];
        let rot = Affine {
            m: [
                [r[0][0], r[0][1], r[0][2], 0.0],
                [r[1][0], r[1][1], r[1][2], 0.0],
                [r[2][0], r[2][1], r[2][2], 0.0],
            ],
        };
        Affine::translation(p)
            .then_after(&rot)
            .then_after(&Affine::translation(-p))
    }

    /// The reflection through the plane with unit normal `n` through `p`.
    pub fn mirror(p: V3, n: V3) -> Affine {
        let n = n.unit();
        let mut a = Affine::IDENTITY;
        for i in 0..3 {
            for j in 0..3 {
                a.m[i][j] -= 2.0 * n[i] * n[j];
            }
        }
        Affine::translation(p)
            .then_after(&a)
            .then_after(&Affine::translation(-p))
    }

    /// `self ∘ other`: `other` first, then `self`.
    pub fn then_after(&self, other: &Affine) -> Affine {
        let mut out = [[0.0; 4]; 3];
        for (i, row) in out.iter_mut().enumerate() {
            for (j, cell) in row.iter_mut().enumerate() {
                let mut s = 0.0;
                for k in 0..3 {
                    s += self.m[i][k] * other.m[k][j];
                }
                if j == 3 {
                    s += self.m[i][3];
                }
                *cell = s;
            }
        }
        Affine { m: out }
    }

    /// `other ∘ self`: `self` first, then `other`.
    pub fn then(&self, other: &Affine) -> Affine {
        other.then_after(self)
    }

    pub fn point(&self, p: V3) -> V3 {
        let m = &self.m;
        v3(
            m[0][0] * p.x + m[0][1] * p.y + m[0][2] * p.z + m[0][3],
            m[1][0] * p.x + m[1][1] * p.y + m[1][2] * p.z + m[1][3],
            m[2][0] * p.x + m[2][1] * p.y + m[2][2] * p.z + m[2][3],
        )
    }

    pub fn vector(&self, p: V3) -> V3 {
        let m = &self.m;
        v3(
            m[0][0] * p.x + m[0][1] * p.y + m[0][2] * p.z,
            m[1][0] * p.x + m[1][1] * p.y + m[1][2] * p.z,
            m[2][0] * p.x + m[2][1] * p.y + m[2][2] * p.z,
        )
    }

    pub fn det(&self) -> f64 {
        let m = &self.m;
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    }

    /// Where a surface normal goes: the inverse transpose of the linear part, unit length.
    pub fn normal(&self, n: V3) -> V3 {
        let m = &self.m;
        // The cofactor matrix: det times the inverse transpose.
        let c = [
            [
                m[1][1] * m[2][2] - m[1][2] * m[2][1],
                m[1][2] * m[2][0] - m[1][0] * m[2][2],
                m[1][0] * m[2][1] - m[1][1] * m[2][0],
            ],
            [
                m[0][2] * m[2][1] - m[0][1] * m[2][2],
                m[0][0] * m[2][2] - m[0][2] * m[2][0],
                m[0][1] * m[2][0] - m[0][0] * m[2][1],
            ],
            [
                m[0][1] * m[1][2] - m[0][2] * m[1][1],
                m[0][2] * m[1][0] - m[0][0] * m[1][2],
                m[0][0] * m[1][1] - m[0][1] * m[1][0],
            ],
        ];
        let out = v3(
            c[0][0] * n.x + c[0][1] * n.y + c[0][2] * n.z,
            c[1][0] * n.x + c[1][1] * n.y + c[1][2] * n.z,
            c[2][0] * n.x + c[2][1] * n.y + c[2][2] * n.z,
        );
        let u = out.unit();
        if self.det() < 0.0 { -u } else { u }
    }

    /// The uniform scale the map applies to lengths, for radii.
    pub fn length_scale(&self) -> f64 {
        libm::cbrt(self.det().abs())
    }
}
