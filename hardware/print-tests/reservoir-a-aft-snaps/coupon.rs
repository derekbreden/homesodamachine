//! The reservoir A aft snap coupon crops the production lid around its two aft tube clips and
//! keeps the lid's print regions that reach into the crop.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Solid, stl_bytes, v3};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const HERE: &str = "hardware/print-tests/reservoir-a-aft-snaps";
const NAME: &str = "reservoir-a-aft-snaps";

fn digest(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }

/// A row's box cut down to the crop, or nothing where the two do not meet.
fn clip_bounds(row: &mut Value, key: &str, lo: [f64; 3], hi: [f64; 3]) -> bool {
    let Some(b) = row.get(key).and_then(Value::as_array) else { return true; };
    let mut b: Vec<f64> = b.iter().filter_map(Value::as_f64).collect();
    if b.len() != 6 { return false; }
    for k in 0..3 {
        b[2 * k] = b[2 * k].max(lo[k]);
        b[2 * k + 1] = b[2 * k + 1].min(hi[k]);
        if b[2 * k] >= b[2 * k + 1] { return false; }
    }
    row[key] = json!(b);
    true
}

fn main() -> Result<()> {
    let here = Path::new(HERE);
    let inputs: Value = serde_json::from_slice(&fs::read(here.join("inputs.json"))?)?;
    let text = |name: &str| inputs[name].as_str().with_context(|| format!("{name} is text"));
    let point = |name: &str| -> Result<[f64; 3]> {
        let values = inputs[name].as_array().with_context(|| format!("{name} is a point"))?;
        ensure!(values.len() == 3, "{name} needs three coordinates");
        Ok([values[0].as_f64().context("x")?, values[1].as_f64().context("y")?, values[2].as_f64().context("z")?])
    };
    let (lo, hi) = (point("crop_min_mm")?, point("crop_max_mm")?);
    let model = text("source_model")?;
    let source = hsm_kernel::import::model(model)?;
    let crop = source[0].solid.intersect(&Solid::cuboid(v3(lo[0], lo[1], lo[2]), v3(hi[0], hi[1], hi[2])))?;
    crop.check()?;
    ensure!(crop.components().len() == 1, "both clips must stay on one piece of lid");
    let out = here.join("parts");
    fs::create_dir_all(&out)?;
    let bytes = stl_bytes(&[&crop])?;
    fs::write(out.join(format!("{NAME}.stl")), &bytes)?;

    let regions_path = text("source_print_regions")?;
    let production: Value = serde_json::from_slice(&fs::read(regions_path)?)?;
    let piece = text("source_piece")?;
    let source_stl = fs::read(text("source_stl")?)?;
    ensure!(production["native_artifact_sha256"][piece][".stl"].as_str() == Some(digest(&source_stl).as_str()),
            "{regions_path} binds {piece} to another export; regenerate it from the current geometry");
    let rows: Vec<Value> = production["pieces"][piece].as_array().into_iter().flatten().filter_map(|row| {
        let mut row = row.clone();
        if let Some(fields) = row.as_object_mut() { fields.remove("world_bounds_mm"); }
        (clip_bounds(&mut row, "applied_source_bounds_mm", lo, hi) && clip_bounds(&mut row, "machine_bounds_mm", lo, hi)).then_some(row)
    }).collect();
    ensure!(!rows.is_empty(), "the crop holds none of the lid's print regions");
    let regions = json!({
        "producer": format!("{HERE}/coupon.rs"),
        "use": "The lid's infill-only modifiers that reach into the coupon's crop, in the lid's own source coordinates.",
        "source_print_regions": regions_path,
        "source_print_regions_sha256": digest(&fs::read(regions_path)?),
        "native_artifact_sha256": { NAME: { ".stl": digest(&bytes) } },
        "pieces": { NAME: rows },
    });
    fs::write(out.join(format!("{NAME}.print-regions.json")), serde_json::to_vec_pretty(&regions)?)?;

    let bounds = crop.bounds();
    let report = json!({
        "inputs": inputs,
        "source_model_sha256": digest(&fs::read(model)?),
        "source_stl_sha256": digest(&source_stl),
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
