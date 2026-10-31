//! Volume, area, centroid and inertia of a closed triangle mesh, integrated over the
//! tetrahedra its triangles make with the center of its bounds (Eberly, "Polyhedral Mass
//! Properties (Revisited)"). Unit density: the inertia is in mm⁵.
use crate::math::{V3, v3};

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Mass {
    pub volume: f64,
    pub area: f64,
    pub centroid: V3,
    /// About the centroid, along the world's axes.
    pub inertia: [[f64; 3]; 3],
}

fn center(verts: &[V3], tris: &[[u32; 3]]) -> V3 {
    let mut lo = v3(f64::INFINITY, f64::INFINITY, f64::INFINITY);
    let mut hi = -lo;
    for t in tris {
        for &i in t {
            lo = lo.min(verts[i as usize]);
            hi = hi.max(verts[i as usize]);
        }
    }
    if tris.is_empty() { V3::ZERO } else { (lo + hi) * 0.5 }
}

pub fn signed_volume(verts: &[V3], tris: &[[u32; 3]]) -> f64 {
    let o = center(verts, tris);
    tris.iter()
        .map(|t| {
            let (a, b, c) = (verts[t[0] as usize] - o, verts[t[1] as usize] - o, verts[t[2] as usize] - o);
            a.dot(b.cross(c))
        })
        .sum::<f64>()
        / 6.0
}

pub fn area(verts: &[V3], tris: &[[u32; 3]]) -> f64 {
    tris.iter()
        .map(|t| {
            let (a, b, c) = (verts[t[0] as usize], verts[t[1] as usize], verts[t[2] as usize]);
            (b - a).cross(c - a).norm()
        })
        .sum::<f64>()
        * 0.5
}

fn sub(w0: f64, w1: f64, w2: f64) -> [f64; 6] {
    let t0 = w0 + w1;
    let f1 = t0 + w2;
    let t1 = w0 * w0;
    let t2 = t1 + w1 * t0;
    let f2 = t2 + w2 * f1;
    let f3 = w0 * t1 + w1 * t2 + w2 * f2;
    [f1, f2, f3, f2 + w0 * (f1 + w0), f2 + w1 * (f1 + w1), f2 + w2 * (f1 + w2)]
}

pub fn of(verts: &[V3], tris: &[[u32; 3]]) -> Mass {
    let o = center(verts, tris);
    let mut s = [0.0f64; 10];
    for t in tris {
        let (p0, p1, p2) = (verts[t[0] as usize] - o, verts[t[1] as usize] - o, verts[t[2] as usize] - o);
        let (a1, b1, c1) = (p1.x - p0.x, p1.y - p0.y, p1.z - p0.z);
        let (a2, b2, c2) = (p2.x - p0.x, p2.y - p0.y, p2.z - p0.z);
        let (d0, d1, d2) = (b1 * c2 - b2 * c1, a2 * c1 - a1 * c2, a1 * b2 - a2 * b1);
        let x = sub(p0.x, p1.x, p2.x);
        let y = sub(p0.y, p1.y, p2.y);
        let z = sub(p0.z, p1.z, p2.z);
        s[0] += d0 * x[0];
        s[1] += d0 * x[1];
        s[2] += d1 * y[1];
        s[3] += d2 * z[1];
        s[4] += d0 * x[2];
        s[5] += d1 * y[2];
        s[6] += d2 * z[2];
        s[7] += d0 * (p0.y * x[3] + p1.y * x[4] + p2.y * x[5]);
        s[8] += d1 * (p0.z * y[3] + p1.z * y[4] + p2.z * y[5]);
        s[9] += d2 * (p0.x * z[3] + p1.x * z[4] + p2.x * z[5]);
    }
    let k = [1.0 / 6.0, 1.0 / 24.0, 1.0 / 24.0, 1.0 / 24.0, 1.0 / 60.0, 1.0 / 60.0, 1.0 / 60.0, 1.0 / 120.0, 1.0 / 120.0, 1.0 / 120.0];
    for i in 0..10 {
        s[i] *= k[i];
    }
    let m = s[0];
    let c = if m != 0.0 { v3(s[1] / m, s[2] / m, s[3] / m) } else { V3::ZERO };
    let ixx = s[5] + s[6] - m * (c.y * c.y + c.z * c.z);
    let iyy = s[4] + s[6] - m * (c.z * c.z + c.x * c.x);
    let izz = s[4] + s[5] - m * (c.x * c.x + c.y * c.y);
    let ixy = -(s[7] - m * c.x * c.y);
    let iyz = -(s[8] - m * c.y * c.z);
    let ixz = -(s[9] - m * c.z * c.x);
    Mass {
        volume: m,
        area: area(verts, tris),
        centroid: c + o,
        inertia: [[ixx, ixy, ixz], [ixy, iyy, iyz], [ixz, iyz, izz]],
    }
}

#[cfg(test)]
mod tests {
    use crate::math::v3;
    use crate::solid::Solid;

    #[test]
    fn a_box() {
        let m = Solid::cuboid(v3(1.0, 2.0, 3.0), v3(3.0, 5.0, 7.0)).mass();
        assert!((m.volume - 24.0).abs() < 1e-12);
        assert!((m.area - 2.0 * (6.0 + 8.0 + 12.0)).abs() < 1e-12);
        assert!((m.centroid - v3(2.0, 3.5, 5.0)).norm() < 1e-12);
        let ixx = 24.0 * (9.0 + 16.0) / 12.0;
        assert!((m.inertia[0][0] - ixx).abs() < 1e-9);
        assert!(m.inertia[0][1].abs() < 1e-9);
    }
}
