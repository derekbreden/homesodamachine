//! The positioner's bounded host transport, observed response models and dry-run trajectories.
pub mod client;
pub mod kinematics;
pub mod linear;
pub mod noise;
pub mod observe;
pub mod policy;
pub mod servo;
pub mod trajectory;

#[cfg(test)]
mod tests;

use anyhow::Result;
use serde::{Serialize, de::DeserializeOwned};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};

static INTERRUPTED: AtomicBool = AtomicBool::new(false);
pub fn interrupted() -> bool {
    INTERRUPTED.load(Ordering::Relaxed)
}
pub fn interrupt() {
    INTERRUPTED.store(true, Ordering::Relaxed);
}

pub fn read<T: DeserializeOwned>(path: impl AsRef<Path>) -> Result<T> {
    Ok(serde_json::from_slice(&std::fs::read(path)?)?)
}
pub fn write(path: impl AsRef<Path>, value: &impl Serialize) -> Result<()> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    std::fs::write(path, bytes)?;
    Ok(())
}
pub fn digest(value: &impl Serialize) -> Result<String> {
    let value = serde_json::to_value(value)?;
    Ok(format!("{:x}", Sha256::digest(serde_json::to_vec(&value)?)))
}
pub fn root() -> PathBuf {
    let mut root = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    while !root.join("tools/hsm/Cargo.toml").is_file() {
        if !root.pop() {
            return PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../..");
        }
    }
    root
}
