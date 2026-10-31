//! Rays into the scene, on the CPU against the payload's own triangles: a click through the frame
//! as the viewer's component picker casts it, and a `--ray`'s run to the first surface.

use crate::camera::Camera;
use crate::scene::{Aabb, Scene};
use glam::DVec3;

#[derive(Clone, Copy, Debug)]
pub struct Hit {
    pub mesh: usize,
    pub point: DVec3,
    pub distance: f64,
}

/// The distances at which the ray enters and leaves the box, if it meets it ahead of `from`.
fn through(b: &Aabb, from: DVec3, dir: DVec3) -> Option<(f64, f64)> {
    let (mut t0, mut t1) = (f64::NEG_INFINITY, f64::INFINITY);
    for a in 0..3 {
        if dir[a] == 0.0 {
            if from[a] < b.min[a] || from[a] > b.max[a] {
                return None;
            }
            continue;
        }
        let (lo, hi) = ((b.min[a] - from[a]) / dir[a], (b.max[a] - from[a]) / dir[a]);
        t0 = t0.max(lo.min(hi));
        t1 = t1.min(lo.max(hi));
    }
    (t0 <= t1 && t1 >= 0.0).then_some((t0, t1))
}

/// three.js `Ray.intersectTriangle`: the distance along the ray to the triangle, if it meets it.
/// `front_only` drops a triangle whose counter-clockwise face looks away from the ray, as a
/// `FrontSide` material's raycast does.
fn triangle(from: DVec3, dir: DVec3, [a, b, c]: [DVec3; 3], front_only: bool) -> Option<f64> {
    let e1 = b - a;
    let e2 = c - a;
    let normal = e1.cross(e2);
    let mut ddn = dir.dot(normal);
    let sign = if ddn > 0.0 {
        if front_only {
            return None;
        }
        1.0
    } else if ddn < 0.0 {
        ddn = -ddn;
        -1.0
    } else {
        return None;
    };
    let diff = from - a;
    let dde2 = sign * dir.dot(diff.cross(e2));
    if dde2 < 0.0 {
        return None;
    }
    let dde1 = sign * dir.dot(e1.cross(diff));
    if dde1 < 0.0 || dde2 + dde1 > ddn {
        return None;
    }
    let qdn = -sign * diff.dot(normal);
    (qdn >= 0.0).then(|| qdn / ddn)
}

/// Every surface the ray meets within `limit` on the meshes `admit` lets through, nearest first.
pub fn cast(
    scene: &Scene,
    from: DVec3,
    dir: DVec3,
    limit: f64,
    front_only: bool,
    admit: impl Fn(usize) -> bool,
) -> Vec<Hit> {
    let mut hits = Vec::new();
    for (mi, mesh) in scene.meshes.iter().enumerate() {
        if !admit(mi) {
            continue;
        }
        match through(&mesh.bbox, from, dir) {
            Some((enter, _)) if enter <= limit => {}
            _ => continue,
        }
        for t in scene.triangles(mi) {
            let corners = t.map(|p| DVec3::new(p[0] as f64, p[1] as f64, p[2] as f64));
            if let Some(d) = triangle(from, dir, corners, front_only)
                && d <= limit
            {
                hits.push(Hit {
                    mesh: mi,
                    point: from + dir * d,
                    distance: d,
                });
            }
        }
    }
    hits.sort_by(|a, b| a.distance.total_cmp(&b.distance));
    hits
}

/// The ray three.js `Raycaster.setFromCamera` casts through pixel (x, y): from the eye for a
/// perspective camera, from the eye's plane straight down the view for an orthographic one.
pub fn pixel_ray(camera: &Camera, x: f64, y: f64) -> (DVec3, DVec3) {
    let nx = x / camera.width as f64 * 2.0 - 1.0;
    let ny = -(y / camera.height as f64) * 2.0 + 1.0;
    let forward = -camera.back();
    if camera.ortho {
        let on_near = camera.unproject(nx, ny, 0.0);
        (on_near - forward * camera.near, forward)
    } else {
        let through = camera.unproject(nx, ny, 0.5);
        (camera.eye, (through - camera.eye).normalize())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_triangle_is_met_from_the_front_and_only_then_when_culling() {
        let t = [DVec3::ZERO, DVec3::X, DVec3::Y];
        let down = DVec3::new(0.0, 0.0, -1.0);
        let d = triangle(DVec3::new(0.2, 0.2, 5.0), down, t, true).unwrap();
        assert!((d - 5.0).abs() < 1e-12);
        assert!(triangle(DVec3::new(0.2, 0.2, -5.0), -down, t, true).is_none());
        assert!(triangle(DVec3::new(0.2, 0.2, -5.0), -down, t, false).is_some());
        assert!(triangle(DVec3::new(0.8, 0.8, 5.0), down, t, false).is_none());
    }

    #[test]
    fn a_box_is_met_ahead_and_missed_behind() {
        let b = Aabb { min: [0.0; 3], max: [1.0; 3] };
        assert!(through(&b, DVec3::new(0.5, 0.5, 3.0), DVec3::new(0.0, 0.0, -1.0)).is_some());
        assert!(through(&b, DVec3::new(0.5, 0.5, 3.0), DVec3::new(0.0, 0.0, 1.0)).is_none());
        assert!(through(&b, DVec3::new(2.0, 0.5, 3.0), DVec3::new(0.0, 0.0, -1.0)).is_none());
    }
}
