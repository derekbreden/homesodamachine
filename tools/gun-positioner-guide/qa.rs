//! An explicit PGFUN release review binds the shop book, print archive and current geometry record.
use anyhow::{Context, Result, ensure};
use serde::Deserialize;
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::process::Command;

#[derive(Deserialize)]
struct Release {
    geometry_sha256: String,
    artifacts: BTreeMap<String, String>,
}
#[derive(Deserialize)]
struct Geometry {
    sha256: String,
}
#[derive(Deserialize)]
struct Receipt {
    geometry_sha256: String,
    #[serde(alias = "sources")]
    source_sha256: BTreeMap<String, String>,
    pdf_sha256: String,
    pages: usize,
}
#[derive(Deserialize)]
struct Part {
    name: String,
    sha256: String,
}
#[derive(Deserialize)]
struct Parts {
    parts: Vec<Part>,
}
#[derive(Deserialize)]
struct Item {
    subtotal: f64,
    prime: bool,
}
#[derive(Deserialize)]
struct Purchases {
    mechanism: Vec<Item>,
    observation: Vec<Item>,
}
#[derive(Deserialize)]
struct Clearance {
    geometry_sha256: String,
    unintended_intersections: Vec<Value>,
}
fn read<T: serde::de::DeserializeOwned>(path: PathBuf) -> Result<T> {
    serde_json::from_slice(&std::fs::read(&path)?)
        .with_context(|| format!("read PGFUN release source {}", path.display()))
}
fn sha(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}
fn peripheral() -> Result<PathBuf> {
    if let Some(path) = std::env::var_os("HSM_PERIPHERAL") {
        return Ok(path.into());
    }
    let sibling = std::env::current_exe()?.with_file_name("hsm-peripheral");
    if sibling.is_file() {
        return Ok(sibling);
    }
    Ok(PathBuf::from("hsm-peripheral"))
}

pub fn review(root: &Path) -> Result<()> {
    let cad = root.join("hardware/printed-parts/fixtures/pgfun-positioner");
    let doc = root.join("hardware/gun-positioner");
    let guide = root.join("hardware/gun-positioner-guide");
    let release: Release = read(doc.join("release-manifest.json"))?;
    let geometry: Geometry = read(cad.join("motion-geometry.json"))?;
    ensure!(
        release.geometry_sha256 == geometry.sha256,
        "PGFUN release geometry differs from the current binding"
    );
    for (path, expected) in &release.artifacts {
        ensure!(
            crate::sha(&root.join(path))? == *expected,
            "PGFUN release artifact changed: {path}"
        );
    }
    let receipt: Receipt = read(guide.join("source-receipt.json"))?;
    ensure!(
        receipt.geometry_sha256 == geometry.sha256,
        "PGFUN guide geometry differs from the current binding"
    );
    for (path, expected) in &receipt.source_sha256 {
        ensure!(
            crate::sha(&root.join(path))? == *expected,
            "PGFUN guide input changed: {path}"
        );
    }
    let pdf = guide.join("gun-positioner-guide.pdf");
    ensure!(
        crate::sha(&pdf)? == receipt.pdf_sha256,
        "PGFUN guide PDF differs from its receipt"
    );
    ensure!(
        lopdf::Document::load(pdf)?.get_pages().len() == receipt.pages,
        "PGFUN guide page count differs from its receipt"
    );
    let parts: Parts = read(cad.join("print-manifest.json"))?;
    let archive = cad.join("print-pack.zip");
    let output = Command::new("unzip").args(["-Z1"]).arg(&archive).output()?;
    ensure!(output.status.success(), "read the PGFUN print archive");
    let members: Vec<_> = String::from_utf8(output.stdout)?
        .lines()
        .filter(|s| s.ends_with(".stl"))
        .map(str::to_owned)
        .collect();
    let actual: BTreeSet<_> = members.iter().cloned().collect();
    let expected: BTreeSet<_> = parts
        .parts
        .iter()
        .map(|p| format!("{}.stl", p.name))
        .collect();
    ensure!(
        actual == expected && actual.len() == members.len(),
        "PGFUN print archive identities differ from its manifest"
    );
    for part in &parts.parts {
        let bytes = Command::new("unzip")
            .arg("-p")
            .arg(&archive)
            .arg(format!("{}.stl", part.name))
            .output()?;
        ensure!(
            bytes.status.success() && sha(&bytes.stdout) == part.sha256,
            "PGFUN archived part differs: {}",
            part.name
        );
    }
    let purchases: Purchases = read(doc.join("purchases.json"))?;
    ensure!(
        purchases
            .mechanism
            .iter()
            .chain(&purchases.observation)
            .all(|p| p.prime),
        "PGFUN recorded purchase has no Prime observation"
    );
    let cents = purchases
        .mechanism
        .iter()
        .chain(&purchases.observation)
        .map(|p| (p.subtotal * 100.).round() as i64)
        .sum::<i64>();
    let clearance: Clearance = read(cad.join("clearance-check.json"))?;
    ensure!(
        clearance.geometry_sha256 == geometry.sha256
            && clearance.unintended_intersections.is_empty(),
        "PGFUN clearance record differs or contains unintended intersections"
    );
    let status = Command::new(peripheral()?)
        .arg("--root")
        .arg(root)
        .arg("positioner-verify")
        .status()?;
    ensure!(
        status.success(),
        "PGFUN firmware binding review exited with {status}"
    );
    println!(
        "PGFUN guide, release inputs, {} archived print identities and recorded Prime total ${:.2} match their current geometry binding",
        parts.parts.len(),
        cents as f64 / 100.
    );
    Ok(())
}
