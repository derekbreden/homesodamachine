//! Where the camera stands, the planes it sees between and the fog it sees through, by the
//! viewer's rules (web/public/js/viewer/scene.js and navigation.js).

use crate::job::{Framing, Job};
use crate::scene::Aabb;
use glam::{DMat4, DVec3, DVec4};

/// The viewer's perspective camera.
pub const FOV_Y_DEG: f64 = 45.0;

#[derive(Clone, Debug)]
pub struct Camera {
    pub ortho: bool,
    pub eye: DVec3,
    pub target: DVec3,
    pub up: DVec3,
    /// Orthographic half-height, in mm.
    pub half: f64,
    pub width: u32,
    pub height: u32,
    pub near: f64,
    pub far: f64,
    /// Fog near and far, in view depth.
    pub fog: (f64, f64),
    view: DMat4,
    proj: DMat4,
}

/// three.js's `Matrix4.lookAt`, including its nudge when `up` lies along the view.
fn look_at(eye: DVec3, target: DVec3, up: DVec3) -> DMat4 {
    let mut z = eye - target;
    if z.length_squared() == 0.0 {
        z.z = 1.0;
    }
    z = z.normalize();
    let mut x = up.cross(z);
    if x.length_squared() == 0.0 {
        if up.z.abs() == 1.0 {
            z.x += 0.0001;
        } else {
            z.z += 0.0001;
        }
        z = z.normalize();
        x = up.cross(z);
    }
    x = x.normalize();
    let y = z.cross(x);
    // The camera's world matrix is [x y z eye]; the view matrix is its inverse.
    let world = DMat4::from_cols(x.extend(0.0), y.extend(0.0), z.extend(0.0), eye.extend(1.0));
    world.inverse()
}

/// A right-handed perspective projection onto wgpu's clip space, depth 0 at `near`, 1 at `far`.
fn perspective(fov_y: f64, aspect: f64, near: f64, far: f64) -> DMat4 {
    let f = 1.0 / (fov_y / 2.0).tan();
    let d = near - far;
    DMat4::from_cols(
        DVec4::new(f / aspect, 0.0, 0.0, 0.0),
        DVec4::new(0.0, f, 0.0, 0.0),
        DVec4::new(0.0, 0.0, far / d, -1.0),
        DVec4::new(0.0, 0.0, near * far / d, 0.0),
    )
}

/// The orthographic one, the same clip space.
fn orthographic(left: f64, right: f64, bottom: f64, top: f64, near: f64, far: f64) -> DMat4 {
    let d = near - far;
    DMat4::from_cols(
        DVec4::new(2.0 / (right - left), 0.0, 0.0, 0.0),
        DVec4::new(0.0, 2.0 / (top - bottom), 0.0, 0.0),
        DVec4::new(0.0, 0.0, 1.0 / d, 0.0),
        DVec4::new(-(right + left) / (right - left), -(top + bottom) / (top - bottom), near / d, 1.0),
    )
}

/// navigation.js `depthRangeFor`.
pub fn depth_range(distance: f64, radius: f64) -> (f64, f64) {
    let near = (distance - radius * 1.25).max(distance * 0.002).max(1e-4);
    (near, (distance + radius * 2.0).max(near * 1.01))
}

/// scene.js `fitFog` at the framing `resetCamera` gives a model: 2.5 of its largest sides away,
/// with the fade complete three radii past the model's back. A picture's fog is a function of
/// the model it shows, not of the camera that shows it.
pub fn fog_range(model: &Aabb) -> (f64, f64) {
    let distance = model.max_dim() * 2.5;
    let radius = model.radius();
    ((distance - radius).max(0.0), distance + radius * 3.0)
}

impl Camera {
    /// Frame `subject` for `job`; the depth planes are fitted to `whole`, everything in the frame.
    pub fn frame(job: &Job, subject: &Aabb, whole: &Aabb, fog_box: &Aabb, width: u32, height: u32) -> Camera {
        let (cam, up) = job.cam_up();
        let center = DVec3::from(subject.center());
        let target = job.target.map(DVec3::from).unwrap_or(center);
        let dir = DVec3::from(cam).normalize_or(DVec3::Z);
        let ortho = job.is_ortho();
        let (radius, margin, zoom) = match job.frame {
            Framing::Posed => (subject.max_dim() * 0.5, 1.1, 3.0),
            Framing::Look => (subject.max_dim().max(1.0) * 0.5, 1.15, 2.5),
        };
        let margin = job.margin.unwrap_or(margin);
        let zoom = job.zoom.unwrap_or(zoom);
        let half = job.span.unwrap_or(radius * margin);
        let distance = job.distance.unwrap_or(match (ortho, job.frame) {
            (true, Framing::Look) => radius.max(half) * 8.0,
            _ => radius * zoom,
        });
        let eye = target + dir * distance;
        let (sphere, sphere_radius) = match &job.depth {
            Some(d) => (DVec3::from(d.center), d.radius),
            None => (DVec3::from(whole.center()), whole.radius()),
        };
        let (near, far) = depth_range(eye.distance(sphere), sphere_radius);
        let mut c = Camera {
            ortho,
            eye,
            target,
            up: DVec3::from(up),
            half,
            width,
            height,
            near,
            far,
            fog: fog_range(fog_box),
            view: DMat4::IDENTITY,
            proj: DMat4::IDENTITY,
        };
        c.update();
        c
    }

