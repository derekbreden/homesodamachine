//! The rear equipment fit article crops the production enclosure and keeps its matching caps.
mod regions;
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Solid, stl_bytes, v3};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{fs, path::Path};

const HERE: &str = "hardware/print-tests/rear-equipment-corner";

fn digest(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }
fn write_json(path: &Path, value: &Value) -> Result<()> {
    fs::write(path, serde_json::to_vec_pretty(value)?)?;
    Ok(())
}

fn main() -> Result<()> {
    let here = Path::new(HERE);
    let spec: Value = serde_json::from_slice(&fs::read(here.join("inputs.json"))?)?;
    let point = |key: &str| -> Result<[f64; 3]> {
        Ok(std::array::from_fn(|k| spec[key][k].as_f64().unwrap()))
    };
    let (lo, hi) = (point("crop_min_mm")?, point("crop_max_mm")?);
    let model = spec["source_model"].as_str().context("source model")?;
    let source = hsm_kernel::import::model(model)?;
    let crop = source[0].solid.intersect(&Solid::cuboid(v3(lo[0],lo[1],lo[2]),v3(hi[0],hi[1],hi[2])))?;
    crop.check()?;
    ensure!(crop.components().len() == 1, "the enclosure corner must remain connected");
    let out = here.join("parts");
    fs::create_dir_all(&out)?;
    let bytes = stl_bytes(&[&crop])?;
    let crop_sha = digest(&bytes);
    fs::write(out.join("rear-equipment-corner.stl"), bytes)?;
    let native: Value = serde_json::from_slice(&fs::read(spec["source_print_features"].as_str().context("print features")?)?)?;
    let regions = regions::crop_regions(&native, "rear-equipment-corner", &crop_sha, lo, hi, |_| true);
    write_json(&out.join("rear-equipment-corner.print-features.json"), &regions)?;
    let mut caps = Vec::new();
    for cap in spec["caps"].as_array().context("caps")? {
        let name = cap.as_str().context("cap name")?;
        let source = format!("hardware/printed-parts/enclosure/rear-equipment-caps/{name}.stl");
        let bytes = fs::read(&source)?;
        let sha = digest(&bytes);
        fs::write(out.join(format!("{name}.stl")), bytes)?;
        caps.push(json!({"name":name,"source":source,"stl_sha256":sha}));
    }
    let b = crop.bounds();
    write_json(&out.join("geometry.json"), &json!({"inputs":spec,
        "source_model_sha256":digest(&fs::read(model)?),
        "source_stl_sha256":digest(&fs::read(spec["source_stl"].as_str().unwrap())?),
        "corner_stl_sha256":crop_sha,"corner_volume_mm3":crop.volume(),
        "corner_bounds_mm":[[b.min.x,b.min.y,b.min.z],[b.max.x,b.max.y,b.max.z]],
        "connected_solids":1,"watertight":true,"caps":caps}))?;
    println!("{}", out.join("geometry.json").display());
    Ok(())
}
