//! Print preparation: the Bambu Studio projects the H2C and Mark2 print from, made from the
//! parts' printed meshes and a saved printer recipe, and their offline slices. It never sends a
//! job to a printer.

pub mod audit;
pub mod base_courses;
pub mod cooling;
pub mod course_field;
pub mod derive;
pub mod faucet;
pub mod faucet_contact;
pub mod faucet_recesses;
pub mod faucet_underside;
pub mod feed_cap;
pub mod filled_base;
pub mod gcode;
pub mod ids;
pub mod json;
pub mod mesh;
pub mod npz;
pub mod plate_rings;
pub mod plate_sequence;
pub mod preset;
pub mod profile;
pub mod project;
pub mod python_text;
pub mod refresh;
pub mod review;
pub mod seam;
pub mod rim_contour;
pub mod ring_offset;
pub mod shaft_join_cooling;
pub mod shaft_stitch;
pub mod slice;
pub mod stretch_cooling;
pub mod tip_courses;
pub mod tip_supports;
pub mod tip_warp;
pub mod trial_archive;
pub mod xml;

use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};

pub fn sha256_hex(data: &[u8]) -> String {
    Sha256::digest(data).iter().map(|b| format!("{b:02x}")).collect()
}

/// The checkout, found from the running program or the current directory.
pub fn root() -> PathBuf {
    let start = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    let mut at: &Path = &start;
    loop {
        if at.join("tools/hsm/Cargo.toml").is_file() && at.join("hardware").is_dir() {
            return at.to_path_buf();
        }
        match at.parent() {
            Some(p) => at = p,
            None => return start,
        }
    }
}

/// A rotation about X by `degrees`, as the preparers lay parts on the bed.
pub fn rotation_x(degrees: f64) -> [[f64; 3]; 3] {
    let (s, c) = degrees.to_radians().sin_cos();
    [[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]]
}

pub fn apply(rotation: &[[f64; 3]; 3], v: [f64; 3]) -> [f64; 3] {
    [0, 1, 2].map(|i| rotation[i][0] * v[0] + rotation[i][1] * v[1] + rotation[i][2] * v[2])
}
