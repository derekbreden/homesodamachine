//! This coupon prints the meter's recessed aft shoulder on a permanent slope rooted in the enclosure flank.
use anyhow::{Context, Result, ensure};
use hsm_enclosure_numbers::{Bounds, shell::BACK_TOP_FLANK_T};
use hsm_kernel::{Solid, import, stl_bytes, v3};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const SOURCE: &str = "hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step.npz";
const FEATURES: &str = "hardware/printed-parts/enclosure/enclosure/enclosure-back-top.print-features.json";
const PROFILE: &str = "hardware/printed-parts/petgf.profile.json";
const OUT: &str = "hardware/print-tests/rear-receiver-quick/parts";
const NAME: &str = "meter-shoulder-backed";
const CROWN_DEPTH: f64 = 3.9;
const FLANK_LEAD: f64 = 1.2;

fn region(features: &Value, kind: &str, name: &str) -> Result<Bounds> {
    let row = features[kind].as_array().context("production feature regions")?.iter()
        .find(|row| row["name"] == name).with_context(|| format!("missing {name}"))?;
    Ok(serde_json::from_value(row["bounds_source_mm"].clone())?)
}

fn main() -> Result<()> {
    let out = Path::new(OUT);
    fs::create_dir_all(out)?;
    let production = import::model(SOURCE)?;
    let source = import::body(&production, "enclosure-back-top")?;
    let features: Value = serde_json::from_slice(&fs::read(FEATURES)?)?;
    let [west, flank, fore, aft, face, top] = region(&features, "support_free_regions", "Backed flow meter aft shoulder")?;
    let profile: Value = serde_json::from_slice(&fs::read(PROFILE)?)?;
    let pitch: f64 = profile["Metadata/project_settings.config"]["layer_height"]
        .as_str().context("PET-GF layer height")?.parse()?;
    let production_bed = source.bounds().max.z;
    let required_bed = top + FLANK_LEAD;
    let bed = production_bed - ((production_bed - required_bed) / pitch).floor() * pitch;
    // Start the section on the aft shoulder, clear of the adjacent catch's end face.
    let low = v3(west, fore, face - CROWN_DEPTH);
    let high = v3(flank + BACK_TOP_FLANK_T, aft, bed);
    let crop = Solid::cuboid(low, high);
    let sample = source.intersect(&crop)?;
    sample.check()?;
    ensure!(sample.components().len() == 1, "the shoulder and flank must form one part");

    let bytes = stl_bytes(&[&sample])?;
    let sha = format!("{:x}", Sha256::digest(&bytes));
    fs::write(out.join(format!("{NAME}.stl")), bytes)?;
    let data = json!({"part":NAME, "source":SOURCE, "source_sha256":format!("{:x}",Sha256::digest(fs::read(SOURCE)?)),
        "feature_source":FEATURES, "stl_sha256":sha, "print_up_source":[0,0,-1],
        "crop_bounds_source_mm":[low.x,high.x,low.y,high.y,low.z,high.z], "production_bed_z_mm":production_bed,
        "shoulder_face_z_mm":face, "west_edge_x_mm":west, "flank_x_mm":flank, "aft_y_mm":aft, "volume_mm3":sample.volume(),
        "purpose":"Print the production meter shoulder with its flank backing and fore taper."});
    let mut report = serde_json::to_vec_pretty(&data)?;
    report.push(b'\n');
    fs::write(out.join("meter-geometry.json"), report)?;
    Ok(())
}