    pub fn update(&mut self) {
        self.view = look_at(self.eye, self.target, self.up);
        let aspect = self.aspect();
        self.proj = if self.ortho {
            let h = self.half;
            orthographic(-h * aspect, h * aspect, -h, h, self.near, self.far)
        } else {
            perspective(FOV_Y_DEG.to_radians(), aspect, self.near, self.far)
        };
    }

    pub fn aspect(&self) -> f64 {
        self.width as f64 / self.height as f64
    }

    pub fn view(&self) -> DMat4 {
        self.view
    }

    pub fn proj(&self) -> DMat4 {
        self.proj
    }

    pub fn view_proj(&self) -> DMat4 {
        self.proj * self.view
    }

    /// Unit vector from the scene toward the camera.
    pub fn back(&self) -> DVec3 {
        (self.eye - self.target).normalize_or(DVec3::Z)
    }

    /// World point to pixel (x right, y down) and NDC depth (0 at near, 1 at far).
    pub fn to_screen(&self, p: DVec3) -> (f64, f64, f64) {
        let c = self.view_proj() * DVec4::new(p.x, p.y, p.z, 1.0);
        let n = c.truncate() / c.w;
        (
            (n.x * 0.5 + 0.5) * self.width as f64,
            (-n.y * 0.5 + 0.5) * self.height as f64,
            n.z,
        )
    }

    /// NDC (x, y in -1..1, z in 0..1) back to world.
    pub fn unproject(&self, x: f64, y: f64, z: f64) -> DVec3 {
        let c = self.view_proj().inverse() * DVec4::new(x, y, z, 1.0);
        c.truncate() / c.w
    }

    /// The ray a click at pixel (x, y) casts: origin and unit direction.
    pub fn pixel_ray(&self, x: f64, y: f64) -> (DVec3, DVec3) {
        let nx = x / self.width as f64 * 2.0 - 1.0;
        let ny = -(y / self.height as f64) * 2.0 + 1.0;
        let a = self.unproject(nx, ny, 0.0);
        let b = self.unproject(nx, ny, 1.0);
        (a, (b - a).normalize())
    }

    /// NDC depth of the target, for reading the frame's world rectangle at the target plane.
    pub fn target_depth(&self) -> f64 {
        self.to_screen(self.target).2
    }

    /// Millimetres one pixel spans at the target plane.
    pub fn mm_per_px(&self) -> f64 {
        let z = self.target_depth();
        self.unproject(-1.0, -1.0, z).distance(self.unproject(1.0, -1.0, z)) / self.width as f64
    }

    /// The frame's up in the world: the camera's own Y axis.
    pub fn screen_up(&self) -> DVec3 {
        self.view.inverse().y_axis.truncate()
    }

    pub fn report(&self) -> serde_json::Value {
        let r = |v: DVec3| [v.x, v.y, v.z];
        let mut out = serde_json::json!({
            "projection": if self.ortho { "orthographic" } else { "perspective" },
            "position": r(self.eye),
            "target": r(self.target),
            "up": r(self.up),
            "screen_up": r(self.screen_up()),
            "near": self.near,
            "far": self.far,
            "aspect": self.aspect(),
            "width": self.width,
            "height": self.height,
            "view_proj": self.view_proj().to_cols_array(),
        });
        if self.ortho {
            out["half"] = self.half.into();
        } else {
            out["fov"] = FOV_Y_DEG.into();
        }
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_target_lands_mid_frame() {
        let mut job = Job::default();
        job.cam = Some([1.0, -1.0, 1.0]);
        let b = Aabb { min: [0.0; 3], max: [100.0, 50.0, 80.0] };
        let c = Camera::frame(&job, &b, &b, &b, 1600, 1200);
        let (x, y, z) = c.to_screen(DVec3::from(b.center()));
        assert!((x - 800.0).abs() < 1e-6 && (y - 600.0).abs() < 1e-6 && z > 0.0 && z < 1.0);
    }

    #[test]
    fn the_depth_planes_map_to_zero_and_one() {
        for p in [perspective(0.8, 1.5, 2.0, 50.0), orthographic(-3.0, 3.0, -2.0, 2.0, 2.0, 50.0)] {
            let near = p * DVec4::new(0.3, 0.2, -2.0, 1.0);
            let far = p * DVec4::new(0.3, 0.2, -50.0, 1.0);
            assert!((near.z / near.w).abs() < 1e-12 && (far.z / far.w - 1.0).abs() < 1e-12);
        }
    }

    #[test]
    fn up_along_the_view_is_nudged() {
        let v = look_at(DVec3::new(0.0, 0.0, 10.0), DVec3::ZERO, DVec3::Z);
        assert!(v.is_finite());
    }
}
