//! The rear equipment fit article crops the production enclosure and keeps its matching caps.
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

fn clip_bounds(row: &mut Value, key: &str, lo: [f64; 3], hi: [f64; 3]) -> bool {
    let Some(b) = row.get(key).and_then(Value::as_array) else { return true; };
    let mut b: Vec<f64> = b.iter().filter_map(Value::as_f64).collect();
    if b.len() != 6 { return false; }
    for k in 0..3 {
        b[2*k] = b[2*k].max(lo[k]);
        b[2*k+1] = b[2*k+1].min(hi[k]);
        if b[2*k] >= b[2*k+1] { return false; }
    }
    row[key] = json!(b);
    true
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
    let mut regions = json!({"producer":"rear-equipment-corner", "source_stl_sha256":crop_sha,
                             "boundary_overlap_mm":native["boundary_overlap_mm"]});
    for key in ["support_free_regions", "support_regions", "bridge_regions"] {
        let rows: Vec<Value> = native[key].as_array().into_iter().flatten().filter_map(|r| {
            let mut row = r.clone();
            (clip_bounds(&mut row, "bounds_source_mm", lo, hi)
             && clip_bounds(&mut row, "blocking_bounds_source_mm", lo, hi)).then_some(row)
        }).collect();
        regions[key] = json!(rows);
    }
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
