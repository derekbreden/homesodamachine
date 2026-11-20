//! Crops the production tube seat with its full host wall for a ceiling-down fit print.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Solid, stl_bytes, v3};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const HERE: &str = "hardware/print-tests/tube-snap-corbel";

fn digest(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }

fn main() -> Result<()> {
    let here = Path::new(HERE);
    let inputs: Value = serde_json::from_slice(&fs::read(here.join("inputs.json"))?)?;
    let point = |name: &str| -> Result<[f64; 3]> {
        let values = inputs[name].as_array().with_context(|| format!("{name} is a point"))?;
        ensure!(values.len() == 3, "{name} needs three coordinates");
        Ok([
            values[0].as_f64().context("x")?,
            values[1].as_f64().context("y")?,
            values[2].as_f64().context("z")?,
        ])
    };
    let (lo, hi) = (point("crop_min_mm")?, point("crop_max_mm")?);
    let model = inputs["source_model"].as_str().context("source model")?;
    let source = hsm_kernel::import::model(model)?;
    let crop = source[0].solid.intersect(&Solid::cuboid(
        v3(lo[0], lo[1], lo[2]), v3(hi[0], hi[1], hi[2])))?;
    crop.check()?;
    ensure!(crop.components().len() == 1, "the tube seat and its wall must remain connected");
    let out = here.join("parts");
    fs::create_dir_all(&out)?;
    let bytes = stl_bytes(&[&crop])?;
    fs::write(out.join("tube-snap-corbel.stl"), &bytes)?;
    let production_features: Value = serde_json::from_slice(&fs::read(
        "hardware/printed-parts/enclosure/enclosure/enclosure-back-top.print-features.json")?)?;
    let select = |key: &str| -> Vec<Value> {
        production_features[key].as_array().into_iter().flatten()
            .filter(|feature| feature["name"].as_str().is_some_and(|name| name.starts_with("Fill tube snap")))
            .cloned().collect()
    };
    let support_features = json!({
        "producer": "tube-snap-corbel",
        "source_stl_sha256": digest(&bytes),
        "support_regions": select("support_regions"),
        "support_free_regions": [],
        "bridge_regions": [],
        "removable_support_stock": select("removable_support_stock"),
    });
    fs::write(out.join("tube-snap-corbel.print-features.json"), serde_json::to_vec_pretty(&support_features)?)?;
    let bounds = crop.bounds();
    let report = json!({
        "inputs": inputs,
        "source_model_sha256": digest(&fs::read(model)?),
        "source_stl_sha256": digest(&fs::read(inputs["source_stl"].as_str().context("source STL")?)?),
        "coupon_stl_sha256": digest(&bytes),
        "bounds_mm": [[bounds.min.x, bounds.min.y, bounds.min.z], [bounds.max.x, bounds.max.y, bounds.max.z]],
        "volume_mm3": crop.volume(),
        "connected_solids": 1,
        "watertight": true
    });
    fs::write(out.join("geometry.json"), serde_json::to_vec_pretty(&report)?)?;
    println!("{}", out.join("geometry.json").display());
    Ok(())
}
