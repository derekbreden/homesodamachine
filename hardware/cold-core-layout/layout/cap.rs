//! The cap lid's pose in the enclosure, and the frames it relates: the enclosure's world, the
//! cap's own frame and the shell's. The above-core design (`hardware/manifold-layout/above-core.json`)
//! holds the pose and the face the lid presents; this module reads both from it.
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as core;
use serde::Deserialize;
use std::sync::OnceLock;

/// A rigid placement: rows of a rotation and a translation, as the above-core design writes them.
#[derive(Clone, Copy, Debug, Deserialize, PartialEq)]
pub struct Pose {
    pub rotation: [[f64; 3]; 3],
    #[serde(rename = "translation_mm")]
    pub translation: [f64; 3],
}

fn dot(a: [f64; 3], b: [f64; 3]) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

impl Pose {
    /// A direction carried by the rotation.
    pub fn vector(&self, p: [f64; 3]) -> [f64; 3] {
        [dot(self.rotation[0], p), dot(self.rotation[1], p), dot(self.rotation[2], p)]
    }

    /// A point carried from the pose's own frame into the frame it is placed in.
    pub fn point(&self, p: [f64; 3]) -> [f64; 3] {
        let v = self.vector(p);
        [v[0] + self.translation[0], v[1] + self.translation[1], v[2] + self.translation[2]]
    }

    /// A point carried back into the pose's own frame.
    pub fn inverse_point(&self, p: [f64; 3]) -> [f64; 3] {
        let d = [p[0] - self.translation[0], p[1] - self.translation[1], p[2] - self.translation[2]];
        let mut out = [0.; 3];
        for (j, o) in out.iter_mut().enumerate() {
            for (i, di) in d.iter().enumerate() {
                *o += self.rotation[i][j] * di;
            }
        }
        out
    }
}

#[derive(Deserialize)]
struct AboveCore {
    cap_lid_pose: Pose,
    cap_face_z_mm: f64,
}

fn above_core() -> &'static AboveCore {
    static DESIGN: OnceLock<AboveCore> = OnceLock::new();
    DESIGN.get_or_init(|| {
        serde_json::from_str(include_str!("../../manifold-layout/above-core.json"))
            .expect("the above-core design parses")
    })
}

/// Where the cap lid sits in the enclosure: its underside's centre and its turn.
pub fn cap_lid_pose() -> Pose {
    above_core().cap_lid_pose
}

/// The world height of the lid's top face, which the above-core parts stand on.
pub fn cap_face_z() -> f64 {
    above_core().cap_face_z_mm
}

/// An enclosure point in the cap's own frame.
pub fn world_to_cap(p: [f64; 3]) -> [f64; 3] {
    cap_lid_pose().inverse_point(p)
}

/// A point of the cap's own frame in the enclosure.
pub fn cap_to_world(p: [f64; 3]) -> [f64; 3] {
    cap_lid_pose().point(p)
}

/// An enclosure point in the shell's own frame: the cap installs spun a half turn on the shell,
/// and the lid's underside stands the shell's height and the top cap's cup above the shell's base.
pub fn world_to_shell(p: [f64; 3]) -> [f64; 3] {
    let [x, y, z] = world_to_cap(p);
    [-x, -y, z + core::FOAM_SHELL_OUTER_HEIGHT + core::top_cap_height(&catalog::fits())]
}
