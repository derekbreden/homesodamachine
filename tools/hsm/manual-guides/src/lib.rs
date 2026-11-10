//! Manual shop-guide commands bind authored pages and draw their illustrations on demand.
#![recursion_limit = "512"]
#[path = "../../../assembly-guides/artwork.rs"]
pub mod artwork;
#[path = "../../../../hardware/printed-parts/fixtures/tube-insertion/donor-hold-down/donor_hold_down.rs"]
pub mod donor_pad;
#[path = "../../../faucet-assembly-guide/art.rs"]
pub mod faucet_art;
#[path = "../../../faucet-assembly-guide/book.rs"]
pub mod faucet_book;
#[path = "../../../assembly-guides/book.rs"]
pub mod fixed_book;
pub mod float;
pub mod html;
#[path = "../../../water-inlet-jet-guide/book.rs"]
pub mod jet_book;
#[path = "../../../../hardware/markings/build.rs"]
pub mod markings;
#[path = "../../../assembly-guides/guide.rs"]
pub mod paper;
pub mod pdf;
#[path = "../../../gun-positioner-guide/art.rs"]
pub mod pgfun_art;
#[path = "../../../gun-positioner-guide/book.rs"]
pub mod pgfun_book;
#[path = "../../../gun-positioner-guide/qa.rs"]
pub mod pgfun_qa;
#[path = "../../../tube-insertion-guide/art.rs"]
pub mod tube_art;
#[path = "../../../../hardware/printed-parts/fixtures/tube-insertion/tube_insertion.rs"]
pub mod tube_fixture;
#[path = "../../../../hardware/printed-parts/fixtures/tube-insertion/review_geometry.rs"]
pub mod tube_review;

use anyhow::{Context, Result};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};

pub fn root() -> Result<PathBuf> {
    let current = std::env::current_dir()?;
    current
        .ancestors()
        .find(|p| p.join("tools/hsm/Cargo.toml").is_file())
        .map(Path::to_path_buf)
        .context("run from the Home Soda Machine checkout or pass --root")
}

pub fn sha(path: &Path) -> Result<String> {
    Ok(format!(
        "{:x}",
        Sha256::digest(std::fs::read(path).with_context(|| format!("read {}", path.display()))?)
    ))
}

pub fn write(path: &Path, data: &[u8]) -> Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    hsm_documents::write_if_changed(path, data)?;
    Ok(())
}

pub fn write_json(path: &Path, value: &impl serde::Serialize) -> Result<()> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    write(path, &bytes)
}
