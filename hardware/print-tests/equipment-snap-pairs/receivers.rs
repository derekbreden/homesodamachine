//! The individual bench receivers retain each complete production seat and its rooted enclosure stock.
#[path = "../rear-equipment-corner/regions.rs"]
mod regions;
mod firm_regulator;
mod supported_meter;
mod three_dot;

use anyhow::{Context, Result, ensure};
use hsm_kernel::{Solid, import, stl_bytes, v3};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const HERE: &str = "hardware/print-tests/equipment-snap-pairs";
fn sha(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }
fn write_json(path: &Path, data: &Value) -> Result<()> {
    let mut bytes = serde_json::to_vec_pretty(data)?;
    bytes.push(b'\n');
    Ok(fs::write(path, bytes)?)
}

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    if let Some(arg) = args.next() {
        ensure!(args.next().is_none(), "expected one equipment snap variant");
        return match arg.to_str() {
            Some("--three-dot") => three_dot::write(),
            Some("--firm-regulator") => firm_regulator::write(),
            Some("--supported-meter") => supported_meter::write(),
            _ => anyhow::bail!("usage: equipment-snap-receivers [--three-dot | --firm-regulator | --supported-meter]"),
        };
    }
    let here = Path::new(HERE);
    let spec: Value = serde_json::from_slice(&fs::read(here.join("inputs.json"))?)?;
    let model = spec["source_model"].as_str().context("production enclosure model")?;
    let source = import::model(model)?;
    let body = import::body(&source, "enclosure-back-top")?;
    let features_file = spec["source_print_features"].as_str().context("print features")?;
    let feature_bytes = fs::read(features_file)?;
    let native = serde_json::from_slice(&feature_bytes)?;
    let out = here.join("parts");
    fs::create_dir_all(&out)?;
    let mut receivers = Vec::new();
    for fixture in spec["receivers"].as_array().context("receiver crops")? {
        let name = fixture["name"].as_str().context("receiver name")?;
        let lo: [f64; 3] = serde_json::from_value(fixture["min_mm"].clone())?;
        let hi: [f64; 3] = serde_json::from_value(fixture["max_mm"].clone())?;
        let clip = Solid::cuboid(v3(lo[0],lo[1],lo[2]), v3(hi[0],hi[1],hi[2]));
        let intersection = body.intersect(&clip)?;
        // Only the seat joined to the roof or the meter's flank is on the bench.
        let mut rooted: Vec<_> = intersection.components().into_iter().filter(|s|
            (s.bounds().max.z - hi[2]).abs() < 1e-5).collect();
        ensure!(rooted.len() == 1, "{name} must reach the print bed as one connected receiver");
        let seat = rooted.pop().unwrap();
        seat.check()?;
        let bytes = stl_bytes(&[&seat])?;
        let stl_sha = sha(&bytes);
        fs::write(out.join(format!("{name}.stl")), &bytes)?;
        let omit = fixture["omit_region_substring"].as_str();
        let features = regions::crop_regions(&native, "equipment-snap-receivers", &stl_sha, lo, hi, |row|
            !omit.is_some_and(|word| row["name"].as_str().unwrap_or("").to_lowercase().contains(word)));
        write_json(&out.join(format!("{name}.print-features.json")), &features)?;
        let b = seat.bounds();
        receivers.push(json!({"name": name, "sha256":stl_sha, "volume_mm3":seat.volume(),
            "removed_disconnected_volume_mm3":intersection.volume()-seat.volume(),
            "bounds_source_mm":[[b.min.x,b.min.y,b.min.z],[b.max.x,b.max.y,b.max.z]],
            "print_up_source":[0,0,-1],"connected_solids":1}));
    }
    write_json(&out.join("geometry.json"), &json!({"source_model":model,
        "source_model_sha256":sha(&fs::read(model)?),
        "source_stl_sha256":sha(&fs::read(spec["source_stl"].as_str().context("production STL")?)?),
        "source_print_features_sha256":sha(&feature_bytes),"receivers":receivers}))?;
    Ok(())
}
